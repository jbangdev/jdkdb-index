"""Run with: python -m unittest discover -s .github/scripts -p 'test_*.py'."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("retain-history.py").resolve()


class RetainHistoryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test Author")
        self.git("config", "user.email", "author@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")

    def git(self, *args, input=None):
        return subprocess.run(
            ["git", *args], cwd=self.repo, input=input,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        ).stdout

    def commit(self, number):
        (self.repo / "data.txt").write_text(f"snapshot {number}\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", f"Update {number}\n\nDetails: café")

    def trim(self):
        return subprocess.check_output(
            [sys.executable, str(SCRIPT)], cwd=self.repo, text=True
        ).strip()

    def history(self, ref):
        return self.git("rev-list", "--first-parent", ref).decode().splitlines()

    def snapshot_and_metadata(self, ref):
        headers, message = self.git("cat-file", "commit", ref).split(b"\n\n", 1)
        return [line for line in headers.splitlines() if not line.startswith(b"parent ")], message

    def assert_retained(self, sha):
        expected = self.history("HEAD")[:5]
        actual = self.history(sha)
        self.assertEqual(len(actual), len(expected))
        for before, after in zip(expected, actual):
            self.assertEqual(self.snapshot_and_metadata(before), self.snapshot_and_metadata(after))
        self.assertEqual(self.git("rev-list", "--count", sha).strip(), str(len(expected)).encode())

    def test_retains_five_snapshots_without_moving_head_or_worktree(self):
        for number in range(8):
            self.commit(number)
        before = self.git("rev-parse", "HEAD")
        (self.repo / "data.txt").write_text("uncommitted work\n", encoding="utf-8")
        sha = self.trim()
        self.assert_retained(sha)
        self.assertEqual(before, self.git("rev-parse", "HEAD"))
        self.assertEqual((self.repo / "data.txt").read_text(), "uncommitted work\n")

    def test_short_history_is_unchanged(self):
        for number in range(3):
            self.commit(number)
        self.assertEqual(self.trim(), self.git("rev-parse", "HEAD").decode().strip())

    def test_repeated_daily_updates_and_no_change_run(self):
        for number in range(8):
            self.commit(number)
        for number in range(8, 11):
            sha = self.trim()
            self.assert_retained(sha)
            self.git("update-ref", "HEAD", sha)
            self.assertEqual(self.trim(), sha)
            self.commit(number)

    def test_depth_five_checkout_with_new_commit(self):
        for number in range(8):
            self.commit(number)
        source = self.repo
        remote = self.root / "remote.git"
        self.git("clone", "--bare", str(source), str(remote))
        self.git("clone", "--depth=5", remote.as_uri(), str(self.root / "shallow"))
        self.repo = self.root / "shallow"
        self.git("config", "user.name", "Update Bot")
        self.git("config", "user.email", "bot@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.assertEqual(self.git("rev-parse", "--is-shallow-repository").strip(), b"true")
        self.assert_retained(self.trim())
        self.commit(8)
        sha = self.trim()
        self.assert_retained(sha)
        expected = self.git("rev-parse", "origin/main").decode().strip()
        self.git("push", f"--force-with-lease=refs/heads/main:{expected}",
                 "origin", f"{sha}:refs/heads/main")
        self.assertEqual(self.git("--git-dir", str(remote), "rev-list", "--count", "main").strip(), b"5")

    def test_invalidated_signature_is_removed(self):
        for number in range(6):
            self.commit(number)
        expected = self.snapshot_and_metadata("HEAD")
        headers, message = self.git("cat-file", "commit", "HEAD").split(b"\n\n", 1)
        signed = headers + b"\ngpgsig -----BEGIN PGP SIGNATURE-----\n fake\n -----END PGP SIGNATURE-----\n\n" + message
        sha = self.git("hash-object", "-t", "commit", "-w", "--stdin", input=signed).strip().decode()
        self.git("update-ref", "HEAD", sha)
        self.assertEqual(self.snapshot_and_metadata(self.trim()), expected)

    def test_merge_uses_latest_first_parent_snapshots(self):
        for number in range(6):
            self.commit(number)
        self.git("checkout", "-b", "feature", "HEAD~2")
        (self.repo / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "Feature")
        self.git("checkout", "main")
        self.git("merge", "--no-ff", "feature", "-m", "Merge feature")
        self.assert_retained(self.trim())

    def test_push_lease_rejects_concurrent_change(self):
        for number in range(8):
            self.commit(number)
        remote = str(self.root / "remote.git")
        self.git("init", "--bare", remote)
        self.git("remote", "add", "origin", remote)
        self.git("push", "origin", "HEAD:refs/heads/main")
        expected = self.git("rev-parse", "HEAD").decode().strip()
        sha = self.trim()
        self.git("push", f"--force-with-lease=refs/heads/main:{expected}",
                 "origin", f"{sha}:refs/heads/main")
        self.assertEqual(self.git("--git-dir", remote, "rev-list", "--count", "main").strip(), b"5")
        with self.assertRaises(subprocess.CalledProcessError):
            self.git("push", f"--force-with-lease=refs/heads/main:{expected}",
                     "origin", "HEAD:refs/heads/main")


if __name__ == "__main__":
    unittest.main()

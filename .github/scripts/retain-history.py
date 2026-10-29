#!/usr/bin/env python3
"""Print a standalone chain of the latest five first-parent commits.

Write commit objects only: leave refs, the index and the working tree untouched.
This works with a depth-five checkout; no older history needs to be downloaded.
"""

import subprocess


def git(*args, input=None):
    return subprocess.run(
        ["git", *args], input=input, stdout=subprocess.PIPE, check=True
    ).stdout


def retain_history():
    commits = git("rev-list", "--first-parent", "--max-count=5", "HEAD").splitlines()
    parent = None
    for commit in reversed(commits):
        raw = git("cat-file", "commit", commit.decode("ascii"))
        headers, message = raw.split(b"\n\n", 1)
        retained = []
        discard = False
        for line in headers.split(b"\n"):
            if not line.startswith(b" "):
                # Parent links change; signatures and signed merge tags no longer apply.
                discard = line.split(b" ", 1)[0] in (
                    b"parent", b"gpgsig", b"gpgsig-sha256", b"mergetag"
                )
            if not discard:
                retained.append(line)
        if parent is not None:
            retained.insert(1, b"parent " + parent)
        rewritten = b"\n".join(retained) + b"\n\n" + message
        parent = git("hash-object", "-t", "commit", "-w", "--stdin", input=rewritten).strip()
    return parent.decode("ascii")


if __name__ == "__main__":
    print(retain_history())

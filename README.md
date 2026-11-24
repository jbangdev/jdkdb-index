# jdkdb-index - JDK Metadata Index

This repository stores different kinds of metadata index files from a list of currently available Java JRE/JDK distributions and stores them in the [`metadata/`](./db/metadata) directory.

The information in this repository is updated daily using the [jdkdb-scraper project](https://github.com/jbangdev/jdkdb-scraper) and the metadata collected in the [jdkdb-data repository](https://github.com/jbangdev/jdkdb-data).
This project is based on [Joschi's Java Metadata project](https://github.com/joschi/java-metadata) and incorporates ideas from the [Foojay's Disco API project](https://github.com/foojayio/discoapi).

## Rolling Git history

The update workflow retains only the latest five first-parent commits on the
updated branch, including manual changes. Each retained commit keeps its complete
file snapshot, author, committer, dates and message. Merge ancestry is flattened
and commit signatures are removed because rewriting invalidates them.

Publishing an update rewrites history and force-pushes with a lease against the
commit checked out at the start of the run. If the branch changes during indexing,
the push fails instead of overwriting that change; rerun the workflow to retry.
Branch protection must allow the workflow to force-push. A manual run with
`do_commit: false` does not commit, trim history or push.

Existing clones must resync with the rewritten branch (save local work first).
Other branches, tags and GitHub pull request references may retain older history,
and GitHub storage reclamation depends on server-side garbage collection.

## Supported distributions

* [AdoptOpenJDK](https://adoptopenjdk.net/)
* [Bisheng](https://www.openeuler.org/en/other/projects/bishengjdk/)
* [Corretto](https://aws.amazon.com/corretto/)
* [Debian](https://wiki.debian.org/Java)
* [Dragonwell](https://dragonwell-jdk.io/)
* [Eclipse Temurin](https://adoptium.net/)
* [Gluon GraalVM](https://github.com/gluonhq/graal)
* [GraalVM Community Edition](https://www.graalvm.org/)
* [IBM Semeru](https://developer.ibm.com/languages/java/semeru-runtimes/)
* [Java SE Reference Implementations](https://jdk.java.net/)
* [JetBrains Runtime](https://github.com/JetBrains/JetBrainsRuntime)
* [Kona](https://github.com/Tencent/TencentKona-8)
* [Liberica](https://bell-sw.com/)
* [Liberica Native Image Kit](https://bell-sw.com/liberica-native-image-kit/)
* [Mandrel](https://github.com/graalvm/mandrel)
* [Microsoft OpenJDK](https://www.microsoft.com/openjdk)
* [OpenJDK](https://jdk.java.net/)
* [OpenLogic](https://www.openlogic.com/openjdk-downloads)
* [Oracle JDK](https://www.oracle.com/java/)
* [Oracle GraalVM](https://www.graalvm.org/)
* [Red Hat OpenJDK](https://developers.redhat.com/products/openjdk/overview)
* [SapMachine](https://sap.github.io/SapMachine/)
* [Semeru Certified](https://developer.ibm.com/languages/java/semeru-runtimes/)
* [Trava OpenJDK](https://github.com/TravaOpenJDK/)
* [Zulu Community](https://www.azul.com/products/zulu-community/)

## Metadata structure

| Field name      | Description                                         |
| --------------- | --------------------------------------------------- |
| `architecture`  | Supported machine architecture                      |
| `checksum`      | Distro-provided checksum of the artifact            |
| `checksum_type` | Hash algorithm of the distro checksum               |
| `distro`        | Distribution identifier                             |
| `features`      | Features of the distribution (e.g. `musl`, `fx`)    |
| `file_type`     | The file extension of the artifact                  |
| `filename`      | Filename of the artifact                            |
| `image_type`    | JRE (`jre`) or JDK (`jdk`)                          |
| `java_version`  | Java version the artifact is based on               |
| `jvm_impl`      | JVM implementation (`hotspot`, `openj9`, `graalvm`) |
| `md5`           | MD5 checksum of the artifact                        |
| `os`            | Supported operating system                          |
| `release_info`  | Additional release metadata                         |
| `release_type`  | `ga` (stable) or `ea` (early access)                |
| `sha1`          | SHA-1 checksum of the artifact                      |
| `sha256`        | SHA-256 checksum of the artifact                    |
| `sha512`        | SHA-512 checksum of the artifact                    |
| `size`          | Size of the artifact in bytes                       |
| `url`           | Full source URL of the artifact                     |
| `vendor`        | Name of publishing organization                     |
| `version`       | Version of the JDK/JRE distribution                 |

Example:

```json
{
  "architecture": "x86_64",
  "checksum": "f07e67b9773cadaf539e67b4e26957b9d85220b7",
  "checksum_type": "sha1",
  "distro": "zulu",
  "features": [
    "javafx"
  ],
  "file_type": "tar.gz",
  "filename": "zulu8.44.0.13-ca-fx-jdk8.0.242-linux_x64.tar.gz",
  "image_type": "jdk",
  "java_version": "8.0.242",
  "jvm_impl": "hotspot",
  "md5": "fda058637e054eae280eb8761824d064",
  "os": "linux",
  "release_info": {
    "IMPLEMENTOR": "Azul Systems, Inc.",
    "IMPLEMENTOR_VERSION": "Zulu8.44.0.13-CA-linux_x64",
    "JAVA_VERSION": "1.8.0_242",
    "OS_ARCH": "x64",
    "OS_NAME": "Linux",
    "OS_VERSION": "2.6",
    "SOURCE": ".:git:16a32e42b474+"
  },
  "release_type": "ga",
  "sha1": "f07e67b9773cadaf539e67b4e26957b9d85220b7",
  "sha256": "e35bad183b6309384fd440890b4c7888b30670006a6e10ce3d4fefb40fbefc93",
  "sha512": "2f650295baf38d99794343b04dd2dd81ebeff92fa9c3a8bf110700118d1879e20016c6ff441f4488e87dd1fc733b87836e90ec9ba26184d8288c400e11bc9057",
  "size": 155585453,
  "url": "https://static.azul.com/zulu/bin/zulu8.44.0.13-ca-fx-jdk8.0.242-linux_x64.tar.gz",
  "vendor": "zulu",
  "version": "8.44.0.13"
}
```

See also the files inside the [`metadata/`](./db/metadata/) directory.

## Disclaimer

This project is in no way affiliated with any of the companies or projects offering and distributing the actual JREs and JDKs.

All respective copyrights and trademarks are theirs.

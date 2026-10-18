"""Download and verify the source archives offered with a NumeriPlot app release.

The app bundles Qt (LGPL-3.0-only), PyQt6 (GPL-3.0-only) and, through SciPy, the
GCC runtime libraries. Their upstream source archives are published next to
the disk image. The hashes below were checked against the official records:
Qt's .sha256 files, GCC's sha512.sum and PyPI's metadata.

Usage: python tools/fetch_release_sources.py [--output DIR]
"""
import argparse
import hashlib
import shutil
import sys
import urllib.request
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.version import SOURCES_DIRNAME, VERSION  # noqa: E402

QT = "https://download.qt.io/archive/qt/6.10/6.10.2/submodules"
SOURCES = [
    {
        "file": "qtbase-everywhere-src-6.10.2.tar.xz",
        "url": f"{QT}/qtbase-everywhere-src-6.10.2.tar.xz",
        "sha256": "aeb78d29291a2b5fd53cb55950f8f5065b4978c25fb1d77f627d695ab9adf21e",
        "covers": "Qt 6.10.2 QtCore, QtGui, QtDBus, QtWidgets and their plugins (LGPL-3.0-only)",
    },
    {
        "file": "qtsvg-everywhere-src-6.10.2.tar.xz",
        "url": f"{QT}/qtsvg-everywhere-src-6.10.2.tar.xz",
        "sha256": "f07ff80f38caf235187200345392ca7479445ddf49a36c3694cd52a735dad6e1",
        "covers": "Qt 6.10.2 QtSvg and its SVG plugins (LGPL-3.0-only)",
    },
    {
        "file": "pyqt6-6.10.2.tar.gz",
        "url": "https://files.pythonhosted.org/packages/96/03/"
               "e756f52e8b0d7bb5527baf8c46d59af0746391943bdb8655acba22ee4168/pyqt6-6.10.2.tar.gz",
        "sha256": "6c0db5d8cbb9a3e7e2b5b51d0ff3f283121fa27b864db6d2f35b663c9be5cc83",
        "covers": "PyQt6 6.10.2 (GPL-3.0-only)",
    },
    {
        "file": "gcc-12.1.0.tar.xz",
        "url": "https://ftp.gnu.org/gnu/gcc/gcc-12.1.0/gcc-12.1.0.tar.xz",
        "sha256": "62fd634889f31c02b64af2c468f064b47ad1ca78411c45abe6ac4b5f8dd19c7b",
        "covers": "GCC 12.1 runtime libraries bundled by SciPy 1.15.2: libgfortran and "
                  "libgcc_s (GPL-3.0 with the GCC Runtime Library Exception), "
                  "libquadmath (LGPL-2.1-or-later)",
    },
]

# The archives above match these installed versions; update both together.
EXPECTED_VERSIONS = {"PyQt6": "6.10.2", "PyQt6-Qt6": "6.10.2", "scipy": "1.15.2"}

README = """NumeriPlot {version} — source code for the bundled GPL/LGPL components
=====================================================================

The NumeriPlot app for macOS (Apple Silicon) contains the unmodified binaries
of the components below. Each archive is the official upstream source release,
verified against the publisher's checksum (see SHA256SUMS).

{entries}

NumeriPlot itself (GPL-3.0-only): the "Source code" archives of the same
GitHub release (tag v{version}), including the build scripts build_macos.sh,
NumeriPlot.spec and tools/.

GCC runtime: SciPy's wheel ships these libraries as built by the
gfortran-for-macOS 12.1 toolchain (https://github.com/fxcoudert/gfortran-for-macOS),
which applies the Darwin/arm64 port maintained at
https://github.com/iains/gcc-12-branch on top of GCC 12.1. SciPy's own license
file names the GCC sources as their origin; gcc-12.1.0.tar.xz is that release.

Replacing Qt: the Qt frameworks and plugins are separate files inside
NumeriPlot.app/Contents/Frameworks/PyQt6/Qt6/. Build a compatible Qt 6.10
from these sources, copy your frameworks or plugins over the bundled ones and
re-sign the app locally:  codesign --force --deep --sign - NumeriPlot.app
Details and all license texts: THIRD_PARTY_NOTICES.md and, inside the app,
About NumeriPlot → Third-Party Licenses.
"""


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_versions():
    wrong = {name: metadata.version(name) for name, expected in EXPECTED_VERSIONS.items()
             if metadata.version(name) != expected}
    if wrong:
        raise SystemExit(f"Installed versions differ from the pinned sources: {wrong}. "
                         "Update SOURCES and EXPECTED_VERSIONS together.")


def fetch(source, folder):
    target = folder / source["file"]
    if target.is_file() and sha256(target) == source["sha256"]:
        print(f"ok (present)  {source['file']}")
        return
    partial = target.with_name(target.name + ".part")
    with urllib.request.urlopen(source["url"], timeout=120) as response, open(partial, "wb") as out:
        shutil.copyfileobj(response, out)
    actual = sha256(partial)
    if actual != source["sha256"]:
        partial.unlink()
        raise SystemExit(f"Checksum mismatch for {source['file']}: {actual}")
    partial.replace(target)
    print(f"ok (downloaded) {source['file']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / SOURCES_DIRNAME)
    args = parser.parse_args(argv)
    check_versions()
    args.output.mkdir(parents=True, exist_ok=True)
    for source in SOURCES:
        fetch(source, args.output)
    (args.output / "SHA256SUMS").write_text(
        "".join(f"{s['sha256']}  {s['file']}\n" for s in SOURCES), encoding="utf-8")
    entries = "\n".join(f"- {s['file']}\n  {s['covers']}\n  {s['url']}" for s in SOURCES)
    (args.output / "README.txt").write_text(
        README.format(version=VERSION, entries=entries), encoding="utf-8")
    print(f"Release sources ready: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

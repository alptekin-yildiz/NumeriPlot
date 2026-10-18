"""Check a built NumeriPlot.app before it is packaged into the disk image.

Usage: python tools/check_app_bundle.py dist/NumeriPlot.app
"""
import plistlib
import sys
from pathlib import Path

from macholib.mach_o import CPU_TYPE_NAMES
from macholib.MachO import MachO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.version import BUNDLE_ID, MACOS_MINIMUM_VERSION, VERSION  # noqa: E402
from tools.bundle_policy import EXCLUDED_QT_FRAMEWORKS, EXCLUDED_QT_PATHS  # noqa: E402

CPU_TYPE_ARM64 = next(code for code, name in CPU_TYPE_NAMES.items() if name == "ARM64")
MACHO_MAGIC = {b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe"}  # thin 64-bit, universal


def bundled(app, relative):
    """PyInstaller places data in Resources and binaries in Frameworks."""
    for base in ("Resources", "Frameworks"):
        candidate = app / "Contents" / base / relative
        if candidate.exists() or candidate.is_symlink():
            return candidate
    return None


def macho_files(app):
    for path in (app / "Contents").rglob("*"):
        if path.is_file() and not path.is_symlink():
            with open(path, "rb") as stream:
                if stream.read(4) in MACHO_MAGIC:
                    yield path


def problems(app):
    found = []
    info = plistlib.loads((app / "Contents" / "Info.plist").read_bytes())
    expected = {"CFBundleShortVersionString": VERSION, "CFBundleIdentifier": BUNDLE_ID,
                "LSMinimumSystemVersion": MACOS_MINIMUM_VERSION}
    found += [f"Info.plist {key} is {info.get(key)!r}, expected {value!r}"
              for key, value in expected.items() if info.get(key) != value]

    qt_notices = next((ROOT / "licenses").glob("Qt-*-third-party.txt")).name
    required = ["LICENSE", "THIRD_PARTY_NOTICES.md", "licenses/LGPL-3.0-only.txt",
                f"licenses/{qt_notices}", "licenses/third-party/INDEX.md",
                "licenses/third-party/THIRD_PARTY_LICENSES.txt",
                "examples/NumeriPlot_example_project.json"]
    found += [f"missing {name}" for name in required if bundled(app, name) is None]
    found += [f"excluded Qt part present: {name}" for name in EXCLUDED_QT_PATHS
              if bundled(app, name) is not None]
    found += [f"bytecode cache in bundle: {path.relative_to(app)}"
              for path in app.rglob("__pycache__")]
    found += [f"dangling link: {path.relative_to(app)}" for path in (app / "Contents").rglob("*")
              if path.is_symlink() and not path.exists()]

    executable = app / "Contents" / "MacOS" / info.get("CFBundleExecutable", "")
    if CPU_TYPE_ARM64 not in {header.header.cputype for header in MachO(str(executable)).headers}:
        found.append(f"{executable.name} has no arm64 code")
    for path in macho_files(app):
        for header in MachO(str(path)).headers:
            for _, _, name in header.walkRelocatables():
                if any(f"{framework}.framework" in name for framework in EXCLUDED_QT_FRAMEWORKS):
                    found.append(f"{path.relative_to(app)} still links {name}")
    return found


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__)
    app = Path(argv[1])
    found = problems(app)
    for problem in found:
        print(f"ERROR: {problem}")
    if not found:
        print(f"Bundle check passed: {app}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

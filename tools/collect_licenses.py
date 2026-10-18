"""Collect the third-party license notices bundled with the NumeriPlot app.

build_macos.sh runs this with the build environment's Python before
PyInstaller. It resolves requirements.txt to the installed runtime
distributions and copies the license files from their wheel metadata, then
adds Python's license, PyInstaller's bootloader terms and the Qt notices.

Usage: python tools/collect_licenses.py [--output build/third-party-licenses]
"""
import argparse
import platform
import re
import shutil
import sys
import sysconfig
from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.version import SOURCES_DIRNAME, VERSION  # noqa: E402

# PyInstaller's bootloader and runtime hooks run inside the app.
BUILD_TOOLS = ("pyinstaller", "pyinstaller-hooks-contrib")
NOTICE_NAME = re.compile(r"^(LICEN[CS]E|COPYING|NOTICE|AUTHORS)", re.IGNORECASE)
CODE_SUFFIXES = {".py", ".pyc", ".pyi", ".so", ".dylib"}
# Classifiers that would hide an exception the license file grants.
SUMMARY_OVERRIDES = {
    "pyinstaller": "GPL-2.0-or-later with the bootloader exception; run-time hooks Apache-2.0",
}
# Notices a wheel omits, kept in the repository as licenses/<name>-<version>/.
TRACKED_NOTICES = ROOT / "licenses"

INDEX_INTRO = """# Third-party components in NumeriPlot {version}

NumeriPlot is licensed under GPL-3.0-only (see LICENSE). The app bundles the
components below. They are unmodified apart from the library paths and ad-hoc
signatures that PyInstaller sets. Each folder holds the license files shipped
with that component.
"""

INDEX_SOURCES = """
## Source code

Qt (LGPL-3.0-only), PyQt6 (GPL-3.0-only) and the GCC runtime libraries that
SciPy bundles (libgfortran and libgcc_s: GPL-3.0 with the GCC Runtime Library
Exception; libquadmath: LGPL-2.1-or-later, notices in SciPy's LICENSE.txt) are
offered as source archives with the NumeriPlot {version} release on GitHub
({sources}). NumeriPlot's own source is the release's source code archive.
How to replace the Qt libraries: THIRD_PARTY_NOTICES.md, "Replacing Qt".
"""


def runtime_distributions(requirements):
    """Installed distributions for requirements.txt and their runtime dependencies."""
    pending = [Requirement(line.strip()).name
               for line in requirements.read_text(encoding="utf-8").splitlines()
               if line.strip() and not line.lstrip().startswith("#")]
    found = {}
    while pending:
        key = canonicalize_name(pending.pop())
        if key in found:
            continue
        dist = metadata.distribution(key)
        found[key] = dist
        for raw in dist.requires or []:
            requirement = Requirement(raw)
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                pending.append(requirement.name)
    return [found[key] for key in sorted(found)]


def notice_files(dist):
    """License files in the .dist-info folder and among the installed package files."""
    selected = []
    for item in dist.files or []:
        parts = Path(str(item)).parts
        if not parts or Path(parts[-1]).suffix.lower() in CODE_SUFFIXES:
            continue
        in_metadata = parts[0].endswith(".dist-info")
        if NOTICE_NAME.match(parts[-1]) or (in_metadata and "licenses" in parts[1:-1]):
            selected.append(item)
    return sorted(selected, key=str)


def notice_target(folder, item):
    parts = Path(str(item)).parts
    # Metadata files sit at the top; package files keep their installed path.
    return folder.joinpath(*(parts[1:] if parts[0].endswith(".dist-info") else parts))


def tracked_notices(name, version):
    """Repository notices for this exact version; stale versions stop the build."""
    folders = [path for path in TRACKED_NOTICES.glob(f"{name}-*")
               if path.is_dir() and canonicalize_name(path.name.rsplit("-", 1)[0]) == canonicalize_name(name)]
    stale = [path.name for path in folders if path.name != f"{name}-{version}"]
    if stale:
        raise SystemExit(f"licenses/{stale[0]} does not match the installed {name} {version}. "
                         "Refresh it from that version's source distribution.")
    return sorted(path for folder in folders for path in folder.iterdir() if path.is_file())


def license_summary(dist):
    meta = dist.metadata
    override = SUMMARY_OVERRIDES.get(canonicalize_name(meta["Name"]))
    if override:
        return override
    if meta.get("License-Expression"):
        return meta["License-Expression"]
    classifiers = [c.split(" :: ")[-1] for c in meta.get_all("Classifier") or []
                   if c.startswith("License ::")]
    if classifiers:
        return ", ".join(classifiers)
    value = (meta.get("License") or "").strip()
    return value if value and "\n" not in value and len(value) <= 40 else "see license files"


def copy_notices(dist, output):
    name, version = dist.metadata["Name"], dist.version
    folder = output / f"{name}-{version}"
    copied = []
    for item in notice_files(dist):
        target = notice_target(folder, item)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dist.locate_file(item), target)
        copied.append(target)
    for path in tracked_notices(name, version):
        target = folder / "source-distribution" / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        copied.append(target)
    if not copied:
        raise SystemExit(f"No license file found for {name} {version}.")
    return name, version, license_summary(dist), copied


def collect(output):
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    distributions = runtime_distributions(ROOT / "requirements.txt")
    distributions += [metadata.distribution(name) for name in BUILD_TOOLS]
    entries = [copy_notices(dist, output) for dist in distributions]

    python_version = platform.python_version()
    python_license = output / f"Python-{python_version}" / "LICENSE.txt"
    python_license.parent.mkdir()
    shutil.copyfile(Path(sysconfig.get_path("stdlib")) / "LICENSE.txt", python_license)
    entries.append(("Python", python_version, "PSF-2.0 and incorporated software", [python_license]))

    qt_version = metadata.version("PyQt6-Qt6")
    qt_notices = ROOT / "licenses" / f"Qt-{qt_version}-third-party.txt"
    if not qt_notices.is_file():
        raise SystemExit(f"{qt_notices.name} is missing. Regenerate it with tools/qt_attributions.py.")
    lgpl = ROOT / "licenses" / "LGPL-3.0-only.txt"

    rows = [f"| {name} | {version} | {summary} | "
            + ", ".join(str(path.relative_to(output)) for path in paths) + " |"
            for name, version, summary, paths in entries]
    rows.append(f"| Qt modules (qtbase, qtsvg) | {qt_version} | LGPL-3.0-only; bundled code "
                f"under its own terms | ../{qt_notices.name}, ../{lgpl.name} |")
    index = (INDEX_INTRO.format(version=VERSION)
             + "\n| Component | Version | License | Files |\n| --- | --- | --- | --- |\n"
             + "\n".join(rows) + "\n"
             + INDEX_SOURCES.format(version=VERSION, sources=SOURCES_DIRNAME))
    (output / "INDEX.md").write_text(index, encoding="utf-8")

    parts = [f"NumeriPlot {VERSION} — third-party licenses\n\n{index}"]
    for name, version, _, paths in entries:
        for path in paths:
            parts.append(f"==== {name} {version}: {path.relative_to(output)} ====\n\n"
                         + path.read_text(encoding="utf-8", errors="replace").strip())
    parts.append(f"==== Qt {qt_version} ====\n\n" + qt_notices.read_text(encoding="utf-8").strip())
    parts.append("==== GNU Lesser General Public License v3 ====\n\n"
                 + lgpl.read_text(encoding="utf-8").strip())
    (output / "THIRD_PARTY_LICENSES.txt").write_text("\n\n\n".join(parts) + "\n", encoding="utf-8")
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "third-party-licenses")
    args = parser.parse_args(argv)
    entries = collect(args.output)
    print(f"Collected notices for {len(entries)} components into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

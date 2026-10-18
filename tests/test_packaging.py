"""The macOS app build: what it bundles, its notices, launch cache and resources."""
import os
import platform
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import PyQt6
from macholib.MachO import MachO

from src import app_paths
from src.version import BUNDLE_ID, MACOS_MINIMUM_VERSION, VERSION
from tools import bundle_policy, check_app_bundle, collect_licenses

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_IN_APP = (
    "LICENSE", "THIRD_PARTY_NOTICES.md", "licenses/LGPL-3.0-only.txt",
    "licenses/Qt-6.10.2-third-party.txt", "licenses/third-party/INDEX.md",
    "licenses/third-party/THIRD_PARTY_LICENSES.txt",
    "examples/NumeriPlot_example_project.json",
)


def test_build_script_removes_only_its_own_outputs():
    script = (ROOT / "build_macos.sh").read_text(encoding="utf-8")

    assert "rm -rf build dist" not in script
    targets = script.split("for old in ", 1)[1].split("; do", 1)[0].split()
    for target in targets:
        assert target == "build/dmg" or any(
            name in target for name in ("${APP_SLUG}", "${APP_PATH}", "${DMG_PATH}")), target
    for step in ("tools/collect_licenses.py", "tools/check_app_bundle.py",
                 "codesign --verify --deep --strict", "hdiutil create", "macosx_12_0_arm64"):
        assert step in script


@pytest.mark.parametrize("dest, excluded", [
    ("PyQt6/Qt6/lib/QtPdf.framework/Versions/A/QtPdf", True),
    ("PyQt6/Qt6/lib/QtNetwork.framework", True),
    ("PyQt6/Qt6/plugins/imageformats/libqpdf.dylib", True),
    ("PyQt6/Qt6/plugins/generic/libqtuiotouchplugin.dylib", True),
    ("PyQt6/Qt6/plugins/imageformats/libqtiff.dylib", True),
    ("PyQt6/Qt6/lib/QtDBus.framework/Versions/A/QtDBus", False),
    ("PyQt6/Qt6/lib/QtSvg.framework/Versions/A/QtSvg", False),
    ("PyQt6/Qt6/lib/QtWidgets.framework/Versions/A/QtWidgets", False),
    ("PyQt6/Qt6/plugins/imageformats/libqjpeg.dylib", False),
    ("PyQt6/Qt6/plugins/platforms/libqcocoa.dylib", False),
    ("PyQt6/Qt6/lib/QtPdfWidgets.framework", False),
])
def test_bundle_policy_drops_only_unused_qt_parts(dest, excluded):
    assert bundle_policy.is_excluded(dest) is excluded


@pytest.mark.parametrize("entry, excluded", [
    (("QtPdf", "PyQt6/Qt6/lib/QtPdf.framework/Versions/A/QtPdf", "SYMLINK"), True),
    (("QtNetwork", "PyQt6/Qt6/lib/QtNetwork.framework/Versions/A/QtNetwork", "SYMLINK"), True),
    (("QtGui", "PyQt6/Qt6/lib/QtGui.framework/Versions/A/QtGui", "SYMLINK"), False),
    (("QtPdf", "/synthetic/QtPdf", "BINARY"), False),
])
def test_links_to_excluded_qt_parts_are_dropped_too(entry, excluded):
    assert bundle_policy.is_excluded_entry(*entry) is excluded


def test_kept_qt_libraries_do_not_need_the_excluded_frameworks():
    qt = Path(PyQt6.__file__).parent / "Qt6"
    kept = [qt / "lib" / f"{name}.framework" / "Versions" / "A" / name
            for name in ("QtCore", "QtGui", "QtDBus", "QtWidgets", "QtSvg")]
    kept += [path for path in (qt / "plugins").glob("*/*.dylib")
             if path.parent.name in ("platforms", "styles", "iconengines", "imageformats", "generic")
             and not bundle_policy.is_excluded(f"PyQt6/Qt6/plugins/{path.parent.name}/{path.name}")]
    assert len(kept) > 5
    for path in kept:
        for header in MachO(str(path)).headers:
            for _, _, name in header.walkRelocatables():
                assert not any(f"{framework}.framework" in name
                               for framework in bundle_policy.EXCLUDED_QT_FRAMEWORKS), (path.name, name)


def test_license_collection_covers_every_bundled_component(tmp_path):
    output = tmp_path / "notices"
    entries = collect_licenses.collect(output)

    names = {name.lower().replace("_", "-") for name, *_ in entries}
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            assert line.split("==")[0].lower().replace("_", "-") in names
    assert {"python", "pyinstaller"} <= names
    index = (output / "INDEX.md").read_text(encoding="utf-8")
    assert "| Qt modules (qtbase, qtsvg) | 6.10.2 |" in index
    text = (output / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    for expected in ("GNU LESSER GENERAL PUBLIC LICENSE", "GCC RUNTIME LIBRARY EXCEPTION",
                     "libquadmath", "Data Compression Library (zlib)", "LICENSE_DEJAVU",
                     "LICENSE_COLORBREWER", "bootloader exception"):
        assert expected in text, expected
    assert "/Users/" not in text and "/home/" not in text


def test_stale_repository_notices_stop_collection(tmp_path, monkeypatch):
    stale = tmp_path / "matplotlib-0.0.1"
    stale.mkdir()
    (stale / "LICENSE_SYNTHETIC").write_text("synthetic", encoding="utf-8")
    monkeypatch.setattr(collect_licenses, "TRACKED_NOTICES", tmp_path)

    with pytest.raises(SystemExit, match="matplotlib-0.0.1"):
        collect_licenses.collect(tmp_path / "out")


def synthetic_app(tmp_path):
    contents = tmp_path / "NumeriPlot.app" / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    shutil.copyfile(Path(sys.executable).resolve(), contents / "MacOS" / "NumeriPlot")
    (contents / "Info.plist").write_bytes(plistlib.dumps({
        "CFBundleExecutable": "NumeriPlot", "CFBundleShortVersionString": VERSION,
        "CFBundleIdentifier": BUNDLE_ID, "LSMinimumSystemVersion": MACOS_MINIMUM_VERSION,
    }))
    for name in REQUIRED_IN_APP:
        path = contents / "Resources" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic", encoding="utf-8")
    return contents.parent


@pytest.mark.skipif(platform.machine() != "arm64", reason="the app targets Apple Silicon")
def test_bundle_check_accepts_a_complete_app(tmp_path):
    assert check_app_bundle.problems(synthetic_app(tmp_path)) == []


@pytest.mark.skipif(platform.machine() != "arm64", reason="the app targets Apple Silicon")
def test_bundle_check_reports_missing_notices_and_excluded_qt(tmp_path):
    app = synthetic_app(tmp_path)
    (app / "Contents/Resources/examples/NumeriPlot_example_project.json").unlink()
    pdf = app / "Contents/Frameworks/PyQt6/Qt6/lib/QtPdf.framework/QtPdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_text("synthetic", encoding="utf-8")

    (app / "Contents/Resources/QtNetwork").symlink_to("PyQt6/Qt6/lib/QtNetwork.framework/QtNetwork")

    found = check_app_bundle.problems(app)
    assert "missing examples/NumeriPlot_example_project.json" in found
    assert "excluded Qt part present: PyQt6/Qt6/lib/QtPdf.framework" in found
    assert "dangling link: Contents/Resources/QtNetwork" in found


def test_packaged_app_keeps_matplotlib_cache_between_launches(tmp_path, monkeypatch):
    import main

    hook_dir = tmp_path / "pyinstaller-temporary"
    hook_dir.mkdir()
    cache = tmp_path / "Caches" / "NumeriPlot" / "matplotlib"
    monkeypatch.setenv("MPLCONFIGDIR", str(hook_dir))
    monkeypatch.setattr(main, "_matplotlib_cache_dir", lambda: cache)

    assert main._use_persistent_matplotlib_cache() == cache
    assert cache.is_dir()
    assert os.environ["MPLCONFIGDIR"] == str(cache)
    assert not hook_dir.exists()


def test_matplotlib_cache_falls_back_to_the_temporary_folder(tmp_path, monkeypatch):
    import main

    hook_dir = tmp_path / "pyinstaller-temporary"
    hook_dir.mkdir()
    blocker = tmp_path / "not-a-folder"
    blocker.write_text("synthetic", encoding="utf-8")
    monkeypatch.setenv("MPLCONFIGDIR", str(hook_dir))
    monkeypatch.setattr(main, "_matplotlib_cache_dir", lambda: blocker / "matplotlib")

    assert main._use_persistent_matplotlib_cache() is None
    assert os.environ["MPLCONFIGDIR"] == str(hook_dir)
    assert hook_dir.is_dir()


def test_font_cache_is_built_without_the_slow_macos_font_query(tmp_path):
    script = '''
import subprocess
calls = []
real = subprocess.check_output
def recording(args, *pargs, **kwargs):
    calls.append(args[0])
    return real(args, *pargs, **kwargs)
subprocess.check_output = recording
import main
main._build_matplotlib_font_cache()
import matplotlib.font_manager as font_manager
assert "system_profiler" not in calls, calls
assert subprocess.check_output is recording
assert any(font.name == "DejaVu Sans" for font in font_manager.fontManager.ttflist)
'''
    result = subprocess.run([sys.executable, "-c", script], cwd=ROOT, capture_output=True,
                            text=True, timeout=120,
                            env=dict(os.environ, MPLCONFIGDIR=str(tmp_path)))

    assert result.returncode == 0, result.stderr
    assert list(tmp_path.glob("fontlist-*.json"))


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS cache location")
def test_matplotlib_cache_lives_in_the_users_caches_folder(tmp_path, monkeypatch):
    import main

    monkeypatch.setattr(main.Path, "home", lambda: tmp_path)
    assert main._matplotlib_cache_dir() == tmp_path / "Library/Caches/NumeriPlot/matplotlib"


def test_resources_come_from_the_checkout_or_the_app(tmp_path, monkeypatch):
    assert app_paths.example_project_path() == ROOT / "examples/NumeriPlot_example_project.json"
    assert app_paths.example_project_path().is_file()

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert app_paths.example_project_path() == tmp_path / "examples/NumeriPlot_example_project.json"
    assert app_paths.third_party_notices_path() == tmp_path / "THIRD_PARTY_NOTICES.md"
    collected = tmp_path / "licenses/third-party/THIRD_PARTY_LICENSES.txt"
    collected.parent.mkdir(parents=True)
    collected.write_text("synthetic", encoding="utf-8")
    assert app_paths.third_party_notices_path() == collected

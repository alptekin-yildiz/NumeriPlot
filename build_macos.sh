#!/bin/bash
# NumeriPlot — macOS app and disk image build (Apple Silicon)
# Usage: bash build_macos.sh

set -euo pipefail

cd -- "$(dirname -- "$0")"

if [ -z "${VIRTUAL_ENV:-}" ]; then
  if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
  elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
  else
    echo "ERROR: No active virtual environment found. Run: bash setup.sh --dev"
    exit 1
  fi
fi

PYTHON_BIN=$(command -v python3 || true)
if [ -z "${PYTHON_BIN}" ]; then
  echo "ERROR: python3 not found in the active environment."
  exit 1
fi

if [ "$(uname -s)" != "Darwin" ] || [ "$(uname -m)" != "arm64" ]; then
  echo "ERROR: Build the NumeriPlot app on an Apple Silicon Mac."
  exit 1
fi

if ! "${PYTHON_BIN}" -m PyInstaller --version >/dev/null 2>&1; then
  echo "ERROR: PyInstaller is missing from the active environment."
  echo "Install the pinned tools first: bash setup.sh --dev"
  exit 1
fi

META=$("${PYTHON_BIN}" -c "from src.version import APP_NAME, APP_SLUG, DISPLAY_VERSION, DMG_BASENAME, VERSION; print('|'.join([APP_NAME, APP_SLUG, DISPLAY_VERSION, DMG_BASENAME, VERSION]))")
IFS='|' read -r APP_NAME APP_SLUG DISPLAY_VERSION DMG_NAME VERSION <<< "${META}"
SPEC_FILE="${APP_SLUG}.spec"
ICON_FILE="${APP_SLUG}.icns"
APP_PATH="dist/${APP_SLUG}.app"
DMG_PATH="dist/${DMG_NAME}"

echo "================================================"
echo " ${APP_NAME} — macOS Build"
echo " ${DISPLAY_VERSION}"
echo "================================================"
echo ""

if [ ! -f "${SPEC_FILE}" ]; then
  echo "ERROR: ${SPEC_FILE} not found in project root."
  exit 1
fi

if [ ! -f "${ICON_FILE}" ]; then
  echo "ERROR: ${ICON_FILE} not found in project root."
  exit 1
fi

echo "Checking the SciPy build input..."
"${PYTHON_BIN}" - <<'PY'
from importlib.metadata import distribution

scipy = distribution("scipy")
tags = [line.split(":", 1)[1].strip() for line in scipy.read_text("WHEEL").splitlines()
        if line.startswith("Tag:")]
# SciPy 1.15.2's macOS 14 wheel fails to import on macOS 27; its macOS 12
# wheel runs on every macOS version the app supports.
if scipy.version == "1.15.2" and not any(tag.endswith("macosx_12_0_arm64") for tag in tags):
    raise SystemExit(
        f"ERROR: SciPy {scipy.version} is the {', '.join(tags)} build; the app needs "
        "macosx_12_0_arm64. Install it with:\n"
        "  python3 -m pip download --only-binary=:all: --no-deps --platform macosx_12_0_arm64 "
        "--python-version 3.11 --implementation cp --abi cp311 --dest build/wheels scipy==1.15.2\n"
        "  python3 -m pip install --force-reinstall --no-deps "
        "build/wheels/scipy-1.15.2-cp311-cp311-macosx_12_0_arm64.whl")
print(f"SciPy {scipy.version}: {', '.join(tags)}")
PY

echo "Collecting third-party license notices..."
"${PYTHON_BIN}" tools/collect_licenses.py --output build/third-party-licenses

echo "Removing the previous ${APP_NAME} build outputs..."
# Only this script's own outputs: dist/ also holds backups and release materials.
for old in "build/${APP_SLUG}" build/dmg "dist/${APP_SLUG}" "${APP_PATH}" "${DMG_PATH}" "${DMG_PATH}.sha256"; do
  if [ -e "${old}" ] || [ -L "${old}" ]; then
    chmod -R u+w "${old}" 2>/dev/null || true
    rm -rf "${old}"
  fi
done

echo "Starting build..."
"${PYTHON_BIN}" -m PyInstaller "${SPEC_FILE}" --noconfirm --clean

if [ ! -d "${APP_PATH}" ]; then
  echo "Build failed: ${APP_PATH} not found."
  exit 1
fi
# The .app is the only product; PyInstaller's intermediate folder is not shipped.
rm -rf "dist/${APP_SLUG}"

echo "Checking the app..."
codesign --verify --deep --strict "${APP_PATH}"
"${PYTHON_BIN}" tools/check_app_bundle.py "${APP_PATH}"

APP_SIZE=$(du -sh "${APP_PATH}" | cut -f1)

echo "Creating the disk image..."
mkdir -p build/dmg
ditto "${APP_PATH}" "build/dmg/${APP_SLUG}.app"
ln -s /Applications build/dmg/Applications
cp "assets/dmg/Lisanslar - Licenses.txt" build/dmg/
hdiutil create -volname "${APP_NAME} ${VERSION}" -srcfolder build/dmg \
  -fs HFS+ -format UDZO -ov "${DMG_PATH}" >/dev/null
hdiutil verify "${DMG_PATH}" >/dev/null
rm -rf build/dmg
(cd dist && shasum -a 256 "${DMG_NAME}" > "${DMG_NAME}.sha256")
# Users receive the disk image, so test the app from there. A second copy in
# dist/ would also show up in Spotlight next to the installed app.
rm -rf "${APP_PATH}"

echo ""
echo "================================================"
echo " Build successful"
echo " Disk image: ${DMG_PATH} ($(du -sh "${DMG_PATH}" | cut -f1); app ${APP_SIZE})"
echo " Checksum:   ${DMG_PATH}.sha256"
echo " Test:       open ${DMG_PATH}"
echo " Sources:    python3 tools/fetch_release_sources.py"
echo "================================================"

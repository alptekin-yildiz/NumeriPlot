#!/bin/bash
# NumeriPlot — macOS .app Build Script
# Usage: bash build_macos.sh

set -euo pipefail

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

if ! "${PYTHON_BIN}" -m PyInstaller --version >/dev/null 2>&1; then
  echo "ERROR: PyInstaller is missing from the active environment."
  echo "Install the pinned tools first: bash setup.sh --dev"
  exit 1
fi

META=$("${PYTHON_BIN}" -c "from src.version import APP_NAME, APP_SLUG, DISPLAY_VERSION, ZIP_BASENAME; print('|'.join([APP_NAME, APP_SLUG, DISPLAY_VERSION, ZIP_BASENAME]))")
IFS='|' read -r APP_NAME APP_SLUG DISPLAY_VERSION ZIP_NAME <<< "${META}"
SPEC_FILE="${APP_SLUG}.spec"
ICON_FILE="${APP_SLUG}.icns"

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

# Prevent permission issues on previous artifacts.
if [ -d build ]; then
  chmod -R u+w build || true
fi
if [ -d dist ]; then
  chmod -R u+w dist || true
fi

echo "Cleaning previous build artifacts..."
rm -rf build dist

echo "Starting build..."
"${PYTHON_BIN}" -m PyInstaller "${SPEC_FILE}" --noconfirm --clean

APP_PATH="dist/${APP_SLUG}.app"
if [ -d "${APP_PATH}" ]; then
  SIZE=$(du -sh "${APP_PATH}" | cut -f1)
  echo "Creating ZIP package..."
  ditto -c -k --sequesterRsrc --keepParent "${APP_PATH}" "dist/${ZIP_NAME}"
  ZIP_SIZE=$(du -sh "dist/${ZIP_NAME}" | cut -f1)
  echo ""
  echo "================================================"
  echo " Build successful"
  echo " Output: ${APP_PATH} (${SIZE})"
  echo " Package: dist/${ZIP_NAME} (${ZIP_SIZE})"
  echo " Test: open ${APP_PATH}"
  echo "================================================"
else
  echo "Build failed: ${APP_PATH} not found."
  exit 1
fi

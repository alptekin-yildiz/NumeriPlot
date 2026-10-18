#!/bin/bash
# NumeriPlot — macOS Setup Script
# Usage: bash setup.sh [--dev]

set -euo pipefail
cd -- "$(dirname -- "$0")"

INSTALL_DEV=0
case "${1:-}" in
  "") ;;
  --dev) INSTALL_DEV=1 ;;
  -h|--help)
    echo "Usage: bash setup.sh [--dev]"
    echo "  --dev  Install pinned test, lint, and packaging tools."
    exit 0
    ;;
  *)
    echo "ERROR: Unknown option: $1" >&2
    echo "Usage: bash setup.sh [--dev]" >&2
    exit 2
    ;;
esac

if [ "$#" -gt 1 ]; then
  echo "ERROR: Too many arguments." >&2
  echo "Usage: bash setup.sh [--dev]" >&2
  exit 2
fi

PYTHON_BIN=""
if [ -d venv ]; then
  if [ -x venv/bin/python3 ] && ./venv/bin/python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
    PYTHON_BIN="$PWD/venv/bin/python3"
  else
    echo "Mevcut sanal ortam çalışmıyor veya Python sürümü eski. Yeni bir kaynak kopyasında kurulum yapın."
    echo "Existing virtual environment is broken or too old. Install in a fresh source copy."
    echo "Kılavuz / Guide: docs/SOURCE_INSTALL_TR.md / docs/SOURCE_INSTALL.md"
    exit 1
  fi
else
  for candidate in python3.11 python3; do
    candidate_path=$(command -v "$candidate" || true)
    if [ -n "$candidate_path" ] && "$candidate_path" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
      PYTHON_BIN="$candidate_path"
      break
    fi
  done
fi
if [ -z "${PYTHON_BIN}" ]; then
  echo "Python 3.11+ bulunamadı / Python 3.11+ not found."
  echo "Kılavuz / Guide: docs/SOURCE_INSTALL_TR.md / docs/SOURCE_INSTALL.md"
  exit 1
fi

META=$("${PYTHON_BIN}" -c "from src.version import APP_NAME, DISPLAY_VERSION; print(f'{APP_NAME}|{DISPLAY_VERSION}')")
IFS='|' read -r APP_NAME DISPLAY_VERSION <<< "${META}"
echo "================================================"
echo " ${APP_NAME} — ${DISPLAY_VERSION}"
echo " Setup starting..."
echo "================================================"

PY_VER=$("${PYTHON_BIN}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$("${PYTHON_BIN}" -c "import sys; print(sys.version_info.major)")
PY_MINOR=$("${PYTHON_BIN}" -c "import sys; print(sys.version_info.minor)")

echo "Python ${PY_VER} found."

if [ "${PY_MAJOR}" -lt 3 ] || ([ "${PY_MAJOR}" -eq 3 ] && [ "${PY_MINOR}" -lt 11 ]); then
  echo "ERROR: Python 3.11+ required. Found: ${PY_VER}"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  "${PYTHON_BIN}" -m venv venv
fi

source venv/bin/activate
VENV_PYTHON="$PWD/venv/bin/python3"

echo "Installing dependencies..."
"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -r requirements.txt

if [ "${INSTALL_DEV}" -eq 1 ]; then
  echo "Installing development dependencies..."
  "${VENV_PYTHON}" -m pip install -r requirements-dev.txt
fi

echo "Checking startup imports / Açılış kontrolü..."
"${VENV_PYTHON}" -m src.runtime_check --repair

echo ""
echo "================================================"
echo " Setup complete"
echo ""
echo "Run app:"
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo ""
if [ "${INSTALL_DEV}" -eq 1 ]; then
  echo "Test or build:"
  echo "  bash release_check.sh"
  echo "  bash build_macos.sh"
else
  echo "For test and build tools:"
  echo "  bash setup.sh --dev"
fi
echo "================================================"

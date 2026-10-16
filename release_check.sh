#!/usr/bin/env bash
# NumeriPlot - Release Gate

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

step() {
  echo ""
  echo "==> $1"
}

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

PYTHON_BIN=$(command -v python3 || true)
[ -n "${PYTHON_BIN}" ] || fail "python3 not found."

step "Environment"
echo "PYTHON=${PYTHON_BIN}"
"${PYTHON_BIN}" --version

step "Pinned dependencies"
"${PYTHON_BIN}" - <<'PY'
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


problems = []
checked = 0
for requirements_file in ("requirements.txt", "requirements-dev.txt"):
    for raw_line in Path(requirements_file).read_text(encoding="utf-8").splitlines():
        requirement = raw_line.strip()
        if not requirement or requirement.startswith("#"):
            continue
        if "==" not in requirement:
            problems.append(f"{requirements_file}: unpinned entry: {requirement}")
            continue
        package, expected = requirement.split("==", 1)
        try:
            actual = version(package)
        except PackageNotFoundError:
            problems.append(f"{package}: missing (expected {expected})")
            continue
        checked += 1
        if actual != expected:
            problems.append(f"{package}: installed {actual}, expected {expected}")

if problems:
    print("Pinned dependency check failed:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print(f"Pinned dependency versions OK ({checked} packages).")
PY

"${PYTHON_BIN}" -m pytest --version \
  || fail "pytest is missing. Run: bash setup.sh --dev"
"${PYTHON_BIN}" -m PyInstaller --version \
  || fail "PyInstaller is missing. Run: bash setup.sh --dev"
"${PYTHON_BIN}" -m ruff --version \
  || fail "Ruff is missing. Run: bash setup.sh --dev"

step "Version"
"${PYTHON_BIN}" - <<'PY'
from src.version import VERSION, APP_VERSION, DISPLAY_VERSION
print(f"VERSION={VERSION}")
print(f"APP_VERSION={APP_VERSION}")
print(f"DISPLAY_VERSION={DISPLAY_VERSION}")
PY

step "Shell script syntax check"
bash -n NumeriPlot.command
bash -n setup.sh
bash -n build_macos.sh
bash -n release_check.sh

step "Python syntax check (project files)"
"${PYTHON_BIN}" - <<'PY'
import pathlib
import py_compile
from src.version import APP_SLUG

paths = [pathlib.Path("main.py"), pathlib.Path(f"{APP_SLUG}.spec")]
for folder in ("src", "lang", "models", "tests", "examples"):
    paths.extend(sorted(pathlib.Path(folder).rglob("*.py")))

for p in paths:
    py_compile.compile(str(p), doraise=True)

print(f"Compiled {len(paths)} Python files.")
PY

step "Ruff correctness check"
"${PYTHON_BIN}" -m ruff check --no-cache main.py src lang models tests examples

step "TR/EN key parity check"
"${PYTHON_BIN}" - <<'PY'
from lang.tr import STRINGS as TR
from lang.en import STRINGS as EN

tr_keys = set(TR.keys())
en_keys = set(EN.keys())
only_tr = sorted(tr_keys - en_keys)
only_en = sorted(en_keys - tr_keys)

if only_tr or only_en:
    if only_tr:
        print("Keys only in TR:")
        for k in only_tr:
            print(f"  - {k}")
    if only_en:
        print("Keys only in EN:")
        for k in only_en:
            print(f"  - {k}")
    raise SystemExit(1)

print(f"TR/EN key parity OK ({len(tr_keys)} keys).")
PY

step "Unit tests"
PYTHONPATH=. "${PYTHON_BIN}" -m pytest -q

echo ""
echo "Release gate PASSED."

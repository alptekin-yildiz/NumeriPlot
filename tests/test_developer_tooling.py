from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _requirements(path: str) -> set[str]:
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.startswith("#")}


def test_runtime_and_development_dependencies_are_separate_and_pinned():
    runtime = _requirements("requirements.txt")
    development = _requirements("requirements-dev.txt")

    assert "pytest==9.1.1" in development
    assert "PyInstaller==6.22.2" in development
    assert "pyinstaller-hooks-contrib==2026.7" in development
    assert "altgraph==0.17.5" in development
    assert "macholib==1.16.4" in development
    assert "ruff==0.16.5" in development
    assert not any(
        requirement.lower().startswith(("pytest", "pyinstaller", "ruff"))
        for requirement in runtime
    )
    assert all("==" in requirement for requirement in runtime | development)


def test_build_requires_preinstalled_pinned_tooling():
    build_script = (ROOT / "build_macos.sh").read_text(encoding="utf-8")

    assert "pip install pyinstaller" not in build_script.lower()
    assert "requirements-dev.txt" not in build_script
    assert "bash setup.sh --dev" in build_script
    assert '"${PYTHON_BIN}" -m PyInstaller' in build_script


def test_release_gate_uses_one_python_environment_and_ruff():
    release_script = (ROOT / "release_check.sh").read_text(encoding="utf-8")

    assert 'PYTHON_BIN=$(command -v python3 || true)' in release_script
    assert '"${PYTHON_BIN}" -m pytest -q' in release_script
    assert '"${PYTHON_BIN}" -m PyInstaller --version' in release_script
    assert '"${PYTHON_BIN}" -m ruff check --no-cache' in release_script
    assert '("requirements.txt", "requirements-dev.txt")' in release_script
    assert "PYTHONPATH=. pytest -q" not in release_script


def test_ruff_is_limited_to_correctness_checks_for_recovered_baseline():
    config = (ROOT / "ruff.toml").read_text(encoding="utf-8")

    assert 'target-version = "py311"' in config
    assert 'select = ["E9", "F63", "F7", "F82"]' in config


def test_ci_runs_the_release_gate_with_pinned_read_only_actions():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "permissions:\n  contents: read" in workflow
    assert "runs-on: macos-14" in workflow
    assert 'QT_QPA_PLATFORM: "offscreen"' in workflow
    assert 'python-version: "3.11"' in workflow
    assert (
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
        in workflow
    )
    assert (
        "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97"
        in workflow
    )
    assert "persist-credentials: false" in workflow
    assert (
        "python -m pip install -r requirements.txt -r requirements-dev.txt"
        in workflow
    )
    assert "bash release_check.sh" in workflow
    assert "build_macos.sh" not in workflow

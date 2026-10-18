"""Exercise the Finder launcher's working directory and failure handling."""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def checkout(tmp_path):
    folder = tmp_path / "NumeriPlot with spaces"
    folder.mkdir()
    shutil.copy2(ROOT / "NumeriPlot.command", folder)
    (folder / "main.py").write_text("# synthetic launcher fixture\n")
    return folder


def launch(checkout):
    return subprocess.run(
        ["bash", str(checkout / "NumeriPlot.command")],
        cwd=checkout.parent, input="", capture_output=True, text=True, timeout=5,
    )


def test_missing_environment_explains_setup(checkout):
    result = launch(checkout)
    assert result.returncode == 1
    assert "First-time setup" in result.stdout
    assert "SOURCE_INSTALL_TR.md" in result.stdout
    assert "SOURCE_INSTALL.md" in result.stdout


@pytest.mark.parametrize("exit_code", [0, 7])
def test_launch_from_other_directory_and_preserve_exit_status(checkout, exit_code):
    interpreter = checkout / "venv/bin/python"
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text(
        '#!/bin/bash\n[ -f main.py ] || exit 99\n'
        '[ "$1" = main.py ] || exit 98\n'
        f'exit {exit_code}\n'
    )
    interpreter.chmod(0o755)
    result = launch(checkout)
    assert result.returncode == exit_code
    assert ("Launch failed" in result.stdout) == bool(exit_code)


def test_moved_launcher_explains_location(checkout):
    (checkout / 'main.py').unlink()
    result = launch(checkout)
    assert result.returncode == 1
    assert 'Finder alias' in result.stdout
    assert 'First-time setup' not in result.stdout

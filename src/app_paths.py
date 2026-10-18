"""Paths to files shipped with NumeriPlot, in a source checkout or the app."""
import sys
from pathlib import Path

EXAMPLE_PROJECT = Path("examples") / "NumeriPlot_example_project.json"
COLLECTED_NOTICES = Path("licenses") / "third-party" / "THIRD_PARTY_LICENSES.txt"


def resource_root() -> Path:
    """PyInstaller's resource folder in the app, the repository otherwise."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]


def example_project_path() -> Path:
    return resource_root() / EXAMPLE_PROJECT


def third_party_notices_path() -> Path:
    """Full notices collected into the app; the review document in a checkout."""
    collected = resource_root() / COLLECTED_NOTICES
    if collected.is_file():
        return collected
    return resource_root() / "THIRD_PARTY_NOTICES.md"

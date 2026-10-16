"""Keep one Qt application alive across all GUI test modules."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    # Qt widgets and Matplotlib can outlive a module-scoped fixture.
    # Recreating QApplication while those objects exist is unsafe.
    app = QApplication.instance() or QApplication([])
    yield app

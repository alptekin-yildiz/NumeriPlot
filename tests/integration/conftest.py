"""Keep one Qt application alive across all GUI test modules."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    # Qt widgets and Matplotlib can outlive a module-scoped fixture.
    # Recreating QApplication while those objects exist is unsafe.
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def flush_deleted_widgets(qapp):
    yield
    # processEvents() alone does not deliver DeferredDelete without exec().
    # Finish deleteLater() before another window changes the global stylesheet.
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qapp.processEvents()

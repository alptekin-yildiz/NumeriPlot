import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from src.ui.main_window import MainWindow
from src.version import WINDOW_TITLE


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "legacy_v2_project.json"
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_legacy_v2_project_opens_and_saves_as_schema_v1(
    qapp, monkeypatch, tmp_path
):
    """Open a synthetic legacy project without overwriting its source file."""
    source_path = tmp_path / "legacy_source.json"
    original = FIXTURE_PATH.read_text(encoding="utf-8")
    source_path.write_text(original, encoding="utf-8")
    converted_path = tmp_path / "converted_project.json"
    errors = []
    save_dialog_calls = []
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(source_path), "JSON Files (*.json)"),
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (
            save_dialog_calls.append(True) or str(converted_path),
            "JSON Files (*.json)",
        ),
    )
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Ok,
    )
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda _parent, _title, message, **_kwargs: errors.append(message),
    )

    window = MainWindow()
    try:
        window.open_project_action()

        assert errors == []
        assert window.windowTitle() == WINDOW_TITLE
        assert list(window.data_manager.df.columns) == ["Time", "Signal"]
        assert window.data_manager.df.shape == (3, 2)
        assert window.canvas.panel_names == ["Synthetic Legacy Panel"]
        assert window.canvas.panel_configs[0]["title"] == "Synthetic legacy project"
        assert len(window.series_list) == 1
        assert window.series_list[0]["label"] == "Synthetic signal"
        np.testing.assert_allclose(window.series_list[0]["x"], [0.0, 1.0, 2.0])
        np.testing.assert_allclose(window.series_list[0]["y"], [1.0, 2.0, 4.0])
        assert window.text_items[0]["text"] == "Synthetic fixture"

        window.save_project_action()

        assert errors == []
        assert save_dialog_calls == [True]
        assert source_path.read_text(encoding="utf-8") == original
        saved = json.loads(converted_path.read_text(encoding="utf-8"))
        assert saved["schema_version"] == "1.0"
        assert "version" not in saved
        assert saved["raw_data"].startswith("Time,Signal\n")
        assert saved["panel_configs"][0]["title"] == "Synthetic legacy project"
        assert saved["series"][0]["label"] == "Synthetic signal"
        assert saved["text_items"][0]["text"] == "Synthetic fixture"
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()

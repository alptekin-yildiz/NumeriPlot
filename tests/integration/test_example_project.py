import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from src.ui.main_window import MainWindow


PROJECT_PATH = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "NumeriPlot_example_project.json"
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_synthetic_example_project_opens_and_round_trips(
    qapp, monkeypatch, tmp_path
):
    errors = []
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(PROJECT_PATH), "JSON Files (*.json)"),
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
        assert list(window.data_manager.df.columns) == ["x", "y", "y_error"]
        assert window.data_manager.df.shape == (101, 3)
        assert window.canvas.panel_names == ["Gaussian Peak"]
        assert window.canvas.panel_configs[0]["title"] == (
            "Synthetic Gaussian Peak and Fit"
        )
        assert len(window.series_list) == 1
        assert window.series_list[0]["label"] == "Synthetic observations"
        assert len(window.fit_list) == 1
        assert window.fit_list[0]["model_name"] == "Gaussian Distribution"
        assert window.fit_list[0]["r2"] > 0.98
        assert "Synthetic data only" in window.text_items[0]["text"]

        round_trip_path = tmp_path / "example_round_trip.json"
        window._current_project_path = str(round_trip_path)
        window.save_project_action()

        assert errors == []
        saved = json.loads(round_trip_path.read_text(encoding="utf-8"))
        assert saved["schema_version"] == "1.0"
        assert "version" not in saved
        assert saved["series"][0]["label"] == "Synthetic observations"
        assert saved["fits"][0]["model_name"] == "Gaussian Distribution"
        assert "Synthetic data only" in saved["text_items"][0]["text"]
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_unknown_project_schema_is_rejected_before_loading(
    qapp, monkeypatch, tmp_path
):
    future_path = tmp_path / "future_project.json"
    future_path.write_text(
        json.dumps(
            {
                "schema_version": "2.0",
                "raw_data": "x,y\n0,1\n",
                "series": [],
            }
        ),
        encoding="utf-8",
    )
    errors = []
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(future_path), "JSON Files (*.json)"),
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

        assert len(errors) == 1
        assert window.table_w.rowCount() == 0
        assert window.table_w.columnCount() == 0
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()

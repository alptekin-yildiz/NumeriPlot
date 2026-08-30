import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PyQt6.QtWidgets import QApplication, QFormLayout, QMessageBox

from src.analysis.data_manager import DataManager
from src.ui.data_ops_dialog import DataOpsDialog


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.mark.parametrize(
    ("signal", "peak_type", "distance", "expected_x", "expected_y"),
    [
        (
            [0.0, 5.0, 0.0, np.nan, 0.0, 4.0, 0.0, 3.0, 0.0],
            0,
            1,
            [1.0, 5.0, 7.0],
            [5.0, 4.0, 3.0],
        ),
        (
            [5.0, 0.0, 5.0, 1.0, 5.0, 0.0, 5.0],
            1,
            1,
            [1.0, 3.0, 5.0],
            [0.0, 1.0, 0.0],
        ),
        (
            [0.0, 5.0, 0.0, 4.0, 0.0, 3.0, 0.0],
            0,
            3,
            [1.0, 5.0],
            [5.0, 3.0],
        ),
    ],
    ids=("maximum-with-nan", "minimum", "minimum-distance"),
)
def test_peak_finding_preview_and_apply_scenarios(
    qapp,
    monkeypatch,
    signal,
    peak_type,
    distance,
    expected_x,
    expected_y,
):
    manager = DataManager()
    manager.df = pd.DataFrame(
        {
            "x": np.arange(len(signal), dtype=float),
            "signal": signal,
        }
    )
    warnings = []
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Ok,
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, _title, message, **_kwargs: warnings.append(message),
    )

    dialog = DataOpsDialog(manager)
    try:
        dialog.combo_cat.setCurrentIndex(dialog.combo_cat.findData("peaks"))
        dialog.combo_op.setCurrentIndex(dialog.combo_op.findData("find_peaks"))
        dialog.combo_col_a.setCurrentText("signal")
        dialog.combo_col_b.setCurrentText("x")
        peak_type_widget = dialog.params_layout.itemAt(
            0, QFormLayout.ItemRole.FieldRole
        ).widget()
        height_widget = dialog.params_layout.itemAt(
            1, QFormLayout.ItemRole.FieldRole
        ).widget()
        distance_widget = dialog.params_layout.itemAt(
            2, QFormLayout.ItemRole.FieldRole
        ).widget()
        peak_type_widget.setCurrentIndex(peak_type)
        height_widget.setValue(0.0)
        distance_widget.setValue(distance)
        dialog.inp_new_name_x.setText("detected_x")
        dialog.inp_new_name.setText("detected_y")

        dialog.btn_preview.click()
        assert dialog.btn_apply.isEnabled()
        dialog.btn_apply.click()

        assert warnings == []
        assert manager.df["detected_x"].dropna().tolist() == expected_x
        assert manager.df["detected_y"].dropna().tolist() == expected_y
    finally:
        dialog.close()
        dialog.deleteLater()
        qapp.processEvents()

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from matplotlib import ticker
from PIL import Image
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
    QPushButton,
)

from lang import get_language, t
from src.project_schema import write_project
from src.ui.dialogs import PlotSettingsDialog
from src.ui.main_window import MainWindow
from src.version import WINDOW_TITLE


PROJECT_PATH = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "NumeriPlot_example_project.json"
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _open_example(window, monkeypatch):
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

    window.act_open_proj.trigger()
    assert errors == []


def test_main_window_opens_headless_with_empty_workspace(qapp):
    window = MainWindow()
    try:
        window.show()
        qapp.processEvents()

        assert window.isVisible()
        assert window.windowTitle() == WINDOW_TITLE
        assert window.data_manager.df is None
        assert window.canvas.panel_count == 1
        assert window.table_w.rowCount() == 0
        assert window.table_w.columnCount() == 0
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_table_edit_and_undo_refresh_the_plotted_series(
    qapp, monkeypatch
):
    window = MainWindow()
    try:
        _open_example(window, monkeypatch)
        monkeypatch.setattr(
            QMessageBox,
            "question",
            lambda *_args, **_kwargs: QMessageBox.StandardButton.Yes,
        )
        original = float(window.data_manager.df.iat[0, 1])

        window.table_w.item(0, 1).setText("12.345")
        qapp.processEvents()

        assert float(window.data_manager.df.iat[0, 1]) == 12.345
        assert float(window.series_list[0]["y"][0]) == 12.345
        assert float(window.canvas.axes.lines[0].get_ydata()[0]) == 12.345
        assert window.btn_table_undo.isEnabled()

        window.btn_table_undo.click()
        qapp.processEvents()

        assert float(window.data_manager.df.iat[0, 1]) == original
        assert np.isclose(window.series_list[0]["y"][0], original)
        assert np.isclose(window.canvas.axes.lines[0].get_ydata()[0], original)
        assert not window.btn_table_undo.isEnabled()
    finally:
        monkeypatch.setattr(
            QMessageBox,
            "question",
            lambda *_args, **_kwargs: QMessageBox.StandardButton.Discard,
        )
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_role_based_y_only_series_can_be_fitted(qapp, monkeypatch, tmp_path):
    project_path = tmp_path / "y_only_project.json"
    write_project(
        project_path,
        {
            "raw_data": "signal\n2\n4\n6\n8\n10\n",
            "series": [],
            "fits": [],
        },
    )
    errors = []
    warnings = []
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), "JSON Files (*.json)"),
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
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, _title, message, **_kwargs: warnings.append(message),
    )
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Yes,
    )

    window = MainWindow()
    try:
        window.act_open_proj.trigger()
        template_index = window.combo_role_template.findData("all_y_left")
        window.combo_role_template.setCurrentIndex(template_index)
        window.btn_add_from_roles.click()

        assert len(window.series_list) == 1
        assert window.series_list[0]["x_col"] is None
        np.testing.assert_array_equal(
            window.series_list[0]["x"],
            np.array([1, 2, 3, 4, 5]),
        )
        np.testing.assert_array_equal(
            window.series_list[0]["y"],
            np.array([2, 4, 6, 8, 10]),
        )

        model_name = "Linear" if get_language() == "en" else "Doğrusal"
        window.lst_ser.setCurrentRow(0)
        window.combo_mod.setCurrentText(model_name)
        QTimer.singleShot(0, lambda: QApplication.activeModalWidget().accept())
        fit_button = next(
            button
            for button in window.findChildren(QPushButton)
            if button.text() == t("btn_fit")
        )
        fit_button.click()

        assert errors == []
        assert warnings == []
        assert len(window.fit_list) == 1
        np.testing.assert_allclose(
            window.fit_list[0]["param_values"],
            [2.0, 0.0],
            atol=1e-6,
        )
        assert window.fit_list[0]["r2"] == pytest.approx(1.0)
    finally:
        monkeypatch.setattr(
            QMessageBox,
            "question",
            lambda *_args, **_kwargs: QMessageBox.StandardButton.Discard,
        )
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_plot_settings_preserve_marker_and_legend_item_choices(
    qapp, monkeypatch
):
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Discard,
    )
    window = MainWindow()
    try:
        _open_example(window, monkeypatch)
        window.act_styles.trigger()
        qapp.processEvents()
        dialog = window.findChild(PlotSettingsDialog)
        button_box = dialog.findChild(QDialogButtonBox)

        dialog.tbl_legend_items.setCurrentCell(1, 3)
        dialog.btn_legend_up.click()
        dialog.tbl_legend_items.item(0, 3).setText("Gaussian fit first")
        dialog.tbl_legend_items.item(1, 3).setText("Hidden observations")
        dialog.tbl_legend_items.item(1, 0).setCheckState(
            Qt.CheckState.Unchecked
        )
        dialog.list_style_series.setCurrentRow(0)
        dialog.combo_marker.setCurrentIndex(2)
        button_box.button(
            QDialogButtonBox.StandardButton.Apply
        ).click()
        qapp.processEvents()

        data_series = window.series_list[0]
        saved_fit = window.fit_list[0]
        assert data_series["marker"] == "s"
        assert data_series["legend_show"] is False
        assert data_series["legend_label"] == "Hidden observations"
        assert data_series["legend_order"] == 1
        assert saved_fit["legend_show"] is True
        assert saved_fit["legend_label"] == "Gaussian fit first"
        assert saved_fit["legend_order"] == 0
        assert [text.get_text() for text in window.canvas.axes.get_legend().texts] == [
            "Gaussian fit first"
        ]
    finally:
        dialog = window.findChild(PlotSettingsDialog)
        if dialog is not None:
            dialog.close()
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_axis_settings_apply_left_right_and_scientific_formats(
    qapp, monkeypatch, tmp_path
):
    project_path = tmp_path / "dual_axis_project.json"
    base_style = {
        "plot_type": "scatter",
        "marker": "o",
        "linestyle": "-",
        "filled": True,
        "markersize": 4,
        "markeredgewidth": 0.5,
        "linewidth": 1.0,
        "capsize": 1,
        "alpha": 1.0,
        "panel_id": 0,
    }
    write_project(
        project_path,
        {
            "raw_data": "x,left,right\n1000,0.001,100\n2000,0.002,200\n",
            "series": [
                {
                    **base_style,
                    "label": "Left signal",
                    "x": [1000.0, 2000.0],
                    "y": [0.001, 0.002],
                    "x_col": "x",
                    "y_col": "left",
                    "axis": "left",
                    "color": "#3366cc",
                },
                {
                    **base_style,
                    "label": "Right signal",
                    "x": [1000.0, 2000.0],
                    "y": [100.0, 200.0],
                    "x_col": "x",
                    "y_col": "right",
                    "axis": "right",
                    "color": "#cc6633",
                },
            ],
            "fits": [],
        },
    )
    errors = []
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), "JSON Files (*.json)"),
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
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Discard,
    )

    window = MainWindow()
    try:
        window.act_open_proj.trigger()
        window.act_axes.trigger()
        qapp.processEvents()
        dialog = window.findChild(PlotSettingsDialog)
        button_box = dialog.findChild(QDialogButtonBox)
        dialog.combo_x_notation.setCurrentIndex(
            dialog.combo_x_notation.findData("e")
        )
        dialog.combo_y_notation.setCurrentIndex(
            dialog.combo_y_notation.findData("pow10")
        )
        dialog.combo_yr_notation.setCurrentIndex(
            dialog.combo_yr_notation.findData("e_offset")
        )
        button_box.button(
            QDialogButtonBox.StandardButton.Apply
        ).click()
        qapp.processEvents()

        cfg = window.canvas.panel_configs[0]
        assert errors == []
        assert cfg["x_tick_notation"] == "e"
        assert cfg["y_tick_notation"] == "pow10"
        assert cfg["y_right_tick_notation"] == "e_offset"
        assert isinstance(
            window.canvas.axes.xaxis.get_major_formatter(),
            ticker.FormatStrFormatter,
        )
        assert isinstance(
            window.canvas.axes.yaxis.get_major_formatter(),
            ticker.FuncFormatter,
        )
        right_axis = window.canvas.axes2_list[0]
        assert right_axis is not None
        assert isinstance(
            right_axis.yaxis.get_major_formatter(),
            ticker.ScalarFormatter,
        )
        assert window.canvas.axes.lines[0].get_label() == "Left signal"
        assert right_axis.lines[0].get_label() == "Right signal"
    finally:
        dialog = window.findChild(PlotSettingsDialog)
        if dialog is not None:
            dialog.close()
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_export_actions_create_readable_outputs(qapp, monkeypatch, tmp_path):
    window = MainWindow()
    try:
        _open_example(window, monkeypatch)
        plot_path = tmp_path / "plot.png"
        table_path = tmp_path / "table.csv"
        script_path = tmp_path / "figure.py"
        notebook_path = tmp_path / "figure.ipynb"
        destinations = iter(
            [
                (str(plot_path), "PNG (*.png)"),
                (str(table_path), "CSV (*.csv)"),
                (str(script_path), "Python Files (*.py)"),
                (str(notebook_path), "Jupyter Notebook (*.ipynb)"),
            ]
        )
        errors = []
        monkeypatch.setattr(
            QFileDialog,
            "getSaveFileName",
            lambda *_args, **_kwargs: next(destinations),
        )
        monkeypatch.setattr(
            QMessageBox,
            "critical",
            lambda _parent, _title, message, **_kwargs: errors.append(message),
        )

        window.act_export.trigger()
        window.act_export_table.trigger()
        window.act_export_py.trigger()
        window.act_export_nb.trigger()

        assert errors == []
        with Image.open(plot_path) as image:
            image.verify()
        exported_table = pd.read_csv(table_path)
        assert exported_table.shape == (101, 3)
        assert list(exported_table.columns) == ["x", "y", "y_error"]
        script = script_path.read_text(encoding="utf-8")
        compile(script, str(script_path), "exec")
        assert "Synthetic observations" in script
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        assert notebook["cells"]
        assert any(
            "Synthetic observations" in "".join(cell.get("source", []))
            for cell in notebook["cells"]
        )
        for index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") == "code":
                source = "".join(cell.get("source", []))
                plain_python = "\n".join(
                    line
                    for line in source.splitlines()
                    if not line.lstrip().startswith("%")
                )
                compile(
                    plain_python,
                    f"{notebook_path}:cell-{index}",
                    "exec",
                )
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()

"""Synthetic regression cases for the actual fit dialog and workflow."""

import os
import json

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox

from lang import get_language, set_language, t
from src.ui.dialogs import FitDialog
from src.ui.main_window import MainWindow
from src.ui.main_window import core
from src.ui.python_exporter import export_as_notebook, export_as_python



@pytest.fixture
def fit_window(qapp, monkeypatch):
    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda _p, _t, text: messages.append(text))
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Discard)
    monkeypatch.setattr(FitDialog, "exec", lambda self: QDialog.DialogCode.Accepted)
    window = MainWindow()
    window.data_manager.df = pd.DataFrame({"x": [1., 2., 3., 4.], "y": [2., 4., 6., 8.]})
    window.data_manager.create_series("x", "y")
    window._refresh_series_list()
    window.lst_ser.setCurrentRow(0)
    window.combo_mod.setCurrentText("Linear" if get_language() == "en" else "Doğrusal")
    yield window, messages
    window._is_modified = False
    window.close()
    window.deleteLater()
    qapp.processEvents()


@pytest.mark.parametrize("text", ["", "bad", "nan", "inf", "-inf"])
def test_dialog_rejects_invalid_initial_value(qapp, monkeypatch, text):
    messages = []
    monkeypatch.setattr(QMessageBox, "warning", lambda _p, _t, msg: messages.append(msg))
    dialog = FitDialog(["slope", "offset"])
    try:
        dialog.inputs["slope"].setText(text)
        dialog.accept()
        assert dialog.result() != QDialog.DialogCode.Accepted
        assert messages and "slope" in messages[0]
        dialog.inputs["slope"].setText("2.5")
        dialog.accept()
        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.get_values() == [2.5, 1.0]
    finally:
        dialog.deleteLater()


@pytest.mark.parametrize("language", ["tr", "en"])
def test_fit_dialog_explains_unweighted_fit(qapp, language):
    previous = get_language()
    set_language(language)
    dialog = FitDialog(["a"])
    try:
        assert any(label.text() == t("fit_unweighted_notice") for label in dialog.findChildren(QLabel))
    finally:
        dialog.deleteLater()
        set_language(previous)


def test_constant_y_has_undefined_r2_and_finite_residuals(fit_window):
    window, messages = fit_window
    window.series_list[0]["y"] = np.full(4, 5.)
    window.perform_fit()
    assert not messages
    assert len(window.fit_list) == 1
    fit = window.fit_list[0]
    assert fit["r2"] is None
    # y = 0*x + 5; absolute tolerance accommodates optimizer roundoff.
    np.testing.assert_allclose(fit["param_values"], [0., 5.], atol=1e-6)
    assert fit["res_stats"]["rmse"] < 1e-6
    assert t("report_r2_undefined") in window.report_info.toPlainText()


@pytest.mark.parametrize("axis", ["x", "y"])
def test_infinite_input_is_rejected_before_optimizer(fit_window, monkeypatch, axis):
    window, messages = fit_window
    window.series_list[0][axis][1] = np.inf
    calls = []
    monkeypatch.setattr(core, "curve_fit", lambda *a, **k: calls.append(True))
    window.perform_fit()
    assert not calls
    assert not window.fit_list
    assert messages and t("fit_nonfinite_data") in messages[0]


@pytest.mark.parametrize("invalid", ["parameters", "prediction", "curve"])
def test_invalid_optimizer_or_model_result_is_not_added(fit_window, monkeypatch, invalid):
    window, messages = fit_window
    name = window.combo_mod.currentText()
    def model(x, a, b):
        if invalid == "prediction" or (invalid == "curve" and len(x) == 500):
            return np.full_like(x, np.nan)
        return a * x + b
    window.loaded_models[name] = model
    params = [np.inf, 0.] if invalid == "parameters" else [2., 0.]
    monkeypatch.setattr(core, "curve_fit", lambda *a, **k: (np.array(params), np.eye(2)))
    window.perform_fit()
    assert not window.fit_list
    assert window.lst_fits.count() == 0
    assert messages and t("fit_invalid_result") in messages[0]


def test_optimizer_failure_is_reported_without_adding_fit(fit_window, monkeypatch):
    window, messages = fit_window
    def fail(*args, **kwargs):
        raise RuntimeError("Synthetic convergence failure")
    monkeypatch.setattr(core, "curve_fit", fail)
    window.perform_fit()
    assert not window.fit_list
    assert "Synthetic convergence failure" in messages[0]


def test_uncertain_covariance_is_explained(fit_window, monkeypatch):
    window, messages = fit_window
    monkeypatch.setattr(core, "curve_fit", lambda *a, **k: (np.array([2., 0.]), np.full((2, 2), np.inf)))
    window.perform_fit()
    assert len(window.fit_list) == 1
    assert messages == [t("fit_covariance_warning")]


@pytest.mark.parametrize("case", ["empty_range", "same_x", "invalid_domain"])
def test_invalid_fit_inputs_leave_workspace_unchanged(fit_window, monkeypatch, case):
    window, messages = fit_window
    if case == "empty_range":
        window.fit_xrange = (10., 20.)
    elif case == "same_x":
        window.series_list[0]["x"][:] = 1.
    else:
        from models.power_law import model
        window.series_list[0]["x"][:] = [-2., -1., 1., 2.]
        window.loaded_models[window.combo_mod.currentText()] = model
        # A fractional exponent has no real values for the negative X inputs.
        monkeypatch.setattr(FitDialog, "get_values", lambda self: [1., 0.5])
        window.perform_fit()
        assert not window.fit_list
        assert messages and t("fit_invalid_result") in messages[0]
        return
    window.perform_fit()
    assert not window.fit_list
    assert messages


@pytest.mark.parametrize("constant", [False, True])
def test_y_only_missing_rows_match_plot_fit_save_and_exports(fit_window, monkeypatch, tmp_path, constant):
    window, messages = fit_window
    window.data_manager.df = pd.DataFrame({"y": [2., np.nan, 4., 6., 8.]})
    if constant:
        window.data_manager.df["y"] = [5., np.nan, 5., 5., 5.]
    window.series_list.clear()
    window.data_manager.create_series(None, "y")
    window._sync_series_from_dataframe()
    window._refresh_series_list()
    window.lst_ser.setCurrentRow(0)
    window.redraw_plot()
    window.perform_fit()
    assert not messages
    # Existing auto-X policy: number the remaining Y values consecutively.
    expected_x = np.array([1., 2., 3., 4.])
    expected_y = np.full(4, 5.) if constant else 2 * expected_x
    np.testing.assert_array_equal(window.series_list[0]["x"], expected_x)
    np.testing.assert_array_equal(window.fit_list[0]["res_x"], expected_x)
    np.testing.assert_array_equal(window.canvas.axes.lines[0].get_xdata(), expected_x)
    np.testing.assert_allclose(window.fit_list[0]["param_values"], [0., 5.] if constant else [2., 0.], atol=1e-6)

    path = tmp_path / "synthetic.json"
    monkeypatch.setattr(QMessageBox, "information", lambda *a: None)
    monkeypatch.setattr(QMessageBox, "critical", lambda _p, _t, text: messages.append(text))
    window._current_project_path = str(path)
    window.save_project_action()
    from PyQt6.QtWidgets import QFileDialog
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a: (str(path), "JSON"))
    window.open_project_action()
    assert not messages
    if constant:
        assert window.fit_list[0]["r2"] is None
    else:
        assert window.fit_list[0]["r2"] == pytest.approx(1.)
    window._update_report(window.fit_list[0])

    monkeypatch.setattr(core.plt, "show", lambda: None)
    for exporter in (export_as_python, export_as_notebook):
        output = exporter(window.canvas, window.data_manager, window.fit_list, window.loaded_models)
        sources = [output] if exporter is export_as_python else [
            "".join(cell["source"]) for cell in json.loads(output)["cells"] if cell["cell_type"] == "code"
        ]
        namespace = {}
        try:
            for source in sources:
                source = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("%"))
                exec(compile(source, "<synthetic-export>", "exec"), namespace)
            exported_line = namespace["ax1"].lines[0]
            np.testing.assert_array_equal(exported_line.get_xdata(), expected_x)
            np.testing.assert_array_equal(exported_line.get_ydata(), expected_y)
        finally:
            if "fig" in namespace:
                core.plt.close(namespace["fig"])

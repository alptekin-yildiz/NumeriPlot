"""Capture real NumeriPlot UI screenshots using the synthetic example project."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from lang import set_language

set_language("en")

from src.ui.main_window import MainWindow
from src.version import APP_NAME, APP_VERSION


DEFAULT_PROJECT = Path(__file__).resolve().parent / "NumeriPlot_example_project.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "assets" / "screenshots"


def _capture(window: MainWindow, output_path: Path) -> None:
    app = QApplication.instance()
    if app is not None:
        app.processEvents()
    pixmap = window.grab()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not pixmap.save(str(output_path), "PNG"):
        raise RuntimeError(f"Could not save screenshot: {output_path}")


def capture_screenshots(project_path: Path, output_dir: Path) -> list[Path]:
    """Open ``project_path`` in the real UI and capture two synthetic views."""
    project_path = project_path.resolve()
    if not project_path.is_file():
        raise FileNotFoundError(project_path)

    app = QApplication.instance() or QApplication(["numeriplot-screenshot"])
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    errors = []
    QFileDialog.getOpenFileName = staticmethod(
        lambda *_args, **_kwargs: (str(project_path), "JSON Files (*.json)")
    )
    QMessageBox.information = staticmethod(
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Ok
    )
    QMessageBox.critical = staticmethod(
        lambda _parent, _title, message, **_kwargs: errors.append(str(message))
    )

    window = MainWindow()
    try:
        window.resize(1440, 900)
        window._main_splitter.setSizes([340, 1100])
        window.show()
        window.open_project_action()
        if errors:
            raise RuntimeError("; ".join(errors))

        window.lst_ser.setCurrentRow(0)
        window.lst_fits.setCurrentRow(0)
        window._btn_fit.setChecked(True)
        model_index = window.combo_mod.findText("Gaussian Distribution")
        if model_index >= 0:
            window.combo_mod.setCurrentIndex(model_index)

        window._tabs.setCurrentWidget(window.plot_w)
        window.redraw_plot()
        app.processEvents()
        overview = output_dir / "numeriplot-overview.png"
        _capture(window, overview)

        window._tabs.setCurrentWidget(window.report_w)
        window.lst_report_fits.setCurrentRow(0)
        window._update_report(window.fit_list[0])
        app.processEvents()
        fit_analysis = output_dir / "numeriplot-fit-analysis.png"
        _capture(window, fit_analysis)
        return [overview, fit_analysis]
    finally:
        window._is_modified = False
        window.close()
        window.deleteLater()
        app.processEvents()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    for path in capture_screenshots(args.project, args.output_dir):
        print(path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

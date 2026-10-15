"""Capture the real bilingual UI for the offline guide, using synthetic data only."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import QPoint, QTimer
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QScrollArea
from lang import set_language
from src.ui.main_window import MainWindow
from src.ui.main_window import core
from src.ui.dialogs import FitDialog, PlotSettingsDialog, DataImportDialog
from src.ui.data_ops_dialog import DataOpsDialog

OUTPUT = ROOT / 'docs' / 'guide' / 'assets'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication(['NumeriPlot-guide'])
    app.setStyle('Fusion')
    manifest = {}
    for language in ('tr', 'en'):
        set_language(language)
        core.LAYOUT_OPTIONS = core._build_layout_options()
        window = MainWindow()
        window.menuBar().setNativeMenuBar(False)
        window.resize(1440, 1000)
        window._main_splitter.setSizes([370, 1070])
        window.show()
        with patch.object(QFileDialog, 'getOpenFileName', return_value=(str(ROOT / 'examples' / 'NumeriPlot_example_project.json'), 'JSON')), patch.object(QMessageBox, 'information'):
            window.open_project_action()
        window.lst_ser.setCurrentRow(0)
        window.lst_fits.setCurrentRow(0)
        window._tabs.setCurrentWidget(window.plot_w)
        window.redraw_plot()

        def capture(widget, name):
            app.processEvents()
            pixmap = widget.grab()
            filename = f'{name}-{language}.png'
            if not pixmap.save(str(OUTPUT / filename), 'PNG'):
                raise RuntimeError(name)
            manifest.setdefault(name, {})[language] = {
                'src': f'assets/{filename}',
                'width': pixmap.width(), 'height': pixmap.height(),
            }

        capture(window, 'overview')
        # Pins are HTML links over the unchanged screenshot, using actual widget positions.
        manifest['overview'][language]['pins'] = []
        for number, (widget, target) in enumerate(((window._btn_panels, 'panels'), (window._btn_layers, 'layers'), (window._btn_texts, 'text'), (window._btn_fit, 'fit'), (window._tabs.tabBar(), 'table')), 1):
            point = widget.mapTo(window, QPoint(8, widget.height() // 2))
            manifest['overview'][language]['pins'].append({'number': number, 'target': target, 'x': 100 * point.x() / window.width(), 'y': 100 * point.y() / window.height()})
        for name, menu in [('menus-file', window._m_file), ('menus-view', window._m_view), ('menus-plot', window._m_plot), ('menus-language', window._m_lang)]:
            menu.popup(QPoint(40, 40))
            capture(menu, name)
            menu.hide()
        for name, button in [('panels', window._btn_panels), ('layers', window._btn_layers), ('text', window._btn_texts)]:
            button.setChecked(True)
            app.processEvents()
            capture(button.parentWidget(), name)
        window._tabs.setCurrentIndex(0)
        capture(window, 'table')

        def capture_popup(name):
            popup = app.activePopupWidget()
            if popup is None:
                raise RuntimeError(f'No popup: {name}')
            capture(popup, name)
            popup.close()

        header = window.table_w.horizontalHeader()
        QTimer.singleShot(30, lambda: capture_popup('table-roles'))
        window._show_column_role_menu(QPoint(header.sectionPosition(1) + 10, 10))
        window.table_w.setCurrentCell(0, 1)
        QTimer.singleShot(30, lambda: capture_popup('table-context'))
        window._show_table_context_menu(window.table_w.visualItemRect(window.table_w.item(0, 1)).center())

        def symbol_capture():
            popup = app.activePopupWidget() or app.activeModalWidget()
            capture(popup, 'symbols')
            popup.accept()
        QTimer.singleShot(30, symbol_capture)
        window._open_symbol_palette(window.inp_text_item)
        window._tabs.setCurrentWidget(window.report_w)
        window.lst_report_fits.setCurrentRow(0)
        window._update_report(window.fit_list[0])
        capture(window, 'report')
        window._tabs.setCurrentWidget(window.plot_w)

        settings = PlotSettingsDialog(window, window)
        settings._reload_for_panel(window.canvas.active_index)
        settings.resize(850, 1100)
        settings.show()
        for index, name in enumerate(('settings-axes', 'settings-appearance', 'settings-legend', 'settings-styles', 'settings-canvas')):
            settings.tabs.setCurrentIndex(index)
            app.processEvents()
            if name == 'settings-styles' and settings.list_style_series.count():
                settings.list_style_series.setCurrentRow(0)
            capture(settings, name)
            scroll = settings.tabs.currentWidget().findChild(QScrollArea)
            if scroll and scroll.verticalScrollBar().maximum() > 0:
                scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
                capture(settings, name + '-bottom')
                scroll.verticalScrollBar().setValue(0)
        settings.tabs.setCurrentIndex(0)
        settings.combo_x_notation.showPopup()
        capture(settings.combo_x_notation.view().window(), 'notation-options')
        settings.combo_x_notation.hidePopup()
        settings.tabs.setCurrentIndex(2)
        settings.combo_leg_layout.showPopup()
        capture(settings.combo_leg_layout.view().window(), 'legend-options')
        settings.combo_leg_layout.hidePopup()
        settings.tabs.setCurrentIndex(3)
        settings._chk_global.setChecked(True)
        capture(settings, 'settings-styles-global')
        settings.close()
        settings.deleteLater()
        # Type-specific controls, with new synthetic series only in this temporary workspace.
        for plot_type in ('histogram', 'bar'):
            window.data_manager.create_series('x', 'y', plot_type=plot_type)
            typed_settings = PlotSettingsDialog(window, window)
            typed_settings._reload_for_panel(0)
            typed_settings.resize(850, 1000)
            typed_settings.tabs.setCurrentIndex(3)
            typed_settings.list_style_series.setCurrentRow(len(window.series_list) - 1)
            typed_settings.show()
            capture(typed_settings, 'settings-styles-' + plot_type)
            typed_settings.close()
            typed_settings.deleteLater()

        fit = FitDialog(['A', 'μ', 'σ'], 'y = A·exp(-(x-μ)²/(2σ²))', window)
        fit.show()
        capture(fit, 'fit')
        fit.close()
        importer = DataImportDialog(str(ROOT / 'examples' / 'data' / 'gaussian_peak.csv'), window)
        importer.show()
        capture(importer, 'import')
        importer.close()
        operations = DataOpsDialog(window.data_manager, window)
        operations.show()
        capture(operations, 'data-operations')
        operations.close()
        window._is_modified = False
        window.close()
        window.deleteLater()
        app.processEvents()
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Captured {sum(len(value) for value in manifest.values())} UI images.')


if __name__ == '__main__':
    main()

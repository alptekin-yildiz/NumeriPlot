from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from lang import t


class MainWindowThemeMixin:
    def _on_plot_type_changed(self, idx: int):
        """Histogram seçilince X combo ve ±X/±Y devre dışı kalır."""
        is_hist = idx == 4
        self.combo_x.setEnabled(not is_hist)
        self.combo_x_err.setEnabled(not is_hist)
        self.combo_y_err.setEnabled(not is_hist)
        self._lbl_x.setEnabled(not is_hist)
        self._lbl_xe.setEnabled(not is_hist)
        self._lbl_ye.setEnabled(not is_hist)

    def _on_y_selection_changed(self):
        """Çoklu Y seçilince ±Y hata combo'sunu devre dışı bırak."""
        multi = len(self.lst_y_select.selectedItems()) > 1
        self.combo_y_err.setEnabled(not multi)
        self.combo_y_err.setToolTip(t("msg_bulk_warn") if multi else "")

    def _on_toggle_theme(self, checked: bool):
        self.apply_theme("dark" if checked else "light")

    def _retranslate_menu(self):
        """Menü başlıklarını ve action metinlerini günceller."""
        self._m_file.setTitle(t("menu_file"))
        self._m_view.setTitle(t("menu_view"))
        self._m_plot.setTitle(t("menu_plot"))
        self._m_lang.setTitle(t("menu_language"))

        self.act_open_data.setText(t("action_load_data"))
        if hasattr(self, "act_append_cols"):
            self.act_append_cols.setText(t("action_append_cols"))
        self.act_open_proj.setText(t("action_open_project"))
        if hasattr(self, "act_open_example"):
            self.act_open_example.setText(t("action_open_example"))
        self.act_save_proj.setText(t("action_save_project"))
        if hasattr(self, "act_save_proj_as"):
            self.act_save_proj_as.setText(t("action_save_project_as"))
        self.act_export.setText(t("action_export_image"))
        if hasattr(self, "act_export_table"):
            self.act_export_table.setText(t("action_export_table"))
        if hasattr(self, "act_data_ops"):
            self.act_data_ops.setText(t("action_data_ops"))
        if hasattr(self, "act_export_py"):
            self.act_export_py.setText(t("action_export_python"))
        if hasattr(self, "act_export_nb"):
            self.act_export_nb.setText(t("action_export_notebook"))
        if hasattr(self, "act_about"):
            self.act_about.setText(t("action_about"))
        self.act_axes.setText(t("action_axes"))
        self.act_general.setText(t("action_appearance"))
        self.act_styles.setText(t("action_styles"))
        self.act_canvas.setText(t("action_canvas"))

        is_dark = self._current_theme == "dark"
        self.act_toggle_theme.setText(
            t("action_light_theme") if is_dark else t("action_dark_theme")
        )

    def _retranslate_left_panel(self):
        """Sol paneldeki collapsible başlıkları ve buton/label metinlerini günceller."""
        if hasattr(self, "_btn_panels"):
            self._btn_panels.setText(f"  {t('section_panels')}")
        if hasattr(self, "_btn_layers"):
            self._btn_layers.setText(f"  {t('section_layers')}")
        if hasattr(self, "_btn_texts"):
            self._btn_texts.setText(f"  {t('section_texts')}")
        if hasattr(self, "_btn_fit"):
            self._btn_fit.setText(f"  {t('section_fit')}")

        if hasattr(self, "_lbl_x"):
            self._lbl_x.setText(t("label_x_col"))
        if hasattr(self, "_lbl_y"):
            self._lbl_y.setText(t("label_y_col"))
        if hasattr(self, "_lbl_xe"):
            self._lbl_xe.setText(t("label_x_err"))
        if hasattr(self, "_lbl_ye"):
            self._lbl_ye.setText(t("label_y_err"))
        if hasattr(self, "_lbl_layers"):
            self._lbl_layers.setText(t("label_layers"))

        if hasattr(self, "inp_series_label"):
            self.inp_series_label.setPlaceholderText(t("placeholder_series_label"))
        if hasattr(self, "_btn_add_l"):
            self._btn_add_l.setText(t("btn_add_left"))
        if hasattr(self, "_btn_add_r"):
            self._btn_add_r.setText(t("btn_add_right"))
        if hasattr(self, "_btn_del"):
            self._btn_del.setText(t("btn_delete"))
        if hasattr(self, "_btn_rename_panel"):
            self._btn_rename_panel.setText(t("btn_rename_panel"))
        if hasattr(self, "_btn_clear_panel"):
            self._btn_clear_panel.setText(t("btn_clear_panel"))

        if hasattr(self, "_lbl_model"):
            self._lbl_model.setText(t("label_model"))
        if hasattr(self, "_btn_fit_run"):
            self._btn_fit_run.setText(t("btn_fit"))
        if hasattr(self, "_lbl_fits"):
            self._lbl_fits.setText(t("label_fits"))
        if hasattr(self, "_btn_del_fit"):
            self._btn_del_fit.setText(t("btn_delete_fit"))

        if hasattr(self, "inp_text_item"):
            self.inp_text_item.setPlaceholderText(t("placeholder_text_item"))
        if hasattr(self, "btn_text_symbol"):
            self.btn_text_symbol.setToolTip(t("tip_symbol_palette"))
        if hasattr(self, "_lbl_text_coord_mode"):
            self._lbl_text_coord_mode.setText(t("lbl_text_coord_mode"))
        if hasattr(self, "_lbl_text_align"):
            self._lbl_text_align.setText(t("lbl_text_align"))
        if hasattr(self, "_lbl_text_font"):
            self._lbl_text_font.setText(t("lbl_text_font"))
        if hasattr(self, "_lbl_text_angle"):
            self._lbl_text_angle.setText(t("lbl_text_angle"))
        if hasattr(self, "combo_text_coord"):
            current = self.combo_text_coord.currentData()
            self.combo_text_coord.blockSignals(True)
            self.combo_text_coord.clear()
            self.combo_text_coord.addItem(t("text_coord_axes"), "axes")
            self.combo_text_coord.addItem(t("text_coord_data"), "data")
            idx = self.combo_text_coord.findData(current)
            self.combo_text_coord.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_text_coord.blockSignals(False)
        if hasattr(self, "combo_text_ha"):
            current = self.combo_text_ha.currentData()
            self.combo_text_ha.blockSignals(True)
            self.combo_text_ha.clear()
            self.combo_text_ha.addItem(t("align_left"), "left")
            self.combo_text_ha.addItem(t("align_center"), "center")
            self.combo_text_ha.addItem(t("align_right"), "right")
            idx = self.combo_text_ha.findData(current)
            self.combo_text_ha.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_text_ha.blockSignals(False)
        if hasattr(self, "combo_text_va"):
            current = self.combo_text_va.currentData()
            self.combo_text_va.blockSignals(True)
            self.combo_text_va.clear()
            self.combo_text_va.addItem(t("align_top"), "top")
            self.combo_text_va.addItem(t("align_center"), "center")
            self.combo_text_va.addItem(t("align_bottom"), "bottom")
            idx = self.combo_text_va.findData(current)
            self.combo_text_va.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_text_va.blockSignals(False)
        if hasattr(self, "combo_text_font") and hasattr(self, "_populate_text_font_combo"):
            current_data = str(self.combo_text_font.currentData() or "").strip()
            current_text = (self.combo_text_font.currentText() or "").strip()
            self._populate_text_font_combo()
            if current_data:
                idx = self.combo_text_font.findData(current_data)
                if idx >= 0:
                    self.combo_text_font.setCurrentIndex(idx)
                else:
                    self.combo_text_font.setEditText(current_data)
            elif current_text and current_text != t("text_font_default"):
                self.combo_text_font.setEditText(current_text)
        if hasattr(self, "btn_text_add"):
            self.btn_text_add.setText(t("btn_text_add"))
        if hasattr(self, "btn_text_update"):
            self.btn_text_update.setText(t("btn_text_update"))
        if hasattr(self, "btn_text_delete"):
            self.btn_text_delete.setText(t("btn_text_delete"))
        if hasattr(self, "grp_auto_panel_labels"):
            self.grp_auto_panel_labels.setTitle(t("grp_auto_panel_labels"))
        if hasattr(self, "chk_auto_panel_labels"):
            self.chk_auto_panel_labels.setText(t("chk_auto_panel_labels"))
        if hasattr(self, "chk_auto_label_bold"):
            self.chk_auto_label_bold.setText(t("chk_bold"))
        if hasattr(self, "chk_auto_label_italic"):
            self.chk_auto_label_italic.setText(t("chk_italic"))
        if hasattr(self, "combo_auto_label_ha"):
            current = self.combo_auto_label_ha.currentData()
            self.combo_auto_label_ha.blockSignals(True)
            self.combo_auto_label_ha.clear()
            self.combo_auto_label_ha.addItem(t("align_left"), "left")
            self.combo_auto_label_ha.addItem(t("align_center"), "center")
            self.combo_auto_label_ha.addItem(t("align_right"), "right")
            idx = self.combo_auto_label_ha.findData(current)
            self.combo_auto_label_ha.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_auto_label_ha.blockSignals(False)
        if hasattr(self, "combo_auto_label_va"):
            current = self.combo_auto_label_va.currentData()
            self.combo_auto_label_va.blockSignals(True)
            self.combo_auto_label_va.clear()
            self.combo_auto_label_va.addItem(t("align_top"), "top")
            self.combo_auto_label_va.addItem(t("align_center"), "center")
            self.combo_auto_label_va.addItem(t("align_bottom"), "bottom")
            idx = self.combo_auto_label_va.findData(current)
            self.combo_auto_label_va.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_auto_label_va.blockSignals(False)
        if hasattr(self, "combo_text_preset") and hasattr(self, "_populate_text_preset_combo"):
            current = self.combo_text_preset.currentData()
            self._populate_text_preset_combo()
            idx = self.combo_text_preset.findData(current)
            self.combo_text_preset.blockSignals(True)
            self.combo_text_preset.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_text_preset.blockSignals(False)
        if hasattr(self, "combo_auto_label_style") and hasattr(self, "_populate_auto_label_style_combo"):
            current = self.combo_auto_label_style.currentData()
            self._populate_auto_label_style_combo()
            idx = self.combo_auto_label_style.findData(current)
            self.combo_auto_label_style.blockSignals(True)
            self.combo_auto_label_style.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_auto_label_style.blockSignals(False)
        if hasattr(self, "combo_auto_label_preset") and hasattr(self, "_populate_auto_label_preset_combo"):
            current = self.combo_auto_label_preset.currentData()
            self._populate_auto_label_preset_combo()
            idx = self.combo_auto_label_preset.findData(current)
            self.combo_auto_label_preset.blockSignals(True)
            self.combo_auto_label_preset.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_auto_label_preset.blockSignals(False)

        if hasattr(self, "_lbl_ptype"):
            self._lbl_ptype.setText(t("label_plot_type"))
        if hasattr(self, "combo_plot_type"):
            idx = self.combo_plot_type.currentIndex()
            self.combo_plot_type.blockSignals(True)
            self.combo_plot_type.clear()
            self.combo_plot_type.addItems(
                [
                    t("plot_type_scatter"),
                    t("plot_type_line"),
                    t("plot_type_scatter_line"),
                    t("plot_type_bar"),
                    t("plot_type_histogram"),
                ]
            )
            self.combo_plot_type.setCurrentIndex(idx)
            self.combo_plot_type.blockSignals(False)
        if hasattr(self, "combo_table_plot_type"):
            idx = self.combo_table_plot_type.currentIndex()
            self.combo_table_plot_type.blockSignals(True)
            self.combo_table_plot_type.clear()
            self.combo_table_plot_type.addItems(
                [
                    t("plot_type_scatter"),
                    t("plot_type_line"),
                    t("plot_type_scatter_line"),
                    t("plot_type_bar"),
                    t("plot_type_histogram"),
                ]
            )
            self.combo_table_plot_type.setCurrentIndex(idx)
            self.combo_table_plot_type.blockSignals(False)

        if hasattr(self, "_tabs"):
            self._tabs.setTabText(0, t("tab_table"))
            self._tabs.setTabText(1, t("tab_plot"))
            self._tabs.setTabText(2, t("tab_report"))

        if hasattr(self, "btn_copy_report"):
            self.btn_copy_report.setText(t("btn_copy_report"))
        if hasattr(self, "report_info"):
            self.report_info.setPlaceholderText(t("report_placeholder"))

        # Tablo işlem butonları
        if hasattr(self, "btn_row_delete"):
            self.btn_row_delete.setText(t("btn_table_row_delete"))
        if hasattr(self, "btn_col_delete"):
            self.btn_col_delete.setText(t("btn_table_col_delete"))
        if hasattr(self, "btn_cells_shift_delete"):
            self.btn_cells_shift_delete.setText(t("btn_table_cells_shift_delete"))
        if hasattr(self, "btn_insert_row_above"):
            self.btn_insert_row_above.setText(t("btn_table_insert_above"))
        if hasattr(self, "btn_insert_row_below"):
            self.btn_insert_row_below.setText(t("btn_table_insert_below"))
        if hasattr(self, "btn_table_undo"):
            self.btn_table_undo.setText(t("btn_table_undo_last"))
        if hasattr(self, "table_w"):
            self.table_w.horizontalHeader().setToolTip(t("table_role_hint"))
        if hasattr(self, "lbl_table_plot_type"):
            self.lbl_table_plot_type.setText(t("label_plot_type"))
        if hasattr(self, "btn_add_from_roles"):
            self.btn_add_from_roles.setText(t("btn_add_from_roles"))
        if hasattr(self, "btn_reset_roles"):
            self.btn_reset_roles.setText(t("btn_reset_roles"))
        if hasattr(self, "_populate_role_template_combo"):
            self._populate_role_template_combo()
        if hasattr(self, "_rebuild_role_combo_row"):
            self._rebuild_role_combo_row()

    def apply_theme(self, theme: str):
        theme = (theme or "light").lower().strip()
        if theme not in ("light", "dark"):
            theme = "light"
        self._current_theme = theme

        app = QApplication.instance()
        if app is not None:
            app.setPalette(self._build_palette(theme))
            app.setStyleSheet(self._build_qss(theme))

        if hasattr(self, "act_toggle_theme"):
            self.act_toggle_theme.blockSignals(True)
            self.act_toggle_theme.setChecked(theme == "dark")
            self.act_toggle_theme.setText(
                t("action_dark_theme") if theme == "light" else t("action_light_theme")
            )
            self.act_toggle_theme.blockSignals(False)

    def _build_palette(self, theme: str) -> QPalette:
        p = QPalette()
        if theme == "dark":
            p.setColor(QPalette.ColorRole.Window, QColor(28, 28, 30))
            p.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
            p.setColor(QPalette.ColorRole.Base, QColor(38, 38, 41))
            p.setColor(QPalette.ColorRole.AlternateBase, QColor(32, 32, 35))
            p.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
            p.setColor(QPalette.ColorRole.Button, QColor(40, 40, 43))
            p.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
            p.setColor(QPalette.ColorRole.Highlight, QColor(90, 160, 255))
            p.setColor(QPalette.ColorRole.HighlightedText, QColor(10, 10, 10))
        else:
            p.setColor(QPalette.ColorRole.Window, QColor(245, 246, 248))
            p.setColor(QPalette.ColorRole.WindowText, QColor(18, 18, 18))
            p.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            p.setColor(QPalette.ColorRole.AlternateBase, QColor(247, 248, 250))
            p.setColor(QPalette.ColorRole.Text, QColor(18, 18, 18))
            p.setColor(QPalette.ColorRole.Button, QColor(245, 246, 248))
            p.setColor(QPalette.ColorRole.ButtonText, QColor(18, 18, 18))
            p.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            p.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        return p

    def _build_qss(self, theme: str) -> str:
        if theme == "dark":
            qss = r"""
            QGroupBox { font-weight: 600; border: 1px solid #3a3a3d; border-radius: 8px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }

            QLineEdit, QComboBox {
                background: #262629; border: 1px solid #3a3a3d; border-radius: 6px; padding: 6px;
                selection-background-color: #5aa0ff;
            }
            QComboBox QAbstractItemView { background: #262629; border: 1px solid #3a3a3d; }

            QComboBox:disabled,
            QLineEdit:disabled {
                background: #1e1e21; color: #555558; border-color: #2a2a2d;
            }

            QListWidget, QTableWidget { background: #262629; border: 1px solid #3a3a3d; border-radius: 8px; }

            QPushButton {
                background: #2a2a2d; border: 1px solid #3a3a3d; border-bottom: 2px solid #141416;
                border-radius: 8px; padding: 7px 10px;
            }
            QPushButton:hover { background: #323236; }
            QPushButton:pressed {
                background: #202023; border-top: 2px solid #141416; border-bottom: 1px solid #3a3a3d;
                padding-top: 8px; padding-bottom: 6px;
            }
            QPushButton[variant="primary"] { border-color: #5aa0ff; }
            QPushButton[variant="success"] { border-color: #46c46e; }
            QPushButton[variant="danger"]  { border-color: #ff5a5a; }
            QPushButton[variant="info"]    { border-color: #79c6ff; }
            QPushButton[variant="neutral"] { border-color: #3a3a3d; }
            QPushButton[variant="neutral"]:pressed {
                background: #16161a; border-top: 2px solid #0f1012; border-bottom: 1px solid #3a3a3d;
                padding-top: 8px; padding-bottom: 6px;
            }

            QLabel#resultBox { background: #202023; border: 1px solid #3a3a3d; border-radius: 8px; padding: 10px; font-family: 'Courier New'; }
            QWidget#plotCanvas { background: transparent; }
            """
        else:
            qss = r"""
            QGroupBox { font-weight: 600; border: 1px solid #d9dde3; border-radius: 8px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }

            QLineEdit, QComboBox {
                background: #ffffff; border: 1px solid #d9dde3; border-radius: 6px; padding: 6px;
                selection-background-color: #2a82da; selection-color: #ffffff;
            }
            QComboBox QAbstractItemView { background: #ffffff; border: 1px solid #d9dde3; }

            QComboBox:disabled,
            QLineEdit:disabled {
                background: #e8eaed; color: #aaaaaa; border-color: #d0d3d8;
            }

            QListWidget, QTableWidget { background: #ffffff; border: 1px solid #d9dde3; border-radius: 8px; }

            QPushButton {
                background: #ffffff; border: 1px solid #d9dde3; border-bottom: 2px solid #b9c0c9;
                border-radius: 8px; padding: 7px 10px;
            }
            QPushButton:hover { background: #f0f2f5; }
            QPushButton:pressed {
                background: #e6e9ef; border-top: 2px solid #b9c0c9; border-bottom: 1px solid #d9dde3;
                padding-top: 8px; padding-bottom: 6px;
            }
            QPushButton[variant="primary"] { border-color: #2a82da; }
            QPushButton[variant="success"] { border-color: #2e7d32; }
            QPushButton[variant="danger"]  { border-color: #d32f2f; }
            QPushButton[variant="info"]    { border-color: #0277bd; }
            QPushButton[variant="neutral"] { border-color: #424242; }
            QPushButton[variant="neutral"]:pressed {
                background: #dce2eb; border-top: 2px solid #a8b2bf; border-bottom: 1px solid #c4cbd6;
                padding-top: 8px; padding-bottom: 6px;
            }

            QLabel#resultBox { background: #eceff1; border: 1px solid #cfd8dc; border-radius: 8px; padding: 10px; font-family: 'Courier New'; color: #263238; }
            QWidget#plotCanvas { background: transparent; }
            """
        return qss

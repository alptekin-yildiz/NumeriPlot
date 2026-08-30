from ..emoji_spinbox import EmojiSpinBox, EmojiDoubleSpinBox

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDialogButtonBox, QFormLayout, QTabWidget, QWidget,
    QCheckBox, QComboBox, QPushButton, QListWidget,
    QColorDialog, QRadioButton, QButtonGroup,
    QGroupBox, QGridLayout, QToolButton, QSizePolicy,
    QScrollArea, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from lang import t
class PlotSettingsDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.canvas = main_window.canvas
        self.cc = main_window.canvas_config

        self.setWindowTitle(t("dialog_settings_title"))

        try:
            screen = self.screen() or (self.parent().screen() if self.parent() else None)
            if screen:
                sg = screen.availableGeometry()
                dlg_h = min(900, max(640, int(sg.height() * 0.90)))
            else:
                dlg_h = 760
        except Exception:
            dlg_h = 760
        self.resize(520, dlg_h)
        self.setMinimumSize(600, 575)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Panel başlık etiketi (combo yerine sadece bilgi)
        self._lbl_panel_title = QLabel()
        self._lbl_panel_title.setStyleSheet("font-weight: 600; font-size: 12px; padding: 2px 0;")
        layout.addWidget(self._lbl_panel_title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Global mod state — her panel için ayrı kayıt (dialog ömrü boyunca korunur)
        self._global_states = {}
        self._last_pid = self.canvas.active_index

        # İlk panel verilerini yükle
        self._load_panel_data(self.canvas.active_index)
        self._build_tabs()

        self._btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Close)
        self._btns.button(QDialogButtonBox.StandardButton.Apply).setText(t("btn_apply"))
        self._btns.button(QDialogButtonBox.StandardButton.Close).setText(t("btn_close"))
        self._btns.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        self._btns.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        layout.addWidget(self._btns)

        self._connect_toggles()

    def _reload_for_panel(self, panel_id: int):
        """Dialog yeniden açılınca aktif panele göre tüm sekmeleri günceller."""
        # Mevcut panelin global state'ini kaydet
        self._save_global_state_for(self._last_pid)
        self._last_pid = panel_id

        # Panel başlığını güncelle
        name = self.canvas.panel_names[panel_id] if panel_id < len(self.canvas.panel_names) else f"Ax{panel_id+1}"
        self._lbl_panel_title.setText("🎯 " + t("panel_settings_title").format(name=name))

        # Veriyi güncelle ve sekmeleri yeniden oluştur
        self._load_panel_data(panel_id)
        current_tab = self.tabs.currentIndex()
        self._build_tabs()
        self._connect_toggles()
        if current_tab < self.tabs.count():
            self.tabs.setCurrentIndex(current_tab)

    def _load_panel_data(self, panel_id: int):
        """Seçili panelin verilerini instance değişkenlerine yükler."""
        self.cfg = self.canvas.panel_configs[panel_id]
        self.series_list = self.main_window.data_manager.get_series_for_panel(panel_id)
        self.fit_list = [
            f for f in self.main_window.fit_list
            if f.get('panel_id', 0) == panel_id
        ]

    def _build_tabs(self):
        """Sekmeleri (yeniden) oluşturur."""
        self.tabs.clear()
        self._setup_tab_axes()
        self._setup_tab_appearance()
        self._setup_tab_legend()
        self._setup_tab_style()
        self._setup_tab_canvas()

    def _connect_toggles(self):
        self.toggle_inputs()
        self.chk_x_auto.toggled.connect(self.toggle_inputs)
        self.chk_y_auto.toggled.connect(self.toggle_inputs)
        self.chk_yr_auto.toggled.connect(self.toggle_inputs)
        self.radio_auto.toggled.connect(self.toggle_inputs)
        self.radio_manual.toggled.connect(self.toggle_inputs)


    def _save_global_state_for(self, pid: int):
        """Belirtilen panel için mevcut widget değerlerini kaydeder."""
        self._global_states[pid] = {
            'mode':        self._chk_global.isChecked() if hasattr(self, '_chk_global') else False,
            'show_marker': self.chk_global_marker.isChecked() if hasattr(self, 'chk_global_marker') else True,
            'theme':       self.combo_global_theme.currentText() if hasattr(self, 'combo_global_theme') else "— Tema Yok (renklere dokunma) —",
        }

    def _save_global_state(self):
        """Mevcut panelin global mod state'ini kaydeder (_last_pid kullanır)."""
        self._save_global_state_for(getattr(self, '_last_pid', 0))

    def _load_global_state(self, pid: int):
        """Panele özgü global mod state'ini widget'lara yükler."""
        state = self._global_states.get(pid, {
            'mode': False, 'show_marker': True,
            'theme': "— Tema Yok (renklere dokunma) —"
        })
        if hasattr(self, '_chk_global'):
            self._chk_global.blockSignals(True)
            self._chk_global.setChecked(state.get('mode', False))
            self._chk_global.blockSignals(False)
        if hasattr(self, 'chk_global_marker'):
            self.chk_global_marker.blockSignals(True)
            self.chk_global_marker.setChecked(state.get('show_marker', True))
            self.chk_global_marker.blockSignals(False)
            self._on_global_marker_toggled(state.get('show_marker', True))
        if hasattr(self, 'combo_global_theme'):
            self.combo_global_theme.blockSignals(True)
            idx = self.combo_global_theme.findText(state.get('theme', ''))
            if idx >= 0:
                self.combo_global_theme.setCurrentIndex(idx)
            self.combo_global_theme.blockSignals(False)
            self._update_global_theme_preview(state.get('theme', ''))
        self._on_global_toggled(state.get('mode', False))

    # -------------------------
    # Scroll tab helper
    # -------------------------
    def _add_scroll_tab(self, title: str) -> QVBoxLayout:
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        inner = QVBoxLayout(container)
        inner.setContentsMargins(6, 6, 6, 6)
        inner.setSpacing(5)

        scroll.setWidget(container)
        outer.addWidget(scroll)

        self.tabs.addTab(tab, title)
        return inner

    # -------------------------
    # TAB: Eksenler
    # -------------------------
    def _setup_tab_axes(self):
        lay = self._add_scroll_tab(t("tab_axes"))
        axis_value_min_w = 90
        axis_angle_min_w = 108
        axis_field_label_w = 44

        pid = self._last_pid
        ax, ax2 = self.canvas.get_axes(pid)
        curr_xlim = ax.get_xlim() if ax else (0, 10)
        curr_ylim = ax.get_ylim() if ax else (0, 10)
        curr_ylim_r = ax2.get_ylim() if ax2 else (0, 10)

        # 1) ÇERÇEVE
        grp_frame = QGroupBox(t("grp_frame"))
        gl_f = QGridLayout()
        gl_f.setHorizontalSpacing(4)
        gl_f.setVerticalSpacing(4)

        self.spin_spine_width = EmojiDoubleSpinBox()
        self.spin_spine_width.setRange(0.5, 5.0)
        self.spin_spine_width.setSingleStep(0.1)
        self.spin_spine_width.setValue(self.cfg.get('spine_width', 1.0))
        gl_f.addWidget(QLabel(t("lbl_spine_width")), 0, 0)
        gl_f.addWidget(self.spin_spine_width, 0, 1, 1, 3)

        self.chk_spine_bottom = QCheckBox(t("chk_spine_bottom"))
        self.chk_spine_bottom.setChecked(self.cfg.get('spine_bottom', True))
        self.chk_tick_bottom = QCheckBox(t("chk_tick_bottom"))
        self.chk_tick_bottom.setChecked(self.cfg.get('tick_bottom', True))

        self.chk_spine_top = QCheckBox(t("chk_spine_top"))
        self.chk_spine_top.setChecked(self.cfg.get('spine_top', True))
        self.chk_tick_top = QCheckBox(t("chk_tick_top"))
        self.chk_tick_top.setChecked(self.cfg.get('tick_top', False))

        self.chk_spine_left = QCheckBox(t("chk_spine_left"))
        self.chk_spine_left.setChecked(self.cfg.get('spine_left', True))
        self.chk_tick_left = QCheckBox(t("chk_tick_left"))
        self.chk_tick_left.setChecked(self.cfg.get('tick_left', True))

        self.chk_spine_right = QCheckBox(t("chk_spine_right"))
        self.chk_spine_right.setChecked(self.cfg.get('spine_right', True))
        self.chk_tick_right = QCheckBox(t("chk_tick_right"))
        self.chk_tick_right.setChecked(self.cfg.get('tick_right', False))

        gl_f.addWidget(self.chk_spine_bottom, 1, 0)
        gl_f.addWidget(self.chk_tick_bottom, 1, 1)
        gl_f.addWidget(self.chk_spine_top, 1, 2)
        gl_f.addWidget(self.chk_tick_top, 1, 3)

        gl_f.addWidget(self.chk_spine_left, 2, 0)
        gl_f.addWidget(self.chk_tick_left, 2, 1)
        gl_f.addWidget(self.chk_spine_right, 2, 2)
        gl_f.addWidget(self.chk_tick_right, 2, 3)

        self.spin_maj_len = EmojiDoubleSpinBox()
        self.spin_maj_len.setRange(0, 20)
        self.spin_maj_len.setSingleStep(0.5)
        self.spin_maj_len.setValue(self.cfg.get('tick_major_len', 3.0))

        self.spin_maj_wid = EmojiDoubleSpinBox()
        self.spin_maj_wid.setRange(0, 5)
        self.spin_maj_wid.setSingleStep(0.1)
        self.spin_maj_wid.setValue(self.cfg.get('tick_major_width', 1.0))

        self.spin_min_len = EmojiDoubleSpinBox()
        self.spin_min_len.setRange(0, 20)
        self.spin_min_len.setSingleStep(0.5)
        self.spin_min_len.setValue(self.cfg.get('tick_minor_len', 2.0))

        self.spin_min_wid = EmojiDoubleSpinBox()
        self.spin_min_wid.setRange(0, 5)
        self.spin_min_wid.setSingleStep(0.1)
        self.spin_min_wid.setValue(self.cfg.get('tick_minor_width', 0.8))

        gl_f.addWidget(QLabel(t("lbl_maj_tick")), 3, 0)
        h_maj = QHBoxLayout()
        h_maj.setSpacing(6)
        h_maj.addWidget(self.spin_maj_len)
        h_maj.addWidget(self.spin_maj_wid)
        gl_f.addLayout(h_maj, 3, 1, 1, 3)

        gl_f.addWidget(QLabel(t("lbl_min_tick")), 4, 0)
        h_min = QHBoxLayout()
        h_min.setSpacing(6)
        h_min.addWidget(self.spin_min_len)
        h_min.addWidget(self.spin_min_wid)
        gl_f.addLayout(h_min, 4, 1, 1, 3)

        grp_frame.setLayout(gl_f)
        lay.addWidget(grp_frame)

        # 2) GRID
        grp_grid = QGroupBox(t("grp_grid"))
        gl_grid = QGridLayout()
        gl_grid.setHorizontalSpacing(8)
        gl_grid.setVerticalSpacing(6)

        self.chk_grid = QCheckBox(t("chk_grid_show"))
        self.chk_grid.setChecked(self.cfg.get('grid', False))

        self.combo_grid_style = QComboBox()
        self.combo_grid_style.addItems([t('grid_style_dot'), t('grid_style_dash'), t('grid_style_solid'), t('grid_style_dashdot')])
        curr_g = self.cfg.get('grid_style', ':')
        idx = self.combo_grid_style.findText(curr_g, Qt.MatchFlag.MatchStartsWith)
        if idx >= 0:
            self.combo_grid_style.setCurrentIndex(idx)

        self.spin_grid_alpha = EmojiDoubleSpinBox()
        self.spin_grid_alpha.setRange(0.1, 1.0)
        self.spin_grid_alpha.setSingleStep(0.1)
        self.spin_grid_alpha.setValue(self.cfg.get('grid_alpha', 0.6))

        gl_grid.addWidget(self.chk_grid, 0, 0)
        gl_grid.addWidget(self.combo_grid_style, 0, 1)
        gl_grid.addWidget(QLabel(t("lbl_opacity")), 1, 0)
        gl_grid.addWidget(self.spin_grid_alpha, 1, 1)
        grp_grid.setLayout(gl_grid)
        lay.addWidget(grp_grid)

        # 3) X Ekseni
        grp_x = QGroupBox(t("grp_x"))
        gl_x = QGridLayout()
        gl_x.setHorizontalSpacing(6)
        gl_x.setVerticalSpacing(4)
        for c in range(10):
            gl_x.setColumnStretch(c, 1)

        is_x_auto = self.cfg.get('x_auto', True)
        self.chk_x_auto = QCheckBox(t("chk_auto"))
        self.chk_x_auto.setChecked(is_x_auto)
        self.chk_logx = QCheckBox(t("chk_log"))
        self.chk_logx.setChecked(self.cfg.get('logx', False))
        self.combo_x_notation = QComboBox()
        self.combo_x_notation.addItem(t("tick_mode_auto"), "auto")
        self.combo_x_notation.addItem(t("tick_mode_e"), "e")
        self.combo_x_notation.addItem(t("tick_mode_e_offset"), "e_offset")
        self.combo_x_notation.addItem(t("tick_mode_pow10"), "pow10")
        self.combo_x_notation.addItem(t("tick_mode_pow10_offset"), "pow10_offset")
        old_x_mode = self.cfg.get("x_tick_notation", "auto")
        old_x_style = self.cfg.get("x_tick_sci_style", "pow10")
        x_mode = old_x_mode
        if old_x_mode == "scientific":
            x_mode = "pow10" if old_x_style == "pow10" else "e"
        elif old_x_mode == "offset":
            x_mode = "pow10_offset" if old_x_style == "pow10" else "e_offset"
        if x_mode not in ("auto", "e", "e_offset", "pow10", "pow10_offset"):
            x_mode = "auto"
        x_idx = self.combo_x_notation.findData(x_mode)
        self.combo_x_notation.setCurrentIndex(x_idx if x_idx >= 0 else 0)
        self.chk_show_xticklabels = QCheckBox(t("chk_show_ticklabels"))
        self.chk_show_xticklabels.setChecked(self.cfg.get('show_xticklabels', True))

        val_xmin = curr_xlim[0] if is_x_auto else self.cfg.get('x_min', 0)
        val_xmax = curr_xlim[1] if is_x_auto else self.cfg.get('x_max', 10)

        self.spin_x_min = EmojiDoubleSpinBox(); self.spin_x_min.setRange(-9e9, 9e9); self.spin_x_min.setValue(val_xmin)
        self.spin_x_max = EmojiDoubleSpinBox(); self.spin_x_max.setRange(-9e9, 9e9); self.spin_x_max.setValue(val_xmax)
        self.spin_x_step = EmojiDoubleSpinBox(); self.spin_x_step.setRange(0, 9e9); self.spin_x_step.setValue(self.cfg.get('x_step', 0))
        self.spin_x_minor = EmojiSpinBox(); self.spin_x_minor.setRange(0, 50); self.spin_x_minor.setValue(self.cfg.get('x_minor', 0))
        self.spin_x_min.setMinimumWidth(axis_value_min_w)
        self.spin_x_max.setMinimumWidth(axis_value_min_w)
        self.spin_x_step.setMinimumWidth(axis_value_min_w)
        self.spin_x_minor.setMinimumWidth(axis_value_min_w)
        self.spin_x_rotation = EmojiSpinBox()
        self.spin_x_rotation.setRange(-90, 90)
        self.spin_x_rotation.setValue(self.cfg.get('x_tick_rotation', 0))
        self.spin_x_rotation.setMinimumWidth(axis_angle_min_w)

        gl_x.addWidget(self.chk_x_auto, 0, 0, 1, 2)
        gl_x.addWidget(self.chk_logx, 0, 2, 1, 2)
        gl_x.addWidget(self.chk_show_xticklabels, 0, 4, 1, 2)
        gl_x.addWidget(self.combo_x_notation, 0, 6, 1, 2)
        h_rot_x = QHBoxLayout()
        h_rot_x.setContentsMargins(0, 0, 0, 0)
        h_rot_x.setSpacing(4)
        h_rot_x.addWidget(QLabel(t("lbl_tick_rotation")))
        h_rot_x.addWidget(self.spin_x_rotation)
        gl_x.addLayout(h_rot_x, 0, 8, 1, 2)

        h_x_min = QHBoxLayout()
        h_x_min.setContentsMargins(0, 0, 0, 0)
        h_x_min.setSpacing(4)
        lbl_x_min = QLabel(t("lbl_min"))
        lbl_x_min.setFixedWidth(axis_field_label_w)
        lbl_x_min.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_x_min.addWidget(lbl_x_min)
        h_x_min.addWidget(self.spin_x_min, 1)
        gl_x.addLayout(h_x_min, 1, 0, 1, 5)

        h_x_max = QHBoxLayout()
        h_x_max.setContentsMargins(0, 0, 0, 0)
        h_x_max.setSpacing(4)
        lbl_x_max = QLabel(t("lbl_max"))
        lbl_x_max.setFixedWidth(axis_field_label_w)
        lbl_x_max.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_x_max.addWidget(lbl_x_max)
        h_x_max.addWidget(self.spin_x_max, 1)
        gl_x.addLayout(h_x_max, 1, 5, 1, 5)

        h_x_step = QHBoxLayout()
        h_x_step.setContentsMargins(0, 0, 0, 0)
        h_x_step.setSpacing(4)
        lbl_x_step = QLabel(t("lbl_step"))
        lbl_x_step.setFixedWidth(axis_field_label_w)
        lbl_x_step.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_x_step.addWidget(lbl_x_step)
        h_x_step.addWidget(self.spin_x_step, 1)
        gl_x.addLayout(h_x_step, 2, 0, 1, 5)

        h_x_minor = QHBoxLayout()
        h_x_minor.setContentsMargins(0, 0, 0, 0)
        h_x_minor.setSpacing(4)
        lbl_x_minor = QLabel(t("lbl_minor"))
        lbl_x_minor.setFixedWidth(axis_field_label_w)
        lbl_x_minor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_x_minor.addWidget(lbl_x_minor)
        h_x_minor.addWidget(self.spin_x_minor, 1)
        gl_x.addLayout(h_x_minor, 2, 5, 1, 5)

        grp_x.setLayout(gl_x)
        lay.addWidget(grp_x)

        # 4) Y Sol
        grp_y = QGroupBox(t("grp_y"))
        gl_y = QGridLayout()
        gl_y.setHorizontalSpacing(6)
        gl_y.setVerticalSpacing(4)
        for c in range(10):
            gl_y.setColumnStretch(c, 1)

        is_y_auto = self.cfg.get('y_auto', True)
        self.chk_y_auto = QCheckBox(t("chk_auto"))
        self.chk_y_auto.setChecked(is_y_auto)
        self.chk_logy = QCheckBox(t("chk_log"))
        self.chk_logy.setChecked(self.cfg.get('logy', False))
        self.combo_y_notation = QComboBox()
        self.combo_y_notation.addItem(t("tick_mode_auto"), "auto")
        self.combo_y_notation.addItem(t("tick_mode_e"), "e")
        self.combo_y_notation.addItem(t("tick_mode_e_offset"), "e_offset")
        self.combo_y_notation.addItem(t("tick_mode_pow10"), "pow10")
        self.combo_y_notation.addItem(t("tick_mode_pow10_offset"), "pow10_offset")
        old_y_mode = self.cfg.get("y_tick_notation", "auto")
        old_y_style = self.cfg.get("y_tick_sci_style", "pow10")
        y_mode = old_y_mode
        if old_y_mode == "scientific":
            y_mode = "pow10" if old_y_style == "pow10" else "e"
        elif old_y_mode == "offset":
            y_mode = "pow10_offset" if old_y_style == "pow10" else "e_offset"
        if y_mode not in ("auto", "e", "e_offset", "pow10", "pow10_offset"):
            y_mode = "auto"
        y_idx = self.combo_y_notation.findData(y_mode)
        self.combo_y_notation.setCurrentIndex(y_idx if y_idx >= 0 else 0)

        val_ymin = curr_ylim[0] if is_y_auto else self.cfg.get('y_min', 0)
        val_ymax = curr_ylim[1] if is_y_auto else self.cfg.get('y_max', 10)

        self.spin_y_min = EmojiDoubleSpinBox(); self.spin_y_min.setRange(-9e9, 9e9); self.spin_y_min.setValue(val_ymin)
        self.spin_y_max = EmojiDoubleSpinBox(); self.spin_y_max.setRange(-9e9, 9e9); self.spin_y_max.setValue(val_ymax)
        self.spin_y_step = EmojiDoubleSpinBox(); self.spin_y_step.setRange(0, 9e9); self.spin_y_step.setValue(self.cfg.get('y_step', 0))
        self.spin_y_minor = EmojiSpinBox(); self.spin_y_minor.setRange(0, 50); self.spin_y_minor.setValue(self.cfg.get('y_minor', 0))
        self.spin_y_min.setMinimumWidth(axis_value_min_w)
        self.spin_y_max.setMinimumWidth(axis_value_min_w)
        self.spin_y_step.setMinimumWidth(axis_value_min_w)
        self.spin_y_minor.setMinimumWidth(axis_value_min_w)
        self.spin_y_rotation = EmojiSpinBox()
        self.spin_y_rotation.setRange(-90, 90)
        self.spin_y_rotation.setValue(self.cfg.get('y_tick_rotation', 0))

        self.chk_show_yticklabels = QCheckBox(t("chk_show_ticklabels"))
        self.chk_show_yticklabels.setChecked(self.cfg.get('show_yticklabels', True))
        self.spin_y_rotation.setMinimumWidth(axis_angle_min_w)

        gl_y.addWidget(self.chk_y_auto, 0, 0, 1, 2)
        gl_y.addWidget(self.chk_logy, 0, 2, 1, 2)
        gl_y.addWidget(self.chk_show_yticklabels, 0, 4, 1, 2)
        gl_y.addWidget(self.combo_y_notation, 0, 6, 1, 2)
        h_rot_y = QHBoxLayout()
        h_rot_y.setContentsMargins(0, 0, 0, 0)
        h_rot_y.setSpacing(4)
        h_rot_y.addWidget(QLabel(t("lbl_tick_rotation")))
        h_rot_y.addWidget(self.spin_y_rotation)
        gl_y.addLayout(h_rot_y, 0, 8, 1, 2)

        h_y_min = QHBoxLayout()
        h_y_min.setContentsMargins(0, 0, 0, 0)
        h_y_min.setSpacing(4)
        lbl_y_min = QLabel(t("lbl_min"))
        lbl_y_min.setFixedWidth(axis_field_label_w)
        lbl_y_min.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_y_min.addWidget(lbl_y_min)
        h_y_min.addWidget(self.spin_y_min, 1)
        gl_y.addLayout(h_y_min, 1, 0, 1, 5)

        h_y_max = QHBoxLayout()
        h_y_max.setContentsMargins(0, 0, 0, 0)
        h_y_max.setSpacing(4)
        lbl_y_max = QLabel(t("lbl_max"))
        lbl_y_max.setFixedWidth(axis_field_label_w)
        lbl_y_max.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_y_max.addWidget(lbl_y_max)
        h_y_max.addWidget(self.spin_y_max, 1)
        gl_y.addLayout(h_y_max, 1, 5, 1, 5)

        h_y_step = QHBoxLayout()
        h_y_step.setContentsMargins(0, 0, 0, 0)
        h_y_step.setSpacing(4)
        lbl_y_step = QLabel(t("lbl_step"))
        lbl_y_step.setFixedWidth(axis_field_label_w)
        lbl_y_step.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_y_step.addWidget(lbl_y_step)
        h_y_step.addWidget(self.spin_y_step, 1)
        gl_y.addLayout(h_y_step, 2, 0, 1, 5)

        h_y_minor = QHBoxLayout()
        h_y_minor.setContentsMargins(0, 0, 0, 0)
        h_y_minor.setSpacing(4)
        lbl_y_minor = QLabel(t("lbl_minor"))
        lbl_y_minor.setFixedWidth(axis_field_label_w)
        lbl_y_minor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_y_minor.addWidget(lbl_y_minor)
        h_y_minor.addWidget(self.spin_y_minor, 1)
        gl_y.addLayout(h_y_minor, 2, 5, 1, 5)

        grp_y.setLayout(gl_y)
        lay.addWidget(grp_y)

        # 5) Y Sağ
        grp_yr = QGroupBox(t("grp_yr"))
        gl_yr = QGridLayout()
        gl_yr.setHorizontalSpacing(6)
        gl_yr.setVerticalSpacing(4)
        for c in range(10):
            gl_yr.setColumnStretch(c, 1)

        is_yr_auto = self.cfg.get('y_right_auto', True)
        self.chk_yr_auto = QCheckBox(t("chk_auto"))
        self.chk_yr_auto.setChecked(is_yr_auto)
        self.chk_logyr = QCheckBox(t("chk_log"))
        self.chk_logyr.setChecked(self.cfg.get('logy_right', False))
        self.combo_yr_notation = QComboBox()
        self.combo_yr_notation.addItem(t("tick_mode_auto"), "auto")
        self.combo_yr_notation.addItem(t("tick_mode_e"), "e")
        self.combo_yr_notation.addItem(t("tick_mode_e_offset"), "e_offset")
        self.combo_yr_notation.addItem(t("tick_mode_pow10"), "pow10")
        self.combo_yr_notation.addItem(t("tick_mode_pow10_offset"), "pow10_offset")
        old_yr_mode = self.cfg.get("y_right_tick_notation", "auto")
        old_yr_style = self.cfg.get("y_right_tick_sci_style", "pow10")
        yr_mode = old_yr_mode
        if old_yr_mode == "scientific":
            yr_mode = "pow10" if old_yr_style == "pow10" else "e"
        elif old_yr_mode == "offset":
            yr_mode = "pow10_offset" if old_yr_style == "pow10" else "e_offset"
        if yr_mode not in ("auto", "e", "e_offset", "pow10", "pow10_offset"):
            yr_mode = "auto"
        yr_idx = self.combo_yr_notation.findData(yr_mode)
        self.combo_yr_notation.setCurrentIndex(yr_idx if yr_idx >= 0 else 0)

        val_yrmin = curr_ylim_r[0] if is_yr_auto else self.cfg.get('y_right_min', 0)
        val_yrmax = curr_ylim_r[1] if is_yr_auto else self.cfg.get('y_right_max', 10)

        self.spin_yr_min = EmojiDoubleSpinBox(); self.spin_yr_min.setRange(-9e9, 9e9); self.spin_yr_min.setValue(val_yrmin)
        self.spin_yr_max = EmojiDoubleSpinBox(); self.spin_yr_max.setRange(-9e9, 9e9); self.spin_yr_max.setValue(val_yrmax)
        self.spin_yr_step = EmojiDoubleSpinBox(); self.spin_yr_step.setRange(0, 9e9); self.spin_yr_step.setValue(self.cfg.get('y_right_step', 0))
        self.spin_yr_minor = EmojiSpinBox(); self.spin_yr_minor.setRange(0, 50); self.spin_yr_minor.setValue(self.cfg.get('y_right_minor', 0))
        self.spin_yr_min.setMinimumWidth(axis_value_min_w)
        self.spin_yr_max.setMinimumWidth(axis_value_min_w)
        self.spin_yr_step.setMinimumWidth(axis_value_min_w)
        self.spin_yr_minor.setMinimumWidth(axis_value_min_w)
        self.spin_yr_rotation = EmojiSpinBox()
        self.spin_yr_rotation.setRange(-90, 90)
        self.spin_yr_rotation.setValue(self.cfg.get('y_right_tick_rotation', 0))

        self.chk_show_yrticklabels = QCheckBox(t("chk_show_ticklabels"))
        self.chk_show_yrticklabels.setChecked(self.cfg.get('show_yrticklabels', True))
        self.spin_yr_rotation.setMinimumWidth(axis_angle_min_w)

        gl_yr.addWidget(self.chk_yr_auto, 0, 0, 1, 2)
        gl_yr.addWidget(self.chk_logyr, 0, 2, 1, 2)
        gl_yr.addWidget(self.chk_show_yrticklabels, 0, 4, 1, 2)
        gl_yr.addWidget(self.combo_yr_notation, 0, 6, 1, 2)
        h_rot_yr = QHBoxLayout()
        h_rot_yr.setContentsMargins(0, 0, 0, 0)
        h_rot_yr.setSpacing(4)
        h_rot_yr.addWidget(QLabel(t("lbl_tick_rotation")))
        h_rot_yr.addWidget(self.spin_yr_rotation)
        gl_yr.addLayout(h_rot_yr, 0, 8, 1, 2)

        h_yr_min = QHBoxLayout()
        h_yr_min.setContentsMargins(0, 0, 0, 0)
        h_yr_min.setSpacing(4)
        lbl_yr_min = QLabel(t("lbl_min"))
        lbl_yr_min.setFixedWidth(axis_field_label_w)
        lbl_yr_min.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_yr_min.addWidget(lbl_yr_min)
        h_yr_min.addWidget(self.spin_yr_min, 1)
        gl_yr.addLayout(h_yr_min, 1, 0, 1, 5)

        h_yr_max = QHBoxLayout()
        h_yr_max.setContentsMargins(0, 0, 0, 0)
        h_yr_max.setSpacing(4)
        lbl_yr_max = QLabel(t("lbl_max"))
        lbl_yr_max.setFixedWidth(axis_field_label_w)
        lbl_yr_max.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_yr_max.addWidget(lbl_yr_max)
        h_yr_max.addWidget(self.spin_yr_max, 1)
        gl_yr.addLayout(h_yr_max, 1, 5, 1, 5)

        h_yr_step = QHBoxLayout()
        h_yr_step.setContentsMargins(0, 0, 0, 0)
        h_yr_step.setSpacing(4)
        lbl_yr_step = QLabel(t("lbl_step"))
        lbl_yr_step.setFixedWidth(axis_field_label_w)
        lbl_yr_step.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_yr_step.addWidget(lbl_yr_step)
        h_yr_step.addWidget(self.spin_yr_step, 1)
        gl_yr.addLayout(h_yr_step, 2, 0, 1, 5)

        h_yr_minor = QHBoxLayout()
        h_yr_minor.setContentsMargins(0, 0, 0, 0)
        h_yr_minor.setSpacing(4)
        lbl_yr_minor = QLabel(t("lbl_minor"))
        lbl_yr_minor.setFixedWidth(axis_field_label_w)
        lbl_yr_minor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h_yr_minor.addWidget(lbl_yr_minor)
        h_yr_minor.addWidget(self.spin_yr_minor, 1)
        gl_yr.addLayout(h_yr_minor, 2, 5, 1, 5)
        
        grp_yr.setLayout(gl_yr)
        lay.addWidget(grp_yr)

        lay.addStretch(1)

    # -------------------------
    # TAB: Genel Görünüm
    # -------------------------
    def _make_symbol_btn(self, target_input: "QLineEdit") -> "QPushButton":
        """Sembol paleti açan küçük buton — verilen QLineEdit'e ekler."""
        btn = QPushButton("Ω")
        btn.setFixedWidth(28)
        btn.setFixedHeight(24)
        btn.setToolTip("Sembol / Yunan harfi ekle")
        btn.setStyleSheet("font-size: 11px; padding: 0px;")

        SYMBOLS = [
            # Math şablonları (Math modu açıkken)
            ("xⁿ", "^{}", "Üst indis şablonu", 1),
            ("xₙ", "_{}", "Alt indis şablonu", 1),
            # Unicode üst/alt indis kısayolları (Math modu kapalıyken de güvenli)
            ("⁰", "⁰", "Üst indis 0", 0), ("¹", "¹", "Üst indis 1", 0),
            ("²", "²", "Üst indis 2", 0), ("³", "³", "Üst indis 3", 0),
            ("⁴", "⁴", "Üst indis 4", 0), ("⁵", "⁵", "Üst indis 5", 0),
            ("⁶", "⁶", "Üst indis 6", 0), ("⁷", "⁷", "Üst indis 7", 0),
            ("⁸", "⁸", "Üst indis 8", 0), ("⁹", "⁹", "Üst indis 9", 0),
            ("₀", "₀", "Alt indis 0", 0), ("₁", "₁", "Alt indis 1", 0),
            ("₂", "₂", "Alt indis 2", 0), ("₃", "₃", "Alt indis 3", 0),
            ("₄", "₄", "Alt indis 4", 0), ("₅", "₅", "Alt indis 5", 0),
            ("₆", "₆", "Alt indis 6", 0), ("₇", "₇", "Alt indis 7", 0),
            ("₈", "₈", "Alt indis 8", 0), ("₉", "₉", "Alt indis 9", 0),
            # Yunan küçük
            ("α","α","α",0), ("β","β","β",0), ("γ","γ","γ",0), ("δ","δ","δ",0), ("ε","ε","ε",0),
            ("ζ","ζ","ζ",0), ("η","η","η",0), ("θ","θ","θ",0), ("λ","λ","λ",0), ("µ","µ","µ",0),
            ("ν","ν","ν",0), ("π","π","π",0), ("ρ","ρ","ρ",0), ("σ","σ","σ",0), ("τ","τ","τ",0),
            ("φ","φ","φ",0), ("χ","χ","χ",0), ("ψ","ψ","ψ",0), ("ω","ω","ω",0),
            # Yunan büyük
            ("Γ","Γ","Γ",0), ("Δ","Δ","Δ",0), ("Θ","Θ","Θ",0), ("Λ","Λ","Λ",0), ("Π","Π","Π",0),
            ("Σ","Σ","Σ",0), ("Φ","Φ","Φ",0), ("Ψ","Ψ","Ψ",0), ("Ω","Ω","Ω",0),
            # Birim / bilim
            ("°","°","°",0), ("±","±","±",0), ("×","×","×",0), ("÷","÷","÷",0),
            ("⁻¹","⁻¹","⁻¹",0), ("µ","µ","µ",0), ("Å","Å","Å",0), ("∞","∞","∞",0),
            ("√","√","√",0), ("∂","∂","∂",0), ("∇","∇","∇",0), ("∑","∑","∑",0), ("∏","∏","∏",0),
        ]

        def open_palette():
            dlg = QDialog(btn.window())
            dlg.setWindowTitle(t("dlg_symbol_title"))
            dlg.setWindowFlags(Qt.WindowType.Popup)
            lay = QGridLayout(dlg)
            lay.setSpacing(2)
            lay.setContentsMargins(6, 6, 6, 6)
            cols = 8
            for i, (label, insert_text, tip, back) in enumerate(SYMBOLS):
                b = QPushButton(label)
                b.setFixedSize(32, 32)
                b.setToolTip(tip)
                b.setStyleSheet("font-size: 14px;")
                def insert(_, s=insert_text, move_back=back):
                    pos = target_input.cursorPosition()
                    txt = target_input.text()
                    target_input.setText(txt[:pos] + s + txt[pos:])
                    target_input.setCursorPosition(max(0, pos + len(s) - move_back))
                    dlg.accept()
                b.clicked.connect(insert)
                lay.addWidget(b, i // cols, i % cols)
            # Dialog boyutunu hesapla, input'un üstüne konumlandır
            dlg.adjustSize()
            dlg_h = dlg.sizeHint().height()
            gp = btn.mapToGlobal(btn.rect().topLeft())
            dlg.move(gp.x(), gp.y() - dlg_h - 4)
            dlg.exec()

        btn.clicked.connect(open_palette)
        return btn

    def _setup_tab_appearance(self):
        lay = self._add_scroll_tab(t("tab_appearance"))

        # Etiketler
        grp_lbl = QGroupBox(t("grp_labels"))
        gl_lbl = QGridLayout()
        gl_lbl.setHorizontalSpacing(4)
        gl_lbl.setVerticalSpacing(4)
        gl_lbl.setColumnStretch(1, 1)   # metin kutusu esner
        gl_lbl.setColumnMinimumWidth(4, 100)  # spinbox sütunu sabit 80px

        self.inp_title = QLineEdit(self.cfg.get('title', ''))
        self.chk_title_bold = QCheckBox("K")
        self.chk_title_bold.setChecked(self.cfg.get('title_bold', False))
        self.chk_title_italic = QCheckBox("İ")
        self.chk_title_italic.setChecked(self.cfg.get('title_italic', False))
        self.spin_title_pad = EmojiDoubleSpinBox()
        self.spin_title_pad.setRange(-20, 40)
        self.spin_title_pad.setSingleStep(0.5)
        self.spin_title_pad.setFixedWidth(100)
        self.spin_title_pad.setValue(self.cfg.get('title_pad', 6.0))
        self.spin_title_pad.setToolTip(t("tip_title_pad"))
        _hw_title = QWidget()
        _hl_title = QHBoxLayout(_hw_title)
        _hl_title.setContentsMargins(0,0,0,0)
        _hl_title.setSpacing(3)
        _hl_title.addWidget(self.inp_title)
        _hl_title.addWidget(self._make_symbol_btn(self.inp_title))
        gl_lbl.addWidget(QLabel(t("lbl_title")), 0, 0)
        gl_lbl.addWidget(_hw_title, 0, 1)
        gl_lbl.addWidget(self.chk_title_bold, 0, 2)
        gl_lbl.addWidget(self.chk_title_italic, 0, 3)
        gl_lbl.addWidget(self.spin_title_pad, 0, 4)

        self.inp_xlabel = QLineEdit(self.cfg.get('xlabel', ''))
        self.chk_xlabel_bold = QCheckBox("K")
        self.chk_xlabel_bold.setChecked(self.cfg.get('xlabel_bold', False))
        self.chk_xlabel_italic = QCheckBox("İ")
        self.chk_xlabel_italic.setChecked(self.cfg.get('xlabel_italic', False))
        self.spin_xlabel_pad = EmojiDoubleSpinBox()
        self.spin_xlabel_pad.setRange(-20, 40)
        self.spin_xlabel_pad.setSingleStep(0.5)
        self.spin_xlabel_pad.setSuffix("")
        self.spin_xlabel_pad.setFixedWidth(100)
        self.spin_xlabel_pad.setValue(self.cfg.get('xlabel_pad', 2.0))
        self.spin_xlabel_pad.setToolTip(t("tip_axis_pad"))
        _hw_xlabel = QWidget()
        _hl_xlabel = QHBoxLayout(_hw_xlabel)
        _hl_xlabel.setContentsMargins(0,0,0,0)
        _hl_xlabel.setSpacing(3)
        _hl_xlabel.addWidget(self.inp_xlabel)
        _hl_xlabel.addWidget(self._make_symbol_btn(self.inp_xlabel))
        gl_lbl.addWidget(QLabel(t("lbl_xlabel")), 1, 0)
        gl_lbl.addWidget(_hw_xlabel, 1, 1)
        gl_lbl.addWidget(self.chk_xlabel_bold, 1, 2)
        gl_lbl.addWidget(self.chk_xlabel_italic, 1, 3)
        gl_lbl.addWidget(self.spin_xlabel_pad, 1, 4)

        self.inp_ylabel = QLineEdit(self.cfg.get('ylabel', ''))
        self.chk_ylabel_bold = QCheckBox("K")
        self.chk_ylabel_bold.setChecked(self.cfg.get('ylabel_bold', False))
        self.chk_ylabel_italic = QCheckBox("İ")
        self.chk_ylabel_italic.setChecked(self.cfg.get('ylabel_italic', False))
        self.spin_ylabel_pad = EmojiDoubleSpinBox()
        self.spin_ylabel_pad.setRange(-20, 40)
        self.spin_ylabel_pad.setSingleStep(0.5)
        self.spin_ylabel_pad.setSuffix("")
        self.spin_ylabel_pad.setFixedWidth(100)
        self.spin_ylabel_pad.setValue(self.cfg.get('ylabel_pad', 2.0))
        self.spin_ylabel_pad.setToolTip(t("tip_axis_pad"))
        _hw_ylabel = QWidget()
        _hl_ylabel = QHBoxLayout(_hw_ylabel)
        _hl_ylabel.setContentsMargins(0,0,0,0)
        _hl_ylabel.setSpacing(3)
        _hl_ylabel.addWidget(self.inp_ylabel)
        _hl_ylabel.addWidget(self._make_symbol_btn(self.inp_ylabel))
        gl_lbl.addWidget(QLabel(t("lbl_ylabel")), 2, 0)
        gl_lbl.addWidget(_hw_ylabel, 2, 1)
        gl_lbl.addWidget(self.chk_ylabel_bold, 2, 2)
        gl_lbl.addWidget(self.chk_ylabel_italic, 2, 3)
        gl_lbl.addWidget(self.spin_ylabel_pad, 2, 4)

        self.inp_ylabel_right = QLineEdit(self.cfg.get('ylabel_right', ''))
        self.chk_ylabel_right_bold = QCheckBox("K")
        self.chk_ylabel_right_bold.setChecked(self.cfg.get('ylabel_right_bold', False))
        self.chk_ylabel_right_italic = QCheckBox("İ")
        self.chk_ylabel_right_italic.setChecked(self.cfg.get('ylabel_right_italic', False))
        self.spin_ylabel_right_pad = EmojiDoubleSpinBox()
        self.spin_ylabel_right_pad.setRange(-20, 40)
        self.spin_ylabel_right_pad.setSingleStep(0.5)
        self.spin_ylabel_right_pad.setSuffix("")
        self.spin_ylabel_right_pad.setFixedWidth(100)
        self.spin_ylabel_right_pad.setValue(self.cfg.get('ylabel_right_pad', 2.0))
        self.spin_ylabel_right_pad.setToolTip(t("tip_axis_pad"))
        _hw_ylabel_right = QWidget()
        _hl_ylabel_right = QHBoxLayout(_hw_ylabel_right)
        _hl_ylabel_right.setContentsMargins(0,0,0,0)
        _hl_ylabel_right.setSpacing(3)
        _hl_ylabel_right.addWidget(self.inp_ylabel_right)
        _hl_ylabel_right.addWidget(self._make_symbol_btn(self.inp_ylabel_right))
        gl_lbl.addWidget(QLabel(t("lbl_ylabel_right")), 3, 0)
        gl_lbl.addWidget(_hw_ylabel_right, 3, 1)
        gl_lbl.addWidget(self.chk_ylabel_right_bold, 3, 2)
        gl_lbl.addWidget(self.chk_ylabel_right_italic, 3, 3)
        gl_lbl.addWidget(self.spin_ylabel_right_pad, 3, 4)

        self.chk_math_mode = QCheckBox(t("chk_math_mode"))
        self.chk_math_mode.setChecked(self.cfg.get("math_mode", False))
        self.chk_math_mode.setToolTip(t("tip_math_mode"))
        gl_lbl.addWidget(self.chk_math_mode, 4, 1, 1, 4)

        grp_lbl.setLayout(gl_lbl)
        lay.addWidget(grp_lbl)

        grp_font = QGroupBox(t("grp_font"))
        gl_font = QGridLayout()
        gl_font.setHorizontalSpacing(8)
        gl_font.setVerticalSpacing(6)

        self.combo_font = QComboBox()
        self.combo_font.addItems(["Times New Roman", "Arial", "Helvetica", "Calibri", "Courier New"])
        self.combo_font.setCurrentText(self.cfg.get('fontfamily', "Times New Roman"))

        self.spin_title_size = EmojiSpinBox()
        self.spin_title_size.setRange(6, 72)
        self.spin_title_size.setValue(int(self.cfg.get('size_title', 12)))
        self.spin_label_size = EmojiSpinBox()
        self.spin_label_size.setRange(6, 72)
        self.spin_label_size.setValue(int(self.cfg.get('size_label', 10)))
        self.spin_tick_size = EmojiSpinBox()
        self.spin_tick_size.setRange(6, 72)
        self.spin_tick_size.setValue(int(self.cfg.get('size_tick', 10)))

        gl_font.addWidget(QLabel(t("lbl_font")), 0, 0)
        gl_font.addWidget(self.combo_font, 0, 1)
        gl_font.addWidget(QLabel(t("lbl_title_size")), 1, 0)
        gl_font.addWidget(self.spin_title_size, 1, 1)
        gl_font.addWidget(QLabel(t("lbl_label_size")), 2, 0)
        gl_font.addWidget(self.spin_label_size, 2, 1)
        gl_font.addWidget(QLabel(t("lbl_tick_size")), 3, 0)
        gl_font.addWidget(self.spin_tick_size, 3, 1)

        grp_font.setLayout(gl_font)
        lay.addWidget(grp_font)

        lay.addStretch(1)

    # -------------------------
    # TAB: Lejant
    # -------------------------
    def _setup_tab_legend(self):
        lay = self._add_scroll_tab(t("tab_legend"))

        # Yerleşim ve boşluk ayarları
        grp_leg = QGroupBox(t("grp_legend_layout"))
        gl_leg = QGridLayout()
        gl_leg.setHorizontalSpacing(8)
        gl_leg.setVerticalSpacing(6)

        self.chk_leg_show = QCheckBox(t("chk_leg_show"))
        self.chk_leg_show.setChecked(self.cfg.get('legend_show', True))

        self.chk_leg_frame = QCheckBox(t("chk_leg_frame"))
        self.chk_leg_frame.setChecked(self.cfg.get('legend_frame', True))

        self.spin_leg_font = EmojiSpinBox()
        self.spin_leg_font.setRange(6, 24)
        self.spin_leg_font.setValue(self.cfg.get('legend_fontsize', 10))

        self.radio_auto = QRadioButton(t("radio_auto_loc"))
        self.radio_manual = QRadioButton(t("radio_manual_loc"))
        bg = QButtonGroup(self)
        bg.addButton(self.radio_auto)
        bg.addButton(self.radio_manual)

        self.combo_leg_loc = QComboBox()
        self.combo_leg_loc.addItems(['best', 'upper right', 'upper left', 'lower right', 'lower left'])
        self.combo_leg_loc.setCurrentText(self.cfg.get('legend_loc', 'best'))

        self.spin_leg_x = EmojiDoubleSpinBox()
        self.spin_leg_x.setRange(-0.5, 1.5)
        self.spin_leg_x.setSingleStep(0.05)
        self.spin_leg_x.setValue(self.cfg.get('legend_x', 1.0))

        self.spin_leg_y = EmojiDoubleSpinBox()
        self.spin_leg_y.setRange(-0.5, 1.5)
        self.spin_leg_y.setSingleStep(0.05)
        self.spin_leg_y.setValue(self.cfg.get('legend_y', 1.0))

        is_man = self.cfg.get('legend_manual', False)
        self.radio_manual.setChecked(is_man)
        self.radio_auto.setChecked(not is_man)

        self.combo_leg_layout = QComboBox()
        self.combo_leg_layout.addItem(t("legend_layout_auto"), "auto")
        self.combo_leg_layout.addItem(t("legend_layout_vertical"), "vertical")
        self.combo_leg_layout.addItem(t("legend_layout_horizontal"), "horizontal")
        self.combo_leg_layout.addItem(t("legend_layout_custom"), "custom")
        idx_layout = self.combo_leg_layout.findData(str(self.cfg.get("legend_layout_mode", "auto")))
        self.combo_leg_layout.setCurrentIndex(idx_layout if idx_layout >= 0 else 0)
        self.combo_leg_layout.currentIndexChanged.connect(self._on_legend_layout_mode_changed)

        self.spin_leg_ncol = EmojiSpinBox()
        self.spin_leg_ncol.setRange(1, 20)
        self.spin_leg_ncol.setValue(int(self.cfg.get("legend_ncol", 1)))

        self.spin_leg_handletextpad = EmojiDoubleSpinBox()
        self.spin_leg_handletextpad.setRange(0.0, 5.0)
        self.spin_leg_handletextpad.setSingleStep(0.1)
        self.spin_leg_handletextpad.setValue(float(self.cfg.get("legend_handletextpad", 0.8)))

        self.spin_leg_labelspacing = EmojiDoubleSpinBox()
        self.spin_leg_labelspacing.setRange(0.0, 5.0)
        self.spin_leg_labelspacing.setSingleStep(0.1)
        self.spin_leg_labelspacing.setValue(float(self.cfg.get("legend_labelspacing", 0.5)))

        self.spin_leg_columnspacing = EmojiDoubleSpinBox()
        self.spin_leg_columnspacing.setRange(0.0, 10.0)
        self.spin_leg_columnspacing.setSingleStep(0.1)
        self.spin_leg_columnspacing.setValue(float(self.cfg.get("legend_columnspacing", 2.0)))

        self.spin_leg_handlelength = EmojiDoubleSpinBox()
        self.spin_leg_handlelength.setRange(0.1, 10.0)
        self.spin_leg_handlelength.setSingleStep(0.1)
        self.spin_leg_handlelength.setValue(float(self.cfg.get("legend_handlelength", 2.5)))

        self.spin_leg_markerscale = EmojiDoubleSpinBox()
        self.spin_leg_markerscale.setRange(0.1, 5.0)
        self.spin_leg_markerscale.setSingleStep(0.1)
        self.spin_leg_markerscale.setValue(float(self.cfg.get("legend_markerscale", 1.0)))

        h_top = QHBoxLayout()
        h_top.setSpacing(12)
        h_top.addWidget(self.chk_leg_show)
        h_top.addWidget(self.chk_leg_frame)
        h_top.addStretch(1)
        h_top.addWidget(QLabel(t("lbl_font")))
        h_top.addWidget(self.spin_leg_font)
        gl_leg.addLayout(h_top, 0, 0, 1, 4)

        gl_leg.addWidget(self.radio_auto, 1, 0)
        gl_leg.addWidget(self.combo_leg_loc, 1, 1, 1, 3)

        gl_leg.addWidget(self.radio_manual, 2, 0)
        h_man = QHBoxLayout()
        h_man.setSpacing(6)
        h_man.addWidget(QLabel(t("lbl_leg_x")))
        h_man.addWidget(self.spin_leg_x)
        h_man.addWidget(QLabel(t("lbl_leg_y")))
        h_man.addWidget(self.spin_leg_y)
        gl_leg.addLayout(h_man, 2, 1, 1, 3)

        gl_leg.addWidget(QLabel(t("lbl_legend_layout")), 3, 0)
        gl_leg.addWidget(self.combo_leg_layout, 3, 1)
        gl_leg.addWidget(QLabel(t("lbl_legend_ncol")), 3, 2)
        gl_leg.addWidget(self.spin_leg_ncol, 3, 3)

        gl_leg.addWidget(QLabel(t("lbl_legend_handletextpad")), 4, 0)
        gl_leg.addWidget(self.spin_leg_handletextpad, 4, 1)
        gl_leg.addWidget(QLabel(t("lbl_legend_labelspacing")), 4, 2)
        gl_leg.addWidget(self.spin_leg_labelspacing, 4, 3)

        gl_leg.addWidget(QLabel(t("lbl_legend_columnspacing")), 5, 0)
        gl_leg.addWidget(self.spin_leg_columnspacing, 5, 1)
        gl_leg.addWidget(QLabel(t("lbl_legend_handlelength")), 5, 2)
        gl_leg.addWidget(self.spin_leg_handlelength, 5, 3)

        gl_leg.addWidget(QLabel(t("lbl_legend_markerscale")), 6, 0)
        gl_leg.addWidget(self.spin_leg_markerscale, 6, 1)

        grp_leg.setLayout(gl_leg)
        lay.addWidget(grp_leg)
        self._on_legend_layout_mode_changed(self.combo_leg_layout.currentIndex())

        # Öğe tablosu
        grp_items = QGroupBox(t("grp_legend_items"))
        v_items = QVBoxLayout()
        v_items.setContentsMargins(6, 6, 6, 6)
        v_items.setSpacing(6)

        self.tbl_legend_items = QTableWidget()
        self.tbl_legend_items.setColumnCount(5)
        self.tbl_legend_items.setHorizontalHeaderLabels([
            t("legend_col_show"),
            t("legend_col_type"),
            t("legend_col_source"),
            t("legend_col_text"),
            t("legend_col_order"),
        ])
        self.tbl_legend_items.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_legend_items.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl_legend_items.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.tbl_legend_items.verticalHeader().setVisible(False)
        hdr = self.tbl_legend_items.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_legend_items.setColumnWidth(2, 180)
        self.tbl_legend_items.setMaximumHeight(220)
        v_items.addWidget(self.tbl_legend_items)

        h_btn = QHBoxLayout()
        self.btn_legend_up = QPushButton(t("btn_legend_up"))
        self.btn_legend_down = QPushButton(t("btn_legend_down"))
        self.btn_legend_reload = QPushButton(t("btn_legend_reload"))
        self.btn_legend_up.clicked.connect(lambda: self._move_legend_item(-1))
        self.btn_legend_down.clicked.connect(lambda: self._move_legend_item(1))
        self.btn_legend_reload.clicked.connect(self._populate_legend_items_table)
        h_btn.addWidget(self.btn_legend_up)
        h_btn.addWidget(self.btn_legend_down)
        h_btn.addWidget(self.btn_legend_reload)
        h_btn.addStretch(1)
        v_items.addLayout(h_btn)

        grp_items.setLayout(v_items)
        lay.addWidget(grp_items)
        self._populate_legend_items_table()

        lay.addStretch(1)

    def _on_legend_layout_mode_changed(self, _idx: int):
        mode = str(self.combo_leg_layout.currentData() or "auto")
        self.spin_leg_ncol.setEnabled(mode == "custom")

    def _legend_objects_for_table(self):
        entries = []
        seq = 0
        for obj in self.series_list:
            entries.append(("data", obj, seq))
            seq += 1
        for obj in self.fit_list:
            entries.append(("fit", obj, seq))
            seq += 1

        ordered = []
        for kind, obj, seq_val in entries:
            try:
                order_val = int(obj.get("legend_order", seq_val))
            except Exception:
                order_val = seq_val
            ordered.append((kind, obj, seq_val, order_val))
        ordered.sort(key=lambda x: (x[3], x[2]))
        return ordered

    def _populate_legend_items_table(self):
        if not hasattr(self, "tbl_legend_items"):
            return
        entries = self._legend_objects_for_table()
        self._legend_table_objects = [obj for _, obj, _, _ in entries]
        tw = self.tbl_legend_items
        tw.blockSignals(True)
        tw.setRowCount(len(entries))
        for r, (kind, obj, _seq_val, _order_val) in enumerate(entries):
            show_item = QTableWidgetItem()
            show_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
            show_item.setCheckState(Qt.CheckState.Checked if obj.get("legend_show", True) else Qt.CheckState.Unchecked)
            tw.setItem(r, 0, show_item)

            kind_item = QTableWidgetItem(t("legend_type_data") if kind == "data" else t("legend_type_fit"))
            kind_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            tw.setItem(r, 1, kind_item)

            source_label = str(obj.get("label", ""))
            source_item = QTableWidgetItem(source_label)
            source_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            tw.setItem(r, 2, source_item)

            legend_text = str(obj.get("legend_label", source_label))
            text_item = QTableWidgetItem(legend_text)
            tw.setItem(r, 3, text_item)

            order_item = QTableWidgetItem(str(r + 1))
            order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            order_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            tw.setItem(r, 4, order_item)
        tw.blockSignals(False)
        if tw.rowCount() > 0 and tw.currentRow() < 0:
            tw.setCurrentCell(0, 3)

    def _apply_legend_table_to_objects(self):
        if not hasattr(self, "tbl_legend_items"):
            return
        tw = self.tbl_legend_items
        if not hasattr(self, "_legend_table_objects"):
            return
        n = min(tw.rowCount(), len(self._legend_table_objects))
        for r in range(n):
            obj = self._legend_table_objects[r]
            show_item = tw.item(r, 0)
            text_item = tw.item(r, 3)
            show_flag = True
            if show_item is not None:
                show_flag = show_item.checkState() == Qt.CheckState.Checked
            legend_text = ""
            if text_item is not None and text_item.text() is not None:
                legend_text = text_item.text().strip()
            if not legend_text:
                legend_text = str(obj.get("label", ""))
            obj["legend_show"] = bool(show_flag)
            obj["legend_label"] = legend_text
            obj["legend_order"] = int(r)

    def _move_legend_item(self, direction: int):
        if not hasattr(self, "tbl_legend_items"):
            return
        tw = self.tbl_legend_items
        row = tw.currentRow()
        if row < 0:
            return
        target = row + direction
        if target < 0 or target >= tw.rowCount():
            return
        self._apply_legend_table_to_objects()
        obj_a = self._legend_table_objects[row]
        obj_b = self._legend_table_objects[target]
        ord_a = int(obj_a.get("legend_order", row))
        ord_b = int(obj_b.get("legend_order", target))
        obj_a["legend_order"] = ord_b
        obj_b["legend_order"] = ord_a
        self._populate_legend_items_table()
        self.tbl_legend_items.setCurrentCell(target, 3)

    # -------------------------
    # -------------------------
    # TAB: Stiller
    # -------------------------
    def _make_collapsible(self, title: str, content_widget: QWidget,
                          collapsed: bool = True):
        wrapper = QWidget()
        vlay = QVBoxLayout(wrapper)
        vlay.setContentsMargins(0, 2, 0, 2)
        vlay.setSpacing(0)

        btn = QToolButton()
        btn.setText(f"  {title}")
        btn.setCheckable(True)
        btn.setChecked(not collapsed)
        btn.setArrowType(Qt.ArrowType.DownArrow if not collapsed else Qt.ArrowType.RightArrow)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setStyleSheet(
            "QToolButton { font-weight: 600; font-size: 11px; border: none; "
            "padding: 5px 4px; text-align: left; }"
        )
        content_widget.setVisible(not collapsed)

        def toggle(checked):
            content_widget.setVisible(checked)
            btn.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)

        btn.toggled.connect(toggle)
        vlay.addWidget(btn)
        vlay.addWidget(content_widget)
        return wrapper, btn

    def _setup_tab_style(self):
        from src.ui.color_themes import COLOR_THEMES, MARKER_SEQUENCE
        lay = self._add_scroll_tab(t("tab_styles"))

        # ── Global / Lokal toggle ─────────────────────────
        self._chk_global = QCheckBox(t("chk_global"))
        self._chk_global.setStyleSheet("font-weight: 600; padding: 4px 0;")
        self._chk_global.toggled.connect(self._on_global_toggled)
        self._chk_global.toggled.connect(lambda _: self._save_global_state())
        lay.addWidget(self._chk_global)

        # ── Seri listesi (lokal modda aktif) ─────────────
        self._lbl_series = QLabel(t("lbl_series"))
        lay.addWidget(self._lbl_series)
        self.list_style_series = QListWidget()
        self.list_style_series.setMaximumHeight(100)
        for s in self.series_list:
            pt = s.get('plot_type', 'scatter')
            icon = {'histogram': '📊', 'bar': '▬', 'scatter': '◉'}.get(pt, '◉')
            self.list_style_series.addItem(f"{icon} [Data] {s['label']}")
        for f in self.fit_list:
            self.list_style_series.addItem(f"[Fit] {f['label']}")
        lay.addWidget(self.list_style_series)

        # ── Global: Tema & Tip grubu ──────────────────────
        gtheme_w = QWidget()
        gtheme_f = QFormLayout(gtheme_w)
        gtheme_f.setContentsMargins(8, 4, 4, 8)
        gtheme_f.setVerticalSpacing(8)

        # Sembol göster/gizle (global mod)
        self.chk_global_marker = QCheckBox(t("chk_global_marker"))
        self.chk_global_marker.setChecked(True)
        self.chk_global_marker.toggled.connect(self._on_global_marker_toggled)
        self.chk_global_marker.toggled.connect(lambda _: self._save_global_state())
        gtheme_f.addRow(self.chk_global_marker)

        # Tema seçici
        self.combo_global_theme = QComboBox()
        self.combo_global_theme.addItem("— Tema Yok (renklere dokunma) —")
        self.combo_global_theme.addItems(list(COLOR_THEMES.keys()))
        self.combo_global_theme.currentTextChanged.connect(self._update_global_theme_preview)
        self.combo_global_theme.currentTextChanged.connect(lambda _: self._save_global_state())
        gtheme_f.addRow(t("lbl_color_theme"), self.combo_global_theme)

        # Önizleme şeridi
        self._global_preview_w = QWidget()
        self._global_preview_w.setFixedHeight(24)
        self._global_preview_layout = QHBoxLayout(self._global_preview_w)
        self._global_preview_layout.setContentsMargins(0, 0, 0, 0)
        self._global_preview_layout.setSpacing(2)
        gtheme_f.addRow("", self._global_preview_w)

        self._grp_global, self._btn_grp_global = self._make_collapsible(
            t("grp_theme_title"), gtheme_w, collapsed=False)
        self._grp_global.setVisible(False)
        lay.addWidget(self._grp_global)

        # ── Ortak stil ayarları ───────────────────────────
        # (Global modda: sembol hariç tümüne, Lokal modda: seçili seriye)
        self.btn_color = QPushButton(t("btn_color"))
        self.btn_color.clicked.connect(self.choose_color)
        self.current_color = "#000000"
        h_color = QHBoxLayout()
        h_color.addWidget(QLabel(t("lbl_color")))
        h_color.addWidget(self.btn_color, 1)
        self._w_color = QWidget()
        self._w_color.setLayout(h_color)
        lay.addWidget(self._w_color)

        # ── Scatter / Line grubu ──────────────────────────
        sw = QWidget()
        sf = QFormLayout(sw)
        sf.setVerticalSpacing(6)
        sf.setHorizontalSpacing(8)
        sf.setContentsMargins(8, 4, 4, 4)

        self.combo_marker = QComboBox()
        self.combo_marker.addItems([
            'None', t('marker_circle'), t('marker_square'), t('marker_tri_up'), t('marker_tri_down'),
            t('marker_tri_left'), t('marker_tri_right'), t('marker_diamond'), t('marker_thin_diamond'),
            t('marker_pentagon'), t('marker_hexagon1'), t('marker_hexagon2'),
            t('marker_x'), t('marker_plus'), t('marker_star') 
        ])
        self.spin_msize = EmojiSpinBox()
        self.spin_msize.setRange(0, 50)
        self.spin_mew = EmojiDoubleSpinBox()
        self.spin_mew.setRange(0.0, 10.0)
        self.spin_mew.setSingleStep(0.1)
        self.chk_filled = QCheckBox(t("chk_filled"))
        self.combo_line = QComboBox()
        self.combo_line.addItems(['None', '-', '--', ':', '-.'])
        self.combo_interp = QComboBox()
        self.combo_interp.addItems(['Linear', 'Spline'])
        self.spin_lwidth = EmojiDoubleSpinBox()
        self.spin_lwidth.setRange(0.0, 10.0)
        self.spin_lwidth.setSingleStep(0.1)
        self.spin_capsize = EmojiDoubleSpinBox()
        self.spin_capsize.setRange(0, 20)
        self.spin_capsize.setValue(1.0)
        self.spin_elinewidth = EmojiDoubleSpinBox()
        self.spin_elinewidth.setRange(0.1, 10.0)
        self.spin_elinewidth.setSingleStep(0.1)
        self.spin_elinewidth.setValue(0.8)
        self.btn_scatter_ecolor = QPushButton(t("btn_color"))
        self.btn_scatter_ecolor.clicked.connect(self.choose_scatter_ecolor)
        self.current_scatter_ecolor = "#000000"

        # Sembol satırı — wrapper widget ile gizlenebilir (global modda gizlenir)
        h_marker_row = QHBoxLayout()
        h_marker_row.setContentsMargins(0, 0, 0, 0)
        h_marker_row.addWidget(QLabel(t("lbl_marker")))
        h_marker_row.addWidget(self.combo_marker, 1)
        self._w_marker_row = QWidget()
        self._w_marker_row.setLayout(h_marker_row)

        # Boyut + Kenar satırı — wrapper widget
        h_sym = QHBoxLayout()
        h_sym.setSpacing(4)
        h_sym.addWidget(QLabel(t("lbl_marker_size")))
        h_sym.addWidget(self.spin_msize)
        h_sym.addWidget(QLabel(t("lbl_marker_edge")))
        h_sym.addWidget(self.spin_mew)
        self._w_sym_row = QWidget()
        self._w_sym_row.setLayout(h_sym)

        # İçi dolu satırı — wrapper widget
        h_filled = QHBoxLayout()
        h_filled.setContentsMargins(0, 0, 0, 0)
        h_filled.addWidget(self.chk_filled)
        self._w_filled_row = QWidget()
        self._w_filled_row.setLayout(h_filled)

        self._row_scatter_marker = sf.rowCount()
        sf.addRow(self._w_marker_row)
        sf.addRow(self._w_sym_row)
        sf.addRow(self._w_filled_row)
        sf.addRow(t("lbl_line_type"), self.combo_line)
        sf.addRow(t("lbl_interp"), self.combo_interp)
        sf.addRow(t("lbl_line_width"), self.spin_lwidth)
        sf.addRow(t("lbl_capsize"), self.spin_capsize)
        sf.addRow(t("lbl_elinewidth"), self.spin_elinewidth)
        sf.addRow(t("lbl_ecolor"), self.btn_scatter_ecolor)

        self._grp_scatter, self._btn_grp_scatter = self._make_collapsible(t("grp_scatter"), sw, collapsed=True)
        lay.addWidget(self._grp_scatter)

        # ── Bar grubu önce eklenir (histogram altında görünmesi için önce inşa et)
        # ── Histogram grubu ───────────────────────────────
        hw = QWidget()
        hf = QFormLayout(hw)
        hf.setVerticalSpacing(6)
        hf.setHorizontalSpacing(8)
        hf.setContentsMargins(8, 4, 4, 4)

        self.spin_bins = EmojiSpinBox()
        self.spin_bins.setRange(1, 500)
        self.spin_bins.setValue(20)
        self.spin_alpha = EmojiDoubleSpinBox()
        self.spin_alpha.setRange(0.0, 1.0)
        self.spin_alpha.setSingleStep(0.05)
        self.spin_alpha.setValue(0.7)
        self.combo_edgecolor = QComboBox()
        self.combo_edgecolor.addItems(['white', 'black', 'none'])

        hf.addRow(t("lbl_bins"), self.spin_bins)
        hf.addRow(t("lbl_bar_alpha"), self.spin_alpha)
        hf.addRow(t("lbl_edge_color"), self.combo_edgecolor)

        self._grp_hist, self._btn_grp_hist = self._make_collapsible(t("grp_hist"), hw, collapsed=True)
        # (hist layout'a bar'dan sonra ekleniyor)

        bw = QWidget()
        bf = QFormLayout(bw)
        bf.setVerticalSpacing(6)
        bf.setHorizontalSpacing(8)
        bf.setContentsMargins(8, 4, 4, 4)

        self.spin_bar_width = EmojiDoubleSpinBox()
        self.spin_bar_width.setRange(1e-6, 1e6)
        self.spin_bar_width.setSingleStep(0.05)
        self.spin_bar_width.setValue(0.8)
        self.chk_bar_filled = QCheckBox(t("chk_filled"))
        self.chk_bar_filled.setChecked(True)
        self.chk_bar_filled.toggled.connect(self._on_bar_filled_toggled)
        self.spin_bar_edge_width = EmojiDoubleSpinBox()
        self.spin_bar_edge_width.setRange(0.1, 10.0)
        self.spin_bar_edge_width.setSingleStep(0.1)
        self.spin_bar_edge_width.setValue(1.0)
        self.spin_bar_alpha = EmojiDoubleSpinBox()
        self.spin_bar_alpha.setRange(0.0, 1.0)
        self.spin_bar_alpha.setSingleStep(0.05)
        self.spin_bar_alpha.setValue(1.0)
        self.combo_bar_edgecolor = QComboBox()
        self.combo_bar_edgecolor.addItems(['none', 'black', 'white'])
        self.btn_ecolor = QPushButton(t("btn_color"))
        self.btn_ecolor.clicked.connect(self.choose_ecolor)
        self.current_ecolor = "#000000"
        self.spin_bar_capsize = EmojiDoubleSpinBox()
        self.spin_bar_capsize.setRange(0, 20)
        self.spin_bar_capsize.setValue(3.0)
        self.spin_bar_elinewidth = EmojiDoubleSpinBox()
        self.spin_bar_elinewidth.setRange(0.1, 10.0)
        self.spin_bar_elinewidth.setSingleStep(0.1)
        self.spin_bar_elinewidth.setValue(1.0)
        self.combo_bar_mode = QComboBox()
        self.combo_bar_mode.addItem(t("bar_mode_overlay"), "overlay")
        self.combo_bar_mode.addItem(t("bar_mode_grouped"), "grouped")
        idx_bar_mode = self.combo_bar_mode.findData(str(self.cfg.get("bar_mode", "overlay")))
        self.combo_bar_mode.setCurrentIndex(idx_bar_mode if idx_bar_mode >= 0 else 0)

        bf.addRow(t("lbl_bar_width"), self.spin_bar_width)
        bf.addRow(t("lbl_bar_mode"), self.combo_bar_mode)
        bf.addRow(t("chk_filled"), self.chk_bar_filled)
        self._row_bar_edgew_lbl = QLabel(t("lbl_spine_width"))
        bf.addRow(self._row_bar_edgew_lbl, self.spin_bar_edge_width)
        bf.addRow(t("lbl_bar_alpha"), self.spin_bar_alpha)
        bf.addRow(t("lbl_edge_color"), self.combo_bar_edgecolor)
        bf.addRow(t("lbl_bar_ecolor"), self.btn_ecolor)
        bf.addRow(t("lbl_bar_capsize"), self.spin_bar_capsize)
        bf.addRow(t("lbl_bar_elinewidth"), self.spin_bar_elinewidth)

        self._grp_bar, self._btn_grp_bar = self._make_collapsible(t("grp_bar"), bw, collapsed=True)
        lay.addWidget(self._grp_bar)
        lay.addWidget(self._grp_hist)

        # ── Global Uygula butonu — Apply ile birleştirildi, burada yok
        # apply_settings() çağrılınca global mod aktifse otomatik uygulanır

        # Başta her şey gizli
        self._w_color.setVisible(False)

        self.list_style_series.currentRowChanged.connect(self.load_series_style)
        if self.list_style_series.count() > 0:
            self.list_style_series.setCurrentRow(0)

        # Panele özgü global state'i yükle
        self._load_global_state(self._last_pid)

        lay.addStretch(1)

    def _on_global_toggled(self, checked: bool):
        """Global mod açılınca seri listesi pasifleşir, tema grubu görünür."""
        self.list_style_series.setEnabled(not checked)
        self._lbl_series.setEnabled(not checked)
        self._grp_global.setVisible(checked)

        if checked:
            self._w_color.setVisible(False)
            self._grp_scatter.setVisible(True)
            self._btn_grp_scatter.setChecked(True)
            self._grp_hist.setVisible(False)
            self._grp_bar.setVisible(False)
            # Sembol tipi combo'yu gizle — show_marker checkbox'a göre boyut/kenar/dolu göster
            self._w_marker_row.setVisible(False)
            show_mk = self.chk_global_marker.isChecked() if hasattr(self, 'chk_global_marker') else True
            self._w_sym_row.setVisible(show_mk)
            self._w_filled_row.setVisible(show_mk)
        else:
            self._w_marker_row.setVisible(True)
            self._w_sym_row.setVisible(True)
            self._w_filled_row.setVisible(True)
            row = self.list_style_series.currentRow()
            if row >= 0:
                self.load_series_style(row)

    def _on_global_marker_toggled(self, checked: bool):
        """Global modda sembol göster/gizle değişince boyut/kenar/dolu satırlarını ayarla."""
        if hasattr(self, '_w_sym_row'):
            self._w_sym_row.setVisible(checked)
        if hasattr(self, '_w_filled_row'):
            self._w_filled_row.setVisible(checked)

    def _update_global_theme_preview(self, theme_name: str):
        from src.ui.color_themes import COLOR_THEMES
        layout = self._global_preview_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        colors = COLOR_THEMES.get(theme_name, [])
        for c in colors:
            swatch = QWidget()
            swatch.setFixedSize(20, 20)
            swatch.setStyleSheet(f"background: {c}; border-radius: 3px;")
            layout.addWidget(swatch)
        layout.addStretch(1)

    def _apply_global_style(self):
        """Aktif paneldeki tüm scatter/line serilerine global ayarları uygula."""
        from src.ui.color_themes import COLOR_THEMES, MARKER_SEQUENCE

        theme_name = self.combo_global_theme.currentText()
        use_theme  = theme_name != "— Tema Yok (renklere dokunma) —"
        colors     = COLOR_THEMES.get(theme_name, []) if use_theme else []

        show_marker = self.chk_global_marker.isChecked()

        # Ortak stil değerleri
        lwidth  = self.spin_lwidth.value()
        msize   = self.spin_msize.value()
        mew     = self.spin_mew.value()
        filled  = self.chk_filled.isChecked() if show_marker else False
        capsize = self.spin_capsize.value()
        elw     = self.spin_elinewidth.value()
        interp  = self.combo_interp.currentText().lower()

        pid    = self._last_pid
        series = self.main_window.data_manager.get_series_for_panel(pid)
        idx    = 0

        for s in series:
            if s.get('plot_type', 'scatter') != 'scatter':
                continue  # Bar ve histogram'a dokunma

            # Renk
            if use_theme and colors:
                s['color'] = colors[idx % len(colors)]
                s['ecolor'] = s['color']

            # Sembol
            if show_marker:
                s['marker'] = MARKER_SEQUENCE[idx % len(MARKER_SEQUENCE)]
            else:
                s['marker'] = 'None'

            # Çizgi tipi — combo_line'dan al
            s['linestyle'] = self.combo_line.currentText()

            # Ortak stiller
            s['linewidth']       = lwidth
            s['markersize']      = msize
            s['markeredgewidth'] = mew
            s['filled']          = filled
            s['capsize']         = capsize
            s['elinewidth']      = elw
            s['interpolation']   = interp

            idx += 1

        self.main_window.mark_modified()
        self.main_window.redraw_plot()

    def _set_style_groups_visible(self, plot_type: str):
        """Sadece ilgili grubu aç, diğerlerini kapat."""
        is_scatter = plot_type == 'scatter'
        is_hist    = plot_type == 'histogram'
        is_bar     = plot_type == 'bar'
        show       = plot_type in ('scatter', 'histogram', 'bar')

        self._w_color.setVisible(show)

        # Scatter grubunu aç/kapat
        self._grp_scatter.setVisible(is_scatter)
        if is_scatter:
            self._btn_grp_scatter.setChecked(True)

        # Histogram grubunu aç/kapat
        self._grp_hist.setVisible(is_hist)
        if is_hist:
            self._btn_grp_hist.setChecked(True)

        # Bar grubunu aç/kapat
        self._grp_bar.setVisible(is_bar)
        if is_bar:
            self._btn_grp_bar.setChecked(True)

    # -------------------------
    # TAB: Renk Teması
    # -------------------------
    # -------------------------
    # TAB: Canvas Ayarları (YENİ)
    # -------------------------
    def _setup_tab_canvas(self):
        lay = self._add_scroll_tab(t("tab_canvas"))

        info = QLabel(t("info_canvas"))
        info.setWordWrap(True)
        info.setStyleSheet("color: gray; font-size: 10px; padding-bottom: 4px;")
        lay.addWidget(info)

        # Boyut (cm) — figure-level
        grp_dim = QGroupBox(t("grp_dim"))
        gl_dim = QGridLayout()
        gl_dim.setHorizontalSpacing(8)
        gl_dim.setVerticalSpacing(6)

        self.spin_width = EmojiDoubleSpinBox()
        self.spin_width.setRange(2, 50)
        self.spin_width.setValue(self.cc.get('width_cm', 10.0))
        self.spin_height = EmojiDoubleSpinBox()
        self.spin_height.setRange(2, 50)
        self.spin_height.setValue(self.cc.get('height_cm', 8.0))

        self.combo_preset = QComboBox()
        self.combo_preset.addItems([t("preset_custom"), t("preset_single"), t("preset_one_half"), t("preset_full"), t("preset_a4half")])
        self.combo_preset.currentIndexChanged.connect(self.apply_preset)

        gl_dim.addWidget(QLabel(t("lbl_width")), 0, 0)
        gl_dim.addWidget(self.spin_width, 0, 1)
        gl_dim.addWidget(QLabel(t("lbl_height")), 1, 0)
        gl_dim.addWidget(self.spin_height, 1, 1)
        gl_dim.addWidget(QLabel(t("lbl_preset")), 2, 0)
        gl_dim.addWidget(self.combo_preset, 2, 1)

        grp_dim.setLayout(gl_dim)
        lay.addWidget(grp_dim)

        # Subplot Boşlukları
        grp_sp = QGroupBox(t("grp_subplots"))
        gl_sp = QGridLayout()
        gl_sp.setHorizontalSpacing(8)
        gl_sp.setVerticalSpacing(6)

        self.spin_hspace = EmojiDoubleSpinBox()
        self.spin_hspace.setRange(0.0, 2.0)
        self.spin_hspace.setSingleStep(0.05)
        self.spin_hspace.setValue(self.cc.get('hspace', 0.4))

        self.spin_wspace = EmojiDoubleSpinBox()
        self.spin_wspace.setRange(0.0, 2.0)
        self.spin_wspace.setSingleStep(0.05)
        self.spin_wspace.setValue(self.cc.get('wspace', 0.3))

        gl_sp.addWidget(QLabel(t("lbl_hspace")), 0, 0)
        gl_sp.addWidget(self.spin_hspace, 0, 1)
        gl_sp.addWidget(QLabel(t("lbl_wspace")), 1, 0)
        gl_sp.addWidget(self.spin_wspace, 1, 1)
        grp_sp.setLayout(gl_sp)
        lay.addWidget(grp_sp)

        # Figure Kenar Boşlukları
        grp_fm = QGroupBox(t("grp_margins"))
        gl_fm = QGridLayout()
        gl_fm.setHorizontalSpacing(8)
        gl_fm.setVerticalSpacing(6)

        self.spin_cc_left = EmojiDoubleSpinBox()
        self.spin_cc_left.setRange(0.0, 0.99)
        self.spin_cc_left.setSingleStep(0.01)
        self.spin_cc_left.setValue(self.cc.get('margin_left', 0.12))

        self.spin_cc_bottom = EmojiDoubleSpinBox()
        self.spin_cc_bottom.setRange(0.0, 0.99)
        self.spin_cc_bottom.setSingleStep(0.01)
        self.spin_cc_bottom.setValue(self.cc.get('margin_bottom', 0.12))

        self.spin_cc_right = EmojiDoubleSpinBox()
        self.spin_cc_right.setRange(0.01, 1.0)
        self.spin_cc_right.setSingleStep(0.01)
        self.spin_cc_right.setValue(self.cc.get('margin_right', 0.95))

        self.spin_cc_top = EmojiDoubleSpinBox()
        self.spin_cc_top.setRange(0.01, 1.0)
        self.spin_cc_top.setSingleStep(0.01)
        self.spin_cc_top.setValue(self.cc.get('margin_top', 0.95))

        gl_fm.addWidget(QLabel(t("lbl_margin_left")), 0, 0)
        gl_fm.addWidget(self.spin_cc_left, 0, 1)
        gl_fm.addWidget(QLabel(t("lbl_margin_bottom")), 0, 2)
        gl_fm.addWidget(self.spin_cc_bottom, 0, 3)
        gl_fm.addWidget(QLabel(t("lbl_margin_right")), 1, 0)
        gl_fm.addWidget(self.spin_cc_right, 1, 1)
        gl_fm.addWidget(QLabel(t("lbl_margin_top")), 1, 2)
        gl_fm.addWidget(self.spin_cc_top, 1, 3)

        grp_fm.setLayout(gl_fm)
        lay.addWidget(grp_fm)

        lay.addStretch(1)

    # -------------------------
    # Helpers
    # -------------------------
    def apply_preset(self, idx):
        if idx == 1:
            self.spin_width.setValue(8.5)
            self.spin_height.setValue(6.5)
        elif idx == 2:
            self.spin_width.setValue(13.0)
            self.spin_height.setValue(8.0)
        elif idx == 3:
            self.spin_width.setValue(17.0)
            self.spin_height.setValue(10.0)
        elif idx == 4:
            self.spin_width.setValue(14.0)
            self.spin_height.setValue(10.0)

    def toggle_inputs(self):
        m = self.radio_manual.isChecked()
        self.spin_leg_x.setEnabled(m)
        self.spin_leg_y.setEnabled(m)
        self.combo_leg_loc.setEnabled(not m)

        xa = self.chk_x_auto.isChecked()
        self.spin_x_min.setEnabled(not xa)
        self.spin_x_max.setEnabled(not xa)
        self.spin_x_step.setEnabled(not xa)

        ya = self.chk_y_auto.isChecked()
        self.spin_y_min.setEnabled(not ya)
        self.spin_y_max.setEnabled(not ya)
        self.spin_y_step.setEnabled(not ya)

        yra = self.chk_yr_auto.isChecked()
        self.spin_yr_min.setEnabled(not yra)
        self.spin_yr_max.setEnabled(not yra)
        self.spin_yr_step.setEnabled(not yra)

    def get_selected_object(self):
        row = self.list_style_series.currentRow()
        if row < 0:
            return None
        if row < len(self.series_list):
            return self.series_list[row]
        return self.fit_list[row - len(self.series_list)]

    def load_series_style(self, row):
        obj = self.get_selected_object()
        if not obj:
            return

        pt = obj.get('plot_type', 'scatter')
        self._set_style_groups_visible(pt)

        self.current_color = obj.get('color', '#000000')
        self.btn_color.setStyleSheet(f"background-color: {self.current_color}")

        if pt == 'scatter':
            # combobox index order:
            # 0=None, 1=o, 2=s, 3=^, 4=v, 5=<, 6=>, 7=D, 8=d, 9=p, 10=h, 11=H, 12=x, 13=+, 14=*
            m_map = {
                None: 0,
                'None': 0,
                'o': 1,
                's': 2,
                '^': 3,
                'v': 4,
                '<': 5,
                '>': 6,
                'D': 7,
                'd': 8,
                'p': 9,
                'h': 10,
                'H': 11,
                'x': 12,
                '+': 13,
                '*': 14,
            }
            self.combo_marker.setCurrentIndex(m_map.get(obj.get('marker', 'o'), 1))
            l_map = {'None': 0, '-': 1, '--': 2, ':': 3, '-.': 4}
            self.combo_line.setCurrentIndex(l_map.get(obj.get('linestyle', 'None'), 0))
            i_map = {'linear': 0, 'spline': 1}
            self.combo_interp.setCurrentIndex(i_map.get(obj.get('interpolation', 'linear'), 0))
            self.chk_filled.setChecked(obj.get('filled', False))
            self.spin_msize.setValue(int(obj.get('markersize', 3)))
            self.spin_mew.setValue(float(obj.get('markeredgewidth', 0.5)))
            self.spin_lwidth.setValue(float(obj.get('linewidth', 0.5)))
            self.spin_capsize.setValue(float(obj.get('capsize', 1)))
            self.spin_elinewidth.setValue(float(obj.get('elinewidth', 0.8)))
            self.current_scatter_ecolor = obj.get('ecolor', obj.get('color', '#000000'))
            self.btn_scatter_ecolor.setStyleSheet(f"background-color: {self.current_scatter_ecolor}")
        elif pt == 'histogram':
            self.spin_bins.setValue(int(obj.get('bins', 20)))
            self.spin_alpha.setValue(float(obj.get('alpha', 0.7)))
            ec = obj.get('edgecolor', 'white')
            idx = self.combo_edgecolor.findText(ec)
            self.combo_edgecolor.setCurrentIndex(max(0, idx))
        elif pt == 'bar':
            self.spin_bar_width.setValue(float(obj.get('bar_width', 0.8)))
            idx_mode = self.combo_bar_mode.findData(str(self.cfg.get("bar_mode", "overlay")))
            self.combo_bar_mode.setCurrentIndex(idx_mode if idx_mode >= 0 else 0)
            filled = obj.get('bar_filled', True)
            self.chk_bar_filled.setChecked(filled)
            self.spin_bar_edge_width.setVisible(not filled)
            self._row_bar_edgew_lbl.setVisible(not filled)
            self.spin_bar_edge_width.setValue(float(obj.get('bar_edge_width', 1.0)))
            self.spin_bar_alpha.setValue(float(obj.get('alpha', 1.0)))
            ec = obj.get('edgecolor', 'none')
            idx = self.combo_bar_edgecolor.findText(ec)
            self.combo_bar_edgecolor.setCurrentIndex(max(0, idx))
            self.current_ecolor = obj.get('ecolor', '#000000')
            self.btn_ecolor.setStyleSheet(f"background-color: {self.current_ecolor}")
            self.spin_bar_capsize.setValue(float(obj.get('capsize', 3.0)))
            self.spin_bar_elinewidth.setValue(float(obj.get('elinewidth', 1.0)))

    def choose_scatter_ecolor(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.current_scatter_ecolor = c.name()
            self.btn_scatter_ecolor.setStyleSheet(f"background-color: {self.current_scatter_ecolor}")
            obj = self.get_selected_object()
            if obj:
                obj['ecolor'] = self.current_scatter_ecolor

    def choose_ecolor(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.current_ecolor = c.name()
            self.btn_ecolor.setStyleSheet(f"background-color: {self.current_ecolor}")
            obj = self.get_selected_object()
            if obj:
                obj['ecolor'] = self.current_ecolor

    def _on_bar_filled_toggled(self, checked: bool):
        self.spin_bar_edge_width.setVisible(not checked)
        self._row_bar_edgew_lbl.setVisible(not checked)
        obj = self.get_selected_object()
        if obj and obj.get('plot_type') == 'bar':
            obj['bar_filled'] = checked
            self.main_window.mark_modified()
            self.main_window.redraw_plot()

    def choose_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.current_color = c.name()
            self.btn_color.setStyleSheet(f"background-color: {self.current_color}")
            obj = self.get_selected_object()
            if obj:
                obj['color'] = self.current_color

    # -------------------------
    # APPLY
    # -------------------------
    def apply_settings(self):
        try:
            # Global mod aktifse önce tema/stil uygula
            if hasattr(self, '_chk_global') and self._chk_global.isChecked():
                self._apply_global_style()

            # Aktif panelin config'ini güncelle
            self.cfg.update({
                'title': self.inp_title.text(),
                'xlabel': self.inp_xlabel.text(),
                'ylabel': self.inp_ylabel.text(),
                'ylabel_right': self.inp_ylabel_right.text(),
                'math_mode': self.chk_math_mode.isChecked(),
                'title_pad': self.spin_title_pad.value(),
                'xlabel_pad': self.spin_xlabel_pad.value(),
                'ylabel_pad': self.spin_ylabel_pad.value(),
                'ylabel_right_pad': self.spin_ylabel_right_pad.value(),
                'show_xticklabels': self.chk_show_xticklabels.isChecked(),
                'show_yticklabels': self.chk_show_yticklabels.isChecked(),
                'show_yrticklabels': self.chk_show_yrticklabels.isChecked(),

                'title_bold': self.chk_title_bold.isChecked(),
                'title_italic': self.chk_title_italic.isChecked(),
                'xlabel_bold': self.chk_xlabel_bold.isChecked(),
                'xlabel_italic': self.chk_xlabel_italic.isChecked(),
                'ylabel_bold': self.chk_ylabel_bold.isChecked(),
                'ylabel_italic': self.chk_ylabel_italic.isChecked(),
                'ylabel_right_bold': self.chk_ylabel_right_bold.isChecked(),
                'ylabel_right_italic': self.chk_ylabel_right_italic.isChecked(),

                'spine_width': self.spin_spine_width.value(),
                'spine_bottom': self.chk_spine_bottom.isChecked(),
                'spine_top': self.chk_spine_top.isChecked(),
                'spine_left': self.chk_spine_left.isChecked(),
                'spine_right': self.chk_spine_right.isChecked(),
                'tick_bottom': self.chk_tick_bottom.isChecked(),
                'tick_top': self.chk_tick_top.isChecked(),
                'tick_left': self.chk_tick_left.isChecked(),
                'tick_right': self.chk_tick_right.isChecked(),

                'tick_major_len': self.spin_maj_len.value(),
                'tick_major_width': self.spin_maj_wid.value(),
                'tick_minor_len': self.spin_min_len.value(),
                'tick_minor_width': self.spin_min_wid.value(),

                'x_tick_rotation': self.spin_x_rotation.value(),
                'y_tick_rotation': self.spin_y_rotation.value(),
                'y_right_tick_rotation': self.spin_yr_rotation.value(),
                'x_tick_notation': self.combo_x_notation.currentData(),
                'y_tick_notation': self.combo_y_notation.currentData(),
                'y_right_tick_notation': self.combo_yr_notation.currentData(),
                'x_tick_sci_style': 'pow10' if self.combo_x_notation.currentData() in ("pow10", "pow10_offset") else 'e',
                'y_tick_sci_style': 'pow10' if self.combo_y_notation.currentData() in ("pow10", "pow10_offset") else 'e',
                'y_right_tick_sci_style': 'pow10' if self.combo_yr_notation.currentData() in ("pow10", "pow10_offset") else 'e',

                'grid': self.chk_grid.isChecked(),
                'grid_style': self.combo_grid_style.currentText().split()[0],
                'grid_alpha': self.spin_grid_alpha.value(),

                'logx': self.chk_logx.isChecked(),
                'logy': self.chk_logy.isChecked(),
                'logy_right': self.chk_logyr.isChecked(),

                'x_auto': self.chk_x_auto.isChecked(),
                'x_min': self.spin_x_min.value(),
                'x_max': self.spin_x_max.value(),
                'x_step': self.spin_x_step.value(),
                'x_minor': self.spin_x_minor.value(),

                'y_auto': self.chk_y_auto.isChecked(),
                'y_min': self.spin_y_min.value(),
                'y_max': self.spin_y_max.value(),
                'y_step': self.spin_y_step.value(),
                'y_minor': self.spin_y_minor.value(),

                'y_right_auto': self.chk_yr_auto.isChecked(),
                'y_right_min': self.spin_yr_min.value(),
                'y_right_max': self.spin_yr_max.value(),
                'y_right_step': self.spin_yr_step.value(),
                'y_right_minor': self.spin_yr_minor.value(),

                'fontfamily': self.combo_font.currentText(),
                'size_title': self.spin_title_size.value(),
                'size_label': self.spin_label_size.value(),
                'size_tick': self.spin_tick_size.value(),
                'legend_show': self.chk_leg_show.isChecked(),
                'legend_manual': self.radio_manual.isChecked(),
                'legend_loc': self.combo_leg_loc.currentText(),
                'legend_x': self.spin_leg_x.value(),
                'legend_y': self.spin_leg_y.value(),
                'legend_frame': self.chk_leg_frame.isChecked(),
                'legend_fontsize': self.spin_leg_font.value(),
                'legend_layout_mode': str(self.combo_leg_layout.currentData() or 'auto'),
                'legend_ncol': int(self.spin_leg_ncol.value()),
                'legend_handletextpad': float(self.spin_leg_handletextpad.value()),
                'legend_labelspacing': float(self.spin_leg_labelspacing.value()),
                'legend_columnspacing': float(self.spin_leg_columnspacing.value()),
                'legend_handlelength': float(self.spin_leg_handlelength.value()),
                'legend_markerscale': float(self.spin_leg_markerscale.value()),
            })

            # Canvas config (figure-level) güncelle
            self.cc.update({
                'width_cm': self.spin_width.value(),
                'height_cm': self.spin_height.value(),
                'hspace': self.spin_hspace.value(),
                'wspace': self.spin_wspace.value(),
                'margin_left': self.spin_cc_left.value(),
                'margin_bottom': self.spin_cc_bottom.value(),
                'margin_right': self.spin_cc_right.value(),
                'margin_top': self.spin_cc_top.value(),
            })
            self.cfg['bar_mode'] = str(self.combo_bar_mode.currentData() or 'overlay')

            # Stil seçimi — global modda _apply_global_style zaten halletti, tekrar yazma
            if not (hasattr(self, '_chk_global') and self._chk_global.isChecked()):
                obj = self.get_selected_object()
                if obj:
                    obj['color'] = self.current_color
                    pt = obj.get('plot_type', 'scatter')
                    if pt == 'scatter':
                        m = self.combo_marker.currentText().split()[0]
                        obj['marker'] = 'None' if m == 'None' else m
                        l = self.combo_line.currentText()
                        obj['linestyle'] = 'None' if l == 'None' else l
                        obj['interpolation'] = ['linear', 'spline'][self.combo_interp.currentIndex()]
                        obj['filled'] = self.chk_filled.isChecked()
                        obj['markersize'] = self.spin_msize.value()
                        obj['markeredgewidth'] = self.spin_mew.value()
                        obj['linewidth'] = self.spin_lwidth.value()
                        obj['capsize'] = self.spin_capsize.value()
                        obj['elinewidth'] = self.spin_elinewidth.value()
                        obj['ecolor'] = self.current_scatter_ecolor
                    elif pt == 'histogram':
                        obj['bins'] = self.spin_bins.value()
                        obj['alpha'] = self.spin_alpha.value()
                        obj['edgecolor'] = self.combo_edgecolor.currentText()
                    elif pt == 'bar':
                        obj['bar_width'] = self.spin_bar_width.value()
                        obj['bar_filled'] = self.chk_bar_filled.isChecked()
                        obj['bar_edge_width'] = self.spin_bar_edge_width.value()
                        obj['alpha'] = self.spin_bar_alpha.value()
                        obj['edgecolor'] = self.combo_bar_edgecolor.currentText()
                        obj['ecolor'] = self.current_ecolor
                        obj['capsize'] = self.spin_bar_capsize.value()
                        obj['elinewidth'] = self.spin_bar_elinewidth.value()
                        if obj['bar_width'] > 5.0:
                            bar_mode = str(self.cfg.get('bar_mode', 'overlay'))
                            msg_key = "status_bar_width_large_grouped" if bar_mode == "grouped" else "status_bar_width_large"
                            self.main_window.statusBar().showMessage(
                                t(msg_key, w=obj['bar_width']),
                                6000
                            )

            self._apply_legend_table_to_objects()
            self.main_window.mark_modified()
            self.main_window._refresh_series_list()
            self.main_window.redraw_plot()

        except Exception as e:
            print(f"Error: {e}")

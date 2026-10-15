import os
import importlib.util
import inspect
from itertools import cycle
from functools import partial
import io
import warnings

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QGroupBox, QListWidget, QListWidgetItem, QTableWidget, QCheckBox,
    QTableWidgetItem, QTabWidget, QRadioButton, QGridLayout, QSplitter,
    QButtonGroup, QFileDialog, QMessageBox, QFormLayout, QAbstractItemView, QLineEdit,
    QScrollArea, QApplication, QInputDialog, QPlainTextEdit, QSizePolicy, QToolButton,
    QDialog, QDialogButtonBox, QMenu, QFrame
)
from PyQt6.QtGui import QColor, QPalette, QAction, QKeySequence, QFont
from PyQt6.QtCore import Qt, QEvent, QItemSelectionModel

# --- MATPLOTLIB ---
from matplotlib.widgets import SpanSelector
from matplotlib.mathtext import MathTextParser
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import OptimizeWarning, curve_fit
from src.ui.python_exporter import export_as_python, export_as_notebook
from src.ui.data_ops_dialog import DataOpsDialog
from src.ui.main_window.dialogs_mixin import MainWindowDialogsMixin
from src.ui.main_window.theme_mixin import MainWindowThemeMixin
import numpy as np
import pandas as pd

# --- MODÜLLER ---
from src.plotting.canvas import MplCanvas
from src.analysis.data_manager import DataManager
from src.analysis.fit_utils import prepare_fit_xy, evaluate_fit_model, fit_statistics
from src.analysis.text_utils import format_panel_label, get_text_preset
from src.project_schema import ProjectSchemaError, read_project, write_project
from src.ui.emoji_spinbox import EmojiDoubleSpinBox, EmojiSpinBox
from src.ui.dialogs import FitDialog, PlotSettingsDialog, DataImportDialog
from lang import t, set_language, get_language

from src.ui.color_themes import COLOR_THEMES, reset_color_cycle
from src.version import APP_NAME, DISPLAY_VERSION

_COLOR_CYCLE_state = {'cycle': reset_color_cycle()}

def _reset_color_cycle(theme_name: str = None):
    _COLOR_CYCLE_state['cycle'] = reset_color_cycle(theme_name)

COLOR_CYCLE = _COLOR_CYCLE_state['cycle']

MARKER_CYCLE = cycle([
    'o', 's', '^', 'v', '<', '>',
    'D', 'd', 'p', 'h', 'H',
    'x', '+', '*', '1', '2'
])

# Layout seçenekleri: (label, rows, cols)
def _build_layout_options():
    return [
        ("1×1", 1, 1),
        (f"1×2 ({t('layout_side_by_side')})", 1, 2),
        (f"2×1 ({t('layout_stacked')})", 2, 1),
        ("2×2", 2, 2),
        ("3×1", 3, 1),
        ("1×3", 1, 3),
        ("3×2", 3, 2),
        ("2×3", 2, 3),
        (t("layout_custom"), None, None),
    ]

LAYOUT_OPTIONS = _build_layout_options()


class MainWindow(MainWindowDialogsMixin, MainWindowThemeMixin, QMainWindow):
    def __init__(self):
        super().__init__()
        self._app_title = APP_NAME
        self._app_version = DISPLAY_VERSION
        self.setWindowTitle(f"{self._app_title} {self._app_version}")

        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            w = min(1200, int(geo.width() * 0.95))
            h = min(780, int(geo.height() * 0.90))
            self.resize(w, h)
            self.move(geo.center() - self.rect().center())
        else:
            self.setGeometry(100, 100, 1200, 700)

        plt.rcParams['mathtext.fontset'] = 'cm'
        plt.rcParams['mathtext.rm'] = 'serif'

        self._current_theme = "light"

        self.data_manager = DataManager()
        # series_list artık data_manager üzerinden yönetiliyor (property)
        self.fit_list = []
        self.loaded_models = {}
        self._model_meta   = {}

        # Canvas-genelinde (tüm figure) ayarlar
        self.canvas_config = {
            'width_cm': 10.0,
            'height_cm': 8.0,
            'hspace': 0.4,   # subplot dikey boşluk
            'wspace': 0.3,   # subplot yatay boşluk
            'margin_left': 0.12,
            'margin_bottom': 0.12,
            'margin_right': 0.95,
            'margin_top': 0.95,
        }

        self.fit_xrange = None
        self._span_selectors = []   # Her panel için ayrı SpanSelector listesi
        self._is_modified = False
        self._last_table_undo_df = None
        self._last_table_undo_action = ""
        self._column_roles = {}
        self._table_plot_syncing = False
        self._role_scroll_syncing = False
        self._role_combos = []
        self._last_dialog_dir = os.path.expanduser("~")
        self._current_project_path = None
        self.text_items = []
        self._next_text_item_id = 1
        self.text_auto_cfg = {
            "enabled": False,
            "style": "lower_rparen",
            "x": 0.02,
            "y": 0.98,
            "ha": "left",
            "va": "top",
            "fontsize": 11,
            "bold": True,
            "italic": False,
            "math_mode": False,
        }

        self.setup_ui_components()
        self._create_menu()
        self.apply_theme(self._current_theme)
        self.populate_models()

    # --------------------------------------------------
    # Kısayol: aktif panel config'i
    # --------------------------------------------------
    @property
    def plot_config(self):
        """Geriye dönük uyumluluk: aktif panelin config'ini döndürür."""
        return self.canvas.get_active_config()

    @plot_config.setter
    def plot_config(self, value):
        """Geriye dönük uyumluluk: aktif panelin config'ini günceller."""
        self.canvas.get_active_config().update(value)

    @property
    def series_list(self):
        return self.data_manager.series_list

    @series_list.setter
    def series_list(self, value):
        self.data_manager.series_list = value

    # --------------------------------------------------
    # Değişiklik takibi
    # --------------------------------------------------
    def mark_modified(self):
        """Projeyi 'değiştirildi' olarak işaretler."""
        self._is_modified = True

    def _dialog_start_path(self, suggested_name: str = "") -> str:
        base_dir = self._last_dialog_dir if os.path.isdir(self._last_dialog_dir) else os.path.expanduser("~")
        if suggested_name:
            return os.path.join(base_dir, suggested_name)
        return base_dir

    def _remember_dialog_path(self, selected_path: str):
        if not selected_path:
            return
        abs_path = os.path.abspath(selected_path)
        self._last_dialog_dir = abs_path if os.path.isdir(abs_path) else os.path.dirname(abs_path)

    def closeEvent(self, event):
        if self._is_modified:
            reply = QMessageBox.question(
                self,
                t("msg_exit_title"),
                t("msg_exit_text"),
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_project_action()
                # Kayıt başarılıysa _is_modified temizlendi, çık
                if not self._is_modified:
                    event.accept()
                else:
                    event.ignore()   # Kayıt iptal edildi
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # --------------------------------------------------
    # Tema assetleri (SpinBox okları)
    # --------------------------------------------------
    # --------------------------------------------------
    # --------------------------------------------------
    # Tema
    # --------------------------------------------------

    def _switch_language(self, code: str):
        """Dili değiştir ve menü/collapsible başlıklarını güncelle."""
        if code == get_language():
            return
        # Dil değişmeden önce eski varsayılan değerleri sakla
        old_xlabel = t('default_xlabel')
        old_ylabel = t('default_ylabel')

        set_language(code)

        # Panel cfg'lerindeki varsayılan xlabel/ylabel'leri yeni dile güncelle
        # (Kullanıcının değiştirdiği değerlere dokunma)
        new_xlabel = t('default_xlabel')
        new_ylabel = t('default_ylabel')
        for cfg in self.canvas.panel_configs:
            if cfg.get('xlabel', '') == old_xlabel:
                cfg['xlabel'] = new_xlabel
            if cfg.get('ylabel', '') == old_ylabel:
                cfg['ylabel'] = new_ylabel
        self.redraw_plot()

        # Layout seçeneklerini yeni dile göre yenile
        global LAYOUT_OPTIONS
        LAYOUT_OPTIONS = _build_layout_options()
        current_idx = self.combo_layout.currentIndex()
        self.combo_layout.blockSignals(True)
        self.combo_layout.clear()
        for label, _, _ in LAYOUT_OPTIONS:
            self.combo_layout.addItem(label)
        self.combo_layout.setCurrentIndex(current_idx)
        self.combo_layout.blockSignals(False)
        self._retranslate_menu()
        self._retranslate_left_panel()
        self.populate_models()   # Model isim/açıklamalarını dile göre yenile
        # Ayarlar penceresi açıksa sekme başlıklarını güncelle
        if hasattr(self, '_settings_dlg') and self._settings_dlg is not None:
            self._settings_dlg.setWindowTitle(t("dialog_settings_title"))
            self._settings_dlg._reload_for_panel(self._settings_dlg._last_pid)
            # Buton metinlerini de güncelle
            dlg = self._settings_dlg
            dlg._btns.button(QDialogButtonBox.StandardButton.Apply).setText(t("btn_apply"))
            dlg._btns.button(QDialogButtonBox.StandardButton.Close).setText(t("btn_close"))

    # --------------------------------------------------
    # Menü
    # --------------------------------------------------
    def _create_menu(self):
        mb = self.menuBar()
        self._m_file = mb.addMenu(t("menu_file"))
        self._m_view = mb.addMenu(t("menu_view"))
        self._m_plot = mb.addMenu(t("menu_plot"))
        self._m_lang = mb.addMenu(t("menu_language"))

        self.act_open_data = QAction(t("action_load_data"), self)
        self.act_open_data.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open_data.triggered.connect(self.load_data_action)

        self.act_append_cols = QAction(t("action_append_cols"), self)
        self.act_append_cols.triggered.connect(self.append_cols_action)

        self.act_open_proj = QAction(t("action_open_project"), self)
        self.act_open_proj.triggered.connect(self.open_project_action)

        self.act_save_proj = QAction(t("action_save_project"), self)
        self.act_save_proj.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save_proj.triggered.connect(self.save_project_action)

        self.act_save_proj_as = QAction(t("action_save_project_as"), self)
        self.act_save_proj_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_proj_as.triggered.connect(self.save_project_as_action)

        self.act_export = QAction(t("action_export_image"), self)
        self.act_export.triggered.connect(self.save_plot_action)
        self.act_export_table = QAction(t("action_export_table"), self)
        self.act_export_table.triggered.connect(self.export_table_action)

        act_exit = QAction("Çıkış / Exit", self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)

        self._m_file.addAction(self.act_open_data)
        self._m_file.addAction(self.act_append_cols)
        self._m_file.addSeparator()
        self._m_file.addAction(self.act_open_proj)
        self._m_file.addAction(self.act_save_proj)
        self._m_file.addAction(self.act_save_proj_as)
        self._m_file.addSeparator()
        self._m_file.addAction(self.act_export)
        self._m_file.addAction(self.act_export_table)
        self.act_data_ops = QAction(t("action_data_ops"), self)
        self.act_data_ops.triggered.connect(self._open_data_ops)
        self._m_file.addAction(self.act_data_ops)
        self._m_file.addSeparator()
        self.act_export_py = QAction(t("action_export_python"), self)
        self.act_export_py.triggered.connect(self._export_python_action)
        self._m_file.addAction(self.act_export_py)
        self.act_export_nb = QAction(t("action_export_notebook"), self)
        self.act_export_nb.triggered.connect(self._export_notebook_action)
        self._m_file.addAction(self.act_export_nb)
        self._m_file.addSeparator()
        self.act_about = QAction(t("action_about"), self)
        self.act_about.triggered.connect(self._show_about)
        # macOS "About" ile başlayan action'ları uygulama menüsüne taşır
        # NoRole ile bunu engelle — File menüsünde kalır
        self.act_about.setMenuRole(QAction.MenuRole.NoRole)
        self._m_file.addAction(self.act_about)
        self._m_file.addSeparator()
        self._m_file.addAction(act_exit)

        self.act_toggle_theme = QAction(t("action_dark_theme"), self)
        self.act_toggle_theme.setCheckable(True)
        self.act_toggle_theme.setChecked(False)
        self.act_toggle_theme.triggered.connect(self._on_toggle_theme)
        self._m_view.addAction(self.act_toggle_theme)

        self.act_axes = QAction(t("action_axes"), self)
        self.act_axes.triggered.connect(lambda: self.open_settings(t("tab_axes")))

        self.act_general = QAction(t("action_appearance"), self)
        self.act_general.triggered.connect(lambda: self.open_settings(t("tab_appearance")))

        self.act_styles = QAction(t("action_styles"), self)
        self.act_styles.triggered.connect(lambda: self.open_settings(t("tab_styles")))

        self.act_canvas = QAction(t("action_canvas"), self)
        self.act_canvas.triggered.connect(lambda: self.open_settings(t("tab_canvas")))

        self._m_plot.addAction(self.act_axes)
        self._m_plot.addAction(self.act_general)
        self._m_plot.addAction(self.act_styles)
        self._m_plot.addSeparator()
        self._m_plot.addAction(self.act_canvas)

        # Dil seçenekleri
        act_tr = QAction("🇹🇷 Türkçe", self)
        act_tr.triggered.connect(lambda: self._switch_language("tr"))
        act_en = QAction("🇺🇸 English", self)
        act_en.triggered.connect(lambda: self._switch_language("en"))
        self._m_lang.addAction(act_tr)
        self._m_lang.addAction(act_en)
        
    # --------------------------------------------------
    # Collapsible Section yardımcısı
    # --------------------------------------------------
    def _make_collapsible(self, title: str, content_widget: QWidget,
                          collapsed: bool = False) -> QWidget:
        """
        Başlık çubuğuna tıklanınca içeriği gösteren/gizleyen
        hafif collapsible bileşen döndürür.
        """
        wrapper = QWidget()
        vlay = QVBoxLayout(wrapper)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(0)

        btn = QToolButton()
        btn.setText(f"  {title}")
        btn.setCheckable(True)
        btn.setChecked(not collapsed)
        btn.setArrowType(Qt.ArrowType.DownArrow if not collapsed else Qt.ArrowType.RightArrow)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setStyleSheet(
            "QToolButton { font-weight: 600; font-size: 12px; border: none; border-radius: 0px; "
            "padding: 6px 4px; text-align: left; }"
        )

        content_widget.setVisible(not collapsed)

        def toggle(checked):
            content_widget.setVisible(checked)
            btn.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)

        btn.toggled.connect(toggle)

        vlay.addWidget(btn)
        vlay.addWidget(content_widget)
        return wrapper, btn

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def setup_ui_components(self):
        w = QWidget()
        self.setCentralWidget(w)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(0)

        # Ana splitter: sol panel | sağ içerik
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter.setChildrenCollapsible(False)
        lay.addWidget(self._main_splitter)

        # SOL PANEL
        left_container = QWidget()
        left_container.setMinimumWidth(260)
        left_outer = QVBoxLayout(left_container)
        left_outer.setContentsMargins(0, 0, 0, 0)
        left_outer.setSpacing(0)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        left_scroll.setFrameShape(left_scroll.Shape.NoFrame)
        left_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        left_inner = QWidget()
        left = QVBoxLayout(left_inner)
        left.setContentsMargins(4, 4, 4, 4)
        left.setSpacing(4)

        left_scroll.setWidget(left_inner)
        left_outer.addWidget(left_scroll)
        self._main_splitter.addWidget(left_container)

        # Başlangıç genişliği — ekrana göre
        try:
            geo = self.screen().availableGeometry()
            panel_w = max(300, min(380, int(geo.width() * 0.24)))
        except Exception:
            panel_w = 320

        # ==========================================
        # PANELLER — kritik, her zaman açık
        # ==========================================
        g_panels_w = QWidget()
        lp = QVBoxLayout(g_panels_w)
        lp.setContentsMargins(4, 4, 4, 4)
        lp.setSpacing(4)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(4)
        h_layout.addWidget(QLabel("Layout:"))
        self.combo_layout = QComboBox()
        for label, _, _ in LAYOUT_OPTIONS:
            self.combo_layout.addItem(label)
        self.combo_layout.setCurrentIndex(0)
        self.combo_layout.currentIndexChanged.connect(self._on_layout_changed)
        h_layout.addWidget(self.combo_layout, 1)
        lp.addLayout(h_layout)

        self.lst_panels = QListWidget()
        self.lst_panels.setMaximumHeight(150)
        self.lst_panels.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        lp.addWidget(self.lst_panels)

        self.lbl_active_panel = QLabel("Active: Ax1 | Layout: 1×1")
        self.lbl_active_panel.setStyleSheet("font-size: 10px; color: gray;")
        lp.addWidget(self.lbl_active_panel)

        h_panel_btns = QHBoxLayout()
        h_panel_btns.setSpacing(4)
        self._btn_rename_panel = QPushButton(t("btn_rename_panel"))
        self._btn_rename_panel.setProperty("variant", "neutral")
        self._btn_rename_panel.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_rename_panel.clicked.connect(self._rename_panel_action)
        self._btn_clear_panel = QPushButton(t("btn_clear_panel"))
        self._btn_clear_panel.setProperty("variant", "danger")
        self._btn_clear_panel.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear_panel.clicked.connect(self._clear_panel_action)
        h_panel_btns.addWidget(self._btn_rename_panel)
        h_panel_btns.addWidget(self._btn_clear_panel)
        lp.addLayout(h_panel_btns)

        panels_section, self._btn_panels = self._make_collapsible(t("section_panels"), g_panels_w, collapsed=False)
        left.addWidget(panels_section)
        self.lst_panels.currentRowChanged.connect(self._on_panel_selection_changed)

        # ==========================================
        # KATMANLAR — manuel ekleme kaldırıldı, sadece liste yönetimi
        # ==========================================
        g2_w = QWidget()
        l2s = QVBoxLayout(g2_w)
        l2s.setContentsMargins(4, 4, 4, 4)
        l2s.setSpacing(4)

        # Legacy kontroller (UI'da gösterilmiyor, geriye dönük uyumluluk için tutuluyor)
        self._lbl_ptype = QLabel(t("label_plot_type"))
        self.combo_plot_type = QComboBox()
        self.combo_plot_type.addItems([
            t("plot_type_scatter"),
            t("plot_type_line"),
            t("plot_type_scatter_line"),
            t("plot_type_bar"),
            t("plot_type_histogram"),
        ])
        self.combo_plot_type.currentIndexChanged.connect(self._on_plot_type_changed_with_sync)

        self.combo_x = QComboBox()
        self.combo_x_err = QComboBox()
        self.combo_y_err = QComboBox()
        self.combo_x_err.addItem("Yok")
        self.combo_y_err.addItem("Yok")

        # Y sütunu — çoklu seçim destekli liste
        self.lst_y_select = QListWidget()
        self.lst_y_select.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.lst_y_select.setMaximumHeight(1)
        self.lst_y_select.setToolTip(t("tooltip_y_select"))
        self.lst_y_select.itemSelectionChanged.connect(self._on_y_selection_changed)

        self._lbl_x  = QLabel(t("label_x_col"))
        self._lbl_xe = QLabel(t("label_x_err"))
        self._lbl_xe.setStyleSheet("color: gray; font-size: 10px;")
        self._lbl_ye = QLabel(t("label_y_err"))
        self._lbl_ye.setStyleSheet("color: gray; font-size: 10px;")

        # combo_y uyumluluk için (mevcut kodun combo_y.currentText() çağrıları)
        self.combo_y = QComboBox()
        self.combo_y.setVisible(False)

        self.inp_series_label = QLineEdit()
        self.inp_series_label.setPlaceholderText(t("placeholder_series_label"))
        self.inp_series_label.setVisible(False)

        h_list_header = QHBoxLayout()
        self._lbl_layers = QLabel(t("label_layers"))
        h_list_header.addWidget(self._lbl_layers)
        h_list_header.addStretch()
        self._btn_del = QPushButton(t("btn_delete"))
        self._btn_del.setMaximumWidth(64)
        self._btn_del.setProperty("variant", "danger")
        self._btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_del.clicked.connect(self.remove_series_action)
        h_list_header.addWidget(self._btn_del)
        l2s.addLayout(h_list_header)

        self.lst_ser = QListWidget()
        self.lst_ser.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.lst_ser.setMaximumHeight(220)
        l2s.addWidget(self.lst_ser)
        self.lst_ser.itemDoubleClicked.connect(self.rename_series_action)

        katman_section, self._btn_layers = self._make_collapsible(t("section_layers"), g2_w, collapsed=False)
        left.addWidget(katman_section)

        # ==========================================
        # METİN YÖNETİMİ
        # ==========================================
        g_text_w = QWidget()
        lt = QVBoxLayout(g_text_w)
        lt.setContentsMargins(4, 4, 4, 4)
        lt.setSpacing(4)

        self.lst_text_items = QListWidget()
        self.lst_text_items.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.lst_text_items.setMaximumHeight(120)
        self.lst_text_items.currentRowChanged.connect(self._on_text_item_selected)
        lt.addWidget(self.lst_text_items)

        h_text = QHBoxLayout()
        h_text.setSpacing(4)
        self.inp_text_item = QLineEdit()
        self.inp_text_item.setPlaceholderText(t("placeholder_text_item"))
        self.btn_text_symbol = QPushButton("Ω")
        self.btn_text_symbol.setFixedWidth(28)
        self.btn_text_symbol.setToolTip(t("tip_symbol_palette"))
        self.btn_text_symbol.clicked.connect(lambda: self._open_symbol_palette(self.inp_text_item))
        h_text.addWidget(self.inp_text_item, 1)
        h_text.addWidget(self.btn_text_symbol)
        lt.addLayout(h_text)

        h_mode = QHBoxLayout()
        h_mode.setSpacing(4)
        self._lbl_text_coord_mode = QLabel(t("lbl_text_coord_mode"))
        h_mode.addWidget(self._lbl_text_coord_mode)
        self.combo_text_coord = QComboBox()
        self.combo_text_coord.addItem(t("text_coord_axes"), "axes")
        self.combo_text_coord.addItem(t("text_coord_data"), "data")
        h_mode.addWidget(self.combo_text_coord, 1)
        self.combo_text_preset = QComboBox()
        h_mode.addWidget(self.combo_text_preset, 1)
        lt.addLayout(h_mode)

        h_xy = QHBoxLayout()
        h_xy.setSpacing(4)
        self._lbl_text_x = QLabel("X")
        h_xy.addWidget(self._lbl_text_x)
        self.spin_text_x = EmojiDoubleSpinBox(minimum=-1e6, maximum=1e6, value=0.02, step=0.01, decimals=4)
        h_xy.addWidget(self.spin_text_x, 1)
        self._lbl_text_y = QLabel("Y")
        h_xy.addWidget(self._lbl_text_y)
        self.spin_text_y = EmojiDoubleSpinBox(minimum=-1e6, maximum=1e6, value=0.98, step=0.01, decimals=4)
        h_xy.addWidget(self.spin_text_y, 1)
        lt.addLayout(h_xy)

        h_style = QHBoxLayout()
        h_style.setSpacing(4)
        self._lbl_text_align = QLabel(t("lbl_text_align"))
        h_style.addWidget(self._lbl_text_align)
        self.combo_text_ha = QComboBox()
        self.combo_text_ha.addItem(t("align_left"), "left")
        self.combo_text_ha.addItem(t("align_center"), "center")
        self.combo_text_ha.addItem(t("align_right"), "right")
        self.combo_text_va = QComboBox()
        self.combo_text_va.addItem(t("align_top"), "top")
        self.combo_text_va.addItem(t("align_center"), "center")
        self.combo_text_va.addItem(t("align_bottom"), "bottom")
        h_style.addWidget(self.combo_text_ha, 1)
        h_style.addWidget(self.combo_text_va, 1)
        self.spin_text_size = EmojiSpinBox(minimum=6, maximum=48, value=11, step=1)
        h_style.addWidget(self.spin_text_size)
        lt.addLayout(h_style)

        h_font = QHBoxLayout()
        h_font.setSpacing(4)
        self._lbl_text_font = QLabel(t("lbl_text_font"))
        h_font.addWidget(self._lbl_text_font)
        self.combo_text_font = QComboBox()
        self.combo_text_font.setEditable(True)
        self.combo_text_font.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        h_font.addWidget(self.combo_text_font, 1)
        self._lbl_text_angle = QLabel(t("lbl_text_angle"))
        h_font.addWidget(self._lbl_text_angle)
        self.spin_text_rotation = EmojiSpinBox(minimum=-360, maximum=360, value=0, step=1)
        h_font.addWidget(self.spin_text_rotation)
        lt.addLayout(h_font)

        h_flags = QHBoxLayout()
        h_flags.setSpacing(8)
        self.chk_text_bold = QCheckBox(t("chk_bold"))
        self.chk_text_italic = QCheckBox(t("chk_italic"))
        self.chk_text_math = QCheckBox(t("chk_math_mode"))
        h_flags.addWidget(self.chk_text_bold)
        h_flags.addWidget(self.chk_text_italic)
        h_flags.addWidget(self.chk_text_math)
        h_flags.addStretch(1)
        lt.addLayout(h_flags)

        h_text_btns = QHBoxLayout()
        h_text_btns.setSpacing(4)
        self.btn_text_add = QPushButton(t("btn_text_add"))
        self.btn_text_add.setProperty("variant", "success")
        self.btn_text_add.clicked.connect(self._add_text_item)
        self.btn_text_update = QPushButton(t("btn_text_update"))
        self.btn_text_update.setProperty("variant", "neutral")
        self.btn_text_update.clicked.connect(self._update_text_item)
        self.btn_text_delete = QPushButton(t("btn_text_delete"))
        self.btn_text_delete.setProperty("variant", "danger")
        self.btn_text_delete.clicked.connect(self._delete_text_item)
        h_text_btns.addWidget(self.btn_text_add)
        h_text_btns.addWidget(self.btn_text_update)
        h_text_btns.addWidget(self.btn_text_delete)
        lt.addLayout(h_text_btns)

        self.grp_auto_panel_labels = QGroupBox(t("grp_auto_panel_labels"))
        gl_auto = QGridLayout()
        gl_auto.setHorizontalSpacing(6)
        gl_auto.setVerticalSpacing(4)

        self.chk_auto_panel_labels = QCheckBox(t("chk_auto_panel_labels"))
        self.combo_auto_label_style = QComboBox()
        self.combo_auto_label_preset = QComboBox()
        self.combo_auto_label_ha = QComboBox()
        self.combo_auto_label_ha.addItem(t("align_left"), "left")
        self.combo_auto_label_ha.addItem(t("align_center"), "center")
        self.combo_auto_label_ha.addItem(t("align_right"), "right")
        self.combo_auto_label_va = QComboBox()
        self.combo_auto_label_va.addItem(t("align_top"), "top")
        self.combo_auto_label_va.addItem(t("align_center"), "center")
        self.combo_auto_label_va.addItem(t("align_bottom"), "bottom")
        self.spin_auto_label_x = EmojiDoubleSpinBox(minimum=-1.0, maximum=2.0, value=0.02, step=0.01, decimals=3)
        self.spin_auto_label_y = EmojiDoubleSpinBox(minimum=-1.0, maximum=2.0, value=0.98, step=0.01, decimals=3)
        self.spin_auto_label_size = EmojiSpinBox(minimum=6, maximum=48, value=11, step=1)
        self.chk_auto_label_bold = QCheckBox(t("chk_bold"))
        self.chk_auto_label_italic = QCheckBox(t("chk_italic"))

        gl_auto.addWidget(self.chk_auto_panel_labels, 0, 0, 1, 2)
        gl_auto.addWidget(self.combo_auto_label_style, 0, 2, 1, 2)
        gl_auto.addWidget(self.combo_auto_label_preset, 1, 0, 1, 2)
        gl_auto.addWidget(self.spin_auto_label_x, 1, 2)
        gl_auto.addWidget(self.spin_auto_label_y, 1, 3)
        gl_auto.addWidget(self.combo_auto_label_ha, 2, 0)
        gl_auto.addWidget(self.combo_auto_label_va, 2, 1)
        gl_auto.addWidget(self.spin_auto_label_size, 2, 2)
        h_auto_flags = QHBoxLayout()
        h_auto_flags.setSpacing(6)
        h_auto_flags.addWidget(self.chk_auto_label_bold)
        h_auto_flags.addWidget(self.chk_auto_label_italic)
        h_auto_flags.addStretch(1)
        gl_auto.addLayout(h_auto_flags, 2, 3)
        self.grp_auto_panel_labels.setLayout(gl_auto)
        lt.addWidget(self.grp_auto_panel_labels)

        self._populate_text_preset_combo()
        self._populate_text_font_combo()
        self._populate_auto_label_style_combo()
        self._populate_auto_label_preset_combo()
        self.combo_text_preset.currentIndexChanged.connect(self._apply_selected_text_preset)
        self.combo_auto_label_preset.currentIndexChanged.connect(self._apply_auto_label_preset)
        self._load_auto_label_controls()

        for wdg, sig_name in (
            (self.chk_auto_panel_labels, "toggled"),
            (self.combo_auto_label_style, "currentIndexChanged"),
            (self.combo_auto_label_ha, "currentIndexChanged"),
            (self.combo_auto_label_va, "currentIndexChanged"),
            (self.spin_auto_label_x, "valueChanged"),
            (self.spin_auto_label_y, "valueChanged"),
            (self.spin_auto_label_size, "valueChanged"),
            (self.chk_auto_label_bold, "toggled"),
            (self.chk_auto_label_italic, "toggled"),
        ):
            getattr(wdg, sig_name).connect(self._on_auto_label_settings_changed)

        texts_section, self._btn_texts = self._make_collapsible(t("section_texts"), g_text_w, collapsed=True)
        left.addWidget(texts_section)
        self._refresh_text_list()

        # ==========================================
        g3_w = QWidget()
        l3 = QVBoxLayout(g3_w)
        l3.setContentsMargins(4, 4, 4, 4)
        l3.setSpacing(4)

        h_model_fit = QHBoxLayout()
        h_model_fit.setSpacing(4)
        self.combo_mod = QComboBox()
        self._btn_fit_run = QPushButton(t("btn_fit"))
        self._btn_fit_run.setProperty("variant", "info")
        self._btn_fit_run.setMaximumWidth(64)
        self._btn_fit_run.clicked.connect(self.perform_fit)
        h_model_fit.addWidget(self.combo_mod, 1)
        h_model_fit.addWidget(self._btn_fit_run)
        l3.addLayout(h_model_fit)

        h_fit_header = QHBoxLayout()
        self._lbl_fits = QLabel(t("label_fits"))
        h_fit_header.addWidget(self._lbl_fits)
        h_fit_header.addStretch()
        self._btn_del_fit = QPushButton(t("btn_delete_fit"))
        self._btn_del_fit.setMaximumWidth(64)
        self._btn_del_fit.setProperty("variant", "neutral")
        self._btn_del_fit.clicked.connect(self.remove_fit_action)
        h_fit_header.addWidget(self._btn_del_fit)
        l3.addLayout(h_fit_header)

        self.lst_fits = QListWidget()
        self.lst_fits.setMaximumHeight(72)
        l3.addWidget(self.lst_fits)
        self.lst_fits.itemDoubleClicked.connect(self.rename_fit_action)
        self.lst_fits.currentRowChanged.connect(self.on_fit_selection_changed)

        fit_section, self._btn_fit = self._make_collapsible(t("section_fit"), g3_w, collapsed=True)
        left.addWidget(fit_section)
        left.addWidget(fit_section)

        left.addStretch(1)

        # ==========================================
        # SAĞ PANEL: Sekmeler
        # ==========================================
        self._tabs = tabs = QTabWidget()

        self.plot_w = QWidget()
        pl = QVBoxLayout(self.plot_w)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas = MplCanvas(self)
        self.canvas.dblclick_callback = self._on_canvas_panel_dblclick
        self.scroll_area.setWidget(self.canvas)
        pl.addWidget(self.scroll_area)

        self.table_w = QTableWidget()
        self.table_w.itemChanged.connect(self.update_from_table)
        self.table_w.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_w.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        header = self.table_w.horizontalHeader()
        header.sectionDoubleClicked.connect(self._cycle_table_column_role)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_column_role_menu)
        header.setToolTip(t("table_role_hint"))
        header.setFixedHeight(44)
        header.sectionResized.connect(lambda *_: self._sync_role_row_layout())
        header.sectionMoved.connect(lambda *_: self._sync_role_row_layout())
        self.table_w.installEventFilter(self)
        self.table_w.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_w.customContextMenuRequested.connect(self._show_table_context_menu)

        table_tab = QWidget()
        table_tab_lay = QVBoxLayout(table_tab)
        table_tab_lay.setContentsMargins(6, 6, 6, 6)
        table_tab_lay.setSpacing(6)
        plot_lbl_w = 30
        self.btn_table_undo = QPushButton(t("btn_table_undo_last"))
        self.btn_table_undo.setProperty("variant", "neutral")
        self.btn_table_undo.setEnabled(False)
        self.btn_table_undo.clicked.connect(self._undo_last_table_action)

        table_role_row = QHBoxLayout()
        table_role_row.setSpacing(6)
        self.combo_role_template = QComboBox()
        self._populate_role_template_combo()
        self.combo_role_template.currentIndexChanged.connect(self._apply_role_template_from_combo)
        self.lbl_table_plot_type = QLabel(t("label_plot_type"))
        self.combo_table_plot_type = QComboBox()
        self.combo_table_plot_type.addItems([
            t("plot_type_scatter"),
            t("plot_type_line"),
            t("plot_type_scatter_line"),
            t("plot_type_bar"),
            t("plot_type_histogram"),
        ])
        self.combo_table_plot_type.currentIndexChanged.connect(self._on_table_plot_type_changed)
        self.btn_reset_roles = QPushButton(t("btn_reset_roles"))
        self.btn_reset_roles.setProperty("variant", "danger")
        self.btn_reset_roles.setStyleSheet("QPushButton { border-bottom-width: 1px; padding: 6px 10px; }")
        self.btn_reset_roles.clicked.connect(self._reset_all_column_roles)
        self.btn_add_from_roles = QPushButton(t("btn_add_from_roles"))
        self.btn_add_from_roles.setProperty("variant", "success")
        self.btn_add_from_roles.setStyleSheet("QPushButton { border-bottom-width: 1px; padding: 6px 10px; }")
        self.btn_add_from_roles.clicked.connect(self._add_series_from_roles)
        self.lbl_table_plot_type.setFixedWidth(plot_lbl_w)
        self.lbl_table_plot_type.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        table_role_row.addWidget(self.combo_role_template)
        table_role_row.addWidget(self.btn_reset_roles)
        table_role_row.addWidget(self.lbl_table_plot_type)
        table_role_row.addWidget(self.combo_table_plot_type)
        table_role_row.addWidget(self.btn_add_from_roles)
        table_role_row.addStretch(1)
        table_role_row.addWidget(self.btn_table_undo)
        table_tab_lay.addLayout(table_role_row)

        role_row_wrap = QHBoxLayout()
        role_row_wrap.setContentsMargins(0, 0, 0, 0)
        role_row_wrap.setSpacing(0)
        self.role_left_pad = QWidget()
        self.role_left_pad.setFixedWidth(0)
        role_row_wrap.addWidget(self.role_left_pad)

        self.role_select_scroll = QScrollArea()
        self.role_select_scroll.setWidgetResizable(False)
        self.role_select_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.role_select_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.role_select_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.role_select_scroll.setStyleSheet("QScrollArea { margin: 0px; padding: 0px; border: 0px; }")
        self.role_select_scroll.setMaximumHeight(54)
        self.role_select_scroll.setMinimumHeight(54)
        self.role_select_host = QWidget()
        self.role_select_layout = QHBoxLayout(self.role_select_host)
        self.role_select_layout.setContentsMargins(0, 0, 0, 0)
        self.role_select_layout.setSpacing(0)
        self.role_select_scroll.setWidget(self.role_select_host)
        self.role_select_scroll.horizontalScrollBar().valueChanged.connect(self._sync_table_scroll_from_role)
        self.table_w.horizontalScrollBar().valueChanged.connect(self._sync_role_scroll_from_table)
        role_row_wrap.addWidget(self.role_select_scroll, 1)
        self.role_row_widget = QWidget()
        self.role_row_widget.setLayout(role_row_wrap)
        table_tab_lay.addWidget(self.role_row_widget)
        # Rol seçimi artık sağ tık menü üzerinden; dropdown satırı gizli.
        self.role_row_widget.setVisible(False)
        table_tab_lay.addWidget(self.table_w, 1)

        tabs.addTab(table_tab, t("tab_table"))
        tabs.addTab(self.plot_w, t("tab_plot"))

        # --- Analiz Raporu sekmesi ---
        self.report_w = QWidget()
        report_layout = QHBoxLayout(self.report_w)
        report_layout.setContentsMargins(6, 6, 6, 6)
        report_layout.setSpacing(8)

        # Sol: Fit listesi + Kopyala butonu
        left_report = QVBoxLayout()
        left_report.addWidget(QLabel(t("label_fits_list")))
        self.lst_report_fits = QListWidget()
        self.lst_report_fits.setMinimumWidth(190)
        self.lst_report_fits.setMaximumWidth(240)
        self.lst_report_fits.currentRowChanged.connect(self._on_report_fit_selected)
        left_report.addWidget(self.lst_report_fits)

        self.btn_copy_report = QPushButton(t("btn_copy_report"))
        self.btn_copy_report.setProperty("variant", "neutral")
        self.btn_copy_report.clicked.connect(self._copy_report_to_clipboard)
        left_report.addWidget(self.btn_copy_report)

        self.lbl_copy_status = QLabel("")
        self.lbl_copy_status.setStyleSheet("font-size: 10px; color: gray;")
        self.lbl_copy_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_copy_status.setFixedHeight(18)
        left_report.addWidget(self.lbl_copy_status)
        report_layout.addLayout(left_report)

        # Sağ: Bilgi kutusu (üst) + Residual grafiği (alt)
        right_report = QVBoxLayout()

        self.report_info = QPlainTextEdit()
        self.report_info.setReadOnly(True)
        self.report_info.setMaximumHeight(220)
        self.report_info.setPlaceholderText(t("report_placeholder"))
        font = self.report_info.font()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.report_info.setFont(font)
        right_report.addWidget(self.report_info)

        self.resid_canvas = MplCanvas(self)
        right_report.addWidget(self.resid_canvas, 1)

        report_layout.addLayout(right_report, 1)

        tabs.addTab(self.report_w, t("tab_report"))
        tabs.setCurrentIndex(0)

        self._main_splitter.addWidget(tabs)

        # Başlangıç boyutları: sol panel | sağ içerik
        self._main_splitter.setSizes([panel_w, 9999])
        self._main_splitter.setStretchFactor(0, 0)   # sol panel esnemez
        self._main_splitter.setStretchFactor(1, 1)   # sağ alan tüm boşluğu alır

        # İlk panel listesini doldur
        self._refresh_panel_list()

    # --------------------------------------------------
    # Panel Yönetimi
    # --------------------------------------------------
    def _refresh_panel_list(self):
        """Panel listesini canvas durumuna göre yeniden oluşturur."""
        self.lst_panels.blockSignals(True)
        self.lst_panels.clear()
        active = self.canvas.active_index
        for i, name in enumerate(self.canvas.panel_names):
            self.lst_panels.addItem(name)
            item = self.lst_panels.item(i)
            if i == active:
                f = item.font()
                f.setBold(True)
                item.setFont(f)
        self.lst_panels.setCurrentRow(active)
        self.lst_panels.blockSignals(False)
        self._update_active_label()

    def _update_active_label(self):
        rows = self.canvas._layout_rows
        cols = self.canvas._layout_cols
        name = self.canvas.panel_names[self.canvas.active_index]
        self.lbl_active_panel.setText(
            f"Active: {name} | Layout: {rows}×{cols}"
        )

    def _reset_theme_cycle(self, theme_name: str = None):
        """Döngüyü başa al."""
        _reset_color_cycle(theme_name)

    def _apply_color_theme(self, theme_name: str):
        """Aktif panelin serilerine temayı sırayla uygula — renk + sembol."""
        from src.ui.color_themes import MARKER_SEQUENCE
        colors  = COLOR_THEMES.get(theme_name, COLOR_THEMES["Classic"])
        pid     = self.canvas.active_index
        series  = self.data_manager.get_series_for_panel(pid)

        for i, s in enumerate(series):
            s['color'] = colors[i % len(colors)]
            pt = s.get('plot_type', 'scatter')
            if pt == 'scatter':
                # Renk + sembol
                s['marker'] = MARKER_SEQUENCE[i % len(MARKER_SEQUENCE)]
                # Çizgi tipi değiştirilmez — kullanıcı ayarına bırak
            # Line ve bar için sadece renk, sembol/çizgi dokunulmaz

        _reset_color_cycle(theme_name)
        self.mark_modified()
        self.redraw_plot()

    def _on_panel_selection_changed(self, row: int):
        if row < 0 or row >= self.canvas.panel_count:
            return
        old_active = self.canvas.active_index
        self.canvas.set_active(row)

        # Eski aktif item'ı normal yap
        old_item = self.lst_panels.item(old_active)
        if old_item:
            f = old_item.font()
            f.setBold(False)
            old_item.setFont(f)

        # Yeni aktif item'ı bold yap
        new_item = self.lst_panels.item(row)
        if new_item:
            f = new_item.font()
            f.setBold(True)
            new_item.setFont(f)

        self._update_active_label()
        # Aktif panel'in serilerini göster
        self._refresh_series_list()
        self._refresh_text_list()

    def _refresh_series_list(self):
        """Aktif panelin serilerini lst_ser'e yükler."""
        self.lst_ser.clear()
        pid = self.canvas.active_index
        for s in self.data_manager.get_series_for_panel(pid):
            self.lst_ser.addItem(s['label'])

    # --------------------------------------------------
    # Metin Yönetimi
    # --------------------------------------------------
    def _text_preset_options(self) -> list[tuple[str, str]]:
        return [
            ("custom", t("text_preset_custom")),
            ("top_left", t("text_preset_top_left")),
            ("top_center", t("text_preset_top_center")),
            ("top_right", t("text_preset_top_right")),
            ("center_left", t("text_preset_center_left")),
            ("center", t("text_preset_center")),
            ("center_right", t("text_preset_center_right")),
            ("bottom_left", t("text_preset_bottom_left")),
            ("bottom_center", t("text_preset_bottom_center")),
            ("bottom_right", t("text_preset_bottom_right")),
        ]

    def _auto_label_style_options(self) -> list[tuple[str, str]]:
        return [
            ("lower_rparen", t("auto_label_style_lower_rparen")),
            ("lower_paren", t("auto_label_style_lower_paren")),
            ("lower", t("auto_label_style_lower")),
            ("upper_rparen", t("auto_label_style_upper_rparen")),
            ("upper_paren", t("auto_label_style_upper_paren")),
            ("upper", t("auto_label_style_upper")),
            ("num_rparen", t("auto_label_style_num_rparen")),
            ("num_paren", t("auto_label_style_num_paren")),
            ("num", t("auto_label_style_num")),
        ]

    def _text_font_options(self) -> list[tuple[str, str]]:
        return [
            ("", t("text_font_default")),
            ("Times New Roman", "Times New Roman"),
            ("Arial", "Arial"),
            ("Helvetica", "Helvetica"),
            ("Calibri", "Calibri"),
            ("Cambria", "Cambria"),
            ("Georgia", "Georgia"),
            ("DejaVu Sans", "DejaVu Sans"),
            ("DejaVu Serif", "DejaVu Serif"),
            ("Courier New", "Courier New"),
        ]

    def _populate_text_font_combo(self):
        if not hasattr(self, "combo_text_font"):
            return
        current_data = str(self.combo_text_font.currentData() or "").strip()
        current_text = (self.combo_text_font.currentText() or "").strip()

        self.combo_text_font.blockSignals(True)
        self.combo_text_font.clear()
        for key, label in self._text_font_options():
            self.combo_text_font.addItem(label, key)

        if current_data:
            idx = self.combo_text_font.findData(current_data)
            if idx >= 0:
                self.combo_text_font.setCurrentIndex(idx)
            else:
                self.combo_text_font.setEditText(current_data)
        else:
            idx = self.combo_text_font.findData("")
            self.combo_text_font.setCurrentIndex(idx if idx >= 0 else 0)
            if current_text and current_text != t("text_font_default"):
                self.combo_text_font.setEditText(current_text)
        self.combo_text_font.blockSignals(False)

    def _selected_text_font(self) -> str:
        if not hasattr(self, "combo_text_font"):
            return ""
        data_val = str(self.combo_text_font.currentData() or "").strip()
        if data_val:
            return data_val
        txt_val = (self.combo_text_font.currentText() or "").strip()
        if txt_val and txt_val != t("text_font_default"):
            return txt_val
        return ""

    def _populate_text_preset_combo(self):
        if not hasattr(self, "combo_text_preset"):
            return
        self.combo_text_preset.blockSignals(True)
        self.combo_text_preset.clear()
        for key, label in self._text_preset_options():
            self.combo_text_preset.addItem(label, key)
        self.combo_text_preset.setCurrentIndex(0)
        self.combo_text_preset.blockSignals(False)

    def _populate_auto_label_style_combo(self):
        if not hasattr(self, "combo_auto_label_style"):
            return
        current = self.text_auto_cfg.get("style", "lower_rparen")
        self.combo_auto_label_style.blockSignals(True)
        self.combo_auto_label_style.clear()
        for key, label in self._auto_label_style_options():
            self.combo_auto_label_style.addItem(label, key)
        idx = self.combo_auto_label_style.findData(current)
        self.combo_auto_label_style.setCurrentIndex(idx if idx >= 0 else 0)
        self.combo_auto_label_style.blockSignals(False)

    def _populate_auto_label_preset_combo(self):
        if not hasattr(self, "combo_auto_label_preset"):
            return
        self.combo_auto_label_preset.blockSignals(True)
        self.combo_auto_label_preset.clear()
        for key, label in self._text_preset_options():
            self.combo_auto_label_preset.addItem(label, key)
        self.combo_auto_label_preset.setCurrentIndex(0)
        self.combo_auto_label_preset.blockSignals(False)

    def _next_text_id(self) -> int:
        tid = self._next_text_item_id
        self._next_text_item_id += 1
        return tid

    def _panel_text_items(self, panel_id: int) -> list[dict]:
        return [it for it in self.text_items if it.get("panel_id", 0) == panel_id]

    def _refresh_text_list(self):
        if not hasattr(self, "lst_text_items"):
            return
        if not hasattr(self, "canvas"):
            self.lst_text_items.clear()
            self._clear_text_editor_fields()
            return
        self.lst_text_items.blockSignals(True)
        self.lst_text_items.clear()
        pid = self.canvas.active_index
        for it in self._panel_text_items(pid):
            txt = str(it.get("text", "")).replace("\n", " ").strip()
            short = txt if len(txt) <= 34 else (txt[:31] + "...")
            label = f"#{it.get('id', 0)}  {short}"
            row = QListWidgetItem(label)
            row.setData(Qt.ItemDataRole.UserRole, int(it.get("id", 0)))
            self.lst_text_items.addItem(row)
        self.lst_text_items.blockSignals(False)
        if self.lst_text_items.count() > 0:
            self.lst_text_items.setCurrentRow(0)
        else:
            self._clear_text_editor_fields()

    def _clear_text_editor_fields(self):
        if not hasattr(self, "inp_text_item"):
            return
        self.inp_text_item.clear()
        self.combo_text_coord.setCurrentIndex(0)
        self.combo_text_preset.setCurrentIndex(0)
        self.spin_text_x.setValue(0.02)
        self.spin_text_y.setValue(0.98)
        self.combo_text_ha.setCurrentIndex(0)
        self.combo_text_va.setCurrentIndex(0)
        self.spin_text_size.setValue(11)
        idx_font = self.combo_text_font.findData("")
        self.combo_text_font.setCurrentIndex(idx_font if idx_font >= 0 else 0)
        self.spin_text_rotation.setValue(0)
        self.chk_text_bold.setChecked(False)
        self.chk_text_italic.setChecked(False)
        self.chk_text_math.setChecked(False)

    def _selected_text_item(self) -> dict | None:
        if not hasattr(self, "lst_text_items"):
            return None
        row_item = self.lst_text_items.currentItem()
        if row_item is None:
            return None
        tid = int(row_item.data(Qt.ItemDataRole.UserRole) or 0)
        for it in self.text_items:
            if int(it.get("id", -1)) == tid:
                return it
        return None

    def _on_text_item_selected(self, row: int):
        if row < 0:
            self._clear_text_editor_fields()
            return
        it = self._selected_text_item()
        if not it:
            self._clear_text_editor_fields()
            return
        self.inp_text_item.setText(str(it.get("text", "")))
        mode = str(it.get("coord_mode", "axes"))
        idx_mode = self.combo_text_coord.findData(mode)
        self.combo_text_coord.setCurrentIndex(idx_mode if idx_mode >= 0 else 0)
        self.spin_text_x.setValue(float(it.get("x", 0.02)))
        self.spin_text_y.setValue(float(it.get("y", 0.98)))
        idx_ha = self.combo_text_ha.findData(str(it.get("ha", "left")))
        self.combo_text_ha.setCurrentIndex(idx_ha if idx_ha >= 0 else 0)
        idx_va = self.combo_text_va.findData(str(it.get("va", "top")))
        self.combo_text_va.setCurrentIndex(idx_va if idx_va >= 0 else 0)
        self.spin_text_size.setValue(int(it.get("fontsize", 11)))
        text_font = str(it.get("fontfamily", "") or "").strip()
        if text_font:
            idx_font = self.combo_text_font.findData(text_font)
            if idx_font >= 0:
                self.combo_text_font.setCurrentIndex(idx_font)
            else:
                self.combo_text_font.setEditText(text_font)
        else:
            idx_font = self.combo_text_font.findData("")
            self.combo_text_font.setCurrentIndex(idx_font if idx_font >= 0 else 0)
        self.spin_text_rotation.setValue(int(round(float(it.get("rotation", 0.0)))))
        self.chk_text_bold.setChecked(bool(it.get("bold", False)))
        self.chk_text_italic.setChecked(bool(it.get("italic", False)))
        self.chk_text_math.setChecked(bool(it.get("math_mode", False)))
        self.combo_text_preset.setCurrentIndex(0)

    def _apply_selected_text_preset(self, _idx: int):
        if not hasattr(self, "combo_text_preset"):
            return
        key = str(self.combo_text_preset.currentData() or "custom")
        if key == "custom":
            return
        x, y, ha, va = get_text_preset(key)
        self.combo_text_coord.setCurrentIndex(self.combo_text_coord.findData("axes"))
        self.spin_text_x.setValue(x)
        self.spin_text_y.setValue(y)
        i_ha = self.combo_text_ha.findData(ha)
        if i_ha >= 0:
            self.combo_text_ha.setCurrentIndex(i_ha)
        i_va = self.combo_text_va.findData(va)
        if i_va >= 0:
            self.combo_text_va.setCurrentIndex(i_va)

    def _add_text_item(self):
        text_val = (self.inp_text_item.text() or "").strip()
        if not text_val:
            QMessageBox.information(self, t("msg_warning"), t("msg_text_empty"))
            return
        item = {
            "id": self._next_text_id(),
            "panel_id": int(self.canvas.active_index),
            "text": text_val,
            "coord_mode": str(self.combo_text_coord.currentData() or "axes"),
            "x": float(self.spin_text_x.value()),
            "y": float(self.spin_text_y.value()),
            "ha": str(self.combo_text_ha.currentData() or "left"),
            "va": str(self.combo_text_va.currentData() or "top"),
            "fontsize": int(self.spin_text_size.value()),
            "fontfamily": self._selected_text_font(),
            "rotation": float(self.spin_text_rotation.value()),
            "bold": bool(self.chk_text_bold.isChecked()),
            "italic": bool(self.chk_text_italic.isChecked()),
            "math_mode": bool(self.chk_text_math.isChecked()),
        }
        self.text_items.append(item)
        self._refresh_text_list()
        for i in range(self.lst_text_items.count()):
            li = self.lst_text_items.item(i)
            if int(li.data(Qt.ItemDataRole.UserRole) or -1) == item["id"]:
                self.lst_text_items.setCurrentRow(i)
                break
        self.mark_modified()
        self.redraw_plot()

    def _update_text_item(self):
        it = self._selected_text_item()
        if not it:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_text_item"))
            return
        text_val = (self.inp_text_item.text() or "").strip()
        if not text_val:
            QMessageBox.information(self, t("msg_warning"), t("msg_text_empty"))
            return
        it["text"] = text_val
        it["coord_mode"] = str(self.combo_text_coord.currentData() or "axes")
        it["x"] = float(self.spin_text_x.value())
        it["y"] = float(self.spin_text_y.value())
        it["ha"] = str(self.combo_text_ha.currentData() or "left")
        it["va"] = str(self.combo_text_va.currentData() or "top")
        it["fontsize"] = int(self.spin_text_size.value())
        it["fontfamily"] = self._selected_text_font()
        it["rotation"] = float(self.spin_text_rotation.value())
        it["bold"] = bool(self.chk_text_bold.isChecked())
        it["italic"] = bool(self.chk_text_italic.isChecked())
        it["math_mode"] = bool(self.chk_text_math.isChecked())
        self._refresh_text_list()
        self.mark_modified()
        self.redraw_plot()

    def _delete_text_item(self):
        it = self._selected_text_item()
        if not it:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_text_item"))
            return
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_delete_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        tid = int(it.get("id", -1))
        self.text_items = [x for x in self.text_items if int(x.get("id", -2)) != tid]
        self._refresh_text_list()
        self.mark_modified()
        self.redraw_plot()

    def _load_auto_label_controls(self):
        cfg = self.text_auto_cfg
        self.chk_auto_panel_labels.blockSignals(True)
        self.chk_auto_panel_labels.setChecked(bool(cfg.get("enabled", False)))
        self.chk_auto_panel_labels.blockSignals(False)

        idx_style = self.combo_auto_label_style.findData(str(cfg.get("style", "lower_rparen")))
        self.combo_auto_label_style.setCurrentIndex(idx_style if idx_style >= 0 else 0)
        self.spin_auto_label_x.setValue(float(cfg.get("x", 0.02)))
        self.spin_auto_label_y.setValue(float(cfg.get("y", 0.98)))
        idx_ha = self.combo_auto_label_ha.findData(str(cfg.get("ha", "left")))
        self.combo_auto_label_ha.setCurrentIndex(idx_ha if idx_ha >= 0 else 0)
        idx_va = self.combo_auto_label_va.findData(str(cfg.get("va", "top")))
        self.combo_auto_label_va.setCurrentIndex(idx_va if idx_va >= 0 else 0)
        self.spin_auto_label_size.setValue(int(cfg.get("fontsize", 11)))
        self.chk_auto_label_bold.setChecked(bool(cfg.get("bold", True)))
        self.chk_auto_label_italic.setChecked(bool(cfg.get("italic", False)))

    def _apply_auto_label_preset(self, _idx: int):
        key = str(self.combo_auto_label_preset.currentData() or "custom")
        if key == "custom":
            return
        x, y, ha, va = get_text_preset(key)
        self.spin_auto_label_x.setValue(x)
        self.spin_auto_label_y.setValue(y)
        i_ha = self.combo_auto_label_ha.findData(ha)
        if i_ha >= 0:
            self.combo_auto_label_ha.setCurrentIndex(i_ha)
        i_va = self.combo_auto_label_va.findData(va)
        if i_va >= 0:
            self.combo_auto_label_va.setCurrentIndex(i_va)

    def _on_auto_label_settings_changed(self, *_args):
        self.text_auto_cfg.update({
            "enabled": bool(self.chk_auto_panel_labels.isChecked()),
            "style": str(self.combo_auto_label_style.currentData() or "lower_rparen"),
            "x": float(self.spin_auto_label_x.value()),
            "y": float(self.spin_auto_label_y.value()),
            "ha": str(self.combo_auto_label_ha.currentData() or "left"),
            "va": str(self.combo_auto_label_va.currentData() or "top"),
            "fontsize": int(self.spin_auto_label_size.value()),
            "bold": bool(self.chk_auto_label_bold.isChecked()),
            "italic": bool(self.chk_auto_label_italic.isChecked()),
        })
        self.mark_modified()
        self.redraw_plot()

    def _on_layout_changed(self, idx: int):
        label, rows, cols = LAYOUT_OPTIONS[idx]

        if rows is None:
            # Custom: kullanıcıdan al
            text, ok = QInputDialog.getText(
                self, t("dlg_layout_title"), t("dlg_layout_prompt"), text=t("dlg_layout_default")
            )
            if not ok or not text.strip():
                # İptal: combo'yu önceki değere döndür
                self.combo_layout.blockSignals(True)
                self.combo_layout.setCurrentIndex(0)
                self.combo_layout.blockSignals(False)
                return
            try:
                parts = text.replace('x', '×').split('×')
                rows, cols = int(parts[0].strip()), int(parts[1].strip())
                if rows < 1 or cols < 1 or rows * cols > 12:
                    raise ValueError
            except Exception:
                QMessageBox.warning(self, t("msg_error"), t("msg_layout_error"))
                self.combo_layout.blockSignals(True)
                self.combo_layout.setCurrentIndex(0)
                self.combo_layout.blockSignals(False)
                return

        orphan_ids = self.canvas.apply_layout(rows, cols)

        if orphan_ids:
            moved = self.data_manager.reassign_orphan_series(orphan_ids, target_panel_id=0)
            if moved > 0:
                QMessageBox.information(
                    self, "Bilgi",
                    t("msg_layout_moved").format(moved=moved)
                )
            moved_texts = 0
            for it in self.text_items:
                if int(it.get("panel_id", 0)) in orphan_ids:
                    it["panel_id"] = 0
                    moved_texts += 1
            if moved_texts > 0:
                self.statusBar().showMessage(t("msg_layout_texts_moved", n=moved_texts), 3000)

        self._refresh_panel_list()
        self._refresh_series_list()
        self._refresh_text_list()
        self.redraw_plot()

    def _rename_panel_action(self):
        row = self.lst_panels.currentRow()
        if row < 0:
            return
        old = self.canvas.panel_names[row]
        new, ok = QInputDialog.getText(self, t("dlg_panel_rename"), t("dlg_panel_rename_prompt"), text=old)
        if ok and new.strip():
            self.canvas.panel_names[row] = new.strip()
            self._refresh_panel_list()
            self._update_active_label()

    def _clear_panel_action(self):
        pid = self.canvas.active_index
        name = self.canvas.panel_names[pid]
        reply = QMessageBox.question(
            self, "Paneli Temizle",
            t("msg_panel_delete_text").format(name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.clear_panel(pid)
            # Bu panele ait fitleri de temizle
            self.fit_list = [f for f in self.fit_list if f.get('panel_id', 0) != pid]
            self.lst_fits.clear()
            self.lst_report_fits.clear()
            for f in self.fit_list:
                self.lst_fits.addItem(f['label'])
                fpid = f.get('panel_id', 0)
                pname = self.canvas.panel_names[fpid] if fpid < len(self.canvas.panel_names) else f"Ax{fpid+1}"
                self.lst_report_fits.addItem(f"{f.get('model_name', f['label'])} → {f.get('source_series', '')}  [{pname}]")
            self._clear_report()
            self._refresh_series_list()
            self.text_items = [it for it in self.text_items if int(it.get("panel_id", 0)) != pid]
            self._refresh_text_list()
            self.canvas.clear_panel(pid)
            self.redraw_plot()

    # --------------------------------------------------
    # Data table live update
    # --------------------------------------------------
    def update_from_table(self, item):
        df = self.data_manager.df
        if df is None:
            return

        row = item.row()
        col = item.column()
        if row < 0 or col < 0 or row >= df.shape[0] or col >= df.shape[1]:
            return

        col_name = df.columns[col]
        old_val = df.iat[row, col]
        txt = (item.text() or "").strip()

        # Boş değer her zaman NaN kabul edilir (hızlı silme senaryosu).
        if txt == "":
            new_val = np.nan
        else:
            col_is_numeric = pd.api.types.is_numeric_dtype(df[col_name])
            if col_is_numeric:
                parsed = pd.to_numeric(pd.Series([txt]), errors="coerce").iat[0]
                # Sayısal kolonda geçersiz girişte eski değeri geri yükle.
                if pd.isna(parsed) and txt.lower() != "nan":
                    self.table_w.blockSignals(True)
                    item.setText("" if pd.isna(old_val) else str(old_val))
                    self.table_w.blockSignals(False)
                    return
                new_val = parsed
            else:
                new_val = txt

        both_na = pd.isna(old_val) and pd.isna(new_val)
        if not both_na and old_val == new_val:
            return

        self._capture_last_table_undo(t("action_table_edit_cell"))
        df.iat[row, col] = new_val
        self._sync_series_from_dataframe()
        self.mark_modified()
        self.redraw_plot()

    def _capture_last_table_undo(self, action_label: str):
        """Tek adımlık geri-al için mevcut DataFrame'in derin kopyasını sakla."""
        if self.data_manager.df is None:
            return
        self._last_table_undo_df = self.data_manager.df.copy(deep=True)
        self._last_table_undo_action = action_label
        if hasattr(self, "btn_table_undo"):
            self.btn_table_undo.setEnabled(True)

    def _clear_last_table_undo(self):
        self._last_table_undo_df = None
        self._last_table_undo_action = ""
        if hasattr(self, "btn_table_undo"):
            self.btn_table_undo.setEnabled(False)

    def _sync_column_roles_with_df(self, reset: bool = False):
        """Sütun rol durumunu DataFrame kolonlarıyla senkronlar."""
        df = self.data_manager.df
        if df is None:
            self._column_roles = {}
            return

        cols = [str(c) for c in df.columns]
        if reset or not self._column_roles:
            self._column_roles = {c: "none" for c in cols}
            return

        self._column_roles = {c: self._column_roles.get(c, "none") for c in cols}

    def _role_template_options(self) -> list[tuple[str, str]]:
        return [
            ("none", t("role_template_none")),
            ("x_then_all_y_left", t("role_template_x_all_y")),
            ("alternating_x_y", t("role_template_xy_alternate")),
            ("all_y_left", t("role_template_all_y")),
            ("x_then_y_yerr_pairs", t("role_template_x_pairs")),
            ("x_xerr_then_y_yerr_pairs", t("role_template_x_xerr_pairs")),
        ]

    def _populate_role_template_combo(self):
        if not hasattr(self, "combo_role_template"):
            return
        self.combo_role_template.blockSignals(True)
        self.combo_role_template.clear()
        for key, label in self._role_template_options():
            self.combo_role_template.addItem(label, key)
        self.combo_role_template.setCurrentIndex(0)
        self.combo_role_template.blockSignals(False)

    def _apply_role_template_from_combo(self, _idx: int):
        if not hasattr(self, "combo_role_template"):
            return
        template_key = str(self.combo_role_template.currentData() or "none")
        if template_key == "none":
            return
        self._apply_role_template(template_key)
        self.combo_role_template.blockSignals(True)
        self.combo_role_template.setCurrentIndex(0)
        self.combo_role_template.blockSignals(False)

    def _column_role_options(self) -> list[tuple[str, str]]:
        return [
            ("none", t("table_role_empty")),
            ("x", t("table_role_x")),
            ("y_left", t("table_role_y_left")),
            ("y_right", t("table_role_y_right")),
            ("x_err", t("table_role_x_err")),
            ("y_err", t("table_role_y_err")),
        ]

    def _column_role_marker(self, role: str) -> str:
        if role == "x":
            return "X"
        if role == "y_left":
            return "YL"
        if role == "y_right":
            return "YR"
        if role == "x_err":
            return "XE"
        if role == "y_err":
            return "YE"
        return " "

    def _column_role_display(self, role: str) -> str:
        labels = dict(self._column_role_options())
        return labels.get(role, t("table_role_empty"))

    def _column_role_header_text(self, role: str) -> str:
        mapping = {
            "none": "",
            "x": "[X]",
            "y_left": "[YL]",
            "y_right": "[YR]",
            "x_err": "[XE]",
            "y_err": "[YE]",
        }
        return mapping.get(role, "")

    def _apply_table_headers_with_roles(self):
        """Header metinlerini sütun rol etiketleri ile birlikte günceller."""
        df = self.data_manager.df
        if df is None:
            self.table_w.setHorizontalHeaderLabels([])
            return

        cols = [str(c) for c in df.columns]
        labels = []
        for c in cols:
            role = self._column_roles.get(c, "none")
            role_text = self._column_role_header_text(role)
            labels.append(f"{role_text}\n{c}")
        self.table_w.setHorizontalHeaderLabels(labels)

    def _cycle_table_column_role(self, section: int):
        """Header'a çift tıklanınca rol döngüsü."""
        df = self.data_manager.df
        if df is None or section < 0 or section >= len(df.columns):
            return

        col_name = str(df.columns[section])
        current = self._column_roles.get(col_name, "none")
        ordered = [k for k, _ in self._column_role_options()]
        try:
            idx = ordered.index(current)
        except ValueError:
            idx = 0
        nxt = ordered[(idx + 1) % len(ordered)]
        self._set_column_role(section, nxt)

    def _set_column_role(self, section: int, role: str):
        df = self.data_manager.df
        if df is None or section < 0 or section >= len(df.columns):
            return
        valid_roles = {k for k, _ in self._column_role_options()}
        role = role if role in valid_roles else "none"
        col_name = str(df.columns[section])
        self._column_roles[col_name] = role
        self._apply_table_headers_with_roles()
        self._sync_role_combo_row()
        self.statusBar().showMessage(
            t("status_col_role_set", col=col_name, role=self._column_role_display(role)),
            2500
        )

    def _reset_all_column_roles(self):
        """Veri tablosundaki tüm sütun rol atamalarını temizler."""
        df = self.data_manager.df
        if df is None:
            return
        self._column_roles = {str(c): "none" for c in df.columns}
        self._apply_table_headers_with_roles()
        self._sync_role_combo_row()
        self.statusBar().showMessage(t("status_roles_reset"), 2000)

    def _apply_role_template(self, template_key: str):
        df = self.data_manager.df
        if df is None or df.empty:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return

        labels = dict(self._role_template_options())
        template_label = labels.get(template_key, template_key)
        confirm = QMessageBox.question(
            self,
            t("msg_confirm"),
            t("msg_role_template_confirm", template=template_label),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        cols = [str(c) for c in df.columns]
        roles = {c: "none" for c in cols}
        numeric_cols = {c for c in cols if pd.api.types.is_numeric_dtype(df[c])}
        numeric_only_roles = {"y_left", "y_right", "x_err", "y_err"}
        skipped_non_numeric = []

        def _set_role(idx: int, role: str) -> bool:
            if idx < 0 or idx >= len(cols):
                return False
            col = cols[idx]
            if role in numeric_only_roles and col not in numeric_cols:
                skipped_non_numeric.append(col)
                return False
            roles[col] = role
            return True

        if template_key == "x_then_all_y_left":
            _set_role(0, "x")
            for i in range(1, len(cols)):
                _set_role(i, "y_left")
        elif template_key == "alternating_x_y":
            for i in range(len(cols)):
                _set_role(i, "x" if i % 2 == 0 else "y_left")
        elif template_key == "all_y_left":
            for i in range(len(cols)):
                _set_role(i, "y_left")
        elif template_key == "x_then_y_yerr_pairs":
            _set_role(0, "x")
            i = 1
            while i < len(cols):
                _set_role(i, "y_left")
                _set_role(i + 1, "y_err")
                i += 2
        elif template_key == "x_xerr_then_y_yerr_pairs":
            _set_role(0, "x")
            _set_role(1, "x_err")
            i = 2
            while i < len(cols):
                _set_role(i, "y_left")
                _set_role(i + 1, "y_err")
                i += 2
        else:
            return

        self._column_roles = roles
        self._apply_table_headers_with_roles()
        self._sync_role_combo_row()

        x_count = sum(1 for r in roles.values() if r == "x")
        y_count = sum(1 for r in roles.values() if r == "y_left")
        xerr_count = sum(1 for r in roles.values() if r == "x_err")
        yerr_count = sum(1 for r in roles.values() if r == "y_err")
        skipped_count = len(set(skipped_non_numeric))
        self.statusBar().showMessage(
            t(
                "status_role_template_applied",
                template=template_label,
                x=x_count,
                y=y_count,
                xerr=xerr_count,
                yerr=yerr_count,
                skipped=skipped_count,
            ),
            3500
        )

    def _show_column_role_menu(self, pos):
        """Header sağ tık menüsü: rol atama + sütun adı değiştirme."""
        header = self.table_w.horizontalHeader()
        section = header.logicalIndexAt(pos)
        if section < 0:
            return
        df = self.data_manager.df
        if df is None or section >= len(df.columns):
            return

        col_name = str(df.columns[section])
        current = self._column_roles.get(col_name, "none")

        menu = QMenu(self)
        menu.setTitle(t("table_role_menu_title"))
        actions = {}
        for role_key, role_label in self._column_role_options():
            act = menu.addAction(role_label)
            act.setCheckable(True)
            act.setChecked(current == role_key)
            actions[act] = role_key
        menu.addSeparator()
        act_rename_col = menu.addAction(t("table_col_rename_action"))

        selected = menu.exec(header.mapToGlobal(pos))
        if selected in actions:
            self._set_column_role(section, actions[selected])
        elif selected == act_rename_col:
            self._rename_table_column(section)

    def _rename_table_column(self, section: int):
        df = self.data_manager.df
        if df is None or section < 0 or section >= len(df.columns):
            return

        old_name = str(df.columns[section])
        new_name, ok = QInputDialog.getText(
            self,
            t("dlg_rename_column_title"),
            t("dlg_rename_column_prompt"),
            text=old_name,
        )
        if not ok:
            return

        new_name = new_name.strip()
        if not new_name:
            QMessageBox.warning(self, t("msg_warning"), t("msg_col_name_empty"))
            return
        if new_name == old_name:
            return
        if new_name in {str(c) for c in df.columns}:
            QMessageBox.warning(
                self,
                t("msg_warning"),
                t("msg_col_name_exists").format(name=new_name),
            )
            return

        action_label = t("action_table_rename_col", old=old_name, new=new_name)
        self._capture_last_table_undo(action_label)

        new_df = df.copy(deep=True)
        cols = list(new_df.columns)
        cols[section] = new_name
        new_df.columns = cols

        # Rol eşlemesini yeni sütun adına taşı.
        old_roles = dict(self._column_roles)
        renamed_role = old_roles.pop(old_name, "none")
        self._column_roles = {str(c): old_roles.get(str(c), "none") for c in new_df.columns}
        self._column_roles[new_name] = renamed_role

        # Seri kaynak sütun referanslarını güncelle.
        for s in self.series_list:
            if s.get("x_col") == old_name:
                s["x_col"] = new_name
            if s.get("y_col") == old_name:
                s["y_col"] = new_name
            if s.get("x_err_col") == old_name:
                s["x_err_col"] = new_name
            if s.get("y_err_col") == old_name:
                s["y_err_col"] = new_name

        self._apply_dataframe_mutation(new_df, action_label)

    def _clear_role_combo_row(self):
        self._role_combos = []
        while self.role_select_layout.count():
            item = self.role_select_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _sync_role_combo_row(self):
        for i in range(self.role_select_layout.count()):
            combo = self.role_select_layout.itemAt(i).widget()
            if not isinstance(combo, QComboBox):
                continue
            col_name = combo.property("col_name")
            role = self._column_roles.get(str(col_name), "none")
            combo.blockSignals(True)
            idx = combo.findData(role)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.blockSignals(False)

    def _rebuild_role_combo_row(self):
        df = self.data_manager.df
        self._clear_role_combo_row()
        if df is None or df.empty:
            return
        self._sync_column_roles_with_df(reset=False)
        options = self._column_role_options()
        for col in [str(c) for c in df.columns]:
            combo = QComboBox()
            combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            combo.setStyleSheet("QComboBox { margin: 0px; }")
            combo.setProperty("col_name", col)
            combo.setToolTip(col)
            for role_key, role_label in options:
                combo.addItem(role_label, role_key)
            idx = combo.findData(self._column_roles.get(col, "none"))
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            combo.currentIndexChanged.connect(partial(self._on_role_combo_changed, combo))
            self.role_select_layout.addWidget(combo)
            self._role_combos.append(combo)
        self._sync_role_row_layout()

    def _on_role_combo_changed(self, combo: QComboBox, _idx: int):
        col_name = str(combo.property("col_name"))
        role = combo.currentData()
        if role is None:
            role = "none"
        self._column_roles[col_name] = str(role)
        self._apply_table_headers_with_roles()
        self.statusBar().showMessage(
            t("status_col_role_set", col=col_name, role=self._column_role_display(str(role))),
            2000
        )

    def _sync_role_row_layout(self):
        """Rol dropdown satırını tablo sütunlarına hizalar."""
        if not hasattr(self, "_role_combos"):
            return
        left_pad = self.table_w.verticalHeader().width()
        if hasattr(self, "role_left_pad"):
            self.role_left_pad.setFixedWidth(max(0, left_pad))
        n = min(len(self._role_combos), self.table_w.columnCount())
        total_w = 0
        for i in range(n):
            w = self.table_w.columnWidth(i)
            self._role_combos[i].setFixedWidth(w)
            total_w += w
        self.role_select_host.setFixedWidth(total_w)
        self._sync_role_scroll_from_table(self.table_w.horizontalScrollBar().value())

    def _sync_role_scroll_from_table(self, value: int):
        if self._role_scroll_syncing:
            return
        self._role_scroll_syncing = True
        self.role_select_scroll.horizontalScrollBar().setValue(value)
        self._role_scroll_syncing = False

    def _sync_table_scroll_from_role(self, value: int):
        if self._role_scroll_syncing:
            return
        self._role_scroll_syncing = True
        self.table_w.horizontalScrollBar().setValue(value)
        self._role_scroll_syncing = False

    def _on_plot_type_changed_with_sync(self, idx: int):
        self._on_plot_type_changed(idx)
        if hasattr(self, "combo_table_plot_type"):
            self._table_plot_syncing = True
            self.combo_table_plot_type.setCurrentIndex(idx)
            self._table_plot_syncing = False

    def _on_table_plot_type_changed(self, idx: int):
        if self._table_plot_syncing:
            return
        self._table_plot_syncing = True
        self.combo_plot_type.setCurrentIndex(idx)
        self._table_plot_syncing = False

    def _build_role_series_specs(self, plot_type: str):
        """
        Rol şemasından seri spesifikasyonları üretir.
        Geçersiz bir desen varsa tüm işlemi iptal edecek hata listesi döndürür.
        """
        df = self.data_manager.df
        if df is None or df.empty:
            return [], [t("msg_no_data")]

        cols = [str(c) for c in df.columns]
        roles = [self._column_roles.get(c, "none") for c in cols]
        active = [r for r in roles if r != "none"]
        if not active:
            return [], [t("msg_role_empty")]
        if not any(r in ("y_left", "y_right") for r in active):
            return [], [t("msg_role_no_y")]

        if plot_type == "histogram":
            if any(r in ("x", "x_err", "y_err") for r in active):
                return [], [t("msg_role_invalid_for_hist")]
            specs = []
            for i, role in enumerate(roles):
                if role in ("y_left", "y_right"):
                    specs.append({
                        "x_col": None,
                        "x_err_col": None,
                        "y_col": cols[i],
                        "y_err_col": None,
                        "axis": "left" if role == "y_left" else "right",
                    })
            return specs, []

        errors = []
        groups = [{"x_col": None, "x_err_col": None, "items": []}]

        for i, role in enumerate(roles):
            col = cols[i]
            grp = groups[-1]
            if role == "none":
                continue

            if role == "x":
                if grp["x_col"] is not None and not grp["items"]:
                    errors.append(t("msg_role_invalid_double_x", col=col))
                    continue
                groups.append({"x_col": col, "x_err_col": None, "items": []})
                continue

            if role == "x_err":
                if grp["x_col"] is None:
                    errors.append(t("msg_role_xerr_without_x", col=col))
                    continue
                if grp["x_err_col"] is not None:
                    errors.append(t("msg_role_multi_xerr", col=col, prev=grp["x_err_col"]))
                    continue
                grp["x_err_col"] = col
                continue

            if role in ("y_left", "y_right"):
                grp["items"].append({
                    "y_col": col,
                    "y_err_col": None,
                    "axis": "left" if role == "y_left" else "right",
                })
                continue

            if role == "y_err":
                if not grp["items"]:
                    errors.append(t("msg_role_yerr_without_y", col=col))
                    continue
                target = None
                for item in reversed(grp["items"]):
                    if item["y_err_col"] is None:
                        target = item
                        break
                if target is None:
                    errors.append(t("msg_role_multi_yerr", col=col))
                    continue
                target["y_err_col"] = col

        for grp in groups:
            if grp["x_col"] is not None and not grp["items"]:
                errors.append(t("msg_role_invalid_x_without_y", col=grp["x_col"]))
            if plot_type == "bar":
                if grp["x_col"] is None and grp["items"]:
                    errors.append(t("msg_role_bar_requires_x"))

        specs = []
        for grp in groups:
            x_col = grp["x_col"]
            x_err_col = grp["x_err_col"]
            for item in grp["items"]:
                specs.append({
                    "x_col": x_col,
                    "x_err_col": x_err_col,
                    "y_col": item["y_col"],
                    "y_err_col": item["y_err_col"],
                    "axis": item["axis"],
                })

        # Numeric doğrulama
        for spec in specs:
            y_col = spec["y_col"]
            if y_col not in df.columns or not pd.api.types.is_numeric_dtype(df[y_col]):
                errors.append(t("msg_role_non_numeric_y", col=y_col))
            y_err_col = spec["y_err_col"]
            if y_err_col and (y_err_col not in df.columns or not pd.api.types.is_numeric_dtype(df[y_err_col])):
                errors.append(t("msg_role_non_numeric_yerr", col=y_err_col))
            if plot_type == "scatter":
                x_col = spec["x_col"]
                if x_col and (x_col not in df.columns or not pd.api.types.is_numeric_dtype(df[x_col])):
                    errors.append(t("msg_role_non_numeric_x", col=x_col))
                x_err_col = spec["x_err_col"]
                if x_err_col and (x_err_col not in df.columns or not pd.api.types.is_numeric_dtype(df[x_err_col])):
                    errors.append(t("msg_role_non_numeric_xerr", col=x_err_col))

        return specs, sorted(set(errors))

    def _series_exists(
        self,
        panel_id: int,
        axis: str,
        plot_type: str,
        x_col: str | None,
        y_col: str,
        x_err_col: str | None = None,
        y_err_col: str | None = None,
    ) -> bool:
        for s in self.series_list:
            if s.get("panel_id", 0) != panel_id:
                continue
            if s.get("axis", "left") != axis:
                continue
            if s.get("plot_type", "scatter") != plot_type:
                continue
            if s.get("x_col") == x_col and s.get("y_col") == y_col:
                if x_err_col is not None and s.get("x_err_col") != x_err_col:
                    continue
                if y_err_col is not None and s.get("y_err_col") != y_err_col:
                    continue
                return True
        return False

    def _refresh_table_widget_from_df(self):
        """QTableWidget içeriğini mevcut DataFrame ile tam senkron yeniler."""
        df = self.data_manager.df
        tw = self.table_w
        if df is None:
            self._column_roles = {}
            tw.blockSignals(True)
            tw.clearContents()
            tw.setRowCount(0)
            tw.setColumnCount(0)
            tw.blockSignals(False)
            self._clear_role_combo_row()
            return

        self._sync_column_roles_with_df(reset=False)
        tw.setUpdatesEnabled(False)
        tw.blockSignals(True)
        tw.clearContents()
        tw.setRowCount(df.shape[0])
        tw.setColumnCount(df.shape[1])
        self._apply_table_headers_with_roles()
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                tw.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        tw.blockSignals(False)
        tw.setUpdatesEnabled(True)
        tw.viewport().update()
        self._rebuild_role_combo_row()

    def _sync_series_from_dataframe(self):
        """
        Mevcut seri listelerini DataFrame'den yeniden hesapla.
        Satır ekleme/silme/shift-up işlemlerinden sonra x/y ve hata dizileri güncel kalır.
        """
        df = self.data_manager.df
        if df is None:
            return

        for s in self.series_list:
            plot_type = s.get("plot_type", "scatter")
            y_col = s.get("y_col")
            x_col = s.get("x_col")
            if y_col not in df.columns:
                s["x"] = np.array([])
                s["y"] = np.array([])
                s["x_err"] = None
                s["y_err"] = None
                continue

            if plot_type == "histogram":
                y = pd.to_numeric(df[y_col], errors="coerce").values
                y_clean = y[~np.isnan(y)]
                s["x"] = np.array([])
                s["y"] = y_clean
                s["x_err"] = None
                s["y_err"] = None
                continue

            if plot_type == "bar":
                if x_col not in df.columns:
                    s["x"] = np.array([])
                    s["y"] = np.array([])
                    s["x_err"] = None
                    s["y_err"] = None
                    continue
                subset = df[[x_col, y_col]].copy()
                x = subset[x_col].values
                y = pd.to_numeric(subset[y_col], errors="coerce").values
                mask = ~pd.isna(x) & ~np.isnan(y)
                s["x"] = x[mask]
                s["y"] = y[mask]
                s["x_err"] = None
                yerr_col = s.get("y_err_col")
                if yerr_col and yerr_col in df.columns:
                    yerr = pd.to_numeric(df[yerr_col], errors="coerce").values
                    s["y_err"] = yerr[mask]
                else:
                    s["y_err"] = None
                continue

            # scatter / line
            y = pd.to_numeric(df[y_col], errors="coerce").values
            if x_col is not None and x_col in df.columns:
                x = pd.to_numeric(df[x_col], errors="coerce").values
                mask = ~np.isnan(x) & ~np.isnan(y)
                x_clean = x[mask]
            else:
                mask = ~np.isnan(y)
                x_clean = np.arange(1, int(np.sum(mask)) + 1)
            s["x"] = x_clean
            s["y"] = y[mask]

            xerr_col = s.get("x_err_col")
            if xerr_col and xerr_col in df.columns and x_col is not None:
                xerr = pd.to_numeric(df[xerr_col], errors="coerce").values
                s["x_err"] = xerr[mask]
            else:
                s["x_err"] = None

            yerr_col = s.get("y_err_col")
            if yerr_col and yerr_col in df.columns:
                yerr = pd.to_numeric(df[yerr_col], errors="coerce").values
                s["y_err"] = yerr[mask]
            else:
                s["y_err"] = None

    def _apply_dataframe_mutation(self, new_df: pd.DataFrame, action_label: str):
        """Tablo mutasyonu sonrası ortak yenileme adımları."""
        self.data_manager.df = new_df.reset_index(drop=True)
        self._refresh_table_widget_from_df()
        self._refresh_axis_selectors_from_df()
        self._sync_series_from_dataframe()
        self.mark_modified()
        self.redraw_plot()
        self.statusBar().showMessage(t("status_done_action", action=action_label), 2500)

    def _selected_table_rows(self) -> list[int]:
        """Sadece tablonun tamamını yatay kapsayan (tam satır) seçimleri döndürür."""
        col_count = self.table_w.columnCount()
        if col_count <= 0:
            return []
        rows = set()
        for sel in self.table_w.selectedRanges():
            if sel.leftColumn() == 0 and sel.rightColumn() == (col_count - 1):
                for r in range(sel.topRow(), sel.bottomRow() + 1):
                    rows.add(r)
        return sorted(rows)

    def _selected_table_columns(self) -> list[int]:
        """Sadece tablonun tamamını dikey kapsayan (tam sütun) seçimleri döndürür."""
        row_count = self.table_w.rowCount()
        if row_count <= 0:
            return []
        cols = set()
        for sel in self.table_w.selectedRanges():
            if sel.topRow() == 0 and sel.bottomRow() == (row_count - 1):
                for c in range(sel.leftColumn(), sel.rightColumn() + 1):
                    cols.add(c)
        return sorted(cols)

    def _refresh_axis_selectors_from_df(self):
        """DataFrame değişimi sonrası X/Y ve hata kolon seçimlerini günceller."""
        df = self.data_manager.df
        if df is None:
            return

        numeric_cols = [str(c) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        all_cols = [str(c) for c in df.columns]

        cur_x = self.combo_x.currentText()
        cur_y = self.combo_y.currentText()
        cur_xerr = self.combo_x_err.currentText()
        cur_yerr = self.combo_y_err.currentText()
        selected_y = {it.text() for it in self.lst_y_select.selectedItems()}

        self.combo_x.blockSignals(True)
        self.combo_x.clear()
        self.combo_x.addItem(t("auto_x_label"))
        self.combo_x.addItems(all_cols)
        self.combo_x.blockSignals(False)
        idx = self.combo_x.findText(cur_x)
        if idx >= 0:
            self.combo_x.setCurrentIndex(idx)

        self.combo_y.blockSignals(True)
        self.combo_y.clear()
        self.combo_y.addItems(numeric_cols)
        self.combo_y.blockSignals(False)
        idx = self.combo_y.findText(cur_y)
        if idx >= 0:
            self.combo_y.setCurrentIndex(idx)
        elif self.combo_y.count() > 0:
            self.combo_y.setCurrentIndex(0)

        for combo, cur in ((self.combo_x_err, cur_xerr), (self.combo_y_err, cur_yerr)):
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Yok")
            combo.addItems(numeric_cols)
            combo.blockSignals(False)
            idx = combo.findText(cur)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        self.lst_y_select.blockSignals(True)
        self.lst_y_select.clear()
        self.lst_y_select.addItems(numeric_cols)
        for i in range(self.lst_y_select.count()):
            if self.lst_y_select.item(i).text() in selected_y:
                self.lst_y_select.item(i).setSelected(True)
        self.lst_y_select.blockSignals(False)
        self._on_y_selection_changed()

    def _show_table_context_menu(self, pos):
        """Tablo gövdesinde sağ tık menüsü: seçim tipine göre işlem önerir."""
        df = self.data_manager.df
        if df is None or self.table_w.rowCount() == 0 or self.table_w.columnCount() == 0:
            return

        index = self.table_w.indexAt(pos)
        if index.isValid():
            sel_model = self.table_w.selectionModel()
            if sel_model is not None and not sel_model.isSelected(index):
                sel_model.select(
                    index,
                    QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Current
                )

        if not self.table_w.selectedIndexes():
            return

        rows = self._selected_table_rows()
        cols = self._selected_table_columns()
        row_mode = bool(rows) and not bool(cols)
        col_mode = bool(cols) and not bool(rows)

        menu = QMenu(self)
        act_delete_cells = None
        act_set_cells_nan = None
        act_delete_rows = None
        act_delete_cols = None
        act_insert_col_left_blank = None
        act_insert_col_right_blank = None
        act_insert_col_left_index = None
        act_insert_col_right_index = None
        act_insert_above = None
        act_insert_below = None

        if col_mode:
            act_insert_col_left_blank = menu.addAction(t("btn_table_insert_col_left_blank"))
            act_insert_col_right_blank = menu.addAction(t("btn_table_insert_col_right_blank"))
            act_insert_col_left_index = menu.addAction(t("btn_table_insert_col_left_index"))
            act_insert_col_right_index = menu.addAction(t("btn_table_insert_col_right_index"))
            menu.addSeparator()
            act_delete_cols = menu.addAction(t("btn_table_col_delete"))
        elif row_mode:
            act_delete_rows = menu.addAction(t("btn_table_row_delete"))
            menu.addSeparator()
            act_insert_above = menu.addAction(t("btn_table_insert_above"))
            act_insert_below = menu.addAction(t("btn_table_insert_below"))
        else:
            act_set_cells_nan = menu.addAction(t("btn_table_cells_set_nan"))
            act_delete_cells = menu.addAction(t("btn_table_cells_shift_delete"))
            menu.addSeparator()
            act_insert_above = menu.addAction(t("btn_table_insert_above"))
            act_insert_below = menu.addAction(t("btn_table_insert_below"))

        chosen = menu.exec(self.table_w.viewport().mapToGlobal(pos))
        if chosen is None:
            return
        if chosen == act_delete_cols:
            self._delete_selected_columns_from_table()
        elif chosen == act_insert_col_left_blank:
            self._insert_column_relative_to_selection("left", "blank")
        elif chosen == act_insert_col_right_blank:
            self._insert_column_relative_to_selection("right", "blank")
        elif chosen == act_insert_col_left_index:
            self._insert_column_relative_to_selection("left", "index")
        elif chosen == act_insert_col_right_index:
            self._insert_column_relative_to_selection("right", "index")
        elif chosen == act_delete_rows:
            self._delete_selected_rows_from_table()
        elif chosen == act_set_cells_nan:
            self._set_selected_cells_nan()
        elif chosen == act_delete_cells:
            self._delete_selected_cells_shift_up()
        elif chosen == act_insert_above:
            self._insert_rows_relative_to_selection("above")
        elif chosen == act_insert_below:
            self._insert_rows_relative_to_selection("below")

    def _set_selected_cells_nan(self):
        df = self.data_manager.df
        if df is None or df.empty:
            return
        selected = self.table_w.selectedIndexes()
        if not selected:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_cells"))
            return

        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_set_nan"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._capture_last_table_undo(t("action_table_cells_set_nan"))
        new_df = df.copy(deep=True)
        for idx in selected:
            new_df.iat[idx.row(), idx.column()] = np.nan

        self._apply_dataframe_mutation(new_df, t("action_table_cells_set_nan"))

    def _delete_selected_rows_from_table(self):
        df = self.data_manager.df
        if df is None or df.empty:
            return
        rows = self._selected_table_rows()
        if not rows:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_rows_delete"))
            return
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_delete_rows", n=len(rows)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._capture_last_table_undo(t("action_table_row_delete"))
        new_df = df.drop(index=rows).reset_index(drop=True)
        self._apply_dataframe_mutation(new_df, t("action_table_row_delete"))

    def _delete_selected_columns_from_table(self):
        df = self.data_manager.df
        if df is None or df.empty:
            return
        cols_idx = self._selected_table_columns()
        if not cols_idx:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_cols_delete"))
            return
        if len(cols_idx) >= df.shape[1]:
            QMessageBox.warning(self, t("msg_warning"), t("msg_cannot_delete_all_columns"))
            return

        col_names = [str(df.columns[i]) for i in cols_idx]
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_delete_cols", n=len(col_names), cols=", ".join(col_names)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._capture_last_table_undo(t("action_table_col_delete"))
        keep_cols = [c for i, c in enumerate(df.columns) if i not in cols_idx]
        new_df = df.loc[:, keep_cols].copy()

        # Silinen kolonları kullanan serileri kaldır.
        removed = set(col_names)
        new_series = []
        for s in self.series_list:
            y_col = s.get("y_col")
            x_col = s.get("x_col")
            x_err_col = s.get("x_err_col")
            y_err_col = s.get("y_err_col")
            if y_col in removed or x_col in removed or x_err_col in removed or y_err_col in removed:
                continue
            new_series.append(s)
        self.series_list = new_series
        self._refresh_series_list()

        self._apply_dataframe_mutation(new_df, t("action_table_col_delete"))

    def _delete_selected_cells_shift_up(self):
        df = self.data_manager.df
        if df is None or df.empty:
            return
        selected = self.table_w.selectedIndexes()
        if not selected:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_cells"))
            return
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_shift_delete"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._capture_last_table_undo(t("action_table_cells_shift_delete"))
        new_df = df.copy(deep=True)
        by_col = {}
        for idx in selected:
            by_col.setdefault(idx.column(), set()).add(idx.row())

        for col_idx, rows_set in by_col.items():
            rows = sorted(rows_set)
            col_series = new_df.iloc[:, col_idx]
            remaining = col_series.drop(index=rows).reset_index(drop=True)
            padded = pd.concat(
                [remaining, pd.Series([np.nan] * len(rows), index=range(len(rows)))],
                ignore_index=True,
            )
            new_df.iloc[:, col_idx] = padded.values

        self._apply_dataframe_mutation(new_df, t("action_table_cells_shift_delete"))

    @staticmethod
    def _parse_clipboard_matrix(raw_text: str) -> list[list[str]]:
        if not raw_text:
            return []
        normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        rows = [line.split("\t") for line in normalized.split("\n")]
        while rows and len(rows[-1]) == 1 and rows[-1][0] == "":
            rows.pop()
        if not rows:
            return []
        width = max(len(r) for r in rows)
        if width <= 0:
            return []
        return [r + ([""] * (width - len(r))) for r in rows]

    @staticmethod
    def _cell_values_equal(old_val, new_val) -> bool:
        try:
            if pd.isna(old_val) and pd.isna(new_val):
                return True
        except Exception:
            pass
        try:
            return bool(old_val == new_val)
        except Exception:
            return False

    def _coerce_pasted_value(self, df: pd.DataFrame, col_idx: int, raw_text: str):
        col_name = df.columns[col_idx]
        txt = (raw_text or "").strip()
        if txt == "":
            return np.nan, True

        if pd.api.types.is_numeric_dtype(df[col_name]):
            parsed = pd.to_numeric(pd.Series([txt]), errors="coerce").iat[0]
            if pd.isna(parsed) and txt.lower() != "nan":
                return None, False
            return parsed, True

        return txt, True

    def _paste_table_from_clipboard(self) -> bool:
        df = self.data_manager.df
        if df is None or df.shape[1] == 0:
            return False

        clip_text = QApplication.clipboard().text()
        matrix = self._parse_clipboard_matrix(clip_text)
        if not matrix:
            self.statusBar().showMessage(t("msg_paste_empty_clipboard"), 2500)
            return True

        selected = self.table_w.selectedIndexes()
        new_df = df.copy(deep=True)
        updated_count = 0
        skipped_count = 0
        added_rows = 0
        trimmed_cols = 0

        # Tek değer + çoklu seçim: tüm seçili hücrelere uygula.
        if len(matrix) == 1 and len(matrix[0]) == 1 and len(selected) > 1:
            value_text = matrix[0][0]
            for idx in selected:
                value, ok = self._coerce_pasted_value(new_df, idx.column(), value_text)
                if not ok:
                    skipped_count += 1
                    continue
                old_val = new_df.iat[idx.row(), idx.column()]
                if self._cell_values_equal(old_val, value):
                    continue
                new_df.iat[idx.row(), idx.column()] = value
                updated_count += 1
        else:
            current = self.table_w.currentIndex()
            if current.isValid():
                start_row, start_col = current.row(), current.column()
            elif selected:
                start_row = min(i.row() for i in selected)
                start_col = min(i.column() for i in selected)
            else:
                start_row, start_col = 0, 0

            if start_col >= new_df.shape[1]:
                self.statusBar().showMessage(t("msg_paste_select_target"), 2500)
                return True

            row_need = start_row + len(matrix)
            if row_need > new_df.shape[0]:
                added_rows = row_need - new_df.shape[0]
                extra = pd.DataFrame(np.nan, index=range(added_rows), columns=new_df.columns)
                new_df = pd.concat([new_df, extra], ignore_index=True)

            max_cols = max(len(r) for r in matrix)
            usable_cols = min(max_cols, new_df.shape[1] - start_col)
            trimmed_cols = max(0, max_cols - usable_cols)
            if usable_cols <= 0:
                self.statusBar().showMessage(t("msg_paste_select_target"), 2500)
                return True

            for r_off, row_vals in enumerate(matrix):
                r = start_row + r_off
                for c_off in range(usable_cols):
                    c = start_col + c_off
                    value, ok = self._coerce_pasted_value(new_df, c, row_vals[c_off])
                    if not ok:
                        skipped_count += 1
                        continue
                    old_val = new_df.iat[r, c]
                    if self._cell_values_equal(old_val, value):
                        continue
                    new_df.iat[r, c] = value
                    updated_count += 1

        shape_changed = new_df.shape != df.shape
        if not shape_changed and updated_count == 0:
            self.statusBar().showMessage(t("msg_paste_no_change"), 2500)
            return True

        action_label = t("action_table_paste")
        self._capture_last_table_undo(action_label)
        self._apply_dataframe_mutation(new_df, action_label)
        if skipped_count > 0 or trimmed_cols > 0 or added_rows > 0:
            self.statusBar().showMessage(
                t(
                    "status_table_paste_summary",
                    updated=updated_count,
                    skipped=skipped_count,
                    trimmed=trimmed_cols,
                    rows=added_rows,
                ),
                4500,
            )
        return True

    def _insert_rows_relative_to_selection(self, mode: str):
        """mode: 'above' | 'below'"""
        df = self.data_manager.df
        if df is None:
            return
        rows = self._selected_table_rows()
        if not rows:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_target_rows"))
            return
        mode_text = t("table_insert_above_word") if mode == "above" else t("table_insert_below_word")
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_insert_rows", n=len(rows), where=mode_text),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._capture_last_table_undo(t("action_table_insert_rows", where=mode_text))
        new_df = df.copy(deep=True)
        offset = 0
        for r in rows:
            insert_at = r + offset if mode == "above" else r + 1 + offset
            nan_row = pd.DataFrame([[np.nan] * new_df.shape[1]], columns=new_df.columns)
            new_df = pd.concat(
                [new_df.iloc[:insert_at], nan_row, new_df.iloc[insert_at:]],
                ignore_index=True,
            )
            offset += 1
        self._apply_dataframe_mutation(new_df, t("action_table_insert_rows", where=mode_text))

    @staticmethod
    def _unique_column_name(existing_cols, base_name: str) -> str:
        existing = {str(c) for c in existing_cols}
        if base_name not in existing:
            return base_name
        i = 2
        while True:
            cand = f"{base_name}_{i}"
            if cand not in existing:
                return cand
            i += 1

    def _insert_column_relative_to_selection(self, side: str, mode: str):
        """
        side: 'left' | 'right'
        mode: 'blank' | 'index'
        """
        df = self.data_manager.df
        if df is None:
            return
        cols = self._selected_table_columns()
        if not cols:
            QMessageBox.information(self, t("msg_warning"), t("msg_select_cols_delete"))
            return

        where_text = t("table_insert_left_word") if side == "left" else t("table_insert_right_word")
        fill_text = t("table_col_fill_blank_word") if mode == "blank" else t("table_col_fill_index_word")
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_insert_col", where=where_text, fill=fill_text),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if side == "left":
            insert_at = min(cols)
        else:
            insert_at = max(cols) + 1

        new_df = df.copy(deep=True)
        base_name = "X_Index" if mode == "index" else "New_Column"
        new_name = self._unique_column_name(new_df.columns, base_name)
        if mode == "index":
            values = np.arange(1, len(new_df) + 1, dtype=float)
            action_label = t("action_table_insert_col_index", where=where_text)
        else:
            values = np.full(len(new_df), np.nan, dtype=float)
            action_label = t("action_table_insert_col_blank", where=where_text)

        self._capture_last_table_undo(action_label)
        new_df.insert(insert_at, new_name, values)
        self._apply_dataframe_mutation(new_df, action_label)

    def _undo_last_table_action(self):
        if self._last_table_undo_df is None:
            return
        reply = QMessageBox.question(
            self,
            t("msg_confirm_title"),
            t("msg_confirm_undo_last", action=self._last_table_undo_action),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        restore_df = self._last_table_undo_df.copy(deep=True)
        self._clear_last_table_undo()
        self._apply_dataframe_mutation(restore_df, t("action_table_undo"))

    def eventFilter(self, source, event):
        if source is self.table_w and event.type() == QEvent.Type.KeyPress:
            if event.matches(QKeySequence.StandardKey.Paste):
                if self._paste_table_from_clipboard():
                    return True
            if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                has_col_selection = bool(self._selected_table_columns())
                has_row_selection = bool(self._selected_table_rows())
                has_cell_selection = bool(self.table_w.selectedIndexes())

                if has_col_selection:
                    self._delete_selected_columns_from_table()
                    return True
                if has_row_selection:
                    self._delete_selected_rows_from_table()
                    return True
                if has_cell_selection:
                    self._delete_selected_cells_shift_up()
                    return True
        return super().eventFilter(source, event)

    # --------------------------------------------------
    # Dialogs
    # --------------------------------------------------
    def open_settings(self, tab_title: str | None = None):
        pid = self.canvas.active_index
        if not hasattr(self, '_settings_dlg') or self._settings_dlg is None:
            self._settings_dlg = PlotSettingsDialog(self, self)
        dlg = self._settings_dlg
        dlg._reload_for_panel(pid)
        if tab_title:
            for i in range(dlg.tabs.count()):
                if dlg.tabs.tabText(i) == tab_title:
                    dlg.tabs.setCurrentIndex(i)
                    break
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    # --------------------------------------------------
    # Proje Kaydet / Aç
    # --------------------------------------------------
    def save_project_action(self, force_dialog: bool = False):
        if self.data_manager.df is None or self.data_manager.df.empty:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return
        save_path = self._current_project_path
        if force_dialog or not save_path:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Projeyi Kaydet",
                self._dialog_start_path("proje.json"),
                "JSON Files (*.json)",
            )
            if not save_path:
                return
            self._remember_dialog_path(save_path)
        try:
            csv_buffer = io.StringIO()
            self.data_manager.df.to_csv(csv_buffer, index=False)
            csv_text = csv_buffer.getvalue()

            serializable_series = []
            for s in self.series_list:
                s_copy = s.copy()
                s_copy.setdefault('panel_id', 0)
                if isinstance(s_copy.get('x'), np.ndarray):
                    s_copy['x'] = s_copy['x'].tolist()
                if isinstance(s_copy.get('y'), np.ndarray):
                    s_copy['y'] = s_copy['y'].tolist()
                if isinstance(s_copy.get('x_err'), np.ndarray):
                    s_copy['x_err'] = s_copy['x_err'].tolist()
                if isinstance(s_copy.get('y_err'), np.ndarray):
                    s_copy['y_err'] = s_copy['y_err'].tolist()
                serializable_series.append(s_copy)

            serializable_fits = []
            for f_item in self.fit_list:
                f_copy = f_item.copy()
                f_copy.setdefault('panel_id', 0)
                if isinstance(f_copy.get('x'), np.ndarray):
                    f_copy['x'] = f_copy['x'].tolist()
                if isinstance(f_copy.get('y'), np.ndarray):
                    f_copy['y'] = f_copy['y'].tolist()
                if isinstance(f_copy.get('res_x'), np.ndarray):
                    f_copy['res_x'] = f_copy['res_x'].tolist()
                if isinstance(f_copy.get('res_y'), np.ndarray):
                    f_copy['res_y'] = f_copy['res_y'].tolist()
                serializable_fits.append(f_copy)

            # Panel config ve isimleri kaydet
            panel_configs_save = []
            for cfg in self.canvas.panel_configs:
                panel_configs_save.append(cfg.copy())

            project_data = {
                "raw_data": csv_text,
                "canvas_config": self.canvas_config,
                "layout": [self.canvas._layout_rows, self.canvas._layout_cols],
                "panel_names": self.canvas.panel_names,
                "panel_configs": panel_configs_save,
                "series": serializable_series,
                "fits": serializable_fits,
                "text_items": self.text_items,
                "text_auto_cfg": self.text_auto_cfg,
                "global_states": getattr(self._settings_dlg, '_global_states', {}) if hasattr(self, '_settings_dlg') and self._settings_dlg else {},
            }
            write_project(save_path, project_data)

            self._current_project_path = save_path
            self._remember_dialog_path(save_path)
            self._is_modified = False
            QMessageBox.information(self, t("msg_success"), t("msg_save_ok"))
        except Exception as e:
            QMessageBox.critical(self, t("msg_error"), t("msg_save_error").format(err=str(e)))

    def save_project_as_action(self):
        self.save_project_action(force_dialog=True)

    def open_project_action(self):
        f, _ = QFileDialog.getOpenFileName(
            self,
            t("dlg_open_project"),
            self._dialog_start_path(),
            "JSON Files (*.json)",
        )
        if not f:
            return
        try:
            loaded_project = read_project(f)
            data = loaded_project.data
            self._clear_last_table_undo()

            csv_text = data.get("raw_data", "")
            if csv_text:
                csv_buffer = io.StringIO(csv_text)
                df = pd.read_csv(csv_buffer)
                self.data_manager.df = df

                self.table_w.setRowCount(df.shape[0])
                self.table_w.setColumnCount(df.shape[1])
                self._sync_column_roles_with_df(reset=True)
                self._apply_table_headers_with_roles()

                self.table_w.blockSignals(True)
                for i in range(min(df.shape[0], 100)):
                    for j in range(df.shape[1]):
                        self.table_w.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                self.table_w.blockSignals(False)
                self._rebuild_role_combo_row()

                cols = [str(c) for c in df.columns]
                self.combo_x.clear()
                self.combo_y.clear()
                self.combo_x_err.clear()
                self.combo_y_err.clear()
                self.combo_x.addItems(cols)
                self.combo_y.addItems(cols)
                self.combo_x_err.addItem("Yok")
                self.combo_y_err.addItem("Yok")
                self.combo_x_err.addItems(cols)
                self.combo_y_err.addItems(cols)
                self.lst_y_select.clear()
                self.lst_y_select.addItems(cols)
                if len(df.columns) > 1:
                    self.combo_y.setCurrentIndex(1)

            # Canvas config
            if "canvas_config" in data:
                self.canvas_config.update(data["canvas_config"])

            # Layout restore
            layout = data.get("layout", [1, 1])
            rows, cols_l = layout[0], layout[1]
            self.canvas.apply_layout(rows, cols_l)

            # Panel isimleri
            p_names = data.get("panel_names", [])
            for i, name in enumerate(p_names):
                if i < len(self.canvas.panel_names):
                    self.canvas.panel_names[i] = name

            # Panel configs
            p_cfgs = data.get("panel_configs", [])
            for i, cfg in enumerate(p_cfgs):
                if i < len(self.canvas.panel_configs):
                    self.canvas.panel_configs[i].update(cfg)

            # Layout combo güncelle
            self.combo_layout.blockSignals(True)
            label = f"{rows}×{cols_l}"
            idx = self.combo_layout.findText(label, Qt.MatchFlag.MatchStartsWith)
            self.combo_layout.setCurrentIndex(idx if idx >= 0 else 0)
            self.combo_layout.blockSignals(False)

            # Seriler
            self.data_manager.series_list.clear()
            self.lst_ser.clear()
            for s in data.get("series", []):
                s.setdefault('panel_id', 0)
                s['x'] = np.array(s['x'])
                s['y'] = np.array(s['y'])
                if s.get('x_err') is not None:
                    s['x_err'] = np.array(s['x_err'])
                if s.get('y_err') is not None:
                    s['y_err'] = np.array(s['y_err'])
                self.data_manager.series_list.append(s)

            # Fitler
            self.fit_list = []
            self.lst_fits.clear()
            self.lst_report_fits.clear()
            for f_item in data.get("fits", []):
                f_item.setdefault('panel_id', 0)
                f_item['x'] = np.array(f_item['x'])
                f_item['y'] = np.array(f_item['y'])
                if f_item.get('res_x') is not None:
                    f_item['res_x'] = np.array(f_item['res_x'])
                if f_item.get('res_y') is not None:
                    f_item['res_y'] = np.array(f_item['res_y'])
                self.fit_list.append(f_item)
                self.lst_fits.addItem(f_item['label'])
                pid = f_item.get('panel_id', 0)
                panel_name = self.canvas.panel_names[pid] if pid < len(self.canvas.panel_names) else f"Ax{pid+1}"
                mn = f_item.get('model_name', f_item.get('label', ''))
                src = f_item.get('source_series', '')
                self.lst_report_fits.addItem(f"{mn} → {src}  [{panel_name}]")

            self.text_items = list(data.get("text_items", []))
            max_tid = 0
            for it in self.text_items:
                tid = int(it.get("id", 0) or 0)
                if tid <= 0:
                    tid = max_tid + 1
                    it["id"] = tid
                max_tid = max(max_tid, tid)
            self._next_text_item_id = max(1, max_tid + 1)
            saved_auto = data.get("text_auto_cfg", {})
            if isinstance(saved_auto, dict):
                self.text_auto_cfg.update(saved_auto)
            self._populate_auto_label_style_combo()
            self._populate_auto_label_preset_combo()
            self._load_auto_label_controls()
            self._refresh_text_list()

            self._refresh_panel_list()
            self._refresh_series_list()
            self.redraw_plot()

            # Global states'i dialog instance'ına geri yükle
            saved_gs = data.get("global_states", {})
            if saved_gs:
                gs_int = {int(k): v for k, v in saved_gs.items()}
                if not hasattr(self, '_settings_dlg') or self._settings_dlg is None:
                    self._settings_dlg = PlotSettingsDialog(self, self)
                self._settings_dlg._global_states = gs_int
                # Mevcut aktif panel için state'i hemen widget'lara yükle
                self._settings_dlg._load_global_state(self.canvas.active_index)

            if self.fit_list:
                self.lst_report_fits.setCurrentRow(len(self.fit_list) - 1)

            QMessageBox.information(self, t("msg_success"), t("msg_load_ok"))
            self._current_project_path = (
                None if loaded_project.requires_save_as else f
            )
            self._remember_dialog_path(f)
            self._is_modified = False
        except ProjectSchemaError:
            QMessageBox.critical(
                self,
                t("msg_error"),
                t("msg_project_schema_error"),
            )
        except Exception as e:
            QMessageBox.critical(self, t("msg_error"), t("msg_load_error").format(err=str(e)))


    def append_cols_action(self):
        """Mevcut df'e sagdan yeni sutunlar ekler."""
        if self.data_manager.df is None:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data_to_append"))
            return

        f, _ = QFileDialog.getOpenFileName(
            self, t("dlg_append_cols"), self._dialog_start_path(),
            t("dlg_data_filter")
        )
        if not f:
            return
        self._remember_dialog_path(f)

        dlg = DataImportDialog(f, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self._clear_last_table_undo()

        new_df = dlg.df
        existing_df = self.data_manager.df

        # Cakisan sutun adlarini yeniden adlandir: Stress -> Stress_2, Stress_3 ...
        existing_cols = set(str(c) for c in existing_df.columns)
        final_cols = []
        renamed = {}
        for col in new_df.columns:
            col_str = str(col)
            if col_str in existing_cols:
                n = 2
                while f"{col_str}_{n}" in existing_cols:
                    n += 1
                new_col = f"{col_str}_{n}"
                renamed[col_str] = new_col
                existing_cols.add(new_col)
                final_cols.append(new_col)
            else:
                existing_cols.add(col_str)
                final_cols.append(col_str)
        new_df = new_df.copy()
        new_df.columns = final_cols

        # Boyut farki: pd.concat axis=1 ile NaN doldurur otomatik
        merged = pd.concat(
            [existing_df.reset_index(drop=True),
             new_df.reset_index(drop=True)],
            axis=1
        )
        self.data_manager.df = merged
        self._sync_column_roles_with_df(reset=False)

        numeric_cols = [str(c) for c in merged.columns
                        if pd.api.types.is_numeric_dtype(merged[c])]
        all_cols = [str(c) for c in merged.columns]

        # Veri tablosunu tam yenile
        tw = self.table_w
        tw.setUpdatesEnabled(False)
        tw.blockSignals(True)
        tw.clearContents()
        tw.setRowCount(merged.shape[0])
        tw.setColumnCount(merged.shape[1])
        self._apply_table_headers_with_roles()
        for i in range(merged.shape[0]):
            for j in range(merged.shape[1]):
                tw.setItem(i, j, QTableWidgetItem(str(merged.iat[i, j])))
        tw.blockSignals(False)
        tw.setUpdatesEnabled(True)
        tw.viewport().update()
        self._rebuild_role_combo_row()

        # Combo'lara yeni sutunlar dahil edilsin, eskiler korunsun
        cur_x    = self.combo_x.currentText()
        cur_xerr = self.combo_x_err.currentText()
        cur_y    = self.combo_y.currentText()
        cur_yerr = self.combo_y_err.currentText()

        for combo in (self.combo_x, self.combo_y):
            combo.blockSignals(True)
            combo.clear()
            if combo is self.combo_x:
                combo.addItem(t("auto_x_label"))
                combo.addItems(all_cols)   # X: metin sütunlar dahil
            else:
                combo.addItems(numeric_cols)
            combo.blockSignals(False)

        for combo, saved in ((self.combo_x, cur_x), (self.combo_y, cur_y)):
            idx = combo.findText(saved)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        for combo, saved in ((self.combo_x_err, cur_xerr), (self.combo_y_err, cur_yerr)):
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Yok")
            combo.addItems(numeric_cols)
            combo.blockSignals(False)
            idx = combo.findText(saved)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        self.lst_y_select.blockSignals(True)
        self.lst_y_select.clear()
        self.lst_y_select.addItems(numeric_cols)
        self.lst_y_select.blockSignals(False)

        # Kullaniciyi bilgilendir
        n_new = len(final_cols)
        msg_parts = [t("msg_append_cols_ok").format(n=n_new)]
        if renamed:
            rn_str = ", ".join(f"{k} -> {v}" for k, v in renamed.items())
            msg_parts.append(t("msg_append_renamed").format(cols=rn_str))
        QMessageBox.information(self, t("msg_success"), "\n".join(msg_parts))
        self.mark_modified()

    def load_data_action(self):
        f, _ = QFileDialog.getOpenFileName(
            self, t("dlg_open_data"), self._dialog_start_path(),
            t("dlg_data_filter")
        )
        if not f:
            return
        self._remember_dialog_path(f)

        dlg = DataImportDialog(f, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self._clear_last_table_undo()
        self._current_project_path = None

        df = dlg.df
        col_types = dlg.col_types  # {col: 'numeric'|'text'}

        # DataManager'a aktar
        self.data_manager.df = df
        self.data_manager.series_list.clear()
        self._sync_column_roles_with_df(reset=True)

        # Sütunları tipe göre ayır
        numeric_cols = [str(c) for c in df.columns
                        if col_types.get(str(c), 'numeric') == 'numeric']
        all_cols = [str(c) for c in df.columns]

        # Veri tablosunu güncelle
        self.table_w.setRowCount(df.shape[0])
        self.table_w.setColumnCount(df.shape[1])
        self._apply_table_headers_with_roles()
        self.table_w.blockSignals(True)
        for i in range(min(df.shape[0], 200)):
            for j in range(df.shape[1]):
                self.table_w.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        self.table_w.blockSignals(False)
        self._rebuild_role_combo_row()

        # Combo'ları güncelle — sadece sayısal sütunlar X/Y'ye gider
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_x_err.clear()
        self.combo_y_err.clear()
        self.lst_y_select.clear()

        self.combo_x.addItem(t("auto_x_label"))
        self.combo_x.addItems(all_cols)   # X: metin sütunlar dahil
        self.combo_y.addItems(numeric_cols)
        self.combo_x_err.addItem("Yok")
        self.combo_x_err.addItems(numeric_cols)
        self.combo_y_err.addItem("Yok")
        self.combo_y_err.addItems(numeric_cols)
        self.lst_y_select.addItems(numeric_cols)

        if len(numeric_cols) > 1:
            self.combo_y.setCurrentIndex(1)

        # Eski serileri temizle
        self.lst_ser.clear()
        self.lst_fits.clear()
        self.lst_report_fits.clear()
        self.fit_list.clear()
        self.text_items.clear()
        self._refresh_text_list()
        self.canvas.clear_plot()
        self._clear_report()
        self.mark_modified()

    # --------------------------------------------------
    # Seri / Toplu Ekleme
    # --------------------------------------------------
    def add_series_left(self):
        self._add_series('left')

    def add_series_right(self):
        self._add_series('right')

    def _add_series(self, axis: str):
        """Tekli veya çoklu Y seçimine ve plot tipine göre seri ekler."""
        # 0=scatter, 1=line, 2=scatter+line, 3=bar, 4=histogram
        idx = self.combo_plot_type.currentIndex()
        if idx == 4:
            plot_type = 'histogram'
        elif idx == 3:
            plot_type = 'bar'
        else:
            plot_type = 'scatter'  # scatter, line, scatter+line hepsi 'scatter' tipinde

        # Marker ve linestyle seçime göre belirlenir
        if idx == 0:    # Sadece scatter
            default_marker, default_line = next(MARKER_CYCLE), 'None'
        elif idx == 1:  # Sadece line
            default_marker, default_line = 'None', '-'
        elif idx == 2:  # Scatter + Line
            default_marker, default_line = next(MARKER_CYCLE), '-'
        else:
            default_marker, default_line = next(MARKER_CYCLE), 'None'

        df = self.data_manager.df
        if df is None or df.empty:
            return

        xc = self.combo_x.currentText().strip()
        if not xc and plot_type != 'histogram':
            return
        selected = self.lst_y_select.selectedItems()
        y_cols = [it.text().strip() for it in selected if it.text().strip()]
        if plot_type != 'histogram':
            y_cols = [yc for yc in y_cols if yc != xc]
        if not y_cols:
            return
        pairs = []
        if plot_type == "histogram":
            for yc in y_cols:
                pairs.append((None, yc))
        else:
            auto_x = (xc == t("auto_x_label"))
            x_col_arg = None if auto_x else xc
            for yc in y_cols:
                pairs.append((x_col_arg, yc))

        prefix = self.inp_series_label.text().strip()
        xe = self.combo_x_err.currentText()
        ye = self.combo_y_err.currentText()
        pid = self.canvas.active_index
        added = 0
        skipped_duplicates = 0
        skipped_invalid_x = []
        multi = len(pairs) > 1

        for x_col_arg, yc in pairs:
            # scatter/line için x sütunu numeric olmalı (auto-x hariç)
            if plot_type == "scatter" and x_col_arg is not None:
                if x_col_arg in df.columns and not pd.api.types.is_numeric_dtype(df[x_col_arg]):
                    skipped_invalid_x.append(x_col_arg)
                    continue

            # bar için auto-x desteklenmiyor; x zorunlu
            if plot_type == "bar" and x_col_arg is None:
                continue

            if self._series_exists(pid, axis, plot_type, x_col_arg, yc):
                skipped_duplicates += 1
                continue

            st = {
                'color': next(_COLOR_CYCLE_state['cycle']),
                'marker': default_marker,
                'linestyle': default_line,
                'markersize': 5,
                'markeredgewidth': 0.5,
                'linewidth': 1.0,
                'capsize': 2,
                'elinewidth': 1.0,
                'filled': True,
                'alpha': 0.7 if plot_type == 'histogram' else 1.0,
                'bins': 20,
                'bar_width': 0.8,
                'edgecolor': 'white' if plot_type == 'histogram' else 'none',
            }
            s = self.data_manager.create_series(
                x_col_arg,
                yc, axis, st, panel_id=pid, plot_type=plot_type
            )
            if not s:
                continue

            if prefix:
                s['label'] = prefix if not multi else f"{prefix} - {yc}"
            else:
                s['label'] = yc

            s['x_col'] = x_col_arg
            s['y_col'] = yc

            if plot_type in ('scatter', 'bar'):
                y_raw = pd.to_numeric(df[yc], errors='coerce').values
                auto_x = (x_col_arg is None)
                if auto_x:
                    mask = ~np.isnan(y_raw)
                    s['x'] = np.arange(1, int(np.sum(mask)) + 1)
                    s['y'] = y_raw[mask]
                elif x_col_arg:
                    if plot_type == 'bar':
                        x_raw = df[x_col_arg].values
                        mask = ~pd.isna(x_raw) & ~np.isnan(y_raw)
                    else:
                        x_raw = pd.to_numeric(df[x_col_arg], errors='coerce').values
                        mask = ~np.isnan(x_raw) & ~np.isnan(y_raw)
                else:
                    mask = ~np.isnan(y_raw)

                if not auto_x:
                    if xe != "Yok" and plot_type == 'scatter':
                        xe_raw = pd.to_numeric(df[xe], errors='coerce').values
                        s['x_err'] = xe_raw[mask]
                        s['x_err_col'] = xe
                    if ye != "Yok":
                        ye_raw = pd.to_numeric(df[ye], errors='coerce').values
                        s['y_err'] = ye_raw[mask]
                        s['y_err_col'] = ye

            self.lst_ser.addItem(s['label'])
            added += 1

        if skipped_invalid_x:
            bad = ", ".join(sorted(set(skipped_invalid_x)))
            QMessageBox.warning(
                self,
                t("msg_warning"),
                t("msg_x_must_be_numeric").format(col=bad),
            )
        if skipped_duplicates:
            self.statusBar().showMessage(t("status_skipped_duplicate_series", n=skipped_duplicates), 2500)

        if added:
            self.mark_modified()
            self.redraw_plot()
            self.inp_series_label.clear()

    def _add_series_from_roles(self):
        """Tablo üstündeki rol atamalarından serileri güvenli/atomik şekilde ekler."""
        df = self.data_manager.df
        if df is None or df.empty:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return

        idx = self.combo_table_plot_type.currentIndex() if hasattr(self, "combo_table_plot_type") else self.combo_plot_type.currentIndex()
        if idx == 4:
            plot_type = "histogram"
        elif idx == 3:
            plot_type = "bar"
        else:
            plot_type = "scatter"

        if idx == 0:
            default_marker, default_line = next(MARKER_CYCLE), 'None'
        elif idx == 1:
            default_marker, default_line = 'None', '-'
        elif idx == 2:
            default_marker, default_line = next(MARKER_CYCLE), '-'
        else:
            default_marker, default_line = next(MARKER_CYCLE), 'None'

        specs, errors = self._build_role_series_specs(plot_type)
        if errors:
            QMessageBox.warning(self, t("msg_warning"), "\n".join(f"• {e}" for e in errors))
            return
        if not specs:
            QMessageBox.warning(self, t("msg_warning"), t("msg_role_empty"))
            return

        pid = self.canvas.active_index
        seen = set()
        duplicate_errors = []
        for spec in specs:
            key = (
                pid,
                spec["axis"],
                plot_type,
                spec.get("x_col"),
                spec["y_col"],
                spec.get("x_err_col"),
                spec.get("y_err_col"),
            )
            if key in seen or self._series_exists(
                pid,
                spec["axis"],
                plot_type,
                spec.get("x_col"),
                spec["y_col"],
                spec.get("x_err_col"),
                spec.get("y_err_col"),
            ):
                duplicate_errors.append(t("msg_role_duplicate_series", y=spec["y_col"], axis=spec["axis"]))
            seen.add(key)
        if duplicate_errors:
            QMessageBox.warning(self, t("msg_warning"), "\n".join(f"• {e}" for e in sorted(set(duplicate_errors))))
            return

        prefix = self.inp_series_label.text().strip()
        start_len = len(self.series_list)
        added = 0
        try:
            for k, spec in enumerate(specs, start=1):
                st = {
                    'color': next(_COLOR_CYCLE_state['cycle']),
                    'marker': default_marker,
                    'linestyle': default_line,
                    'markersize': 5,
                    'markeredgewidth': 0.5,
                    'linewidth': 1.0,
                    'capsize': 2,
                    'elinewidth': 1.0,
                    'filled': True,
                    'alpha': 0.7 if plot_type == 'histogram' else 1.0,
                    'bins': 20,
                    'bar_width': 0.8,
                    'edgecolor': 'white' if plot_type == 'histogram' else 'none',
                }
                s = self.data_manager.create_series(
                    spec.get("x_col"),
                    spec["y_col"],
                    spec["axis"],
                    st,
                    panel_id=pid,
                    plot_type=plot_type,
                )
                if not s:
                    raise ValueError(t("msg_role_series_create_failed", y=spec["y_col"]))

                label_base = spec["y_col"]
                if prefix:
                    label_base = prefix if len(specs) == 1 else f"{prefix} - {spec['y_col']}"
                s["label"] = label_base
                s["x_col"] = spec.get("x_col")
                s["y_col"] = spec["y_col"]
                s["x_err_col"] = spec.get("x_err_col")
                s["y_err_col"] = spec.get("y_err_col")

                if plot_type in ("scatter", "bar"):
                    y_raw = pd.to_numeric(df[spec["y_col"]], errors="coerce").values
                    x_col = spec.get("x_col")
                    if x_col is None:
                        mask = ~np.isnan(y_raw)
                        s["x"] = np.arange(1, int(np.sum(mask)) + 1)
                        s["y"] = y_raw[mask]
                    elif plot_type == "bar":
                        x_raw = df[x_col].values
                        mask = ~pd.isna(x_raw) & ~np.isnan(y_raw)
                    else:
                        x_raw = pd.to_numeric(df[x_col], errors="coerce").values
                        mask = ~np.isnan(x_raw) & ~np.isnan(y_raw)

                    if x_col is not None and plot_type == "bar":
                        s["x"] = x_raw[mask]
                        s["y"] = y_raw[mask]
                    elif x_col is not None and plot_type == "scatter":
                        s["x"] = x_raw[mask]
                        s["y"] = y_raw[mask]

                    x_err_col = spec.get("x_err_col")
                    y_err_col = spec.get("y_err_col")
                    if plot_type == "scatter" and x_err_col:
                        xerr_raw = pd.to_numeric(df[x_err_col], errors="coerce").values
                        s["x_err"] = xerr_raw[mask]
                    if y_err_col:
                        yerr_raw = pd.to_numeric(df[y_err_col], errors="coerce").values
                        s["y_err"] = yerr_raw[mask]

                self.lst_ser.addItem(s["label"])
                added += 1
        except Exception as exc:
            del self.series_list[start_len:]
            self._refresh_series_list()
            QMessageBox.warning(self, t("msg_warning"), t("msg_role_atomic_failed", err=str(exc)))
            return

        if added:
            self.mark_modified()
            self.redraw_plot()
            self.inp_series_label.clear()
            self.statusBar().showMessage(t("status_role_add_done", n=added), 2500)

    # Geriye dönük uyumluluk
    def _add_single_series(self, ax: str):
        self._add_series(ax)

    def add_multiple_series_left(self):
        self._add_series('left')

    def add_multiple_series_right(self):
        self._add_series('right')

    def remove_series_action(self):
        r = self.lst_ser.currentRow()
        if r != -1:
            pid = self.canvas.active_index
            self.data_manager.remove_series_from_panel(pid, r)
            self.lst_ser.takeItem(r)
            self.mark_modified()
            self.redraw_plot()

    def rename_series_action(self, item):
        pid = self.canvas.active_index
        row = self.lst_ser.row(item)
        panel_series = self.data_manager.get_series_for_panel(pid)
        if row >= len(panel_series):
            return
        old_name = item.text()
        new_name, ok = self._open_rename_dialog(t("dlg_rename_series"), t("dlg_rename_prompt"), old_name)
        if ok and new_name:
            panel_series[row]['label'] = new_name
            item.setText(new_name)
            self.redraw_plot()

    def rename_fit_action(self, item):
        row = self.lst_fits.row(item)
        old_name = item.text()
        new_name, ok = self._open_rename_dialog(t("dlg_rename_series"), t("dlg_rename_fit_prompt"), old_name)
        if ok and new_name:
            self.fit_list[row]['label'] = new_name
            item.setText(new_name)
            self.redraw_plot()

    def remove_fit_action(self):
        r = self.lst_fits.currentRow()
        if r != -1:
            del self.fit_list[r]
            self.lst_fits.takeItem(r)
            self.lst_report_fits.takeItem(r)
            self.redraw_plot()
            if len(self.fit_list) == 0:
                self._clear_report()
            else:
                # Bir önceki veya ilk fiti seç
                new_row = max(0, r - 1)
                self.lst_report_fits.setCurrentRow(new_row)

    # --------------------------------------------------
    # Fit Models
    # --------------------------------------------------
    def _get_models_dir(self) -> str:
        """
        PyInstaller modunda bundle içindeki models/ klasörünü,
        geliştirici modunda projenin models/ klasörünü döndürür.
        """
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstaller — bundle read-only, models _MEIPASS içinde
            base = sys._MEIPASS
        else:
            # Geliştirici modu — bu dosyanın konumuna göre
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)
            ))))
        return os.path.join(base, 'models')

    def populate_models(self):
        models_dir = self._get_models_dir()
        # Geliştirici modunda klasör yoksa oluştur (bundle'da asla yazma)
        import sys
        if not getattr(sys, 'frozen', False):
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
        self.combo_mod.clear()
        self.loaded_models.clear()
        self._model_meta.clear()
        lang = get_language()
        if not os.path.exists(models_dir):
            return
        self.combo_mod.addItem(t("model_select_placeholder"))
        for f in sorted(os.listdir(models_dir)):
            if f.endswith(".py") and f != "__init__.py":
                try:
                    n = f[:-3]
                    s = importlib.util.spec_from_file_location(n, os.path.join(models_dir, f))
                    m = importlib.util.module_from_spec(s)
                    s.loader.exec_module(m)
                    if hasattr(m, 'model'):
                        # Dile göre isim/açıklama/parametre seç
                        if lang == 'en':
                            display_name = getattr(m, 'NAME_EN', getattr(m, 'NAME', n))
                            description  = getattr(m, 'DESCRIPTION_EN', getattr(m, 'DESCRIPTION', ''))
                            param_names  = getattr(m, 'PARAM_NAMES_EN', getattr(m, 'PARAM_NAMES', None))
                        else:
                            display_name = getattr(m, 'NAME', n)
                            description  = getattr(m, 'DESCRIPTION', '')
                            param_names  = getattr(m, 'PARAM_NAMES', None)

                        self.loaded_models[display_name] = m.model
                        self._model_meta[display_name] = {
                            'description': description,
                            'param_names': param_names,
                            'file': n,
                        }
                        self.combo_mod.addItem(display_name)
                except Exception:
                    pass

    def perform_fit(self):
        r = self.lst_ser.currentRow()
        if r == -1:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_series"))
            return
        mn = self.combo_mod.currentText()
        if not mn or mn not in self.loaded_models:
            QMessageBox.warning(self, t("msg_warning"), t("msg_select_model"))
            return
        func = self.loaded_models[mn]
        meta = self._model_meta.get(mn, {})

        # Parametre isimleri: PARAM_NAMES varsa onu kullan, yoksa fonksiyon signature'dan al
        raw_pn = list(inspect.signature(func).parameters.keys())[1:]
        display_pn = meta.get('param_names') or raw_pn

        dt = meta.get('description') or func.__doc__ or ""
        d = FitDialog(display_pn, dt, self)
        if not d.exec():
            return
        try:
            p0 = d.get_values()
            pid = self.canvas.active_index
            panel_series = self.data_manager.get_series_for_panel(pid)
            if r >= len(panel_series):
                QMessageBox.warning(self, t("msg_warning"), t("msg_no_series"))
                return
            s = panel_series[r]
            x, y = prepare_fit_xy(s.get("x", []), s.get("y", []))

            if self.fit_xrange:
                msk = (x >= self.fit_xrange[0]) & (x <= self.fit_xrange[1])
                x, y = x[msk], y[msk]
            if x.size < 2 or y.size < 2:
                raise ValueError(t("fit_insufficient_data"))
            idx = np.argsort(x)
            x, y = x[idx], y[idx]
            if np.unique(x).size < 2:
                raise ValueError(t("fit_distinct_x"))
            def checked_model(values, *parameters):
                return evaluate_fit_model(func, values, parameters)

            with warnings.catch_warnings(record=True) as fit_warnings:
                warnings.simplefilter("always", OptimizeWarning)
                popt, pcov = curve_fit(checked_model, x, y, p0=p0, method='trf', maxfev=5000)
            if not np.isfinite(popt).all():
                raise ValueError(t("fit_invalid_result"))
            xf = np.linspace(x.min(), x.max(), 500)
            yf = evaluate_fit_model(func, xf, popt)
            y_pred = evaluate_fit_model(func, x, popt)
            resid, r2, stats = fit_statistics(y, y_pred)
            fit_obj = {
                'label': f"Fit: {mn}",
                'x': xf, 'y': yf,
                'color': s['color'],
                'axis': s['axis'],
                'panel_id': pid,
                'linewidth': 1.0, 'linestyle': '-', 'marker': 'None', 'markersize': 0,
                'model_name': mn,
                'model_description': meta.get('description', ''),
                'param_names': display_pn,
                'param_values': [float(v) for v in popt],
                'source_series': s.get('label', '')
            }

            fit_obj['res_x'] = x
            fit_obj['res_y'] = resid
            fit_obj['r2'] = r2
            fit_obj['res_stats'] = stats

            self.fit_list.append(fit_obj)
            self.lst_fits.addItem(f"{mn} -> {s['label']}")

            # Analiz Raporu listesine de ekle
            panel_name = self.canvas.panel_names[pid]
            self.lst_report_fits.addItem(f"{mn} → {s['label']}  [{panel_name}]")
            self.lst_report_fits.setCurrentRow(self.lst_report_fits.count() - 1)

            self.mark_modified()
            self.redraw_plot()
            if not np.isfinite(pcov).all() or any(
                issubclass(warning.category, OptimizeWarning) for warning in fit_warnings
            ):
                QMessageBox.warning(self, t("msg_warning"), t("fit_covariance_warning"))

        except Exception as e:
            QMessageBox.warning(self, t("msg_warning"), t("msg_fit_error").format(error=str(e)))

    # --------------------------------------------------
    # Residuals
    # --------------------------------------------------
    # --------------------------------------------------
    # Analiz Raporu
    # --------------------------------------------------
    def _on_report_fit_selected(self, row: int):
        """Rapor listesinde fit seçilince bilgi ve grafiği güncelle."""
        if row < 0 or row >= len(self.fit_list):
            self._clear_report()
            return
        self._update_report(self.fit_list[row])

    def on_fit_selection_changed(self, row: int):
        """Sol paneldeki fit listesi değişince raporu da güncelle."""
        if row is None or row < 0 or row >= len(self.fit_list):
            return
        self.lst_report_fits.blockSignals(True)
        self.lst_report_fits.setCurrentRow(row)
        self.lst_report_fits.blockSignals(False)
        self._update_report(self.fit_list[row])

    def _clear_report(self):
        self.report_info.clear()
        if hasattr(self, 'resid_canvas'):
            self.resid_canvas.axes.cla()
            self.resid_canvas.draw()

    def clear_residuals_tab(self):
        """Geriye dönük uyumluluk."""
        self._clear_report()

    def update_residuals_tab(self, fit_obj: dict):
        """Geriye dönük uyumluluk."""
        self._update_report(fit_obj)

    def _copy_report_to_clipboard(self):
        from PyQt6.QtCore import QTimer
        text = self.report_info.toPlainText()
        if text.strip():
            QApplication.clipboard().setText(text)
            self.lbl_copy_status.setText(t("report_copied"))
            QTimer.singleShot(3000, lambda: self.lbl_copy_status.setText("✓"))

    def _update_report(self, fit_obj: dict):
        """Seçili fit için bilgi kutusunu ve residual grafiğini günceller."""
        if not hasattr(self, 'report_info') or fit_obj is None:
            return

        rx  = fit_obj.get('res_x')
        ry  = fit_obj.get('res_y')
        stats      = fit_obj.get('res_stats') or {}
        model_name = fit_obj.get('model_name', fit_obj.get('label', ''))
        src        = fit_obj.get('source_series', '')
        pid        = fit_obj.get('panel_id', 0)
        panel_name = self.canvas.panel_names[pid] if pid < len(self.canvas.panel_names) else f"Ax{pid+1}"

        # --- Bilgi kutusu ---
        lines = [
            f"{t('report_lbl_model'):<8}: {model_name}",
        ]
        desc = fit_obj.get('model_description', '')
        if desc:
            formula = desc.split('|')[0].strip() if '|' in desc else desc
            lines.append(f"{t('report_lbl_formula'):<8}: {formula}")

        lines += [
            f"{t('report_lbl_series'):<8}: {src}",
            f"{t('report_lbl_panel'):<8}: {panel_name}",
        ]

        # Parametre isimleri ve değerleri
        pnames = fit_obj.get('param_names', [])
        pvalues = fit_obj.get('param_values', [])
        if pnames and pvalues:
            lines.append("─" * 34)
            for pn, pv in zip(pnames, pvalues):
                lines.append(f"  {pn:<20}: {pv:.6g}")

        if stats:
            n    = int(stats.get('n', 0))
            mean = float(stats.get('mean', 0.0))
            std  = float(stats.get('std',  0.0))
            rmse = float(stats.get('rmse', 0.0))
            r2 = fit_obj.get('r2')
            r2_str = (t("report_r2_undefined") if 'r2' in fit_obj and r2 is None
                      else f"{r2:.6f}" if r2 is not None and np.isfinite(r2) else "—")
            lines += [
                "─" * 34,
                f"  {t('report_lbl_n'):<20}: {n}",
                f"  {t('report_lbl_r2'):<20}: {r2_str}",
                f"  {t('report_lbl_rmse'):<20}: {rmse:.4e}",
                f"  {t('report_lbl_mean'):<20}: {mean:.4e}",
                f"  {t('report_lbl_std'):<20}: {std:.4e}",
            ]

        self.report_info.setPlainText("\n".join(lines))

        # --- Residual grafiği ---
        ax = self.resid_canvas.axes
        ax.cla()

        if rx is None or ry is None:
            ax.text(0.5, 0.5, "Residual verisi yok",
                    ha='center', va='center', transform=ax.transAxes,
                    fontsize=10, color='gray')
            self.resid_canvas.draw()
            return

        cfg = self.canvas.panel_configs[min(pid, len(self.canvas.panel_configs) - 1)]
        tick_fs  = cfg.get('size_tick',  9)
        label_fs = cfg.get('size_label', 9)

        ax.axhline(0.0, color='gray', linewidth=0.8, linestyle='--')
        ax.plot(rx, ry, linestyle='None', marker='o',
                markersize=3, color=fit_obj.get('color', 'steelblue'),
                linewidth=fit_obj.get('linewidth', 1.0),
                markeredgewidth=0.5, markeredgecolor='white')

        ax.set_title(t("resid_title", model=model_name), fontsize=label_fs + 1, pad=4)
        ax.set_xlabel(cfg.get('xlabel', 'X'), fontsize=label_fs, labelpad=2)
        ax.set_ylabel(t("resid_ylabel"), fontsize=label_fs, labelpad=2)
        ax.tick_params(axis='both', which='both', labelsize=tick_fs)

        for spine in ax.spines.values():
            spine.set_linewidth(0.8)

        self.resid_canvas.fig.tight_layout(pad=0.8)
        self.resid_canvas.draw()

    # --------------------------------------------------
    # REDRAW — tüm panelleri çizer
    # --------------------------------------------------
    def redraw_plot(self):
        cc = self.canvas_config
        dpi = 150
        w_inch = cc.get('width_cm', 10.0) / 2.54
        h_inch = cc.get('height_cm', 8.0) / 2.54

        self.canvas.fig.set_size_inches(w_inch, h_inch)
        self.canvas.setFixedSize(int(w_inch * dpi), int(h_inch * dpi))

        # Tüm axes içeriklerini temizle, ax2'leri sıfırla
        for i in range(self.canvas.panel_count):
            self.canvas.axes_list[i].cla()
            if self.canvas.axes2_list[i]:
                try:
                    self.canvas.axes2_list[i].remove()
                except Exception:
                    pass
                self.canvas.axes2_list[i] = None

        self._span_selectors = []

        # Figure-level rcParams
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['mathtext.fontset'] = 'cm'
        plt.rcParams['mathtext.rm'] = 'serif'

        def _apply_tick_notation(ax_obj, axis: str, mode: str, sci_style: str, is_log: bool):
            """axis: 'x' | 'y', mode: auto|offset|scientific"""
            axis_obj = ax_obj.xaxis if axis == 'x' else ax_obj.yaxis
            if is_log:
                return

            if mode == "auto":
                sf = ticker.ScalarFormatter(useMathText=True)
                sf.set_useOffset(True)
                axis_obj.set_major_formatter(sf)
                axis_obj.offsetText.set_visible(True)
                return

            if mode in ("e", "pow10", "scientific"):
                use_e_style = (mode == "e") or (mode == "scientific" and sci_style == "e")
                if use_e_style:
                    axis_obj.set_major_formatter(ticker.FormatStrFormatter("%.3e"))
                    axis_obj.offsetText.set_visible(False)
                    return

                def _fmt_tick(v, _pos):
                    if np.isclose(v, 0.0):
                        return "0"
                    exp = int(np.floor(np.log10(abs(v))))
                    mant = v / (10 ** exp)
                    return rf"${mant:.3g}\times10^{{{exp}}}$"

                axis_obj.set_major_formatter(ticker.FuncFormatter(_fmt_tick))
                axis_obj.offsetText.set_visible(False)
                return

            if mode == "e_offset":
                sf = ticker.ScalarFormatter(useMathText=False)
                sf.set_scientific(True)
                sf.set_powerlimits((-3, 3))
                sf.set_useOffset(True)
                axis_obj.set_major_formatter(sf)
                axis_obj.offsetText.set_visible(True)
                return

            # mode == pow10_offset / offset
            sf = ticker.ScalarFormatter(useMathText=(sci_style == "pow10"))
            sf.set_scientific(True)
            sf.set_powerlimits((-3, 3))
            sf.set_useOffset(True)
            axis_obj.set_major_formatter(sf)
            axis_obj.offsetText.set_visible(True)

        def _apply_offset_text_size(ax_obj, axis: str, size: float):
            axis_obj = ax_obj.xaxis if axis == 'x' else ax_obj.yaxis
            try:
                axis_obj.offsetText.set_fontsize(size)
            except Exception:
                pass

        def _legend_label_for(obj: dict) -> str:
            if not obj.get("legend_show", True):
                return "_nolegend_"
            lbl = str(obj.get("legend_label", obj.get("label", "")) or "").strip()
            if not lbl:
                lbl = str(obj.get("label", "") or "")
            return lbl if lbl else "_nolegend_"

        def _legend_entries_sorted_by_order(panel_series: list[dict], panel_fits: list[dict]):
            desired = []
            seq = 0
            for obj in panel_series + panel_fits:
                lbl = _legend_label_for(obj)
                if lbl == "_nolegend_":
                    continue
                try:
                    ord_val = int(obj.get("legend_order", seq))
                except Exception:
                    ord_val = seq
                desired.append((lbl, ord_val, seq))
                seq += 1
            desired.sort(key=lambda x: (x[1], x[2]))
            per_label_order = {}
            for lbl, ord_val, seq_val in desired:
                per_label_order.setdefault(lbl, []).append((ord_val, seq_val))
            return per_label_order

        def _draw_grouped_bars(bar_series: list[dict], ax_left, ax_right):
            """Aynı X değerlerine sahip bar serilerini yan yana (grouped) çizer."""
            if not bar_series:
                return
            min_width = 1e-6

            def _norm_x(v):
                if isinstance(v, np.generic):
                    return v.item()
                return v

            def _is_numeric_scalar(v):
                if isinstance(v, (bool, np.bool_)):
                    return False
                return isinstance(v, (int, float, np.integer, np.floating))

            all_x_vals = []
            for s in bar_series:
                for xv in np.asarray(s.get("x", []), dtype=object):
                    xv = _norm_x(xv)
                    if pd.isna(xv):
                        continue
                    all_x_vals.append(xv)
            if not all_x_vals:
                return

            numeric_mode = all(_is_numeric_scalar(v) for v in all_x_vals)
            if numeric_mode:
                x_keys = sorted(set(float(v) for v in all_x_vals))
                x_centers = np.asarray(x_keys, dtype=float)
            else:
                seen = set()
                x_keys = []
                for v in all_x_vals:
                    key = str(v)
                    if key not in seen:
                        seen.add(key)
                        x_keys.append(key)
                x_centers = np.arange(len(x_keys), dtype=float)
            if x_centers.size == 0:
                return

            width_vals = []
            for s in bar_series:
                try:
                    width_vals.append(max(float(s.get("bar_width", 0.8)), min_width))
                except Exception:
                    width_vals.append(0.8)
            group_width = float(np.mean(width_vals)) if width_vals else 0.8
            group_width = max(group_width, min_width)
            if numeric_mode and x_centers.size > 1:
                diffs = np.diff(np.sort(x_centers))
                diffs = np.abs(diffs[np.isfinite(diffs)])
                diffs = diffs[diffs > 0]
                if diffs.size:
                    group_width = min(group_width, float(np.min(diffs)) * 0.9)
            else:
                group_width = min(group_width, 0.9)

            n_series = len(bar_series)
            single_width = max(group_width / max(n_series, 1), min_width)
            offsets = (np.arange(n_series) - (n_series - 1) / 2.0) * single_width

            for i, s in enumerate(bar_series):
                t_ax = ax_right if (ax_right and s.get("axis") == "right") else ax_left
                x_vals = np.asarray(s.get("x", []), dtype=object)
                y_vals = np.asarray(s.get("y", []), dtype=float)
                yerr_src = s.get("y_err")
                yerr_vals = np.asarray(yerr_src, dtype=float) if yerr_src is not None else None

                y_map = {}
                yerr_map = {}
                n = min(len(x_vals), len(y_vals))
                for j in range(n):
                    xv = _norm_x(x_vals[j])
                    yv = y_vals[j]
                    if pd.isna(xv) or np.isnan(yv):
                        continue
                    key = float(xv) if numeric_mode else str(xv)
                    y_map[key] = float(yv)
                    if yerr_vals is not None and j < len(yerr_vals):
                        ev = yerr_vals[j]
                        if np.isfinite(ev):
                            yerr_map[key] = float(ev)

                y_plot = np.asarray([y_map.get(k, np.nan) for k in x_keys], dtype=float)
                yerr_plot = None
                if yerr_map:
                    yerr_plot = np.asarray([yerr_map.get(k, 0.0) for k in x_keys], dtype=float)

                filled = s.get("bar_filled", True)
                bar_color = s["color"] if filled else "none"
                bar_edge = s.get("edgecolor", "none") if filled else s["color"]
                bar_edgew = s.get("bar_edge_width", 1.0) if not filled else 0.5
                ecolor = s.get("ecolor", s["color"])
                t_ax.bar(
                    x_centers + offsets[i],
                    y_plot,
                    width=single_width * 0.92,
                    color=bar_color,
                    alpha=s.get("alpha", 1.0),
                    edgecolor=bar_edge,
                    linewidth=bar_edgew,
                    label=_legend_label_for(s),
                    yerr=yerr_plot,
                    capsize=s.get("capsize", 2.0) if yerr_plot is not None else 0,
                    error_kw={
                        "elinewidth": s.get("elinewidth", 1.0),
                        "ecolor": ecolor,
                        "capthick": s.get("elinewidth", 1.0),
                    },
                )

            if not numeric_mode:
                ax_left.set_xticks(x_centers)
                ax_left.set_xticklabels([str(k) for k in x_keys])

        math_parser = MathTextParser("path")
        math_fallback_notified = [False]

        # Her panel için çiz
        for panel_id in range(self.canvas.panel_count):
            cfg = self.canvas.panel_configs[panel_id]
            ax = self.canvas.axes_list[panel_id]

            plt.rcParams['font.serif'] = [cfg.get('fontfamily', 'Times New Roman')]
            plt.rcParams['xtick.major.size'] = cfg.get('tick_major_len', 3.0)
            plt.rcParams['xtick.major.width'] = cfg.get('tick_major_width', 1.0)
            plt.rcParams['ytick.major.size'] = cfg.get('tick_major_len', 3.0)
            plt.rcParams['ytick.major.width'] = cfg.get('tick_major_width', 1.0)
            plt.rcParams['xtick.minor.size'] = cfg.get('tick_minor_len', 2.0)
            plt.rcParams['xtick.minor.width'] = cfg.get('tick_minor_width', 0.8)
            plt.rcParams['ytick.minor.size'] = cfg.get('tick_minor_len', 2.0)
            plt.rcParams['ytick.minor.width'] = cfg.get('tick_minor_width', 0.8)

            panel_series = self.data_manager.get_series_for_panel(panel_id)
            panel_fits = [f for f in self.fit_list if f.get('panel_id', 0) == panel_id]

            has_right = (
                any(s.get('axis') == 'right' for s in panel_series) or
                any(f.get('axis') == 'right' for f in panel_fits)
            )

            ax2 = None
            if has_right:
                ax2 = ax.twinx()
                self.canvas.axes2_list[panel_id] = ax2
            bar_mode = str(cfg.get("bar_mode", "overlay")).lower()
            grouped_bars = []

            # Serileri çiz
            for s in panel_series:
                t_ax = ax2 if (ax2 and s['axis'] == 'right') else ax
                pt = s.get('plot_type', 'scatter')

                if pt == 'histogram':
                    t_ax.hist(
                        s['y'],
                        bins=s.get('bins', 20),
                        color=s['color'],
                        alpha=s.get('alpha', 0.7),
                        edgecolor=s.get('edgecolor', 'white'),
                        label=_legend_label_for(s),
                    )

                elif pt == 'bar':
                    if bar_mode == "grouped":
                        grouped_bars.append(s)
                        continue
                    yerr = s.get('y_err')
                    filled = s.get('bar_filled', True)
                    bar_color  = s['color'] if filled else 'none'
                    bar_edge   = s.get('edgecolor', 'none') if filled else s['color']
                    bar_edgew  = s.get('bar_edge_width', 1.0) if not filled else 0.5
                    ecolor     = s.get('ecolor', s['color'])
                    t_ax.bar(
                        s['x'], s['y'],
                        width=s.get('bar_width', 0.8),
                        color=bar_color,
                        alpha=s.get('alpha', 1.0),
                        edgecolor=bar_edge,
                        linewidth=bar_edgew,
                        label=_legend_label_for(s),
                        yerr=yerr,
                        capsize=s.get('capsize', 2.0) if yerr is not None else 0,
                        error_kw={
                            'elinewidth': s.get('elinewidth', 1.0),
                            'ecolor': ecolor,
                            'capthick': s.get('elinewidth', 1.0),
                        },
                    )

                else:
                    # scatter / line — spline desteği ile
                    fc = s['color'] if s.get('filled', True) else 'none'
                    mk = s.get('marker', 'o')
                    mk = None if mk == 'None' else mk
                    # ls: matplotlib plot() için 'None' string çizgiyi gizler
                    ls_raw = s.get('linestyle', 'None')
                    ls = 'None' if (ls_raw == 'None' or ls_raw == '') else ls_raw

                    x_data, y_data = s['x'], s['y']
                    has_err = s.get('x_err') is not None or s.get('y_err') is not None

                    # Spline interpolasyonu
                    interp = s.get('interpolation', 'linear')
                    if ls != 'None' and interp == 'spline' and len(x_data) >= 4:
                        from scipy.interpolate import make_interp_spline
                        idx_sort = np.argsort(x_data)
                        xs, ys = x_data[idx_sort], y_data[idx_sort]
                        x_smooth = np.linspace(xs.min(), xs.max(), 300)
                        try:
                            spl = make_interp_spline(xs, ys, k=3)
                            y_smooth = spl(x_smooth)
                            # Semboller + hata çubukları (label yok)
                            if has_err:
                                t_ax.errorbar(
                                    x_data, y_data,
                                    xerr=s.get('x_err'), yerr=s.get('y_err'),
                                    fmt='none' if not mk else '',
                                    color=s['color'],
                                    marker=mk, linestyle='',
                                    markerfacecolor=fc,
                                    markeredgecolor=s['color'],
                                    markeredgewidth=s.get('markeredgewidth', 0.5),
                                    markersize=s.get('markersize', 5),
                                    capsize=s.get('capsize', 2.0),
                                    elinewidth=s.get('elinewidth', 1.0),
                                    ecolor=s.get('ecolor', s['color']),
                                )
                            else:
                                t_ax.plot(
                                    x_data, y_data,
                                    color=s['color'], marker=mk, linestyle='',
                                    markerfacecolor=fc,
                                    markeredgecolor=s['color'],
                                    markeredgewidth=s.get('markeredgewidth', 0.5),
                                    markersize=s.get('markersize', 5),
                                )
                            # Spline çizgisi — label burada, lejant çizgiyi göreceği için
                            t_ax.plot(x_smooth, y_smooth, color=s['color'],
                                      linewidth=s.get('linewidth', 1.0), linestyle=ls,
                                      label=_legend_label_for(s))
                        except Exception:
                            # Spline başarısız — düz çiz, lejant handle'ı plot ile
                            t_ax.plot(
                                x_data, y_data,
                                label=_legend_label_for(s), color=s['color'],
                                marker=mk, linestyle=ls,
                                linewidth=s.get('linewidth', 1.0),
                                markerfacecolor=fc,
                                markeredgecolor=s['color'],
                                markeredgewidth=s.get('markeredgewidth', 0.5),
                                markersize=s.get('markersize', 5),
                            )
                            if has_err:
                                t_ax.errorbar(
                                    x_data, y_data,
                                    xerr=s.get('x_err'), yerr=s.get('y_err'),
                                    fmt='none', color=s['color'],
                                    capsize=s.get('capsize', 2.0),
                                    elinewidth=s.get('elinewidth', 1.0),
                                    ecolor=s.get('ecolor', s['color']),
                                )
                    else:
                        # Normal (linear) çizim
                        # plot() ile çizersek lejant hem çizgi hem sembolü doğru gösterir
                        t_ax.plot(
                            x_data, y_data,
                            label=_legend_label_for(s),
                            color=s['color'],
                            marker=mk,
                            linestyle=ls,
                            linewidth=s.get('linewidth', 1.0),
                            markerfacecolor=fc,
                            markeredgecolor=s['color'],
                            markeredgewidth=s.get('markeredgewidth', 0.5),
                            markersize=s.get('markersize', 5),
                        )
                        if has_err:
                            t_ax.errorbar(
                                x_data, y_data,
                                xerr=s.get('x_err'), yerr=s.get('y_err'),
                                fmt='none', color=s['color'],
                                capsize=s.get('capsize', 2.0),
                                elinewidth=s.get('elinewidth', 1.0),
                                ecolor=s.get('ecolor', s['color']),
                            )

            if bar_mode == "grouped" and grouped_bars:
                _draw_grouped_bars(grouped_bars, ax, ax2)

            # Fitleri çiz
            for fit in panel_fits:
                t_ax = ax2 if (ax2 and fit['axis'] == 'right') else ax
                t_ax.plot(
                    fit['x'], fit['y'],
                    label=_legend_label_for(fit),
                    color=fit.get('color', 'red'),
                    linewidth=fit.get('linewidth', 1.0),
                    linestyle=fit.get('linestyle', '-'),
                    marker=fit.get('marker', None),
                    markersize=fit.get('markersize', 0)
                )

            # Eksen ayarları
            self.apply_axis_settings(ax, 'x', cfg)
            self.apply_axis_settings(ax, 'y', cfg)
            if ax2:
                self.apply_axis_settings(ax2, 'y', cfg, is_right=True)

            # Spine ayarları
            spine_w = cfg.get('spine_width', 1.0)
            spine_vis = {
                'bottom': cfg.get('spine_bottom', True),
                'top': cfg.get('spine_top', True),
                'left': cfg.get('spine_left', True),
                'right': cfg.get('spine_right', True),
            }
            for side, vis in spine_vis.items():
                ax.spines[side].set_visible(vis)
                ax.spines[side].set_linewidth(spine_w)

            # Tick yönleri
            ax.tick_params(
                top=cfg.get('tick_top', False),
                bottom=cfg.get('tick_bottom', True),
                left=cfg.get('tick_left', True),
                right=cfg.get('tick_right', False),
            )

            # Başlık ve etiketler
            def _fmt(text, bold, italic, math_mode=False):
                txt = "" if text is None else str(text)
                # QLineEdit tek satır olduğu için kullanıcı '\n' yazar; burada gerçek satır sonuna çevir.
                txt = txt.replace("\\n", "\n")
                if math_mode:
                    out_lines = []
                    ok = True
                    for line in txt.splitlines() or [txt]:
                        core = line.strip()
                        if not core:
                            out_lines.append("")
                            continue
                        if core.startswith("$") and core.endswith("$") and len(core) >= 2:
                            core = core[1:-1]
                        if bold and italic:
                            candidate = r"$\mathit{\mathbf{" + core + r"}}$"
                        elif bold:
                            candidate = r"$\mathbf{" + core + r"}$"
                        elif italic:
                            candidate = r"$\mathit{" + core + r"}$"
                        else:
                            candidate = "$" + core + "$"
                        try:
                            math_parser.parse(candidate, dpi=100)
                            out_lines.append(candidate)
                        except Exception:
                            ok = False
                            break
                    if ok:
                        return "\n".join(out_lines)
                    if not math_fallback_notified[0]:
                        self.statusBar().showMessage(t("status_math_fallback"), 3500)
                        math_fallback_notified[0] = True

                if not (bold or italic):
                    return txt
                # Bold/italic mathtext kullanıyor — sorunlu karakterleri escape et
                safe_lines = []
                for line in txt.splitlines() or [txt]:
                    safe = (line
                            .replace('\\', r'\backslash ')
                            .replace('$',  r'\$')
                            .replace('{',  r'\{')
                            .replace('}',  r'\}')
                            .replace('^',  r'\^{}')
                            .replace('_',  r'\_')
                            .replace('%',  r'\%')
                            .replace('&',  r'\&')
                            .replace('#',  r'\#')
                            .replace('°',  r'^\circ ')
                            .replace('µ',  r'\mu ')
                            .replace('\u03a9', r'\Omega ')
                            .replace('\u03b1', r'\alpha ')
                            .replace('\u03b2', r'\beta ')
                            .replace('\u03b3', r'\gamma ')
                            .replace('\u03b4', r'\delta ')
                            .replace('\u03c3', r'\sigma ')
                            .replace('\u03c0', r'\pi '))
                    if bold and italic:
                        safe_lines.append(r"$\mathit{\mathbf{" + safe + r"}}$")
                    elif bold:
                        safe_lines.append(r"$\mathbf{" + safe + r"}$")
                    else:
                        safe_lines.append(r"$\mathit{" + safe + r"}$")
                return "\n".join(safe_lines)

            tick_fs = cfg.get('size_tick', 10)
            math_mode = cfg.get("math_mode", False)
            ax.set_title(_fmt(cfg.get('title', ''), cfg.get('title_bold', False), cfg.get('title_italic', False), math_mode),
                         fontsize=cfg.get('size_title', 12),
                         pad=cfg.get('title_pad', 6.0))
            ax.set_xlabel(_fmt(cfg.get('xlabel', ''), cfg.get('xlabel_bold', False), cfg.get('xlabel_italic', False), math_mode),
                          fontsize=cfg.get('size_label', 10),
                          labelpad=cfg.get('xlabel_pad', 2.0))
            ax.set_ylabel(_fmt(cfg.get('ylabel', ''), cfg.get('ylabel_bold', False), cfg.get('ylabel_italic', False), math_mode),
                          fontsize=cfg.get('size_label', 10),
                          labelpad=cfg.get('ylabel_pad', 2.0))

            # Panel metinleri (faz 1)
            for it in self._panel_text_items(panel_id):
                t_mode = str(it.get("coord_mode", "axes"))
                is_math = bool(it.get("math_mode", False))
                is_bold = bool(it.get("bold", False))
                is_italic = bool(it.get("italic", False))
                raw_text = it.get("text", "")
                if is_math:
                    txt = _fmt(raw_text, is_bold, is_italic, True)
                    fw = "normal"
                    fs = "normal"
                else:
                    txt = str(raw_text).replace("\\n", "\n")
                    fw = "bold" if is_bold else "normal"
                    fs = "italic" if is_italic else "normal"
                tr = ax.transData if t_mode == "data" else ax.transAxes
                text_kwargs = {
                    "transform": tr,
                    "ha": str(it.get("ha", "left")),
                    "va": str(it.get("va", "top")),
                    "fontsize": int(it.get("fontsize", 11)),
                    "fontweight": fw,
                    "fontstyle": fs,
                    "rotation": float(it.get("rotation", 0.0)),
                    "rotation_mode": "anchor",
                    "color": str(it.get("color", "#000000")),
                    "clip_on": False,
                    "zorder": 20,
                }
                font_family = str(it.get("fontfamily", "") or "").strip()
                if font_family:
                    text_kwargs["fontfamily"] = font_family
                ax.text(
                    float(it.get("x", 0.02)),
                    float(it.get("y", 0.98)),
                    txt,
                    **text_kwargs,
                )

            # Otomatik panel etiketleri (faz 2)
            if self.text_auto_cfg.get("enabled", False):
                label_text = format_panel_label(panel_id, str(self.text_auto_cfg.get("style", "lower_rparen")))
                auto_math = bool(self.text_auto_cfg.get("math_mode", False))
                if auto_math:
                    draw_label = _fmt(
                        label_text,
                        bool(self.text_auto_cfg.get("bold", True)),
                        bool(self.text_auto_cfg.get("italic", False)),
                        True,
                    )
                    fw = "normal"
                    fs = "normal"
                else:
                    draw_label = label_text.replace("\\n", "\n")
                    fw = "bold" if self.text_auto_cfg.get("bold", True) else "normal"
                    fs = "italic" if self.text_auto_cfg.get("italic", False) else "normal"
                ax.text(
                    float(self.text_auto_cfg.get("x", 0.02)),
                    float(self.text_auto_cfg.get("y", 0.98)),
                    draw_label,
                    transform=ax.transAxes,
                    ha=str(self.text_auto_cfg.get("ha", "left")),
                    va=str(self.text_auto_cfg.get("va", "top")),
                    fontsize=int(self.text_auto_cfg.get("fontsize", 11)),
                    fontweight=fw,
                    fontstyle=fs,
                    color=str(self.text_auto_cfg.get("color", "#000000")),
                    clip_on=False,
                    zorder=25,
                )
            
            # YENİ EKLENEN KISIM: axis='both' yerine x ve y'yi ayırıp açı veriyoruz
            ax.tick_params(axis='x', which='major', labelsize=tick_fs, labelrotation=cfg.get('x_tick_rotation', 0))
            ax.tick_params(axis='x', which='minor', labelsize=tick_fs, labelrotation=cfg.get('x_tick_rotation', 0))
            ax.tick_params(axis='y', which='major', labelsize=tick_fs, labelrotation=cfg.get('y_tick_rotation', 0))
            ax.tick_params(axis='y', which='minor', labelsize=tick_fs, labelrotation=cfg.get('y_tick_rotation', 0))

            _apply_tick_notation(
                ax,
                "x",
                cfg.get("x_tick_notation", "auto"),
                cfg.get("x_tick_sci_style", "pow10"),
                cfg.get("logx", False),
            )
            _apply_offset_text_size(ax, "x", tick_fs)
            _apply_tick_notation(
                ax,
                "y",
                cfg.get("y_tick_notation", "auto"),
                cfg.get("y_tick_sci_style", "pow10"),
                cfg.get("logy", False),
            )
            _apply_offset_text_size(ax, "y", tick_fs)

            # Tick label görünürlüğü
            if not cfg.get('show_xticklabels', True):
                ax.tick_params(axis='x', labelbottom=False, labeltop=False)
            else:
                ax.tick_params(axis='x', labelbottom=True, labeltop=False)
            if not cfg.get('show_yticklabels', True):
                ax.tick_params(axis='y', labelleft=False, labelright=False)
            else:
                ax.tick_params(axis='y', labelleft=True, labelright=False)
            if ax2 and not cfg.get('show_yrticklabels', True):
                ax2.tick_params(axis='y', labelleft=False, labelright=False)
            elif ax2:
                ax2.tick_params(axis='y', labelleft=False, labelright=True)

            if ax2:
                ax2.set_ylabel(
                    _fmt(cfg.get('ylabel_right', ''), cfg.get('ylabel_right_bold', False), cfg.get('ylabel_right_italic', False), math_mode),
                    fontsize=cfg.get('size_label', 10),
                    labelpad=cfg.get('ylabel_right_pad', 2.0)
                )
                # YENİ EKLENEN KISIM
                ax2.tick_params(axis='y', which='major', labelsize=tick_fs, labelrotation=cfg.get('y_right_tick_rotation', 0))
                ax2.tick_params(axis='y', which='minor', labelsize=tick_fs, labelrotation=cfg.get('y_right_tick_rotation', 0))
                _apply_tick_notation(
                    ax2,
                    "y",
                    cfg.get("y_right_tick_notation", "auto"),
                    cfg.get("y_right_tick_sci_style", "pow10"),
                    cfg.get("logy_right", False),
                )
                _apply_offset_text_size(ax2, "y", tick_fs)

            # Izgara
            if cfg.get('grid', False):
                ax.grid(True, linestyle=cfg.get('grid_style', ':'), alpha=cfg.get('grid_alpha', 0.6))
            else:
                ax.grid(False)

            # Lejant
            if cfg.get('legend_show', True):
                h1, l1 = ax.get_legend_handles_labels()
                h2, l2 = (ax2.get_legend_handles_labels()) if ax2 else ([], [])
                if h1 or h2:
                    handles = list(h1) + list(h2)
                    labels = list(l1) + list(l2)
                    per_label_order = _legend_entries_sorted_by_order(panel_series, panel_fits)

                    decorated = []
                    for idx_h, (h, lbl) in enumerate(zip(handles, labels)):
                        order_list = per_label_order.get(lbl, [])
                        if order_list:
                            ord_val, seq_val = order_list.pop(0)
                        else:
                            ord_val, seq_val = 10**9, idx_h
                        decorated.append((ord_val, seq_val, h, lbl))
                    decorated.sort(key=lambda x: (x[0], x[1]))
                    handles = [d[2] for d in decorated]
                    labels = [d[3] for d in decorated]

                    visible_count = len(handles)
                    layout_mode = str(cfg.get('legend_layout_mode', 'auto'))
                    try:
                        ncol_custom = max(1, int(cfg.get('legend_ncol', 1)))
                    except Exception:
                        ncol_custom = 1
                    if layout_mode == "vertical":
                        legend_ncol = 1
                    elif layout_mode == "horizontal":
                        legend_ncol = max(1, visible_count)
                    elif layout_mode == "custom":
                        legend_ncol = ncol_custom
                    else:
                        legend_ncol = ncol_custom

                    legend_fs = cfg.get('legend_fontsize', tick_fs)
                    legend_kwargs = dict(
                        frameon=cfg.get('legend_frame', True),
                        fontsize=legend_fs,
                        ncol=legend_ncol,
                        handlelength=float(cfg.get('legend_handlelength', 2.5)),
                        handletextpad=float(cfg.get('legend_handletextpad', 0.8)),
                        labelspacing=float(cfg.get('legend_labelspacing', 0.5)),
                        columnspacing=float(cfg.get('legend_columnspacing', 2.0)),
                        markerscale=float(cfg.get('legend_markerscale', 1.0)),
                        numpoints=1,
                    )
                    if cfg.get('legend_manual', False):
                        leg = ax.legend(
                            handles, labels,
                            bbox_to_anchor=(cfg.get('legend_x', 1.0), cfg.get('legend_y', 1.0)),
                            loc='upper left',
                            **legend_kwargs
                        )
                    else:
                        leg = ax.legend(
                            handles, labels,
                            loc=cfg.get('legend_loc', 'best'),
                            **legend_kwargs
                        )
                    for t in leg.get_texts():
                        t.set_fontsize(legend_fs)

        # Figure-level subplots_adjust
        # Kullanıcı ayarları hatalı olsa bile matplotlib sınır koşullarını koru:
        # 0 <= left < right <= 1 ve 0 <= bottom < top <= 1
        def _as_float(v, default):
            try:
                return float(v)
            except Exception:
                return float(default)

        left = _as_float(cc.get('margin_left', 0.12), 0.12)
        right = _as_float(cc.get('margin_right', 0.95), 0.95)
        bottom = _as_float(cc.get('margin_bottom', 0.12), 0.12)
        top = _as_float(cc.get('margin_top', 0.95), 0.95)

        left = min(max(left, 0.0), 0.99)
        right = min(max(right, 0.01), 1.0)
        bottom = min(max(bottom, 0.0), 0.99)
        top = min(max(top, 0.01), 1.0)

        min_gap = 1e-3
        if left >= right:
            if left >= 1.0 - min_gap:
                left = 1.0 - min_gap
            right = min(1.0, left + min_gap)
        if bottom >= top:
            if bottom >= 1.0 - min_gap:
                bottom = 1.0 - min_gap
            top = min(1.0, bottom + min_gap)

        n = self.canvas.panel_count
        if n == 1:
            self.canvas.fig.subplots_adjust(
                left=left,
                bottom=bottom,
                right=right,
                top=top,
            )
        else:
            self.canvas.fig.subplots_adjust(
                left=left,
                bottom=bottom,
                right=right,
                top=top,
                hspace=cc.get('hspace', 0.4),
                wspace=cc.get('wspace', 0.3),
            )

        self.canvas.draw()
        self.setup_selector()

    def _open_data_ops(self):
        """Veri İşlemleri diyaloğunu açar."""
        if self.data_manager.df is None:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return
        dlg = DataOpsDialog(self.data_manager, parent=self)
        dlg.column_added.connect(lambda name: self._refresh_columns_after_ops(name, "add"))
        dlg.data_changed.connect(lambda: self._refresh_columns_after_ops("", "refresh"))
        dlg.exec()

    def _refresh_columns_after_ops(self, col_name: str = "", op: str = "add"):
        """Veri İşlemleri sonrası sütun listelerini günceller."""
        df = self.data_manager.df
        if df is None:
            return
        self._clear_last_table_undo()
        numeric_cols = [str(c) for c in df.columns
                        if pd.api.types.is_numeric_dtype(df[c])]
        cur_x    = self.combo_x.currentText()
        cur_xerr = self.combo_x_err.currentText()
        cur_y    = self.combo_y.currentText()
        cur_yerr = self.combo_y_err.currentText()

        all_cols = [str(c) for c in df.columns]
        self._sync_column_roles_with_df(reset=False)
        for combo in (self.combo_x, self.combo_y):
            combo.blockSignals(True)
            combo.clear()
            if combo is self.combo_x:
                combo.addItem(t("auto_x_label"))
                combo.addItems(all_cols)   # X: metin sütunlar dahil
            else:
                combo.addItems(numeric_cols)
            combo.blockSignals(False)

        for combo, cur in ((self.combo_x, cur_x), (self.combo_y, cur_y)):
            idx = combo.findText(cur)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        for combo in (self.combo_x_err, self.combo_y_err):
            cur = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Yok")
            combo.addItems(numeric_cols)
            combo.blockSignals(False)
            idx = combo.findText(cur)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        self.lst_y_select.blockSignals(True)
        self.lst_y_select.clear()
        self.lst_y_select.addItems(numeric_cols)
        self.lst_y_select.blockSignals(False)

        # Veri tablosunu güncelle — op'a göre optimize
        tw = self.table_w
        tw.setUpdatesEnabled(False)
        tw.blockSignals(True)

        if op == "delete" and col_name:
            # Sadece o sütunu kaldır — tüm tabloyu yeniden çizme
            col_headers = []
            for c in range(tw.columnCount()):
                header_item = tw.horizontalHeaderItem(c)
                raw = header_item.text() if header_item else ""
                norm = raw.split("] ", 1)[1] if raw.startswith("[") and "] " in raw else raw
                col_headers.append(norm)
            if col_name in col_headers:
                col_idx = col_headers.index(col_name)
                tw.removeColumn(col_idx)

        elif op == "add" and col_name and col_name in df.columns:
            # Sadece yeni sütunu ekle
            col_idx = list(df.columns).index(col_name)
            tw.insertColumn(col_idx)
            tw.setHorizontalHeaderItem(col_idx, QTableWidgetItem(col_name))
            col_data = df[col_name]
            for i in range(df.shape[0]):
                tw.setItem(i, col_idx, QTableWidgetItem(str(col_data.iat[i])))

        else:
            # Tam yenileme (fallback)
            tw.clearContents()
            tw.setRowCount(df.shape[0])
            tw.setColumnCount(df.shape[1])
            self._apply_table_headers_with_roles()
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    tw.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

        tw.blockSignals(False)
        self._sync_column_roles_with_df(reset=False)
        self._apply_table_headers_with_roles()
        self._rebuild_role_combo_row()
        tw.setUpdatesEnabled(True)
        tw.viewport().update()

    def _export_python_action(self):
        """Mevcut grafiği bağımsız Python scripti olarak kaydeder."""
        if not self.data_manager.get_all_series():
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return

        # Figure boyutunu cm olarak al
        path, _ = QFileDialog.getSaveFileName(
            self,
            t("dlg_export_python"),
            self._dialog_start_path("figure.py"),
            "Python Files (*.py)",
        )
        if not path:
            return
        if not path.endswith(".py"):
            path += ".py"
        self._remember_dialog_path(path)

        try:
            code = export_as_python(
                canvas=self.canvas,
                data_manager=self.data_manager,
                fit_list=self.fit_list,
                loaded_models=getattr(self, 'loaded_models', {}),
                canvas_config=self.canvas_config,
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            QMessageBox.information(
                self, t("msg_success"),
                t("msg_export_python_ok").format(path=path)
            )
        except Exception as e:
            QMessageBox.critical(self, t("msg_error"), str(e))

    def _export_notebook_action(self):
        """Mevcut grafiği Jupyter Notebook olarak kaydeder."""
        if not self.data_manager.get_all_series():
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            t("dlg_export_notebook"),
            self._dialog_start_path("figure.ipynb"),
            "Jupyter Notebook (*.ipynb)",
        )
        if not path:
            return
        if not path.endswith(".ipynb"):
            path += ".ipynb"
        self._remember_dialog_path(path)

        try:
            nb_json = export_as_notebook(
                canvas=self.canvas,
                data_manager=self.data_manager,
                fit_list=self.fit_list,
                loaded_models=getattr(self, 'loaded_models', {}),
                canvas_config=self.canvas_config,
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(nb_json)
            QMessageBox.information(
                self, t("msg_success"),
                t("msg_export_notebook_ok").format(path=path)
            )
        except Exception as e:
            QMessageBox.critical(self, t("msg_error"), str(e))

    def save_plot_action(self):
        p, _ = QFileDialog.getSaveFileName(
            self,
            "Kaydet",
            self._dialog_start_path("plot.png"),
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)",
        )
        if p:
            self._remember_dialog_path(p)
            self.canvas.fig.savefig(p, dpi=300, bbox_inches='tight')

    def export_table_action(self):
        df = self.data_manager.df
        if df is None or df.empty:
            QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
            return

        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            t("dlg_export_table"),
            self._dialog_start_path("data.csv"),
            "CSV (*.csv);;Excel (*.xlsx)",
        )
        if not path:
            return

        try:
            path_l = path.lower()
            as_excel = ("xlsx" in selected_filter.lower()) or path_l.endswith(".xlsx")
            if as_excel:
                if not path_l.endswith(".xlsx"):
                    path += ".xlsx"
                df.to_excel(path, index=False)
            else:
                if not path_l.endswith(".csv"):
                    path += ".csv"
                df.to_csv(path, index=False, encoding="utf-8-sig")
            self._remember_dialog_path(path)

            QMessageBox.information(
                self,
                t("msg_success"),
                t("msg_export_table_ok").format(path=path),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                t("msg_error"),
                t("msg_export_error").format(error=str(e)),
            )

    def apply_axis_settings(self, ax, axis_name, cfg, is_right=False):
        axis_obj = ax.xaxis if axis_name == 'x' else ax.yaxis
        prefix = f"{axis_name}_right" if (is_right and axis_name == 'y') else axis_name
        is_auto = cfg.get(f'{prefix}_auto', True)

        if axis_name == 'y' and is_right:
            is_log = cfg.get('logy_right', False)
        else:
            is_log = cfg.get(f'log{axis_name}', False)

        if not is_auto:
            vmin = cfg.get(f'{prefix}_min', 0)
            vmax = cfg.get(f'{prefix}_max', 10)
            if axis_name == 'x':
                ax.set_xlim(vmin, vmax)
            else:
                ax.set_ylim(vmin, vmax)

        step = cfg.get(f'{prefix}_step', 0)
        axis_obj.set_major_locator(ticker.MultipleLocator(step) if step > 0 else ticker.AutoLocator())

        minor_cnt = cfg.get(f'{prefix}_minor', 0)
        if minor_cnt > 0:
            axis_obj.set_minor_locator(ticker.AutoMinorLocator(minor_cnt + 1))
        else:
            axis_obj.set_minor_locator(ticker.NullLocator())

        if axis_name == 'x' and is_log:
            ax.set_xscale('log')
        if axis_name == 'y' and is_log:
            ax.set_yscale('log')

    def _on_canvas_panel_dblclick(self, panel_id: int | None):
        """Çift tıkta panel içi için Eksenler, dış boşluk için Kanvas ayarlarını açar."""
        if panel_id is None:
            self.open_settings(t("tab_canvas"))
            return
        self.canvas.set_active(panel_id)
        self._refresh_panel_list()
        self._refresh_series_list()
        self.open_settings(t("tab_axes"))

    def setup_selector(self):
        """Her panel için ayrı SpanSelector kurar."""
        def make_callback(pid):
            def on_sel(mi, ma):
                self.fit_xrange = (mi, ma)
                self.canvas.set_active(pid)
                self._refresh_panel_list()
                self._refresh_series_list()
                self.statusBar().showMessage(
                    f"Fit Aralığı [{self.canvas.panel_names[pid]}]: [{mi:.2f}, {ma:.2f}]"
                )
            return on_sel

        self._span_selectors = []
        for i, ax in enumerate(self.canvas.axes_list):
            sel = SpanSelector(
                ax, make_callback(i), 'horizontal',
                useblit=True,
                props=dict(alpha=0.2, facecolor='gray'),
                interactive=True,
            )
            self._span_selectors.append(sel)

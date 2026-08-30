"""
data_ops_dialog.py
──────────────────
NumeriPlot — Veri İşlemleri Diyaloğu

Yeni sütun oluşturma operasyonları:
  - Ölçekleme  : Normalize, Standardize, Min-Max
  - Dönüşüm    : Log₁₀, Ln, Karekök, Mutlak Değer, 1/x
  - Türev/Kümül: Türev, Kümülatif Toplam
  - Kayma      : Fark, Hareketli Ortalama
  - İki Sütun  : Topla, Çıkar, Çarp, Böl, Oran (%)
  - Seyreltme  : Periyodik Örnekleme, Pencere İndirgemesi
  - Pik Bulma  : scipy.signal.find_peaks

Kullanım (MainWindow içinden):
    from src.ui.data_ops_dialog import DataOpsDialog
    dlg = DataOpsDialog(data_manager, parent=self)
    if dlg.exec():
        self._refresh_columns_after_ops()
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import signal as _scipy_signal

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox,
    QDialogButtonBox, QSplitter, QSpinBox,
    QDoubleSpinBox, QStackedWidget, QWidget,
    QMessageBox, QHeaderView, QAbstractItemView, QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from lang import t


# ── Operasyon tanımları ───────────────────────────────────────────────────────

# Her operasyon: (anahtar, görünen ad, kategori, ikinci_sütun_gerekli, parametre_listesi)
# parametre: (ad, tip, varsayılan, min, max, adım)
_OP_KEYS = [
    ("normalize",    "scale",    False, []),
    ("standardize",  "scale",    False, []),
    ("minmax",       "scale",    False,
        [("p_new_min","float",0.0,-1e9,1e9,0.1),
         ("p_new_max","float",1.0,-1e9,1e9,0.1)]),
    ("log10",        "transform",False, []),
    ("ln",           "transform",False, []),
    ("sqrt",         "transform",False, []),
    ("abs",          "transform",False, []),
    ("inv",          "transform",False, []),
    ("power",        "transform",False,
        [("p_exponent","float",2.0,-100.0,100.0,0.5)]),
    ("gradient",     "calculus", True,  []),
    ("cumsum",       "calculus", False, []),
    ("cumtrapz",     "calculus", True,  []),
    ("diff",         "shift",    False, [("p_period","int",1,1,1000,1)]),
    ("rolling_mean", "shift",    False, [("p_window","int",5,2,10000,1)]),
    ("rolling_std",  "shift",    False, [("p_window","int",5,2,10000,1)]),
    ("add",          "twocol",   True,  []),
    ("subtract",     "twocol",   True,  []),
    ("multiply",     "twocol",   True,  []),
    ("divide",       "twocol",   True,  []),
    ("ratio_pct",    "twocol",   True,  []),
    ("decimate_n",   "decimate", False, [("p_step","int",10,2,100000,1)]),
    ("decimate_win", "decimate", False,
        [("p_window","int",10,2,100000,1),
         ("p_method","combo",0,["m_mean","m_median","m_min","m_max"],None,None)]),
    ("find_peaks",   "peaks",    True,
        [("p_peak_type","combo",0,["m_maximum","m_minimum"],None,None),
         ("p_min_height","float",10.0,0.0,100.0,1.0),
         ("p_min_dist","int",5,1,100000,1)]),
]


def _get_operations():
    result = []
    for key, cat, needs_b, param_defs in _OP_KEYS:
        resolved = []
        for p in param_defs:
            pk, ptype = p[0], p[1]
            rest = list(p[2:])
            if ptype == "combo":
                rest[1] = [t(c) for c in rest[1]]
            resolved.append((t(pk), ptype, *rest))
        result.append((key, t(f"op_{key}"), cat, needs_b, resolved))
    return result


def _get_categories():
    return {
        "scale":     t("cat_scale"),
        "transform": t("cat_transform"),
        "calculus":  t("cat_calculus"),
        "shift":     t("cat_shift"),
        "twocol":    t("cat_twocol"),
        "decimate":  t("cat_decimate"),
        "peaks":     t("cat_peaks"),
    }


# ── Hesaplama motoru ──────────────────────────────────────────────────────────

def _compute(op_key: str, col_a: np.ndarray, col_b: np.ndarray | None,
             params: list) -> np.ndarray:
    """
    Operasyonu hesaplar. Sonuç numpy array döner.
    col_a: birincil sütun, col_b: ikincil sütun (gerekirse), params: parametre değerleri.
    """
    a = np.asarray(col_a, dtype=float)

    # ── Ölçekleme
    if op_key == "normalize":
        mn, mx = np.nanmin(a), np.nanmax(a)
        return (a - mn) / (mx - mn) if mx != mn else np.zeros_like(a)

    elif op_key == "standardize":
        return (a - np.nanmean(a)) / (np.nanstd(a) or 1.0)

    elif op_key == "minmax":
        new_min, new_max = params[0], params[1]
        mn, mx = np.nanmin(a), np.nanmax(a)
        if mx == mn:
            return np.full_like(a, new_min)
        return new_min + (a - mn) / (mx - mn) * (new_max - new_min)

    # ── Dönüşüm
    elif op_key == "log10":
        return np.log10(np.where(a > 0, a, np.nan))

    elif op_key == "ln":
        return np.log(np.where(a > 0, a, np.nan))

    elif op_key == "sqrt":
        return np.sqrt(np.where(a >= 0, a, np.nan))

    elif op_key == "abs":
        return np.abs(a)

    elif op_key == "inv":
        return np.where(a != 0, 1.0 / a, np.nan)

    elif op_key == "power":
        n = params[0]
        return np.power(a, n)

    # ── Türev / İntegral
    elif op_key == "gradient":
        b = np.asarray(col_b, dtype=float) if col_b is not None else None
        return np.gradient(a, b) if b is not None else np.gradient(a)

    elif op_key == "cumsum":
        return np.nancumsum(a)

    elif op_key == "cumtrapz":
        b = np.asarray(col_b, dtype=float) if col_b is not None else None
        from scipy.integrate import cumulative_trapezoid
        result = cumulative_trapezoid(a, b, initial=0)
        return result

    # ── Kayma
    elif op_key == "diff":
        period = int(params[0])
        return pd.Series(a).diff(period).values

    elif op_key == "rolling_mean":
        window = int(params[0])
        return pd.Series(a).rolling(window, min_periods=1).mean().values

    elif op_key == "rolling_std":
        window = int(params[0])
        return pd.Series(a).rolling(window, min_periods=2).std().values

    # ── İki sütun
    elif op_key in ("add", "subtract", "multiply", "divide", "ratio_pct"):
        b = np.asarray(col_b, dtype=float)
        if op_key == "add":       return a + b
        if op_key == "subtract":  return a - b
        if op_key == "multiply":  return a * b
        if op_key == "divide":    return np.where(b != 0, a / b, np.nan)
        if op_key == "ratio_pct": return np.where(b != 0, a / b * 100.0, np.nan)

    # ── Seyreltme
    elif op_key == "decimate_n":
        step = int(params[0])
        return a[::step]

    elif op_key == "decimate_win":
        window = int(params[0])
        method_idx = int(params[1])
        _fns = [np.nanmean, np.nanmedian, np.nanmin, np.nanmax]
        fn = _fns[method_idx] if method_idx < len(_fns) else np.nanmean
        n = len(a)
        chunks = [a[i:i+window] for i in range(0, n, window)]
        return np.array([fn(c) for c in chunks])

    # ── Pik Bulma
    elif op_key == "find_peaks":
        peak_type  = int(params[0])   # 0=Maksimum, 1=Minimum
        height_pct = params[1] / 100.0
        distance   = int(params[2])

        work = -a if peak_type == 1 else a  # Min için ters çevir
        rng = np.nanmax(work) - np.nanmin(work)
        min_h = np.nanmin(work) + height_pct * rng if rng > 0 else None

        peak_idx, _ = _scipy_signal.find_peaks(
            work, height=min_h, distance=distance,
        )

        if col_b is not None:
            # İki sütun modu: (x_peaks, y_peaks) tuple — X önce, Y sonra
            b = np.asarray(col_b, dtype=float)
            return (b[peak_idx], a[peak_idx])
        else:
            # Tek sütun modu: NaN doldur
            result = np.full(len(a), np.nan)
            result[peak_idx] = a[peak_idx]
            return result

    raise ValueError(f"Bilinmeyen operasyon: {op_key}")


# ── Dialog ────────────────────────────────────────────────────────────────────

class DataOpsDialog(QDialog):
    """Veri İşlemleri Diyaloğu."""

    # Sinyal: yeni sütun eklendi (sütun adı)
    column_added = pyqtSignal(str)
    # Sinyal: veri yerinde güncellendi (sütun eklenmeden)
    data_changed = pyqtSignal()

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.dm = data_manager
        self._preview_result: np.ndarray | None = None
        self._current_op = None

        self.setWindowTitle(t("dlg_data_ops_title"))
        self.setMinimumSize(820, 520)
        self.resize(920, 580)

        self._build_ui()
        self._connect_signals()
        self._on_category_changed(0)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(6)
        root.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # ── Sol: İşlem paneli ──────────────────────────────────────────────
        left = QWidget()
        left.setMinimumWidth(300)
        left.setMaximumWidth(380)
        lv = QVBoxLayout(left)
        lv.setSpacing(8)
        lv.setContentsMargins(0, 0, 0, 0)

        # Kategori
        grp_op = QGroupBox(t("grp_operation"))
        fl = QFormLayout(grp_op)
        fl.setSpacing(6)

        self.combo_cat = QComboBox()
        for key, label in _get_categories().items():
            self.combo_cat.addItem(label, key)
        fl.addRow(t("lbl_category"), self.combo_cat)

        self.combo_op = QComboBox()
        fl.addRow(t("lbl_operation"), self.combo_op)

        lv.addWidget(grp_op)

        # Sütun seçimi
        grp_col = QGroupBox(t("grp_columns"))
        cl = QFormLayout(grp_col)
        cl.setSpacing(6)

        cols = self._get_columns()

        # X sütunu (üstte) — opsiyonel, needs_b'ye göre gösterilir
        self.lbl_col_b = QLabel(t("lbl_col_b"))
        self.combo_col_b = QComboBox()
        self.combo_col_b.addItems(cols)
        cl.addRow(self.lbl_col_b, self.combo_col_b)

        # Değer sütunu (altta) — her zaman görünür
        self.lbl_col_a = QLabel(t("lbl_col_a"))
        self.combo_col_a = QComboBox()
        self.combo_col_a.addItems(cols)
        cl.addRow(self.lbl_col_a, self.combo_col_a)

        lv.addWidget(grp_col)

        # Parametreler (dinamik)
        self.grp_params = QGroupBox(t("grp_params"))
        self.params_layout = QFormLayout(self.grp_params)
        self.params_layout.setSpacing(6)
        self._param_widgets: list = []
        lv.addWidget(self.grp_params)

        # Yeni sütun adı
        grp_out = QGroupBox(t("grp_output"))
        ol = QFormLayout(grp_out)
        ol.setSpacing(6)
        # Peaks iki sütun modunda: X adı üstte
        self.lbl_new_name_x = QLabel(t("lbl_new_col_x"))
        self.inp_new_name_x = QLineEdit()
        self.inp_new_name_x.setPlaceholderText(t("ph_new_col_x"))
        ol.addRow(self.lbl_new_name_x, self.inp_new_name_x)
        self.lbl_new_name_x.setVisible(False)
        self.inp_new_name_x.setVisible(False)
        # Y adı (veya tek sütun adı)
        self.lbl_new_name_y = QLabel(t("lbl_new_col"))
        self.inp_new_name = QLineEdit()
        self.inp_new_name.setPlaceholderText(t("ph_new_col_name"))
        ol.addRow(self.lbl_new_name_y, self.inp_new_name)
        self.lbl_decimate_target = QLabel(t("lbl_decimate_target"))
        self.combo_decimate_target = QComboBox()
        self.combo_decimate_target.addItem(t("decimate_target_new_col"), "new_col")
        self.combo_decimate_target.addItem(t("decimate_target_inplace"), "inplace")
        self.combo_decimate_target.setVisible(False)
        self.lbl_decimate_target.setVisible(False)
        self.combo_decimate_target.currentIndexChanged.connect(self._update_decimate_ui_state)
        ol.addRow(self.lbl_decimate_target, self.combo_decimate_target)
        self.chk_apply_all_cols = QCheckBox(t("chk_apply_all_cols"))
        self.chk_apply_all_cols.setVisible(False)
        self.chk_apply_all_cols.toggled.connect(self._update_decimate_ui_state)
        ol.addRow("", self.chk_apply_all_cols)
        lv.addWidget(grp_out)

        # Butonlar
        btn_row = QHBoxLayout()
        self.btn_preview = QPushButton(t("btn_preview"))
        self.btn_apply   = QPushButton(t("btn_apply_col"))
        self.btn_apply.setEnabled(False)
        btn_row.addWidget(self.btn_preview)
        btn_row.addWidget(self.btn_apply)
        lv.addLayout(btn_row)
        lv.addStretch(1)

        splitter.addWidget(left)

        # ── Sağ: Önizleme tablosu ─────────────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setSpacing(4)
        rv.setContentsMargins(0, 0, 0, 0)

        self.lbl_preview_title = QLabel(t("lbl_preview_title"))
        self.lbl_preview_title.setStyleSheet("font-weight: 600; font-size: 11px;")
        rv.addWidget(self.lbl_preview_title)

        self.preview_table = QTableWidget()
        self.preview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setDefaultSectionSize(22)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        rv.addWidget(self.preview_table, 1)

        self.lbl_preview_info = QLabel("")
        self.lbl_preview_info.setStyleSheet("color: gray; font-size: 10px;")
        self.lbl_preview_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        rv.addWidget(self.lbl_preview_info)

        splitter.addWidget(right)
        splitter.setSizes([340, 560])

        # ── Alt: Kapat
        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(self.reject)
        bottom_row.addWidget(btns)

        root.addLayout(bottom_row)

    # ── Sinyal bağlantıları ───────────────────────────────────────────────────

    def _connect_signals(self):
        self.combo_cat.currentIndexChanged.connect(self._on_category_changed)
        self.combo_op.currentIndexChanged.connect(self._on_op_changed)
        self.combo_col_a.currentIndexChanged.connect(self._suggest_name)
        self.combo_col_b.currentIndexChanged.connect(self._suggest_name)
        self.btn_preview.clicked.connect(self._on_preview)
        self.btn_apply.clicked.connect(self._on_apply)

    # ── Kategori değişti ─────────────────────────────────────────────────────

    def _on_category_changed(self, _idx):
        cat_key = self.combo_cat.currentData()
        self.combo_op.blockSignals(True)
        self.combo_op.clear()
        for key, label, cat, needs_b, params in _get_operations():
            if cat == cat_key:
                self.combo_op.addItem(label, key)
        self.combo_op.blockSignals(False)
        self._on_op_changed(0)

    # ── Operasyon değişti ─────────────────────────────────────────────────────

    def _on_op_changed(self, _idx):
        op_key = self.combo_op.currentData()
        if not op_key:
            return
        self._current_op = op_key

        # Operasyon tanımını bul
        op_def = next((o for o in _get_operations() if o[0] == op_key), None)
        if not op_def:
            return
        _, _, _, needs_b, param_defs = op_def

        # Sütun görünürlüğü
        self.lbl_col_b.setVisible(needs_b)
        self.combo_col_b.setVisible(needs_b)

        # Operasyon tipine göre sütun etiketlerini güncelle
        is_peaks   = (op_key == "find_peaks")
        is_calculus = (op_key in ("gradient", "cumtrapz"))
        is_twocol  = (op_key in ("add", "subtract", "multiply", "divide", "ratio_pct"))

        if is_peaks:
            self.lbl_col_a.setText(t("lbl_col_value"))
            self.lbl_col_b.setText(t("lbl_col_x_optional"))
        elif is_calculus:
            self.lbl_col_a.setText(t("lbl_col_y"))
            self.lbl_col_b.setText(t("lbl_col_x"))
        elif is_twocol:
            self.lbl_col_a.setText(t("lbl_col_a"))
            self.lbl_col_b.setText(t("lbl_col_b"))
        else:
            self.lbl_col_a.setText(t("lbl_col_a"))
            self.lbl_col_b.setText(t("lbl_col_b"))

        # Parametreleri yeniden oluştur
        self._clear_params()
        for pname, ptype, default, *rest in param_defs:
            self._add_param_widget(pname, ptype, default, rest)

        self.grp_params.setVisible(len(param_defs) > 0)

        # Peaks: ikinci çıktı adı alanını göster/gizle
        self.lbl_new_name_x.setVisible(is_peaks)
        self.inp_new_name_x.setVisible(is_peaks)
        self.lbl_new_name_y.setText(t("lbl_new_col_y") if is_peaks else t("lbl_new_col"))
        is_decimate = op_key in ("decimate_n", "decimate_win")
        self.chk_apply_all_cols.setVisible(is_decimate)
        self.lbl_decimate_target.setVisible(is_decimate)
        self.combo_decimate_target.setVisible(is_decimate)
        if not is_decimate:
            self.chk_apply_all_cols.setChecked(False)
            self.combo_decimate_target.setCurrentIndex(0)
        self._update_decimate_ui_state()

        self._suggest_name()
        self.btn_apply.setEnabled(False)
        self._clear_preview()

    def _update_decimate_ui_state(self):
        op_key = self.combo_op.currentData()
        is_decimate = op_key in ("decimate_n", "decimate_win")
        use_all = is_decimate and self.chk_apply_all_cols.isVisible() and self.chk_apply_all_cols.isChecked()
        inplace = is_decimate and str(self.combo_decimate_target.currentData() or "new_col") == "inplace"
        need_new_name = is_decimate and (not use_all) and (not inplace)
        self.lbl_new_name_y.setEnabled(not is_decimate or need_new_name)
        self.inp_new_name.setEnabled(not is_decimate or need_new_name)

    # ── Parametre widget'ları ─────────────────────────────────────────────────

    def _clear_params(self):
        while self.params_layout.rowCount():
            self.params_layout.removeRow(0)
        self._param_widgets.clear()

    def _add_param_widget(self, pname, ptype, default, rest):
        if ptype == "int":
            mn, mx, step = rest[0], rest[1], rest[2]
            w = QSpinBox()
            w.setRange(int(mn), int(mx))
            w.setSingleStep(int(step))
            w.setValue(int(default))
        elif ptype == "float":
            mn, mx, step = rest[0], rest[1], rest[2]
            w = QDoubleSpinBox()
            w.setRange(float(mn), float(mx))
            w.setSingleStep(float(step))
            w.setDecimals(3)
            w.setValue(float(default))
        elif ptype == "combo":
            choices = rest[0]
            w = QComboBox()
            w.addItems(choices)
            w.setCurrentIndex(int(default))
        else:
            w = QLineEdit(str(default))

        self.params_layout.addRow(pname + ":", w)
        self._param_widgets.append((ptype, w))

    def _get_param_values(self) -> list:
        vals = []
        for ptype, w in self._param_widgets:
            if ptype == "int":
                vals.append(w.value())
            elif ptype == "float":
                vals.append(w.value())
            elif ptype == "combo":
                vals.append(w.currentIndex())
            else:
                vals.append(w.text())
        return vals

    # ── Sütun adı önerisi ─────────────────────────────────────────────────────

    def _suggest_name(self):
        op_key = self.combo_op.currentData()
        if not op_key:
            return
        col_a = self.combo_col_a.currentText()

        prefixes = {
            "normalize": "norm", "standardize": "std_z", "minmax": "scaled",
            "log10": "log10", "ln": "ln", "sqrt": "sqrt", "abs": "abs",
            "inv": "inv", "power": "pow", "gradient": "grad",
            "cumsum": "cumsum", "cumtrapz": "cumint", "diff": "diff",
            "rolling_mean": "ma", "rolling_std": "mstd",
            "add": "sum", "subtract": "diff", "multiply": "prod",
            "divide": "div", "ratio_pct": "ratio_pct",
            "decimate_n": "dec", "decimate_win": "dec_win",
            "find_peaks": "peaks",
        }
        prefix = prefixes.get(op_key, op_key)
        suggested = f"{prefix}_{col_a}" if col_a else prefix
        self.inp_new_name.setText(suggested)

        # Peaks: X adı üstte, Y adı altta
        if op_key == "find_peaks":
            col_b = self.combo_col_b.currentText()
            if col_b and col_b != col_a:
                self.inp_new_name_x.setText(f"peaks_x_{col_b}")
            else:
                self.inp_new_name_x.setText(f"peaks_x")
            self.inp_new_name.setText(f"peaks_y_{col_a}")

    # ── Önizleme ──────────────────────────────────────────────────────────────

    def _on_preview(self):
        result, err = self._run_op(preview=True)
        if err:
            QMessageBox.warning(self, t("msg_error"), err)
            self.btn_apply.setEnabled(False)
            return

        self._preview_result = result
        self.btn_apply.setEnabled(True)
        self._populate_preview(result)

    def _run_op(self, preview=False):
        """Operasyonu çalıştır. (result, error_str) döner."""
        if self.dm.df is None:
            return None, t("msg_no_data")

        op_key = self.combo_op.currentData()
        if not op_key:
            return None, "Operasyon seçilmedi."

        op_def = next((o for o in _get_operations() if o[0] == op_key), None)
        if not op_def:
            return None, "Operasyon tanımı bulunamadı."

        _, _, _, needs_b, _ = op_def
        col_a_name = self.combo_col_a.currentText()
        col_b_name = self.combo_col_b.currentText() if needs_b else None

        if not col_a_name or col_a_name not in self.dm.df.columns:
            return None, t("msg_col_not_found")

        try:
            col_a = pd.to_numeric(self.dm.df[col_a_name], errors='coerce').values
            col_b = None
            if needs_b and col_b_name and col_b_name in self.dm.df.columns:
                # Peaks: col_b (X sütunu) col_a ile aynıysa opsiyonel say
                if not (op_key == "find_peaks" and col_b_name == col_a_name):
                    col_b = pd.to_numeric(self.dm.df[col_b_name], errors='coerce').values

            params = self._get_param_values()
            result = _compute(op_key, col_a, col_b, params)
            return result, None

        except Exception as e:
            return None, str(e)

    def _populate_preview(self, result):
        """Önizleme tablosunu doldur. result: ndarray veya (x_arr, y_arr) tuple."""
        col_a_name = self.combo_col_a.currentText()
        new_name   = self.inp_new_name.text().strip() or t("lbl_new_col_default")

        self.preview_table.clear()
        self.preview_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)

        if isinstance(result, tuple):
            # Pik iki sütun modu: (x_peaks, y_peaks) — X önce, Y sonra
            x_peaks, y_peaks = result
            x_name = self.inp_new_name_x.text().strip() or "peaks_x"
            n_preview = min(10, len(y_peaks))
            self.preview_table.setRowCount(n_preview)
            self.preview_table.setColumnCount(2)
            self.preview_table.setHorizontalHeaderLabels(
                [f"→ {x_name}", f"→ {new_name}"])
            for r in range(n_preview):
                xv = f"{x_peaks[r]:.6g}" if not np.isnan(x_peaks[r]) else "NaN"
                yv = f"{y_peaks[r]:.6g}" if not np.isnan(y_peaks[r]) else "NaN"
                for c, val in enumerate([xv, yv]):
                    item = QTableWidgetItem(val)
                    item.setForeground(Qt.GlobalColor.blue)
                    self.preview_table.setItem(r, c, item)
            total = len(y_peaks)
            self.lbl_preview_info.setText(
                f"{total} pik bulundu  |  {n_preview} satır gösteriliyor"
            )
        else:
            # Tek sütun modu
            src = pd.to_numeric(self.dm.df[col_a_name], errors='coerce').values
            n_preview = min(10, len(result), len(src))
            self.preview_table.setRowCount(n_preview)
            self.preview_table.setColumnCount(2)
            self.preview_table.setHorizontalHeaderLabels([col_a_name, f"→ {new_name}"])
            for r in range(n_preview):
                src_val = f"{src[r]:.6g}" if not np.isnan(src[r]) else "NaN"
                res_val = f"{result[r]:.6g}" if not np.isnan(result[r]) else "NaN"
                self.preview_table.setItem(r, 0, QTableWidgetItem(src_val))
                item = QTableWidgetItem(res_val)
                item.setForeground(Qt.GlobalColor.blue)
                self.preview_table.setItem(r, 1, item)
            total = len(result)
            n_nan = int(np.sum(np.isnan(result)))
            self.lbl_preview_info.setText(
                f"{n_preview} / {total} satır gösteriliyor  |  NaN: {n_nan}"
            )

    def _clear_preview(self):
        self.preview_table.clear()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.lbl_preview_info.setText("")

    def _refresh_col_combos(self):
        """Tüm sütun combo'larını yenile."""
        cols = self._get_columns()
        for combo in (self.combo_col_a, self.combo_col_b):
            cur = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(cols)
            idx = combo.findText(cur)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.blockSignals(False)

    # ── Uygula ───────────────────────────────────────────────────────────────

    def _on_apply(self):
        if self._preview_result is None:
            QMessageBox.warning(self, t("msg_warning"), t("msg_preview_first"))
            return

        op_key = self.combo_op.currentData()
        use_all_decimate = (
            op_key in ("decimate_n", "decimate_win")
            and self.chk_apply_all_cols.isVisible()
            and self.chk_apply_all_cols.isChecked()
        )
        decimate_inplace = (
            op_key in ("decimate_n", "decimate_win")
            and str(self.combo_decimate_target.currentData() or "new_col") == "inplace"
        )

        if use_all_decimate:
            df = self.dm.df
            if df is None:
                QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
                return
            numeric_cols = [str(c) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if not numeric_cols:
                QMessageBox.warning(self, t("msg_warning"), t("msg_no_numeric_cols"))
                return

            if decimate_inplace:
                reply = QMessageBox.question(
                    self, t("msg_confirm"), t("msg_confirm_decimate_inplace_all"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            params = self._get_param_values()
            existing = set(str(c) for c in df.columns)
            changed_count = 0
            prefix = "dec" if op_key == "decimate_n" else "dec_win"

            for col_name in numeric_cols:
                col_a = pd.to_numeric(df[col_name], errors='coerce').values
                result = _compute(op_key, col_a, None, params)

                if decimate_inplace:
                    target_name = col_name
                else:
                    base_name = f"{prefix}_{col_name}"
                    target_name = base_name
                    suffix = 1
                    while target_name in existing:
                        suffix += 1
                        target_name = f"{base_name}_{suffix}"
                    existing.add(target_name)

                if len(result) == len(df):
                    df[target_name] = result
                elif len(result) < len(df):
                    col = pd.Series(np.nan, index=df.index)
                    col.iloc[:len(result)] = result
                    df[target_name] = col
                else:
                    df[target_name] = result[:len(df)]

                changed_count += 1
                if not decimate_inplace:
                    self.column_added.emit(target_name)

            self.dm.df = df
            self._refresh_col_combos()
            self.data_changed.emit()
            QMessageBox.information(
                self, t("msg_success"),
                t("msg_multi_cols_updated").format(n=changed_count) if decimate_inplace
                else t("msg_multi_cols_added").format(n=changed_count)
            )
            self._preview_result = None
            self.btn_apply.setEnabled(False)
            return

        if decimate_inplace:
            df = self.dm.df
            if df is None:
                QMessageBox.warning(self, t("msg_warning"), t("msg_no_data"))
                return
            col_name = self.combo_col_a.currentText()
            if not col_name:
                QMessageBox.warning(self, t("msg_warning"), t("msg_col_not_found"))
                return
            reply = QMessageBox.question(
                self, t("msg_confirm"), t("msg_confirm_decimate_inplace_one", col=col_name),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            result = np.asarray(self._preview_result, dtype=float)
            if len(result) == len(df):
                df[col_name] = result
            elif len(result) < len(df):
                col = pd.Series(np.nan, index=df.index)
                col.iloc[:len(result)] = result
                df[col_name] = col
            else:
                df[col_name] = result[:len(df)]
            self.dm.df = df
            self._refresh_col_combos()
            self.data_changed.emit()
            QMessageBox.information(
                self, t("msg_success"),
                t("msg_col_updated_inplace").format(name=col_name)
            )
            self._preview_result = None
            self.btn_apply.setEnabled(False)
            return

        new_name = self.inp_new_name.text().strip()
        if not new_name:
            QMessageBox.warning(self, t("msg_warning"), t("msg_col_name_empty"))
            return

        result = self._preview_result
        df = self.dm.df
        existing = set(str(c) for c in df.columns)

        if isinstance(result, tuple):
            # Pik iki sütun modu: (x_peaks, y_peaks) — X önce df'e, sonra Y
            x_peaks, y_peaks = result
            x_name = self.inp_new_name_x.text().strip()
            if not x_name:
                QMessageBox.warning(self, t("msg_warning"), t("msg_col_name_empty"))
                return
            # Çakışma kontrolü
            if new_name in existing or x_name in existing:
                QMessageBox.warning(
                    self, t("msg_warning"),
                    t("msg_col_name_exists").format(name=new_name if new_name in existing else x_name)
                )
                return
            n = len(y_peaks)
            col_x = pd.Series(np.nan, index=df.index)
            col_x.iloc[:n] = x_peaks
            df[x_name] = col_x
            col_y = pd.Series(np.nan, index=df.index)
            col_y.iloc[:n] = y_peaks
            df[new_name] = col_y
            self.dm.df = df
            self._refresh_col_combos()
            self.column_added.emit(x_name)
            self.column_added.emit(new_name)
            QMessageBox.information(
                self, t("msg_success"),
                t("msg_peaks_added").format(n=n, x=x_name, y=new_name)
            )
        else:
            # Çakışma kontrolü
            if new_name in existing:
                QMessageBox.warning(
                    self, t("msg_warning"),
                    t("msg_col_name_exists").format(name=new_name)
                )
                return
            # Tek sütun modu
            if len(result) == len(df):
                df[new_name] = result
            elif len(result) < len(df):
                col = pd.Series(np.nan, index=df.index)
                col.iloc[:len(result)] = result
                df[new_name] = col
            else:
                df[new_name] = result[:len(df)]
            self.dm.df = df
            self._refresh_col_combos()
            self.column_added.emit(new_name)
            QMessageBox.information(
                self, t("msg_success"),
                t("msg_col_added").format(name=new_name)
            )

        self._populate_preview(result)
        self._preview_result = None
        self.btn_apply.setEnabled(False)

    # ── Yardımcı ─────────────────────────────────────────────────────────────

    def _get_columns(self) -> list[str]:
        if self.dm.df is None:
            return []
        return [str(c) for c in self.dm.df.columns]

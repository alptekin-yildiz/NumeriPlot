from ..emoji_spinbox import EmojiSpinBox, EmojiDoubleSpinBox
import inspect
import pandas as pd
import numpy as np
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

class DataImportDialog(QDialog):
    """
    Geliştirilmiş veri import dialog'u.
    - Başlık / birim / açıklama satır seçimi
    - Kaç satır atlanacağı (skiprows)
    - Sütun seçimi (checkbox)
    - Canlı önizleme
    """

    SEPARATORS = {}  # __init__ içinde t() ile doldurulur

    ENCODINGS = ["utf-8", "latin-1", "cp1252", "utf-8-sig"]

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.SEPARATORS = {
            t("sep_auto"): None,
            t("sep_comma"): ",",
            t("sep_semicolon"): ";",
            t("sep_tab"): "\t",
            t("sep_space"): " ",
        }
        self.file_path = file_path
        self.df = None
        self.col_types = {}
        self._df_raw = None
        self._col_checks = {}   # {col_name: QCheckBox}
        self._type_combos = {}  # {col_name: QComboBox}

        self.setWindowTitle(t("dlg_import_title"))
        self.setMinimumSize(900, 680)
        self.resize(980, 780)
        self._build_ui()
        self._refresh_preview()

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(2)
        root.setContentsMargins(8, 8, 8, 8)

        # ── ÜST BÖLÜM: Sol=Ayırıcı+Kodlama, Sağ=Satır Yapısı ─
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        # Sol: Ayırıcı ve Kodlama alt alta
        left_form = QFormLayout()
        left_form.setSpacing(4)
        left_form.setContentsMargins(0, 0, 0, 0)

        self.combo_sep = QComboBox()
        self.combo_sep.addItems(list(self.SEPARATORS.keys()))
        self.combo_sep.currentIndexChanged.connect(self._refresh_preview)
        left_form.addRow(t("lbl_separator"), self.combo_sep)

        self.combo_enc = QComboBox()
        self.combo_enc.addItems(self.ENCODINGS)
        self.combo_enc.currentIndexChanged.connect(self._refresh_preview)
        left_form.addRow(t("lbl_encoding"), self.combo_enc)

        left_w = QWidget()
        left_w.setLayout(left_form)
        top_row.addWidget(left_w, 0)

        # Sağ: Satır Yapısı grubu
        grp = QGroupBox(t("grp_row_structure"))
        grp.setStyleSheet("QGroupBox { font-weight: 600; }")
        gl = QGridLayout(grp)
        gl.setHorizontalSpacing(8)
        gl.setVerticalSpacing(4)
        gl.setContentsMargins(6, 8, 6, 4)

        # Başlık satırı
        self.chk_header = QCheckBox(t("chk_header"))
        self.chk_header.setChecked(True)
        self.chk_header.toggled.connect(self._on_header_toggled)
        self.chk_header.toggled.connect(self._refresh_preview)
        self.spin_header_row = EmojiSpinBox()
        self.spin_header_row.setRange(0, 50)
        self.spin_header_row.setValue(0)
        self.spin_header_row.setMinimumWidth(72)
        self.spin_header_row.setToolTip(t("tip_header_row"))
        self.spin_header_row.valueChanged.connect(self._refresh_preview)
        gl.addWidget(self.chk_header, 0, 0)
        gl.addWidget(QLabel(t("lbl_row_no")), 0, 1)
        gl.addWidget(self.spin_header_row, 0, 2)

        # Birim satırı
        self.chk_unit = QCheckBox(t("chk_unit"))
        self.chk_unit.setChecked(False)
        self.chk_unit.toggled.connect(self._on_unit_toggled)
        self.chk_unit.toggled.connect(self._refresh_preview)
        self.spin_unit_row = EmojiSpinBox()
        self.spin_unit_row.setRange(0, 50)
        self.spin_unit_row.setValue(1)
        self.spin_unit_row.setMinimumWidth(72)
        self.spin_unit_row.setEnabled(False)
        self.spin_unit_row.setToolTip(t("tip_unit_row"))
        self.spin_unit_row.valueChanged.connect(self._refresh_preview)
        self.chk_unit_append = QCheckBox(t("chk_unit_append"))
        self.chk_unit_append.setChecked(True)
        self.chk_unit_append.setEnabled(False)
        self.chk_unit_append.toggled.connect(self._refresh_preview)
        gl.addWidget(self.chk_unit, 1, 0)
        gl.addWidget(QLabel(t("lbl_row_no")), 1, 1)
        gl.addWidget(self.spin_unit_row, 1, 2)
        gl.addWidget(self.chk_unit_append, 1, 3)

        # Açıklama satırları
        self.chk_skip = QCheckBox(t("chk_skip"))
        self.chk_skip.setChecked(False)
        self.chk_skip.toggled.connect(self._on_skip_toggled)
        self.chk_skip.toggled.connect(self._refresh_preview)
        self.spin_skip = EmojiSpinBox()
        self.spin_skip.setRange(0, 100)
        self.spin_skip.setValue(0)
        self.spin_skip.setMinimumWidth(72)
        self.spin_skip.setEnabled(False)
        self.spin_skip.setToolTip(t("tip_skip_rows"))
        self.spin_skip.valueChanged.connect(self._refresh_preview)
        gl.addWidget(self.chk_skip, 2, 0)
        gl.addWidget(QLabel(t("lbl_skip_rows")), 2, 1)
        gl.addWidget(self.spin_skip, 2, 2)
        gl.setColumnStretch(4, 1)

        top_row.addWidget(grp, 1)
        root.addLayout(top_row)

        # ── Status ────────────────────────────────────────────
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: gray; font-size: 10px; margin: 0px; padding: 0px;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_status.setFixedHeight(14)
        root.addWidget(self.lbl_status)

        # ── Önizleme: QTabWidget ile Ham + Parse ─────────────
        self.preview_tabs = QTabWidget()
        self.preview_tabs.setMinimumHeight(160)

        self.raw_table = QTableWidget()
        self.raw_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.raw_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.raw_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.raw_table.setAlternatingRowColors(True)
        self.preview_tabs.addTab(self.raw_table, t("tab_raw_preview"))

        self.preview_table = QTableWidget()
        self.preview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.preview_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_tabs.addTab(self.preview_table, t("tab_parsed_preview"))

        root.addWidget(self.preview_tabs, 2)

        # ── Sütun tipleri başlık — sağa yanaşık ──────────────
        lbl_col = QLabel(t("lbl_col_types"))
        lbl_col.setStyleSheet("font-weight: 600; font-size: 11px; padding: 0px; margin: 0px;")
        lbl_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(lbl_col)

        # ── Sütun seçim tablosu ───────────────────────────────
        self.col_table = QTableWidget()
        self.col_table.setColumnCount(4)
        self.col_table.setHorizontalHeaderLabels(["✔", t("tbl_col"), t("tbl_detect"), t("tbl_use")])
        self.col_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.col_table.setColumnWidth(0, 32)
        self.col_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.col_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.col_table.setColumnWidth(2, 110)
        self.col_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.col_table.setColumnWidth(3, 130)
        self.col_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.col_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.col_table.setMinimumHeight(120)
        self.col_table.setMaximumHeight(220)
        root.addWidget(self.col_table, 1)

        # ── Butonlar ──────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(t("btn_import"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(t("btn_cancel"))
        root.addWidget(btns)

    # ── Toggle yardımcıları ───────────────────────────────────
    def _on_header_toggled(self, checked):
        self.spin_header_row.setEnabled(checked)

    def _on_unit_toggled(self, checked):
        self.spin_unit_row.setEnabled(checked)
        self.chk_unit_append.setEnabled(checked)

    def _on_skip_toggled(self, checked):
        self.spin_skip.setEnabled(checked)

    # ── Önizleme yenile ───────────────────────────────────────
    def _refresh_preview(self):
        sep_key = self.combo_sep.currentText()
        sep = self.SEPARATORS[sep_key]
        enc = self.combo_enc.currentText()
        fp = self.file_path

        has_header = self.chk_header.isChecked()
        header_row = self.spin_header_row.value() if has_header else None
        has_unit   = self.chk_unit.isChecked()
        unit_row   = self.spin_unit_row.value() if has_unit else None
        unit_append = self.chk_unit_append.isChecked()
        has_skip   = self.chk_skip.isChecked()
        extra_skip = self.spin_skip.value() if has_skip else 0

        try:
            # skiprows: başlık + birim + açıklama satırlarını hesapla
            skip_set = set()
            if has_unit and unit_row is not None:
                skip_set.add(unit_row)

            # Ekstra atlanacak satırlar: başlık/birim satırından sonra extra_skip adet
            if extra_skip > 0:
                start = 0
                if has_header and header_row is not None:
                    start = max(start, header_row + 1)
                if has_unit and unit_row is not None:
                    start = max(start, unit_row + 1)
                for r in range(start, start + extra_skip):
                    skip_set.add(r)

            skiprows = sorted(skip_set) if skip_set else None

            if fp.endswith(('.xlsx', '.xls')):
                df_raw = pd.read_excel(fp, header=header_row, skiprows=skiprows, nrows=200)
            else:
                kwargs = dict(header=header_row, encoding=enc, nrows=200)
                if skiprows:
                    kwargs['skiprows'] = skiprows
                if sep is None:
                    df_raw = pd.read_csv(fp, sep=None, engine='python', **kwargs)
                else:
                    df_raw = pd.read_csv(fp, sep=sep, **kwargs)

            # Sütun adlarını temizle
            if header_row is None:
                df_raw.columns = [f"Col_{i}" for i in range(df_raw.shape[1])]
            else:
                df_raw.columns = [str(c).strip().lstrip('\ufeff') for c in df_raw.columns]

            # Birim satırını başlığa ekle
            if has_unit and unit_append and header_row is not None and unit_row is not None:
                try:
                    if fp.endswith(('.xlsx', '.xls')):
                        df_unit = pd.read_excel(fp, header=None, skiprows=unit_row, nrows=1)
                    else:
                        unit_kwargs = dict(header=None, encoding=enc, nrows=1, skiprows=unit_row)
                        if sep is None:
                            df_unit = pd.read_csv(fp, sep=None, engine='python', **unit_kwargs)
                        else:
                            df_unit = pd.read_csv(fp, sep=sep, **unit_kwargs)
                    units = [str(v).strip() for v in df_unit.iloc[0]]
                    new_cols = []
                    for i, col in enumerate(df_raw.columns):
                        u = units[i] if i < len(units) else ''
                        if u and u.lower() not in ('nan', '', '-'):
                            new_cols.append(f"{col} ({u})")
                        else:
                            new_cols.append(col)
                    df_raw.columns = new_cols
                except Exception:
                    pass

            self._df_raw = df_raw
            self._populate_raw_preview()
            self._populate_preview(df_raw)
            self._populate_col_table(df_raw)
            self.lbl_status.setText(
                f"{df_raw.shape[0]} {t('lbl_status_rows')} × {df_raw.shape[1]} {t('lbl_status_cols')} ({t('lbl_status_preview')})"
            )

        except Exception as e:
            self.lbl_status.setText(f"⚠ {e}")
            self.raw_table.clear()
            self.preview_table.clear()
            self.col_table.setRowCount(0)
            self._df_raw = None

    def _populate_raw_preview(self):
        """Ham dosyayı satır numarasıyla birlikte gösterir."""
        sep_key = self.combo_sep.currentText()
        sep = self.SEPARATORS[sep_key]
        enc = self.combo_enc.currentText()
        fp = self.file_path
        try:
            if fp.endswith(('.xlsx', '.xls')):
                df_ham = pd.read_excel(fp, header=None, nrows=200)
            else:
                kwargs = dict(header=None, encoding=enc, nrows=200)
                if sep is None:
                    df_ham = pd.read_csv(fp, sep=None, engine='python', **kwargs)
                else:
                    df_ham = pd.read_csv(fp, sep=sep, **kwargs)

            rows = len(df_ham)
            self.raw_table.setRowCount(rows)
            self.raw_table.setColumnCount(df_ham.shape[1])
            self.raw_table.setHorizontalHeaderLabels(
                [f"{t('lbl_col_prefix')} {i}" for i in range(df_ham.shape[1])]
            )
            # Satır numaraları 0'dan başlasın (pandas gibi)
            self.raw_table.setVerticalHeaderLabels([str(i) for i in range(rows)])

            for r in range(rows):
                for c in range(df_ham.shape[1]):
                    item = QTableWidgetItem(str(df_ham.iat[r, c]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # Başlık/birim/skip satırlarını renklendir
                    has_header = self.chk_header.isChecked()
                    header_row = self.spin_header_row.value() if has_header else -1
                    has_unit   = self.chk_unit.isChecked()
                    unit_row   = self.spin_unit_row.value() if has_unit else -1
                    has_skip   = self.chk_skip.isChecked()
                    extra_skip = self.spin_skip.value() if has_skip else 0
                    skip_start = max(
                        (header_row + 1 if has_header else 0),
                        (unit_row   + 1 if has_unit   else 0)
                    )
                    skip_rows  = set(range(skip_start, skip_start + extra_skip))

                    if r == header_row and has_header:
                        item.setBackground(QColor("#b3d9ff"))   # mavi — başlık
                        item.setFont(QFont("", -1, QFont.Weight.Bold))
                    elif r == unit_row and has_unit:
                        item.setBackground(QColor("#c8f0c8"))   # yeşil — birim
                    elif r in skip_rows:
                        item.setBackground(QColor("#ffe0b3"))   # turuncu — atla
                    self.raw_table.setItem(r, c, item)
        except Exception:
            self.raw_table.clear()

    def _populate_preview(self, df: pd.DataFrame):
        rows = len(df)
        self.preview_table.setRowCount(rows)
        self.preview_table.setColumnCount(df.shape[1])
        self.preview_table.setHorizontalHeaderLabels([str(c) for c in df.columns])
        for r in range(rows):
            for c in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[r, c]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.preview_table.setItem(r, c, item)

    def _populate_col_table(self, df: pd.DataFrame):
        self.col_table.setRowCount(df.shape[1])
        self._col_checks = {}
        self._type_combos = {}

        for i, col in enumerate(df.columns):
            numeric = pd.to_numeric(df[col], errors='coerce').notna().mean() > 0.7
            detected = t("lbl_num") if numeric else t("lbl_text")

            # Checkbox — sütun seçimi
            chk = QCheckBox()
            chk.setChecked(True)
            chk_w = QWidget()
            chk_l = QHBoxLayout(chk_w)
            chk_l.addWidget(chk)
            chk_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_l.setContentsMargins(0, 0, 0, 0)
            self.col_table.setCellWidget(i, 0, chk_w)
            self._col_checks[str(col)] = chk

            self.col_table.setItem(i, 1, QTableWidgetItem(str(col)))
            det_item = QTableWidgetItem(detected)
            det_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.col_table.setItem(i, 2, det_item)

            combo = QComboBox()
            combo.addItems([t("lbl_num"), t("lbl_text")])
            combo.setCurrentIndex(0 if numeric else 1)
            self.col_table.setCellWidget(i, 3, combo)
            self._type_combos[str(col)] = combo

    # ── Onayla ────────────────────────────────────────────────
    def _on_accept(self):
        if self._df_raw is None:
            QMessageBox.warning(self, t("msg_error"), t("msg_load_file_first"))
            return

        sep_key = self.combo_sep.currentText()
        sep = self.SEPARATORS[sep_key]
        enc = self.combo_enc.currentText()
        fp = self.file_path

        has_header  = self.chk_header.isChecked()
        header_row  = self.spin_header_row.value() if has_header else None
        has_unit    = self.chk_unit.isChecked()
        unit_row    = self.spin_unit_row.value() if has_unit else None
        unit_append = self.chk_unit_append.isChecked()
        has_skip    = self.chk_skip.isChecked()
        extra_skip  = self.spin_skip.value() if has_skip else 0

        try:
            skip_set = set()
            if has_unit and unit_row is not None:
                skip_set.add(unit_row)
            if extra_skip > 0:
                start = 0
                if has_header and header_row is not None:
                    start = max(start, header_row + 1)
                if has_unit and unit_row is not None:
                    start = max(start, unit_row + 1)
                for r in range(start, start + extra_skip):
                    skip_set.add(r)
            skiprows = sorted(skip_set) if skip_set else None

            if fp.endswith(('.xlsx', '.xls')):
                df_full = pd.read_excel(fp, header=header_row, skiprows=skiprows)
            else:
                kwargs = dict(header=header_row, encoding=enc)
                if skiprows:
                    kwargs['skiprows'] = skiprows
                if sep is None:
                    df_full = pd.read_csv(fp, sep=None, engine='python', **kwargs)
                else:
                    df_full = pd.read_csv(fp, sep=sep, **kwargs)

            if header_row is None:
                df_full.columns = [f"Col_{i}" for i in range(df_full.shape[1])]
            else:
                df_full.columns = [str(c).strip().lstrip('\ufeff') for c in df_full.columns]

            # Birim ekle
            if has_unit and unit_append and header_row is not None and unit_row is not None:
                try:
                    if fp.endswith(('.xlsx', '.xls')):
                        df_unit = pd.read_excel(fp, header=None, skiprows=unit_row, nrows=1)
                    else:
                        unit_kwargs = dict(header=None, encoding=enc, nrows=1, skiprows=unit_row)
                        if sep is None:
                            df_unit = pd.read_csv(fp, sep=None, engine='python', **unit_kwargs)
                        else:
                            df_unit = pd.read_csv(fp, sep=sep, **unit_kwargs)
                    units = [str(v).strip() for v in df_unit.iloc[0]]
                    new_cols = []
                    for i, col in enumerate(df_full.columns):
                        u = units[i] if i < len(units) else ''
                        if u and u.lower() not in ('nan', '', '-'):
                            new_cols.append(f"{col} ({u})")
                        else:
                            new_cols.append(col)
                    df_full.columns = new_cols
                except Exception:
                    pass

            # Sadece seçili sütunları al
            selected_cols = [
                col for col, chk in self._col_checks.items()
                if chk.isChecked() and col in df_full.columns
            ]
            if selected_cols:
                df_full = df_full[selected_cols]

            # Tip uygula
            self.col_types = {}
            for col, combo in self._type_combos.items():
                if col in df_full.columns:
                    typ = 'numeric' if '🔢' in combo.currentText() else 'text'
                    self.col_types[col] = typ
                    if typ == 'numeric':
                        df_full[col] = pd.to_numeric(df_full[col], errors='coerce')

            self.df = df_full
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, t("msg_load_error_title"), str(e))

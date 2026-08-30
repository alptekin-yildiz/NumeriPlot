import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lang import get_language, t
from src.version import APP_SUBTITLE, SUPPORT_EMAIL


class MainWindowDialogsMixin:
    def _show_about(self):
        """Hakkinda / About dialog."""
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            )
        license_path = os.path.join(base, "LICENSE")

        dlg = QDialog(self)
        dlg.setWindowTitle(t("action_about"))
        dlg.setFixedWidth(440)
        dlg.setMinimumHeight(340)

        root = QVBoxLayout(dlg)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header.setStyleSheet("background-color: #1a1a2e;")
        header.setFixedHeight(88)
        h_lay = QVBoxLayout(header)
        h_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_name = QLabel(self._app_title)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fnt = QFont()
        fnt.setPointSize(20)
        fnt.setBold(True)
        lbl_name.setFont(fnt)
        lbl_name.setStyleSheet("color: #e0e0ff; background: transparent;")

        lbl_ver = QLabel(self._app_version)
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ver.setStyleSheet("color: #8888cc; background: transparent; font-size: 12px;")

        h_lay.addWidget(lbl_name)
        h_lay.addWidget(lbl_ver)
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet("background-color: #f8f8f8;")
        b_lay = QVBoxLayout(body)
        b_lay.setSpacing(6)
        b_lay.setContentsMargins(28, 16, 28, 16)

        is_tr = get_language() == "tr"

        def info_row(label, value, link=None):
            row = QHBoxLayout()
            lbl_l = QLabel(f"<b>{label}</b>")
            lbl_l.setFixedWidth(100)
            lbl_l.setStyleSheet("color: #444;")
            if link:
                lbl_v = QLabel(f'<a href="{link}" style="color:#3355cc;">{value}</a>')
                lbl_v.setOpenExternalLinks(True)
            else:
                lbl_v = QLabel(value)
                lbl_v.setStyleSheet("color: #222;")
            lbl_v.setWordWrap(True)
            row.addWidget(lbl_l)
            row.addWidget(lbl_v, 1)
            return row

        b_lay.addLayout(info_row("", f"<i>{APP_SUBTITLE}</i>"))
        b_lay.addSpacing(4)
        b_lay.addLayout(
            info_row(
                "Proje" if is_tr else "Project",
                "Bağımsız akademik yazılım projesi"
                if is_tr
                else "Independent academic software project",
            )
        )
        b_lay.addLayout(info_row("Geliştirici" if is_tr else "Developer", "Alptekin YILDIZ"))
        b_lay.addLayout(
            info_row(
                "Akademik bağ" if is_tr else "Affiliation",
                "İstanbul Teknik Üniversitesi"
                if is_tr
                else "Istanbul Technical University",
            )
        )
        b_lay.addLayout(
            info_row(
                "E-posta" if is_tr else "E-mail",
                SUPPORT_EMAIL,
                link=f"mailto:{SUPPORT_EMAIL}",
            )
        )
        b_lay.addLayout(
            info_row(
                "Lisans" if is_tr else "License",
                "GNU GPL v3.0 only",
            )
        )
        b_lay.addLayout(info_row("©", "2026 Alptekin YILDIZ"))
        b_lay.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_license = QPushButton(
            "📄 Lisans Metnini Görüntüle" if is_tr else "📄 View License Text"
        )
        btn_license.setStyleSheet("font-size: 11px;")

        def show_license():
            lic_dlg = QDialog(dlg)
            lic_dlg.setWindowTitle("GNU General Public License v3")
            lic_dlg.resize(560, 420)
            ll = QVBoxLayout(lic_dlg)
            txt = QTextEdit()
            txt.setReadOnly(True)
            txt.setStyleSheet("font-family: monospace; font-size: 11px;")
            try:
                with open(license_path, encoding="utf-8") as fobj:
                    txt.setPlainText(fobj.read())
            except Exception:
                txt.setPlainText(
                    "LICENSE dosyası bulunamadı.\n"
                    "Tam metin: https://www.gnu.org/licenses/gpl-3.0.txt"
                )
            ll.addWidget(txt)
            close = QPushButton("Kapat" if is_tr else "Close")
            close.clicked.connect(lic_dlg.accept)
            cl = QHBoxLayout()
            cl.addStretch()
            cl.addWidget(close)
            ll.addLayout(cl)
            lic_dlg.exec()

        btn_license.clicked.connect(show_license)

        btn_close = QPushButton("Kapat" if is_tr else "Close")
        btn_close.setFixedWidth(80)
        btn_close.clicked.connect(dlg.accept)

        btn_row.addWidget(btn_license)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        b_lay.addLayout(btn_row)

        root.addWidget(body)
        dlg.exec()

    def _open_symbol_palette(self, target_input):
        symbols = [
            ("xⁿ", "^{}", "Üst indis şablonu", 1),
            ("xₙ", "_{}", "Alt indis şablonu", 1),
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
            ("α", "α", "α", 0), ("β", "β", "β", 0), ("γ", "γ", "γ", 0), ("δ", "δ", "δ", 0),
            ("ε", "ε", "ε", 0), ("ζ", "ζ", "ζ", 0), ("η", "η", "η", 0), ("θ", "θ", "θ", 0),
            ("λ", "λ", "λ", 0), ("µ", "µ", "µ", 0), ("ν", "ν", "ν", 0), ("π", "π", "π", 0),
            ("ρ", "ρ", "ρ", 0), ("σ", "σ", "σ", 0), ("τ", "τ", "τ", 0), ("φ", "φ", "φ", 0),
            ("χ", "χ", "χ", 0), ("ψ", "ψ", "ψ", 0), ("ω", "ω", "ω", 0),
            ("Γ", "Γ", "Γ", 0), ("Δ", "Δ", "Δ", 0), ("Θ", "Θ", "Θ", 0), ("Λ", "Λ", "Λ", 0),
            ("Π", "Π", "Π", 0), ("Σ", "Σ", "Σ", 0), ("Φ", "Φ", "Φ", 0), ("Ψ", "Ψ", "Ψ", 0),
            ("Ω", "Ω", "Ω", 0), ("°", "°", "°", 0), ("±", "±", "±", 0), ("×", "×", "×", 0),
            ("÷", "÷", "÷", 0), ("⁻¹", "⁻¹", "⁻¹", 0), ("Å", "Å", "Å", 0), ("∞", "∞", "∞", 0),
            ("√", "√", "√", 0), ("∂", "∂", "∂", 0), ("∇", "∇", "∇", 0), ("∑", "∑", "∑", 0),
            ("∏", "∏", "∏", 0),
        ]
        dlg = QDialog(self)
        dlg.setWindowTitle("Sembol Seç")
        dlg.setWindowFlags(Qt.WindowType.Popup)
        lay = QGridLayout(dlg)
        lay.setSpacing(2)
        lay.setContentsMargins(6, 6, 6, 6)
        cols = 8
        for i, (label, insert_text, tip, back) in enumerate(symbols):
            btn = QPushButton(label)
            btn.setFixedSize(32, 32)
            btn.setToolTip(tip)
            btn.setStyleSheet("font-size: 14px;")

            def insert(_, s=insert_text, move_back=back):
                pos = target_input.cursorPosition()
                txt = target_input.text()
                target_input.setText(txt[:pos] + s + txt[pos:])
                target_input.setCursorPosition(max(0, pos + len(s) - move_back))
                dlg.accept()

            btn.clicked.connect(insert)
            lay.addWidget(btn, i // cols, i % cols)

        dlg.adjustSize()
        dlg_h = dlg.sizeHint().height()
        gp = target_input.mapToGlobal(target_input.rect().topLeft())
        dlg.move(gp.x(), gp.y() - dlg_h - 4)
        dlg.exec()

    def _open_rename_dialog(self, title: str, prompt: str, current: str) -> tuple:
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setMinimumWidth(340)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(8)
        lay.addWidget(QLabel(prompt))

        inp = QLineEdit(current)
        inp.selectAll()

        sym_btn = QPushButton("Ω")
        sym_btn.setFixedWidth(28)
        sym_btn.setFixedHeight(24)
        sym_btn.setToolTip("Sembol / Yunan harfi ekle")
        sym_btn.setStyleSheet("font-size: 11px; padding: 0px;")
        sym_btn.clicked.connect(lambda: self._open_symbol_palette(inp))

        row = QHBoxLayout()
        row.setSpacing(3)
        row.addWidget(inp)
        row.addWidget(sym_btn)
        lay.addLayout(row)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)

        inp.returnPressed.connect(dlg.accept)
        ok = dlg.exec() == QDialog.DialogCode.Accepted
        return inp.text(), ok

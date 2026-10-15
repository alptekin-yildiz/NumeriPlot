import inspect
import math

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from lang import t


class FitDialog(QDialog):
    """ Fit Parametreleri Penceresi """

    def __init__(self, param_names, doc_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("dlg_fit_title"))
        self.resize(400, 350)

        layout = QVBoxLayout(self)

        if doc_text:
            info_label = QLabel(inspect.cleandoc(doc_text))
            info_label.setWordWrap(True)
            info_label.setStyleSheet(
                "QLabel { background-color: #fffde7; border: 1px solid #ccc; padding: 10px; "
                "font-family: 'Courier New'; font-size: 11pt; }"
            )
            layout.addWidget(info_label)

        notice = QLabel(t("fit_unweighted_notice"))
        notice.setWordWrap(True)
        layout.addWidget(notice)
        layout.addWidget(QLabel(t("dlg_init_params")))
        self.inputs = {}
        form = QFormLayout()
        for name in param_names:
            inp = QLineEdit("1.0")
            self.inputs[name] = inp
            form.addRow(f"{name} =", inp)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_values(self):
        values = []
        for name, inp in self.inputs.items():
            try:
                value = float(inp.text())
                if not math.isfinite(value):
                    raise ValueError
            except ValueError:
                inp.setFocus()
                inp.selectAll()
                raise ValueError(t("fit_invalid_parameter", parameter=name)) from None
            values.append(value)
        return values

    def accept(self):
        try:
            self.get_values()
        except ValueError as error:
            QMessageBox.warning(self, t("msg_warning"), str(error))
            return
        super().accept()

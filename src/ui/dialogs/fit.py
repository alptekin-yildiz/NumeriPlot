import inspect

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from lang import t


class FitDialog(QDialog):
    """ Fit Parametreleri Penceresi """

    def __init__(self, param_names, doc_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fit Parametreleri")
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
        try:
            return [float(inp.text()) for inp in self.inputs.values()]
        except Exception:
            return None

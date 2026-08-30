"""
EmojiSpinBox ve EmojiDoubleSpinBox
-----------------------------------
Qt'nun kendi spin box ok ikonları stylesheet ile birlikte çalışmadığı için
▲ / ▼ emoji butonlu custom widget. Her temada görünür, platform bağımsız.

Kullanım:
    from src.ui.emoji_spinbox import EmojiSpinBox, EmojiDoubleSpinBox

    sb = EmojiSpinBox(minimum=0, maximum=100, value=10, step=1)
    dsb = EmojiDoubleSpinBox(minimum=0.0, maximum=10.0, value=1.0, step=0.1, decimals=2)

    sb.valueChanged.connect(callback)
    val = sb.value()
    sb.setValue(5)
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class _BaseEmojiSpinBox(QWidget):
    """Ortak taban — int ve float için override edilir."""
    valueChanged = pyqtSignal(object)

    def __init__(self, minimum, maximum, value, step, parent=None):
        super().__init__(parent)
        self._min   = minimum
        self._max   = maximum
        self._step  = step
        self._value = self._clamp(value)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self._edit = QLineEdit(self._format(self._value))
        self._edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._edit.editingFinished.connect(self._on_edit_finished)
        layout.addWidget(self._edit, 1)

        btn_font = QFont()
        btn_font.setPointSize(8)

        self._btn_up = QToolButton()
        self._btn_up.setText("▲")
        self._btn_up.setFont(btn_font)
        self._btn_up.setFixedWidth(22)
        self._btn_up.clicked.connect(self._step_up)

        self._btn_down = QToolButton()
        self._btn_down.setText("▼")
        self._btn_down.setFont(btn_font)
        self._btn_down.setFixedWidth(22)
        self._btn_down.clicked.connect(self._step_down)

        btn_col = QWidget()
        btn_col_lay = QHBoxLayout(btn_col)
        btn_col_lay.setContentsMargins(0, 0, 0, 0)
        btn_col_lay.setSpacing(1)
        btn_col_lay.addWidget(self._btn_up)
        btn_col_lay.addWidget(self._btn_down)
        layout.addWidget(btn_col)

    def _clamp(self, v):
        return max(self._min, min(self._max, v))

    def _format(self, v):
        raise NotImplementedError

    def _parse(self, text):
        raise NotImplementedError

    def _on_edit_finished(self):
        try:
            v = self._clamp(self._parse(self._edit.text()))
        except (ValueError, TypeError):
            v = self._value
        self._set_value(v)

    def _step_up(self):
        self._set_value(self._clamp(self._value + self._step))

    def _step_down(self):
        self._set_value(self._clamp(self._value - self._step))

    def _set_value(self, v):
        if v != self._value:
            self._value = v
            self._edit.setText(self._format(v))
            self.valueChanged.emit(v)
        else:
            self._edit.setText(self._format(v))

    def value(self):
        return self._value

    def setValue(self, v):
        self._set_value(self._clamp(v))

    def setMinimum(self, v):
        self._min = v
        self.setValue(self._value)

    def setMaximum(self, v):
        self._max = v
        self.setValue(self._value)

    def setRange(self, mn, mx):
        self._min = mn
        self._max = mx
        self.setValue(self._value)

    def setSingleStep(self, v):
        self._step = v

    def setSuffix(self, s: str):
        """Görsel suffix — şu an yoksayılır, gerekirse edit'e eklenir."""
        self._suffix = s

    def setPrefix(self, s: str):
        """Görsel prefix — şu an yoksayılır."""
        self._prefix = s

    def setSpecialValueText(self, s: str):
        pass  # Uyumluluk için

    def setButtonSymbols(self, *args):
        pass  # Uyumluluk için

    def setAccelerated(self, *args):
        pass  # Uyumluluk için

    def setWrapping(self, *args):
        pass  # Uyumluluk için

    def setKeyboardTracking(self, *args):
        pass  # Uyumluluk için

    def setReadOnly(self, ro: bool):
        self._edit.setReadOnly(ro)
        self._btn_up.setEnabled(not ro)
        self._btn_down.setEnabled(not ro)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._edit.setEnabled(enabled)
        self._btn_up.setEnabled(enabled)
        self._btn_down.setEnabled(enabled)


class EmojiSpinBox(_BaseEmojiSpinBox):
    """Tam sayı spin box — QSpinBox yerine kullanılır."""
    valueChanged = pyqtSignal(int)

    def __init__(self, minimum=0, maximum=99, value=0, step=1, parent=None):
        super().__init__(minimum, maximum, value, step, parent)

    def _format(self, v):
        return str(int(v))

    def _parse(self, text):
        return int(text.strip())

    def value(self) -> int:
        return int(self._value)


class EmojiDoubleSpinBox(_BaseEmojiSpinBox):
    """Ondalıklı spin box — QDoubleSpinBox yerine kullanılır."""
    valueChanged = pyqtSignal(float)

    def __init__(self, minimum=0.0, maximum=99.0, value=0.0,
                 step=0.1, decimals=2, parent=None):
        self._decimals = decimals
        super().__init__(minimum, maximum, value, step, parent)

    def _format(self, v):
        return f"{v:.{self._decimals}f}"

    def _parse(self, text):
        return float(text.strip().replace(',', '.'))

    def setDecimals(self, d: int):
        self._decimals = d
        self._edit.setText(self._format(self._value))

    def value(self) -> float:
        return float(self._value)

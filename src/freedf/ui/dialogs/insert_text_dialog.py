"""Insert text on page dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class InsertTextDialog(QDialog):
    """Dialog for inserting text directly on a PDF page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Insert Text")
        self.setMinimumWidth(350)

        self.result_text: str = ""
        self.result_font_size: float = 12.0
        self.result_x: float = 72.0
        self.result_y: float = 72.0

        self._text_edit = QLineEdit()
        self._text_edit.setPlaceholderText("Text to insert...")

        self._font_size = QSpinBox()
        self._font_size.setRange(6, 200)
        self._font_size.setValue(12)

        self._x_spin = QSpinBox()
        self._x_spin.setRange(0, 2000)
        self._x_spin.setValue(72)

        self._y_spin = QSpinBox()
        self._y_spin.setRange(0, 2000)
        self._y_spin.setValue(72)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._confirm)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Text:"))
        layout.addWidget(self._text_edit)
        layout.addWidget(QLabel("Font size:"))
        layout.addWidget(self._font_size)
        layout.addWidget(QLabel("X position (pt):"))
        layout.addWidget(self._x_spin)
        layout.addWidget(QLabel("Y position (pt):"))
        layout.addWidget(self._y_spin)
        layout.addWidget(buttons)

    def _confirm(self) -> None:
        text = self._text_edit.text().strip()
        if not text:
            return
        self.result_text = text
        self.result_font_size = self._font_size.value()
        self.result_x = self._x_spin.value()
        self.result_y = self._y_spin.value()
        self.accept()

"""Watermark dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class WatermarkDialog(QDialog):
    """Dialog for adding a text watermark to pages."""

    def __init__(self, page_count: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Watermark")
        self.setMinimumWidth(350)

        self.result_text: str = ""
        self.result_font_size: float = 60.0
        self.result_opacity: float = 0.3
        self.result_all_pages: bool = True

        self._text_edit = QLineEdit()
        self._text_edit.setPlaceholderText("Watermark text...")
        self._text_edit.setText("DRAFT")

        self._font_size = QSpinBox()
        self._font_size.setRange(10, 200)
        self._font_size.setValue(60)

        self._opacity_spin = QSpinBox()
        self._opacity_spin.setRange(5, 100)
        self._opacity_spin.setValue(30)
        self._opacity_spin.setSuffix("%")

        self._all_pages_cb = QCheckBox(f"All pages ({page_count})")
        self._all_pages_cb.setChecked(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._confirm)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Watermark text:"))
        layout.addWidget(self._text_edit)
        layout.addWidget(QLabel("Font size:"))
        layout.addWidget(self._font_size)
        layout.addWidget(QLabel("Opacity:"))
        layout.addWidget(self._opacity_spin)
        layout.addWidget(self._all_pages_cb)
        layout.addWidget(buttons)

    def _confirm(self) -> None:
        text = self._text_edit.text().strip()
        if not text:
            return
        self.result_text = text
        self.result_font_size = self._font_size.value()
        self.result_opacity = self._opacity_spin.value() / 100.0
        self.result_all_pages = self._all_pages_cb.isChecked()
        self.accept()

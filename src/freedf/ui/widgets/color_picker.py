"""Color picker button widget."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QColorDialog, QToolButton, QWidget

from freedf.core.annotations import Color


class ColorPickerButton(QToolButton):
    """A tool button that shows a color swatch and opens a color dialog."""

    color_changed = Signal(object)  # emits Color

    def __init__(
        self, initial: Color | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._color = initial or Color(1.0, 1.0, 0.0)
        self.setToolTip("Annotation color")
        self.clicked.connect(self._pick_color)
        self._update_swatch()

    @property
    def color(self) -> Color:
        return self._color

    def set_color(self, color: Color) -> None:
        self._color = color
        self._update_swatch()

    def _pick_color(self) -> None:
        qc = QColor(
            int(self._color.r * 255),
            int(self._color.g * 255),
            int(self._color.b * 255),
        )
        result = QColorDialog.getColor(qc, self, "Annotation Color")
        if result.isValid():
            self._color = Color(result.redF(), result.greenF(), result.blueF())
            self._update_swatch()
            self.color_changed.emit(self._color)

    def _update_swatch(self) -> None:
        pixmap = QPixmap(16, 16)
        pixmap.fill(
            QColor(
                int(self._color.r * 255),
                int(self._color.g * 255),
                int(self._color.b * 255),
            )
        )
        self.setIcon(pixmap)  # type: ignore[arg-type]

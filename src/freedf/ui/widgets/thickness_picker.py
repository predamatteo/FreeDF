"""Thickness picker combo box widget."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QWidget


class ThicknessPicker(QComboBox):
    """Combo box for selecting annotation line thickness."""

    thickness_changed = Signal(float)

    THICKNESSES: list[float] = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]  # noqa: RUF012

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setToolTip("Line thickness")
        for t in self.THICKNESSES:
            self.addItem(f"{t:.1f}px", t)
        self.setCurrentIndex(3)  # default 2.0
        self.currentIndexChanged.connect(self._on_changed)

    @property
    def thickness(self) -> float:
        return float(self.currentData() or 2.0)

    def _on_changed(self, _index: int) -> None:
        self.thickness_changed.emit(self.thickness)

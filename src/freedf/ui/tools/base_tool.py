"""Base tool protocol for UI interaction tools."""

from __future__ import annotations

from typing import Protocol

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsSceneMouseEvent


class Tool(Protocol):
    """Protocol for UI interaction tools."""

    @property
    def name(self) -> str: ...

    def activate(self) -> None: ...

    def deactivate(self) -> None: ...

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        """Handle mouse press. Return True if handled."""
        ...

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        """Handle mouse move. Return True if handled."""
        ...

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        """Handle mouse release. Return True if handled."""
        ...

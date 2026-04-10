"""Redaction tool — drag to black out areas of the page."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent

from freedf.core.annotations import Rect

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene


class RedactTool:
    """Drag to select an area and apply black redaction."""

    def __init__(
        self,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_scene: Callable[[], PageScene],
        get_zoom: Callable[[], float],
        execute_command: Callable[[object], None],
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom
        self._execute_command = execute_command
        self._start: QPointF | None = None
        self._preview: QGraphicsRectItem | None = None

    @property
    def name(self) -> str:
        return "redact"

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        self._clear_preview()

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        self._start = pdf_pos
        return True

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if self._start is None:
            return False
        self._update_preview(self._start, pdf_pos)
        return True

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if self._start is None:
            return False
        start = self._start
        self._start = None
        self._clear_preview()
        self._apply_redaction(start, pdf_pos)
        return True

    def _update_preview(self, p1: QPointF, p2: QPointF) -> None:
        self._clear_preview()
        z = self._get_zoom()
        x0, y0 = min(p1.x(), p2.x()) * z, min(p1.y(), p2.y()) * z
        x1, y1 = max(p1.x(), p2.x()) * z, max(p1.y(), p2.y()) * z
        rect = QRectF(x0, y0, x1 - x0, y1 - y0)
        self._preview = QGraphicsRectItem(rect)
        self._preview.setBrush(QBrush(QColor(0, 0, 0, 120)))
        self._preview.setPen(QPen(QColor(255, 0, 0), 1))
        self._get_scene().addItem(self._preview)

    def _clear_preview(self) -> None:
        if self._preview:
            self._get_scene().removeItem(self._preview)
            self._preview = None

    def _apply_redaction(self, p1: QPointF, p2: QPointF) -> None:
        from freedf.commands.text_commands import RedactAreaCommand

        doc = self._get_document()
        if doc is None:
            return

        rect = Rect(
            min(p1.x(), p2.x()),
            min(p1.y(), p2.y()),
            max(p1.x(), p2.x()),
            max(p1.y(), p2.y()),
        )
        cmd = RedactAreaCommand(
            document=doc,
            page_number=self._get_page_number(),
            rect=rect,
        )
        self._execute_command(cmd)

"""QGraphicsScene for displaying PDF pages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QPointF
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
)

if TYPE_CHECKING:
    from freedf.ui.tools.tool_manager import ToolManager


class PageScene(QGraphicsScene):
    """Manages the page pixmap, overlays, and tool event forwarding."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._page_item: QGraphicsPixmapItem | None = None
        self._overlay_items: list[QGraphicsItem] = []
        self._zoom: float = 1.0
        self._tool_manager: ToolManager | None = None

    def set_tool_manager(self, manager: ToolManager) -> None:
        self._tool_manager = manager

    def set_zoom(self, zoom: float) -> None:
        self._zoom = zoom

    @property
    def zoom(self) -> float:
        return self._zoom

    def scene_to_pdf(self, scene_point: QPointF) -> QPointF:
        """Convert scene coordinates to PDF points."""
        return QPointF(scene_point.x() / self._zoom, scene_point.y() / self._zoom)

    def pdf_to_scene(self, pdf_x: float, pdf_y: float) -> QPointF:
        """Convert PDF points to scene coordinates."""
        return QPointF(pdf_x * self._zoom, pdf_y * self._zoom)

    def set_page_pixmap(self, pixmap: QPixmap) -> None:
        """Replace the current page pixmap."""
        if self._page_item is not None:
            self.removeItem(self._page_item)
        self._page_item = self.addPixmap(pixmap)
        self._page_item.setPos(0, 0)
        self.setSceneRect(self._page_item.boundingRect())

    def clear_page(self) -> None:
        """Remove the page pixmap."""
        if self._page_item is not None:
            self.removeItem(self._page_item)
            self._page_item = None

    def add_overlay(self, item: QGraphicsItem) -> None:
        self.addItem(item)
        self._overlay_items.append(item)

    def clear_overlays(self) -> None:
        for item in self._overlay_items:
            self.removeItem(item)
        self._overlay_items.clear()

    # --- Mouse event forwarding to tools ---

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        if self._tool_manager and self._tool_manager.current_tool:
            pdf_pos = self.scene_to_pdf(event.scenePos())
            if self._tool_manager.current_tool.mouse_press(event, pdf_pos):
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        if self._tool_manager and self._tool_manager.current_tool:
            pdf_pos = self.scene_to_pdf(event.scenePos())
            if self._tool_manager.current_tool.mouse_move(event, pdf_pos):
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:  # noqa: N802
        if self._tool_manager and self._tool_manager.current_tool:
            pdf_pos = self.scene_to_pdf(event.scenePos())
            if self._tool_manager.current_tool.mouse_release(event, pdf_pos):
                event.accept()
                return
        super().mouseReleaseEvent(event)

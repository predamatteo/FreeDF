"""QGraphicsScene for displaying PDF pages."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene


class PageScene(QGraphicsScene):
    """Manages the page pixmap and future annotation overlays."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._page_item: QGraphicsPixmapItem | None = None

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

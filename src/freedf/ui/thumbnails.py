"""Page thumbnail sidebar panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QListView,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from freedf.ui.page_view import PageView

if TYPE_CHECKING:
    from freedf.rendering.cache import RenderCache

THUMBNAIL_SIZE = 160
PADDING = 12


class ThumbnailPanel(QWidget):
    """Sidebar showing page thumbnails."""

    page_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._list_widget = QListWidget(self)
        self._list_widget.setViewMode(QListView.ViewMode.IconMode)
        self._list_widget.setIconSize(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        self._list_widget.setSpacing(PADDING)
        self._list_widget.setMovement(QListView.Movement.Static)
        self._list_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self._list_widget.setFlow(QListView.Flow.TopToBottom)
        self._list_widget.setWrapping(False)
        self._list_widget.setUniformItemSizes(False)

        self._list_widget.currentRowChanged.connect(self._on_row_changed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list_widget)

        self.setMinimumWidth(THUMBNAIL_SIZE + 40)
        self.setMaximumWidth(THUMBNAIL_SIZE + 60)

    def populate(self, cache: RenderCache, page_count: int) -> None:
        """Generate and display all thumbnails."""
        self._list_widget.clear()
        for i in range(page_count):
            pil_img = cache.get_thumbnail(i, max_size=THUMBNAIL_SIZE)
            qimage = PageView._pil_to_qimage(pil_img)
            pixmap = QPixmap.fromImage(qimage)
            item = QListWidgetItem(QIcon(pixmap), str(i + 1))
            self._list_widget.addItem(item)

    def set_current_page(self, index: int) -> None:
        """Highlight the current page thumbnail."""
        self._list_widget.blockSignals(True)
        self._list_widget.setCurrentRow(index)
        self._list_widget.blockSignals(False)

    def _on_row_changed(self, row: int) -> None:
        if row >= 0:
            self.page_selected.emit(row)

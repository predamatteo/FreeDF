"""Page thumbnail sidebar panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
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
    """Sidebar showing page thumbnails with drag-and-drop reordering."""

    page_selected = Signal(int)
    page_reordered = Signal(int, int)  # from_index, to_index

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._list_widget = _ReorderListWidget(self)
        self._list_widget.setViewMode(QListView.ViewMode.IconMode)
        self._list_widget.setIconSize(QSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        self._list_widget.setSpacing(PADDING)
        self._list_widget.setMovement(QListView.Movement.Free)
        self._list_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self._list_widget.setFlow(QListView.Flow.TopToBottom)
        self._list_widget.setWrapping(False)
        self._list_widget.setUniformItemSizes(False)
        self._list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)

        self._list_widget.currentRowChanged.connect(self._on_row_changed)
        self._list_widget.row_moved.connect(self._on_row_moved)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list_widget)

        self.setMinimumWidth(THUMBNAIL_SIZE + 40)
        self.setMaximumWidth(THUMBNAIL_SIZE + 60)

    def populate(self, cache: RenderCache, page_count: int) -> None:
        """Generate and display all thumbnails."""
        self._list_widget.blockSignals(True)
        self._list_widget.clear()
        for i in range(page_count):
            pil_img = cache.get_thumbnail(i, max_size=THUMBNAIL_SIZE)
            qimage = PageView._pil_to_qimage(pil_img)
            pixmap = QPixmap.fromImage(qimage)
            item = QListWidgetItem(QIcon(pixmap), str(i + 1))
            item.setData(256, i)  # store original page index
            self._list_widget.addItem(item)
        self._list_widget.blockSignals(False)

    def set_current_page(self, index: int) -> None:
        """Highlight the current page thumbnail."""
        self._list_widget.blockSignals(True)
        self._list_widget.setCurrentRow(index)
        self._list_widget.blockSignals(False)

    def _on_row_changed(self, row: int) -> None:
        if row >= 0:
            self.page_selected.emit(row)

    def _on_row_moved(self, from_row: int, to_row: int) -> None:
        self.page_reordered.emit(from_row, to_row)


class _ReorderListWidget(QListWidget):
    """QListWidget subclass that emits row_moved on internal drag-drop."""

    row_moved = Signal(int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._drag_start_row: int = -1

    def startDrag(self, supported_actions: object) -> None:  # noqa: N802
        self._drag_start_row = self.currentRow()
        super().startDrag(supported_actions)  # type: ignore[arg-type]

    def dropEvent(self, event: object) -> None:  # noqa: N802
        from_row = self._drag_start_row
        super().dropEvent(event)  # type: ignore[arg-type]
        to_row = self.currentRow()
        if from_row >= 0 and from_row != to_row:
            self.row_moved.emit(from_row, to_row)
        self._drag_start_row = -1

"""Annotation list sidebar panel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from freedf.core.document import Document


class AnnotationPanel(QWidget):
    """Sidebar showing annotations on the current page."""

    annotation_selected = Signal(str)  # annot_id
    annotation_delete_requested = Signal(str)  # annot_id

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._header = QLabel("Annotations")
        self._header.setStyleSheet("font-weight: bold; padding: 8px;")

        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_item_changed)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._header)
        layout.addWidget(self._list)
        layout.addWidget(self._delete_btn)

        self.setMinimumWidth(180)
        self.setMaximumWidth(220)

    def refresh(self, document: Document | None, page_number: int) -> None:
        """Rebuild the annotation list for the given page."""
        self._list.clear()
        self._delete_btn.setEnabled(False)
        if document is None:
            return
        try:
            page = document.get_page(page_number)
        except Exception:
            return

        for annot in page.get_annotations():
            label = annot.annot_type.name
            if annot.content:
                label += f": {annot.content[:30]}"
            item = QListWidgetItem(label)
            item.setData(256, annot.annot_id)
            self._list.addItem(item)

    def _on_item_changed(
        self, current: QListWidgetItem | None, _prev: QListWidgetItem | None
    ) -> None:
        if current:
            annot_id = current.data(256)
            self._delete_btn.setEnabled(True)
            if annot_id:
                self.annotation_selected.emit(str(annot_id))
        else:
            self._delete_btn.setEnabled(False)

    def _on_delete(self) -> None:
        current = self._list.currentItem()
        if current:
            annot_id = current.data(256)
            if annot_id:
                self.annotation_delete_requested.emit(str(annot_id))

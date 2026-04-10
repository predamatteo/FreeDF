"""Text selection tool — select text on page for copying."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QPen
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsSceneMouseEvent,
    QMenu,
)

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene


class TextSelectorTool:
    """Select text on a page for copying to clipboard."""

    def __init__(
        self,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_scene: Callable[[], PageScene],
        get_zoom: Callable[[], float],
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom

        self._drag_start: QPointF | None = None
        self._selection_rects: list[QGraphicsRectItem] = []
        self._selected_text: str = ""
        self._word_data: list[tuple[float, ...]] = []

    @property
    def name(self) -> str:
        return "text_select"

    def activate(self) -> None:
        self._load_words()

    def deactivate(self) -> None:
        self._clear_overlays()
        self._word_data = []

    def _load_words(self) -> None:
        doc = self._get_document()
        if doc is None:
            self._word_data = []
            return
        self._word_data = doc.get_text_words(self._get_page_number())

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if event.button() == Qt.MouseButton.RightButton:
            if self._selected_text:
                self._show_context_menu(event)
                return True
            return False
        if event.button() != Qt.MouseButton.LeftButton:
            return False
        self._load_words()
        self._drag_start = pdf_pos
        self._clear_overlays()
        return True

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if self._drag_start is None:
            return False
        self._clear_overlays()
        self._update_selection(self._drag_start, pdf_pos)
        return True

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if self._drag_start is None:
            return False
        self._update_selection(self._drag_start, pdf_pos)
        self._drag_start = None
        return True

    def _update_selection(self, p1: QPointF, p2: QPointF) -> None:
        self._clear_overlays()
        selected = self._words_in_rect(p1, p2)
        self._selected_text = " ".join(str(w[4]) for w in selected)

        zoom = self._get_zoom()
        scene = self._get_scene()
        brush = QBrush(QColor(33, 150, 243, 60))
        pen = QPen(Qt.PenStyle.NoPen)

        for w in selected:
            rx, ry = float(w[0]) * zoom, float(w[1]) * zoom
            rw = (float(w[2]) - float(w[0])) * zoom
            rh = (float(w[3]) - float(w[1])) * zoom
            item = QGraphicsRectItem(QRectF(rx, ry, rw, rh))
            item.setBrush(brush)
            item.setPen(pen)
            scene.addItem(item)
            self._selection_rects.append(item)

    def _words_in_rect(self, p1: QPointF, p2: QPointF) -> list[tuple[float, ...]]:
        x0, x1 = min(p1.x(), p2.x()), max(p1.x(), p2.x())
        y0, y1 = min(p1.y(), p2.y()), max(p1.y(), p2.y())
        selected = []
        for w in self._word_data:
            wx0, wy0, wx1, wy1 = float(w[0]), float(w[1]), float(w[2]), float(w[3])
            if not (wx1 < x0 or x1 < wx0 or wy1 < y0 or y1 < wy0):
                selected.append(w)
        return selected

    def _clear_overlays(self) -> None:
        scene = self._get_scene()
        for item in self._selection_rects:
            scene.removeItem(item)
        self._selection_rects.clear()

    def _show_context_menu(self, event: QGraphicsSceneMouseEvent) -> None:
        menu = QMenu()
        copy_action = menu.addAction("Copy")
        action = menu.exec(event.screenPos())  # type: ignore[arg-type]
        if action == copy_action:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(self._selected_text)

"""Highlight tool — select text and create highlight annotations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import fitz
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent

if TYPE_CHECKING:
    from freedf.core.annotations import Color
    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene
    from freedf.ui.tools.tool_manager import ToolManager

CommandCallback = Callable[[object], None]


class HighlightTool:
    """Text selection + highlight annotation creation."""

    def __init__(
        self,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_scene: Callable[[], PageScene],
        get_zoom: Callable[[], float],
        tool_manager: ToolManager,
        execute_command: CommandCallback,
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom
        self._tool_manager = tool_manager
        self._execute_command = execute_command

        self._drag_start: QPointF | None = None
        self._selection_rects: list[QGraphicsRectItem] = []
        self._word_data: list[tuple[float, ...]] = []

    @property
    def name(self) -> str:
        return "highlight"

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
        page_num = self._get_page_number()
        self._word_data = doc.get_text_words(page_num)

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
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
        self._show_selection(self._drag_start, pdf_pos)
        return True

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if self._drag_start is None:
            return False

        selected_words = self._words_in_rect(self._drag_start, pdf_pos)
        self._clear_overlays()
        self._drag_start = None

        if not selected_words:
            return True

        self._create_highlight(selected_words)
        return True

    def _words_in_rect(self, p1: QPointF, p2: QPointF) -> list[tuple[float, ...]]:
        """Find all words whose bounding boxes overlap the selection rect."""
        x0 = min(p1.x(), p2.x())
        y0 = min(p1.y(), p2.y())
        x1 = max(p1.x(), p2.x())
        y1 = max(p1.y(), p2.y())

        selected = []
        for w in self._word_data:
            wx0, wy0, wx1, wy1 = w[0], w[1], w[2], w[3]
            if not (wx1 < x0 or x1 < wx0 or wy1 < y0 or y1 < wy0):
                selected.append(w)
        return selected

    def _show_selection(self, p1: QPointF, p2: QPointF) -> None:
        """Draw selection highlight over selected words."""
        selected = self._words_in_rect(p1, p2)
        zoom = self._get_zoom()
        scene = self._get_scene()
        brush = QBrush(QColor(46, 125, 50, 60))  # green accent, semi-transparent
        pen = QPen(Qt.PenStyle.NoPen)

        for w in selected:
            rx, ry = w[0] * zoom, w[1] * zoom
            rw = (w[2] - w[0]) * zoom
            rh = (w[3] - w[1]) * zoom
            rect = QRectF(rx, ry, rw, rh)
            item = QGraphicsRectItem(rect)
            item.setBrush(brush)
            item.setPen(pen)
            scene.addItem(item)
            self._selection_rects.append(item)

    def _clear_overlays(self) -> None:
        scene = self._get_scene()
        for item in self._selection_rects:
            scene.removeItem(item)
        self._selection_rects.clear()

    def _create_highlight(
        self,
        words: list[tuple[float, ...]],
    ) -> None:
        """Group words by line, create quads, and execute highlight command."""
        from freedf.commands.annotation_commands import AddHighlightCommand

        # Group by line
        lines: dict[int, list[tuple[float, ...]]] = {}
        for w in words:
            line_no = int(w[6])
            if line_no not in lines:
                lines[line_no] = []
            lines[line_no].append(w)

        quads: list[fitz.Quad] = []
        for line_words in lines.values():
            x0 = min(w[0] for w in line_words)
            y0 = min(w[1] for w in line_words)
            x1 = max(w[2] for w in line_words)
            y1 = max(w[3] for w in line_words)
            quad = fitz.Quad(
                fitz.Point(x0, y0),  # upper-left
                fitz.Point(x1, y0),  # upper-right
                fitz.Point(x0, y1),  # lower-left
                fitz.Point(x1, y1),  # lower-right
            )
            quads.append(quad)

        if not quads:
            return

        doc = self._get_document()
        if doc is None:
            return

        color: Color = self._tool_manager.current_color
        opacity = self._tool_manager.current_opacity

        cmd = AddHighlightCommand(
            document=doc,
            page_number=self._get_page_number(),
            quads=quads,
            color=color,
            opacity=opacity,
        )
        self._execute_command(cmd)

"""Ink tool — freehand drawing annotation."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsSceneMouseEvent

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene
    from freedf.ui.tools.tool_manager import ToolManager


class InkTool:
    """Freehand ink drawing tool."""

    def __init__(
        self,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_scene: Callable[[], PageScene],
        get_zoom: Callable[[], float],
        tool_manager: ToolManager,
        execute_command: Callable[[object], None],
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom
        self._tool_manager = tool_manager
        self._execute_command = execute_command

        self._current_stroke: list[tuple[float, float]] = []
        self._all_strokes: list[list[tuple[float, float]]] = []
        self._preview_item: QGraphicsPathItem | None = None
        self._drawing: bool = False

    @property
    def name(self) -> str:
        return "ink"

    def activate(self) -> None:
        self._all_strokes = []

    def deactivate(self) -> None:
        if self._all_strokes:
            self._finalize()
        self._clear_preview()

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            if event.button() == Qt.MouseButton.RightButton and self._all_strokes:
                self._finalize()
                return True
            return False
        self._drawing = True
        self._current_stroke = [(pdf_pos.x(), pdf_pos.y())]
        return True

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if not self._drawing:
            return False
        self._current_stroke.append((pdf_pos.x(), pdf_pos.y()))
        self._update_preview()
        return True

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if not self._drawing:
            return False
        self._drawing = False
        if len(self._current_stroke) > 1:
            self._all_strokes.append(self._current_stroke)
            self._current_stroke = []
            self._finalize()
        return True

    def _update_preview(self) -> None:
        from PySide6.QtGui import QPainterPath

        self._clear_preview()
        if not self._current_stroke:
            return

        zoom = self._get_zoom()
        path = QPainterPath()
        pts = self._current_stroke
        path.moveTo(pts[0][0] * zoom, pts[0][1] * zoom)
        for x, y in pts[1:]:
            path.lineTo(x * zoom, y * zoom)

        scene = self._get_scene()
        self._preview_item = QGraphicsPathItem(path)
        pen = QPen(QColor(46, 125, 50), self._tool_manager.current_thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self._preview_item.setPen(pen)
        scene.addItem(self._preview_item)

    def _clear_preview(self) -> None:
        if self._preview_item:
            scene = self._get_scene()
            scene.removeItem(self._preview_item)
            self._preview_item = None

    def _finalize(self) -> None:
        from freedf.commands.annotation_commands import AddInkCommand

        self._clear_preview()
        doc = self._get_document()
        if doc is None or not self._all_strokes:
            return

        cmd = AddInkCommand(
            document=doc,
            page_number=self._get_page_number(),
            strokes=list(self._all_strokes),
            color=self._tool_manager.current_color,
            width=self._tool_manager.current_thickness,
            opacity=self._tool_manager.current_opacity,
        )
        self._all_strokes = []
        self._execute_command(cmd)

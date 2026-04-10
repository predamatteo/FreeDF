"""Shape tools — rectangle, ellipse, line, arrow annotations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsSceneMouseEvent,
)

from freedf.core.annotations import AnnotationType, Rect

if TYPE_CHECKING:
    from PySide6.QtWidgets import QGraphicsItem

    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene
    from freedf.ui.tools.tool_manager import ToolManager


class _ShapeToolBase:
    """Base for rubber-band shape tools."""

    def __init__(
        self,
        tool_name: str,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_scene: Callable[[], PageScene],
        get_zoom: Callable[[], float],
        tool_manager: ToolManager,
        execute_command: Callable[[object], None],
    ) -> None:
        self._name = tool_name
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom
        self._tool_manager = tool_manager
        self._execute_command = execute_command
        self._start: QPointF | None = None
        self._preview: QGraphicsItem | None = None

    @property
    def name(self) -> str:
        return self._name

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
        self._create_annotation(start, pdf_pos)
        return True

    def _update_preview(self, p1: QPointF, p2: QPointF) -> None:
        raise NotImplementedError

    def _create_annotation(self, p1: QPointF, p2: QPointF) -> None:
        raise NotImplementedError

    def _clear_preview(self) -> None:
        if self._preview:
            self._get_scene().removeItem(self._preview)
            self._preview = None

    def _make_pen(self) -> QPen:
        c = self._tool_manager.current_color
        pen = QPen(QColor(int(c.r * 255), int(c.g * 255), int(c.b * 255)))
        pen.setWidthF(self._tool_manager.current_thickness)
        return pen

    def _ordered_rect(self, p1: QPointF, p2: QPointF) -> Rect:
        return Rect(
            min(p1.x(), p2.x()),
            min(p1.y(), p2.y()),
            max(p1.x(), p2.x()),
            max(p1.y(), p2.y()),
        )

    def _scene_rect(self, p1: QPointF, p2: QPointF) -> QRectF:
        z = self._get_zoom()
        x0, y0 = min(p1.x(), p2.x()) * z, min(p1.y(), p2.y()) * z
        x1, y1 = max(p1.x(), p2.x()) * z, max(p1.y(), p2.y()) * z
        return QRectF(x0, y0, x1 - x0, y1 - y0)


class RectTool(_ShapeToolBase):
    def __init__(self, **kwargs: object) -> None:
        super().__init__("rect", **kwargs)  # type: ignore[arg-type]

    def _update_preview(self, p1: QPointF, p2: QPointF) -> None:
        self._clear_preview()
        item = QGraphicsRectItem(self._scene_rect(p1, p2))
        item.setPen(self._make_pen())
        self._get_scene().addItem(item)
        self._preview = item

    def _create_annotation(self, p1: QPointF, p2: QPointF) -> None:
        from freedf.commands.annotation_commands import AddShapeCommand

        doc = self._get_document()
        if doc is None:
            return
        cmd = AddShapeCommand(
            document=doc,
            page_number=self._get_page_number(),
            shape_type=AnnotationType.SQUARE,
            rect=self._ordered_rect(p1, p2),
            stroke_color=self._tool_manager.current_color,
            width=self._tool_manager.current_thickness,
        )
        self._execute_command(cmd)


class EllipseTool(_ShapeToolBase):
    def __init__(self, **kwargs: object) -> None:
        super().__init__("ellipse", **kwargs)  # type: ignore[arg-type]

    def _update_preview(self, p1: QPointF, p2: QPointF) -> None:
        self._clear_preview()
        item = QGraphicsEllipseItem(self._scene_rect(p1, p2))
        item.setPen(self._make_pen())
        self._get_scene().addItem(item)
        self._preview = item

    def _create_annotation(self, p1: QPointF, p2: QPointF) -> None:
        from freedf.commands.annotation_commands import AddShapeCommand

        doc = self._get_document()
        if doc is None:
            return
        cmd = AddShapeCommand(
            document=doc,
            page_number=self._get_page_number(),
            shape_type=AnnotationType.CIRCLE,
            rect=self._ordered_rect(p1, p2),
            stroke_color=self._tool_manager.current_color,
            width=self._tool_manager.current_thickness,
        )
        self._execute_command(cmd)


class LineTool(_ShapeToolBase):
    def __init__(self, *, arrow: bool = False, **kwargs: object) -> None:
        name = "arrow" if arrow else "line"
        super().__init__(name, **kwargs)  # type: ignore[arg-type]
        self._arrow = arrow

    def _update_preview(self, p1: QPointF, p2: QPointF) -> None:
        self._clear_preview()
        z = self._get_zoom()
        item = QGraphicsLineItem(p1.x() * z, p1.y() * z, p2.x() * z, p2.y() * z)
        item.setPen(self._make_pen())
        self._get_scene().addItem(item)
        self._preview = item

    def _create_annotation(self, p1: QPointF, p2: QPointF) -> None:
        from freedf.commands.annotation_commands import AddLineCommand

        doc = self._get_document()
        if doc is None:
            return
        cmd = AddLineCommand(
            document=doc,
            page_number=self._get_page_number(),
            start=(p1.x(), p1.y()),
            end=(p2.x(), p2.y()),
            color=self._tool_manager.current_color,
            width=self._tool_manager.current_thickness,
            arrow=self._arrow,
        )
        self._execute_command(cmd)

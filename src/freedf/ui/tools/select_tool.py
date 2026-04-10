"""Select tool — pan, annotation selection, move, delete."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsSceneMouseEvent,
    QMenu,
)

from freedf.core.annotations import AnnotationData, Rect

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene


class SelectTool:
    """Default tool: pan, annotation selection, move, and context menu."""

    def __init__(
        self,
        get_document: Callable[[], Document | None] | None = None,
        get_page_number: Callable[[], int] | None = None,
        get_scene: Callable[[], PageScene] | None = None,
        get_zoom: Callable[[], float] | None = None,
        execute_command: Callable[[object], None] | None = None,
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom
        self._execute_command = execute_command

        self._selected_annot: AnnotationData | None = None
        self._selection_rect: QGraphicsRectItem | None = None
        self._dragging: bool = False
        self._drag_start: QPointF | None = None

    @property
    def name(self) -> str:
        return "select"

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        self._clear_selection()

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if self._get_document is None:
            return False

        doc = self._get_document()
        if doc is None:
            return False

        if event.button() == Qt.MouseButton.RightButton:
            hit = self._hit_test(pdf_pos)
            if hit:
                self._select(hit)
                self._show_context_menu(event, hit)
                return True
            return False

        if event.button() != Qt.MouseButton.LeftButton:
            return False

        hit = self._hit_test(pdf_pos)
        if hit:
            self._select(hit)
            self._dragging = True
            self._drag_start = pdf_pos
            return True

        self._clear_selection()
        return False  # let QGraphicsView handle pan

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        return self._dragging and self._selected_annot is not None

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if not self._dragging or self._selected_annot is None:
            self._dragging = False
            return False

        self._dragging = False
        if self._drag_start is None:
            return False

        dx = pdf_pos.x() - self._drag_start.x()
        dy = pdf_pos.y() - self._drag_start.y()
        self._drag_start = None

        if abs(dx) < 2 and abs(dy) < 2:
            return True  # click, not drag

        self._move_annotation(self._selected_annot, dx, dy)
        return True

    def _hit_test(self, pdf_pos: QPointF) -> AnnotationData | None:
        if self._get_document is None or self._get_page_number is None:
            return None
        doc = self._get_document()
        if doc is None:
            return None
        page = doc.get_page(self._get_page_number())
        px, py = pdf_pos.x(), pdf_pos.y()
        for annot in page.get_annotations():
            r = annot.rect
            if r.x0 <= px <= r.x1 and r.y0 <= py <= r.y1:
                return annot
        return None

    def _select(self, annot: AnnotationData) -> None:
        self._clear_selection()
        self._selected_annot = annot
        if self._get_scene is None or self._get_zoom is None:
            return
        z = self._get_zoom()
        scene = self._get_scene()
        r = annot.rect
        rect = QRectF(r.x0 * z, r.y0 * z, r.width * z, r.height * z)
        self._selection_rect = QGraphicsRectItem(rect)
        pen = QPen(QColor(46, 125, 50), 2, Qt.PenStyle.DashLine)
        self._selection_rect.setPen(pen)
        self._selection_rect.setBrush(QColor(46, 125, 50, 20))
        scene.addItem(self._selection_rect)

    def _clear_selection(self) -> None:
        if self._selection_rect and self._get_scene:
            self._get_scene().removeItem(self._selection_rect)
        self._selection_rect = None
        self._selected_annot = None

    def _show_context_menu(
        self, event: QGraphicsSceneMouseEvent, annot: AnnotationData
    ) -> None:
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec(event.screenPos())  # type: ignore[arg-type]
        if action == delete_action:
            self._delete_annotation(annot)

    def _delete_annotation(self, annot: AnnotationData) -> None:
        from freedf.commands.annotation_commands import DeleteAnnotationCommand

        if self._get_document is None or self._get_page_number is None:
            return
        doc = self._get_document()
        if doc is None:
            return
        cmd = DeleteAnnotationCommand(
            document=doc,
            page_number=self._get_page_number(),
            annot_id=annot.annot_id,
        )
        if self._execute_command:
            self._execute_command(cmd)
        self._clear_selection()

    def _move_annotation(self, annot: AnnotationData, dx: float, dy: float) -> None:
        from freedf.commands.annotation_commands import ModifyAnnotationCommand

        if self._get_document is None or self._get_page_number is None:
            return
        doc = self._get_document()
        if doc is None:
            return

        r = annot.rect
        new_rect = Rect(r.x0 + dx, r.y0 + dy, r.x1 + dx, r.y1 + dy)
        cmd = ModifyAnnotationCommand(
            document=doc,
            page_number=self._get_page_number(),
            annot_id=annot.annot_id,
            new_props={"rect": new_rect},
        )
        if self._execute_command:
            self._execute_command(cmd)
        self._clear_selection()

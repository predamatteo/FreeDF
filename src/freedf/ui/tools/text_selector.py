"""Text selection tool — select text on page for copying, editing, deleting."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QPen
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsSceneMouseEvent,
    QInputDialog,
    QMenu,
    QMessageBox,
)

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.page_scene import PageScene


class TextSelectorTool:
    """Select text on a page for copying, replacing, or deleting."""

    def __init__(
        self,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_scene: Callable[[], PageScene],
        get_zoom: Callable[[], float],
        execute_command: Callable[[object], None] | None = None,
        get_parent_widget: Callable[[], object] | None = None,
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_scene = get_scene
        self._get_zoom = get_zoom
        self._execute_command = execute_command
        self._get_parent = get_parent_widget

        self._drag_start: QPointF | None = None
        self._selection_rects: list[QGraphicsRectItem] = []
        self._selected_text: str = ""
        self._selected_words: list[tuple[float, ...]] = []
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
        self._selected_words = self._words_in_rect(p1, p2)
        self._selected_text = " ".join(str(w[4]) for w in self._selected_words)

        zoom = self._get_zoom()
        scene = self._get_scene()
        brush = QBrush(QColor(33, 150, 243, 60))
        pen = QPen(Qt.PenStyle.NoPen)

        for w in self._selected_words:
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
            wx0, wy0, wx1, wy1 = (
                float(w[0]),
                float(w[1]),
                float(w[2]),
                float(w[3]),
            )
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
        edit_action = menu.addAction("Edit...")
        replace_action = menu.addAction("Replace...")
        delete_action = menu.addAction("Delete")

        action = menu.exec(event.screenPos())  # type: ignore[arg-type]
        if action == copy_action:
            self._do_copy()
        elif action == edit_action:
            self._do_edit()
        elif action == replace_action:
            self._do_replace()
        elif action == delete_action:
            self._do_delete()

    def _do_copy(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(self._selected_text)

    def _do_edit(self) -> None:
        """Open dialog to edit the selected text in-place."""
        if not self._selected_text or not self._execute_command:
            return
        parent = self._get_parent() if self._get_parent else None
        new_text, ok = QInputDialog.getText(
            parent,  # type: ignore[arg-type]
            "Edit Text",
            "New text:",
            text=self._selected_text,
        )
        if not ok:
            return
        self._replace_selected_with(new_text)

    def _do_replace(self) -> None:
        """Open dialog to replace the selected text."""
        if not self._selected_text or not self._execute_command:
            return
        parent = self._get_parent() if self._get_parent else None
        new_text, ok = QInputDialog.getText(
            parent,  # type: ignore[arg-type]
            "Replace Text",
            f"Replace '{self._selected_text}' with:",
        )
        if not ok:
            return
        self._replace_selected_with(new_text)

    def _do_delete(self) -> None:
        """Delete the selected text from the page."""
        if not self._selected_text or not self._execute_command:
            return
        parent = self._get_parent() if self._get_parent else None
        reply = QMessageBox.question(
            parent,  # type: ignore[arg-type]
            "Delete Text",
            f"Delete '{self._selected_text}'?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._replace_selected_with("")

    def _replace_selected_with(self, new_text: str) -> None:
        """Replace each selected word with new_text (first word gets text,
        rest get deleted). Uses per-word redaction for precise targeting."""
        from freedf.commands.text_commands import DeleteTextCommand, ReplaceTextCommand

        doc = self._get_document()
        if doc is None or not self._execute_command:
            return

        page_num = self._get_page_number()

        if not self._selected_words:
            return

        from freedf.core.annotations import Color as _Color
        from freedf.core.text_edit import detect_text_style_at

        # Detect original style from the first selected word
        first = self._selected_words[0]
        style = detect_text_style_at(
            doc, page_num, float(first[0]), float(first[1]), str(first[4])
        )
        orig_color = _Color(style.color[0], style.color[1], style.color[2])

        if len(self._selected_words) == 1:
            word = str(first[4])
            if new_text:
                cmd = ReplaceTextCommand(
                    document=doc,
                    page_number=page_num,
                    old_text=word,
                    new_text=new_text,
                )
            else:
                cmd = DeleteTextCommand(  # type: ignore[assignment]
                    document=doc,
                    page_number=page_num,
                    text=word,
                )
            self._execute_command(cmd)
        else:
            from freedf.commands.text_commands import InsertTextCommand

            for w in self._selected_words:
                word = str(w[4])
                cmd_del = DeleteTextCommand(
                    document=doc,
                    page_number=page_num,
                    text=word,
                )
                self._execute_command(cmd_del)

            if new_text:
                cmd_ins = InsertTextCommand(
                    document=doc,
                    page_number=page_num,
                    x=style.origin[0],
                    y=style.origin[1],
                    text=new_text,
                    font_size=style.size,
                    color=orig_color,
                )
                self._execute_command(cmd_ins)

        self._clear_overlays()
        self._selected_text = ""
        self._selected_words = []

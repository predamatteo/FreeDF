"""FreeText tool — click to place a text annotation."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QGraphicsSceneMouseEvent, QInputDialog

from freedf.core.annotations import Color, Rect

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.tools.tool_manager import ToolManager


class FreeTextTool:
    """Click on page to create a freetext annotation."""

    def __init__(
        self,
        get_document: Callable[[], Document | None],
        get_page_number: Callable[[], int],
        get_parent_widget: Callable[[], object],
        tool_manager: ToolManager,
        execute_command: Callable[[object], None],
    ) -> None:
        self._get_document = get_document
        self._get_page_number = get_page_number
        self._get_parent = get_parent_widget
        self._tool_manager = tool_manager
        self._execute_command = execute_command

    @property
    def name(self) -> str:
        return "freetext"

    def activate(self) -> None:
        pass

    def deactivate(self) -> None:
        pass

    def mouse_press(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        if event.button() != Qt.MouseButton.LeftButton:
            return False

        doc = self._get_document()
        if doc is None:
            return False

        parent = self._get_parent()
        text, ok = QInputDialog.getMultiLineText(
            parent,  # type: ignore[arg-type]
            "Add Note",
            "Text:",
            "",
        )
        if not ok or not text.strip():
            return True

        self._create_freetext(pdf_pos, text.strip())
        return True

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        return False

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        return False

    def _create_freetext(self, pdf_pos: QPointF, text: str) -> None:
        from freedf.commands.annotation_commands import AddFreeTextCommand

        doc = self._get_document()
        if doc is None:
            return

        font_size = self._tool_manager.current_font_size
        # Estimate rect size based on text length
        width = max(100, min(300, len(text) * font_size * 0.6))
        line_count = text.count("\n") + 1
        height = max(30, font_size * 1.5 * line_count + 10)

        rect = Rect(
            pdf_pos.x(),
            pdf_pos.y(),
            pdf_pos.x() + width,
            pdf_pos.y() + height,
        )

        cmd = AddFreeTextCommand(
            document=doc,
            page_number=self._get_page_number(),
            rect=rect,
            text=text,
            font_size=font_size,
            text_color=Color(0.0, 0.0, 0.0),
            fill_color=Color(1.0, 1.0, 0.9),  # light yellow background
        )
        self._execute_command(cmd)

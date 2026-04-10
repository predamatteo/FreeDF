"""Stamp tool — place predefined or custom stamps on pages."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QGraphicsSceneMouseEvent, QInputDialog

from freedf.core.annotations import Rect

if TYPE_CHECKING:
    from freedf.core.document import Document
    from freedf.ui.tools.tool_manager import ToolManager

PREDEFINED_STAMPS = [
    "Approved",
    "Rejected",
    "Draft",
    "Confidential",
    "Final",
    "Expired",
    "Not Approved",
]


class StampTool:
    """Click on page to place a stamp annotation."""

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
        return "stamp"

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
        items = [*PREDEFINED_STAMPS, "Custom..."]
        choice, ok = QInputDialog.getItem(
            parent,  # type: ignore[arg-type]
            "Place Stamp",
            "Stamp type:",
            items,
            0,
            False,
        )
        if not ok:
            return True

        if choice == "Custom...":
            choice, ok = QInputDialog.getText(
                parent,  # type: ignore[arg-type]
                "Custom Stamp",
                "Stamp text:",
            )
            if not ok or not choice.strip():
                return True
            choice = choice.strip()

        self._create_stamp(pdf_pos, choice)
        return True

    def mouse_move(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        return False

    def mouse_release(self, event: QGraphicsSceneMouseEvent, pdf_pos: QPointF) -> bool:
        return False

    def _create_stamp(self, pdf_pos: QPointF, text: str) -> None:
        from freedf.commands.annotation_commands import AddFreeTextCommand
        from freedf.core.annotations import Color

        doc = self._get_document()
        if doc is None:
            return

        # Create a bordered freetext that looks like a stamp
        width = max(120, len(text) * 12)
        rect = Rect(
            pdf_pos.x(),
            pdf_pos.y(),
            pdf_pos.x() + width,
            pdf_pos.y() + 30,
        )

        cmd = AddFreeTextCommand(
            document=doc,
            page_number=self._get_page_number(),
            rect=rect,
            text=text.upper(),
            font_size=14.0,
            text_color=Color(0.8, 0.0, 0.0),
            fill_color=Color(1.0, 0.95, 0.95),
        )
        self._execute_command(cmd)

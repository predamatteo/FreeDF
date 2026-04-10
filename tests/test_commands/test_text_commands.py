"""Tests for freedf.commands.text_commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from freedf.commands.base import CommandStack
from freedf.commands.text_commands import InsertTextCommand, ReplaceTextCommand

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestReplaceTextCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        cmd = ReplaceTextCommand(
            document=sample_document,
            page_number=0,
            old_text="Page 1",
            new_text="CHANGED",
        )
        cmd.execute()
        assert "CHANGED" in sample_document.get_page(0).get_text()

        cmd.undo()
        restored = sample_document.get_page(0).get_text()
        assert "Page 1" in restored

    def test_via_stack(self, sample_document: Document) -> None:
        stack = CommandStack()
        cmd = ReplaceTextCommand(
            document=sample_document,
            page_number=0,
            old_text="Page 1",
            new_text="NEW",
        )
        stack.execute(cmd)
        assert "NEW" in sample_document.get_page(0).get_text()
        stack.undo()
        assert "Page 1" in sample_document.get_page(0).get_text()


class TestInsertTextCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        cmd = InsertTextCommand(
            document=sample_document,
            page_number=0,
            x=72,
            y=800,
            text="TEST INSERT",
        )
        cmd.execute()
        assert "TEST INSERT" in sample_document.get_page(0).get_text()

        cmd.undo()
        assert "TEST INSERT" not in sample_document.get_page(0).get_text()

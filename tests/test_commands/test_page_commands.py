"""Tests for freedf.commands.page_commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

from freedf.commands.base import CommandStack
from freedf.commands.page_commands import (
    DeletePageCommand,
    DuplicatePageCommand,
    RotatePageCommand,
)

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestRotatePageCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        cmd = RotatePageCommand(sample_document, 0, 90)
        cmd.execute()
        assert sample_document.get_page(0).rotation == 90
        cmd.undo()
        assert sample_document.get_page(0).rotation == 0

    def test_via_stack(self, sample_document: Document) -> None:
        stack = CommandStack()
        cmd = RotatePageCommand(sample_document, 0, 180)
        stack.execute(cmd)
        assert sample_document.get_page(0).rotation == 180
        stack.undo()
        assert sample_document.get_page(0).rotation == 0
        stack.redo()
        assert sample_document.get_page(0).rotation == 180


class TestDeletePageCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        original_count = sample_document.page_count
        text_page1 = sample_document.get_page(1).get_text()

        cmd = DeletePageCommand(sample_document, 1)
        cmd.execute()
        assert sample_document.page_count == original_count - 1

        cmd.undo()
        assert sample_document.page_count == original_count
        restored_text = sample_document.get_page(1).get_text()
        assert "Page 2" in restored_text or text_page1[:20] in restored_text

    def test_via_stack(self, sample_document: Document) -> None:
        stack = CommandStack()
        original_count = sample_document.page_count
        cmd = DeletePageCommand(sample_document, 0)
        stack.execute(cmd)
        assert sample_document.page_count == original_count - 1
        stack.undo()
        assert sample_document.page_count == original_count


class TestDuplicatePageCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        original_count = sample_document.page_count
        cmd = DuplicatePageCommand(sample_document, 0)
        cmd.execute()
        assert sample_document.page_count == original_count + 1
        cmd.undo()
        assert sample_document.page_count == original_count

    def test_via_stack(self, sample_document: Document) -> None:
        stack = CommandStack()
        original_count = sample_document.page_count
        cmd = DuplicatePageCommand(sample_document, 1)
        stack.execute(cmd)
        assert sample_document.page_count == original_count + 1
        stack.undo()
        assert sample_document.page_count == original_count
        stack.redo()
        assert sample_document.page_count == original_count + 1


class TestCommandComposition:
    def test_rotate_then_delete_then_undo_both(self, sample_document: Document) -> None:
        stack = CommandStack()
        original_count = sample_document.page_count

        # Rotate page 0
        stack.execute(RotatePageCommand(sample_document, 0, 90))
        assert sample_document.get_page(0).rotation == 90

        # Delete page 1
        stack.execute(DeletePageCommand(sample_document, 1))
        assert sample_document.page_count == original_count - 1

        # Undo delete
        stack.undo()
        assert sample_document.page_count == original_count

        # Undo rotate
        stack.undo()
        assert sample_document.get_page(0).rotation == 0

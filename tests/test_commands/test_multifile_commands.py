"""Tests for freedf.commands.multifile_commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import fitz

from freedf.commands.base import CommandStack
from freedf.commands.multifile_commands import InsertPagesCommand

if TYPE_CHECKING:
    from freedf.core.document import Document


def _make_source_bytes(page_count: int = 2) -> bytes:
    """Create a small PDF in memory and return its bytes."""
    doc = fitz.open()
    for i in range(page_count):
        page = doc.new_page(width=595, height=842)
        page.insert_text(fitz.Point(72, 72), f"Inserted page {i + 1}")
    data = bytes(doc.tobytes())
    doc.close()
    return data


class TestInsertPagesCommand:
    def test_execute(self, sample_document: Document) -> None:
        original = sample_document.page_count
        src = _make_source_bytes(2)
        cmd = InsertPagesCommand(
            document=sample_document,
            source_pdf_bytes=src,
            source_page_numbers=[0, 1],
            insert_at=1,
        )
        cmd.execute()
        assert sample_document.page_count == original + 2

    def test_undo(self, sample_document: Document) -> None:
        original = sample_document.page_count
        src = _make_source_bytes(2)
        cmd = InsertPagesCommand(
            document=sample_document,
            source_pdf_bytes=src,
            source_page_numbers=[0, 1],
            insert_at=0,
        )
        cmd.execute()
        assert sample_document.page_count == original + 2
        cmd.undo()
        assert sample_document.page_count == original

    def test_via_stack(self, sample_document: Document) -> None:
        original = sample_document.page_count
        src = _make_source_bytes(1)
        stack = CommandStack()
        cmd = InsertPagesCommand(
            document=sample_document,
            source_pdf_bytes=src,
            source_page_numbers=[0],
            insert_at=sample_document.page_count,
        )
        stack.execute(cmd)
        assert sample_document.page_count == original + 1
        stack.undo()
        assert sample_document.page_count == original
        stack.redo()
        assert sample_document.page_count == original + 1

    def test_insert_at_end(self, sample_document: Document) -> None:
        original = sample_document.page_count
        src = _make_source_bytes(1)
        cmd = InsertPagesCommand(
            document=sample_document,
            source_pdf_bytes=src,
            source_page_numbers=[0],
            insert_at=original,
        )
        cmd.execute()
        assert sample_document.page_count == original + 1
        text = sample_document.get_page(original).get_text()
        assert "Inserted" in text

"""Tests for freedf.commands.annotation_commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import fitz

from freedf.commands.annotation_commands import (
    AddFreeTextCommand,
    AddHighlightCommand,
    DeleteAnnotationCommand,
)
from freedf.commands.base import CommandStack
from freedf.core.annotations import Color, Rect

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestAddHighlightCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        words = page.get_text_words()
        assert len(words) > 0

        # Create a quad from the first word
        w = words[0]
        quad = fitz.Quad(
            fitz.Point(w[0], w[1]),
            fitz.Point(w[2], w[1]),
            fitz.Point(w[0], w[3]),
            fitz.Point(w[2], w[3]),
        )

        cmd = AddHighlightCommand(
            document=sample_document,
            page_number=0,
            quads=[quad],
            color=Color.yellow(),
        )
        cmd.execute()

        annots = sample_document.get_page(0).get_annotations()
        assert len(annots) == 1
        assert annots[0].annot_type.value == 8  # HIGHLIGHT

        cmd.undo()
        annots = sample_document.get_page(0).get_annotations()
        assert len(annots) == 0

    def test_via_stack(self, sample_document: Document) -> None:
        words = sample_document.get_page(0).get_text_words()
        w = words[0]
        quad = fitz.Quad(
            fitz.Point(w[0], w[1]),
            fitz.Point(w[2], w[1]),
            fitz.Point(w[0], w[3]),
            fitz.Point(w[2], w[3]),
        )

        stack = CommandStack()
        cmd = AddHighlightCommand(
            document=sample_document,
            page_number=0,
            quads=[quad],
            color=Color.yellow(),
        )
        stack.execute(cmd)
        assert len(sample_document.get_page(0).get_annotations()) == 1

        stack.undo()
        assert len(sample_document.get_page(0).get_annotations()) == 0

        stack.redo()
        assert len(sample_document.get_page(0).get_annotations()) == 1


class TestAddFreeTextCommand:
    def test_execute_and_undo(self, sample_document: Document) -> None:
        rect = Rect(100, 100, 300, 150)
        cmd = AddFreeTextCommand(
            document=sample_document,
            page_number=0,
            rect=rect,
            text="Test note",
            font_size=12.0,
            text_color=Color(0.0, 0.0, 0.0),
        )
        cmd.execute()

        annots = sample_document.get_page(0).get_annotations()
        assert len(annots) == 1
        assert annots[0].annot_type.value == 2  # FREE_TEXT

        cmd.undo()
        assert len(sample_document.get_page(0).get_annotations()) == 0


class TestDeleteAnnotationCommand:
    def test_delete_highlight(self, sample_document: Document) -> None:
        # First add a highlight
        words = sample_document.get_page(0).get_text_words()
        w = words[0]
        quad = fitz.Quad(
            fitz.Point(w[0], w[1]),
            fitz.Point(w[2], w[1]),
            fitz.Point(w[0], w[3]),
            fitz.Point(w[2], w[3]),
        )
        add_cmd = AddHighlightCommand(
            document=sample_document,
            page_number=0,
            quads=[quad],
            color=Color.yellow(),
        )
        add_cmd.execute()

        annots = sample_document.get_page(0).get_annotations()
        assert len(annots) == 1
        annot_id = annots[0].annot_id

        # Now delete it
        del_cmd = DeleteAnnotationCommand(
            document=sample_document,
            page_number=0,
            annot_id=annot_id,
        )
        del_cmd.execute()
        assert len(sample_document.get_page(0).get_annotations()) == 0

        # Undo should restore it
        del_cmd.undo()
        annots = sample_document.get_page(0).get_annotations()
        assert len(annots) == 1

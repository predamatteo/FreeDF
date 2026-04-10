"""Tests for freedf.commands.form_commands."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from freedf.commands.base import CommandStack
from freedf.commands.form_commands import (
    FillFieldCommand,
    FlattenAnnotationsCommand,
)
from freedf.core.forms import get_field_value
from freedf.io.loader import open_pdf


@pytest.fixture(scope="session")
def form_pdf_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Generate a PDF with form fields."""
    path = tmp_path_factory.mktemp("fixtures") / "form_cmd.pdf"
    doc = fitz.open()
    page = doc.new_page()
    widget = fitz.Widget()
    widget.field_name = "city"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(100, 100, 300, 130)
    widget.field_value = "Rome"
    page.add_widget(widget)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture()
def form_doc(form_pdf_path: Path, tmp_path: Path) -> object:
    import shutil

    copy = tmp_path / "form_cmd_copy.pdf"
    shutil.copy(form_pdf_path, copy)
    doc = open_pdf(copy)
    yield doc
    doc.close()


class TestFillFieldCommand:
    def test_execute_and_undo(self, form_doc: object) -> None:
        cmd = FillFieldCommand(
            document=form_doc,
            field_name="city",
            new_value="Milan",  # type: ignore[arg-type]
        )
        cmd.execute()
        assert get_field_value(form_doc, "city") == "Milan"  # type: ignore[arg-type]
        cmd.undo()
        assert get_field_value(form_doc, "city") == "Rome"  # type: ignore[arg-type]

    def test_via_stack(self, form_doc: object) -> None:
        stack = CommandStack()
        cmd = FillFieldCommand(
            document=form_doc,
            field_name="city",
            new_value="Naples",  # type: ignore[arg-type]
        )
        stack.execute(cmd)
        assert get_field_value(form_doc, "city") == "Naples"  # type: ignore[arg-type]
        stack.undo()
        assert get_field_value(form_doc, "city") == "Rome"  # type: ignore[arg-type]


class TestFlattenAnnotationsCommand:
    def test_execute_and_undo(self, sample_document: object) -> None:
        from freedf.commands.annotation_commands import AddHighlightCommand
        from freedf.core.annotations import Color

        doc = sample_document
        # Add a highlight annotation first
        words = doc.get_page(0).get_text_words()  # type: ignore[union-attr]
        if words:
            w = words[0]
            quad = fitz.Quad(
                fitz.Point(w[0], w[1]),
                fitz.Point(w[2], w[1]),
                fitz.Point(w[0], w[3]),
                fitz.Point(w[2], w[3]),
            )
            add = AddHighlightCommand(
                document=doc,
                page_number=0,
                quads=[quad],
                color=Color.yellow(),  # type: ignore[arg-type]
            )
            add.execute()
            assert len(doc.get_page(0).get_annotations()) == 1  # type: ignore[union-attr]

        cmd = FlattenAnnotationsCommand(document=doc, page_number=0)  # type: ignore[arg-type]
        cmd.execute()
        assert len(doc.get_page(0).get_annotations()) == 0  # type: ignore[union-attr]

        cmd.undo()
        # After undo, annotations should be restored
        annots = doc.get_page(0).get_annotations()  # type: ignore[union-attr]
        assert len(annots) >= 1

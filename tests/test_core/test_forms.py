"""Tests for freedf.core.forms."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from freedf.core.forms import detect_form_fields, fill_field, get_field_value
from freedf.io.loader import open_pdf


@pytest.fixture(scope="session")
def form_pdf_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Generate a PDF with form fields."""
    path = tmp_path_factory.mktemp("fixtures") / "form.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Add a text widget
    widget = fitz.Widget()
    widget.field_name = "name"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(100, 100, 300, 130)
    widget.field_value = "John"
    page.add_widget(widget)

    # Add a checkbox widget
    widget2 = fitz.Widget()
    widget2.field_name = "agree"
    widget2.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
    widget2.rect = fitz.Rect(100, 150, 130, 180)
    widget2.field_value = "Off"
    page.add_widget(widget2)

    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture()
def form_document(form_pdf_path: Path, tmp_path: Path) -> object:
    """Open a copy of the form PDF."""
    import shutil

    copy = tmp_path / "form_copy.pdf"
    shutil.copy(form_pdf_path, copy)
    doc = open_pdf(copy)
    yield doc
    doc.close()


class TestDetectFormFields:
    def test_detect(self, form_document: object) -> None:
        fields = detect_form_fields(form_document)  # type: ignore[arg-type]
        assert len(fields) >= 2
        names = [f.field_name for f in fields]
        assert "name" in names
        assert "agree" in names

    def test_field_types(self, form_document: object) -> None:
        fields = detect_form_fields(form_document)  # type: ignore[arg-type]
        name_field = next(f for f in fields if f.field_name == "name")
        assert name_field.field_type == "Text"


class TestFillField:
    def test_fill_text(self, form_document: object) -> None:
        old = fill_field(form_document, "name", "Alice")  # type: ignore[arg-type]
        assert old == "John"
        assert get_field_value(form_document, "name") == "Alice"  # type: ignore[arg-type]

    def test_fill_nonexistent_raises(self, form_document: object) -> None:
        with pytest.raises(ValueError, match="not found"):
            fill_field(form_document, "nonexistent", "x")  # type: ignore[arg-type]

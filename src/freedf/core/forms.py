"""AcroForm field detection and filling (no Qt dependency)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from freedf.core.annotations import Rect

if TYPE_CHECKING:
    from freedf.core.document import Document


@dataclass(frozen=True)
class FormField:
    """Immutable snapshot of a PDF form field."""

    field_name: str
    field_type: str  # "Text", "CheckBox", "ComboBox", "ListBox", "RadioButton"
    page_number: int
    rect: Rect
    current_value: str
    options: list[str] = field(default_factory=list)
    is_read_only: bool = False


def detect_form_fields(document: Document) -> list[FormField]:
    """Scan all pages for AcroForm widget annotations."""
    fields: list[FormField] = []
    fitz_doc = document.fitz_document

    for page_num in range(document.page_count):
        page = fitz_doc[page_num]
        widget = page.first_widget
        while widget:
            ft = _widget_type_name(widget.field_type)
            r = widget.rect
            choices: list[str] = []
            if hasattr(widget, "choice_values") and widget.choice_values:
                choices = list(widget.choice_values)

            fields.append(
                FormField(
                    field_name=widget.field_name or "",
                    field_type=ft,
                    page_number=page_num,
                    rect=Rect(r.x0, r.y0, r.x1, r.y1),
                    current_value=widget.field_value or "",
                    options=choices,
                    is_read_only=bool(widget.field_flags & 1),  # ReadOnly flag
                )
            )
            widget = widget.next
    return fields


def fill_field(document: Document, field_name: str, value: str) -> str:
    """Set a form field's value. Returns the previous value for undo."""
    fitz_doc = document.fitz_document
    for page_num in range(document.page_count):
        page = fitz_doc[page_num]
        widget = page.first_widget
        while widget:
            if widget.field_name == field_name:
                old_value = widget.field_value or ""
                widget.field_value = value
                widget.update()
                document._notify_modified(page_num)
                return old_value
            widget = widget.next
    msg = f"Form field '{field_name}' not found"
    raise ValueError(msg)


def get_field_value(document: Document, field_name: str) -> str:
    """Read the current value of a named form field."""
    fitz_doc = document.fitz_document
    for page_num in range(document.page_count):
        page = fitz_doc[page_num]
        widget = page.first_widget
        while widget:
            if widget.field_name == field_name:
                return widget.field_value or ""
            widget = widget.next
    msg = f"Form field '{field_name}' not found"
    raise ValueError(msg)


def _widget_type_name(field_type: int) -> str:
    """Convert fitz widget field_type int to a readable name."""
    import fitz

    mapping = {
        fitz.PDF_WIDGET_TYPE_TEXT: "Text",
        fitz.PDF_WIDGET_TYPE_CHECKBOX: "CheckBox",
        fitz.PDF_WIDGET_TYPE_COMBOBOX: "ComboBox",
        fitz.PDF_WIDGET_TYPE_LISTBOX: "ListBox",
        fitz.PDF_WIDGET_TYPE_RADIOBUTTON: "RadioButton",
    }
    return mapping.get(field_type, "Unknown")

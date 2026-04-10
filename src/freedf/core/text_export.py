"""Text extraction and export (no Qt dependency)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from freedf.core.document import Document


def extract_text_from_page(document: Document, page_number: int) -> str:
    """Extract all text from a single page."""
    page = document.get_page(page_number)
    return page.get_text()


def extract_text_from_document(
    document: Document,
    page_numbers: Sequence[int] | None = None,
) -> str:
    """Extract text from selected pages (or all pages).

    Pages are separated by a header line.
    """
    if page_numbers is None:
        page_numbers = list(range(document.page_count))

    parts: list[str] = []
    for pn in page_numbers:
        text = extract_text_from_page(document, pn)
        parts.append(f"--- Page {pn + 1} ---\n{text}")
    return "\n\n".join(parts)


def export_text_to_file(
    document: Document,
    output_path: str | Path,
    page_numbers: Sequence[int] | None = None,
) -> None:
    """Export extracted text to a .txt file."""
    text = extract_text_from_document(document, page_numbers)
    Path(output_path).write_text(text, encoding="utf-8")

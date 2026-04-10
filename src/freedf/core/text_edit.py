"""Text editing operations on PDF pages (no Qt dependency).

Uses PyMuPDF's redaction API for text replacement and direct
insertion for new text/watermarks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import fitz

from freedf.core.annotations import Color, Rect

if TYPE_CHECKING:
    from freedf.core.document import Document


@dataclass(frozen=True)
class TextMatch:
    """A text match found on a page."""

    page_number: int
    rect: Rect
    text: str


def find_text(
    document: Document,
    query: str,
    page_numbers: list[int] | None = None,
) -> list[TextMatch]:
    """Find all occurrences of text across pages."""
    if page_numbers is None:
        page_numbers = list(range(document.page_count))

    matches: list[TextMatch] = []
    for pn in page_numbers:
        page = document.fitz_document[pn]
        rects = page.search_for(query)
        for r in rects:
            matches.append(
                TextMatch(
                    page_number=pn,
                    rect=Rect(r.x0, r.y0, r.x1, r.y1),
                    text=query,
                )
            )
    return matches


def replace_text_on_page(
    document: Document,
    page_number: int,
    old_text: str,
    new_text: str,
    font_size: float = 11.0,
    color: Color | None = None,
) -> int:
    """Replace all occurrences of old_text with new_text on a page.

    Uses redaction (removes old text area) then inserts new text.
    Returns the number of replacements made.
    """
    page = document.fitz_document[page_number]
    rects = page.search_for(old_text)
    if not rects:
        return 0

    tc = color.to_tuple() if color else (0, 0, 0)

    for rect in rects:
        page.add_redact_annot(rect, text=new_text, fontsize=font_size, text_color=tc)

    page.apply_redactions()
    document._notify_modified(page_number)
    return len(rects)


def insert_text_on_page(
    document: Document,
    page_number: int,
    x: float,
    y: float,
    text: str,
    font_size: float = 12.0,
    color: Color | None = None,
    font_name: str = "helv",
) -> None:
    """Insert text directly into page content at a specific position."""
    page = document.fitz_document[page_number]
    tc = color.to_tuple() if color else (0, 0, 0)
    page.insert_text(
        fitz.Point(x, y),
        text,
        fontsize=font_size,
        fontname=font_name,
        color=tc,
    )
    document._notify_modified(page_number)


def add_watermark(
    document: Document,
    text: str,
    page_numbers: list[int] | None = None,
    font_size: float = 60.0,
    color: Color | None = None,
    opacity: float = 0.3,
    rotation: float = -45.0,
) -> int:
    """Add a diagonal text watermark to pages.

    Returns the number of pages watermarked.
    """
    if page_numbers is None:
        page_numbers = list(range(document.page_count))

    tc = color.to_tuple() if color else (0.5, 0.5, 0.5)

    for pn in page_numbers:
        page = document.fitz_document[pn]
        rect = page.rect
        # Center the watermark
        cx = rect.width / 2
        cy = rect.height / 2

        # Use a text writer for rotated text with opacity
        tw = fitz.TextWriter(page.rect)
        tw.append(
            fitz.Point(cx - len(text) * font_size * 0.25, cy),
            text,
            fontsize=font_size,
            font=fitz.Font("helv"),
        )
        morph = (fitz.Point(cx, cy), fitz.Matrix(rotation))
        tw.write_text(page, opacity=opacity, color=tc, morph=morph)
        document._notify_modified(pn)

    return len(page_numbers)

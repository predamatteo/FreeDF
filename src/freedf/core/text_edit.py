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


def delete_text_on_page(
    document: Document,
    page_number: int,
    text: str,
) -> int:
    """Delete all occurrences of text on a page.

    Uses redaction to permanently remove the text from the content stream.
    Returns the number of deletions made.
    """
    page = document.fitz_document[page_number]
    rects = page.search_for(text)
    if not rects:
        return 0

    for rect in rects:
        page.add_redact_annot(rect)

    page.apply_redactions()
    document._notify_modified(page_number)
    return len(rects)


def detect_text_style_at(
    document: Document,
    page_number: int,
    x: float,
    y: float,
    target_text: str | None = None,
) -> TextStyle:
    """Detect full text style near a point.

    Searches the page's text dict for the span closest to (x, y).
    If target_text is given, prefers spans containing that text.
    """
    page = document.fitz_document[page_number]
    search_rect = fitz.Rect(x - 5, y - 15, x + 200, y + 5)
    return _detect_text_style(page, search_rect, target_text)


@dataclass(frozen=True)
class TextStyle:
    """Detected style of a text span."""

    size: float
    color: tuple[float, float, float]
    font_name: str  # original PDF font name (e.g. "BCDFEE+Calibri-Italic")
    base_font: str  # usable font name for insert_text (e.g. "helv")
    is_italic: bool
    is_bold: bool
    origin: tuple[float, float]  # baseline origin point (x, y)


def _map_to_base_font(pdf_font_name: str) -> tuple[str, bool, bool]:
    """Map a PDF font name to a base14 font + italic/bold flags.

    PDF fonts are like "BCDFEE+Calibri-BoldItalic" or "TimesNewRoman,Italic".
    We detect bold/italic from the name and pick the right base font.
    """
    name_lower = pdf_font_name.lower()
    is_bold = "bold" in name_lower or "black" in name_lower or "heavy" in name_lower
    is_italic = "italic" in name_lower or "oblique" in name_lower

    # Detect font family
    if "times" in name_lower or "serif" in name_lower:
        if is_bold and is_italic:
            return "tibi", True, True
        if is_bold:
            return "tibo", False, True
        if is_italic:
            return "tiit", True, False
        return "tiro", False, False
    if "courier" in name_lower or "mono" in name_lower:
        if is_bold and is_italic:
            return "cobi", True, True
        if is_bold:
            return "cobo", False, True
        if is_italic:
            return "coit", True, False
        return "cour", False, False
    # Default: Helvetica family
    if is_bold and is_italic:
        return "hebi", True, True
    if is_bold:
        return "hebo", False, True
    if is_italic:
        return "heit", True, False
    return "helv", False, False


def _detect_text_style(
    page: fitz.Page,
    search_rect: fitz.Rect,
    target_text: str | None = None,
) -> TextStyle:
    """Detect full text style at search_rect.

    Looks through the page's text dict for spans overlapping the rect.
    If target_text is given, prefers spans containing that text.
    """
    default = TextStyle(
        size=11.0,
        color=(0.0, 0.0, 0.0),
        font_name="helv",
        base_font="helv",
        is_italic=False,
        is_bold=False,
        origin=(search_rect.x0, search_rect.y1),
    )
    try:
        data = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    except Exception:
        return default

    best: TextStyle | None = None
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                span_rect = fitz.Rect(span["bbox"])
                if not span_rect.intersects(search_rect):
                    continue
                size = span.get("size", 11.0)
                color_int = span.get("color", 0)
                r = ((color_int >> 16) & 0xFF) / 255.0
                g = ((color_int >> 8) & 0xFF) / 255.0
                b = (color_int & 0xFF) / 255.0
                font_name = span.get("font", "helv")
                base_font, is_italic, is_bold = _map_to_base_font(font_name)
                # origin is the baseline start point
                origin = tuple(span.get("origin", (span_rect.x0, span_rect.y1)))
                result = TextStyle(
                    size=float(size),
                    color=(r, g, b),
                    font_name=font_name,
                    base_font=base_font,
                    is_italic=is_italic,
                    is_bold=is_bold,
                    origin=(float(origin[0]), float(origin[1])),
                )
                if target_text and target_text in span.get("text", ""):
                    return result
                if best is None:
                    best = result
    return best or default


def replace_text_on_page(
    document: Document,
    page_number: int,
    old_text: str,
    new_text: str,
    font_size: float | None = None,
    color: Color | None = None,
) -> int:
    """Replace all occurrences of old_text with new_text on a page.

    Uses redaction (removes old text area) then inserts new text.
    If font_size is None, auto-detects the original text size.
    If color is None, auto-detects the original text color.
    Returns the number of replacements made.
    """
    page = document.fitz_document[page_number]
    rects = page.search_for(old_text)
    if not rects:
        return 0

    # Collect full style info BEFORE redacting (redaction destroys the text)
    detected: list[tuple[fitz.Rect, TextStyle]] = []
    for rect in rects:
        style = _detect_text_style(page, rect, old_text)
        detected.append((rect, style))

    # Step 1: redact all occurrences (removes old text, NO replacement)
    for rect, _style in detected:
        page.add_redact_annot(rect)
    page.apply_redactions()

    # Step 2: insert new text at each original position with correct style
    if new_text:
        for rect, style in detected:
            use_size = font_size if font_size is not None else style.size
            use_color = color.to_tuple() if color else style.color
            # X from search rect (exact match position),
            # Y baseline from span origin (correct vertical alignment)
            page.insert_text(
                fitz.Point(rect.x0, style.origin[1]),
                new_text,
                fontsize=use_size,
                fontname=style.base_font,
                color=use_color,
            )

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

"""OCR engine wrapper using Tesseract (no Qt dependency).

pytesseract is an optional dependency. All functions gracefully handle
its absence via is_tesseract_available().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from freedf.core.annotations import Rect

if TYPE_CHECKING:
    from freedf.core.document import Document


@dataclass(frozen=True)
class WordBox:
    """A recognized word with its bounding box."""

    text: str
    rect: Rect
    confidence: float


@dataclass(frozen=True)
class OCRResult:
    """Result of OCR on a single page."""

    page_number: int
    text: str
    word_boxes: list[WordBox] = field(default_factory=list)
    language: str = "eng"
    confidence: float = 0.0


def is_tesseract_available() -> bool:
    """Check if Tesseract is installed and callable."""
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
    except Exception:
        return False
    return True


def get_available_languages() -> list[str]:
    """Return list of installed Tesseract language packs."""
    try:
        import pytesseract

        langs = pytesseract.get_languages(config="")
        return [lang for lang in langs if lang != "osd"]
    except Exception:
        return []


def ocr_page(
    document: Document,
    page_number: int,
    language: str = "eng",
    dpi: int = 300,
) -> OCRResult:
    """Run OCR on a page. Returns structured result with word boxes."""
    import pytesseract

    from freedf.rendering.renderer import PageRenderer

    # Render page at specified DPI
    image = PageRenderer.render_to_image(document, page_number, dpi=dpi)

    # Run Tesseract with word-level bounding boxes
    data = pytesseract.image_to_data(
        image, lang=language, output_type=pytesseract.Output.DICT
    )

    # Also get plain text
    text = pytesseract.image_to_string(image, lang=language)

    # Parse word boxes, converting pixel coords to PDF points
    scale = 72.0 / dpi
    word_boxes: list[WordBox] = []
    total_conf = 0.0
    word_count = 0

    n_boxes = len(data["text"])
    for i in range(n_boxes):
        word = data["text"][i].strip()
        conf = float(data["conf"][i])
        if not word or conf < 0:
            continue
        x = float(data["left"][i]) * scale
        y = float(data["top"][i]) * scale
        w = float(data["width"][i]) * scale
        h = float(data["height"][i]) * scale
        word_boxes.append(
            WordBox(text=word, rect=Rect(x, y, x + w, y + h), confidence=conf)
        )
        total_conf += conf
        word_count += 1

    avg_conf = total_conf / word_count if word_count > 0 else 0.0

    return OCRResult(
        page_number=page_number,
        text=text,
        word_boxes=word_boxes,
        language=language,
        confidence=avg_conf,
    )


def apply_ocr_text_layer(
    document: Document,
    page_number: int,
    ocr_result: OCRResult,
) -> None:
    """Insert an invisible text layer matching OCR results.

    Uses render_mode=3 (invisible) so the text is searchable/selectable
    but does not visually alter the page.
    """
    import fitz

    fitz_page = document.fitz_document[page_number]

    for wb in ocr_result.word_boxes:
        r = wb.rect
        # Calculate font size to approximately fill the bounding box height
        font_size = max(1.0, r.height * 0.8)
        try:
            fitz_page.insert_text(
                fitz.Point(r.x0, r.y1),  # baseline point
                wb.text,
                fontsize=font_size,
                fontname="helv",
                render_mode=3,  # invisible
            )
        except Exception:
            continue

    document._notify_modified(page_number)


def page_has_text(document: Document, page_number: int) -> bool:
    """Check if a page already has extractable text."""
    page = document.get_page(page_number)
    return bool(page.get_text().strip())

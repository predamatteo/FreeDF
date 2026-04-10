"""Image insertion on PDF pages (no Qt dependency)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import fitz

from freedf.core.annotations import Rect

if TYPE_CHECKING:
    from freedf.core.document import Document


def insert_image_on_page(
    document: Document,
    page_number: int,
    image_path: str | Path,
    rect: Rect,
    keep_aspect: bool = True,
) -> None:
    """Insert a raster image (PNG/JPEG) into a page."""
    image_path = Path(image_path)
    if not image_path.exists():
        msg = f"Image file not found: {image_path}"
        raise FileNotFoundError(msg)

    page = document.fitz_document[page_number]
    fitz_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
    page.insert_image(fitz_rect, filename=str(image_path), keep_proportion=keep_aspect)
    document._notify_modified(page_number)

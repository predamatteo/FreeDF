"""Stateless page renderer (no Qt dependency)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import fitz
from PIL import Image

if TYPE_CHECKING:
    from freedf.core.document import Document


class PageRenderer:
    """Renders PDF pages to images. Stateless — caching is in RenderCache."""

    @staticmethod
    def render_to_pixmap(
        document: Document,
        page_number: int,
        zoom: float = 1.0,
        dpi: int | None = None,
        alpha: bool = False,
    ) -> fitz.Pixmap:
        """Render a page to a fitz.Pixmap."""
        page = document.get_page(page_number)
        return page.get_pixmap(zoom=zoom, dpi=dpi, alpha=alpha)

    @staticmethod
    def render_to_image(
        document: Document,
        page_number: int,
        zoom: float = 1.0,
        dpi: int | None = None,
    ) -> Image.Image:
        """Render a page to a PIL Image (RGB)."""
        pixmap = PageRenderer.render_to_pixmap(
            document, page_number, zoom=zoom, dpi=dpi, alpha=False
        )
        return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

    @staticmethod
    def render_to_png_bytes(
        document: Document,
        page_number: int,
        zoom: float = 1.0,
        dpi: int | None = None,
    ) -> bytes:
        """Render a page to PNG bytes."""
        pixmap = PageRenderer.render_to_pixmap(
            document, page_number, zoom=zoom, dpi=dpi, alpha=False
        )
        return bytes(pixmap.tobytes(output="png"))

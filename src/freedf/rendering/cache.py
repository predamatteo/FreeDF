"""LRU rendering cache (no Qt dependency)."""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

from PIL import Image

from freedf.rendering.renderer import PageRenderer

if TYPE_CHECKING:
    from freedf.core.document import Document

CacheKey = tuple[int, float]


class RenderCache:
    """LRU cache for rendered page images.

    Keyed by (page_number, zoom_level). Automatically invalidates
    when the document is modified via modification callbacks.
    """

    def __init__(self, document: Document, max_size: int = 50) -> None:
        self._document = document
        self._max_size = max_size
        self._cache: OrderedDict[CacheKey, Image.Image] = OrderedDict()
        self._document.add_modification_callback(self._on_document_modified)

    def get_page_image(
        self,
        page_number: int,
        zoom: float = 1.0,
    ) -> Image.Image:
        """Get a rendered page image, using cache if available."""
        key = self._make_key(page_number, zoom)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]

        image = PageRenderer.render_to_image(self._document, page_number, zoom=zoom)
        self._put(key, image)
        return image

    def get_thumbnail(
        self,
        page_number: int,
        max_size: int = 160,
    ) -> Image.Image:
        """Render a small thumbnail for the sidebar."""
        page = self._document.get_page(page_number)
        scale = min(max_size / page.width, max_size / page.height)
        return PageRenderer.render_to_image(self._document, page_number, zoom=scale)

    def invalidate_page(self, page_number: int) -> None:
        """Remove all cached entries for a specific page."""
        keys_to_remove = [k for k in self._cache if k[0] == page_number]
        for key in keys_to_remove:
            del self._cache[key]

    def invalidate_all(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()

    def _on_document_modified(
        self, document: Document, page_number: int | None
    ) -> None:
        if page_number is None:
            self.invalidate_all()
        else:
            self.invalidate_page(page_number)

    def _make_key(self, page_number: int, zoom: float) -> CacheKey:
        return (page_number, round(zoom, 2))

    def _put(self, key: CacheKey, image: Image.Image) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = image
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def dispose(self) -> None:
        """Unregister from document callbacks and clear cache."""
        self._document.remove_modification_callback(self._on_document_modified)
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

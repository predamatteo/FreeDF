"""Tests for freedf.rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PIL import Image

from freedf.rendering.cache import RenderCache
from freedf.rendering.renderer import PageRenderer

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestPageRenderer:
    def test_render_to_image(self, sample_document: Document) -> None:
        img = PageRenderer.render_to_image(sample_document, 0)
        assert isinstance(img, Image.Image)
        assert img.width > 0
        assert img.height > 0

    def test_render_zoom_scales(self, sample_document: Document) -> None:
        img1 = PageRenderer.render_to_image(sample_document, 0, zoom=1.0)
        img2 = PageRenderer.render_to_image(sample_document, 0, zoom=2.0)
        assert img2.width == pytest.approx(img1.width * 2, abs=2)

    def test_render_to_png_bytes(self, sample_document: Document) -> None:
        data = PageRenderer.render_to_png_bytes(sample_document, 0)
        assert isinstance(data, bytes)
        assert data[:4] == b"\x89PNG"


class TestRenderCache:
    def test_cache_hit(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        img1 = cache.get_page_image(0, zoom=1.0)
        img2 = cache.get_page_image(0, zoom=1.0)
        assert img1 is img2
        assert cache.size == 1
        cache.dispose()

    def test_cache_miss_different_zoom(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        img1 = cache.get_page_image(0, zoom=1.0)
        img2 = cache.get_page_image(0, zoom=2.0)
        assert img1 is not img2
        assert cache.size == 2
        cache.dispose()

    def test_invalidate_page(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        cache.get_page_image(0, zoom=1.0)
        cache.get_page_image(0, zoom=2.0)
        assert cache.size == 2
        cache.invalidate_page(0)
        assert cache.size == 0
        cache.dispose()

    def test_invalidate_all(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        cache.get_page_image(0, zoom=1.0)
        cache.get_page_image(1, zoom=1.0)
        cache.invalidate_all()
        assert cache.size == 0
        cache.dispose()

    def test_auto_invalidate_on_rotate(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        cache.get_page_image(0, zoom=1.0)
        assert cache.size == 1
        sample_document.rotate_page(0, 90)
        assert cache.size == 0
        cache.dispose()

    def test_auto_invalidate_on_delete(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        cache.get_page_image(0, zoom=1.0)
        cache.get_page_image(1, zoom=1.0)
        assert cache.size == 2
        sample_document.delete_page(1)
        assert cache.size == 0  # structural change clears all
        cache.dispose()

    def test_lru_eviction(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=2)
        cache.get_page_image(0, zoom=1.0)
        cache.get_page_image(0, zoom=1.5)
        cache.get_page_image(0, zoom=2.0)  # evicts zoom=1.0
        assert cache.size == 2
        cache.dispose()

    def test_thumbnail(self, sample_document: Document) -> None:
        cache = RenderCache(sample_document, max_size=10)
        thumb = cache.get_thumbnail(0, max_size=100)
        assert isinstance(thumb, Image.Image)
        assert max(thumb.width, thumb.height) <= 110  # some margin
        cache.dispose()

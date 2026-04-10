"""Tests for freedf.core.page."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from freedf.core.annotations import Rect
from freedf.core.exceptions import InvalidRotationError

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestPage:
    def test_page_number(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        assert page.page_number == 0

    def test_rotation_default(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        assert page.rotation == 0

    def test_set_rotation_valid(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        page.set_rotation(90)
        assert page.rotation == 90

    def test_set_rotation_invalid(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        with pytest.raises(InvalidRotationError):
            page.set_rotation(45)

    def test_rect(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        rect = page.rect
        assert isinstance(rect, Rect)
        assert rect.width > 0
        assert rect.height > 0

    def test_width_height(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        assert page.width == pytest.approx(595, abs=1)
        assert page.height == pytest.approx(842, abs=1)

    def test_get_text(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        text = page.get_text()
        assert "Page 1" in text

    def test_get_pixmap(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        pixmap = page.get_pixmap(zoom=1.0)
        assert pixmap.width > 0
        assert pixmap.height > 0

    def test_get_pixmap_zoom(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        pix1 = page.get_pixmap(zoom=1.0)
        pix2 = page.get_pixmap(zoom=2.0)
        assert pix2.width == pytest.approx(pix1.width * 2, abs=2)

    def test_get_annotations_empty(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        annotations = page.get_annotations()
        assert annotations == []

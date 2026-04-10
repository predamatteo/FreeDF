"""Tests for freedf.core.ocr.

These tests require Tesseract to be installed and are marked with
@pytest.mark.ocr. Skip with: pytest -m "not ocr"
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from freedf.core.ocr import is_tesseract_available, page_has_text

if TYPE_CHECKING:
    from freedf.core.document import Document

pytestmark = pytest.mark.ocr


class TestOCRAvailability:
    def test_is_tesseract_available(self) -> None:
        # This test just verifies the function doesn't crash.
        # The result depends on whether Tesseract is installed.
        result = is_tesseract_available()
        assert isinstance(result, bool)


class TestPageHasText:
    def test_digital_page_has_text(self, sample_document: Document) -> None:
        assert page_has_text(sample_document, 0) is True


@pytest.mark.skipif(not is_tesseract_available(), reason="Tesseract not installed")
class TestOCRExecution:
    def test_ocr_page(self, sample_document: Document) -> None:
        from freedf.core.ocr import ocr_page

        result = ocr_page(sample_document, 0, language="eng", dpi=150)
        assert result.page_number == 0
        assert len(result.text) > 0
        assert len(result.word_boxes) > 0

    def test_ocr_result_confidence(self, sample_document: Document) -> None:
        from freedf.core.ocr import ocr_page

        result = ocr_page(sample_document, 0, language="eng", dpi=150)
        assert result.confidence > 0

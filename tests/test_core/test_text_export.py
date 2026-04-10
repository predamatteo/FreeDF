"""Tests for freedf.core.text_export."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from freedf.core.text_export import (
    export_text_to_file,
    extract_text_from_document,
    extract_text_from_page,
)

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestExtractText:
    def test_from_page(self, sample_document: Document) -> None:
        text = extract_text_from_page(sample_document, 0)
        assert "Page 1" in text

    def test_from_document(self, sample_document: Document) -> None:
        text = extract_text_from_document(sample_document)
        assert "Page 1" in text
        assert "Page 2" in text
        assert "Page 3" in text
        assert "--- Page 1 ---" in text

    def test_from_document_selected_pages(self, sample_document: Document) -> None:
        text = extract_text_from_document(sample_document, [0, 2])
        assert "Page 1" in text
        assert "Page 3" in text
        # Page 2 should not be in output
        assert "--- Page 2 ---" not in text

    def test_export_to_file(self, sample_document: Document, tmp_path: Path) -> None:
        output = tmp_path / "output.txt"
        export_text_to_file(sample_document, output)
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "Page 1" in content

"""Tests for freedf.core.text_edit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from freedf.core.text_edit import find_text, insert_text_on_page, replace_text_on_page

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestFindText:
    def test_find_existing(self, sample_document: Document) -> None:
        matches = find_text(sample_document, "Page 1")
        assert len(matches) >= 1
        assert matches[0].page_number == 0

    def test_find_nonexistent(self, sample_document: Document) -> None:
        matches = find_text(sample_document, "ZZZZNOTFOUND")
        assert len(matches) == 0

    def test_find_on_specific_pages(self, sample_document: Document) -> None:
        matches = find_text(sample_document, "Page", [0])
        assert all(m.page_number == 0 for m in matches)


class TestReplaceText:
    def test_replace(self, sample_document: Document) -> None:
        count = replace_text_on_page(sample_document, 0, "Page 1", "REPLACED")
        assert count >= 1
        # After replacement, original text should not be found
        text = sample_document.get_page(0).get_text()
        assert "REPLACED" in text


class TestInsertText:
    def test_insert(self, sample_document: Document) -> None:
        insert_text_on_page(sample_document, 0, 72, 800, "INSERTED TEXT")
        text = sample_document.get_page(0).get_text()
        assert "INSERTED TEXT" in text

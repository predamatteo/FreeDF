"""Tests for freedf.core.document."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from freedf.core.exceptions import PageIndexError, SinglePageDeleteError

if TYPE_CHECKING:
    from freedf.core.document import Document


class TestDocument:
    def test_page_count(self, sample_document: Document) -> None:
        assert sample_document.page_count == 3

    def test_get_page_valid(self, sample_document: Document) -> None:
        page = sample_document.get_page(0)
        assert page.page_number == 0

    def test_get_page_invalid(self, sample_document: Document) -> None:
        with pytest.raises(PageIndexError):
            sample_document.get_page(99)

    def test_get_page_negative(self, sample_document: Document) -> None:
        with pytest.raises(PageIndexError):
            sample_document.get_page(-1)

    def test_rotate_page(self, sample_document: Document) -> None:
        sample_document.rotate_page(0, 90)
        page = sample_document.get_page(0)
        assert page.rotation == 90

    def test_delete_page(self, sample_document: Document) -> None:
        original_count = sample_document.page_count
        sample_document.delete_page(1)
        assert sample_document.page_count == original_count - 1

    def test_delete_single_page_raises(self, single_page_document: Document) -> None:
        with pytest.raises(SinglePageDeleteError):
            single_page_document.delete_page(0)

    def test_duplicate_page(self, sample_document: Document) -> None:
        original_count = sample_document.page_count
        new_idx = sample_document.duplicate_page(0)
        assert sample_document.page_count == original_count + 1
        assert new_idx == 1

    def test_backup_page(self, sample_document: Document) -> None:
        data = sample_document.backup_page(0)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_modification_callback(self, sample_document: Document) -> None:
        notifications: list[int | None] = []
        sample_document.add_modification_callback(
            lambda doc, pn: notifications.append(pn)
        )
        sample_document.rotate_page(0, 90)
        assert notifications == [0]

    def test_structural_callback_on_delete(self, sample_document: Document) -> None:
        notifications: list[int | None] = []
        sample_document.add_modification_callback(
            lambda doc, pn: notifications.append(pn)
        )
        sample_document.delete_page(0)
        assert notifications == [None]

    def test_is_dirty_after_modification(self, sample_document: Document) -> None:
        sample_document.rotate_page(0, 90)
        assert sample_document.is_dirty

    def test_context_manager(self, sample_pdf_path: object, tmp_path: object) -> None:
        import shutil
        from pathlib import Path

        src = Path(str(sample_pdf_path))
        dst = Path(str(tmp_path)) / "ctx.pdf"
        shutil.copy(src, dst)

        from freedf.io.loader import open_pdf

        with open_pdf(dst) as doc:
            assert doc.page_count == 3

    def test_metadata(self, sample_document: Document) -> None:
        meta = sample_document.metadata
        assert isinstance(meta, dict)

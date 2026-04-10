"""Tests for freedf.core.multifile."""

from __future__ import annotations

from pathlib import Path

import pytest

from freedf.core.exceptions import InvalidPageRangeError
from freedf.core.multifile import (
    extract_pages,
    merge_pdfs,
    split_pdf_by_ranges,
    split_pdf_single_pages,
)


class TestMergePdfs:
    def test_merge_two(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        output = tmp_path / "merged.pdf"
        merge_pdfs([sample_pdf_path, sample_pdf_path], output)
        assert output.exists()
        import fitz

        doc = fitz.open(str(output))
        assert doc.page_count == 6  # 3 + 3
        doc.close()

    def test_merge_single(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        output = tmp_path / "single.pdf"
        merge_pdfs([sample_pdf_path], output)
        assert output.exists()

    def test_merge_empty_raises(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidPageRangeError):
            merge_pdfs([], tmp_path / "out.pdf")


class TestSplitPdf:
    def test_split_by_ranges(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        results = split_pdf_by_ranges(sample_pdf_path, [(0, 1), (2, 2)], tmp_path)
        assert len(results) == 2
        import fitz

        doc1 = fitz.open(str(results[0]))
        assert doc1.page_count == 2
        doc1.close()
        doc2 = fitz.open(str(results[1]))
        assert doc2.page_count == 1
        doc2.close()

    def test_split_single_pages(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        results = split_pdf_single_pages(sample_pdf_path, tmp_path)
        assert len(results) == 3

    def test_invalid_range_raises(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        with pytest.raises(InvalidPageRangeError):
            split_pdf_by_ranges(sample_pdf_path, [(0, 99)], tmp_path)


class TestExtractPages:
    def test_extract(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        output = tmp_path / "extracted.pdf"
        extract_pages(sample_pdf_path, [0, 2], output)
        assert output.exists()
        import fitz

        doc = fitz.open(str(output))
        assert doc.page_count == 2
        doc.close()

    def test_extract_empty_raises(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        with pytest.raises(InvalidPageRangeError):
            extract_pages(sample_pdf_path, [], tmp_path / "out.pdf")

    def test_extract_invalid_page(self, sample_pdf_path: Path, tmp_path: Path) -> None:
        with pytest.raises(InvalidPageRangeError):
            extract_pages(sample_pdf_path, [99], tmp_path / "out.pdf")

"""Multi-file PDF operations: merge, split, extract (no Qt dependency)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import fitz

from freedf.core.exceptions import InvalidPageRangeError, PDFOpenError


def merge_pdfs(paths: Sequence[str | Path], output_path: str | Path) -> None:
    """Combine multiple PDF files into a single output file."""
    if not paths:
        raise InvalidPageRangeError("No input files provided")

    output_path = Path(output_path)
    dest = fitz.open()

    try:
        for p in paths:
            p = Path(p)
            if not p.exists():
                raise PDFOpenError(str(p), "File not found")
            src = fitz.open(str(p))
            dest.insert_pdf(src)
            src.close()
        dest.save(str(output_path), garbage=3, deflate=True)
    finally:
        dest.close()


def split_pdf_by_ranges(
    source_path: str | Path,
    ranges: Sequence[tuple[int, int]],
    output_dir: str | Path,
    name_template: str = "{stem}_pages_{start}-{end}.pdf",
) -> list[Path]:
    """Split a PDF into multiple files, one per range (inclusive, 0-based)."""
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    src = fitz.open(str(source_path))
    pc = src.page_count
    results: list[Path] = []

    try:
        for start, end in ranges:
            if start < 0 or end >= pc or start > end:
                raise InvalidPageRangeError(
                    f"Range ({start}, {end}) invalid for {pc}-page document"
                )
            out = fitz.open()
            out.insert_pdf(src, from_page=start, to_page=end)
            name = name_template.format(
                stem=source_path.stem, start=start + 1, end=end + 1
            )
            out_path = output_dir / name
            out.save(str(out_path), garbage=3, deflate=True)
            out.close()
            results.append(out_path)
    finally:
        src.close()

    return results


def split_pdf_single_pages(
    source_path: str | Path,
    output_dir: str | Path,
) -> list[Path]:
    """Split a PDF into one file per page."""
    source_path = Path(source_path)
    src = fitz.open(str(source_path))
    pc = src.page_count
    src.close()
    ranges = [(i, i) for i in range(pc)]
    return split_pdf_by_ranges(
        source_path,
        ranges,
        output_dir,
        name_template="{stem}_page_{start}.pdf",
    )


def extract_pages(
    source_path: str | Path,
    page_numbers: Sequence[int],
    output_path: str | Path,
) -> None:
    """Extract selected pages (0-based) into a new PDF."""
    if not page_numbers:
        raise InvalidPageRangeError("No pages selected")

    source_path = Path(source_path)
    output_path = Path(output_path)
    src = fitz.open(str(source_path))

    try:
        for pn in page_numbers:
            if pn < 0 or pn >= src.page_count:
                raise InvalidPageRangeError(
                    f"Page {pn} out of range ({src.page_count} pages)"
                )
        dest = fitz.open()
        for pn in page_numbers:
            dest.insert_pdf(src, from_page=pn, to_page=pn)
        dest.save(str(output_path), garbage=3, deflate=True)
        dest.close()
    finally:
        src.close()

"""Shared fixtures for FreeDF tests."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def _ensure_fixtures_dir() -> None:
    FIXTURES_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def sample_pdf_path(_ensure_fixtures_dir: None) -> Path:
    """Generate a 3-page test PDF."""
    path = FIXTURES_DIR / "sample.pdf"
    if path.exists():
        return path

    doc = fitz.open()
    for i in range(3):
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text(fitz.Point(72, 72), f"Page {i + 1} of 3", fontsize=24)
        rect = fitz.Rect(72, 120, 523, 770)
        page.insert_textbox(
            rect,
            f"Content of page {i + 1}. "
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            fontsize=11,
        )
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture(scope="session")
def single_page_pdf_path(_ensure_fixtures_dir: None) -> Path:
    """Generate a single-page test PDF."""
    path = FIXTURES_DIR / "single_page.pdf"
    if path.exists():
        return path

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(72, 72), "Single Page", fontsize=18)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture()
def sample_document(sample_pdf_path: Path, tmp_path: Path) -> fitz.Document:
    """Open a copy of the sample PDF as a Document (so tests can mutate it)."""
    import shutil

    from freedf.io.loader import open_pdf

    copy_path = tmp_path / "sample_copy.pdf"
    shutil.copy(sample_pdf_path, copy_path)
    doc = open_pdf(copy_path)
    yield doc  # type: ignore[misc]
    doc.close()


@pytest.fixture()
def single_page_document(single_page_pdf_path: Path, tmp_path: Path) -> fitz.Document:
    """Open a copy of the single-page PDF."""
    import shutil

    from freedf.io.loader import open_pdf

    copy_path = tmp_path / "single_copy.pdf"
    shutil.copy(single_page_pdf_path, copy_path)
    doc = open_pdf(copy_path)
    yield doc  # type: ignore[misc]
    doc.close()

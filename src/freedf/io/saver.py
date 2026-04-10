"""PDF file saving."""

from __future__ import annotations

from pathlib import Path

import fitz

from freedf.core.document import Document
from freedf.core.exceptions import PDFSaveError


def save(document: Document) -> None:
    """Save the document to its current file_path.

    Uses incremental save when possible, falls back to full rewrite.
    """
    if document.file_path is None:
        raise PDFSaveError("<no path>", "No file path set. Use save_as() instead.")

    path_str = str(document.file_path)
    try:
        fitz_doc = document.fitz_document
        if fitz_doc.can_save_incrementally():
            fitz_doc.save(
                path_str,
                incremental=True,
                encryption=fitz.PDF_ENCRYPT_KEEP,
            )
        else:
            _full_save(document, document.file_path)
    except PDFSaveError:
        raise
    except Exception as exc:
        raise PDFSaveError(path_str, str(exc)) from exc


def save_as(document: Document, path: str | Path) -> None:
    """Save the document to a new path, then reopen from it."""
    path = Path(path)
    path_str = str(path)

    try:
        document.fitz_document.save(path_str, garbage=3, deflate=True)
    except Exception as exc:
        raise PDFSaveError(path_str, str(exc)) from exc

    try:
        new_fitz_doc = fitz.open(path_str)
    except Exception as exc:
        raise PDFSaveError(path_str, f"Saved but failed to reopen: {exc}") from exc

    old_fitz_doc = document.fitz_document
    document._fitz_doc = new_fitz_doc
    document.file_path = path
    old_fitz_doc.close()


def _full_save(document: Document, path: Path) -> None:
    """Full rewrite: tobytes -> close -> write -> reopen."""
    fitz_doc = document.fitz_document
    data = fitz_doc.tobytes(garbage=3, deflate=True)
    fitz_doc.close()

    path.write_bytes(data)

    new_fitz_doc = fitz.open(str(path))
    document._fitz_doc = new_fitz_doc

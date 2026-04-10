"""PDF file loading."""

from __future__ import annotations

from pathlib import Path

import fitz

from freedf.core.document import Document
from freedf.core.exceptions import PDFOpenError, PDFPasswordRequiredError


def open_pdf(path: str | Path, password: str | None = None) -> Document:
    """Open a PDF file and return a Document wrapper."""
    path = Path(path)

    if not path.exists():
        raise PDFOpenError(str(path), "File not found")

    if not path.is_file():
        raise PDFOpenError(str(path), "Not a file")

    try:
        fitz_doc = fitz.open(str(path))
    except Exception as exc:
        raise PDFOpenError(str(path), str(exc)) from exc

    if fitz_doc.needs_pass:
        if password is None:
            fitz_doc.close()
            raise PDFPasswordRequiredError(str(path), "Password required")
        if not fitz_doc.authenticate(password):
            fitz_doc.close()
            raise PDFPasswordRequiredError(str(path), "Incorrect password")

    if not fitz_doc.is_pdf:
        fitz_doc.close()
        raise PDFOpenError(str(path), "Not a valid PDF file")

    return Document(fitz_doc, file_path=path)

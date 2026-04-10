"""FreeDF core — PDF document model (no Qt dependencies)."""

from freedf.core.document import Document
from freedf.core.exceptions import (
    FreedfError,
    InvalidRotationError,
    PageIndexError,
    PDFOpenError,
    PDFPasswordRequiredError,
    PDFSaveError,
    SinglePageDeleteError,
)
from freedf.core.page import Page

__all__ = [
    "Document",
    "FreedfError",
    "InvalidRotationError",
    "PDFOpenError",
    "PDFPasswordRequiredError",
    "PDFSaveError",
    "Page",
    "PageIndexError",
    "SinglePageDeleteError",
]

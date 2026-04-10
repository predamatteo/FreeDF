"""FreeDF exception hierarchy."""

from __future__ import annotations


class FreedfError(Exception):
    """Base exception for all FreeDF errors."""


class PDFOpenError(FreedfError):
    """Raised when a PDF file cannot be opened."""

    def __init__(self, path: str, reason: str = "") -> None:
        self.path = path
        self.reason = reason
        msg = f"Cannot open '{path}': {reason}" if reason else f"Cannot open '{path}'"
        super().__init__(msg)


class PDFSaveError(FreedfError):
    """Raised when saving a PDF fails."""

    def __init__(self, path: str, reason: str = "") -> None:
        self.path = path
        self.reason = reason
        msg = f"Cannot save '{path}': {reason}" if reason else f"Cannot save '{path}'"
        super().__init__(msg)


class PDFPasswordRequiredError(PDFOpenError):
    """Raised when the PDF is encrypted and no/wrong password was supplied."""


class PageIndexError(FreedfError):
    """Raised when a page index is out of range."""

    def __init__(self, index: int, page_count: int) -> None:
        self.index = index
        self.page_count = page_count
        msg = f"Page index {index} out of range ({page_count} pages)"
        super().__init__(msg)


class SinglePageDeleteError(FreedfError):
    """Raised when attempting to delete the last remaining page."""

    def __init__(self) -> None:
        super().__init__("Cannot delete the only remaining page")


class InvalidRotationError(FreedfError):
    """Raised when rotation is not one of 0, 90, 180, 270."""

    def __init__(self, value: int) -> None:
        self.value = value
        super().__init__(f"Invalid rotation {value}: must be 0, 90, 180, or 270")

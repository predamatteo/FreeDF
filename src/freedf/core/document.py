"""Document wrapper around fitz.Document (no Qt dependency)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import fitz

from freedf.core.exceptions import (
    PageIndexError,
    SinglePageDeleteError,
)
from freedf.core.page import Page

ModificationCallback = Callable[["Document", int | None], None]


class Document:
    """High-level wrapper around fitz.Document.

    Owns the fitz.Document lifecycle. All PDF mutations go through this
    class so that modification callbacks fire reliably.
    """

    def __init__(self, fitz_doc: fitz.Document, file_path: Path | None = None) -> None:
        self._fitz_doc = fitz_doc
        self._file_path = file_path
        self._modification_callbacks: list[ModificationCallback] = []

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    @file_path.setter
    def file_path(self, value: Path | None) -> None:
        self._file_path = value

    @property
    def page_count(self) -> int:
        return int(self._fitz_doc.page_count)

    @property
    def metadata(self) -> dict[str, str]:
        meta = self._fitz_doc.metadata
        if meta is None:
            return {}
        return {k: str(v) for k, v in meta.items() if v is not None}

    @property
    def is_dirty(self) -> bool:
        return bool(self._fitz_doc.is_dirty)

    @property
    def is_pdf(self) -> bool:
        return bool(self._fitz_doc.is_pdf)

    @property
    def fitz_document(self) -> fitz.Document:
        return self._fitz_doc

    # --- Modification callbacks ---

    def add_modification_callback(self, cb: ModificationCallback) -> None:
        self._modification_callbacks.append(cb)

    def remove_modification_callback(self, cb: ModificationCallback) -> None:
        self._modification_callbacks.remove(cb)

    def _notify_modified(self, page_number: int | None = None) -> None:
        for cb in list(self._modification_callbacks):
            cb(self, page_number)

    # --- Page access ---

    def get_page(self, page_number: int) -> Page:
        self._validate_page_index(page_number)
        return Page(self._fitz_doc[page_number], page_number)

    def _validate_page_index(self, page_number: int) -> None:
        if not 0 <= page_number < self.page_count:
            raise PageIndexError(page_number, self.page_count)

    # --- Page mutations (called by commands) ---

    def rotate_page(self, page_number: int, degrees: int) -> None:
        page = self.get_page(page_number)
        page.set_rotation(degrees)
        self._notify_modified(page_number)

    def delete_page(self, page_number: int) -> None:
        if self.page_count <= 1:
            raise SinglePageDeleteError()
        self._validate_page_index(page_number)
        self._fitz_doc.delete_page(page_number)
        self._notify_modified(None)

    def insert_pdf_page(
        self,
        source_doc: fitz.Document,
        source_page: int,
        insert_at: int,
    ) -> None:
        self._fitz_doc.insert_pdf(
            source_doc,
            from_page=source_page,
            to_page=source_page,
            start_at=insert_at,
        )
        self._notify_modified(None)

    def duplicate_page(self, page_number: int) -> int:
        self._validate_page_index(page_number)
        if page_number >= self.page_count - 1:
            # Last page: fullcopy_page requires -1 to append at end
            self._fitz_doc.fullcopy_page(page_number, -1)
        else:
            self._fitz_doc.fullcopy_page(page_number, page_number + 1)
        new_page_index = page_number + 1
        self._notify_modified(None)
        return new_page_index

    def backup_page(self, page_number: int) -> bytes:
        """Serialize a single page to PDF bytes (for undo storage)."""
        self._validate_page_index(page_number)
        tmp_doc = fitz.open()
        tmp_doc.insert_pdf(self._fitz_doc, from_page=page_number, to_page=page_number)
        data = tmp_doc.tobytes()
        tmp_doc.close()
        return bytes(data)

    # --- Lifecycle ---

    def close(self) -> None:
        if self._fitz_doc and not self._fitz_doc.is_closed:
            self._fitz_doc.close()

    def __enter__(self) -> Document:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

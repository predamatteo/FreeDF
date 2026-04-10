"""Concrete page commands for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass, field

import fitz

from freedf.core.document import Document


@dataclass
class RotatePageCommand:
    """Rotate a page to a new absolute rotation."""

    document: Document
    page_number: int
    new_rotation: int
    _old_rotation: int = field(init=False, default=0)

    @property
    def description(self) -> str:
        return f"Rotate page {self.page_number + 1} to {self.new_rotation}\u00b0"

    def execute(self) -> None:
        page = self.document.get_page(self.page_number)
        self._old_rotation = page.rotation
        self.document.rotate_page(self.page_number, self.new_rotation)

    def undo(self) -> None:
        self.document.rotate_page(self.page_number, self._old_rotation)


@dataclass
class DeletePageCommand:
    """Delete a page with full undo support via page backup."""

    document: Document
    page_number: int
    _backup_bytes: bytes = field(init=False, default=b"")

    @property
    def description(self) -> str:
        return f"Delete page {self.page_number + 1}"

    def execute(self) -> None:
        self._backup_bytes = self.document.backup_page(self.page_number)
        self.document.delete_page(self.page_number)

    def undo(self) -> None:
        backup_doc = fitz.open(stream=self._backup_bytes, filetype="pdf")
        self.document.insert_pdf_page(
            source_doc=backup_doc,
            source_page=0,
            insert_at=self.page_number,
        )
        backup_doc.close()


@dataclass
class DuplicatePageCommand:
    """Duplicate a page, inserting the copy after the original."""

    document: Document
    page_number: int
    _copy_index: int = field(init=False, default=-1)

    @property
    def description(self) -> str:
        return f"Duplicate page {self.page_number + 1}"

    def execute(self) -> None:
        self._copy_index = self.document.duplicate_page(self.page_number)

    def undo(self) -> None:
        self.document.delete_page(self._copy_index)

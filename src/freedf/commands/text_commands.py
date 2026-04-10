"""Text editing commands for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass, field

import fitz

from freedf.core.annotations import Color, Rect
from freedf.core.document import Document
from freedf.core.text_edit import (
    add_watermark,
    insert_text_on_page,
    replace_text_on_page,
)


@dataclass
class ReplaceTextCommand:
    """Find and replace text on a page (page-backup undo)."""

    document: Document
    page_number: int
    old_text: str
    new_text: str
    font_size: float = 11.0
    color: Color | None = None
    _page_backup: bytes = field(init=False, default=b"")
    _count: int = field(init=False, default=0)

    @property
    def description(self) -> str:
        return f"Replace '{self.old_text}' on page {self.page_number + 1}"

    def execute(self) -> None:
        self._page_backup = self.document.backup_page(self.page_number)
        self._count = replace_text_on_page(
            self.document,
            self.page_number,
            self.old_text,
            self.new_text,
            self.font_size,
            self.color,
        )

    def undo(self) -> None:
        self.document.restore_page_from_backup(self.page_number, self._page_backup)


@dataclass
class InsertTextCommand:
    """Insert text on a page (page-backup undo)."""

    document: Document
    page_number: int
    x: float
    y: float
    text: str
    font_size: float = 12.0
    color: Color | None = None
    _page_backup: bytes = field(init=False, default=b"")

    @property
    def description(self) -> str:
        return f"Insert text on page {self.page_number + 1}"

    def execute(self) -> None:
        self._page_backup = self.document.backup_page(self.page_number)
        insert_text_on_page(
            self.document,
            self.page_number,
            self.x,
            self.y,
            self.text,
            self.font_size,
            self.color,
        )

    def undo(self) -> None:
        self.document.restore_page_from_backup(self.page_number, self._page_backup)


@dataclass
class AddWatermarkCommand:
    """Add watermark to pages (page-backup undo for all)."""

    document: Document
    text: str
    page_numbers: list[int] | None = None
    font_size: float = 60.0
    color: Color | None = None
    opacity: float = 0.3
    _page_backups: dict[int, bytes] = field(init=False, default_factory=dict)

    @property
    def description(self) -> str:
        return f"Add watermark '{self.text}'"

    def execute(self) -> None:
        pages = self.page_numbers or list(range(self.document.page_count))
        for pn in pages:
            self._page_backups[pn] = self.document.backup_page(pn)
        add_watermark(
            self.document,
            self.text,
            self.page_numbers,
            self.font_size,
            self.color,
            self.opacity,
        )

    def undo(self) -> None:
        for pn in sorted(self._page_backups.keys(), reverse=True):
            self.document.restore_page_from_backup(pn, self._page_backups[pn])


@dataclass
class RedactAreaCommand:
    """Redact (black out) an area of a page (page-backup undo)."""

    document: Document
    page_number: int
    rect: Rect
    _page_backup: bytes = field(init=False, default=b"")

    @property
    def description(self) -> str:
        return f"Redact area on page {self.page_number + 1}"

    def execute(self) -> None:
        self._page_backup = self.document.backup_page(self.page_number)
        page = self.document.fitz_document[self.page_number]
        fitz_rect = fitz.Rect(self.rect.x0, self.rect.y0, self.rect.x1, self.rect.y1)
        page.add_redact_annot(fitz_rect, fill=(0, 0, 0))
        page.apply_redactions()
        self.document._notify_modified(self.page_number)

    def undo(self) -> None:
        self.document.restore_page_from_backup(self.page_number, self._page_backup)

"""OCR commands for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass, field

from freedf.core.document import Document
from freedf.core.ocr import apply_ocr_text_layer, ocr_page


@dataclass
class OCRPageCommand:
    """Run OCR on a single page and apply invisible text layer."""

    document: Document
    page_number: int
    language: str = "eng"
    dpi: int = 300
    _page_backup: bytes = field(init=False, default=b"")

    @property
    def description(self) -> str:
        return f"OCR page {self.page_number + 1}"

    def execute(self) -> None:
        self._page_backup = self.document.backup_page(self.page_number)
        result = ocr_page(self.document, self.page_number, self.language, self.dpi)
        apply_ocr_text_layer(self.document, self.page_number, result)

    def undo(self) -> None:
        self.document.restore_page_from_backup(self.page_number, self._page_backup)


@dataclass
class OCRDocumentCommand:
    """Run OCR on multiple pages (batch)."""

    document: Document
    page_numbers: list[int]
    language: str = "eng"
    dpi: int = 300
    _page_backups: dict[int, bytes] = field(init=False, default_factory=dict)

    @property
    def description(self) -> str:
        n = len(self.page_numbers)
        return f"OCR {n} page{'s' if n != 1 else ''}"

    def execute(self) -> None:
        for pn in self.page_numbers:
            self._page_backups[pn] = self.document.backup_page(pn)
            result = ocr_page(self.document, pn, self.language, self.dpi)
            apply_ocr_text_layer(self.document, pn, result)

    def undo(self) -> None:
        for pn in sorted(self._page_backups.keys(), reverse=True):
            self.document.restore_page_from_backup(pn, self._page_backups[pn])

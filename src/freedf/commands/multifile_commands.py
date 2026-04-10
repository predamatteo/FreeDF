"""Multi-file commands for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass, field

import fitz

from freedf.core.document import Document


@dataclass
class InsertPagesCommand:
    """Insert pages from another PDF into the current document."""

    document: Document
    source_pdf_bytes: bytes
    source_page_numbers: list[int]
    insert_at: int
    _inserted_count: int = field(init=False, default=0)

    @property
    def description(self) -> str:
        n = len(self.source_page_numbers)
        s = "s" if n != 1 else ""
        return f"Insert {n} page{s} at position {self.insert_at + 1}"

    def execute(self) -> None:
        source_doc = fitz.open(stream=self.source_pdf_bytes, filetype="pdf")
        try:
            for i, src_page in enumerate(self.source_page_numbers):
                self.document.insert_pdf_page(source_doc, src_page, self.insert_at + i)
            self._inserted_count = len(self.source_page_numbers)
        finally:
            source_doc.close()

    def undo(self) -> None:
        for i in range(self._inserted_count - 1, -1, -1):
            self.document.delete_page(self.insert_at + i)

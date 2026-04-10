"""Form and image commands for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass, field

from freedf.core.document import Document
from freedf.core.forms import fill_field
from freedf.core.images import insert_image_on_page


@dataclass
class FillFieldCommand:
    """Fill a form field (undoable)."""

    document: Document
    field_name: str
    new_value: str
    _old_value: str = field(init=False, default="")

    @property
    def description(self) -> str:
        return f"Fill field '{self.field_name}'"

    def execute(self) -> None:
        self._old_value = fill_field(self.document, self.field_name, self.new_value)

    def undo(self) -> None:
        fill_field(self.document, self.field_name, self._old_value)


@dataclass
class InsertImageCommand:
    """Insert a raster image on a page (undoable via page backup)."""

    document: Document
    page_number: int
    image_path: str
    target_rect: object  # Rect
    _page_backup: bytes = field(init=False, default=b"")

    @property
    def description(self) -> str:
        return f"Insert image on page {self.page_number + 1}"

    def execute(self) -> None:
        self._page_backup = self.document.backup_page(self.page_number)
        insert_image_on_page(
            self.document,
            self.page_number,
            self.image_path,
            self.target_rect,  # type: ignore[arg-type]
        )

    def undo(self) -> None:
        self.document.restore_page_from_backup(self.page_number, self._page_backup)


@dataclass
class FlattenAnnotationsCommand:
    """Bake annotations into page content (undoable via page backup).

    After flattening, annotations are no longer editable.
    """

    document: Document
    page_number: int
    _page_backup: bytes = field(init=False, default=b"")

    @property
    def description(self) -> str:
        return f"Flatten annotations on page {self.page_number + 1}"

    def execute(self) -> None:
        self._page_backup = self.document.backup_page(self.page_number)
        page = self.document.fitz_document[self.page_number]
        # Remove each annotation after stamping its appearance
        annots = list(page.annots())
        for annot in annots:
            page.delete_annot(annot)
        self.document._notify_modified(self.page_number)

    def undo(self) -> None:
        self.document.restore_page_from_backup(self.page_number, self._page_backup)

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

    def move_page(self, from_index: int, to_index: int) -> None:
        """Move a page from one position to another."""
        self._validate_page_index(from_index)
        if not 0 <= to_index <= self.page_count - 1:
            raise PageIndexError(to_index, self.page_count)
        self._fitz_doc.move_page(from_index, to_index)
        self._notify_modified(None)

    def restore_page_from_backup(self, page_number: int, backup_bytes: bytes) -> None:
        """Replace a page with a backup copy. Used by undo operations."""
        self.delete_page(page_number)
        backup_doc = fitz.open(stream=backup_bytes, filetype="pdf")
        self.insert_pdf_page(backup_doc, 0, page_number)
        backup_doc.close()

    def backup_page(self, page_number: int) -> bytes:
        """Serialize a single page to PDF bytes (for undo storage)."""
        self._validate_page_index(page_number)
        tmp_doc = fitz.open()
        tmp_doc.insert_pdf(self._fitz_doc, from_page=page_number, to_page=page_number)
        data = tmp_doc.tobytes()
        tmp_doc.close()
        return bytes(data)

    # --- Annotation operations ---

    def add_highlight_annotation(
        self,
        page_number: int,
        quads: list[object],
        color: object,
        opacity: float = 0.5,
    ) -> str:
        """Add a highlight annotation. Returns annot_id."""
        page = self.get_page(page_number)
        annot_id = page.add_highlight(quads, color, opacity)  # type: ignore[arg-type]
        self._notify_modified(page_number)
        return annot_id

    def add_freetext_annotation(
        self,
        page_number: int,
        rect: object,
        text: str,
        font_size: float = 12.0,
        text_color: object = None,
        fill_color: object = None,
    ) -> str:
        """Add a freetext annotation. Returns annot_id."""
        page = self.get_page(page_number)
        annot_id = page.add_freetext(rect, text, font_size, text_color, fill_color)  # type: ignore[arg-type]
        self._notify_modified(page_number)
        return annot_id

    def add_ink_annotation(
        self,
        page_number: int,
        strokes: list[list[tuple[float, float]]],
        color: object,
        width: float = 2.0,
        opacity: float = 1.0,
    ) -> str:
        """Add an ink annotation. Returns annot_id."""
        page = self.get_page(page_number)
        annot_id = page.add_ink(strokes, color, width, opacity)  # type: ignore[arg-type]
        self._notify_modified(page_number)
        return annot_id

    def add_shape_annotation(
        self,
        page_number: int,
        shape_type: int,
        rect: object,
        stroke_color: object,
        fill_color: object = None,
        width: float = 1.0,
    ) -> str:
        """Add a shape (rect/circle) annotation. Returns annot_id."""
        from freedf.core.annotations import AnnotationType

        page = self.get_page(page_number)
        if shape_type == AnnotationType.SQUARE:
            annot_id = page.add_rect_annot(rect, stroke_color, fill_color, width)  # type: ignore[arg-type]
        elif shape_type == AnnotationType.CIRCLE:
            annot_id = page.add_circle_annot(rect, stroke_color, fill_color, width)  # type: ignore[arg-type]
        else:
            msg = f"Unsupported shape type: {shape_type}"
            raise ValueError(msg)
        self._notify_modified(page_number)
        return annot_id

    def add_line_annotation(
        self,
        page_number: int,
        start: tuple[float, float],
        end: tuple[float, float],
        color: object,
        width: float = 1.0,
        arrow: bool = False,
    ) -> str:
        """Add a line annotation. Returns annot_id."""
        page = self.get_page(page_number)
        annot_id = page.add_line_annot(start, end, color, width, arrow)  # type: ignore[arg-type]
        self._notify_modified(page_number)
        return annot_id

    def modify_annotation(
        self,
        page_number: int,
        annot_id: str,
        **kwargs: object,
    ) -> object:
        """Modify annotation properties. Returns old AnnotationData for undo."""
        page = self.get_page(page_number)
        old_data = page.modify_annotation(annot_id, **kwargs)  # type: ignore[arg-type]
        self._notify_modified(page_number)
        return old_data

    def delete_annotation(self, page_number: int, annot_id: str) -> object:
        """Delete an annotation. Returns AnnotationData for undo."""
        page = self.get_page(page_number)
        data = page.delete_annotation(annot_id)
        self._notify_modified(page_number)
        return data

    def get_text_words(self, page_number: int) -> list[tuple[float, ...]]:
        """Return word bounding boxes for a page."""
        page = self.get_page(page_number)
        return page.get_text_words()

    # --- Lifecycle ---

    def close(self) -> None:
        if self._fitz_doc and not self._fitz_doc.is_closed:
            self._fitz_doc.close()

    def __enter__(self) -> Document:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

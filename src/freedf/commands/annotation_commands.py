"""Annotation commands for undo/redo."""

from __future__ import annotations

from dataclasses import dataclass, field

import fitz

from freedf.core.annotations import AnnotationData, AnnotationType, Color, Rect
from freedf.core.document import Document


@dataclass
class AddHighlightCommand:
    """Add a highlight annotation over selected text."""

    document: Document
    page_number: int
    quads: list[fitz.Quad]
    color: Color
    opacity: float = 0.5
    _annot_id: str = field(init=False, default="")

    @property
    def description(self) -> str:
        return f"Highlight on page {self.page_number + 1}"

    def execute(self) -> None:
        self._annot_id = self.document.add_highlight_annotation(
            self.page_number, self.quads, self.color, self.opacity
        )

    def undo(self) -> None:
        self.document.delete_annotation(self.page_number, self._annot_id)


@dataclass
class AddFreeTextCommand:
    """Add a freetext annotation."""

    document: Document
    page_number: int
    rect: Rect
    text: str
    font_size: float = 12.0
    text_color: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))
    fill_color: Color | None = None
    _annot_id: str = field(init=False, default="")

    @property
    def description(self) -> str:
        return f"Text note on page {self.page_number + 1}"

    def execute(self) -> None:
        self._annot_id = self.document.add_freetext_annotation(
            self.page_number,
            self.rect,
            self.text,
            self.font_size,
            self.text_color,
            self.fill_color,
        )

    def undo(self) -> None:
        self.document.delete_annotation(self.page_number, self._annot_id)


@dataclass
class AddInkCommand:
    """Add an ink (freehand) annotation."""

    document: Document
    page_number: int
    strokes: list[list[tuple[float, float]]]
    color: Color
    width: float = 2.0
    opacity: float = 1.0
    _annot_id: str = field(init=False, default="")

    @property
    def description(self) -> str:
        return f"Ink drawing on page {self.page_number + 1}"

    def execute(self) -> None:
        self._annot_id = self.document.add_ink_annotation(
            self.page_number,
            self.strokes,
            self.color,
            self.width,
            self.opacity,
        )

    def undo(self) -> None:
        self.document.delete_annotation(self.page_number, self._annot_id)


@dataclass
class AddShapeCommand:
    """Add a shape annotation (rectangle or circle)."""

    document: Document
    page_number: int
    shape_type: AnnotationType
    rect: Rect
    stroke_color: Color
    fill_color: Color | None = None
    width: float = 1.0
    _annot_id: str = field(init=False, default="")

    @property
    def description(self) -> str:
        name = "Rectangle" if self.shape_type == AnnotationType.SQUARE else "Ellipse"
        return f"{name} on page {self.page_number + 1}"

    def execute(self) -> None:
        self._annot_id = self.document.add_shape_annotation(
            self.page_number,
            self.shape_type,
            self.rect,
            self.stroke_color,
            self.fill_color,
            self.width,
        )

    def undo(self) -> None:
        self.document.delete_annotation(self.page_number, self._annot_id)


@dataclass
class AddLineCommand:
    """Add a line or arrow annotation."""

    document: Document
    page_number: int
    start: tuple[float, float]
    end: tuple[float, float]
    color: Color
    width: float = 1.0
    arrow: bool = False
    _annot_id: str = field(init=False, default="")

    @property
    def description(self) -> str:
        kind = "Arrow" if self.arrow else "Line"
        return f"{kind} on page {self.page_number + 1}"

    def execute(self) -> None:
        self._annot_id = self.document.add_line_annotation(
            self.page_number,
            self.start,
            self.end,
            self.color,
            self.width,
            self.arrow,
        )

    def undo(self) -> None:
        self.document.delete_annotation(self.page_number, self._annot_id)


@dataclass
class ModifyAnnotationCommand:
    """Modify annotation properties (color, opacity, rect, etc.)."""

    document: Document
    page_number: int
    annot_id: str
    new_props: dict[str, object]
    _old_data: AnnotationData | None = field(init=False, default=None)

    @property
    def description(self) -> str:
        return f"Modify annotation on page {self.page_number + 1}"

    def execute(self) -> None:
        result = self.document.modify_annotation(
            self.page_number, self.annot_id, **self.new_props
        )
        self._old_data = result  # type: ignore[assignment]

    def undo(self) -> None:
        if self._old_data is None:
            return
        old = self._old_data
        restore: dict[str, object] = {}
        if old.color_stroke and "stroke_color" in self.new_props:
            restore["stroke_color"] = old.color_stroke
        if old.color_fill and "fill_color" in self.new_props:
            restore["fill_color"] = old.color_fill
        if "opacity" in self.new_props:
            restore["opacity"] = old.opacity
        if "border_width" in self.new_props:
            restore["border_width"] = old.border_width
        if "rect" in self.new_props:
            restore["rect"] = old.rect
        if restore:
            self.document.modify_annotation(self.page_number, self.annot_id, **restore)


@dataclass
class DeleteAnnotationCommand:
    """Delete an existing annotation (undoable)."""

    document: Document
    page_number: int
    annot_id: str
    _backup_data: AnnotationData | None = field(init=False, default=None)

    @property
    def description(self) -> str:
        return f"Delete annotation on page {self.page_number + 1}"

    def execute(self) -> None:
        result = self.document.delete_annotation(self.page_number, self.annot_id)
        self._backup_data = result  # type: ignore[assignment]

    def undo(self) -> None:
        if self._backup_data is None:
            return
        data = self._backup_data
        new_id = _recreate_annotation(self.document, self.page_number, data)
        if new_id:
            self.annot_id = new_id


def _recreate_annotation(
    document: Document, page_number: int, data: AnnotationData
) -> str:
    """Recreate an annotation from its backup data. Returns new annot_id."""
    if data.annot_type == AnnotationType.HIGHLIGHT:
        quads = []
        for quad_pts in data.vertices:
            if len(quad_pts) == 4:
                q = fitz.Quad(
                    fitz.Point(*quad_pts[0]),
                    fitz.Point(*quad_pts[1]),
                    fitz.Point(*quad_pts[2]),
                    fitz.Point(*quad_pts[3]),
                )
                quads.append(q)
        color = data.color_stroke or Color.yellow()
        return document.add_highlight_annotation(
            page_number, quads, color, data.opacity
        )
    elif data.annot_type == AnnotationType.FREE_TEXT:
        return document.add_freetext_annotation(
            page_number,
            data.rect,
            data.content,
            data.font_size,
            data.color_stroke,
            data.color_fill,
        )
    elif data.annot_type == AnnotationType.INK:
        color = data.color_stroke or Color(0.0, 0.0, 0.0)
        return document.add_ink_annotation(
            page_number, data.vertices, color, data.border_width, data.opacity
        )
    elif data.annot_type in (AnnotationType.SQUARE, AnnotationType.CIRCLE):
        color = data.color_stroke or Color(0.0, 0.0, 0.0)
        return document.add_shape_annotation(
            page_number,
            data.annot_type,
            data.rect,
            color,
            data.color_fill,
            data.border_width,
        )
    elif data.annot_type == AnnotationType.LINE:
        color = data.color_stroke or Color(0.0, 0.0, 0.0)
        if len(data.vertices) >= 1 and len(data.vertices[0]) >= 2:
            start = data.vertices[0][0]
            end = data.vertices[0][1]
        else:
            start = (data.rect.x0, data.rect.y0)
            end = (data.rect.x1, data.rect.y1)
        return document.add_line_annotation(
            page_number, start, end, color, data.border_width
        )
    return ""

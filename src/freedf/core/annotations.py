"""Pure data classes for PDF annotations (no fitz/Qt dependency)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class AnnotationType(IntEnum):
    """Annotation types (values mirror fitz.PDF_ANNOT_* constants)."""

    FREE_TEXT = 2
    LINE = 3
    SQUARE = 4
    CIRCLE = 5
    HIGHLIGHT = 8
    INK = 15


@dataclass(frozen=True)
class Rect:
    """Axis-aligned rectangle in PDF points."""

    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0


@dataclass(frozen=True)
class Color:
    """RGB color with components in [0.0, 1.0]."""

    r: float
    g: float
    b: float

    @classmethod
    def yellow(cls) -> Color:
        return cls(1.0, 1.0, 0.0)

    @classmethod
    def red(cls) -> Color:
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def green(cls) -> Color:
        return cls(0.0, 1.0, 0.0)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.r, self.g, self.b)


@dataclass(frozen=True)
class AnnotationData:
    """Immutable snapshot of an annotation's properties."""

    annot_type: AnnotationType
    rect: Rect
    color_stroke: Color | None = None
    color_fill: Color | None = None
    content: str = ""
    opacity: float = 1.0
    annot_id: str = ""
    border_width: float = 1.0
    font_size: float = 12.0
    vertices: list[list[tuple[float, float]]] = field(default_factory=list)

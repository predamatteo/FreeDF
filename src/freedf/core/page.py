"""Page wrapper around a single fitz.Page (no Qt dependency)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import fitz

from freedf.core.annotations import AnnotationData, AnnotationType, Color, Rect
from freedf.core.exceptions import InvalidRotationError

if TYPE_CHECKING:
    pass

VALID_ROTATIONS = frozenset({0, 90, 180, 270})


class Page:
    """Lightweight wrapper around a fitz.Page.

    Page objects are obtained via Document.get_page() and should not be
    cached — they become invalid after structural document changes.
    """

    def __init__(self, fitz_page: fitz.Page, page_number: int) -> None:
        self._fitz_page = fitz_page
        self._page_number = page_number

    @property
    def page_number(self) -> int:
        """Zero-based page index."""
        return self._page_number

    @property
    def rotation(self) -> int:
        """Current rotation in degrees (0, 90, 180, 270)."""
        return int(self._fitz_page.rotation)

    @property
    def rect(self) -> Rect:
        """Page bounding rectangle in PDF points."""
        r = self._fitz_page.rect
        return Rect(r.x0, r.y0, r.x1, r.y1)

    @property
    def width(self) -> float:
        return float(self._fitz_page.rect.width)

    @property
    def height(self) -> float:
        return float(self._fitz_page.rect.height)

    def set_rotation(self, degrees: int) -> None:
        """Set absolute rotation. Must be 0, 90, 180, or 270."""
        if degrees not in VALID_ROTATIONS:
            raise InvalidRotationError(degrees)
        self._fitz_page.set_rotation(degrees)

    def get_text(self, option: str = "text") -> str:
        """Extract text from the page."""
        result = self._fitz_page.get_text(option)
        if isinstance(result, str):
            return result
        return str(result)

    def get_annotations(self) -> list[AnnotationData]:
        """Return annotation data for all annotations on this page."""
        result: list[AnnotationData] = []
        for annot in self._fitz_page.annots():
            data = self._annot_to_data(annot)
            if data is not None:
                result.append(data)
        return result

    def get_pixmap(
        self,
        zoom: float = 1.0,
        dpi: int | None = None,
        alpha: bool = False,
    ) -> fitz.Pixmap:
        """Render page to a fitz.Pixmap.

        Args:
            zoom: Scaling factor (1.0 = 72 DPI native).
            dpi: If set, overrides zoom.
            alpha: Include alpha channel.
        """
        if dpi is not None:
            scale = dpi / 72.0
            mat = fitz.Matrix(scale, scale)
        else:
            mat = fitz.Matrix(zoom, zoom)
        return self._fitz_page.get_pixmap(matrix=mat, alpha=alpha)

    @staticmethod
    def _annot_to_data(annot: fitz.Annot) -> AnnotationData | None:
        """Convert a fitz.Annot to an AnnotationData."""
        try:
            annot_type_val = annot.type[0]
            if annot_type_val not in (t.value for t in AnnotationType):
                return None

            r = annot.rect
            rect = Rect(r.x0, r.y0, r.x1, r.y1)

            colors = annot.colors
            stroke = None
            fill = None
            if colors.get("stroke"):
                s = colors["stroke"]
                stroke = Color(float(s[0]), float(s[1]), float(s[2]))
            if colors.get("fill"):
                f = colors["fill"]
                fill = Color(float(f[0]), float(f[1]), float(f[2]))

            return AnnotationData(
                annot_type=AnnotationType(annot_type_val),
                rect=rect,
                color_stroke=stroke,
                color_fill=fill,
                content=annot.info.get("content", ""),
                opacity=annot.opacity,
                annot_id=str(annot.xref),
            )
        except Exception:
            return None

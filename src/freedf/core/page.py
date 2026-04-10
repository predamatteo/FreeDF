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

            # Extract vertices for highlight/ink
            vertices: list[list[tuple[float, float]]] = []
            if annot_type_val == AnnotationType.HIGHLIGHT:
                try:
                    vs = annot.vertices
                    if vs:
                        # Group into quads of 4 points
                        pts = [
                            (float(vs[i]), float(vs[i + 1]))
                            for i in range(0, len(vs), 2)
                        ]
                        quad: list[tuple[float, float]] = []
                        for pt in pts:
                            quad.append(pt)
                            if len(quad) == 4:
                                vertices.append(quad)
                                quad = []
                except Exception:
                    pass

            return AnnotationData(
                annot_type=AnnotationType(annot_type_val),
                rect=rect,
                color_stroke=stroke,
                color_fill=fill,
                content=annot.info.get("content", ""),
                opacity=annot.opacity,
                annot_id=str(annot.xref),
                vertices=vertices,
            )
        except Exception:
            return None

    def add_highlight(
        self,
        quads: list[fitz.Quad],
        color: Color,
        opacity: float = 0.5,
    ) -> str:
        """Add a highlight annotation. Returns annot xref as string."""
        annot = self._fitz_page.add_highlight_annot(quads=quads)
        annot.set_colors(stroke=color.to_tuple())
        annot.set_opacity(opacity)
        annot.update()
        return str(annot.xref)

    def add_freetext(
        self,
        rect: Rect,
        text: str,
        font_size: float = 12.0,
        text_color: Color | None = None,
        fill_color: Color | None = None,
    ) -> str:
        """Add a freetext annotation. Returns annot xref as string."""
        fitz_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
        tc = text_color.to_tuple() if text_color else (0.0, 0.0, 0.0)
        annot = self._fitz_page.add_freetext_annot(
            fitz_rect,
            text,
            fontsize=font_size,
            text_color=tc,
        )
        if fill_color:
            annot.set_colors(fill=fill_color.to_tuple())
        annot.update()
        return str(annot.xref)

    def add_ink(
        self,
        strokes: list[list[tuple[float, float]]],
        color: Color,
        width: float = 2.0,
        opacity: float = 1.0,
    ) -> str:
        """Add an ink (freehand) annotation. Returns annot xref."""
        fitz_strokes = [[fitz.Point(x, y) for x, y in stroke] for stroke in strokes]
        annot = self._fitz_page.add_ink_annot(fitz_strokes)
        annot.set_colors(stroke=color.to_tuple())
        annot.set_border(width=width)
        annot.set_opacity(opacity)
        annot.update()
        return str(annot.xref)

    def add_rect_annot(
        self,
        rect: Rect,
        stroke_color: Color,
        fill_color: Color | None = None,
        width: float = 1.0,
    ) -> str:
        """Add a rectangle annotation. Returns annot xref."""
        fitz_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
        annot = self._fitz_page.add_rect_annot(fitz_rect)
        annot.set_colors(stroke=stroke_color.to_tuple())
        if fill_color:
            annot.set_colors(fill=fill_color.to_tuple())
        annot.set_border(width=width)
        annot.update()
        return str(annot.xref)

    def add_circle_annot(
        self,
        rect: Rect,
        stroke_color: Color,
        fill_color: Color | None = None,
        width: float = 1.0,
    ) -> str:
        """Add a circle/ellipse annotation. Returns annot xref."""
        fitz_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
        annot = self._fitz_page.add_circle_annot(fitz_rect)
        annot.set_colors(stroke=stroke_color.to_tuple())
        if fill_color:
            annot.set_colors(fill=fill_color.to_tuple())
        annot.set_border(width=width)
        annot.update()
        return str(annot.xref)

    def add_line_annot(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: Color,
        width: float = 1.0,
        arrow: bool = False,
    ) -> str:
        """Add a line annotation. Returns annot xref."""
        p1, p2 = fitz.Point(*start), fitz.Point(*end)
        annot = self._fitz_page.add_line_annot(p1, p2)
        annot.set_colors(stroke=color.to_tuple())
        annot.set_border(width=width)
        if arrow:
            annot.set_line_ends(0, fitz.PDF_ANNOT_LE_OPEN_ARROW)
        annot.update()
        return str(annot.xref)

    def modify_annotation(
        self,
        annot_id: str,
        *,
        stroke_color: Color | None = None,
        fill_color: Color | None = None,
        opacity: float | None = None,
        border_width: float | None = None,
        rect: Rect | None = None,
    ) -> AnnotationData:
        """Modify an annotation. Returns old state for undo."""
        for annot in self._fitz_page.annots():
            if str(annot.xref) == annot_id:
                old_data = self._annot_to_data(annot)
                if old_data is None:
                    msg = f"Could not read annotation {annot_id}"
                    raise ValueError(msg)
                if stroke_color:
                    annot.set_colors(stroke=stroke_color.to_tuple())
                if fill_color:
                    annot.set_colors(fill=fill_color.to_tuple())
                if opacity is not None:
                    annot.set_opacity(opacity)
                if border_width is not None:
                    annot.set_border(width=border_width)
                if rect is not None:
                    annot.set_rect(fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y1))
                annot.update()
                return old_data
        msg = f"Annotation {annot_id} not found"
        raise ValueError(msg)

    def delete_annotation(self, annot_id: str) -> AnnotationData:
        """Delete an annotation by xref. Returns its data for undo."""
        for annot in self._fitz_page.annots():
            if str(annot.xref) == annot_id:
                data = self._annot_to_data(annot)
                self._fitz_page.delete_annot(annot)
                if data is None:
                    msg = f"Could not read annotation {annot_id}"
                    raise ValueError(msg)
                return data
        msg = f"Annotation {annot_id} not found"
        raise ValueError(msg)

    def get_text_words(self) -> list[tuple[float, ...]]:
        """Return word bounding boxes: (x0, y0, x1, y1, word, block, line, word_no)."""
        result: list[tuple[float, ...]] = self._fitz_page.get_text("words")  # type: ignore[assignment]
        return result

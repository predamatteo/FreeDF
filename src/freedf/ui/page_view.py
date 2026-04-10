"""Custom QGraphicsView for PDF page display."""

from __future__ import annotations

from PIL import Image
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QWidget

from freedf.ui.page_scene import PageScene


class PageView(QGraphicsView):
    """Displays a rendered PDF page with zoom and pan support."""

    zoom_changed = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._scene = PageScene(self)
        self.setScene(self._scene)

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setBackgroundBrush(QColor("#f0f0f0"))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    @property
    def page_scene(self) -> PageScene:
        return self._scene

    def display_image(self, image: Image.Image) -> None:
        """Convert a PIL Image to QPixmap and display it."""
        qimage = self._pil_to_qimage(image)
        pixmap = QPixmap.fromImage(qimage)
        self._scene.set_page_pixmap(pixmap)
        self.setSceneRect(self._scene.itemsBoundingRect())

    def clear_display(self) -> None:
        self._scene.clear_page()

    @staticmethod
    def _pil_to_qimage(pil_image: Image.Image) -> QImage:
        """Convert PIL.Image to QImage (RGB)."""
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        data = pil_image.tobytes("raw", "RGB")
        qimg = QImage(
            data,
            pil_image.width,
            pil_image.height,
            3 * pil_image.width,
            QImage.Format.Format_RGB888,
        )
        return qimg.copy()  # deep copy to detach from Python bytes buffer

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Ctrl+wheel = zoom, plain wheel = scroll."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.25 if delta > 0 else 1 / 1.25
            self.zoom_changed.emit(factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Gesture:
            return True
        return super().event(event)

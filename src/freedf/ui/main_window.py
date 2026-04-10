"""FreeDF main window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QWidget,
)

from freedf.commands.base import CommandStack
from freedf.commands.page_commands import (
    DeletePageCommand,
    DuplicatePageCommand,
    RotatePageCommand,
)
from freedf.core.document import Document
from freedf.core.exceptions import FreedfError
from freedf.io.loader import open_pdf
from freedf.io.saver import save, save_as
from freedf.rendering.cache import RenderCache
from freedf.ui.page_view import PageView
from freedf.ui.thumbnails import ThumbnailPanel
from freedf.ui.toolbar import ToolbarManager


class MainWindow(QMainWindow):
    """FreeDF main application window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("FreeDF")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        self.setAcceptDrops(True)

        self._document: Document | None = None
        self._render_cache: RenderCache | None = None
        self._command_stack = CommandStack()
        self._current_page: int = 0
        self._current_zoom: float = 1.0

        # UI components
        self._thumbnail_panel = ThumbnailPanel()
        self._page_view = PageView()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._thumbnail_panel)
        splitter.addWidget(self._page_view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([200, 1000])
        self.setCentralWidget(splitter)

        # Toolbar
        self._toolbar_mgr = ToolbarManager(self)
        self._connect_actions()

        # Status bar
        self.statusBar().showMessage("Ready")

    def _connect_actions(self) -> None:
        a = self._toolbar_mgr.actions
        a["open"].triggered.connect(lambda: self.open_file())
        a["save"].triggered.connect(self.save_file)
        a["save_as"].triggered.connect(self.save_file_as)
        a["undo"].triggered.connect(self._undo)
        a["redo"].triggered.connect(self._redo)
        a["zoom_in"].triggered.connect(self.zoom_in)
        a["zoom_out"].triggered.connect(self.zoom_out)
        a["fit_width"].triggered.connect(self.fit_width)
        a["fit_page"].triggered.connect(self.fit_page)
        a["rotate_cw"].triggered.connect(lambda: self.rotate_page(90))
        a["rotate_ccw"].triggered.connect(lambda: self.rotate_page(-90))
        a["delete_page"].triggered.connect(self.delete_page)
        a["duplicate_page"].triggered.connect(self.duplicate_page)
        a["prev_page"].triggered.connect(self.prev_page)
        a["next_page"].triggered.connect(self.next_page)
        a["first_page"].triggered.connect(self.first_page)
        a["last_page"].triggered.connect(self.last_page)

        self._thumbnail_panel.page_selected.connect(self.go_to_page)
        self._page_view.zoom_changed.connect(self._on_zoom_factor)

    # --- File operations ---

    def open_file(self, path: str | Path | None = None) -> None:
        if path is None:
            path_str, _ = QFileDialog.getOpenFileName(
                self, "Open PDF", "", "PDF Files (*.pdf);;All Files (*)"
            )
            if not path_str:
                return
            path = Path(path_str)

        try:
            doc = open_pdf(path)
        except FreedfError as exc:
            QMessageBox.warning(self, "Error", str(exc))
            return

        self._close_document()
        self._document = doc
        self._render_cache = RenderCache(doc)
        self._command_stack.clear()
        self._current_page = 0
        self._current_zoom = 1.0
        self._refresh_all()
        self._update_title()

    def save_file(self) -> None:
        if self._document is None:
            return
        if self._document.file_path is None:
            self.save_file_as()
            return
        try:
            save(self._document)
            self.statusBar().showMessage("Saved", 3000)
        except FreedfError as exc:
            QMessageBox.warning(self, "Save Error", str(exc))

    def save_file_as(self) -> None:
        if self._document is None:
            return
        path_str, _ = QFileDialog.getSaveFileName(
            self, "Save PDF As", "", "PDF Files (*.pdf)"
        )
        if not path_str:
            return
        try:
            save_as(self._document, path_str)
            self._update_title()
            self.statusBar().showMessage("Saved", 3000)
        except FreedfError as exc:
            QMessageBox.warning(self, "Save Error", str(exc))

    def _close_document(self) -> None:
        if self._render_cache is not None:
            self._render_cache.dispose()
            self._render_cache = None
        if self._document is not None:
            self._document.close()
            self._document = None
        self._page_view.clear_display()
        self._command_stack.clear()

    # --- Navigation ---

    def go_to_page(self, index: int) -> None:
        if self._document is None:
            return
        index = max(0, min(index, self._document.page_count - 1))
        self._current_page = index
        self._refresh_page()
        self._update_status()
        self._thumbnail_panel.set_current_page(index)

    def prev_page(self) -> None:
        self.go_to_page(self._current_page - 1)

    def next_page(self) -> None:
        self.go_to_page(self._current_page + 1)

    def first_page(self) -> None:
        self.go_to_page(0)

    def last_page(self) -> None:
        if self._document:
            self.go_to_page(self._document.page_count - 1)

    # --- Zoom ---

    def zoom_in(self) -> None:
        self._set_zoom(self._current_zoom * 1.25)

    def zoom_out(self) -> None:
        self._set_zoom(self._current_zoom / 1.25)

    def fit_width(self) -> None:
        if self._document is None:
            return
        page = self._document.get_page(self._current_page)
        view_width = self._page_view.viewport().width()
        self._set_zoom(view_width / page.width)

    def fit_page(self) -> None:
        if self._document is None:
            return
        page = self._document.get_page(self._current_page)
        vp = self._page_view.viewport()
        zoom_w = vp.width() / page.width
        zoom_h = vp.height() / page.height
        self._set_zoom(min(zoom_w, zoom_h))

    def _set_zoom(self, zoom: float) -> None:
        self._current_zoom = max(0.1, min(zoom, 10.0))
        self._refresh_page()
        self._update_status()

    def _on_zoom_factor(self, factor: float) -> None:
        self._set_zoom(self._current_zoom * factor)

    # --- Page operations ---

    def rotate_page(self, degrees: int = 90) -> None:
        if self._document is None:
            return
        page = self._document.get_page(self._current_page)
        new_rotation = (page.rotation + degrees) % 360
        cmd = RotatePageCommand(self._document, self._current_page, new_rotation)
        self._execute_command(cmd)

    def delete_page(self) -> None:
        if self._document is None or self._document.page_count <= 1:
            return
        cmd = DeletePageCommand(self._document, self._current_page)
        self._execute_command(cmd)
        if self._current_page >= self._document.page_count:
            self._current_page = self._document.page_count - 1
        self._refresh_all()

    def duplicate_page(self) -> None:
        if self._document is None:
            return
        cmd = DuplicatePageCommand(self._document, self._current_page)
        self._execute_command(cmd)
        self._refresh_all()

    # --- Undo/Redo ---

    def _undo(self) -> None:
        cmd = self._command_stack.undo()
        if cmd:
            self._on_document_changed()

    def _redo(self) -> None:
        cmd = self._command_stack.redo()
        if cmd:
            self._on_document_changed()

    def _execute_command(self, command: object) -> None:
        try:
            self._command_stack.execute(command)  # type: ignore[arg-type]
        except FreedfError as exc:
            QMessageBox.warning(self, "Error", str(exc))
            return
        self._on_document_changed()

    def _on_document_changed(self) -> None:
        self._refresh_all()
        self._update_action_states()

    # --- Internal refresh ---

    def _refresh_all(self) -> None:
        self._refresh_page()
        self._refresh_thumbnails()
        self._update_status()
        self._update_action_states()

    def _refresh_page(self) -> None:
        if self._document is None or self._render_cache is None:
            return
        if self._current_page >= self._document.page_count:
            self._current_page = max(0, self._document.page_count - 1)
        image = self._render_cache.get_page_image(
            self._current_page, self._current_zoom
        )
        self._page_view.display_image(image)

    def _refresh_thumbnails(self) -> None:
        if self._document is None or self._render_cache is None:
            return
        self._thumbnail_panel.populate(self._render_cache, self._document.page_count)
        self._thumbnail_panel.set_current_page(self._current_page)

    def _update_title(self) -> None:
        if self._document and self._document.file_path:
            self.setWindowTitle(f"FreeDF \u2014 {self._document.file_path.name}")
        else:
            self.setWindowTitle("FreeDF")

    def _update_status(self) -> None:
        if self._document:
            self.statusBar().showMessage(
                f"Page {self._current_page + 1} / {self._document.page_count}"
                f"    Zoom: {int(self._current_zoom * 100)}%"
            )
        else:
            self.statusBar().showMessage("Ready")

    def _update_action_states(self) -> None:
        a = self._toolbar_mgr.actions
        has_doc = self._document is not None
        a["save"].setEnabled(has_doc)
        a["save_as"].setEnabled(has_doc)
        a["undo"].setEnabled(self._command_stack.can_undo)
        a["redo"].setEnabled(self._command_stack.can_redo)
        a["zoom_in"].setEnabled(has_doc)
        a["zoom_out"].setEnabled(has_doc)
        a["fit_width"].setEnabled(has_doc)
        a["fit_page"].setEnabled(has_doc)
        a["rotate_cw"].setEnabled(has_doc)
        a["rotate_ccw"].setEnabled(has_doc)
        a["delete_page"].setEnabled(
            has_doc and self._document is not None and self._document.page_count > 1
        )
        a["duplicate_page"].setEnabled(has_doc)
        a["prev_page"].setEnabled(has_doc and self._current_page > 0)
        a["next_page"].setEnabled(
            has_doc
            and self._document is not None
            and self._current_page < self._document.page_count - 1
        )
        a["first_page"].setEnabled(has_doc and self._current_page > 0)
        a["last_page"].setEnabled(
            has_doc
            and self._document is not None
            and self._current_page < self._document.page_count - 1
        )

    # --- Drag and drop ---

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self.open_file(path)
                break

    def closeEvent(self, event: object) -> None:  # noqa: N802
        self._close_document()
        super().closeEvent(event)  # type: ignore[arg-type]

"""FreeDF main window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QSplitter,
    QWidget,
)

from freedf.commands.base import CommandStack
from freedf.commands.page_commands import (
    DeletePageCommand,
    DuplicatePageCommand,
    ReorderPageCommand,
    RotatePageCommand,
)
from freedf.core.document import Document
from freedf.core.exceptions import FreedfError
from freedf.core.recent_files import RecentFilesManager
from freedf.io.loader import open_pdf
from freedf.io.saver import save, save_as
from freedf.rendering.cache import RenderCache
from freedf.ui.annotation_panel import AnnotationPanel
from freedf.ui.page_view import PageView
from freedf.ui.panels.form_panel import FormPanel
from freedf.ui.thumbnails import ThumbnailPanel
from freedf.ui.toolbar import ToolbarManager
from freedf.ui.tools.freetext_tool import FreeTextTool
from freedf.ui.tools.highlight_tool import HighlightTool
from freedf.ui.tools.ink_tool import InkTool
from freedf.ui.tools.select_tool import SelectTool
from freedf.ui.tools.shape_tool import EllipseTool, LineTool, RectTool
from freedf.ui.tools.text_selector import TextSelectorTool
from freedf.ui.tools.tool_manager import ToolManager


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
        self._recent_files = RecentFilesManager()

        # UI components
        self._thumbnail_panel = ThumbnailPanel()
        self._page_view = PageView()
        self._annotation_panel = AnnotationPanel()
        self._form_panel = FormPanel(execute_command=self._execute_command)
        self._form_panel.hide()  # shown only when form fields exist

        # Right sidebar: stack annotation + form panels
        right_sidebar = QSplitter(Qt.Orientation.Vertical)
        right_sidebar.addWidget(self._annotation_panel)
        right_sidebar.addWidget(self._form_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._thumbnail_panel)
        splitter.addWidget(self._page_view)
        splitter.addWidget(right_sidebar)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([200, 800, 220])
        self.setCentralWidget(splitter)

        # Menu bar
        self._setup_menu_bar()

        # Toolbar
        self._toolbar_mgr = ToolbarManager(self)

        # Tool system
        self._setup_tools()

        self._connect_actions()

        # Status bar
        self.statusBar().showMessage("Ready")

    def _setup_menu_bar(self) -> None:
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("&Open...", self.open_file, "Ctrl+O")
        file_menu.addAction("&Save", self.save_file, "Ctrl+S")
        file_menu.addAction("Save &As...", self.save_file_as, "Ctrl+Shift+S")
        file_menu.addSeparator()
        self._recent_menu = QMenu("Recent Files", self)
        file_menu.addMenu(self._recent_menu)
        self._update_recent_menu()
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close, "Ctrl+Q")

    def _update_recent_menu(self) -> None:
        self._recent_menu.clear()
        recent = self._recent_files.get_list()
        if not recent:
            action = self._recent_menu.addAction("(empty)")
            action.setEnabled(False)
            return
        for path in recent:
            action = self._recent_menu.addAction(path.name)
            action.setToolTip(str(path))
            action.triggered.connect(lambda checked, p=path: self.open_file(p))
        self._recent_menu.addSeparator()
        self._recent_menu.addAction("Clear Recent", self._recent_files.clear)

    def _setup_tools(self) -> None:
        self._tool_manager = ToolManager()
        self._page_view.page_scene.set_tool_manager(self._tool_manager)

        common = {
            "get_document": lambda: self._document,
            "get_page_number": lambda: self._current_page,
            "get_scene": lambda: self._page_view.page_scene,
            "get_zoom": lambda: self._current_zoom,
            "tool_manager": self._tool_manager,
            "execute_command": self._execute_command,
        }

        self._tool_manager.register(
            SelectTool(
                get_document=lambda: self._document,
                get_page_number=lambda: self._current_page,
                get_scene=lambda: self._page_view.page_scene,
                get_zoom=lambda: self._current_zoom,
                execute_command=self._execute_command,
            )
        )
        self._tool_manager.register(HighlightTool(**common))  # type: ignore[arg-type]
        self._tool_manager.register(
            FreeTextTool(
                get_document=lambda: self._document,
                get_page_number=lambda: self._current_page,
                get_parent_widget=lambda: self,
                tool_manager=self._tool_manager,
                execute_command=self._execute_command,
            )
        )
        self._tool_manager.register(InkTool(**common))  # type: ignore[arg-type]
        self._tool_manager.register(RectTool(**common))  # type: ignore[arg-type]
        self._tool_manager.register(EllipseTool(**common))  # type: ignore[arg-type]
        self._tool_manager.register(LineTool(**common))  # type: ignore[arg-type]
        self._tool_manager.register(LineTool(arrow=True, **common))  # type: ignore[arg-type]
        self._tool_manager.register(
            TextSelectorTool(
                get_document=lambda: self._document,
                get_page_number=lambda: self._current_page,
                get_scene=lambda: self._page_view.page_scene,
                get_zoom=lambda: self._current_zoom,
            )
        )
        self._tool_manager.set_tool("select")

    def _on_tool_changed(self, tool_name: str) -> None:
        from PySide6.QtWidgets import QGraphicsView

        self._tool_manager.set_tool(tool_name)
        if tool_name == "select":
            self._page_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            self._page_view.setDragMode(QGraphicsView.DragMode.NoDrag)

    def _on_color_changed(self, color: object) -> None:
        from freedf.core.annotations import Color

        if isinstance(color, Color):
            self._tool_manager.current_color = color

    def _on_thickness_changed(self, thickness: float) -> None:
        self._tool_manager.current_thickness = thickness

    def _delete_annotation_by_id(self, annot_id: str) -> None:
        from freedf.commands.annotation_commands import DeleteAnnotationCommand

        if self._document is None:
            return
        cmd = DeleteAnnotationCommand(
            document=self._document,
            page_number=self._current_page,
            annot_id=annot_id,
        )
        self._execute_command(cmd)

    # --- Multi-file operations ---

    def _show_merge_dialog(self) -> None:
        from freedf.ui.dialogs.merge_dialog import MergeDialog

        dlg = MergeDialog(self)
        dlg.exec()

    def _show_split_dialog(self) -> None:
        from freedf.ui.dialogs.split_dialog import SplitDialog

        if self._document is None or self._document.file_path is None:
            return
        dlg = SplitDialog(self._document.file_path, self._document.page_count, self)
        dlg.exec()

    def _show_extract_dialog(self) -> None:
        from freedf.ui.dialogs.extract_dialog import ExtractDialog

        if self._document is None or self._document.file_path is None:
            return
        dlg = ExtractDialog(self._document.file_path, self._document.page_count, self)
        dlg.exec()

    def _show_insert_dialog(self) -> None:
        from freedf.commands.multifile_commands import InsertPagesCommand
        from freedf.ui.dialogs.insert_dialog import InsertDialog

        if self._document is None:
            return
        dlg = InsertDialog(self._document.page_count, self)
        if dlg.exec() and dlg.result_bytes:
            cmd = InsertPagesCommand(
                document=self._document,
                source_pdf_bytes=dlg.result_bytes,
                source_page_numbers=dlg.result_pages,
                insert_at=dlg.result_insert_at,
            )
            self._execute_command(cmd)
            self._refresh_all()

    def _show_image_dialog(self) -> None:
        from freedf.commands.form_commands import InsertImageCommand
        from freedf.ui.dialogs.image_dialog import ImageDialog

        if self._document is None:
            return
        dlg = ImageDialog(parent=self)
        if dlg.exec() and dlg.result_rect:
            cmd = InsertImageCommand(
                document=self._document,
                page_number=self._current_page,
                image_path=dlg.result_path,
                target_rect=dlg.result_rect,
            )
            self._execute_command(cmd)

    def _flatten_annotations(self) -> None:
        from freedf.commands.form_commands import FlattenAnnotationsCommand

        if self._document is None:
            return
        reply = QMessageBox.question(
            self,
            "Flatten Annotations",
            f"Flatten all annotations on page {self._current_page + 1}?\n"
            "This bakes them into the page content (undoable).",
        )
        if reply == QMessageBox.StandardButton.Yes:
            cmd = FlattenAnnotationsCommand(
                document=self._document,
                page_number=self._current_page,
            )
            self._execute_command(cmd)

    def _show_ocr_dialog(self) -> None:
        from freedf.ui.dialogs.ocr_dialog import OCRDialog

        if self._document is None:
            return
        dlg = OCRDialog(self._document, self._current_page, self)
        if dlg.exec() and dlg.result_pages:
            if len(dlg.result_pages) == 1:
                from freedf.commands.ocr_commands import OCRPageCommand

                ocr_cmd: object = OCRPageCommand(
                    document=self._document,
                    page_number=dlg.result_pages[0],
                    language=dlg.result_language,
                    dpi=dlg.result_dpi,
                )
            else:
                from freedf.commands.ocr_commands import OCRDocumentCommand

                ocr_cmd = OCRDocumentCommand(
                    document=self._document,
                    page_numbers=dlg.result_pages,
                    language=dlg.result_language,
                    dpi=dlg.result_dpi,
                )
            self._execute_command(ocr_cmd)

    def _show_export_text_dialog(self) -> None:
        from freedf.ui.dialogs.export_text_dialog import ExportTextDialog

        if self._document is None:
            return
        dlg = ExportTextDialog(self._document, self._current_page, self)
        dlg.exec()

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

        # Tool switching
        for key, tool_name in [
            ("tool_select", "select"),
            ("tool_highlight", "highlight"),
            ("tool_freetext", "freetext"),
            ("tool_ink", "ink"),
            ("tool_rect", "rect"),
            ("tool_ellipse", "ellipse"),
            ("tool_line", "line"),
            ("tool_arrow", "arrow"),
            ("tool_text_select", "text_select"),
        ]:
            a[key].triggered.connect(
                lambda _checked=False, n=tool_name: self._on_tool_changed(n)
            )

        # Color and thickness
        if self._toolbar_mgr.color_picker:
            self._toolbar_mgr.color_picker.color_changed.connect(self._on_color_changed)
        if self._toolbar_mgr.thickness_picker:
            self._toolbar_mgr.thickness_picker.thickness_changed.connect(
                self._on_thickness_changed
            )

        # Annotation panel
        self._annotation_panel.annotation_delete_requested.connect(
            self._delete_annotation_by_id
        )

        # Multi-file operations
        a["merge"].triggered.connect(self._show_merge_dialog)
        a["split"].triggered.connect(self._show_split_dialog)
        a["extract"].triggered.connect(self._show_extract_dialog)
        a["insert_pages"].triggered.connect(self._show_insert_dialog)
        a["insert_image"].triggered.connect(self._show_image_dialog)
        a["flatten"].triggered.connect(self._flatten_annotations)
        a["ocr"].triggered.connect(self._show_ocr_dialog)
        a["export_text"].triggered.connect(self._show_export_text_dialog)

        self._thumbnail_panel.page_selected.connect(self.go_to_page)
        self._thumbnail_panel.page_reordered.connect(self._reorder_page)
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
        self._refresh_form_panel()
        self._update_title()
        self._recent_files.add(path)
        self._update_recent_menu()

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

    def _reorder_page(self, from_index: int, to_index: int) -> None:
        if self._document is None or from_index == to_index:
            return
        cmd = ReorderPageCommand(self._document, from_index, to_index)
        self._execute_command(cmd)
        self._current_page = to_index
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
        self._refresh_annotations()
        self._update_status()
        self._update_action_states()

    def _refresh_annotations(self) -> None:
        self._annotation_panel.refresh(self._document, self._current_page)

    def _refresh_form_panel(self) -> None:
        self._form_panel.refresh(self._document)
        if self._document is not None:
            from freedf.core.forms import detect_form_fields

            fields = detect_form_fields(self._document)
            if fields:
                self._form_panel.show()
            else:
                self._form_panel.hide()
        else:
            self._form_panel.hide()

    def _refresh_page(self) -> None:
        if self._document is None or self._render_cache is None:
            return
        if self._current_page >= self._document.page_count:
            self._current_page = max(0, self._document.page_count - 1)
        self._page_view.page_scene.set_zoom(self._current_zoom)
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

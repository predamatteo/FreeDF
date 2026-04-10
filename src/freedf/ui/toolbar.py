"""Toolbar and action management."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import QMainWindow, QToolBar

from freedf.ui.widgets.color_picker import ColorPickerButton
from freedf.ui.widgets.thickness_picker import ThicknessPicker


class ToolbarManager:
    """Creates and manages the toolbars and actions.

    Two toolbars:
    - Main: file, undo/redo, zoom, page ops, navigation
    - Tools: annotation tools, color/thickness, editing actions
    """

    def __init__(self, main_window: QMainWindow) -> None:
        self._window = main_window
        self.actions: dict[str, QAction] = {}
        self._tool_group: QActionGroup | None = None
        self.color_picker: ColorPickerButton | None = None
        self.thickness_picker: ThicknessPicker | None = None

        # --- Toolbar 1: Main actions ---
        self._main_tb = QToolBar("Main", main_window)
        self._main_tb.setMovable(False)
        self._main_tb.setIconSize(QSize(18, 18))
        self._main_tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        main_window.addToolBar(self._main_tb)

        # --- Toolbar 2: Tools ---
        self._tools_tb = QToolBar("Tools", main_window)
        self._tools_tb.setMovable(False)
        self._tools_tb.setIconSize(QSize(18, 18))
        self._tools_tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        main_window.addToolBarBreak()
        main_window.addToolBar(self._tools_tb)

        self._build()

    def _build(self) -> None:
        tb = self._main_tb

        # File
        self._add("open", "Open", "Ctrl+O", tb)
        self._add("save", "Save", "Ctrl+S", tb)
        self._add("save_as", "Save As", "Ctrl+Shift+S", tb)
        tb.addSeparator()
        self._add("undo", "Undo", "Ctrl+Z", tb)
        self._add("redo", "Redo", "Ctrl+Shift+Z", tb)
        tb.addSeparator()

        # Zoom
        self._add("zoom_in", "+", "Ctrl+=", tb)
        self._add("zoom_out", "-", "Ctrl+-", tb)
        self._add("fit_width", "FitW", "Ctrl+1", tb)
        self._add("fit_page", "FitP", "Ctrl+0", tb)
        tb.addSeparator()

        # Page ops
        self._add("rotate_cw", "RotR", "Ctrl+R", tb)
        self._add("rotate_ccw", "RotL", "Ctrl+Shift+R", tb)
        self._add("delete_page", "Del", None, tb)
        self._add("duplicate_page", "Dup", None, tb)
        tb.addSeparator()

        # Navigation
        self._add("prev_page", "Prev", "PgUp", tb)
        self._add("next_page", "Next", "PgDown", tb)
        self._add("first_page", "First", "Home", tb)
        self._add("last_page", "Last", "End", tb)

        # --- Tools toolbar ---
        tt = self._tools_tb

        # Tool selection (mutually exclusive)
        self._tool_group = QActionGroup(self._window)
        self._tool_group.setExclusive(True)
        self._add_tool("tool_select", "Select", "Escape", checked=True)
        self._add_tool("tool_highlight", "Highlight", "H")
        self._add_tool("tool_freetext", "Note", "T")
        self._add_tool("tool_ink", "Ink", "I")
        self._add_tool("tool_rect", "Rect", None)
        self._add_tool("tool_ellipse", "Ellipse", None)
        self._add_tool("tool_line", "Line", None)
        self._add_tool("tool_arrow", "Arrow", None)
        self._add_tool("tool_text_select", "SelTxt", None)
        self._add_tool("tool_stamp", "Stamp", None)
        self._add_tool("tool_redact", "Redact", "R")
        tt.addSeparator()

        # Color and thickness
        self.color_picker = ColorPickerButton()
        tt.addWidget(self.color_picker)
        self.thickness_picker = ThicknessPicker()
        self.thickness_picker.setMaximumWidth(75)
        tt.addWidget(self.thickness_picker)
        tt.addSeparator()

        # Editing actions
        self._add("find_replace", "Find", "Ctrl+H", tt)
        self._add("insert_text", "AddTxt", None, tt)
        self._add("watermark", "Wmark", None, tt)
        tt.addSeparator()

        # Multi-file & advanced
        self._add("merge", "Merge", None, tt)
        self._add("split", "Split", None, tt)
        self._add("extract", "Extract", None, tt)
        self._add("insert_pages", "InsertPg", None, tt)
        tt.addSeparator()
        self._add("insert_image", "Image", None, tt)
        self._add("flatten", "Flatten", None, tt)
        self._add("ocr", "OCR", None, tt)
        self._add("export_text", "ExpTxt", None, tt)

    def _add(
        self,
        key: str,
        text: str,
        shortcut: str | None,
        toolbar: QToolBar,
    ) -> None:
        action = QAction(text, self._window)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        self.actions[key] = action
        toolbar.addAction(action)

    def _add_tool(
        self,
        key: str,
        text: str,
        shortcut: str | None = None,
        *,
        checked: bool = False,
    ) -> None:
        action = QAction(text, self._window)
        action.setCheckable(True)
        action.setChecked(checked)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if self._tool_group:
            self._tool_group.addAction(action)
        self.actions[key] = action
        self._tools_tb.addAction(action)

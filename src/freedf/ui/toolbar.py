"""Toolbar and action management."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import QMainWindow, QToolBar

from freedf.ui.widgets.color_picker import ColorPickerButton
from freedf.ui.widgets.thickness_picker import ThicknessPicker


class ToolbarManager:
    """Creates and manages the main toolbar and actions."""

    def __init__(self, main_window: QMainWindow) -> None:
        self._window = main_window
        self._toolbar = QToolBar("Main", main_window)
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(QSize(20, 20))
        self._toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        main_window.addToolBar(self._toolbar)

        self.actions: dict[str, QAction] = {}
        self._tool_group: QActionGroup | None = None
        self.color_picker: ColorPickerButton | None = None
        self.thickness_picker: ThicknessPicker | None = None
        self._build()

    def _build(self) -> None:
        self._add("open", "Open", "Ctrl+O")
        self._add("save", "Save", "Ctrl+S")
        self._add("save_as", "Save As", "Ctrl+Shift+S")
        self._toolbar.addSeparator()
        self._add("undo", "Undo", "Ctrl+Z")
        self._add("redo", "Redo", "Ctrl+Shift+Z")
        self._toolbar.addSeparator()
        self._add("zoom_in", "Zoom +", "Ctrl+=")
        self._add("zoom_out", "Zoom -", "Ctrl+-")
        self._add("fit_width", "Fit W", "Ctrl+1")
        self._add("fit_page", "Fit P", "Ctrl+0")
        self._toolbar.addSeparator()
        self._add("rotate_cw", "Rotate R", "Ctrl+R")
        self._add("rotate_ccw", "Rotate L", "Ctrl+Shift+R")
        self._add("delete_page", "Del Page", None)
        self._add("duplicate_page", "Dup Page", None)
        self._toolbar.addSeparator()
        self._add("prev_page", "Prev", "PgUp")
        self._add("next_page", "Next", "PgDown")
        self._add("first_page", "First", "Home")
        self._add("last_page", "Last", "End")
        self._toolbar.addSeparator()
        self._add("merge", "Merge", None)
        self._add("split", "Split", None)
        self._add("extract", "Extract", None)
        self._add("insert_pages", "Insert", None)
        self._toolbar.addSeparator()
        self._add("insert_image", "Image", None)
        self._add("flatten", "Flatten", None)
        self._toolbar.addSeparator()
        self._add("ocr", "OCR", None)
        self._add("export_text", "Text", None)

        # Tool selection (mutually exclusive)
        self._toolbar.addSeparator()
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
        self._add_tool("tool_text_select", "Sel Text", None)

        # Color and thickness pickers
        self._toolbar.addSeparator()
        self.color_picker = ColorPickerButton()
        self._toolbar.addWidget(self.color_picker)
        self.thickness_picker = ThicknessPicker()
        self.thickness_picker.setMaximumWidth(80)
        self._toolbar.addWidget(self.thickness_picker)

    def _add(self, key: str, text: str, shortcut: str | None = None) -> None:
        action = QAction(text, self._window)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        self.actions[key] = action
        self._toolbar.addAction(action)

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
        self._toolbar.addAction(action)

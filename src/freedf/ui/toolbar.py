"""Toolbar and action management."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QToolBar


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

    def _add(self, key: str, text: str, shortcut: str | None = None) -> None:
        action = QAction(text, self._window)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        self.actions[key] = action
        self._toolbar.addAction(action)

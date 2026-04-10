"""FreeDF application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from freedf.ui.main_window import MainWindow

STYLESHEET = """
/* Global */
QMainWindow {
    background-color: #fafafa;
    color: #212121;
    font-size: 13px;
}

/* Toolbar */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    padding: 4px 8px;
    spacing: 6px;
}

QToolBar::separator {
    width: 1px;
    background-color: #e0e0e0;
    margin: 4px 6px;
}

QToolButton {
    background: transparent;
    border: none;
    border-radius: 2px;
    padding: 6px 10px;
    color: #424242;
    font-size: 12px;
}

QToolButton:hover {
    background-color: #f0f0f0;
}

QToolButton:pressed {
    background-color: #e0e0e0;
}

QToolButton:disabled {
    color: #bdbdbd;
}

/* Status bar */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e0e0e0;
    color: #757575;
    font-size: 12px;
    padding: 2px 8px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* Thumbnail sidebar */
QListWidget {
    background-color: #fafafa;
    border: none;
    border-right: 1px solid #e0e0e0;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border: 2px solid transparent;
    border-radius: 2px;
}

QListWidget::item:selected {
    border: 2px solid #2e7d32;
    background-color: #e8f5e9;
}

QListWidget::item:hover:!selected {
    background-color: #f5f5f5;
}

/* Graphics view */
QGraphicsView {
    background-color: #f0f0f0;
    border: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #e0e0e0;
    width: 1px;
}

/* Tooltips */
QToolTip {
    background-color: #424242;
    color: #ffffff;
    border: none;
    padding: 4px 8px;
    font-size: 12px;
}
"""

DARK_STYLESHEET = """
/* Global */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-size: 13px;
}

/* Toolbar */
QToolBar {
    background-color: #252525;
    border-bottom: 1px solid #333333;
    padding: 4px 8px;
    spacing: 6px;
}

QToolBar::separator {
    width: 1px;
    background-color: #333333;
    margin: 4px 6px;
}

QToolButton {
    background: transparent;
    border: none;
    border-radius: 2px;
    padding: 6px 10px;
    color: #cccccc;
    font-size: 12px;
}

QToolButton:hover {
    background-color: #333333;
}

QToolButton:pressed {
    background-color: #404040;
}

QToolButton:disabled {
    color: #555555;
}

/* Status bar */
QStatusBar {
    background-color: #252525;
    border-top: 1px solid #333333;
    color: #999999;
    font-size: 12px;
    padding: 2px 8px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #777777;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #777777;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* Thumbnail sidebar */
QListWidget {
    background-color: #1e1e1e;
    border: none;
    border-right: 1px solid #333333;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border: 2px solid transparent;
    border-radius: 2px;
}

QListWidget::item:selected {
    border: 2px solid #4caf50;
    background-color: #1b3a1b;
}

QListWidget::item:hover:!selected {
    background-color: #2a2a2a;
}

/* Graphics view */
QGraphicsView {
    background-color: #2a2a2a;
    border: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #333333;
    width: 1px;
}

/* Menu bar */
QMenuBar {
    background-color: #252525;
    color: #e0e0e0;
    border-bottom: 1px solid #333333;
}

QMenuBar::item:selected {
    background-color: #333333;
}

QMenu {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #333333;
}

QMenu::item:selected {
    background-color: #4caf50;
    color: #ffffff;
}

/* Dialogs and inputs */
QDialog {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QLineEdit, QSpinBox, QComboBox, QPlainTextEdit {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #333333;
    padding: 4px;
    border-radius: 2px;
}

QLabel {
    color: #e0e0e0;
}

QPushButton {
    background-color: #333333;
    color: #e0e0e0;
    border: 1px solid #444444;
    padding: 6px 16px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #444444;
}

QCheckBox, QRadioButton {
    color: #e0e0e0;
}

/* Tooltips */
QToolTip {
    background-color: #333333;
    color: #ffffff;
    border: none;
    padding: 4px 8px;
    font-size: 12px;
}
"""

STYLESHEETS = {"light": STYLESHEET, "dark": DARK_STYLESHEET}


def main() -> None:
    """Launch the FreeDF application."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("FreeDF")
    app.setOrganizationName("FreeDF")
    app.setApplicationVersion("0.5.0")

    # Load saved preferences
    from PySide6.QtCore import QSettings

    settings = QSettings("FreeDF", "FreeDF")
    theme = str(settings.value("theme", "light"))
    app.setStyleSheet(STYLESHEETS.get(theme, STYLESHEET))

    # Load translation
    from PySide6.QtCore import QTranslator

    translator = QTranslator()
    lang = str(settings.value("language", "en"))
    if lang != "en":
        from freedf.i18n import I18N_DIR

        ts_path = I18N_DIR / f"freedf_{lang}.qm"
        if ts_path.exists() and translator.load(str(ts_path)):
            app.installTranslator(translator)

    window = MainWindow()
    window.show()

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if file_path.exists() and file_path.suffix.lower() == ".pdf":
            window.open_file(file_path)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

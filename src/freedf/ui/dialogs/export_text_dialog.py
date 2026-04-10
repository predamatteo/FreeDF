"""Export text dialog."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from freedf.core.text_export import export_text_to_file, extract_text_from_document

if TYPE_CHECKING:
    from freedf.core.document import Document


class ExportTextDialog(QDialog):
    """Dialog for previewing and exporting extracted text."""

    def __init__(
        self,
        document: Document,
        current_page: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Text")
        self.setMinimumSize(500, 500)
        self._document = document
        self._current_page = current_page

        # Scope
        self._current_radio = QRadioButton(f"Current page ({current_page + 1})")
        self._current_radio.setChecked(True)
        self._all_radio = QRadioButton("All pages")
        self._range_radio = QRadioButton("Page range:")
        self._from_spin = QSpinBox()
        self._from_spin.setRange(1, document.page_count)
        self._from_spin.setValue(1)
        self._to_spin = QSpinBox()
        self._to_spin.setRange(1, document.page_count)
        self._to_spin.setValue(document.page_count)

        # Preview
        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)

        # Refresh preview on scope change
        self._current_radio.toggled.connect(self._refresh_preview)
        self._all_radio.toggled.connect(self._refresh_preview)
        self._range_radio.toggled.connect(self._refresh_preview)
        self._from_spin.valueChanged.connect(self._refresh_preview)
        self._to_spin.valueChanged.connect(self._refresh_preview)
        self._refresh_preview()

        # Buttons
        copy_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        copy_btn.rejected.connect(self.reject)

        export_btn = copy_btn.addButton(
            "Export to File...", QDialogButtonBox.ButtonRole.ActionRole
        )
        export_btn.clicked.connect(self._export_file)

        clipboard_btn = copy_btn.addButton(
            "Copy to Clipboard", QDialogButtonBox.ButtonRole.ActionRole
        )
        clipboard_btn.clicked.connect(self._copy_clipboard)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Scope:"))
        layout.addWidget(self._current_radio)
        layout.addWidget(self._all_radio)
        layout.addWidget(self._range_radio)
        layout.addWidget(self._from_spin)
        layout.addWidget(self._to_spin)
        layout.addWidget(QLabel("Preview:"))
        layout.addWidget(self._preview)
        layout.addWidget(copy_btn)

    def _get_page_numbers(self) -> list[int] | None:
        if self._current_radio.isChecked():
            return [self._current_page]
        if self._all_radio.isChecked():
            return None  # all pages
        start = self._from_spin.value() - 1
        end = self._to_spin.value() - 1
        return list(range(start, end + 1))

    def _refresh_preview(self) -> None:
        pages = self._get_page_numbers()
        text = extract_text_from_document(self._document, pages)
        self._preview.setPlainText(text)

    def _export_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Text", "", "Text Files (*.txt)"
        )
        if not path:
            return
        try:
            pages = self._get_page_numbers()
            export_text_to_file(self._document, Path(path), pages)
            QMessageBox.information(self, "Done", "Text exported successfully.")
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

    def _copy_clipboard(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(self._preview.toPlainText())
            QMessageBox.information(self, "Done", "Text copied to clipboard.")

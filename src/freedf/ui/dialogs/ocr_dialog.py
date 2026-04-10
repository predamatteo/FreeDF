"""OCR dialog — configure and run OCR on pages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from freedf.core.ocr import (
    get_available_languages,
    is_tesseract_available,
    page_has_text,
)

if TYPE_CHECKING:
    from freedf.core.document import Document


class OCRDialog(QDialog):
    """Dialog for configuring and running OCR."""

    def __init__(
        self,
        document: Document,
        current_page: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("OCR - Text Recognition")
        self.setMinimumWidth(400)
        self._document = document
        self._current_page = current_page
        self.result_pages: list[int] = []
        self.result_language: str = "eng"
        self.result_dpi: int = 300

        if not is_tesseract_available():
            layout = QVBoxLayout(self)
            layout.addWidget(
                QLabel(
                    "Tesseract OCR is not installed.\n\n"
                    "Install Tesseract to enable OCR:\n"
                    "https://github.com/tesseract-ocr/tesseract"
                )
            )
            close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            close_btn.rejected.connect(self.reject)
            layout.addWidget(close_btn)
            return

        # Language selector
        self._lang_combo = QComboBox()
        langs = get_available_languages()
        if not langs:
            langs = ["eng"]
        self._lang_combo.addItems(langs)

        # DPI selector
        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(72, 600)
        self._dpi_spin.setValue(300)
        self._dpi_spin.setSingleStep(50)

        # Scope
        self._current_radio = QRadioButton(f"Current page ({current_page + 1})")
        self._current_radio.setChecked(True)
        self._no_text_radio = QRadioButton("All pages without text")
        self._all_radio = QRadioButton("All pages")

        # Count pages without text
        no_text_count = sum(
            1 for i in range(document.page_count) if not page_has_text(document, i)
        )
        self._no_text_radio.setText(f"All pages without text ({no_text_count} pages)")

        # Progress
        self._progress = QProgressBar()
        self._progress.setVisible(False)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._confirm)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Language:"))
        layout.addWidget(self._lang_combo)
        layout.addWidget(QLabel("DPI (higher = better quality, slower):"))
        layout.addWidget(self._dpi_spin)
        layout.addWidget(QLabel("Scope:"))
        layout.addWidget(self._current_radio)
        layout.addWidget(self._no_text_radio)
        layout.addWidget(self._all_radio)
        layout.addWidget(self._progress)
        layout.addWidget(buttons)

    def _confirm(self) -> None:
        self.result_language = self._lang_combo.currentText()
        self.result_dpi = self._dpi_spin.value()

        if self._current_radio.isChecked():
            self.result_pages = [self._current_page]
        elif self._no_text_radio.isChecked():
            self.result_pages = [
                i
                for i in range(self._document.page_count)
                if not page_has_text(self._document, i)
            ]
        else:
            self.result_pages = list(range(self._document.page_count))

        if not self.result_pages:
            QMessageBox.information(
                self, "OCR", "No pages need OCR (all pages already have text)."
            )
            self.reject()
            return

        self.accept()

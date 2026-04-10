"""Split PDF dialog."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from freedf.core.multifile import split_pdf_by_ranges, split_pdf_single_pages


class SplitDialog(QDialog):
    """Dialog for splitting a PDF into multiple files."""

    def __init__(
        self, source_path: Path, page_count: int, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Split PDF")
        self.setMinimumWidth(400)
        self._source = source_path
        self._page_count = page_count

        self._single_radio = QRadioButton("One file per page")
        self._single_radio.setChecked(True)
        self._range_radio = QRadioButton("Split by range")

        self._from_spin = QSpinBox()
        self._from_spin.setRange(1, page_count)
        self._from_spin.setValue(1)
        self._to_spin = QSpinBox()
        self._to_spin.setRange(1, page_count)
        self._to_spin.setValue(page_count)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._split)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Source: {source_path.name} ({page_count} pages)"))
        layout.addWidget(self._single_radio)
        layout.addWidget(self._range_radio)
        layout.addWidget(QLabel("From page:"))
        layout.addWidget(self._from_spin)
        layout.addWidget(QLabel("To page:"))
        layout.addWidget(self._to_spin)
        layout.addWidget(buttons)

    def _split(self) -> None:
        output_dir = QFileDialog.getExistingDirectory(self, "Output Directory")
        if not output_dir:
            return

        try:
            if self._single_radio.isChecked():
                results = split_pdf_single_pages(self._source, Path(output_dir))
            else:
                start = self._from_spin.value() - 1
                end = self._to_spin.value() - 1
                results = split_pdf_by_ranges(
                    self._source, [(start, end)], Path(output_dir)
                )
            QMessageBox.information(self, "Done", f"Created {len(results)} file(s).")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

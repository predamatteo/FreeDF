"""Extract pages dialog."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from freedf.core.multifile import extract_pages


class ExtractDialog(QDialog):
    """Dialog for extracting selected pages to a new PDF."""

    def __init__(
        self, source_path: Path, page_count: int, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Extract Pages")
        self.setMinimumSize(350, 400)
        self._source = source_path
        self._page_count = page_count

        self._checkboxes: list[QCheckBox] = []

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        for i in range(page_count):
            cb = QCheckBox(f"Page {i + 1}")
            cb.setChecked(True)
            self._checkboxes.append(cb)
            scroll_layout.addWidget(cb)
        scroll_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._extract)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Select pages from {source_path.name}:"))
        layout.addWidget(scroll)
        layout.addWidget(buttons)

    def _extract(self) -> None:
        selected = [i for i, cb in enumerate(self._checkboxes) if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Error", "Select at least one page.")
            return

        output, _ = QFileDialog.getSaveFileName(
            self, "Save Extracted PDF", "", "PDF Files (*.pdf)"
        )
        if not output:
            return

        try:
            extract_pages(self._source, selected, Path(output))
            QMessageBox.information(self, "Done", f"Extracted {len(selected)} pages.")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

"""Insert pages from another PDF dialog."""

from __future__ import annotations

from pathlib import Path

import fitz
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class InsertDialog(QDialog):
    """Dialog for selecting pages from another PDF to insert."""

    def __init__(self, target_page_count: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Insert Pages")
        self.setMinimumSize(400, 450)
        self._target_page_count = target_page_count

        self._source_path: Path | None = None
        self._source_page_count = 0
        self._checkboxes: list[QCheckBox] = []
        self.result_bytes: bytes = b""
        self.result_pages: list[int] = []
        self.result_insert_at: int = 0

        self._source_label = QLabel("No file selected")
        pick_btn = __import__(
            "PySide6.QtWidgets", fromlist=["QPushButton"]
        ).QPushButton("Choose PDF...")
        pick_btn.clicked.connect(self._pick_source)

        self._scroll_widget = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_widget)
        self._scroll_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self._scroll_widget)
        scroll.setWidgetResizable(True)

        self._insert_spin = QSpinBox()
        self._insert_spin.setRange(1, target_page_count + 1)
        self._insert_spin.setValue(target_page_count + 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._confirm)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._source_label)
        layout.addWidget(pick_btn)
        layout.addWidget(QLabel("Pages to insert:"))
        layout.addWidget(scroll)
        layout.addWidget(QLabel("Insert at position:"))
        layout.addWidget(self._insert_spin)
        layout.addWidget(buttons)

    def _pick_source(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)"
        )
        if not path:
            return
        self._source_path = Path(path)
        doc = fitz.open(path)
        self._source_page_count = doc.page_count
        doc.close()

        self._source_label.setText(
            f"{self._source_path.name} ({self._source_page_count} pages)"
        )

        # Clear and rebuild checkboxes
        for cb in self._checkboxes:
            self._scroll_layout.removeWidget(cb)
            cb.deleteLater()
        self._checkboxes.clear()

        for i in range(self._source_page_count):
            cb = QCheckBox(f"Page {i + 1}")
            cb.setChecked(True)
            self._checkboxes.append(cb)
            self._scroll_layout.insertWidget(i, cb)

    def _confirm(self) -> None:
        if self._source_path is None:
            QMessageBox.warning(self, "Error", "Select a source PDF first.")
            return

        selected = [i for i, cb in enumerate(self._checkboxes) if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Error", "Select at least one page.")
            return

        try:
            doc = fitz.open(str(self._source_path))
            self.result_bytes = bytes(doc.tobytes())
            doc.close()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))
            return

        self.result_pages = selected
        self.result_insert_at = self._insert_spin.value() - 1
        self.accept()

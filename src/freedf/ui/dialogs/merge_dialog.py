"""Merge PDFs dialog."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from freedf.core.multifile import merge_pdfs


class MergeDialog(QDialog):
    """Dialog for merging multiple PDF files."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Merge PDFs")
        self.setMinimumSize(500, 400)

        self._file_list = QListWidget()

        add_btn = QPushButton("Add Files...")
        add_btn.clicked.connect(self._add_files)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_selected)
        up_btn = QPushButton("Move Up")
        up_btn.clicked.connect(self._move_up)
        down_btn = QPushButton("Move Down")
        down_btn.clicked.connect(self._move_down)

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        btn_layout.addStretch()

        top_layout = QHBoxLayout()
        top_layout.addWidget(self._file_list)
        top_layout.addLayout(btn_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._merge)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(buttons)

    def _add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDFs", "", "PDF Files (*.pdf)"
        )
        for p in paths:
            self._file_list.addItem(p)

    def _remove_selected(self) -> None:
        for item in self._file_list.selectedItems():
            self._file_list.takeItem(self._file_list.row(item))

    def _move_up(self) -> None:
        row = self._file_list.currentRow()
        if row > 0:
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row - 1, item)
            self._file_list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self._file_list.currentRow()
        if row < self._file_list.count() - 1:
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row + 1, item)
            self._file_list.setCurrentRow(row + 1)

    def _merge(self) -> None:
        if self._file_list.count() < 2:
            QMessageBox.warning(self, "Error", "Select at least 2 files.")
            return

        output, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "", "PDF Files (*.pdf)"
        )
        if not output:
            return

        paths = [self._file_list.item(i).text() for i in range(self._file_list.count())]
        try:
            merge_pdfs(paths, Path(output))
            QMessageBox.information(self, "Done", "PDFs merged successfully.")
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

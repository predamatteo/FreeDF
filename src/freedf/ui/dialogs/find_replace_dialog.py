"""Find and Replace dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from freedf.core.text_edit import find_text

if TYPE_CHECKING:
    from freedf.core.document import Document


class FindReplaceDialog(QDialog):
    """Dialog for finding and replacing text in the PDF."""

    def __init__(
        self,
        document: Document,
        current_page: int,
        execute_command: object,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Find & Replace")
        self.setMinimumWidth(450)
        self._document = document
        self._current_page = current_page
        self._execute_command = execute_command

        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText("Find text...")
        self._replace_edit = QLineEdit()
        self._replace_edit.setPlaceholderText("Replace with... (keeps original size)")
        self._results_label = QLabel("")

        find_btn = QPushButton("Find")
        find_btn.clicked.connect(self._find)
        replace_page_btn = QPushButton("Replace on Page")
        replace_page_btn.clicked.connect(self._replace_page)
        replace_all_btn = QPushButton("Replace All")
        replace_all_btn.clicked.connect(self._replace_all)
        delete_page_btn = QPushButton("Delete on Page")
        delete_page_btn.clicked.connect(self._delete_page)
        delete_all_btn = QPushButton("Delete All")
        delete_all_btn.clicked.connect(self._delete_all)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(find_btn)
        btn_layout.addWidget(replace_page_btn)
        btn_layout.addWidget(replace_all_btn)
        btn_layout.addWidget(delete_page_btn)
        btn_layout.addWidget(delete_all_btn)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Find:"))
        layout.addWidget(self._find_edit)
        layout.addWidget(QLabel("Replace with:"))
        layout.addWidget(self._replace_edit)
        layout.addLayout(btn_layout)
        layout.addWidget(self._results_label)
        layout.addWidget(close_btn)

    def _find(self) -> None:
        query = self._find_edit.text().strip()
        if not query:
            return
        matches = find_text(self._document, query)
        self._results_label.setText(f"Found {len(matches)} matches")

    def _replace_page(self) -> None:
        self._do_replace([self._current_page])

    def _replace_all(self) -> None:
        self._do_replace(list(range(self._document.page_count)))

    def _do_replace(self, pages: list[int]) -> None:
        from freedf.commands.text_commands import ReplaceTextCommand

        old = self._find_edit.text().strip()
        new = self._replace_edit.text()
        if not old:
            return

        total = 0
        for pn in pages:
            cmd = ReplaceTextCommand(
                document=self._document,
                page_number=pn,
                old_text=old,
                new_text=new,
            )
            self._execute_command(cmd)  # type: ignore[operator]
            total += cmd._count

        self._results_label.setText(f"Replaced {total} occurrences")
        if total == 0:
            QMessageBox.information(self, "Find & Replace", "No matches found.")

    def _delete_page(self) -> None:
        self._do_delete([self._current_page])

    def _delete_all(self) -> None:
        self._do_delete(list(range(self._document.page_count)))

    def _do_delete(self, pages: list[int]) -> None:
        from freedf.commands.text_commands import DeleteTextCommand

        text = self._find_edit.text().strip()
        if not text:
            return

        total = 0
        for pn in pages:
            cmd = DeleteTextCommand(
                document=self._document,
                page_number=pn,
                text=text,
            )
            self._execute_command(cmd)  # type: ignore[operator]
            total += cmd._count

        self._results_label.setText(f"Deleted {total} occurrences")
        if total == 0:
            QMessageBox.information(self, "Delete Text", "No matches found.")

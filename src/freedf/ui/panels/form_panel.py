"""Form fields panel — lists and edits AcroForm fields."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from freedf.core.forms import FormField, detect_form_fields

if TYPE_CHECKING:
    from freedf.core.document import Document


class FormPanel(QWidget):
    """Sidebar for viewing and editing PDF form fields."""

    def __init__(
        self,
        execute_command: Callable[[object], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._execute_command = execute_command
        self._document: Document | None = None
        self._fields: list[FormField] = []
        self._editors: dict[str, QWidget] = {}

        self._header = QLabel("Form Fields")
        self._header.setStyleSheet("font-weight: bold; padding: 8px;")

        self._scroll_widget = QWidget()
        self._form_layout = QFormLayout(self._scroll_widget)
        self._form_layout.setContentsMargins(8, 8, 8, 8)

        self._scroll = QScrollArea()
        self._scroll.setWidget(self._scroll_widget)
        self._scroll.setWidgetResizable(True)

        self._no_fields_label = QLabel("No form fields found")
        self._no_fields_label.setStyleSheet("color: #757575; padding: 16px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._header)
        layout.addWidget(self._no_fields_label)
        layout.addWidget(self._scroll)

        self.setMinimumWidth(220)
        self.setMaximumWidth(300)

    def refresh(self, document: Document | None) -> None:
        """Detect form fields and build editors."""
        self._document = document
        self._fields = []
        self._editors.clear()

        # Clear form layout
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if document is None:
            self._no_fields_label.show()
            self._scroll.hide()
            return

        self._fields = detect_form_fields(document)
        if not self._fields:
            self._no_fields_label.show()
            self._scroll.hide()
            return

        self._no_fields_label.hide()
        self._scroll.show()

        for ff in self._fields:
            editor = self._create_editor(ff)
            self._form_layout.addRow(ff.field_name + ":", editor)
            self._editors[ff.field_name] = editor

    def _create_editor(self, ff: FormField) -> QWidget:
        if ff.field_type == "CheckBox":
            cb = QCheckBox()
            cb.setChecked(ff.current_value.lower() in ("yes", "on", "true"))
            cb.setEnabled(not ff.is_read_only)
            cb.toggled.connect(
                lambda checked, name=ff.field_name: self._on_field_changed(
                    name, "Yes" if checked else "Off"
                )
            )
            return cb
        elif ff.field_type in ("ComboBox", "ListBox") and ff.options:
            combo = QComboBox()
            combo.addItems(ff.options)
            if ff.current_value in ff.options:
                combo.setCurrentText(ff.current_value)
            combo.setEnabled(not ff.is_read_only)
            combo.currentTextChanged.connect(
                lambda text, name=ff.field_name: self._on_field_changed(name, text)
            )
            return combo
        else:
            line = QLineEdit(ff.current_value)
            line.setReadOnly(ff.is_read_only)
            line.editingFinished.connect(
                lambda name=ff.field_name, ed=line: self._on_field_changed(
                    name, ed.text()
                )
            )
            return line

    def _on_field_changed(self, field_name: str, value: str) -> None:
        from freedf.commands.form_commands import FillFieldCommand

        if self._document is None:
            return
        cmd = FillFieldCommand(
            document=self._document,
            field_name=field_name,
            new_value=value,
        )
        self._execute_command(cmd)

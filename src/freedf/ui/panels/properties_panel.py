"""Annotation properties panel — edit selected annotation's properties."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from freedf.core.annotations import AnnotationData, Color
from freedf.ui.widgets.color_picker import ColorPickerButton

if TYPE_CHECKING:
    from freedf.core.document import Document


class PropertiesPanel(QWidget):
    """Panel showing editable properties of the selected annotation."""

    def __init__(
        self,
        execute_command: Callable[[object], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._execute_command = execute_command
        self._document: Document | None = None
        self._page_number: int = 0
        self._annot_data: AnnotationData | None = None

        self._header = QLabel("Properties")
        self._header.setStyleSheet("font-weight: bold; padding: 8px;")

        self._type_label = QLabel("-")
        self._stroke_picker = ColorPickerButton(Color(0, 0, 0))
        self._fill_picker = ColorPickerButton(Color(1, 1, 1))
        self._opacity_spin = QDoubleSpinBox()
        self._opacity_spin.setRange(0.0, 1.0)
        self._opacity_spin.setSingleStep(0.1)
        self._opacity_spin.setValue(1.0)
        self._width_spin = QDoubleSpinBox()
        self._width_spin.setRange(0.5, 20.0)
        self._width_spin.setSingleStep(0.5)
        self._width_spin.setValue(1.0)
        self._text_edit = QLineEdit()
        self._text_edit.setPlaceholderText("Text content")
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 72)
        self._font_size_spin.setValue(12)

        self._apply_btn = QPushButton("Apply")
        self._apply_btn.clicked.connect(self._apply_changes)

        form = QFormLayout()
        form.addRow("Type:", self._type_label)
        form.addRow("Stroke:", self._stroke_picker)
        form.addRow("Fill:", self._fill_picker)
        form.addRow("Opacity:", self._opacity_spin)
        form.addRow("Width:", self._width_spin)
        form.addRow("Text:", self._text_edit)
        form.addRow("Font size:", self._font_size_spin)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self._header)
        layout.addLayout(form)
        layout.addWidget(self._apply_btn)
        layout.addStretch()

        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        self.clear()

    def set_context(self, document: Document | None, page_number: int) -> None:
        self._document = document
        self._page_number = page_number

    def show_annotation(self, annot_data: AnnotationData) -> None:
        """Populate panel with annotation properties."""
        self._annot_data = annot_data
        self._type_label.setText(annot_data.annot_type.name)

        if annot_data.color_stroke:
            self._stroke_picker.set_color(annot_data.color_stroke)
        if annot_data.color_fill:
            self._fill_picker.set_color(annot_data.color_fill)

        self._opacity_spin.setValue(annot_data.opacity)
        self._width_spin.setValue(annot_data.border_width)
        self._text_edit.setText(annot_data.content)
        self._font_size_spin.setValue(int(annot_data.font_size))

        self._text_edit.setVisible(annot_data.annot_type.value == 2)
        self._font_size_spin.setVisible(annot_data.annot_type.value == 2)
        self._apply_btn.setEnabled(True)
        self.show()

    def clear(self) -> None:
        self._annot_data = None
        self._type_label.setText("-")
        self._apply_btn.setEnabled(False)

    def _apply_changes(self) -> None:
        if self._annot_data is None or self._document is None:
            return

        from freedf.commands.annotation_commands import ModifyAnnotationCommand

        props: dict[str, object] = {
            "stroke_color": self._stroke_picker.color,
            "fill_color": self._fill_picker.color,
            "opacity": self._opacity_spin.value(),
            "border_width": self._width_spin.value(),
        }

        cmd = ModifyAnnotationCommand(
            document=self._document,
            page_number=self._page_number,
            annot_id=self._annot_data.annot_id,
            new_props=props,
        )
        self._execute_command(cmd)

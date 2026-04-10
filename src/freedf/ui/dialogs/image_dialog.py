"""Image insertion dialog."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from freedf.core.annotations import Rect


class ImageDialog(QDialog):
    """Dialog for selecting an image and configuring insertion parameters."""

    def __init__(
        self,
        default_x: float = 72,
        default_y: float = 72,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Insert Image")
        self.setMinimumWidth(350)

        self._image_path: Path | None = None
        self.result_path: str = ""
        self.result_rect: Rect | None = None

        self._path_label = QLabel("No image selected")
        pick_btn = __import__(
            "PySide6.QtWidgets", fromlist=["QPushButton"]
        ).QPushButton("Choose Image...")
        pick_btn.clicked.connect(self._pick_image)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(10, 2000)
        self._width_spin.setValue(200)
        self._height_spin = QSpinBox()
        self._height_spin.setRange(10, 2000)
        self._height_spin.setValue(200)
        self._x_spin = QSpinBox()
        self._x_spin.setRange(0, 2000)
        self._x_spin.setValue(int(default_x))
        self._y_spin = QSpinBox()
        self._y_spin.setRange(0, 2000)
        self._y_spin.setValue(int(default_y))
        self._keep_aspect = QCheckBox("Keep aspect ratio")
        self._keep_aspect.setChecked(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._confirm)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._path_label)
        layout.addWidget(pick_btn)
        layout.addWidget(QLabel("X position (pt):"))
        layout.addWidget(self._x_spin)
        layout.addWidget(QLabel("Y position (pt):"))
        layout.addWidget(self._y_spin)
        layout.addWidget(QLabel("Width (pt):"))
        layout.addWidget(self._width_spin)
        layout.addWidget(QLabel("Height (pt):"))
        layout.addWidget(self._height_spin)
        layout.addWidget(self._keep_aspect)
        layout.addWidget(buttons)

    def _pick_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)",
        )
        if path:
            self._image_path = Path(path)
            self._path_label.setText(self._image_path.name)

    def _confirm(self) -> None:
        if self._image_path is None:
            return
        x = self._x_spin.value()
        y = self._y_spin.value()
        w = self._width_spin.value()
        h = self._height_spin.value()
        self.result_path = str(self._image_path)
        self.result_rect = Rect(x, y, x + w, y + h)
        self.accept()

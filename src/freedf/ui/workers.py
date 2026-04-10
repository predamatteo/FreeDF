"""Background worker threads for long-running operations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QThread, Signal


class WorkerThread(QThread):
    """Generic worker thread that runs a callable and emits signals."""

    progress = Signal(int, str)  # percentage, message
    finished_ok = Signal(object)  # result
    error = Signal(str)  # error message

    def __init__(
        self,
        task: Callable[..., Any],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self._task = task
        self._args = args
        self._kwargs = kwargs or {}

    def run(self) -> None:
        try:
            result = self._task(*self._args, **self._kwargs)
            self.finished_ok.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))

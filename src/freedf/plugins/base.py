"""Plugin protocol and hook definitions."""

from __future__ import annotations

from enum import Enum, auto
from typing import Protocol


class PluginHook(Enum):
    """Available plugin hook points."""

    ON_APP_STARTED = auto()
    ON_DOCUMENT_OPENED = auto()
    ON_DOCUMENT_CLOSED = auto()
    ON_PAGE_CHANGED = auto()
    ON_BEFORE_SAVE = auto()
    ON_AFTER_SAVE = auto()


class Plugin(Protocol):
    """Protocol that all FreeDF plugins must satisfy."""

    @property
    def name(self) -> str:
        """Unique plugin name."""
        ...

    @property
    def version(self) -> str:
        """Plugin version string."""
        ...

    def activate(self) -> None:
        """Called when the plugin is loaded."""
        ...

    def deactivate(self) -> None:
        """Called when the plugin is unloaded."""
        ...

    def on_hook(self, hook: PluginHook, **kwargs: object) -> None:
        """Called when a hook event fires."""
        ...

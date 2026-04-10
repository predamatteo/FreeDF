"""Tool manager for switching between interaction tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

from freedf.core.annotations import Color

if TYPE_CHECKING:
    from freedf.ui.tools.base_tool import Tool


class ToolManager:
    """Manages the active tool and shared tool properties."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._current_tool: Tool | None = None
        self.current_color: Color = Color.yellow()
        self.current_opacity: float = 0.5
        self.current_thickness: float = 2.0
        self.current_font_size: float = 12.0

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def set_tool(self, name: str) -> None:
        if self._current_tool is not None:
            self._current_tool.deactivate()
        self._current_tool = self._tools.get(name)
        if self._current_tool is not None:
            self._current_tool.activate()

    @property
    def current_tool(self) -> Tool | None:
        return self._current_tool

    @property
    def current_tool_name(self) -> str:
        if self._current_tool is not None:
            return self._current_tool.name
        return ""

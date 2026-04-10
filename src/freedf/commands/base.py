"""Command protocol and CommandStack for undo/redo."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Command(Protocol):
    """Protocol for undoable commands."""

    @property
    def description(self) -> str: ...

    def execute(self) -> None: ...

    def undo(self) -> None: ...


class CommandStack:
    """Manages undo/redo stacks of Command objects."""

    def __init__(self, max_depth: int = 100) -> None:
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []
        self._max_depth = max_depth

    def execute(self, command: Command) -> None:
        """Execute a command and push it onto the undo stack."""
        command.execute()
        self._undo_stack.append(command)
        if len(self._undo_stack) > self._max_depth:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> Command | None:
        """Undo the most recent command. Returns the command, or None."""
        if not self._undo_stack:
            return None
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo(self) -> Command | None:
        """Redo the most recently undone command. Returns the command, or None."""
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return command

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    @property
    def undo_description(self) -> str | None:
        if self._undo_stack:
            return self._undo_stack[-1].description
        return None

    @property
    def redo_description(self) -> str | None:
        if self._redo_stack:
            return self._redo_stack[-1].description
        return None

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

"""Tests for freedf.commands.base.CommandStack."""

from __future__ import annotations

import pytest

from freedf.commands.base import CommandStack


class MockCommand:
    def __init__(self, label: str = "mock") -> None:
        self.label = label
        self.execute_count = 0
        self.undo_count = 0

    @property
    def description(self) -> str:
        return self.label

    def execute(self) -> None:
        self.execute_count += 1

    def undo(self) -> None:
        self.undo_count += 1


class FailingCommand:
    @property
    def description(self) -> str:
        return "fail"

    def execute(self) -> None:
        raise RuntimeError("boom")

    def undo(self) -> None:
        pass


class TestCommandStack:
    def test_execute(self) -> None:
        stack = CommandStack()
        cmd = MockCommand()
        stack.execute(cmd)
        assert cmd.execute_count == 1
        assert stack.can_undo

    def test_undo(self) -> None:
        stack = CommandStack()
        cmd = MockCommand()
        stack.execute(cmd)
        result = stack.undo()
        assert result is cmd
        assert cmd.undo_count == 1
        assert not stack.can_undo
        assert stack.can_redo

    def test_redo(self) -> None:
        stack = CommandStack()
        cmd = MockCommand()
        stack.execute(cmd)
        stack.undo()
        result = stack.redo()
        assert result is cmd
        assert cmd.execute_count == 2

    def test_new_execute_clears_redo(self) -> None:
        stack = CommandStack()
        cmd1 = MockCommand("first")
        cmd2 = MockCommand("second")
        stack.execute(cmd1)
        stack.undo()
        stack.execute(cmd2)
        assert not stack.can_redo

    def test_undo_empty(self) -> None:
        stack = CommandStack()
        assert stack.undo() is None

    def test_redo_empty(self) -> None:
        stack = CommandStack()
        assert stack.redo() is None

    def test_max_depth(self) -> None:
        stack = CommandStack(max_depth=3)
        cmds = [MockCommand(f"cmd{i}") for i in range(5)]
        for cmd in cmds:
            stack.execute(cmd)
        # Only last 3 should remain
        count = 0
        while stack.undo():
            count += 1
        assert count == 3

    def test_clear(self) -> None:
        stack = CommandStack()
        stack.execute(MockCommand())
        stack.clear()
        assert not stack.can_undo
        assert not stack.can_redo

    def test_descriptions(self) -> None:
        stack = CommandStack()
        cmd = MockCommand("rotate")
        stack.execute(cmd)
        assert stack.undo_description == "rotate"
        assert stack.redo_description is None
        stack.undo()
        assert stack.redo_description == "rotate"
        assert stack.undo_description is None

    def test_failed_execute_does_not_push(self) -> None:
        stack = CommandStack()
        cmd = FailingCommand()
        with pytest.raises(RuntimeError):
            stack.execute(cmd)
        assert not stack.can_undo

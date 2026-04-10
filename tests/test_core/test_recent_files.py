"""Tests for freedf.core.recent_files."""

from __future__ import annotations

from pathlib import Path

from freedf.core.recent_files import RecentFilesManager


class TestRecentFilesManager:
    def test_add_and_retrieve(self, tmp_path: Path) -> None:
        config = tmp_path / "recent.json"
        mgr = RecentFilesManager(config_path=config, max_entries=5)

        # Create real files so they pass the exists() check
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.touch()
        f2.touch()

        mgr.add(f1)
        mgr.add(f2)

        result = mgr.get_list()
        assert len(result) == 2
        assert result[0].name == "b.pdf"  # most recent first
        assert result[1].name == "a.pdf"

    def test_max_entries(self, tmp_path: Path) -> None:
        config = tmp_path / "recent.json"
        mgr = RecentFilesManager(config_path=config, max_entries=2)

        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.pdf"
            f.touch()
            files.append(f)

        for f in files:
            mgr.add(f)

        result = mgr.get_list()
        assert len(result) == 2
        assert result[0].name == "file2.pdf"

    def test_persistence(self, tmp_path: Path) -> None:
        config = tmp_path / "recent.json"
        f = tmp_path / "test.pdf"
        f.touch()

        mgr1 = RecentFilesManager(config_path=config)
        mgr1.add(f)

        mgr2 = RecentFilesManager(config_path=config)
        result = mgr2.get_list()
        assert len(result) == 1

    def test_clear(self, tmp_path: Path) -> None:
        config = tmp_path / "recent.json"
        f = tmp_path / "test.pdf"
        f.touch()

        mgr = RecentFilesManager(config_path=config)
        mgr.add(f)
        mgr.clear()
        assert mgr.get_list() == []

    def test_nonexistent_pruned(self, tmp_path: Path) -> None:
        config = tmp_path / "recent.json"
        f = tmp_path / "gone.pdf"
        f.touch()

        mgr = RecentFilesManager(config_path=config)
        mgr.add(f)
        f.unlink()

        result = mgr.get_list()
        assert len(result) == 0

    def test_duplicate_moves_to_top(self, tmp_path: Path) -> None:
        config = tmp_path / "recent.json"
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.touch()
        f2.touch()

        mgr = RecentFilesManager(config_path=config)
        mgr.add(f1)
        mgr.add(f2)
        mgr.add(f1)  # re-add f1

        result = mgr.get_list()
        assert result[0].name == "a.pdf"  # f1 moved to top

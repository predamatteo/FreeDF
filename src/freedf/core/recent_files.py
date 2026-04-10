"""Recent files manager (no Qt dependency)."""

from __future__ import annotations

import json
from pathlib import Path


class RecentFilesManager:
    """Manages a list of recently opened PDF files, persisted to JSON."""

    def __init__(self, config_path: Path | None = None, max_entries: int = 10) -> None:
        if config_path is None:
            config_dir = Path.home() / ".freedf"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "recent.json"
        self._path = config_path
        self._max_entries = max_entries
        self._entries: list[str] = self._load()

    def add(self, path: str | Path) -> None:
        """Add a file path to the top of the list."""
        path_str = str(Path(path).resolve())
        if path_str in self._entries:
            self._entries.remove(path_str)
        self._entries.insert(0, path_str)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[: self._max_entries]
        self._save()

    def get_list(self) -> list[Path]:
        """Return recent files, pruning entries that no longer exist."""
        valid = [Path(p) for p in self._entries if Path(p).exists()]
        if len(valid) != len(self._entries):
            self._entries = [str(p) for p in valid]
            self._save()
        return valid

    def clear(self) -> None:
        """Clear the recent files list."""
        self._entries.clear()
        self._save()

    def _load(self) -> list[str]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return [str(e) for e in data]
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._entries, indent=2), encoding="utf-8")
        except OSError:
            pass

"""Plugin discovery and lifecycle management."""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path
from typing import Any

from freedf.plugins.base import Plugin, PluginHook

ENTRY_POINT_GROUP = "freedf.plugins"
USER_PLUGINS_DIR = Path.home() / ".freedf" / "plugins"


class PluginManager:
    """Discovers, loads, and manages FreeDF plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    @property
    def plugins(self) -> dict[str, Plugin]:
        return dict(self._plugins)

    def discover(self) -> list[str]:
        """Discover plugins from entry points and user directory.

        Returns list of discovered plugin names.
        """
        discovered: list[str] = []

        # 1. Entry points (pip-installed plugins)
        try:
            eps = importlib.metadata.entry_points()
            group = eps.select(group=ENTRY_POINT_GROUP)  # type: ignore[union-attr]
            for ep in group:
                try:
                    plugin_cls = ep.load()
                    plugin = plugin_cls()
                    if hasattr(plugin, "name") and hasattr(plugin, "activate"):
                        self._plugins[plugin.name] = plugin
                        discovered.append(plugin.name)
                except Exception as exc:
                    print(
                        f"Warning: Failed to load plugin {ep.name}: {exc}",
                        file=sys.stderr,
                    )
        except Exception:
            pass

        # 2. User plugins directory (~/.freedf/plugins/)
        if USER_PLUGINS_DIR.exists():
            for py_file in USER_PLUGINS_DIR.glob("*.py"):
                try:
                    name = py_file.stem
                    spec = importlib.util.spec_from_file_location(  # type: ignore[attr-defined]
                        f"freedf_plugin_{name}", str(py_file)
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
                        spec.loader.exec_module(module)
                        if hasattr(module, "create_plugin"):
                            plugin = module.create_plugin()
                            self._plugins[plugin.name] = plugin
                            discovered.append(plugin.name)
                except Exception as exc:
                    print(
                        f"Warning: Failed to load user plugin {py_file.name}: {exc}",
                        file=sys.stderr,
                    )

        return discovered

    def activate_all(self) -> None:
        """Activate all discovered plugins."""
        for plugin in self._plugins.values():
            try:
                plugin.activate()
            except Exception as exc:
                print(
                    f"Warning: Plugin {plugin.name} activation failed: {exc}",
                    file=sys.stderr,
                )

    def deactivate_all(self) -> None:
        """Deactivate all plugins."""
        import contextlib

        for plugin in self._plugins.values():
            with contextlib.suppress(Exception):
                plugin.deactivate()

    def fire_hook(self, hook: PluginHook, **kwargs: Any) -> None:
        """Fire a hook event to all active plugins."""
        import contextlib

        for plugin in self._plugins.values():
            with contextlib.suppress(Exception):
                plugin.on_hook(hook, **kwargs)

    def get_plugin(self, name: str) -> Plugin | None:
        """Get a plugin by name."""
        return self._plugins.get(name)

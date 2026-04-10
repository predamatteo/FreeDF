"""FreeDF plugin system — discovery, loading, and lifecycle management."""

from freedf.plugins.base import Plugin, PluginHook
from freedf.plugins.loader import PluginManager

__all__ = ["Plugin", "PluginHook", "PluginManager"]

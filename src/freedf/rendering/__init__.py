"""FreeDF rendering — page rendering and cache (no Qt dependency)."""

from freedf.rendering.cache import RenderCache
from freedf.rendering.renderer import PageRenderer

__all__ = ["PageRenderer", "RenderCache"]

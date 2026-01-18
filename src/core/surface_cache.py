"""
Surface Cache - Shared Surface object cache for activities and UI.

This module provides pre-allocated Surface objects to avoid creating new ones every frame.
Creating pygame.Surface() every frame is expensive and causes GC pressure.

Usage:
    from src.core.surface_cache import get_overlay, get_shadow_surface, get_glow_surface

    # In draw() method:
    overlay = get_overlay()  # Returns cached full-screen overlay
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
"""

import pygame
from typing import Dict, Tuple, Optional
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Cache for full-screen overlay surfaces
_overlay_cache: Dict[Tuple[int, int, int], pygame.Surface] = {}

# Cache for commonly used surface sizes
_surface_cache: Dict[Tuple[int, int, bool], pygame.Surface] = {}

# Pre-allocated overlay (most common use case)
_main_overlay: Optional[pygame.Surface] = None
_main_overlay_alpha: Optional[pygame.Surface] = None


def _ensure_display_initialized():
    """Ensure pygame display is initialized before creating surfaces."""
    if not pygame.get_init():
        return False
    try:
        pygame.display.get_surface()
        return True
    except:
        return False


def get_overlay(color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
    """
    Get a full-screen overlay surface (cached).

    Args:
        color: RGB color tuple for the overlay.

    Returns:
        A cached Surface filled with the specified color.
    """
    global _main_overlay

    if not _ensure_display_initialized():
        # Fallback: create new surface if display not ready
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(color)
        return surface

    # Use main overlay for black (most common)
    if color == (0, 0, 0):
        if _main_overlay is None:
            _main_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            _main_overlay.fill((0, 0, 0))
        else:
            # Reset to black in case it was modified
            _main_overlay.fill((0, 0, 0))
        return _main_overlay

    # Cache other colors
    if color not in _overlay_cache:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(color)
        _overlay_cache[color] = surface
    else:
        # Reset the fill in case alpha was modified
        _overlay_cache[color].fill(color)

    return _overlay_cache[color]


def get_overlay_alpha() -> pygame.Surface:
    """
    Get a full-screen overlay with alpha channel support (cached).

    Returns:
        A cached Surface with SRCALPHA flag.
    """
    global _main_overlay_alpha

    if not _ensure_display_initialized():
        return pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    if _main_overlay_alpha is None:
        _main_overlay_alpha = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Clear the surface for reuse
    _main_overlay_alpha.fill((0, 0, 0, 0))
    return _main_overlay_alpha


def get_surface(width: int, height: int, alpha: bool = False) -> pygame.Surface:
    """
    Get a cached surface of the specified size.

    For frequently used sizes, this returns a cached surface.
    For rare sizes, creates a new one.

    Args:
        width: Surface width.
        height: Surface height.
        alpha: Whether to include alpha channel.

    Returns:
        A Surface of the specified dimensions.
    """
    # Round to common sizes to improve cache hit rate
    width = _round_to_common_size(width)
    height = _round_to_common_size(height)

    key = (width, height, alpha)

    if key not in _surface_cache:
        if alpha:
            _surface_cache[key] = pygame.Surface((width, height), pygame.SRCALPHA)
        else:
            _surface_cache[key] = pygame.Surface((width, height))

    surface = _surface_cache[key]

    # Clear the surface for reuse
    if alpha:
        surface.fill((0, 0, 0, 0))
    else:
        surface.fill((0, 0, 0))

    return surface


def _round_to_common_size(size: int) -> int:
    """Round size to common values to improve cache hit rate."""
    # Common UI element sizes
    common_sizes = [16, 32, 48, 64, 100, 128, 150, 200, 256, 300, 400, 512, 600, 800, 1024, 1200]

    for common in common_sizes:
        if size <= common:
            return common

    # For very large sizes, round up to nearest 100
    return ((size + 99) // 100) * 100


def get_shadow_surface(width: int, height: int) -> pygame.Surface:
    """
    Get a shadow surface (with alpha channel).

    Args:
        width: Shadow width.
        height: Shadow height.

    Returns:
        A Surface for drawing shadows.
    """
    return get_surface(width, height, alpha=True)


def get_glow_surface(width: int, height: int) -> pygame.Surface:
    """
    Get a glow effect surface (with alpha channel).

    Args:
        width: Glow width.
        height: Glow height.

    Returns:
        A Surface for drawing glow effects.
    """
    return get_surface(width, height, alpha=True)


def get_cache_stats() -> dict:
    """Get cache statistics for debugging."""
    return {
        "overlay_colors_cached": len(_overlay_cache),
        "surfaces_cached": len(_surface_cache),
        "main_overlay_initialized": _main_overlay is not None,
        "main_overlay_alpha_initialized": _main_overlay_alpha is not None,
    }


def clear_cache():
    """Clear all cached surfaces to free memory."""
    global _overlay_cache, _surface_cache, _main_overlay, _main_overlay_alpha

    _overlay_cache.clear()
    _surface_cache.clear()
    _main_overlay = None
    _main_overlay_alpha = None

    print("[SURFACE_CACHE] Cache cleared")


# Pre-create common box surfaces for UI elements
class BoxCache:
    """Cache for common UI box sizes."""

    def __init__(self):
        self._boxes: Dict[Tuple[int, int, Tuple[int, int, int]], pygame.Surface] = {}

    def get_box(
        self,
        width: int,
        height: int,
        color: Tuple[int, int, int] = (25, 25, 30),
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 0
    ) -> pygame.Surface:
        """
        Get a cached box surface.

        Args:
            width: Box width.
            height: Box height.
            color: Fill color.
            border_color: Optional border color.
            border_width: Border width.

        Returns:
            A Surface with the box drawn on it.
        """
        # Round dimensions
        width = _round_to_common_size(width)
        height = _round_to_common_size(height)

        key = (width, height, color)

        if key not in self._boxes:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(surface, color, (0, 0, width, height))
            self._boxes[key] = surface

        box = self._boxes[key]

        # Draw border if specified (not cached since it changes)
        if border_color and border_width > 0:
            # Create a copy to avoid modifying cached version
            result = box.copy()
            pygame.draw.rect(result, border_color, (0, 0, width, height), border_width)
            return result

        return box

    def clear(self):
        """Clear the box cache."""
        self._boxes.clear()


# Global box cache instance
_box_cache = BoxCache()


def get_box(
    width: int,
    height: int,
    color: Tuple[int, int, int] = (25, 25, 30),
    border_color: Optional[Tuple[int, int, int]] = None,
    border_width: int = 0
) -> pygame.Surface:
    """
    Get a cached UI box surface.

    Args:
        width: Box width.
        height: Box height.
        color: Fill color.
        border_color: Optional border color.
        border_width: Border width.

    Returns:
        A Surface with the box.
    """
    return _box_cache.get_box(width, height, color, border_color, border_width)

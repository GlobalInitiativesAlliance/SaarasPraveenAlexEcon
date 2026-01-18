"""
Sprite Cache - Lazy loading sprite cache optimized for web/Chromebook performance.

Instead of preloading ALL sprites at startup (which blocks for seconds and uses tons of memory),
this module implements on-demand loading with smart caching and priority tiers.
"""

import os
import pygame
from typing import Dict, Optional, Set
from functools import lru_cache

# Global sprite cache with lazy loading
_sprite_cache: Dict[str, pygame.Surface] = {}
_failed_paths: Set[str] = set()  # Track paths that failed to load (avoid retrying)
_cache_initialized = False

# Priority tiers for sprites - only critical sprites loaded at startup
PRIORITY_CRITICAL = [
    # Player sprites - needed immediately
    "sprites/player/idle_front.png",
    "sprites/player/idle_back.png",
    "sprites/player/idle_left.png",
    "sprites/player/idle_right.png",
]

PRIORITY_HIGH = [
    # Walking animations - needed for movement
    "sprites/player/walk_front_1.png",
    "sprites/player/walk_front_2.png",
    "sprites/player/walk_back_1.png",
    "sprites/player/walk_back_2.png",
    "sprites/player/walk_left_1.png",
    "sprites/player/walk_left_2.png",
    "sprites/player/walk_right_1.png",
    "sprites/player/walk_right_2.png",
]

# These are loaded on-demand when entering interiors
INTERIOR_SPRITES = [
    "assets/moderninteriors-win/1_Interiors/16x16/Interiors_16x16.png",
    "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_16x16.png",
]


def get_base_dir() -> str:
    """Get the project base directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _load_single_sprite(relative_path: str) -> Optional[pygame.Surface]:
    """
    Load a single sprite without caching logic.

    Args:
        relative_path: Path relative to project root.

    Returns:
        The loaded surface, or None on error.
    """
    base_dir = get_base_dir()
    full_path = os.path.join(base_dir, relative_path)

    if not os.path.exists(full_path):
        return None

    try:
        surface = pygame.image.load(full_path).convert_alpha()
        return surface
    except Exception as e:
        print(f"[SPRITE_CACHE] Error loading {relative_path}: {e}")
        return None


def preload_all_sprites() -> int:
    """
    Preload only CRITICAL sprites at startup for fast load times.
    Other sprites are loaded on-demand.

    Returns:
        Number of sprites loaded.
    """
    global _sprite_cache, _cache_initialized

    if _cache_initialized:
        return len(_sprite_cache)

    loaded = 0

    # Only load critical sprites at startup (player idle sprites)
    print("[SPRITE_CACHE] Loading critical sprites only (lazy loading enabled)...")

    for relative_path in PRIORITY_CRITICAL:
        surface = _load_single_sprite(relative_path)
        if surface:
            _sprite_cache[relative_path] = surface
            loaded += 1

    # Optionally preload high-priority sprites in background-friendly way
    for relative_path in PRIORITY_HIGH:
        surface = _load_single_sprite(relative_path)
        if surface:
            _sprite_cache[relative_path] = surface
            loaded += 1

    _cache_initialized = True
    print(f"[SPRITE_CACHE] Preloaded {loaded} critical sprites (others loaded on-demand)")
    return loaded


def get_cached_sprite(relative_path: str) -> Optional[pygame.Surface]:
    """
    Get a sprite from the cache (does not load if missing).

    Args:
        relative_path: Path relative to project root.

    Returns:
        The cached surface, or None if not found.
    """
    return _sprite_cache.get(relative_path)


def load_sprite(relative_path: str) -> Optional[pygame.Surface]:
    """
    Load a sprite with lazy caching.
    This is the main function to use - it handles caching automatically.

    Args:
        relative_path: Path relative to project root.

    Returns:
        The loaded surface, or None on error.
    """
    # Check cache first
    if relative_path in _sprite_cache:
        return _sprite_cache[relative_path]

    # Check if we already failed to load this
    if relative_path in _failed_paths:
        return None

    # Load on-demand
    surface = _load_single_sprite(relative_path)

    if surface:
        _sprite_cache[relative_path] = surface
        return surface
    else:
        _failed_paths.add(relative_path)
        return None


def preload_interior_sprites() -> int:
    """
    Preload interior sprites when entering a building.
    Call this when transitioning to an interior to avoid stutter.

    Returns:
        Number of sprites loaded.
    """
    loaded = 0

    for relative_path in INTERIOR_SPRITES:
        if relative_path not in _sprite_cache:
            surface = _load_single_sprite(relative_path)
            if surface:
                _sprite_cache[relative_path] = surface
                loaded += 1

    if loaded > 0:
        print(f"[SPRITE_CACHE] Loaded {loaded} interior sprites on-demand")

    return loaded


def preload_sprite_list(paths: list) -> int:
    """
    Preload a specific list of sprites.
    Use this for scene-specific preloading.

    Args:
        paths: List of relative paths to preload.

    Returns:
        Number of sprites loaded.
    """
    loaded = 0

    for relative_path in paths:
        if relative_path not in _sprite_cache:
            surface = _load_single_sprite(relative_path)
            if surface:
                _sprite_cache[relative_path] = surface
                loaded += 1

    return loaded


def unload_sprites(paths: list) -> int:
    """
    Unload sprites to free memory.
    Use this when leaving an area to reduce memory pressure.

    Args:
        paths: List of relative paths to unload.

    Returns:
        Number of sprites unloaded.
    """
    unloaded = 0

    for relative_path in paths:
        if relative_path in _sprite_cache:
            del _sprite_cache[relative_path]
            unloaded += 1

    if unloaded > 0:
        print(f"[SPRITE_CACHE] Unloaded {unloaded} sprites to free memory")

    return unloaded


def get_cache_stats() -> dict:
    """
    Get cache statistics for debugging.

    Returns:
        Dictionary with cache stats.
    """
    return {
        "cached_sprites": len(_sprite_cache),
        "failed_loads": len(_failed_paths),
        "initialized": _cache_initialized,
    }


def clear_cache():
    """Clear the entire sprite cache (use sparingly)."""
    global _sprite_cache, _failed_paths
    _sprite_cache.clear()
    _failed_paths.clear()
    print("[SPRITE_CACHE] Cache cleared")


def is_cache_initialized() -> bool:
    """Check if the sprite cache has been initialized."""
    return _cache_initialized

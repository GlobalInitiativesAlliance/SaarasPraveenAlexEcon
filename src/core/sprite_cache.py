"""
Sprite Cache - Preloads and caches all interior sprites for web compatibility.
This prevents freezing in pygbag web builds by loading all assets upfront.
"""

import os
import pygame
from typing import Dict, Optional

# Global sprite cache
_sprite_cache: Dict[str, pygame.Surface] = {}
_cache_initialized = False


def get_base_dir() -> str:
    """Get the project base directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def preload_all_sprites() -> int:
    """
    Preload all interior sprites into cache.
    Call this once at game startup before the async main loop.

    Returns:
        Number of sprites loaded.
    """
    global _sprite_cache, _cache_initialized

    if _cache_initialized:
        return len(_sprite_cache)

    base_dir = get_base_dir()
    loaded = 0

    # All sprite sheets used by interiors
    sprite_paths = [
        # Main interior sprites
        "assets/moderninteriors-win/1_Interiors/16x16/Interiors_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_16x16.png",
        # Theme sprites
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/1_Generic_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/2_LivingRoom_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/3_Bathroom_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/4_Bedroom_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/5_Classroom_and_library_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/12_Kitchen_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/16_Grocery_store_16x16.png",
        # Wall/floor sprites
        "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Walls_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Floor_Shadows_16x16.png",
        "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Baseboards_16x16.png",
        # Custom sprites
        "assets/grocery_custom_16x16.png",
        # Top-down retro interior
        "Top-Down_Retro_Interior/TopDownHouse_FloorsAndWalls.png",
        "Top-Down_Retro_Interior/TopDownHouse_FurnitureState1.png",
        "Top-Down_Retro_Interior/TopDownHouse_FurnitureState2.png",
        "Top-Down_Retro_Interior/TopDownHouse_DoorsAndWindows.png",
        "Top-Down_Retro_Interior/TopDownHouse_SmallItems.png",
        # Player sprites
        "sprites/player/idle_front.png",
        "sprites/player/idle_back.png",
        "sprites/player/idle_left.png",
        "sprites/player/idle_right.png",
        "sprites/player/walk_front_1.png",
        "sprites/player/walk_front_2.png",
        "sprites/player/walk_back_1.png",
        "sprites/player/walk_back_2.png",
        "sprites/player/walk_left_1.png",
        "sprites/player/walk_left_2.png",
        "sprites/player/walk_right_1.png",
        "sprites/player/walk_right_2.png",
    ]

    for relative_path in sprite_paths:
        full_path = os.path.join(base_dir, relative_path)
        if os.path.exists(full_path):
            try:
                surface = pygame.image.load(full_path).convert_alpha()
                _sprite_cache[relative_path] = surface
                loaded += 1
            except Exception as e:
                print(f"[SPRITE_CACHE] Error loading {relative_path}: {e}")

    _cache_initialized = True
    print(f"[SPRITE_CACHE] Preloaded {loaded} sprites for web compatibility")
    return loaded


def get_cached_sprite(relative_path: str) -> Optional[pygame.Surface]:
    """
    Get a sprite from the cache.

    Args:
        relative_path: Path relative to project root.

    Returns:
        The cached surface, or None if not found.
    """
    return _sprite_cache.get(relative_path)


def load_sprite(relative_path: str) -> Optional[pygame.Surface]:
    """
    Load a sprite, using cache if available.
    Falls back to direct loading if not in cache.

    Args:
        relative_path: Path relative to project root.

    Returns:
        The loaded surface, or None on error.
    """
    # Check cache first
    if relative_path in _sprite_cache:
        return _sprite_cache[relative_path]

    # Not in cache, load directly
    base_dir = get_base_dir()
    full_path = os.path.join(base_dir, relative_path)

    if not os.path.exists(full_path):
        return None

    try:
        surface = pygame.image.load(full_path).convert_alpha()
        _sprite_cache[relative_path] = surface
        return surface
    except Exception as e:
        print(f"[SPRITE_CACHE] Error loading {relative_path}: {e}")
        return None


def is_cache_initialized() -> bool:
    """Check if the sprite cache has been initialized."""
    return _cache_initialized

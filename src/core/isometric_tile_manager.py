"""
Isometric Tile Manager

Handles loading and caching of isometric sprites from the Isometric City asset pack.
Ground tiles are stored as horizontal strips with 4 variants per image.
Buildings and props are individual sprites.
"""

import pygame
import os
import random
from src.constants import ISO_TILE_WIDTH, ISO_TILE_HEIGHT
from src.utils.isometric_asset_definitions import (
    ISOMETRIC_ASSETS_BASE,
    GROUND_TILES,
    BUILDINGS,
    PROPS,
    get_asset_path
)


class IsometricTileManager:
    """Manages loading and caching of isometric sprites."""

    # Number of variants per ground tile strip
    VARIANTS_PER_STRIP = 4

    def __init__(self):
        self.ground_tiles = {}  # category -> list of sprites
        self.buildings = {}  # building_type -> list of sprites
        self.props = {}  # prop_type -> list of sprites
        self.loaded = False

    def load_all(self):
        """Load all isometric assets."""
        if self.loaded:
            return

        print("[ISOMETRIC] Loading isometric assets...")
        self._load_ground_tiles()
        self._load_buildings()
        self._load_props()
        self.loaded = True
        print("[ISOMETRIC] Asset loading complete.")

    def _load_strip_sprites(self, file_path, sprite_width=None, sprite_height=None):
        """
        Load a horizontal strip image and extract individual sprites.

        Args:
            file_path: Path to the strip image
            sprite_width: Width of each sprite (defaults to ISO_TILE_WIDTH)
            sprite_height: Height of each sprite (defaults to ISO_TILE_HEIGHT)

        Returns:
            list: List of pygame.Surface sprites
        """
        if sprite_width is None:
            sprite_width = ISO_TILE_WIDTH
        if sprite_height is None:
            sprite_height = ISO_TILE_HEIGHT

        full_path = get_asset_path(file_path)

        try:
            strip = pygame.image.load(full_path).convert_alpha()
        except pygame.error as e:
            print(f"[ISOMETRIC] Error loading {file_path}: {e}")
            return []

        strip_width = strip.get_width()
        strip_height = strip.get_height()

        # Calculate number of sprites in strip
        num_sprites = strip_width // sprite_width

        sprites = []
        for i in range(num_sprites):
            # Create surface for this sprite
            sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            # Blit portion of strip to new surface
            sprite.blit(strip, (0, 0), (i * sprite_width, 0, sprite_width, sprite_height))
            sprites.append(sprite)

        return sprites

    def _load_single_sprite(self, file_path):
        """
        Load a single sprite image (for buildings and props).

        Args:
            file_path: Path to the sprite image

        Returns:
            pygame.Surface or None
        """
        full_path = get_asset_path(file_path)

        try:
            sprite = pygame.image.load(full_path).convert_alpha()
            return sprite
        except pygame.error as e:
            print(f"[ISOMETRIC] Error loading {file_path}: {e}")
            return None

    def _load_ground_tiles(self):
        """Load all ground tile sprites."""
        print("[ISOMETRIC] Loading ground tiles...")

        for category, files in GROUND_TILES.items():
            self.ground_tiles[category] = []

            for file_path in files:
                sprites = self._load_strip_sprites(file_path)
                self.ground_tiles[category].extend(sprites)

            print(f"  {category}: {len(self.ground_tiles[category])} sprites")

    def _load_buildings(self):
        """Load all building sprites."""
        print("[ISOMETRIC] Loading buildings...")

        for building_type, files in BUILDINGS.items():
            self.buildings[building_type] = []

            for file_path in files:
                sprite = self._load_single_sprite(file_path)
                if sprite:
                    self.buildings[building_type].append(sprite)

            print(f"  {building_type}: {len(self.buildings[building_type])} sprites")

    def _load_props(self):
        """Load all prop sprites."""
        print("[ISOMETRIC] Loading props...")

        for prop_type, files in PROPS.items():
            self.props[prop_type] = []

            for file_path in files:
                sprite = self._load_single_sprite(file_path)
                if sprite:
                    self.props[prop_type].append(sprite)

            print(f"  {prop_type}: {len(self.props[prop_type])} sprites")

    def get_ground_tile(self, category, variant=None):
        """
        Get a ground tile sprite.

        Args:
            category: Tile category ('road', 'sidewalk', 'grass', etc.)
            variant: Specific variant index, or None for random

        Returns:
            pygame.Surface or None
        """
        if category not in self.ground_tiles:
            return None

        tiles = self.ground_tiles[category]
        if not tiles:
            return None

        if variant is None:
            return random.choice(tiles)
        return tiles[variant % len(tiles)]

    def get_ground_tile_for_position(self, category, x, y):
        """
        Get a deterministic ground tile for a position (for consistent rendering).

        Args:
            category: Tile category
            x, y: Grid position

        Returns:
            pygame.Surface or None
        """
        if category not in self.ground_tiles:
            return None

        tiles = self.ground_tiles[category]
        if not tiles:
            return None

        # Use position to determine variant (deterministic)
        variant = (x * 7 + y * 13) % len(tiles)
        return tiles[variant]

    def get_building(self, building_type, variant=0):
        """
        Get a building sprite.

        Args:
            building_type: Building type ('yellow', 'blue', 'brown', 'light_brown')
            variant: Specific variant index

        Returns:
            pygame.Surface or None
        """
        if building_type not in self.buildings:
            return None

        buildings = self.buildings[building_type]
        if not buildings:
            return None

        return buildings[variant % len(buildings)]

    def get_prop(self, prop_type, variant=None):
        """
        Get a prop sprite.

        Args:
            prop_type: Prop type ('trees', 'vehicles', etc.)
            variant: Specific variant index, or None for random

        Returns:
            pygame.Surface or None
        """
        if prop_type not in self.props:
            return None

        props = self.props[prop_type]
        if not props:
            return None

        if variant is None:
            return random.choice(props)
        return props[variant % len(props)]

    def get_building_footprint(self, building_sprite):
        """
        Calculate the footprint (in tiles) of a building sprite.

        Args:
            building_sprite: pygame.Surface of the building

        Returns:
            tuple: (width_tiles, height_tiles)
        """
        if building_sprite is None:
            return (1, 1)

        # Buildings are typically multiple tiles wide
        width = building_sprite.get_width()
        height = building_sprite.get_height()

        # Estimate footprint based on sprite size
        # Buildings are usually 2-3 tiles wide and tall
        width_tiles = max(1, width // ISO_TILE_WIDTH + 1)
        height_tiles = max(1, height // ISO_TILE_HEIGHT)

        return (width_tiles, height_tiles)


# Singleton instance
_isometric_tile_manager = None


def get_isometric_tile_manager():
    """Get or create the singleton IsometricTileManager instance."""
    global _isometric_tile_manager
    if _isometric_tile_manager is None:
        _isometric_tile_manager = IsometricTileManager()
    return _isometric_tile_manager

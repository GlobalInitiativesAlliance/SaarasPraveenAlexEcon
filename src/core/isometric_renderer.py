"""
Isometric Renderer

Handles rendering of the isometric exterior view with proper depth sorting.
"""

import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_HEIGHT,
    ISO_TILE_WIDTH, ISO_TILE_HEIGHT, ISOMETRIC_MODE
)
from src.core.isometric import (
    cart_to_iso, get_tile_screen_pos, get_visible_tiles,
    get_depth_value, ISO_TILE_HALF_WIDTH, ISO_TILE_HALF_HEIGHT
)
from src.core.isometric_tile_manager import get_isometric_tile_manager


class IsometricRenderer:
    """Renders the isometric exterior view."""

    # Layer constants for depth sorting
    LAYER_GROUND = 0
    LAYER_BUILDING = 1
    LAYER_PLAYER = 2
    LAYER_PROP = 3

    def __init__(self, isometric_map):
        """
        Initialize the isometric renderer.

        Args:
            isometric_map: IsometricCityMap instance to render
        """
        self.iso_map = isometric_map
        self.tile_manager = get_isometric_tile_manager()

        # Camera offset in screen pixels
        self.camera_x = 0
        self.camera_y = 0

        # Screen dimensions for rendering
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT - UI_HEIGHT

        # Cached ground surface for performance
        self._ground_cache = None
        self._ground_cache_valid = False

        # Debug rendering options
        self.debug_grid = False
        self.debug_coords = False

    def initialize(self):
        """Initialize the renderer after pygame is ready."""
        self.tile_manager.load_all()
        print("[ISOMETRIC_RENDERER] Initialized with tile manager")

    def update_camera(self, player_x, player_y):
        """
        Update camera position to follow player.

        Args:
            player_x, player_y: Player grid coordinates
        """
        # Convert player position to screen coordinates
        target_iso_x, target_iso_y = cart_to_iso(player_x, player_y)

        # Center camera on player
        self.camera_x = target_iso_x - self.screen_width // 2
        self.camera_y = target_iso_y - self.screen_height // 2

    def get_screen_offset(self):
        """Get the screen offset for centering the map."""
        # Center the map on screen
        return self.screen_width // 2, 0

    def render(self, screen, player):
        """
        Render the isometric view.

        Args:
            screen: pygame.Surface to render to
            player: Player object with x, y, pixel_x, pixel_y attributes
        """
        # Get screen offset for centering
        offset_x, offset_y = self.get_screen_offset()

        # Collect all renderable objects with depth values
        render_list = []

        # 1. Add ground tiles
        self._collect_ground_tiles(render_list, offset_x, offset_y)

        # 2. Add buildings
        self._collect_buildings(render_list, offset_x, offset_y)

        # 3. Add player
        self._collect_player(render_list, player, offset_x, offset_y)

        # 4. Add props
        self._collect_props(render_list, offset_x, offset_y)

        # Sort by depth (lower depth values drawn first)
        render_list.sort(key=lambda item: item[0])

        # Render all items
        for depth, sprite, screen_x, screen_y in render_list:
            if sprite is not None:
                screen.blit(sprite, (screen_x, screen_y))

        # Debug rendering
        if self.debug_grid:
            self._render_debug_grid(screen, offset_x, offset_y)

    def _collect_ground_tiles(self, render_list, offset_x, offset_y):
        """Collect ground tiles for rendering."""
        for y in range(self.iso_map.height):
            for x in range(self.iso_map.width):
                tile_info = self.iso_map.get_ground_tile(x, y)
                if tile_info is None:
                    continue

                tile_type = tile_info.get('type', 'grass')
                variant = tile_info.get('variant')

                # Get sprite from tile manager
                if variant is not None:
                    sprite = self.tile_manager.get_ground_tile(tile_type, variant)
                else:
                    sprite = self.tile_manager.get_ground_tile_for_position(tile_type, x, y)

                if sprite is None:
                    continue

                # Calculate screen position
                screen_x, screen_y = get_tile_screen_pos(x, y, self.camera_x, self.camera_y)
                screen_x += offset_x
                screen_y += offset_y

                # Check if visible on screen
                if self._is_visible(screen_x, screen_y, sprite.get_width(), sprite.get_height()):
                    depth = get_depth_value(x, y, self.LAYER_GROUND)
                    render_list.append((depth, sprite, screen_x, screen_y))

    def _collect_buildings(self, render_list, offset_x, offset_y):
        """Collect buildings for rendering."""
        for (bx, by), building_info in self.iso_map.building_layer.items():
            building_type = building_info.get('type', 'yellow')
            variant = building_info.get('variant', 0)

            sprite = self.tile_manager.get_building(building_type, variant)
            if sprite is None:
                continue

            # Calculate screen position
            screen_x, screen_y = get_tile_screen_pos(bx, by, self.camera_x, self.camera_y)
            screen_x += offset_x
            screen_y += offset_y

            # Offset to account for building height (buildings are taller than tiles)
            sprite_height = sprite.get_height()
            screen_y -= (sprite_height - ISO_TILE_HEIGHT)

            # Check if visible
            if self._is_visible(screen_x, screen_y, sprite.get_width(), sprite_height):
                # Buildings are depth-sorted by their front edge
                depth = get_depth_value(bx, by + 2, self.LAYER_BUILDING)
                render_list.append((depth, sprite, screen_x, screen_y))

    def _collect_player(self, render_list, player, offset_x, offset_y):
        """Collect player for rendering."""
        # Get player's current animation frame
        current_anim = player.animations.get(player.current_animation)
        if not current_anim or not current_anim[player.animation_frame]:
            return

        sprite = current_anim[player.animation_frame]

        # Calculate player screen position based on pixel position
        # Convert pixel position to grid position for isometric conversion
        grid_x = player.pixel_x / player.tile_size
        grid_y = player.pixel_y / player.tile_size

        iso_x, iso_y = cart_to_iso(grid_x, grid_y)
        screen_x = iso_x - self.camera_x + offset_x - sprite.get_width() // 2
        screen_y = iso_y - self.camera_y + offset_y - sprite.get_height() + ISO_TILE_HALF_HEIGHT

        depth = get_depth_value(grid_x, grid_y, self.LAYER_PLAYER)
        render_list.append((depth, sprite, screen_x, screen_y))

    def _collect_props(self, render_list, offset_x, offset_y):
        """Collect props for rendering."""
        for (px, py), prop_info in self.iso_map.prop_layer.items():
            prop_type = prop_info.get('type', 'trees')
            variant = prop_info.get('variant')

            sprite = self.tile_manager.get_prop(prop_type, variant)
            if sprite is None:
                continue

            # Calculate screen position
            screen_x, screen_y = get_tile_screen_pos(px, py, self.camera_x, self.camera_y)
            screen_x += offset_x
            screen_y += offset_y

            # Offset for prop height
            sprite_height = sprite.get_height()
            screen_y -= (sprite_height - ISO_TILE_HEIGHT)

            # Check if visible
            if self._is_visible(screen_x, screen_y, sprite.get_width(), sprite_height):
                depth = get_depth_value(px, py, self.LAYER_PROP)
                render_list.append((depth, sprite, screen_x, screen_y))

    def _is_visible(self, screen_x, screen_y, width, height):
        """Check if a sprite is visible on screen."""
        return (screen_x + width > 0 and
                screen_x < self.screen_width and
                screen_y + height > 0 and
                screen_y < self.screen_height)

    def _render_debug_grid(self, screen, offset_x, offset_y):
        """Render debug grid lines."""
        grid_color = (100, 100, 100, 128)

        for y in range(self.iso_map.height + 1):
            for x in range(self.iso_map.width + 1):
                # Get tile corners
                iso_x, iso_y = cart_to_iso(x, y)
                sx = int(iso_x - self.camera_x + offset_x)
                sy = int(iso_y - self.camera_y + offset_y)

                # Draw lines to adjacent tiles
                if x < self.iso_map.width:
                    next_x, next_y = cart_to_iso(x + 1, y)
                    nx = int(next_x - self.camera_x + offset_x)
                    ny = int(next_y - self.camera_y + offset_y)
                    pygame.draw.line(screen, grid_color, (sx, sy), (nx, ny), 1)

                if y < self.iso_map.height:
                    next_x, next_y = cart_to_iso(x, y + 1)
                    nx = int(next_x - self.camera_x + offset_x)
                    ny = int(next_y - self.camera_y + offset_y)
                    pygame.draw.line(screen, grid_color, (sx, sy), (nx, ny), 1)

    def screen_to_tile(self, screen_x, screen_y):
        """
        Convert screen coordinates to tile coordinates.

        Args:
            screen_x, screen_y: Screen position (e.g., mouse position)

        Returns:
            tuple: (tile_x, tile_y) or None if outside map
        """
        offset_x, offset_y = self.get_screen_offset()

        # Convert to world coordinates
        world_x = screen_x - offset_x + self.camera_x
        world_y = screen_y - offset_y + self.camera_y

        # Convert to isometric grid coordinates
        from src.core.isometric import iso_to_cart
        cart_x, cart_y = iso_to_cart(world_x + ISO_TILE_HALF_WIDTH, world_y)

        tile_x = int(cart_x)
        tile_y = int(cart_y)

        if 0 <= tile_x < self.iso_map.width and 0 <= tile_y < self.iso_map.height:
            return tile_x, tile_y
        return None

    def get_building_at_screen(self, screen_x, screen_y):
        """
        Get building info at screen position if any.

        Args:
            screen_x, screen_y: Screen position

        Returns:
            dict or None: Building info if found
        """
        tile_pos = self.screen_to_tile(screen_x, screen_y)
        if tile_pos is None:
            return None

        tx, ty = tile_pos

        # Check if this is an entry point
        entry_building = self.iso_map.get_entry_point(tx, ty)
        if entry_building:
            return entry_building

        # Check nearby tiles for building footprints
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                bx, by = tx + dx, ty + dy
                building = self.iso_map.get_building(bx, by)
                if building:
                    return building

        return None

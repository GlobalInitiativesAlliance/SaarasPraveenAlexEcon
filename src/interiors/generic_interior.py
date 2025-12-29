"""
Generic Interior - Loads and displays custom interior rooms created with interior_room_builder
"""
import pygame
import os
import math
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.interiors.zone_system import ZoneSystem
from src.interiors.zone_types import ZoneType
from src.interiors.wall_generator import WallGenerator
from src.interiors.collision_shapes import (
    CollisionShape, ShapeType, check_collision as shape_check_collision,
    circle_vs_circle, circle_vs_rect
)
from src.interiors.furniture_colliders import get_collider_for_tile, is_flat_tile

class GenericInterior:
    def __init__(self, game, room_data, building_pos):
        self.game = game
        self.room_data = room_data
        self.building_pos = building_pos
        self.active = True  # Interior is active when created

        # Room dimensions
        self.room_width = room_data.get('width', 16)
        self.room_height = room_data.get('height', 12)

        # Constants (moved earlier so they're available)
        self.TILE_SIZE = 32
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        # Handle multi-floor rooms (version 2+)
        if room_data.get('version', 1) >= 2 and 'floors' in room_data:
            # Extract layers from the first floor (ground floor)
            if room_data['floors'] and len(room_data['floors']) > 0:
                self.layers = room_data['floors'][0].get('layers', {})
            else:
                self.layers = {}
        else:
            # Backward compatibility with old format
            self.layers = room_data.get('layers', {})

        # Sync room dimensions with actual floor layer size to fix boundary mismatches
        # This ensures the player bounds match the visible floor area
        # IMPORTANT: Use MINIMUM of declared vs actual to prevent player escaping visible area
        floor_layer = self.layers.get('floor', [])
        if floor_layer:
            actual_height = len(floor_layer)
            actual_width = len(floor_layer[0]) if floor_layer else 0
            if actual_height != self.room_height or actual_width != self.room_width:
                print(f"[INTERIOR_WARNING] Room dimension mismatch! JSON: {self.room_width}x{self.room_height}, Floor layer: {actual_width}x{actual_height}")
                # Use MINIMUM to ensure player stays within visible floor area
                self.room_height = min(actual_height, self.room_height)
                self.room_width = min(actual_width, self.room_width)
                print(f"[INTERIOR] Using safe dimensions: {self.room_width}x{self.room_height}")

        self.doors = room_data.get('doors', [])

        # Player state - use tile coordinates for logic
        self.player_tile_x = self.room_width // 2
        self.player_tile_y = self.room_height - 2

        # Use pixel coordinates for smooth movement (matching exterior)
        self.player_pixel_x = float(self.player_tile_x * self.TILE_SIZE)
        self.player_pixel_y = float(self.player_tile_y * self.TILE_SIZE)
        self.target_pixel_x = self.player_pixel_x
        self.target_pixel_y = self.player_pixel_y

        # Movement state
        self.player_direction = 'down'  # Track player direction
        self.player_walking = False  # Track if player is walking
        self.is_moving = False
        self.move_speed = 3.0  # Pixels per frame for smooth movement

        # Pixel-based collision settings
        # Player uses a small CIRCLE collider at feet (smoother than rectangle)
        self.player_collision_radius = 8  # Small circle radius for smooth collision
        self.player_collision_offset_x = self.TILE_SIZE // 2  # Center of sprite
        self.player_collision_offset_y = self.TILE_SIZE - 6   # Near feet

        # Legacy rectangle settings (for backward compatibility)
        self.player_collision_width = 20
        self.player_collision_height = 12

        # Build collision shapes from furniture tiles
        self.collision_shapes = []  # New: shape-based collision
        self.collision_rects = []   # Legacy: kept for compatibility

        # Debug mode for collision visualization
        self.debug_collision = False

        # Animation state
        self.animation_timer = 0
        self.animation_frame = 0
        self.animation_speed = 0.08  # Match exterior animation speed

        # If doors exist, spawn above the first door
        if self.doors and len(self.doors) > 0:
            first_door = self.doors[0]
            if isinstance(first_door, list) and len(first_door) >= 2:
                self.player_tile_x = first_door[0]
                self.player_tile_y = first_door[1] - 1  # Spawn one tile above the door
                # Update pixel coordinates
                self.player_pixel_x = float(self.player_tile_x * self.TILE_SIZE)
                self.player_pixel_y = float(self.player_tile_y * self.TILE_SIZE)
                self.target_pixel_x = self.player_pixel_x
                self.target_pixel_y = self.player_pixel_y

        # SAFETY: Clamp initial spawn position to room bounds
        self.player_pixel_x, self.player_pixel_y = self.clamp_position(
            self.player_pixel_x, self.player_pixel_y
        )
        self.target_pixel_x = self.player_pixel_x
        self.target_pixel_y = self.player_pixel_y
        # Update tile position
        self.player_tile_x = int(self.player_pixel_x / self.TILE_SIZE)
        self.player_tile_y = int(self.player_pixel_y / self.TILE_SIZE)

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Calculate room offset for centering
        self.calculate_room_offset()

        # Get player sprite from game if available
        self.player_sprite = None
        if hasattr(self.game, 'player'):
            self.player_sprite = self.game.player

        # Load sprite sheets
        self.load_sprites()

        # Initialize zone system for collision/interaction
        self.zone_system = ZoneSystem(self.room_width, self.room_height)
        self._build_zone_map()

        # Auto-generate walls if enabled
        self.auto_walls_layer = None
        self._setup_auto_walls()

    def load_sprites(self):
        """Load sprite sheets for rendering"""
        self.sheets = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Try to load common interior sprite sheets
        sheet_paths = [
            ("Interiors_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Interiors_16x16.png"),
            ("Room_Builder_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_16x16.png"),
            ("1_Generic_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/1_Generic_16x16.png"),
            ("2_LivingRoom_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/2_LivingRoom_16x16.png"),
            ("3_Bathroom_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/3_Bathroom_16x16.png"),
            ("4_Bedroom_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/4_Bedroom_16x16.png"),
            ("5_Classroom_and_library_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/5_Classroom_and_library_16x16.png"),
            ("12_Kitchen_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/12_Kitchen_16x16.png"),
            ("16_Grocery_store_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter/16_Grocery_store_16x16.png"),
        ]

        for sheet_name, relative_path in sheet_paths:
            full_path = os.path.join(base_dir, relative_path)
            if os.path.exists(full_path):
                try:
                    self.sheets[sheet_name] = pygame.image.load(full_path).convert_alpha()
                    print(f"Loaded sheet: {sheet_name}")
                except Exception as e:
                    print(f"Error loading {sheet_name}: {e}")

        # Also load wall generator sprites
        wall_sheets = [
            ("Room_Builder_Walls_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Walls_16x16.png"),
            ("Room_Builder_Floor_Shadows_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Floor_Shadows_16x16.png"),
            ("Room_Builder_Baseboards_16x16.png", "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Baseboards_16x16.png"),
        ]
        for sheet_name, relative_path in wall_sheets:
            full_path = os.path.join(base_dir, relative_path)
            if os.path.exists(full_path):
                try:
                    self.sheets[sheet_name] = pygame.image.load(full_path).convert_alpha()
                except Exception as e:
                    print(f"Error loading wall sheet {sheet_name}: {e}")

    def _build_zone_map(self):
        """Build zone map from room layers"""
        # Build from room data (layers + doors)
        room_data_for_zones = {'layers': self.layers}
        self.zone_system.build_from_room_data(room_data_for_zones, self.doors)

        # Note: Out-of-bounds checking is handled by zone_map.get_zone() returning BOUNDARY
        # for coordinates outside (0 to width-1, 0 to height-1). We don't need to block
        # the perimeter tiles unless they have walls/furniture on them.

        # Build collision shapes from furniture tiles (professional shape-based system)
        self._build_collision_shapes()

        # Also build legacy collision rects for compatibility
        self._build_collision_rects()

        # Build furniture groups for Y-sorting (depth rendering)
        self._build_furniture_groups()

    def _build_collision_shapes(self):
        """Build collision shapes from furniture tiles.

        Uses the professional shape-based collision system:
        - Round furniture gets circle colliders
        - Rectangular furniture gets smaller rectangle colliders
        - Flat tiles (floor, rugs) have no collision

        This provides smooth, pixel-accurate collision detection.
        """
        self.collision_shapes = []

        # Process furniture and decor layers
        for layer_name in ['furniture', 'decor']:
            if layer_name not in self.layers:
                continue

            layer = self.layers[layer_name]
            for y, row in enumerate(layer):
                for x, tile_info in enumerate(row):
                    if tile_info and not is_flat_tile(tile_info):
                        shape = get_collider_for_tile(tile_info, x, y)
                        if shape:
                            self.collision_shapes.append(shape)

        print(f"[COLLISION] Built {len(self.collision_shapes)} collision shapes")

    def _build_furniture_groups(self):
        """Build furniture groups for Y-sorted rendering.

        Groups connected furniture/decor tiles so they render as a unit.
        Each group is sorted by its bottom-most Y position (the "foot").

        This enables proper depth sorting - characters can walk behind
        tall furniture when above it, and in front when below.
        """
        self.furniture_groups = []
        processed = set()

        # Process furniture and decor layers
        for layer_name in ['furniture', 'decor']:
            if layer_name not in self.layers:
                continue

            layer = self.layers[layer_name]
            for y, row in enumerate(layer):
                for x, tile_info in enumerate(row):
                    if tile_info and (layer_name, x, y) not in processed:
                        # Flood-fill to find connected tiles
                        group_tiles = []
                        stack = [(x, y)]

                        while stack:
                            tx, ty = stack.pop()
                            key = (layer_name, tx, ty)
                            if key in processed:
                                continue
                            if not (0 <= ty < len(layer) and 0 <= tx < len(layer[ty])):
                                continue
                            if layer[ty][tx] is None:
                                continue

                            processed.add(key)
                            group_tiles.append((tx, ty, layer[ty][tx]))

                            # Check 4 neighbors
                            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                                stack.append((tx + dx, ty + dy))

                        if group_tiles:
                            # Sort Y is the bottom of the group (highest Y value + 1 tile)
                            bottom_y = max(t[1] for t in group_tiles)
                            sort_y = (bottom_y + 1) * self.TILE_SIZE

                            self.furniture_groups.append({
                                'tiles': group_tiles,
                                'sort_y': sort_y,
                                'layer': layer_name
                            })

        print(f"[Y-SORT] Built {len(self.furniture_groups)} furniture groups for depth sorting")

    def _build_collision_rects(self):
        """Build pixel-based collision rectangles using bounding boxes for furniture groups.

        This approach:
        1. Finds all BLOCKED tiles (furniture, not boundaries)
        2. Groups connected tiles using flood-fill
        3. Creates a bounding box for each group (fills internal gaps)

        NOTE: BOUNDARY tiles (room edges) are NOT included here - they're
        handled by position clamping in clamp_position(). This prevents the
        room perimeter from forming one giant collision rect.
        """
        from src.interiors.zone_types import ZoneType

        self.collision_rects = []

        # Collect only BLOCKED tiles (furniture), NOT BOUNDARY tiles (room edges)
        # Boundaries are handled by position clamping, not collision rects
        blocked_tiles = set()
        for y in range(self.room_height):
            for x in range(self.room_width):
                zone = self.zone_system.get_zone_at(x, y)
                # Only include actual furniture/walls (BLOCKED), not room edges (BOUNDARY)
                if zone == ZoneType.BLOCKED:
                    blocked_tiles.add((x, y))

        # Find connected groups of blocked tiles using flood-fill
        processed = set()
        groups = []

        def flood_fill(start_x, start_y):
            """Find all tiles connected to start position (4-directional connectivity)

            Using 4-direction (not diagonal) prevents furniture pieces that are
            only diagonally adjacent from being merged into one collision group.
            """
            group = set()
            stack = [(start_x, start_y)]

            while stack:
                x, y = stack.pop()
                if (x, y) in group or (x, y) not in blocked_tiles:
                    continue

                group.add((x, y))

                # Check 4 neighbors (up, down, left, right - no diagonals)
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in blocked_tiles and (nx, ny) not in group:
                        stack.append((nx, ny))

            return group

        # Find all groups
        for (x, y) in blocked_tiles:
            if (x, y) not in processed:
                group = flood_fill(x, y)
                if group:
                    groups.append(group)
                    processed.update(group)

        # Create bounding box collision rect for each group
        # Small padding allows player to walk next to furniture without clipping
        padding = 4

        for group in groups:
            if not group:
                continue

            # Find bounding box of the group
            min_x = min(x for x, y in group)
            max_x = max(x for x, y in group)
            min_y = min(y for x, y in group)
            max_y = max(y for x, y in group)

            # Create collision rect with padding for clearance
            # This automatically fills any internal gaps in the furniture
            rect = pygame.Rect(
                min_x * self.TILE_SIZE + padding,
                min_y * self.TILE_SIZE + padding,
                (max_x - min_x + 1) * self.TILE_SIZE - padding * 2,
                (max_y - min_y + 1) * self.TILE_SIZE - padding * 2
            )
            self.collision_rects.append(rect)

        # NOTE: Room boundaries are handled by hard clamping in handle_input,
        # NOT by collision rectangles. This is more reliable.

    def get_room_bounds(self):
        """Get the valid pixel bounds for player position.

        Uses actual room dimensions - boundaries are handled by the zone system
        (mark_boundary marks room edges as BLOCKED, except at door positions).

        The player sprite (32x32) position is top-left, so we account for that.
        Small edge padding prevents visual clipping at room edges.
        """
        # Small padding to prevent visual clipping at edges
        edge_padding = 4

        # Calculate room pixel dimensions
        room_pixel_width = self.room_width * self.TILE_SIZE
        room_pixel_height = self.room_height * self.TILE_SIZE

        # Player position is top-left of sprite (32x32)
        # Allow walking to actual room edges (zone system handles boundaries)
        min_x = edge_padding
        min_y = edge_padding
        max_x = room_pixel_width - self.TILE_SIZE - edge_padding
        # Allow player to reach bottom edge - zone system handles blocking
        # Player at y=max_y has feet at y+24, which is near the room bottom
        max_y = room_pixel_height - self.TILE_SIZE - edge_padding

        return min_x, min_y, max_x, max_y

    def clamp_position(self, x, y):
        """Clamp position to valid room bounds - this is the safety net"""
        min_x, min_y, max_x, max_y = self.get_room_bounds()
        clamped_x = max(min_x, min(x, max_x))
        clamped_y = max(min_y, min(y, max_y))
        return clamped_x, clamped_y

    def get_player_collision_rect(self, px=None, py=None):
        """Get the player's collision rectangle at given position (legacy, for compatibility)"""
        if px is None:
            px = self.player_pixel_x
        if py is None:
            py = self.player_pixel_y
        return pygame.Rect(
            px + self.player_collision_offset_x - self.player_collision_width // 2,
            py + self.player_collision_offset_y - self.player_collision_height // 2,
            self.player_collision_width,
            self.player_collision_height
        )

    def get_player_collision_circle(self, px=None, py=None):
        """Get the player's collision circle at given position.

        Returns a CollisionShape (circle) centered at the player's feet.
        This provides smoother collision than rectangles.
        """
        if px is None:
            px = self.player_pixel_x
        if py is None:
            py = self.player_pixel_y

        return CollisionShape(
            shape_type=ShapeType.CIRCLE,
            x=px + self.player_collision_offset_x,
            y=py + self.player_collision_offset_y,
            width=self.player_collision_radius  # radius
        )

    def check_collision(self, new_x, new_y):
        """Check if player would collide at the given pixel position.

        Uses simple pygame.Rect AABB collision - the industry standard.
        Player has a small rectangle at feet for smooth movement.
        """
        # Player collision box: small rectangle at feet
        # Much smaller than sprite to prevent "sticky" feeling
        player_rect = pygame.Rect(
            new_x + 8,              # Centered horizontally (8px padding on 32px tile)
            new_y + 24,             # At feet (bottom 8px of 32px sprite)
            16,                     # 16px wide (half tile width)
            6                       # 6px tall (just feet)
        )

        # Check against collision rectangles (simple AABB)
        for rect in self.collision_rects:
            if player_rect.colliderect(rect):
                return True

        return False

    def _get_extra_sortable_entities(self, offset_x, offset_y):
        """Hook for subclasses to add extra entities to Y-sorting.

        Override this in subclasses to add NPCs, items, etc. to the
        depth-sorted rendering.

        Returns:
            list: List of entity dicts with 'type', 'sort_y', and optional 'draw_func'
        """
        return []

    def _setup_auto_walls(self):
        """Set up auto-generated walls if enabled in room config"""
        wall_config = self.room_data.get('wall_config', {})

        # Check if auto-walls are enabled (default: False until wall tiles are properly mapped)
        if wall_config.get('enabled', False):
            style = wall_config.get('style', 'modern')
            generator = WallGenerator(style)

            # Generate walls around perimeter
            self.auto_walls_layer = generator.generate_walls(
                self.room_width,
                self.room_height,
                self.doors,
                include_bottom=False  # Usually don't include bottom (exit area)
            )

            # Merge with existing walls if any
            existing_walls = self.layers.get('walls', [])
            if existing_walls:
                self.auto_walls_layer = generator.merge_walls_with_existing(
                    self.auto_walls_layer,
                    existing_walls
                )

    def calculate_room_offset(self):
        """Calculate room offset for centering"""
        # Calculate room dimensions in pixels
        room_pixel_width = self.room_width * self.TILE_SIZE
        room_pixel_height = self.room_height * self.TILE_SIZE

        # Center the room on screen
        self.room_offset_x = (self.SCREEN_WIDTH - room_pixel_width) // 2
        self.room_offset_y = (self.SCREEN_HEIGHT - room_pixel_height) // 2

    def get_tile_surface(self, tile_info):
        """Get a tile surface from the sprite sheets"""
        if not tile_info or not isinstance(tile_info, list) or len(tile_info) < 3:
            return None

        sheet_name, x, y = tile_info
        if sheet_name not in self.sheets:
            return None

        sheet = self.sheets[sheet_name]
        try:
            # Original tiles are 16x16
            src_rect = pygame.Rect(x * 16, y * 16, 16, 16)
            if src_rect.right <= sheet.get_width() and src_rect.bottom <= sheet.get_height():
                tile = sheet.subsurface(src_rect)
                # Scale to display size
                return pygame.transform.scale(tile, (self.TILE_SIZE, self.TILE_SIZE))
        except Exception as e:
            print(f"Error getting tile surface: {e}")
        return None

    def enter(self):
        """Enter the interior"""
        min_x, min_y, max_x, max_y = self.get_room_bounds()
        print(f"Entered generic interior room: {self.room_width}x{self.room_height}")
        print(f"  Player position: ({self.player_pixel_x}, {self.player_pixel_y})")
        print(f"  Room bounds: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
        print(f"  Player tile: ({self.player_tile_x}, {self.player_tile_y})")

    def exit(self):
        """Exit the interior and return to the main game"""
        print("Exiting interior...")
        # Return player to position near the building
        if self.building_pos:
            # Place player just below the building (positions are already in tiles)
            self.game.player.x = self.building_pos[0] + 1
            self.game.player.y = self.building_pos[1] + 2
            # Update player's pixel position to match
            self.game.player.pixel_x = float(self.game.player.x * self.game.player.tile_size)
            self.game.player.pixel_y = float(self.game.player.y * self.game.player.tile_size)
            self.game.player.target_x = self.game.player.pixel_x
            self.game.player.target_y = self.game.player.pixel_y
        self.game.current_interior = None
        self.active = False

    def handle_event(self, event):
        """Handle events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_F3:
                # Toggle collision debug visualization
                self.debug_collision = not self.debug_collision
                print(f"Collision debug: {'ON' if self.debug_collision else 'OFF'}")
            elif event.key == pygame.K_e:
                # Check if player is at a door to exit
                current_tile_x = int(self.player_pixel_x / self.TILE_SIZE)
                current_tile_y = int(self.player_pixel_y / self.TILE_SIZE)

                # Check explicit door positions
                for door in self.doors:
                    if isinstance(door, list) and len(door) >= 2:
                        door_x, door_y = door[0], door[1]
                        if abs(current_tile_x - door_x) <= 1 and abs(current_tile_y - door_y) <= 1:
                            self.exit()
                            return

                # Fallback: allow exit from bottom row if no doors defined
                if not self.doors and current_tile_y >= self.room_height - 2:
                    self.exit()
                    return

    def handle_input(self, keys):
        """Handle continuous input for pixel-based movement"""
        # Calculate movement vector
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.move_speed
            self.player_direction = 'up'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.move_speed
            self.player_direction = 'down'

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.move_speed
            self.player_direction = 'left'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.move_speed
            self.player_direction = 'right'

        # If there's movement input
        if dx != 0 or dy != 0:
            self.player_walking = True

            # Try horizontal movement first
            if dx != 0:
                new_x = self.player_pixel_x + dx
                if not self.check_collision(new_x, self.player_pixel_y):
                    self.player_pixel_x = new_x
                else:
                    # Slide along obstacle - try smaller steps
                    for step in range(int(abs(dx)), 0, -1):
                        test_x = self.player_pixel_x + (step if dx > 0 else -step)
                        if not self.check_collision(test_x, self.player_pixel_y):
                            self.player_pixel_x = test_x
                            break

            # Try vertical movement
            if dy != 0:
                new_y = self.player_pixel_y + dy
                if not self.check_collision(self.player_pixel_x, new_y):
                    self.player_pixel_y = new_y
                else:
                    # Slide along obstacle - try smaller steps
                    for step in range(int(abs(dy)), 0, -1):
                        test_y = self.player_pixel_y + (step if dy > 0 else -step)
                        if not self.check_collision(self.player_pixel_x, test_y):
                            self.player_pixel_y = test_y
                            break

        # CRITICAL: Always clamp position to room bounds - this is the safety net
        # This ensures player can NEVER escape the room, regardless of collision detection
        self.player_pixel_x, self.player_pixel_y = self.clamp_position(
            self.player_pixel_x, self.player_pixel_y
        )

        # Update tile position for compatibility
        self.player_tile_x = int(self.player_pixel_x / self.TILE_SIZE)
        self.player_tile_y = int(self.player_pixel_y / self.TILE_SIZE)

        if dx == 0 and dy == 0:
            self.player_walking = False

    def update(self, dt):
        """Update interior state"""
        # Movement is now handled in handle_input() with pixel-based collision
        # No longer need tile-based target movement

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.player_sprite and hasattr(self.player_sprite, 'animations'):
                anim_name = f'walk_{self.player_direction}' if self.player_walking else f'idle_{self.player_direction}'
                if anim_name in self.player_sprite.animations:
                    frames = self.player_sprite.animations[anim_name]
                    if frames:
                        self.animation_frame = (self.animation_frame + 1) % len(frames)
                    else:
                        self.animation_frame = 0
                else:
                    self.animation_frame = 0
            else:
                if self.player_walking:
                    self.animation_frame = (self.animation_frame + 1) % 2
                else:
                    self.animation_frame = 0

        # For small rooms that fit on screen, don't use camera scrolling
        room_pixel_width = self.room_width * self.TILE_SIZE
        room_pixel_height = self.room_height * self.TILE_SIZE

        if room_pixel_width <= self.SCREEN_WIDTH and room_pixel_height <= self.SCREEN_HEIGHT:
            # Center the room, no scrolling
            self.camera_x = 0
            self.camera_y = 0
        else:
            # Update camera to follow player for larger rooms
            self.camera_x = int(self.player_pixel_x - self.SCREEN_WIDTH // 2)
            self.camera_y = int(self.player_pixel_y - self.SCREEN_HEIGHT // 2)

            # Clamp camera
            max_camera_x = room_pixel_width - self.SCREEN_WIDTH
            max_camera_y = room_pixel_height - self.SCREEN_HEIGHT

            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def draw(self, screen):
        """Draw the interior"""
        # Fill background
        screen.fill((40, 40, 40))

        # Calculate room dimensions in pixels
        room_pixel_width = self.room_width * self.TILE_SIZE
        room_pixel_height = self.room_height * self.TILE_SIZE

        # Always center the room on screen
        offset_x = (self.SCREEN_WIDTH - room_pixel_width) // 2
        offset_y = (self.SCREEN_HEIGHT - room_pixel_height) // 2

        # Draw floor layer first (no grid)
        if 'floor' in self.layers:
            layer = self.layers['floor']
            for y, row in enumerate(layer):
                for x, tile_info in enumerate(row):
                    if tile_info:
                        tile_surf = self.get_tile_surface(tile_info)
                        if tile_surf:
                            screen_x = x * self.TILE_SIZE - self.camera_x + offset_x
                            screen_y = y * self.TILE_SIZE - self.camera_y + offset_y

                            # Only draw if on screen
                            if -self.TILE_SIZE <= screen_x <= self.SCREEN_WIDTH and \
                               -self.TILE_SIZE <= screen_y <= self.SCREEN_HEIGHT:
                                screen.blit(tile_surf, (screen_x, screen_y))

        # Draw auto-generated walls first (perimeter walls)
        if self.auto_walls_layer:
            for y, row in enumerate(self.auto_walls_layer):
                for x, tile_info in enumerate(row):
                    if tile_info:
                        tile_surf = self.get_tile_surface(tile_info)
                        if tile_surf:
                            screen_x = x * self.TILE_SIZE - self.camera_x + offset_x
                            screen_y = y * self.TILE_SIZE - self.camera_y + offset_y

                            # Only draw if on screen
                            if -self.TILE_SIZE <= screen_x <= self.SCREEN_WIDTH and \
                               -self.TILE_SIZE <= screen_y <= self.SCREEN_HEIGHT:
                                screen.blit(tile_surf, (screen_x, screen_y))

        # Draw walls layer (usually flat against walls, always behind characters)
        if 'walls' in self.layers:
            layer = self.layers['walls']
            for y, row in enumerate(layer):
                for x, tile_info in enumerate(row):
                    if tile_info:
                        tile_surf = self.get_tile_surface(tile_info)
                        if tile_surf:
                            screen_x = x * self.TILE_SIZE - self.camera_x + offset_x
                            screen_y = y * self.TILE_SIZE - self.camera_y + offset_y
                            if -self.TILE_SIZE <= screen_x <= self.SCREEN_WIDTH and \
                               -self.TILE_SIZE <= screen_y <= self.SCREEN_HEIGHT:
                                screen.blit(tile_surf, (screen_x, screen_y))

        # === Y-SORTED RENDERING ===
        # Collect all entities that need depth sorting
        sortable_entities = []

        # Add furniture groups
        for group in self.furniture_groups:
            sortable_entities.append({
                'type': 'furniture',
                'sort_y': group['sort_y'],
                'data': group
            })

        # Add player
        # Player sort_y is bottom of sprite (feet position)
        player_sort_y = self.player_pixel_y + self.TILE_SIZE
        sortable_entities.append({
            'type': 'player',
            'sort_y': player_sort_y,
            'data': None
        })

        # Add extra entities from subclasses (NPCs, etc.)
        sortable_entities.extend(self._get_extra_sortable_entities(offset_x, offset_y))

        # Sort all entities by Y (top to bottom = back to front)
        sortable_entities.sort(key=lambda e: e['sort_y'])

        # Draw in sorted order
        for entity in sortable_entities:
            if entity['type'] == 'furniture':
                # Draw all tiles in this furniture group
                group = entity['data']
                for tx, ty, tile_info in group['tiles']:
                    tile_surf = self.get_tile_surface(tile_info)
                    if tile_surf:
                        screen_x = tx * self.TILE_SIZE - self.camera_x + offset_x
                        screen_y = ty * self.TILE_SIZE - self.camera_y + offset_y
                        if -self.TILE_SIZE <= screen_x <= self.SCREEN_WIDTH and \
                           -self.TILE_SIZE <= screen_y <= self.SCREEN_HEIGHT:
                            screen.blit(tile_surf, (screen_x, screen_y))

            elif entity['type'] == 'player':
                # SAFETY: Ensure player position is clamped before drawing
                # This catches any edge cases where position might have escaped bounds
                clamped_x, clamped_y = self.clamp_position(self.player_pixel_x, self.player_pixel_y)
                if clamped_x != self.player_pixel_x or clamped_y != self.player_pixel_y:
                    print(f"[INTERIOR_WARNING] Player out of bounds! Clamping from ({self.player_pixel_x}, {self.player_pixel_y}) to ({clamped_x}, {clamped_y})")
                    self.player_pixel_x = clamped_x
                    self.player_pixel_y = clamped_y

                # Draw player
                player_screen_x = int(self.player_pixel_x - self.camera_x + offset_x)
                player_screen_y = int(self.player_pixel_y - self.camera_y + offset_y)

                if self.player_sprite and hasattr(self.player_sprite, 'animations'):
                    anim_name = f'walk_{self.player_direction}' if self.player_walking else f'idle_{self.player_direction}'
                    if anim_name in self.player_sprite.animations:
                        frames = self.player_sprite.animations[anim_name]
                        if frames and len(frames) > 0:
                            frame_index = min(self.animation_frame, len(frames) - 1)
                            screen.blit(frames[frame_index], (player_screen_x, player_screen_y))
                        else:
                            pygame.draw.circle(screen, (255, 255, 0),
                                             (player_screen_x + self.TILE_SIZE // 2,
                                              player_screen_y + self.TILE_SIZE // 2), 12)
                    else:
                        pygame.draw.circle(screen, (255, 255, 0),
                                         (player_screen_x + self.TILE_SIZE // 2,
                                          player_screen_y + self.TILE_SIZE // 2), 12)
                else:
                    pygame.draw.circle(screen, (255, 255, 0),
                                     (player_screen_x + self.TILE_SIZE // 2,
                                      player_screen_y + self.TILE_SIZE // 2), 12)
                    pygame.draw.circle(screen, (200, 200, 0),
                                     (player_screen_x + self.TILE_SIZE // 2,
                                      player_screen_y + self.TILE_SIZE // 2), 12, 2)

            elif entity['type'] == 'npc':
                # Draw NPC (handled by subclass via draw_func)
                draw_func = entity.get('draw_func')
                if draw_func:
                    draw_func(screen)

        # Draw door indicators (thin yellow arc outline)
        import math
        for door in self.doors:
            if isinstance(door, list) and len(door) >= 2:
                door_x, door_y = door[0], door[1]
                # Calculate door position on screen
                door_screen_x = door_x * self.TILE_SIZE - self.camera_x + offset_x
                door_screen_y = door_y * self.TILE_SIZE - self.camera_y + offset_y

                # Position arc exactly at the door tile
                center_x = door_screen_x + self.TILE_SIZE // 2
                center_y = door_screen_y + self.TILE_SIZE  # Exactly at bottom of door tile

                # Draw only the arc outline (not filled) - larger radius
                radius = int(self.TILE_SIZE * 0.85)

                # Draw arc as connected line segments
                points = []
                for angle in range(0, 181, 2):  # Semi-circle from 0 to 180 degrees
                    x = center_x + radius * math.cos(math.radians(angle))
                    y = center_y - radius * math.sin(math.radians(angle))  # Negative for upward arc
                    points.append((x, y))

                # Draw the arc outline only - no fill, no hover effect changes
                if len(points) > 1:
                    pygame.draw.lines(screen, (255, 220, 100, 100), False, points, 2)

        # Show contextual hint near door only (no permanent UI clutter)
        font = pygame.font.Font(None, 20)
        for door in self.doors:
            if isinstance(door, list) and len(door) >= 2:
                door_x, door_y = door[0], door[1]
                if abs(self.player_tile_x - door_x) <= 1 and abs(self.player_tile_y - door_y) <= 1:
                    # Draw subtle exit hint at bottom center
                    hint_text = "E to exit"
                    hint_surf = font.render(hint_text, True, (180, 200, 180))
                    hint_x = self.SCREEN_WIDTH // 2 - hint_surf.get_width() // 2
                    hint_y = self.SCREEN_HEIGHT - 40
                    # Draw background pill
                    pill_rect = pygame.Rect(hint_x - 12, hint_y - 4, hint_surf.get_width() + 24, hint_surf.get_height() + 8)
                    pill_surf = pygame.Surface((pill_rect.width, pill_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(pill_surf, (30, 35, 30, 200), pill_surf.get_rect(), border_radius=12)
                    screen.blit(pill_surf, pill_rect.topleft)
                    screen.blit(hint_surf, (hint_x, hint_y))
                    break

        # Debug: Draw collision boxes if enabled (press F3 to toggle)
        if self.debug_collision:
            # Draw furniture collision rectangles in red
            for rect in self.collision_rects:
                if rect.x >= 0 and rect.y >= 0:
                    screen_rect = pygame.Rect(
                        rect.x - self.camera_x + offset_x,
                        rect.y - self.camera_y + offset_y,
                        rect.width,
                        rect.height
                    )
                    debug_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(debug_surf, (255, 100, 100, 80), debug_surf.get_rect())
                    pygame.draw.rect(debug_surf, (255, 0, 0, 200), debug_surf.get_rect(), 2)
                    screen.blit(debug_surf, screen_rect.topleft)

            # Draw player collision box in green (small rect at feet)
            player_rect = pygame.Rect(
                self.player_pixel_x + 8,
                self.player_pixel_y + 24,
                16, 6
            )
            screen_player_rect = pygame.Rect(
                player_rect.x - self.camera_x + offset_x,
                player_rect.y - self.camera_y + offset_y,
                player_rect.width,
                player_rect.height
            )
            debug_surf = pygame.Surface((player_rect.width, player_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(debug_surf, (100, 255, 100, 150), debug_surf.get_rect())
            pygame.draw.rect(debug_surf, (0, 255, 0, 255), debug_surf.get_rect(), 2)
            screen.blit(debug_surf, screen_player_rect.topleft)

            # Draw room boundary outline in blue
            room_outline = pygame.Rect(
                offset_x,
                offset_y,
                self.room_width * self.TILE_SIZE,
                self.room_height * self.TILE_SIZE
            )
            pygame.draw.rect(screen, (0, 100, 255), room_outline, 2)

            # Show debug info
            debug_font = pygame.font.Font(None, 18)
            min_x, min_y, max_x, max_y = self.get_room_bounds()
            debug_info = [
                f"Player pos: ({self.player_pixel_x:.1f}, {self.player_pixel_y:.1f})",
                f"Player tile: ({self.player_tile_x}, {self.player_tile_y})",
                f"Player collider: 16x6 rect at feet",
                f"Room: {self.room_width}x{self.room_height} tiles",
                f"Collision rects: {len(self.collision_rects)}",
                "Press F3 to hide"
            ]
            for i, text in enumerate(debug_info):
                surf = debug_font.render(text, True, (255, 255, 0))
                screen.blit(surf, (10, 10 + i * 18))
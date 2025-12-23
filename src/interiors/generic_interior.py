"""
Generic Interior - Loads and displays custom interior rooms created with interior_room_builder
"""
import pygame
import os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.interiors.zone_system import ZoneSystem
from src.interiors.zone_types import ZoneType
from src.interiors.wall_generator import WallGenerator

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
        # Player collision box is smaller than sprite (just feet area)
        self.player_collision_width = 20  # Width of collision box
        self.player_collision_height = 12  # Height of collision box (feet only)
        self.player_collision_offset_x = (self.TILE_SIZE - self.player_collision_width) // 2  # Center horizontally
        self.player_collision_offset_y = self.TILE_SIZE - self.player_collision_height - 2  # At bottom of sprite

        # Build collision rectangles from blocked tiles
        self.collision_rects = []

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

        # Build pixel-based collision rectangles from blocked zones
        self._build_collision_rects()

    def _build_collision_rects(self):
        """Build pixel-based collision rectangles from blocked tiles (furniture only)"""
        self.collision_rects = []

        # First, collect all blocked tile positions
        blocked_tiles = set()
        for y in range(self.room_height):
            for x in range(self.room_width):
                if not self.zone_system.can_move_to(x, y):
                    blocked_tiles.add((x, y))

        # Merge adjacent tiles into larger rectangles (greedy algorithm)
        processed = set()

        for (x, y) in sorted(blocked_tiles):
            if (x, y) in processed:
                continue

            # Find the maximum width of this rectangle
            width = 1
            while (x + width, y) in blocked_tiles and (x + width, y) not in processed:
                width += 1

            # Find the maximum height that works for this width
            height = 1
            while True:
                can_extend = True
                for dx in range(width):
                    if (x + dx, y + height) not in blocked_tiles or (x + dx, y + height) in processed:
                        can_extend = False
                        break
                if can_extend:
                    height += 1
                else:
                    break

            # Mark all tiles in this rectangle as processed
            for dy in range(height):
                for dx in range(width):
                    processed.add((x + dx, y + dy))

            # Create collision rect with small padding for better feel
            padding = 2
            rect = pygame.Rect(
                x * self.TILE_SIZE + padding,
                y * self.TILE_SIZE + padding,
                width * self.TILE_SIZE - padding * 2,
                height * self.TILE_SIZE - padding * 2
            )
            self.collision_rects.append(rect)

        # NOTE: Room boundaries are handled by hard clamping in handle_input,
        # NOT by collision rectangles. This is more reliable.

    def get_room_bounds(self):
        """Get the valid pixel bounds for player position (hard limits)

        This uses simple, robust bounds:
        - Player sprite (top-left position) must stay within room
        - Small edge padding prevents player from touching the very edge
        """
        # Simple edge padding from room boundaries
        edge_padding = 4

        # Calculate room pixel dimensions
        room_pixel_width = self.room_width * self.TILE_SIZE
        room_pixel_height = self.room_height * self.TILE_SIZE

        # Player position is top-left of sprite
        # Keep the entire sprite within the room bounds
        min_x = edge_padding
        min_y = edge_padding
        max_x = room_pixel_width - self.TILE_SIZE - edge_padding
        max_y = room_pixel_height - self.TILE_SIZE - edge_padding

        return min_x, min_y, max_x, max_y

    def clamp_position(self, x, y):
        """Clamp position to valid room bounds - this is the safety net"""
        min_x, min_y, max_x, max_y = self.get_room_bounds()
        clamped_x = max(min_x, min(x, max_x))
        clamped_y = max(min_y, min(y, max_y))
        return clamped_x, clamped_y

    def get_player_collision_rect(self, px=None, py=None):
        """Get the player's collision rectangle at given position (or current position)"""
        if px is None:
            px = self.player_pixel_x
        if py is None:
            py = self.player_pixel_y
        return pygame.Rect(
            px + self.player_collision_offset_x,
            py + self.player_collision_offset_y,
            self.player_collision_width,
            self.player_collision_height
        )

    def check_collision(self, new_x, new_y):
        """Check if player would collide at the given pixel position"""
        player_rect = self.get_player_collision_rect(new_x, new_y)
        for rect in self.collision_rects:
            if player_rect.colliderect(rect):
                return True
        return False

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
        print(f"Entered generic interior room: {self.room_width}x{self.room_height}")

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
                for door in self.doors:
                    if isinstance(door, list) and len(door) >= 2:
                        door_x, door_y = door[0], door[1]
                        if abs(current_tile_x - door_x) <= 1 and abs(current_tile_y - door_y) <= 1:
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

        # Draw other layers (walls from room data, then furniture, then decor)
        for layer_name in ['walls', 'furniture', 'decor']:
            if layer_name in self.layers:
                layer = self.layers[layer_name]
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

        # Draw player using actual sprite if available, otherwise use simple circle
        # Use floating point position for smooth movement
        player_screen_x = int(self.player_pixel_x - self.camera_x + offset_x)
        player_screen_y = int(self.player_pixel_y - self.camera_y + offset_y)

        if self.player_sprite and hasattr(self.player_sprite, 'animations'):
            # Use the actual player sprite with animations
            if self.player_walking:
                anim_name = f'walk_{self.player_direction}'
            else:
                anim_name = f'idle_{self.player_direction}'

            # Get the animation frames
            if anim_name in self.player_sprite.animations:
                frames = self.player_sprite.animations[anim_name]
                if frames and len(frames) > 0:
                    frame_index = min(self.animation_frame, len(frames) - 1)
                    screen.blit(frames[frame_index], (player_screen_x, player_screen_y))
                else:
                    # Fallback if no frames
                    pygame.draw.circle(screen, (255, 255, 0),
                                     (player_screen_x + self.TILE_SIZE // 2, player_screen_y + self.TILE_SIZE // 2), 12)
            else:
                # Fallback if animation not found
                pygame.draw.circle(screen, (255, 255, 0),
                                 (player_screen_x + self.TILE_SIZE // 2, player_screen_y + self.TILE_SIZE // 2), 12)
        else:
            # Fallback to circle
            pygame.draw.circle(screen, (255, 255, 0),
                             (player_screen_x + self.TILE_SIZE // 2, player_screen_y + self.TILE_SIZE // 2), 12)
            pygame.draw.circle(screen, (200, 200, 0),
                             (player_screen_x + self.TILE_SIZE // 2, player_screen_y + self.TILE_SIZE // 2), 12, 2)

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
                # Only draw if within room bounds (not boundary rects)
                if rect.x >= 0 and rect.y >= 0 and rect.x < self.room_width * self.TILE_SIZE and rect.y < self.room_height * self.TILE_SIZE:
                    screen_rect = pygame.Rect(
                        rect.x - self.camera_x + offset_x,
                        rect.y - self.camera_y + offset_y,
                        rect.width,
                        rect.height
                    )
                    # Semi-transparent red
                    debug_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(debug_surf, (255, 0, 0, 100), debug_surf.get_rect())
                    pygame.draw.rect(debug_surf, (255, 0, 0, 200), debug_surf.get_rect(), 1)
                    screen.blit(debug_surf, screen_rect.topleft)

            # Draw player collision box in green
            player_rect = self.get_player_collision_rect()
            screen_player_rect = pygame.Rect(
                player_rect.x - self.camera_x + offset_x,
                player_rect.y - self.camera_y + offset_y,
                player_rect.width,
                player_rect.height
            )
            debug_surf = pygame.Surface((player_rect.width, player_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(debug_surf, (0, 255, 0, 100), debug_surf.get_rect())
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
                f"Bounds: X[{min_x:.0f}-{max_x:.0f}] Y[{min_y:.0f}-{max_y:.0f}]",
                f"Room: {self.room_width}x{self.room_height} tiles",
                f"Collision rects: {len(self.collision_rects)}",
                "Press F3 to hide"
            ]
            for i, text in enumerate(debug_info):
                surf = debug_font.render(text, True, (255, 255, 0))
                screen.blit(surf, (10, 10 + i * 18))
"""
Generic Interior - Loads and displays custom interior rooms created with interior_room_builder
"""
import pygame
import os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

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
        self.move_speed = self.TILE_SIZE / 16.0  # Slower speed for interiors: tile_size / 16.0 pixels per frame

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
        """Handle continuous input for movement"""
        if not self.is_moving:
            # Get current tile position
            current_tile_x = int(self.player_pixel_x / self.TILE_SIZE)
            current_tile_y = int(self.player_pixel_y / self.TILE_SIZE)
            new_tile_x = current_tile_x
            new_tile_y = current_tile_y

            # Check movement keys and set target position
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                if current_tile_y > 0:
                    new_tile_y = current_tile_y - 1
                    self.player_direction = 'up'
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                if current_tile_y < self.room_height - 1:
                    new_tile_y = current_tile_y + 1
                    self.player_direction = 'down'
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                if current_tile_x > 0:
                    new_tile_x = current_tile_x - 1
                    self.player_direction = 'left'
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                if current_tile_x < self.room_width - 1:
                    new_tile_x = current_tile_x + 1
                    self.player_direction = 'right'

            # If position changed, start movement
            if new_tile_x != current_tile_x or new_tile_y != current_tile_y:
                self.player_tile_x = new_tile_x
                self.player_tile_y = new_tile_y
                self.target_pixel_x = float(new_tile_x * self.TILE_SIZE)
                self.target_pixel_y = float(new_tile_y * self.TILE_SIZE)
                self.is_moving = True
                self.player_walking = True

    def update(self, dt):
        """Update interior state"""
        # Update movement (matching exterior player update logic)
        if self.is_moving:
            # Calculate movement step based on dt (normalize to 60 FPS like exterior)
            step = self.move_speed * dt * 60

            # Move towards target
            dx = self.target_pixel_x - self.player_pixel_x
            dy = self.target_pixel_y - self.player_pixel_y

            # Calculate distance
            distance = (dx * dx + dy * dy) ** 0.5

            if distance <= step:
                # Arrived at target
                self.player_pixel_x = self.target_pixel_x
                self.player_pixel_y = self.target_pixel_y
                self.is_moving = False
                self.player_walking = False
            else:
                # Move towards target
                ratio = step / distance
                self.player_pixel_x += dx * ratio
                self.player_pixel_y += dy * ratio
        else:
            self.player_walking = False

        # Update animation exactly like exterior
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

        # Draw other layers
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

        # Draw UI
        font = pygame.font.Font(None, 24)
        text = font.render("Press E at door to exit | ESC to leave", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Show if near door
        for door in self.doors:
            if isinstance(door, list) and len(door) >= 2:
                door_x, door_y = door[0], door[1]
                if abs(self.player_tile_x - door_x) <= 1 and abs(self.player_tile_y - door_y) <= 1:
                    exit_text = font.render("Press E to EXIT", True, (0, 255, 0))
                    screen.blit(exit_text, (self.SCREEN_WIDTH // 2 - 80, 50))
                    break
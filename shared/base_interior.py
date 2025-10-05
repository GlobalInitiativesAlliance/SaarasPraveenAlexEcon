import pygame
import json
import os
from .constants import *

class BaseInterior:
    """Base class for all interior spaces with flexible tileset loading"""
    
    def __init__(self, game, room_name):
        self.game = game
        self.room_name = room_name
        self.active = False
        self.room_data = None
        
        # Room dimensions (in tiles)
        self.room_width = 16
        self.room_height = 12
        
        # Calculate room position to center on screen
        self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
        self.room_y = (SCREEN_HEIGHT - self.room_height * TILE_SIZE) // 2
        
        # Player position in interior (tile coordinates)
        self.player_x = 8
        self.player_y = 10
        self.player_facing = "up"
        self.player_moving = False
        self.player_move_progress = 0.0
        self.player_start_x = self.player_x
        self.player_start_y = self.player_y
        self.player_target_x = self.player_x
        self.player_target_y = self.player_y
        self.move_speed = 5.0  # tiles per second
        
        # Animation timers
        self.animation_timer = 0
        
        # Transition effects
        self.transition_alpha = 255
        self.transition_state = "fade_in"
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Tileset storage
        self.tilesets = {}
        self.tile_scale = TILE_SIZE / 16
        
        # Available tileset names
        self.tileset_names = [
            'TopDownHouse_FloorsAndWalls.png',
            'TopDownHouse_FurnitureState1.png',
            'TopDownHouse_FurnitureState2.png',
            'TopDownHouse_SmallItems.png',
            'TopDownHouse_DoorsAndWindows.png',
            'Japanese_Home_1_preview_16x16.png',
            'Tv_Studio_Design_preview.png',
            'Museum_room_4_preview_48x48.png',
            'Condominium_Design_preview.png'
        ]
        
        # Load room layout and tilesets
        self.load_room_data()
        self.load_interior_tiles()
        
        # Create collision map
        self.collision_map = set()
        self.create_collision_map()
        
    def load_room_data(self):
        """Load room data from interior_rooms.json"""
        try:
            with open("data/interiors/interior_rooms.json", "r") as f:
                data = json.load(f)
                if self.room_name in data.get("rooms", {}):
                    self.room_data = data["rooms"][self.room_name]
                    self.room_width = self.room_data.get("width", 16)
                    self.room_height = self.room_data.get("height", 12)
                    # Recalculate room position with new dimensions
                    self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
                    self.room_y = (SCREEN_HEIGHT - self.room_height * TILE_SIZE) // 2
                    print(f"Loaded room: {self.room_name} ({self.room_width}x{self.room_height})")
        except:
            print(f"Warning: Could not load room data for {self.room_name}")
            
    def load_interior_tiles(self):
        """Load all interior tileset images"""
        base_dir = "assets/Top-Down_Retro_Interior"
        
        for tileset_name in self.tileset_names:
            try:
                path = os.path.join(base_dir, tileset_name)
                if os.path.exists(path):
                    self.tilesets[tileset_name] = pygame.image.load(path).convert_alpha()
                    print(f"Loaded tileset: {tileset_name}")
                else:
                    print(f"Warning: Tileset not found at {path}")
            except Exception as e:
                print(f"Warning: Could not load tileset {tileset_name}: {e}")
                
        # Legacy compatibility - map old attribute names
        if 'TopDownHouse_FloorsAndWalls.png' in self.tilesets:
            self.floor_tileset = self.tilesets['TopDownHouse_FloorsAndWalls.png']
        if 'TopDownHouse_FurnitureState1.png' in self.tilesets:
            self.furniture_tileset = self.tilesets['TopDownHouse_FurnitureState1.png']
        if 'TopDownHouse_SmallItems.png' in self.tilesets:
            self.small_items_tileset = self.tilesets['TopDownHouse_SmallItems.png']
        if 'TopDownHouse_DoorsAndWindows.png' in self.tilesets:
            self.doors_windows_tileset = self.tilesets['TopDownHouse_DoorsAndWindows.png']
            
    def get_tile_from_sheet(self, sheet, x, y, width=16, height=16):
        """Extract a tile from a tileset"""
        if sheet is None:
            return None
        try:
            # Check bounds
            sheet_width, sheet_height = sheet.get_size()
            max_x = (sheet_width // width) - 1
            max_y = (sheet_height // height) - 1
            
            if x > max_x or y > max_y:
                # Only print warning once per tileset to reduce spam
                warning_key = f"{sheet.get_size()}_{width}x{height}"
                if not hasattr(self, '_tileset_warnings'):
                    self._tileset_warnings = set()
                if warning_key not in self._tileset_warnings:
                    print(f"Warning: Some tiles are out of bounds for tileset (max: {max_x}, {max_y}) with tile size {width}x{height}")
                    self._tileset_warnings.add(warning_key)
                return None
                
            tile = sheet.subsurface(pygame.Rect(x * width, y * height, width, height))
            # Always scale to TILE_SIZE
            scaled_tile = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
            return scaled_tile
        except Exception as e:
            print(f"Error getting tile at ({x}, {y}) with size {width}x{height}: {e}")
            return None
            
    def get_tileset_by_name(self, sheet_name):
        """Get tileset by name with fallback logic"""
        # Direct match
        if sheet_name in self.tilesets:
            return self.tilesets[sheet_name]
            
        # Try to match by partial name
        for tileset_name, tileset in self.tilesets.items():
            if sheet_name in tileset_name or tileset_name in sheet_name:
                return tileset
                
        # Legacy compatibility
        if 'FloorsAndWalls' in sheet_name:
            return self.tilesets.get('TopDownHouse_FloorsAndWalls.png')
        elif 'FurnitureState1' in sheet_name:
            return self.tilesets.get('TopDownHouse_FurnitureState1.png')
        elif 'FurnitureState2' in sheet_name:
            return self.tilesets.get('TopDownHouse_FurnitureState2.png')
        elif 'SmallItems' in sheet_name:
            return self.tilesets.get('TopDownHouse_SmallItems.png')
        elif 'DoorsAndWindows' in sheet_name:
            return self.tilesets.get('TopDownHouse_DoorsAndWindows.png')
            
        print(f"Warning: Tileset not found for {sheet_name}")
        return None
        
    def create_collision_map(self):
        """Create collision map based on furniture and walls"""
        self.collision_map.clear()
        
        if not self.room_data:
            return
            
        # Add furniture layer to collision map
        furniture_layer = self.room_data.get('layers', {}).get('furniture', [])
        for y in range(len(furniture_layer)):
            for x in range(len(furniture_layer[y])):
                if furniture_layer[y][x] is not None:
                    self.collision_map.add((x, y))
                    
        # Add walls layer to collision map
        walls_layer = self.room_data.get('layers', {}).get('walls', [])
        for y in range(len(walls_layer)):
            for x in range(len(walls_layer[y])):
                if walls_layer[y][x] is not None:
                    self.collision_map.add((x, y))
                    
    def enter(self):
        """Enter the interior"""
        self.active = True
        self.transition_state = "fade_in"
        self.transition_alpha = 255
        # Reset player position
        self.player_x = self.room_width // 2
        self.player_y = self.room_height - 2
        self.player_facing = "up"
        self.player_moving = False
        
    def exit(self):
        """Exit the interior"""
        self.transition_state = "fade_out"
        
    def handle_input(self, keys):
        """Handle keyboard input for movement"""
        if not self.player_moving:
            new_x, new_y = self.player_x, self.player_y
            new_facing = self.player_facing
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x -= 1
                new_facing = "left"
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x += 1
                new_facing = "right"
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                new_y -= 1
                new_facing = "up"
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                new_y += 1
                new_facing = "down"
                
            self.player_facing = new_facing
                
            # Check collision
            if new_x != self.player_x or new_y != self.player_y:
                if (new_x, new_y) not in self.collision_map and \
                   0 <= new_x < self.room_width and 0 <= new_y < self.room_height:
                    self.player_start_x = self.player_x
                    self.player_start_y = self.player_y
                    self.player_target_x = new_x
                    self.player_target_y = new_y
                    self.player_moving = True
                    self.player_move_progress = 0.0
                    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
                
    def update(self, dt):
        """Update interior state"""
        # Update animations
        self.animation_timer += dt
        
        # Update player movement
        if self.player_moving:
            self.player_move_progress += self.move_speed * dt
            if self.player_move_progress >= 1.0:
                self.player_x = self.player_target_x
                self.player_y = self.player_target_y
                self.player_moving = False
                self.player_move_progress = 0.0
                
        # Update transitions
        if self.transition_state == "fade_in":
            self.transition_alpha = max(0, self.transition_alpha - 500 * dt)
            if self.transition_alpha == 0:
                self.transition_state = "active"
        elif self.transition_state == "fade_out":
            self.transition_alpha = min(255, self.transition_alpha + 500 * dt)
            if self.transition_alpha == 255:
                self.active = False
                
    def draw_room_tiles(self, screen):
        """Draw room tiles from saved data"""
        if not self.room_data:
            # Fallback to basic floor
            for y in range(self.room_height):
                for x in range(self.room_width):
                    screen_x = self.room_x + x * TILE_SIZE
                    screen_y = self.room_y + y * TILE_SIZE
                    pygame.draw.rect(screen, (100, 80, 60), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
            return
            
        # Draw layers in order
        layers = self.room_data.get('layers', {})
        layer_order = ['floor', 'walls', 'furniture', 'decor']
        
        for layer_name in layer_order:
            if layer_name in layers:
                layer = layers[layer_name]
                for y in range(min(len(layer), self.room_height)):
                    for x in range(min(len(layer[y]), self.room_width)):
                        tile_info = layer[y][x]
                        if tile_info and len(tile_info) >= 3:
                            sheet_name, tile_x, tile_y = tile_info
                            
                            # Get the appropriate tileset
                            tileset = self.get_tileset_by_name(sheet_name)
                            
                            if tileset:
                                # Determine tile size based on tileset name
                                tile_size = 16
                                if '48x48' in sheet_name:
                                    tile_size = 48
                                    
                                tile = self.get_tile_from_sheet(tileset, tile_x, tile_y, tile_size, tile_size)
                                if tile:
                                    screen_x = self.room_x + x * TILE_SIZE
                                    screen_y = self.room_y + y * TILE_SIZE
                                    screen.blit(tile, (screen_x, screen_y))
                                    
    def draw_player(self, screen):
        """Draw the player character"""
        # Calculate interpolated position if moving
        if self.player_moving:
            interp_x = self.player_start_x + (self.player_target_x - self.player_start_x) * self.player_move_progress
            interp_y = self.player_start_y + (self.player_target_y - self.player_start_y) * self.player_move_progress
        else:
            interp_x = self.player_x
            interp_y = self.player_y
            
        player_x = self.room_x + int(interp_x * TILE_SIZE)
        player_y = self.room_y + int(interp_y * TILE_SIZE)
        
        # Use game's player sprite if available
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            frame = int(self.animation_timer * 4) % 2 if self.player_moving else 0
            self.game.player.draw_at_position(screen, player_x, player_y, self.player_facing, frame)
        else:
            # Fallback to simple rectangle
            pygame.draw.rect(screen, (0, 100, 200), (player_x + 8, player_y + 8, 16, 16))
            
    def draw(self, screen):
        """Draw the interior"""
        # Clear background
        screen.fill((20, 20, 30))
        
        # Draw room tiles
        self.draw_room_tiles(screen)
        
        # Draw player
        self.draw_player(screen)
        
        # Draw exit prompt
        exit_text = self.font.render("Press ESC to exit", True, (255, 255, 255))
        screen.blit(exit_text, (10, SCREEN_HEIGHT - 30))
        
        # Draw transition overlay
        if self.transition_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.transition_alpha)
            screen.blit(overlay, (0, 0))
import pygame
import math
import json
from constants import *

class HomeInterior:
    """Home interior with sofa that can be used as a bed"""
    def __init__(self, game, room_name="home"):
        self.game = game
        self.active = False
        self.room_name = room_name
        self.room_data = None
        
        # Room dimensions (in tiles)
        self.room_width = 16
        self.room_height = 12
        
        # Calculate room position to center on screen
        self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
        self.room_y = (SCREEN_HEIGHT - self.room_height * TILE_SIZE) // 2
        
        # Player position in home (tile coordinates)
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
        
        # Sofa/bed state
        self.sofa_position = (0, 6)  # Based on the furniture in the room
        self.sofa_width = 2  # Sofa spans 2 tiles
        self.sofa_height = 2  # And is 2 tiles tall
        self.near_sofa = False
        self.sleeping = False
        self.sleep_timer = 0
        self.sleep_duration = 3.0  # 3 seconds of sleep animation
        
        # Animation timers
        self.animation_timer = 0
        
        # Transition effects
        self.transition_alpha = 255
        self.transition_state = "fade_in"
        
        # Sleep overlay
        self.sleep_overlay_alpha = 0
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Load room layout and tilesets
        self.load_room_data()
        self.load_interior_tiles()
        
        # Find sofa position from room data
        self.find_sofa_position()
        
        # Create collision map
        self.create_collision_map()
        
    def load_room_data(self):
        """Load room data from interior_rooms.json"""
        try:
            with open("interior_rooms.json", "r") as f:
                data = json.load(f)
                if self.room_name in data["rooms"]:
                    self.room_data = data["rooms"][self.room_name]
                    self.room_width = self.room_data.get('width', 16)
                    self.room_height = self.room_data.get('height', 12)
                    print(f"Loaded home: {self.room_name} ({self.room_width}x{self.room_height})")
                else:
                    print(f"Room '{self.room_name}' not found, using default layout")
                    self.room_data = None
        except Exception as e:
            print(f"Could not load room data: {e}")
            self.room_data = None
    
    def load_interior_tiles(self):
        """Load interior tileset images"""
        try:
            self.floor_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FloorsAndWalls.png").convert_alpha()
            self.furniture_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FurnitureState1.png").convert_alpha()
            self.small_items_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_SmallItems.png").convert_alpha()
            self.doors_windows_tileset = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_DoorsAndWindows.png").convert_alpha()
            
            # Load second furniture state for bed transformation
            self.furniture_tileset2 = pygame.image.load("Top-Down_Retro_Interior/TopDownHouse_FurnitureState2.png").convert_alpha()
            
            # Scale factor for tiles
            self.tile_scale = TILE_SIZE / 16
        except:
            print("Warning: Could not load interior tilesets")
            self.floor_tileset = None
            self.furniture_tileset = None
            self.furniture_tileset2 = None
            
    def get_tile_from_sheet(self, sheet, x, y, width=16, height=16):
        """Extract a tile from a tileset"""
        if sheet is None:
            return None
        try:
            tile = sheet.subsurface(pygame.Rect(x * width, y * height, width, height))
            scaled_tile = pygame.transform.scale(tile, (int(width * self.tile_scale), int(height * self.tile_scale)))
            return scaled_tile
        except:
            return None
            
    def find_sofa_position(self):
        """Find the sofa position from room data"""
        # The sofa is already set based on the room layout
        # It's the furniture at position (0,6) spanning 2x2 tiles
        print(f"Sofa is at position: {self.sofa_position}, size: {self.sofa_width}x{self.sofa_height}")
                        
    def create_collision_map(self):
        """Create collision map for the home"""
        self.collision_map = set()
        
        # Walls (except door)
        for x in range(self.room_width):
            self.collision_map.add((x, 0))
            if x != 8:  # Door position
                self.collision_map.add((x, self.room_height - 1))
        for y in range(1, self.room_height - 1):
            self.collision_map.add((0, y))
            self.collision_map.add((self.room_width - 1, y))
            
        # Add furniture collisions from room data
        if self.room_data and 'layers' in self.room_data:
            furniture_layer = self.room_data['layers'].get('furniture', [])
            for y in range(len(furniture_layer)):
                for x in range(len(furniture_layer[y])):
                    if furniture_layer[y][x]:
                        # Don't add collision for sofa area (we want to interact with it)
                        sofa_x, sofa_y = self.sofa_position
                        if not (x >= sofa_x and x < sofa_x + self.sofa_width and 
                                y >= sofa_y and y < sofa_y + self.sofa_height):
                            self.collision_map.add((x, y))
                
    def enter(self):
        """Enter the home"""
        self.active = True
        self.transition_state = "fade_in"
        self.transition_alpha = 255
        self.sleeping = False
        self.sleep_timer = 0
        
        print(f"Entered home. Sofa at {self.sofa_position}, player at ({self.player_x}, {self.player_y})")
        
        # Clear the player near objective flag
        if hasattr(self.game, 'player_near_objective'):
            self.game.player_near_objective = False
            
    def exit(self):
        """Exit the home"""
        self.transition_state = "fade_out"
        
    def handle_input(self, keys):
        """Handle keyboard input"""
        if self.sleeping:
            return  # Can't move while sleeping
            
        # Movement
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
            if event.key == pygame.K_e:
                self.handle_interaction()
                    
    def handle_interaction(self):
        """Handle E key interactions"""
        # Check for door
        if self.player_y >= self.room_height - 3 and (self.player_x >= 7 and self.player_x <= 9):
            self.exit()
            return
            
        # Check for sofa interaction - sleep directly
        if self.near_sofa and not self.sleeping:
            self.start_sleeping()
                
    def start_sleeping(self):
        """Start the sleep animation"""
        self.sleeping = True
        self.sleep_timer = 0
        self.sleep_overlay_alpha = 0
        
        # Check if this completes a sleep objective
        if hasattr(self.game, 'objective_manager'):
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj and 'sleep' in current_obj.id:
                # We'll advance the objective after sleep animation
                pass
                
    def update(self, dt):
        """Update home state"""
        self.animation_timer += dt
        
        # Handle transitions
        if self.transition_state == "fade_in":
            self.transition_alpha = max(0, self.transition_alpha - 400 * dt)
            if self.transition_alpha <= 0:
                self.transition_state = "active"
        elif self.transition_state == "fade_out":
            self.transition_alpha = min(255, self.transition_alpha + 400 * dt)
            if self.transition_alpha >= 255:
                self.active = False
                
        # Update player movement
        if self.player_moving and not self.sleeping:
            self.player_move_progress += self.move_speed * dt
            if self.player_move_progress >= 1.0:
                self.player_x = self.player_target_x
                self.player_y = self.player_target_y
                self.player_moving = False
                self.player_move_progress = 0.0
            else:
                t = self.player_move_progress
                t = t * t * (3.0 - 2.0 * t)
                
        # Check if player is near sofa (considering its size)
        sofa_x, sofa_y = self.sofa_position
        # Check if player is within 1 tile of the sofa area
        near_x = (self.player_x >= sofa_x - 1) and (self.player_x <= sofa_x + self.sofa_width)
        near_y = (self.player_y >= sofa_y - 1) and (self.player_y <= sofa_y + self.sofa_height)
        self.near_sofa = near_x and near_y
        
        # Update sleep animation
        if self.sleeping:
            self.sleep_timer += dt
            
            # Fade to black and back
            if self.sleep_timer < 1.0:
                # Fade to black
                self.sleep_overlay_alpha = int(255 * self.sleep_timer)
            elif self.sleep_timer < 2.0:
                # Stay black
                self.sleep_overlay_alpha = 255
            elif self.sleep_timer < 3.0:
                # Fade back
                self.sleep_overlay_alpha = int(255 * (3.0 - self.sleep_timer))
            else:
                # Sleep complete
                self.sleeping = False
                self.sleep_overlay_alpha = 0
                
                # Advance time and complete sleep objective
                if hasattr(self.game, 'objective_manager'):
                    current_obj = self.game.objective_manager.get_current_objective()
                    if current_obj and 'sleep' in current_obj.id:
                        # Update game time
                        if 'day1' in current_obj.id or 'work' in current_obj.id:
                            self.game.objective_manager.game_time = "6:00 AM"
                            self.game.objective_manager.current_day = 2
                        elif 'day2' in current_obj.id:
                            self.game.objective_manager.game_time = "7:00 AM"
                            self.game.objective_manager.current_day = 3
                            
                        # Complete the objective
                        self.game.objective_manager.advance_to_next_objective()
                        
                        # Show wake up message
                        if hasattr(self.game.objective_manager, 'show_notification'):
                            self.game.objective_manager.show_notification("You wake up feeling refreshed!")
                
    def get_player_pixel_pos(self):
        """Get interpolated player position in pixels"""
        if self.player_moving:
            t = self.player_move_progress
            t = t * t * (3.0 - 2.0 * t)
            
            current_x = self.player_start_x + (self.player_target_x - self.player_start_x) * t
            current_y = self.player_start_y + (self.player_target_y - self.player_start_y) * t
            
            pixel_x = self.room_x + current_x * TILE_SIZE
            pixel_y = self.room_y + current_y * TILE_SIZE
        else:
            pixel_x = self.room_x + self.player_x * TILE_SIZE
            pixel_y = self.room_y + self.player_y * TILE_SIZE
            
        return pixel_x, pixel_y
        
    def draw(self, screen):
        """Draw the home interior"""
        if not self.active:
            return
            
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Draw room from saved layout
        if self.room_data and 'layers' in self.room_data:
            layers = self.room_data['layers']
            
            # Draw each layer in order
            for layer_name in ['floor', 'walls', 'furniture', 'decor']:
                if layer_name in layers:
                    layer = layers[layer_name]
                    
                    for y in range(min(len(layer), self.room_height)):
                        for x in range(min(len(layer[y]), self.room_width)):
                            tile_info = layer[y][x]
                            if tile_info and len(tile_info) == 3:
                                sheet_name, tile_x, tile_y = tile_info
                                
                                # Determine which tileset to use
                                tileset = None
                                if 'FloorsAndWalls' in sheet_name:
                                    tileset = self.floor_tileset
                                elif 'FurnitureState1' in sheet_name:
                                    tileset = self.furniture_tileset
                                elif 'FurnitureState2' in sheet_name:
                                    tileset = self.furniture_tileset2
                                elif 'SmallItems' in sheet_name:
                                    tileset = self.small_items_tileset
                                elif 'DoorsAndWindows' in sheet_name:
                                    tileset = self.doors_windows_tileset
                                    
                                if tileset:
                                    tile = self.get_tile_from_sheet(tileset, tile_x, tile_y)
                                    if tile:
                                        screen_x = self.room_x + x * TILE_SIZE
                                        screen_y = self.room_y + y * TILE_SIZE
                                        screen.blit(tile, (screen_x, screen_y))
        else:
            # Fallback drawing
            # Draw floor
            for y in range(self.room_height):
                for x in range(self.room_width):
                    screen_x = self.room_x + x * TILE_SIZE
                    screen_y = self.room_y + y * TILE_SIZE
                    color = (120, 100, 80) if (x + y) % 2 == 0 else (110, 90, 70)
                    pygame.draw.rect(screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    
            # Draw sofa
            sofa_x = self.room_x + self.sofa_position[0] * TILE_SIZE
            sofa_y = self.room_y + self.sofa_position[1] * TILE_SIZE
            
            # Draw as sofa/bed combo
            pygame.draw.rect(screen, (100, 80, 120), 
                           (sofa_x, sofa_y, TILE_SIZE * self.sofa_width, TILE_SIZE * self.sofa_height))
            pygame.draw.rect(screen, (120, 100, 140), 
                           (sofa_x + 5, sofa_y + 5, TILE_SIZE * self.sofa_width - 10, TILE_SIZE * self.sofa_height - 10))
                                        
        # Draw door
        door_x = self.room_x + 8 * TILE_SIZE
        door_y = self.room_y + (self.room_height - 1) * TILE_SIZE
        
        if self.doors_windows_tileset:
            door_tile = self.get_tile_from_sheet(self.doors_windows_tileset, 1, 0)
            if door_tile:
                screen.blit(door_tile, (door_x, door_y))
        else:
            pygame.draw.rect(screen, (80, 60, 40), (door_x, door_y, TILE_SIZE, TILE_SIZE))
            
        # Draw player (if not in bed sleeping)
        if not (self.sleeping and self.sleep_timer > 0.5 and self.sleep_timer < 2.5):
            player_x, player_y = self.get_player_pixel_pos()
            
            if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
                self.game.player.draw_at_position(screen, player_x, player_y, self.player_facing)
            else:
                pygame.draw.circle(screen, (255, 100, 100),
                                 (player_x + TILE_SIZE // 2, player_y + TILE_SIZE // 2),
                                 TILE_SIZE // 3)
                             
        # Draw highlight around sofa if player is near
        if self.near_sofa and not self.sleeping:
            sofa_x = self.room_x + self.sofa_position[0] * TILE_SIZE
            sofa_y = self.room_y + self.sofa_position[1] * TILE_SIZE
            highlight_rect = pygame.Rect(sofa_x - 2, sofa_y - 2, 
                                       TILE_SIZE * self.sofa_width + 4, 
                                       TILE_SIZE * self.sofa_height + 4)
            pygame.draw.rect(screen, (255, 255, 100), highlight_rect, 3)
        
        # Draw interaction prompts
        font = pygame.font.Font(None, 20)
        
        # Sofa/bed prompt
        if self.near_sofa and not self.sleeping:
            prompt = font.render("Press E to sleep", True, (255, 255, 200))
            player_x, player_y = self.get_player_pixel_pos()
            prompt_x = player_x - prompt.get_width() // 2 + TILE_SIZE // 2
            prompt_y = player_y - 25
            screen.blit(prompt, (prompt_x, prompt_y))
            
        # Door prompt
        if self.player_y >= self.room_height - 3 and (self.player_x >= 7 and self.player_x <= 9):
            prompt = font.render("Press E to exit", True, (255, 255, 200))
            player_x, player_y = self.get_player_pixel_pos()
            prompt_x = player_x - prompt.get_width() // 2 + TILE_SIZE // 2
            prompt_y = player_y - 25
            screen.blit(prompt, (prompt_x, prompt_y))
            
        # Draw sleep overlay
        if self.sleep_overlay_alpha > 0:
            sleep_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            sleep_surface.fill((0, 0, 0))
            sleep_surface.set_alpha(self.sleep_overlay_alpha)
            screen.blit(sleep_surface, (0, 0))
            
            # Draw Z's during sleep
            if self.sleep_timer > 0.5 and self.sleep_timer < 2.5:
                z_font = pygame.font.Font(None, 48)
                z_count = int(self.sleep_timer * 2) % 3 + 1
                z_text = "Z" * z_count
                z_surf = z_font.render(z_text, True, (255, 255, 255))
                z_rect = z_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(z_surf, z_rect)
            
        # Draw transition overlay
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.transition_alpha)
            screen.blit(fade_surface, (0, 0))
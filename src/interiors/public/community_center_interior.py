import pygame
import math
import json
from src.constants import *
from ..residential.home_interior import HomeInterior

class CommunityCenterInterior(HomeInterior):
    """Community center interior for life skills workshop and TLP application"""
    def __init__(self, game, room_name="community_center"):
        # Initialize parent class
        super().__init__(game, room_name)
        
        # Camera offset for large rooms - needs to be initialized properly
        # These will be set in update_camera but need initial values
        self.camera_x = 0
        self.camera_y = 0
        
        # Debug: print room info after loading
        print(f"CommunityCenterInterior initialized:")
        print(f"  Room name: {self.room_name}")
        print(f"  Room size from data: {self.room_width}x{self.room_height}")
        print(f"  Room position: ({self.room_x}, {self.room_y})")
        
        # Override player start position
        self.player_x = self.room_width // 2
        self.player_y = self.room_height - 2
        
        # Activity states
        self.workshop_complete = False
        self.application_submitted = False
        
        # NPCs - positioned for TV studio layout (11x10 tiles)
        self.workshop_instructor = {
            'x': 5,  # Center of presentation area
            'y': 2,  # Near the screens at top
            'facing': 'down',
            'name': 'Sarah'
        }
        
        self.application_desk = {
            'x': 8,  # Right side of room
            'y': 6,  # Lower area near desks
            'facing': 'left',
            'name': 'Mr. Johnson'
        }
        
        # Debug mode
        self.debug_mode = False
        self.debug_font = pygame.font.Font(None, 20)
        
        # Visual effects
        self.glow_animation = 0
        
    def load_interior_tiles(self):
        """Load interior tileset images - override to tag TV studio tileset"""
        super().load_interior_tiles()
        
        # Mark the TV studio tileset for special handling
        if 'Tv_Studio_Design_preview.png' in self.tilesets:
            self.tv_studio_tileset = self.tilesets['Tv_Studio_Design_preview.png']
            print(f"TV Studio tileset loaded successfully: {self.tv_studio_tileset.get_size()}")
    
    def get_tile_from_sheet(self, sheet, x, y, width=16, height=16):
        """Extract a tile from a tileset - override to handle different tile sizes"""
        if sheet is None:
            return None
            
        # TV studio tileset uses 16x16 tiles, not 48x48
        # The tileset is 176x160 pixels for 11x10 tiles = 16x16 per tile
        return super().get_tile_from_sheet(sheet, x, y, width, height)
    
    def override_initial_position(self):
        """Override the initial room positioning for large rooms"""
        # Force large rooms to start at origin
        self.room_x = 0
        self.room_y = 0
        
    def enter(self):
        """Enter the community center"""
        # Don't call super().enter() yet - we need to set player position first
        self.active = True
        self.transition_state = "fade_in"
        self.transition_alpha = 255
        
        # Set player position at the door (for TV studio which is 11x10 tiles)
        self.player_x = 5   # Middle of the 11-wide room
        self.player_y = 8   # Near bottom of the 10-high room
        self.player_facing = "up"
        self.player_moving = False
        
        # Force room to be at origin since it's so large
        self.room_x = 0
        self.room_y = 0
        
        # Update camera to center on player immediately
        self.update_camera()
        
        # Debug output
        print(f"\n=== COMMUNITY CENTER ENTERED ===")
        print(f"Room loaded: {self.room_width}x{self.room_height} tiles")
        print(f"Room pixel size: {self.room_width * TILE_SIZE}x{self.room_height * TILE_SIZE}")
        print(f"Room position: ({self.room_x}, {self.room_y})")
        print(f"Player position: ({self.player_x}, {self.player_y})")
        print(f"Initial camera: ({self.camera_x}, {self.camera_y})")
        print(f"Room bounds on screen: ({self.room_x + self.camera_x}, {self.room_y + self.camera_y})")
        print(f"Bottom-right corner: ({self.room_x + self.room_width * TILE_SIZE + self.camera_x}, {self.room_y + self.room_height * TILE_SIZE + self.camera_y})")
        print(f"Visible tiles range: X({-self.camera_x // TILE_SIZE} to {(-self.camera_x + SCREEN_WIDTH) // TILE_SIZE}), Y({-self.camera_y // TILE_SIZE} to {(-self.camera_y + SCREEN_HEIGHT) // TILE_SIZE})")
        print("Press F9 for debug screenshot, F10 to toggle debug overlay")
        print("================================\n")
            
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_F9:
                # Take debug screenshot
                self.take_debug_screenshot()
            elif event.key == pygame.K_F10:
                # Toggle debug mode
                self.debug_mode = not self.debug_mode
                print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
            elif event.key == pygame.K_SPACE:
                # Check interactions
                if self.is_near_workshop_instructor() and not self.workshop_complete:
                    self.attend_workshop()
                elif self.is_near_application_desk() and not self.application_submitted:
                    self.submit_application()
            else:
                # Let parent handle movement
                super().handle_event(event)
                    
    def is_near_workshop_instructor(self):
        """Check if player is near the workshop instructor"""
        dx = abs(self.player_x - self.workshop_instructor['x'])
        dy = abs(self.player_y - self.workshop_instructor['y'])
        return dx <= 2 and dy <= 2
        
    def is_near_application_desk(self):
        """Check if player is near the application desk"""
        dx = abs(self.player_x - self.application_desk['x'])
        dy = abs(self.player_y - self.application_desk['y'])
        return dx <= 2 and dy <= 2
        
    def attend_workshop(self):
        """Attend the life skills workshop"""
        self.workshop_complete = True
        self.game.objective_manager.show_notification("Life Skills Workshop complete! You learned budgeting and job skills.")
        
        # Update game objective if needed
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and "Life Skills Workshop" in current_obj.description:
            self.game.objective_manager.complete_current_objective()
            
    def submit_application(self):
        """Submit TLP application"""
        self.application_submitted = True
        self.game.objective_manager.show_notification("TLP Application submitted! You'll hear back soon.")
        
        # Update game objective if needed
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and "Submit TLP Application" in current_obj.description:
            self.game.objective_manager.complete_current_objective()
                    
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        # Check room bounds
        if x < 0 or x >= self.room_width or y < 0 or y >= self.room_height:
            return False
        
        # Check NPC positions
        if (x == self.workshop_instructor['x'] and y == self.workshop_instructor['y']) or \
           (x == self.application_desk['x'] and y == self.application_desk['y']):
            return False
            
        # For TV studio, add collision for furniture based on visible layout
        # Top wall and presentation screens
        if y == 0:
            return False
            
        # Stage/presentation area furniture (monitors, podium)
        if y == 1 and 2 <= x <= 8:
            return False
        if y == 2 and x in [2, 3, 7, 8]:  # Side monitors
            return False
            
        # Middle seating area chairs
        if y == 4 and x in [3, 5, 7]:
            return False
        if y == 5 and x in [3, 5, 7]:
            return False
            
        # Bottom area desks and equipment
        if y == 8 and x in [1, 2, 8, 9]:
            return False
            
        return True
    
    def update_camera(self):
        """Update camera to follow player and keep room centered"""
        # Calculate room size in pixels
        room_pixel_width = self.room_width * TILE_SIZE
        room_pixel_height = self.room_height * TILE_SIZE
        
        # Check if room fits entirely on screen
        if room_pixel_width <= SCREEN_WIDTH and room_pixel_height <= SCREEN_HEIGHT:
            # Room is smaller than screen - center it
            self.camera_x = (SCREEN_WIDTH - room_pixel_width) // 2
            self.camera_y = (SCREEN_HEIGHT - room_pixel_height) // 2
        else:
            # Room is larger than screen - follow player
            # Center the player on screen
            self.camera_x = SCREEN_WIDTH // 2 - (self.player_x * TILE_SIZE + TILE_SIZE // 2)
            self.camera_y = SCREEN_HEIGHT // 2 - (self.player_y * TILE_SIZE + TILE_SIZE // 2)
            
            # Clamp camera to prevent showing outside the room
            # Don't let camera go too far right (would show left edge)
            min_camera_x = -(room_pixel_width - SCREEN_WIDTH)
            max_camera_x = 0
            self.camera_x = max(min_camera_x, min(max_camera_x, self.camera_x))
            
            # Don't let camera go too far down (would show top edge) 
            min_camera_y = -(room_pixel_height - SCREEN_HEIGHT)
            max_camera_y = 0
            self.camera_y = max(min_camera_y, min(max_camera_y, self.camera_y))
        
        # Debug info
        if not hasattr(self, '_debug_printed'):
            print(f"Community Center: {self.room_width}x{self.room_height} tiles")
            print(f"Room pixels: {room_pixel_width}x{room_pixel_height}")
            print(f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
            print(f"Player at: ({self.player_x}, {self.player_y})")
            print(f"Camera offset: ({self.camera_x}, {self.camera_y})")
            self._debug_printed = True
    
    def update(self, dt):
        """Update the interior state"""
        super().update(dt)
        self.update_camera()
        
        # Update glow animation
        self.glow_animation += dt * 3
                    
    def draw(self, screen):
        """Draw the community center"""
        if not self.active:
            return
            
        # Clear background
        screen.fill((20, 20, 30))
        
        # Initialize tiles_drawn counter for debug tracking
        self.tiles_drawn = 0
        
        # Update camera before drawing
        self.update_camera()
        
        # Debug: Log drawing info once
        if not hasattr(self, '_draw_debug_logged'):
            self._draw_debug_logged = True
            print(f"\n=== COMMUNITY CENTER DRAW DEBUG ===")
            print(f"Room position: ({self.room_x}, {self.room_y})")
            print(f"Camera offset: ({self.camera_x}, {self.camera_y})")
            print(f"Room size: {self.room_width}x{self.room_height} tiles")
            print(f"Room has data: {self.room_data is not None}")
            if self.room_data:
                print(f"Has layers: {'layers' in self.room_data}")
                if 'layers' in self.room_data:
                    for layer_name, layer_data in self.room_data['layers'].items():
                        print(f"  Layer '{layer_name}': {len(layer_data)} rows")
            print("===================================\n")
        
        # Call parent draw method which handles tile rendering
        super().draw(screen)
        
        # Draw activity areas (outlines)
        self.draw_activity_areas(screen)
        
        # Draw NPCs on top
        self.draw_npcs(screen)
        
        # Draw custom UI
        self.draw_custom_ui(screen)
        
        # Draw debug overlay last so it's on top
        self.draw_debug_overlay(screen)
        
    def draw_activity_areas(self, screen):
        """Draw subtle glowing areas for activities"""
        # Calculate glow intensity
        glow_alpha = int((math.sin(self.glow_animation) + 1) * 0.5 * 30 + 20)
        
        # Workshop area (presentation/stage area at top)
        workshop_x = self.room_x + 2 * TILE_SIZE + self.camera_x
        workshop_y = self.room_y + 0 * TILE_SIZE + self.camera_y
        
        # Draw soft glow effect for workshop area
        glow_surf = pygame.Surface((7 * TILE_SIZE, 4 * TILE_SIZE), pygame.SRCALPHA)
        glow_color = (120, 170, 255, glow_alpha)
        pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, (workshop_x, workshop_y))
        
        # Application desk area (lower right area with desks)
        desk_x = self.room_x + 6 * TILE_SIZE + self.camera_x
        desk_y = self.room_y + 5 * TILE_SIZE + self.camera_y
        
        # Draw soft glow effect for desk area
        desk_glow = pygame.Surface((4 * TILE_SIZE, 3 * TILE_SIZE), pygame.SRCALPHA)
        desk_color = (255, 170, 120, glow_alpha)
        pygame.draw.rect(desk_glow, desk_color, desk_glow.get_rect(), border_radius=10)
        screen.blit(desk_glow, (desk_x, desk_y))
        
    def draw_npcs(self, screen):
        """Draw the NPCs with subtle glow effects"""
        # Calculate distance-based glow for NPCs
        player_pixel_x = self.player_x * TILE_SIZE + TILE_SIZE // 2
        player_pixel_y = self.player_y * TILE_SIZE + TILE_SIZE // 2
        
        # Draw workshop instructor
        instructor_x = self.room_x + self.workshop_instructor['x'] * TILE_SIZE + self.camera_x
        instructor_y = self.room_y + self.workshop_instructor['y'] * TILE_SIZE + self.camera_y
        
        # Calculate distance to instructor
        instructor_dist = math.sqrt((self.workshop_instructor['x'] - self.player_x)**2 + 
                                   (self.workshop_instructor['y'] - self.player_y)**2)
        
        # Draw glow if player is near
        if instructor_dist < 3:
            glow_alpha = int((3 - instructor_dist) / 3 * 60)
            glow_radius = int(TILE_SIZE * 0.8)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (120, 170, 255, glow_alpha), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (instructor_x + TILE_SIZE//2 - glow_radius, 
                                   instructor_y + TILE_SIZE//2 - glow_radius))
        
        # Draw instructor sprite
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            self.game.player.draw_at_position(screen, instructor_x, instructor_y, 
                                            self.workshop_instructor['facing'])
        else:
            pygame.draw.circle(screen, (0, 150, 100), 
                             (instructor_x + TILE_SIZE//2, instructor_y + TILE_SIZE//2), 
                             TILE_SIZE // 3)
        
        # Draw name label for instructor if close
        if instructor_dist < 2:
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(self.workshop_instructor['name'], True, (255, 255, 255))
            name_x = instructor_x + TILE_SIZE//2 - name_text.get_width()//2
            name_y = instructor_y - 10
            screen.blit(name_text, (name_x, name_y))
        
        # Draw application desk person
        desk_x = self.room_x + self.application_desk['x'] * TILE_SIZE + self.camera_x
        desk_y = self.room_y + self.application_desk['y'] * TILE_SIZE + self.camera_y
        
        # Calculate distance to desk person
        desk_dist = math.sqrt((self.application_desk['x'] - self.player_x)**2 + 
                             (self.application_desk['y'] - self.player_y)**2)
        
        # Draw glow if player is near
        if desk_dist < 3:
            glow_alpha = int((3 - desk_dist) / 3 * 60)
            glow_radius = int(TILE_SIZE * 0.8)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 170, 120, glow_alpha), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (desk_x + TILE_SIZE//2 - glow_radius, 
                                   desk_y + TILE_SIZE//2 - glow_radius))
        
        # Draw desk person sprite
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            self.game.player.draw_at_position(screen, desk_x, desk_y, 
                                            self.application_desk['facing'])
        else:
            pygame.draw.circle(screen, (100, 0, 150), 
                             (desk_x + TILE_SIZE//2, desk_y + TILE_SIZE//2), 
                             TILE_SIZE // 3)
        
        # Draw name label for desk person if close
        if desk_dist < 2:
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(self.application_desk['name'], True, (255, 255, 255))
            name_x = desk_x + TILE_SIZE//2 - name_text.get_width()//2
            name_y = desk_y - 10
            screen.blit(name_text, (name_x, name_y))
            
    def take_debug_screenshot(self):
        """Take a debug screenshot with information overlay"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"community_center_debug_{timestamp}.png"
        pygame.image.save(self.game.screen, filename)
        print(f"Debug screenshot saved as {filename}")
        print(f"  Room size: {self.room_width}x{self.room_height} tiles")
        print(f"  Room position: ({self.room_x}, {self.room_y})")
        print(f"  Player position: ({self.player_x}, {self.player_y})")
        print(f"  Camera offset: ({self.camera_x}, {self.camera_y})")
        print(f"  Screen size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        
    def draw_debug_overlay(self, screen):
        """Draw debug information overlay"""
        if not self.debug_mode:
            return
            
        # Draw room boundary
        room_screen_x = self.room_x + self.camera_x
        room_screen_y = self.room_y + self.camera_y
        room_screen_width = self.room_width * TILE_SIZE
        room_screen_height = self.room_height * TILE_SIZE
        
        # Room boundary (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (room_screen_x, room_screen_y, room_screen_width, room_screen_height), 3)
        
        # Draw grid lines every 5 tiles
        for x in range(0, self.room_width, 5):
            line_x = room_screen_x + x * TILE_SIZE
            if -100 < line_x < SCREEN_WIDTH + 100:
                pygame.draw.line(screen, (100, 100, 100), 
                               (line_x, max(0, room_screen_y)), 
                               (line_x, min(SCREEN_HEIGHT, room_screen_y + room_screen_height)), 1)
                # Draw coordinate
                coord_text = self.debug_font.render(str(x), True, (255, 255, 0))
                screen.blit(coord_text, (line_x + 2, max(5, room_screen_y + 5)))
                
        for y in range(0, self.room_height, 5):
            line_y = room_screen_y + y * TILE_SIZE
            if -100 < line_y < SCREEN_HEIGHT + 100:
                pygame.draw.line(screen, (100, 100, 100), 
                               (max(0, room_screen_x), line_y), 
                               (min(SCREEN_WIDTH, room_screen_x + room_screen_width), line_y), 1)
                # Draw coordinate
                coord_text = self.debug_font.render(str(y), True, (255, 255, 0))
                screen.blit(coord_text, (max(5, room_screen_x + 5), line_y + 2))
        
        # Draw debug info panel
        debug_info = [
            f"Community Center Debug Info",
            f"Room: {self.room_width}x{self.room_height} tiles ({room_screen_width}x{room_screen_height}px)",
            f"Total tiles: {self.room_width * self.room_height}, Drawn: {getattr(self, 'tiles_drawn', 0)}",
            f"Room pos: ({self.room_x}, {self.room_y})",
            f"Camera: ({self.camera_x}, {self.camera_y})",
            f"Player tile: ({self.player_x}, {self.player_y})",
            f"Player screen: ({self.room_x + self.player_x * TILE_SIZE + self.camera_x}, {self.room_y + self.player_y * TILE_SIZE + self.camera_y})",
            f"Room on screen: ({room_screen_x}, {room_screen_y})",
            "Press F9 for screenshot, F10 to toggle debug"
        ]
        
        # Background for text
        panel_height = len(debug_info) * 22 + 10
        pygame.draw.rect(screen, (0, 0, 0, 180), (5, 5, 500, panel_height))
        pygame.draw.rect(screen, (255, 255, 0), (5, 5, 500, panel_height), 2)
        
        # Draw text
        y_offset = 10
        for line in debug_info:
            text = self.debug_font.render(line, True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 22
            
        # Highlight player position with a yellow box
        player_screen_x = self.room_x + self.player_x * TILE_SIZE + self.camera_x
        player_screen_y = self.room_y + self.player_y * TILE_SIZE + self.camera_y
        pygame.draw.rect(screen, (255, 255, 0), 
                        (player_screen_x, player_screen_y, TILE_SIZE, TILE_SIZE), 3)
        
        # Draw center crosshair
        pygame.draw.line(screen, (0, 255, 0), 
                        (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2), 
                        (SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2), 2)
        pygame.draw.line(screen, (0, 255, 0), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20), 2)
        
    def draw_custom_ui(self, screen):
        """Draw community center specific UI elements"""
        # Instructions
        font = pygame.font.Font(None, 24)
        
        instruction_text = None
        if self.is_near_workshop_instructor() and not self.workshop_complete:
            instruction_text = "Press SPACE to attend Life Skills Workshop"
        elif self.is_near_application_desk() and not self.application_submitted:
            instruction_text = "Press SPACE to submit TLP Application"
            
        if instruction_text:
            text = font.render(instruction_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
            
        # Room name
        title = font.render("Community Center", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (0, 0, 0), title_rect.inflate(20, 10))
        screen.blit(title, title_rect)
        
        # Show completed activities
        status_y = 60
        if self.workshop_complete:
            status = font.render("✓ Life Skills Workshop Complete", True, (0, 255, 0))
            status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, status_y))
            screen.blit(status, status_rect)
            status_y += 30
            
        if self.application_submitted:
            status = font.render("✓ TLP Application Submitted", True, (0, 255, 0))
            status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, status_y))
            screen.blit(status, status_rect)
            

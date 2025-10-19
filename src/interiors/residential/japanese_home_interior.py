import pygame
import json
import os
from .home_interior import HomeInterior
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class JapaneseHomeAuto(HomeInterior):
    """Japanese home that automatically loads blocks from editor saves"""
    
    def __init__(self, game, room_name="japenese_home"):
        # Call parent to load tilemap
        super().__init__(game, room_name)
        
        # Debug visualization
        self.show_blocks = False  # Start with blocks OFF
        self.block_alpha = 120
        
        # Initialize empty sets
        self.walls = set()
        self.furniture_tiles = set()
        self.interaction_zones = {}
        
        # Auto-load from saved file
        self.load_blocks_from_file()
        
    def load_blocks_from_file(self):
        """Automatically load blocks from the editor save file"""
        filename = f"{self.room_name}_blocks.json"
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Load walls
                self.walls = set(tuple(pos) for pos in data.get('walls', []))
                
                # Load furniture
                self.furniture_tiles = set(tuple(pos) for pos in data.get('furniture', []))
                
                # Load and process interactions
                interaction_tiles = set(tuple(pos) for pos in data.get('interactions', []))
                self.process_interaction_zones(interaction_tiles)
                
                print(f"Auto-loaded blocks from {filename}:")
                print(f"  - {len(self.walls)} walls")
                print(f"  - {len(self.furniture_tiles)} furniture")
                print(f"  - {len(self.interaction_zones)} interaction zones")
                
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                self.fallback_generation()
        else:
            print(f"No saved blocks found ({filename}), using defaults")
            self.fallback_generation()
            
    def process_interaction_zones(self, interaction_tiles):
        """Convert interaction tiles into grouped zones"""
        # Group connected tiles
        used = set()
        zone_id = 0
        
        for tile in interaction_tiles:
            if tile not in used:
                # Find all connected tiles
                group = self.find_connected_tiles(tile, interaction_tiles, used)
                if group:
                    x_coords = [p[0] for p in group]
                    y_coords = [p[1] for p in group]
                    
                    # Determine zone type based on location
                    zone_name, message = self.identify_zone_type(group)
                    
                    self.interaction_zones[zone_name] = {
                        'x': x_coords,
                        'y': y_coords,
                        'message': message
                    }
                    zone_id += 1
                    
    def find_connected_tiles(self, start, tile_set, used):
        """Find all tiles connected to start tile"""
        group = []
        stack = [start]
        
        while stack:
            current = stack.pop()
            if current in used or current not in tile_set:
                continue
                
            used.add(current)
            group.append(current)
            
            # Check adjacent tiles
            x, y = current
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                adj = (x + dx, y + dy)
                if adj in tile_set and adj not in used:
                    stack.append(adj)
                    
        return group
        
    def identify_zone_type(self, tiles):
        """Identify what type of interaction zone this is based on location"""
        # Get average position
        avg_x = sum(t[0] for t in tiles) / len(tiles)
        avg_y = sum(t[1] for t in tiles) / len(tiles)
        
        # Based on the updated blocks file, bed is now around (14-17, 3-4)
        # Check if this is the bed area
        if 13 <= avg_x <= 17 and 3 <= avg_y <= 4:
            # This is the bed! Update parent's bed position
            if hasattr(self, 'bed_position'):
                # Find the actual furniture tiles nearby to get exact bed position
                bed_furniture = []
                for fx, fy in self.furniture_tiles:
                    if 14 <= fx <= 17 and 1 <= fy <= 2:
                        bed_furniture.append((fx, fy))
                
                if bed_furniture:
                    # Get min x,y for bed position
                    min_x = min(pos[0] for pos in bed_furniture)
                    min_y = min(pos[1] for pos in bed_furniture)
                    self.bed_position = (min_x, min_y)
                    print(f"Updated bed position to: {self.bed_position}")
            
            return "bed", "Your futon bed. Rest here to save your progress."
        
        # Near kitchen (typically upper left)
        elif avg_x < 5 and avg_y < 3:
            return "kitchen", "A traditional Japanese kitchen."
        
        # Near center (table)
        elif 7 <= avg_x <= 11 and 5 <= avg_y <= 8:
            return "table", "A low dining table with floor cushions."
        
        # Near exit (bottom center)
        elif 8 <= avg_x <= 10 and avg_y > 10:
            return "exit", "Press E to exit"
        
        # Default
        else:
            return f"zone_{int(avg_x)}_{int(avg_y)}", "Press E to interact"
            
    def fallback_generation(self):
        """Generate default blocks if no save file exists"""
        # Add perimeter walls
        for x in range(self.room_width):
            self.walls.add((x, 0))
            if x != 9:  # Leave door at center
                self.walls.add((x, self.room_height - 1))
                
        for y in range(self.room_height):
            self.walls.add((0, y))
            self.walls.add((self.room_width - 1, y))
            
        # Add some default furniture based on bed position
        if hasattr(self, 'bed_x') and hasattr(self, 'bed_y'):
            for dx in range(2):
                for dy in range(2):
                    self.furniture_tiles.add((self.bed_x + dx, self.bed_y + dy))
                    
    def handle_event(self, event):
        """Handle events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                self.show_blocks = not self.show_blocks
                if self.show_blocks:
                    print("Debug blocks: ON")
                else:
                    print("Debug blocks: OFF")
                    
            elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Ctrl+R to reload blocks from file
                self.load_blocks_from_file()
                print("Reloaded blocks from file")
                
            elif event.key == pygame.K_e:
                # Check interactions using internal player position
                for zone_name, zone in self.interaction_zones.items():
                    if self.player_x in zone['x'] and self.player_y in zone['y']:
                        print(f"Interaction: {zone['message']}")
                        
                        # Special actions
                        if zone_name == 'bed':
                            # Trigger sleep if we have the method
                            if hasattr(self, 'start_sleeping'):
                                self.start_sleeping()
                            else:
                                print("Sleeping...")
                                # Set sleeping flag for parent class
                                self.sleeping = True
                                self.sleep_timer = 0
                                if hasattr(self, 'sleep_overlay_alpha'):
                                    self.sleep_overlay_alpha = 0
                        elif zone_name == 'exit':
                            self.exit()
                        break
                        
    def check_collision(self, x, y):
        """Check collision with blocks"""
        # Boundaries
        if x < 0 or x >= self.room_width or y < 0 or y >= self.room_height:
            return True
            
        # Check saved blocks
        if (x, y) in self.walls or (x, y) in self.furniture_tiles:
            return True
            
        return False
        
    def handle_input(self, keys):
        """Handle input with proper collision detection"""
        # Let parent handle the base input (it manages player_x, player_y internally)
        # But we need to override collision checking
        if self.sleeping:
            return
            
        # Movement (following parent's pattern)
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
                
            # Check collision using our loaded blocks
            if new_x != self.player_x or new_y != self.player_y:
                if not self.check_collision(new_x, new_y):
                    self.player_start_x = self.player_x
                    self.player_start_y = self.player_y
                    self.player_target_x = new_x
                    self.player_target_y = new_y
                    self.player_moving = True
                    self.player_move_progress = 0.0
        
    def draw(self, screen):
        """Draw tilemap with block overlay"""
        # Draw tilemap
        super().draw(screen)
        
        # Draw blocks if enabled
        if self.show_blocks and self.transition_state == "active":
            self.draw_debug_blocks(screen)
            
    def draw_debug_blocks(self, screen):
        """Draw the debug block overlay"""
        # Create surfaces
        wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall_surface.set_alpha(self.block_alpha)
        wall_surface.fill((255, 0, 0))
        
        furniture_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        furniture_surface.set_alpha(self.block_alpha)
        furniture_surface.fill((255, 165, 0))
        
        interaction_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        interaction_surface.set_alpha(self.block_alpha)
        interaction_surface.fill((0, 255, 0))
        
        # Draw blocks
        for x, y in self.walls:
            screen_x = self.room_x + x * TILE_SIZE
            screen_y = self.room_y + y * TILE_SIZE
            screen.blit(wall_surface, (screen_x, screen_y))
            
        for x, y in self.furniture_tiles:
            screen_x = self.room_x + x * TILE_SIZE
            screen_y = self.room_y + y * TILE_SIZE
            screen.blit(furniture_surface, (screen_x, screen_y))
            
        # Draw all interaction zones
        for zone_name, zone in self.interaction_zones.items():
            for i in range(len(zone['x'])):
                x = zone['x'][i]
                y = zone['y'][i]
                screen_x = self.room_x + x * TILE_SIZE
                screen_y = self.room_y + y * TILE_SIZE
                screen.blit(interaction_surface, (screen_x, screen_y))
                
        # Show controls hint
        font = pygame.font.Font(None, 16)
        if not self.show_blocks:
            # Just show F3 hint when blocks are off
            hint = font.render("Press F3 to show debug blocks", True, (150, 150, 150))
            screen.blit(hint, (10, 10))
        else:
            # Show full legend when blocks are on
            legend_items = [
                ("Debug Blocks ON (F3 to hide)", (255, 255, 255)),
                ("Reload (Ctrl+R)", (255, 255, 100))
            ]
            
            y = 10
            for text, color in legend_items:
                surface = font.render(text, True, color)
                screen.blit(surface, (10, y))
                y += 20
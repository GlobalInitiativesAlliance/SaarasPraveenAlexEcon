import pygame
import json
import os
from japanese_home_enhanced import JapaneseHomeEnhanced
from constants import *

class TilemapBlockEditor:
    def __init__(self, room_name="japenese_home"):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + 300, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Tilemap Block Editor - {room_name}")
        self.clock = pygame.time.Clock()
        
        # Mock game setup
        self.game = type('obj', (object,), {})()
        self.game.player = type('obj', (object,), {
            'x': 10, 'y': 10, 
            'pixel_x': 10 * TILE_SIZE, 
            'pixel_y': 10 * TILE_SIZE,
            'tile_size': TILE_SIZE
        })()
        self.game.screen = self.screen
        
        # Load the room
        self.room_name = room_name
        self.interior = JapaneseHomeEnhanced(self.game, room_name)
        self.interior.player = self.game.player
        self.interior.enter()
        self.interior.transition_state = "active"
        self.interior.transition_alpha = 0
        
        # Editor state
        self.mode = 'wall'  # wall, furniture, interaction, erase
        self.show_blocks = True
        self.show_grid = True
        self.selected_tile = None
        self.hover_tile = None
        
        # Copy the current blocks for editing
        self.edited_walls = set()
        self.edited_furniture = set()
        self.edited_interactions = set()
        
        # UI
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # History for undo (must be before load_from_file)
        self.history = []
        
        # UI feedback
        self.show_save_message = False
        self.save_message_timer = 0
        
        # Load existing blocks from file if it exists
        self.load_from_file(silent=True)
        
    def generate_interaction_zones(self):
        """Generate interaction zones based on furniture"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for fx, fy in self.edited_furniture:
            for dx, dy in directions:
                x, y = fx + dx, fy + dy
                if (x, y) not in self.edited_walls and \
                   (x, y) not in self.edited_furniture and \
                   0 <= x < self.interior.room_width and \
                   0 <= y < self.interior.room_height:
                    self.edited_interactions.add((x, y))
                    
    def save_state(self):
        """Save current state for undo"""
        self.history.append({
            'walls': set(self.edited_walls),
            'furniture': set(self.edited_furniture),
            'interactions': set(self.edited_interactions)
        })
        # Keep only last 50 states
        if len(self.history) > 50:
            self.history.pop(0)
            
    def undo(self):
        """Undo last action"""
        if len(self.history) > 1:
            self.history.pop()  # Remove current state
            state = self.history[-1]
            self.edited_walls = set(state['walls'])
            self.edited_furniture = set(state['furniture'])
            self.edited_interactions = set(state['interactions'])
            
    def screen_to_tile(self, pos):
        """Convert screen position to tile coordinates"""
        x = (pos[0] - self.interior.room_x) // TILE_SIZE
        y = (pos[1] - self.interior.room_y) // TILE_SIZE
        if 0 <= x < self.interior.room_width and 0 <= y < self.interior.room_height:
            return (x, y)
        return None
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for editing"""
        tile = self.screen_to_tile(pos)
        if not tile:
            return
            
        x, y = tile
        changed = False
        
        if self.mode == 'erase':  # Erase mode - remove from all sets
            if (x, y) in self.edited_walls:
                self.edited_walls.remove((x, y))
                changed = True
            if (x, y) in self.edited_furniture:
                self.edited_furniture.remove((x, y))
                changed = True
            if (x, y) in self.edited_interactions:
                self.edited_interactions.remove((x, y))
                changed = True
        elif button == 1:  # Left click - add
            if self.mode == 'wall':
                if (x, y) not in self.edited_walls:
                    self.edited_walls.add((x, y))
                    # Remove from other sets
                    self.edited_furniture.discard((x, y))
                    self.edited_interactions.discard((x, y))
                    changed = True
            elif self.mode == 'furniture':
                if (x, y) not in self.edited_furniture:
                    self.edited_furniture.add((x, y))
                    # Remove from other sets
                    self.edited_walls.discard((x, y))
                    self.edited_interactions.discard((x, y))
                    changed = True
            elif self.mode == 'interaction':
                if (x, y) not in self.edited_interactions:
                    self.edited_interactions.add((x, y))
                    # Remove from solid sets
                    self.edited_walls.discard((x, y))
                    self.edited_furniture.discard((x, y))
                    changed = True
                    
        elif button == 3:  # Right click - remove
            if (x, y) in self.edited_walls:
                self.edited_walls.remove((x, y))
                changed = True
            if (x, y) in self.edited_furniture:
                self.edited_furniture.remove((x, y))
                changed = True
            if (x, y) in self.edited_interactions:
                self.edited_interactions.remove((x, y))
                changed = True
                
        if changed:
            self.save_state()
            
    def export_code(self):
        """Export the edited blocks as code"""
        print("\n" + "="*60)
        print("GENERATED CODE FOR JAPANESE HOME")
        print("="*60)
        print("\nAdd this to your JapaneseHomeEnhanced class:\n")
        
        print("def add_known_furniture(self):")
        print("    \"\"\"Manually defined collision and interaction zones\"\"")
        print("    ")
        print("    # Clear existing data")
        print("    self.walls.clear()")
        print("    self.furniture_tiles.clear()")
        print("    ")
        
        # Export walls
        print("    # Wall tiles")
        print("    wall_positions = [")
        for pos in sorted(self.edited_walls):
            print(f"        {pos},")
        print("    ]")
        print("    self.walls.update(wall_positions)")
        print("    ")
        
        # Export furniture
        print("    # Furniture tiles")
        print("    furniture_positions = [")
        for pos in sorted(self.edited_furniture):
            print(f"        {pos},")
        print("    ]")
        print("    self.furniture_tiles.update(furniture_positions)")
        print("    ")
        
        # Export interaction zones
        print("    # Interaction zones")
        print("    self.interaction_zones = {")
        
        # Group interactions by proximity
        used = set()
        zone_id = 0
        for pos in sorted(self.edited_interactions):
            if pos not in used:
                # Find all connected interaction tiles
                group = self.find_connected_tiles(pos, self.edited_interactions, used)
                if group:
                    x_coords = [p[0] for p in group]
                    y_coords = [p[1] for p in group]
                    print(f"        'zone_{zone_id}': {{")
                    print(f"            'x': {x_coords},")
                    print(f"            'y': {y_coords},")
                    print(f"            'message': 'Interaction zone {zone_id}'")
                    print("        },")
                    zone_id += 1
                    
        print("    }")
        print("\n" + "="*60 + "\n")
        
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
        
    def save_to_file(self):
        """Save the edited blocks to a JSON file"""
        data = {
            'room_name': self.room_name,
            'walls': list(self.edited_walls),
            'furniture': list(self.edited_furniture),
            'interactions': list(self.edited_interactions)
        }
        
        filename = f"{self.room_name}_blocks.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved to {filename}")
        print("Changes will be automatically loaded in the game!")
        print("(In-game: Press Ctrl+R to reload if already playing)")
        
        # Show visual feedback
        self.show_save_message = True
        self.save_message_timer = 3.0
        
    def load_from_file(self, silent=False):
        """Load blocks from a JSON file"""
        filename = f"{self.room_name}_blocks.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            self.edited_walls = set(tuple(pos) for pos in data.get('walls', []))
            self.edited_furniture = set(tuple(pos) for pos in data.get('furniture', []))
            self.edited_interactions = set(tuple(pos) for pos in data.get('interactions', []))
            self.save_state()
            if not silent:
                print(f"Loaded from {filename}")
            
    def run(self):
        print("\nTILEMAP BLOCK EDITOR")
        print("====================")
        print("Edit collision blocks and interaction zones")
        print("\nControls:")
        print("- Left Click: Add block")
        print("- Right Click: Remove block")
        print("- 1-4: Switch modes (Wall/Furniture/Interaction/Erase)")
        print("- G: Toggle grid")
        print("- B: Toggle blocks visibility")
        print("- R: Regenerate interaction zones")
        print("- Z: Undo")
        print("- S: Save to file")
        print("- L: Load from file")
        print("- E: Export as code")
        print("- ESC: Exit")
        
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEMOTION:
                    self.hover_tile = self.screen_to_tile(event.pos)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos, event.button)
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_1:
                        self.mode = 'wall'
                    elif event.key == pygame.K_2:
                        self.mode = 'furniture'
                    elif event.key == pygame.K_3:
                        self.mode = 'interaction'
                    elif event.key == pygame.K_4:
                        self.mode = 'erase'
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_b:
                        self.show_blocks = not self.show_blocks
                    elif event.key == pygame.K_r:
                        self.edited_interactions.clear()
                        self.generate_interaction_zones()
                        self.save_state()
                    elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.undo()
                    elif event.key == pygame.K_s:
                        self.save_to_file()
                    elif event.key == pygame.K_l:
                        self.load_from_file()
                    elif event.key == pygame.K_e:
                        self.export_code()
                        
            # Update interior
            self.interior.update(dt)
            
            # Update UI timers
            if self.show_save_message:
                self.save_message_timer -= dt
                if self.save_message_timer <= 0:
                    self.show_save_message = False
            
            # Draw everything
            self.draw()
            
        pygame.quit()
        
    def draw(self):
        """Draw the editor"""
        self.screen.fill((20, 20, 20))
        
        # Draw the tilemap
        self.interior.show_blocks = False
        self.interior.draw(self.screen)
        
        # Draw custom blocks
        if self.show_blocks:
            self.draw_blocks()
            
        # Draw grid
        if self.show_grid:
            self.draw_grid()
            
        # Draw hover highlight
        if self.hover_tile:
            x, y = self.hover_tile
            screen_x = self.interior.room_x + x * TILE_SIZE
            screen_y = self.interior.room_y + y * TILE_SIZE
            
            # Different colors for different modes
            colors = {
                'wall': (255, 100, 100),
                'furniture': (255, 200, 100),
                'interaction': (100, 255, 100),
                'erase': (255, 255, 255)
            }
            color = colors.get(self.mode, (200, 200, 200))
            pygame.draw.rect(self.screen, color, 
                           (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 2)
            
        # Draw UI
        self.draw_ui()
        
        # Draw save message if active
        if self.show_save_message:
            self.draw_save_message()
        
        pygame.display.flip()
        
    def draw_blocks(self):
        """Draw the edited blocks"""
        # Create surfaces - match exactly what's in japanese_home_auto.py
        wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall_surface.set_alpha(120)  # Same alpha as game
        wall_surface.fill((255, 0, 0))  # Red for walls
        
        furniture_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        furniture_surface.set_alpha(120)  # Same alpha as game
        furniture_surface.fill((255, 165, 0))  # Orange for furniture
        
        interaction_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        interaction_surface.set_alpha(120)  # Same alpha as game
        interaction_surface.fill((0, 255, 0))  # Green for interactions
        
        # Draw blocks
        for x, y in self.edited_walls:
            screen_x = self.interior.room_x + x * TILE_SIZE
            screen_y = self.interior.room_y + y * TILE_SIZE
            self.screen.blit(wall_surface, (screen_x, screen_y))
            
        for x, y in self.edited_furniture:
            screen_x = self.interior.room_x + x * TILE_SIZE
            screen_y = self.interior.room_y + y * TILE_SIZE
            self.screen.blit(furniture_surface, (screen_x, screen_y))
            
        for x, y in self.edited_interactions:
            screen_x = self.interior.room_x + x * TILE_SIZE
            screen_y = self.interior.room_y + y * TILE_SIZE
            self.screen.blit(interaction_surface, (screen_x, screen_y))
            
    def draw_grid(self):
        """Draw tile grid"""
        grid_color = (60, 60, 60)
        
        # Vertical lines
        for x in range(self.interior.room_width + 1):
            screen_x = self.interior.room_x + x * TILE_SIZE
            pygame.draw.line(self.screen, grid_color,
                           (screen_x, self.interior.room_y),
                           (screen_x, self.interior.room_y + self.interior.room_height * TILE_SIZE))
                           
        # Horizontal lines
        for y in range(self.interior.room_height + 1):
            screen_y = self.interior.room_y + y * TILE_SIZE
            pygame.draw.line(self.screen, grid_color,
                           (self.interior.room_x, screen_y),
                           (self.interior.room_x + self.interior.room_width * TILE_SIZE, screen_y))
                           
    def draw_ui(self):
        """Draw UI panel"""
        ui_x = SCREEN_WIDTH + 20
        y_offset = 20
        
        # Title
        title = self.font.render("BLOCK EDITOR", True, (255, 255, 255))
        self.screen.blit(title, (ui_x, y_offset))
        y_offset += 30
        
        # Current mode
        mode_colors = {
            'wall': (255, 100, 100),
            'furniture': (255, 165, 0),
            'interaction': (0, 255, 0),
            'erase': (255, 255, 255)
        }
        mode_text = self.font.render(f"Mode: {self.mode.upper()}", True, 
                                   mode_colors.get(self.mode, (255, 255, 255)))
        self.screen.blit(mode_text, (ui_x, y_offset))
        y_offset += 30
        
        # Stats
        stats = [
            f"Walls: {len(self.edited_walls)}",
            f"Furniture: {len(self.edited_furniture)}",
            f"Interactions: {len(self.edited_interactions)}",
            "",
            f"Grid: {'ON' if self.show_grid else 'OFF'}",
            f"Blocks: {'ON' if self.show_blocks else 'OFF'}"
        ]
        
        for stat in stats:
            if stat:
                text = self.small_font.render(stat, True, (200, 200, 200))
                self.screen.blit(text, (ui_x, y_offset))
            y_offset += 20
            
        # Mouse position
        if self.hover_tile:
            y_offset += 20
            pos_text = self.small_font.render(f"Tile: {self.hover_tile}", True, (255, 255, 100))
            self.screen.blit(pos_text, (ui_x, y_offset))
            
    def draw_save_message(self):
        """Draw save success message"""
        msg_font = pygame.font.Font(None, 36)
        msg_text = "SAVED! Changes will auto-load in game"
        text_surface = msg_font.render(msg_text, True, (0, 255, 0))
        
        # Create background
        padding = 20
        bg_rect = text_surface.get_rect()
        bg_rect.inflate_ip(padding * 2, padding)
        bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Draw background
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.fill((0, 0, 0))
        bg_surface.set_alpha(200)
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, (0, 255, 0), bg_rect, 3)
        
        # Draw text
        text_rect = text_surface.get_rect(center=bg_rect.center)
        self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    editor = TilemapBlockEditor("japenese_home")
    editor.run()
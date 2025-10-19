import pygame
import sys
import json
import os

pygame.init()

# Constants
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BG_COLOR = (30, 30, 40)
GRID_COLOR = (60, 60, 70)
SELECTED_COLOR = (255, 255, 0)
HOVER_COLOR = (100, 100, 150)
TEXT_COLOR = (255, 255, 255)
PREVIEW_BG = (50, 50, 60)

class InteriorThemeEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Interior Theme Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Interior sprite sheets
        self.sheet_names = [
            'TopDownHouse_FloorsAndWalls.png',
            'TopDownHouse_FurnitureState1.png',
            'TopDownHouse_SmallItems.png',
            'TopDownHouse_DoorsAndWindows.png'
        ]
        self.sheets = {}
        self.current_sheet_index = 0
        self.load_sheets()
        
        # Theme data
        self.themes = {}
        self.current_theme = "custom_theme"
        self.load_themes()
        
        # Current selections
        self.current_category = "floor"  # floor, walls, furniture, doors
        self.selected_tiles = {
            "floor": [],
            "walls": [],
            "furniture": {},
            "doors": {}
        }
        
        # UI State
        self.hover_tile = None
        self.scroll_x = 0
        self.scroll_y = 0
        self.preview_room = True
        
        # Input state
        self.input_active = False
        self.input_text = ""
        self.input_type = None  # "theme_name", "furniture_name", etc.
        
    def load_sheets(self):
        """Load interior tileset images"""
        base_dir = "Top-Down_Retro_Interior"
        
        for sheet_name in self.sheet_names:
            try:
                path = os.path.join(base_dir, sheet_name)
                self.sheets[sheet_name] = pygame.image.load(path).convert_alpha()
                print(f"Loaded {sheet_name}")
            except Exception as e:
                print(f"Failed to load {sheet_name}: {e}")
                # Create placeholder
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((100, 0, 0))
                
    def load_themes(self):
        """Load existing themes"""
        try:
            with open("interior_themes.json", "r") as f:
                data = json.load(f)
                self.themes = data.get("themes", {})
                print(f"Loaded {len(self.themes)} themes")
        except:
            print("No themes file found")
            
    def save_themes(self):
        """Save all themes"""
        # First load existing unique items
        unique_items = {}
        try:
            with open("tile_selections_unique.json", "r") as f:
                data = json.load(f)
                unique_items = data.get("unique_items", {})
        except:
            pass
            
        # Add interior tiles to unique items
        tile_counter = 0
        for theme_name, theme_data in self.themes.items():
            # Add floor tiles
            if "floor" in theme_data:
                for i, tile in enumerate(theme_data["floor"].get("tiles", [])):
                    tile_name = f"interior_{theme_name}_floor_{i}"
                    if tile_name not in unique_items:
                        unique_items[tile_name] = {
                            "type": "tile",
                            "tile": tile,
                            "size": (1, 1)
                        }
                        tile_counter += 1
                        
            # Add wall tiles
            if "walls" in theme_data:
                for i, tile in enumerate(theme_data["walls"].get("tiles", [])):
                    tile_name = f"interior_{theme_name}_wall_{i}"
                    if tile_name not in unique_items:
                        unique_items[tile_name] = {
                            "type": "tile",
                            "tile": tile,
                            "size": (1, 1)
                        }
                        tile_counter += 1
                        
        # Save updated unique items
        with open("tile_selections_unique.json", "w") as f:
            json.dump({"unique_items": unique_items}, f, indent=2)
            
        # Save themes
        save_data = {"themes": self.themes}
        with open("interior_themes.json", "w") as f:
            json.dump(save_data, f, indent=2)
            
        print(f"Saved themes and added {tile_counter} interior tiles")
        
    def get_tile_at_pos(self, mx, my):
        """Get tile coordinates at mouse position"""
        if mx < 400:  # Left panel
            return None
            
        sheet_name = self.sheet_names[self.current_sheet_index]
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            return None
            
        grid_x = (mx - 400 + self.scroll_x) // TILE_SIZE
        grid_y = (my - 150 + self.scroll_y) // TILE_SIZE
        
        max_x = sheet.get_width() // ORIGINAL_TILE_SIZE
        max_y = sheet.get_height() // ORIGINAL_TILE_SIZE
        
        if 0 <= grid_x < max_x and 0 <= grid_y < max_y:
            return (sheet_name, grid_x, grid_y)
        return None
        
    def get_tile_surface(self, tile_info):
        """Get tile surface for preview"""
        if not tile_info or len(tile_info) != 3:
            return None
            
        sheet_name, x, y = tile_info
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            return None
            
        try:
            rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                             ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
            tile = sheet.subsurface(rect)
            return pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
        except:
            return None
            
    def draw_ui(self):
        """Draw the main UI"""
        self.screen.fill(BG_COLOR)
        
        # Left panel - Theme controls
        panel_width = 380
        pygame.draw.rect(self.screen, (40, 40, 50), (0, 0, panel_width, SCREEN_HEIGHT))
        
        # Title
        title = self.font.render("INTERIOR THEME EDITOR", True, TEXT_COLOR)
        self.screen.blit(title, (10, 10))
        
        # Current theme
        theme_text = self.small_font.render(f"Theme: {self.current_theme}", True, TEXT_COLOR)
        self.screen.blit(theme_text, (10, 40))
        
        # Category buttons
        categories = ["floor", "walls", "furniture", "doors"]
        y_offset = 80
        for cat in categories:
            color = SELECTED_COLOR if cat == self.current_category else TEXT_COLOR
            cat_text = self.font.render(cat.title(), True, color)
            self.screen.blit(cat_text, (10, y_offset))
            y_offset += 35
            
        # Selected tiles for current category
        y_offset = 250
        selected_text = self.font.render(f"Selected {self.current_category}:", True, TEXT_COLOR)
        self.screen.blit(selected_text, (10, y_offset))
        y_offset += 30
        
        if self.current_category in ["floor", "walls"]:
            tiles = self.selected_tiles.get(self.current_category, [])
            for i, tile in enumerate(tiles):
                # Draw tile preview
                tile_surf = self.get_tile_surface(tile)
                if tile_surf:
                    self.screen.blit(tile_surf, (10 + i * 40, y_offset))
        
        # Room preview
        if self.preview_room:
            self.draw_room_preview()
            
        # Top bar - sheet selection
        pygame.draw.rect(self.screen, (40, 40, 50), (panel_width, 0, SCREEN_WIDTH - panel_width, 140))
        sheet_text = self.font.render(f"Sheet: {self.sheet_names[self.current_sheet_index]}", 
                                    True, TEXT_COLOR)
        self.screen.blit(sheet_text, (panel_width + 10, 10))
        
        # Controls
        controls = [
            "Tab: Next sheet",
            "Click: Select tile",
            "S: Save theme",
            "L: Load themes",
            "N: New theme",
            "P: Toggle preview"
        ]
        x_offset = panel_width + 10
        y_offset = 40
        for i, control in enumerate(controls):
            if i == 3:
                x_offset += 200
                y_offset = 40
            control_text = self.small_font.render(control, True, (180, 180, 180))
            self.screen.blit(control_text, (x_offset, y_offset))
            y_offset += 20
            
        # Hover info
        if self.hover_tile:
            hover_text = f"Tile: {self.hover_tile[1]}, {self.hover_tile[2]}"
            rendered = self.small_font.render(hover_text, True, TEXT_COLOR)
            self.screen.blit(rendered, (panel_width + 10, 100))
            
        # Input dialog
        if self.input_active:
            self.draw_input_dialog()
            
    def draw_room_preview(self):
        """Draw a preview of the room with current theme"""
        preview_x = 10
        preview_y = 400
        preview_size = 8  # 8x8 room
        tile_size = 20  # Smaller tiles for preview
        
        # Background
        pygame.draw.rect(self.screen, PREVIEW_BG, 
                        (preview_x - 5, preview_y - 5, 
                         preview_size * tile_size + 10, 
                         preview_size * tile_size + 10))
        
        # Draw tiles
        floor_tiles = self.selected_tiles.get("floor", [])
        wall_tiles = self.selected_tiles.get("walls", [])
        
        for y in range(preview_size):
            for x in range(preview_size):
                tile_x = preview_x + x * tile_size
                tile_y = preview_y + y * tile_size
                
                # Walls on edges
                if x == 0 or x == preview_size - 1 or y == 0 or y == preview_size - 1:
                    if wall_tiles:
                        tile_surf = self.get_tile_surface(wall_tiles[0])
                        if tile_surf:
                            scaled = pygame.transform.scale(tile_surf, (tile_size, tile_size))
                            self.screen.blit(scaled, (tile_x, tile_y))
                    else:
                        pygame.draw.rect(self.screen, (100, 90, 80), 
                                       (tile_x, tile_y, tile_size, tile_size))
                else:
                    # Floor
                    if floor_tiles:
                        # Checkerboard pattern if multiple tiles
                        if len(floor_tiles) > 1 and (x + y) % 2 == 1:
                            tile_surf = self.get_tile_surface(floor_tiles[1])
                        else:
                            tile_surf = self.get_tile_surface(floor_tiles[0])
                            
                        if tile_surf:
                            scaled = pygame.transform.scale(tile_surf, (tile_size, tile_size))
                            self.screen.blit(scaled, (tile_x, tile_y))
                    else:
                        pygame.draw.rect(self.screen, (80, 70, 60), 
                                       (tile_x, tile_y, tile_size, tile_size))
                        
        # Label
        label = self.small_font.render("Preview", True, TEXT_COLOR)
        self.screen.blit(label, (preview_x, preview_y - 20))
        
    def draw_tile_grid(self):
        """Draw the sprite sheet grid"""
        sheet_name = self.sheet_names[self.current_sheet_index]
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            return
            
        # Draw tiles
        start_x = self.scroll_x // TILE_SIZE
        start_y = self.scroll_y // TILE_SIZE
        end_x = min((self.scroll_x + SCREEN_WIDTH - 400) // TILE_SIZE + 2,
                    sheet.get_width() // ORIGINAL_TILE_SIZE)
        end_y = min((self.scroll_y + SCREEN_HEIGHT - 150) // TILE_SIZE + 2,
                    sheet.get_height() // ORIGINAL_TILE_SIZE)
                    
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                src_rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                                     ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                try:
                    tile = sheet.subsurface(src_rect)
                    scaled = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
                    
                    screen_x = 400 + x * TILE_SIZE - self.scroll_x
                    screen_y = 150 + y * TILE_SIZE - self.scroll_y
                    
                    self.screen.blit(scaled, (screen_x, screen_y))
                    
                    # Highlight selected tiles
                    tile_info = (sheet_name, x, y)
                    if self.current_category in ["floor", "walls"]:
                        if tile_info in self.selected_tiles.get(self.current_category, []):
                            pygame.draw.rect(self.screen, SELECTED_COLOR, 
                                           (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 2)
                    
                    # Grid
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                   (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
                except:
                    pass
                    
        # Hover highlight
        if self.hover_tile:
            x = 400 + self.hover_tile[1] * TILE_SIZE - self.scroll_x
            y = 150 + self.hover_tile[2] * TILE_SIZE - self.scroll_y
            pygame.draw.rect(self.screen, HOVER_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 2)
            
    def draw_input_dialog(self):
        """Draw input dialog"""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog
        dialog_width = 400
        dialog_height = 150
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        pygame.draw.rect(self.screen, (50, 50, 60), 
                       (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, TEXT_COLOR, 
                       (dialog_x, dialog_y, dialog_width, dialog_height), 2)
                       
        # Prompt
        prompt = "Enter theme name:" if self.input_type == "theme_name" else "Enter name:"
        prompt_text = self.font.render(prompt, True, TEXT_COLOR)
        self.screen.blit(prompt_text, (dialog_x + 20, dialog_y + 20))
        
        # Input field
        input_rect = pygame.Rect(dialog_x + 20, dialog_y + 60, dialog_width - 40, 30)
        pygame.draw.rect(self.screen, (30, 30, 40), input_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, input_rect, 1)
        
        # Text
        text_surface = self.font.render(self.input_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # Instructions
        inst_text = self.small_font.render("Press Enter to confirm, Esc to cancel", 
                                         True, (180, 180, 180))
        self.screen.blit(inst_text, (dialog_x + 20, dialog_y + dialog_height - 30))
        
    def handle_input(self, event):
        """Handle user input"""
        if self.input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.input_type == "theme_name" and self.input_text:
                        self.current_theme = self.input_text
                        self.themes[self.current_theme] = {
                            "name": self.input_text,
                            "floor": {"pattern": "single", "tiles": []},
                            "walls": {"pattern": "single", "tiles": []},
                            "furniture": {},
                            "doors": {}
                        }
                        self.selected_tiles = {
                            "floor": [],
                            "walls": [],
                            "furniture": {},
                            "doors": {}
                        }
                    self.input_active = False
                    self.input_text = ""
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                    self.input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        self.input_text += event.unicode
            return True
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_TAB:
                self.current_sheet_index = (self.current_sheet_index + 1) % len(self.sheet_names)
            elif event.key == pygame.K_s:
                self.save_current_theme()
                self.save_themes()
            elif event.key == pygame.K_l:
                self.load_themes()
            elif event.key == pygame.K_n:
                self.input_active = True
                self.input_type = "theme_name"
                self.input_text = ""
            elif event.key == pygame.K_p:
                self.preview_room = not self.preview_room
            elif event.key == pygame.K_1:
                self.current_category = "floor"
            elif event.key == pygame.K_2:
                self.current_category = "walls"
            elif event.key == pygame.K_3:
                self.current_category = "furniture"
            elif event.key == pygame.K_4:
                self.current_category = "doors"
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = event.pos
                
                # Check category buttons
                if mx < 380:
                    categories = ["floor", "walls", "furniture", "doors"]
                    y_start = 80
                    for i, cat in enumerate(categories):
                        if y_start + i * 35 <= my <= y_start + (i + 1) * 35:
                            self.current_category = cat
                            return True
                
                # Click on tile
                tile = self.get_tile_at_pos(mx, my)
                if tile:
                    if self.current_category in ["floor", "walls"]:
                        current_tiles = self.selected_tiles.get(self.current_category, [])
                        if tile in current_tiles:
                            current_tiles.remove(tile)
                        else:
                            current_tiles.append(tile)
                        self.selected_tiles[self.current_category] = current_tiles
                        
        elif event.type == pygame.MOUSEMOTION:
            self.hover_tile = self.get_tile_at_pos(*event.pos)
            
        elif event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self.scroll_x = max(0, self.scroll_x - event.y * TILE_SIZE)
            else:
                self.scroll_y = max(0, self.scroll_y - event.y * TILE_SIZE)
                
        return True
        
    def save_current_theme(self):
        """Save current selections to theme"""
        if self.current_theme not in self.themes:
            self.themes[self.current_theme] = {
                "name": self.current_theme,
                "floor": {"pattern": "single", "tiles": []},
                "walls": {"pattern": "single", "tiles": []},
                "furniture": {},
                "doors": {}
            }
            
        theme = self.themes[self.current_theme]
        
        # Update floor
        floor_tiles = self.selected_tiles.get("floor", [])
        if floor_tiles:
            pattern = "checkerboard" if len(floor_tiles) > 1 else "single"
            theme["floor"] = {"pattern": pattern, "tiles": floor_tiles}
            
        # Update walls
        wall_tiles = self.selected_tiles.get("walls", [])
        if wall_tiles:
            theme["walls"] = {"pattern": "single", "tiles": wall_tiles}
            
        print(f"Saved theme: {self.current_theme}")
        
    def run(self):
        """Main loop"""
        print("\n=== INTERIOR THEME EDITOR ===")
        print("Select tiles for floors, walls, furniture, and doors")
        print("Press N to create a new theme")
        print("Press S to save your theme\n")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if not self.handle_input(event):
                        running = False
                        
            self.draw_ui()
            self.draw_tile_grid()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
        
if __name__ == "__main__":
    editor = InteriorThemeEditor()
    editor.run()
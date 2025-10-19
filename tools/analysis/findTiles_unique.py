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
SELECTION_COLOR = (255, 100, 100, 128)
BUILDING_PREVIEW_COLOR = (100, 255, 100, 128)


class UniqueTilePicker:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Unique Tile/Building Picker")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Sprite sheets
        self.sheet_names = ['CP_V1.0.4.png', 'BL001.png', 'BD001.png', 'SL001.png']
        self.sheets = {}
        self.current_sheet_index = 0
        self.load_sheets()

        # Scrolling
        self.scroll_x = 0
        self.scroll_y = 0
        self.max_scroll_x = 0
        self.max_scroll_y = 0
        self.update_max_scroll()

        # All selections stored as unique items
        self.unique_items = {}  # {name: data}
        
        # UI State
        self.hover_tile = None
        self.show_help = True
        self.selected_item_name = None
        
        # Text input state
        self.input_active = False
        self.input_text = ""
        self.input_prompt = ""
        self.pending_action = None  # ('tile', tile_info) or ('building', start, end)

        # Rectangle selection for buildings
        self.selecting_rect = False
        self.rect_start = None
        self.rect_end = None

        # Sidebar
        self.sidebar_scroll = 0
        self.max_sidebar_scroll = 0

        # Try to load existing selections
        self.load_selections()

    def load_sheets(self):
        base_dir = os.path.dirname(__file__)
        animations_path = os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations")

        for sheet_name in self.sheet_names:
            try:
                if sheet_name == 'CP_V1.0.4.png':
                    path = os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", sheet_name)
                else:
                    path = os.path.join(animations_path, sheet_name)
                self.sheets[sheet_name] = pygame.image.load(path)
                print(f"Loaded {sheet_name}: {self.sheets[sheet_name].get_size()}")
            except Exception as e:
                print(f"Failed to load {sheet_name}: {e}")
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((100, 0, 0))

    def update_max_scroll(self):
        if self.sheet_names[self.current_sheet_index] in self.sheets:
            sheet = self.sheets[self.sheet_names[self.current_sheet_index]]
            total_width = (sheet.get_width() // ORIGINAL_TILE_SIZE) * TILE_SIZE
            total_height = (sheet.get_height() // ORIGINAL_TILE_SIZE) * TILE_SIZE
            self.max_scroll_x = max(0, total_width - (SCREEN_WIDTH - 300))
            self.max_scroll_y = max(0, total_height - (SCREEN_HEIGHT - 150))

    def save_selections(self):
        """Save all unique items"""
        # Convert to format compatible with the visual map editor
        save_data = {
            'unique_items': self.unique_items
        }
        
        with open("tile_selections_unique.json", "w") as f:
            json.dump(save_data, f, indent=2)

        print(f"Saved {len(self.unique_items)} unique items")

    def load_selections(self):
        """Load previously saved items"""
        try:
            with open("tile_selections_unique.json", "r") as f:
                data = json.load(f)
                self.unique_items = data.get('unique_items', {})
                print(f"Loaded {len(self.unique_items)} unique items")
        except:
            print("No previous selections found, starting fresh")

    def get_tile_at_pos(self, mx, my):
        """Get tile coordinates at mouse position"""
        if mx < 300 or my < 150:
            return None

        sheet_name = self.sheet_names[self.current_sheet_index]
        if sheet_name not in self.sheets:
            return None

        sheet = self.sheets[sheet_name]

        grid_x = (mx - 300 + self.scroll_x) // TILE_SIZE
        grid_y = (my - 150 + self.scroll_y) // TILE_SIZE

        if grid_x * ORIGINAL_TILE_SIZE >= sheet.get_width() or grid_y * ORIGINAL_TILE_SIZE >= sheet.get_height():
            return None

        return (sheet_name, grid_x, grid_y)

    def add_single_tile(self, tile_info):
        """Add a single tile as a unique item"""
        if not tile_info:
            return
            
        # Start text input
        self.input_active = True
        self.input_text = ""
        self.input_prompt = f"Name for tile at ({tile_info[1]}, {tile_info[2]})"
        self.pending_action = ('tile', tile_info)

    def create_building_from_rect(self, start_tile, end_tile):
        """Create a building from rectangle selection"""
        if not start_tile or not end_tile:
            return

        sheet_name = start_tile[0]
        x1, y1 = start_tile[1], start_tile[2]
        x2, y2 = end_tile[1], end_tile[2]

        # Ensure correct order
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Start text input
        self.input_active = True
        self.input_text = ""
        self.input_prompt = f"Name for building ({width}x{height})"
        self.pending_action = ('building', start_tile, end_tile)

    def delete_item(self, name):
        """Delete an item"""
        if name in self.unique_items:
            del self.unique_items[name]
            print(f"Deleted: {name}")
            if self.selected_item_name == name:
                self.selected_item_name = None

    def get_tile_surface(self, tile_info):
        """Get a tile surface for preview"""
        if not tile_info:
            return None
            
        sheet_name, x, y = tile_info
        if sheet_name not in self.sheets:
            return None
            
        sheet = self.sheets[sheet_name]
        try:
            src_rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                                 ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
            return sheet.subsurface(src_rect)
        except:
            return None

    def complete_pending_action(self):
        """Complete the pending action with the entered name"""
        if not self.input_text.strip():
            print("Name required! Item not added.")
            return
            
        name = self.input_text.strip()
        
        if self.pending_action[0] == 'tile':
            tile_info = self.pending_action[1]
            if name in self.unique_items:
                print(f"Warning: Overwriting existing item '{name}'")
                
            self.unique_items[name] = {
                'type': 'tile',
                'tile': tile_info,
                'size': (1, 1)
            }
            print(f"Added tile: {name}")
            
        elif self.pending_action[0] == 'building':
            start_tile = self.pending_action[1]
            end_tile = self.pending_action[2]
            
            sheet_name = start_tile[0]
            x1, y1 = start_tile[1], start_tile[2]
            x2, y2 = end_tile[1], end_tile[2]

            # Ensure correct order
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)

            width = max_x - min_x + 1
            height = max_y - min_y + 1

            # Create building tiles array
            tiles = []
            for y in range(height):
                row = []
                for x in range(width):
                    row.append((sheet_name, min_x + x, min_y + y))
                tiles.append(row)
                
            if name in self.unique_items:
                print(f"Warning: Overwriting existing item '{name}'")

            self.unique_items[name] = {
                'type': 'building',
                'tiles': tiles,
                'size': (width, height)
            }

            print(f"Added building: {name} ({width}x{height})")
    
    def draw_ui(self):
        """Draw the UI elements"""
        self.screen.fill(BG_COLOR)

        # Left panel
        panel_width = 280
        pygame.draw.rect(self.screen, (40, 40, 50), (0, 0, panel_width, SCREEN_HEIGHT))

        # Title
        title = self.font.render("UNIQUE ITEM PICKER", True, TEXT_COLOR)
        self.screen.blit(title, (10, 10))

        # Item count
        count_text = self.small_font.render(f"{len(self.unique_items)} items", True, TEXT_COLOR)
        self.screen.blit(count_text, (10, 40))

        # Items list
        y_offset = 70 - self.sidebar_scroll
        for name, item_data in sorted(self.unique_items.items()):
            if y_offset > 60 and y_offset < SCREEN_HEIGHT - 100:
                # Item background
                item_rect = pygame.Rect(5, y_offset, panel_width - 10, 60)
                is_selected = self.selected_item_name == name
                
                if is_selected:
                    pygame.draw.rect(self.screen, (60, 60, 80), item_rect)
                    pygame.draw.rect(self.screen, SELECTED_COLOR, item_rect, 2)
                else:
                    pygame.draw.rect(self.screen, (50, 50, 60), item_rect)
                    pygame.draw.rect(self.screen, (70, 70, 80), item_rect, 1)

                # Preview
                if item_data['type'] == 'tile':
                    tile_surf = self.get_tile_surface(item_data['tile'])
                    if tile_surf:
                        scaled = pygame.transform.scale(tile_surf, (32, 32))
                        self.screen.blit(scaled, (10, y_offset + 14))
                else:  # building
                    # Show first tile
                    if item_data['tiles'] and item_data['tiles'][0]:
                        tile_surf = self.get_tile_surface(item_data['tiles'][0][0])
                        if tile_surf:
                            scaled = pygame.transform.scale(tile_surf, (32, 32))
                            self.screen.blit(scaled, (10, y_offset + 14))

                # Name
                name_text = self.small_font.render(name, True, TEXT_COLOR)
                self.screen.blit(name_text, (50, y_offset + 10))

                # Size
                size_text = self.small_font.render(f"{item_data['size'][0]}x{item_data['size'][1]}", True, (180, 180, 180))
                self.screen.blit(size_text, (50, y_offset + 30))

                # Delete button
                del_rect = pygame.Rect(panel_width - 35, y_offset + 20, 25, 20)
                pygame.draw.rect(self.screen, (150, 50, 50), del_rect)
                del_text = self.small_font.render("X", True, TEXT_COLOR)
                self.screen.blit(del_text, (del_rect.x + 8, del_rect.y + 2))

            y_offset += 65

        # Update max scroll
        self.max_sidebar_scroll = max(0, y_offset + self.sidebar_scroll - SCREEN_HEIGHT + 150)

        # Help text
        if self.show_help:
            help_y = SCREEN_HEIGHT - 200
            help_texts = [
                "Controls:",
                "Click: Select single tile",
                "Drag: Select building area",
                "Tab: Next sprite sheet",
                "Arrows/Wheel: Scroll",
                "S: Save | L: Load",
                "H: Toggle help | ESC: Exit"
            ]
            for i, text in enumerate(help_texts):
                rendered = self.small_font.render(text, True, TEXT_COLOR)
                self.screen.blit(rendered, (10, help_y + i * 20))

        # Top panel
        pygame.draw.rect(self.screen, (40, 40, 50), (panel_width, 0, SCREEN_WIDTH - panel_width, 140))

        # Current action
        action_text = "CLICK to add tile, DRAG to create building"
        rendered = self.font.render(action_text, True, TEXT_COLOR)
        self.screen.blit(rendered, (panel_width + 10, 10))

        # Sheet info
        sheet_text = self.small_font.render(f"Sheet: {self.sheet_names[self.current_sheet_index]}",
                                            True, TEXT_COLOR)
        self.screen.blit(sheet_text, (panel_width + 10, 40))

        # Hover info
        if self.hover_tile:
            hover_text = f"Tile: {self.hover_tile[1]}, {self.hover_tile[2]}"
            rendered = self.small_font.render(hover_text, True, TEXT_COLOR)
            self.screen.blit(rendered, (panel_width + 10, 60))
            
        # Draw input dialog if active
        if self.input_active:
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Dialog box
            dialog_width = 400
            dialog_height = 150
            dialog_x = (SCREEN_WIDTH - dialog_width) // 2
            dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
            
            pygame.draw.rect(self.screen, (50, 50, 60), 
                           (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(self.screen, TEXT_COLOR, 
                           (dialog_x, dialog_y, dialog_width, dialog_height), 2)
            
            # Prompt
            prompt_text = self.font.render(self.input_prompt, True, TEXT_COLOR)
            prompt_rect = prompt_text.get_rect(centerx=dialog_x + dialog_width // 2, 
                                              y=dialog_y + 20)
            self.screen.blit(prompt_text, prompt_rect)
            
            # Input field
            input_rect = pygame.Rect(dialog_x + 20, dialog_y + 60, dialog_width - 40, 30)
            pygame.draw.rect(self.screen, (30, 30, 40), input_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, input_rect, 1)
            
            # Input text
            input_surface = self.font.render(self.input_text, True, TEXT_COLOR)
            self.screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 5))
            
            # Cursor
            cursor_x = input_rect.x + 5 + input_surface.get_width()
            pygame.draw.line(self.screen, TEXT_COLOR, 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.y + 25), 2)
            
            # Instructions
            inst_text = self.small_font.render("Press Enter to confirm, Esc to cancel", 
                                             True, (180, 180, 180))
            inst_rect = inst_text.get_rect(centerx=dialog_x + dialog_width // 2, 
                                          y=dialog_y + dialog_height - 30)
            self.screen.blit(inst_text, inst_rect)

        # Selected item info
        if self.selected_item_name:
            sel_text = f"Selected: {self.selected_item_name}"
            rendered = self.font.render(sel_text, True, SELECTED_COLOR)
            self.screen.blit(rendered, (panel_width + 10, 90))

    def draw_tile_grid(self):
        """Draw the sprite sheet with grid"""
        sheet_name = self.sheet_names[self.current_sheet_index]
        if sheet_name not in self.sheets:
            return

        sheet = self.sheets[sheet_name]

        # Calculate visible area
        start_x = self.scroll_x // TILE_SIZE
        start_y = self.scroll_y // TILE_SIZE
        end_x = min((self.scroll_x + SCREEN_WIDTH - 300) // TILE_SIZE + 2,
                    sheet.get_width() // ORIGINAL_TILE_SIZE)
        end_y = min((self.scroll_y + SCREEN_HEIGHT - 150) // TILE_SIZE + 2,
                    sheet.get_height() // ORIGINAL_TILE_SIZE)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                src_x = x * ORIGINAL_TILE_SIZE
                src_y = y * ORIGINAL_TILE_SIZE

                if src_x + ORIGINAL_TILE_SIZE <= sheet.get_width() and \
                        src_y + ORIGINAL_TILE_SIZE <= sheet.get_height():

                    src_rect = pygame.Rect(src_x, src_y, ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                    tile_surface = sheet.subsurface(src_rect)
                    scaled = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))

                    screen_x = 300 + x * TILE_SIZE - self.scroll_x
                    screen_y = 150 + y * TILE_SIZE - self.scroll_y

                    self.screen.blit(scaled, (screen_x, screen_y))

                    # Draw grid
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Draw current rectangle selection
        if self.selecting_rect and self.rect_start and self.rect_end:
            x1 = 300 + self.rect_start[1] * TILE_SIZE - self.scroll_x
            y1 = 150 + self.rect_start[2] * TILE_SIZE - self.scroll_y
            x2 = 300 + self.rect_end[1] * TILE_SIZE - self.scroll_x
            y2 = 150 + self.rect_end[2] * TILE_SIZE - self.scroll_y

            min_x, max_x = min(x1, x2), max(x1, x2) + TILE_SIZE
            min_y, max_y = min(y1, y2), max(y1, y2) + TILE_SIZE

            selection_surf = pygame.Surface((max_x - min_x, max_y - min_y), pygame.SRCALPHA)
            selection_surf.fill(SELECTION_COLOR)
            self.screen.blit(selection_surf, (min_x, min_y))
            pygame.draw.rect(self.screen, (255, 100, 100), (min_x, min_y, max_x - min_x, max_y - min_y), 2)

        # Highlight hover
        if self.hover_tile:
            x = 300 + self.hover_tile[1] * TILE_SIZE - self.scroll_x
            y = 150 + self.hover_tile[2] * TILE_SIZE - self.scroll_y
            pygame.draw.rect(self.screen, HOVER_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 2)

    def handle_input(self, event):
        """Handle user input"""
        # Handle text input mode
        if self.input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Complete the action
                    self.complete_pending_action()
                    self.input_active = False
                    self.pending_action = None
                elif event.key == pygame.K_ESCAPE:
                    # Cancel
                    self.input_active = False
                    self.pending_action = None
                    print("Action cancelled")
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    # Add character
                    if event.unicode and event.unicode.isprintable():
                        self.input_text += event.unicode
            return True
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_TAB:
                self.current_sheet_index = (self.current_sheet_index + 1) % len(self.sheet_names)
                self.scroll_x = 0
                self.scroll_y = 0
                self.update_max_scroll()
            elif event.key == pygame.K_s:
                self.save_selections()
            elif event.key == pygame.K_l:
                self.load_selections()
            elif event.key == pygame.K_h:
                self.show_help = not self.show_help
            elif event.key == pygame.K_LEFT:
                self.scroll_x = max(0, self.scroll_x - TILE_SIZE)
            elif event.key == pygame.K_RIGHT:
                self.scroll_x = min(self.max_scroll_x, self.scroll_x + TILE_SIZE)
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - TILE_SIZE)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll_y, self.scroll_y + TILE_SIZE)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = event.pos
                
                # Check if clicking on item list
                if mx < 280:
                    # Check for delete buttons
                    y_offset = 70 - self.sidebar_scroll
                    for name in sorted(self.unique_items.keys()):
                        if 70 <= my <= y_offset + 60:
                            # Check if clicking delete button
                            if mx >= 245:
                                self.delete_item(name)
                                return True
                            else:
                                # Select item
                                self.selected_item_name = name
                                return True
                        y_offset += 65
                else:
                    # Clicking on tile grid
                    tile = self.get_tile_at_pos(mx, my)
                    if tile:
                        self.selecting_rect = True
                        self.rect_start = tile
                        self.rect_end = tile

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.selecting_rect:
                # Finish selection
                if not self.input_active:  # Don't process if input dialog is open
                    if self.rect_start == self.rect_end:
                        # Single tile
                        self.add_single_tile(self.rect_start)
                    else:
                        # Building
                        self.create_building_from_rect(self.rect_start, self.rect_end)
                    
                    self.selecting_rect = False
                    self.rect_start = None
                    self.rect_end = None

        elif event.type == pygame.MOUSEMOTION:
            self.hover_tile = self.get_tile_at_pos(*event.pos)
            if self.selecting_rect and self.hover_tile:
                self.rect_end = self.hover_tile

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x < 280:
                # Scroll sidebar
                self.sidebar_scroll = max(0, min(self.max_sidebar_scroll,
                                               self.sidebar_scroll - event.y * 20))
            else:
                # Scroll tile view
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self.scroll_x = max(0, min(self.max_scroll_x,
                                               self.scroll_x - event.y * TILE_SIZE))
                else:
                    self.scroll_y = max(0, min(self.max_scroll_y,
                                               self.scroll_y - event.y * TILE_SIZE))

        return True

    def run(self):
        """Main loop"""
        print("\n=== UNIQUE TILE/BUILDING PICKER ===")
        print("Each item gets a unique name - no categories!")
        print("Click for single tiles, drag for buildings")
        print("Name each selection when prompted\n")

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
    tool = UniqueTilePicker()
    tool.run()
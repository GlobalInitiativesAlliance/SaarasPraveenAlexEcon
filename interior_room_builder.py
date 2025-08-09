import pygame
import sys
import json
import os

pygame.init()

# Constants
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

# Colors
BG_COLOR = (30, 30, 40)
GRID_COLOR = (60, 60, 70)
SELECTED_COLOR = (255, 255, 0)
HOVER_COLOR = (100, 100, 150)
TEXT_COLOR = (255, 255, 255)
PANEL_COLOR = (40, 40, 50)
ROOM_BG_COLOR = (20, 20, 25)
BUTTON_COLOR = (60, 60, 70)
BUTTON_HOVER = (80, 80, 90)

class InteriorRoomBuilder:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Interior Room Builder")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Interior sprite sheets
        self.sheet_names = [
            'TopDownHouse_FloorsAndWalls.png',
            'TopDownHouse_FurnitureState1.png',
            'TopDownHouse_FurnitureState2.png',
            'TopDownHouse_SmallItems.png',
            'TopDownHouse_DoorsAndWindows.png'
        ]
        self.sheets = {}
        self.current_sheet_index = 0
        self.load_sheets()
        
        # Room configuration
        self.room_width = 16
        self.room_height = 12
        self.room_data = [[None for _ in range(self.room_width)] for _ in range(self.room_height)]
        self.room_layers = {
            'floor': [[None for _ in range(self.room_width)] for _ in range(self.room_height)],
            'walls': [[None for _ in range(self.room_width)] for _ in range(self.room_height)],
            'furniture': [[None for _ in range(self.room_width)] for _ in range(self.room_height)],
            'decor': [[None for _ in range(self.room_width)] for _ in range(self.room_height)]
        }
        
        # Saved rooms
        self.saved_rooms = {}
        self.load_rooms()
        
        # UI State
        self.selected_tile = None
        self.current_layer = 'floor'  # floor, walls, furniture, decor
        self.hover_room_tile = None
        self.hover_palette_tile = None
        self.palette_offset_x = 0
        self.palette_offset_y = 0
        self.room_list_scroll = 0
        
        # Palette dragging
        self.dragging_palette = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Tools
        self.current_tool = 'paint'  # paint, erase, fill
        self.show_grid = True
        
        # Room viewport
        self.room_offset_x = 400
        self.room_offset_y = 100
        
        # Input state
        self.input_active = False
        self.input_text = ""
        self.input_type = None
        
        # Drawing state
        self.is_drawing = False
        
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
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((100, 0, 0))
                
    def load_rooms(self):
        """Load saved room layouts"""
        try:
            with open("interior_rooms.json", "r") as f:
                data = json.load(f)
                self.saved_rooms = data.get("rooms", {})
                print(f"Loaded {len(self.saved_rooms)} rooms")
        except:
            print("No saved rooms found")
            
    def save_rooms(self):
        """Save all room layouts"""
        save_data = {"rooms": self.saved_rooms}
        with open("interior_rooms.json", "w") as f:
            json.dump(save_data, f, indent=2)
        print(f"Saved {len(self.saved_rooms)} rooms")
        
    def get_tile_surface(self, tile_info):
        """Get tile surface for rendering"""
        if not tile_info or len(tile_info) != 3:
            return None
            
        sheet_name, x, y = tile_info
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            return None
            
        try:
            # Handle multi-tile furniture
            if isinstance(x, list):  # Multi-tile object
                # For now, just return the first tile
                x, y = x[0], y[0]
                
            rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                             ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
            tile = sheet.subsurface(rect)
            return pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
        except:
            return None
            
    def draw_ui(self):
        """Draw the main UI"""
        self.screen.fill(BG_COLOR)
        
        # Left panel - Toolbox
        panel_width = 350
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, panel_width, SCREEN_HEIGHT))
        
        # Title
        title = self.font.render("ROOM BUILDER", True, TEXT_COLOR)
        self.screen.blit(title, (10, 10))
        
        # Room size controls
        size_text = self.small_font.render(f"Room Size: {self.room_width}x{self.room_height}", True, TEXT_COLOR)
        self.screen.blit(size_text, (10, 40))
        
        # Draw size adjustment buttons
        self.draw_button(150, 35, 30, 25, "-W", self.room_width > 8)
        self.draw_button(185, 35, 30, 25, "+W", self.room_width < 24)
        self.draw_button(220, 35, 30, 25, "-H", self.room_height > 8)
        self.draw_button(255, 35, 30, 25, "+H", self.room_height < 24)
        
        # Layer selection
        layers = ['floor', 'walls', 'furniture', 'decor']
        y_offset = 80
        layer_text = self.font.render("Layers:", True, TEXT_COLOR)
        self.screen.blit(layer_text, (10, y_offset))
        y_offset += 30
        
        for layer in layers:
            color = SELECTED_COLOR if layer == self.current_layer else TEXT_COLOR
            bg_color = (50, 50, 60) if layer == self.current_layer else None
            
            if bg_color:
                pygame.draw.rect(self.screen, bg_color, (10, y_offset - 2, 150, 24))
                
            layer_text = self.small_font.render(layer.title(), True, color)
            self.screen.blit(layer_text, (15, y_offset))
            y_offset += 25
            
        # Tools
        y_offset += 20
        tools_text = self.font.render("Tools:", True, TEXT_COLOR)
        self.screen.blit(tools_text, (10, y_offset))
        y_offset += 30
        
        tools = [('paint', 'P - Paint'), ('erase', 'E - Erase'), ('fill', 'F - Fill')]
        for tool_id, tool_name in tools:
            color = SELECTED_COLOR if tool_id == self.current_tool else TEXT_COLOR
            bg_color = (50, 50, 60) if tool_id == self.current_tool else None
            
            if bg_color:
                pygame.draw.rect(self.screen, bg_color, (10, y_offset - 2, 150, 24))
                
            tool_text = self.small_font.render(tool_name, True, color)
            self.screen.blit(tool_text, (15, y_offset))
            y_offset += 25
            
        # Selected tile preview
        y_offset += 20
        selected_text = self.font.render("Selected Tile:", True, TEXT_COLOR)
        self.screen.blit(selected_text, (10, y_offset))
        y_offset += 30
        
        if self.selected_tile:
            tile_surf = self.get_tile_surface(self.selected_tile)
            if tile_surf:
                # Draw larger preview
                preview_size = 64
                scaled = pygame.transform.scale(tile_surf, (preview_size, preview_size))
                preview_rect = pygame.Rect(10, y_offset, preview_size, preview_size)
                pygame.draw.rect(self.screen, (60, 60, 70), preview_rect, 1)
                self.screen.blit(scaled, (10, y_offset))
                
                # Tile info
                tile_info = f"Sheet: {self.selected_tile[0].split('.')[0]}"
                info_text = self.small_font.render(tile_info, True, (180, 180, 180))
                self.screen.blit(info_text, (80, y_offset))
                
                coord_info = f"Pos: ({self.selected_tile[1]}, {self.selected_tile[2]})"
                coord_text = self.small_font.render(coord_info, True, (180, 180, 180))
                self.screen.blit(coord_text, (80, y_offset + 20))
        
        # Draw tile palette
        self.draw_tile_palette()
        
        # Right panel - Saved rooms
        self.draw_saved_rooms_panel()
        
        # Top bar - Info and controls
        pygame.draw.rect(self.screen, PANEL_COLOR, (panel_width, 0, SCREEN_WIDTH - panel_width - 250, 80))
        
        # Current sheet and layer info
        sheet_text = self.font.render(f"Tileset: {self.sheet_names[self.current_sheet_index].split('.')[0]}", 
                                    True, TEXT_COLOR)
        self.screen.blit(sheet_text, (panel_width + 10, 10))
        
        # Current layer indicator
        layer_text = self.font.render(f"Active Layer: {self.current_layer.upper()}", 
                                    True, SELECTED_COLOR)
        self.screen.blit(layer_text, (panel_width + 400, 10))
        
        # Controls help
        controls = [
            "Tab: Next tileset",
            "G: Toggle grid",
            "S: Save room",
            "Delete: Clear room",
            "Scroll: Navigate palette"
        ]
        x_offset = panel_width + 10
        y_offset = 35
        col = 0
        for control in controls:
            control_text = self.small_font.render(control, True, (180, 180, 180))
            self.screen.blit(control_text, (x_offset + col * 150, y_offset))
            col += 1
            if col > 2:
                col = 0
                y_offset += 18
                
        # Draw the room canvas
        self.draw_room_canvas()
        
        # Input dialog
        if self.input_active:
            self.draw_input_dialog()
            
    def draw_button(self, x, y, w, h, text, enabled=True):
        """Draw a simple button"""
        color = BUTTON_COLOR if enabled else (40, 40, 40)
        text_color = TEXT_COLOR if enabled else (100, 100, 100)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if enabled and x <= mouse_x <= x + w and y <= mouse_y <= y + h:
            color = BUTTON_HOVER
            
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        pygame.draw.rect(self.screen, text_color, (x, y, w, h), 1)
        
        button_text = self.small_font.render(text, True, text_color)
        text_rect = button_text.get_rect(center=(x + w//2, y + h//2))
        self.screen.blit(button_text, text_rect)
        
    def draw_tile_palette(self):
        """Draw tile palette with arrow navigation"""
        palette_y = 500
        palette_height = SCREEN_HEIGHT - palette_y - 10
        palette_width = 340
        
        # Background
        pygame.draw.rect(self.screen, (35, 35, 45), (5, palette_y, palette_width, palette_height))
        pygame.draw.rect(self.screen, (60, 60, 70), (5, palette_y, palette_width, palette_height), 1)
        
        # Title and navigation arrows
        palette_title = self.small_font.render("Tile Palette", True, TEXT_COLOR)
        self.screen.blit(palette_title, (10, palette_y - 20))
        
        # Arrow buttons
        arrow_size = 25
        arrow_y = palette_y - 25
        
        # Left arrow
        left_arrow_x = 150
        self.draw_button(left_arrow_x, arrow_y, arrow_size, arrow_size, "◄", self.palette_offset_x > 0)
        
        # Right arrow
        right_arrow_x = left_arrow_x + arrow_size + 5
        sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
        max_x = (sheet.get_width() // ORIGINAL_TILE_SIZE - 9) if sheet else 0
        self.draw_button(right_arrow_x, arrow_y, arrow_size, arrow_size, "►", self.palette_offset_x < max_x)
        
        # Up arrow
        up_arrow_x = right_arrow_x + arrow_size + 5
        self.draw_button(up_arrow_x, arrow_y, arrow_size, arrow_size, "▲", self.palette_offset_y > 0)
        
        # Down arrow
        down_arrow_x = up_arrow_x + arrow_size + 5
        max_y = (sheet.get_height() // ORIGINAL_TILE_SIZE - 10) if sheet else 0
        self.draw_button(down_arrow_x, arrow_y, arrow_size, arrow_size, "▼", self.palette_offset_y < max_y)
        
        # Drag hint
        hint_text = self.small_font.render("Drag to pan", True, (150, 150, 150))
        self.screen.blit(hint_text, (down_arrow_x + arrow_size + 10, arrow_y + 5))
        
        # Get current sheet
        sheet_name = self.sheet_names[self.current_sheet_index]
        if not sheet:
            return
            
        # Create clipping region for palette viewport
        palette_rect = pygame.Rect(5, palette_y, palette_width, palette_height)
        self.screen.set_clip(palette_rect)
        
        # Calculate grid
        tiles_per_row = 10
        tile_display_size = 32
        padding = 2
        
        sheet_width = sheet.get_width() // ORIGINAL_TILE_SIZE
        sheet_height = sheet.get_height() // ORIGINAL_TILE_SIZE
        
        # Reset hover state
        self.hover_palette_tile = None
        
        # Draw tiles with offset
        visible_cols = 10
        visible_rows = palette_height // (tile_display_size + padding)
        
        for row in range(visible_rows + 2):
            for col in range(visible_cols + 1):
                tile_x = col + self.palette_offset_x
                tile_y = row + self.palette_offset_y
                
                if tile_x >= sheet_width or tile_y >= sheet_height:
                    continue
                    
                # Get tile
                try:
                    src_rect = pygame.Rect(tile_x * ORIGINAL_TILE_SIZE, tile_y * ORIGINAL_TILE_SIZE,
                                         ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                    if src_rect.right <= sheet.get_width() and src_rect.bottom <= sheet.get_height():
                        tile = sheet.subsurface(src_rect)
                        scaled = pygame.transform.scale(tile, (tile_display_size, tile_display_size))
                        
                        # Calculate position
                        x = 10 + col * (tile_display_size + padding)
                        y = palette_y + 5 + row * (tile_display_size + padding)
                        
                        # Draw tile
                        self.screen.blit(scaled, (x, y))
                        
                        # Highlight if selected
                        tile_info = (sheet_name, tile_x, tile_y)
                        if self.selected_tile and self.selected_tile == tile_info:
                            pygame.draw.rect(self.screen, SELECTED_COLOR, 
                                           (x-1, y-1, tile_display_size+2, tile_display_size+2), 2)
                        
                        # Hover effect
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if (x <= mouse_x <= x + tile_display_size and 
                            y <= mouse_y <= y + tile_display_size and
                            palette_rect.collidepoint(mouse_x, mouse_y)):
                            pygame.draw.rect(self.screen, HOVER_COLOR, 
                                           (x, y, tile_display_size, tile_display_size), 1)
                            self.hover_palette_tile = tile_info
                except:
                    pass
                    
        # Reset clipping
        self.screen.set_clip(None)
        
        # Draw position indicator
        pos_text = self.small_font.render(f"Position: {self.palette_offset_x}, {self.palette_offset_y}", 
                                        True, (150, 150, 150))
        self.screen.blit(pos_text, (10, SCREEN_HEIGHT - 25))
                    
    def draw_room_canvas(self):
        """Draw the room editing area"""
        # Room background
        room_pixel_width = self.room_width * TILE_SIZE
        room_pixel_height = self.room_height * TILE_SIZE
        
        canvas_rect = pygame.Rect(self.room_offset_x - 10, self.room_offset_y - 10,
                                room_pixel_width + 20, room_pixel_height + 20)
        pygame.draw.rect(self.screen, ROOM_BG_COLOR, canvas_rect)
        pygame.draw.rect(self.screen, (80, 80, 90), canvas_rect, 2)
        
        # Draw room tiles layer by layer
        for layer_name in ['floor', 'walls', 'furniture', 'decor']:
            layer = self.room_layers[layer_name]
            
            for y in range(self.room_height):
                for x in range(self.room_width):
                    tile_info = layer[y][x]
                    if tile_info:
                        tile_surf = self.get_tile_surface(tile_info)
                        if tile_surf:
                            pos_x = self.room_offset_x + x * TILE_SIZE
                            pos_y = self.room_offset_y + y * TILE_SIZE
                            self.screen.blit(tile_surf, (pos_x, pos_y))
                            
        # Draw grid
        if self.show_grid:
            for y in range(self.room_height + 1):
                y_pos = self.room_offset_y + y * TILE_SIZE
                pygame.draw.line(self.screen, GRID_COLOR,
                               (self.room_offset_x, y_pos),
                               (self.room_offset_x + room_pixel_width, y_pos))
                               
            for x in range(self.room_width + 1):
                x_pos = self.room_offset_x + x * TILE_SIZE
                pygame.draw.line(self.screen, GRID_COLOR,
                               (x_pos, self.room_offset_y),
                               (x_pos, self.room_offset_y + room_pixel_height))
                               
        # Highlight hover tile
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (self.room_offset_x <= mouse_x < self.room_offset_x + room_pixel_width and
            self.room_offset_y <= mouse_y < self.room_offset_y + room_pixel_height):
            
            hover_x = (mouse_x - self.room_offset_x) // TILE_SIZE
            hover_y = (mouse_y - self.room_offset_y) // TILE_SIZE
            
            if 0 <= hover_x < self.room_width and 0 <= hover_y < self.room_height:
                self.hover_room_tile = (hover_x, hover_y)
                
                # Draw hover indicator
                hover_rect = pygame.Rect(self.room_offset_x + hover_x * TILE_SIZE,
                                       self.room_offset_y + hover_y * TILE_SIZE,
                                       TILE_SIZE, TILE_SIZE)
                                       
                if self.current_tool == 'erase':
                    pygame.draw.rect(self.screen, (255, 100, 100), hover_rect, 2)
                else:
                    pygame.draw.rect(self.screen, HOVER_COLOR, hover_rect, 2)
                    
                    # Preview tile
                    if self.selected_tile and self.current_tool == 'paint':
                        preview_surf = self.get_tile_surface(self.selected_tile)
                        if preview_surf:
                            preview_surf.set_alpha(128)
                            self.screen.blit(preview_surf, hover_rect)
        else:
            self.hover_room_tile = None
            
    def draw_saved_rooms_panel(self):
        """Draw panel showing saved rooms"""
        panel_x = SCREEN_WIDTH - 240
        panel_width = 240
        
        pygame.draw.rect(self.screen, PANEL_COLOR, (panel_x, 0, panel_width, SCREEN_HEIGHT))
        
        # Title
        title = self.font.render("SAVED ROOMS", True, TEXT_COLOR)
        self.screen.blit(title, (panel_x + 10, 10))
        
        # Room list
        y_offset = 50 - self.room_list_scroll
        for room_name in sorted(self.saved_rooms.keys()):
            if y_offset > 40 and y_offset < SCREEN_HEIGHT - 100:
                # Room button
                room_rect = pygame.Rect(panel_x + 10, y_offset, panel_width - 20, 80)
                pygame.draw.rect(self.screen, (50, 50, 60), room_rect)
                pygame.draw.rect(self.screen, (70, 70, 80), room_rect, 1)
                
                # Room name
                name_text = self.small_font.render(room_name, True, TEXT_COLOR)
                self.screen.blit(name_text, (panel_x + 15, y_offset + 5))
                
                # Room info
                room_data = self.saved_rooms[room_name]
                size_text = self.small_font.render(f"Size: {room_data['width']}x{room_data['height']}", 
                                                 True, (180, 180, 180))
                self.screen.blit(size_text, (panel_x + 15, y_offset + 25))
                
                # Load button
                load_rect = pygame.Rect(panel_x + 15, y_offset + 50, 60, 25)
                self.draw_button(load_rect.x, load_rect.y, load_rect.width, load_rect.height, "Load", True)
                
                # Delete button
                del_rect = pygame.Rect(panel_x + 85, y_offset + 50, 60, 25)
                pygame.draw.rect(self.screen, (150, 50, 50), del_rect)
                pygame.draw.rect(self.screen, TEXT_COLOR, del_rect, 1)
                del_text = self.small_font.render("Delete", True, TEXT_COLOR)
                del_text_rect = del_text.get_rect(center=del_rect.center)
                self.screen.blit(del_text, del_text_rect)
                
            y_offset += 90
            
    def draw_input_dialog(self):
        """Draw input dialog for room name"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        dialog_width = 400
        dialog_height = 150
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        pygame.draw.rect(self.screen, (50, 50, 60), 
                       (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, TEXT_COLOR, 
                       (dialog_x, dialog_y, dialog_width, dialog_height), 2)
                       
        # Prompt
        prompt = "Enter room name:"
        prompt_text = self.font.render(prompt, True, TEXT_COLOR)
        self.screen.blit(prompt_text, (dialog_x + 20, dialog_y + 20))
        
        # Input field
        input_rect = pygame.Rect(dialog_x + 20, dialog_y + 60, dialog_width - 40, 30)
        pygame.draw.rect(self.screen, (30, 30, 40), input_rect)
        pygame.draw.rect(self.screen, TEXT_COLOR, input_rect, 1)
        
        # Text
        text_surface = self.font.render(self.input_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        
        # Cursor
        cursor_x = input_rect.x + 5 + text_surface.get_width()
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            pygame.draw.line(self.screen, TEXT_COLOR, 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.y + 25), 2)
        
        # Instructions
        inst_text = self.small_font.render("Press Enter to save, Esc to cancel", 
                                         True, (180, 180, 180))
        self.screen.blit(inst_text, (dialog_x + 20, dialog_y + dialog_height - 30))
        
    def paint_tile(self, x, y):
        """Paint a tile at the given position"""
        if not self.selected_tile or not (0 <= x < self.room_width and 0 <= y < self.room_height):
            return
            
        if self.current_tool == 'paint':
            self.room_layers[self.current_layer][y][x] = self.selected_tile
        elif self.current_tool == 'erase':
            self.room_layers[self.current_layer][y][x] = None
        elif self.current_tool == 'fill':
            # Simple fill - fills entire layer
            for fy in range(self.room_height):
                for fx in range(self.room_width):
                    self.room_layers[self.current_layer][fy][fx] = self.selected_tile
                    
    def resize_room(self, new_width, new_height):
        """Resize the room and preserve existing tiles"""
        # Create new layers
        new_layers = {}
        for layer_name in self.room_layers:
            new_layer = [[None for _ in range(new_width)] for _ in range(new_height)]
            
            # Copy existing tiles
            for y in range(min(self.room_height, new_height)):
                for x in range(min(self.room_width, new_width)):
                    new_layer[y][x] = self.room_layers[layer_name][y][x]
                    
            new_layers[layer_name] = new_layer
            
        self.room_layers = new_layers
        self.room_width = new_width
        self.room_height = new_height
        
    def save_current_room(self):
        """Save the current room layout"""
        if not self.input_text:
            return
            
        room_data = {
            'width': self.room_width,
            'height': self.room_height,
            'layers': self.room_layers
        }
        
        self.saved_rooms[self.input_text] = room_data
        self.save_rooms()
        print(f"Saved room: {self.input_text}")
        
    def load_room(self, room_name):
        """Load a saved room"""
        if room_name not in self.saved_rooms:
            return
            
        room_data = self.saved_rooms[room_name]
        self.room_width = room_data['width']
        self.room_height = room_data['height']
        self.room_layers = room_data['layers']
        print(f"Loaded room: {room_name}")
        
    def clear_room(self):
        """Clear all tiles in the current room"""
        for layer_name in self.room_layers:
            self.room_layers[layer_name] = [[None for _ in range(self.room_width)] 
                                           for _ in range(self.room_height)]
        print("Cleared room")
        
    def handle_input(self, event):
        """Handle user input"""
        if self.input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.save_current_room()
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
                self.selected_tile = None
                # Reset palette position when switching sheets
                self.palette_offset_x = 0
                self.palette_offset_y = 0
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
            elif event.key == pygame.K_s:
                self.input_active = True
                self.input_text = ""
            elif event.key == pygame.K_DELETE:
                self.clear_room()
            elif event.key == pygame.K_p:
                self.current_tool = 'paint'
            elif event.key == pygame.K_e:
                self.current_tool = 'erase'
            elif event.key == pygame.K_f:
                self.current_tool = 'fill'
            elif event.key == pygame.K_1:
                self.current_layer = 'floor'
            elif event.key == pygame.K_2:
                self.current_layer = 'walls'
            elif event.key == pygame.K_3:
                self.current_layer = 'furniture'
            elif event.key == pygame.K_4:
                self.current_layer = 'decor'
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = event.pos
                
                # Check size buttons
                if 35 <= my <= 60:
                    if 150 <= mx <= 180:  # -W
                        if self.room_width > 8:
                            self.resize_room(self.room_width - 1, self.room_height)
                    elif 185 <= mx <= 215:  # +W
                        if self.room_width < 24:
                            self.resize_room(self.room_width + 1, self.room_height)
                    elif 220 <= mx <= 250:  # -H
                        if self.room_height > 8:
                            self.resize_room(self.room_width, self.room_height - 1)
                    elif 255 <= mx <= 285:  # +H
                        if self.room_height < 24:
                            self.resize_room(self.room_width, self.room_height + 1)
                
                # Check layer buttons
                if 10 <= mx <= 160:
                    layers = ['floor', 'walls', 'furniture', 'decor']
                    y_start = 110
                    for i, layer in enumerate(layers):
                        if y_start + i * 25 <= my <= y_start + (i + 1) * 25:
                            self.current_layer = layer
                            
                # Check tool buttons
                if 10 <= mx <= 160:
                    tools = ['paint', 'erase', 'fill']
                    y_start = 230
                    for i, tool in enumerate(tools):
                        if y_start + i * 25 <= my <= y_start + (i + 1) * 25:
                            self.current_tool = tool
                
                # Check arrow buttons for palette navigation
                arrow_y = 475
                arrow_size = 25
                
                if arrow_y <= my <= arrow_y + arrow_size:
                    # Left arrow
                    if 150 <= mx <= 175 and self.palette_offset_x > 0:
                        self.palette_offset_x -= 1
                    # Right arrow
                    elif 180 <= mx <= 205:
                        sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                        if sheet:
                            max_x = (sheet.get_width() // ORIGINAL_TILE_SIZE - 9)
                            if self.palette_offset_x < max_x:
                                self.palette_offset_x += 1
                    # Up arrow
                    elif 210 <= mx <= 235 and self.palette_offset_y > 0:
                        self.palette_offset_y -= 1
                    # Down arrow
                    elif 240 <= mx <= 265:
                        sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                        if sheet:
                            max_y = (sheet.get_height() // ORIGINAL_TILE_SIZE - 10)
                            if self.palette_offset_y < max_y:
                                self.palette_offset_y += 1
                
                # Check palette click or start dragging
                if 5 <= mx <= 345 and 500 <= my <= SCREEN_HEIGHT - 10:
                    if self.hover_palette_tile:
                        self.selected_tile = self.hover_palette_tile
                    else:
                        # Start dragging palette
                        self.dragging_palette = True
                        self.drag_start_x = mx
                        self.drag_start_y = my
                        self.drag_offset_x = self.palette_offset_x
                        self.drag_offset_y = self.palette_offset_y
                        
                # Check room canvas click
                if self.hover_room_tile:
                    self.paint_tile(*self.hover_room_tile)
                    self.is_drawing = True
                    
                # Check saved rooms panel
                if mx >= SCREEN_WIDTH - 240:
                    y_offset = 50 - self.room_list_scroll
                    for room_name in sorted(self.saved_rooms.keys()):
                        if 0 <= y_offset <= SCREEN_HEIGHT:  # Only process visible rooms
                            if y_offset + 50 <= my <= y_offset + 75:
                                # Check which button
                                if SCREEN_WIDTH - 225 <= mx <= SCREEN_WIDTH - 165:  # Load
                                    self.load_room(room_name)
                                elif SCREEN_WIDTH - 155 <= mx <= SCREEN_WIDTH - 95:  # Delete
                                    if room_name in self.saved_rooms:
                                        del self.saved_rooms[room_name]
                                        self.save_rooms()
                                break
                        y_offset += 90
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_drawing = False
                self.dragging_palette = False
                
        elif event.type == pygame.MOUSEMOTION:
            # Handle palette dragging
            if self.dragging_palette:
                mx, my = event.pos
                
                # Calculate drag delta
                delta_x = (self.drag_start_x - mx) // 34  # tile size + padding
                delta_y = (self.drag_start_y - my) // 34
                
                # Update palette offset
                sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                if sheet:
                    max_x = max(0, (sheet.get_width() // ORIGINAL_TILE_SIZE - 9))
                    max_y = max(0, (sheet.get_height() // ORIGINAL_TILE_SIZE - 10))
                    
                    self.palette_offset_x = max(0, min(max_x, self.drag_offset_x + delta_x))
                    self.palette_offset_y = max(0, min(max_y, self.drag_offset_y + delta_y))
            
            # Continue drawing if mouse is held
            elif self.is_drawing and self.hover_room_tile:
                self.paint_tile(*self.hover_room_tile)
                
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Only handle scrolling for saved rooms panel
            if mouse_x >= SCREEN_WIDTH - 240:  # Saved rooms area
                # Scroll saved rooms
                total_rooms = len(self.saved_rooms)
                max_room_scroll = max(0, total_rooms * 90 - SCREEN_HEIGHT + 200)
                self.room_list_scroll = max(0, min(max_room_scroll, self.room_list_scroll - event.y * 20))
                
        return True
        
    def run(self):
        """Main loop"""
        print("\n=== INTERIOR ROOM BUILDER ===")
        print("Build rooms tile by tile!")
        print("Select tiles from palette, choose layer, and paint")
        print("Press S to save your room design\n")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if not self.handle_input(event):
                        running = False
                        
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
        
if __name__ == "__main__":
    builder = InteriorRoomBuilder()
    builder.run()
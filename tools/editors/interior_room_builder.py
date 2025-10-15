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
        
        # Store the room file path
        self.room_file_path = None
        
        # Interior sprite sheets - updated paths for current structure
        self.sheet_names = [
            'Interiors_16x16.png',
            'Room_Builder_16x16.png',
            '1_Generic_16x16.png',
            '2_LivingRoom_16x16.png',
            '3_Bathroom_16x16.png',
            '4_Bedroom_16x16.png',
            '5_Classroom_and_library_16x16.png',
            '12_Kitchen_16x16.png',
            '16_Grocery_store_16x16.png'
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
        
        # Tileset viewer position
        self.tileset_x = 350
        self.tileset_y = 380
        self.tile_display_size = 16  # Default tile display size for zoom - smaller to fit more tiles
        
        # Tools
        self.current_tool = 'paint'  # paint, erase, fill
        self.show_grid = True
        
        # Room viewport
        self.room_offset_x = 550
        self.room_offset_y = 50
        
        # Input state
        self.input_active = False
        self.input_text = ""
        self.input_type = None
        
        # Drawing state
        self.is_drawing = False
        
    def load_sheets(self):
        """Load interior tileset images"""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to get to the project root
        project_root = os.path.dirname(os.path.dirname(script_dir))
        
        # Try multiple possible locations relative to project root
        possible_bases = [
            os.path.join(project_root, "assets/moderninteriors-win/1_Interiors/16x16"),
            os.path.join(project_root, "assets/moderninteriors-win/1_Interiors/16x16/Theme_Sorter"),
            os.path.join(project_root, "Top-Down_Retro_Interior"),
            os.path.join(project_root, "assets/Top-Down_Retro_Interior")
        ]
        
        for sheet_name in self.sheet_names:
            loaded = False
            for base_dir in possible_bases:
                try:
                    path = os.path.join(base_dir, sheet_name)
                    if os.path.exists(path):
                        self.sheets[sheet_name] = pygame.image.load(path).convert_alpha()
                        print(f"Loaded {sheet_name} from {base_dir}")
                        loaded = True
                        break
                except Exception as e:
                    continue
            
            if not loaded:
                print(f"Failed to load {sheet_name} from any location")
                # Create a placeholder surface
                placeholder = pygame.Surface((256, 256))
                placeholder.fill((50, 50, 50))
                # Draw text indicating missing tileset
                font = pygame.font.Font(None, 24)
                text = font.render(f"Missing: {sheet_name}", True, (255, 100, 100))
                placeholder.blit(text, (10, 10))
                self.sheets[sheet_name] = placeholder
                
    def load_rooms(self):
        """Load saved room layouts from individual JSON files"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        
        # Define the rooms directory
        self.rooms_dir = os.path.join(project_root, "data", "interiors", "rooms")
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.rooms_dir):
            os.makedirs(self.rooms_dir)
            print(f"Created rooms directory: {self.rooms_dir}")
        
        # Load all room files
        self.saved_rooms = {}
        room_files = [f for f in os.listdir(self.rooms_dir) if f.endswith('.json')]
        
        for room_file in room_files:
            room_path = os.path.join(self.rooms_dir, room_file)
            try:
                with open(room_path, "r") as f:
                    room_data = json.load(f)
                    room_name = room_file[:-5]  # Remove .json extension
                    self.saved_rooms[room_name] = room_data
                    print(f"Loaded room: {room_name}")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in {room_file}: {e}")
            except Exception as e:
                print(f"Error loading {room_file}: {type(e).__name__}: {e}")
        
        print(f"Loaded {len(self.saved_rooms)} rooms from {self.rooms_dir}")
        if self.saved_rooms:
            room_names = list(self.saved_rooms.keys())[:5]
            print(f"First few rooms: {room_names}")
            
    def save_rooms(self):
        """Save all room layouts as individual JSON files"""
        # Ensure rooms directory exists
        if not hasattr(self, 'rooms_dir'):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            self.rooms_dir = os.path.join(project_root, "data", "interiors", "rooms")
            os.makedirs(self.rooms_dir, exist_ok=True)
        
        # Remove any deleted rooms from disk
        existing_files = [f for f in os.listdir(self.rooms_dir) if f.endswith('.json')]
        for room_file in existing_files:
            room_name = room_file[:-5]  # Remove .json extension
            if room_name not in self.saved_rooms:
                file_path = os.path.join(self.rooms_dir, room_file)
                os.remove(file_path)
                print(f"Deleted room file: {room_file}")
        
        # Save each room as an individual file
        for room_name, room_data in self.saved_rooms.items():
            file_path = os.path.join(self.rooms_dir, f"{room_name}.json")
            with open(file_path, "w") as f:
                json.dump(room_data, f, indent=2)
        
        print(f"Saved {len(self.saved_rooms)} rooms to {self.rooms_dir}")
        
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
        panel_width = 280
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
        
        # Draw the room canvas
        self.draw_room_canvas()
        
        # Draw saved rooms list on left panel
        self.draw_saved_rooms_list()
        
        # Top bar - Info and controls
        pygame.draw.rect(self.screen, PANEL_COLOR, (panel_width, 0, SCREEN_WIDTH - panel_width, 40))
        
        # Current layer indicator
        layer_text = self.font.render(f"Active Layer: {self.current_layer.upper()}", 
                                    True, SELECTED_COLOR)
        self.screen.blit(layer_text, (panel_width + 20, 10))
        
        # Controls help in top bar
        controls = [
            "Tab: Next tileset",
            "G: Grid",
            "S: Save",
            "Arrows: Navigate",
            "+/-: Zoom",
            "F12: Screenshot"
        ]
        x_offset = panel_width + 200
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, (180, 180, 180))
            self.screen.blit(control_text, (x_offset + i * 110, 10))
        
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
        """Draw full tileset viewer"""
        # Get current sheet
        sheet_name = self.sheet_names[self.current_sheet_index]
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            return
            
        # Tileset viewer area
        viewer_width = SCREEN_WIDTH - self.tileset_x - 10
        viewer_height = SCREEN_HEIGHT - self.tileset_y - 10
        
        # Background
        pygame.draw.rect(self.screen, (25, 25, 30), (self.tileset_x - 5, self.tileset_y - 5, viewer_width + 10, viewer_height + 10))
        pygame.draw.rect(self.screen, (60, 60, 70), (self.tileset_x - 5, self.tileset_y - 5, viewer_width + 10, viewer_height + 10), 2)
        
        # Title with zoom level
        title_text = self.font.render(f"Tileset: {sheet_name.split('.')[0]} (Zoom: {self.tile_display_size}px)", True, TEXT_COLOR)
        self.screen.blit(title_text, (self.tileset_x, self.tileset_y - 35))
        
        # Calculate tile display size to fit the entire tileset
        sheet_width_tiles = sheet.get_width() // ORIGINAL_TILE_SIZE
        sheet_height_tiles = sheet.get_height() // ORIGINAL_TILE_SIZE
        
        # Use the instance tile display size (can be adjusted with zoom)
        tile_display_size = self.tile_display_size
        
        # Create viewport
        viewport_rect = pygame.Rect(self.tileset_x, self.tileset_y, viewer_width, viewer_height)
        self.screen.set_clip(viewport_rect)
        
        # Calculate actual tileset area
        tileset_pixel_width = sheet_width_tiles * tile_display_size
        tileset_pixel_height = sheet_height_tiles * tile_display_size
        
        # Center the tileset if it's smaller than the viewport
        offset_x = (viewer_width - tileset_pixel_width) // 2 if tileset_pixel_width < viewer_width else 0
        offset_y = (viewer_height - tileset_pixel_height) // 2 if tileset_pixel_height < viewer_height else 0
        
        # Handle scrolling if tileset is larger than viewport
        if tileset_pixel_width > viewer_width or tileset_pixel_height > viewer_height:
            # Allow scrolling with drag
            offset_x = -self.palette_offset_x * tile_display_size
            offset_y = -self.palette_offset_y * tile_display_size
            
            # Clamp offsets
            offset_x = max(-(tileset_pixel_width - viewer_width), min(0, offset_x))
            offset_y = max(-(tileset_pixel_height - viewer_height), min(0, offset_y))
        
        # Reset hover state
        self.hover_palette_tile = None
        
        # Draw all tiles
        for y in range(sheet_height_tiles):
            for x in range(sheet_width_tiles):
                try:
                    src_rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                                         ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                    if src_rect.right <= sheet.get_width() and src_rect.bottom <= sheet.get_height():
                        tile = sheet.subsurface(src_rect)
                        scaled = pygame.transform.scale(tile, (tile_display_size, tile_display_size))
                        
                        # Calculate position
                        draw_x = self.tileset_x + offset_x + x * tile_display_size
                        draw_y = self.tileset_y + offset_y + y * tile_display_size
                        
                        # Only draw if visible
                        if (draw_x + tile_display_size >= self.tileset_x and draw_x < self.tileset_x + viewer_width and
                            draw_y + tile_display_size >= self.tileset_y and draw_y < self.tileset_y + viewer_height):
                            
                            # Draw tile
                            self.screen.blit(scaled, (draw_x, draw_y))
                            
                            # Draw grid
                            pygame.draw.rect(self.screen, (40, 40, 45), 
                                           (draw_x, draw_y, tile_display_size, tile_display_size), 1)
                            
                            # Highlight if selected
                            tile_info = (sheet_name, x, y)
                            if self.selected_tile and self.selected_tile == tile_info:
                                pygame.draw.rect(self.screen, SELECTED_COLOR, 
                                               (draw_x-1, draw_y-1, tile_display_size+2, tile_display_size+2), 3)
                            
                            # Hover effect
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            if (draw_x <= mouse_x <= draw_x + tile_display_size and 
                                draw_y <= mouse_y <= draw_y + tile_display_size):
                                pygame.draw.rect(self.screen, HOVER_COLOR, 
                                               (draw_x, draw_y, tile_display_size, tile_display_size), 2)
                                self.hover_palette_tile = tile_info
                except:
                    pass
                    
        # Reset clipping
        self.screen.set_clip(None)
        
        # Draw info overlay
        if self.hover_palette_tile:
            info_text = self.small_font.render(f"Tile: ({self.hover_palette_tile[1]}, {self.hover_palette_tile[2]})", 
                                            True, TEXT_COLOR)
            info_bg = pygame.Surface((info_text.get_width() + 10, 20))
            info_bg.fill((40, 40, 50))
            info_bg.set_alpha(200)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(info_bg, (mouse_x + 10, mouse_y - 25))
            self.screen.blit(info_text, (mouse_x + 15, mouse_y - 22))
        
        # Scroll indicators if needed
        if tileset_pixel_width > viewer_width or tileset_pixel_height > viewer_height:
            # Show navigation help at the top
            nav_text = self.small_font.render("Use arrow keys or drag to navigate", True, (200, 200, 200))
            nav_bg = pygame.Surface((nav_text.get_width() + 20, 25))
            nav_bg.fill((40, 40, 50))
            nav_bg.set_alpha(180)
            nav_x = self.tileset_x + (viewer_width - nav_text.get_width()) // 2
            self.screen.blit(nav_bg, (nav_x - 10, self.tileset_y + 5))
            self.screen.blit(nav_text, (nav_x, self.tileset_y + 8))
            
        # Import hint
        import_hint = self.small_font.render(f"Press 'I' to import entire tileset ({sheet_width_tiles}x{sheet_height_tiles} tiles)", 
                                           True, (150, 150, 150))
        self.screen.blit(import_hint, (self.tileset_x, self.tileset_y + viewer_height - 25))
                    
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
            # Ensure we don't draw beyond the room boundaries
            for y in range(self.room_height + 1):
                y_pos = self.room_offset_y + y * TILE_SIZE
                if y_pos <= self.room_offset_y + room_pixel_height:
                    pygame.draw.line(self.screen, GRID_COLOR,
                                   (self.room_offset_x, y_pos),
                                   (self.room_offset_x + room_pixel_width, y_pos))
                               
            for x in range(self.room_width + 1):
                x_pos = self.room_offset_x + x * TILE_SIZE
                if x_pos <= self.room_offset_x + room_pixel_width:
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
            
    def draw_saved_rooms_list(self):
        """Draw saved rooms in the left panel"""
        y_offset = 420
        
        # Title
        title = self.small_font.render("SAVED ROOMS", True, TEXT_COLOR)
        self.screen.blit(title, (10, y_offset))
        y_offset += 25
        
        # Room list - compact view
        max_visible = 5
        room_names = sorted(self.saved_rooms.keys())
        
        # Show scroll indicators if needed
        if len(room_names) > max_visible:
            scroll_text = self.small_font.render(f"({len(room_names)} rooms, scroll with wheel)", 
                                               True, (150, 150, 150))
            self.screen.blit(scroll_text, (10, y_offset))
            y_offset += 20
        
        start_idx = max(0, min(self.room_list_scroll // 40, len(room_names) - max_visible))
        for i in range(start_idx, min(start_idx + max_visible, len(room_names))):
            room_name = room_names[i]
            room_data = self.saved_rooms[room_name]
            
            # Room entry background
            entry_rect = pygame.Rect(10, y_offset, 260, 35)
            pygame.draw.rect(self.screen, (45, 45, 55), entry_rect)
            pygame.draw.rect(self.screen, (60, 60, 70), entry_rect, 1)
            
            # Room name and size
            name_text = self.small_font.render(f"{room_name} ({room_data['width']}x{room_data['height']})", 
                                             True, TEXT_COLOR)
            self.screen.blit(name_text, (15, y_offset + 2))
            
            # Mini buttons
            self.draw_button(150, y_offset + 5, 40, 25, "Load", True)
            self.draw_button(195, y_offset + 5, 40, 25, "Del", True)
            
            y_offset += 40
            
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
        if not (0 <= x < self.room_width and 0 <= y < self.room_height):
            return
            
        if self.current_tool == 'paint':
            if not self.selected_tile:
                return
            self.room_layers[self.current_layer][y][x] = self.selected_tile
        elif self.current_tool == 'erase':
            self.room_layers[self.current_layer][y][x] = None
        elif self.current_tool == 'fill':
            if not self.selected_tile:
                return
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
        
        # Save to memory
        self.saved_rooms[self.input_text] = room_data
        
        # Save just this room to its individual file
        if not hasattr(self, 'rooms_dir'):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            self.rooms_dir = os.path.join(project_root, "data", "interiors", "rooms")
            os.makedirs(self.rooms_dir, exist_ok=True)
        
        file_path = os.path.join(self.rooms_dir, f"{self.input_text}.json")
        with open(file_path, "w") as f:
            json.dump(room_data, f, indent=2)
        
        print(f"Saved room: {self.input_text} to {file_path}")
        
    def load_room(self, room_name):
        """Load a saved room"""
        if room_name not in self.saved_rooms:
            return
            
        room_data = self.saved_rooms[room_name]
        new_width = room_data.get('width', 16)
        new_height = room_data.get('height', 12)
        
        # Resize room first
        self.resize_room(new_width, new_height)
        
        # Load layers if they exist and are in the correct format
        if 'layers' in room_data and isinstance(room_data['layers'], dict):
            for layer_name in ['floor', 'walls', 'furniture', 'decor']:
                if layer_name in room_data['layers']:
                    layer_data = room_data['layers'][layer_name]
                    # Ensure layer data is properly sized
                    if isinstance(layer_data, list) and len(layer_data) > 0:
                        for y in range(min(len(layer_data), new_height)):
                            if isinstance(layer_data[y], list):
                                for x in range(min(len(layer_data[y]), new_width)):
                                    self.room_layers[layer_name][y][x] = layer_data[y][x]
        
        print(f"Loaded room: {room_name}")
        
    def clear_room(self):
        """Clear all tiles in the current room"""
        for layer_name in self.room_layers:
            self.room_layers[layer_name] = [[None for _ in range(self.room_width)] 
                                           for _ in range(self.room_height)]
        print("Cleared room")
        
    def import_tileset_as_room(self):
        """Import the entire current tileset as a room"""
        sheet_name = self.sheet_names[self.current_sheet_index]
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            print("No sheet loaded")
            return
            
        # Calculate tileset dimensions
        sheet_width_tiles = sheet.get_width() // ORIGINAL_TILE_SIZE
        sheet_height_tiles = sheet.get_height() // ORIGINAL_TILE_SIZE
        
        # Resize room to fit tileset
        self.resize_room(sheet_width_tiles, sheet_height_tiles)
        
        # Clear all layers first
        self.clear_room()
        
        # Fill the current layer with all tiles from the tileset
        for y in range(sheet_height_tiles):
            for x in range(sheet_width_tiles):
                if x < self.room_width and y < self.room_height:
                    tile_info = (sheet_name, x, y)
                    self.room_layers[self.current_layer][y][x] = tile_info
                    
        print(f"Imported {sheet_name} as {sheet_width_tiles}x{sheet_height_tiles} room on {self.current_layer} layer")
        
    def take_screenshot(self):
        """Take a screenshot of the current screen"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interior_builder_screenshot_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved as {filename}")
        
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
            elif event.key == pygame.K_i:
                # Import entire tileset as a room
                self.import_tileset_as_room()
            elif event.key == pygame.K_F12:
                # Take screenshot
                self.take_screenshot()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Zoom in
                self.tile_display_size = min(64, self.tile_display_size + 8)
            elif event.key == pygame.K_MINUS:
                # Zoom out
                self.tile_display_size = max(16, self.tile_display_size - 8)
            # Arrow keys for tileset navigation
            elif event.key == pygame.K_UP:
                self.palette_offset_y = max(0, self.palette_offset_y - 1)
            elif event.key == pygame.K_DOWN:
                sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                if sheet:
                    sheet_height_tiles = sheet.get_height() // ORIGINAL_TILE_SIZE
                    viewer_height = SCREEN_HEIGHT - self.tileset_y - 10
                    tile_display_size = self.tile_display_size
                    max_offset_y = max(0, sheet_height_tiles - viewer_height // tile_display_size)
                    self.palette_offset_y = min(max_offset_y, self.palette_offset_y + 1)
            elif event.key == pygame.K_LEFT:
                self.palette_offset_x = max(0, self.palette_offset_x - 1)
            elif event.key == pygame.K_RIGHT:
                sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                if sheet:
                    sheet_width_tiles = sheet.get_width() // ORIGINAL_TILE_SIZE
                    viewer_width = SCREEN_WIDTH - self.tileset_x - 10
                    tile_display_size = self.tile_display_size
                    max_offset_x = max(0, sheet_width_tiles - viewer_width // tile_display_size)
                    self.palette_offset_x = min(max_offset_x, self.palette_offset_x + 1)
                
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
                
                # Check tileset viewer click
                sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                if sheet and mx >= self.tileset_x and my >= self.tileset_y:
                    sheet_width_tiles = sheet.get_width() // ORIGINAL_TILE_SIZE
                    sheet_height_tiles = sheet.get_height() // ORIGINAL_TILE_SIZE
                    viewer_width = SCREEN_WIDTH - self.tileset_x - 10
                    viewer_height = SCREEN_HEIGHT - self.tileset_y - 10
                    
                    # Use fixed display size
                    tile_display_size = self.tile_display_size
                    
                    tileset_pixel_width = sheet_width_tiles * tile_display_size
                    tileset_pixel_height = sheet_height_tiles * tile_display_size
                    
                    # Check tile selection or drag
                    if self.hover_palette_tile:
                        self.selected_tile = self.hover_palette_tile
                    elif tileset_pixel_width > viewer_width or tileset_pixel_height > viewer_height:
                        # Start dragging tileset if it's scrollable
                        self.dragging_palette = True
                        self.drag_start_x = mx
                        self.drag_start_y = my
                        self.drag_offset_x = self.palette_offset_x
                        self.drag_offset_y = self.palette_offset_y
                        
                # Check room canvas click
                if self.hover_room_tile:
                    self.paint_tile(*self.hover_room_tile)
                    self.is_drawing = True
                    
                # Check saved rooms in left panel
                if mx < 280:  # Left panel width
                    # Match the y_offset from draw_saved_rooms_list
                    y_offset = 420 + 25  # Title offset
                    max_visible = 5
                    room_names = sorted(self.saved_rooms.keys())
                    
                    # Account for scroll indicator if needed
                    if len(room_names) > max_visible:
                        y_offset += 20
                    
                    start_idx = max(0, min(self.room_list_scroll // 40, len(room_names) - max_visible))
                    
                    for i in range(start_idx, min(start_idx + max_visible, len(room_names))):
                        if y_offset <= my <= y_offset + 35:
                            room_name = room_names[i]
                            # Load button
                            if 150 <= mx <= 190:
                                self.load_room(room_name)
                                print(f"Loading room: {room_name}")
                            # Delete button  
                            elif 195 <= mx <= 235:
                                if room_name in self.saved_rooms:
                                    del self.saved_rooms[room_name]
                                    # Delete the individual room file
                                    if hasattr(self, 'rooms_dir'):
                                        file_path = os.path.join(self.rooms_dir, f"{room_name}.json")
                                        if os.path.exists(file_path):
                                            os.remove(file_path)
                                            print(f"Deleted room file: {file_path}")
                                    print(f"Deleted room: {room_name}")
                            break
                        y_offset += 40
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_drawing = False
                self.dragging_palette = False
                
        elif event.type == pygame.MOUSEMOTION:
            # Handle tileset dragging
            if self.dragging_palette:
                mx, my = event.pos
                
                # Calculate drag delta in pixels
                delta_x = mx - self.drag_start_x
                delta_y = my - self.drag_start_y
                
                # Update palette offset based on tile size
                sheet = self.sheets.get(self.sheet_names[self.current_sheet_index])
                if sheet:
                    sheet_width_tiles = sheet.get_width() // ORIGINAL_TILE_SIZE
                    sheet_height_tiles = sheet.get_height() // ORIGINAL_TILE_SIZE
                    viewer_width = SCREEN_WIDTH - self.tileset_x - 10
                    viewer_height = SCREEN_HEIGHT - self.tileset_y - 10
                    
                    # Use fixed display size
                    tile_display_size = self.tile_display_size
                    
                    # Convert pixel delta to tile offset
                    self.palette_offset_x = self.drag_offset_x - delta_x // tile_display_size
                    self.palette_offset_y = self.drag_offset_y - delta_y // tile_display_size
                    
                    # Clamp offsets
                    max_offset_x = max(0, sheet_width_tiles - viewer_width // tile_display_size)
                    max_offset_y = max(0, sheet_height_tiles - viewer_height // tile_display_size)
                    
                    self.palette_offset_x = max(0, min(max_offset_x, self.palette_offset_x))
                    self.palette_offset_y = max(0, min(max_offset_y, self.palette_offset_y))
            
            # Continue drawing if mouse is held - drag to paint!
            elif self.is_drawing and self.hover_room_tile:
                self.paint_tile(*self.hover_room_tile)
                
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Handle scrolling for saved rooms in left panel
            if mouse_x < 280:  # Left panel area
                # Scroll saved rooms
                total_rooms = len(self.saved_rooms)
                max_room_scroll = max(0, (total_rooms - 5) * 40)
                self.room_list_scroll = max(0, min(max_room_scroll, self.room_list_scroll - event.y * 40))
                
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
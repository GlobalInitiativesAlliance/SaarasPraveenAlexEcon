import pygame
import json
import os
from enum import Enum
import pickle

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
TILE_SIZE = 32  # Display size
ORIGINAL_TILE_SIZE = 16  # Source tile size
SIDEBAR_WIDTH = 350
MAP_AREA_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH

# Colors
BACKGROUND_COLOR = (40, 40, 40)
SIDEBAR_COLOR = (30, 30, 30)
GRID_COLOR = (60, 60, 60)
SELECTED_COLOR = (255, 255, 0)
HOVER_COLOR = (100, 100, 150)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (90, 90, 90)
BUTTON_ACTIVE_COLOR = (110, 110, 110)
PREVIEW_OVERLAY = (255, 255, 255, 100)


class ToolType(Enum):
    TILE = 1
    BUILDING = 2
    ERASER = 3
    FILL = 4


class VisualMapEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Visual City Map Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)

        # Load sprite sheets
        self.load_sprite_sheets()
        
        # Load tile/building data
        self.load_tile_data()
        
        # Initialize or load map
        self.map_width = 64
        self.map_height = 64
        self.map_data = [[None for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.load_map()

        # Editor state
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1
        self.show_grid = True
        self.current_tool = ToolType.TILE
        self.selected_item = None  # Can be tile or building
        self.selected_category = 'tiles'  # Default category for unique items
        self.selected_item_name = None  # Track selected unique item name
        
        # Background fill mode
        self.background_fill_mode = False  # When true, clicking fills building backgrounds
        
        # Mouse state
        self.mouse_dragging = False
        self.space_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # UI state
        self.sidebar_scroll = 0
        self.max_sidebar_scroll = 0
        self.unsaved_changes = False
        self.search_text = ""
        self.search_active = False
        
        # Preview
        self.preview_tiles = []
        self.preview_valid = True

    def load_sprite_sheets(self):
        """Load all sprite sheets"""
        self.sheets = {}
        base_dir = os.path.dirname(__file__)
        
        sheet_paths = {
            'CP_V1.0.4.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", "CP_V1.0.4.png"),
            'BL001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "BL001.png"),
            'BD001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "BD001.png"),
            'SL001.png': os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations", "SL001.png")
        }
        
        for sheet_name, path in sheet_paths.items():
            try:
                self.sheets[sheet_name] = pygame.image.load(path)
                print(f"Loaded {sheet_name}")
            except Exception as e:
                print(f"Failed to load {sheet_name}: {e}")
                # Create placeholder
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((255, 0, 255))

    def load_tile_data(self):
        """Load unique items from findTiles_unique"""
        try:
            # Try loading from unique items format first
            with open("tile_selections_unique.json", "r") as f:
                data = json.load(f)
                self.unique_items = data.get('unique_items', {})
                
                # Convert to internal format for compatibility
                self.tiles = {}
                self.buildings = {}
                
                for name, item in self.unique_items.items():
                    if item['type'] == 'tile':
                        # Group tiles by a generic category for UI
                        if 'tiles' not in self.tiles:
                            self.tiles['tiles'] = []
                        self.tiles['tiles'].append(item['tile'])
                    else:  # building
                        self.buildings[name] = {
                            'size': item['size'],
                            'tiles': item['tiles'],
                            'category': 'building'  # Generic category
                        }
                
                print(f"Loaded {len(self.unique_items)} unique items")
                print(f"  - Tiles: {sum(1 for item in self.unique_items.values() if item['type'] == 'tile')}")
                print(f"  - Buildings: {sum(1 for item in self.unique_items.values() if item['type'] == 'building')}")
                return
        except:
            pass
            
        # Fallback to old format
        try:
            with open("tile_selections.json", "r") as f:
                data = json.load(f)
                self.tiles = data.get('tiles', {})
                self.buildings = data.get('buildings', {})
                self.unique_items = {}  # Empty for old format
                print(f"Loaded old format: {sum(len(tiles) for tiles in self.tiles.values())} tiles")
                print(f"Loaded {len(self.buildings)} buildings")
        except:
            print("No tile selections found!")
            self.tiles = {}
            self.buildings = {}
            self.unique_items = {}

    def get_tile_surface(self, tile_info):
        """Get a tile surface from sheet"""
        if not tile_info:
            return None
            
        sheet_name, x, y = tile_info
        if sheet_name not in self.sheets:
            return None
            
        sheet = self.sheets[sheet_name]
        try:
            src_rect = pygame.Rect(
                x * ORIGINAL_TILE_SIZE, 
                y * ORIGINAL_TILE_SIZE,
                ORIGINAL_TILE_SIZE, 
                ORIGINAL_TILE_SIZE
            )
            tile_surface = sheet.subsurface(src_rect)
            return pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
        except:
            return None

    def load_map(self):
        """Load existing map data"""
        try:
            with open("city_map_data.json", "r") as f:
                save_data = json.load(f)
                self.map_width = save_data['width']
                self.map_height = save_data['height']
                self.map_data = save_data['map_data']
                print(f"Loaded map: {self.map_width}x{self.map_height}")
        except:
            print("No existing map found, creating new")
            # Initialize with dirt tiles if available
            if 'dirt' in self.tiles and self.tiles['dirt']:
                default_tile = self.tiles['dirt'][0]
                for y in range(self.map_height):
                    for x in range(self.map_width):
                        self.map_data[y][x] = {
                            'type': 'tile',
                            'data': default_tile
                        }

    def save_map(self):
        """Save map data and render to PNG"""
        # Save map data
        save_data = {
            'width': self.map_width,
            'height': self.map_height,
            'map_data': self.map_data
        }
        
        with open("city_map_data.json", "w") as f:
            json.dump(save_data, f, indent=2)
        
        # Render to PNG for visualization
        render_surface = pygame.Surface((self.map_width * TILE_SIZE, self.map_height * TILE_SIZE))
        render_surface.fill((139, 69, 19))  # Brown/dirt background
        
        for y in range(self.map_height):
            for x in range(self.map_width):
                cell = self.map_data[y][x]
                if cell:
                    if cell['type'] == 'tile':
                        tile_surf = self.get_tile_surface(cell['data'])
                        if tile_surf:
                            render_surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))
                    elif cell['type'] == 'building_part':
                        # Get tile from building definition
                        building_name = cell['building_name']
                        offset_x = cell['offset_x']
                        offset_y = cell['offset_y']
                        
                        building = None
                        if self.unique_items and building_name in self.unique_items:
                            building = self.unique_items[building_name]
                        elif building_name in self.buildings:
                            building = self.buildings[building_name]
                            
                        if building:
                            if offset_y < len(building['tiles']) and offset_x < len(building['tiles'][offset_y]):
                                tile_info = building['tiles'][offset_y][offset_x]
                                tile_surf = self.get_tile_surface(tile_info)
                                if tile_surf:
                                    render_surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))
        
        # Scale down for PNG
        scaled_surface = pygame.transform.scale(render_surface, (self.map_width, self.map_height))
        pygame.image.save(scaled_surface, "city_map.png")
        
        self.unsaved_changes = False
        print("Map saved!")

    def place_tile(self, world_x, world_y):
        """Place a single tile"""
        if not self.selected_item or self.current_tool != ToolType.TILE:
            return
            
        if 0 <= world_x < self.map_width and 0 <= world_y < self.map_height:
            self.map_data[world_y][world_x] = {
                'type': 'tile',
                'data': self.selected_item
            }
            self.unsaved_changes = True

    def place_building(self, world_x, world_y):
        """Place a building"""
        if not self.selected_item or self.current_tool != ToolType.BUILDING:
            return
            
        # Handle unique items
        if self.unique_items and self.selected_item_name:
            building = self.unique_items[self.selected_item_name]
            width, height = building['size']
            
            # Check if it fits
            if world_x + width > self.map_width or world_y + height > self.map_height:
                return
                
            # Place all tiles
            for dy in range(height):
                for dx in range(width):
                    self.map_data[world_y + dy][world_x + dx] = {
                        'type': 'building_part',
                        'building_name': self.selected_item_name,
                        'offset_x': dx,
                        'offset_y': dy
                    }
        else:
            # Old format
            building = self.buildings[self.selected_item]
            width, height = building['size']
            
            # Check if it fits
            if world_x + width > self.map_width or world_y + height > self.map_height:
                return
                
            # Place all tiles
            for dy in range(height):
                for dx in range(width):
                    self.map_data[world_y + dy][world_x + dx] = {
                        'type': 'building_part',
                        'building_name': self.selected_item,
                        'offset_x': dx,
                        'offset_y': dy
                    }
        
        self.unsaved_changes = True

    def erase_tile(self, world_x, world_y):
        """Erase a tile"""
        if 0 <= world_x < self.map_width and 0 <= world_y < self.map_height:
            self.map_data[world_y][world_x] = None
            self.unsaved_changes = True
    
    def fill_building_background(self, world_x, world_y):
        """Fill the background of a building at this position with selected tile"""
        if not self.selected_item or self.current_tool != ToolType.TILE:
            return False
            
        # Check if there's a building at this position
        cell = self.map_data[world_y][world_x]
        if not cell or cell.get('type') != 'building_part':
            return False
            
        # Get the building info
        building_name = cell['building_name']
        
        # Find all tiles of this building
        building_tiles = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                check_cell = self.map_data[y][x]
                if (check_cell and check_cell.get('type') == 'building_part' 
                    and check_cell.get('building_name') == building_name):
                    building_tiles.append((x, y))
        
        # For each building tile, store it with a background
        for bx, by in building_tiles:
            # Store the building data with background info
            self.map_data[by][bx] = {
                'type': 'building_part_with_bg',
                'building_name': building_name,
                'offset_x': self.map_data[by][bx]['offset_x'],
                'offset_y': self.map_data[by][bx]['offset_y'],
                'background': self.selected_item  # Store the background tile
            }
        
        self.unsaved_changes = True
        print(f"Filled background for {building_name} with {len(building_tiles)} tiles")
        return True

    def update_preview(self, mouse_x, mouse_y):
        """Update preview based on current tool"""
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
        if world_x is None:
            self.preview_tiles = []
            return
            
        self.preview_tiles = []
        self.preview_valid = True
        
        if self.current_tool == ToolType.TILE and self.selected_item:
            self.preview_tiles = [(world_x, world_y)]
            
        elif self.current_tool == ToolType.BUILDING and self.selected_item:
            building = None
            if self.unique_items and self.selected_item_name:
                building = self.unique_items[self.selected_item_name]
            elif self.selected_item in self.buildings:
                building = self.buildings[self.selected_item]
                
            if not building:
                return
                
            width, height = building['size']
            
            # Check validity
            if world_x + width > self.map_width or world_y + height > self.map_height:
                self.preview_valid = False
                
            for dy in range(height):
                for dx in range(width):
                    self.preview_tiles.append((world_x + dx, world_y + dy))

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (x - self.camera_x) * self.zoom * TILE_SIZE + SIDEBAR_WIDTH
        screen_y = (y - self.camera_y) * self.zoom * TILE_SIZE
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        if screen_x < SIDEBAR_WIDTH:
            return None, None
            
        world_x = int((screen_x - SIDEBAR_WIDTH) / (self.zoom * TILE_SIZE) + self.camera_x)
        world_y = int(screen_y / (self.zoom * TILE_SIZE) + self.camera_y)
        
        if 0 <= world_x < self.map_width and 0 <= world_y < self.map_height:
            return world_x, world_y
        return None, None

    def draw_map(self):
        """Draw the map with actual textures"""
        # Calculate visible range
        start_x = max(0, int(self.camera_x))
        end_x = min(self.map_width, int(self.camera_x + MAP_AREA_WIDTH / (self.zoom * TILE_SIZE)) + 2)
        start_y = max(0, int(self.camera_y))
        end_y = min(self.map_height, int(self.camera_y + SCREEN_HEIGHT / (self.zoom * TILE_SIZE)) + 2)
        
        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x, screen_y = self.world_to_screen(x, y)
                
                # Draw base (dirt)
                base_rect = pygame.Rect(screen_x, screen_y, self.zoom * TILE_SIZE, self.zoom * TILE_SIZE)
                pygame.draw.rect(self.screen, (139, 69, 19), base_rect)
                
                # Draw tile content
                cell = self.map_data[y][x]
                if cell:
                    if cell['type'] == 'tile':
                        tile_surf = self.get_tile_surface(cell['data'])
                        if tile_surf:
                            scaled = pygame.transform.scale(tile_surf, (self.zoom * TILE_SIZE, self.zoom * TILE_SIZE))
                            self.screen.blit(scaled, (screen_x, screen_y))
                            
                    elif cell['type'] in ['building_part', 'building_part_with_bg']:
                        # Draw background first if it exists
                        if cell['type'] == 'building_part_with_bg' and 'background' in cell:
                            bg_surf = self.get_tile_surface(cell['background'])
                            if bg_surf:
                                bg_scaled = pygame.transform.scale(bg_surf, (self.zoom * TILE_SIZE, self.zoom * TILE_SIZE))
                                self.screen.blit(bg_scaled, (screen_x, screen_y))
                        
                        # Then draw the building tile
                        building_name = cell['building_name']
                        building = None
                        
                        # Try unique items first
                        if self.unique_items and building_name in self.unique_items:
                            building = self.unique_items[building_name]
                        elif building_name in self.buildings:
                            building = self.buildings[building_name]
                        
                        if building:
                            offset_x = cell['offset_x']
                            offset_y = cell['offset_y']
                            
                            if offset_y < len(building['tiles']) and offset_x < len(building['tiles'][offset_y]):
                                tile_info = building['tiles'][offset_y][offset_x]
                                tile_surf = self.get_tile_surface(tile_info)
                                if tile_surf:
                                    scaled = pygame.transform.scale(tile_surf, (self.zoom * TILE_SIZE, self.zoom * TILE_SIZE))
                                    self.screen.blit(scaled, (screen_x, screen_y))
                
                # Draw grid
                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR, base_rect, 1)
        
        # Draw preview
        if self.preview_tiles:
            for px, py in self.preview_tiles:
                screen_x, screen_y = self.world_to_screen(px, py)
                preview_rect = pygame.Rect(screen_x, screen_y, self.zoom * TILE_SIZE, self.zoom * TILE_SIZE)
                
                color = (0, 255, 0, 100) if self.preview_valid else (255, 0, 0, 100)
                preview_surf = pygame.Surface((self.zoom * TILE_SIZE, self.zoom * TILE_SIZE))
                preview_surf.set_alpha(100)
                preview_surf.fill(color[:3])
                self.screen.blit(preview_surf, (screen_x, screen_y))
                
                pygame.draw.rect(self.screen, color[:3], preview_rect, 2)

    def draw_sidebar(self):
        """Draw the sidebar UI"""
        # Background
        pygame.draw.rect(self.screen, SIDEBAR_COLOR, (0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        
        # Fixed header section
        y_offset = 10
        
        # Title
        title = self.title_font.render("Visual Map Editor", True, TEXT_COLOR)
        self.screen.blit(title, (10, y_offset))
        y_offset += 40
        
        # Save button
        save_rect = pygame.Rect(10, y_offset, SIDEBAR_WIDTH - 20, 30)
        color = BUTTON_ACTIVE_COLOR if self.unsaved_changes else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, save_rect)
        save_text = self.font.render("Save Map (S)" + (" *" if self.unsaved_changes else ""), True, TEXT_COLOR)
        text_rect = save_text.get_rect(center=save_rect.center)
        self.screen.blit(save_text, text_rect)
        y_offset += 40
        
        # Background Fill Mode button (when tile tool and tile selected)
        if self.current_tool == ToolType.TILE and self.selected_item:
            bg_rect = pygame.Rect(10, y_offset, SIDEBAR_WIDTH - 20, 30)
            color = BUTTON_ACTIVE_COLOR if self.background_fill_mode else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, bg_rect)
            bg_text = self.font.render("Fill Building BG (F)" + (" ON" if self.background_fill_mode else ""), True, TEXT_COLOR)
            text_rect = bg_text.get_rect(center=bg_rect.center)
            self.screen.blit(bg_text, text_rect)
            y_offset += 40
        
        # Tool buttons
        tools = [
            (ToolType.TILE, "Single Tiles (T)"),
            (ToolType.BUILDING, "Buildings (B)"),
            (ToolType.ERASER, "Eraser (E)"),
            (ToolType.FILL, "Fill Tool (F)")
        ]
        
        for tool, name in tools:
            rect = pygame.Rect(10, y_offset, SIDEBAR_WIDTH - 20, 30)
            is_active = self.current_tool == tool
            color = BUTTON_ACTIVE_COLOR if is_active else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            y_offset += 35
        
        y_offset += 10
        
        # Search box for unique items
        if self.unique_items:
            search_rect = pygame.Rect(10, y_offset, SIDEBAR_WIDTH - 20, 30)
            search_color = BUTTON_ACTIVE_COLOR if self.search_active else BUTTON_COLOR
            pygame.draw.rect(self.screen, search_color, search_rect, border_radius=5)
            
            # Search icon and text
            search_label = self.font.render("🔍 Search: " + self.search_text + ("_" if self.search_active else ""), True, TEXT_COLOR)
            self.screen.blit(search_label, (search_rect.x + 10, search_rect.y + 5))
            
            # Show match count when searching
            if self.search_text:
                item_type = 'tile' if self.current_tool == ToolType.TILE else 'building'
                matches = sum(1 for name, item in self.unique_items.items() 
                            if item['type'] == item_type and self.search_text.lower() in name.lower())
                total = sum(1 for item in self.unique_items.values() if item['type'] == item_type)
                count_text = self.small_font.render(f"{matches}/{total} matches", True, (180, 180, 180))
                self.screen.blit(count_text, (search_rect.x + search_rect.width - count_text.get_width() - 10, search_rect.y + 8))
            
            y_offset += 40
            
        # For unique items mode, skip category selection
        if not self.unique_items:
            # Old category selection for compatibility
            categories = list(self.tiles.keys()) if self.current_tool == ToolType.TILE else ['all']
            
            if categories:
                cat_text = self.font.render("Categories:", True, TEXT_COLOR)
                self.screen.blit(cat_text, (10, y_offset))
                y_offset += 25
                
                for category in categories:
                    rect = pygame.Rect(10, y_offset - self.sidebar_scroll, SIDEBAR_WIDTH - 40, 25)
                    is_selected = category == self.selected_category
                    if rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)):
                        color = BUTTON_ACTIVE_COLOR if is_selected else BUTTON_COLOR
                        pygame.draw.rect(self.screen, color, rect)
                        text = self.font.render(category, True, TEXT_COLOR)
                        self.screen.blit(text, (20, rect.y + 5))
                    y_offset += 30
            
            y_offset += 10
        
        # Item list based on tool
        if self.unique_items:
            # Show unique items
            if self.current_tool == ToolType.TILE:
                items_text = self.font.render("Tiles:", True, TEXT_COLOR)
                self.screen.blit(items_text, (10, y_offset - self.sidebar_scroll))
                y_offset += 30
                
                # Show filtered tile items with better layout
                for name, item in sorted(self.unique_items.items()):
                    if item['type'] == 'tile' and (not self.search_text or self.search_text.lower() in name.lower()):
                        rect = pygame.Rect(10, y_offset - self.sidebar_scroll, SIDEBAR_WIDTH - 30, 60)
                        if rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT - 200)):
                            is_selected = self.selected_item_name == name
                            
                            # Draw background with rounded corners effect
                            if is_selected:
                                pygame.draw.rect(self.screen, BUTTON_ACTIVE_COLOR, rect, border_radius=5)
                                pygame.draw.rect(self.screen, (255, 220, 100), rect, 2, border_radius=5)
                            else:
                                pygame.draw.rect(self.screen, BUTTON_COLOR, rect, border_radius=5)
                                if rect.collidepoint(pygame.mouse.get_pos()):
                                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1, border_radius=5)
                            
                            # Draw tile preview with border
                            preview_rect = pygame.Rect(rect.x + 8, rect.y + 10, 40, 40)
                            pygame.draw.rect(self.screen, (60, 60, 60), preview_rect, 1)
                            
                            tile_surf = self.get_tile_surface(item['tile'])
                            if tile_surf:
                                # Scale to fit preview box
                                scaled_tile = pygame.transform.scale(tile_surf, (38, 38))
                                self.screen.blit(scaled_tile, (preview_rect.x + 1, preview_rect.y + 1))
                            
                            # Tile name (larger, bold)
                            name_text = self.font.render(name, True, TEXT_COLOR if not is_selected else (255, 255, 100))
                            self.screen.blit(name_text, (rect.x + 55, rect.y + 12))
                            
                            # Tile info (smaller)
                            info_text = self.small_font.render(f"Sheet: {item['tile'][0]}", True, (160, 160, 160))
                            self.screen.blit(info_text, (rect.x + 55, rect.y + 35))
                            
                        y_offset += 65
            
            elif self.current_tool == ToolType.BUILDING:
                items_text = self.font.render("Buildings:", True, TEXT_COLOR)
                self.screen.blit(items_text, (10, y_offset - self.sidebar_scroll))
                y_offset += 30
                
                # Show filtered building items with better layout
                for name, item in sorted(self.unique_items.items()):
                    if item['type'] == 'building' and (not self.search_text or self.search_text.lower() in name.lower()):
                        rect = pygame.Rect(10, y_offset - self.sidebar_scroll, SIDEBAR_WIDTH - 30, 65)
                        if rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT - 200)):
                            is_selected = self.selected_item_name == name
                            
                            # Draw background with rounded corners
                            if is_selected:
                                pygame.draw.rect(self.screen, BUTTON_ACTIVE_COLOR, rect, border_radius=5)
                                pygame.draw.rect(self.screen, (255, 220, 100), rect, 2, border_radius=5)
                            else:
                                pygame.draw.rect(self.screen, BUTTON_COLOR, rect, border_radius=5)
                                if rect.collidepoint(pygame.mouse.get_pos()):
                                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1, border_radius=5)
                            
                            # Building preview with border
                            preview_rect = pygame.Rect(rect.x + 8, rect.y + 12, 40, 40)
                            pygame.draw.rect(self.screen, (60, 60, 60), preview_rect, 1)
                            
                            if item['tiles'] and item['tiles'][0]:
                                tile_surf = self.get_tile_surface(item['tiles'][0][0])
                                if tile_surf:
                                    scaled_tile = pygame.transform.scale(tile_surf, (38, 38))
                                    self.screen.blit(scaled_tile, (preview_rect.x + 1, preview_rect.y + 1))
                            
                            # Building name
                            name_text = self.font.render(name, True, TEXT_COLOR if not is_selected else (255, 255, 100))
                            self.screen.blit(name_text, (rect.x + 55, rect.y + 12))
                            
                            # Size info with icon
                            size_text = self.small_font.render(f"Size: {item['size'][0]}×{item['size'][1]} tiles", True, (160, 160, 160))
                            self.screen.blit(size_text, (rect.x + 55, rect.y + 35))
                            
                        y_offset += 70
        
        else:
            # Old format compatibility
            if self.current_tool == ToolType.TILE and self.selected_category in self.tiles:
                items_text = self.font.render("Tiles:", True, TEXT_COLOR)
                self.screen.blit(items_text, (10, y_offset - self.sidebar_scroll))
                y_offset += 30
                
                for i, tile_info in enumerate(self.tiles[self.selected_category]):
                    rect = pygame.Rect(10, y_offset - self.sidebar_scroll, SIDEBAR_WIDTH - 40, 40)
                    if rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)):
                        is_selected = self.selected_item == tile_info
                        color = BUTTON_ACTIVE_COLOR if is_selected else BUTTON_COLOR
                        pygame.draw.rect(self.screen, color, rect)
                        
                        # Draw tile preview
                        tile_surf = self.get_tile_surface(tile_info)
                        if tile_surf:
                            self.screen.blit(tile_surf, (rect.x + 5, rect.y + 4))
                        
                        # Tile info
                        info_text = self.small_font.render(f"{tile_info[0]} ({tile_info[1]},{tile_info[2]})", True, TEXT_COLOR)
                        self.screen.blit(info_text, (rect.x + 45, rect.y + 12))
                        
                    y_offset += 45
                
            elif self.current_tool == ToolType.BUILDING:
                items_text = self.font.render("Buildings:", True, TEXT_COLOR)
                self.screen.blit(items_text, (10, y_offset - self.sidebar_scroll))
                y_offset += 30
                
                for name, building in self.buildings.items():
                    rect = pygame.Rect(10, y_offset - self.sidebar_scroll, SIDEBAR_WIDTH - 40, 50)
                    if rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)):
                        is_selected = self.selected_item == name
                        color = BUTTON_ACTIVE_COLOR if is_selected else BUTTON_COLOR
                        pygame.draw.rect(self.screen, color, rect)
                        
                        # Building preview (first tile)
                        if building['tiles'] and building['tiles'][0]:
                            tile_surf = self.get_tile_surface(building['tiles'][0][0])
                            if tile_surf:
                                self.screen.blit(tile_surf, (rect.x + 5, rect.y + 9))
                        
                        # Building info
                        name_text = self.small_font.render(name, True, TEXT_COLOR)
                        self.screen.blit(name_text, (rect.x + 45, rect.y + 8))
                        
                        size_text = self.small_font.render(f"Size: {building['size'][0]}x{building['size'][1]}", True, (200, 200, 200))
                        self.screen.blit(size_text, (rect.x + 45, rect.y + 28))
                        
                    y_offset += 55
        
        # Calculate max scroll
        content_height = y_offset
        visible_height = SCREEN_HEIGHT - 250  # Leave space for controls
        self.max_sidebar_scroll = max(0, content_height - visible_height)
        
        # Draw scroll indicator if needed
        if self.max_sidebar_scroll > 0:
            # Scroll bar background
            scrollbar_x = SIDEBAR_WIDTH - 10
            scrollbar_y = 250
            scrollbar_height = visible_height - 50
            pygame.draw.rect(self.screen, (40, 40, 40), 
                           (scrollbar_x, scrollbar_y, 6, scrollbar_height))
            
            # Scroll bar position
            scroll_percent = self.sidebar_scroll / self.max_sidebar_scroll if self.max_sidebar_scroll > 0 else 0
            bar_height = max(20, scrollbar_height * (visible_height / content_height))
            bar_y = scrollbar_y + (scrollbar_height - bar_height) * scroll_percent
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (scrollbar_x, int(bar_y), 6, int(bar_height)))
        
        # Controls help (fixed at bottom)
        help_bg = pygame.Surface((SIDEBAR_WIDTH, 200))
        help_bg.fill(SIDEBAR_COLOR)
        self.screen.blit(help_bg, (0, SCREEN_HEIGHT - 200))
        
        # Draw separator line
        pygame.draw.line(self.screen, (60, 60, 60), 
                        (10, SCREEN_HEIGHT - 200), 
                        (SIDEBAR_WIDTH - 10, SCREEN_HEIGHT - 200), 1)
        
        help_y = SCREEN_HEIGHT - 190
        help_texts = [
            "Controls:",
            "WASD/Arrows - Move camera",
            "Mouse wheel - Zoom/Scroll",
            "Space + drag - Pan",
            "G - Toggle grid",
            "Click - Place/erase",
            "↑↓ - Scroll tile list"
        ]
        
        for text in help_texts:
            rendered = self.small_font.render(text, True, (180, 180, 180))
            self.screen.blit(rendered, (10, help_y))
            help_y += 20

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_s:
                    self.save_map()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_t:
                    self.current_tool = ToolType.TILE
                elif event.key == pygame.K_b:
                    self.current_tool = ToolType.BUILDING
                elif event.key == pygame.K_e:
                    self.current_tool = ToolType.ERASER
                elif event.key == pygame.K_f:
                    if self.current_tool == ToolType.TILE and self.selected_item:
                        # Toggle background fill mode
                        self.background_fill_mode = not self.background_fill_mode
                        print(f"Background fill mode: {'ON' if self.background_fill_mode else 'OFF'}")
                    else:
                        self.current_tool = ToolType.FILL
                        
                # Scroll sidebar with arrow keys  
                elif event.key == pygame.K_UP:
                    self.sidebar_scroll = max(0, self.sidebar_scroll - 50)
                elif event.key == pygame.K_DOWN:
                    self.sidebar_scroll = min(self.max_sidebar_scroll, self.sidebar_scroll + 50)
                elif event.key == pygame.K_PAGEUP:
                    self.sidebar_scroll = max(0, self.sidebar_scroll - 200)
                elif event.key == pygame.K_PAGEDOWN:
                    self.sidebar_scroll = min(self.max_sidebar_scroll, self.sidebar_scroll + 200)
                    
                # Search functionality
                elif event.key == pygame.K_SLASH or (event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.search_active = True
                    self.sidebar_scroll = 0  # Reset scroll when starting search
                elif event.key == pygame.K_ESCAPE and self.search_active:
                    self.search_active = False
                    self.search_text = ""
                    self.sidebar_scroll = 0
                elif self.search_active:
                    if event.key == pygame.K_RETURN:
                        self.search_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.search_text = self.search_text[:-1]
                    else:
                        # Add character to search
                        if event.unicode and event.unicode.isprintable():
                            self.search_text += event.unicode
                            
                elif event.key == pygame.K_SPACE and not self.search_active:
                    self.space_dragging = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.drag_start_x = mouse_x
                    self.drag_start_y = mouse_y
                    
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_dragging = False
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Check sidebar clicks
                if mouse_x < SIDEBAR_WIDTH:
                    self.handle_sidebar_click(mouse_x, mouse_y)
                else:
                    # Map clicks
                    if event.button == 1:  # Left click
                        self.mouse_dragging = True
                        world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
                        if world_x is not None:
                            if self.current_tool == ToolType.TILE:
                                # Check if we're in background fill mode
                                if self.background_fill_mode:
                                    self.fill_building_background(world_x, world_y)
                                else:
                                    self.place_tile(world_x, world_y)
                            elif self.current_tool == ToolType.BUILDING:
                                self.place_building(world_x, world_y)
                            elif self.current_tool == ToolType.ERASER:
                                self.erase_tile(world_x, world_y)
                                
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False
                    
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                
                # Handle panning
                if self.space_dragging:
                    dx = mouse_x - self.drag_start_x
                    dy = mouse_y - self.drag_start_y
                    self.camera_x -= dx / (self.zoom * TILE_SIZE)
                    self.camera_y -= dy / (self.zoom * TILE_SIZE)
                    self.drag_start_x = mouse_x
                    self.drag_start_y = mouse_y
                    
                # Handle dragging for tools
                elif self.mouse_dragging and mouse_x >= SIDEBAR_WIDTH:
                    world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
                    if world_x is not None:
                        if self.current_tool == ToolType.TILE:
                            self.place_tile(world_x, world_y)
                        elif self.current_tool == ToolType.ERASER:
                            self.erase_tile(world_x, world_y)
                            
                # Update preview
                self.update_preview(mouse_x, mouse_y)
                
            elif event.type == pygame.MOUSEWHEEL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check if mouse is over sidebar
                if mouse_x < SIDEBAR_WIDTH:
                    # Scroll sidebar
                    scroll_speed = 30
                    self.sidebar_scroll -= event.y * scroll_speed
                    self.sidebar_scroll = max(0, min(self.sidebar_scroll, self.max_sidebar_scroll))
                else:
                    # Zoom map
                    old_zoom = self.zoom
                    if event.y > 0:
                        self.zoom = min(4, self.zoom + 0.5)
                    else:
                        self.zoom = max(0.5, self.zoom - 0.5)
                        
                    # Adjust camera to zoom around mouse position
                    if old_zoom != self.zoom and mouse_x >= SIDEBAR_WIDTH:
                        # Calculate world position under mouse
                        world_x = (mouse_x - SIDEBAR_WIDTH) / (old_zoom * TILE_SIZE) + self.camera_x
                        world_y = mouse_y / (old_zoom * TILE_SIZE) + self.camera_y
                        
                        # Adjust camera so same world position stays under mouse
                        self.camera_x = world_x - (mouse_x - SIDEBAR_WIDTH) / (self.zoom * TILE_SIZE)
                        self.camera_y = world_y - mouse_y / (self.zoom * TILE_SIZE)
        
        # Handle keyboard camera movement
        keys = pygame.key.get_pressed()
        cam_speed = 10 / (self.zoom * TILE_SIZE)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera_y -= cam_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera_y += cam_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera_x -= cam_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera_x += cam_speed
            
        return True

    def handle_sidebar_click(self, x, y):
        """Handle clicks in the sidebar"""
        # Check save button
        save_rect = pygame.Rect(10, 50, SIDEBAR_WIDTH - 20, 30)
        if save_rect.collidepoint(x, y):
            self.save_map()
            return
            
        # Check background fill mode button
        if self.current_tool == ToolType.TILE and self.selected_item:
            bg_rect = pygame.Rect(10, 90, SIDEBAR_WIDTH - 20, 30)
            if bg_rect.collidepoint(x, y):
                self.background_fill_mode = not self.background_fill_mode
                print(f"Background fill mode: {'ON' if self.background_fill_mode else 'OFF'}")
                return
        
        # Check tool buttons (adjust Y based on whether BG button is shown)
        tool_y = 90 if not (self.current_tool == ToolType.TILE and self.selected_item) else 130
        tools = [
            (ToolType.TILE, "Single Tiles (T)"),
            (ToolType.BUILDING, "Buildings (B)"),
            (ToolType.ERASER, "Eraser (E)"),
            (ToolType.FILL, "Fill Tool (F)")
        ]
        
        for tool, name in tools:
            rect = pygame.Rect(10, tool_y, SIDEBAR_WIDTH - 20, 30)
            if rect.collidepoint(x, y):
                self.current_tool = tool
                # Turn off background fill mode when switching tools
                if tool != ToolType.TILE:
                    self.background_fill_mode = False
                return
            tool_y += 35
        
        # Check search box if using unique items
        if self.unique_items:
            search_y = tool_y + 10
            search_rect = pygame.Rect(10, search_y, SIDEBAR_WIDTH - 20, 30)
            if search_rect.collidepoint(x, y):
                self.search_active = True
                return
        
        # Check item selection
        if self.unique_items:
            # Calculate item list start position
            items_y = 250
            
            if self.current_tool == ToolType.TILE:
                for name, item in sorted(self.unique_items.items()):
                    if item['type'] == 'tile' and (not self.search_text or self.search_text.lower() in name.lower()):
                        rect = pygame.Rect(10, items_y - self.sidebar_scroll, SIDEBAR_WIDTH - 30, 60)
                        if rect.collidepoint(x, y) and rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT - 200)):
                            self.selected_item_name = name
                            self.selected_item = item['tile']
                            return
                        items_y += 65
            
            elif self.current_tool == ToolType.BUILDING:
                for name, item in sorted(self.unique_items.items()):
                    if item['type'] == 'building' and (not self.search_text or self.search_text.lower() in name.lower()):
                        rect = pygame.Rect(10, items_y - self.sidebar_scroll, SIDEBAR_WIDTH - 30, 65)
                        if rect.collidepoint(x, y) and rect.colliderect(pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT - 200)):
                            self.selected_item_name = name
                            self.selected_item = name  # For buildings, store the name
                            return
                        items_y += 70

    def run(self):
        """Main loop"""
        running = True
        while running:
            running = self.handle_events()
            
            # Clear screen
            self.screen.fill(BACKGROUND_COLOR)
            
            # Draw map area
            map_clip = pygame.Rect(SIDEBAR_WIDTH, 0, MAP_AREA_WIDTH, SCREEN_HEIGHT)
            self.screen.set_clip(map_clip)
            self.draw_map()
            self.screen.set_clip(None)
            
            # Draw sidebar
            self.draw_sidebar()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()


if __name__ == "__main__":
    editor = VisualMapEditor()
    editor.run()
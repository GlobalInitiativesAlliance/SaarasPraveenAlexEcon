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

CATEGORY_COLORS = {
    'road': (60, 60, 60),
    'sidewalk': (160, 160, 160),
    'grass': (50, 150, 50),
    'water': (50, 100, 200),
    'house': (150, 100, 50),
    'building': (120, 120, 120),
    'store': (200, 150, 100),
    'skyscraper': (70, 130, 180),
    'bank': (180, 180, 140),
}


class EnhancedTilePicker:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Tile Picker - Single tiles (Click) or Buildings (Drag)")
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

        # Categories
        self.categories = ['road', 'sidewalk', 'grass', 'water', 'house', 'building', 'store', 'skyscraper', 'bank']
        self.current_category = 0

        # Selection modes
        self.selection_mode = 'single'  # 'single' or 'building'

        # Selected items
        self.selected_tiles = {cat: [] for cat in self.categories}
        self.building_definitions = {}  # Store multi-tile buildings

        # UI State
        self.hover_tile = None
        self.show_help = True

        # Rectangle selection
        self.selecting_rect = False
        self.rect_start = None
        self.rect_end = None

        # Building preview
        self.preview_building = None

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
            # Calculate the total size when tiles are scaled up
            total_width = (sheet.get_width() // ORIGINAL_TILE_SIZE) * TILE_SIZE
            total_height = (sheet.get_height() // ORIGINAL_TILE_SIZE) * TILE_SIZE
            # Calculate max scroll based on scaled size
            self.max_scroll_x = max(0, total_width - (SCREEN_WIDTH - 300))
            self.max_scroll_y = max(0, total_height - (SCREEN_HEIGHT - 150))

    def save_selections(self):
        """Save selected tiles and building definitions"""
        # Save single tiles
        with open("selected_tiles.py", "w") as f:
            f.write("# Tile positions selected using the Enhanced Tile Picker\n\n")
            f.write("TILE_POSITIONS = {\n")
            for category, tiles in self.selected_tiles.items():
                f.write(f"    '{category}': [\n")
                for tile in tiles:
                    f.write(f"        {tile},\n")
                f.write("    ],\n")
            f.write("}\n")

        # Save building definitions
        with open("building_definitions.py", "w") as f:
            f.write("# Multi-tile building definitions\n\n")
            f.write("BUILDING_DEFINITIONS = {\n")
            for name, building in self.building_definitions.items():
                f.write(f"    '{name}': {{\n")
                f.write(f"        'size': {building['size']},\n")
                f.write(f"        'category': '{building['category']}',\n")
                f.write(f"        'tiles': [\n")
                for row in building['tiles']:
                    f.write(f"            {row},\n")
                f.write("        ]\n")
                f.write("    },\n")
            f.write("}\n")

        # Save as JSON for easy loading
        save_data = {
            'tiles': self.selected_tiles,
            'buildings': self.building_definitions
        }
        with open("tile_selections.json", "w") as f:
            json.dump(save_data, f, indent=2)

        print("Saved selections to selected_tiles.py, building_definitions.py, and tile_selections.json")

    def load_selections(self):
        """Load previously selected tiles and buildings"""
        try:
            with open("tile_selections.json", "r") as f:
                data = json.load(f)

                # Load single tiles
                if 'tiles' in data:
                    for category in data['tiles']:
                        self.selected_tiles[category] = [tuple(tile) for tile in data['tiles'][category]]

                # Load building definitions
                if 'buildings' in data:
                    self.building_definitions = data['buildings']
                    # Convert tile lists back to tuples
                    for building in self.building_definitions.values():
                        building['tiles'] = [[tuple(tile) for tile in row] for row in building['tiles']]
                        building['size'] = tuple(building['size'])

                print("Loaded previous selections")
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

    def toggle_tile_selection(self, tile_info):
        """Toggle selection of a single tile"""
        if not tile_info:
            return

        category = self.categories[self.current_category]

        if tile_info in self.selected_tiles[category]:
            self.selected_tiles[category].remove(tile_info)
            print(f"Removed {tile_info} from {category}")
        else:
            self.selected_tiles[category].append(tile_info)
            print(f"Added {tile_info} to {category}")

    def create_building_from_rect(self, start_tile, end_tile):
        """Create a building definition from a rectangle selection"""
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

        # Create building definition
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append((sheet_name, min_x + x, min_y + y))
            tiles.append(row)

        # Generate unique name
        category = self.categories[self.current_category]
        building_count = sum(1 for name in self.building_definitions if name.startswith(category))
        building_name = f"{category}_{building_count + 1}_{width}x{height}"

        self.building_definitions[building_name] = {
            'size': (width, height),
            'category': category,
            'tiles': tiles
        }

        print(f"Created building: {building_name} ({width}x{height})")

    def draw_ui(self):
        """Draw the UI elements"""
        self.screen.fill(BG_COLOR)

        # Left panel
        panel_width = 280
        pygame.draw.rect(self.screen, (40, 40, 50), (0, 0, panel_width, SCREEN_HEIGHT))

        # Title
        title = self.font.render("ENHANCED TILE PICKER", True, TEXT_COLOR)
        self.screen.blit(title, (10, 10))

        # Mode indicator
        mode_text = self.small_font.render(f"Mode: {self.selection_mode.upper()}", True,
                                           (255, 255, 100) if self.selection_mode == 'building' else TEXT_COLOR)
        self.screen.blit(mode_text, (10, 40))

        # Categories
        y_offset = 80
        for i, category in enumerate(self.categories):
            if i == self.current_category:
                pygame.draw.rect(self.screen, (60, 60, 80), (5, y_offset - 5, panel_width - 10, 30))

            pygame.draw.rect(self.screen, CATEGORY_COLORS[category], (10, y_offset, 20, 20))

            # Count tiles and buildings
            tile_count = len(self.selected_tiles[category])
            building_count = sum(1 for b in self.building_definitions.values() if b['category'] == category)
            text = self.font.render(f"{category} (T:{tile_count} B:{building_count})", True, TEXT_COLOR)
            self.screen.blit(text, (40, y_offset))

            y_offset += 35

        # Buildings in current category
        y_offset += 20
        buildings_text = self.small_font.render("Buildings in category:", True, TEXT_COLOR)
        self.screen.blit(buildings_text, (10, y_offset))
        y_offset += 25

        category = self.categories[self.current_category]
        building_y = y_offset
        for name, building in self.building_definitions.items():
            if building['category'] == category:
                size_text = self.small_font.render(f"{name}: {building['size'][0]}x{building['size'][1]}",
                                                   True, TEXT_COLOR)
                self.screen.blit(size_text, (10, building_y))
                building_y += 20
                if building_y > SCREEN_HEIGHT - 250:
                    break

        # Help text
        if self.show_help:
            help_y = SCREEN_HEIGHT - 230
            help_texts = [
                "Controls:",
                "M: Toggle mode (Single/Building)",
                "Click: Select single tile",
                "Drag: Select building area",
                "1-9: Switch category",
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
        if self.selection_mode == 'building':
            action_text = "DRAG to select building area"
            color = (255, 200, 100)
        else:
            action_text = "CLICK to select/deselect tiles"
            color = TEXT_COLOR
        rendered = self.font.render(action_text, True, color)
        self.screen.blit(rendered, (panel_width + 10, 10))

        # Current category
        cat_text = self.font.render(f"Category: {self.categories[self.current_category].upper()}",
                                    True, CATEGORY_COLORS[self.categories[self.current_category]])
        self.screen.blit(cat_text, (panel_width + 10, 40))

        # Sheet info
        sheet_text = self.small_font.render(f"Sheet: {self.sheet_names[self.current_sheet_index]}",
                                            True, TEXT_COLOR)
        self.screen.blit(sheet_text, (panel_width + 10, 70))

        # Hover info
        if self.hover_tile:
            hover_text = f"Tile: {self.hover_tile[1]}, {self.hover_tile[2]}"
            rendered = self.small_font.render(hover_text, True, TEXT_COLOR)
            self.screen.blit(rendered, (panel_width + 10, 100))

    def draw_tile_grid(self):
        """Draw the sprite sheet with grid and selections"""
        sheet_name = self.sheet_names[self.current_sheet_index]
        if sheet_name not in self.sheets:
            return

        sheet = self.sheets[sheet_name]

        # Create selection overlay surface
        overlay = pygame.Surface((SCREEN_WIDTH - 300, SCREEN_HEIGHT - 150), pygame.SRCALPHA)

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

                    # Highlight single tile selections
                    tile_info = (sheet_name, x, y)
                    for category, tiles in self.selected_tiles.items():
                        if tile_info in tiles:
                            color = CATEGORY_COLORS[category]
                            pygame.draw.rect(self.screen, color,
                                             (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 3)

                    # Draw grid
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Draw building overlays
        for name, building in self.building_definitions.items():
            if building['tiles'] and building['tiles'][0][0][0] == sheet_name:
                # Check if this building is visible
                top_left = building['tiles'][0][0]
                if start_x <= top_left[1] < end_x and start_y <= top_left[2] < end_y:
                    # Draw building outline
                    x = 300 + top_left[1] * TILE_SIZE - self.scroll_x
                    y = 150 + top_left[2] * TILE_SIZE - self.scroll_y
                    w = building['size'][0] * TILE_SIZE
                    h = building['size'][1] * TILE_SIZE

                    color = CATEGORY_COLORS[building['category']]
                    pygame.draw.rect(overlay, (*color, 64), (x - 300, y - 150, w, h))
                    pygame.draw.rect(self.screen, color, (x, y, w, h), 2)

                    # Draw building name
                    text = self.small_font.render(name.split('_')[-1], True, color)
                    self.screen.blit(text, (x + 2, y + 2))

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

        # Apply overlay
        self.screen.blit(overlay, (300, 150))

        # Highlight hover
        if self.hover_tile:
            x = 300 + self.hover_tile[1] * TILE_SIZE - self.scroll_x
            y = 150 + self.hover_tile[2] * TILE_SIZE - self.scroll_y
            pygame.draw.rect(self.screen, HOVER_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 2)

    def handle_input(self, event):
        """Handle user input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_m:
                self.selection_mode = 'building' if self.selection_mode == 'single' else 'single'
                print(f"Switched to {self.selection_mode} mode")
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
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                if index < len(self.categories):
                    self.current_category = index
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
                tile = self.get_tile_at_pos(*event.pos)
                if self.selection_mode == 'single':
                    self.toggle_tile_selection(tile)
                elif self.selection_mode == 'building' and tile:
                    self.selecting_rect = True
                    self.rect_start = tile
                    self.rect_end = tile

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.selecting_rect:
                # Finish rectangle selection
                self.create_building_from_rect(self.rect_start, self.rect_end)
                self.selecting_rect = False
                self.rect_start = None
                self.rect_end = None

        elif event.type == pygame.MOUSEMOTION:
            self.hover_tile = self.get_tile_at_pos(*event.pos)
            if self.selecting_rect and self.hover_tile:
                self.rect_end = self.hover_tile

        elif event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self.scroll_x = max(0, min(self.max_scroll_x,
                                           self.scroll_x - event.y * TILE_SIZE))
            else:
                self.scroll_y = max(0, min(self.max_scroll_y,
                                           self.scroll_y - event.y * TILE_SIZE))

        return True

    def run(self):
        """Main loop"""
        print("\n=== ENHANCED TILE PICKER ===")
        print("Press M to toggle between Single Tile and Building modes")
        print("In Building mode, drag to select multi-tile buildings")
        print("Press S to save, L to load, H for help\n")

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
    tool = EnhancedTilePicker()
    tool.run()
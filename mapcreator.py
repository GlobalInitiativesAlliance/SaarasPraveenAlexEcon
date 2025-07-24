import pygame
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
TILE_SIZE = 16  # Size for editing (matches PNG pixels)
SIDEBAR_WIDTH = 300
MAP_AREA_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH

# Colors
BACKGROUND_COLOR = (40, 40, 40)
SIDEBAR_COLOR = (30, 30, 30)
GRID_COLOR = (60, 60, 60)
SELECTED_COLOR = (255, 255, 0)
HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (90, 90, 90)
BUTTON_ACTIVE_COLOR = (110, 110, 110)

# Color mappings for the PNG
TILE_COLORS = {
    'grass': (34, 139, 34),
    'tree': (0, 100, 0),
    'rock': (128, 128, 128),
    'water': (0, 119, 190),
    'sand': (238, 203, 173),
    'dirt': (139, 69, 19),
    'deep_water': (0, 80, 150),
    'road': (32, 32, 32),
    'sidewalk': (190, 190, 190),
    'house': (139, 90, 43),
    'bank': (192, 192, 192),
    'building': (105, 105, 105),
    'skyscraper': (70, 130, 180),
    'store': (255, 140, 0),
}


class ToolType(Enum):
    TILE = 1
    BUILDING = 2
    ERASER = 3


class MapEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Map Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 24)

        # Load data
        self.load_tile_data()
        self.load_map()

        # Editor state
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 2  # Start zoomed in for easier editing
        self.show_grid = True
        self.current_tool = ToolType.TILE
        self.selected_tile = 'grass'
        self.selected_building = None
        self.mouse_dragging = False
        self.space_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # UI elements
        self.sidebar_scroll = 0
        self.max_sidebar_scroll = 0
        self.hovering_tile = None
        self.unsaved_changes = False

        # Preview
        self.preview_building = None
        self.preview_x = 0
        self.preview_y = 0

    def load_tile_data(self):
        """Load tile and building data from JSON"""
        try:
            with open("tile_selections.json", "r") as f:
                data = json.load(f)
                self.tiles = data.get('tiles', {})
                self.buildings = data.get('buildings', {})
                print(f"Loaded {len(self.tiles)} tile categories")
                print(f"Loaded {len(self.buildings)} building types")
        except FileNotFoundError:
            print("tile_selections.json not found!")
            self.tiles = {}
            self.buildings = {}

    def load_map(self):
        """Load the existing city map"""
        try:
            self.map_surface = pygame.image.load("city_map.png")
            self.map_width = self.map_surface.get_width()
            self.map_height = self.map_surface.get_height()
            print(f"Loaded map: {self.map_width}x{self.map_height}")
        except:
            # Create new map if doesn't exist
            self.map_width = 64
            self.map_height = 64
            self.map_surface = pygame.Surface((self.map_width, self.map_height))
            self.map_surface.fill(TILE_COLORS['dirt'])
            print("Created new map")

    def save_map(self):
        """Save the map to PNG"""
        pygame.image.save(self.map_surface, "city_map.png")
        self.unsaved_changes = False
        print("Map saved to city_map.png")

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (x - self.camera_x) * self.zoom * TILE_SIZE + SIDEBAR_WIDTH
        screen_y = (y - self.camera_y) * self.zoom * TILE_SIZE
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        if screen_x < SIDEBAR_WIDTH:
            return None, None
        world_x = (screen_x - SIDEBAR_WIDTH) // (self.zoom * TILE_SIZE) + self.camera_x
        world_y = screen_y // (self.zoom * TILE_SIZE) + self.camera_y
        if 0 <= world_x < self.map_width and 0 <= world_y < self.map_height:
            return world_x, world_y
        return None, None

    def draw_map(self):
        """Draw the map with grid"""
        # Calculate visible range
        start_x = max(0, self.camera_x)
        end_x = min(self.map_width, self.camera_x + MAP_AREA_WIDTH // (self.zoom * TILE_SIZE) + 1)
        start_y = max(0, self.camera_y)
        end_y = min(self.map_height, self.camera_y + SCREEN_HEIGHT // (self.zoom * TILE_SIZE) + 1)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                color = self.map_surface.get_at((x, y))
                screen_x, screen_y = self.world_to_screen(x, y)

                # Draw the tile
                pygame.draw.rect(self.screen, (color.r, color.g, color.b),
                                 (screen_x, screen_y, self.zoom * TILE_SIZE, self.zoom * TILE_SIZE))

                # Draw grid
                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, self.zoom * TILE_SIZE, self.zoom * TILE_SIZE), 1)

        # Draw building preview
        if self.preview_building and self.current_tool == ToolType.BUILDING:
            self.draw_building_preview()

        # Highlight hovered tile
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
        if world_x is not None:
            screen_x, screen_y = self.world_to_screen(world_x, world_y)
            pygame.draw.rect(self.screen, HOVER_COLOR,
                             (screen_x, screen_y, self.zoom * TILE_SIZE, self.zoom * TILE_SIZE), 2)

    def draw_building_preview(self):
        """Draw preview of building placement"""
        if not self.selected_building or self.selected_building not in self.buildings:
            return

        building = self.buildings[self.selected_building]
        width, height = building['size']

        # Check if placement is valid
        valid = self.can_place_building(self.preview_x, self.preview_y, width, height)

        # Draw preview rectangles
        for dy in range(height):
            for dx in range(width):
                x, y = self.preview_x + dx, self.preview_y + dy
                if 0 <= x < self.map_width and 0 <= y < self.map_height:
                    screen_x, screen_y = self.world_to_screen(x, y)
                    color = (0, 255, 0, 128) if valid else (255, 0, 0, 128)
                    preview_surf = pygame.Surface((self.zoom * TILE_SIZE, self.zoom * TILE_SIZE))
                    preview_surf.set_alpha(128)
                    preview_surf.fill(color[:3])
                    self.screen.blit(preview_surf, (screen_x, screen_y))
                    pygame.draw.rect(self.screen, color[:3],
                                     (screen_x, screen_y, self.zoom * TILE_SIZE, self.zoom * TILE_SIZE), 2)

    def can_place_building(self, x, y, width, height):
        """Check if building can be placed at position"""
        if x + width > self.map_width or y + height > self.map_height:
            return False
        if x < 0 or y < 0:
            return False
        return True

    def place_building(self, x, y):
        """Place selected building at position"""
        if not self.selected_building or self.selected_building not in self.buildings:
            return

        building = self.buildings[self.selected_building]
        width, height = building['size']

        if not self.can_place_building(x, y, width, height):
            return

        # Get building color
        building_type = building['category']
        color = TILE_COLORS.get(building_type, TILE_COLORS['building'])

        # Fill the area with building color
        for dy in range(height):
            for dx in range(width):
                self.map_surface.set_at((x + dx, y + dy), color)

        self.unsaved_changes = True

    def draw_sidebar(self):
        """Draw the sidebar with tools and options"""
        # Background
        pygame.draw.rect(self.screen, SIDEBAR_COLOR, (0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        y_offset = 10

        # Title
        title = self.title_font.render("Map Editor", True, TEXT_COLOR)
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

        # Tool selection
        tools = [
            (ToolType.TILE, "Tiles"),
            (ToolType.BUILDING, "Buildings"),
            (ToolType.ERASER, "Eraser")
        ]

        for tool, name in tools:
            rect = pygame.Rect(10, y_offset, SIDEBAR_WIDTH - 20, 30)
            color = BUTTON_ACTIVE_COLOR if self.current_tool == tool else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            y_offset += 35

        y_offset += 10
        pygame.draw.line(self.screen, GRID_COLOR, (10, y_offset), (SIDEBAR_WIDTH - 10, y_offset))
        y_offset += 10

        # Scrollable content area
        content_start_y = y_offset
        content_height = SCREEN_HEIGHT - y_offset - 100

        # Create clipping rectangle for scrollable area
        clip_rect = pygame.Rect(0, content_start_y, SIDEBAR_WIDTH, content_height)
        self.screen.set_clip(clip_rect)

        # Offset for scrolling
        y_offset -= self.sidebar_scroll

        # Show options based on current tool
        if self.current_tool == ToolType.TILE:
            self.draw_tile_options(y_offset)
        elif self.current_tool == ToolType.BUILDING:
            self.draw_building_options(y_offset)
        elif self.current_tool == ToolType.ERASER:
            text = self.font.render("Click to erase tiles", True, TEXT_COLOR)
            self.screen.blit(text, (10, y_offset))

        # Remove clipping
        self.screen.set_clip(None)

        # Controls info at bottom
        y_offset = SCREEN_HEIGHT - 90
        controls = [
            "Space + Drag: Pan",
            "Scroll: Zoom",
            "G: Toggle Grid",
            f"Zoom: {self.zoom}x"
        ]

        for control in controls:
            text = self.font.render(control, True, TEXT_COLOR)
            self.screen.blit(text, (10, y_offset))
            y_offset += 20

    def draw_tile_options(self, y_offset):
        """Draw tile selection options"""
        start_y = y_offset

        for tile_type, color in TILE_COLORS.items():
            if tile_type in ['house', 'bank', 'building', 'skyscraper', 'store']:
                continue  # Skip building tiles

            # Tile preview
            rect = pygame.Rect(10, y_offset, 30, 30)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, SELECTED_COLOR if self.selected_tile == tile_type else GRID_COLOR, rect, 2)

            # Tile name
            text = self.font.render(tile_type.title(), True, TEXT_COLOR)
            self.screen.blit(text, (50, y_offset + 5))

            y_offset += 35

        # Update max scroll
        self.max_sidebar_scroll = max(0, y_offset - start_y - (SCREEN_HEIGHT - 200))

    def draw_building_options(self, y_offset):
        """Draw building selection options"""
        start_y = y_offset

        for building_name, building_data in self.buildings.items():
            # Building info
            width, height = building_data['size']
            category = building_data['category']
            color = TILE_COLORS.get(category, TILE_COLORS['building'])

            # Selection rectangle
            rect = pygame.Rect(10, y_offset, SIDEBAR_WIDTH - 20, 40)
            is_selected = self.selected_building == building_name
            pygame.draw.rect(self.screen, BUTTON_ACTIVE_COLOR if is_selected else BUTTON_COLOR, rect)

            # Building preview
            preview_rect = pygame.Rect(15, y_offset + 5, 30, 30)
            pygame.draw.rect(self.screen, color, preview_rect)

            # Building name and size
            name_text = self.font.render(building_name, True, TEXT_COLOR)
            self.screen.blit(name_text, (55, y_offset + 5))
            size_text = self.font.render(f"{width}x{height}", True, TEXT_COLOR)
            self.screen.blit(size_text, (55, y_offset + 20))

            y_offset += 45

        # Update max scroll
        self.max_sidebar_scroll = max(0, y_offset - start_y - (SCREEN_HEIGHT - 200))

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.unsaved_changes:
                    # In a real app, you'd show a dialog here
                    self.save_map()
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.save_map()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_SPACE:
                    self.space_dragging = True
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.drag_start_x = mouse_x
                    self.drag_start_y = mouse_y
                elif event.key == pygame.K_ESCAPE:
                    return False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_dragging = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if event.button == 1:  # Left click
                    if mouse_x < SIDEBAR_WIDTH:
                        self.handle_sidebar_click(mouse_x, mouse_y)
                    else:
                        self.mouse_dragging = True
                        self.handle_map_click(mouse_x, mouse_y)

                elif event.button == 4:  # Scroll up
                    if mouse_x < SIDEBAR_WIDTH:
                        self.sidebar_scroll = max(0, self.sidebar_scroll - 20)
                    else:
                        self.zoom = min(8, self.zoom + 1)

                elif event.button == 5:  # Scroll down
                    if mouse_x < SIDEBAR_WIDTH:
                        self.sidebar_scroll = min(self.max_sidebar_scroll, self.sidebar_scroll + 20)
                    else:
                        self.zoom = max(1, self.zoom - 1)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Update building preview position
                if self.current_tool == ToolType.BUILDING:
                    world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
                    if world_x is not None:
                        self.preview_x = world_x
                        self.preview_y = world_y

                # Handle dragging
                if self.space_dragging:
                    dx = mouse_x - self.drag_start_x
                    dy = mouse_y - self.drag_start_y
                    self.camera_x -= dx / (self.zoom * TILE_SIZE)
                    self.camera_y -= dy / (self.zoom * TILE_SIZE)
                    self.drag_start_x = mouse_x
                    self.drag_start_y = mouse_y
                elif self.mouse_dragging and mouse_x >= SIDEBAR_WIDTH:
                    self.handle_map_click(mouse_x, mouse_y)

        return True

    def handle_sidebar_click(self, x, y):
        """Handle clicks in the sidebar"""
        # Save button
        if 10 <= x <= SIDEBAR_WIDTH - 10 and 50 <= y <= 80:
            self.save_map()
            return

        # Tool buttons
        tool_y = 90
        tools = [ToolType.TILE, ToolType.BUILDING, ToolType.ERASER]
        for tool in tools:
            if 10 <= x <= SIDEBAR_WIDTH - 10 and tool_y <= y <= tool_y + 30:
                self.current_tool = tool
                return
            tool_y += 35

        # Tile/Building selection (with scrolling)
        content_y = 180 - self.sidebar_scroll

        if self.current_tool == ToolType.TILE:
            for tile_type in TILE_COLORS:
                if tile_type in ['house', 'bank', 'building', 'skyscraper', 'store']:
                    continue
                if 10 <= x <= SIDEBAR_WIDTH - 10 and content_y <= y <= content_y + 30:
                    self.selected_tile = tile_type
                    return
                content_y += 35

        elif self.current_tool == ToolType.BUILDING:
            for building_name in self.buildings:
                if 10 <= x <= SIDEBAR_WIDTH - 10 and content_y <= y <= content_y + 40:
                    self.selected_building = building_name
                    return
                content_y += 45

    def handle_map_click(self, screen_x, screen_y):
        """Handle clicks on the map"""
        world_x, world_y = self.screen_to_world(screen_x, screen_y)
        if world_x is None:
            return

        if self.current_tool == ToolType.TILE:
            color = TILE_COLORS[self.selected_tile]
            self.map_surface.set_at((world_x, world_y), color)
            self.unsaved_changes = True

        elif self.current_tool == ToolType.BUILDING:
            self.place_building(world_x, world_y)

        elif self.current_tool == ToolType.ERASER:
            # Erase to dirt
            self.map_surface.set_at((world_x, world_y), TILE_COLORS['dirt'])
            self.unsaved_changes = True

    def run(self):
        """Main editor loop"""
        running = True

        while running:
            # Handle events
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
    editor = MapEditor()
    editor.run()
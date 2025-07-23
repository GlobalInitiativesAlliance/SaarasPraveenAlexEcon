import pygame
import random
import json
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
FPS = 60
UI_HEIGHT = 60  # Reduced UI height

# Colors
BACKGROUND_COLOR = (50, 50, 50)
GRID_COLOR = (70, 70, 70)
UI_BACKGROUND = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)
PLAYER_COLOR = (255, 0, 0)  # Red player icon


class TileManager:
    def __init__(self):
        self.sheets = {}
        self.tile_cache = {}
        self.tile_data = None
        self.building_data = None
        self.load_tile_selections()
        self.load_sheets()
        self.analyze_grass_tiles()

    def load_tile_selections(self):
        """Load tile selections from JSON file"""
        try:
            with open("tile_selections.json", "r") as f:
                data = json.load(f)
                self.tile_data = data.get('tiles', {})
                self.building_data = data.get('buildings', {})
                print(f"Loaded {sum(len(tiles) for tiles in self.tile_data.values())} tiles")
                print(f"Loaded {len(self.building_data)} building definitions")

                # Print grass tiles for debugging
                if 'grass' in self.tile_data:
                    print(f"Grass tiles: {len(self.tile_data['grass'])} tiles loaded")
                    for tile in self.tile_data['grass']:
                        print(f"  - Position: ({tile[1]}, {tile[2]})")
        except FileNotFoundError:
            print("tile_selections.json not found! Please run the tile picker first.")
            self.tile_data = {}
            self.building_data = {}

    def analyze_grass_tiles(self):
        """Analyze grass tiles to determine their types (corner, edge, center)"""
        self.grass_tile_types = {
            'center': None,
            'edges': {},
            'corners': {},
            'inner_corners': {}
        }

        if 'grass' not in self.tile_data or not self.tile_data['grass']:
            print("No grass tiles found!")
            return

        grass_tiles = self.tile_data['grass']
        print(f"\nAnalyzing {len(grass_tiles)} grass tiles...")

        # Based on the 3x3 pattern in your tileset:
        # The tiles represent how grass (green) transitions to dirt (brown/sand)
        # Looking at typical autotile patterns:

        for tile in grass_tiles:
            x, y = tile[1], tile[2]

            # Center tile (16, 50) - full grass, no dirt
            if x == 16 and y == 50:
                self.grass_tile_types['center'] = tile
                print(f"  -> Center (full grass): ({x}, {y})")

            # Edge tiles - grass with dirt on one side
            # These show where grass meets dirt in cardinal directions
            elif x == 14 and y == 50:
                self.grass_tile_types['edges']['left'] = tile
                print(f"  -> Left edge: ({x}, {y})")
            elif x == 18 and y == 50:
                self.grass_tile_types['edges']['right'] = tile
                print(f"  -> Right edge: ({x}, {y})")
            elif x == 16 and y == 48:
                self.grass_tile_types['edges']['top'] = tile
                print(f"  -> Top edge: ({x}, {y})")
            elif x == 16 and y == 52:
                self.grass_tile_types['edges']['bottom'] = tile
                print(f"  -> Bottom edge: ({x}, {y})")

            # Outer corners - grass in one corner, dirt elsewhere
            elif x == 14 and y == 48:
                self.grass_tile_types['corners']['top_left'] = tile
                print(f"  -> Top-left corner: ({x}, {y})")
            elif x == 18 and y == 48:
                self.grass_tile_types['corners']['top_right'] = tile
                print(f"  -> Top-right corner: ({x}, {y})")
            elif x == 14 and y == 52:
                self.grass_tile_types['corners']['bottom_left'] = tile
                print(f"  -> Bottom-left corner: ({x}, {y})")
            elif x == 18 and y == 52:
                self.grass_tile_types['corners']['bottom_right'] = tile
                print(f"  -> Bottom-right corner: ({x}, {y})")

        # If we don't have a center tile, use the first available grass tile
        if not self.grass_tile_types['center'] and grass_tiles:
            self.grass_tile_types['center'] = grass_tiles[0]
            print(f"  -> No center tile found, using first tile as default")

        print("\nGrass tile analysis complete:")
        print(f"  Center: {self.grass_tile_types['center'] is not None}")
        print(f"  Edges: {list(self.grass_tile_types['edges'].keys())}")
        print(f"  Corners: {list(self.grass_tile_types['corners'].keys())}")

    def load_sheets(self):
        """Load sprite sheets"""
        base_dir = os.path.dirname(__file__)

        # Define sheet paths
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
                # Create placeholder surface
                self.sheets[sheet_name] = pygame.Surface((256, 256))
                self.sheets[sheet_name].fill((255, 0, 255))

    def get_tile(self, sheet_name, x, y):
        """Get a tile from cache or create it"""
        cache_key = (sheet_name, x, y)

        if cache_key in self.tile_cache:
            return self.tile_cache[cache_key]

        if sheet_name not in self.sheets:
            return None

        sheet = self.sheets[sheet_name]
        src_rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                               ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)

        try:
            tile_surface = sheet.subsurface(src_rect)
            scaled_tile = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
            self.tile_cache[cache_key] = scaled_tile
            return scaled_tile
        except ValueError:
            return None

    def get_random_tile(self, category):
        """Get a random tile from a category"""
        if category not in self.tile_data or not self.tile_data[category]:
            return None

        tile_info = random.choice(self.tile_data[category])
        return self.get_tile(tile_info[0], tile_info[1], tile_info[2])

    def get_grass_tile_for_position(self, map_data, x, y):
        """Get appropriate grass tile based on neighboring tiles"""
        if 'grass' not in self.tile_data or not self.tile_data['grass']:
            return None

        # Check all 8 neighbors - but treat buildings as non-grass
        neighbors = {
            'top': y > 0 and self.is_grass_tile(map_data[y - 1][x]),
            'bottom': y < len(map_data) - 1 and self.is_grass_tile(map_data[y + 1][x]),
            'left': x > 0 and self.is_grass_tile(map_data[y][x - 1]),
            'right': x < len(map_data[0]) - 1 and self.is_grass_tile(map_data[y][x + 1]),
            'top_left': y > 0 and x > 0 and self.is_grass_tile(map_data[y - 1][x - 1]),
            'top_right': y > 0 and x < len(map_data[0]) - 1 and self.is_grass_tile(map_data[y - 1][x + 1]),
            'bottom_left': y < len(map_data) - 1 and x > 0 and self.is_grass_tile(map_data[y + 1][x - 1]),
            'bottom_right': y < len(map_data) - 1 and x < len(map_data[0]) - 1 and self.is_grass_tile(
                map_data[y + 1][x + 1])
        }

        # Count orthogonal neighbors
        orthogonal_count = sum([neighbors['top'], neighbors['bottom'], neighbors['left'], neighbors['right']])

        # Determine which tile to use based on neighbors
        tile_info = None

        # All neighbors are grass = use center tile (full grass)
        if orthogonal_count == 4:
            tile_info = self.grass_tile_types['center']

        # Single tile or peninsula (1 or 0 orthogonal neighbors)
        elif orthogonal_count <= 1:
            # Isolated grass tile or end of peninsula - use center
            tile_info = self.grass_tile_types['center']

        # Corners - exactly 2 orthogonal neighbors at 90 degrees
        # These are OUTER corners where grass is surrounded by dirt
        elif orthogonal_count == 2:
            # Check which two sides have grass to determine corner orientation
            if neighbors['bottom'] and neighbors['right'] and not neighbors['top'] and not neighbors['left']:
                # Grass extends down and right = top-left corner piece
                tile_info = self.grass_tile_types['corners'].get('top_left')
            elif neighbors['bottom'] and neighbors['left'] and not neighbors['top'] and not neighbors['right']:
                # Grass extends down and left = top-right corner piece
                tile_info = self.grass_tile_types['corners'].get('top_right')
            elif neighbors['top'] and neighbors['right'] and not neighbors['bottom'] and not neighbors['left']:
                # Grass extends up and right = bottom-left corner piece
                tile_info = self.grass_tile_types['corners'].get('bottom_left')
            elif neighbors['top'] and neighbors['left'] and not neighbors['bottom'] and not neighbors['right']:
                # Grass extends up and left = bottom-right corner piece
                tile_info = self.grass_tile_types['corners'].get('bottom_right')
            # Straight sections (opposite neighbors)
            elif neighbors['top'] and neighbors['bottom']:
                tile_info = self.grass_tile_types['center']
            elif neighbors['left'] and neighbors['right']:
                tile_info = self.grass_tile_types['center']

        # Edges - exactly 3 orthogonal neighbors
        elif orthogonal_count == 3:
            # The edge tiles show the transition on the side WITHOUT grass
            if not neighbors['top']:
                tile_info = self.grass_tile_types['edges'].get('top')
            elif not neighbors['bottom']:
                tile_info = self.grass_tile_types['edges'].get('bottom')
            elif not neighbors['left']:
                tile_info = self.grass_tile_types['edges'].get('left')
            elif not neighbors['right']:
                tile_info = self.grass_tile_types['edges'].get('right')

        # Default to center tile if no specific case matches
        if not tile_info:
            tile_info = self.grass_tile_types['center']

        # If we still don't have a tile, use the first grass tile
        if not tile_info and self.tile_data['grass']:
            tile_info = self.tile_data['grass'][0]

        if tile_info:
            return self.get_tile(tile_info[0], tile_info[1], tile_info[2])
        return None

    def is_grass_tile(self, tile_data):
        """Check if a tile is grass (not a building or other type)"""
        if isinstance(tile_data, tuple):
            return False  # Buildings are stored as tuples
        return tile_data == 'grass'


class CityMap:
    def __init__(self):
        # First load a dummy map to get dimensions
        self.load_map_dimensions()
        self.map_data = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.tile_manager = None  # Will be set by Game class
        self.building_tiles = set()
        self.load_from_image()

    def load_map_dimensions(self):
        """Load map dimensions from the PNG file"""
        try:
            city_map_path = os.path.join(os.path.dirname(__file__), "city_map.png")
            map_image = pygame.image.load(city_map_path)
            img_width, img_height = map_image.get_size()

            # Set map dimensions based on image
            # Each pixel in the image represents one tile
            self.width = img_width
            self.height = img_height

            print(f"Map dimensions set to {self.width}x{self.height} from image")
        except Exception as e:
            print(f"Failed to load city_map.png for dimensions: {e}")
            # Fallback dimensions
            self.width = 50
            self.height = 40

    def load_from_image(self):
        """Load city layout from city_map.png"""
        try:
            # Load the city map image
            city_map_path = os.path.join(os.path.dirname(__file__), "city_map.png")
            map_image = pygame.image.load(city_map_path)

            # Get image dimensions
            img_width, img_height = map_image.get_size()

            print(f"Loading map from city_map.png: {img_width}x{img_height} pixels")

            # Define color mappings to match map_generator.py
            COLOR_TO_TILE = {
                # Natural terrain
                (34, 139, 34): 'grass',  # Forest green
                (0, 100, 0): 'tree',  # Dark green
                (128, 128, 128): 'rock',  # Gray
                (0, 119, 190): 'water',  # Blue
                (238, 203, 173): 'sand',  # Sandy beige
                (139, 69, 19): 'dirt',  # Brown
                (0, 80, 150): 'deep_water',  # Deep blue

                # Buildings - these will be handled separately
                (139, 90, 43): 'house',  # Brown house
                (192, 192, 192): 'bank',  # Silver/light gray
                (105, 105, 105): 'building',  # Dark gray office
                (70, 130, 180): 'skyscraper',  # Steel blue
                (255, 140, 0): 'store',  # Dark orange

                # Roads and urban
                (32, 32, 32): 'road',  # Asphalt black
                (190, 190, 190): 'sidewalk',  # Light gray concrete
            }

            # Building colors for easy lookup
            BUILDING_COLORS = {
                (139, 90, 43): 'house',
                (192, 192, 192): 'bank',
                (105, 105, 105): 'building',
                (70, 130, 180): 'skyscraper',
                (255, 140, 0): 'store',
            }

            # Initialize all tiles as dirt first
            for y in range(self.height):
                for x in range(self.width):
                    if y < len(self.map_data) and x < len(self.map_data[y]):
                        self.map_data[y][x] = 'dirt'

            # Read pixels directly - 1 pixel = 1 tile
            grass_count = 0
            building_count = 0

            # Track which tiles are part of buildings (to avoid overlaps)
            self.building_tiles = set()

            # First pass: identify all tiles
            for y in range(min(self.height, img_height)):
                for x in range(min(self.width, img_width)):
                    # Skip if this tile is already part of a building
                    if (x, y) in self.building_tiles:
                        continue

                    # Get pixel color
                    color = map_image.get_at((x, y))
                    color_tuple = (color.r, color.g, color.b)

                    # Check if it's a building color
                    if color_tuple in BUILDING_COLORS:
                        # Try to place a building starting from this position
                        building_type = BUILDING_COLORS[color_tuple]
                        if self.try_place_building_by_type(x, y, building_type, map_image, BUILDING_COLORS):
                            building_count += 1
                    else:
                        # Find closest matching color
                        tile_type = 'dirt'  # default
                        min_distance = float('inf')

                        for ref_color, ref_type in COLOR_TO_TILE.items():
                            # Calculate color distance
                            dist = sum((c1 - c2) ** 2 for c1, c2 in zip(color_tuple, ref_color))
                            if dist < min_distance:
                                min_distance = dist
                                tile_type = ref_type

                        # Apply the tile type
                        self.map_data[y][x] = tile_type

                        if tile_type == 'grass':
                            grass_count += 1

            print(f"Map loaded with {grass_count} grass tiles and {building_count} buildings")

        except Exception as e:
            print(f"Failed to load city_map.png: {e}")
            print("Please ensure city_map.png is in the same directory as this script")

    def try_place_building_by_type(self, start_x, start_y, building_type, map_image, building_colors):
        """Try to place a specific building type at the given position"""
        # Check if we have building data
        if not hasattr(self, 'tile_manager') or not self.tile_manager:
            return False

        building_data = self.tile_manager.building_data
        if not building_data:
            return False

        # Find the right building in our data
        building_key = None
        for key, data in building_data.items():
            if building_type in key.lower():
                building_key = key
                break

        if not building_key:
            print(f"Warning: No building data found for type '{building_type}'")
            return False

        building = building_data[building_key]
        width, height = building['size']

        # Check if building fits
        if start_x + width > self.width or start_y + height > self.height:
            return False

        # Verify all tiles of the building have the same color
        expected_color = None
        for color_tuple, b_type in building_colors.items():
            if b_type == building_type:
                expected_color = color_tuple
                break

        if not expected_color:
            return False

        # Check if all tiles in the building area have the correct color
        img_width, img_height = map_image.get_size()
        for dy in range(height):
            for dx in range(width):
                px = start_x + dx
                py = start_y + dy

                if px >= img_width or py >= img_height:
                    return False

                color = map_image.get_at((px, py))
                if (color.r, color.g, color.b) != expected_color:
                    return False

        # Mark all tiles as building tiles
        for dy in range(height):
            for dx in range(width):
                self.building_tiles.add((start_x + dx, start_y + dy))
                self.map_data[start_y + dy][start_x + dx] = ('building', building_key, dx, dy)

        print(f"Placed {building_key} at ({start_x}, {start_y})")
        return True

    def smooth_map(self):
        """Smooth the map to remove isolated tiles"""
        temp_map = [row[:] for row in self.map_data]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                tile_type = self.map_data[y][x]

                # Count neighbors of the same type
                same_neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        if self.map_data[y + dy][x + dx] == tile_type:
                            same_neighbors += 1

                # Remove isolated tiles
                if same_neighbors <= 2:
                    # Change isolated grass to dirt
                    if tile_type == 'grass':
                        temp_map[y][x] = 'dirt'

                # Fill in gaps
                elif tile_type == 'dirt':
                    grass_neighbors = sum(1 for dy in [-1, 0, 1] for dx in [-1, 0, 1]
                                          if (dx != 0 or dy != 0) and
                                          self.map_data[y + dy][x + dx] == 'grass')
                    if grass_neighbors >= 6:
                        temp_map[y][x] = 'grass'

        self.map_data = temp_map


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Builder - Tile Based")
        self.clock = pygame.time.Clock()

        # Initialize components
        self.tile_manager = TileManager()
        self.city_map = CityMap()
        self.city_map.tile_manager = self.tile_manager  # Pass tile manager to city map
        self.city_map.load_from_image()  # Reload with tile manager available

        # Player position (in tile coordinates)
        self.player_x = self.city_map.width // 2
        self.player_y = self.city_map.height // 2

        # Camera - centered on player initially
        self.camera_x = 0
        self.camera_y = 0
        self.update_camera()

        # UI
        self.font = pygame.font.Font(None, 20)  # Smaller font
        self.show_grid = True

        # Pre-render the map
        self.render_map_cache()

    def update_camera(self):
        """Update camera to follow player"""
        # Center camera on player
        self.camera_x = self.player_x * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.player_y * TILE_SIZE - (SCREEN_HEIGHT - UI_HEIGHT) // 2 + TILE_SIZE // 2

        # Clamp camera to map bounds
        max_camera_x = self.city_map.width * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = self.city_map.height * TILE_SIZE - (SCREEN_HEIGHT - UI_HEIGHT)

        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def render_map_cache(self):
        """Pre-render grass tiles with proper edges and buildings"""
        self.map_cache = {}

        for y in range(self.city_map.height):
            for x in range(self.city_map.width):
                tile_data = self.city_map.map_data[y][x]

                # Handle building tiles
                if isinstance(tile_data, tuple) and tile_data[0] == 'building':
                    _, building_key, offset_x, offset_y = tile_data
                    building = self.tile_manager.building_data.get(building_key)

                    if building and offset_y < len(building['tiles']) and offset_x < len(building['tiles'][offset_y]):
                        tile_info = building['tiles'][offset_y][offset_x]
                        tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                        if tile:
                            self.map_cache[(x, y)] = ('building', tile)

                # Handle regular tiles
                elif tile_data == 'grass':
                    # Get appropriate grass tile based on neighbors
                    tile = self.tile_manager.get_grass_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('grass', tile)
                elif tile_data == 'road':
                    tile = self.tile_manager.get_random_tile('road')
                    if tile:
                        self.map_cache[(x, y)] = ('road', tile)
                elif tile_data == 'sidewalk':
                    # Use a light gray color for concrete/sidewalk
                    self.map_cache[(x, y)] = ('concrete', None)
                else:
                    # For dirt/sand background
                    self.map_cache[(x, y)] = ('dirt', None)

    def handle_input(self):
        """Handle user input"""
        keys = pygame.key.get_pressed()

        # Player movement
        old_x, old_y = self.player_x, self.player_y

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.player_x > 0:
                self.player_x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.player_x < self.city_map.width - 1:
                self.player_x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.player_y > 0:
                self.player_y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if self.player_y < self.city_map.height - 1:
                self.player_y += 1

        # Update camera if player moved
        if self.player_x != old_x or self.player_y != old_y:
            self.update_camera()

    def draw(self):
        """Draw everything"""
        self.screen.fill(BACKGROUND_COLOR)

        # Calculate visible tile range
        start_x = max(0, self.camera_x // TILE_SIZE)
        end_x = min((self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 2, self.city_map.width)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_y = min((self.camera_y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE + 2, self.city_map.height)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y

                # Get cached tile
                if (x, y) in self.map_cache:
                    tile_type, tile_surface = self.map_cache[(x, y)]

                    if tile_type == 'dirt':
                        # Draw brown background for dirt
                        pygame.draw.rect(self.screen, (139, 90, 43),
                                         (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile_type == 'concrete':
                        # Draw light gray for concrete/sidewalk
                        pygame.draw.rect(self.screen, (180, 180, 180),
                                         (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile_surface:
                        self.screen.blit(tile_surface, (screen_x, screen_y))

                # Draw grid
                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Draw player
        player_screen_x = self.player_x * TILE_SIZE - self.camera_x
        player_screen_y = self.player_y * TILE_SIZE - self.camera_y

        # Draw player as a circle in the center of the tile
        pygame.draw.circle(self.screen, PLAYER_COLOR,
                           (player_screen_x + TILE_SIZE // 2, player_screen_y + TILE_SIZE // 2),
                           TILE_SIZE // 3)
        # Add a white outline for visibility
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (player_screen_x + TILE_SIZE // 2, player_screen_y + TILE_SIZE // 2),
                           TILE_SIZE // 3, 2)

        # Draw UI
        self.draw_ui()

    def draw_ui(self):
        """Draw user interface"""
        # Bottom panel
        pygame.draw.rect(self.screen, UI_BACKGROUND,
                         (0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))

        # Info text
        info_texts = [
            f"Player: ({self.player_x}, {self.player_y}) | Camera: ({self.camera_x}, {self.camera_y})",
            f"Map: {self.city_map.width}x{self.city_map.height} | WASD to move, G for grid, R to reload, ESC to exit"
        ]

        y_offset = SCREEN_HEIGHT - UI_HEIGHT + 10
        for text in info_texts:
            rendered = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(rendered, (10, y_offset))
            y_offset += 25

    def run(self):
        """Main game loop"""
        running = True
        move_delay = 0
        MOVE_SPEED = 100  # milliseconds between moves when holding key

        while running:
            dt = self.clock.tick(FPS)
            move_delay = max(0, move_delay - dt)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_r:
                        # Reload from image
                        self.city_map.load_from_image()
                        self.render_map_cache()

            # Handle continuous movement with delay
            if move_delay == 0:
                self.handle_input()
                keys = pygame.key.get_pressed()
                if any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
                        keys[pygame.K_UP], keys[pygame.K_DOWN],
                        keys[pygame.K_a], keys[pygame.K_d],
                        keys[pygame.K_w], keys[pygame.K_s]]):
                    move_delay = MOVE_SPEED

            # Draw
            self.draw()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
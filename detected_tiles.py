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


class AnimatedPlayer:
    def __init__(self, x, y, tile_size):
        self.x = x  # Tile position
        self.y = y
        self.tile_size = tile_size

        # Player display size (make it larger than tile)
        self.display_size = int(tile_size * 1.5)  # 1.5x larger than tile

        # Pixel position for smooth movement
        self.pixel_x = x * tile_size
        self.pixel_y = y * tile_size
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        # Movement
        self.moving = False
        self.move_speed = 4  # Pixels per frame
        self.direction = 'down'  # 'up', 'down', 'left', 'right'

        # Animation
        self.animations = {}
        self.current_animation = 'idle_down'
        self.animation_frame = 0
        self.animation_speed = 0.15  # How fast to cycle frames
        self.animation_timer = 0

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load all character animations"""
        sprite_dir = os.path.join(os.path.dirname(__file__), 'sprites', 'player')

        # Define which files belong to which animations
        # You'll need to adjust these based on your actual file names
        animation_files = {
            'idle_down': ['idle_front.png'],
            'idle_up': ['idle_back.png'],
            'idle_left': ['idle_left.png'],
            'idle_right': ['idle_right.png'],
            'walk_down': ['walk_front_1.png', 'walk_front_2.png'],
            'walk_up': ['walk_back_1.png', 'walk_back_2.png'],
            'walk_left': ['idle_left.png'],
            'walk_right': ['idle_right.png']
        }

        # Load each animation
        for anim_name, files in animation_files.items():
            self.animations[anim_name] = []
            for file in files:
                path = os.path.join(sprite_dir, file)
                try:
                    # Load and scale the image
                    img = pygame.image.load(path)
                    # Scale to display size (larger than tile)
                    img = pygame.transform.scale(img, (self.display_size, self.display_size))
                    self.animations[anim_name].append(img)
                except:
                    print(f"Warning: Could not load {path}")
                    # Create placeholder if file missing
                    placeholder = pygame.Surface((self.display_size, self.display_size))
                    placeholder.fill((255, 0, 255))  # Magenta for missing sprites
                    self.animations[anim_name].append(placeholder)

        # Fallback if no animations loaded
        if not any(self.animations.values()):
            print("No animations loaded, using placeholder")
            placeholder = pygame.Surface((self.display_size, self.display_size))
            placeholder.fill((255, 0, 0))
            self.animations['idle_down'] = [placeholder]

    def move_to(self, new_x, new_y):
        """Start moving to a new tile position"""
        if self.moving:
            return False  # Already moving

        # Set new target position
        self.x = new_x
        self.y = new_y
        self.target_x = new_x * self.tile_size
        self.target_y = new_y * self.tile_size

        # Determine direction
        dx = self.target_x - self.pixel_x
        dy = self.target_y - self.pixel_y

        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'

        self.moving = True
        self.set_animation(f'walk_{self.direction}')
        return True

    def set_animation(self, anim_name):
        """Change current animation"""
        if anim_name != self.current_animation and anim_name in self.animations:
            self.current_animation = anim_name
            self.animation_frame = 0
            self.animation_timer = 0

    def update(self, dt):
        """Update player position and animation"""
        # Update movement
        if self.moving:
            # Move towards target
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y

            # Move in x direction
            if abs(dx) > self.move_speed:
                self.pixel_x += self.move_speed if dx > 0 else -self.move_speed
            else:
                self.pixel_x = self.target_x

            # Move in y direction
            if abs(dy) > self.move_speed:
                self.pixel_y += self.move_speed if dy > 0 else -self.move_speed
            else:
                self.pixel_y = self.target_y

            # Check if reached target
            if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
                self.moving = False
                self.set_animation(f'idle_{self.direction}')

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            current_anim = self.animations.get(self.current_animation, [])
            if current_anim:
                self.animation_frame = (self.animation_frame + 1) % len(current_anim)

    def draw(self, screen, camera_x, camera_y):
        """Draw the player"""
        # Calculate screen position (centered on tile)
        screen_x = self.pixel_x - camera_x - (self.display_size - self.tile_size) // 2
        screen_y = self.pixel_y - camera_y - (self.display_size - self.tile_size) // 2

        # Get current frame
        current_anim = self.animations.get(self.current_animation)
        if current_anim and current_anim[self.animation_frame]:
            screen.blit(current_anim[self.animation_frame], (screen_x, screen_y))
        else:
            # Fallback circle if no sprite (also larger)
            pygame.draw.circle(screen, (255, 0, 0),
                               (int(self.pixel_x - camera_x + self.tile_size // 2),
                                int(self.pixel_y - camera_y + self.tile_size // 2)),
                               self.display_size // 3)


class TileManager:
    def __init__(self):
        self.sheets = {}
        self.tile_cache = {}
        self.tile_data = None
        self.building_data = None
        self.load_tile_selections()
        self.load_sheets()
        self.analyze_grass_tiles()
        self.analyze_sidewalk_tiles()

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

                # Print sidewalk tiles for debugging
                if 'sidewalk' in self.tile_data:
                    print(f"Sidewalk tiles: {len(self.tile_data['sidewalk'])} tiles loaded")
                    for tile in self.tile_data['sidewalk']:
                        print(f"  - Sidewalk Position: ({tile[1]}, {tile[2]})")
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

    def analyze_sidewalk_tiles(self):
        """Analyze sidewalk tiles to determine their types (corner, edge, center)"""
        self.sidewalk_tile_types = {
            'center': None,
            'edges': {},
            'corners': {},
            'inner_corners': {}
        }

        if 'sidewalk' not in self.tile_data or not self.tile_data['sidewalk']:
            print("No sidewalk tiles found!")
            return

        sidewalk_tiles = self.tile_data['sidewalk']
        print(f"\nAnalyzing {len(sidewalk_tiles)} sidewalk tiles...")

        # Based on your tile data, sidewalk tiles are in a 4x4 grid from (13,38) to (19,44)
        # The pattern typically follows:
        # - Center tiles: full sidewalk
        # - Edge tiles: sidewalk meeting road/dirt on one side
        # - Corner tiles: sidewalk in corner configurations

        for tile in sidewalk_tiles:
            x, y = tile[1], tile[2]

            # Center tiles - these appear to be the main body tiles
            if (x, y) in [(15, 40), (17, 40), (15, 42), (17, 42)]:
                if not self.sidewalk_tile_types['center']:
                    self.sidewalk_tile_types['center'] = tile
                print(f"  -> Center sidewalk: ({x}, {y})")

            # Edge tiles
            elif x == 13 and y in [40, 41, 42]:  # Left edge
                self.sidewalk_tile_types['edges']['left'] = tile
                print(f"  -> Left edge: ({x}, {y})")
            elif x == 19 and y in [40, 41, 42]:  # Right edge
                self.sidewalk_tile_types['edges']['right'] = tile
                print(f"  -> Right edge: ({x}, {y})")
            elif y == 38 and x in [15, 16, 17]:  # Top edge
                self.sidewalk_tile_types['edges']['top'] = tile
                print(f"  -> Top edge: ({x}, {y})")
            elif y == 44 and x in [15, 16, 17]:  # Bottom edge
                self.sidewalk_tile_types['edges']['bottom'] = tile
                print(f"  -> Bottom edge: ({x}, {y})")

            # Corner tiles
            elif x == 13 and y == 38:  # Top-left
                self.sidewalk_tile_types['corners']['top_left'] = tile
                print(f"  -> Top-left corner: ({x}, {y})")
            elif x == 19 and y == 38:  # Top-right
                self.sidewalk_tile_types['corners']['top_right'] = tile
                print(f"  -> Top-right corner: ({x}, {y})")
            elif x == 13 and y == 44:  # Bottom-left
                self.sidewalk_tile_types['corners']['bottom_left'] = tile
                print(f"  -> Bottom-left corner: ({x}, {y})")
            elif x == 19 and y == 44:  # Bottom-right
                self.sidewalk_tile_types['corners']['bottom_right'] = tile
                print(f"  -> Bottom-right corner: ({x}, {y})")

        # If we don't have a center tile, use the first available sidewalk tile
        if not self.sidewalk_tile_types['center'] and sidewalk_tiles:
            self.sidewalk_tile_types['center'] = sidewalk_tiles[0]
            print(f"  -> No center tile found, using first tile as default")

        print("\nSidewalk tile analysis complete:")
        print(f"  Center: {self.sidewalk_tile_types['center'] is not None}")
        print(f"  Edges: {list(self.sidewalk_tile_types['edges'].keys())}")
        print(f"  Corners: {list(self.sidewalk_tile_types['corners'].keys())}")

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

    def get_sidewalk_tile_for_position(self, map_data, x, y):
        """Get appropriate sidewalk tile based on neighboring tiles"""
        if 'sidewalk' not in self.tile_data or not self.tile_data['sidewalk']:
            return None

        # Check all 8 neighbors
        neighbors = {
            'top': y > 0 and self.is_sidewalk_tile(map_data[y - 1][x]),
            'bottom': y < len(map_data) - 1 and self.is_sidewalk_tile(map_data[y + 1][x]),
            'left': x > 0 and self.is_sidewalk_tile(map_data[y][x - 1]),
            'right': x < len(map_data[0]) - 1 and self.is_sidewalk_tile(map_data[y][x + 1]),
            'top_left': y > 0 and x > 0 and self.is_sidewalk_tile(map_data[y - 1][x - 1]),
            'top_right': y > 0 and x < len(map_data[0]) - 1 and self.is_sidewalk_tile(map_data[y - 1][x + 1]),
            'bottom_left': y < len(map_data) - 1 and x > 0 and self.is_sidewalk_tile(map_data[y + 1][x - 1]),
            'bottom_right': y < len(map_data) - 1 and x < len(map_data[0]) - 1 and self.is_sidewalk_tile(
                map_data[y + 1][x + 1])
        }

        # Count orthogonal neighbors
        orthogonal_count = sum([neighbors['top'], neighbors['bottom'], neighbors['left'], neighbors['right']])

        # Determine which tile to use based on neighbors
        tile_info = None

        # All neighbors are sidewalk = use center tile
        if orthogonal_count == 4:
            tile_info = self.sidewalk_tile_types['center']

        # Single tile or peninsula (1 or 0 orthogonal neighbors)
        elif orthogonal_count <= 1:
            # Isolated sidewalk tile - use center
            tile_info = self.sidewalk_tile_types['center']

        # Corners - exactly 2 orthogonal neighbors at 90 degrees
        elif orthogonal_count == 2:
            # Check which two sides have sidewalk to determine corner orientation
            if neighbors['bottom'] and neighbors['right'] and not neighbors['top'] and not neighbors['left']:
                # Sidewalk extends down and right = top-left corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('top_left')
            elif neighbors['bottom'] and neighbors['left'] and not neighbors['top'] and not neighbors['right']:
                # Sidewalk extends down and left = top-right corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('top_right')
            elif neighbors['top'] and neighbors['right'] and not neighbors['bottom'] and not neighbors['left']:
                # Sidewalk extends up and right = bottom-left corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('bottom_left')
            elif neighbors['top'] and neighbors['left'] and not neighbors['bottom'] and not neighbors['right']:
                # Sidewalk extends up and left = bottom-right corner piece
                tile_info = self.sidewalk_tile_types['corners'].get('bottom_right')
            # Straight sections (opposite neighbors)
            elif neighbors['top'] and neighbors['bottom']:
                tile_info = self.sidewalk_tile_types['center']
            elif neighbors['left'] and neighbors['right']:
                tile_info = self.sidewalk_tile_types['center']

        # Edges - exactly 3 orthogonal neighbors
        elif orthogonal_count == 3:
            # The edge tiles show the transition on the side WITHOUT sidewalk
            if not neighbors['top']:
                tile_info = self.sidewalk_tile_types['edges'].get('top')
            elif not neighbors['bottom']:
                tile_info = self.sidewalk_tile_types['edges'].get('bottom')
            elif not neighbors['left']:
                tile_info = self.sidewalk_tile_types['edges'].get('left')
            elif not neighbors['right']:
                tile_info = self.sidewalk_tile_types['edges'].get('right')

        # Default to center tile if no specific case matches
        if not tile_info:
            tile_info = self.sidewalk_tile_types['center']

        # If we still don't have a tile, use the first sidewalk tile
        if not tile_info and self.tile_data['sidewalk']:
            tile_info = self.tile_data['sidewalk'][0]

        if tile_info:
            return self.get_tile(tile_info[0], tile_info[1], tile_info[2])
        return None

    def is_grass_tile(self, tile_data):
        """Check if a tile is grass (not a building or other type)"""
        if isinstance(tile_data, tuple):
            return False  # Buildings are stored as tuples
        return tile_data == 'grass'

    def is_sidewalk_tile(self, tile_data):
        """Check if a tile is sidewalk (not a building or other type)"""
        if isinstance(tile_data, tuple):
            return False  # Buildings are stored as tuples
        return tile_data == 'sidewalk'


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

        # Initialize animated player instead of simple position
        self.player = AnimatedPlayer(
            self.city_map.width // 2,
            self.city_map.height // 2,
            TILE_SIZE
        )

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
        # Use the player's pixel position for smooth camera
        self.camera_x = self.player.pixel_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.player.pixel_y - (SCREEN_HEIGHT - UI_HEIGHT) // 2 + TILE_SIZE // 2

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
                elif tile_data == 'sidewalk':
                    # Get appropriate sidewalk tile based on neighbors
                    tile = self.tile_manager.get_sidewalk_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('sidewalk', tile)
                elif tile_data == 'road':
                    tile = self.tile_manager.get_random_tile('road')
                    if tile:
                        self.map_cache[(x, y)] = ('road', tile)
                else:
                    # For dirt/sand background
                    self.map_cache[(x, y)] = ('dirt', None)

    def handle_input(self):
        """Handle user input"""
        keys = pygame.key.get_pressed()

        # Only move if not already moving (for tile-based movement)
        if not self.player.moving:
            new_x, new_y = self.player.x, self.player.y

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if new_x > 0:
                    new_x -= 1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if new_x < self.city_map.width - 1:
                    new_x += 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                if new_y > 0:
                    new_y -= 1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if new_y < self.city_map.height - 1:
                    new_y += 1

            # Move player if position changed
            if new_x != self.player.x or new_y != self.player.y:
                self.player.move_to(new_x, new_y)

    def draw(self):
        """Draw everything"""
        self.screen.fill(BACKGROUND_COLOR)

        # Calculate visible tile range
        start_x = max(0, int(self.camera_x // TILE_SIZE))
        end_x = min(int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 2), self.city_map.width)
        start_y = max(0, int(self.camera_y // TILE_SIZE))
        end_y = min(int((self.camera_y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE + 2), self.city_map.height)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - int(self.camera_x)
                screen_y = y * TILE_SIZE - int(self.camera_y)

                # Get cached tile
                if (x, y) in self.map_cache:
                    tile_type, tile_surface = self.map_cache[(x, y)]

                    if tile_type == 'dirt':
                        # Draw brown background for dirt
                        pygame.draw.rect(self.screen, (139, 90, 43),
                                         (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif tile_surface:
                        self.screen.blit(tile_surface, (screen_x, screen_y))

                # Draw grid
                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Draw player using animated player
        self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Draw UI
        self.draw_ui()

    def draw_ui(self):
        """Draw user interface"""
        # Bottom panel
        pygame.draw.rect(self.screen, UI_BACKGROUND,
                         (0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))

        # Info text - update to use self.player.x and self.player.y
        info_texts = [
            f"Player: ({self.player.x}, {self.player.y}) | Camera: ({int(self.camera_x)}, {int(self.camera_y)})",
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

        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds

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

            # Handle input
            self.handle_input()

            # Update player animation
            self.player.update(dt)

            # Update camera to follow player
            self.update_camera()

            # Draw
            self.draw()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
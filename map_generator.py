import pygame
import sys
from PIL import Image
import numpy as np
import math
import random

# Initialize Pygame
pygame.init()

# Game constants
TILE_SIZE = 32  # Size of each tile in pixels
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Time of day effects
DAY_NIGHT_CYCLE = False  # Set to True to enable day/night cycle
ENABLE_LIGHTING = True  # Set to True for lighting effects

# Define tile mappings (RGB colors from map to tile types)
TILE_MAPPINGS = {
    # Natural terrain
    (34, 139, 34): 'grass',  # Forest green
    (0, 100, 0): 'tree',  # Dark green
    (128, 128, 128): 'rock',  # Gray
    (0, 119, 190): 'water',  # Blue
    (238, 203, 173): 'sand',  # Sandy beige
    (139, 69, 19): 'dirt',  # Brown

    # Modern buildings
    (139, 90, 43): 'house',  # Brown house
    (192, 192, 192): 'bank',  # Silver/light gray
    (105, 105, 105): 'building',  # Dark gray office
    (70, 130, 180): 'skyscraper',  # Steel blue
    (255, 140, 0): 'store',  # Dark orange
    (64, 64, 64): 'factory',  # Dark gray
    (255, 255, 255): 'hospital',  # White
    (178, 34, 34): 'school',  # Brick red

    # Urban terrain
    (32, 32, 32): 'road',  # Asphalt black
    (190, 190, 190): 'sidewalk',  # Light gray concrete
}

# Define which tiles are walkable
WALKABLE_TILES = {'grass', 'sand', 'dirt', 'road', 'sidewalk', 'water'}


class TileMap:
    def __init__(self, map_path):
        """Load the map from a PNG file."""
        # Load the PNG file
        img = Image.open(map_path)
        self.map_array = np.array(img)
        self.height, self.width = self.map_array.shape[:2]

        # Parse the map to identify tile types
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                pixel_color = tuple(self.map_array[y, x][:3])  # Get RGB values
                tile_type = TILE_MAPPINGS.get(pixel_color, 'grass')  # Default to grass
                row.append(tile_type)
            self.tiles.append(row)

        print(f"Map loaded: {self.width}x{self.height} tiles")

    def get_tile(self, x, y):
        """Get the tile type at given coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def is_walkable(self, x, y):
        """Check if a tile is walkable."""
        tile = self.get_tile(x, y)
        return tile in WALKABLE_TILES


class Player:
    def __init__(self, x, y):
        """Initialize the player."""
        self.x = x
        self.y = y
        self.speed = 5  # Tiles per second
        self.move_cooldown = 0

    def update(self, dt, keys, tile_map):
        """Update player position based on input."""
        self.move_cooldown -= dt

        if self.move_cooldown <= 0:
            dx, dy = 0, 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            # Check if the new position is walkable
            new_x, new_y = self.x + dx, self.y + dy
            if dx != 0 or dy != 0:
                if tile_map.is_walkable(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    self.move_cooldown = 1.0 / self.speed


class Game:
    def __init__(self, map_path):
        """Initialize the game."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tile Map Game")
        self.clock = pygame.time.Clock()

        # Load the tile map
        self.tile_map = TileMap(map_path)

        # Find a walkable starting position for the player
        start_x, start_y = self.find_walkable_position()
        self.player = Player(start_x, start_y)

        # Camera offset
        self.camera_x = 0
        self.camera_y = 0

        # Load or create tile textures
        self.textures = self.load_textures()

    def find_walkable_position(self):
        """Find a walkable position on the map for the player to start."""
        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                if self.tile_map.is_walkable(x, y):
                    return x, y
        return 0, 0  # Default position

    def load_textures(self):
        """Load textures from files, or create simple colored rectangles as fallback."""
        textures = {}

        # Define texture file paths
        texture_files = {
            # Natural terrain
            'grass': 'textures/grass.png',
            'tree': 'textures/tree.png',
            'rock': 'textures/rock.png',
            'water': 'textures/water.png',
            'sand': 'textures/sand.png',
            'dirt': 'textures/dirt.png',

            # Modern buildings
            'house': 'textures/house.png',
            'bank': 'textures/bank.png',
            'building': 'textures/building.png',
            'skyscraper': 'textures/skyscraper.png',
            'store': 'textures/store.png',
            'factory': 'textures/factory.png',
            'hospital': 'textures/hospital.png',
            'school': 'textures/school.png',

            # Urban terrain
            'road': 'textures/road.png',
            'sidewalk': 'textures/sidewalk.png',

            # Player
            'player': 'textures/player.png',
        }

        # Define fallback colors for each tile type
        tile_colors = {
            # Natural terrain
            'grass': (34, 139, 34),
            'tree': (0, 100, 0),
            'rock': (128, 128, 128),
            'water': (0, 119, 190),
            'sand': (238, 203, 173),
            'dirt': (139, 69, 19),

            # Modern buildings
            'house': (139, 90, 43),
            'bank': (192, 192, 192),
            'building': (105, 105, 105),
            'skyscraper': (70, 130, 180),
            'store': (255, 140, 0),
            'factory': (64, 64, 64),
            'hospital': (255, 255, 255),
            'school': (178, 34, 34),

            # Urban terrain
            'road': (32, 32, 32),
            'sidewalk': (190, 190, 190),
        }

        # Try to load each texture from file
        for tile_type, filepath in texture_files.items():
            try:
                # Try to load the texture file
                img = pygame.image.load(filepath)
                # Scale it to the correct tile size
                textures[tile_type] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                print(f"Loaded {tile_type} texture from {filepath}")
            except:
                # If file doesn't exist, create a colored rectangle as fallback
                print(f"Could not load {filepath}, using colored rectangle instead")

                if tile_type == 'player':
                    # Create player texture
                    surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    surface.fill((255, 255, 255))  # White background
                    pygame.draw.circle(surface, (255, 0, 0),
                                       (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
                    textures[tile_type] = surface
                else:
                    # Create colored surface
                    surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    surface.fill(tile_colors.get(tile_type, (255, 0, 255)))  # Magenta if unknown

                    # Add some visual detail for fallback textures
                    if tile_type == 'tree':
                        # Draw a simple tree trunk
                        pygame.draw.rect(surface, (101, 67, 33),
                                         (TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3, TILE_SIZE // 2))
                    elif tile_type == 'rock':
                        # Draw a circle for rock
                        pygame.draw.circle(surface, (100, 100, 100),
                                           (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
                    elif tile_type == 'water':
                        # Add wave lines
                        pygame.draw.line(surface, (0, 100, 170), (0, TILE_SIZE // 3),
                                         (TILE_SIZE, TILE_SIZE // 3), 2)
                        pygame.draw.line(surface, (0, 100, 170), (0, 2 * TILE_SIZE // 3),
                                         (TILE_SIZE, 2 * TILE_SIZE // 3), 2)

                    textures[tile_type] = surface

        return textures

    def update_camera(self):
        """Update camera to follow player."""
        # Center camera on player
        self.camera_x = self.player.x * TILE_SIZE - SCREEN_WIDTH // 2
        self.camera_y = self.player.y * TILE_SIZE - SCREEN_HEIGHT // 2

        # Clamp camera to map bounds
        max_camera_x = self.tile_map.width * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = self.tile_map.height * TILE_SIZE - SCREEN_HEIGHT

        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def draw(self):
        """Draw the game."""
        self.screen.fill((0, 0, 0))  # Clear screen

        # Calculate visible tile range
        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(self.tile_map.width, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(self.tile_map.height, (self.camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)

        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tile_map.get_tile(x, y)
                if tile_type and tile_type in self.textures:
                    screen_x = x * TILE_SIZE - self.camera_x
                    screen_y = y * TILE_SIZE - self.camera_y
                    self.screen.blit(self.textures[tile_type], (screen_x, screen_y))

        # Draw player
        player_screen_x = self.player.x * TILE_SIZE - self.camera_x
        player_screen_y = self.player.y * TILE_SIZE - self.camera_y
        self.screen.blit(self.textures['player'], (player_screen_x, player_screen_y))

        # Draw UI
        font = pygame.font.Font(None, 36)
        pos_text = font.render(f"Position: ({self.player.x}, {self.player.y})", True, (255, 255, 255))
        self.screen.blit(pos_text, (10, 10))

        tile_text = font.render(f"Tile: {self.tile_map.get_tile(self.player.x, self.player.y)}", True, (255, 255, 255))
        self.screen.blit(tile_text, (10, 50))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        dt = 0

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Get keyboard state
            keys = pygame.key.get_pressed()

            # Update game
            self.player.update(dt, keys, self.tile_map)
            self.update_camera()

            # Draw everything
            self.draw()

            # Control frame rate
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds

        pygame.quit()
        sys.exit()


def load_textures_from_files(texture_paths):
    """
    Load textures from PNG files if provided.

    texture_paths should be a dictionary like:
    {
        'grass': 'textures/grass.png',
        'tree': 'textures/tree.png',
        ...
    }
    """
    textures = {}

    for tile_type, path in texture_paths.items():
        try:
            img = pygame.image.load(path)
            textures[tile_type] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            print(f"Loaded texture for {tile_type} from {path}")
        except:
            print(f"Failed to load texture for {tile_type} from {path}")

    return textures


if __name__ == "__main__":
    # Check if a map path was provided
    if len(sys.argv) > 1:
        map_path = sys.argv[1]
    else:
        map_path = "city_map.png"

    # Create and run the game
    game = Game(map_path)
    game.run()
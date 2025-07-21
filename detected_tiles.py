import pygame
import sys
import numpy as np
import random
import os

pygame.init()

# Constants
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
MAP_WIDTH = 50
MAP_HEIGHT = 50

# Multi-tile building definitions from your file
BUILDING_DEFINITIONS = {
    'skyscraper_1_3x6': {
        'size': (3, 6),
        'category': 'skyscraper',
        'tiles': [
            [('CP_V1.0.4.png', 7, 2), ('CP_V1.0.4.png', 8, 2), ('CP_V1.0.4.png', 9, 2)],
            [('CP_V1.0.4.png', 7, 3), ('CP_V1.0.4.png', 8, 3), ('CP_V1.0.4.png', 9, 3)],
            [('CP_V1.0.4.png', 7, 4), ('CP_V1.0.4.png', 8, 4), ('CP_V1.0.4.png', 9, 4)],
            [('CP_V1.0.4.png', 7, 5), ('CP_V1.0.4.png', 8, 5), ('CP_V1.0.4.png', 9, 5)],
            [('CP_V1.0.4.png', 7, 6), ('CP_V1.0.4.png', 8, 6), ('CP_V1.0.4.png', 9, 6)],
            [('CP_V1.0.4.png', 7, 7), ('CP_V1.0.4.png', 8, 7), ('CP_V1.0.4.png', 9, 7)],
        ]
    },
    'store_1_4x3': {
        'size': (4, 3),
        'category': 'store',
        'tiles': [
            [('CP_V1.0.4.png', 1, 17), ('CP_V1.0.4.png', 2, 17), ('CP_V1.0.4.png', 3, 17), ('CP_V1.0.4.png', 4, 17)],
            [('CP_V1.0.4.png', 1, 18), ('CP_V1.0.4.png', 2, 18), ('CP_V1.0.4.png', 3, 18), ('CP_V1.0.4.png', 4, 18)],
            [('CP_V1.0.4.png', 1, 19), ('CP_V1.0.4.png', 2, 19), ('CP_V1.0.4.png', 3, 19), ('CP_V1.0.4.png', 4, 19)],
        ]
    },
    'building_1_3x3': {
        'size': (3, 3),
        'category': 'building',
        'tiles': [
            [('CP_V1.0.4.png', 18, 11), ('CP_V1.0.4.png', 19, 11), ('CP_V1.0.4.png', 20, 11)],
            [('CP_V1.0.4.png', 18, 12), ('CP_V1.0.4.png', 19, 12), ('CP_V1.0.4.png', 20, 12)],
            [('CP_V1.0.4.png', 18, 13), ('CP_V1.0.4.png', 19, 13), ('CP_V1.0.4.png', 20, 13)],
        ]
    },
}

# Simple single tiles for ground (you should add your actual selected tiles here)
TILE_POSITIONS = {
    'grass': [('CP_V1.0.4.png', 16, 48)],  # Default grass
    'road': [('CP_V1.0.4.png', 3, 38)],  # Default road
    'sidewalk': [('CP_V1.0.4.png', 5, 8)],  # Default sidewalk
}


class BuildingMapGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("City Map with Multi-tile Buildings")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Load sprite sheets
        self.sheets = {}
        self.load_sheets()

        # Generate map
        self.map_data = self.generate_map()

        # Load sprites
        self.sprites = {}
        self.load_sprites()

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Player
        self.player_x = MAP_WIDTH // 2
        self.player_y = MAP_HEIGHT // 2

    def load_sheets(self):
        """Load sprite sheets"""
        base_dir = os.path.dirname(__file__)

        # Try to load CP_V1.0.4.png
        try:
            path = os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", "CP_V1.0.4.png")
            self.sheets['CP_V1.0.4.png'] = pygame.image.load(path)
            print(f"Loaded CP_V1.0.4.png")
        except Exception as e:
            print(f"Failed to load sprite sheet: {e}")
            # Create fallback colored surface
            self.sheets['CP_V1.0.4.png'] = pygame.Surface((1024, 1024))
            self.sheets['CP_V1.0.4.png'].fill((100, 100, 100))

    def load_sprites(self):
        """Extract sprites from sheets"""
        # Load single tiles
        for tile_type, positions in TILE_POSITIONS.items():
            self.sprites[tile_type] = []
            for sheet_name, x, y in positions:
                if sheet_name in self.sheets:
                    sheet = self.sheets[sheet_name]
                    rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                                       ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                    if rect.right <= sheet.get_width() and rect.bottom <= sheet.get_height():
                        tile = sheet.subsurface(rect).copy()
                        tile = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
                        self.sprites[tile_type].append(tile)

            # Fallback if sprite not found
            if not self.sprites[tile_type]:
                fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
                colors = {
                    'grass': (50, 150, 50),
                    'road': (60, 60, 60),
                    'sidewalk': (150, 150, 150),
                }
                fallback.fill(colors.get(tile_type, (255, 0, 255)))
                self.sprites[tile_type] = [fallback]

        # Create player sprite
        player = pygame.Surface((TILE_SIZE - 8, TILE_SIZE - 8), pygame.SRCALPHA)
        pygame.draw.circle(player, (0, 100, 255), (player.get_width() // 2, player.get_height() // 2), 12)
        pygame.draw.circle(player, (0, 150, 255), (player.get_width() // 2, player.get_height() // 2), 10)
        self.sprites['player'] = player

    def can_place_building(self, map_data, building_def, x, y):
        """Check if a building can be placed at the given position"""
        width, height = building_def['size']

        # Check bounds
        if x + width > MAP_WIDTH or y + height > MAP_HEIGHT:
            return False

        # Check if area is clear (only grass)
        for dy in range(height):
            for dx in range(width):
                if map_data[y + dy][x + dx] != 'grass':
                    return False

        # Check minimum distance from other buildings
        padding = 1
        for dy in range(-padding, height + padding):
            for dx in range(-padding, width + padding):
                check_x = x + dx
                check_y = y + dy
                if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                    cell = map_data[check_y][check_x]
                    if cell.startswith('building:'):
                        return False

        return True

    def place_building(self, map_data, building_name, x, y):
        """Place a building on the map"""
        building = BUILDING_DEFINITIONS[building_name]
        width, height = building['size']

        # Mark all cells occupied by this building
        for dy in range(height):
            for dx in range(width):
                map_data[y + dy][x + dx] = f'building:{building_name}:{dx},{dy}'

    def generate_map(self):
        """Generate a city map with roads and buildings"""
        # Initialize with grass
        map_data = [['grass' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

        # Add main roads in a grid pattern
        road_spacing = 12

        # Vertical roads
        for x in range(road_spacing // 2, MAP_WIDTH, road_spacing):
            for y in range(MAP_HEIGHT):
                map_data[y][x] = 'road'

        # Horizontal roads
        for y in range(road_spacing // 2, MAP_HEIGHT, road_spacing):
            for x in range(MAP_WIDTH):
                map_data[y][x] = 'road'

        # Add sidewalks next to roads
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if map_data[y][x] == 'road':
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH:
                            if map_data[ny][nx] == 'grass':
                                map_data[ny][nx] = 'sidewalk'

        # Place buildings
        building_types = list(BUILDING_DEFINITIONS.keys())
        attempts = 0
        max_attempts = 500

        while attempts < max_attempts:
            # Random position
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)

            # Random building type
            building_name = random.choice(building_types)
            building = BUILDING_DEFINITIONS[building_name]

            # Try to place it
            if self.can_place_building(map_data, building, x, y):
                # Check if near a road (for realism)
                near_road = False
                width, height = building['size']
                for dy in range(-1, height + 1):
                    for dx in range(-1, width + 1):
                        check_x = x + dx
                        check_y = y + dy
                        if 0 <= check_x < MAP_WIDTH and 0 <= check_y < MAP_HEIGHT:
                            if map_data[check_y][check_x] in ['road', 'sidewalk']:
                                near_road = True
                                break

                if near_road:
                    self.place_building(map_data, building_name, x, y)
                    print(f"Placed {building_name} at ({x}, {y})")

            attempts += 1

        return map_data

    def get_tile_sprite(self, x, y):
        """Get the appropriate sprite for a map cell"""
        cell = self.map_data[y][x]

        if cell.startswith('building:'):
            # Parse building info
            parts = cell.split(':')
            building_name = parts[1]
            offset = parts[2]
            dx, dy = map(int, offset.split(','))

            # Get the specific tile from the building definition
            building = BUILDING_DEFINITIONS[building_name]
            sheet_name, tile_x, tile_y = building['tiles'][dy][dx]

            if sheet_name in self.sheets:
                sheet = self.sheets[sheet_name]
                rect = pygame.Rect(tile_x * ORIGINAL_TILE_SIZE, tile_y * ORIGINAL_TILE_SIZE,
                                   ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                if rect.right <= sheet.get_width() and rect.bottom <= sheet.get_height():
                    tile = sheet.subsurface(rect).copy()
                    return pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))

            # Fallback
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill((200, 100, 100))
            return fallback
        else:
            # Regular single tile
            if cell in self.sprites and self.sprites[cell]:
                return self.sprites[cell][0]
            else:
                # Fallback
                fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback.fill((255, 0, 255))
                return fallback

    def draw(self):
        """Draw the game"""
        self.screen.fill((20, 20, 30))

        # Calculate visible tiles
        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(MAP_WIDTH, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(MAP_HEIGHT, (self.camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)

        # Draw map
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y

                sprite = self.get_tile_sprite(x, y)
                self.screen.blit(sprite, (screen_x, screen_y))

        # Draw player
        player_screen_x = self.player_x * TILE_SIZE - self.camera_x + 4
        player_screen_y = self.player_y * TILE_SIZE - self.camera_y + 4
        self.screen.blit(self.sprites['player'], (player_screen_x, player_screen_y))

        # UI
        texts = [
            "City Map with Multi-tile Buildings",
            f"Position: {self.player_x}, {self.player_y}",
            "WASD/Arrows: Move, ESC: Exit",
            "Buildings are properly assembled from tiles!"
        ]
        for i, text in enumerate(texts):
            rendered = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(rendered, (10, 10 + i * 25))

    def handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        if dx or dy:
            new_x = self.player_x + dx
            new_y = self.player_y + dy

            # Check bounds
            if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
                # Check if walkable
                cell = self.map_data[new_y][new_x]
                if cell in ['road', 'sidewalk', 'grass']:
                    self.player_x = new_x
                    self.player_y = new_y

        # Update camera to follow player
        self.camera_x = max(0, min(self.player_x * TILE_SIZE - SCREEN_WIDTH // 2,
                                   MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.player_y * TILE_SIZE - SCREEN_HEIGHT // 2,
                                   MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))

    def save_map_image(self):
        """Save the entire map as an image"""
        surface = pygame.Surface((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                sprite = self.get_tile_sprite(x, y)
                surface.blit(sprite, (x * TILE_SIZE, y * TILE_SIZE))

        pygame.image.save(surface, "city_map_with_buildings.png")
        print("Saved map to city_map_with_buildings.png")

    def run(self):
        """Main game loop"""
        running = True

        print("\nControls:")
        print("- WASD or Arrow keys to move")
        print("- P to save map as PNG")
        print("- ESC to exit\n")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        self.save_map_image()

            self.handle_input()
            self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = BuildingMapGame()
    game.run()
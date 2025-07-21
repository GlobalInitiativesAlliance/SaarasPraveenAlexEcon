import pygame
import sys
import numpy as np
import os
import random

pygame.init()

# Constants
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
MAP_WIDTH = 100
MAP_HEIGHT = 100

# TILE_POSITIONS (added example positions for ground tiles from CP_V1.0.4.png; user should update with actual from debug mode)
TILE_POSITIONS = {
    'road': [
        ('CP_V1.0.4.png', 0, 10),  # Example: assume some road variants
        ('CP_V1.0.4.png', 1, 10),
        ('CP_V1.0.4.png', 2, 10),
        ('CP_V1.0.4.png', 3, 10),
    ],
    'sidewalk': [
        ('CP_V1.0.4.png', 4, 10),  # Example
        ('CP_V1.0.4.png', 5, 10),
        ('CP_V1.0.4.png', 6, 10),
    ],
    'grass': [
        ('CP_V1.0.4.png', 0, 0),   # Example: multiple grass variants for pattern
        ('CP_V1.0.4.png', 1, 0),
        ('CP_V1.0.4.png', 2, 0),
        ('CP_V1.0.4.png', 3, 0),
        ('CP_V1.0.4.png', 0, 1),
    ],
    'water': [
        ('CP_V1.0.4.png', 4, 0),   # Example: water variants
        ('CP_V1.0.4.png', 5, 0),
        ('CP_V1.0.4.png', 6, 0),
        ('CP_V1.0.4.png', 7, 0),
    ],
    'house': [
        ('BL001.png', 0, 0),
        ('BL001.png', 1, 0),
        ('BL001.png', 0, 1),
        ('BL001.png', 1, 1),
        ('BL001.png', 0, 2),
        ('BL001.png', 14, 1),
        ('BL001.png', 3, 10),
    ],
    'building': [
        ('BD001.png', 0, 0),
        ('BD001.png', 1, 0),
        ('BD001.png', 2, 0),
        ('BD001.png', 0, 1),
        ('BL001.png', 6, 6),
    ],
    'store': [
        ('BL001.png', 0, 3),
        ('BL001.png', 1, 3),
        ('BL001.png', 2, 3),
        ('BL001.png', 14, 1),
    ],
    'skyscraper': [
        ('BD001.png', 0, 2),
        ('BD001.png', 1, 2),
        ('BD001.png', 2, 2),
        ('BD001.png', 0, 3),
    ],
    'bank': [
        ('BL001.png', 3, 0),
        ('BL001.png', 4, 0),
        ('BL001.png', 3, 1),
    ],
}

WALKABLE = {'road', 'sidewalk', 'grass'}

class DebugGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NYKNCK City Game - Debug Mode")
        self.clock = pygame.time.Clock()

        self.sheet_names = ['SL001.png', 'BL001.png', 'BD001.png', 'CP_V1.0.4.png']
        self.current_sheet_index = 0
        self.scroll_x = 0
        self.scroll_y = 0

        self.sheets = {}
        self.load_sheets()

        # Generate procedural map instead of loading PNG
        self.generate_map(MAP_WIDTH, MAP_HEIGHT)
        self.sprites = {}
        self.load_sprites()
        self.player_x, self.player_y = self.find_start_position()
        self.camera_x = 0
        self.camera_y = 0
        self.move_timer = 0

        self.debug_mode = False

    def generate_map(self, width, height):
        """Redesigned procedural generation for a more realistic city pattern:
        - Start with grass
        - Add a river (horizontal or vertical)
        - Add grid-like roads with variable spacing
        - Add sidewalks adjacent to roads
        - Fill blocks near roads with buildings, leaving some grass for parks
        """
        self.tiles = np.full((height, width), 'grass', dtype=object)
        self.map_height, self.map_width = height, width

        # Add water: a river crossing the map
        river_center = random.randint(20, height - 20) if random.random() < 0.5 else random.randint(20, width - 20)
        river_width = random.randint(3, 6)
        direction = random.choice(['horizontal', 'vertical'])

        if direction == 'horizontal':
            for x in range(width):
                for dy in range(-river_width // 2, river_width // 2 + 1):
                    y = river_center + dy + random.randint(-1, 1)  # Slight meandering
                    if 0 <= y < height:
                        self.tiles[y, x] = 'water'
        else:
            for y in range(height):
                for dx in range(-river_width // 2, river_width // 2 + 1):
                    x = river_center + dx + random.randint(-1, 1)  # Slight meandering
                    if 0 <= x < width:
                        self.tiles[y, x] = 'water'

        # Add grid roads with variable spacing for a natural city feel
        v_spacings = [random.randint(8, 15) for _ in range(20)]  # Enough for ~100 width
        h_spacings = [random.randint(8, 15) for _ in range(20)]

        # Vertical roads
        current_x = random.randint(5, 10)
        while current_x < width:
            for y in range(height):
                if self.tiles[y, current_x] != 'water':
                    self.tiles[y, current_x] = 'road'
            current_x += random.choice(v_spacings)

        # Horizontal roads
        current_y = random.randint(5, 10)
        while current_y < height:
            for x in range(width):
                if self.tiles[current_y, x] != 'water':
                    self.tiles[current_y, x] = 'road'
            current_y += random.choice(h_spacings)

        # Add sidewalks next to roads
        for y in range(height):
            for x in range(width):
                if self.tiles[y, x] == 'road':
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width and self.tiles[ny, nx] not in {'road', 'water', 'sidewalk'}:
                            if random.random() < 0.8:  # Higher chance for consistent sidewalks
                                self.tiles[ny, nx] = 'sidewalk'

        # Add buildings in city blocks (areas between roads)
        building_types = ['house', 'building', 'store', 'skyscraper', 'bank']
        for y in range(height):
            for x in range(width):
                if self.tiles[y, x] in {'grass', 'sidewalk'}:
                    # Check proximity to road
                    near_road = any(
                        self.tiles[max(0, min(height - 1, y + dy)), max(0, min(width - 1, x + dx))] == 'road'
                        for dy in [-1, 0, 1] for dx in [-1, 0, 1] if dy != 0 or dx != 0
                    )
                    if near_road:
                        if random.random() < 0.75:  # Dense buildings near roads
                            self.tiles[y, x] = random.choice(building_types)
                    elif random.random() < 0.05:  # Sparse buildings elsewhere
                        self.tiles[y, x] = random.choice(building_types)

        # Optional: Add small parks or green spaces by clearing some building areas
        num_parks = random.randint(3, 6)
        for _ in range(num_parks):
            px, py = random.randint(0, width - 1), random.randint(0, height - 1)
            park_size = random.randint(5, 10)
            for dy in range(-park_size // 2, park_size // 2 + 1):
                for dx in range(-park_size // 2, park_size // 2 + 1):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < width and 0 <= ny < height and self.tiles[ny, nx] not in {'road', 'water', 'sidewalk'}:
                        self.tiles[ny, nx] = 'grass'

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
                print(f"Failed to load {sheet_name}: {e}. Check the path.")

    def load_sprites(self):
        base_dir = os.path.dirname(__file__)
        animations_path = os.path.join(base_dir, "CP_V1.1.0_nyknck", "Animations")

        for tile_type, positions in TILE_POSITIONS.items():
            self.sprites[tile_type] = []
            loaded_count = 0

            for sheet_name, x, y in positions:
                try:
                    if sheet_name == 'CP_V1.0.4.png':
                        sheet_path = os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", sheet_name)
                    else:
                        sheet_path = os.path.join(animations_path, sheet_name)
                    sheet = pygame.image.load(sheet_path)

                    px = x * ORIGINAL_TILE_SIZE
                    py = y * ORIGINAL_TILE_SIZE

                    if px + ORIGINAL_TILE_SIZE <= sheet.get_width() and py + ORIGINAL_TILE_SIZE <= sheet.get_height():
                        rect = pygame.Rect(px, py, ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                        tile = sheet.subsurface(rect).copy()
                        tile = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
                        self.sprites[tile_type].append(tile)
                        loaded_count += 1
                    else:
                        print(f"Invalid position ({x}, {y}) for {tile_type} in {sheet_name}")
                except Exception as e:
                    print(f"Failed to load sprite for {tile_type} from {sheet_name} at ({x},{y}): {e}")

            print(f"Loaded {loaded_count} sprites for {tile_type}")

            if not self.sprites[tile_type]:
                fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_color = {
                    'road': (40, 40, 40),
                    'sidewalk': (180, 180, 180),
                    'grass': (50, 150, 50),
                    'water': (50, 140, 255),
                    'house': (150, 100, 50),
                    'building': (120, 120, 120),
                    'store': (255, 140, 0),
                    'skyscraper': (70, 130, 180),
                    'bank': (192, 192, 192),
                }.get(tile_type, (255, 0, 255))
                fallback.fill(fallback_color)
                self.sprites[tile_type] = [fallback]

        # Player sprite
        player = pygame.Surface((TILE_SIZE - 4, TILE_SIZE - 4), pygame.SRCALPHA)
        pygame.draw.circle(player, (50, 100, 200), ((TILE_SIZE - 4)//2, (TILE_SIZE - 4)//2), 14)
        pygame.draw.circle(player, (100, 150, 255), ((TILE_SIZE - 4)//2, (TILE_SIZE - 4)//2), 12)
        pygame.draw.circle(player, (255, 255, 255), ((TILE_SIZE - 4)//2 - 4, (TILE_SIZE - 4)//2 - 4), 3)
        pygame.draw.circle(player, (255, 255, 255), ((TILE_SIZE - 4)//2 + 4, (TILE_SIZE - 4)//2 - 4), 3)
        self.sprites['player'] = player

    def find_start_position(self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.tiles[y][x] in WALKABLE:
                    return x, y
        return 0, 0

    def save_full_map(self):
        full_width = self.map_width * TILE_SIZE
        full_height = self.map_height * TILE_SIZE
        surface = pygame.Surface((full_width, full_height))
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_type = self.tiles[y][x]
                if tile_type in self.sprites and self.sprites[tile_type]:
                    variants = self.sprites[tile_type]
                    variant = variants[(x + y * self.map_width) % len(variants)]
                    surface.blit(variant, (x * TILE_SIZE, y * TILE_SIZE))
        pygame.image.save(surface, "full_city_map.png")
        print("Saved full city map to full_city_map.png")

    def draw_debug(self):
        self.screen.fill((30, 30, 40))

        sheet_name = self.sheet_names[self.current_sheet_index]
        if sheet_name not in self.sheets:
            return

        sheet = self.sheets[sheet_name]

        for gy in range(20):
            for gx in range(40):
                px = gx * ORIGINAL_TILE_SIZE + self.scroll_x
                py = gy * ORIGINAL_TILE_SIZE + self.scroll_y

                if px + ORIGINAL_TILE_SIZE <= sheet.get_width() and py + ORIGINAL_TILE_SIZE <= sheet.get_height():
                    rect = pygame.Rect(px, py, ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                    tile = sheet.subsurface(rect)
                    scaled = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))

                    screen_x = gx * (TILE_SIZE + 2) + 10
                    screen_y = gy * (TILE_SIZE + 2) + 50

                    self.screen.blit(scaled, (screen_x, screen_y))

                    pygame.draw.rect(self.screen, (100, 100, 100), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        font = pygame.font.Font(None, 24)
        info_text = [
            f"Sheet: {sheet_name} ({sheet.get_width()}x{sheet.get_height()}px)",
            f"Scroll: {self.scroll_x}, {self.scroll_y}",
            "Keys: Tab=switch, Arrows=scroll, Y=toggle debug",
            "Click tile to print coords"
        ]
        for i, text in enumerate(info_text):
            self.screen.blit(font.render(text, True, (255, 255, 255)), (10, 10 + i * 25))

        mx, my = pygame.mouse.get_pos()
        grid_x = (mx - 10) // (TILE_SIZE + 2)
        grid_y = (my - 50) // (TILE_SIZE + 2)
        tile_x = grid_x + self.scroll_x // ORIGINAL_TILE_SIZE
        tile_y = grid_y + self.scroll_y // ORIGINAL_TILE_SIZE
        mouse_text = font.render(f"Cursor: ({tile_x}, {tile_y})", True, (255, 255, 0))
        self.screen.blit(mouse_text, (SCREEN_WIDTH - 200, 10))

    def draw_game(self):
        self.screen.fill((20, 20, 30))

        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(self.map_width, (self.camera_x + SCREEN_WIDTH + TILE_SIZE) // TILE_SIZE)
        end_y = min(self.map_height, (self.camera_y + SCREEN_HEIGHT + TILE_SIZE) // TILE_SIZE)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                if tile_type in self.sprites and self.sprites[tile_type]:
                    variants = self.sprites[tile_type]
                    variant = variants[(x + y * self.map_width) % len(variants)]
                    screen_x = x * TILE_SIZE - self.camera_x
                    screen_y = y * TILE_SIZE - self.camera_y
                    self.screen.blit(variant, (screen_x, screen_y))

        player_screen_x = self.player_x * TILE_SIZE - self.camera_x + 2
        player_screen_y = self.player_y * TILE_SIZE - self.camera_y + 2
        self.screen.blit(self.sprites['player'], (player_screen_x, player_screen_y))

        font = pygame.font.Font(None, 24)
        texts = [
            ("NYKNCK City", (100, 255, 100)),
            (f"Pos: {self.player_x}, {self.player_y}", (255, 255, 255)),
            (f"Tile: {self.tiles[self.player_y][self.player_x]}", (255, 255, 255)),
            ("WASD move, Y debug, S save full map", (200, 200, 200)),
        ]
        for i, (text, color) in enumerate(texts):
            self.screen.blit(font.render(text, True, color), (10, 10 + i * 25))

    def handle_input(self, dt):
        self.move_timer -= dt
        if self.move_timer > 0:
            return

        keys = pygame.key.get_pressed()

        if self.debug_mode:
            scroll_speed = ORIGINAL_TILE_SIZE if keys[pygame.K_LSHIFT] else 4
            if keys[pygame.K_LEFT]:
                self.scroll_x = max(0, self.scroll_x - scroll_speed)
            if keys[pygame.K_RIGHT]:
                self.scroll_x += scroll_speed
            if keys[pygame.K_UP]:
                self.scroll_y = max(0, self.scroll_y - scroll_speed)
            if keys[pygame.K_DOWN]:
                self.scroll_y += scroll_speed
        else:
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
                if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height and self.tiles[new_y][new_x] in WALKABLE:
                    self.player_x = new_x
                    self.player_y = new_y
                    self.move_timer = 0.15

                self.camera_x = max(0, min(self.player_x * TILE_SIZE - SCREEN_WIDTH // 2, self.map_width * TILE_SIZE - SCREEN_WIDTH))
                self.camera_y = max(0, min(self.player_y * TILE_SIZE - SCREEN_HEIGHT // 2, self.map_height * TILE_SIZE - SCREEN_HEIGHT))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_y:  # Changed to 'Y' for debug toggle
                        self.debug_mode = not self.debug_mode
                    elif event.key == pygame.K_TAB and self.debug_mode:  # Fixed to K_TAB
                        self.current_sheet_index = (self.current_sheet_index + 1) % len(self.sheet_names)
                        self.scroll_x = 0
                        self.scroll_y = 0
                    elif event.key == pygame.K_s and not self.debug_mode:  # Save full map on 'S'
                        self.save_full_map()
                elif event.type == pygame.MOUSEBUTTONDOWN and self.debug_mode:
                    mx, my = event.pos
                    grid_x = (mx - 10) // (TILE_SIZE + 2)
                    grid_y = (my - 50) // (TILE_SIZE + 2)
                    tile_x = grid_x + self.scroll_x // ORIGINAL_TILE_SIZE
                    tile_y = grid_y + self.scroll_y // ORIGINAL_TILE_SIZE
                    sheet_name = self.sheet_names[self.current_sheet_index]
                    print(f"('{sheet_name}', {tile_x}, {tile_y}),")

            self.handle_input(dt)

            if self.debug_mode:
                self.draw_debug()
            else:
                self.draw_game()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = DebugGame()
    print("\nPress 'Y' to toggle debug mode!")
    print("In debug mode: Tab=switch sheets (now includes CP_V1.0.4.png), Arrows=scroll (Shift for faster), Click=print tile position")
    print("Use debug mode on CP_V1.0.4.png to find ground tile positions and update TILE_POSITIONS accordingly.")
    print("In game mode: Press 'S' to save full city map as PNG")
    game.run()

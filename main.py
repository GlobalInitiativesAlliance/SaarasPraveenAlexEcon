import random
from PIL import Image
import numpy as np
import math

# Define color mappings - ONLY the tiles you have
TILE_COLORS = {
    'grass': (34, 139, 34),  # Forest green
    'water': (0, 119, 190),  # Blue
    'road': (32, 32, 32),  # Asphalt black
    'sidewalk': (190, 190, 190),  # Light gray concrete
    'house': (139, 90, 43),  # Brown house
    'building': (105, 105, 105),  # Dark gray office
    'store': (255, 140, 0),  # Dark orange
    'skyscraper': (70, 130, 180),  # Steel blue
    'bank': (192, 192, 192),  # Silver/light gray
}

# Define building sizes to match your tile_selections.json
BUILDING_SIZES = {
    'house': (3, 3),  # house_1_3x3
    'store': (4, 3),  # store_1_4x3 (also have 4x4 variant)
    'bank': (3, 6),  # bank_1_3x6
    'building': (3, 3),  # building_1_3x3
    'skyscraper': (3, 6),  # skyscraper_1_3x6
}


def place_building(map_array, occupied, x, y, building_type):
    """Place a building on the map, coloring ALL its tiles."""
    if building_type not in BUILDING_SIZES:
        return False

    width, height = BUILDING_SIZES[building_type]
    building_color = TILE_COLORS[building_type]

    # Check if building fits
    map_height, map_width = map_array.shape[:2]
    if x + width > map_width or y + height > map_height:
        return False

    # Check if area is free
    for dy in range(height):
        for dx in range(width):
            if occupied[y + dy, x + dx]:
                return False

    # Color ALL tiles of the building
    for dy in range(height):
        for dx in range(width):
            map_array[y + dy, x + dx] = building_color
            occupied[y + dy, x + dx] = True

    return True


def create_simple_road_grid(map_array, occupied):
    """Create a simple, clean road grid"""
    height, width = map_array.shape[:2]

    # Main roads - create a grid pattern
    # Vertical roads every 12 tiles
    for x in range(8, width - 8, 12):
        for y in range(height):
            map_array[y, x] = TILE_COLORS['road']
            occupied[y, x] = True

    # Horizontal roads every 12 tiles
    for y in range(8, height - 8, 12):
        for x in range(width):
            map_array[y, x] = TILE_COLORS['road']
            occupied[y, x] = True

    # Add sidewalks along roads
    for y in range(height):
        for x in range(width):
            if not occupied[y, x]:
                # Check if next to road
                next_to_road = False
                for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < height and 0 <= nx < width and
                            tuple(map_array[ny, nx]) == TILE_COLORS['road']):
                        next_to_road = True
                        break

                if next_to_road:
                    map_array[y, x] = TILE_COLORS['sidewalk']
                    occupied[y, x] = True


def fill_block_with_buildings(map_array, occupied, x_start, y_start, x_end, y_end, block_type):
    """Fill a block completely with buildings and minimal grass"""
    # Leave 1 tile border for sidewalk
    inner_x_start = x_start + 1
    inner_y_start = y_start + 1
    inner_x_end = x_end - 1
    inner_y_end = y_end - 1

    if block_type == 'residential':
        # Fill with houses in a grid pattern
        for y in range(inner_y_start, inner_y_end - 1, 3):
            for x in range(inner_x_start, inner_x_end - 1, 3):
                if x + 2 <= inner_x_end and y + 2 <= inner_y_end:
                    if place_building(map_array, occupied, x, y, 'house'):
                        # Add a bit of grass around some houses
                        if random.random() < 0.3:
                            for dy, dx in [(2, 0), (0, 2), (2, 2)]:
                                gy, gx = y + dy, x + dx
                                if (gy < inner_y_end and gx < inner_x_end and
                                        not occupied[gy, gx]):
                                    map_array[gy, gx] = TILE_COLORS['grass']
                                    occupied[gy, gx] = True

    elif block_type == 'commercial':
        # Mix of stores and offices
        y = inner_y_start
        while y < inner_y_end - 2:
            x = inner_x_start
            while x < inner_x_end - 2:
                # Try store first
                if x + 4 <= inner_x_end and y + 3 <= inner_y_end and random.random() < 0.5:
                    if place_building(map_array, occupied, x, y, 'store'):
                        x += 4
                        continue

                # Try other buildings
                building_type = random.choice(['building', 'bank'])
                bw, bh = BUILDING_SIZES[building_type]
                if x + bw <= inner_x_end and y + bh <= inner_y_end:
                    if place_building(map_array, occupied, x, y, building_type):
                        x += bw
                        continue

                x += 1
            y += 3

    elif block_type == 'downtown':
        # Dense with skyscrapers
        y = inner_y_start
        while y < inner_y_end - 2:
            x = inner_x_start
            while x < inner_x_end - 2:
                # Try skyscraper if there's room
                if y + 6 <= inner_y_end and x + 3 <= inner_x_end and random.random() < 0.7:
                    if place_building(map_array, occupied, x, y, 'skyscraper'):
                        x += 3
                        continue

                # Try other buildings
                building_type = random.choice(['building', 'bank'])
                bw, bh = BUILDING_SIZES[building_type]
                if x + bw <= inner_x_end and y + bh <= inner_y_end:
                    if place_building(map_array, occupied, x, y, building_type):
                        x += bw
                        continue

                x += 1
            y += 3

    elif block_type == 'park':
        # All grass with maybe a pond
        for y in range(inner_y_start, inner_y_end):
            for x in range(inner_x_start, inner_x_end):
                if not occupied[y, x]:
                    map_array[y, x] = TILE_COLORS['grass']
                    occupied[y, x] = True

        # Add small pond if space
        if inner_x_end - inner_x_start > 6 and inner_y_end - inner_y_start > 6:
            pond_x = (inner_x_start + inner_x_end) // 2
            pond_y = (inner_y_start + inner_y_end) // 2
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    py, px = pond_y + dy, pond_x + dx
                    if inner_y_start <= py < inner_y_end and inner_x_start <= px < inner_x_end:
                        map_array[py, px] = TILE_COLORS['water']

    # Fill any remaining empty space with grass
    for y in range(inner_y_start, inner_y_end):
        for x in range(inner_x_start, inner_x_end):
            if not occupied[y, x]:
                map_array[y, x] = TILE_COLORS['grass']
                occupied[y, x] = True


def generate_working_city_map(width=64, height=64, filename='city_map.png'):
    """Generate a city map that actually works with the game"""

    print("Generating working city map...")

    # Initialize map with grass
    map_array = np.zeros((height, width, 3), dtype=np.uint8)
    occupied = np.zeros((height, width), dtype=bool)
    map_array[:, :] = TILE_COLORS['grass']

    # Create road grid
    print("Creating road grid...")
    create_simple_road_grid(map_array, occupied)

    # Define city center
    center_x, center_y = width // 2, height // 2

    # Fill each block created by roads
    print("Filling city blocks...")
    buildings_count = {'house': 0, 'store': 0, 'building': 0, 'bank': 0, 'skyscraper': 0}

    # Process each grid square
    for block_y in range(0, height - 12, 12):
        for block_x in range(0, width - 12, 12):
            # Find actual block boundaries
            x_start = block_x
            y_start = block_y
            x_end = min(block_x + 12, width)
            y_end = min(block_y + 12, height)

            # Skip if too small
            if x_end - x_start < 4 or y_end - y_start < 4:
                continue

            # Determine block type based on distance from center
            block_center_x = (x_start + x_end) // 2
            block_center_y = (y_start + y_end) // 2
            dist = math.sqrt((block_center_x - center_x) ** 2 + (block_center_y - center_y) ** 2)
            max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
            normalized_dist = dist / max_dist

            # Assign block type
            if normalized_dist < 0.2:
                block_type = 'downtown'
            elif normalized_dist < 0.4:
                block_type = 'commercial'
            elif normalized_dist < 0.7:
                block_type = 'residential'
            else:
                # Some suburban blocks are parks
                block_type = 'park' if random.random() < 0.2 else 'residential'

            # Fill the block
            fill_block_with_buildings(map_array, occupied, x_start, y_start, x_end, y_end, block_type)

    # Count buildings placed
    for y in range(height):
        for x in range(width):
            color = tuple(map_array[y, x])
            for building_type, building_color in TILE_COLORS.items():
                if color == building_color and building_type in buildings_count:
                    buildings_count[building_type] += 1

    print("\nBuildings placed:")
    for building_type, count in buildings_count.items():
        if count > 0:
            print(f"  {building_type}: {count // BUILDING_SIZES[building_type][0] // BUILDING_SIZES[building_type][1]}")

    # Save the map
    img = Image.fromarray(map_array, 'RGB')
    img.save(filename)
    print(f"\nCity map saved as '{filename}'")

    return filename


if __name__ == "__main__":
    generate_working_city_map(filename='city_map.png')
    print("\nMap generation complete!")
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


def create_city_roads(map_array, occupied):
    """Create a simple road grid"""
    height, width = map_array.shape[:2]

    # Create road grid with varied spacing
    road_spacing = [10, 12, 14, 16]  # Varied block sizes

    # Vertical roads
    x = 0
    while x < width:
        spacing = random.choice(road_spacing)
        for y in range(height):
            if x < width:
                map_array[y, x] = TILE_COLORS['road']
                occupied[y, x] = True
        x += spacing

    # Horizontal roads
    y = 0
    while y < height:
        spacing = random.choice(road_spacing)
        for x in range(width):
            if y < height:
                map_array[y, x] = TILE_COLORS['road']
                occupied[y, x] = True
        y += spacing

    # Add sidewalks along roads
    for y in range(height):
        for x in range(width):
            if not occupied[y, x]:
                # Check if next to road
                for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < height and 0 <= nx < width and
                            tuple(map_array[ny, nx]) == TILE_COLORS['road']):
                        map_array[y, x] = TILE_COLORS['sidewalk']
                        occupied[y, x] = True
                        break


def get_block_type(x, y, width, height):
    """Determine block type with more variety"""
    center_x, center_y = width // 2, height // 2
    dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
    normalized_dist = dist / max_dist

    # Add some randomness to avoid perfect circles
    normalized_dist += random.uniform(-0.1, 0.1)

    # More varied distribution
    if normalized_dist < 0.15:
        return 'downtown'
    elif normalized_dist < 0.25:
        return random.choice(['downtown', 'commercial'])
    elif normalized_dist < 0.4:
        return 'commercial'
    elif normalized_dist < 0.5:
        return random.choice(['commercial', 'mixed'])
    elif normalized_dist < 0.7:
        return 'mixed'
    elif normalized_dist < 0.85:
        return random.choice(['residential', 'mixed'])
    else:
        return random.choice(['residential', 'park'])


def fill_block_varied(map_array, occupied, x_start, y_start, x_end, y_end, block_type):
    """Fill blocks with more variety and better spacing"""
    inner_x_start = x_start + 1
    inner_y_start = y_start + 1
    inner_x_end = x_end - 1
    inner_y_end = y_end - 1

    block_width = inner_x_end - inner_x_start
    block_height = inner_y_end - inner_y_start

    if block_type == 'downtown':
        # Mix of tall buildings with some spacing
        buildings_placed = 0
        attempts = 0
        max_buildings = (block_width * block_height) // 25  # Less dense

        while buildings_placed < max_buildings and attempts < 50:
            x = random.randint(inner_x_start, max(inner_x_start, inner_x_end - 4))
            y = random.randint(inner_y_start, max(inner_y_start, inner_y_end - 7))

            building_type = random.choices(
                ['skyscraper', 'bank', 'building'],
                weights=[0.5, 0.3, 0.2]
            )[0]

            if place_building(map_array, occupied, x, y, building_type):
                buildings_placed += 1
                # Add small grass or sidewalk around building
                add_building_surroundings(map_array, occupied, x, y, building_type)
            attempts += 1

    elif block_type == 'commercial':
        # Stores and offices with good spacing
        y = inner_y_start
        while y < inner_y_end - 3:
            x = inner_x_start
            while x < inner_x_end - 3:
                if random.random() < 0.6:  # 60% chance to place building
                    building_type = random.choices(
                        ['store', 'building', 'bank'],
                        weights=[0.5, 0.3, 0.2]
                    )[0]

                    if building_type == 'bank' and y + 6 > inner_y_end:
                        building_type = 'building'  # Use smaller building if bank doesn't fit

                    place_building(map_array, occupied, x, y, building_type)
                x += random.randint(5, 7)  # Variable spacing
            y += random.randint(4, 6)

    elif block_type == 'mixed':
        # Mix of houses, stores, and small buildings
        buildings_placed = 0
        max_buildings = (block_width * block_height) // 35

        # Place some larger buildings first
        for _ in range(max_buildings // 3):
            x = random.randint(inner_x_start, max(inner_x_start, inner_x_end - 5))
            y = random.randint(inner_y_start, max(inner_y_start, inner_y_end - 4))
            building_type = random.choice(['store', 'building'])
            place_building(map_array, occupied, x, y, building_type)

        # Fill with houses
        for y in range(inner_y_start, inner_y_end - 3, 5):
            for x in range(inner_x_start, inner_x_end - 3, 5):
                if random.random() < 0.5 and not is_area_occupied(occupied, x, y, 3, 3):
                    place_building(map_array, occupied, x, y, 'house')

    elif block_type == 'residential':
        # Houses with yards and occasional corner store
        # Add a corner store sometimes
        if random.random() < 0.3 and block_width > 8 and block_height > 8:
            store_x = random.choice([inner_x_start, inner_x_end - 4])
            store_y = random.choice([inner_y_start, inner_y_end - 3])
            place_building(map_array, occupied, store_x, store_y, 'store')

        # Place houses in a more organic pattern
        house_spacing = random.randint(4, 6)
        for y in range(inner_y_start, inner_y_end - 3, house_spacing):
            for x in range(inner_x_start, inner_x_end - 3, house_spacing):
                if random.random() < 0.7:  # 70% chance for house
                    # Slight offset for more organic look
                    offset_x = random.randint(-1, 1)
                    offset_y = random.randint(-1, 1)
                    house_x = max(inner_x_start, min(x + offset_x, inner_x_end - 3))
                    house_y = max(inner_y_start, min(y + offset_y, inner_y_end - 3))

                    if not is_area_occupied(occupied, house_x, house_y, 3, 3):
                        place_building(map_array, occupied, house_x, house_y, 'house')

    elif block_type == 'park':
        # Mostly grass with maybe a small building
        if random.random() < 0.2 and block_width > 6 and block_height > 6:
            # Small cafe or house in the park
            x = random.randint(inner_x_start + 1, inner_x_end - 4)
            y = random.randint(inner_y_start + 1, inner_y_end - 4)
            place_building(map_array, occupied, x, y, 'house')

        # Add pond
        if block_width > 8 and block_height > 8:
            pond_x = (inner_x_start + inner_x_end) // 2
            pond_y = (inner_y_start + inner_y_end) // 2
            pond_size = min(3, min(block_width, block_height) // 4)

            for y in range(pond_y - pond_size, pond_y + pond_size):
                for x in range(pond_x - pond_size, pond_x + pond_size):
                    if (inner_x_start <= x < inner_x_end and
                            inner_y_start <= y < inner_y_end):
                        dist = math.sqrt((x - pond_x) ** 2 + (y - pond_y) ** 2)
                        if dist < pond_size:
                            map_array[y, x] = TILE_COLORS['water']
                            occupied[y, x] = True

    # Fill remaining empty space with grass
    for y in range(inner_y_start, inner_y_end):
        for x in range(inner_x_start, inner_x_end):
            if not occupied[y, x]:
                map_array[y, x] = TILE_COLORS['grass']
                occupied[y, x] = True


def is_area_occupied(occupied, x, y, width, height):
    """Check if an area is occupied"""
    for dy in range(height):
        for dx in range(width):
            if y + dy >= occupied.shape[0] or x + dx >= occupied.shape[1]:
                return True
            if occupied[y + dy, x + dx]:
                return True
    return False


def add_building_surroundings(map_array, occupied, x, y, building_type):
    """Add some grass or sidewalk around buildings"""
    width, height = BUILDING_SIZES[building_type]

    # Add grass patches around residential buildings
    if building_type == 'house':
        for dy in range(-1, height + 1):
            for dx in range(-1, width + 1):
                ny, nx = y + dy, x + dx
                if (0 <= ny < map_array.shape[0] and
                        0 <= nx < map_array.shape[1] and
                        not occupied[ny, nx] and
                        random.random() < 0.3):
                    map_array[ny, nx] = TILE_COLORS['grass']
                    occupied[ny, nx] = True


def generate_varied_city_map(width=64, height=64, filename='city_map.png'):
    """Generate a more varied and realistic city map"""

    print("Generating varied city map...")
    print("Features:")
    print("- Better building distribution")
    print("- Mixed-use districts")
    print("- Varied block sizes")
    print("- More organic layouts")

    # Initialize map with grass
    map_array = np.zeros((height, width, 3), dtype=np.uint8)
    occupied = np.zeros((height, width), dtype=bool)
    map_array[:, :] = TILE_COLORS['grass']

    # Create road network
    print("Creating road network...")
    create_city_roads(map_array, occupied)

    # Find and fill blocks
    print("Building city blocks...")
    visited = np.zeros((height, width), dtype=bool)
    blocks_filled = 0

    for y in range(height):
        for x in range(width):
            if not occupied[y, x] and not visited[y, x]:
                # Find block using flood fill
                block_cells = []
                stack = [(x, y)]

                while stack:
                    cx, cy = stack.pop()
                    if (cx < 0 or cx >= width or cy < 0 or cy >= height or
                            visited[cy, cx] or occupied[cy, cx]):
                        continue

                    visited[cy, cx] = True
                    block_cells.append((cx, cy))

                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        stack.append((cx + dx, cy + dy))

                if len(block_cells) < 9:  # Skip tiny blocks
                    continue

                # Get block bounds
                xs = [c[0] for c in block_cells]
                ys = [c[1] for c in block_cells]
                x_start, x_end = min(xs), max(xs) + 1
                y_start, y_end = min(ys), max(ys) + 1

                # Determine block type
                block_center_x = (x_start + x_end) // 2
                block_center_y = (y_start + y_end) // 2
                block_type = get_block_type(block_center_x, block_center_y, width, height)

                # Fill block
                fill_block_varied(map_array, occupied, x_start, y_start, x_end, y_end, block_type)
                blocks_filled += 1

    print(f"Filled {blocks_filled} city blocks")

    # Save the map
    img = Image.fromarray(map_array, 'RGB')
    img.save(filename)
    print(f"\nCity map saved as '{filename}'")

    return filename


if __name__ == "__main__":
    generate_varied_city_map(filename='city_map.png')
    print("\nMap generation complete!")
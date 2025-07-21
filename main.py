import random
from PIL import Image
import numpy as np
from enum import Enum
import math

# Define color mappings for different tile types
TILE_COLORS = {
    # Natural terrain
    'grass': (34, 139, 34),  # Forest green
    'tree': (0, 100, 0),  # Dark green
    'rock': (128, 128, 128),  # Gray
    'water': (0, 119, 190),  # Blue
    'sand': (238, 203, 173),  # Sandy beige
    'dirt': (139, 69, 19),  # Brown
    'deep_water': (0, 80, 150),  # Deep blue
    'snow': (255, 250, 250),  # White
    'mountain': (105, 105, 105),  # Dark gray

    # Modern buildings
    'house': (139, 90, 43),  # Brown house
    'bank': (192, 192, 192),  # Silver/light gray
    'building': (105, 105, 105),  # Dark gray office
    'skyscraper': (70, 130, 180),  # Steel blue
    'store': (255, 140, 0),  # Dark orange
    'factory': (64, 64, 64),  # Dark gray
    'hospital': (255, 255, 255),  # White
    'school': (178, 34, 34),  # Brick red

    # Roads and urban
    'road': (32, 32, 32),  # Asphalt black
    'sidewalk': (190, 190, 190),  # Light gray concrete
}

# Define building sizes (width, height) - must match main.py
BUILDING_SIZES = {
    'house': (2, 2),
    'store': (3, 2),
    'bank': (3, 3),
    'building': (2, 3),
    'skyscraper': (3, 4),
    'factory': (4, 3),
    'hospital': (4, 3),
    'school': (3, 3),
}


class TerrainType(Enum):
    DEEP_WATER = 'deep_water'
    WATER = 'water'
    SAND = 'sand'
    GRASS = 'grass'
    DIRT = 'dirt'
    ROCK = 'rock'
    MOUNTAIN = 'mountain'
    SNOW = 'snow'


def generate_noise_map(width, height, scale=20.0, octaves=6, persistence=0.5, lacunarity=2.0):
    """Generate Perlin-like noise using multiple octaves of random values."""
    noise_map = np.zeros((height, width))

    for octave in range(octaves):
        freq = lacunarity ** octave
        amp = persistence ** octave

        # Generate random gradients
        gradient_width = int(width / scale * freq) + 2
        gradient_height = int(height / scale * freq) + 2
        gradients = np.random.randn(gradient_height, gradient_width, 2)

        # Normalize gradients
        gradient_mag = np.sqrt(gradients[:, :, 0] ** 2 + gradients[:, :, 1] ** 2)
        gradients[:, :, 0] /= gradient_mag
        gradients[:, :, 1] /= gradient_mag

        # Generate noise for this octave
        for y in range(height):
            for x in range(width):
                # Calculate grid coordinates
                x_grid = x / scale * freq
                y_grid = y / scale * freq

                # Get grid cell coordinates
                x0 = int(x_grid)
                y0 = int(y_grid)
                x1 = x0 + 1
                y1 = y0 + 1

                # Calculate interpolation weights
                wx = x_grid - x0
                wy = y_grid - y0

                # Smooth the weights
                wx = wx * wx * (3 - 2 * wx)
                wy = wy * wy * (3 - 2 * wy)

                # Get corner gradients
                g00 = gradients[y0 % gradient_height, x0 % gradient_width]
                g01 = gradients[y1 % gradient_height, x0 % gradient_width]
                g10 = gradients[y0 % gradient_height, x1 % gradient_width]
                g11 = gradients[y1 % gradient_height, x1 % gradient_width]

                # Calculate dot products
                d00 = g00[0] * (x_grid - x0) + g00[1] * (y_grid - y0)
                d01 = g01[0] * (x_grid - x0) + g01[1] * (y_grid - y1)
                d10 = g10[0] * (x_grid - x1) + g10[1] * (y_grid - y0)
                d11 = g11[0] * (x_grid - x1) + g11[1] * (y_grid - y1)

                # Interpolate
                dx0 = d00 * (1 - wx) + d10 * wx
                dx1 = d01 * (1 - wx) + d11 * wx
                value = dx0 * (1 - wy) + dx1 * wy

                noise_map[y, x] += value * amp

    # Normalize to 0-1 range
    noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
    return noise_map


def generate_height_map(width, height):
    """Generate a realistic height map using noise."""
    # Generate base terrain
    height_map = generate_noise_map(width, height, scale=30.0, octaves=6)

    # Add some variety with different scales
    detail = generate_noise_map(width, height, scale=10.0, octaves=4)
    height_map = height_map * 0.7 + detail * 0.3

    # Apply island mask (optional - creates island-like maps)
    use_island_mask = random.random() < 0.3  # 30% chance of island map
    if use_island_mask:
        center_x, center_y = width / 2, height / 2
        max_dist = min(width, height) * 0.45

        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                mask = max(0, 1 - (dist / max_dist) ** 2)
                height_map[y, x] *= mask

    return height_map


def height_to_terrain(height):
    """Convert height value to terrain type."""
    if height < 0.15:
        return TerrainType.DEEP_WATER
    elif height < 0.25:
        return TerrainType.WATER
    elif height < 0.3:
        return TerrainType.SAND
    elif height < 0.55:
        return TerrainType.GRASS
    elif height < 0.65:
        return TerrainType.DIRT
    elif height < 0.75:
        return TerrainType.ROCK
    elif height < 0.85:
        return TerrainType.MOUNTAIN
    else:
        return TerrainType.SNOW


def generate_moisture_map(width, height, height_map):
    """Generate moisture map influenced by water bodies."""
    moisture_map = generate_noise_map(width, height, scale=40.0, octaves=4)

    # Water bodies increase nearby moisture
    water_influence = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            if height_map[y, x] < 0.25:  # Water
                # Spread moisture around water
                for dy in range(-5, 6):
                    for dx in range(-5, 6):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            dist = math.sqrt(dy ** 2 + dx ** 2)
                            if dist > 0:
                                water_influence[ny, nx] += 1.0 / (dist + 1)

    # Normalize and combine
    if water_influence.max() > 0:
        water_influence /= water_influence.max()

    moisture_map = moisture_map * 0.6 + water_influence * 0.4
    return np.clip(moisture_map, 0, 1)


def apply_biome_rules(terrain_type, moisture, height):
    """Apply biome rules based on terrain, moisture, and height."""
    if terrain_type in [TerrainType.DEEP_WATER, TerrainType.WATER]:
        return terrain_type.value

    if terrain_type == TerrainType.SAND:
        # Beaches stay sand near water, become desert inland
        if moisture < 0.3:
            return 'dirt'  # Dry sand/desert
        return 'sand'

    if terrain_type == TerrainType.GRASS:
        # Forests in high moisture areas
        if moisture > 0.65 and random.random() < 0.7:
            return 'tree'
        # Dry grass becomes dirt/savanna
        elif moisture < 0.25:
            return 'dirt'
        return 'grass'

    if terrain_type == TerrainType.DIRT:
        # Some rocks in dry areas
        if moisture < 0.2 and random.random() < 0.3:
            return 'rock'
        return 'dirt'

    return terrain_type.value


def generate_rivers(height_map, moisture_map):
    """Generate rivers that flow from high to low elevation."""
    height, width = height_map.shape
    river_map = np.zeros((height, width), dtype=bool)

    # Start rivers from high moisture mountain areas
    num_rivers = random.randint(2, 5)

    for _ in range(num_rivers):
        # Find a good starting point (high elevation, high moisture)
        candidates = []
        for y in range(height):
            for x in range(width):
                if height_map[y, x] > 0.6 and moisture_map[y, x] > 0.5:
                    candidates.append((x, y))

        if not candidates:
            continue

        start_x, start_y = random.choice(candidates)
        x, y = start_x, start_y

        # Flow downhill
        while 0 <= x < width and 0 <= y < height:
            river_map[y, x] = True

            # Stop if we hit water
            if height_map[y, x] < 0.25:
                break

            # Find lowest neighbor
            min_height = height_map[y, x]
            next_x, next_y = x, y

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if height_map[ny, nx] < min_height:
                        min_height = height_map[ny, nx]
                        next_x, next_y = nx, ny

            # Stop if no downhill path
            if (next_x, next_y) == (x, y):
                break

            x, y = next_x, next_y

    return river_map


def smooth_terrain(map_array, iterations=2):
    """Smooth terrain transitions using cellular automata-like rules."""
    height, width = map_array.shape[:2]

    for _ in range(iterations):
        new_map = map_array.copy()

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Count neighbors of each type
                neighbor_counts = {}
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        color = tuple(map_array[y + dy, x + dx])
                        neighbor_counts[color] = neighbor_counts.get(color, 0) + 1

                # If surrounded by a different tile type, maybe change
                current_color = tuple(map_array[y, x])
                max_count = max(neighbor_counts.values()) if neighbor_counts else 0

                if max_count >= 6:  # If 6+ neighbors are the same type
                    for color, count in neighbor_counts.items():
                        if count == max_count and color != current_color:
                            # Don't change water to land or vice versa easily
                            current_type = None
                            new_type = None

                            for tile_name, tile_color in TILE_COLORS.items():
                                if tuple(tile_color) == current_color:
                                    current_type = tile_name
                                if tuple(tile_color) == color:
                                    new_type = tile_name

                            # Allow transitions between similar types
                            allowed_transitions = {
                                ('grass', 'tree'), ('tree', 'grass'),
                                ('grass', 'dirt'), ('dirt', 'grass'),
                                ('sand', 'grass'), ('grass', 'sand'),
                                ('dirt', 'rock'), ('rock', 'dirt'),
                                ('water', 'deep_water'), ('deep_water', 'water'),
                                ('sand', 'water'), ('water', 'sand'),
                            }

                            if current_type and new_type:
                                if (current_type, new_type) in allowed_transitions or \
                                        (new_type, current_type) in allowed_transitions:
                                    new_map[y, x] = np.array(color)
                            break

        map_array = new_map

    return map_array


def can_place_building(occupied_map, x, y, width, height):
    """Check if a building can be placed at the given position."""
    map_height, map_width = occupied_map.shape

    # Check bounds
    if x + width > map_width or y + height > map_height:
        return False

    # Check if area is free
    for dy in range(height):
        for dx in range(width):
            if occupied_map[y + dy, x + dx]:
                return False

    return True


def mark_building_placed(occupied_map, x, y, width, height):
    """Mark the area as occupied by a building."""
    for dy in range(height):
        for dx in range(width):
            occupied_map[y + dy, x + dx] = True


def generate_realistic_map(width=64, height=64, filename='game_map.png'):
    """Generate a realistic map with proper terrain generation."""
    print("Generating height map...")
    height_map = generate_height_map(width, height)

    print("Generating moisture map...")
    moisture_map = generate_moisture_map(width, height, height_map)

    print("Generating rivers...")
    river_map = generate_rivers(height_map, moisture_map)

    print("Applying biomes...")
    map_array = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            # Get base terrain from height
            terrain = height_to_terrain(height_map[y, x])

            # Apply biome rules
            tile_type = apply_biome_rules(terrain, moisture_map[y, x], height_map[y, x])

            # Override with river if present
            if river_map[y, x] and tile_type not in ['water', 'deep_water']:
                tile_type = 'water'

            # Set color
            map_array[y, x] = TILE_COLORS[tile_type]

    print("Smoothing terrain...")
    map_array = smooth_terrain(map_array, iterations=2)

    # Save the image
    img = Image.fromarray(map_array, 'RGB')
    img.save(filename)
    print(f"Realistic map generated and saved as '{filename}'")

    return filename


def generate_city_map(width=64, height=64, filename='city_map.png'):
    """Generate a modern city map with properly spaced multi-tile buildings."""
    # First generate natural terrain
    height_map = generate_height_map(width, height)
    map_array = np.zeros((height, width, 3), dtype=np.uint8)

    # Fill with base terrain
    for y in range(height):
        for x in range(width):
            h = height_map[y, x]
            if h < 0.2:
                map_array[y, x] = TILE_COLORS['water']
            elif h < 0.25:
                map_array[y, x] = TILE_COLORS['sand']
            else:
                map_array[y, x] = TILE_COLORS['grass']

    # Find suitable area for city (flat land)
    city_mask = np.zeros((height, width), dtype=bool)
    for y in range(height):
        for x in range(width):
            if 0.25 < height_map[y, x] < 0.6:  # Flat land
                city_mask[y, x] = True

    # Create city grid with roads
    block_size = 12  # Larger blocks for multi-tile buildings
    road_width = 2

    # Draw roads only in suitable areas
    for y in range(0, height, block_size + road_width):
        for x in range(width):
            for road_line in range(road_width):
                if y + road_line < height and city_mask[y + road_line, x]:
                    map_array[y + road_line, x] = TILE_COLORS['road']

    for x in range(0, width, block_size + road_width):
        for y in range(height):
            for road_line in range(road_width):
                if x + road_line < width and city_mask[y, x + road_line]:
                    map_array[y, x + road_line] = TILE_COLORS['road']

    # Track occupied spaces for buildings
    occupied = np.zeros((height, width), dtype=bool)

    # Mark roads as occupied
    for y in range(height):
        for x in range(width):
            if tuple(map_array[y, x]) == TILE_COLORS['road']:
                occupied[y, x] = True

    # Fill city blocks with properly spaced buildings
    for block_y in range(0, height, block_size + road_width):
        for block_x in range(0, width, block_size + road_width):
            # Check if this block is in city area
            block_in_city = False
            for y in range(block_y, min(block_y + block_size, height)):
                for x in range(block_x, min(block_x + block_size, width)):
                    if city_mask[y, x]:
                        block_in_city = True
                        break

            if not block_in_city:
                continue

            # Decide block type
            block_type = random.choice(['commercial', 'residential', 'park', 'industrial', 'mixed'])

            # Define building types for each block type
            if block_type == 'commercial':
                building_options = ['building', 'building', 'skyscraper', 'store', 'bank']
            elif block_type == 'residential':
                building_options = ['house', 'house', 'house']
            elif block_type == 'industrial':
                building_options = ['factory', 'factory']
            elif block_type == 'mixed':
                building_options = ['house', 'store', 'building', 'school', 'hospital']
            else:  # park
                building_options = []

            # Place buildings in the block with proper spacing
            block_start_x = block_x + road_width
            block_start_y = block_y + road_width
            block_end_x = min(block_x + block_size, width - 1)
            block_end_y = min(block_y + block_size, height - 1)

            # Add sidewalks around the block
            for y in range(block_start_y - 1, block_end_y + 1):
                for x in range(block_start_x - 1, block_end_x + 1):
                    if 0 <= x < width and 0 <= y < height and not occupied[y, x]:
                        if (y == block_start_y - 1 or y == block_end_y or
                                x == block_start_x - 1 or x == block_end_x):
                            map_array[y, x] = TILE_COLORS['sidewalk']
                            occupied[y, x] = True

            # Try to place buildings
            if building_options:
                # Shuffle to get random placement
                positions = []
                for y in range(block_start_y + 1, block_end_y - 3):
                    for x in range(block_start_x + 1, block_end_x - 3):
                        positions.append((x, y))

                random.shuffle(positions)

                for x, y in positions:
                    if not city_mask[y, x]:
                        continue

                    # Try to place a random building
                    building_type = random.choice(building_options)
                    b_width, b_height = BUILDING_SIZES.get(building_type, (1, 1))

                    if can_place_building(occupied, x, y, b_width, b_height):
                        # Place the building (only mark the base tile with the building color)
                        map_array[y, x] = TILE_COLORS[building_type]

                        # Mark all tiles as occupied
                        mark_building_placed(occupied, x, y, b_width, b_height)

                        # Add some spacing between buildings
                        buffer = 1
                        for dy in range(-buffer, b_height + buffer):
                            for dx in range(-buffer, b_width + buffer):
                                if (0 <= x + dx < width and 0 <= y + dy < height and
                                        not occupied[y + dy, x + dx]):
                                    if block_type == 'residential':
                                        # Grass around houses
                                        map_array[y + dy, x + dx] = TILE_COLORS['grass']
                                    else:
                                        # Sidewalk around other buildings
                                        map_array[y + dy, x + dx] = TILE_COLORS['sidewalk']
                                    occupied[y + dy, x + dx] = True

            elif block_type == 'park':
                # Fill with grass and trees
                for y in range(block_start_y, block_end_y):
                    for x in range(block_start_x, block_end_x):
                        if city_mask[y, x] and not occupied[y, x]:
                            if random.random() < 0.15:
                                map_array[y, x] = TILE_COLORS['tree']
                            else:
                                map_array[y, x] = TILE_COLORS['grass']

    # Save the image
    img = Image.fromarray(map_array, 'RGB')
    img.save(filename)
    print(f"City map generated and saved as '{filename}'")

    return filename


if __name__ == "__main__":
    # Generate different types of maps
    print("1. Generating realistic terrain map...")
    generate_realistic_map()

    print("\n2. Generating city map...")
    generate_city_map(filename='city_map.png')

    print("\nMaps generated successfully!")
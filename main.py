import random
from PIL import Image
import numpy as np
import math
from collections import deque
from enum import Enum

# Define color mappings
TILE_COLORS = {
    'grass': (34, 139, 34),
    'water': (0, 119, 190),
    'road': (32, 32, 32),
    'sidewalk': (190, 190, 190),
    'house': (139, 90, 43),
    'building': (105, 105, 105),
    'store': (255, 140, 0),
    'skyscraper': (70, 130, 180),
    'bank': (192, 192, 192),
}

# Building sizes
BUILDING_SIZES = {
    'house': (3, 3),
    'store': (4, 3),
    'bank': (3, 6),
    'building': (3, 3),
    'skyscraper': (3, 6),
}


class RoadType(Enum):
    HIGHWAY = 3
    MAIN = 2
    LOCAL = 1


class L_System_City_Generator:
    """
    Uses L-System (Lindenmayer System) for road generation,
    similar to Parish and Müller's approach used in CityEngine
    """

    def __init__(self, width=64, height=64):
        self.width = width
        self.height = height
        self.map_array = np.zeros((height, width, 3), dtype=np.uint8)
        self.occupied = np.zeros((height, width), dtype=bool)
        self.map_array[:, :] = TILE_COLORS['grass']

        # For L-System road generation
        self.road_segments = deque()
        self.placed_segments = []
        self.intersections = {}
        self.downtown_area = []  # Track downtown interior

        # Population density map (using Perlin-like noise simulation)
        self.population_map = self.generate_population_map()

    def generate_population_map(self):
        """Generate population density map with strong downtown center"""
        pop_map = np.zeros((self.height, self.width))

        # Main downtown center - much stronger now
        center_x, center_y = self.width // 2, self.height // 2

        # Create a strong central business district
        for y in range(self.height):
            for x in range(self.width):
                # Distance from center
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

                # Downtown core (very high density)
                if dist < 8:
                    pop_map[y, x] = 1.0
                # Inner city (high density)
                elif dist < 15:
                    pop_map[y, x] = 0.85 - (dist - 8) * 0.05
                # Urban area (medium-high density)
                elif dist < 25:
                    pop_map[y, x] = 0.5 - (dist - 15) * 0.03
                # Suburban (low density)
                else:
                    pop_map[y, x] = max(0.2 - (dist - 25) * 0.01, 0.1)

        # Add some secondary centers for variety
        secondary_centers = [
            (self.width // 4, self.height // 3, 0.3),
            (3 * self.width // 4, 2 * self.height // 3, 0.3),
        ]

        for cx, cy, strength in secondary_centers:
            for y in range(self.height):
                for x in range(self.width):
                    dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    if dist < 10:
                        additional = strength * math.exp(-dist / 5)
                        pop_map[y, x] = min(pop_map[y, x] + additional, 0.6)

        return pop_map

    def generate(self):
        """Generate city using L-System approach"""
        print("Generating city using L-System algorithm...")
        print("Based on Parish and Müller's procedural city generation")

        # Step 1: Generate road network using L-System
        self.generate_road_network()

        # Step 2: Fill downtown area with buildings first
        self.fill_downtown()

        # Step 3: Find blocks (parcels) outside downtown
        blocks = self.find_blocks()

        # Step 4: Subdivide blocks into lots
        lots = self.subdivide_blocks(blocks)

        # Step 5: Place buildings on lots
        self.place_buildings(lots)

        # Step 6: Add parks and features
        self.add_city_features()

        return self.map_array

    def fill_downtown(self):
        """Fill the circular downtown area with skyscrapers and banks"""
        center_x, center_y = self.width // 2, self.height // 2

        # Group downtown area into small lots for building placement
        downtown_lots = []
        used = set()

        for x, y in self.downtown_area:
            if (x, y) not in used:
                # Create a small lot around this point
                lot = []
                for dx in range(4):
                    for dy in range(4):
                        nx, ny = x + dx, y + dy
                        if (nx, ny) in self.downtown_area and (nx, ny) not in used:
                            lot.append((nx, ny))
                            used.add((nx, ny))

                if len(lot) >= 9:  # Minimum size for a building
                    downtown_lots.append(lot)

        # Place buildings in downtown lots
        for lot in downtown_lots:
            # Downtown is all skyscrapers and banks
            building_types = ['skyscraper', 'skyscraper', 'skyscraper', 'bank']
            weights = [0.7, 0.15, 0.1, 0.05]

            building_type = random.choices(building_types, weights=weights)[0]

            # Get lot bounds
            xs = [p[0] for p in lot]
            ys = [p[1] for p in lot]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            bw, bh = BUILDING_SIZES[building_type]

            # Try to place building
            if max_x - min_x >= bw and max_y - min_y >= bh:
                x = min_x
                y = min_y

                # Check if area is free
                can_place = True
                for dy in range(bh):
                    for dx in range(bw):
                        if (y + dy >= self.height or x + dx >= self.width or
                                self.occupied[y + dy, x + dx]):
                            can_place = False
                            break
                    if not can_place:
                        break

                # Place building
                if can_place:
                    for dy in range(bh):
                        for dx in range(bw):
                            self.map_array[y + dy, x + dx] = TILE_COLORS[building_type]
                            self.occupied[y + dy, x + dx] = True

    def generate_road_network(self):
        """Generate roads using L-System growth"""
        # Initialize with main highways
        center_x, center_y = self.width // 2, self.height // 2

        # Add initial road segments (axiom) - but stop them at downtown circle
        downtown_radius = 12

        # East-West highway (split by downtown)
        self.road_segments.append({
            'start': (0, center_y),
            'end': (center_x - downtown_radius - 2, center_y),
            'type': RoadType.HIGHWAY,
            'time': 0
        })
        self.road_segments.append({
            'start': (center_x + downtown_radius + 2, center_y),
            'end': (self.width - 1, center_y),
            'type': RoadType.HIGHWAY,
            'time': 0
        })

        # North-South highway (split by downtown)
        self.road_segments.append({
            'start': (center_x, 0),
            'end': (center_x, center_y - downtown_radius - 2),
            'type': RoadType.HIGHWAY,
            'time': 0
        })
        self.road_segments.append({
            'start': (center_x, center_y + downtown_radius + 2),
            'end': (center_x, self.height - 1),
            'type': RoadType.HIGHWAY,
            'time': 0
        })

        # Create main ring road around downtown
        num_points = 32
        ring_points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            x = int(center_x + downtown_radius * math.cos(angle))
            y = int(center_y + downtown_radius * math.sin(angle))
            if 0 <= x < self.width and 0 <= y < self.height:
                ring_points.append((x, y))

        # Connect the points to form the main ring road
        for i in range(len(ring_points)):
            start = ring_points[i]
            end = ring_points[(i + 1) % len(ring_points)]
            self.road_segments.append({
                'start': start,
                'end': end,
                'type': RoadType.MAIN,
                'time': 1
            })

        # Add connecting roads from highways to ring road
        # Connect E-W highway to ring
        self.road_segments.append({
            'start': (center_x - downtown_radius - 2, center_y),
            'end': (center_x - downtown_radius, center_y),
            'type': RoadType.MAIN,
            'time': 1
        })
        self.road_segments.append({
            'start': (center_x + downtown_radius, center_y),
            'end': (center_x + downtown_radius + 2, center_y),
            'type': RoadType.MAIN,
            'time': 1
        })

        # Connect N-S highway to ring
        self.road_segments.append({
            'start': (center_x, center_y - downtown_radius - 2),
            'end': (center_x, center_y - downtown_radius),
            'type': RoadType.MAIN,
            'time': 1
        })
        self.road_segments.append({
            'start': (center_x, center_y + downtown_radius),
            'end': (center_x, center_y + downtown_radius + 2),
            'type': RoadType.MAIN,
            'time': 1
        })

        # Mark downtown area as special (not occupied by roads)
        self.downtown_area = []
        for y in range(center_y - downtown_radius + 2, center_y + downtown_radius - 1):
            for x in range(center_x - downtown_radius + 2, center_x + downtown_radius - 1):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if dist < downtown_radius - 2:
                    self.downtown_area.append((x, y))

        # Process segments using priority queue (by time)
        iteration = 0
        while self.road_segments and iteration < 200:
            # Get segment with minimum time
            self.road_segments = deque(sorted(self.road_segments, key=lambda s: s['time']))
            segment = self.road_segments.popleft()

            # Check local constraints
            if self.check_local_constraints(segment):
                # Place segment
                self.place_road_segment(segment)
                self.placed_segments.append(segment)

                # Apply global goals (generate new segments)
                new_segments = self.apply_global_goals(segment)
                self.road_segments.extend(new_segments)

            iteration += 1

        # Add sidewalks
        self.add_sidewalks()

    def check_local_constraints(self, segment):
        """Check if segment can be placed (avoid conflicts)"""
        # Simplified - just check if endpoints are in bounds
        start_x, start_y = segment['start']
        end_x, end_y = segment['end']

        if not (0 <= start_x < self.width and 0 <= start_y < self.height):
            return False
        if not (0 <= end_x < self.width and 0 <= end_y < self.height):
            return False

        return True

    def place_road_segment(self, segment):
        """Place a road segment on the map"""
        start_x, start_y = segment['start']
        end_x, end_y = segment['end']

        # Draw line between points
        points = self.bresenham_line(start_x, start_y, end_x, end_y)

        for x, y in points:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.map_array[y, x] = TILE_COLORS['road']
                self.occupied[y, x] = True

                # Make highways wider
                if segment['type'] == RoadType.HIGHWAY:
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            self.map_array[ny, nx] = TILE_COLORS['road']
                            self.occupied[ny, nx] = True

    def bresenham_line(self, x0, y0, x1, y1):
        """Bresenham's line algorithm"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            points.append((x0, y0))

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return points

    def apply_global_goals(self, segment):
        """Generate new road segments based on population density"""
        new_segments = []
        end_x, end_y = segment['end']

        # Only branch from non-highway roads
        if segment['type'] != RoadType.HIGHWAY:
            return new_segments

        # Sample population density around endpoint
        if 0 <= end_x < self.width and 0 <= end_y < self.height:
            density = self.population_map[end_y, end_x]

            # Higher density = more branches
            if density > 0.3 and random.random() < density:
                # Branch perpendicular to current segment
                dx = segment['end'][0] - segment['start'][0]
                dy = segment['end'][1] - segment['start'][1]

                # Perpendicular directions
                if abs(dx) > abs(dy):  # Horizontal road
                    branches = [(0, 10), (0, -10)]
                else:  # Vertical road
                    branches = [(10, 0), (-10, 0)]

                for bdx, bdy in branches:
                    if random.random() < 0.5:
                        new_end = (end_x + bdx, end_y + bdy)
                        new_segments.append({
                            'start': (end_x, end_y),
                            'end': new_end,
                            'type': RoadType.MAIN,
                            'time': segment['time'] + 1
                        })

        return new_segments

    def add_sidewalks(self):
        """Add sidewalks along all roads"""
        for y in range(self.height):
            for x in range(self.width):
                if not self.occupied[y, x]:
                    # Check if next to road
                    for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < self.height and 0 <= nx < self.width and
                                tuple(self.map_array[ny, nx]) == TILE_COLORS['road']):
                            self.map_array[y, x] = TILE_COLORS['sidewalk']
                            self.occupied[y, x] = True
                            break

    def find_blocks(self):
        """Find city blocks (areas bounded by roads)"""
        visited = np.zeros((self.height, self.width), dtype=bool)
        blocks = []

        # Mark downtown as visited so it's not included in blocks
        for x, y in self.downtown_area:
            visited[y, x] = True

        for y in range(self.height):
            for x in range(self.width):
                if not self.occupied[y, x] and not visited[y, x]:
                    # Flood fill to find block
                    block = []
                    stack = [(x, y)]

                    while stack:
                        cx, cy = stack.pop()
                        if (cx < 0 or cx >= self.width or cy < 0 or cy >= self.height or
                                visited[cy, cx] or self.occupied[cy, cx]):
                            continue

                        visited[cy, cx] = True
                        block.append((cx, cy))

                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            stack.append((cx + dx, cy + dy))

                    if len(block) > 20:  # Minimum block size
                        blocks.append(block)

        return blocks

    def subdivide_blocks(self, blocks):
        """Subdivide blocks into building lots using OBB algorithm"""
        all_lots = []

        for block in blocks:
            # Get block bounds
            xs = [p[0] for p in block]
            ys = [p[1] for p in block]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            # Get center of block to determine lot size
            center_x = (min_x + max_x) // 2
            center_y = (min_y + max_y) // 2

            # Downtown gets smaller lots for more buildings
            dist_from_center = math.sqrt((center_x - self.width // 2) ** 2 + (center_y - self.height // 2) ** 2)

            if dist_from_center < 10:
                lot_size = 5  # Small lots in downtown core
            elif dist_from_center < 18:
                lot_size = 6  # Medium lots in inner city
            else:
                lot_size = 8  # Larger lots in suburbs

            for y in range(min_y, max_y, lot_size):
                for x in range(min_x, max_x, lot_size):
                    lot = []
                    for ly in range(y, min(y + lot_size, max_y)):
                        for lx in range(x, min(x + lot_size, max_x)):
                            if (lx, ly) in block:
                                lot.append((lx, ly))

                    if len(lot) > 8:  # Smaller minimum lot size for downtown
                        all_lots.append(lot)

        return all_lots

    def place_buildings(self, lots):
        """Place buildings on lots based on location"""
        for lot in lots:
            # Get lot center
            center_x = sum(p[0] for p in lot) // len(lot)
            center_y = sum(p[1] for p in lot) // len(lot)

            # Get lot bounds
            xs = [p[0] for p in lot]
            ys = [p[1] for p in lot]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            # Determine building type based on population density
            density = self.population_map[center_y, center_x]

            # Distance from city center
            dist_from_center = math.sqrt((center_x - self.width // 2) ** 2 + (center_y - self.height // 2) ** 2)

            # Downtown core - force skyscrapers
            if dist_from_center < 8:
                # Very center - only skyscrapers and banks
                building_types = ['skyscraper', 'skyscraper', 'skyscraper', 'bank']
                weights = [0.7, 0.2, 0.05, 0.05]
            elif dist_from_center < 12:
                # Inner downtown - mostly skyscrapers
                building_types = ['skyscraper', 'skyscraper', 'bank', 'building']
                weights = [0.5, 0.3, 0.1, 0.1]
            elif density > 0.7 or dist_from_center < 18:
                # High density - mix of tall buildings
                building_types = ['skyscraper', 'bank', 'building', 'store']
                weights = [0.3, 0.3, 0.2, 0.2]
            elif density > 0.4:
                # Medium density - commercial
                building_types = ['store', 'building', 'bank', 'house']
                weights = [0.4, 0.3, 0.2, 0.1]
            else:
                # Low density - residential
                building_types = ['house', 'house', 'store']
                weights = [0.7, 0.2, 0.1]

            # In downtown, try to place multiple buildings per lot
            if dist_from_center < 15:
                # Calculate how many buildings can fit
                lot_width = max_x - min_x
                lot_height = max_y - min_y

                # Try to place buildings in a grid pattern within the lot
                placed_count = 0
                for attempt in range(3):  # Try up to 3 buildings per lot
                    building_type = random.choices(building_types, weights=weights)[0]
                    bw, bh = BUILDING_SIZES[building_type]

                    # Try different positions
                    positions = []

                    # If lot is big enough, create a grid of positions
                    if lot_width >= bw * 2 and lot_height >= bh:
                        positions.extend([
                            (min_x, min_y),
                            (max_x - bw, min_y),
                        ])
                    if lot_width >= bw and lot_height >= bh * 2:
                        positions.extend([
                            (min_x, min_y),
                            (min_x, max_y - bh),
                        ])

                    # Always try center
                    positions.append((min_x + (lot_width - bw) // 2, min_y + (lot_height - bh) // 2))

                    # Try random positions too
                    for _ in range(3):
                        if lot_width > bw and lot_height > bh:
                            rx = min_x + random.randint(0, lot_width - bw)
                            ry = min_y + random.randint(0, lot_height - bh)
                            positions.append((rx, ry))

                    # Try to place building
                    for x, y in positions:
                        if self.place_building(x, y, building_type):
                            placed_count += 1
                            break

                    if placed_count >= 2:  # Don't overcrowd
                        break
            else:
                # Outside downtown, single building per lot
                building_type = random.choices(building_types, weights=weights)[0]
                bw, bh = BUILDING_SIZES[building_type]

                if min_x + bw <= max_x and min_y + bh <= max_y:
                    x = min_x + (max_x - min_x - bw) // 2
                    y = min_y + (max_y - min_y - bh) // 2
                    self.place_building(x, y, building_type)

    def place_building(self, x, y, building_type):
        """Place a single building"""
        width, height = BUILDING_SIZES[building_type]
        color = TILE_COLORS[building_type]

        # Check if area is free
        for dy in range(height):
            for dx in range(width):
                if (y + dy >= self.height or x + dx >= self.width or
                        self.occupied[y + dy, x + dx]):
                    return False

        # Place building
        for dy in range(height):
            for dx in range(width):
                self.map_array[y + dy, x + dx] = color
                self.occupied[y + dy, x + dx] = True

        # Add some grass around houses (but not in downtown)
        if building_type == 'house':
            center_dist = math.sqrt((x - self.width // 2) ** 2 + (y - self.height // 2) ** 2)
            if center_dist > 20:  # Only add grass in suburbs
                for dy in range(-1, height + 1):
                    for dx in range(-1, width + 1):
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < self.height and 0 <= nx < self.width and
                                not self.occupied[ny, nx] and random.random() < 0.5):
                            self.map_array[ny, nx] = TILE_COLORS['grass']
                            self.occupied[ny, nx] = True

        return True

    def add_city_features(self):
        """Add parks and other features"""
        # Find suitable locations for parks (not in downtown)
        for _ in range(2):
            # Random location in low-density area
            attempts = 0
            while attempts < 50:
                x = random.randint(10, self.width - 10)
                y = random.randint(10, self.height - 10)

                # Don't place parks in downtown
                dist_from_center = math.sqrt((x - self.width // 2) ** 2 + (y - self.height // 2) ** 2)

                if self.population_map[y, x] < 0.3 and not self.occupied[y, x] and dist_from_center > 20:
                    # Create park
                    park_size = 5
                    for py in range(y - park_size, y + park_size):
                        for px in range(x - park_size, x + park_size):
                            if (0 <= py < self.height and 0 <= px < self.width and
                                    not self.occupied[py, px]):
                                self.map_array[py, px] = TILE_COLORS['grass']
                                self.occupied[py, px] = True

                    # Add pond
                    for py in range(y - 1, y + 2):
                        for px in range(x - 1, x + 2):
                            if 0 <= py < self.height and 0 <= px < self.width:
                                self.map_array[py, px] = TILE_COLORS['water']
                    break

                attempts += 1

        # Fill remaining empty spaces
        for y in range(self.height):
            for x in range(self.width):
                if not self.occupied[y, x]:
                    self.map_array[y, x] = TILE_COLORS['grass']


def generate_l_system_city(width=64, height=64, filename='city_map.png'):
    """Generate city using L-System algorithm"""
    generator = L_System_City_Generator(width, height)
    map_array = generator.generate()

    # Save the map
    img = Image.fromarray(map_array, 'RGB')
    img.save(filename)
    print(f"\nL-System city map saved as '{filename}'")

    return filename


if __name__ == "__main__":
    # Generate using L-System (industry standard algorithm)
    generate_l_system_city(filename='city_map.png')
    print("\nMap generation complete!")
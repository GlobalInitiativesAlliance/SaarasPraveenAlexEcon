"""
Diagnostic script to check what's at position (54,33) in the map
"""

import json
import sys
import os

# Check the city map data
print("Checking position (54,33) in city map...")
print("-" * 50)

# Load city map data
with open("data/maps/city_map_data.json", 'r') as f:
    map_data = json.load(f)

# Get map dimensions
width = map_data.get('width', 0)
height = map_data.get('height', 0)
print(f"Map size: {width}x{height}")

# Check if (54,33) is in bounds
if 54 < width and 33 < height:
    print(f"Position (54,33) is within map bounds")

    # Get the tile data at position (54,33)
    tiles = map_data.get('map_data', [])
    if tiles and 33 < len(tiles) and 54 < len(tiles[33]):
        tile_data = tiles[33][54]
        print(f"\nTile data at (54,33): {tile_data}")

        if tile_data:
            if isinstance(tile_data, list) or isinstance(tile_data, tuple):
                if len(tile_data) > 0:
                    print(f"  Tile type: {tile_data[0]}")
                    if tile_data[0] in ['building', 'building_with_bg']:
                        print(f"  ✓ This is a building tile!")
                        if len(tile_data) > 1:
                            print(f"  Building name: {tile_data[1]}")
                    else:
                        print(f"  ✗ This is NOT a building tile")
            else:
                print(f"  Raw value: {tile_data}")
        else:
            print("  Tile is None/empty")
    else:
        print("  ERROR: Tiles array doesn't have this position")
else:
    print(f"Position (54,33) is OUT OF BOUNDS")

# Check building interiors mapping
print("\n" + "-" * 50)
print("Checking building_interiors.json...")

with open("data/maps/building_interiors.json", 'r') as f:
    interiors = json.load(f)

if "54,33" in interiors:
    print(f"✓ Position 54,33 is mapped to: {interiors['54,33']}")
else:
    print("✗ Position 54,33 is NOT in building_interiors.json")

# Check for nearby buildings
print("\n" + "-" * 50)
print("Checking nearby positions for buildings...")

for dy in range(-2, 3):
    for dx in range(-2, 3):
        x = 54 + dx
        y = 33 + dy
        if 0 <= x < width and 0 <= y < height:
            if y < len(tiles) and x < len(tiles[y]):
                tile = tiles[y][x]
                if tile and isinstance(tile, (list, tuple)) and len(tile) > 0:
                    if tile[0] in ['building', 'building_with_bg']:
                        print(f"  Building found at ({x},{y}): {tile[1] if len(tile) > 1 else 'unnamed'}")
#!/usr/bin/env python3
"""Test script to verify map loading without running the full game"""

import pygame
import sys
sys.path.insert(0, './src')

from core.game_world import CityMap, TileManager

# Initialize pygame (needed for image loading)
pygame.init()

# Create tile manager and city map
tile_manager = TileManager()
city_map = CityMap()

# Set the tile manager and load the map
city_map.tile_manager = tile_manager
city_map.load_from_image()

# Check results
print(f"\n=== Map Loading Test Results ===")
print(f"Map dimensions: {city_map.width}x{city_map.height}")
print(f"Building tiles found: {len(city_map.building_tiles)}")
print(f"Building data available: {hasattr(tile_manager, 'building_data') and len(tile_manager.building_data) if hasattr(tile_manager, 'building_data') else 'No'}")

# Debug building data
if hasattr(tile_manager, 'building_data'):
    print(f"\nBuilding definitions in tile_manager:")
    for key, data in tile_manager.building_data.items():
        print(f"  {key}: category={data.get('category')}, size={data.get('size')}")

# Count different tile types
tile_counts = {}
for y in range(city_map.height):
    for x in range(city_map.width):
        tile = city_map.map_data[y][x]
        if isinstance(tile, tuple):
            tile_type = tile[0]
        else:
            tile_type = tile
        
        tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1

print(f"\nTile type counts:")
for tile_type, count in sorted(tile_counts.items()):
    print(f"  {tile_type}: {count}")

# Check if any buildings were detected
building_types = [k for k in tile_counts.keys() if k and 'building' in str(k)]
if building_types:
    print(f"\nBuilding detection: SUCCESS ✓")
    print(f"Building types found: {building_types}")
else:
    print(f"\nBuilding detection: FAILED ✗")
    print("No buildings were detected in the map")

pygame.quit()
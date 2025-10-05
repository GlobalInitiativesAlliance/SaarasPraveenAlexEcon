#!/usr/bin/env python3
"""Analyze the colors in city_map.png"""

import pygame
from collections import Counter

# Initialize pygame
pygame.init()

# Load the map
map_image = pygame.image.load("assets/images/city_map.png")
width, height = map_image.get_size()

# Collect all unique colors
color_counts = Counter()

for y in range(height):
    for x in range(width):
        color = map_image.get_at((x, y))
        color_tuple = (color.r, color.g, color.b)
        color_counts[color_tuple] += 1

# Print the most common colors
print(f"Map size: {width}x{height}")
print(f"Total unique colors: {len(color_counts)}")
print("\nMost common colors (RGB):")

for color, count in color_counts.most_common(20):
    percentage = (count / (width * height)) * 100
    print(f"  {color}: {count} pixels ({percentage:.1f}%)")

# Check for specific building colors
print("\nChecking for expected building colors:")
BUILDING_COLORS = {
    (139, 90, 43): 'house',
    (192, 192, 192): 'bank', 
    (105, 105, 105): 'building',
    (70, 130, 180): 'skyscraper',
    (255, 140, 0): 'store',
}

for color, name in BUILDING_COLORS.items():
    if color in color_counts:
        print(f"  {name} {color}: {color_counts[color]} pixels")
    else:
        print(f"  {name} {color}: NOT FOUND")

pygame.quit()
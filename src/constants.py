import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
FPS = 60
UI_HEIGHT = 60

# Colors
BACKGROUND_COLOR = (50, 50, 50)
GRID_COLOR = (70, 70, 70)
UI_BACKGROUND = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)
PLAYER_COLOR = (255, 0, 0)
CUTSCENE_OVERLAY = (0, 0, 0, 180)
CUTSCENE_TEXT_BG = (20, 20, 20, 220)

# Isometric rendering mode flag
ISOMETRIC_MODE = True  # Set to False to use original top-down rendering

# Isometric tile dimensions (2:1 ratio diamond)
ISO_TILE_WIDTH = 128
ISO_TILE_HEIGHT = 64

# Isometric map dimensions (smaller for denser layout)
ISO_MAP_WIDTH = 32
ISO_MAP_HEIGHT = 32

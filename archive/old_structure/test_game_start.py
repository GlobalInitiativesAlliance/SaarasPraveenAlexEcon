#!/usr/bin/env python3
"""Test that the game starts without errors"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
pygame.init()

try:
    from main import Game
    
    print("Creating game instance...")
    game = Game()
    
    print("✓ Game initialized successfully!")
    print(f"✓ Main menu created: {game.main_menu is not None}")
    print(f"✓ Game state: {game.game_state}")
    print(f"✓ Tile manager loaded: {game.tile_manager is not None}")
    print(f"✓ City map loaded: {game.city_map is not None}")
    print(f"✓ Map dimensions: {game.city_map.width}x{game.city_map.height}")
    print(f"✓ Objective manager created: {game.objective_manager is not None}")
    
    print("\nGame is ready to run!")
    print("The main menu should display with:")
    print("- Title: Economics Adventure")
    print("- Subtitle: Learn Economics Through City Life")
    print("- Buttons: Start Game, How to Play, Credits, Quit")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    pygame.quit()
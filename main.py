#!/usr/bin/env python3
"""
Economics Adventure Game - Web Version
Main entry point for pygbag web deployment
"""

import asyncio
import pygame
import sys
import os

#here to be here

# Initialize Pygame
pygame.init()

# Add src to path so imports work  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import the game
from src.main import Game

async def main():
    """Main entry point for the web version"""
    print("Starting Economics Adventure Game (Web Version)...")
    
    # Create and run the game
    game = Game()
    await game.run()

# This is required for pygbag
if __name__ == "__main__":
    asyncio.run(main())

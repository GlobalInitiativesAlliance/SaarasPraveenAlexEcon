"""
Test script for Foster Home narrative interior
"""
import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game_world import ObjectiveManager
from src.interiors.narratives.foster_home_narrative import FosterHomeNarrative
from part_1_housing_stability.objectives_narrative import get_part1_narrative_objectives

# Initialize Pygame
pygame.init()

# Create screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Foster Home Narrative Test")

# Create a minimal game object
class MockGame:
    def __init__(self):
        self.objective_manager = ObjectiveManager(self)
        self.objectives = get_part1_narrative_objectives()
        self.objective_manager.objectives = self.objectives
        self.objective_manager.current_objective_index = 0
        self.objective_manager.activate_current_objective()

# Create game and interior
game = MockGame()

# Load foster home room data
import json
room_data_path = "data/interiors/rooms/foster_home.json"
with open(room_data_path, 'r') as f:
    room_data = json.load(f)

# Create foster home interior
foster_home = FosterHomeNarrative(game, room_data, (29, 39))
foster_home.enter()

# Game loop
clock = pygame.time.Clock()
running = True

print("\n=== FOSTER HOME NARRATIVE TEST ===")
print("Controls:")
print("- Arrow keys/WASD: Move")
print("- E: Interact with objects")
print("- SPACE: Continue dialogue")
print("- ESC: Exit")
print("\nObjective:", game.objective_manager.get_current_objective().title)
print("Description:", game.objective_manager.get_current_objective().description)
print("================================\n")

while running:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not foster_home.active:
                running = False
            else:
                foster_home.handle_event(event)

    # Handle continuous input
    keys = pygame.key.get_pressed()
    foster_home.handle_input(keys)

    # Update
    foster_home.update(dt)

    # Check if objective was completed
    current_obj = game.objective_manager.get_current_objective()
    if current_obj and current_obj.completed:
        print(f"✓ Completed: {current_obj.title}")
        # Activate next objective if available
        if game.objective_manager.current_objective_index < len(game.objectives) - 1:
            game.objective_manager.current_objective_index += 1
            game.objective_manager.activate_current_objective()
            new_obj = game.objective_manager.get_current_objective()
            print(f"\nNew Objective: {new_obj.title}")
            print(f"Description: {new_obj.description}")

            # Restart the narrative for the new objective
            foster_home.check_for_objective_narrative()

    # Draw
    screen.fill((20, 20, 30))
    foster_home.draw(screen)

    # Draw objective info at top
    font = pygame.font.Font(None, 24)
    obj = game.objective_manager.get_current_objective()
    if obj:
        obj_text = f"Objective: {obj.title}"
        obj_surf = font.render(obj_text, True, (255, 220, 100))
        screen.blit(obj_surf, (10, 10))

    pygame.display.flip()

pygame.quit()
print("\nTest completed!")
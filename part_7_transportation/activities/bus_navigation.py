"""Bus Navigation Game - Navigate complex transit system"""

import pygame
from shared.constants import *

class BusNavigationGame:
    """Try to get to work using buses"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        self.transfers = 0
        self.time_elapsed = 0
        
    def start(self):
        self.active = True
        self.completed = False
        
    def handle_key(self, key):
        if key == pygame.K_SPACE:
            self.transfers += 1
            if self.transfers >= 3:
                self.end_game()
                
    def update(self, dt):
        self.time_elapsed += dt
        
    def end_game(self):
        self.active = False
        self.completed = True
        
    def draw(self, screen):
        if not self.active:
            return
        screen.fill((240, 240, 250))
        
    def get_results(self):
        return {
            'energy': -20,
            'message': "2 hour commute each way",
            'color': (255, 200, 100)
        }

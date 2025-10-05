"""Food Bank Line Game - Wait in line for food assistance"""

import pygame
from shared.constants import *

class FoodBankLineGame:
    """Stand in line at food bank"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        self.wait_time = 0
        self.position_in_line = 50
        
    def start(self):
        self.active = True
        self.completed = False
        
    def update(self, dt):
        self.wait_time += dt
        self.position_in_line = max(0, self.position_in_line - dt * 0.5)
        if self.position_in_line <= 0:
            self.end_game()
            
    def handle_key(self, key):
        pass
        
    def end_game(self):
        self.active = False
        self.completed = True
        
    def draw(self, screen):
        if not self.active:
            return
        screen.fill((240, 240, 250))
        
    def get_results(self):
        return {
            'hunger': -30,
            'message': "Got food for 3 days",
            'color': (100, 255, 100)
        }

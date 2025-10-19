"""Court Navigation Game - Navigate the legal system"""

import pygame
from shared.constants import *

class CourtNavigationGame:
    """Find the right courtroom and navigate bureaucracy"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        self.rooms_checked = 0
        self.correct_room = 5
        
    def start(self):
        self.active = True
        self.completed = False
        
    def handle_key(self, key):
        if pygame.K_1 <= key <= pygame.K_9:
            self.rooms_checked += 1
            if self.rooms_checked == self.correct_room:
                self.end_game()
                
    def update(self, dt):
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
            'stress': 15,
            'message': "Made it to court on time",
            'color': (255, 255, 100)
        }

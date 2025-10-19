"""Credit Application Game - Navigate credit checks and denials"""

import pygame
import random
from shared.constants import *

class CreditApplicationGame:
    """Experience credit application rejections"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        self.applications_sent = 0
        self.rejections = 0
        self.credit_score = 0  # Unknown to player
        self.selected_apartment = 0
        self.apartments = []
        self.fonts = {
            'title': pygame.font.Font(None, 36),
            'normal': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 20)
        }
        
    def start(self):
        self.active = True
        self.completed = False
        self.generate_apartments()
        
    def generate_apartments(self):
        self.apartments = [
            {'name': 'Luxury Complex', 'rent': 1800, 'required_score': 750},
            {'name': 'Downtown Loft', 'rent': 1500, 'required_score': 700},
            {'name': 'Standard Apartment', 'rent': 1200, 'required_score': 650},
            {'name': 'Budget Studios', 'rent': 900, 'required_score': 600},
            {'name': 'Sketchy Place', 'rent': 700, 'required_score': 500}
        ]
        
    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selected_apartment = max(0, self.selected_apartment - 1)
        elif key == pygame.K_DOWN:
            self.selected_apartment = min(len(self.apartments) - 1, self.selected_apartment + 1)
        elif key == pygame.K_RETURN:
            self.apply_for_apartment()
            
    def apply_for_apartment(self):
        self.applications_sent += 1
        # Always reject - player has no/bad credit
        self.rejections += 1
        if self.applications_sent >= 5:
            self.end_game()
            
    def end_game(self):
        self.active = False
        self.completed = True
        
    def update(self, dt):
        pass
        
    def draw(self, screen):
        if not self.active:
            return
        screen.fill((240, 240, 250))
        # Simple rejection interface
        title = "APARTMENT APPLICATIONS"
        title_surf = self.fonts['title'].render(title, True, (50, 50, 60))
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - 150, 50))
        
        status = f"Applications: {self.applications_sent} | Rejections: {self.rejections}"
        status_surf = self.fonts['normal'].render(status, True, (180, 60, 60))
        screen.blit(status_surf, (50, 100))
        
    def get_results(self):
        return {
            'stress': 20,
            'message': "All applications rejected due to credit",
            'color': (255, 100, 100)
        }

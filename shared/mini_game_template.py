"""Template Mini-Game - Quick template for creating mini-games"""

import pygame
import random
from shared.constants import *

class TemplateMiniGame:
    """Template for quickly creating mini-games"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.score = 0
        self.timer = 60.0  # 60 seconds
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
    def start(self):
        """Start the mini-game"""
        self.active = True
        self.completed = False
        self.score = 0
        self.timer = 60.0
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update timer
        self.timer -= dt
        if self.timer <= 0:
            self.end_game()
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_SPACE:
            self.score += 10
            
    def handle_click(self, pos):
        """Handle mouse clicks"""
        if not self.active:
            return
            
    def end_game(self):
        """End the mini-game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return results that affect game state"""
        return {
            'money': self.score // 10,
            'stress': -10 if self.score > 50 else 10,
            'message': f"Mini-game complete! Score: {self.score}",
            'color': (100, 255, 100)
        }
        
    def draw(self, screen):
        """Draw the mini-game"""
        if not self.active:
            return
            
        # Background
        screen.fill((240, 240, 250))
        
        # Title
        title = "MINI-GAME TITLE"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surf, title_rect)
        
        # Timer
        timer_text = f"Time: {int(self.timer)}s"
        timer_color = (255, 100, 100) if self.timer < 10 else (100, 100, 110)
        timer_surf = self.font.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (50, 50))
        
        # Score
        score_text = f"Score: {self.score}"
        score_surf = self.font.render(score_text, True, (100, 100, 110))
        screen.blit(score_surf, (SCREEN_WIDTH - 150, 50))
        
        # Game content goes here
        game_area = pygame.Rect(50, 100, SCREEN_WIDTH - 100, 400)
        pygame.draw.rect(screen, (255, 255, 255), game_area)
        pygame.draw.rect(screen, (200, 200, 210), game_area, 2)
        
        # Instructions
        inst_surf = self.small_font.render("Press SPACE to score points", True, (120, 120, 140))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(inst_surf, inst_rect)
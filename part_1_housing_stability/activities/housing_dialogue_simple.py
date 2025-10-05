"""Simplified Housing Intro Dialogue"""

import pygame
import math
from shared.constants import *

class SimpleHousingDialogue:
    """Simplified intro dialogue for housing crisis"""
    
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.dialogue_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        # Dialogue state
        self.current_line = 0
        self.text_progress = 0
        self.text_speed = 0.8  # Characters per frame
        self.fade_in = 0
        
        # Simple intro text
        self.intro_lines = [
            "You just turned 18.",
            "The foster care system no longer supports you.",
            "With $73 in your pocket and nowhere to go,",
            "you must find stable housing within 30 days.",
            "",
            "Every choice matters. Every dollar counts.",
            "Welcome to adulthood."
        ]
        
    def start(self):
        """Start the dialogue sequence"""
        self.active = True
        self.current_line = 0
        self.text_progress = 0
        self.fade_in = 0
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_SPACE or key == pygame.K_RETURN or key == pygame.K_e:
            # If text is still animating, complete it instantly
            if self.current_line < len(self.intro_lines) and self.text_progress < len(self.intro_lines[self.current_line]):
                self.text_progress = len(self.intro_lines[self.current_line])
            else:
                # Move to next line
                self.current_line += 1
                self.text_progress = 0
                
                # Check if we've finished all lines
                if self.current_line >= len(self.intro_lines):
                    self.active = False
                    self.objective_manager.complete_current_objective()
                    
    def update(self, dt):
        """Update dialogue animation"""
        if not self.active:
            return
            
        # Fade in effect
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + dt * 1.5)
            
        # Text animation
        if self.current_line < len(self.intro_lines):
            target_length = len(self.intro_lines[self.current_line])
            if self.text_progress < target_length:
                self.text_progress = min(target_length, self.text_progress + self.text_speed)
                
    def draw(self, screen):
        """Draw the dialogue interface"""
        if not self.active:
            return
            
        # Dark background
        screen.fill((10, 10, 20))
        
        # Title
        title_surf = self.title_font.render("HOUSING CRISIS", True, (200, 200, 200))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        title_rect.y -= math.sin(pygame.time.get_ticks() * 0.002) * 5  # Subtle float effect
        screen.blit(title_surf, title_rect)
        
        # Draw previous lines (faded)
        y_offset = SCREEN_HEIGHT // 2 - len(self.intro_lines) * 20
        for i in range(self.current_line):
            line_color = (150, 150, 150) if i < self.current_line else (255, 255, 255)
            line_surf = self.dialogue_font.render(self.intro_lines[i], True, line_color)
            line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 50))
            screen.blit(line_surf, line_rect)
        
        # Draw current line with typewriter effect
        if self.current_line < len(self.intro_lines):
            displayed_text = self.intro_lines[self.current_line][:int(self.text_progress)]
            if displayed_text:
                text_surf = self.dialogue_font.render(displayed_text, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset + self.current_line * 50))
                screen.blit(text_surf, text_rect)
                
                # Blinking cursor
                if self.text_progress < len(self.intro_lines[self.current_line]) and pygame.time.get_ticks() % 500 < 250:
                    cursor_x = text_rect.right + 5
                    cursor_y = text_rect.y
                    pygame.draw.rect(screen, (255, 255, 255), (cursor_x, cursor_y, 2, text_rect.height))
        
        # Continue prompt
        if self.current_line < len(self.intro_lines) and self.text_progress >= len(self.intro_lines[self.current_line]):
            prompt_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 255)
            prompt_surf = self.small_font.render("PRESS SPACE TO CONTINUE", True, (200, 200, 200))
            prompt_surf.set_alpha(prompt_alpha)
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(prompt_surf, prompt_rect)
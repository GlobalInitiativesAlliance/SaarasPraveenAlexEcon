"""Standalone intro dialogue screen for Part 1"""

import pygame
import math
from shared.constants import *

class IntroDialogueScreen:
    """Simple intro screen that plays automatically when Part 1 starts"""
    
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.complete = False
        
        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.dialogue_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Dialogue state
        self.current_line = 0
        self.text_progress = 0
        self.text_speed = 1.2  # Characters per frame
        self.fade_in = 0
        self.fade_out = 0
        self.ending = False
        
        # Simple intro text
        self.intro_lines = [
            "Happy 18th birthday.",
            "Your foster parents are packing your things.",
            "The state payments stopped at midnight.",
            "",
            "$73 in your wallet. No savings. No family.",
            "Everything you own fits in a garbage bag.",
            "",
            "You have 30 days to find stable housing.",
            "This is based on real experiences."
        ]
        
        # Auto-advance timer for smoother flow
        self.line_complete_timer = 0
        self.auto_advance_delay = 60  # frames to wait after line completes
        
    def start(self):
        """Start the dialogue sequence"""
        self.active = True
        self.complete = False
        self.current_line = 0
        self.text_progress = 0
        self.fade_in = 0
        self.fade_out = 0
        self.ending = False
        
    def handle_event(self, event):
        """Handle keyboard input"""
        if not self.active or self.ending:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e, pygame.K_ESCAPE]:
                # Skip to end or advance
                if self.current_line < len(self.intro_lines):
                    if self.text_progress < len(self.intro_lines[self.current_line]):
                        # Complete current line instantly
                        self.text_progress = len(self.intro_lines[self.current_line])
                    else:
                        # Advance to next line
                        self.advance_line()
                return True
                    
        return False
        
    def advance_line(self):
        """Move to next line or end"""
        self.current_line += 1
        self.text_progress = 0
        self.line_complete_timer = 0
        
        if self.current_line >= len(self.intro_lines):
            self.end_dialogue()
            
    def end_dialogue(self):
        """Start ending the dialogue"""
        self.ending = True
        self.fade_out = 0
        
    def update(self, dt):
        """Update dialogue animation"""
        if not self.active:
            return
            
        # Fade in at start
        if self.fade_in < 1.0 and not self.ending:
            self.fade_in = min(1.0, self.fade_in + dt * 1.5)
            
        # Fade out at end
        if self.ending:
            self.fade_out += dt * 1.5
            if self.fade_out >= 1.0:
                self.active = False
                self.complete = True
                # Just mark as complete, don't call complete_current_objective to avoid loops
            return
            
        # Text animation
        if self.current_line < len(self.intro_lines):
            target_length = len(self.intro_lines[self.current_line])
            if self.text_progress < target_length:
                self.text_progress = min(target_length, self.text_progress + self.text_speed)
            else:
                # Line is complete, handle auto-advance
                self.line_complete_timer += 1
                if self.line_complete_timer >= self.auto_advance_delay:
                    self.advance_line()
                
    def draw(self, screen):
        """Draw the dialogue interface"""
        if not self.active:
            return
            
        # Calculate opacity
        if self.ending:
            opacity = max(0, 255 - int(self.fade_out * 255))
        else:
            opacity = int(self.fade_in * 255)
            
        # Create a surface for the entire screen with alpha
        dialogue_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dialogue_surface.set_alpha(opacity)
        
        # Dark background
        dialogue_surface.fill((10, 10, 20))
        
        # Title with floating effect
        title_surf = self.title_font.render("HOUSING CRISIS", True, (200, 200, 200))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
        title_rect.y -= math.sin(pygame.time.get_ticks() * 0.002) * 5
        dialogue_surface.blit(title_surf, title_rect)
        
        # Draw all lines with a staggered fade effect
        y_offset = SCREEN_HEIGHT // 2 - len(self.intro_lines) * 25
        
        for i in range(min(self.current_line + 1, len(self.intro_lines))):
            if i < self.current_line:
                # Previous lines (fully visible but dimmed)
                line_color = (150, 150, 150)
                line_text = self.intro_lines[i]
            elif i == self.current_line:
                # Current line (typewriter effect)
                line_color = (255, 255, 255)
                line_text = self.intro_lines[i][:int(self.text_progress)]
            else:
                continue
                
            if line_text:  # Skip empty lines
                line_surf = self.dialogue_font.render(line_text, True, line_color)
                line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 60))
                dialogue_surface.blit(line_surf, line_rect)
                
                # Blinking cursor on current line
                if i == self.current_line and self.text_progress < len(self.intro_lines[i]):
                    if pygame.time.get_ticks() % 500 < 250:
                        cursor_x = line_rect.right + 5
                        pygame.draw.rect(dialogue_surface, (255, 255, 255), 
                                       (cursor_x, line_rect.y, 3, line_rect.height))
        
        # Continue prompt (only show after some text is visible)
        if self.current_line > 0 or self.text_progress > 20:
            prompt_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 200)
            prompt_text = "PRESS SPACE TO CONTINUE" if self.current_line < len(self.intro_lines) - 1 else "PRESS SPACE TO BEGIN"
            prompt_surf = self.small_font.render(prompt_text, True, (200, 200, 200))
            prompt_surf.set_alpha(prompt_alpha)
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
            dialogue_surface.blit(prompt_surf, prompt_rect)
        
        # Blit the dialogue surface to the main screen
        screen.blit(dialogue_surface, (0, 0))
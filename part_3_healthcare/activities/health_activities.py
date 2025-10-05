import pygame
from shared.constants import *

class AnxietyActivity:
    """Anxiety management minigame"""
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        
        # Breathing exercise properties
        self.breath_phase = "inhale"  # inhale, hold, exhale
        self.breath_timer = 0.0
        self.breath_count = 0
        self.target_breaths = 3
        
        # Visual properties
        self.circle_radius = 50
        self.max_radius = 150
        self.current_radius = self.circle_radius
        
    def start(self):
        """Start the anxiety activity"""
        self.active = True
        self.completed = False
        self.breath_count = 0
        self.breath_timer = 0.0
        self.breath_phase = "inhale"
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_SPACE:
            # Space bar to control breathing
            if self.breath_phase == "inhale" and self.breath_timer > 2.0:
                self.breath_phase = "hold"
                self.breath_timer = 0.0
            elif self.breath_phase == "hold" and self.breath_timer > 1.0:
                self.breath_phase = "exhale"
                self.breath_timer = 0.0
            elif self.breath_phase == "exhale" and self.breath_timer > 3.0:
                self.breath_phase = "inhale"
                self.breath_timer = 0.0
                self.breath_count += 1
                
                if self.breath_count >= self.target_breaths:
                    self.complete()
                    
    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return
            
        self.breath_timer += dt
        
        # Update circle size based on breathing phase
        if self.breath_phase == "inhale":
            target = self.max_radius
            self.current_radius += (target - self.current_radius) * dt * 0.5
        elif self.breath_phase == "hold":
            # Keep current size
            pass
        elif self.breath_phase == "exhale":
            target = self.circle_radius
            self.current_radius += (target - self.current_radius) * dt * 0.3
            
    def draw(self, screen):
        """Draw the breathing exercise"""
        if not self.active:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Draw breathing circle
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        color = (100, 150, 255) if self.breath_phase == "inhale" else (100, 255, 150)
        pygame.draw.circle(screen, color, center, int(self.current_radius), 3)
        
        # Draw instructions
        font = pygame.font.Font(None, 36)
        phase_text = {
            "inhale": "BREATHE IN... (Press SPACE when ready)",
            "hold": "HOLD... (Press SPACE when ready)",
            "exhale": "BREATHE OUT... (Press SPACE when ready)"
        }
        
        text = phase_text[self.breath_phase]
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
        screen.blit(text_surf, text_rect)
        
        # Draw progress
        progress_text = f"Breaths completed: {self.breath_count}/{self.target_breaths}"
        progress_surf = pygame.font.Font(None, 24).render(progress_text, True, (200, 200, 200))
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(progress_surf, progress_rect)
        
    def complete(self):
        """Complete the activity"""
        self.completed = True
        self.active = False
        self.objective_manager.complete_current_objective()
        
    def handle_mouse_motion(self, pos):
        """Handle mouse motion (not used)"""
        pass
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse click (not used)"""
        pass
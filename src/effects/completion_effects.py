import pygame
from src.constants import *


class ActivityCompletionFeedback:
    """Handles visual feedback when activities are completed"""

    def __init__(self):
        self.active = False
        self.completion_type = "success"
        self.message = ""
        self.submessage = ""
        self.center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.timer = 0.0
        self.duration = 2.0

        # Visual properties
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.background_alpha = 128

    def show_completion(self, completion_type="success", message="Complete!", submessage="", center_pos=None):
        """Show completion feedback"""
        self.active = True
        self.completion_type = completion_type
        self.message = message
        self.submessage = submessage
        if center_pos:
            self.center_pos = center_pos
        else:
            self.center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.timer = 0.0

    def update(self, dt):
        """Update the feedback display"""
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False

    def is_active(self):
        """Check if feedback is currently active"""
        return self.active

    def draw(self, screen):
        """Draw the completion feedback"""
        if not self.active:
            return

        # Create semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(self.background_alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Choose colors based on completion type
        if self.completion_type == "success":
            text_color = (0, 255, 0)
            bg_color = (0, 100, 0)
        elif self.completion_type == "failure":
            text_color = (255, 0, 0)
            bg_color = (100, 0, 0)
        else:
            text_color = (255, 255, 255)
            bg_color = (100, 100, 100)

        # Render main message
        text_surface = self.font_large.render(self.message, True, text_color)
        text_rect = text_surface.get_rect(center=self.center_pos)

        # Create background for text
        padding = 20
        bg_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding,
            text_rect.width + 2 * padding,
            text_rect.height + 2 * padding
        )

        # Add submessage height if present
        if self.submessage:
            sub_surface = self.font_small.render(self.submessage, True, text_color)
            bg_rect.height += sub_surface.get_height() + 10

        pygame.draw.rect(screen, bg_color, bg_rect)
        pygame.draw.rect(screen, text_color, bg_rect, 3)

        # Draw main message
        screen.blit(text_surface, text_rect)

        # Draw submessage if present
        if self.submessage:
            sub_surface = self.font_small.render(self.submessage, True, text_color)
            sub_rect = sub_surface.get_rect(
                center=(self.center_pos[0], self.center_pos[1] + text_rect.height // 2 + 15)
            )
            screen.blit(sub_surface, sub_rect)
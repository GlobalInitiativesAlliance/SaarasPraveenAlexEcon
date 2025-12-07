"""
Professional Smooth Transition Manager
Creates seamless, polished transitions for activities and objectives
"""
import pygame
import math

class SmoothTransitionManager:
    """Manages professional fade transitions and smooth scene changes"""

    def __init__(self, screen_width=1280, screen_height=720):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Transition state
        self.transitioning = False
        self.transition_type = None  # 'fade_out', 'fade_in', 'crossfade'
        self.transition_progress = 0.0
        self.transition_speed = 2.0  # Transitions per second
        self.transition_callback = None

        # Fade surfaces
        self.fade_surface = pygame.Surface((screen_width, screen_height))
        self.fade_surface.fill((0, 0, 0))

        # Professional easing curves
        self.easing_type = "ease_in_out"

    def start_fade_out(self, callback=None, duration=0.5):
        """Start a smooth fade out transition"""
        self.transitioning = True
        self.transition_type = "fade_out"
        self.transition_progress = 0.0
        self.transition_speed = 1.0 / duration
        self.transition_callback = callback

    def start_fade_in(self, callback=None, duration=0.5):
        """Start a smooth fade in transition"""
        self.transitioning = True
        self.transition_type = "fade_in"
        self.transition_progress = 0.0
        self.transition_speed = 1.0 / duration
        self.transition_callback = callback

    def start_activity_transition(self, callback=None):
        """Professional transition for launching activities"""
        self.start_fade_out(callback, duration=0.3)

    def ease_in_out(self, t):
        """Smooth easing function for professional feel"""
        if t < 0.5:
            return 2 * t * t
        else:
            return -1 + (4 - 2 * t) * t

    def ease_out_quart(self, t):
        """Smooth deceleration easing"""
        return 1 - pow(1 - t, 4)

    def update(self, dt):
        """Update transition state"""
        if not self.transitioning:
            return False

        # Update progress
        self.transition_progress += self.transition_speed * dt

        # Check if transition complete
        if self.transition_progress >= 1.0:
            self.transition_progress = 1.0
            self.transitioning = False

            # Execute callback
            if self.transition_callback:
                self.transition_callback()
                self.transition_callback = None

            return True

        return False

    def draw(self, screen):
        """Draw transition effects"""
        if not self.transitioning:
            return

        # Calculate eased progress
        eased_progress = self.ease_in_out(self.transition_progress)

        if self.transition_type == "fade_out":
            # Fade to black
            alpha = int(eased_progress * 255)
            self.fade_surface.set_alpha(alpha)
            screen.blit(self.fade_surface, (0, 0))

        elif self.transition_type == "fade_in":
            # Fade from black
            alpha = int((1.0 - eased_progress) * 255)
            self.fade_surface.set_alpha(alpha)
            screen.blit(self.fade_surface, (0, 0))

    def is_transitioning(self):
        """Check if currently transitioning"""
        return self.transitioning

    def get_transition_alpha(self):
        """Get current transition alpha for custom effects"""
        if not self.transitioning:
            return 0

        eased_progress = self.ease_in_out(self.transition_progress)

        if self.transition_type == "fade_out":
            return eased_progress
        elif self.transition_type == "fade_in":
            return 1.0 - eased_progress
        else:
            return 0
"""Simple narrative dialogue activities for housing crisis objectives"""

import pygame
import math
from shared.constants import *

class NarrativeActivity:
    """Base activity for simple narrative moments"""

    def __init__(self, objective_manager, title, lines, next_action="Press SPACE to continue"):
        self.objective_manager = objective_manager
        self.active = False
        self.complete = False

        self.title = title
        self.lines = lines
        self.next_action = next_action

        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.action_font = pygame.font.Font(None, 28)

        # Animation state
        self.fade_in = 0
        self.fade_out = 0
        self.ending = False

    def start(self):
        """Start the activity"""
        self.active = True
        self.complete = False
        self.fade_in = 0
        self.fade_out = 0
        self.ending = False

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active or self.ending:
            return False

        if key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
            self.end_activity()
            return True
        elif key == pygame.K_ESCAPE:
            self.end_activity()
            return True

        return False

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or self.ending:
            return

        if button == 1:  # Left click
            self.end_activity()

    def handle_mouse_motion(self, pos):
        """Handle mouse motion (unused)"""
        pass

    def end_activity(self):
        """Start ending the activity"""
        self.ending = True
        self.fade_out = 0

    def update(self, dt):
        """Update animation"""
        if not self.active:
            return

        # Fade in
        if self.fade_in < 1.0 and not self.ending:
            self.fade_in = min(1.0, self.fade_in + dt * 2.0)

        # Fade out
        if self.ending:
            self.fade_out += dt * 2.0
            if self.fade_out >= 1.0:
                self.active = False
                self.complete = True

    def draw(self, screen):
        """Draw the narrative screen"""
        if not self.active:
            return

        # Calculate opacity
        if self.ending:
            opacity = max(0, 255 - int(self.fade_out * 255))
        else:
            opacity = int(self.fade_in * 255)

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(int(opacity * 0.9))
        overlay.fill((10, 10, 15))
        screen.blit(overlay, (0, 0))

        # Content surface
        content_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        content_surf.set_colorkey((0, 0, 0))
        content_surf.set_alpha(opacity)

        # Draw title
        title_surf = self.title_font.render(self.title, True, (220, 220, 220))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        content_surf.blit(title_surf, title_rect)

        # Draw lines
        y_offset = SCREEN_HEIGHT // 2 - len(self.lines) * 20
        for line in self.lines:
            if line:  # Skip empty lines
                line_surf = self.text_font.render(line, True, (255, 255, 255))
                line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                content_surf.blit(line_surf, line_rect)
            y_offset += 45

        # Draw action prompt
        action_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 200)
        action_surf = self.action_font.render(self.next_action, True, (200, 200, 200))
        action_surf.set_alpha(min(opacity, action_alpha))
        action_rect = action_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        content_surf.blit(action_surf, action_rect)

        screen.blit(content_surf, (0, 0))


class RealityCheckActivity(NarrativeActivity):
    """The harsh reality after aging out"""
    def __init__(self, objective_manager):
        super().__init__(
            objective_manager,
            "REALITY CHECK",
            [
                "No family to call.",
                "No co-signer for apartments.",
                "Just a backpack and $73.",
                "",
                "Your phone battery: 12%"
            ]
        )


class ApartmentSearchActivity(NarrativeActivity):
    """Searching for apartments at the library"""
    def __init__(self, objective_manager):
        super().__init__(
            objective_manager,
            "LIBRARY COMPUTER",
            [
                "Searching: 'cheap apartments near me'",
                "",
                "Results: Everything requires proof of income.",
                "Cheapest studio: $1,400/month",
                "You have: $73"
            ]
        )


class ApplicationBarriersActivity(NarrativeActivity):
    """Facing the rental application requirements"""
    def __init__(self, objective_manager):
        super().__init__(
            objective_manager,
            "APPLICATION REQUIREMENTS",
            [
                "☐ Income 3x rent ($4,200/month)",
                "☐ Credit score 650+",
                "☐ Co-signer with good credit",
                "☐ First, last, and deposit ($4,200)",
                "",
                "You qualify for: nothing"
            ]
        )


class EvictionNoticeActivity(NarrativeActivity):
    """Alex disappears, leaving you with eviction"""
    def __init__(self, objective_manager):
        super().__init__(
            objective_manager,
            "EVICTION NOTICE",
            [
                "Alex hasn't been home for 5 days.",
                "Landlord posts 3-day notice on door.",
                "",
                "Alex never put you on the lease.",
                "You have no tenant rights.",
                "72 hours to leave."
            ]
        )


class ShelterNightActivity(NarrativeActivity):
    """First night in a youth shelter"""
    def __init__(self, objective_manager):
        super().__init__(
            objective_manager,
            "YOUTH SHELTER",
            [
                "Beds fill by 6 PM.",
                "Lights out at 9 PM.",
                "Wake up at 5 AM.",
                "",
                "Someone cries all night.",
                "Your shoes get stolen."
            ]
        )


class PaydayLoanActivity(NarrativeActivity):
    """Taking out a payday loan for deposit"""
    def __init__(self, objective_manager):
        super().__init__(
            objective_manager,
            "PAYDAY LOAN",
            [
                "Need $1,400 for apartment deposit.",
                "Your paycheck: $980",
                "",
                "Loan: $500",
                "Due in 2 weeks: $675",
                "APR: 391%"
            ]
        )
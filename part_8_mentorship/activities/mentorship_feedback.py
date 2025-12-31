"""
Mentorship Feedback System (Simplified)
Simple banners and status messages - NO heavy effects
For Part 8 (Lack of Guidance/Mentorship) mini-games
"""
import pygame
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass

from .mentorship_visual_base import MentorshipUIColors, MentorshipUIMetrics


@dataclass
class SimpleBanner:
    """Simple fade-in/out banner"""
    text: str
    color: Tuple[int, int, int]
    bg_color: Tuple[int, int, int]
    life: float
    max_life: float
    position: str = 'center'  # 'top', 'center', 'bottom'

    @property
    def alpha(self) -> int:
        """Get current alpha based on life (fade in/out)"""
        fade_time = 0.3
        if self.life > self.max_life - fade_time:
            # Fade in
            return int(255 * (self.max_life - self.life) / fade_time)
        elif self.life < fade_time:
            # Fade out
            return int(255 * self.life / fade_time)
        else:
            return 255


@dataclass
class StatusMessage:
    """Simple status message that fades"""
    text: str
    x: float
    y: float
    color: Tuple[int, int, int]
    life: float
    max_life: float

    @property
    def alpha(self) -> int:
        """Get current alpha based on life"""
        fade_time = 0.3
        if self.life > self.max_life - fade_time:
            return int(255 * (self.max_life - self.life) / fade_time)
        elif self.life < fade_time:
            return int(255 * self.life / fade_time)
        else:
            return 255


class SimpleFeedbackManager:
    """
    Simplified feedback manager for mentorship games.
    Uses simple fading banners and messages instead of heavy effects.
    """

    def __init__(self):
        self.banners: List[SimpleBanner] = []
        self.messages: List[StatusMessage] = []
        self.overlay_alpha: int = 0
        self.overlay_target: int = 0
        self.overlay_color: Tuple[int, int, int] = (0, 0, 0)
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 20)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 16)
            self.fonts['banner'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 42)
            self.fonts['heading'] = pygame.font.Font(None, 32)
            self.fonts['body'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['banner'] = pygame.font.Font(None, 32)

    def update(self, dt: float) -> None:
        """Update all effects"""
        # Update banners
        for banner in self.banners[:]:
            banner.life -= dt
            if banner.life <= 0:
                self.banners.remove(banner)

        # Update messages
        for msg in self.messages[:]:
            msg.life -= dt
            if msg.life <= 0:
                self.messages.remove(msg)

        # Update overlay
        if self.overlay_alpha != self.overlay_target:
            diff = self.overlay_target - self.overlay_alpha
            speed = 400  # Alpha units per second
            change = min(abs(diff), speed * dt)
            if diff > 0:
                self.overlay_alpha = min(self.overlay_target, self.overlay_alpha + change)
            else:
                self.overlay_alpha = max(self.overlay_target, self.overlay_alpha - change)

    def render(self, screen: pygame.Surface) -> None:
        """Render all effects"""
        screen_rect = screen.get_rect()

        # Render overlay first (background)
        if self.overlay_alpha > 1:
            overlay = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            overlay.fill((*self.overlay_color, int(self.overlay_alpha)))
            screen.blit(overlay, (0, 0))

        # Render messages
        for msg in self.messages:
            self._render_message(screen, msg)

        # Render banners
        for banner in self.banners:
            self._render_banner(screen, banner, screen_rect)

    def _render_message(self, screen: pygame.Surface, msg: StatusMessage) -> None:
        """Render a status message"""
        text_surface = self.fonts['body'].render(msg.text, True, msg.color)
        text_surface.set_alpha(msg.alpha)
        screen.blit(text_surface,
                   (msg.x - text_surface.get_width() // 2,
                    msg.y - text_surface.get_height() // 2))

    def _render_banner(self, screen: pygame.Surface, banner: SimpleBanner,
                      screen_rect: pygame.Rect) -> None:
        """Render a simple banner"""
        text_surface = self.fonts['banner'].render(banner.text, True, banner.color)
        banner_width = text_surface.get_width() + 48
        banner_height = text_surface.get_height() + 24

        # Calculate Y position
        if banner.position == 'top':
            y = 60
        elif banner.position == 'bottom':
            y = screen_rect.height - banner_height - 60
        else:
            y = screen_rect.centery - banner_height // 2

        x = screen_rect.centerx - banner_width // 2

        # Draw banner background
        banner_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        pygame.draw.rect(banner_surface, (*banner.bg_color, banner.alpha),
                        (0, 0, banner_width, banner_height),
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(banner_surface, (*banner.color, banner.alpha),
                        (0, 0, banner_width, banner_height), 2,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)
        screen.blit(banner_surface, (x, y))

        # Draw text
        text_surface.set_alpha(banner.alpha)
        screen.blit(text_surface,
                   (screen_rect.centerx - text_surface.get_width() // 2,
                    y + 12))

    def clear(self) -> None:
        """Clear all effects"""
        self.banners.clear()
        self.messages.clear()
        self.overlay_alpha = 0
        self.overlay_target = 0

    # ==================== Banner Creation Functions ====================

    def add_banner(self, text: str, status: str = "info",
                  duration: float = 3.0, position: str = 'center') -> None:
        """Add a simple status banner"""
        if status == "success":
            color = MentorshipUIColors.SUCCESS_GREEN
            bg_color = MentorshipUIColors.BACKGROUND_DARK
        elif status == "error":
            color = MentorshipUIColors.ERROR_RED
            bg_color = MentorshipUIColors.BACKGROUND_DARK
        elif status == "warning":
            color = MentorshipUIColors.WARNING_AMBER
            bg_color = MentorshipUIColors.BACKGROUND_DARK
        else:
            color = MentorshipUIColors.GUIDANCE_PRIMARY
            bg_color = MentorshipUIColors.BACKGROUND_DARK

        self.banners.append(SimpleBanner(
            text=text,
            color=color,
            bg_color=bg_color,
            life=duration,
            max_life=duration,
            position=position
        ))

    def add_message(self, text: str, x: float, y: float,
                   color: Tuple[int, int, int] = None,
                   duration: float = 2.0) -> None:
        """Add a status message at a location"""
        if color is None:
            color = MentorshipUIColors.TEXT_SECONDARY

        self.messages.append(StatusMessage(
            text=text,
            x=x,
            y=y,
            color=color,
            life=duration,
            max_life=duration
        ))

    # ==================== Preset Banners (API compatibility) ====================

    def add_uncertain_future_banner(self) -> None:
        """Add the 'Uncertain Future' banner"""
        self.add_banner("Your path remains uncertain...", "warning", 4.0)

    def add_collapse_banner(self) -> None:
        """Add 'Future Plan Collapsed' banner"""
        self.add_banner("Future Plan Collapsed", "error", 3.5)

    def add_balance_banner(self) -> None:
        """Add 'Temporary Balance' banner"""
        self.add_banner("Temporary Balance Achieved", "success", 3.0)

    def add_mentor_found_banner(self) -> None:
        """Add 'Mentor Found' special banner"""
        self.add_banner("A Guide Appears...", "success", 3.5)

    def add_no_guidance_banner(self) -> None:
        """Add 'No Guidance' banner"""
        self.add_banner("No guidance provided", "warning", 3.0)

    def add_incomplete_banner(self) -> None:
        """Add 'Incomplete Plan' banner"""
        self.add_banner("Plan Incomplete - No Feedback Given", "warning", 3.5)

    # ==================== Overlay Functions ====================

    def show_overlay(self, color: Tuple[int, int, int] = None, alpha: int = 120) -> None:
        """Show a color overlay"""
        if color is None:
            color = (0, 0, 0)
        self.overlay_color = color
        self.overlay_target = alpha

    def hide_overlay(self) -> None:
        """Hide the overlay"""
        self.overlay_target = 0

    def fade_to_black(self, target_alpha: int = 180) -> None:
        """Fade screen to dark"""
        self.overlay_color = (0, 0, 0)
        self.overlay_target = target_alpha

    def fade_from_black(self) -> None:
        """Fade back from dark"""
        self.overlay_target = 0

    # ==================== Compatibility Functions ====================

    def start_collapse_effect(self, x: float, y: float, duration: float = 2.0) -> None:
        """Start collapse effect (simplified - just shows overlay)"""
        self.show_overlay(MentorshipUIColors.ERROR_RED_DARK, 80)

    def get_collapse_progress(self) -> float:
        """Get collapse progress (dummy - always 0)"""
        return 0.0

    def is_collapse_active(self) -> bool:
        """Check if collapse is active (dummy)"""
        return self.overlay_alpha > 0 and self.overlay_target > 0

    def add_door_reveal(self, x: float, y: float, width: int, height: int,
                       color: Tuple[int, int, int] = None) -> None:
        """Add door reveal (no-op in simplified version)"""
        pass

    def add_ethereal_text(self, text: str, x: float, y: float, **kwargs) -> None:
        """Add ethereal text (simplified to regular message)"""
        color = kwargs.get('color', MentorshipUIColors.TEXT_PRIMARY)
        duration = kwargs.get('duration', 3.0)
        self.add_message(text, x, y, color, duration)

    def add_glow_pulse(self, x: float, y: float, **kwargs) -> None:
        """Add glow pulse (no-op in simplified version)"""
        pass


# Global instance for easy access
mentorship_feedback = SimpleFeedbackManager()

# Backwards compatibility alias
dream_feedback = mentorship_feedback
DreamFeedbackManager = SimpleFeedbackManager

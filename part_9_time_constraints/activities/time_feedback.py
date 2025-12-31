"""
Time Constraints Feedback System - Simplified Version
Clean banners, status messages, and overlays
For Part 9 (Time Constraints / Conflicting Responsibilities) mini-games
No heavy effects, no per-frame surface creation
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass

from .time_visual_base import PressureUIColors, PressureUIMetrics


@dataclass
class SimpleBanner:
    """Simple fade-in/out banner - no glow, no shake"""
    text: str
    color: Tuple[int, int, int]
    bg_color: Tuple[int, int, int]
    life: float
    max_life: float
    position: str = 'center'  # 'top', 'center', 'bottom'

    @property
    def alpha(self) -> int:
        """Calculate current alpha based on life"""
        elapsed = self.max_life - self.life
        if elapsed < 0.3:  # Fade in
            return int(255 * (elapsed / 0.3))
        elif self.life < 0.3:  # Fade out
            return int(255 * (self.life / 0.3))
        return 255


@dataclass
class StatusMessage:
    """Centered status text with simple fade"""
    text: str
    x: float
    y: float
    color: Tuple[int, int, int]
    life: float
    max_life: float
    font_name: str = 'body'

    @property
    def alpha(self) -> int:
        """Calculate current alpha based on life"""
        elapsed = self.max_life - self.life
        if elapsed < 0.2:
            return int(255 * (elapsed / 0.2))
        elif self.life < 0.3:
            return int(255 * (self.life / 0.3))
        return 255


class SimpleFeedbackManager:
    """
    Simplified feedback manager for time constraint games
    Clean banners and messages without heavy effects
    """

    def __init__(self):
        self.banners: List[SimpleBanner] = []
        self.messages: List[StatusMessage] = []
        self.fonts = {}

        # Simple overlay state
        self.overlay_alpha = 0
        self.overlay_target = 0
        self.overlay_color = (0, 0, 0)

        # Simple stress tint
        self.stress_level = 0.0
        self.target_stress = 0.0

        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('Arial', 42, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('Arial', 32, bold=True)
            self.fonts['body'] = pygame.font.SysFont('Arial', 22)
            self.fonts['body_bold'] = pygame.font.SysFont('Arial', 22, bold=True)
            self.fonts['small'] = pygame.font.SysFont('Arial', 18)
            self.fonts['banner'] = pygame.font.SysFont('Arial', 36, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 48)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['body'] = pygame.font.Font(None, 26)
            self.fonts['body_bold'] = pygame.font.Font(None, 26)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['banner'] = pygame.font.Font(None, 40)

    def update(self, dt: float) -> None:
        """Update all feedback effects"""
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
            self.overlay_alpha += diff * dt * 4
            if abs(diff) < 1:
                self.overlay_alpha = self.overlay_target

        # Update stress level
        stress_diff = self.target_stress - self.stress_level
        self.stress_level += stress_diff * dt * 2

    def render(self, screen: pygame.Surface) -> None:
        """Render all feedback effects"""
        screen_rect = screen.get_rect()

        # Render simple stress tint (if active)
        if self.stress_level > 0.2:
            self._render_stress_tint(screen, screen_rect)

        # Render banners
        for banner in self.banners:
            self._render_banner(screen, banner, screen_rect)

        # Render messages
        for msg in self.messages:
            self._render_message(screen, msg)

        # Render overlay
        if self.overlay_alpha > 1:
            overlay = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            overlay.fill((*self.overlay_color, int(self.overlay_alpha)))
            screen.blit(overlay, (0, 0))

    def _render_stress_tint(self, screen: pygame.Surface, screen_rect: pygame.Rect) -> None:
        """Render simple stress color tint (replaces heavy vignette)"""
        alpha = int(self.stress_level * 30)
        if alpha > 0:
            tint = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            tint.fill((*PressureUIColors.PRESSURE_RED_DARK, alpha))
            screen.blit(tint, (0, 0))

    def _render_banner(self, screen: pygame.Surface, banner: SimpleBanner,
                      screen_rect: pygame.Rect) -> None:
        """Render simple banner without glow"""
        font = self.fonts['banner']
        text_surface = font.render(banner.text, True, banner.color)

        # Calculate position
        banner_height = text_surface.get_height() + 30
        if banner.position == 'top':
            y = 50
        elif banner.position == 'bottom':
            y = screen_rect.height - banner_height - 50
        else:
            y = screen_rect.centery - banner_height // 2

        # Banner dimensions
        banner_width = text_surface.get_width() + 60
        x = screen_rect.centerx - banner_width // 2

        # Draw banner background
        alpha = banner.alpha
        banner_rect = pygame.Rect(x, y, banner_width, banner_height)

        banner_surf = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        pygame.draw.rect(banner_surf, (*banner.bg_color, int(alpha * 0.9)),
                        (0, 0, banner_width, banner_height),
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(banner_surf, (*banner.color, alpha),
                        (0, 0, banner_width, banner_height), 2,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)
        screen.blit(banner_surf, banner_rect)

        # Draw text
        text_surface.set_alpha(alpha)
        screen.blit(text_surface,
                   (screen_rect.centerx - text_surface.get_width() // 2,
                    y + 15))

    def _render_message(self, screen: pygame.Surface, msg: StatusMessage) -> None:
        """Render simple status message"""
        font = self.fonts.get(msg.font_name, self.fonts['body'])
        text_surface = font.render(msg.text, True, msg.color)
        text_surface.set_alpha(msg.alpha)
        screen.blit(text_surface,
                   (msg.x - text_surface.get_width() // 2,
                    msg.y - text_surface.get_height() // 2))

    def clear(self) -> None:
        """Clear all effects"""
        self.banners.clear()
        self.messages.clear()
        self.overlay_alpha = 0
        self.overlay_target = 0
        self.stress_level = 0.0
        self.target_stress = 0.0

    # ==================== Effect Creation Functions ====================

    def add_banner(self, text: str, color: Tuple[int, int, int] = None,
                  position: str = 'center', duration: float = 3.0) -> None:
        """Add a simple banner"""
        if color is None:
            color = PressureUIColors.PRESSURE_RED

        self.banners.append(SimpleBanner(
            text=text,
            color=color,
            bg_color=PressureUIColors.DARK_BG,
            life=duration,
            max_life=duration,
            position=position
        ))

    def add_message(self, text: str, x: float, y: float,
                   color: Tuple[int, int, int] = None,
                   duration: float = 2.0,
                   font_name: str = 'body') -> None:
        """Add a status message"""
        if color is None:
            color = PressureUIColors.TEXT_PRIMARY

        self.messages.append(StatusMessage(
            text=text,
            x=x,
            y=y,
            color=color,
            life=duration,
            max_life=duration,
            font_name=font_name
        ))

    # Preset banners for API compatibility
    def add_conflict_banner(self, text: str = "CONFLICT!",
                           color: Tuple[int, int, int] = None,
                           position: str = 'center',
                           duration: float = 3.0,
                           shake: bool = True,  # Ignored
                           flash: bool = True) -> None:  # Ignored
        """Add conflict warning banner (API compatible)"""
        self.add_banner(text, color or PressureUIColors.PRESSURE_RED, position, duration)

    def add_overload_banner(self) -> None:
        """Add 'OVERLOAD' warning banner"""
        self.add_banner("OVERLOAD!", PressureUIColors.PRESSURE_RED, 'center', 3.5)

    def add_time_conflict_banner(self) -> None:
        """Add time conflict detected banner"""
        self.add_banner("TIME CONFLICT DETECTED", PressureUIColors.CONFLICT_MAGENTA, 'center', 3.0)

    def add_no_good_options_banner(self) -> None:
        """Add 'No Good Options' banner"""
        self.add_banner("No good options remain...", PressureUIColors.URGENT_ORANGE, 'center', 3.0)

    def add_consequence_banner(self, positive: bool, text: str = None) -> None:
        """Add consequence result banner"""
        if text is None:
            text = "Choice made." if positive else "Consequence unavoidable."
        color = PressureUIColors.CALM_BLUE_LIGHT if positive else PressureUIColors.PRESSURE_RED
        self.add_banner(text, color, 'center', 2.5)

    def add_urgent_summons_banner(self) -> None:
        """Add urgent court summons banner"""
        self.add_banner("URGENT: COURT DATE CONFLICTS!", PressureUIColors.PRESSURE_RED, 'center', 4.0)

    # API compatibility methods (simplified or no-op)
    def add_pressure_text(self, text: str, x: float, y: float,
                         color: Tuple[int, int, int] = None, **kwargs) -> None:
        """Add pressure text (simplified)"""
        self.add_message(text, x, y, color or PressureUIColors.TEXT_WARNING, 3.0, 'heading')

    def add_clock_pulse(self, x: float, y: float, **kwargs) -> None:
        """No-op - clock pulses replaced with simpler visuals"""
        pass

    def add_consequence_flash(self, x: float, y: float, width: int, height: int,
                             positive: bool = True, **kwargs) -> None:
        """No-op - consequence flashes replaced with simpler visuals"""
        pass

    def add_overlap_highlight(self, rect: pygame.Rect, **kwargs) -> None:
        """No-op - overlap highlights handled by activity visuals"""
        pass

    def start_overload_effect(self, duration: float = 2.5) -> None:
        """Simplified - just show overlay"""
        self.show_overlay(PressureUIColors.PRESSURE_RED_DARK, 80)

    def set_stress_level(self, level: float) -> None:
        """Set target stress level for tint"""
        self.target_stress = max(0, min(1, level))

    def trigger_screen_shake(self, intensity: float = 8.0) -> None:
        """No-op - screen shake removed"""
        pass

    def trigger_screen_flash(self, color: Tuple[int, int, int] = None,
                            intensity: int = 150) -> None:
        """Simplified flash via overlay"""
        self.show_overlay(color or PressureUIColors.PRESSURE_RED, intensity, temporary=True)

    def show_overlay(self, color: Tuple[int, int, int], alpha: int,
                    temporary: bool = False) -> None:
        """Show color overlay"""
        self.overlay_color = color
        self.overlay_target = alpha
        if temporary:
            self.overlay_alpha = alpha  # Start visible, will fade

    def fade_to_black(self, target_alpha: int = 200) -> None:
        """Start fading screen to dark"""
        self.overlay_color = (0, 0, 0)
        self.overlay_target = target_alpha

    def fade_from_black(self) -> None:
        """Start fading back from dark"""
        self.overlay_target = 0

    def get_screen_shake_offset(self) -> Tuple[float, float]:
        """No-op - returns zero offset"""
        return (0, 0)

    def is_overload_active(self) -> bool:
        """Check if in overload state"""
        return self.overlay_alpha > 50 and self.overlay_color == PressureUIColors.PRESSURE_RED_DARK

    def get_overload_progress(self) -> float:
        """Get overload progress (0-1)"""
        return self.overlay_alpha / 255 if self.is_overload_active() else 0.0


# Global instance for easy access
time_feedback = SimpleFeedbackManager()

# Backwards compatibility aliases
pressure_feedback = time_feedback
PressureFeedbackManager = SimpleFeedbackManager

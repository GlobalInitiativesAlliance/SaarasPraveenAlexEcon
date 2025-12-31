"""
Systemic Barriers Feedback System
Animated stamps, error popups, disconnection effects
For Part 5 (Systemic and Structural Barriers) mini-games
"""
import pygame
import math
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .systemic_visual_base import SystemicUIColors, SystemicUIMetrics


@dataclass
class StampAnimation:
    """Animated stamp slam effect"""
    x: float
    y: float
    text: str
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 1.5
    phase: str = 'slam'  # 'slam', 'impact', 'settle'
    scale: float = 3.0
    rotation: float = -15
    target_rotation: float = -15


@dataclass
class TextPopup:
    """Floating text popup"""
    x: float
    y: float
    text: str
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 1.5
    velocity_y: float = -30
    font_size: str = 'medium'
    scale: float = 1.0


@dataclass
class ErrorBanner:
    """Slide-in error/status banner"""
    title: str
    message: str
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 4.0
    slide_progress: float = 0.0
    state: str = 'entering'  # 'entering', 'visible', 'exiting'
    shake_offset: float = 0.0


@dataclass
class LoopCounter:
    """Visual counter for frustration loops"""
    count: int
    max_display: int = 5
    pulse: float = 0.0
    color: Tuple[int, int, int] = None

    def __post_init__(self):
        if self.color is None:
            self.color = SystemicUIColors.WARNING_ORANGE


class SystemicFeedbackManager:
    """
    Manages animated feedback for systemic barriers games
    Stamps, error popups, loop counters, frustration indicators
    """

    def __init__(self):
        self.stamps: List[StampAnimation] = []
        self.popups: List[TextPopup] = []
        self.banners: List[ErrorBanner] = []
        self.loop_counter: Optional[LoopCounter] = None
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['stamp'] = pygame.font.SysFont('Impact', 52, bold=True)
            self.fonts['stamp_large'] = pygame.font.SysFont('Impact', 72, bold=True)
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 24, bold=True)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 18)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 16)
            self.fonts['popup'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.fonts['counter'] = pygame.font.SysFont('SF Pro Display', 20, bold=True)
        except:
            self.fonts['stamp'] = pygame.font.Font(None, 58)
            self.fonts['stamp_large'] = pygame.font.Font(None, 78)
            self.fonts['title'] = pygame.font.Font(None, 28)
            self.fonts['body'] = pygame.font.Font(None, 22)
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['popup'] = pygame.font.Font(None, 32)
            self.fonts['counter'] = pygame.font.Font(None, 24)

    def update(self, dt: float) -> None:
        """Update all feedback elements"""
        # Update stamps
        for stamp in self.stamps[:]:
            stamp.life -= dt / stamp.max_life
            if stamp.life <= 0:
                self.stamps.remove(stamp)
                continue

            # Phase progression
            progress = 1 - stamp.life
            if progress < 0.15:
                stamp.phase = 'slam'
                # Scale down quickly
                stamp.scale = 3.0 - (progress / 0.15) * 2.5
            elif progress < 0.25:
                stamp.phase = 'impact'
                stamp.scale = 0.5 + (progress - 0.15) / 0.1 * 0.7
            else:
                stamp.phase = 'settle'
                stamp.scale = 1.0 + math.sin((progress - 0.25) * 20) * 0.05 * (1 - progress)

        # Update popups
        for popup in self.popups[:]:
            popup.life -= dt / popup.max_life
            if popup.life <= 0:
                self.popups.remove(popup)
                continue

            popup.y += popup.velocity_y * dt
            # Scale animation
            progress = 1 - popup.life
            if progress < 0.2:
                popup.scale = 0.5 + (progress / 0.2) * 0.7
            else:
                popup.scale = 1.2 - (progress - 0.2) * 0.25

        # Update banners
        for banner in self.banners[:]:
            banner.life -= dt / banner.max_life
            if banner.life <= 0:
                self.banners.remove(banner)
                continue

            # State transitions
            if banner.state == 'entering':
                banner.slide_progress = min(1.0, banner.slide_progress + dt * 5)
                if banner.slide_progress >= 1.0:
                    banner.state = 'visible'
            elif banner.state == 'visible':
                if banner.life < 0.2:
                    banner.state = 'exiting'
                # Shake effect for errors
                banner.shake_offset = math.sin(time.time() * 20) * 2 * banner.life
            elif banner.state == 'exiting':
                banner.slide_progress = max(0.0, banner.slide_progress - dt * 5)

        # Update loop counter
        if self.loop_counter:
            self.loop_counter.pulse = max(0, self.loop_counter.pulse - dt * 2)
            # Color escalation based on count
            if self.loop_counter.count >= 3:
                self.loop_counter.color = SystemicUIColors.ERROR_RED
            elif self.loop_counter.count >= 2:
                self.loop_counter.color = SystemicUIColors.WARNING_ORANGE
            else:
                self.loop_counter.color = SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT

    def render(self, screen: pygame.Surface) -> None:
        """Render all feedback elements"""
        # Render stamps
        for stamp in self.stamps:
            self._render_stamp(screen, stamp)

        # Render popups
        for popup in self.popups:
            self._render_popup(screen, popup)

        # Render banners
        for i, banner in enumerate(self.banners):
            self._render_banner(screen, banner, i)

        # Render loop counter
        if self.loop_counter and self.loop_counter.count > 0:
            self._render_loop_counter(screen)

    def _render_stamp(self, screen: pygame.Surface, stamp: StampAnimation) -> None:
        """Render a stamp animation"""
        # Calculate alpha
        alpha = int(255 * min(1.0, stamp.life * 2))

        # Render stamp text
        text_surface = self.fonts['stamp_large'].render(stamp.text, True, stamp.color)

        # Scale
        if stamp.scale != 1.0:
            new_width = int(text_surface.get_width() * stamp.scale)
            new_height = int(text_surface.get_height() * stamp.scale)
            if new_width > 0 and new_height > 0:
                text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        # Rotate
        rotated = pygame.transform.rotate(text_surface, stamp.rotation)
        rotated.set_alpha(alpha)

        # Draw border effect (stamp outline)
        border_color = (*stamp.color[:3], alpha // 2)
        border_rect = rotated.get_rect(center=(stamp.x, stamp.y))

        # Stamp border
        border_surface = pygame.Surface((border_rect.width + 16, border_rect.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, border_color,
                        (0, 0, border_surface.get_width(), border_surface.get_height()), 4)
        border_surface = pygame.transform.rotate(border_surface, stamp.rotation)
        border_rect2 = border_surface.get_rect(center=(stamp.x, stamp.y))
        screen.blit(border_surface, border_rect2)

        # Main text
        screen.blit(rotated, border_rect)

    def _render_popup(self, screen: pygame.Surface, popup: TextPopup) -> None:
        """Render a text popup"""
        alpha = int(255 * min(1.0, popup.life * 2))

        font = self.fonts['popup']
        text_surface = font.render(popup.text, True, popup.color)

        # Scale
        if popup.scale != 1.0:
            new_width = int(text_surface.get_width() * popup.scale)
            new_height = int(text_surface.get_height() * popup.scale)
            if new_width > 0 and new_height > 0:
                text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        text_surface.set_alpha(alpha)

        # Shadow
        shadow_surface = font.render(popup.text, True, (0, 0, 0))
        if popup.scale != 1.0:
            shadow_surface = pygame.transform.scale(shadow_surface, (new_width, new_height))
        shadow_surface.set_alpha(alpha // 3)

        x = int(popup.x - text_surface.get_width() // 2)
        y = int(popup.y - text_surface.get_height() // 2)

        screen.blit(shadow_surface, (x + 2, y + 2))
        screen.blit(text_surface, (x, y))

    def _render_banner(self, screen: pygame.Surface, banner: ErrorBanner,
                      index: int) -> None:
        """Render an error/status banner"""
        screen_width = screen.get_width()

        # Banner dimensions
        banner_width = 380
        banner_height = 80
        y = 20 + index * (banner_height + 10)

        # Slide position
        target_x = screen_width - banner_width - 20
        start_x = screen_width + 20
        current_x = start_x + (target_x - start_x) * self._ease_out(banner.slide_progress)
        current_x += banner.shake_offset

        # Banner surface
        banner_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(banner_surface, (45, 45, 55, 245),
                        (0, 0, banner_width, banner_height),
                        border_radius=SystemicUIMetrics.RADIUS_MEDIUM)

        # Color accent bar
        pygame.draw.rect(banner_surface, banner.color,
                        (0, 0, 5, banner_height),
                        border_top_left_radius=SystemicUIMetrics.RADIUS_MEDIUM,
                        border_bottom_left_radius=SystemicUIMetrics.RADIUS_MEDIUM)

        # Icon circle
        icon_x = 30
        icon_y = banner_height // 2
        pygame.draw.circle(banner_surface, banner.color, (icon_x, icon_y), 18)

        # Icon (X for error, ! for warning)
        is_error = banner.color == SystemicUIColors.ERROR_RED or banner.color == SystemicUIColors.STAMP_RED
        icon_text = "X" if is_error else "!"
        icon_surface = self.fonts['title'].render(icon_text, True, (255, 255, 255))
        icon_rect = icon_surface.get_rect(center=(icon_x, icon_y))
        banner_surface.blit(icon_surface, icon_rect)

        # Title
        title_surface = self.fonts['title'].render(banner.title, True, (255, 255, 255))
        banner_surface.blit(title_surface, (60, 15))

        # Message
        msg_surface = self.fonts['small'].render(banner.message, True, (180, 180, 190))
        banner_surface.blit(msg_surface, (60, 45))

        # Border
        pygame.draw.rect(banner_surface, (70, 70, 80),
                        (0, 0, banner_width, banner_height),
                        width=1, border_radius=SystemicUIMetrics.RADIUS_MEDIUM)

        screen.blit(banner_surface, (int(current_x), y))

    def _render_loop_counter(self, screen: pygame.Surface) -> None:
        """Render the frustration loop counter"""
        counter = self.loop_counter
        x = 20
        y = screen.get_height() - 60

        # Background
        width = 200
        height = 40
        rect = pygame.Rect(x, y, width, height)

        pygame.draw.rect(screen, (40, 40, 50, 220), rect,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Pulse effect
        if counter.pulse > 0:
            pulse_rect = rect.inflate(int(10 * counter.pulse), int(6 * counter.pulse))
            pulse_color = (*counter.color, int(100 * counter.pulse))
            surf = pygame.Surface((pulse_rect.width, pulse_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(surf, pulse_color, (0, 0, pulse_rect.width, pulse_rect.height),
                            border_radius=SystemicUIMetrics.RADIUS_SMALL)
            screen.blit(surf, pulse_rect.topleft)

        # Label
        label = self.fonts['small'].render("Redirected:", True, SystemicUIColors.TEXT_LIGHT)
        screen.blit(label, (x + 10, y + 10))

        # Count circles
        circle_x = x + 110
        for i in range(counter.max_display):
            if i < counter.count:
                pygame.draw.circle(screen, counter.color, (circle_x + i * 18, y + 20), 6)
            else:
                pygame.draw.circle(screen, SystemicUIColors.INSTITUTIONAL_GRAY, (circle_x + i * 18, y + 20), 6, 1)

        # Border
        pygame.draw.rect(screen, counter.color, rect, 1,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

    def _ease_out(self, t: float) -> float:
        """Ease out cubic"""
        return 1 - pow(1 - t, 3)

    def clear(self) -> None:
        """Clear all feedback elements"""
        self.stamps.clear()
        self.popups.clear()
        self.banners.clear()
        self.loop_counter = None

    # ==================== Stamp Functions ====================

    def add_rejected_stamp(self, x: float, y: float) -> None:
        """Add REJECTED stamp animation"""
        self.stamps.append(StampAnimation(
            x=x,
            y=y,
            text="REJECTED",
            color=SystemicUIColors.STAMP_RED,
            max_life=2.0,
            rotation=-12
        ))

    def add_incomplete_stamp(self, x: float, y: float) -> None:
        """Add INCOMPLETE stamp animation"""
        self.stamps.append(StampAnimation(
            x=x,
            y=y,
            text="INCOMPLETE",
            color=SystemicUIColors.STAMP_RED,
            max_life=2.0,
            rotation=-15
        ))

    def add_denied_stamp(self, x: float, y: float) -> None:
        """Add DENIED stamp animation"""
        self.stamps.append(StampAnimation(
            x=x,
            y=y,
            text="DENIED",
            color=SystemicUIColors.STAMP_RED_DARK,
            max_life=2.0,
            rotation=-10
        ))

    def add_pending_stamp(self, x: float, y: float) -> None:
        """Add PENDING stamp animation"""
        self.stamps.append(StampAnimation(
            x=x,
            y=y,
            text="PENDING",
            color=SystemicUIColors.WARNING_ORANGE,
            max_life=1.5,
            rotation=-8
        ))

    def add_approved_stamp(self, x: float, y: float) -> None:
        """Add APPROVED stamp animation (rare!)"""
        self.stamps.append(StampAnimation(
            x=x,
            y=y,
            text="APPROVED",
            color=SystemicUIColors.APPROVAL_GREEN,
            max_life=2.5,
            rotation=-12
        ))

    # ==================== Popup Functions ====================

    def add_error_popup(self, x: float, y: float, text: str) -> None:
        """Add error text popup"""
        self.popups.append(TextPopup(
            x=x,
            y=y,
            text=text,
            color=SystemicUIColors.ERROR_RED,
            max_life=1.5
        ))

    def add_warning_popup(self, x: float, y: float, text: str) -> None:
        """Add warning text popup"""
        self.popups.append(TextPopup(
            x=x,
            y=y,
            text=text,
            color=SystemicUIColors.WARNING_ORANGE,
            max_life=1.2
        ))

    def add_info_popup(self, x: float, y: float, text: str) -> None:
        """Add info text popup"""
        self.popups.append(TextPopup(
            x=x,
            y=y,
            text=text,
            color=SystemicUIColors.GOVERNMENT_BLUE_LIGHT,
            max_life=1.0
        ))

    # ==================== Banner Functions ====================

    def add_error_banner(self, title: str, message: str) -> None:
        """Add error banner notification"""
        self.banners.append(ErrorBanner(
            title=title,
            message=message,
            color=SystemicUIColors.ERROR_RED,
            max_life=4.0
        ))

    def add_warning_banner(self, title: str, message: str) -> None:
        """Add warning banner notification"""
        self.banners.append(ErrorBanner(
            title=title,
            message=message,
            color=SystemicUIColors.WARNING_ORANGE,
            max_life=3.5
        ))

    def add_disconnect_banner(self) -> None:
        """Add call disconnected banner"""
        self.banners.append(ErrorBanner(
            title="Call Disconnected",
            message="Connection lost due to high call volume",
            color=SystemicUIColors.ERROR_RED,
            max_life=3.0
        ))

    def add_timeout_banner(self) -> None:
        """Add session timeout banner"""
        self.banners.append(ErrorBanner(
            title="Session Expired",
            message="Your session has timed out. Please start over.",
            color=SystemicUIColors.WARNING_ORANGE,
            max_life=4.0
        ))

    def add_crash_banner(self) -> None:
        """Add website crash banner"""
        self.banners.append(ErrorBanner(
            title="Connection Failed",
            message="Unable to reach server. Please try again later.",
            color=SystemicUIColors.ERROR_RED,
            max_life=4.0
        ))

    # ==================== Loop Counter Functions ====================

    def init_loop_counter(self) -> None:
        """Initialize the loop counter"""
        self.loop_counter = LoopCounter(count=0)

    def increment_loop_counter(self) -> int:
        """Increment loop counter and return new count"""
        if self.loop_counter is None:
            self.init_loop_counter()

        self.loop_counter.count += 1
        self.loop_counter.pulse = 1.0
        return self.loop_counter.count

    def get_loop_count(self) -> int:
        """Get current loop count"""
        return self.loop_counter.count if self.loop_counter else 0


# Global instance for easy access
systemic_feedback = SystemicFeedbackManager()

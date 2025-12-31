"""
Behavioral Visual Base Module
Stress/Overwhelm themed colors, helpers, and visual components
For Part 7 (Behavioral Economics) mini-games
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass


class BehavioralUIColors:
    """Stress/Overwhelm themed color palette"""

    # Primary behavioral theme - stress/calm spectrum
    STRESS_RED = (220, 80, 80)
    STRESS_RED_LIGHT = (245, 130, 130)
    STRESS_RED_DARK = (180, 60, 60)

    CALM_BLUE = (100, 160, 210)
    CALM_BLUE_LIGHT = (140, 190, 230)
    CALM_BLUE_DARK = (70, 130, 180)

    # Emotional states
    GUILT_PURPLE = (170, 100, 180)
    GUILT_PURPLE_LIGHT = (200, 140, 210)
    GUILT_PURPLE_DARK = (140, 70, 150)

    ANXIETY_ORANGE = (230, 160, 80)
    ANXIETY_ORANGE_LIGHT = (245, 190, 120)
    ANXIETY_ORANGE_DARK = (200, 130, 50)

    OVERWHELM_GRAY = (120, 115, 130)
    OVERWHELM_GRAY_LIGHT = (160, 155, 170)
    OVERWHELM_GRAY_DARK = (90, 85, 100)

    # Decision colors
    DECISION_GREEN = (90, 180, 120)
    DECISION_GREEN_LIGHT = (130, 210, 155)
    DECISION_GREEN_DARK = (65, 145, 90)

    # Financial
    MONEY_GREEN = (75, 160, 100)
    MONEY_GREEN_LIGHT = (110, 190, 135)
    MONEY_GREEN_DARK = (50, 130, 75)
    MONEY_RED = (200, 90, 90)
    MONEY_GOLD = (215, 175, 80)

    # Bill/Document colors
    BILL_RED = (255, 235, 235)
    BILL_GREEN = (235, 255, 240)
    BILL_YELLOW = (255, 250, 230)

    # UI Elements
    PANEL_BG = (30, 32, 38)
    PANEL_BG_LIGHT = (45, 48, 55)
    PANEL_BORDER = (55, 60, 70)

    CARD_BG = (255, 253, 250)
    CARD_BG_HOVER = (250, 248, 245)
    CARD_BG_ACTIVE = (245, 250, 255)
    CARD_BORDER = (210, 208, 200)

    BUTTON_PRIMARY = (80, 140, 200)
    BUTTON_PRIMARY_HOVER = (100, 160, 220)
    BUTTON_SECONDARY = (100, 105, 115)
    BUTTON_SECONDARY_HOVER = (120, 125, 135)
    BUTTON_DANGER = (200, 90, 90)
    BUTTON_SUCCESS = (90, 180, 120)

    # Background gradients
    BG_CALM = (245, 245, 250)
    BG_STRESSED = (255, 245, 240)
    BG_ANXIOUS = (255, 250, 240)

    # Text colors
    TEXT_PRIMARY = (35, 35, 45)
    TEXT_SECONDARY = (85, 85, 95)
    TEXT_MUTED = (130, 130, 140)
    TEXT_LIGHT = (250, 250, 252)
    TEXT_ERROR = (200, 70, 70)
    TEXT_SUCCESS = (60, 150, 90)

    # Timer colors
    TIMER_SAFE = (90, 180, 120)
    TIMER_WARNING = (230, 160, 80)
    TIMER_DANGER = (220, 80, 80)

    # Urgency colors for tasks
    URGENCY_HIGH = (255, 220, 220)
    URGENCY_HIGH_BORDER = (200, 100, 100)
    URGENCY_MEDIUM = (255, 245, 220)
    URGENCY_MEDIUM_BORDER = (200, 170, 90)
    URGENCY_LOW = (220, 240, 255)
    URGENCY_LOW_BORDER = (100, 150, 200)


class BehavioralUIMetrics:
    """Consistent spacing and sizing - 8px grid system"""

    # Grid base
    GRID_UNIT = 8

    # Spacing
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32
    SPACING_XXL = 48

    # Border radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_XLARGE = 16
    RADIUS_PILL = 999

    # Shadows
    SHADOW_SM = 3
    SHADOW_MD = 6
    SHADOW_LG = 10
    SHADOW_XL = 15

    # Standard component sizes
    BUTTON_HEIGHT = 44
    BUTTON_HEIGHT_SM = 36
    INPUT_HEIGHT = 40
    CARD_PADDING = 16
    CARD_PADDING_LG = 24

    # Bill card sizes
    BILL_CARD_WIDTH = 140
    BILL_CARD_HEIGHT = 70

    # Task card sizes
    TASK_CARD_WIDTH = 200
    TASK_CARD_HEIGHT = 60

    # Meter sizes
    METER_HEIGHT = 24
    METER_HEIGHT_SM = 16

    # Animation
    TRANSITION_SPEED = 0.15
    TRANSITION_FAST = 0.1
    TRANSITION_SLOW = 0.25


@dataclass
class UIAnimation:
    """Simple animation state tracker with smooth interpolation"""
    current: float
    target: float
    speed: float = 0.15

    def update(self, dt: float = 0.016) -> float:
        """Update animation value towards target"""
        diff = self.target - self.current
        self.current += diff * min(self.speed * 60 * dt, 1.0)
        return self.current

    @property
    def value(self) -> float:
        return self.current

    @property
    def is_complete(self) -> bool:
        return abs(self.target - self.current) < 0.01

    def set_target(self, target: float) -> None:
        """Set a new target value"""
        self.target = target

    def snap_to_target(self) -> None:
        """Immediately jump to target"""
        self.current = self.target


class BehavioralVisualHelpers:
    """Static helper functions for drawing common elements"""

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                   offset: int = 4, alpha: int = 40, radius: int = 0) -> None:
        """Draw a soft shadow behind a rectangle"""
        shadow_surface = pygame.Surface(
            (rect.width + offset * 2, rect.height + offset * 2),
            pygame.SRCALPHA
        )
        shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_rect,
                        border_radius=radius)
        screen.blit(shadow_surface, (rect.x - offset // 2, rect.y + offset // 2))

    @staticmethod
    def draw_glow(screen: pygame.Surface, rect: pygame.Rect,
                 color: Tuple[int, int, int], intensity: int = 80,
                 radius: int = 8) -> None:
        """Draw a colored glow around a rectangle"""
        glow_rect = rect.inflate(radius * 2, radius * 2)
        glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*color, intensity),
                        (0, 0, glow_rect.width, glow_rect.height),
                        border_radius=radius + BehavioralUIMetrics.RADIUS_MEDIUM)
        screen.blit(glow_surface, glow_rect.topleft)

    @staticmethod
    def draw_gradient_rect(screen: pygame.Surface, rect: pygame.Rect,
                          color_top: Tuple[int, int, int],
                          color_bottom: Tuple[int, int, int],
                          radius: int = 0) -> None:
        """Draw a vertical gradient rectangle"""
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        for y in range(rect.height):
            progress = y / max(rect.height - 1, 1)
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * progress)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * progress)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (rect.width, y))

        if radius > 0:
            mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask_surface, (255, 255, 255),
                           (0, 0, rect.width, rect.height),
                           border_radius=radius)
            surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        screen.blit(surface, rect.topleft)

    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int],
                         color2: Tuple[int, int, int],
                         t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        t = max(0, min(1, t))
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )

    @staticmethod
    def darken_color(color: Tuple[int, int, int], factor: float = 0.8) -> Tuple[int, int, int]:
        """Darken a color by a factor"""
        return (
            int(color[0] * factor),
            int(color[1] * factor),
            int(color[2] * factor)
        )

    @staticmethod
    def lighten_color(color: Tuple[int, int, int], factor: float = 1.2) -> Tuple[int, int, int]:
        """Lighten a color by a factor"""
        return (
            min(255, int(color[0] * factor)),
            min(255, int(color[1] * factor)),
            min(255, int(color[2] * factor))
        )

    @staticmethod
    def pulse_value(base: float, amplitude: float, speed: float = 4.0) -> float:
        """Get a pulsing value based on time"""
        return base + amplitude * abs(math.sin(time.time() * speed))


class BehavioralVisualComponents:
    """Reusable visual components for behavioral economics games"""

    def __init__(self):
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 38, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('SF Pro Display', 30, bold=True)
            self.fonts['subheading'] = pygame.font.SysFont('SF Pro Display', 24)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 20)
            self.fonts['body_bold'] = pygame.font.SysFont('SF Pro Text', 20, bold=True)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 16)
            self.fonts['small_bold'] = pygame.font.SysFont('SF Pro Text', 16, bold=True)
            self.fonts['tiny'] = pygame.font.SysFont('SF Pro Text', 14)
            self.fonts['money'] = pygame.font.SysFont('SF Mono', 28, bold=True)
            self.fonts['timer'] = pygame.font.SysFont('SF Mono', 32, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 44)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['subheading'] = pygame.font.Font(None, 28)
            self.fonts['body'] = pygame.font.Font(None, 24)
            self.fonts['body_bold'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['small_bold'] = pygame.font.Font(None, 20)
            self.fonts['tiny'] = pygame.font.Font(None, 16)
            self.fonts['money'] = pygame.font.Font(None, 34)
            self.fonts['timer'] = pygame.font.Font(None, 38)

    def draw_stress_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                         level: float, label: str = "Stress",
                         show_percentage: bool = False) -> None:
        """Draw a stress meter with gradient fill"""
        # Background with subtle shadow
        BehavioralVisualHelpers.draw_shadow(screen, rect, 3, 30,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)

        # Background track
        pygame.draw.rect(screen, (220, 220, 225), rect,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Fill based on level
        if level > 0:
            fill_width = int((rect.width - 4) * min(1.0, level))
            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, fill_width, rect.height - 4)

            # Color gradient based on level
            if level < 0.4:
                fill_color = BehavioralUIColors.CALM_BLUE
            elif level < 0.7:
                fill_color = BehavioralVisualHelpers.interpolate_color(
                    BehavioralUIColors.ANXIETY_ORANGE,
                    BehavioralUIColors.STRESS_RED,
                    (level - 0.4) / 0.3
                )
            else:
                fill_color = BehavioralUIColors.STRESS_RED
                # Pulsing effect when high
                pulse = BehavioralVisualHelpers.pulse_value(0, 20, 3.0)
                fill_color = (min(255, fill_color[0] + int(pulse)),
                            fill_color[1], fill_color[2])

            pygame.draw.rect(screen, fill_color, fill_rect,
                            border_radius=BehavioralUIMetrics.RADIUS_MEDIUM - 2)

        # Border
        pygame.draw.rect(screen, BehavioralUIColors.OVERWHELM_GRAY, rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Label
        label_text = self.fonts['small'].render(label, True, BehavioralUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (rect.x, rect.y - 20))

        # Percentage if requested
        if show_percentage:
            percent_text = self.fonts['tiny'].render(f"{int(level * 100)}%", True,
                                                     BehavioralUIColors.TEXT_MUTED)
            screen.blit(percent_text, (rect.right - percent_text.get_width(), rect.y - 18))

    def draw_emotional_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                            level: float, label: str,
                            color: Tuple[int, int, int],
                            icon: str = "") -> None:
        """Draw an emotional state meter (guilt, anxiety, etc.)"""
        # Shadow
        BehavioralVisualHelpers.draw_shadow(screen, rect, 3, 25,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)

        # Background
        pygame.draw.rect(screen, (235, 235, 240), rect,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Fill
        if level > 0:
            fill_width = int((rect.width - 4) * min(1.0, level))
            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, fill_width, rect.height - 4)

            # Gradient from light to full color
            light_color = BehavioralVisualHelpers.lighten_color(color, 1.3)
            BehavioralVisualHelpers.draw_gradient_rect(
                screen, fill_rect, light_color, color,
                BehavioralUIMetrics.RADIUS_MEDIUM - 2
            )

        # Border
        border_color = BehavioralVisualHelpers.darken_color(color, 0.7) if level > 0.5 else (180, 180, 190)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Icon + Label
        if icon:
            try:
                icon_font = pygame.font.SysFont('Segoe UI Emoji', 14)
                icon_text = icon_font.render(icon, True, BehavioralUIColors.TEXT_SECONDARY)
                screen.blit(icon_text, (rect.x, rect.y - 20))
                label_x = rect.x + icon_text.get_width() + 4
            except:
                label_x = rect.x
        else:
            label_x = rect.x

        label_text = self.fonts['small'].render(label, True, BehavioralUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (label_x, rect.y - 20))

    def draw_money_display(self, screen: pygame.Surface, rect: pygame.Rect,
                          amount: float, label: str = "Balance",
                          is_positive: bool = True) -> None:
        """Draw a professional money display"""
        # Shadow
        BehavioralVisualHelpers.draw_shadow(screen, rect, 4, 35,
                                           BehavioralUIMetrics.RADIUS_LARGE)

        # Background gradient
        if is_positive and amount > 50:
            bg_top = (245, 255, 248)
            bg_bottom = (235, 250, 240)
            border_color = BehavioralUIColors.MONEY_GREEN
        elif amount > 20:
            bg_top = (255, 252, 245)
            bg_bottom = (250, 248, 235)
            border_color = BehavioralUIColors.MONEY_GOLD
        else:
            bg_top = (255, 248, 248)
            bg_bottom = (250, 240, 240)
            border_color = BehavioralUIColors.MONEY_RED

        BehavioralVisualHelpers.draw_gradient_rect(screen, rect, bg_top, bg_bottom,
                                                   BehavioralUIMetrics.RADIUS_LARGE)

        # Border
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_LARGE)

        # Label
        label_text = self.fonts['small'].render(label, True, BehavioralUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (rect.centerx - label_text.get_width() // 2, rect.y + 10))

        # Amount
        amount_color = BehavioralUIColors.MONEY_GREEN if amount > 50 else \
                      BehavioralUIColors.MONEY_GOLD if amount > 20 else \
                      BehavioralUIColors.MONEY_RED
        amount_text = self.fonts['money'].render(f"${amount:.2f}", True, amount_color)
        screen.blit(amount_text, (rect.centerx - amount_text.get_width() // 2, rect.y + 35))

    def draw_bill_card(self, screen: pygame.Surface, rect: pygame.Rect,
                      name: str, amount: float, is_paid: bool = False,
                      is_dragging: bool = False, is_hover: bool = False) -> None:
        """Draw a professional bill card"""
        # Determine colors
        if is_paid:
            bg_color = BehavioralUIColors.BILL_GREEN
            border_color = BehavioralUIColors.DECISION_GREEN
            icon = "checkmark"
        elif is_dragging:
            bg_color = BehavioralUIColors.CARD_BG_ACTIVE
            border_color = BehavioralUIColors.CALM_BLUE
            icon = None
        elif is_hover:
            bg_color = BehavioralUIColors.CARD_BG_HOVER
            border_color = BehavioralUIColors.ANXIETY_ORANGE
            icon = None
        else:
            bg_color = BehavioralUIColors.BILL_RED
            border_color = BehavioralUIColors.STRESS_RED_LIGHT
            icon = None

        # Shadow (larger when dragging)
        shadow_offset = 8 if is_dragging else 4
        shadow_alpha = 60 if is_dragging else 35
        BehavioralVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)

        # Card background
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Inner highlight (top)
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, 20)
        highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, (255, 255, 255, 40),
                        (0, 0, highlight_rect.width, highlight_rect.height),
                        border_top_left_radius=BehavioralUIMetrics.RADIUS_MEDIUM - 2,
                        border_top_right_radius=BehavioralUIMetrics.RADIUS_MEDIUM - 2)
        screen.blit(highlight_surface, highlight_rect.topleft)

        # Border
        border_width = 2 if is_dragging or is_paid else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Bill name
        name_text = self.fonts['small_bold'].render(name, True, BehavioralUIColors.TEXT_PRIMARY)
        name_x = rect.centerx - name_text.get_width() // 2
        screen.blit(name_text, (name_x, rect.y + 12))

        # Amount
        amount_color = BehavioralUIColors.DECISION_GREEN if is_paid else BehavioralUIColors.STRESS_RED
        amount_text = self.fonts['body_bold'].render(f"${amount:.0f}", True, amount_color)
        amount_x = rect.centerx - amount_text.get_width() // 2
        screen.blit(amount_text, (amount_x, rect.y + 38))

        # Checkmark if paid
        if is_paid:
            check_center = (rect.right - 18, rect.y + 18)
            self.draw_checkmark(screen, check_center, 10, BehavioralUIColors.DECISION_GREEN)

    def draw_task_card(self, screen: pygame.Surface, rect: pygame.Rect,
                      name: str, urgency: str,
                      is_dragging: bool = False, is_hover: bool = False,
                      is_prioritized: bool = False) -> None:
        """Draw a floating task card"""
        # Urgency colors
        if urgency == 'HIGH':
            bg_color = BehavioralUIColors.URGENCY_HIGH
            border_color = BehavioralUIColors.URGENCY_HIGH_BORDER
            urgency_color = BehavioralUIColors.STRESS_RED
        elif urgency == 'MEDIUM':
            bg_color = BehavioralUIColors.URGENCY_MEDIUM
            border_color = BehavioralUIColors.URGENCY_MEDIUM_BORDER
            urgency_color = BehavioralUIColors.ANXIETY_ORANGE_DARK
        else:
            bg_color = BehavioralUIColors.URGENCY_LOW
            border_color = BehavioralUIColors.URGENCY_LOW_BORDER
            urgency_color = BehavioralUIColors.CALM_BLUE_DARK

        # Override colors for special states
        if is_dragging:
            bg_color = BehavioralUIColors.CARD_BG_ACTIVE
            border_color = BehavioralUIColors.CALM_BLUE
        elif is_hover:
            bg_color = BehavioralVisualHelpers.lighten_color(bg_color, 1.05)

        # Shadow
        shadow_offset = 10 if is_dragging else 5
        shadow_alpha = 70 if is_dragging else 40
        BehavioralVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)

        # Card background
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Border
        border_width = 2 if is_dragging else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Urgency indicator bar
        indicator_rect = pygame.Rect(rect.x + 4, rect.y + 4, 4, rect.height - 8)
        pygame.draw.rect(screen, urgency_color, indicator_rect,
                        border_radius=2)

        # Task name
        name_text = self.fonts['small'].render(name, True, BehavioralUIColors.TEXT_PRIMARY)
        name_x = rect.x + 16
        screen.blit(name_text, (name_x, rect.y + 12))

        # Urgency label
        urgency_text = self.fonts['tiny'].render(urgency, True, urgency_color)
        screen.blit(urgency_text, (name_x, rect.y + 35))

    def draw_priority_slot(self, screen: pygame.Surface, rect: pygame.Rect,
                          label: str, is_filled: bool = False,
                          is_highlighted: bool = False) -> None:
        """Draw a priority drop zone"""
        # Glow when highlighted
        if is_highlighted:
            BehavioralVisualHelpers.draw_glow(screen, rect,
                                             BehavioralUIColors.CALM_BLUE, 60, 10)

        # Shadow
        BehavioralVisualHelpers.draw_shadow(screen, rect, 4, 30,
                                           BehavioralUIMetrics.RADIUS_LARGE)

        # Background
        if is_filled:
            bg_color = BehavioralUIColors.BILL_GREEN
            border_color = BehavioralUIColors.DECISION_GREEN
        elif is_highlighted:
            bg_color = (240, 248, 255)
            border_color = BehavioralUIColors.CALM_BLUE
        else:
            bg_color = (252, 252, 255)
            border_color = (180, 180, 200)

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=BehavioralUIMetrics.RADIUS_LARGE)

        # Dashed border when empty
        if not is_filled:
            # Simple dashed effect with multiple rects
            dash_color = border_color
            dash_length = 8
            gap = 6

            # Top and bottom edges
            for x in range(rect.x, rect.right, dash_length + gap):
                dash_width = min(dash_length, rect.right - x)
                pygame.draw.line(screen, dash_color, (x, rect.y), (x + dash_width, rect.y), 2)
                pygame.draw.line(screen, dash_color, (x, rect.bottom - 1), (x + dash_width, rect.bottom - 1), 2)

            # Left and right edges
            for y in range(rect.y, rect.bottom, dash_length + gap):
                dash_height = min(dash_length, rect.bottom - y)
                pygame.draw.line(screen, dash_color, (rect.x, y), (rect.x, y + dash_height), 2)
                pygame.draw.line(screen, dash_color, (rect.right - 1, y), (rect.right - 1, y + dash_height), 2)
        else:
            pygame.draw.rect(screen, border_color, rect, 2,
                            border_radius=BehavioralUIMetrics.RADIUS_LARGE)

        # Label
        label_text = self.fonts['body_bold'].render(label, True, BehavioralUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (rect.x, rect.y - 28))

    def draw_countdown_timer(self, screen: pygame.Surface, center: Tuple[int, int],
                            time_remaining: float, time_total: float,
                            radius: int = 40) -> None:
        """Draw a circular countdown timer"""
        progress = max(0, min(1, time_remaining / time_total)) if time_total > 0 else 0

        # Determine color based on time
        if progress > 0.5:
            color = BehavioralUIColors.TIMER_SAFE
        elif progress > 0.2:
            color = BehavioralUIColors.TIMER_WARNING
        else:
            color = BehavioralUIColors.TIMER_DANGER
            # Pulsing effect when critical
            pulse = BehavioralVisualHelpers.pulse_value(0, 0.1, 5.0)
            radius = int(radius * (1 + pulse))

        # Background circle
        pygame.draw.circle(screen, (230, 230, 235), center, radius, 5)

        # Progress arc
        if progress > 0:
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * progress)

            num_segments = max(1, int(60 * progress))
            points = []
            for i in range(num_segments + 1):
                angle = start_angle + (end_angle - start_angle) * i / num_segments
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))

            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 5)

        # Center fill
        pygame.draw.circle(screen, BehavioralUIColors.CARD_BG, center, radius - 12)

        # Time text
        time_text = f"{int(time_remaining)}"
        text_surface = self.fonts['timer'].render(time_text, True, color)
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)

    def draw_choice_button(self, screen: pygame.Surface, rect: pygame.Rect,
                          text: str, index: int,
                          is_hover: bool = False, is_selected: bool = False) -> None:
        """Draw a professional choice button"""
        # Shadow
        shadow_offset = 5 if is_hover else 3
        BehavioralVisualHelpers.draw_shadow(screen, rect, shadow_offset, 30,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_selected:
            bg_color = BehavioralUIColors.CALM_BLUE_LIGHT
            border_color = BehavioralUIColors.CALM_BLUE
        elif is_hover:
            bg_color = (245, 250, 255)
            border_color = BehavioralUIColors.CALM_BLUE_LIGHT
        else:
            bg_color = (255, 255, 255)
            border_color = BehavioralUIColors.CARD_BORDER

        # Scale slightly on hover
        draw_rect = rect
        if is_hover:
            draw_rect = rect.inflate(4, 4)

        pygame.draw.rect(screen, bg_color, draw_rect,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border_color, draw_rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Number circle
        num_center = (draw_rect.x + 28, draw_rect.centery)
        pygame.draw.circle(screen, border_color, num_center, 14)
        num_text = self.fonts['small_bold'].render(str(index + 1), True,
                                                   BehavioralUIColors.TEXT_LIGHT)
        num_rect = num_text.get_rect(center=num_center)
        screen.blit(num_text, num_rect)

        # Choice text
        text_surface = self.fonts['body'].render(text, True, BehavioralUIColors.TEXT_PRIMARY)
        screen.blit(text_surface, (draw_rect.x + 55, draw_rect.centery - text_surface.get_height() // 2))

    def draw_modal_overlay(self, screen: pygame.Surface, alpha: int = 180) -> None:
        """Draw a dark modal overlay"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

    def draw_modal_container(self, screen: pygame.Surface, rect: pygame.Rect,
                            header_text: str = "",
                            header_color: Optional[Tuple[int, int, int]] = None,
                            success: bool = True) -> None:
        """Draw a modal container with optional header"""
        # Shadow
        BehavioralVisualHelpers.draw_shadow(screen, rect, 12, 80,
                                           BehavioralUIMetrics.RADIUS_XLARGE)

        # Main background
        pygame.draw.rect(screen, BehavioralUIColors.CARD_BG, rect,
                        border_radius=BehavioralUIMetrics.RADIUS_XLARGE)

        # Header strip
        if header_color or header_text:
            header_color = header_color or (BehavioralUIColors.DECISION_GREEN if success
                                           else BehavioralUIColors.STRESS_RED)
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 55)
            pygame.draw.rect(screen, header_color, header_rect,
                            border_top_left_radius=BehavioralUIMetrics.RADIUS_XLARGE,
                            border_top_right_radius=BehavioralUIMetrics.RADIUS_XLARGE)

            if header_text:
                header_surface = self.fonts['heading'].render(header_text, True,
                                                             BehavioralUIColors.TEXT_LIGHT)
                header_text_rect = header_surface.get_rect(center=(rect.centerx, rect.y + 27))
                screen.blit(header_surface, header_text_rect)

        # Border
        pygame.draw.rect(screen, BehavioralUIColors.PANEL_BORDER, rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_XLARGE)

    def draw_drop_zone(self, screen: pygame.Surface, rect: pygame.Rect,
                      label: str, is_highlighted: bool = False,
                      fill_color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a drop zone for drag and drop"""
        # Glow when highlighted
        if is_highlighted:
            BehavioralVisualHelpers.draw_glow(screen, rect,
                                             BehavioralUIColors.DECISION_GREEN, 70, 12)

        # Shadow
        BehavioralVisualHelpers.draw_shadow(screen, rect, 4, 25,
                                           BehavioralUIMetrics.RADIUS_LARGE)

        # Background
        bg_color = fill_color or (BehavioralUIColors.BILL_GREEN if is_highlighted
                                 else (250, 250, 255))
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=BehavioralUIMetrics.RADIUS_LARGE)

        # Border
        border_color = BehavioralUIColors.DECISION_GREEN if is_highlighted else (180, 180, 200)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_LARGE)

        # Label
        label_text = self.fonts['body_bold'].render(label, True,
                                                    BehavioralUIColors.DECISION_GREEN if is_highlighted
                                                    else BehavioralUIColors.TEXT_SECONDARY)
        label_x = rect.centerx - label_text.get_width() // 2
        screen.blit(label_text, (label_x, rect.y - 28))

    def draw_checkmark(self, screen: pygame.Surface, center: Tuple[int, int],
                      size: int = 16, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a checkmark icon"""
        if color is None:
            color = BehavioralUIColors.DECISION_GREEN

        # Circle background
        pygame.draw.circle(screen, color, center, size)

        # Checkmark
        check_points = [
            (center[0] - size * 0.4, center[1]),
            (center[0] - size * 0.1, center[1] + size * 0.35),
            (center[0] + size * 0.4, center[1] - size * 0.25)
        ]
        pygame.draw.lines(screen, (255, 255, 255), False, check_points, 3)

    def draw_x_mark(self, screen: pygame.Surface, center: Tuple[int, int],
                   size: int = 16, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw an X mark icon"""
        if color is None:
            color = BehavioralUIColors.STRESS_RED

        # Circle background
        pygame.draw.circle(screen, color, center, size)

        # X mark
        offset = size * 0.35
        pygame.draw.line(screen, (255, 255, 255),
                        (center[0] - offset, center[1] - offset),
                        (center[0] + offset, center[1] + offset), 3)
        pygame.draw.line(screen, (255, 255, 255),
                        (center[0] + offset, center[1] - offset),
                        (center[0] - offset, center[1] + offset), 3)

    def draw_instruction_text(self, screen: pygame.Surface, text: str,
                             center_x: int, y: int) -> None:
        """Draw centered instruction text"""
        text_surface = self.fonts['body'].render(text, True, BehavioralUIColors.TEXT_SECONDARY)
        screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

    def draw_continue_prompt(self, screen: pygame.Surface, center_x: int, y: int,
                            visible: bool = True) -> None:
        """Draw a pulsing continue prompt"""
        if not visible:
            return

        # Pulsing alpha
        alpha = int(150 + 100 * abs(math.sin(time.time() * 2)))

        prompt_surface = self.fonts['small'].render("Press any key to continue...", True,
                                                    BehavioralUIColors.TEXT_MUTED)
        # Create surface with alpha
        alpha_surface = pygame.Surface(prompt_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.fill((0, 0, 0, 0))
        alpha_surface.blit(prompt_surface, (0, 0))
        alpha_surface.set_alpha(alpha)

        screen.blit(alpha_surface, (center_x - prompt_surface.get_width() // 2, y))


# Global instance for easy access
behavioral_visuals = BehavioralVisualComponents()

"""
Time Constraints Visual Base Module
Pressure/Urgency themed colors, helpers, and visual components
For Part 9 (Time Constraints / Conflicting Responsibilities) mini-games
"""
import pygame
import math
import time
import random
from typing import Tuple, Optional, List
from dataclasses import dataclass


class PressureUIColors:
    """Pressure/Urgency color palette"""

    # Primary pressure colors
    PRESSURE_RED = (200, 60, 60)
    PRESSURE_RED_LIGHT = (230, 100, 100)
    PRESSURE_RED_DARK = (140, 40, 40)

    # Urgent orange/amber (warning state)
    URGENT_ORANGE = (220, 140, 60)
    URGENT_ORANGE_LIGHT = (245, 175, 100)
    URGENT_ORANGE_DARK = (180, 110, 40)

    # Time/clock gold (neutral time)
    TIME_GOLD = (200, 180, 100)
    TIME_GOLD_BRIGHT = (240, 220, 140)
    TIME_GOLD_DARK = (160, 140, 70)

    # Calm state (before stress builds)
    CALM_BLUE = (80, 120, 160)
    CALM_BLUE_LIGHT = (110, 155, 195)
    CALM_BLUE_DARK = (50, 85, 120)

    # High stress purple
    STRESS_PURPLE = (140, 80, 140)
    STRESS_PURPLE_LIGHT = (175, 115, 175)

    # Conflict magenta (overlapping events)
    CONFLICT_MAGENTA = (200, 80, 160)
    CONFLICT_MAGENTA_BRIGHT = (240, 120, 200)

    # Status colors
    SUCCESS_GREEN = (80, 160, 100)
    SUCCESS_GREEN_LIGHT = (110, 190, 130)
    WARNING_YELLOW = (220, 200, 80)
    FAILURE_RED = (180, 60, 60)

    # Card colors (notifications)
    CARD_WORK = (100, 180, 100)
    CARD_WORK_DARK = (70, 140, 70)
    CARD_PROGRAM = (100, 150, 200)
    CARD_PROGRAM_DARK = (70, 115, 160)
    CARD_THERAPY = (180, 130, 180)
    CARD_THERAPY_DARK = (145, 95, 145)
    CARD_COURT = (200, 80, 80)
    CARD_COURT_DARK = (160, 55, 55)
    CARD_JUNK = (100, 100, 110)
    CARD_BILL = (180, 150, 100)

    # UI Elements
    PANEL_BG = (28, 32, 40)
    PANEL_BG_LIGHT = (40, 45, 55)
    PANEL_BORDER = (52, 58, 70)
    BUTTON_DEFAULT = (55, 65, 81)
    BUTTON_HOVER = (71, 85, 105)

    # Background colors
    DARK_BG = (25, 25, 35)
    DARK_BG_STRESS = (45, 25, 30)
    DARK_BG_CALM = (25, 30, 40)

    # Highlight/emphasis
    HIGHLIGHT_WHITE = (240, 240, 250)
    HIGHLIGHT_DIM = (180, 180, 195)

    # Text colors
    TEXT_PRIMARY = (240, 240, 250)
    TEXT_SECONDARY = (180, 180, 195)
    TEXT_MUTED = (120, 125, 140)
    TEXT_WARNING = (255, 200, 150)
    TEXT_URGENT = (255, 150, 150)
    TEXT_DARK = (30, 30, 40)


class PressureUIMetrics:
    """Consistent spacing and sizing for pressure theme"""

    GRID_UNIT = 8

    # Spacing
    SPACING_XS = GRID_UNIT // 2      # 4px
    SPACING_SM = GRID_UNIT           # 8px
    SPACING_MD = GRID_UNIT * 2       # 16px
    SPACING_LG = GRID_UNIT * 3       # 24px
    SPACING_XL = GRID_UNIT * 5       # 40px

    # Border radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_XLARGE = 16

    # Shadows
    SHADOW_SM = 3
    SHADOW_MD = 6
    SHADOW_LG = 10

    # Card dimensions
    CARD_WIDTH = 180
    CARD_HEIGHT = 80

    # Calendar slot dimensions
    SLOT_WIDTH = 280
    SLOT_HEIGHT = 70

    # Clock dimensions
    CLOCK_RADIUS = 45
    CLOCK_RADIUS_SMALL = 30

    # Stress meter dimensions
    METER_WIDTH = 300
    METER_HEIGHT = 30


@dataclass
class UIAnimation:
    """Smooth animation handler"""
    current: float
    target: float
    speed: float = 0.15

    def update(self, dt: float) -> float:
        """Smoothly animate towards target"""
        diff = self.target - self.current
        self.current += diff * min(self.speed * 60 * dt, 1.0)
        return self.current

    @property
    def value(self) -> float:
        return self.current

    @property
    def is_complete(self) -> bool:
        return abs(self.target - self.current) < 0.01


@dataclass
class PulseAnimation:
    """Pulsing animation for urgency effects"""
    phase: float = 0.0
    speed: float = 3.0
    min_val: float = 0.3
    max_val: float = 1.0

    def update(self, dt: float) -> None:
        self.phase += dt * self.speed

    @property
    def value(self) -> float:
        range_val = self.max_val - self.min_val
        return self.min_val + (math.sin(self.phase) + 1) / 2 * range_val

    @property
    def alpha(self) -> int:
        return int(self.value * 255)


class PressureVisualHelpers:
    """Static helper functions for drawing pressure-themed elements"""

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                    offset: int = 4, alpha: int = 60,
                    border_radius: int = 8) -> None:
        """Draw a soft shadow behind an element"""
        shadow_surface = pygame.Surface(
            (rect.width + offset * 2, rect.height + offset * 2), pygame.SRCALPHA
        )
        shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_rect,
                        border_radius=border_radius)
        screen.blit(shadow_surface, (rect.x - offset // 2, rect.y + offset // 2))

    @staticmethod
    def draw_gradient_rect(screen: pygame.Surface, rect: pygame.Rect,
                          color_top: Tuple[int, int, int],
                          color_bottom: Tuple[int, int, int],
                          border_radius: int = 0) -> None:
        """Draw a rectangle with vertical gradient fill"""
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            progress = y / max(rect.height - 1, 1)
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * progress)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * progress)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (rect.width, y))
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
    def draw_urgent_glow(screen: pygame.Surface, center: Tuple[int, int],
                         radius: int, color: Tuple[int, int, int],
                         intensity: float = 0.5, layers: int = 4) -> None:
        """Draw a pulsing urgent glow effect"""
        for i in range(layers, 0, -1):
            layer_radius = radius + i * (radius // layers)
            alpha = int(50 * intensity * (1 - i / (layers + 1)))
            if alpha > 0:
                glow_surface = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, alpha),
                                 (layer_radius, layer_radius), layer_radius)
                screen.blit(glow_surface,
                          (center[0] - layer_radius, center[1] - layer_radius))

    @staticmethod
    def draw_warning_border(screen: pygame.Surface, rect: pygame.Rect,
                            time_val: float, intensity: float = 1.0,
                            border_radius: int = 8) -> None:
        """Draw a flashing warning border"""
        flash = (math.sin(time_val * 6) + 1) / 2
        alpha = int(150 + flash * 105 * intensity)
        color = PressureVisualHelpers.interpolate_color(
            PressureUIColors.URGENT_ORANGE,
            PressureUIColors.PRESSURE_RED,
            flash * intensity
        )
        pygame.draw.rect(screen, (*color, min(255, alpha)), rect, 3,
                        border_radius=border_radius)

    @staticmethod
    def draw_stress_vignette(screen: pygame.Surface, stress_level: float = 0.0) -> None:
        """Draw a stress-based vignette (edges turn red with stress)"""
        if stress_level < 0.1:
            return

        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        vignette_color = PressureVisualHelpers.interpolate_color(
            (0, 0, 0), PressureUIColors.PRESSURE_RED_DARK, stress_level
        )

        edge_width = int(60 + stress_level * 80)
        for i in range(edge_width):
            alpha = int(stress_level * 100 * (1 - i / edge_width))
            if alpha > 0:
                pygame.draw.rect(vignette, (*vignette_color, alpha),
                               (0, 0, width, i))
                pygame.draw.rect(vignette, (*vignette_color, alpha),
                               (0, height - i, width, i))
                pygame.draw.rect(vignette, (*vignette_color, alpha),
                               (0, 0, i, height))
                pygame.draw.rect(vignette, (*vignette_color, alpha),
                               (width - i, 0, i, height))

        screen.blit(vignette, (0, 0))


class PressureVisualComponents:
    """Reusable visual components for time constraint games"""

    def __init__(self):
        self.fonts = {}
        self.time_offset = random.random() * 100
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 42, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('SF Pro Display', 32, bold=True)
            self.fonts['subheading'] = pygame.font.SysFont('SF Pro Display', 26)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 22)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 18)
            self.fonts['tiny'] = pygame.font.SysFont('SF Pro Text', 14)
            self.fonts['clock'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.fonts['urgent'] = pygame.font.SysFont('Impact', 40, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 48)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['subheading'] = pygame.font.Font(None, 30)
            self.fonts['body'] = pygame.font.Font(None, 26)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['tiny'] = pygame.font.Font(None, 16)
            self.fonts['clock'] = pygame.font.Font(None, 32)
            self.fonts['urgent'] = pygame.font.Font(None, 44)

    def get_time(self) -> float:
        """Get animation time with offset"""
        return time.time() + self.time_offset

    def draw_clock_face(self, screen: pygame.Surface, center: Tuple[int, int],
                        radius: int, hour: int = 3, minute: int = 0,
                        is_urgent: bool = False) -> None:
        """Draw an analog clock face"""
        t = self.get_time()

        # Urgent glow
        if is_urgent:
            pulse = (math.sin(t * 4) + 1) / 2
            glow_intensity = 0.5 + pulse * 0.3
            PressureVisualHelpers.draw_urgent_glow(screen, center, radius + 10,
                                                   PressureUIColors.PRESSURE_RED, glow_intensity)

        # Clock face background
        pygame.draw.circle(screen, PressureUIColors.PANEL_BG_LIGHT, center, radius)
        pygame.draw.circle(screen, PressureUIColors.TIME_GOLD, center, radius, 3)

        # Hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            inner_r = radius - 12
            outer_r = radius - 5
            x1 = center[0] + int(math.cos(angle) * inner_r)
            y1 = center[1] + int(math.sin(angle) * inner_r)
            x2 = center[0] + int(math.cos(angle) * outer_r)
            y2 = center[1] + int(math.sin(angle) * outer_r)
            color = PressureUIColors.TIME_GOLD if i % 3 == 0 else PressureUIColors.HIGHLIGHT_DIM
            width = 3 if i % 3 == 0 else 1
            pygame.draw.line(screen, color, (x1, y1), (x2, y2), width)

        # Hour hand
        hour_angle = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
        hour_length = radius * 0.5
        hour_x = center[0] + int(math.cos(hour_angle) * hour_length)
        hour_y = center[1] + int(math.sin(hour_angle) * hour_length)
        pygame.draw.line(screen, PressureUIColors.HIGHLIGHT_WHITE, center, (hour_x, hour_y), 4)

        # Minute hand
        minute_angle = math.radians(minute * 6 - 90)
        minute_length = radius * 0.75
        minute_x = center[0] + int(math.cos(minute_angle) * minute_length)
        minute_y = center[1] + int(math.sin(minute_angle) * minute_length)
        minute_color = PressureUIColors.PRESSURE_RED if is_urgent else PressureUIColors.HIGHLIGHT_WHITE
        pygame.draw.line(screen, minute_color, center, (minute_x, minute_y), 3)

        # Center dot
        pygame.draw.circle(screen, PressureUIColors.TIME_GOLD, center, 6)
        pygame.draw.circle(screen, PressureUIColors.HIGHLIGHT_WHITE, center, 3)

        # Animated second hand when urgent
        if is_urgent:
            second = int((t * 2) % 60)
            second_angle = math.radians(second * 6 - 90)
            second_length = radius * 0.85
            second_x = center[0] + int(math.cos(second_angle) * second_length)
            second_y = center[1] + int(math.sin(second_angle) * second_length)
            pygame.draw.line(screen, PressureUIColors.PRESSURE_RED, center, (second_x, second_y), 2)

    def draw_notification_card(self, screen: pygame.Surface, rect: pygame.Rect,
                               title: str, time_text: str, description: str,
                               color: Tuple[int, int, int],
                               icon: str = "", is_hover: bool = False,
                               is_dragging: bool = False,
                               is_urgent: bool = False) -> None:
        """Draw a styled notification card"""
        t = self.get_time()

        # Urgent glow
        if is_urgent:
            pulse = (math.sin(t * 5) + 1) / 2
            PressureVisualHelpers.draw_urgent_glow(screen, rect.center, rect.width // 2,
                                                   PressureUIColors.PRESSURE_RED, 0.4 + pulse * 0.3)

        # Shadow
        shadow_offset = 10 if is_dragging else 4
        shadow_alpha = 80 if is_dragging else 40
        PressureVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                          PressureUIMetrics.RADIUS_MEDIUM)

        # Card background
        bg_color = color if not is_hover else PressureVisualHelpers.lighten_color(color, 1.15)
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (*bg_color, 240),
                        (0, 0, rect.width, rect.height),
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Top highlight
        highlight_rect = pygame.Rect(2, 2, rect.width - 4, rect.height // 4)
        highlight_color = PressureVisualHelpers.lighten_color(color, 1.2)
        pygame.draw.rect(card_surface, (*highlight_color, 60), highlight_rect,
                        border_top_left_radius=PressureUIMetrics.RADIUS_MEDIUM - 1,
                        border_top_right_radius=PressureUIMetrics.RADIUS_MEDIUM - 1)

        screen.blit(card_surface, rect)

        # Border
        border_color = PressureUIColors.HIGHLIGHT_WHITE if is_hover else PressureVisualHelpers.lighten_color(color, 1.3)
        border_width = 2 if is_dragging else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Icon
        text_x = rect.x + 12
        if icon:
            icon_surface = self.fonts['body'].render(icon, True, PressureUIColors.TEXT_PRIMARY)
            screen.blit(icon_surface, (text_x, rect.y + 12))
            text_x += 28

        # Title
        title_surface = self.fonts['body'].render(title, True, PressureUIColors.TEXT_PRIMARY)
        screen.blit(title_surface, (text_x, rect.y + 12))

        # Time badge
        time_bg_rect = pygame.Rect(rect.right - 70, rect.y + 10, 60, 24)
        pygame.draw.rect(screen, (0, 0, 0, 120), time_bg_rect,
                        border_radius=PressureUIMetrics.RADIUS_SMALL)
        time_surface = self.fonts['small'].render(time_text, True, PressureUIColors.TEXT_WARNING)
        screen.blit(time_surface, (time_bg_rect.x + 6, time_bg_rect.y + 4))

        # Description
        desc_surface = self.fonts['small'].render(description[:35], True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(desc_surface, (rect.x + 12, rect.y + 45))

    def draw_calendar_slot(self, screen: pygame.Surface, rect: pygame.Rect,
                           time_label: str, has_conflict: bool = False,
                           conflict_intensity: float = 0.0,
                           is_hover: bool = False, items_count: int = 0) -> None:
        """Draw a calendar time slot"""
        t = self.get_time()

        # Background color based on state
        if has_conflict:
            flash = (math.sin(t * 6) + 1) / 2
            bg_color = PressureVisualHelpers.interpolate_color(
                PressureUIColors.PRESSURE_RED_DARK,
                PressureUIColors.PRESSURE_RED,
                flash * conflict_intensity
            )
        elif is_hover:
            bg_color = PressureUIColors.CALM_BLUE_DARK
        else:
            bg_color = PressureUIColors.PANEL_BG_LIGHT

        # Slot background
        pygame.draw.rect(screen, bg_color, rect, border_radius=PressureUIMetrics.RADIUS_SMALL)

        # Border
        if has_conflict:
            PressureVisualHelpers.draw_warning_border(screen, rect, t, conflict_intensity,
                                                      PressureUIMetrics.RADIUS_SMALL)
        else:
            border_color = PressureUIColors.CALM_BLUE if is_hover else PressureUIColors.PANEL_BORDER
            pygame.draw.rect(screen, border_color, rect, 2,
                           border_radius=PressureUIMetrics.RADIUS_SMALL)

        # Time label (to the left of the slot)
        time_surface = self.fonts['body'].render(time_label, True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(time_surface, (rect.x - 80, rect.centery - time_surface.get_height() // 2))

        # Overlap warning
        if items_count > 1:
            overlap_text = f"{items_count} OVERLAP!"
            overlap_surface = self.fonts['small'].render(overlap_text, True, PressureUIColors.TEXT_URGENT)
            overlap_surface.set_alpha(int(150 + (math.sin(t * 4) + 1) / 2 * 105))
            screen.blit(overlap_surface, (rect.right - overlap_surface.get_width() - 10, rect.y + 8))

    def draw_stress_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                          stress_level: float, label: str = "STRESS") -> None:
        """Draw a stress meter with pulsing effect at high levels"""
        t = self.get_time()

        # Background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, rect,
                        border_radius=rect.height // 2)

        # Fill with gradient
        if stress_level > 0:
            pulse = 1.0
            if stress_level > 0.8:
                pulse = 1 + (math.sin(t * 8) * 0.05)

            fill_width = int((rect.width - 4) * min(1.0, stress_level * pulse))

            for x in range(fill_width):
                progress = x / max(1, rect.width - 4)
                color = PressureVisualHelpers.interpolate_color(
                    PressureUIColors.URGENT_ORANGE,
                    PressureUIColors.PRESSURE_RED,
                    progress
                )
                pygame.draw.line(screen, color,
                               (rect.x + 2 + x, rect.y + 2),
                               (rect.x + 2 + x, rect.bottom - 2))

        # Border with pulse at high stress
        if stress_level > 0.9:
            flash = (math.sin(t * 6) + 1) / 2
            border_color = PressureVisualHelpers.interpolate_color(
                PressureUIColors.PRESSURE_RED,
                PressureUIColors.HIGHLIGHT_WHITE,
                flash * 0.5
            )
        else:
            border_color = PressureUIColors.URGENT_ORANGE if stress_level > 0.5 else PressureUIColors.PANEL_BORDER

        pygame.draw.rect(screen, border_color, rect, 2, border_radius=rect.height // 2)

        # Label
        label_surface = self.fonts['small'].render(label, True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(label_surface, (rect.centerx - label_surface.get_width() // 2, rect.y - 22))

        # Warning at max
        if stress_level >= 1.0:
            warning_surface = self.fonts['small'].render("MAXIMUM", True, PressureUIColors.TEXT_URGENT)
            warning_surface.set_alpha(int(150 + (math.sin(t * 5) + 1) / 2 * 105))
            screen.blit(warning_surface, (rect.centerx - warning_surface.get_width() // 2, rect.bottom + 5))

    def draw_mail_envelope(self, screen: pygame.Surface, rect: pygame.Rect,
                           title: str, preview: str,
                           color: Tuple[int, int, int],
                           is_important: bool = False,
                           is_opened: bool = False,
                           is_hover: bool = False) -> None:
        """Draw a styled mail envelope"""
        t = self.get_time()

        # Important glow
        if is_important and not is_opened:
            pulse = (math.sin(t * 4) + 1) / 2
            PressureVisualHelpers.draw_urgent_glow(screen, rect.center, rect.width // 2,
                                                   PressureUIColors.PRESSURE_RED, 0.4 + pulse * 0.4)

        # Shadow
        shadow_offset = 6 if is_hover else 4
        PressureVisualHelpers.draw_shadow(screen, rect, shadow_offset, 50,
                                          PressureUIMetrics.RADIUS_MEDIUM)

        # Envelope body
        env_color = color if not is_opened else PressureVisualHelpers.darken_color(color, 0.6)
        if is_hover and not is_opened:
            env_color = PressureVisualHelpers.lighten_color(color, 1.15)

        pygame.draw.rect(screen, env_color, rect, border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Envelope flap (triangle at top)
        if not is_opened:
            flap_points = [
                (rect.x + 2, rect.y + 2),
                (rect.centerx, rect.y + rect.height // 3),
                (rect.right - 2, rect.y + 2)
            ]
            flap_color = PressureVisualHelpers.darken_color(env_color, 0.85)
            pygame.draw.polygon(screen, flap_color, flap_points)
            pygame.draw.lines(screen, PressureUIColors.HIGHLIGHT_DIM, False, flap_points, 1)

        # Border
        if is_important and not is_opened:
            flash = (math.sin(t * 4) + 1) / 2
            border_color = PressureVisualHelpers.interpolate_color(
                PressureUIColors.PRESSURE_RED,
                PressureUIColors.HIGHLIGHT_WHITE,
                flash * 0.5
            )
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=PressureUIMetrics.RADIUS_MEDIUM)
        else:
            border_color = PressureUIColors.HIGHLIGHT_DIM
            pygame.draw.rect(screen, border_color, rect, 1, border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # URGENT stamp for important mail
        if is_important and not is_opened:
            stamp_rect = pygame.Rect(rect.right - 65, rect.y + 6, 58, 22)
            pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED, stamp_rect,
                           border_radius=PressureUIMetrics.RADIUS_SMALL)
            stamp_text = self.fonts['tiny'].render("URGENT", True, PressureUIColors.HIGHLIGHT_WHITE)
            screen.blit(stamp_text, (stamp_rect.x + 6, stamp_rect.y + 4))

        # Title
        title_y = rect.y + rect.height // 3 + 8 if not is_opened else rect.y + 15
        title_color = PressureUIColors.TEXT_DARK if not is_opened else PressureUIColors.TEXT_MUTED
        title_surface = self.fonts['body'].render(title, True, title_color)
        screen.blit(title_surface, (rect.x + 15, title_y))

        # Preview
        preview_surface = self.fonts['small'].render(preview[:30], True, PressureUIColors.TEXT_MUTED)
        screen.blit(preview_surface, (rect.x + 15, title_y + 25))

        # Opened indicator
        if is_opened:
            opened_surface = self.fonts['tiny'].render("[OPENED]", True, PressureUIColors.TEXT_MUTED)
            screen.blit(opened_surface, (rect.right - 65, rect.y + 6))

    def draw_choice_panel(self, screen: pygame.Surface, rect: pygame.Rect,
                          text: str, number: int,
                          is_hover: bool = False,
                          is_selected: bool = False,
                          has_consequence: bool = True) -> None:
        """Draw a choice panel for dialogue"""
        t = self.get_time()

        # Shadow
        PressureVisualHelpers.draw_shadow(screen, rect, 4, 40, PressureUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_selected:
            bg_color = (70, 90, 70)
        elif is_hover:
            bg_color = (60, 65, 80)
        else:
            bg_color = PressureUIColors.PANEL_BG_LIGHT

        pygame.draw.rect(screen, bg_color, rect, border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Warning tint overlay for choices with consequences
        if has_consequence and not is_selected:
            warning_overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(warning_overlay, (*PressureUIColors.URGENT_ORANGE, 15),
                           (0, 0, rect.width, rect.height),
                           border_radius=PressureUIMetrics.RADIUS_MEDIUM)
            screen.blit(warning_overlay, rect)

        # Border
        if is_selected:
            border_color = PressureUIColors.SUCCESS_GREEN
        elif is_hover:
            border_color = PressureUIColors.CALM_BLUE_LIGHT
        else:
            border_color = PressureUIColors.PANEL_BORDER

        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Number badge
        num_surface = self.fonts['body'].render(f"[{number}]", True, PressureUIColors.TEXT_MUTED)
        screen.blit(num_surface, (rect.x + 15, rect.centery - num_surface.get_height() // 2))

        # Choice text
        text_color = PressureUIColors.TEXT_PRIMARY if is_hover or is_selected else PressureUIColors.TEXT_SECONDARY
        text_surface = self.fonts['body'].render(text, True, text_color)
        screen.blit(text_surface, (rect.x + 60, rect.centery - text_surface.get_height() // 2))

    def draw_conflict_warning(self, screen: pygame.Surface, rect: pygame.Rect,
                              text: str, sub_text: str = "") -> None:
        """Draw a flashing conflict warning box"""
        t = self.get_time()
        flash = int((t * 4) % 2)

        # Background with flash
        if flash:
            bg_color = PressureUIColors.PRESSURE_RED_DARK
        else:
            bg_color = (100, 30, 30)

        PressureVisualHelpers.draw_shadow(screen, rect, 6, 60, PressureUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, bg_color, rect, border_radius=PressureUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED_LIGHT, rect, 3,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Main text
        text_surface = self.fonts['heading'].render(text, True, PressureUIColors.TEXT_URGENT)
        screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.y + 12))

        # Sub text
        if sub_text:
            sub_surface = self.fonts['small'].render(sub_text, True, PressureUIColors.TEXT_WARNING)
            screen.blit(sub_surface, (rect.centerx - sub_surface.get_width() // 2, rect.y + 42))

    def draw_pressure_background(self, screen: pygame.Surface, rect: pygame.Rect,
                                  stress_level: float = 0.0) -> None:
        """Draw a background that shifts based on stress level"""
        calm_color = PressureUIColors.DARK_BG_CALM
        stress_color = PressureUIColors.DARK_BG_STRESS

        bg_color = PressureVisualHelpers.interpolate_color(calm_color, stress_color, stress_level)
        screen.fill(bg_color)

        # Add stress vignette
        if stress_level > 0.2:
            PressureVisualHelpers.draw_stress_vignette(screen, stress_level)

    def draw_result_box(self, screen: pygame.Surface, rect: pygame.Rect,
                        result_text: str, consequence_text: str,
                        is_positive: bool = False) -> None:
        """Draw a result box showing outcome and consequence"""
        PressureVisualHelpers.draw_shadow(screen, rect, 8, 60, PressureUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, rect,
                        border_radius=PressureUIMetrics.RADIUS_LARGE)

        # Border color based on outcome
        border_color = PressureUIColors.SUCCESS_GREEN if is_positive else PressureUIColors.PRESSURE_RED
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=PressureUIMetrics.RADIUS_LARGE)

        # Result text (positive)
        result_color = PressureUIColors.SUCCESS_GREEN_LIGHT if is_positive else PressureUIColors.TEXT_WARNING
        result_surface = self.fonts['body'].render(result_text, True, result_color)
        screen.blit(result_surface, (rect.x + 20, rect.y + 20))

        # Consequence text (negative)
        cons_surface = self.fonts['small'].render(consequence_text, True, PressureUIColors.TEXT_URGENT)
        screen.blit(cons_surface, (rect.x + 20, rect.y + 55))


# Global instance for easy access
pressure_visuals = PressureVisualComponents()

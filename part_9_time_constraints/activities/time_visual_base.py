"""
Time Constraints Visual Base Module - Professional Version
Pressure/Urgency themed colors, helpers, and visual components
For Part 9 (Time Constraints / Conflicting Responsibilities) mini-games
Clean, performant visuals with no per-frame surface creation
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass


class PressureUIColors:
    """Pressure/Urgency color palette - professional theme"""

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
    BACKGROUND = (35, 38, 48)
    BACKGROUND_LIGHT = (45, 48, 58)
    DARK_BG = (25, 25, 35)
    DARK_BG_STRESS = (45, 25, 30)
    DARK_BG_CALM = (25, 30, 40)

    # Card backgrounds
    CARD_BG = (50, 55, 68)
    CARD_BG_HOVER = (60, 65, 80)
    CARD_BG_ACTIVE = (70, 75, 90)
    CARD_BORDER = (75, 80, 95)

    # Border colors
    BORDER_DEFAULT = (75, 80, 95)
    BORDER_HOVER = (110, 120, 140)
    BORDER_ACTIVE = (140, 150, 170)

    # Slot colors
    SLOT_EMPTY = (38, 42, 52)
    SLOT_FILLED = (45, 55, 50)
    SLOT_HIGHLIGHT = (50, 60, 75)

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
    TEXT_LIGHT = (250, 250, 252)
    TEXT_SUCCESS = (120, 200, 140)
    TEXT_ERROR = (220, 100, 100)


class PressureUIMetrics:
    """Consistent spacing and sizing for pressure theme - 8px grid"""

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

    # Shadows - simple, not layered
    SHADOW_SM = 2
    SHADOW_MD = 4
    SHADOW_LG = 6

    # Card dimensions
    CARD_WIDTH = 180
    CARD_HEIGHT = 80
    CARD_PADDING = 16

    # Calendar slot dimensions
    SLOT_WIDTH = 280
    SLOT_HEIGHT = 70

    # Clock dimensions
    CLOCK_RADIUS = 45
    CLOCK_RADIUS_SMALL = 30

    # Stress meter dimensions
    METER_WIDTH = 300
    METER_HEIGHT = 30

    # Button sizes
    BUTTON_HEIGHT = 44
    BUTTON_HEIGHT_SM = 36


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


class PressureVisualHelpers:
    """Static helper functions for drawing pressure-themed elements"""

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                   offset: int = 4, alpha: int = 35, radius: int = 0) -> None:
        """Draw a simple shadow behind a rectangle"""
        shadow_surface = pygame.Surface(
            (rect.width + offset, rect.height + offset),
            pygame.SRCALPHA
        )
        shadow_rect = pygame.Rect(offset // 2, offset // 2, rect.width, rect.height)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_rect,
                        border_radius=radius)
        screen.blit(shadow_surface, (rect.x, rect.y + offset // 2))

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
    def get_pulse_value(speed: float = 3.0, min_val: float = 0.5, max_val: float = 1.0) -> float:
        """Get a simple pulsing value between min and max"""
        t = time.time() * speed
        return min_val + (max_val - min_val) * (0.5 + 0.5 * math.sin(t))

    @staticmethod
    def get_pulse_alpha(min_alpha: int = 180, max_alpha: int = 255, speed: float = 2.0) -> int:
        """Get a pulsing alpha value"""
        return int(PressureVisualHelpers.get_pulse_value(speed, min_alpha / 255, max_alpha / 255) * 255)

    @staticmethod
    def draw_simple_overlay(screen: pygame.Surface, color: Tuple[int, int, int],
                           alpha: int) -> None:
        """Draw a simple color overlay on the screen"""
        if alpha <= 0:
            return
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((*color, min(255, alpha)))
        screen.blit(overlay, (0, 0))


class PressureVisualComponents:
    """Reusable visual components for time constraint games - clean and performant"""

    def __init__(self):
        self.fonts = {}
        self._init_fonts()
        # Cache for expensive surfaces
        self._cached_background = None
        self._cached_background_size = (0, 0)

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 42, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('SF Pro Display', 32, bold=True)
            self.fonts['subheading'] = pygame.font.SysFont('SF Pro Display', 26)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 22)
            self.fonts['body_bold'] = pygame.font.SysFont('SF Pro Text', 22, bold=True)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 18)
            self.fonts['small_bold'] = pygame.font.SysFont('SF Pro Text', 18, bold=True)
            self.fonts['tiny'] = pygame.font.SysFont('SF Pro Text', 14)
            self.fonts['clock'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.fonts['urgent'] = pygame.font.SysFont('Impact', 40, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 48)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['subheading'] = pygame.font.Font(None, 30)
            self.fonts['body'] = pygame.font.Font(None, 26)
            self.fonts['body_bold'] = pygame.font.Font(None, 26)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['small_bold'] = pygame.font.Font(None, 20)
            self.fonts['tiny'] = pygame.font.Font(None, 16)
            self.fonts['clock'] = pygame.font.Font(None, 32)
            self.fonts['urgent'] = pygame.font.Font(None, 44)

    def draw_background(self, screen: pygame.Surface, stress_level: float = 0.0) -> None:
        """Draw a clean background with optional stress tint"""
        # Interpolate between calm and stress backgrounds
        bg_color = PressureVisualHelpers.interpolate_color(
            PressureUIColors.DARK_BG_CALM,
            PressureUIColors.DARK_BG_STRESS,
            stress_level
        )
        screen.fill(bg_color)

    def draw_stress_overlay(self, screen: pygame.Surface, stress_level: float) -> None:
        """Draw a simple stress overlay (replaces vignette)"""
        if stress_level > 0.2:
            alpha = int(stress_level * 40)
            PressureVisualHelpers.draw_simple_overlay(
                screen, PressureUIColors.PRESSURE_RED_DARK, alpha
            )

    def draw_title(self, screen: pygame.Surface, text: str,
                  center_x: int, y: int) -> None:
        """Draw centered title text"""
        text_surface = self.fonts['title'].render(text, True, PressureUIColors.TEXT_PRIMARY)
        screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

    def draw_instruction_text(self, screen: pygame.Surface, text: str,
                             center_x: int, y: int) -> None:
        """Draw centered instruction text"""
        text_surface = self.fonts['body'].render(text, True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

    def draw_clock_face(self, screen: pygame.Surface, center: Tuple[int, int],
                        radius: int, hour: int = 3, minute: int = 0,
                        is_urgent: bool = False) -> None:
        """Draw an analog clock face - clean version"""
        # Clock face background
        pygame.draw.circle(screen, PressureUIColors.PANEL_BG_LIGHT, center, radius)

        # Border - urgent uses red, normal uses gold
        border_color = PressureUIColors.PRESSURE_RED if is_urgent else PressureUIColors.TIME_GOLD
        pygame.draw.circle(screen, border_color, center, radius, 3)

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

    def draw_notification_card(self, screen: pygame.Surface, rect: pygame.Rect,
                               title: str, time_text: str, description: str,
                               color: Tuple[int, int, int],
                               icon: str = "", is_hover: bool = False,
                               is_dragging: bool = False,
                               is_urgent: bool = False) -> None:
        """Draw a styled notification card - clean version"""
        # Shadow (larger when dragging)
        shadow_offset = PressureUIMetrics.SHADOW_LG if is_dragging else PressureUIMetrics.SHADOW_MD
        shadow_alpha = 50 if is_dragging else 35
        PressureVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                         PressureUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_dragging:
            bg_color = PressureUIColors.CARD_BG_ACTIVE
        elif is_hover:
            bg_color = PressureUIColors.CARD_BG_HOVER
        else:
            bg_color = PressureUIColors.CARD_BG

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Color strip at top
        strip_rect = pygame.Rect(rect.x, rect.y, rect.width, 6)
        pygame.draw.rect(screen, color, strip_rect,
                        border_top_left_radius=PressureUIMetrics.RADIUS_MEDIUM,
                        border_top_right_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Border
        border_color = color if is_hover or is_dragging or is_urgent else PressureUIColors.CARD_BORDER
        border_width = 2 if is_dragging or is_urgent else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Icon
        text_x = rect.x + 12
        if icon:
            icon_surface = self.fonts['body'].render(icon, True, color)
            screen.blit(icon_surface, (text_x, rect.y + 14))
            text_x += 28

        # Title
        title_surface = self.fonts['body_bold'].render(title, True, PressureUIColors.TEXT_PRIMARY)
        screen.blit(title_surface, (text_x, rect.y + 14))

        # Time badge
        time_bg_rect = pygame.Rect(rect.right - 70, rect.y + 12, 60, 24)
        badge_color = PressureUIColors.PRESSURE_RED_DARK if is_urgent else (0, 0, 0)
        pygame.draw.rect(screen, (*badge_color, 180) if len(badge_color) == 3 else badge_color,
                        time_bg_rect, border_radius=PressureUIMetrics.RADIUS_SMALL)
        time_surface = self.fonts['small'].render(time_text, True, PressureUIColors.TEXT_WARNING)
        screen.blit(time_surface, (time_bg_rect.x + 6, time_bg_rect.y + 4))

        # Description
        desc_surface = self.fonts['small'].render(description[:35], True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(desc_surface, (rect.x + 12, rect.y + 48))

    def draw_calendar_slot(self, screen: pygame.Surface, rect: pygame.Rect,
                           time_label: str, has_conflict: bool = False,
                           is_hover: bool = False, items_count: int = 0) -> None:
        """Draw a calendar time slot - clean version"""
        # Shadow
        PressureVisualHelpers.draw_shadow(screen, rect,
                                         PressureUIMetrics.SHADOW_SM, 25,
                                         PressureUIMetrics.RADIUS_SMALL)

        # Background color based on state
        if has_conflict:
            bg_color = PressureUIColors.PRESSURE_RED_DARK
        elif is_hover:
            bg_color = PressureUIColors.SLOT_HIGHLIGHT
        else:
            bg_color = PressureUIColors.SLOT_EMPTY

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=PressureUIMetrics.RADIUS_SMALL)

        # Border
        if has_conflict:
            border_color = PressureUIColors.PRESSURE_RED
        elif is_hover:
            border_color = PressureUIColors.CALM_BLUE
        else:
            border_color = PressureUIColors.PANEL_BORDER

        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=PressureUIMetrics.RADIUS_SMALL)

        # Time label (to the left of the slot)
        time_surface = self.fonts['body'].render(time_label, True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(time_surface, (rect.x - 80, rect.centery - time_surface.get_height() // 2))

        # Overlap warning
        if items_count > 1:
            overlap_text = f"{items_count} OVERLAP!"
            overlap_surface = self.fonts['small_bold'].render(overlap_text, True, PressureUIColors.TEXT_URGENT)
            screen.blit(overlap_surface, (rect.right - overlap_surface.get_width() - 10, rect.y + 8))

    def draw_stress_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                          stress_level: float, label: str = "STRESS") -> None:
        """Draw a stress meter - clean version without pulsing"""
        # Background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, rect,
                        border_radius=rect.height // 2)

        # Fill
        if stress_level > 0:
            fill_width = int((rect.width - 4) * min(1.0, stress_level))

            # Color based on stress level
            if stress_level > 0.8:
                fill_color = PressureUIColors.PRESSURE_RED
            elif stress_level > 0.5:
                fill_color = PressureUIColors.URGENT_ORANGE
            else:
                fill_color = PressureUIColors.CALM_BLUE

            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, fill_width, rect.height - 4)
            pygame.draw.rect(screen, fill_color, fill_rect,
                            border_radius=(rect.height - 4) // 2)

        # Border
        border_color = PressureUIColors.PRESSURE_RED if stress_level > 0.9 else PressureUIColors.PANEL_BORDER
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=rect.height // 2)

        # Label
        label_surface = self.fonts['small'].render(label, True, PressureUIColors.TEXT_SECONDARY)
        screen.blit(label_surface, (rect.centerx - label_surface.get_width() // 2, rect.y - 22))

        # Warning at max
        if stress_level >= 1.0:
            warning_surface = self.fonts['small_bold'].render("MAXIMUM", True, PressureUIColors.TEXT_URGENT)
            screen.blit(warning_surface, (rect.centerx - warning_surface.get_width() // 2, rect.bottom + 5))

    def draw_mail_envelope(self, screen: pygame.Surface, rect: pygame.Rect,
                           title: str, preview: str,
                           color: Tuple[int, int, int],
                           is_important: bool = False,
                           is_opened: bool = False,
                           is_hover: bool = False) -> None:
        """Draw a styled mail envelope - clean version"""
        # Shadow
        shadow_offset = PressureUIMetrics.SHADOW_LG if is_hover else PressureUIMetrics.SHADOW_MD
        PressureVisualHelpers.draw_shadow(screen, rect, shadow_offset, 40,
                                         PressureUIMetrics.RADIUS_MEDIUM)

        # Envelope body
        env_color = color if not is_opened else PressureVisualHelpers.darken_color(color, 0.6)
        if is_hover and not is_opened:
            env_color = PressureVisualHelpers.lighten_color(color, 1.15)

        pygame.draw.rect(screen, env_color, rect,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

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
            border_color = PressureUIColors.PRESSURE_RED
            border_width = 3
        else:
            border_color = PressureUIColors.HIGHLIGHT_DIM
            border_width = 1

        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

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
                          color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a choice panel for dialogue - clean version"""
        # Shadow
        shadow_offset = PressureUIMetrics.SHADOW_MD if is_hover else PressureUIMetrics.SHADOW_SM
        PressureVisualHelpers.draw_shadow(screen, rect, shadow_offset, 30,
                                         PressureUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_selected:
            bg_color = PressureUIColors.SUCCESS_GREEN_LIGHT if color is None else color
            bg_color = PressureVisualHelpers.darken_color(bg_color, 0.4)
        elif is_hover:
            bg_color = PressureUIColors.CARD_BG_HOVER
        else:
            bg_color = PressureUIColors.CARD_BG

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Border
        if is_selected:
            border_color = PressureUIColors.SUCCESS_GREEN
        elif is_hover:
            border_color = PressureUIColors.CALM_BLUE_LIGHT
        else:
            border_color = PressureUIColors.CARD_BORDER

        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Number circle
        num_center = (rect.x + 28, rect.centery)
        num_color = color if color and is_hover else (
            PressureUIColors.CALM_BLUE if is_hover else PressureUIColors.TEXT_MUTED
        )
        pygame.draw.circle(screen, num_color, num_center, 14)

        num_text = self.fonts['small_bold'].render(str(number), True, PressureUIColors.TEXT_LIGHT)
        num_rect = num_text.get_rect(center=num_center)
        screen.blit(num_text, num_rect)

        # Choice text
        text_color = PressureUIColors.TEXT_LIGHT if is_selected else PressureUIColors.TEXT_PRIMARY
        text_surface = self.fonts['body'].render(text, True, text_color)
        screen.blit(text_surface, (rect.x + 52, rect.centery - text_surface.get_height() // 2))

    def draw_conflict_warning(self, screen: pygame.Surface, rect: pygame.Rect,
                              text: str, sub_text: str = "") -> None:
        """Draw a conflict warning box - clean version"""
        # Shadow
        PressureVisualHelpers.draw_shadow(screen, rect,
                                         PressureUIMetrics.SHADOW_LG, 50,
                                         PressureUIMetrics.RADIUS_MEDIUM)

        # Background
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED_DARK, rect,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Border
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED_LIGHT, rect, 3,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Main text
        text_surface = self.fonts['heading'].render(text, True, PressureUIColors.TEXT_URGENT)
        screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.y + 12))

        # Sub text
        if sub_text:
            sub_surface = self.fonts['small'].render(sub_text, True, PressureUIColors.TEXT_WARNING)
            screen.blit(sub_surface, (rect.centerx - sub_surface.get_width() // 2, rect.y + 42))

    def draw_result_box(self, screen: pygame.Surface, rect: pygame.Rect,
                        result_text: str, consequence_text: str,
                        is_positive: bool = False) -> None:
        """Draw a result box showing outcome and consequence"""
        # Shadow
        PressureVisualHelpers.draw_shadow(screen, rect,
                                         PressureUIMetrics.SHADOW_LG, 50,
                                         PressureUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, rect,
                        border_radius=PressureUIMetrics.RADIUS_LARGE)

        # Border color based on outcome
        border_color = PressureUIColors.SUCCESS_GREEN if is_positive else PressureUIColors.PRESSURE_RED
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=PressureUIMetrics.RADIUS_LARGE)

        # Result text (positive)
        result_color = PressureUIColors.TEXT_SUCCESS if is_positive else PressureUIColors.TEXT_WARNING
        result_surface = self.fonts['body'].render(result_text, True, result_color)
        screen.blit(result_surface, (rect.x + 20, rect.y + 20))

        # Consequence text (negative)
        cons_surface = self.fonts['small'].render(consequence_text, True, PressureUIColors.TEXT_URGENT)
        screen.blit(cons_surface, (rect.x + 20, rect.y + 55))

    def draw_priority_notification(self, screen: pygame.Surface, rect: pygame.Rect,
                                   text: str, color: Tuple[int, int, int],
                                   is_active: bool = True) -> None:
        """Draw a priority notification for stress overload sequence"""
        # Shadow
        PressureVisualHelpers.draw_shadow(screen, rect,
                                         PressureUIMetrics.SHADOW_MD, 35,
                                         PressureUIMetrics.RADIUS_MEDIUM)

        # Background
        bg_color = color if is_active else PressureVisualHelpers.darken_color(color, 0.5)
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Border
        border_color = PressureUIColors.HIGHLIGHT_WHITE if is_active else PressureUIColors.PANEL_BORDER
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        # Text
        text_surface = self.fonts['body_bold'].render(text, True, PressureUIColors.TEXT_LIGHT)
        screen.blit(text_surface,
                   (rect.centerx - text_surface.get_width() // 2,
                    rect.centery - text_surface.get_height() // 2))

    def draw_status_banner(self, screen: pygame.Surface, text: str,
                          center_x: int, y: int,
                          status: str = "info", alpha: int = 255) -> None:
        """Draw a simple status banner"""
        # Status colors
        if status == "success":
            bg_color = PressureUIColors.SUCCESS_GREEN
        elif status == "error":
            bg_color = PressureUIColors.PRESSURE_RED
        elif status == "warning":
            bg_color = PressureUIColors.URGENT_ORANGE
        else:
            bg_color = PressureUIColors.CALM_BLUE

        # Render text to get width
        text_surface = self.fonts['body_bold'].render(text, True, PressureUIColors.TEXT_LIGHT)
        padding = PressureUIMetrics.SPACING_MD

        # Banner rect
        banner_width = text_surface.get_width() + padding * 2
        banner_height = text_surface.get_height() + padding
        banner_rect = pygame.Rect(center_x - banner_width // 2, y,
                                 banner_width, banner_height)

        # Draw banner with alpha
        banner_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        pygame.draw.rect(banner_surface, (*bg_color, alpha),
                        (0, 0, banner_width, banner_height),
                        border_radius=PressureUIMetrics.RADIUS_MEDIUM)

        screen.blit(banner_surface, banner_rect.topleft)

        # Text
        if alpha >= 200:
            screen.blit(text_surface, (banner_rect.x + padding, banner_rect.y + padding // 2))
        else:
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (banner_rect.x + padding, banner_rect.y + padding // 2))

    def draw_modal_overlay(self, screen: pygame.Surface, alpha: int = 160) -> None:
        """Draw a dark modal overlay"""
        PressureVisualHelpers.draw_simple_overlay(screen, (0, 0, 0), alpha)

    def draw_continue_prompt(self, screen: pygame.Surface, center_x: int, y: int,
                            visible: bool = True) -> None:
        """Draw a continue prompt"""
        if not visible:
            return

        # Simple pulsing alpha
        alpha = PressureVisualHelpers.get_pulse_alpha(120, 255, 2.0)

        prompt_surface = self.fonts['small'].render("Press any key to continue...", True,
                                                    PressureUIColors.TEXT_MUTED)
        prompt_surface.set_alpha(alpha)
        screen.blit(prompt_surface, (center_x - prompt_surface.get_width() // 2, y))


# Global singleton for easy access
pressure_visuals = PressureVisualComponents()

# Backwards compatibility aliases
time_visuals = pressure_visuals
TimeUIColors = PressureUIColors
TimeUIMetrics = PressureUIMetrics
TimeVisualHelpers = PressureVisualHelpers
TimeVisualComponents = PressureVisualComponents

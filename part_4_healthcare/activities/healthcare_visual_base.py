"""
Healthcare Visual Base Module
Shared visual components for Part 4 (Healthcare Crisis) mini-games
Provides consistent styling, colors, and reusable UI components
"""

import pygame
import math
import time
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass


class HealthcareUIColors:
    """Healthcare-themed color palette"""

    # Primary Healthcare Theme
    HEALTHCARE_PRIMARY = (41, 128, 185)      # Medical blue
    HEALTHCARE_SECONDARY = (39, 174, 96)     # Health green
    HEALTHCARE_ACCENT = (231, 76, 60)        # Alert red (urgent)
    HEALTHCARE_NEUTRAL = (236, 240, 241)     # Clinical white/gray
    HEALTHCARE_WARM = (243, 156, 18)         # Warning orange
    HEALTHCARE_PURPLE = (155, 89, 182)       # Generic/special purple

    # Short aliases for convenience
    PRIMARY = HEALTHCARE_PRIMARY
    PRIMARY_DARK = (31, 108, 155)            # Darker primary
    PRIMARY_LIGHT = (220, 235, 250)          # Lighter primary bg
    SECONDARY = HEALTHCARE_SECONDARY
    ACCENT = HEALTHCARE_ACCENT
    NEUTRAL = HEALTHCARE_NEUTRAL

    # Document/Form Colors
    PAPER_BG = (253, 254, 254)               # Clean white paper
    PAPER_SHADOW = (230, 225, 218)           # Subtle paper shadow

    # Form field aliases
    FORM_FIELD = (245, 248, 250)             # Alias for FORM_FIELD_BG
    FORM_BORDER = (189, 195, 199)            # Alias for FORM_FIELD_BORDER
    PAPER_LINES = (235, 230, 225)            # Form lines
    FORM_FIELD_BG = (245, 248, 250)          # Input field background
    FORM_FIELD_BORDER = (189, 195, 199)      # Field borders
    FORM_FIELD_FOCUS = (52, 152, 219)        # Active field highlight

    # Status Indicators
    SUCCESS = (46, 204, 113)                 # Green - approved/correct
    ERROR = (231, 76, 60)                    # Red - denied/wrong
    WARNING = (241, 196, 15)                 # Yellow - pending/caution
    INFO = (52, 152, 219)                    # Blue - informational
    APPROVED = (46, 204, 113)                # Insurance approved
    DENIED = (231, 76, 60)                   # Insurance denied
    PENDING = (241, 196, 15)                 # Processing

    # Medication/Pharmacy
    AFFORDABLE = (46, 204, 113)              # Green - can afford
    EXPENSIVE = (231, 76, 60)                # Red - too expensive
    GENERIC = (155, 89, 182)                 # Purple - generic option
    BRAND = (52, 73, 94)                     # Dark - brand name

    # Stress/Anxiety
    CALM = (46, 204, 113)                    # Green - relaxed
    STRESSED = (231, 76, 60)                 # Red - high anxiety
    BREATHING_INHALE = (52, 152, 219)        # Blue - inhale
    BREATHING_HOLD = (241, 196, 15)          # Yellow - hold
    BREATHING_EXHALE = (46, 204, 113)        # Green - exhale

    # Mail Types
    MAIL_JUNK = (189, 195, 199)              # Gray - junk mail
    MAIL_BILL = (243, 156, 18)               # Orange - bills
    MAIL_IMPORTANT = (52, 152, 219)          # Blue - important
    MAIL_URGENT = (231, 76, 60)              # Red - urgent/medical

    # UI Elements
    PANEL_BG = (28, 32, 40)                  # Dark panel background
    PANEL_BORDER = (52, 58, 70)              # Panel border
    BUTTON_DEFAULT = (55, 65, 81)            # Button normal
    BUTTON_HOVER = (71, 85, 105)             # Button hover
    BUTTON_ACTIVE = (52, 152, 219)           # Button active/pressed

    # Text Colors
    TEXT_PRIMARY = (30, 30, 40)              # Dark text on light bg
    TEXT_SECONDARY = (80, 85, 100)           # Secondary text
    TEXT_MUTED = (140, 145, 160)             # Muted/hint text
    TEXT_LIGHT = (255, 255, 255)             # Light text on dark bg

    # Timer Colors
    TIMER_SAFE = (46, 204, 113)              # Green - plenty of time
    TIMER_WARNING = (243, 156, 18)           # Orange - getting low
    TIMER_DANGER = (231, 76, 60)             # Red - almost out


class HealthcareUIMetrics:
    """Standardized spacing and sizing"""

    GRID_UNIT = 8

    # Spacing
    PADDING_SMALL = GRID_UNIT          # 8px
    PADDING = GRID_UNIT * 2            # 16px
    PADDING_LARGE = GRID_UNIT * 3      # 24px
    MARGIN = GRID_UNIT * 4             # 32px

    # Border radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_PILL = 999  # For pill-shaped buttons

    # Animation
    TRANSITION_SPEED = 0.15


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


class HealthcareVisualHelpers:
    """Helper functions for drawing common visual elements"""

    @staticmethod
    def color_lerp(color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                   t: float) -> Tuple[int, int, int]:
        """Linearly interpolate between two colors"""
        t = max(0.0, min(1.0, t))
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )

    @staticmethod
    def draw_vignette(screen: pygame.Surface, intensity: float = 0.5) -> None:
        """Draw a vignette effect on the screen"""
        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create radial gradient vignette
        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(0, height, 4):  # Step by 4 for performance
            for x in range(0, width, 4):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                alpha = int((dist / max_dist) * 180 * intensity)
                alpha = min(255, alpha)
                pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))

        screen.blit(vignette, (0, 0))

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                   offset: int = 4, blur_radius: int = 8, alpha: int = 60,
                   border_radius: int = 8) -> None:
        """Draw a soft shadow behind an element"""
        # blur_radius affects the shadow spread
        spread = blur_radius // 2
        shadow_surface = pygame.Surface((rect.width + offset * 2 + spread * 2,
                                        rect.height + offset * 2 + spread * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(offset + spread, offset + spread, rect.width, rect.height)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_rect,
                        border_radius=border_radius)
        screen.blit(shadow_surface, (rect.x - offset // 2 - spread, rect.y - offset // 2 - spread))

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

        if border_radius > 0:
            mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask_surface, (255, 255, 255),
                           (0, 0, rect.width, rect.height),
                           border_radius=border_radius)
            surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        screen.blit(surface, rect.topleft)

    @staticmethod
    def draw_dashed_rect(screen: pygame.Surface, color: Tuple[int, int, int, int],
                        rect: pygame.Rect, dash_length: int = 8,
                        gap_length: int = 4, width: int = 2) -> None:
        """Draw a rectangle with dashed border"""
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        step = dash_length + gap_length

        # Top edge
        for i in range(0, w, step):
            end_x = min(i + dash_length, w)
            pygame.draw.line(screen, color, (x + i, y), (x + end_x, y), width)

        # Bottom edge
        for i in range(0, w, step):
            end_x = min(i + dash_length, w)
            pygame.draw.line(screen, color, (x + i, y + h - 1), (x + end_x, y + h - 1), width)

        # Left edge
        for i in range(0, h, step):
            end_y = min(i + dash_length, h)
            pygame.draw.line(screen, color, (x, y + i), (x, y + end_y), width)

        # Right edge
        for i in range(0, h, step):
            end_y = min(i + dash_length, h)
            pygame.draw.line(screen, color, (x + w - 1, y + i), (x + w - 1, y + end_y), width)

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
    def draw_vignette(screen: pygame.Surface, intensity: float = 0.3) -> None:
        """Draw a vignette effect around screen edges"""
        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        # Create radial gradient from center
        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)

        for y in range(0, height, 4):  # Step by 4 for performance
            for x in range(0, width, 4):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                alpha = int(intensity * 255 * (dist / max_dist)**2)
                pygame.draw.rect(vignette, (0, 0, 0, min(alpha, 200)), (x, y, 4, 4))

        screen.blit(vignette, (0, 0))


class HealthcareVisualComponents:
    """Reusable visual components for healthcare mini-games"""

    def __init__(self):
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.fonts['subheading'] = pygame.font.SysFont('SF Pro Display', 22)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 18)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 14)
            self.fonts['tiny'] = pygame.font.SysFont('SF Pro Text', 12)
        except:
            self.fonts['title'] = pygame.font.Font(None, 42)
            self.fonts['heading'] = pygame.font.Font(None, 32)
            self.fonts['subheading'] = pygame.font.Font(None, 26)
            self.fonts['body'] = pygame.font.Font(None, 22)
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['tiny'] = pygame.font.Font(None, 14)

    def draw_paper_background(self, screen: pygame.Surface, rect: pygame.Rect,
                             with_lines: bool = True, shadow: bool = True,
                             header_text: str = None) -> None:
        """Draw a paper-like form background"""
        if shadow:
            HealthcareVisualHelpers.draw_shadow(screen, rect, offset=6, alpha=40,
                                               border_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Main paper surface
        pygame.draw.rect(screen, HealthcareUIColors.PAPER_BG, rect,
                        border_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Header bar if provided
        header_height = 0
        if header_text:
            header_height = 45
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_height)
            pygame.draw.rect(screen, HealthcareUIColors.HEALTHCARE_PRIMARY, header_rect,
                            border_top_left_radius=HealthcareUIMetrics.RADIUS_LARGE,
                            border_top_right_radius=HealthcareUIMetrics.RADIUS_LARGE)

            header_surface = self.fonts['subheading'].render(header_text, True,
                                                            HealthcareUIColors.TEXT_LIGHT)
            header_text_rect = header_surface.get_rect(center=(rect.centerx, rect.y + header_height // 2))
            screen.blit(header_surface, header_text_rect)

        # Paper texture - subtle gradient from top
        start_y = rect.y + header_height
        for y in range(min(50, rect.height - header_height)):
            alpha = int(15 * (1 - y / 50))
            pygame.draw.line(screen, (255, 255, 255, alpha),
                           (rect.x + HealthcareUIMetrics.RADIUS_LARGE, start_y + y),
                           (rect.right - HealthcareUIMetrics.RADIUS_LARGE, start_y + y))

        # Ruled lines
        if with_lines:
            line_start_y = rect.y + header_height + 40
            line_spacing = 28
            for y in range(line_start_y, rect.bottom - 30, line_spacing):
                pygame.draw.line(screen, HealthcareUIColors.PAPER_LINES,
                               (rect.x + 25, y), (rect.right - 25, y), 1)

        # Border
        pygame.draw.rect(screen, HealthcareUIColors.PAPER_SHADOW, rect, 2,
                        border_radius=HealthcareUIMetrics.RADIUS_LARGE)

    def draw_form_field(self, screen: pygame.Surface, rect: pygame.Rect,
                       label: str, value: str, state: str = 'normal',
                       show_cursor: bool = False) -> None:
        """
        Draw a professional form input field
        States: 'normal', 'filled', 'focus', 'error', 'success'
        """
        # Determine colors based on state
        if state == 'filled' or state == 'success':
            bg_color = (230, 255, 230)
            border_color = HealthcareUIColors.SUCCESS
        elif state == 'focus':
            bg_color = HealthcareUIColors.FORM_FIELD_BG
            border_color = HealthcareUIColors.FORM_FIELD_FOCUS
        elif state == 'error':
            bg_color = (255, 230, 230)
            border_color = HealthcareUIColors.ERROR
        else:
            bg_color = HealthcareUIColors.FORM_FIELD_BG
            border_color = HealthcareUIColors.FORM_FIELD_BORDER

        # Draw field background
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=HealthcareUIMetrics.RADIUS_SMALL)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=HealthcareUIMetrics.RADIUS_SMALL)

        # Draw label above field
        label_text = self.fonts['small'].render(label, True, HealthcareUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (rect.x, rect.y - 20))

        # Draw value
        if value:
            value_color = HealthcareUIColors.TEXT_PRIMARY if state != 'error' else HealthcareUIColors.ERROR
            display_value = value
            if show_cursor:
                display_value += '|'
            value_text = self.fonts['body'].render(display_value, True, value_color)
            screen.blit(value_text, (rect.x + 12, rect.y + rect.height // 2 - value_text.get_height() // 2))

    def draw_timer_arc(self, screen: pygame.Surface, center: Tuple[int, int],
                      radius: int, time_remaining: float, time_total: float,
                      show_text: bool = True) -> None:
        """Draw a circular timer arc with progress"""
        progress = max(0, min(1, time_remaining / time_total))

        # Determine color based on time
        if progress > 0.5:
            color = HealthcareUIColors.TIMER_SAFE
        elif progress > 0.2:
            color = HealthcareUIColors.TIMER_WARNING
        else:
            color = HealthcareUIColors.TIMER_DANGER
            # Pulsing effect when critical
            pulse = abs(math.sin(time.time() * 4)) * 0.3
            radius = int(radius * (1 + pulse * 0.1))

        # Background circle
        pygame.draw.circle(screen, (220, 225, 230), center, radius, 4)

        # Progress arc
        if progress > 0:
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * progress)

            # Draw arc using multiple small lines
            num_segments = max(1, int(50 * progress))
            points = []
            for i in range(num_segments + 1):
                angle = start_angle + (end_angle - start_angle) * i / num_segments
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))

            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 4)

        # Center fill
        pygame.draw.circle(screen, HealthcareUIColors.PAPER_BG, center, radius - 8)

        # Timer text
        if show_text:
            time_text = f"{int(time_remaining)}"
            text_surface = self.fonts['heading'].render(time_text, True, color)
            text_rect = text_surface.get_rect(center=center)
            screen.blit(text_surface, text_rect)

    def draw_mail_piece(self, screen: pygame.Surface, rect: pygame.Rect,
                       mail_type: str, label: str, is_dragging: bool = False,
                       is_hover: bool = False) -> None:
        """Draw a mail piece with type-specific styling"""
        # Get mail-specific color
        type_colors = {
            'junk': HealthcareUIColors.MAIL_JUNK,
            'bill': HealthcareUIColors.MAIL_BILL,
            'important': HealthcareUIColors.MAIL_IMPORTANT,
            'urgent': HealthcareUIColors.MAIL_URGENT,
            'medical': HealthcareUIColors.MAIL_URGENT,
        }
        type_color = type_colors.get(mail_type, HealthcareUIColors.MAIL_JUNK)

        # Shadow (larger when dragging)
        shadow_offset = 8 if is_dragging else 4
        shadow_alpha = 80 if is_dragging else 40
        HealthcareVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                           HealthcareUIMetrics.RADIUS_MEDIUM)

        # Mail background
        bg_color = HealthcareUIColors.PAPER_BG
        if is_dragging:
            bg_color = (240, 245, 255)
        elif is_hover:
            bg_color = (250, 252, 255)

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=HealthcareUIMetrics.RADIUS_MEDIUM)

        # Type indicator stripe on left edge
        stripe_rect = pygame.Rect(rect.x, rect.y, 6, rect.height)
        pygame.draw.rect(screen, type_color, stripe_rect,
                        border_top_left_radius=HealthcareUIMetrics.RADIUS_MEDIUM,
                        border_bottom_left_radius=HealthcareUIMetrics.RADIUS_MEDIUM)

        # Border
        border_color = type_color if is_dragging else HealthcareUIColors.FORM_FIELD_BORDER
        border_width = 2 if is_dragging else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=HealthcareUIMetrics.RADIUS_MEDIUM)

        # Label
        label_text = self.fonts['body'].render(label, True, HealthcareUIColors.TEXT_PRIMARY)
        screen.blit(label_text, (rect.x + 15, rect.centery - label_text.get_height() // 2))

        # Urgent badge for medical mail
        if mail_type in ['urgent', 'medical']:
            badge_text = self.fonts['tiny'].render('URGENT', True, HealthcareUIColors.TEXT_LIGHT)
            badge_rect = pygame.Rect(rect.right - 60, rect.y + 5, 55, 18)
            pygame.draw.rect(screen, HealthcareUIColors.MAIL_URGENT, badge_rect,
                            border_radius=HealthcareUIMetrics.RADIUS_SMALL)
            badge_text_rect = badge_text.get_rect(center=badge_rect.center)
            screen.blit(badge_text, badge_text_rect)

    def draw_drop_zone(self, screen: pygame.Surface, rect: pygame.Rect,
                      label: str, count: int = 0, capacity: int = 5,
                      is_highlighted: bool = False) -> None:
        """Draw a drop zone for sorting items"""
        fill_ratio = count / max(capacity, 1)

        # Background with fill indication
        bg_color = HealthcareVisualHelpers.interpolate_color(
            HealthcareUIColors.FORM_FIELD_BG,
            HealthcareVisualHelpers.lighten_color(HealthcareUIColors.HEALTHCARE_SECONDARY),
            fill_ratio * 0.3
        )

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Highlight glow when valid drop target
        if is_highlighted:
            glow_rect = rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*HealthcareUIColors.HEALTHCARE_PRIMARY, 80),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=HealthcareUIMetrics.RADIUS_LARGE + 4)
            screen.blit(glow_surface, glow_rect.topleft)
            pygame.draw.rect(screen, bg_color, rect,
                            border_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Border
        border_color = HealthcareUIColors.HEALTHCARE_PRIMARY if is_highlighted else HealthcareUIColors.PANEL_BORDER
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Header
        header_rect = pygame.Rect(rect.x, rect.y, rect.width, 35)
        pygame.draw.rect(screen, HealthcareUIColors.BUTTON_DEFAULT, header_rect,
                        border_top_left_radius=HealthcareUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Label
        label_text = self.fonts['small'].render(label, True, HealthcareUIColors.TEXT_LIGHT)
        label_rect = label_text.get_rect(center=(rect.centerx, rect.y + 17))
        screen.blit(label_text, label_rect)

        # Count indicator
        count_text = self.fonts['tiny'].render(f"{count}", True, HealthcareUIColors.TEXT_MUTED)
        screen.blit(count_text, (rect.right - 25, rect.y + 10))

    def draw_medication_card(self, screen: pygame.Surface, rect: pygame.Rect,
                            name: str, price: float, is_generic: bool = False,
                            is_affordable: bool = True, is_selected: bool = False,
                            is_hover: bool = False) -> None:
        """Draw a medication card with pricing info"""
        # Shadow
        shadow_offset = 6 if is_selected else 4
        HealthcareVisualHelpers.draw_shadow(screen, rect, shadow_offset, 50,
                                           HealthcareUIMetrics.RADIUS_MEDIUM)

        # Card background
        bg_color = HealthcareUIColors.PAPER_BG
        if is_selected:
            bg_color = (230, 245, 255)
        elif is_hover:
            bg_color = (248, 250, 255)

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=HealthcareUIMetrics.RADIUS_MEDIUM)

        # Border
        if is_selected:
            border_color = HealthcareUIColors.HEALTHCARE_PRIMARY
            border_width = 3
        else:
            border_color = HealthcareUIColors.FORM_FIELD_BORDER
            border_width = 1

        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=HealthcareUIMetrics.RADIUS_MEDIUM)

        # Generic badge
        if is_generic:
            badge_rect = pygame.Rect(rect.x + 10, rect.y + 10, 60, 22)
            pygame.draw.rect(screen, HealthcareUIColors.GENERIC, badge_rect,
                            border_radius=HealthcareUIMetrics.RADIUS_SMALL)
            badge_text = self.fonts['tiny'].render('GENERIC', True, HealthcareUIColors.TEXT_LIGHT)
            badge_text_rect = badge_text.get_rect(center=badge_rect.center)
            screen.blit(badge_text, badge_text_rect)

        # Medication name
        name_y = rect.y + 40 if is_generic else rect.y + 20
        name_text = self.fonts['body'].render(name, True, HealthcareUIColors.TEXT_PRIMARY)
        screen.blit(name_text, (rect.x + 15, name_y))

        # Price
        price_color = HealthcareUIColors.AFFORDABLE if is_affordable else HealthcareUIColors.EXPENSIVE
        price_text = self.fonts['heading'].render(f"${price:.0f}", True, price_color)
        screen.blit(price_text, (rect.x + 15, rect.bottom - 40))

        # Affordability label
        afford_label = "Affordable" if is_affordable else "Too Expensive"
        afford_text = self.fonts['tiny'].render(afford_label, True, price_color)
        screen.blit(afford_text, (rect.x + 15, rect.bottom - 20))

        # Selected checkmark
        if is_selected:
            self.draw_checkmark(screen, (rect.right - 25, rect.y + 25), size=15)

    def draw_breathing_circle(self, screen: pygame.Surface, center: Tuple[int, int],
                             base_radius: int, progress: float, phase: str,
                             anxiety_level: float = 0.5) -> None:
        """Draw the breathing exercise circle with phase indication"""
        # Phase colors
        phase_colors = {
            'inhale': HealthcareUIColors.BREATHING_INHALE,
            'hold': HealthcareUIColors.BREATHING_HOLD,
            'exhale': HealthcareUIColors.BREATHING_EXHALE,
        }
        color = phase_colors.get(phase, HealthcareUIColors.BREATHING_INHALE)

        # Calculate current radius based on progress and phase
        if phase == 'inhale':
            current_radius = int(base_radius * (0.6 + 0.4 * progress))
        elif phase == 'exhale':
            current_radius = int(base_radius * (1.0 - 0.4 * progress))
        else:  # hold
            current_radius = base_radius

        # Outer guide circle
        pygame.draw.circle(screen, (200, 210, 220), center, base_radius, 2)

        # Main breathing circle with gradient
        for r in range(current_radius, 0, -2):
            alpha = int(150 * (r / current_radius))
            circle_color = (*color, alpha)
            circle_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, circle_color, (r, r), r)
            screen.blit(circle_surface, (center[0] - r, center[1] - r))

        # Phase text
        phase_text = phase.upper()
        text_surface = self.fonts['subheading'].render(phase_text, True, HealthcareUIColors.TEXT_LIGHT)
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)

    def draw_anxiety_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                          anxiety_level: float, label: str = "Anxiety") -> None:
        """Draw an anxiety/stress meter"""
        # Background
        pygame.draw.rect(screen, (40, 45, 55), rect,
                        border_radius=HealthcareUIMetrics.RADIUS_MEDIUM)

        # Label
        label_text = self.fonts['small'].render(label, True, HealthcareUIColors.TEXT_LIGHT)
        screen.blit(label_text, (rect.x + 10, rect.y + 5))

        # Meter bar
        bar_rect = pygame.Rect(rect.x + 10, rect.y + 28, rect.width - 20, 20)
        pygame.draw.rect(screen, (30, 35, 45), bar_rect,
                        border_radius=HealthcareUIMetrics.RADIUS_SMALL)

        # Fill with gradient from green to red
        fill_width = int(bar_rect.width * anxiety_level)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
            fill_color = HealthcareVisualHelpers.interpolate_color(
                HealthcareUIColors.CALM,
                HealthcareUIColors.STRESSED,
                anxiety_level
            )
            pygame.draw.rect(screen, fill_color, fill_rect,
                            border_radius=HealthcareUIMetrics.RADIUS_SMALL)

        # Percentage text
        percent_text = self.fonts['tiny'].render(f"{int(anxiety_level * 100)}%", True,
                                                 HealthcareUIColors.TEXT_LIGHT)
        screen.blit(percent_text, (rect.right - 35, rect.y + 30))

    def draw_button(self, screen: pygame.Surface, rect: pygame.Rect,
                   text: str, is_hovered: bool = False, is_primary: bool = True,
                   is_disabled: bool = False, scale: float = 1.0) -> None:
        """Draw a professional button with optional scale animation"""
        # Apply scale
        if scale != 1.0:
            center = rect.center
            new_width = int(rect.width * scale)
            new_height = int(rect.height * scale)
            rect = pygame.Rect(0, 0, new_width, new_height)
            rect.center = center

        # Colors
        if is_disabled:
            bg_color = HealthcareUIColors.BUTTON_DEFAULT
            text_color = HealthcareUIColors.TEXT_MUTED
        elif is_primary:
            bg_color = HealthcareUIColors.HEALTHCARE_PRIMARY if not is_hovered else \
                      HealthcareVisualHelpers.lighten_color(HealthcareUIColors.HEALTHCARE_PRIMARY)
            text_color = HealthcareUIColors.TEXT_LIGHT
        else:
            bg_color = HealthcareUIColors.BUTTON_DEFAULT if not is_hovered else \
                      HealthcareUIColors.BUTTON_HOVER
            text_color = HealthcareUIColors.TEXT_LIGHT

        # Shadow
        HealthcareVisualHelpers.draw_shadow(screen, rect, 3, 30,
                                           rect.height // 2)

        # Button background
        pygame.draw.rect(screen, bg_color, rect, border_radius=rect.height // 2)

        # Text
        btn_text = self.fonts['body'].render(text, True, text_color)
        text_rect = btn_text.get_rect(center=rect.center)
        screen.blit(btn_text, text_rect)

    def draw_progress_bar(self, screen: pygame.Surface, rect: pygame.Rect,
                         progress: float, label: str = None,
                         color: Tuple[int, int, int] = None) -> None:
        """Draw an animated progress bar"""
        if color is None:
            color = HealthcareUIColors.HEALTHCARE_PRIMARY

        # Background
        pygame.draw.rect(screen, (220, 225, 230), rect,
                        border_radius=rect.height // 2)

        # Fill
        fill_width = int(rect.width * max(0, min(1, progress)))
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(screen, color, fill_rect,
                            border_radius=rect.height // 2)

        # Label
        if label:
            label_text = self.fonts['small'].render(label, True, HealthcareUIColors.TEXT_PRIMARY)
            label_rect = label_text.get_rect(center=rect.center)
            screen.blit(label_text, label_rect)

    def draw_modal_overlay(self, screen: pygame.Surface, alpha: int = 180) -> None:
        """Draw a dark modal overlay"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

    def draw_modal_container(self, screen: pygame.Surface, rect: pygame.Rect,
                            header_color: Optional[Tuple[int, int, int]] = None,
                            header_text: str = "") -> None:
        """Draw a modal container with optional colored header"""
        # Shadow
        HealthcareVisualHelpers.draw_shadow(screen, rect, 8, 100,
                                           HealthcareUIMetrics.RADIUS_LARGE)

        # Main background
        pygame.draw.rect(screen, HealthcareUIColors.PAPER_BG, rect,
                        border_radius=HealthcareUIMetrics.RADIUS_LARGE)

        # Header strip if provided
        if header_color:
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 50)
            pygame.draw.rect(screen, header_color, header_rect,
                            border_top_left_radius=HealthcareUIMetrics.RADIUS_LARGE,
                            border_top_right_radius=HealthcareUIMetrics.RADIUS_LARGE)

            if header_text:
                header_surface = self.fonts['subheading'].render(header_text, True,
                                                                HealthcareUIColors.TEXT_LIGHT)
                header_text_rect = header_surface.get_rect(center=(rect.centerx, rect.y + 25))
                screen.blit(header_surface, header_text_rect)

        # Border
        pygame.draw.rect(screen, HealthcareUIColors.PANEL_BORDER, rect, 2,
                        border_radius=HealthcareUIMetrics.RADIUS_LARGE)

    def draw_checkmark(self, screen: pygame.Surface, center: Tuple[int, int],
                      size: int = 20, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a checkmark icon"""
        if color is None:
            color = HealthcareUIColors.SUCCESS

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
                   size: int = 20, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw an X mark icon"""
        if color is None:
            color = HealthcareUIColors.ERROR

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

    def draw_stamp_effect(self, screen: pygame.Surface, center: Tuple[int, int],
                         text: str, color: Tuple[int, int, int], rotation: float = -15) -> None:
        """Draw a stamp effect (like APPROVED or DENIED)"""
        # Create stamp surface
        stamp_font = pygame.font.Font(None, 48)
        stamp_text = stamp_font.render(text, True, color)

        # Rotate
        rotated = pygame.transform.rotate(stamp_text, rotation)

        # Add border effect
        border_rect = rotated.get_rect(center=center)
        border_rect = border_rect.inflate(20, 10)

        # Draw border
        pygame.draw.rect(screen, color, border_rect, 3, border_radius=4)

        # Draw text
        text_rect = rotated.get_rect(center=center)
        screen.blit(rotated, text_rect)


# Global instance for easy access
healthcare_visuals = HealthcareVisualComponents()

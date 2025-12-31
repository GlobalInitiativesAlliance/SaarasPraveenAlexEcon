"""
Education Visual Base Module
Shared visual components for Scenario 4 (Education Access) mini-games
Provides consistent styling, colors, and reusable UI components
"""

import pygame
import math
import time
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass


class EducationUIColors:
    """Education-themed color palette"""

    # Primary Education Theme
    EDUCATION_PRIMARY = (56, 123, 203)      # Academic blue
    EDUCATION_SECONDARY = (72, 156, 118)    # Knowledge green
    EDUCATION_ACCENT = (246, 173, 85)       # Achievement gold
    EDUCATION_PURPLE = (147, 51, 234)       # Special status purple

    # Document/Form Colors
    PAPER_BG = (252, 251, 248)              # Natural paper color
    PAPER_SHADOW = (230, 225, 218)          # Subtle paper shadow
    PAPER_LINES = (235, 230, 225)           # Ruled paper lines
    FORM_FIELD_BG = (248, 250, 252)         # Input field background
    FORM_FIELD_BORDER = (203, 213, 225)     # Input field border
    FORM_FIELD_FOCUS = (56, 123, 203)       # Focused field highlight

    # Status Indicators
    VERIFIED = (72, 187, 120)               # Document verified - green
    PENDING = (246, 173, 85)                # Awaiting action - gold
    BLOCKED = (237, 94, 104)                # Blocked/Error - red
    BYPASSED = (147, 51, 234)               # Special status (foster youth) - purple

    # UI Elements
    PANEL_BG = (28, 32, 40)                 # Dark panel background
    PANEL_BORDER = (52, 58, 70)             # Panel border
    BUTTON_DEFAULT = (55, 65, 81)           # Button normal
    BUTTON_HOVER = (71, 85, 105)            # Button hover
    BUTTON_ACTIVE = (96, 165, 250)          # Button active/pressed

    # Text Colors
    TEXT_PRIMARY = (30, 30, 40)             # Dark text on light bg
    TEXT_SECONDARY = (80, 85, 100)          # Secondary text
    TEXT_MUTED = (140, 145, 160)            # Muted/hint text
    TEXT_LIGHT = (255, 255, 255)            # Light text on dark bg

    # Timer Colors
    TIMER_SAFE = (72, 187, 120)             # Green - plenty of time
    TIMER_WARNING = (246, 173, 85)          # Orange - getting low
    TIMER_DANGER = (237, 94, 104)           # Red - almost out


class EducationUIMetrics:
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


class EducationVisualHelpers:
    """Helper functions for drawing common visual elements"""

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                   offset: int = 4, alpha: int = 60,
                   border_radius: int = 8) -> None:
        """Draw a soft shadow behind an element"""
        shadow_surface = pygame.Surface((rect.width + offset * 2,
                                        rect.height + offset * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_rect,
                        border_radius=border_radius)
        screen.blit(shadow_surface, (rect.x - offset // 2, rect.y - offset // 2))

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
    def draw_dashed_rect(screen: pygame.Surface, rect: pygame.Rect,
                        color: Tuple[int, int, int], width: int = 2,
                        dash_length: int = 8) -> None:
        """Draw a rectangle with dashed border"""
        x, y, w, h = rect.x, rect.y, rect.width, rect.height

        # Top edge
        for i in range(0, w, dash_length * 2):
            end_x = min(i + dash_length, w)
            pygame.draw.line(screen, color, (x + i, y), (x + end_x, y), width)

        # Bottom edge
        for i in range(0, w, dash_length * 2):
            end_x = min(i + dash_length, w)
            pygame.draw.line(screen, color, (x + i, y + h), (x + end_x, y + h), width)

        # Left edge
        for i in range(0, h, dash_length * 2):
            end_y = min(i + dash_length, h)
            pygame.draw.line(screen, color, (x, y + i), (x, y + end_y), width)

        # Right edge
        for i in range(0, h, dash_length * 2):
            end_y = min(i + dash_length, h)
            pygame.draw.line(screen, color, (x + w, y + i), (x + w, y + end_y), width)

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


class EducationVisualComponents:
    """Reusable visual components for education mini-games"""

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
                             with_lines: bool = True, shadow: bool = True) -> None:
        """Draw a paper-like background with optional ruled lines"""
        if shadow:
            EducationVisualHelpers.draw_shadow(screen, rect, offset=6, alpha=40,
                                               border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Main paper surface
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Paper texture - subtle gradient from top
        for y in range(min(50, rect.height)):
            alpha = int(15 * (1 - y / 50))
            pygame.draw.line(screen, (255, 255, 255, alpha),
                           (rect.x + EducationUIMetrics.RADIUS_LARGE, rect.y + y),
                           (rect.right - EducationUIMetrics.RADIUS_LARGE, rect.y + y))

        # Ruled lines
        if with_lines:
            line_start_y = rect.y + 60
            line_spacing = 28
            for y in range(line_start_y, rect.bottom - 30, line_spacing):
                pygame.draw.line(screen, EducationUIColors.PAPER_LINES,
                               (rect.x + 25, y), (rect.right - 25, y), 1)

        # Border
        pygame.draw.rect(screen, EducationUIColors.PAPER_SHADOW, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def draw_form_field(self, screen: pygame.Surface, rect: pygame.Rect,
                       label: str, value: str, state: str = 'normal',
                       show_cursor: bool = False) -> None:
        """
        Draw a professional form input field
        States: 'normal', 'filled', 'focus', 'blocked', 'bypassed'
        """
        # Determine colors based on state
        if state == 'filled':
            bg_color = (230, 255, 230)
            border_color = EducationUIColors.VERIFIED
        elif state == 'focus':
            bg_color = EducationUIColors.FORM_FIELD_BG
            border_color = EducationUIColors.FORM_FIELD_FOCUS
        elif state == 'blocked':
            bg_color = (255, 230, 230)
            border_color = EducationUIColors.BLOCKED
        elif state == 'bypassed':
            bg_color = (240, 230, 255)
            border_color = EducationUIColors.BYPASSED
        else:
            bg_color = EducationUIColors.FORM_FIELD_BG
            border_color = EducationUIColors.FORM_FIELD_BORDER

        # Draw field background
        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)

        # Draw label above field
        label_text = self.fonts['small'].render(label, True, EducationUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (rect.x, rect.y - 20))

        # Draw value
        if value:
            value_color = EducationUIColors.TEXT_PRIMARY if state != 'blocked' else EducationUIColors.TEXT_MUTED
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
            color = EducationUIColors.TIMER_SAFE
        elif progress > 0.2:
            color = EducationUIColors.TIMER_WARNING
        else:
            color = EducationUIColors.TIMER_DANGER
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
        pygame.draw.circle(screen, EducationUIColors.PAPER_BG, center, radius - 8)

        # Timer text
        if show_text:
            time_text = f"{int(time_remaining)}"
            text_surface = self.fonts['heading'].render(time_text, True, color)
            text_rect = text_surface.get_rect(center=center)
            screen.blit(text_surface, text_rect)

    def draw_document_card(self, screen: pygame.Surface, rect: pygame.Rect,
                          title: str, doc_type: str, is_dragging: bool = False,
                          is_hover: bool = False) -> None:
        """Draw a professional document card with icon"""
        # Get document-specific color
        type_colors = {
            'id': EducationUIColors.EDUCATION_PRIMARY,
            'foster': EducationUIColors.EDUCATION_PURPLE,
            'address': EducationUIColors.EDUCATION_SECONDARY,
            'income': EducationUIColors.EDUCATION_ACCENT
        }
        type_color = type_colors.get(doc_type, EducationUIColors.EDUCATION_PRIMARY)

        # Shadow (larger when dragging)
        shadow_offset = 8 if is_dragging else 4
        shadow_alpha = 80 if is_dragging else 40
        EducationVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Card background
        bg_color = EducationUIColors.PAPER_BG
        if is_dragging:
            bg_color = (240, 245, 255)
        elif is_hover:
            bg_color = (250, 252, 255)

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Border
        border_color = type_color if is_dragging else EducationUIColors.FORM_FIELD_BORDER
        border_width = 2 if is_dragging else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Icon area
        icon_size = 36
        icon_rect = pygame.Rect(rect.x + 10, rect.centery - icon_size // 2,
                               icon_size, icon_size)
        pygame.draw.rect(screen, type_color, icon_rect,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)

        # Icon symbol (simple text for now)
        icon_symbols = {
            'id': 'ID',
            'foster': 'FC',
            'address': 'AD',
            'income': '$'
        }
        symbol = icon_symbols.get(doc_type, '?')
        symbol_text = self.fonts['small'].render(symbol, True, (255, 255, 255))
        symbol_rect = symbol_text.get_rect(center=icon_rect.center)
        screen.blit(symbol_text, symbol_rect)

        # Title
        title_text = self.fonts['body'].render(title, True, EducationUIColors.TEXT_PRIMARY)
        screen.blit(title_text, (rect.x + icon_size + 20,
                                rect.centery - title_text.get_height() // 2))

    def draw_category_zone(self, screen: pygame.Surface, rect: pygame.Rect,
                          label: str, items: List[str], capacity: int = 3,
                          is_highlighted: bool = False) -> None:
        """Draw a drop zone for categorizing items"""
        fill_ratio = len(items) / max(capacity, 1)

        # Background with fill indication
        bg_color = EducationVisualHelpers.interpolate_color(
            EducationUIColors.FORM_FIELD_BG,
            EducationVisualHelpers.lighten_color(EducationUIColors.EDUCATION_SECONDARY),
            fill_ratio * 0.3
        )

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Highlight glow when valid drop target
        if is_highlighted:
            glow_rect = rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*EducationUIColors.EDUCATION_PRIMARY, 80),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=EducationUIMetrics.RADIUS_LARGE + 4)
            screen.blit(glow_surface, glow_rect.topleft)
            pygame.draw.rect(screen, bg_color, rect,
                            border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Border
        border_color = EducationUIColors.EDUCATION_PRIMARY if is_highlighted else EducationUIColors.PANEL_BORDER
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Header
        header_rect = pygame.Rect(rect.x, rect.y, rect.width, 35)
        pygame.draw.rect(screen, EducationUIColors.BUTTON_DEFAULT, header_rect,
                        border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

        # Label
        label_text = self.fonts['small'].render(label, True, EducationUIColors.TEXT_LIGHT)
        label_rect = label_text.get_rect(center=(rect.centerx, rect.y + 17))
        screen.blit(label_text, label_rect)

        # Capacity indicator
        capacity_text = self.fonts['tiny'].render(f"{len(items)}/{capacity}", True,
                                                  EducationUIColors.TEXT_MUTED)
        screen.blit(capacity_text, (rect.right - 35, rect.y + 10))

        # Items list
        y_offset = 45
        for item in items[:capacity]:
            item_text = self.fonts['small'].render(item, True, EducationUIColors.VERIFIED)
            screen.blit(item_text, (rect.x + 15, rect.y + y_offset))
            y_offset += 22

    def draw_calendar_slot(self, screen: pygame.Surface, rect: pygame.Rect,
                          hour: int, is_occupied: bool = False,
                          block_color: Optional[Tuple[int, int, int]] = None,
                          is_highlighted: bool = False) -> None:
        """Draw a calendar time slot"""
        # Background
        if is_occupied and block_color:
            bg_color = block_color
        elif is_highlighted:
            bg_color = (*EducationUIColors.EDUCATION_PRIMARY, 40)
        else:
            bg_color = (252, 252, 254) if hour % 2 == 0 else (248, 250, 252)

        pygame.draw.rect(screen, bg_color, rect)
        pygame.draw.rect(screen, (200, 210, 220), rect, 1)

        # Hour label (if at start of slot)
        if not is_occupied:
            time_str = f"{hour}:00" if hour <= 12 else f"{hour-12}:00"
            if hour == 12:
                time_str = "12:00"
            time_text = self.fonts['tiny'].render(time_str, True, EducationUIColors.TEXT_MUTED)
            screen.blit(time_text, (rect.x + 3, rect.y + 3))

    def draw_button(self, screen: pygame.Surface, rect: pygame.Rect,
                   text: str, is_hovered: bool = False, is_primary: bool = True,
                   icon: Optional[str] = None) -> None:
        """Draw a professional button"""
        # Colors
        if is_primary:
            bg_color = EducationUIColors.EDUCATION_PRIMARY if not is_hovered else \
                      EducationVisualHelpers.lighten_color(EducationUIColors.EDUCATION_PRIMARY)
            text_color = EducationUIColors.TEXT_LIGHT
        else:
            bg_color = EducationUIColors.BUTTON_DEFAULT if not is_hovered else \
                      EducationUIColors.BUTTON_HOVER
            text_color = EducationUIColors.TEXT_LIGHT

        # Scale on hover
        if is_hovered:
            rect = rect.inflate(4, 4)

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, rect, 3, 30,
                                          rect.height // 2)

        # Button background
        pygame.draw.rect(screen, bg_color, rect, border_radius=rect.height // 2)

        # Text
        btn_text = self.fonts['body'].render(text, True, text_color)
        text_rect = btn_text.get_rect(center=rect.center)

        if icon:
            text_rect.x -= 10
            icon_text = self.fonts['body'].render(icon, True, text_color)
            screen.blit(icon_text, (text_rect.right + 5, text_rect.y))

        screen.blit(btn_text, text_rect)

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
        EducationVisualHelpers.draw_shadow(screen, rect, 8, 100,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Main background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Header strip if provided
        if header_color:
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 50)
            pygame.draw.rect(screen, header_color, header_rect,
                            border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                            border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

            if header_text:
                header_surface = self.fonts['subheading'].render(header_text, True,
                                                                EducationUIColors.TEXT_LIGHT)
                header_text_rect = header_surface.get_rect(center=(rect.centerx, rect.y + 25))
                screen.blit(header_surface, header_text_rect)

        # Border
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def draw_checkmark(self, screen: pygame.Surface, center: Tuple[int, int],
                      size: int = 20, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw an animated checkmark icon"""
        if color is None:
            color = EducationUIColors.VERIFIED

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
            color = EducationUIColors.BLOCKED

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


# Global instance for easy access
education_visuals = EducationVisualComponents()

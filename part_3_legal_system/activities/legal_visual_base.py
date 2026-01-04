"""
Legal System Visual Base Module
Shared visual components for Part 3 (Legal System Entanglements) mini-games
Provides consistent styling, colors, and reusable UI components with a legal/courthouse theme
"""

import pygame
import math
import time
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass


class LegalUIColors:
    """Legal system themed color palette"""

    # Primary Theme - Courthouse Authority
    LEGAL_PRIMARY = (70, 90, 120)       # Steel blue (bureaucratic)
    LEGAL_SECONDARY = (139, 90, 43)     # Gavel brown (wood tones)
    LEGAL_ACCENT = (198, 40, 40)        # Warning red (urgency/debt)
    LEGAL_NEUTRAL = (180, 180, 175)     # Courthouse gray (documents)
    LEGAL_GOLD = (212, 175, 55)         # Justice gold (positive outcomes)

    # Document/Mail Colors
    PAPER_BG = (252, 251, 248)          # Natural paper color
    PAPER_SHADOW = (230, 225, 218)      # Subtle paper shadow
    PAPER_LINES = (235, 230, 225)       # Ruled paper lines
    ENVELOPE_JUNK = (255, 230, 100)     # Yellow junk mail
    ENVELOPE_IMPORTANT = (255, 255, 255) # White important mail
    ENVELOPE_LEGAL = (200, 200, 255)    # Blue-tint legal docs
    COURT_SUMMONS = (255, 200, 200)     # Alarming pink/red tint

    # Form Field Colors
    FORM_FIELD_BG = (248, 250, 252)     # Input field background
    FORM_FIELD_BORDER = (203, 213, 225) # Input field border
    FORM_FIELD_FOCUS = (70, 90, 120)    # Focused field highlight (legal primary)

    # Status Indicators
    SUCCESS = (72, 187, 120)            # Green - correct/verified
    ERROR = (237, 94, 104)              # Red - wrong/rejected
    WARNING = (246, 173, 85)            # Orange - caution/pending
    URGENT = (198, 40, 40)              # Deep red - critical/debt
    BLOCKED = (147, 51, 234)            # Purple - special status

    # UI Elements
    PANEL_BG = (28, 32, 40)             # Dark panel background
    PANEL_BORDER = (52, 58, 70)         # Panel border
    BUTTON_DEFAULT = (55, 65, 81)       # Button normal
    BUTTON_HOVER = (71, 85, 105)        # Button hover
    BUTTON_ACTIVE = (70, 90, 120)       # Button active/pressed (legal primary)

    # Text Colors
    TEXT_PRIMARY = (30, 30, 40)         # Dark text on light bg
    TEXT_SECONDARY = (80, 85, 100)      # Secondary text
    TEXT_MUTED = (140, 145, 160)        # Muted/hint text
    TEXT_LIGHT = (255, 255, 255)        # Light text on dark bg

    # Timer Colors
    TIMER_SAFE = (72, 187, 120)         # Green - plenty of time
    TIMER_WARNING = (246, 173, 85)      # Orange - getting low
    TIMER_DANGER = (237, 94, 104)       # Red - almost out

    # Wood/Interior Colors (for backgrounds)
    WOOD_DARK = (50, 40, 30)            # Dark wood floor
    WOOD_MEDIUM = (80, 60, 40)          # Medium wood
    WOOD_LIGHT = (100, 80, 60)          # Light wood desk
    WOOD_LINE = (40, 30, 20)            # Wood grain lines


class LegalUIMetrics:
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


class LegalVisualHelpers:
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

    @staticmethod
    def draw_glow(screen: pygame.Surface, center: Tuple[int, int],
                 radius: int, color: Tuple[int, int, int],
                 intensity: int = 80) -> None:
        """Draw a glowing effect around a point"""
        for r in range(radius, 0, -2):
            alpha = int(intensity * (r / radius))
            glow_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, alpha), (r, r), r)
            screen.blit(glow_surface, (center[0] - r, center[1] - r))

    @staticmethod
    def draw_vignette(screen: pygame.Surface, intensity: float = 0.3) -> None:
        """Draw a vignette effect around screen edges"""
        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw gradient from edges
        max_dist = math.sqrt((width/2)**2 + (height/2)**2)
        for x in range(0, width, 4):
            for y in range(0, height, 4):
                dist = math.sqrt((x - width/2)**2 + (y - height/2)**2)
                alpha = int(255 * intensity * (dist / max_dist) ** 2)
                alpha = min(255, alpha)
                pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))

        screen.blit(vignette, (0, 0))


class LegalVisualComponents:
    """Reusable visual components for legal system mini-games"""

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
            self.fonts['label'] = pygame.font.SysFont('SF Pro Text', 16, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 42)
            self.fonts['heading'] = pygame.font.Font(None, 32)
            self.fonts['subheading'] = pygame.font.Font(None, 26)
            self.fonts['body'] = pygame.font.Font(None, 22)
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['tiny'] = pygame.font.Font(None, 14)
            self.fonts['label'] = pygame.font.Font(None, 20)

    def draw_wood_background(self, screen: pygame.Surface) -> None:
        """Draw a wooden floor/desk background"""
        width, height = screen.get_size()

        # Base wood color with gradient
        LegalVisualHelpers.draw_gradient_rect(
            screen, pygame.Rect(0, 0, width, height),
            LegalUIColors.WOOD_MEDIUM,
            LegalUIColors.WOOD_DARK
        )

        # Wood grain lines
        for y in range(0, height, 50):
            pygame.draw.line(screen, LegalUIColors.WOOD_LINE, (0, y), (width, y), 1)
            # Slight variation
            if y % 100 == 0:
                pygame.draw.line(screen, LegalUIColors.WOOD_LINE, (0, y + 25), (width, y + 25), 1)

    def draw_envelope(self, screen: pygame.Surface, rect: pygame.Rect,
                     mail_type: str, label: str, is_dragging: bool = False,
                     is_hover: bool = False, is_court_notice: bool = False) -> None:
        """Draw a professional envelope with visual states"""
        # Get envelope color based on type
        if is_court_notice:
            base_color = LegalUIColors.COURT_SUMMONS
            stripe_color = LegalUIColors.URGENT
        elif mail_type == 'junk':
            base_color = LegalUIColors.ENVELOPE_JUNK
            stripe_color = (200, 180, 60)
        elif mail_type == 'legal':
            base_color = LegalUIColors.ENVELOPE_LEGAL
            stripe_color = LegalUIColors.LEGAL_PRIMARY
        else:  # important
            base_color = LegalUIColors.ENVELOPE_IMPORTANT
            stripe_color = LegalUIColors.LEGAL_GOLD

        # Shadow (larger when dragging)
        shadow_offset = 8 if is_dragging else 4
        shadow_alpha = 100 if is_dragging else 50
        LegalVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                       LegalUIMetrics.RADIUS_SMALL)

        # Envelope background with gradient
        if is_dragging:
            top_color = LegalVisualHelpers.lighten_color(base_color, 1.1)
        elif is_hover:
            top_color = LegalVisualHelpers.lighten_color(base_color, 1.05)
        else:
            top_color = base_color

        bottom_color = LegalVisualHelpers.darken_color(base_color, 0.95)
        LegalVisualHelpers.draw_gradient_rect(screen, rect, top_color, bottom_color,
                                              LegalUIMetrics.RADIUS_SMALL)

        # Type indicator stripe on left edge
        stripe_rect = pygame.Rect(rect.x, rect.y, 6, rect.height)
        pygame.draw.rect(screen, stripe_color, stripe_rect,
                        border_top_left_radius=LegalUIMetrics.RADIUS_SMALL,
                        border_bottom_left_radius=LegalUIMetrics.RADIUS_SMALL)

        # Border
        border_color = stripe_color if is_dragging else LegalUIColors.PAPER_SHADOW
        border_width = 2 if is_dragging else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=LegalUIMetrics.RADIUS_SMALL)

        # Label text
        label_color = LegalUIColors.TEXT_PRIMARY
        if is_court_notice:
            # Make court notice label more alarming
            label_color = LegalUIColors.URGENT

        label_text = self.fonts['label'].render(label, True, label_color)
        label_rect = label_text.get_rect(center=(rect.centerx + 3, rect.centery))
        screen.blit(label_text, label_rect)

        # URGENT stamp for court notice
        if is_court_notice:
            stamp_font = self.fonts['tiny']
            stamp_text = stamp_font.render("URGENT", True, LegalUIColors.URGENT)
            stamp_rect = stamp_text.get_rect(topright=(rect.right - 8, rect.top + 5))
            # Stamp background
            stamp_bg = stamp_rect.inflate(6, 4)
            pygame.draw.rect(screen, (255, 255, 255, 200), stamp_bg)
            pygame.draw.rect(screen, LegalUIColors.URGENT, stamp_bg, 1)
            screen.blit(stamp_text, stamp_rect)

    def draw_drop_zone(self, screen: pygame.Surface, rect: pygame.Rect,
                      label: str, zone_type: str, is_highlighted: bool = False,
                      pulse_time: float = 0) -> None:
        """Draw a drop zone for sorting items"""
        # Colors based on zone type
        if zone_type == 'trash':
            base_color = LegalUIColors.WOOD_MEDIUM
            border_color = LegalUIColors.WOOD_LINE
            highlight_color = LegalUIColors.ERROR
        else:  # important
            base_color = LegalUIColors.WOOD_LIGHT
            border_color = LegalUIColors.LEGAL_SECONDARY
            highlight_color = LegalUIColors.SUCCESS

        # Pulse animation when highlighted
        if is_highlighted:
            pulse = abs(math.sin(pulse_time * 3)) * 0.15
            inflated_rect = rect.inflate(int(rect.width * pulse), int(rect.height * pulse))

            # Glow effect
            glow_surface = pygame.Surface((inflated_rect.width + 20, inflated_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*highlight_color, 60),
                           (10, 10, inflated_rect.width, inflated_rect.height),
                           border_radius=LegalUIMetrics.RADIUS_LARGE)
            screen.blit(glow_surface, (inflated_rect.x - 10, inflated_rect.y - 10))

        # Zone background
        pygame.draw.rect(screen, base_color, rect, border_radius=LegalUIMetrics.RADIUS_MEDIUM)

        # Border (thicker when highlighted)
        border_width = 4 if is_highlighted else 2
        current_border = highlight_color if is_highlighted else border_color
        pygame.draw.rect(screen, current_border, rect, border_width,
                        border_radius=LegalUIMetrics.RADIUS_MEDIUM)

        # Label
        label_text = self.fonts['heading'].render(label, True, LegalUIColors.PAPER_BG)
        label_rect = label_text.get_rect(center=rect.center)
        screen.blit(label_text, label_rect)

    def draw_progress_bar(self, screen: pygame.Surface, rect: pygame.Rect,
                         progress: float, label: str = "",
                         color: Tuple[int, int, int] = None) -> None:
        """Draw an animated progress bar"""
        if color is None:
            color = LegalUIColors.LEGAL_GOLD

        # Background
        pygame.draw.rect(screen, LegalUIColors.PANEL_BG, rect,
                        border_radius=rect.height // 2)

        # Progress fill with gradient
        if progress > 0:
            fill_width = int(rect.width * min(1.0, progress))
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)

            lighter = LegalVisualHelpers.lighten_color(color, 1.2)
            LegalVisualHelpers.draw_gradient_rect(screen, fill_rect, lighter, color,
                                                  rect.height // 2)

        # Border
        pygame.draw.rect(screen, LegalUIColors.PANEL_BORDER, rect, 2,
                        border_radius=rect.height // 2)

        # Label
        if label:
            label_text = self.fonts['small'].render(label, True, LegalUIColors.TEXT_LIGHT)
            label_rect = label_text.get_rect(center=rect.center)
            screen.blit(label_text, label_rect)

    def draw_instruction_box(self, screen: pygame.Surface, text: str,
                            alpha: float = 1.0) -> None:
        """Draw a styled instruction box at top of screen"""
        width = screen.get_width()

        # Create instruction surface
        inst_font = self.fonts['heading']
        inst_text = inst_font.render(text, True, LegalUIColors.TEXT_LIGHT)

        padding = 24
        box_width = inst_text.get_width() + padding * 2
        box_height = inst_text.get_height() + padding
        box_x = (width - box_width) // 2
        box_y = 30

        # Background with transparency
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (*LegalUIColors.PANEL_BG, int(220 * alpha)),
                        (0, 0, box_width, box_height),
                        border_radius=LegalUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(box_surface, (*LegalUIColors.LEGAL_PRIMARY, int(255 * alpha)),
                        (0, 0, box_width, box_height), 2,
                        border_radius=LegalUIMetrics.RADIUS_MEDIUM)

        screen.blit(box_surface, (box_x, box_y))

        # Text with alpha
        inst_text.set_alpha(int(255 * alpha))
        text_rect = inst_text.get_rect(center=(width // 2, box_y + box_height // 2))
        screen.blit(inst_text, text_rect)

    def draw_counter(self, screen: pygame.Surface, x: int, y: int,
                    current: int, total: int, label: str = "",
                    color: Tuple[int, int, int] = None) -> None:
        """Draw a counter display (e.g., 3/5)"""
        if color is None:
            color = LegalUIColors.LEGAL_GOLD

        # Counter text
        counter_text = f"{current}/{total}"
        counter_surface = self.fonts['heading'].render(counter_text, True, color)

        # Label if provided
        if label:
            label_surface = self.fonts['small'].render(label, True, LegalUIColors.TEXT_MUTED)
            total_width = counter_surface.get_width() + label_surface.get_width() + 10

            screen.blit(label_surface, (x, y + 5))
            screen.blit(counter_surface, (x + label_surface.get_width() + 10, y))
        else:
            screen.blit(counter_surface, (x, y))

    def draw_debt_counter(self, screen: pygame.Surface, amount: int,
                         x: int = None, y: int = 20) -> None:
        """Draw debt amount display with warning styling"""
        if x is None:
            x = screen.get_width() - 20

        # Format amount
        text = f"${amount:,}"
        if amount > 0:
            text = f"-${amount:,}"

        # Color based on amount severity
        if amount >= 1000:
            color = LegalUIColors.URGENT
        elif amount >= 500:
            color = LegalUIColors.ERROR
        elif amount > 0:
            color = LegalUIColors.WARNING
        else:
            color = LegalUIColors.SUCCESS

        # Background pill
        text_surface = self.fonts['heading'].render(text, True, color)
        padding = 12
        pill_rect = pygame.Rect(
            x - text_surface.get_width() - padding * 2,
            y,
            text_surface.get_width() + padding * 2,
            text_surface.get_height() + padding
        )

        pygame.draw.rect(screen, (*LegalUIColors.PANEL_BG, 200), pill_rect,
                        border_radius=LegalUIMetrics.RADIUS_PILL)
        pygame.draw.rect(screen, color, pill_rect, 2,
                        border_radius=LegalUIMetrics.RADIUS_PILL)

        text_rect = text_surface.get_rect(center=pill_rect.center)
        screen.blit(text_surface, text_rect)

    def draw_checkmark(self, screen: pygame.Surface, center: Tuple[int, int],
                      size: int = 20, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a checkmark icon"""
        if color is None:
            color = LegalUIColors.SUCCESS

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
            color = LegalUIColors.ERROR

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
        LegalVisualHelpers.draw_shadow(screen, rect, 8, 100,
                                       LegalUIMetrics.RADIUS_LARGE)

        # Main background
        pygame.draw.rect(screen, LegalUIColors.PAPER_BG, rect,
                        border_radius=LegalUIMetrics.RADIUS_LARGE)

        # Header strip if provided
        if header_color:
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 50)
            pygame.draw.rect(screen, header_color, header_rect,
                            border_top_left_radius=LegalUIMetrics.RADIUS_LARGE,
                            border_top_right_radius=LegalUIMetrics.RADIUS_LARGE)

            if header_text:
                header_surface = self.fonts['subheading'].render(header_text, True,
                                                                LegalUIColors.TEXT_LIGHT)
                header_text_rect = header_surface.get_rect(center=(rect.centerx, rect.y + 25))
                screen.blit(header_surface, header_text_rect)

        # Border
        pygame.draw.rect(screen, LegalUIColors.PANEL_BORDER, rect, 2,
                        border_radius=LegalUIMetrics.RADIUS_LARGE)

    def draw_button(self, screen: pygame.Surface, rect: pygame.Rect,
                   text: str, is_hovered: bool = False, is_primary: bool = True,
                   icon: Optional[str] = None) -> None:
        """Draw a professional button"""
        # Colors
        if is_primary:
            bg_color = LegalUIColors.LEGAL_PRIMARY if not is_hovered else \
                      LegalVisualHelpers.lighten_color(LegalUIColors.LEGAL_PRIMARY)
            text_color = LegalUIColors.TEXT_LIGHT
        else:
            bg_color = LegalUIColors.BUTTON_DEFAULT if not is_hovered else \
                      LegalUIColors.BUTTON_HOVER
            text_color = LegalUIColors.TEXT_LIGHT

        # Scale on hover
        if is_hovered:
            rect = rect.inflate(4, 4)

        # Shadow
        LegalVisualHelpers.draw_shadow(screen, rect, 3, 30,
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


# Global instance for easy access
legal_visuals = LegalVisualComponents()

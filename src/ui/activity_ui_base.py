"""
Activity UI Base Module
Unified UI framework for all mini-games and activities
Provides consistent styling, dynamic sizing, and responsive layout

Extends concepts from EducationVisualBase to work across all scenarios.
"""

import pygame
import math
import time
from typing import Tuple, List, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum


class UIColors:
    """Unified color palette for all activities"""

    # Primary Theme
    PRIMARY = (56, 123, 203)          # Main action blue
    SECONDARY = (72, 156, 118)        # Success green
    ACCENT = (246, 173, 85)           # Warning/highlight gold
    PURPLE = (147, 51, 234)           # Special status

    # Backgrounds
    BG_DARK = (25, 28, 35)            # Dark mode background
    BG_LIGHT = (245, 247, 250)        # Light mode background
    PANEL_BG = (28, 32, 40)           # Panel/card dark
    CARD_BG = (252, 251, 248)         # Card light (paper)

    # Form/Input
    INPUT_BG = (248, 250, 252)
    INPUT_BORDER = (203, 213, 225)
    INPUT_FOCUS = (56, 123, 203)
    INPUT_FILLED = (230, 255, 230)

    # Status
    SUCCESS = (72, 187, 120)
    WARNING = (246, 173, 85)
    ERROR = (237, 94, 104)
    INFO = (56, 123, 203)

    # Text
    TEXT_PRIMARY = (30, 30, 40)
    TEXT_SECONDARY = (80, 85, 100)
    TEXT_MUTED = (140, 145, 160)
    TEXT_LIGHT = (255, 255, 255)
    TEXT_ON_PRIMARY = (255, 255, 255)

    # Buttons
    BTN_PRIMARY = (56, 123, 203)
    BTN_PRIMARY_HOVER = (70, 140, 220)
    BTN_SECONDARY = (55, 65, 81)
    BTN_SECONDARY_HOVER = (71, 85, 105)
    BTN_DANGER = (220, 53, 69)
    BTN_SUCCESS = (40, 167, 69)


class Align(Enum):
    """Alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class UIMetrics:
    """Dynamic metrics based on screen size"""
    screen_width: int
    screen_height: int

    # Base grid unit (scales with screen)
    @property
    def grid(self) -> int:
        """8px base grid, scales slightly with screen"""
        base = 8
        scale = min(self.screen_width / 1024, self.screen_height / 768)
        return int(base * max(0.8, min(1.2, scale)))

    # Spacing
    @property
    def padding_xs(self) -> int: return self.grid
    @property
    def padding_sm(self) -> int: return self.grid * 2
    @property
    def padding_md(self) -> int: return self.grid * 3
    @property
    def padding_lg(self) -> int: return self.grid * 4
    @property
    def padding_xl(self) -> int: return self.grid * 6

    # Content area (with margins)
    @property
    def content_margin(self) -> int:
        """Margin from screen edges"""
        return max(40, int(self.screen_width * 0.04))

    @property
    def content_width(self) -> int:
        return self.screen_width - (self.content_margin * 2)

    @property
    def content_height(self) -> int:
        return self.screen_height - (self.content_margin * 2)

    @property
    def content_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.content_margin,
            self.content_margin,
            self.content_width,
            self.content_height
        )

    # Border radius
    @property
    def radius_sm(self) -> int: return 4
    @property
    def radius_md(self) -> int: return 8
    @property
    def radius_lg(self) -> int: return 12
    @property
    def radius_xl(self) -> int: return 16
    @property
    def radius_pill(self) -> int: return 999

    # Standard component sizes
    @property
    def button_height(self) -> int: return self.grid * 5  # 40px at base
    @property
    def input_height(self) -> int: return self.grid * 5
    @property
    def header_height(self) -> int: return self.grid * 7  # 56px at base

    # Percentage-based sizing
    def pct_width(self, percent: float) -> int:
        """Get width as percentage of content area"""
        return int(self.content_width * percent / 100)

    def pct_height(self, percent: float) -> int:
        """Get height as percentage of content area"""
        return int(self.content_height * percent / 100)

    def center_x(self, width: int) -> int:
        """Get x position to center an element"""
        return (self.screen_width - width) // 2

    def center_y(self, height: int) -> int:
        """Get y position to center an element"""
        return (self.screen_height - height) // 2


class UIFonts:
    """Font manager with size scaling"""

    def __init__(self, metrics: UIMetrics):
        self.metrics = metrics
        self._cache: Dict[str, pygame.font.Font] = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts with fallback"""
        scale = min(self.metrics.screen_width / 1024, self.metrics.screen_height / 768)
        scale = max(0.8, min(1.3, scale))

        sizes = {
            'title': int(36 * scale),
            'heading': int(28 * scale),
            'subheading': int(22 * scale),
            'body': int(18 * scale),
            'small': int(14 * scale),
            'tiny': int(12 * scale),
        }

        for name, size in sizes.items():
            try:
                self._cache[name] = pygame.font.SysFont('SF Pro Display', size)
            except:
                self._cache[name] = pygame.font.Font(None, size + 4)

    def get(self, name: str) -> pygame.font.Font:
        return self._cache.get(name, self._cache['body'])

    @property
    def title(self): return self.get('title')
    @property
    def heading(self): return self.get('heading')
    @property
    def subheading(self): return self.get('subheading')
    @property
    def body(self): return self.get('body')
    @property
    def small(self): return self.get('small')
    @property
    def tiny(self): return self.get('tiny')


class UIHelpers:
    """Static drawing helpers"""

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                   offset: int = 4, alpha: int = 60, radius: int = 8):
        """Draw soft shadow behind element"""
        shadow = pygame.Surface((rect.width + offset * 2, rect.height + offset * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
        pygame.draw.rect(shadow, (0, 0, 0, alpha), shadow_rect, border_radius=radius)
        screen.blit(shadow, (rect.x - offset // 2, rect.y - offset // 2))

    @staticmethod
    def draw_rounded_rect(screen: pygame.Surface, rect: pygame.Rect,
                         color: Tuple[int, int, int], radius: int = 8,
                         border: int = 0, border_color: Tuple[int, int, int] = None):
        """Draw rounded rectangle with optional border"""
        pygame.draw.rect(screen, color, rect, border_radius=radius)
        if border > 0 and border_color:
            pygame.draw.rect(screen, border_color, rect, border, border_radius=radius)

    @staticmethod
    def interpolate_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int],
                         t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        t = max(0, min(1, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    @staticmethod
    def darken(color: Tuple[int, int, int], factor: float = 0.8) -> Tuple[int, int, int]:
        return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

    @staticmethod
    def lighten(color: Tuple[int, int, int], factor: float = 1.2) -> Tuple[int, int, int]:
        return (min(255, int(color[0] * factor)), min(255, int(color[1] * factor)),
                min(255, int(color[2] * factor)))


class ActivityUIBase:
    """
    Base UI framework for activities with dynamic sizing.

    Usage:
        class MyActivity:
            def __init__(self, screen):
                self.ui = ActivityUIBase(screen)

            def draw(self, screen):
                # Get dynamic layout
                panel = self.ui.centered_panel(80, 70)  # 80% width, 70% height
                self.ui.draw_panel(screen, panel, "My Panel")

                # Draw button at bottom of panel
                btn = self.ui.button_rect(panel, "Submit", Align.CENTER, Align.BOTTOM)
                self.ui.draw_button(screen, btn, "Submit", is_hovered)
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.update_metrics()

    def update_metrics(self):
        """Update metrics when screen size changes"""
        w, h = self.screen.get_size()
        self.metrics = UIMetrics(w, h)
        self.fonts = UIFonts(self.metrics)
        self.colors = UIColors

    # === Layout Helpers ===

    def centered_rect(self, width_pct: float, height_pct: float,
                     offset_y: int = 0) -> pygame.Rect:
        """Create a centered rectangle by percentage of screen"""
        w = self.metrics.pct_width(width_pct)
        h = self.metrics.pct_height(height_pct)
        x = self.metrics.center_x(w)
        y = self.metrics.center_y(h) + offset_y
        return pygame.Rect(x, y, w, h)

    def centered_panel(self, width_pct: float = 80, height_pct: float = 80) -> pygame.Rect:
        """Create a centered panel with standard margins"""
        return self.centered_rect(width_pct, height_pct)

    def grid_layout(self, parent: pygame.Rect, rows: int, cols: int,
                   gap: int = None) -> List[List[pygame.Rect]]:
        """Create a grid of rectangles within parent"""
        if gap is None:
            gap = self.metrics.padding_sm

        cell_w = (parent.width - gap * (cols + 1)) // cols
        cell_h = (parent.height - gap * (rows + 1)) // rows

        grid = []
        for row in range(rows):
            row_rects = []
            for col in range(cols):
                x = parent.x + gap + col * (cell_w + gap)
                y = parent.y + gap + row * (cell_h + gap)
                row_rects.append(pygame.Rect(x, y, cell_w, cell_h))
            grid.append(row_rects)
        return grid

    def stack_vertical(self, parent: pygame.Rect, heights: List[int],
                      gap: int = None, padding: int = None) -> List[pygame.Rect]:
        """Stack rectangles vertically within parent"""
        if gap is None:
            gap = self.metrics.padding_sm
        if padding is None:
            padding = self.metrics.padding_md

        rects = []
        y = parent.y + padding
        inner_width = parent.width - padding * 2

        for h in heights:
            rects.append(pygame.Rect(parent.x + padding, y, inner_width, h))
            y += h + gap
        return rects

    def button_rect(self, parent: pygame.Rect, text: str,
                   align_x: Align = Align.CENTER,
                   align_y: Align = Align.BOTTOM,
                   width: int = None, margin: int = None) -> pygame.Rect:
        """Create a button rectangle within parent"""
        if margin is None:
            margin = self.metrics.padding_md

        # Calculate button width based on text
        text_width = self.fonts.body.size(text)[0]
        btn_width = width or max(120, text_width + self.metrics.padding_lg * 2)
        btn_height = self.metrics.button_height

        # X position
        if align_x == Align.LEFT:
            x = parent.x + margin
        elif align_x == Align.RIGHT:
            x = parent.right - btn_width - margin
        else:  # CENTER
            x = parent.centerx - btn_width // 2

        # Y position
        if align_y == Align.TOP:
            y = parent.y + margin
        elif align_y == Align.BOTTOM:
            y = parent.bottom - btn_height - margin
        else:  # CENTER
            y = parent.centery - btn_height // 2

        return pygame.Rect(x, y, btn_width, btn_height)

    # === Drawing Methods ===

    def draw_background(self, screen: pygame.Surface, dark: bool = True):
        """Fill screen with theme background"""
        color = UIColors.BG_DARK if dark else UIColors.BG_LIGHT
        screen.fill(color)

    def draw_panel(self, screen: pygame.Surface, rect: pygame.Rect,
                  title: str = None, shadow: bool = True,
                  header_color: Tuple[int, int, int] = None):
        """Draw a panel/card with optional title"""
        if shadow:
            UIHelpers.draw_shadow(screen, rect, 6, 50, self.metrics.radius_lg)

        # Main panel
        pygame.draw.rect(screen, UIColors.CARD_BG, rect,
                        border_radius=self.metrics.radius_lg)
        pygame.draw.rect(screen, UIColors.INPUT_BORDER, rect, 1,
                        border_radius=self.metrics.radius_lg)

        # Header
        if title:
            header_h = self.metrics.header_height
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_h)
            color = header_color or UIColors.PRIMARY
            pygame.draw.rect(screen, color, header_rect,
                            border_top_left_radius=self.metrics.radius_lg,
                            border_top_right_radius=self.metrics.radius_lg)

            title_surf = self.fonts.heading.render(title, True, UIColors.TEXT_LIGHT)
            title_rect = title_surf.get_rect(center=(rect.centerx, rect.y + header_h // 2))
            screen.blit(title_surf, title_rect)

    def draw_button(self, screen: pygame.Surface, rect: pygame.Rect,
                   text: str, is_hovered: bool = False, is_disabled: bool = False,
                   style: str = 'primary'):
        """Draw a button"""
        # Colors based on style and state
        if is_disabled:
            bg = UIColors.TEXT_MUTED
            fg = UIColors.TEXT_LIGHT
        elif style == 'primary':
            bg = UIColors.BTN_PRIMARY_HOVER if is_hovered else UIColors.BTN_PRIMARY
            fg = UIColors.TEXT_LIGHT
        elif style == 'danger':
            bg = UIHelpers.lighten(UIColors.BTN_DANGER) if is_hovered else UIColors.BTN_DANGER
            fg = UIColors.TEXT_LIGHT
        elif style == 'success':
            bg = UIHelpers.lighten(UIColors.BTN_SUCCESS) if is_hovered else UIColors.BTN_SUCCESS
            fg = UIColors.TEXT_LIGHT
        else:  # secondary
            bg = UIColors.BTN_SECONDARY_HOVER if is_hovered else UIColors.BTN_SECONDARY
            fg = UIColors.TEXT_LIGHT

        # Hover effect
        draw_rect = rect.inflate(4, 4) if is_hovered and not is_disabled else rect

        # Shadow and background
        UIHelpers.draw_shadow(screen, draw_rect, 3, 30, draw_rect.height // 2)
        pygame.draw.rect(screen, bg, draw_rect, border_radius=draw_rect.height // 2)

        # Text
        text_surf = self.fonts.body.render(text, True, fg)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_surf, text_rect)

    def draw_input_field(self, screen: pygame.Surface, rect: pygame.Rect,
                        label: str, value: str, state: str = 'normal',
                        show_cursor: bool = False):
        """Draw a form input field. States: normal, focus, filled, error"""
        # Background colors by state
        if state == 'filled':
            bg = UIColors.INPUT_FILLED
            border = UIColors.SUCCESS
        elif state == 'focus':
            bg = UIColors.INPUT_BG
            border = UIColors.INPUT_FOCUS
        elif state == 'error':
            bg = (255, 230, 230)
            border = UIColors.ERROR
        else:
            bg = UIColors.INPUT_BG
            border = UIColors.INPUT_BORDER

        # Draw field
        pygame.draw.rect(screen, bg, rect, border_radius=self.metrics.radius_sm)
        pygame.draw.rect(screen, border, rect, 2, border_radius=self.metrics.radius_sm)

        # Label
        if label:
            label_surf = self.fonts.small.render(label, True, UIColors.TEXT_SECONDARY)
            screen.blit(label_surf, (rect.x, rect.y - 20))

        # Value
        if value or show_cursor:
            display = value + ('|' if show_cursor else '')
            value_surf = self.fonts.body.render(display, True, UIColors.TEXT_PRIMARY)
            screen.blit(value_surf, (rect.x + 12, rect.centery - value_surf.get_height() // 2))

    def draw_progress_bar(self, screen: pygame.Surface, rect: pygame.Rect,
                         progress: float, label: str = None,
                         color: Tuple[int, int, int] = None):
        """Draw a progress bar (progress 0-1)"""
        progress = max(0, min(1, progress))
        color = color or UIColors.PRIMARY

        # Background
        pygame.draw.rect(screen, UIColors.INPUT_BORDER, rect,
                        border_radius=rect.height // 2)

        # Fill
        if progress > 0:
            fill_width = int(rect.width * progress)
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(screen, color, fill_rect,
                            border_radius=rect.height // 2)

        # Label
        if label:
            label_surf = self.fonts.small.render(label, True, UIColors.TEXT_PRIMARY)
            label_rect = label_surf.get_rect(center=rect.center)
            screen.blit(label_surf, label_rect)

    def draw_text(self, screen: pygame.Surface, text: str, pos: Tuple[int, int],
                 font: str = 'body', color: Tuple[int, int, int] = None,
                 align: Align = Align.LEFT):
        """Draw text with alignment"""
        color = color or UIColors.TEXT_PRIMARY
        font_obj = self.fonts.get(font)
        text_surf = font_obj.render(text, True, color)

        x, y = pos
        if align == Align.CENTER:
            x -= text_surf.get_width() // 2
        elif align == Align.RIGHT:
            x -= text_surf.get_width()

        screen.blit(text_surf, (x, y))

    def draw_overlay(self, screen: pygame.Surface, alpha: int = 180):
        """Draw dark modal overlay"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

    def draw_timer(self, screen: pygame.Surface, center: Tuple[int, int],
                  time_remaining: float, time_total: float, radius: int = 40):
        """Draw circular timer"""
        progress = max(0, min(1, time_remaining / time_total))

        # Color based on time
        if progress > 0.5:
            color = UIColors.SUCCESS
        elif progress > 0.2:
            color = UIColors.WARNING
        else:
            color = UIColors.ERROR
            # Pulse effect
            pulse = abs(math.sin(time.time() * 4)) * 0.1
            radius = int(radius * (1 + pulse))

        # Background circle
        pygame.draw.circle(screen, UIColors.INPUT_BORDER, center, radius, 4)

        # Progress arc
        if progress > 0:
            start = -math.pi / 2
            end = start + (2 * math.pi * progress)
            points = []
            for i in range(int(50 * progress) + 1):
                angle = start + (end - start) * i / max(1, int(50 * progress))
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 4)

        # Center and text
        pygame.draw.circle(screen, UIColors.CARD_BG, center, radius - 8)
        time_text = self.fonts.heading.render(str(int(time_remaining)), True, color)
        text_rect = time_text.get_rect(center=center)
        screen.blit(time_text, text_rect)

    # === Utility Methods ===

    def is_hovered(self, rect: pygame.Rect, mouse_pos: Tuple[int, int] = None) -> bool:
        """Check if mouse is over rect"""
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        return rect.collidepoint(mouse_pos)


# Singleton-style accessor for current screen
_current_ui: Optional[ActivityUIBase] = None

def get_ui(screen: pygame.Surface = None) -> ActivityUIBase:
    """Get or create UI instance for screen"""
    global _current_ui
    if screen is not None:
        _current_ui = ActivityUIBase(screen)
    if _current_ui is None:
        raise RuntimeError("UI not initialized. Call get_ui(screen) first.")
    return _current_ui

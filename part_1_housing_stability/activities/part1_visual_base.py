"""
Part 1 Visual Base Module
Shared visual components for Scenario 1 (Foster Care Aging Out) mini-games
Provides consistent styling, colors, and reusable UI components

Theme: Warm, nostalgic, slightly melancholic - reflecting the bittersweet
nature of leaving foster care and packing memories.
"""

import pygame
import math
from typing import Tuple, Optional
from dataclasses import dataclass


class Part1UIColors:
    """Foster care/aging out themed color palette - warm and nostalgic"""

    # Primary Theme - Warm earth tones
    PRIMARY = (180, 130, 90)           # Sepia/warm brown
    SECONDARY = (120, 100, 140)        # Soft purple (memories)
    ACCENT = (220, 180, 120)           # Golden warm
    HIGHLIGHT = (255, 220, 160)        # Soft gold highlight

    # Background tones
    PANEL_BG = (35, 32, 38)            # Dark warm gray
    PANEL_BORDER = (55, 50, 58)        # Lighter border
    OVERLAY_BG = (20, 18, 25, 235)     # Near black with alpha

    # Card/Item Colors
    CARD_BG = (252, 250, 245)          # Warm paper
    CARD_SELECTED = (230, 245, 230)    # Light green tint when selected
    CARD_HOVER = (255, 252, 248)       # Slightly brighter on hover
    CARD_BORDER = (200, 190, 180)      # Soft border

    # Item type colors
    ESSENTIAL = (100, 160, 100)        # Green - must have
    CLOTHING = (100, 140, 180)         # Blue - regular clothes
    PERSONAL = (180, 130, 160)         # Purple-pink - personal items
    DOCUMENT = (180, 160, 100)         # Gold - documents

    # Status Colors
    SUCCESS = (72, 180, 120)           # Green checkmark
    WARNING = (220, 180, 80)           # Amber warning
    INACTIVE = (140, 135, 145)         # Gray inactive

    # Text Colors
    TEXT_LIGHT = (255, 255, 255)
    TEXT_DARK = (45, 40, 50)
    TEXT_MUTED = (140, 135, 145)
    TEXT_WARM = (220, 200, 180)        # Warm light text

    # Button Colors
    BUTTON_PRIMARY = (100, 160, 100)
    BUTTON_HOVER = (120, 180, 120)
    BUTTON_DISABLED = (80, 80, 85)


class Part1UIMetrics:
    """Standardized spacing and sizing for Part 1"""

    GRID_UNIT = 8

    # Spacing
    PADDING_SMALL = 8
    PADDING = 16
    PADDING_LARGE = 24
    MARGIN = 32

    # Border radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_PILL = 999

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


class Part1VisualHelpers:
    """Helper functions for drawing common visual elements"""

    @staticmethod
    def draw_shadow(screen: pygame.Surface, rect: pygame.Rect,
                   offset: int = 4, alpha: int = 50,
                   border_radius: int = 8) -> None:
        """Draw a soft shadow behind an element"""
        shadow = pygame.Surface((rect.width + offset * 2, rect.height + offset * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
        pygame.draw.rect(shadow, (0, 0, 0, alpha), shadow_rect, border_radius=border_radius)
        screen.blit(shadow, (rect.x - offset // 2, rect.y))

    @staticmethod
    def darken_color(color: Tuple[int, int, int], factor: float = 0.8) -> Tuple[int, int, int]:
        """Darken a color by a factor"""
        return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

    @staticmethod
    def lighten_color(color: Tuple[int, int, int], factor: float = 1.2) -> Tuple[int, int, int]:
        """Lighten a color by a factor"""
        return (min(255, int(color[0] * factor)), min(255, int(color[1] * factor)), min(255, int(color[2] * factor)))

    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        t = max(0, min(1, t))
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )


class Part1VisualComponents:
    """Reusable visual components for Part 1 mini-games"""

    def __init__(self):
        self.fonts = {}
        self._fonts_initialized = False

    def init_fonts(self):
        """Initialize font cache - call after pygame.init()"""
        if self._fonts_initialized:
            return
        try:
            self.fonts['title'] = pygame.font.SysFont('Helvetica', 38, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('Helvetica', 28, bold=True)
            self.fonts['subheading'] = pygame.font.SysFont('Helvetica', 22)
            self.fonts['body'] = pygame.font.SysFont('Helvetica', 18)
            self.fonts['small'] = pygame.font.SysFont('Helvetica', 14)
            self.fonts['tiny'] = pygame.font.SysFont('Helvetica', 12)
        except:
            self.fonts['title'] = pygame.font.Font(None, 44)
            self.fonts['heading'] = pygame.font.Font(None, 32)
            self.fonts['subheading'] = pygame.font.Font(None, 26)
            self.fonts['body'] = pygame.font.Font(None, 22)
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['tiny'] = pygame.font.Font(None, 14)
        self._fonts_initialized = True

    def draw_modal_overlay(self, screen: pygame.Surface, alpha: int = 235) -> None:
        """Draw a dark modal overlay with warm tint"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((25, 22, 28, alpha))
        screen.blit(overlay, (0, 0))

    def draw_title(self, screen: pygame.Surface, text: str, y: int = 40,
                  color: Tuple[int, int, int] = None) -> None:
        """Draw a title with shadow effect"""
        self.init_fonts()
        if color is None:
            color = Part1UIColors.ACCENT

        title_shadow = self.fonts['title'].render(text, True, (0, 0, 0))
        title_main = self.fonts['title'].render(text, True, color)
        x = screen.get_width() // 2 - title_main.get_width() // 2
        screen.blit(title_shadow, (x + 2, y + 2))
        screen.blit(title_main, (x, y))

    def draw_subtitle(self, screen: pygame.Surface, text: str, y: int = 90,
                     color: Tuple[int, int, int] = None) -> None:
        """Draw a subtitle"""
        self.init_fonts()
        if color is None:
            color = Part1UIColors.TEXT_WARM

        subtitle = self.fonts['subheading'].render(text, True, color)
        x = screen.get_width() // 2 - subtitle.get_width() // 2
        screen.blit(subtitle, (x, y))

    def draw_card(self, screen: pygame.Surface, rect: pygame.Rect,
                 is_hover: bool = False, is_selected: bool = False,
                 hover_anim: float = 0.0, select_anim: float = 0.0) -> pygame.Rect:
        """
        Draw a card with hover/selection effects.
        Returns the actual draw rect (may be offset for hover lift).
        """
        # Calculate lift effect
        lift = int(hover_anim * 4)
        draw_rect = rect.copy()
        draw_rect.y -= lift

        # Shadow
        shadow_alpha = 40 + int(hover_anim * 30) + int(select_anim * 20)
        Part1VisualHelpers.draw_shadow(screen, draw_rect, offset=5 + lift,
                                       alpha=shadow_alpha, border_radius=12)

        # Background color
        if is_selected:
            bg = Part1UIColors.CARD_SELECTED
        elif is_hover:
            bg = Part1UIColors.CARD_HOVER
        else:
            bg = Part1UIColors.CARD_BG

        pygame.draw.rect(screen, bg, draw_rect, border_radius=12)

        # Selection glow
        if select_anim > 0.1:
            glow_alpha = int(100 * select_anim)
            glow_rect = draw_rect.inflate(6, 6)
            glow = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*Part1UIColors.SUCCESS, glow_alpha),
                           glow.get_rect(), border_radius=14)
            screen.blit(glow, glow_rect.topleft)
            pygame.draw.rect(screen, bg, draw_rect, border_radius=12)

        # Border
        border_color = Part1UIColors.SUCCESS if is_selected else (
            Part1UIColors.PRIMARY if is_hover else Part1UIColors.CARD_BORDER
        )
        pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=12)

        return draw_rect

    def draw_button(self, screen: pygame.Surface, rect: pygame.Rect,
                   text: str, is_hover: bool = False,
                   is_enabled: bool = True) -> None:
        """Draw a button with hover effect"""
        self.init_fonts()

        if not is_enabled:
            btn_color = Part1UIColors.BUTTON_DISABLED
        elif is_hover:
            btn_color = Part1UIColors.BUTTON_HOVER
        else:
            btn_color = Part1UIColors.BUTTON_PRIMARY

        # Shadow
        Part1VisualHelpers.draw_shadow(screen, rect, offset=4, alpha=60, border_radius=25)

        # Background
        pygame.draw.rect(screen, btn_color, rect, border_radius=25)

        # Text
        btn_surf = self.fonts['body'].render(text, True, Part1UIColors.TEXT_LIGHT)
        btn_x = rect.centerx - btn_surf.get_width() // 2
        btn_y = rect.centery - btn_surf.get_height() // 2
        screen.blit(btn_surf, (btn_x, btn_y))

    def draw_progress_bar(self, screen: pygame.Surface, rect: pygame.Rect,
                         current: int, maximum: int,
                         label: str = None) -> None:
        """Draw a progress bar with label"""
        self.init_fonts()

        # Background
        pygame.draw.rect(screen, Part1UIColors.PANEL_BORDER, rect, border_radius=8)

        # Fill
        if maximum > 0:
            fill_width = int((current / maximum) * (rect.width - 4))
            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, fill_width, rect.height - 4)

            # Color based on fill level
            if current >= maximum:
                fill_color = Part1UIColors.SUCCESS
            elif current >= maximum * 0.5:
                fill_color = Part1UIColors.PRIMARY
            else:
                fill_color = Part1UIColors.WARNING

            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=6)

        # Label
        if label:
            label_text = f"{label}: {current}/{maximum}"
            label_surf = self.fonts['small'].render(label_text, True, Part1UIColors.TEXT_LIGHT)
            label_x = rect.centerx - label_surf.get_width() // 2
            label_y = rect.centery - label_surf.get_height() // 2
            screen.blit(label_surf, (label_x, label_y))

    def draw_checkmark(self, screen: pygame.Surface, center: Tuple[int, int],
                      size: int = 16, color: Tuple[int, int, int] = None) -> None:
        """Draw a checkmark icon"""
        if color is None:
            color = Part1UIColors.SUCCESS

        pygame.draw.circle(screen, color, center, size)
        check_pts = [
            (center[0] - size * 0.4, center[1]),
            (center[0] - size * 0.1, center[1] + size * 0.35),
            (center[0] + size * 0.4, center[1] - size * 0.25)
        ]
        pygame.draw.lines(screen, (255, 255, 255), False, check_pts, 3)

    def draw_item_type_indicator(self, screen: pygame.Surface,
                                 rect: pygame.Rect, item_type: str) -> None:
        """Draw a colored indicator for item type"""
        type_colors = {
            'essential': Part1UIColors.ESSENTIAL,
            'clothing': Part1UIColors.CLOTHING,
            'personal': Part1UIColors.PERSONAL,
            'document': Part1UIColors.DOCUMENT,
            'accessory': Part1UIColors.CLOTHING,
            'junk': Part1UIColors.INACTIVE
        }
        color = type_colors.get(item_type, Part1UIColors.INACTIVE)
        pygame.draw.rect(screen, color, rect, border_radius=4)

    def draw_hint(self, screen: pygame.Surface, text: str, y: int = None) -> None:
        """Draw hint text at bottom of screen"""
        self.init_fonts()
        if y is None:
            y = screen.get_height() - 35

        hint_surf = self.fonts['small'].render(text, True, Part1UIColors.TEXT_MUTED)
        x = screen.get_width() // 2 - hint_surf.get_width() // 2
        screen.blit(hint_surf, (x, y))

    def draw_backpack(self, screen: pygame.Surface, rect: pygame.Rect,
                     capacity: int, used: int) -> None:
        """Draw a stylized backpack with capacity indicator"""
        # Colors
        BACKPACK_MAIN = (45, 85, 120)
        BACKPACK_DARK = (30, 60, 90)
        BACKPACK_LIGHT = (65, 110, 150)

        # Shadow
        Part1VisualHelpers.draw_shadow(screen, rect, offset=6, alpha=50, border_radius=15)

        # Main body
        pygame.draw.rect(screen, BACKPACK_MAIN, rect, border_radius=15)

        # Top flap
        flap_rect = pygame.Rect(rect.x + 10, rect.y, rect.width - 20, 40)
        pygame.draw.rect(screen, BACKPACK_DARK, flap_rect, border_radius=10)

        # Pocket
        pocket_rect = pygame.Rect(rect.x + 20, rect.y + rect.height - 120,
                                  rect.width - 40, 80)
        pygame.draw.rect(screen, BACKPACK_LIGHT, pocket_rect, border_radius=8)
        pygame.draw.rect(screen, BACKPACK_DARK, pocket_rect, 2, border_radius=8)

        # Straps
        strap_width = 15
        pygame.draw.rect(screen, BACKPACK_DARK,
                        (rect.x + 20, rect.y + 40, strap_width, rect.height - 60),
                        border_radius=4)
        pygame.draw.rect(screen, BACKPACK_DARK,
                        (rect.right - 35, rect.y + 40, strap_width, rect.height - 60),
                        border_radius=4)

        # Capacity text
        self.init_fonts()
        cap_text = f"{used}/{capacity}"
        cap_surf = self.fonts['heading'].render(cap_text, True, Part1UIColors.TEXT_LIGHT)
        cap_x = rect.centerx - cap_surf.get_width() // 2
        cap_y = rect.centery - 20
        screen.blit(cap_surf, (cap_x, cap_y))

        # "Slots" label
        slots_surf = self.fonts['small'].render("slots used", True, Part1UIColors.TEXT_WARM)
        slots_x = rect.centerx - slots_surf.get_width() // 2
        screen.blit(slots_surf, (slots_x, cap_y + 35))

    def draw_drawer(self, screen: pygame.Surface, rect: pygame.Rect,
                   is_open: bool = False, is_hover: bool = False,
                   is_searched: bool = False) -> None:
        """Draw a desk drawer"""
        # Colors
        WOOD_MAIN = (139, 90, 60) if not is_searched else (100, 120, 100)
        WOOD_DARK = Part1VisualHelpers.darken_color(WOOD_MAIN)
        WOOD_LIGHT = Part1VisualHelpers.lighten_color(WOOD_MAIN)

        # Shadow if open
        if is_open:
            Part1VisualHelpers.draw_shadow(screen, rect, offset=8, alpha=60, border_radius=6)

        # Main drawer body
        pygame.draw.rect(screen, WOOD_MAIN, rect, border_radius=6)

        # Depth effect (sides)
        pygame.draw.rect(screen, WOOD_DARK,
                        (rect.x, rect.y, 4, rect.height), border_radius=2)
        pygame.draw.rect(screen, WOOD_DARK,
                        (rect.right - 4, rect.y, 4, rect.height), border_radius=2)

        # Top highlight
        pygame.draw.rect(screen, WOOD_LIGHT,
                        (rect.x + 4, rect.y, rect.width - 8, 3), border_radius=2)

        # Handle
        handle_rect = pygame.Rect(rect.centerx - 25, rect.centery - 6, 50, 12)
        handle_color = (180, 150, 100) if is_hover else (150, 120, 80)
        pygame.draw.rect(screen, handle_color, handle_rect, border_radius=4)
        pygame.draw.rect(screen, WOOD_DARK, handle_rect, 1, border_radius=4)

        # Border
        border_color = Part1UIColors.PRIMARY if is_hover else WOOD_DARK
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=6)

        # Searched indicator
        if is_searched:
            self.draw_checkmark(screen, (rect.right - 15, rect.y + 15), size=10)


# Global instance for easy access
part1_visuals = Part1VisualComponents()

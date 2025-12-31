"""
Systemic Barriers Visual Base Module
Government/Bureaucratic themed colors, helpers, and visual components
For Part 5 (Systemic and Structural Barriers) mini-games
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass


class SystemicUIColors:
    """Government/Bureaucratic color palette"""

    # Primary institutional colors
    INSTITUTIONAL_GRAY = (85, 90, 100)
    INSTITUTIONAL_GRAY_LIGHT = (120, 125, 135)
    INSTITUTIONAL_GRAY_DARK = (55, 60, 70)

    # Government blue
    GOVERNMENT_BLUE = (45, 65, 95)
    GOVERNMENT_BLUE_LIGHT = (70, 95, 130)
    GOVERNMENT_BLUE_DARK = (30, 45, 70)

    # Document colors
    FORM_CREAM = (255, 252, 245)
    FORM_CREAM_DARK = (245, 240, 230)
    MANILA = (235, 220, 180)
    MANILA_DARK = (210, 195, 155)
    MANILA_SHADOW = (180, 165, 130)

    # Status colors
    STAMP_RED = (180, 45, 55)
    STAMP_RED_DARK = (140, 35, 45)
    APPROVAL_GREEN = (65, 140, 90)
    APPROVAL_GREEN_LIGHT = (90, 170, 115)
    WARNING_ORANGE = (215, 140, 45)
    WARNING_ORANGE_LIGHT = (235, 170, 80)
    ERROR_RED = (200, 60, 60)
    ERROR_RED_DARK = (160, 45, 45)

    # Browser/Tech colors
    BROWSER_CHROME = (240, 240, 242)
    BROWSER_BORDER = (200, 200, 205)
    URL_BAR = (255, 255, 255)
    LOADING_GREEN = (100, 180, 100)
    CRASH_RED = (180, 50, 50)

    # Phone colors
    PHONE_BODY = (45, 45, 55)
    PHONE_BODY_LIGHT = (65, 65, 75)
    LCD_GREEN = (180, 220, 180)
    LCD_GREEN_DARK = (150, 190, 150)
    KEYPAD_BUTTON = (70, 70, 80)
    KEYPAD_BUTTON_PRESSED = (50, 50, 60)

    # Text colors
    TEXT_PRIMARY = (30, 30, 40)
    TEXT_SECONDARY = (80, 80, 90)
    TEXT_MUTED = (120, 120, 130)
    TEXT_LIGHT = (240, 240, 245)
    TEXT_ERROR = (180, 50, 50)

    # Background
    BACKGROUND_LIGHT = (240, 240, 245)
    BACKGROUND_DARK = (35, 35, 45)
    OVERLAY_DARK = (0, 0, 0, 180)


class SystemicUIMetrics:
    """Consistent spacing and sizing"""

    # Spacing (8px grid)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32

    # Border radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_XLARGE = 16

    # Shadows
    SHADOW_SM = 3
    SHADOW_MD = 6
    SHADOW_LG = 10

    # Standard sizes
    BUTTON_HEIGHT = 44
    INPUT_HEIGHT = 36
    CARD_PADDING = 16
    DOCUMENT_WIDTH = 140
    DOCUMENT_HEIGHT = 80


@dataclass
class UIAnimation:
    """Simple animation state tracker"""
    current: float
    target: float
    speed: float = 0.15

    def update(self, dt: float) -> None:
        """Update animation value towards target"""
        diff = self.target - self.current
        self.current += diff * self.speed

    @property
    def value(self) -> float:
        return self.current

    @property
    def is_complete(self) -> bool:
        return abs(self.target - self.current) < 0.01


class SystemicVisualHelpers:
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
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), shadow_rect, border_radius=radius)
        screen.blit(shadow_surface, (rect.x - offset // 2, rect.y + offset // 2))

    @staticmethod
    def draw_gradient_rect(screen: pygame.Surface, rect: pygame.Rect,
                          color_top: Tuple[int, int, int],
                          color_bottom: Tuple[int, int, int],
                          radius: int = 0) -> None:
        """Draw a vertical gradient rectangle"""
        for y in range(rect.height):
            progress = y / rect.height
            r = int(color_top[0] + (color_bottom[0] - color_top[0]) * progress)
            g = int(color_top[1] + (color_bottom[1] - color_top[1]) * progress)
            b = int(color_top[2] + (color_bottom[2] - color_top[2]) * progress)
            pygame.draw.line(screen, (r, g, b),
                           (rect.x, rect.y + y),
                           (rect.x + rect.width, rect.y + y))

    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int],
                         color2: Tuple[int, int, int],
                         t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors"""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )

    @staticmethod
    def draw_paper_edge(screen: pygame.Surface, rect: pygame.Rect,
                       edge_width: int = 3) -> None:
        """Draw realistic paper edge shadow"""
        # Right edge shadow
        for i in range(edge_width):
            alpha = 40 - (i * 12)
            if alpha > 0:
                pygame.draw.line(screen, (0, 0, 0, alpha),
                               (rect.right + i, rect.top + i),
                               (rect.right + i, rect.bottom + i))
        # Bottom edge shadow
        for i in range(edge_width):
            alpha = 40 - (i * 12)
            if alpha > 0:
                pygame.draw.line(screen, (0, 0, 0, alpha),
                               (rect.left + i, rect.bottom + i),
                               (rect.right + i, rect.bottom + i))


class SystemicVisualComponents:
    """Reusable visual components for systemic barriers games"""

    def __init__(self):
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.fonts['body'] = pygame.font.SysFont('SF Pro Text', 20)
            self.fonts['small'] = pygame.font.SysFont('SF Pro Text', 16)
            self.fonts['tiny'] = pygame.font.SysFont('SF Pro Text', 14)
            self.fonts['stamp'] = pygame.font.SysFont('Impact', 48, bold=True)
            self.fonts['mono'] = pygame.font.SysFont('Monaco', 16)
        except:
            self.fonts['title'] = pygame.font.Font(None, 42)
            self.fonts['heading'] = pygame.font.Font(None, 32)
            self.fonts['body'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['tiny'] = pygame.font.Font(None, 16)
            self.fonts['stamp'] = pygame.font.Font(None, 56)
            self.fonts['mono'] = pygame.font.Font(None, 18)

    def draw_manila_folder(self, screen: pygame.Surface, rect: pygame.Rect,
                          label: str = "", is_highlighted: bool = False) -> None:
        """Draw a manila folder with tab"""
        # Shadow
        SystemicVisualHelpers.draw_shadow(screen, rect, 6, 50, SystemicUIMetrics.RADIUS_MEDIUM)

        # Folder tab
        tab_width = 80
        tab_height = 25
        tab_rect = pygame.Rect(rect.x + 20, rect.y - tab_height + 5, tab_width, tab_height)

        tab_color = SystemicUIColors.MANILA if not is_highlighted else SystemicUIColors.WARNING_ORANGE_LIGHT
        pygame.draw.rect(screen, tab_color, tab_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_SMALL,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Folder body
        folder_color = SystemicUIColors.MANILA if not is_highlighted else SystemicUIColors.WARNING_ORANGE
        pygame.draw.rect(screen, folder_color, rect, border_radius=SystemicUIMetrics.RADIUS_MEDIUM)

        # Folder inner shade
        inner_rect = pygame.Rect(rect.x + 5, rect.y + 5, rect.width - 10, rect.height - 10)
        pygame.draw.rect(screen, SystemicUIColors.MANILA_DARK, inner_rect,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Border
        border_color = SystemicUIColors.MANILA_SHADOW if not is_highlighted else SystemicUIColors.WARNING_ORANGE
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=SystemicUIMetrics.RADIUS_MEDIUM)

        # Label
        if label:
            label_text = self.fonts['heading'].render(label, True, SystemicUIColors.TEXT_PRIMARY)
            label_x = rect.centerx - label_text.get_width() // 2
            screen.blit(label_text, (label_x, rect.y + 20))

    def draw_document_card(self, screen: pygame.Surface, rect: pygame.Rect,
                          title: str, icon: str = "",
                          is_dragging: bool = False, is_hover: bool = False) -> None:
        """Draw a paper document card"""
        # Shadow (larger when dragging)
        shadow_offset = 10 if is_dragging else 4
        shadow_alpha = 80 if is_dragging else 40
        SystemicVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                         SystemicUIMetrics.RADIUS_SMALL)

        # Paper background
        if is_dragging:
            bg_color = (255, 255, 250)
        elif is_hover:
            bg_color = (252, 250, 245)
        else:
            bg_color = SystemicUIColors.FORM_CREAM

        pygame.draw.rect(screen, bg_color, rect, border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Paper lines (subtle)
        line_color = (230, 225, 215)
        for y in range(rect.y + 25, rect.bottom - 10, 12):
            pygame.draw.line(screen, line_color, (rect.x + 10, y), (rect.right - 10, y))

        # Border
        border_color = SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT if not is_dragging else SystemicUIColors.GOVERNMENT_BLUE
        pygame.draw.rect(screen, border_color, rect, 1 if not is_dragging else 2,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Icon and title
        if icon:
            try:
                icon_font = pygame.font.SysFont('Segoe UI Emoji', 20)
            except:
                icon_font = self.fonts['body']
            icon_text = icon_font.render(icon, True, SystemicUIColors.TEXT_PRIMARY)
            screen.blit(icon_text, (rect.x + 10, rect.y + 8))
            title_x = rect.x + 35
        else:
            title_x = rect.x + 10

        # Title (wrap if needed)
        title_text = self.fonts['small'].render(title, True, SystemicUIColors.TEXT_PRIMARY)
        if title_text.get_width() > rect.width - 45:
            words = title.split()
            y_offset = 10
            for word in words:
                word_text = self.fonts['small'].render(word, True, SystemicUIColors.TEXT_PRIMARY)
                screen.blit(word_text, (title_x, rect.y + y_offset))
                y_offset += 18
        else:
            screen.blit(title_text, (title_x, rect.y + 12))

    def draw_official_stamp(self, screen: pygame.Surface, center: Tuple[int, int],
                           text: str, color: Tuple[int, int, int],
                           rotation: float = -15, scale: float = 1.0) -> None:
        """Draw a rubber stamp effect"""
        # Create stamp surface
        stamp_text = self.fonts['stamp'].render(text, True, color)

        # Scale
        if scale != 1.0:
            new_width = int(stamp_text.get_width() * scale)
            new_height = int(stamp_text.get_height() * scale)
            stamp_text = pygame.transform.scale(stamp_text, (new_width, new_height))

        # Rotate
        rotated = pygame.transform.rotate(stamp_text, rotation)

        # Add border effect
        border_surface = pygame.Surface((rotated.get_width() + 8, rotated.get_height() + 8), pygame.SRCALPHA)
        border_rect = border_surface.get_rect()
        pygame.draw.rect(border_surface, (*color, 180), border_rect, 3)

        # Position and draw
        stamp_rect = rotated.get_rect(center=center)
        border_rect.center = center

        screen.blit(border_surface, border_rect)
        screen.blit(rotated, stamp_rect)

    def draw_progress_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                           progress: float, label: str = "",
                           show_percentage: bool = True) -> None:
        """Draw a government-style progress meter"""
        # Background
        pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT, rect,
                        border_radius=rect.height // 2)

        # Fill
        if progress > 0:
            fill_width = int((rect.width - 4) * min(1.0, progress))
            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, fill_width, rect.height - 4)

            # Color based on progress
            if progress < 0.7:
                fill_color = SystemicUIColors.LOADING_GREEN
            elif progress < 0.85:
                fill_color = SystemicUIColors.WARNING_ORANGE
            else:
                fill_color = SystemicUIColors.ERROR_RED

            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=(rect.height - 4) // 2)

        # Border
        pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY_DARK, rect, 2,
                        border_radius=rect.height // 2)

        # Percentage text
        if show_percentage:
            percent_text = f"{int(progress * 100)}%"
            text_surface = self.fonts['small'].render(percent_text, True, SystemicUIColors.TEXT_LIGHT)
            text_x = rect.centerx - text_surface.get_width() // 2
            text_y = rect.centery - text_surface.get_height() // 2
            screen.blit(text_surface, (text_x, text_y))

        # Label
        if label:
            label_surface = self.fonts['tiny'].render(label, True, SystemicUIColors.TEXT_SECONDARY)
            screen.blit(label_surface, (rect.x, rect.y - 20))

    def draw_browser_chrome(self, screen: pygame.Surface, rect: pygame.Rect,
                           url: str = "https://benefits.ca.gov") -> pygame.Rect:
        """Draw browser window chrome, return content area rect"""
        header_height = 50

        # Window background
        pygame.draw.rect(screen, SystemicUIColors.BROWSER_CHROME, rect,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Header bar
        header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_height)
        pygame.draw.rect(screen, SystemicUIColors.BROWSER_CHROME, header_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Window buttons
        button_y = rect.y + 18
        for i, color in enumerate([(255, 95, 87), (255, 189, 46), (39, 201, 63)]):
            pygame.draw.circle(screen, color, (rect.x + 20 + i * 22, button_y), 7)

        # URL bar
        url_rect = pygame.Rect(rect.x + 90, rect.y + 10, rect.width - 110, 30)
        pygame.draw.rect(screen, SystemicUIColors.URL_BAR, url_rect,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)
        pygame.draw.rect(screen, SystemicUIColors.BROWSER_BORDER, url_rect, 1,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # URL text
        url_text = self.fonts['tiny'].render(url, True, SystemicUIColors.TEXT_SECONDARY)
        screen.blit(url_text, (url_rect.x + 10, url_rect.centery - url_text.get_height() // 2))

        # Separator line
        pygame.draw.line(screen, SystemicUIColors.BROWSER_BORDER,
                        (rect.x, rect.y + header_height),
                        (rect.right, rect.y + header_height))

        # Content area
        content_rect = pygame.Rect(rect.x + 2, rect.y + header_height + 2,
                                   rect.width - 4, rect.height - header_height - 4)
        pygame.draw.rect(screen, (255, 255, 255), content_rect)

        return content_rect

    def draw_phone_button(self, screen: pygame.Surface, rect: pygame.Rect,
                         label: str, is_pressed: bool = False) -> None:
        """Draw a tactile phone keypad button"""
        # Button body
        if is_pressed:
            pygame.draw.rect(screen, SystemicUIColors.KEYPAD_BUTTON_PRESSED, rect,
                            border_radius=SystemicUIMetrics.RADIUS_SMALL)
        else:
            # 3D effect
            highlight = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 2)
            shadow = pygame.Rect(rect.x, rect.y + rect.height // 2, rect.width, rect.height // 2)

            pygame.draw.rect(screen, SystemicUIColors.KEYPAD_BUTTON, rect,
                            border_radius=SystemicUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, (85, 85, 95), highlight,
                            border_top_left_radius=SystemicUIMetrics.RADIUS_SMALL,
                            border_top_right_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Border
        pygame.draw.rect(screen, SystemicUIColors.PHONE_BODY_LIGHT, rect, 1,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Label
        label_text = self.fonts['heading'].render(label, True, SystemicUIColors.TEXT_LIGHT)
        label_x = rect.centerx - label_text.get_width() // 2
        label_y = rect.centery - label_text.get_height() // 2
        if is_pressed:
            label_y += 2
        screen.blit(label_text, (label_x, label_y))

    def draw_lcd_screen(self, screen: pygame.Surface, rect: pygame.Rect,
                       lines: List[str], has_scanlines: bool = True) -> None:
        """Draw an LCD phone screen with text"""
        # Background
        pygame.draw.rect(screen, SystemicUIColors.LCD_GREEN, rect)

        # Scanlines effect
        if has_scanlines:
            for y in range(rect.y, rect.bottom, 3):
                pygame.draw.line(screen, SystemicUIColors.LCD_GREEN_DARK,
                               (rect.x, y), (rect.right, y))

        # Text
        y_offset = 15
        for line in lines:
            text_surface = self.fonts['mono'].render(line, True, (40, 60, 40))
            screen.blit(text_surface, (rect.x + 15, rect.y + y_offset))
            y_offset += 22

        # Border (inset effect)
        pygame.draw.rect(screen, (100, 130, 100), rect, 2)

    def draw_error_popup(self, screen: pygame.Surface, center: Tuple[int, int],
                        title: str, message: str, width: int = 500) -> pygame.Rect:
        """Draw an error popup modal"""
        height = 200
        rect = pygame.Rect(center[0] - width // 2, center[1] - height // 2, width, height)

        # Shadow
        SystemicVisualHelpers.draw_shadow(screen, rect, 15, 100, SystemicUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, (255, 245, 245), rect, border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Red header bar
        header_rect = pygame.Rect(rect.x, rect.y, rect.width, 50)
        pygame.draw.rect(screen, SystemicUIColors.ERROR_RED, header_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Error icon
        icon_text = self.fonts['heading'].render("!", True, SystemicUIColors.TEXT_LIGHT)
        pygame.draw.circle(screen, (255, 255, 255), (rect.x + 30, header_rect.centery), 15, 2)
        screen.blit(icon_text, (rect.x + 25, header_rect.centery - icon_text.get_height() // 2))

        # Title
        title_text = self.fonts['heading'].render(title, True, SystemicUIColors.TEXT_LIGHT)
        screen.blit(title_text, (rect.x + 55, header_rect.centery - title_text.get_height() // 2))

        # Message
        message_text = self.fonts['body'].render(message, True, SystemicUIColors.ERROR_RED)
        screen.blit(message_text, (rect.centerx - message_text.get_width() // 2, rect.y + 80))

        # Border
        pygame.draw.rect(screen, SystemicUIColors.ERROR_RED, rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        return rect

    def draw_countdown_timer(self, screen: pygame.Surface, center: Tuple[int, int],
                            time_remaining: float, max_time: float,
                            radius: int = 35) -> None:
        """Draw a circular countdown timer"""
        progress = time_remaining / max_time if max_time > 0 else 0

        # Color based on time remaining
        if progress > 0.5:
            color = SystemicUIColors.APPROVAL_GREEN
        elif progress > 0.2:
            color = SystemicUIColors.WARNING_ORANGE
        else:
            color = SystemicUIColors.ERROR_RED
            # Pulsing effect when critical
            pulse = abs(math.sin(time.time() * 4)) * 0.2
            radius = int(radius * (1 + pulse))

        # Background circle
        pygame.draw.circle(screen, SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT, center, radius, 4)

        # Progress arc
        if progress > 0:
            start_angle = -math.pi / 2
            end_angle = start_angle + (2 * math.pi * progress)

            num_segments = max(1, int(50 * progress))
            points = []
            for i in range(num_segments + 1):
                angle = start_angle + (end_angle - start_angle) * i / num_segments
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))

            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 5)

        # Center
        pygame.draw.circle(screen, SystemicUIColors.FORM_CREAM, center, radius - 10)

        # Time text
        time_text = f"{int(time_remaining)}"
        text_surface = self.fonts['heading'].render(time_text, True, color)
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)

    def draw_signal_bars(self, screen: pygame.Surface, pos: Tuple[int, int],
                        signal_level: int = 4, max_bars: int = 4) -> None:
        """Draw phone signal strength bars"""
        bar_width = 6
        bar_spacing = 4
        max_height = 24

        for i in range(max_bars):
            bar_height = int((i + 1) / max_bars * max_height)
            x = pos[0] + i * (bar_width + bar_spacing)
            y = pos[1] + max_height - bar_height

            if i < signal_level:
                color = SystemicUIColors.APPROVAL_GREEN if signal_level >= 3 else SystemicUIColors.WARNING_ORANGE
            else:
                color = SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT

            pygame.draw.rect(screen, color, (x, y, bar_width, bar_height))


# Global instance for easy access
systemic_visuals = SystemicVisualComponents()

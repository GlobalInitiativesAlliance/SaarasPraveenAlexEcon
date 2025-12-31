"""
Mentorship Visual Base Module
Guidance/Planning themed colors, helpers, and visual components
For Part 8 (Lack of Guidance/Mentorship) mini-games
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass


class MentorshipUIColors:
    """Guidance/Planning themed color palette - warm and professional"""

    # Primary guidance colors - navy and slate
    GUIDANCE_PRIMARY = (45, 65, 95)
    GUIDANCE_PRIMARY_LIGHT = (65, 90, 130)
    GUIDANCE_PRIMARY_DARK = (30, 45, 70)

    # Warm accent - amber/gold for mentor/guidance elements
    GUIDANCE_ACCENT = (210, 165, 75)
    GUIDANCE_ACCENT_LIGHT = (235, 195, 110)
    GUIDANCE_ACCENT_DARK = (175, 135, 55)

    # Success/positive - soft sage green
    SUCCESS_GREEN = (95, 165, 120)
    SUCCESS_GREEN_LIGHT = (130, 195, 150)
    SUCCESS_GREEN_DARK = (70, 135, 95)

    # Warning/uncertainty
    WARNING_AMBER = (200, 150, 70)
    WARNING_AMBER_LIGHT = (230, 185, 110)

    # Error/failure
    ERROR_RED = (190, 85, 85)
    ERROR_RED_LIGHT = (220, 120, 120)
    ERROR_RED_DARK = (155, 65, 65)

    # Neutral grays
    SLATE_GRAY = (85, 95, 110)
    SLATE_GRAY_LIGHT = (120, 130, 145)
    SLATE_GRAY_DARK = (60, 70, 85)

    # Backgrounds
    BACKGROUND = (240, 242, 248)
    BACKGROUND_WARM = (248, 246, 242)
    BACKGROUND_DARK = (35, 40, 50)

    # Card/Panel colors
    CARD_BG = (255, 253, 250)
    CARD_BG_HOVER = (250, 248, 245)
    CARD_BG_ACTIVE = (245, 250, 255)
    CARD_BORDER = (200, 195, 185)

    # Panel colors
    PANEL_BG = (250, 248, 245)
    PANEL_BORDER = (180, 175, 165)

    # Text colors
    TEXT_PRIMARY = (35, 40, 50)
    TEXT_SECONDARY = (85, 90, 100)
    TEXT_MUTED = (140, 145, 155)
    TEXT_LIGHT = (250, 250, 252)
    TEXT_ERROR = (180, 70, 70)
    TEXT_SUCCESS = (65, 140, 95)

    # Option/Door theme colors
    OPTION_WORK = (200, 170, 90)      # Gold/amber
    OPTION_SCHOOL = (90, 130, 185)    # Blue
    OPTION_UNCERTAIN = (130, 125, 135) # Gray
    OPTION_ALTERNATIVE = (145, 105, 165) # Purple

    # Priority slot colors
    SLOT_EMPTY = (235, 238, 245)
    SLOT_FILLED = (230, 245, 235)
    SLOT_HIGHLIGHT = (240, 248, 255)


class MentorshipUIMetrics:
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

    # Shadows - simple, not layered
    SHADOW_SM = 2
    SHADOW_MD = 4
    SHADOW_LG = 6

    # Standard component sizes
    BUTTON_HEIGHT = 44
    BUTTON_HEIGHT_SM = 36
    CARD_PADDING = 16
    CARD_PADDING_LG = 24

    # Option card sizes
    OPTION_CARD_WIDTH = 140
    OPTION_CARD_HEIGHT = 180

    # Block/draggable sizes
    BLOCK_WIDTH = 140
    BLOCK_HEIGHT = 55

    # Slot sizes
    SLOT_WIDTH = 160
    SLOT_HEIGHT = 70

    # Animation
    TRANSITION_SPEED = 0.15
    TRANSITION_FAST = 0.1


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


class MentorshipVisualHelpers:
    """Static helper functions for drawing common elements"""

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
    def get_pulse_alpha(min_alpha: int = 180, max_alpha: int = 255, speed: float = 2.0) -> int:
        """Get a pulsing alpha value"""
        return int(min_alpha + (max_alpha - min_alpha) * (0.5 + 0.5 * math.sin(time.time() * speed)))


class MentorshipVisualComponents:
    """Reusable visual components for mentorship/guidance games"""

    def __init__(self):
        self.fonts = {}
        self._init_fonts()
        # Cache for expensive surfaces
        self._cached_background = None
        self._cached_background_size = (0, 0)

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
        except:
            self.fonts['title'] = pygame.font.Font(None, 44)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['subheading'] = pygame.font.Font(None, 28)
            self.fonts['body'] = pygame.font.Font(None, 24)
            self.fonts['body_bold'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['small_bold'] = pygame.font.Font(None, 20)
            self.fonts['tiny'] = pygame.font.Font(None, 16)

    def draw_background(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw a clean professional background"""
        # Simple solid fill - no complex effects
        screen.fill(MentorshipUIColors.BACKGROUND)

    def draw_panel(self, screen: pygame.Surface, rect: pygame.Rect,
                  title: str = "", has_shadow: bool = True) -> None:
        """Draw a professional panel/container"""
        if has_shadow:
            MentorshipVisualHelpers.draw_shadow(screen, rect,
                                               MentorshipUIMetrics.SHADOW_MD, 30,
                                               MentorshipUIMetrics.RADIUS_LARGE)

        # Panel background
        pygame.draw.rect(screen, MentorshipUIColors.PANEL_BG, rect,
                        border_radius=MentorshipUIMetrics.RADIUS_LARGE)

        # Border
        pygame.draw.rect(screen, MentorshipUIColors.PANEL_BORDER, rect, 1,
                        border_radius=MentorshipUIMetrics.RADIUS_LARGE)

        # Title if provided
        if title:
            title_surface = self.fonts['heading'].render(title, True, MentorshipUIColors.TEXT_PRIMARY)
            screen.blit(title_surface, (rect.x + MentorshipUIMetrics.CARD_PADDING,
                                        rect.y + MentorshipUIMetrics.CARD_PADDING))

    def draw_option_card(self, screen: pygame.Surface, rect: pygame.Rect,
                        label: str, color: Tuple[int, int, int],
                        description: str = "", icon: str = "",
                        is_hover: bool = False, is_selected: bool = False) -> None:
        """Draw a professional option card (replaces dream doors)"""
        # Shadow
        shadow_offset = MentorshipUIMetrics.SHADOW_LG if is_hover else MentorshipUIMetrics.SHADOW_MD
        MentorshipVisualHelpers.draw_shadow(screen, rect, shadow_offset, 40,
                                           MentorshipUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_selected:
            bg_color = MentorshipUIColors.CARD_BG_ACTIVE
        elif is_hover:
            bg_color = MentorshipUIColors.CARD_BG_HOVER
        else:
            bg_color = MentorshipUIColors.CARD_BG

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Color strip at top
        strip_rect = pygame.Rect(rect.x, rect.y, rect.width, 8)
        pygame.draw.rect(screen, color, strip_rect,
                        border_top_left_radius=MentorshipUIMetrics.RADIUS_MEDIUM,
                        border_top_right_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Border
        border_color = color if is_hover or is_selected else MentorshipUIColors.CARD_BORDER
        border_width = 2 if is_hover or is_selected else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Icon if provided
        content_y = rect.y + 20
        if icon:
            try:
                icon_font = pygame.font.SysFont('Segoe UI Emoji', 28)
            except:
                icon_font = self.fonts['heading']
            icon_surface = icon_font.render(icon, True, color)
            icon_x = rect.centerx - icon_surface.get_width() // 2
            screen.blit(icon_surface, (icon_x, content_y))
            content_y += 40

        # Label
        label_surface = self.fonts['body_bold'].render(label, True, MentorshipUIColors.TEXT_PRIMARY)
        label_x = rect.centerx - label_surface.get_width() // 2
        screen.blit(label_surface, (label_x, content_y))
        content_y += 28

        # Description if provided
        if description:
            desc_surface = self.fonts['small'].render(description, True, MentorshipUIColors.TEXT_SECONDARY)
            desc_x = rect.centerx - desc_surface.get_width() // 2
            screen.blit(desc_surface, (desc_x, content_y))

    def draw_draggable_block(self, screen: pygame.Surface, rect: pygame.Rect,
                            label: str, color: Tuple[int, int, int],
                            icon: str = "", value: str = "",
                            is_dragging: bool = False, is_hover: bool = False) -> None:
        """Draw a professional draggable block (replaces floating blocks)"""
        # Shadow (larger when dragging)
        shadow_offset = MentorshipUIMetrics.SHADOW_LG if is_dragging else MentorshipUIMetrics.SHADOW_MD
        shadow_alpha = 50 if is_dragging else 35
        MentorshipVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                           MentorshipUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_dragging:
            bg_color = MentorshipUIColors.CARD_BG_ACTIVE
        elif is_hover:
            bg_color = MentorshipUIColors.CARD_BG_HOVER
        else:
            bg_color = MentorshipUIColors.CARD_BG

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Color indicator on left side
        indicator_rect = pygame.Rect(rect.x + 4, rect.y + 4, 6, rect.height - 8)
        pygame.draw.rect(screen, color, indicator_rect, border_radius=3)

        # Border
        border_color = color if is_dragging or is_hover else MentorshipUIColors.CARD_BORDER
        border_width = 2 if is_dragging else 1
        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Icon and label
        content_x = rect.x + 20
        if icon:
            try:
                icon_font = pygame.font.SysFont('Segoe UI Emoji', 18)
            except:
                icon_font = self.fonts['body']
            icon_surface = icon_font.render(icon, True, color)
            screen.blit(icon_surface, (content_x, rect.centery - icon_surface.get_height() // 2))
            content_x += icon_surface.get_width() + 8

        label_surface = self.fonts['body_bold'].render(label, True, MentorshipUIColors.TEXT_PRIMARY)
        screen.blit(label_surface, (content_x, rect.centery - label_surface.get_height() // 2))

        # Value on right side
        if value:
            value_surface = self.fonts['small'].render(value, True, color)
            screen.blit(value_surface, (rect.right - value_surface.get_width() - 12,
                                        rect.centery - value_surface.get_height() // 2))

    def draw_drop_slot(self, screen: pygame.Surface, rect: pygame.Rect,
                      label: str, number: int = 0,
                      is_filled: bool = False, is_hover: bool = False) -> None:
        """Draw a professional drop slot (replaces glowing priority slots)"""
        # Shadow
        MentorshipVisualHelpers.draw_shadow(screen, rect,
                                           MentorshipUIMetrics.SHADOW_SM, 25,
                                           MentorshipUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_filled:
            bg_color = MentorshipUIColors.SLOT_FILLED
            border_color = MentorshipUIColors.SUCCESS_GREEN
        elif is_hover:
            bg_color = MentorshipUIColors.SLOT_HIGHLIGHT
            border_color = MentorshipUIColors.GUIDANCE_PRIMARY_LIGHT
        else:
            bg_color = MentorshipUIColors.SLOT_EMPTY
            border_color = MentorshipUIColors.CARD_BORDER

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Dashed border when empty and not hovered
        if not is_filled and not is_hover:
            # Simple dashed effect
            dash_color = MentorshipUIColors.SLATE_GRAY_LIGHT
            dash_length = 8
            gap = 6

            # Top and bottom edges
            for x in range(rect.x + 4, rect.right - 4, dash_length + gap):
                dash_width = min(dash_length, rect.right - 4 - x)
                pygame.draw.line(screen, dash_color, (x, rect.y), (x + dash_width, rect.y), 2)
                pygame.draw.line(screen, dash_color, (x, rect.bottom - 1), (x + dash_width, rect.bottom - 1), 2)

            # Left and right edges
            for y in range(rect.y + 4, rect.bottom - 4, dash_length + gap):
                dash_height = min(dash_length, rect.bottom - 4 - y)
                pygame.draw.line(screen, dash_color, (rect.x, y), (rect.x, y + dash_height), 2)
                pygame.draw.line(screen, dash_color, (rect.right - 1, y), (rect.right - 1, y + dash_height), 2)
        else:
            pygame.draw.rect(screen, border_color, rect, 2,
                            border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Number badge
        if number > 0 and not is_filled:
            badge_text = f"#{number}"
            badge_surface = self.fonts['body_bold'].render(badge_text, True, MentorshipUIColors.TEXT_MUTED)
            badge_x = rect.centerx - badge_surface.get_width() // 2
            badge_y = rect.centery - badge_surface.get_height() // 2
            screen.blit(badge_surface, (badge_x, badge_y))

        # Label above
        if label:
            label_surface = self.fonts['small'].render(label, True, MentorshipUIColors.TEXT_SECONDARY)
            screen.blit(label_surface, (rect.x, rect.y - 22))

    def draw_balance_scale(self, screen: pygame.Surface, center: Tuple[int, int],
                          beam_width: int = 280, beam_angle: float = 0.0,
                          left_weight: int = 0, right_weight: int = 0,
                          is_balanced: bool = False) -> Tuple[pygame.Rect, pygame.Rect]:
        """Draw a professional balance scale, return pan rects"""
        # Fulcrum/base
        base_width = 50
        base_height = 70

        # Draw base triangle
        base_points = [
            (center[0], center[1] - 5),
            (center[0] - base_width // 2, center[1] + base_height // 2),
            (center[0] + base_width // 2, center[1] + base_height // 2)
        ]
        pygame.draw.polygon(screen, MentorshipUIColors.SLATE_GRAY, base_points)
        pygame.draw.polygon(screen, MentorshipUIColors.SLATE_GRAY_DARK, base_points, 2)

        # Beam
        beam_height = 12
        beam_rect = pygame.Rect(center[0] - beam_width // 2, center[1] - beam_height // 2 - 10,
                               beam_width, beam_height)

        # Create rotated beam surface
        beam_surface = pygame.Surface((beam_width + 20, beam_height + 20), pygame.SRCALPHA)
        pygame.draw.rect(beam_surface, MentorshipUIColors.GUIDANCE_PRIMARY,
                        (10, 10, beam_width, beam_height),
                        border_radius=4)
        pygame.draw.rect(beam_surface, MentorshipUIColors.GUIDANCE_PRIMARY_DARK,
                        (10, 10, beam_width, beam_height), 2, border_radius=4)

        # Rotate beam
        rotated_beam = pygame.transform.rotate(beam_surface, -math.degrees(beam_angle))
        beam_pos = (center[0] - rotated_beam.get_width() // 2,
                   center[1] - rotated_beam.get_height() // 2 - 10)
        screen.blit(rotated_beam, beam_pos)

        # Calculate pan positions
        pan_width = 80
        pan_height = 40
        chain_length = 70

        cos_a, sin_a = math.cos(beam_angle), math.sin(beam_angle)

        left_x = center[0] - (beam_width // 2 - 20)
        right_x = center[0] + (beam_width // 2 - 20)

        left_pan_x = center[0] + (left_x - center[0]) * cos_a
        left_pan_y = center[1] - 10 + (left_x - center[0]) * sin_a + chain_length

        right_pan_x = center[0] + (right_x - center[0]) * cos_a
        right_pan_y = center[1] - 10 + (right_x - center[0]) * (-sin_a) + chain_length

        # Draw chains (simple lines)
        chain_color = MentorshipUIColors.SLATE_GRAY
        pygame.draw.line(screen, chain_color,
                        (left_pan_x, center[1] - 5),
                        (left_pan_x, left_pan_y - pan_height // 2), 2)
        pygame.draw.line(screen, chain_color,
                        (right_pan_x, center[1] - 5),
                        (right_pan_x, right_pan_y - pan_height // 2), 2)

        # Draw pans
        for pan_x, pan_y, weight in [(left_pan_x, left_pan_y, left_weight),
                                      (right_pan_x, right_pan_y, right_weight)]:
            pan_rect = pygame.Rect(pan_x - pan_width // 2, pan_y - pan_height // 2,
                                  pan_width, pan_height)

            # Pan color based on weight
            if weight > 0:
                pan_color = MentorshipVisualHelpers.interpolate_color(
                    MentorshipUIColors.SLOT_EMPTY,
                    MentorshipUIColors.GUIDANCE_ACCENT_LIGHT,
                    min(1.0, weight / 10)
                )
            else:
                pan_color = MentorshipUIColors.SLOT_EMPTY

            pygame.draw.ellipse(screen, pan_color, pan_rect)
            pygame.draw.ellipse(screen, MentorshipUIColors.SLATE_GRAY, pan_rect, 2)

        # Return pan rects
        left_pan_rect = pygame.Rect(left_pan_x - pan_width // 2, left_pan_y - pan_height // 2,
                                    pan_width, pan_height)
        right_pan_rect = pygame.Rect(right_pan_x - pan_width // 2, right_pan_y - pan_height // 2,
                                     pan_width, pan_height)

        return left_pan_rect, right_pan_rect

    def draw_progress_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                           progress: float, label: str = "",
                           color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a simple progress meter"""
        if color is None:
            color = MentorshipUIColors.GUIDANCE_PRIMARY

        # Background
        pygame.draw.rect(screen, MentorshipUIColors.SLATE_GRAY_LIGHT, rect,
                        border_radius=rect.height // 2)

        # Fill
        if progress > 0:
            fill_width = int((rect.width - 4) * min(1.0, progress))
            fill_rect = pygame.Rect(rect.x + 2, rect.y + 2, fill_width, rect.height - 4)
            pygame.draw.rect(screen, color, fill_rect,
                            border_radius=(rect.height - 4) // 2)

        # Border
        pygame.draw.rect(screen, MentorshipUIColors.SLATE_GRAY, rect, 1,
                        border_radius=rect.height // 2)

        # Label
        if label:
            label_surface = self.fonts['small'].render(label, True, MentorshipUIColors.TEXT_SECONDARY)
            screen.blit(label_surface, (rect.x, rect.y - 20))

    def draw_status_banner(self, screen: pygame.Surface, text: str,
                          center_x: int, y: int,
                          status: str = "info", alpha: int = 255) -> None:
        """Draw a simple status banner"""
        # Status colors
        if status == "success":
            bg_color = MentorshipUIColors.SUCCESS_GREEN
        elif status == "error":
            bg_color = MentorshipUIColors.ERROR_RED
        elif status == "warning":
            bg_color = MentorshipUIColors.WARNING_AMBER
        else:
            bg_color = MentorshipUIColors.GUIDANCE_PRIMARY

        # Render text to get width
        text_surface = self.fonts['body_bold'].render(text, True, MentorshipUIColors.TEXT_LIGHT)
        padding = MentorshipUIMetrics.SPACING_MD

        # Banner rect
        banner_width = text_surface.get_width() + padding * 2
        banner_height = text_surface.get_height() + padding
        banner_rect = pygame.Rect(center_x - banner_width // 2, y,
                                 banner_width, banner_height)

        # Draw banner with alpha
        banner_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        pygame.draw.rect(banner_surface, (*bg_color, alpha),
                        (0, 0, banner_width, banner_height),
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        screen.blit(banner_surface, banner_rect.topleft)

        # Text
        if alpha >= 200:
            screen.blit(text_surface, (banner_rect.x + padding, banner_rect.y + padding // 2))
        else:
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (banner_rect.x + padding, banner_rect.y + padding // 2))

    def draw_instruction_text(self, screen: pygame.Surface, text: str,
                             center_x: int, y: int) -> None:
        """Draw centered instruction text"""
        text_surface = self.fonts['body'].render(text, True, MentorshipUIColors.TEXT_SECONDARY)
        screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

    def draw_title(self, screen: pygame.Surface, text: str,
                  center_x: int, y: int) -> None:
        """Draw centered title text"""
        text_surface = self.fonts['title'].render(text, True, MentorshipUIColors.TEXT_PRIMARY)
        screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

    def draw_choice_button(self, screen: pygame.Surface, rect: pygame.Rect,
                          text: str, index: int,
                          is_hover: bool = False, is_selected: bool = False) -> None:
        """Draw a professional choice button"""
        # Shadow
        shadow_offset = MentorshipUIMetrics.SHADOW_MD if is_hover else MentorshipUIMetrics.SHADOW_SM
        MentorshipVisualHelpers.draw_shadow(screen, rect, shadow_offset, 30,
                                           MentorshipUIMetrics.RADIUS_MEDIUM)

        # Background
        if is_selected:
            bg_color = MentorshipUIColors.GUIDANCE_PRIMARY_LIGHT
            border_color = MentorshipUIColors.GUIDANCE_PRIMARY
        elif is_hover:
            bg_color = MentorshipUIColors.CARD_BG_HOVER
            border_color = MentorshipUIColors.GUIDANCE_PRIMARY_LIGHT
        else:
            bg_color = MentorshipUIColors.CARD_BG
            border_color = MentorshipUIColors.CARD_BORDER

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=MentorshipUIMetrics.RADIUS_MEDIUM)

        # Number circle
        num_center = (rect.x + 28, rect.centery)
        num_color = MentorshipUIColors.GUIDANCE_PRIMARY if is_selected or is_hover else MentorshipUIColors.SLATE_GRAY
        pygame.draw.circle(screen, num_color, num_center, 14)

        num_text = self.fonts['small_bold'].render(str(index + 1), True, MentorshipUIColors.TEXT_LIGHT)
        num_rect = num_text.get_rect(center=num_center)
        screen.blit(num_text, num_rect)

        # Choice text
        text_color = MentorshipUIColors.TEXT_LIGHT if is_selected else MentorshipUIColors.TEXT_PRIMARY
        text_surface = self.fonts['body'].render(text, True, text_color)
        screen.blit(text_surface, (rect.x + 52, rect.centery - text_surface.get_height() // 2))

    def draw_result_text(self, screen: pygame.Surface, text: str,
                        center_x: int, y: int,
                        is_positive: bool = True, alpha: int = 255) -> None:
        """Draw result/outcome text"""
        color = MentorshipUIColors.SUCCESS_GREEN if is_positive else MentorshipUIColors.ERROR_RED
        text_surface = self.fonts['body'].render(text, True, color)

        if alpha < 255:
            text_surface.set_alpha(alpha)

        screen.blit(text_surface, (center_x - text_surface.get_width() // 2, y))

    def draw_checkmark(self, screen: pygame.Surface, center: Tuple[int, int],
                      size: int = 16, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw a checkmark icon"""
        if color is None:
            color = MentorshipUIColors.SUCCESS_GREEN

        # Circle background
        pygame.draw.circle(screen, color, center, size)

        # Checkmark
        check_points = [
            (center[0] - size * 0.4, center[1]),
            (center[0] - size * 0.1, center[1] + size * 0.35),
            (center[0] + size * 0.4, center[1] - size * 0.25)
        ]
        pygame.draw.lines(screen, MentorshipUIColors.TEXT_LIGHT, False, check_points, 3)

    def draw_x_mark(self, screen: pygame.Surface, center: Tuple[int, int],
                   size: int = 16, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Draw an X mark icon"""
        if color is None:
            color = MentorshipUIColors.ERROR_RED

        # Circle background
        pygame.draw.circle(screen, color, center, size)

        # X mark
        offset = size * 0.35
        pygame.draw.line(screen, MentorshipUIColors.TEXT_LIGHT,
                        (center[0] - offset, center[1] - offset),
                        (center[0] + offset, center[1] + offset), 3)
        pygame.draw.line(screen, MentorshipUIColors.TEXT_LIGHT,
                        (center[0] + offset, center[1] - offset),
                        (center[0] - offset, center[1] + offset), 3)

    def draw_modal_overlay(self, screen: pygame.Surface, alpha: int = 160) -> None:
        """Draw a dark modal overlay"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

    def draw_continue_prompt(self, screen: pygame.Surface, center_x: int, y: int,
                            visible: bool = True) -> None:
        """Draw a pulsing continue prompt"""
        if not visible:
            return

        # Pulsing alpha
        alpha = MentorshipVisualHelpers.get_pulse_alpha(120, 255, 2.0)

        prompt_surface = self.fonts['small'].render("Press any key to continue...", True,
                                                    MentorshipUIColors.TEXT_MUTED)
        prompt_surface.set_alpha(alpha)
        screen.blit(prompt_surface, (center_x - prompt_surface.get_width() // 2, y))


# Global singleton for easy access
mentorship_visuals = MentorshipVisualComponents()

# Backwards compatibility aliases
dream_visuals = mentorship_visuals
DreamUIColors = MentorshipUIColors
DreamUIMetrics = MentorshipUIMetrics
DreamVisualHelpers = MentorshipVisualHelpers
DreamVisualComponents = MentorshipVisualComponents

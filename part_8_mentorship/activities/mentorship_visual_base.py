"""
Mentorship Visual Base Module
Dream/Surreal themed colors, helpers, and visual components
For Part 8 (Lack of Guidance/Mentorship) mini-games
"""
import pygame
import math
import time
import random
from typing import Tuple, Optional, List
from dataclasses import dataclass


class DreamUIColors:
    """Dream/Surreal color palette"""

    # Primary dream colors
    DREAM_PURPLE = (45, 30, 70)
    DREAM_PURPLE_LIGHT = (70, 50, 100)
    DREAM_PURPLE_DARK = (25, 15, 45)

    # Ethereal blues
    ETHEREAL_BLUE = (80, 100, 140)
    ETHEREAL_BLUE_LIGHT = (110, 135, 175)
    ETHEREAL_BLUE_DARK = (55, 75, 110)

    # Fog and mist (with alpha for transparency)
    FOG_GRAY = (120, 130, 150)
    FOG_LIGHT = (160, 170, 185)
    FOG_DARK = (80, 90, 110)

    # Glow colors
    GLOW_CYAN = (100, 180, 200)
    GLOW_CYAN_BRIGHT = (140, 220, 240)
    GLOW_PINK = (200, 140, 180)
    GLOW_PINK_BRIGHT = (240, 180, 215)
    GLOW_GOLD = (220, 190, 120)
    GLOW_GOLD_BRIGHT = (255, 230, 160)

    # Warning/Status
    UNCERTAIN_AMBER = (200, 160, 80)
    UNCERTAIN_AMBER_LIGHT = (230, 195, 120)
    COLLAPSE_RED = (180, 80, 90)
    SUCCESS_GREEN = (100, 180, 130)

    # Void and depth
    VOID_BLACK = (15, 10, 25)
    VOID_DEEP = (8, 5, 15)

    # Highlights
    STARLIGHT = (230, 235, 255)
    STARLIGHT_DIM = (180, 185, 200)
    MOONLIGHT = (200, 210, 230)

    # Door theme colors
    DOOR_WORK = (180, 150, 80)  # Amber/gold
    DOOR_SCHOOL = (80, 120, 180)  # Blue
    DOOR_HOMELESS = (90, 85, 95)  # Gray
    DOOR_UNKNOWN = (130, 80, 150)  # Purple

    # Text colors
    TEXT_ETHEREAL = (200, 210, 230)
    TEXT_DIM = (140, 150, 170)
    TEXT_GLOW = (240, 245, 255)
    TEXT_WARNING = (220, 180, 100)

    # Background layers
    BACKGROUND_DREAM = (20, 15, 35)
    OVERLAY_FOG = (100, 110, 130, 80)


class DreamUIMetrics:
    """Consistent spacing and sizing for dream theme"""

    # Spacing (fluid, dreamlike)
    SPACING_XS = 4
    SPACING_SM = 10
    SPACING_MD = 20
    SPACING_LG = 30
    SPACING_XL = 45

    # Border radius (soft, rounded)
    RADIUS_SMALL = 8
    RADIUS_MEDIUM = 15
    RADIUS_LARGE = 25
    RADIUS_ROUND = 50

    # Glow sizes
    GLOW_SM = 5
    GLOW_MD = 12
    GLOW_LG = 20
    GLOW_XL = 35

    # Float animation
    FLOAT_AMPLITUDE = 8
    FLOAT_SPEED = 0.8

    # Door dimensions
    DOOR_WIDTH = 120
    DOOR_HEIGHT = 200

    # Block/orb sizes
    ORB_RADIUS = 45
    BLOCK_WIDTH = 110
    BLOCK_HEIGHT = 55


@dataclass
class FloatAnimation:
    """Floating animation state"""
    offset: float = 0.0
    phase: float = 0.0
    amplitude: float = 8.0
    speed: float = 1.0

    def update(self, dt: float) -> None:
        self.phase += dt * self.speed
        self.offset = math.sin(self.phase) * self.amplitude

    @property
    def y_offset(self) -> int:
        return int(self.offset)


@dataclass
class GlowPulse:
    """Pulsing glow animation"""
    intensity: float = 0.5
    phase: float = 0.0
    speed: float = 2.0
    min_intensity: float = 0.3
    max_intensity: float = 1.0

    def update(self, dt: float) -> None:
        self.phase += dt * self.speed
        range_val = self.max_intensity - self.min_intensity
        self.intensity = self.min_intensity + (math.sin(self.phase) + 1) / 2 * range_val

    @property
    def alpha(self) -> int:
        return int(self.intensity * 255)


class DreamVisualHelpers:
    """Static helper functions for drawing dream-themed elements"""

    @staticmethod
    def draw_glow(screen: pygame.Surface, center: Tuple[int, int],
                  radius: int, color: Tuple[int, int, int],
                  intensity: float = 0.5, layers: int = 5) -> None:
        """Draw a soft radial glow effect"""
        for i in range(layers, 0, -1):
            layer_radius = radius + i * (radius // layers)
            alpha = int(40 * intensity * (1 - i / (layers + 1)))
            if alpha > 0:
                glow_surface = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, alpha),
                                 (layer_radius, layer_radius), layer_radius)
                screen.blit(glow_surface,
                          (center[0] - layer_radius, center[1] - layer_radius))

    @staticmethod
    def draw_soft_shadow(screen: pygame.Surface, rect: pygame.Rect,
                         offset: int = 8, blur_layers: int = 4) -> None:
        """Draw a soft, blurred shadow"""
        for i in range(blur_layers, 0, -1):
            alpha = int(30 * (1 - i / (blur_layers + 1)))
            expand = i * 3
            shadow_rect = pygame.Rect(
                rect.x + offset - expand,
                rect.y + offset - expand,
                rect.width + expand * 2,
                rect.height + expand * 2
            )
            shadow_surface = pygame.Surface(
                (shadow_rect.width, shadow_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(shadow_surface, (0, 0, 0, alpha),
                           (0, 0, shadow_rect.width, shadow_rect.height),
                           border_radius=DreamUIMetrics.RADIUS_MEDIUM)
            screen.blit(shadow_surface, shadow_rect)

    @staticmethod
    def draw_fog_wisps(screen: pygame.Surface, rect: pygame.Rect,
                       time_val: float, density: int = 5) -> None:
        """Draw drifting fog wisps across an area"""
        fog_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        for i in range(density):
            phase = time_val * 0.3 + i * 1.2
            x = rect.width * 0.1 + (math.sin(phase) + 1) / 2 * rect.width * 0.8
            y = rect.height * (i / density)
            width = 80 + math.sin(phase * 0.7) * 30
            alpha = int(25 + math.sin(phase * 1.3) * 15)

            for layer in range(3):
                layer_alpha = alpha // (layer + 1)
                layer_width = width + layer * 20
                layer_height = 15 + layer * 8
                pygame.draw.ellipse(fog_surface,
                                  (*DreamUIColors.FOG_GRAY, layer_alpha),
                                  (x - layer_width // 2, y - layer_height // 2,
                                   layer_width, layer_height))

        screen.blit(fog_surface, rect)

    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int],
                         color2: Tuple[int, int, int],
                         t: float) -> Tuple[int, int, int]:
        """Smoothly interpolate between two colors"""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )

    @staticmethod
    def draw_ethereal_text(screen: pygame.Surface, text: str,
                           center: Tuple[int, int], font: pygame.font.Font,
                           color: Tuple[int, int, int],
                           glow_color: Optional[Tuple[int, int, int]] = None,
                           alpha: int = 255) -> None:
        """Draw text with ethereal glow effect"""
        if glow_color is None:
            glow_color = color

        # Glow layer
        for offset in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, 1)]:
            glow_surface = font.render(text, True, (*glow_color, min(alpha // 3, 80)))
            screen.blit(glow_surface,
                       (center[0] - glow_surface.get_width() // 2 + offset[0] * 2,
                        center[1] - glow_surface.get_height() // 2 + offset[1] * 2))

        # Main text
        text_surface = font.render(text, True, color)
        if alpha < 255:
            text_surface.set_alpha(alpha)
        screen.blit(text_surface,
                   (center[0] - text_surface.get_width() // 2,
                    center[1] - text_surface.get_height() // 2))

    @staticmethod
    def draw_vignette(screen: pygame.Surface, intensity: float = 0.4) -> None:
        """Draw a soft vignette at screen edges"""
        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(0, height, 4):
            for x in range(0, width, 4):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                alpha = int(intensity * 255 * (dist / max_dist) ** 2)
                if alpha > 0:
                    pygame.draw.rect(vignette, (0, 0, 0, min(alpha, 200)), (x, y, 4, 4))

        screen.blit(vignette, (0, 0))


class DreamVisualComponents:
    """Reusable visual components for mentorship/dream games"""

    def __init__(self):
        self.fonts = {}
        self.time_offset = random.random() * 100  # Random starting phase
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('Georgia', 42, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('Georgia', 32)
            self.fonts['body'] = pygame.font.SysFont('Georgia', 22)
            self.fonts['small'] = pygame.font.SysFont('Georgia', 18)
            self.fonts['tiny'] = pygame.font.SysFont('Georgia', 14)
            self.fonts['ethereal'] = pygame.font.SysFont('Georgia', 28, italic=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 48)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['body'] = pygame.font.Font(None, 26)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['tiny'] = pygame.font.Font(None, 16)
            self.fonts['ethereal'] = pygame.font.Font(None, 32)

    def get_time(self) -> float:
        """Get animation time with offset"""
        return time.time() + self.time_offset

    def draw_glowing_panel(self, screen: pygame.Surface, rect: pygame.Rect,
                           glow_color: Tuple[int, int, int] = DreamUIColors.GLOW_CYAN,
                           bg_color: Optional[Tuple[int, int, int]] = None,
                           glow_intensity: float = 0.5,
                           border_alpha: int = 180) -> None:
        """Draw a panel with soft outer glow"""
        if bg_color is None:
            bg_color = DreamUIColors.DREAM_PURPLE_DARK

        # Outer glow
        for i in range(4, 0, -1):
            glow_rect = rect.inflate(i * 8, i * 8)
            alpha = int(30 * glow_intensity * (1 - i / 5))
            glow_surface = pygame.Surface(
                (glow_rect.width, glow_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(glow_surface, (*glow_color, alpha),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=DreamUIMetrics.RADIUS_LARGE + i * 3)
            screen.blit(glow_surface, glow_rect)

        # Shadow
        DreamVisualHelpers.draw_soft_shadow(screen, rect)

        # Panel background
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*bg_color, 230),
                        (0, 0, rect.width, rect.height),
                        border_radius=DreamUIMetrics.RADIUS_LARGE)
        screen.blit(panel_surface, rect)

        # Border with glow
        pygame.draw.rect(screen, (*glow_color, border_alpha), rect, 2,
                        border_radius=DreamUIMetrics.RADIUS_LARGE)

    def draw_floating_block(self, screen: pygame.Surface, rect: pygame.Rect,
                            label: str, color: Tuple[int, int, int],
                            icon: str = "", float_offset: int = 0,
                            is_dragging: bool = False, is_hover: bool = False,
                            glow_intensity: float = 0.0) -> None:
        """Draw a floating block with glow effect"""
        # Apply float offset
        draw_rect = pygame.Rect(rect.x, rect.y + float_offset, rect.width, rect.height)

        # Glow when hovering or selected
        if is_hover or glow_intensity > 0:
            intensity = max(0.6 if is_hover else 0, glow_intensity)
            DreamVisualHelpers.draw_glow(screen, draw_rect.center,
                                        draw_rect.width // 2, color, intensity)

        # Shadow (larger when dragging)
        if is_dragging:
            DreamVisualHelpers.draw_soft_shadow(screen, draw_rect, 15, 6)
        else:
            DreamVisualHelpers.draw_soft_shadow(screen, draw_rect, 6, 3)

        # Block background with gradient feel
        block_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)

        # Main fill
        alpha = 240 if is_dragging else 220
        pygame.draw.rect(block_surface, (*color, alpha),
                        (0, 0, draw_rect.width, draw_rect.height),
                        border_radius=DreamUIMetrics.RADIUS_MEDIUM)

        # Inner highlight
        highlight_rect = pygame.Rect(3, 3, draw_rect.width - 6, draw_rect.height // 3)
        highlight_color = DreamVisualHelpers.interpolate_color(color, (255, 255, 255), 0.2)
        pygame.draw.rect(block_surface, (*highlight_color, 60),
                        highlight_rect,
                        border_top_left_radius=DreamUIMetrics.RADIUS_MEDIUM - 2,
                        border_top_right_radius=DreamUIMetrics.RADIUS_MEDIUM - 2)

        screen.blit(block_surface, draw_rect)

        # Border
        border_color = DreamVisualHelpers.interpolate_color(color, DreamUIColors.STARLIGHT, 0.4)
        pygame.draw.rect(screen, border_color, draw_rect, 2,
                        border_radius=DreamUIMetrics.RADIUS_MEDIUM)

        # Icon and label
        text_y = draw_rect.centery

        if icon:
            try:
                icon_font = pygame.font.SysFont('Segoe UI Emoji', 22)
            except:
                icon_font = self.fonts['body']
            icon_surface = icon_font.render(icon, True, DreamUIColors.TEXT_GLOW)
            screen.blit(icon_surface,
                       (draw_rect.x + 12, text_y - icon_surface.get_height() // 2))
            label_x = draw_rect.x + 42
        else:
            label_x = draw_rect.centerx

        label_surface = self.fonts['body'].render(label, True, DreamUIColors.TEXT_GLOW)
        if icon:
            screen.blit(label_surface,
                       (label_x, text_y - label_surface.get_height() // 2))
        else:
            screen.blit(label_surface,
                       (label_x - label_surface.get_width() // 2,
                        text_y - label_surface.get_height() // 2))

    def draw_dream_door(self, screen: pygame.Surface, rect: pygame.Rect,
                        label: str, color: Tuple[int, int, int],
                        is_hover: bool = False, is_selected: bool = False,
                        reveal_progress: float = 0.0) -> None:
        """Draw an ornate dream door with ethereal frame"""
        t = self.get_time()

        # Door glow (stronger on hover/select)
        glow_intensity = 0.3
        if is_hover:
            glow_intensity = 0.7
        if is_selected:
            glow_intensity = 1.0

        # Pulsing glow
        pulse = (math.sin(t * 2) + 1) / 2 * 0.2
        glow_intensity += pulse

        DreamVisualHelpers.draw_glow(screen, rect.center,
                                    rect.width // 2 + 20, color, glow_intensity, 6)

        # Door frame (outer)
        frame_rect = rect.inflate(16, 16)
        frame_color = DreamVisualHelpers.interpolate_color(color, DreamUIColors.STARLIGHT, 0.3)
        pygame.draw.rect(screen, frame_color, frame_rect,
                        border_radius=DreamUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, (*DreamUIColors.VOID_BLACK, 200), frame_rect, 3,
                        border_radius=DreamUIMetrics.RADIUS_MEDIUM)

        # Door body
        door_color = color if not is_hover else DreamVisualHelpers.interpolate_color(
            color, (255, 255, 255), 0.15)
        pygame.draw.rect(screen, door_color, rect,
                        border_radius=DreamUIMetrics.RADIUS_SMALL)

        # Door panels (decorative)
        panel_margin = 12
        panel_height = (rect.height - panel_margin * 3) // 2
        for i, y_off in enumerate([panel_margin, panel_margin * 2 + panel_height]):
            panel = pygame.Rect(rect.x + panel_margin, rect.y + y_off,
                              rect.width - panel_margin * 2, panel_height)
            panel_color = DreamVisualHelpers.interpolate_color(color, DreamUIColors.VOID_BLACK, 0.2)
            pygame.draw.rect(screen, panel_color, panel,
                           border_radius=DreamUIMetrics.RADIUS_SMALL - 2)
            pygame.draw.rect(screen, (*DreamUIColors.VOID_BLACK, 100), panel, 1,
                           border_radius=DreamUIMetrics.RADIUS_SMALL - 2)

        # Door handle
        handle_x = rect.right - 25
        handle_y = rect.centery
        handle_glow = DreamUIColors.GLOW_GOLD if is_hover else DreamUIColors.UNCERTAIN_AMBER
        DreamVisualHelpers.draw_glow(screen, (handle_x, handle_y), 8, handle_glow, 0.5 if is_hover else 0.3)
        pygame.draw.circle(screen, DreamUIColors.GLOW_GOLD, (handle_x, handle_y), 8)
        pygame.draw.circle(screen, DreamUIColors.STARLIGHT, (handle_x, handle_y), 5)

        # Door border
        border_alpha = 200 if is_hover else 150
        pygame.draw.rect(screen, (*DreamUIColors.STARLIGHT, border_alpha), rect, 2,
                        border_radius=DreamUIMetrics.RADIUS_SMALL)

        # Floating label above door
        label_y = rect.top - 30 + int(math.sin(t * 1.5) * 3)
        DreamVisualHelpers.draw_ethereal_text(screen, label, (rect.centerx, label_y),
                                             self.fonts['heading'], DreamUIColors.TEXT_ETHEREAL,
                                             color)

        # Light burst effect when selected
        if is_selected and reveal_progress > 0:
            burst_alpha = int(255 * reveal_progress * (1 - reveal_progress))
            burst_surface = pygame.Surface((rect.width + 100, rect.height + 100), pygame.SRCALPHA)
            for r in range(5, 0, -1):
                radius = int((rect.width // 2 + 50) * reveal_progress * (r / 5))
                pygame.draw.circle(burst_surface, (*DreamUIColors.STARLIGHT, burst_alpha // r),
                                 (burst_surface.get_width() // 2, burst_surface.get_height() // 2),
                                 radius)
            screen.blit(burst_surface, (rect.centerx - burst_surface.get_width() // 2,
                                        rect.centery - burst_surface.get_height() // 2))

    def draw_balance_scale(self, screen: pygame.Surface, center: Tuple[int, int],
                           beam_width: int = 300, beam_angle: float = 0.0,
                           left_weight: int = 0, right_weight: int = 0,
                           is_collapsing: bool = False, collapse_progress: float = 0.0) -> Tuple[pygame.Rect, pygame.Rect]:
        """Draw an ethereal balance scale, return pan rects"""
        t = self.get_time()

        # Gentle sway animation
        sway = math.sin(t * 0.5) * 0.02 if not is_collapsing else 0
        actual_angle = beam_angle + sway

        # Collapse animation
        if is_collapsing:
            actual_angle += collapse_progress * 0.8
            alpha_mult = 1 - collapse_progress * 0.7

        else:
            alpha_mult = 1.0

        # Base/fulcrum
        base_height = 80
        base_width = 60

        # Draw ethereal glow at base
        DreamVisualHelpers.draw_glow(screen, (center[0], center[1] + 30),
                                    40, DreamUIColors.GLOW_CYAN, 0.4 * alpha_mult)

        # Base triangle
        base_points = [
            (center[0], center[1] - 10),
            (center[0] - base_width // 2, center[1] + base_height // 2),
            (center[0] + base_width // 2, center[1] + base_height // 2)
        ]
        pygame.draw.polygon(screen, DreamUIColors.ETHEREAL_BLUE, base_points)
        pygame.draw.polygon(screen, (*DreamUIColors.STARLIGHT, int(180 * alpha_mult)),
                          base_points, 2)

        # Beam
        beam_surface = pygame.Surface((beam_width + 40, 30), pygame.SRCALPHA)
        beam_rect = pygame.Rect(20, 10, beam_width, 10)
        pygame.draw.rect(beam_surface, (*DreamUIColors.ETHEREAL_BLUE_LIGHT, int(220 * alpha_mult)),
                        beam_rect, border_radius=5)
        pygame.draw.rect(beam_surface, (*DreamUIColors.STARLIGHT, int(150 * alpha_mult)),
                        beam_rect, 2, border_radius=5)

        # Rotate beam
        rotated_beam = pygame.transform.rotate(beam_surface, -math.degrees(actual_angle))
        beam_center = (center[0] - rotated_beam.get_width() // 2,
                      center[1] - rotated_beam.get_height() // 2 - 15)
        screen.blit(rotated_beam, beam_center)

        # Calculate pan positions
        pan_radius = 50
        chain_length = 80

        left_beam_x = center[0] - beam_width // 2
        right_beam_x = center[0] + beam_width // 2

        # Apply rotation to find pan positions
        cos_a, sin_a = math.cos(actual_angle), math.sin(actual_angle)

        left_pan_x = center[0] + (left_beam_x - center[0]) * cos_a
        left_pan_y = center[1] - 15 + (left_beam_x - center[0]) * sin_a + chain_length

        right_pan_x = center[0] + (right_beam_x - center[0]) * cos_a
        right_pan_y = center[1] - 15 + (right_beam_x - center[0]) * (-sin_a) + chain_length

        # Draw chains
        chain_alpha = int(180 * alpha_mult)
        pygame.draw.line(screen, (*DreamUIColors.STARLIGHT_DIM, chain_alpha),
                        (left_beam_x + (center[0] - left_beam_x) * (1 - cos_a) / 2, center[1] - 15),
                        (left_pan_x, left_pan_y - pan_radius // 2), 2)
        pygame.draw.line(screen, (*DreamUIColors.STARLIGHT_DIM, chain_alpha),
                        (right_beam_x - (right_beam_x - center[0]) * (1 - cos_a) / 2, center[1] - 15),
                        (right_pan_x, right_pan_y - pan_radius // 2), 2)

        # Draw pans with glow
        for pan_x, pan_y, weight in [(left_pan_x, left_pan_y, left_weight),
                                      (right_pan_x, right_pan_y, right_weight)]:
            # Glow based on weight
            glow_intensity = 0.3 + (weight / 15) * 0.4 if weight > 0 else 0.2
            DreamVisualHelpers.draw_glow(screen, (int(pan_x), int(pan_y)),
                                        pan_radius, DreamUIColors.GLOW_PINK,
                                        glow_intensity * alpha_mult)

            # Pan
            pan_color = (*DreamUIColors.ETHEREAL_BLUE_LIGHT, int(200 * alpha_mult))
            pan_surface = pygame.Surface((pan_radius * 2, pan_radius), pygame.SRCALPHA)
            pygame.draw.ellipse(pan_surface, pan_color, (0, 0, pan_radius * 2, pan_radius))
            screen.blit(pan_surface, (pan_x - pan_radius, pan_y - pan_radius // 2))

            # Pan rim
            pygame.draw.ellipse(screen, (*DreamUIColors.STARLIGHT, int(150 * alpha_mult)),
                              (pan_x - pan_radius, pan_y - pan_radius // 2,
                               pan_radius * 2, pan_radius), 2)

        # Return pan rects for collision
        left_pan_rect = pygame.Rect(left_pan_x - pan_radius, left_pan_y - pan_radius // 2,
                                    pan_radius * 2, pan_radius)
        right_pan_rect = pygame.Rect(right_pan_x - pan_radius, right_pan_y - pan_radius // 2,
                                     pan_radius * 2, pan_radius)

        return left_pan_rect, right_pan_rect

    def draw_choice_orb(self, screen: pygame.Surface, center: Tuple[int, int],
                        radius: int, label: str, color: Tuple[int, int, int],
                        is_hover: bool = False, is_selected: bool = False,
                        float_offset: int = 0) -> None:
        """Draw a glowing choice orb"""
        t = self.get_time()

        draw_y = center[1] + float_offset

        # Pulsing glow
        pulse = (math.sin(t * 2) + 1) / 2
        glow_intensity = 0.3 + pulse * 0.2
        if is_hover:
            glow_intensity = 0.7 + pulse * 0.2
        if is_selected:
            glow_intensity = 1.0

        DreamVisualHelpers.draw_glow(screen, (center[0], draw_y),
                                    radius + 15, color, glow_intensity, 5)

        # Orb
        orb_surface = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        orb_center = (radius + 5, radius + 5)

        # Main orb
        pygame.draw.circle(orb_surface, (*color, 200), orb_center, radius)

        # Inner highlight
        highlight_offset = (-radius // 4, -radius // 4)
        pygame.draw.circle(orb_surface, (*DreamUIColors.STARLIGHT, 80),
                         (orb_center[0] + highlight_offset[0],
                          orb_center[1] + highlight_offset[1]),
                         radius // 3)

        screen.blit(orb_surface, (center[0] - radius - 5, draw_y - radius - 5))

        # Border
        border_color = DreamUIColors.STARLIGHT if is_hover or is_selected else color
        pygame.draw.circle(screen, (*border_color, 180), (center[0], draw_y), radius, 2)

        # Label
        label_surface = self.fonts['small'].render(label, True, DreamUIColors.TEXT_GLOW)
        screen.blit(label_surface,
                   (center[0] - label_surface.get_width() // 2,
                    draw_y - label_surface.get_height() // 2))

    def draw_priority_slot(self, screen: pygame.Surface, rect: pygame.Rect,
                           number: int, is_filled: bool = False,
                           is_hover: bool = False, float_offset: int = 0) -> None:
        """Draw a priority slot with floating number"""
        t = self.get_time()
        draw_rect = pygame.Rect(rect.x, rect.y + float_offset, rect.width, rect.height)

        # Glow ring
        glow_intensity = 0.2
        if is_hover:
            glow_intensity = 0.5
        if is_filled:
            glow_intensity = 0.7

        glow_color = DreamUIColors.GLOW_CYAN if not is_filled else DreamUIColors.SUCCESS_GREEN
        DreamVisualHelpers.draw_glow(screen, draw_rect.center,
                                    draw_rect.width // 2, glow_color, glow_intensity)

        # Slot ring
        ring_color = glow_color if is_hover or is_filled else DreamUIColors.FOG_GRAY
        pygame.draw.ellipse(screen, (*DreamUIColors.VOID_BLACK, 150), draw_rect)
        pygame.draw.ellipse(screen, (*ring_color, 180), draw_rect, 3)

        # Floating number
        if not is_filled:
            number_y = draw_rect.centery + int(math.sin(t * 1.5 + number) * 4)
            number_text = f"#{number}"
            DreamVisualHelpers.draw_ethereal_text(screen, number_text,
                                                 (draw_rect.centerx, number_y),
                                                 self.fonts['heading'],
                                                 DreamUIColors.TEXT_DIM,
                                                 glow_color)

    def draw_uncertainty_meter(self, screen: pygame.Surface, rect: pygame.Rect,
                               uncertainty: float, label: str = "Uncertainty") -> None:
        """Draw an uncertainty/confusion meter"""
        t = self.get_time()

        # Background
        pygame.draw.rect(screen, DreamUIColors.VOID_BLACK, rect,
                        border_radius=rect.height // 2)

        # Fill with flickering effect
        if uncertainty > 0:
            flicker = 1 + math.sin(t * 8) * 0.05 * uncertainty
            fill_width = int((rect.width - 4) * min(1.0, uncertainty * flicker))

            # Gradient fill
            for x in range(fill_width):
                progress = x / max(1, fill_width)
                color = DreamVisualHelpers.interpolate_color(
                    DreamUIColors.UNCERTAIN_AMBER,
                    DreamUIColors.COLLAPSE_RED,
                    progress * uncertainty
                )
                pygame.draw.line(screen, color,
                               (rect.x + 2 + x, rect.y + 2),
                               (rect.x + 2 + x, rect.bottom - 2))

        # Border
        border_color = DreamUIColors.FOG_GRAY if uncertainty < 0.7 else DreamUIColors.COLLAPSE_RED
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=rect.height // 2)

        # Label
        label_surface = self.fonts['tiny'].render(label, True, DreamUIColors.TEXT_DIM)
        screen.blit(label_surface, (rect.x, rect.y - 18))

    def draw_dream_background(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw the dreamscape background with stars and fog"""
        t = self.get_time()

        # Base gradient
        for y in range(rect.height):
            progress = y / rect.height
            color = DreamVisualHelpers.interpolate_color(
                DreamUIColors.VOID_DEEP,
                DreamUIColors.DREAM_PURPLE_DARK,
                progress
            )
            pygame.draw.line(screen, color, (rect.x, rect.y + y),
                           (rect.right, rect.y + y))

        # Stars
        random.seed(42)  # Consistent star pattern
        for _ in range(50):
            x = random.randint(rect.x, rect.right)
            y = random.randint(rect.y, rect.y + rect.height // 2)
            twinkle = (math.sin(t * random.uniform(1, 3) + random.random() * 10) + 1) / 2
            alpha = int(100 + twinkle * 100)
            size = 1 if random.random() > 0.3 else 2
            pygame.draw.circle(screen, (*DreamUIColors.STARLIGHT, alpha), (x, y), size)

        # Fog at bottom
        DreamVisualHelpers.draw_fog_wisps(screen,
                                         pygame.Rect(rect.x, rect.y + rect.height * 2 // 3,
                                                    rect.width, rect.height // 3),
                                         t)


# Global instance for easy access
dream_visuals = DreamVisualComponents()

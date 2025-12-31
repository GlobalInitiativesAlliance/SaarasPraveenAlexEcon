"""
Mentorship Feedback System
Ethereal text animations, glow pulses, banners, and dream effects
For Part 8 (Lack of Guidance/Mentorship) mini-games
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass, field

from .mentorship_visual_base import DreamUIColors, DreamVisualHelpers


@dataclass
class EtherealText:
    """Floating ethereal text that fades in/out"""
    text: str
    x: float
    y: float
    color: Tuple[int, int, int]
    glow_color: Tuple[int, int, int]
    font_name: str  # 'title', 'heading', 'body', 'ethereal'
    life: float
    max_life: float
    fade_in_time: float = 0.5
    float_amplitude: float = 5.0
    phase: float = 0.0
    typewriter: bool = False
    chars_revealed: int = 0


@dataclass
class GlowPulseEffect:
    """Pulsing glow effect at a location"""
    x: float
    y: float
    radius: int
    color: Tuple[int, int, int]
    life: float
    max_life: float
    pulse_speed: float = 3.0
    expanding: bool = False
    max_radius: int = 0


@dataclass
class DreamBanner:
    """Sliding banner with ethereal message"""
    text: str
    color: Tuple[int, int, int]
    bg_color: Tuple[int, int, int]
    life: float
    max_life: float
    slide_progress: float = 0.0
    slide_in_time: float = 0.5
    slide_out_time: float = 0.5
    position: str = 'center'  # 'top', 'center', 'bottom'


@dataclass
class CollapseEffect:
    """Visual effect for balance scale collapse"""
    x: float
    y: float
    progress: float = 0.0
    duration: float = 2.0
    active: bool = True


@dataclass
class DoorReveal:
    """Door opening light reveal effect"""
    x: float
    y: float
    width: int
    height: int
    progress: float = 0.0
    duration: float = 1.5
    color: Tuple[int, int, int] = field(default_factory=lambda: DreamUIColors.STARLIGHT)


class DreamFeedbackManager:
    """
    Manages all feedback effects for mentorship/dream games
    Includes ethereal text, glow pulses, banners, and special effects
    """

    def __init__(self):
        self.texts: List[EtherealText] = []
        self.pulses: List[GlowPulseEffect] = []
        self.banners: List[DreamBanner] = []
        self.collapse_effect: Optional[CollapseEffect] = None
        self.door_reveals: List[DoorReveal] = []
        self.fonts = {}
        self.screen_fade_alpha = 0
        self.screen_fade_target = 0
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('Georgia', 42, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('Georgia', 32)
            self.fonts['body'] = pygame.font.SysFont('Georgia', 22)
            self.fonts['small'] = pygame.font.SysFont('Georgia', 18)
            self.fonts['ethereal'] = pygame.font.SysFont('Georgia', 28, italic=True)
            self.fonts['banner'] = pygame.font.SysFont('Georgia', 36, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 48)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['body'] = pygame.font.Font(None, 26)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['ethereal'] = pygame.font.Font(None, 32)
            self.fonts['banner'] = pygame.font.Font(None, 42)

    def update(self, dt: float) -> None:
        """Update all feedback effects"""
        # Update ethereal texts
        for text in self.texts[:]:
            text.life -= dt
            if text.life <= 0:
                self.texts.remove(text)
                continue

            text.phase += dt * 2

            # Typewriter effect
            if text.typewriter:
                reveal_speed = len(text.text) / (text.max_life - text.fade_in_time - 0.5)
                elapsed = text.max_life - text.life
                if elapsed > text.fade_in_time:
                    text.chars_revealed = min(len(text.text),
                                             int((elapsed - text.fade_in_time) * reveal_speed))

        # Update glow pulses
        for pulse in self.pulses[:]:
            pulse.life -= dt
            if pulse.life <= 0:
                self.pulses.remove(pulse)
                continue

            if pulse.expanding and pulse.max_radius > 0:
                progress = 1 - (pulse.life / pulse.max_life)
                pulse.radius = int(pulse.max_radius * progress)

        # Update banners
        for banner in self.banners[:]:
            banner.life -= dt
            if banner.life <= 0:
                self.banners.remove(banner)
                continue

            elapsed = banner.max_life - banner.life
            if elapsed < banner.slide_in_time:
                banner.slide_progress = elapsed / banner.slide_in_time
            elif banner.life < banner.slide_out_time:
                banner.slide_progress = banner.life / banner.slide_out_time
            else:
                banner.slide_progress = 1.0

        # Update collapse effect
        if self.collapse_effect and self.collapse_effect.active:
            self.collapse_effect.progress += dt / self.collapse_effect.duration
            if self.collapse_effect.progress >= 1.0:
                self.collapse_effect.active = False

        # Update door reveals
        for reveal in self.door_reveals[:]:
            reveal.progress += dt / reveal.duration
            if reveal.progress >= 1.0:
                self.door_reveals.remove(reveal)

        # Update screen fade
        if self.screen_fade_alpha != self.screen_fade_target:
            diff = self.screen_fade_target - self.screen_fade_alpha
            self.screen_fade_alpha += diff * dt * 3
            if abs(diff) < 1:
                self.screen_fade_alpha = self.screen_fade_target

    def render(self, screen: pygame.Surface) -> None:
        """Render all feedback effects"""
        screen_rect = screen.get_rect()

        # Render door reveals (behind other elements)
        for reveal in self.door_reveals:
            self._render_door_reveal(screen, reveal)

        # Render glow pulses
        for pulse in self.pulses:
            self._render_pulse(screen, pulse)

        # Render ethereal texts
        for text in self.texts:
            self._render_text(screen, text)

        # Render banners
        for banner in self.banners:
            self._render_banner(screen, banner, screen_rect)

        # Render collapse effect overlay
        if self.collapse_effect and self.collapse_effect.active:
            self._render_collapse_overlay(screen, screen_rect)

        # Render screen fade overlay
        if self.screen_fade_alpha > 1:
            fade_surface = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            fade_surface.fill((*DreamUIColors.VOID_BLACK, int(self.screen_fade_alpha)))
            screen.blit(fade_surface, (0, 0))

    def _render_text(self, screen: pygame.Surface, text: EtherealText) -> None:
        """Render ethereal text with glow and float"""
        if text.font_name not in self.fonts:
            text.font_name = 'body'

        font = self.fonts[text.font_name]

        # Calculate alpha based on life
        life_ratio = text.life / text.max_life
        elapsed = text.max_life - text.life

        if elapsed < text.fade_in_time:
            alpha = int(255 * (elapsed / text.fade_in_time))
        elif text.life < 0.5:
            alpha = int(255 * (text.life / 0.5))
        else:
            alpha = 255

        # Float offset
        float_y = int(math.sin(text.phase) * text.float_amplitude)

        # Get text to display
        display_text = text.text
        if text.typewriter:
            display_text = text.text[:text.chars_revealed]

        # Draw glow layers
        glow_surface = font.render(display_text, True, text.glow_color)
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]:
            glow_alpha = alpha // 4
            if glow_alpha > 0:
                glow_copy = glow_surface.copy()
                glow_copy.set_alpha(glow_alpha)
                screen.blit(glow_copy,
                           (text.x - glow_surface.get_width() // 2 + offset[0],
                            text.y + float_y - glow_surface.get_height() // 2 + offset[1]))

        # Draw main text
        main_surface = font.render(display_text, True, text.color)
        main_surface.set_alpha(alpha)
        screen.blit(main_surface,
                   (text.x - main_surface.get_width() // 2,
                    text.y + float_y - main_surface.get_height() // 2))

    def _render_pulse(self, screen: pygame.Surface, pulse: GlowPulseEffect) -> None:
        """Render pulsing glow effect"""
        life_ratio = pulse.life / pulse.max_life

        # Pulsing intensity
        pulse_val = (math.sin(time.time() * pulse.pulse_speed) + 1) / 2
        intensity = 0.5 + pulse_val * 0.5

        # Draw glow layers
        for i in range(5, 0, -1):
            layer_radius = pulse.radius + i * 8
            alpha = int(50 * intensity * life_ratio * (1 - i / 6))
            if alpha > 0:
                glow_surface = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*pulse.color, alpha),
                                 (layer_radius, layer_radius), layer_radius)
                screen.blit(glow_surface,
                          (int(pulse.x - layer_radius), int(pulse.y - layer_radius)))

    def _render_banner(self, screen: pygame.Surface, banner: DreamBanner,
                       screen_rect: pygame.Rect) -> None:
        """Render sliding banner"""
        # Calculate position
        text_surface = self.fonts['banner'].render(banner.text, True, banner.color)
        banner_height = text_surface.get_height() + 40

        if banner.position == 'top':
            target_y = 50
        elif banner.position == 'bottom':
            target_y = screen_rect.height - banner_height - 50
        else:
            target_y = screen_rect.centery - banner_height // 2

        # Slide animation
        start_y = -banner_height if banner.position == 'top' else screen_rect.height
        current_y = start_y + (target_y - start_y) * self._ease_out(banner.slide_progress)

        # Draw banner background with glow
        banner_width = text_surface.get_width() + 80
        banner_x = screen_rect.centerx - banner_width // 2

        # Outer glow
        for i in range(4, 0, -1):
            glow_rect = pygame.Rect(banner_x - i * 5, current_y - i * 3,
                                    banner_width + i * 10, banner_height + i * 6)
            glow_alpha = int(30 * banner.slide_progress * (1 - i / 5))
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*banner.color, glow_alpha),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=15 + i * 2)
            screen.blit(glow_surface, glow_rect)

        # Banner background
        banner_rect = pygame.Rect(banner_x, current_y, banner_width, banner_height)
        bg_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*banner.bg_color, int(230 * banner.slide_progress)),
                        (0, 0, banner_width, banner_height), border_radius=15)
        screen.blit(bg_surface, banner_rect)

        # Border
        pygame.draw.rect(screen, (*banner.color, int(200 * banner.slide_progress)),
                        banner_rect, 2, border_radius=15)

        # Text
        text_alpha = int(255 * banner.slide_progress)
        text_surface.set_alpha(text_alpha)
        screen.blit(text_surface,
                   (screen_rect.centerx - text_surface.get_width() // 2,
                    current_y + 20))

    def _render_door_reveal(self, screen: pygame.Surface, reveal: DoorReveal) -> None:
        """Render door opening light burst"""
        # Expanding light from door center
        progress = self._ease_out(reveal.progress)

        # Light rays
        num_rays = 12
        max_length = max(reveal.width, reveal.height) * 2

        for i in range(num_rays):
            angle = (i / num_rays) * 2 * math.pi
            ray_length = max_length * progress

            end_x = reveal.x + math.cos(angle) * ray_length
            end_y = reveal.y + math.sin(angle) * ray_length

            # Fade based on progress
            alpha = int(150 * (1 - progress))
            if alpha > 0:
                pygame.draw.line(screen, (*reveal.color, alpha),
                               (reveal.x, reveal.y), (end_x, end_y), 3)

        # Central glow
        glow_radius = int(reveal.width * 0.5 * progress)
        if glow_radius > 0:
            for i in range(5, 0, -1):
                layer_radius = glow_radius + i * 10
                alpha = int(80 * (1 - progress) * (1 - i / 6))
                if alpha > 0:
                    glow_surface = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*reveal.color, alpha),
                                     (layer_radius, layer_radius), layer_radius)
                    screen.blit(glow_surface,
                              (int(reveal.x - layer_radius), int(reveal.y - layer_radius)))

    def _render_collapse_overlay(self, screen: pygame.Surface, screen_rect: pygame.Rect) -> None:
        """Render collapse effect overlay with screen darkening"""
        if not self.collapse_effect:
            return

        progress = self.collapse_effect.progress

        # Darken screen
        dark_alpha = int(100 * progress)
        dark_surface = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
        dark_surface.fill((*DreamUIColors.VOID_BLACK, dark_alpha))
        screen.blit(dark_surface, (0, 0))

        # Red vignette at edges
        vignette_intensity = 0.3 * progress
        DreamVisualHelpers.draw_vignette(screen, vignette_intensity)

    def _ease_out(self, t: float) -> float:
        """Ease out cubic for smooth animations"""
        return 1 - (1 - t) ** 3

    def clear(self) -> None:
        """Clear all effects"""
        self.texts.clear()
        self.pulses.clear()
        self.banners.clear()
        self.collapse_effect = None
        self.door_reveals.clear()
        self.screen_fade_alpha = 0
        self.screen_fade_target = 0

    # ==================== Effect Creation Functions ====================

    def add_ethereal_text(self, text: str, x: float, y: float,
                          color: Tuple[int, int, int] = None,
                          glow_color: Tuple[int, int, int] = None,
                          font_name: str = 'ethereal',
                          duration: float = 3.0,
                          typewriter: bool = False) -> None:
        """Add floating ethereal text"""
        if color is None:
            color = DreamUIColors.TEXT_ETHEREAL
        if glow_color is None:
            glow_color = DreamUIColors.GLOW_CYAN

        self.texts.append(EtherealText(
            text=text,
            x=x,
            y=y,
            color=color,
            glow_color=glow_color,
            font_name=font_name,
            life=duration,
            max_life=duration,
            typewriter=typewriter
        ))

    def add_glow_pulse(self, x: float, y: float, radius: int = 30,
                       color: Tuple[int, int, int] = None,
                       duration: float = 1.0, expanding: bool = False) -> None:
        """Add pulsing glow effect"""
        if color is None:
            color = DreamUIColors.GLOW_CYAN

        self.pulses.append(GlowPulseEffect(
            x=x,
            y=y,
            radius=radius if not expanding else 5,
            color=color,
            life=duration,
            max_life=duration,
            expanding=expanding,
            max_radius=radius if expanding else 0
        ))

    def add_uncertain_future_banner(self) -> None:
        """Add the 'Uncertain Future' banner"""
        self.banners.append(DreamBanner(
            text="Your path remains uncertain...",
            color=DreamUIColors.TEXT_WARNING,
            bg_color=DreamUIColors.DREAM_PURPLE_DARK,
            life=4.0,
            max_life=4.0,
            position='center'
        ))

    def add_collapse_banner(self) -> None:
        """Add 'Future Plan Collapsed' banner"""
        self.banners.append(DreamBanner(
            text="Future Plan Collapsed",
            color=DreamUIColors.COLLAPSE_RED,
            bg_color=DreamUIColors.VOID_BLACK,
            life=3.5,
            max_life=3.5,
            position='center'
        ))

    def add_balance_banner(self) -> None:
        """Add 'Temporary Balance' banner"""
        self.banners.append(DreamBanner(
            text="Temporary Balance Achieved",
            color=DreamUIColors.SUCCESS_GREEN,
            bg_color=DreamUIColors.DREAM_PURPLE_DARK,
            life=3.0,
            max_life=3.0,
            position='center'
        ))

    def add_mentor_found_banner(self) -> None:
        """Add 'Mentor Found' special banner"""
        self.banners.append(DreamBanner(
            text="A Guide Appears...",
            color=DreamUIColors.GLOW_GOLD_BRIGHT,
            bg_color=DreamUIColors.DREAM_PURPLE,
            life=3.5,
            max_life=3.5,
            position='center'
        ))

    def add_no_guidance_banner(self) -> None:
        """Add 'No Guidance' banner"""
        self.banners.append(DreamBanner(
            text="No guidance provided",
            color=DreamUIColors.FOG_GRAY,
            bg_color=DreamUIColors.VOID_BLACK,
            life=3.0,
            max_life=3.0,
            position='center'
        ))

    def add_incomplete_banner(self) -> None:
        """Add 'Incomplete Plan' banner"""
        self.banners.append(DreamBanner(
            text="Plan Incomplete - No Feedback Given",
            color=DreamUIColors.UNCERTAIN_AMBER,
            bg_color=DreamUIColors.VOID_BLACK,
            life=3.5,
            max_life=3.5,
            position='center'
        ))

    def start_collapse_effect(self, x: float, y: float, duration: float = 2.0) -> None:
        """Start the balance collapse effect"""
        self.collapse_effect = CollapseEffect(
            x=x,
            y=y,
            duration=duration
        )

    def add_door_reveal(self, x: float, y: float, width: int, height: int,
                        color: Tuple[int, int, int] = None) -> None:
        """Add door opening light reveal"""
        if color is None:
            color = DreamUIColors.STARLIGHT

        self.door_reveals.append(DoorReveal(
            x=x,
            y=y,
            width=width,
            height=height,
            color=color
        ))

    def fade_to_black(self, target_alpha: int = 200) -> None:
        """Start fading screen to dark"""
        self.screen_fade_target = target_alpha

    def fade_from_black(self) -> None:
        """Start fading back from dark"""
        self.screen_fade_target = 0

    def get_collapse_progress(self) -> float:
        """Get current collapse effect progress"""
        if self.collapse_effect:
            return self.collapse_effect.progress
        return 0.0

    def is_collapse_active(self) -> bool:
        """Check if collapse effect is active"""
        return self.collapse_effect is not None and self.collapse_effect.active


# Global instance for easy access
dream_feedback = DreamFeedbackManager()

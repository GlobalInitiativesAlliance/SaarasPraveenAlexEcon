"""
Time Constraints Feedback System
Conflict banners, stress vignettes, overload effects, clock pulses
For Part 9 (Time Constraints / Conflicting Responsibilities) mini-games
"""
import pygame
import math
import time
from typing import Tuple, Optional, List
from dataclasses import dataclass, field

from .time_visual_base import PressureUIColors, PressureVisualHelpers


@dataclass
class PressureText:
    """Urgent text that appears with pressure styling"""
    text: str
    x: float
    y: float
    color: Tuple[int, int, int]
    glow_color: Tuple[int, int, int]
    font_name: str  # 'title', 'heading', 'body', 'small'
    life: float
    max_life: float
    fade_in_time: float = 0.3
    shake_intensity: float = 0.0
    pulse: bool = False
    pulse_phase: float = 0.0
    typewriter: bool = False
    chars_revealed: int = 0


@dataclass
class ConflictBanner:
    """Warning banner for conflicts and urgency"""
    text: str
    color: Tuple[int, int, int]
    bg_color: Tuple[int, int, int]
    life: float
    max_life: float
    slide_progress: float = 0.0
    slide_in_time: float = 0.3
    slide_out_time: float = 0.4
    position: str = 'center'  # 'top', 'center', 'bottom'
    shake: bool = False
    flash: bool = False
    flash_phase: float = 0.0


@dataclass
class ClockPulse:
    """Clock ticking pulse effect"""
    x: float
    y: float
    radius: float
    max_radius: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    tick_count: int = 0


@dataclass
class OverloadEffect:
    """Visual effect for stress overload"""
    progress: float = 0.0
    duration: float = 2.5
    active: bool = True
    screen_shake: float = 0.0
    flash_intensity: float = 0.0


@dataclass
class ConsequenceFlash:
    """Flash effect for choice consequences"""
    x: float
    y: float
    width: int
    height: int
    color: Tuple[int, int, int]
    life: float
    max_life: float
    positive: bool = True


@dataclass
class OverlapHighlight:
    """Highlight for calendar overlap conflicts"""
    rect: pygame.Rect
    color: Tuple[int, int, int]
    life: float
    max_life: float
    pulse_phase: float = 0.0


class PressureFeedbackManager:
    """
    Manages all feedback effects for time constraint games
    Includes conflict banners, stress vignettes, clock pulses, overload effects
    """

    def __init__(self):
        self.texts: List[PressureText] = []
        self.banners: List[ConflictBanner] = []
        self.clock_pulses: List[ClockPulse] = []
        self.consequence_flashes: List[ConsequenceFlash] = []
        self.overlap_highlights: List[OverlapHighlight] = []
        self.overload_effect: Optional[OverloadEffect] = None
        self.fonts = {}

        # Stress vignette state
        self.stress_level = 0.0
        self.target_stress = 0.0

        # Screen effects
        self.screen_shake_offset = (0, 0)
        self.screen_shake_intensity = 0.0
        self.screen_flash_alpha = 0
        self.screen_flash_color = PressureUIColors.PRESSURE_RED
        self.screen_fade_alpha = 0
        self.screen_fade_target = 0

        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['title'] = pygame.font.SysFont('Arial', 42, bold=True)
            self.fonts['heading'] = pygame.font.SysFont('Arial', 32, bold=True)
            self.fonts['body'] = pygame.font.SysFont('Arial', 22)
            self.fonts['small'] = pygame.font.SysFont('Arial', 18)
            self.fonts['banner'] = pygame.font.SysFont('Arial', 38, bold=True)
            self.fonts['urgent'] = pygame.font.SysFont('Arial', 28, bold=True)
        except:
            self.fonts['title'] = pygame.font.Font(None, 48)
            self.fonts['heading'] = pygame.font.Font(None, 36)
            self.fonts['body'] = pygame.font.Font(None, 26)
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['banner'] = pygame.font.Font(None, 44)
            self.fonts['urgent'] = pygame.font.Font(None, 32)

    def update(self, dt: float) -> None:
        """Update all feedback effects"""
        # Update pressure texts
        for text in self.texts[:]:
            text.life -= dt
            if text.life <= 0:
                self.texts.remove(text)
                continue

            if text.pulse:
                text.pulse_phase += dt * 6

            # Typewriter effect
            if text.typewriter:
                reveal_speed = len(text.text) / (text.max_life - text.fade_in_time - 0.3)
                elapsed = text.max_life - text.life
                if elapsed > text.fade_in_time:
                    text.chars_revealed = min(len(text.text),
                                             int((elapsed - text.fade_in_time) * reveal_speed))

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

            if banner.flash:
                banner.flash_phase += dt * 10

        # Update clock pulses
        for pulse in self.clock_pulses[:]:
            pulse.life -= dt
            if pulse.life <= 0:
                self.clock_pulses.remove(pulse)
                continue

            progress = 1 - (pulse.life / pulse.max_life)
            pulse.radius = pulse.max_radius * progress

        # Update consequence flashes
        for flash in self.consequence_flashes[:]:
            flash.life -= dt
            if flash.life <= 0:
                self.consequence_flashes.remove(flash)

        # Update overlap highlights
        for highlight in self.overlap_highlights[:]:
            highlight.life -= dt
            highlight.pulse_phase += dt * 8
            if highlight.life <= 0:
                self.overlap_highlights.remove(highlight)

        # Update overload effect
        if self.overload_effect and self.overload_effect.active:
            self.overload_effect.progress += dt / self.overload_effect.duration

            # Screen shake increases with progress
            self.overload_effect.screen_shake = self.overload_effect.progress * 15

            # Flash intensity peaks in middle
            if self.overload_effect.progress < 0.5:
                self.overload_effect.flash_intensity = self.overload_effect.progress * 2
            else:
                self.overload_effect.flash_intensity = (1 - self.overload_effect.progress) * 2

            if self.overload_effect.progress >= 1.0:
                self.overload_effect.active = False

        # Update stress vignette
        stress_diff = self.target_stress - self.stress_level
        self.stress_level += stress_diff * dt * 2

        # Update screen shake
        if self.screen_shake_intensity > 0:
            self.screen_shake_offset = (
                (math.sin(time.time() * 50) * self.screen_shake_intensity),
                (math.cos(time.time() * 47) * self.screen_shake_intensity)
            )
            self.screen_shake_intensity *= 0.9
            if self.screen_shake_intensity < 0.5:
                self.screen_shake_intensity = 0
                self.screen_shake_offset = (0, 0)

        # Update screen flash
        if self.screen_flash_alpha > 0:
            self.screen_flash_alpha = max(0, self.screen_flash_alpha - dt * 400)

        # Update screen fade
        if self.screen_fade_alpha != self.screen_fade_target:
            diff = self.screen_fade_target - self.screen_fade_alpha
            self.screen_fade_alpha += diff * dt * 3
            if abs(diff) < 1:
                self.screen_fade_alpha = self.screen_fade_target

    def render(self, screen: pygame.Surface) -> None:
        """Render all feedback effects"""
        screen_rect = screen.get_rect()

        # Render overlap highlights (background layer)
        for highlight in self.overlap_highlights:
            self._render_overlap_highlight(screen, highlight)

        # Render clock pulses
        for pulse in self.clock_pulses:
            self._render_clock_pulse(screen, pulse)

        # Render consequence flashes
        for flash in self.consequence_flashes:
            self._render_consequence_flash(screen, flash)

        # Render pressure texts
        for text in self.texts:
            self._render_text(screen, text)

        # Render banners
        for banner in self.banners:
            self._render_banner(screen, banner, screen_rect)

        # Render stress vignette
        if self.stress_level > 0.1:
            self._render_stress_vignette(screen, screen_rect)

        # Render overload effect overlay
        if self.overload_effect and self.overload_effect.active:
            self._render_overload_overlay(screen, screen_rect)

        # Render screen flash
        if self.screen_flash_alpha > 0:
            flash_surface = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            flash_surface.fill((*self.screen_flash_color, int(self.screen_flash_alpha)))
            screen.blit(flash_surface, (0, 0))

        # Render screen fade overlay
        if self.screen_fade_alpha > 1:
            fade_surface = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(self.screen_fade_alpha)))
            screen.blit(fade_surface, (0, 0))

    def _render_text(self, screen: pygame.Surface, text: PressureText) -> None:
        """Render pressure text with effects"""
        if text.font_name not in self.fonts:
            text.font_name = 'body'

        font = self.fonts[text.font_name]

        # Calculate alpha based on life
        elapsed = text.max_life - text.life
        if elapsed < text.fade_in_time:
            alpha = int(255 * (elapsed / text.fade_in_time))
        elif text.life < 0.3:
            alpha = int(255 * (text.life / 0.3))
        else:
            alpha = 255

        # Shake offset
        shake_x = 0
        shake_y = 0
        if text.shake_intensity > 0:
            shake_x = math.sin(time.time() * 30) * text.shake_intensity
            shake_y = math.cos(time.time() * 27) * text.shake_intensity

        # Pulse scale effect
        scale = 1.0
        if text.pulse:
            scale = 1.0 + math.sin(text.pulse_phase) * 0.05

        # Get text to display
        display_text = text.text
        if text.typewriter:
            display_text = text.text[:text.chars_revealed]

        # Draw glow
        glow_surface = font.render(display_text, True, text.glow_color)
        glow_alpha = alpha // 3
        if glow_alpha > 0:
            for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                glow_copy = glow_surface.copy()
                glow_copy.set_alpha(glow_alpha)
                if scale != 1.0:
                    new_size = (int(glow_copy.get_width() * scale),
                               int(glow_copy.get_height() * scale))
                    glow_copy = pygame.transform.scale(glow_copy, new_size)
                screen.blit(glow_copy,
                           (text.x + shake_x - glow_copy.get_width() // 2 + offset[0],
                            text.y + shake_y - glow_copy.get_height() // 2 + offset[1]))

        # Draw main text
        main_surface = font.render(display_text, True, text.color)
        main_surface.set_alpha(alpha)
        if scale != 1.0:
            new_size = (int(main_surface.get_width() * scale),
                       int(main_surface.get_height() * scale))
            main_surface = pygame.transform.scale(main_surface, new_size)
        screen.blit(main_surface,
                   (text.x + shake_x - main_surface.get_width() // 2,
                    text.y + shake_y - main_surface.get_height() // 2))

    def _render_banner(self, screen: pygame.Surface, banner: ConflictBanner,
                       screen_rect: pygame.Rect) -> None:
        """Render conflict banner with slide and flash"""
        text_surface = self.fonts['banner'].render(banner.text, True, banner.color)
        banner_height = text_surface.get_height() + 40

        if banner.position == 'top':
            target_y = 60
        elif banner.position == 'bottom':
            target_y = screen_rect.height - banner_height - 60
        else:
            target_y = screen_rect.centery - banner_height // 2

        # Slide animation
        start_y = -banner_height if banner.position == 'top' else screen_rect.height
        current_y = start_y + (target_y - start_y) * self._ease_out(banner.slide_progress)

        # Shake offset
        shake_x = 0
        shake_y = 0
        if banner.shake:
            shake_x = math.sin(time.time() * 40) * 3
            shake_y = math.cos(time.time() * 37) * 2

        # Flash effect
        flash_mod = 1.0
        if banner.flash:
            flash_mod = 0.7 + math.sin(banner.flash_phase) * 0.3

        # Banner dimensions
        banner_width = text_surface.get_width() + 100
        banner_x = screen_rect.centerx - banner_width // 2 + shake_x

        # Warning glow
        for i in range(4, 0, -1):
            glow_rect = pygame.Rect(banner_x - i * 6, current_y - i * 3 + shake_y,
                                    banner_width + i * 12, banner_height + i * 6)
            glow_alpha = int(40 * banner.slide_progress * flash_mod * (1 - i / 5))
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*banner.color, glow_alpha),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=10)
            screen.blit(glow_surface, glow_rect)

        # Banner background
        banner_rect = pygame.Rect(banner_x, current_y + shake_y, banner_width, banner_height)
        bg_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*banner.bg_color, int(240 * banner.slide_progress)),
                        (0, 0, banner_width, banner_height), border_radius=8)
        screen.blit(bg_surface, banner_rect)

        # Border with warning color
        border_color = tuple(int(c * flash_mod) for c in banner.color)
        pygame.draw.rect(screen, (*border_color, int(220 * banner.slide_progress)),
                        banner_rect, 3, border_radius=8)

        # Text
        text_alpha = int(255 * banner.slide_progress * flash_mod)
        text_surface.set_alpha(text_alpha)
        screen.blit(text_surface,
                   (screen_rect.centerx - text_surface.get_width() // 2 + shake_x,
                    current_y + 20 + shake_y))

    def _render_clock_pulse(self, screen: pygame.Surface, pulse: ClockPulse) -> None:
        """Render clock tick pulse ring"""
        life_ratio = pulse.life / pulse.max_life
        alpha = int(180 * life_ratio)

        if alpha > 0 and pulse.radius > 0:
            # Main ring
            try:
                pygame.draw.circle(screen, (*pulse.color, alpha),
                                 (int(pulse.x), int(pulse.y)),
                                 int(pulse.radius), 3)
            except:
                pass

            # Inner glow ring
            inner_alpha = alpha // 2
            if inner_alpha > 0 and pulse.radius > 5:
                try:
                    pygame.draw.circle(screen, (*pulse.color, inner_alpha),
                                     (int(pulse.x), int(pulse.y)),
                                     int(pulse.radius - 5), 2)
                except:
                    pass

    def _render_consequence_flash(self, screen: pygame.Surface,
                                   flash: ConsequenceFlash) -> None:
        """Render consequence flash effect"""
        life_ratio = flash.life / flash.max_life
        alpha = int(150 * life_ratio)

        if alpha > 0:
            flash_surface = pygame.Surface((flash.width, flash.height), pygame.SRCALPHA)
            pygame.draw.rect(flash_surface, (*flash.color, alpha),
                           (0, 0, flash.width, flash.height), border_radius=8)

            # Border glow
            border_alpha = int(200 * life_ratio)
            pygame.draw.rect(flash_surface, (*flash.color, border_alpha),
                           (0, 0, flash.width, flash.height), 3, border_radius=8)

            screen.blit(flash_surface, (flash.x, flash.y))

    def _render_overlap_highlight(self, screen: pygame.Surface,
                                   highlight: OverlapHighlight) -> None:
        """Render overlap conflict highlight"""
        life_ratio = highlight.life / highlight.max_life
        pulse_mod = 0.6 + math.sin(highlight.pulse_phase) * 0.4
        alpha = int(100 * life_ratio * pulse_mod)

        if alpha > 0:
            highlight_surface = pygame.Surface(
                (highlight.rect.width, highlight.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (*highlight.color, alpha),
                           (0, 0, highlight.rect.width, highlight.rect.height))
            screen.blit(highlight_surface, highlight.rect)

            # Pulsing border
            border_alpha = int(200 * life_ratio * pulse_mod)
            pygame.draw.rect(screen, (*highlight.color, border_alpha),
                           highlight.rect, 3)

    def _render_stress_vignette(self, screen: pygame.Surface,
                                 screen_rect: pygame.Rect) -> None:
        """Render red stress vignette at screen edges"""
        vignette_intensity = self.stress_level * 0.5
        PressureVisualHelpers.draw_stress_vignette(screen, vignette_intensity,
                                                   PressureUIColors.PRESSURE_RED)

    def _render_overload_overlay(self, screen: pygame.Surface,
                                  screen_rect: pygame.Rect) -> None:
        """Render overload effect with screen distortion"""
        if not self.overload_effect:
            return

        progress = self.overload_effect.progress

        # Red flash overlay
        flash_alpha = int(60 * self.overload_effect.flash_intensity)
        if flash_alpha > 0:
            flash_surface = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            flash_surface.fill((*PressureUIColors.PRESSURE_RED, flash_alpha))
            screen.blit(flash_surface, (0, 0))

        # Darkening as it progresses
        if progress > 0.6:
            dark_progress = (progress - 0.6) / 0.4
            dark_alpha = int(180 * dark_progress)
            dark_surface = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
            dark_surface.fill((0, 0, 0, dark_alpha))
            screen.blit(dark_surface, (0, 0))

        # Intensifying red vignette
        vignette_intensity = progress * 0.7
        PressureVisualHelpers.draw_stress_vignette(screen, vignette_intensity,
                                                   PressureUIColors.PRESSURE_RED)

    def _ease_out(self, t: float) -> float:
        """Ease out cubic for smooth animations"""
        return 1 - (1 - t) ** 3

    def clear(self) -> None:
        """Clear all effects"""
        self.texts.clear()
        self.banners.clear()
        self.clock_pulses.clear()
        self.consequence_flashes.clear()
        self.overlap_highlights.clear()
        self.overload_effect = None
        self.stress_level = 0.0
        self.target_stress = 0.0
        self.screen_shake_intensity = 0.0
        self.screen_shake_offset = (0, 0)
        self.screen_flash_alpha = 0
        self.screen_fade_alpha = 0
        self.screen_fade_target = 0

    # ==================== Effect Creation Functions ====================

    def add_pressure_text(self, text: str, x: float, y: float,
                          color: Tuple[int, int, int] = None,
                          glow_color: Tuple[int, int, int] = None,
                          font_name: str = 'urgent',
                          duration: float = 3.0,
                          shake: float = 0.0,
                          pulse: bool = False,
                          typewriter: bool = False) -> None:
        """Add urgent pressure text"""
        if color is None:
            color = PressureUIColors.HIGHLIGHT_WHITE
        if glow_color is None:
            glow_color = PressureUIColors.URGENT_ORANGE

        self.texts.append(PressureText(
            text=text,
            x=x,
            y=y,
            color=color,
            glow_color=glow_color,
            font_name=font_name,
            life=duration,
            max_life=duration,
            shake_intensity=shake,
            pulse=pulse,
            typewriter=typewriter
        ))

    def add_conflict_banner(self, text: str = "CONFLICT!",
                            color: Tuple[int, int, int] = None,
                            position: str = 'center',
                            duration: float = 3.0,
                            shake: bool = True,
                            flash: bool = True) -> None:
        """Add conflict warning banner"""
        if color is None:
            color = PressureUIColors.PRESSURE_RED

        self.banners.append(ConflictBanner(
            text=text,
            color=color,
            bg_color=PressureUIColors.DARK_BG,
            life=duration,
            max_life=duration,
            position=position,
            shake=shake,
            flash=flash
        ))

    def add_overload_banner(self) -> None:
        """Add 'OVERLOAD' warning banner"""
        self.add_conflict_banner(
            text="OVERLOAD!",
            color=PressureUIColors.PRESSURE_RED,
            duration=3.5,
            shake=True,
            flash=True
        )

    def add_time_conflict_banner(self) -> None:
        """Add time conflict detected banner"""
        self.add_conflict_banner(
            text="TIME CONFLICT DETECTED",
            color=PressureUIColors.CONFLICT_MAGENTA,
            duration=3.0,
            shake=True,
            flash=True
        )

    def add_no_good_options_banner(self) -> None:
        """Add 'No Good Options' banner for impossible choices"""
        self.banners.append(ConflictBanner(
            text="No good options remain...",
            color=PressureUIColors.URGENT_ORANGE,
            bg_color=PressureUIColors.DARK_BG,
            life=3.0,
            max_life=3.0,
            position='center',
            shake=False,
            flash=False
        ))

    def add_consequence_banner(self, positive: bool, text: str = None) -> None:
        """Add consequence result banner"""
        if text is None:
            text = "Choice made." if positive else "Consequence unavoidable."

        color = PressureUIColors.CALM_BLUE_LIGHT if positive else PressureUIColors.PRESSURE_RED

        self.banners.append(ConflictBanner(
            text=text,
            color=color,
            bg_color=PressureUIColors.DARK_BG,
            life=2.5,
            max_life=2.5,
            position='center',
            shake=not positive,
            flash=not positive
        ))

    def add_urgent_summons_banner(self) -> None:
        """Add urgent court summons banner"""
        self.add_conflict_banner(
            text="URGENT: COURT DATE CONFLICTS!",
            color=PressureUIColors.PRESSURE_RED,
            duration=4.0,
            shake=True,
            flash=True
        )

    def add_clock_pulse(self, x: float, y: float, max_radius: float = 80,
                        color: Tuple[int, int, int] = None,
                        duration: float = 0.8) -> None:
        """Add expanding clock tick pulse"""
        if color is None:
            color = PressureUIColors.TIME_GOLD

        self.clock_pulses.append(ClockPulse(
            x=x,
            y=y,
            radius=0,
            max_radius=max_radius,
            life=duration,
            max_life=duration,
            color=color
        ))

    def add_consequence_flash(self, x: float, y: float, width: int, height: int,
                              positive: bool = True,
                              duration: float = 0.6) -> None:
        """Add consequence flash effect on an area"""
        color = PressureUIColors.CALM_BLUE_LIGHT if positive else PressureUIColors.PRESSURE_RED

        self.consequence_flashes.append(ConsequenceFlash(
            x=x,
            y=y,
            width=width,
            height=height,
            color=color,
            life=duration,
            max_life=duration,
            positive=positive
        ))

    def add_overlap_highlight(self, rect: pygame.Rect,
                              color: Tuple[int, int, int] = None,
                              duration: float = 2.0) -> None:
        """Add pulsing overlap conflict highlight"""
        if color is None:
            color = PressureUIColors.CONFLICT_MAGENTA

        self.overlap_highlights.append(OverlapHighlight(
            rect=rect.copy(),
            color=color,
            life=duration,
            max_life=duration
        ))

    def start_overload_effect(self, duration: float = 2.5) -> None:
        """Start the stress overload effect"""
        self.overload_effect = OverloadEffect(
            duration=duration
        )

    def set_stress_level(self, level: float) -> None:
        """Set target stress level for vignette (0.0 to 1.0)"""
        self.target_stress = max(0, min(1, level))

    def trigger_screen_shake(self, intensity: float = 8.0) -> None:
        """Trigger screen shake effect"""
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)

    def trigger_screen_flash(self, color: Tuple[int, int, int] = None,
                             intensity: int = 150) -> None:
        """Trigger screen flash effect"""
        if color is None:
            color = PressureUIColors.PRESSURE_RED
        self.screen_flash_color = color
        self.screen_flash_alpha = intensity

    def fade_to_black(self, target_alpha: int = 200) -> None:
        """Start fading screen to dark"""
        self.screen_fade_target = target_alpha

    def fade_from_black(self) -> None:
        """Start fading back from dark"""
        self.screen_fade_target = 0

    def get_screen_shake_offset(self) -> Tuple[float, float]:
        """Get current screen shake offset for rendering"""
        if self.overload_effect and self.overload_effect.active:
            shake = self.overload_effect.screen_shake
            return (
                math.sin(time.time() * 45) * shake,
                math.cos(time.time() * 42) * shake
            )
        return self.screen_shake_offset

    def is_overload_active(self) -> bool:
        """Check if overload effect is active"""
        return self.overload_effect is not None and self.overload_effect.active

    def get_overload_progress(self) -> float:
        """Get current overload effect progress"""
        if self.overload_effect:
            return self.overload_effect.progress
        return 0.0


# Global instance for easy access
pressure_feedback = PressureFeedbackManager()

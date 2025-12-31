"""
Mentorship Effects Module (Minimal)
Simple visual feedback effects - NO PARTICLES
For Part 8 (Lack of Guidance/Mentorship) mini-games

This replaces the heavy particle system with lightweight effect helpers.
"""
import math
import time
from typing import Tuple


class MentorshipEffects:
    """Minimal visual feedback effects - no particles, no per-frame allocations"""

    @staticmethod
    def get_hover_scale(is_hovered: bool, current: float, dt: float,
                       target_scale: float = 1.03) -> float:
        """Get smooth scale interpolation for hover feedback"""
        target = target_scale if is_hovered else 1.0
        speed = 10.0
        return current + (target - current) * min(dt * speed, 1.0)

    @staticmethod
    def get_pulse_alpha(min_alpha: int = 180, max_alpha: int = 255,
                       speed: float = 2.0) -> int:
        """Get a pulsing alpha value for attention effects"""
        t = time.time() * speed
        return int(min_alpha + (max_alpha - min_alpha) * (0.5 + 0.5 * math.sin(t)))

    @staticmethod
    def get_pulse_scale(base: float = 1.0, amplitude: float = 0.02,
                       speed: float = 3.0) -> float:
        """Get a pulsing scale value"""
        t = time.time() * speed
        return base + amplitude * math.sin(t)

    @staticmethod
    def get_fade_alpha(progress: float, fade_in_end: float = 0.2,
                      fade_out_start: float = 0.8) -> int:
        """Get alpha for fade in/out based on progress (0.0 to 1.0)"""
        if progress < fade_in_end:
            return int(255 * (progress / fade_in_end))
        elif progress > fade_out_start:
            return int(255 * (1.0 - (progress - fade_out_start) / (1.0 - fade_out_start)))
        else:
            return 255

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out function for smooth animations"""
        return 1.0 - pow(1.0 - t, 3)

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out function"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2


class DummyParticleSystem:
    """
    Dummy particle system that does nothing.
    Maintains API compatibility with old code.
    """

    def __init__(self, max_particles: int = 0):
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, screen) -> None:
        pass

    def clear(self) -> None:
        pass

    def enable_ambient(self, rect) -> None:
        pass

    def disable_ambient(self) -> None:
        pass

    # All emission functions do nothing
    def emit_dust_motes(self, rect, count: int = 0) -> None:
        pass

    def emit_fog_wisps(self, rect, count: int = 0) -> None:
        pass

    def emit_glow_sparks(self, x: float, y: float, count: int = 0, color=None) -> None:
        pass

    def emit_star_burst(self, x: float, y: float, count: int = 0) -> None:
        pass

    def emit_collapse_particles(self, x: float, y: float, count: int = 0) -> None:
        pass

    def emit_question_marks(self, rect, count: int = 0) -> None:
        pass

    def emit_drag_trail(self, x: float, y: float, color=None) -> None:
        pass

    def emit_mentor_glow(self, x: float, y: float) -> None:
        pass

    def emit_scatter_to_fog(self, items) -> None:
        pass

    def emit_light_burst(self, x: float, y: float, color=None) -> None:
        pass

    def emit_success_sparkle(self, x: float, y: float, count: int = 0) -> None:
        pass


# Global instances for easy access
mentorship_effects = MentorshipEffects()

# Backwards compatibility - dummy particle system that does nothing
dream_particles = DummyParticleSystem()
DreamParticleSystem = DummyParticleSystem

"""
Time Constraints Effects System - Minimal Version
Replaces heavy particle system with lightweight helpers
For Part 9 (Time Constraints / Conflicting Responsibilities) mini-games
No per-frame surface creation, no particles, no lag
"""
import math
import time
from typing import Tuple

from .time_visual_base import PressureUIColors


class TimeEffects:
    """Minimal visual feedback helpers - no particles, no lag"""

    @staticmethod
    def get_hover_scale(is_hovered: bool, current: float, dt: float) -> float:
        """Simple scale interpolation for hover feedback"""
        target = 1.05 if is_hovered else 1.0
        return current + (target - current) * min(dt * 10, 1.0)

    @staticmethod
    def get_pulse_alpha(min_alpha: int = 200, max_alpha: int = 255, speed: float = 3.0) -> int:
        """Simple alpha pulse for attention effects"""
        t = time.time() * speed
        return int(min_alpha + (max_alpha - min_alpha) * (0.5 + 0.5 * math.sin(t)))

    @staticmethod
    def get_pulse_scale(min_scale: float = 0.95, max_scale: float = 1.05, speed: float = 3.0) -> float:
        """Simple scale pulse for attention effects"""
        t = time.time() * speed
        return min_scale + (max_scale - min_scale) * (0.5 + 0.5 * math.sin(t))

    @staticmethod
    def get_fade_alpha(progress: float, fade_in_end: float = 0.2, fade_out_start: float = 0.8) -> int:
        """Get alpha for fade-in/fade-out based on progress (0-1)"""
        if progress < fade_in_end:
            return int(255 * (progress / fade_in_end))
        elif progress > fade_out_start:
            return int(255 * (1 - (progress - fade_out_start) / (1 - fade_out_start)))
        return 255

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Ease-out cubic function for smooth animations"""
        return 1 - pow(1 - t, 3)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Ease-in-out quadratic for smooth transitions"""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2

    @staticmethod
    def get_urgency_color(stress_level: float) -> Tuple[int, int, int]:
        """Get color interpolated from calm to urgent based on stress"""
        if stress_level < 0.5:
            # Calm blue to warning orange
            t = stress_level * 2
            return (
                int(PressureUIColors.CALM_BLUE[0] + (PressureUIColors.URGENT_ORANGE[0] - PressureUIColors.CALM_BLUE[0]) * t),
                int(PressureUIColors.CALM_BLUE[1] + (PressureUIColors.URGENT_ORANGE[1] - PressureUIColors.CALM_BLUE[1]) * t),
                int(PressureUIColors.CALM_BLUE[2] + (PressureUIColors.URGENT_ORANGE[2] - PressureUIColors.CALM_BLUE[2]) * t)
            )
        else:
            # Warning orange to pressure red
            t = (stress_level - 0.5) * 2
            return (
                int(PressureUIColors.URGENT_ORANGE[0] + (PressureUIColors.PRESSURE_RED[0] - PressureUIColors.URGENT_ORANGE[0]) * t),
                int(PressureUIColors.URGENT_ORANGE[1] + (PressureUIColors.PRESSURE_RED[1] - PressureUIColors.URGENT_ORANGE[1]) * t),
                int(PressureUIColors.URGENT_ORANGE[2] + (PressureUIColors.PRESSURE_RED[2] - PressureUIColors.URGENT_ORANGE[2]) * t)
            )


class DummyParticleSystem:
    """
    No-op particle system for backwards compatibility
    All emit methods do nothing - particles are replaced with clean UI feedback
    """

    def __init__(self, max_particles: int = 300):
        self.max_particles = max_particles
        self.particles = []
        self.pulse_rings = []
        self.ambient_enabled = False
        self.ambient_rect = None
        self.stress_level = 0.0

    def update(self, dt: float) -> None:
        """No-op - no particles to update"""
        pass

    def render(self, screen) -> None:
        """No-op - no particles to render"""
        pass

    def clear(self) -> None:
        """No-op - no particles to clear"""
        pass

    def enable_ambient(self, rect, stress_level: float = 0.0) -> None:
        """No-op - ambient particles disabled"""
        self.ambient_enabled = True
        self.ambient_rect = rect
        self.stress_level = stress_level

    def disable_ambient(self) -> None:
        """No-op"""
        self.ambient_enabled = False

    def set_stress_level(self, level: float) -> None:
        """Store stress level but don't emit particles"""
        self.stress_level = max(0, min(1, level))

    # All emission methods are no-ops
    def emit_clock_ticks(self, center, radius: float, count: int = 12) -> None:
        pass

    def emit_alarm_particles(self, x: float, y: float, count: int = 8) -> None:
        pass

    def emit_stress_sparks(self, x: float, y: float, count: int = 15, intensity: float = 1.0) -> None:
        pass

    def emit_paper_scatter(self, x: float, y: float, count: int = 20) -> None:
        pass

    def emit_countdown_numbers(self, x: float, y: float, count: int = 5) -> None:
        pass

    def emit_conflict_pulse(self, x: float, y: float, color=None) -> None:
        pass

    def emit_overlap_warning(self, rect) -> None:
        pass

    def emit_drag_trail(self, x: float, y: float, color=None) -> None:
        pass

    def emit_selection_burst(self, x: float, y: float, color=None) -> None:
        pass

    def emit_urgent_notification(self, rect) -> None:
        pass


# Global instances for easy access
time_effects = TimeEffects()
time_particles = DummyParticleSystem()

# Backwards compatibility aliases
pressure_particles = time_particles
PressureParticleSystem = DummyParticleSystem

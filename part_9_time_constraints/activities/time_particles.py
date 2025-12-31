"""
Time Constraints Particle Effects System
Clock ticks, alarm particles, stress sparks, paper scatter
For Part 9 (Time Constraints / Conflicting Responsibilities) mini-games
"""
import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .time_visual_base import PressureUIColors


@dataclass
class PressureParticle:
    """Individual pressure/urgency particle"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    gravity: float = 0.0
    rotation: float = 0.0
    rotation_speed: float = 0.0
    shape: str = 'circle'  # 'circle', 'tick', 'exclaim', 'paper', 'spark', 'ring'
    alpha: int = 255
    pulse: bool = False
    pulse_phase: float = 0.0


@dataclass
class PulseRing:
    """Expanding pulse ring effect"""
    x: float
    y: float
    radius: float
    max_radius: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    width: int = 3


class PressureParticleSystem:
    """
    Particle system for time constraint/pressure themed effects
    Includes clock ticks, alarm particles, stress sparks, paper scatter
    """

    def __init__(self, max_particles: int = 300):
        self.particles: List[PressureParticle] = []
        self.pulse_rings: List[PulseRing] = []
        self.max_particles = max_particles
        self.ambient_enabled = False
        self.ambient_rect = None
        self.stress_level = 0.0

    def update(self, dt: float) -> None:
        """Update all particles"""
        # Update pressure particles
        for particle in self.particles[:]:
            particle.life -= dt
            if particle.life <= 0:
                self.particles.remove(particle)
                continue

            # Physics
            particle.x += particle.vx * dt * 60
            particle.y += particle.vy * dt * 60
            particle.vy += particle.gravity * dt * 60

            # Rotation
            particle.rotation += particle.rotation_speed * dt * 60

            # Pulse effect
            if particle.pulse:
                particle.pulse_phase += dt * 6
                pulse_scale = 0.8 + math.sin(particle.pulse_phase) * 0.2
                particle.size = particle.size * pulse_scale

            # Fade out
            life_ratio = particle.life / particle.max_life
            fade_curve = math.sin(life_ratio * math.pi / 2)
            particle.alpha = int(255 * fade_curve)

        # Update pulse rings
        for ring in self.pulse_rings[:]:
            ring.life -= dt
            if ring.life <= 0:
                self.pulse_rings.remove(ring)
                continue

            # Expand outward
            progress = 1 - (ring.life / ring.max_life)
            ring.radius = ring.max_radius * progress

        # Generate ambient particles if enabled
        if self.ambient_enabled and self.ambient_rect:
            spawn_chance = 0.03 + self.stress_level * 0.1
            if random.random() < spawn_chance:
                self._emit_ambient_particle()

    def render(self, screen: pygame.Surface) -> None:
        """Render all particles"""
        # Render pulse rings first (background)
        for ring in self.pulse_rings:
            life_ratio = ring.life / ring.max_life
            alpha = int(200 * life_ratio)
            if alpha > 0 and ring.radius > 0:
                try:
                    pygame.draw.circle(screen, (*ring.color, alpha),
                                     (int(ring.x), int(ring.y)),
                                     int(ring.radius), ring.width)
                except:
                    pass

        # Render particles
        for particle in self.particles:
            if particle.alpha <= 0:
                continue
            self._render_particle(screen, particle)

    def _render_particle(self, screen: pygame.Surface, particle: PressureParticle) -> None:
        """Render individual particle based on shape"""
        color_with_alpha = (*particle.color, particle.alpha)
        life_ratio = particle.life / particle.max_life
        size = max(1, int(particle.size))

        if particle.shape == 'circle':
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (size, size), size)
            screen.blit(surf, (int(particle.x) - size, int(particle.y) - size))

        elif particle.shape == 'spark':
            # Glowing spark
            for i in range(3, 0, -1):
                glow_alpha = particle.alpha // (i + 1)
                glow_size = size + i * 2
                pygame.draw.circle(screen, (*particle.color, glow_alpha),
                                 (int(particle.x), int(particle.y)), glow_size)
            pygame.draw.circle(screen, color_with_alpha[:3],
                             (int(particle.x), int(particle.y)), size)

        elif particle.shape == 'tick':
            # Clock tick mark
            tick_length = size
            angle = math.radians(particle.rotation)
            x1 = particle.x - math.cos(angle) * tick_length / 2
            y1 = particle.y - math.sin(angle) * tick_length / 2
            x2 = particle.x + math.cos(angle) * tick_length / 2
            y2 = particle.y + math.sin(angle) * tick_length / 2
            pygame.draw.line(screen, color_with_alpha[:3], (x1, y1), (x2, y2), 2)

        elif particle.shape == 'exclaim':
            # Exclamation mark
            try:
                font = pygame.font.SysFont('Arial', max(12, int(size)), bold=True)
            except:
                font = pygame.font.Font(None, max(12, int(size)))

            text_surface = font.render('!', True, color_with_alpha[:3])
            text_surface.set_alpha(particle.alpha)
            rotated = pygame.transform.rotate(text_surface, particle.rotation)
            screen.blit(rotated, (int(particle.x - rotated.get_width() // 2),
                                  int(particle.y - rotated.get_height() // 2)))

        elif particle.shape == 'paper':
            # Paper scrap (rectangle)
            paper_w = int(size * 1.5)
            paper_h = int(size)
            paper_surf = pygame.Surface((paper_w, paper_h), pygame.SRCALPHA)
            pygame.draw.rect(paper_surf, color_with_alpha, (0, 0, paper_w, paper_h))
            # Add a fold line
            pygame.draw.line(paper_surf, (*PressureUIColors.HIGHLIGHT_DIM, particle.alpha // 2),
                           (paper_w // 3, 0), (paper_w // 3, paper_h), 1)
            rotated = pygame.transform.rotate(paper_surf, particle.rotation)
            screen.blit(rotated, (int(particle.x - rotated.get_width() // 2),
                                  int(particle.y - rotated.get_height() // 2)))

        elif particle.shape == 'number':
            # Countdown number
            try:
                font = pygame.font.SysFont('Arial', max(14, int(size)), bold=True)
            except:
                font = pygame.font.Font(None, max(14, int(size)))

            # Use rotation as the number
            num = str(max(0, int(particle.rotation) % 10))
            text_surface = font.render(num, True, color_with_alpha[:3])
            text_surface.set_alpha(particle.alpha)
            screen.blit(text_surface, (int(particle.x - text_surface.get_width() // 2),
                                       int(particle.y - text_surface.get_height() // 2)))

    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
        self.pulse_rings.clear()

    def enable_ambient(self, rect: pygame.Rect, stress_level: float = 0.0) -> None:
        """Enable ambient particles in an area"""
        self.ambient_enabled = True
        self.ambient_rect = rect
        self.stress_level = stress_level

    def disable_ambient(self) -> None:
        """Disable ambient particles"""
        self.ambient_enabled = False

    def set_stress_level(self, level: float) -> None:
        """Update stress level for particle intensity"""
        self.stress_level = max(0, min(1, level))

    def _emit_ambient_particle(self) -> None:
        """Emit ambient stress particle"""
        if not self.ambient_rect or len(self.particles) >= self.max_particles:
            return

        # Particle color based on stress
        if self.stress_level < 0.5:
            color = random.choice([
                PressureUIColors.TIME_GOLD_DARK,
                PressureUIColors.CALM_BLUE,
                PressureUIColors.HIGHLIGHT_DIM
            ])
        else:
            color = random.choice([
                PressureUIColors.URGENT_ORANGE,
                PressureUIColors.PRESSURE_RED,
                PressureUIColors.STRESS_PURPLE
            ])

        self.particles.append(PressureParticle(
            x=random.uniform(self.ambient_rect.left, self.ambient_rect.right),
            y=random.uniform(self.ambient_rect.top, self.ambient_rect.bottom),
            vx=random.uniform(-0.3, 0.3),
            vy=random.uniform(-0.5, 0.2),
            life=random.uniform(2.0, 4.0),
            max_life=4.0,
            color=color,
            size=random.uniform(2, 4 + self.stress_level * 3),
            gravity=0.01,
            shape='circle',
            pulse=self.stress_level > 0.7
        ))

    # ==================== Emission Functions ====================

    def emit_clock_ticks(self, center: Tuple[float, float], radius: float, count: int = 12) -> None:
        """Emit clock tick marks radiating outward"""
        for i in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = (i / count) * 2 * math.pi
            speed = random.uniform(2, 4)

            self.particles.append(PressureParticle(
                x=center[0] + math.cos(angle) * radius * 0.5,
                y=center[1] + math.sin(angle) * radius * 0.5,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.5, 1.0),
                max_life=1.0,
                color=PressureUIColors.TIME_GOLD,
                size=random.uniform(8, 14),
                rotation=math.degrees(angle),
                shape='tick'
            ))

    def emit_alarm_particles(self, x: float, y: float, count: int = 8) -> None:
        """Emit alarm/warning exclamation particles"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4)

            self.particles.append(PressureParticle(
                x=x + random.uniform(-20, 20),
                y=y + random.uniform(-20, 20),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=random.uniform(0.8, 1.5),
                max_life=1.5,
                color=PressureUIColors.PRESSURE_RED,
                size=random.uniform(18, 28),
                rotation=random.uniform(-15, 15),
                rotation_speed=random.uniform(-2, 2),
                shape='exclaim',
                pulse=True
            ))

    def emit_stress_sparks(self, x: float, y: float, count: int = 15,
                          intensity: float = 1.0) -> None:
        """Emit stress sparks (for high stress moments)"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5) * intensity

            color = random.choice([
                PressureUIColors.PRESSURE_RED,
                PressureUIColors.URGENT_ORANGE,
                PressureUIColors.STRESS_PURPLE
            ])

            self.particles.append(PressureParticle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.4, 0.8),
                max_life=0.8,
                color=color,
                size=random.uniform(3, 6) * intensity,
                gravity=0.08,
                shape='spark'
            ))

    def emit_paper_scatter(self, x: float, y: float, count: int = 20) -> None:
        """Emit scattered paper particles (for collapse scene)"""
        paper_colors = [
            (245, 240, 230),  # White paper
            (235, 225, 210),  # Off-white
            (220, 215, 200),  # Gray-white
            (250, 235, 215),  # Cream
        ]

        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)

            self.particles.append(PressureParticle(
                x=x + random.uniform(-30, 30),
                y=y + random.uniform(-30, 30),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed + random.uniform(-1, 2),
                life=random.uniform(2.0, 4.0),
                max_life=4.0,
                color=random.choice(paper_colors),
                size=random.uniform(15, 30),
                gravity=0.06,
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-4, 4),
                shape='paper'
            ))

    def emit_countdown_numbers(self, x: float, y: float, count: int = 5) -> None:
        """Emit fading countdown numbers"""
        for i in range(count):
            if len(self.particles) >= self.max_particles:
                break

            self.particles.append(PressureParticle(
                x=x + random.uniform(-40, 40),
                y=y + random.uniform(-40, 40),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-1.5, -0.5),
                life=random.uniform(1.5, 2.5),
                max_life=2.5,
                color=PressureUIColors.TIME_GOLD,
                size=random.uniform(24, 36),
                rotation=random.randint(0, 9),  # Store number in rotation
                shape='number'
            ))

    def emit_conflict_pulse(self, x: float, y: float, color: Tuple[int, int, int] = None) -> None:
        """Emit expanding pulse ring (for conflict detection)"""
        if color is None:
            color = PressureUIColors.PRESSURE_RED

        self.pulse_rings.append(PulseRing(
            x=x,
            y=y,
            radius=0,
            max_radius=100,
            life=0.8,
            max_life=0.8,
            color=color,
            width=3
        ))

    def emit_overlap_warning(self, rect: pygame.Rect) -> None:
        """Emit warning particles for overlapping events"""
        for _ in range(5):
            if len(self.particles) >= self.max_particles:
                break

            x = random.uniform(rect.left, rect.right)
            y = random.uniform(rect.top, rect.bottom)

            self.particles.append(PressureParticle(
                x=x,
                y=y,
                vx=random.uniform(-0.3, 0.3),
                vy=random.uniform(-1, -0.3),
                life=random.uniform(0.8, 1.5),
                max_life=1.5,
                color=PressureUIColors.CONFLICT_MAGENTA,
                size=random.uniform(4, 8),
                shape='spark',
                pulse=True
            ))

        # Also emit a pulse ring
        self.emit_conflict_pulse(rect.centerx, rect.centery)

    def emit_drag_trail(self, x: float, y: float,
                        color: Tuple[int, int, int] = None) -> None:
        """Emit trail particles when dragging"""
        if len(self.particles) >= self.max_particles:
            return

        if color is None:
            color = PressureUIColors.CALM_BLUE

        self.particles.append(PressureParticle(
            x=x + random.uniform(-3, 3),
            y=y + random.uniform(-3, 3),
            vx=random.uniform(-0.2, 0.2),
            vy=random.uniform(0.2, 0.5),
            life=0.3,
            max_life=0.3,
            color=color,
            size=random.uniform(3, 6),
            shape='circle'
        ))

    def emit_selection_burst(self, x: float, y: float,
                            color: Tuple[int, int, int] = None) -> None:
        """Emit burst effect for selection"""
        if color is None:
            color = PressureUIColors.CALM_BLUE_LIGHT

        for _ in range(12):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)

            self.particles.append(PressureParticle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.4, 0.8),
                max_life=0.8,
                color=color,
                size=random.uniform(4, 8),
                gravity=0.05,
                shape='spark'
            ))

    def emit_urgent_notification(self, rect: pygame.Rect) -> None:
        """Emit urgent notification particles around a rect"""
        for edge in ['top', 'right', 'bottom', 'left']:
            for _ in range(3):
                if len(self.particles) >= self.max_particles:
                    break

                if edge == 'top':
                    x = random.uniform(rect.left, rect.right)
                    y = rect.top
                    vy = -random.uniform(0.5, 1.5)
                    vx = random.uniform(-0.3, 0.3)
                elif edge == 'bottom':
                    x = random.uniform(rect.left, rect.right)
                    y = rect.bottom
                    vy = random.uniform(0.5, 1.5)
                    vx = random.uniform(-0.3, 0.3)
                elif edge == 'left':
                    x = rect.left
                    y = random.uniform(rect.top, rect.bottom)
                    vx = -random.uniform(0.5, 1.5)
                    vy = random.uniform(-0.3, 0.3)
                else:
                    x = rect.right
                    y = random.uniform(rect.top, rect.bottom)
                    vx = random.uniform(0.5, 1.5)
                    vy = random.uniform(-0.3, 0.3)

                self.particles.append(PressureParticle(
                    x=x,
                    y=y,
                    vx=vx,
                    vy=vy,
                    life=random.uniform(0.5, 1.0),
                    max_life=1.0,
                    color=PressureUIColors.PRESSURE_RED_LIGHT,
                    size=random.uniform(3, 5),
                    shape='spark'
                ))


# Global instance for easy access
pressure_particles = PressureParticleSystem()

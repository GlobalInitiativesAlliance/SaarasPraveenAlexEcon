"""
Mentorship Particle Effects System
Floating dust motes, fog wisps, glow sparks, and dream particles
For Part 8 (Lack of Guidance/Mentorship) mini-games
"""
import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .mentorship_visual_base import DreamUIColors


@dataclass
class DreamParticle:
    """Individual dream particle with ethereal physics"""
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
    shape: str = 'circle'  # 'circle', 'star', 'orb', 'wisp', 'question'
    alpha: int = 255
    glow: bool = True
    drift: float = 0.0  # Horizontal drift for floating effect
    phase: float = 0.0  # For oscillation


@dataclass
class FogWisp:
    """Drifting fog wisp"""
    x: float
    y: float
    width: float
    height: float
    drift_speed: float
    life: float
    max_life: float
    alpha: int = 60


class DreamParticleSystem:
    """
    Particle system for dream/mentorship themed effects
    Includes floating motes, fog wisps, glow sparks, collapse effects
    """

    def __init__(self, max_particles: int = 300):
        self.particles: List[DreamParticle] = []
        self.fog_wisps: List[FogWisp] = []
        self.max_particles = max_particles
        self.ambient_enabled = False
        self.ambient_rect = None

    def update(self, dt: float) -> None:
        """Update all particles"""
        # Update dream particles
        for particle in self.particles[:]:
            particle.life -= dt
            if particle.life <= 0:
                self.particles.remove(particle)
                continue

            # Phase update for oscillation
            particle.phase += dt * 3

            # Ethereal physics - slower, floatier
            particle.x += particle.vx * dt * 60
            particle.y += particle.vy * dt * 60
            particle.vy += particle.gravity * dt * 60

            # Drift (horizontal wandering)
            if particle.drift != 0:
                particle.x += math.sin(particle.phase) * particle.drift * dt

            # Rotation
            particle.rotation += particle.rotation_speed * dt * 60

            # Fade out smoothly
            life_ratio = particle.life / particle.max_life
            # Smooth fade curve
            fade_curve = math.sin(life_ratio * math.pi / 2)
            particle.alpha = int(255 * fade_curve)

        # Update fog wisps
        for wisp in self.fog_wisps[:]:
            wisp.life -= dt
            if wisp.life <= 0:
                self.fog_wisps.remove(wisp)
                continue

            wisp.x += wisp.drift_speed * dt * 60
            life_ratio = wisp.life / wisp.max_life
            wisp.alpha = int(60 * life_ratio)

        # Generate ambient particles if enabled
        if self.ambient_enabled and self.ambient_rect:
            if random.random() < 0.1:  # 10% chance each frame
                self._emit_ambient_mote()

    def render(self, screen: pygame.Surface) -> None:
        """Render all particles"""
        # Render fog wisps first (background layer)
        for wisp in self.fog_wisps:
            if wisp.alpha <= 0:
                continue

            wisp_surface = pygame.Surface((int(wisp.width), int(wisp.height)), pygame.SRCALPHA)
            pygame.draw.ellipse(wisp_surface,
                              (*DreamUIColors.FOG_GRAY, wisp.alpha),
                              (0, 0, int(wisp.width), int(wisp.height)))
            screen.blit(wisp_surface, (int(wisp.x - wisp.width / 2),
                                       int(wisp.y - wisp.height / 2)))

        # Render particles
        for particle in self.particles:
            if particle.alpha <= 0:
                continue

            self._render_particle(screen, particle)

    def _render_particle(self, screen: pygame.Surface, particle: DreamParticle) -> None:
        """Render individual particle based on shape"""
        color_with_alpha = (*particle.color, particle.alpha)
        life_ratio = particle.life / particle.max_life
        size = max(1, int(particle.size * (0.5 + life_ratio * 0.5)))

        if particle.shape == 'circle':
            if particle.glow:
                # Glow effect
                glow_size = size + 6
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                for i in range(3, 0, -1):
                    glow_alpha = particle.alpha // (i + 1)
                    pygame.draw.circle(glow_surface,
                                     (*particle.color, glow_alpha),
                                     (glow_size, glow_size), size + i * 2)
                screen.blit(glow_surface,
                          (int(particle.x) - glow_size, int(particle.y) - glow_size))

            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (size, size), size)
            screen.blit(surf, (int(particle.x) - size, int(particle.y) - size))

        elif particle.shape == 'star':
            # Draw a simple star
            points = []
            for i in range(5):
                angle = particle.rotation + i * 72 - 90
                outer_x = particle.x + math.cos(math.radians(angle)) * size
                outer_y = particle.y + math.sin(math.radians(angle)) * size
                points.append((outer_x, outer_y))

                inner_angle = angle + 36
                inner_x = particle.x + math.cos(math.radians(inner_angle)) * size * 0.4
                inner_y = particle.y + math.sin(math.radians(inner_angle)) * size * 0.4
                points.append((inner_x, inner_y))

            if len(points) >= 3:
                surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                offset_points = [(p[0] - particle.x + size * 1.5, p[1] - particle.y + size * 1.5)
                               for p in points]
                try:
                    pygame.draw.polygon(surf, color_with_alpha, offset_points)
                except:
                    pass
                screen.blit(surf, (int(particle.x - size * 1.5), int(particle.y - size * 1.5)))

        elif particle.shape == 'orb':
            # Glowing orb with highlight
            orb_size = size * 2
            orb_surface = pygame.Surface((orb_size, orb_size), pygame.SRCALPHA)

            # Glow layers
            for i in range(4, 0, -1):
                glow_alpha = particle.alpha // (i + 1)
                pygame.draw.circle(orb_surface, (*particle.color, glow_alpha),
                                 (orb_size // 2, orb_size // 2), size // 2 + i * 3)

            # Main orb
            pygame.draw.circle(orb_surface, color_with_alpha,
                             (orb_size // 2, orb_size // 2), size // 2)

            # Highlight
            highlight_alpha = min(particle.alpha, 150)
            pygame.draw.circle(orb_surface, (*DreamUIColors.STARLIGHT, highlight_alpha),
                             (orb_size // 2 - size // 6, orb_size // 2 - size // 6), size // 5)

            screen.blit(orb_surface, (int(particle.x - orb_size // 2),
                                      int(particle.y - orb_size // 2)))

        elif particle.shape == 'wisp':
            # Elongated wisp particle
            wisp_width = int(size * 2)
            wisp_height = int(size * 0.6)
            wisp_surface = pygame.Surface((wisp_width, wisp_height), pygame.SRCALPHA)
            pygame.draw.ellipse(wisp_surface, color_with_alpha,
                              (0, 0, wisp_width, wisp_height))
            rotated = pygame.transform.rotate(wisp_surface, particle.rotation)
            screen.blit(rotated, (int(particle.x - rotated.get_width() // 2),
                                  int(particle.y - rotated.get_height() // 2)))

        elif particle.shape == 'question':
            # Question mark particle (for uncertainty)
            try:
                font = pygame.font.SysFont('Georgia', max(12, int(size)))
            except:
                font = pygame.font.Font(None, max(12, int(size)))

            text_surface = font.render('?', True, color_with_alpha[:3])
            text_surface.set_alpha(particle.alpha)
            rotated = pygame.transform.rotate(text_surface, particle.rotation)
            screen.blit(rotated, (int(particle.x - rotated.get_width() // 2),
                                  int(particle.y - rotated.get_height() // 2)))

    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
        self.fog_wisps.clear()

    def enable_ambient(self, rect: pygame.Rect) -> None:
        """Enable ambient floating particles in an area"""
        self.ambient_enabled = True
        self.ambient_rect = rect

    def disable_ambient(self) -> None:
        """Disable ambient particles"""
        self.ambient_enabled = False

    def _emit_ambient_mote(self) -> None:
        """Emit a single ambient dust mote"""
        if not self.ambient_rect or len(self.particles) >= self.max_particles:
            return

        self.particles.append(DreamParticle(
            x=random.uniform(self.ambient_rect.left, self.ambient_rect.right),
            y=random.uniform(self.ambient_rect.top, self.ambient_rect.bottom),
            vx=random.uniform(-0.2, 0.2),
            vy=random.uniform(-0.3, 0.1),
            life=random.uniform(3.0, 6.0),
            max_life=6.0,
            color=random.choice([
                DreamUIColors.STARLIGHT_DIM,
                DreamUIColors.GLOW_CYAN,
                DreamUIColors.FOG_LIGHT
            ]),
            size=random.uniform(2, 5),
            gravity=-0.002,  # Float upward
            drift=random.uniform(0.3, 0.8),
            shape='circle',
            glow=True
        ))

    # ==================== Emission Functions ====================

    def emit_dust_motes(self, rect: pygame.Rect, count: int = 20) -> None:
        """Emit floating dust motes in an area"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            self.particles.append(DreamParticle(
                x=random.uniform(rect.left, rect.right),
                y=random.uniform(rect.top, rect.bottom),
                vx=random.uniform(-0.3, 0.3),
                vy=random.uniform(-0.5, 0.2),
                life=random.uniform(4.0, 8.0),
                max_life=8.0,
                color=random.choice([
                    DreamUIColors.STARLIGHT_DIM,
                    DreamUIColors.GLOW_CYAN,
                    DreamUIColors.FOG_LIGHT
                ]),
                size=random.uniform(2, 6),
                gravity=-0.003,
                drift=random.uniform(0.2, 0.6),
                shape='circle',
                glow=True
            ))

    def emit_fog_wisps(self, rect: pygame.Rect, count: int = 8) -> None:
        """Emit drifting fog wisps"""
        for _ in range(count):
            self.fog_wisps.append(FogWisp(
                x=random.uniform(rect.left - 50, rect.right),
                y=random.uniform(rect.top, rect.bottom),
                width=random.uniform(60, 120),
                height=random.uniform(20, 40),
                drift_speed=random.uniform(0.3, 0.8),
                life=random.uniform(4.0, 8.0),
                max_life=8.0,
                alpha=random.randint(30, 70)
            ))

    def emit_glow_sparks(self, x: float, y: float, count: int = 15,
                         color: Tuple[int, int, int] = None) -> None:
        """Emit glowing sparks (for selection/activation)"""
        if color is None:
            color = DreamUIColors.GLOW_CYAN

        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)

            self.particles.append(DreamParticle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=random.uniform(0.5, 1.2),
                max_life=1.2,
                color=color,
                size=random.uniform(3, 7),
                gravity=0.05,
                shape='orb',
                glow=True
            ))

    def emit_star_burst(self, x: float, y: float, count: int = 12) -> None:
        """Emit star particles (for door reveals)"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)

            self.particles.append(DreamParticle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.8, 1.5),
                max_life=1.5,
                color=random.choice([
                    DreamUIColors.STARLIGHT,
                    DreamUIColors.GLOW_GOLD,
                    DreamUIColors.GLOW_CYAN
                ]),
                size=random.uniform(8, 15),
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-3, 3),
                shape='star',
                glow=True
            ))

    def emit_collapse_particles(self, x: float, y: float, count: int = 25) -> None:
        """Emit particles for balance collapse effect"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)

            self.particles.append(DreamParticle(
                x=x + random.uniform(-50, 50),
                y=y + random.uniform(-30, 30),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed + random.uniform(-1, 2),
                life=random.uniform(1.0, 2.5),
                max_life=2.5,
                color=random.choice([
                    DreamUIColors.COLLAPSE_RED,
                    DreamUIColors.UNCERTAIN_AMBER,
                    DreamUIColors.FOG_DARK
                ]),
                size=random.uniform(5, 12),
                gravity=0.08,
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-5, 5),
                shape='wisp'
            ))

    def emit_question_marks(self, rect: pygame.Rect, count: int = 8) -> None:
        """Emit floating question mark particles (for uncertainty)"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            self.particles.append(DreamParticle(
                x=random.uniform(rect.left, rect.right),
                y=random.uniform(rect.top, rect.bottom),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-1, -0.3),
                life=random.uniform(2.0, 4.0),
                max_life=4.0,
                color=DreamUIColors.TEXT_DIM,
                size=random.uniform(16, 24),
                gravity=-0.005,
                rotation=random.uniform(-15, 15),
                rotation_speed=random.uniform(-1, 1),
                drift=random.uniform(0.3, 0.7),
                shape='question'
            ))

    def emit_drag_trail(self, x: float, y: float,
                        color: Tuple[int, int, int] = None) -> None:
        """Emit trail particles when dragging"""
        if len(self.particles) >= self.max_particles:
            return

        if color is None:
            color = DreamUIColors.GLOW_CYAN

        self.particles.append(DreamParticle(
            x=x + random.uniform(-5, 5),
            y=y + random.uniform(-5, 5),
            vx=random.uniform(-0.3, 0.3),
            vy=random.uniform(0, 0.5),
            life=0.4,
            max_life=0.4,
            color=color,
            size=random.uniform(4, 8),
            shape='circle',
            glow=True
        ))

    def emit_mentor_glow(self, x: float, y: float) -> None:
        """Emit special golden glow effect for finding mentor"""
        # Bright central burst
        for _ in range(20):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)

            self.particles.append(DreamParticle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(1.0, 2.0),
                max_life=2.0,
                color=DreamUIColors.GLOW_GOLD_BRIGHT,
                size=random.uniform(5, 12),
                gravity=-0.02,
                shape='orb',
                glow=True
            ))

        # Surrounding stars
        for _ in range(8):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(30, 80)

            self.particles.append(DreamParticle(
                x=x + math.cos(angle) * dist,
                y=y + math.sin(angle) * dist,
                vx=math.cos(angle) * 0.5,
                vy=math.sin(angle) * 0.5,
                life=1.5,
                max_life=1.5,
                color=DreamUIColors.STARLIGHT,
                size=random.uniform(12, 18),
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-2, 2),
                shape='star',
                glow=True
            ))

    def emit_scatter_to_fog(self, items: List[Tuple[float, float]]) -> None:
        """Emit particles for items scattering into fog (priority puzzle)"""
        for x, y in items:
            for _ in range(5):
                if len(self.particles) >= self.max_particles:
                    break

                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)

                self.particles.append(DreamParticle(
                    x=x + random.uniform(-20, 20),
                    y=y + random.uniform(-20, 20),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=random.uniform(1.5, 3.0),
                    max_life=3.0,
                    color=DreamUIColors.FOG_GRAY,
                    size=random.uniform(15, 25),
                    gravity=0.02,
                    shape='wisp',
                    glow=False
                ))

    def emit_light_burst(self, x: float, y: float, color: Tuple[int, int, int] = None) -> None:
        """Emit a bright light burst (door selection)"""
        if color is None:
            color = DreamUIColors.STARLIGHT

        # Central flash
        for _ in range(15):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 12)

            self.particles.append(DreamParticle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.3, 0.7),
                max_life=0.7,
                color=color,
                size=random.uniform(8, 16),
                shape='circle',
                glow=True
            ))

    def emit_success_sparkle(self, x: float, y: float, count: int = 12) -> None:
        """Emit success sparkle effect (rare in this part!)"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)

            self.particles.append(DreamParticle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=1.2,
                max_life=1.2,
                color=DreamUIColors.SUCCESS_GREEN,
                size=random.uniform(6, 10),
                gravity=0.06,
                shape='star',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-2, 2),
                glow=True
            ))


# Global instance for easy access
dream_particles = DreamParticleSystem()

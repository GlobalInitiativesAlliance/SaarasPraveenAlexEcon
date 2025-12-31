"""
Systemic Barriers Particle Effects System
Paper scatter, error sparks, glitch effects, and frustration indicators
For Part 5 (Systemic and Structural Barriers) mini-games
"""
import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

from .systemic_visual_base import SystemicUIColors


@dataclass
class Particle:
    """Individual particle with physics"""
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
    shape: str = 'circle'  # 'circle', 'square', 'line', 'paper'
    alpha: int = 255


@dataclass
class GlitchLine:
    """Screen glitch line effect"""
    y: float
    height: int
    offset: int
    life: float
    max_life: float


class SystemicParticleSystem:
    """
    Particle system for systemic barriers themed effects
    Includes paper scatter, error sparks, glitch effects
    """

    def __init__(self, max_particles: int = 200):
        self.particles: List[Particle] = []
        self.glitch_lines: List[GlitchLine] = []
        self.max_particles = max_particles
        self.screen_shake = 0.0
        self.shake_intensity = 0

    def update(self, dt: float) -> None:
        """Update all particles"""
        # Update regular particles
        for particle in self.particles[:]:
            particle.life -= dt
            if particle.life <= 0:
                self.particles.remove(particle)
                continue

            # Physics
            particle.x += particle.vx * dt * 60
            particle.y += particle.vy * dt * 60
            particle.vy += particle.gravity * dt * 60
            particle.rotation += particle.rotation_speed * dt * 60

            # Fade out
            life_ratio = particle.life / particle.max_life
            particle.alpha = int(255 * life_ratio)

        # Update glitch lines
        for glitch in self.glitch_lines[:]:
            glitch.life -= dt
            if glitch.life <= 0:
                self.glitch_lines.remove(glitch)

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 3)

    def render(self, screen: pygame.Surface) -> Tuple[int, int]:
        """Render all particles, return screen shake offset"""
        # Calculate shake offset
        shake_x = 0
        shake_y = 0
        if self.screen_shake > 0:
            shake_x = int(random.uniform(-self.shake_intensity, self.shake_intensity) * self.screen_shake)
            shake_y = int(random.uniform(-self.shake_intensity, self.shake_intensity) * self.screen_shake)

        # Render particles
        for particle in self.particles:
            if particle.alpha <= 0:
                continue

            color_with_alpha = (*particle.color, particle.alpha)
            size = int(particle.size * (particle.life / particle.max_life + 0.5))

            if particle.shape == 'circle':
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color_with_alpha, (size, size), size)
                screen.blit(surf, (int(particle.x) - size, int(particle.y) - size))

            elif particle.shape == 'square':
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                surf.fill(color_with_alpha)
                if particle.rotation != 0:
                    surf = pygame.transform.rotate(surf, particle.rotation)
                screen.blit(surf, (int(particle.x) - size // 2, int(particle.y) - size // 2))

            elif particle.shape == 'paper':
                # Paper piece effect
                width = int(size * 1.5)
                height = int(size * 0.8)
                surf = pygame.Surface((width, height), pygame.SRCALPHA)
                surf.fill((*SystemicUIColors.FORM_CREAM, particle.alpha))
                pygame.draw.rect(surf, (*SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT, particle.alpha),
                               (0, 0, width, height), 1)
                rotated = pygame.transform.rotate(surf, particle.rotation)
                screen.blit(rotated, (int(particle.x) - rotated.get_width() // 2,
                                     int(particle.y) - rotated.get_height() // 2))

            elif particle.shape == 'line':
                # Spark/error line
                end_x = particle.x + math.cos(math.radians(particle.rotation)) * size
                end_y = particle.y + math.sin(math.radians(particle.rotation)) * size
                surf = pygame.Surface((abs(int(end_x - particle.x)) + 4,
                                       abs(int(end_y - particle.y)) + 4), pygame.SRCALPHA)
                pygame.draw.line(screen, color_with_alpha,
                               (int(particle.x), int(particle.y)),
                               (int(end_x), int(end_y)), 2)

        # Render glitch lines
        for glitch in self.glitch_lines:
            alpha = int(255 * (glitch.life / glitch.max_life))
            surf = pygame.Surface((screen.get_width(), glitch.height), pygame.SRCALPHA)

            # Copy and shift a horizontal strip
            glitch_color = random.choice([
                (255, 50, 50, alpha),
                (50, 255, 50, alpha),
                (50, 50, 255, alpha),
                (255, 255, 255, alpha)
            ])
            surf.fill(glitch_color)
            screen.blit(surf, (glitch.offset, int(glitch.y)))

        return shake_x, shake_y

    def clear(self) -> None:
        """Clear all particles"""
        self.particles.clear()
        self.glitch_lines.clear()
        self.screen_shake = 0

    # ==================== Emission Functions ====================

    def emit_paper_scatter(self, x: float, y: float, count: int = 15) -> None:
        """Emit paper pieces flying out (document rejection)"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)

            self.particles.append(Particle(
                x=x + random.uniform(-20, 20),
                y=y + random.uniform(-20, 20),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                life=random.uniform(1.0, 2.0),
                max_life=2.0,
                color=SystemicUIColors.FORM_CREAM,
                size=random.uniform(10, 20),
                gravity=0.15,
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-10, 10),
                shape='paper'
            ))

    def emit_stamp_impact(self, x: float, y: float, color: Tuple[int, int, int] = None) -> None:
        """Emit particles when stamp hits paper"""
        if color is None:
            color = SystemicUIColors.STAMP_RED

        # Impact dust
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)

            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=0.5,
                max_life=0.5,
                color=color,
                size=random.uniform(3, 6),
                gravity=0.05,
                shape='circle'
            ))

        # Add screen shake
        self.screen_shake = 1.0
        self.shake_intensity = 5

    def emit_error_sparks(self, x: float, y: float, count: int = 20) -> None:
        """Emit error/crash sparks"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 10)

            color = random.choice([
                SystemicUIColors.ERROR_RED,
                SystemicUIColors.WARNING_ORANGE,
                (255, 200, 100),  # Yellow spark
                (255, 255, 255),  # White spark
            ])

            self.particles.append(Particle(
                x=x + random.uniform(-30, 30),
                y=y + random.uniform(-30, 30),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.3, 0.8),
                max_life=0.8,
                color=color,
                size=random.uniform(2, 5),
                gravity=0.1,
                rotation=random.uniform(0, 360),
                shape='line'
            ))

    def emit_glitch_effect(self, screen_height: int, intensity: int = 5) -> None:
        """Emit screen glitch lines"""
        for _ in range(intensity):
            self.glitch_lines.append(GlitchLine(
                y=random.uniform(0, screen_height),
                height=random.randint(2, 8),
                offset=random.randint(-20, 20),
                life=random.uniform(0.05, 0.15),
                max_life=0.15
            ))

        # Add screen shake for dramatic effect
        self.screen_shake = 0.5
        self.shake_intensity = 8

    def emit_static(self, rect: pygame.Rect, density: int = 50) -> None:
        """Emit TV static particles within a rect"""
        for _ in range(density):
            gray = random.randint(100, 255)
            self.particles.append(Particle(
                x=random.uniform(rect.x, rect.right),
                y=random.uniform(rect.y, rect.bottom),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1, 1),
                life=0.1,
                max_life=0.1,
                color=(gray, gray, gray),
                size=random.uniform(1, 3),
                shape='square'
            ))

    def emit_disconnect(self, x: float, y: float) -> None:
        """Emit particles for phone disconnect"""
        # Fading signal bars
        for i in range(4):
            self.particles.append(Particle(
                x=x + i * 10,
                y=y,
                vx=0,
                vy=-1,
                life=1.0,
                max_life=1.0,
                color=SystemicUIColors.ERROR_RED,
                size=6 + i * 2,
                gravity=0,
                shape='square'
            ))

        self.screen_shake = 0.3
        self.shake_intensity = 3

    def emit_frustration(self, x: float, y: float, intensity: float = 1.0) -> None:
        """Emit frustration indicator particles (steam/heat waves)"""
        count = int(5 * intensity)
        for _ in range(count):
            self.particles.append(Particle(
                x=x + random.uniform(-30, 30),
                y=y,
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-2, -4),
                life=random.uniform(0.8, 1.5),
                max_life=1.5,
                color=SystemicUIColors.WARNING_ORANGE,
                size=random.uniform(4, 8),
                gravity=-0.02,  # Float up
                shape='circle'
            ))

    def emit_success(self, x: float, y: float, count: int = 15) -> None:
        """Emit success particles (rare in systemic barriers!)"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)

            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=1.0,
                max_life=1.0,
                color=SystemicUIColors.APPROVAL_GREEN,
                size=random.uniform(4, 8),
                gravity=0.08,
                shape='circle'
            ))

    def emit_typing_cursor(self, x: float, y: float) -> None:
        """Emit subtle particles at typing cursor position"""
        self.particles.append(Particle(
            x=x,
            y=y,
            vx=random.uniform(-0.5, 0.5),
            vy=random.uniform(-1, 0),
            life=0.3,
            max_life=0.3,
            color=SystemicUIColors.GOVERNMENT_BLUE_LIGHT,
            size=2,
            shape='circle'
        ))

    def emit_loading_spinner(self, center: Tuple[int, int], radius: int,
                            angle: float, count: int = 3) -> None:
        """Emit particles along a loading spinner path"""
        for i in range(count):
            particle_angle = angle - i * 0.2
            x = center[0] + math.cos(particle_angle) * radius
            y = center[1] + math.sin(particle_angle) * radius

            self.particles.append(Particle(
                x=x,
                y=y,
                vx=0,
                vy=0,
                life=0.3,
                max_life=0.3,
                color=SystemicUIColors.GOVERNMENT_BLUE_LIGHT,
                size=4 - i,
                shape='circle'
            ))

    def trigger_crash_effect(self, screen_width: int, screen_height: int) -> None:
        """Trigger full crash visual effect"""
        # Multiple glitch waves
        for _ in range(3):
            self.emit_glitch_effect(screen_height, intensity=8)

        # Error sparks from center
        self.emit_error_sparks(screen_width // 2, screen_height // 2, 30)

        # Heavy screen shake
        self.screen_shake = 1.0
        self.shake_intensity = 15

    def trigger_rejection_effect(self, x: float, y: float) -> None:
        """Trigger rejection stamp effect"""
        self.emit_stamp_impact(x, y, SystemicUIColors.STAMP_RED)
        self.emit_paper_scatter(x, y, 10)


# Global instance for easy access
systemic_particles = SystemicParticleSystem()

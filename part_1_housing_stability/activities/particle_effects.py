"""
Particle Effects System for Part 1 Housing Stability
Provides visual feedback through animated particles
Themed for housing/packing/documents scenarios
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Particle:
    """Individual particle with physics"""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    life: float = 1.0
    max_life: float = 1.0
    size: float = 5.0
    color: Tuple[int, int, int] = (255, 255, 255)
    gravity: float = 0.0
    friction: float = 0.98
    fade: bool = True
    shrink: bool = True
    shape: str = 'circle'  # 'circle', 'square', 'star', 'line'
    rotation: float = 0.0
    rotation_speed: float = 0.0


class Part1ParticleSystem:
    """
    Manages particles for Part 1 Housing Stability
    Themed for packing, documents, and emotional moments
    """

    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 500

    def update(self, dt: float) -> None:
        """Update all particles with physics"""
        for particle in self.particles[:]:
            # Update life
            particle.life -= dt / particle.max_life
            if particle.life <= 0:
                self.particles.remove(particle)
                continue

            # Apply physics
            particle.vy += particle.gravity * dt * 60
            particle.vx *= particle.friction
            particle.vy *= particle.friction

            # Update position
            particle.x += particle.vx * dt * 60
            particle.y += particle.vy * dt * 60

            # Update rotation
            particle.rotation += particle.rotation_speed * dt * 60

    def render(self, screen: pygame.Surface) -> None:
        """Render all active particles"""
        for particle in self.particles:
            alpha = int(255 * particle.life) if particle.fade else 255
            size = max(1, particle.size * particle.life) if particle.shrink else particle.size
            color = (*particle.color[:3], alpha)

            if particle.shape == 'circle':
                self._draw_circle(screen, particle, size, color)
            elif particle.shape == 'square':
                self._draw_square(screen, particle, size, color)
            elif particle.shape == 'star':
                self._draw_star(screen, particle, size, color)
            elif particle.shape == 'line':
                self._draw_line(screen, particle, size, color)

    def _draw_circle(self, screen: pygame.Surface, particle: Particle,
                    size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a circular particle"""
        surface = pygame.Surface((int(size * 2 + 2), int(size * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (int(size + 1), int(size + 1)), int(size))
        screen.blit(surface, (int(particle.x - size), int(particle.y - size)))

    def _draw_square(self, screen: pygame.Surface, particle: Particle,
                    size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a square particle with rotation"""
        surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, int(size * 2), int(size * 2)))
        rotated = pygame.transform.rotate(surface, particle.rotation)
        rect = rotated.get_rect(center=(int(particle.x), int(particle.y)))
        screen.blit(rotated, rect)

    def _draw_star(self, screen: pygame.Surface, particle: Particle,
                  size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a star particle"""
        points = []
        for i in range(5):
            angle = particle.rotation + (i * 72 - 90) * math.pi / 180
            points.append((
                particle.x + size * math.cos(angle),
                particle.y + size * math.sin(angle)
            ))
            angle = particle.rotation + (i * 72 + 36 - 90) * math.pi / 180
            points.append((
                particle.x + size * 0.4 * math.cos(angle),
                particle.y + size * 0.4 * math.sin(angle)
            ))

        if len(points) >= 3:
            surface = pygame.Surface((int(size * 3), int(size * 3)), pygame.SRCALPHA)
            adjusted_points = [(p[0] - particle.x + size * 1.5,
                               p[1] - particle.y + size * 1.5) for p in points]
            pygame.draw.polygon(surface, color, adjusted_points)
            screen.blit(surface, (int(particle.x - size * 1.5), int(particle.y - size * 1.5)))

    def _draw_line(self, screen: pygame.Surface, particle: Particle,
                  size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a line particle"""
        angle = particle.rotation
        dx = math.cos(angle) * size
        dy = math.sin(angle) * size
        surface = pygame.Surface((int(size * 3), int(size * 3)), pygame.SRCALPHA)
        pygame.draw.line(surface, color,
                        (size * 1.5, size * 1.5),
                        (size * 1.5 + dx, size * 1.5 + dy), 2)
        screen.blit(surface, (int(particle.x - size * 1.5), int(particle.y - size * 1.5)))

    def clear(self) -> None:
        """Remove all particles"""
        self.particles.clear()

    # ==================== Housing-Themed Emitters ====================

    def emit_success(self, x: float, y: float, count: int = 15) -> None:
        """Emit warm success particles (housing green)"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x=x + random.randint(-5, 5),
                y=y + random.randint(-5, 5),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(4, 8),
                color=(134, 168, 133),  # Soft green (housing theme)
                gravity=0.15,
                friction=0.95,
                shape='circle'
            ))

    def emit_error(self, x: float, y: float, count: int = 10) -> None:
        """Emit subtle error particles"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append(Particle(
                x=x + random.randint(-3, 3),
                y=y + random.randint(-3, 3),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(0.4, 0.7),
                size=random.uniform(3, 6),
                color=(180, 90, 90),  # Soft red
                gravity=0.1,
                friction=0.92,
                shape='square',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-10, 10)
            ))

    def emit_packing(self, x: float, y: float, count: int = 12) -> None:
        """Emit particles when packing an item (clothes/belongings)"""
        if len(self.particles) >= self.max_particles:
            return

        # Fabric-like particles
        fabric_colors = [
            (101, 128, 156),  # Blue denim
            (180, 160, 140),  # Beige
            (130, 110, 100),  # Brown
            (160, 160, 170),  # Grey
        ]

        for _ in range(count):
            angle = random.uniform(-math.pi, 0)  # Upward arc
            speed = random.uniform(2, 4)
            self.particles.append(Particle(
                x=x + random.randint(-10, 10),
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=1.0,
                max_life=random.uniform(0.5, 0.8),
                size=random.uniform(4, 8),
                color=random.choice(fabric_colors),
                gravity=0.2,
                friction=0.94,
                shape='square',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-8, 8)
            ))

    def emit_document_found(self, x: float, y: float, count: int = 15) -> None:
        """Emit sparkles when finding an important document"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x=x + random.randint(-15, 15),
                y=y + random.randint(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(5, 10),
                color=(255, 230, 150),  # Golden/document color
                gravity=0.05,
                friction=0.96,
                shape='star',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-15, 15)
            ))

    def emit_paper_flutter(self, x: float, y: float, count: int = 8) -> None:
        """Emit paper-like particles (for documents/papers)"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            self.particles.append(Particle(
                x=x + random.randint(-15, 15),
                y=y + random.randint(-10, 10),
                vx=random.uniform(-2, 2),
                vy=random.uniform(0.5, 2),
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(4, 8),
                color=(250, 248, 240),  # Paper white
                gravity=0.08,
                friction=0.92,
                shape='square',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-10, 10)
            ))

    def emit_memory_sparkle(self, x: float, y: float, count: int = 20) -> None:
        """Emit nostalgic/memory particles (for photos/mementos)"""
        if len(self.particles) >= self.max_particles:
            return

        memory_colors = [
            (255, 220, 180),  # Warm sepia
            (240, 200, 160),  # Golden memory
            (220, 190, 170),  # Faded pink
            (200, 180, 160),  # Vintage brown
        ]

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2)
            self.particles.append(Particle(
                x=x + random.randint(-30, 30),
                y=y + random.randint(-20, 20),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 0.5,
                life=1.0,
                max_life=random.uniform(1.0, 1.8),
                size=random.uniform(3, 7),
                color=random.choice(memory_colors),
                gravity=-0.02,  # Float upward
                friction=0.98,
                shape='star',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-5, 5)
            ))

    def emit_door_exit(self, x: float, y: float, count: int = 25) -> None:
        """Emit particles when exiting through a door (leaving foster home)"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            # Outward burst from door
            angle = random.uniform(-0.5, 0.5)  # Mostly forward
            speed = random.uniform(3, 7)
            self.particles.append(Particle(
                x=x + random.randint(-5, 5),
                y=y + random.randint(-20, 20),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(4, 8),
                color=(180, 170, 160),  # Neutral grey
                gravity=0.1,
                friction=0.93,
                shape='circle'
            ))

    def emit_achievement(self, x: float, y: float, count: int = 40) -> None:
        """Emit celebration particles for achievements"""
        if len(self.particles) >= self.max_particles:
            return

        colors = [
            (134, 168, 133),  # Green
            (101, 128, 156),  # Blue
            (200, 170, 120),  # Gold
            (180, 140, 160),  # Mauve
            (255, 255, 255),  # White
        ]

        for _ in range(count):
            angle = random.uniform(-math.pi, 0)  # Upward
            speed = random.uniform(5, 10)
            self.particles.append(Particle(
                x=x + random.randint(-30, 30),
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 4,
                life=1.0,
                max_life=random.uniform(1.2, 2.0),
                size=random.uniform(5, 12),
                color=random.choice(colors),
                gravity=0.2,
                friction=0.97,
                shape=random.choice(['circle', 'square', 'star']),
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-12, 12)
            ))

    def emit_stress(self, x: float, y: float, count: int = 8) -> None:
        """Emit stress/anxiety particles"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 2)
            self.particles.append(Particle(
                x=x + math.cos(angle) * 20,
                y=y + math.sin(angle) * 20,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=0.4,
                size=random.uniform(2, 4),
                color=(200, 100, 100),  # Anxious red
                gravity=0,
                friction=0.95,
                shape='circle'
            ))

    def emit_coin_collect(self, x: float, y: float, count: int = 10) -> None:
        """Emit particles when collecting money/resources"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 4)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,
                life=1.0,
                max_life=random.uniform(0.5, 0.8),
                size=random.uniform(4, 8),
                color=(218, 190, 130),  # Gold coin
                gravity=0.15,
                friction=0.94,
                shape='circle'
            ))


# Global instance for easy access
part1_particles = Part1ParticleSystem()

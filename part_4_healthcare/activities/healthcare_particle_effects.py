"""
Particle Effects System for Healthcare Mini-Games
Provides visual feedback through animated particles
Includes healthcare-specific effects (pills, heartbeat, breath)
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
    shape: str = 'circle'  # 'circle', 'square', 'star', 'line', 'pill', 'heart'
    rotation: float = 0.0
    rotation_speed: float = 0.0


class HealthcareParticleSystem:
    """
    Manages multiple particle emitters and particles
    Used for celebrations, feedback, and visual effects
    """

    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 500  # Performance limit

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
            # Calculate alpha based on life
            alpha = int(255 * particle.life) if particle.fade else 255

            # Calculate size based on life
            size = particle.size
            if particle.shrink:
                size = max(1, particle.size * particle.life)

            # Create color with alpha
            color = (*particle.color[:3], alpha)

            # Draw based on shape
            if particle.shape == 'circle':
                self._draw_circle(screen, particle, size, color)
            elif particle.shape == 'square':
                self._draw_square(screen, particle, size, color)
            elif particle.shape == 'star':
                self._draw_star(screen, particle, size, color)
            elif particle.shape == 'line':
                self._draw_line(screen, particle, size, color)
            elif particle.shape == 'pill':
                self._draw_pill(screen, particle, size, color)
            elif particle.shape == 'heart':
                self._draw_heart(screen, particle, size, color)

    def draw(self, screen: pygame.Surface) -> None:
        """Alias for render - draw all active particles"""
        self.render(screen)

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

        # Rotate
        rotated = pygame.transform.rotate(surface, particle.rotation)
        rect = rotated.get_rect(center=(int(particle.x), int(particle.y)))
        screen.blit(rotated, rect)

    def _draw_star(self, screen: pygame.Surface, particle: Particle,
                  size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a star particle"""
        points = []
        for i in range(5):
            # Outer point
            angle = particle.rotation + (i * 72 - 90) * math.pi / 180
            points.append((
                particle.x + size * math.cos(angle),
                particle.y + size * math.sin(angle)
            ))
            # Inner point
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
        """Draw a line particle (for trails)"""
        angle = particle.rotation
        dx = math.cos(angle) * size
        dy = math.sin(angle) * size

        surface = pygame.Surface((int(size * 3), int(size * 3)), pygame.SRCALPHA)
        pygame.draw.line(surface, color,
                        (size * 1.5, size * 1.5),
                        (size * 1.5 + dx, size * 1.5 + dy), 2)
        screen.blit(surface, (int(particle.x - size * 1.5), int(particle.y - size * 1.5)))

    def _draw_pill(self, screen: pygame.Surface, particle: Particle,
                  size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a pill-shaped particle (capsule)"""
        width = int(size * 2)
        height = int(size)
        surface = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)

        # Draw capsule shape (rounded rectangle)
        pygame.draw.rect(surface, color, (2, 2, width, height), border_radius=height // 2)

        # Rotate
        rotated = pygame.transform.rotate(surface, particle.rotation)
        rect = rotated.get_rect(center=(int(particle.x), int(particle.y)))
        screen.blit(rotated, rect)

    def _draw_heart(self, screen: pygame.Surface, particle: Particle,
                   size: float, color: Tuple[int, int, int, int]) -> None:
        """Draw a heart-shaped particle"""
        surface = pygame.Surface((int(size * 3), int(size * 3)), pygame.SRCALPHA)
        center = size * 1.5

        # Simple heart using circles and triangle
        radius = size * 0.4
        # Left bump
        pygame.draw.circle(surface, color,
                          (int(center - radius * 0.5), int(center - radius * 0.3)),
                          int(radius))
        # Right bump
        pygame.draw.circle(surface, color,
                          (int(center + radius * 0.5), int(center - radius * 0.3)),
                          int(radius))
        # Bottom point
        points = [
            (center - radius, center),
            (center + radius, center),
            (center, center + radius * 1.5)
        ]
        pygame.draw.polygon(surface, color, points)

        screen.blit(surface, (int(particle.x - size * 1.5), int(particle.y - size * 1.5)))

    def clear(self) -> None:
        """Remove all particles"""
        self.particles.clear()

    # ==================== Emitter Functions ====================

    def emit_success(self, x: float, y: float, count: int = 15) -> None:
        """Emit green success particles (checkmark burst)"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x=x + random.randint(-5, 5),
                y=y + random.randint(-5, 5),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,  # Slight upward bias
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(4, 8),
                color=(46, 204, 113),  # Healthcare green
                gravity=0.15,
                friction=0.95,
                shape='circle'
            ))

    def emit_error(self, x: float, y: float, count: int = 10) -> None:
        """Emit red error particles (subtle X pattern)"""
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
                color=(231, 76, 60),  # Healthcare red
                gravity=0.1,
                friction=0.92,
                shape='square',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-10, 10)
            ))

    def emit_confetti(self, x: float, y: float, count: int = 50,
                     colors: Optional[List[Tuple[int, int, int]]] = None) -> None:
        """Emit colorful confetti burst for celebrations"""
        if len(self.particles) >= self.max_particles:
            return

        if colors is None:
            colors = [
                (41, 128, 185),   # Medical blue
                (39, 174, 96),    # Health green
                (243, 156, 18),   # Warning orange
                (155, 89, 182),   # Purple
                (231, 76, 60),    # Red
                (255, 255, 255),  # White
            ]

        for _ in range(count):
            angle = random.uniform(-math.pi, 0)  # Upward spread
            speed = random.uniform(5, 12)
            self.particles.append(Particle(
                x=x + random.randint(-20, 20),
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 5,  # Strong upward
                life=1.0,
                max_life=random.uniform(1.5, 2.5),
                size=random.uniform(4, 10),
                color=random.choice(colors),
                gravity=0.25,
                friction=0.98,
                shape=random.choice(['square', 'circle']),
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-15, 15)
            ))

    def emit_paper_trail(self, x: float, y: float, count: int = 5) -> None:
        """Emit paper-like particles for document/mail movement"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            self.particles.append(Particle(
                x=x + random.randint(-10, 10),
                y=y + random.randint(-5, 5),
                vx=random.uniform(-1, 1),
                vy=random.uniform(0, 2),
                life=1.0,
                max_life=random.uniform(0.3, 0.6),
                size=random.uniform(3, 6),
                color=(253, 254, 254),  # Paper color
                gravity=0.05,
                friction=0.9,
                shape='square',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-5, 5)
            ))

    def emit_glow(self, x: float, y: float, color: Tuple[int, int, int],
                 radius: int = 30, count: int = 20) -> None:
        """Emit glowing particles around a point"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius)
            self.particles.append(Particle(
                x=x + math.cos(angle) * dist,
                y=y + math.sin(angle) * dist,
                vx=0,
                vy=-random.uniform(0.5, 1.5),
                life=1.0,
                max_life=random.uniform(0.5, 1.0),
                size=random.uniform(2, 5),
                color=color,
                gravity=0,
                friction=1.0,
                shape='circle'
            ))

    def emit_sparkle(self, x: float, y: float, color: Tuple[int, int, int] = (255, 255, 200),
                    count: int = 8) -> None:
        """Emit sparkling star particles"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(0.4, 0.8),
                size=random.uniform(5, 10),
                color=color,
                gravity=0,
                friction=0.95,
                shape='star',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-20, 20)
            ))

    def emit_stamp(self, x: float, y: float, color: Tuple[int, int, int] = (46, 204, 113)) -> None:
        """Emit particles for stamp effect (APPROVED/DENIED)"""
        if len(self.particles) >= self.max_particles:
            return

        # Ring of particles
        for i in range(20):
            angle = (i / 20) * 2 * math.pi
            speed = random.uniform(3, 6)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(0.4, 0.7),
                size=random.uniform(3, 6),
                color=color,
                gravity=0.1,
                friction=0.92,
                shape='circle'
            ))

    def emit_timer_warning(self, x: float, y: float) -> None:
        """Emit warning particles for timer (red pulsing)"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 2)
            self.particles.append(Particle(
                x=x + math.cos(angle) * 30,
                y=y + math.sin(angle) * 30,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=0.5,
                size=random.uniform(3, 5),
                color=(231, 76, 60),  # Red
                gravity=0,
                friction=0.95,
                shape='circle'
            ))

    # ==================== Healthcare-Specific Emitters ====================

    def emit_pill(self, x: float, y: float, count: int = 8) -> None:
        """Emit pill-shaped particles for pharmacy/medication"""
        if len(self.particles) >= self.max_particles:
            return

        pill_colors = [
            (155, 89, 182),   # Purple
            (41, 128, 185),   # Blue
            (231, 76, 60),    # Red
            (46, 204, 113),   # Green
            (243, 156, 18),   # Orange
        ]

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x=x + random.randint(-10, 10),
                y=y + random.randint(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                life=1.0,
                max_life=random.uniform(0.8, 1.2),
                size=random.uniform(6, 10),
                color=random.choice(pill_colors),
                gravity=0.2,
                friction=0.95,
                shape='pill',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-10, 10)
            ))

    def emit_heartbeat(self, x: float, y: float, count: int = 5) -> None:
        """Emit heart-shaped particles for health/pulse effect"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append(Particle(
                x=x + random.randint(-5, 5),
                y=y + random.randint(-5, 5),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 1,  # Slight upward
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(8, 14),
                color=(231, 76, 60),  # Red heart
                gravity=0.1,
                friction=0.95,
                shape='heart'
            ))

    def emit_breath(self, x: float, y: float, phase: str = 'exhale',
                   count: int = 10) -> None:
        """Emit soft circular particles for breathing exercise"""
        if len(self.particles) >= self.max_particles:
            return

        # Different colors for different phases
        if phase == 'inhale':
            color = (52, 152, 219)  # Blue
            direction = 1  # Inward
        elif phase == 'exhale':
            color = (46, 204, 113)  # Green
            direction = -1  # Outward
        else:  # hold
            color = (241, 196, 15)  # Yellow
            direction = 0

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            if direction == 0:
                # Gentle float for hold
                speed = random.uniform(0.3, 0.8)
                vx = math.cos(angle) * speed
                vy = -random.uniform(0.5, 1)
            else:
                # Radial movement for inhale/exhale
                speed = random.uniform(1, 3) * direction
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed

            self.particles.append(Particle(
                x=x + math.cos(angle) * random.uniform(20, 40),
                y=y + math.sin(angle) * random.uniform(20, 40),
                vx=vx,
                vy=vy,
                life=1.0,
                max_life=random.uniform(0.5, 0.8),
                size=random.uniform(3, 7),
                color=color,
                gravity=0,
                friction=0.96,
                shape='circle',
                fade=True,
                shrink=True
            ))

    def emit_anxiety_reduction(self, x: float, y: float, count: int = 12) -> None:
        """Emit calming particles when anxiety decreases"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(20, 50)
            self.particles.append(Particle(
                x=x + math.cos(angle) * dist,
                y=y + math.sin(angle) * dist,
                vx=0,
                vy=-random.uniform(0.5, 1.5),
                life=1.0,
                max_life=random.uniform(0.8, 1.2),
                size=random.uniform(4, 8),
                color=(46, 204, 113),  # Calming green
                gravity=-0.02,  # Float upward
                friction=0.98,
                shape='circle'
            ))

    def emit_insurance_approved(self, x: float, y: float) -> None:
        """Special effect for insurance approval"""
        # Green burst
        self.emit_success(x, y, count=20)

        # Plus some confetti
        self.emit_confetti(x, y, count=30, colors=[
            (46, 204, 113),   # Green
            (39, 174, 96),    # Darker green
            (255, 255, 255),  # White
        ])

        # Stamp effect
        self.emit_stamp(x, y, color=(46, 204, 113))

    def emit_insurance_denied(self, x: float, y: float) -> None:
        """Special effect for insurance denial"""
        # Red burst
        self.emit_error(x, y, count=15)

        # Stamp effect in red
        self.emit_stamp(x, y, color=(231, 76, 60))

    def emit_money_saved(self, x: float, y: float, amount: int = 0) -> None:
        """Emit particles when money is saved (generic medication choice)"""
        if len(self.particles) >= self.max_particles:
            return

        # Green sparkles for savings
        self.emit_sparkle(x, y, color=(46, 204, 113), count=10)

        # Coin-like circles
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 4)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=random.uniform(5, 9),
                color=(243, 156, 18),  # Gold/orange for money
                gravity=0.15,
                friction=0.95,
                shape='circle'
            ))

    def emit_mail_important(self, x: float, y: float) -> None:
        """Special effect for finding important mail"""
        # Urgent red glow
        self.emit_glow(x, y, color=(231, 76, 60), radius=40, count=15)

        # Sparkles
        self.emit_sparkle(x, y, color=(255, 200, 200), count=10)


# Global instance for easy access
healthcare_particles = HealthcareParticleSystem()

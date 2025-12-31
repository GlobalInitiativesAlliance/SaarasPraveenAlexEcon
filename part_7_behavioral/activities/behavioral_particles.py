"""
Behavioral Particles Module
Visual particle effects for stress, overwhelm, money drain, and decisions
For Part 7 (Behavioral Economics) mini-games
"""
import pygame
import random
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass, field


@dataclass
class Particle:
    """Single particle with physics and rendering properties"""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    life: float = 1.0
    max_life: float = 1.0
    size: float = 4.0
    color: Tuple[int, int, int] = (255, 255, 255)
    alpha: int = 255
    gravity: float = 0.0
    friction: float = 0.98
    shrink: bool = True
    rotation: float = 0.0
    rotation_speed: float = 0.0
    shape: str = 'circle'  # 'circle', 'square', 'star', 'dollar'

    def update(self, dt: float) -> bool:
        """Update particle, return False if dead"""
        # Apply physics
        self.vy += self.gravity * dt * 60
        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60

        # Update life
        self.life -= dt
        if self.life <= 0:
            return False

        # Update visual properties
        life_ratio = self.life / self.max_life
        self.alpha = int(255 * life_ratio)

        if self.shrink:
            # Size decreases over lifetime
            self.size = self.size * (0.95 + 0.05 * life_ratio)

        self.rotation += self.rotation_speed * dt * 60

        return True

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the particle"""
        if self.alpha <= 0 or self.size < 1:
            return

        if self.shape == 'circle':
            # Create surface with alpha
            size = int(self.size * 2) + 2
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.alpha),
                             (size // 2, size // 2), int(self.size))
            screen.blit(surf, (int(self.x - size // 2), int(self.y - size // 2)))

        elif self.shape == 'square':
            size = int(self.size * 2)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color, self.alpha), (0, 0, size, size))
            # Rotate
            if self.rotation != 0:
                surf = pygame.transform.rotate(surf, self.rotation)
            screen.blit(surf, (int(self.x - surf.get_width() // 2),
                              int(self.y - surf.get_height() // 2)))

        elif self.shape == 'star':
            self._draw_star(screen)

        elif self.shape == 'dollar':
            self._draw_dollar(screen)

    def _draw_star(self, screen: pygame.Surface) -> None:
        """Draw a star-shaped particle"""
        points = []
        for i in range(5):
            angle = self.rotation + i * 72 * math.pi / 180 - math.pi / 2
            # Outer point
            ox = self.x + self.size * math.cos(angle)
            oy = self.y + self.size * math.sin(angle)
            points.append((ox, oy))
            # Inner point
            inner_angle = angle + 36 * math.pi / 180
            ix = self.x + self.size * 0.4 * math.cos(inner_angle)
            iy = self.y + self.size * 0.4 * math.sin(inner_angle)
            points.append((ix, iy))

        if len(points) >= 3:
            surf = pygame.Surface((int(self.size * 3), int(self.size * 3)), pygame.SRCALPHA)
            offset_points = [(p[0] - self.x + self.size * 1.5,
                            p[1] - self.y + self.size * 1.5) for p in points]
            pygame.draw.polygon(surf, (*self.color, self.alpha), offset_points)
            screen.blit(surf, (int(self.x - self.size * 1.5),
                              int(self.y - self.size * 1.5)))

    def _draw_dollar(self, screen: pygame.Surface) -> None:
        """Draw a dollar sign particle"""
        try:
            font = pygame.font.Font(None, int(self.size * 2))
            text = font.render("$", True, self.color)
            text.set_alpha(self.alpha)
            screen.blit(text, (int(self.x - text.get_width() // 2),
                              int(self.y - text.get_height() // 2)))
        except:
            # Fallback to circle
            self.shape = 'circle'
            self.draw(screen)


class ParticleSystem:
    """Manages and updates a collection of particles"""

    def __init__(self, max_particles: int = 200):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def add(self, particle: Particle) -> None:
        """Add a particle to the system"""
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)

    def update(self, dt: float) -> None:
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)

    def clear(self) -> None:
        """Remove all particles"""
        self.particles.clear()

    @property
    def count(self) -> int:
        return len(self.particles)


class BehavioralParticleEffects:
    """Pre-defined particle effects for behavioral economics games"""

    def __init__(self):
        self.system = ParticleSystem(300)

    def update(self, dt: float) -> None:
        """Update the particle system"""
        self.system.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles"""
        self.system.draw(screen)

    def clear(self) -> None:
        """Clear all particles"""
        self.system.clear()

    def emit_stress_burst(self, x: float, y: float, intensity: float = 1.0) -> None:
        """Emit stress particles - red/orange burst"""
        count = int(15 * intensity)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5) * intensity
            self.system.add(Particle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.4, 0.8),
                max_life=0.8,
                size=random.uniform(3, 6),
                color=(220, random.randint(60, 120), random.randint(60, 100)),
                gravity=0.1,
                friction=0.96,
                shape='circle'
            ))

    def emit_anxiety_swirl(self, x: float, y: float, radius: float = 30) -> None:
        """Emit anxiety particles - orange swirling effect"""
        for i in range(8):
            angle = (i / 8) * 2 * math.pi + random.uniform(-0.2, 0.2)
            dist = radius * random.uniform(0.5, 1.0)
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist

            # Spiral velocity
            spiral_angle = angle + math.pi / 2
            speed = random.uniform(1, 2)

            self.system.add(Particle(
                x=px, y=py,
                vx=math.cos(spiral_angle) * speed,
                vy=math.sin(spiral_angle) * speed,
                life=random.uniform(0.5, 1.0),
                max_life=1.0,
                size=random.uniform(2, 4),
                color=(230, random.randint(140, 180), random.randint(60, 100)),
                gravity=0.05,
                friction=0.98,
                rotation_speed=random.uniform(-5, 5),
                shape='square'
            ))

    def emit_guilt_particles(self, x: float, y: float) -> None:
        """Emit guilt particles - purple falling slowly"""
        for _ in range(10):
            self.system.add(Particle(
                x=x + random.uniform(-20, 20),
                y=y + random.uniform(-10, 10),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-2, -0.5),
                life=random.uniform(0.8, 1.5),
                max_life=1.5,
                size=random.uniform(3, 5),
                color=(170, random.randint(80, 120), random.randint(160, 200)),
                gravity=0.15,
                friction=0.99,
                shape='circle'
            ))

    def emit_money_drain(self, x: float, y: float, amount: int = 1) -> None:
        """Emit money particles - green dollars falling away"""
        count = min(amount, 5)
        for _ in range(count):
            self.system.add(Particle(
                x=x + random.uniform(-15, 15),
                y=y,
                vx=random.uniform(-1.5, 1.5),
                vy=random.uniform(-3, -1),
                life=random.uniform(1.0, 1.5),
                max_life=1.5,
                size=random.uniform(12, 18),
                color=(80, random.randint(140, 180), random.randint(80, 120)),
                gravity=0.2,
                friction=0.98,
                rotation_speed=random.uniform(-3, 3),
                shape='dollar',
                shrink=False
            ))

    def emit_success_burst(self, x: float, y: float) -> None:
        """Emit success particles - green starburst"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            self.system.add(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.5, 1.0),
                max_life=1.0,
                size=random.uniform(4, 8),
                color=(random.randint(70, 120), random.randint(180, 220), random.randint(100, 140)),
                gravity=0.08,
                friction=0.95,
                rotation_speed=random.uniform(-10, 10),
                shape='star'
            ))

    def emit_decision_sparkle(self, x: float, y: float) -> None:
        """Emit decision sparkles - blue/white twinkles"""
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(5, 25)
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist

            self.system.add(Particle(
                x=px, y=py,
                vx=random.uniform(-0.3, 0.3),
                vy=random.uniform(-0.3, 0.3),
                life=random.uniform(0.3, 0.6),
                max_life=0.6,
                size=random.uniform(2, 4),
                color=(random.randint(180, 255), random.randint(200, 255), 255),
                gravity=0,
                friction=0.99,
                shape='star'
            ))

    def emit_overwhelm_cloud(self, x: float, y: float, width: float = 100) -> None:
        """Emit overwhelm particles - gray cloud spreading"""
        for _ in range(15):
            self.system.add(Particle(
                x=x + random.uniform(-width / 2, width / 2),
                y=y + random.uniform(-20, 20),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-1.5, 0.5),
                life=random.uniform(0.8, 1.5),
                max_life=1.5,
                size=random.uniform(8, 15),
                color=(random.randint(100, 140), random.randint(95, 135), random.randint(110, 150)),
                gravity=-0.02,  # Float upward
                friction=0.97,
                shrink=True,
                shape='circle'
            ))

    def emit_payment_success(self, x: float, y: float) -> None:
        """Emit payment success - green check effect"""
        # Central burst
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.system.add(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.4, 0.8),
                max_life=0.8,
                size=random.uniform(3, 6),
                color=(random.randint(80, 120), random.randint(180, 220), random.randint(100, 140)),
                gravity=0.1,
                friction=0.94,
                shape='circle'
            ))

        # Add some sparkles
        self.emit_decision_sparkle(x, y)

    def emit_bill_drop(self, x: float, y: float, amount: float) -> None:
        """Emit effect when bill is paid - money floating away"""
        # More particles for larger bills
        count = min(int(amount / 20) + 3, 8)
        for _ in range(count):
            self.system.add(Particle(
                x=x + random.uniform(-10, 10),
                y=y,
                vx=random.uniform(-2, 2),
                vy=random.uniform(-4, -2),
                life=random.uniform(0.6, 1.0),
                max_life=1.0,
                size=random.uniform(10, 16),
                color=(75, 160, 100),
                gravity=0.15,
                friction=0.97,
                rotation_speed=random.uniform(-4, 4),
                shape='dollar',
                shrink=False
            ))

    def emit_time_warning(self, x: float, y: float) -> None:
        """Emit time warning particles - red pulsing"""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.system.add(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.3, 0.5),
                max_life=0.5,
                size=random.uniform(4, 8),
                color=(220, random.randint(60, 100), random.randint(60, 100)),
                gravity=0,
                friction=0.92,
                shape='circle'
            ))

    def emit_task_complete(self, x: float, y: float) -> None:
        """Emit task completion effect"""
        # Upward burst
        for _ in range(12):
            angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)  # Upward arc
            speed = random.uniform(2, 5)
            self.system.add(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(0.5, 0.9),
                max_life=0.9,
                size=random.uniform(3, 6),
                color=(random.randint(100, 150), random.randint(180, 220), random.randint(120, 160)),
                gravity=0.12,
                friction=0.96,
                shape='star' if random.random() > 0.5 else 'circle'
            ))

    def emit_choice_made(self, x: float, y: float, is_positive: bool = True) -> None:
        """Emit effect when a choice is made"""
        if is_positive:
            self.emit_success_burst(x, y)
        else:
            self.emit_anxiety_swirl(x, y)


# Global instance for easy access
behavioral_particles = BehavioralParticleEffects()

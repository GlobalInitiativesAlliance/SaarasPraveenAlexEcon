"""
Legal System Particle Effects
Provides visual feedback through animated particles for Part 3 mini-games
Includes legal-themed emitters for courthouse, documents, and debt visualizations
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


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
    shape: str = 'circle'  # 'circle', 'square', 'star', 'line', 'dollar'
    rotation: float = 0.0
    rotation_speed: float = 0.0
    text: str = ""  # For text-based particles (like dollar signs)


class LegalParticleSystem:
    """
    Manages particle effects for legal system mini-games
    Provides success, error, paper, and legal-themed effects
    """

    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 500  # Performance limit
        self._font = None

    def _get_font(self, size: int = 16):
        """Get or create font for text particles"""
        if self._font is None:
            try:
                self._font = pygame.font.SysFont('SF Pro Display', size, bold=True)
            except:
                self._font = pygame.font.Font(None, size)
        return self._font

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
            elif particle.shape == 'dollar':
                self._draw_dollar(screen, particle, alpha)
            elif particle.shape == 'text':
                self._draw_text(screen, particle, alpha)

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

    def _draw_dollar(self, screen: pygame.Surface, particle: Particle,
                    alpha: int) -> None:
        """Draw a dollar sign particle"""
        font = self._get_font(int(particle.size * 2))
        text = font.render("$", True, particle.color)
        text.set_alpha(alpha)
        rect = text.get_rect(center=(int(particle.x), int(particle.y)))
        screen.blit(text, rect)

    def _draw_text(self, screen: pygame.Surface, particle: Particle,
                  alpha: int) -> None:
        """Draw a text particle"""
        font = self._get_font(int(particle.size * 2))
        text = font.render(particle.text, True, particle.color)
        text.set_alpha(alpha)
        rect = text.get_rect(center=(int(particle.x), int(particle.y)))
        screen.blit(text, rect)

    def clear(self) -> None:
        """Remove all particles"""
        self.particles.clear()

    # ==================== Standard Emitter Functions ====================

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
                color=(72, 187, 120),  # Green
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
                color=(237, 94, 104),  # Red
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
                (70, 90, 120),    # Steel blue
                (212, 175, 55),   # Gold
                (72, 187, 120),   # Green
                (139, 90, 43),    # Brown
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
        """Emit paper-like particles for document/envelope movement"""
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
                color=(252, 251, 248),  # Paper color
                gravity=0.05,
                friction=0.9,
                shape='square',
                rotation=random.uniform(0, 360),
                rotation_speed=random.uniform(-5, 5)
            ))

    def emit_sparkle(self, x: float, y: float,
                    color: Tuple[int, int, int] = (212, 175, 55),
                    count: int = 8) -> None:
        """Emit sparkling star particles (gold by default for legal theme)"""
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

    # ==================== Legal-Themed Emitter Functions ====================

    def emit_gavel(self, x: float, y: float, count: int = 20) -> None:
        """Emit gavel impact particles (brown/gold burst for court scenes)"""
        if len(self.particles) >= self.max_particles:
            return

        colors = [
            (139, 90, 43),    # Gavel brown
            (212, 175, 55),   # Justice gold
            (100, 65, 30),    # Dark wood
        ]

        # Ring of particles like a stamp/impact
        for i in range(count):
            angle = (i / count) * 2 * math.pi
            speed = random.uniform(4, 8)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(0.5, 0.9),
                size=random.uniform(4, 8),
                color=random.choice(colors),
                gravity=0.2,
                friction=0.92,
                shape='circle'
            ))

    def emit_stamp(self, x: float, y: float,
                  color: Tuple[int, int, int] = (70, 90, 120)) -> None:
        """Emit particles for stamp/seal effect"""
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

    def emit_debt_increase(self, x: float, y: float, amount: int = 100) -> None:
        """Emit rising dollar signs to show debt increasing"""
        if len(self.particles) >= self.max_particles:
            return

        # Main amount particle
        self.particles.append(Particle(
            x=x,
            y=y,
            vx=random.uniform(-0.5, 0.5),
            vy=-2,  # Rise upward
            life=1.0,
            max_life=1.5,
            size=12,
            color=(198, 40, 40),  # Warning red
            gravity=-0.02,  # Float upward
            friction=0.99,
            shape='text',
            text=f"-${amount}"
        ))

        # Small dollar particles around it
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            self.particles.append(Particle(
                x=x + random.randint(-20, 20),
                y=y + random.randint(-10, 10),
                vx=math.cos(angle) * 2,
                vy=-random.uniform(1, 3),
                life=1.0,
                max_life=random.uniform(0.6, 1.0),
                size=8,
                color=(237, 94, 104),  # Lighter red
                gravity=-0.01,
                friction=0.98,
                shape='dollar'
            ))

    def emit_debt_decrease(self, x: float, y: float, amount: int = 100) -> None:
        """Emit falling particles to show debt decreasing (positive)"""
        if len(self.particles) >= self.max_particles:
            return

        # Main amount particle
        self.particles.append(Particle(
            x=x,
            y=y,
            vx=random.uniform(-0.5, 0.5),
            vy=-1.5,  # Rise slightly
            life=1.0,
            max_life=1.5,
            size=12,
            color=(72, 187, 120),  # Success green
            gravity=-0.01,
            friction=0.99,
            shape='text',
            text=f"+${amount}"
        ))

        # Success sparkles
        self.emit_sparkle(x, y, color=(72, 187, 120), count=10)

    def emit_warning(self, x: float, y: float, count: int = 10) -> None:
        """Emit red warning/urgent particles"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
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
                color=(198, 40, 40),  # Urgent red
                gravity=0,
                friction=0.95,
                shape='circle'
            ))

    def emit_court_summons_discovery(self, x: float, y: float) -> None:
        """Special dramatic effect when court summons is discovered"""
        if len(self.particles) >= self.max_particles:
            return

        # Central burst of warning particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(0.8, 1.2),
                size=random.uniform(5, 10),
                color=(255, 100, 100),  # Alarming red/pink
                gravity=0.1,
                friction=0.94,
                shape='circle'
            ))

        # Rising exclamation marks
        for i in range(3):
            self.particles.append(Particle(
                x=x + (i - 1) * 30,
                y=y - 20,
                vx=0,
                vy=-2,
                life=1.0,
                max_life=1.5,
                size=10,
                color=(198, 40, 40),
                gravity=-0.02,
                friction=0.99,
                shape='text',
                text="!"
            ))

    def emit_envelope_sorted(self, x: float, y: float, correct: bool) -> None:
        """Emit particles when envelope is sorted"""
        if correct:
            self.emit_success(x, y, count=12)
        else:
            self.emit_error(x, y, count=8)

    def emit_screen_flash(self, screen: pygame.Surface,
                         color: Tuple[int, int, int] = (255, 255, 255),
                         alpha: int = 100) -> None:
        """Create a brief screen flash effect (call in render, manages its own timing)"""
        flash_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill((*color, alpha))
        screen.blit(flash_surface, (0, 0))


# Global instance for easy access
legal_particles = LegalParticleSystem()

"""
Stress Overload Visual Sequence - Clean Version
All priorities flash on screen simultaneously
Stress meter fills to maximum, character collapses
No heavy effects, no particles, smooth 60 FPS
"""
import pygame
import math

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    pressure_visuals
)
from .time_particles import time_particles
from .time_feedback import time_feedback


class StressOverload:
    """Visual stress overload sequence - clean version"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Priorities that flash
        self.priorities = [
            {"name": "COURT DATE", "color": PressureUIColors.PRESSURE_RED, "x": 80, "y": 140},
            {"name": "SCHOOL MIDTERM", "color": PressureUIColors.CALM_BLUE_LIGHT, "x": 480, "y": 140},
            {"name": "HOUSING CHECK-IN", "color": PressureUIColors.URGENT_ORANGE, "x": 80, "y": 280},
            {"name": "WORK SHIFT", "color": PressureUIColors.TIME_GOLD, "x": 480, "y": 280},
            {"name": "THERAPY", "color": PressureUIColors.STRESS_PURPLE_LIGHT, "x": 280, "y": 420},
        ]

        # Stress meter
        self.stress_level = 0.0

        # Animation
        self.time_elapsed = 0
        self.flash_speed = 3.0
        self.phase = "building"  # building, maximum, collapse

        # Result
        self.show_collapse = False
        self.collapse_timer = 0

    def start(self):
        """Start the stress sequence"""
        self.active = True
        self.completed = False
        self.stress_level = 0.0
        self.time_elapsed = 0
        self.phase = "building"
        self.show_collapse = False
        self.collapse_timer = 0

        time_particles.clear()
        time_feedback.clear()

    def stop(self):
        """Stop the sequence"""
        self.active = False

    def update(self, dt):
        """Update stress sequence"""
        if not self.active:
            return

        self.time_elapsed += dt

        if self.phase == "building":
            # Build stress over time
            self.stress_level = min(1.0, self.stress_level + dt * 0.18)
            self.flash_speed = 3.0 + self.stress_level * 6.0

            if self.stress_level >= 1.0:
                self.phase = "maximum"
                time_feedback.add_overload_banner()

        elif self.phase == "maximum":
            # Hold at maximum stress
            if self.time_elapsed > 7.0:
                self.phase = "collapse"
                time_feedback.fade_to_black(150)

        elif self.phase == "collapse":
            self.show_collapse = True
            self.collapse_timer += dt

            if self.collapse_timer > 6.0:
                self.completed = True
                self.active = False

        # Update feedback
        time_feedback.update(dt)
        time_feedback.set_stress_level(self.stress_level if self.phase != "collapse" else 0.3)

    def handle_event(self, event):
        """Handle events"""
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.phase == "maximum":
                    self.phase = "collapse"
                    time_feedback.fade_to_black(150)
                elif self.phase == "collapse" and self.collapse_timer > 1.5:
                    self.completed = True
                    self.active = False

    def render(self, screen):
        """Render the stress sequence with clean visuals"""
        self._render_content(screen)

        # Render feedback on top
        time_feedback.render(screen)

    def _render_content(self, screen):
        """Render main content"""
        # Background with stress tint
        pressure_visuals.draw_background(screen, self.stress_level if not self.show_collapse else 0.3)

        if not self.show_collapse:
            self._render_building_phase(screen)
        else:
            self._render_collapse_scene(screen)

    def _render_building_phase(self, screen):
        """Render the stress building phase"""
        # Title
        title_color = PressureVisualHelpers.interpolate_color(
            PressureUIColors.TEXT_PRIMARY,
            PressureUIColors.PRESSURE_RED_LIGHT,
            self.stress_level
        )
        pressure_visuals.draw_title(screen, "PRIORITIES", self.SCREEN_WIDTH // 2, 40)

        # Subtitle that changes with stress
        if self.stress_level < 0.5:
            subtitle = "Managing your responsibilities..."
        elif self.stress_level < 0.8:
            subtitle = "Too many things at once..."
        else:
            subtitle = "OVERWHELMING!"

        subtitle_color = PressureVisualHelpers.interpolate_color(
            PressureUIColors.TEXT_SECONDARY,
            PressureUIColors.TEXT_URGENT,
            self.stress_level
        )
        subtitle_surface = pressure_visuals.fonts['body'].render(subtitle, True, subtitle_color)
        screen.blit(subtitle_surface,
                   (self.SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2, 85))

        # Render priority notifications
        for i, priority in enumerate(self.priorities):
            self._render_priority_notification(screen, priority, i)

        # Stress meter
        meter_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 175,
            530, 350, 30
        )
        pressure_visuals.draw_stress_meter(screen, meter_rect, self.stress_level, "STRESS LEVEL")

        # Maximum warning
        if self.stress_level >= 1.0:
            pulse = PressureVisualHelpers.get_pulse_alpha(180, 255, 4.0)
            warning_surface = pressure_visuals.fonts['body_bold'].render(
                "MAXIMUM OVERLOAD", True, PressureUIColors.PRESSURE_RED_LIGHT
            )
            warning_surface.set_alpha(pulse)
            screen.blit(warning_surface,
                       (self.SCREEN_WIDTH // 2 - warning_surface.get_width() // 2, 570))

    def _render_priority_notification(self, screen, priority, index):
        """Render a priority notification - clean version"""
        # Calculate flash intensity
        offset = index * 0.5
        flash = math.sin((self.time_elapsed + offset) * self.flash_speed)
        flash_normalized = (flash + 1) / 2  # 0 to 1

        # Create notification rect
        width = 220
        height = 70
        rect = pygame.Rect(priority["x"], priority["y"], width, height)

        # Draw using the visual component
        is_active = flash_normalized > 0.5 or self.stress_level > 0.8
        pressure_visuals.draw_priority_notification(
            screen, rect,
            priority["name"],
            priority["color"],
            is_active=is_active
        )

    def _render_collapse_scene(self, screen):
        """Render the collapse scene - clean version"""
        # Darken overlay that increases
        overlay_alpha = min(180, int(self.collapse_timer * 60))
        if overlay_alpha > 0:
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 8, 15, overlay_alpha))
            screen.blit(overlay, (0, 0))

        # Static scattered papers (no rotation for performance)
        paper_positions = [
            (140, 380, 70, 90),
            (260, 400, 80, 60),
            (420, 370, 65, 85),
            (520, 395, 75, 70),
            (340, 430, 60, 80),
            (180, 420, 55, 65),
            (580, 410, 70, 55),
        ]

        paper_alpha = min(160, int(self.collapse_timer * 100))
        if paper_alpha > 0:
            for x, y, w, h in paper_positions:
                paper_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(paper_surf, (220, 215, 205, paper_alpha),
                               (0, 0, w, h), border_radius=2)
                pygame.draw.line(paper_surf, (180, 175, 165, paper_alpha // 2),
                               (w // 3, 0), (w // 3, h), 1)
                screen.blit(paper_surf, (x - w // 2, y - h // 2))

        # Bed
        bed_rect = pygame.Rect(230, 290, 340, 160)

        # Bed shadow
        shadow_rect = bed_rect.inflate(20, 10)
        shadow_rect.y += 15
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 50),
                        (0, 0, shadow_rect.width, shadow_rect.height), border_radius=15)
        screen.blit(shadow_surf, shadow_rect)

        # Bed frame
        pygame.draw.rect(screen, (70, 55, 50), bed_rect, border_radius=10)
        pygame.draw.rect(screen, (90, 75, 70), bed_rect.inflate(-10, -10), border_radius=8)

        # Pillow
        pillow_rect = pygame.Rect(bed_rect.x + 20, bed_rect.y + 20, 100, 60)
        pygame.draw.ellipse(screen, (180, 175, 170), pillow_rect)
        pygame.draw.ellipse(screen, (200, 195, 190), pillow_rect.inflate(-10, -8))

        # Blanket
        blanket_rect = pygame.Rect(bed_rect.x + 40, bed_rect.y + 60, 280, 90)
        pygame.draw.rect(screen, (100, 85, 110), blanket_rect, border_radius=8)

        # Character collapsed (simple form under blanket)
        character_color = (150, 130, 120)
        # Head
        pygame.draw.ellipse(screen, character_color,
                          (pillow_rect.x + 25, pillow_rect.y + 10, 55, 45))
        # Body lump under blanket
        pygame.draw.ellipse(screen, (110, 95, 120),
                          (blanket_rect.x + 20, blanket_rect.y - 10, 180, 70))

        # Breathing animation (subtle)
        breath = math.sin(self.collapse_timer * 1.5) * 3
        pygame.draw.ellipse(screen, (115, 100, 125),
                          (blanket_rect.x + 30, blanket_rect.y - 5 + int(breath), 160, 60))

        # Narration text
        if self.collapse_timer > 1.8:
            self._render_narration(screen)

        # Part complete message
        if self.collapse_timer > 5.0:
            complete_alpha = min(255, int((self.collapse_timer - 5.0) * 200))
            complete_text = "Part 9 Complete - Conflicting Responsibilities"
            text_surf = pressure_visuals.fonts['body'].render(
                complete_text, True, PressureUIColors.TEXT_MUTED
            )
            text_surf.set_alpha(complete_alpha)
            screen.blit(text_surf, (self.SCREEN_WIDTH // 2 - text_surf.get_width() // 2, 555))

    def _render_narration(self, screen):
        """Render narration text - clean version"""
        lines = [
            ("Too many responsibilities.", 1.8),
            ("Not enough time.", 2.5),
            ("", 0),
            ("Without support, every decision feels like failure.", 3.5)
        ]

        y_offset = 80
        for line, appear_time in lines:
            if not line:
                y_offset += 15
                continue

            if self.collapse_timer >= appear_time:
                progress = min(1.0, (self.collapse_timer - appear_time) / 0.8)
                alpha = int(255 * progress)
                move_offset = int((1 - progress) * 15)

                text_surf = pressure_visuals.fonts['heading'].render(
                    line, True, PressureUIColors.TEXT_SECONDARY
                )
                text_surf.set_alpha(alpha)
                screen.blit(text_surf,
                           (self.SCREEN_WIDTH // 2 - text_surf.get_width() // 2,
                            y_offset + move_offset - text_surf.get_height() // 2))

            y_offset += 40

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

"""
Stress Overload Visual Sequence - Pressure/Urgency Version
All priorities flash on screen simultaneously
Stress meter fills to maximum, character collapses
Features: Floating notifications, screen shake, paper scatter, cinematic collapse
"""
import pygame
import math
import random

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    PressureVisualComponents, UIAnimation, pressure_visuals
)
from .time_particles import pressure_particles
from .time_feedback import pressure_feedback


class StressOverload:
    """Visual stress overload sequence with pressure theme"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Priorities that flash with icons and styling
        self.priorities = [
            {
                "name": "COURT DATE",
                "icon": "!",
                "color": PressureUIColors.PRESSURE_RED,
                "glow": PressureUIColors.PRESSURE_RED_LIGHT,
                "x": 80, "y": 140
            },
            {
                "name": "SCHOOL MIDTERM",
                "icon": "E",
                "color": PressureUIColors.CALM_BLUE_LIGHT,
                "glow": PressureUIColors.CALM_BLUE,
                "x": 480, "y": 140
            },
            {
                "name": "HOUSING CHECK-IN",
                "icon": "H",
                "color": PressureUIColors.URGENT_ORANGE,
                "glow": PressureUIColors.URGENT_ORANGE_DARK,
                "x": 80, "y": 280
            },
            {
                "name": "WORK SHIFT",
                "icon": "W",
                "color": PressureUIColors.TIME_GOLD,
                "glow": PressureUIColors.TIME_GOLD_DARK,
                "x": 480, "y": 280
            },
            {
                "name": "THERAPY",
                "icon": "T",
                "color": PressureUIColors.STRESS_PURPLE_LIGHT,
                "glow": PressureUIColors.STRESS_PURPLE,
                "x": 280, "y": 420
            },
        ]

        # Priority animation states
        self.priority_animations = []

        # Stress meter
        self.stress_level = 0.0
        self.max_stress = 1.0

        # Animation
        self.time_elapsed = 0
        self.flash_speed = 3.0
        self.phase = "building"  # building, maximum, collapse

        # Result
        self.show_collapse = False
        self.collapse_timer = 0

        # Screen effects
        self.shake_intensity = 0.0
        self.background_stress = 0.0

    def start(self):
        """Start the stress sequence"""
        self.active = True
        self.completed = False
        self.stress_level = 0.0
        self.time_elapsed = 0
        self.phase = "building"
        self.show_collapse = False
        self.collapse_timer = 0
        self.shake_intensity = 0.0
        self.background_stress = 0.0

        # Initialize priority animations
        self.priority_animations = []
        for i in range(len(self.priorities)):
            self.priority_animations.append(UIAnimation(
                phase=i * 0.6,
                speed=1.0 + i * 0.15
            ))

        # Initialize particles and feedback
        pressure_particles.clear()
        pressure_particles.enable_ambient(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            stress_level=0.3
        )
        pressure_feedback.clear()

    def stop(self):
        """Stop the sequence"""
        self.active = False
        pressure_particles.disable_ambient()

    def update(self, dt):
        """Update stress sequence"""
        if not self.active:
            return

        self.time_elapsed += dt

        # Update animations
        for anim in self.priority_animations:
            anim.update(dt)

        if self.phase == "building":
            # Build stress over time
            self.stress_level = min(1.0, self.stress_level + dt * 0.18)
            self.flash_speed = 3.0 + self.stress_level * 6.0
            self.background_stress = self.stress_level

            # Increase shake with stress
            self.shake_intensity = self.stress_level * 6

            # Update particle stress
            pressure_particles.set_stress_level(self.stress_level)

            # Emit stress sparks periodically at high stress
            if self.stress_level > 0.6:
                if random.random() < self.stress_level * 0.15:
                    idx = random.randint(0, len(self.priorities) - 1)
                    p = self.priorities[idx]
                    pressure_particles.emit_stress_sparks(
                        p["x"] + 100, p["y"] + 30,
                        count=3, intensity=self.stress_level
                    )

            if self.stress_level >= 1.0:
                self.phase = "maximum"
                pressure_feedback.add_overload_banner()
                pressure_feedback.trigger_screen_shake(15)

        elif self.phase == "maximum":
            # Hold at maximum stress with intense effects
            self.shake_intensity = 8 + math.sin(self.time_elapsed * 10) * 4

            # Constant alarm particles
            if random.random() < 0.1:
                pressure_particles.emit_alarm_particles(
                    self.SCREEN_WIDTH // 2,
                    self.SCREEN_HEIGHT // 2,
                    count=3
                )

            if self.time_elapsed > 7.0:
                self.phase = "collapse"
                pressure_feedback.start_overload_effect(3.0)

        elif self.phase == "collapse":
            self.show_collapse = True
            self.collapse_timer += dt

            # Emit paper scatter at start
            if self.collapse_timer < 0.5:
                pressure_particles.emit_paper_scatter(
                    self.SCREEN_WIDTH // 2,
                    self.SCREEN_HEIGHT // 2,
                    count=2
                )

            # Decrease shake as collapse progresses
            self.shake_intensity = max(0, 10 - self.collapse_timer * 3)
            self.background_stress = max(0.3, 1.0 - self.collapse_timer * 0.2)

            if self.collapse_timer > 6.0:
                self.completed = True
                self.active = False

        # Update particles and feedback
        pressure_particles.update(dt)
        pressure_feedback.update(dt)
        pressure_feedback.set_stress_level(self.background_stress)

    def handle_event(self, event):
        """Handle events"""
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.phase == "maximum":
                    self.phase = "collapse"
                    pressure_feedback.start_overload_effect(3.0)
                elif self.phase == "collapse" and self.collapse_timer > 1.5:
                    self.completed = True
                    self.active = False

    def render(self, screen):
        """Render the stress sequence with pressure visuals"""
        # Get shake offset
        shake_x = 0
        shake_y = 0
        if self.shake_intensity > 0:
            shake_x = math.sin(self.time_elapsed * 40) * self.shake_intensity
            shake_y = math.cos(self.time_elapsed * 37) * self.shake_intensity * 0.7

        # Create offset surface for shake
        if abs(shake_x) > 0.5 or abs(shake_y) > 0.5:
            temp_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self._render_content(temp_surface)
            screen.fill(PressureUIColors.DARK_BG)
            screen.blit(temp_surface, (int(shake_x), int(shake_y)))
        else:
            self._render_content(screen)

        # Render particles and feedback on top
        pressure_particles.render(screen)
        pressure_feedback.render(screen)

    def _render_content(self, screen):
        """Render main content"""
        # Background with stress gradient
        pressure_visuals.draw_pressure_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            stress_level=self.background_stress
        )

        if not self.show_collapse:
            self._render_building_phase(screen)
        else:
            self._render_collapse_scene(screen)

    def _render_building_phase(self, screen):
        """Render the stress building phase"""
        # Title with urgency glow
        title_color = PressureUIColors.HIGHLIGHT_WHITE
        glow_color = PressureVisualHelpers.interpolate_color(
            PressureUIColors.TIME_GOLD,
            PressureUIColors.PRESSURE_RED,
            self.stress_level
        )

        PressureVisualHelpers.draw_text_with_glow(
            screen, "PRIORITIES",
            (self.SCREEN_WIDTH // 2, 50),
            pressure_visuals.fonts['title'],
            title_color, glow_color
        )

        # Subtitle that changes with stress
        if self.stress_level < 0.5:
            subtitle = "Managing your responsibilities..."
        elif self.stress_level < 0.8:
            subtitle = "Too many things at once..."
        else:
            subtitle = "OVERWHELMING!"

        PressureVisualHelpers.draw_text_with_glow(
            screen, subtitle,
            (self.SCREEN_WIDTH // 2, 95),
            pressure_visuals.fonts['small'],
            PressureUIColors.HIGHLIGHT_DIM,
            PressureUIColors.URGENT_ORANGE
        )

        # Render priority notifications
        for i, priority in enumerate(self.priorities):
            self._render_priority_notification(screen, priority, i)

        # Stress meter
        self._render_stress_meter(screen)

    def _render_priority_notification(self, screen, priority, index):
        """Render a flashing priority notification"""
        anim = self.priority_animations[index] if index < len(self.priority_animations) else None

        # Calculate flash intensity
        offset = index * 0.5
        flash = math.sin((self.time_elapsed + offset) * self.flash_speed)
        flash_normalized = (flash + 1) / 2  # 0 to 1

        # Float offset
        float_offset = 0
        if anim:
            float_offset = int(math.sin(anim.phase) * (3 + self.stress_level * 4))

        # Scale effect at high stress
        scale = 1.0
        if self.stress_level > 0.7:
            scale = 1.0 + flash_normalized * 0.1 * self.stress_level

        # Create notification rect
        base_width = 220
        base_height = 70
        width = int(base_width * scale)
        height = int(base_height * scale)
        x = priority["x"] - (width - base_width) // 2
        y = priority["y"] + float_offset - (height - base_height) // 2

        rect = pygame.Rect(x, y, width, height)

        # Draw notification bubble
        glow_intensity = 0.3 + flash_normalized * 0.5 * self.stress_level

        # Background with glow
        for i in range(4, 0, -1):
            glow_rect = rect.inflate(i * 6, i * 4)
            glow_alpha = int(40 * glow_intensity * (1 - i / 5))
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*priority["glow"], glow_alpha),
                           (0, 0, glow_rect.width, glow_rect.height), border_radius=12)
            screen.blit(glow_surface, glow_rect)

        # Main background
        bg_alpha = int(200 + flash_normalized * 55)
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*PressureUIColors.DARK_BG, bg_alpha),
                        (0, 0, width, height), border_radius=10)
        screen.blit(bg_surface, rect)

        # Border
        border_color = PressureVisualHelpers.interpolate_color(
            priority["color"],
            PressureUIColors.HIGHLIGHT_WHITE,
            flash_normalized * 0.4
        )
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)

        # Icon circle
        icon_radius = 18
        icon_x = rect.x + 25
        icon_y = rect.centery
        pygame.draw.circle(screen, priority["color"], (icon_x, icon_y), icon_radius)

        # Icon text
        icon_font = pressure_visuals.fonts['body']
        icon_text = icon_font.render(priority["icon"], True, PressureUIColors.DARK_BG)
        screen.blit(icon_text, (icon_x - icon_text.get_width() // 2,
                                icon_y - icon_text.get_height() // 2))

        # Priority name
        text_alpha = int(180 + flash_normalized * 75)
        text_color = PressureVisualHelpers.interpolate_color(
            priority["color"],
            PressureUIColors.HIGHLIGHT_WHITE,
            flash_normalized * 0.3
        )
        name_font = pressure_visuals.fonts['body']
        name_text = name_font.render(priority["name"], True, text_color)
        name_text.set_alpha(text_alpha)
        screen.blit(name_text, (rect.x + 55, rect.centery - name_text.get_height() // 2))

    def _render_stress_meter(self, screen):
        """Render the stress meter with visual effects"""
        meter_width = 350
        meter_height = 35
        meter_x = self.SCREEN_WIDTH // 2 - meter_width // 2
        meter_y = 530

        # Label
        label_color = PressureVisualHelpers.interpolate_color(
            PressureUIColors.HIGHLIGHT_DIM,
            PressureUIColors.PRESSURE_RED_LIGHT,
            self.stress_level
        )
        PressureVisualHelpers.draw_text_with_glow(
            screen, "STRESS LEVEL",
            (self.SCREEN_WIDTH // 2, meter_y - 20),
            pressure_visuals.fonts['small'],
            label_color,
            PressureUIColors.PRESSURE_RED if self.stress_level > 0.7 else PressureUIColors.TIME_GOLD
        )

        # Draw the meter
        pressure_visuals.draw_stress_meter(
            screen, meter_x, meter_y, meter_width, meter_height,
            self.stress_level,
            pulse=self.stress_level > 0.5,
            flash_phase=self.time_elapsed * 4 if self.stress_level >= 1.0 else 0
        )

        # Maximum warning
        if self.stress_level >= 1.0:
            pulse = 0.7 + math.sin(self.time_elapsed * 8) * 0.3
            max_color = tuple(int(c * pulse) for c in PressureUIColors.PRESSURE_RED_LIGHT)
            PressureVisualHelpers.draw_text_with_glow(
                screen, "MAXIMUM OVERLOAD",
                (self.SCREEN_WIDTH // 2, meter_y + meter_height + 20),
                pressure_visuals.fonts['body'],
                max_color,
                PressureUIColors.PRESSURE_RED
            )

    def _render_collapse_scene(self, screen):
        """Render the collapse scene"""
        # Darken overlay that increases
        overlay_alpha = min(200, int(self.collapse_timer * 80))
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 8, 15, overlay_alpha))
        screen.blit(overlay, (0, 0))

        # Scattered papers (drawn as static elements)
        paper_positions = [
            (140, 380, 70, 90, -15),
            (260, 400, 80, 60, 12),
            (420, 370, 65, 85, -8),
            (520, 395, 75, 70, 20),
            (340, 430, 60, 80, 5),
            (180, 420, 55, 65, -22),
            (580, 410, 70, 55, 15),
        ]

        paper_alpha = min(180, int(self.collapse_timer * 120))
        for x, y, w, h, angle in paper_positions:
            paper_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Paper with slight color variation
            paper_color = random.choice([
                (220, 215, 205),
                (230, 225, 215),
                (210, 205, 195),
            ])
            pygame.draw.rect(paper_surf, (*paper_color, paper_alpha),
                           (0, 0, w, h), border_radius=2)
            # Fold line
            pygame.draw.line(paper_surf, (180, 175, 165, paper_alpha // 2),
                           (w // 3, 0), (w // 3, h), 1)
            rotated = pygame.transform.rotate(paper_surf, angle)
            screen.blit(rotated, (x - rotated.get_width() // 2,
                                  y - rotated.get_height() // 2))

        # Bed
        bed_rect = pygame.Rect(230, 290, 340, 160)

        # Bed shadow
        shadow_rect = bed_rect.inflate(20, 10)
        shadow_rect.y += 15
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_rect.width, shadow_rect.height),
                        border_radius=15)
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
                          (blanket_rect.x + 30, blanket_rect.y - 5 + breath, 160, 60))

        # Narration text
        if self.collapse_timer > 1.8:
            self._render_narration(screen)

        # Part complete message
        if self.collapse_timer > 5.0:
            complete_alpha = min(255, int((self.collapse_timer - 5.0) * 200))
            complete_text = "Part 9 Complete - Conflicting Responsibilities"
            text_surf = pressure_visuals.fonts['body'].render(
                complete_text, True, PressureUIColors.HIGHLIGHT_DIM
            )
            text_surf.set_alpha(complete_alpha)
            screen.blit(text_surf, (self.SCREEN_WIDTH // 2 - text_surf.get_width() // 2, 555))

    def _render_narration(self, screen):
        """Render cinematic narration"""
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

                # Fade in with slight upward movement
                move_offset = int((1 - progress) * 15)

                PressureVisualHelpers.draw_text_with_glow(
                    screen, line,
                    (self.SCREEN_WIDTH // 2, y_offset + move_offset),
                    pressure_visuals.fonts['heading'],
                    (*PressureUIColors.HIGHLIGHT_DIM[:3],),
                    PressureUIColors.STRESS_PURPLE
                )

                # Draw with alpha
                text_surf = pressure_visuals.fonts['heading'].render(
                    line, True, PressureUIColors.HIGHLIGHT_DIM
                )
                text_surf.set_alpha(alpha)
                screen.blit(text_surf, (self.SCREEN_WIDTH // 2 - text_surf.get_width() // 2,
                                        y_offset + move_offset - text_surf.get_height() // 2))

            y_offset += 40

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

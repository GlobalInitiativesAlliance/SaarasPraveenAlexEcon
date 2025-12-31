"""
Stress Overload Visual Sequence
All priorities flash on screen simultaneously
Stress meter fills to maximum, character collapses
"""
import pygame
import math


class StressOverload:
    """Visual stress overload sequence"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Priorities that flash
        self.priorities = [
            {"name": "COURT DATE", "color": (200, 80, 80), "x": 100, "y": 150},
            {"name": "SCHOOL MIDTERM", "color": (100, 150, 200), "x": 500, "y": 150},
            {"name": "HOUSING CHECK-IN", "color": (200, 150, 100), "x": 100, "y": 300},
            {"name": "WORK SHIFT", "color": (100, 180, 100), "x": 500, "y": 300},
            {"name": "THERAPY", "color": (180, 130, 180), "x": 300, "y": 450},
        ]

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

    def start(self):
        """Start the stress sequence"""
        self.active = True
        self.completed = False
        self.stress_level = 0.0
        self.time_elapsed = 0
        self.phase = "building"
        self.show_collapse = False
        self.collapse_timer = 0

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
            self.stress_level = min(1.0, self.stress_level + dt * 0.2)
            self.flash_speed = 3.0 + self.stress_level * 5.0

            if self.stress_level >= 1.0:
                self.phase = "maximum"

        elif self.phase == "maximum":
            # Hold at maximum stress
            self.time_elapsed += dt
            if self.time_elapsed > 8.0:
                self.phase = "collapse"

        elif self.phase == "collapse":
            self.show_collapse = True
            self.collapse_timer += dt
            if self.collapse_timer > 5.0:
                self.completed = True
                self.active = False

    def handle_event(self, event):
        """Handle events"""
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.phase == "maximum":
                    self.phase = "collapse"
                elif self.phase == "collapse" and self.collapse_timer > 1.0:
                    self.completed = True
                    self.active = False

    def render(self, screen):
        """Render the stress sequence"""
        # Background - gets more red as stress increases
        bg_r = int(30 + self.stress_level * 40)
        bg_g = int(30 - self.stress_level * 20)
        bg_b = int(40 - self.stress_level * 20)
        screen.fill((bg_r, bg_g, bg_b))

        if not self.show_collapse:
            # Title
            title_font = pygame.font.Font(None, 48)
            title = title_font.render("PRIORITIES", True, (200, 200, 210))
            screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

            # Flash priorities
            priority_font = pygame.font.Font(None, 36)
            for i, priority in enumerate(self.priorities):
                # Calculate flash
                offset = i * 0.5
                flash = math.sin((self.time_elapsed + offset) * self.flash_speed)
                alpha = int(128 + flash * 127)

                # Create flashing text
                text_surface = priority_font.render(priority["name"], True, priority["color"])
                text_surface.set_alpha(alpha)

                # Shake effect at high stress
                shake_x = 0
                shake_y = 0
                if self.stress_level > 0.7:
                    shake_x = int((flash * 3) * self.stress_level)
                    shake_y = int((math.cos(self.time_elapsed * 10 + i) * 2) * self.stress_level)

                screen.blit(text_surface, (priority["x"] + shake_x, priority["y"] + shake_y))

            # Stress meter
            meter_width = 300
            meter_height = 30
            meter_x = self.SCREEN_WIDTH // 2 - meter_width // 2
            meter_y = 520

            # Background
            pygame.draw.rect(screen, (40, 30, 30), (meter_x, meter_y, meter_width, meter_height))

            # Fill
            fill_width = int(self.stress_level * meter_width)
            fill_color = (
                int(100 + self.stress_level * 155),
                int(80 - self.stress_level * 60),
                int(80 - self.stress_level * 60)
            )
            pygame.draw.rect(screen, fill_color, (meter_x, meter_y, fill_width, meter_height))

            # Border
            pygame.draw.rect(screen, (150, 80, 80), (meter_x, meter_y, meter_width, meter_height), 2)

            # Label
            meter_font = pygame.font.Font(None, 24)
            label = meter_font.render("STRESS", True, (200, 150, 150))
            screen.blit(label, (meter_x + meter_width // 2 - label.get_width() // 2, meter_y - 25))

            if self.stress_level >= 1.0:
                max_text = meter_font.render("MAXIMUM", True, (255, 100, 100))
                screen.blit(max_text, (meter_x + meter_width // 2 - max_text.get_width() // 2, meter_y + 35))

        else:
            # Collapse scene
            # Dark overlay
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.fill((20, 15, 25))
            overlay.set_alpha(int(min(255, self.collapse_timer * 100)))
            screen.blit(overlay, (0, 0))

            # Scattered papers visual (simple rectangles)
            paper_color = (80, 75, 70)
            papers = [
                (150, 400, 60, 80, 15),
                (250, 420, 70, 50, -10),
                (400, 380, 55, 75, 25),
                (500, 410, 65, 60, -20),
                (350, 450, 50, 70, 5),
            ]
            for x, y, w, h, angle in papers:
                paper_surf = pygame.Surface((w, h))
                paper_surf.fill(paper_color)
                paper_surf.set_alpha(150)
                screen.blit(paper_surf, (x, y))

            # Bed shape
            bed_rect = pygame.Rect(250, 300, 300, 150)
            pygame.draw.rect(screen, (60, 50, 50), bed_rect)
            pygame.draw.rect(screen, (80, 70, 70), bed_rect, 2)

            # Character collapsed (simple shape)
            pygame.draw.ellipse(screen, (120, 100, 90), (300, 320, 200, 80))

            # Narration
            if self.collapse_timer > 1.5:
                narration_font = pygame.font.Font(None, 32)

                lines = [
                    "Too many responsibilities.",
                    "Not enough time.",
                    "",
                    "Without support, every decision feels like failure."
                ]

                y_offset = 100
                for line in lines:
                    if line:
                        alpha = min(255, int((self.collapse_timer - 1.5) * 150))
                        text = narration_font.render(line, True, (180, 170, 190))
                        text.set_alpha(alpha)
                        screen.blit(text, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                    y_offset += 35

            # Part complete message
            if self.collapse_timer > 4.0:
                complete_font = pygame.font.Font(None, 28)
                complete = complete_font.render("Part 9 Complete - Conflicting Responsibilities", True, (150, 150, 160))
                complete.set_alpha(min(255, int((self.collapse_timer - 4.0) * 200)))
                screen.blit(complete, (self.SCREEN_WIDTH // 2 - complete.get_width() // 2, 550))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

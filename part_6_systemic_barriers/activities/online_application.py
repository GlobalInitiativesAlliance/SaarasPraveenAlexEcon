"""
Online Application Crash Simulation
Government website that always crashes at 90% completion
Demonstrates digital barriers and system failures

UPGRADED: Browser chrome, form fields, glitch effects,
crash animation, error popups
"""
import pygame
import random
import math
import time

from .systemic_visual_base import (
    SystemicUIColors, SystemicUIMetrics, SystemicVisualHelpers,
    SystemicVisualComponents, UIAnimation, systemic_visuals
)
from .systemic_particles import SystemicParticleSystem
from .systemic_feedback import SystemicFeedbackManager


class OnlineApplicationGame:
    """Simulate a government website that crashes near completion"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Application progress
        self.progress = 0.0
        self.max_progress = 100.0
        self.crash_point = 88.0
        self.has_crashed = False

        # Form fields
        self.form_fields = [
            {'label': 'First Name', 'filled': False, 'progress': 10, 'icon': '👤'},
            {'label': 'Last Name', 'filled': False, 'progress': 10, 'icon': '👤'},
            {'label': 'Date of Birth', 'filled': False, 'progress': 10, 'icon': '📅'},
            {'label': 'SSN', 'filled': False, 'progress': 15, 'icon': '🔐'},
            {'label': 'Address', 'filled': False, 'progress': 10, 'icon': '🏠'},
            {'label': 'Phone', 'filled': False, 'progress': 10, 'icon': '📱'},
            {'label': 'Income', 'filled': False, 'progress': 15, 'icon': '💵'},
            {'label': 'Household Size', 'filled': False, 'progress': 10, 'icon': '👨‍👩‍👧'},
            {'label': 'Foster Status', 'filled': False, 'progress': 10, 'icon': '📋'},
        ]

        self.current_field = 0
        self.filling_field = False
        self.fill_timer = 0
        self.fill_duration = 60

        # UI Rects
        self.browser_rect = pygame.Rect(140, 80, 1000, 560)

        # Error state
        self.error_messages = [
            "Error 500: Internal Server Error",
            "Connection timeout. Please try again later.",
            "Session expired. All data lost.",
            "Database connection failed.",
            "System maintenance in progress."
        ]
        self.current_error = None
        self.error_timer = 0

        # Visual systems
        self.particles = SystemicParticleSystem()
        self.feedback = SystemicFeedbackManager()
        self.visuals = systemic_visuals

        # Animations
        self.loading_angle = 0
        self.cursor_blink = 0
        self.crash_shake = 0
        self.glitch_intensity = 0

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 32, bold=True)
            self.font_heading = pygame.font.SysFont('SF Pro Display', 24, bold=True)
            self.font_body = pygame.font.SysFont('SF Pro Text', 18)
            self.font_small = pygame.font.SysFont('SF Pro Text', 14)
            self.font_mono = pygame.font.SysFont('Monaco', 16)
            self.font_icon = pygame.font.SysFont('Segoe UI Emoji', 16)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_heading = pygame.font.Font(None, 28)
            self.font_body = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 18)
            self.font_mono = pygame.font.Font(None, 18)
            self.font_icon = pygame.font.Font(None, 20)

    def handle_event(self, event):
        """Handle form interaction"""
        if not self.active or self.completed:
            return False

        if self.has_crashed:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if self.error_timer > 60:
                    self.completed = True
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.filling_field and self.current_field < len(self.form_fields):
                self.filling_field = True
                self.fill_timer = self.fill_duration

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not self.filling_field:
                if self.current_field < len(self.form_fields):
                    self.filling_field = True
                    self.fill_timer = self.fill_duration

        return True

    def update(self, dt):
        """Update application state"""
        if not self.active:
            return

        # Update particles and feedback
        self.particles.update(dt)
        self.feedback.update(dt)

        # Animation updates
        self.loading_angle += dt * 5
        self.cursor_blink = (self.cursor_blink + dt * 3) % 2

        if self.has_crashed:
            self.error_timer += 1
            self.crash_shake = max(0, self.crash_shake - dt * 3)

            # Continuous glitch effect
            if self.glitch_intensity > 0:
                self.glitch_intensity = max(0, self.glitch_intensity - dt * 2)
                if random.random() < 0.3:
                    self.particles.emit_glitch_effect(self.browser_rect.height, 2)
            return

        # Update field filling
        if self.filling_field:
            self.fill_timer -= 1

            # Emit typing particles
            if self.fill_timer % 10 == 0:
                field_y = self.browser_rect.y + 180 + self.current_field * 40
                self.particles.emit_typing_cursor(
                    self.browser_rect.x + 450,
                    field_y
                )

            if self.fill_timer <= 0:
                field = self.form_fields[self.current_field]
                field['filled'] = True
                self.progress += field['progress']
                self.current_field += 1
                self.filling_field = False

                # Check for crash
                if self.progress >= self.crash_point:
                    self.trigger_crash()

    def trigger_crash(self):
        """Trigger the website crash"""
        self.has_crashed = True
        self.current_error = random.choice(self.error_messages)
        self.error_timer = 0
        self.crash_shake = 1.0
        self.glitch_intensity = 1.0

        # Trigger crash effects
        self.particles.trigger_crash_effect(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.feedback.add_crash_banner()

    def render(self, screen):
        """Render the online application interface"""
        if not self.active:
            return

        # Background
        screen.fill(SystemicUIColors.BACKGROUND_LIGHT)

        # Apply shake offset
        shake_x = int(random.uniform(-8, 8) * self.crash_shake) if self.crash_shake > 0 else 0
        shake_y = int(random.uniform(-8, 8) * self.crash_shake) if self.crash_shake > 0 else 0

        # Browser window with shake
        browser_rect = self.browser_rect.copy()
        browser_rect.x += shake_x
        browser_rect.y += shake_y

        # Draw browser chrome
        content_rect = self.visuals.draw_browser_chrome(
            screen, browser_rect,
            url="https://benefits.ca.gov/apply-online"
        )

        if not self.has_crashed:
            self._render_form(screen, content_rect)
            self._render_progress_bar(screen)
        else:
            self._render_error(screen, content_rect)

        # Particles and feedback
        self.particles.render(screen)
        self.feedback.render(screen)

    def _render_form(self, screen, content_rect):
        """Render the application form"""
        # Form title
        title = self.font_title.render("California Benefits Application", True,
                                       SystemicUIColors.GOVERNMENT_BLUE)
        screen.blit(title, (content_rect.centerx - title.get_width() // 2,
                           content_rect.y + 20))

        # Subtitle
        subtitle = self.font_small.render("Complete all fields to submit your application",
                                         True, SystemicUIColors.TEXT_SECONDARY)
        screen.blit(subtitle, (content_rect.centerx - subtitle.get_width() // 2,
                              content_rect.y + 55))

        # Form fields
        field_start_y = content_rect.y + 95
        field_x = content_rect.x + 80

        for i, field in enumerate(self.form_fields):
            y = field_start_y + i * 42
            self._render_field(screen, field, field_x, y, i)

        # Next button hint
        if self.current_field < len(self.form_fields) and not self.filling_field:
            hint = self.font_small.render("Click or press Enter to fill next field",
                                         True, SystemicUIColors.TEXT_MUTED)
            screen.blit(hint, (content_rect.centerx - hint.get_width() // 2,
                              content_rect.bottom - 40))

    def _render_field(self, screen, field, x, y, index):
        """Render a single form field"""
        # Icon
        try:
            icon_text = self.font_icon.render(field['icon'], True, SystemicUIColors.TEXT_SECONDARY)
            screen.blit(icon_text, (x, y + 2))
        except:
            pass

        # Label
        label_color = SystemicUIColors.APPROVAL_GREEN if field['filled'] else SystemicUIColors.TEXT_PRIMARY
        label = self.font_body.render(f"{field['label']}:", True, label_color)
        screen.blit(label, (x + 30, y))

        # Input field
        field_rect = pygame.Rect(x + 180, y - 3, 280, 30)

        if field['filled']:
            # Filled field
            pygame.draw.rect(screen, (235, 250, 235), field_rect,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, SystemicUIColors.APPROVAL_GREEN, field_rect, 1,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)

            # Value
            value = "********" if field['label'] == 'SSN' else "Completed"
            value_text = self.font_mono.render(value, True, SystemicUIColors.APPROVAL_GREEN)
            screen.blit(value_text, (field_rect.x + 10, field_rect.y + 6))

            # Checkmark
            check = self.font_body.render("✓", True, SystemicUIColors.APPROVAL_GREEN)
            screen.blit(check, (field_rect.right + 10, field_rect.y + 3))

        elif index == self.current_field and self.filling_field:
            # Currently filling
            pygame.draw.rect(screen, (255, 255, 240), field_rect,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, SystemicUIColors.GOVERNMENT_BLUE, field_rect, 2,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)

            # Typing animation
            fill_progress = 1 - (self.fill_timer / self.fill_duration)
            chars = int(fill_progress * 12)
            typing_text = "█" * chars
            if self.cursor_blink < 1:
                typing_text += "│"

            text_surface = self.font_mono.render(typing_text, True,
                                                SystemicUIColors.GOVERNMENT_BLUE)
            screen.blit(text_surface, (field_rect.x + 10, field_rect.y + 6))

            # Loading spinner
            self._render_loading_spinner(screen, field_rect.right + 15, field_rect.centery)

        elif index == self.current_field:
            # Next field to fill (highlighted)
            pygame.draw.rect(screen, (250, 250, 255), field_rect,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, SystemicUIColors.GOVERNMENT_BLUE_LIGHT, field_rect, 2,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)

            placeholder = self.font_small.render("Click to fill...", True,
                                                SystemicUIColors.TEXT_MUTED)
            screen.blit(placeholder, (field_rect.x + 10, field_rect.y + 8))

        else:
            # Empty field
            pygame.draw.rect(screen, (252, 252, 252), field_rect,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT, field_rect, 1,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)

    def _render_loading_spinner(self, screen, x, y):
        """Render a small loading spinner"""
        radius = 8
        for i in range(8):
            angle = self.loading_angle + i * (math.pi / 4)
            alpha = int(255 * (1 - i / 8))
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius

            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*SystemicUIColors.GOVERNMENT_BLUE, alpha), (3, 3), 3)
            screen.blit(surf, (int(px) - 3, int(py) - 3))

    def _render_progress_bar(self, screen):
        """Render the progress bar"""
        bar_rect = pygame.Rect(340, 650, 600, 35)

        # Background
        pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT, bar_rect,
                        border_radius=bar_rect.height // 2)

        # Fill
        if self.progress > 0:
            fill_width = int((bar_rect.width - 4) * (self.progress / self.max_progress))
            fill_rect = pygame.Rect(bar_rect.x + 2, bar_rect.y + 2,
                                   fill_width, bar_rect.height - 4)

            # Color gradient based on progress
            if self.progress < 70:
                fill_color = SystemicUIColors.LOADING_GREEN
            elif self.progress < 85:
                fill_color = SystemicUIColors.WARNING_ORANGE
            else:
                fill_color = SystemicUIColors.ERROR_RED

            pygame.draw.rect(screen, fill_color, fill_rect,
                           border_radius=(bar_rect.height - 4) // 2)

        # Border
        pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY, bar_rect, 2,
                        border_radius=bar_rect.height // 2)

        # Percentage text
        percent_text = f"{int(self.progress)}% Complete"
        text_surface = self.font_body.render(percent_text, True, SystemicUIColors.TEXT_LIGHT)
        screen.blit(text_surface, (bar_rect.centerx - text_surface.get_width() // 2,
                                  bar_rect.centery - text_surface.get_height() // 2))

        # Processing indicator
        if self.filling_field:
            proc_text = "Processing..."
            dots = "." * (int(time.time() * 3) % 4)
            proc_surface = self.font_small.render(f"Processing{dots}", True,
                                                 SystemicUIColors.TEXT_SECONDARY)
            screen.blit(proc_surface, (bar_rect.x, bar_rect.y - 22))

    def _render_error(self, screen, content_rect):
        """Render the crash error screen"""
        # Glitchy background
        if self.glitch_intensity > 0 and random.random() < 0.3:
            # Random color blocks
            for _ in range(3):
                glitch_rect = pygame.Rect(
                    content_rect.x + random.randint(0, content_rect.width - 100),
                    content_rect.y + random.randint(0, content_rect.height - 20),
                    random.randint(50, 200),
                    random.randint(5, 15)
                )
                glitch_color = random.choice([
                    SystemicUIColors.ERROR_RED,
                    (50, 255, 50),
                    (50, 50, 255)
                ])
                pygame.draw.rect(screen, glitch_color, glitch_rect)

        # Error panel
        error_rect = pygame.Rect(
            content_rect.centerx - 350,
            content_rect.centery - 130,
            700,
            260
        )

        # Shadow
        SystemicVisualHelpers.draw_shadow(screen, error_rect, 15, 80,
                                         SystemicUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, (255, 245, 245), error_rect,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Red header
        header_rect = pygame.Rect(error_rect.x, error_rect.y, error_rect.width, 55)
        pygame.draw.rect(screen, SystemicUIColors.ERROR_RED, header_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Error icon
        icon_text = self.font_title.render("⚠", True, SystemicUIColors.TEXT_LIGHT)
        screen.blit(icon_text, (error_rect.x + 20, error_rect.y + 10))

        # Error title
        title_text = self.font_heading.render("Connection Failed", True,
                                             SystemicUIColors.TEXT_LIGHT)
        screen.blit(title_text, (error_rect.x + 60, error_rect.y + 15))

        # Error message
        error_text = self.font_body.render(self.current_error, True,
                                          SystemicUIColors.ERROR_RED)
        screen.blit(error_text, (error_rect.centerx - error_text.get_width() // 2,
                                error_rect.y + 80))

        # Impact messages
        messages = [
            "Your application data has been lost.",
            "You will need to start over from the beginning.",
            "This happens frequently to many users."
        ]

        y = error_rect.y + 120
        for msg in messages:
            msg_surface = self.font_small.render(msg, True, SystemicUIColors.TEXT_SECONDARY)
            screen.blit(msg_surface, (error_rect.centerx - msg_surface.get_width() // 2, y))
            y += 25

        # Continue prompt
        if self.error_timer > 60:
            prompt = "Press any key to continue..."
            prompt_surface = self.font_small.render(prompt, True, SystemicUIColors.TEXT_MUTED)
            screen.blit(prompt_surface, (error_rect.centerx - prompt_surface.get_width() // 2,
                                        error_rect.bottom - 35))

        # Border
        pygame.draw.rect(screen, SystemicUIColors.ERROR_RED, error_rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the online application"""
        self.active = True
        self.completed = False
        self.has_crashed = False
        self.progress = 0.0
        self.current_field = 0
        self.filling_field = False
        self.current_error = None
        self.error_timer = 0
        self.crash_shake = 0
        self.glitch_intensity = 0

        # Reset form
        for field in self.form_fields:
            field['filled'] = False

        # Clear effects
        self.particles.clear()
        self.feedback.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

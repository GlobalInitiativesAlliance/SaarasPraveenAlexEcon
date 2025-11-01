"""
Online Application Crash Simulation
Government website that always crashes at 90% completion
Demonstrates digital barriers and system failures
"""
import pygame
import random

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
        self.crash_point = 88.0  # Crash at 88%
        self.has_crashed = False

        # Form fields (simulate filling)
        self.form_fields = [
            {'label': 'First Name', 'filled': False, 'progress': 10},
            {'label': 'Last Name', 'filled': False, 'progress': 10},
            {'label': 'Date of Birth', 'filled': False, 'progress': 10},
            {'label': 'SSN', 'filled': False, 'progress': 15},
            {'label': 'Address', 'filled': False, 'progress': 10},
            {'label': 'Phone', 'filled': False, 'progress': 10},
            {'label': 'Income', 'filled': False, 'progress': 15},
            {'label': 'Household Size', 'filled': False, 'progress': 10},
            {'label': 'Foster Status', 'filled': False, 'progress': 10},
        ]

        self.current_field = 0
        self.filling_field = False
        self.fill_timer = 0

        # Website UI
        self.browser_rect = pygame.Rect(140, 100, 1000, 520)
        self.progress_bar_rect = pygame.Rect(340, 550, 600, 30)

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

        # Loading animation
        self.loading_dots = 0
        self.loading_timer = 0

    def handle_event(self, event):
        """Handle form interaction"""
        if not self.active or self.completed:
            return False

        if self.has_crashed:
            # Can only continue after crash
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.completed = True
                if self.objective_manager:
                    self.objective_manager.complete_objective("online_application")
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.filling_field and self.current_field < len(self.form_fields):
                # Start filling next field
                self.filling_field = True
                self.fill_timer = 60  # 1 second to fill

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not self.filling_field:
                if self.current_field < len(self.form_fields):
                    self.filling_field = True
                    self.fill_timer = 60

        return True

    def update(self, dt):
        """Update application state"""
        if not self.active:
            return

        if self.has_crashed:
            # Update error display
            self.error_timer += 1
            return

        # Update field filling
        if self.filling_field:
            self.fill_timer -= 1
            if self.fill_timer <= 0:
                # Field filled
                field = self.form_fields[self.current_field]
                field['filled'] = True
                self.progress += field['progress']
                self.current_field += 1
                self.filling_field = False

                # Check for crash
                if self.progress >= self.crash_point:
                    self.trigger_crash()

        # Update loading animation
        self.loading_timer += 1
        if self.loading_timer >= 20:
            self.loading_timer = 0
            self.loading_dots = (self.loading_dots + 1) % 4

    def trigger_crash(self):
        """Trigger the website crash"""
        self.has_crashed = True
        self.current_error = random.choice(self.error_messages)
        self.error_timer = 0

    def render(self, screen):
        """Render the online application interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)
        overlay.fill((230, 230, 235))
        screen.blit(overlay, (0, 0))

        # Browser window
        pygame.draw.rect(screen, (255, 255, 255), self.browser_rect)
        pygame.draw.rect(screen, (180, 180, 190), self.browser_rect, 2)

        # Browser header
        header_rect = pygame.Rect(self.browser_rect.x, self.browser_rect.y, self.browser_rect.width, 40)
        pygame.draw.rect(screen, (240, 240, 245), header_rect)
        pygame.draw.rect(screen, (180, 180, 190), header_rect, 1)

        # URL bar
        url_font = pygame.font.Font(None, 20)
        url_text = "https://benefits.ca.gov/apply-online"
        url_surface = url_font.render(url_text, True, (100, 100, 110))
        screen.blit(url_surface, (header_rect.x + 50, header_rect.y + 12))

        if not self.has_crashed:
            # Application form
            self.render_form(screen)

            # Progress bar
            self.render_progress_bar(screen)

        else:
            # Error screen
            self.render_error(screen)

    def render_form(self, screen):
        """Render the application form"""
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("California Benefits Application", True, (30, 30, 40))
        title_x = self.browser_rect.centerx - title_text.get_width() // 2
        screen.blit(title_text, (title_x, self.browser_rect.y + 60))

        # Form fields
        field_font = pygame.font.Font(None, 24)
        y_offset = 120

        for i, field in enumerate(self.form_fields):
            x = self.browser_rect.x + 200
            y = self.browser_rect.y + y_offset

            # Field label
            label_color = (50, 150, 50) if field['filled'] else (30, 30, 40)
            label = field['label'] + ":"
            label_surface = field_font.render(label, True, label_color)
            screen.blit(label_surface, (x, y))

            # Field box
            field_rect = pygame.Rect(x + 150, y - 2, 300, 28)
            if field['filled']:
                pygame.draw.rect(screen, (230, 255, 230), field_rect)
                value = "*" * 8 if field['label'] == 'SSN' else "Completed"
                value_surface = field_font.render(value, True, (50, 150, 50))
                screen.blit(value_surface, (field_rect.x + 10, field_rect.y + 4))
            elif i == self.current_field and self.filling_field:
                pygame.draw.rect(screen, (255, 255, 230), field_rect)
                # Show typing animation
                dots = "." * (3 - (self.fill_timer // 20))
                typing_surface = field_font.render(f"Filling{dots}", True, (100, 100, 110))
                screen.blit(typing_surface, (field_rect.x + 10, field_rect.y + 4))
            else:
                pygame.draw.rect(screen, (250, 250, 250), field_rect)

            pygame.draw.rect(screen, (180, 180, 190), field_rect, 1)

            y_offset += 40

        # Next button hint
        if self.current_field < len(self.form_fields) and not self.filling_field:
            hint_font = pygame.font.Font(None, 22)
            hint = "Click or press Enter to fill next field"
            hint_surface = hint_font.render(hint, True, (100, 100, 120))
            hint_x = self.browser_rect.centerx - hint_surface.get_width() // 2
            screen.blit(hint_surface, (hint_x, self.browser_rect.y + 480))

    def render_progress_bar(self, screen):
        """Render the progress bar"""
        # Background
        pygame.draw.rect(screen, (220, 220, 230), self.progress_bar_rect)

        # Progress fill
        fill_width = int((self.progress / self.max_progress) * self.progress_bar_rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(
                self.progress_bar_rect.x,
                self.progress_bar_rect.y,
                fill_width,
                self.progress_bar_rect.height
            )
            # Color changes as it gets closer to crash
            if self.progress < 70:
                color = (100, 200, 100)
            elif self.progress < 85:
                color = (200, 200, 100)
            else:
                color = (200, 100, 100)

            pygame.draw.rect(screen, color, fill_rect)

        # Border
        pygame.draw.rect(screen, (100, 100, 110), self.progress_bar_rect, 2)

        # Percentage text
        percent_font = pygame.font.Font(None, 24)
        percent_text = f"{int(self.progress)}% Complete"
        percent_surface = percent_font.render(percent_text, True, (30, 30, 40))
        text_x = self.progress_bar_rect.centerx - percent_surface.get_width() // 2
        text_y = self.progress_bar_rect.centery - percent_surface.get_height() // 2
        screen.blit(percent_surface, (text_x, text_y))

        # Loading dots
        if self.filling_field:
            dots = "." * self.loading_dots
            loading_text = f"Processing{dots}"
            loading_surface = percent_font.render(loading_text, True, (100, 100, 110))
            screen.blit(loading_surface, (self.progress_bar_rect.x, self.progress_bar_rect.y - 25))

    def render_error(self, screen):
        """Render the crash error screen"""
        # Error box
        error_rect = pygame.Rect(
            self.browser_rect.x + 150,
            self.browser_rect.y + 150,
            700,
            250
        )
        pygame.draw.rect(screen, (255, 240, 240), error_rect)
        pygame.draw.rect(screen, (255, 100, 100), error_rect, 3)

        # Error icon
        icon_font = pygame.font.Font(None, 72)
        icon_text = "⚠"
        icon_surface = icon_font.render(icon_text, True, (255, 50, 50))
        icon_x = error_rect.centerx - icon_surface.get_width() // 2
        screen.blit(icon_surface, (icon_x, error_rect.y + 20))

        # Error message
        error_font = pygame.font.Font(None, 32)
        error_surface = error_font.render(self.current_error, True, (200, 50, 50))
        error_x = error_rect.centerx - error_surface.get_width() // 2
        screen.blit(error_surface, (error_x, error_rect.y + 100))

        # Additional messages
        msg_font = pygame.font.Font(None, 24)
        messages = [
            "Your application data has been lost.",
            "You will need to start over.",
            "This happens frequently to many users."
        ]

        y = error_rect.y + 150
        for msg in messages:
            msg_surface = msg_font.render(msg, True, (100, 50, 50))
            msg_x = error_rect.centerx - msg_surface.get_width() // 2
            screen.blit(msg_surface, (msg_x, y))
            y += 30

        # Continue prompt
        if self.error_timer > 60:
            prompt = "Press any key to continue..."
            prompt_surface = msg_font.render(prompt, True, (100, 100, 110))
            prompt_x = error_rect.centerx - prompt_surface.get_width() // 2
            screen.blit(prompt_surface, (prompt_x, error_rect.bottom - 40))

    def start(self):
        """Start the online application"""
        self.active = True
        self.completed = False
        self.has_crashed = False
        self.progress = 0.0
        self.current_field = 0
        self.filling_field = False
        self.current_error = None

        # Reset form
        for field in self.form_fields:
            field['filled'] = False

    def stop(self):
        """Stop the mini-game"""
        self.active = False
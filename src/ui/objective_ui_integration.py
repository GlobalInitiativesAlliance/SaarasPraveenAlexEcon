import pygame
from src.ui.modern_objective_ui import ModernObjectiveUI, UITheme

class ObjectiveUIManager:
    """Manages the integration of modern UI with the game's objective system"""

    def __init__(self, game):
        self.game = game
        # Import constants to get screen dimensions
        from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        self.modern_ui = ModernObjectiveUI(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Track UI state
        self.ui_initialized = False
        self.last_objective_id = None
        self.theme_index = 0

        # Animation timers
        self.intro_played = False

    def switch_theme(self):
        """Toggle between available themes"""
        themes = [UITheme.DARK_GLASS, UITheme.CYBERPUNK]
        self.theme_index = (self.theme_index + 1) % len(themes)
        self.modern_ui.theme = themes[self.theme_index].value

    def update(self, dt):
        """Update UI animations and states"""
        if not self.ui_initialized and self.game.objective_manager.get_current_objective():
            self.modern_ui.animate_in()
            self.ui_initialized = True

        # Check for objective changes
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id != self.last_objective_id:
            self.last_objective_id = current_obj.id
            # Show notification for new objective
            self.modern_ui.show_notification(
                "NEW OBJECTIVE",
                current_obj.title,
                'info'
            )

    def draw(self, screen):
        """Draw the modern UI elements"""
        objective_manager = self.game.objective_manager
        current_objective = objective_manager.get_current_objective()

        if not current_objective:
            return

        # Don't draw during notifications or activities
        if objective_manager.showing_notification:
            self.draw_notification_screen(screen, objective_manager)
            return

        if objective_manager.current_activity and objective_manager.current_activity.active:
            return

        # Prepare objective data
        objective_data = {
            'part': objective_manager.game_part,
            'time': objective_manager.game_time,
            'title': current_objective.title,
            'description': current_objective.description,
            'progress': (objective_manager.current_objective_index + 1) / len(objective_manager.objectives)
        }

        # Draw the modern objective panel
        self.modern_ui.draw_objective_panel(screen, objective_data)

        # Draw notifications
        self.modern_ui.draw_notifications(screen)

        # Draw interaction prompt if near objective
        if self.game.player_near_objective and not self.game.current_interior:
            self.modern_ui.draw_interaction_prompt(
                screen,
                current_objective.interaction_text
            )

    def draw_notification_screen(self, screen, objective_manager):
        """Draw fullscreen notification with modern styling"""
        # Darken background
        from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((10, 10, 15))
        screen.blit(overlay, (0, 0))

        # Create notification panel
        panel_width = 600
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        # Use modern UI panel
        panel = self.modern_ui.create_glass_panel(panel_width, panel_height, 240)
        screen.blit(panel, (panel_x, panel_y))

        # Draw notification content
        title_font = pygame.font.Font(None, 36)
        body_font = pygame.font.Font(None, 24)

        # Title with gradient effect
        title = title_font.render("STORY UPDATE", True, self.modern_ui.theme['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 50))
        screen.blit(title, title_rect)

        # Notification text with word wrap
        text_lines = self.wrap_text(objective_manager.notification_text, body_font, panel_width - 100)
        y_offset = panel_y + 120

        for line in text_lines[:8]:  # Max 8 lines
            text_surface = body_font.render(line, True, self.modern_ui.theme['text_primary'])
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 35

        # Continue prompt
        prompt_text = "Press E to continue"
        prompt_font = pygame.font.Font(None, 20)
        prompt_surface = prompt_font.render(prompt_text, True, self.modern_ui.theme['text_secondary'])
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 40))

        # Pulsing effect
        import math
        import time
        pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5
        prompt_surface.set_alpha(int(255 * pulse))
        screen.blit(prompt_surface, prompt_rect)

    def wrap_text(self, text, font, max_width):
        """Word wrap text for display"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def handle_click(self, pos):
        """Handle mouse clicks on UI elements"""
        # Check if skip button was clicked
        current_objective = self.game.objective_manager.get_current_objective()
        if not current_objective:
            return False

        # Skip button bounds (from modern_objective_ui)
        skip_x = 30 + 380 - 100  # panel_x + panel_width - 100
        skip_y = self.modern_ui.panel_y + 20
        skip_width = 80
        skip_height = 32

        if (skip_x <= pos[0] <= skip_x + skip_width and
            skip_y <= pos[1] <= skip_y + skip_height):
            self.game.objective_manager.skip_to_next_objective()
            return True

        return False
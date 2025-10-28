import pygame
import math
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

        # Navigation data
        self.player_pos = None
        self.target_pos = None
        self.direction = None
        self.distance = None

    def calculate_navigation(self, player_x, player_y, target_x, target_y):
        """Calculate direction and distance to target"""
        if target_x is None or target_y is None:
            self.direction = None
            self.distance = None
            return

        # Calculate distance in tiles
        dx = target_x - player_x
        dy = target_y - player_y
        self.distance = math.sqrt(dx * dx + dy * dy)

        # Calculate direction (8-way compass)
        if self.distance > 0:
            # Get angle in degrees
            angle = math.degrees(math.atan2(-dy, dx))  # Negative dy for screen coordinates
            # Normalize to 0-360
            angle = (angle + 360) % 360

            # Convert to 8-way compass direction
            if angle <= 22.5 or angle > 337.5:
                self.direction = "E"
                self.direction_arrow = "→"
            elif angle <= 67.5:
                self.direction = "NE"
                self.direction_arrow = "↗"
            elif angle <= 112.5:
                self.direction = "N"
                self.direction_arrow = "↑"
            elif angle <= 157.5:
                self.direction = "NW"
                self.direction_arrow = "↖"
            elif angle <= 202.5:
                self.direction = "W"
                self.direction_arrow = "←"
            elif angle <= 247.5:
                self.direction = "SW"
                self.direction_arrow = "↙"
            elif angle <= 292.5:
                self.direction = "S"
                self.direction_arrow = "↓"
            else:
                self.direction = "SE"
                self.direction_arrow = "↘"
        else:
            self.direction = "HERE"
            self.direction_arrow = "◉"

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

        # Update navigation data if objective has a position
        if hasattr(current_objective, 'target_position') and current_objective.target_position:
            target_x, target_y = current_objective.target_position
            self.calculate_navigation(
                self.game.player.x,
                self.game.player.y,
                target_x,
                target_y
            )

        # Prepare objective data with navigation info
        # Use get_display_text() for dynamic descriptions
        description_text = current_objective.get_display_text() if hasattr(current_objective, 'get_display_text') else current_objective.description

        # Add progress text if available
        if hasattr(current_objective, 'progress_text') and current_objective.progress_text:
            description_text = f"{description_text} - {current_objective.progress_text}"

        objective_data = {
            'part': objective_manager.game_part,
            'time': objective_manager.game_time,
            'title': current_objective.title,
            'description': description_text,
            'progress': (objective_manager.current_objective_index + 1) / len(objective_manager.objectives),
            'direction': self.direction,
            'direction_arrow': getattr(self, 'direction_arrow', None),
            'distance': self.distance
        }

        # Draw the modern objective panel
        self.modern_ui.draw_objective_panel(screen, objective_data)

        # Draw navigation indicator
        self.draw_navigation_indicator(screen)

        # Draw notifications
        self.modern_ui.draw_notifications(screen)

        # Draw interaction prompt if near objective
        if self.game.player_near_objective and not self.game.current_interior:
            self.modern_ui.draw_interaction_prompt(
                screen,
                current_objective.interaction_text
            )

    def draw_navigation_indicator(self, screen):
        """Draw navigation compass/arrow indicator in the UI"""
        if not self.direction or not self.distance:
            return

        from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

        # Position in top-left panel area, below objective text
        nav_x = 30
        nav_y = 160

        # Navigation background panel
        panel_width = 180
        panel_height = 60

        # Semi-transparent background
        nav_panel = pygame.Surface((panel_width, panel_height))
        nav_panel.set_alpha(230)
        nav_panel.fill((25, 25, 30))
        screen.blit(nav_panel, (nav_x, nav_y))

        # Border
        pygame.draw.rect(screen, (100, 100, 120), (nav_x, nav_y, panel_width, panel_height), 2, border_radius=6)

        # Navigation label
        nav_font = pygame.font.Font(None, 16)
        label_text = nav_font.render("NAVIGATION", True, (150, 150, 150))
        screen.blit(label_text, (nav_x + 10, nav_y + 5))

        # Direction arrow and text
        arrow_font = pygame.font.Font(None, 28)
        direction_font = pygame.font.Font(None, 20)

        # Draw arrow with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.3 + 0.7
        arrow_color = (int(255 * pulse), int(220 * pulse), int(100 * pulse))

        arrow_text = arrow_font.render(self.direction_arrow, True, arrow_color)
        arrow_x = nav_x + 20
        arrow_y = nav_y + 22
        screen.blit(arrow_text, (arrow_x, arrow_y))

        # Direction text
        dir_text = direction_font.render(self.direction, True, (255, 255, 200))
        screen.blit(dir_text, (arrow_x + 35, arrow_y + 4))

        # Distance text
        if self.distance < 2:
            distance_str = "Arrived!"
            distance_color = (100, 255, 100)
        else:
            distance_str = f"{int(self.distance)}m away"
            distance_color = (200, 200, 200)

        distance_font = pygame.font.Font(None, 18)
        distance_text = distance_font.render(distance_str, True, distance_color)
        screen.blit(distance_text, (arrow_x + 80, arrow_y + 5))

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
"""
Unified UI Manager for Economics Adventure
Integrates the collapsible UI system with the game
"""

import pygame
from src.ui.collapsible_ui import CollapsibleUI
from src.ui.professional_ui import InteractionPrompt, NotificationToast
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class GameUIManager:
    """Manages all UI elements for the game"""

    def __init__(self, game):
        self.game = game

        # Initialize UI components with new collapsible UI
        self.objective_panel = CollapsibleUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.objective_panel.game = game  # Pass game reference for counter
        self.interaction_prompt = InteractionPrompt()
        self.notifications = NotificationToast(SCREEN_WIDTH, SCREEN_HEIGHT)

        # State tracking
        self.ui_initialized = False
        self.last_objective_id = None
        self.skip_button_rect = None

        # Debug panel visibility
        self.show_debug = False  # Can be toggled with Y key

    def handle_click(self, pos):
        """Handle mouse clicks and return True if handled"""
        # Check collapsible UI panel for navigation clicks
        print(f"[UI_MANAGER] handle_click called with pos: {pos}")
        action = self.objective_panel.handle_click(pos)
        print(f"[UI_MANAGER] objective_panel returned action: {action}")

        if action == 'prev':
            # Go to previous objective
            if self.game.objective_manager.current_objective_index > 0:
                print(f"[NAV] Going to previous objective from {self.game.objective_manager.current_objective_index}")
                self.game.objective_manager.current_objective_index -= 1
                self.game.objective_manager.activate_current_objective()
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj:
                    print(f"[NAV] Now at objective {self.game.objective_manager.current_objective_index}: {current_obj.title}")
                    self.notifications.show(
                        "Previous Objective",
                        current_obj.title,
                        'info'
                    )
            else:
                self.notifications.show(
                    "Beginning",
                    "You're at the start of the story",
                    'warning'
                )
            return True
        elif action == 'next':
            # Go to next objective
            current_obj = self.game.objective_manager.get_current_objective()

            # Special case: if we're on the last objective of Part 1, skip to Part 2
            if (self.game.objective_manager.game_part == 1 and
                self.game.objective_manager.current_objective_index == len(self.game.objective_manager.objectives) - 1):
                print(f"[NAV] Last objective of Part 1, skipping to Part 2")
                self.game.objective_manager.skip_to_part2()
                self.notifications.show(
                    "Part 2",
                    "Welcome to Part 2!",
                    'success'
                )
            elif self.game.objective_manager.current_objective_index < len(self.game.objective_manager.objectives) - 1:
                print(f"[NAV] Going to next objective from {self.game.objective_manager.current_objective_index}")
                self.game.objective_manager.skip_to_next_objective()
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj:
                    print(f"[NAV] Now at objective {self.game.objective_manager.current_objective_index}: {current_obj.title}")
                    self.notifications.show(
                        "Next Objective",
                        current_obj.title,
                        'info'
                    )
            else:
                self.notifications.show(
                    "End",
                    f"You've reached the end of Part {self.game.objective_manager.game_part}",
                    'warning'
                )
            return True
        elif action == 'toggle':
            # Panel was toggled
            return True

        return False

    def initialize(self):
        """Initialize UI when game starts"""
        if not self.ui_initialized:
            # Collapsible UI doesn't need explicit show
            self.ui_initialized = True
            self.notifications.show(
                "Welcome",
                "Your journey begins...",
                'info'
            )

    def update(self, dt):
        """Update all UI elements"""
        # Update components
        self.objective_panel.update(dt)
        self.interaction_prompt.update(dt)
        self.notifications.update(dt)

        # Check for objective changes
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj:
            # Initialize if needed
            if not self.ui_initialized:
                self.initialize()

            # Check for objective change
            if current_obj.id != self.last_objective_id:
                self.last_objective_id = current_obj.id
                self.notifications.show(
                    "New Objective",
                    current_obj.title,
                    'info'
                )

            # Update interaction prompt
            if self.game.player_near_objective and not self.game.current_interior:
                self.interaction_prompt.show(current_obj.interaction_text)
            else:
                self.interaction_prompt.hide()

    def draw(self, screen):
        """Draw all UI elements"""
        objective_manager = self.game.objective_manager
        current_objective = objective_manager.get_current_objective()

        if not current_objective:
            return

        # Skip drawing during certain states
        if objective_manager.showing_notification:
            self.draw_notification_overlay(screen, objective_manager)
            return

        # Skip drawing during activities (except transition scenes which should show UI)
        if objective_manager.current_activity and objective_manager.current_activity.active:
            from src.activities.activities import TransitionScene
            # Allow UI to show during transition scenes
            if not isinstance(objective_manager.current_activity, TransitionScene):
                return

        # Prepare objective data - ALWAYS get fresh data
        current_idx = objective_manager.current_objective_index
        # Use get_current_objective which returns the ACTUAL current objective
        fresh_objective = objective_manager.get_current_objective()
        if not fresh_objective:
            return

        objective_data = {
            'part': objective_manager.game_part,
            'day': objective_manager.current_day,
            'time': objective_manager.game_time,
            'title': fresh_objective.title,
            'description': fresh_objective.description,
            'progress': (current_idx + 1) / len(objective_manager.objectives),
            'index': current_idx  # Add index for debugging
        }

        # Debug print to see if objective changes
        if not hasattr(self, '_last_debug_idx') or self._last_debug_idx != current_idx:
            print(f"Drawing objective {current_idx}: {fresh_objective.title}")
            self._last_debug_idx = current_idx

        # Draw main objective panel with new collapsible UI
        self.objective_panel.draw(screen, objective_data)
        self.skip_button_rect = None  # Collapsible UI handles its own interactions

        # Draw interaction prompt if near objective
        if self.game.player_near_objective and not self.game.current_interior:
            player_screen_x = self.game.player.pixel_x - self.game.camera_x
            player_screen_y = self.game.player.pixel_y - self.game.camera_y - 60
            self.interaction_prompt.draw(screen, player_screen_x, player_screen_y)

        # Draw notifications
        self.notifications.draw(screen)

        # Debug panel disabled - removed from UI
        # if self.show_debug:
        #     self.draw_debug_panel(screen)

    def draw_notification_overlay(self, screen, objective_manager):
        """Draw fullscreen story notification"""
        from src.ui.professional_ui import UIColors, UIMetrics

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((10, 12, 15))
        screen.blit(overlay, (0, 0))

        # Notification panel
        panel_width = 640
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        # Panel background
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        # Shadow
        for i in range(4):
            alpha = 40 - i * 10
            shadow_rect = pygame.Rect(
                4 + i, 4 + i,
                panel_width - i * 2, panel_height - i * 2
            )
            pygame.draw.rect(
                panel_surf,
                (10, 12, 15, alpha),
                shadow_rect,
                border_radius=UIMetrics.RADIUS_LARGE
            )

        # Main panel
        pygame.draw.rect(
            panel_surf,
            UIColors.PANEL_BG,
            panel_surf.get_rect(),
            border_radius=UIMetrics.RADIUS_LARGE
        )

        # Border
        pygame.draw.rect(
            panel_surf,
            UIColors.PANEL_BORDER,
            panel_surf.get_rect(),
            width=2,
            border_radius=UIMetrics.RADIUS_LARGE
        )

        # Header accent
        pygame.draw.rect(
            panel_surf,
            UIColors.BUTTON_ACTIVE,
            pygame.Rect(40, 0, panel_width - 80, 3)
        )

        screen.blit(panel_surf, (panel_x, panel_y))

        # Content
        title_font = pygame.font.Font(None, 32)
        body_font = pygame.font.Font(None, 20)
        prompt_font = pygame.font.Font(None, 16)

        # Title
        title = title_font.render("STORY UPDATE", True, UIColors.BUTTON_ACTIVE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 50))
        screen.blit(title, title_rect)

        # Divider
        pygame.draw.line(
            screen,
            UIColors.PANEL_ACCENT,
            (panel_x + 60, panel_y + 80),
            (panel_x + panel_width - 60, panel_y + 80),
            1
        )

        # Story text (wrapped)
        text_lines = self.wrap_notification_text(
            objective_manager.notification_text,
            body_font,
            panel_width - 120
        )

        y_offset = panel_y + 110
        for line in text_lines[:10]:  # Max 10 lines
            text_surf = body_font.render(line, True, UIColors.TEXT_PRIMARY)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 28

        # Continue prompt with pulsing
        import math, time
        pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5
        prompt_color = (
            UIColors.TEXT_SECONDARY[0],
            UIColors.TEXT_SECONDARY[1],
            UIColors.TEXT_SECONDARY[2]
        )

        # Key indicator
        key_bg = pygame.Surface((100, 32), pygame.SRCALPHA)
        key_rect = key_bg.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 50))

        pygame.draw.rect(
            key_bg,
            (*UIColors.BUTTON_DEFAULT, int(200 * pulse)),
            key_bg.get_rect(),
            border_radius=16
        )
        pygame.draw.rect(
            key_bg,
            (*UIColors.BUTTON_ACTIVE, int(255 * pulse)),
            key_bg.get_rect(),
            width=2,
            border_radius=16
        )

        screen.blit(key_bg, key_rect)

        prompt_text = "Press E"
        prompt_surf = prompt_font.render(prompt_text, True, UIColors.TEXT_PRIMARY)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 50))
        screen.blit(prompt_surf, prompt_rect)

    def draw_debug_panel(self, screen):
        """Draw debug information panel"""
        from src.ui.professional_ui import UIColors, UIMetrics

        # Only draw if debug mode is on
        if not self.show_debug:
            return

        # Debug panel dimensions
        debug_width = 200
        debug_height = 120
        debug_x = SCREEN_WIDTH - debug_width - UIMetrics.MARGIN
        debug_y = UIMetrics.MARGIN + UIMetrics.PANEL_HEIGHT + UIMetrics.PADDING

        # Semi-transparent background
        debug_surf = pygame.Surface((debug_width, debug_height), pygame.SRCALPHA)
        pygame.draw.rect(
            debug_surf,
            (*UIColors.PANEL_BG, 200),
            debug_surf.get_rect(),
            border_radius=UIMetrics.RADIUS_MEDIUM
        )
        pygame.draw.rect(
            debug_surf,
            (*UIColors.SUCCESS, 100),
            debug_surf.get_rect(),
            width=1,
            border_radius=UIMetrics.RADIUS_MEDIUM
        )

        # Header
        header_font = pygame.font.Font(None, 14)
        header_text = header_font.render("— GAME DEBUG —", True, UIColors.SUCCESS)
        header_rect = header_text.get_rect(center=(debug_width // 2, 12))
        debug_surf.blit(header_text, header_rect)

        # Debug info
        debug_font = pygame.font.Font(None, 12)
        debug_lines = [
            f"Part: {self.game.objective_manager.game_part}",
            f"Day: {self.game.objective_manager.current_day} | {self.game.objective_manager.game_time}",
            f"Objective: {self.game.objective_manager.current_objective_index + 1}/{len(self.game.objective_manager.objectives)}",
        ]

        # Add current objective ID if available
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj:
            obj_id = current_obj.id[:20] + "..." if len(current_obj.id) > 20 else current_obj.id
            debug_lines.append(f"ID: {obj_id}")

        # Draw debug lines
        y = 28
        for line in debug_lines:
            text = debug_font.render(line, True, UIColors.TEXT_SECONDARY)
            debug_surf.blit(text, (10, y))
            y += 16

        # Next step hint
        next_text = "NEXT STEP:"
        next_surf = debug_font.render(next_text, True, UIColors.WARNING)
        debug_surf.blit(next_surf, (10, y))

        if current_obj:
            hint = "Watch the intro dialogue" if current_obj.id == "housing_intro" else "Press E near objective"
            hint_surf = debug_font.render(hint, True, UIColors.TEXT_MUTED)
            debug_surf.blit(hint_surf, (10, y + 14))

        # Controls hint
        controls = "Press G to toggle grid"
        controls_surf = debug_font.render(controls, True, UIColors.TEXT_MUTED)
        debug_surf.blit(controls_surf, (10, debug_height - 14))

        screen.blit(debug_surf, (debug_x, debug_y))

    def wrap_notification_text(self, text, font, max_width):
        """Wrap text for notifications"""
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

    def handle_mouse_motion(self, pos):
        """Handle mouse motion for hover effects"""
        self.objective_panel.handle_motion(pos)

    def toggle_debug(self):
        """Toggle debug panel visibility"""
        self.show_debug = not self.show_debug
        status = "enabled" if self.show_debug else "disabled"
        self.notifications.show(
            "Debug Mode",
            f"Debug panel {status}",
            'info'
        )
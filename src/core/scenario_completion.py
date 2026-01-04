"""
Scenario Completion System - Unified handler for part/scenario transitions.

This module provides a SINGLE source of truth for scenario completion:
- Detects completion via objective ID pattern matching
- Handles the TV transition effect
- Saves progress and unlocks next part
- Returns to main menu

Usage:
    handler = ScenarioCompletionHandler(game)

    # Check if an objective triggers completion
    if handler.is_completion_objective(objective_id):
        handler.trigger_completion()

    # In game loop
    handler.update(dt)
    handler.draw(screen)
"""
import pygame
import re
from typing import Optional, Tuple


class ScenarioCompletionHandler:
    """
    Single unified handler for all scenario/part completion logic.

    Replaces scattered completion checks throughout the codebase with
    one consistent implementation.
    """

    # Pattern to match completion objectives: part1_complete, part2_complete, etc.
    COMPLETION_PATTERN = re.compile(r'^part(\d+)_complete$')

    def __init__(self, game):
        self.game = game

        # Transition state
        self.active = False
        self.completed = False
        self.timer = 0.0
        self.stage = 0  # 0=vertical, 1=horizontal, 2=flash
        self.part_number = 0

        # Screen dimensions - get dynamically for consistency
        self._screen_width = 0
        self._screen_height = 0
        self._update_screen_dimensions()

        # Effect parameters (will be updated when transition starts)
        self.vertical_height = self._screen_height
        self.horizontal_width = self._screen_width

        # Timing
        self.vertical_duration = 0.3
        self.horizontal_duration = 0.4
        self.flash_duration = 0.15

        # Guard against double-trigger
        self._completing = False

    def _update_screen_dimensions(self):
        """Get current screen dimensions from pygame display."""
        # Try to get from game's screen first
        if hasattr(self.game, 'screen') and self.game.screen:
            self._screen_width = self.game.screen.get_width()
            self._screen_height = self.game.screen.get_height()
        else:
            # Fallback to pygame display surface
            display_surface = pygame.display.get_surface()
            if display_surface:
                self._screen_width = display_surface.get_width()
                self._screen_height = display_surface.get_height()
            else:
                # Final fallback to display info
                info = pygame.display.Info()
                self._screen_width = info.current_w if info.current_w > 0 else 960
                self._screen_height = info.current_h if info.current_h > 0 else 640

    def _get_screen_center(self) -> Tuple[int, int]:
        """Get the center of the screen."""
        return self._screen_width // 2, self._screen_height // 2

    def is_completion_objective(self, objective_id: str) -> bool:
        """Check if an objective ID is a completion objective."""
        return bool(self.COMPLETION_PATTERN.match(objective_id))

    def extract_part_number(self, objective_id: str) -> Optional[int]:
        """Extract part number from a completion objective ID."""
        match = self.COMPLETION_PATTERN.match(objective_id)
        if match:
            return int(match.group(1))
        return None

    @property
    def is_transitioning(self) -> bool:
        """Check if transition is active."""
        return self.active

    def trigger_completion(self, objective_id: str = None):
        """
        Start the completion transition.

        Args:
            objective_id: Optional objective ID to extract part number from.
                         If not provided, uses current game_part.
        """
        if self._completing or self.active:
            return

        # Determine part number
        if objective_id:
            self.part_number = self.extract_part_number(objective_id) or 1
        elif hasattr(self.game, 'objective_manager'):
            self.part_number = getattr(self.game.objective_manager, 'game_part', 1)
        else:
            self.part_number = 1

        # Update screen dimensions before starting transition
        self._update_screen_dimensions()

        self._completing = True
        self.active = True
        self.completed = False
        self.timer = 0.0
        self.stage = 0
        self.vertical_height = self._screen_height
        self.horizontal_width = self._screen_width

        print(f"🎬 [SCENARIO_COMPLETE] Part {self.part_number} - TV transition started")
        print(f"    Screen size: {self._screen_width}x{self._screen_height}")

    def _ease_in_expo(self, t: float) -> float:
        """Exponential ease-in for CRT effect."""
        return 0 if t == 0 else pow(2, 10 * t - 10)

    def update(self, dt: float):
        """Update transition state."""
        if not self.active:
            return

        self.timer += dt

        if self.stage == 0:
            # Vertical collapse
            progress = min(1.0, self.timer / self.vertical_duration)
            self.vertical_height = self._screen_height * (1.0 - self._ease_in_expo(progress))

            if progress >= 1.0:
                self.stage = 1
                self.timer = 0
                self.vertical_height = 2

        elif self.stage == 1:
            # Horizontal collapse
            progress = min(1.0, self.timer / self.horizontal_duration)
            self.horizontal_width = self._screen_width * (1.0 - self._ease_in_expo(progress))

            if progress >= 1.0:
                self.stage = 2
                self.timer = 0
                self.horizontal_width = 0

        elif self.stage == 2:
            # Flash and complete
            if self.timer > self.flash_duration:
                self._finalize()

    def _finalize(self):
        """Complete the transition and clean up."""
        print(f"🎬 [SCENARIO_COMPLETE] Part {self.part_number} - transition finished")

        self.active = False
        self.completed = True
        self._completing = False

        # Clean up interior
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            self.game.current_interior.active = False
            self.game.current_interior = None

        # Clean up activity
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = None

        # Save progress
        self._save_progress()

        # Return to menu
        self._return_to_menu()

    def _save_progress(self):
        """Save completion and unlock next part."""
        try:
            if hasattr(self.game, 'progress_manager'):
                pm = self.game.progress_manager

                if hasattr(self.game, 'objective_manager'):
                    total = len(self.game.objective_manager.objectives)
                else:
                    total = 1

                # Mark complete
                pm.update_scenario_progress(
                    self.part_number, total, total,
                    f"part{self.part_number}_complete"
                )
                print(f"[SCENARIO_COMPLETE] Part {self.part_number} saved ({total}/{total})")

                # Unlock next
                next_part = self.part_number + 1
                pm.unlock_scenario(next_part)
                pm.save_progress()
                print(f"[SCENARIO_COMPLETE] Part {next_part} unlocked")

        except Exception as e:
            print(f"[SCENARIO_COMPLETE] Save error: {e}")

    def _return_to_menu(self):
        """Return to main menu."""
        self.game.game_state = 'menu'
        if hasattr(self.game, 'main_menu'):
            self.game.main_menu.reset()
        print("[SCENARIO_COMPLETE] Returned to menu")

    def draw(self, screen: pygame.Surface):
        """Draw the TV transition effect covering the entire screen."""
        if not self.active:
            return

        # Get actual screen dimensions from the surface for guaranteed full coverage
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        center_x = screen_width // 2
        center_y = screen_height // 2

        # Fill entire screen with black first
        screen.fill((0, 0, 0))

        if self.stage == 0:
            # Vertical band - spans full width
            if self.vertical_height > 0:
                top = center_y - self.vertical_height / 2
                brightness = min(255, 100 + int(155 * (1 - self.vertical_height / screen_height)))
                # Use screen_width to ensure full horizontal coverage
                rect = pygame.Rect(0, int(top), screen_width, max(1, int(self.vertical_height)))
                pygame.draw.rect(screen, (brightness, brightness, brightness), rect)

                # Scanlines for CRT effect
                if self.vertical_height > 4:
                    for y in range(int(top), int(top + self.vertical_height), 2):
                        pygame.draw.line(screen, (0, 0, 0), (0, y), (screen_width, y), 1)

        elif self.stage == 1:
            # Horizontal line - centered
            if self.horizontal_width > 0:
                left = center_x - self.horizontal_width / 2
                brightness = min(255, 150 + int(105 * (1 - self.horizontal_width / screen_width)))
                rect = pygame.Rect(int(left), center_y - 1, max(1, int(self.horizontal_width)), 3)
                pygame.draw.rect(screen, (brightness, brightness, brightness), rect)

        elif self.stage == 2:
            # Center glow fade out
            alpha = int(255 * (1 - self.timer / self.flash_duration))
            if alpha > 0:
                size = max(2, int(8 * (1 - self.timer / self.flash_duration)))
                glow = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 255, 255, alpha), (size, size), size)
                screen.blit(glow, (center_x - size, center_y - size))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Block input during transition. Returns True if consumed."""
        if self.active:
            # Allow skip after brief delay
            if event.type == pygame.KEYDOWN and self.timer > 0.2:
                self._finalize()
            return True
        return False

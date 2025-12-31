"""
Dream Doors Sequence - Professional Version
Shows multiple door options labeled "Work," "School," "Homelessness," "Unknown"
Clean professional cards instead of ornate doors
"""
import pygame

from .mentorship_visual_base import (
    MentorshipUIColors, MentorshipUIMetrics, MentorshipVisualHelpers,
    mentorship_visuals
)
from .mentorship_particles import dream_particles
from .mentorship_feedback import dream_feedback


class DreamDoors:
    """Choice sequence with professional option cards"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions - Full HD layout
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Options with theme colors
        self.doors = [
            {"label": "Work", "color": MentorshipUIColors.OPTION_WORK, "hover": False,
             "icon": "💼", "description": "Steady income, limited growth"},
            {"label": "School", "color": MentorshipUIColors.OPTION_SCHOOL, "hover": False,
             "icon": "🎓", "description": "Future investment, debt today"},
            {"label": "Homelessness", "color": MentorshipUIColors.OPTION_UNCERTAIN, "hover": False,
             "icon": "🏚️", "description": "When choices run out"},
            {"label": "Unknown", "color": MentorshipUIColors.OPTION_ALTERNATIVE, "hover": False,
             "icon": "❓", "description": "A leap of faith"},
        ]

        self.door_rects = []
        self.door_width = 160
        self.door_height = 200

        # Selection
        self.selected_door = None
        self.show_result = False
        self.result_timer = 0

        # Animation
        self.fade_alpha = 0
        self.fading_in = True

    def start(self):
        """Start the sequence"""
        self.active = True
        self.completed = False
        self.selected_door = None
        self.show_result = False
        self.result_timer = 0
        self.fade_alpha = 0
        self.fading_in = True

        # Position option cards
        card_spacing = 40
        total_width = len(self.doors) * self.door_width + (len(self.doors) - 1) * card_spacing
        start_x = (self.SCREEN_WIDTH - total_width) // 2
        y = 200
        self.door_rects = []

        for i, door in enumerate(self.doors):
            rect = pygame.Rect(
                start_x + i * (self.door_width + card_spacing),
                y,
                self.door_width,
                self.door_height
            )
            self.door_rects.append(rect)
            door["hover"] = False

        # Clear feedback
        dream_feedback.clear()

    def stop(self):
        """Stop the sequence"""
        self.active = False

    def update(self, dt):
        """Update state"""
        if not self.active:
            return

        # Fade in effect
        if self.fading_in:
            self.fade_alpha = min(255, self.fade_alpha + dt * 180)
            if self.fade_alpha >= 255:
                self.fading_in = False

        # Result timer
        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

        # Update feedback
        dream_feedback.update(dt)

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result or self.fading_in:
            return

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for i, rect in enumerate(self.door_rects):
                self.doors[i]["hover"] = rect.collidepoint(pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, rect in enumerate(self.door_rects):
                if rect.collidepoint(pos):
                    self._select_door(i)
                    break

        elif event.type == pygame.KEYDOWN:
            # Number keys to select
            if event.key == pygame.K_1:
                self._select_door(0)
            elif event.key == pygame.K_2:
                self._select_door(1)
            elif event.key == pygame.K_3:
                self._select_door(2)
            elif event.key == pygame.K_4:
                self._select_door(3)

    def _select_door(self, index):
        """Select an option"""
        if index < 0 or index >= len(self.doors):
            return

        self.selected_door = index
        self.show_result = True

        # Add uncertain future banner
        dream_feedback.add_uncertain_future_banner()
        dream_feedback.fade_to_black(120)

    def render(self, screen):
        """Render with clean professional visuals"""
        # Clean background
        screen.fill(MentorshipUIColors.BACKGROUND)

        # Title
        mentorship_visuals.draw_title(
            screen, "Choose Your Path",
            self.SCREEN_WIDTH // 2, 50
        )

        # Subtitle
        mentorship_visuals.draw_instruction_text(
            screen, "Each path leads somewhere different. Choose wisely.",
            self.SCREEN_WIDTH // 2, 100
        )

        # Additional context
        context_text = mentorship_visuals.fonts['small'].render(
            "You cannot know what lies beyond until you choose.",
            True, MentorshipUIColors.TEXT_MUTED
        )
        screen.blit(context_text,
                   (self.SCREEN_WIDTH // 2 - context_text.get_width() // 2, 140))

        # Draw option cards
        for i, (door, rect) in enumerate(zip(self.doors, self.door_rects)):
            is_selected = (self.selected_door == i)
            is_hover = door["hover"]

            mentorship_visuals.draw_option_card(
                screen, rect,
                door["label"], door["color"],
                description=door["description"],
                icon=door["icon"],
                is_hover=is_hover,
                is_selected=is_selected
            )

            # Number indicator below card
            num_text = mentorship_visuals.fonts['small'].render(
                f"Press {i + 1}", True, MentorshipUIColors.TEXT_MUTED
            )
            screen.blit(num_text,
                       (rect.centerx - num_text.get_width() // 2, rect.bottom + 15))

        # Instructions
        if not self.show_result and not self.fading_in:
            mentorship_visuals.draw_instruction_text(
                screen, "Click a card or press 1-4 to choose your path",
                self.SCREEN_WIDTH // 2, 500
            )

        # Show result
        if self.show_result and self.selected_door is not None:
            door = self.doors[self.selected_door]

            # Result text (fades in)
            result_alpha = min(255, int(self.result_timer * 200))

            result_text = f"You chose: {door['label']}"
            result_surface = mentorship_visuals.fonts['heading'].render(
                result_text, True, door["color"]
            )
            result_surface.set_alpha(result_alpha)
            screen.blit(result_surface,
                       (self.SCREEN_WIDTH // 2 - result_surface.get_width() // 2, 520))

            if self.result_timer > 1.0:
                sub_alpha = min(255, int((self.result_timer - 1.0) * 200))
                sub_text = "But without guidance, your long-term path remains uncertain."
                sub_surface = mentorship_visuals.fonts['body'].render(
                    sub_text, True, MentorshipUIColors.WARNING_AMBER
                )
                sub_surface.set_alpha(sub_alpha)
                screen.blit(sub_surface,
                           (self.SCREEN_WIDTH // 2 - sub_surface.get_width() // 2, 570))

            if self.result_timer > 2.0:
                final_alpha = min(255, int((self.result_timer - 2.0) * 200))
                final_text = "The future remains uncertain..."
                final_surface = mentorship_visuals.fonts['small'].render(
                    final_text, True, MentorshipUIColors.TEXT_MUTED
                )
                final_surface.set_alpha(final_alpha)
                screen.blit(final_surface,
                           (self.SCREEN_WIDTH // 2 - final_surface.get_width() // 2, 620))

        # Render feedback
        dream_feedback.render(screen)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

"""
Dream Doors Sequence - Ethereal Version
Shows multiple doors labeled "Work," "School," "Homelessness," "Unknown"
Features: Ornate glowing doors, fog, light burst reveals, star particles
"""
import pygame
import math
import random

from .mentorship_visual_base import (
    DreamUIColors, DreamUIMetrics, DreamVisualHelpers,
    DreamVisualComponents, FloatAnimation, dream_visuals
)
from .mentorship_particles import dream_particles
from .mentorship_feedback import dream_feedback


class DreamDoors:
    """Dream sequence with ethereal door choices"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions - Full HD layout
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Doors with theme colors - larger descriptions
        self.doors = [
            {"label": "Work", "color": DreamUIColors.DOOR_WORK, "hover": False,
             "description": "Steady income, but limited growth potential"},
            {"label": "School", "color": DreamUIColors.DOOR_SCHOOL, "hover": False,
             "description": "Investment in future, debt burden today"},
            {"label": "Homelessness", "color": DreamUIColors.DOOR_HOMELESS, "hover": False,
             "description": "The path when choices run out"},
            {"label": "Unknown", "color": DreamUIColors.DOOR_UNKNOWN, "hover": False,
             "description": "A leap of faith into uncertainty"},
        ]

        self.door_rects = []
        self.door_width = 180
        self.door_height = 280

        # Float animations for doors
        self.door_floats = []

        # Selection
        self.selected_door = None
        self.show_result = False
        self.result_timer = 0
        self.reveal_progress = 0

        # Animation
        self.fade_alpha = 0
        self.fading_in = True
        self.time = 0

    def start(self):
        """Start the dream sequence"""
        self.active = True
        self.completed = False
        self.selected_door = None
        self.show_result = False
        self.result_timer = 0
        self.reveal_progress = 0
        self.fade_alpha = 0
        self.fading_in = True
        self.time = 0

        # Position doors - HD layout with more spacing
        door_spacing = 60
        total_width = len(self.doors) * self.door_width + (len(self.doors) - 1) * door_spacing
        start_x = (self.SCREEN_WIDTH - total_width) // 2
        y = 200
        self.door_rects = []
        self.door_floats = []

        for i, door in enumerate(self.doors):
            rect = pygame.Rect(
                start_x + i * (self.door_width + door_spacing),
                y,
                self.door_width,
                self.door_height
            )
            self.door_rects.append(rect)
            door["hover"] = False
            self.door_floats.append(FloatAnimation(
                phase=i * 0.8,
                amplitude=7,
                speed=0.6 + i * 0.1
            ))

        # Initialize particles
        dream_particles.clear()
        dream_particles.enable_ambient(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Add initial fog and dust - HD layout
        dream_particles.emit_fog_wisps(
            pygame.Rect(0, self.SCREEN_HEIGHT - 250, self.SCREEN_WIDTH, 250),
            count=15
        )
        dream_particles.emit_dust_motes(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            count=60
        )

        # Clear feedback
        dream_feedback.clear()

    def stop(self):
        """Stop the dream sequence"""
        self.active = False
        dream_particles.disable_ambient()

    def update(self, dt):
        """Update dream state"""
        if not self.active:
            return

        self.time += dt

        # Update float animations
        for float_anim in self.door_floats:
            float_anim.update(dt)

        # Fade in effect
        if self.fading_in:
            self.fade_alpha = min(255, self.fade_alpha + dt * 180)
            if self.fade_alpha >= 255:
                self.fading_in = False

        # Result timer and reveal animation
        if self.show_result:
            self.result_timer += dt
            self.reveal_progress = min(1.0, self.reveal_progress + dt * 0.8)

            if self.result_timer > 4.5:
                self.completed = True
                self.active = False

        # Update particles and feedback
        dream_particles.update(dt)
        dream_feedback.update(dt)

        # Periodically add fog wisps - HD layout
        if random.random() < 0.02:
            dream_particles.emit_fog_wisps(
                pygame.Rect(0, self.SCREEN_HEIGHT - 200, self.SCREEN_WIDTH, 200),
                count=1
            )

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result or self.fading_in:
            return

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for i, rect in enumerate(self.door_rects):
                was_hover = self.doors[i]["hover"]
                is_hover = rect.collidepoint(pos)
                self.doors[i]["hover"] = is_hover

                # Emit glow when first hovering
                if is_hover and not was_hover:
                    dream_particles.emit_glow_sparks(
                        rect.centerx, rect.centery, 6,
                        self.doors[i]["color"]
                    )

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, rect in enumerate(self.door_rects):
                if rect.collidepoint(pos):
                    self._select_door(i)
                    break

        elif event.type == pygame.KEYDOWN:
            # Number keys to select doors
            if event.key == pygame.K_1:
                self._select_door(0)
            elif event.key == pygame.K_2:
                self._select_door(1)
            elif event.key == pygame.K_3:
                self._select_door(2)
            elif event.key == pygame.K_4:
                self._select_door(3)

    def _select_door(self, index):
        """Select a door and trigger effects"""
        if index < 0 or index >= len(self.doors):
            return

        self.selected_door = index
        self.show_result = True

        door = self.doors[index]
        rect = self.door_rects[index]

        # Light burst from door
        dream_particles.emit_light_burst(rect.centerx, rect.centery, door["color"])
        dream_particles.emit_star_burst(rect.centerx, rect.centery, 15)

        # Add door reveal effect
        dream_feedback.add_door_reveal(
            rect.centerx, rect.centery,
            rect.width, rect.height,
            DreamUIColors.STARLIGHT
        )

        # Add uncertain future banner
        dream_feedback.add_uncertain_future_banner()

        # Fade to darker
        dream_feedback.fade_to_black(150)

    def render(self, screen):
        """Render the dream sequence with ethereal visuals"""
        # Dream background with stars
        dream_visuals.draw_dream_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        # Alpha for fade-in
        alpha_mult = self.fade_alpha / 255.0

        # Title with ethereal glow - HD layout
        title_alpha = int(255 * alpha_mult)
        DreamVisualHelpers.draw_ethereal_text(
            screen, "You dream of doors...",
            (self.SCREEN_WIDTH // 2, 60),
            dream_visuals.fonts['title'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_PINK,
            title_alpha
        )

        # Subtitle - HD layout
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Each leads somewhere, but you cannot see beyond.",
            (self.SCREEN_WIDTH // 2, 110),
            dream_visuals.fonts['body'],
            DreamUIColors.TEXT_DIM,
            DreamUIColors.FOG_GRAY,
            title_alpha
        )

        # Additional atmosphere text
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Choose your path wisely...",
            (self.SCREEN_WIDTH // 2, 150),
            dream_visuals.fonts['small'],
            DreamUIColors.GLOW_CYAN,
            DreamUIColors.ETHEREAL_BLUE,
            int(title_alpha * 0.7)
        )

        # Draw doors
        for i, (door, rect) in enumerate(zip(self.doors, self.door_rects)):
            # Get float offset
            float_offset = self.door_floats[i].y_offset if not self.show_result else 0

            # Adjust rect for float
            draw_rect = pygame.Rect(rect.x, rect.y + float_offset, rect.width, rect.height)

            # Check if this door is selected
            is_selected = (self.selected_door == i)
            reveal = self.reveal_progress if is_selected else 0

            # Draw ethereal door
            dream_visuals.draw_dream_door(
                screen, draw_rect,
                door["label"], door["color"],
                is_hover=door["hover"],
                is_selected=is_selected,
                reveal_progress=reveal
            )

            # Number indicator below door
            num_y = draw_rect.bottom + 25 + int(math.sin(self.time * 1.5 + i) * 2)
            DreamVisualHelpers.draw_ethereal_text(
                screen, f"[{i + 1}]",
                (draw_rect.centerx, num_y),
                dream_visuals.fonts['small'],
                DreamUIColors.TEXT_DIM,
                door["color"],
                int(180 * alpha_mult)
            )

            # Show description on hover
            if door["hover"] and not self.show_result:
                desc_y = draw_rect.bottom + 55
                DreamVisualHelpers.draw_ethereal_text(
                    screen, door["description"],
                    (draw_rect.centerx, desc_y),
                    dream_visuals.fonts['small'],
                    DreamUIColors.TEXT_ETHEREAL,
                    door["color"]
                )

        # Instructions - HD layout
        if not self.show_result and not self.fading_in:
            DreamVisualHelpers.draw_ethereal_text(
                screen, "Click a door or press 1-4 to choose your path",
                (self.SCREEN_WIDTH // 2, 560),
                dream_visuals.fonts['heading'],
                DreamUIColors.TEXT_DIM,
                DreamUIColors.GLOW_CYAN
            )

            DreamVisualHelpers.draw_ethereal_text(
                screen, "You cannot know what lies beyond until you step through.",
                (self.SCREEN_WIDTH // 2, 610),
                dream_visuals.fonts['body'],
                DreamUIColors.UNCERTAIN_AMBER,
                DreamUIColors.COLLAPSE_RED
            )

        # Show result overlay - HD layout
        if self.show_result and self.selected_door is not None:
            door = self.doors[self.selected_door]

            # Result text (fades in)
            result_alpha = min(255, int(self.result_timer * 150))

            DreamVisualHelpers.draw_ethereal_text(
                screen, f"You stepped through: {door['label']}",
                (self.SCREEN_WIDTH // 2, 560),
                dream_visuals.fonts['title'],
                DreamUIColors.TEXT_ETHEREAL,
                door["color"],
                result_alpha
            )

            if self.result_timer > 1.0:
                sub_alpha = min(255, int((self.result_timer - 1.0) * 200))
                DreamVisualHelpers.draw_ethereal_text(
                    screen, "But without guidance, your long-term path remains uncertain.",
                    (self.SCREEN_WIDTH // 2, 620),
                    dream_visuals.fonts['heading'],
                    DreamUIColors.UNCERTAIN_AMBER,
                    DreamUIColors.COLLAPSE_RED,
                    sub_alpha
                )

            if self.result_timer > 2.0:
                final_alpha = min(255, int((self.result_timer - 2.0) * 200))
                DreamVisualHelpers.draw_ethereal_text(
                    screen, "The future remains shrouded in mystery...",
                    (self.SCREEN_WIDTH // 2, 670),
                    dream_visuals.fonts['body'],
                    DreamUIColors.FOG_GRAY,
                    DreamUIColors.VOID_BLACK,
                    final_alpha
                )

        # Render particles
        dream_particles.render(screen)

        # Render feedback
        dream_feedback.render(screen)

        # Vignette
        DreamVisualHelpers.draw_vignette(screen, 0.35)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

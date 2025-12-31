"""
Priority Ordering Mini-Game - Ethereal Version
Drag life options (college, job, trade school, gap year) into priority order
Features: Floating orbs, glowing slots, scatter-to-fog effect on completion
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


class PriorityPuzzle:
    """Drag-and-drop priority ordering game with dream visuals"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Life options to prioritize
        self.options = [
            {"name": "College", "icon": "C", "color": DreamUIColors.ETHEREAL_BLUE},
            {"name": "Job", "icon": "J", "color": DreamUIColors.SUCCESS_GREEN},
            {"name": "Trade School", "icon": "T", "color": DreamUIColors.UNCERTAIN_AMBER},
            {"name": "Gap Year", "icon": "G", "color": DreamUIColors.GLOW_PINK},
        ]

        # Slot positions for priority order
        self.slots = []
        self.slot_width = 160
        self.slot_height = 65
        self.slot_spacing = 25

        # Float animations
        self.item_floats = []
        self.slot_floats = []

        # Draggable items
        self.items = []
        self.dragging = None
        self.drag_offset = (0, 0)
        self.hover_item = None

        # Placed items (index in slots)
        self.placed = [None, None, None, None]

        # UI state
        self.show_result = False
        self.result_timer = 0
        self.time = 0
        self.scatter_triggered = False

    def start(self):
        """Start the puzzle"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.result_timer = 0
        self.dragging = None
        self.hover_item = None
        self.placed = [None, None, None, None]
        self.time = 0
        self.scatter_triggered = False

        # Initialize slots (right side)
        slot_x = self.SCREEN_WIDTH - 220
        slot_start_y = 160
        self.slots = []
        self.slot_floats = []
        for i in range(4):
            self.slots.append(pygame.Rect(
                slot_x, slot_start_y + i * (self.slot_height + self.slot_spacing),
                self.slot_width, self.slot_height
            ))
            self.slot_floats.append(FloatAnimation(
                phase=i * 0.6,
                amplitude=4,
                speed=0.5
            ))

        # Initialize draggable items (left side)
        item_x = 120
        item_start_y = 160
        self.items = []
        self.item_floats = []
        for i, opt in enumerate(self.options):
            rect = pygame.Rect(
                item_x, item_start_y + i * (self.slot_height + self.slot_spacing),
                self.slot_width, self.slot_height
            )
            self.items.append({
                "option": opt,
                "rect": rect,
                "original_pos": (rect.x, rect.y),
                "in_slot": None
            })
            self.item_floats.append(FloatAnimation(
                phase=i * 0.8 + 2,
                amplitude=5,
                speed=0.7 + i * 0.1
            ))

        # Initialize particles
        dream_particles.clear()
        dream_particles.enable_ambient(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Add initial atmosphere
        dream_particles.emit_dust_motes(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            count=25
        )

        # Clear feedback
        dream_feedback.clear()

    def stop(self):
        """Stop the puzzle"""
        self.active = False
        dream_particles.disable_ambient()

    def update(self, dt):
        """Update puzzle state"""
        if not self.active:
            return

        self.time += dt

        # Update float animations
        for float_anim in self.item_floats:
            float_anim.update(dt)
        for float_anim in self.slot_floats:
            float_anim.update(dt)

        if self.show_result:
            self.result_timer += dt

            # Trigger scatter effect once
            if not self.scatter_triggered and self.result_timer > 0.5:
                self.scatter_triggered = True
                self._trigger_scatter_effect()

            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

        # Update particles and feedback
        dream_particles.update(dt)
        dream_feedback.update(dt)

        # Emit drag trail if dragging
        if self.dragging:
            rect = self.dragging["rect"]
            dream_particles.emit_drag_trail(
                rect.centerx, rect.centery,
                self.dragging["option"]["color"]
            )

    def _trigger_scatter_effect(self):
        """Trigger the items scattering to fog effect"""
        # Collect item positions
        item_positions = []
        for item in self.items:
            item_positions.append((item["rect"].centerx, item["rect"].centery))

        # Emit scatter particles
        dream_particles.emit_scatter_to_fog(item_positions)

        # Question marks
        dream_particles.emit_question_marks(
            pygame.Rect(200, 200, 400, 200), 8
        )

        # Add incomplete banner
        dream_feedback.add_incomplete_banner()

        # Fade to darker
        dream_feedback.fade_to_black(120)

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Check if clicking on an item
            for i, item in enumerate(self.items):
                if item["rect"].collidepoint(pos):
                    self.dragging = item
                    self.dragging["index"] = i
                    self.drag_offset = (
                        pos[0] - item["rect"].x,
                        pos[1] - item["rect"].y
                    )
                    # Remove from slot if placed
                    if item["in_slot"] is not None:
                        self.placed[item["in_slot"]] = None
                        item["in_slot"] = None

                    # Emit selection glow
                    dream_particles.emit_glow_sparks(
                        item["rect"].centerx, item["rect"].centery, 8,
                        item["option"]["color"]
                    )
                    break

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos

            if self.dragging:
                self.dragging["rect"].x = pos[0] - self.drag_offset[0]
                self.dragging["rect"].y = pos[1] - self.drag_offset[1]
            else:
                # Update hover state
                self.hover_item = None
                for item in self.items:
                    if item["rect"].collidepoint(pos):
                        self.hover_item = item
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in a slot
                dropped_in_slot = False
                for i, slot in enumerate(self.slots):
                    if slot.colliderect(self.dragging["rect"]):
                        if self.placed[i] is None:
                            # Place in slot
                            self.dragging["rect"].x = slot.x
                            self.dragging["rect"].y = slot.y
                            self.dragging["in_slot"] = i
                            self.placed[i] = self.dragging
                            dropped_in_slot = True

                            # Snap effect
                            dream_particles.emit_glow_sparks(
                                slot.centerx, slot.centery, 12,
                                DreamUIColors.GLOW_CYAN
                            )
                            dream_feedback.add_glow_pulse(
                                slot.centerx, slot.centery, 40,
                                DreamUIColors.SUCCESS_GREEN, 0.5, True
                            )
                            break

                if not dropped_in_slot:
                    # Return to original position
                    self.dragging["rect"].x = self.dragging["original_pos"][0]
                    self.dragging["rect"].y = self.dragging["original_pos"][1]

                self.dragging = None

                # Check if all slots filled
                if all(p is not None for p in self.placed):
                    self.show_result = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Allow early completion
                self.show_result = True

    def render(self, screen):
        """Render the puzzle with dream visuals"""
        # Dream background
        dream_visuals.draw_dream_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        # Title with ethereal glow
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Future Planning Worksheet",
            (self.SCREEN_WIDTH // 2, 40),
            dream_visuals.fonts['title'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_CYAN
        )

        # Instructions
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Drag options to set your priorities (1 = highest)",
            (self.SCREEN_WIDTH // 2, 85),
            dream_visuals.fonts['small'],
            DreamUIColors.TEXT_DIM,
            DreamUIColors.FOG_GRAY
        )

        # Left side label
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Options",
            (120 + self.slot_width // 2, 130),
            dream_visuals.fonts['body'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_PINK
        )

        # Right side label
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Priority",
            (self.SCREEN_WIDTH - 220 + self.slot_width // 2, 130),
            dream_visuals.fonts['body'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_CYAN
        )

        # Draw slots with floating numbers
        for i, slot in enumerate(self.slots):
            float_offset = self.slot_floats[i].y_offset
            draw_rect = pygame.Rect(slot.x, slot.y + float_offset, slot.width, slot.height)

            is_filled = self.placed[i] is not None

            # Check if dragging item is hovering over this slot
            is_hover = False
            if self.dragging and slot.colliderect(self.dragging["rect"]) and not is_filled:
                is_hover = True

            # Draw priority slot
            dream_visuals.draw_priority_slot(
                screen, draw_rect,
                i + 1,
                is_filled=is_filled,
                is_hover=is_hover,
                float_offset=0  # Already applied
            )

        # Draw items (not being dragged first, then dragged on top)
        items_to_draw = [(i, item) for i, item in enumerate(self.items) if item != self.dragging]
        if self.dragging:
            items_to_draw.append((self.dragging.get("index", 0), self.dragging))

        for i, item in items_to_draw:
            opt = item["option"]
            rect = item["rect"]

            # Get float offset (only for items not in slots and not dragging)
            float_offset = 0
            if item["in_slot"] is None and item != self.dragging:
                float_offset = self.item_floats[i].y_offset

            # Update rect position if in slot (follow slot float)
            if item["in_slot"] is not None:
                slot_idx = item["in_slot"]
                slot = self.slots[slot_idx]
                slot_float = self.slot_floats[slot_idx].y_offset
                rect.x = slot.x
                rect.y = slot.y + slot_float

            is_dragging = (item == self.dragging)
            is_hover = (item == self.hover_item)

            # Draw floating block
            dream_visuals.draw_floating_block(
                screen, rect,
                opt["name"],
                opt["color"],
                icon=opt["icon"],
                float_offset=float_offset,
                is_dragging=is_dragging,
                is_hover=is_hover
            )

        # Hint text
        if not self.show_result:
            placed_count = sum(1 for p in self.placed if p is not None)
            hint_text = f"Placed: {placed_count}/4"
            DreamVisualHelpers.draw_ethereal_text(
                screen, hint_text,
                (self.SCREEN_WIDTH // 2, 520),
                dream_visuals.fonts['body'],
                DreamUIColors.TEXT_DIM,
                DreamUIColors.FOG_GRAY
            )

            if placed_count == 4:
                DreamVisualHelpers.draw_ethereal_text(
                    screen, "All placed! Submitting...",
                    (self.SCREEN_WIDTH // 2, 555),
                    dream_visuals.fonts['small'],
                    DreamUIColors.GLOW_CYAN,
                    DreamUIColors.ETHEREAL_BLUE
                )

        # Show result - ethereal fade overlay with message
        if self.show_result and self.result_timer > 1.0:
            # Result text appears ethereally
            result_alpha = min(255, int((self.result_timer - 1.0) * 200))

            DreamVisualHelpers.draw_ethereal_text(
                screen, "Incomplete Plan",
                (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 20),
                dream_visuals.fonts['heading'],
                DreamUIColors.UNCERTAIN_AMBER,
                DreamUIColors.COLLAPSE_RED,
                result_alpha
            )

            if self.result_timer > 2.0:
                sub_alpha = min(255, int((self.result_timer - 2.0) * 200))
                DreamVisualHelpers.draw_ethereal_text(
                    screen, "No feedback provided.",
                    (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 30),
                    dream_visuals.fonts['body'],
                    DreamUIColors.TEXT_DIM,
                    DreamUIColors.FOG_GRAY,
                    sub_alpha
                )

                DreamVisualHelpers.draw_ethereal_text(
                    screen, "Please contact your ILP case manager.",
                    (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 65),
                    dream_visuals.fonts['small'],
                    DreamUIColors.TEXT_DIM,
                    DreamUIColors.FOG_GRAY,
                    sub_alpha
                )

        # Render particles
        dream_particles.render(screen)

        # Render feedback
        dream_feedback.render(screen)

        # Vignette
        DreamVisualHelpers.draw_vignette(screen, 0.3)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

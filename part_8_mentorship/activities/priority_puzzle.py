"""
Priority Ordering Mini-Game - Professional Version
Drag life options (college, job, trade school, gap year) into priority order
Clean professional cards and drop zones
"""
import pygame

from .mentorship_visual_base import (
    MentorshipUIColors, MentorshipUIMetrics, MentorshipVisualHelpers,
    mentorship_visuals
)
from .mentorship_particles import dream_particles
from .mentorship_feedback import dream_feedback


class PriorityPuzzle:
    """Drag-and-drop priority ordering game with professional visuals"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions - Full HD layout
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Life options to prioritize
        self.options = [
            {"name": "College", "icon": "🎓", "color": MentorshipUIColors.OPTION_SCHOOL},
            {"name": "Job", "icon": "💼", "color": MentorshipUIColors.SUCCESS_GREEN},
            {"name": "Trade School", "icon": "🔧", "color": MentorshipUIColors.WARNING_AMBER},
            {"name": "Gap Year", "icon": "🌍", "color": MentorshipUIColors.OPTION_ALTERNATIVE},
        ]

        # Slot positions for priority order
        self.slots = []
        self.slot_width = 200
        self.slot_height = 65
        self.slot_spacing = 20

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

    def start(self):
        """Start the puzzle"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.result_timer = 0
        self.dragging = None
        self.hover_item = None
        self.placed = [None, None, None, None]

        # Initialize slots (right side)
        slot_x = self.SCREEN_WIDTH - 280
        slot_start_y = 180
        self.slots = []
        for i in range(4):
            self.slots.append(pygame.Rect(
                slot_x, slot_start_y + i * (self.slot_height + self.slot_spacing),
                self.slot_width, self.slot_height
            ))

        # Initialize draggable items (left side)
        item_x = 150
        item_start_y = 180
        self.items = []
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

        # Clear feedback
        dream_feedback.clear()

    def stop(self):
        """Stop the puzzle"""
        self.active = False

    def update(self, dt):
        """Update puzzle state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

        # Update feedback
        dream_feedback.update(dt)

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
                            break

                if not dropped_in_slot:
                    # Return to original position
                    self.dragging["rect"].x = self.dragging["original_pos"][0]
                    self.dragging["rect"].y = self.dragging["original_pos"][1]

                self.dragging = None

                # Check if all slots filled
                if all(p is not None for p in self.placed):
                    self.show_result = True
                    self._trigger_result()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Allow early completion
                self.show_result = True
                self._trigger_result()

    def _trigger_result(self):
        """Trigger result effects"""
        dream_feedback.add_incomplete_banner()
        dream_feedback.fade_to_black(100)

    def render(self, screen):
        """Render the puzzle with professional visuals"""
        # Clean background
        screen.fill(MentorshipUIColors.BACKGROUND)

        # Title
        mentorship_visuals.draw_title(
            screen, "Future Planning Worksheet",
            self.SCREEN_WIDTH // 2, 40
        )

        # Instructions
        mentorship_visuals.draw_instruction_text(
            screen, "Drag options to set your priorities (1 = highest priority)",
            self.SCREEN_WIDTH // 2, 90
        )

        # Left side label
        left_label = mentorship_visuals.fonts['heading'].render(
            "Your Options", True, MentorshipUIColors.TEXT_PRIMARY
        )
        screen.blit(left_label, (150, 140))

        # Right side label
        right_label = mentorship_visuals.fonts['heading'].render(
            "Your Priorities", True, MentorshipUIColors.TEXT_PRIMARY
        )
        screen.blit(right_label, (self.SCREEN_WIDTH - 280, 140))

        # Center arrow guides
        arrow_x = self.SCREEN_WIDTH // 2
        arrow_font = mentorship_visuals.fonts['heading']
        for i in range(4):
            arrow_y = 200 + i * (self.slot_height + self.slot_spacing)
            arrow_text = arrow_font.render("→", True, MentorshipUIColors.TEXT_MUTED)
            screen.blit(arrow_text, (arrow_x - arrow_text.get_width() // 2, arrow_y))

        # Draw slots
        for i, slot in enumerate(self.slots):
            is_filled = self.placed[i] is not None

            # Check if dragging item is hovering over this slot
            is_hover = False
            if self.dragging and slot.colliderect(self.dragging["rect"]) and not is_filled:
                is_hover = True

            # Draw priority slot
            mentorship_visuals.draw_drop_slot(
                screen, slot,
                label=f"Priority #{i + 1}",
                number=i + 1,
                is_filled=is_filled,
                is_hover=is_hover
            )

        # Draw items (not being dragged first, then dragged on top)
        items_to_draw = [(i, item) for i, item in enumerate(self.items) if item != self.dragging]
        if self.dragging:
            items_to_draw.append((self.dragging.get("index", 0), self.dragging))

        for i, item in items_to_draw:
            opt = item["option"]
            rect = item["rect"]

            # Update rect position if in slot
            if item["in_slot"] is not None:
                slot_idx = item["in_slot"]
                slot = self.slots[slot_idx]
                rect.x = slot.x
                rect.y = slot.y

            is_dragging = (item == self.dragging)
            is_hover = (item == self.hover_item)

            # Draw draggable block
            mentorship_visuals.draw_draggable_block(
                screen, rect,
                opt["name"],
                opt["color"],
                icon=opt["icon"],
                is_dragging=is_dragging,
                is_hover=is_hover
            )

        # Hint text
        if not self.show_result:
            placed_count = sum(1 for p in self.placed if p is not None)
            hint_text = f"Placed: {placed_count}/4"
            hint_surface = mentorship_visuals.fonts['body'].render(
                hint_text, True, MentorshipUIColors.TEXT_SECONDARY
            )
            screen.blit(hint_surface,
                       (self.SCREEN_WIDTH // 2 - hint_surface.get_width() // 2, 600))

            if placed_count == 4:
                complete_text = "All placed! Submitting..."
                complete_surface = mentorship_visuals.fonts['body'].render(
                    complete_text, True, MentorshipUIColors.SUCCESS_GREEN
                )
                screen.blit(complete_surface,
                           (self.SCREEN_WIDTH // 2 - complete_surface.get_width() // 2, 640))

        # Show result
        if self.show_result and self.result_timer > 0.5:
            result_alpha = min(255, int((self.result_timer - 0.5) * 200))

            result_text = "Incomplete Plan"
            result_surface = mentorship_visuals.fonts['title'].render(
                result_text, True, MentorshipUIColors.WARNING_AMBER
            )
            result_surface.set_alpha(result_alpha)
            screen.blit(result_surface,
                       (self.SCREEN_WIDTH // 2 - result_surface.get_width() // 2,
                        self.SCREEN_HEIGHT // 2 - 30))

            if self.result_timer > 1.5:
                sub_alpha = min(255, int((self.result_timer - 1.5) * 200))
                sub_text = "No feedback provided. Contact your ILP case manager."
                sub_surface = mentorship_visuals.fonts['body'].render(
                    sub_text, True, MentorshipUIColors.TEXT_SECONDARY
                )
                sub_surface.set_alpha(sub_alpha)
                screen.blit(sub_surface,
                           (self.SCREEN_WIDTH // 2 - sub_surface.get_width() // 2,
                            self.SCREEN_HEIGHT // 2 + 30))

        # Render feedback
        dream_feedback.render(screen)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

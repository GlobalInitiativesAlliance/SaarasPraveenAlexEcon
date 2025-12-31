"""
Balance Scale Puzzle - Professional Version
Place "income," "education," and "housing" blocks to balance the scale
Clean, professional visuals with no heavy effects
"""
import pygame
import math

from .mentorship_visual_base import (
    MentorshipUIColors, MentorshipUIMetrics, MentorshipVisualHelpers,
    mentorship_visuals
)
from .mentorship_particles import dream_particles
from .mentorship_feedback import dream_feedback


class BalancePuzzle:
    """Balance scale puzzle with professional clean visuals"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions - Full HD layout
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Blocks to balance with icons
        self.blocks = [
            {"name": "Income", "weight": 3, "color": MentorshipUIColors.SUCCESS_GREEN,
             "icon": "💰", "placed": False, "side": None},
            {"name": "Education", "weight": 4, "color": MentorshipUIColors.OPTION_SCHOOL,
             "icon": "📚", "placed": False, "side": None},
            {"name": "Housing", "weight": 5, "color": MentorshipUIColors.WARNING_AMBER,
             "icon": "🏠", "placed": False, "side": None},
        ]

        # Block positions and rects
        self.block_rects = []
        self.block_width = 150
        self.block_height = 60

        # Scale state
        self.left_weight = 0
        self.right_weight = 0
        self.scale_angle = 0  # radians, 0 = balanced
        self.max_angle = 0.4  # max tilt before collapse

        # Dragging
        self.dragging = None
        self.drag_offset = (0, 0)
        self.hover_item = None

        # Drop zones
        self.left_zone = None
        self.right_zone = None

        # Game state
        self.collapsed = False
        self.balanced = False
        self.show_result = False
        self.result_timer = 0

    def start(self):
        """Start the puzzle"""
        self.active = True
        self.completed = False
        self.collapsed = False
        self.balanced = False
        self.show_result = False
        self.result_timer = 0
        self.left_weight = 0
        self.right_weight = 0
        self.scale_angle = 0
        self.dragging = None
        self.hover_item = None

        # Reset blocks
        for block in self.blocks:
            block["placed"] = False
            block["side"] = None

        # Initialize block positions (top of screen, spread out)
        total_width = 3 * self.block_width + 2 * 50
        start_x = (self.SCREEN_WIDTH - total_width) // 2
        start_y = 120
        self.block_rects = []

        for i, block in enumerate(self.blocks):
            rect = pygame.Rect(
                start_x + i * (self.block_width + 50),
                start_y,
                self.block_width,
                self.block_height
            )
            self.block_rects.append({
                "block": block,
                "rect": rect,
                "original_pos": (rect.x, rect.y)
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

        # Calculate balance
        weight_diff = self.left_weight - self.right_weight
        target_angle = weight_diff * 0.1

        # Smoothly move toward target angle
        self.scale_angle += (target_angle - self.scale_angle) * dt * 3

        # Check for collapse
        if abs(self.scale_angle) > self.max_angle and not self.collapsed:
            self.collapsed = True
            self.show_result = True
            self._trigger_collapse()

        # Check for balance (all placed and balanced)
        all_placed = all(b["placed"] for b in self.blocks)
        if all_placed and abs(self.scale_angle) < 0.05 and not self.collapsed:
            self.balanced = True
            self.show_result = True
            self._trigger_success()

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 3.5:
                self.completed = True
                self.active = False

        # Update feedback
        dream_feedback.update(dt)

    def _trigger_collapse(self):
        """Trigger collapse visual effects"""
        dream_feedback.add_collapse_banner()
        dream_feedback.show_overlay(MentorshipUIColors.ERROR_RED_DARK, 60)

    def _trigger_success(self):
        """Trigger success visual effects"""
        dream_feedback.add_balance_banner()

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Check if clicking on a block
            for i, item in enumerate(self.block_rects):
                if item["rect"].collidepoint(pos) and not item["block"]["placed"]:
                    self.dragging = item
                    self.dragging["index"] = i
                    self.drag_offset = (
                        pos[0] - item["rect"].x,
                        pos[1] - item["rect"].y
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
                for item in self.block_rects:
                    if item["rect"].collidepoint(pos) and not item["block"]["placed"]:
                        self.hover_item = item
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                block = self.dragging["block"]
                rect = self.dragging["rect"]

                # Check if dropped in left zone
                if self.left_zone and self.left_zone.colliderect(rect):
                    block["placed"] = True
                    block["side"] = "left"
                    self.left_weight += block["weight"]

                # Check if dropped in right zone
                elif self.right_zone and self.right_zone.colliderect(rect):
                    block["placed"] = True
                    block["side"] = "right"
                    self.right_weight += block["weight"]

                else:
                    # Return to original position
                    rect.x = self.dragging["original_pos"][0]
                    rect.y = self.dragging["original_pos"][1]

                self.dragging = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.collapsed = True
                self.show_result = True
                self._trigger_collapse()

    def render(self, screen):
        """Render the puzzle with clean professional visuals"""
        # Clean background
        screen.fill(MentorshipUIColors.BACKGROUND)

        # Title
        mentorship_visuals.draw_title(
            screen, "Balance Your Future",
            self.SCREEN_WIDTH // 2, 40
        )

        # Instructions
        mentorship_visuals.draw_instruction_text(
            screen, "Drag and drop blocks onto the scale pans to find balance",
            self.SCREEN_WIDTH // 2, 80
        )

        # Draw scale
        self.left_zone, self.right_zone = mentorship_visuals.draw_balance_scale(
            screen,
            (self.SCREEN_WIDTH // 2, 420),
            beam_width=400,
            beam_angle=self.scale_angle,
            left_weight=self.left_weight,
            right_weight=self.right_weight,
            is_balanced=self.balanced
        )

        # Draw blocks
        for i, item in enumerate(self.block_rects):
            block = item["block"]
            rect = item["rect"]

            # Update position if placed on moving pan
            if block["placed"]:
                if block["side"] == "left" and self.left_zone:
                    rect.centerx = self.left_zone.centerx
                    rect.y = self.left_zone.y - 30
                elif block["side"] == "right" and self.right_zone:
                    rect.centerx = self.right_zone.centerx
                    rect.y = self.right_zone.y - 30

            # Check hover/drag state
            is_dragging = (self.dragging == item)
            is_hover = (self.hover_item == item)

            # Draw draggable block
            mentorship_visuals.draw_draggable_block(
                screen, rect,
                block['name'],
                block["color"],
                icon=block["icon"],
                value=str(block['weight']),
                is_dragging=is_dragging,
                is_hover=is_hover
            )

        # Weight indicators
        left_color = MentorshipUIColors.TEXT_SECONDARY
        right_color = MentorshipUIColors.TEXT_SECONDARY

        if self.left_weight > self.right_weight:
            left_color = MentorshipUIColors.WARNING_AMBER
        elif self.right_weight > self.left_weight:
            right_color = MentorshipUIColors.WARNING_AMBER

        # Left weight text
        left_text = mentorship_visuals.fonts['body_bold'].render(
            f"Left: {self.left_weight}", True, left_color
        )
        screen.blit(left_text, (200, 650))

        # Right weight text
        right_text = mentorship_visuals.fonts['body_bold'].render(
            f"Right: {self.right_weight}", True, right_color
        )
        screen.blit(right_text, (self.SCREEN_WIDTH - 200 - right_text.get_width(), 650))

        # Balance status indicator
        if abs(self.left_weight - self.right_weight) == 0 and self.left_weight > 0:
            status_text = "Balanced!"
            status_color = MentorshipUIColors.SUCCESS_GREEN
        elif abs(self.left_weight - self.right_weight) <= 2:
            status_text = "Almost balanced..."
            status_color = MentorshipUIColors.WARNING_AMBER
        else:
            status_text = "Unbalanced"
            status_color = MentorshipUIColors.ERROR_RED

        if self.left_weight > 0 or self.right_weight > 0:
            status_surface = mentorship_visuals.fonts['body_bold'].render(
                status_text, True, status_color
            )
            screen.blit(status_surface,
                       (self.SCREEN_WIDTH // 2 - status_surface.get_width() // 2, 650))

        # Render feedback (banners, overlay)
        dream_feedback.render(screen)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

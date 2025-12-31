"""
Balance Scale Puzzle - Dream/Ethereal Version
Place "income," "education," and "housing" blocks to balance the scale
Features: Glowing ethereal scale, floating blocks, collapse particles
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


class BalancePuzzle:
    """Balance scale puzzle with ethereal dream visuals"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions - Full HD layout
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Blocks to balance with icons - using emoji icons
        self.blocks = [
            {"name": "Income", "weight": 3, "color": DreamUIColors.SUCCESS_GREEN,
             "icon": "💰", "placed": False, "side": None},
            {"name": "Education", "weight": 4, "color": DreamUIColors.ETHEREAL_BLUE,
             "icon": "📚", "placed": False, "side": None},
            {"name": "Housing", "weight": 5, "color": DreamUIColors.UNCERTAIN_AMBER,
             "icon": "🏠", "placed": False, "side": None},
        ]

        # Block positions and rects - larger for HD
        self.block_rects = []
        self.block_width = 150
        self.block_height = 70

        # Float animations for blocks
        self.block_floats = []

        # Scale state
        self.left_weight = 0
        self.right_weight = 0
        self.scale_angle = 0  # radians, 0 = balanced
        self.max_angle = 0.4  # max tilt before collapse
        self.scale_sway_phase = 0

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
        self.collapse_started = False

        # Animation time
        self.time = 0

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
        self.collapse_started = False
        self.time = 0

        # Reset blocks
        for block in self.blocks:
            block["placed"] = False
            block["side"] = None

        # Initialize block positions (top of screen, spread out) - HD layout
        total_width = 3 * self.block_width + 2 * 60  # 3 blocks + 2 gaps
        start_x = (self.SCREEN_WIDTH - total_width) // 2
        start_y = 110
        self.block_rects = []
        self.block_floats = []

        for i, block in enumerate(self.blocks):
            rect = pygame.Rect(
                start_x + i * (self.block_width + 60),
                start_y,
                self.block_width,
                self.block_height
            )
            self.block_rects.append({
                "block": block,
                "rect": rect,
                "original_pos": (rect.x, rect.y)
            })
            self.block_floats.append(FloatAnimation(
                phase=i * 1.2,  # Different phases for each block
                amplitude=8,
                speed=0.8 + i * 0.2
            ))

        # Initialize particle system
        dream_particles.clear()
        dream_particles.enable_ambient(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Clear feedback
        dream_feedback.clear()

        # Add initial dust motes
        dream_particles.emit_dust_motes(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            count=30
        )

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
        for float_anim in self.block_floats:
            float_anim.update(dt)

        # Calculate balance
        weight_diff = self.left_weight - self.right_weight
        target_angle = weight_diff * 0.1

        # Smoothly move toward target angle with gentle sway
        self.scale_sway_phase += dt * 0.5
        sway = math.sin(self.scale_sway_phase) * 0.015 if not self.collapsed else 0
        self.scale_angle += (target_angle - self.scale_angle + sway) * dt * 3

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

        # Update particles and feedback
        dream_particles.update(dt)
        dream_feedback.update(dt)

        # Emit drag trail if dragging
        if self.dragging:
            rect = self.dragging["rect"]
            dream_particles.emit_drag_trail(
                rect.centerx, rect.centery,
                self.dragging["block"]["color"]
            )

    def _trigger_collapse(self):
        """Trigger collapse visual effects"""
        if not self.collapse_started:
            self.collapse_started = True

            # Start collapse effect at scale center - HD layout
            center_x = self.SCREEN_WIDTH // 2
            center_y = 420
            dream_feedback.start_collapse_effect(center_x, center_y, 2.0)

            # Emit collapse particles
            dream_particles.emit_collapse_particles(center_x, center_y, 40)

            # Add collapse banner
            dream_feedback.add_collapse_banner()

            # Question marks for uncertainty - HD layout
            dream_particles.emit_question_marks(
                pygame.Rect(300, 250, 680, 300), 15
            )

    def _trigger_success(self):
        """Trigger success visual effects (rare!)"""
        center_x = self.SCREEN_WIDTH // 2
        center_y = 420

        # Success sparkles
        dream_particles.emit_success_sparkle(center_x, center_y, 25)

        # Glow pulse
        dream_feedback.add_glow_pulse(center_x, center_y, 80,
                                      DreamUIColors.SUCCESS_GREEN, 2.0, True)

        # Balance banner
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
                    # Emit selection glow
                    dream_particles.emit_glow_sparks(
                        item["rect"].centerx, item["rect"].centery, 8,
                        item["block"]["color"]
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
                    # Snap effect
                    dream_particles.emit_glow_sparks(
                        self.left_zone.centerx, self.left_zone.centery, 12,
                        DreamUIColors.GLOW_PINK
                    )

                # Check if dropped in right zone
                elif self.right_zone and self.right_zone.colliderect(rect):
                    block["placed"] = True
                    block["side"] = "right"
                    self.right_weight += block["weight"]
                    # Snap effect
                    dream_particles.emit_glow_sparks(
                        self.right_zone.centerx, self.right_zone.centery, 12,
                        DreamUIColors.GLOW_PINK
                    )

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
        """Render the puzzle with dream visuals"""
        # Dream background
        dream_visuals.draw_dream_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        # Fog at bottom - HD adjusted
        dream_particles.emit_fog_wisps(
            pygame.Rect(0, self.SCREEN_HEIGHT - 180, self.SCREEN_WIDTH, 180),
            count=2
        )

        # Title with ethereal glow - HD layout
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Balance Your Future",
            (self.SCREEN_WIDTH // 2, 40),
            dream_visuals.fonts['title'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_CYAN
        )

        # Instructions - HD layout
        DreamVisualHelpers.draw_ethereal_text(
            screen, "Place the blocks to find balance in life's demands",
            (self.SCREEN_WIDTH // 2, 80),
            dream_visuals.fonts['body'],
            DreamUIColors.TEXT_DIM,
            DreamUIColors.FOG_GRAY
        )

        # Draw scale with glow - larger scale for HD
        collapse_progress = dream_feedback.get_collapse_progress()
        self.left_zone, self.right_zone = dream_visuals.draw_balance_scale(
            screen,
            (self.SCREEN_WIDTH // 2, 440),
            beam_width=450,
            beam_angle=self.scale_angle,
            left_weight=self.left_weight,
            right_weight=self.right_weight,
            is_collapsing=self.collapsed,
            collapse_progress=collapse_progress
        )

        # Draw blocks
        for i, item in enumerate(self.block_rects):
            block = item["block"]
            rect = item["rect"]

            # Update position if placed on moving pan
            if block["placed"]:
                if block["side"] == "left" and self.left_zone:
                    rect.centerx = self.left_zone.centerx
                    rect.y = self.left_zone.y - 20
                elif block["side"] == "right" and self.right_zone:
                    rect.centerx = self.right_zone.centerx
                    rect.y = self.right_zone.y - 20

            # Get float offset (only for unplaced blocks)
            float_offset = 0
            if not block["placed"] and self.dragging != item:
                float_offset = self.block_floats[i].y_offset

            # Check hover/drag state
            is_dragging = (self.dragging == item)
            is_hover = (self.hover_item == item)

            # Draw floating block with glow
            dream_visuals.draw_floating_block(
                screen, rect,
                f"{block['name']} ({block['weight']})",
                block["color"],
                icon=block["icon"],
                float_offset=float_offset,
                is_dragging=is_dragging,
                is_hover=is_hover
            )

        # Weight indicators with glow - HD layout
        left_color = DreamUIColors.TEXT_ETHEREAL
        right_color = DreamUIColors.TEXT_ETHEREAL

        if self.left_weight > self.right_weight:
            left_color = DreamUIColors.UNCERTAIN_AMBER
        elif self.right_weight > self.left_weight:
            right_color = DreamUIColors.UNCERTAIN_AMBER

        DreamVisualHelpers.draw_ethereal_text(
            screen, f"Left: {self.left_weight}",
            (250, 660),
            dream_visuals.fonts['heading'],
            left_color,
            DreamUIColors.GLOW_CYAN
        )

        DreamVisualHelpers.draw_ethereal_text(
            screen, f"Right: {self.right_weight}",
            (self.SCREEN_WIDTH - 250, 660),
            dream_visuals.fonts['heading'],
            right_color,
            DreamUIColors.GLOW_CYAN
        )

        # Balance status indicator
        if abs(self.left_weight - self.right_weight) == 0 and self.left_weight > 0:
            status_text = "⚖️ Balanced!"
            status_color = DreamUIColors.SUCCESS_GREEN
        elif abs(self.left_weight - self.right_weight) <= 2:
            status_text = "Almost balanced..."
            status_color = DreamUIColors.UNCERTAIN_AMBER
        else:
            status_text = "Unbalanced"
            status_color = DreamUIColors.COLLAPSE_RED

        if self.left_weight > 0 or self.right_weight > 0:
            DreamVisualHelpers.draw_ethereal_text(
                screen, status_text,
                (self.SCREEN_WIDTH // 2, 660),
                dream_visuals.fonts['body'],
                status_color,
                DreamUIColors.FOG_GRAY
            )

        # Render particles
        dream_particles.render(screen)

        # Render feedback (banners, effects)
        dream_feedback.render(screen)

        # Vignette for atmosphere
        DreamVisualHelpers.draw_vignette(screen, 0.3)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

"""
Clothes Packing Mini-Game for Foster Home Aging Out
Clean implementation using Part 1 visual base
"""
import pygame
from src.activities.activities import Activity
from .part1_visual_base import (
    Part1UIColors, Part1UIMetrics, Part1VisualHelpers,
    Part1VisualComponents, UIAnimation, part1_visuals
)
from .particle_effects import part1_particles
from .feedback_popups import part1_feedback

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


class ClothesPacking(Activity):
    """Pack clothes into backpack - drag and drop mini-game"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.foster_home_ref = None
        self.visuals = part1_visuals

        # Closet items with properties
        self.items = [
            {"name": "T-Shirt", "type": "essential", "size": 1, "grid": (0, 0)},
            {"name": "Jeans", "type": "essential", "size": 2, "grid": (1, 0)},
            {"name": "Underwear", "type": "essential", "size": 1, "grid": (2, 0)},
            {"name": "Hoodie", "type": "clothing", "size": 2, "grid": (0, 1)},
            {"name": "Jacket", "type": "clothing", "size": 2, "grid": (1, 1)},
            {"name": "Dress Shirt", "type": "clothing", "size": 1, "grid": (2, 1)},
            {"name": "Sneakers", "type": "essential", "size": 2, "grid": (0, 2)},
            {"name": "Socks", "type": "essential", "size": 1, "grid": (1, 2)},
            {"name": "Phone Charger", "type": "essential", "size": 1, "grid": (2, 2)},
        ]

        # Initialize item state
        for item in self.items:
            item["packed"] = False
            item["hover_anim"] = 0.0
            item["drag_anim"] = 0.0

        # Backpack state
        self.backpack_capacity = 8
        self.backpack_used = 0
        self.packed_items = []
        self.min_required = 4

        # Drag state
        self.dragging = None
        self.drag_pos = (0, 0)
        self.drag_offset = (0, 0)
        self.hover_item = None
        self.over_backpack = False

        # Layout
        self.item_width = 130
        self.item_height = 85
        self.grid_x = 100
        self.grid_y = 180
        self.grid_gap = 20

        # Backpack area
        self.backpack_rect = pygame.Rect(SCREEN_WIDTH - 300, 150, 220, 400)

        # Button
        self.button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        self.button_hover = False

    def start(self):
        """Start the packing activity"""
        super().start()
        self.visuals.init_fonts()

        # Reset state
        for item in self.items:
            item["packed"] = False
            item["hover_anim"] = 0.0
            item["drag_anim"] = 0.0

        self.backpack_used = 0
        self.packed_items = []
        self.dragging = None
        self.hover_item = None

    def get_item_rect(self, item):
        """Get rectangle for an item in the closet grid"""
        col, row = item["grid"]
        x = self.grid_x + col * (self.item_width + self.grid_gap)
        y = self.grid_y + row * (self.item_height + self.grid_gap)
        return pygame.Rect(x, y, self.item_width, self.item_height)

    def draw_item(self, screen, item, rect=None, is_dragging=False):
        """Draw a single clothing item card"""
        if rect is None:
            rect = self.get_item_rect(item)

        is_hover = (item == self.hover_item) and not is_dragging
        is_packed = item["packed"]

        # Animate hover
        target_hover = 1.0 if is_hover else 0.0
        item["hover_anim"] += (target_hover - item["hover_anim"]) * 0.2

        # Skip packed items in closet view
        if is_packed and not is_dragging:
            # Draw empty slot
            pygame.draw.rect(screen, Part1UIColors.PANEL_BORDER, rect, 2, border_radius=10)
            return

        # Draw card with lift effect
        lift = int(item["hover_anim"] * 5) if not is_dragging else 8
        draw_rect = rect.copy()
        draw_rect.y -= lift

        # Shadow
        shadow_alpha = 40 + int(item["hover_anim"] * 30)
        if is_dragging:
            shadow_alpha = 80
        Part1VisualHelpers.draw_shadow(screen, draw_rect, offset=4 + lift,
                                       alpha=shadow_alpha, border_radius=10)

        # Background
        bg_color = Part1UIColors.CARD_HOVER if is_hover or is_dragging else Part1UIColors.CARD_BG
        pygame.draw.rect(screen, bg_color, draw_rect, border_radius=10)

        # Type indicator strip at top
        type_colors = {
            'essential': Part1UIColors.ESSENTIAL,
            'clothing': Part1UIColors.CLOTHING,
            'personal': Part1UIColors.PERSONAL,
        }
        type_color = type_colors.get(item["type"], Part1UIColors.CLOTHING)
        indicator_rect = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, 6)
        pygame.draw.rect(screen, type_color, indicator_rect,
                        border_top_left_radius=10, border_top_right_radius=10)

        # Border
        border_color = Part1UIColors.PRIMARY if (is_hover or is_dragging) else Part1UIColors.CARD_BORDER
        pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=10)

        # Item name
        name_surf = self.visuals.fonts['body'].render(item["name"], True, Part1UIColors.TEXT_DARK)
        name_x = draw_rect.x + (draw_rect.width - name_surf.get_width()) // 2
        screen.blit(name_surf, (name_x, draw_rect.y + 20))

        # Size indicator
        size_text = f"Size: {item['size']}"
        size_surf = self.visuals.fonts['small'].render(size_text, True, Part1UIColors.TEXT_MUTED)
        size_x = draw_rect.x + (draw_rect.width - size_surf.get_width()) // 2
        screen.blit(size_surf, (size_x, draw_rect.y + 45))

        # Type label
        type_label = item["type"].capitalize()
        if item["type"] == "essential":
            type_label = "Essential!"
        type_surf = self.visuals.fonts['tiny'].render(type_label, True, type_color)
        type_x = draw_rect.x + (draw_rect.width - type_surf.get_width()) // 2
        screen.blit(type_surf, (type_x, draw_rect.y + 65))

    def draw(self, screen):
        """Draw the packing interface"""
        if not self.active:
            return

        # Dark overlay
        self.visuals.draw_modal_overlay(screen)

        # Title
        self.visuals.draw_title(screen, "Pack Your Clothes", y=30)

        # Subtitle
        subtitle = f"Drag items to your backpack ({self.backpack_used}/{self.backpack_capacity} slots used)"
        self.visuals.draw_subtitle(screen, subtitle, y=80,
                                   color=Part1UIColors.TEXT_WARM)

        # Draw closet section header
        closet_header = self.visuals.fonts['subheading'].render("Closet", True, Part1UIColors.TEXT_WARM)
        screen.blit(closet_header, (self.grid_x, self.grid_y - 40))

        # Draw closet items
        for item in self.items:
            if not item["packed"] and item != self.dragging:
                self.draw_item(screen, item)

        # Draw backpack
        self.draw_backpack_area(screen)

        # Draw dragged item last (on top)
        if self.dragging:
            drag_rect = pygame.Rect(
                self.drag_pos[0] - self.drag_offset[0],
                self.drag_pos[1] - self.drag_offset[1],
                self.item_width, self.item_height
            )
            self.draw_item(screen, self.dragging, rect=drag_rect, is_dragging=True)

        # Draw complete button
        can_complete = len(self.packed_items) >= self.min_required
        self.visuals.draw_button(screen, self.button_rect,
                                f"Done Packing ({len(self.packed_items)} items)",
                                is_hover=self.button_hover,
                                is_enabled=can_complete)

        # Hint
        if len(self.packed_items) < self.min_required:
            hint = f"Pack at least {self.min_required} items to continue"
        else:
            hint = "Press ESC, SPACE, or click Done to finish"
        self.visuals.draw_hint(screen, hint)

        # Draw particles and feedback popups on top
        part1_particles.render(screen)
        part1_feedback.render(screen)

    def draw_backpack_area(self, screen):
        """Draw the backpack drop zone"""
        rect = self.backpack_rect

        # Highlight when dragging over
        if self.over_backpack and self.dragging:
            glow_rect = rect.inflate(10, 10)
            glow = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*Part1UIColors.SUCCESS, 60), glow.get_rect(), border_radius=18)
            screen.blit(glow, glow_rect.topleft)

        # Draw backpack
        self.visuals.draw_backpack(screen, rect, self.backpack_capacity, self.backpack_used)

        # Draw packed items list
        list_y = rect.bottom + 20
        if self.packed_items:
            packed_label = self.visuals.fonts['small'].render("Packed:", True, Part1UIColors.TEXT_WARM)
            screen.blit(packed_label, (rect.x, list_y))

            list_y += 25
            for i, item in enumerate(self.packed_items[:6]):
                item_text = f"• {item['name']} ({item['size']})"
                item_surf = self.visuals.fonts['tiny'].render(item_text, True, Part1UIColors.TEXT_MUTED)
                screen.blit(item_surf, (rect.x + 10, list_y + i * 18))

            if len(self.packed_items) > 6:
                more_text = f"... and {len(self.packed_items) - 6} more"
                more_surf = self.visuals.fonts['tiny'].render(more_text, True, Part1UIColors.TEXT_MUTED)
                screen.blit(more_surf, (rect.x + 10, list_y + 6 * 18))

    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        if not self.active:
            return

        self.drag_pos = pos
        self.over_backpack = self.backpack_rect.collidepoint(pos)

        # Update hover state when not dragging
        if not self.dragging:
            self.hover_item = None
            self.button_hover = self.button_rect.collidepoint(pos)

            for item in self.items:
                if not item["packed"]:
                    if self.get_item_rect(item).collidepoint(pos):
                        self.hover_item = item
                        break

    def handle_mouse_click(self, pos, button):
        """Handle mouse click to start dragging"""
        if not self.active or button != 1:
            return

        # Check button click
        if self.button_rect.collidepoint(pos):
            if len(self.packed_items) >= self.min_required:
                self.finish_packing()
            return

        # Start dragging an item
        for item in self.items:
            if not item["packed"]:
                rect = self.get_item_rect(item)
                if rect.collidepoint(pos):
                    self.dragging = item
                    self.drag_offset = (pos[0] - rect.x, pos[1] - rect.y)
                    self.drag_pos = pos
                    break

    def handle_mouse_release(self, pos, button):
        """Handle mouse release to drop item"""
        if not self.active or button != 1 or not self.dragging:
            return

        # Check if dropped on backpack
        if self.backpack_rect.collidepoint(pos):
            item = self.dragging
            # Check capacity
            if self.backpack_used + item["size"] <= self.backpack_capacity:
                item["packed"] = True
                self.packed_items.append(item)
                self.backpack_used += item["size"]

                # Particle effects and feedback
                part1_particles.emit_packing(pos[0], pos[1])
                part1_feedback.add_item_packed(pos[0], pos[1], item["name"])

        self.dragging = None

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            if len(self.packed_items) >= self.min_required:
                self.finish_packing()

    def finish_packing(self):
        """Complete packing and notify foster home"""
        # Achievement and celebration particles
        part1_feedback.add_packing_complete_achievement()
        part1_particles.emit_achievement(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if self.foster_home_ref:
            self.foster_home_ref.items_packed.add('clothes')
            self.foster_home_ref.update_objective_display()

            # Build message
            if self.packed_items:
                names = [item["name"] for item in self.packed_items[:3]]
                msg = f"You packed: {', '.join(names)}"
                if len(self.packed_items) > 3:
                    msg += f" and {len(self.packed_items) - 3} more items"
                msg += ". The rest stays behind."
            else:
                msg = "You couldn't fit anything in your backpack."

            if hasattr(self.foster_home_ref, 'dialogue_box'):
                self.foster_home_ref.dialogue_box.show(None, msg)

        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        # Update particles and feedback popups
        part1_particles.update(dt)
        part1_feedback.update(dt)

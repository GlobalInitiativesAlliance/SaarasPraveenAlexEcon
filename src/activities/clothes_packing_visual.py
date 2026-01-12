"""
Enhanced Clothes Packing Activity with Visual Textures
Uses actual sprite images for drag-and-drop functionality
"""

import pygame
import os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from src.core.transform_cache import get_scaled

class VisualClothesPacking:
    """Enhanced closet packing mini-game with visual textures"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Load textures for clothing items
        self.item_textures = self.load_item_textures()

        # Closet items with visual properties
        self.closet_items = [
            {
                "name": "T-Shirt",
                "type": "essential",
                "size": 1,
                "grid_pos": (0, 0),  # Position in closet grid
                "texture_key": "tshirt",
                "packed": False,
                "description": "Your favorite band t-shirt"
            },
            {
                "name": "Jeans",
                "type": "essential",
                "size": 2,
                "grid_pos": (1, 0),
                "texture_key": "jeans",
                "packed": False,
                "description": "Worn but comfortable jeans"
            },
            {
                "name": "Underwear Pack",
                "type": "essential",
                "size": 1,
                "grid_pos": (2, 0),
                "texture_key": "underwear",
                "packed": False,
                "description": "7-day pack of basics"
            },
            {
                "name": "Hoodie",
                "type": "clothing",
                "size": 2,
                "grid_pos": (0, 1),
                "texture_key": "hoodie",
                "packed": False,
                "description": "Warm school hoodie"
            },
            {
                "name": "Jacket",
                "type": "clothing",
                "size": 2,
                "grid_pos": (1, 1),
                "texture_key": "jacket",
                "packed": False,
                "description": "Light rain jacket"
            },
            {
                "name": "Sneakers",
                "type": "essential",
                "size": 2,
                "grid_pos": (0, 2),
                "texture_key": "shoes",
                "packed": False,
                "description": "Only pair of good shoes"
            },
            {
                "name": "Photo Album",
                "type": "personal",
                "size": 1,
                "grid_pos": (2, 2),
                "texture_key": "photo",
                "packed": False,
                "description": "Memories from better times"
            },
            {
                "name": "Phone Charger",
                "type": "essential",
                "size": 1,
                "grid_pos": (3, 0),
                "texture_key": "charger",
                "packed": False,
                "description": "Can't survive without this"
            },
            {
                "name": "Toiletries",
                "type": "essential",
                "size": 1,
                "grid_pos": (3, 1),
                "texture_key": "toiletries",
                "packed": False,
                "description": "Basic hygiene supplies"
            },
            {
                "name": "Blanket",
                "type": "comfort",
                "size": 3,
                "grid_pos": (2, 1),
                "texture_key": "blanket",
                "packed": False,
                "description": "Childhood blanket"
            }
        ]

        # Visual properties
        self.closet_bg = None
        self.backpack_bg = None
        self.item_scale = 80  # Size of item sprites

        # Closet layout
        self.closet_rect = pygame.Rect(100, 150, 600, 400)
        self.closet_grid_size = (4, 3)
        self.closet_cell_size = 140

        # Backpack visual properties
        self.backpack_rect = pygame.Rect(SCREEN_WIDTH - 400, 150, 350, 450)
        self.backpack_slots = []  # Visual slots in backpack
        self.backpack_capacity = 10
        self.backpack_used = 0
        self.packed_items = []

        # Initialize backpack slots (visual grid inside backpack)
        self.init_backpack_slots()

        # Drag and drop state
        self.dragging = False
        self.dragged_item = None
        self.drag_offset = (0, 0)
        self.original_pos = None
        self.hover_item = None
        self.hover_slot = None

        # Animation states
        self.animation_timer = 0
        self.item_animations = {}  # Store animation states for items

        # UI elements
        self.complete_button = None
        self.cancel_button = None
        self.tooltip_text = None
        self.tooltip_timer = 0

    def load_item_textures(self):
        """Load or create visual textures for items"""
        textures = {}

        # Try to load actual textures from assets
        asset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'moderninteriors-win', '1_Interiors', '16x16'
        )

        # For now, create colored rectangles as placeholders
        # In production, you'd load actual sprites here
        texture_configs = {
            'tshirt': {'color': (150, 200, 255), 'icon': '👕'},
            'jeans': {'color': (70, 100, 180), 'icon': '👖'},
            'underwear': {'color': (255, 220, 220), 'icon': '🩲'},
            'hoodie': {'color': (180, 140, 200), 'icon': '🧥'},
            'jacket': {'color': (100, 150, 100), 'icon': '🧥'},
            'shoes': {'color': (80, 60, 40), 'icon': '👟'},
            'photo': {'color': (255, 255, 200), 'icon': '📷'},
            'charger': {'color': (60, 60, 60), 'icon': '🔌'},
            'toiletries': {'color': (200, 255, 200), 'icon': '🧼'},
            'blanket': {'color': (255, 180, 150), 'icon': '🛏️'}
        }

        for key, config in texture_configs.items():
            # Create a surface with the item visual
            surf = pygame.Surface((80, 80), pygame.SRCALPHA)

            # Draw item background
            pygame.draw.rect(surf, config['color'], (5, 5, 70, 70), border_radius=10)
            pygame.draw.rect(surf, (255, 255, 255, 100), (5, 5, 70, 70), 2, border_radius=10)

            # Add some visual detail (stripes, patterns, etc.)
            if key == 'tshirt':
                # Draw collar
                pygame.draw.arc(surf, (255, 255, 255), (25, 10, 30, 20), 0, 3.14, 2)
            elif key == 'jeans':
                # Draw pockets
                pygame.draw.rect(surf, (60, 80, 140), (15, 20, 20, 15))
                pygame.draw.rect(surf, (60, 80, 140), (45, 20, 20, 15))
            elif key == 'shoes':
                # Draw laces
                for i in range(3):
                    pygame.draw.line(surf, (255, 255, 255), (30, 20 + i*10), (50, 20 + i*10), 2)

            textures[key] = surf

        # Load closet background
        closet_bg = pygame.Surface((600, 400), pygame.SRCALPHA)
        closet_bg.fill((40, 35, 30))
        # Draw shelves
        for i in range(3):
            pygame.draw.rect(closet_bg, (60, 50, 40), (10, i * 130 + 100, 580, 5))
        textures['closet_bg'] = closet_bg

        # Create backpack visual
        backpack_bg = pygame.Surface((350, 450), pygame.SRCALPHA)
        backpack_bg.fill((80, 60, 40))
        pygame.draw.rect(backpack_bg, (60, 45, 30), (10, 10, 330, 430), border_radius=20)
        # Draw zipper
        pygame.draw.line(backpack_bg, (180, 180, 150), (175, 20), (175, 420), 3)
        textures['backpack_bg'] = backpack_bg

        return textures

    def init_backpack_slots(self):
        """Initialize visual slots in the backpack"""
        self.backpack_slots = []
        slot_size = 70
        padding = 15
        cols = 4
        rows = 3

        start_x = self.backpack_rect.x + 40
        start_y = self.backpack_rect.y + 80

        for row in range(rows):
            for col in range(cols):
                if len(self.backpack_slots) < self.backpack_capacity:
                    slot_rect = pygame.Rect(
                        start_x + col * (slot_size + padding),
                        start_y + row * (slot_size + padding),
                        slot_size,
                        slot_size
                    )
                    self.backpack_slots.append({
                        'rect': slot_rect,
                        'occupied': False,
                        'item': None
                    })

    def get_item_screen_pos(self, item):
        """Get the screen position for an item in the closet"""
        if item["packed"]:
            # Find item in backpack slots
            for slot in self.backpack_slots:
                if slot['item'] == item:
                    return (slot['rect'].x, slot['rect'].y)
            return (0, 0)

        # Calculate position in closet grid
        grid_x, grid_y = item["grid_pos"]
        x = self.closet_rect.x + 50 + grid_x * self.closet_cell_size
        y = self.closet_rect.y + 50 + grid_y * self.closet_cell_size
        return (x, y)

    def get_item_rect(self, item):
        """Get the bounding rectangle for an item"""
        x, y = self.get_item_screen_pos(item)
        return pygame.Rect(x, y, self.item_scale, self.item_scale)

    def handle_mouse_click(self, pos, button):
        """Handle mouse click for starting drag"""
        if not self.active or button != 1:
            return

        # Check complete button
        if self.complete_button and self.complete_button.collidepoint(pos):
            if len(self.packed_items) >= 5:
                self.complete_packing()
            return

        # Check cancel button
        if self.cancel_button and self.cancel_button.collidepoint(pos):
            self.active = False
            return

        # Check items for dragging
        for item in self.closet_items:
            rect = self.get_item_rect(item)
            if rect.collidepoint(pos):
                self.start_dragging(item, pos, rect)
                break

    def start_dragging(self, item, mouse_pos, item_rect):
        """Start dragging an item"""
        self.dragging = True
        self.dragged_item = item
        self.drag_offset = (mouse_pos[0] - item_rect.x, mouse_pos[1] - item_rect.y)
        self.original_pos = (item_rect.x, item_rect.y)

        # If item was packed, remove from backpack
        if item["packed"]:
            self.unpack_item(item)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release for dropping items"""
        if not self.active or button != 1 or not self.dragging:
            return

        if self.dragged_item:
            # Check if dropped on backpack
            if self.backpack_rect.collidepoint(pos):
                self.try_pack_item(self.dragged_item, pos)
            else:
                # Return to closet
                if self.dragged_item["packed"]:
                    self.unpack_item(self.dragged_item)

            self.dragging = False
            self.dragged_item = None
            self.drag_offset = (0, 0)

    def handle_mouse_motion(self, pos):
        """Handle mouse motion for hover effects and tooltips"""
        if not self.active:
            return

        # Update hover item
        self.hover_item = None
        self.hover_slot = None

        # Check closet items
        for item in self.closet_items:
            if not item["packed"]:
                rect = self.get_item_rect(item)
                if rect.collidepoint(pos):
                    self.hover_item = item
                    self.tooltip_text = f"{item['name']}: {item['description']}"
                    self.tooltip_timer = 0
                    break

        # Check backpack slots
        for slot in self.backpack_slots:
            if slot['rect'].collidepoint(pos):
                self.hover_slot = slot
                if slot['item']:
                    self.tooltip_text = f"{slot['item']['name']} ({slot['item']['size']} slots)"
                break

    def try_pack_item(self, item, pos):
        """Try to pack an item into the backpack"""
        if self.backpack_used + item["size"] > self.backpack_capacity:
            # Not enough space
            self.show_message("Not enough space in backpack!")
            return False

        # Find available slots
        slots_needed = item["size"]
        available_slots = [s for s in self.backpack_slots if not s['occupied']]

        if len(available_slots) >= slots_needed:
            # Pack the item
            for i in range(slots_needed):
                available_slots[i]['occupied'] = True
                available_slots[i]['item'] = item

            item["packed"] = True
            self.packed_items.append(item)
            self.backpack_used += item["size"]
            return True

        return False

    def unpack_item(self, item):
        """Remove an item from the backpack"""
        if item in self.packed_items:
            self.packed_items.remove(item)
            item["packed"] = False
            self.backpack_used -= item["size"]

            # Free up backpack slots
            for slot in self.backpack_slots:
                if slot['item'] == item:
                    slot['occupied'] = False
                    slot['item'] = None

    def show_message(self, text):
        """Show a temporary message to the player"""
        self.tooltip_text = text
        self.tooltip_timer = 0

    def complete_packing(self):
        """Complete the packing activity"""
        self.completed = True
        self.active = False

        # Mark clothes as packed in foster home
        if hasattr(self, 'foster_home_ref') and self.foster_home_ref:
            self.foster_home_ref.items_packed.add('clothes')

    def update(self, dt):
        """Update animations and timers"""
        if not self.active:
            return

        self.animation_timer += dt

        # Update tooltip timer
        if self.tooltip_text:
            self.tooltip_timer += dt
            if self.tooltip_timer > 3.0:
                self.tooltip_text = None

    def draw(self, screen):
        """Draw the visual packing interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Draw closet background
        if 'closet_bg' in self.item_textures:
            screen.blit(self.item_textures['closet_bg'], self.closet_rect)
        else:
            pygame.draw.rect(screen, (40, 35, 30), self.closet_rect)

        pygame.draw.rect(screen, (100, 85, 70), self.closet_rect, 3)

        # Draw backpack background
        if 'backpack_bg' in self.item_textures:
            screen.blit(self.item_textures['backpack_bg'], self.backpack_rect)
        else:
            pygame.draw.rect(screen, (80, 60, 40), self.backpack_rect)

        pygame.draw.rect(screen, (120, 90, 60), self.backpack_rect, 3)

        # Draw backpack slots
        for slot in self.backpack_slots:
            color = (60, 50, 40) if not slot['occupied'] else (80, 70, 50)
            if slot == self.hover_slot:
                color = (100, 90, 70)
            pygame.draw.rect(screen, color, slot['rect'], 1)

        # Draw items in closet (not packed and not being dragged)
        for item in self.closet_items:
            if not item["packed"] and item != self.dragged_item:
                self.draw_item(screen, item)

        # Draw packed items in backpack
        for item in self.closet_items:
            if item["packed"] and item != self.dragged_item:
                self.draw_item(screen, item)

        # Draw dragged item on top
        if self.dragging and self.dragged_item:
            mouse_pos = pygame.mouse.get_pos()
            x = mouse_pos[0] - self.drag_offset[0]
            y = mouse_pos[1] - self.drag_offset[1]
            self.draw_item_at(screen, self.dragged_item, x, y, dragging=True)

        # Draw UI elements
        self.draw_ui(screen)

        # Draw tooltip
        if self.tooltip_text and self.tooltip_timer < 2.0:
            self.draw_tooltip(screen, pygame.mouse.get_pos(), self.tooltip_text)

    def draw_item(self, item, screen):
        """Draw an item at its current position"""
        x, y = self.get_item_screen_pos(item)
        self.draw_item_at(screen, item, x, y)

    def draw_item_at(self, screen, item, x, y, dragging=False):
        """Draw an item at a specific position"""
        texture_key = item.get('texture_key', 'tshirt')

        if texture_key in self.item_textures:
            texture = self.item_textures[texture_key]

            # Apply effects
            if dragging:
                # Scale up slightly when dragging - CACHED
                scaled = get_scaled(texture, (90, 90))
                # Add shadow
                shadow = pygame.Surface((90, 90), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 100))
                screen.blit(shadow, (x + 5, y + 5))
                screen.blit(scaled, (x, y))
            elif item == self.hover_item:
                # Highlight on hover - CACHED
                scaled = get_scaled(texture, (85, 85))
                screen.blit(scaled, (x - 2, y - 2))
                pygame.draw.rect(screen, (255, 220, 100), (x - 2, y - 2, 85, 85), 2)
            else:
                screen.blit(texture, (x, y))

        # Draw item name label
        font = pygame.font.Font(None, 16)
        name_text = font.render(item['name'], True, (255, 255, 255))
        name_bg = pygame.Surface((name_text.get_width() + 4, name_text.get_height() + 2))
        name_bg.fill((0, 0, 0))
        name_bg.set_alpha(150)
        screen.blit(name_bg, (x, y + self.item_scale - 20))
        screen.blit(name_text, (x + 2, y + self.item_scale - 19))

    def draw_ui(self, screen):
        """Draw UI elements"""
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pack Your Belongings", True, (255, 220, 180))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        # Closet label
        label_font = pygame.font.Font(None, 32)
        closet_label = label_font.render("Closet", True, (220, 200, 180))
        screen.blit(closet_label, (self.closet_rect.x, self.closet_rect.y - 30))

        # Backpack label and capacity
        backpack_label = label_font.render("Backpack", True, (220, 200, 180))
        screen.blit(backpack_label, (self.backpack_rect.x, self.backpack_rect.y - 30))

        # Capacity bar
        capacity_rect = pygame.Rect(self.backpack_rect.x, self.backpack_rect.y + 30,
                                   self.backpack_rect.width - 20, 30)
        pygame.draw.rect(screen, (40, 30, 20), capacity_rect)

        if self.backpack_used > 0:
            fill_width = int((self.backpack_used / self.backpack_capacity) * capacity_rect.width)
            fill_color = (200, 50, 50) if self.backpack_used == self.backpack_capacity else (50, 200, 50)
            pygame.draw.rect(screen, fill_color, (capacity_rect.x, capacity_rect.y, fill_width, capacity_rect.height))

        pygame.draw.rect(screen, (100, 80, 60), capacity_rect, 2)

        # Capacity text
        info_font = pygame.font.Font(None, 22)
        capacity_text = info_font.render(f"{self.backpack_used}/{self.backpack_capacity} slots used",
                                        True, (255, 255, 255))
        screen.blit(capacity_text, (capacity_rect.x + 10, capacity_rect.y + 5))

        # Instructions
        instruction_text = "Drag items from closet to backpack. Pack at least 5 items."
        inst_surface = info_font.render(instruction_text, True, (200, 180, 150))
        screen.blit(inst_surface, (SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, SCREEN_HEIGHT - 140))

        # Item count
        count_text = f"Items packed: {len(self.packed_items)}/5 minimum"
        count_surface = info_font.render(count_text, True, (255, 200, 150))
        screen.blit(count_surface, (SCREEN_WIDTH // 2 - count_surface.get_width() // 2, SCREEN_HEIGHT - 110))

        # Buttons
        if len(self.packed_items) >= 5:
            # Complete button
            self.complete_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70, 200, 50)
            pygame.draw.rect(screen, (50, 150, 50), self.complete_button)
            pygame.draw.rect(screen, (100, 200, 100), self.complete_button, 2)

            button_text = label_font.render("Complete", True, (255, 255, 255))
            button_rect = button_text.get_rect(center=self.complete_button.center)
            screen.blit(button_text, button_rect)

        # Cancel button (always visible)
        self.cancel_button = pygame.Rect(50, SCREEN_HEIGHT - 70, 100, 40)
        pygame.draw.rect(screen, (150, 50, 50), self.cancel_button)
        pygame.draw.rect(screen, (200, 100, 100), self.cancel_button, 2)

        cancel_text = info_font.render("Cancel", True, (255, 255, 255))
        cancel_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_rect)

    def draw_tooltip(self, screen, pos, text):
        """Draw a tooltip near the mouse cursor"""
        font = pygame.font.Font(None, 20)
        text_surface = font.render(text, True, (255, 255, 255))

        # Create background
        padding = 10
        bg_rect = pygame.Rect(pos[0] + 20, pos[1] - 30,
                             text_surface.get_width() + padding * 2,
                             text_surface.get_height() + padding)

        # Keep tooltip on screen
        if bg_rect.right > SCREEN_WIDTH:
            bg_rect.x = pos[0] - bg_rect.width - 20
        if bg_rect.top < 0:
            bg_rect.y = pos[1] + 20

        # Draw background
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)

        # Draw text
        screen.blit(text_surface, (bg_rect.x + padding, bg_rect.y + padding // 2))

    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            self.active = False
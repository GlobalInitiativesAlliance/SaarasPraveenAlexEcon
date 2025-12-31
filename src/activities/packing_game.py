"""
Packing Mini-Game for Alex's Apartment
Emotional drag-and-drop interface showing possessions and their meaning
"""
import pygame
import math
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class PackingGame(Activity):
    """Packing/unpacking possessions with emotional weight"""

    def __init__(self, objective_manager, mode='unpack'):
        super().__init__(objective_manager)
        self.narrative_ref = None  # Set by parent interior

        # Game mode: 'unpack' (moving in) or 'pack' (forced to leave)
        self.mode = mode

        # Dragging state
        self.dragging = False
        self.dragged_item = None
        self.drag_offset = (0, 0)

        # Items and their states
        self.create_items()
        self.packed_items = []
        self.unpacked_items = []

        # UI elements
        self.bag_rect = None
        self.room_rect = None
        self.continue_button_rect = None

        # Emotional state
        self.emotional_messages = []
        self.message_timer = 0
        self.current_message = ""

        # Animation
        self.animation_timer = 0
        self.animating_items = []  # List of items currently animating
        self.animation_speed = 5.0  # Speed of lerp animation
        self.particles = []  # Active particles

        # Colors
        self.bg_color = (40, 40, 50) if mode == 'pack' else (60, 60, 70)
        self.hope_color = (150, 200, 150) if mode == 'unpack' else (200, 100, 100)

    def create_items(self):
        """Create items with emotional significance"""
        if self.mode == 'unpack':
            # Moving in - hopeful
            self.items = [
                {
                    'name': 'Foster Care Photo',
                    'image': self.create_item_image('photo', (60, 40)),
                    'pos': [100, 300],
                    'target_pos': None,
                    'packed': True,
                    'description': 'The only proof of better times',
                    'emotional_weight': 'heavy',
                    'memory': 'Hidden away - too painful to display'
                },
                {
                    'name': 'Shelter Blanket',
                    'image': self.create_item_image('blanket', (80, 60)),
                    'pos': [100, 400],
                    'target_pos': None,
                    'packed': True,
                    'description': 'Thin but yours',
                    'emotional_weight': 'comfort',
                    'memory': '30 nights of minimal warmth'
                },
                {
                    'name': 'Phone Charger',
                    'image': self.create_item_image('charger', (40, 50)),
                    'pos': [100, 500],
                    'target_pos': None,
                    'packed': True,
                    'description': 'Your lifeline to the world',
                    'emotional_weight': 'essential',
                    'memory': 'Guarded carefully - impossible to replace'
                },
                {
                    'name': 'Last $20',
                    'image': self.create_item_image('money', (60, 30)),
                    'pos': [200, 350],
                    'target_pos': None,
                    'packed': True,
                    'description': 'Emergency fund',
                    'emotional_weight': 'survival',
                    'memory': 'Hidden in three different places'
                },
                {
                    'name': 'Change of Clothes',
                    'image': self.create_item_image('clothes', (70, 50)),
                    'pos': [200, 450],
                    'target_pos': None,
                    'packed': True,
                    'description': 'Two shirts, one pair of jeans',
                    'emotional_weight': 'necessity',
                    'memory': 'Washed in shelter sinks'
                }
            ]
        else:
            # Packing to leave - defeated
            self.items = [
                {
                    'name': 'Foster Care Photo',
                    'image': self.create_item_image('photo', (60, 40)),
                    'pos': [600, 200],
                    'target_pos': None,
                    'packed': False,
                    'description': 'Still hidden in the drawer',
                    'emotional_weight': 'heavy',
                    'memory': 'Three months and you never displayed it'
                },
                {
                    'name': 'Small Plant',
                    'image': self.create_item_image('plant', (50, 60)),
                    'pos': [700, 250],
                    'target_pos': None,
                    'packed': False,
                    'description': 'Bought with first saved money',
                    'emotional_weight': 'hope',
                    'memory': 'Too heavy to carry. Leave it behind.'
                },
                {
                    'name': 'Borrowed Book',
                    'image': self.create_item_image('book', (40, 50)),
                    'pos': [650, 350],
                    'target_pos': None,
                    'packed': False,
                    'description': 'Library book about getting your life together',
                    'emotional_weight': 'irony',
                    'memory': 'Overdue. Another debt.'
                },
                {
                    'name': "Alex's $50",
                    'image': self.create_item_image('money', (60, 30)),
                    'pos': [600, 450],
                    'target_pos': None,
                    'packed': False,
                    'description': 'Guilt money',
                    'emotional_weight': 'bitter',
                    'memory': "Won't even cover a shelter bed"
                },
                {
                    'name': 'Worn Clothes',
                    'image': self.create_item_image('clothes', (70, 50)),
                    'pos': [700, 400],
                    'target_pos': None,
                    'packed': False,
                    'description': 'Same clothes, more worn',
                    'emotional_weight': 'exhaustion',
                    'memory': 'Three months of hand washing'
                },
                {
                    'name': 'Phone (14% battery)',
                    'image': self.create_item_image('phone', (35, 60)),
                    'pos': [550, 300],
                    'target_pos': None,
                    'packed': False,
                    'description': 'No charger at the shelter',
                    'emotional_weight': 'anxiety',
                    'memory': 'Your only connection, dying'
                }
            ]

    def create_item_image(self, item_type, size):
        """Create simple visual representations of items"""
        surface = pygame.Surface(size, pygame.SRCALPHA)

        if item_type == 'photo':
            pygame.draw.rect(surface, (200, 180, 150), (0, 0, *size))
            pygame.draw.rect(surface, (100, 80, 60), (0, 0, *size), 2)
            # Simple face drawings
            pygame.draw.circle(surface, (80, 60, 40), (20, 20), 5)
            pygame.draw.circle(surface, (80, 60, 40), (40, 20), 5)

        elif item_type == 'blanket':
            pygame.draw.rect(surface, (150, 150, 180), (0, 0, *size))
            # Fold lines
            for i in range(0, size[1], 10):
                pygame.draw.line(surface, (130, 130, 160), (0, i), (size[0], i))

        elif item_type == 'charger':
            pygame.draw.rect(surface, (30, 30, 30), (10, 0, 20, 30))
            pygame.draw.line(surface, (30, 30, 30), (20, 30), (20, 50), 3)

        elif item_type == 'money':
            pygame.draw.rect(surface, (100, 150, 100), (0, 0, *size))
            pygame.draw.rect(surface, (50, 100, 50), (0, 0, *size), 2)
            font = pygame.font.Font(None, 20)
            text = font.render("$", True, (50, 100, 50))
            surface.blit(text, (size[0]//2 - 5, size[1]//2 - 10))

        elif item_type == 'clothes':
            pygame.draw.rect(surface, (100, 100, 150), (0, 0, *size))
            pygame.draw.rect(surface, (80, 80, 120), (0, 0, *size), 2)
            # Fold line
            pygame.draw.line(surface, (80, 80, 120), (0, size[1]//2), (size[0], size[1]//2), 2)

        elif item_type == 'plant':
            # Pot
            pygame.draw.rect(surface, (150, 100, 80), (10, 30, 30, 30))
            # Plant
            pygame.draw.circle(surface, (100, 200, 100), (25, 25), 15)

        elif item_type == 'book':
            pygame.draw.rect(surface, (180, 150, 120), (0, 0, *size))
            pygame.draw.rect(surface, (120, 100, 80), (0, 0, *size), 2)
            # Spine
            pygame.draw.line(surface, (100, 80, 60), (10, 0), (10, size[1]), 3)

        elif item_type == 'phone':
            pygame.draw.rect(surface, (30, 30, 30), (0, 0, *size))
            pygame.draw.rect(surface, (200, 200, 200), (3, 5, size[0]-6, size[1]-15))
            # Battery indicator
            pygame.draw.rect(surface, (255, 50, 50), (5, 7, size[0]//4, 3))

        return surface

    def start(self):
        """Start the packing activity"""
        super().start()
        self.animation_timer = 0

        if self.mode == 'unpack':
            self.current_message = "Unpack your few possessions into your new room"
        else:
            self.current_message = "Pack everything. You have 5 minutes."

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # Update animation
        self.animation_timer += 0.016

        # Background
        screen.fill(self.bg_color)

        # Draw main areas
        self.draw_areas(screen)

        # Draw items
        for item in self.items:
            self.draw_item(screen, item)

        # Draw currently dragged item on top
        if self.dragged_item:
            self.draw_item(screen, self.dragged_item)

        # Draw particles (after items, before UI for proper layering)
        self.draw_particles(screen)

        # Draw UI elements
        self.draw_ui(screen)

        # Draw emotional messages
        self.draw_messages(screen)

    def draw_areas(self, screen):
        """Draw bag and room areas with gradients"""
        if self.mode == 'unpack':
            # Bag area (left) with gradient
            self.bag_rect = pygame.Rect(50, 200, 250, 400)
            self.draw_gradient_rect(screen, self.bag_rect, (60, 50, 40), (80, 70, 60))

            # Glow border
            pygame.draw.rect(screen, (100, 90, 80), self.bag_rect, 3, border_radius=8)

            # Bag label with shadow
            font = pygame.font.Font(None, 28)
            self.draw_text_with_shadow(screen, "Your Bag", font, (125, 170), (200, 200, 200))

            # Room area (right) with gradient
            self.room_rect = pygame.Rect(500, 150, 450, 500)

            # Calculate how many items unpacked for color transition
            unpacked_count = sum(1 for item in self.items if not item['packed'])
            progress = unpacked_count / len(self.items)

            # Transition from brown to warm green as items are placed
            start_color = (100, 90, 80)
            end_color = (110, 130, 100)  # Warmer, more hopeful
            current_color = self.lerp_color(start_color, end_color, progress)
            darker = tuple(max(0, c - 20) for c in current_color)

            self.draw_gradient_rect(screen, self.room_rect, darker, current_color)

            # Glow effect if items are being placed
            if progress > 0:
                glow_alpha = int(progress * 60)
                glow_surf = pygame.Surface((self.room_rect.width + 10, self.room_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (150, 200, 150, glow_alpha), (0, 0, glow_surf.get_width(), glow_surf.get_height()), border_radius=12)
                screen.blit(glow_surf, (self.room_rect.x - 5, self.room_rect.y - 5))

            pygame.draw.rect(screen, (120, 140, 110), self.room_rect, 3, border_radius=8)

            # Room label
            self.draw_text_with_shadow(screen, "Your New Room", font, (650, 120), (200, 200, 200))

        else:  # packing mode with defeated colors
            # Room area (right) with gradient
            self.room_rect = pygame.Rect(500, 150, 450, 500)
            self.draw_gradient_rect(screen, self.room_rect, (80, 70, 60), (100, 90, 80))
            pygame.draw.rect(screen, (80, 70, 60), self.room_rect, 3, border_radius=8)

            # Room label
            font = pygame.font.Font(None, 28)
            self.draw_text_with_shadow(screen, "The Room That Was Yours", font, (600, 120), (150, 150, 150))

            # Bag area (left) with gradient
            self.bag_rect = pygame.Rect(50, 200, 250, 400)
            self.draw_gradient_rect(screen, self.bag_rect, (50, 40, 30), (70, 60, 50))
            pygame.draw.rect(screen, (50, 40, 30), self.bag_rect, 3, border_radius=8)

            # Bag label
            self.draw_text_with_shadow(screen, "Pack Your Life", font, (110, 170), (200, 200, 200))

    def draw_item(self, screen, item):
        """Draw a single item with idle float and drag scale effects"""
        # Calculate idle float offset (gentle breathing effect)
        if not self.dragging or item != self.dragged_item:
            # Each item has unique time offset based on hash of name
            time_offset = hash(item['name']) % 100 / 100.0 * 6.28  # Unique phase
            offset_y = math.sin(self.animation_timer * 2 + time_offset) * 2
        else:
            offset_y = 0  # No float when dragging

        # Calculate scale (larger when dragging)
        scale = 1.15 if item == self.dragged_item else 1.0

        # Get base image and size
        base_image = item['image']
        base_width, base_height = base_image.get_size()

        # Apply scale
        if scale != 1.0:
            scaled_width = int(base_width * scale)
            scaled_height = int(base_height * scale)
            scaled_image = pygame.transform.scale(base_image, (scaled_width, scaled_height))
        else:
            scaled_image = base_image
            scaled_width, scaled_height = base_width, base_height

        # Calculate final position with float offset and centering for scale
        final_x = item['pos'][0] - (scaled_width - base_width) / 2
        final_y = item['pos'][1] - (scaled_height - base_height) / 2 + offset_y

        # Draw shadow (offset with float)
        shadow_pos = (final_x + 3, final_y + 3)
        shadow_surf = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        screen.blit(shadow_surf, shadow_pos)

        # Draw item
        screen.blit(scaled_image, (final_x, final_y))

        # Hover effect - show description (use original rect for hit detection)
        mouse_pos = pygame.mouse.get_pos()
        item_rect = pygame.Rect(*item['pos'], base_width, base_height)
        if item_rect.collidepoint(mouse_pos) and not self.dragging:
            self.draw_item_tooltip(screen, item, mouse_pos)

    def draw_item_tooltip(self, screen, item, mouse_pos):
        """Draw tooltip for hovered item"""
        font_small = pygame.font.Font(None, 20)
        font_tiny = pygame.font.Font(None, 16)

        # Create tooltip surface
        lines = [
            item['name'],
            item['description'],
            f"[{item['emotional_weight']}]"
        ]

        max_width = max(font_small.size(line)[0] for line in lines) + 20
        height = len(lines) * 25 + 10

        tooltip = pygame.Surface((max_width, height), pygame.SRCALPHA)
        tooltip.fill((20, 20, 20, 230))
        pygame.draw.rect(tooltip, (100, 100, 100), (0, 0, max_width, height), 1)

        # Draw text
        y = 5
        for i, line in enumerate(lines):
            font = font_small if i == 0 else font_tiny
            color = self.hope_color if i == 2 else (255, 255, 255)
            text = font.render(line, True, color)
            tooltip.blit(text, (10, y))
            y += 25

        # Position tooltip
        x = min(mouse_pos[0] + 10, SCREEN_WIDTH - max_width - 10)
        y = min(mouse_pos[1] + 10, SCREEN_HEIGHT - height - 10)
        screen.blit(tooltip, (x, y))

    def draw_ui(self, screen):
        """Draw UI elements with animated progress bar"""
        # Calculate progress
        if self.mode == 'unpack':
            current = sum(1 for item in self.items if not item['packed'])
            total = len(self.items)
            label = "Unpacked"
        else:
            current = sum(1 for item in self.items if item['packed'])
            total = len([i for i in self.items if i['name'] != 'Small Plant'])  # Can't take plant
            label = "Packed"

        progress_ratio = current / total if total > 0 else 0

        # Animated progress bar
        bar_width = 300
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 40

        # Background (empty bar)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        self.draw_gradient_rect(screen, bg_rect, (40, 40, 40), (60, 60, 60))
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 2, border_radius=15)

        # Filled portion (smoothly animated)
        if progress_ratio > 0:
            fill_width = int(bar_width * progress_ratio)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

            # Gradient fill based on mode
            if self.mode == 'unpack':
                color1 = (100, 180, 100)
                color2 = (150, 220, 150)
            else:
                color1 = (180, 100, 100)
                color2 = (220, 150, 150)

            self.draw_gradient_rect(screen, fill_rect, color1, color2)

            # Shine effect (moving highlight)
            shine_pos = (self.animation_timer * 100) % (fill_width + 100) - 50
            if 0 <= shine_pos <= fill_width:
                shine_surf = pygame.Surface((30, bar_height), pygame.SRCALPHA)
                shine_alpha = 80
                pygame.draw.rect(shine_surf, (255, 255, 255, shine_alpha), (0, 0, 30, bar_height))
                screen.blit(shine_surf, (bar_x + int(shine_pos), bar_y))

            pygame.draw.rect(screen, (200, 200, 200), fill_rect, 2, border_radius=15)

        # Progress text with shadow
        font = pygame.font.Font(None, 24)
        progress_text = f"{label}: {current}/{total}"
        self.draw_text_with_shadow(screen, progress_text, font,
                                   (SCREEN_WIDTH // 2 - font.size(progress_text)[0] // 2, bar_y + 35),
                                   (220, 220, 220))

        # Continue button (when done)
        if self.mode == 'unpack':
            done = all(not item['packed'] for item in self.items)
        else:
            # Can't pack the plant, so check all others
            done = all(item['packed'] or item['name'] == 'Small Plant' for item in self.items)

        if done:
            self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 60)

            # Enhanced button with glow, pulse, and gradient
            pulse = math.sin(self.animation_timer * 3) * 4
            button_rect = pygame.Rect(
                self.continue_button_rect.x - pulse,
                self.continue_button_rect.y - pulse,
                self.continue_button_rect.width + pulse * 2,
                self.continue_button_rect.height + pulse * 2
            )

            # Outer glow
            glow_alpha = int(128 + math.sin(self.animation_timer * 3) * 64)
            glow_surf = pygame.Surface((button_rect.width + 20, button_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.hope_color, glow_alpha), (0, 0, glow_surf.get_width(), glow_surf.get_height()), border_radius=35)
            screen.blit(glow_surf, (button_rect.x - 10, button_rect.y - 10))

            # Button gradient
            button_surf = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            if self.mode == 'unpack':
                self.draw_gradient_rect(screen, button_rect, (120, 200, 120), (100, 180, 100))
            else:
                self.draw_gradient_rect(screen, button_rect, (200, 120, 120), (180, 100, 100))

            # Button border
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 3, border_radius=30)

            # Button text with shadow
            button_font = pygame.font.Font(None, 32)
            button_text = "Settle In" if self.mode == 'unpack' else "Leave Forever"
            text_x = button_rect.centerx - button_font.size(button_text)[0] // 2
            text_y = button_rect.centery - button_font.size(button_text)[1] // 2
            self.draw_text_with_shadow(screen, button_text, button_font, (text_x, text_y), (255, 255, 255))

    def draw_messages(self, screen):
        """Draw emotional messages"""
        if self.current_message:
            font = pygame.font.Font(None, 24)
            msg_surf = font.render(self.current_message, True, (255, 255, 255))
            x = SCREEN_WIDTH // 2 - msg_surf.get_width() // 2
            y = SCREEN_HEIGHT - 150

            # Background for readability
            bg_rect = pygame.Rect(x - 10, y - 5, msg_surf.get_width() + 20, 30)
            pygame.draw.rect(screen, (40, 40, 40, 200), bg_rect)

            screen.blit(msg_surf, (x, y))

        # Memory text when moving items
        if self.message_timer > 0:
            self.message_timer -= 0.016
            for msg in self.emotional_messages:
                font = pygame.font.Font(None, 20)
                msg_surf = font.render(msg['text'], True, (200, 200, 200))
                msg_surf.set_alpha(int(255 * self.message_timer))
                screen.blit(msg_surf, msg['pos'])

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Check continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.complete_packing()
            return

        # Check for item click
        for item in self.items:
            item_rect = pygame.Rect(*item['pos'], *item['image'].get_size())
            if item_rect.collidepoint(pos):
                # Special case: can't pack the plant
                if self.mode == 'pack' and item['name'] == 'Small Plant':
                    self.current_message = "Too heavy to carry. You have to leave it."
                    self.message_timer = 3.0
                    return

                # Start dragging
                self.dragging = True
                self.dragged_item = item
                self.drag_offset = (pos[0] - item['pos'][0], pos[1] - item['pos'][1])
                break

    def handle_mouse_release(self, pos, button):
        """Handle mouse release"""
        if not self.active or button != 1 or not self.dragging:
            return

        self.dragging = False

        if self.dragged_item:
            # Check if dropped in valid area
            if self.mode == 'unpack':
                # Unpacking: from bag to room
                if self.room_rect.collidepoint(pos) and self.dragged_item['packed']:
                    self.dragged_item['packed'] = False
                    target_pos = [
                        max(self.room_rect.x, min(pos[0] - 30, self.room_rect.right - 60)),
                        max(self.room_rect.y, min(pos[1] - 20, self.room_rect.bottom - 50))
                    ]
                    self.animate_item_to_position(self.dragged_item, target_pos)
                    # Show memory
                    self.show_memory(self.dragged_item, pos)
                elif self.bag_rect.collidepoint(pos) and not self.dragged_item['packed']:
                    # Put back in bag
                    self.dragged_item['packed'] = True
                    target_pos = [
                        self.bag_rect.x + 20 + (hash(self.dragged_item['name']) % 150),
                        self.bag_rect.y + 50 + (hash(self.dragged_item['name']) % 250)
                    ]
                    self.animate_item_to_position(self.dragged_item, target_pos)
            else:
                # Packing: from room to bag
                if self.bag_rect.collidepoint(pos) and not self.dragged_item['packed']:
                    self.dragged_item['packed'] = True
                    target_pos = [
                        self.bag_rect.x + 20 + (hash(self.dragged_item['name']) % 150),
                        self.bag_rect.y + 50 + (hash(self.dragged_item['name']) % 250)
                    ]
                    self.animate_item_to_position(self.dragged_item, target_pos)
                    # Show memory
                    self.show_memory(self.dragged_item, pos)
                elif self.room_rect.collidepoint(pos) and self.dragged_item['packed']:
                    # Put back in room
                    self.dragged_item['packed'] = False
                    target_pos = [
                        max(self.room_rect.x, min(pos[0] - 30, self.room_rect.right - 60)),
                        max(self.room_rect.y, min(pos[1] - 20, self.room_rect.bottom - 50))
                    ]
                    self.animate_item_to_position(self.dragged_item, target_pos)

        self.dragged_item = None

    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        if self.dragging and self.dragged_item:
            self.dragged_item['pos'] = [
                pos[0] - self.drag_offset[0],
                pos[1] - self.drag_offset[1]
            ]

    def show_memory(self, item, pos):
        """Show item memory when moved"""
        self.emotional_messages = [{
            'text': item['memory'],
            'pos': (pos[0] - 100, pos[1] - 30)
        }]
        self.message_timer = 3.0

    def complete_packing(self):
        """Complete the packing activity"""
        # Update parent interior state
        if self.narrative_ref:
            if self.mode == 'unpack':
                self.narrative_ref.possessions_unpacked = True
                if hasattr(self.narrative_ref, 'dialogue_box'):
                    self.narrative_ref.dialogue_box.show(None,
                        "Your few possessions make the room feel slightly more like home.")
            else:
                self.narrative_ref.packing_complete = True
                if hasattr(self.narrative_ref, 'dialogue_box'):
                    self.narrative_ref.dialogue_box.show(None,
                        "Everything you own fits in one bag. Again.")

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

        # Mark activity complete
        self.complete()

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        # ESC to skip (if mostly done)
        if key == pygame.K_ESCAPE:
            if self.mode == 'unpack':
                done = sum(1 for item in self.items if not item['packed']) >= 3
            else:
                done = sum(1 for item in self.items if item['packed']) >= 3

            if done:
                self.complete_packing()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt

        # Update item animations
        self.update_item_animations(dt)

        # Update particles
        self.update_particles(dt)

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt

    # ===== NEW ANIMATION AND VISUAL METHODS =====

    def animate_item_to_position(self, item, target_pos):
        """Smoothly animate item to target position"""
        item['animating'] = True
        item['start_pos'] = item['pos'].copy() if isinstance(item['pos'], list) else list(item['pos'])
        item['target_pos'] = target_pos
        item['anim_progress'] = 0.0
        if item not in self.animating_items:
            self.animating_items.append(item)

    def update_item_animations(self, dt):
        """Update all animating items"""
        for item in self.animating_items[:]:  # Copy list to allow removal
            if item.get('animating', False):
                # Increment progress with ease-out curve
                item['anim_progress'] = min(1.0, item['anim_progress'] + dt * self.animation_speed)
                t = item['anim_progress']

                # Ease-out cubic: 1 - (1-t)^3
                ease_t = 1 - pow(1 - t, 3)

                # Lerp position
                start_x, start_y = item['start_pos']
                target_x, target_y = item['target_pos']
                item['pos'] = [
                    start_x + (target_x - start_x) * ease_t,
                    start_y + (target_y - start_y) * ease_t
                ]

                # Check if animation complete
                if item['anim_progress'] >= 1.0:
                    item['pos'] = item['target_pos']
                    item['animating'] = False
                    self.animating_items.remove(item)

                    # Spawn particles when item lands
                    self.spawn_landing_particles(item)

    def spawn_landing_particles(self, item):
        """Spawn particles when item is placed"""
        import random
        center_x = item['pos'][0] + 30  # Item width/2
        center_y = item['pos'][1] + 30

        # Determine color based on mode
        if self.mode == 'unpack':
            color = (150, 255, 150)  # Hopeful green
        else:
            color = (255, 150, 150)  # Defeated red

        # Spawn 8-12 particles in a burst
        for i in range(random.randint(8, 12)):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(50, 100)
            particle = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 30,  # Slight upward bias
                'life': 1.0,  # 1.0 = full life, 0.0 = dead
                'size': random.randint(3, 6),
                'color': color
            }
            self.particles.append(particle)

    def update_particles(self, dt):
        """Update particle physics and lifetime"""
        for particle in self.particles[:]:
            # Move particle
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt

            # Apply gravity
            particle['vy'] += 200 * dt

            # Fade out
            particle['life'] -= dt * 2.0  # Fade over 0.5 seconds

            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        """Draw all active particles"""
        for particle in self.particles:
            alpha = int(particle['life'] * 255)
            color = (*particle['color'], alpha)

            # Draw particle as circle with alpha
            particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(particle_surf, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))

    def lerp_color(self, color1, color2, t):
        """Linear interpolate between two colors"""
        return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))

    def draw_gradient_rect(self, screen, rect, color1, color2):
        """Draw a vertical gradient rectangle"""
        for i in range(rect.height):
            blend = i / rect.height
            color = self.lerp_color(color1, color2, blend)
            pygame.draw.line(screen, color, (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))

    def draw_text_with_shadow(self, screen, text, font, pos, color):
        """Draw text with subtle shadow"""
        # Shadow
        shadow_surf = font.render(text, True, (0, 0, 0))
        screen.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
        # Text
        text_surf = font.render(text, True, color)
        screen.blit(text_surf, pos)
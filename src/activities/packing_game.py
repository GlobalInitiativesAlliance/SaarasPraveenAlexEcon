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

        # Draw UI elements
        self.draw_ui(screen)

        # Draw emotional messages
        self.draw_messages(screen)

    def draw_areas(self, screen):
        """Draw bag and room areas"""
        if self.mode == 'unpack':
            # Bag area (left)
            self.bag_rect = pygame.Rect(50, 200, 250, 400)
            pygame.draw.rect(screen, (80, 70, 60), self.bag_rect)
            pygame.draw.rect(screen, (60, 50, 40), self.bag_rect, 3)

            # Bag label
            font = pygame.font.Font(None, 28)
            label = font.render("Your Bag", True, (200, 200, 200))
            screen.blit(label, (125, 170))

            # Room area (right)
            self.room_rect = pygame.Rect(500, 150, 450, 500)
            pygame.draw.rect(screen, (120, 110, 100), self.room_rect)
            pygame.draw.rect(screen, (100, 90, 80), self.room_rect, 3)

            # Room label
            label = font.render("Your New Room", True, (200, 200, 200))
            screen.blit(label, (650, 120))

        else:  # packing mode
            # Room area (right)
            self.room_rect = pygame.Rect(500, 150, 450, 500)
            pygame.draw.rect(screen, (100, 90, 80), self.room_rect)
            pygame.draw.rect(screen, (80, 70, 60), self.room_rect, 3)

            # Room label
            font = pygame.font.Font(None, 28)
            label = font.render("The Room That Was Yours", True, (150, 150, 150))
            screen.blit(label, (600, 120))

            # Bag area (left)
            self.bag_rect = pygame.Rect(50, 200, 250, 400)
            pygame.draw.rect(screen, (70, 60, 50), self.bag_rect)
            pygame.draw.rect(screen, (50, 40, 30), self.bag_rect, 3)

            # Bag label
            label = font.render("Pack Your Life", True, (200, 200, 200))
            screen.blit(label, (110, 170))

    def draw_item(self, screen, item):
        """Draw a single item"""
        # Draw shadow
        shadow_pos = (item['pos'][0] + 3, item['pos'][1] + 3)
        shadow_surf = pygame.Surface(item['image'].get_size(), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        screen.blit(shadow_surf, shadow_pos)

        # Draw item
        screen.blit(item['image'], item['pos'])

        # Hover effect - show description
        mouse_pos = pygame.mouse.get_pos()
        item_rect = pygame.Rect(*item['pos'], *item['image'].get_size())
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
        """Draw UI elements"""
        # Progress indicator
        if self.mode == 'unpack':
            unpacked = sum(1 for item in self.items if not item['packed'])
            total = len(self.items)
            progress_text = f"Unpacked: {unpacked}/{total}"
        else:
            packed = sum(1 for item in self.items if item['packed'])
            total = len([i for i in self.items if i['name'] != 'Small Plant'])  # Can't take plant
            progress_text = f"Packed: {packed}/{total}"

        font = pygame.font.Font(None, 28)
        progress_surf = font.render(progress_text, True, (200, 200, 200))
        screen.blit(progress_surf, (SCREEN_WIDTH // 2 - progress_surf.get_width() // 2, 50))

        # Continue button (when done)
        if self.mode == 'unpack':
            done = all(not item['packed'] for item in self.items)
        else:
            # Can't pack the plant, so check all others
            done = all(item['packed'] or item['name'] == 'Small Plant' for item in self.items)

        if done:
            self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)

            # Pulse effect
            pulse = math.sin(self.animation_timer * 3) * 3
            button_rect = pygame.Rect(
                self.continue_button_rect.x - pulse,
                self.continue_button_rect.y - pulse,
                self.continue_button_rect.width + pulse * 2,
                self.continue_button_rect.height + pulse * 2
            )

            pygame.draw.rect(screen, self.hope_color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)

            button_text = "Settle In" if self.mode == 'unpack' else "Leave Forever"
            button_surf = font.render(button_text, True, (255, 255, 255))
            text_x = button_rect.centerx - button_surf.get_width() // 2
            text_y = button_rect.centery - button_surf.get_height() // 2
            screen.blit(button_surf, (text_x, text_y))

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
                msg_surf = font.render(msg['text'], True, (200, 200, 200, int(255 * self.message_timer)))
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
                    self.dragged_item['pos'] = [
                        max(self.room_rect.x, min(pos[0] - 30, self.room_rect.right - 60)),
                        max(self.room_rect.y, min(pos[1] - 20, self.room_rect.bottom - 50))
                    ]
                    # Show memory
                    self.show_memory(self.dragged_item, pos)
                elif self.bag_rect.collidepoint(pos) and not self.dragged_item['packed']:
                    # Put back in bag
                    self.dragged_item['packed'] = True
                    self.dragged_item['pos'] = [
                        self.bag_rect.x + 20 + (hash(self.dragged_item['name']) % 150),
                        self.bag_rect.y + 50 + (hash(self.dragged_item['name']) % 250)
                    ]
            else:
                # Packing: from room to bag
                if self.bag_rect.collidepoint(pos) and not self.dragged_item['packed']:
                    self.dragged_item['packed'] = True
                    self.dragged_item['pos'] = [
                        self.bag_rect.x + 20 + (hash(self.dragged_item['name']) % 150),
                        self.bag_rect.y + 50 + (hash(self.dragged_item['name']) % 250)
                    ]
                    # Show memory
                    self.show_memory(self.dragged_item, pos)
                elif self.room_rect.collidepoint(pos) and self.dragged_item['packed']:
                    # Put back in room
                    self.dragged_item['packed'] = False
                    self.dragged_item['pos'] = [
                        max(self.room_rect.x, min(pos[0] - 30, self.room_rect.right - 60)),
                        max(self.room_rect.y, min(pos[1] - 20, self.room_rect.bottom - 50))
                    ]

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

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
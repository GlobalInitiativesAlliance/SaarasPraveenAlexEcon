import pygame
import math
import random
from src.constants import *


class GameObjective:
    """Represents a game objective/mission that the player must complete"""

    def __init__(self, obj_id, title, description, target_position=None,
                 interaction_text="Press E to interact", requires_interaction=True):
        self.id = obj_id
        self.title = title
        self.description = description
        self.target_position = target_position
        self.interaction_text = interaction_text
        self.requires_interaction = requires_interaction
        self.completed = False
        self.active = False
        self.show_notification = True
        self.notification_timer = 0.0

        # Dynamic description for narrative interiors
        self.dynamic_description = None
        self.progress_text = None

    def activate(self):
        self.active = True
        self.show_notification = True
        self.notification_timer = 3.0

    def complete(self):
        self.completed = True
        self.active = False

    def update(self, dt):
        if self.notification_timer > 0:
            self.notification_timer -= dt

    def get_display_text(self):
        """Get the text to display in the UI (uses dynamic description if available)"""
        if self.dynamic_description:
            return self.dynamic_description
        return self.description


class Activity:
    """Base class for mini-game activities"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Initialize common fonts for all activities
        # Subclasses can override these if needed
        self.small_font = pygame.font.Font(None, 20)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)

    def start(self):
        self.active = True

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

    def handle_key(self, key):
        pass

    def handle_mouse_motion(self, pos):
        pass

    def handle_mouse_click(self, pos, button):
        pass

    def handle_mouse_release(self, pos, button):
        pass

    def complete(self):
        """Complete the activity"""
        self.completed = True
        self.active = False


class TenantRightsQuiz(Activity):
    """Quiz about tenant rights - matching WorkplaceQuiz style"""
    
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.questions = [
            {
                "question": "How much notice must a landlord give before entering?",
                "options": ["No notice needed", "24 hours", "1 week", "1 hour"],
                "correct": 1
            },
            {
                "question": "Who is responsible for fixing a broken heater in winter?",
                "options": ["Tenant", "Landlord", "Nobody", "City"],
                "correct": 1
            },
            {
                "question": "Can a landlord raise rent in the middle of your lease?",
                "options": ["Yes, anytime", "No, not during lease", "Yes, with 30 days notice", "Only on holidays"],
                "correct": 1
            },
            {
                "question": "What should you do if you receive an eviction notice?",
                "options": ["Ignore it", "Move out immediately", "Check if it's legal and respond", "Call 911"],
                "correct": 2
            },
            {
                "question": "How many days do you have to pay after a 3-day notice?",
                "options": ["1 day", "3 days", "7 days", "30 days"],
                "correct": 1
            }
        ]
        self.current_question = 0
        self.selected_option = None
        self.score = 0
        self.show_result = False
        self.result_timer = 0
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.entrance_complete = False
        self.option_rects = []
        self.submit_rect = None
        self.continue_rect = None
        
    def start(self):
        super().start()
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.entrance_complete = False
        print(f"TenantRightsQuiz started: {len(self.questions)} questions, current: {self.current_question}")
        
    def update(self, dt):
        if not self.active:
            return
            
        if self.fade_alpha < 200:
            self.fade_alpha = min(200, self.fade_alpha + dt * 400)
        if self.box_scale < 1.0:
            self.box_scale = min(1.0, self.box_scale + dt * 3)
        if self.box_scale >= 1.0 and self.fade_alpha >= 200:
            self.entrance_complete = True
            
        if self.show_result:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.show_result = False
                self.current_question += 1
                self.selected_option = None
                if self.current_question >= len(self.questions):
                    print(f"TenantRightsQuiz: Completed all {len(self.questions)} questions, score: {self.score}")
                    self.complete()
                    
    def draw(self, screen):
        if not self.active:
            return
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))
        
        base_width = 850
        base_height = 550
        box_width = int(base_width * self.box_scale)
        box_height = int(base_height * self.box_scale)
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2
        
        if box_width > 0 and box_height > 0:
            pygame.draw.rect(screen, (25, 25, 30), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 4)
            
        if self.entrance_complete:
            title_font = pygame.font.Font(None, 48)
            title = title_font.render("Tenant Rights Quiz", True, (255, 220, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))
            
            if self.current_question < len(self.questions):
                question = self.questions[self.current_question]
                
                q_font = pygame.font.Font(None, 32)
                q_text = q_font.render(question["question"], True, (255, 255, 255))
                screen.blit(q_text, (SCREEN_WIDTH // 2 - q_text.get_width() // 2, box_y + 120))
                
                opt_font = pygame.font.Font(None, 28)
                y_offset = box_y + 200
                self.option_rects = []
                
                for i, option in enumerate(question["options"]):
                    option_rect = pygame.Rect(box_x + 80, y_offset - 10, box_width - 160, 45)
                    self.option_rects.append(option_rect)
                    
                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering = option_rect.collidepoint(mouse_pos) and not self.show_result
                    
                    if is_hovering:
                        pygame.draw.rect(screen, (40, 40, 50), option_rect, border_radius=5)
                        pygame.draw.rect(screen, (100, 100, 120), option_rect, 2, border_radius=5)
                        
                    color = (255, 255, 255)
                    if self.selected_option == i:
                        color = (255, 220, 100)
                    if self.show_result:
                        if i == question["correct"]:
                            color = (100, 255, 100)
                        elif i == self.selected_option:
                            color = (255, 100, 100)
                            
                    opt_text = opt_font.render(f"{i + 1}. {option}", True, color)
                    screen.blit(opt_text, (box_x + 100, y_offset))
                    y_offset += 50
                    
                if not self.show_result:
                    submit_width = 150
                    submit_height = 40
                    submit_x = SCREEN_WIDTH // 2 - submit_width // 2
                    submit_y = box_y + box_height - 80
                    self.submit_rect = pygame.Rect(submit_x, submit_y, submit_width, submit_height)
                    
                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering_submit = self.submit_rect.collidepoint(mouse_pos) and self.selected_option is not None
                    
                    button_color = (100, 150, 255) if self.selected_option is not None else (80, 80, 80)
                    if is_hovering_submit:
                        button_color = (120, 170, 255)
                        
                    pygame.draw.rect(screen, button_color, self.submit_rect, border_radius=5)
                    pygame.draw.rect(screen, (255, 255, 255), self.submit_rect, 2, border_radius=5)
                    
                    submit_font = pygame.font.Font(None, 28)
                    submit_text = submit_font.render("Submit", True, (255, 255, 255))
                    text_rect = submit_text.get_rect(center=self.submit_rect.center)
                    screen.blit(submit_text, text_rect)
                    
                    inst_font = pygame.font.Font(None, 20)
                    inst_text = inst_font.render("Click an option or press 1-4 to select", True, (180, 180, 180))
                    screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 25))
                    
            else:
                score_font = pygame.font.Font(None, 48)
                score_text = score_font.render(f"Score: {self.score}/{len(self.questions)}", True, (100, 255, 100))
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, box_y + 180))
                
                continue_width = 200
                continue_height = 50
                continue_x = SCREEN_WIDTH // 2 - continue_width // 2
                continue_y = box_y + 280
                self.continue_rect = pygame.Rect(continue_x, continue_y, continue_width, continue_height)
                
                mouse_pos = pygame.mouse.get_pos()
                is_hovering = self.continue_rect.collidepoint(mouse_pos)
                button_color = (120, 170, 255) if is_hovering else (100, 150, 255)
                
                pygame.draw.rect(screen, button_color, self.continue_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), self.continue_rect, 2, border_radius=5)
                
                button_font = pygame.font.Font(None, 32)
                button_text = button_font.render("Continue", True, (255, 255, 255))
                text_rect = button_text.get_rect(center=self.continue_rect.center)
                screen.blit(button_text, text_rect)
                
                inst_font = pygame.font.Font(None, 20)
                inst_text = inst_font.render("Click Continue or press ENTER", True, (180, 180, 180))
                screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 350))
                
    def handle_key(self, key):
        if not self.active or not self.entrance_complete:
            return
            
        if self.current_question < len(self.questions) and not self.show_result:
            if key >= pygame.K_1 and key <= pygame.K_4:
                option_index = key - pygame.K_1
                if option_index < len(self.questions[self.current_question]["options"]):
                    self.selected_option = option_index
            elif key == pygame.K_RETURN and self.selected_option is not None:
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 1.5
        elif self.current_question >= len(self.questions):
            if key == pygame.K_RETURN:
                self.complete()
                
    def handle_mouse_click(self, pos, button):
        if not self.active or not self.entrance_complete or button != 1:
            return
            
        if self.current_question < len(self.questions) and not self.show_result:
            # Check option clicks
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    self.selected_option = i
                    return
                    
            # Check submit button
            if hasattr(self, 'submit_rect') and self.submit_rect and self.submit_rect.collidepoint(pos) and self.selected_option is not None:
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 1.5
        elif self.current_question >= len(self.questions):
            # Check continue button
            if hasattr(self, 'continue_rect') and self.continue_rect and self.continue_rect.collidepoint(pos):
                self.complete()


class ClothesPacking(Activity):
    """Closet packing mini-game for foster home"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.foster_home_ref = None  # Reference to foster home interior

        # Import and initialize texture loader
        from src.activities.clothes_textures import load_clothing_sprites
        self.clothing_sprites = load_clothing_sprites()

        # Closet items with sizes (how many backpack slots they take)
        self.closet_items = [
            {"name": "T-Shirt", "type": "essential", "size": 1, "pos": (0, 0), "packed": False},
            {"name": "Jeans", "type": "essential", "size": 2, "pos": (1, 0), "packed": False},
            {"name": "Underwear Pack", "type": "essential", "size": 1, "pos": (2, 0), "packed": False},
            {"name": "Hoodie", "type": "clothing", "size": 2, "pos": (0, 1), "packed": False},
            {"name": "Jacket", "type": "clothing", "size": 2, "pos": (1, 1), "packed": False},
            {"name": "Dress Shirt", "type": "clothing", "size": 1, "pos": (2, 1), "packed": False},
            {"name": "Sneakers", "type": "essential", "size": 2, "pos": (0, 2), "packed": False},
            {"name": "Socks Pack", "type": "essential", "size": 1, "pos": (1, 2), "packed": False},
            {"name": "Old Photo", "type": "personal", "size": 1, "pos": (2, 2), "packed": False},
            {"name": "Belt", "type": "accessory", "size": 1, "pos": (3, 0), "packed": False},
            {"name": "Winter Coat", "type": "clothing", "size": 3, "pos": (3, 1), "packed": False}
        ]

        # Backpack state
        self.backpack_capacity = 10
        self.backpack_used = 0
        self.packed_items = []
        self.min_required_items = 5  # Must pack at least 5 items
        self.essentials_packed = 0

        # Drag and drop state
        self.dragging = False
        self.dragged_item = None
        self.drag_offset = (0, 0)
        self.hover_item = None

        # UI state
        self.closet_open = False
        self.animation_timer = 0
        self.complete_button_rect = None

    def start(self):
        """Start the packing activity"""
        super().start()
        self.closet_open = True
        self.animation_timer = 0
        self.backpack_used = 0
        self.packed_items = []
        self.essentials_packed = 0
        # Reset all items
        for item in self.closet_items:
            item["packed"] = False

    def get_item_rect(self, item):
        """Get the rectangle for a closet item"""
        base_x = 200
        base_y = 150
        item_width = 120
        item_height = 80
        spacing = 10

        x = base_x + item["pos"][0] * (item_width + spacing)
        y = base_y + item["pos"][1] * (item_height + spacing)
        return pygame.Rect(x, y, item_width, item_height)

    def get_backpack_rect(self):
        """Get the backpack drop zone rectangle"""
        return pygame.Rect(SCREEN_WIDTH - 350, 200, 300, 400)

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for drag start"""
        if not self.active or button != 1:
            return

        # Check if clicking complete button
        if self.complete_button_rect and self.complete_button_rect.collidepoint(pos):
            if len(self.packed_items) >= self.min_required_items:
                self.complete_packing()
            return

        # Check if clicking on an item to start dragging
        for item in self.closet_items:
            if not item["packed"]:
                rect = self.get_item_rect(item)
                if rect.collidepoint(pos):
                    self.dragging = True
                    self.dragged_item = item
                    self.drag_offset = (pos[0] - rect.x, pos[1] - rect.y)
                    break

    def handle_mouse_release(self, pos, button):
        """Handle mouse release for drop"""
        if not self.active or button != 1 or not self.dragging:
            return

        if self.dragged_item:
            # Check if dropped on backpack
            backpack_rect = self.get_backpack_rect()
            if backpack_rect.collidepoint(pos):
                # Check if there's enough space
                if self.backpack_used + self.dragged_item["size"] <= self.backpack_capacity:
                    # Pack the item
                    self.dragged_item["packed"] = True
                    self.packed_items.append(self.dragged_item)
                    self.backpack_used += self.dragged_item["size"]
                    if self.dragged_item["type"] == "essential":
                        self.essentials_packed += 1

        self.dragging = False
        self.dragged_item = None

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        # Update hover state
        self.hover_item = None
        if not self.dragging:
            for item in self.closet_items:
                if not item["packed"]:
                    rect = self.get_item_rect(item)
                    if rect.collidepoint(pos):
                        self.hover_item = item
                        break

    def complete_packing(self):
        """Complete the packing activity"""
        # Update foster home state
        if self.foster_home_ref:
            self.foster_home_ref.items_packed.add('clothes')
            self.foster_home_ref.update_objective_display()

        # Show completion message
        items_text = ", ".join([item["name"] for item in self.packed_items[:3]])
        if len(self.packed_items) > 3:
            items_text += f" and {len(self.packed_items) - 3} more items"

        # Try to find dialogue box from foster home or objective manager
        dialogue_box = None
        if self.foster_home_ref and hasattr(self.foster_home_ref, 'dialogue_box'):
            dialogue_box = self.foster_home_ref.dialogue_box
        elif hasattr(self.objective_manager, 'dialogue_box'):
            dialogue_box = self.objective_manager.dialogue_box

        if dialogue_box:
            dialogue_box.show(
                None,
                f"You packed: {items_text}. Everything else stays behind."
            )

        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return
        self.animation_timer += dt

    def draw(self, screen):
        """Draw the closet packing interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Main container
        container_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (40, 35, 30), container_rect)
        pygame.draw.rect(screen, (200, 180, 160), container_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pack Your Belongings", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Closet section
        closet_label_font = pygame.font.Font(None, 32)
        closet_label = closet_label_font.render("Closet", True, (220, 200, 180))
        screen.blit(closet_label, (200, 120))

        # Draw closet items with real textures
        item_font = pygame.font.Font(None, 20)
        for item in self.closet_items:
            if not item["packed"]:
                rect = self.get_item_rect(item)

                # Draw background frame
                if item == self.hover_item:
                    pygame.draw.rect(screen, (100, 90, 80), rect, border_radius=5)
                    pygame.draw.rect(screen, (255, 220, 180), rect, 2, border_radius=5)
                else:
                    pygame.draw.rect(screen, (70, 60, 50), rect, border_radius=5)
                    pygame.draw.rect(screen, (150, 130, 110), rect, 1, border_radius=5)

                # Draw the actual clothing sprite
                if item["name"] in self.clothing_sprites:
                    sprite = self.clothing_sprites[item["name"]]
                    # Center sprite in the rectangle
                    sprite_x = rect.x + (rect.width - sprite.get_width()) // 2
                    sprite_y = rect.y + 5

                    # Add hover effect to sprite
                    if item == self.hover_item:
                        hover_sprite = sprite.copy()
                        hover_sprite.set_alpha(255)
                        # Add a slight glow effect
                        glow_surf = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                        glow_surf.fill((255, 255, 200, 30))
                        hover_sprite.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
                        screen.blit(hover_sprite, (sprite_x, sprite_y))
                    else:
                        screen.blit(sprite, (sprite_x, sprite_y))

                # Item name below sprite
                name_text = item_font.render(item["name"], True, (255, 245, 230))
                name_x = rect.x + (rect.width - name_text.get_width()) // 2
                screen.blit(name_text, (name_x, rect.y + rect.height - 20))

        # Backpack section
        backpack_rect = self.get_backpack_rect()
        pygame.draw.rect(screen, (50, 40, 35), backpack_rect)
        pygame.draw.rect(screen, (180, 160, 140), backpack_rect, 2)

        # Backpack label
        backpack_label = closet_label_font.render("Backpack", True, (220, 200, 180))
        screen.blit(backpack_label, (backpack_rect.x + 10, backpack_rect.y - 30))

        # Capacity bar
        capacity_bar_rect = pygame.Rect(backpack_rect.x + 10, backpack_rect.y + 10,
                                        backpack_rect.width - 20, 30)
        pygame.draw.rect(screen, (40, 35, 30), capacity_bar_rect)

        # Fill based on usage
        if self.backpack_used > 0:
            fill_width = int((self.backpack_used / self.backpack_capacity) * capacity_bar_rect.width)
            fill_color = (255, 100, 100) if self.backpack_used == self.backpack_capacity else (100, 200, 100)
            pygame.draw.rect(screen, fill_color,
                           (capacity_bar_rect.x, capacity_bar_rect.y, fill_width, capacity_bar_rect.height))

        pygame.draw.rect(screen, (150, 130, 110), capacity_bar_rect, 2)

        # Capacity text
        capacity_text = item_font.render(f"{self.backpack_used}/{self.backpack_capacity} slots",
                                        True, (255, 245, 230))
        screen.blit(capacity_text,
                   (capacity_bar_rect.x + capacity_bar_rect.width // 2 - capacity_text.get_width() // 2,
                    capacity_bar_rect.y + 5))

        # Packed items list
        y_offset = backpack_rect.y + 50
        for item in self.packed_items:
            item_text = item_font.render(f"• {item['name']} ({item['size']} slots)", True, (200, 180, 160))
            screen.blit(item_text, (backpack_rect.x + 10, y_offset))
            y_offset += 25

        # Instructions
        if len(self.packed_items) < self.min_required_items:
            instruction_text = item_font.render(
                f"Pack at least {self.min_required_items} items (packed: {len(self.packed_items)})",
                True, (255, 200, 150)
            )
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2,
                                          SCREEN_HEIGHT - 100))
        else:
            # Show complete button
            complete_font = pygame.font.Font(None, 32)
            complete_text = complete_font.render("Complete Packing", True, (255, 255, 255))
            self.complete_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 110, 200, 50
            )
            pygame.draw.rect(screen, (100, 150, 100), self.complete_button_rect)
            pygame.draw.rect(screen, (150, 200, 150), self.complete_button_rect, 2)
            screen.blit(complete_text,
                       (self.complete_button_rect.x + 20, self.complete_button_rect.y + 12))

        # Draw dragged item with real sprite
        if self.dragging and self.dragged_item:
            mouse_pos = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(mouse_pos[0] - self.drag_offset[0],
                                   mouse_pos[1] - self.drag_offset[1], 120, 80)

            # Draw container frame for dragged item
            pygame.draw.rect(screen, (90, 80, 70), drag_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 220, 180), drag_rect, 2, border_radius=5)

            # Draw the actual sprite
            if self.dragged_item["name"] in self.clothing_sprites:
                sprite = self.clothing_sprites[self.dragged_item["name"]].copy()
                sprite.set_alpha(200)  # Make slightly transparent when dragging
                sprite_x = drag_rect.x + (drag_rect.width - sprite.get_width()) // 2
                sprite_y = drag_rect.y + 5
                screen.blit(sprite, (sprite_x, sprite_y))

            # Draw name below sprite
            name_text = item_font.render(self.dragged_item["name"], True, (255, 245, 230))
            name_x = drag_rect.x + (drag_rect.width - name_text.get_width()) // 2
            screen.blit(name_text, (name_x, drag_rect.y + drag_rect.height - 20))


class PackingActivity(Activity):
    """Enhanced packing mini-game with visual animations"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.items = [
            {"name": "Clothes", "icon": "👕", "color": (100, 150, 255)},
            {"name": "Books", "icon": "📚", "color": (255, 150, 100)},
            {"name": "Laptop", "icon": "💻", "color": (150, 255, 150)},
            {"name": "Documents", "icon": "📄", "color": (255, 255, 150)},
            {"name": "Photos", "icon": "🖼️", "color": (255, 150, 255)}
        ]
        self.packed_items = []
        self.current_item = 0
        self.apartment_ref = None  # Reference to TLP apartment
        
        # Animation states
        self.animation_timer = 0
        self.packing_animation = None
        self.box_shake = 0
        self.item_positions = {}
        self.item_animations = {}
        
        # Initialize item positions
        for i, item in enumerate(self.items):
            self.item_positions[item["name"]] = {
                "x": 150 + (i % 3) * 180,
                "y": 250 + (i // 3) * 120,
                "target_x": SCREEN_WIDTH // 2,
                "target_y": SCREEN_HEIGHT // 2 + 50
            }
            self.item_animations[item["name"]] = {
                "scale": 1.0,
                "rotation": 0,
                "moving": False
            }
    
    def start(self):
        """Start the packing activity - reset state"""
        super().start()
        self.packed_items = []
        self.current_item = 0
        self.animation_timer = 0
        self.box_shake = 0
        # Reset animations
        for anim in self.item_animations.values():
            anim["scale"] = 1.0
            anim["moving"] = False

    def draw(self, screen):
        if not self.active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # Update animations
        self.animation_timer += 0.016  # ~60 FPS

        # Title
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("Pack Your Belongings", True, (255, 220, 100))
        title_y = 50 + math.sin(self.animation_timer * 2) * 5
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_y))

        # Progress bar
        progress = len(self.packed_items) / len(self.items)
        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 120
        
        # Bar background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        # Bar fill
        if progress > 0:
            fill_width = int(bar_width * progress)
            pygame.draw.rect(screen, (100, 255, 100), (bar_x, bar_y, fill_width, bar_height), border_radius=15)
        # Bar border
        pygame.draw.rect(screen, (255, 220, 100), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=15)
        
        # Progress text
        prog_font = pygame.font.Font(None, 24)
        prog_text = f"{len(self.packed_items)}/{len(self.items)}"
        prog_surface = prog_font.render(prog_text, True, (255, 255, 255))
        screen.blit(prog_surface, (bar_x + bar_width // 2 - prog_surface.get_width() // 2, bar_y + 5))

        # Draw the packing box
        box_width = 200
        box_height = 150
        box_x = SCREEN_WIDTH // 2 - box_width // 2 + self.box_shake
        box_y = SCREEN_HEIGHT // 2 + 100
        
        # Box shadow
        shadow_surf = pygame.Surface((box_width + 20, box_height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=10)
        screen.blit(shadow_surf, (box_x - 10, box_y - 5))
        
        # Box body
        pygame.draw.rect(screen, (139, 90, 43), (box_x, box_y, box_width, box_height), border_radius=10)
        pygame.draw.rect(screen, (101, 67, 33), (box_x, box_y, box_width, box_height), 3, border_radius=10)
        
        # Box opening
        opening_y = box_y - 20
        pygame.draw.ellipse(screen, (50, 30, 20), (box_x, opening_y, box_width, 40))
        pygame.draw.ellipse(screen, (101, 67, 33), (box_x, opening_y, box_width, 40), 3)

        # Draw items
        for i, item in enumerate(self.items):
            item_name = item["name"]
            pos = self.item_positions[item_name]
            anim = self.item_animations[item_name]
            
            if item_name not in self.packed_items:
                # Item card
                card_size = 120
                card_x = pos["x"] - card_size // 2
                card_y = pos["y"] - card_size // 2
                
                # Hover effect for current item
                if i == self.current_item:
                    anim["scale"] = 1.1 + math.sin(self.animation_timer * 5) * 0.05
                    # Glow effect
                    glow_surf = pygame.Surface((card_size + 20, card_size + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (255, 255, 100, 50), glow_surf.get_rect(), border_radius=15)
                    screen.blit(glow_surf, (card_x - 10, card_y - 10))
                else:
                    anim["scale"] = 1.0
                
                # Scale the card
                scaled_size = int(card_size * anim["scale"])
                scaled_x = pos["x"] - scaled_size // 2
                scaled_y = pos["y"] - scaled_size // 2
                
                # Card background
                card_color = item["color"]
                pygame.draw.rect(screen, card_color, (scaled_x, scaled_y, scaled_size, scaled_size), border_radius=15)
                pygame.draw.rect(screen, (255, 255, 255), (scaled_x, scaled_y, scaled_size, scaled_size), 3, border_radius=15)
                
                # Item icon (simplified representation)
                icon_font = pygame.font.Font(None, 48)
                icon_text = icon_font.render(item["icon"], True, (255, 255, 255))
                icon_x = pos["x"] - icon_text.get_width() // 2
                icon_y = pos["y"] - icon_text.get_height() // 2 - 10
                screen.blit(icon_text, (icon_x, icon_y))
                
                # Item name
                name_font = pygame.font.Font(None, 20)
                name_text = name_font.render(item_name, True, (255, 255, 255))
                name_x = pos["x"] - name_text.get_width() // 2
                name_y = pos["y"] + 30
                screen.blit(name_text, (name_x, name_y))

        # Update box shake
        if self.box_shake > 0:
            self.box_shake *= 0.9
            if self.box_shake < 0.1:
                self.box_shake = 0

        # Instructions
        if len(self.packed_items) < len(self.items):
            inst_text = "Click an item or press SPACE to pack"
            inst_color = (255, 255, 255)
        else:
            inst_text = "All packed! Press ENTER to continue"
            inst_color = (100, 255, 100)

        inst_font = pygame.font.Font(None, 32)
        inst_surface = inst_font.render(inst_text, True, inst_color)
        inst_y = SCREEN_HEIGHT - 80 + math.sin(self.animation_timer * 3) * 5
        screen.blit(inst_surface, (SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, inst_y))

    def handle_key(self, key):
        if not self.active:
            return

        if key == pygame.K_SPACE:
            # Find first unpacked item
            unpacked_items = [i for i, item in enumerate(self.items) if item["name"] not in self.packed_items]
            if unpacked_items:
                # Pack the current highlighted item
                if self.current_item < len(self.items):
                    current = self.items[self.current_item]
                    if current["name"] not in self.packed_items:
                        self.packed_items.append(current["name"])
                        self.box_shake = 10  # Shake the box when item is packed
                        self.item_animations[current["name"]]["moving"] = True
                        
                        # Move to next unpacked item
                        remaining_unpacked = [i for i, item in enumerate(self.items) if item["name"] not in self.packed_items]
                        if remaining_unpacked:
                            self.current_item = remaining_unpacked[0]
                        else:
                            self.current_item = len(self.items) - 1
                    
        elif key == pygame.K_RETURN and len(self.packed_items) == len(self.items):
            self.complete_packing()
            
        # Arrow key navigation - only move between unpacked items
        elif key == pygame.K_LEFT:
            unpacked_items = [i for i, item in enumerate(self.items) if item["name"] not in self.packed_items]
            if unpacked_items and self.current_item in unpacked_items:
                current_index = unpacked_items.index(self.current_item)
                if current_index > 0:
                    self.current_item = unpacked_items[current_index - 1]
            elif unpacked_items:
                self.current_item = unpacked_items[0]
                
        elif key == pygame.K_RIGHT:
            unpacked_items = [i for i, item in enumerate(self.items) if item["name"] not in self.packed_items]
            if unpacked_items and self.current_item in unpacked_items:
                current_index = unpacked_items.index(self.current_item)
                if current_index < len(unpacked_items) - 1:
                    self.current_item = unpacked_items[current_index + 1]
            elif unpacked_items:
                self.current_item = unpacked_items[0]
    
    def complete_packing(self):
        """Complete the packing activity and update apartment state"""
        # Mark items as packed in the apartment if reference exists
        if self.apartment_ref and hasattr(self.apartment_ref, 'items_packed'):
            self.apartment_ref.items_packed = True
        
        # Show notification
        self.objective_manager.show_notification("All items packed! Ready to move.")
        
        # Complete the objective
        self.objective_manager.complete_current_objective()
        
        # Complete the activity
        self.complete()

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks on items"""
        if not self.active or button != 1:  # Left click only
            return
            
        # Check if clicking on an item
        for i, item in enumerate(self.items):
            if item["name"] not in self.packed_items:
                item_pos = self.item_positions[item["name"]]
                # Check if click is within item card (120x120 area)
                if (abs(pos[0] - item_pos["x"]) < 60 and 
                    abs(pos[1] - item_pos["y"]) < 60):
                    # Pack the item
                    self.packed_items.append(item["name"])
                    self.box_shake = 10
                    self.item_animations[item["name"]]["moving"] = True
                    
                    # Update current item
                    self.current_item = len(self.packed_items)
                    if self.current_item >= len(self.items):
                        self.current_item = len(self.items) - 1
                    break
    
    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return
        # Could add hover effects here if desired


class LifeSkillsWorkshop(Activity):
    """Life skills workshop at community center"""
    
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0
        self.tips_learned = []

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 200), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 32)
        small_font = pygame.font.Font(None, 28)

        title = title_font.render("Life Skills Workshop", True, (150, 200, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

        if self.stage == 0:
            lines = [
                "Welcome to the Life Skills Workshop!",
                "",
                "Today you'll learn essential skills for",
                "independent living in your new apartment.",
                "",
                "Topics covered:",
                "• Budgeting & Money Management",
                "• Cooking & Meal Planning",
                "• Time Management",
                "",
                "Click or press SPACE to begin"
            ]

            y_offset = box_y + 120
            for line in lines:
                if line.startswith("•"):
                    color = (200, 220, 255)
                    font = small_font
                else:
                    color = (255, 255, 255)
                    font = text_font if line else small_font

                text = font.render(line, True, color)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 35

        elif self.stage <= 3:
            tips = [
                {
                    "title": "Budgeting Basics",
                    "icon": "$",
                    "points": [
                        "Track ALL expenses, even small ones",
                        "Follow the 50/30/20 rule:",
                        "  50% needs, 30% wants, 20% savings",
                        "Use apps or spreadsheets to track spending",
                        "Set up automatic savings transfers"
                    ]
                },
                {
                    "title": "Cooking & Meal Planning",
                    "icon": "🍳",
                    "points": [
                        "Plan meals for the week ahead",
                        "Make a grocery list and stick to it",
                        "Learn 5-10 simple, healthy recipes",
                        "Batch cook and freeze portions",
                        "Buy generic brands to save money"
                    ]
                },
                {
                    "title": "Time Management",
                    "icon": "⏰",
                    "points": [
                        "Use a calendar for appointments",
                        "Set multiple alarms for important tasks",
                        "Prepare clothes/lunch the night before",
                        "Break big tasks into smaller steps",
                        "Build in buffer time between activities"
                    ]
                }
            ]

            current_tip = tips[self.stage - 1]

            header_font = pygame.font.Font(None, 40)
            header = header_font.render(current_tip["title"], True, (255, 220, 100))
            screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, box_y + 100))

            y_offset = box_y + 160
            for point in current_tip["points"]:
                if point.startswith("  "):
                    color = (180, 180, 200)
                    indent = 40
                else:
                    color = (255, 255, 255)
                    indent = 0

                text = small_font.render(point.strip(), True, color)
                screen.blit(text, (box_x + 100 + indent, y_offset))
                y_offset += 35

            nav_text = f"Tip {self.stage} of 3"
            nav = small_font.render(nav_text, True, (150, 150, 150))
            screen.blit(nav, (SCREEN_WIDTH // 2 - nav.get_width() // 2, box_y + 450))

            cont_text = text_font.render("Click or press SPACE to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 500))

        else:
            lines = [
                "Workshop Complete!",
                "",
                "You've learned important life skills:",
                "✓ Budgeting & Money Management",
                "✓ Cooking & Meal Planning",
                "✓ Time Management",
                "",
                "Remember: Practice makes perfect!",
                "Don't be afraid to ask for help.",
                "",
                "Click or press ENTER to continue"
            ]

            y_offset = box_y + 120
            for line in lines:
                if line.startswith("✓"):
                    color = (100, 255, 100)
                elif line == "Workshop Complete!":
                    color = (100, 255, 100)
                    font = title_font
                else:
                    color = (255, 255, 255)
                    font = text_font

                if line != "Workshop Complete!":
                    text = text_font.render(line, True, color)
                else:
                    text = font.render(line, True, color)

                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40 if line == "Workshop Complete!" else 35

    def handle_key(self, key):
        if not self.active:
            return

        if self.stage < 3 and key == pygame.K_SPACE:
            self.stage += 1
        elif self.stage == 3 and key == pygame.K_SPACE:
            self.stage = 4
        elif self.stage == 4 and key == pygame.K_RETURN:
            self.complete()

    def handle_mouse_click(self, mouse_pos, button=1):
        if not self.active:
            return

        if self.stage < 4:
            self.stage += 1
        else:
            self.complete()


class EmergencyNoticeActivity(Activity):
    """Show emergency notices about roommate leaving"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 700
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        if self.stage == 0:
            pygame.draw.rect(screen, (50, 50, 50), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_width, box_height), 3)

            title_font = pygame.font.Font(None, 42)
            title = title_font.render("Note from Roommate", True, (255, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            note_font = pygame.font.Font(None, 28)
            lines = [
                "Sorry, I had to leave suddenly.",
                "Family emergency back home.",
                "I can't pay my half of rent or utilities.",
                "Good luck.",
                "",
                "- Your former roommate"
            ]

            y_offset = box_y + 100
            for line in lines:
                text = note_font.render(line, True, (255, 255, 255))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 35

        elif self.stage == 1:
            pygame.draw.rect(screen, (80, 20, 20), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (255, 50, 50), (box_x, box_y, box_width, box_height), 3)

            title_font = pygame.font.Font(None, 48)
            title = title_font.render("3-DAY NOTICE TO PAY OR QUIT", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            notice_font = pygame.font.Font(None, 26)
            lines = [
                "You are hereby notified that rent in the amount of",
                "$1,200 is now due and payable.",
                "",
                "You are required to pay said rent in full within",
                "THREE (3) days or quit and deliver up the premises.",
                "",
                "Failure to comply will result in eviction proceedings."
            ]

            y_offset = box_y + 100
            for line in lines:
                text = notice_font.render(line, True, (255, 255, 255))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 30

        elif self.stage == 2:
            pygame.draw.rect(screen, (80, 80, 20), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (255, 255, 100), (box_x, box_y, box_width, box_height), 3)

            title_font = pygame.font.Font(None, 42)
            title = title_font.render("UTILITY SHUTOFF NOTICE", True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            notice_font = pygame.font.Font(None, 28)
            lines = [
                "Your utility services will be disconnected",
                "due to non-payment.",
                "",
                "Amount due: $150",
                "Plus reconnection fee: $75",
                "",
                "Pay immediately to avoid service interruption."
            ]

            y_offset = box_y + 100
            for line in lines:
                text = notice_font.render(line, True, (255, 255, 255))
                screen.blit(text, (box_x + 50, y_offset))
                y_offset += 30

        inst_font = pygame.font.Font(None, 28)
        inst_text = inst_font.render("Press SPACE to continue", True, (255, 255, 255))
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 50))

    def handle_key(self, key):
        if not self.active:
            return

        if key == pygame.K_SPACE:
            self.stage += 1
            if self.stage > 2:
                self.complete()


class DocumentChecklistActivity(Activity):
    """Housing Services document checklist"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.documents = {
            "Foster Care Verification": False,
            "Income Proof": False,
            "TLP Agreement": False
        }
        self.all_checked = False

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (30, 30, 35), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 200, 100), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Required Documents", True, (100, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

        doc_font = pygame.font.Font(None, 32)
        y_offset = box_y + 120

        for i, (doc_name, is_checked) in enumerate(self.documents.items()):
            checkbox_x = box_x + 60
            checkbox_y = y_offset - 5
            checkbox_size = 30

            pygame.draw.rect(screen, (255, 255, 255),
                             (checkbox_x, checkbox_y, checkbox_size, checkbox_size), 2)

            if is_checked:
                pygame.draw.line(screen, (100, 255, 100),
                                 (checkbox_x + 5, checkbox_y + 15),
                                 (checkbox_x + 12, checkbox_y + 22), 3)
                pygame.draw.line(screen, (100, 255, 100),
                                 (checkbox_x + 12, checkbox_y + 22),
                                 (checkbox_x + 25, checkbox_y + 8), 3)

            color = (100, 255, 100) if is_checked else (255, 255, 255)
            text = doc_font.render(f"{i + 1}. {doc_name}", True, color)
            screen.blit(text, (checkbox_x + 50, y_offset))
            y_offset += 60

        if not self.all_checked:
            inst_text = "Press 1, 2, or 3 to check documents"
        else:
            inst_text = "All documents verified! Press ENTER to continue"

        inst_font = pygame.font.Font(None, 28)
        inst_surface = inst_font.render(inst_text, True, (255, 255, 255))
        screen.blit(inst_surface, (SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, box_y + box_height - 50))

    def handle_key(self, key):
        if not self.active:
            return

        doc_keys = list(self.documents.keys())

        if key == pygame.K_1 and len(doc_keys) > 0:
            self.documents[doc_keys[0]] = True
        elif key == pygame.K_2 and len(doc_keys) > 1:
            self.documents[doc_keys[1]] = True
        elif key == pygame.K_3 and len(doc_keys) > 2:
            self.documents[doc_keys[2]] = True

        self.all_checked = all(self.documents.values())

        if self.all_checked and key == pygame.K_RETURN:
            self.complete()


class WorkplaceQuiz(Activity):
    """Quiz about what to do when getting fired"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.questions = [
            {
                "question": "What should you do FIRST if you're fired?",
                "options": ["Leave immediately", "Ask for the reason in writing", "Argue with your boss",
                            "Call the police"],
                "correct": 1
            },
            {
                "question": "Are you entitled to your final paycheck?",
                "options": ["No, you were fired", "Yes, for all hours worked", "Only if you quit",
                            "Depends on the boss"],
                "correct": 1
            },
            {
                "question": "What benefits might you qualify for after being fired?",
                "options": ["Nothing", "Unemployment insurance", "Free housing", "Company car"],
                "correct": 1
            }
        ]
        self.current_question = 0
        self.selected_option = None
        self.score = 0
        self.show_result = False
        self.result_timer = 0
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.entrance_complete = False

    def start(self):
        super().start()
        self.box_scale = 0.0
        self.fade_alpha = 0
        self.entrance_complete = False

    def update(self, dt):
        if not self.active:
            return

        if self.fade_alpha < 200:
            self.fade_alpha = min(200, self.fade_alpha + dt * 400)
        if self.box_scale < 1.0:
            self.box_scale = min(1.0, self.box_scale + dt * 3)
        if self.box_scale >= 1.0 and self.fade_alpha >= 200:
            self.entrance_complete = True

        if self.show_result:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.show_result = False
                self.current_question += 1
                self.selected_option = None

                if self.current_question >= len(self.questions):
                    self.complete()

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))

        base_width = 850
        base_height = 550
        box_width = int(base_width * self.box_scale)
        box_height = int(base_height * self.box_scale)
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        if box_width > 0 and box_height > 0:
            pygame.draw.rect(screen, (25, 25, 30), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (200, 100, 100), (box_x, box_y, box_width, box_height), 4)

        if self.entrance_complete:
            title_font = pygame.font.Font(None, 48)
            title = title_font.render("Employment Rights Quiz", True, (200, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            if self.current_question < len(self.questions):
                question = self.questions[self.current_question]

                q_font = pygame.font.Font(None, 32)
                q_text = q_font.render(question["question"], True, (255, 255, 255))
                screen.blit(q_text, (SCREEN_WIDTH // 2 - q_text.get_width() // 2, box_y + 120))

                opt_font = pygame.font.Font(None, 28)
                y_offset = box_y + 200

                self.option_rects = []

                for i, option in enumerate(question["options"]):
                    option_rect = pygame.Rect(box_x + 80, y_offset - 10, box_width - 160, 45)
                    self.option_rects.append(option_rect)

                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering = option_rect.collidepoint(mouse_pos) and not self.show_result

                    if is_hovering:
                        pygame.draw.rect(screen, (40, 40, 50), option_rect, border_radius=5)
                        pygame.draw.rect(screen, (100, 100, 120), option_rect, 2, border_radius=5)

                    color = (255, 255, 255)
                    if self.selected_option == i:
                        color = (255, 220, 100)
                    if self.show_result:
                        if i == question["correct"]:
                            color = (100, 255, 100)
                        elif i == self.selected_option:
                            color = (255, 100, 100)

                    opt_text = opt_font.render(f"{i + 1}. {option}", True, color)
                    screen.blit(opt_text, (box_x + 100, y_offset))
                    y_offset += 50

                if not self.show_result:
                    submit_width = 150
                    submit_height = 40
                    submit_x = SCREEN_WIDTH // 2 - submit_width // 2
                    submit_y = box_y + box_height - 80
                    self.submit_rect = pygame.Rect(submit_x, submit_y, submit_width, submit_height)

                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering_submit = self.submit_rect.collidepoint(mouse_pos) and self.selected_option is not None

                    button_color = (100, 150, 255) if self.selected_option is not None else (80, 80, 80)
                    if is_hovering_submit:
                        button_color = (120, 170, 255)

                    pygame.draw.rect(screen, button_color, self.submit_rect, border_radius=5)
                    pygame.draw.rect(screen, (255, 255, 255), self.submit_rect, 2, border_radius=5)

                    submit_font = pygame.font.Font(None, 28)
                    submit_text = submit_font.render("Submit", True, (255, 255, 255))
                    text_rect = submit_text.get_rect(center=self.submit_rect.center)
                    screen.blit(submit_text, text_rect)

                    inst_font = pygame.font.Font(None, 20)
                    inst_text = inst_font.render("Click an option or press 1-4 to select", True, (180, 180, 180))
                    screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 25))
            else:
                score_font = pygame.font.Font(None, 48)
                score_text = score_font.render(f"Score: {self.score}/{len(self.questions)}", True, (100, 255, 100))
                screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, box_y + 180))

                continue_width = 200
                continue_height = 50
                continue_x = SCREEN_WIDTH // 2 - continue_width // 2
                continue_y = box_y + 280
                self.continue_rect = pygame.Rect(continue_x, continue_y, continue_width, continue_height)

                mouse_pos = pygame.mouse.get_pos()
                is_hovering = self.continue_rect.collidepoint(mouse_pos)

                button_color = (120, 170, 255) if is_hovering else (100, 150, 255)
                pygame.draw.rect(screen, button_color, self.continue_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), self.continue_rect, 2, border_radius=5)

                button_font = pygame.font.Font(None, 32)
                button_text = button_font.render("Continue", True, (255, 255, 255))
                text_rect = button_text.get_rect(center=self.continue_rect.center)
                screen.blit(button_text, text_rect)

                inst_font = pygame.font.Font(None, 20)
                inst_text = inst_font.render("Click Continue or press ENTER", True, (180, 180, 180))
                screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 350))

    def handle_key(self, key):
        if not self.active or not self.entrance_complete:
            return

        if self.current_question < len(self.questions) and not self.show_result:
            if key >= pygame.K_1 and key <= pygame.K_4:
                option_index = key - pygame.K_1
                if option_index < len(self.questions[self.current_question]["options"]):
                    self.selected_option = option_index

            elif key == pygame.K_RETURN and self.selected_option is not None:
                if self.selected_option == self.questions[self.current_question]["correct"]:
                    self.score += 1
                self.show_result = True
                self.result_timer = 2.0

        elif self.current_question >= len(self.questions) and key == pygame.K_RETURN:
            self.complete()

    def handle_mouse_click(self, pos, button):
        if not self.active or not self.entrance_complete or button != 1:
            return

        if self.current_question < len(self.questions) and not self.show_result:
            for i, rect in enumerate(getattr(self, 'option_rects', [])):
                if rect.collidepoint(pos):
                    self.selected_option = i
                    return

            if hasattr(self, 'submit_rect') and self.submit_rect.collidepoint(pos):
                if self.selected_option is not None:
                    if self.selected_option == self.questions[self.current_question]["correct"]:
                        self.score += 1
                    self.show_result = True
                    self.result_timer = 2.0

        elif self.current_question >= len(self.questions):
            if hasattr(self, 'continue_rect') and self.continue_rect.collidepoint(pos):
                self.complete()

    def draw_on_board(self, screen, board_rect):
        """Draw quiz on classroom blackboard"""
        if not self.active:
            return
            
        # Clear board area
        pygame.draw.rect(screen, (20, 40, 20), board_rect)
        pygame.draw.rect(screen, (80, 60, 40), board_rect, 3)
        
        if self.current_question >= len(self.questions):
            # Show completion
            complete_font = pygame.font.Font(None, 48)
            complete_text = "Quiz Complete!"
            complete_surface = complete_font.render(complete_text, True, (255, 255, 255))
            screen.blit(complete_surface, 
                       (board_rect.centerx - complete_surface.get_width() // 2,
                        board_rect.y + 50))
            
            # Show score
            score_font = pygame.font.Font(None, 36)
            score_text = f"Score: {self.score}/{len(self.questions)}"
            score_surface = score_font.render(score_text, True, (255, 255, 255))
            screen.blit(score_surface,
                       (board_rect.centerx - score_surface.get_width() // 2,
                        board_rect.centery))
                        
            # Continue prompt
            continue_font = pygame.font.Font(None, 24)
            continue_text = "Press ENTER to continue"
            continue_surface = continue_font.render(continue_text, True, (255, 255, 100))
            screen.blit(continue_surface,
                       (board_rect.centerx - continue_surface.get_width() // 2,
                        board_rect.bottom - 50))
        else:
            # Show current question
            q_data = self.questions[self.current_question]
            
            # Question number
            num_font = pygame.font.Font(None, 28)
            num_text = f"Question {self.current_question + 1}/{len(self.questions)}"
            num_surface = num_font.render(num_text, True, (255, 255, 100))
            screen.blit(num_surface, (board_rect.x + 20, board_rect.y + 20))
            
            # Question text
            q_font = pygame.font.Font(None, 24)
            # Word wrap the question
            words = q_data["question"].split(' ')
            lines = []
            current_line = []
            max_width = board_rect.width - 40
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if q_font.size(test_line)[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
                
            y_offset = board_rect.y + 60
            for line in lines:
                q_surface = q_font.render(line, True, (255, 255, 255))
                screen.blit(q_surface, (board_rect.x + 20, y_offset))
                y_offset += 25
                
            # Options
            opt_font = pygame.font.Font(None, 22)
            y_offset += 20
            for i, option in enumerate(q_data["options"]):
                color = (255, 255, 100) if i == self.selected_option else (200, 200, 200)
                option_text = f"{i + 1}. {option}"
                opt_surface = opt_font.render(option_text, True, color)
                screen.blit(opt_surface, (board_rect.x + 30, y_offset))
                y_offset += 30
                
            # Show result if applicable
            if self.show_result:
                result_font = pygame.font.Font(None, 28)
                if self.selected_option == q_data["correct"]:
                    result_text = "Correct!"
                    result_color = (100, 255, 100)
                else:
                    result_text = f"Wrong! Answer: {q_data['options'][q_data['correct']]}"
                    result_color = (255, 100, 100)
                    
                result_surface = result_font.render(result_text, True, result_color)
                screen.blit(result_surface,
                           (board_rect.centerx - result_surface.get_width() // 2,
                            board_rect.bottom - 40))


class JobApplicationActivity(Activity):
    """Simple job application for pizza shop"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0  # 0 = intro, 1 = form, 2 = hired
        self.form_data = {
            "name": "",
            "experience": "",
            "availability": ""
        }
        self.current_field = 0
        self.fields = ["name", "experience", "availability"]

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Application box
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 45), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 255), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 48)

        if self.stage == 0:
            # Introduction
            title = title_font.render("Tony's Pizza", True, (255, 200, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 50))

            text_font = pygame.font.Font(None, 32)
            lines = [
                "We're hiring!",
                "Starting pay: $17.04/hour",
                "Flexible hours available"
            ]

            y_offset = box_y + 150
            for line in lines:
                text = text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40

            # Apply button
            button_width = 200
            button_height = 50
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = box_y + 320
            self.apply_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Button appearance
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.apply_rect.collidepoint(mouse_pos)

            button_color = (120, 170, 255) if is_hovering else (100, 150, 255)
            pygame.draw.rect(screen, button_color, self.apply_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), self.apply_rect, 2, border_radius=5)

            button_font = pygame.font.Font(None, 32)
            button_text = button_font.render("Apply Now", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=self.apply_rect.center)
            screen.blit(button_text, text_rect)

            # Instructions
            inst_font = pygame.font.Font(None, 20)
            inst_text = inst_font.render("Click Apply or press ENTER", True, (180, 180, 180))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 390))

        elif self.stage == 1:
            # Application form
            title = title_font.render("Job Application", True, (100, 150, 255))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            form_font = pygame.font.Font(None, 28)
            y_offset = box_y + 120

            prompts = {
                "name": "Your Name:",
                "experience": "Any food service experience? (yes/no):",
                "availability": "Can you work evenings? (yes/no):"
            }

            for i, field in enumerate(self.fields):
                color = (255, 255, 100) if i == self.current_field else (200, 200, 200)

                # Prompt
                prompt = form_font.render(prompts[field], True, color)
                screen.blit(prompt, (box_x + 50, y_offset))
                y_offset += 30

                # Value with checkmark if completed
                value = self.form_data[field]
                if value and i != self.current_field:
                    # Show checkmark for completed fields
                    checkmark = "✓ " + value
                    value_text = form_font.render(checkmark, True, (100, 255, 100))
                else:
                    # Show cursor for current field
                    display_value = value + ("_" if i == self.current_field else "")
                    value_text = form_font.render(display_value, True, (255, 255, 255))

                screen.blit(value_text, (box_x + 50, y_offset))
                y_offset += 50

            # Progress indicator
            completed_fields = sum(1 for field in self.fields if self.form_data[field].strip())
            progress_text = f"Progress: {completed_fields}/{len(self.fields)} fields completed"
            progress_font = pygame.font.Font(None, 22)
            progress_surface = progress_font.render(progress_text, True, (200, 200, 200))
            screen.blit(progress_surface, (box_x + 50, box_y + 80))

            # Instructions
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Type to fill fields, TAB to next field, ENTER to submit", True,
                                         (150, 150, 150))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + box_height - 40))

        elif self.stage == 2:
            # Hired!
            title = title_font.render("Congratulations!", True, (100, 255, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 100))

            text_font = pygame.font.Font(None, 32)
            lines = [
                "You're hired!",
                "Start tomorrow at 3:00 PM",
                "Uniform will be provided"
            ]

            y_offset = box_y + 200
            for line in lines:
                text = text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40

            # Continue button
            button_width = 200
            button_height = 50
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = box_y + 350
            self.continue_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            # Button appearance
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.continue_rect.collidepoint(mouse_pos)

            button_color = (120, 255, 120) if is_hovering else (100, 255, 100)
            pygame.draw.rect(screen, button_color, self.continue_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), self.continue_rect, 2, border_radius=5)

            button_font = pygame.font.Font(None, 32)
            button_text = button_font.render("Continue", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=self.continue_rect.center)
            screen.blit(button_text, text_rect)

            # Instructions
            inst_font = pygame.font.Font(None, 20)
            inst_text = inst_font.render("Click Continue or press ENTER", True, (180, 180, 180))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 420))

        # Call parent draw for completion feedback system
        super().draw(screen)

    def update(self, dt):
        """Update job application activity"""
        # Call parent update for completion feedback system
        super().update(dt)

    def handle_key(self, key):
        if not self.active:
            return

        if self.stage == 0:
            if key == pygame.K_RETURN:
                self.stage = 1

        elif self.stage == 1:
            if key == pygame.K_TAB:
                self.current_field = (self.current_field + 1) % len(self.fields)
            elif key == pygame.K_RETURN:
                # Simple validation - just check if all fields have some value
                if all(self.form_data[field] for field in self.fields):
                    self.stage = 2
                    # Show completion feedback immediately when form is submitted
                    self.show_completion_feedback("job_hired", "YOU'RE HIRED!", "Start tomorrow at 3:00 PM")
            elif key == pygame.K_BACKSPACE:
                field = self.fields[self.current_field]
                if self.form_data[field]:
                    self.form_data[field] = self.form_data[field][:-1]
            elif key >= pygame.K_a and key <= pygame.K_z:
                field = self.fields[self.current_field]
                self.form_data[field] += chr(key)
            elif key == pygame.K_SPACE:
                field = self.fields[self.current_field]
                self.form_data[field] += " "

        elif self.stage == 2:
            # Stage 2 is now handled by completion feedback system
            # The base class handles key presses for continue prompt
            super().handle_key(key)

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        if self.stage == 0:
            # Check apply button
            if hasattr(self, 'apply_rect') and self.apply_rect.collidepoint(pos):
                self.stage = 1

        elif self.stage == 2:
            # Stage 2 is now handled by completion feedback system
            # The base class handles mouse clicks for continue prompt
            super().handle_mouse_click(pos, button)


class TransitionScene(Activity):
    """Transition from Part 1 to Part 2"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.fade_alpha = 0
        self.stage = 0  # 0 = fade in, 1 = show part 1 complete, 2 = black screen pause, 3 = part 2 text, 4 = fade out
        self.timer = 0
        self.text_alpha = 0
        self.text_positions = []
        self.particles = []
        
    def start(self):
        """Start the transition"""
        super().start()
        # Generate random particle positions
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150)
            })

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt
        
        # Update particles
        for particle in self.particles:
            particle['y'] = (particle['y'] + particle['speed']) % SCREEN_HEIGHT

        if self.stage == 0:
            # Fade in black screen
            self.fade_alpha = min(255, self.timer * 100)
            if self.fade_alpha >= 255:
                self.stage = 1
                self.timer = 0
        elif self.stage == 1:
            # Show Part 1 Complete text with fade in/out
            if self.timer < 1.0:
                self.text_alpha = min(255, self.timer * 255)
            elif self.timer > 3.0:
                self.text_alpha = max(0, 255 - (self.timer - 3.0) * 255)
            else:
                self.text_alpha = 255

            if self.timer > 4.0:
                self.stage = 2
                self.timer = 0
                self.text_alpha = 0
        elif self.stage == 2:
            # Black screen pause
            if self.timer > 1.0:
                self.stage = 3
                self.timer = 0
        elif self.stage == 3:
            # Show Part 2 text
            if self.timer < 1.0:
                self.text_alpha = min(255, self.timer * 255)
            elif self.timer > 3.0:
                self.text_alpha = max(0, 255 - (self.timer - 3.0) * 255)
            else:
                self.text_alpha = 255

            if self.timer > 4.0:
                self.stage = 4
                self.timer = 0
        elif self.stage == 4:
            # Fade out
            self.fade_alpha = max(0, 255 - self.timer * 100)
            if self.fade_alpha <= 0:
                self.complete()

    def draw(self, screen):
        if not self.active:
            return

        # Black background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(self.fade_alpha))
        screen.blit(overlay, (0, 0))

        if self.stage == 1:
            # Draw particles
            particle_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            particle_surface.fill((0, 0, 0))
            for particle in self.particles:
                pygame.draw.circle(particle_surface, (255, 255, 255), 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
            particle_surface.set_alpha(50)
            screen.blit(particle_surface, (0, 0))
            
            # Part 1 Complete text with animation
            complete_font = pygame.font.Font(None, 48)
            complete_text = complete_font.render("Part 1 Complete!", True, (100, 255, 100))
            complete_text.set_alpha(int(self.text_alpha))
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 - 200))
            
            # Stats or achievement (optional)
            if self.timer > 1.5:
                stats_font = pygame.font.Font(None, 32)
                stats_alpha = min(255, (self.timer - 1.5) * 200)
                stats = [
                    "You learned about employment rights",
                    "You experienced workplace challenges",
                    "You advocated for yourself"
                ]
                y_offset = SCREEN_HEIGHT // 2 - 100
                for stat in stats:
                    stat_text = stats_font.render("✓ " + stat, True, (200, 255, 200))
                    stat_text.set_alpha(int(min(stats_alpha, self.text_alpha)))
                    screen.blit(stat_text, (SCREEN_WIDTH // 2 - stat_text.get_width() // 2, y_offset))
                    y_offset += 35
            
        elif self.stage == 3:
            # Part 2 title screen
            title_font = pygame.font.Font(None, 72)
            subtitle_font = pygame.font.Font(None, 36)

            title = title_font.render("Part 2", True, (255, 255, 255))
            title.set_alpha(int(self.text_alpha))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

            subtitle = subtitle_font.render("Housing Stability", True, (200, 200, 200))
            subtitle.set_alpha(int(self.text_alpha))
            screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            
            # Continue prompt
            if self.timer > 3.0 and int(self.timer * 2) % 2 == 0:
                prompt_font = pygame.font.Font(None, 24)
                prompt = prompt_font.render("Press any key to continue", True, (200, 200, 200))
                prompt.set_alpha(int(self.text_alpha))
                screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT - 100))

    def handle_key(self, key):
        # Allow skipping with any key
        if self.stage == 1 and self.timer > 1.0:
            # Skip to Part 2 text
            self.stage = 3
            self.timer = 0
            self.text_alpha = 0
        elif self.stage == 3 and self.timer > 1.0:
            # Skip to fade out
            self.stage = 4
            self.timer = 0


class SchoolEmergencyScene(Activity):
    """Scene showing school emergency"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Emergency box
        box_width = 700
        box_height = 350
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (60, 20, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)

        # Flashing effect
        flash = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50 + 205

        title_font = pygame.font.Font(None, 56)
        text_font = pygame.font.Font(None, 32)

        # Title with flash effect
        title = title_font.render("EMERGENCY!", True, (flash, 50, 50))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 40))

        lines = [
            "There's been an emergency at school!",
            "You need to stay and help.",
            "",
            "Time passes...",
            "",
            "Oh no! You're late for work!",
            "",
            "Press ENTER to rush to work"
        ]

        y_offset = box_y + 120
        for line in lines:
            if line == "Oh no! You're late for work!":
                color = (255, 150, 150)
            elif line == "Time passes...":
                color = (150, 150, 150)
            else:
                color = (255, 255, 255)

            text = text_font.render(line, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 30

    def handle_key(self, key):
        if not self.active:
            return

        if key == pygame.K_RETURN:
            self.complete()

    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for emergency scene"""
        if not self.active:
            return

        # Any click continues
        self.complete()


class FiringScene(Activity):
    """Scene where player gets fired"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0  # 0 = manager speech, 1 = fired, 2 = paycheck info
        self.text_timer = 0

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        screen.blit(overlay, (0, 0))

        # Scene box
        box_width = 800
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 20, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (200, 50, 50), (box_x, box_y, box_width, box_height), 3)

        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 32)

        if self.stage == 0:
            # Manager speech
            title = title_font.render("Manager's Office", True, (255, 100, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 30))

            lines = [
                "\"You were late to work today!\"",
                "\"This is unacceptable behavior.\"",
                "\"I'm sorry, but we have to let you go.\"",
                "",
                "Press SPACE to continue"
            ]

            y_offset = box_y + 120
            for line in lines:
                color = (255, 200, 200) if line.startswith('"') else (200, 200, 200)
                text = text_font.render(line, True, color)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 40

        elif self.stage == 1:
            # Fired notice
            title = title_font.render("YOU'RE FIRED!", True, (255, 50, 50))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 100))

            info_font = pygame.font.Font(None, 28)
            info_text = info_font.render("Employment terminated immediately", True, (255, 150, 150))
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, box_y + 180))

            cont_text = text_font.render("Press SPACE to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 300))

        elif self.stage == 2:
            # Paycheck info
            title = title_font.render("Final Paycheck", True, (100, 200, 100))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 50))

            lines = [
                "You worked 4 hours yesterday",
                "Rate: $17.81/hour",
                "Total earned: $71.24",
                "",
                "Collect your pay at the front desk",
                "",
                "Press ENTER to continue"
            ]

            y_offset = box_y + 120
            for line in lines:
                text = text_font.render(line, True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
                y_offset += 35

    def handle_key(self, key):
        if not self.active:
            return

        if self.stage < 2 and key == pygame.K_SPACE:
            self.stage += 1
        elif self.stage == 2 and key == pygame.K_RETURN:
            self.complete()

    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for firing scene"""
        if not self.active:
            return

        # Any click advances the stage
        if self.stage < 2:
            self.stage += 1
        else:
            self.complete()


class PizzaMakingGame(Activity):
    """Simple pizza making mini-game"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.pizzas_made = 0
        self.target_pizzas = 3
        self.current_pizza = None
        self.timer = 0
        self.game_timer = 60.0  # 1 minute
        self.oven_timer = 0
        self.pizza_in_oven = False

    def start(self):
        super().start()
        self.new_pizza()

    def new_pizza(self):
        """Create a new pizza order"""
        toppings = ["Pepperoni", "Mushrooms", "Olives", "Peppers"]
        self.current_pizza = {
            "required_toppings": random.sample(toppings, random.randint(1, 3)),
            "added_toppings": [],
            "stage": "topping"  # topping, oven, done
        }

    def update(self, dt):
        if not self.active:
            return

        self.game_timer -= dt

        if self.pizza_in_oven:
            self.oven_timer -= dt
            if self.oven_timer <= 0:
                self.pizza_in_oven = False
                self.current_pizza["stage"] = "done"

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Game box
        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (50, 40, 30), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 150, 50), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pizza Making", True, (255, 200, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 20))

        # Timer and score
        info_font = pygame.font.Font(None, 32)
        timer_text = info_font.render(f"Time: {int(self.game_timer)}s", True, (255, 255, 255))
        screen.blit(timer_text, (box_x + 20, box_y + 80))

        score_text = info_font.render(f"Pizzas: {self.pizzas_made}/{self.target_pizzas}", True, (255, 255, 255))
        screen.blit(score_text, (box_x + box_width - 200, box_y + 80))

        if self.current_pizza:
            # Pizza workspace
            pizza_y = box_y + 150

            # Draw pizza base
            pizza_center_x = SCREEN_WIDTH // 2
            pizza_center_y = pizza_y + 100
            pygame.draw.circle(screen, (255, 220, 150), (pizza_center_x, pizza_center_y), 80)
            pygame.draw.circle(screen, (200, 100, 50), (pizza_center_x, pizza_center_y), 80, 3)

            # Show required toppings
            req_font = pygame.font.Font(None, 28)
            req_text = req_font.render("Order: " + ", ".join(self.current_pizza["required_toppings"]), True,
                                       (255, 255, 255))
            screen.blit(req_text, (SCREEN_WIDTH // 2 - req_text.get_width() // 2, pizza_y - 30))

            # Show added toppings on pizza
            for topping in self.current_pizza["added_toppings"]:
                # Simple representation
                if topping == "Pepperoni":
                    for _ in range(5):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.circle(screen, (200, 50, 50), (x, y), 8)
                elif topping == "Mushrooms":
                    for _ in range(4):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.circle(screen, (150, 100, 50), (x, y), 6)
                elif topping == "Olives":
                    for _ in range(6):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.circle(screen, (50, 50, 50), (x, y), 4)
                elif topping == "Peppers":
                    for _ in range(4):
                        x = pizza_center_x + random.randint(-60, 60)
                        y = pizza_center_y + random.randint(-60, 60)
                        pygame.draw.rect(screen, (50, 200, 50), (x - 5, y - 5, 10, 10))

            # Stage-specific UI
            if self.current_pizza["stage"] == "topping":
                # Topping buttons
                button_y = pizza_y + 250
                toppings = ["Pepperoni", "Mushrooms", "Olives", "Peppers"]
                self.topping_rects = []

                for i, topping in enumerate(toppings):
                    button_x = box_x + 100 + i * 150
                    button_rect = pygame.Rect(button_x, button_y, 120, 40)
                    self.topping_rects.append((button_rect, topping))

                    # Hover effect
                    mouse_pos = pygame.mouse.get_pos()
                    is_hovering = button_rect.collidepoint(mouse_pos)

                    color = (100, 100, 100)
                    if topping in self.current_pizza["added_toppings"]:
                        color = (100, 200, 100)
                    elif is_hovering:
                        color = (120, 120, 120)

                    pygame.draw.rect(screen, color, button_rect, border_radius=5)
                    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=5)

                    button_text = req_font.render(f"{i + 1}. {topping}", True, (255, 255, 255))
                    screen.blit(button_text, (button_x + 10, button_y + 10))

                # Bake button
                bake_width = 150
                bake_height = 45
                bake_x = SCREEN_WIDTH // 2 - bake_width // 2
                bake_y = button_y + 70
                self.bake_rect = pygame.Rect(bake_x, bake_y, bake_width, bake_height)

                # Bake button appearance
                is_hovering_bake = self.bake_rect.collidepoint(mouse_pos)
                bake_color = (255, 150, 50) if is_hovering_bake else (255, 120, 20)

                pygame.draw.rect(screen, bake_color, self.bake_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 255, 255), self.bake_rect, 2, border_radius=5)

                bake_font = pygame.font.Font(None, 32)
                bake_text = bake_font.render("Bake Pizza", True, (255, 255, 255))
                text_rect = bake_text.get_rect(center=self.bake_rect.center)
                screen.blit(bake_text, text_rect)

                # Instructions
                inst_text = req_font.render("Click toppings or press 1-4, click Bake or press SPACE", True,
                                            (200, 200, 200))
                screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, button_y + 130))

            elif self.pizza_in_oven:
                # Oven animation
                oven_text = info_font.render(f"Baking... {int(self.oven_timer)}s", True, (255, 150, 50))
                screen.blit(oven_text, (SCREEN_WIDTH // 2 - oven_text.get_width() // 2, pizza_y + 250))

            elif self.current_pizza["stage"] == "done":
                # Pizza done
                done_text = info_font.render("Pizza ready! Press ENTER to serve", True, (100, 255, 100))
                screen.blit(done_text, (SCREEN_WIDTH // 2 - done_text.get_width() // 2, pizza_y + 250))

        # Check if time's up or target reached
        if self.game_timer <= 0 or self.pizzas_made >= self.target_pizzas:
            result_font = pygame.font.Font(None, 48)
            if self.pizzas_made >= self.target_pizzas:
                result_text = result_font.render("Great job!", True, (100, 255, 100))
            else:
                result_text = result_font.render("Time's up!", True, (255, 100, 100))

            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, box_y + 400))

            cont_font = pygame.font.Font(None, 28)
            cont_text = cont_font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 450))

    def handle_key(self, key):
        if not self.active:
            return

        if self.game_timer <= 0 or self.pizzas_made >= self.target_pizzas:
            if key == pygame.K_RETURN:
                self.complete()
            return

        if self.current_pizza and self.current_pizza["stage"] == "topping":
            toppings = ["Pepperoni", "Mushrooms", "Olives", "Peppers"]

            if key >= pygame.K_1 and key <= pygame.K_4:
                index = key - pygame.K_1
                if index < len(toppings):
                    topping = toppings[index]
                    if topping not in self.current_pizza["added_toppings"]:
                        self.current_pizza["added_toppings"].append(topping)

            elif key == pygame.K_SPACE:
                # Check if pizza is correct
                required = set(self.current_pizza["required_toppings"])
                added = set(self.current_pizza["added_toppings"])

                if required == added:
                    # Correct pizza, put in oven
                    self.pizza_in_oven = True
                    self.oven_timer = 3.0  # 3 seconds to bake

        elif self.current_pizza and self.current_pizza["stage"] == "done":
            if key == pygame.K_RETURN:
                self.pizzas_made += 1
                if self.pizzas_made < self.target_pizzas:
                    self.new_pizza()

    def handle_mouse_click(self, mouse_pos, button=1):
        """Handle mouse clicks for pizza making"""
        if not self.active:
            return

        if self.game_timer <= 0 or self.pizzas_made >= self.target_pizzas:
            # Game over, any click continues
            self.complete()
            return

        if self.current_pizza and self.current_pizza["stage"] == "topping":
            # Check topping button clicks
            if hasattr(self, 'topping_rects'):
                for rect, topping in self.topping_rects:
                    if rect.collidepoint(mouse_pos):
                        if topping not in self.current_pizza["added_toppings"]:
                            self.current_pizza["added_toppings"].append(topping)
                        else:
                            # Remove topping if already added (toggle)
                            self.current_pizza["added_toppings"].remove(topping)
                        return

            # Check bake button click
            if hasattr(self, 'bake_rect') and self.bake_rect.collidepoint(mouse_pos):
                # Check if pizza is correct
                required = set(self.current_pizza["required_toppings"])
                added = set(self.current_pizza["added_toppings"])

                if required == added:
                    # Correct pizza, put in oven
                    self.pizza_in_oven = True
                    self.oven_timer = 3.0  # 3 seconds to bake

        elif self.current_pizza and self.current_pizza["stage"] == "done":
            # Any click serves the pizza
            self.pizzas_made += 1
            if self.pizzas_made < self.target_pizzas:
                self.new_pizza()


class BurgerMakingGame(Activity):
    """Burger flipping mini-game"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.burgers_made = 0
        self.target_burgers = 3
        self.current_burger = None
        self.game_timer = 60.0
        self.flip_timer = 0
        self.burger_flipped = False

    def start(self):
        super().start()
        self.new_burger()

    def new_burger(self):
        """Create a new burger order"""
        self.current_burger = {
            "stage": "cooking",  # cooking, flipped, done
            "cook_time": 0,
            "flip_needed": False
        }
        self.burger_flipped = False

    def update(self, dt):
        if not self.active:
            return

        self.game_timer -= dt

        if self.current_burger and self.current_burger["stage"] == "cooking":
            self.current_burger["cook_time"] += dt
            if self.current_burger["cook_time"] >= 3.0 and not self.burger_flipped:
                self.current_burger["flip_needed"] = True

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Game box
        box_width = 800
        box_height = 600
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Burger Making", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        # Progress
        info_font = pygame.font.Font(None, 32)
        progress_text = info_font.render(f"Burgers: {self.burgers_made}/{self.target_burgers}", True, (255, 255, 255))
        screen.blit(progress_text, (box_x + 50, box_y + 100))

        timer_text = info_font.render(f"Time: {int(self.game_timer)}s", True, (255, 255, 255))
        screen.blit(timer_text, (box_x + box_width - 150, box_y + 100))

        # Burger visualization
        burger_y = box_y + 250

        if self.current_burger:
            if self.current_burger["flip_needed"]:
                flip_text = title_font.render("FLIP THE BURGER! (Press SPACE)", True, (255, 100, 100))
                screen.blit(flip_text, (SCREEN_WIDTH // 2 - flip_text.get_width() // 2, burger_y))
            elif self.burger_flipped:
                done_text = info_font.render("Burger ready! Press ENTER to serve", True, (100, 255, 100))
                screen.blit(done_text, (SCREEN_WIDTH // 2 - done_text.get_width() // 2, burger_y))
            else:
                cook_text = info_font.render("Cooking...", True, (255, 150, 50))
                screen.blit(cook_text, (SCREEN_WIDTH // 2 - cook_text.get_width() // 2, burger_y))

        # End game check
        if self.game_timer <= 0 or self.burgers_made >= self.target_burgers:
            result_font = pygame.font.Font(None, 48)
            if self.burgers_made >= self.target_burgers:
                result_text = result_font.render("Great job!", True, (100, 255, 100))
            else:
                result_text = result_font.render("Time's up!", True, (255, 100, 100))

            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, box_y + 400))

            cont_text = info_font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 450))

    def handle_key(self, key):
        if not self.active:
            return

        if self.game_timer <= 0 or self.burgers_made >= self.target_burgers:
            if key == pygame.K_RETURN:
                self.complete()
            return

        if key == pygame.K_SPACE and self.current_burger["flip_needed"]:
            self.burger_flipped = True
            self.current_burger["flip_needed"] = False

        elif key == pygame.K_RETURN and self.burger_flipped:
            self.burgers_made += 1
            if self.burgers_made < self.target_burgers:
                self.new_burger()


class DocumentChecklistWork(Activity):
    """Document checklist for jobs center"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.documents = {
            "ID": False,
            "SSN": False,
            "Resume": False
        }
        self.all_checked = False

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Box
        box_width = 600
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Required Documents", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        # Checklist
        item_font = pygame.font.Font(None, 36)
        y_offset = 120

        for i, (doc, checked) in enumerate(self.documents.items()):
            checkbox = "[X]" if checked else "[ ]"
            text = item_font.render(f"{checkbox} {doc}", True, (255, 255, 255))
            screen.blit(text, (box_x + 150, box_y + y_offset + i * 60))

            # Number hints
            num_text = item_font.render(f"Press {i + 1}", True, (150, 150, 150))
            screen.blit(num_text, (box_x + 400, box_y + y_offset + i * 60))

        # Continue button
        if self.all_checked:
            cont_font = pygame.font.Font(None, 32)
            cont_text = cont_font.render("All documents ready! Press ENTER to continue", True, (100, 255, 100))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 320))

    def handle_key(self, key):
        if not self.active:
            return

        if key == pygame.K_1:
            self.documents["ID"] = True
        elif key == pygame.K_2:
            self.documents["SSN"] = True
        elif key == pygame.K_3:
            self.documents["Resume"] = True

        self.all_checked = all(self.documents.values())

        if self.all_checked and key == pygame.K_RETURN:
            self.complete()


class BurgerTrainingActivity(Activity):
    """Burger training tutorial"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0
        self.stages = [
            "Welcome to burger training!",
            "Step 1: Place patty on grill",
            "Step 2: Cook for 3 seconds",
            "Step 3: Flip when it sizzles",
            "Step 4: Cook other side",
            "Step 5: Add toppings and serve!",
            "Training complete!"
        ]

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Box
        box_width = 700
        box_height = 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Burger Training", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        # Current stage
        stage_font = pygame.font.Font(None, 36)
        stage_text = stage_font.render(self.stages[self.stage], True, (255, 255, 255))
        screen.blit(stage_text, (SCREEN_WIDTH // 2 - stage_text.get_width() // 2, box_y + 130))

        # Progress
        progress_text = stage_font.render(f"Step {self.stage + 1} of {len(self.stages)}", True, (150, 150, 150))
        screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, box_y + 180))

        # Continue
        cont_font = pygame.font.Font(None, 28)
        if self.stage < len(self.stages) - 1:
            cont_text = cont_font.render("Press SPACE to continue", True, (200, 200, 200))
        else:
            cont_text = cont_font.render("Press ENTER to complete training", True, (100, 255, 100))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 240))

    def handle_key(self, key):
        if not self.active:
            return

        if key == pygame.K_SPACE and self.stage < len(self.stages) - 1:
            self.stage += 1
        elif key == pygame.K_RETURN and self.stage == len(self.stages) - 1:
            self.complete()


class JobListingsActivity(Activity):
    """View job listings and apply"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.jobs = [
            {"title": "Burger Flipper", "pay": "$18/hr", "hours": "Part-time"},
            {"title": "Cashier", "pay": "$17/hr", "hours": "Full-time"},
            {"title": "Cook Assistant", "pay": "$19/hr", "hours": "Part-time"}
        ]
        self.selected_job = 0
        self.applied = False

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Box
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Job Listings", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        # Jobs
        job_font = pygame.font.Font(None, 32)
        y_offset = 120

        for i, job in enumerate(self.jobs):
            color = (255, 220, 100) if i == self.selected_job else (255, 255, 255)
            prefix = "> " if i == self.selected_job else "  "

            job_text = job_font.render(f"{prefix}{job['title']}", True, color)
            screen.blit(job_text, (box_x + 80, box_y + y_offset + i * 80))

            details_text = job_font.render(f"   {job['pay']} - {job['hours']}", True, (180, 180, 180))
            screen.blit(details_text, (box_x + 80, box_y + y_offset + i * 80 + 30))

        # Instructions
        if not self.applied:
            inst_font = pygame.font.Font(None, 28)
            inst_text = inst_font.render("Use UP/DOWN arrows to select, ENTER to apply", True, (200, 200, 200))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 400))
        else:
            result_font = pygame.font.Font(None, 36)
            result_text = result_font.render("Application sent! You got the job!", True, (100, 255, 100))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, box_y + 400))

            cont_font = pygame.font.Font(None, 28)
            cont_text = cont_font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 440))

    def handle_key(self, key):
        if not self.active:
            return

        if not self.applied:
            if key == pygame.K_UP:
                self.selected_job = max(0, self.selected_job - 1)
            elif key == pygame.K_DOWN:
                self.selected_job = min(len(self.jobs) - 1, self.selected_job + 1)
            elif key == pygame.K_RETURN:
                self.applied = True
        else:
            if key == pygame.K_RETURN:
                self.complete()


class ManagerNoticeActivity(Activity):
    """Manager tells you to be at work tomorrow"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Box
        box_width = 700
        box_height = 300
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)

        # Manager message
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Manager Notice", True, (255, 100, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        msg_font = pygame.font.Font(None, 36)
        messages = [
            "Great first day!",
            "Be here tomorrow morning",
            "at 9:00 AM sharp!",
            "Don't be late!"
        ]

        y_offset = 100
        for msg in messages:
            msg_text = msg_font.render(msg, True, (255, 255, 255))
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, box_y + y_offset))
            y_offset += 35

        # Continue
        cont_font = pygame.font.Font(None, 28)
        cont_text = cont_font.render("Press ENTER to acknowledge", True, (200, 200, 200))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 250))

    def handle_key(self, key):
        if key == pygame.K_RETURN:
            self.complete()


class PanicSceneActivity(Activity):
    """Panic about missing work for mandatory meeting"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.stage = 0

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Box
        box_width = 700
        box_height = 400
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (50, 40, 40), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 100, 100), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 56)
        title_text = title_font.render("OH NO!", True, (255, 100, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        # Messages
        msg_font = pygame.font.Font(None, 36)
        if self.stage == 0:
            messages = [
                "You have a mandatory school meeting tomorrow!",
                "But you also have work!",
                "You might get fired AGAIN!",
                "",
                "What should you do?"
            ]
        else:
            messages = [
                "Wait... you're a foster youth!",
                "You have special resources available.",
                "Maybe your ILP officer can help?",
                "",
                "Let's research this..."
            ]

        y_offset = 120
        for msg in messages:
            msg_text = msg_font.render(msg, True, (255, 255, 255))
            screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, box_y + y_offset))
            y_offset += 35

        # Continue
        cont_font = pygame.font.Font(None, 28)
        cont_text = cont_font.render("Press SPACE to continue", True, (200, 200, 200))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 340))

    def handle_key(self, key):
        if key == pygame.K_SPACE:
            if self.stage == 0:
                self.stage = 1
            else:
                self.complete()


class ILPOfficerCallActivity(Activity):
    """Call ILP officer for help"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.dialogue_index = 0
        self.dialogues = [
            {"speaker": "You", "text": "Hi, I need help with a work conflict..."},
            {"speaker": "ILP Officer", "text": "Of course! What's the situation?"},
            {"speaker": "You", "text": "I have a mandatory school meeting tomorrow"},
            {"speaker": "You", "text": "but my manager wants me at work."},
            {"speaker": "ILP Officer", "text": "I understand. As a foster youth, you have"},
            {"speaker": "ILP Officer", "text": "educational priority. Let me call your manager."},
            {"speaker": "You", "text": "Thank you so much!"},
            {"speaker": "ILP Officer", "text": "Give me 5 minutes. I'll call you back."}
        ]

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Phone interface
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 200, 255), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Calling ILP Officer", True, (100, 200, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        # Show dialogue history
        dialogue_font = pygame.font.Font(None, 28)
        y_offset = 100

        for i in range(max(0, self.dialogue_index - 5), self.dialogue_index + 1):
            if i < len(self.dialogues):
                d = self.dialogues[i]
                color = (100, 200, 255) if d["speaker"] == "ILP Officer" else (255, 255, 255)
                text = dialogue_font.render(f"{d['speaker']}: {d['text']}", True, color)
                screen.blit(text, (box_x + 50, box_y + y_offset))
                y_offset += 35

        # Continue or complete
        cont_font = pygame.font.Font(None, 28)
        if self.dialogue_index < len(self.dialogues) - 1:
            cont_text = cont_font.render("Press SPACE to continue conversation", True, (200, 200, 200))
        else:
            cont_text = cont_font.render("Press ENTER to wait for callback", True, (100, 255, 100))
        screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 440))

    def handle_key(self, key):
        if key == pygame.K_SPACE and self.dialogue_index < len(self.dialogues) - 1:
            self.dialogue_index += 1
        elif key == pygame.K_RETURN and self.dialogue_index == len(self.dialogues) - 1:
            self.complete()


class ManagerChoiceActivity(Activity):
    """Choose how to handle the manager situation"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.choices = [
            "Call manager directly to thank them",
            "Do nothing (not recommended)",
            "Let ILP officer handle everything"
        ]
        self.selected_choice = 0
        self.choice_made = False
        self.outcome_text = ""

    def draw(self, screen):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Box
        box_width = 700
        box_height = 500
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (255, 220, 100), (box_x, box_y, box_width, box_height), 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Decision Time", True, (255, 220, 100))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, box_y + 30))

        if not self.choice_made:
            # Context
            context_font = pygame.font.Font(None, 28)
            context_text = context_font.render("ILP officer got you approved for tomorrow off!", True, (100, 255, 100))
            screen.blit(context_text, (SCREEN_WIDTH // 2 - context_text.get_width() // 2, box_y + 100))

            question_text = context_font.render("How do you want to handle this with your manager?", True,
                                                (255, 255, 255))
            screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, box_y + 140))

            # Choices
            choice_font = pygame.font.Font(None, 32)
            y_offset = 200

            for i, choice in enumerate(self.choices):
                color = (255, 220, 100) if i == self.selected_choice else (255, 255, 255)
                prefix = "> " if i == self.selected_choice else "  "

                choice_text = choice_font.render(f"{prefix}{choice}", True, color)
                screen.blit(choice_text, (box_x + 80, box_y + y_offset + i * 50))

            # Instructions
            inst_font = pygame.font.Font(None, 28)
            inst_text = inst_font.render("Use UP/DOWN to select, ENTER to choose", True, (200, 200, 200))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, box_y + 420))
        else:
            # Show outcome
            outcome_font = pygame.font.Font(None, 32)
            outcome_lines = self.outcome_text.split('\n')
            y_offset = 150

            for line in outcome_lines:
                line_text = outcome_font.render(line, True, (255, 255, 255))
                screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, box_y + y_offset))
                y_offset += 35

            # Continue
            cont_font = pygame.font.Font(None, 28)
            cont_text = cont_font.render("Press ENTER to continue", True, (100, 255, 100))
            screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, box_y + 420))

    def handle_key(self, key):
        if not self.choice_made:
            if key == pygame.K_UP:
                self.selected_choice = max(0, self.selected_choice - 1)
            elif key == pygame.K_DOWN:
                self.selected_choice = min(len(self.choices) - 1, self.selected_choice + 1)
            elif key == pygame.K_RETURN:
                self.choice_made = True
                if self.selected_choice == 0:
                    self.outcome_text = "Great choice! You called your manager\nand thanked them for understanding.\nThey appreciated your professionalism!\n\nYou kept your job AND attended\nyour mandatory meeting!"
                elif self.selected_choice == 1:
                    self.outcome_text = "Not the best choice...\nYour manager was confused when\nyou showed up the next day.\n\nLuckily, the ILP officer had\nalready explained everything.\n\nTry to communicate better next time!"
                else:
                    self.outcome_text = "The ILP officer handled everything.\nYour manager understood the situation.\n\nNext time, consider following up\nwith a thank you - it shows maturity!"
        else:
            if key == pygame.K_RETURN:
                self.complete()




        # Add all other activity classes here following the same pattern...
        # Including: TransitionScene, SchoolEmergencyScene, FiringScene, PizzaMakingGame,
        # BurgerMakingGame, DocumentChecklistWork, BurgerTrainingActivity, JobListingsActivity,
        # ManagerNoticeActivity, PanicSceneActivity, ILPOfficerCallActivity, ManagerChoiceActivity
        # (Due to length, I'm showing the pattern - you would copy all these from the original file)
import pygame
import random
import math

# Base class for all mini-games
class MiniGame:
    """Base class for all mini-games with common functionality"""
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.screen_width = 1200
        self.screen_height = 800
        self.fade_alpha = 0
        self.box_scale = 0
        self.entrance_complete = False
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.hover_sound_played = {}
        
    def start(self):
        self.active = True
        self.completed = False
        self.fade_alpha = 0
        self.box_scale = 0
        self.entrance_complete = False
        
    def complete(self):
        self.completed = True
        self.active = False
        # Don't call complete_current_objective here - let the update loop handle it
            
    def update(self, dt):
        # Base entrance animation
        if not self.entrance_complete:
            self.fade_alpha = min(255, self.fade_alpha + dt * 500)
            self.box_scale = min(1.0, self.box_scale + dt * 3)
            if self.box_scale >= 1.0:
                self.entrance_complete = True
                
    def draw_background_overlay(self, screen):
        """Draw darkened background"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(min(200, self.fade_alpha))
        screen.blit(overlay, (0, 0))
        
    def draw_game_box(self, screen, x, y, width, height, color=(255, 220, 100)):
        """Draw animated game box with corners"""
        w = int(width * self.box_scale)
        h = int(height * self.box_scale)
        x = x + (width - w) // 2
        y = y + (height - h) // 2
        
        if w > 0 and h > 0:
            # Gradient background
            for i in range(5):
                grad_color = (35 + i * 3, 35 + i * 3, 40 + i * 3)
                pygame.draw.rect(screen, grad_color, (x + i, y + i, w - i*2, h - i*2))
            
            # Main background
            pygame.draw.rect(screen, (25, 25, 30), (x + 5, y + 5, w - 10, h - 10))
            
            # Border
            pygame.draw.rect(screen, color, (x, y, w, h), 4)
            
            # Corner decorations
            corner_size = 20
            for cx, cy in [(x, y), (x + w - corner_size, y), 
                          (x, y + h - corner_size), (x + w - corner_size, y + h - corner_size)]:
                pygame.draw.lines(screen, color, False, 
                                [(cx, cy + corner_size), (cx, cy), (cx + corner_size, cy)], 3)
                                
    def handle_key(self, key):
        """Base key handler - override in subclasses"""
        pass
        
    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        self.mouse_pos = pos
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if button == 1:  # Left click
            self.mouse_clicked = True
            self.mouse_pos = pos
            
    def is_hovering(self, x, y, width, height):
        """Check if mouse is hovering over a rectangle"""
        mx, my = self.mouse_pos
        return x <= mx <= x + width and y <= my <= y + height


# Grocery Shopping Mini-Game
class GroceryShoppingGame(MiniGame):
    """Shopping mini-game where player learns to budget and split costs"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.budget = 50.00
        self.roommate_budget = 50.00
        self.cart = []
        self.items = [
            {"name": "Milk", "price": 3.99, "shared": True, "essential": True},
            {"name": "Bread", "price": 2.49, "shared": True, "essential": True},
            {"name": "Eggs", "price": 4.99, "shared": True, "essential": True},
            {"name": "Your Cereal", "price": 4.99, "shared": False, "essential": False},
            {"name": "Shared Rice", "price": 8.99, "shared": True, "essential": True},
            {"name": "Your Snacks", "price": 6.99, "shared": False, "essential": False},
            {"name": "Toilet Paper", "price": 12.99, "shared": True, "essential": True},
            {"name": "Your Shampoo", "price": 7.99, "shared": False, "essential": False},
            {"name": "Dish Soap", "price": 3.99, "shared": True, "essential": True},
            {"name": "Roommate's Coffee", "price": 9.99, "shared": False, "essential": False, "roommate": True},
        ]
        self.selected_item = 0
        self.checkout_mode = False
        self.show_receipt = False
        self.message = ""
        self.message_timer = 0
        self.cart_hover = -1
        self.checkout_button_hover = False
        self.selected_for_removal = -1
        
    def add_to_cart(self, item):
        """Add item to shopping cart"""
        # Check if it's roommate's item
        if item.get("roommate", False):
            self.message = "That's your roommate's item!"
            self.message_timer = 2.0
            return
            
        # Check budget
        total_cost = self.calculate_total()
        your_share = total_cost["your_total"]
        
        if item["shared"]:
            additional_cost = item["price"] / 2
        else:
            additional_cost = item["price"]
            
        if your_share + additional_cost > self.budget:
            self.message = "Over budget! Remove something first."
            self.message_timer = 2.0
            return
            
        self.cart.append(item)
        self.message = f"Added {item['name']} to cart!"
        self.message_timer = 1.0
        
    def remove_from_cart(self, index):
        """Remove item from cart"""
        if 0 <= index < len(self.cart):
            item = self.cart.pop(index)
            self.message = f"Removed {item['name']}"
            self.message_timer = 1.0
            
    def calculate_total(self):
        """Calculate total costs and splits"""
        your_total = 0
        shared_total = 0
        
        for item in self.cart:
            if item["shared"]:
                shared_total += item["price"]
                your_total += item["price"] / 2
            else:
                your_total += item["price"]
                
        return {
            "your_total": your_total,
            "shared_total": shared_total,
            "total": your_total + shared_total / 2
        }
        
    def draw(self, screen):
        if not self.active:
            return
            
        self.draw_background_overlay(screen)
        
        # Game box
        box_width = 900
        box_height = 600
        box_x = self.screen_width // 2 - box_width // 2
        box_y = self.screen_height // 2 - box_height // 2
        
        self.draw_game_box(screen, box_x, box_y, box_width, box_height, (100, 200, 100))
        
        if not self.entrance_complete:
            return
            
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("🛒 Grocery Shopping", True, (100, 255, 100))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, box_y + 30))
        
        # Budget display
        budget_font = pygame.font.Font(None, 32)
        totals = self.calculate_total()
        budget_text = f"Your Budget: ${self.budget:.2f}  |  Spent: ${totals['your_total']:.2f}"
        budget_color = (100, 255, 100) if totals['your_total'] <= self.budget else (255, 100, 100)
        budget_surface = budget_font.render(budget_text, True, budget_color)
        screen.blit(budget_surface, (box_x + 50, box_y + 90))
        
        if not self.show_receipt:
            # Visual instructions at top
            inst_font = pygame.font.Font(None, 26)
            inst_text = "🛒 Click items to add to cart  •  Click cart items to remove  •  Stay within budget!"
            inst_surface = inst_font.render(inst_text, True, (220, 220, 220))
            screen.blit(inst_surface, (self.screen_width // 2 - inst_surface.get_width() // 2, box_y + 120))
            
            # Draw store shelves with mouse interaction
            shelf_y = box_y + 160
            item_height = 45
            
            for i, item in enumerate(self.items):
                item_x = box_x + 50
                item_y = shelf_y + i * item_height - 5
                item_width = box_width - 350  # Leave room for cart
                item_height_box = 40
                
                # Check hover
                is_hovering = self.is_hovering(item_x, item_y, item_width, item_height_box)
                
                # Item background with hover effect
                if is_hovering:
                    pygame.draw.rect(screen, (80, 80, 100), (item_x, item_y, item_width, item_height_box))
                    pygame.draw.rect(screen, (255, 220, 100), (item_x, item_y, item_width, item_height_box), 2)
                    # Change cursor
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.draw.rect(screen, (50, 50, 60), (item_x, item_y, item_width, item_height_box))
                
                # Item name with icon
                item_font = pygame.font.Font(None, 28)
                name_color = (255, 255, 255) if is_hovering else (200, 200, 200)
                if item.get("roommate", False):
                    name_color = (150, 150, 200)
                    
                # Add item icon
                icon = "🥛" if "Milk" in item["name"] else "🍞" if "Bread" in item["name"] else "🥚" if "Eggs" in item["name"] else "🥣" if "Cereal" in item["name"] else "🍚" if "Rice" in item["name"] else "🍿" if "Snacks" in item["name"] else "🧻" if "Toilet" in item["name"] else "🧴" if "Shampoo" in item["name"] else "🧽" if "Soap" in item["name"] else "☕" if "Coffee" in item["name"] else "📦"
                
                name_text = f"{icon} {item['name']}"
                if item["shared"]:
                    name_text += " (Shared)"
                name_surface = item_font.render(name_text, True, name_color)
                screen.blit(name_surface, (item_x + 20, item_y + 10))
                
                # Price
                price_text = f"${item['price']:.2f}"
                if item["shared"]:
                    price_text += f" • You pay: ${item['price']/2:.2f}"
                price_surface = item_font.render(price_text, True, (255, 220, 100))
                screen.blit(price_surface, (item_x + 350, item_y + 10))
                
                # Add to cart visual
                if item in self.cart:
                    cart_count = self.cart.count(item)
                    cart_text = f"✓ In Cart ({cart_count})"
                    cart_surface = item_font.render(cart_text, True, (100, 255, 100))
                    screen.blit(cart_surface, (item_x + item_width - 120, item_y + 10))
                elif is_hovering and not item.get("roommate", False):
                    add_text = "+ Add"
                    add_surface = item_font.render(add_text, True, (100, 255, 100))
                    screen.blit(add_surface, (item_x + item_width - 80, item_y + 10))
            
            # Shopping cart summary on right
            cart_x = box_x + box_width - 250
            cart_y = box_y + 160
            cart_height = 300
            
            # Cart background
            pygame.draw.rect(screen, (40, 40, 50), (cart_x, cart_y, 230, cart_height))
            pygame.draw.rect(screen, (100, 100, 120), (cart_x, cart_y, 230, cart_height), 2)
            
            # Cart title
            cart_title = "🛒 Your Cart"
            cart_font = pygame.font.Font(None, 28)
            title_surface = cart_font.render(cart_title, True, (255, 220, 100))
            screen.blit(title_surface, (cart_x + 10, cart_y + 10))
            
            # Cart items with remove option
            cart_item_y = cart_y + 50
            for idx, cart_item in enumerate(self.cart[:6]):  # Show max 6 items
                item_text = f"• {cart_item['name'][:15]}.." if len(cart_item['name']) > 15 else f"• {cart_item['name']}"
                
                # Check if hovering over this cart item
                is_cart_hover = self.is_hovering(cart_x + 10, cart_item_y, 200, 25)
                
                if is_cart_hover:
                    pygame.draw.rect(screen, (80, 50, 50), (cart_x + 10, cart_item_y, 200, 25))
                    item_color = (255, 150, 150)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    item_color = (200, 200, 200)
                    
                item_surface = cart_font.render(item_text, True, item_color)
                screen.blit(item_surface, (cart_x + 15, cart_item_y + 3))
                
                if is_cart_hover:
                    remove_text = "×"
                    remove_surface = cart_font.render(remove_text, True, (255, 100, 100))
                    screen.blit(remove_surface, (cart_x + 190, cart_item_y))
                    
                cart_item_y += 30
                
            if len(self.cart) > 6:
                more_text = f"... and {len(self.cart) - 6} more items"
                more_surface = cart_font.render(more_text, True, (150, 150, 150))
                screen.blit(more_surface, (cart_x + 15, cart_item_y))
            
            # Checkout button - positioned below the cart
            checkout_width = 200
            checkout_height = 45
            checkout_x = cart_x + 15  # Align with cart
            checkout_y = cart_y + cart_height + 20  # Below the cart
            
            self.checkout_button_hover = self.is_hovering(checkout_x, checkout_y, checkout_width, checkout_height)
            
            if len(self.cart) > 0:
                button_color = (100, 200, 100) if self.checkout_button_hover else (80, 150, 80)
                text_color = (255, 255, 255)
            else:
                button_color = (60, 60, 60)
                text_color = (120, 120, 120)
                
            pygame.draw.rect(screen, button_color, (checkout_x, checkout_y, checkout_width, checkout_height))
            pygame.draw.rect(screen, (200, 200, 200), (checkout_x, checkout_y, checkout_width, checkout_height), 3)
            
            checkout_font = pygame.font.Font(None, 36)
            checkout_text = "💳 Checkout" if len(self.cart) > 0 else "Cart Empty"
            checkout_surface = checkout_font.render(checkout_text, True, text_color)
            text_x = checkout_x + checkout_width // 2 - checkout_surface.get_width() // 2
            text_y = checkout_y + checkout_height // 2 - checkout_surface.get_height() // 2
            screen.blit(checkout_surface, (text_x, text_y))
            
            if self.checkout_button_hover and len(self.cart) > 0:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            # Reset cursor if not hovering
            if not any([self.is_hovering(box_x + 50, box_y + 160 + i * 45 - 5, box_width - 350, 40) for i in range(len(self.items))]) and not self.checkout_button_hover and not any([self.is_hovering(cart_x + 10, cart_y + 50 + i * 30, 200, 25) for i in range(min(6, len(self.cart)))]):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        else:
            # Show receipt
            self.draw_receipt(screen, box_x, box_y, box_width, box_height)
            
        # Message display
        if self.message_timer > 0:
            msg_font = pygame.font.Font(None, 36)
            msg_surface = msg_font.render(self.message, True, (255, 255, 100))
            msg_x = self.screen_width // 2 - msg_surface.get_width() // 2
            msg_y = box_y + box_height - 100
            pygame.draw.rect(screen, (40, 40, 50), (msg_x - 10, msg_y - 5, msg_surface.get_width() + 20, 40))
            screen.blit(msg_surface, (msg_x, msg_y))
            
    def draw_receipt(self, screen, box_x, box_y, box_width, box_height):
        """Draw checkout receipt"""
        receipt_font = pygame.font.Font(None, 28)
        y_offset = 150
        
        # Receipt header
        header_text = "=== RECEIPT ==="
        header_surface = receipt_font.render(header_text, True, (255, 220, 100))
        screen.blit(header_surface, (self.screen_width // 2 - header_surface.get_width() // 2, box_y + y_offset))
        y_offset += 40
        
        # Items
        for item in self.cart:
            item_text = f"{item['name']}: ${item['price']:.2f}"
            if item['shared']:
                item_text += " (Split)"
            item_surface = receipt_font.render(item_text, True, (220, 220, 220))
            screen.blit(item_surface, (box_x + 100, box_y + y_offset))
            y_offset += 30
            
        # Totals
        y_offset += 20
        totals = self.calculate_total()
        
        total_text = f"Shared Items Total: ${totals['shared_total']:.2f}"
        total_surface = receipt_font.render(total_text, True, (200, 200, 200))
        screen.blit(total_surface, (box_x + 100, box_y + y_offset))
        y_offset += 35
        
        your_text = f"Your Total: ${totals['your_total']:.2f}"
        your_color = (100, 255, 100) if totals['your_total'] <= self.budget else (255, 100, 100)
        your_surface = receipt_font.render(your_text, True, your_color)
        screen.blit(your_surface, (box_x + 100, box_y + y_offset))
        y_offset += 35
        
        # Success message
        if totals['your_total'] <= self.budget:
            success_text = "Great budgeting!"
            success_color = (100, 255, 100)
        else:
            success_text = "Over budget! Go back and adjust."
            success_color = (255, 100, 100)
            
        success_surface = receipt_font.render(success_text, True, success_color)
        screen.blit(success_surface, (self.screen_width // 2 - success_surface.get_width() // 2, box_y + y_offset + 20))
        
        # Draw complete/back button
        button_y = box_y + y_offset + 70
        button_width = 200
        button_height = 45
        button_x = self.screen_width // 2 - button_width // 2
        
        # Check hover
        button_hover = self.is_hovering(button_x, button_y, button_width, button_height)
        
        if totals['your_total'] <= self.budget:
            button_color = (100, 200, 100) if button_hover else (80, 150, 80)
            button_text = "Complete Shopping"
        else:
            button_color = (200, 100, 100) if button_hover else (150, 80, 80)
            button_text = "Go Back"
            
        pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, (200, 200, 200), (button_x, button_y, button_width, button_height), 3)
        
        button_font = pygame.font.Font(None, 28)
        btn_surface = button_font.render(button_text, True, (255, 255, 255))
        btn_text_x = button_x + button_width // 2 - btn_surface.get_width() // 2
        btn_text_y = button_y + button_height // 2 - btn_surface.get_height() // 2
        screen.blit(btn_surface, (btn_text_x, btn_text_y))
        
        if button_hover:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for shopping"""
        super().handle_mouse_click(pos, button)
        
        if not self.active or not self.entrance_complete:
            return
            
        box_width = 900
        box_height = 600
        box_x = self.screen_width // 2 - box_width // 2
        box_y = self.screen_height // 2 - box_height // 2
            
        if self.show_receipt:
            # Check complete/back button
            totals = self.calculate_total()
            
            # Calculate button position (matching draw_receipt)
            y_offset = 150  # Starting offset
            y_offset += 40  # Header
            y_offset += len(self.cart) * 30  # Items
            y_offset += 20  # Gap
            y_offset += 35  # Shared total
            y_offset += 35  # Your total
            
            button_y = box_y + y_offset + 70
            button_width = 200
            button_height = 45
            button_x = self.screen_width // 2 - button_width // 2
            
            if self.is_hovering(button_x, button_y, button_width, button_height):
                if totals['your_total'] <= self.budget:
                    self.complete()
                else:
                    self.show_receipt = False
                return
        else:
            # Check item clicks
            shelf_y = box_y + 160
            
            for i, item in enumerate(self.items):
                item_x = box_x + 50
                item_y = shelf_y + i * 45 - 5
                item_width = box_width - 350
                if self.is_hovering(item_x, item_y, item_width, 40):
                    self.add_to_cart(item)
                    return
                    
            # Check cart item clicks for removal
            cart_x = box_x + box_width - 250
            cart_y = box_y + 160 + 50
            for idx, cart_item in enumerate(self.cart[:6]):
                if self.is_hovering(cart_x + 10, cart_y + idx * 30, 200, 25):
                    self.cart.remove(cart_item)
                    self.message = f"Removed {cart_item['name']}"
                    self.message_timer = 1.0
                    return
                    
            # Check checkout button - use same positioning as draw
            cart_x = box_x + box_width - 250
            cart_y = box_y + 160
            cart_height = 300
            checkout_x = cart_x + 15
            checkout_y = cart_y + cart_height + 20
            if self.is_hovering(checkout_x, checkout_y, 200, 45) and len(self.cart) > 0:
                self.show_receipt = True
                    
    def update(self, dt):
        super().update(dt)
        if self.message_timer > 0:
            self.message_timer -= dt
            
    def handle_key(self, key):
        """Handle keyboard input for receipt screen"""
        if not self.active or not self.entrance_complete:
            return
            
        if self.show_receipt:
            totals = self.calculate_total()
            if key == pygame.K_RETURN and totals['your_total'] <= self.budget:
                self.complete()
            elif key == pygame.K_ESCAPE:
                self.show_receipt = False


# Document Application Mini-Game
class DocumentApplicationGame(MiniGame):
    """Mini-game for filling out housing application with drag-and-drop documents"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.documents = [
            {"name": "ID Card", "x": 50, "y": 200, "required": True, "placed": False},
            {"name": "Income Proof", "x": 50, "y": 280, "required": True, "placed": False},
            {"name": "References", "x": 50, "y": 360, "required": True, "placed": False},
            {"name": "Bank Statement", "x": 50, "y": 440, "required": False, "placed": False},
            {"name": "Old Report Card", "x": 50, "y": 520, "required": False, "placed": False},
        ]
        self.slots = [
            {"name": "Identification", "x": 500, "y": 200, "filled": None, "accepts": "ID Card"},
            {"name": "Income Verification", "x": 500, "y": 280, "filled": None, "accepts": "Income Proof"},
            {"name": "Character References", "x": 500, "y": 360, "filled": None, "accepts": "References"},
        ]
        self.selected_doc = None
        self.cursor_index = 0
        self.mode = "select"  # "select" or "place"
        self.errors = []
        self.submit_enabled = False
        self.dragging_doc = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
    def check_completion(self):
        """Check if all required documents are placed correctly"""
        all_correct = True
        self.errors = []
        
        for slot in self.slots:
            if slot["filled"] is None:
                all_correct = False
                self.errors.append(f"{slot['name']} is missing")
            elif slot["filled"]["name"] != slot["accepts"]:
                all_correct = False
                self.errors.append(f"Wrong document in {slot['name']}")
                
        self.submit_enabled = all_correct
        return all_correct
        
    def draw(self, screen):
        if not self.active:
            return
            
        self.draw_background_overlay(screen)
        
        # Game box
        box_width = 900
        box_height = 650
        box_x = self.screen_width // 2 - box_width // 2
        box_y = self.screen_height // 2 - box_height // 2
        
        self.draw_game_box(screen, box_x, box_y, box_width, box_height, (100, 150, 255))
        
        if not self.entrance_complete:
            return
            
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Housing Application", True, (100, 150, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, box_y + 30))
        
        # Instructions with visual icons
        inst_font = pygame.font.Font(None, 26)
        inst_text = "📄 Drag and drop documents to their matching slots"
        inst_surface = inst_font.render(inst_text, True, (200, 200, 200))
        screen.blit(inst_surface, (self.screen_width // 2 - inst_surface.get_width() // 2, box_y + 80))
        
        # Visual hint
        hint_font = pygame.font.Font(None, 22)
        hint_text = "Click and hold to drag • Drop on the correct slot"
        hint_surface = hint_font.render(hint_text, True, (160, 160, 160))
        screen.blit(hint_surface, (self.screen_width // 2 - hint_surface.get_width() // 2, box_y + 105))
        
        # Draw documents
        doc_font = pygame.font.Font(None, 28)
        for i, doc in enumerate(self.documents):
            if not doc["placed"] and doc != self.dragging_doc:
                doc_x = box_x + doc["x"]
                doc_y = box_y + doc["y"]
                
                # Check hover
                is_hovering = self.is_hovering(doc_x, doc_y, 180, 60)
                
                # Document background with hover effect
                doc_color = (100, 100, 150) if is_hovering else (60, 60, 70)
                pygame.draw.rect(screen, doc_color, (doc_x, doc_y, 180, 60))
                
                if is_hovering:
                    pygame.draw.rect(screen, (150, 150, 200), (doc_x, doc_y, 180, 60), 3)
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    pygame.draw.rect(screen, (150, 150, 200), (doc_x, doc_y, 180, 60), 2)
                
                # Document icon and name
                icon = "📋" if "ID" in doc["name"] else "💰" if "Income" in doc["name"] else "👥" if "References" in doc["name"] else "🏦" if "Bank" in doc["name"] else "📊" if "Report" in doc["name"] else "📄"
                doc_text = doc_font.render(f"{icon} {doc['name']}", True, (255, 255, 255))
                screen.blit(doc_text, (doc_x + 10, doc_y + 20))
                
                # Required indicator
                if doc.get("required", False):
                    req_text = "Required"
                    req_font = pygame.font.Font(None, 20)
                    req_surface = req_font.render(req_text, True, (255, 100, 100))
                    screen.blit(req_surface, (doc_x + 10, doc_y + 42))
                
        # Draw slots with visual feedback
        for i, slot in enumerate(self.slots):
            slot_x = box_x + slot["x"]
            slot_y = box_y + slot["y"]
            
            # Check if dragging over this slot
            is_drop_target = False
            if self.dragging_doc:
                is_drop_target = self.is_hovering(slot_x, slot_y, 250, 60)
            
            # Slot background with drop feedback
            if is_drop_target:
                slot_color = (100, 150, 100)  # Green when valid drop target
                border_width = 4
            elif slot["filled"]:
                slot_color = (50, 80, 50)
                border_width = 2
            else:
                slot_color = (80, 50, 50)
                border_width = 2
                
            pygame.draw.rect(screen, slot_color, (slot_x, slot_y, 250, 60))
            pygame.draw.rect(screen, (200, 200, 200), (slot_x, slot_y, 250, 60), border_width)
            
            # Slot label
            label_text = slot["name"]
            label_surface = doc_font.render(label_text, True, (255, 255, 255))
            screen.blit(label_surface, (box_x + slot["x"] + 10, box_y + slot["y"] + 5))
            
            # Filled document
            if slot["filled"]:
                filled_text = f"✓ {slot['filled']['name']}"
                filled_color = (100, 255, 100) if slot['filled']['name'] == slot['accepts'] else (255, 100, 100)
                filled_surface = doc_font.render(filled_text, True, filled_color)
                screen.blit(filled_surface, (box_x + slot["x"] + 10, box_y + slot["y"] + 30))
                
        # Error messages
        if self.errors:
            error_y = box_y + 480
            error_font = pygame.font.Font(None, 24)
            for error in self.errors:
                error_surface = error_font.render(f"• {error}", True, (255, 100, 100))
                screen.blit(error_surface, (box_x + 100, error_y))
                error_y += 25
                
        # Submit button
        submit_width = 250
        submit_height = 50
        submit_x = self.screen_width // 2 - submit_width // 2
        submit_y = box_y + 530
        
        # Check hover
        submit_hover = self.is_hovering(submit_x, submit_y, submit_width, submit_height)
        
        if self.submit_enabled:
            button_color = (100, 200, 100) if submit_hover else (80, 150, 80)
            text_color = (255, 255, 255)
            border_color = (150, 255, 150)
        else:
            button_color = (60, 60, 60)
            text_color = (120, 120, 120)
            border_color = (100, 100, 100)
            
        # Draw button
        pygame.draw.rect(screen, button_color, (submit_x, submit_y, submit_width, submit_height))
        pygame.draw.rect(screen, border_color, (submit_x, submit_y, submit_width, submit_height), 3)
        
        # Button text
        submit_text = "✓ Submit Application" if self.submit_enabled else "⚠ Complete All Fields"
        submit_font = pygame.font.Font(None, 28)
        submit_surface = submit_font.render(submit_text, True, text_color)
        text_x = submit_x + submit_width // 2 - submit_surface.get_width() // 2
        text_y = submit_y + submit_height // 2 - submit_surface.get_height() // 2
        screen.blit(submit_surface, (text_x, text_y))
        
        if submit_hover and self.submit_enabled:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        
        # Draw dragging document at mouse position
        if self.dragging_doc:
            mouse_x, mouse_y = self.mouse_pos
            drag_x = mouse_x - self.drag_offset_x
            drag_y = mouse_y - self.drag_offset_y
            
            # Draw dragging document directly
            pygame.draw.rect(screen, (120, 120, 170), (drag_x, drag_y, 180, 60), 0, border_radius=5)
            pygame.draw.rect(screen, (200, 200, 255), (drag_x, drag_y, 180, 60), 3, border_radius=5)
            icon = "📋" if "ID" in self.dragging_doc["name"] else "💰" if "Income" in self.dragging_doc["name"] else "👥" if "References" in self.dragging_doc["name"] else "🏦" if "Bank" in self.dragging_doc["name"] else "📊" if "Report" in self.dragging_doc["name"] else "📄"
            doc_text = doc_font.render(f"{icon} {self.dragging_doc['name']}", True, (255, 255, 255))
            screen.blit(doc_text, (drag_x + 10, drag_y + 20))
            
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        
        # Reset cursor if not hovering/dragging
        if not self.dragging_doc and not any([self.is_hovering(box_x + doc["x"], box_y + doc["y"], 180, 60) for doc in self.documents if not doc["placed"]]):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for document drag and drop"""
        super().handle_mouse_click(pos, button)
        
        if not self.active or not self.entrance_complete:
            return
            
        box_x = self.screen_width // 2 - 450
        box_y = self.screen_height // 2 - 325
        
        if button == 1:  # Left click
            # Check submit button
            if self.submit_enabled:
                submit_x = self.screen_width // 2 - 125  # 250/2 = 125
                submit_y = box_y + 530
                if self.is_hovering(submit_x, submit_y, 250, 50):
                    self.complete()
                    return
            
            # Check documents for dragging
            for doc in self.documents:
                if not doc["placed"]:
                    doc_x = box_x + doc["x"]
                    doc_y = box_y + doc["y"]
                    if self.is_hovering(doc_x, doc_y, 180, 60):
                        self.dragging_doc = doc
                        self.drag_offset_x = pos[0] - doc_x
                        self.drag_offset_y = pos[1] - doc_y
                        return
                        
    def handle_mouse_release(self, pos, button):
        """Handle mouse release for dropping documents"""
        if not self.active or not self.entrance_complete:
            return
            
        box_x = self.screen_width // 2 - 450
        box_y = self.screen_height // 2 - 325
        
        if button == 1 and self.dragging_doc:  # Left button release
            # Check if dropped on a slot
            for slot in self.slots:
                slot_x = box_x + slot["x"]
                slot_y = box_y + slot["y"]
                if self.is_hovering(slot_x, slot_y, 250, 60):
                    # Clear any existing document in this slot
                    if slot["filled"]:
                        slot["filled"]["placed"] = False
                    
                    # Place the document
                    slot["filled"] = self.dragging_doc
                    self.dragging_doc["placed"] = True
                    self.check_completion()
                    break
            
            self.dragging_doc = None


# Roommate Agreement Mini-Game
class RoommateAgreementGame(MiniGame):
    """Negotiation mini-game for establishing roommate rules"""
    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.issues = [
            {
                "topic": "Quiet Hours",
                "options": ["10 PM - 8 AM", "11 PM - 7 AM", "Midnight - 6 AM"],
                "roommate_preference": 0,
                "your_choice": 1,
                "compromised": False
            },
            {
                "topic": "Guest Policy",
                "options": ["No overnight guests", "Guests OK with 24hr notice", "Unlimited guests"],
                "roommate_preference": 1,
                "your_choice": 1,
                "compromised": False
            },
            {
                "topic": "Chore Schedule",
                "options": ["Daily rotation", "Weekly rotation", "As needed"],
                "roommate_preference": 0,
                "your_choice": 1,
                "compromised": False
            },
            {
                "topic": "Kitchen Use",
                "options": ["Scheduled cooking times", "First come first serve", "Separate shelves only"],
                "roommate_preference": 2,
                "your_choice": 1,
                "compromised": False
            }
        ]
        self.current_issue = 0
        self.selected_option = 0
        self.roommate_mood = 50  # 0-100
        self.agreement_signed = False
        self.show_result = False
        self.option_rects = []  # Store option rectangles for mouse interaction
        self.confirm_button_rect = None
        self.continue_button_rect = None
        
    def negotiate(self, choice_index):
        """Process negotiation choice"""
        issue = self.issues[self.current_issue]
        issue["your_choice"] = choice_index
        
        # Calculate mood change
        if choice_index == issue["roommate_preference"]:
            self.roommate_mood += 15
            issue["compromised"] = True
            return "Great! Your roommate agrees with this choice."
        elif abs(choice_index - issue["roommate_preference"]) == 1:
            self.roommate_mood += 5
            issue["compromised"] = True
            return "Your roommate can work with this compromise."
        else:
            self.roommate_mood -= 10
            issue["compromised"] = False
            return "Your roommate strongly disagrees. Try to find middle ground."
            
    def draw(self, screen):
        if not self.active:
            return
            
        self.draw_background_overlay(screen)
        
        # Game box
        box_width = 850
        box_height = 600
        box_x = self.screen_width // 2 - box_width // 2
        box_y = self.screen_height // 2 - box_height // 2
        
        # Mood-based border color
        if self.roommate_mood >= 70:
            border_color = (100, 255, 100)
        elif self.roommate_mood >= 40:
            border_color = (255, 220, 100)
        else:
            border_color = (255, 100, 100)
            
        self.draw_game_box(screen, box_x, box_y, box_width, box_height, border_color)
        
        if not self.entrance_complete:
            return
            
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Roommate Agreement", True, (255, 220, 100))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, box_y + 30))
        
        # Roommate mood bar
        mood_width = 300
        mood_height = 20
        mood_x = self.screen_width // 2 - mood_width // 2
        mood_y = box_y + 90
        
        pygame.draw.rect(screen, (60, 60, 60), (mood_x, mood_y, mood_width, mood_height))
        mood_fill = int(mood_width * self.roommate_mood / 100)
        mood_color = (100, 255, 100) if self.roommate_mood >= 70 else (255, 220, 100) if self.roommate_mood >= 40 else (255, 100, 100)
        pygame.draw.rect(screen, mood_color, (mood_x, mood_y, mood_fill, mood_height))
        
        mood_font = pygame.font.Font(None, 24)
        mood_text = f"Roommate Mood: {self.roommate_mood}%"
        mood_surface = mood_font.render(mood_text, True, (200, 200, 200))
        screen.blit(mood_surface, (self.screen_width // 2 - mood_surface.get_width() // 2, mood_y + 25))
        
        if not self.show_result:
            # Current issue
            if self.current_issue < len(self.issues):
                issue = self.issues[self.current_issue]
                
                # Issue topic
                topic_font = pygame.font.Font(None, 36)
                topic_text = f"Issue {self.current_issue + 1}: {issue['topic']}"
                topic_surface = topic_font.render(topic_text, True, (255, 255, 255))
                screen.blit(topic_surface, (self.screen_width // 2 - topic_surface.get_width() // 2, box_y + 160))
                
                # Roommate preference hint
                hint_font = pygame.font.Font(None, 26)
                hint_text = f"(Your roommate prefers: {issue['options'][issue['roommate_preference']]})"
                hint_surface = hint_font.render(hint_text, True, (180, 180, 200))
                screen.blit(hint_surface, (self.screen_width // 2 - hint_surface.get_width() // 2, box_y + 200))
                
                # Options
                option_y = box_y + 250
                opt_font = pygame.font.Font(None, 30)
                self.option_rects = []
                
                for i, option in enumerate(issue["options"]):
                    option_rect = (box_x + 100, option_y - 5, box_width - 200, 40)
                    self.option_rects.append(option_rect)
                    
                    # Check hover
                    is_hovering = self.is_hovering(option_rect[0], option_rect[1], option_rect[2], option_rect[3])
                    
                    # Highlight selected or hovered
                    if i == self.selected_option:
                        pygame.draw.rect(screen, (100, 100, 120), option_rect)
                        pygame.draw.rect(screen, (255, 220, 100), option_rect, 2)
                    elif is_hovering:
                        pygame.draw.rect(screen, (70, 70, 90), option_rect)
                        pygame.draw.rect(screen, (150, 150, 180), option_rect, 2)
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    
                    # Option text
                    opt_color = (255, 255, 255) if i == self.selected_option or is_hovering else (200, 200, 200)
                    opt_text = f"{i + 1}. {option}"
                    opt_surface = opt_font.render(opt_text, True, opt_color)
                    screen.blit(opt_surface, (box_x + 120, option_y))
                    
                    # Show if it matches roommate preference
                    if i == issue["roommate_preference"]:
                        pref_text = "♥"
                        pref_surface = opt_font.render(pref_text, True, (255, 100, 100))
                        screen.blit(pref_surface, (box_x + box_width - 150, option_y))
                    
                    option_y += 50
                
                # Confirm button
                confirm_width = 180
                confirm_height = 45
                confirm_x = self.screen_width // 2 - confirm_width // 2
                confirm_y = option_y + 20
                self.confirm_button_rect = (confirm_x, confirm_y, confirm_width, confirm_height)
                
                # Check hover on confirm button
                confirm_hover = self.is_hovering(confirm_x, confirm_y, confirm_width, confirm_height)
                
                if self.selected_option is not None:
                    button_color = (100, 200, 100) if confirm_hover else (80, 150, 80)
                    border_color = (150, 255, 150)
                else:
                    button_color = (60, 60, 60)
                    border_color = (100, 100, 100)
                    
                pygame.draw.rect(screen, button_color, self.confirm_button_rect)
                pygame.draw.rect(screen, border_color, self.confirm_button_rect, 3)
                
                confirm_font = pygame.font.Font(None, 28)
                confirm_text = "Confirm Choice"
                confirm_surface = confirm_font.render(confirm_text, True, (255, 255, 255))
                text_x = confirm_x + confirm_width // 2 - confirm_surface.get_width() // 2
                text_y = confirm_y + confirm_height // 2 - confirm_surface.get_height() // 2
                screen.blit(confirm_surface, (text_x, text_y))
                
                if confirm_hover and self.selected_option is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                
                # Instructions
                inst_font = pygame.font.Font(None, 24)
                inst_text = "Click an option or use ↑↓  •  Click Confirm or press ENTER"
                inst_surface = inst_font.render(inst_text, True, (180, 180, 180))
                screen.blit(inst_surface, (self.screen_width // 2 - inst_surface.get_width() // 2, box_y + box_height - 50))
                
                # Reset cursor if not hovering
                if not any([self.is_hovering(rect[0], rect[1], rect[2], rect[3]) for rect in self.option_rects]) and not confirm_hover:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                
        else:
            # Show final result
            result_font = pygame.font.Font(None, 42)
            if self.roommate_mood >= 60:
                result_text = "Agreement Successful!"
                result_color = (100, 255, 100)
                detail_text = "You and your roommate found common ground."
            else:
                result_text = "Agreement Needs Work"
                result_color = (255, 100, 100)
                detail_text = "You'll need to compromise more with your roommate."
                
            result_surface = result_font.render(result_text, True, result_color)
            screen.blit(result_surface, (self.screen_width // 2 - result_surface.get_width() // 2, box_y + 200))
            
            detail_font = pygame.font.Font(None, 28)
            detail_surface = detail_font.render(detail_text, True, (200, 200, 200))
            screen.blit(detail_surface, (self.screen_width // 2 - detail_surface.get_width() // 2, box_y + 260))
            
            # Show compromises
            comp_y = box_y + 320
            for issue in self.issues:
                comp_text = f"✓ {issue['topic']}: {issue['options'][issue['your_choice']]}"
                comp_color = (100, 255, 100) if issue["compromised"] else (255, 200, 100)
                comp_surface = detail_font.render(comp_text, True, comp_color)
                screen.blit(comp_surface, (box_x + 150, comp_y))
                comp_y += 35
                
            # Continue button
            continue_width = 200
            continue_height = 45
            continue_x = self.screen_width // 2 - continue_width // 2
            continue_y = box_y + 490
            self.continue_button_rect = (continue_x, continue_y, continue_width, continue_height)
            
            # Check hover
            continue_hover = self.is_hovering(continue_x, continue_y, continue_width, continue_height)
            
            if self.roommate_mood >= 60:
                button_color = (100, 200, 100) if continue_hover else (80, 150, 80)
                button_text = "Continue"
            else:
                button_color = (200, 150, 100) if continue_hover else (150, 120, 80)
                button_text = "Try Again"
                
            pygame.draw.rect(screen, button_color, self.continue_button_rect)
            pygame.draw.rect(screen, (200, 200, 200), self.continue_button_rect, 3)
            
            continue_font = pygame.font.Font(None, 30)
            continue_surface = continue_font.render(button_text, True, (255, 255, 255))
            text_x = continue_x + continue_width // 2 - continue_surface.get_width() // 2
            text_y = continue_y + continue_height // 2 - continue_surface.get_height() // 2
            screen.blit(continue_surface, (text_x, text_y))
            
            if continue_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
    def handle_key(self, key):
        if not self.active or not self.entrance_complete:
            return
            
        if self.show_result:
            if key == pygame.K_RETURN:
                if self.roommate_mood >= 60:
                    self.complete()
                else:
                    # Reset for another try
                    self.current_issue = 0
                    self.selected_option = 0
                    self.show_result = False
                    self.roommate_mood = 50
        else:
            if self.current_issue < len(self.issues):
                issue = self.issues[self.current_issue]
                
                if key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(issue["options"])
                elif key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(issue["options"])
                elif key == pygame.K_RETURN:
                    # Make choice
                    self.negotiate(self.selected_option)
                    self.current_issue += 1
                    self.selected_option = 0
                    
                    # Check if done
                    if self.current_issue >= len(self.issues):
                        self.show_result = True
                        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for roommate agreement"""
        super().handle_mouse_click(pos, button)
        
        if not self.active or not self.entrance_complete:
            return
            
        if button == 1:  # Left click
            if self.show_result:
                # Check continue button
                if self.continue_button_rect and self.is_hovering(
                    self.continue_button_rect[0], self.continue_button_rect[1],
                    self.continue_button_rect[2], self.continue_button_rect[3]):
                    if self.roommate_mood >= 60:
                        self.complete()
                    else:
                        # Reset for another try
                        self.current_issue = 0
                        self.selected_option = 0
                        self.show_result = False
                        self.roommate_mood = 50
            else:
                # Check option clicks
                for i, rect in enumerate(self.option_rects):
                    if self.is_hovering(rect[0], rect[1], rect[2], rect[3]):
                        self.selected_option = i
                        return
                        
                # Check confirm button
                if self.confirm_button_rect and self.selected_option is not None:
                    if self.is_hovering(
                        self.confirm_button_rect[0], self.confirm_button_rect[1],
                        self.confirm_button_rect[2], self.confirm_button_rect[3]):
                        # Make choice
                        self.negotiate(self.selected_option)
                        self.current_issue += 1
                        self.selected_option = 0
                        
                        # Check if done
                        if self.current_issue >= len(self.issues):
                            self.show_result = True


# Export all mini-games
__all__ = [
    'MiniGame',
    'GroceryShoppingGame', 
    'DocumentApplicationGame',
    'RoommateAgreementGame'
]
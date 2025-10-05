import pygame
import random
import math
from shared.constants import *

class PizzaMakingActivity:
    """Professional pizza making tutorial activity"""
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        
        # Pizza making state
        self.current_order = 0
        self.orders = []
        self.current_pizza = None
        self.pizza_state = "dough"  # dough, sauce, cheese, toppings, bake, done
        self.bake_timer = 0
        self.score = 0
        
        # UI positioning
        self.orders_panel_x = 50
        self.orders_panel_y = 100
        self.orders_panel_width = 250
        self.orders_panel_height = 400
        
        self.work_area_x = 350
        self.work_area_y = 100
        self.work_area_width = 600
        self.work_area_height = 400
        
        self.instructions_y = 550
        
        # Pizza components
        self.pizza_x = SCREEN_WIDTH // 2
        self.pizza_y = 300
        self.pizza_radius = 100
        
        # Toppings positions (relative to pizza center)
        self.topping_positions = []
        self.generate_topping_positions()
        
        # Mouse state
        self.mouse_held = False
        self.current_topping = None
        self.toppings_added = 0  # Track how many toppings added
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Generate orders
        self.generate_orders()
        
    def generate_topping_positions(self):
        """Generate random positions for toppings on pizza"""
        for _ in range(20):
            # Random angle and distance from center
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(0, self.pizza_radius - 20)
            x = int(distance * math.cos(angle))
            y = int(distance * math.sin(angle))
            self.topping_positions.append((x, y))
            
    def generate_orders(self):
        """Generate 3 pizza orders"""
        pizza_types = [
            {
                'name': 'Margherita',
                'toppings': ['basil'],
                'color': (100, 200, 100)
            },
            {
                'name': 'Pepperoni',
                'toppings': ['pepperoni'],
                'color': (200, 100, 100)
            },
            {
                'name': 'Veggie Deluxe',
                'toppings': ['mushrooms', 'peppers'],
                'color': (150, 150, 100)
            }
        ]
        
        # Pick 3 random orders
        for i in range(3):
            order = random.choice(pizza_types).copy()
            order['number'] = i + 1
            order['completed'] = False
            self.orders.append(order)
            
    def start(self):
        """Start the pizza making activity"""
        self.active = True
        self.completed = False
        self.current_order = 0
        self.start_new_pizza()
        
    def start_new_pizza(self):
        """Start making a new pizza"""
        if self.current_order < len(self.orders):
            self.current_pizza = {
                'has_dough': False,
                'has_sauce': False,
                'has_cheese': False,
                'toppings': [],
                'baked': False
            }
            self.pizza_state = "dough"
            self.bake_timer = 0
            self.toppings_added = 0
        else:
            # All orders complete
            self.complete()
            
    def complete(self):
        """Complete the activity"""
        self.completed = True
        self.active = False
        # Don't call complete_current_objective here - let the interior handle it
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        # Number keys for quick actions
        if self.pizza_state == "dough" and key == pygame.K_1:
            self.current_pizza['has_dough'] = True
            self.pizza_state = "sauce"
        elif self.pizza_state == "sauce" and key == pygame.K_2:
            self.current_pizza['has_sauce'] = True
            self.pizza_state = "cheese"
        elif self.pizza_state == "cheese" and key == pygame.K_3:
            self.current_pizza['has_cheese'] = True
            self.pizza_state = "toppings"
        elif self.pizza_state == "bake" and key == pygame.K_5:
            self.pizza_state = "baking"
            self.bake_timer = 3.0  # 3 seconds to bake
            
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return
            
        x, y = pos
        
        # Check if clicking on pizza during toppings phase
        if self.pizza_state == "toppings":
            dx = x - self.pizza_x
            dy = y - self.pizza_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.pizza_radius - 20:
                # Add a random topping from the current order
                order = self.orders[self.current_order]
                if order['toppings']:
                    topping = order['toppings'][self.toppings_added % len(order['toppings'])]
                    self.current_pizza['toppings'].append({
                        'type': topping,
                        'x': dx,
                        'y': dy
                    })
                    self.toppings_added += 1
                    
                    # Check if enough toppings
                    required_toppings = len(order['toppings']) * 3
                    if self.toppings_added >= required_toppings:
                        self.pizza_state = "bake"
                return
        
        # Check ingredient buttons
        button_y = self.work_area_y + self.work_area_height + 20
        button_height = 40
        button_spacing = 10
        
        buttons = []
        if self.pizza_state == "dough":
            buttons.append(("Add Dough", 0))
        elif self.pizza_state == "sauce":
            buttons.append(("Add Sauce", 1))
        elif self.pizza_state == "cheese":
            buttons.append(("Add Cheese", 2))
        elif self.pizza_state == "toppings":
            order = self.orders[self.current_order]
            for i, topping in enumerate(order['toppings']):
                buttons.append((f"Add {topping.title()}", 3 + i))
        elif self.pizza_state == "bake":
            buttons.append(("Bake Pizza", 5))
            
        # Check button clicks
        start_x = self.work_area_x
        for i, (text, action) in enumerate(buttons):
            button_width = 150
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(pos):
                if action == 0:  # Dough
                    self.current_pizza['has_dough'] = True
                    self.pizza_state = "sauce"
                elif action == 1:  # Sauce
                    self.current_pizza['has_sauce'] = True
                    self.pizza_state = "cheese"
                elif action == 2:  # Cheese
                    self.current_pizza['has_cheese'] = True
                    self.pizza_state = "toppings"
                elif action >= 3 and action < 5:  # Toppings
                    topping_index = action - 3
                    order = self.orders[self.current_order]
                    if topping_index < len(order['toppings']):
                        topping = order['toppings'][topping_index]
                        # Place topping immediately at mouse position if over pizza
                        dx = pos[0] - self.pizza_x
                        dy = pos[1] - self.pizza_y
                        distance = math.sqrt(dx * dx + dy * dy)
                        
                        if distance < self.pizza_radius - 20:
                            self.current_pizza['toppings'].append({
                                'type': topping,
                                'x': dx,
                                'y': dy
                            })
                            self.toppings_added += 1
                            
                            # Check if enough toppings are added
                            required_toppings = len(order['toppings']) * 3
                            if self.toppings_added >= required_toppings:
                                self.pizza_state = "bake"
                elif action == 5:  # Bake
                    self.pizza_state = "baking"
                    self.bake_timer = 3.0
                    
    def handle_mouse_motion(self, pos):
        """Handle mouse motion for topping placement"""
        if self.mouse_held and self.current_topping:
            # Check if mouse is over pizza
            dx = pos[0] - self.pizza_x
            dy = pos[1] - self.pizza_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.pizza_radius - 10:
                # Can place topping here
                pass
                
    def handle_mouse_release(self, pos, button):
        """Handle mouse release"""
        if button == 1 and self.mouse_held and self.current_topping:
            # Place topping if over pizza
            dx = pos[0] - self.pizza_x
            dy = pos[1] - self.pizza_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.pizza_radius - 20:
                self.current_pizza['toppings'].append({
                    'type': self.current_topping,
                    'x': dx,
                    'y': dy
                })
                self.toppings_added += 1
                
                # Check if enough toppings are added (at least 3 per topping type)
                order = self.orders[self.current_order]
                required_toppings = len(order['toppings']) * 3
                if self.toppings_added >= required_toppings:
                    self.pizza_state = "bake"
                    
            self.mouse_held = False
            self.current_topping = None
            
    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return
            
        # Update baking timer
        if self.pizza_state == "baking":
            self.bake_timer -= dt
            if self.bake_timer <= 0:
                self.current_pizza['baked'] = True
                self.pizza_state = "done"
                
        # Check for completion
        if self.pizza_state == "done":
            self.orders[self.current_order]['completed'] = True
            self.current_order += 1
            self.score += 100
            
            if self.current_order >= len(self.orders):
                # All pizzas complete
                self.complete()
            else:
                # Start next pizza
                self.start_new_pizza()
                
    def draw(self, screen):
        """Draw the pizza making interface"""
        if not self.active:
            return
            
        # Draw full opaque background to ensure we're on top of everything
        screen.fill((20, 20, 25))  # Dark background
        
        # Draw title
        title = self.title_font.render("Pizza Making Station", True, (255, 220, 100))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Draw orders panel
        self.draw_orders_panel(screen)
        
        # Draw work area
        self.draw_work_area(screen)
        
        # Draw instructions
        self.draw_instructions(screen)
        
    def draw_orders_panel(self, screen):
        """Draw the orders panel on the left"""
        # Panel background
        panel_rect = pygame.Rect(self.orders_panel_x, self.orders_panel_y, 
                                self.orders_panel_width, self.orders_panel_height)
        pygame.draw.rect(screen, (40, 40, 45), panel_rect)
        pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3)
        
        # Title
        title = self.font.render("Orders", True, (255, 255, 255))
        screen.blit(title, (self.orders_panel_x + 10, self.orders_panel_y + 10))
        
        # Orders
        y_offset = self.orders_panel_y + 50
        for i, order in enumerate(self.orders):
            # Order background
            order_rect = pygame.Rect(self.orders_panel_x + 10, y_offset, 
                                   self.orders_panel_width - 20, 100)
            
            if i == self.current_order and not order['completed']:
                # Current order - highlight
                pygame.draw.rect(screen, (60, 60, 65), order_rect)
                pygame.draw.rect(screen, (255, 220, 100), order_rect, 2)
            else:
                pygame.draw.rect(screen, (50, 50, 55), order_rect)
                pygame.draw.rect(screen, (100, 100, 100), order_rect, 2)
                
            # Order number
            num_text = self.font.render(f"Order #{order['number']}", True, (255, 255, 255))
            screen.blit(num_text, (order_rect.x + 10, order_rect.y + 10))
            
            # Pizza name
            name_text = self.small_font.render(order['name'], True, order['color'])
            screen.blit(name_text, (order_rect.x + 10, order_rect.y + 40))
            
            # Toppings
            toppings_text = self.small_font.render(f"Toppings: {', '.join(order['toppings'])}", 
                                                  True, (200, 200, 200))
            screen.blit(toppings_text, (order_rect.x + 10, order_rect.y + 65))
            
            # Completed status
            if order['completed']:
                check = self.font.render("✓", True, (100, 255, 100))
                screen.blit(check, (order_rect.right - 30, order_rect.y + 35))
                
            y_offset += 110
            
    def draw_work_area(self, screen):
        """Draw the main work area"""
        # Work area background
        work_rect = pygame.Rect(self.work_area_x, self.work_area_y, 
                               self.work_area_width, self.work_area_height)
        pygame.draw.rect(screen, (45, 45, 50), work_rect)
        pygame.draw.rect(screen, (150, 150, 150), work_rect, 3)
        
        # Draw pizza base
        if self.current_pizza:
            # Dough
            if self.current_pizza['has_dough']:
                pygame.draw.circle(screen, (220, 180, 120), 
                                 (self.pizza_x, self.pizza_y), self.pizza_radius)
                pygame.draw.circle(screen, (180, 140, 80), 
                                 (self.pizza_x, self.pizza_y), self.pizza_radius, 3)
                
            # Sauce
            if self.current_pizza['has_sauce']:
                pygame.draw.circle(screen, (180, 60, 60), 
                                 (self.pizza_x, self.pizza_y), self.pizza_radius - 10)
                
            # Cheese
            if self.current_pizza['has_cheese']:
                # Draw cheese as a solid layer with some texture
                # First draw a solid cheese circle
                pygame.draw.circle(screen, (255, 220, 150), 
                                 (self.pizza_x, self.pizza_y), self.pizza_radius - 10)
                # Add some texture spots for realism
                random.seed(42)  # Fixed seed so cheese doesn't move
                for i in range(30):
                    angle = (i * 137.5) % 360  # Golden angle distribution
                    r = (self.pizza_radius - 20) * (0.3 + (i % 3) * 0.3)
                    x = int(self.pizza_x + r * math.cos(math.radians(angle)))
                    y = int(self.pizza_y + r * math.sin(math.radians(angle)))
                    pygame.draw.circle(screen, (255, 230, 160), (x, y), 4)
                random.seed()  # Reset random seed
                        
            # Toppings
            for topping in self.current_pizza['toppings']:
                x = self.pizza_x + topping['x']
                y = self.pizza_y + topping['y']
                
                if topping['type'] == 'pepperoni':
                    pygame.draw.circle(screen, (150, 50, 50), (x, y), 15)
                    pygame.draw.circle(screen, (100, 30, 30), (x, y), 15, 2)
                elif topping['type'] == 'mushrooms':
                    pygame.draw.circle(screen, (150, 130, 100), (x, y), 12)
                    pygame.draw.circle(screen, (100, 80, 60), (x, y), 12, 2)
                elif topping['type'] == 'peppers':
                    pygame.draw.rect(screen, (50, 150, 50), (x - 10, y - 5, 20, 10))
                    pygame.draw.rect(screen, (30, 100, 30), (x - 10, y - 5, 20, 10), 2)
                elif topping['type'] == 'basil':
                    # Draw leaf shape
                    points = [(x, y - 10), (x - 8, y + 5), (x, y), (x + 8, y + 5)]
                    pygame.draw.polygon(screen, (50, 150, 50), points)
                    pygame.draw.polygon(screen, (30, 100, 30), points, 2)
                    
        # Draw current topping being held
        if self.mouse_held and self.current_topping:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.current_topping == 'pepperoni':
                pygame.draw.circle(screen, (150, 50, 50), (mouse_x, mouse_y), 15)
                pygame.draw.circle(screen, (100, 30, 30), (mouse_x, mouse_y), 15, 2)
            elif self.current_topping == 'mushrooms':
                pygame.draw.circle(screen, (150, 130, 100), (mouse_x, mouse_y), 12)
                pygame.draw.circle(screen, (100, 80, 60), (mouse_x, mouse_y), 12, 2)
            elif self.current_topping == 'peppers':
                pygame.draw.rect(screen, (50, 150, 50), (mouse_x - 10, mouse_y - 5, 20, 10))
                pygame.draw.rect(screen, (30, 100, 30), (mouse_x - 10, mouse_y - 5, 20, 10), 2)
            elif self.current_topping == 'basil':
                points = [(mouse_x, mouse_y - 10), (mouse_x - 8, mouse_y + 5), 
                         (mouse_x, mouse_y), (mouse_x + 8, mouse_y + 5)]
                pygame.draw.polygon(screen, (50, 150, 50), points)
                pygame.draw.polygon(screen, (30, 100, 30), points, 2)
                
        # Baking effect
        if self.pizza_state == "baking":
            # Draw oven effect
            oven_rect = pygame.Rect(self.pizza_x - self.pizza_radius - 20, 
                                   self.pizza_y - self.pizza_radius - 20,
                                   self.pizza_radius * 2 + 40, self.pizza_radius * 2 + 40)
            pygame.draw.rect(screen, (80, 60, 40), oven_rect, 5)
            
            # Baking progress
            progress = 1.0 - (self.bake_timer / 3.0)
            progress_text = self.font.render(f"Baking... {int(progress * 100)}%", 
                                           True, (255, 200, 100))
            screen.blit(progress_text, (self.pizza_x - progress_text.get_width() // 2, 
                                      self.pizza_y + self.pizza_radius + 30))
                                      
        # Draw ingredient buttons
        self.draw_ingredient_buttons(screen)
        
    def draw_ingredient_buttons(self, screen):
        """Draw buttons for adding ingredients"""
        button_y = self.work_area_y + self.work_area_height + 20
        button_height = 40
        button_spacing = 10
        
        buttons = []
        if self.pizza_state == "dough":
            buttons.append(("Add Dough (1)", (220, 180, 120)))
        elif self.pizza_state == "sauce":
            buttons.append(("Add Sauce (2)", (180, 60, 60)))
        elif self.pizza_state == "cheese":
            buttons.append(("Add Cheese (3)", (255, 220, 150)))
        elif self.pizza_state == "toppings":
            # Just show a visual indicator, not clickable buttons
            order = self.orders[self.current_order]
            toppings_text = f"Adding: {', '.join(order['toppings'])}"
            buttons.append((toppings_text, (100, 150, 100)))
        elif self.pizza_state == "bake":
            buttons.append(("Bake Pizza (5)", (255, 150, 50)))
            
        # Draw buttons
        start_x = self.work_area_x
        for i, (text, color) in enumerate(buttons):
            button_width = 200 if "Click" in text else 150
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            is_hover = button_rect.collidepoint(mouse_pos)
            
            # Draw button
            button_color = tuple(min(255, c + 30) for c in color) if is_hover else color
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
            
            # Draw text
            text_surf = self.small_font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=button_rect.center)
            screen.blit(text_surf, text_rect)
            
    def draw_instructions(self, screen):
        """Draw instructions at the bottom"""
        instructions = ""
        if self.pizza_state == "dough":
            instructions = "Step 1: Add the pizza dough base"
        elif self.pizza_state == "sauce":
            instructions = "Step 2: Spread tomato sauce on the dough"
        elif self.pizza_state == "cheese":
            instructions = "Step 3: Add mozzarella cheese"
        elif self.pizza_state == "toppings":
            order = self.orders[self.current_order]
            required = len(order['toppings']) * 3
            instructions = f"Step 4: Add {', '.join(order['toppings'])} - Click directly on the pizza! ({self.toppings_added}/{required})"
        elif self.pizza_state == "bake":
            instructions = "Step 5: Put the pizza in the oven"
        elif self.pizza_state == "baking":
            instructions = "Pizza is baking... Please wait!"
        elif self.pizza_state == "done":
            instructions = "Pizza complete! Starting next order..."
            
        # Draw instruction box
        inst_rect = pygame.Rect(50, self.instructions_y, SCREEN_WIDTH - 100, 60)
        pygame.draw.rect(screen, (40, 40, 45), inst_rect)
        pygame.draw.rect(screen, (150, 150, 150), inst_rect, 2)
        
        # Draw text
        inst_surf = self.font.render(instructions, True, (255, 255, 255))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, self.instructions_y + 30))
        screen.blit(inst_surf, inst_rect)
        
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, (255, 220, 100))
        screen.blit(score_text, (SCREEN_WIDTH - 150, 70))
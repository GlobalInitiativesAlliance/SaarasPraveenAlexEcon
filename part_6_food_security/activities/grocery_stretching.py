"""Grocery Stretching Game - Make limited food budget last"""

import pygame
import random
import math
from shared.constants import *

class GroceryStretchingGame:
    """Try to feed yourself on an impossible budget"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Budget and time
        self.budget = 47.00  # Weekly SNAP benefit for 1 person
        self.days_to_feed = 7
        self.current_day = 1
        self.money_remaining = self.budget
        
        # Nutrition tracking
        self.calories_today = 0
        self.calories_needed = 2000  # Daily
        self.protein_today = 0
        self.vitamins_today = 0
        self.hunger_level = 30  # 0-100
        
        # Health impacts
        self.energy_level = 70
        self.health_score = 75
        self.concentration = 80
        
        # Shopping state
        self.current_store = 'grocery'  # grocery, dollar, corner
        self.cart = []
        self.cart_total = 0
        self.shopping_mode = True
        self.selected_item = 0
        self.selected_category = 0
        
        # Food inventory
        self.food_inventory = {}
        
        # Meal history
        self.meals_eaten = []
        self.skipped_meals = 0
        
        # Visual elements
        self.price_particles = []
        self.hunger_shake = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.price_font = pygame.font.Font(None, 28)
        
        # Store inventories
        self.stores = {
            'grocery': {
                'name': 'Grocery Store',
                'price_modifier': 1.0,
                'quality_modifier': 1.0,
                'categories': {
                    'Proteins': [
                        {'name': 'Chicken breast (1 lb)', 'price': 5.99, 'calories': 750, 'protein': 140, 'vitamins': 20, 'servings': 4},
                        {'name': 'Ground beef (1 lb)', 'price': 4.99, 'calories': 1150, 'protein': 100, 'vitamins': 15, 'servings': 4},
                        {'name': 'Eggs (dozen)', 'price': 3.49, 'calories': 840, 'protein': 72, 'vitamins': 30, 'servings': 12},
                        {'name': 'Canned tuna', 'price': 1.29, 'calories': 200, 'protein': 40, 'vitamins': 10, 'servings': 2},
                        {'name': 'Peanut butter', 'price': 3.99, 'calories': 2500, 'protein': 100, 'vitamins': 5, 'servings': 16},
                        {'name': 'Dried beans (1 lb)', 'price': 1.49, 'calories': 1500, 'protein': 100, 'vitamins': 25, 'servings': 8}
                    ],
                    'Grains': [
                        {'name': 'White rice (5 lb)', 'price': 4.99, 'calories': 8000, 'protein': 160, 'vitamins': 5, 'servings': 40},
                        {'name': 'Pasta (1 lb)', 'price': 1.29, 'calories': 1600, 'protein': 60, 'vitamins': 10, 'servings': 8},
                        {'name': 'White bread', 'price': 1.99, 'calories': 1200, 'protein': 40, 'vitamins': 15, 'servings': 20},
                        {'name': 'Oatmeal', 'price': 2.99, 'calories': 2400, 'protein': 80, 'vitamins': 20, 'servings': 20},
                        {'name': 'Ramen (6 pack)', 'price': 2.49, 'calories': 2280, 'protein': 48, 'vitamins': 0, 'servings': 6}
                    ],
                    'Produce': [
                        {'name': 'Bananas (bunch)', 'price': 1.99, 'calories': 600, 'protein': 6, 'vitamins': 40, 'servings': 6},
                        {'name': 'Apples (3 lb)', 'price': 3.99, 'calories': 750, 'protein': 3, 'vitamins': 45, 'servings': 9},
                        {'name': 'Potatoes (5 lb)', 'price': 2.99, 'calories': 1750, 'protein': 50, 'vitamins': 35, 'servings': 15},
                        {'name': 'Carrots (2 lb)', 'price': 1.99, 'calories': 200, 'protein': 4, 'vitamins': 60, 'servings': 8},
                        {'name': 'Cabbage', 'price': 1.49, 'calories': 200, 'protein': 10, 'vitamins': 50, 'servings': 8},
                        {'name': 'Frozen vegetables', 'price': 1.99, 'calories': 150, 'protein': 6, 'vitamins': 40, 'servings': 4}
                    ],
                    'Dairy': [
                        {'name': 'Milk (gallon)', 'price': 3.99, 'calories': 2400, 'protein': 128, 'vitamins': 40, 'servings': 16},
                        {'name': 'Cheese (8 oz)', 'price': 3.49, 'calories': 900, 'protein': 56, 'vitamins': 20, 'servings': 8},
                        {'name': 'Yogurt (4 pack)', 'price': 2.99, 'calories': 400, 'protein': 20, 'vitamins': 25, 'servings': 4}
                    ]
                }
            },
            'dollar': {
                'name': 'Dollar Store',
                'price_modifier': 0.8,
                'quality_modifier': 0.6,
                'categories': {
                    'Canned': [
                        {'name': 'Canned soup', 'price': 1.00, 'calories': 300, 'protein': 10, 'vitamins': 15, 'servings': 2},
                        {'name': 'Canned pasta', 'price': 1.00, 'calories': 400, 'protein': 12, 'vitamins': 5, 'servings': 2},
                        {'name': 'Canned vegetables', 'price': 1.00, 'calories': 100, 'protein': 4, 'vitamins': 20, 'servings': 2}
                    ],
                    'Snacks': [
                        {'name': 'Chips', 'price': 1.00, 'calories': 600, 'protein': 8, 'vitamins': 0, 'servings': 3},
                        {'name': 'Cookies', 'price': 1.00, 'calories': 800, 'protein': 8, 'vitamins': 0, 'servings': 6},
                        {'name': 'Crackers', 'price': 1.00, 'calories': 500, 'protein': 10, 'vitamins': 5, 'servings': 8}
                    ]
                }
            },
            'corner': {
                'name': 'Corner Store',
                'price_modifier': 1.5,
                'quality_modifier': 0.7,
                'categories': {
                    'Quick': [
                        {'name': 'Hot dog', 'price': 2.99, 'calories': 300, 'protein': 10, 'vitamins': 0, 'servings': 1},
                        {'name': 'Microwave burrito', 'price': 2.49, 'calories': 400, 'protein': 12, 'vitamins': 5, 'servings': 1},
                        {'name': 'Instant noodles', 'price': 0.99, 'calories': 380, 'protein': 8, 'vitamins': 0, 'servings': 1}
                    ]
                }
            }
        }
        
    def start(self):
        """Start the grocery stretching game"""
        self.active = True
        self.completed = False
        self.current_day = 1
        self.shopping_mode = True
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if self.shopping_mode:
            self.handle_shopping_keys(key)
        else:
            self.handle_meal_keys(key)
            
    def handle_shopping_keys(self, key):
        """Handle shopping mode keys"""
        store = self.stores[self.current_store]
        categories = list(store['categories'].keys())
        
        if key == pygame.K_TAB:
            # Switch stores
            store_names = list(self.stores.keys())
            current_idx = store_names.index(self.current_store)
            self.current_store = store_names[(current_idx + 1) % len(store_names)]
            self.selected_category = 0
            self.selected_item = 0
            
        elif key == pygame.K_LEFT:
            # Previous category
            self.selected_category = max(0, self.selected_category - 1)
            self.selected_item = 0
            
        elif key == pygame.K_RIGHT:
            # Next category
            self.selected_category = min(len(categories) - 1, self.selected_category + 1)
            self.selected_item = 0
            
        elif key == pygame.K_UP:
            # Previous item
            self.selected_item = max(0, self.selected_item - 1)
            
        elif key == pygame.K_DOWN:
            # Next item
            current_category = categories[self.selected_category]
            items = store['categories'][current_category]
            self.selected_item = min(len(items) - 1, self.selected_item + 1)
            
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Add to cart
            self.add_to_cart()
            
        elif key == pygame.K_c:
            # Checkout
            if self.cart:
                self.checkout()
                
        elif key == pygame.K_r:
            # Remove from cart
            if self.cart:
                removed = self.cart.pop()
                self.cart_total -= removed['price']
                
    def handle_meal_keys(self, key):
        """Handle meal planning keys"""
        if key == pygame.K_1:
            # Eat breakfast
            self.eat_meal('breakfast')
        elif key == pygame.K_2:
            # Eat lunch
            self.eat_meal('lunch')
        elif key == pygame.K_3:
            # Eat dinner
            self.eat_meal('dinner')
        elif key == pygame.K_4:
            # Skip meal
            self.skip_meal()
        elif key == pygame.K_SPACE:
            # Next day
            self.advance_day()
            
    def add_to_cart(self):
        """Add selected item to cart"""
        store = self.stores[self.current_store]
        categories = list(store['categories'].keys())
        current_category = categories[self.selected_category]
        items = store['categories'][current_category]
        
        if self.selected_item < len(items):
            item = items[self.selected_item].copy()
            
            # Apply store modifiers
            item['price'] *= store['price_modifier']
            item['vitamins'] *= store['quality_modifier']
            
            if self.cart_total + item['price'] <= self.money_remaining:
                self.cart.append(item)
                self.cart_total += item['price']
                
                # Visual feedback
                for _ in range(10):
                    self.price_particles.append({
                        'x': SCREEN_WIDTH // 2,
                        'y': 400,
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(-3, -1),
                        'life': 30,
                        'text': f"${item['price']:.2f}"
                    })
            else:
                # Can't afford
                self.hunger_shake = 20
                
    def checkout(self):
        """Complete purchase"""
        self.money_remaining -= self.cart_total
        
        # Add items to inventory
        for item in self.cart:
            if item['name'] in self.food_inventory:
                self.food_inventory[item['name']]['servings'] += item['servings']
            else:
                self.food_inventory[item['name']] = item.copy()
                
        # Clear cart
        self.cart = []
        self.cart_total = 0
        
        # Switch to meal mode
        self.shopping_mode = False
        
    def eat_meal(self, meal_type):
        """Eat a meal from inventory"""
        if not self.food_inventory:
            self.skip_meal()
            return
            
        # Calculate meal from available food
        meal_calories = 0
        meal_protein = 0
        meal_vitamins = 0
        items_used = []
        
        # Try to compose a balanced meal
        target_calories = 600 if meal_type == 'dinner' else 400
        
        # Sort food by calorie density
        available_food = sorted(self.food_inventory.items(), 
                               key=lambda x: x[1]['calories'] / x[1]['servings'],
                               reverse=True)
        
        for food_name, food_data in available_food:
            if meal_calories < target_calories and food_data['servings'] > 0:
                # Use one serving
                meal_calories += food_data['calories'] / food_data['servings']
                meal_protein += food_data['protein'] / food_data['servings']
                meal_vitamins += food_data['vitamins'] / food_data['servings']
                
                food_data['servings'] -= 1
                items_used.append(food_name)
                
                # Remove if empty
                if food_data['servings'] <= 0:
                    del self.food_inventory[food_name]
                    
        # Update nutrition
        self.calories_today += meal_calories
        self.protein_today += meal_protein
        self.vitamins_today += meal_vitamins
        
        # Update hunger
        self.hunger_level = max(0, self.hunger_level - (meal_calories / 20))
        
        # Record meal
        self.meals_eaten.append({
            'type': meal_type,
            'calories': meal_calories,
            'items': items_used
        })
        
    def skip_meal(self):
        """Skip a meal"""
        self.skipped_meals += 1
        self.hunger_level = min(100, self.hunger_level + 15)
        
        # Health impacts
        self.energy_level = max(0, self.energy_level - 10)
        self.concentration = max(0, self.concentration - 5)
        
    def advance_day(self):
        """Move to next day"""
        # Daily impacts based on nutrition
        calorie_ratio = self.calories_today / self.calories_needed
        
        if calorie_ratio < 0.5:
            self.health_score -= 5
            self.energy_level -= 15
            self.concentration -= 10
        elif calorie_ratio < 0.8:
            self.health_score -= 2
            self.energy_level -= 5
            self.concentration -= 5
        else:
            self.energy_level = min(100, self.energy_level + 5)
            
        # Vitamin impacts
        if self.vitamins_today < 50:
            self.health_score -= 3
            
        # Reset daily nutrition
        self.calories_today = 0
        self.protein_today = 0
        self.vitamins_today = 0
        
        # Next day
        self.current_day += 1
        
        if self.current_day > self.days_to_feed:
            self.end_game()
        else:
            # Can shop again if have money
            if self.money_remaining > 1:
                self.shopping_mode = True
            else:
                # Must survive on inventory
                self.shopping_mode = False
                
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update hunger effects
        self.hunger_level = min(100, self.hunger_level + dt * 2)  # Slowly get hungry
        
        # Update visual effects
        if self.hunger_shake > 0:
            self.hunger_shake -= 1
            
        # Update particles
        for particle in self.price_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.price_particles.remove(particle)
                
    def end_game(self):
        """End the grocery game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate average nutrition
        avg_health = self.health_score
        total_meals = self.meals_eaten
        meal_skip_rate = self.skipped_meals / (self.days_to_feed * 3)
        
        if avg_health < 50:
            message = "Severe malnutrition. Health deteriorating."
            success = False
        elif meal_skip_rate > 0.3:
            message = f"Skipped {int(meal_skip_rate * 100)}% of meals. Constant hunger."
            success = False
        elif self.money_remaining < 0:
            message = "Ran out of money. Going hungry."
            success = False
        else:
            message = f"Survived the week. Health: {int(avg_health)}%"
            success = avg_health > 60
            
        return {
            'health': -20 if not success else -5,
            'stress': 20 if not success else 10,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the grocery stretching interface"""
        if not self.active:
            return
            
        # Background with hunger effect
        base_color = 245
        if self.hunger_level > 70:
            base_color -= int((self.hunger_level - 70) / 2)
        
        screen.fill((base_color, base_color, base_color + 5))
        
        # Apply shake if can't afford
        offset_x = random.randint(-2, 2) if self.hunger_shake > 0 else 0
        offset_y = random.randint(-2, 2) if self.hunger_shake > 0 else 0
        
        if self.shopping_mode:
            self.draw_shopping_interface(screen, offset_x, offset_y)
        else:
            self.draw_meal_interface(screen, offset_x, offset_y)
            
        # Draw particles
        for particle in self.price_particles:
            price_surf = self.small_font.render(particle['text'], True, (255, 100, 100))
            price_surf.set_alpha(int(255 * particle['life'] / 30))
            screen.blit(price_surf, (int(particle['x']), int(particle['y'])))
            
    def draw_shopping_interface(self, screen, offset_x, offset_y):
        """Draw shopping mode"""
        # Title
        store = self.stores[self.current_store]
        title = f"{store['name']} - Day {self.current_day}/7"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset_x, 30 + offset_y))
        screen.blit(title_surf, title_rect)
        
        # Budget display
        budget_rect = pygame.Rect(50, 70, 200, 80)
        pygame.draw.rect(screen, (255, 255, 255), budget_rect)
        pygame.draw.rect(screen, (100, 200, 100) if self.money_remaining > 10 else (255, 200, 100), budget_rect, 3)
        
        budget_text = f"${self.money_remaining:.2f}"
        budget_surf = self.title_font.render(budget_text, True, (50, 100, 50))
        budget_text_rect = budget_surf.get_rect(center=(budget_rect.centerx, budget_rect.centery - 10))
        screen.blit(budget_surf, budget_text_rect)
        
        remaining_text = "Remaining"
        remaining_surf = self.small_font.render(remaining_text, True, (80, 80, 90))
        remaining_rect = remaining_surf.get_rect(center=(budget_rect.centerx, budget_rect.centery + 20))
        screen.blit(remaining_surf, remaining_rect)
        
        # Categories
        categories = list(store['categories'].keys())
        cat_x = 50
        cat_y = 170
        
        for i, category in enumerate(categories):
            cat_rect = pygame.Rect(cat_x + i * 150, cat_y, 140, 30)
            
            if i == self.selected_category:
                pygame.draw.rect(screen, (220, 230, 255), cat_rect)
                pygame.draw.rect(screen, (150, 170, 220), cat_rect, 2)
            else:
                pygame.draw.rect(screen, (240, 240, 245), cat_rect)
                pygame.draw.rect(screen, (200, 200, 210), cat_rect, 1)
                
            cat_surf = self.font.render(category, True, (60, 60, 80))
            cat_text_rect = cat_surf.get_rect(center=cat_rect.center)
            screen.blit(cat_surf, cat_text_rect)
            
        # Items in current category
        current_category = categories[self.selected_category]
        items = store['categories'][current_category]
        
        items_rect = pygame.Rect(50, 220, SCREEN_WIDTH - 100, 280)
        pygame.draw.rect(screen, (255, 255, 255), items_rect)
        pygame.draw.rect(screen, (200, 200, 210), items_rect, 2)
        
        item_y = items_rect.y + 10
        for i, item in enumerate(items):
            # Selection highlight
            if i == self.selected_item:
                sel_rect = pygame.Rect(items_rect.x + 5, item_y - 5, items_rect.width - 10, 50)
                pygame.draw.rect(screen, (230, 240, 255), sel_rect)
                
            # Item name
            name_surf = self.font.render(item['name'], True, (40, 40, 60))
            screen.blit(name_surf, (items_rect.x + 20, item_y))
            
            # Price (with store modifier)
            actual_price = item['price'] * store['price_modifier']
            price_color = (100, 200, 100) if actual_price <= self.money_remaining - self.cart_total else (255, 100, 100)
            price_text = f"${actual_price:.2f}"
            price_surf = self.price_font.render(price_text, True, price_color)
            screen.blit(price_surf, (items_rect.x + 300, item_y))
            
            # Nutrition info
            nutrition_text = f"{item['calories']} cal, {item['servings']} servings"
            nutrition_surf = self.small_font.render(nutrition_text, True, (100, 100, 120))
            screen.blit(nutrition_surf, (items_rect.x + 20, item_y + 25))
            
            # Quality indicator
            if store['quality_modifier'] < 1.0:
                quality_text = f"(Quality: {int(store['quality_modifier'] * 100)}%)"
                quality_surf = self.small_font.render(quality_text, True, (255, 150, 100))
                screen.blit(quality_surf, (items_rect.x + 400, item_y + 25))
                
            item_y += 55
            
        # Cart display
        cart_rect = pygame.Rect(SCREEN_WIDTH - 250, 70, 200, 150)
        pygame.draw.rect(screen, (250, 255, 250), cart_rect)
        pygame.draw.rect(screen, (150, 200, 150), cart_rect, 2)
        
        cart_title = "Shopping Cart"
        cart_surf = self.font.render(cart_title, True, (60, 100, 60))
        screen.blit(cart_surf, (cart_rect.x + 10, cart_rect.y + 5))
        
        # Cart items (show last 3)
        cart_y = cart_rect.y + 30
        for item in self.cart[-3:]:
            item_text = f"{item['name'][:15]}..."
            item_surf = self.small_font.render(item_text, True, (80, 80, 90))
            screen.blit(item_surf, (cart_rect.x + 10, cart_y))
            cart_y += 20
            
        # Cart total
        total_text = f"Total: ${self.cart_total:.2f}"
        total_color = (100, 200, 100) if self.cart_total <= self.money_remaining else (255, 100, 100)
        total_surf = self.font.render(total_text, True, total_color)
        screen.blit(total_surf, (cart_rect.x + 10, cart_rect.bottom - 30))
        
        # Instructions
        inst_lines = [
            "TAB: Switch stores | ←→: Categories | ↑↓: Items | ENTER: Add to cart",
            "C: Checkout | R: Remove last item"
        ]
        inst_y = SCREEN_HEIGHT - 60
        for line in inst_lines:
            inst_surf = self.small_font.render(line, True, (120, 120, 140))
            inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect)
            inst_y += 20
            
    def draw_meal_interface(self, screen, offset_x, offset_y):
        """Draw meal planning mode"""
        # Title
        title = f"Day {self.current_day} - Meal Planning"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Nutrition status
        status_rect = pygame.Rect(50, 80, 300, 180)
        pygame.draw.rect(screen, (255, 255, 255), status_rect)
        pygame.draw.rect(screen, (200, 200, 210), status_rect, 2)
        
        status_title = "Today's Nutrition"
        status_surf = self.font.render(status_title, True, (60, 60, 80))
        screen.blit(status_surf, (status_rect.x + 10, status_rect.y + 10))
        
        # Nutrition bars
        nutrition_y = status_rect.y + 40
        
        # Calories
        cal_percent = min(100, (self.calories_today / self.calories_needed) * 100)
        self.draw_nutrition_bar(screen, "Calories", self.calories_today, self.calories_needed, 
                               status_rect.x + 20, nutrition_y, cal_percent > 80)
        
        # Protein
        protein_percent = min(100, (self.protein_today / 50) * 100)  # 50g daily target
        self.draw_nutrition_bar(screen, "Protein", self.protein_today, 50,
                               status_rect.x + 20, nutrition_y + 40, protein_percent > 60)
                               
        # Vitamins
        vitamin_percent = min(100, self.vitamins_today)
        self.draw_nutrition_bar(screen, "Vitamins", self.vitamins_today, 100,
                               status_rect.x + 20, nutrition_y + 80, vitamin_percent > 50)
                               
        # Health metrics
        health_rect = pygame.Rect(400, 80, 350, 180)
        pygame.draw.rect(screen, (255, 255, 255), health_rect)
        pygame.draw.rect(screen, (200, 200, 210), health_rect, 2)
        
        health_title = "Health Status"
        health_surf = self.font.render(health_title, True, (60, 60, 80))
        screen.blit(health_surf, (health_rect.x + 10, health_rect.y + 10))
        
        # Health indicators
        indicators = [
            ('Hunger', self.hunger_level, True),  # Lower is better
            ('Energy', self.energy_level, False),
            ('Health', self.health_score, False),
            ('Focus', self.concentration, False)
        ]
        
        ind_y = health_rect.y + 40
        for name, value, inverse in indicators:
            color = self.get_indicator_color(value, inverse)
            
            # Label
            label_surf = self.font.render(name, True, (80, 80, 90))
            screen.blit(label_surf, (health_rect.x + 20, ind_y))
            
            # Bar
            bar_rect = pygame.Rect(health_rect.x + 120, ind_y, 200, 20)
            pygame.draw.rect(screen, (220, 220, 230), bar_rect)
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * value / 100), 20)
            pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, (180, 180, 190), bar_rect, 2)
            
            # Value
            value_text = f"{int(value)}%"
            value_surf = self.small_font.render(value_text, True, (100, 100, 110))
            screen.blit(value_surf, (bar_rect.right + 10, ind_y + 2))
            
            ind_y += 35
            
        # Food inventory
        inv_rect = pygame.Rect(50, 280, SCREEN_WIDTH - 100, 180)
        pygame.draw.rect(screen, (250, 250, 255), inv_rect)
        pygame.draw.rect(screen, (200, 200, 220), inv_rect, 2)
        
        inv_title = "Food Inventory"
        inv_surf = self.font.render(inv_title, True, (60, 60, 80))
        screen.blit(inv_surf, (inv_rect.x + 10, inv_rect.y + 10))
        
        # List food items
        inv_y = inv_rect.y + 40
        inv_x = inv_rect.x + 20
        items_shown = 0
        
        if not self.food_inventory:
            empty_text = "No food remaining!"
            empty_surf = self.font.render(empty_text, True, (255, 100, 100))
            empty_rect = empty_surf.get_rect(center=inv_rect.center)
            screen.blit(empty_surf, empty_rect)
        else:
            for food_name, food_data in list(self.food_inventory.items())[:8]:
                food_text = f"{food_name}: {food_data['servings']} servings"
                food_surf = self.small_font.render(food_text, True, (80, 80, 100))
                screen.blit(food_surf, (inv_x, inv_y))
                
                items_shown += 1
                if items_shown % 2 == 0:
                    inv_y += 25
                    inv_x = inv_rect.x + 20
                else:
                    inv_x += 350
                    
        # Meal options
        options_rect = pygame.Rect(100, 480, SCREEN_WIDTH - 200, 80)
        pygame.draw.rect(screen, (240, 255, 240), options_rect)
        pygame.draw.rect(screen, (150, 200, 150), options_rect, 2)
        
        options = [
            "1 - Eat breakfast",
            "2 - Eat lunch", 
            "3 - Eat dinner",
            "4 - Skip meal",
            "SPACE - Next day"
        ]
        
        opt_x = options_rect.x + 20
        opt_y = options_rect.centery - 20
        
        for i, opt in enumerate(options[:4]):
            opt_surf = self.font.render(opt, True, (60, 100, 60))
            screen.blit(opt_surf, (opt_x, opt_y))
            opt_x += 160
            
        # Next day option
        next_surf = self.font.render(options[4], True, (100, 100, 150))
        next_rect = next_surf.get_rect(center=(options_rect.centerx, options_rect.bottom - 15))
        screen.blit(next_surf, next_rect)
        
    def draw_nutrition_bar(self, screen, label, current, target, x, y, is_good):
        """Draw a nutrition progress bar"""
        # Label
        label_surf = self.font.render(label, True, (80, 80, 90))
        screen.blit(label_surf, (x, y))
        
        # Values
        value_text = f"{int(current)}/{int(target)}"
        value_surf = self.small_font.render(value_text, True, (100, 100, 110))
        screen.blit(value_surf, (x + 80, y + 2))
        
        # Bar
        bar_rect = pygame.Rect(x + 150, y, 100, 20)
        pygame.draw.rect(screen, (220, 220, 230), bar_rect)
        
        fill_percent = min(1.0, current / target)
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * fill_percent), 20)
        
        if is_good:
            color = (100, 200, 100)
        else:
            if fill_percent < 0.3:
                color = (255, 100, 100)
            elif fill_percent < 0.6:
                color = (255, 200, 100)
            else:
                color = (255, 255, 100)
                
        pygame.draw.rect(screen, color, fill_rect)
        pygame.draw.rect(screen, (180, 180, 190), bar_rect, 2)
        
    def get_indicator_color(self, value, inverse=False):
        """Get color based on indicator value"""
        if inverse:  # Lower is better
            if value > 70:
                return (255, 100, 100)
            elif value > 40:
                return (255, 200, 100)
            else:
                return (100, 200, 100)
        else:  # Higher is better
            if value < 30:
                return (255, 100, 100)
            elif value < 60:
                return (255, 200, 100)
            else:
                return (100, 200, 100)
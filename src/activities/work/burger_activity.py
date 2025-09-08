import pygame
import random
import math
from src.constants import *

class BurgerFlippingActivity:
    """Professional burger flipping minigame"""
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        
        # Burger making state
        self.current_order = 0
        self.orders = []
        self.current_burger = None
        self.burger_state = "patty"  # patty, flip, bun, toppings, serve, complete
        self.cook_timer = 0
        self.flip_timer = 0
        self.score = 0
        self.patties_cooked = 0
        
        # Completion state
        self.completion_timer = 0
        self.show_completion = False
        
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
        
        # Grill and burger positions
        self.grill_x = SCREEN_WIDTH // 2
        self.grill_y = 250
        self.grill_width = 400
        self.grill_height = 200
        
        # Patty states
        self.patty_x = self.grill_x
        self.patty_y = self.grill_y
        self.patty_size = 80
        self.patty_cooked_side1 = 0  # 0-100%
        self.patty_cooked_side2 = 0  # 0-100%
        self.patty_flipped = False
        self.patty_burnt = False
        
        # Assembly area
        self.assembly_x = self.grill_x
        self.assembly_y = self.grill_y + 150
        
        # Mouse state
        self.mouse_held = False
        self.dragging_item = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Burger assembly
        self.assembled_items = []  # List of items on the burger
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Generate orders
        self.generate_orders()
        
    def generate_orders(self):
        """Generate 3 burger orders"""
        burger_types = [
            {
                'name': 'Classic Burger',
                'items': ['bottom_bun', 'patty', 'lettuce', 'tomato', 'top_bun'],
                'color': (200, 150, 100)
            },
            {
                'name': 'Cheese Burger',
                'items': ['bottom_bun', 'patty', 'cheese', 'lettuce', 'top_bun'],
                'color': (220, 180, 100)
            },
            {
                'name': 'Deluxe Burger',
                'items': ['bottom_bun', 'patty', 'cheese', 'lettuce', 'tomato', 'onion', 'top_bun'],
                'color': (180, 140, 90)
            }
        ]
        
        # Pick 3 random orders
        for i in range(3):
            order = random.choice(burger_types).copy()
            order['number'] = i + 1
            order['completed'] = False
            self.orders.append(order)
            
    def start(self):
        """Start the burger flipping activity"""
        self.active = True
        self.completed = False
        self.current_order = 0
        self.start_new_burger()
        
    def start_new_burger(self):
        """Start making a new burger"""
        if self.current_order >= len(self.orders):
            self.complete_activity()
            return
            
        self.current_burger = self.orders[self.current_order]
        self.burger_state = "patty"
        self.cook_timer = 0
        self.flip_timer = 0
        self.patty_cooked_side1 = 0
        self.patty_cooked_side2 = 0
        self.patty_flipped = False
        self.patty_burnt = False
        self.assembled_items = []
        self.patties_cooked = 0
        
        # Reset dragging state
        self.dragging_item = None
        self.mouse_held = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
    def complete_activity(self):
        """Complete the burger making activity"""
        self.burger_state = "complete"
        self.show_completion = True
        self.completion_timer = 0
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            self.active = False
            
    def handle_mouse_click(self, pos, button):
        """Handle mouse click"""
        if button == 1:  # Left click
            self.mouse_held = True
            
            # Clear any stuck dragging state
            if self.dragging_item:
                self.dragging_item = None
            
            if self.burger_state == "patty" and not self.patty_flipped:
                # Check if clicking on patty to flip
                patty_rect = pygame.Rect(self.patty_x - self.patty_size//2, 
                                       self.patty_y - self.patty_size//2,
                                       self.patty_size, self.patty_size)
                if patty_rect.collidepoint(pos) and self.patty_cooked_side1 >= 40:
                    self.flip_patty()
                    
            elif self.burger_state == "bun":
                # Check if clicking on bottom bun at new position
                bun_x = self.grill_x - 200
                bun_y = self.assembly_y - 100
                bun_rect = pygame.Rect(bun_x - 30, bun_y - 10, 60, 20)
                if bun_rect.collidepoint(pos):
                    self.dragging_item = "bottom_bun"
                    self.drag_offset_x = pos[0] - bun_x
                    self.drag_offset_y = pos[1] - bun_y
                    
            elif self.burger_state == "toppings":
                # Check various topping areas
                self.check_topping_click(pos)
                
    def check_topping_click(self, pos):
        """Check if clicking on a topping"""
        toppings_y = self.grill_y - 100
        
        # Define topping positions
        toppings = [
            ("lettuce", self.grill_x - 150, toppings_y),
            ("tomato", self.grill_x - 50, toppings_y),
            ("cheese", self.grill_x + 50, toppings_y),
            ("onion", self.grill_x + 150, toppings_y),
            ("top_bun", self.grill_x + 250, toppings_y)
        ]
        
        for topping, x, y in toppings:
            rect = pygame.Rect(x - 30, y - 20, 60, 40)
            if rect.collidepoint(pos):
                # Check if this topping is needed for current order
                if topping in self.current_burger['items']:
                    self.dragging_item = topping
                    self.drag_offset_x = pos[0] - x
                    self.drag_offset_y = pos[1] - y
                break
                
    def flip_patty(self):
        """Flip the burger patty"""
        self.patty_flipped = True
        self.flip_timer = 0
        
    def handle_mouse_motion(self, pos):
        """Handle mouse motion"""
        pass
        
    def handle_mouse_release(self, pos, button):
        """Handle mouse release"""
        if button == 1:
            self.mouse_held = False
            
            if self.dragging_item:
                # Check if dropping on assembly area
                assembly_rect = pygame.Rect(self.assembly_x - 100, self.assembly_y - 50, 200, 100)
                
                if assembly_rect.collidepoint(pos):
                    # Add item to burger
                    self.assembled_items.append(self.dragging_item)
                    
                    # Check if burger is complete
                    if self.dragging_item == "top_bun":
                        self.check_burger_complete()
                    elif self.dragging_item == "bottom_bun":
                        self.burger_state = "patty_ready"
                        
                # Always clear the dragging item
                self.dragging_item = None
                self.drag_offset_x = 0
                self.drag_offset_y = 0
                
    def check_burger_complete(self):
        """Check if the assembled burger matches the order"""
        required_items = self.current_burger['items']
        
        # Simple check - just verify all items are present
        if all(item in self.assembled_items for item in required_items):
            # Order complete!
            self.orders[self.current_order]['completed'] = True
            self.score += 100
            self.current_order += 1
            
            # Start next burger or complete activity
            if self.current_order < len(self.orders):
                pygame.time.wait(1000)  # Brief pause
                self.start_new_burger()
            else:
                self.complete_activity()
        
    def update(self, dt):
        """Update the burger making activity"""
        if not self.active:
            return
            
        # Handle completion state
        if self.burger_state == "complete":
            self.completion_timer += dt
            if self.completion_timer > 3.0:  # Show completion for 3 seconds
                self.active = False
                self.completed = True
            return
            
        # Safety check for stuck dragging
        if self.dragging_item and not self.mouse_held:
            self.dragging_item = None
            
        # Update cooking timers
        if self.burger_state == "patty":
            self.cook_timer += dt
            
            if not self.patty_flipped:
                # Cook first side
                self.patty_cooked_side1 = min(100, self.patty_cooked_side1 + dt * 20)  # 5 seconds to cook
                if self.patty_cooked_side1 >= 100:
                    self.patty_burnt = True
            else:
                # Cook second side
                self.patty_cooked_side2 = min(100, self.patty_cooked_side2 + dt * 20)
                if self.patty_cooked_side2 >= 100:
                    self.patty_burnt = True
                    
                # Check if ready to move to bun stage
                if self.patty_cooked_side2 >= 80 and not self.patty_burnt:
                    self.burger_state = "bun"
                    self.patties_cooked += 1
                    
        elif self.burger_state == "patty_ready":
            # Patty is on bun, ready for toppings
            self.assembled_items.append("patty")
            self.burger_state = "toppings"
            
    def draw(self, screen):
        """Draw the burger making interface"""
        if not self.active:
            return
            
        # Draw dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((20, 20, 20))
        overlay.set_alpha(240)
        screen.blit(overlay, (0, 0))
        
        # Draw completion screen
        if self.burger_state == "complete":
            self.draw_completion_screen(screen)
            return
        
        # Draw title
        title = self.title_font.render("Burger Flipping Training", True, (255, 220, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(title, title_rect)
        
        # Draw orders panel
        self.draw_orders_panel(screen)
        
        # Draw work area
        self.draw_work_area(screen)
        
        # Draw instructions
        self.draw_instructions(screen)
        
        # Draw dragging item - add extra check
        if self.dragging_item and self.dragging_item != "":
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Only draw if we have a valid item
            if self.dragging_item in ['bottom_bun', 'top_bun', 'patty', 'lettuce', 'tomato', 'cheese', 'onion']:
                self.draw_item(screen, self.dragging_item, 
                             mouse_x - self.drag_offset_x, 
                             mouse_y - self.drag_offset_y)
        
    def draw_orders_panel(self, screen):
        """Draw the orders panel"""
        # Panel background
        panel_rect = pygame.Rect(self.orders_panel_x, self.orders_panel_y, 
                               self.orders_panel_width, self.orders_panel_height)
        pygame.draw.rect(screen, (40, 40, 40), panel_rect)
        pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3)
        
        # Title
        title = self.font.render("Orders", True, (255, 220, 100))
        title_rect = title.get_rect(center=(panel_rect.centerx, panel_rect.y + 30))
        screen.blit(title, title_rect)
        
        # Draw each order
        y_offset = 80
        for i, order in enumerate(self.orders):
            # Order background
            order_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + y_offset,
                                   panel_rect.width - 20, 80)
            
            if i == self.current_order:
                pygame.draw.rect(screen, (60, 60, 80), order_rect)
            else:
                pygame.draw.rect(screen, (30, 30, 30), order_rect)
                
            pygame.draw.rect(screen, order['color'], order_rect, 2)
            
            # Order text
            order_text = self.small_font.render(f"Order #{order['number']}", True, (255, 255, 255))
            screen.blit(order_text, (order_rect.x + 10, order_rect.y + 10))
            
            name_text = self.small_font.render(order['name'], True, (200, 200, 200))
            screen.blit(name_text, (order_rect.x + 10, order_rect.y + 35))
            
            # Completion status
            if order['completed']:
                status_text = self.small_font.render("✓ Complete", True, (100, 255, 100))
                screen.blit(status_text, (order_rect.x + 10, order_rect.y + 55))
            
            y_offset += 100
            
    def draw_work_area(self, screen):
        """Draw the main work area"""
        # Work area background
        work_rect = pygame.Rect(self.work_area_x, self.work_area_y,
                              self.work_area_width, self.work_area_height)
        pygame.draw.rect(screen, (50, 45, 40), work_rect)
        pygame.draw.rect(screen, (150, 150, 150), work_rect, 3)
        
        if self.burger_state == "patty":
            self.draw_grill(screen)
        elif self.burger_state in ["bun", "patty_ready", "toppings"]:
            self.draw_assembly_area(screen)
            
    def draw_grill(self, screen):
        """Draw the grill and patty"""
        # Draw grill
        grill_rect = pygame.Rect(self.grill_x - self.grill_width//2, 
                               self.grill_y - self.grill_height//2,
                               self.grill_width, self.grill_height)
        pygame.draw.rect(screen, (60, 60, 60), grill_rect)
        
        # Grill lines
        for i in range(10):
            y = grill_rect.y + i * 20
            pygame.draw.line(screen, (40, 40, 40), 
                           (grill_rect.x, y), (grill_rect.right, y), 2)
        
        # Draw patty
        if not self.patty_flipped:
            # Bottom side cooking
            cook_color = self.get_cook_color(self.patty_cooked_side1)
        else:
            # Top side cooking
            cook_color = self.get_cook_color(self.patty_cooked_side2)
            
        pygame.draw.circle(screen, cook_color, 
                         (int(self.patty_x), int(self.patty_y)), 
                         self.patty_size//2)
        
        # Draw flip prompt if ready
        if not self.patty_flipped and self.patty_cooked_side1 >= 40:
            prompt = self.small_font.render("Click to flip!", True, (255, 255, 100))
            prompt_rect = prompt.get_rect(center=(self.patty_x, self.patty_y - 60))
            screen.blit(prompt, prompt_rect)
            
        # Draw cooking progress
        if not self.patty_burnt:
            if not self.patty_flipped:
                progress_text = f"Side 1: {int(self.patty_cooked_side1)}%"
            else:
                progress_text = f"Side 2: {int(self.patty_cooked_side2)}%"
            
            progress = self.small_font.render(progress_text, True, (255, 255, 255))
            progress_rect = progress.get_rect(center=(self.grill_x, self.grill_y + 120))
            screen.blit(progress, progress_rect)
        else:
            burnt_text = self.font.render("BURNT!", True, (255, 50, 50))
            burnt_rect = burnt_text.get_rect(center=(self.grill_x, self.grill_y + 120))
            screen.blit(burnt_text, burnt_rect)
            
    def draw_assembly_area(self, screen):
        """Draw the burger assembly area"""
        # Draw counter
        counter_rect = pygame.Rect(self.assembly_x - 150, self.assembly_y - 20, 300, 100)
        pygame.draw.rect(screen, (100, 80, 60), counter_rect)
        pygame.draw.rect(screen, (150, 120, 90), counter_rect, 3)
        
        # Draw assembly area highlight
        if self.burger_state == "bun" and not self.assembled_items:
            # Highlight drop zone
            highlight_rect = pygame.Rect(self.assembly_x - 100, self.assembly_y - 50, 200, 100)
            pygame.draw.rect(screen, (255, 255, 100), highlight_rect, 3)
            drop_text = self.small_font.render("Drop Here", True, (255, 255, 100))
            drop_rect = drop_text.get_rect(center=(self.assembly_x, self.assembly_y + 60))
            screen.blit(drop_text, drop_rect)
        
        # Draw assembled items
        y_offset = 0
        for item in self.assembled_items:
            self.draw_item(screen, item, self.assembly_x, self.assembly_y - y_offset)
            y_offset += 10
            
        # Draw available ingredients
        if self.burger_state == "bun":
            # Show bottom bun closer to assembly area
            bun_x = self.grill_x - 200
            bun_y = self.assembly_y - 100
            self.draw_item(screen, "bottom_bun", bun_x, bun_y)
            label = self.small_font.render("Bottom Bun", True, (255, 255, 255))
            label_rect = label.get_rect(center=(bun_x, bun_y + 30))
            screen.blit(label, label_rect)
            
            # Draw instruction
            instruction = self.small_font.render("Drag to assembly area →", True, (255, 255, 100))
            screen.blit(instruction, (bun_x + 80, bun_y - 5))
            
        elif self.burger_state == "toppings":
            # Show all toppings
            toppings_y = self.grill_y - 100
            toppings = [
                ("lettuce", "Lettuce", self.grill_x - 150),
                ("tomato", "Tomato", self.grill_x - 50),
                ("cheese", "Cheese", self.grill_x + 50),
                ("onion", "Onion", self.grill_x + 150),
                ("top_bun", "Top Bun", self.grill_x + 250)
            ]
            
            for item, label_text, x in toppings:
                if item in self.current_burger['items']:
                    self.draw_item(screen, item, x, toppings_y)
                    label = self.small_font.render(label_text, True, (255, 255, 255))
                    label_rect = label.get_rect(center=(x, toppings_y + 30))
                    screen.blit(label, label_rect)
                    
    def draw_item(self, screen, item_type, x, y):
        """Draw a burger item"""
        colors = {
            'bottom_bun': (180, 140, 80),
            'top_bun': (180, 140, 80),
            'patty': (100, 60, 40),
            'lettuce': (100, 200, 100),
            'tomato': (200, 50, 50),
            'cheese': (255, 200, 50),
            'onion': (220, 180, 220)
        }
        
        color = colors.get(item_type, (150, 150, 150))
        
        if 'bun' in item_type:
            # Draw bun shape
            pygame.draw.ellipse(screen, color, 
                              pygame.Rect(x - 30, y - 10, 60, 20))
        elif item_type == 'patty':
            # Draw patty
            pygame.draw.circle(screen, color, (int(x), int(y)), 30)
        else:
            # Draw other toppings as rectangles
            pygame.draw.rect(screen, color, 
                           pygame.Rect(x - 25, y - 8, 50, 16))
            
    def get_cook_color(self, cook_percent):
        """Get color based on cooking percentage"""
        if cook_percent < 20:
            return (255, 180, 180)  # Raw
        elif cook_percent < 40:
            return (220, 140, 120)  # Rare
        elif cook_percent < 60:
            return (180, 100, 80)   # Medium rare
        elif cook_percent < 80:
            return (140, 80, 60)    # Medium
        elif cook_percent < 95:
            return (100, 60, 40)    # Well done
        else:
            return (60, 40, 30)     # Burnt
            
    def draw_instructions(self, screen):
        """Draw instructions at the bottom"""
        instructions = {
            "patty": "Cook the patty on both sides. Click to flip when ready!",
            "bun": "Drag the bottom bun to the assembly area",
            "patty_ready": "Great! Now add the toppings",
            "toppings": f"Add toppings for {self.current_burger['name']}"
        }
        
        instruction_text = instructions.get(self.burger_state, "")
        if instruction_text:
            text_surf = self.font.render(instruction_text, True, (255, 255, 200))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, self.instructions_y))
            screen.blit(text_surf, text_rect)
            
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (50, 50))
        
    def draw_completion_screen(self, screen):
        """Draw the completion screen"""
        # Title
        title = self.title_font.render("Training Complete!", True, (100, 255, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title, title_rect)
        
        # Score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Score: {self.score}/300", True, (255, 220, 100))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        # Message
        msg_font = pygame.font.Font(None, 36)
        messages = [
            "Excellent work!",
            "You've mastered burger flipping!",
            "Please wait..."
        ]
        
        y_offset = SCREEN_HEIGHT // 2 + 80
        for msg in messages:
            msg_surf = msg_font.render(msg, True, (200, 200, 200))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(msg_surf, msg_rect)
            y_offset += 40
            
        # Progress bar
        bar_width = 300
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT // 2 + 200
        
        # Background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        
        # Progress
        progress = min(1.0, self.completion_timer / 3.0)
        pygame.draw.rect(screen, (100, 255, 100), 
                        (bar_x, bar_y, int(bar_width * progress), bar_height))
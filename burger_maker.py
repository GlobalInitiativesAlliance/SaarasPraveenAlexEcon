import pygame
import random
import math

class BurgerMakerModal:
    def __init__(self, screen_width=1000, screen_height=700):
        pygame.init()
        
        # Constants
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.FPS = 60
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BROWN = (139, 69, 19)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.LIGHT_BROWN = (210, 180, 140)
        self.DARK_RED = (139, 0, 0)
        self.BUN_COLOR = (222, 184, 135)
        self.PATTY_COLOR = (101, 67, 33)
        self.CHEESE_COLOR = (255, 215, 0)
        self.LETTUCE_COLOR = (124, 252, 0)
        self.TOMATO_COLOR = (255, 99, 71)
        self.PICKLE_COLOR = (107, 142, 35)
        self.ONION_COLOR = (255, 248, 220)
        
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Burger Making Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game objects
        self.burger_layers = []
        self.ingredients = []
        self.dragging_ingredient = None
        self.cooking = False
        self.cooking_timer = 0
        self.running = False
        self.finished = False
        self.burger_base_y = self.SCREEN_HEIGHT // 2 + 100
        self.burger_center_x = self.SCREEN_WIDTH // 2
        
    class Ingredient:
        def __init__(self, x, y, ingredient_type, color, width=80, height=20):
            self.x = x
            self.y = y
            self.ingredient_type = ingredient_type
            self.color = color
            self.width = width
            self.height = height
            self.dragging = False
            self.on_burger = False
            self.cooked = False
            self.original_pos = (x, y)
            self.layer_position = -1
            
        def draw(self, screen):
            color = self.color
            if self.cooked and self.ingredient_type == "patty":
                # Darker, more cooked appearance for patty
                color = tuple(max(0, c - 40) for c in color)
                
            if self.ingredient_type == "bottom_bun":
                # Draw bottom bun as rounded rectangle
                pygame.draw.ellipse(screen, color, 
                                  (self.x - self.width//2, self.y - self.height//2, 
                                   self.width, self.height))
                # Add sesame seeds
                if not self.dragging:
                    for i in range(5):
                        seed_x = self.x - 30 + i * 15
                        seed_y = self.y - 8
                        pygame.draw.circle(screen, (255, 255, 255), (seed_x, seed_y), 2)
                        
            elif self.ingredient_type == "top_bun":
                # Draw top bun as rounded dome
                pygame.draw.ellipse(screen, color, 
                                  (self.x - self.width//2, self.y - self.height, 
                                   self.width, self.height * 2))
                # Add sesame seeds
                if not self.dragging:
                    for i in range(5):
                        seed_x = self.x - 30 + i * 15
                        seed_y = self.y - 5
                        pygame.draw.circle(screen, (255, 255, 255), (seed_x, seed_y), 2)
                        
            elif self.ingredient_type == "patty":
                # Draw patty as flattened oval
                pygame.draw.ellipse(screen, color, 
                                  (self.x - self.width//2, self.y - self.height//2, 
                                   self.width, self.height))
                # Add grill marks if cooked
                if self.cooked:
                    mark_color = tuple(max(0, c - 60) for c in color)
                    for i in range(3):
                        y_pos = self.y - 6 + i * 6
                        pygame.draw.line(screen, mark_color, 
                                       (self.x - 25, y_pos), (self.x + 25, y_pos), 2)
                        
            elif self.ingredient_type == "cheese":
                # Draw cheese as melted square
                points = [(self.x - self.width//2, self.y - self.height//2),
                         (self.x + self.width//2, self.y - self.height//2),
                         (self.x + self.width//2 + 5, self.y + self.height//2),
                         (self.x - self.width//2 - 5, self.y + self.height//2)]
                pygame.draw.polygon(screen, color, points)
                
            elif self.ingredient_type == "lettuce":
                # Draw lettuce as wavy rectangle
                for i in range(self.width // 10):
                    wave_x = self.x - self.width//2 + i * 10
                    wave_y = self.y + math.sin(i * 0.5) * 3
                    pygame.draw.circle(screen, color, (int(wave_x), int(wave_y)), 8)
                    
            elif self.ingredient_type == "tomato":
                # Draw tomato as red circles
                for i in range(3):
                    tomato_x = self.x - 20 + i * 20
                    pygame.draw.circle(screen, color, (tomato_x, int(self.y)), 12)
                    pygame.draw.circle(screen, (200, 50, 50), (tomato_x, int(self.y)), 12, 2)
                    
            elif self.ingredient_type == "pickle":
                # Draw pickles as green ovals
                for i in range(4):
                    pickle_x = self.x - 30 + i * 20
                    pygame.draw.ellipse(screen, color,
                                      (pickle_x - 8, self.y - 6, 16, 12))
                    
            elif self.ingredient_type == "onion":
                # Draw onion as white/transparent rings
                for i in range(3):
                    ring_x = self.x - 20 + i * 20
                    pygame.draw.circle(screen, color, (ring_x, int(self.y)), 10, 3)
            
        def is_clicked(self, pos):
            return (abs(pos[0] - self.x) <= self.width//2 and 
                   abs(pos[1] - self.y) <= self.height//2)
            
        def is_near_burger(self, burger_center_x, burger_base_y):
            return (abs(self.x - burger_center_x) <= 100 and 
                   abs(self.y - burger_base_y) <= 200)

    def setup_ingredients(self):
        # Create ingredient stations
        ingredient_data = [
            ("bottom_bun", self.BUN_COLOR, 90, 25),
            ("patty", self.PATTY_COLOR, 75, 15),
            ("cheese", self.CHEESE_COLOR, 70, 10),
            ("lettuce", self.LETTUCE_COLOR, 80, 15),
            ("tomato", self.TOMATO_COLOR, 75, 12),
            ("pickle", self.PICKLE_COLOR, 70, 8),
            ("onion", self.ONION_COLOR, 65, 10),
            ("top_bun", self.BUN_COLOR, 90, 30)
        ]
        
        start_x = 80
        start_y = 100
        spacing = 70
        
        for i, (ing_type, color, width, height) in enumerate(ingredient_data):
            # Create multiple of each ingredient (except buns - only 2 each)
            count = 2 if "bun" in ing_type else 6
            for j in range(count):
                x = start_x + (j % 3) * 45
                y = start_y + i * spacing + (j // 3) * 35
                ingredient = self.Ingredient(x, y, ing_type, color, width, height)
                self.ingredients.append(ingredient)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()
                    
                    # Check if cook button is clicked
                    cook_button_rect = pygame.Rect(self.SCREEN_WIDTH - 150, self.SCREEN_HEIGHT - 80, 120, 50)
                    if cook_button_rect.collidepoint(pos) and not self.cooking:
                        self.start_cooking()
                    
                    # Check if any ingredient is clicked
                    for ingredient in reversed(self.ingredients):  # Reverse to get top-most first
                        if ingredient.is_clicked(pos) and not ingredient.on_burger:
                            ingredient.dragging = True
                            self.dragging_ingredient = ingredient
                            break
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging_ingredient:
                    # Check if ingredient is dropped near burger area
                    if self.dragging_ingredient.is_near_burger(self.burger_center_x, self.burger_base_y):
                        self.add_to_burger(self.dragging_ingredient)
                    else:
                        # Return to original position
                        self.dragging_ingredient.x = self.dragging_ingredient.original_pos[0]
                        self.dragging_ingredient.y = self.dragging_ingredient.original_pos[1]
                    
                    self.dragging_ingredient.dragging = False
                    self.dragging_ingredient = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_ingredient:
                    self.dragging_ingredient.x = event.pos[0]
                    self.dragging_ingredient.y = event.pos[1]
        
        return True
    
    def add_to_burger(self, ingredient):
        ingredient.on_burger = True
        ingredient.layer_position = len(self.burger_layers)
        
        # Position ingredient in burger stack
        layer_height = 20
        ingredient.x = self.burger_center_x
        ingredient.y = self.burger_base_y - (len(self.burger_layers) * layer_height)
        
        self.burger_layers.append(ingredient)
    
    def start_cooking(self):
        # Only cook if we have patties to cook
        if any(layer.ingredient_type == "patty" for layer in self.burger_layers):
            self.cooking = True
            self.cooking_timer = 0
        
    def update(self):
        if self.cooking:
            self.cooking_timer += 1
            cooking_progress = min((self.cooking_timer / 120) * 100, 100)  # 2 seconds to cook
            
            if cooking_progress >= 100:
                self.cooking = False
                self.finished = True
                # Mark all patties as cooked
                for layer in self.burger_layers:
                    if layer.ingredient_type == "patty":
                        layer.cooked = True
    
    def draw(self):
        self.screen.fill((101, 67, 33))  # Brown kitchen background
        
        # Draw title
        title = self.font.render("Burger Making Simulator", True, self.WHITE)
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw ingredient labels
        labels = ["Bottom Bun", "Patty", "Cheese", "Lettuce", "Tomato", "Pickles", "Onions", "Top Bun"]
        for i, label in enumerate(labels):
            text = self.small_font.render(label, True, self.WHITE)
            self.screen.blit(text, (10, 85 + i * 70))
        
        # Draw burger building area
        build_area = pygame.Rect(self.burger_center_x - 150, self.burger_base_y - 200, 300, 250)
        pygame.draw.rect(self.screen, (139, 69, 19), build_area, 3)
        area_text = self.small_font.render("Burger Building Area", True, self.WHITE)
        self.screen.blit(area_text, (build_area.x + 10, build_area.y - 25))
        
        # Draw burger layers (bottom to top)
        for layer in self.burger_layers:
            layer.draw(self.screen)
        
        # Draw loose ingredients
        for ingredient in self.ingredients:
            if not ingredient.on_burger:
                ingredient.draw(self.screen)
        
        # Draw cook button
        cook_button_rect = pygame.Rect(self.SCREEN_WIDTH - 150, self.SCREEN_HEIGHT - 80, 120, 50)
        can_cook = any(layer.ingredient_type == "patty" for layer in self.burger_layers)
        button_color = self.RED if (not self.cooking and can_cook) else (100, 100, 100)
        pygame.draw.rect(self.screen, button_color, cook_button_rect)
        pygame.draw.rect(self.screen, self.BLACK, cook_button_rect, 2)
        
        if self.cooking:
            progress = min((self.cooking_timer / 120) * 100, 100)
            button_text = f"Cooking {int(progress)}%"
        elif can_cook:
            button_text = "COOK!"
        else:
            button_text = "Add Patty"
            
        text = self.small_font.render(button_text, True, self.WHITE)
        text_rect = text.get_rect(center=cook_button_rect.center)
        self.screen.blit(text, text_rect)
        
        # Draw instructions
        if len(self.burger_layers) == 0:
            instruction = self.small_font.render("Start with a bottom bun! Drag ingredients to build your burger.", True, self.WHITE)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        elif not any(layer.ingredient_type == "patty" for layer in self.burger_layers):
            instruction = self.small_font.render("Add a patty to your burger!", True, self.WHITE)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        elif not any(layer.ingredient_type == "top_bun" for layer in self.burger_layers):
            instruction = self.small_font.render("Add more ingredients and finish with a top bun!", True, self.WHITE)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        elif any(layer.ingredient_type == "patty" and not layer.cooked for layer in self.burger_layers):
            instruction = self.small_font.render("Click COOK to grill your patties!", True, self.WHITE)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        else:
            instruction = self.font.render("🍔 Delicious! Your burger is ready! 🍔", True, self.YELLOW)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        
        # Draw cooking effects
        if self.cooking:
            # Sizzle effect around patties
            for layer in self.burger_layers:
                if layer.ingredient_type == "patty":
                    for _ in range(8):
                        sizzle_x = layer.x + random.randint(-40, 40)
                        sizzle_y = layer.y + random.randint(-10, 10)
                        pygame.draw.circle(self.screen, (255, 255, 0, 150), 
                                         (sizzle_x, sizzle_y), random.randint(2, 5))
        
        # Draw burger count
        burger_count = len(self.burger_layers)
        count_text = self.small_font.render(f"Layers: {burger_count}", True, self.WHITE)
        self.screen.blit(count_text, (self.SCREEN_WIDTH - 200, 60))
        
        pygame.display.flip()
    
    def run(self):
        # Initialize game objects
        self.setup_ingredients()
        
        self.running = True
        self.finished = False
        
        while self.running:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
            
            # Check if we should exit (optional - remove if you want it to run indefinitely)
            # if self.finished and pygame.time.get_ticks() > 8000:  # 8 seconds after done
            #     self.running = False
        
        pygame.quit()
        return self.finished

if __name__ == "__main__":
    game = BurgerMakerModal()
    game.run()
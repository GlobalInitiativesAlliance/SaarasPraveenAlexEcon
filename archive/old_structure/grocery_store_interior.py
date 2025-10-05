import pygame
import math
import json
from constants import *
from home_interior import HomeInterior

class GroceryStoreInterior(HomeInterior):
    """Grocery store interior for shopping objectives"""
    def __init__(self, game, room_name="groccery_store"):  # Note: matching JSON spelling
        # Initialize parent class
        super().__init__(game, room_name)
        
        # Override room dimensions
        self.room_width = 20
        self.room_height = 16
        
        # Override player start position
        self.player_x = 10
        self.player_y = 14
        
        # Shopping state
        self.shopping_list = []
        self.items_collected = []
        self.shopping_complete = False
        
        # Store sections
        self.sections = {
            'produce': {'x': 2, 'y': 4, 'w': 4, 'h': 8, 'items': ['Apples', 'Bananas', 'Lettuce']},
            'dairy': {'x': 8, 'y': 4, 'w': 4, 'h': 4, 'items': ['Milk', 'Cheese', 'Yogurt']},
            'bakery': {'x': 14, 'y': 4, 'w': 4, 'h': 4, 'items': ['Bread', 'Bagels', 'Muffins']},
            'frozen': {'x': 8, 'y': 10, 'w': 4, 'h': 4, 'items': ['Ice Cream', 'Frozen Pizza', 'Vegetables']},
            'checkout': {'x': 14, 'y': 12, 'w': 4, 'h': 2}
        }
        
        # Cashier NPC
        self.cashier = {
            'x': 16,
            'y': 13,
            'facing': 'left',
            'name': 'Sam'
        }
        
        # Initialize shopping list
        self.init_shopping_list()
        
    def init_shopping_list(self):
        """Initialize the shopping list based on current objective"""
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and "Groceries" in current_obj.description:
            # Create a simple shopping list
            self.shopping_list = ['Bread', 'Milk', 'Apples']
            self.items_collected = []
            
    def enter(self):
        """Enter the grocery store"""
        super().enter()  # Call parent's enter method
        self.player_x = 10
        self.player_y = 14
        self.player_facing = "up"
        self.init_shopping_list()
            
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_SPACE:
                # Check interactions
                self.check_interactions()
            else:
                # Let parent handle movement
                super().handle_event(event)
                    
    def check_interactions(self):
        """Check for interactions based on player position"""
        # Check if in any section
        for section_name, section in self.sections.items():
            if section_name == 'checkout':
                continue
                
            if self.is_in_section(section):
                # Check available items
                for item in section['items']:
                    if item in self.shopping_list and item not in self.items_collected:
                        self.items_collected.append(item)
                        self.game.objective_manager.show_notification(f"Collected {item}!")
                        
                        # Check if shopping complete
                        if set(self.items_collected) == set(self.shopping_list):
                            self.game.objective_manager.show_notification("Shopping complete! Head to checkout.")
                        return
                        
        # Check if at checkout
        if self.is_near_cashier() and set(self.items_collected) == set(self.shopping_list):
            self.checkout()
            
    def is_in_section(self, section):
        """Check if player is in a store section"""
        return (section['x'] <= self.player_x < section['x'] + section['w'] and
                section['y'] <= self.player_y < section['y'] + section['h'])
                
    def is_near_cashier(self):
        """Check if player is near the cashier"""
        dx = abs(self.player_x - self.cashier['x'])
        dy = abs(self.player_y - self.cashier['y'])
        return dx <= 2 and dy <= 2
        
    def checkout(self):
        """Complete the shopping and checkout"""
        self.shopping_complete = True
        self.game.objective_manager.show_notification("Shopping complete! You learned to budget and shop for essentials.")
        
        # Update game objective if needed
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and "Groceries" in current_obj.description:
            self.game.objective_manager.complete_current_objective()
                    
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        # Check cashier position
        if x == self.cashier['x'] and y == self.cashier['y']:
            return False
            
        # Let parent handle the rest
        return super().is_walkable(x, y)
                    
    def draw(self, screen):
        """Draw the grocery store"""
        if not self.active:
            return
            
        # Let parent draw the room tiles
        super().draw(screen)
        
        # Draw store sections
        self.draw_store_sections(screen)
        
        # Draw cashier
        self.draw_cashier(screen)
        
        # Draw custom UI
        self.draw_custom_ui(screen)
        
    def draw_store_sections(self, screen):
        """Draw store section outlines"""
        for section_name, section in self.sections.items():
            section_x = self.room_x + section['x'] * TILE_SIZE
            section_y = self.room_y + section['y'] * TILE_SIZE
            section_w = section['w'] * TILE_SIZE
            section_h = section['h'] * TILE_SIZE
            
            if section_name == 'produce':
                color = (150, 200, 150)
            elif section_name == 'dairy':
                color = (200, 200, 150)
            elif section_name == 'bakery':
                color = (200, 180, 140)
            elif section_name == 'frozen':
                color = (150, 150, 200)
            elif section_name == 'checkout':
                color = (200, 150, 150)
            else:
                color = (180, 180, 180)
                
            pygame.draw.rect(screen, color, (section_x, section_y, section_w, section_h), 3)
        
    def draw_cashier(self, screen):
        """Draw the cashier NPC"""
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            cashier_x = self.room_x + self.cashier['x'] * TILE_SIZE
            cashier_y = self.room_y + self.cashier['y'] * TILE_SIZE
            self.game.player.draw_at_position(screen, cashier_x, cashier_y, self.cashier['facing'])
        else:
            # Fallback to circle
            pixel_x = self.room_x + self.cashier['x'] * TILE_SIZE + TILE_SIZE // 2
            pixel_y = self.room_y + self.cashier['y'] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, (0, 100, 100), (int(pixel_x), int(pixel_y)), TILE_SIZE // 3)
            
    def draw_custom_ui(self, screen):
        """Draw grocery store specific UI elements"""
        # Instructions
        font = pygame.font.Font(None, 24)
        
        # Check player location for context-sensitive instructions
        instruction_text = None
        in_section = False
        for section_name, section in self.sections.items():
            if section_name != 'checkout' and self.is_in_section(section):
                in_section = True
                break
                
        if in_section and len(self.items_collected) < len(self.shopping_list):
            instruction_text = "Press SPACE to collect items"
        elif self.is_near_cashier() and set(self.items_collected) == set(self.shopping_list):
            instruction_text = "Press SPACE to checkout"
            
        if instruction_text:
            text = font.render(instruction_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
            
        # Room name
        title = font.render("Grocery Store", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (0, 0, 0), title_rect.inflate(20, 10))
        screen.blit(title, title_rect)
        
        # Shopping list
        if self.shopping_list:
            list_y = 60
            list_text = font.render("Shopping List:", True, (255, 255, 255))
            screen.blit(list_text, (20, list_y))
            list_y += 25
            
            for item in self.shopping_list:
                if item in self.items_collected:
                    item_text = font.render(f"✓ {item}", True, (0, 255, 0))
                else:
                    item_text = font.render(f"  {item}", True, (255, 255, 255))
                screen.blit(item_text, (20, list_y))
                list_y += 20
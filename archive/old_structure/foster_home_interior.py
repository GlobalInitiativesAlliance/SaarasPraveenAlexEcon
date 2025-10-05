import pygame
import math
import json
from constants import *
from home_interior import HomeInterior

class FosterHomeInterior(HomeInterior):
    """Foster home interior for tenant rights class"""
    def __init__(self, game, room_name="foster_home"):
        # Initialize parent class
        super().__init__(game, room_name)
        
        # Override room dimensions if needed
        self.room_width = 20
        self.room_height = 16
        
        # Override player start position
        self.player_x = 10
        self.player_y = 14
        
        # Class-specific state
        self.in_class = False
        self.class_complete = False
        
        # Teacher NPC
        self.teacher = {
            'x': 10,
            'y': 4,
            'facing': 'down',
            'name': 'Ms. Rodriguez'
        }
        
    # Remove load_room_data - parent class handles this
            
    def enter(self):
        """Enter the foster home"""
        super().enter()  # Call parent's enter method
        self.player_x = 10
        self.player_y = 14
        self.player_facing = "up"
        
    # Remove exit() - parent class handles this
        
    # Remove handle_input - parent class handles this
            
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_SPACE:
                # Check if near teacher
                if self.is_near_teacher() and not self.in_class:
                    self.start_class()
                elif self.in_class:
                    self.advance_class()
            else:
                # Let parent handle movement
                super().handle_event(event)
                    
    def is_near_teacher(self):
        """Check if player is near the teacher"""
        dx = abs(self.player_x - self.teacher['x'])
        dy = abs(self.player_y - self.teacher['y'])
        return dx <= 2 and dy <= 2
        
    def start_class(self):
        """Start the tenant rights class"""
        self.in_class = True
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.show_notification("Tenant Rights Class started! Press SPACE to continue.")
        
    def advance_class(self):
        """Advance through the class content"""
        # Simple class progression
        self.class_complete = True
        self.in_class = False
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.show_notification("Class complete! You learned about tenant rights.")
        
        # Update game objective if needed
        if hasattr(self.game, 'objective_manager'):
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj and "Tenant Rights Class" in current_obj.description:
                self.game.objective_manager.complete_current_objective()
                    
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        # Check teacher position
        if x == self.teacher['x'] and y == self.teacher['y']:
            return False
            
        # Let parent handle the rest
        return super().is_walkable(x, y)
        
    def draw(self, screen):
        """Draw the foster home"""
        if not self.active:
            return
            
        # Let parent draw the room tiles
        super().draw(screen)
        
        # Draw teacher on top
        self.draw_teacher(screen)
        
        # Draw custom UI
        self.draw_custom_ui(screen)
        
    def draw_teacher(self, screen):
        """Draw the teacher NPC"""
        pixel_x = self.room_x + self.teacher['x'] * TILE_SIZE
        pixel_y = self.room_y + self.teacher['y'] * TILE_SIZE
        
        # Try to use player sprite for teacher
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            # Draw teacher using player sprite (will appear in different idle pose)
            self.game.player.draw_at_position(screen, pixel_x, pixel_y, self.teacher['facing'])
        else:
            # Fallback to circle
            center_x = pixel_x + TILE_SIZE // 2
            center_y = pixel_y + TILE_SIZE // 2
            pygame.draw.circle(screen, (0, 100, 200), (int(center_x), int(center_y)), TILE_SIZE // 3)
            
            # Draw direction indicator
            if self.teacher['facing'] == "down":
                pygame.draw.circle(screen, (255, 255, 255), 
                                 (int(center_x), int(center_y + TILE_SIZE // 4)), 3)
            
    def draw_custom_ui(self, screen):
        """Draw foster home specific UI elements"""
        # Instructions
        font = pygame.font.Font(None, 24)
        
        instruction_text = None
        if self.is_near_teacher() and not self.in_class and not self.class_complete:
            instruction_text = "Press SPACE to start Tenant Rights Class"
        elif self.in_class:
            instruction_text = "In class... Press SPACE to continue"
            
        if instruction_text:
            text = font.render(instruction_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
            
        # Room name (override parent's title)
        title = font.render("Foster Home - Classroom", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (0, 0, 0), title_rect.inflate(20, 10))
        screen.blit(title, title_rect)
import pygame
import math
import json
from constants import *
from home_interior import HomeInterior

class CommunityCenterInterior(HomeInterior):
    """Community center interior for life skills workshop and TLP application"""
    def __init__(self, game, room_name="community_center"):
        # Initialize parent class
        super().__init__(game, room_name)
        
        # Override room dimensions
        self.room_width = 24
        self.room_height = 18
        
        # Override player start position
        self.player_x = 12
        self.player_y = 16
        
        # Activity states
        self.workshop_complete = False
        self.application_submitted = False
        
        # NPCs
        self.workshop_instructor = {
            'x': 6,
            'y': 6,
            'facing': 'down',
            'name': 'Sarah'
        }
        
        self.application_desk = {
            'x': 18,
            'y': 8,
            'facing': 'left',
            'name': 'Mr. Johnson'
        }
        
    def enter(self):
        """Enter the community center"""
        super().enter()  # Call parent's enter method
        self.player_x = 12
        self.player_y = 16
        self.player_facing = "up"
            
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_SPACE:
                # Check interactions
                if self.is_near_workshop_instructor() and not self.workshop_complete:
                    self.attend_workshop()
                elif self.is_near_application_desk() and not self.application_submitted:
                    self.submit_application()
            else:
                # Let parent handle movement
                super().handle_event(event)
                    
    def is_near_workshop_instructor(self):
        """Check if player is near the workshop instructor"""
        dx = abs(self.player_x - self.workshop_instructor['x'])
        dy = abs(self.player_y - self.workshop_instructor['y'])
        return dx <= 2 and dy <= 2
        
    def is_near_application_desk(self):
        """Check if player is near the application desk"""
        dx = abs(self.player_x - self.application_desk['x'])
        dy = abs(self.player_y - self.application_desk['y'])
        return dx <= 2 and dy <= 2
        
    def attend_workshop(self):
        """Attend the life skills workshop"""
        self.workshop_complete = True
        self.game.objective_manager.show_notification("Life Skills Workshop complete! You learned budgeting and job skills.")
        
        # Update game objective if needed
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and "Life Skills Workshop" in current_obj.description:
            self.game.objective_manager.complete_current_objective()
            
    def submit_application(self):
        """Submit TLP application"""
        self.application_submitted = True
        self.game.objective_manager.show_notification("TLP Application submitted! You'll hear back soon.")
        
        # Update game objective if needed
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and "Submit TLP Application" in current_obj.description:
            self.game.objective_manager.complete_current_objective()
                    
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        # Check NPC positions
        if (x == self.workshop_instructor['x'] and y == self.workshop_instructor['y']) or \
           (x == self.application_desk['x'] and y == self.application_desk['y']):
            return False
            
        # Let parent handle the rest
        return super().is_walkable(x, y)
                    
    def draw(self, screen):
        """Draw the community center"""
        if not self.active:
            return
            
        # Let parent draw the room tiles
        super().draw(screen)
        
        # Draw activity areas (outlines)
        self.draw_activity_areas(screen)
        
        # Draw NPCs on top
        self.draw_npcs(screen)
        
        # Draw custom UI
        self.draw_custom_ui(screen)
        
    def draw_activity_areas(self, screen):
        """Draw outlines for activity areas"""
        # Workshop area
        workshop_x = self.room_x + 4 * TILE_SIZE
        workshop_y = self.room_y + 4 * TILE_SIZE
        pygame.draw.rect(screen, (150, 150, 200), 
                        (workshop_x, workshop_y, 5 * TILE_SIZE, 5 * TILE_SIZE), 2)
        
        # Application desk area
        desk_x = self.room_x + 16 * TILE_SIZE
        desk_y = self.room_y + 6 * TILE_SIZE
        pygame.draw.rect(screen, (200, 150, 150), 
                        (desk_x, desk_y, 4 * TILE_SIZE, 4 * TILE_SIZE), 2)
        
    def draw_npcs(self, screen):
        """Draw the NPCs"""
        # Draw workshop instructor
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            instructor_x = self.room_x + self.workshop_instructor['x'] * TILE_SIZE
            instructor_y = self.room_y + self.workshop_instructor['y'] * TILE_SIZE
            self.game.player.draw_at_position(screen, instructor_x, instructor_y, self.workshop_instructor['facing'])
            
            desk_x = self.room_x + self.application_desk['x'] * TILE_SIZE
            desk_y = self.room_y + self.application_desk['y'] * TILE_SIZE
            self.game.player.draw_at_position(screen, desk_x, desk_y, self.application_desk['facing'])
        else:
            # Fallback to circles
            instructor_pixel_x = self.room_x + self.workshop_instructor['x'] * TILE_SIZE + TILE_SIZE // 2
            instructor_pixel_y = self.room_y + self.workshop_instructor['y'] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, (0, 150, 100), (int(instructor_pixel_x), int(instructor_pixel_y)), TILE_SIZE // 3)
            
            desk_pixel_x = self.room_x + self.application_desk['x'] * TILE_SIZE + TILE_SIZE // 2
            desk_pixel_y = self.room_y + self.application_desk['y'] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, (100, 0, 150), (int(desk_pixel_x), int(desk_pixel_y)), TILE_SIZE // 3)
            
    def draw_custom_ui(self, screen):
        """Draw community center specific UI elements"""
        # Instructions
        font = pygame.font.Font(None, 24)
        
        instruction_text = None
        if self.is_near_workshop_instructor() and not self.workshop_complete:
            instruction_text = "Press SPACE to attend Life Skills Workshop"
        elif self.is_near_application_desk() and not self.application_submitted:
            instruction_text = "Press SPACE to submit TLP Application"
            
        if instruction_text:
            text = font.render(instruction_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
            
        # Room name
        title = font.render("Community Center", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (0, 0, 0), title_rect.inflate(20, 10))
        screen.blit(title, title_rect)
        
        # Show completed activities
        status_y = 60
        if self.workshop_complete:
            status = font.render("✓ Life Skills Workshop Complete", True, (0, 255, 0))
            status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, status_y))
            screen.blit(status, status_rect)
            status_y += 30
            
        if self.application_submitted:
            status = font.render("✓ TLP Application Submitted", True, (0, 255, 0))
            status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, status_y))
            screen.blit(status, status_rect)
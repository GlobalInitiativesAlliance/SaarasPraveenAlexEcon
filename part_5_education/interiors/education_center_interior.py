import pygame
from shared.constants import *
from shared.base_interior import BaseInterior

class EducationCenterInterior(BaseInterior):
    """Adult education center for GED classes"""
    def __init__(self, game, room_name="education_center"):
        super().__init__(game, room_name)
        self.showed_schedule = False
        
    def handle_event(self, event):
        """Handle events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            current_obj = self.game.objective_manager.get_current_objective()
            
            if current_obj and current_obj.id == "ged_center":
                self.message = "Welcome to Adult Education. How can we help?"
                self.message_timer = 3.0
                self.game.objective_manager.complete_current_objective()
                
            elif current_obj and current_obj.id == "class_schedule":
                if not self.showed_schedule:
                    self.showed_schedule = True
                    self.message = "GED Classes: Monday-Friday 9AM-12PM"
                    self.message2 = "But you work those exact hours..."
                    self.message_timer = 4.0
                else:
                    self.game.objective_manager.complete_current_objective()
                    
    def draw(self, screen):
        """Draw the education center"""
        super().draw(screen)
        
        # Draw classroom setting
        desk_color = (139, 90, 43)
        for i in range(3):
            for j in range(3):
                x = self.room_x + 100 + j * 100
                y = self.room_y + 100 + i * 80
                pygame.draw.rect(screen, desk_color, (x, y, 60, 40))
                
        # Draw whiteboard
        board_rect = pygame.Rect(self.room_x + 50, self.room_y + 50, 300, 150)
        pygame.draw.rect(screen, (255, 255, 255), board_rect)
        pygame.draw.rect(screen, (50, 50, 50), board_rect, 3)
        
        if self.showed_schedule:
            schedule_font = pygame.font.Font(None, 20)
            schedule_text = "CLASS TIMES: 9AM-12PM M-F"
            text_surf = schedule_font.render(schedule_text, True, (0, 0, 0))
            screen.blit(text_surf, (board_rect.x + 20, board_rect.y + 20))
        
        # Draw messages
        if hasattr(self, 'message') and self.message_timer > 0:
            self.message_timer -= 1/60
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 150))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 5)
            screen.blit(msg_surf, msg_rect)
            
        if hasattr(self, 'message2') and self.showed_schedule:
            msg2_surf = self.small_font.render(self.message2, True, (255, 150, 150))
            msg2_rect = msg2_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
            screen.blit(msg2_surf, msg2_rect)
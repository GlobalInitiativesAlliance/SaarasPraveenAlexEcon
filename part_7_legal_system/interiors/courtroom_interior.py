import pygame
from shared.constants import *
from shared.base_interior import BaseInterior

class CourtroomInterior(BaseInterior):
    """Courtroom interior for legal proceedings"""
    def __init__(self, game, room_name="courtroom"):
        super().__init__(game, room_name)
        self.showed_warrant = False
        
    def handle_event(self, event):
        """Handle events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            current_obj = self.game.objective_manager.get_current_objective()
            
            if current_obj and current_obj.id == "court_date":
                self.message = "Court Date: Tuesday 9:00 AM (Same time as your shift)"
                self.message_timer = 4.0
                self.game.objective_manager.complete_current_objective()
                
            elif current_obj and current_obj.id == "miss_court":
                if not self.showed_warrant:
                    self.showed_warrant = True
                    self.message = "BENCH WARRANT ISSUED FOR FAILURE TO APPEAR"
                    self.message2 = "You're now wanted by police"
                    self.message_timer = 5.0
                else:
                    self.game.objective_manager.complete_current_objective()
                    self.exit()
                    
    def draw(self, screen):
        """Draw the courtroom"""
        super().draw(screen)
        
        # Draw judge's bench
        bench_rect = pygame.Rect(self.room_x + 100, self.room_y + 50, 300, 100)
        pygame.draw.rect(screen, (100, 50, 0), bench_rect)
        pygame.draw.rect(screen, (50, 25, 0), bench_rect, 3)
        
        # Draw defendant table
        table_rect = pygame.Rect(self.room_x + 150, self.room_y + 250, 200, 80)
        pygame.draw.rect(screen, (139, 90, 43), table_rect)
        
        # Draw legal text
        if self.showed_warrant:
            warrant_font = pygame.font.Font(None, 28)
            warrant_text = "WARRANT STATUS: ACTIVE"
            text_surf = warrant_font.render(warrant_text, True, (255, 50, 50))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 100))
            screen.blit(text_surf, text_rect)
        
        # Draw messages
        if hasattr(self, 'message') and self.message_timer > 0:
            self.message_timer -= 1/60
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 150))
            bg_rect = msg_rect.inflate(20, 10)
            color = (100, 20, 20) if "WARRANT" in self.message else (40, 40, 50)
            pygame.draw.rect(screen, color, bg_rect, 0, 5)
            screen.blit(msg_surf, msg_rect)
            
        if hasattr(self, 'message2') and self.showed_warrant:
            msg2_surf = self.small_font.render(self.message2, True, (255, 150, 150))
            msg2_rect = msg2_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
            screen.blit(msg2_surf, msg2_rect)
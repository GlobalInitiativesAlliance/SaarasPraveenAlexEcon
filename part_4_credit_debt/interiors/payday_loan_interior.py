import pygame
from shared.constants import *
from shared.base_interior import BaseInterior

class PaydayLoanInterior(BaseInterior):
    """Payday loan store interior"""
    def __init__(self, game, room_name="payday_loan"):
        super().__init__(game, room_name)
        self.showed_terms = False
        self.loan_amount = 500
        self.payback_amount = 650
        
    def handle_event(self, event):
        """Handle events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            current_obj = self.game.objective_manager.get_current_objective()
            
            if current_obj and current_obj.id == "payday_loan_store":
                self.message = "Welcome to QuickCash! Need money fast?"
                self.message_timer = 3.0
                self.game.objective_manager.complete_current_objective()
                
            elif current_obj and current_obj.id == "loan_terms":
                if not self.showed_terms:
                    self.showed_terms = True
                    self.message = f"Loan Terms: Borrow ${self.loan_amount}, Pay back ${self.payback_amount} in 14 days"
                    self.message2 = "That's only 30% interest! (Actually 390% APR)"
                    self.message_timer = 5.0
                else:
                    self.game.objective_manager.complete_current_objective()
                    self.exit()
    
    def draw(self, screen):
        """Draw the interior"""
        super().draw(screen)
        
        # Draw predatory signs
        sign_font = pygame.font.Font(None, 36)
        sign_text = "FAST CASH! NO CREDIT CHECK!"
        sign_surf = sign_font.render(sign_text, True, (255, 255, 0))
        screen.blit(sign_surf, (SCREEN_WIDTH//2 - 200, 100))
        
        # Draw messages
        if hasattr(self, 'message') and self.message_timer > 0:
            self.message_timer -= 1/60
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 150))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (100, 20, 20), bg_rect, 0, 5)
            screen.blit(msg_surf, msg_rect)
            
        if hasattr(self, 'message2') and self.showed_terms:
            msg2_surf = self.small_font.render(self.message2, True, (255, 150, 150))
            msg2_rect = msg2_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
            screen.blit(msg2_surf, msg2_rect)
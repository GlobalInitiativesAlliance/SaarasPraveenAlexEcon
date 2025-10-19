import pygame
from shared.constants import *
from shared.base_interior import BaseInterior

class HospitalInterior(BaseInterior):
    """Hospital/ER interior for emergency healthcare"""
    def __init__(self, game, room_name="hospital"):
        super().__init__(game, room_name)
        
        # Hospital-specific properties
        self.in_er = False
        self.treatment_complete = False
        self.bill_amount = 3500.00
        self.showed_bill = False
        
    def enter(self):
        """Enter the hospital"""
        super().enter()
        print("Entered hospital emergency room")
        
        # Check if it's an emergency visit
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == "emergency_room":
            self.message = "Triage nurse: 'You look terrible. We'll get you in right away.'"
            self.message_timer = 3.0
            
    def handle_event(self, event):
        """Handle pygame events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                current_obj = self.game.objective_manager.get_current_objective()
                
                if current_obj and current_obj.id == "emergency_room":
                    self.in_er = True
                    self.game.objective_manager.complete_current_objective()
                    
                elif current_obj and current_obj.id == "er_treatment":
                    if not self.treatment_complete:
                        self.treatment_complete = True
                        self.message = "Doctor: 'We've given you IV antibiotics. You should feel better soon.'"
                        self.message_timer = 4.0
                    else:
                        self.game.objective_manager.complete_current_objective()
                        
                elif current_obj and current_obj.id == "hospital_bill":
                    if not self.showed_bill:
                        self.showed_bill = True
                        self.message = f"EMERGENCY ROOM BILL: ${self.bill_amount:.2f}"
                        self.message_timer = 5.0
                        self.message2 = "Payment due in 30 days or will be sent to collections"
                        self.message2_timer = 5.0
                    else:
                        self.game.objective_manager.complete_current_objective()
                        self.exit()
                        
    def draw(self, screen):
        """Draw the hospital interior"""
        super().draw(screen)
        
        # Draw ER sign
        if self.in_er:
            er_text = "EMERGENCY ROOM"
            er_surf = pygame.font.Font(None, 36).render(er_text, True, (255, 50, 50))
            er_rect = er_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(er_surf, er_rect)
            
        # Draw hospital bed if in treatment
        if self.treatment_complete:
            bed_rect = pygame.Rect(self.room_x + 150, self.room_y + 150, 200, 100)
            pygame.draw.rect(screen, (200, 200, 200), bed_rect)
            pygame.draw.rect(screen, (100, 100, 100), bed_rect, 3)
            
        # Draw messages
        if hasattr(self, 'message') and hasattr(self, 'message_timer') and self.message_timer > 0:
            self.message_timer -= 1/60
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
            bg_rect = msg_rect.inflate(20, 10)
            if "BILL" in self.message:
                pygame.draw.rect(screen, (100, 20, 20), bg_rect, 0, 5)
            else:
                pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 5)
            screen.blit(msg_surf, msg_rect)
            
        if hasattr(self, 'message2') and hasattr(self, 'message2_timer') and self.message2_timer > 0:
            self.message2_timer -= 1/60
            msg_surf = self.small_font.render(self.message2, True, (255, 150, 150))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            screen.blit(msg_surf, msg_rect)
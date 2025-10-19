import pygame
from shared.constants import *
from shared.base_interior import BaseInterior

class PharmacyInterior(BaseInterior):
    """Pharmacy interior for medication objectives"""
    def __init__(self, game, room_name="pharmacy"):
        super().__init__(game, room_name)
        
        # Pharmacy-specific properties
        self.medication_price = 85.00
        self.has_insurance = False
        self.showed_price = False
        
    def enter(self):
        """Enter the pharmacy"""
        super().enter()
        print("Entered pharmacy")
        
    def handle_event(self, event):
        """Handle pygame events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                current_obj = self.game.objective_manager.get_current_objective()
                
                if current_obj and current_obj.id == "pharmacy_prices":
                    if not self.showed_price:
                        # Show medication price
                        self.showed_price = True
                        self.message = f"Pharmacist: 'That'll be ${self.medication_price:.2f} without insurance.'"
                        self.message_timer = 4.0
                        
                        # Check player money
                        if hasattr(self.game.objective_manager, 'player_money'):
                            if self.game.objective_manager.player_money < self.medication_price:
                                self.can_afford = False
                                self.message2 = "You can't afford this medication..."
                                self.message2_timer = 4.0
                    else:
                        # Complete objective
                        self.game.objective_manager.complete_current_objective()
                        self.exit()
                        
    def draw(self, screen):
        """Draw the pharmacy interior"""
        super().draw(screen)
        
        # Draw pharmacy counter
        counter_rect = pygame.Rect(self.room_x + 100, self.room_y + 200, 300, 80)
        pygame.draw.rect(screen, (139, 90, 43), counter_rect)
        pygame.draw.rect(screen, (100, 60, 30), counter_rect, 3)
        
        # Draw price sign
        if self.showed_price:
            price_text = f"Antibiotics: ${self.medication_price}"
            price_surf = self.font.render(price_text, True, (255, 50, 50))
            screen.blit(price_surf, (self.room_x + 150, self.room_y + 150))
        
        # Draw messages
        if hasattr(self, 'message') and hasattr(self, 'message_timer') and self.message_timer > 0:
            self.message_timer -= 1/60
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 5)
            screen.blit(msg_surf, msg_rect)
            
        if hasattr(self, 'message2') and hasattr(self, 'message2_timer') and self.message2_timer > 0:
            self.message2_timer -= 1/60
            msg_surf = self.small_font.render(self.message2, True, (255, 150, 150))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            screen.blit(msg_surf, msg_rect)
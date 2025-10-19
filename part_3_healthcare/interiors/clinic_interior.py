import pygame
import math
from shared.constants import *
from shared.base_interior import BaseInterior

class ClinicInterior(BaseInterior):
    """Community health clinic interior"""
    def __init__(self, game, room_name="clinic"):
        super().__init__(game, room_name)
        
        # Clinic-specific properties
        self.waiting_time = 0
        self.is_waiting = False
        self.seen_doctor = False
        
    def enter(self):
        """Enter the clinic"""
        super().enter()
        print("Entered community health clinic")
        
        # Check current objective
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == "visit_clinic":
            # Start the clinic visit
            self.show_clinic_message()
            
    def show_clinic_message(self):
        """Show initial clinic message"""
        self.message = "The waiting room is packed. This might take a while..."
        self.message_timer = 3.0
        
    def handle_event(self, event):
        """Handle pygame events"""
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                current_obj = self.game.objective_manager.get_current_objective()
                
                if current_obj and current_obj.id == "visit_clinic":
                    self.game.objective_manager.complete_current_objective()
                elif current_obj and current_obj.id == "long_wait":
                    # Start waiting sequence
                    self.is_waiting = True
                    self.waiting_time = 0
                elif current_obj and current_obj.id == "see_doctor":
                    # Doctor consultation
                    self.seen_doctor = True
                    self.message = "Doctor: 'You need antibiotics. We don't have any here, try the pharmacy.'"
                    self.message_timer = 4.0
                    self.game.objective_manager.complete_current_objective()
                    
    def update(self, dt):
        """Update clinic state"""
        super().update(dt)
        
        # Handle waiting room timer
        if self.is_waiting:
            self.waiting_time += dt
            if self.waiting_time > 3.0:  # 3 seconds for demo (would be longer in real game)
                self.is_waiting = False
                self.message = "Finally! A nurse calls your name."
                self.message_timer = 3.0
                self.game.objective_manager.complete_current_objective()
                
    def draw(self, screen):
        """Draw the clinic interior"""
        super().draw(screen)
        
        # Draw waiting room status
        if self.is_waiting:
            wait_text = f"Waiting... ({int(self.waiting_time)}s)"
            wait_surf = self.font.render(wait_text, True, (255, 200, 100))
            screen.blit(wait_surf, (SCREEN_WIDTH // 2 - 100, 100))
            
        # Draw any messages
        if hasattr(self, 'message') and hasattr(self, 'message_timer') and self.message_timer > 0:
            self.message_timer -= 1/60  # Rough dt
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            # Draw background for message
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 5)
            pygame.draw.rect(screen, (100, 100, 120), bg_rect, 2, 5)
            screen.blit(msg_surf, msg_rect)
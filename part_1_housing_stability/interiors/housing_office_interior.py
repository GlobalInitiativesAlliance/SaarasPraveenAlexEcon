"""Housing Office Interior - Where players make housing choices"""

import pygame
from shared.constants import *
from shared.base_interior import BaseInterior
from part_1_housing_stability.activities.housing_menu import HousingMenuActivity

class HousingOfficeInterior(BaseInterior):
    """Housing assistance office where players access the menu"""
    
    def __init__(self, game, room_name="housing_office"):
        super().__init__(game, room_name)
        self.housing_menu = HousingMenuActivity(game.objective_manager)
        self.showed_intro = False
        
    def handle_event(self, event):
        """Handle events"""
        # If housing menu is active, pass events to it
        if self.housing_menu.active:
            if event.type == pygame.KEYDOWN:
                self.housing_menu.handle_key(event.key)
            return
            
        super().handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            current_obj = self.game.objective_manager.get_current_objective()
            
            if current_obj and current_obj.id == "housing_intro":
                if not self.showed_intro:
                    self.showed_intro = True
                    self.message = "Welcome to Housing Assistance. We'll try to help..."
                    self.message2 = "But honestly, the options aren't great."
                    self.message_timer = 4.0
                else:
                    self.game.objective_manager.complete_current_objective()
                    
            elif current_obj and current_obj.id == "housing_menu":
                # Open the housing menu
                self.housing_menu.start()
                
    def update(self, dt):
        """Update the interior"""
        super().update(dt)
        
        # Don't update player if menu is active
        if self.housing_menu.active:
            return
            
    def draw(self, screen):
        """Draw the interior"""
        super().draw(screen)
        
        # Draw office furniture
        desk_rect = pygame.Rect(self.room_x + 150, self.room_y + 200, 200, 100)
        pygame.draw.rect(screen, (100, 60, 40), desk_rect)
        pygame.draw.rect(screen, (60, 40, 30), desk_rect, 3)
        
        # Draw posters on wall
        poster1 = pygame.Rect(self.room_x + 50, self.room_y + 50, 80, 100)
        pygame.draw.rect(screen, (200, 200, 150), poster1)
        pygame.draw.rect(screen, (100, 100, 80), poster1, 2)
        
        # Draw "Housing Resources" text on poster
        poster_font = pygame.font.Font(None, 16)
        text_lines = ["HOUSING", "RESOURCES", "AVAILABLE"]
        for i, line in enumerate(text_lines):
            text_surf = poster_font.render(line, True, (50, 50, 50))
            text_rect = text_surf.get_rect(center=(poster1.centerx, poster1.y + 20 + i * 20))
            screen.blit(text_surf, text_rect)
        
        # Draw filing cabinets
        cabinet1 = pygame.Rect(self.room_x + 400, self.room_y + 100, 60, 120)
        cabinet2 = pygame.Rect(self.room_x + 400, self.room_y + 230, 60, 120)
        for cabinet in [cabinet1, cabinet2]:
            pygame.draw.rect(screen, (80, 80, 90), cabinet)
            pygame.draw.rect(screen, (50, 50, 60), cabinet, 2)
            # Draw handles
            for j in range(3):
                handle_y = cabinet.y + 20 + j * 35
                pygame.draw.rect(screen, (150, 150, 160), 
                               (cabinet.x + 20, handle_y, 20, 5))
        
        # Draw motivational poster (ironic)
        poster2 = pygame.Rect(self.room_x + 250, self.room_y + 50, 100, 60)
        pygame.draw.rect(screen, (180, 200, 220), poster2)
        pygame.draw.rect(screen, (100, 120, 140), poster2, 2)
        text_surf = poster_font.render("BELIEVE IN", True, (50, 50, 70))
        screen.blit(text_surf, (poster2.x + 15, poster2.y + 15))
        text_surf = poster_font.render("YOURSELF", True, (50, 50, 70))
        screen.blit(text_surf, (poster2.x + 20, poster2.y + 35))
        
        # Draw waiting room chairs
        for i in range(3):
            chair_x = self.room_x + 80 + i * 80
            chair_y = self.room_y + 300
            pygame.draw.rect(screen, (60, 60, 70), 
                           (chair_x, chair_y, 50, 50))
            pygame.draw.rect(screen, (40, 40, 50), 
                           (chair_x, chair_y, 50, 50), 2)
        
        # Draw the housing menu if active
        if self.housing_menu.active:
            self.housing_menu.draw(screen)
        
        # Draw any messages
        if hasattr(self, 'message') and self.message_timer > 0:
            self.message_timer -= 1/60
            # Draw background box for message
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 5)
            screen.blit(msg_surf, msg_rect)
            
        if hasattr(self, 'message2') and self.message_timer > 0:
            msg2_surf = self.small_font.render(self.message2, True, (200, 200, 200))
            msg2_rect = msg2_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
            screen.blit(msg2_surf, msg2_rect)
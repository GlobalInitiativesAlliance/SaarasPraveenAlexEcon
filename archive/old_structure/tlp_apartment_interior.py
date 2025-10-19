import pygame
import math
import json
from constants import *
from home_interior import HomeInterior

class TLPApartmentInterior(HomeInterior):
    """TLP (Transitional Living Program) apartment interior"""
    def __init__(self, game, room_name="tlp_apartment"):
        # Initialize parent class
        super().__init__(game, room_name)
        
        # Override room dimensions
        self.room_width = 18
        self.room_height = 14
        
        # Override player start position
        self.player_x = 9
        self.player_y = 12
        
        # Apartment state
        self.items_packed = False
        self.agreement_signed = False
        self.roommate_present = True
        self.roommate_crisis = False
        
        # Roommate NPC
        self.roommate = {
            'x': 14,
            'y': 6,
            'facing': 'left',
            'name': 'Alex',
            'visible': True
        }
        
        # Furniture and interaction points (override parent's bed position)
        self.bed_position = (3, 4)  # Player's bed
        self.bed_width = 2
        self.bed_height = 2
        self.desk_pos = (7, 3)
        self.roommate_bed_pos = (14, 4)
        self.kitchen_pos = (12, 10)
        
    def enter(self):
        """Enter the apartment"""
        super().enter()  # Call parent's enter method
        self.player_x = 9
        self.player_y = 12
        self.player_facing = "up"
        
        # Check current objective to set appropriate state
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj:
            if "Roommate Gone" in current_obj.description:
                self.roommate_crisis = True
                self.roommate['visible'] = False
            elif "Meet Your Roommate" in current_obj.description:
                self.roommate['visible'] = True
                self.roommate_crisis = False
                
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_SPACE:
                # Check interactions based on position
                self.check_interactions()
            else:
                # Let parent handle movement
                super().handle_event(event)
                    
    def check_interactions(self):
        """Check for interactions based on player position"""
        current_obj = self.game.objective_manager.get_current_objective()
        if not current_obj:
            return
            
        # Near bed - pack items
        if self.is_near_position(self.bed_position) and "Pack" in current_obj.description:
            if not self.items_packed:
                # Launch the packing mini-game
                if hasattr(self.game.objective_manager, 'packing'):
                    packing_activity = self.game.objective_manager.packing
                    packing_activity.apartment_ref = self  # Pass reference to apartment
                    self.game.objective_manager.current_activity = packing_activity
                    packing_activity.start()
                    # The activity will handle completion
                else:
                    # Fallback if packing activity not available
                    self.items_packed = True
                    self.game.objective_manager.show_notification("Items packed! Ready to move.")
                    self.game.objective_manager.complete_current_objective()
                
        # Near desk - sign agreement
        elif self.is_near_position(self.desk_pos) and "Living Agreement" in current_obj.description:
            if not self.agreement_signed:
                self.agreement_signed = True
                self.game.objective_manager.show_notification("Living agreement signed!")
                self.game.objective_manager.complete_current_objective()
                
        # Near roommate - meet them
        elif self.is_near_roommate() and "Meet Your Roommate" in current_obj.description:
            self.game.objective_manager.show_notification("You met Alex, your new roommate!")
            self.game.objective_manager.complete_current_objective()
            
        # Near roommate bed during crisis
        elif self.is_near_position(self.roommate_bed_pos) and self.roommate_crisis:
            if "Emergency" in current_obj.description:
                self.game.objective_manager.show_notification("Alex's things are gone! You need to find help.")
                self.game.objective_manager.complete_current_objective()
                
        # Rest for tomorrow
        elif self.is_near_position(self.bed_position) and "Rest for Tomorrow" in current_obj.description:
            self.game.objective_manager.show_notification("You rest for the night...")
            self.game.objective_manager.complete_current_objective()
            
    def is_near_position(self, pos):
        """Check if player is near a specific position"""
        dx = abs(self.player_x - pos[0])
        dy = abs(self.player_y - pos[1])
        return dx <= 1 and dy <= 1
        
    def is_near_roommate(self):
        """Check if player is near the roommate"""
        if not self.roommate['visible']:
            return False
        dx = abs(self.player_x - self.roommate['x'])
        dy = abs(self.player_y - self.roommate['y'])
        return dx <= 2 and dy <= 2
                    
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        # Check furniture positions
        furniture_positions = [self.desk_pos, self.roommate_bed_pos, self.kitchen_pos]
        for pos in furniture_positions:
            if x == pos[0] and y == pos[1]:
                return False
                
        # Check roommate position
        if self.roommate['visible'] and x == self.roommate['x'] and y == self.roommate['y']:
            return False
            
        # Let parent handle the rest (including player's bed)
        return super().is_walkable(x, y)
                    
    def draw(self, screen):
        """Draw the apartment"""
        if not self.active:
            return
            
        # Let parent draw the room tiles
        super().draw(screen)
        
        # Draw additional furniture markers
        self.draw_furniture(screen)
        
        # Draw roommate if visible
        if self.roommate['visible']:
            self.draw_roommate(screen)
        
        # Draw custom UI
        self.draw_custom_ui(screen)
        
    def draw_furniture(self, screen):
        """Draw furniture overlays"""
        # Desk marker
        desk_x = self.room_x + self.desk_pos[0] * TILE_SIZE
        desk_y = self.room_y + self.desk_pos[1] * TILE_SIZE
        pygame.draw.rect(screen, (101, 67, 33), 
                        (desk_x, desk_y, TILE_SIZE, TILE_SIZE), 2)
        
        # Roommate's bed marker
        rbed_x = self.room_x + self.roommate_bed_pos[0] * TILE_SIZE
        rbed_y = self.room_y + self.roommate_bed_pos[1] * TILE_SIZE
        if self.roommate['visible']:
            pygame.draw.rect(screen, (139, 69, 19), 
                            (rbed_x, rbed_y, TILE_SIZE * 2, TILE_SIZE * 2), 2)
        else:
            # Empty space during crisis
            pygame.draw.rect(screen, (200, 100, 100), 
                            (rbed_x, rbed_y, TILE_SIZE * 2, TILE_SIZE * 2), 3)
        
        # Kitchen area marker
        kitchen_x = self.room_x + self.kitchen_pos[0] * TILE_SIZE
        kitchen_y = self.room_y + self.kitchen_pos[1] * TILE_SIZE
        pygame.draw.rect(screen, (180, 180, 200), 
                        (kitchen_x, kitchen_y, TILE_SIZE * 2, TILE_SIZE), 2)
        
    def draw_roommate(self, screen):
        """Draw the roommate NPC"""
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
            roommate_x = self.room_x + self.roommate['x'] * TILE_SIZE
            roommate_y = self.room_y + self.roommate['y'] * TILE_SIZE
            self.game.player.draw_at_position(screen, roommate_x, roommate_y, self.roommate['facing'])
        else:
            # Fallback to circle
            pixel_x = self.room_x + self.roommate['x'] * TILE_SIZE + TILE_SIZE // 2
            pixel_y = self.room_y + self.roommate['y'] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, (0, 100, 200), (int(pixel_x), int(pixel_y)), TILE_SIZE // 3)
            
    def draw_custom_ui(self, screen):
        """Draw apartment specific UI elements"""
        # Instructions
        font = pygame.font.Font(None, 24)
        
        current_obj = self.game.objective_manager.get_current_objective()
        instruction_text = None
        
        if current_obj:
            if self.is_near_position(self.bed_position) and "Pack" in current_obj.description:
                instruction_text = "Press SPACE to pack your items"
            elif self.is_near_position(self.desk_pos) and "Living Agreement" in current_obj.description:
                instruction_text = "Press SPACE to sign the living agreement"
            elif self.is_near_roommate() and "Meet Your Roommate" in current_obj.description:
                instruction_text = "Press SPACE to meet your roommate"
            elif self.is_near_position(self.roommate_bed_pos) and self.roommate_crisis:
                instruction_text = "Press SPACE to investigate"
            elif self.is_near_position(self.bed_position) and "Rest for Tomorrow" in current_obj.description:
                instruction_text = "Press SPACE to rest"
                
        if instruction_text:
            text = font.render(instruction_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
            
        # Room name
        title = font.render("TLP Apartment", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (0, 0, 0), title_rect.inflate(20, 10))
        screen.blit(title, title_rect)
        
        # Show apartment status
        if self.roommate_crisis:
            crisis_text = font.render("! ROOMMATE MISSING !", True, (255, 0, 0))
            crisis_rect = crisis_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
            screen.blit(crisis_text, crisis_rect)
import pygame
import math
import json
from constants import *
from home_interior import HomeInterior

class HousingOfficeInterior(HomeInterior):
    """Housing office interior for emergency assistance"""
    def __init__(self, game, room_name="housing_office"):
        # Initialize parent class
        super().__init__(game, room_name)
        
        # Override room dimensions
        self.room_width = 16
        self.room_height = 12
        
        # Override player start position
        self.player_x = 8
        self.player_y = 10
        
        # Office state
        self.assistance_received = False
        
        # Office workers
        self.workers = [
            {
                'x': 4,
                'y': 3,
                'facing': 'down',
                'name': 'Ms. Chen',
                'desk': (4, 4)
            },
            {
                'x': 8,
                'y': 3,
                'facing': 'down',
                'name': 'Mr. Davis',
                'desk': (8, 4)
            },
            {
                'x': 12,
                'y': 3,
                'facing': 'down',
                'name': 'Ms. Williams',
                'desk': (12, 4)
            }
        ]
        
        # Waiting area
        self.waiting_chairs = [(2, 7), (3, 7), (13, 7), (14, 7)]
        
    def enter(self):
        """Enter the housing office"""
        super().enter()  # Call parent's enter method
        self.player_x = 8
        self.player_y = 10
        self.player_facing = "up"
            
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit()
            elif event.key == pygame.K_SPACE:
                # Check if near any worker
                for worker in self.workers:
                    if self.is_near_worker(worker) and not self.assistance_received:
                        self.get_assistance(worker)
                        break
            else:
                # Let parent handle movement
                super().handle_event(event)
                    
    def is_near_worker(self, worker):
        """Check if player is near a specific worker"""
        dx = abs(self.player_x - worker['x'])
        dy = abs(self.player_y - worker['y'])
        return dx <= 2 and dy <= 2
        
    def get_assistance(self, worker):
        """Get assistance from a worker"""
        self.assistance_received = True
        self.game.objective_manager.show_notification(f"{worker['name']}: We'll help you find emergency housing. Don't worry!")
        
        # Update game objective if needed
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and ("Housing" in current_obj.description or "Emergency" in current_obj.description):
            self.game.objective_manager.complete_current_objective()
                    
    def is_walkable(self, x, y):
        """Check if a tile is walkable"""
        # Check worker positions and desks
        for worker in self.workers:
            if (x == worker['x'] and y == worker['y']) or \
               (x == worker['desk'][0] and y == worker['desk'][1]):
                return False
                
        # Check waiting chairs
        for chair in self.waiting_chairs:
            if x == chair[0] and y == chair[1]:
                return False
            
        # Let parent handle the rest
        return super().is_walkable(x, y)
                    
    def draw(self, screen):
        """Draw the housing office"""
        if not self.active:
            return
            
        # Let parent draw the room tiles
        super().draw(screen)
        
        # Draw office furniture
        self.draw_office_furniture(screen)
        
        # Draw workers
        self.draw_workers(screen)
        
        # Draw custom UI
        self.draw_custom_ui(screen)
        
    def draw_office_furniture(self, screen):
        """Draw desks and chairs"""
        # Draw desks
        for worker in self.workers:
            desk_x = self.room_x + worker['desk'][0] * TILE_SIZE
            desk_y = self.room_y + worker['desk'][1] * TILE_SIZE
            pygame.draw.rect(screen, (139, 90, 43), 
                           (desk_x, desk_y, TILE_SIZE, TILE_SIZE), 2)
        
        # Draw waiting chairs
        for chair in self.waiting_chairs:
            chair_x = self.room_x + chair[0] * TILE_SIZE
            chair_y = self.room_y + chair[1] * TILE_SIZE
            pygame.draw.rect(screen, (100, 100, 150), 
                           (chair_x, chair_y, TILE_SIZE, TILE_SIZE), 2)
        
    def draw_workers(self, screen):
        """Draw the office workers"""
        for worker in self.workers:
            if hasattr(self.game, 'player') and hasattr(self.game.player, 'draw_at_position'):
                worker_x = self.room_x + worker['x'] * TILE_SIZE
                worker_y = self.room_y + worker['y'] * TILE_SIZE
                self.game.player.draw_at_position(screen, worker_x, worker_y, worker['facing'])
            else:
                # Fallback to circle
                pixel_x = self.room_x + worker['x'] * TILE_SIZE + TILE_SIZE // 2
                pixel_y = self.room_y + worker['y'] * TILE_SIZE + TILE_SIZE // 2
                pygame.draw.circle(screen, (0, 100, 150), (int(pixel_x), int(pixel_y)), TILE_SIZE // 3)
            
    def draw_custom_ui(self, screen):
        """Draw housing office specific UI elements"""
        # Instructions
        font = pygame.font.Font(None, 24)
        
        instruction_text = None
        if any(self.is_near_worker(w) for w in self.workers) and not self.assistance_received:
            instruction_text = "Press SPACE to ask for emergency housing assistance"
            
        if instruction_text:
            text = font.render(instruction_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 10))
            screen.blit(text, text_rect)
            
        # Room name
        title = font.render("Housing Assistance Office", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (0, 0, 0), title_rect.inflate(20, 10))
        screen.blit(title, title_rect)
        
        # Show assistance status
        if self.assistance_received:
            status = font.render("✓ Emergency assistance arranged", True, (0, 255, 0))
            status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, 60))
            screen.blit(status, status_rect)
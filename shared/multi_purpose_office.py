"""Multi-Purpose Office Interior - Can be housing office, courthouse, shelter, etc."""

import pygame
from shared.enhanced_interior import TaskEnabledInterior
from shared.constants import *

class MultiPurposeOffice(TaskEnabledInterior):
    """Office that transforms based on current objective"""
    
    def __init__(self, game, room_name="multi_office"):
        super().__init__(game, room_name, interior_type='office')
        
        # Office can serve many purposes
        self.current_purpose = 'generic'
        self.purpose_decorations = {}
        
        # NPC positions for different purposes
        self.npcs = {}
        
    def enter(self):
        """Enter and configure based on current objective"""
        super().enter()
        self.detect_purpose()
        self.setup_purpose_specific()
        
    def detect_purpose(self):
        """Detect what this office is being used for"""
        if not hasattr(self.game, 'objective_manager'):
            return
            
        obj = self.game.objective_manager.get_current_objective()
        if not obj:
            return
            
        # Map objectives to office purposes
        if 'housing' in obj.id or 'tlp' in obj.id:
            self.current_purpose = 'housing_office'
        elif 'court' in obj.id or 'legal' in obj.id:
            self.current_purpose = 'courtroom'
        elif 'shelter' in obj.id:
            self.current_purpose = 'shelter'
        elif 'food_bank' in obj.id:
            self.current_purpose = 'food_bank'
        elif 'benefits' in obj.id or 'snap' in obj.id:
            self.current_purpose = 'benefits_office'
        elif 'defender' in obj.id:
            self.current_purpose = 'legal_aid'
        else:
            self.current_purpose = 'generic'
            
    def setup_purpose_specific(self):
        """Set up room based on current purpose"""
        self.npcs = {}
        self.purpose_decorations = {}
        
        if self.current_purpose == 'housing_office':
            self.npcs['caseworker'] = {
                'pos': (8, 4),
                'name': 'Housing Specialist',
                'dialogue': [
                    "Let me check what's available...",
                    "The waitlist is currently 6-8 months.",
                    "You'll need proof of income and ID."
                ]
            }
            self.purpose_decorations = {
                'posters': [(2, 2), (14, 2)],  # Housing resource posters
                'filing_cabinets': [(12, 3), (12, 4)],
                'waiting_chairs': [(5, 8), (7, 8), (9, 8)]
            }
            
        elif self.current_purpose == 'courtroom':
            self.npcs['judge'] = {
                'pos': (8, 2),
                'name': 'Judge',
                'dialogue': ["Order in the court!", "State your case."]
            }
            self.npcs['prosecutor'] = {
                'pos': (10, 5),
                'name': 'Prosecutor',
                'dialogue': ["The state seeks maximum penalty."]
            }
            self.purpose_decorations = {
                'judge_bench': (8, 2),
                'defendant_table': (6, 6),
                'gallery_seats': [(4, 8), (6, 8), (10, 8), (12, 8)]
            }
            
        elif self.current_purpose == 'shelter':
            self.npcs['shelter_staff'] = {
                'pos': (8, 8),
                'name': 'Night Staff',
                'dialogue': [
                    "Lights out at 10 PM.",
                    "No drugs, no weapons, no guests.",
                    "You must be out by 6 AM."
                ]
            }
            self.purpose_decorations = {
                'cots': [(4, 4), (7, 4), (10, 4), (4, 7), (7, 7), (10, 7)],
                'belongings_area': (2, 10),
                'bathroom_sign': (14, 2)
            }
            
        elif self.current_purpose == 'food_bank':
            self.npcs['volunteer'] = {
                'pos': (8, 6),
                'name': 'Volunteer',
                'dialogue': [
                    "Take one bag per family.",
                    "We have bread and canned goods today.",
                    "Next distribution is Thursday."
                ]
            }
            self.purpose_decorations = {
                'food_tables': [(4, 5), (8, 5), (12, 5)],
                'line_markers': [(8, 8), (8, 9), (8, 10)],
                'food_boxes': [(3, 3), (5, 3), (11, 3), (13, 3)]
            }
            
    def draw_purpose_specific(self, screen):
        """Draw decorations specific to current purpose"""
        if self.current_purpose == 'housing_office':
            # Draw posters
            for pos in self.purpose_decorations.get('posters', []):
                x, y = pos
                rect = pygame.Rect(self.room_x + x * TILE_SIZE, 
                                 self.room_y + y * TILE_SIZE,
                                 TILE_SIZE * 2, TILE_SIZE * 2)
                pygame.draw.rect(screen, (200, 200, 150), rect)
                pygame.draw.rect(screen, (100, 100, 80), rect, 2)
                
                # Poster text
                text = self.small_font.render("HOUSING", True, (50, 50, 40))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                
        elif self.current_purpose == 'courtroom':
            # Draw judge's bench
            bench_pos = self.purpose_decorations.get('judge_bench')
            if bench_pos:
                x, y = bench_pos
                bench_rect = pygame.Rect(self.room_x + (x-1) * TILE_SIZE,
                                       self.room_y + y * TILE_SIZE,
                                       TILE_SIZE * 3, TILE_SIZE * 2)
                pygame.draw.rect(screen, (60, 40, 20), bench_rect)
                pygame.draw.rect(screen, (40, 20, 10), bench_rect, 3)
                
        elif self.current_purpose == 'shelter':
            # Draw cots
            for cot_pos in self.purpose_decorations.get('cots', []):
                x, y = cot_pos
                cot_rect = pygame.Rect(self.room_x + x * TILE_SIZE + 4,
                                     self.room_y + y * TILE_SIZE + 8,
                                     24, 40)
                pygame.draw.rect(screen, (80, 80, 100), cot_rect)
                pygame.draw.rect(screen, (50, 50, 70), cot_rect, 2)
                
            # Dim lighting for nighttime
            if self.game.game_hour >= 20 or self.game.game_hour < 6:
                overlay = pygame.Surface((self.room_width * TILE_SIZE,
                                        self.room_height * TILE_SIZE))
                overlay.fill((0, 0, 20))
                overlay.set_alpha(150)
                screen.blit(overlay, (self.room_x, self.room_y))
                
        elif self.current_purpose == 'food_bank':
            # Draw food tables
            for table_pos in self.purpose_decorations.get('food_tables', []):
                x, y = table_pos
                table_rect = pygame.Rect(self.room_x + x * TILE_SIZE,
                                       self.room_y + y * TILE_SIZE,
                                       TILE_SIZE * 2, TILE_SIZE)
                pygame.draw.rect(screen, (139, 69, 19), table_rect)
                
                # Food items on table
                food_items = ['Bread', 'Cans', 'Produce']
                item_text = self.small_font.render(food_items[x % 3], True, (255, 255, 200))
                item_rect = item_text.get_rect(center=table_rect.center)
                screen.blit(item_text, item_rect)
                
    def draw_npcs(self, screen):
        """Draw NPCs based on current purpose"""
        for npc_id, npc_data in self.npcs.items():
            x, y = npc_data['pos']
            npc_x = self.room_x + x * TILE_SIZE
            npc_y = self.room_y + y * TILE_SIZE
            
            # Draw NPC sprite (simple for now)
            if 'judge' in npc_id:
                color = (40, 40, 60)  # Black robes
            elif 'caseworker' in npc_id:
                color = (100, 120, 180)  # Business casual
            elif 'volunteer' in npc_id:
                color = (150, 180, 120)  # Volunteer vest
            else:
                color = (120, 100, 80)  # Default
                
            # Body
            pygame.draw.rect(screen, color, (npc_x + 8, npc_y + 16, 16, 24))
            # Head
            pygame.draw.circle(screen, (200, 180, 160), (npc_x + 16, npc_y + 12), 8)
            
            # Name label when player is near
            if abs(self.player_x - x) <= 2 and abs(self.player_y - y) <= 2:
                name_surf = self.small_font.render(npc_data['name'], True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(npc_x + TILE_SIZE // 2, npc_y - 10))
                
                # Background for name
                pygame.draw.rect(screen, (40, 40, 50), name_rect.inflate(10, 4))
                screen.blit(name_surf, name_rect)
                
    def draw(self, screen):
        """Draw the multi-purpose office"""
        # Draw base interior
        super().draw(screen)
        
        # Draw purpose-specific elements
        self.draw_purpose_specific(screen)
        
        # Draw NPCs
        self.draw_npcs(screen)
        
        # Draw room title based on purpose
        title_text = {
            'housing_office': "Housing Assistance Office",
            'courtroom': "Municipal Courtroom",
            'shelter': "Emergency Shelter",
            'food_bank': "Community Food Bank",
            'benefits_office': "Benefits Office",
            'legal_aid': "Public Defender's Office"
        }.get(self.current_purpose, "Community Office")
        
        title_surf = self.font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        
        # Title background
        pygame.draw.rect(screen, (40, 40, 50), title_rect.inflate(20, 10))
        screen.blit(title_surf, title_rect)
"""Housing Menu Activity - Non-sequential choice system for Part 1"""

import pygame
from shared.constants import *

class HousingMenuActivity:
    """Displays housing options for players to choose their path"""
    
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        
        # Housing path options
        self.housing_options = [
            {
                'id': 'apartment',
                'title': 'Try to Rent Apartment',
                'desc': 'Search for traditional housing',
                'objectives': ['apartment_search', 'rental_application', 'cosigner_denial'],
                'color': (120, 170, 255)
            },
            {
                'id': 'roommate',
                'title': 'Find a Roommate',
                'desc': 'Look for shared housing',
                'objectives': ['roommate_search', 'roommate_found', 'roommate_risk', 'roommate_leaves'],
                'color': (255, 170, 120)
            },
            {
                'id': 'couch_surf',
                'title': 'Couch Surfing',
                'desc': 'Stay with friends temporarily',
                'objectives': ['couch_surf_start', 'sarah_couch', 'mike_couch', 'couch_exhaustion'],
                'color': (120, 255, 170)
            },
            {
                'id': 'tlp',
                'title': 'Transitional Housing',
                'desc': 'Apply for TLP program',
                'objectives': ['tlp_application', 'tlp_waitlist', 'tlp_accepted', 'tlp_ending'],
                'color': (200, 120, 255)
            },
            {
                'id': 'shelter',
                'title': 'Emergency Shelter',
                'desc': 'Seek emergency housing',
                'objectives': ['shelter_search', 'shelter_full', 'shelter_rules'],
                'color': (255, 120, 120)
            },
            {
                'id': 'save',
                'title': 'Save for Deposit',
                'desc': 'Try to save money first',
                'objectives': ['save_deposit', 'work_calculate', 'deposit_timeline'],
                'color': (255, 220, 120)
            }
        ]
        
        # Additional challenge categories
        self.challenge_categories = [
            {
                'title': 'Daily Struggles',
                'objectives': ['address_needed', 'belongings_stolen', 'shower_access', 'winter_coming']
            },
            {
                'title': 'Support Systems',
                'objectives': ['case_worker', 'support_group', 'document_help']
            },
            {
                'title': 'Consequences',
                'objectives': ['job_lost', 'school_dropped', 'health_declining', 'police_harassment']
            },
            {
                'title': 'Small Victories',
                'objectives': ['found_room', 'laundry_day', 'hot_meal']
            }
        ]
        
        self.selected_option = 0
        self.selected_category = None
        self.completed_paths = set()
        
    def start(self):
        """Start the housing menu activity"""
        self.active = True
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_ESCAPE:
            self.active = False
            
        elif key == pygame.K_UP:
            if self.selected_category is None:
                self.selected_option = (self.selected_option - 1) % len(self.housing_options)
            
        elif key == pygame.K_DOWN:
            if self.selected_category is None:
                self.selected_option = (self.selected_option + 1) % len(self.housing_options)
                
        elif key == pygame.K_RETURN or key == pygame.K_e:
            if self.selected_category is None:
                # Select a housing path
                selected = self.housing_options[self.selected_option]
                self.start_housing_path(selected)
                
        elif key == pygame.K_TAB:
            # Switch between main options and challenge categories
            if self.selected_category is None:
                self.selected_category = 0
            else:
                self.selected_category = None
                
    def start_housing_path(self, path):
        """Start the selected housing path"""
        # Mark this path as attempted
        self.completed_paths.add(path['id'])
        
        # Find the first objective in this path
        first_objective_id = path['objectives'][0]
        
        # Update the objective manager to jump to this objective
        for i, obj in enumerate(self.objective_manager.objectives):
            if obj.id == first_objective_id:
                self.objective_manager.current_objective_index = i
                self.objective_manager.showing_notification = False
                self.active = False
                break
    
    def draw(self, screen):
        """Draw the housing menu"""
        if not self.active:
            return
            
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_text = "HOUSING CRISIS: CHOOSE YOUR PATH"
        title_surf = self.title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Each path leads to different challenges. There's no easy solution."
        subtitle_surf = self.small_font.render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 90))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw housing options
        start_y = 140
        option_height = 80
        option_width = 600
        
        for i, option in enumerate(self.housing_options):
            x = (SCREEN_WIDTH - option_width) // 2
            y = start_y + i * (option_height + 10)
            
            # Background
            bg_color = option['color'] if i == self.selected_option and self.selected_category is None else (40, 40, 50)
            if i == self.selected_option and self.selected_category is None:
                # Glow effect
                glow_rect = pygame.Rect(x - 5, y - 5, option_width + 10, option_height + 10)
                pygame.draw.rect(screen, (*option['color'], 50), glow_rect, border_radius=10)
            
            option_rect = pygame.Rect(x, y, option_width, option_height)
            pygame.draw.rect(screen, bg_color, option_rect, border_radius=8)
            
            # Border
            border_color = option['color']
            pygame.draw.rect(screen, border_color, option_rect, width=2, border_radius=8)
            
            # Completed indicator
            if option['id'] in self.completed_paths:
                check_text = "✓ ATTEMPTED"
                check_surf = self.small_font.render(check_text, True, (120, 255, 120))
                screen.blit(check_surf, (x + option_width - 100, y + 10))
            
            # Title
            title_surf = self.font.render(option['title'], True, (255, 255, 255))
            screen.blit(title_surf, (x + 20, y + 15))
            
            # Description
            desc_surf = self.small_font.render(option['desc'], True, (180, 180, 180))
            screen.blit(desc_surf, (x + 20, y + 45))
            
            # Objective count
            obj_text = f"{len(option['objectives'])} scenarios"
            obj_surf = self.small_font.render(obj_text, True, (150, 150, 150))
            screen.blit(obj_surf, (x + option_width - 150, y + 45))
        
        # Instructions
        inst_y = SCREEN_HEIGHT - 80
        instructions = [
            "↑↓ Navigate    ENTER/E Select Path    TAB View Challenges    ESC Close"
        ]
        
        for i, text in enumerate(instructions):
            surf = self.small_font.render(text, True, (180, 180, 180))
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y + i * 25))
            screen.blit(surf, rect)
        
        # Progress indicator
        progress_text = f"Paths Attempted: {len(self.completed_paths)}/6"
        progress_surf = self.font.render(progress_text, True, (255, 220, 100))
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(progress_surf, progress_rect)
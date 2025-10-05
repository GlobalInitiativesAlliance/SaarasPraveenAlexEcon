"""Activity Manager for Part 1 Housing Mini-Games"""

import pygame
from .packing_game import PackingGame
from .apartment_search_game import ApartmentSearchGame
from .budget_survival_game import BudgetSurvivalGame
from .schedule_conflict_game import ScheduleConflictGame
from .couch_surfing_game import CouchSurfingGame
from .form_filling_game import FormFillingGame
from .shelter_night_game import ShelterNightGame

class HousingActivityManager:
    """Manages all mini-game activities for housing storyline"""
    
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.current_activity = None
        
        # Initialize all mini-games
        self.activities = {
            'packing': PackingGame(),
            'apartment_search': ApartmentSearchGame(),
            'budget_survival': BudgetSurvivalGame(),
            'schedule_conflict': ScheduleConflictGame(),
            'couch_surfing': CouchSurfingGame(),
            'form_filling': FormFillingGame(),
            'shelter_night': ShelterNightGame()
        }
        
        # Map objectives to activities
        self.objective_activities = {
            'packed_belongings': 'packing',
            'apartment_search': 'apartment_search',
            'cash_reality': 'budget_survival',
            'work_schedule_conflict': 'schedule_conflict',
            'first_night': 'couch_surfing',
            'tlp_application': 'form_filling',
            'shelter_rules': 'shelter_night'
        }
        
    def start_activity(self, objective_id):
        """Start activity based on current objective"""
        if objective_id in self.objective_activities:
            activity_key = self.objective_activities[objective_id]
            self.current_activity = self.activities[activity_key]
            self.current_activity.start()
            return True
        return False
        
    def update(self, dt):
        """Update current activity"""
        if self.current_activity and self.current_activity.active:
            self.current_activity.update(dt)
            
            # Check if activity completed
            if self.current_activity.completed:
                self.handle_activity_completion()
                
    def handle_activity_completion(self):
        """Process activity results"""
        if not self.current_activity:
            return
            
        # Get results based on activity type
        if isinstance(self.current_activity, PackingGame):
            essentials = self.current_activity.essential_packed
            if essentials < 5:
                self.objective_manager.show_notification(
                    "You forgot essential items. This will make life harder.",
                    (255, 100, 100)
                )
            else:
                self.objective_manager.show_notification(
                    "You packed the essentials. Ready to face the world.",
                    (100, 255, 100)
                )
                
        elif isinstance(self.current_activity, ApartmentSearchGame):
            if self.current_activity.viewings_scheduled:
                self.objective_manager.show_notification(
                    f"Scheduled {len(self.current_activity.viewings_scheduled)} viewings. Most during work hours...",
                    (255, 200, 100)
                )
            else:
                self.objective_manager.show_notification(
                    "No apartments found. The requirements are impossible.",
                    (255, 100, 100)
                )
                
        elif isinstance(self.current_activity, BudgetSurvivalGame):
            if self.current_activity.success:
                self.objective_manager.show_notification(
                    f"Survived {self.current_activity.days_survived} days on ${73}. Barely.",
                    (100, 255, 100)
                )
            else:
                self.objective_manager.show_notification(
                    f"{self.current_activity.game_over_reason}",
                    (255, 100, 100)
                )
                
        # Complete objective
        self.objective_manager.complete_current_objective()
        self.current_activity = None
        
    def handle_event(self, event):
        """Pass events to current activity"""
        if self.current_activity and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.current_activity, 'handle_click'):
                    self.current_activity.handle_click(event.pos)
                    
    def draw(self, screen):
        """Draw current activity"""
        if self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return True
        return False
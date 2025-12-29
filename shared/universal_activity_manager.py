"""Universal Activity Manager - Handles mini-games for all parts"""

import pygame

class UniversalActivityManager:
    """Manages all mini-game activities across all parts"""
    
    def __init__(self, game):
        self.game = game
        self.current_activity = None
        self.activities = {}
        
        # Load all activities lazily when needed
        self.activity_mappings = {
            # Part 1 - Housing
            'packing': ('part_1_housing_stability.activities.packing_game', 'PackingGame'),
            'apartment_search': ('src.activities.apartment_search', 'ApartmentSearch'),
            'budget_survival': ('part_1_housing_stability.activities.budget_survival_game', 'BudgetSurvivalGame'),
            'schedule_conflict': ('part_1_housing_stability.activities.schedule_conflict_game', 'ScheduleConflictGame'),
            'couch_surfing': ('part_1_housing_stability.activities.couch_surfing_game', 'CouchSurfingGame'),
            'form_filling': ('part_1_housing_stability.activities.form_filling_game', 'FormFillingGame'),
            'shelter_night': ('part_1_housing_stability.activities.shelter_night_game', 'ShelterNightGame'),
            'foster_parent_call': ('src.activities.foster_parent_call', 'FosterParentCall'),
            'facebook_search': ('src.activities.facebook_search', 'FacebookSearch'),
            'packing_game': ('src.activities.packing_game', 'PackingGame'),
            'packing_game_exit': ('src.activities.packing_game', 'PackingGame'),

            # Part 2 - Housing Crisis
            'tenant_rights': ('part_2_housing_crisis.activities.tenant_rights_quiz', 'TenantRightsQuiz'),
            'emergency_packing': ('part_2_housing_crisis.activities.emergency_packing', 'EmergencyPackingGame'),
            'roommate_selection': ('part_2_housing_crisis.activities.roommate_selection', 'RoommateSelectionGame'),
            'crisis_budgeting': ('part_2_housing_crisis.activities.crisis_budgeting', 'CrisisBudgetingGame'),

            # Part 3 - Legal System
            # NOTE: Part 3 activities are handled directly by their interiors
            # (TLPApartmentPart3, SchoolPart3, etc.) - do NOT add them here
            # to avoid duplicate activity instances
        }

        # Map objectives to activities
        # NOTE: Only map objectives that should be auto-started by the activity manager
        # Interiors that manage their own activities should NOT be listed here
        self.objective_to_activity = {
            # Part 1
            'packed_belongings': 'packing',
            'apartment_search': 'apartment_search',
            'cash_reality': 'budget_survival',
            'work_schedule_conflict': 'schedule_conflict',
            'first_night': 'couch_surfing',
            'tlp_application': 'form_filling',
            'shelter_rules': 'shelter_night',
            'call_foster_parents': 'foster_parent_call',
            'your_reality': None,  # Handled by rental office interior directly
            'first_rejection': None,  # Handled by rental office interior directly
            'facebook_search': 'facebook_search',
            'move_in': 'packing_game',
            'pack_again': 'packing_game_exit',

            # Part 2
            'foster_home_class': 'tenant_rights',
            'pack_essentials': 'emergency_packing',
            'select_roommate': 'roommate_selection',
            'emergency_assistance': 'crisis_budgeting',

            # Part 3 - Activities handled by interiors directly
            # DO NOT ADD HERE - interiors launch activities on interaction
        }
        
    def load_activity(self, activity_key):
        """Dynamically load an activity"""
        if activity_key not in self.activities and activity_key in self.activity_mappings:
            module_path, class_name = self.activity_mappings[activity_key]
            try:
                # Dynamic import
                module = __import__(module_path, fromlist=[class_name])
                activity_class = getattr(module, class_name)
                self.activities[activity_key] = activity_class()
            except Exception as e:
                print(f"Failed to load activity {activity_key}: {e}")
                return None
                
        return self.activities.get(activity_key)
        
    def start_activity_for_objective(self, objective_id):
        """Start the appropriate activity for an objective"""
        activity_key = self.objective_to_activity.get(objective_id)
        if not activity_key:
            return False
            
        activity = self.load_activity(activity_key)
        if activity:
            self.current_activity = activity
            self.current_activity.start()
            return True
            
        return False
        
    def update(self, dt):
        """Update current activity"""
        if self.current_activity and self.current_activity.active:
            self.current_activity.update(dt)
            
            # Check completion
            if hasattr(self.current_activity, 'completed') and self.current_activity.completed:
                # Apply results if available
                if hasattr(self.current_activity, 'get_results'):
                    results = self.current_activity.get_results()
                    self.apply_activity_results(results)
                    
                self.current_activity = None
                return True  # Activity completed
                
        return False  # Activity still running
        
    def apply_activity_results(self, results):
        """Apply the results of an activity to game state"""
        if not results:
            return
            
        # Apply money changes
        if 'money' in results:
            self.game.player_money += results['money']
            
        # Apply stat changes
        if 'health' in results:
            self.game.player_health = max(0, min(100, self.game.player_health + results['health']))
        if 'stress' in results:
            self.game.player_stress = max(0, min(100, self.game.player_stress + results['stress']))
        if 'energy' in results:
            self.game.player_energy = max(0, min(100, self.game.player_energy + results['energy']))
            
        # Show notification
        if 'message' in results:
            self.game.show_notification(results['message'], results.get('color', (255, 255, 255)))
            
    def handle_event(self, event):
        """Pass events to current activity"""
        if self.current_activity and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.current_activity, 'handle_click'):
                    self.current_activity.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self.current_activity, 'handle_mouse_motion'):
                    self.current_activity.handle_mouse_motion(event.pos)
                    
    def draw(self, screen):
        """Draw current activity"""
        if self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
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
            'apartment_search': ('part_1_housing_stability.activities.apartment_search_game', 'ApartmentSearchGame'),
            'budget_survival': ('part_1_housing_stability.activities.budget_survival_game', 'BudgetSurvivalGame'),
            'schedule_conflict': ('part_1_housing_stability.activities.schedule_conflict_game', 'ScheduleConflictGame'),
            'couch_surfing': ('part_1_housing_stability.activities.couch_surfing_game', 'CouchSurfingGame'),
            'form_filling': ('part_1_housing_stability.activities.form_filling_game', 'FormFillingGame'),
            'shelter_night': ('part_1_housing_stability.activities.shelter_night_game', 'ShelterNightGame'),
            'foster_parent_call': ('src.activities.foster_parent_call', 'FosterParentCall'),

            # Part 2 - Housing Crisis  
            'tenant_rights': ('part_2_housing_crisis.activities.tenant_rights_quiz', 'TenantRightsQuiz'),
            'emergency_packing': ('part_2_housing_crisis.activities.emergency_packing', 'EmergencyPackingGame'),
            'roommate_selection': ('part_2_housing_crisis.activities.roommate_selection', 'RoommateSelectionGame'),
            'crisis_budgeting': ('part_2_housing_crisis.activities.crisis_budgeting', 'CrisisBudgetingGame'),
            
            # Part 3 - Healthcare
            'emergency_room': ('part_3_healthcare.activities.emergency_room_wait', 'EmergencyRoomWait'),
            'medication_rationing': ('part_3_healthcare.activities.medication_rationing', 'MedicationRationingGame'),
            'insurance_navigation': ('part_3_healthcare.activities.insurance_navigation', 'InsuranceNavigationGame'),
            'free_clinic_search': ('part_3_healthcare.activities.free_clinic_search', 'FreeClinicSearchGame'),
            
            # Part 4 - Credit/Debt
            'credit_application': ('part_4_credit_debt.activities.credit_application', 'CreditApplicationGame'),
            'payday_loan': ('part_4_credit_debt.activities.payday_loan_trap', 'PaydayLoanTrap'),
            'debt_juggling': ('part_4_credit_debt.activities.debt_juggling', 'DebtJugglingGame'),
            'collection_calls': ('part_4_credit_debt.activities.collection_calls', 'CollectionCallsGame'),
            
            # Part 5 - Education
            'class_attendance': ('part_5_education.activities.class_attendance', 'ClassAttendanceGame'),
            'homework_struggle': ('part_5_education.activities.homework_struggle', 'HomeworkStruggleGame'),
            'financial_aid_maze': ('part_5_education.activities.financial_aid_maze', 'FinancialAidMaze'),
            'study_vs_work': ('part_5_education.activities.study_vs_work', 'StudyVsWorkGame'),
            
            # Part 6 - Food Security
            'food_bank_line': ('part_6_food_security.activities.food_bank_line', 'FoodBankLineGame'),
            'grocery_stretching': ('part_6_food_security.activities.grocery_stretching', 'GroceryStretchingGame'),
            'meal_planning': ('part_6_food_security.activities.meal_planning', 'MealPlanningGame'),
            'hunger_management': ('part_6_food_security.activities.hunger_management', 'HungerManagementGame'),
            
            # Part 7 - Transportation
            'bus_navigation': ('part_7_transportation.activities.bus_navigation', 'BusNavigationGame'),
            'car_breakdown': ('part_7_transportation.activities.car_breakdown', 'CarBreakdownGame'),
            'commute_planning': ('part_7_transportation.activities.commute_planning', 'CommutePlanningGame'),
            'fare_management': ('part_7_transportation.activities.fare_management', 'FareManagementGame'),
            
            # Part 8 - Legal System
            'court_navigation': ('part_8_legal_system.activities.court_navigation', 'CourtNavigationGame'),
            'legal_document_maze': ('part_8_legal_system.activities.legal_document_maze', 'LegalDocumentMaze'),
            'public_defender_meeting': ('part_8_legal_system.activities.public_defender_meeting', 'PublicDefenderMeeting'),
            'plea_negotiation': ('part_8_legal_system.activities.plea_negotiation', 'PleaNegotiationGame')
        }
        
        # Map objectives to activities
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

            # Part 2
            'foster_home_class': 'tenant_rights',
            'pack_essentials': 'emergency_packing',
            'select_roommate': 'roommate_selection',
            'emergency_assistance': 'crisis_budgeting',
            
            # Part 3
            'er_wait': 'emergency_room',
            'medication_management': 'medication_rationing',
            'insurance_application': 'insurance_navigation',
            'find_free_clinic': 'free_clinic_search',
            
            # Part 4
            'credit_check': 'credit_application',
            'payday_loan': 'payday_loan',
            'manage_debts': 'debt_juggling',
            'collection_harassment': 'collection_calls',
            
            # Part 5
            'attend_class': 'class_attendance',
            'complete_homework': 'homework_struggle',
            'fafsa_application': 'financial_aid_maze',
            'work_study_balance': 'study_vs_work',
            
            # Part 6
            'food_bank_wait': 'food_bank_line',
            'grocery_budget': 'grocery_stretching',
            'meal_prep': 'meal_planning',
            'hunger_crisis': 'hunger_management',
            
            # Part 7
            'catch_bus': 'bus_navigation',
            'fix_car': 'car_breakdown',
            'plan_commute': 'commute_planning',
            'manage_fare': 'fare_management',
            
            # Part 8
            'navigate_court': 'court_navigation',
            'complete_forms': 'legal_document_maze',
            'meet_defender': 'public_defender_meeting',
            'negotiate_plea': 'plea_negotiation'
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
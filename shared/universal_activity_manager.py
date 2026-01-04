"""Universal Activity Manager - Handles mini-games for all parts"""

import pygame

class UniversalActivityManager:
    """Manages all mini-game activities across all parts"""
    
    def __init__(self, game):
        self.game = game
        self.current_activity = None
        self.activities = {}
        self.narrative_ref = None  # Reference to current interior for callbacks
        
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

            # Part 2 - Healthcare Access
            'mailbox_sorting': ('part_2_healthcare.activities.mailbox_sorting', 'MailboxSortingGame'),
            'enhanced_mailbox_sorting': ('part_2_healthcare.activities.enhanced_mailbox_sorting', 'EnhancedMailboxSortingGame'),
            'medicaid_notice': ('part_2_healthcare.activities.medicaid_notice_activity', 'MedicaidNoticeActivity'),
            'therapy_reminder': ('part_2_healthcare.activities.therapy_reminder_activity', 'TherapyReminderActivity'),
            'insurance_panic': ('part_2_healthcare.activities.insurance_panic_activity', 'InsurancePanicActivity'),
            'clinic_navigation': ('part_2_healthcare.activities.clinic_navigation', 'ClinicNavigationGame'),
            'clinic_checklist': ('part_2_healthcare.activities.clinic_checklist_activity', 'ClinicChecklistActivity'),
            'foster_youth_application': ('part_2_healthcare.activities.foster_youth_application_form', 'FosterYouthApplicationFormGame'),
            'approval_notification': ('part_2_healthcare.activities.approval_notification', 'ApprovalNotificationGame'),
            'therapist_call': ('part_2_healthcare.activities.therapist_call_activity', 'TherapistCallActivity'),
            'therapy_payment_decision': ('part_2_healthcare.activities.therapy_payment_decision_activity', 'TherapyPaymentDecisionActivity'),
            'workday_anxiety': ('part_2_healthcare.activities.workday_anxiety_activity', 'WorkdayAnxietyActivity'),
            'enhanced_workday_anxiety': ('part_2_healthcare.activities.enhanced_workday_anxiety_activity', 'EnhancedWorkdayAnxietyActivity'),
            'healthcare_breathing': ('part_2_healthcare.activities.breathing_exercise', 'BreathingExerciseGame'),
            'enhanced_breathing': ('part_2_healthcare.activities.enhanced_breathing_exercise', 'EnhancedBreathingExercise'),
            'pharmacy_activity': ('part_2_healthcare.activities.pharmacy_activity', 'PharmacyMedicationActivity'),
            'enhanced_pharmacy': ('part_2_healthcare.activities.enhanced_pharmacy_activity', 'EnhancedPharmacyActivity'),
            'bus_route': ('part_2_healthcare.activities.bus_route_game', 'BusRouteGame'),
            'enhanced_bus_route': ('part_2_healthcare.activities.enhanced_bus_route_game', 'EnhancedBusRouteGame'),
            'burger_rush': ('part_2_healthcare.activities.burger_rush_game', 'BurgerRushGame'),

            # Part 3 - Legal System
            'document_sorting_legal': ('part_3_legal_system.activities.document_sorting_legal', 'LegalDocumentSortingGame'),
            'mail_sorting_legal': ('part_3_legal_system.activities.mail_sorting', 'MailSortingGame'),
            'breathing_exercise_legal': ('part_3_legal_system.activities.breathing_game', 'BreathingGame'),
            'note_taking_legal': ('part_3_legal_system.activities.note_taking', 'NoteTakingGame'),
            'police_encounter_legal': ('part_3_legal_system.activities.police_encounter', 'PoliceEncounterActivity'),

            # Part 4 - Healthcare Crisis
            'breathing_exercise_part4': ('part_4_healthcare.activities.breathing_exercise', 'BreathingExerciseGame'),
            'mail_mini_game_part4': ('part_4_healthcare.activities.mail_mini_game', 'HealthcareMailGame'),
            'form_filling_part4': ('part_4_healthcare.activities.form_filling', 'MediCalFormGame'),
            'bus_route_game_part4': ('part_4_healthcare.activities.bus_route_game', 'BusRouteGame'),
            'medication_selection_part4': ('part_4_healthcare.activities.medication_selection', 'MedicationSelectionGame'),
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

            # Part 2 - Healthcare Access
            'check_mailbox': 'mailbox_sorting',
            'medicaid_notice': 'medicaid_notice',
            'therapy_reminder': 'therapy_reminder',
            'insurance_panic': 'insurance_panic',
            'travel_to_clinic': 'clinic_navigation',
            'clinic_checklist': 'clinic_checklist',
            'foster_youth_application': 'foster_youth_application',
            'application_approved': 'approval_notification',
            'therapist_call_options': 'therapist_call',
            'therapy_payment_decision': 'therapy_payment_decision',
            'work_day_anxiety': 'workday_anxiety',
            'breathing_exercise': 'healthcare_breathing',
            'pharmacy_visit': 'pharmacy_activity',
            'medication_selection': 'pharmacy_activity',
            'bus_route_game': 'bus_route',

            # Part 3 - Legal System
            # All Part 3 activity-based objectives now use UniversalActivityManager
            'mail_on_floor': 'mail_sorting_legal',
            'class_distraction': 'note_taking_legal',
            'police_stop': 'police_encounter_legal',
            # Note: stay_calm and court_citation are handled within PoliceEncounterActivity
            'document_sorting': 'document_sorting_legal',

            # Part 4 - Healthcare Crisis
            # Note: Most Part 4 activities are launched directly by interiors
            # These mappings support UAM-based launching if needed
            'sort_mail': 'mail_mini_game_part4',
            'breathing_game': 'breathing_exercise_part4',
            'medicaid_form': 'form_filling_part4',
            'catch_bus': 'bus_route_game_part4',
            'select_medication': 'medication_selection_part4',
        }
        
    def load_activity(self, activity_key, fresh=False):
        """Dynamically load an activity

        Args:
            activity_key: The key of the activity to load
            fresh: If True, create a fresh instance instead of using cached
        """
        # Always create fresh instance for activities that need state reset
        if fresh or activity_key not in self.activities:
            if activity_key in self.activity_mappings:
                module_path, class_name = self.activity_mappings[activity_key]
                try:
                    # Dynamic import
                    module = __import__(module_path, fromlist=[class_name])
                    activity_class = getattr(module, class_name)
                    # Pass objective_manager to activity constructor
                    objective_manager = getattr(self.game, 'objective_manager', None)
                    activity_instance = activity_class(objective_manager)
                    self.activities[activity_key] = activity_instance
                except Exception as e:
                    print(f"[UAM] Failed to load activity {activity_key}: {e}")
                    import traceback
                    traceback.print_exc()
                    return None

        return self.activities.get(activity_key)
        
    def start_activity_for_objective(self, objective_id, narrative_ref=None):
        """Start the appropriate activity for an objective

        Args:
            objective_id: The objective ID to start activity for
            narrative_ref: Optional reference to the interior/scene for callbacks
        """
        activity_key = self.objective_to_activity.get(objective_id)
        if not activity_key:
            # Not an error - many objectives are walk-to-location without activities
            return False

        # Always create fresh instance to reset state
        activity = self.load_activity(activity_key, fresh=True)
        if activity:
            # Store narrative reference for callbacks
            self.narrative_ref = narrative_ref
            if narrative_ref:
                activity.narrative_ref = narrative_ref

            self.current_activity = activity
            self.current_activity.start()
            print(f"[UAM] Started activity '{activity_key}' for objective '{objective_id}'")
            return True

        print(f"[UAM] Failed to load activity for objective: {objective_id}")
        return False
        
    def update(self, dt):
        """Update current activity"""
        if not self.current_activity:
            return False

        # Update if still active
        if self.current_activity.active:
            self.current_activity.update(dt)

        # Check completion (even if activity just became inactive)
        # Activities may set completed=True and active=False simultaneously
        if hasattr(self.current_activity, 'completed') and self.current_activity.completed:
                # Get results before clearing activity
                results = None
                if hasattr(self.current_activity, 'get_results'):
                    results = self.current_activity.get_results()
                    self.apply_activity_results(results)

                # Notify narrative_ref if it exists
                if self.narrative_ref and hasattr(self.narrative_ref, 'on_activity_complete'):
                    self.narrative_ref.on_activity_complete(self.current_activity, results)

                print(f"[UAM] Activity completed with results: {results}")

                # Clear activity state
                self.current_activity = None
                self.narrative_ref = None
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
            
    def is_handling_events(self):
        """Check if UAM has an active activity that should handle events

        Returns:
            bool: True if there's an active activity that should receive events
        """
        return bool(self.current_activity and self.current_activity.active)

    def handle_event(self, event):
        """Pass events to current activity

        Returns:
            bool: True if event was handled by an active activity, False otherwise
        """
        if self.current_activity and self.current_activity.active:
            # First try generic handle_event if available
            if hasattr(self.current_activity, 'handle_event'):
                self.current_activity.handle_event(event)
                return True

            # Otherwise route to specific handlers
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
            elif event.type == pygame.TEXTINPUT:
                if hasattr(self.current_activity, 'handle_text_input'):
                    self.current_activity.handle_text_input(event.text)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.current_activity, 'handle_mouse_click'):
                    self.current_activity.handle_mouse_click(event.pos, event.button)
                elif hasattr(self.current_activity, 'handle_click'):
                    self.current_activity.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self.current_activity, 'handle_mouse_motion'):
                    self.current_activity.handle_mouse_motion(event.pos)
            return True
        return False
                    
    def draw(self, screen):
        """Draw current activity"""
        if self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
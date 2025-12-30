"""
Pharmacy Interior for Part 4 - Healthcare
Handles pharmacy visit and medication selection scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class PharmacyPart4(NarrativeInterior):
    """Pharmacy with medication selection narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.medication_selected = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up pharmacy scene based on objective"""
        super().enter()

        print(f"[PHARMACY_P4] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[PHARMACY_P4]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[PHARMACY_P4]   Phase changed!")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[PHARMACY_P4]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'pharmacy_visit':
            # Arriving at pharmacy - dialogue only
            pass

        elif phase_id == 'select_medication':
            # Medication selection mini-game
            interactions = self.narrative_content.get('select_medication', {}).get('interactions', {})
            if 'browse_medications' in interactions:
                self.add_interactive_object('browse_medications', interactions['browse_medications'])

    def load_narrative_content(self):
        """Load the pharmacy narrative content for Part 4"""
        return {
            'pharmacy_visit': {
                'npcs': [
                    {'name': 'Pharmacist', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You enter the pharmacy."),
                    (None, "The fluorescent lights hum overhead. Rows of medications line the shelves."),
                    ("Pharmacist", "Hello! How can I help you today?"),
                    ("You", "I need to pick up my prescription..."),
                    ("Pharmacist", "Let me check your insurance..."),
                    ("Pharmacist", "I see your Medi-Cal is currently in processing."),
                    ("Pharmacist", "You'll have to pay out of pocket today."),
                    ("You", "How much will that cost?"),
                    ("Pharmacist", "The brand name is over $120..."),
                    ("Pharmacist", "But we have generic options that might be more affordable."),
                    ("Pharmacist", "Take a look at what we have available."),
                ],
                'interactions': {}
            },

            'select_medication': {
                'npcs': [
                    {'name': 'Pharmacist', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Pharmacist", "Here are your options."),
                    (None, "You need a 50mg dose, 30-day supply."),
                    (None, "You have $40 in your budget."),
                    (None, "Look for a generic that fits your needs."),
                ],
                'interactions': {
                    'browse_medications': {
                        'position': (10, 6),
                        'prompt': 'Browse medications',
                        'trigger_activity': 'medication_selection',
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'pharmacy_visit':
            current.dynamic_description = "Visit the pharmacy"

        elif current.id == 'select_medication':
            if self.medication_selected:
                current.dynamic_description = "Medication purchased!"
            else:
                current.dynamic_description = "Select affordable medication"
                current.progress_text = "Press E to browse medications"

    def interact_with_object(self, name):
        """Handle interactions for Part 4 pharmacy"""
        print(f"[PHARMACY_P4] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'medication_selection':
                self.launch_medication_selection_game()
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            print(f"[PHARMACY_P4] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_medication_selection_game(self):
        """Launch the medication selection mini-game"""
        from part_4_healthcare.activities.medication_selection import MedicationSelectionGame

        if self.current_activity and self.current_activity.active:
            print("[PHARMACY_P4] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None

            activity = MedicationSelectionGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[PHARMACY_P4] Medication selection game launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            return

        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            if self.current_activity.completed or not self.current_activity.active:
                print(f"[PHARMACY_P4] Activity completed - cleaning up")

                if self.current_objective_phase == 'select_medication':
                    self.medication_selected = True
                    print("[PHARMACY_P4] Medication selected!")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    self.game.objective_manager.activity_manager.current_activity = None
                print(f"[PHARMACY_P4] All activities cleared")

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw pharmacy interior with activity overlay"""
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            self.current_activity.draw(screen)
            return

        super().draw(screen)

    def end_narrative_sequence(self):
        """Handle pharmacy transitions"""
        print(f"[PHARMACY_P4] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            print(f"[PHARMACY_P4] Objective not complete yet")
            return

        print(f"[PHARMACY_P4] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[PHARMACY_P4] Next objective also at pharmacy: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'select_medication':
            return self.medication_selected

        if current.id == 'pharmacy_visit':
            return not self.narrative_active

        return True

"""
Community Health Clinic Interior for Part 4 - Healthcare
Handles document check, Medi-Cal reapplication, and coverage delay scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class ClinicPart4(NarrativeInterior):
    """Community Health Clinic with healthcare narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.documents_checked = False
        self.form_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up clinic scene based on objective"""
        super().enter()

        print(f"[CLINIC_P4] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[CLINIC_P4]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[CLINIC_P4]   Phase changed!")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[CLINIC_P4]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'visit_clinic':
            # Arriving at clinic
            pass

        elif phase_id == 'document_check':
            # Check documents interaction
            interactions = self.narrative_content.get('document_check', {}).get('interactions', {})
            if 'check_documents' in interactions:
                self.add_interactive_object('check_documents', interactions['check_documents'])

        elif phase_id == 'medicaid_form':
            # Fill out form mini-game
            interactions = self.narrative_content.get('medicaid_form', {}).get('interactions', {})
            if 'fill_form' in interactions:
                self.add_interactive_object('fill_form', interactions['fill_form'])

        elif phase_id == 'coverage_delay':
            # Approval with delay
            pass

    def load_narrative_content(self):
        """Load the clinic narrative content for Part 4"""
        return {
            'visit_clinic': {
                'npcs': [
                    {'name': 'Receptionist', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You enter the Community Health Clinic."),
                    (None, "The waiting room is busy, but not overwhelming."),
                    ("Receptionist", "Hi there! How can I help you today?"),
                    ("You", "I received a notice that my Medi-Cal was terminated..."),
                    ("Receptionist", "Oh, that happens when you turn 21. But don't worry!"),
                    ("Receptionist", "You can apply for the Former Foster Youth program."),
                    ("Receptionist", "You'll need to show some documents first."),
                ],
                'interactions': {}
            },

            'document_check': {
                'npcs': [
                    {'name': 'Receptionist', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Receptionist", "Let me check your documents."),
                    (None, "You need: ID, previous Medi-Cal card, proof of income"),
                ],
                'interactions': {
                    'check_documents': {
                        'position': (8, 6),
                        'prompt': 'Show your documents',
                        'dialogue': [
                            "You hand over your ID and documents.",
                            "The receptionist reviews everything carefully.",
                            "Everything looks good! You can fill out the application now."
                        ],
                        'required': True
                    }
                }
            },

            'medicaid_form': {
                'npcs': [
                    {'name': 'Receptionist', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Receptionist", "Here's the Former Foster Youth program application."),
                    (None, "It's just 4 questions - shouldn't take long."),
                ],
                'interactions': {
                    'fill_form': {
                        'position': (10, 6),
                        'prompt': 'Fill out the form',
                        'trigger_activity': 'form_filling',
                        'required': True
                    }
                }
            },

            'coverage_delay': {
                'npcs': [
                    {'name': 'Receptionist', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Receptionist", "Great news! Your application is approved!"),
                    ("You", "Oh, that's such a relief!"),
                    ("Receptionist", "However... there's a 2-week processing period."),
                    ("You", "Two weeks? But I have appointments..."),
                    ("Receptionist", "I'm sorry, that's just how the system works."),
                    ("Receptionist", "Your coverage will be active in about 14 days."),
                    (None, "You'll need to manage without coverage for the next two weeks."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'visit_clinic':
            current.dynamic_description = "Visit the Community Health Clinic"

        elif current.id == 'document_check':
            if self.documents_checked:
                current.dynamic_description = "Documents verified!"
            else:
                current.dynamic_description = "Show your documents"
                current.progress_text = "Press E to present documents"

        elif current.id == 'medicaid_form':
            if self.form_completed:
                current.dynamic_description = "Application submitted!"
            else:
                current.dynamic_description = "Fill out the application"
                current.progress_text = "Press E to start form"

        elif current.id == 'coverage_delay':
            current.dynamic_description = "Approved - but you must wait..."

    def interact_with_object(self, name):
        """Handle interactions for Part 4 clinic"""
        print(f"[CLINIC_P4] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'form_filling':
                self.launch_form_filling_game()
                return

            # Handle document check
            if name == 'check_documents':
                self.documents_checked = True

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            print(f"[CLINIC_P4] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_form_filling_game(self):
        """Launch the Medi-Cal form filling mini-game"""
        from part_4_healthcare.activities.form_filling import MediCalFormGame

        if self.current_activity and self.current_activity.active:
            print("[CLINIC_P4] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None

            activity = MediCalFormGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[CLINIC_P4] Form filling game launched")

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
                print(f"[CLINIC_P4] Activity completed - cleaning up")

                if self.current_objective_phase == 'medicaid_form':
                    self.form_completed = True
                    print("[CLINIC_P4] Form completed!")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    self.game.objective_manager.activity_manager.current_activity = None
                print(f"[CLINIC_P4] All activities cleared")

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw clinic interior with activity overlay"""
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            self.current_activity.draw(screen)
            return

        super().draw(screen)

    def end_narrative_sequence(self):
        """Handle clinic transitions"""
        print(f"[CLINIC_P4] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            print(f"[CLINIC_P4] Objective not complete yet")
            return

        print(f"[CLINIC_P4] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[CLINIC_P4] Next objective also at clinic: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'document_check':
            return self.documents_checked

        if current.id == 'medicaid_form':
            return self.form_completed

        if current.id in ['visit_clinic', 'coverage_delay']:
            return not self.narrative_active

        return True

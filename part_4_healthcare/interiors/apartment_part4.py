"""
TLP Apartment Interior for Part 4 - Healthcare
Handles mail sorting, Medi-Cal notice discovery, therapy decisions, and later scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class ApartmentPart4(NarrativeInterior):
    """TLP apartment with healthcare narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.mail_sorted = False
        self.medicaid_notice_read = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up apartment scene based on objective"""
        super().enter()

        print(f"[APT_P4] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P4]   current objective: {current.id if current else 'None'}")
        print(f"[APT_P4]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[APT_P4]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[APT_P4]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[APT_P4]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'morning_mail':
            # Initial scene - just dialogue
            pass

        elif phase_id == 'sort_mail':
            # Mail sorting mini-game
            interactions = self.narrative_content.get('sort_mail', {}).get('interactions', {})
            if 'mailbox' in interactions:
                self.add_interactive_object('mailbox', interactions['mailbox'])

        elif phase_id == 'medicaid_notice':
            # Reading the Medi-Cal notice
            pass

        elif phase_id == 'therapy_reminder':
            # Phone notification about therapy
            pass

        elif phase_id == 'therapy_decision':
            # Choose therapy payment option
            pass

        elif phase_id in ['missed_appointment', 'caseworker_call', 'navigator_quiz',
                          'coverage_active', 'healthcare_reflection']:
            # Later apartment scenes
            pass

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 4"""
        return {
            'morning_mail': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "It's 9am. You wake up in your TLP apartment."),
                    (None, "A pile of mail sits by the door - you've been putting off checking it."),
                    ("You", "I should probably go through that mail today..."),
                ],
                'interactions': {}
            },

            'sort_mail': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to sort through the mail pile."),
                    (None, "Bills, junk mail, official-looking envelopes..."),
                ],
                'interactions': {
                    'mailbox': {
                        'position': (8, 6),
                        'prompt': 'Sort through the mail',
                        'trigger_activity': 'mail_sorting',
                        'required': True
                    }
                }
            },

            'medicaid_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at the letter in your hands."),
                    (None, "NOTICE OF TERMINATION - MEDI-CAL COVERAGE"),
                    ("You", "What? My coverage is ending?"),
                    (None, "Due to age eligibility requirements at 21..."),
                    (None, "Your Medi-Cal coverage has been terminated."),
                    ("You", "But I still need my medications... my therapy..."),
                    (None, "The letter mentions a 'Former Foster Youth' program."),
                    (None, "You'll need to visit the Community Health Clinic to reapply."),
                ],
                'interactions': {}
            },

            'therapy_reminder': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone buzzes."),
                    (None, "REMINDER: Therapy appointment tomorrow at 2pm"),
                    ("You", "Oh no... I don't have insurance anymore."),
                    (None, "The appointment will cost $150 out of pocket."),
                ],
                'interactions': {}
            },

            'therapy_decision': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your therapist's office calls."),
                    ("Therapist Office", "We noticed your insurance lapsed. How would you like to proceed?"),
                    (None, "1. Pay $150 for the session"),
                    (None, "2. Cancel the appointment"),
                    (None, "3. Ask about sliding scale options"),
                ],
                'interactions': {}
            },

            'missed_appointment': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You couldn't make it to your caseworker appointment."),
                    (None, "Your trust level with the system has decreased."),
                    ("You", "I tried... the bus was late, and I had class..."),
                ],
                'interactions': {}
            },

            'caseworker_call': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone rings."),
                    ("Caseworker", "Hi, I noticed you missed your appointment."),
                    ("Caseworker", "I understand things can be difficult to juggle."),
                    ("Caseworker", "I want to connect you with a Foster Youth Navigator."),
                    ("Caseworker", "They specialize in helping with exactly these situations."),
                    ("You", "That... would actually be really helpful."),
                ],
                'interactions': {}
            },

            'navigator_quiz': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The navigator teaches you about maintaining coverage."),
                    (None, "Let's review what you've learned..."),
                ],
                'interactions': {}
            },

            'coverage_active': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You receive a notification."),
                    (None, "MEDI-CAL COVERAGE RESTORED"),
                    ("You", "Finally! It's been such a stressful few weeks."),
                    (None, "A new therapy appointment has been scheduled."),
                    (None, "Your medications are covered again."),
                ],
                'interactions': {}
            },

            'healthcare_reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit in your apartment, reflecting on everything."),
                    (None, "Navigating the healthcare system felt impossible at times."),
                    (None, "But with the right support, you made it through."),
                    ("You", "I wish I had known about the Former Foster Youth program sooner."),
                    (None, "You've learned valuable lessons about advocating for yourself."),
                    (None, "Part 4 Complete - Healthcare System Navigation"),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'morning_mail':
            current.dynamic_description = "Check your mail"
            current.progress_text = "Walk to the mailbox"

        elif current.id == 'sort_mail':
            if self.mail_sorted:
                current.dynamic_description = "Mail sorted!"
            else:
                current.dynamic_description = "Sort through your mail"
                current.progress_text = "Press E near the mail pile"

        elif current.id == 'medicaid_notice':
            current.dynamic_description = "Read the official notice"
            current.progress_text = "Your coverage has been terminated..."

    def interact_with_object(self, name):
        """Handle interactions for Part 4"""
        print(f"[APT_P4] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'mail_sorting':
                self.launch_mail_mini_game()
                return

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[APT_P4] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_mail_mini_game(self):
        """Launch the healthcare mail sorting mini-game"""
        from part_4_healthcare.activities.mail_mini_game import HealthcareMailGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[APT_P4] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            # Clear any stale activity_manager reference
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None

            activity = HealthcareMailGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P4] Mail sorting game launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                # Route key events to activity (including ESC)
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            return

        # Use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed (or inactive but not yet cleaned up)
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[APT_P4] Activity completed/inactive - cleaning up")

                # Handle completion based on activity type
                if self.current_objective_phase == 'sort_mail':
                    self.mail_sorted = True
                    # Get results from mail sorting
                    if hasattr(self.current_activity, 'found_medicaid_notice'):
                        if self.current_activity.found_medicaid_notice:
                            print("[APT_P4] Medi-Cal notice found in mail!")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    self.game.objective_manager.activity_manager.current_activity = None
                print(f"[APT_P4] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[APT_P4] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw apartment interior with activity overlay"""
        # Draw activity ONLY if it's truly active
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            self.current_activity.draw(screen)
            return

        # Draw base interior
        super().draw(screen)

    def end_narrative_sequence(self):
        """Override to properly handle apartment transitions"""
        print(f"[APT_P4] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P4]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[APT_P4] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[APT_P4] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this apartment
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in apartment, reinitialize for next phase
            print(f"[APT_P4] Next objective also at apartment: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            # Exit apartment
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'sort_mail':
            print(f"[APT_P4] check_objective_complete for sort_mail: mail_sorted={self.mail_sorted}")
            return self.mail_sorted

        # For dialogue-only objectives, complete after dialogue ends
        if current.id in ['morning_mail', 'medicaid_notice', 'therapy_reminder',
                          'therapy_decision', 'missed_appointment', 'caseworker_call',
                          'navigator_quiz', 'coverage_active', 'healthcare_reflection']:
            # Check if dialogue is complete
            return not self.narrative_active

        return True

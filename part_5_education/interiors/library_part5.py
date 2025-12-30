"""
Library Interior for Part 5 - Education Access
Handles laptop request process and document verification
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class LibraryPart5(NarrativeInterior):
    """Library with education narrative phases for laptop program"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.documents_verified = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up library scene based on objective"""
        super().enter()

        print(f"[LIBRARY_P5] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[LIBRARY_P5]   current objective: {current.id if current else 'None'}")
        print(f"[LIBRARY_P5]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[LIBRARY_P5]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[LIBRARY_P5]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[LIBRARY_P5]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'library_visit':
            # Initial library visit - approach front desk
            interactions = self.narrative_content.get('library_visit', {}).get('interactions', {})
            if 'front_desk' in interactions:
                self.add_interactive_object('front_desk', interactions['front_desk'])

        elif phase_id == 'id_verification':
            # Document verification mini-game
            interactions = self.narrative_content.get('id_verification', {}).get('interactions', {})
            if 'document_station' in interactions:
                self.add_interactive_object('document_station', interactions['document_station'])

        elif phase_id == 'laptop_waitlist':
            # Result - laptops unavailable
            pass

    def load_narrative_content(self):
        """Load the library narrative content for Part 5"""
        return {
            'library_visit': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You enter the public library."),
                    (None, "A sign reads: 'Free Laptop Lending Program for Students'"),
                    ("You", "Maybe I can get a laptop for school..."),
                    ("Librarian", "Welcome! Are you here about the laptop program?"),
                    ("You", "Yes, I need a computer for my classes."),
                    ("Librarian", "Great! We have a program for foster youth and students."),
                    ("Librarian", "I just need to verify your documents first."),
                ],
                'interactions': {
                    'front_desk': {
                        'position': (8, 4),
                        'prompt': 'Ask about laptop program',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'id_verification': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "For the laptop program, I need to see:"),
                    (None, "- A valid photo ID"),
                    (None, "- Proof of foster care status"),
                    (None, "- Current address verification (optional)"),
                    ("Librarian", "Please match your documents to the form requirements."),
                ],
                'interactions': {
                    'document_station': {
                        'position': (10, 6),
                        'prompt': 'Verify your documents',
                        'trigger_activity': 'id_verification',
                        'required': True
                    }
                }
            },

            'laptop_waitlist': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "Your documents have been verified!"),
                    ("Librarian", "Unfortunately, all our laptops are currently checked out."),
                    ("You", "Oh no... I really needed one for class."),
                    ("Librarian", "Don't worry! You're on the waitlist."),
                    ("Librarian", "We'll notify you when one becomes available."),
                    ("Librarian", "Usually it's about a week."),
                    (None, "Scheduled for pickup next week."),
                    ("You", "At least I'll have one eventually..."),
                    (None, "In the meantime, you can use the library computers."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'library_visit':
            current.dynamic_description = "Ask about the laptop program"
            current.progress_text = "Speak with the librarian"

        elif current.id == 'id_verification':
            if self.documents_verified:
                current.dynamic_description = "Documents verified!"
            else:
                current.dynamic_description = "Verify your documents"
                current.progress_text = "Match documents to form requirements"

        elif current.id == 'laptop_waitlist':
            current.dynamic_description = "Laptops out of stock"
            current.progress_text = "Scheduled for next week"

    def interact_with_object(self, name):
        """Handle interactions for Part 5 library"""
        print(f"[LIBRARY_P5] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            # Mark interaction as completed
            self.completed_interactions.add(name)

            if trigger == 'id_verification':
                self.launch_id_verification_game()
                return
        else:
            # Mark interaction as completed for non-activity interactions
            self.completed_interactions.add(name)

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[LIBRARY_P5] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_id_verification_game(self):
        """Launch the ID verification mini-game"""
        from part_5_education.activities.id_verification import IDVerificationGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[LIBRARY_P5] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = IDVerificationGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[LIBRARY_P5] ID verification game launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
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

        # Auto-launch id_verification for id_verification phase
        if (self.current_objective_phase == 'id_verification' and
            not self.narrative_active and
            self.current_activity is None and
            not self.documents_verified):
            self.launch_id_verification_game()

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[LIBRARY_P5] Activity completed/inactive - cleaning up")

                # Handle completion based on activity TYPE (not phase)
                from part_5_education.activities.id_verification import IDVerificationGame

                if isinstance(self.current_activity, IDVerificationGame):
                    self.documents_verified = True
                    print(f"[LIBRARY_P5] Documents verified marked complete")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[LIBRARY_P5] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[LIBRARY_P5] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw library interior with activity overlay"""
        # Draw activity ONLY if it's truly active
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            if hasattr(self.current_activity, 'render'):
                self.current_activity.render(screen)
            elif hasattr(self.current_activity, 'draw'):
                self.current_activity.draw(screen)
            return

        # Draw base interior
        super().draw(screen)

    def end_narrative_sequence(self):
        """Override to properly handle library transitions"""
        print(f"[LIBRARY_P5] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[LIBRARY_P5]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[LIBRARY_P5] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[LIBRARY_P5] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this library
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in library, reinitialize for next phase
            print(f"[LIBRARY_P5] Next objective also at library: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            # Exit library
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'id_verification':
            print(f"[LIBRARY_P5] check_objective_complete: documents_verified={self.documents_verified}")
            return self.documents_verified

        # For interaction-based objectives
        if current.id == 'library_visit':
            return 'front_desk' in self.completed_interactions

        # For dialogue-only objectives, complete after dialogue ends
        if current.id == 'laptop_waitlist':
            return not self.narrative_active

        return True

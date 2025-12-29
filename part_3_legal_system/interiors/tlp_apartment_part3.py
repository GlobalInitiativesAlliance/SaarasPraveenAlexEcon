"""
TLP Apartment Interior for Part 3 - Legal System
Handles mail sorting, court notice discovery, and return home scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class TLPApartmentPart3(NarrativeInterior):
    """TLP apartment with legal system narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.mail_sorted = False
        self.court_notice_read = False

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

        print(f"[TLP_APT_P3] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[TLP_APT_P3]   current objective: {current.id if current else 'None'}")
        print(f"[TLP_APT_P3]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[TLP_APT_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[TLP_APT_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[TLP_APT_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'mail_on_floor':
            # Mail sorting scene
            interactions = self.narrative_content['mail_on_floor']['interactions']
            if 'sort_mail' in interactions:
                self.add_interactive_object('sort_mail', interactions['sort_mail'])

        elif phase_id == 'read_court_notice':
            # Reading court notice - just dialogue
            pass  # Dialogue sequence handles this

        elif phase_id == 'go_home':
            # Return home after courthouse
            pass  # Dialogue sequence handles this

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 3"""
        return {
            'mail_on_floor': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You return to your TLP apartment after a long day."),
                    (None, "Mail is scattered across the floor - you've been too busy to sort it."),
                    (None, "Bills, junk mail, official-looking envelopes... it's overwhelming."),
                    ("You", "I should really go through this stuff..."),
                ],
                'interactions': {
                    'sort_mail': {
                        'position': (8, 6),
                        'prompt': 'Sort through the mail',
                        'trigger_activity': 'mail_sorting',
                        'required': True
                    }
                }
            },

            'read_court_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Among the sorted mail, one envelope stands out."),
                    (None, "Official government letterhead. Your name in bold."),
                    ("You", "(reading) 'You are hereby summoned to appear...'"),
                    ("You", "A court date? For what? I didn't do anything!"),
                    (None, "The summons is for an unpaid traffic violation from months ago."),
                    (None, "You remember now - a ticket you couldn't afford to pay."),
                    (None, "Court date: Tomorrow morning. 9:00 AM."),
                    ("You", "Tomorrow?! But I have class AND work tomorrow!"),
                    (None, "The letter warns: Failure to appear may result in a warrant."),
                    ("You", "I can't miss work. I'll lose my job. But court..."),
                    (None, "Your phone buzzes. A text from your boss."),
                    ("Boss", "(text) Reminder: 7am shift tomorrow. MANDATORY. No excuses."),
                    ("You", "7am work. 9am court. How am I supposed to do both?"),
                    (None, "There's no good option. Only impossible choices."),
                ],
                'interactions': {}
            },

            'go_home': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You're back at your apartment."),
                    (None, "The court papers sit heavy in your pocket."),
                    (None, "$300 in fines. 30 days to pay."),
                    ("You", "Three hundred dollars..."),
                    (None, "That's almost your entire paycheck."),
                    ("You", "Rent is due next week. And utilities. And food."),
                    (None, "You sit on the edge of your bed, staring at the papers."),
                    ("You", "How am I supposed to survive this?"),
                    (None, "The walls feel like they're closing in."),
                    (None, "But there's no time to process. There never is."),
                    ("You", "I have an exam to study for..."),
                    (None, "You pull out your textbook, but the words blur together."),
                    (None, "Court. Work. School. Survival."),
                    (None, "Pick two. You can't have all four."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on apartment progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'mail_on_floor':
            if not self.mail_sorted:
                current.dynamic_description = "Sort through the scattered mail"
                current.progress_text = "Find anything important"
            else:
                current.dynamic_description = "Mail sorted..."

        elif current.id == 'read_court_notice':
            current.dynamic_description = "Read the official-looking envelope"
            current.progress_text = "Discover the court summons"

        elif current.id == 'go_home':
            current.dynamic_description = "Return to your apartment"
            current.progress_text = "Process everything that happened"

    def end_narrative_sequence(self):
        """Override to properly handle apartment transitions"""
        print(f"")
        print(f"="*80)
        print(f"[TLP_APT_P3] *** end_narrative_sequence() CALLED ***")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[TLP_APT_P3]   current objective: {current.id if current else 'None'}")
        print(f"[TLP_APT_P3]   objective complete check: {self.check_objective_complete()}")
        print(f"="*80)

        if not current:
            return

        # Only transition when the objective is actually complete (all tasks done)
        if not self.check_objective_complete():
            print(f"[TLP_APT_P3] Objective not complete yet - waiting for interactions")
            return

        # Helper function for clean transitions
        def _complete_and_transition(from_phase, to_phase):
            print(f"[TLP_APT_P3] Completing {from_phase}, moving to {to_phase}")
            print(f"[TLP_APT_P3]   Setting should_exit = True")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            print(f"[TLP_APT_P3]   Resetting should_exit = False")
            self.should_exit = False

            next_obj = self.game.objective_manager.get_current_objective()
            print(f"[TLP_APT_P3]   Next objective: {next_obj.id if next_obj else 'None'}")

            if next_obj and next_obj.id == to_phase:
                print(f"[TLP_APT_P3]   Auto-reloading for {to_phase}")
                self.enter()  # Re-initialize for next phase

        # Chain apartment objectives based on current phase
        if current.id == 'mail_on_floor':
            _complete_and_transition('mail_on_floor', 'read_court_notice')
        elif current.id == 'read_court_notice':
            # Exit after reading notice - player goes to school next
            print("[TLP_APT_P3] Completing read_court_notice, exiting apartment")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.active = False
        elif current.id == 'go_home':
            # Final apartment scene - complete Part 3 scene 16
            print("[TLP_APT_P3] Completing go_home")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.active = False
        else:
            # For other objectives, use default behavior
            print(f"[TLP_APT_P3] Other objective, completing and exiting")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.should_exit = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'mail_on_floor':
            print(f"[TLP_APT_P3] check_objective_complete for {current.id}")
            print(f"[TLP_APT_P3]   mail_sorted: {self.mail_sorted}")
            return self.mail_sorted

        # Get required interactions for current phase
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        # Find all required interactions
        required_interactions = set()
        for obj_name, obj_data in interactions.items():
            if obj_data.get('required', False):
                required_interactions.add(obj_name)

        print(f"[TLP_APT_P3] check_objective_complete for {current.id}")
        print(f"[TLP_APT_P3]   required: {required_interactions}")
        print(f"[TLP_APT_P3]   completed: {self.completed_interactions}")

        # Check if all required interactions are completed
        if required_interactions:
            completion_status = required_interactions.issubset(self.completed_interactions)
            print(f"[TLP_APT_P3]   completion status: {completion_status}")
            return completion_status
        else:
            # If no required interactions, complete after dialogue ends
            print(f"[TLP_APT_P3]   no required interactions - complete")
            return True

    def launch_activity(self, activity_name):
        """Launch activity by name - bridges NarrativeInterior to specific activities"""
        print(f"[TLP_APT_P3] Activity trigger: {activity_name}")

        if activity_name == 'mail_sorting':
            self.launch_mail_sorting_game()
        else:
            print(f"[TLP_APT_P3] Unknown activity: {activity_name}")

    def interact_with_object(self, name):
        """Handle apartment-specific interactions"""
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'mail_on_floor'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            if trigger == 'mail_sorting':
                self.launch_mail_sorting_game()
                return

        # Use parent's interaction handling
        super().interact_with_object(name)

        self.update_objective_display()

        # Check if current phase is complete (will trigger end_narrative_sequence)
        if self.check_objective_complete():
            print(f"[TLP_APT_P3] Phase complete, end_narrative_sequence will handle transition")
            self.end_narrative_sequence()

    def launch_mail_sorting_game(self):
        """Launch the mail sorting mini-game"""
        from part_3_legal_system.activities.mail_sorting import MailSortingGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[TLP_APT_P3] Activity already running, skipping launch")
            return

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            # Clear any existing activity_manager activity first
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None

            activity = MailSortingGame(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[TLP_APT_P3] Mail sorting game launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                # Route key events to activity (including ESC)
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
                # Also handle via generic handle_event if available
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.current_activity, 'handle_mouse_click'):
                    self.current_activity.handle_mouse_click(event.pos, event.button)
                elif hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self.current_activity, 'handle_mouse_motion'):
                    self.current_activity.handle_mouse_motion(event.pos)
                elif hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
                elif hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            return

        # Use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed (or inactive but not yet cleaned up)
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[TLP_APT_P3] Activity completed/inactive - cleaning up")

                # Handle completion based on activity type
                if self.current_objective_phase == 'mail_on_floor':
                    self.mail_sorted = True
                    # Get results from mail sorting
                    if hasattr(self.current_activity, 'get_results'):
                        results = self.current_activity.get_results()
                        if results.get('court_notice_found'):
                            print("[TLP_APT_P3] Court notice found in mail!")

                # Clear ALL activity references FIRST
                activity_ref = self.current_activity
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                # Also clear activity_manager's reference if it exists
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    self.game.objective_manager.activity_manager.current_activity = None
                print(f"[TLP_APT_P3] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[TLP_APT_P3] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return  # Important: return after cleanup to avoid double processing

    def draw(self, screen):
        """Draw apartment interior with activity overlay"""
        # Draw activity ONLY if it's truly active (not just existing)
        if (hasattr(self, 'current_activity') and
            self.current_activity is not None and
            hasattr(self.current_activity, 'active') and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            self.current_activity.draw(screen)
            return

        # Draw base interior (normal view)
        super().draw(screen)

        # Add subtle visual cues based on scene
        if self.current_objective_phase == 'go_home':
            # Dark overlay for somber mood
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(30)
            overlay.fill((0, 0, 40))  # Dark blue tint
            screen.blit(overlay, (0, 0))

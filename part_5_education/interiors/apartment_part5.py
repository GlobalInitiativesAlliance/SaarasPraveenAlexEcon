"""
TLP Apartment Interior for Part 5 - Education Access
Handles FAFSA application, work/study decisions, and schedule management
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class ApartmentPart5(NarrativeInterior):
    """TLP apartment with education narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.fafsa_completed = False
        self.choice_made = False
        self.schedule_completed = False

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

        print(f"[APT_P5] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P5]   current objective: {current.id if current else 'None'}")
        print(f"[APT_P5]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[APT_P5]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[APT_P5]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[APT_P5]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'foster_home_laptop':
            # Initial scene - just dialogue, then laptop interaction
            interactions = self.narrative_content.get('foster_home_laptop', {}).get('interactions', {})
            if 'laptop' in interactions:
                self.add_interactive_object('laptop', interactions['laptop'])

        elif phase_id == 'fafsa_form':
            # FAFSA form mini-game - auto-starts after entering
            pass

        elif phase_id == 'parent_info_bypass':
            # Part of FAFSA form - handled by the FAFSA game
            pass

        elif phase_id == 'double_shift_notice':
            # Phone notification about work conflict
            pass

        elif phase_id == 'work_study_choice':
            # Choice dialogue - auto-starts
            pass

        elif phase_id == 'orientation_notice':
            # Email about orientation
            pass

        elif phase_id == 'schedule_puzzle':
            # Schedule puzzle mini-game
            interactions = self.narrative_content.get('schedule_puzzle', {}).get('interactions', {})
            if 'calendar' in interactions:
                self.add_interactive_object('calendar', interactions['calendar'])

        elif phase_id == 'schedule_result':
            # Result of schedule puzzle
            pass

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 5"""
        return {
            'foster_home_laptop': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit in your foster home living room."),
                    (None, "The laptop screen glows in front of you."),
                    ("You", "Today's the day. I need to fill out this FAFSA."),
                    (None, "College seems like a distant dream sometimes..."),
                    (None, "But you've heard there's financial aid for foster youth."),
                ],
                'interactions': {
                    'laptop': {
                        'position': (8, 6),
                        'prompt': 'Open FAFSA application',
                        'trigger_activity': 'fafsa_form',
                        'required': True
                    }
                }
            },

            'fafsa_form': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The FAFSA application loads on screen."),
                    (None, "You have 60 seconds before the session times out."),
                    ("You", "Okay, let's do this..."),
                ],
                'interactions': {}
            },

            'parent_info_bypass': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The form asks for parental information."),
                    (None, "But as a foster youth, you have special status."),
                    ("You", "I remember my caseworker mentioned something about this..."),
                ],
                'interactions': {}
            },

            'double_shift_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone buzzes with a text from your manager."),
                    ("Manager", "Hey, can you cover a double shift tonight? $100 bonus."),
                    (None, "But you have a big exam tomorrow..."),
                    ("You", "I really need that money, but I also need to pass this class."),
                    (None, "You haven't studied enough yet."),
                ],
                'interactions': {}
            },

            'work_study_choice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at your phone, weighing your options."),
                    (None, "Taking the shift means $100 more, but risking your exam."),
                    (None, "Calling out means losing $50 in wages, but keeping your grades up."),
                ],
                'interactions': {}
            },

            'orientation_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your laptop pings with a new email."),
                    (None, "MANDATORY: Campus Orientation Tomorrow at 11am"),
                    ("You", "Oh no, that's the same day as my work shift..."),
                    (None, "Missing orientation could delay your enrollment."),
                    (None, "You need to figure out your schedule."),
                ],
                'interactions': {}
            },

            'schedule_puzzle': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to sort out your schedule."),
                    (None, "You need to fit both work and orientation somehow."),
                ],
                'interactions': {
                    'calendar': {
                        'position': (10, 6),
                        'prompt': 'Plan your schedule',
                        'trigger_activity': 'schedule_puzzle',
                        'required': True
                    }
                }
            },

            'schedule_result': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You've worked out your schedule."),
                    (None, "It wasn't easy, but you found a way to make it work."),
                    ("You", "I just need to stay organized and communicate clearly."),
                    (None, "Time to head to school and meet with your counselor."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'foster_home_laptop':
            current.dynamic_description = "Start your FAFSA application"
            current.progress_text = "Press E to open the laptop"

        elif current.id == 'fafsa_form':
            if self.fafsa_completed:
                current.dynamic_description = "FAFSA submitted!"
            else:
                current.dynamic_description = "Complete the FAFSA form"
                current.progress_text = "Fill in the fields before time runs out"

        elif current.id == 'work_study_choice':
            current.dynamic_description = "Make a difficult decision"
            current.progress_text = "Choose: Work shift or study for exam?"

        elif current.id == 'schedule_puzzle':
            if self.schedule_completed:
                current.dynamic_description = "Schedule complete!"
            else:
                current.dynamic_description = "Plan your schedule"
                current.progress_text = "Fit work and orientation together"

    def interact_with_object(self, name):
        """Handle interactions for Part 5"""
        print(f"[APT_P5] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'fafsa_form':
                self.launch_fafsa_game()
                return

            if trigger == 'schedule_puzzle':
                self.launch_schedule_puzzle()
                return

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[APT_P5] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_fafsa_game(self):
        """Launch the FAFSA form mini-game"""
        from part_5_education.activities.fafsa_form_game import FAFSAFormGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[APT_P5] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = FAFSAFormGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P5] FAFSA form game launched")

    def launch_schedule_puzzle(self):
        """Launch the schedule puzzle mini-game"""
        from part_5_education.activities.schedule_puzzle import SchedulePuzzleGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[APT_P5] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = SchedulePuzzleGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P5] Schedule puzzle game launched")

    def launch_choice_dialogue(self):
        """Launch the work/study choice dialogue"""
        from part_5_education.activities.choice_dialogue import ChoiceDialogueSystem

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[APT_P5] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialogueSystem(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P5] Choice dialogue launched")

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

        # Auto-launch FAFSA game for fafsa_form/parent_info_bypass phases
        if (self.current_objective_phase in ['fafsa_form', 'parent_info_bypass'] and
            not self.narrative_active and
            self.current_activity is None and
            not self.fafsa_completed):
            self.launch_fafsa_game()

        # Auto-launch choice dialogue for work_study_choice
        if (self.current_objective_phase == 'work_study_choice' and
            not self.narrative_active and
            self.current_activity is None and
            not self.choice_made):
            self.launch_choice_dialogue()

        # Auto-launch schedule puzzle for schedule_puzzle phase
        if (self.current_objective_phase == 'schedule_puzzle' and
            not self.narrative_active and
            self.current_activity is None and
            not self.schedule_completed):
            self.launch_schedule_puzzle()

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[APT_P5] Activity completed/inactive - cleaning up")

                # Handle completion based on activity type
                if self.current_objective_phase == 'fafsa_form':
                    self.fafsa_completed = True
                elif self.current_objective_phase == 'work_study_choice':
                    self.choice_made = True
                elif self.current_objective_phase == 'schedule_puzzle':
                    self.schedule_completed = True

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[APT_P5] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[APT_P5] Objective complete - calling end_narrative_sequence")
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
            if hasattr(self.current_activity, 'render'):
                self.current_activity.render(screen)
            elif hasattr(self.current_activity, 'draw'):
                self.current_activity.draw(screen)
            return

        # Draw base interior
        super().draw(screen)

    def end_narrative_sequence(self):
        """Override to properly handle apartment transitions"""
        print(f"[APT_P5] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P5]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[APT_P5] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[APT_P5] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this apartment
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in apartment, reinitialize for next phase
            print(f"[APT_P5] Next objective also at apartment: {next_obj.id}")
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
        if current.id == 'fafsa_form' or current.id == 'parent_info_bypass':
            print(f"[APT_P5] check_objective_complete for {current.id}: fafsa_completed={self.fafsa_completed}")
            return self.fafsa_completed

        if current.id == 'work_study_choice':
            return self.choice_made

        if current.id == 'schedule_puzzle':
            return self.schedule_completed

        # For interaction-based objectives
        if current.id == 'foster_home_laptop':
            return 'laptop' in self.completed_interactions

        # For dialogue-only objectives, complete after dialogue ends
        if current.id in ['double_shift_notice', 'orientation_notice', 'schedule_result']:
            return not self.narrative_active

        return True

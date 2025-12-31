"""
Community Center Interior for Part 8 - Lack of Guidance/Mentorship
Handles conflicting advice, seeking mentor, and mentor result
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class CommunityCenterPart8(NarrativeInterior):
    """Community Center with mentorship narrative phases"""

    def __init__(self, game, room_data, building_pos):
        # Set mentor_found BEFORE super().__init__ since load_narrative_content accesses it
        self.mentor_found = False

        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.conflicting_advice_completed = False
        self.seek_mentor_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up community center scene based on objective"""
        super().enter()

        print(f"[CC_P8] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[CC_P8]   current objective: {current.id if current else 'None'}")
        print(f"[CC_P8]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[CC_P8]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[CC_P8]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[CC_P8]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'community_center':
            interactions = self.narrative_content.get('community_center', {}).get('interactions', {})
            if 'door' in interactions:
                self.add_interactive_object('door', interactions['door'])

        elif phase_id == 'conflicting_advice':
            interactions = self.narrative_content.get('conflicting_advice', {}).get('interactions', {})
            if 'people' in interactions:
                self.add_interactive_object('people', interactions['people'])

        elif phase_id == 'ask_whats_best':
            interactions = self.narrative_content.get('ask_whats_best', {}).get('interactions', {})
            if 'crowd' in interactions:
                self.add_interactive_object('crowd', interactions['crowd'])

        elif phase_id == 'seek_mentor':
            interactions = self.narrative_content.get('seek_mentor', {}).get('interactions', {})
            if 'help_desk' in interactions:
                self.add_interactive_object('help_desk', interactions['help_desk'])

        # mentor_result is dialogue-only

    def load_narrative_content(self):
        """Load the community center narrative content for Part 8"""
        return {
            'community_center': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You arrive at the Community Center."),
                    (None, "A busy room full of people of all ages."),
                    ("You", "Maybe someone here can help me figure things out..."),
                    (None, "You look around for someone who looks helpful."),
                    (None, "Everyone seems busy with their own problems."),
                ],
                'interactions': {
                    'door': {
                        'position': (6, 8),
                        'prompt': 'Enter the center',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'conflicting_advice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You approach a group of people."),
                    ("You", "I'm trying to figure out what to do with my life..."),
                    (None, "Several people start talking at once."),
                ],
                'interactions': {
                    'people': {
                        'position': (8, 6),
                        'prompt': 'Ask for advice',
                        'trigger_activity': 'conflicting_advice',
                        'required': True
                    }
                }
            },

            'ask_whats_best': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You ask around: 'What's the best path for me?'"),
                    ("Person 1", "Go to college! Education is everything!"),
                    ("Person 2", "No, get a job first. You need money now."),
                    ("Person 3", "Trade school is the smart choice."),
                    ("Person 4", "Take a gap year and figure yourself out."),
                    ("You", "But which one is RIGHT?"),
                    (None, "Everyone shrugs. Nobody knows YOUR answer."),
                    (None, "The advice is plentiful. The guidance is absent."),
                ],
                'interactions': {
                    'crowd': {
                        'position': (6, 5),
                        'prompt': 'Ask the crowd',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'seek_mentor': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You approach the help desk."),
                    ("You", "I need... guidance."),
                    ("Volunteer", "What kind of help are you looking for?"),
                    (None, "You have one question. Choose wisely."),
                ],
                'interactions': {
                    'help_desk': {
                        'position': (10, 4),
                        'prompt': 'Approach the help desk',
                        'trigger_activity': 'seek_mentor',
                        'required': True
                    }
                }
            },

            'mentor_result': {
                'npcs': [],
                'dialogue_sequence': self.get_mentor_result_dialogue(),
                'interactions': {}
            }
        }

    def get_mentor_result_dialogue(self):
        """Get the mentor result dialogue based on whether mentor was found"""
        if self.mentor_found:
            return [
                (None, "Someone pauses and looks at you with understanding."),
                ("Counselor", "I work with young people who aged out of foster care."),
                ("Counselor", "I can't tell you what to do..."),
                ("Counselor", "But I can help you think through your options."),
                ("You", "Really? You'd help me?"),
                ("Counselor", "That's what I'm here for."),
                (None, "You found a mentor. Someone to guide, not decide for you."),
                (None, "This changes everything."),
            ]
        else:
            return [
                (None, "Nobody has the answer you're looking for."),
                (None, "People offer sympathy, but not solutions."),
                ("You", "I guess I'm on my own..."),
                (None, "Without a mentor, you'll have to figure things out alone."),
                (None, "Many do. But it's harder."),
            ]

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'conflicting_advice':
            if self.conflicting_advice_completed:
                current.dynamic_description = "Advice received"
            else:
                current.dynamic_description = "Talk to people"
                current.progress_text = "Ask for guidance"

        elif current.id == 'seek_mentor':
            if self.seek_mentor_completed:
                current.dynamic_description = "Question asked"
            else:
                current.dynamic_description = "Ask for guidance"
                current.progress_text = "Choose your question"

    def interact_with_object(self, name):
        """Handle interactions for Part 8 community center"""
        print(f"[CC_P8] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            # Mark interaction as completed
            self.completed_interactions.add(name)

            if trigger == 'conflicting_advice':
                self.launch_conflicting_advice()
                return

            if trigger == 'seek_mentor':
                self.launch_seek_mentor()
                return
        else:
            # Mark interaction as completed for non-activity interactions
            self.completed_interactions.add(name)

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[CC_P8] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_conflicting_advice(self):
        """Launch the conflicting advice choice dialogue"""
        from part_8_mentorship.activities.choice_dialogue_part8 import ChoiceDialoguePart8

        if self.current_activity and self.current_activity.active:
            print("[CC_P8] Activity already running, skipping launch")
            return

        activity = ChoiceDialoguePart8()
        activity.set_scenario('conflicting_advice')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[CC_P8] Conflicting advice launched")

    def launch_seek_mentor(self):
        """Launch the seek mentor choice dialogue"""
        from part_8_mentorship.activities.choice_dialogue_part8 import ChoiceDialoguePart8

        if self.current_activity and self.current_activity.active:
            print("[CC_P8] Activity already running, skipping launch")
            return

        activity = ChoiceDialoguePart8()
        activity.set_scenario('seek_mentor')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[CC_P8] Seek mentor launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
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

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[CC_P8] Activity completed/inactive - cleaning up")

                # Check if mentor was found
                if hasattr(self.current_activity, 'mentor_found'):
                    self.mentor_found = self.current_activity.mentor_found
                    print(f"[CC_P8] Mentor found: {self.mentor_found}")

                # Mark appropriate completion flag
                if self.current_objective_phase == 'conflicting_advice':
                    self.conflicting_advice_completed = True
                    print(f"[CC_P8] Conflicting advice marked complete")
                elif self.current_objective_phase == 'seek_mentor':
                    self.seek_mentor_completed = True
                    print(f"[CC_P8] Seek mentor marked complete")
                    # Update the mentor_result dialogue based on choice
                    self.narrative_content['mentor_result']['dialogue_sequence'] = self.get_mentor_result_dialogue()

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[CC_P8] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[CC_P8] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw community center interior with activity overlay"""
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
        """Override to properly handle community center transitions"""
        print(f"[CC_P8] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[CC_P8]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[CC_P8] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[CC_P8] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this community center
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in community center, reinitialize for next phase
            print(f"[CC_P8] Next objective also at community center: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            # Exit community center
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'conflicting_advice':
            return self.conflicting_advice_completed

        if current.id == 'seek_mentor':
            return self.seek_mentor_completed

        # For interaction-based objectives
        if current.id == 'community_center':
            return 'door' in self.completed_interactions

        if current.id == 'ask_whats_best':
            return 'crowd' in self.completed_interactions

        # For dialogue-only objectives, complete after dialogue ends
        if current.id == 'mentor_result':
            return not self.narrative_active

        return True

"""
School/Campus Interior for Part 5 - Education Access
Handles counselor visits, career matching, advisor meetings, and education decisions
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class SchoolPart5(NarrativeInterior):
    """School/campus with education narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.career_matching_completed = False
        self.education_path_chosen = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up school scene based on objective"""
        super().enter()

        print(f"[SCHOOL_P5] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P5]   current objective: {current.id if current else 'None'}")
        print(f"[SCHOOL_P5]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[SCHOOL_P5]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[SCHOOL_P5]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[SCHOOL_P5]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'visit_counselor':
            # Initial counselor meeting - dialogue then interaction
            interactions = self.narrative_content.get('visit_counselor', {}).get('interactions', {})
            if 'counselor_desk' in interactions:
                self.add_interactive_object('counselor_desk', interactions['counselor_desk'])

        elif phase_id == 'career_matching':
            # Career matching game - auto-starts or interaction
            interactions = self.narrative_content.get('career_matching', {}).get('interactions', {})
            if 'career_board' in interactions:
                self.add_interactive_object('career_board', interactions['career_board'])

        elif phase_id == 'trade_school_unlock':
            # Trade school appears on map
            pass

        elif phase_id == 'advisor_meeting':
            # Financial aid advisor meeting
            interactions = self.narrative_content.get('advisor_meeting', {}).get('interactions', {})
            if 'advisor_desk' in interactions:
                self.add_interactive_object('advisor_desk', interactions['advisor_desk'])

        elif phase_id == 'resource_packet':
            # Receive resource packet
            pass

        elif phase_id == 'campus_quad':
            # Campus exploration with choices
            interactions = self.narrative_content.get('campus_quad', {}).get('interactions', {})
            if 'quad_center' in interactions:
                self.add_interactive_object('quad_center', interactions['quad_center'])

        elif phase_id == 'education_path':
            # Final education decision
            pass

        elif phase_id == 'education_reflection':
            # Final reflection
            pass

    def load_narrative_content(self):
        """Load the school narrative content for Part 5"""
        return {
            'visit_counselor': {
                'npcs': [
                    {'name': 'Counselor', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You walk into the school counselor's office."),
                    ("Counselor", "Hi! I've been expecting you."),
                    ("Counselor", "I know navigating college options can feel overwhelming."),
                    ("Counselor", "Let's talk about your career interests first."),
                    ("You", "I'm not really sure what I want to do..."),
                    ("Counselor", "That's perfectly normal! Let's explore some options together."),
                ],
                'interactions': {
                    'counselor_desk': {
                        'position': (8, 4),
                        'prompt': 'Talk to counselor about careers',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'career_matching': {
                'npcs': [
                    {'name': 'Counselor', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Counselor", "I have an exercise that might help."),
                    ("Counselor", "Let's match different careers with their training requirements."),
                    (None, "Some careers need a 4-year degree, others just a certificate."),
                    ("Counselor", "This will help you see all your options."),
                ],
                'interactions': {
                    'career_board': {
                        'position': (10, 4),
                        'prompt': 'Match careers with training',
                        'trigger_activity': 'career_matching',
                        'required': True
                    }
                }
            },

            'trade_school_unlock': {
                'npcs': [
                    {'name': 'Counselor', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Counselor", "Great job with that exercise!"),
                    ("Counselor", "I noticed you seemed interested in the trade careers."),
                    (None, "A trade school tour location has appeared on your map."),
                    ("Counselor", "It's another option worth considering."),
                    ("You", "I didn't know trade school could lead to good careers."),
                    ("Counselor", "Absolutely! Many trades pay very well and are in high demand."),
                ],
                'interactions': {}
            },

            'advisor_meeting': {
                'npcs': [
                    {'name': 'Financial Advisor', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    (None, "You meet with the financial aid advisor."),
                    ("Advisor", "I see your FAFSA has been processed."),
                    ("Advisor", "Great news - you qualify for several grants as a foster youth."),
                    ("You", "Really? I wasn't sure if I'd get anything."),
                    ("Advisor", "The Chafee Grant is specifically for students like you."),
                    ("Advisor", "Up to $5,000 per year for educational expenses."),
                ],
                'interactions': {
                    'advisor_desk': {
                        'position': (10, 6),
                        'prompt': 'Discuss financial aid',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'resource_packet': {
                'npcs': [
                    {'name': 'Financial Advisor', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Advisor", "Here's a resource packet for you."),
                    (None, "The packet contains information about:"),
                    (None, "- Campus housing for foster youth"),
                    (None, "- Free tutoring services"),
                    (None, "- Emergency aid funds"),
                    (None, "- Mental health counseling"),
                    ("Advisor", "Don't hesitate to use these resources. They're here for you."),
                    ("You", "Thank you... I didn't know all this existed."),
                ],
                'interactions': {}
            },

            'campus_quad': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You walk through the campus quad."),
                    (None, "Students sit on benches, studying and chatting."),
                    ("You", "Could this really be my future?"),
                    (None, "You see signs pointing to different departments."),
                    (None, "It's time to think about which path to take."),
                ],
                'interactions': {
                    'quad_center': {
                        'position': (8, 8),
                        'prompt': 'Consider your options',
                        'trigger_activity': 'education_choice',
                        'required': True
                    }
                }
            },

            'education_path': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You think about everything you've learned."),
                    (None, "There are multiple paths forward..."),
                ],
                'interactions': {}
            },

            'education_reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You've made your decision about your education path."),
                    (None, "It wasn't an easy journey getting here."),
                    ("You", "Filling out that FAFSA was scary at first."),
                    ("You", "But knowing there are people who want to help..."),
                    (None, "You feel more confident about your future."),
                    (None, "The path won't be easy, but you're not alone."),
                    (None, "Part 5 Complete - Education Access"),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'visit_counselor':
            current.dynamic_description = "Meet with school counselor"
            current.progress_text = "Discuss your career options"

        elif current.id == 'career_matching':
            if self.career_matching_completed:
                current.dynamic_description = "Career matching complete!"
            else:
                current.dynamic_description = "Match careers with training"
                current.progress_text = "Drag careers to correct categories"

        elif current.id == 'education_path':
            current.dynamic_description = "Choose your education path"
            current.progress_text = "Make your final decision"

    def interact_with_object(self, name):
        """Handle interactions for Part 5 school"""
        print(f"[SCHOOL_P5] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'career_matching':
                self.launch_career_matching_game()
                return

            if trigger == 'education_choice':
                self.launch_education_choice()
                return

        # Mark interaction as completed
        self.completed_interactions.add(name)

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[SCHOOL_P5] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_career_matching_game(self):
        """Launch the career matching mini-game"""
        from part_5_education.activities.career_matching_game import CareerMatchingGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[SCHOOL_P5] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = CareerMatchingGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[SCHOOL_P5] Career matching game launched")

    def launch_education_choice(self):
        """Launch the education path choice dialogue"""
        from part_5_education.activities.choice_dialogue import ChoiceDialogueSystem

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[SCHOOL_P5] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialogueSystem(self.game.objective_manager)
            # Set to use the education_path scenario
            activity.set_scenario_by_id('education_path')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[SCHOOL_P5] Education choice dialogue launched")

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

        # Auto-launch career matching for career_matching phase
        if (self.current_objective_phase == 'career_matching' and
            not self.narrative_active and
            self.current_activity is None and
            not self.career_matching_completed):
            self.launch_career_matching_game()

        # Auto-launch education choice for education_path/campus_quad phase
        if (self.current_objective_phase in ['education_path', 'campus_quad'] and
            not self.narrative_active and
            self.current_activity is None and
            not self.education_path_chosen):
            self.launch_education_choice()

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[SCHOOL_P5] Activity completed/inactive - cleaning up")

                # Handle completion based on activity type
                if self.current_objective_phase == 'career_matching':
                    self.career_matching_completed = True
                elif self.current_objective_phase in ['campus_quad', 'education_path']:
                    self.education_path_chosen = True

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[SCHOOL_P5] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[SCHOOL_P5] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw school interior with activity overlay"""
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
        """Override to properly handle school transitions"""
        print(f"[SCHOOL_P5] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P5]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[SCHOOL_P5] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[SCHOOL_P5] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this school
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in school, reinitialize for next phase
            print(f"[SCHOOL_P5] Next objective also at school: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            # Exit school
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'career_matching':
            print(f"[SCHOOL_P5] check_objective_complete: career_matching_completed={self.career_matching_completed}")
            return self.career_matching_completed

        if current.id in ['campus_quad', 'education_path']:
            return self.education_path_chosen

        # For interaction-based objectives
        if current.id == 'visit_counselor':
            return 'counselor_desk' in self.completed_interactions

        if current.id == 'advisor_meeting':
            return 'advisor_desk' in self.completed_interactions

        # For dialogue-only objectives, complete after dialogue ends
        if current.id in ['trade_school_unlock', 'resource_packet', 'education_reflection']:
            return not self.narrative_active

        return True

"""
School Interior for Part 3 - Legal System
Handles arrival at school and note-taking while distracted scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class SchoolPart3(NarrativeInterior):
    """School/Classroom with Part 3 legal system narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.notes_completed = False
        self.arrived_at_school = False

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

        print(f"[SCHOOL_P3] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P3]   current objective: {current.id if current else 'None'}")
        print(f"[SCHOOL_P3]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[SCHOOL_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[SCHOOL_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[SCHOOL_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'walk_to_school':
            # Arrival scene - just dialogue
            pass

        elif phase_id == 'class_distraction':
            # Note-taking with distractions
            interactions = self.narrative_content['class_distraction']['interactions']
            if 'take_notes' in interactions:
                self.add_interactive_object('take_notes', interactions['take_notes'])

    def load_narrative_content(self):
        """Load the school narrative content for Part 3"""
        return {
            'walk_to_school': {
                'npcs': [
                    {'name': 'Classmate', 'x': 5, 'y': 4},
                ],
                'dialogue_sequence': [
                    (None, "You arrive at school, exhausted and distracted."),
                    ("You", "I couldn't sleep last night. That court thing..."),
                    (None, "Your mind keeps racing through impossible options."),
                    (None, "Your phone buzzes. Another text from your boss."),
                    ("Boss", "(text) Don't forget - 7am shift tomorrow. MANDATORY."),
                    ("You", "Court is at 9am. Work is at 7am. Class is now."),
                    (None, "A classmate waves at you from across the hall."),
                    ("Classmate", "Hey! You look tired. Everything okay?"),
                    ("You", "Yeah, just... a lot going on. You know how it is."),
                    ("Classmate", "Totally. Hey, don't forget - exam next week!"),
                    ("You", "Right... the exam..."),
                    (None, "Another thing to worry about. Another ball to juggle."),
                    (None, "You take a seat as the professor begins."),
                ],
                'interactions': {}
            },

            'class_distraction': {
                'npcs': [
                    {'name': 'Professor', 'x': 8, 'y': 2},
                ],
                'dialogue_sequence': [
                    ("Professor", "Good morning, everyone. Today we'll cover Chapter 7."),
                    ("Professor", "Constitutional Rights - an important topic."),
                    (None, "You pull out your notebook, trying to focus."),
                    ("Professor", "The right to due process. The right to representation."),
                    (None, "Your phone vibrates in your pocket."),
                    ("You", "(thinking) Ignore it. Focus on class."),
                    ("Professor", "Pay attention - this will be on the exam."),
                    (None, "Another vibration. And another."),
                    ("You", "(thinking) I need to focus. But what about court?"),
                    (None, "The irony isn't lost on you - learning about legal rights"),
                    (None, "while your own legal problems threaten to consume you."),
                ],
                'interactions': {
                    'take_notes': {
                        'position': (6, 5),
                        'prompt': 'Try to take notes',
                        'trigger_activity': 'note_taking',
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on school progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'walk_to_school':
            current.dynamic_description = "Head to class"
            current.progress_text = "Try to focus despite everything"

        elif current.id == 'class_distraction':
            if not self.notes_completed:
                current.dynamic_description = "Take notes in class"
                current.progress_text = "Stay focused despite distractions"
            else:
                current.dynamic_description = "Class ending..."

    def end_narrative_sequence(self):
        """Override to properly handle school transitions"""
        print(f"")
        print(f"="*80)
        print(f"[SCHOOL_P3] *** end_narrative_sequence() CALLED ***")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P3]   current objective: {current.id if current else 'None'}")
        print(f"[SCHOOL_P3]   objective complete check: {self.check_objective_complete()}")
        print(f"="*80)

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[SCHOOL_P3] Objective not complete yet - waiting for interactions")
            return

        # Helper function for clean transitions
        def _complete_and_transition(from_phase, to_phase):
            print(f"[SCHOOL_P3] Completing {from_phase}, moving to {to_phase}")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.should_exit = False

            next_obj = self.game.objective_manager.get_current_objective()
            print(f"[SCHOOL_P3]   Next objective: {next_obj.id if next_obj else 'None'}")

            if next_obj and next_obj.id == to_phase:
                print(f"[SCHOOL_P3]   Auto-reloading for {to_phase}")
                self.enter()

        # Chain school objectives
        if current.id == 'walk_to_school':
            _complete_and_transition('walk_to_school', 'class_distraction')
        elif current.id == 'class_distraction':
            # Exit school after class - player goes to work next
            print("[SCHOOL_P3] Completing class_distraction, exiting school")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.active = False
        else:
            print(f"[SCHOOL_P3] Other objective, completing and exiting")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.should_exit = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'class_distraction':
            print(f"[SCHOOL_P3] check_objective_complete for {current.id}")
            print(f"[SCHOOL_P3]   notes_completed: {self.notes_completed}")
            return self.notes_completed

        # Get required interactions for current phase
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        required_interactions = set()
        for obj_name, obj_data in interactions.items():
            if obj_data.get('required', False):
                required_interactions.add(obj_name)

        print(f"[SCHOOL_P3] check_objective_complete for {current.id}")
        print(f"[SCHOOL_P3]   required: {required_interactions}")
        print(f"[SCHOOL_P3]   completed: {self.completed_interactions}")

        if required_interactions:
            completion_status = required_interactions.issubset(self.completed_interactions)
            return completion_status
        else:
            return True

    def launch_activity(self, activity_name):
        """Launch activity by name"""
        print(f"[SCHOOL_P3] Activity trigger: {activity_name}")

        if activity_name == 'note_taking':
            self.launch_note_taking_game()
        else:
            print(f"[SCHOOL_P3] Unknown activity: {activity_name}")

    def interact_with_object(self, name):
        """Handle school-specific interactions"""
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'walk_to_school'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'note_taking':
                self.launch_note_taking_game()
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            print(f"[SCHOOL_P3] Phase complete")
            self.end_narrative_sequence()

    def launch_note_taking_game(self):
        """Launch the note-taking mini-game"""
        from part_3_legal_system.activities.note_taking import NoteTakingGame

        if hasattr(self.game, 'objective_manager'):
            activity = NoteTakingGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def handle_event(self, event):
        """Handle events with activity priority"""
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.active = False
                    return
                self.current_activity.handle_key(event.key)
            return

        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            if self.current_activity.completed:
                if self.current_objective_phase == 'class_distraction':
                    self.notes_completed = True
                    results = self.current_activity.get_results()
                    stress_gained = results.get('stress', 0)
                    print(f"[SCHOOL_P3] Notes completed with stress: {stress_gained}")

                self.current_activity = None
                self.game.objective_manager.current_activity = None

                if self.check_objective_complete():
                    self.end_narrative_sequence()

    def draw(self, screen):
        """Draw school interior"""
        super().draw(screen)

        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return

        # Draw classroom ambiance
        if self.current_objective_phase == 'class_distraction':
            # Subtle stressed overlay when phone keeps buzzing
            if hasattr(self, 'current_activity') and self.current_activity:
                if hasattr(self.current_activity, 'distraction_level') and self.current_activity.distraction_level > 5:
                    overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                    overlay.set_alpha(20)
                    overlay.fill((255, 50, 50))  # Red stress tint
                    screen.blit(overlay, (0, 0))

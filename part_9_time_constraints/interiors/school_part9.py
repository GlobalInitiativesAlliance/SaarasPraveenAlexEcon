"""
School Interior for Part 9 - Conflicting Responsibilities
Handles teacher dialogue choice about court/midterm conflict
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class SchoolPart9(NarrativeInterior):
    """School with teacher choice narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.teacher_choice_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up school scene based on objective"""
        super().enter()

        print(f"[SCHOOL_P9] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P9]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[SCHOOL_P9]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[SCHOOL_P9]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[SCHOOL_P9]   Interactive objects: {list(self.interactive_objects.keys())}")

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        interactions = self.narrative_content.get(phase_id, {}).get('interactions', {})

        for name, data in interactions.items():
            self.add_interactive_object(name, data)

    def load_narrative_content(self):
        """Load the school narrative content for Part 9"""
        return {
            'teacher_choice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You arrive at school before your midterm."),
                    (None, "The court summons weighs heavy in your pocket."),
                    ("Teacher", "Good morning! Ready for the exam?"),
                    ("You", "(Should I tell them about the court date?)"),
                ],
                'interactions': {
                    'teacher': {
                        'position': (10, 4),
                        'prompt': 'Talk to teacher',
                        'trigger_activity': 'teacher_choice',
                        'required': True
                    }
                }
            },

            'teacher_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The consequence of your choice arrives."),
                    (None, "Either way, there's a cost to pay."),
                    ("You", "I did what I had to do."),
                    (None, "But did you have a real choice?"),
                ],
                'interactions': {}
            }
        }

    def interact_with_object(self, name):
        """Handle interactions for Part 9 school"""
        print(f"[SCHOOL_P9] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            self.completed_interactions.add(name)

            if trigger == 'teacher_choice':
                self.launch_teacher_choice()
                return
        else:
            self.completed_interactions.add(name)

        super().interact_with_object(name)

        if self.check_objective_complete():
            print(f"[SCHOOL_P9] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_teacher_choice(self):
        """Launch the teacher choice dialogue"""
        from part_9_time_constraints.activities.choice_dialogue_part9 import ChoiceDialoguePart9

        if self.current_activity and self.current_activity.active:
            return

        activity = ChoiceDialoguePart9()
        activity.set_scenario('teacher_choice')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[SCHOOL_P9] Teacher choice launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
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

        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Auto-launch teacher choice
        if self.current_objective_phase == 'teacher_choice':
            if (not self.narrative_active and
                self.current_activity is None and
                not self.teacher_choice_completed):
                self.launch_teacher_choice()

        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            if self.current_activity.completed or not self.current_activity.active:
                print(f"[SCHOOL_P9] Activity completed - cleaning up")

                if self.current_objective_phase == 'teacher_choice':
                    self.teacher_choice_completed = True

                self.current_activity = None
                self.game.objective_manager.current_activity = None

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

    def draw(self, screen):
        """Draw school interior with activity overlay"""
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            if hasattr(self.current_activity, 'render'):
                self.current_activity.render(screen)
            elif hasattr(self.current_activity, 'draw'):
                self.current_activity.draw(screen)
            return

        super().draw(screen)

    def end_narrative_sequence(self):
        """Handle school transitions"""
        print(f"[SCHOOL_P9] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[SCHOOL_P9] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[SCHOOL_P9] Next objective also at school: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'teacher_choice':
            return self.teacher_choice_completed

        # Dialogue-only objectives
        if current.id == 'teacher_consequence':
            return not self.narrative_active

        return True

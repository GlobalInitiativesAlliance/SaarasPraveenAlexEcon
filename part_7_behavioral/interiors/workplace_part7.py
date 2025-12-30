"""
Workplace Interior for Part 7 - Behavioral & Emotional Survival
Handles manager praise, self-sabotage response, and shift conflicts
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class WorkplacePart7(NarrativeInterior):
    """Workplace with behavioral survival narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.self_sabotage_completed = False
        self.shift_conflict_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Emotional state
        self.guilt_level = 0.0
        self.anxiety_level = 0.0

    def enter(self):
        """Override enter to set up workplace scene based on objective"""
        super().enter()

        print(f"[WORK_P7] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[WORK_P7]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[WORK_P7]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[WORK_P7]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[WORK_P7]   Interactive objects: {list(self.interactive_objects.keys())}")

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        interactions = self.narrative_content.get(phase_id, {}).get('interactions', {})

        for name, data in interactions.items():
            self.add_interactive_object(name, data)

    def load_narrative_content(self):
        """Load the workplace narrative content for Part 7"""
        return {
            'work_arrival': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You arrive at work."),
                    (None, "Your manager waves you over."),
                    ("Manager", "Hey, got a minute?"),
                ],
                'interactions': {
                    'manager': {
                        'position': (8, 6),
                        'prompt': 'Talk to manager',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'manager_praise': {
                'npcs': [],
                'dialogue_sequence': [
                    ("Manager", "I've been watching your work lately."),
                    ("Manager", "You're really stepping up."),
                    ("Manager", "Showing up on time, handling customers well."),
                    ("Manager", "Keep it up - you could go far here."),
                ],
                'interactions': {
                    'manager': {
                        'position': (8, 6),
                        'prompt': 'Listen to manager',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'self_sabotage': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "How do you respond to the praise?"),
                    ("You", "This feels... uncomfortable."),
                ],
                'interactions': {
                    'respond': {
                        'position': (8, 6),
                        'prompt': 'Respond to praise',
                        'trigger_activity': 'self_sabotage',
                        'required': True
                    }
                }
            },

            'shift_conflict': {
                'npcs': [],
                'dialogue_sequence': [
                    ("Manager", "Oh, one more thing."),
                    ("Manager", "Can you pick up an extra shift tomorrow?"),
                    ("Manager", "3pm to close. We're short-staffed."),
                    (None, "*You check your phone - your ILP meeting is at 4pm*"),
                    ("You", "Missing ILP could affect my benefits..."),
                ],
                'interactions': {
                    'decide': {
                        'position': (8, 6),
                        'prompt': 'Make a decision',
                        'trigger_activity': 'shift_conflict',
                        'required': True
                    }
                }
            },

            'shift_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Every choice has consequences."),
                    (None, "When you can't be in two places at once..."),
                    ("You", "Something always gets sacrificed."),
                ],
                'interactions': {}
            }
        }

    def interact_with_object(self, name):
        """Handle interactions for Part 7 workplace"""
        print(f"[WORK_P7] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            self.completed_interactions.add(name)

            if trigger == 'self_sabotage':
                self.launch_self_sabotage()
                return

            if trigger == 'shift_conflict':
                self.launch_shift_conflict()
                return
        else:
            self.completed_interactions.add(name)

        super().interact_with_object(name)

        if self.check_objective_complete():
            print(f"[WORK_P7] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_self_sabotage(self):
        """Launch the self-sabotage choice"""
        from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

        if self.current_activity and self.current_activity.active:
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialoguePart7()
            activity.set_scenario('self_sabotage')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[WORK_P7] Self sabotage choice launched")

    def launch_shift_conflict(self):
        """Launch the shift conflict choice"""
        from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

        if self.current_activity and self.current_activity.active:
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialoguePart7()
            activity.set_scenario('shift_conflict')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[WORK_P7] Shift conflict choice launched")

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

        # Auto-launch activities
        if (self.current_objective_phase == 'self_sabotage' and
            not self.narrative_active and
            self.current_activity is None and
            not self.self_sabotage_completed):
            self.launch_self_sabotage()

        if (self.current_objective_phase == 'shift_conflict' and
            not self.narrative_active and
            self.current_activity is None and
            not self.shift_conflict_completed):
            self.launch_shift_conflict()

        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            if self.current_activity.completed or not self.current_activity.active:
                print(f"[WORK_P7] Activity completed - cleaning up")

                from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

                if isinstance(self.current_activity, ChoiceDialoguePart7):
                    self.guilt_level = self.current_activity.guilt_level
                    self.anxiety_level = self.current_activity.anxiety_level

                    if self.current_objective_phase == 'self_sabotage':
                        self.self_sabotage_completed = True
                    elif self.current_objective_phase == 'shift_conflict':
                        self.shift_conflict_completed = True

                self.current_activity = None
                self.game.objective_manager.current_activity = None

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw workplace interior with activity overlay"""
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
        """Handle workplace transitions"""
        print(f"[WORK_P7] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[WORK_P7] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[WORK_P7] Next objective also at workplace: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'self_sabotage':
            return self.self_sabotage_completed

        if current.id == 'shift_conflict':
            return self.shift_conflict_completed

        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        for name, data in interactions.items():
            if data.get('required', False):
                if name not in self.completed_interactions:
                    return False

        if current.id == 'shift_consequence':
            return not self.narrative_active

        return True

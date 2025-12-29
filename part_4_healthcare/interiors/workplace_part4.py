"""
Burger Shop Workplace Interior for Part 4 - Healthcare
Handles work anxiety, breathing exercise, and work warning scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class WorkplacePart4(NarrativeInterior):
    """Burger Shop workplace with healthcare narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.breathing_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up workplace scene based on objective"""
        super().enter()

        print(f"[WORK_P4] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[WORK_P4]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[WORK_P4]   Phase changed!")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[WORK_P4]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'work_anxiety':
            # Arriving at work, anxiety building
            pass

        elif phase_id == 'breathing_game':
            # Breathing exercise mini-game
            interactions = self.narrative_content.get('breathing_game', {}).get('interactions', {})
            if 'do_breathing' in interactions:
                self.add_interactive_object('do_breathing', interactions['do_breathing'])

        elif phase_id == 'work_warning':
            # Manager warning scene
            pass

    def load_narrative_content(self):
        """Load the workplace narrative content for Part 4"""
        return {
            'work_anxiety': {
                'npcs': [
                    {'name': 'Manager', 'x': 6, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You arrive at work feeling the weight of everything."),
                    (None, "The insurance issues, the missed appointments..."),
                    ("You", "I can do this. Just focus on the job."),
                    ("Manager", "There you are! We're short-staffed today."),
                    ("Manager", "I need you on the grill. It's going to be busy."),
                    (None, "You feel your anxiety rising as orders start coming in."),
                    (None, "Your hands are shaking slightly."),
                ],
                'interactions': {}
            },

            'breathing_game': {
                'npcs': [
                    {'name': 'Manager', 'x': 6, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "The lunch rush is overwhelming."),
                    (None, "Orders are piling up. You feel your chest tightening."),
                    ("You", "I need to calm down or I'll mess up..."),
                    (None, "Remember the breathing exercises your therapist taught you."),
                ],
                'interactions': {
                    'do_breathing': {
                        'position': (8, 6),
                        'prompt': 'Do breathing exercises',
                        'trigger_activity': 'breathing_exercise',
                        'required': True
                    }
                }
            },

            'work_warning': {
                'npcs': [
                    {'name': 'Manager', 'x': 6, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Manager", "Hey, can I talk to you for a minute?"),
                    (None, "The manager pulls you aside from the grill."),
                    ("Manager", "I've noticed you've been struggling lately."),
                    ("Manager", "A couple of orders came out wrong during the rush."),
                    ("You", "I'm sorry, I've been dealing with some personal stuff..."),
                    ("Manager", "Look, I get it. But I need you focused here."),
                    ("Manager", "This is your first warning. Please try to do better."),
                    (None, "You nod, feeling the weight of everything pressing down."),
                    (None, "Between insurance, appointments, and now work..."),
                    (None, "It feels like everything is falling apart."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'work_anxiety':
            current.dynamic_description = "Get through your work shift"

        elif current.id == 'breathing_game':
            if self.breathing_completed:
                current.dynamic_description = "Anxiety managed!"
            else:
                current.dynamic_description = "Manage your anxiety"
                current.progress_text = "Press E to do breathing exercises"

        elif current.id == 'work_warning':
            current.dynamic_description = "Talk to your manager"

    def interact_with_object(self, name):
        """Handle interactions for Part 4 workplace"""
        print(f"[WORK_P4] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'breathing_exercise':
                self.launch_breathing_exercise()
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            print(f"[WORK_P4] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_breathing_exercise(self):
        """Launch the breathing exercise mini-game"""
        from part_4_healthcare.activities.breathing_exercise import BreathingExerciseGame

        if self.current_activity and self.current_activity.active:
            print("[WORK_P4] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            # Clear any stale activity_manager reference
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None

            activity = BreathingExerciseGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[WORK_P4] Breathing exercise launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.KEYUP:
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
                print(f"[WORK_P4] Activity completed - cleaning up")

                if self.current_objective_phase == 'breathing_game':
                    self.breathing_completed = True
                    # Check if failed or succeeded
                    if hasattr(self.current_activity, 'failed') and self.current_activity.failed:
                        print("[WORK_P4] Breathing exercise failed!")
                    else:
                        print("[WORK_P4] Breathing exercise completed!")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    self.game.objective_manager.activity_manager.current_activity = None
                print(f"[WORK_P4] All activities cleared")

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
            self.current_activity.draw(screen)
            return

        super().draw(screen)

    def end_narrative_sequence(self):
        """Handle workplace transitions"""
        print(f"[WORK_P4] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            print(f"[WORK_P4] Objective not complete yet")
            return

        print(f"[WORK_P4] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[WORK_P4] Next objective also at workplace: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'breathing_game':
            return self.breathing_completed

        if current.id in ['work_anxiety', 'work_warning']:
            return not self.narrative_active

        return True

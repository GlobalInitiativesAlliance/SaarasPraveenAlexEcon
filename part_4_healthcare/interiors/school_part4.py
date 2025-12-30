"""
School Interior for Part 4 - Healthcare
Handles appointment conflict and bus route scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class SchoolPart4(NarrativeInterior):
    """School with healthcare appointment conflict narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.bus_route_completed = False

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

        print(f"[SCHOOL_P4] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P4]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[SCHOOL_P4]   Phase changed!")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[SCHOOL_P4]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'appointment_conflict':
            # Appointment reminder during school
            pass

        elif phase_id == 'catch_bus':
            # Bus route mini-game
            interactions = self.narrative_content.get('catch_bus', {}).get('interactions', {})
            if 'check_bus' in interactions:
                self.add_interactive_object('check_bus', interactions['check_bus'])

    def load_narrative_content(self):
        """Load the school narrative content for Part 4"""
        return {
            'appointment_conflict': {
                'npcs': [
                    {'name': 'Teacher', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You're in the middle of class when your phone buzzes."),
                    (None, "It's a reminder: therapy appointment in 45 minutes."),
                    ("You", "(thinking) The appointment is across town..."),
                    ("You", "(thinking) If I leave now, I might make it."),
                    ("Teacher", "Is everything okay? You look distracted."),
                    ("You", "I... I have a medical appointment. I forgot it was today."),
                    ("Teacher", "You should have told me earlier. You'll miss the quiz."),
                    (None, "You grab your things and rush out, anxiety building."),
                    (None, "Now you need to figure out how to get there in time."),
                ],
                'interactions': {}
            },

            'catch_bus': {
                'npcs': [
                    {'name': 'Bus Driver', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You rush to the bus stop outside school."),
                    (None, "You have 20 seconds to figure out which bus to take!"),
                    (None, "The clinic is downtown - which route gets you there fastest?"),
                ],
                'interactions': {
                    'check_bus': {
                        'position': (10, 6),
                        'prompt': 'Check bus routes',
                        'trigger_activity': 'bus_route',
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'appointment_conflict':
            current.dynamic_description = "Deal with schedule conflict"

        elif current.id == 'catch_bus':
            if self.bus_route_completed:
                current.dynamic_description = "Bus route found!"
            else:
                current.dynamic_description = "Find the right bus"
                current.progress_text = "Press E to check routes"

    def interact_with_object(self, name):
        """Handle interactions for Part 4 school"""
        print(f"[SCHOOL_P4] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'bus_route':
                self.launch_bus_route_game()
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            print(f"[SCHOOL_P4] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_bus_route_game(self):
        """Launch the bus route selection mini-game"""
        from part_4_healthcare.activities.bus_route_game import BusRouteGame

        if self.current_activity and self.current_activity.active:
            print("[SCHOOL_P4] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None

            activity = BusRouteGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[SCHOOL_P4] Bus route game launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
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
                print(f"[SCHOOL_P4] Activity completed - cleaning up")

                if self.current_objective_phase == 'catch_bus':
                    self.bus_route_completed = True
                    print("[SCHOOL_P4] Bus route completed!")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    self.game.objective_manager.activity_manager.current_activity = None
                print(f"[SCHOOL_P4] All activities cleared")

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw school interior with activity overlay"""
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            self.current_activity.draw(screen)
            return

        super().draw(screen)

    def end_narrative_sequence(self):
        """Handle school transitions"""
        print(f"[SCHOOL_P4] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            print(f"[SCHOOL_P4] Objective not complete yet")
            return

        print(f"[SCHOOL_P4] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[SCHOOL_P4] Next objective also at school: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'catch_bus':
            return self.bus_route_completed

        if current.id == 'appointment_conflict':
            return not self.narrative_active

        return True

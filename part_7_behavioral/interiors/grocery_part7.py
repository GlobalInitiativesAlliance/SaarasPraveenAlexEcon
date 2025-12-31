"""
Grocery Store Interior for Part 7 - Behavioral & Emotional Survival
Handles fruit vs ramen choice and food consequence
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class GroceryPart7(NarrativeInterior):
    """Grocery store with food choice narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.food_choice_completed = False

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
        """Override enter to set up grocery scene based on objective"""
        super().enter()

        print(f"[GROCERY_P7] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[GROCERY_P7]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[GROCERY_P7]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[GROCERY_P7]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[GROCERY_P7]   Interactive objects: {list(self.interactive_objects.keys())}")

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        interactions = self.narrative_content.get(phase_id, {}).get('interactions', {})

        for name, data in interactions.items():
            self.add_interactive_object(name, data)

    def load_narrative_content(self):
        """Load the grocery store narrative content for Part 7"""
        return {
            'grocery_trip': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You enter the grocery store."),
                    (None, "Budget: $12 for the week."),
                    (None, "The fresh produce aisle looks expensive."),
                    ("You", "The instant food section looks... realistic."),
                ],
                'interactions': {
                    'entrance': {
                        'position': (10, 12),
                        'prompt': 'Enter store',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'food_choice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stand between two aisles."),
                    (None, "Fresh fruit: $8 for a small selection"),
                    (None, "Instant ramen: $2 for a 6-pack"),
                    ("You", "My stomach growls. My wallet sighs."),
                ],
                'interactions': {
                    'food_display': {
                        'position': (10, 8),
                        'prompt': 'Make your choice',
                        'trigger_activity': 'food_choice',
                        'required': True
                    }
                }
            },

            'food_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You made your choice."),
                    (None, "Another week of making do."),
                    ("You", "Food is fuel. Budget is reality."),
                ],
                'interactions': {
                    'checkout': {
                        'position': (10, 12),
                        'prompt': 'Checkout',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            }
        }

    def interact_with_object(self, name):
        """Handle interactions for Part 7 grocery"""
        print(f"[GROCERY_P7] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            self.completed_interactions.add(name)

            if trigger == 'food_choice':
                self.launch_food_choice()
                return
        else:
            self.completed_interactions.add(name)

        super().interact_with_object(name)

        if self.check_objective_complete():
            print(f"[GROCERY_P7] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_food_choice(self):
        """Launch the food choice dialogue"""
        from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

        if self.current_activity and self.current_activity.active:
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialoguePart7()
            activity.set_scenario('food_choice')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[GROCERY_P7] Food choice launched")

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
        if (self.current_objective_phase == 'food_choice' and
            not self.narrative_active and
            self.current_activity is None and
            not self.food_choice_completed):
            self.launch_food_choice()

        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            if self.current_activity.completed or not self.current_activity.active:
                print(f"[GROCERY_P7] Activity completed - cleaning up")

                from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

                if isinstance(self.current_activity, ChoiceDialoguePart7):
                    self.guilt_level = self.current_activity.guilt_level
                    self.anxiety_level = self.current_activity.anxiety_level
                    self.food_choice_completed = True

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
        """Draw grocery interior with activity overlay"""
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
        """Handle grocery transitions"""
        print(f"[GROCERY_P7] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[GROCERY_P7] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[GROCERY_P7] Next objective also at grocery: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'food_choice':
            return self.food_choice_completed

        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        for name, data in interactions.items():
            if data.get('required', False):
                if name not in self.completed_interactions:
                    return False

        if current.id == 'food_consequence':
            return not self.narrative_active

        return True

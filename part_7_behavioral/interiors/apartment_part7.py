"""
Apartment Interior for Part 7 - Behavioral & Emotional Survival
Handles paycheck, bill paying, spending choices, task overwhelm, and final reflection
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class ApartmentPart7(NarrativeInterior):
    """Apartment with behavioral survival narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.bill_game_completed = False
        self.spending_choice_completed = False
        self.task_game_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Emotional state (persists through Part 7)
        self.guilt_level = 0.0
        self.anxiety_level = 0.0

    def enter(self):
        """Override enter to set up apartment scene based on objective"""
        super().enter()

        print(f"[APT_P7] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P7]   current objective: {current.id if current else 'None'}")
        print(f"[APT_P7]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[APT_P7]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[APT_P7]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[APT_P7]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        interactions = self.narrative_content.get(phase_id, {}).get('interactions', {})

        for name, data in interactions.items():
            self.add_interactive_object(name, data)

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 7"""
        return {
            'paycheck_arrival': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "A paycheck envelope sits on the table."),
                    (None, "Your bi-weekly pay: $400.00"),
                    ("You", "Finally. Let me see what's left after bills..."),
                ],
                'interactions': {
                    'paycheck': {
                        'position': (8, 6),
                        'prompt': 'Check paycheck',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'bill_paying_game': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to pay your bills."),
                    ("You", "Let's see what's due..."),
                ],
                'interactions': {
                    'desk': {
                        'position': (8, 6),
                        'prompt': 'Pay bills',
                        'trigger_activity': 'bill_game',
                        'required': True
                    }
                }
            },

            'leftover_money': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "After all bills are paid..."),
                    (None, "Remaining balance: $40.00"),
                    (None, "This needs to last two weeks."),
                    ("You", "What am I going to do with this?"),
                ],
                'interactions': {
                    'wallet': {
                        'position': (8, 6),
                        'prompt': 'Check remaining balance',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'spending_choice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at the $40."),
                    ("You", "I could save it... or treat myself..."),
                    (None, "Every decision feels weighted."),
                ],
                'interactions': {
                    'money': {
                        'position': (8, 6),
                        'prompt': 'Decide what to do',
                        'trigger_activity': 'spending_choice',
                        'required': True
                    }
                }
            },

            'spending_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The weight of every small decision..."),
                    (None, "When you're on your own, everything costs something."),
                    ("You", "Not just money - mental energy too."),
                    (None, "You feel the guilt. Or the anxiety. Or both."),
                ],
                'interactions': {}
            },

            'return_home': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You return home exhausted from work."),
                    ("You", "Another long day."),
                    (None, "But there's still more to do."),
                ],
                'interactions': {
                    'door': {
                        'position': (8, 9),
                        'prompt': 'Enter apartment',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'college_reminder': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "*Phone buzzes*"),
                    (None, "REMINDER: College application due in 5 days"),
                    ("You", "I've been meaning to work on that..."),
                    (None, "But when? There's always something else."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 6),
                        'prompt': 'Check phone',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'floating_tasks': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Everything hits you at once:"),
                    (None, "- College application"),
                    (None, "- Work tomorrow"),
                    (None, "- Pay electric"),
                    (None, "- Groceries"),
                    (None, "- Call case worker"),
                    (None, "- Laundry"),
                    (None, "- Clean apartment"),
                    ("You", "How do I choose what matters?"),
                ],
                'interactions': {
                    'list': {
                        'position': (8, 6),
                        'prompt': 'Look at task list',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'task_game': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to prioritize."),
                    ("You", "What comes first?"),
                ],
                'interactions': {
                    'desk': {
                        'position': (8, 6),
                        'prompt': 'Prioritize tasks',
                        'trigger_activity': 'task_game',
                        'required': True
                    }
                }
            },

            'task_result': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "No matter what you choose, something gets dropped."),
                    (None, "That's the reality of survival mode."),
                    ("You", "I can only do so much alone."),
                ],
                'interactions': {}
            },

            'final_return': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Home after the grocery store."),
                    (None, "Another day of decisions made."),
                    ("You", "Some good, some just... necessary."),
                ],
                'interactions': {
                    'door': {
                        'position': (8, 9),
                        'prompt': 'Enter apartment',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'survival_reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit on the edge of your bed."),
                    (None, "Today was full of small decisions."),
                    ("You", "Save or spend. Work or meeting. Health or budget."),
                    (None, "None of them were easy."),
                    (None, "This is survival mode."),
                    (None, "Every choice costs something."),
                    ("You", "And I'm learning to live with that weight."),
                    (None, "..."),
                    (None, "Part 7 Complete - Behavioral & Emotional Survival"),
                ],
                'interactions': {
                    'bed': {
                        'position': (4, 8),
                        'prompt': 'Sit and reflect',
                        'trigger_activity': None,
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

        if current.id == 'bill_paying_game':
            if self.bill_game_completed:
                current.dynamic_description = "Bills paid"
            else:
                current.dynamic_description = "Pay your bills"
                current.progress_text = "Drag bills to paid pile"

        elif current.id == 'spending_choice':
            if self.spending_choice_completed:
                current.dynamic_description = "Decision made"
            else:
                current.dynamic_description = "Decide how to spend"
                current.progress_text = "Save, spend, or split?"

        elif current.id == 'task_game':
            if self.task_game_completed:
                current.dynamic_description = "Tasks prioritized"
            else:
                current.dynamic_description = "Prioritize your tasks"
                current.progress_text = "30 seconds to decide"

    def interact_with_object(self, name):
        """Handle interactions for Part 7 apartment"""
        print(f"[APT_P7] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            # Mark interaction as completed
            self.completed_interactions.add(name)

            if trigger == 'bill_game':
                self.launch_bill_game()
                return

            if trigger == 'spending_choice':
                self.launch_spending_choice()
                return

            if trigger == 'task_game':
                self.launch_task_game()
                return
        else:
            # Mark interaction as completed for non-activity interactions
            self.completed_interactions.add(name)

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[APT_P7] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_bill_game(self):
        """Launch the bill paying mini-game"""
        from part_7_behavioral.activities.bill_paying_game import BillPayingGame

        if self.current_activity and self.current_activity.active:
            print("[APT_P7] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = BillPayingGame()
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P7] Bill paying game launched")

    def launch_spending_choice(self):
        """Launch the spending choice dialogue"""
        from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

        if self.current_activity and self.current_activity.active:
            print("[APT_P7] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialoguePart7()
            activity.set_scenario('spending_choice')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P7] Spending choice launched")

    def launch_task_game(self):
        """Launch the task prioritization game"""
        from part_7_behavioral.activities.task_prioritization_game import TaskPrioritizationGame

        if self.current_activity and self.current_activity.active:
            print("[APT_P7] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = TaskPrioritizationGame()
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P7] Task prioritization game launched")

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

        # Auto-launch activities for their respective phases
        if (self.current_objective_phase == 'bill_paying_game' and
            not self.narrative_active and
            self.current_activity is None and
            not self.bill_game_completed):
            self.launch_bill_game()

        if (self.current_objective_phase == 'spending_choice' and
            not self.narrative_active and
            self.current_activity is None and
            not self.spending_choice_completed):
            self.launch_spending_choice()

        if (self.current_objective_phase == 'task_game' and
            not self.narrative_active and
            self.current_activity is None and
            not self.task_game_completed):
            self.launch_task_game()

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[APT_P7] Activity completed/inactive - cleaning up")

                # Handle completion based on activity TYPE
                from part_7_behavioral.activities.bill_paying_game import BillPayingGame
                from part_7_behavioral.activities.task_prioritization_game import TaskPrioritizationGame
                from part_7_behavioral.activities.choice_dialogue_part7 import ChoiceDialoguePart7

                if isinstance(self.current_activity, BillPayingGame):
                    self.bill_game_completed = True
                    print(f"[APT_P7] Bill game marked complete")
                elif isinstance(self.current_activity, TaskPrioritizationGame):
                    self.task_game_completed = True
                    print(f"[APT_P7] Task game marked complete")
                elif isinstance(self.current_activity, ChoiceDialoguePart7):
                    # Transfer emotional state
                    self.guilt_level = self.current_activity.guilt_level
                    self.anxiety_level = self.current_activity.anxiety_level
                    self.spending_choice_completed = True
                    print(f"[APT_P7] Spending choice marked complete (guilt={self.guilt_level}, anxiety={self.anxiety_level})")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[APT_P7] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[APT_P7] Objective complete - calling end_narrative_sequence")
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
            # Draw emotional meters on top
            self.render_emotional_meters(screen)
            return

        # Draw base interior
        super().draw(screen)

        # Draw emotional meters overlay
        self.render_emotional_meters(screen)

    def render_emotional_meters(self, screen):
        """Render persistent guilt and anxiety meters"""
        meter_width = 120
        meter_height = 16
        y = 60

        # Only show if there's some value
        if self.guilt_level > 0 or self.anxiety_level > 0:
            # Guilt meter
            guilt_rect = pygame.Rect(screen.get_width() - 140, y, meter_width, meter_height)
            pygame.draw.rect(screen, (60, 60, 70), guilt_rect)
            if self.guilt_level > 0:
                fill_width = int(self.guilt_level * meter_width)
                fill_rect = pygame.Rect(guilt_rect.x, guilt_rect.y, fill_width, meter_height)
                pygame.draw.rect(screen, (180, 100, 180), fill_rect)
            pygame.draw.rect(screen, (100, 100, 110), guilt_rect, 1)

            label_font = pygame.font.Font(None, 16)
            guilt_label = label_font.render("Guilt", True, (180, 180, 190))
            screen.blit(guilt_label, (guilt_rect.x, guilt_rect.y - 14))

            # Anxiety meter
            y += 40
            anxiety_rect = pygame.Rect(screen.get_width() - 140, y, meter_width, meter_height)
            pygame.draw.rect(screen, (60, 60, 70), anxiety_rect)
            if self.anxiety_level > 0:
                fill_width = int(self.anxiety_level * meter_width)
                fill_rect = pygame.Rect(anxiety_rect.x, anxiety_rect.y, fill_width, meter_height)
                pygame.draw.rect(screen, (200, 150, 100), fill_rect)
            pygame.draw.rect(screen, (100, 100, 110), anxiety_rect, 1)

            anxiety_label = label_font.render("Anxiety", True, (180, 180, 190))
            screen.blit(anxiety_label, (anxiety_rect.x, anxiety_rect.y - 14))

    def end_narrative_sequence(self):
        """Override to properly handle apartment transitions"""
        print(f"[APT_P7] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P7]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[APT_P7] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[APT_P7] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this apartment
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in apartment, reinitialize for next phase
            print(f"[APT_P7] Next objective also at apartment: {next_obj.id}")
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
        if current.id == 'bill_paying_game':
            return self.bill_game_completed

        if current.id == 'spending_choice':
            return self.spending_choice_completed

        if current.id == 'task_game':
            return self.task_game_completed

        # For interaction-based objectives
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        for name, data in interactions.items():
            if data.get('required', False):
                if name not in self.completed_interactions:
                    return False

        # For dialogue-only objectives, complete after dialogue ends
        dialogue_only = [
            'spending_consequence', 'task_result'
        ]
        if current.id in dialogue_only:
            return not self.narrative_active

        return True

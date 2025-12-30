"""
Bedroom Interior for Part 8 - Lack of Guidance/Mentorship
Handles future planning, phone notifications, panic, balance puzzle, sleep/dreams
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class BedroomPart8(NarrativeInterior):
    """Bedroom with mentorship narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.priority_completed = False
        self.choice_completed = False
        self.balance_completed = False
        self.dream_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Panic level (visual indicator)
        self.panic_level = 0.0

    def enter(self):
        """Override enter to set up bedroom scene based on objective"""
        super().enter()

        print(f"[BEDROOM_P8] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[BEDROOM_P8]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[BEDROOM_P8]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[BEDROOM_P8]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[BEDROOM_P8]   Interactive objects: {list(self.interactive_objects.keys())}")

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        interactions = self.narrative_content.get(phase_id, {}).get('interactions', {})

        for name, data in interactions.items():
            self.add_interactive_object(name, data)

    def load_narrative_content(self):
        """Load the bedroom narrative content for Part 8"""
        return {
            'future_planning': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your laptop screen glows in the dim room."),
                    (None, "'Future Planning Worksheet' - open and waiting."),
                    ("You", "I need to figure out my future..."),
                ],
                'interactions': {
                    'laptop': {
                        'position': (8, 5),
                        'prompt': 'Open Future Planning',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'priority_puzzle': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The worksheet asks you to prioritize:"),
                    (None, "College, Job, Trade School, Gap Year"),
                    ("You", "Which matters most? I don't know..."),
                ],
                'interactions': {
                    'laptop': {
                        'position': (8, 5),
                        'prompt': 'Set priorities',
                        'trigger_activity': 'priority_puzzle',
                        'required': True
                    }
                }
            },

            'incomplete_plan': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The screen displays: 'Incomplete Plan'"),
                    (None, "No feedback. No suggestions. No help."),
                    ("You", "That's it? No guidance at all?"),
                ],
                'interactions': {}
            },

            'no_advisor': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "A pop-up appears:"),
                    (None, "'No advisor assigned.'"),
                    (None, "'Please contact your ILP case manager.'"),
                    ("You", "Who's supposed to help me with this?"),
                ],
                'interactions': {}
            },

            'phone_notifications': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "*Phone buzzes twice*"),
                    (None, "Text 1: 'Interview scheduled for 2pm today - don't be late!'"),
                    (None, "Text 2: 'REMINDER: College application deadline TODAY'"),
                    ("You", "Wait... I can't do both of these!"),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Check phone',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'impossible_choice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at the two notifications."),
                    ("You", "This is impossible. I have to choose."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Make your choice',
                        'trigger_activity': 'impossible_choice',
                        'required': True
                    }
                }
            },

            'choice_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You made a choice."),
                    (None, "But whatever you chose, you lost the other option."),
                    ("You", "There was no way to win."),
                    (None, "This is what happens without support."),
                ],
                'interactions': {}
            },

            'panic_meter': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "*Heart racing*"),
                    (None, "NO SAFETY NET AVAILABLE"),
                    ("You", "What if I made the wrong choice?"),
                    (None, "What if there's no coming back from this?"),
                ],
                'interactions': {}
            },

            'call_ilp': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You dial your ILP officer's number."),
                    ("You", "Please pick up... I need help..."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Call ILP officer',
                        'trigger_activity': 'ilp_response',
                        'required': True
                    }
                }
            },

            'no_decision_help': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The call ends."),
                    (None, "'I can't decide for you. It's your choice.'"),
                    ("You", "But I don't know how to decide..."),
                    (None, "No one taught you. No one showed you."),
                ],
                'interactions': {}
            },

            'balance_puzzle': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit with a piece of paper."),
                    (None, "Drawing a balance scale..."),
                    ("You", "Income... Education... Housing..."),
                    (None, "How do you balance what you can't control?"),
                ],
                'interactions': {
                    'desk': {
                        'position': (6, 5),
                        'prompt': 'Try to balance',
                        'trigger_activity': 'balance_puzzle',
                        'required': True
                    }
                }
            },

            'puzzle_result': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The balance failed."),
                    (None, "'Future Plan Collapsed'"),
                    ("You", "I needed someone to help me see this..."),
                    (None, "Without guidance, the weight was too much."),
                ],
                'interactions': {}
            },

            'sleep': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Exhausted. Overwhelmed. Alone."),
                    ("You", "Maybe sleep will help..."),
                    (None, "You close your eyes..."),
                ],
                'interactions': {
                    'bed': {
                        'position': (4, 8),
                        'prompt': 'Go to sleep',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'dream_doors': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You dream of a dark hallway."),
                    (None, "Four doors stand before you."),
                    (None, "Work. School. Homelessness. Unknown."),
                    ("You", "Which door do I choose?"),
                ],
                'interactions': {
                    'dream': {
                        'position': (8, 6),
                        'prompt': 'Choose a door',
                        'trigger_activity': 'dream_doors',
                        'required': True
                    }
                }
            },

            'wake_up': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You wake up."),
                    (None, "The dream fades, but the feeling remains."),
                    (None, "You made a decision..."),
                    (None, "But without guidance, your long-term path remains uncertain."),
                    ("You", "I walked through a door I couldn't see beyond."),
                    (None, "That's what happens when no one shows you the way."),
                    (None, "Part 8 Complete - Lack of Guidance/Mentorship"),
                ],
                'interactions': {}
            }
        }

    def interact_with_object(self, name):
        """Handle interactions for Part 8 bedroom"""
        print(f"[BEDROOM_P8] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            self.completed_interactions.add(name)

            if trigger == 'priority_puzzle':
                self.launch_priority_puzzle()
                return

            if trigger == 'impossible_choice':
                self.launch_impossible_choice()
                return

            if trigger == 'ilp_response':
                self.launch_ilp_response()
                return

            if trigger == 'balance_puzzle':
                self.launch_balance_puzzle()
                return

            if trigger == 'dream_doors':
                self.launch_dream_doors()
                return
        else:
            self.completed_interactions.add(name)

        super().interact_with_object(name)

        if self.check_objective_complete():
            print(f"[BEDROOM_P8] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_priority_puzzle(self):
        """Launch the priority ordering puzzle"""
        from part_8_mentorship.activities.priority_puzzle import PriorityPuzzle

        if self.current_activity and self.current_activity.active:
            return

        activity = PriorityPuzzle()
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[BEDROOM_P8] Priority puzzle launched")

    def launch_impossible_choice(self):
        """Launch the impossible choice dialogue"""
        from part_8_mentorship.activities.choice_dialogue_part8 import ChoiceDialoguePart8

        if self.current_activity and self.current_activity.active:
            return

        activity = ChoiceDialoguePart8()
        activity.set_scenario('impossible_choice')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[BEDROOM_P8] Impossible choice launched")

    def launch_ilp_response(self):
        """Launch the ILP response dialogue"""
        from part_8_mentorship.activities.choice_dialogue_part8 import ChoiceDialoguePart8

        if self.current_activity and self.current_activity.active:
            return

        activity = ChoiceDialoguePart8()
        activity.set_scenario('ilp_response')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[BEDROOM_P8] ILP response launched")

    def launch_balance_puzzle(self):
        """Launch the balance scale puzzle"""
        from part_8_mentorship.activities.balance_puzzle import BalancePuzzle

        if self.current_activity and self.current_activity.active:
            return

        activity = BalancePuzzle()
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[BEDROOM_P8] Balance puzzle launched")

    def launch_dream_doors(self):
        """Launch the dream doors sequence"""
        from part_8_mentorship.activities.dream_doors import DreamDoors

        if self.current_activity and self.current_activity.active:
            return

        activity = DreamDoors()
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[BEDROOM_P8] Dream doors launched")

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
        activity_phases = {
            'priority_puzzle': (self.launch_priority_puzzle, 'priority_completed'),
            'impossible_choice': (self.launch_impossible_choice, 'choice_completed'),
            'balance_puzzle': (self.launch_balance_puzzle, 'balance_completed'),
            'dream_doors': (self.launch_dream_doors, 'dream_completed'),
        }

        if self.current_objective_phase in activity_phases:
            launch_func, completed_attr = activity_phases[self.current_objective_phase]
            if (not self.narrative_active and
                self.current_activity is None and
                not getattr(self, completed_attr)):
                launch_func()

        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            if self.current_activity.completed or not self.current_activity.active:
                print(f"[BEDROOM_P8] Activity completed - cleaning up")

                # Mark completion based on phase
                if self.current_objective_phase == 'priority_puzzle':
                    self.priority_completed = True
                elif self.current_objective_phase in ['impossible_choice', 'call_ilp']:
                    self.choice_completed = True
                elif self.current_objective_phase == 'balance_puzzle':
                    self.balance_completed = True
                elif self.current_objective_phase == 'dream_doors':
                    self.dream_completed = True

                self.current_activity = None
                self.game.objective_manager.current_activity = None

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

    def draw(self, screen):
        """Draw bedroom interior with activity overlay"""
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            if hasattr(self.current_activity, 'render'):
                self.current_activity.render(screen)
            elif hasattr(self.current_activity, 'draw'):
                self.current_activity.draw(screen)
            self.render_panic_meter(screen)
            return

        super().draw(screen)
        self.render_panic_meter(screen)

    def render_panic_meter(self, screen):
        """Render panic meter when applicable"""
        if self.current_objective_phase in ['panic_meter', 'balance_puzzle', 'impossible_choice']:
            meter_width = 150
            meter_height = 20
            x = screen.get_width() - 170
            y = 60

            # Background
            bg_rect = pygame.Rect(x, y, meter_width, meter_height)
            pygame.draw.rect(screen, (60, 40, 40), bg_rect)

            # Fill based on panic level
            if self.panic_level > 0:
                fill_width = int(self.panic_level * meter_width)
                fill_rect = pygame.Rect(x, y, fill_width, meter_height)
                pygame.draw.rect(screen, (200, 80, 80), fill_rect)

            pygame.draw.rect(screen, (120, 80, 80), bg_rect, 1)

            # Label
            font = pygame.font.Font(None, 16)
            label = font.render("PANIC", True, (200, 150, 150))
            screen.blit(label, (x, y - 14))

            # Increase panic during certain phases
            self.panic_level = min(1.0, self.panic_level + 0.002)

    def end_narrative_sequence(self):
        """Handle bedroom transitions"""
        print(f"[BEDROOM_P8] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[BEDROOM_P8] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[BEDROOM_P8] Next objective also at bedroom: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Activity-based objectives
        if current.id == 'priority_puzzle':
            return self.priority_completed

        if current.id in ['impossible_choice', 'call_ilp']:
            return self.choice_completed

        if current.id == 'balance_puzzle':
            return self.balance_completed

        if current.id == 'dream_doors':
            return self.dream_completed

        # Interaction-based objectives
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        for name, data in interactions.items():
            if data.get('required', False):
                if name not in self.completed_interactions:
                    return False

        # Dialogue-only objectives
        dialogue_only = [
            'incomplete_plan', 'no_advisor', 'choice_consequence',
            'panic_meter', 'no_decision_help', 'puzzle_result', 'wake_up'
        ]
        if current.id in dialogue_only:
            return not self.narrative_active

        return True

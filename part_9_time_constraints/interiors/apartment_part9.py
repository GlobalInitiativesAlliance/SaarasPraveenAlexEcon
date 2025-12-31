"""
Apartment Interior for Part 9 - Conflicting Responsibilities & Time Constraints
Handles phone notifications, calendar conflicts, mailbox, and stress overload
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class ApartmentPart9(NarrativeInterior):
    """Apartment with time conflict narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.calendar_completed = False
        self.mailbox_completed = False
        self.first_choice_completed = False
        self.second_choice_completed = False
        self.stress_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Stress level (visual indicator)
        self.stress_level = 0.0

    def enter(self):
        """Override enter to set up apartment scene based on objective"""
        super().enter()

        print(f"[APT_P9] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P9]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[APT_P9]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[APT_P9]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[APT_P9]   Interactive objects: {list(self.interactive_objects.keys())}")

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        interactions = self.narrative_content.get(phase_id, {}).get('interactions', {})

        for name, data in interactions.items():
            self.add_interactive_object(name, data)

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 9"""
        return {
            'phone_buzzes': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone buzzes three times in quick succession."),
                    (None, "*buzz* *buzz* *buzz*"),
                    ("You", "What now?"),
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

            'calendar_conflict': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Three notifications demand your attention:"),
                    (None, "1. Work shift at 3pm - need the money"),
                    (None, "2. Mandatory program meeting at 3pm - benefits depend on it"),
                    (None, "3. Therapy session at 3:30pm - mental health"),
                    ("You", "Let me check my calendar..."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Open calendar',
                        'trigger_activity': 'calendar_conflict',
                        'required': True
                    }
                }
            },

            'overlap_warning': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The calendar flashes RED."),
                    (None, "All three events overlap."),
                    ("You", "This can't be right..."),
                    (None, "But it is. There's no way to attend all three."),
                ],
                'interactions': {}
            },

            'choose_one': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "A pop-up appears on your screen:"),
                    (None, "'You cannot attend everything.'"),
                    (None, "'Choose one.'"),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Make your choice',
                        'trigger_activity': 'choose_one',
                        'required': True
                    }
                }
            },

            'first_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You made your choice."),
                    (None, "Whatever you picked, you lost the others."),
                    ("You", "I had no real choice."),
                    (None, "The system doesn't care."),
                ],
                'interactions': {}
            },

            'next_morning': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "THE NEXT MORNING"),
                    (None, "You wake up to the sound of the mail slot."),
                    ("You", "More mail..."),
                ],
                'interactions': {
                    'door': {
                        'position': (4, 8),
                        'prompt': 'Check mailbox',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'mailbox_letter': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sort through the mail."),
                    (None, "Bills, junk, more bills..."),
                    ("You", "What's this official-looking one?"),
                ],
                'interactions': {
                    'mailbox': {
                        'position': (4, 8),
                        'prompt': 'Open mail',
                        'trigger_activity': 'mailbox_letter',
                        'required': True
                    }
                }
            },

            'court_school_conflict': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The court summons stares back at you."),
                    (None, "Date: During your midterm exam week."),
                    (None, "Time: 10:00 AM - exactly when your test starts."),
                    ("You", "They can't seriously expect me to skip my midterm..."),
                    (None, "But the court doesn't care about your schedule."),
                ],
                'interactions': {}
            },

            'try_reschedule': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You try to reschedule the court date online."),
                    (None, "Loading... loading..."),
                    ("You", "Come on, there has to be another option..."),
                ],
                'interactions': {
                    'laptop': {
                        'position': (8, 5),
                        'prompt': 'Reschedule online',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'no_appointments': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The website displays:"),
                    (None, "'No alternate appointments available.'"),
                    (None, "'Your appearance is MANDATORY.'"),
                    ("You", "Of course there's no other option."),
                    (None, "The system never offers flexibility."),
                ],
                'interactions': {}
            },

            'case_manager_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "A new notification appears:"),
                    (None, "'Your housing case manager has scheduled a check-in.'"),
                    (None, "'Tomorrow at 2:00 PM'"),
                    (None, "'Attendance REQUIRED to maintain housing status.'"),
                    ("You", "Tomorrow at 2pm... let me check my work schedule."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Check notification',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'work_conflict_again': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You check your work schedule."),
                    (None, "Tomorrow: 2:00 PM - 10:00 PM"),
                    ("You", "No. No, no, no..."),
                    (None, "Work shift starts at exactly 2pm."),
                    (None, "Direct conflict. Again."),
                ],
                'interactions': {}
            },

            'housing_vs_work': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at both notifications."),
                    (None, "Case manager at 2pm: housing depends on it."),
                    (None, "Work shift at 2pm: income depends on it."),
                    ("You", "I literally cannot be in two places at once."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 5),
                        'prompt': 'Make your choice',
                        'trigger_activity': 'housing_vs_work',
                        'required': True
                    }
                }
            },

            'second_consequence': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The consequence arrives immediately."),
                    (None, "Whatever you chose, there's a price."),
                    ("You", "Why does everything have to conflict?"),
                    (None, "Because nobody designed this system with you in mind."),
                ],
                'interactions': {}
            },

            'stress_maximum': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your head is spinning."),
                    (None, "Court. School. Housing. Work. Health."),
                    (None, "All of them demanding attention."),
                    (None, "All of them conflicting."),
                ],
                'interactions': {
                    'self': {
                        'position': (8, 7),
                        'prompt': 'Try to cope',
                        'trigger_activity': 'stress_overload',
                        'required': True
                    }
                }
            },

            'priorities_flash': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Everything flashes before your eyes."),
                    (None, "COURT. SCHOOL. HOUSING. WORK. HEALTH."),
                    (None, "All at once. All demanding. All conflicting."),
                ],
                'interactions': {}
            },

            'collapse': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You can't do this anymore."),
                    (None, "Papers scatter as you collapse onto the bed."),
                    ("You", "I just need... a moment..."),
                ],
                'interactions': {}
            },

            'final_narration': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Too many responsibilities."),
                    (None, "Not enough time."),
                    (None, "Without support, every decision feels like failure."),
                    (None, "This is what it means to navigate alone."),
                    (None, "Part 9 Complete - Conflicting Responsibilities & Time Constraints"),
                ],
                'interactions': {}
            }
        }

    def interact_with_object(self, name):
        """Handle interactions for Part 9 apartment"""
        print(f"[APT_P9] Interacting with: {name}")

        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            self.completed_interactions.add(name)

            if trigger == 'calendar_conflict':
                self.launch_calendar_conflict()
                return

            if trigger == 'mailbox_letter':
                self.launch_mailbox_letter()
                return

            if trigger == 'choose_one':
                self.launch_choose_one()
                return

            if trigger == 'housing_vs_work':
                self.launch_housing_vs_work()
                return

            if trigger == 'stress_overload':
                self.launch_stress_overload()
                return
        else:
            self.completed_interactions.add(name)

        super().interact_with_object(name)

        if self.check_objective_complete():
            print(f"[APT_P9] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_calendar_conflict(self):
        """Launch the calendar conflict game"""
        from part_9_time_constraints.activities.calendar_conflict import CalendarConflict

        if self.current_activity and self.current_activity.active:
            return

        activity = CalendarConflict()
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[APT_P9] Calendar conflict launched")

    def launch_mailbox_letter(self):
        """Launch the mailbox letter game"""
        from part_9_time_constraints.activities.mailbox_letter import MailboxLetter

        if self.current_activity and self.current_activity.active:
            return

        activity = MailboxLetter()
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[APT_P9] Mailbox letter launched")

    def launch_choose_one(self):
        """Launch the first choice dialogue"""
        from part_9_time_constraints.activities.choice_dialogue_part9 import ChoiceDialoguePart9

        if self.current_activity and self.current_activity.active:
            return

        activity = ChoiceDialoguePart9()
        activity.set_scenario('choose_one')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[APT_P9] Choose one launched")

    def launch_housing_vs_work(self):
        """Launch the housing vs work choice"""
        from part_9_time_constraints.activities.choice_dialogue_part9 import ChoiceDialoguePart9

        if self.current_activity and self.current_activity.active:
            return

        activity = ChoiceDialoguePart9()
        activity.set_scenario('housing_vs_work')
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[APT_P9] Housing vs work launched")

    def launch_stress_overload(self):
        """Launch the stress overload sequence"""
        from part_9_time_constraints.activities.stress_overload import StressOverload

        if self.current_activity and self.current_activity.active:
            return

        activity = StressOverload()
        activity.narrative_ref = self
        activity.start()

        self.game.objective_manager.current_activity = activity
        self.current_activity = activity
        print(f"[APT_P9] Stress overload launched")

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
            'calendar_conflict': (self.launch_calendar_conflict, 'calendar_completed'),
            'mailbox_letter': (self.launch_mailbox_letter, 'mailbox_completed'),
            'choose_one': (self.launch_choose_one, 'first_choice_completed'),
            'housing_vs_work': (self.launch_housing_vs_work, 'second_choice_completed'),
            'stress_maximum': (self.launch_stress_overload, 'stress_completed'),
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
                print(f"[APT_P9] Activity completed - cleaning up")

                # Mark completion based on phase
                if self.current_objective_phase == 'calendar_conflict':
                    self.calendar_completed = True
                elif self.current_objective_phase == 'mailbox_letter':
                    self.mailbox_completed = True
                elif self.current_objective_phase == 'choose_one':
                    self.first_choice_completed = True
                elif self.current_objective_phase == 'housing_vs_work':
                    self.second_choice_completed = True
                elif self.current_objective_phase == 'stress_maximum':
                    self.stress_completed = True

                self.current_activity = None
                self.game.objective_manager.current_activity = None

                if self.check_objective_complete():
                    self.end_narrative_sequence()
                return

        # Update stress level for visual indicator
        stress_phases = ['work_conflict_again', 'housing_vs_work', 'second_consequence',
                        'stress_maximum', 'priorities_flash', 'collapse']
        if self.current_objective_phase in stress_phases:
            self.stress_level = min(1.0, self.stress_level + dt * 0.1)

    def draw(self, screen):
        """Draw apartment interior with activity overlay"""
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            if hasattr(self.current_activity, 'render'):
                self.current_activity.render(screen)
            elif hasattr(self.current_activity, 'draw'):
                self.current_activity.draw(screen)
            return

        super().draw(screen)
        self.render_stress_meter(screen)

    def render_stress_meter(self, screen):
        """Render stress meter when applicable"""
        if self.stress_level > 0:
            meter_width = 150
            meter_height = 20
            x = screen.get_width() - 170
            y = 60

            # Background
            bg_rect = pygame.Rect(x, y, meter_width, meter_height)
            pygame.draw.rect(screen, (60, 40, 40), bg_rect)

            # Fill
            fill_width = int(self.stress_level * meter_width)
            fill_rect = pygame.Rect(x, y, fill_width, meter_height)
            pygame.draw.rect(screen, (200, 80, 80), fill_rect)

            pygame.draw.rect(screen, (120, 80, 80), bg_rect, 1)

            # Label
            font = pygame.font.Font(None, 16)
            label = font.render("STRESS", True, (200, 150, 150))
            screen.blit(label, (x, y - 14))

    def end_narrative_sequence(self):
        """Handle apartment transitions"""
        print(f"[APT_P9] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[APT_P9] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[APT_P9] Next objective also at apartment: {next_obj.id}")
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
        if current.id == 'calendar_conflict':
            return self.calendar_completed

        if current.id == 'mailbox_letter':
            return self.mailbox_completed

        if current.id == 'choose_one':
            return self.first_choice_completed

        if current.id == 'housing_vs_work':
            return self.second_choice_completed

        if current.id == 'stress_maximum':
            return self.stress_completed

        # Interaction-based objectives
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        for name, data in interactions.items():
            if data.get('required', False):
                if name not in self.completed_interactions:
                    return False

        # Dialogue-only objectives
        dialogue_only = [
            'overlap_warning', 'first_consequence', 'court_school_conflict',
            'no_appointments', 'work_conflict_again', 'second_consequence',
            'priorities_flash', 'collapse', 'final_narration'
        ]
        if current.id in dialogue_only:
            return not self.narrative_active

        return True

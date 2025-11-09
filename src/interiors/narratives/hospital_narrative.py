"""
Hospital Narrative for Part 2 - Emergency Room Visit
Handles the emergency room experience after the broken stair accident
"""

import pygame
import random
from src.interiors.narrative_interior import NarrativeInterior

class HospitalNarrative(NarrativeInterior):
    """Hospital with emergency room experience for Part 2"""

    def __init__(self, game, room_data, building_pos):
        # Initialize ER state BEFORE calling super().__init__
        # ER specific state
        self.wait_time_elapsed = 0
        self.total_wait_time = 6 * 60  # 6 hours represented in game minutes
        self.current_wait_phase = 0
        self.pain_level = 8  # Out of 10

        # Track ER progress
        self.checked_in = False
        self.triaged = False
        self.seen_by_doctor = False
        self.treatment_complete = False

        # Visual timers for effects
        self.pain_pulse_timer = 0
        self.clock_update_timer = 0

        # Activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Now call super().__init__ after our attributes are set
        super().__init__(game, room_data, building_pos)

    def enter(self):
        """Override enter to set up ER scene"""
        super().enter()

        # Check which objective we're on
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'emergency_room':
            # Set up emergency room scenario
            self.setup_emergency_room()

        self.update_objective_display()

    def setup_emergency_room(self):
        """Set up the emergency room waiting experience"""
        # Define NPCs specific to ER
        er_npcs = [
            {'name': 'Receptionist', 'x': 9, 'y': 3},
            {'name': 'Triage Nurse', 'x': 7, 'y': 3},
            {'name': 'Security', 'x': 2, 'y': 6},
            {'name': 'Doctor', 'x': 14, 'y': 8}
        ]

        # Add them to the scene
        for npc_data in er_npcs:
            self.add_npc(npc_data['name'], npc_data['x'], npc_data['y'])

        # Start with arrival dialogue
        self.start_narrative_sequence('emergency_room')

    def load_narrative_content(self):
        """Load the ER narrative content"""
        return {
            'emergency_room': {
                'npcs': [],  # NPCs added dynamically in setup_emergency_room
                'dialogue_sequence': [
                    (None, "You limp into the emergency room, ankle throbbing."),
                    (None, "The pain shoots up your leg with every step."),
                    ("Receptionist", "Oh honey, you look hurt! Fill out these forms."),
                    ("You", "I fell down broken stairs... my ankle..."),
                    ("Receptionist", "Take a seat. We'll call you for triage soon."),
                    (None, "The waiting room is packed. This is going to be a long wait.")
                ],
                'interactions': {
                    'reception_desk': {
                        'position': (9, 3),
                        'prompt': 'Check in at desk',
                        'trigger_activity': 'er_checkin',
                        'dialogue': None,
                        'required': True
                    },
                    'triage_area': {
                        'position': (7, 3),
                        'prompt': 'Go to triage',
                        'dialogue': [
                            "The nurse examines your swollen ankle.",
                            "Nurse: 'Pain level from 1 to 10?'",
                            "You: 'Eight... maybe nine when I put weight on it.'",
                            "Nurse: 'Significant swelling. We need X-rays.'",
                            "She marks your chart 'Urgent' but says it's busy today.",
                            "Back to the waiting room..."
                        ],
                        'required': False
                    },
                    'waiting_chair_1': {
                        'position': (4, 7),
                        'prompt': 'Sit and wait',
                        'trigger_activity': 'er_waiting',
                        'dialogue': None,
                        'required': True
                    },
                    'waiting_chair_2': {
                        'position': (6, 7),
                        'prompt': 'Sit and wait',
                        'trigger_activity': 'er_waiting',
                        'dialogue': None,
                        'required': False
                    },
                    'waiting_chair_3': {
                        'position': (8, 7),
                        'prompt': 'Sit and wait',
                        'trigger_activity': 'er_waiting',
                        'dialogue': None,
                        'required': False
                    },
                    'vending_machine': {
                        'position': (2, 10),
                        'prompt': 'Get snack ($3)',
                        'dialogue': [
                            "Your stomach growls. You haven't eaten in hours.",
                            "$3 for chips. $4 for a candy bar.",
                            "Everything costs triple what it should.",
                            "You count your cash... need to save for the taxi home."
                        ],
                        'required': False
                    },
                    'water_fountain': {
                        'position': (12, 10),
                        'prompt': 'Get water',
                        'dialogue': [
                            "At least the water is free.",
                            "You drink deeply, trying to ignore the pain.",
                            "Your ankle throbs worse when you stand."
                        ],
                        'required': False
                    },
                    'treatment_room': {
                        'position': (14, 8),
                        'prompt': 'Enter treatment room',
                        'dialogue': [
                            "Finally! After 6 hours, they call your name.",
                            "The doctor looks exhausted. 'Let's see that ankle.'",
                            "X-rays show: severe sprain, no fracture.",
                            "Doctor: 'Lucky it's not broken. Those stairs could've killed you.'",
                            "You get a walking boot, crutches, and pain medication.",
                            "Doctor: 'No weight bearing for a week. Rest as much as possible.'",
                            "You think: 'How am I supposed to work?'",
                            "The discharge nurse hands you papers.",
                            "Initial bill estimate: $2,400.",
                            "Your heart sinks. That's two months rent.",
                            "Time to go home and figure out how to survive this."
                        ],
                        'required': True
                    },
                    'clock': {
                        'position': (9, 1),
                        'prompt': 'Check the time',
                        'dialogue': None,  # Will be handled dynamically
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update the objective display with current status"""
        if hasattr(self.game, 'objective_manager'):
            current = self.game.objective_manager.get_current_objective()
            if current and current.id == 'emergency_room':
                # Could add status text about waiting time
                pass

    def interact_with_object(self, name):
        """Handle object interactions with activities"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            super().interact_with_object(name)
            return

        # Get the interactions for current objective
        interactions = self.narrative_content.get(current.id, {}).get('interactions', {})
        if name not in interactions:
            super().interact_with_object(name)
            return

        interaction = interactions[name]

        # Launch activity if specified
        trigger = interaction.get('trigger_activity')

        if trigger == 'er_checkin':
            # Mark as checked in
            self.checked_in = True
            self.show_checkin_dialogue()
        elif trigger == 'er_waiting':
            # Launch the visual ER waiting room activity
            from src.activities.er_waiting import ERWaitingRoom
            activity = ERWaitingRoom(self.game.objective_manager)
            activity.narrative_ref = self
            if hasattr(self.game, 'activity_manager'):
                self.game.activity_manager.start_activity(activity)
            else:
                # Fallback if no activity manager
                activity.start()
                self.current_activity = activity
        elif name == 'clock':
            # Handle clock interaction dynamically
            hours = int(self.wait_time_elapsed // 60)
            minutes = int(self.wait_time_elapsed % 60)
            clock_dialogue = [
                f"You've been waiting for {hours} hours and {minutes} minutes.",
                "The clock seems to be moving backwards.",
                "Every minute feels like an hour."
            ]
            self.current_sequence = [(None, text) for text in clock_dialogue]
            self.sequence_index = 0
            self.show_next_dialogue()
        else:
            # Show dialogue if no activity
            if interaction.get('dialogue'):
                self.current_sequence = [(None, text) for text in interaction['dialogue']]
                self.sequence_index = 0
                self.show_next_dialogue()

        # Mark as completed
        self.completed_interactions.add(name)

        # Check if all required interactions are complete
        self.check_objective_completion()

    def show_checkin_dialogue(self):
        """Show check-in process dialogue"""
        self.current_sequence = [
            (None, "You fill out endless forms despite the pain."),
            ("Receptionist", "Insurance?"),
            ("You", "I... I don't have any."),
            ("Receptionist", "We'll work out payment later. Take a seat."),
            (None, "You limp to the waiting area.")
        ]
        self.sequence_index = 0
        self.show_next_dialogue()

    def start_waiting_experience(self):
        """Start the 6-hour waiting room experience"""
        # Show waiting phases
        wait_phase = self.current_wait_phase

        if wait_phase == 0:
            dialogue = [
                (None, "Hour 1: The pain is sharp. Every heartbeat hurts."),
                (None, "A child nearby is crying. Someone coughs constantly."),
                (None, "You try to find a comfortable position. There isn't one.")
            ]
        elif wait_phase == 1:
            dialogue = [
                (None, "Hour 2: Your ankle is swelling more."),
                (None, "You ask the receptionist how much longer."),
                ("Receptionist", "We're very busy today. Shouldn't be too much longer."),
                (None, "That's what she said an hour ago.")
            ]
        elif wait_phase == 2:
            dialogue = [
                (None, "Hour 3: You're called for triage."),
                (None, "They take your vitals, give you an ice pack."),
                ("Triage Nurse", "You're priority 3. Shouldn't be too long now."),
                (None, "Back to waiting.")
            ]
        elif wait_phase == 3:
            dialogue = [
                (None, "Hour 4: The ice pack has melted."),
                (None, "Your stomach is empty. Your phone battery is dying."),
                (None, "You watch people who came after you get called first.")
            ]
        elif wait_phase == 4:
            dialogue = [
                (None, "Hour 5: You can barely stay awake."),
                (None, "The pain has become a constant companion."),
                (None, "You wonder if you should just leave.")
            ]
        else:
            dialogue = [
                (None, "Hour 6: Finally, they call your name."),
                (None, "You struggle to stand. Your leg has stiffened."),
                (None, "Time to see the doctor at last.")
            ]
            self.triaged = True

        self.current_sequence = dialogue
        self.sequence_index = 0
        self.show_next_dialogue()

        # Increment wait phase for next interaction
        self.current_wait_phase = min(self.current_wait_phase + 1, 5)

    def check_objective_completion(self):
        """Check if current objective requirements are met"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        interactions = self.narrative_content.get(current.id, {}).get('interactions', {})
        required_complete = True

        for name, data in interactions.items():
            if data.get('required') and name not in self.completed_interactions:
                required_complete = False
                break

        if required_complete and current.id == 'emergency_room':
            # Show completion dialogue
            self.current_sequence = [
                (None, "After 6 hours, you finally leave the ER."),
                (None, "Ankle wrapped, on crutches, with a huge bill coming."),
                (None, "Now you have to figure out how to work like this."),
                (None, "How to pay rent when you can't stand."),
                (None, "The broken stair that caused this still isn't fixed.")
            ]
            self.sequence_index = 0
            self.show_next_dialogue()
            self.should_exit = True

    def update(self, dt):
        """Update the ER experience"""
        super().update(dt)

        # Update current activity if one is running
        if self.current_activity and self.current_activity.active:
            self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                self.on_activity_complete()
                self.current_activity = None

        # Update visual timers
        self.pain_pulse_timer += dt
        self.clock_update_timer += dt

        # Slowly increment wait time for realism
        if self.checked_in and not self.treatment_complete:
            self.wait_time_elapsed += dt * 0.1  # Accelerated time

        # Auto-exit after completion
        if self.should_exit and not self.dialogue_box.active:
            self.exit_timer += dt
            if self.exit_timer > 2:
                self.game.objective_manager.complete_current_objective()
                self.active = False

    def on_activity_complete(self):
        """Handle activity completion"""
        # After waiting room activity, move to treatment
        self.triaged = True
        self.current_wait_phase = 6
        self.wait_time_elapsed = 360  # 6 hours

        # Show completion dialogue
        self.current_sequence = [
            (None, "You're finally called for treatment."),
            (None, "The waiting is over, but the bills are just beginning.")
        ]
        self.sequence_index = 0
        self.show_next_dialogue()

    def handle_event(self, event):
        """Handle events including activity input"""
        # If activity is active, let it handle input
        if self.current_activity and self.current_activity.active:
            return self.current_activity.handle_event(event)

        # Otherwise use normal event handling
        return super().handle_event(event)

    def draw(self, screen):
        """Draw the interior and ER-specific elements"""
        # If activity is active, let it render
        if self.current_activity and self.current_activity.active:
            self.current_activity.render(screen)
            return

        # Draw base interior
        super().draw(screen)

        # Draw waiting time indicator if checked in
        if self.checked_in and not self.treatment_complete:
            self.draw_wait_timer(screen)

        # Draw pain indicator
        if self.checked_in:
            self.draw_pain_indicator(screen)

    def draw_wait_timer(self, screen):
        """Draw the waiting time on screen"""
        font = pygame.font.Font(None, 28)
        hours = int(self.wait_time_elapsed // 60)
        minutes = int(self.wait_time_elapsed % 60)

        # Create time display
        time_text = f"Waiting: {hours}h {minutes}m"
        time_surf = font.render(time_text, True, (255, 100, 100))

        # Position in top right
        time_rect = time_surf.get_rect(topright=(self.SCREEN_WIDTH - 20, 20))

        # Draw background
        bg_rect = time_rect.inflate(20, 10)
        pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 3)
        pygame.draw.rect(screen, (255, 100, 100), bg_rect, 2, 3)

        screen.blit(time_surf, time_rect)

    def draw_pain_indicator(self, screen):
        """Draw pain level indicator with pulsing effect"""
        # Pulse effect based on timer
        pulse = abs(pygame.math.Vector2(1, 0).rotate(self.pain_pulse_timer * 100).x) * 0.3 + 0.7

        font = pygame.font.Font(None, 24)
        pain_text = f"Pain Level: {self.pain_level}/10"
        color = (255, int(100 * pulse), int(100 * pulse))
        pain_surf = font.render(pain_text, True, color)

        # Position in top left
        pain_rect = pain_surf.get_rect(topleft=(20, 20))

        # Draw background
        bg_rect = pain_rect.inflate(20, 10)
        pygame.draw.rect(screen, (50, 20, 20), bg_rect, 0, 3)

        screen.blit(pain_surf, pain_rect)

        # Draw pain bars
        bar_x = pain_rect.left
        bar_y = pain_rect.bottom + 5
        for i in range(self.pain_level):
            bar_color = (255, 50, 50) if i < 5 else (255, 0, 0)
            pygame.draw.rect(screen, bar_color,
                           (bar_x + i * 15, bar_y, 12, 6))
"""
Hospital Emergency Room Narrative for Part 2
Handles the emergency room visit after the broken stair accident
"""

import pygame
import random
from src.interiors.narrative_interior import NarrativeInterior

class HospitalERNarrative(NarrativeInterior):
    """Hospital ER with waiting room experience and injury treatment"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # ER specific state
        self.wait_time_elapsed = 0
        self.total_wait_time = 6 * 60 * 60  # 6 hours in seconds
        self.triage_complete = False
        self.treatment_complete = False
        self.bill_preview_shown = False

        # Pain level tracking
        self.pain_level = 8  # Out of 10
        self.mobility_impaired = True

        # Other patients for atmosphere
        self.other_patients = [
            {'name': 'Crying Child', 'condition': 'Broken arm from playground'},
            {'name': 'Elderly Man', 'condition': 'Chest pains, looks worried'},
            {'name': 'Young Woman', 'condition': 'Bad cut on hand, bleeding through towel'},
            {'name': 'Construction Worker', 'condition': 'Back injury, can barely move'}
        ]

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
        # Add NPCs
        self.npcs = {
            'triage_nurse': {'name': 'Triage Nurse', 'x': 8, 'y': 3},
            'receptionist': {'name': 'Receptionist', 'x': 10, 'y': 3},
            'doctor': {'name': 'Doctor', 'x': 14, 'y': 8}
        }

        # Start with arrival dialogue
        self.start_narrative_sequence('emergency_room')

    def load_narrative_content(self):
        """Load the ER narrative content"""
        return {
            'emergency_room': {
                'npcs': [
                    {'name': 'Triage Nurse', 'x': 8, 'y': 3},
                    {'name': 'Receptionist', 'x': 10, 'y': 3},
                    {'name': 'Security Guard', 'x': 3, 'y': 8}
                ],
                'dialogue_sequence': [
                    (None, "You limp into the emergency room, ankle throbbing with pain."),
                    ("Receptionist", "Oh honey, you look hurt! What happened?"),
                    ("You", "Fell down broken stairs at my apartment... My ankle..."),
                    ("Receptionist", "Fill out these forms. Triage will call you soon."),
                    (None, "The waiting room is packed. This is going to be a long wait."),
                    (None, "Every step sends shooting pain up your leg.")
                ],
                'interactions': {
                    'check_in_desk': {
                        'position': (10, 3),
                        'prompt': 'Check in at desk',
                        'trigger_activity': 'er_checkin',
                        'dialogue': None,
                        'required': True
                    },
                    'triage_station': {
                        'position': (8, 3),
                        'prompt': 'Go to triage',
                        'dialogue': [
                            "The nurse examines your ankle carefully.",
                            "Nurse: 'Significant swelling. Pain level?'",
                            "You: 'Eight out of ten...'",
                            "Nurse: 'We'll get you seen, but it's busy today.'",
                            "She gives you an ice pack and marks your chart 'Urgent'.",
                            "Back to waiting..."
                        ],
                        'required': False
                    },
                    'waiting_chair': {
                        'position': (6, 7),
                        'prompt': 'Sit and wait',
                        'trigger_activity': 'er_waiting',
                        'dialogue': None,
                        'required': True
                    },
                    'vending_machine': {
                        'position': (3, 10),
                        'prompt': 'Get snack ($3)',
                        'dialogue': [
                            "Your stomach growls. You haven't eaten in hours.",
                            "$3 for a small bag of chips. Highway robbery.",
                            "But you need something in your stomach.",
                            "You count your remaining cash... Not much left."
                        ],
                        'required': False
                    },
                    'treatment_room': {
                        'position': (14, 8),
                        'prompt': 'Enter treatment room',
                        'dialogue': [
                            "Finally! After 6 hours, they call your name.",
                            "The doctor looks exhausted. 'Let's see that ankle.'",
                            "X-rays confirm: bad sprain, no break.",
                            "Doctor: 'Lucky. Could have been worse on those stairs.'",
                            "You get a walking boot and crutches.",
                            "Doctor: 'No weight bearing for a week. Rest.'",
                            "You think: 'How am I supposed to work?'",
                            "The discharge papers include a bill estimate: $2,400.",
                            "Your heart sinks. That's two months rent."
                        ],
                        'required': True
                    }
                }
            },

            'missed_work': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Back in your apartment, reality sets in."),
                    (None, "You can't walk properly. Can't stand for long."),
                    (None, "Your job requires you to be on your feet all day."),
                    (None, "You text your manager about the injury."),
                    (None, "'Sorry, no sick leave for part-time. See you when you're better.'"),
                    (None, "That's 5 days of work... $450 in lost income."),
                    (None, "Plus the medical bill coming."),
                    (None, "The math is getting worse by the day.")
                ],
                'interactions': {
                    'phone': {
                        'position': (8, 7),
                        'prompt': 'Call manager',
                        'dialogue': [
                            "You try calling instead of texting.",
                            "Manager: 'Look, I'm sorry you're hurt, but...'",
                            "'I need someone who can work. That's the job.'",
                            "'Take the time you need, but I can't pay you.'",
                            "'And if you're out too long, I'll need to hire someone.'",
                            "The threat is clear: your job isn't secure."
                        ],
                        'required': True
                    },
                    'calculator': {
                        'position': (10, 6),
                        'prompt': 'Calculate losses',
                        'trigger_activity': 'medical_bill_calculator',
                        'dialogue': None,
                        'required': True
                    }
                }
            }
        }

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
            # Launch ER check-in activity
            from src.activities.er_checkin import ERCheckIn
            activity = ERCheckIn(self.game.objective_manager)
            activity.narrative_ref = self
            self.game.activity_manager.start_activity(activity)
        elif trigger == 'er_waiting':
            # Launch ER waiting room experience
            from src.activities.er_waiting import ERWaitingRoom
            activity = ERWaitingRoom(self.game.objective_manager)
            activity.narrative_ref = self
            self.game.activity_manager.start_activity(activity)
        elif trigger == 'medical_bill_calculator':
            # Launch medical bill breakdown
            from src.activities.medical_bills import MedicalBillCalculator
            activity = MedicalBillCalculator(self.game.objective_manager)
            activity.narrative_ref = self
            self.game.activity_manager.start_activity(activity)
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

        if required_complete:
            # Add completion dialogue
            if current.id == 'emergency_room':
                self.current_sequence = [
                    (None, "After 6 hours, you finally leave the ER."),
                    (None, "Ankle wrapped, on crutches, with a huge bill coming."),
                    (None, "Time to figure out how to survive this setback.")
                ]
                self.sequence_index = 0
                self.show_next_dialogue()
                self.should_exit = True

            elif current.id == 'missed_work':
                self.should_exit = True

    def update(self, dt):
        """Update the ER experience"""
        super().update(dt)

        # Auto-exit after completion
        if self.should_exit and not self.dialogue_box.active:
            self.exit_timer += dt
            if self.exit_timer > 1:
                self.game.objective_manager.complete_current_objective()
                self.active = False
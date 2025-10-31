"""
Local bank - trying to build financial stability
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class BankNarrative(NarrativeInterior):
    """bank with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/bank.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'secured_credit': {
                'npcs': [
                    {'name': 'Bank Teller', 'x': 7, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Bank Teller", "How can I help you today?"),
                    ("You", "I want to build credit. I have no credit history."),
                    ("Bank Teller", "We offer a secured credit card."),
                    ("Bank Teller", "You put down $200, that becomes your credit limit."),
                    ("You", "So I'm borrowing my own money?"),
                    ("Bank Teller", "Essentially, yes. But it builds credit history."),
                    ("You", "I'll do it. I need to break this cycle."),
                    (None, "You hand over $200 you can't really spare."),
                    (None, "But maybe it's an investment in your future.")
                ],
                'interactions': {
                    'application': {
                        'position': (7, 6),
                        'prompt': 'Fill out application',
                        'trigger_activity': 'credit_application',
                    }
                }
            },
            'small_savings': {
                'npcs': [
                    {'name': 'Bank Teller', 'x': 7, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Bank Teller", "Checking your balance?"),
                    ("You", "Yeah. I've been saving $50 a month."),
                    ("Bank Teller", "Your balance is $400."),
                    ("You", "It took 8 months to save that."),
                    ("Bank Teller", "Every bit helps. You're doing great."),
                    (None, "It's not much. One emergency could wipe it out."),
                    (None, "But it's more than you've ever had before."),
                    (None, "Maybe things are getting better. Slowly.")
                ],
                'interactions': {
                    'atm': {
                        'position': (5, 6),
                        'prompt': 'Check balance',
                        'dialogue': ["Savings: $400", "Checking: $87", "Total: $487", "Your entire net worth."],
                    }
                }
            },
        }

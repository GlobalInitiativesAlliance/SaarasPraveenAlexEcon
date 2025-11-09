"""
Free legal aid office for tenant rights
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class LegalAidNarrative(NarrativeInterior):
    """legal_aid with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/housing_office.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'legal_aid_visit': {
                'npcs': [
                    {'name': 'Lawyer', 'x': 8, 'y': 5},
                    {'name': 'Receptionist', 'x': 4, 'y': 3}
                ],
                'dialogue_sequence': [
                    ("Receptionist", "Sign in and take a number. Wait time is about 2 hours."),
                    ("You", "I can wait. I need help with my landlord."),
                    (None, "Two hours later..."),
                    ("Lawyer", "I've reviewed your documentation. You have a strong case."),
                    ("Lawyer", "Your landlord is violating at least 12 housing codes."),
                    ("You", "Can he evict me if I complain?"),
                    ("Lawyer", "Not legally. That would be retaliation, which is illegal."),
                    ("Lawyer", "But document everything. They might try anyway.")
                ],
                'interactions': {
                    'desk': {
                        'position': (8, 6),
                        'prompt': 'Show evidence',
                        'dialogue': ["You spread out your photos.", "The lawyer takes notes.", "This is worse than most cases."],
                    },
                    'pamphlets': {
                        'position': (3, 7),
                        'prompt': 'Read tenant rights',
                        'trigger_activity': 'research_rights',
                    }
                }
            },
            'withholding_threat': {
                'npcs': [
                    {'name': 'Lawyer', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Lawyer", "I'll send a demand letter to your landlord."),
                    ("Lawyer", "Fix the violations or you can legally withhold rent."),
                    ("You", "Won't that make things worse?"),
                    ("Lawyer", "Maybe. But freezing in an unsafe apartment is already worse."),
                    ("Lawyer", "You have rights. It's time to use them.")
                ],
                'interactions': {
                    'letter': {
                        'position': (8, 6),
                        'prompt': 'Review demand letter',
                        'dialogue': ["It lists every violation.", "The legal language is intimidating.", "This might actually work."],
                    }
                }
            },
        }

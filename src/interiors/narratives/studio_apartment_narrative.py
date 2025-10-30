"""
Crappy studio apartment from Part 1 ending
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class StudioApartmentNarrative(NarrativeInterior):
    """studio_apartment with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/bad_studio.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'studio_day_one': {
                'npcs': [
                    {'name': 'Landlord', 'x': 5, 'y': 6},
                    {'name': 'Neighbor', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Landlord", "Rent's due on the first. Don't be late."),
                    ("You", "What about the broken heater you promised to fix?"),
                    ("Landlord", "I'll get to it when I get to it."),
                    (None, "He leaves without another word. You're on your own."),
                    ("Neighbor", "Hey, new tenant? Word of advice - document everything."),
                    ("Neighbor", "Take photos, save texts. You'll need evidence."),
                    (None, "The apartment is worse than you thought. Roaches scatter as you walk.")
                ],
                'interactions': {
                    'heater': {
                        'position': (3, 8),
                        'prompt': 'Examine broken heater',
                        'dialogue': ["It hasn't worked in months.", "Ice cold to the touch.", "Landlord knew about this."],
                    },
                    'window': {
                        'position': (12, 5),
                        'prompt': 'Check window locks',
                        'dialogue': ["The lock is broken.", "Anyone could get in.", "No wonder there were break-ins."],
                    },
                    'phone': {
                        'position': (7, 7),
                        'prompt': 'Document problems',
                        'trigger_activity': 'document_violations',
                    }
                }
            },
            'document_problems': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to build your case. Document everything."),
                    (None, "Take photos of every violation, every broken thing."),
                    (None, "This evidence might save you later.")
                ],
                'interactions': {
                    'camera': {
                        'position': (7, 7),
                        'prompt': 'Start documenting',
                        'trigger_activity': 'document_violations',
                    }
                }
            },
            'first_repair_request': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You text the landlord about the heater."),
                    (None, "He reads it immediately. The 'read' receipt shows."),
                    (None, "No response. Hours pass. Still nothing."),
                    (None, "You'll freeze tonight. Again.")
                ],
                'interactions': {}
            },
        }

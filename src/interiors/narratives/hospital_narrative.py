"""
Emergency room - where bills pile up
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class HospitalNarrative(NarrativeInterior):
    """hospital with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/hospital.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'emergency_room': {
                'npcs': [
                    {'name': 'Nurse', 'x': 6, 'y': 5},
                    {'name': 'Doctor', 'x': 9, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Nurse", "What brings you in today?"),
                    ("You", "I fell on broken stairs. My ankle..."),
                    ("Nurse", "We'll get you an X-ray. Have a seat."),
                    (None, "Six hours pass. The pain is unbearable."),
                    ("Doctor", "Severe sprain. You need to stay off it for a week."),
                    ("You", "I can't miss work. I'll lose my apartment."),
                    ("Doctor", "If you don't rest it, you could cause permanent damage."),
                    (None, "The bill will come later. Thousands, probably."),
                    (None, "Another debt you can't pay.")
                ],
                'interactions': {
                    'discharge_papers': {
                        'position': (7, 6),
                        'prompt': 'Review discharge papers',
                        'dialogue': ["Diagnosis: Severe ankle sprain", "Treatment: Rest, ice, elevation", "Follow up in 2 weeks", "You can't afford any of this."],
                    }
                }
            },
        }

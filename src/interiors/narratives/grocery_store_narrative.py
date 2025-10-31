"""
Your workplace - where you struggle to earn enough
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class GroceryStoreNarrative(NarrativeInterior):
    """grocery_store with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/grocery_store.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'second_job_hunt': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("You", "Any chance of more hours? Or overtime?"),
                    ("Manager", "Sorry, company policy. No overtime."),
                    ("Manager", "I can give you 5 more hours a week, max."),
                    ("You", "That's only $75 more. I need another job."),
                    ("Manager", "The diner down the street is hiring night shift."),
                    (None, "Night shift means no sleep."),
                    (None, "But homelessness means no sleep either.")
                ],
                'interactions': {
                    'schedule': {
                        'position': (8, 6),
                        'prompt': 'Check work schedule',
                        'dialogue': ["Current: 20 hours/week", "Maximum: 25 hours/week", "Still not enough to survive."],
                    }
                }
            },
            'exhaustion_sets_in': {
                'npcs': [
                    {'name': 'Coworker', 'x': 6, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Coworker", "You okay? You look exhausted."),
                    ("You", "Working 60 hours between two jobs."),
                    ("Coworker", "That's not sustainable."),
                    ("You", "Neither is homelessness."),
                    (None, "You're falling asleep standing up."),
                    (None, "Making mistakes. Getting complaints."),
                    (None, "But what choice do you have?")
                ],
                'interactions': {}
            },
            'promotion_earned': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Manager", "I have good news. You're being promoted to shift lead."),
                    ("You", "Really? What does that mean?"),
                    ("Manager", "$2 more per hour. More responsibility."),
                    ("Manager", "That's $320 more per month if you work full time."),
                    ("You", "I'll take it! Thank you!"),
                    (None, "It's not much, but it's something."),
                    (None, "Maybe now you can save a little.")
                ],
                'interactions': {
                    'name_tag': {
                        'position': (8, 6),
                        'prompt': 'Put on new name tag',
                        'dialogue': ["'Shift Lead'", "A small step up.", "Every dollar counts."],
                    }
                }
            },
        }

"""
Public library - for research and tenant organizing
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class LibraryNarrative(NarrativeInterior):
    """library with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/library.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'roommate_search': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "Looking for roommate listings?"),
                    ("You", "Yeah, my rent just went up 15%."),
                    ("Librarian", "Try Facebook groups and Craigslist."),
                    (None, "You search for an hour."),
                    (None, "Every listing wants credit checks, references, deposits."),
                    (None, "Plus your studio is too small to legally share."),
                    (None, "The lease also forbids subletting."),
                    (None, "There's no way out of this.")
                ],
                'interactions': {
                    'computer': {
                        'position': (5, 6),
                        'prompt': 'Search for roommates',
                        'trigger_activity': 'roommate_search',
                    }
                }
            },
            'research_rights': {
                'npcs': [
                    {'name': 'Law Student', 'x': 10, 'y': 7}
                ],
                'dialogue_sequence': [
                    ("Law Student", "Researching tenant law?"),
                    ("You", "My landlord won't fix anything."),
                    ("Law Student", "Check the warranty of habitability statute."),
                    ("Law Student", "Landlords must maintain livable conditions."),
                    ("Law Student", "Document everything. Get it in writing."),
                    ("Law Student", "You might be able to withhold rent legally."),
                    ("You", "Really? That's allowed?"),
                    ("Law Student", "If done properly. Get legal help first.")
                ],
                'interactions': {
                    'law_book': {
                        'position': (10, 6),
                        'prompt': 'Read tenant rights',
                        'trigger_activity': 'tenant_rights_quiz',
                    }
                }
            },
            'tenant_union': {
                'npcs': [
                    {'name': 'Union Organizer', 'x': 7, 'y': 5},
                    {'name': 'Fellow Tenant 1', 'x': 5, 'y': 6},
                    {'name': 'Fellow Tenant 2', 'x': 9, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Union Organizer", "Welcome to the tenant union meeting."),
                    ("Fellow Tenant 1", "My landlord raised rent 20% last month."),
                    ("Fellow Tenant 2", "Mine won't fix the black mold."),
                    ("You", "Mine threatened eviction after I got injured."),
                    ("Union Organizer", "Together we have power. Alone we're victims."),
                    ("Union Organizer", "We share resources, knowledge, support."),
                    ("Union Organizer", "And when needed, we fight together."),
                    (None, "For the first time, you don't feel alone.")
                ],
                'interactions': {
                    'signup_sheet': {
                        'position': (7, 6),
                        'prompt': 'Join the union',
                        'dialogue': ["You write your name and contact info.", "You're part of something bigger now.", "Together, you might win."],
                    }
                }
            },
            'tenant_meeting': {
                'npcs': [
                    {'name': 'Building Organizer', 'x': 7, 'y': 5},
                    {'name': 'Tenant A', 'x': 4, 'y': 6},
                    {'name': 'Tenant B', 'x': 10, 'y': 6},
                    {'name': 'Tenant C', 'x': 7, 'y': 8}
                ],
                'dialogue_sequence': [
                    ("Building Organizer", "How many got the cash-for-keys offer?"),
                    ("Tenant A", "I did. $1,500 for me."),
                    ("Tenant B", "They offered me $2,000."),
                    ("Tenant C", "Only $1,000 for me. Why the difference?"),
                    ("Building Organizer", "They're trying to divide us."),
                    ("Building Organizer", "If we all refuse, they can't evict everyone."),
                    ("You", "But what if they try anyway?"),
                    ("Building Organizer", "Then we make it very public. Very expensive for them."),
                    (None, "The room buzzes with nervous energy. This is resistance.")
                ],
                'interactions': {
                    'strategy_board': {
                        'position': (7, 4),
                        'prompt': 'Review strategy',
                        'dialogue': ["Tenant rights hotline numbers", "Media contacts", "Legal aid resources", "Protest plans"],
                    }
                }
            },
        }

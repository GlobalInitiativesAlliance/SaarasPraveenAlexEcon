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

    def launch_activity(self, activity_name):
        """Launch the appropriate activity based on the name"""
        if activity_name == 'roommate_search':
            self.launch_roommate_search()
        elif activity_name == 'research_rights':
            self.launch_research_rights()
        else:
            super().launch_activity(activity_name)

    def launch_roommate_search(self):
        """Launch the roommate search mini-game"""
        from src.activities.roommate_search import RoommateSearchActivity

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = RoommateSearchActivity(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            # Set as current activity both locally and on objective_manager
            self.current_activity = activity
            self.game.objective_manager.current_activity = activity
            print("Launched roommate search activity")

    def launch_research_rights(self):
        """Launch the tenant rights research mini-game"""
        from src.activities.research_rights import TenantRightsResearch

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = TenantRightsResearch(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            # Set as current activity both locally and on objective_manager
            self.current_activity = activity
            self.game.objective_manager.current_activity = activity
            print("Launched tenant rights research activity")

    def handle_event(self, event):
        """Handle events, routing to activity if active"""
        # If an activity is active, route events to it
        if self.current_activity and hasattr(self.current_activity, 'active') and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            return  # Don't process other events during activity

        # Otherwise use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update the interior and any active activity"""
        super().update(dt)

        # Update activity if active
        if self.current_activity and hasattr(self.current_activity, 'active') and self.current_activity.active:
            self.current_activity.update(dt)

            # Check if activity completed
            if hasattr(self.current_activity, 'completed') and self.current_activity.completed:
                print("Roommate search activity completed")
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                # Complete the objective
                if hasattr(self.game, 'objective_manager'):
                    self.game.objective_manager.complete_current_objective()

    def draw(self, screen):
        """Draw the interior or activity"""
        # If activity is active, let it handle the entire screen
        if self.current_activity and hasattr(self.current_activity, 'active') and self.current_activity.active:
            self.current_activity.draw(screen)
        else:
            # Otherwise draw normally
            super().draw(screen)

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
                    ("Librarian", "The computers are over there.")
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
                        'trigger_activity': 'research_rights',
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

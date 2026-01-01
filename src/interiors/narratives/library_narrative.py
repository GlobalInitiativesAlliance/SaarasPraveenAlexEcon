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
        self.should_exit = False

        # Track search progress (original integration)
        self.search_complete = False
        self.listings_found = 0
        self.exit_timer = 0.0

        # Track initial objective for exit detection
        self.initial_objective_id = None

        # Flag to prevent double objective advancement
        self.handles_own_objectives = True

    def enter(self):
        """Store initial objective when entering library"""
        # Store the current objective for exit detection
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj:
            self.initial_objective_id = current_obj.id
            print(f"[LIBRARY_ENTER] Entering library with objective: {self.initial_objective_id}")

        # Call parent enter method
        super().enter()

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/library.json"

    def launch_activity(self, activity_name):
        """Launch the appropriate activity based on the name"""
        if activity_name == 'apartment_search':
            self.launch_apartment_search()
        elif activity_name == 'facebook_search':
            self.launch_facebook_search()
        elif activity_name == 'text_everyone':
            self.launch_text_everyone()
        elif activity_name == 'roommate_search':
            self.launch_roommate_search()
        elif activity_name == 'research_rights':
            self.launch_research_rights()
        else:
            super().launch_activity(activity_name)

    def launch_roommate_search(self):
        """Launch the roommate search mini-game with smooth transition"""

        def start_roommate_search():
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

        # Use professional smooth transition
        self.launch_activity_with_transition(start_roommate_search)

    def launch_research_rights(self):
        """Launch the tenant rights research mini-game with smooth transition"""

        def start_research_rights():
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

        # Use professional smooth transition
        self.launch_activity_with_transition(start_research_rights)

    def launch_apartment_search(self):
        """Launch the apartment search mini-game with smooth transition"""

        def start_apartment_search():
            from src.activities.apartment_search import ApartmentSearch

            # Create and start the activity
            if hasattr(self.game, 'objective_manager'):
                activity = ApartmentSearch(self.game.objective_manager)
                activity.narrative_ref = self
                activity.start()

                # Set as current activity both locally and on objective_manager
                self.current_activity = activity
                self.game.objective_manager.current_activity = activity
                print("Launched apartment search activity")

        # Use professional smooth transition
        self.launch_activity_with_transition(start_apartment_search)

    def launch_facebook_search(self):
        """Launch the Facebook roommate search mini-game with smooth transition"""

        def start_facebook_search():
            from src.activities.facebook_search import FacebookSearch

            # Create and start the activity
            if hasattr(self.game, 'objective_manager'):
                activity = FacebookSearch(self.game.objective_manager)
                activity.narrative_ref = self
                activity.start()

                # Set as current activity both locally and on objective_manager
                self.current_activity = activity
                self.game.objective_manager.current_activity = activity
                print("Launched Facebook search activity")

        # Use professional smooth transition
        self.launch_activity_with_transition(start_facebook_search)

    def launch_text_everyone(self):
        """Launch the mass text messaging mini-game with smooth transition"""

        def start_text_everyone():
            from src.activities.text_messaging import TextMessaging

            # Create and start the activity
            if hasattr(self.game, 'objective_manager'):
                activity = TextMessaging(self.game.objective_manager)
                activity.narrative_ref = self
                activity.start()

                # Set as current activity both locally and on objective_manager
                self.current_activity = activity
                self.game.objective_manager.current_activity = activity
                print("Launched text messaging activity")

        # Use professional smooth transition
        self.launch_activity_with_transition(start_text_everyone)

    def update_objective_display(self):
        """Update objective text based on library progress (original integration)"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'apartment_search':
            if not self.search_complete:
                current.dynamic_description = "Search for apartments online"
                current.progress_text = "Use the computer to search"
            elif self.search_complete:
                current.dynamic_description = "No affordable options found"
                current.progress_text = f"Searched {self.listings_found} listings"

    def add_exit_interaction(self):
        """Add the exit door after completing search (original integration)"""
        if hasattr(self, 'add_interactive_object'):
            exit_data = {
                'position': (8, 11),
                'prompt': 'Leave library',
                'dialogue': [
                    "You've searched every listing site. Nothing is affordable.",
                    "Every place wants 3x income, credit history, and huge deposits.",
                    "With $73 to your name and no job, you're locked out of everything."
                ]
            }
            self.add_interactive_object('exit_door', exit_data)

    def handle_event(self, event):
        """Handle events, routing to activity if active"""
        # Check for active activity - check all possible sources
        activity = self.current_activity
        if not activity or not getattr(activity, 'active', False):
            # Fallback to objective_manager's activity
            activity = getattr(self.game.objective_manager, 'current_activity', None)
        if not activity or not getattr(activity, 'active', False):
            # Fallback to activity_manager's activity (UAM)
            am = getattr(self.game.objective_manager, 'activity_manager', None)
            if am:
                activity = getattr(am, 'current_activity', None)

        # If an activity is active, route events to it
        if activity and hasattr(activity, 'active') and activity.active:
            print(f"[LIBRARY_EVENT] Routing {event.type} to activity: {activity.__class__.__name__}")
            if event.type == pygame.KEYDOWN:
                if hasattr(activity, 'handle_key'):
                    activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(f"[LIBRARY_EVENT] Mouse click at {event.pos} -> activity.handle_mouse_click")
                if hasattr(activity, 'handle_mouse_click'):
                    activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(activity, 'handle_mouse_motion'):
                    activity.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(activity, 'handle_mouse_release'):
                    activity.handle_mouse_release(event.pos, event.button)
            return  # Don't process other events during activity

        # Otherwise use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update the interior and any active activity"""
        super().update(dt)

        # Update activity if active
        if self.current_activity and hasattr(self.current_activity, 'active') and self.current_activity.active:
            self.current_activity.update(dt)

        # Check if objective has changed (indicating completion)
        if self.initial_objective_id and not getattr(self, 'should_exit', False):
            current_obj = self.game.objective_manager.get_current_objective()
            current_obj_id = current_obj.id if current_obj else None

            if current_obj_id != self.initial_objective_id:
                print(f"[LIBRARY_EXIT] Objective changed from {self.initial_objective_id} to {current_obj_id} - triggering exit")
                self.should_exit = True
                self.exit_timer = 1.5  # Give time to read any completion messages

        # Base class handles exit timer automatically - no need for duplicate logic

    def draw(self, screen):
        """Draw library interior with activity overlay"""
        # Draw base interior FIRST
        super().draw(screen)

        # Then draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'apartment_search': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "Looking for housing?"),
                    ("You", "Yeah, I need an apartment."),
                    ("Librarian", "The computers have internet access."),
                    ("Librarian", "Try Realter.com, Facebook, anywhere you can find listings.")
                ],
                'interactions': {
                    'computer_station': {
                        'position': (8, 7),
                        'prompt': 'Use computer',
                        'trigger_activity': 'apartment_search',
                    }
                }
            },
            'facebook_search': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "Back again? Still looking for housing?"),
                    ("You", "Apartments are impossible. Looking for roommates now."),
                    ("Librarian", "Facebook groups are your best bet."),
                    ("Librarian", "Try 'Housing for Students' or 'Roommate Finder' groups.")
                ],
                'interactions': {
                    'computer': {
                        'position': (5, 6),
                        'prompt': 'Search Facebook for roommates',
                        'trigger_activity': 'facebook_search',
                    }
                }
            },
            'text_everyone': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "You look stressed. Everything okay?"),
                    ("You", "My roommate bailed. Need a place to crash tonight."),
                    ("Librarian", "That's rough. Free WiFi here if you need to contact people."),
                    ("You", "Thanks. Going to text everyone I know.")
                ],
                'interactions': {
                    'computer': {
                        'position': (5, 6),
                        'prompt': 'Send mass text for help',
                        'trigger_activity': 'text_everyone',
                    }
                }
            },
            'roommate_search': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Librarian", "Looking for roommate listings?"),
                    ("You", "Yeah, my rent just went up 15%."),
                    ("Librarian", "Try Facebook groups and Realtor.com."),
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

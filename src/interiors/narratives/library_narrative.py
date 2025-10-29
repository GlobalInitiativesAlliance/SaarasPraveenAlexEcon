"""
Library Interior with Apartment Search Narrative
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class LibraryNarrative(NarrativeInterior):
    """Library with apartment search narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track search progress
        self.search_complete = False
        self.listings_found = 0
        self.facebook_search_complete = False
        self.alex_found = False
        self.current_activity = None

        # Exit timer for auto-exit after completion
        self.should_exit = False
        self.exit_timer = 0

    def enter(self):
        """Override enter to set up library scene"""
        super().enter()

        # Add computer stations immediately
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'apartment_search':
            interactions = self.narrative_content['apartment_search']['interactions']
            if 'computer_station' in interactions:
                self.add_interactive_object('computer_station', interactions['computer_station'])
                if 'computer_station' in self.completed_interactions:
                    self.completed_interactions.remove('computer_station')

        self.update_objective_display()

    def load_narrative_content(self):
        """Load the library narrative content"""
        return {
            'apartment_search': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4},
                    {'name': 'Job Seeker', 'x': 5, 'y': 7},
                    {'name': 'Student', 'x': 11, 'y': 7}
                ],
                'dialogue_sequence': [
                    (None, "After a restless night at the shelter, you arrive at the library as soon as it opens."),
                    ("Librarian", "You're here early! Looking for housing?"),
                    ("You", "Yes... I stayed at the emergency shelter last night. I need to find something real."),
                    ("Librarian", "Oh honey... The shelter only gives you 30 days, right? The rental market is brutal right now."),
                    ("You", "30 days. That's all I have."),
                    ("Librarian", "The computers are free to use. Try Craigslist and Apartments.com, but... manage your expectations."),
                    (None, "You notice several other people hunched over computers, also desperately searching."),
                    (None, "The competition for affordable housing is fierce. You're not the only one struggling.")
                ],
                'interactions': {
                    'computer_station': {
                        'position': (8, 7),
                        'prompt': 'Use computer',
                        'trigger_activity': 'apartment_search',  # Launch the mini-game
                        'dialogue': None,
                        'required': True
                    },
                    'exit_door': {
                        'position': (8, 11),
                        'prompt': 'Leave library',
                        'dialogue': [
                            "You've searched every listing site. Nothing is affordable.",
                            "Every place wants 3x income, credit history, and huge deposits.",
                            "With $73 to your name and no job, you're locked out of everything.",
                            "Maybe you should check that one listing again... the $1400 studio.",
                            "It's the cheapest thing available. Worth a try?"
                        ],
                        'required': False
                    }
                }
            },

            'search_complete': {
                'dialogue_sequence': [
                    (None, "Search Results: 0 affordable options found."),
                    ("Job Seeker", "Any luck? I've been looking for weeks..."),
                    ("You", "Everything needs proof of income three times the rent. How is that even possible?"),
                    ("Job Seeker", "Welcome to the housing crisis. I'm sleeping in my car."),
                    (None, "The reality sinks in. This isn't going to be easy."),
                    (None, "Maybe that overpriced studio is your only shot...")
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on library progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'apartment_search':
            if self.narrative_active and self.sequence_index < 4:
                current.dynamic_description = "Listen to the librarian..."
            elif not self.search_complete:
                current.dynamic_description = "Search for apartments online"
                current.progress_text = "Use the computer to search"
            elif self.search_complete and 'exit_door' not in self.completed_interactions:
                current.dynamic_description = "No affordable options found"
                current.progress_text = f"Searched {self.listings_found} listings"
            elif 'exit_door' in self.completed_interactions:
                current.dynamic_description = "Leaving to check the studio apartment..."
                current.progress_text = None

        elif current.id == 'facebook_search':
            if self.narrative_active and self.sequence_index < 4:
                current.dynamic_description = "Considering informal housing options..."
            elif not self.facebook_search_complete:
                current.dynamic_description = "Search Facebook for roommates"
                current.progress_text = "Try social media"
            elif self.facebook_search_complete and not self.alex_found:
                current.dynamic_description = "Processing what you found..."
                current.progress_text = "Found a possibility"
            elif self.alex_found and 'exit_to_alex' not in self.completed_interactions:
                current.dynamic_description = "Alex is willing to rent to you"
                current.progress_text = "Go meet them"
            else:
                current.dynamic_description = "Heading to Alex's apartment..."

    def interact_with_object(self, name):
        """Handle library-specific interactions"""
        print(f"DEBUG: Interacting with {name}")
        print(f"DEBUG: Current activity: {self.current_activity}")
        print(f"DEBUG: Search complete: {self.search_complete}")

        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'apartment_search'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            # Check if already completed search
            if trigger == 'apartment_search' and self.search_complete:
                self.dialogue_box.show(None, "You've already searched. Nothing has changed in the last 5 minutes.")
                return

            if trigger == 'apartment_search':
                print("DEBUG: Launching apartment search")
                self.launch_apartment_search()
                return

        # Handle non-activity interactions
        if name != 'computer_station':
            super().interact_with_object(name)

        self.update_objective_display()

        # Handle exit door completion
        if name == 'exit_door' and 'exit_door' in self.completed_interactions:
            current = self.game.objective_manager.get_current_objective()
            if current and current.id == 'apartment_search':
                # Start exit timer to let final dialogue show
                self.should_exit = True
                self.exit_timer = 3.0  # 3 seconds to read the final messages

    def launch_apartment_search(self):
        """Launch the apartment search mini-game"""
        from src.activities.apartment_search import ApartmentSearch

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = ApartmentSearch(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def add_exit_interaction(self):
        """Add the exit door after completing search"""
        if 'apartment_search' in self.narrative_content:
            exit_data = self.narrative_content['apartment_search']['interactions']['exit_door']
            self.add_interactive_object('exit_door', exit_data)

            # Show completion message
            self.dialogue_box.show(None, "You've searched everything. Time to face reality.")

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            print(f"DEBUG: Activity is active, blocking other events")
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current = self.game.objective_manager.get_current_objective()

                if current and current.id == 'apartment_search':
                    if not self.search_complete:
                        self.dialogue_box.show(None, "You need to search for apartments first!")
                        return
                    elif 'exit_door' not in self.completed_interactions:
                        self.dialogue_box.show(None, "You should leave through the exit.")
                        return
                elif current and current.id == 'facebook_search':
                    if not self.facebook_search_complete:
                        self.dialogue_box.show(None, "You need to search Facebook first!")
                        return
                    elif 'exit_to_alex' not in self.completed_interactions:
                        self.dialogue_box.show(None, "You should go meet Alex.")
                        return

        # Use parent's event handling
        super().handle_event(event)

    def get_nearby_object(self):
        """Allow re-interaction with computer"""
        player_tile_x = int(self.player_pixel_x // self.TILE_SIZE)
        player_tile_y = int(self.player_pixel_y // self.TILE_SIZE)

        for name, obj in self.interactive_objects.items():
            # Always allow computer interaction
            if name == 'computer_station':
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj
            # Normal logic for other objects
            elif name not in self.completed_interactions:
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj

        return None, None

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                # Mark search as complete
                self.search_complete = True
                self.listings_found = self.current_activity.listings_viewed if hasattr(self.current_activity, 'listings_viewed') else 15
                self.update_objective_display()

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Add exit door interaction
                self.add_exit_interaction()

                # Start the search complete narrative
                if 'search_complete' in self.narrative_content:
                    self.start_narrative_sequence('search_complete')

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Complete objective and exit
                self.game.objective_manager.complete_current_objective()
                self.active = False
                # Show a message about the next step
                if hasattr(self, 'dialogue_box'):
                    self.dialogue_box.show(None, "Time to check out that studio apartment...")

    def draw(self, screen):
        """Draw library interior with activity overlay"""
        # Draw base interior
        super().draw(screen)

        # Always show computer station even if "completed"
        if 'computer_station' in self.interactive_objects and 'computer_station' in self.completed_interactions:
            obj = self.interactive_objects['computer_station']
            obj_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + obj['x'] * self.TILE_SIZE
            obj_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + obj['y'] * self.TILE_SIZE

            # Draw with green tint if completed
            if self.search_complete:
                pygame.draw.rect(screen, (100, 200, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)
            else:
                pygame.draw.rect(screen, (255, 220, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return

        # Draw status in corner
        if self.search_complete:
            font = pygame.font.Font(None, 24)
            status_text = f"✓ Searched {self.listings_found} listings"
            status_surf = font.render(status_text, True, (100, 255, 100))
            screen.blit(status_surf, (10, 10))

            result_text = "0 affordable options"
            result_surf = font.render(result_text, True, (255, 100, 100))
            screen.blit(result_surf, (10, 40))
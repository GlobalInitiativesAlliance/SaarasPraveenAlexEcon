"""
Foster Home Interior with Aging Out Narrative
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class FosterHomeNarrative(NarrativeInterior):
    """Foster home with aging out narrative sequence"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track packing progress
        self.items_packed = set()
        self.required_items = {'clothes', 'documents', 'photo'}

        # Exit timer for door interaction
        self.exit_timer = 0
        self.should_exit = False

        # Activity management
        self.current_activity = None

    def enter(self):
        """Override enter to update objective display"""
        super().enter()

        # Add packing objects immediately (visible from start)
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'housing_intro':
                # Add the three packing objects right away so they're visible
                interactions = self.narrative_content['housing_intro']['interactions']
                for obj_name in ['closet', 'desk', 'nightstand']:
                    if obj_name in interactions:
                        # Always add these as interactive, even if already in completed_interactions
                        self.add_interactive_object(obj_name, interactions[obj_name])
                        # Remove from completed interactions to allow re-interaction
                        if obj_name in self.completed_interactions:
                            self.completed_interactions.remove(obj_name)

            elif current.id in ['tlp_rules', 'eighteen_months']:
                # Handle TLP objectives
                interactions = self.narrative_content.get(current.id, {}).get('interactions', {})
                for obj_name, obj_data in interactions.items():
                    self.add_interactive_object(obj_name, obj_data)
                # Start the narrative sequence
                self.start_narrative_sequence(current.id)

        # Update objective display when entering
        self.update_objective_display()

    def show_next_dialogue(self):
        """Override to update objective during dialogue"""
        super().show_next_dialogue()
        # Update objective display as dialogue progresses
        self.update_objective_display()

    def end_narrative_sequence(self):
        """Override to update when narrative ends"""
        super().end_narrative_sequence()
        # Update objective display when dialogue completes
        self.update_objective_display()

    def load_narrative_content(self):
        """Load the foster home narrative content"""
        return {
            # First objective: Aging out introduction
            'housing_intro': {
                'npcs': [
                    {'name': 'Foster Parent', 'x': 8, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Foster Parent", "Happy 18th birthday. I know this is hard, but you know the rules."),
                    ("Foster Parent", "Foster care ends at 18. You need to pack your things today."),
                    ("You", "Today? But I don't have anywhere to go..."),
                    ("Foster Parent", "I'm sorry, but those are the state regulations. You have until noon."),
                    ("Foster Parent", "Pack your essentials - clothes, documents, and anything personal you want to keep."),
                    (None, "You feel a knot in your stomach. This is really happening.")
                ],
                'interactions': {
                    'closet': {
                        'position': (3, 3),
                        'prompt': 'Open closet',
                        'trigger_activity': 'clothes_packing',  # Launch the mini-game
                        'dialogue': None,  # No dialogue, uses activity instead
                        'required': True
                    },
                    'desk': {
                        'position': (12, 8),
                        'prompt': 'Search desk drawers',
                        'trigger_activity': 'document_search',  # Launch the mini-game
                        'dialogue': None,  # No dialogue, uses activity instead
                        'required': True
                    },
                    'nightstand': {
                        'position': (3, 6),
                        'prompt': 'Look through photos',
                        'trigger_activity': 'photo_selection',  # Launch the mini-game
                        'dialogue': None,  # No dialogue, uses activity instead
                        'required': True
                    },
                    'door': {
                        'position': (8, 11),
                        'prompt': 'Leave foster home',
                        'dialogue': [
                            "You stand at the door with your backpack. Seven years in this house, and now...",
                            "The foster parent watches from the kitchen, says nothing.",
                            "Once you leave, you can't come back. This is it.",
                            "You step outside. The door clicks shut behind you. You're on your own now."
                        ],
                        'required': False  # Only available after packing
                    }
                }
            },

            # Second objective: Reality check
            'reality_check': {
                'dialogue_sequence': [
                    (None, "You're standing outside the foster home with nowhere to go."),
                    (None, "Your phone shows 12% battery. You have $73 in your pocket."),
                    (None, "No family to call. No couch to crash on. No backup plan."),
                    (None, "You remember hearing about an emergency shelter downtown."),
                    (None, "Maybe they have beds available. You start walking.")
                ],
                'interactions': {}
            },

            'tlp_rules': {
                'dialogue_sequence': [
                    (None, "TLP Housing - Your new home for the next 24 months."),
                    ("House Manager", "Welcome! Let me show you the rules."),
                    ("House Manager", "Shared room with one roommate. Keep it clean."),
                    ("House Manager", "Curfew is 10 PM sharp. Three violations and you're out."),
                    ("House Manager", "Mandatory life skills meetings every Tuesday."),
                    ("House Manager", "Save 30% of your income. We check monthly."),
                    ("House Manager", "No overnight guests. No substances. No excuses."),
                    ("You", "I understand. I'm just grateful to be here."),
                    ("House Manager", "Work hard. Save money. You have 24 months to get stable."),
                    (None, "It's restrictive. But after 6 months of chaos, restrictions feel like safety.")
                ],
                'interactions': {
                    'your_bed': {
                        'position': (10, 6),
                        'prompt': 'Sit on bed',
                        'dialogue': [
                            "Your own bed. First time in 6 months.",
                            "You sit on the bed. It's firm but clean.",
                            "Your own bed. Not a couch, not a floor.",
                            "You can stay here for 24 months.",
                            "Time to rebuild."
                        ],
                        'required': True
                    },
                    'rules_poster': {
                        'position': (7, 3),
                        'prompt': 'Read house rules',
                        'dialogue': [
                            "TLP House Rules:",
                            "1. Curfew: 10 PM (No exceptions)",
                            "2. Savings: 30% of income mandatory",
                            "3. Meetings: Tuesday 7 PM (Required)",
                            "4. Chores: See weekly schedule",
                            "5. Guests: No overnight visitors",
                            "6. Substances: Zero tolerance",
                            "Breaking rules = losing housing. Again."
                        ],
                        'required': False
                    }
                }
            },

            'eighteen_months': {
                'dialogue_sequence': [
                    (None, "18 months at the TLP. 6 months left."),
                    (None, "You've been working. Saving. Going to community college."),
                    (None, "Bank account: $1,800 saved."),
                    (None, "But apartments still need first, last, and deposit."),
                    (None, "That's $4,200 for a $1,400 apartment."),
                    (None, "You're $2,400 short. With 6 months left."),
                    (None, "The clock is ticking.")
                ],
                'interactions': {
                    'savings_book': {
                        'position': (8, 5),
                        'prompt': 'Check savings',
                        'dialogue': [
                            "Your savings record book.",
                            "18 months of saving $100/month.",
                            "Total saved: $1,800",
                            "Needed for apartment: $4,200",
                            "Still need: $2,400",
                            "Time remaining at TLP: 6 months",
                            "The math doesn't work."
                        ],
                        'required': True
                    },
                    'calendar': {
                        'position': (5, 3),
                        'prompt': 'Check calendar',
                        'dialogue': [
                            "Month 18 of 24 at TLP.",
                            "Red X marks: 6 months remaining.",
                            "You've circled apartment viewing dates.",
                            "All crossed out - 'Need more savings'",
                            "The deadline approaches."
                        ],
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'housing_intro':
            # Update based on narrative state
            if self.narrative_active and self.sequence_index < 4:
                # During initial dialogue with foster parent
                current.dynamic_description = "Listen to your foster parent..."
            elif len(self.items_packed) < 3:
                # Packing phase
                packed = len(self.items_packed)
                current.dynamic_description = f"Pack your belongings ({packed}/3)"

                # Add specific hints for what's left
                if packed > 0:
                    remaining = []
                    if 'clothes' not in self.items_packed:
                        remaining.append("clothes from closet")
                    if 'documents' not in self.items_packed:
                        remaining.append("documents from desk")
                    if 'photo' not in self.items_packed:
                        remaining.append("photo from nightstand")
                    if remaining:
                        current.progress_text = "Need: " + ", ".join(remaining[:2])  # Show max 2 items
                else:
                    current.progress_text = "Look for closet, desk, and nightstand"
            elif self.items_packed == self.required_items and 'door' not in self.completed_interactions:
                # All packed, ready to leave
                current.dynamic_description = "Everything packed. Time to leave..."
                current.progress_text = "Find the door"
            elif 'door' in self.completed_interactions:
                current.dynamic_description = "Leaving foster care forever..."
                current.progress_text = None

        elif current.id == 'reality_check':
            # For the second objective
            if self.narrative_active:
                current.dynamic_description = "Reality is setting in..."
            else:
                current.dynamic_description = "You're on your own now"

        elif current.id == 'tlp_rules':
            if self.narrative_active:
                current.dynamic_description = "Learning the TLP house rules..."
            else:
                current.dynamic_description = "Your new home for 24 months"
                current.progress_text = "Read the rules, check your bed"

        elif current.id == 'eighteen_months':
            if self.narrative_active:
                current.dynamic_description = "Checking your savings progress..."
            else:
                current.dynamic_description = "Still $2,400 short with 6 months left"
                current.progress_text = "Check your savings book"

    def interact_with_object(self, name):
        """Handle special interactions for packing"""
        print(f"DEBUG: Interacting with {name}")
        print(f"DEBUG: Current activity: {self.current_activity}")
        print(f"DEBUG: Items packed: {self.items_packed}")

        # Check if this interaction triggers an activity
        # Get current objective to determine which narrative content to use
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'housing_intro'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            # Check if this item has already been packed
            item_map = {
                'closet': 'clothes',
                'desk': 'documents',
                'nightstand': 'photo'
            }

            # If this is a packing activity and already packed, show a message instead
            if trigger and name in item_map and item_map[name] in self.items_packed:
                self.dialogue_box.show(None, f"You've already packed your {item_map[name]}.")
                return

            if trigger == 'clothes_packing':
                print("DEBUG: Launching clothes packing")
                self.launch_clothes_packing()
                return  # Don't process normal interaction
            elif trigger == 'document_search':
                print("DEBUG: Launching document search")
                self.launch_document_search()
                return  # Don't process normal interaction
            elif trigger == 'photo_selection':
                print("DEBUG: Launching photo selection")
                self.launch_photo_selection()
                return  # Don't process normal interaction

        # Note: items_packed is now handled by the mini-games themselves

        # Only call parent interaction for non-activity objects (like the door)
        if name not in ['closet', 'desk', 'nightstand']:
            super().interact_with_object(name)

        # Update objective display after interaction
        self.update_objective_display()

        # Special handling for door interaction
        if name == 'door' and 'door' in self.completed_interactions:
            # Complete objective and prepare to exit
            current = self.game.objective_manager.get_current_objective()
            if current and current.id == 'housing_intro':
                # Start exit timer to let final dialogue show
                self.should_exit = True
                self.exit_timer = 2.0  # 2 seconds

        # Check if all required items are packed
        if self.items_packed == self.required_items:
            # Enable the door interaction
            if 'door' not in self.completed_interactions:
                self.add_door_interaction()

    def launch_clothes_packing(self):
        """Launch the clothes packing mini-game"""
        from src.activities.activities import ClothesPacking

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = ClothesPacking(self.game.objective_manager)
            activity.foster_home_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_document_search(self):
        """Launch the document search mini-game"""
        from src.activities.document_search import DocumentSearch

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = DocumentSearch(self.game.objective_manager)
            activity.foster_home_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_photo_selection(self):
        """Launch the photo selection mini-game"""
        from src.activities.photo_selection import PhotoSelection

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = PhotoSelection(self.game.objective_manager)
            activity.foster_home_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def add_door_interaction(self):
        """Add the final door interaction after packing"""
        # Make door visible as interactive
        if 'housing_intro' in self.narrative_content:
            door_data = self.narrative_content['housing_intro']['interactions']['door']
            self.add_interactive_object('door', door_data)

            # Show a message
            self.dialogue_box.show(None, "You've packed everything. Time to leave.")

    def handle_event(self, event):
        """Override to prevent exit until tasks complete"""
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
            return  # Don't process other events during activity

        if event.type == pygame.KEYDOWN:
            # Block ESC exit if tasks not complete
            if event.key == pygame.K_ESCAPE:
                current = self.game.objective_manager.get_current_objective()

                if current and current.id == 'housing_intro':
                    # Can't leave until you've packed and used the door
                    if 'door' not in self.completed_interactions:
                        # Show message that you can't leave yet
                        if self.items_packed != self.required_items:
                            self.dialogue_box.show(None, "You need to pack your belongings before leaving!")
                        else:
                            self.dialogue_box.show(None, "Use the door to leave the foster home.")
                        return  # Don't process ESC
                    else:
                        # Completed the objective, advance and exit
                        self.game.objective_manager.complete_current_objective()
                        self.active = False
                        return

        # Otherwise use parent's event handling
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            print(f"DEBUG: E key pressed, calling parent's handle_event")
        super().handle_event(event)

    def get_nearby_object(self):
        """Override to always allow interaction with packing objects"""
        player_tile_x = int(self.player_pixel_x // self.TILE_SIZE)
        player_tile_y = int(self.player_pixel_y // self.TILE_SIZE)

        for name, obj in self.interactive_objects.items():
            # For packing objects, allow interaction even if "completed"
            if name in ['closet', 'desk', 'nightstand']:
                # Check if player is adjacent to object
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj
            # For other objects, use normal logic
            elif name not in self.completed_interactions:
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj

        return None, None

    def check_objective_complete(self):
        """Check if the objective is complete"""
        current = self.game.objective_manager.get_current_objective()

        if current and current.id == 'housing_intro':
            # Complete when player interacts with door
            return 'door' in self.completed_interactions
        elif current and current.id == 'reality_check':
            # Complete after dialogue sequence
            return not self.narrative_active

        return True

    def update(self, dt):
        """Update method to handle exit timer and activity"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                # Activities handle adding to items_packed themselves through their foster_home_ref
                self.update_objective_display()

                # Clear the current activity completely
                self.current_activity = None

                # Also clear it from the objective manager if it has one
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Check if all required items are now packed
                if self.items_packed == self.required_items:
                    self.add_door_interaction()

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Complete objective and exit
                self.game.objective_manager.complete_current_objective()
                self.active = False

    def draw(self, screen):
        """Draw the foster home interior with visual indicators"""
        # Draw base interior (but we need to handle interactive objects specially)
        super().draw(screen)

        # Always draw packing objects even if "completed"
        packing_objects = ['closet', 'desk', 'nightstand']
        for name in packing_objects:
            if name in self.interactive_objects and name in self.completed_interactions:
                obj = self.interactive_objects[name]
                obj_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + obj['x'] * self.TILE_SIZE
                obj_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + obj['y'] * self.TILE_SIZE

                # Draw the object with a different color if already packed
                item_map = {'closet': 'clothes', 'desk': 'documents', 'nightstand': 'photo'}
                if item_map.get(name) in self.items_packed:
                    # Draw with green tint for packed items
                    pygame.draw.rect(screen, (100, 200, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)
                else:
                    # Draw with normal yellow glow for unpacked
                    pygame.draw.rect(screen, (255, 220, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return  # Don't draw other UI when activity is active

        # Draw packed status in corner
        if self.items_packed:
            font = pygame.font.Font(None, 22)
            y_offset = 10

            # Draw packed items list
            for item in ['clothes', 'documents', 'photo']:
                color = (100, 255, 100) if item in self.items_packed else (150, 150, 150)
                text = f"✓ {item.capitalize()}" if item in self.items_packed else f"  {item.capitalize()}"
                item_surf = font.render(text, True, color)
                screen.blit(item_surf, (10, y_offset))
                y_offset += 25

            # Show completion status
            if self.items_packed == self.required_items:
                ready_surf = font.render("Ready to leave", True, (255, 220, 100))
                screen.blit(ready_surf, (10, y_offset + 10))
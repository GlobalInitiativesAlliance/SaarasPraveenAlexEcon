"""
Foster Home Aging Out Scene - Clean Single-Purpose Interior
Handles ONLY the 'housing_intro' objective where player packs and leaves foster care
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class FosterHomeAgingOut(NarrativeInterior):
    """Foster home aging out scene - single objective only"""

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

        # Add packing objects immediately for housing_intro
        interactions = self.narrative_content['housing_intro']['interactions']
        for obj_name in ['closet', 'desk', 'nightstand']:
            if obj_name in interactions:
                self.add_interactive_object(obj_name, interactions[obj_name])
                # Remove from completed interactions to allow re-interaction
                if obj_name in self.completed_interactions:
                    self.completed_interactions.remove(obj_name)

        # Update objective display when entering
        self.update_objective_display()

    def load_narrative_content(self):
        """Load ONLY the aging out narrative content"""
        return {
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
                        'trigger_activity': 'clothes_packing',
                        'dialogue': None,
                        'required': True
                    },
                    'desk': {
                        'position': (12, 8),
                        'prompt': 'Search desk drawers',
                        'trigger_activity': 'document_search',
                        'dialogue': None,
                        'required': True
                    },
                    'nightstand': {
                        'position': (3, 6),
                        'prompt': 'Look through photos',
                        'trigger_activity': 'photo_selection',
                        'dialogue': None,
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
                        current.progress_text = "Need: " + ", ".join(remaining[:2])
                else:
                    current.progress_text = "Look for closet, desk, and nightstand"
            elif self.items_packed == self.required_items and 'door' not in self.completed_interactions:
                # All packed, ready to leave
                current.dynamic_description = "Everything packed. Time to leave..."
                current.progress_text = "Find the door"
            elif 'door' in self.completed_interactions:
                current.dynamic_description = "Leaving foster care forever..."
                current.progress_text = None

    def interact_with_object(self, name):
        """Handle special interactions for packing"""
        print(f"DEBUG: Interacting with {name}")

        # Get interactions for housing_intro only
        interactions = self.narrative_content['housing_intro']['interactions']

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
                self.launch_clothes_packing()
                return
            elif trigger == 'document_search':
                self.launch_document_search()
                return
            elif trigger == 'photo_selection':
                self.launch_photo_selection()
                return

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
                self.exit_timer = 2.0

        # Check if all required items are packed
        if self.items_packed == self.required_items:
            # Enable the door interaction
            if 'door' not in self.completed_interactions:
                self.add_door_interaction()

    def launch_clothes_packing(self):
        """Launch the clothes packing mini-game"""
        from src.activities.activities import ClothesPacking

        if hasattr(self.game, 'objective_manager'):
            activity = ClothesPacking(self.game.objective_manager)
            activity.foster_home_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_document_search(self):
        """Launch the document search mini-game"""
        from src.activities.document_search import DocumentSearch

        if hasattr(self.game, 'objective_manager'):
            activity = DocumentSearch(self.game.objective_manager)
            activity.foster_home_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_photo_selection(self):
        """Launch the photo selection mini-game"""
        from src.activities.photo_selection import PhotoSelection

        if hasattr(self.game, 'objective_manager'):
            activity = PhotoSelection(self.game.objective_manager)
            activity.foster_home_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def add_door_interaction(self):
        """Add the final door interaction after packing"""
        door_data = self.narrative_content['housing_intro']['interactions']['door']
        self.add_interactive_object('door', door_data)
        self.dialogue_box.show(None, "You've packed everything. Time to leave.")

    def handle_event(self, event):
        """Override to prevent exit until tasks complete"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
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
            # Block ESC exit if tasks not complete
            if event.key == pygame.K_ESCAPE:
                current = self.game.objective_manager.get_current_objective()

                if current and current.id == 'housing_intro':
                    # Can't leave until you've packed and used the door
                    if 'door' not in self.completed_interactions:
                        if self.items_packed != self.required_items:
                            self.dialogue_box.show(None, "You need to pack your belongings before leaving!")
                        else:
                            self.dialogue_box.show(None, "Use the door to leave the foster home.")
                        return
                    else:
                        # Completed the objective, advance and exit
                        self.game.objective_manager.complete_current_objective()
                        self.active = False
                        return

        # Otherwise use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update method to handle exit timer and activity"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                self.update_objective_display()
                self.current_activity = None

                # Clear from objective manager
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
            return

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
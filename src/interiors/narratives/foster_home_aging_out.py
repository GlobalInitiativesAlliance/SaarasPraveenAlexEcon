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
        self.objective_completed = False

        # Activity management
        self.current_activity = None

        # Simple narrative handling for non-packing objectives
        self.simple_narrative_active = False
        self.current_dialogue_sequence = []
        self.dialogue_sequence_index = 0

    def enter(self):
        """Override enter to update objective display"""
        super().enter()

        # Check current objective
        current_objective = None
        if hasattr(self.game, 'objective_manager'):
            obj = self.game.objective_manager.get_current_objective()
            if obj:
                current_objective = obj.id

        # Only add packing objects for housing_intro and tlp_rules
        if current_objective in ['housing_intro', 'tlp_rules']:
            interactions = self.narrative_content['housing_intro']['interactions']
            for obj_name in ['closet', 'desk', 'nightstand']:
                if obj_name in interactions:
                    self.add_interactive_object(obj_name, interactions[obj_name])
                    # Remove from completed interactions to allow re-interaction
                    if obj_name in self.completed_interactions:
                        self.completed_interactions.remove(obj_name)
        else:
            # For other objectives (eighteen_months, not_alone), just show dialogue and exit
            print(f"[FOSTER_HOME] Objective {current_objective} - showing simple narrative")
            self._show_objective_narrative(current_objective)

        # Update objective display when entering
        self.update_objective_display()

    def _show_objective_narrative(self, objective_id):
        """Show narrative for objectives that don't need activities"""
        narratives = {
            'eighteen_months': [
                "18 months at the TLP. You've made it work.",
                "Worked part-time at the grocery store. Community college classes.",
                "Saved $1,800. Still need more for an apartment deposit.",
                "But time's running out. TLP has a 24-month maximum."
            ],
            'not_alone': [
                "You made it. Against all odds, you found stable housing.",
                "It wasn't easy. The system wasn't designed to help you succeed.",
                "But you're here now. And you're not alone anymore."
            ]
        }

        if objective_id in narratives:
            # Show dialogue sequence
            dialogue = narratives[objective_id]
            self.current_dialogue_sequence = dialogue
            self.dialogue_sequence_index = 0
            self.simple_narrative_active = True
            self.dialogue_box.show(None, dialogue[0])
        else:
            # No narrative - just exit
            self.should_exit = True
            self.exit_timer = 0.5

    def check_objective_complete(self):
        """Override to require all items packed before objective can complete"""
        # Don't allow completion until all 3 required items are packed
        if len(self.items_packed) < len(self.required_items):
            print(f"[FOSTER_HOME] check_objective_complete: {len(self.items_packed)}/{len(self.required_items)} items packed - NOT complete")
            return False
        print(f"[FOSTER_HOME] check_objective_complete: All {len(self.required_items)} items packed - ready for door")
        return False  # Still return False - door interaction handles completion

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
                        'position': (8, 11),  # Bottom edge - zone system allows access
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
            if current and not self.objective_completed:
                # Works for housing_intro, tlp_rules, or any objective at this location
                print(f"[FOSTER_HOME] Door exit - completing objective: {current.id}")
                self.game.objective_manager.advance_to_next_objective()
                self.objective_completed = True
                # Start exit timer to let UI update
                self.should_exit = True
                self.exit_timer = 1.0

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
        print(f"[FOSTER_HOME] add_door_interaction() called")
        door_data = self.narrative_content['housing_intro']['interactions']['door']
        print(f"[FOSTER_HOME] Door data: {door_data}")
        self.add_interactive_object('door', door_data)
        print(f"[FOSTER_HOME] Door added to interactive_objects: {'door' in self.interactive_objects}")
        print(f"[FOSTER_HOME] Door position: tile ({door_data['position'][0]}, {door_data['position'][1]})")
        print(f"[FOSTER_HOME] Walk to the bottom center of the room and press E to leave!")
        self.dialogue_box.show(None, "You've packed everything. Walk down toward the bottom of the room and press E near the door to leave.")

    def handle_event(self, event):
        """Override to prevent exit until tasks complete"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                # Check for ESC even during activities (but still respect completion requirements)
                if event.key == pygame.K_ESCAPE:
                    current = self.game.objective_manager.get_current_objective()
                    if current and current.id == 'housing_intro':
                        if 'door' not in self.completed_interactions:
                            if self.items_packed != self.required_items:
                                self.dialogue_box.show(None, "You need to pack your belongings before leaving!")
                                return
                            else:
                                self.dialogue_box.show(None, "Use the door to leave!")
                                return
                    # If we reach here, allow exit
                    self.active = False
                    return
                # Only forward non-printable keys to avoid double-processing with TEXTINPUT
                if event.key < 32 or event.key > 126:  # Non-printable keys only
                    self.current_activity.handle_key(event.key)
                else:
                    # For printable characters, only forward if activity doesn't support text input
                    if not hasattr(self.current_activity, 'handle_text_input'):
                        self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            return

        # Handle simple narrative progression
        if self.simple_narrative_active:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
                self.dialogue_sequence_index += 1
                if self.dialogue_sequence_index < len(self.current_dialogue_sequence):
                    self.dialogue_box.show(None, self.current_dialogue_sequence[self.dialogue_sequence_index])
                else:
                    # Done with narrative - advance objective and exit
                    self.simple_narrative_active = False
                    self.dialogue_box.active = False
                    current = self.game.objective_manager.get_current_objective()
                    if current and not self.objective_completed:
                        print(f"[FOSTER_HOME] Simple narrative complete - advancing from {current.id}")
                        self.game.objective_manager.advance_to_next_objective()
                        self.objective_completed = True
                    self.should_exit = True
                    self.exit_timer = 0.5
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
                        # Already completed the objective in interact_with_object, just exit
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
                print(f"[FOSTER_HOME] Activity completed! items_packed={self.items_packed}, required={self.required_items}")
                self.update_objective_display()

                # Mark the corresponding object as completed so autoplay doesn't re-interact
                item_to_object = {'clothes': 'closet', 'documents': 'desk', 'photo': 'nightstand'}
                for item, obj_name in item_to_object.items():
                    if item in self.items_packed and obj_name not in self.completed_interactions:
                        self.completed_interactions.add(obj_name)
                        print(f"[FOSTER_HOME] Marked {obj_name} as completed")

                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Check if all required items are now packed
                print(f"[FOSTER_HOME] Checking door: items_packed={self.items_packed} == required={self.required_items}? {self.items_packed == self.required_items}")
                if self.items_packed == self.required_items:
                    print("[FOSTER_HOME] All items packed! Adding door interaction.")
                    self.add_door_interaction()

        # Check if door dialogue finished and we should exit
        # Debug: Check door status every update
        if 'door' in self.interactive_objects:
            door_in_completed = 'door' in self.completed_interactions
            dialogue_active = self.dialogue_box.active if hasattr(self, 'dialogue_box') else False
            if door_in_completed and not self.objective_completed and not dialogue_active:
                print(f"[FOSTER_HOME_DEBUG] Door ready to exit: completed={door_in_completed}, obj_done={self.objective_completed}, dialogue={dialogue_active}")

        if 'door' in self.completed_interactions and not self.objective_completed:
            # Wait for dialogue to finish before exiting
            if hasattr(self, 'dialogue_box') and self.dialogue_box.active:
                return  # Still showing dialogue

            if self.items_packed == self.required_items:
                current = self.game.objective_manager.get_current_objective()
                if current:
                    print(f"[FOSTER_HOME] Door dialogue complete - exiting. Objective: {current.id}")
                    self.game.objective_manager.advance_to_next_objective()
                    self.objective_completed = True
                    self.should_exit = True
                    self.exit_timer = 1.0

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Exit without calling complete_current_objective again
                # since we already completed it in interact_with_object
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

        # Task progress is shown in the top-center UI panel
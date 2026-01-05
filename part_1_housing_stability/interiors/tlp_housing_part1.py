"""
Unified TLP Housing Interior - Handles Foster Home Aging Out and TLP Housing Progression
Combines housing_intro, tlp_rules, and eighteen_months objectives at position (29, 39)
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class TLPHousingUnified(NarrativeInterior):
    """Unified TLP housing narrative handling multiple stages of the housing journey"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Objective mapping
        self.objective_mapping = {
            'housing_intro': 'housing_intro',
            'tlp_rules': 'tlp_rules'
        }

        # Track packing progress (for housing_intro)
        self.items_packed = set()
        self.required_items = {'clothes', 'documents', 'photo'}

        # Activity management
        self.current_activity = None

        # Exit handling
        self.exit_timer = 0
        self.should_exit = False
        self.objective_completed = False

    def enter(self):
        """Override enter to set up appropriate scene based on current objective"""
        super().enter()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # Set up interactions based on current objective
        if current.id == 'housing_intro':
            # Add packing objects for foster home aging out
            interactions = self.narrative_content['housing_intro']['interactions']
            for obj_name in ['closet', 'desk', 'nightstand']:
                if obj_name in interactions:
                    self.add_interactive_object(obj_name, interactions[obj_name])
                    # Remove from completed to allow re-interaction
                    if obj_name in self.completed_interactions:
                        self.completed_interactions.remove(obj_name)
        elif current.id == 'tlp_rules':
            # Add interactions for TLP rules objective
            interactions = self.narrative_content['tlp_rules']['interactions']
            for obj_name, obj_data in interactions.items():
                self.add_interactive_object(obj_name, obj_data)

        # Start narrative sequence if not reloading
        if not hasattr(self, 'is_reloading') or not self.is_reloading:
            self.start_narrative_sequence(current.id)

        self.update_objective_display()

    def load_narrative_content(self):
        """Load all TLP housing narrative content"""
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
            },
            'tlp_rules': {
                'npcs': [
                    {'name': 'House Manager', 'x': 8, 'y': 3}
                ],
                'dialogue_sequence': [
                    (None, "After 6 months of homelessness, you finally made it."),
                    ("House Manager", "Welcome to Transitional Living Program! This is YOUR home for the next 24 months."),
                    ("House Manager", "You'll have a safe place to sleep, stability to work and save money."),
                    ("House Manager", "We're here to support you with life skills training every Tuesday."),
                    ("House Manager", "You'll learn budgeting, job skills, and how to maintain independent housing."),
                    ("You", "Twenty-four months... that's enough time to build a real foundation."),
                    ("House Manager", "Exactly! Most residents save enough for their own place within 18-20 months."),
                    ("House Manager", "You're going to make it. This program exists because you deserve stability."),
                    (None, "For the first time since aging out, you feel HOPE."),
                    (None, "A real chance to build your life. A safe place to call home."),
                    (None, "The nightmare of homelessness is finally over.")
                ],
                'interactions': {
                    'your_bed': {
                        'position': (10, 6),
                        'prompt': 'Sit on bed',
                        'dialogue': [
                            "Your own bed. Your own space. SAFE.",
                            "You sit on the bed and close your eyes.",
                            "No more couches. No more shelters. No more fear.",
                            "Twenty-four months to work, save, and build a future.",
                            "You made it through the hardest part.",
                            "This is where your new life begins."
                        ],
                        'required': True
                    },
                    'welcome_packet': {
                        'position': (7, 3),
                        'prompt': 'Read welcome packet',
                        'dialogue': [
                            "TRANSITIONAL LIVING PROGRAM - Welcome!",
                            "Your 24-month journey to independence starts here.",
                            "Support services available:",
                            "• Life skills training (budgeting, cooking, job skills)",
                            "• Case manager meetings to help you reach your goals",
                            "• Career counseling and job placement assistance",
                            "• Financial literacy workshops to build savings",
                            "• Mental health support and peer groups",
                            "You're not alone anymore. We're here to help you succeed."
                        ],
                        'required': True
                    }
                }
            }
        }

    def handle_auto_progression(self):
        """Custom auto-progression that stays inside for consecutive TLP housing objectives"""
        if not self.check_completion_status():
            return
        if self.completion_triggered:
            return

        self.completion_triggered = True
        self.show_objective_completion()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            self.start_exit_timer(0.5)
            return

        print(f"[TLP_UNIFIED] Objective {current.id} complete")

        current_index = self.game.objective_manager.current_objective_index
        next_index = current_index + 1

        if next_index < len(self.game.objective_manager.objectives):
            next_obj = self.game.objective_manager.objectives[next_index]

            if next_obj.target_position == (29, 39):
                print(f"[TLP_UNIFIED] Next objective '{next_obj.id}' is also here - staying inside")
                if hasattr(self.game, 'health_manager'):
                    self.game.health_manager.on_objective_complete()
                self.game.objective_manager.advance_to_next_objective()
                self.completed_interactions.clear()
                self.narrative_active = False
                self.completion_triggered = False
                # Reset objective-specific state
                if current.id == 'housing_intro':
                    self.items_packed.clear()
                    self.objective_completed = False
                self.enter()
                return

        print(f"[TLP_UNIFIED] Exiting to continue elsewhere")
        self.start_exit_timer(0.5)

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'housing_intro':
            # Foster home packing phase
            if self.narrative_active and self.sequence_index < 4:
                current.dynamic_description = "Listen to your foster parent..."
            elif len(self.items_packed) < 3:
                packed = len(self.items_packed)
                current.dynamic_description = f"Pack your belongings ({packed}/3)"
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
                current.dynamic_description = "Everything packed. Time to leave..."
                current.progress_text = "Find the door"
            elif 'door' in self.completed_interactions:
                current.dynamic_description = "Leaving foster care forever..."
                current.progress_text = None

        elif current.id == 'tlp_rules':
            # TLP housing - success!
            if self.narrative_active:
                current.dynamic_description = "Welcome to your new home..."
            else:
                bed_done = 'your_bed' in self.completed_interactions
                packet_done = 'welcome_packet' in self.completed_interactions

                if bed_done and packet_done:
                    current.dynamic_description = "You made it! Stability at last."
                    current.progress_text = None
                else:
                    tasks_done = sum([bed_done, packet_done])
                    current.dynamic_description = f"Settle into your new home ({tasks_done}/2)"
                    remaining = []
                    if not bed_done:
                        remaining.append("sit on your bed")
                    if not packet_done:
                        remaining.append("read welcome packet")
                    current.progress_text = "Need: " + ", ".join(remaining)

    def interact_with_object(self, name):
        """Handle special interactions for different objectives"""
        print(f"[TLP_UNIFIED] Interacting with {name}")

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # Get interactions for current objective
        interactions = self.narrative_content[current.id]['interactions']

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified (housing_intro only)
            trigger = interaction.get('trigger_activity')

            if current.id == 'housing_intro':
                # Check if this item has already been packed
                item_map = {
                    'closet': 'clothes',
                    'desk': 'documents',
                    'nightstand': 'photo'
                }

                # If already packed, show message
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

        # Only call parent interaction for non-activity objects
        if name not in ['closet', 'desk', 'nightstand']:
            super().interact_with_object(name)

        # Update objective display after interaction
        self.update_objective_display()

        # Special handling for door interaction (housing_intro)
        if current.id == 'housing_intro' and name == 'door' and 'door' in self.completed_interactions:
            # Mark interaction as completed, let handle_auto_progression handle the rest
            self.completed_interactions.add('door')

        # Check if all required items are packed (housing_intro)
        if current.id == 'housing_intro' and self.items_packed == self.required_items:
            if 'door' not in self.completed_interactions:
                self.add_door_interaction()

    def launch_clothes_packing(self):
        """Launch the clothes packing mini-game"""
        from part_1_housing_stability.activities import ClothesPacking

        if hasattr(self.game, 'objective_manager'):
            activity = ClothesPacking(self.game.objective_manager)
            activity.foster_home_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_document_search(self):
        """Launch the document search mini-game"""
        from part_1_housing_stability.activities import DocumentSearch

        if hasattr(self.game, 'objective_manager'):
            activity = DocumentSearch(self.game.objective_manager)
            activity.foster_home_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_photo_selection(self):
        """Launch the photo selection mini-game"""
        from part_1_housing_stability.activities import PhotoSelection

        if hasattr(self.game, 'objective_manager'):
            activity = PhotoSelection(self.game.objective_manager)
            activity.foster_home_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def add_door_interaction(self):
        """Add the final door interaction after packing"""
        print(f"[TLP_UNIFIED] add_door_interaction() called")
        door_data = self.narrative_content['housing_intro']['interactions']['door']
        print(f"[TLP_UNIFIED] Door data: {door_data}")
        self.add_interactive_object('door', door_data)
        print(f"[TLP_UNIFIED] Door added to interactive_objects: {'door' in self.interactive_objects}")
        self.dialogue_box.show(None, "You've packed everything. Walk down toward the bottom of the room and press E near the door to leave.")

    def check_objective_complete(self):
        """Check if current objective is complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return False

        if current.id == 'housing_intro':
            # Don't allow completion until all items packed and door used
            if len(self.items_packed) < len(self.required_items):
                return False
            return 'door' in self.completed_interactions

        elif current.id == 'tlp_rules':
            # Complete when both bed and welcome packet interactions are done and narrative finished
            bed_done = 'your_bed' in self.completed_interactions
            packet_done = 'welcome_packet' in self.completed_interactions
            return bed_done and packet_done and not self.narrative_active

        return super().check_objective_complete()

    def handle_event(self, event):
        """Override to handle activity events and prevent early exit"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
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
                    self.active = False
                    return
                if event.key < 32 or event.key > 126:
                    self.current_activity.handle_key(event.key)
                else:
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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current = self.game.objective_manager.get_current_objective()

                if current and current.id == 'housing_intro':
                    if 'door' not in self.completed_interactions:
                        if self.items_packed != self.required_items:
                            self.dialogue_box.show(None, "You need to pack your belongings before leaving!")
                        else:
                            self.dialogue_box.show(None, "Use the door to leave the foster home.")
                        return
                    else:
                        self.active = False
                        return

                # For other objectives, allow normal ESC handling
                if current and current.id == 'tlp_rules':
                    if not self.check_objective_complete():
                        self.dialogue_box.show(None, "Complete the required interactions before leaving.")
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
                print(f"[TLP_UNIFIED] Activity completed! items_packed={self.items_packed}, required={self.required_items}")
                self.update_objective_display()
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Check if all required items are now packed
                if self.items_packed == self.required_items:
                    print("[TLP_UNIFIED] All items packed! Adding door interaction.")
                    self.add_door_interaction()

        # Exit timer is handled by parent class's handle_exit_timer() which is called in super().update(dt)

    def draw(self, screen):
        """Draw the TLP housing interior with visual indicators"""
        super().draw(screen)

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # For housing_intro, draw packing objects even if completed
        if current.id == 'housing_intro':
            packing_objects = ['closet', 'desk', 'nightstand']
            for name in packing_objects:
                if name in self.interactive_objects and name in self.completed_interactions:
                    obj = self.interactive_objects[name]
                    obj_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + obj['x'] * self.TILE_SIZE
                    obj_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + obj['y'] * self.TILE_SIZE

                    # Draw with different color if already packed
                    item_map = {'closet': 'clothes', 'desk': 'documents', 'nightstand': 'photo'}
                    if item_map.get(name) in self.items_packed:
                        pygame.draw.rect(screen, (100, 200, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)
                    else:
                        pygame.draw.rect(screen, (255, 220, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return

        # Draw stage indicators
        if not self.narrative_active:
            font = pygame.font.Font(None, 24)

            if current.id == 'tlp_rules':
                success_text = font.render("SUCCESS: You made it to TLP!", True, (100, 255, 100))
                screen.blit(success_text, (50, 100))
                stability_text = font.render("Safe housing for 24 months", True, (100, 200, 255))
                screen.blit(stability_text, (50, 130))
                hope_text = font.render("Time to rebuild your life", True, (255, 255, 100))
                screen.blit(hope_text, (50, 160))

"""
Narrative Interior Base Class - Connects interiors to story objectives
"""
import pygame
import os
from src.interiors.generic_interior import GenericInterior
from src.ui.dialogue_box import DialogueBox
from src.core.debug_logger import debug_logger
from src.effects.completion_effects import ActivityCompletionFeedback

class NarrativeInterior(GenericInterior):
    """Base class for interiors with narrative content"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Narrative components
        self.dialogue_box = DialogueBox()
        self.narrative_active = False
        self.current_sequence = []
        self.sequence_index = 0

        # Interactive objects
        self.interactive_objects = {}
        self.completed_interactions = set()

        # NPC management
        self.npcs = {}

        # Track objective when sequence starts (for auto-reload detection)
        self.sequence_start_objective_id = None

        # Load NPC sprite (same as player character)
        self.npc_sprite = self.load_npc_sprite()

        # Load narrative content for this room
        self.narrative_content = self.load_narrative_content()

        # Auto-progression system
        self.completion_triggered = False
        self.exit_timer = 0
        self.should_exit = False
        self.completion_dialogue_shown = False

        # Activity completion system
        self.activity_completion_delay = 3.0  # Wait for activity completion feedback
        self.activity_completion_timer = 0.0
        self.waiting_for_activity = False
        self.objective_completion_feedback = ActivityCompletionFeedback()

    def load_narrative_content(self):
        """Override in subclasses to provide narrative content"""
        return {}

    def load_npc_sprite(self):
        """Load the same sprite used for the player character"""
        sprite_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
            '0_Premade_Characters', '16x16', 'Premade_Character_01.png'
        )

        try:
            # Load the spritesheet
            spritesheet = pygame.image.load(sprite_path)

            # Extract the idle down sprite (column 2, row 0)
            sprite_width = 16
            sprite_height = 32  # Characters are 2 tiles tall

            rect = pygame.Rect(2 * sprite_width, 0, sprite_width, sprite_height)
            sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
            sprite.blit(spritesheet, (0, 0), rect)

            # Scale to proper display size
            sprite = pygame.transform.scale(sprite, (self.TILE_SIZE, self.TILE_SIZE * 2))
            sprite = sprite.convert_alpha()

            return sprite
        except Exception as e:
            print(f"Could not load NPC sprite: {e}")
            return None

    def enter(self):
        """Enter the interior with safe error handling"""
        try:
            self.safe_enter()
        except Exception as e:
            debug_logger.error('ROOM_ENTRY', f"Failed to enter {self.__class__.__name__}",
                              error=str(e), building_pos=self.building_pos)
            # Try to maintain game state
            self.active = False

    def safe_enter(self):
        """Safe enter implementation with error recovery"""
        debug_logger.debug('ROOM_ENTRY', f"Entering {self.__class__.__name__}",
                          building_pos=self.building_pos)

        # Call parent enter
        super().enter()

        # Validate room state before proceeding
        if not self.validate_room_state():
            debug_logger.warning('ROOM_ENTRY', "Room state validation failed",
                                room_name=self.__class__.__name__)
            return

        # Check if current objective triggers narrative
        self.check_for_objective_narrative()

        debug_logger.info('ROOM_ENTRY', f"Successfully entered {self.__class__.__name__}")

    def check_for_objective_narrative(self):
        """Check if current objective has narrative in this room"""
        if not hasattr(self.game, 'objective_manager'):
            print("No objective manager found")
            return

        current = self.game.objective_manager.get_current_objective()
        if not current:
            print("No current objective found")
            return

        print(f"[NARRATIVE] Checking objective '{current.id}' at target_position: {current.target_position}")
        print(f"[NARRATIVE] Current building_pos: {self.building_pos}")
        print(f"[NARRATIVE] Position match: {current.target_position == self.building_pos}")
        print(f"[NARRATIVE] Available narrative content: {list(self.narrative_content.keys())}")

        # Check if this room is the objective location
        if current.target_position == self.building_pos:
            print(f"✅ This room is the objective location for: {current.id}")

            # Check if we have narrative content for this objective
            if current.id in self.narrative_content:
                print(f"✅ Starting narrative sequence for: {current.id}")
                self.start_narrative_sequence(current.id)
            else:
                print(f"❌ No narrative content found for objective: {current.id}")
        else:
            print(f"❌ Position mismatch - objective target: {current.target_position}, building pos: {self.building_pos}")

    def start_narrative_sequence(self, objective_id):
        """Start a narrative sequence for an objective"""
        if objective_id not in self.narrative_content:
            return

        content = self.narrative_content[objective_id]
        self.narrative_active = True
        self.current_sequence = content.get('dialogue_sequence', [])
        self.sequence_index = 0

        # Track which objective started this sequence
        self.sequence_start_objective_id = objective_id

        # Add NPCs for this sequence
        for npc in content.get('npcs', []):
            self.add_npc(npc['name'], npc['x'], npc['y'])

        # Add interactive objects (skip if already added)
        for obj_name, obj_data in content.get('interactions', {}).items():
            if obj_name not in self.interactive_objects:
                self.add_interactive_object(obj_name, obj_data)

        # Show first dialogue
        if self.current_sequence:
            self.show_next_dialogue()

    def show_next_dialogue(self):
        """Show the next dialogue in sequence"""
        if self.sequence_index < len(self.current_sequence):
            speaker, text = self.current_sequence[self.sequence_index]
            self.dialogue_box.show(speaker, text)
            self.sequence_index += 1
        else:
            # Sequence complete
            self.end_narrative_sequence()

    def end_narrative_sequence(self):
        """End the current narrative sequence"""
        self.narrative_active = False
        self.dialogue_box.hide()

        # Check if all required interactions are complete
        if self.check_objective_complete():
            # Complete the objective
            if hasattr(self.game, 'objective_manager'):
                self.game.objective_manager.complete_current_objective()

    def check_objective_complete(self):
        """Check if objective requirements are met"""
        # Override in subclasses for specific completion conditions
        return True

    def add_npc(self, name, tile_x, tile_y):
        """Add an NPC to the room"""
        self.npcs[name] = {
            'x': tile_x,
            'y': tile_y,
            'name': name
        }

    def add_interactive_object(self, name, data):
        """Add an interactive object to the room"""
        self.interactive_objects[name] = {
            'x': data['position'][0],
            'y': data['position'][1],
            'prompt': data['prompt'],
            'dialogue': data.get('dialogue', []),
            'required': data.get('required', False),
            'trigger_activity': data.get('trigger_activity', None)
        }

    def check_interactions(self):
        """Check if player is near interactive objects"""
        player_tile_x = int(self.player_pixel_x // self.TILE_SIZE)
        player_tile_y = int(self.player_pixel_y // self.TILE_SIZE)

        for name, obj in self.interactive_objects.items():
            if name not in self.completed_interactions:
                # Check if player is adjacent to object
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj
        return None, None

    def interact_with_object(self, name):
        """Interact with an object"""
        if name in self.interactive_objects:
            obj = self.interactive_objects[name]

            # Check if this object triggers an activity
            if obj.get('trigger_activity'):
                self.launch_activity(obj['trigger_activity'])
                # Don't mark as completed if it triggers an activity - let the activity handle completion
                print(f"[NARRATIVE] Triggered activity '{obj['trigger_activity']}' - not marking interaction as completed")
            # Show interaction dialogue
            elif obj['dialogue']:
                self.current_sequence = [(None, text) for text in obj['dialogue']]
                self.sequence_index = 0
                self.show_next_dialogue()
                # Mark as completed for dialogue interactions
                self.completed_interactions.add(name)
            else:
                # Mark as completed for other interactions
                self.completed_interactions.add(name)

    def launch_activity(self, activity_name):
        """Launch an activity based on its name - override in subclasses"""
        print(f"Activity trigger: {activity_name} (override launch_activity in subclass)")

    def get_required_interactions(self):
        """Get list of required interactions for current objective"""
        current = self.game.objective_manager.get_current_objective()
        if not current or current.id not in self.narrative_content:
            return []

        objective_data = self.narrative_content[current.id]
        interactions = objective_data.get('interactions', {})

        required = []
        for name, data in interactions.items():
            if data.get('required', False):
                required.append(name)

        return required

    def check_completion_status(self):
        """Check if all required interactions are complete"""
        required = self.get_required_interactions()
        if not required:
            return False

        completed_required = [name for name in required if name in self.completed_interactions]
        return len(completed_required) == len(required)

    def handle_auto_progression(self):
        """Handle automatic progression when all tasks complete"""
        if self.completion_triggered:
            return

        # Check if we have an active activity that needs to complete first
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            # Wait for activity to complete before checking objective completion
            if self.current_activity.completed and not self.waiting_for_activity:
                self.waiting_for_activity = True
                self.activity_completion_timer = 0.0
            return

        # If we were waiting for activity completion, handle the delay
        if self.waiting_for_activity:
            return  # Timer is handled in update method

        if self.check_completion_status():
            self.completion_triggered = True
            self.show_objective_completion()
            self.start_exit_timer(2.5)  # 2.5 second delay

    def show_objective_completion(self):
        """Show visual objective completion feedback"""
        if self.completion_dialogue_shown:
            return

        self.completion_dialogue_shown = True
        current = self.game.objective_manager.get_current_objective()

        if current:
            # Get next objective for better messaging
            next_objective = self.game.objective_manager.get_next_objective()
            next_title = next_objective.title if next_objective else "Continue Story"

            # Show visual completion feedback
            self.objective_completion_feedback.show_completion(
                completion_type="success",
                message="Objective Complete!",
                submessage=f"Next: {next_title}"
            )

            # Also show dialogue for context
            completion_messages = {
                'job_search_reality': "✅ Application submitted. You've started working!",
                'got_job': "✅ You're now employed. Time to learn about income.",
                'income_math': "✅ Math calculated. Reality is setting in.",
                'housing_intro': "✅ You've packed everything. Time to start your journey.",
                'housing_menu': "✅ You've learned about housing options. Choose your path.",
                'sarah_responds': "✅ Sarah has offered her couch. Rest for tonight.",
                'reality_check': "✅ Shelter intake complete. You have a bed for tonight.",
                'apartment_search': "✅ You've found listings. Time to apply.",
                'default': "✅ Task complete. Moving to next objective..."
            }

            message = completion_messages.get(current.id, completion_messages['default'])
            self.dialogue_box.show(None, message)

    def show_completion_dialogue(self):
        """Legacy method - redirects to new system"""
        self.show_objective_completion()

    def start_exit_timer(self, duration):
        """Start timer for automatic exit"""
        self.should_exit = True
        self.exit_timer = duration

    def handle_exit_timer(self, dt):
        """Handle automatic exit after completion"""
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Advance to next objective and exit
                self.game.objective_manager.advance_to_next_objective()
                self.active = False

    def get_progress_info(self):
        """Get current progress information"""
        required = self.get_required_interactions()
        if not required:
            return None

        completed_required = [name for name in required if name in self.completed_interactions]
        return len(completed_required), len(required)

    def handle_input(self, keys):
        """Handle input with narrative awareness"""
        # If dialogue is active, handle dialogue input
        if self.dialogue_box.active:
            # Don't allow movement during dialogue
            return

        # Otherwise use normal movement
        super().handle_input(keys)

    def handle_event(self, event):
        """Handle events including narrative interactions"""
        # CRITICAL: If an activity is active, don't intercept any keys - let the activity handle them
        if hasattr(self, 'current_activity') and self.current_activity is not None and hasattr(self.current_activity, 'active') and self.current_activity.active:
            # Activity is handling events, don't process them here
            return

        if event.type == pygame.KEYDOWN:
            # Handle dialogue progression with both SPACE and E
            if (event.key == pygame.K_SPACE or event.key == pygame.K_e) and self.dialogue_box.active:
                if self.dialogue_box.text_progress < len(self.dialogue_box.current_text):
                    # Skip typewriter effect
                    self.dialogue_box.skip_typewriter()
                else:
                    # Show next dialogue
                    self.show_next_dialogue()
                return

            # Handle interactions (only when dialogue is not active)
            if event.key == pygame.K_e and not self.narrative_active and not self.dialogue_box.active:
                # Check for nearby interactive objects
                obj_name, obj = self.check_interactions()
                if obj:
                    self.interact_with_object(obj_name)
                    return

            # Handle exit
            if event.key == pygame.K_ESCAPE:
                self.active = False

    def update(self, dt):
        """Update the interior including narrative elements"""
        super().update(dt)

        # Update dialogue box
        self.dialogue_box.update(dt)

        # Update objective completion feedback
        self.objective_completion_feedback.update(dt)

        # Handle activity completion delay
        if self.waiting_for_activity:
            self.activity_completion_timer += dt
            if self.activity_completion_timer >= self.activity_completion_delay:
                self.waiting_for_activity = False
                # Now check for objective completion
                if self.check_completion_status():
                    self.completion_triggered = True
                    self.show_objective_completion()
                    self.start_exit_timer(2.5)

        # Check for auto-progression after each interaction
        self.handle_auto_progression()

        # Handle exit timer
        self.handle_exit_timer(dt)

    def draw(self, screen):
        """Draw the interior and narrative elements"""
        # Draw base interior
        super().draw(screen)

        # Draw interactive objects with visual indicators
        for name, obj in self.interactive_objects.items():
            if name not in self.completed_interactions:
                obj_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + obj['x'] * self.TILE_SIZE
                obj_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + obj['y'] * self.TILE_SIZE

                # Draw glowing effect around interactive objects
                glow_radius = 25 + abs(pygame.time.get_ticks() % 1000 - 500) / 50  # Pulsing effect
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 220, 100, 30), (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (obj_x + 16 - glow_radius, obj_y + 16 - glow_radius))

                # Draw object highlight
                pygame.draw.rect(screen, (255, 220, 100), (obj_x, obj_y, self.TILE_SIZE, self.TILE_SIZE), 2)

                # Draw small icon or indicator
                font = pygame.font.Font(None, 24)
                icon = "!" if obj.get('required') else "?"
                icon_surf = font.render(icon, True, (255, 220, 100))
                icon_rect = icon_surf.get_rect(center=(obj_x + 16, obj_y + 16))
                screen.blit(icon_surf, icon_rect)

        # Draw NPCs
        for npc in self.npcs.values():
            npc_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + npc['x'] * self.TILE_SIZE
            npc_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + npc['y'] * self.TILE_SIZE

            # Draw the NPC sprite if available, otherwise fallback to circle
            if self.npc_sprite:
                # Draw sprite (offset Y by -TILE_SIZE since character is 2 tiles tall)
                screen.blit(self.npc_sprite, (npc_x, npc_y - self.TILE_SIZE))
            else:
                # Fallback to circle if sprite loading failed
                pygame.draw.circle(screen, (100, 150, 200), (npc_x + 16, npc_y + 16), 12)

            # Draw name label above the character
            font = pygame.font.Font(None, 20)
            name_surf = font.render(npc['name'], True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(npc_x + 16, npc_y - self.TILE_SIZE - 10))
            screen.blit(name_surf, name_rect)

        # Draw interaction prompts
        if not self.narrative_active:
            obj_name, obj = self.check_interactions()
            if obj:
                # Draw prompt above player
                font = pygame.font.Font(None, 22)
                prompt_text = f"[E] {obj['prompt']}"
                prompt_surf = font.render(prompt_text, True, (255, 255, 200))

                player_screen_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + self.player_pixel_x
                player_screen_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + self.player_pixel_y

                prompt_rect = prompt_surf.get_rect(center=(player_screen_x + 16, player_screen_y - 20))

                # Draw background for prompt
                bg_rect = prompt_rect.inflate(10, 5)
                pygame.draw.rect(screen, (40, 40, 50), bg_rect, 0, 3)
                screen.blit(prompt_surf, prompt_rect)

        # Draw progress indicator
        progress_info = self.get_progress_info()
        if progress_info:
            completed, total = progress_info

            # Draw progress bar in top-right corner
            bar_width = 200
            bar_height = 20
            bar_x = self.SCREEN_WIDTH - bar_width - 20
            bar_y = 20

            # Background
            pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_width, bar_height))

            # Progress fill
            progress_width = int((completed / total) * bar_width)
            if progress_width > 0:
                pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, progress_width, bar_height))

            # Border
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

            # Progress text
            font = pygame.font.Font(None, 20)
            progress_text = f"Tasks: {completed}/{total}"
            text_surf = font.render(progress_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
            screen.blit(text_surf, text_rect)

        # Draw dialogue box
        self.dialogue_box.draw(screen)

        # Draw objective completion feedback
        self.objective_completion_feedback.draw(screen)

    def validate_room_state(self):
        """Validate room state to prevent freezes"""
        try:
            # Check required attributes exist
            required_attrs = ['game', 'room_data', 'building_pos', 'TILE_SIZE', 'dialogue_box']
            for attr in required_attrs:
                if not hasattr(self, attr):
                    debug_logger.error('VALIDATION', f"Missing required attribute: {attr}")
                    return False

            # Check room dimensions are reasonable
            if hasattr(self, 'room_width') and hasattr(self, 'room_height'):
                if self.room_width <= 0 or self.room_height <= 0:
                    debug_logger.error('VALIDATION', "Invalid room dimensions",
                                      width=self.room_width, height=self.room_height)
                    return False

                if self.room_width > 100 or self.room_height > 100:
                    debug_logger.warning('VALIDATION', "Unusually large room dimensions",
                                        width=self.room_width, height=self.room_height)

            # Check player position is valid
            if hasattr(self, 'player_pixel_x') and hasattr(self, 'player_pixel_y'):
                max_x = self.room_width * self.TILE_SIZE if hasattr(self, 'room_width') else 1000
                max_y = self.room_height * self.TILE_SIZE if hasattr(self, 'room_height') else 1000

                if self.player_pixel_x < 0 or self.player_pixel_x > max_x:
                    debug_logger.warning('VALIDATION', "Player X position out of bounds",
                                       x=self.player_pixel_x, max_x=max_x)

                if self.player_pixel_y < 0 or self.player_pixel_y > max_y:
                    debug_logger.warning('VALIDATION', "Player Y position out of bounds",
                                       y=self.player_pixel_y, max_y=max_y)

            # Check narrative content is valid
            if hasattr(self, 'narrative_content') and self.narrative_content:
                if not isinstance(self.narrative_content, dict):
                    debug_logger.error('VALIDATION', "narrative_content is not a dictionary")
                    return False

            debug_logger.debug('VALIDATION', f"Room state validation passed for {self.__class__.__name__}")
            return True

        except Exception as e:
            debug_logger.error('VALIDATION', f"Validation error: {str(e)}")
            return False
"""
Narrative Interior Base Class - Connects interiors to story objectives
"""
import pygame
import os
from src.interiors.generic_interior import GenericInterior
from src.ui.dialogue_box import DialogueBox

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

        # Load NPC sprite (same as player character)
        self.npc_sprite = self.load_npc_sprite()

        # Load narrative content for this room
        self.narrative_content = self.load_narrative_content()

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
        """Enter the interior and check for narrative triggers"""
        super().enter()

        # Check if current objective triggers narrative
        self.check_for_objective_narrative()

    def check_for_objective_narrative(self):
        """Check if current objective has narrative in this room"""
        if not hasattr(self.game, 'objective_manager'):
            print("No objective manager found")
            return

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # Check if this room is the objective location
        if current.target_position == self.building_pos:
            print(f"This room is the objective location for: {current.id}")

            # Check if we have narrative content for this objective
            if current.id in self.narrative_content:
                self.start_narrative_sequence(current.id)

    def start_narrative_sequence(self, objective_id):
        """Start a narrative sequence for an objective"""
        if objective_id not in self.narrative_content:
            return

        content = self.narrative_content[objective_id]
        self.narrative_active = True
        self.current_sequence = content.get('dialogue_sequence', [])
        self.sequence_index = 0

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
            # Show interaction dialogue
            elif obj['dialogue']:
                self.current_sequence = [(None, text) for text in obj['dialogue']]
                self.sequence_index = 0
                self.show_next_dialogue()

            # Mark as completed
            self.completed_interactions.add(name)

    def launch_activity(self, activity_name):
        """Launch an activity based on its name - override in subclasses"""
        print(f"Activity trigger: {activity_name} (override launch_activity in subclass)")

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
        if event.type == pygame.KEYDOWN:
            # Handle dialogue progression
            if event.key == pygame.K_SPACE and self.dialogue_box.active:
                if self.dialogue_box.text_progress < len(self.dialogue_box.current_text):
                    # Skip typewriter effect
                    self.dialogue_box.skip_typewriter()
                else:
                    # Show next dialogue
                    self.show_next_dialogue()
                return

            # Handle interactions
            if event.key == pygame.K_e and not self.narrative_active:
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

        # Draw dialogue box
        self.dialogue_box.draw(screen)
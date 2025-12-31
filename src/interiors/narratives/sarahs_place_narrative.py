"""
Sarah's Place Interior - Couch Surfing Chapter 3
Handles objectives: sarah_responds, sneaking_around
"""
import pygame
import random
from src.interiors.narrative_interior import NarrativeInterior

class SarahsPlaceNarrative(NarrativeInterior):
    """Sarah's house with stealth mechanics for couch surfing"""

    def __init__(self, game, room_data, building_pos):
        # Initialize all attributes BEFORE calling super().__init__()
        # This ensures they exist when load_narrative_content() is called

        # Stealth mechanics
        self.noise_level = 0
        self.max_noise = 100
        self.parents_awareness = 0
        self.is_sneaking = False

        # Time tracking
        self.current_time = "11:00 PM"
        self.day_count = 1
        self.max_days = 3

        # Room states
        self.in_sarahs_room = False
        self.caught_by_parents = False

        # Stress tracking
        self.sarah_stress = 0
        self.player_exhaustion = 50

        # Floor tiles that make noise
        self.creaky_tiles = [
            (5, 4), (6, 4), (7, 4),  # Hallway boards
            (8, 7), (9, 7),  # Near stairs
            (4, 8), (5, 8),  # Living room entrance
        ]

        # Parent positions (they move around)
        self.dad_position = (10, 3)  # Master bedroom
        self.mom_position = (10, 3)  # Master bedroom
        self.parents_awake = False

        # Player animation state
        self.player_pixel_x = 0
        self.player_pixel_y = 0
        self.player_moving = False
        self.player_direction = 'down'  # down, up, left, right
        self.animation_timer = 0
        self.animation_frame = 0

        # Animated NPCs with walking animations (separate from narrative NPCs)
        self.animated_npcs = {
            'Sarah': {
                'position': (7, 10),
                'sprite_num': 12,  # Female character
                'sprite_col': 0,
                'sprite_row': 0,
                'direction': 'down',
                'animation_frame': 0,
                'animation_timer': 0
            }
        }

        # Now call super().__init__() first to initialize TILE_SIZE and other base attributes
        super().__init__(game, room_data, building_pos)

        # Load character sprites after TILE_SIZE is available
        self.load_character_sprites()

    def load_character_sprites(self):
        """Load character sprites for NPCs and player - using 16x16 sheets like Mike's place"""
        import os
        self.character_sprites = {}
        sprite_width = 16
        sprite_height = 32  # Characters are 2 tiles tall

        for name, data in self.animated_npcs.items():
            sprite_num = data['sprite_num']
            sprite_col = data.get('sprite_col', 0)
            sprite_row = data.get('sprite_row', 0)

            # Use 16x16 character sheets
            sprite_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
                '0_Premade_Characters', '16x16', f'Premade_Character_{sprite_num:02d}.png'
            )

            try:
                spritesheet = pygame.image.load(sprite_path)
                # Load all 4 directions (down, left, right, up) with 4 animation frames each
                self.character_sprites[name] = {}

                directions = ['down', 'left', 'right', 'up']
                for dir_idx, direction in enumerate(directions):
                    self.character_sprites[name][direction] = []
                    for frame in range(4):  # 4 animation frames per direction
                        sprite_rect = pygame.Rect(
                            frame * sprite_width,
                            dir_idx * sprite_height,
                            sprite_width,
                            sprite_height
                        )
                        sprite_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                        sprite_surface.blit(spritesheet, (0, 0), sprite_rect)

                        # Scale to match tile size
                        scaled_sprite = pygame.transform.scale(
                            sprite_surface,
                            (self.TILE_SIZE, self.TILE_SIZE * 2)
                        )
                        scaled_sprite = scaled_sprite.convert_alpha()
                        self.character_sprites[name][direction].append(scaled_sprite)

                print(f"Loaded animated sprites for {name} from character {sprite_num:02d}")
            except Exception as e:
                print(f"Failed to load sprites for {name}: {e}")
                self.character_sprites[name] = None

    def load_narrative_content(self):
        """Load Sarah's place narrative content"""
        return {
            'sarah_responds': {
                'npcs': [
                    {'name': 'Sarah', 'x': 7, 'y': 10}
                ],
                'dialogue_sequence': [
                    ("Sarah", "*whispering* Thank god you're here. My parents are asleep."),
                    ("Sarah", "You can crash on my couch for a few nights, but we have to be SUPER quiet."),
                    ("You", "Thank you so much Sarah. I promise I'll be invisible."),
                    ("Sarah", "My parents wake up at 6:30 AM sharp. You HAVE to be gone by then."),
                    ("Sarah", "The third and fifth floorboards in the hallway creak. Avoid them."),
                    ("Sarah", "If they catch you here... we're both in huge trouble."),
                    (None, "Your stomach churns with anxiety. This is going to be stressful.")
                ],
                'interactions': {
                    'front_door': {
                        'position': (7, 11),
                        'prompt': 'Enter quietly',
                        'dialogue': [
                            "Sarah opens the door just wide enough for you to slip inside.",
                            "The house is dark. You can hear a TV upstairs.",
                            "Every footstep feels like thunder."
                        ],
                        'required': True
                    },
                    'living_room': {
                        'position': (5, 6),
                        'prompt': 'Sneak past',
                        'trigger_stealth': True,
                        'dialogue': None,
                        'required': True
                    },
                    'sarahs_couch': {
                        'position': (3, 3),
                        'prompt': 'Rest on couch',
                        'dialogue': [
                            "The couch is small but it's better than the shelter.",
                            "You lie down fully clothed, ready to run if needed.",
                            "You barely sleep, jumping at every noise."
                        ],
                        'required': True
                    }
                }
            },

            'sneaking_around': {
                'dialogue_sequence': [
                    (None, f"Day {self.day_count} at Sarah's place..."),
                    ("Sarah", "My mom almost saw your backpack this morning!"),
                    ("Sarah", "I told her it was for a school project but she looked suspicious."),
                    ("You", "I'm so sorry. Maybe I should find somewhere else..."),
                    ("Sarah", "No, no, it's okay. Just... we need to be more careful."),
                    ("Sarah", "Hide everything in my closet during the day."),
                    (None, "Each day here gets more stressful for both of you.")
                ],
                'interactions': {
                    'morning_alarm': {
                        'position': (3, 3),
                        'prompt': 'Wake up (5:30 AM)',
                        'dialogue': [
                            "Your phone vibrates. 5:30 AM.",
                            "Time to pack everything and sneak out.",
                            "Sarah is already up, looking stressed.",
                            "One hour until her parents wake up."
                        ],
                        'required': True
                    },
                    'pack_belongings': {
                        'position': (4, 3),
                        'prompt': 'Pack quickly',
                        'dialogue': [
                            "You stuff everything into your backpack.",
                            "Can't leave any trace you were here.",
                            "Check under the couch... behind cushions...",
                            "Everything accounted for. Time to go."
                        ],
                        'required': True
                    },
                    'sneak_out': {
                        'position': (7, 11),
                        'prompt': 'Exit before 6:30',
                        'trigger_stealth': True,
                        'dialogue': None,
                        'required': True
                    }
                }
            }
        }

    def enter(self):
        """Enter Sarah's place with time check"""
        super().enter()

        # Initialize player position (convert from game world coordinates)
        # Start player near the entrance
        entrance_tile_x = 7  # Near front door
        entrance_tile_y = 11
        self.player_pixel_x = entrance_tile_x * self.TILE_SIZE
        self.player_pixel_y = entrance_tile_y * self.TILE_SIZE

        # Set initial state based on objective
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'sarah_responds':
                self.current_time = "11:00 PM"
                self.parents_awake = False
                # Auto-complete front_door since entering the building means you went through it
                self.completed_interactions.add('front_door')
            elif current.id == 'sneaking_around':
                self.current_time = "5:30 AM"
                self.day_count = 2

    def handle_stealth_movement(self, new_x, new_y):
        """Handle movement with forgiving stealth mechanics"""
        # Check if stepping on creaky tile
        if (new_x, new_y) in self.creaky_tiles and not self.is_sneaking:
            self.noise_level += 20  # Less harsh penalty
            self.parents_awareness += 10  # Less harsh penalty

            # Show helpful warning instead of punishing
            self.dialogue_box.show(None, "*CREAK* Careful! Hold SHIFT to sneak quietly!")

            # Much more forgiving threshold - give players more chances
            if self.parents_awareness > 90:  # Was 70, now 90
                self.trigger_caught_sequence()
                return False

        # Normal tile movement
        elif not self.is_sneaking:
            self.noise_level += 3  # Less noise
        else:
            self.noise_level += 1  # Even quieter when sneaking

        # Faster noise decay - more forgiving
        self.noise_level = max(0, self.noise_level - 3)

        return True

    def trigger_caught_sequence(self):
        """Handle being caught by parents"""
        self.caught_by_parents = True
        self.dialogue_box.show("Sarah's Dad", "What the HELL is going on here?!")

        # Force objective failure
        current = self.game.objective_manager.get_current_objective()
        if current and current.id in ['sarah_responds', 'sneaking_around']:
            # Jump to next objective or retry
            self.dialogue_box.show(None, "You grab your things and run. Sarah is grounded. You lost this safe space.")
            self.should_exit = True

    def handle_input(self, keys):
        """Handle input with stealth mode and animations"""
        # Check for sneak mode (holding shift)
        self.is_sneaking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Slower movement when sneaking
        if not self.dialogue_box.active:
            old_x, old_y = self.player_pixel_x, self.player_pixel_y
            new_x, new_y = self.player_pixel_x, self.player_pixel_y
            move_speed = self.TILE_SIZE // 8 if self.is_sneaking else self.TILE_SIZE // 4

            moving = False
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x -= move_speed
                self.player_direction = 'left'
                moving = True
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x += move_speed
                self.player_direction = 'right'
                moving = True
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                new_y -= move_speed
                self.player_direction = 'up'
                moving = True
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                new_y += move_speed
                self.player_direction = 'down'
                moving = True

            # Update movement state
            self.player_moving = moving

            if moving:
                # Check tile boundaries and stealth
                new_tile_x = int(new_x // self.TILE_SIZE)
                new_tile_y = int(new_y // self.TILE_SIZE)

                if (0 <= new_tile_x < self.room_width and
                    0 <= new_tile_y < self.room_height):

                    if self.handle_stealth_movement(new_tile_x, new_tile_y):
                        self.player_pixel_x = new_x
                        self.player_pixel_y = new_y

    def update(self, dt):
        """Update stealth mechanics, animations, and time"""
        super().update(dt)

        # Check if objective should complete (for cases where dialogue already ended)
        current = self.game.objective_manager.get_current_objective()
        if current and not self.should_exit:
            if self.check_objective_complete():
                # Trigger objective completion
                if hasattr(self.game, 'objective_manager'):
                    self.game.objective_manager.complete_current_objective()

        # Update player animation
        if self.player_moving:
            self.animation_timer += dt * 8  # Animation speed
            if self.animation_timer >= 1.0:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0  # Idle frame

        # Update NPC animations
        for name, npc in self.animated_npcs.items():
            # Initialize animation fields if they don't exist
            if 'animation_timer' not in npc:
                npc['animation_timer'] = 0
            if 'animation_frame' not in npc:
                npc['animation_frame'] = 0

            npc['animation_timer'] += dt * 6
            if npc['animation_timer'] >= 1.0:
                npc['animation_timer'] = 0
                npc['animation_frame'] = (npc['animation_frame'] + 1) % 4

        # Update noise level decay
        if self.noise_level > 0:
            self.noise_level = max(0, self.noise_level - dt * 10)

        # Update parent awareness decay (slowly)
        if self.parents_awareness > 0:
            self.parents_awareness = max(0, self.parents_awareness - dt * 2)

        # Check day progression
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'sneaking_around':
            # Increase stress over time
            self.sarah_stress += dt * 5
            self.player_exhaustion += dt * 3

            # Check if time to leave
            if self.day_count >= self.max_days and not self.dialogue_box.active:
                self.trigger_time_to_leave()

    def trigger_time_to_leave(self):
        """Sarah asks player to leave after 3 days"""
        self.dialogue_box.show("Sarah", "I'm sorry... my parents are getting suspicious. You need to find somewhere else.")
        self.dialogue_box.show("You", "I understand. Thank you for everything, Sarah.")
        self.dialogue_box.show(None, "You pack your things one last time. Sarah's couch is no longer an option.")

        # Mark the final interaction as completed to trigger auto-progression
        if 'time_to_leave' not in self.interactive_objects:
            self.add_interactive_object('time_to_leave', {
                'position': (7, 10),  # Near Sarah
                'prompt': 'Say goodbye',
                'dialogue': ["Time to leave..."],
                'required': True
            })
        self.completed_interactions.add('time_to_leave')

    def draw(self, screen):
        """Draw Sarah's house with helpful UI"""
        super().draw(screen)

        if self.active and not self.dialogue_box.active:
            # Draw clear instructions
            self.draw_instructions(screen)

            # Draw time display
            self.draw_time_display(screen)

            # Draw creaky floorboards with clear warnings
            self.draw_creaky_tiles(screen)

            # Sneak mode visual feedback is shown through player movement

            # Draw interaction point highlights
            self.draw_interaction_highlights(screen)

            # Draw animated characters
            self.draw_animated_characters(screen)

    def draw_instructions(self, screen):
        """Draw clear, helpful instructions"""
        font = pygame.font.Font(None, 20)
        instructions = [
            "🤫 Hold SHIFT to sneak quietly",
            "❌ Avoid the RED tiles (they creak!)",
            "🎯 Walk to the interaction points",
            "⏰ Don't wake Sarah's parents!"
        ]

        # Draw instruction box
        box_height = len(instructions) * 25 + 20
        box_rect = pygame.Rect(10, 130, 280, box_height)
        pygame.draw.rect(screen, (0, 0, 0, 180), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)

        # Draw instructions
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (20, 140 + i * 25))

    def draw_noise_meter(self, screen):
        """Draw the noise level meter"""
        meter_width = 200
        meter_height = 20
        x = self.SCREEN_WIDTH - meter_width - 20
        y = 20

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (x, y, meter_width, meter_height))

        # Noise level bar
        noise_color = (255, 100, 100) if self.noise_level > 70 else (255, 200, 100) if self.noise_level > 40 else (100, 255, 100)
        bar_width = int((self.noise_level / self.max_noise) * meter_width)
        pygame.draw.rect(screen, noise_color, (x, y, bar_width, meter_height))

        # Border
        pygame.draw.rect(screen, (200, 200, 200), (x, y, meter_width, meter_height), 2)

        # Label
        font = pygame.font.Font(None, 18)
        label = font.render("NOISE", True, (200, 200, 200))
        screen.blit(label, (x - 50, y + 2))

    def draw_awareness_indicator(self, screen):
        """Draw parent awareness level"""
        if self.parents_awareness > 0:
            font = pygame.font.Font(None, 24)
            color = (255, 100, 100) if self.parents_awareness > 50 else (255, 200, 100)

            if self.parents_awareness > 70:
                text = "PARENTS WAKING UP!"
            elif self.parents_awareness > 50:
                text = "Parents stirring..."
            else:
                text = "You hear movement upstairs"

            warning = font.render(text, True, color)
            x = self.SCREEN_WIDTH // 2 - warning.get_width() // 2
            screen.blit(warning, (x, 60))

    def draw_time_display(self, screen):
        """Time is shown in top-center UI panel"""
        # Warning if close to wake time (centered, not top-left)
        if self.current_time == "6:15 AM":
            font = pygame.font.Font(None, 22)
            warning = font.render("15 MINUTES UNTIL PARENTS WAKE!", True, (255, 100, 100))
            x = self.SCREEN_WIDTH // 2 - warning.get_width() // 2
            screen.blit(warning, (x, 90))

    def draw_creaky_tiles(self, screen):
        """Draw obvious highlights on creaky floorboards"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        for tile_x, tile_y in self.creaky_tiles:
            x = offset_x + tile_x * self.TILE_SIZE
            y = offset_y + tile_y * self.TILE_SIZE

            # Bright red warning overlay
            s = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            s.set_alpha(120)
            s.fill((255, 50, 50))
            screen.blit(s, (x, y))

            # Add warning symbol
            font = pygame.font.Font(None, 16)
            warning_text = font.render("⚠", True, (255, 255, 255))
            text_x = x + self.TILE_SIZE // 2 - warning_text.get_width() // 2
            text_y = y + self.TILE_SIZE // 2 - warning_text.get_height() // 2
            screen.blit(warning_text, (text_x, text_y))

    def draw_interaction_highlights(self, screen):
        """Draw glowing highlights on interaction points"""
        import math

        current_obj = self.game.objective_manager.get_current_objective()
        if not current_obj:
            return

        # Get current objective interactions
        objective_data = self.load_narrative_content().get(current_obj.id, {})
        interactions = objective_data.get('interactions', {})

        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        for interaction_key, interaction in interactions.items():
            if interaction.get('required', False):
                pos = interaction.get('position')
                if pos:
                    tile_x, tile_y = pos
                    x = offset_x + tile_x * self.TILE_SIZE
                    y = offset_y + tile_y * self.TILE_SIZE

                    # Pulsing glow effect
                    pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.3 + 0.7
                    glow_alpha = int(100 * pulse)

                    # Draw glowing circle
                    glow_surf = pygame.Surface((self.TILE_SIZE + 20, self.TILE_SIZE + 20), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (100, 255, 100, glow_alpha),
                                     (self.TILE_SIZE // 2 + 10, self.TILE_SIZE // 2 + 10),
                                     self.TILE_SIZE // 2 + 10)
                    screen.blit(glow_surf, (x - 10, y - 10))

                    # Draw prompt text
                    prompt = interaction.get('prompt', 'Interact')
                    font = pygame.font.Font(None, 18)
                    text = font.render(f"💡 {prompt}", True, (255, 255, 255))
                    text_x = x + self.TILE_SIZE // 2 - text.get_width() // 2
                    text_y = y - 25

                    # Background for text
                    text_bg = pygame.Rect(text_x - 5, text_y - 2, text.get_width() + 10, text.get_height() + 4)
                    pygame.draw.rect(screen, (0, 0, 0, 180), text_bg)
                    screen.blit(text, (text_x, text_y))

    def draw_animated_characters(self, screen):
        """Draw animated player and NPCs with walking animations"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        # Draw the player with animations
        player_screen_x = offset_x + self.player_pixel_x
        player_screen_y = offset_y + self.player_pixel_y

        # For now, just draw a basic animated player circle with direction indicator
        # You could load player sprites the same way as NPCs if desired
        player_color = (100, 255, 100) if self.is_sneaking else (100, 150, 255)
        pygame.draw.circle(screen, player_color,
                         (int(player_screen_x + self.TILE_SIZE // 2),
                          int(player_screen_y + self.TILE_SIZE // 2)),
                         12)

        # Direction indicator for player
        direction_offsets = {
            'down': (0, 8),
            'up': (0, -8),
            'left': (-8, 0),
            'right': (8, 0)
        }
        if self.player_direction in direction_offsets:
            dx, dy = direction_offsets[self.player_direction]
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(player_screen_x + self.TILE_SIZE // 2 + dx),
                              int(player_screen_y + self.TILE_SIZE // 2 + dy)), 3)

        # Draw NPCs with animated sprites
        for name, npc in self.animated_npcs.items():
            if name in self.character_sprites and self.character_sprites[name]:
                npc_x = offset_x + npc['position'][0] * self.TILE_SIZE
                npc_y = offset_y + npc['position'][1] * self.TILE_SIZE

                # Get current sprite frame
                direction = npc['direction']
                frame = npc['animation_frame']

                if (direction in self.character_sprites[name] and
                    frame < len(self.character_sprites[name][direction])):
                    sprite = self.character_sprites[name][direction][frame]
                    # Characters are 2 tiles tall, so offset Y
                    screen.blit(sprite, (npc_x, npc_y - self.TILE_SIZE))

                    # Draw name label
                    font = pygame.font.Font(None, 16)
                    name_surf = font.render(name, True, (255, 255, 255))
                    name_rect = name_surf.get_rect(center=(npc_x + self.TILE_SIZE // 2,
                                                         npc_y - self.TILE_SIZE - 20))

                    # Background for name
                    bg_rect = name_rect.inflate(8, 4)
                    pygame.draw.rect(screen, (50, 100, 150, 200), bg_rect, 0, 3)
                    pygame.draw.rect(screen, (200, 200, 200), bg_rect, 1, 3)
                    screen.blit(name_surf, name_rect)
            else:
                # Fallback circle if sprite loading failed
                npc_x = offset_x + npc['position'][0] * self.TILE_SIZE + self.TILE_SIZE // 2
                npc_y = offset_y + npc['position'][1] * self.TILE_SIZE + self.TILE_SIZE // 2
                pygame.draw.circle(screen, (255, 150, 150), (npc_x, npc_y), 12)

    def check_objective_complete(self):
        """Override base class to provide Sarah's Place specific completion logic"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return False

        if current.id == 'sarah_responds':
            # Complete when player has entered, gone to couch, and rested
            required_interactions = ['front_door', 'living_room', 'sarahs_couch']
            if all(name in self.completed_interactions for name in required_interactions):
                # Add exit door if not already added
                if 'exit_door' not in self.interactive_objects:
                    self.add_interactive_object('exit_door', {
                        'position': (7, 11),
                        'prompt': 'Leave',
                        'dialogue': [
                            "You settle in on the couch.",
                            "It's temporary, but it's better than the shelter.",
                            "For now, you have a place to sleep."
                        ],
                        'required': False
                    })

                # Set should_exit to trigger automatic progression
                self.should_exit = True
                return True
            return False

        elif current.id == 'sneaking_around':
            # Complete when the daily routine is done or time to leave is triggered
            if 'time_to_leave' in self.completed_interactions:
                self.should_exit = True
                return True
            # Or when all morning routine interactions are done
            required_interactions = ['morning_alarm', 'pack_belongings', 'sneak_out']
            if all(name in self.completed_interactions for name in required_interactions):
                self.should_exit = True
                return True
            return False

        # Use base class logic for other objectives
        return super().check_objective_complete()
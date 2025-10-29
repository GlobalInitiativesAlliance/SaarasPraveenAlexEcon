"""
Mike's Place Interior - Couch Surfing Chapter 3
Handles objectives: mike_floor, losing_stuff, wearing_out_welcome
"""
import pygame
import random
import os
from src.interiors.narrative_interior import NarrativeInterior

class MikesPlaceNarrative(NarrativeInterior):
    """Mike's chaotic apartment with roommate dynamics"""

    def __init__(self, game, room_data, building_pos):
        # Initialize attributes needed by load_narrative_content first
        self.hours_no_sleep = 0
        self.narrative_stage = 'arrival'  # arrival -> chaos -> leaving
        self.chaos_events_seen = 0
        self.interactions_completed = set()

        # Now call parent init which will call load_narrative_content
        super().__init__(game, room_data, building_pos)

        # Chaos mechanics
        self.chaos_level = 75  # Starts high
        self.noise_level = 60
        self.cleanliness = 20  # Very messy

        # Roommate tracking with sprite info - better positioned around apartment
        self.roommates = {
            'Tyler': {'position': (13, 3), 'mood': 'loud', 'active': True, 'sprite_num': 3, 'sprite_col': 1, 'sprite_row': 0},  # Near TV/stereo
            'Kevin': {'position': (4, 8), 'mood': 'messy', 'active': True, 'sprite_num': 5, 'sprite_col': 2, 'sprite_row': 0},  # Kitchen area
            'Brian': {'position': (11, 9), 'mood': 'hostile', 'active': True, 'sprite_num': 8, 'sprite_col': 3, 'sprite_row': 0},  # Blocking bathroom
            'Jessica': {'position': (7, 5), 'mood': 'sympathetic', 'active': True, 'sprite_num': 10, 'sprite_col': 0, 'sprite_row': 0},  # Center/couch
            'Mike': {'position': (14, 7), 'mood': 'apologetic', 'active': True, 'sprite_num': 2, 'sprite_col': 0, 'sprite_row': 0}  # His room door
        }

        # Load character sprites for roommates
        self.load_roommate_sprites()

        # Player belongings tracking
        self.belongings = {
            'phone_charger': {'status': 'safe', 'location': 'backpack'},
            'work_uniform': {'status': 'safe', 'location': 'backpack'},
            'toothbrush': {'status': 'safe', 'location': 'backpack'},
            'spare_clothes': {'status': 'safe', 'location': 'backpack'},
            'documents': {'status': 'safe', 'location': 'backpack'},
            'family_photo': {'status': 'safe', 'location': 'backpack'},
            'wallet': {'status': 'safe', 'location': 'pocket'},
            'phone': {'status': 'safe', 'location': 'pocket'}
        }

        # Floor space assignment
        self.player_floor_spot = (3, 9)  # Near kitchen, worst spot
        self.setup_complete = False

        # Random events timer
        self.event_timer = 0
        self.next_event_time = random.uniform(5, 15)

        # Visual effects
        self.particles = []  # For noise/chaos particles
        self.screen_shake = 0
        self.shake_intensity = 0

    def load_roommate_sprites(self):
        """Load character sprites for each roommate - using 16x16 sheets like other NPCs"""
        self.roommate_sprites = {}
        sprite_width = 16
        sprite_height = 32  # Characters are 2 tiles tall

        for name, data in self.roommates.items():
            sprite_num = data['sprite_num']
            sprite_col = data.get('sprite_col', 0)
            sprite_row = data.get('sprite_row', 0)

            # Use 16x16 character sheets, not 32x32
            sprite_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
                '0_Premade_Characters', '16x16', f'Premade_Character_{sprite_num:02d}.png'
            )

            try:
                spritesheet = pygame.image.load(sprite_path)
                # Extract the sprite from the correct position on the sheet
                # Characters are 16 wide, 32 tall
                sprite_rect = pygame.Rect(
                    sprite_col * sprite_width,
                    sprite_row * sprite_height,
                    sprite_width,
                    sprite_height
                )
                sprite_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                sprite_surface.blit(spritesheet, (0, 0), sprite_rect)

                # Scale to match tile size (characters are 2 tiles tall)
                scaled_sprite = pygame.transform.scale(
                    sprite_surface,
                    (self.TILE_SIZE, self.TILE_SIZE * 2)
                )
                scaled_sprite = scaled_sprite.convert_alpha()

                self.roommate_sprites[name] = scaled_sprite
                print(f"Loaded sprite for {name} from character {sprite_num:02d}")
            except Exception as e:
                print(f"Failed to load sprite for {name}: {e}")
                self.roommate_sprites[name] = None

    def load_narrative_content(self):
        """Load Mike's place narrative content"""
        return {
            'mike_floor': {
                'npcs': [
                    {'name': 'Mike', 'x': 14, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Mike", "Hey! Sorry about the mess. We've got 5 people in a 2-bedroom."),
                    ("Mike", "You can crash on the floor by the kitchen tonight."),
                    ("You", "Just tonight is fine. Thanks Mike."),
                    ("Brian", "Another freeloader? This place is already too crowded!"),
                    ("Tyler", "Hope you don't need sleep. I've got a playlist to get through!"),
                    (None, "The apartment reeks. This is going to be a long night.")
                ],
                'interactions': {
                    'floor_spot': {
                        'position': (3, 9),
                        'prompt': 'Set up sleeping area',
                        'dialogue': [
                            "You unroll the thin blanket Mike gave you.",
                            "The floor is hard and cold. The kitchen light stays on all night.",
                            "Someone's dirty dishes are piled just feet from your head.",
                            "This is going to be a long week."
                        ],
                        'required': True
                    },
                    'backpack_corner': {
                        'position': (2, 10),
                        'prompt': 'Store belongings',
                        'dialogue': [
                            "You tuck your backpack into the corner.",
                            "It contains everything you own. You eye it nervously.",
                            "In this chaos, things could easily go missing."
                        ],
                        'required': True
                    },
                    'bathroom': {
                        'position': (15, 8),
                        'prompt': 'Use bathroom',
                        'dialogue': [
                            "The bathroom is a disaster. Mold in the shower.",
                            "No toilet paper. Someone's underwear on the floor.",
                            "You'll have to buy your own supplies."
                        ],
                        'required': False
                    }
                }
            },

            'losing_stuff': {
                'dialogue_sequence': [
                    (None, "Your belongings are scattered around the apartment."),
                    ("You", "Has anyone seen my phone charger?"),
                    ("Kevin", "Oh, I borrowed it. I think it's... somewhere."),
                    ("You", "My work uniform was right here!"),
                    ("Tyler", "Jessica was doing laundry. Check the pile."),
                    (None, "You search frantically. The uniform is nowhere."),
                    (None, "Without it, you'll lose your job. Without the job, you'll have nothing.")
                ],
                'interactions': {
                    'search_kitchen': {
                        'position': (6, 6),
                        'prompt': 'Search kitchen',
                        'trigger_activity': 'item_search',
                        'dialogue': None,
                        'required': True
                    },
                    'search_living_room': {
                        'position': (10, 7),
                        'prompt': 'Search living room',
                        'trigger_activity': 'item_search',
                        'dialogue': None,
                        'required': True
                    },
                    'check_backpack': {
                        'position': (2, 10),
                        'prompt': 'Check remaining items',
                        'dialogue': [
                            "You inventory what's left:",
                            "Phone charger: Missing",
                            "Work uniform: Missing",
                            "Toothbrush: Found in bathroom sink",
                            "Documents: Safe but crumpled",
                            "Family photo: Torn but recoverable",
                            "You're losing pieces of your life."
                        ],
                        'required': True
                    }
                }
            },

            'wearing_out_welcome': {
                'dialogue_sequence': [
                    (None, "It's 6 AM. You haven't slept at all."),
                    ("You", "I can't do another night like this..."),
                    ("Mike", "Yeah... about that. Brian's already complained to the landlord."),
                    ("Mike", "You should probably find somewhere else tonight."),
                    (None, "You gather what's left of your belongings."),
                    (None, "Another 'temporary' solution that didn't work out."),
                    (None, "The emergency shelter is your only option now.")
                ],
                'interactions': {
                    'pack_what_remains': {
                        'position': (2, 10),
                        'prompt': 'Pack remaining belongings',
                        'dialogue': [
                            "You gather what's left of your things.",
                            "Half your belongings are gone.",
                            "Your work uniform never turned up.",
                            "You lost your job yesterday because of it.",
                            "Everything is falling apart."
                        ],
                        'required': True
                    },
                    'leave_apartment': {
                        'position': (8, 11),
                        'prompt': 'Leave Mike\'s place',
                        'dialogue': [
                            "Mike slips you $20 as you leave. 'For food,' he says.",
                            "You want to refuse but you need it too badly.",
                            "The door closes behind you.",
                            "Where do you go when you've worn out every welcome?"
                        ],
                        'required': True
                    }
                }
            }
        }

    def add_noise_particle(self, x, y, particle_type='music'):
        """Add visual particle for noise/chaos"""
        particle = {
            'x': x,
            'y': y,
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-3, -1),
            'life': 60,
            'type': particle_type,
            'color': (255, 200, 100) if particle_type == 'music' else (255, 100, 100)
        }
        self.particles.append(particle)

    def update_particles(self, dt):
        """Update visual effect particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            particle['life'] -= 1

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        """Draw visual effect particles"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 60))
            color = (*particle['color'], alpha)

            if particle['type'] == 'music':
                # Draw music note
                pygame.draw.circle(screen, particle['color'],
                                 (int(particle['x']), int(particle['y'])),
                                 5, 2)
                pygame.draw.line(screen, particle['color'],
                               (int(particle['x']) + 5, int(particle['y'])),
                               (int(particle['x']) + 5, int(particle['y']) - 10), 2)
            else:
                # Draw angry exclamation
                font = pygame.font.Font(None, 20)
                text = font.render("!", True, particle['color'])
                screen.blit(text, (int(particle['x']), int(particle['y'])))

    def trigger_screen_shake(self, intensity=5, duration=10):
        """Trigger screen shake effect"""
        self.screen_shake = duration
        self.shake_intensity = intensity

    def interact_with_object(self, obj_name):
        """Override to handle interaction completion"""
        super().interact_with_object(obj_name)

        # Mark this interaction as completed
        self.interactions_completed.add(obj_name)

        # Check if both setup interactions are done
        if 'floor_spot' in self.interactions_completed and 'backpack_corner' in self.interactions_completed:
            if not self.setup_complete:
                self.setup_complete = True
                # Start chaos immediately
                self.dialogue_box.show(None, "Time to try to sleep...")
                # Trigger Tyler's music
                self.noise_level = 90
                self.trigger_screen_shake(5, 20)
                self.roommates['Tyler']['mood'] = 'loud'
                # Add music particles
                for _ in range(10):
                    offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
                    offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2
                    tx = offset_x + self.roommates['Tyler']['position'][0] * self.TILE_SIZE
                    ty = offset_y + self.roommates['Tyler']['position'][1] * self.TILE_SIZE
                    self.add_noise_particle(tx + random.randint(-20, 20), ty + random.randint(-20, 20), 'music')

    def trigger_random_event(self):
        """Random chaotic events in the apartment"""
        events = [
            {
                'actor': 'Tyler',
                'action': 'starts blasting music at 2 AM',
                'effect': lambda: (
                    setattr(self, 'noise_level', min(100, self.noise_level + 30)),
                    self.trigger_screen_shake(3, 15),
                    [self.add_noise_particle(
                        self.roommates['Tyler']['position'][0] * self.TILE_SIZE + random.randint(-20, 20) + 256,
                        self.roommates['Tyler']['position'][1] * self.TILE_SIZE + random.randint(-20, 20) + 128,
                        'music'
                    ) for _ in range(5)]
                )
            },
            {
                'actor': 'Kevin',
                'action': 'spills food near your sleeping area',
                'effect': lambda: setattr(self, 'cleanliness', max(0, self.cleanliness - 20))
            },
            {
                'actor': 'Brian',
                'action': 'complains loudly about "freeloaders"',
                'effect': lambda: self.lose_random_item()
            },
            {
                'actor': 'Someone',
                'action': 'is using the bathroom... for the past hour',
                'effect': lambda: None
            },
            {
                'actor': 'The neighbors',
                'action': 'are banging on the wall about the noise',
                'effect': lambda: setattr(self, 'chaos_level', min(100, self.chaos_level + 20))
            }
        ]

        event = random.choice(events)
        self.dialogue_box.show(None, f"{event['actor']} {event['action']}.")
        event['effect']()

    def lose_random_item(self):
        """Randomly lose a belonging"""
        safe_items = [k for k, v in self.belongings.items() if v['status'] == 'safe']
        if safe_items:
            lost_item = random.choice(safe_items)
            self.belongings[lost_item]['status'] = 'missing'
            self.belongings[lost_item]['location'] = 'unknown'

            # Special message for important items
            if lost_item == 'work_uniform':
                self.dialogue_box.show(None, "Your work uniform is missing! This is a disaster!")
            elif lost_item == 'phone_charger':
                self.dialogue_box.show(None, "Your phone charger disappeared. Phone at 12%.")

    def update(self, dt):
        """Update chaos mechanics and visual effects"""
        super().update(dt)

        # Update visual effects
        self.update_particles(dt)

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

        # Chaos naturally increases
        self.chaos_level = min(100, self.chaos_level + dt * 2)

        # Generate ambient noise particles when noise is high
        if self.noise_level > 60 and random.random() < 0.02:
            # Random music notes from Tyler's position
            if 'Tyler' in self.roommates and self.roommates['Tyler']['active']:
                offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
                offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2
                tx = offset_x + self.roommates['Tyler']['position'][0] * self.TILE_SIZE
                ty = offset_y + self.roommates['Tyler']['position'][1] * self.TILE_SIZE
                self.add_noise_particle(tx + 16, ty, 'music')

        # Random events
        self.event_timer += dt
        if self.event_timer >= self.next_event_time and not self.dialogue_box.active:
            self.trigger_random_event()
            self.event_timer = 0
            self.next_event_time = random.uniform(10, 25)

        # Sleep deprivation accumulates faster
        if self.noise_level > 70:
            self.hours_no_sleep += dt * 30  # Much faster accumulation

        # Check narrative progression
        current = self.game.objective_manager.get_current_objective()
        if current:
            # After initial setup, start chaos
            if current.id == 'mike_floor' and self.setup_complete and self.narrative_stage == 'arrival':
                self.narrative_stage = 'chaos'
                self.start_narrative_sequence('losing_stuff')

            # After enough chaos and exhaustion, time to leave
            elif self.narrative_stage == 'chaos' and self.hours_no_sleep >= 8:
                if not hasattr(self, 'leaving_triggered'):
                    self.leaving_triggered = True
                    self.narrative_stage = 'leaving'
                    self.start_narrative_sequence('wearing_out_welcome')

    def draw(self, screen):
        """Draw Mike's chaotic apartment with all visual elements"""
        # Always draw the base room first
        super().draw(screen)

        # Only apply to active interior
        if not self.active:
            return

        # Apply screen shake if active
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake > 0:
            shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        # Create drawing surface (with or without shake)
        if self.screen_shake > 0:
            draw_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            draw_surface.blit(screen, (0, 0))  # Copy current screen
        else:
            draw_surface = screen

        # Always draw environmental elements (they're part of the room)
        # Draw mess and clutter
        self.draw_apartment_mess(draw_surface)

        # Always draw roommates - they live here!
        self.draw_roommates(draw_surface)

        # Draw particles (music notes, etc.)
        self.draw_particles(draw_surface)

        # Add atmospheric overlay for poor air quality
        if self.chaos_level > 60:
            haze = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            haze.fill((100, 80, 60, int(20 * (self.chaos_level / 100))))
            draw_surface.blit(haze, (0, 0))

        # Apply shake effect if active
        if self.screen_shake > 0:
            screen.fill((0, 0, 0))  # Clear screen
            screen.blit(draw_surface, (shake_offset_x, shake_offset_y))

        # Draw UI elements only when dialogue is not active
        if not self.dialogue_box.active:
            # Draw chaos meters
            self.draw_chaos_ui(screen)

            # Draw belongings status
            self.draw_belongings_status(screen)

            # Draw exhaustion indicator
            self.draw_exhaustion_indicator(screen)

    def draw_exhaustion_indicator(self, screen):
        """Draw exhaustion level prominently"""
        if self.hours_no_sleep > 0:
            font = pygame.font.Font(None, 24)
            hours = int(self.hours_no_sleep)
            if hours < 3:
                text = f"Tired: {hours} hours without sleep"
                color = (255, 255, 200)
            elif hours < 6:
                text = f"Exhausted: {hours} hours without sleep"
                color = (255, 200, 100)
            else:
                text = f"DESPERATE: {hours} hours without sleep!"
                color = (255, 100, 100)

            text_surf = font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 30))

            # Draw background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, (50, 50, 60), bg_rect, 0, 5)
            pygame.draw.rect(screen, (200, 200, 200), bg_rect, 2, 5)
            screen.blit(text_surf, text_rect)

    def draw_chaos_ui(self, screen):
        """Draw chaos level indicators with improved styling"""
        # Create panel for meters
        panel_x = 10
        panel_y = 60
        panel_width = 200
        panel_height = 140

        # Draw panel background
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((30, 30, 40, 200))
        pygame.draw.rect(panel_surf, (150, 150, 150), panel_surf.get_rect(), 2, 5)
        screen.blit(panel_surf, (panel_x, panel_y))

        # Title
        font_title = pygame.font.Font(None, 18)
        title = font_title.render("APARTMENT STATUS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 15))
        screen.blit(title, title_rect)

        y_offset = panel_y + 35

        # Chaos level
        self.draw_meter(screen, "CHAOS", self.chaos_level, 100, panel_x + 10, y_offset, (255, 100, 100))
        y_offset += 25

        # Noise level
        self.draw_meter(screen, "NOISE", self.noise_level, 100, panel_x + 10, y_offset, (255, 200, 100))
        y_offset += 25

        # Cleanliness (inverted - lower is worse)
        self.draw_meter(screen, "FILTH", 100 - self.cleanliness, 100, panel_x + 10, y_offset, (150, 100, 50))
        y_offset += 25

        # Sleep deprivation
        if self.hours_no_sleep > 0:
            font = pygame.font.Font(None, 16)
            hours = int(self.hours_no_sleep)
            if hours < 24:
                sleep_text = f"Awake: {hours}h"
                color = (255, 200, 150)
            else:
                sleep_text = f"No sleep: {hours//24}d {hours%24}h"
                color = (255, 100, 100)
            text_surf = font.render(sleep_text, True, color)
            screen.blit(text_surf, (panel_x + 10, y_offset))

    def draw_meter(self, screen, label, value, max_value, x, y, color):
        """Draw a styled status meter"""
        meter_width = 120
        meter_height = 16

        # Label
        font = pygame.font.Font(None, 14)
        label_surf = font.render(label, True, (220, 220, 220))
        screen.blit(label_surf, (x, y))

        # Meter position
        meter_x = x + 50
        meter_y = y

        # Background
        pygame.draw.rect(screen, (20, 20, 20), (meter_x, meter_y, meter_width, meter_height), 0, 3)

        # Value bar with gradient effect
        if value > 0:
            bar_width = int((value / max_value) * meter_width)
            # Main bar
            pygame.draw.rect(screen, color, (meter_x, meter_y, bar_width, meter_height), 0, 3)
            # Highlight
            highlight_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
            pygame.draw.rect(screen, highlight_color, (meter_x, meter_y, bar_width, meter_height // 3), 0, 3)

        # Border
        pygame.draw.rect(screen, (100, 100, 100), (meter_x, meter_y, meter_width, meter_height), 1, 3)

        # Value text
        value_text = f"{int(value)}%"
        value_surf = font.render(value_text, True, (255, 255, 255))
        value_rect = value_surf.get_rect(center=(meter_x + meter_width // 2, meter_y + meter_height // 2))
        screen.blit(value_surf, value_rect)

    def draw_belongings_status(self, screen):
        """Draw status of player's belongings with icons"""
        # Create semi-transparent background panel
        panel_width = 260
        panel_height = 220
        panel_x = self.SCREEN_WIDTH - panel_width - 10
        panel_y = 60

        # Draw panel background
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((40, 40, 50, 220))
        pygame.draw.rect(panel_surf, (200, 200, 200), panel_surf.get_rect(), 2, 5)
        screen.blit(panel_surf, (panel_x, panel_y))

        # Title
        font_title = pygame.font.Font(None, 20)
        font_item = pygame.font.Font(None, 16)

        title = font_title.render("YOUR BELONGINGS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 15))
        screen.blit(title, title_rect)

        # Draw items with icons
        y = panel_y + 35
        x = panel_x + 10

        item_icons = {
            'phone_charger': '🔌',
            'work_uniform': '👔',
            'toothbrush': '🪥',
            'spare_clothes': '👕',
            'documents': '📄',
            'family_photo': '🖼️',
            'wallet': '💳',
            'phone': '📱'
        }

        for item, info in self.belongings.items():
            # Determine status color and text
            if info['status'] == 'missing':
                color = (255, 100, 100)
                status_text = "MISSING!"
                bg_color = (100, 20, 20, 100)
            elif info['status'] == 'damaged':
                color = (255, 200, 100)
                status_text = "DAMAGED"
                bg_color = (100, 80, 20, 100)
            else:
                color = (100, 255, 100)
                status_text = "SAFE"
                bg_color = (20, 60, 20, 100)

            # Draw item background
            item_bg = pygame.Surface((panel_width - 20, 22), pygame.SRCALPHA)
            item_bg.fill(bg_color)
            screen.blit(item_bg, (x, y))

            # Draw icon (as colored square if emoji not supported)
            icon_color = color if info['status'] != 'safe' else (150, 150, 150)
            pygame.draw.rect(screen, icon_color, (x + 5, y + 3, 16, 16), 2)

            # Draw item name
            item_name = item.replace('_', ' ').title()
            name_surf = font_item.render(item_name, True, (255, 255, 255))
            screen.blit(name_surf, (x + 25, y + 3))

            # Draw status
            status_surf = font_item.render(status_text, True, color)
            status_rect = status_surf.get_rect(right=panel_x + panel_width - 15, centery=y + 11)
            screen.blit(status_surf, status_rect)

            y += 24

        # Draw warning if items are missing
        missing_count = sum(1 for info in self.belongings.values() if info['status'] == 'missing')
        if missing_count > 0:
            warning_text = f"WARNING: {missing_count} items missing!"
            warning_surf = font_item.render(warning_text, True, (255, 100, 100))
            warning_rect = warning_surf.get_rect(center=(panel_x + panel_width // 2, y + 10))
            screen.blit(warning_surf, warning_rect)

    def draw_roommates(self, screen):
        """Draw roommate characters properly positioned"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        for name, data in self.roommates.items():
            if data['active']:
                x = offset_x + data['position'][0] * self.TILE_SIZE
                y = offset_y + data['position'][1] * self.TILE_SIZE

                # Draw roommate sprite if available
                if name in self.roommate_sprites and self.roommate_sprites[name]:
                    # Characters are 2 tiles tall, so offset Y by -TILE_SIZE
                    screen.blit(self.roommate_sprites[name], (x, y - self.TILE_SIZE))
                else:
                    # Fallback to circle if sprite loading failed
                    color = {
                        'hostile': (255, 100, 100),
                        'loud': (255, 200, 100),
                        'messy': (150, 150, 100),
                        'sympathetic': (100, 200, 255),
                        'apologetic': (150, 150, 255)
                    }.get(data['mood'], (150, 150, 150))
                    pygame.draw.circle(screen, color, (x + 16, y + 16), 12)

                # Draw name label above character
                font = pygame.font.Font(None, 16)
                name_surf = font.render(name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(x + 16, y - self.TILE_SIZE - 20))

                # Draw background for name based on mood
                mood_color = {
                    'hostile': (180, 50, 50),
                    'loud': (200, 150, 50),
                    'messy': (120, 100, 80),
                    'sympathetic': (50, 150, 200),
                    'apologetic': (100, 100, 180)
                }.get(data['mood'], (100, 100, 100))

                bg_rect = name_rect.inflate(8, 4)
                pygame.draw.rect(screen, mood_color, bg_rect, 0, 3)
                pygame.draw.rect(screen, (200, 200, 200), bg_rect, 1, 3)
                screen.blit(name_surf, name_rect)

    def draw_apartment_mess(self, screen):
        """Draw extensive visual clutter and mess throughout the apartment"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        # Draw floor stains and dirt
        stain_positions = [
            (3, 4, 40, 30, (90, 70, 50, 80)),  # Coffee stain
            (6, 9, 35, 25, (120, 100, 80, 60)),  # Food spill
            (10, 6, 25, 20, (80, 60, 40, 70)),  # Mystery stain
            (12, 10, 30, 30, (100, 80, 60, 50)),  # Another spill
            (5, 3, 20, 15, (70, 50, 30, 60))  # Dirt patch
        ]

        for sx, sy, sw, sh, color in stain_positions:
            stain_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            stain_surf.fill(color)
            x = offset_x + sx * self.TILE_SIZE
            y = offset_y + sy * self.TILE_SIZE
            screen.blit(stain_surf, (x, y))

        # Draw trash items with variety - reduced for better navigation
        trash_items = [
            # Pizza boxes
            (2, 10, 'pizza', (160, 90, 40)),
            (12, 2, 'pizza', (150, 85, 35)),
            # Beer cans
            (1, 5, 'can', (150, 150, 160)),
            (14, 8, 'can', (140, 140, 150)),
            # Dirty clothes
            (15, 10, 'clothes', (100, 100, 120)),
            (1, 2, 'clothes', (80, 80, 100)),
            # Paper/trash
            (6, 1, 'paper', (200, 200, 180)),
            (9, 10, 'paper', (190, 190, 170)),
            # Dishes
            (2, 3, 'dish', (180, 180, 190))
        ]

        for tx, ty, item_type, color in trash_items:
            # Always show trash items - no random flickering
            x = offset_x + tx * self.TILE_SIZE
            y = offset_y + ty * self.TILE_SIZE

            if item_type == 'pizza':
                # Draw pizza box
                pygame.draw.rect(screen, color, (x + 4, y + 6, 24, 20))
                pygame.draw.rect(screen, (color[0]-20, color[1]-20, color[2]-20), (x + 4, y + 6, 24, 20), 2)
                # Pizza grease stains
                pygame.draw.circle(screen, (color[0]+20, color[1], color[2]-10), (x + 16, y + 16), 6)

            elif item_type == 'can':
                # Draw beer/soda can
                pygame.draw.ellipse(screen, color, (x + 10, y + 8, 12, 18))
                pygame.draw.ellipse(screen, (color[0]-30, color[1]-30, color[2]-30), (x + 10, y + 8, 12, 4))

            elif item_type == 'clothes':
                # Draw crumpled clothes
                points = [(x + 8, y + 12), (x + 24, y + 10), (x + 22, y + 22), (x + 10, y + 20)]
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (color[0]-20, color[1]-20, color[2]-20), points, 2)

            elif item_type == 'paper':
                # Draw crumpled paper
                pygame.draw.rect(screen, color, (x + 8, y + 10, 16, 12))
                pygame.draw.lines(screen, (color[0]-40, color[1]-40, color[2]-40), False,
                                [(x + 8, y + 14), (x + 24, y + 14), (x + 8, y + 18), (x + 24, y + 18)], 1)

            elif item_type == 'dish':
                # Draw dirty dishes
                pygame.draw.ellipse(screen, color, (x + 6, y + 10, 20, 12))
                pygame.draw.ellipse(screen, (color[0]-20, color[1]-20, color[2]-10), (x + 6, y + 10, 20, 12), 2)

        # Draw player's sleeping spot on floor (marked with old blanket)
        if hasattr(self, 'player_floor_spot'):
            px, py = self.player_floor_spot
            floor_x = offset_x + px * self.TILE_SIZE
            floor_y = offset_y + py * self.TILE_SIZE
            # Draw thin mattress/blanket
            blanket_color = (80, 90, 100, 180)
            blanket_surf = pygame.Surface((self.TILE_SIZE * 2, int(self.TILE_SIZE * 1.5)), pygame.SRCALPHA)
            blanket_surf.fill(blanket_color)
            screen.blit(blanket_surf, (floor_x - self.TILE_SIZE // 2, floor_y - self.TILE_SIZE // 4))
            # Draw pillow
            pygame.draw.ellipse(screen, (100, 110, 120), (floor_x, floor_y - 10, 25, 15))
            # Label
            font = pygame.font.Font(None, 12)
            label = font.render("Your 'bed'", True, (180, 180, 180))
            screen.blit(label, (floor_x, floor_y - 25))
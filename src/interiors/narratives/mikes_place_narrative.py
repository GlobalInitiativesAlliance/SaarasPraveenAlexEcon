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

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

    def is_mikes_place_active(self):
        """Check if this should actually be Mike's place with all the chaos"""
        # Only show Mike's chaos for Part 1 Mike-specific objectives
        if hasattr(self.game, 'objective_manager'):
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj:
                # Mike-specific objectives that should show full chaos
                mike_objectives = ['mike_floor', 'losing_stuff', 'wearing_out_welcome']
                return current_obj.id in mike_objectives

        # Default to showing Mike's place if no objective info available
        return True

    def deactivate(self):
        """Clean up Mike's place state when leaving"""
        print("[CLEANUP] Deactivating Mike's place - clearing chaos state")

        # Stop all chaos mechanics
        self.chaos_level = 0
        self.noise_level = 0
        self.screen_shake = 0
        self.shake_intensity = 0

        # Clear particles
        self.particles.clear()

        # Reset roommate activity (don't delete them, just make them inactive)
        for name, data in self.roommates.items():
            data['active'] = False

        # Reset timers
        self.event_timer = 0
        self.hours_no_sleep = 0

        # Clear interaction state
        self.interactions_completed.clear()
        self.setup_complete = False

        # Reset narrative stage
        self.narrative_stage = 'arrival'

        # Set as inactive
        self.active = False

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
        """Load Mike's place narrative content - simplified and more purposeful"""
        return {
            'mike_floor': {
                'npcs': [
                    {'name': 'Mike', 'x': 14, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Mike", "Hey! Sorry about the mess. We've got 5 people in a 2-bedroom."),
                    ("Mike", "You can crash on the floor by the kitchen for a few days."),
                    ("You", "Thanks Mike, I really appreciate this."),
                    ("Mike", "Just... try to stay out of everyone's way, okay?"),
                    ("Mike", "My roommates aren't thrilled about another person here."),
                    (None, "This overcrowded apartment shows the reality of housing desperation.")
                ],
                'interactions': {
                    'setup_sleep_area': {
                        'position': (3, 9),
                        'prompt': '💡 Set up sleeping area',
                        'dialogue': [
                            "You lay out the thin blanket Mike gave you on the kitchen floor.",
                            "It's not comfortable, but it's better than the street.",
                            "The refrigerator hums loudly next to your head.",
                            "You can hear the roommates talking in the next room."
                        ],
                        'required': True
                    },
                    'meet_roommates': {
                        'position': (10, 6),
                        'prompt': '💡 Meet the roommates',
                        'dialogue': [
                            "You introduce yourself to Mike's roommates.",
                            "Tyler: 'Hope you don't mind noise - I'm a night owl.'",
                            "Kevin: 'Just don't use my food in the fridge.'",
                            "Brian: 'This place is already too crowded...'",
                            "Everyone seems stressed about the living situation."
                        ],
                        'required': True
                    },
                    'observe_conditions': {
                        'position': (6, 8),
                        'prompt': '💡 Observe living conditions',
                        'dialogue': [
                            "You look around the overcrowded apartment.",
                            "Dirty dishes everywhere, no privacy, tension in the air.",
                            "5 people sharing 1 bathroom and a tiny kitchen.",
                            "This is what housing desperation looks like.",
                            "Everyone here is just trying to survive."
                        ],
                        'required': True
                    }
                }
            },

            'losing_stuff': {
                'dialogue_sequence': [
                    (None, "Day 2 at Mike's place. Something's wrong."),
                    ("You", "Has anyone seen my phone charger?"),
                    ("Kevin", "Oh yeah, I borrowed it. It's... um... somewhere around here."),
                    ("You", "My work uniform was in my backpack!"),
                    ("Tyler", "Jessica did laundry yesterday. Check the pile by the couch."),
                    (None, "In shared spaces, your belongings aren't really safe."),
                    (None, "This is how people lose important things when desperate for housing.")
                ],
                'interactions': {
                    'check_belongings': {
                        'position': (2, 10),
                        'prompt': '💡 Check your belongings',
                        'trigger_activity': 'backpack_investigation',
                        'dialogue': [
                            "You go through your backpack carefully.",
                            "Phone charger: Missing",
                            "Work uniform: Missing",
                            "Important documents: Still here, thankfully",
                            "This shows how vulnerable you are without stable housing."
                        ],
                        'required': True
                    },
                    'talk_to_roommates': {
                        'position': (10, 6),
                        'prompt': '💡 Ask roommates about missing items',
                        'dialogue': [
                            "You politely ask about your missing things.",
                            "Kevin: 'Oh, the charger? I think I left it at work...'",
                            "Tyler: 'Your shirt? Maybe it got mixed up in laundry?'",
                            "No one seems to be lying, but your stuff is still gone.",
                            "This is the reality of unstable housing situations."
                        ],
                        'required': True
                    },
                    'learn_lesson': {
                        'position': (6, 8),
                        'prompt': '💡 Reflect on the situation',
                        'dialogue': [
                            "You realize this is how housing instability works.",
                            "Without your own space, you can't protect your belongings.",
                            "Every day you risk losing something important.",
                            "Your work uniform missing could cost you your job.",
                            "Stable housing isn't just about shelter - it's about security."
                        ],
                        'required': True
                    }
                }
            },

            'wearing_out_welcome': {
                'dialogue_sequence': [
                    (None, "Day 3 at Mike's place. The situation has changed."),
                    ("Mike", "Hey... we need to talk."),
                    ("Mike", "The landlord came by yesterday asking questions."),
                    ("Mike", "He's suspicious about how many people are living here."),
                    ("Brian", "If he finds out there's an extra person, we could all get evicted."),
                    ("Mike", "I'm really sorry, but you need to find somewhere else."),
                    ("You", "I understand... Thanks for letting me stay this long."),
                    (None, "Even temporary housing arrangements can fall apart quickly."),
                    (None, "When you're housing insecure, you're always one step from the street.")
                ],
                'interactions': {
                    'understand_situation': {
                        'position': (14, 4),
                        'prompt': '💡 Talk to Mike',
                        'dialogue': [
                            "Mike explains the landlord situation in more detail.",
                            "'He counts cars in the parking lot, watches for too much activity.'",
                            "'If we get evicted, all 5 of us lose our housing too.'",
                            "You realize Mike is also in a precarious situation.",
                            "Everyone here is just trying to avoid homelessness."
                        ],
                        'required': True
                    },
                    'pack_belongings': {
                        'position': (2, 10),
                        'prompt': '💡 Pack your things',
                        'dialogue': [
                            "You carefully pack what belongings you can find.",
                            "Some things are still missing, but you have the essentials.",
                            "Your backpack feels lighter than when you arrived.",
                            "This is how housing instability works - you lose things.",
                            "Time to find another temporary solution."
                        ],
                        'required': True
                    },
                    'leave_with_understanding': {
                        'position': (8, 11),
                        'prompt': '💡 Leave the apartment',
                        'dialogue': [
                            "You thank Mike and his roommates for their help.",
                            "Everyone understands this isn't personal - it's survival.",
                            "Mike: 'I wish things were different, man.'",
                            "You head back to the emergency shelter system.",
                            "This cycle shows why stable housing is so important."
                        ],
                        'required': True,
                        'trigger_completion': True
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
        """Simplified interaction handling - much cleaner"""
        # Get the object data first
        if obj_name in self.interactive_objects:
            obj_data = self.interactive_objects[obj_name]
        else:
            return

        # Check for specific activity triggers that we want to keep
        if 'trigger_activity' in obj_data:
            activity_type = obj_data['trigger_activity']
            if activity_type == 'backpack_investigation':
                self.launch_backpack_investigation()
                return

        # Call parent interaction to show dialogue
        super().interact_with_object(obj_name)

        # Mark this interaction as completed
        if not hasattr(self, 'interactions_completed'):
            self.interactions_completed = set()
        self.interactions_completed.add(obj_name)

        # Check for completion trigger
        if obj_data.get('trigger_completion'):
            self.game.objective_manager.complete_current_objective()

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
        """Update simplified mechanics - much cleaner and more purposeful"""
        super().update(dt)

        # Only run when actually active and in Mike's place
        if not self.active or not self.is_mikes_place_active():
            return

        # Simple progress tracking instead of chaotic mechanics
        current = self.game.objective_manager.get_current_objective()
        if current:
            # Check if all required interactions are complete for current objective
            if hasattr(self, 'interactions_completed'):
                objective_data = self.load_narrative_content().get(current.id, {})
                required_interactions = [key for key, data in objective_data.get('interactions', {}).items()
                                       if data.get('required', False)]

                completed_required = [key for key in required_interactions if key in self.interactions_completed]

                # If all required interactions are done, complete the objective
                if len(completed_required) == len(required_interactions) and len(required_interactions) > 0:
                    if not hasattr(self, f'{current.id}_completed'):
                        setattr(self, f'{current.id}_completed', True)
                        self.game.objective_manager.complete_current_objective()

    def draw(self, screen):
        """Draw Mike's apartment with clean, purposeful visuals"""
        # Always draw the base room first
        super().draw(screen)

        # Only apply Mike's elements when actually active AND in Mike's place
        if not self.active or not self.is_mikes_place_active():
            return

        # Draw a cleaner version of the apartment mess (not overwhelming)
        self.draw_apartment_mess(screen)

        # Draw roommates with clear labels
        self.draw_roommates(screen)

        # Draw simple, clear instructions and interaction highlights
        if not self.dialogue_box.active:
            self.draw_instructions(screen)
            self.draw_interaction_highlights(screen)

    def draw_instructions(self, screen):
        """Draw clear, helpful instructions"""
        font = pygame.font.Font(None, 20)
        current = self.game.objective_manager.get_current_objective()

        if current:
            if current.id == 'mike_floor':
                instruction_text = "💡 Complete all interactions to understand the housing situation"
            elif current.id == 'losing_stuff':
                instruction_text = "💡 Learn about the challenges of protecting belongings without stable housing"
            elif current.id == 'wearing_out_welcome':
                instruction_text = "💡 Understand why temporary housing arrangements often fail"
            else:
                instruction_text = "💡 Walk to the highlighted interaction points"

            # Draw instruction box
            instruction_rect = pygame.Rect(10, 10, 600, 30)
            pygame.draw.rect(screen, (0, 0, 0, 180), instruction_rect)
            pygame.draw.rect(screen, (255, 255, 255), instruction_rect, 2)

            instruction_surf = font.render(instruction_text, True, (255, 255, 255))
            screen.blit(instruction_surf, (20, 20))

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
            if interaction.get('required', False) and interaction_key not in getattr(self, 'interactions_completed', set()):
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
                    text = font.render(prompt, True, (255, 255, 255))
                    text_x = x + self.TILE_SIZE // 2 - text.get_width() // 2
                    text_y = y - 25

                    # Background for text
                    text_bg = pygame.Rect(text_x - 5, text_y - 2, text.get_width() + 10, text.get_height() + 4)
                    pygame.draw.rect(screen, (0, 0, 0, 180), text_bg)
                    screen.blit(text, (text_x, text_y))

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

    def launch_couch_surfing_activity(self):
        """Launch the couch surfing mini-game with smooth transition"""

        def start_couch_surfing():
            from src.activities.couch_surfing_game import CouchSurfingGame

            # Clear any active dialogue
            if hasattr(self, 'dialogue_box'):
                self.dialogue_box.hide()

            # Create and start the activity
            activity = CouchSurfingGame()
            activity.start()
            self.current_activity = activity

            # Set it in the game/objective manager if available
            if hasattr(self.game, 'objective_manager'):
                self.game.objective_manager.current_activity = activity

        # Use professional smooth transition
        self.launch_activity_with_transition(start_couch_surfing)

    def launch_housing_dialogue_activity(self):
        """Launch the housing dialogue system with smooth transition"""

        def start_housing_dialogue():
            from src.activities.housing_dialogue import HousingDialogueActivity

            # Clear any active dialogue
            if hasattr(self, 'dialogue_box'):
                self.dialogue_box.hide()

            # Create and start the activity
            activity = HousingDialogueActivity(self.game.objective_manager if hasattr(self.game, 'objective_manager') else None)
            activity.start()
            self.current_activity = activity

            # Set it in the game/objective manager if available
            if hasattr(self.game, 'objective_manager'):
                self.game.objective_manager.current_activity = activity

        # Use professional smooth transition
        self.launch_activity_with_transition(start_housing_dialogue)

    def launch_shelter_night_activity(self):
        """Launch the shelter night survival game with smooth transition"""

        def start_shelter_night():
            from src.activities.shelter_night_game import ShelterNightGame

            # Clear any active dialogue
            if hasattr(self, 'dialogue_box'):
                self.dialogue_box.hide()

            # Create and start the activity
            activity = ShelterNightGame()
            activity.start()
            self.current_activity = activity

            # Set it in the game/objective manager if available
            if hasattr(self.game, 'objective_manager'):
                self.game.objective_manager.current_activity = activity

        # Use professional smooth transition
        self.launch_activity_with_transition(start_shelter_night)

    def launch_backpack_investigation(self):
        """Launch the backpack investigation activity with smooth transition"""

        def start_backpack_investigation():
            from src.activities.backpack_investigation import BackpackInvestigation

            # Clear any active dialogue
            if hasattr(self, 'dialogue_box'):
                self.dialogue_box.hide()

            # Create and start the activity
            activity = BackpackInvestigation(self.game)
            self.current_activity = activity

            # Set it in the game/objective manager if available
            if hasattr(self.game, 'objective_manager'):
                self.game.objective_manager.current_activity = activity

        # Use professional smooth transition
        self.launch_activity_with_transition(start_backpack_investigation)

    def launch_text_desperation(self):
        """Launch the text messaging desperation activity (already exists)"""
        from src.activities.text_desperation import TextDesperation

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = TextDesperation(self.game)
        activity.start()
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity
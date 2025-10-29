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

        # Now call super().__init__() after all attributes are initialized
        super().__init__(game, room_data, building_pos)

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

        # Set initial state based on objective
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'sarah_responds':
                self.current_time = "11:00 PM"
                self.parents_awake = False
            elif current.id == 'sneaking_around':
                self.current_time = "5:30 AM"
                self.day_count = 2

    def handle_stealth_movement(self, new_x, new_y):
        """Handle movement with stealth mechanics"""
        # Check if stepping on creaky tile
        if (new_x, new_y) in self.creaky_tiles and not self.is_sneaking:
            self.noise_level += 30
            self.parents_awareness += 15

            # Show warning
            self.dialogue_box.show(None, "*CREAK* The floorboard groans loudly!")

            # Check if parents wake up
            if self.parents_awareness > 70:
                self.trigger_caught_sequence()
                return False

        # Normal tile movement
        elif not self.is_sneaking:
            self.noise_level += 5
        else:
            self.noise_level += 2  # Quieter when sneaking

        # Decay noise over time
        self.noise_level = max(0, self.noise_level - 1)

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
        """Handle input with stealth mode"""
        # Check for sneak mode (holding shift)
        self.is_sneaking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Slower movement when sneaking
        if not self.dialogue_box.active:
            new_x, new_y = self.player_pixel_x, self.player_pixel_y
            move_speed = self.TILE_SIZE // 8 if self.is_sneaking else self.TILE_SIZE // 4

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x -= move_speed
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x += move_speed
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                new_y -= move_speed
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                new_y += move_speed
            else:
                return

            # Check tile boundaries and stealth
            new_tile_x = int(new_x // self.TILE_SIZE)
            new_tile_y = int(new_y // self.TILE_SIZE)

            if (0 <= new_tile_x < self.room_width and
                0 <= new_tile_y < self.room_height):

                if self.handle_stealth_movement(new_tile_x, new_tile_y):
                    self.player_pixel_x = new_x
                    self.player_pixel_y = new_y

    def update(self, dt):
        """Update stealth mechanics and time"""
        super().update(dt)

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

        # Complete objective
        self.game.objective_manager.complete_current_objective()
        self.should_exit = True

    def draw(self, screen):
        """Draw Sarah's house with stealth UI"""
        super().draw(screen)

        if self.active and not self.dialogue_box.active:
            # Draw noise meter
            self.draw_noise_meter(screen)

            # Draw parent awareness indicator
            self.draw_awareness_indicator(screen)

            # Draw time display
            self.draw_time_display(screen)

            # Draw creaky floorboards (subtle highlight)
            self.draw_creaky_tiles(screen)

            # Draw sneak mode indicator
            if self.is_sneaking:
                font = pygame.font.Font(None, 20)
                sneak_text = font.render("SNEAKING", True, (100, 150, 255))
                screen.blit(sneak_text, (10, 100))

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
        """Draw current time and day"""
        font = pygame.font.Font(None, 22)
        time_text = font.render(f"Day {self.day_count} - {self.current_time}", True, (200, 200, 200))
        screen.blit(time_text, (10, 10))

        # Warning if close to wake time
        if self.current_time == "6:15 AM":
            warning = font.render("15 MINUTES UNTIL PARENTS WAKE!", True, (255, 100, 100))
            x = self.SCREEN_WIDTH // 2 - warning.get_width() // 2
            screen.blit(warning, (x, 90))

    def draw_creaky_tiles(self, screen):
        """Draw subtle highlights on creaky floorboards"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        for tile_x, tile_y in self.creaky_tiles:
            x = offset_x + tile_x * self.TILE_SIZE
            y = offset_y + tile_y * self.TILE_SIZE

            # Very subtle red tint
            s = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            s.set_alpha(30)
            s.fill((255, 100, 100))
            screen.blit(s, (x, y))
"""
Mike's Place Interior - Couch Surfing Chapter 3
Handles objectives: mike_floor, losing_stuff, wearing_out_welcome
"""
import pygame
import random
from src.interiors.narrative_interior import NarrativeInterior

class MikesPlaceNarrative(NarrativeInterior):
    """Mike's chaotic apartment with roommate dynamics"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Chaos mechanics
        self.chaos_level = 75  # Starts high
        self.noise_level = 60
        self.cleanliness = 20  # Very messy

        # Roommate tracking
        self.roommates = {
            'Tyler': {'position': (12, 5), 'mood': 'loud', 'active': True},
            'Kevin': {'position': (8, 8), 'mood': 'messy', 'active': True},
            'Brian': {'position': (10, 10), 'mood': 'hostile', 'active': True},
            'Jessica': {'position': (5, 7), 'mood': 'sympathetic', 'active': True},
            'Mike': {'position': (14, 4), 'mood': 'apologetic', 'active': True}
        }

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

        # Day tracking
        self.current_day = 1
        self.max_days = 7
        self.hours_no_sleep = 0

        # Floor space assignment
        self.player_floor_spot = (3, 9)  # Near kitchen, worst spot

        # Random events timer
        self.event_timer = 0
        self.next_event_time = random.uniform(5, 15)

    def load_narrative_content(self):
        """Load Mike's place narrative content"""
        return {
            'mike_floor': {
                'npcs': [
                    {'name': 'Mike', 'x': 14, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Mike", "Hey! Sorry about the mess. We've got 5 people in a 2-bedroom."),
                    ("Mike", "You can crash on the floor over there by the kitchen."),
                    ("You", "Thanks Mike, I really appreciate this."),
                    ("Mike", "Fair warning - Tyler plays music until like 3 AM and Brian is..."),
                    ("Brian", "Who's this? We already have too many people here!"),
                    ("Mike", "It's just for a week, Brian. They're in a tough spot."),
                    ("Brian", "Whatever. Touch my stuff and we have problems."),
                    (None, "The apartment reeks of old food and unwashed clothes.")
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
                    (None, f"Day {self.current_day}. Your belongings are scattered."),
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
                    ("Mike", "Hey... we need to talk."),
                    ("Mike", "The roommates voted. Brian and Tyler want you out."),
                    ("You", "But it's only been a week..."),
                    ("Mike", "I know, I'm sorry. Brian threatened to call the landlord."),
                    ("Mike", "You've got until tomorrow morning."),
                    (None, "Another couch lost. Another bridge burned."),
                    (None, "You're running out of options. Running out of friends."),
                    (None, "The emergency shelter is your last resort.")
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

    def trigger_random_event(self):
        """Random chaotic events in the apartment"""
        events = [
            {
                'actor': 'Tyler',
                'action': 'starts blasting music at 2 AM',
                'effect': lambda: setattr(self, 'noise_level', min(100, self.noise_level + 30))
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
        """Update chaos mechanics"""
        super().update(dt)

        # Chaos naturally increases
        self.chaos_level = min(100, self.chaos_level + dt * 2)

        # Random events
        self.event_timer += dt
        if self.event_timer >= self.next_event_time and not self.dialogue_box.active:
            self.trigger_random_event()
            self.event_timer = 0
            self.next_event_time = random.uniform(10, 25)

        # Sleep deprivation
        if self.noise_level > 70:
            self.hours_no_sleep += dt * 10  # Accelerated for gameplay

        # Check objectives
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'losing_stuff' and self.current_day >= 4:
                # Trigger major loss event
                if self.belongings['work_uniform']['status'] == 'safe':
                    self.belongings['work_uniform']['status'] = 'missing'
                    self.dialogue_box.show(None, "Your work uniform is gone. You need it for your shift!")

            elif current.id == 'wearing_out_welcome' and self.current_day >= 7:
                # Time to leave
                if not hasattr(self, 'eviction_triggered'):
                    self.eviction_triggered = True
                    self.start_narrative_sequence('wearing_out_welcome')

    def draw(self, screen):
        """Draw Mike's chaotic apartment"""
        super().draw(screen)

        if self.active and not self.dialogue_box.active:
            # Draw chaos meters
            self.draw_chaos_ui(screen)

            # Draw belongings status
            self.draw_belongings_status(screen)

            # Draw roommate positions
            self.draw_roommates(screen)

            # Draw mess and clutter
            self.draw_apartment_mess(screen)

    def draw_chaos_ui(self, screen):
        """Draw chaos level indicators"""
        y_offset = 20

        # Chaos level
        self.draw_meter(screen, "CHAOS", self.chaos_level, 100, 20, y_offset, (255, 100, 100))
        y_offset += 30

        # Noise level
        self.draw_meter(screen, "NOISE", self.noise_level, 100, 20, y_offset, (255, 200, 100))
        y_offset += 30

        # Cleanliness
        self.draw_meter(screen, "CLEAN", self.cleanliness, 100, 20, y_offset, (100, 255, 100))
        y_offset += 30

        # Sleep deprivation
        if self.hours_no_sleep > 0:
            font = pygame.font.Font(None, 20)
            sleep_text = font.render(f"No sleep: {int(self.hours_no_sleep)} hours", True, (255, 150, 150))
            screen.blit(sleep_text, (20, y_offset))

    def draw_meter(self, screen, label, value, max_value, x, y, color):
        """Draw a status meter"""
        meter_width = 150
        meter_height = 20

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (x + 60, y, meter_width, meter_height))

        # Value bar
        bar_width = int((value / max_value) * meter_width)
        pygame.draw.rect(screen, color, (x + 60, y, bar_width, meter_height))

        # Border
        pygame.draw.rect(screen, (200, 200, 200), (x + 60, y, meter_width, meter_height), 2)

        # Label
        font = pygame.font.Font(None, 18)
        label_surf = font.render(label, True, (200, 200, 200))
        screen.blit(label_surf, (x, y + 2))

    def draw_belongings_status(self, screen):
        """Draw status of player's belongings"""
        font = pygame.font.Font(None, 18)
        x = self.SCREEN_WIDTH - 250
        y = 20

        title = font.render("BELONGINGS:", True, (200, 200, 200))
        screen.blit(title, (x, y))
        y += 25

        for item, info in self.belongings.items():
            if info['status'] == 'missing':
                color = (255, 100, 100)
                status = "MISSING"
            elif info['status'] == 'damaged':
                color = (255, 200, 100)
                status = "DAMAGED"
            else:
                color = (100, 200, 100)
                status = "✓"

            item_name = item.replace('_', ' ').title()
            text = font.render(f"{item_name}: {status}", True, color)
            screen.blit(text, (x, y))
            y += 20

    def draw_roommates(self, screen):
        """Draw roommate indicators"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        for name, data in self.roommates.items():
            if data['active']:
                x = offset_x + data['position'][0] * self.TILE_SIZE
                y = offset_y + data['position'][1] * self.TILE_SIZE

                # Draw roommate circle
                color = {
                    'hostile': (255, 100, 100),
                    'loud': (255, 200, 100),
                    'messy': (150, 150, 100),
                    'sympathetic': (100, 200, 255),
                    'apologetic': (150, 150, 255)
                }.get(data['mood'], (150, 150, 150))

                pygame.draw.circle(screen, color, (x + 16, y + 16), 14)

                # Draw name
                font = pygame.font.Font(None, 16)
                name_surf = font.render(name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(x + 16, y - 10))
                screen.blit(name_surf, name_rect)

    def draw_apartment_mess(self, screen):
        """Draw visual clutter and mess"""
        offset_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2
        offset_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2

        # Random mess items based on cleanliness
        if self.cleanliness < 50:
            mess_positions = [
                (4, 6), (7, 8), (9, 5), (11, 9), (5, 10),
                (13, 7), (6, 4), (10, 6), (8, 10), (12, 4)
            ]

            for i, (mx, my) in enumerate(mess_positions):
                if i * 10 > (100 - self.cleanliness):
                    break

                x = offset_x + mx * self.TILE_SIZE
                y = offset_y + my * self.TILE_SIZE

                # Draw trash/mess indicator
                pygame.draw.rect(screen, (80, 60, 40), (x + 8, y + 8, 16, 16))
                pygame.draw.rect(screen, (60, 40, 20), (x + 8, y + 8, 16, 16), 1)
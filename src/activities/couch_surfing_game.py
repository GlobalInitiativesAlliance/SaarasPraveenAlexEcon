"""Couch Surfing Game - Navigate social dynamics while homeless"""

import pygame
import random
from shared.constants import *

class CouchSurfingGame:
    """Manage relationships and survival while couch surfing"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Game state
        self.current_day = 1
        self.max_days = 14  # Two weeks to find something stable
        self.current_host = None
        self.relationship_score = {}
        self.nights_stayed = {}
        self.banned_from = []

        # Resources
        self.energy = 60
        self.hygiene = 70
        self.stress = 40
        self.belongings_safe = True

        # Available friends/contacts
        self.create_contacts()

        # Current situation
        self.current_situation = None
        self.selected_choice = 0

        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # Messages
        self.message = ""
        self.message_timer = 0
        self.message_color = (255, 255, 255)

    def create_contacts(self):
        """Create network of potential hosts"""
        self.contacts = {
            'Sarah': {
                'relationship': 80,
                'max_nights': 3,
                'rules': ['Out by 8am', 'No kitchen use', 'Quiet after 10pm'],
                'personality': 'strict',
                'home_quality': 70,
                'safety': 90
            },
            'Mike': {
                'relationship': 60,
                'max_nights': 5,
                'rules': ['No rules bro', 'Parties happen', 'Lock your stuff'],
                'personality': 'chaotic',
                'home_quality': 40,
                'safety': 50
            },
            'Aunt Lisa': {
                'relationship': 50,
                'max_nights': 7,
                'rules': ['Help with chores', 'No overnight guests', 'Church on Sunday'],
                'personality': 'religious',
                'home_quality': 80,
                'safety': 95
            },
            'Coworker James': {
                'relationship': 40,
                'max_nights': 2,
                'rules': ['Emergency only', 'Keep it professional', 'Don\'t tell boss'],
                'personality': 'awkward',
                'home_quality': 60,
                'safety': 85
            },
            'Online Friend': {
                'relationship': 20,
                'max_nights': 1,
                'rules': ['Never met IRL', 'Seems nice?', 'Has spare room'],
                'personality': 'unknown',
                'home_quality': 50,
                'safety': 30
            }
        }

        # Initialize tracking
        for contact in self.contacts:
            self.relationship_score[contact] = self.contacts[contact]['relationship']
            self.nights_stayed[contact] = 0

    def start(self):
        """Start couch surfing"""
        self.active = True
        self.completed = False
        self.current_day = 1
        self.generate_daily_situation()

    def generate_daily_situation(self):
        """Create situation for current day"""
        if not self.current_host:
            # Need to find place for tonight
            available = [c for c in self.contacts if c not in self.banned_from
                        and self.relationship_score[c] > 20]

            if not available:
                self.current_situation = {
                    'type': 'no_options',
                    'description': 'Nobody is responding to your messages...',
                    'choices': [
                        {'text': 'Sleep outside (dangerous)', 'effects': {
                            'energy': -30, 'hygiene': -40, 'stress': 20, 'safety_risk': True
                        }},
                        {'text': 'Ride buses all night ($5)', 'effects': {
                            'energy': -20, 'hygiene': -20, 'stress': 10, 'cost': 5
                        }},
                        {'text': '24hr laundromat ($3)', 'effects': {
                            'energy': -15, 'hygiene': -10, 'stress': 5, 'cost': 3
                        }}
                    ]
                }
            else:
                self.current_situation = {
                    'type': 'find_host',
                    'description': 'Where will you stay tonight?',
                    'choices': []
                }

                # Add available hosts as choices
                for host in available[:4]:  # Show up to 4 options
                    choice = {
                        'text': f"{host} (Relationship: {self.relationship_score[host]}%)",
                        'host': host,
                        'effects': {}
                    }
                    self.current_situation['choices'].append(choice)

        else:
            # Already staying somewhere - generate host-specific events
            self.generate_host_event()

    def generate_host_event(self):
        """Generate event while staying with current host"""
        host_data = self.contacts[self.current_host]

        events = []

        # Universal events
        events.extend([
            {
                'description': f"{self.current_host} seems annoyed. You've been here {self.nights_stayed[self.current_host]} nights.",
                'choices': [
                    {'text': 'Offer to buy groceries ($20)', 'effects': {
                        'relationship': 10, 'cost': 20
                    }},
                    {'text': 'Clean the entire place', 'effects': {
                        'relationship': 5, 'energy': -20
                    }},
                    {'text': 'Give them space', 'effects': {
                        'relationship': -5, 'stress': 10
                    }}
                ]
            },
            {
                'description': 'You need to shower but they have guests over.',
                'choices': [
                    {'text': 'Wait until later', 'effects': {
                        'hygiene': -20, 'stress': 10
                    }},
                    {'text': 'Quick shower anyway', 'effects': {
                        'hygiene': 30, 'relationship': -10
                    }},
                    {'text': 'Skip shower today', 'effects': {
                        'hygiene': -30, 'energy': -5
                    }}
                ]
            }
        ])

        # Personality-specific events
        if host_data['personality'] == 'strict':
            events.append({
                'description': 'You came back 10 minutes past their curfew.',
                'choices': [
                    {'text': 'Apologize profusely', 'effects': {'relationship': -5}},
                    {'text': 'Make excuse about work', 'effects': {'relationship': -10}},
                    {'text': 'Promise it won\'t happen again', 'effects': {'stress': 15}}
                ]
            })
        elif host_data['personality'] == 'chaotic':
            events.append({
                'description': 'Another party. People going through your stuff.',
                'choices': [
                    {'text': 'Guard your belongings all night', 'effects': {
                        'energy': -30, 'stress': 20
                    }},
                    {'text': 'Hide stuff and try to sleep', 'effects': {
                        'energy': -20, 'belongings_risk': True
                    }},
                    {'text': 'Join the party', 'effects': {
                        'energy': -25, 'relationship': 10, 'hygiene': -20
                    }}
                ]
            })
        elif host_data['personality'] == 'religious':
            events.append({
                'description': f"{self.current_host} insists you join them for church.",
                'choices': [
                    {'text': 'Go along (lose morning)', 'effects': {
                        'relationship': 15, 'energy': -10, 'time_lost': True
                    }},
                    {'text': 'Politely decline', 'effects': {'relationship': -20}},
                    {'text': 'Pretend to be sick', 'effects': {'relationship': -10, 'stress': 10}}
                ]
            })

        self.current_situation = random.choice(events)
        self.current_situation['type'] = 'host_event'

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt

        # Check end conditions
        if self.current_day >= self.max_days:
            self.end_game("Two weeks of couch surfing...", success=True)
        elif self.stress >= 100:
            self.end_game("Mental breakdown from instability")
        elif not self.belongings_safe:
            self.end_game("Your belongings were stolen")

    def handle_key(self, key):
        """Handle input"""
        if not self.active or not self.current_situation:
            return

        if key == pygame.K_UP:
            self.selected_choice = max(0, self.selected_choice - 1)
        elif key == pygame.K_DOWN:
            max_choice = len(self.current_situation['choices']) - 1
            self.selected_choice = min(max_choice, self.selected_choice + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.make_choice()

    def make_choice(self):
        """Execute selected choice"""
        choice = self.current_situation['choices'][self.selected_choice]

        # Handle finding new host
        if self.current_situation['type'] == 'find_host':
            self.current_host = choice.get('host')
            self.nights_stayed[self.current_host] += 1

            host_data = self.contacts[self.current_host]
            self.message = f"Staying with {self.current_host} tonight."
            self.message_timer = 3

            # Apply host-specific effects
            self.energy = min(100, self.energy + (host_data['home_quality'] // 2))
            self.hygiene = min(100, self.hygiene + 20)
            self.stress = max(0, self.stress - 10)

        # Apply choice effects
        effects = choice.get('effects', {})

        if 'relationship' in effects and self.current_host:
            self.relationship_score[self.current_host] += effects['relationship']
            self.relationship_score[self.current_host] = max(0, min(100,
                self.relationship_score[self.current_host]))

            # Check if kicked out
            if self.relationship_score[self.current_host] <= 10:
                self.banned_from.append(self.current_host)
                self.message = f"{self.current_host} asked you to leave. Can't go back."
                self.message_color = (255, 100, 100)
                self.message_timer = 4
                self.current_host = None

        if 'energy' in effects:
            self.energy = max(0, min(100, self.energy + effects['energy']))
        if 'hygiene' in effects:
            self.hygiene = max(0, min(100, self.hygiene + effects['hygiene']))
        if 'stress' in effects:
            self.stress = max(0, min(100, self.stress + effects['stress']))
        if 'belongings_risk' in effects and random.random() < 0.3:
            self.belongings_safe = False

        # Check if need to leave
        if self.current_host:
            if self.nights_stayed[self.current_host] >= self.contacts[self.current_host]['max_nights']:
                self.message = f"You've overstayed at {self.current_host}'s. Time to find somewhere else."
                self.message_color = (255, 200, 100)
                self.message_timer = 4
                self.current_host = None

        # Next day
        self.current_day += 1
        self.selected_choice = 0
        self.generate_daily_situation()

    def end_game(self, reason, success=False):
        """End couch surfing"""
        self.active = False
        self.completed = True
        self.end_reason = reason
        self.success = success

    def draw(self, screen):
        """Draw couch surfing interface"""
        if not self.active:
            return

        screen.fill((25, 25, 35))

        # Title
        title = f"COUCH SURFING - Day {self.current_day} of {self.max_days}"
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))
        screen.blit(title_surf, title_rect)

        # Current host
        if self.current_host:
            host_text = f"Staying with: {self.current_host} (Night {self.nights_stayed[self.current_host]})"
            host_surf = self.font.render(host_text, True, (200, 200, 255))
            host_rect = host_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
            screen.blit(host_surf, host_rect)

        # Stats
        stats_y = 120
        stats = [
            ('Energy', self.energy, (255, 200, 100)),
            ('Hygiene', self.hygiene, (100, 200, 255)),
            ('Stress', self.stress, (255, 100, 100))
        ]

        for name, value, color in stats:
            # Label
            label_surf = self.font.render(name, True, (200, 200, 200))
            screen.blit(label_surf, (100, stats_y))

            # Bar
            bar_rect = pygame.Rect(200, stats_y, 300, 25)
            pygame.draw.rect(screen, (40, 40, 40), bar_rect)
            fill_width = int((value / 100) * 296)
            fill_rect = pygame.Rect(202, stats_y + 2, fill_width, 21)
            pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, (80, 80, 80), bar_rect, 2)

            # Value
            value_surf = self.small_font.render(f"{value}%", True, (255, 255, 255))
            screen.blit(value_surf, (510, stats_y + 3))

            stats_y += 35

        # Relationship status
        rel_y = 250
        rel_text = "Relationships:"
        rel_surf = self.font.render(rel_text, True, (200, 200, 200))
        screen.blit(rel_surf, (100, rel_y))
        rel_y += 30

        for contact in self.contacts:
            score = self.relationship_score[contact]

            if contact in self.banned_from:
                status = "BURNED BRIDGE"
                color = (255, 50, 50)
            elif score > 70:
                status = "Good"
                color = (100, 255, 100)
            elif score > 40:
                status = "Okay"
                color = (255, 255, 100)
            else:
                status = "Strained"
                color = (255, 150, 100)

            contact_text = f"{contact}: {score}% - {status}"
            contact_surf = self.small_font.render(contact_text, True, color)
            screen.blit(contact_surf, (120, rel_y))
            rel_y += 25

        # Current situation
        if self.current_situation:
            # Situation box
            sit_box = pygame.Rect(50, 420, SCREEN_WIDTH - 100, 200)
            pygame.draw.rect(screen, (40, 40, 50), sit_box)
            pygame.draw.rect(screen, (100, 100, 120), sit_box, 2)

            # Description
            desc_surf = self.font.render(self.current_situation['description'], True, (255, 255, 255))
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH // 2, 450))
            screen.blit(desc_surf, desc_rect)

            # Choices
            choice_y = 490
            for i, choice in enumerate(self.current_situation['choices']):
                # Highlight selected
                if i == self.selected_choice:
                    pygame.draw.rect(screen, (60, 60, 80),
                                   (70, choice_y - 5, SCREEN_WIDTH - 140, 30))

                choice_color = (255, 255, 100) if i == self.selected_choice else (200, 200, 200)
                choice_surf = self.font.render(choice['text'], True, choice_color)
                screen.blit(choice_surf, (80, choice_y))
                choice_y += 35

        # Message
        if self.message_timer > 0:
            msg_surf = self.font.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))

            # Message background
            pygame.draw.rect(screen, (20, 20, 30), msg_rect.inflate(20, 10))
            pygame.draw.rect(screen, self.message_color, msg_rect.inflate(20, 10), 2)
            screen.blit(msg_surf, msg_rect)
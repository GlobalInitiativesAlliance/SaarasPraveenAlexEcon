"""Shelter Night Game - Survive a night in emergency shelter"""

import pygame
import random
from shared.constants import *

class ShelterNightGame:
    """Try to sleep and keep belongings safe in shelter"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.hours_passed = 0
        self.target_hours = 10  # 8 PM to 6 AM
        self.energy_gained = 0
        self.stress_level = 50
        self.belongings_safe = True
        
        # Sleep quality factors
        self.noise_level = 70
        self.safety_feeling = 30
        self.comfort_level = 20
        
        # Events
        self.current_event = None
        self.event_timer = 0
        self.selected_choice = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Visual elements
        self.cot_positions = [
            (100, 200), (250, 200), (400, 200), (550, 200),
            (100, 350), (250, 350), (400, 350), (550, 350)
        ]
        self.player_cot = 2  # Third cot
        
    def start(self):
        """Start shelter night"""
        self.active = True
        self.completed = False
        self.hours_passed = 0
        self.generate_event()
        
    def generate_event(self):
        """Generate random shelter events"""
        events = [
            {
                'description': 'Someone is going through your bag!',
                'choices': [
                    {'text': 'Confront them', 'effects': {'stress': 20, 'safety': -10}},
                    {'text': 'Pretend to sleep', 'effects': {'belongings_risk': True}},
                    {'text': 'Call staff', 'effects': {'noise': 20, 'reputation': -5}}
                ]
            },
            {
                'description': 'Loud argument breaks out nearby',
                'choices': [
                    {'text': 'Try to ignore it', 'effects': {'stress': 15, 'sleep': -20}},
                    {'text': 'Move to different area', 'effects': {'comfort': -10}},
                    {'text': 'Put in earbuds', 'effects': {'belongings_risk': True}}
                ]
            },
            {
                'description': 'You really need the bathroom',
                'choices': [
                    {'text': 'Hold it', 'effects': {'comfort': -30, 'stress': 10}},
                    {'text': 'Go (leave belongings)', 'effects': {'belongings_risk': True}},
                    {'text': 'Take everything with you', 'effects': {'energy': -10, 'noise': 10}}
                ]
            },
            {
                'description': 'Staff doing bed checks with flashlights',
                'choices': [
                    {'text': 'Cooperate', 'effects': {'sleep': -15}},
                    {'text': 'Hide contraband', 'effects': {'stress': 25}},
                    {'text': 'Complain', 'effects': {'reputation': -10}}
                ]
            },
            {
                'description': 'Someone offers to watch your stuff',
                'choices': [
                    {'text': 'Trust them', 'effects': {'stress': -10, 'belongings_risk': True}},
                    {'text': 'Politely decline', 'effects': {'stress': 5}},
                    {'text': 'Sleep on your bag', 'effects': {'comfort': -20}}
                ]
            }
        ]
        
        self.current_event = random.choice(events)
        self.event_timer = 3.0
        self.selected_choice = 0
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Progress time
        self.event_timer -= dt
        
        if self.event_timer <= 0 and not self.current_event:
            # Time passes
            self.hours_passed += 1
            
            # Calculate sleep quality
            sleep_quality = (100 - self.noise_level + self.safety_feeling + self.comfort_level) / 3
            self.energy_gained += sleep_quality / 10
            
            # Random chance of event
            if random.random() < 0.4:
                self.generate_event()
                
            # Check if night is over
            if self.hours_passed >= self.target_hours:
                self.end_game()
                
    def handle_key(self, key):
        """Handle input"""
        if not self.active or not self.current_event:
            return
            
        if key == pygame.K_UP:
            self.selected_choice = max(0, self.selected_choice - 1)
        elif key == pygame.K_DOWN:
            self.selected_choice = min(2, self.selected_choice + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.make_choice()
            
    def make_choice(self):
        """Execute selected choice"""
        if not self.current_event:
            return
            
        choice = self.current_event['choices'][self.selected_choice]
        effects = choice['effects']
        
        # Apply effects
        if 'stress' in effects:
            self.stress_level = min(100, self.stress_level + effects['stress'])
        if 'noise' in effects:
            self.noise_level = min(100, self.noise_level + effects['noise'])
        if 'comfort' in effects:
            self.comfort_level = max(0, self.comfort_level + effects['comfort'])
        if 'safety' in effects:
            self.safety_feeling = max(0, self.safety_feeling + effects['safety'])
        if 'sleep' in effects:
            self.energy_gained = max(0, self.energy_gained + effects['sleep'] / 10)
        if 'belongings_risk' in effects and random.random() < 0.3:
            self.belongings_safe = False
            
        self.current_event = None
        
    def end_game(self):
        """End the shelter night"""
        self.active = False
        self.completed = True
        
    def draw(self, screen):
        """Draw shelter environment"""
        if not self.active:
            return
            
        # Dark background
        screen.fill((20, 20, 30))
        
        # Title
        current_hour = 8 + self.hours_passed  # Starting at 8 PM
        if current_hour >= 24:
            current_hour -= 24
        title = f"EMERGENCY SHELTER - {current_hour}:00"
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Draw cots
        for i, pos in enumerate(self.cot_positions):
            x, y = pos
            
            # Cot
            cot_color = (60, 60, 80) if i != self.player_cot else (80, 80, 120)
            pygame.draw.rect(screen, cot_color, (x, y, 120, 60))
            pygame.draw.rect(screen, (40, 40, 60), (x, y, 120, 60), 2)
            
            # Person on cot (except player's cot)
            if i != self.player_cot:
                # Random sleeping person
                person_color = (random.randint(80, 120), random.randint(80, 120), random.randint(80, 120))
                pygame.draw.rect(screen, person_color, (x + 20, y + 10, 80, 40))
                
        # Player on their cot
        player_x, player_y = self.cot_positions[self.player_cot]
        pygame.draw.rect(screen, (100, 100, 150), (player_x + 20, player_y + 10, 80, 40))
        
        # Belongings
        if self.belongings_safe:
            bag_color = (100, 80, 60)
        else:
            bag_color = (200, 50, 50)  # Red if stolen
        pygame.draw.rect(screen, bag_color, (player_x + 5, player_y + 50, 30, 20))
        
        # Stats
        stats_y = 100
        stats = [
            ('Energy Gained', f"{int(self.energy_gained)}%", (100, 200, 100)),
            ('Stress Level', f"{self.stress_level}%", (255, 100, 100)),
            ('Noise Level', f"{self.noise_level}%", (255, 200, 100)),
            ('Safety Feeling', f"{self.safety_feeling}%", (100, 150, 255)),
            ('Belongings', "Safe" if self.belongings_safe else "STOLEN!", 
             (100, 255, 100) if self.belongings_safe else (255, 50, 50))
        ]
        
        for stat_name, stat_value, color in stats:
            # Label
            label_surf = self.small_font.render(stat_name + ":", True, (200, 200, 200))
            screen.blit(label_surf, (50, stats_y))
            
            # Value
            value_surf = self.font.render(stat_value, True, color)
            screen.blit(value_surf, (200, stats_y))
            
            stats_y += 30
            
        # Current event
        if self.current_event:
            # Event box
            event_box = pygame.Rect(150, 400, SCREEN_WIDTH - 300, 180)
            pygame.draw.rect(screen, (40, 40, 50), event_box)
            pygame.draw.rect(screen, (255, 255, 100), event_box, 3)
            
            # Event description
            desc_surf = self.font.render(self.current_event['description'], True, (255, 255, 255))
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH // 2, 430))
            screen.blit(desc_surf, desc_rect)
            
            # Choices
            choice_y = 470
            for i, choice in enumerate(self.current_event['choices']):
                # Highlight selected
                if i == self.selected_choice:
                    pygame.draw.rect(screen, (60, 60, 80), 
                                   (170, choice_y - 5, SCREEN_WIDTH - 340, 30))
                    
                color = (255, 255, 100) if i == self.selected_choice else (200, 200, 200)
                choice_surf = self.font.render(choice['text'], True, color)
                screen.blit(choice_surf, (180, choice_y))
                choice_y += 35
                
        else:
            # Time passing message
            time_msg = f"Hours until morning: {self.target_hours - self.hours_passed}"
            time_surf = self.font.render(time_msg, True, (200, 200, 200))
            time_rect = time_surf.get_rect(center=(SCREEN_WIDTH // 2, 450))
            screen.blit(time_surf, time_rect)
            
        # Shelter rules
        rules = [
            "SHELTER RULES:",
            "- Lights out 10 PM",
            "- No visitors",
            "- Out by 6 AM",
            "- No drugs/weapons"
        ]
        rule_y = 300
        for rule in rules:
            rule_surf = self.small_font.render(rule, True, (150, 150, 150))
            screen.blit(rule_surf, (SCREEN_WIDTH - 200, rule_y))
            rule_y += 20
"""Budget Survival Mini-Game - Make impossible financial decisions"""

import pygame
import random
import math
from shared.constants import *

class BudgetSurvivalGame:
    """Manage $73 for 30 days while homeless"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Starting resources
        self.money = 73.00
        self.days_survived = 0
        self.target_days = 30
        
        # Needs (0-100)
        self.hunger = 70
        self.hygiene = 60
        self.energy = 50
        self.health = 80
        self.phone_battery = 65
        self.work_ready = 50  # How presentable for work
        
        # Status flags
        self.has_shelter_tonight = False
        self.days_without_shower = 2
        self.missed_meals = 0
        self.job_interviews_missed = 0
        
        # Daily events
        self.current_day_events = []
        self.current_event_index = 0
        self.choices_today = []
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # UI state
        self.selected_choice = 0
        self.day_summary = []
        self.game_over_reason = ""
        
    def start(self):
        """Start budget survival"""
        self.active = True
        self.completed = False
        self.days_survived = 0
        self.generate_day_events()
        
    def generate_day_events(self):
        """Generate events for the current day"""
        self.current_day_events = []
        self.current_event_index = 0
        
        # Morning decisions
        self.current_day_events.append({
            'time': 'Morning',
            'description': 'You wake up. What\'s the priority?',
            'choices': [
                {'text': 'Find breakfast ($3-5)', 'cost': random.randint(3, 5), 
                 'effects': {'hunger': 30, 'energy': 20}},
                {'text': 'Skip breakfast (save money)', 'cost': 0,
                 'effects': {'hunger': -20, 'energy': -10}},
                {'text': 'Food bank (2 hr wait)', 'cost': 0, 'time_cost': 2,
                 'effects': {'hunger': 25}},
                {'text': 'Dumpster dive (risky)', 'cost': 0,
                 'effects': {'hunger': 15, 'health': -10, 'hygiene': -20}}
            ]
        })
        
        # Hygiene crisis
        if self.days_without_shower > 2:
            self.current_day_events.append({
                'time': 'Midday',
                'description': f'Haven\'t showered in {self.days_without_shower} days. People avoid you.',
                'choices': [
                    {'text': 'Gym day pass ($15)', 'cost': 15,
                     'effects': {'hygiene': 80, 'work_ready': 40}},
                    {'text': 'Bathroom sink wash', 'cost': 0,
                     'effects': {'hygiene': 20, 'work_ready': 10}},
                    {'text': 'Wait another day', 'cost': 0,
                     'effects': {'hygiene': -10, 'work_ready': -20, 'health': -5}}
                ]
            })
            
        # Phone crisis
        if self.phone_battery < 20:
            self.current_day_events.append({
                'time': 'Urgent',
                'description': 'Phone dying! Need it for job callbacks.',
                'choices': [
                    {'text': 'Buy charger at store ($12)', 'cost': 12,
                     'effects': {'phone_battery': 100}},
                    {'text': 'Charge at library (lose 2 hrs)', 'cost': 0, 'time_cost': 2,
                     'effects': {'phone_battery': 60}},
                    {'text': 'Ask stranger to borrow', 'cost': 0,
                     'effects': {'phone_battery': 30} if random.random() > 0.5 else {}},
                    {'text': 'Let it die', 'cost': 0,
                     'effects': {'job_interviews_missed': 1}}
                ]
            })
            
        # Shelter for tonight
        self.current_day_events.append({
            'time': 'Evening',
            'description': 'Where will you sleep tonight?',
            'choices': [
                {'text': 'Youth hostel ($20/night)', 'cost': 20,
                 'effects': {'energy': 40, 'health': 10, 'has_shelter': True}},
                {'text': 'Night bus riding ($2.50)', 'cost': 2.50,
                 'effects': {'energy': 10, 'has_shelter': True}},
                {'text': 'Under bridge (free, dangerous)', 'cost': 0,
                 'effects': {'energy': -10, 'health': -15, 'hygiene': -15}},
                {'text': '24hr laundromat ($5 washing)', 'cost': 5,
                 'effects': {'energy': 15, 'hygiene': 30, 'has_shelter': True}}
            ]
        })
        
        # Random events
        random_events = [
            {
                'time': 'Random',
                'description': 'Found a $5 bill on the ground!',
                'choices': [
                    {'text': 'Keep it', 'cost': -5, 'effects': {}},
                    {'text': 'Turn it in (karma)', 'cost': 0, 'effects': {'health': 5}}
                ]
            },
            {
                'time': 'Emergency',
                'description': 'Shoes falling apart. Sole is separating.',
                'choices': [
                    {'text': 'Duct tape ($3)', 'cost': 3, 'effects': {'work_ready': 10}},
                    {'text': 'Thrift store shoes ($15)', 'cost': 15, 'effects': {'work_ready': 30}},
                    {'text': 'Keep walking carefully', 'cost': 0, 'effects': {'work_ready': -20}}
                ]
            },
            {
                'time': 'Opportunity',
                'description': 'Job interview tomorrow at 9 AM!',
                'choices': [
                    {'text': 'Prepare (laundry, shower)', 'cost': 20, 
                     'effects': {'work_ready': 50}},
                    {'text': 'Just show up as is', 'cost': 0,
                     'effects': {'job_interviews_missed': 1}}
                ]
            }
        ]
        
        # Add 1-2 random events
        for _ in range(random.randint(1, 2)):
            if random.random() < 0.6:  # 60% chance
                self.current_day_events.append(random.choice(random_events))
                
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Check failure conditions
        if self.money < 0:
            self.end_game("Went into debt. No safety net.")
        elif self.health <= 0:
            self.end_game("Health crisis. No insurance.")
        elif self.hunger <= 0:
            self.end_game("Starving. Collapsed.")
        elif self.job_interviews_missed >= 3:
            self.end_game("Missed too many opportunities.")
            
        # Check success
        if self.days_survived >= self.target_days:
            self.end_game("Survived 30 days!", success=True)
            
    def handle_key(self, key):
        """Handle input"""
        if not self.active:
            return
            
        if self.current_event_index >= len(self.current_day_events):
            if key == pygame.K_SPACE:
                self.end_day()
            return
            
        event = self.current_day_events[self.current_event_index]
        
        if key == pygame.K_UP:
            self.selected_choice = max(0, self.selected_choice - 1)
        elif key == pygame.K_DOWN:
            self.selected_choice = min(len(event['choices']) - 1, self.selected_choice + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.make_choice()
            
    def make_choice(self):
        """Execute selected choice"""
        event = self.current_day_events[self.current_event_index]
        choice = event['choices'][self.selected_choice]
        
        # Apply cost
        self.money -= choice['cost']
        
        # Apply effects
        effects = choice.get('effects', {})
        if 'hunger' in effects:
            self.hunger = max(0, min(100, self.hunger + effects['hunger']))
        if 'hygiene' in effects:
            self.hygiene = max(0, min(100, self.hygiene + effects['hygiene']))
            if effects['hygiene'] > 50:
                self.days_without_shower = 0
        if 'energy' in effects:
            self.energy = max(0, min(100, self.energy + effects['energy']))
        if 'health' in effects:
            self.health = max(0, min(100, self.health + effects['health']))
        if 'phone_battery' in effects:
            self.phone_battery = max(0, min(100, self.phone_battery + effects['phone_battery']))
        if 'work_ready' in effects:
            self.work_ready = max(0, min(100, self.work_ready + effects['work_ready']))
        if 'job_interviews_missed' in effects:
            self.job_interviews_missed += effects['job_interviews_missed']
        if 'has_shelter' in effects:
            self.has_shelter_tonight = True
            
        # Record choice
        self.choices_today.append(f"{event['time']}: {choice['text']}")
        
        # Next event
        self.current_event_index += 1
        self.selected_choice = 0
        
    def end_day(self):
        """Process end of day"""
        # Daily degradation
        self.hunger -= 20
        self.hygiene -= 15
        self.energy -= 10 if self.has_shelter_tonight else 30
        self.phone_battery -= 15
        self.work_ready -= 10
        
        if not self.has_shelter_tonight:
            self.health -= 10
            
        self.days_without_shower += 1
        if self.hunger < 30:
            self.missed_meals += 1
            
        # Reset for next day
        self.days_survived += 1
        self.has_shelter_tonight = False
        self.choices_today = []
        self.generate_day_events()
        
    def end_game(self, reason, success=False):
        """End the game"""
        self.active = False
        self.completed = True
        self.game_over_reason = reason
        self.success = success
        
    def draw(self, screen):
        """Draw the budget game"""
        if not self.active:
            return
            
        screen.fill((20, 25, 35))
        
        # Title
        title = f"SURVIVAL BUDGET - Day {self.days_survived + 1} of {self.target_days}"
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Money
        money_color = (255, 100, 100) if self.money < 20 else (100, 255, 100)
        money_text = f"${self.money:.2f}"
        money_surf = self.title_font.render(money_text, True, money_color)
        money_rect = money_surf.get_rect(center=(SCREEN_WIDTH // 2, 70))
        screen.blit(money_surf, money_rect)
        
        # Stats bars
        stats = [
            ('Hunger', self.hunger, (255, 200, 100)),
            ('Hygiene', self.hygiene, (100, 200, 255)),
            ('Energy', self.energy, (255, 255, 100)),
            ('Health', self.health, (255, 100, 100)),
            ('Phone', self.phone_battery, (200, 100, 255)),
            ('Work Ready', self.work_ready, (100, 255, 100))
        ]
        
        stat_y = 110
        for name, value, color in stats:
            # Label
            label_surf = self.small_font.render(name, True, (200, 200, 200))
            screen.blit(label_surf, (50, stat_y))
            
            # Bar background
            bar_rect = pygame.Rect(150, stat_y, 200, 20)
            pygame.draw.rect(screen, (40, 40, 40), bar_rect)
            
            # Bar fill
            fill_width = int((value / 100) * 196)
            fill_rect = pygame.Rect(152, stat_y + 2, fill_width, 16)
            bar_color = color if value > 30 else (255, 50, 50)
            pygame.draw.rect(screen, bar_color, fill_rect)
            
            # Value
            value_surf = self.small_font.render(f"{int(value)}", True, (255, 255, 255))
            screen.blit(value_surf, (360, stat_y))
            
            stat_y += 25
            
        # Current event
        if self.current_event_index < len(self.current_day_events):
            event = self.current_day_events[self.current_event_index]
            
            # Event box
            event_box = pygame.Rect(50, 300, SCREEN_WIDTH - 100, 250)
            pygame.draw.rect(screen, (40, 40, 50), event_box)
            pygame.draw.rect(screen, (100, 100, 120), event_box, 2)
            
            # Event time
            time_surf = self.font.render(event['time'], True, (255, 200, 100))
            screen.blit(time_surf, (70, 320))
            
            # Event description
            desc_lines = event['description'].split('. ')
            y_offset = 350
            for line in desc_lines:
                if line:
                    desc_surf = self.font.render(line, True, (255, 255, 255))
                    screen.blit(desc_surf, (70, y_offset))
                    y_offset += 25
                    
            # Choices
            y_offset = 410
            for i, choice in enumerate(event['choices']):
                # Selection highlight
                if i == self.selected_choice:
                    pygame.draw.rect(screen, (60, 60, 80), (60, y_offset - 5, SCREEN_WIDTH - 120, 25))
                
                # Choice text
                cost_text = f" (-${choice['cost']})" if choice['cost'] > 0 else ""
                choice_text = choice['text'] + cost_text
                
                color = (255, 100, 100) if choice['cost'] > self.money else (200, 200, 200)
                if i == self.selected_choice:
                    color = (255, 255, 100)
                    
                choice_surf = self.small_font.render(choice_text, True, color)
                screen.blit(choice_surf, (70, y_offset))
                y_offset += 25
                
        else:
            # Day summary
            summary_text = "Day Complete - Press SPACE to continue"
            summary_surf = self.font.render(summary_text, True, (255, 255, 100))
            summary_rect = summary_surf.get_rect(center=(SCREEN_WIDTH // 2, 400))
            screen.blit(summary_surf, summary_rect)
            
        # Status indicators
        if self.days_without_shower > 3:
            smell_text = f"Smell deterring people ({self.days_without_shower} days)"
            smell_surf = self.small_font.render(smell_text, True, (255, 150, 150))
            screen.blit(smell_surf, (50, SCREEN_HEIGHT - 60))
            
        if self.missed_meals > 5:
            starve_text = f"Malnourished ({self.missed_meals} missed meals)"
            starve_surf = self.small_font.render(starve_text, True, (255, 150, 150))
            screen.blit(starve_surf, (50, SCREEN_HEIGHT - 40))
            
        if self.job_interviews_missed > 0:
            missed_text = f"Opportunities lost: {self.job_interviews_missed}"
            missed_surf = self.small_font.render(missed_text, True, (255, 150, 150))
            screen.blit(missed_surf, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 40))
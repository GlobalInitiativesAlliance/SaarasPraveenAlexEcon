"""Medication Rationing Game - Stretch limited medication supply"""

import pygame
import random
import math
from shared.constants import *

class MedicationRationingGame:
    """Manage limited medication while waiting for refill"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.days_until_refill = 14  # 2 weeks
        self.current_day = 1
        
        # Medication supply
        self.pills_remaining = 7  # Only 1 week worth
        self.daily_prescribed = 1
        self.pills_taken_today = 0
        
        # Health metrics
        self.symptom_level = 30  # 0-100 (lower is better)
        self.side_effects = 0  # 0-100
        self.functionality = 70  # 0-100 (higher is better)
        self.withdrawal_risk = 0  # 0-100
        
        # Daily events and choices
        self.current_event = None
        self.daily_choice_made = False
        self.event_history = []
        
        # Visual elements
        self.pill_positions = []
        self.generate_pill_visual()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 48)
        
        # Daily scenarios
        self.scenarios = [
            {
                'text': "Important job interview today",
                'stress_factor': 0.8,
                'functionality_need': 80
            },
            {
                'text': "Just a regular day",
                'stress_factor': 0.2,
                'functionality_need': 50
            },
            {
                'text': "Family gathering - need to appear well",
                'stress_factor': 0.5,
                'functionality_need': 70
            },
            {
                'text': "Feeling worse than usual",
                'stress_factor': 0.9,
                'functionality_need': 60
            },
            {
                'text': "Weekend - can rest at home",
                'stress_factor': 0.1,
                'functionality_need': 30
            },
            {
                'text': "Work presentation deadline",
                'stress_factor': 0.7,
                'functionality_need': 85
            }
        ]
        
    def generate_pill_visual(self):
        """Generate visual pill positions"""
        self.pill_positions = []
        for i in range(30):  # Max 30 pills
            angle = (i / 30) * math.pi * 2
            radius = 80 + (i % 3) * 20
            x = SCREEN_WIDTH // 2 + math.cos(angle) * radius
            y = 300 + math.sin(angle) * radius
            self.pill_positions.append((x, y))
            
    def start(self):
        """Start the rationing game"""
        self.active = True
        self.completed = False
        self.current_day = 1
        self.generate_daily_scenario()
        
    def generate_daily_scenario(self):
        """Create scenario for current day"""
        self.daily_choice_made = False
        self.pills_taken_today = 0
        
        # Select random scenario
        self.current_event = random.choice(self.scenarios)
        
        # Adjust symptom progression
        if self.pills_taken_today == 0 and self.current_day > 1:
            self.symptom_level = min(100, self.symptom_level + 15)
            self.withdrawal_risk = min(100, self.withdrawal_risk + 10)
            
    def take_pill(self, fraction=1.0):
        """Take medication (full or partial dose)"""
        if self.pills_remaining <= 0:
            return
            
        # Consume medication
        self.pills_remaining -= fraction
        self.pills_taken_today += fraction
        
        # Effects of medication
        if fraction >= 1.0:
            # Full dose
            self.symptom_level = max(0, self.symptom_level - 25)
            self.functionality = min(100, self.functionality + 20)
            self.side_effects = min(100, self.side_effects + 5)
            self.withdrawal_risk = max(0, self.withdrawal_risk - 20)
        elif fraction >= 0.5:
            # Half dose
            self.symptom_level = max(0, self.symptom_level - 12)
            self.functionality = min(100, self.functionality + 10)
            self.side_effects = min(100, self.side_effects + 2)
            self.withdrawal_risk = max(0, self.withdrawal_risk - 5)
        else:
            # Quarter dose
            self.symptom_level = max(0, self.symptom_level - 5)
            self.functionality = min(100, self.functionality + 5)
            
        self.daily_choice_made = True
        
    def skip_dose(self):
        """Skip medication for the day"""
        self.symptom_level = min(100, self.symptom_level + 20)
        self.functionality = max(0, self.functionality - 25)
        self.withdrawal_risk = min(100, self.withdrawal_risk + 15)
        self.side_effects = max(0, self.side_effects - 10)
        self.daily_choice_made = True
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active or self.daily_choice_made:
            return
            
        if key == pygame.K_1:
            # Take full dose
            if self.pills_remaining >= 1:
                self.take_pill(1.0)
        elif key == pygame.K_2:
            # Take half dose
            if self.pills_remaining >= 0.5:
                self.take_pill(0.5)
        elif key == pygame.K_3:
            # Take quarter dose
            if self.pills_remaining >= 0.25:
                self.take_pill(0.25)
        elif key == pygame.K_4:
            # Skip dose
            self.skip_dose()
        elif key == pygame.K_SPACE and self.daily_choice_made:
            # Advance to next day
            self.advance_day()
            
    def advance_day(self):
        """Move to next day"""
        self.current_day += 1
        
        # Natural degradation
        self.functionality = max(0, self.functionality - 5)
        self.side_effects = max(0, self.side_effects - 3)
        
        if self.current_day > self.days_until_refill:
            self.end_game()
        else:
            self.generate_daily_scenario()
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update visual effects
        if self.withdrawal_risk > 70:
            # Shaking effect when in withdrawal
            for i in range(len(self.pill_positions)):
                x, y = self.pill_positions[i]
                offset = math.sin(pygame.time.get_ticks() * 0.01 + i) * 2
                self.pill_positions[i] = (x + offset, y)
                
    def end_game(self):
        """End the rationing game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate success based on management
        avg_functionality = self.functionality
        health_maintained = self.symptom_level < 70
        avoided_crisis = self.withdrawal_risk < 80
        
        success = health_maintained and avoided_crisis
        
        return {
            'health': -20 if not success else -5,
            'stress': 30 if not success else 10,
            'message': "Managed medication successfully" if success else "Health deteriorated significantly",
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the medication management interface"""
        if not self.active:
            return
            
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color_value = int(240 - (y / SCREEN_HEIGHT) * 20)
            pygame.draw.line(screen, (color_value, color_value, color_value + 5), 
                           (0, y), (SCREEN_WIDTH, y))
            
        # Title
        title = f"MEDICATION RATIONING - Day {self.current_day}/{self.days_until_refill}"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Pills remaining visual
        pills_area = pygame.Rect(50, 80, 200, 150)
        pygame.draw.rect(screen, (255, 255, 255), pills_area)
        pygame.draw.rect(screen, (100, 100, 120), pills_area, 2)
        
        # Draw pill bottle
        bottle_rect = pygame.Rect(pills_area.centerx - 40, pills_area.y + 20, 80, 100)
        pygame.draw.rect(screen, (255, 140, 0), bottle_rect, 0, 10)
        pygame.draw.rect(screen, (200, 100, 0), bottle_rect, 3, 10)
        
        # Cap
        cap_rect = pygame.Rect(bottle_rect.x + 10, bottle_rect.y - 15, 60, 20)
        pygame.draw.rect(screen, (255, 255, 255), cap_rect)
        pygame.draw.rect(screen, (200, 200, 200), cap_rect, 2)
        
        # Pills count
        pills_text = f"{self.pills_remaining:.2f}"
        pills_surf = self.big_font.render(pills_text, True, (255, 255, 255))
        pills_rect = pills_surf.get_rect(center=bottle_rect.center)
        screen.blit(pills_surf, pills_rect)
        
        pills_label = self.small_font.render("Pills Left", True, (80, 80, 90))
        label_rect = pills_label.get_rect(center=(pills_area.centerx, pills_area.bottom - 20))
        screen.blit(pills_label, label_rect)
        
        # Health metrics panel
        metrics_rect = pygame.Rect(300, 80, 450, 150)
        pygame.draw.rect(screen, (250, 250, 255), metrics_rect)
        pygame.draw.rect(screen, (150, 150, 180), metrics_rect, 2)
        
        metrics = [
            ('Symptoms', self.symptom_level, (255, 100, 100), True),  # Lower is better
            ('Functionality', self.functionality, (100, 200, 100), False),
            ('Side Effects', self.side_effects, (255, 200, 100), True),
            ('Withdrawal Risk', self.withdrawal_risk, (200, 100, 200), True)
        ]
        
        metric_y = metrics_rect.y + 15
        for name, value, color, inverse in metrics:
            # Label
            label_surf = self.font.render(name, True, (60, 60, 80))
            screen.blit(label_surf, (metrics_rect.x + 10, metric_y))
            
            # Bar
            bar_rect = pygame.Rect(metrics_rect.x + 150, metric_y, 250, 20)
            pygame.draw.rect(screen, (220, 220, 230), bar_rect)
            
            # Fill (red/green depending on if lower or higher is better)
            fill_color = color
            if inverse:  # Lower is better
                if value > 70:
                    fill_color = (255, 50, 50)
                elif value > 40:
                    fill_color = (255, 200, 50)
                else:
                    fill_color = (50, 255, 50)
            
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * value / 100), 20)
            pygame.draw.rect(screen, fill_color, fill_rect)
            pygame.draw.rect(screen, (100, 100, 120), bar_rect, 2)
            
            # Value
            value_surf = self.small_font.render(f"{int(value)}%", True, (80, 80, 90))
            screen.blit(value_surf, (bar_rect.right + 10, metric_y + 2))
            
            metric_y += 35
            
        # Today's scenario
        scenario_rect = pygame.Rect(50, 250, SCREEN_WIDTH - 100, 100)
        pygame.draw.rect(screen, (255, 255, 240), scenario_rect)
        pygame.draw.rect(screen, (200, 200, 180), scenario_rect, 3)
        
        scenario_title = self.font.render("Today's Situation:", True, (60, 60, 80))
        screen.blit(scenario_title, (scenario_rect.x + 20, scenario_rect.y + 10))
        
        # Scenario text
        scenario_lines = []
        words = self.current_event['text'].split()
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font.size(test_line)[0] < scenario_rect.width - 40:
                current_line.append(word)
            else:
                scenario_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            scenario_lines.append(' '.join(current_line))
            
        scenario_y = scenario_rect.y + 40
        for line in scenario_lines:
            line_surf = self.font.render(line, True, (40, 40, 60))
            screen.blit(line_surf, (scenario_rect.x + 20, scenario_y))
            scenario_y += 25
            
        # Functionality requirement indicator
        req_text = f"Functionality needed: {self.current_event['functionality_need']}%"
        req_color = (255, 50, 50) if self.functionality < self.current_event['functionality_need'] else (50, 255, 50)
        req_surf = self.small_font.render(req_text, True, req_color)
        screen.blit(req_surf, (scenario_rect.x + 20, scenario_rect.bottom - 25))
        
        # Decision options
        if not self.daily_choice_made:
            options_rect = pygame.Rect(50, 370, SCREEN_WIDTH - 100, 180)
            pygame.draw.rect(screen, (240, 255, 240), options_rect)
            pygame.draw.rect(screen, (100, 200, 100), options_rect, 3)
            
            options_title = self.font.render("Medication Decision:", True, (50, 100, 50))
            screen.blit(options_title, (options_rect.x + 20, options_rect.y + 10))
            
            # Options
            options = [
                (f"1 - Take full dose (1 pill)", self.pills_remaining >= 1),
                (f"2 - Take half dose (0.5 pill)", self.pills_remaining >= 0.5),
                (f"3 - Take quarter dose (0.25 pill)", self.pills_remaining >= 0.25),
                ("4 - Skip dose today", True)
            ]
            
            option_y = options_rect.y + 45
            for option_text, available in options:
                color = (50, 50, 60) if available else (180, 180, 190)
                option_surf = self.font.render(option_text, True, color)
                screen.blit(option_surf, (options_rect.x + 40, option_y))
                option_y += 30
                
            # Warning if pills are low
            if self.pills_remaining < 3:
                warning_text = f"⚠ WARNING: Only {self.pills_remaining:.1f} pills for {self.days_until_refill - self.current_day} days!"
                warning_surf = self.font.render(warning_text, True, (255, 50, 50))
                warning_rect = warning_surf.get_rect(center=(SCREEN_WIDTH // 2, options_rect.bottom - 20))
                screen.blit(warning_surf, warning_rect)
        else:
            # Show result of choice
            result_rect = pygame.Rect(100, 400, SCREEN_WIDTH - 200, 120)
            pygame.draw.rect(screen, (240, 240, 255), result_rect)
            pygame.draw.rect(screen, (180, 180, 200), result_rect, 3)
            
            result_text = "Day completed. Press SPACE to continue to tomorrow."
            result_surf = self.font.render(result_text, True, (60, 60, 80))
            result_rect_text = result_surf.get_rect(center=result_rect.center)
            screen.blit(result_surf, result_rect_text)
            
        # Visual pills scattered (artistic element)
        visible_pills = int(self.pills_remaining)
        for i in range(min(visible_pills, len(self.pill_positions))):
            x, y = self.pill_positions[i]
            # Pill shape
            pygame.draw.ellipse(screen, (255, 255, 255), (x - 12, y - 8, 24, 16))
            pygame.draw.ellipse(screen, (200, 200, 220), (x - 12, y - 8, 24, 16), 2)
            # Pill line
            pygame.draw.line(screen, (180, 180, 200), (x - 10, y), (x + 10, y), 2)
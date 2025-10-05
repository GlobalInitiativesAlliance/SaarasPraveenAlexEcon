"""Crisis Budgeting Game - Manage emergency expenses"""

import pygame
import random
from shared.constants import *

class CrisisBudgetingGame:
    """Manage limited funds during housing crisis"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Financial state
        self.current_money = 250.00  # Emergency assistance
        self.days_remaining = 7  # One week to stabilize
        self.current_day = 1
        
        # Needs
        self.needs = {
            'housing': {'paid': False, 'cost': 150, 'priority': 'critical'},
            'food': {'level': 70, 'daily_cost': 10},
            'phone': {'active': True, 'cost': 45, 'days_until_shutoff': 3},
            'transport': {'passes': 2, 'cost_per_pass': 5}
        }
        
        # Daily events
        self.current_choices = []
        self.selected_choice = 0
        self.outcome_message = ""
        self.outcome_timer = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
    def start(self):
        """Start the budgeting crisis"""
        self.active = True
        self.completed = False
        self.generate_daily_choices()
        
    def generate_daily_choices(self):
        """Generate choices for the current day"""
        self.current_choices = []
        
        # Always have basic options
        if self.current_money >= 10:
            self.current_choices.append({
                'text': 'Buy food for today ($10)',
                'cost': 10,
                'effect': lambda: self.buy_food()
            })
            
        if self.current_money >= 5 and self.needs['transport']['passes'] < 5:
            self.current_choices.append({
                'text': 'Buy bus pass ($5)',
                'cost': 5,
                'effect': lambda: self.buy_transport()
            })
            
        # Housing payment
        if not self.needs['housing']['paid'] and self.current_money >= 150:
            self.current_choices.append({
                'text': 'Pay deposit for shelter bed ($150)',
                'cost': 150,
                'effect': lambda: self.pay_housing()
            })
            
        # Phone bill
        if self.needs['phone']['days_until_shutoff'] <= 1 and self.current_money >= 45:
            self.current_choices.append({
                'text': 'Pay phone bill ($45)',
                'cost': 45,
                'effect': lambda: self.pay_phone()
            })
            
        # Skip eating option
        self.current_choices.append({
            'text': 'Skip meals today to save money',
            'cost': 0,
            'effect': lambda: self.skip_food()
        })
        
        # Random crisis events
        if self.current_day == 3:
            self.current_choices.insert(0, {
                'text': 'Medical emergency! Go to ER? ($0 now, bill later)',
                'cost': 0,
                'effect': lambda: self.medical_emergency()
            })
            
        self.selected_choice = 0
        
    def buy_food(self):
        """Buy food for the day"""
        self.current_money -= 10
        self.needs['food']['level'] = min(100, self.needs['food']['level'] + 30)
        self.outcome_message = "You eat a decent meal. Hunger satisfied."
        
    def buy_transport(self):
        """Buy transportation pass"""
        self.current_money -= 5
        self.needs['transport']['passes'] += 1
        self.outcome_message = "Bus pass purchased. You can get to work/appointments."
        
    def pay_housing(self):
        """Pay for housing"""
        self.current_money -= 150
        self.needs['housing']['paid'] = True
        self.outcome_message = "Shelter bed secured for the week!"
        
    def pay_phone(self):
        """Pay phone bill"""
        self.current_money -= 45
        self.needs['phone']['days_until_shutoff'] = 30
        self.outcome_message = "Phone service maintained. Critical for job search."
        
    def skip_food(self):
        """Skip eating to save money"""
        self.needs['food']['level'] = max(0, self.needs['food']['level'] - 25)
        self.outcome_message = "You go hungry but save money..."
        
    def medical_emergency(self):
        """Handle medical emergency"""
        self.outcome_message = "ER visit will result in $1200 bill. No choice."
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active or self.outcome_timer > 0:
            return
            
        if key == pygame.K_UP:
            self.selected_choice = max(0, self.selected_choice - 1)
        elif key == pygame.K_DOWN:
            self.selected_choice = min(len(self.current_choices) - 1, self.selected_choice + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.make_choice()
            
    def make_choice(self):
        """Execute the selected choice"""
        if 0 <= self.selected_choice < len(self.current_choices):
            choice = self.current_choices[self.selected_choice]
            if self.current_money >= choice['cost']:
                choice['effect']()
                self.outcome_timer = 2.0
                
    def advance_day(self):
        """Move to next day"""
        self.current_day += 1
        
        # Daily changes
        self.needs['food']['level'] = max(0, self.needs['food']['level'] - 15)
        self.needs['phone']['days_until_shutoff'] -= 1
        
        if self.needs['transport']['passes'] > 0:
            self.needs['transport']['passes'] -= 1
            
        if self.current_day > self.days_remaining:
            self.end_game()
        else:
            self.generate_daily_choices()
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        if self.outcome_timer > 0:
            self.outcome_timer -= dt
            if self.outcome_timer <= 0:
                self.advance_day()
                
    def end_game(self):
        """End the budgeting game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        success = self.needs['housing']['paid'] and self.current_money > 0
        return {
            'money': -50 if not success else 0,
            'stress': -20 if success else 20,
            'message': "Survived the week!" if success else "Ran out of money...",
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the budgeting interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((240, 240, 245))
        
        # Title
        title = f"CRISIS BUDGET - Day {self.current_day} of {self.days_remaining}"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Money display (prominent)
        money_rect = pygame.Rect(50, 70, 200, 60)
        pygame.draw.rect(screen, (100, 200, 100) if self.current_money > 50 else (255, 200, 100), money_rect)
        pygame.draw.rect(screen, (50, 100, 50), money_rect, 3)
        
        money_text = f"${self.current_money:.2f}"
        money_surf = self.title_font.render(money_text, True, (255, 255, 255))
        money_text_rect = money_surf.get_rect(center=money_rect.center)
        screen.blit(money_surf, money_text_rect)
        
        # Needs status
        needs_rect = pygame.Rect(300, 70, 450, 120)
        pygame.draw.rect(screen, (255, 255, 255), needs_rect)
        pygame.draw.rect(screen, (200, 200, 210), needs_rect, 2)
        
        needs_y = needs_rect.y + 10
        
        # Housing status
        housing_color = (100, 200, 100) if self.needs['housing']['paid'] else (255, 100, 100)
        housing_text = "✓ Housing Secured" if self.needs['housing']['paid'] else "✗ Need Housing ($150)"
        housing_surf = self.font.render(housing_text, True, housing_color)
        screen.blit(housing_surf, (needs_rect.x + 10, needs_y))
        
        # Food level
        needs_y += 30
        food_text = f"Food Level: {int(self.needs['food']['level'])}%"
        food_color = (255, 100, 100) if self.needs['food']['level'] < 30 else (255, 200, 100) if self.needs['food']['level'] < 60 else (100, 200, 100)
        food_surf = self.font.render(food_text, True, food_color)
        screen.blit(food_surf, (needs_rect.x + 10, needs_y))
        
        # Phone status
        needs_y += 30
        phone_text = f"Phone: {'Active' if self.needs['phone']['active'] else 'SHUT OFF'}"
        if self.needs['phone']['days_until_shutoff'] <= 2:
            phone_text += f" (Due in {self.needs['phone']['days_until_shutoff']} days!)"
        phone_color = (100, 200, 100) if self.needs['phone']['days_until_shutoff'] > 3 else (255, 100, 100)
        phone_surf = self.font.render(phone_text, True, phone_color)
        screen.blit(phone_surf, (needs_rect.x + 10, needs_y))
        
        # Transport
        needs_y += 30
        transport_text = f"Bus Passes: {self.needs['transport']['passes']}"
        transport_surf = self.font.render(transport_text, True, (100, 100, 120))
        screen.blit(transport_surf, (needs_rect.x + 10, needs_y))
        
        # Choices
        choices_rect = pygame.Rect(50, 220, SCREEN_WIDTH - 100, 300)
        pygame.draw.rect(screen, (250, 250, 255), choices_rect)
        pygame.draw.rect(screen, (200, 200, 220), choices_rect, 2)
        
        choices_title = self.font.render("Today's Decisions:", True, (50, 50, 80))
        screen.blit(choices_title, (choices_rect.x + 20, choices_rect.y + 10))
        
        # Draw choices
        choice_y = choices_rect.y + 50
        for i, choice in enumerate(self.current_choices):
            # Selection highlight
            if i == self.selected_choice:
                sel_rect = pygame.Rect(choices_rect.x + 10, choice_y - 5, choices_rect.width - 20, 40)
                pygame.draw.rect(screen, (220, 230, 255), sel_rect)
                
            # Choice text
            choice_color = (50, 50, 60) if i != self.selected_choice else (0, 0, 200)
            if choice['cost'] > self.current_money:
                choice_color = (180, 180, 190)  # Grayed out if can't afford
                
            choice_surf = self.font.render(choice['text'], True, choice_color)
            screen.blit(choice_surf, (choices_rect.x + 30, choice_y))
            
            choice_y += 45
            
        # Outcome message
        if self.outcome_timer > 0:
            outcome_rect = pygame.Rect(100, 540, SCREEN_WIDTH - 200, 60)
            pygame.draw.rect(screen, (255, 255, 200), outcome_rect)
            pygame.draw.rect(screen, (200, 200, 100), outcome_rect, 2)
            
            outcome_surf = self.font.render(self.outcome_message, True, (80, 80, 60))
            outcome_text_rect = outcome_surf.get_rect(center=outcome_rect.center)
            screen.blit(outcome_surf, outcome_text_rect)
        else:
            # Instructions
            inst_surf = self.small_font.render("↑↓ Select choice | ENTER Make decision", True, (120, 120, 140))
            inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            screen.blit(inst_surf, inst_rect)
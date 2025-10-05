"""Debt Juggling Game - Balance multiple debts and collectors"""

import pygame
import random
import math
from shared.constants import *

class DebtJugglingGame:
    """Juggle multiple debts while avoiding financial collapse"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game timing
        self.month = 1
        self.day_of_month = 1
        self.total_days = 0
        
        # Financial state
        self.current_money = 850.00  # Monthly income
        self.credit_score = 620
        
        # Debts with different priorities and consequences
        self.debts = {
            'rent': {
                'name': 'Rent',
                'amount': 450,
                'minimum': 450,  # Must pay in full
                'due_day': 1,
                'priority': 'critical',
                'paid_this_month': 0,
                'months_behind': 0,
                'consequence': 'eviction',
                'collector_aggression': 0
            },
            'credit_card': {
                'name': 'Credit Card',
                'amount': 1200,
                'minimum': 45,
                'due_day': 15,
                'priority': 'high',
                'paid_this_month': 0,
                'months_behind': 0,
                'consequence': 'credit_damage',
                'apr': 24.99,
                'collector_aggression': 0
            },
            'medical': {
                'name': 'Medical Bill',
                'amount': 2300,
                'minimum': 75,
                'due_day': 20,
                'priority': 'medium',
                'paid_this_month': 0,
                'months_behind': 0,
                'consequence': 'collections',
                'collector_aggression': 0
            },
            'payday_loan': {
                'name': 'Payday Loan',
                'amount': 300,
                'minimum': 375,  # Full plus fee
                'due_day': 10,
                'priority': 'urgent',
                'paid_this_month': 0,
                'months_behind': 0,
                'consequence': 'bank_levy',
                'apr': 400,
                'collector_aggression': 0
            },
            'utilities': {
                'name': 'Utilities',
                'amount': 120,
                'minimum': 120,
                'due_day': 25,
                'priority': 'high',
                'paid_this_month': 0,
                'months_behind': 0,
                'consequence': 'shutoff',
                'collector_aggression': 0
            }
        }
        
        # Daily expenses
        self.daily_expenses = 15  # Food, transport, etc.
        self.days_without_food = 0
        
        # Collector calls and harassment
        self.calls_today = []
        self.total_calls_received = 0
        self.work_performance = 100
        self.stress_level = 40
        
        # Visual elements
        self.debt_bubbles = []
        self.generate_debt_bubbles()
        self.call_notifications = []
        
        # Selected debt for payment
        self.selected_debt = 'rent'
        self.payment_amount = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 48)
        
    def generate_debt_bubbles(self):
        """Create visual representation of debts"""
        self.debt_bubbles = []
        angle_step = (2 * math.pi) / len(self.debts)
        
        for i, (debt_key, debt) in enumerate(self.debts.items()):
            angle = i * angle_step
            radius = 150
            x = SCREEN_WIDTH // 2 + math.cos(angle) * radius
            y = 250 + math.sin(angle) * radius
            
            self.debt_bubbles.append({
                'key': debt_key,
                'x': x,
                'y': y,
                'radius': 40 + (debt['amount'] / 100),  # Size based on amount
                'pulse': random.uniform(0, math.pi * 2)
            })
            
    def start(self):
        """Start the debt juggling game"""
        self.active = True
        self.completed = False
        self.month = 1
        self.day_of_month = 1
        self.check_daily_events()
        
    def check_daily_events(self):
        """Check what happens today"""
        self.calls_today = []
        
        # Check for due dates
        for debt_key, debt in self.debts.items():
            if self.day_of_month == debt['due_day']:
                if debt['paid_this_month'] < debt['minimum']:
                    # Payment due and not met
                    debt['months_behind'] += 1
                    debt['collector_aggression'] = min(100, debt['collector_aggression'] + 20)
                    
        # Generate collector calls based on aggression
        for debt_key, debt in self.debts.items():
            if debt['collector_aggression'] > 0:
                call_chance = debt['collector_aggression'] / 100
                if random.random() < call_chance:
                    self.generate_collector_call(debt_key, debt)
                    
    def generate_collector_call(self, debt_key, debt):
        """Generate a collector call"""
        call_scripts = {
            'friendly': [
                f"This is about your {debt['name']} balance of ${debt['amount']:.2f}.",
                "We'd like to help you set up a payment plan.",
                "Please call us back at your earliest convenience."
            ],
            'firm': [
                f"You are {debt['months_behind']} months behind on your {debt['name']}.",
                "We need payment immediately to avoid further action.",
                "This is an attempt to collect a debt."
            ],
            'aggressive': [
                f"FINAL NOTICE: Your {debt['name']} will be sent to legal!",
                "We WILL garnish your wages!",
                "You cannot ignore this debt forever!"
            ]
        }
        
        # Determine tone based on months behind
        if debt['months_behind'] <= 1:
            tone = 'friendly'
        elif debt['months_behind'] <= 3:
            tone = 'firm'
        else:
            tone = 'aggressive'
            
        script = random.choice(call_scripts[tone])
        
        self.calls_today.append({
            'debt': debt['name'],
            'message': script,
            'tone': tone,
            'time_remaining': 5.0
        })
        
        self.total_calls_received += 1
        
        # Add visual notification
        self.call_notifications.append({
            'x': random.randint(100, SCREEN_WIDTH - 300),
            'y': random.randint(100, 300),
            'text': f"CALL: {debt['name']} Collector",
            'life': 120
        })
        
        # Impact work if during work hours
        if 9 <= (self.total_days % 24) <= 17:
            self.work_performance = max(0, self.work_performance - 5)
            
        # Increase stress
        self.stress_level = min(100, self.stress_level + 10)
        
    def make_payment(self, debt_key, amount):
        """Make a payment on a debt"""
        if debt_key not in self.debts or amount > self.current_money:
            return False
            
        debt = self.debts[debt_key]
        self.current_money -= amount
        debt['paid_this_month'] += amount
        debt['amount'] = max(0, debt['amount'] - amount)
        
        # Reduce collector aggression
        if amount >= debt['minimum']:
            debt['collector_aggression'] = max(0, debt['collector_aggression'] - 30)
            debt['months_behind'] = max(0, debt['months_behind'] - 1)
        else:
            debt['collector_aggression'] = max(0, debt['collector_aggression'] - 10)
            
        return True
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        # Debt selection
        debt_keys = list(self.debts.keys())
        current_index = debt_keys.index(self.selected_debt)
        
        if key == pygame.K_LEFT:
            current_index = (current_index - 1) % len(debt_keys)
            self.selected_debt = debt_keys[current_index]
        elif key == pygame.K_RIGHT:
            current_index = (current_index + 1) % len(debt_keys)
            self.selected_debt = debt_keys[current_index]
        elif key == pygame.K_UP:
            # Increase payment amount
            self.payment_amount = min(self.current_money, self.payment_amount + 10)
        elif key == pygame.K_DOWN:
            # Decrease payment amount
            self.payment_amount = max(0, self.payment_amount - 10)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Make payment
            if self.payment_amount > 0:
                self.make_payment(self.selected_debt, self.payment_amount)
                self.payment_amount = 0
        elif key == pygame.K_n:
            # Next day
            self.advance_day()
            
    def advance_day(self):
        """Move to next day"""
        self.day_of_month += 1
        self.total_days += 1
        
        # Daily expenses
        if self.current_money >= self.daily_expenses:
            self.current_money -= self.daily_expenses
        else:
            self.days_without_food += 1
            self.stress_level = min(100, self.stress_level + 5)
            
        # End of month
        if self.day_of_month > 30:
            self.day_of_month = 1
            self.month += 1
            
            # Get paid
            self.current_money += 850 * (self.work_performance / 100)
            
            # Reset monthly payments
            for debt in self.debts.values():
                debt['paid_this_month'] = 0
                
            # Apply interest
            if 'apr' in self.debts['credit_card']:
                monthly_rate = self.debts['credit_card']['apr'] / 12 / 100
                self.debts['credit_card']['amount'] *= (1 + monthly_rate)
                
            if 'apr' in self.debts['payday_loan']:
                # Payday loans compound differently
                self.debts['payday_loan']['amount'] *= 1.15  # 15% every month!
                
        # Check daily events
        self.check_daily_events()
        
        # Check end conditions
        if self.month > 6:
            self.end_game()
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update debt bubble animations
        for bubble in self.debt_bubbles:
            bubble['pulse'] += dt * 2
            
        # Update call notifications
        for notif in self.call_notifications[:]:
            notif['life'] -= 1
            notif['y'] -= 0.5
            if notif['life'] <= 0:
                self.call_notifications.remove(notif)
                
        # Update active calls
        for call in self.calls_today[:]:
            call['time_remaining'] -= dt
            if call['time_remaining'] <= 0:
                self.calls_today.remove(call)
                
    def end_game(self):
        """End the debt juggling game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate outcome
        total_debt = sum(debt['amount'] for debt in self.debts.values())
        credit_damage = 580 - self.credit_score
        
        if self.debts['rent']['months_behind'] >= 3:
            message = "Evicted. Lost housing due to unpaid rent."
            success = False
        elif self.work_performance < 50:
            message = "Lost job due to collector harassment."
            success = False
        elif total_debt > 5000:
            message = f"Debt spiral out of control: ${total_debt:.2f}"
            success = False
        else:
            message = f"Survived 6 months. Debt remaining: ${total_debt:.2f}"
            success = True
            
        return {
            'money': -abs(credit_damage * 2),  # Rough financial impact
            'stress': 50 if not success else 30,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the debt juggling interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((240, 240, 245))
        
        # Draw call notifications in background
        for notif in self.call_notifications:
            alpha = int(255 * notif['life'] / 120)
            notif_surf = self.small_font.render(notif['text'], True, (255, 100, 100))
            notif_surf.set_alpha(alpha)
            screen.blit(notif_surf, (notif['x'], notif['y']))
            
        # Title
        title = f"DEBT JUGGLING - Month {self.month}, Day {self.day_of_month}"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Financial status
        status_rect = pygame.Rect(50, 70, 200, 150)
        pygame.draw.rect(screen, (255, 255, 255), status_rect)
        pygame.draw.rect(screen, (180, 180, 200), status_rect, 2)
        
        # Money display
        money_color = (100, 200, 100) if self.current_money > 200 else (255, 200, 100) if self.current_money > 50 else (255, 100, 100)
        money_text = f"${self.current_money:.2f}"
        money_surf = self.big_font.render(money_text, True, money_color)
        money_rect = money_surf.get_rect(center=(status_rect.centerx, status_rect.y + 35))
        screen.blit(money_surf, money_rect)
        
        # Other stats
        stats_y = status_rect.y + 70
        stats = [
            (f"Credit: {self.credit_score}", self.credit_score > 600),
            (f"Work: {int(self.work_performance)}%", self.work_performance > 70),
            (f"Stress: {int(self.stress_level)}%", self.stress_level < 70)
        ]
        
        for stat_text, is_good in stats:
            color = (100, 200, 100) if is_good else (255, 100, 100)
            stat_surf = self.small_font.render(stat_text, True, color)
            screen.blit(stat_surf, (status_rect.x + 10, stats_y))
            stats_y += 25
            
        # Debt bubbles visualization
        for bubble in self.debt_bubbles:
            debt = self.debts[bubble['key']]
            
            # Bubble size pulses based on urgency
            pulse_size = math.sin(bubble['pulse']) * 5
            radius = bubble['radius'] + pulse_size
            
            # Color based on status
            if debt['months_behind'] >= 3:
                color = (255, 50, 50)
            elif debt['months_behind'] >= 1:
                color = (255, 150, 50)
            elif debt['paid_this_month'] >= debt['minimum']:
                color = (50, 255, 50)
            else:
                color = (200, 200, 100)
                
            # Draw bubble
            pygame.draw.circle(screen, color, (int(bubble['x']), int(bubble['y'])), int(radius))
            
            # Selected highlight
            if bubble['key'] == self.selected_debt:
                pygame.draw.circle(screen, (255, 255, 255), (int(bubble['x']), int(bubble['y'])), int(radius + 5), 3)
                
            # Debt name
            name_surf = self.small_font.render(debt['name'], True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(bubble['x'], bubble['y'] - 10))
            screen.blit(name_surf, name_rect)
            
            # Amount
            amount_text = f"${debt['amount']:.0f}"
            amount_surf = self.font.render(amount_text, True, (255, 255, 255))
            amount_rect = amount_surf.get_rect(center=(bubble['x'], bubble['y'] + 10))
            screen.blit(amount_surf, amount_rect)
            
        # Selected debt details
        selected_debt = self.debts[self.selected_debt]
        detail_rect = pygame.Rect(300, 70, 450, 150)
        pygame.draw.rect(screen, (250, 250, 255), detail_rect)
        pygame.draw.rect(screen, (150, 150, 200), detail_rect, 3)
        
        detail_title = self.font.render(selected_debt['name'].upper(), True, (50, 50, 100))
        screen.blit(detail_title, (detail_rect.x + 20, detail_rect.y + 10))
        
        detail_y = detail_rect.y + 40
        details = [
            f"Balance: ${selected_debt['amount']:.2f}",
            f"Minimum payment: ${selected_debt['minimum']:.2f}",
            f"Due day: {selected_debt['due_day']}th",
            f"Paid this month: ${selected_debt['paid_this_month']:.2f}",
            f"Months behind: {selected_debt['months_behind']}"
        ]
        
        for detail in details:
            detail_surf = self.small_font.render(detail, True, (60, 60, 80))
            screen.blit(detail_surf, (detail_rect.x + 20, detail_y))
            detail_y += 22
            
        # Payment interface
        payment_rect = pygame.Rect(50, 400, 400, 100)
        pygame.draw.rect(screen, (240, 255, 240), payment_rect)
        pygame.draw.rect(screen, (100, 200, 100), payment_rect, 2)
        
        payment_title = self.font.render("Make Payment", True, (50, 100, 50))
        screen.blit(payment_title, (payment_rect.x + 10, payment_rect.y + 10))
        
        payment_text = f"Amount: ${self.payment_amount:.2f}"
        payment_surf = self.font.render(payment_text, True, (50, 50, 60))
        screen.blit(payment_surf, (payment_rect.x + 20, payment_rect.y + 40))
        
        # Payment slider visual
        slider_rect = pygame.Rect(payment_rect.x + 20, payment_rect.y + 70, 360, 10)
        pygame.draw.rect(screen, (200, 200, 210), slider_rect)
        if self.current_money > 0:
            slider_fill = pygame.Rect(slider_rect.x, slider_rect.y, 
                                    int(slider_rect.width * self.payment_amount / self.current_money), 10)
            pygame.draw.rect(screen, (100, 200, 100), slider_fill)
            
        # Active calls display
        if self.calls_today:
            call_rect = pygame.Rect(480, 400, 270, 150)
            pygame.draw.rect(screen, (255, 240, 240), call_rect)
            pygame.draw.rect(screen, (255, 100, 100), call_rect, 3)
            
            call_title = self.font.render("INCOMING CALL!", True, (200, 50, 50))
            screen.blit(call_title, (call_rect.x + 10, call_rect.y + 10))
            
            current_call = self.calls_today[0]
            call_from = self.small_font.render(f"From: {current_call['debt']}", True, (150, 50, 50))
            screen.blit(call_from, (call_rect.x + 10, call_rect.y + 40))
            
            # Message with word wrap
            message_lines = self.wrap_text(current_call['message'], call_rect.width - 20)
            message_y = call_rect.y + 65
            for line in message_lines:
                line_surf = self.small_font.render(line, True, (100, 50, 50))
                screen.blit(line_surf, (call_rect.x + 10, message_y))
                message_y += 20
                
        # Instructions
        inst_lines = [
            "←→ Select debt | ↑↓ Adjust payment | ENTER Pay | N Next day"
        ]
        inst_y = SCREEN_HEIGHT - 40
        for line in inst_lines:
            inst_surf = self.small_font.render(line, True, (100, 100, 120))
            inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect)
            inst_y += 20
            
    def wrap_text(self, text, max_width):
        """Wrap text to fit within width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.small_font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
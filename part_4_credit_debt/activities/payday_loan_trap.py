"""Payday Loan Trap Game - Experience the debt spiral"""

import pygame
import random
import math
from shared.constants import *

class PaydayLoanTrap:
    """Experience the payday loan debt spiral"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Financial state
        self.current_money = 20.00
        self.bills_due = 450.00
        self.payday_in_days = 12
        self.current_day = 1
        
        # Loan details
        self.loan_amount = 0
        self.loan_fee = 0
        self.loan_due_date = 0
        self.total_fees_paid = 0
        self.loans_taken = 0
        self.current_apr = 0
        
        # Life expenses tracking
        self.daily_needs = {
            'food': 15,
            'transport': 5,
            'phone': 2
        }
        self.days_without_food = 0
        self.missed_work_days = 0
        
        # Stress and consequences
        self.stress_level = 50
        self.credit_score = 580  # Already low
        self.employer_warnings = 0
        
        # Visual elements
        self.money_particles = []
        self.warning_flash = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 48)
        
        # Lender options (predatory)
        self.lenders = [
            {
                'name': 'QuickCash Express',
                'fee_per_100': 25,  # $25 per $100 borrowed
                'term_days': 14,
                'max_loan': 500,
                'marketing': 'Get cash in minutes!'
            },
            {
                'name': 'PayDay Advance Plus',
                'fee_per_100': 30,
                'term_days': 14,
                'max_loan': 300,
                'marketing': 'No credit check required!'
            },
            {
                'name': 'Emergency Money Now',
                'fee_per_100': 35,
                'term_days': 7,
                'max_loan': 400,
                'marketing': 'Bad credit? No problem!'
            }
        ]
        
        self.selected_lender = 0
        self.loan_amount_selected = 100
        self.current_screen = 'main'  # 'main', 'lender', 'repay'
        
    def start(self):
        """Start the payday loan trap"""
        self.active = True
        self.completed = False
        self.current_day = 1
        self.generate_daily_situation()
        
    def generate_daily_situation(self):
        """Generate daily financial pressures"""
        # Random emergencies
        if random.random() < 0.15:
            emergencies = [
                ('Car broke down - need $200 for repairs', 200),
                ('Medical copay required - $75', 75),
                ('Landlord demanding late fee - $50', 50),
                ('Phone about to be shut off - $45', 45)
            ]
            self.current_emergency = random.choice(emergencies)
        else:
            self.current_emergency = None
            
    def calculate_apr(self, fee, amount, days):
        """Calculate APR for display"""
        if amount == 0 or days == 0:
            return 0
        rate = fee / amount
        annual_rate = (rate * 365 / days) * 100
        return int(annual_rate)
        
    def take_loan(self):
        """Process taking out a payday loan"""
        if self.selected_lender >= len(self.lenders):
            return
            
        lender = self.lenders[self.selected_lender]
        
        # Calculate loan details
        self.loan_amount = self.loan_amount_selected
        self.loan_fee = (self.loan_amount / 100) * lender['fee_per_100']
        self.loan_due_date = self.current_day + lender['term_days']
        
        # Give money (minus fee if paid upfront)
        self.current_money += self.loan_amount
        
        # Track stats
        self.loans_taken += 1
        self.current_apr = self.calculate_apr(self.loan_fee, self.loan_amount, lender['term_days'])
        
        # Add stress
        self.stress_level = min(100, self.stress_level + 15)
        
        # Create money particle effect
        for _ in range(20):
            self.money_particles.append({
                'x': SCREEN_WIDTH // 2,
                'y': 300,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -2),
                'life': 60
            })
            
        self.current_screen = 'main'
        
    def pay_loan(self):
        """Attempt to pay off loan"""
        total_due = self.loan_amount + self.loan_fee
        
        if self.current_money >= total_due:
            # Can pay in full
            self.current_money -= total_due
            self.total_fees_paid += self.loan_fee
            self.loan_amount = 0
            self.loan_fee = 0
            self.stress_level = max(0, self.stress_level - 10)
        else:
            # Can't pay - rollover or default
            self.warning_flash = 30
            
    def rollover_loan(self):
        """Pay fee to extend loan"""
        if self.current_money >= self.loan_fee:
            self.current_money -= self.loan_fee
            self.total_fees_paid += self.loan_fee
            self.loan_due_date = self.current_day + 14
            # Stress increases with rollover
            self.stress_level = min(100, self.stress_level + 20)
        else:
            # Can't even pay the fee
            self.credit_score = max(300, self.credit_score - 50)
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if self.current_screen == 'main':
            if key == pygame.K_1:
                # Go to lender selection
                self.current_screen = 'lender'
            elif key == pygame.K_2 and self.loan_amount > 0:
                # Try to pay loan
                self.pay_loan()
            elif key == pygame.K_3 and self.loan_amount > 0:
                # Rollover loan
                self.rollover_loan()
            elif key == pygame.K_4:
                # Skip to next day
                self.advance_day()
                
        elif self.current_screen == 'lender':
            if key == pygame.K_UP:
                self.selected_lender = max(0, self.selected_lender - 1)
            elif key == pygame.K_DOWN:
                self.selected_lender = min(len(self.lenders) - 1, self.selected_lender + 1)
            elif key == pygame.K_LEFT:
                self.loan_amount_selected = max(100, self.loan_amount_selected - 50)
            elif key == pygame.K_RIGHT:
                lender = self.lenders[self.selected_lender]
                self.loan_amount_selected = min(lender['max_loan'], self.loan_amount_selected + 50)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.take_loan()
            elif key == pygame.K_ESCAPE:
                self.current_screen = 'main'
                
    def advance_day(self):
        """Move to next day"""
        self.current_day += 1
        
        # Daily expenses
        daily_cost = sum(self.daily_needs.values())
        if self.current_money >= daily_cost:
            self.current_money -= daily_cost
        else:
            # Can't afford basic needs
            if self.current_money < self.daily_needs['food']:
                self.days_without_food += 1
            if self.current_money < self.daily_needs['transport']:
                self.missed_work_days += 1
                self.employer_warnings += 1
                
        # Check if payday
        self.payday_in_days -= 1
        if self.payday_in_days <= 0:
            # Payday! But...
            paycheck = 450
            if self.missed_work_days > 2:
                paycheck *= 0.7  # Reduced pay
            self.current_money += paycheck
            self.payday_in_days = 14
            self.missed_work_days = 0
            
        # Check loan due
        if self.loan_amount > 0 and self.current_day >= self.loan_due_date:
            self.warning_flash = 60
            
        # Generate new daily situation
        self.generate_daily_situation()
        
        # Check end conditions
        if self.current_day > 30:
            self.end_game()
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update particles
        for particle in self.money_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3  # Gravity
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.money_particles.remove(particle)
                
        # Update warning flash
        if self.warning_flash > 0:
            self.warning_flash -= 1
            
    def end_game(self):
        """End the payday loan game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate outcome
        debt_spiral = self.loans_taken > 3
        fees_excessive = self.total_fees_paid > self.loan_amount
        
        if debt_spiral:
            message = f"Trapped in debt spiral. Total fees paid: ${self.total_fees_paid:.2f}"
        else:
            message = f"Survived the month. Fees paid: ${self.total_fees_paid:.2f}"
            
        return {
            'money': -self.total_fees_paid,
            'stress': 40 if debt_spiral else 20,
            'message': message,
            'color': (255, 100, 100) if debt_spiral else (255, 200, 100)
        }
        
    def draw(self, screen):
        """Draw the payday loan interface"""
        if not self.active:
            return
            
        # Background with subtle gradient
        for y in range(SCREEN_HEIGHT):
            darkness = min(50, int(y / SCREEN_HEIGHT * 30))
            color = (240 - darkness, 240 - darkness, 245 - darkness)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
            
        # Warning flash overlay
        if self.warning_flash > 0 and self.warning_flash % 10 < 5:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(50)
            overlay.fill((255, 50, 50))
            screen.blit(overlay, (0, 0))
            
        # Title
        title = f"PAYDAY LOAN SPIRAL - Day {self.current_day}"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        if self.current_screen == 'main':
            self.draw_main_screen(screen)
        elif self.current_screen == 'lender':
            self.draw_lender_screen(screen)
            
        # Draw particles
        for particle in self.money_particles:
            alpha = int(255 * particle['life'] / 60)
            color = (100, 200, 100)
            pygame.draw.circle(screen, color, 
                             (int(particle['x']), int(particle['y'])), 
                             3)
            
    def draw_main_screen(self, screen):
        """Draw main game screen"""
        # Financial status panel
        status_rect = pygame.Rect(50, 80, 300, 200)
        pygame.draw.rect(screen, (255, 255, 255), status_rect)
        pygame.draw.rect(screen, (200, 200, 210), status_rect, 2)
        
        # Current money (big display)
        money_color = (100, 200, 100) if self.current_money > 50 else (255, 200, 100) if self.current_money > 10 else (255, 100, 100)
        money_text = f"${self.current_money:.2f}"
        money_surf = self.big_font.render(money_text, True, money_color)
        money_rect = money_surf.get_rect(center=(status_rect.centerx, status_rect.y + 40))
        screen.blit(money_surf, money_rect)
        
        # Status details
        status_y = status_rect.y + 80
        status_items = [
            (f"Bills due: ${self.bills_due:.2f}", (255, 100, 100)),
            (f"Payday in: {self.payday_in_days} days", (100, 150, 255)),
            (f"Credit score: {self.credit_score}", (255, 200, 100) if self.credit_score > 500 else (255, 100, 100))
        ]
        
        for text, color in status_items:
            surf = self.font.render(text, True, color)
            screen.blit(surf, (status_rect.x + 20, status_y))
            status_y += 30
            
        # Current loan panel
        loan_rect = pygame.Rect(400, 80, 350, 200)
        if self.loan_amount > 0:
            pygame.draw.rect(screen, (255, 240, 240), loan_rect)
            pygame.draw.rect(screen, (200, 100, 100), loan_rect, 3)
            
            loan_title = self.font.render("CURRENT LOAN", True, (150, 50, 50))
            screen.blit(loan_title, (loan_rect.x + 20, loan_rect.y + 10))
            
            loan_details_y = loan_rect.y + 45
            loan_details = [
                f"Amount borrowed: ${self.loan_amount:.2f}",
                f"Fee: ${self.loan_fee:.2f}",
                f"Total due: ${self.loan_amount + self.loan_fee:.2f}",
                f"Due in: {max(0, self.loan_due_date - self.current_day)} days",
                f"APR: {self.current_apr}%"
            ]
            
            for detail in loan_details:
                detail_surf = self.font.render(detail, True, (80, 40, 40))
                screen.blit(detail_surf, (loan_rect.x + 20, loan_details_y))
                loan_details_y += 28
                
            # Due date warning
            if self.loan_due_date - self.current_day <= 2:
                warning_text = "⚠ PAYMENT DUE SOON!"
                warning_surf = self.font.render(warning_text, True, (255, 50, 50))
                warning_rect = warning_surf.get_rect(center=(loan_rect.centerx, loan_rect.bottom - 20))
                if pygame.time.get_ticks() % 1000 < 500:
                    screen.blit(warning_surf, warning_rect)
        else:
            pygame.draw.rect(screen, (240, 255, 240), loan_rect)
            pygame.draw.rect(screen, (100, 200, 100), loan_rect, 2)
            
            no_loan_text = "No active loan"
            no_loan_surf = self.font.render(no_loan_text, True, (100, 150, 100))
            no_loan_rect = no_loan_surf.get_rect(center=loan_rect.center)
            screen.blit(no_loan_surf, no_loan_rect)
            
        # Daily needs tracker
        needs_rect = pygame.Rect(50, 300, 300, 120)
        pygame.draw.rect(screen, (255, 255, 255), needs_rect)
        pygame.draw.rect(screen, (200, 200, 210), needs_rect, 2)
        
        needs_title = self.font.render("Daily Needs", True, (60, 60, 80))
        screen.blit(needs_title, (needs_rect.x + 10, needs_rect.y + 10))
        
        needs_y = needs_rect.y + 40
        for need, cost in self.daily_needs.items():
            need_text = f"{need.capitalize()}: ${cost}/day"
            can_afford = self.current_money >= cost
            need_color = (100, 200, 100) if can_afford else (255, 100, 100)
            need_surf = self.small_font.render(need_text, True, need_color)
            screen.blit(need_surf, (needs_rect.x + 20, needs_y))
            needs_y += 25
            
        # Emergency notification
        if self.current_emergency:
            emergency_rect = pygame.Rect(400, 300, 350, 120)
            pygame.draw.rect(screen, (255, 240, 200), emergency_rect)
            pygame.draw.rect(screen, (255, 150, 50), emergency_rect, 3)
            
            emergency_title = self.font.render("EMERGENCY!", True, (200, 50, 50))
            screen.blit(emergency_title, (emergency_rect.x + 20, emergency_rect.y + 10))
            
            emerg_text, emerg_cost = self.current_emergency
            text_lines = self.wrap_text(emerg_text, emergency_rect.width - 40)
            text_y = emergency_rect.y + 45
            for line in text_lines:
                line_surf = self.font.render(line, True, (100, 50, 50))
                screen.blit(line_surf, (emergency_rect.x + 20, text_y))
                text_y += 25
                
        # Options
        options_rect = pygame.Rect(50, 450, SCREEN_WIDTH - 100, 120)
        pygame.draw.rect(screen, (240, 240, 250), options_rect)
        pygame.draw.rect(screen, (180, 180, 200), options_rect, 2)
        
        options_title = self.font.render("Options:", True, (60, 60, 80))
        screen.blit(options_title, (options_rect.x + 20, options_rect.y + 10))
        
        options = [
            "1 - Take out payday loan",
            f"2 - Pay current loan (${self.loan_amount + self.loan_fee:.2f})" if self.loan_amount > 0 else "2 - (No loan to pay)",
            f"3 - Rollover loan (pay ${self.loan_fee:.2f} fee)" if self.loan_amount > 0 else "3 - (No loan to rollover)",
            "4 - Try to survive another day"
        ]
        
        option_y = options_rect.y + 40
        for option in options:
            option_surf = self.font.render(option, True, (50, 50, 60))
            screen.blit(option_surf, (options_rect.x + 30, option_y))
            option_y += 25
            
    def draw_lender_screen(self, screen):
        """Draw lender selection screen"""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Lender selection window
        window_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        pygame.draw.rect(screen, (250, 250, 255), window_rect)
        pygame.draw.rect(screen, (100, 100, 150), window_rect, 4)
        
        # Title
        lender_title = "SELECT PAYDAY LENDER"
        lender_surf = self.title_font.render(lender_title, True, (50, 50, 80))
        lender_rect = lender_surf.get_rect(center=(window_rect.centerx, window_rect.y + 30))
        screen.blit(lender_surf, lender_rect)
        
        # Lender options
        lender_y = window_rect.y + 80
        for i, lender in enumerate(self.lenders):
            # Highlight selected
            if i == self.selected_lender:
                sel_rect = pygame.Rect(window_rect.x + 20, lender_y - 5, window_rect.width - 40, 100)
                pygame.draw.rect(screen, (220, 230, 255), sel_rect)
                pygame.draw.rect(screen, (100, 120, 200), sel_rect, 2)
                
            # Lender name
            name_surf = self.font.render(lender['name'], True, (50, 50, 100))
            screen.blit(name_surf, (window_rect.x + 40, lender_y))
            
            # Marketing text
            market_surf = self.small_font.render(f'"{lender["marketing"]}"', True, (100, 100, 150))
            screen.blit(market_surf, (window_rect.x + 40, lender_y + 25))
            
            # Terms
            terms_text = f"Fee: ${lender['fee_per_100']} per $100 | Term: {lender['term_days']} days | Max: ${lender['max_loan']}"
            terms_surf = self.small_font.render(terms_text, True, (80, 80, 100))
            screen.blit(terms_surf, (window_rect.x + 40, lender_y + 50))
            
            # APR calculation for selected amount
            if i == self.selected_lender:
                fee = (self.loan_amount_selected / 100) * lender['fee_per_100']
                apr = self.calculate_apr(fee, self.loan_amount_selected, lender['term_days'])
                apr_text = f"Borrowing ${self.loan_amount_selected} = ${fee:.2f} fee | {apr}% APR"
                apr_surf = self.font.render(apr_text, True, (200, 50, 50))
                screen.blit(apr_surf, (window_rect.x + 40, lender_y + 75))
                
            lender_y += 120
            
        # Amount selector
        amount_rect = pygame.Rect(window_rect.x + 50, window_rect.bottom - 120, window_rect.width - 100, 60)
        pygame.draw.rect(screen, (255, 255, 255), amount_rect)
        pygame.draw.rect(screen, (150, 150, 170), amount_rect, 2)
        
        amount_text = f"Loan Amount: ${self.loan_amount_selected}"
        amount_surf = self.font.render(amount_text, True, (50, 50, 60))
        amount_text_rect = amount_surf.get_rect(center=(amount_rect.centerx, amount_rect.y + 15))
        screen.blit(amount_surf, amount_text_rect)
        
        # Instructions
        inst_text = "↑↓ Select lender | ←→ Adjust amount | ENTER Take loan | ESC Cancel"
        inst_surf = self.small_font.render(inst_text, True, (100, 100, 120))
        inst_rect = inst_surf.get_rect(center=(amount_rect.centerx, amount_rect.y + 40))
        screen.blit(inst_surf, inst_rect)
        
    def wrap_text(self, text, max_width):
        """Wrap text to fit within width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
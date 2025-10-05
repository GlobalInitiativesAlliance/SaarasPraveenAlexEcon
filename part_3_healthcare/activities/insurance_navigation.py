"""Insurance Navigation Game - Navigate complex healthcare bureaucracy"""

import pygame
import random
from shared.constants import *

class InsuranceNavigationGame:
    """Navigate insurance forms, denials, and appeals"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.current_step = 0
        self.total_steps = 8
        self.forms_completed = []
        self.denials_received = 0
        self.appeals_filed = 0
        self.time_spent_hours = 0
        self.phone_hold_time = 0
        
        # Player resources
        self.patience = 100
        self.understanding = 30  # Of the system
        self.documentation = []
        
        # Current task
        self.current_task = None
        self.task_options = []
        self.selected_option = 0
        
        # Phone maze state
        self.phone_menu_level = 0
        self.correct_path = []
        self.current_path = []
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Insurance maze steps
        self.maze_steps = [
            {
                'title': 'Initial Claim Submission',
                'description': 'Submit claim for recent ER visit ($3,200)',
                'options': [
                    ('Submit online (may get lost)', 'online', 0.6),
                    ('Mail certified (costs $8)', 'mail', 0.8),
                    ('Fax to number on card', 'fax', 0.4)
                ]
            },
            {
                'title': 'First Denial - Not Medically Necessary',
                'description': 'Your ER visit was denied as "not an emergency"',
                'options': [
                    ('Give up and pay yourself', 'give_up', 0.0),
                    ('File an appeal', 'appeal', 0.5),
                    ('Get doctor to write letter', 'doctor_letter', 0.7)
                ]
            },
            {
                'title': 'Phone Navigation Hell',
                'description': 'Call insurance to check appeal status',
                'options': [
                    ('Press 1 for English', 'menu_1', 1.0),
                    ('Press 2 for Spanish', 'menu_2', 0.0),
                    ('Press 0 for operator', 'menu_0', 0.1)
                ]
            },
            {
                'title': 'Prior Authorization Required',
                'description': 'Need pre-approval for medication',
                'options': [
                    ('Have doctor submit PA form', 'doctor_pa', 0.6),
                    ('Try to do it yourself', 'self_pa', 0.2),
                    ('Pay out of pocket ($400/month)', 'pay_self', 1.0)
                ]
            },
            {
                'title': 'In-Network vs Out-of-Network',
                'description': 'Find a specialist that takes your insurance',
                'options': [
                    ('Use insurance website (often wrong)', 'website', 0.3),
                    ('Call each doctor individually', 'call_doctors', 0.8),
                    ('Go to out-of-network doctor', 'out_network', 1.0)
                ]
            },
            {
                'title': 'EOB Confusion',
                'description': 'Received 5 different bills for same visit',
                'options': [
                    ('Pay all of them', 'pay_all', 0.0),
                    ('Call each provider', 'call_providers', 0.6),
                    ('Wait for final bill', 'wait', 0.4)
                ]
            },
            {
                'title': 'Appeal Deadline',
                'description': 'You have 72 hours to appeal latest denial',
                'options': [
                    ('Rush to gather documents', 'rush_docs', 0.7),
                    ('Miss deadline', 'miss_deadline', 0.0),
                    ('Hire patient advocate ($200)', 'advocate', 0.9)
                ]
            },
            {
                'title': 'Final Resolution',
                'description': 'After 6 months of fighting...',
                'options': [
                    ('Continue fighting', 'continue', 0.5),
                    ('Negotiate payment plan', 'payment_plan', 0.8),
                    ('Let it go to collections', 'collections', 0.0)
                ]
            }
        ]
        
    def start(self):
        """Start the insurance navigation"""
        self.active = True
        self.completed = False
        self.current_step = 0
        self.load_current_task()
        
    def load_current_task(self):
        """Load the current maze step"""
        if self.current_step < len(self.maze_steps):
            self.current_task = self.maze_steps[self.current_step]
            self.task_options = self.current_task['options']
            self.selected_option = 0
            
            # Special handling for phone menu
            if 'Phone Navigation' in self.current_task['title']:
                self.phone_menu_level = 0
                self.generate_phone_maze()
                
    def generate_phone_maze(self):
        """Generate a complex phone menu tree"""
        self.phone_menus = [
            {
                'prompt': 'For claims, press 1. For benefits, press 2. For providers, press 3.',
                'correct': 1
            },
            {
                'prompt': 'For claim status, press 1. For new claim, press 2. For appeals, press 3.',
                'correct': 3
            },
            {
                'prompt': 'For medical appeals, press 1. For pharmacy appeals, press 2.',
                'correct': 1
            },
            {
                'prompt': 'Enter your member ID followed by pound.',
                'correct': '#'
            },
            {
                'prompt': 'Enter your date of birth as MMDDYYYY.',
                'correct': 'DOB'
            },
            {
                'prompt': 'Please hold for the next available representative...',
                'correct': 'WAIT'
            }
        ]
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if self.phone_menu_level > 0:
            # Handle phone menu navigation
            self.handle_phone_menu(key)
        else:
            # Regular option selection
            if key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif key == pygame.K_DOWN:
                self.selected_option = min(len(self.task_options) - 1, self.selected_option + 1)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.select_option()
                
    def handle_phone_menu(self, key):
        """Handle phone menu navigation"""
        if self.phone_menu_level >= len(self.phone_menus):
            # Completed phone maze
            self.phone_hold_time = random.randint(45, 120)
            self.time_spent_hours += self.phone_hold_time / 60
            self.patience = max(0, self.patience - 30)
            self.advance_step()
            return
            
        current_menu = self.phone_menus[self.phone_menu_level]
        
        if current_menu['correct'] == 'WAIT':
            # Just waiting
            if key == pygame.K_SPACE:
                self.phone_menu_level += 1
        elif current_menu['correct'] == '#':
            # Need to press pound
            if key == pygame.K_HASH or key == pygame.K_3 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.phone_menu_level += 1
        elif current_menu['correct'] == 'DOB':
            # Any 8 digits
            if pygame.K_0 <= key <= pygame.K_9:
                self.phone_menu_level += 1
        else:
            # Numeric choice
            if pygame.K_1 <= key <= pygame.K_9:
                choice = key - pygame.K_0
                if choice == current_menu['correct']:
                    self.phone_menu_level += 1
                else:
                    # Wrong choice, start over
                    self.phone_menu_level = 0
                    self.patience = max(0, self.patience - 10)
                    
    def select_option(self):
        """Process selected option"""
        if self.selected_option >= len(self.task_options):
            return
            
        option_text, option_id, success_rate = self.task_options[self.selected_option]
        
        # Determine success
        if random.random() < success_rate:
            # Success
            self.understanding += 10
            if 'appeal' in option_id:
                self.appeals_filed += 1
            elif 'give_up' in option_id or 'collections' in option_id:
                self.denials_received += 1
                self.patience = 0
        else:
            # Failure
            self.denials_received += 1
            self.patience = max(0, self.patience - 20)
            
        self.time_spent_hours += random.randint(2, 6)
        self.advance_step()
        
    def advance_step(self):
        """Move to next step"""
        self.current_step += 1
        if self.current_step >= len(self.maze_steps):
            self.end_game()
        else:
            self.load_current_task()
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Slowly drain patience over time
        if self.phone_menu_level > 0:
            self.patience = max(0, self.patience - dt * 5)
            
    def end_game(self):
        """End the navigation game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate success
        if self.patience <= 0:
            message = "Gave up fighting insurance company"
            success = False
        elif self.denials_received >= 5:
            message = f"Claim denied {self.denials_received} times. Medical debt: $3,200"
            success = False
        else:
            message = f"Partially resolved after {self.time_spent_hours} hours of work"
            success = True
            
        return {
            'money': -500 if not success else -100,
            'stress': 40 if not success else 20,
            'health': -10,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the insurance navigation interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((245, 245, 250))
        
        # Title
        title = "INSURANCE NAVIGATION MAZE"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Progress bar
        progress_rect = pygame.Rect(50, 70, SCREEN_WIDTH - 100, 30)
        pygame.draw.rect(screen, (200, 200, 210), progress_rect, 2)
        
        # Fill progress
        progress_fill = pygame.Rect(52, 72, 
                                   int((progress_rect.width - 4) * self.current_step / self.total_steps), 
                                   26)
        pygame.draw.rect(screen, (100, 200, 100), progress_fill)
        
        # Progress text
        progress_text = f"Step {self.current_step + 1} of {self.total_steps}"
        progress_surf = self.small_font.render(progress_text, True, (80, 80, 90))
        progress_text_rect = progress_surf.get_rect(center=progress_rect.center)
        screen.blit(progress_surf, progress_text_rect)
        
        # Stats panel
        stats_rect = pygame.Rect(50, 120, 250, 150)
        pygame.draw.rect(screen, (255, 255, 255), stats_rect)
        pygame.draw.rect(screen, (200, 200, 210), stats_rect, 2)
        
        stats = [
            ('Patience', f"{int(self.patience)}%", 
             (100, 200, 100) if self.patience > 50 else (255, 200, 100) if self.patience > 20 else (255, 100, 100)),
            ('Understanding', f"{int(self.understanding)}%", (100, 150, 255)),
            ('Time Spent', f"{self.time_spent_hours}h", (150, 150, 150)),
            ('Denials', str(self.denials_received), (255, 100, 100)),
            ('Appeals Filed', str(self.appeals_filed), (255, 200, 100))
        ]
        
        stat_y = stats_rect.y + 10
        for stat_name, stat_value, color in stats:
            name_surf = self.small_font.render(stat_name + ":", True, (80, 80, 90))
            screen.blit(name_surf, (stats_rect.x + 10, stat_y))
            
            value_surf = self.font.render(stat_value, True, color)
            screen.blit(value_surf, (stats_rect.x + 150, stat_y - 2))
            
            stat_y += 28
            
        # Main task area
        if self.current_task:
            task_rect = pygame.Rect(320, 120, 430, 150)
            pygame.draw.rect(screen, (250, 250, 255), task_rect)
            pygame.draw.rect(screen, (180, 180, 200), task_rect, 3)
            
            # Task title
            task_title_surf = self.font.render(self.current_task['title'], True, (60, 60, 80))
            screen.blit(task_title_surf, (task_rect.x + 20, task_rect.y + 15))
            
            # Task description
            desc_lines = self.wrap_text(self.current_task['description'], task_rect.width - 40)
            desc_y = task_rect.y + 50
            for line in desc_lines:
                desc_surf = self.small_font.render(line, True, (80, 80, 100))
                screen.blit(desc_surf, (task_rect.x + 20, desc_y))
                desc_y += 22
                
        # Phone menu display
        if self.phone_menu_level > 0 and self.phone_menu_level <= len(self.phone_menus):
            phone_rect = pygame.Rect(100, 300, SCREEN_WIDTH - 200, 200)
            pygame.draw.rect(screen, (20, 20, 30), phone_rect)
            pygame.draw.rect(screen, (100, 100, 120), phone_rect, 3)
            
            # Phone interface
            phone_title = "AUTOMATED PHONE SYSTEM"
            phone_surf = self.font.render(phone_title, True, (100, 255, 100))
            phone_rect_text = phone_surf.get_rect(center=(phone_rect.centerx, phone_rect.y + 30))
            screen.blit(phone_surf, phone_rect_text)
            
            # Current menu
            if self.phone_menu_level - 1 < len(self.phone_menus):
                menu = self.phone_menus[self.phone_menu_level - 1]
                menu_lines = self.wrap_text(menu['prompt'], phone_rect.width - 40)
                menu_y = phone_rect.y + 70
                for line in menu_lines:
                    line_surf = self.font.render(line, True, (200, 255, 200))
                    line_rect = line_surf.get_rect(center=(phone_rect.centerx, menu_y))
                    screen.blit(line_surf, line_rect)
                    menu_y += 30
                    
            # Hold time if on hold
            if self.phone_hold_time > 0:
                hold_text = f"Current hold time: {self.phone_hold_time} minutes"
                hold_surf = self.font.render(hold_text, True, (255, 200, 100))
                hold_rect = hold_surf.get_rect(center=(phone_rect.centerx, phone_rect.bottom - 40))
                screen.blit(hold_surf, hold_rect)
        else:
            # Options display
            options_rect = pygame.Rect(50, 300, SCREEN_WIDTH - 100, 200)
            pygame.draw.rect(screen, (255, 255, 255), options_rect)
            pygame.draw.rect(screen, (200, 200, 210), options_rect, 2)
            
            options_title = self.font.render("Your Options:", True, (60, 60, 80))
            screen.blit(options_title, (options_rect.x + 20, options_rect.y + 10))
            
            # Draw options
            option_y = options_rect.y + 50
            for i, (option_text, _, success_rate) in enumerate(self.task_options):
                # Selection highlight
                if i == self.selected_option:
                    sel_rect = pygame.Rect(options_rect.x + 10, option_y - 5, options_rect.width - 20, 35)
                    pygame.draw.rect(screen, (220, 230, 255), sel_rect)
                    
                # Option text
                color = (50, 50, 60) if i != self.selected_option else (0, 0, 200)
                option_surf = self.font.render(f"• {option_text}", True, color)
                screen.blit(option_surf, (options_rect.x + 30, option_y))
                
                # Success rate hint (subtle)
                if success_rate < 0.5:
                    risk_text = "(risky)"
                    risk_color = (255, 150, 150)
                elif success_rate < 0.8:
                    risk_text = "(uncertain)"
                    risk_color = (255, 200, 150)
                else:
                    risk_text = "(recommended)"
                    risk_color = (150, 255, 150)
                    
                risk_surf = self.small_font.render(risk_text, True, risk_color)
                screen.blit(risk_surf, (options_rect.x + options_rect.width - 120, option_y + 5))
                
                option_y += 40
                
        # Instructions
        if self.phone_menu_level > 0:
            inst_text = "Navigate the phone menu - Press number keys as indicated"
        else:
            inst_text = "↑↓ Select option | ENTER Choose | Each choice has consequences"
            
        inst_surf = self.small_font.render(inst_text, True, (120, 120, 140))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst_surf, inst_rect)
        
        # Warning if patience is low
        if self.patience < 20:
            warning_text = "⚠ WARNING: Patience critically low!"
            warning_surf = self.font.render(warning_text, True, (255, 50, 50))
            warning_rect = warning_surf.get_rect(center=(SCREEN_WIDTH // 2, 520))
            
            if int(pygame.time.get_ticks() / 500) % 2:  # Blinking
                screen.blit(warning_surf, warning_rect)
                
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
"""Financial Aid Maze - Navigate FAFSA and financial aid bureaucracy"""

import pygame
import random
import math
from shared.constants import *

class FinancialAidMaze:
    """Navigate the complex financial aid system"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # FAFSA process tracking
        self.current_form = 0
        self.total_forms = 12
        self.forms_completed = []
        self.documents_required = []
        self.documents_obtained = []
        
        # Player state
        self.patience = 100
        self.confusion = 20
        self.time_spent_hours = 0
        self.money_spent = 0
        
        # Current screen
        self.current_screen = 'main'  # main, form, documents, verification
        self.selected_option = 0
        
        # Error messages and rejections
        self.error_messages = []
        self.rejection_reasons = []
        
        # Visual elements
        self.form_particles = []
        self.stress_shake = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.code_font = pygame.font.Font(None, 18)
        
        # FAFSA maze steps
        self.fafsa_steps = [
            {
                'id': 'create_fsaid',
                'name': 'Create FSA ID',
                'complexity': 3,
                'documents': [],
                'errors': [
                    'Password must contain uppercase, lowercase, number, special character',
                    'Username already taken',
                    'Security questions cannot contain dictionary words'
                ]
            },
            {
                'id': 'parent_fsaid',
                'name': 'Parent FSA ID',
                'complexity': 5,
                'documents': ['Parent SSN', 'Parent email'],
                'errors': [
                    'Parent refuses to create account',
                    'Parent forgot their own SSN',
                    'Parent email already has FSA ID from sibling'
                ]
            },
            {
                'id': 'start_fafsa',
                'name': 'Start FAFSA Form',
                'complexity': 4,
                'documents': ['SSN', 'Drivers License'],
                'errors': [
                    'Session timed out - start over',
                    'Browser not supported',
                    'Site under maintenance'
                ]
            },
            {
                'id': 'tax_info',
                'name': 'Import Tax Information',
                'complexity': 7,
                'documents': ['Tax Return', 'W-2 Forms', '1099 Forms'],
                'errors': [
                    'IRS Data Retrieval Tool unavailable',
                    'Tax return not yet processed',
                    'Name mismatch with IRS records'
                ]
            },
            {
                'id': 'parent_tax',
                'name': 'Parent Tax Info',
                'complexity': 8,
                'documents': ['Parent Tax Return', 'Parent W-2'],
                'errors': [
                    'Parents filed separately',
                    'Parent refuses to share tax info',
                    'Parent amended return - DRT unavailable'
                ]
            },
            {
                'id': 'dependency',
                'name': 'Dependency Status',
                'complexity': 6,
                'documents': [],
                'errors': [
                    'You are dependent but parents won\'t help',
                    'Homeless but still considered dependent',
                    'Need dependency override documentation'
                ]
            },
            {
                'id': 'asset_info',
                'name': 'Report Assets',
                'complexity': 5,
                'documents': ['Bank Statements'],
                'errors': [
                    'Include or exclude car? Unclear.',
                    'Parents have complex investments',
                    'Cryptocurrency not listed as option'
                ]
            },
            {
                'id': 'school_list',
                'name': 'Add Schools',
                'complexity': 3,
                'documents': [],
                'errors': [
                    'School code not found',
                    'Maximum 10 schools - need to do multiple rounds',
                    'Community college has 5 different codes'
                ]
            },
            {
                'id': 'sign_submit',
                'name': 'Sign and Submit',
                'complexity': 4,
                'documents': [],
                'errors': [
                    'Parent signature missing',
                    'Signature doesn\'t match FSA ID',
                    'Submit button grayed out - unknown reason'
                ]
            },
            {
                'id': 'sar_review',
                'name': 'Review SAR',
                'complexity': 5,
                'documents': [],
                'errors': [
                    'Selected for verification',
                    'EFC seems impossibly high',
                    'Data doesn\'t match what you entered'
                ]
            },
            {
                'id': 'verification',
                'name': 'Verification Process',
                'complexity': 9,
                'documents': ['Tax Transcript', 'Verification Worksheet', 'Identity Proof'],
                'errors': [
                    'IRS transcript request failed',
                    'School wants different form than provided',
                    'Deadline passed while gathering documents'
                ]
            },
            {
                'id': 'award_letter',
                'name': 'Understand Award',
                'complexity': 6,
                'documents': [],
                'errors': [
                    'Mostly loans, not grants',
                    'Work-study requires car you don\'t have',
                    'Award doesn\'t cover full need'
                ]
            }
        ]
        
        # Required documents master list
        self.all_documents = [
            {'name': 'Social Security Card', 'difficulty': 3, 'cost': 0},
            {'name': 'Drivers License', 'difficulty': 2, 'cost': 25},
            {'name': 'Tax Return', 'difficulty': 5, 'cost': 0},
            {'name': 'W-2 Forms', 'difficulty': 4, 'cost': 0},
            {'name': '1099 Forms', 'difficulty': 6, 'cost': 0},
            {'name': 'Bank Statements', 'difficulty': 2, 'cost': 5},
            {'name': 'Parent Tax Return', 'difficulty': 8, 'cost': 0},
            {'name': 'Parent W-2', 'difficulty': 7, 'cost': 0},
            {'name': 'Parent SSN', 'difficulty': 9, 'cost': 0},
            {'name': 'Parent email', 'difficulty': 6, 'cost': 0},
            {'name': 'Tax Transcript', 'difficulty': 7, 'cost': 0},
            {'name': 'Verification Worksheet', 'difficulty': 5, 'cost': 0},
            {'name': 'Identity Proof', 'difficulty': 4, 'cost': 10}
        ]
        
    def start(self):
        """Start the financial aid maze"""
        self.active = True
        self.completed = False
        self.current_form = 0
        self.load_current_step()
        
    def load_current_step(self):
        """Load the current FAFSA step"""
        if self.current_form < len(self.fafsa_steps):
            step = self.fafsa_steps[self.current_form]
            self.documents_required = step['documents']
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if self.current_screen == 'main':
            options = self.get_main_options()
            if key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif key == pygame.K_DOWN:
                self.selected_option = min(len(options) - 1, self.selected_option + 1)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.select_main_option()
                
        elif self.current_screen == 'form':
            if key == pygame.K_1:
                # Try to complete form
                self.attempt_form_completion()
            elif key == pygame.K_2:
                # Get help
                self.get_help()
            elif key == pygame.K_3:
                # Give up on this step
                self.skip_step()
            elif key == pygame.K_ESCAPE:
                self.current_screen = 'main'
                
        elif self.current_screen == 'documents':
            docs_needed = [d for d in self.documents_required if d not in self.documents_obtained]
            if key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif key == pygame.K_DOWN:
                self.selected_option = min(len(docs_needed) - 1, self.selected_option + 1)
            elif key == pygame.K_RETURN:
                self.obtain_document()
            elif key == pygame.K_ESCAPE:
                self.current_screen = 'main'
                
    def get_main_options(self):
        """Get available main menu options"""
        options = []
        
        if self.current_form < len(self.fafsa_steps):
            step = self.fafsa_steps[self.current_form]
            options.append(f"Work on: {step['name']}")
            
        if self.documents_required:
            missing = [d for d in self.documents_required if d not in self.documents_obtained]
            if missing:
                options.append(f"Gather documents ({len(missing)} needed)")
                
        options.append("Check progress")
        options.append("Give up")
        
        return options
        
    def select_main_option(self):
        """Handle main menu selection"""
        options = self.get_main_options()
        if self.selected_option >= len(options):
            return
            
        selected = options[self.selected_option]
        
        if "Work on:" in selected:
            self.current_screen = 'form'
        elif "Gather documents" in selected:
            self.current_screen = 'documents'
            self.selected_option = 0
        elif "Give up" in selected:
            self.end_game()
            
    def attempt_form_completion(self):
        """Try to complete current form"""
        if self.current_form >= len(self.fafsa_steps):
            return
            
        step = self.fafsa_steps[self.current_form]
        
        # Check if have all required documents
        missing_docs = [d for d in step['documents'] if d not in self.documents_obtained]
        if missing_docs:
            self.error_messages.append(f"Missing required documents: {', '.join(missing_docs)}")
            self.confusion += 15
            self.patience -= 10
            return
            
        # Complexity check - chance of errors
        error_chance = step['complexity'] * 0.1
        if random.random() < error_chance:
            # Hit an error
            error = random.choice(step['errors'])
            self.error_messages.append(error)
            self.confusion += 10
            self.patience -= 15
            self.time_spent_hours += 2
            
            # Some errors are critical
            if "start over" in error.lower() or "deadline passed" in error.lower():
                self.patience -= 30
                self.stress_shake = 30
        else:
            # Success!
            self.forms_completed.append(step['id'])
            self.current_form += 1
            self.time_spent_hours += 1
            self.confusion = max(0, self.confusion - 5)
            
            if self.current_form >= len(self.fafsa_steps):
                self.end_game()
            else:
                self.load_current_step()
                
        self.current_screen = 'main'
        
    def get_help(self):
        """Try to get help with form"""
        help_options = [
            ("Called financial aid office - on hold for 45 minutes", 45, 10),
            ("Googled the question - found conflicting answers", 20, 5),
            ("Asked parent for help - they don't understand either", 30, 15),
            ("Paid $50 for professional help", 10, -20)
        ]
        
        help_result = random.choice(help_options)
        message, time_cost, confusion_change = help_result
        
        self.error_messages.append(message)
        self.time_spent_hours += time_cost / 60
        self.confusion += confusion_change
        self.patience -= 5
        
        if "$50" in message:
            self.money_spent += 50
            
        self.current_screen = 'main'
        
    def skip_step(self):
        """Skip current step (with consequences)"""
        self.rejection_reasons.append(f"Incomplete: {self.fafsa_steps[self.current_form]['name']}")
        self.current_form += 1
        self.patience -= 20
        
        if self.current_form >= len(self.fafsa_steps):
            self.end_game()
        else:
            self.load_current_step()
            
        self.current_screen = 'main'
        
    def obtain_document(self):
        """Try to obtain a required document"""
        docs_needed = [d for d in self.documents_required if d not in self.documents_obtained]
        if self.selected_option >= len(docs_needed):
            return
            
        doc_name = docs_needed[self.selected_option]
        
        # Find document info
        doc_info = next((d for d in self.all_documents if d['name'] == doc_name), None)
        if not doc_info:
            return
            
        # Difficulty check
        success_chance = 1.0 - (doc_info['difficulty'] * 0.08)
        if random.random() < success_chance:
            # Got it!
            self.documents_obtained.append(doc_name)
            self.money_spent += doc_info['cost']
            self.time_spent_hours += doc_info['difficulty'] * 0.5
            
            # Generate particle effect
            for _ in range(10):
                self.form_particles.append({
                    'x': SCREEN_WIDTH // 2,
                    'y': SCREEN_HEIGHT // 2,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-3, -1),
                    'life': 30,
                    'color': (100, 255, 100)
                })
        else:
            # Failed to get document
            fail_reasons = [
                f"Can't find {doc_name}",
                f"{doc_name} request denied",
                f"Wrong version of {doc_name}",
                f"{doc_name} office closed"
            ]
            self.error_messages.append(random.choice(fail_reasons))
            self.patience -= 10
            self.confusion += 5
            
        self.current_screen = 'main'
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update particles
        for particle in self.form_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.5
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.form_particles.remove(particle)
                
        # Update stress shake
        if self.stress_shake > 0:
            self.stress_shake -= 1
            
        # Clear old error messages
        if len(self.error_messages) > 5:
            self.error_messages = self.error_messages[-5:]
            
    def end_game(self):
        """End the financial aid maze"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate success
        completion_rate = len(self.forms_completed) / len(self.fafsa_steps)
        
        if completion_rate >= 0.9 and len(self.rejection_reasons) == 0:
            message = f"FAFSA completed after {int(self.time_spent_hours)} hours!"
            success = True
        elif completion_rate >= 0.6:
            message = f"FAFSA partially complete. May get some aid."
            success = False
        else:
            message = f"FAFSA incomplete. No financial aid available."
            success = False
            
        return {
            'money': -self.money_spent,
            'stress': 30 if not success else 10,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the financial aid maze interface"""
        if not self.active:
            return
            
        # Background with stress effect
        base_color = 245
        if self.stress_shake > 0:
            shake_offset = random.randint(-2, 2)
            base_color = max(200, base_color - self.stress_shake)
        else:
            shake_offset = 0
            
        screen.fill((base_color, base_color, base_color + 5))
        
        # Apply shake to all positions if stressed
        offset_x = shake_offset if self.stress_shake > 0 else 0
        offset_y = shake_offset if self.stress_shake > 0 else 0
        
        # Title
        title = "FAFSA FINANCIAL AID MAZE"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset_x, 30 + offset_y))
        screen.blit(title_surf, title_rect)
        
        # Progress bar
        progress_rect = pygame.Rect(50, 70, SCREEN_WIDTH - 100, 30)
        pygame.draw.rect(screen, (200, 200, 210), progress_rect, 2)
        
        # Fill progress
        progress_fill = pygame.Rect(52, 72,
                                   int((progress_rect.width - 4) * self.current_form / len(self.fafsa_steps)),
                                   26)
        pygame.draw.rect(screen, (100, 200, 100), progress_fill)
        
        # Progress text
        progress_text = f"Step {self.current_form + 1} of {len(self.fafsa_steps)}"
        progress_surf = self.small_font.render(progress_text, True, (80, 80, 90))
        progress_text_rect = progress_surf.get_rect(center=progress_rect.center)
        screen.blit(progress_surf, progress_text_rect)
        
        # Stats panel
        stats_rect = pygame.Rect(50, 120, 250, 180)
        pygame.draw.rect(screen, (255, 255, 255), stats_rect)
        pygame.draw.rect(screen, (200, 200, 210), stats_rect, 2)
        
        stats = [
            ('Patience', f"{int(self.patience)}%", 
             (100, 200, 100) if self.patience > 50 else (255, 200, 100) if self.patience > 20 else (255, 100, 100)),
            ('Confusion', f"{int(self.confusion)}%", 
             (255, 100, 100) if self.confusion > 70 else (255, 200, 100) if self.confusion > 40 else (100, 200, 100)),
            ('Time Spent', f"{int(self.time_spent_hours)}h", (150, 150, 150)),
            ('Money Spent', f"${self.money_spent}", (255, 100, 100) if self.money_spent > 0 else (100, 200, 100)),
            ('Forms Done', f"{len(self.forms_completed)}/{len(self.fafsa_steps)}", (100, 150, 255)),
            ('Documents', f"{len(self.documents_obtained)}", (150, 200, 150))
        ]
        
        stat_y = stats_rect.y + 10
        for stat_name, stat_value, color in stats:
            name_surf = self.small_font.render(stat_name + ":", True, (80, 80, 90))
            screen.blit(name_surf, (stats_rect.x + 10, stat_y))
            
            value_surf = self.font.render(stat_value, True, color)
            screen.blit(value_surf, (stats_rect.x + 150, stat_y - 2))
            
            stat_y += 28
            
        # Draw current screen
        if self.current_screen == 'main':
            self.draw_main_screen(screen, offset_x, offset_y)
        elif self.current_screen == 'form':
            self.draw_form_screen(screen, offset_x, offset_y)
        elif self.current_screen == 'documents':
            self.draw_documents_screen(screen, offset_x, offset_y)
            
        # Error messages
        if self.error_messages:
            error_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 100)
            pygame.draw.rect(screen, (255, 240, 240), error_rect)
            pygame.draw.rect(screen, (255, 100, 100), error_rect, 3)
            
            error_title = self.small_font.render("Recent Issues:", True, (200, 50, 50))
            screen.blit(error_title, (error_rect.x + 10, error_rect.y + 5))
            
            error_y = error_rect.y + 25
            for error in self.error_messages[-3:]:  # Show last 3
                # Word wrap if needed
                if len(error) > 80:
                    error = error[:77] + "..."
                error_surf = self.small_font.render(f"• {error}", True, (150, 50, 50))
                screen.blit(error_surf, (error_rect.x + 20, error_y))
                error_y += 20
                
        # Draw particles
        for particle in self.form_particles:
            pygame.draw.circle(screen, particle['color'],
                             (int(particle['x']), int(particle['y'])), 3)
                             
    def draw_main_screen(self, screen, offset_x, offset_y):
        """Draw main menu screen"""
        # Current step info
        if self.current_form < len(self.fafsa_steps):
            step = self.fafsa_steps[self.current_form]
            
            step_rect = pygame.Rect(320, 120, 430, 180)
            pygame.draw.rect(screen, (250, 250, 255), step_rect)
            pygame.draw.rect(screen, (180, 180, 200), step_rect, 3)
            
            step_title = self.font.render(f"Current: {step['name']}", True, (60, 60, 80))
            screen.blit(step_title, (step_rect.x + 20, step_rect.y + 15))
            
            # Complexity indicator
            complexity_text = "Complexity: "
            comp_surf = self.small_font.render(complexity_text, True, (80, 80, 100))
            screen.blit(comp_surf, (step_rect.x + 20, step_rect.y + 50))
            
            # Draw complexity stars
            star_x = step_rect.x + 120
            for i in range(10):
                color = (255, 200, 50) if i < step['complexity'] else (200, 200, 210)
                pygame.draw.circle(screen, color, (star_x + i * 25, step_rect.y + 55), 8)
                
            # Required documents
            if step['documents']:
                docs_y = step_rect.y + 80
                docs_title = self.small_font.render("Required Documents:", True, (80, 80, 100))
                screen.blit(docs_title, (step_rect.x + 20, docs_y))
                
                docs_y += 20
                for doc in step['documents']:
                    has_doc = doc in self.documents_obtained
                    doc_color = (100, 200, 100) if has_doc else (255, 100, 100)
                    doc_symbol = "✓" if has_doc else "✗"
                    doc_text = f"{doc_symbol} {doc}"
                    doc_surf = self.small_font.render(doc_text, True, doc_color)
                    screen.blit(doc_surf, (step_rect.x + 40, docs_y))
                    docs_y += 20
                    
        # Options menu
        options = self.get_main_options()
        menu_rect = pygame.Rect(50, 320, 400, 200)
        pygame.draw.rect(screen, (255, 255, 255), menu_rect)
        pygame.draw.rect(screen, (200, 200, 210), menu_rect, 2)
        
        menu_title = self.font.render("What would you like to do?", True, (60, 60, 80))
        screen.blit(menu_title, (menu_rect.x + 20, menu_rect.y + 10))
        
        option_y = menu_rect.y + 50
        for i, option in enumerate(options):
            if i == self.selected_option:
                sel_rect = pygame.Rect(menu_rect.x + 10, option_y - 5, menu_rect.width - 20, 30)
                pygame.draw.rect(screen, (220, 230, 255), sel_rect)
                
            color = (0, 0, 200) if i == self.selected_option else (50, 50, 60)
            option_surf = self.font.render(f"• {option}", True, color)
            screen.blit(option_surf, (menu_rect.x + 30 + offset_x, option_y + offset_y))
            option_y += 35
            
        # Instructions
        inst_text = "↑↓ Select option | ENTER Choose"
        inst_surf = self.small_font.render(inst_text, True, (120, 120, 140))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        screen.blit(inst_surf, inst_rect)
        
    def draw_form_screen(self, screen, offset_x, offset_y):
        """Draw form completion screen"""
        if self.current_form >= len(self.fafsa_steps):
            return
            
        step = self.fafsa_steps[self.current_form]
        
        # Form window
        form_rect = pygame.Rect(100, 150, SCREEN_WIDTH - 200, 350)
        pygame.draw.rect(screen, (255, 255, 255), form_rect)
        pygame.draw.rect(screen, (100, 100, 150), form_rect, 4)
        
        # Form header
        header = f"FAFSA FORM - {step['name'].upper()}"
        header_surf = self.title_font.render(header, True, (50, 50, 100))
        header_rect = header_surf.get_rect(center=(form_rect.centerx, form_rect.y + 30))
        screen.blit(header_surf, header_rect)
        
        # Simulate form fields with cryptic labels
        form_fields = [
            "Box 31a: Prior prior year AGI from line 37 or 38:",
            "Schedule 1 additions (if applicable):",
            "Did you file a 1040X amended return?",
            "Untaxed portions of IRA distributions:",
            "Housing/food/other living allowances:",
            "Veterans non-education benefits:",
            "Other untaxed income not reported elsewhere:"
        ]
        
        field_y = form_rect.y + 80
        for field in form_fields[:4]:  # Show first 4
            # Field label
            label_surf = self.code_font.render(field, True, (60, 60, 80))
            screen.blit(label_surf, (form_rect.x + 30, field_y))
            
            # Input box
            input_rect = pygame.Rect(form_rect.x + 30, field_y + 20, 300, 25)
            pygame.draw.rect(screen, (240, 240, 245), input_rect)
            pygame.draw.rect(screen, (180, 180, 190), input_rect, 1)
            
            # Fake input cursor
            if int(pygame.time.get_ticks() / 500) % 2:
                cursor_x = input_rect.x + 5
                pygame.draw.line(screen, (50, 50, 60),
                               (cursor_x, input_rect.y + 5),
                               (cursor_x, input_rect.bottom - 5), 2)
                               
            field_y += 60
            
        # Options
        options_rect = pygame.Rect(form_rect.x + 50, form_rect.bottom - 100, form_rect.width - 100, 80)
        pygame.draw.rect(screen, (240, 240, 250), options_rect)
        pygame.draw.rect(screen, (180, 180, 200), options_rect, 2)
        
        options_text = [
            "1 - Submit this section",
            "2 - Call for help (wait time: 45+ min)",
            "3 - Skip this section (may affect aid)",
            "ESC - Save and return later"
        ]
        
        opt_y = options_rect.y + 10
        for opt in options_text:
            opt_surf = self.small_font.render(opt, True, (60, 60, 80))
            screen.blit(opt_surf, (options_rect.x + 20, opt_y))
            opt_y += 18
            
    def draw_documents_screen(self, screen, offset_x, offset_y):
        """Draw document gathering screen"""
        docs_rect = pygame.Rect(100, 120, SCREEN_WIDTH - 200, 400)
        pygame.draw.rect(screen, (255, 255, 255), docs_rect)
        pygame.draw.rect(screen, (150, 150, 170), docs_rect, 3)
        
        # Title
        docs_title = "GATHER REQUIRED DOCUMENTS"
        title_surf = self.title_font.render(docs_title, True, (60, 60, 80))
        title_rect = title_surf.get_rect(center=(docs_rect.centerx, docs_rect.y + 30))
        screen.blit(title_surf, title_rect)
        
        # List needed documents
        docs_needed = [d for d in self.documents_required if d not in self.documents_obtained]
        
        if not docs_needed:
            no_docs = "All required documents obtained!"
            no_docs_surf = self.font.render(no_docs, True, (100, 200, 100))
            no_docs_rect = no_docs_surf.get_rect(center=docs_rect.center)
            screen.blit(no_docs_surf, no_docs_rect)
        else:
            list_y = docs_rect.y + 80
            for i, doc_name in enumerate(docs_needed):
                # Find document info
                doc_info = next((d for d in self.all_documents if d['name'] == doc_name), None)
                if not doc_info:
                    continue
                    
                # Selection highlight
                if i == self.selected_option:
                    sel_rect = pygame.Rect(docs_rect.x + 20, list_y - 5, docs_rect.width - 40, 60)
                    pygame.draw.rect(screen, (220, 230, 255), sel_rect)
                    
                # Document name
                color = (0, 0, 200) if i == self.selected_option else (50, 50, 60)
                doc_surf = self.font.render(doc_name, True, color)
                screen.blit(doc_surf, (docs_rect.x + 40, list_y))
                
                # Document details
                detail_y = list_y + 25
                details = f"Difficulty: {'*' * doc_info['difficulty']} | "
                if doc_info['cost'] > 0:
                    details += f"Cost: ${doc_info['cost']}"
                else:
                    details += "Cost: Free"
                    
                detail_surf = self.small_font.render(details, True, (100, 100, 120))
                screen.blit(detail_surf, (docs_rect.x + 60, detail_y))
                
                list_y += 70
                
        # Instructions
        inst_text = "↑↓ Select document | ENTER Try to obtain | ESC Back"
        inst_surf = self.small_font.render(inst_text, True, (120, 120, 140))
        inst_rect = inst_surf.get_rect(center=(docs_rect.centerx, docs_rect.bottom - 20))
        screen.blit(inst_surf, inst_rect)
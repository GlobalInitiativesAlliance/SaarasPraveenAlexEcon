"""Tenant Rights Class Quiz - Learn your rights as a tenant"""

import pygame
from shared.constants import *

class TenantRightsQuiz:
    """Interactive quiz about tenant rights"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Quiz state
        self.current_question = 0
        self.score = 0
        self.selected_answer = 0
        self.show_feedback = False
        self.feedback_timer = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.question_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Quiz questions about tenant rights
        self.questions = [
            {
                'question': 'How much notice must a landlord give before entering your apartment?',
                'options': ['No notice needed', '24 hours', '48 hours', '1 week'],
                'correct': 1,
                'explanation': 'In most states, landlords must give 24 hours notice except in emergencies.'
            },
            {
                'question': 'What is a security deposit typically used for?',
                'options': ['First month rent', 'Damages beyond normal wear', 'Landlord profit', 'Utilities'],
                'correct': 1,
                'explanation': 'Security deposits cover damages beyond normal wear and tear, not routine maintenance.'
            },
            {
                'question': 'Can a landlord evict you without going to court?',
                'options': ['Yes, anytime', 'Yes, after 30 days', 'No, court order required', 'Only in winter'],
                'correct': 2,
                'explanation': 'Evictions require a court order. Self-help evictions are illegal in most places.'
            },
            {
                'question': 'What should you do if your landlord refuses to make necessary repairs?',
                'options': ['Stop paying rent', 'Make repairs yourself', 'Document and notify in writing', 'Move out immediately'],
                'correct': 2,
                'explanation': 'Always document issues and notify your landlord in writing. Keep copies of everything.'
            },
            {
                'question': 'What is "normal wear and tear"?',
                'options': ['Broken windows', 'Faded paint from sunlight', 'Large carpet stains', 'Holes in walls'],
                'correct': 1,
                'explanation': 'Normal wear includes natural aging like faded paint or minor carpet wear from regular use.'
            }
        ]
        
    def start(self):
        """Start the quiz"""
        self.active = True
        self.completed = False
        self.current_question = 0
        self.score = 0
        self.selected_answer = 0
        self.show_feedback = False
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if self.show_feedback:
            if key == pygame.K_SPACE or key == pygame.K_RETURN:
                self.next_question()
            return
            
        if key == pygame.K_UP:
            self.selected_answer = (self.selected_answer - 1) % 4
        elif key == pygame.K_DOWN:
            self.selected_answer = (self.selected_answer + 1) % 4
        elif key in [pygame.K_1, pygame.K_KP1]:
            self.selected_answer = 0
        elif key in [pygame.K_2, pygame.K_KP2]:
            self.selected_answer = 1
        elif key in [pygame.K_3, pygame.K_KP3]:
            self.selected_answer = 2
        elif key in [pygame.K_4, pygame.K_KP4]:
            self.selected_answer = 3
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.submit_answer()
            
    def submit_answer(self):
        """Check the selected answer"""
        question = self.questions[self.current_question]
        if self.selected_answer == question['correct']:
            self.score += 1
        self.show_feedback = True
        self.feedback_timer = 2.0
        
    def next_question(self):
        """Move to next question or end quiz"""
        self.current_question += 1
        self.selected_answer = 0
        self.show_feedback = False
        
        if self.current_question >= len(self.questions):
            self.end_quiz()
            
    def end_quiz(self):
        """End the quiz"""
        self.active = False
        self.completed = True
        
    def update(self, dt):
        """Update quiz state"""
        if not self.active:
            return
            
        if self.show_feedback:
            self.feedback_timer -= dt
            
    def draw(self, screen):
        """Draw the quiz interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((240, 240, 235))
        
        # Title
        title = "TENANT RIGHTS CLASS"
        title_surf = self.title_font.render(title, True, (40, 40, 50))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surf, title_rect)
        
        # Progress
        progress_text = f"Question {self.current_question + 1} of {len(self.questions)}"
        progress_surf = self.font.render(progress_text, True, (100, 100, 120))
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH // 2, 90))
        screen.blit(progress_surf, progress_rect)
        
        # Score
        score_text = f"Score: {self.score}/{self.current_question}"
        score_surf = self.font.render(score_text, True, (60, 140, 60))
        screen.blit(score_surf, (50, 50))
        
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Question box
            q_box = pygame.Rect(50, 130, SCREEN_WIDTH - 100, 100)
            pygame.draw.rect(screen, (255, 255, 255), q_box)
            pygame.draw.rect(screen, (200, 200, 210), q_box, 2)
            
            # Question text (word wrap if needed)
            words = question['question'].split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.question_font.size(test_line)[0] < q_box.width - 40:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
                
            y_offset = q_box.y + 20
            for line in lines:
                line_surf = self.question_font.render(line, True, (40, 40, 50))
                line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                screen.blit(line_surf, line_rect)
                y_offset += 35
                
            # Answer options
            options_y = 260
            for i, option in enumerate(question['options']):
                # Option box
                opt_rect = pygame.Rect(100, options_y + i * 60, SCREEN_WIDTH - 200, 50)
                
                # Highlight selected or show correct/incorrect
                if self.show_feedback:
                    if i == question['correct']:
                        pygame.draw.rect(screen, (200, 255, 200), opt_rect)
                        pygame.draw.rect(screen, (60, 180, 60), opt_rect, 3)
                    elif i == self.selected_answer and i != question['correct']:
                        pygame.draw.rect(screen, (255, 200, 200), opt_rect)
                        pygame.draw.rect(screen, (180, 60, 60), opt_rect, 3)
                    else:
                        pygame.draw.rect(screen, (245, 245, 245), opt_rect)
                        pygame.draw.rect(screen, (200, 200, 200), opt_rect, 2)
                else:
                    if i == self.selected_answer:
                        pygame.draw.rect(screen, (220, 230, 255), opt_rect)
                        pygame.draw.rect(screen, (100, 120, 200), opt_rect, 3)
                    else:
                        pygame.draw.rect(screen, (255, 255, 255), opt_rect)
                        pygame.draw.rect(screen, (200, 200, 200), opt_rect, 2)
                        
                # Option number and text
                num_text = f"{i + 1}."
                num_surf = self.font.render(num_text, True, (100, 100, 100))
                screen.blit(num_surf, (opt_rect.x + 10, opt_rect.y + 15))
                
                opt_surf = self.font.render(option, True, (40, 40, 50))
                opt_rect_text = opt_surf.get_rect(midleft=(opt_rect.x + 40, opt_rect.centery))
                screen.blit(opt_surf, opt_rect_text)
                
            # Feedback
            if self.show_feedback:
                # Explanation box
                exp_rect = pygame.Rect(50, 520, SCREEN_WIDTH - 100, 80)
                pygame.draw.rect(screen, (250, 250, 240), exp_rect)
                pygame.draw.rect(screen, (180, 180, 190), exp_rect, 2)
                
                # Result
                if self.selected_answer == question['correct']:
                    result_text = "✓ Correct!"
                    result_color = (60, 140, 60)
                else:
                    result_text = "✗ Incorrect"
                    result_color = (180, 60, 60)
                    
                result_surf = self.font.render(result_text, True, result_color)
                screen.blit(result_surf, (exp_rect.x + 20, exp_rect.y + 10))
                
                # Explanation
                exp_surf = self.small_font.render(question['explanation'], True, (60, 60, 70))
                screen.blit(exp_surf, (exp_rect.x + 20, exp_rect.y + 40))
                
                # Continue prompt
                continue_surf = self.small_font.render("Press SPACE to continue", True, (100, 100, 120))
                continue_rect = continue_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                screen.blit(continue_surf, continue_rect)
            else:
                # Instructions
                inst_surf = self.small_font.render("Use arrows or number keys to select, ENTER to submit", True, (120, 120, 140))
                inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                screen.blit(inst_surf, inst_rect)
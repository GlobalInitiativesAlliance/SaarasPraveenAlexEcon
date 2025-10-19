"""Homework Struggle Game - Complete assignments with limited resources"""

import pygame
import random
import math
from shared.constants import *

class HomeworkStruggleGame:
    """Try to complete homework without proper resources"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Assignment tracking
        self.current_assignment = 0
        self.total_assignments = 5
        self.assignments_completed = []
        self.current_grade = 0
        
        # Resources available
        self.has_computer = False
        self.has_internet = True  # Library wifi, but limited
        self.has_textbook = False
        self.has_quiet_space = False
        self.library_time_remaining = 60  # minutes
        
        # Current problem state
        self.current_problem = None
        self.problem_type = None
        self.user_answer = ""
        self.feedback = ""
        self.feedback_timer = 0
        
        # Performance metrics
        self.focus_level = 70
        self.frustration = 20
        self.time_pressure = 30
        
        # Environmental distractions
        self.distractions = []
        self.distraction_timer = 0
        
        # Visual elements
        self.screen_glitches = []
        self.stress_particles = []
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.problem_font = pygame.font.Font(None, 28)
        
        # Assignment types
        self.assignment_types = [
            {
                'name': 'Math Problem Set',
                'requires_calculator': True,
                'requires_textbook': True,
                'problems': self.generate_math_problems
            },
            {
                'name': 'Essay Draft',
                'requires_computer': True,
                'requires_internet': True,
                'problems': self.generate_essay_tasks
            },
            {
                'name': 'Online Quiz',
                'requires_computer': True,
                'requires_internet': True,
                'problems': self.generate_quiz_questions
            },
            {
                'name': 'Research Paper',
                'requires_computer': True,
                'requires_internet': True,
                'requires_textbook': True,
                'problems': self.generate_research_tasks
            },
            {
                'name': 'Lab Report',
                'requires_computer': True,
                'requires_quiet': True,
                'problems': self.generate_lab_tasks
            }
        ]
        
    def start(self):
        """Start the homework struggle"""
        self.active = True
        self.completed = False
        self.current_assignment = 0
        self.generate_assignment()
        self.generate_environment()
        
    def generate_environment(self):
        """Generate library environment challenges"""
        # Random distractions in library
        self.distractions = [
            "Loud group at next table",
            "Someone playing videos without headphones",
            "Library closing announcement",
            "Computer randomly logged you out",
            "Internet connection dropped"
        ]
        
    def generate_assignment(self):
        """Generate next assignment"""
        if self.current_assignment >= len(self.assignment_types):
            self.end_game()
            return
            
        self.current_problem = self.assignment_types[self.current_assignment]
        self.problem_type = self.current_problem['name']
        self.generate_specific_problem()
        
    def generate_specific_problem(self):
        """Generate specific problem based on assignment type"""
        if 'Math' in self.problem_type:
            self.current_task = self.generate_math_problems()
        elif 'Essay' in self.problem_type:
            self.current_task = self.generate_essay_tasks()
        elif 'Quiz' in self.problem_type:
            self.current_task = self.generate_quiz_questions()
        elif 'Research' in self.problem_type:
            self.current_task = self.generate_research_tasks()
        elif 'Lab' in self.problem_type:
            self.current_task = self.generate_lab_tasks()
            
    def generate_math_problems(self):
        """Generate math homework problems"""
        problems = [
            {
                'question': 'Solve: 3x² + 7x - 4 = 0',
                'hint': 'Use quadratic formula',
                'answer_contains': ['-2.8', '0.5'],
                'without_calculator': 'Nearly impossible without calculator'
            },
            {
                'question': 'Find the derivative of f(x) = 3x³ - 2x² + 5x - 1',
                'hint': 'Power rule',
                'answer_contains': ['9x²', '4x', '5'],
                'without_textbook': 'Need formula reference'
            },
            {
                'question': 'Calculate compound interest: P=$1000, r=5%, t=3 years',
                'hint': 'A = P(1 + r)^t',
                'answer_contains': ['1157', '1158'],
                'without_calculator': 'Manual calculation very difficult'
            }
        ]
        return random.choice(problems)
        
    def generate_essay_tasks(self):
        """Generate essay writing tasks"""
        tasks = [
            {
                'question': 'Write thesis statement for essay on income inequality',
                'requirements': ['Clear argument', 'Specific focus', 'Debatable claim'],
                'without_computer': 'Must handwrite, then retype later',
                'without_internet': 'No access to sources or examples'
            },
            {
                'question': 'Create outline for 5-paragraph essay on education access',
                'requirements': ['Introduction', '3 body paragraphs', 'Conclusion'],
                'without_computer': 'Formatting will be difficult',
                'without_quiet': 'Hard to organize thoughts'
            }
        ]
        return random.choice(tasks)
        
    def generate_quiz_questions(self):
        """Generate online quiz questions"""
        questions = [
            {
                'question': 'Online quiz requires stable internet connection',
                'timer': True,
                'without_internet': 'Quiz will timeout and fail',
                'stress_factor': 'One attempt only'
            }
        ]
        return random.choice(questions)
        
    def generate_research_tasks(self):
        """Generate research paper tasks"""
        tasks = [
            {
                'question': 'Find 5 peer-reviewed sources on poverty cycles',
                'requirements': ['Academic journals', 'Recent (within 5 years)', 'Cite in APA'],
                'without_internet': 'Cannot access databases',
                'without_computer': 'Cannot save or organize sources'
            }
        ]
        return random.choice(tasks)
        
    def generate_lab_tasks(self):
        """Generate lab report tasks"""
        tasks = [
            {
                'question': 'Graph experimental data and calculate standard deviation',
                'requirements': ['Data visualization', 'Statistical analysis', 'Error bars'],
                'without_computer': 'Must draw by hand, very time consuming',
                'without_quiet': 'Calculation errors likely'
            }
        ]
        return random.choice(tasks)
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_1:
            # Try to complete with available resources
            self.attempt_completion(method='available')
        elif key == pygame.K_2:
            # Try workaround/improvise
            self.attempt_completion(method='improvise')
        elif key == pygame.K_3:
            # Skip this problem
            self.skip_problem()
        elif key == pygame.K_4:
            # Ask for help
            self.ask_for_help()
            
    def attempt_completion(self, method):
        """Try to complete current task"""
        success_chance = 0.5
        quality_modifier = 1.0
        
        # Check resource requirements
        missing_resources = []
        if hasattr(self.current_problem, 'requires_computer') and not self.has_computer:
            missing_resources.append('computer')
            success_chance -= 0.3
            quality_modifier *= 0.6
            
        if hasattr(self.current_problem, 'requires_internet') and not self.has_internet:
            missing_resources.append('internet')
            success_chance -= 0.2
            quality_modifier *= 0.7
            
        if hasattr(self.current_problem, 'requires_textbook') and not self.has_textbook:
            missing_resources.append('textbook')
            success_chance -= 0.2
            quality_modifier *= 0.7
            
        # Method modifiers
        if method == 'improvise':
            success_chance += 0.1
            quality_modifier *= 0.8
            self.frustration += 15
            
        # Environmental factors
        if self.focus_level < 50:
            success_chance -= 0.2
            quality_modifier *= 0.8
            
        # Attempt the work
        if random.random() < success_chance:
            # Success but quality varies
            grade = random.randint(60, 100) * quality_modifier
            self.current_grade = int(grade)
            self.assignments_completed.append({
                'type': self.problem_type,
                'grade': self.current_grade,
                'missing_resources': missing_resources
            })
            self.feedback = f"Completed! Grade: {self.current_grade}%"
            
            # Add stress particles for success
            for _ in range(20):
                self.stress_particles.append({
                    'x': SCREEN_WIDTH // 2,
                    'y': SCREEN_HEIGHT // 2,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-5, -2),
                    'life': 30,
                    'color': (100, 255, 100) if self.current_grade > 70 else (255, 200, 100)
                })
        else:
            # Failed
            self.feedback = f"Failed - missing: {', '.join(missing_resources)}"
            self.frustration += 20
            self.focus_level = max(0, self.focus_level - 15)
            
            # Screen glitch effect for failure
            self.screen_glitches.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'width': random.randint(50, 200),
                'height': random.randint(20, 100),
                'life': 10
            })
            
        self.feedback_timer = 3.0
        self.library_time_remaining -= 10
        
        # Move to next assignment
        self.current_assignment += 1
        if self.current_assignment < self.total_assignments:
            self.generate_assignment()
        else:
            self.end_game()
            
    def skip_problem(self):
        """Skip current problem"""
        self.assignments_completed.append({
            'type': self.problem_type,
            'grade': 0,
            'missing_resources': ['skipped']
        })
        self.feedback = "Assignment skipped - 0%"
        self.frustration += 10
        self.feedback_timer = 2.0
        
        self.current_assignment += 1
        if self.current_assignment < self.total_assignments:
            self.generate_assignment()
        else:
            self.end_game()
            
    def ask_for_help(self):
        """Try to get help"""
        help_options = [
            ("Librarian can't help with homework", 0),
            ("Classmate is also struggling", 0.1),
            ("Found helpful YouTube video", 0.3),
            ("Professor email response: 'See textbook'", -0.1)
        ]
        
        help_result, success_mod = random.choice(help_options)
        self.feedback = help_result
        self.feedback_timer = 3.0
        
        # Apply help modifier
        if success_mod > 0:
            self.focus_level = min(100, self.focus_level + 10)
        else:
            self.frustration += 10
            
        self.library_time_remaining -= 5
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update timers
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            
        if self.distraction_timer <= 0 and random.random() < 0.02:
            # Random distraction
            self.handle_distraction()
            self.distraction_timer = 5.0
        else:
            self.distraction_timer -= dt
            
        # Update library time
        self.library_time_remaining -= dt * 0.5  # Time passes
        if self.library_time_remaining <= 0:
            self.feedback = "Library closing! Must leave now."
            self.end_game()
            
        # Update particles
        for particle in self.stress_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.stress_particles.remove(particle)
                
        # Update glitches
        for glitch in self.screen_glitches[:]:
            glitch['life'] -= 1
            if glitch['life'] <= 0:
                self.screen_glitches.remove(glitch)
                
    def handle_distraction(self):
        """Handle random distraction"""
        if self.distractions:
            distraction = random.choice(self.distractions)
            self.feedback = f"DISTRACTION: {distraction}"
            self.feedback_timer = 2.0
            self.focus_level = max(0, self.focus_level - 10)
            
            # Visual effect
            for _ in range(5):
                self.stress_particles.append({
                    'x': random.randint(100, SCREEN_WIDTH - 100),
                    'y': random.randint(100, 300),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(1, 3),
                    'life': 20,
                    'color': (255, 100, 100)
                })
                
    def end_game(self):
        """End the homework struggle"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        if not self.assignments_completed:
            return {
                'stress': 30,
                'message': "No assignments completed",
                'color': (255, 100, 100)
            }
            
        # Calculate average grade
        total_grade = sum(a['grade'] for a in self.assignments_completed)
        avg_grade = total_grade / len(self.assignments_completed)
        
        if avg_grade >= 70:
            message = f"Managed to maintain {avg_grade:.0f}% average despite challenges!"
            success = True
        elif avg_grade >= 50:
            message = f"Struggling but passing with {avg_grade:.0f}% average"
            success = False
        else:
            message = f"Failing grades ({avg_grade:.0f}%) due to lack of resources"
            success = False
            
        return {
            'stress': -10 if success else 20,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the homework struggle interface"""
        if not self.active:
            return
            
        # Background - library computer lab feel
        screen.fill((245, 245, 250))
        
        # Draw glitch effects
        for glitch in self.screen_glitches:
            glitch_surf = pygame.Surface((glitch['width'], glitch['height']))
            glitch_surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            glitch_surf.set_alpha(150)
            screen.blit(glitch_surf, (glitch['x'], glitch['y']))
            
        # Title
        title = f"HOMEWORK STRUGGLE - Assignment {self.current_assignment + 1}/{self.total_assignments}"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Time remaining bar
        time_rect = pygame.Rect(50, 70, SCREEN_WIDTH - 100, 20)
        pygame.draw.rect(screen, (220, 220, 230), time_rect)
        time_fill = pygame.Rect(time_rect.x, time_rect.y,
                               int(time_rect.width * max(0, self.library_time_remaining) / 60), 20)
        time_color = (100, 200, 100) if self.library_time_remaining > 20 else (255, 200, 100) if self.library_time_remaining > 10 else (255, 100, 100)
        pygame.draw.rect(screen, time_color, time_fill)
        pygame.draw.rect(screen, (180, 180, 190), time_rect, 2)
        
        time_text = f"Library time: {int(self.library_time_remaining)} min"
        time_surf = self.small_font.render(time_text, True, (80, 80, 90))
        time_text_rect = time_surf.get_rect(center=time_rect.center)
        screen.blit(time_surf, time_text_rect)
        
        # Status panel
        status_rect = pygame.Rect(50, 110, 250, 120)
        pygame.draw.rect(screen, (255, 255, 255), status_rect)
        pygame.draw.rect(screen, (200, 200, 210), status_rect, 2)
        
        status_items = [
            ('Focus', self.focus_level, (100, 200, 100) if self.focus_level > 50 else (255, 200, 100)),
            ('Frustration', self.frustration, (255, 100, 100) if self.frustration > 50 else (255, 200, 100)),
            ('Completed', len(self.assignments_completed), (100, 150, 255))
        ]
        
        status_y = status_rect.y + 15
        for name, value, color in status_items:
            name_surf = self.small_font.render(f"{name}:", True, (80, 80, 90))
            screen.blit(name_surf, (status_rect.x + 10, status_y))
            
            if name == 'Completed':
                value_text = f"{value}/{self.total_assignments}"
            else:
                value_text = f"{int(value)}%"
            value_surf = self.font.render(value_text, True, color)
            screen.blit(value_surf, (status_rect.x + 150, status_y - 2))
            
            status_y += 35
            
        # Resource availability
        resource_rect = pygame.Rect(SCREEN_WIDTH - 300, 110, 250, 120)
        pygame.draw.rect(screen, (255, 255, 255), resource_rect)
        pygame.draw.rect(screen, (200, 200, 210), resource_rect, 2)
        
        resource_title = self.small_font.render("Available Resources:", True, (80, 80, 90))
        screen.blit(resource_title, (resource_rect.x + 10, resource_rect.y + 10))
        
        resources = [
            ('Computer', self.has_computer),
            ('Internet', self.has_internet),
            ('Textbook', self.has_textbook),
            ('Quiet Space', self.has_quiet_space)
        ]
        
        res_y = resource_rect.y + 35
        for res_name, available in resources:
            symbol = "✓" if available else "✗"
            color = (100, 200, 100) if available else (255, 100, 100)
            res_text = f"{symbol} {res_name}"
            res_surf = self.font.render(res_text, True, color)
            screen.blit(res_surf, (resource_rect.x + 20, res_y))
            res_y += 25
            
        # Current assignment
        if self.current_assignment < self.total_assignments and hasattr(self, 'current_task'):
            assign_rect = pygame.Rect(50, 250, SCREEN_WIDTH - 100, 180)
            pygame.draw.rect(screen, (250, 250, 255), assign_rect)
            pygame.draw.rect(screen, (180, 180, 200), assign_rect, 3)
            
            # Assignment type
            type_surf = self.font.render(self.problem_type, True, (60, 60, 100))
            screen.blit(type_surf, (assign_rect.x + 20, assign_rect.y + 15))
            
            # Problem description
            if 'question' in self.current_task:
                # Word wrap long questions
                question = self.current_task['question']
                words = question.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if self.problem_font.size(test_line)[0] < assign_rect.width - 40:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                    
                q_y = assign_rect.y + 50
                for line in lines[:3]:  # Max 3 lines
                    line_surf = self.problem_font.render(line, True, (40, 40, 60))
                    screen.blit(line_surf, (assign_rect.x + 20, q_y))
                    q_y += 30
                    
            # Missing resources warning
            if hasattr(self.current_problem, 'requires_computer') and not self.has_computer:
                warn_text = "⚠ No computer available - using library terminal"
                warn_surf = self.small_font.render(warn_text, True, (255, 150, 50))
                screen.blit(warn_surf, (assign_rect.x + 20, assign_rect.bottom - 40))
                
        # Options
        options_rect = pygame.Rect(50, 450, SCREEN_WIDTH - 100, 100)
        pygame.draw.rect(screen, (240, 255, 240), options_rect)
        pygame.draw.rect(screen, (150, 200, 150), options_rect, 2)
        
        options = [
            "1 - Attempt with available resources",
            "2 - Try to improvise/work around",
            "3 - Skip this assignment",
            "4 - Ask for help"
        ]
        
        opt_y = options_rect.y + 15
        for opt in options:
            opt_surf = self.font.render(opt, True, (60, 60, 80))
            screen.blit(opt_surf, (options_rect.x + 30, opt_y))
            opt_y += 22
            
        # Feedback message
        if self.feedback_timer > 0:
            feedback_rect = pygame.Rect(100, 300, SCREEN_WIDTH - 200, 60)
            
            if "Failed" in self.feedback or "0%" in self.feedback:
                feedback_color = (255, 240, 240)
                border_color = (255, 100, 100)
                text_color = (200, 50, 50)
            else:
                feedback_color = (240, 255, 240)
                border_color = (100, 200, 100)
                text_color = (50, 150, 50)
                
            pygame.draw.rect(screen, feedback_color, feedback_rect)
            pygame.draw.rect(screen, border_color, feedback_rect, 3)
            
            feedback_surf = self.font.render(self.feedback, True, text_color)
            feedback_text_rect = feedback_surf.get_rect(center=feedback_rect.center)
            screen.blit(feedback_surf, feedback_text_rect)
            
        # Draw stress particles
        for particle in self.stress_particles:
            pygame.draw.circle(screen, particle['color'],
                             (int(particle['x']), int(particle['y'])), 3)
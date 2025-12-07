"""
Foster Youth Application Form Mini-Game
Interactive form with 4 questions about age, residency, and foster history
High-quality UI with smooth transitions and validation feedback
"""

import pygame
import math
import random

class FosterYouthApplicationFormGame:
    """Interactive application form mini-game"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Form state
        self.current_question = 0
        self.total_questions = 4
        self.animation_time = 0
        self.transition_animation = False
        self.transition_direction = 1  # 1 for forward, -1 for backward
        self.transition_progress = 0

        # Questions with multiple choice options
        self.questions = [
            {
                'question': 'What is your current age?',
                'description': 'Former foster youth are eligible until age 26',
                'type': 'multiple_choice',
                'options': ['17 years old', '18 years old', '19-21 years old', '22-26 years old', 'Over 26'],
                'correct': [1, 2, 3],  # Valid ages for eligibility
                'selected': None,
                'icon': '🎂'
            },
            {
                'question': 'Where do you currently live?',
                'description': 'You must be a California resident to apply',
                'type': 'multiple_choice',
                'options': ['California', 'Another state', 'Outside the US', 'No fixed address'],
                'correct': [0],  # Must be California
                'selected': None,
                'icon': '🏠'
            },
            {
                'question': 'Were you in foster care when you turned 18?',
                'description': 'This determines your eligibility for extended coverage',
                'type': 'yes_no',
                'options': ['Yes, I was in foster care at 18', 'No, I left foster care before 18'],
                'correct': [0],  # Must have been in care at 18
                'selected': None,
                'icon': '📋'
            },
            {
                'question': 'Do you have documentation of your foster care history?',
                'description': 'Court records or agency documentation helps verify eligibility',
                'type': 'multiple_choice',
                'options': ['Yes, I have court records', 'Yes, I have agency documentation', 'No, but I can get them', 'No documentation available'],
                'correct': [0, 1, 2],  # Any form of documentation or ability to get it
                'selected': None,
                'icon': '📄'
            }
        ]

        # Fonts
        self.title_font = pygame.font.Font(None, 42)
        self.question_font = pygame.font.Font(None, 36)
        self.option_font = pygame.font.Font(None, 28)
        self.desc_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        # UI state
        self.hovered_option = None
        self.selected_option = None
        self.show_validation = False
        self.validation_message = ""
        self.validation_color = (255, 255, 255)

        # Visual effects
        self.particles = []
        self.completion_particles = []

    def start(self):
        """Start the application form"""
        self.active = True
        self.completed = False
        self.current_question = 0
        self.animation_time = 0
        self.transition_animation = False

        # Reset all questions
        for question in self.questions:
            question['selected'] = None

        # Clear visual effects
        self.particles = []
        self.completion_particles = []
        self.show_validation = False

    def update(self, dt):
        """Update game state and animations"""
        if not self.active:
            return

        self.animation_time += dt

        # Update transition animation
        if self.transition_animation:
            self.transition_progress += dt * 3  # 3 seconds for full transition
            if self.transition_progress >= 1.0:
                self.transition_animation = False
                self.transition_progress = 0

        # Update particles
        self.update_particles(dt)

        # Hide validation message after delay
        if self.show_validation:
            self.validation_timer = getattr(self, 'validation_timer', 0) + dt
            if self.validation_timer > 3.0:
                self.show_validation = False
                self.validation_timer = 0

    def update_particles(self, dt):
        """Update particle effects"""
        # Update question transition particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vel_x'] * dt
            particle['y'] += particle['vel_y'] * dt
            particle['vel_y'] += 150 * dt  # Gravity

            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Update completion particles
        for particle in self.completion_particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vel_x'] * dt
            particle['y'] += particle['vel_y'] * dt
            particle['alpha'] = max(0, int(255 * particle['life']))

            if particle['life'] <= 0:
                self.completion_particles.remove(particle)

    def handle_click(self, pos):
        """Handle mouse clicks on form options"""
        if not self.active or self.transition_animation:
            return

        mx, my = pos

        # Check clicks on options
        for i, option_rect in enumerate(self.get_option_rects()):
            if option_rect.collidepoint(mx, my):
                self.select_option(i)

        # Check navigation buttons
        nav_rects = self.get_navigation_rects()
        if nav_rects['next'].collidepoint(mx, my) and self.can_proceed():
            self.next_question()
        elif nav_rects['prev'].collidepoint(mx, my) and self.current_question > 0:
            self.previous_question()

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active or self.transition_animation:
            return

        mx, my = pos
        self.hovered_option = None

        # Check hover on options
        for i, option_rect in enumerate(self.get_option_rects()):
            if option_rect.collidepoint(mx, my):
                self.hovered_option = i

    def select_option(self, index):
        """Select an option for the current question"""
        current_q = self.questions[self.current_question]
        current_q['selected'] = index

        # Create selection particles
        option_rect = self.get_option_rects()[index]
        for _ in range(10):
            self.particles.append({
                'x': option_rect.centerx + random.randint(-50, 50),
                'y': option_rect.centery,
                'vel_x': random.uniform(-50, 50),
                'vel_y': random.uniform(-100, -50),
                'life': random.uniform(1.0, 2.0),
                'color': (100, 200, 255)
            })

    def can_proceed(self):
        """Check if current question is answered and can proceed"""
        return self.questions[self.current_question]['selected'] is not None

    def next_question(self):
        """Move to next question with validation"""
        current_q = self.questions[self.current_question]

        # Validate answer
        if current_q['selected'] not in current_q['correct']:
            self.show_validation = True
            self.validation_message = "This answer may affect your eligibility. Please review."
            self.validation_color = (255, 200, 100)
            self.validation_timer = 0

        if self.current_question < self.total_questions - 1:
            self.start_transition(1)
            self.current_question += 1
        else:
            self.complete_form()

    def previous_question(self):
        """Move to previous question"""
        if self.current_question > 0:
            self.start_transition(-1)
            self.current_question -= 1

    def start_transition(self, direction):
        """Start the question transition animation"""
        self.transition_animation = True
        self.transition_direction = direction
        self.transition_progress = 0

    def complete_form(self):
        """Complete the application form"""
        # Check overall eligibility
        eligible = True
        for i, question in enumerate(self.questions):
            if question['selected'] not in question['correct']:
                eligible = False

        # Create completion particles
        self.create_completion_particles(eligible)

        # Set completion state
        self.completed = True
        self.active = False

        # Notify objective manager
        if self.objective_manager:
            if eligible:
                message = "Application Complete! You appear eligible for former foster youth coverage."
                color = (100, 255, 100)
            else:
                message = "Application submitted. Some answers may require additional documentation."
                color = (255, 200, 100)

            self.objective_manager.show_notification("Form Submitted", message, color)

    def create_completion_particles(self, eligible):
        """Create particles for form completion"""
        color = (100, 255, 100) if eligible else (255, 200, 100)
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            self.completion_particles.append({
                'x': center_x,
                'y': center_y,
                'vel_x': math.cos(angle) * speed,
                'vel_y': math.sin(angle) * speed,
                'life': random.uniform(2.0, 4.0),
                'color': color,
                'alpha': 255
            })

    def get_option_rects(self):
        """Get rectangles for current question options"""
        current_q = self.questions[self.current_question]
        rects = []

        start_y = 350
        option_height = 60
        option_margin = 15

        for i, option in enumerate(current_q['options']):
            y = start_y + (option_height + option_margin) * i
            rects.append(pygame.Rect(300, y, 680, option_height))

        return rects

    def get_navigation_rects(self):
        """Get rectangles for navigation buttons"""
        button_width = 120
        button_height = 40
        button_y = self.SCREEN_HEIGHT - 80

        return {
            'prev': pygame.Rect(200, button_y, button_width, button_height),
            'next': pygame.Rect(self.SCREEN_WIDTH - 320, button_y, button_width, button_height)
        }

    def draw(self, screen):
        """Draw the application form interface"""
        if not self.active:
            return

        # Background gradient
        self.draw_gradient_background(screen)

        # Header
        self.draw_header(screen)

        # Progress indicator
        self.draw_progress_indicator(screen)

        # Current question (with transition effect)
        if not self.transition_animation:
            self.draw_current_question(screen)
        else:
            self.draw_transition_questions(screen)

        # Navigation
        self.draw_navigation(screen)

        # Validation message
        if self.show_validation:
            self.draw_validation_message(screen)

        # Particles
        self.draw_particles(screen)

    def draw_gradient_background(self, screen):
        """Draw professional gradient background"""
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = (
                int(20 + progress * 15),
                int(35 + progress * 20),
                int(55 + progress * 25)
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

    def draw_header(self, screen):
        """Draw the form header"""
        title = "Former Foster Youth Medi-Cal Application"
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 60))
        screen.blit(title_surf, title_rect)

        subtitle = "Please answer the following questions to determine eligibility"
        subtitle_surf = self.desc_font.render(subtitle, True, (200, 200, 200))
        subtitle_rect = subtitle_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 90))
        screen.blit(subtitle_surf, subtitle_rect)

    def draw_progress_indicator(self, screen):
        """Draw the form progress bar"""
        bar_width = 600
        bar_height = 8
        bar_x = (self.SCREEN_WIDTH - bar_width) // 2
        bar_y = 120

        # Background
        pygame.draw.rect(screen, (60, 60, 80), (bar_x, bar_y, bar_width, bar_height), 0, 4)

        # Progress fill
        progress = (self.current_question + 1) / self.total_questions
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, (100, 200, 255), (bar_x, bar_y, fill_width, bar_height), 0, 4)

        # Step indicators
        step_width = bar_width // self.total_questions
        for i in range(self.total_questions):
            step_x = bar_x + i * step_width + step_width // 2
            step_y = bar_y + bar_height // 2

            if i <= self.current_question:
                color = (100, 200, 255)
            else:
                color = (80, 80, 100)

            pygame.draw.circle(screen, color, (step_x, step_y), 8)

            # Step number
            num_surf = self.small_font.render(str(i + 1), True, (255, 255, 255))
            num_rect = num_surf.get_rect(center=(step_x, step_y))
            screen.blit(num_surf, num_rect)

        # Progress text
        progress_text = f"Question {self.current_question + 1} of {self.total_questions}"
        progress_surf = self.desc_font.render(progress_text, True, (180, 180, 180))
        progress_rect = progress_surf.get_rect(center=(self.SCREEN_WIDTH // 2, bar_y + 35))
        screen.blit(progress_surf, progress_rect)

    def draw_current_question(self, screen):
        """Draw the current question and options"""
        current_q = self.questions[self.current_question]

        # Question icon
        icon_surf = self.title_font.render(current_q['icon'], True, (255, 255, 255))
        icon_rect = icon_surf.get_rect(center=(200, 220))
        screen.blit(icon_surf, icon_rect)

        # Question text
        question_surf = self.question_font.render(current_q['question'], True, (255, 255, 255))
        question_rect = question_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        screen.blit(question_surf, question_rect)

        # Description
        desc_surf = self.desc_font.render(current_q['description'], True, (180, 180, 200))
        desc_rect = desc_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 230))
        screen.blit(desc_surf, desc_rect)

        # Options
        option_rects = self.get_option_rects()
        for i, (option, rect) in enumerate(zip(current_q['options'], option_rects)):
            self.draw_option(screen, option, rect, i, current_q)

    def draw_transition_questions(self, screen):
        """Draw questions during transition animation"""
        # Calculate positions based on transition progress
        offset = int(self.SCREEN_WIDTH * self.transition_progress * self.transition_direction)

        # Draw current question sliding out
        current_surface = pygame.Surface((self.SCREEN_WIDTH, 400))
        current_surface.set_colorkey((0, 0, 0))
        self.draw_question_on_surface(current_surface, self.current_question - self.transition_direction)
        screen.blit(current_surface, (-offset, 180))

        # Draw next question sliding in
        if 0 <= self.current_question < len(self.questions):
            next_surface = pygame.Surface((self.SCREEN_WIDTH, 400))
            next_surface.set_colorkey((0, 0, 0))
            self.draw_question_on_surface(next_surface, self.current_question)
            screen.blit(next_surface, (self.SCREEN_WIDTH - offset, 180))

    def draw_question_on_surface(self, surface, question_index):
        """Draw a question on a surface for transition effects"""
        if not (0 <= question_index < len(self.questions)):
            return

        question = self.questions[question_index]

        # Question text (simplified for transition)
        question_surf = self.question_font.render(question['question'], True, (255, 255, 255))
        question_rect = question_surf.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        surface.blit(question_surf, question_rect)

    def draw_option(self, screen, option_text, rect, index, question):
        """Draw a single option with hover and selection effects"""
        # Determine colors based on state
        is_selected = question['selected'] == index
        is_hovered = self.hovered_option == index

        if is_selected:
            bg_color = (80, 150, 80)
            border_color = (120, 200, 120)
            text_color = (255, 255, 255)
        elif is_hovered:
            bg_color = (70, 70, 120)
            border_color = (120, 120, 180)
            text_color = (255, 255, 255)
        else:
            bg_color = (50, 50, 70)
            border_color = (100, 100, 120)
            text_color = (200, 200, 200)

        # Draw option background
        pygame.draw.rect(screen, bg_color, rect, 0, 8)
        pygame.draw.rect(screen, border_color, rect, 2, 8)

        # Option text
        text_surf = self.option_font.render(option_text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

        # Selection indicator
        if is_selected:
            indicator_surf = self.option_font.render("✓", True, (100, 255, 100))
            indicator_rect = indicator_surf.get_rect(center=(rect.right - 30, rect.centery))
            screen.blit(indicator_surf, indicator_rect)

    def draw_navigation(self, screen):
        """Draw navigation buttons"""
        nav_rects = self.get_navigation_rects()

        # Previous button
        if self.current_question > 0:
            prev_color = (60, 60, 80)
            prev_text_color = (255, 255, 255)
        else:
            prev_color = (40, 40, 50)
            prev_text_color = (100, 100, 100)

        pygame.draw.rect(screen, prev_color, nav_rects['prev'], 0, 5)
        pygame.draw.rect(screen, (100, 100, 120), nav_rects['prev'], 2, 5)

        prev_surf = self.desc_font.render("← Previous", True, prev_text_color)
        prev_rect = prev_surf.get_rect(center=nav_rects['prev'].center)
        screen.blit(prev_surf, prev_rect)

        # Next button
        if self.can_proceed():
            if self.current_question < self.total_questions - 1:
                next_text = "Next →"
                next_color = (60, 120, 60)
            else:
                next_text = "Submit"
                next_color = (80, 150, 80)
            next_text_color = (255, 255, 255)
        else:
            next_text = "Next →"
            next_color = (40, 40, 50)
            next_text_color = (100, 100, 100)

        pygame.draw.rect(screen, next_color, nav_rects['next'], 0, 5)
        pygame.draw.rect(screen, (100, 100, 120), nav_rects['next'], 2, 5)

        next_surf = self.desc_font.render(next_text, True, next_text_color)
        next_rect = next_surf.get_rect(center=nav_rects['next'].center)
        screen.blit(next_surf, next_rect)

    def draw_validation_message(self, screen):
        """Draw validation feedback message"""
        message_surf = self.desc_font.render(self.validation_message, True, self.validation_color)
        message_rect = message_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 40))

        # Background for message
        bg_rect = message_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect, 0, 5)
        screen.blit(message_surf, message_rect)

    def draw_particles(self, screen):
        """Draw all particle effects"""
        # Selection particles
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            if alpha > 0:
                color = (*particle['color'], min(alpha, 255))
                size = max(1, int(particle['life'] * 6))
                pygame.draw.circle(screen, color[:3], (int(particle['x']), int(particle['y'])), size)

        # Completion particles
        for particle in self.completion_particles:
            if particle['alpha'] > 0:
                color = (*particle['color'], particle['alpha'])
                size = max(1, int(particle['life'] * 4))
                pygame.draw.circle(screen, color[:3], (int(particle['x']), int(particle['y'])), size)

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.current_question > 0:
                self.previous_question()
            elif event.key == pygame.K_RIGHT and self.can_proceed():
                self.next_question()

    def get_results(self):
        """Return results for the objective system"""
        eligible = all(
            question['selected'] in question['correct']
            for question in self.questions
            if question['selected'] is not None
        )

        return {
            'completed': self.completed,
            'eligible': eligible,
            'message': "Application form completed successfully.",
            'color': (100, 255, 100) if eligible else (255, 200, 100)
        }

    def render(self, screen):
        """Render method for compatibility with activity system"""
        self.draw(screen)
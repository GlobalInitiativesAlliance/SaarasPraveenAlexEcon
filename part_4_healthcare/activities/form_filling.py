"""
Medi-Cal Former Foster Youth Program Application Form
Quick 4-question form to reapply for coverage
"""
import pygame

class MediCalFormGame:
    """Fill out a short form with 4 questions about age, residency, and foster history"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Form questions
        self.questions = [
            {
                'question': 'Are you between 18 and 26 years old?',
                'options': ['Yes', 'No'],
                'correct': 0,
                'answer': None
            },
            {
                'question': 'Are you a California resident?',
                'options': ['Yes', 'No'],
                'correct': 0,
                'answer': None
            },
            {
                'question': 'Were you in foster care on your 18th birthday?',
                'options': ['Yes', 'No', 'Not sure'],
                'correct': 0,
                'answer': None
            },
            {
                'question': 'Do you currently have other health insurance?',
                'options': ['Yes', 'No'],
                'correct': 1,
                'answer': None
            }
        ]

        self.current_question = 0
        self.form_submitted = False
        self.approval_timer = 0
        self.show_approval = False

        # UI elements
        self.question_rect = pygame.Rect(240, 150, 800, 100)
        self.option_rects = []
        self.submit_button = pygame.Rect(540, 550, 200, 60)

        # Colors
        self.BG_COLOR = (240, 240, 245)
        self.FORM_COLOR = (255, 255, 255)
        self.BUTTON_COLOR = (100, 150, 200)
        self.BUTTON_HOVER = (120, 170, 220)
        self.TEXT_COLOR = (30, 30, 40)
        self.CORRECT_COLOR = (100, 200, 100)

    def create_option_rects(self):
        """Create rectangles for answer options"""
        self.option_rects = []
        num_options = len(self.questions[self.current_question]['options'])

        for i in range(num_options):
            x = 340 + (i * 200)
            y = 300
            rect = pygame.Rect(x, y, 180, 50)
            self.option_rects.append(rect)

    def handle_event(self, event):
        """Handle form interaction events"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            if not self.form_submitted:
                # Check option clicks
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.questions[self.current_question]['answer'] = i

                        # Auto-advance to next question
                        if self.current_question < len(self.questions) - 1:
                            self.current_question += 1
                            self.create_option_rects()
                        break

                # Check submit button
                if self.submit_button.collidepoint(mouse_pos):
                    # Check if all questions answered
                    all_answered = all(q['answer'] is not None for q in self.questions)
                    if all_answered:
                        self.form_submitted = True
                        self.approval_timer = 120  # 2 seconds at 60 FPS

        elif event.type == pygame.KEYDOWN:
            # Allow keyboard navigation
            if event.key >= pygame.K_1 and event.key <= pygame.K_3:
                option_index = event.key - pygame.K_1
                if option_index < len(self.questions[self.current_question]['options']):
                    self.questions[self.current_question]['answer'] = option_index

                    if self.current_question < len(self.questions) - 1:
                        self.current_question += 1
                        self.create_option_rects()

        return True

    def update(self, dt):
        """Update form state"""
        if not self.active:
            return

        if self.form_submitted and self.approval_timer > 0:
            self.approval_timer -= 1
            if self.approval_timer == 60:
                self.show_approval = True
            elif self.approval_timer == 0:
                self.completed = True
                # Activity completion handled by interior callback

    def render(self, screen):
        """Render the form interface"""
        if not self.active:
            return

        # Background overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)
        overlay.fill(self.BG_COLOR)
        screen.blit(overlay, (0, 0))

        # Form container
        form_rect = pygame.Rect(190, 100, 900, 520)
        pygame.draw.rect(screen, self.FORM_COLOR, form_rect)
        pygame.draw.rect(screen, (180, 180, 190), form_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Medi-Cal Former Foster Youth Program", True, self.TEXT_COLOR)
        screen.blit(title_text, (self.SCREEN_WIDTH//2 - title_text.get_width()//2, 120))

        # ESC hint
        esc_font = pygame.font.Font(None, 24)
        esc_text = esc_font.render("Press ESC to exit", True, (150, 150, 150))
        screen.blit(esc_text, (20, self.SCREEN_HEIGHT - 40))

        if not self.show_approval:
            # Progress indicator
            progress_font = pygame.font.Font(None, 24)
            progress_text = progress_font.render(
                f"Question {self.current_question + 1} of {len(self.questions)}",
                True, (100, 100, 110)
            )
            screen.blit(progress_text, (self.SCREEN_WIDTH//2 - progress_text.get_width()//2, 170))

            # Current question
            question_font = pygame.font.Font(None, 32)
            question = self.questions[self.current_question]
            q_text = question_font.render(question['question'], True, self.TEXT_COLOR)
            screen.blit(q_text, (self.SCREEN_WIDTH//2 - q_text.get_width()//2, 220))

            # Answer options
            option_font = pygame.font.Font(None, 28)
            for i, (rect, option) in enumerate(zip(self.option_rects, question['options'])):
                # Determine button color
                color = self.BUTTON_COLOR
                if question['answer'] == i:
                    color = self.CORRECT_COLOR
                else:
                    mouse_pos = pygame.mouse.get_pos()
                    if rect.collidepoint(mouse_pos):
                        color = self.BUTTON_HOVER

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (80, 80, 90), rect, 2)

                option_text = option_font.render(option, True, (255, 255, 255))
                text_x = rect.centerx - option_text.get_width()//2
                text_y = rect.centery - option_text.get_height()//2
                screen.blit(option_text, (text_x, text_y))

            # Show previous answers
            if self.current_question > 0:
                small_font = pygame.font.Font(None, 20)
                y_offset = 380
                for i in range(self.current_question):
                    q = self.questions[i]
                    if q['answer'] is not None:
                        answer_text = f"✓ {q['question'][:40]}... - {q['options'][q['answer']]}"
                        text = small_font.render(answer_text, True, (100, 150, 100))
                        screen.blit(text, (300, y_offset))
                        y_offset += 25

            # Submit button (only show when all answered)
            all_answered = all(q['answer'] is not None for q in self.questions)
            if all_answered:
                mouse_pos = pygame.mouse.get_pos()
                btn_color = self.BUTTON_HOVER if self.submit_button.collidepoint(mouse_pos) else self.BUTTON_COLOR
                pygame.draw.rect(screen, btn_color, self.submit_button)
                pygame.draw.rect(screen, (60, 60, 70), self.submit_button, 2)

                submit_text = option_font.render("SUBMIT APPLICATION", True, (255, 255, 255))
                text_x = self.submit_button.centerx - submit_text.get_width()//2
                text_y = self.submit_button.centery - submit_text.get_height()//2
                screen.blit(submit_text, (text_x, text_y))

        else:
            # Show approval message
            approval_rect = pygame.Rect(340, 250, 600, 200)
            pygame.draw.rect(screen, (100, 200, 100), approval_rect)
            pygame.draw.rect(screen, (50, 50, 50), approval_rect, 3)

            approval_font = pygame.font.Font(None, 48)
            approval_text = approval_font.render("APPLICATION APPROVED!", True, (255, 255, 255))
            screen.blit(approval_text, (self.SCREEN_WIDTH//2 - approval_text.get_width()//2, 280))

            detail_font = pygame.font.Font(None, 28)
            lines = [
                "You qualify for the Former Foster Youth program!",
                "Coverage will be reinstated in 2 weeks.",
                "Keep your confirmation number: FFY-2024-1847"
            ]

            y = 340
            for line in lines:
                line_text = detail_font.render(line, True, (255, 255, 255))
                screen.blit(line_text, (self.SCREEN_WIDTH//2 - line_text.get_width()//2, y))
                y += 35

    def start(self):
        """Start the form filling mini-game"""
        self.active = True
        self.completed = False
        self.current_question = 0
        self.form_submitted = False
        self.show_approval = False
        self.approval_timer = 0

        # Reset answers
        for q in self.questions:
            q['answer'] = None

        self.create_option_rects()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Draw method (alias for render) - standard interface"""
        self.render(screen)

    def handle_key(self, key):
        """Handle keyboard input - ESC to exit"""
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False
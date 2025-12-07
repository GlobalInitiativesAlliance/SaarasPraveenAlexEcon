"""
Enhanced Community Health Clinic Interior
Professional medical facility interface with realistic medical environment and interactive elements
"""
import pygame
import math
import random

class EnhancedClinicInterior:
    def __init__(self, objective_manager, building_pos, room_data):
        self.objective_manager = objective_manager
        self.building_pos = building_pos
        self.room_data = room_data
        self.active = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Clinic state
        self.current_objective = None
        self.documents_checked = []
        self.form_progress = 0
        self.application_status = "pending"

        # Required documents for Medi-Cal application
        self.required_documents = [
            {
                "name": "Photo ID",
                "description": "Driver's License or State ID",
                "required": True,
                "status": "have",
                "icon": "🆔"
            },
            {
                "name": "Previous Medi-Cal Card",
                "description": "Shows prior coverage history",
                "required": True,
                "status": "have",
                "icon": "💳"
            },
            {
                "name": "Proof of Income",
                "description": "Pay stubs or employment letter",
                "required": True,
                "status": "have",
                "icon": "💰"
            },
            {
                "name": "Proof of Foster Care",
                "description": "Documentation from social services",
                "required": True,
                "status": "have",
                "icon": "📋"
            }
        ]

        # Form questions for Former Foster Youth application
        self.form_questions = [
            {
                "question": "What is your current age?",
                "options": ["Under 18", "18-21", "21-26", "Over 26"],
                "correct": 2,  # 21-26
                "explanation": "Former foster youth are eligible until age 26"
            },
            {
                "question": "How long have you lived in California?",
                "options": ["Less than 1 year", "1-2 years", "More than 2 years", "All my life"],
                "correct": 3,  # All my life
                "explanation": "Residency requirement for state benefits"
            },
            {
                "question": "When did you age out of foster care?",
                "options": ["Never in care", "Before age 18", "At age 18", "After age 18"],
                "correct": 2,  # At age 18
                "explanation": "Eligibility based on aging out at 18"
            },
            {
                "question": "Do you have any other health insurance?",
                "options": ["Yes, through employer", "Yes, through family", "No coverage", "Not sure"],
                "correct": 2,  # No coverage
                "explanation": "Medi-Cal is for those without other coverage"
            }
        ]

        self.current_question = 0
        self.form_completed = False

        # Animation state
        self.time = 0
        self.notification_time = 0
        self.success_particles = []

        # UI Layout
        self.setup_clinic_layout()

        # Professional medical color scheme
        self.colors = {
            'medical_blue': (70, 130, 180),
            'medical_green': (85, 170, 85),
            'medical_white': (248, 250, 252),
            'text_dark': (33, 37, 41),
            'text_light': (108, 117, 125),
            'success_green': (40, 167, 69),
            'warning_orange': (255, 193, 7),
            'error_red': (220, 53, 69),
            'accent_teal': (23, 162, 184),
            'background': (245, 248, 250),
            'card_white': (255, 255, 255),
            'shadow': (0, 0, 0, 10)
        }

        # Medical facility fonts
        self.fonts = {
            'title': pygame.font.Font(None, 56),
            'subtitle': pygame.font.Font(None, 36),
            'header': pygame.font.Font(None, 32),
            'body': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 20),
            'tiny': pygame.font.Font(None, 16)
        }

        # Interactive elements
        self.interactive_areas = {}
        self.setup_interactive_areas()

    def setup_clinic_layout(self):
        """Setup medical clinic UI layout"""
        # Header with clinic branding
        self.header_area = pygame.Rect(0, 0, self.SCREEN_WIDTH, 100)

        # Main content area
        self.content_area = pygame.Rect(50, 110, self.SCREEN_WIDTH - 100, self.SCREEN_HEIGHT - 160)

        # Document checklist area (left side)
        self.checklist_area = pygame.Rect(50, 110, 400, 300)

        # Form area (right side)
        self.form_area = pygame.Rect(470, 110, 760, 500)

        # Progress area (bottom)
        self.progress_area = pygame.Rect(50, 430, 400, 180)

    def setup_interactive_areas(self):
        """Setup interactive clickable areas"""
        self.interactive_areas = {
            'document_check': pygame.Rect(50, 110, 400, 300),
            'application_form': pygame.Rect(470, 110, 760, 500),
            'reception_desk': pygame.Rect(self.SCREEN_WIDTH - 200, 620, 180, 80)
        }

    def create_particle(self, x, y, color):
        """Create success particle effect"""
        return {
            'x': x,
            'y': y,
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-5, -1),
            'color': color,
            'life': 2.0,
            'max_life': 2.0,
            'size': random.uniform(3, 8)
        }

    def update_particles(self, dt):
        """Update particle animations"""
        for particle in self.success_particles[:]:
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            particle['vy'] += 200 * dt  # Gravity
            particle['life'] -= dt

            if particle['life'] <= 0:
                self.success_particles.remove(particle)

    def draw_clinic_header(self, surface):
        """Draw professional clinic header"""
        # Background gradient
        for y in range(self.header_area.height):
            progress = y / self.header_area.height
            r = int(70 + (30 * progress))
            g = int(130 + (30 * progress))
            b = int(180 + (20 * progress))
            pygame.draw.line(surface, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

        # Medical cross logo
        logo_rect = pygame.Rect(30, 20, 60, 60)
        pygame.draw.ellipse(surface, (255, 255, 255), logo_rect)
        pygame.draw.ellipse(surface, self.colors['medical_green'], logo_rect, width=4)

        # Cross symbol
        cross_color = self.colors['medical_green']
        pygame.draw.line(surface, cross_color,
                        (logo_rect.centerx, logo_rect.centery - 20),
                        (logo_rect.centerx, logo_rect.centery + 20), width=6)
        pygame.draw.line(surface, cross_color,
                        (logo_rect.centerx - 20, logo_rect.centery),
                        (logo_rect.centerx + 20, logo_rect.centery), width=6)

        # Clinic name
        title_text = self.fonts['title'].render("Community Health Center", True, (255, 255, 255))
        surface.blit(title_text, (110, 25))

        subtitle_text = self.fonts['body'].render("Medi-Cal Enrollment Services", True, (255, 255, 255, 200))
        surface.blit(subtitle_text, (110, 65))

        # Current objective indicator
        if self.current_objective:
            obj_text = f"Current: {self.current_objective}"
            obj_surface = self.fonts['small'].render(obj_text, True, (255, 255, 255))
            surface.blit(obj_surface, (self.SCREEN_WIDTH - 300, 30))

        # Clinic hours
        hours_text = "Open: Mon-Fri 8AM-6PM"
        hours_surface = self.fonts['tiny'].render(hours_text, True, (255, 255, 255, 180))
        surface.blit(hours_surface, (self.SCREEN_WIDTH - 200, 55))

    def draw_document_checklist(self, surface):
        """Draw interactive document checklist"""
        # Panel background
        pygame.draw.rect(surface, self.colors['card_white'], self.checklist_area, border_radius=12)
        pygame.draw.rect(surface, self.colors['medical_blue'], self.checklist_area, width=2, border_radius=12)

        # Header
        header_text = self.fonts['header'].render("Required Documents", True, self.colors['text_dark'])
        surface.blit(header_text, (self.checklist_area.x + 20, self.checklist_area.y + 20))

        # Document list
        y_offset = 60
        for i, doc in enumerate(self.required_documents):
            doc_y = self.checklist_area.y + y_offset

            # Checkbox
            checkbox_rect = pygame.Rect(self.checklist_area.x + 20, doc_y, 20, 20)
            checkbox_color = self.colors['success_green'] if doc['status'] == 'have' else self.colors['text_light']

            pygame.draw.rect(surface, (255, 255, 255), checkbox_rect)
            pygame.draw.rect(surface, checkbox_color, checkbox_rect, width=2)

            if doc['status'] == 'have':
                # Checkmark
                check_points = [
                    (checkbox_rect.x + 4, checkbox_rect.centery),
                    (checkbox_rect.x + 8, checkbox_rect.bottom - 6),
                    (checkbox_rect.right - 4, checkbox_rect.y + 4)
                ]
                pygame.draw.lines(surface, self.colors['success_green'], False, check_points, 2)

            # Document icon
            icon_text = self.fonts['body'].render(doc['icon'], True, self.colors['text_dark'])
            surface.blit(icon_text, (self.checklist_area.x + 50, doc_y - 2))

            # Document name
            name_text = self.fonts['body'].render(doc['name'], True, self.colors['text_dark'])
            surface.blit(name_text, (self.checklist_area.x + 80, doc_y))

            # Description
            desc_text = self.fonts['small'].render(doc['description'], True, self.colors['text_light'])
            surface.blit(desc_text, (self.checklist_area.x + 80, doc_y + 20))

            y_offset += 55

        # All documents status
        all_have_docs = all(doc['status'] == 'have' for doc in self.required_documents)
        status_text = "✓ All documents ready!" if all_have_docs else "❌ Missing documents"
        status_color = self.colors['success_green'] if all_have_docs else self.colors['error_red']

        status_surface = self.fonts['body'].render(status_text, True, status_color)
        surface.blit(status_surface, (self.checklist_area.x + 20, self.checklist_area.bottom - 40))

    def draw_application_form(self, surface):
        """Draw interactive application form"""
        # Panel background
        pygame.draw.rect(surface, self.colors['card_white'], self.form_area, border_radius=12)
        pygame.draw.rect(surface, self.colors['medical_blue'], self.form_area, width=2, border_radius=12)

        # Header
        header_text = self.fonts['header'].render("Former Foster Youth Medi-Cal Application", True, self.colors['text_dark'])
        surface.blit(header_text, (self.form_area.x + 20, self.form_area.y + 20))

        # Progress indicator
        progress_text = f"Question {self.current_question + 1} of {len(self.form_questions)}"
        progress_surface = self.fonts['body'].render(progress_text, True, self.colors['text_light'])
        surface.blit(progress_surface, (self.form_area.right - 200, self.form_area.y + 25))

        if not self.form_completed and self.current_question < len(self.form_questions):
            question = self.form_questions[self.current_question]

            # Question
            question_text = question['question']
            question_surface = self.fonts['subtitle'].render(question_text, True, self.colors['text_dark'])
            surface.blit(question_surface, (self.form_area.x + 20, self.form_area.y + 70))

            # Answer options
            y_offset = 120
            for i, option in enumerate(question['options']):
                option_y = self.form_area.y + y_offset

                # Option button
                button_rect = pygame.Rect(self.form_area.x + 30, option_y, self.form_area.width - 60, 50)
                button_color = self.colors['card_white']

                # Hover effect
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    button_color = (240, 248, 255)

                pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
                pygame.draw.rect(surface, self.colors['text_light'], button_rect, width=1, border_radius=8)

                # Option letter
                letter = chr(ord('A') + i)
                letter_text = self.fonts['body'].render(f"{letter}.", True, self.colors['medical_blue'])
                surface.blit(letter_text, (button_rect.x + 15, button_rect.y + 15))

                # Option text
                option_text = self.fonts['body'].render(option, True, self.colors['text_dark'])
                surface.blit(option_text, (button_rect.x + 45, button_rect.y + 15))

                y_offset += 70

        elif self.form_completed:
            # Application complete message
            complete_text = "✓ Application Completed Successfully!"
            complete_surface = self.fonts['subtitle'].render(complete_text, True, self.colors['success_green'])
            complete_rect = complete_surface.get_rect(center=(self.form_area.centerx, self.form_area.y + 100))
            surface.blit(complete_surface, complete_rect)

            # Approval message
            approval_lines = [
                "Congratulations! Your application has been approved instantly.",
                "",
                "As a former foster youth, you qualify for immediate coverage",
                "under California's Extended Foster Care benefits.",
                "",
                "However, it will take 2 weeks for your new card to arrive",
                "and coverage to be fully reinstated."
            ]

            y_offset = 150
            for line in approval_lines:
                if line:
                    line_color = self.colors['text_dark']
                    if "2 weeks" in line:
                        line_color = self.colors['warning_orange']

                    line_surface = self.fonts['body'].render(line, True, line_color)
                    line_rect = line_surface.get_rect(center=(self.form_area.centerx, self.form_area.y + y_offset))
                    surface.blit(line_surface, line_rect)

                y_offset += 30

    def draw_progress_panel(self, surface):
        """Draw application progress panel"""
        # Panel background
        pygame.draw.rect(surface, self.colors['card_white'], self.progress_area, border_radius=12)
        pygame.draw.rect(surface, self.colors['medical_blue'], self.progress_area, width=2, border_radius=12)

        # Header
        header_text = self.fonts['header'].render("Application Progress", True, self.colors['text_dark'])
        surface.blit(header_text, (self.progress_area.x + 20, self.progress_area.y + 20))

        # Progress steps
        steps = [
            ("Document Check", len(self.documents_checked) >= 4),
            ("Form Submission", self.form_completed),
            ("Application Review", self.form_completed),
            ("Approval Notice", self.form_completed)
        ]

        y_offset = 60
        for i, (step_name, completed) in enumerate(steps):
            step_y = self.progress_area.y + y_offset

            # Step number circle
            circle_pos = (self.progress_area.x + 30, step_y + 10)
            circle_color = self.colors['success_green'] if completed else self.colors['text_light']

            pygame.draw.circle(surface, circle_color, circle_pos, 12)
            pygame.draw.circle(surface, (255, 255, 255), circle_pos, 12, width=2)

            # Step number
            number_text = self.fonts['small'].render(str(i + 1), True, (255, 255, 255))
            number_rect = number_text.get_rect(center=circle_pos)
            surface.blit(number_text, number_rect)

            # Step name
            step_surface = self.fonts['body'].render(step_name, True, self.colors['text_dark'])
            surface.blit(step_surface, (self.progress_area.x + 60, step_y + 2))

            # Status
            status_text = "✓ Complete" if completed else "○ Pending"
            status_color = self.colors['success_green'] if completed else self.colors['text_light']
            status_surface = self.fonts['small'].render(status_text, True, status_color)
            surface.blit(status_surface, (self.progress_area.x + 200, step_y + 5))

            y_offset += 30

    def handle_event(self, event):
        """Handle clinic interior interactions"""
        if not self.active:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Handle document checklist clicks
            if self.checklist_area.collidepoint(mouse_pos):
                self.handle_document_check()

            # Handle form question clicks
            elif self.form_area.collidepoint(mouse_pos) and not self.form_completed:
                self.handle_form_click(mouse_pos)

        elif event.type == pygame.KEYDOWN:
            if not self.form_completed and self.current_question < len(self.form_questions):
                # Handle A, B, C, D key presses for form
                if pygame.K_a <= event.key <= pygame.K_d:
                    option_index = event.key - pygame.K_a
                    if option_index < len(self.form_questions[self.current_question]['options']):
                        self.handle_form_answer(option_index)

        return True

    def handle_document_check(self):
        """Handle document checking interaction"""
        if len(self.documents_checked) < 4:
            self.documents_checked.append(f"doc_{len(self.documents_checked)}")

            # Create success particles
            for _ in range(10):
                particle = self.create_particle(
                    self.checklist_area.centerx + random.uniform(-50, 50),
                    self.checklist_area.centery + random.uniform(-50, 50),
                    self.colors['success_green']
                )
                self.success_particles.append(particle)

            # Check if all documents are verified
            if len(self.documents_checked) >= 4:
                if self.objective_manager:
                    self.objective_manager.complete_objective("clinic_checklist")

    def handle_form_click(self, mouse_pos):
        """Handle form option clicks"""
        if self.current_question >= len(self.form_questions):
            return

        # Calculate which option was clicked
        form_start_y = self.form_area.y + 120
        option_height = 70

        for i in range(len(self.form_questions[self.current_question]['options'])):
            option_y = form_start_y + (i * option_height)
            option_rect = pygame.Rect(self.form_area.x + 30, option_y, self.form_area.width - 60, 50)

            if option_rect.collidepoint(mouse_pos):
                self.handle_form_answer(i)
                break

    def handle_form_answer(self, answer_index):
        """Handle form answer selection"""
        question = self.form_questions[self.current_question]

        # Create feedback particles
        is_correct = (answer_index == question['correct'])
        particle_color = self.colors['success_green'] if is_correct else self.colors['warning_orange']

        for _ in range(8):
            particle = self.create_particle(
                self.form_area.centerx + random.uniform(-100, 100),
                self.form_area.y + 200 + random.uniform(-30, 30),
                particle_color
            )
            self.success_particles.append(particle)

        # Advance to next question or complete form
        self.current_question += 1

        if self.current_question >= len(self.form_questions):
            self.complete_form()

    def complete_form(self):
        """Complete the application form"""
        self.form_completed = True
        self.application_status = "approved"

        # Create celebration particles
        for _ in range(30):
            particle = self.create_particle(
                self.form_area.centerx + random.uniform(-150, 150),
                self.form_area.centery + random.uniform(-100, 100),
                self.colors['success_green']
            )
            self.success_particles.append(particle)

        # Complete the objective
        if self.objective_manager:
            self.objective_manager.complete_objective("foster_youth_application")

    def update(self, dt):
        """Update clinic interior animations"""
        if not self.active:
            return

        self.time += dt

        # Update particles
        self.update_particles(dt)

        # Update current objective based on game state
        current_obj = self.objective_manager.get_current_objective()
        if current_obj:
            self.current_objective = current_obj.title

    def render(self, screen):
        """Render enhanced clinic interior"""
        if not self.active:
            return

        # Background
        screen.fill(self.colors['background'])

        # Draw clinic header
        self.draw_clinic_header(screen)

        # Draw main interface elements
        self.draw_document_checklist(screen)
        self.draw_application_form(screen)
        self.draw_progress_panel(screen)

        # Draw particles
        for particle in self.success_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            size = max(1, int(particle['size']))

            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))

        # Instructions
        if not self.form_completed:
            instruction_text = "Click to check documents, then answer form questions (A, B, C, D keys)"
        else:
            instruction_text = "Application complete! Processing time: 2 weeks for card arrival"

        instruction_surface = self.fonts['small'].render(instruction_text, True, self.colors['text_light'])
        screen.blit(instruction_surface, (50, self.SCREEN_HEIGHT - 40))

    def enter(self):
        """Enter the enhanced clinic interior"""
        self.active = True
        print(f"[ENHANCED_CLINIC] Entered clinic interior at {self.building_pos}")

    def exit(self):
        """Exit the clinic interior"""
        self.active = False
        return self.building_pos  # Return to building position

    def is_active(self):
        """Check if clinic interior is active"""
        return self.active
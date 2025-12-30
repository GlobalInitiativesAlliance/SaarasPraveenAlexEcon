"""
FAFSA Form Mini-Game
Fill out FAFSA application with 60-second timer
Handle foster youth independent status bypass
"""
import pygame
import time

class FAFSAFormGame:
    """FAFSA application with timer and parent info bypass"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 60.0  # seconds
        self.time_remaining = self.time_limit
        self.timer_paused = False

        # Form fields
        self.form_fields = [
            {'label': 'Full Name', 'value': '', 'filled': False, 'required': True},
            {'label': 'SSN', 'value': '***-**-****', 'filled': False, 'required': True},
            {'label': 'Date of Birth', 'value': '', 'filled': False, 'required': True},
            {'label': 'Current Address', 'value': '', 'filled': False, 'required': True},
            {'label': 'High School', 'value': '', 'filled': False, 'required': True},
            {'label': 'Graduation Date', 'value': '', 'filled': False, 'required': True},
            {'label': 'Parent Income', 'value': 'N/A', 'filled': False, 'required': False, 'blocked': True},
            {'label': 'Parent Tax Info', 'value': 'N/A', 'filled': False, 'required': False, 'blocked': True},
        ]

        self.current_field = 0
        self.selected_field = None

        # Parent info popup
        self.show_parent_popup = False
        self.parent_popup_timer = 0
        self.bypass_options = [
            "I don't know my parents",
            "I'm an independent student (foster youth)",
            "My parents refuse to provide info",
            "I need to contact my parents first"
        ]
        self.correct_bypass = 1  # Foster youth option
        self.bypass_selected = None
        self.bypass_completed = False

        # UI elements
        self.field_rects = []
        self.create_field_rects()

        # Colors
        self.BG_COLOR = (240, 245, 250)
        self.FORM_COLOR = (255, 255, 255)
        self.FILLED_COLOR = (220, 255, 220)
        self.BLOCKED_COLOR = (250, 200, 200)
        self.TIMER_GREEN = (100, 200, 100)
        self.TIMER_YELLOW = (255, 200, 100)
        self.TIMER_RED = (255, 100, 100)

    def create_field_rects(self):
        """Create clickable rectangles for form fields"""
        self.field_rects = []
        start_y = 150

        for i in range(len(self.form_fields)):
            y = start_y + (i * 60)
            rect = pygame.Rect(400, y, 400, 40)
            self.field_rects.append(rect)

    def handle_event(self, event):
        """Handle form interaction"""
        if not self.active or self.completed:
            return False

        if self.show_parent_popup:
            # Handle bypass selection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                # Check bypass options
                for i, rect in enumerate(self.bypass_option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.bypass_selected = i
                        if i == self.correct_bypass:
                            # Correct answer - bypass parent fields
                            self.bypass_completed = True
                            self.show_parent_popup = False
                            self.timer_paused = False

                            # Mark parent fields as bypassed
                            for field in self.form_fields:
                                if field.get('blocked'):
                                    field['filled'] = True
                                    field['value'] = 'BYPASSED - Foster Youth'
                        else:
                            # Wrong answer - show feedback
                            self.bypass_selected = i
                        break

        else:
            # Regular form interaction
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                for i, rect in enumerate(self.field_rects):
                    if rect.collidepoint(mouse_pos):
                        field = self.form_fields[i]

                        if field.get('blocked') and not self.bypass_completed:
                            # Show parent info popup
                            self.show_parent_popup = True
                            self.timer_paused = True
                            self.parent_popup_timer = 0
                            self.create_bypass_option_rects()
                        elif not field.get('blocked'):
                            # Auto-fill regular field
                            if not field['filled']:
                                field['filled'] = True
                                field['value'] = self.get_auto_fill_value(field['label'])
                        break

        return True

    def get_auto_fill_value(self, label):
        """Return appropriate auto-fill value for field"""
        values = {
            'Full Name': 'Jordan Foster',
            'SSN': '***-**-1234',
            'Date of Birth': '01/15/2006',
            'Current Address': '123 TLP Housing, City, ST',
            'High School': 'Central High School',
            'Graduation Date': '06/2024'
        }
        return values.get(label, 'Filled')

    def create_bypass_option_rects(self):
        """Create clickable areas for bypass options"""
        self.bypass_option_rects = []
        popup_x = self.SCREEN_WIDTH // 2 - 250
        popup_y = self.SCREEN_HEIGHT // 2 - 150

        for i in range(len(self.bypass_options)):
            y = popup_y + 120 + (i * 45)
            rect = pygame.Rect(popup_x + 20, y, 460, 35)
            self.bypass_option_rects.append(rect)

    def update(self, dt):
        """Update timer and check completion"""
        if not self.active or self.completed:
            return

        # Update timer
        if not self.timer_paused:
            self.time_remaining -= dt

            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.completed = True
                # Activity completion handled by interior callback

        # Check for form completion
        all_filled = all(f['filled'] for f in self.form_fields if f['required'])
        if all_filled and self.bypass_completed and not self.completed:
            self.completed = True
            # Activity completion handled by interior callback

    def render(self, screen):
        """Render the FAFSA form interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)
        overlay.fill(self.BG_COLOR)
        screen.blit(overlay, (0, 0))

        # Form container
        form_rect = pygame.Rect(150, 80, 980, 560)
        pygame.draw.rect(screen, self.FORM_COLOR, form_rect)
        pygame.draw.rect(screen, (100, 100, 110), form_rect, 2)

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("FAFSA Application", True, (30, 30, 40))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Timer
        timer_font = pygame.font.Font(None, 36)
        if self.time_remaining > 30:
            timer_color = self.TIMER_GREEN
        elif self.time_remaining > 10:
            timer_color = self.TIMER_YELLOW
        else:
            timer_color = self.TIMER_RED

        timer_text = timer_font.render(f"Time: {int(self.time_remaining)}s", True, timer_color)
        screen.blit(timer_text, (self.SCREEN_WIDTH - 200, 100))

        # Form fields
        label_font = pygame.font.Font(None, 28)
        value_font = pygame.font.Font(None, 24)

        for i, (field, rect) in enumerate(zip(self.form_fields, self.field_rects)):
            # Label
            label_color = (30, 30, 40)
            if field.get('blocked') and not self.bypass_completed:
                label_color = (200, 50, 50)

            label_text = label_font.render(field['label'] + ':', True, label_color)
            screen.blit(label_text, (200, rect.y + 10))

            # Field background
            if field['filled']:
                if field.get('blocked'):
                    bg_color = (250, 250, 200)
                else:
                    bg_color = self.FILLED_COLOR
            elif field.get('blocked'):
                bg_color = self.BLOCKED_COLOR
            else:
                bg_color = (255, 255, 255)

            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, (150, 150, 160), rect, 1)

            # Field value
            if field['value']:
                value_color = (50, 50, 60) if field['filled'] else (150, 150, 160)
                value_text = value_font.render(field['value'], True, value_color)
                screen.blit(value_text, (rect.x + 10, rect.y + 10))

        # Instructions
        if not self.show_parent_popup:
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Click fields to auto-fill information", True, (100, 100, 120))
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 620))

        # Parent info popup
        if self.show_parent_popup:
            self.render_parent_popup(screen)

    def render_parent_popup(self, screen):
        """Render the parent information bypass popup"""
        # Popup background
        popup_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 250, self.SCREEN_HEIGHT // 2 - 150, 500, 350)
        pygame.draw.rect(screen, (255, 255, 255), popup_rect)
        pygame.draw.rect(screen, (200, 50, 50), popup_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 32)
        title_text = title_font.render("PARENT INFORMATION REQUIRED", True, (200, 50, 50))
        title_x = popup_rect.centerx - title_text.get_width() // 2
        screen.blit(title_text, (title_x, popup_rect.y + 20))

        # Question
        question_font = pygame.font.Font(None, 24)
        question_text = "Why can't you provide parent information?"
        q_surface = question_font.render(question_text, True, (50, 50, 60))
        q_x = popup_rect.centerx - q_surface.get_width() // 2
        screen.blit(q_surface, (q_x, popup_rect.y + 70))

        # Options
        option_font = pygame.font.Font(None, 22)
        for i, (option, rect) in enumerate(zip(self.bypass_options, self.bypass_option_rects)):
            # Background color
            if self.bypass_selected == i:
                if i == self.correct_bypass:
                    bg_color = (150, 255, 150)
                else:
                    bg_color = (255, 150, 150)
            else:
                mouse_pos = pygame.mouse.get_pos()
                if rect.collidepoint(mouse_pos):
                    bg_color = (230, 230, 240)
                else:
                    bg_color = (255, 255, 255)

            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, (100, 100, 110), rect, 1)

            # Option text
            option_text = option_font.render(option, True, (30, 30, 40))
            screen.blit(option_text, (rect.x + 10, rect.y + 8))

        # Feedback for wrong selection
        if self.bypass_selected is not None and self.bypass_selected != self.correct_bypass:
            feedback_font = pygame.font.Font(None, 20)
            feedback_text = "Try again - Foster youth have special status"
            f_surface = feedback_font.render(feedback_text, True, (200, 50, 50))
            f_x = popup_rect.centerx - f_surface.get_width() // 2
            screen.blit(f_surface, (f_x, popup_rect.bottom - 40))

    def start(self):
        """Start the FAFSA form game"""
        self.active = True
        self.completed = False
        self.time_remaining = self.time_limit
        self.show_parent_popup = False
        self.bypass_completed = False
        self.bypass_selected = None

        # Reset form fields
        for field in self.form_fields:
            field['filled'] = False
            if not field.get('blocked'):
                field['value'] = ''

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False
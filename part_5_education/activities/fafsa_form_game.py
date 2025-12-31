"""
FAFSA Form Mini-Game
Fill out FAFSA application with 60-second timer
Handle foster youth independent status bypass

UPGRADED: Professional visuals with paper texture, circular timer,
typewriter animations, and celebration effects
"""
import pygame
import math
import time

from .education_visual_base import (
    EducationUIColors, EducationUIMetrics, EducationVisualHelpers,
    EducationVisualComponents, UIAnimation, education_visuals
)
from .particle_effects import ParticleSystem
from .feedback_popups import FeedbackPopupManager


class FAFSAFormGame:
    """FAFSA application with timer, auto-fill animations, and parent info bypass"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 60.0
        self.time_remaining = self.time_limit
        self.timer_paused = False

        # Form fields
        self.form_fields = [
            {'label': 'Full Name', 'value': '', 'filled': False, 'required': True,
             'target_value': 'Jordan Foster', 'display_chars': 0},
            {'label': 'SSN', 'value': '', 'filled': False, 'required': True,
             'target_value': '***-**-1234', 'display_chars': 0},
            {'label': 'Date of Birth', 'value': '', 'filled': False, 'required': True,
             'target_value': '01/15/2006', 'display_chars': 0},
            {'label': 'Current Address', 'value': '', 'filled': False, 'required': True,
             'target_value': '123 TLP Housing, City, ST', 'display_chars': 0},
            {'label': 'High School', 'value': '', 'filled': False, 'required': True,
             'target_value': 'Central High School', 'display_chars': 0},
            {'label': 'Graduation Date', 'value': '', 'filled': False, 'required': True,
             'target_value': '06/2024', 'display_chars': 0},
            {'label': 'Parent Income', 'value': 'N/A', 'filled': False, 'required': False,
             'blocked': True, 'target_value': 'BYPASSED - Foster Youth', 'display_chars': 0},
            {'label': 'Parent Tax Info', 'value': 'N/A', 'filled': False, 'required': False,
             'blocked': True, 'target_value': 'BYPASSED - Foster Youth', 'display_chars': 0},
        ]

        self.current_field = 0
        self.selected_field = None
        self.filling_field = None  # Currently animating field

        # Parent info popup
        self.show_parent_popup = False
        self.parent_popup_timer = 0
        self.bypass_options = [
            "I don't know my parents",
            "I'm an independent student (foster youth)",
            "My parents refuse to provide info",
            "I need to contact my parents first"
        ]
        self.correct_bypass = 1
        self.bypass_selected = None
        self.bypass_completed = False
        self.popup_alpha = UIAnimation(0, 0, speed=0.2)

        # UI elements
        self.field_rects = []
        self.create_field_rects()
        self.bypass_option_rects = []

        # Visual systems
        self.particles = ParticleSystem()
        self.popups = FeedbackPopupManager()
        self.visuals = education_visuals

        # Animations
        self.form_scale = UIAnimation(0.9, 1.0, speed=0.1)
        self.stamp_visible = False
        self.stamp_scale = UIAnimation(3.0, 1.0, speed=0.15)
        self.stamp_rotation = UIAnimation(20, 0, speed=0.1)
        self.celebration_triggered = False

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 42, bold=True)
            self.font_label = pygame.font.SysFont('SF Pro Text', 20)
            self.font_value = pygame.font.SysFont('SF Pro Text', 18)
            self.font_small = pygame.font.SysFont('SF Pro Text', 16)
            self.font_popup = pygame.font.SysFont('SF Pro Display', 28, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_label = pygame.font.Font(None, 24)
            self.font_value = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 18)
            self.font_popup = pygame.font.Font(None, 32)

    def create_field_rects(self):
        """Create clickable rectangles for form fields"""
        self.field_rects = []
        start_y = 180
        field_height = 45
        field_spacing = 55

        for i in range(len(self.form_fields)):
            y = start_y + (i * field_spacing)
            rect = pygame.Rect(450, y, 380, field_height)
            self.field_rects.append(rect)

    def handle_event(self, event):
        """Handle form interaction"""
        if not self.active or self.completed:
            return False

        if self.show_parent_popup:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                for i, rect in enumerate(self.bypass_option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.bypass_selected = i
                        if i == self.correct_bypass:
                            # Correct answer
                            self.bypass_completed = True
                            self.popup_alpha.target = 0

                            # Mark parent fields as bypassed with animation
                            for field in self.form_fields:
                                if field.get('blocked'):
                                    field['filled'] = True
                                    field['value'] = field['target_value']
                                    field['display_chars'] = len(field['target_value'])

                            # Show success feedback
                            self.popups.add_correct(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
                            self.particles.emit_success(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
                        else:
                            # Wrong answer
                            self.popups.add_incorrect(mouse_pos[0], mouse_pos[1] - 20)
                            self.particles.emit_error(mouse_pos[0], mouse_pos[1])
                        break
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                for i, rect in enumerate(self.field_rects):
                    if rect.collidepoint(mouse_pos):
                        field = self.form_fields[i]

                        if field.get('blocked') and not self.bypass_completed:
                            # Show parent info popup
                            self.show_parent_popup = True
                            self.timer_paused = True
                            self.popup_alpha.target = 1.0
                            self.create_bypass_option_rects()
                        elif not field.get('blocked') and not field['filled']:
                            # Start typewriter animation
                            field['filling'] = True
                            self.filling_field = field
                            self.particles.emit_typing_cursor(rect.right, rect.centery)
                        break

        return True

    def create_bypass_option_rects(self):
        """Create clickable areas for bypass options"""
        self.bypass_option_rects = []
        popup_x = self.SCREEN_WIDTH // 2 - 280
        popup_y = self.SCREEN_HEIGHT // 2 - 180

        for i in range(len(self.bypass_options)):
            y = popup_y + 140 + (i * 55)
            rect = pygame.Rect(popup_x + 30, y, 500, 45)
            self.bypass_option_rects.append(rect)

    def update(self, dt):
        """Update timer, animations, and check completion"""
        if not self.active or self.completed:
            return

        # Update animations
        self.form_scale.update(dt)
        self.popup_alpha.update(dt)
        self.stamp_scale.update(dt)
        self.stamp_rotation.update(dt)
        self.particles.update(dt)
        self.popups.update(dt)

        # Close popup when alpha reaches 0
        if self.show_parent_popup and self.popup_alpha.value < 0.05 and self.bypass_completed:
            self.show_parent_popup = False
            self.timer_paused = False

        # Update timer
        if not self.timer_paused:
            self.time_remaining -= dt

            # Timer warning particles
            if self.time_remaining < 10 and int(self.time_remaining * 2) % 2 == 0:
                timer_center = (self.SCREEN_WIDTH - 100, 130)
                self.particles.emit_timer_warning(timer_center[0], timer_center[1])

            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.completed = True

        # Update typewriter animation
        if self.filling_field:
            field = self.filling_field
            target_len = len(field['target_value'])
            field['display_chars'] += dt * 25  # Characters per second

            if field['display_chars'] >= target_len:
                field['display_chars'] = target_len
                field['value'] = field['target_value']
                field['filled'] = True
                field['filling'] = False
                self.filling_field = None

                # Success feedback
                field_index = self.form_fields.index(field)
                rect = self.field_rects[field_index]
                self.particles.emit_success(rect.centerx, rect.centery)
                self.popups.add_score(rect.centerx, rect.y - 10, 10)
            else:
                field['value'] = field['target_value'][:int(field['display_chars'])]

        # Check for form completion
        required_filled = all(f['filled'] for f in self.form_fields if f['required'])
        all_filled = all(f['filled'] for f in self.form_fields)

        if all_filled and self.bypass_completed and not self.completed and not self.celebration_triggered:
            self.celebration_triggered = True
            self.stamp_visible = True
            self.stamp_scale = UIAnimation(3.0, 1.0, speed=0.15)
            self.stamp_rotation = UIAnimation(20, 0, speed=0.1)

            # Celebration effects
            center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
            self.particles.emit_confetti(center[0], center[1], 60)
            self.particles.emit_stamp(center[0], center[1])
            self.popups.add_submitted(center[0], center[1] - 100)
            self.popups.add_form_complete_achievement()

            # Complete after celebration
            pygame.time.set_timer(pygame.USEREVENT + 100, 2000, loops=1)

    def render(self, screen):
        """Render the FAFSA form interface"""
        if not self.active:
            return

        # Background gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = EducationVisualHelpers.interpolate_color(
                (235, 240, 250), (220, 230, 245), progress
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Form container with paper texture
        form_width = int(900 * self.form_scale.value)
        form_height = int(580 * self.form_scale.value)
        form_x = (self.SCREEN_WIDTH - form_width) // 2
        form_y = 60

        form_rect = pygame.Rect(form_x, form_y, form_width, form_height)
        self.visuals.draw_paper_background(screen, form_rect, with_lines=True, shadow=True)

        # Title with icon
        title_text = self.font_title.render("FAFSA Application", True,
                                           EducationUIColors.EDUCATION_PRIMARY)
        title_x = self.SCREEN_WIDTH // 2 - title_text.get_width() // 2
        screen.blit(title_text, (title_x, form_y + 15))

        # Subtitle
        subtitle = self.font_small.render("Free Application for Federal Student Aid", True,
                                         EducationUIColors.TEXT_SECONDARY)
        screen.blit(subtitle, (self.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, form_y + 55))

        # Circular timer
        timer_center = (self.SCREEN_WIDTH - 100, 130)
        self.visuals.draw_timer_arc(screen, timer_center, 40,
                                   self.time_remaining, self.time_limit)

        # Form fields
        for i, (field, rect) in enumerate(zip(self.form_fields, self.field_rects)):
            self._render_field(screen, field, rect, i)

        # Progress indicator
        filled_count = sum(1 for f in self.form_fields if f['filled'])
        total_count = len(self.form_fields)
        self._render_progress(screen, filled_count, total_count, form_rect)

        # Instructions
        inst_text = self.font_small.render("Click fields to auto-fill your information", True,
                                          EducationUIColors.TEXT_MUTED)
        screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2,
                               form_rect.bottom - 30))

        # Parent info popup
        if self.show_parent_popup:
            self._render_parent_popup(screen)

        # Submitted stamp
        if self.stamp_visible:
            self._render_stamp(screen)

        # Particles and popups (always on top)
        self.particles.render(screen)
        self.popups.render(screen)

    def _render_field(self, screen, field, rect, index):
        """Render a single form field with professional styling"""
        is_blocked = field.get('blocked', False)
        is_filled = field['filled']
        is_filling = field.get('filling', False)

        # Determine state
        if is_filled:
            if is_blocked and self.bypass_completed:
                state = 'bypassed'
            else:
                state = 'filled'
        elif is_blocked:
            state = 'blocked'
        elif is_filling:
            state = 'focus'
        else:
            state = 'normal'

        # State colors
        state_colors = {
            'normal': (EducationUIColors.FORM_FIELD_BG, EducationUIColors.FORM_FIELD_BORDER),
            'filled': ((220, 250, 220), EducationUIColors.VERIFIED),
            'focus': (EducationUIColors.FORM_FIELD_BG, EducationUIColors.EDUCATION_PRIMARY),
            'blocked': ((255, 230, 230), EducationUIColors.BLOCKED),
            'bypassed': ((240, 230, 255), EducationUIColors.BYPASSED)
        }
        bg_color, border_color = state_colors.get(state, state_colors['normal'])

        # Field shadow
        if state == 'focus':
            EducationVisualHelpers.draw_shadow(screen, rect, 4, 40, EducationUIMetrics.RADIUS_SMALL)

        # Field background
        pygame.draw.rect(screen, bg_color, rect, border_radius=EducationUIMetrics.RADIUS_SMALL)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=EducationUIMetrics.RADIUS_SMALL)

        # Label
        label_color = EducationUIColors.BLOCKED if is_blocked and not self.bypass_completed else EducationUIColors.TEXT_SECONDARY
        required_mark = " *" if field['required'] else ""
        label_text = self.font_label.render(field['label'] + required_mark, True, label_color)
        screen.blit(label_text, (rect.x - 230, rect.centery - label_text.get_height() // 2))

        # Value with cursor
        if field['value']:
            value_color = EducationUIColors.TEXT_PRIMARY if not is_blocked else EducationUIColors.TEXT_MUTED
            display_value = field['value']

            # Blinking cursor during typing
            if is_filling and int(time.time() * 3) % 2 == 0:
                display_value += '|'

            value_text = self.font_value.render(display_value, True, value_color)
            screen.blit(value_text, (rect.x + 12, rect.centery - value_text.get_height() // 2))

        # Status icon
        if is_filled:
            icon_x = rect.right - 25
            icon_y = rect.centery
            if state == 'bypassed':
                self.visuals.draw_checkmark(screen, (icon_x, icon_y), 12,
                                           EducationUIColors.BYPASSED)
            else:
                self.visuals.draw_checkmark(screen, (icon_x, icon_y), 12)
        elif is_blocked and not self.bypass_completed:
            # Lock icon placeholder
            lock_text = self.font_small.render("🔒", True, EducationUIColors.BLOCKED)
            screen.blit(lock_text, (rect.right - 30, rect.centery - 8))

    def _render_progress(self, screen, filled, total, form_rect):
        """Render progress indicator"""
        progress_y = form_rect.bottom - 60
        progress_width = 200
        progress_x = self.SCREEN_WIDTH // 2 - progress_width // 2

        # Background
        pygame.draw.rect(screen, (220, 225, 230),
                        (progress_x, progress_y, progress_width, 8),
                        border_radius=4)

        # Fill
        fill_width = int(progress_width * (filled / total))
        if fill_width > 0:
            pygame.draw.rect(screen, EducationUIColors.EDUCATION_PRIMARY,
                            (progress_x, progress_y, fill_width, 8),
                            border_radius=4)

        # Text
        progress_text = self.font_small.render(f"{filled}/{total} fields", True,
                                              EducationUIColors.TEXT_MUTED)
        screen.blit(progress_text, (progress_x + progress_width + 10, progress_y - 3))

    def _render_parent_popup(self, screen):
        """Render the parent information bypass popup"""
        alpha = int(self.popup_alpha.value * 255)
        if alpha < 5:
            return

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(alpha * 0.7)))
        screen.blit(overlay, (0, 0))

        # Popup container
        popup_width = 560
        popup_height = 400
        popup_x = (self.SCREEN_WIDTH - popup_width) // 2
        popup_y = (self.SCREEN_HEIGHT - popup_height) // 2

        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, popup_rect, 12, 80,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, popup_rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Header
        header_rect = pygame.Rect(popup_x, popup_y, popup_width, 60)
        pygame.draw.rect(screen, EducationUIColors.BLOCKED, header_rect,
                        border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

        # Header text
        header_text = self.font_popup.render("PARENT INFORMATION REQUIRED", True,
                                            EducationUIColors.TEXT_LIGHT)
        screen.blit(header_text, (popup_rect.centerx - header_text.get_width() // 2,
                                 popup_y + 15))

        # Question
        question = self.font_label.render("Why can't you provide parent information?", True,
                                         EducationUIColors.TEXT_PRIMARY)
        screen.blit(question, (popup_rect.centerx - question.get_width() // 2, popup_y + 90))

        # Options
        mouse_pos = pygame.mouse.get_pos()
        for i, (option, rect) in enumerate(zip(self.bypass_options, self.bypass_option_rects)):
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = self.bypass_selected == i
            is_correct = i == self.correct_bypass

            # Determine colors
            if is_selected:
                if is_correct:
                    bg_color = (200, 255, 200)
                    border_color = EducationUIColors.VERIFIED
                else:
                    bg_color = (255, 200, 200)
                    border_color = EducationUIColors.BLOCKED
            elif is_hovered:
                bg_color = (240, 245, 255)
                border_color = EducationUIColors.EDUCATION_PRIMARY
            else:
                bg_color = EducationUIColors.FORM_FIELD_BG
                border_color = EducationUIColors.FORM_FIELD_BORDER

            # Draw option
            pygame.draw.rect(screen, bg_color, rect, border_radius=EducationUIMetrics.RADIUS_MEDIUM)
            pygame.draw.rect(screen, border_color, rect, 2,
                            border_radius=EducationUIMetrics.RADIUS_MEDIUM)

            # Option text
            option_text = self.font_value.render(option, True, EducationUIColors.TEXT_PRIMARY)
            screen.blit(option_text, (rect.x + 15, rect.centery - option_text.get_height() // 2))

            # Number badge
            num_rect = pygame.Rect(rect.x - 35, rect.centery - 12, 24, 24)
            pygame.draw.rect(screen, border_color, num_rect, border_radius=12)
            num_text = self.font_small.render(str(i + 1), True, EducationUIColors.TEXT_LIGHT)
            screen.blit(num_text, (num_rect.centerx - num_text.get_width() // 2,
                                  num_rect.centery - num_text.get_height() // 2))

        # Feedback for wrong selection
        if self.bypass_selected is not None and self.bypass_selected != self.correct_bypass:
            feedback = self.font_small.render("Foster youth have special independent status - try again!",
                                             True, EducationUIColors.BLOCKED)
            screen.blit(feedback, (popup_rect.centerx - feedback.get_width() // 2,
                                  popup_rect.bottom - 40))

        # Border
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, popup_rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def _render_stamp(self, screen):
        """Render the SUBMITTED stamp with animation"""
        center = (self.SCREEN_WIDTH // 2 + 200, self.SCREEN_HEIGHT // 2 + 100)
        scale = self.stamp_scale.value
        rotation = self.stamp_rotation.value

        # Create stamp surface
        stamp_width = int(180 * scale)
        stamp_height = int(60 * scale)
        stamp_surface = pygame.Surface((stamp_width + 20, stamp_height + 20), pygame.SRCALPHA)

        # Stamp rectangle
        stamp_rect = pygame.Rect(10, 10, stamp_width, stamp_height)
        pygame.draw.rect(stamp_surface, (72, 187, 120, 200), stamp_rect,
                        border_radius=8)
        pygame.draw.rect(stamp_surface, (50, 150, 90), stamp_rect, 4,
                        border_radius=8)

        # Text
        stamp_font = pygame.font.Font(None, int(32 * scale))
        stamp_text = stamp_font.render("SUBMITTED", True, (255, 255, 255))
        text_rect = stamp_text.get_rect(center=(stamp_width // 2 + 10, stamp_height // 2 + 10))
        stamp_surface.blit(stamp_text, text_rect)

        # Rotate
        rotated = pygame.transform.rotate(stamp_surface, rotation)
        rotated_rect = rotated.get_rect(center=center)
        screen.blit(rotated, rotated_rect)

    def start(self):
        """Start the FAFSA form game"""
        self.active = True
        self.completed = False
        self.time_remaining = self.time_limit
        self.show_parent_popup = False
        self.bypass_completed = False
        self.bypass_selected = None
        self.filling_field = None
        self.stamp_visible = False
        self.celebration_triggered = False
        self.form_scale = UIAnimation(0.9, 1.0, speed=0.1)

        # Reset form fields
        for field in self.form_fields:
            field['filled'] = False
            field['display_chars'] = 0
            field['filling'] = False
            if not field.get('blocked'):
                field['value'] = ''

        # Clear effects
        self.particles.clear()
        self.popups.clear()

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False

"""
Medi-Cal Former Foster Youth Program Application Form
Quick 4-question form to reapply for coverage
UPGRADED with healthcare visual system - animations, particles, polish
"""
import pygame
import math
import random

from part_4_healthcare.activities.healthcare_visual_base import (
    HealthcareUIColors, HealthcareUIMetrics, HealthcareVisualHelpers,
    HealthcareVisualComponents, UIAnimation, healthcare_visuals
)
from part_4_healthcare.activities.healthcare_particle_effects import healthcare_particles
from part_4_healthcare.activities.healthcare_feedback_popups import healthcare_feedback


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
        self.submit_button = pygame.Rect(540, 530, 200, 60)

        # Animation states
        self.form_scale = UIAnimation(0.9, 0.9, 0.3)
        self.form_alpha = UIAnimation(0.0, 0.0, 0.4)
        self.question_slide = UIAnimation(0.0, 0.0, 0.25)
        self.progress_fill = UIAnimation(0.0, 0.0, 0.4)
        self.submit_scale = UIAnimation(1.0, 1.0, 0.15)
        self.submit_pulse_timer = 0.0
        self.approval_scale = UIAnimation(0.0, 0.0, 0.3)
        self.stamp_rotation = UIAnimation(45.0, 45.0, 0.2)
        self.stamp_scale = UIAnimation(2.0, 2.0, 0.25)

        # Option button animations
        self.option_scales = []
        self.option_alphas = []
        self.checkmark_scales = []

        # Visual state
        self.question_x_offset = 0
        self.previous_question = -1
        self.processing_timer = 0
        self.show_processing = False
        self.confetti_spawned = False

        # Fonts
        self.title_font = pygame.font.Font(None, 38)
        self.question_font = pygame.font.Font(None, 30)
        self.option_font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.approval_font = pygame.font.Font(None, 44)
        self.stamp_font = pygame.font.Font(None, 56)

    def create_option_rects(self):
        """Create rectangles for answer options with animations"""
        self.option_rects = []
        self.option_scales = []
        self.option_alphas = []
        self.checkmark_scales = []

        num_options = len(self.questions[self.current_question]['options'])

        # Center options based on count
        total_width = num_options * 160 + (num_options - 1) * 20
        start_x = (self.SCREEN_WIDTH - total_width) // 2

        for i in range(num_options):
            x = start_x + i * 180
            y = 320
            rect = pygame.Rect(x, y, 160, 55)
            self.option_rects.append(rect)

            # Staggered fade-in animations
            alpha_anim = UIAnimation(0.0, 1.0, 0.25)
            self.option_alphas.append(alpha_anim)

            scale_anim = UIAnimation(1.0, 1.0, 0.15)
            self.option_scales.append(scale_anim)

            checkmark_anim = UIAnimation(0.0, 0.0, 0.2)
            self.checkmark_scales.append(checkmark_anim)

    def handle_event(self, event):
        """Handle form interaction events"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            if not self.form_submitted and not self.show_processing:
                # Check option clicks
                for i, rect in enumerate(self.option_rects):
                    # Account for scale
                    scale = self.option_scales[i].current if i < len(self.option_scales) else 1.0
                    scaled_rect = pygame.Rect(
                        rect.centerx - rect.width * scale / 2,
                        rect.centery - rect.height * scale / 2,
                        rect.width * scale,
                        rect.height * scale
                    )

                    if scaled_rect.collidepoint(mouse_pos):
                        self.questions[self.current_question]['answer'] = i

                        # Animate checkmark
                        self.checkmark_scales[i].target = 1.0

                        # Selection feedback
                        healthcare_feedback.add_text(mouse_pos[0], mouse_pos[1], "Selected!",
                                                    HealthcareUIColors.SUCCESS)
                        healthcare_particles.emit_sparkle(mouse_pos[0], mouse_pos[1], count=8)

                        # Auto-advance after delay
                        if self.current_question < len(self.questions) - 1:
                            pygame.time.set_timer(pygame.USEREVENT + 100, 400, loops=1)
                        break

                # Check submit button
                if self.submit_button.collidepoint(mouse_pos):
                    all_answered = all(q['answer'] is not None for q in self.questions)
                    if all_answered:
                        self.show_processing = True
                        self.processing_timer = 90  # 1.5 seconds
                        healthcare_particles.emit_glow(
                            self.submit_button.centerx,
                            self.submit_button.centery,
                            HealthcareUIColors.PRIMARY
                        )

        elif event.type == pygame.USEREVENT + 100:
            # Advance to next question (triggered by timer)
            if self.current_question < len(self.questions) - 1:
                self.previous_question = self.current_question
                self.current_question += 1
                self.question_slide.current = 50  # Start off-screen right
                self.question_slide.target = 0
                self.create_option_rects()

                # Update progress bar
                progress = (self.current_question) / len(self.questions)
                self.progress_fill.target = progress

        elif event.type == pygame.KEYDOWN:
            # Allow keyboard navigation
            if event.key >= pygame.K_1 and event.key <= pygame.K_3:
                option_index = event.key - pygame.K_1
                if option_index < len(self.questions[self.current_question]['options']):
                    self.questions[self.current_question]['answer'] = option_index

                    if option_index < len(self.checkmark_scales):
                        self.checkmark_scales[option_index].target = 1.0

                    if self.current_question < len(self.questions) - 1:
                        pygame.time.set_timer(pygame.USEREVENT + 100, 400, loops=1)

        return True

    def update(self, dt):
        """Update form state and animations"""
        if not self.active:
            return

        # Update all animations
        self.form_scale.update(dt)
        self.form_alpha.update(dt)
        self.question_slide.update(dt)
        self.progress_fill.update(dt)
        self.submit_scale.update(dt)
        self.approval_scale.update(dt)
        self.stamp_rotation.update(dt)
        self.stamp_scale.update(dt)

        for anim in self.option_scales:
            anim.update(dt)
        for anim in self.option_alphas:
            anim.update(dt)
        for anim in self.checkmark_scales:
            anim.update(dt)

        # Submit button pulse when ready
        all_answered = all(q['answer'] is not None for q in self.questions)
        if all_answered and not self.form_submitted and not self.show_processing:
            self.submit_pulse_timer += dt
            pulse = 1.0 + math.sin(self.submit_pulse_timer * 4) * 0.03
            self.submit_scale.current = pulse

        # Processing timer
        if self.show_processing and self.processing_timer > 0:
            self.processing_timer -= 1
            if self.processing_timer <= 0:
                self.form_submitted = True
                self.show_processing = False
                self.approval_timer = 150  # 2.5 seconds
                self.approval_scale.target = 1.0
                self.stamp_rotation.target = -5
                self.stamp_scale.target = 1.0

                # Form submitted achievement
                healthcare_feedback.add_form_submitted()

        if self.form_submitted and self.approval_timer > 0:
            self.approval_timer -= 1

            # Spawn confetti once
            if self.approval_timer == 120 and not self.confetti_spawned:
                self.show_approval = True
                healthcare_particles.emit_confetti(self.SCREEN_WIDTH // 2, 300, count=60)
                healthcare_particles.emit_insurance_approved(self.SCREEN_WIDTH // 2, 350)
                healthcare_feedback.add_coverage_approved()
                self.confetti_spawned = True

            elif self.approval_timer == 0:
                self.completed = True

        # Update particles and feedback
        healthcare_particles.update(dt)
        healthcare_feedback.update(dt)

    def render(self, screen):
        """Render the form interface with visual polish"""
        if not self.active:
            return

        # Background overlay with slight gradient
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = HealthcareVisualHelpers.color_lerp(
                HealthcareUIColors.NEUTRAL,
                (220, 225, 230),
                progress * 0.5
            )
            pygame.draw.line(overlay, (*color, 250), (0, y), (self.SCREEN_WIDTH, y))
        screen.blit(overlay, (0, 0))

        # Form container with paper effect
        form_rect = pygame.Rect(190, 80, 900, 560)
        scale = self.form_scale.current
        alpha = int(self.form_alpha.current * 255)

        scaled_rect = pygame.Rect(
            form_rect.centerx - form_rect.width * scale / 2,
            form_rect.centery - form_rect.height * scale / 2,
            form_rect.width * scale,
            form_rect.height * scale
        )

        # Paper shadow
        HealthcareVisualHelpers.draw_shadow(screen, scaled_rect, offset=8, blur_radius=15, alpha=60)

        # Paper background
        healthcare_visuals.draw_paper_background(screen, scaled_rect)

        # Header with medical blue accent
        header_rect = pygame.Rect(scaled_rect.x, scaled_rect.y, scaled_rect.width, 70)
        pygame.draw.rect(screen, HealthcareUIColors.PRIMARY, header_rect,
                        border_top_left_radius=12, border_top_right_radius=12)

        # Title
        title_text = self.title_font.render("Medi-Cal Former Foster Youth Program", True, (255, 255, 255))
        title_x = header_rect.centerx - title_text.get_width() // 2
        screen.blit(title_text, (title_x, header_rect.y + 22))

        # Progress bar
        progress_y = scaled_rect.y + 85
        progress_rect = pygame.Rect(scaled_rect.x + 40, progress_y, scaled_rect.width - 80, 8)
        healthcare_visuals.draw_progress_bar(
            screen, progress_rect,
            self.progress_fill.current,
            color=HealthcareUIColors.SECONDARY
        )

        # Progress text
        progress_text = self.small_font.render(
            f"Question {self.current_question + 1} of {len(self.questions)}",
            True, HealthcareUIColors.TEXT_SECONDARY
        )
        screen.blit(progress_text, (progress_rect.right - progress_text.get_width(), progress_y + 15))

        # ESC hint
        esc_text = self.small_font.render("Press ESC to exit", True, (150, 150, 150))
        screen.blit(esc_text, (20, self.SCREEN_HEIGHT - 40))

        if not self.show_approval and not self.show_processing:
            self._render_question_form(screen, scaled_rect)
        elif self.show_processing:
            self._render_processing(screen, scaled_rect)
        else:
            self._render_approval(screen, scaled_rect)

        # Render particles and feedback on top
        healthcare_particles.draw(screen)
        healthcare_feedback.draw(screen)

    def _render_question_form(self, screen, form_rect):
        """Render the current question and options"""
        # Question text with slide animation
        question = self.questions[self.current_question]
        q_text = self.question_font.render(question['question'], True, HealthcareUIColors.TEXT_PRIMARY)
        q_x = self.SCREEN_WIDTH // 2 - q_text.get_width() // 2 + self.question_slide.current
        screen.blit(q_text, (q_x, 220))

        # Question number badge
        badge_x = q_x - 45
        badge_rect = pygame.Rect(badge_x, 215, 32, 32)
        pygame.draw.circle(screen, HealthcareUIColors.PRIMARY, badge_rect.center, 16)
        num_text = self.option_font.render(str(self.current_question + 1), True, (255, 255, 255))
        screen.blit(num_text, (badge_rect.centerx - num_text.get_width() // 2,
                               badge_rect.centery - num_text.get_height() // 2))

        # Answer options with animations
        mouse_pos = pygame.mouse.get_pos()
        for i, (rect, option) in enumerate(zip(self.option_rects, question['options'])):
            if i >= len(self.option_scales):
                continue

            scale = self.option_scales[i].current
            alpha = self.option_alphas[i].current
            is_selected = question['answer'] == i
            is_hovered = rect.collidepoint(mouse_pos) and not is_selected

            # Hover scale
            if is_hovered:
                self.option_scales[i].target = 1.05
            elif not is_selected:
                self.option_scales[i].target = 1.0

            # Calculate scaled rect
            scaled_rect = pygame.Rect(
                rect.centerx - rect.width * scale / 2,
                rect.centery - rect.height * scale / 2,
                rect.width * scale,
                rect.height * scale
            )

            # Button shadow
            if alpha > 0.5:
                HealthcareVisualHelpers.draw_shadow(screen, scaled_rect, offset=4, blur_radius=8, alpha=int(40 * alpha))

            # Button background
            if is_selected:
                bg_color = HealthcareUIColors.SUCCESS
            elif is_hovered:
                bg_color = HealthcareUIColors.PRIMARY_LIGHT
            else:
                bg_color = HealthcareUIColors.FORM_FIELD

            btn_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(btn_surface, (*bg_color, int(255 * alpha)),
                           btn_surface.get_rect(), border_radius=10)

            # Border
            border_color = HealthcareUIColors.SUCCESS if is_selected else HealthcareUIColors.FORM_BORDER
            pygame.draw.rect(btn_surface, (*border_color, int(255 * alpha)),
                           btn_surface.get_rect(), 2, border_radius=10)

            screen.blit(btn_surface, scaled_rect.topleft)

            # Option text
            text_color = (255, 255, 255) if is_selected else HealthcareUIColors.TEXT_PRIMARY
            option_text = self.option_font.render(option, True, text_color)
            text_x = scaled_rect.centerx - option_text.get_width() // 2
            text_y = scaled_rect.centery - option_text.get_height() // 2

            # Offset for checkmark if selected
            if is_selected and self.checkmark_scales[i].current > 0.1:
                text_x += 12

            text_surface = option_text.copy()
            text_surface.set_alpha(int(255 * alpha))
            screen.blit(text_surface, (text_x, text_y))

            # Animated checkmark for selected
            if is_selected and self.checkmark_scales[i].current > 0.1:
                check_scale = self.checkmark_scales[i].current
                check_size = int(20 * check_scale)
                check_x = scaled_rect.x + 12
                check_y = scaled_rect.centery - check_size // 2
                healthcare_visuals.draw_checkmark(screen, (check_x, check_y), check_size, (255, 255, 255))

        # Previous answers summary
        if self.current_question > 0:
            y_offset = 400
            summary_text = self.small_font.render("Previous answers:", True, HealthcareUIColors.TEXT_SECONDARY)
            screen.blit(summary_text, (form_rect.x + 50, y_offset))
            y_offset += 25

            for i in range(self.current_question):
                q = self.questions[i]
                if q['answer'] is not None:
                    # Checkmark icon
                    healthcare_visuals.draw_checkmark(screen, (form_rect.x + 55, y_offset + 2), 12,
                                                     HealthcareUIColors.SUCCESS)

                    answer_text = f"{q['question'][:45]}{'...' if len(q['question']) > 45 else ''} - {q['options'][q['answer']]}"
                    text = self.small_font.render(answer_text, True, HealthcareUIColors.TEXT_SECONDARY)
                    screen.blit(text, (form_rect.x + 75, y_offset))
                    y_offset += 22

        # Submit button (only show when all answered)
        all_answered = all(q['answer'] is not None for q in self.questions)
        if all_answered:
            scale = self.submit_scale.current
            btn_rect = pygame.Rect(
                self.submit_button.centerx - self.submit_button.width * scale / 2,
                self.submit_button.centery - self.submit_button.height * scale / 2,
                self.submit_button.width * scale,
                self.submit_button.height * scale
            )

            is_hovered = self.submit_button.collidepoint(mouse_pos)

            # Button with glow when hovered
            if is_hovered:
                glow_rect = btn_rect.inflate(10, 10)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*HealthcareUIColors.PRIMARY, 60),
                               glow_surface.get_rect(), border_radius=15)
                screen.blit(glow_surface, glow_rect.topleft)

            HealthcareVisualHelpers.draw_shadow(screen, btn_rect, offset=4, blur_radius=8)

            btn_color = HealthcareUIColors.PRIMARY_DARK if is_hovered else HealthcareUIColors.PRIMARY
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)

            submit_text = self.option_font.render("SUBMIT APPLICATION", True, (255, 255, 255))
            text_x = btn_rect.centerx - submit_text.get_width() // 2
            text_y = btn_rect.centery - submit_text.get_height() // 2
            screen.blit(submit_text, (text_x, text_y))

    def _render_processing(self, screen, form_rect):
        """Render processing animation"""
        # Processing spinner/dots
        center_x = self.SCREEN_WIDTH // 2
        center_y = 320

        # Animated dots
        dots = "Processing" + "." * (1 + (self.processing_timer // 20) % 3)
        proc_text = self.approval_font.render(dots, True, HealthcareUIColors.PRIMARY)
        screen.blit(proc_text, (center_x - proc_text.get_width() // 2, center_y))

        # Spinning indicator
        angle = (90 - self.processing_timer * 4) % 360
        radius = 30
        for i in range(8):
            dot_angle = math.radians(angle + i * 45)
            dot_x = center_x + math.cos(dot_angle) * radius
            dot_y = center_y + 60 + math.sin(dot_angle) * radius
            alpha = 255 - i * 25
            dot_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (*HealthcareUIColors.PRIMARY, alpha), (5, 5), 5 - i * 0.5)
            screen.blit(dot_surface, (dot_x - 5, dot_y - 5))

        # Submitting text
        sub_text = self.small_font.render("Verifying eligibility...", True, HealthcareUIColors.TEXT_SECONDARY)
        screen.blit(sub_text, (center_x - sub_text.get_width() // 2, center_y + 110))

    def _render_approval(self, screen, form_rect):
        """Render approval message with stamp effect"""
        scale = self.approval_scale.current

        # Approval card
        card_width = int(550 * scale)
        card_height = int(220 * scale)
        card_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - card_width // 2,
            280 - card_height // 2 + 50,
            card_width,
            card_height
        )

        if scale > 0.1:
            # Card shadow
            HealthcareVisualHelpers.draw_shadow(screen, card_rect, offset=8, blur_radius=12)

            # Card background with gradient
            card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            for y in range(card_rect.height):
                progress = y / card_rect.height
                color = HealthcareVisualHelpers.color_lerp(
                    HealthcareUIColors.SUCCESS,
                    (30, 160, 90),
                    progress * 0.3
                )
                pygame.draw.line(card_surface, color, (0, y), (card_rect.width, y))

            # Round corners
            mask = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=15)
            card_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            screen.blit(card_surface, card_rect.topleft)
            pygame.draw.rect(screen, (255, 255, 255, 100), card_rect, 3, border_radius=15)

            # Approval text
            if scale > 0.5:
                title = self.approval_font.render("APPLICATION APPROVED!", True, (255, 255, 255))
                screen.blit(title, (card_rect.centerx - title.get_width() // 2, card_rect.y + 25))

                lines = [
                    "You qualify for the Former Foster Youth program!",
                    "Coverage will be reinstated in 2 weeks.",
                    "Confirmation: FFY-2024-1847"
                ]

                y = card_rect.y + 80
                for line in lines:
                    line_text = self.small_font.render(line, True, (240, 255, 240))
                    screen.blit(line_text, (card_rect.centerx - line_text.get_width() // 2, y))
                    y += 28

            # Stamp effect
            stamp_scale = self.stamp_scale.current
            stamp_rotation = self.stamp_rotation.current

            if stamp_scale < 1.9:  # Only show after animation starts
                stamp_size = int(90 * stamp_scale)
                stamp_surface = pygame.Surface((stamp_size + 20, stamp_size + 20), pygame.SRCALPHA)

                # Stamp circle
                pygame.draw.circle(stamp_surface, (*HealthcareUIColors.SUCCESS, 200),
                                 (stamp_size // 2 + 10, stamp_size // 2 + 10), stamp_size // 2, 4)

                # APPROVED text
                stamp_text = pygame.font.Font(None, max(12, int(22 * stamp_scale))).render(
                    "APPROVED", True, (*HealthcareUIColors.SUCCESS, 200)
                )
                stamp_surface.blit(stamp_text,
                                  (stamp_size // 2 + 10 - stamp_text.get_width() // 2,
                                   stamp_size // 2 + 10 - stamp_text.get_height() // 2))

                # Rotate stamp
                rotated = pygame.transform.rotate(stamp_surface, stamp_rotation)
                stamp_x = card_rect.right - 80 - rotated.get_width() // 2
                stamp_y = card_rect.y + 40
                screen.blit(rotated, (stamp_x, stamp_y))

    def start(self):
        """Start the form filling mini-game"""
        self.active = True
        self.completed = False
        self.current_question = 0
        self.previous_question = -1
        self.form_submitted = False
        self.show_approval = False
        self.show_processing = False
        self.approval_timer = 0
        self.processing_timer = 0
        self.confetti_spawned = False

        # Reset answers
        for q in self.questions:
            q['answer'] = None

        # Reset animations
        self.form_scale = UIAnimation(0.9, 1.0, 0.3)
        self.form_alpha = UIAnimation(0.0, 1.0, 0.4)
        self.question_slide = UIAnimation(0.0, 0.0, 0.25)
        self.progress_fill = UIAnimation(0.0, 0.0, 0.4)
        self.submit_scale = UIAnimation(1.0, 1.0, 0.15)
        self.submit_pulse_timer = 0.0
        self.approval_scale = UIAnimation(0.0, 0.0, 0.3)
        self.stamp_rotation = UIAnimation(45.0, 45.0, 0.2)
        self.stamp_scale = UIAnimation(2.0, 2.0, 0.25)

        self.create_option_rects()

        # Clear any lingering particles/feedback
        healthcare_particles.particles.clear()
        healthcare_feedback.popups.clear()
        healthcare_feedback.achievements.clear()

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

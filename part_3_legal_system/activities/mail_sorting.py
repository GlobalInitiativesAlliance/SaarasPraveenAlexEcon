"""
Mail Sorting Mini-Game for Legal System Part
Drag and drop mail into trash or important pile
Upgraded with Part 5-style visuals: particles, animations, feedback system
"""
import pygame
import random
import math
import time

from .legal_visual_base import (
    LegalUIColors, LegalUIMetrics, LegalVisualHelpers,
    LegalVisualComponents, UIAnimation, legal_visuals
)
from .legal_particle_effects import LegalParticleSystem, legal_particles
from .legal_feedback_popups import LegalFeedbackManager, legal_feedback


class MailSortingGame:
    """Sort through scattered mail - junk to trash, important to desk

    Features:
    - Professional envelope graphics with shadows and gradients
    - Particle effects on sorting actions
    - Animated feedback popups
    - Glowing drop zones when hovering
    - Special court summons discovery effect
    - Completion celebration
    """

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Visual systems
        self.visuals = legal_visuals
        self.particles = LegalParticleSystem()
        self.feedback = LegalFeedbackManager()

        # Mail pieces
        self.mail_pieces = []
        self.create_mail_pieces()

        # Zones (made larger and positioned better)
        self.trash_zone = pygame.Rect(80, 480, 240, 180)
        self.desk_zone = pygame.Rect(960, 480, 240, 180)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.drag_start_pos = None

        # Hover states
        self.hovered_mail = None
        self.trash_highlighted = False
        self.desk_highlighted = False

        # Sorting progress
        self.correctly_sorted = 0
        self.total_important = 5
        self.junk_sorted = 0

        # Instructions
        self.show_instructions = True
        self.instruction_alpha = UIAnimation(current=1.0, target=1.0, speed=0.1)
        self.instruction_timer = 0

        # Found court notice
        self.found_court_notice = False
        self.court_notice_flash_time = 0

        # Animation timers
        self.pulse_time = 0
        self.shake_offset = (0, 0)
        self.shake_timer = 0

        # Completion state
        self.completion_timer = 0
        self.showing_completion = False

    def create_mail_pieces(self):
        """Create various mail pieces scattered on floor"""
        mail_types = [
            {'type': 'junk', 'label': 'SALE!'},
            {'type': 'junk', 'label': 'COUPON'},
            {'type': 'junk', 'label': 'AD'},
            {'type': 'junk', 'label': 'PROMO'},
            {'type': 'junk', 'label': 'OFFER'},
            {'type': 'important', 'label': 'COURT', 'is_court_notice': True},
            {'type': 'important', 'label': 'BILL'},
            {'type': 'important', 'label': 'NOTICE'},
            {'type': 'important', 'label': 'GOV'},
            {'type': 'important', 'label': 'URGENT'},
        ]

        # Shuffle and place mail
        random.shuffle(mail_types)

        for i, mail in enumerate(mail_types):
            # Spread mail across the middle area
            x = random.randint(350, 850)
            y = random.randint(120, 380)

            # Slightly larger envelopes for better visibility
            mail_piece = {
                'rect': pygame.Rect(x, y, 140, 90),
                'type': mail['type'],
                'label': mail['label'],
                'sorted': False,
                'is_court_notice': mail.get('is_court_notice', False),
                'hover_time': 0,
                'z_index': i  # For proper layering
            }

            self.mail_pieces.append(mail_piece)

    def start(self):
        """Start the activity"""
        self.active = True
        self.instruction_timer = time.time()
        self.particles.clear()
        self.feedback.clear()

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        # Update animation timers
        self.pulse_time += dt
        current_time = time.time()

        # Update visual systems
        self.particles.update(dt)
        self.feedback.update(dt)

        # Hide instructions after 4 seconds with fade
        if self.show_instructions:
            if current_time - self.instruction_timer > 3.0:
                self.instruction_alpha.target = 0.0
            if current_time - self.instruction_timer > 4.0:
                self.show_instructions = False

        self.instruction_alpha.update(dt)

        # Update shake effect
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset = (
                random.randint(-3, 3) * (self.shake_timer / 0.3),
                random.randint(-3, 3) * (self.shake_timer / 0.3)
            )
        else:
            self.shake_offset = (0, 0)

        # Check completion
        important_sorted = sum(1 for m in self.mail_pieces
                              if m['type'] == 'important' and m['sorted'])

        if important_sorted >= self.total_important and not self.showing_completion:
            self.showing_completion = True
            self.completion_timer = time.time()

            # Celebration effects
            center_x = self.SCREEN_WIDTH // 2
            center_y = self.SCREEN_HEIGHT // 2
            self.particles.emit_confetti(center_x, center_y - 100, count=80)
            self.feedback.add_complete(center_x, center_y)
            self.feedback.add_mail_sorted_achievement(found_all=True)

        # Auto-complete after celebration
        if self.showing_completion and current_time - self.completion_timer > 3.0:
            self.completed = True
            self.active = False

    def handle_key(self, key):
        """Handle keyboard input - ESC to exit"""
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False

    def handle_mouse_click(self, pos, button=1):
        """Start dragging mail (standard interface)"""
        if button != 1:  # Only left click
            return

        # Check mail pieces from top to bottom (highest z-index first)
        sorted_mail = sorted(self.mail_pieces, key=lambda m: m['z_index'], reverse=True)

        for mail in sorted_mail:
            if not mail['sorted'] and mail['rect'].collidepoint(pos):
                self.dragging = mail
                self.drag_start_pos = pos
                self.drag_offset = (
                    mail['rect'].x - pos[0],
                    mail['rect'].y - pos[1]
                )
                # Bring to top
                mail['z_index'] = max(m['z_index'] for m in self.mail_pieces) + 1

                # Start paper trail particles
                self.particles.emit_paper_trail(mail['rect'].centerx, mail['rect'].centery, count=3)
                break

    def handle_mouse_release(self, pos, button=1):
        """Drop mail and check if sorted correctly"""
        if not self.dragging:
            return

        mail = self.dragging
        center_x = mail['rect'].centerx
        center_y = mail['rect'].centery

        # Check if dropped in trash zone
        if self.trash_zone.colliderect(mail['rect']):
            if mail['type'] == 'junk':
                # Correct - junk goes to trash
                mail['sorted'] = True
                mail['rect'].x = -500  # Move off screen
                self.junk_sorted += 1

                # Success effects
                self.particles.emit_success(center_x, center_y)
                self.feedback.add_sorted(center_x, center_y, correct=True)
            else:
                # Wrong zone - bounce back with error
                self._bounce_back(mail)
                self.particles.emit_error(center_x, center_y)
                self.feedback.add_sorted(center_x, center_y, correct=False)
                self.shake_timer = 0.3

        # Check if dropped in desk zone
        elif self.desk_zone.colliderect(mail['rect']):
            if mail['type'] == 'important':
                # Correct - important goes to desk
                mail['sorted'] = True
                mail['rect'].x = -500  # Move off screen
                self.correctly_sorted += 1

                # Success effects
                self.particles.emit_success(center_x, center_y, count=20)
                self.feedback.add_sorted(center_x, center_y, correct=True)

                # Check if this was the court notice
                if mail.get('is_court_notice'):
                    self.found_court_notice = True
                    self.court_notice_flash_time = time.time()

                    # Special dramatic effects
                    self.particles.emit_court_summons_discovery(center_x, center_y)
                    self.feedback.add_court_summons_found(center_x, center_y - 50)
                    self.feedback.add_court_summons_achievement()
                    self.shake_timer = 0.5
                else:
                    self.feedback.add_found_important(center_x, center_y - 30, mail['label'])
            else:
                # Wrong zone - bounce back with error
                self._bounce_back(mail)
                self.particles.emit_error(center_x, center_y)
                self.feedback.add_sorted(center_x, center_y, correct=False)
                self.shake_timer = 0.3
        else:
            # Dropped in neutral zone - just leave it there
            pass

        self.dragging = None
        self.trash_highlighted = False
        self.desk_highlighted = False

    def _bounce_back(self, mail):
        """Bounce mail back to a random position"""
        mail['rect'].x = random.randint(350, 850)
        mail['rect'].y = random.randint(120, 380)

    def handle_mouse_motion(self, pos):
        """Move dragged mail with mouse and update hover states"""
        # Update hover state for mail
        self.hovered_mail = None
        if not self.dragging:
            for mail in self.mail_pieces:
                if not mail['sorted'] and mail['rect'].collidepoint(pos):
                    self.hovered_mail = mail
                    break

        # Move dragged mail
        if self.dragging:
            self.dragging['rect'].x = pos[0] + self.drag_offset[0]
            self.dragging['rect'].y = pos[1] + self.drag_offset[1]

            # Emit paper trail while dragging
            if random.random() < 0.3:  # 30% chance each frame
                self.particles.emit_paper_trail(
                    self.dragging['rect'].centerx,
                    self.dragging['rect'].centery,
                    count=2
                )

            # Update zone highlighting
            self.trash_highlighted = self.trash_zone.colliderect(self.dragging['rect'])
            self.desk_highlighted = self.desk_zone.colliderect(self.dragging['rect'])

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_release(event.pos, event.button)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)

    def draw(self, screen):
        """Draw the activity with enhanced visuals"""
        # Apply shake offset
        shake_x, shake_y = self.shake_offset

        # Draw wood background
        self.visuals.draw_wood_background(screen)

        # Court summons flash effect
        if self.found_court_notice:
            flash_elapsed = time.time() - self.court_notice_flash_time
            if flash_elapsed < 0.3:
                flash_alpha = int(150 * (1 - flash_elapsed / 0.3))
                flash_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                flash_surface.fill((255, 100, 100, flash_alpha))
                screen.blit(flash_surface, (0, 0))

        # Draw drop zones
        self.visuals.draw_drop_zone(
            screen,
            self.trash_zone.move(shake_x, shake_y),
            "TRASH",
            "trash",
            is_highlighted=self.trash_highlighted,
            pulse_time=self.pulse_time
        )

        self.visuals.draw_drop_zone(
            screen,
            self.desk_zone.move(shake_x, shake_y),
            "IMPORTANT",
            "important",
            is_highlighted=self.desk_highlighted,
            pulse_time=self.pulse_time
        )

        # Draw mail pieces (sorted by z-index)
        sorted_mail = sorted(self.mail_pieces, key=lambda m: m['z_index'])

        for mail in sorted_mail:
            if not mail['sorted']:
                is_dragging = (mail == self.dragging)
                is_hover = (mail == self.hovered_mail)

                # Determine mail type for visual
                if mail.get('is_court_notice'):
                    mail_type = 'legal'
                elif mail['type'] == 'junk':
                    mail_type = 'junk'
                else:
                    mail_type = 'important'

                rect = mail['rect'].move(shake_x, shake_y)

                self.visuals.draw_envelope(
                    screen,
                    rect,
                    mail_type=mail_type,
                    label=mail['label'],
                    is_dragging=is_dragging,
                    is_hover=is_hover,
                    is_court_notice=mail.get('is_court_notice', False)
                )

        # Draw particles
        self.particles.render(screen)

        # Draw instructions (with fade)
        if self.show_instructions and self.instruction_alpha.value > 0.01:
            self.visuals.draw_instruction_box(
                screen,
                "Sort the mail: Yellow to TRASH, White to IMPORTANT",
                alpha=self.instruction_alpha.value
            )

        # Draw progress counter
        self.visuals.draw_counter(
            screen,
            x=self.SCREEN_WIDTH - 250,
            y=25,
            current=self.correctly_sorted,
            total=self.total_important,
            label="Important Found:",
            color=LegalUIColors.LEGAL_GOLD
        )

        # Draw junk sorted counter (smaller, secondary)
        junk_font = self.visuals.fonts['small']
        junk_text = junk_font.render(f"Junk discarded: {self.junk_sorted}", True, LegalUIColors.TEXT_MUTED)
        screen.blit(junk_text, (self.SCREEN_WIDTH - 250, 60))

        # Draw court notice warning if found
        if self.found_court_notice:
            warning_rect = pygame.Rect(0, self.SCREEN_HEIGHT - 80, self.SCREEN_WIDTH, 60)
            warning_surface = pygame.Surface((warning_rect.width, warning_rect.height), pygame.SRCALPHA)

            # Pulsing background
            pulse = abs(math.sin(self.pulse_time * 2)) * 0.3 + 0.7
            pygame.draw.rect(warning_surface, (*LegalUIColors.URGENT, int(180 * pulse)),
                           (0, 0, warning_rect.width, warning_rect.height))

            screen.blit(warning_surface, warning_rect.topleft)

            # Warning text
            warning_font = self.visuals.fonts['heading']
            warning_text = warning_font.render("⚠ COURT SUMMONS DISCOVERED ⚠", True, LegalUIColors.TEXT_LIGHT)
            warning_text_rect = warning_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 50))
            screen.blit(warning_text, warning_text_rect)

        # Draw feedback popups
        self.feedback.render(screen)

        # Draw ESC hint
        esc_font = self.visuals.fonts['tiny']
        esc_text = esc_font.render("Press ESC to exit", True, LegalUIColors.TEXT_MUTED)
        esc_rect = esc_text.get_rect(bottomleft=(20, self.SCREEN_HEIGHT - 20))
        screen.blit(esc_text, esc_rect)

    def get_results(self):
        """Return results of the activity"""
        return {
            'court_notice_found': self.found_court_notice,
            'mail_sorted': self.correctly_sorted,
            'junk_sorted': self.junk_sorted,
            'total_important': self.total_important
        }

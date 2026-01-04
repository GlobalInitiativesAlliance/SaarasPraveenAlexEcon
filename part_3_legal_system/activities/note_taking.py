"""
Note-Taking Mini-Game for Legal System Part
Take notes while being distracted by text messages
Upgraded with Part 5-style visuals: particles, animations, feedback system
"""
import pygame
import random
import time
import math

from .legal_visual_base import (
    LegalUIColors, LegalUIMetrics, LegalVisualHelpers,
    LegalVisualComponents, UIAnimation, legal_visuals
)
from .legal_particle_effects import LegalParticleSystem
from .legal_feedback_popups import LegalFeedbackManager


class NoteTakingGame:
    """Take class notes while receiving distracting texts from boss

    Features:
    - Enhanced notebook and phone visuals
    - Particle effects on typing success
    - Stress vignette effect during distraction
    - Animated message bubbles
    - Progress bar with gradient
    - Achievement banners on completion
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

        # Notebook area
        self.notebook_rect = pygame.Rect(320, 140, 620, 420)

        # Phone area
        self.phone_rect = pygame.Rect(980, 180, 260, 480)
        self.phone_screen_rect = pygame.Rect(995, 230, 230, 380)

        # Text messages from boss
        self.boss_messages = [
            "Hey, need you tomorrow 7am SHARP",
            "Can't find anyone to cover",
            "You there???",
            "This is MANDATORY",
            "I'm scheduling you for doubles",
            "Reply ASAP!!!",
            "Missing this = write up",
            "Last warning about attendance"
        ]

        # Class notes to type
        self.class_notes = [
            "Chapter 7: Constitutional Rights",
            "Due process - fair treatment",
            "Right to legal representation",
            "Court procedures and filing",
            "Important: Always appear on scheduled dates"
        ]

        # Game state
        self.current_note_index = 0
        self.typed_text = ""
        self.current_target = self.class_notes[0]
        self.messages_received = []
        self.last_message_time = 0
        self.message_interval = 3000  # 3 seconds between texts
        self.start_time = 0
        self.typing_enabled = True
        self.distraction_level = 0
        self.max_distraction = 10
        self.focus_timer = 0

        # Performance tracking
        self.notes_completed = 0
        self.errors = 0
        self.phone_vibrating = False
        self.vibrate_timer = 0
        self.vibrate_start_time = 0

        # Animation state
        self.cursor_visible = True
        self.cursor_timer = 0
        self.message_animations = []  # Track message slide-in animations
        self.vignette_intensity = UIAnimation(current=0, target=0, speed=0.1)
        self.completion_shown = False
        self.pulse_time = 0

        # Phone notification badge
        self.unread_count = 0

    def start(self):
        """Start the activity"""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.last_message_time = self.start_time
        self.particles.clear()
        self.feedback.clear()

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        current_time = pygame.time.get_ticks()
        self.pulse_time += dt

        # Update visual systems
        self.particles.update(dt)
        self.feedback.update(dt)

        # Update cursor blink
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # Send boss messages periodically
        if current_time - self.last_message_time > self.message_interval:
            self.send_boss_message()
            self.last_message_time = current_time

        # Update phone vibration
        if self.phone_vibrating:
            if current_time - self.vibrate_start_time > 600:
                self.phone_vibrating = False

        # Update message animations
        for anim in self.message_animations[:]:
            anim['progress'] = min(1.0, anim['progress'] + dt * 4)
            if anim['progress'] >= 1.0 and current_time - anim['start_time'] > 5000:
                self.message_animations.remove(anim)

        # Update distraction vignette
        if self.distraction_level > 3:
            self.vignette_intensity.target = min(0.4, self.distraction_level / self.max_distraction * 0.5)
        else:
            self.vignette_intensity.target = 0
        self.vignette_intensity.update(dt)

        # Reduce distraction over time
        if self.distraction_level > 0:
            self.distraction_level = max(0, self.distraction_level - dt * 0.3)

        # Check if all notes completed
        if self.notes_completed >= len(self.class_notes) and not self.completion_shown:
            self.completion_shown = True
            center_x = self.SCREEN_WIDTH // 2
            center_y = self.SCREEN_HEIGHT // 2

            self.particles.emit_confetti(center_x, center_y - 100, count=60)
            self.feedback.add_complete(center_x, center_y)

            # Calculate score for achievement
            score = self.notes_completed
            max_score = len(self.class_notes)
            self.feedback.add_note_taking_achievement(score, max_score)

        if self.completion_shown and self.notes_completed >= len(self.class_notes):
            # Wait a bit then complete
            if not hasattr(self, 'completion_timer'):
                self.completion_timer = current_time
            elif current_time - self.completion_timer > 3000:
                self.completed = True
                self.active = False

    def send_boss_message(self):
        """Add a new message from boss"""
        if len(self.messages_received) >= len(self.boss_messages):
            return

        message_index = len(self.messages_received) % len(self.boss_messages)
        message = self.boss_messages[message_index]

        current_time = pygame.time.get_ticks()

        self.messages_received.append({
            'text': message,
            'time': current_time,
            'read': False
        })

        # Add animation tracking
        self.message_animations.append({
            'index': len(self.messages_received) - 1,
            'progress': 0,
            'start_time': current_time
        })

        self.phone_vibrating = True
        self.vibrate_start_time = current_time
        self.distraction_level = min(self.distraction_level + 2.5, self.max_distraction)
        self.unread_count += 1

        # Emit warning particles near phone
        self.particles.emit_warning(
            self.phone_rect.centerx,
            self.phone_rect.top + 50,
            count=6
        )

    def handle_key(self, key):
        """Handle keyboard input"""
        # ESC to exit
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False
            return

        if not self.typing_enabled:
            return

        # Check for backspace
        if key == pygame.K_BACKSPACE:
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
        elif key == pygame.K_RETURN:
            # Check if current note is complete
            if self.typed_text.lower().strip() == self.current_target.lower().strip():
                self.notes_completed += 1
                self.typed_text = ""

                # Success effects
                center_x = self.notebook_rect.centerx
                center_y = self.notebook_rect.centery
                self.particles.emit_success(center_x, center_y, count=15)
                self.particles.emit_sparkle(center_x, center_y, count=8)
                self.feedback.add_correct(center_x, center_y)

                if self.notes_completed < len(self.class_notes):
                    self.current_note_index = self.notes_completed
                    self.current_target = self.class_notes[self.current_note_index]

    def handle_text_input(self, text):
        """Handle text input (proper way to handle typing)"""
        if not self.typing_enabled:
            return
        # Add the typed text
        self.typed_text += text

        # Small typing particle effect
        if len(self.typed_text) > 0:
            # Check if correct so far
            is_correct = self.typed_text == self.current_target[:len(self.typed_text)]
            if is_correct:
                # Small green particle
                self.particles.emit_glow(
                    self.notebook_rect.x + 30 + len(self.typed_text) * 8,
                    self.notebook_rect.y + 80,
                    color=(72, 187, 120),
                    radius=10,
                    count=2
                )

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.TEXTINPUT:
            self.handle_text_input(event.text)

    def draw(self, screen):
        """Draw the activity with enhanced visuals"""
        current_time = pygame.time.get_ticks()

        # Classroom background with gradient
        LegalVisualHelpers.draw_gradient_rect(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            (255, 250, 240),  # Warm cream top
            (240, 235, 225)   # Slightly darker bottom
        )

        # Draw chalkboard with better styling
        board_rect = pygame.Rect(40, 15, 1200, 110)
        self._draw_chalkboard(screen, board_rect)

        # Draw desk surface under notebook
        desk_rect = pygame.Rect(280, 130, 700, 450)
        LegalVisualHelpers.draw_gradient_rect(
            screen, desk_rect,
            LegalUIColors.WOOD_LIGHT,
            LegalUIColors.WOOD_MEDIUM,
            border_radius=8
        )
        pygame.draw.rect(screen, LegalUIColors.WOOD_LINE, desk_rect, 2, border_radius=8)

        # Draw notebook with enhanced styling
        self._draw_notebook(screen)

        # Draw phone with enhanced styling
        self._draw_phone(screen, current_time)

        # Draw particles
        self.particles.render(screen)

        # Draw progress bar
        progress = self.notes_completed / len(self.class_notes)
        progress_rect = pygame.Rect(40, 575, 250, 25)
        self.visuals.draw_progress_bar(
            screen, progress_rect, progress,
            label=f"Notes: {self.notes_completed}/{len(self.class_notes)}",
            color=LegalUIColors.LEGAL_GOLD
        )

        # Draw distraction indicator
        if self.distraction_level > 2:
            self._draw_distraction_indicator(screen)

        # Draw vignette effect for stress
        if self.vignette_intensity.value > 0.01:
            self._draw_stress_vignette(screen)

        # Draw feedback popups
        self.feedback.render(screen)

        # Draw instructions
        inst_font = self.visuals.fonts['small']
        inst_text = inst_font.render(
            "Type the gray text exactly, press ENTER to submit each note",
            True, LegalUIColors.TEXT_MUTED
        )
        inst_rect = inst_text.get_rect(bottomleft=(40, self.SCREEN_HEIGHT - 20))
        screen.blit(inst_text, inst_rect)

        # ESC hint
        esc_text = inst_font.render("Press ESC to exit", True, LegalUIColors.TEXT_MUTED)
        esc_rect = esc_text.get_rect(bottomright=(self.SCREEN_WIDTH - 20, self.SCREEN_HEIGHT - 20))
        screen.blit(esc_text, esc_rect)

    def _draw_chalkboard(self, screen, rect):
        """Draw enhanced chalkboard"""
        # Board shadow
        shadow_rect = rect.move(4, 4)
        pygame.draw.rect(screen, (20, 40, 20), shadow_rect, border_radius=4)

        # Board surface with gradient
        LegalVisualHelpers.draw_gradient_rect(
            screen, rect,
            (35, 70, 35),
            (25, 50, 25),
            border_radius=4
        )

        # Wooden frame
        pygame.draw.rect(screen, (120, 80, 50), rect, 6, border_radius=4)
        pygame.draw.rect(screen, (90, 60, 35), rect, 3, border_radius=4)

        # Chalk text with slight glow effect
        chalk_font = self.visuals.fonts['heading']
        title = "Legal Studies 101 - Know Your Rights"
        chalk_text = chalk_font.render(title, True, (255, 255, 255))
        chalk_rect = chalk_text.get_rect(center=rect.center)
        screen.blit(chalk_text, chalk_rect)

    def _draw_notebook(self, screen):
        """Draw enhanced notebook"""
        rect = self.notebook_rect

        # Notebook shadow
        LegalVisualHelpers.draw_shadow(screen, rect, offset=6, alpha=40, border_radius=4)

        # Paper background
        pygame.draw.rect(screen, (255, 255, 250), rect, border_radius=4)

        # Red margin line
        margin_x = rect.x + 50
        pygame.draw.line(screen, (255, 200, 200), (margin_x, rect.y + 10), (margin_x, rect.bottom - 10), 2)

        # Blue ruled lines
        for i in range(12):
            y = rect.y + 35 + (i * 32)
            if y < rect.bottom - 20:
                pygame.draw.line(screen, (220, 230, 255),
                               (rect.x + 20, y),
                               (rect.right - 20, y), 1)

        # Spiral binding holes
        for i in range(15):
            y = rect.y + 25 + (i * 28)
            if y < rect.bottom - 20:
                pygame.draw.circle(screen, (200, 200, 200), (rect.x + 15, y), 5)
                pygame.draw.circle(screen, (255, 255, 250), (rect.x + 15, y), 3)

        # Border
        pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=4)

        # Draw target text (what to type)
        target_font = self.visuals.fonts['body']
        target_surface = target_font.render(self.current_target, True, (180, 180, 180))
        target_rect = target_surface.get_rect(x=rect.x + 60, y=rect.y + 45)
        screen.blit(target_surface, target_rect)

        # Label above
        label_font = self.visuals.fonts['tiny']
        label_text = label_font.render("Type this:", True, LegalUIColors.TEXT_MUTED)
        screen.blit(label_text, (rect.x + 60, rect.y + 25))

        # Draw typed text with color coding
        if self.typed_text:
            is_correct = self.typed_text == self.current_target[:len(self.typed_text)]
            typed_color = LegalUIColors.SUCCESS if is_correct else LegalUIColors.ERROR
            typed_surface = target_font.render(self.typed_text, True, typed_color)
            typed_rect = typed_surface.get_rect(x=rect.x + 60, y=rect.y + 85)
            screen.blit(typed_surface, typed_rect)

            # Draw cursor
            if self.cursor_visible:
                cursor_x = typed_rect.right + 2
                cursor_y = typed_rect.y
                pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + 22), 2)
        else:
            # Draw cursor at start
            if self.cursor_visible:
                cursor_x = rect.x + 60
                cursor_y = rect.y + 85
                pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + 22), 2)

        # Note progress within notebook
        note_num_font = self.visuals.fonts['tiny']
        note_num_text = note_num_font.render(
            f"Note {self.current_note_index + 1} of {len(self.class_notes)}",
            True, LegalUIColors.TEXT_MUTED
        )
        screen.blit(note_num_text, (rect.right - 120, rect.bottom - 25))

    def _draw_phone(self, screen, current_time):
        """Draw enhanced phone with messages"""
        rect = self.phone_rect

        # Phone vibration offset
        vibrate_offset = (0, 0)
        if self.phone_vibrating:
            elapsed = current_time - self.vibrate_start_time
            if elapsed < 600:
                intensity = 3 * (1 - elapsed / 600)
                vibrate_offset = (
                    int(math.sin(elapsed * 0.05) * intensity),
                    int(math.cos(elapsed * 0.07) * intensity)
                )

        phone_rect = rect.move(*vibrate_offset)

        # Phone shadow
        LegalVisualHelpers.draw_shadow(screen, phone_rect, offset=8, alpha=60, border_radius=20)

        # Phone body (dark with rounded corners)
        pygame.draw.rect(screen, (30, 30, 35), phone_rect, border_radius=20)

        # Phone screen
        screen_rect = pygame.Rect(
            phone_rect.x + 12,
            phone_rect.y + 50,
            phone_rect.width - 24,
            phone_rect.height - 100
        )
        pygame.draw.rect(screen, (245, 248, 255), screen_rect, border_radius=8)

        # Status bar
        status_rect = pygame.Rect(screen_rect.x, screen_rect.y, screen_rect.width, 25)
        pygame.draw.rect(screen, (235, 238, 245), status_rect,
                        border_top_left_radius=8, border_top_right_radius=8)

        time_font = self.visuals.fonts['tiny']
        time_text = time_font.render("BOSS", True, (100, 100, 100))
        screen.blit(time_text, (status_rect.centerx - 15, status_rect.y + 5))

        # Notification badge
        if self.unread_count > 0:
            badge_x = phone_rect.right - 25
            badge_y = phone_rect.top + 35
            pygame.draw.circle(screen, LegalUIColors.ERROR, (badge_x, badge_y), 12)
            badge_text = self.visuals.fonts['tiny'].render(
                str(min(self.unread_count, 9)), True, (255, 255, 255)
            )
            badge_rect = badge_text.get_rect(center=(badge_x, badge_y))
            screen.blit(badge_text, badge_rect)

        # Draw messages
        msg_area = pygame.Rect(
            screen_rect.x + 5,
            screen_rect.y + 30,
            screen_rect.width - 10,
            screen_rect.height - 35
        )

        message_font = self.visuals.fonts['tiny']
        y_offset = 0

        # Show last 5 messages that fit
        visible_messages = self.messages_received[-5:]
        for i, msg in enumerate(visible_messages):
            # Calculate animation progress
            anim_progress = 1.0
            for anim in self.message_animations:
                if anim['index'] == len(self.messages_received) - len(visible_messages) + i:
                    anim_progress = self._ease_out(anim['progress'])
                    break

            # Message bubble with slide-in animation
            bubble_height = 50
            bubble_x = msg_area.x + int((1 - anim_progress) * 50)
            bubble_rect = pygame.Rect(
                bubble_x,
                msg_area.y + y_offset,
                msg_area.width - 10,
                bubble_height
            )

            if bubble_rect.bottom < msg_area.bottom:
                # Bubble background with alpha
                bubble_surface = pygame.Surface((bubble_rect.width, bubble_rect.height), pygame.SRCALPHA)
                alpha = int(255 * anim_progress)
                pygame.draw.rect(bubble_surface, (100, 180, 100, alpha),
                               (0, 0, bubble_rect.width, bubble_rect.height),
                               border_radius=10)
                screen.blit(bubble_surface, bubble_rect.topleft)

                # Message text
                lines = self._wrap_text(msg['text'], message_font, bubble_rect.width - 15)
                for j, line in enumerate(lines[:2]):  # Max 2 lines
                    text_surface = message_font.render(line, True, (255, 255, 255))
                    text_surface.set_alpha(alpha)
                    screen.blit(text_surface, (bubble_rect.x + 8, bubble_rect.y + 6 + (j * 18)))

            y_offset += bubble_height + 8

        # Phone home button
        button_y = phone_rect.bottom - 35
        pygame.draw.circle(screen, (60, 60, 65), (phone_rect.centerx, button_y), 15)
        pygame.draw.circle(screen, (80, 80, 85), (phone_rect.centerx, button_y), 12)

        # Glow effect when vibrating
        if self.phone_vibrating:
            glow_surface = pygame.Surface((phone_rect.width + 20, phone_rect.height + 20), pygame.SRCALPHA)
            elapsed = current_time - self.vibrate_start_time
            glow_alpha = int(80 * (1 - elapsed / 600))
            pygame.draw.rect(glow_surface, (100, 200, 100, glow_alpha),
                           (10, 10, phone_rect.width, phone_rect.height),
                           border_radius=20)
            screen.blit(glow_surface, (phone_rect.x - 10, phone_rect.y - 10))

    def _draw_distraction_indicator(self, screen):
        """Draw distraction warning with animation"""
        # Pulsing effect
        pulse = abs(math.sin(self.pulse_time * 4)) * 0.3 + 0.7

        # Warning bar at bottom
        warning_rect = pygame.Rect(40, 620, 250, 35)
        warning_surface = pygame.Surface((warning_rect.width, warning_rect.height), pygame.SRCALPHA)

        # Background
        bg_alpha = int(200 * pulse)
        pygame.draw.rect(warning_surface, (*LegalUIColors.WARNING, bg_alpha),
                        (0, 0, warning_rect.width, warning_rect.height),
                        border_radius=8)

        screen.blit(warning_surface, warning_rect.topleft)

        # Distraction level bar
        level_pct = self.distraction_level / self.max_distraction
        bar_rect = pygame.Rect(warning_rect.x + 10, warning_rect.y + 20, 230, 8)
        pygame.draw.rect(screen, (255, 255, 255, 100), bar_rect, border_radius=4)

        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * level_pct), bar_rect.height)
        pygame.draw.rect(screen, LegalUIColors.ERROR, fill_rect, border_radius=4)

        # Text
        warning_font = self.visuals.fonts['small']
        warning_text = warning_font.render("DISTRACTED!", True, (255, 255, 255))
        screen.blit(warning_text, (warning_rect.x + 10, warning_rect.y + 3))

    def _draw_stress_vignette(self, screen):
        """Draw vignette effect around edges to show stress"""
        intensity = self.vignette_intensity.value
        width, height = screen.get_size()

        # Create vignette surface
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw gradient edges
        edge_width = 100
        for x in range(edge_width):
            alpha = int(255 * intensity * (1 - x / edge_width))
            # Left edge
            pygame.draw.line(vignette, (180, 50, 50, alpha), (x, 0), (x, height))
            # Right edge
            pygame.draw.line(vignette, (180, 50, 50, alpha), (width - x - 1, 0), (width - x - 1, height))

        for y in range(edge_width):
            alpha = int(255 * intensity * (1 - y / edge_width))
            # Top edge
            pygame.draw.line(vignette, (180, 50, 50, alpha), (0, y), (width, y))
            # Bottom edge
            pygame.draw.line(vignette, (180, 50, 50, alpha), (0, height - y - 1), (width, height - y - 1))

        screen.blit(vignette, (0, 0))

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _ease_out(self, t):
        """Ease out cubic function"""
        return 1 - pow(1 - t, 3)

    def get_results(self):
        """Return results of the activity"""
        return {
            'notes_completed': self.notes_completed,
            'total_notes': len(self.class_notes),
            'messages_received': len(self.messages_received),
            'stress': int(self.distraction_level * 5)  # Convert to stress points
        }

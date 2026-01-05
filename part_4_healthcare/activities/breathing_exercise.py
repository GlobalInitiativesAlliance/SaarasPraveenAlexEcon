"""
Breathing Exercise Mini-Game for Anxiety Management
Match inhale and exhale timing to manage anxiety at work
UPGRADED with healthcare visual system - calming visuals, particles, atmosphere
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


class BreathingExerciseGame:
    """Match inhale/exhale timing to manage anxiety during work shift"""

    # Calming color palette
    INHALE_COLOR = (82, 152, 219)      # Soft blue
    EXHALE_COLOR = (46, 204, 113)      # Calm green
    HOLD_COLOR = (155, 89, 182)        # Gentle purple
    CALM_BG = (25, 35, 50)             # Dark calm blue
    STRESSED_BG = (50, 30, 35)         # Dark stressed red

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.failed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Breathing parameters
        self.breath_phase = 'inhale'  # 'inhale', 'hold', 'exhale'
        self.breath_timer = 0
        self.inhale_duration = 4.0  # seconds
        self.hold_duration = 2.0
        self.exhale_duration = 4.0
        self.current_duration = self.inhale_duration
        self.phase_just_changed = False

        # Player interaction
        self.player_holding = False
        self.accuracy_score = 0
        self.breaths_completed = 0
        self.breaths_required = 3
        self.mistakes = 0
        self.max_mistakes = 3

        # Visual elements
        self.circle_radius = 50
        self.max_circle_radius = 150
        self.current_radius = UIAnimation(self.circle_radius, self.circle_radius, 0.1)
        self.circle_glow = UIAnimation(0.0, 0.0, 0.3)

        # Ripple effect on phase change
        self.ripples = []  # List of {radius, alpha, max_radius}

        # Timing windows
        self.perfect_window = 0.3
        self.good_window = 0.6

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0
        self.instruction_alpha = UIAnimation(1.0, 1.0, 0.5)

        # Phase text animation
        self.phase_text_alpha = UIAnimation(1.0, 1.0, 0.3)
        self.phase_text_y_offset = UIAnimation(0.0, 0.0, 0.2)

        # Anxiety meter
        self.anxiety_level = 100
        self.anxiety_display = UIAnimation(100.0, 100.0, 0.5)
        self.target_anxiety = 30

        # Heartbeat animation
        self.heartbeat_timer = 0
        self.heartbeat_scale = UIAnimation(1.0, 1.0, 0.1)

        # Background atmosphere
        self.bg_transition = UIAnimation(1.0, 1.0, 0.8)  # 1.0 = stressed, 0.0 = calm

        # Vignette intensity (higher when stressed)
        self.vignette_intensity = UIAnimation(0.6, 0.6, 0.5)

        # Result display
        self.result_scale = UIAnimation(0.0, 0.0, 0.3)
        self.result_timer = 0
        self.confetti_spawned = False

        # Particle emission timer
        self.particle_emit_timer = 0

        # Fonts
        self.phase_font = pygame.font.Font(None, 52)
        self.progress_font = pygame.font.Font(None, 32)
        self.label_font = pygame.font.Font(None, 24)
        self.instruction_font = pygame.font.Font(None, 28)
        self.result_font = pygame.font.Font(None, 42)

    def handle_event(self, event):
        """Handle breathing input (spacebar)"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player_holding = True
                self.check_timing()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.player_holding = False

        return True

    def check_timing(self):
        """Check if player pressed space at the right time"""
        if self.breath_phase == 'inhale':
            phase_progress = self.breath_timer / self.inhale_duration
            if phase_progress > 0.8:
                self.accuracy_score += 10
                healthcare_feedback.add_text(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 200, "Good!",
                                            HealthcareUIColors.SUCCESS)
        elif self.breath_phase == 'exhale':
            self.mistakes += 1
            healthcare_feedback.add_text(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 200, "Release!",
                                        HealthcareUIColors.ERROR)

    def _spawn_ripple(self):
        """Spawn a ripple effect"""
        self.ripples.append({
            'radius': self.current_radius.current,
            'alpha': 150,
            'max_radius': self.max_circle_radius + 100,
            'color': self._get_phase_color()
        })

    def _get_phase_color(self):
        """Get color for current phase"""
        if self.breath_phase == 'inhale':
            return self.INHALE_COLOR
        elif self.breath_phase == 'hold':
            return self.HOLD_COLOR
        else:
            return self.EXHALE_COLOR

    def update(self, dt):
        """Update breathing cycle and animations"""
        if not self.active:
            return

        # Update animations
        self.current_radius.update(dt)
        self.circle_glow.update(dt)
        self.phase_text_alpha.update(dt)
        self.phase_text_y_offset.update(dt)
        self.anxiety_display.update(dt)
        self.heartbeat_scale.update(dt)
        self.bg_transition.update(dt)
        self.vignette_intensity.update(dt)
        self.result_scale.update(dt)
        self.instruction_alpha.update(dt)

        # Update ripples
        for ripple in self.ripples[:]:
            ripple['radius'] += dt * 80
            ripple['alpha'] -= dt * 100
            if ripple['alpha'] <= 0 or ripple['radius'] >= ripple['max_radius']:
                self.ripples.remove(ripple)

        # Instruction fade
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 3:
                self.instruction_alpha.target = 0.0
            if self.instruction_timer > 4:
                self.show_instructions = False

        # Result timer
        if self.completed and self.result_timer > 0:
            self.result_timer -= dt

        # Skip breathing logic if completed
        if self.completed:
            healthcare_particles.update(dt)
            healthcare_feedback.update(dt)
            return

        # Update breath timer
        self.breath_timer += dt
        self.phase_just_changed = False

        # Heartbeat animation (faster when anxious)
        heartbeat_speed = 2 + (self.anxiety_level / 100) * 4  # 2-6 beats per second
        self.heartbeat_timer += dt * heartbeat_speed
        beat_phase = (math.sin(self.heartbeat_timer * math.pi * 2) + 1) / 2
        self.heartbeat_scale.current = 1.0 + beat_phase * 0.15 * (self.anxiety_level / 100)

        # Emit breath particles periodically during inhale/exhale
        self.particle_emit_timer += dt
        if self.particle_emit_timer > 0.15:
            self.particle_emit_timer = 0
            center_x = self.SCREEN_WIDTH // 2
            center_y = self.SCREEN_HEIGHT // 2
            angle = random.uniform(0, 2 * math.pi)
            radius = self.current_radius.current

            px = center_x + math.cos(angle) * radius
            py = center_y + math.sin(angle) * radius

            if self.breath_phase == 'inhale':
                healthcare_particles.emit_breath(px, py, phase='inhale', count=1)
            elif self.breath_phase == 'exhale':
                healthcare_particles.emit_breath(px, py, phase='exhale', count=1)

        # Update circle radius based on phase
        if self.breath_phase == 'inhale':
            progress = self.breath_timer / self.inhale_duration
            target = self.circle_radius + (self.max_circle_radius - self.circle_radius) * progress
            self.current_radius.target = target

            if self.breath_timer >= self.inhale_duration:
                self.breath_phase = 'hold'
                self.breath_timer = 0
                self.current_duration = self.hold_duration
                self.phase_just_changed = True
                self._spawn_ripple()
                self.phase_text_alpha.current = 0
                self.phase_text_alpha.target = 1.0
                self.phase_text_y_offset.current = 20
                self.phase_text_y_offset.target = 0

        elif self.breath_phase == 'hold':
            self.current_radius.target = self.max_circle_radius
            self.circle_glow.target = 0.5 + math.sin(self.breath_timer * 3) * 0.3

            if self.breath_timer >= self.hold_duration:
                self.breath_phase = 'exhale'
                self.breath_timer = 0
                self.current_duration = self.exhale_duration
                self.phase_just_changed = True
                self._spawn_ripple()
                self.phase_text_alpha.current = 0
                self.phase_text_alpha.target = 1.0
                self.phase_text_y_offset.current = 20
                self.phase_text_y_offset.target = 0
                self.circle_glow.target = 0

        elif self.breath_phase == 'exhale':
            progress = self.breath_timer / self.exhale_duration
            target = self.max_circle_radius - (self.max_circle_radius - self.circle_radius) * progress
            self.current_radius.target = target

            if self.breath_timer >= self.exhale_duration:
                self.breath_phase = 'inhale'
                self.breath_timer = 0
                self.current_duration = self.inhale_duration
                self.breaths_completed += 1
                self.phase_just_changed = True
                self._spawn_ripple()
                self.phase_text_alpha.current = 0
                self.phase_text_alpha.target = 1.0
                self.phase_text_y_offset.current = 20
                self.phase_text_y_offset.target = 0

                # Reduce anxiety with each completed breath
                old_anxiety = self.anxiety_level
                self.anxiety_level = max(30, self.anxiety_level - 25)
                self.anxiety_display.target = self.anxiety_level

                # Update atmosphere
                self.bg_transition.target = self.anxiety_level / 100
                self.vignette_intensity.target = 0.2 + (self.anxiety_level / 100) * 0.4

                # Feedback for anxiety reduction
                healthcare_particles.emit_anxiety_reduction(self.SCREEN_WIDTH // 2, 180)
                healthcare_feedback.add_anxiety_reduced(self.SCREEN_WIDTH // 2, 180, int(old_anxiety - self.anxiety_level))

        # Check for completion
        if self.breaths_completed >= self.breaths_required:
            self.completed = True
            self.result_scale.target = 1.0
            self.result_timer = 3.0

            if not self.confetti_spawned:
                healthcare_particles.emit_confetti(self.SCREEN_WIDTH // 2, 350, count=60)
                healthcare_feedback.add_breathing_complete()
                self.confetti_spawned = True

        # Check for failure
        if self.mistakes >= self.max_mistakes:
            self.failed = True
            self.completed = True
            self.result_scale.target = 1.0
            self.result_timer = 3.0

        # Update particles and feedback
        healthcare_particles.update(dt)
        healthcare_feedback.update(dt)

    def render(self, screen):
        """Render the breathing exercise interface with calming visuals"""
        if not self.active:
            return

        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        # Atmospheric background (transitions from stressed to calm)
        bg_lerp = self.bg_transition.current
        bg_color = HealthcareVisualHelpers.color_lerp(self.CALM_BG, self.STRESSED_BG, bg_lerp)

        # Gradient background
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            line_color = HealthcareVisualHelpers.color_lerp(
                bg_color,
                (bg_color[0] - 10, bg_color[1] - 10, bg_color[2] - 15),
                progress * 0.4
            )
            pygame.draw.line(screen, line_color, (0, y), (self.SCREEN_WIDTH, y))

        # Vignette effect (stronger when stressed)
        if self.vignette_intensity.current > 0.1:
            HealthcareVisualHelpers.draw_vignette(screen, self.vignette_intensity.current)

        # Draw ripple effects
        for ripple in self.ripples:
            ripple_surface = pygame.Surface((int(ripple['max_radius'] * 2), int(ripple['max_radius'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surface, (*ripple['color'], int(ripple['alpha'])),
                             (int(ripple['max_radius']), int(ripple['max_radius'])),
                             int(ripple['radius']), 3)
            screen.blit(ripple_surface,
                       (center_x - int(ripple['max_radius']), center_y - int(ripple['max_radius'])))

        # Outer guide circle with glow
        guide_surface = pygame.Surface((self.max_circle_radius * 2 + 40, self.max_circle_radius * 2 + 40), pygame.SRCALPHA)
        pygame.draw.circle(guide_surface, (80, 90, 110, 60),
                          (self.max_circle_radius + 20, self.max_circle_radius + 20),
                          self.max_circle_radius, 2)
        screen.blit(guide_surface, (center_x - self.max_circle_radius - 20, center_y - self.max_circle_radius - 20))

        # Breathing circle with gradient fill
        current_r = int(self.current_radius.current)
        phase_color = self._get_phase_color()

        # Circle glow
        glow_amount = self.circle_glow.current
        if glow_amount > 0.01:
            glow_radius = current_r + 20
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*phase_color, int(50 * glow_amount)),
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))

        # Main circle with soft gradient
        circle_surface = pygame.Surface((current_r * 2 + 10, current_r * 2 + 10), pygame.SRCALPHA)
        for r in range(current_r, 0, -3):
            progress = r / current_r
            alpha = int(180 + progress * 75)
            inner_color = HealthcareVisualHelpers.color_lerp(
                phase_color,
                (255, 255, 255),
                (1 - progress) * 0.2
            )
            pygame.draw.circle(circle_surface, (*inner_color, alpha),
                             (current_r + 5, current_r + 5), r)

        screen.blit(circle_surface, (center_x - current_r - 5, center_y - current_r - 5))

        # Inner focus point
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 8)
        pygame.draw.circle(screen, phase_color, (center_x, center_y), 4)

        # Phase instruction text with animation
        if self.breath_phase == 'inhale':
            instruction = "INHALE"
            hint = "Hold SPACE"
        elif self.breath_phase == 'hold':
            instruction = "HOLD"
            hint = "Keep holding..."
        else:
            instruction = "EXHALE"
            hint = "Release SPACE"

        text_alpha = int(self.phase_text_alpha.current * 255)
        text_y_offset = self.phase_text_y_offset.current

        phase_text = self.phase_font.render(instruction, True, phase_color)
        phase_text.set_alpha(text_alpha)
        screen.blit(phase_text, (center_x - phase_text.get_width() // 2,
                                center_y + self.max_circle_radius + 40 + text_y_offset))

        hint_text = self.label_font.render(hint, True, (180, 180, 190))
        hint_text.set_alpha(text_alpha)
        screen.blit(hint_text, (center_x - hint_text.get_width() // 2,
                               center_y + self.max_circle_radius + 90 + text_y_offset))

        # Progress indicator
        progress_text = self.progress_font.render(
            f"Breaths: {self.breaths_completed}/{self.breaths_required}",
            True, (200, 200, 210)
        )
        screen.blit(progress_text, (center_x - progress_text.get_width() // 2, 80))

        # Anxiety meter with heartbeat icon
        self._render_anxiety_meter(screen, center_x)

        # ESC hint
        esc_text = self.label_font.render("Press ESC to exit", True, (100, 100, 110))
        screen.blit(esc_text, (20, self.SCREEN_HEIGHT - 30))

        # Instructions overlay
        if self.show_instructions and self.instruction_alpha.current > 0.01:
            self._render_instructions(screen, center_x, center_y)

        # Result overlay
        if self.completed and self.result_scale.current > 0.01:
            self._render_result(screen, center_x, center_y)

        # Particles and feedback
        healthcare_particles.draw(screen)
        healthcare_feedback.draw(screen)

    def _render_anxiety_meter(self, screen, center_x):
        """Render anxiety meter with heartbeat icon"""
        meter_width = 280
        meter_height = 24
        meter_x = center_x - meter_width // 2
        meter_y = 135

        # Label
        label_text = self.label_font.render("Anxiety Level", True, (160, 160, 170))
        screen.blit(label_text, (center_x - label_text.get_width() // 2, meter_y - 22))

        # Meter background with rounded corners
        meter_rect = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
        pygame.draw.rect(screen, (40, 45, 55), meter_rect, border_radius=12)

        # Anxiety level fill with gradient
        fill_width = int((self.anxiety_display.current / 100) * (meter_width - 4))
        if fill_width > 4:
            fill_rect = pygame.Rect(meter_x + 2, meter_y + 2, fill_width, meter_height - 4)

            # Color based on anxiety level
            anxiety_ratio = self.anxiety_display.current / 100
            if anxiety_ratio > 0.6:
                fill_color = HealthcareUIColors.ERROR
            elif anxiety_ratio > 0.3:
                fill_color = HealthcareUIColors.WARNING
            else:
                fill_color = HealthcareUIColors.SUCCESS

            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=10)

        # Meter border
        pygame.draw.rect(screen, (70, 75, 85), meter_rect, 2, border_radius=12)

        # Heartbeat icon (pulsing)
        heart_scale = self.heartbeat_scale.current
        heart_x = meter_x - 40
        heart_y = meter_y + meter_height // 2

        heart_size = int(16 * heart_scale)
        heart_surface = pygame.Surface((heart_size * 2, heart_size * 2), pygame.SRCALPHA)

        # Simple heart shape using circles and triangle
        heart_color = HealthcareUIColors.ERROR if self.anxiety_display.current > 60 else HealthcareUIColors.SUCCESS
        hs = heart_size // 2
        pygame.draw.circle(heart_surface, heart_color, (hs, hs), hs // 2)
        pygame.draw.circle(heart_surface, heart_color, (hs + hs // 2, hs), hs // 2)
        pygame.draw.polygon(heart_surface, heart_color, [
            (hs // 3, hs),
            (hs, heart_size + hs // 3),
            (heart_size + hs // 3, hs)
        ])

        screen.blit(heart_surface, (heart_x - heart_size, heart_y - heart_size))

        # Anxiety percentage
        pct_text = self.label_font.render(f"{int(self.anxiety_display.current)}%", True, (180, 180, 190))
        screen.blit(pct_text, (meter_x + meter_width + 15, meter_y + 2))

    def _render_instructions(self, screen, center_x, center_y):
        """Render initial instructions"""
        alpha = int(self.instruction_alpha.current * 255)

        inst_surface = pygame.Surface((500, 160), pygame.SRCALPHA)
        pygame.draw.rect(inst_surface, (20, 25, 35, int(alpha * 0.9)),
                        inst_surface.get_rect(), border_radius=12)
        pygame.draw.rect(inst_surface, (60, 70, 90, alpha),
                        inst_surface.get_rect(), 2, border_radius=12)

        instructions = [
            "Match your breathing to the circle",
            "Hold SPACE during INHALE",
            "Release SPACE during EXHALE",
            "Complete 3 cycles to calm down"
        ]

        y_offset = 20
        for instruction in instructions:
            inst_text = self.instruction_font.render(instruction, True, (200, 210, 230))
            inst_text.set_alpha(alpha)
            inst_surface.blit(inst_text, (inst_surface.get_width() // 2 - inst_text.get_width() // 2, y_offset))
            y_offset += 32

        screen.blit(inst_surface, (center_x - 250, center_y + 200))

    def _render_result(self, screen, center_x, center_y):
        """Render completion result"""
        scale = self.result_scale.current

        # Dim background
        dim_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, int(120 * scale)))
        screen.blit(dim_surface, (0, 0))

        card_width = int(420 * scale)
        card_height = int(160 * scale)
        card_rect = pygame.Rect(
            center_x - card_width // 2,
            center_y - card_height // 2,
            card_width,
            card_height
        )

        if self.failed:
            # Failure card
            HealthcareVisualHelpers.draw_shadow(screen, card_rect, offset=8, blur_radius=15, alpha=60)

            card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            for y in range(card_rect.height):
                progress = y / card_rect.height
                color = HealthcareVisualHelpers.color_lerp(
                    HealthcareUIColors.ERROR,
                    (180, 60, 60),
                    progress * 0.3
                )
                pygame.draw.line(card_surface, color, (0, y), (card_rect.width, y))

            pygame.draw.rect(card_surface, (255, 255, 255), card_surface.get_rect(), 3, border_radius=15)
            screen.blit(card_surface, card_rect.topleft)

            if scale > 0.5:
                title = self.result_font.render("Too Anxious!", True, (255, 255, 255))
                screen.blit(title, (center_x - title.get_width() // 2, card_rect.y + 40))

                msg = self.instruction_font.render("You burned a burger!", True, (255, 220, 220))
                screen.blit(msg, (center_x - msg.get_width() // 2, card_rect.y + 95))

        else:
            # Success card
            HealthcareVisualHelpers.draw_shadow(screen, card_rect, offset=8, blur_radius=15, alpha=60)

            card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            for y in range(card_rect.height):
                progress = y / card_rect.height
                color = HealthcareVisualHelpers.color_lerp(
                    HealthcareUIColors.SUCCESS,
                    (35, 165, 90),
                    progress * 0.3
                )
                pygame.draw.line(card_surface, color, (0, y), (card_rect.width, y))

            pygame.draw.rect(card_surface, (255, 255, 255), card_surface.get_rect(), 3, border_radius=15)
            screen.blit(card_surface, card_rect.topleft)

            if scale > 0.5:
                # Checkmark icon
                check_size = 40
                check_x = center_x - check_size // 2
                check_y = card_rect.y + 20
                pygame.draw.circle(screen, (255, 255, 255, 200), (check_x + check_size // 2, check_y + check_size // 2), 25)
                healthcare_visuals.draw_checkmark(screen, (check_x + 7, check_y + 8), 26, HealthcareUIColors.SUCCESS)

                title = self.result_font.render("Anxiety Managed!", True, (255, 255, 255))
                screen.blit(title, (center_x - title.get_width() // 2, card_rect.y + 75))

                msg = self.instruction_font.render("You feel calmer now", True, (220, 255, 230))
                screen.blit(msg, (center_x - msg.get_width() // 2, card_rect.y + 115))

    def start(self):
        """Start the breathing exercise"""
        self.active = True
        self.completed = False
        self.failed = False
        self.breath_phase = 'inhale'
        self.breath_timer = 0
        self.breaths_completed = 0
        self.mistakes = 0
        self.anxiety_level = 100
        self.show_instructions = True
        self.instruction_timer = 0
        self.confetti_spawned = False
        self.ripples = []

        # Reset animations
        self.current_radius = UIAnimation(self.circle_radius, self.circle_radius, 0.1)
        self.circle_glow = UIAnimation(0.0, 0.0, 0.3)
        self.phase_text_alpha = UIAnimation(1.0, 1.0, 0.3)
        self.phase_text_y_offset = UIAnimation(0.0, 0.0, 0.2)
        self.anxiety_display = UIAnimation(100.0, 100.0, 0.5)
        self.heartbeat_scale = UIAnimation(1.0, 1.0, 0.1)
        self.bg_transition = UIAnimation(1.0, 1.0, 0.8)
        self.vignette_intensity = UIAnimation(0.6, 0.6, 0.5)
        self.result_scale = UIAnimation(0.0, 0.0, 0.3)
        self.instruction_alpha = UIAnimation(1.0, 1.0, 0.5)
        self.result_timer = 0

        # Clear particles/feedback
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

"""
Breathing Exercise Mini-Game for Legal System Part
Stay calm during police interaction
"""
import pygame
import math

class BreathingGame:
    """Breathing exercise to stay calm during police encounter"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Breathing circle
        self.center_x = self.SCREEN_WIDTH // 2
        self.center_y = self.SCREEN_HEIGHT // 2
        self.base_radius = 100
        self.max_radius = 200
        self.current_radius = self.base_radius

        # Breathing pattern
        self.breath_phase = 'inhale'  # 'inhale', 'hold', 'exhale'
        self.phase_timer = 0
        self.inhale_duration = 4000  # 4 seconds
        self.hold_duration = 4000    # 4 seconds
        self.exhale_duration = 4000   # 4 seconds

        # Player performance
        self.player_radius = self.base_radius
        self.correct_breaths = 0
        self.required_breaths = 3
        self.sync_score = 0
        self.is_breathing = False

        # Visual feedback
        self.feedback_text = ""
        self.feedback_timer = 0
        self.stress_level = 100  # Start stressed
        self.heart_rate = 120

        # Police dialogue
        self.officer_lines = [
            "I need to see your ID.",
            "Do you know why I stopped you?",
            "There's a warrant for missing court.",
            "You need to come to court within 48 hours.",
            "Here's your citation. Don't miss this one."
        ]
        self.current_line_index = 0
        self.dialogue_timer = 0
        self.show_dialogue = True

    def start(self):
        """Start the activity"""
        self.active = True
        self.phase_timer = pygame.time.get_ticks()
        self.dialogue_timer = pygame.time.get_ticks()

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        current_time = pygame.time.get_ticks()

        # Update breathing phase
        phase_elapsed = current_time - self.phase_timer

        if self.breath_phase == 'inhale':
            progress = phase_elapsed / self.inhale_duration
            self.current_radius = self.base_radius + (self.max_radius - self.base_radius) * progress

            if phase_elapsed >= self.inhale_duration:
                self.breath_phase = 'hold'
                self.phase_timer = current_time

        elif self.breath_phase == 'hold':
            self.current_radius = self.max_radius

            if phase_elapsed >= self.hold_duration:
                self.breath_phase = 'exhale'
                self.phase_timer = current_time

        elif self.breath_phase == 'exhale':
            progress = phase_elapsed / self.exhale_duration
            self.current_radius = self.max_radius - (self.max_radius - self.base_radius) * progress

            if phase_elapsed >= self.exhale_duration:
                self.breath_phase = 'inhale'
                self.phase_timer = current_time
                # Check breath completion
                self.check_breath_complete()

        # Update player radius smoothly
        if self.is_breathing:
            target = self.current_radius
            diff = target - self.player_radius
            self.player_radius += diff * 0.1

        # Calculate sync score
        radius_diff = abs(self.player_radius - self.current_radius)
        if radius_diff < 20:
            self.sync_score = min(100, self.sync_score + 1)
            self.stress_level = max(20, self.stress_level - 0.5)
        else:
            self.sync_score = max(0, self.sync_score - 0.5)
            self.stress_level = min(100, self.stress_level + 0.2)

        # Update heart rate based on stress
        self.heart_rate = 70 + int(self.stress_level * 0.5)

        # Update dialogue
        if current_time - self.dialogue_timer > 5000:
            self.current_line_index = min(self.current_line_index + 1, len(self.officer_lines) - 1)
            self.dialogue_timer = current_time

        # Clear feedback text after delay
        if self.feedback_timer > 0 and current_time - self.feedback_timer > 2000:
            self.feedback_text = ""
            self.feedback_timer = 0

        # Check completion
        if self.correct_breaths >= self.required_breaths:
            self.completed = True
            self.active = False

    def check_breath_complete(self):
        """Check if player completed a breath cycle successfully"""
        if self.sync_score > 70:
            self.correct_breaths += 1
            self.feedback_text = "Good breath!"
            self.feedback_timer = pygame.time.get_ticks()
        elif self.sync_score > 40:
            self.feedback_text = "Try to match the pattern"
            self.feedback_timer = pygame.time.get_ticks()
        else:
            self.feedback_text = "Focus on the circle"
            self.feedback_timer = pygame.time.get_ticks()

    def handle_key(self, key):
        """Handle keyboard input"""
        # ESC to exit
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False
            return

        if key == pygame.K_SPACE:
            self.is_breathing = not self.is_breathing

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                pass  # Could use for release if needed

    def draw(self, screen):
        """Draw the activity"""
        # Dark street background
        screen.fill((20, 20, 40))

        # Draw street lights effect
        for x in [200, 1080]:
            pygame.draw.circle(screen, (60, 60, 40), (x, 100), 150)

        # Draw breathing guide circle
        guide_color = (100, 100, 150)
        pygame.draw.circle(screen, guide_color, (self.center_x, self.center_y),
                         int(self.current_radius), 3)

        # Draw player's breathing circle
        if self.is_breathing:
            player_color = (100, 200, 100) if abs(self.player_radius - self.current_radius) < 20 else (200, 100, 100)
        else:
            player_color = (150, 150, 150)

        pygame.draw.circle(screen, player_color, (self.center_x, self.center_y),
                         int(self.player_radius), 5)

        # Draw phase indicator
        font = pygame.font.Font(None, 48)
        phase_text = self.breath_phase.upper()
        if self.breath_phase == 'inhale':
            instruction = "Press SPACE and breathe IN"
        elif self.breath_phase == 'hold':
            instruction = "HOLD your breath"
        else:
            instruction = "Breathe OUT slowly"

        phase_surface = font.render(phase_text, True, (255, 255, 255))
        phase_rect = phase_surface.get_rect(center=(self.center_x, self.center_y - 250))
        screen.blit(phase_surface, phase_rect)

        instruction_font = pygame.font.Font(None, 32)
        instruction_surface = instruction_font.render(instruction, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(self.center_x, self.center_y - 210))
        screen.blit(instruction_surface, instruction_rect)

        # Draw sync indicator
        sync_bar_rect = pygame.Rect(self.center_x - 150, 100, 300, 20)
        pygame.draw.rect(screen, (50, 50, 50), sync_bar_rect)
        sync_fill_rect = pygame.Rect(sync_bar_rect.x, sync_bar_rect.y,
                                    int(sync_bar_rect.width * (self.sync_score / 100)), 20)
        sync_color = (0, 200, 0) if self.sync_score > 70 else (200, 200, 0) if self.sync_score > 40 else (200, 0, 0)
        pygame.draw.rect(screen, sync_color, sync_fill_rect)

        sync_text = instruction_font.render("SYNC", True, (255, 255, 255))
        sync_text_rect = sync_text.get_rect(midright=(sync_bar_rect.x - 10, sync_bar_rect.centery))
        screen.blit(sync_text, sync_text_rect)

        # Draw stress level
        stress_text = instruction_font.render(f"Stress: {int(self.stress_level)}%", True,
                                            (255, 100, 100) if self.stress_level > 70 else (255, 255, 100))
        stress_rect = stress_text.get_rect(topleft=(50, 50))
        screen.blit(stress_text, stress_rect)

        # Draw heart rate
        heart_text = instruction_font.render(f"♥ {self.heart_rate} BPM", True,
                                           (255, 100, 100) if self.heart_rate > 100 else (100, 255, 100))
        heart_rect = heart_text.get_rect(topleft=(50, 90))
        screen.blit(heart_text, heart_rect)

        # Draw progress
        progress_text = instruction_font.render(f"Calm Breaths: {self.correct_breaths}/{self.required_breaths}",
                                              True, (255, 255, 255))
        progress_rect = progress_text.get_rect(topright=(self.SCREEN_WIDTH - 50, 50))
        screen.blit(progress_text, progress_rect)

        # Draw officer dialogue
        if self.show_dialogue and self.current_line_index < len(self.officer_lines):
            dialogue_rect = pygame.Rect(100, 550, 1080, 100)
            pygame.draw.rect(screen, (0, 0, 0), dialogue_rect)
            pygame.draw.rect(screen, (100, 100, 150), dialogue_rect, 3)

            dialogue_font = pygame.font.Font(None, 36)
            dialogue_text = dialogue_font.render(f'Officer: "{self.officer_lines[self.current_line_index]}"',
                                               True, (255, 255, 255))
            dialogue_text_rect = dialogue_text.get_rect(center=dialogue_rect.center)
            screen.blit(dialogue_text, dialogue_text_rect)

        # Draw feedback
        if self.feedback_text:
            feedback_font = pygame.font.Font(None, 40)
            feedback_surface = feedback_font.render(self.feedback_text, True, (100, 255, 100))
            feedback_rect = feedback_surface.get_rect(center=(self.center_x, self.center_y + 250))
            screen.blit(feedback_surface, feedback_rect)

        # ESC hint
        esc_font = pygame.font.Font(None, 24)
        esc_text = esc_font.render("Press ESC to exit", True, (150, 150, 150))
        esc_rect = esc_text.get_rect(bottomright=(self.SCREEN_WIDTH - 20, self.SCREEN_HEIGHT - 20))
        screen.blit(esc_text, esc_rect)

    def get_results(self):
        """Return results of the activity"""
        return {
            'stayed_calm': self.stress_level < 50,
            'final_stress': self.stress_level,
            'breaths_completed': self.correct_breaths
        }
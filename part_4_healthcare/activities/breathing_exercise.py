"""
Breathing Exercise Mini-Game for Anxiety Management
Match inhale and exhale timing to manage anxiety at work
"""
import pygame
import math

class BreathingExerciseGame:
    """Match inhale/exhale timing to manage anxiety during work shift"""

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
        self.current_radius = self.circle_radius
        self.target_radius = self.circle_radius

        # Timing windows
        self.perfect_window = 0.3  # seconds
        self.good_window = 0.6

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0

        # Colors
        self.INHALE_COLOR = (100, 150, 255)
        self.EXHALE_COLOR = (255, 150, 100)
        self.HOLD_COLOR = (150, 255, 150)
        self.BG_COLOR = (30, 30, 40)

        # Anxiety meter visual
        self.anxiety_level = 100  # Start high
        self.target_anxiety = 30  # Goal

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
            # Should be holding during inhale
            phase_progress = self.breath_timer / self.inhale_duration
            if phase_progress > 0.8:  # Near end of inhale
                self.accuracy_score += 10
        elif self.breath_phase == 'exhale':
            # Should release during exhale
            self.mistakes += 1

    def update(self, dt):
        """Update breathing cycle"""
        if not self.active:
            return

        # Update instruction timer
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 4:
                self.show_instructions = False

        # Update breath timer
        self.breath_timer += dt

        # Update circle radius based on phase
        if self.breath_phase == 'inhale':
            progress = self.breath_timer / self.inhale_duration
            self.target_radius = self.circle_radius + (self.max_circle_radius - self.circle_radius) * progress

            if self.breath_timer >= self.inhale_duration:
                self.breath_phase = 'hold'
                self.breath_timer = 0
                self.current_duration = self.hold_duration

        elif self.breath_phase == 'hold':
            self.target_radius = self.max_circle_radius

            if self.breath_timer >= self.hold_duration:
                self.breath_phase = 'exhale'
                self.breath_timer = 0
                self.current_duration = self.exhale_duration

        elif self.breath_phase == 'exhale':
            progress = self.breath_timer / self.exhale_duration
            self.target_radius = self.max_circle_radius - (self.max_circle_radius - self.circle_radius) * progress

            if self.breath_timer >= self.exhale_duration:
                self.breath_phase = 'inhale'
                self.breath_timer = 0
                self.current_duration = self.inhale_duration
                self.breaths_completed += 1

                # Reduce anxiety with each completed breath
                self.anxiety_level = max(30, self.anxiety_level - 25)

        # Smooth radius animation
        self.current_radius += (self.target_radius - self.current_radius) * 0.1

        # Check for completion
        if self.breaths_completed >= self.breaths_required:
            self.completed = True
            if self.objective_manager:
                self.objective_manager.complete_objective("breathing_game")

        # Check for failure
        if self.mistakes >= self.max_mistakes:
            self.failed = True
            self.completed = True

    def render(self, screen):
        """Render the breathing exercise interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(self.BG_COLOR)
        screen.blit(overlay, (0, 0))

        # Determine current color based on phase
        if self.breath_phase == 'inhale':
            color = self.INHALE_COLOR
            instruction = "INHALE - Hold SPACE"
        elif self.breath_phase == 'hold':
            color = self.HOLD_COLOR
            instruction = "HOLD"
        else:
            color = self.EXHALE_COLOR
            instruction = "EXHALE - Release SPACE"

        # Draw breathing circle
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        # Outer guide circle
        pygame.draw.circle(screen, (60, 60, 70), (center_x, center_y), self.max_circle_radius, 2)

        # Animated breathing circle
        pygame.draw.circle(screen, color, (center_x, center_y), int(self.current_radius))

        # Inner circle for focus point
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 10)

        # Phase instruction
        font = pygame.font.Font(None, 48)
        text = font.render(instruction, True, (255, 255, 255))
        screen.blit(text, (center_x - text.get_width()//2, center_y + self.max_circle_radius + 40))

        # Progress indicator
        progress_font = pygame.font.Font(None, 36)
        progress_text = progress_font.render(
            f"Breaths: {self.breaths_completed}/{self.breaths_required}",
            True, (200, 200, 200)
        )
        screen.blit(progress_text, (center_x - progress_text.get_width()//2, 100))

        # Anxiety meter
        meter_width = 300
        meter_height = 30
        meter_x = center_x - meter_width // 2
        meter_y = 150

        # Meter background
        pygame.draw.rect(screen, (50, 50, 50), (meter_x, meter_y, meter_width, meter_height))

        # Anxiety level fill
        fill_width = int((self.anxiety_level / 100) * meter_width)
        anxiety_color = (
            min(255, int(255 * (self.anxiety_level / 100))),
            min(255, int(100 + 155 * (1 - self.anxiety_level / 100))),
            100
        )
        pygame.draw.rect(screen, anxiety_color, (meter_x, meter_y, fill_width, meter_height))

        # Meter border
        pygame.draw.rect(screen, (100, 100, 100), (meter_x, meter_y, meter_width, meter_height), 2)

        # Anxiety label
        label_font = pygame.font.Font(None, 24)
        label_text = label_font.render("Anxiety Level", True, (180, 180, 180))
        screen.blit(label_text, (center_x - label_text.get_width()//2, meter_y - 25))

        # Instructions (initial)
        if self.show_instructions:
            inst_font = pygame.font.Font(None, 32)
            instructions = [
                "Match your breathing to the expanding circle",
                "Hold SPACE during INHALE",
                "Release SPACE during EXHALE",
                "Complete 3 breathing cycles to calm down"
            ]

            y_offset = center_y + 250
            for instruction in instructions:
                inst_text = inst_font.render(instruction, True, (200, 200, 255))
                screen.blit(inst_text, (center_x - inst_text.get_width()//2, y_offset))
                y_offset += 35

        # Failure message
        if self.failed:
            fail_rect = pygame.Rect(center_x - 200, center_y - 50, 400, 100)
            pygame.draw.rect(screen, (200, 50, 50), fail_rect)
            pygame.draw.rect(screen, (255, 255, 255), fail_rect, 3)

            fail_font = pygame.font.Font(None, 36)
            fail_text = fail_font.render("Too anxious! Burned a burger!", True, (255, 255, 255))
            screen.blit(fail_text, (center_x - fail_text.get_width()//2, center_y - 10))

        # Success message
        elif self.completed:
            success_rect = pygame.Rect(center_x - 200, center_y - 50, 400, 100)
            pygame.draw.rect(screen, (50, 200, 50), success_rect)
            pygame.draw.rect(screen, (255, 255, 255), success_rect, 3)

            success_font = pygame.font.Font(None, 36)
            success_text = success_font.render("Anxiety managed!", True, (255, 255, 255))
            screen.blit(success_text, (center_x - success_text.get_width()//2, center_y - 10))

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
        self.current_radius = self.circle_radius

    def stop(self):
        """Stop the mini-game"""
        self.active = False
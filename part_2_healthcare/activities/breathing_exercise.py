"""
Breathing Exercise Mini-Game
Match inhale and exhale timing to manage work anxiety
"""
import pygame
import math

class BreathingExerciseGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.phase = "inhale"  # inhale, hold, exhale, rest
        self.phase_timer = 0
        self.total_time = 0
        self.cycles_completed = 0
        self.target_cycles = 3
        self.success_count = 0

        # Timing (in seconds)
        self.phase_durations = {
            "inhale": 4.0,
            "hold": 2.0,
            "exhale": 6.0,
            "rest": 1.0
        }

        # Visual elements
        self.center_x = self.SCREEN_WIDTH // 2
        self.center_y = self.SCREEN_HEIGHT // 2
        self.base_radius = 80
        self.max_radius = 150

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.LIGHT_BLUE = (173, 216, 230)
        self.GOLD = (255, 215, 0)

        # Player input
        self.player_breathing = False  # True when space is held
        self.input_accuracy = []
        self.current_accuracy = 0

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Audio feedback (visual representation)
        self.feedback_timer = 0
        self.feedback_color = self.WHITE

    def handle_event(self, event):
        """Handle player input"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player_breathing = True
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.player_breathing = False

        return True

    def update(self, dt):
        """Update breathing exercise state"""
        if not self.active or self.completed:
            return

        self.phase_timer += dt
        self.total_time += dt
        self.feedback_timer -= dt

        # Check player input accuracy
        self.check_input_accuracy()

        # Phase transitions
        current_duration = self.phase_durations[self.phase]

        if self.phase_timer >= current_duration:
            self.advance_phase()

        # Check completion
        if self.cycles_completed >= self.target_cycles:
            self.complete_exercise()

    def check_input_accuracy(self):
        """Check how well player is matching breathing pattern"""
        should_breathe = (self.phase == "inhale")
        is_breathing = self.player_breathing

        if should_breathe == is_breathing:
            self.current_accuracy += 1
            if self.current_accuracy > 60:  # Good for 1 second at 60fps
                self.feedback_color = self.GREEN
                self.feedback_timer = 0.2
        else:
            self.current_accuracy = max(0, self.current_accuracy - 2)
            self.feedback_color = self.RED
            self.feedback_timer = 0.2

    def advance_phase(self):
        """Move to next breathing phase"""
        # Record accuracy for this phase
        accuracy_percentage = min(100, (self.current_accuracy / 60) * 100)
        self.input_accuracy.append(accuracy_percentage)

        if accuracy_percentage >= 70:
            self.success_count += 1

        # Reset for next phase
        self.current_accuracy = 0
        self.phase_timer = 0

        # Advance phase
        if self.phase == "inhale":
            self.phase = "hold"
        elif self.phase == "hold":
            self.phase = "exhale"
        elif self.phase == "exhale":
            self.phase = "rest"
        elif self.phase == "rest":
            self.phase = "inhale"
            self.cycles_completed += 1

    def complete_exercise(self):
        """Complete the breathing exercise"""
        self.completed = True

        # Calculate overall success
        overall_accuracy = sum(self.input_accuracy) / len(self.input_accuracy) if self.input_accuracy else 0
        success = overall_accuracy >= 60

        if self.objective_manager:
            if success:
                self.objective_manager.complete_objective("breathing_exercise")
                # Success - no work consequences
            else:
                # Failed breathing exercise leads to work performance issues
                self.objective_manager.advance_to_next_objective()

    def get_current_radius(self):
        """Calculate circle radius based on breathing phase"""
        progress = self.phase_timer / self.phase_durations[self.phase]
        progress = min(1.0, progress)

        if self.phase == "inhale":
            # Expand from base to max
            return self.base_radius + (self.max_radius - self.base_radius) * progress
        elif self.phase == "hold":
            # Stay at max
            return self.max_radius
        elif self.phase == "exhale":
            # Shrink from max to base
            return self.max_radius - (self.max_radius - self.base_radius) * progress
        else:  # rest
            return self.base_radius

    def render(self, screen):
        """Render the breathing exercise interface"""
        if not self.active:
            return

        # Background
        screen.fill((20, 30, 40))

        # Title
        title = self.font_large.render("Breathing Exercise", True, self.WHITE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)

        # Instructions
        instructions = [
            "Hold SPACE when the circle expands (inhale)",
            "Release SPACE when the circle shrinks (exhale)",
            "Follow the rhythm to manage your anxiety"
        ]

        y = 120
        for instruction in instructions:
            text = self.font_small.render(instruction, True, self.LIGHT_BLUE)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
            screen.blit(text, text_rect)
            y += 25

        # Breathing circle
        current_radius = self.get_current_radius()

        # Outer guide circle
        pygame.draw.circle(screen, (50, 50, 50), (self.center_x, self.center_y), self.max_radius, 2)

        # Main breathing circle
        circle_color = self.BLUE
        if self.feedback_timer > 0:
            circle_color = self.feedback_color

        pygame.draw.circle(screen, circle_color, (self.center_x, self.center_y), int(current_radius))
        pygame.draw.circle(screen, self.WHITE, (self.center_x, self.center_y), int(current_radius), 3)

        # Phase indicator
        phase_text = self.phase.upper()
        phase_color = self.WHITE

        if self.phase == "inhale":
            phase_color = self.LIGHT_BLUE
        elif self.phase == "exhale":
            phase_color = self.GREEN
        elif self.phase == "hold":
            phase_color = self.GOLD

        phase_surface = self.font_large.render(phase_text, True, phase_color)
        phase_rect = phase_surface.get_rect(center=(self.center_x, self.center_y))
        screen.blit(phase_surface, phase_rect)

        # Progress indicator
        progress = self.phase_timer / self.phase_durations[self.phase]
        progress_width = 400
        progress_height = 20
        progress_x = (self.SCREEN_WIDTH - progress_width) // 2
        progress_y = self.center_y + 200

        # Progress bar background
        pygame.draw.rect(screen, (50, 50, 50),
                        (progress_x, progress_y, progress_width, progress_height))

        # Progress bar fill
        fill_width = int(progress_width * progress)
        pygame.draw.rect(screen, phase_color,
                        (progress_x, progress_y, fill_width, progress_height))

        # Progress bar border
        pygame.draw.rect(screen, self.WHITE,
                        (progress_x, progress_y, progress_width, progress_height), 2)

        # Cycle counter
        cycle_text = f"Cycle: {self.cycles_completed + 1}/{self.target_cycles}"
        cycle_surface = self.font_medium.render(cycle_text, True, self.WHITE)
        screen.blit(cycle_surface, (50, 50))

        # Input status
        input_status = "BREATHING" if self.player_breathing else "RESTING"
        input_color = self.GREEN if self.player_breathing else self.WHITE
        input_surface = self.font_medium.render(f"Input: {input_status}", True, input_color)
        screen.blit(input_surface, (50, 90))

        # Accuracy indicator
        current_acc = min(100, (self.current_accuracy / 60) * 100)
        acc_text = f"Accuracy: {current_acc:.0f}%"
        acc_color = self.GREEN if current_acc >= 70 else (self.RED if current_acc < 40 else self.WHITE)
        acc_surface = self.font_medium.render(acc_text, True, acc_color)
        screen.blit(acc_surface, (50, 130))

        # Completion message
        if self.completed:
            overall_accuracy = sum(self.input_accuracy) / len(self.input_accuracy) if self.input_accuracy else 0

            if overall_accuracy >= 60:
                message = "Exercise Complete! Anxiety managed successfully."
                message_color = self.GREEN
            else:
                message = "Exercise Complete. Anxiety still affecting performance..."
                message_color = self.RED

            message_surface = self.font_large.render(message, True, message_color)
            message_rect = message_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 600))

            # Message background
            bg_rect = message_rect.copy()
            bg_rect.inflate(40, 20)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, message_color, bg_rect, 2)

            screen.blit(message_surface, message_rect)

    def start(self):
        """Start the breathing exercise"""
        self.active = True
        self.completed = False
        self.phase = "inhale"
        self.phase_timer = 0
        self.total_time = 0
        self.cycles_completed = 0
        self.success_count = 0
        self.current_accuracy = 0
        self.input_accuracy = []
        self.player_breathing = False
        self.feedback_timer = 0

    def stop(self):
        """Stop the breathing exercise"""
        self.active = False
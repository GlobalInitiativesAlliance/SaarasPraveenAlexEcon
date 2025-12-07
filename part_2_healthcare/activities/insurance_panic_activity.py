"""
Insurance Panic Crisis Realization Activity
Interactive experience of realizing you have no insurance coverage for your therapy appointment
"""
import pygame
import math

class InsurancePanicActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.realization_progress = 0
        self.panic_level = 0  # Building panic intensity
        self.current_thought = 0
        self.thoughts_read = []
        self.reading_complete = False
        self.show_breakdown = False
        self.breakdown_timer = 0

        # Crisis realization thoughts
        self.panic_thoughts = [
            {
                "header": "💭 The Realization Hits",
                "content": "Wait... I need to bring my insurance card tomorrow. But I don't have insurance anymore.",
                "panic_weight": 20,
                "color": (100, 120, 150)
            },
            {
                "header": "💸 The Cost Reality",
                "content": "$150 for one therapy session. That's almost half my weekly food budget. How did healthcare get so expensive?",
                "panic_weight": 30,
                "color": (150, 100, 100)
            },
            {
                "header": "🤔 Desperate Calculations",
                "content": "If I skip meals for two weeks... If I don't pay that bill this month... Maybe I can find the money somewhere?",
                "panic_weight": 40,
                "color": (180, 90, 90)
            },
            {
                "header": "😰 The Impossible Choice",
                "content": "Cancel therapy and risk my mental health getting worse? Or pay and risk not having money for rent?",
                "panic_weight": 50,
                "color": (200, 70, 70)
            },
            {
                "header": "😢 The Harsh Truth",
                "content": "This is what happens when you age out of foster care. The safety nets disappear, one by one.",
                "panic_weight": 60,
                "color": (220, 50, 50)
            },
            {
                "header": "😣 Complete Overwhelm",
                "content": "I can't handle this. Everything feels impossible. Why does being an adult have to be so hard?",
                "panic_weight": 80,
                "color": (255, 30, 30)
            }
        ]

        # Visual elements
        self.thought_rects = []
        self.setup_thought_rects()

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (220, 220, 220)
        self.DARK_GRAY = (64, 64, 64)
        self.CRISIS_RED = (180, 40, 40)

        # Fonts
        self.font_header = pygame.font.Font(None, 32)
        self.font_content = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_crisis = pygame.font.Font(None, 48)

        # Animation state
        self.pulse_timer = 0
        self.shake_intensity = 0
        self.breathing_pattern = 0

    def setup_thought_rects(self):
        """Set up rectangles for panic thoughts"""
        self.thought_rects = []
        start_y = 120
        spacing = 90

        for i in range(len(self.panic_thoughts)):
            rect = pygame.Rect(100, start_y + (i * spacing), 1080, 80)
            self.thought_rects.append(rect)

    def start(self):
        """Start the insurance panic activity"""
        print("[INSURANCE_PANIC] Activity starting...")
        self.active = True
        self.completed = False
        self.realization_progress = 0
        self.panic_level = 0
        self.current_thought = 0
        self.thoughts_read = []
        self.reading_complete = False
        self.show_breakdown = False
        self.breakdown_timer = 0
        self.pulse_timer = 0
        self.shake_intensity = 0
        self.breathing_pattern = 0
        print("[INSURANCE_PANIC] Activity started successfully!")

    def stop(self):
        """Stop the insurance panic activity"""
        print("[INSURANCE_PANIC] Activity stopping...")
        self.active = False

    def handle_event(self, event):
        """Handle player input"""
        print(f"[INSURANCE_PANIC] handle_event called: active={self.active}, completed={self.completed}, event_type={event.type}")

        if not self.active or self.completed:
            print(f"[INSURANCE_PANIC] Ignoring event - not active or completed")
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("[INSURANCE_PANIC] Mouse click detected")
            if not self.reading_complete:
                self.advance_thought()
            elif self.show_breakdown:
                self.complete_activity()

        elif event.type == pygame.KEYDOWN:
            print(f"[INSURANCE_PANIC] Key pressed: {event.key}")
            if event.key == pygame.K_SPACE:
                print("[INSURANCE_PANIC] SPACE key pressed")
                if not self.reading_complete:
                    self.advance_thought()
                elif self.show_breakdown:
                    self.complete_activity()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        print(f"[INSURANCE_PANIC] handle_mouse_click called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        print(f"[INSURANCE_PANIC] handle_mouse_release called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONUP, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def advance_thought(self):
        """Advance to next panic thought"""
        print(f"[INSURANCE_PANIC] Advancing thought: current_thought={self.current_thought}")

        if self.current_thought < len(self.panic_thoughts):
            if self.current_thought not in self.thoughts_read:
                self.thoughts_read.append(self.current_thought)
                thought = self.panic_thoughts[self.current_thought]
                self.panic_level += thought["panic_weight"]

                # Add screen shake for high panic moments
                if thought["panic_weight"] >= 50:
                    self.shake_intensity = 15

                # Add breathing difficulty effect
                if self.panic_level > 150:
                    self.breathing_pattern = 20

            self.current_thought += 1

            if self.current_thought >= len(self.panic_thoughts):
                self.reading_complete = True
                self.show_breakdown = True
                self.breakdown_timer = 6.0  # 6 seconds of breakdown

    def complete_activity(self):
        """Complete the insurance panic activity"""
        print("[INSURANCE_PANIC] Completing activity...")
        self.completed = True

        if self.objective_manager:
            print("[INSURANCE_PANIC] Completed panic realization...")
            self.objective_manager.complete_current_objective()

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update timers
        self.pulse_timer += dt

        if self.shake_intensity > 0:
            self.shake_intensity = max(0, self.shake_intensity - dt * 30)

        if self.breathing_pattern > 0:
            self.breathing_pattern = max(0, self.breathing_pattern - dt * 5)

        # Update breakdown timer
        if self.show_breakdown and self.breakdown_timer > 0:
            self.breakdown_timer -= dt

    def draw_background(self, screen):
        """Draw the crisis background with visual effects"""
        # Base dark background
        base_color = (20, 20, 30)

        # Add panic color overlay based on panic level
        if self.panic_level > 0:
            intensity = min(self.panic_level / 300.0, 0.4)
            panic_overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            panic_color = (int(180 * intensity), int(40 * intensity), int(40 * intensity), int(intensity * 100))
            panic_overlay.fill(panic_color)
            screen.fill(base_color)
            screen.blit(panic_overlay, (0, 0))
        else:
            screen.fill(base_color)

    def draw_panic_thoughts(self, screen):
        """Draw the panic thoughts with progressive revelation"""
        for i, (thought, rect) in enumerate(zip(self.panic_thoughts, self.thought_rects)):
            if i >= self.current_thought and i not in self.thoughts_read:
                break

            # Apply screen shake to individual thought boxes
            shake_x = shake_y = 0
            if self.shake_intensity > 0:
                shake_x = math.sin(self.pulse_timer * 25 + i) * self.shake_intensity
                shake_y = math.cos(self.pulse_timer * 30 + i) * self.shake_intensity

            shaken_rect = rect.copy()
            shaken_rect.x += int(shake_x)
            shaken_rect.y += int(shake_y)

            # Thought background with panic color
            bg_color = thought["color"]
            if i in self.thoughts_read:
                # Add pulsing effect to read thoughts
                pulse = math.sin(self.pulse_timer * 4) * 0.2 + 0.8
                bg_color = tuple(int(c * pulse) for c in bg_color)

            pygame.draw.rect(screen, bg_color, shaken_rect, border_radius=10)
            pygame.draw.rect(screen, self.BLACK, shaken_rect, 3, border_radius=10)

            # Thought header
            header_surface = self.font_header.render(thought["header"], True, self.WHITE)
            header_pos = (shaken_rect.x + 20, shaken_rect.y + 10)
            screen.blit(header_surface, header_pos)

            # Thought content with word wrapping
            words = thought["content"].split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.font_content.size(test_line)[0] < shaken_rect.width - 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw content lines
            content_y = shaken_rect.y + 45
            for line in lines:
                content_surface = self.font_content.render(line, True, self.WHITE)
                screen.blit(content_surface, (shaken_rect.x + 20, content_y))
                content_y += 25

    def draw_panic_indicators(self, screen):
        """Draw panic level and breathing indicators"""
        # Panic level bar
        if self.panic_level > 0:
            bar_rect = pygame.Rect(50, 50, 300, 25)
            pygame.draw.rect(screen, self.DARK_GRAY, bar_rect)

            panic_ratio = min(self.panic_level / 300.0, 1.0)
            filled_width = int(bar_rect.width * panic_ratio)

            # Color gradient from yellow to red
            if panic_ratio < 0.3:
                panic_color = (255, 255, 100)  # Yellow
            elif panic_ratio < 0.7:
                panic_color = (255, 150, 50)   # Orange
            else:
                panic_color = (255, 50, 50)    # Red

            if filled_width > 0:
                filled_rect = pygame.Rect(bar_rect.x, bar_rect.y, filled_width, bar_rect.height)
                pygame.draw.rect(screen, panic_color, filled_rect)

            # Label
            panic_text = self.font_small.render(f"Panic Level: {int(panic_ratio * 100)}%", True, self.WHITE)
            screen.blit(panic_text, (bar_rect.x, bar_rect.y - 25))

        # Breathing difficulty indicator
        if self.breathing_pattern > 0:
            breath_y = 100
            breath_text = "Breathing: Difficult"
            breath_color = (255, 100, 100)

            # Pulsing text for breathing difficulty
            pulse = math.sin(self.pulse_timer * 6) * 0.3 + 0.7
            breath_surface = self.font_small.render(breath_text, True,
                                                  tuple(int(c * pulse) for c in breath_color))
            screen.blit(breath_surface, (50, breath_y))

    def draw_breakdown_sequence(self, screen):
        """Draw the breakdown sequence after reading all thoughts"""
        if not self.show_breakdown:
            return

        # Intense screen shake during breakdown
        if self.breakdown_timer > 3:
            shake_x = math.sin(self.pulse_timer * 40) * 20
            shake_y = math.cos(self.pulse_timer * 35) * 15
        else:
            shake_x = shake_y = 0

        # Crisis messages that appear over time
        crisis_messages = [
            "I can't do this...",
            "Everything is falling apart...",
            "I'm completely alone in this...",
            "How do other people manage?"
        ]

        message_y = 300
        for i, message in enumerate(crisis_messages):
            if self.breakdown_timer > (5 - i * 1.2):  # Stagger messages
                # Intense red text with shake effect
                text_x = self.SCREEN_WIDTH // 2 + int(shake_x)
                text_y = message_y + (i * 60) + int(shake_y)

                crisis_surface = self.font_crisis.render(message, True, (255, 30, 30))
                text_rect = crisis_surface.get_rect(center=(text_x, text_y))

                # Add text shadow for intensity
                shadow_surface = self.font_crisis.render(message, True, (100, 10, 10))
                shadow_rect = shadow_surface.get_rect(center=(text_x + 3, text_y + 3))
                screen.blit(shadow_surface, shadow_rect)
                screen.blit(crisis_surface, text_rect)

    def draw(self, screen):
        """Render the insurance panic crisis interface"""
        if not self.active:
            return

        # Draw background with panic effects
        self.draw_background(screen)

        # Title
        title = self.font_crisis.render("INSURANCE CRISIS", True, self.CRISIS_RED)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Draw panic thoughts
        self.draw_panic_thoughts(screen)

        # Draw panic indicators
        self.draw_panic_indicators(screen)

        # Draw breakdown sequence
        self.draw_breakdown_sequence(screen)

        # Instructions
        if not self.reading_complete:
            instruction = "Click or press SPACE to continue the realization..."
            instruction_surface = self.font_small.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)
        elif self.show_breakdown:
            instruction = "Click or press SPACE when ready to continue..."
            instruction_surface = self.font_small.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)

        # Progress indicator
        if not self.reading_complete:
            progress = len(self.thoughts_read) / len(self.panic_thoughts)
            progress_rect = pygame.Rect(100, self.SCREEN_HEIGHT - 80, 400, 12)
            pygame.draw.rect(screen, self.DARK_GRAY, progress_rect)
            filled_width = int(progress_rect.width * progress)
            if filled_width > 0:
                filled_rect = pygame.Rect(progress_rect.x, progress_rect.y, filled_width, progress_rect.height)
                pygame.draw.rect(screen, self.CRISIS_RED, filled_rect)
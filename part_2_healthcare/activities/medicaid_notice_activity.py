"""
Medicaid Notice Reading Activity
Interactive experience reading the coverage termination letter
"""
import pygame
import math

class MedicaidNoticeActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.reading_progress = 0  # How much of the letter has been read
        self.emotional_impact = 0  # Building emotional weight
        self.reading_speed = 20  # Characters per second
        self.current_section = 0
        self.sections_read = []

        # Letter sections with emotional weight
        self.letter_sections = [
            {
                "header": "STATE OF CALIFORNIA - DEPARTMENT OF HEALTH CARE SERVICES",
                "content": "NOTICE OF MEDICAID COVERAGE TERMINATION",
                "emotion": "neutral"
            },
            {
                "header": "Dear Former Foster Youth,",
                "content": "We regret to inform you that your Medi-Cal coverage under the Former Foster Care provision has been terminated effective immediately.",
                "emotion": "concern"
            },
            {
                "header": "REASON FOR TERMINATION:",
                "content": "You have reached the age of 26, which exceeds the maximum age limit for Former Foster Care Medicaid coverage.",
                "emotion": "shock"
            },
            {
                "header": "YOUR COVERAGE ENDS:",
                "content": "All medical, dental, and mental health benefits will cease as of the date of this notice. Any ongoing treatments may be interrupted.",
                "emotion": "anxiety"
            },
            {
                "header": "NEXT STEPS:",
                "content": "You may be eligible for other coverage options through Covered California. Please visit CoveredCA.com or call 1-800-300-1506.",
                "emotion": "overwhelm"
            },
            {
                "header": "IMPORTANT:",
                "content": "Failure to secure alternative coverage may result in significant medical costs and gaps in care for ongoing conditions.",
                "emotion": "panic"
            }
        ]

        # Visual elements
        self.letter_rect = pygame.Rect(200, 100, 880, 520)
        self.reading_complete = False
        self.show_realization = False
        self.realization_timer = 0

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (220, 220, 220)
        self.PAPER_WHITE = (248, 248, 248)
        self.GOVERNMENT_BLUE = (41, 84, 144)

        # Emotional colors
        self.emotion_colors = {
            "neutral": (100, 100, 100),
            "concern": (150, 120, 50),
            "shock": (180, 80, 50),
            "anxiety": (200, 100, 100),
            "overwhelm": (220, 60, 60),
            "panic": (255, 40, 40)
        }

        # Fonts
        self.font_header = pygame.font.Font(None, 24)
        self.font_content = pygame.font.Font(None, 20)
        self.font_title = pygame.font.Font(None, 32)
        self.font_impact = pygame.font.Font(None, 48)

        # Animation state
        self.pulse_timer = 0
        self.shake_intensity = 0

    def start(self):
        """Start the medicaid notice reading activity"""
        print("[MEDICAID_NOTICE] Activity starting...")
        self.active = True
        self.completed = False
        self.reading_progress = 0
        self.emotional_impact = 0
        self.current_section = 0
        self.sections_read = []
        self.reading_complete = False
        self.show_realization = False
        self.realization_timer = 0
        self.pulse_timer = 0
        self.shake_intensity = 0
        print("[MEDICAID_NOTICE] Activity started successfully!")

    def stop(self):
        """Stop the medicaid notice reading activity"""
        self.active = False

    def handle_event(self, event):
        """Handle player input"""
        print(f"[MEDICAID_NOTICE] handle_event called: active={self.active}, completed={self.completed}, event_type={event.type}")

        if not self.active or self.completed:
            print(f"[MEDICAID_NOTICE] Ignoring event - not active or completed")
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("[MEDICAID_NOTICE] Mouse click detected")
            if not self.reading_complete:
                # Speed up reading on click
                self.advance_reading()
            elif self.show_realization:
                # Complete the activity after reading and realization
                self.complete_activity()

        elif event.type == pygame.KEYDOWN:
            print(f"[MEDICAID_NOTICE] Key pressed: {event.key}")
            if event.key == pygame.K_SPACE:
                print("[MEDICAID_NOTICE] SPACE key pressed")
                if not self.reading_complete:
                    self.advance_reading()
                elif self.show_realization:
                    self.complete_activity()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        print(f"[MEDICAID_NOTICE] handle_mouse_click called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        print(f"[MEDICAID_NOTICE] handle_mouse_release called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONUP, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def advance_reading(self):
        """Advance to next section or speed up current reading"""
        if self.current_section < len(self.letter_sections):
            if self.current_section not in self.sections_read:
                self.sections_read.append(self.current_section)
                self.emotional_impact += 15

                # Add shake effect for more impactful sections
                if self.letter_sections[self.current_section]["emotion"] in ["shock", "anxiety", "panic"]:
                    self.shake_intensity = 10

            self.current_section += 1

            if self.current_section >= len(self.letter_sections):
                self.reading_complete = True
                self.show_realization = True
                self.realization_timer = 5.0  # 5 seconds of realization

    def complete_activity(self):
        """Complete the medicaid notice reading activity"""
        self.completed = True

        if self.objective_manager:
            print("[MEDICAID_NOTICE] Completed reading termination notice...")
            self.objective_manager.complete_current_objective()

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update timers
        self.pulse_timer += dt
        if self.shake_intensity > 0:
            self.shake_intensity = max(0, self.shake_intensity - dt * 20)

        # Update realization timer
        if self.show_realization and self.realization_timer > 0:
            self.realization_timer -= dt

        # Auto-advance reading slowly
        if not self.reading_complete and len(self.sections_read) == self.current_section:
            self.reading_progress += self.reading_speed * dt
            if self.reading_progress > 60:  # Auto advance after showing section for a bit
                self.advance_reading()
                self.reading_progress = 0

    def draw_letter_background(self, screen):
        """Draw the government letter background"""
        # Add slight shake for emotional impact
        shake_x = shake_y = 0
        if self.shake_intensity > 0:
            shake_x = (math.sin(self.pulse_timer * 20) * self.shake_intensity)
            shake_y = (math.cos(self.pulse_timer * 25) * self.shake_intensity)

        letter_rect = self.letter_rect.copy()
        letter_rect.x += int(shake_x)
        letter_rect.y += int(shake_y)

        # Paper shadow
        shadow_rect = letter_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (180, 180, 180), shadow_rect)

        # Paper background
        pygame.draw.rect(screen, self.PAPER_WHITE, letter_rect)
        pygame.draw.rect(screen, self.BLACK, letter_rect, 2)

        # Government header bar
        header_rect = pygame.Rect(letter_rect.x, letter_rect.y, letter_rect.width, 40)
        pygame.draw.rect(screen, self.GOVERNMENT_BLUE, header_rect)

        return letter_rect

    def draw_letter_content(self, screen, letter_rect):
        """Draw the letter content with progressive revelation"""
        y_pos = letter_rect.y + 60

        for i, section in enumerate(self.letter_sections):
            if i >= self.current_section and i not in self.sections_read:
                break

            # Section header
            emotion_color = self.emotion_colors.get(section["emotion"], self.BLACK)
            header_surface = self.font_header.render(section["header"], True, emotion_color)
            screen.blit(header_surface, (letter_rect.x + 20, y_pos))
            y_pos += 35

            # Section content with word wrapping
            words = section["content"].split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.font_content.size(test_line)[0] < letter_rect.width - 60:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw content lines
            for line in lines:
                content_surface = self.font_content.render(line, True, self.BLACK)
                screen.blit(content_surface, (letter_rect.x + 30, y_pos))
                y_pos += 25

            y_pos += 20  # Space between sections

    def draw_emotional_overlay(self, screen):
        """Draw emotional impact overlay"""
        if self.emotional_impact > 0:
            # Create emotional color overlay
            intensity = min(self.emotional_impact / 100.0, 0.3)
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(int(intensity * 100))

            # Color based on reading progress
            if self.emotional_impact < 30:
                overlay.fill((100, 100, 150))  # Mild concern
            elif self.emotional_impact < 60:
                overlay.fill((150, 100, 100))  # Growing anxiety
            else:
                overlay.fill((200, 80, 80))    # High stress

            screen.blit(overlay, (0, 0))

    def draw_realization_text(self, screen):
        """Draw realization text when reading is complete"""
        if not self.show_realization:
            return

        # Pulsing realization text
        pulse = math.sin(self.pulse_timer * 3) * 0.2 + 0.8

        realization_texts = [
            "Your healthcare coverage is gone...",
            "All your medications, therapy sessions...",
            "What happens to your mental health treatment?",
            "How will you afford medical care now?"
        ]

        y_start = 650
        for i, text in enumerate(realization_texts):
            if self.realization_timer > (4 - i):  # Stagger the realizations
                alpha = int(pulse * 255)
                color = (int(255 * pulse), int(100 * pulse), int(100 * pulse))

                text_surface = self.font_content.render(text, True, color)
                text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, y_start + i * 25))
                screen.blit(text_surface, text_rect)

    def draw(self, screen):
        """Render the medicaid notice reading interface"""
        if not self.active:
            return

        # Dark background for focus
        screen.fill((40, 40, 50))

        # Title
        title = self.font_title.render("OFFICIAL GOVERNMENT NOTICE", True, self.GOVERNMENT_BLUE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Draw letter
        letter_rect = self.draw_letter_background(screen)
        self.draw_letter_content(screen, letter_rect)

        # Draw emotional overlay
        self.draw_emotional_overlay(screen)

        # Draw realization text
        self.draw_realization_text(screen)

        # Instructions
        if not self.reading_complete:
            instruction = "Click or press SPACE to continue reading..."
            instruction_surface = self.font_content.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)
        elif self.show_realization:
            instruction = "Click or press SPACE to continue..."
            instruction_surface = self.font_content.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)

        # Reading progress indicator
        if not self.reading_complete:
            progress = len(self.sections_read) / len(self.letter_sections)
            progress_rect = pygame.Rect(100, self.SCREEN_HEIGHT - 60, 300, 10)
            pygame.draw.rect(screen, self.GRAY, progress_rect)
            filled_width = int(progress_rect.width * progress)
            if filled_width > 0:
                filled_rect = pygame.Rect(progress_rect.x, progress_rect.y, filled_width, progress_rect.height)
                pygame.draw.rect(screen, self.RED, filled_rect)
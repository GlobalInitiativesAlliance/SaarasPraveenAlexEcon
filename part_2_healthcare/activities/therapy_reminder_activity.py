"""
Therapy Reminder Phone Notification Activity
Interactive experience checking phone notification about upcoming therapy appointment
"""
import pygame
import math

class TherapyReminderActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.notification_progress = 0  # Reading progress
        self.emotional_impact = 0  # Building worry about cost
        self.current_section = 0
        self.sections_read = []
        self.reading_complete = False
        self.show_realization = False
        self.realization_timer = 0

        # Phone notification sections
        self.notification_sections = [
            {
                "header": "📱 PHONE NOTIFICATION",
                "content": "You have 1 new message",
                "emotion": "neutral"
            },
            {
                "header": "💬 From: Wellness Center",
                "content": "Reminder: You have a therapy appointment scheduled for tomorrow at 2:00 PM",
                "emotion": "neutral"
            },
            {
                "header": "📍 Location Details",
                "content": "Dr. Sarah Chen, Licensed Therapist\n123 Mental Health Way, Suite 205\nPlease arrive 15 minutes early for paperwork",
                "emotion": "neutral"
            },
            {
                "header": "💰 Important: Payment Required",
                "content": "Please be prepared to pay your copay at the time of service. Without insurance, the session fee is $150.",
                "emotion": "concern"
            },
            {
                "header": "⚠️ Cancellation Policy",
                "content": "24-hour notice required for cancellations. Late cancellations or no-shows will be charged the full session fee.",
                "emotion": "anxiety"
            },
            {
                "header": "🤔 Your Thoughts",
                "content": "Wait... $150? I don't have insurance anymore. How am I supposed to afford that? Do I cancel? But I really need this appointment...",
                "emotion": "panic"
            }
        ]

        # Visual elements
        self.phone_rect = pygame.Rect(340, 50, 600, 620)
        self.screen_rect = pygame.Rect(360, 100, 560, 520)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (220, 220, 220)
        self.DARK_GRAY = (64, 64, 64)
        self.PHONE_BLACK = (32, 32, 32)
        self.SCREEN_BLUE = (240, 248, 255)

        # Emotional colors
        self.emotion_colors = {
            "neutral": (100, 100, 100),
            "concern": (150, 120, 50),
            "anxiety": (200, 100, 100),
            "panic": (255, 40, 40)
        }

        # Fonts
        self.font_header = pygame.font.Font(None, 28)
        self.font_content = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 20)
        self.font_phone_header = pygame.font.Font(None, 32)

        # Animation state
        self.pulse_timer = 0
        self.phone_glow = 0

    def start(self):
        """Start the therapy reminder activity"""
        print("[THERAPY_REMINDER] Activity starting...")
        self.active = True
        self.completed = False
        self.notification_progress = 0
        self.emotional_impact = 0
        self.current_section = 0
        self.sections_read = []
        self.reading_complete = False
        self.show_realization = False
        self.realization_timer = 0
        self.pulse_timer = 0
        self.phone_glow = 0
        print("[THERAPY_REMINDER] Activity started successfully!")

    def stop(self):
        """Stop the therapy reminder activity"""
        print("[THERAPY_REMINDER] Activity stopping...")
        self.active = False

    def handle_event(self, event):
        """Handle player input"""
        print(f"[THERAPY_REMINDER] handle_event called: active={self.active}, completed={self.completed}, event_type={event.type}")

        if not self.active or self.completed:
            print(f"[THERAPY_REMINDER] Ignoring event - not active or completed")
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("[THERAPY_REMINDER] Mouse click detected")
            if not self.reading_complete:
                self.advance_reading()
            elif self.show_realization:
                self.complete_activity()

        elif event.type == pygame.KEYDOWN:
            print(f"[THERAPY_REMINDER] Key pressed: {event.key}")
            if event.key == pygame.K_SPACE:
                print("[THERAPY_REMINDER] SPACE key pressed")
                if not self.reading_complete:
                    self.advance_reading()
                elif self.show_realization:
                    self.complete_activity()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        print(f"[THERAPY_REMINDER] handle_mouse_click called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        print(f"[THERAPY_REMINDER] handle_mouse_release called: pos={pos}, button={button}")
        if button == 1:  # Left click
            event = type('Event', (), {'type': pygame.MOUSEBUTTONUP, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def advance_reading(self):
        """Advance to next notification section"""
        print(f"[THERAPY_REMINDER] Advancing reading: current_section={self.current_section}")

        if self.current_section < len(self.notification_sections):
            if self.current_section not in self.sections_read:
                self.sections_read.append(self.current_section)
                self.emotional_impact += 20

                # Add phone glow effect for concerning sections
                section = self.notification_sections[self.current_section]
                if section["emotion"] in ["concern", "anxiety", "panic"]:
                    self.phone_glow = 30

            self.current_section += 1

            if self.current_section >= len(self.notification_sections):
                self.reading_complete = True
                self.show_realization = True
                self.realization_timer = 4.0  # 4 seconds of contemplation

    def complete_activity(self):
        """Complete the therapy reminder activity"""
        print("[THERAPY_REMINDER] Completing activity...")
        self.completed = True

        if self.objective_manager:
            print("[THERAPY_REMINDER] Completed reading therapy reminder...")
            self.objective_manager.complete_current_objective()

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update timers
        self.pulse_timer += dt
        if self.phone_glow > 0:
            self.phone_glow = max(0, self.phone_glow - dt * 40)

        # Update realization timer
        if self.show_realization and self.realization_timer > 0:
            self.realization_timer -= dt

    def draw_phone_frame(self, screen):
        """Draw the smartphone frame"""
        # Phone shadow
        shadow_rect = self.phone_rect.copy()
        shadow_rect.x += 8
        shadow_rect.y += 8
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 50))
        screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

        # Phone body
        pygame.draw.rect(screen, self.PHONE_BLACK, self.phone_rect, border_radius=25)

        # Add glow effect if present
        if self.phone_glow > 0:
            glow_intensity = int(self.phone_glow * 255 / 30)
            glow_color = (255, 100, 100, glow_intensity)
            glow_rect = self.phone_rect.copy()
            glow_rect.inflate_ip(10, 10)
            pygame.draw.rect(screen, glow_color[:3], glow_rect, width=3, border_radius=30)

        # Screen background
        pygame.draw.rect(screen, self.SCREEN_BLUE, self.screen_rect, border_radius=15)

        # Home button
        home_button = pygame.Rect(self.phone_rect.centerx - 25, self.phone_rect.bottom - 40, 50, 25)
        pygame.draw.rect(screen, self.DARK_GRAY, home_button, border_radius=12)

    def draw_notification_content(self, screen):
        """Draw the notification content"""
        # Notification header
        header_rect = pygame.Rect(self.screen_rect.x, self.screen_rect.y + 10, self.screen_rect.width, 40)
        pygame.draw.rect(screen, self.BLUE, header_rect)

        header_text = self.font_phone_header.render("Therapy Reminder", True, self.WHITE)
        header_pos = (header_rect.centerx - header_text.get_width() // 2, header_rect.centery - header_text.get_height() // 2)
        screen.blit(header_text, header_pos)

        # Draw notification sections
        y_pos = self.screen_rect.y + 70

        for i, section in enumerate(self.notification_sections):
            if i >= self.current_section and i not in self.sections_read:
                break

            # Section background with emotion-based color
            section_height = 80
            section_rect = pygame.Rect(self.screen_rect.x + 10, y_pos, self.screen_rect.width - 20, section_height)

            emotion_color = self.emotion_colors.get(section["emotion"], self.LIGHT_GRAY)
            bg_color = tuple(min(255, c + 200) for c in emotion_color[:3])  # Lighter version
            pygame.draw.rect(screen, bg_color, section_rect, border_radius=8)
            pygame.draw.rect(screen, emotion_color, section_rect, width=2, border_radius=8)

            # Section header
            header_surface = self.font_header.render(section["header"], True, self.BLACK)
            screen.blit(header_surface, (section_rect.x + 10, section_rect.y + 5))

            # Section content with word wrapping
            content_lines = []
            words = section["content"].split('\n')

            for paragraph in words:
                para_words = paragraph.split()
                current_line = ""

                for word in para_words:
                    test_line = current_line + " " + word if current_line else word
                    if self.font_content.size(test_line)[0] < section_rect.width - 30:
                        current_line = test_line
                    else:
                        if current_line:
                            content_lines.append(current_line)
                        current_line = word
                if current_line:
                    content_lines.append(current_line)

            # Draw content lines
            content_y = section_rect.y + 35
            for line in content_lines[:3]:  # Limit to 3 lines per section
                content_surface = self.font_content.render(line, True, self.BLACK)
                screen.blit(content_surface, (section_rect.x + 10, content_y))
                content_y += 20

            y_pos += section_height + 10

    def draw_emotional_indicators(self, screen):
        """Draw emotional state indicators"""
        if self.emotional_impact > 0:
            # Stress level bar
            bar_rect = pygame.Rect(50, 50, 200, 20)
            pygame.draw.rect(screen, self.GRAY, bar_rect)

            stress_level = min(self.emotional_impact / 120.0, 1.0)
            filled_width = int(bar_rect.width * stress_level)

            if stress_level < 0.3:
                stress_color = self.GREEN
            elif stress_level < 0.7:
                stress_color = (255, 165, 0)  # Orange
            else:
                stress_color = self.RED

            filled_rect = pygame.Rect(bar_rect.x, bar_rect.y, filled_width, bar_rect.height)
            pygame.draw.rect(screen, stress_color, filled_rect)

            # Label
            stress_text = self.font_small.render(f"Stress Level: {int(stress_level * 100)}%", True, self.BLACK)
            screen.blit(stress_text, (bar_rect.x, bar_rect.y - 25))

            # Add emotional overlay to screen
            intensity = min(self.emotional_impact / 100.0, 0.3)
            alpha = int(intensity * 100)

            # Color based on reading progress
            if self.emotional_impact < 30:
                color = (100, 100, 150, alpha)  # Mild concern
            elif self.emotional_impact < 60:
                color = (150, 100, 100, alpha)  # Growing anxiety
            else:
                color = (200, 80, 80, alpha)    # High stress

            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill(color)
            screen.blit(overlay, (0, 0))

    def draw_realization_thoughts(self, screen):
        """Draw final realization thoughts"""
        if not self.show_realization:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Thought bubbles
        thoughts = [
            "Without insurance, I can't afford therapy...",
            "But my mental health is struggling...",
            "Do I cancel and risk my wellbeing?",
            "Or find the money somehow?"
        ]

        bubble_y = 200
        pulse = math.sin(self.pulse_timer * 2) * 0.1 + 0.9

        for i, thought in enumerate(thoughts):
            if self.realization_timer > (3 - i * 0.5):  # Stagger thoughts
                # Thought bubble background
                bubble_rect = pygame.Rect(200, bubble_y + i * 80, 880, 60)
                bubble_surface = pygame.Surface((bubble_rect.width, bubble_rect.height), pygame.SRCALPHA)
                bubble_surface.fill((255, 255, 255, int(200 * pulse)))
                screen.blit(bubble_surface, (bubble_rect.x, bubble_rect.y))
                pygame.draw.ellipse(screen, (100, 100, 100), bubble_rect, 2)

                # Thought text
                thought_surface = self.font_content.render(thought, True, self.BLACK)
                text_rect = thought_surface.get_rect(center=bubble_rect.center)
                screen.blit(thought_surface, text_rect)

    def draw(self, screen):
        """Render the therapy reminder phone interface"""
        if not self.active:
            return

        # Dark background
        screen.fill((20, 30, 40))

        # Draw phone
        self.draw_phone_frame(screen)
        self.draw_notification_content(screen)

        # Draw emotional indicators
        self.draw_emotional_indicators(screen)

        # Draw realization thoughts
        self.draw_realization_thoughts(screen)

        # Instructions
        if not self.reading_complete:
            instruction = "Click or press SPACE to read notification..."
            instruction_surface = self.font_small.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)
        elif self.show_realization:
            instruction = "Click or press SPACE to continue..."
            instruction_surface = self.font_small.render(instruction, True, self.WHITE)
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30))
            screen.blit(instruction_surface, instruction_rect)

        # Progress indicator
        if not self.reading_complete:
            progress = len(self.sections_read) / len(self.notification_sections)
            progress_rect = pygame.Rect(100, self.SCREEN_HEIGHT - 80, 300, 10)
            pygame.draw.rect(screen, self.GRAY, progress_rect)
            filled_width = int(progress_rect.width * progress)
            if filled_width > 0:
                filled_rect = pygame.Rect(progress_rect.x, progress_rect.y, filled_width, progress_rect.height)
                pygame.draw.rect(screen, self.BLUE, filled_rect)
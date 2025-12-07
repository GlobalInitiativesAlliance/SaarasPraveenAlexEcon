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
        """Draw realistic modern smartphone with premium materials"""
        # Enhanced phone shadow with gradient
        shadow_rect = self.phone_rect.copy()
        shadow_rect.x += 12
        shadow_rect.y += 12

        # Multi-layer shadow for depth
        for i in range(8):
            offset = i * 2
            alpha = 60 - (i * 6)
            shadow_surf = pygame.Surface((shadow_rect.width + offset, shadow_rect.height + offset), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, alpha))
            screen.blit(shadow_surf, (shadow_rect.x - offset//2, shadow_rect.y - offset//2))

        # Premium phone body with metallic gradient
        phone_surface = pygame.Surface((self.phone_rect.width, self.phone_rect.height), pygame.SRCALPHA)

        # Create metallic gradient for phone body
        for y in range(self.phone_rect.height):
            progress = y / self.phone_rect.height

            # Metallic black with subtle highlights
            base_color = 25
            highlight = int(math.sin(progress * math.pi) * 20)
            color_value = min(255, base_color + highlight)

            r = color_value
            g = color_value + int(highlight * 0.3)
            b = color_value + int(highlight * 0.5)

            pygame.draw.line(phone_surface, (r, g, b), (0, y), (self.phone_rect.width, y))

        screen.blit(phone_surface, (self.phone_rect.x, self.phone_rect.y))

        # Phone body outline with premium finish
        pygame.draw.rect(screen, (60, 65, 75), self.phone_rect, width=2, border_radius=25)
        pygame.draw.rect(screen, (120, 125, 135), self.phone_rect, width=1, border_radius=25)

        # Premium screen with realistic edge lighting
        screen_surface = pygame.Surface((self.screen_rect.width, self.screen_rect.height), pygame.SRCALPHA)

        # OLED-style deep blacks with notification glow
        base_screen_color = (8, 12, 18) if self.phone_glow <= 0 else (18, 22, 28)

        # Add subtle screen texture
        for y in range(self.screen_rect.height):
            progress = y / self.screen_rect.height
            texture_noise = math.sin(y * 0.1) * 2

            r = min(255, base_screen_color[0] + int(texture_noise))
            g = min(255, base_screen_color[1] + int(texture_noise))
            b = min(255, base_screen_color[2] + int(texture_noise))

            pygame.draw.line(screen_surface, (r, g, b), (0, y), (self.screen_rect.width, y))

        screen.blit(screen_surface, (self.screen_rect.x, self.screen_rect.y))

        # Realistic screen border with curved edges
        pygame.draw.rect(screen, (40, 45, 55), self.screen_rect, width=3, border_radius=20)

        # Add notification glow effect
        if self.phone_glow > 0:
            glow_intensity = self.phone_glow / 30.0

            # Pulsing notification light
            pulse = math.sin(self.pulse_timer * 8) * 0.3 + 0.7
            glow_alpha = int(glow_intensity * 150 * pulse)

            # Top notification LED
            led_rect = pygame.Rect(self.phone_rect.centerx - 15, self.phone_rect.y + 15, 30, 6)
            led_surface = pygame.Surface((led_rect.width, led_rect.height), pygame.SRCALPHA)
            led_surface.fill((255, 80, 80, glow_alpha))
            screen.blit(led_surface, (led_rect.x, led_rect.y))

            # Screen edge glow
            glow_rect = self.screen_rect.copy()
            glow_rect.inflate_ip(8, 8)
            pygame.draw.rect(screen, (255, 100, 100, int(glow_alpha * 0.3)), glow_rect, width=4, border_radius=24)

        # Modern camera notch
        notch_width = 120
        notch_height = 25
        notch_rect = pygame.Rect(self.phone_rect.centerx - notch_width//2, self.phone_rect.y + 8, notch_width, notch_height)
        pygame.draw.rect(screen, (15, 20, 25), notch_rect, border_radius=12)

        # Camera and sensors in notch
        camera_size = 8
        camera_x = notch_rect.centerx - 20
        speaker_x = notch_rect.centerx + 15

        # Front camera
        pygame.draw.circle(screen, (40, 45, 50), (camera_x, notch_rect.centery), camera_size)
        pygame.draw.circle(screen, (60, 65, 70), (camera_x, notch_rect.centery), camera_size - 2)

        # Speaker grille
        for i in range(5):
            line_x = speaker_x + i * 4 - 8
            pygame.draw.line(screen, (50, 55, 60), (line_x, notch_rect.centery - 3), (line_x, notch_rect.centery + 3), 1)

    def draw_notification_content(self, screen):
        """Draw modern notification interface with iOS/Android styling"""
        # Status bar at top
        self.draw_status_bar(screen)

        # Modern notification card stack
        card_start_y = self.screen_rect.y + 50
        card_spacing = 5

        # Draw notification cards with modern design
        for i, section in enumerate(self.notification_sections):
            if i >= self.current_section and i not in self.sections_read:
                break

            card_y = card_start_y + (i * (75 + card_spacing))
            self.draw_modern_notification_card(screen, section, card_y, i)

    def draw_status_bar(self, screen):
        """Draw realistic phone status bar"""
        status_rect = pygame.Rect(self.screen_rect.x + 10, self.screen_rect.y + 5, self.screen_rect.width - 20, 30)

        # Time
        time_text = "2:14 PM"
        time_font = pygame.font.Font(None, 22)
        time_surface = time_font.render(time_text, True, (255, 255, 255))
        screen.blit(time_surface, (status_rect.x + 5, status_rect.y + 5))

        # Signal, WiFi, Battery indicators
        indicators_x = status_rect.right - 80

        # Signal strength
        for i in range(4):
            bar_height = (i + 1) * 3
            bar_rect = pygame.Rect(indicators_x + i * 4, status_rect.y + 15 - bar_height, 2, bar_height)
            color = (255, 255, 255) if i < 3 else (100, 255, 100)
            pygame.draw.rect(screen, color, bar_rect)

        # WiFi icon
        wifi_x = indicators_x + 20
        for i in range(3):
            radius = (i + 1) * 3
            pygame.draw.arc(screen, (255, 255, 255),
                          (wifi_x - radius, status_rect.y + 8 - radius, radius * 2, radius * 2),
                          -math.pi/4, math.pi/4, 1)

        # Battery
        battery_rect = pygame.Rect(indicators_x + 40, status_rect.y + 8, 20, 12)
        pygame.draw.rect(screen, (255, 255, 255), battery_rect, 1, border_radius=2)
        # Battery fill (78%)
        fill_rect = pygame.Rect(battery_rect.x + 1, battery_rect.y + 1, 15, battery_rect.height - 2)
        pygame.draw.rect(screen, (100, 255, 100), fill_rect, border_radius=1)
        # Battery tip
        tip_rect = pygame.Rect(battery_rect.right, battery_rect.y + 4, 2, 4)
        pygame.draw.rect(screen, (255, 255, 255), tip_rect)

    def draw_modern_notification_card(self, screen, section, y_pos, index):
        """Draw individual notification card with modern design"""
        card_rect = pygame.Rect(self.screen_rect.x + 15, y_pos, self.screen_rect.width - 30, 70)

        # Card shadow
        shadow_rect = card_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 30))
        screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

        # Card background with glassmorphism effect
        card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)

        # Emotion-based color mapping
        emotion_colors = {
            "neutral": (245, 248, 252),
            "concern": (255, 248, 235),
            "anxiety": (255, 242, 242),
            "panic": (255, 235, 235)
        }

        base_color = emotion_colors.get(section["emotion"], (245, 248, 252))

        # Create subtle gradient
        for y in range(card_rect.height):
            progress = y / card_rect.height
            r = int(base_color[0] - progress * 5)
            g = int(base_color[1] - progress * 3)
            b = int(base_color[2] - progress * 2)
            pygame.draw.line(card_surface, (r, g, b), (0, y), (card_rect.width, y))

        screen.blit(card_surface, (card_rect.x, card_rect.y))

        # Modern border
        border_colors = {
            "neutral": (200, 210, 220),
            "concern": (255, 180, 100),
            "anxiety": (255, 140, 140),
            "panic": (255, 100, 100)
        }

        border_color = border_colors.get(section["emotion"], (200, 210, 220))
        pygame.draw.rect(screen, border_color, card_rect, width=1, border_radius=12)

        # App icon circle
        icon_size = 35
        icon_center = (card_rect.x + 25, card_rect.y + 25)

        # Medical app icon background
        pygame.draw.circle(screen, (70, 130, 180), icon_center, icon_size // 2)
        pygame.draw.circle(screen, (90, 150, 200), icon_center, icon_size // 2 - 2)

        # Medical cross icon
        cross_color = (255, 255, 255)
        cross_size = 12
        # Horizontal bar
        pygame.draw.rect(screen, cross_color,
                        (icon_center[0] - cross_size // 2, icon_center[1] - 2, cross_size, 4))
        # Vertical bar
        pygame.draw.rect(screen, cross_color,
                        (icon_center[0] - 2, icon_center[1] - cross_size // 2, 4, cross_size))

        # App name and time
        app_font = pygame.font.Font(None, 20)
        app_text = app_font.render("Wellness Center", True, (80, 90, 100))
        screen.blit(app_text, (card_rect.x + 50, card_rect.y + 8))

        time_text = app_font.render("now", True, (150, 160, 170))
        screen.blit(time_text, (card_rect.right - 35, card_rect.y + 8))

        # Notification content with proper typography
        content_font = pygame.font.Font(None, 22)

        # Extract key info from section
        if "appointment" in section["content"].lower():
            # Appointment notification
            main_text = "Therapy appointment reminder"
            sub_text = "Tomorrow at 2:00 PM • Dr. Sarah Chen"
        elif "payment" in section["content"].lower() or "$" in section["content"]:
            # Payment notification
            main_text = "Payment required at visit"
            sub_text = "$150 session fee without insurance"
        elif "cancellation" in section["content"].lower():
            # Policy notification
            main_text = "Cancellation policy reminder"
            sub_text = "24-hour notice required"
        else:
            # Default
            words = section["content"].split()
            main_text = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
            sub_text = " ".join(words[6:12]) + ("..." if len(words) > 12 else "")

        # Main notification text
        main_surface = content_font.render(main_text, True, (40, 50, 60))
        screen.blit(main_surface, (card_rect.x + 50, card_rect.y + 28))

        # Subtitle with emotion coloring
        sub_color = (120, 130, 140)
        if section["emotion"] == "anxiety":
            sub_color = (200, 100, 50)
        elif section["emotion"] == "panic":
            sub_color = (220, 60, 60)

        sub_surface = pygame.font.Font(None, 18).render(sub_text, True, sub_color)
        screen.blit(sub_surface, (card_rect.x + 50, card_rect.y + 48))

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
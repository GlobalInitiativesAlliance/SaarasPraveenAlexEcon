"""
Therapist Office Call Activity
Professional phone call interface for therapy appointment payment options
"""
import pygame
import math

class TherapistCallActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Call state
        self.call_stage = "ringing"  # ringing, answered, options, decision, completed
        self.conversation_progress = 0
        self.current_line = 0
        self.lines_shown = []
        self.auto_advance_timer = 0
        self.ring_animation = 0
        self.selected_option = None

        # Phone call conversation
        self.conversation_lines = [
            {
                "speaker": "system",
                "text": "*Ring ring* You pick up the phone with trembling hands.",
                "pause": 2.0
            },
            {
                "speaker": "receptionist",
                "text": "Hi, this is Sarah from Dr. Chen's office about your appointment tomorrow.",
                "pause": 1.5
            },
            {
                "speaker": "receptionist",
                "text": "We received notice that your insurance coverage was terminated.",
                "pause": 1.5
            },
            {
                "speaker": "receptionist",
                "text": "I'm sorry - I know this is stressful for young adults in your situation.",
                "pause": 1.8
            },
            {
                "speaker": "receptionist",
                "text": "You have three options for tomorrow's session:",
                "pause": 1.2
            },
            {
                "speaker": "system",
                "text": "The receptionist explains your payment options...",
                "pause": 1.0
            }
        ]

        # Payment options
        self.payment_options = [
            {
                "title": "Full Price Payment",
                "cost": "$150",
                "description": "Pay the complete session fee out-of-pocket",
                "pros": ["Keep your appointment", "No paperwork required"],
                "cons": ["Very expensive", "Might strain your budget"],
                "recommendation": "difficult",
                "color": (255, 120, 120)
            },
            {
                "title": "Cancel Appointment",
                "cost": "$0",
                "description": "Reschedule when you have insurance coverage",
                "pros": ["No immediate cost", "Can reschedule later"],
                "cons": ["Delay in mental health treatment", "Uncertain timeline"],
                "recommendation": "risky",
                "color": (255, 180, 100)
            },
            {
                "title": "Sliding Scale Program",
                "cost": "$40",
                "description": "Income-based fee for former foster youth",
                "pros": ["Affordable payment", "Designed for your situation", "Keep treatment schedule"],
                "cons": ["Requires income documentation"],
                "recommendation": "ideal",
                "color": (100, 255, 150)
            }
        ]

        # Visual elements
        self.phone_interface_rect = pygame.Rect(200, 100, 880, 520)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (240, 240, 240)
        self.DARK_GRAY = (60, 60, 70)
        self.CALL_GREEN = (76, 175, 80)
        self.CALL_RED = (244, 67, 54)

        # Fonts
        self.font_header = pygame.font.Font(None, 36)
        self.font_speaker = pygame.font.Font(None, 28)
        self.font_content = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_option_title = pygame.font.Font(None, 30)

        # Animation timers
        self.pulse_timer = 0
        self.selection_animation = 0

    def start(self):
        """Start the therapist call activity"""
        print("[THERAPIST_CALL] Activity starting...")
        self.active = True
        self.completed = False
        self.call_stage = "ringing"
        self.conversation_progress = 0
        self.current_line = 0
        self.lines_shown = []
        self.auto_advance_timer = 0
        self.ring_animation = 0
        self.selected_option = None
        self.pulse_timer = 0
        self.selection_animation = 0
        print("[THERAPIST_CALL] Activity started successfully!")

    def stop(self):
        """Stop the therapist call activity"""
        print("[THERAPIST_CALL] Activity stopping...")
        self.active = False

    def handle_event(self, event):
        """Handle player input"""
        print(f"[THERAPIST_CALL] handle_event called: active={self.active}, completed={self.completed}, event_type={event.type}")

        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.call_stage == "ringing":
                # Answer the phone
                self.call_stage = "answered"
                self.auto_advance_timer = 1.0
            elif self.call_stage == "options":
                # Check option selection
                self.handle_option_click(mouse_pos)
            elif self.call_stage == "decision":
                # Advance to completion
                self.complete_activity()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.call_stage == "ringing":
                    self.call_stage = "answered"
                    self.auto_advance_timer = 1.0
                elif self.call_stage == "answered":
                    self.advance_conversation()
                elif self.call_stage == "decision":
                    self.complete_activity()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        if button == 1:
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        pass

    def handle_option_click(self, mouse_pos):
        """Handle clicking on payment options"""
        option_start_y = 200
        option_height = 140
        option_spacing = 20

        for i, option in enumerate(self.payment_options):
            option_y = option_start_y + (i * (option_height + option_spacing))
            option_rect = pygame.Rect(self.phone_interface_rect.x + 50, option_y,
                                    self.phone_interface_rect.width - 100, option_height)

            if option_rect.collidepoint(mouse_pos):
                self.selected_option = i
                self.call_stage = "decision"
                self.selection_animation = 1.0

    def advance_conversation(self):
        """Advance the conversation to next line"""
        if self.current_line < len(self.conversation_lines):
            if self.current_line not in self.lines_shown:
                self.lines_shown.append(self.current_line)
            self.current_line += 1

            if self.current_line >= len(self.conversation_lines):
                self.call_stage = "options"

    def complete_activity(self):
        """Complete the therapist call activity"""
        print("[THERAPIST_CALL] Completing activity...")
        self.completed = True

        if self.objective_manager:
            print("[THERAPIST_CALL] Completed therapist call options...")
            self.objective_manager.complete_current_objective()

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        self.pulse_timer += dt
        self.ring_animation += dt * 8  # Ring animation speed

        # Auto-advance conversation
        if self.call_stage == "answered":
            if self.auto_advance_timer > 0:
                self.auto_advance_timer -= dt
            else:
                # Auto-advance every 2 seconds
                if self.current_line < len(self.conversation_lines):
                    line = self.conversation_lines[self.current_line]
                    if self.current_line not in self.lines_shown:
                        self.lines_shown.append(self.current_line)
                        self.auto_advance_timer = line["pause"]
                    self.current_line += 1

                    if self.current_line >= len(self.conversation_lines):
                        self.call_stage = "options"

        # Update selection animation
        if self.selection_animation > 0:
            self.selection_animation = max(0, self.selection_animation - dt * 2)

    def draw_phone_interface_background(self, screen):
        """Draw professional phone call interface background"""
        # Main interface panel
        panel_surface = pygame.Surface((self.phone_interface_rect.width, self.phone_interface_rect.height), pygame.SRCALPHA)

        # Professional gradient background
        for y in range(self.phone_interface_rect.height):
            progress = y / self.phone_interface_rect.height
            r = int(245 - progress * 20)
            g = int(250 - progress * 15)
            b = int(255 - progress * 10)
            pygame.draw.line(panel_surface, (r, g, b), (0, y), (self.phone_interface_rect.width, y))

        screen.blit(panel_surface, (self.phone_interface_rect.x, self.phone_interface_rect.y))

        # Professional border
        pygame.draw.rect(screen, (180, 190, 200), self.phone_interface_rect, 3, border_radius=15)
        pygame.draw.rect(screen, (220, 230, 240), self.phone_interface_rect, 1, border_radius=15)

    def draw_call_header(self, screen):
        """Draw professional call interface header"""
        header_rect = pygame.Rect(self.phone_interface_rect.x, self.phone_interface_rect.y,
                                 self.phone_interface_rect.width, 80)

        # Header background
        header_surface = pygame.Surface((header_rect.width, header_rect.height), pygame.SRCALPHA)
        for y in range(header_rect.height):
            progress = y / header_rect.height
            r = int(70 + progress * 20)
            g = int(130 + progress * 30)
            b = int(180 + progress * 40)
            pygame.draw.line(header_surface, (r, g, b), (0, y), (header_rect.width, y))

        screen.blit(header_surface, (header_rect.x, header_rect.y))

        # Call status icon and text
        if self.call_stage == "ringing":
            # Animated ringing icon
            ring_intensity = math.sin(self.ring_animation) * 0.3 + 0.7
            icon_color = (255, int(255 * ring_intensity), int(255 * ring_intensity))
            status_text = "Incoming Call..."
        elif self.call_stage in ["answered", "options", "decision"]:
            icon_color = self.CALL_GREEN
            status_text = "Dr. Chen's Office"
        else:
            icon_color = self.GRAY
            status_text = "Call Ended"

        # Phone icon
        icon_center = (header_rect.x + 50, header_rect.centery)
        pygame.draw.circle(screen, icon_color, icon_center, 20)
        pygame.draw.circle(screen, (255, 255, 255), icon_center, 15)

        # Phone symbol
        phone_rect = pygame.Rect(icon_center[0] - 8, icon_center[1] - 8, 16, 16)
        pygame.draw.ellipse(screen, icon_color, phone_rect)

        # Status text
        status_surface = self.font_header.render(status_text, True, (255, 255, 255))
        screen.blit(status_surface, (header_rect.x + 90, header_rect.centery - 15))

        # Dr. Chen's office info
        if self.call_stage != "ringing":
            office_info = self.font_small.render("Mental Health Services • (555) 123-4567", True, (200, 220, 240))
            screen.blit(office_info, (header_rect.x + 90, header_rect.centery + 15))

    def draw_conversation(self, screen):
        """Draw conversation with professional chat interface"""
        conv_start_y = self.phone_interface_rect.y + 100
        conv_width = self.phone_interface_rect.width - 40
        line_height = 50

        for i, line_index in enumerate(self.lines_shown):
            if line_index >= len(self.conversation_lines):
                continue

            line = self.conversation_lines[line_index]
            line_y = conv_start_y + (i * line_height)

            # Message bubble
            bubble_rect = pygame.Rect(self.phone_interface_rect.x + 20, line_y, conv_width, 40)

            if line["speaker"] == "receptionist":
                # Receptionist message (left side)
                bubble_rect.width = min(conv_width - 100, len(line["text"]) * 8)
                bubble_color = (230, 240, 255)
                text_color = (50, 70, 90)
            elif line["speaker"] == "system":
                # System message (center)
                bubble_rect.x = self.phone_interface_rect.centerx - bubble_rect.width // 2
                bubble_color = (240, 240, 240)
                text_color = (100, 100, 100)
            else:
                # Your response (right side)
                bubble_rect.x = self.phone_interface_rect.right - bubble_rect.width - 20
                bubble_color = (200, 255, 200)
                text_color = (50, 90, 50)

            # Draw bubble
            pygame.draw.rect(screen, bubble_color, bubble_rect, border_radius=20)
            pygame.draw.rect(screen, (180, 190, 200), bubble_rect, 1, border_radius=20)

            # Draw text with word wrapping
            words = line["text"].split()
            current_line = ""
            text_y = bubble_rect.y + 8

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.font_content.size(test_line)[0] < bubble_rect.width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        text_surface = self.font_content.render(current_line, True, text_color)
                        screen.blit(text_surface, (bubble_rect.x + 10, text_y))
                        text_y += 20
                    current_line = word

            if current_line:
                text_surface = self.font_content.render(current_line, True, text_color)
                screen.blit(text_surface, (bubble_rect.x + 10, text_y))

    def draw_payment_options(self, screen):
        """Draw professional payment options interface"""
        if self.call_stage != "options":
            return

        # Options header
        options_header = self.font_header.render("Payment Options for Tomorrow's Session", True, (60, 80, 100))
        header_rect = options_header.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
        screen.blit(options_header, header_rect)

        # Draw each option
        option_start_y = 220
        option_height = 140
        option_spacing = 20

        for i, option in enumerate(self.payment_options):
            option_y = option_start_y + (i * (option_height + option_spacing))
            option_rect = pygame.Rect(self.phone_interface_rect.x + 50, option_y,
                                    self.phone_interface_rect.width - 100, option_height)

            # Option background with recommendation coloring
            bg_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)

            if option["recommendation"] == "ideal":
                bg_color = (240, 255, 245)
                border_color = option["color"]
                border_width = 3
            elif option["recommendation"] == "difficult":
                bg_color = (255, 245, 245)
                border_color = option["color"]
                border_width = 2
            else:
                bg_color = (250, 248, 245)
                border_color = option["color"]
                border_width = 2

            bg_surface.fill(bg_color)
            screen.blit(bg_surface, (option_rect.x, option_rect.y))
            pygame.draw.rect(screen, border_color, option_rect, border_width, border_radius=12)

            # Recommendation badge
            if option["recommendation"] == "ideal":
                badge_rect = pygame.Rect(option_rect.right - 120, option_rect.y + 10, 100, 25)
                pygame.draw.rect(screen, (34, 139, 34), badge_rect, border_radius=12)
                badge_text = self.font_small.render("RECOMMENDED", True, (255, 255, 255))
                badge_text_rect = badge_text.get_rect(center=badge_rect.center)
                screen.blit(badge_text, badge_text_rect)

            # Option title and cost
            title_text = self.font_option_title.render(option["title"], True, (50, 70, 90))
            cost_text = self.font_header.render(option["cost"], True, option["color"])

            screen.blit(title_text, (option_rect.x + 20, option_rect.y + 15))
            cost_rect = cost_text.get_rect(right=option_rect.right - 20, top=option_rect.y + 15)
            screen.blit(cost_text, cost_rect)

            # Description
            desc_text = self.font_content.render(option["description"], True, (80, 100, 120))
            screen.blit(desc_text, (option_rect.x + 20, option_rect.y + 45))

            # Pros and cons
            pros_text = " • ".join(option["pros"])
            cons_text = " • ".join(option["cons"])

            pro_surface = self.font_small.render(f"✓ {pros_text}", True, (60, 140, 60))
            con_surface = self.font_small.render(f"⚠ {cons_text}", True, (140, 90, 60))

            screen.blit(pro_surface, (option_rect.x + 20, option_rect.y + 75))
            screen.blit(con_surface, (option_rect.x + 20, option_rect.y + 95))

            # Click instruction
            click_text = self.font_small.render("Click to select this option", True, (120, 130, 140))
            click_rect = click_text.get_rect(center=(option_rect.centerx, option_rect.bottom - 15))
            screen.blit(click_text, click_rect)

    def draw_decision_confirmation(self, screen):
        """Draw decision confirmation"""
        if self.call_stage != "decision" or self.selected_option is None:
            return

        option = self.payment_options[self.selected_option]

        # Confirmation overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Confirmation panel
        panel_rect = pygame.Rect(300, 200, 680, 320)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, border_radius=20)
        pygame.draw.rect(screen, option["color"], panel_rect, 4, border_radius=20)

        # Confirmation text
        confirm_title = self.font_header.render("Option Selected", True, (50, 70, 90))
        title_rect = confirm_title.get_rect(center=(panel_rect.centerx, panel_rect.y + 50))
        screen.blit(confirm_title, title_rect)

        # Selected option details
        option_title = self.font_option_title.render(f"{option['title']} - {option['cost']}", True, option["color"])
        option_rect = option_title.get_rect(center=(panel_rect.centerx, panel_rect.y + 100))
        screen.blit(option_title, option_rect)

        # Receptionist response
        responses = [
            "Perfect! I'll update your file with the sliding scale rate.",
            "I understand. I'll cancel tomorrow's appointment for now.",
            "Okay, I'll note that you'll pay the full session fee."
        ]

        response_text = responses[self.selected_option]
        response_surface = self.font_content.render(response_text, True, (70, 90, 110))
        response_rect = response_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 150))
        screen.blit(response_surface, response_rect)

        # Final message
        final_message = "Dr. Chen really wants to continue your treatment. We're here to help."
        final_surface = self.font_content.render(final_message, True, (100, 120, 140))
        final_rect = final_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 200))
        screen.blit(final_surface, final_rect)

        # Continue instruction
        continue_text = "Click or press SPACE to continue"
        continue_surface = self.font_small.render(continue_text, True, (150, 160, 170))
        continue_rect = continue_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 250))
        screen.blit(continue_surface, continue_rect)

    def draw(self, screen):
        """Render the therapist call interface"""
        if not self.active:
            return

        # Professional background
        screen.fill((230, 235, 245))

        # Draw main interface
        self.draw_phone_interface_background(screen)
        self.draw_call_header(screen)

        if self.call_stage == "ringing":
            # Answer prompt
            prompt_text = "Incoming call from Dr. Chen's office"
            prompt_surface = self.font_header.render(prompt_text, True, (80, 100, 120))
            prompt_rect = prompt_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 300))
            screen.blit(prompt_surface, prompt_rect)

            instruction_text = "Click anywhere or press SPACE to answer"
            instruction_surface = self.font_content.render(instruction_text, True, (120, 140, 160))
            instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 350))
            screen.blit(instruction_surface, instruction_rect)

        elif self.call_stage == "answered":
            self.draw_conversation(screen)

            # Continue prompt
            if len(self.lines_shown) < len(self.conversation_lines):
                continue_text = "Press SPACE to continue conversation"
                continue_surface = self.font_small.render(continue_text, True, (120, 140, 160))
                continue_rect = continue_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 580))
                screen.blit(continue_surface, continue_rect)

        elif self.call_stage == "options":
            self.draw_payment_options(screen)

        elif self.call_stage == "decision":
            self.draw_decision_confirmation(screen)
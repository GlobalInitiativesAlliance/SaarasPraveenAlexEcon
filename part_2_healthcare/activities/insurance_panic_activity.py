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
        """Draw professional crisis interface background with gradient and effects"""
        # Create dynamic gradient background that shifts with panic level
        panic_ratio = min(self.panic_level / 300.0, 1.0)

        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT

            # Base colors shift from calm blue to anxious red
            if panic_ratio < 0.3:
                # Calm state - deep blue gradient
                r = int(15 + progress * 10 + panic_ratio * 30)
                g = int(25 + progress * 20 + panic_ratio * 20)
                b = int(45 + progress * 25)
            elif panic_ratio < 0.7:
                # Growing anxiety - purple/red gradient
                r = int(45 + progress * 40 + panic_ratio * 60)
                g = int(20 + progress * 15 + panic_ratio * 10)
                b = int(35 + progress * 20 - panic_ratio * 15)
            else:
                # High panic - intense red gradient
                r = int(80 + progress * 50 + panic_ratio * 40)
                g = int(15 + progress * 10)
                b = int(20 + progress * 15)

            # Add breathing/pulsing effect for high panic
            if self.panic_level > 150:
                pulse = math.sin(self.pulse_timer * 8) * 0.1 + 1.0
                r = min(255, int(r * pulse))

            color = (min(255, r), min(255, g), min(255, b))
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Add vignette effect for focus
        vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(100):
            alpha = int(i * 1.5)
            thickness = i * 3
            pygame.draw.ellipse(vignette, (0, 0, 0, alpha),
                              (-thickness, -thickness,
                               self.SCREEN_WIDTH + thickness*2,
                               self.SCREEN_HEIGHT + thickness*2), thickness)
        screen.blit(vignette, (0, 0))

    def draw_panic_thoughts(self, screen):
        """Draw modern card-based panic thoughts with professional design"""
        for i, (thought, rect) in enumerate(zip(self.panic_thoughts, self.thought_rects)):
            if i >= self.current_thought and i not in self.thoughts_read:
                break

            # Apply screen shake to individual thought cards
            shake_x = shake_y = 0
            if self.shake_intensity > 0:
                shake_x = math.sin(self.pulse_timer * 25 + i) * self.shake_intensity
                shake_y = math.cos(self.pulse_timer * 30 + i) * self.shake_intensity

            card_rect = rect.copy()
            card_rect.x += int(shake_x)
            card_rect.y += int(shake_y)

            # Modern card shadow
            shadow_rect = card_rect.copy()
            shadow_rect.x += 8
            shadow_rect.y += 8
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 40))
            screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

            # Card background with gradient
            card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)

            # Create gradient based on panic weight
            panic_intensity = thought["panic_weight"] / 80.0
            for y in range(card_rect.height):
                progress = y / card_rect.height
                base_color = thought["color"]

                # Lighten at top, darken at bottom
                r = min(255, int(base_color[0] * (1.2 - progress * 0.3)))
                g = min(255, int(base_color[1] * (1.2 - progress * 0.3)))
                b = min(255, int(base_color[2] * (1.2 - progress * 0.3)))

                if i in self.thoughts_read:
                    # Add pulsing effect to read thoughts
                    pulse = math.sin(self.pulse_timer * 4) * 0.1 + 0.9
                    r = int(r * pulse)
                    g = int(g * pulse)
                    b = int(b * pulse)

                pygame.draw.line(card_surface, (r, g, b), (0, y), (card_rect.width, y))

            screen.blit(card_surface, (card_rect.x, card_rect.y))

            # Modern border with glow effect
            border_color = (255, 255, 255, 100) if i in self.thoughts_read else (200, 200, 200, 60)
            pygame.draw.rect(screen, border_color[:3], card_rect, 2, border_radius=15)

            # Panic level indicator stripe
            stripe_width = max(5, int(panic_intensity * 15))
            stripe_rect = pygame.Rect(card_rect.x, card_rect.y, stripe_width, card_rect.height)
            stripe_color = (255, int(255 * (1 - panic_intensity)), int(255 * (1 - panic_intensity)))
            pygame.draw.rect(screen, stripe_color, stripe_rect, border_radius=15)

            # Icon/emoji with better positioning
            emoji_surface = self.font_header.render(thought["header"].split()[0], True, (255, 255, 255))
            emoji_pos = (card_rect.x + stripe_width + 15, card_rect.y + 10)
            screen.blit(emoji_surface, emoji_pos)

            # Thought header (without emoji)
            header_text = " ".join(thought["header"].split()[1:])  # Remove emoji
            header_surface = self.font_header.render(header_text, True, (255, 255, 255))
            header_pos = (card_rect.x + stripe_width + 60, card_rect.y + 12)
            screen.blit(header_surface, header_pos)

            # Professional typography for content
            words = thought["content"].split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.font_content.size(test_line)[0] < card_rect.width - stripe_width - 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw content with proper line spacing
            content_y = card_rect.y + 50
            for line in lines:
                content_surface = self.font_content.render(line, True, (240, 240, 240))
                screen.blit(content_surface, (card_rect.x + stripe_width + 20, content_y))
                content_y += 22

            # Severity indicator
            if i in self.thoughts_read:
                severity_text = f"Impact: {thought['panic_weight']}%"
                severity_surface = self.font_small.render(severity_text, True, (200, 200, 100))
                screen.blit(severity_surface, (card_rect.right - 120, card_rect.bottom - 25))

    def draw_panic_indicators(self, screen):
        """Draw modern dashboard-style panic and stress indicators"""
        if self.panic_level <= 0:
            return

        # Modern dashboard panel
        panel_rect = pygame.Rect(30, 30, 400, 120)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)

        # Panel background with glassmorphism effect
        panel_surface.fill((20, 25, 35, 180))
        pygame.draw.rect(panel_surface, (60, 70, 85, 100), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=20)
        screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

        # Panic level visualization
        panic_ratio = min(self.panic_level / 300.0, 1.0)

        # Modern circular progress indicator
        center_x = panel_rect.x + 80
        center_y = panel_rect.y + 60
        radius = 35

        # Background circle
        pygame.draw.circle(screen, (40, 45, 55), (center_x, center_y), radius, 4)

        # Animated progress arc
        if panic_ratio > 0:
            # Calculate color based on panic level
            if panic_ratio < 0.3:
                color = (100, 255, 150)  # Green
            elif panic_ratio < 0.6:
                color = (255, 200, 50)   # Yellow/Orange
            else:
                color = (255, 80, 80)    # Red

            # Draw progress arc
            angle = panic_ratio * 2 * math.pi - math.pi / 2  # Start from top
            arc_points = []
            segments = max(3, int(panic_ratio * 60))

            for i in range(segments + 1):
                segment_angle = -math.pi / 2 + (i / segments) * angle
                x = center_x + (radius - 2) * math.cos(segment_angle)
                y = center_y + (radius - 2) * math.sin(segment_angle)
                arc_points.append((x, y))

            if len(arc_points) > 1:
                pygame.draw.lines(screen, color, False, arc_points, 6)

        # Panic percentage text
        panic_percentage = int(panic_ratio * 100)
        panic_font = pygame.font.Font(None, 32)
        panic_text = panic_font.render(f"{panic_percentage}%", True, (255, 255, 255))
        panic_rect = panic_text.get_rect(center=(center_x, center_y))
        screen.blit(panic_text, panic_rect)

        # Status text
        status_font = pygame.font.Font(None, 24)
        if panic_ratio < 0.3:
            status = "Manageable"
            status_color = (100, 255, 150)
        elif panic_ratio < 0.6:
            status = "Elevated"
            status_color = (255, 200, 50)
        else:
            status = "Critical"
            status_color = (255, 80, 80)

        status_text = status_font.render(status, True, status_color)
        screen.blit(status_text, (panel_rect.x + 20, panel_rect.y + 15))

        # Detailed metrics
        metrics_x = panel_rect.x + 150
        metrics_y = panel_rect.y + 25

        # Stress level bar
        stress_label = self.font_small.render("Anxiety Level", True, (200, 200, 200))
        screen.blit(stress_label, (metrics_x, metrics_y))

        stress_bar_rect = pygame.Rect(metrics_x, metrics_y + 20, 200, 12)
        pygame.draw.rect(screen, (40, 40, 50), stress_bar_rect, border_radius=6)

        stress_fill = int(stress_bar_rect.width * panic_ratio)
        if stress_fill > 0:
            stress_filled = pygame.Rect(stress_bar_rect.x, stress_bar_rect.y, stress_fill, stress_bar_rect.height)
            # Gradient fill for stress bar
            for i in range(stress_fill):
                progress = i / stress_bar_rect.width
                r = int(100 + progress * 155)
                g = int(255 - progress * 175)
                b = int(150 - progress * 70)
                pygame.draw.line(screen, (r, g, b),
                               (stress_bar_rect.x + i, stress_bar_rect.y),
                               (stress_bar_rect.x + i, stress_bar_rect.bottom))

        # Breathing indicator
        if self.breathing_pattern > 0:
            breath_label = self.font_small.render("Breathing Pattern", True, (200, 200, 200))
            screen.blit(breath_label, (metrics_x, metrics_y + 45))

            # Animated breathing visualization
            pulse = math.sin(self.pulse_timer * 6) * 0.4 + 0.6
            breath_circle_radius = int(8 + pulse * 5)
            breath_color = (255, int(100 + pulse * 100), int(100 + pulse * 100))

            pygame.draw.circle(screen, breath_color, (metrics_x + 20, metrics_y + 65), breath_circle_radius)

            breath_status = "Irregular" if self.breathing_pattern > 15 else "Labored"
            breath_text = self.font_small.render(breath_status, True, breath_color)
            screen.blit(breath_text, (metrics_x + 45, metrics_y + 58))

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

    def draw_professional_title(self, screen):
        """Draw professional crisis interface title with modern styling"""
        # Title panel background
        title_panel_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, 100)
        panel_surface = pygame.Surface((title_panel_rect.width, title_panel_rect.height), pygame.SRCALPHA)

        # Gradient background for title panel
        panic_ratio = min(self.panic_level / 300.0, 1.0)
        for y in range(title_panel_rect.height):
            progress = y / title_panel_rect.height

            if panic_ratio < 0.5:
                r = int(20 + progress * 30 + panic_ratio * 40)
                g = int(25 + progress * 35 + panic_ratio * 20)
                b = int(40 + progress * 40)
            else:
                r = int(60 + progress * 40 + panic_ratio * 60)
                g = int(20 + progress * 20)
                b = int(25 + progress * 25)

            alpha = int(200 - progress * 50)
            pygame.draw.line(panel_surface, (r, g, b, alpha), (0, y), (title_panel_rect.width, y))

        screen.blit(panel_surface, (0, 0))

        # Main title with shadow effect
        title_text = "MENTAL HEALTH CRISIS ASSESSMENT"
        title_font = pygame.font.Font(None, 48)

        # Title shadow
        shadow_surface = title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.SCREEN_WIDTH // 2 + 3, 35 + 3))
        screen.blit(shadow_surface, shadow_rect)

        # Main title
        title_color = (255, 255, 255) if panic_ratio < 0.7 else (255, 200, 200)
        title_surface = title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 35))
        screen.blit(title_surface, title_rect)

        # Subtitle
        subtitle_text = "Real-time stress and anxiety monitoring"
        subtitle_font = pygame.font.Font(None, 24)
        subtitle_color = (200, 220, 240) if panic_ratio < 0.7 else (255, 180, 180)
        subtitle_surface = subtitle_font.render(subtitle_text, True, subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 65))
        screen.blit(subtitle_surface, subtitle_rect)

    def draw(self, screen):
        """Render the insurance panic crisis interface"""
        if not self.active:
            return

        # Draw background with panic effects
        self.draw_background(screen)

        # Professional crisis interface title
        self.draw_professional_title(screen)

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
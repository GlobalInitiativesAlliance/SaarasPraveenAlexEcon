"""
Savings Calculator Activity
Shows the impossible math of saving for housing while homeless
"""
import pygame
import math
from src.activities.activities import Activity
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class SavingsCalculator(Activity):
    """Interactive visualization of the impossible savings timeline"""

    def __init__(self, game):
        super().__init__(game)
        self.narrative_ref = None  # Set by parent interior

        # Financial values
        self.deposit_needed = 2800
        self.monthly_savings = 50
        self.months_needed = 56
        self.years_needed = 4.7

        # Visual state
        self.animation_phase = 0  # 0: show calculation, 1: show timeline, 2: show trap
        self.animation_timer = 0
        self.shake_timer = 0
        self.pulse_timer = 0
        self.reveal_timer = 0

        # Timeline milestones
        self.milestones = [
            (1, "Day 30: Shelter kicks you out"),
            (3, "Month 3: Friends stop answering"),
            (6, "Month 6: Lost job from instability"),
            (12, "Year 1: Health declining"),
            (24, "Year 2: Still homeless"),
            (36, "Year 3: System working as designed"),
            (48, "Year 4: Hope extinguished"),
            (56, "Month 56: Finally have deposit (if nothing went wrong)")
        ]

        # UI elements
        self.continue_button_rect = None
        self.current_milestone = 0

    def start(self):
        """Start the savings calculator activity"""
        super().start()
        self.animation_phase = 0
        self.animation_timer = 0
        self.reveal_timer = 0
        self.current_milestone = 0

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(220)
        screen.blit(overlay, (0, 0))

        # Update animation timers
        self.animation_timer += 0.016
        self.pulse_timer += 0.016
        self.reveal_timer += 0.016

        # Main container
        container_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (20, 18, 15), container_rect)
        pygame.draw.rect(screen, (100, 90, 80), container_rect, 2)

        if self.animation_phase == 0:
            self.draw_calculation(screen)
        elif self.animation_phase == 1:
            self.draw_timeline(screen)
        elif self.animation_phase == 2:
            self.draw_trap(screen)

        # Continue button
        if self.reveal_timer > 2.0:
            self.draw_continue_button(screen)

    def draw_calculation(self, screen):
        """Show the brutal math"""
        title_font = pygame.font.Font(None, 48)
        calc_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)

        # Title
        title = title_font.render("The Impossible Math", True, (255, 100, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title, title_rect)

        # The calculation
        y_pos = 220

        # Deposit needed
        if self.reveal_timer > 0.5:
            text = calc_font.render("Deposit Needed:", True, (200, 180, 160))
            screen.blit(text, (300, y_pos))
            amount = calc_font.render(f"${self.deposit_needed}", True, (255, 220, 100))
            screen.blit(amount, (550, y_pos))

        y_pos += 60

        # Monthly savings
        if self.reveal_timer > 1.0:
            text = calc_font.render("Can Save Per Month:", True, (200, 180, 160))
            screen.blit(text, (300, y_pos))
            amount = calc_font.render(f"${self.monthly_savings}", True, (100, 255, 100))
            screen.blit(amount, (550, y_pos))

        y_pos += 80

        # Division line
        if self.reveal_timer > 1.5:
            pygame.draw.line(screen, (150, 130, 110), (300, y_pos), (650, y_pos), 2)

        y_pos += 40

        # Result
        if self.reveal_timer > 2.0:
            # Shake effect for emphasis
            shake_x = 0
            if self.reveal_timer > 2.5:
                self.shake_timer += 0.016
                shake_x = math.sin(self.shake_timer * 30) * 3

            text = calc_font.render("Time to Save:", True, (200, 180, 160))
            screen.blit(text, (300 + shake_x, y_pos))

            # Pulsing red for the devastating timeline
            pulse = abs(math.sin(self.pulse_timer * 2))
            color = (255, 100 + pulse * 50, 100)
            months = calc_font.render(f"{self.months_needed} months", True, color)
            screen.blit(months, (550 + shake_x, y_pos))

        y_pos += 50

        # Years conversion
        if self.reveal_timer > 2.5:
            big_font = pygame.font.Font(None, 56)
            years = big_font.render(f"{self.years_needed} YEARS", True, (255, 50, 50))
            years_rect = years.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 30))
            screen.blit(years, years_rect)

        # Assumptions text
        if self.reveal_timer > 3.0:
            y_pos += 100
            assume = small_font.render("*Assuming:", True, (150, 130, 110))
            screen.blit(assume, (300, y_pos))

            assumptions = [
                "• You never get sick",
                "• You never miss work",
                "• You have no emergencies",
                "• Rent doesn't increase",
                "• You find somewhere to sleep every night"
            ]

            y_offset = 30
            for assumption in assumptions:
                text = small_font.render(assumption, True, (130, 110, 90))
                screen.blit(text, (320, y_pos + y_offset))
                y_offset += 25

    def draw_timeline(self, screen):
        """Draw the timeline showing what happens during those 4.7 years"""
        title_font = pygame.font.Font(None, 42)
        milestone_font = pygame.font.Font(None, 24)

        # Title
        title = title_font.render("Meanwhile, During Those 4.7 Years...", True, (255, 180, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # Timeline base
        timeline_y = SCREEN_HEIGHT // 2
        timeline_start = 150
        timeline_end = SCREEN_WIDTH - 150
        timeline_width = timeline_end - timeline_start

        # Draw timeline line
        pygame.draw.line(screen, (100, 90, 80),
                        (timeline_start, timeline_y),
                        (timeline_end, timeline_y), 3)

        # Draw milestones
        for i, (month, event) in enumerate(self.milestones):
            if i > self.current_milestone:
                break

            x_pos = timeline_start + (month / 56) * timeline_width

            # Milestone marker
            color = (255, 100, 100) if "kicks you out" in event or "Lost job" in event else (200, 180, 160)
            pygame.draw.circle(screen, color, (int(x_pos), timeline_y), 8)

            # Milestone text (alternating above/below)
            text_y = timeline_y - 40 if i % 2 == 0 else timeline_y + 40
            text = milestone_font.render(event, True, color)
            text_rect = text.get_rect(center=(x_pos, text_y))
            screen.blit(text, text_rect)

            # Connect line
            pygame.draw.line(screen, (80, 70, 60),
                           (x_pos, timeline_y),
                           (x_pos, text_y + (10 if i % 2 == 0 else -10)), 1)

        # Progress the timeline
        if self.animation_timer > 1.0 and self.current_milestone < len(self.milestones) - 1:
            if self.animation_timer % 0.5 < 0.016:  # Every half second
                self.current_milestone += 1

        # Bottom message
        if self.current_milestone >= len(self.milestones) - 1:
            message_font = pygame.font.Font(None, 32)
            message = message_font.render("Where will you sleep for 1,700 nights?", True, (255, 50, 50))
            msg_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
            screen.blit(message, msg_rect)

    def draw_trap(self, screen):
        """Draw the circular trap visualization"""
        title_font = pygame.font.Font(None, 48)
        trap_font = pygame.font.Font(None, 28)

        # Title
        title = title_font.render("The Poverty Trap", True, (255, 100, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # Center of trap
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # Draw circular trap with rotating segments
        trap_elements = [
            ("Can't save while homeless", 0),
            ("Can't get housing without savings", 72),
            ("Can't get better job without address", 144),
            ("Can't get address without job", 216),
            ("Everything costs more when poor", 288)
        ]

        radius = 180
        for text, angle_offset in trap_elements:
            angle = math.radians(angle_offset + self.animation_timer * 20)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius

            # Draw arrow pointing to next
            next_angle = angle + math.radians(72)
            next_x = center_x + math.cos(next_angle) * radius
            next_y = center_y + math.sin(next_angle) * radius

            # Arrow
            mid_x = center_x + math.cos(angle + math.radians(36)) * (radius - 30)
            mid_y = center_y + math.sin(angle + math.radians(36)) * (radius - 30)
            pygame.draw.line(screen, (150, 50, 50), (x, y), (mid_x, mid_y), 2)

            # Text
            rendered_text = trap_font.render(text, True, (200, 180, 160))
            text_rect = rendered_text.get_rect(center=(x, y))
            screen.blit(rendered_text, text_rect)

        # Center text
        center_font = pygame.font.Font(None, 36)
        center_text = center_font.render("TRAPPED", True, (255, 50, 50))
        center_rect = center_text.get_rect(center=(center_x, center_y))

        # Pulsing effect
        pulse = abs(math.sin(self.pulse_timer * 2))
        scaled_font = pygame.font.Font(None, int(36 + pulse * 8))
        center_text = scaled_font.render("TRAPPED", True, (255, 50 + pulse * 50, 50))
        center_rect = center_text.get_rect(center=(center_x, center_y))
        screen.blit(center_text, center_rect)

        # Bottom message
        message_font = pygame.font.Font(None, 32)
        messages = [
            "The system is working exactly as designed.",
            "To keep you desperate. To keep wages low.",
            "Welcome to the permanent underclass."
        ]

        y_pos = SCREEN_HEIGHT - 200
        for msg in messages:
            if self.reveal_timer > 2 + messages.index(msg):
                text = message_font.render(msg, True, (180, 160, 140))
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                screen.blit(text, text_rect)
                y_pos += 35

    def draw_continue_button(self, screen):
        """Draw the continue button"""
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT - 100

        self.continue_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Button color changes on hover
        mouse_pos = pygame.mouse.get_pos()
        if self.continue_button_rect.collidepoint(mouse_pos):
            button_color = (100, 90, 80)
            text_color = (255, 220, 180)
        else:
            button_color = (60, 55, 50)
            text_color = (200, 180, 160)

        pygame.draw.rect(screen, button_color, self.continue_button_rect)
        pygame.draw.rect(screen, (150, 130, 110), self.continue_button_rect, 2)

        # Button text changes based on phase
        button_texts = ["See Timeline", "See The Trap", "Accept Reality"]
        button_text = button_texts[min(self.animation_phase, 2)]

        font = pygame.font.Font(None, 28)
        text = font.render(button_text, True, text_color)
        text_rect = text.get_rect(center=self.continue_button_rect.center)
        screen.blit(text, text_rect)

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active:
            return

        if button == 1:  # Left click
            if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
                if self.animation_phase < 2:
                    self.animation_phase += 1
                    self.reveal_timer = 0
                    self.animation_timer = 0
                    if self.animation_phase == 1:
                        self.current_milestone = 0
                else:
                    # Complete the activity
                    self.complete()

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if key == pygame.K_ESCAPE:
            self.complete()
        elif key == pygame.K_SPACE or key == pygame.K_RETURN:
            # Advance phase with space/enter
            if self.reveal_timer > 2.0:
                if self.animation_phase < 2:
                    self.animation_phase += 1
                    self.reveal_timer = 0
                    self.animation_timer = 0
                    if self.animation_phase == 1:
                        self.current_milestone = 0
                else:
                    self.complete()

    def handle_mouse_motion(self, pos):
        """Track mouse movement for hover effects"""
        pass

    def update(self, dt):
        """Update animation timers"""
        if self.active:
            self.animation_timer += dt
            self.pulse_timer += dt
            self.reveal_timer += dt
            if self.shake_timer > 0:
                self.shake_timer += dt
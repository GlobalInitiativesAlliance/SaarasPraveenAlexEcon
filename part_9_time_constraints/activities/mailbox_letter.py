"""
Mailbox Letter Mini-Game - Pressure/Urgency Version
Sort through mail to find the court summons
Reveals the conflict with school midterm
Features: Styled envelopes, mailbox visual, urgent particles, official document styling
"""
import pygame
import math
import random

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    PressureVisualComponents, UIAnimation, pressure_visuals
)
from .time_particles import pressure_particles
from .time_feedback import pressure_feedback


class MailboxLetter:
    """Mailbox sorting game to find court summons - Pressure themed"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Mail items with styling
        self.mail_items = [
            {
                "type": "junk",
                "title": "Pizza Coupons",
                "preview": "50% off your next order!",
                "color": PressureUIColors.HIGHLIGHT_DIM,
                "accent": (120, 115, 110),
                "icon": "AD",
                "important": False
            },
            {
                "type": "bill",
                "title": "Electric Bill",
                "preview": "Amount Due: $87.50",
                "color": PressureUIColors.URGENT_ORANGE,
                "accent": PressureUIColors.URGENT_ORANGE_DARK,
                "icon": "$",
                "important": False
            },
            {
                "type": "court",
                "title": "COURT SUMMONS",
                "preview": "Appearance Required",
                "color": PressureUIColors.PRESSURE_RED,
                "accent": PressureUIColors.PRESSURE_RED_DARK,
                "icon": "!",
                "important": True
            },
            {
                "type": "junk",
                "title": "Credit Card Offer",
                "preview": "You're pre-approved!",
                "color": PressureUIColors.HIGHLIGHT_DIM,
                "accent": (130, 125, 120),
                "icon": "CC",
                "important": False
            },
        ]

        # Mail item rects and animations
        self.mail_rects = []
        self.mail_animations = []
        self.card_width = 220
        self.card_height = 90

        # Selection state
        self.selected_index = -1
        self.hovered_index = -1

        # Game state
        self.found_summons = False
        self.show_summons = False
        self.summons_timer = 0
        self.time = 0

        # Result
        self.show_result = False
        self.result_timer = 0

    def start(self):
        """Start the mailbox game"""
        self.active = True
        self.completed = False
        self.selected_index = -1
        self.hovered_index = -1
        self.found_summons = False
        self.show_summons = False
        self.summons_timer = 0
        self.show_result = False
        self.result_timer = 0
        self.time = 0

        # Initialize mail positions (2x2 grid below mailbox)
        start_x = self.SCREEN_WIDTH // 2 - (self.card_width + 30)
        start_y = 280
        self.mail_rects = []
        self.mail_animations = []

        for i, mail in enumerate(self.mail_items):
            row = i // 2
            col = i % 2
            rect = pygame.Rect(
                start_x + col * (self.card_width + 60),
                start_y + row * (self.card_height + 25),
                self.card_width,
                self.card_height
            )
            self.mail_rects.append({
                "mail": mail,
                "rect": rect,
                "original_y": rect.y,
                "opened": False,
                "hover_offset": 0
            })
            self.mail_animations.append(UIAnimation(
                phase=i * 0.7,
                speed=0.8 + i * 0.1
            ))

        # Initialize particles and feedback
        pressure_particles.clear()
        pressure_particles.enable_ambient(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            stress_level=0.2
        )
        pressure_feedback.clear()

    def stop(self):
        """Stop the game"""
        self.active = False
        pressure_particles.disable_ambient()

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        self.time += dt

        # Update animations
        for anim in self.mail_animations:
            anim.update(dt)

        # Update hover offset animations
        for i, item in enumerate(self.mail_rects):
            target_offset = -8 if i == self.hovered_index else 0
            diff = target_offset - item["hover_offset"]
            item["hover_offset"] += diff * dt * 10

        if self.show_summons:
            self.summons_timer += dt

            # Emit urgent particles periodically
            if int(self.summons_timer * 3) != int((self.summons_timer - dt) * 3):
                pressure_particles.emit_alarm_particles(
                    self.SCREEN_WIDTH // 2,
                    self.SCREEN_HEIGHT // 2 - 50,
                    count=3
                )

            if self.summons_timer > 4.5:
                self.show_result = True
                pressure_feedback.add_urgent_summons_banner()

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 3.5:
                self.completed = True
                self.active = False

        # Update particles and feedback
        pressure_particles.update(dt)
        pressure_feedback.update(dt)

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_summons:
            return

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            old_hover = self.hovered_index
            self.hovered_index = -1
            for i, item in enumerate(self.mail_rects):
                if item["rect"].collidepoint(pos) and not item["opened"]:
                    self.hovered_index = i
                    # Emit glow on first hover
                    if old_hover != i:
                        pressure_particles.emit_selection_burst(
                            item["rect"].centerx,
                            item["rect"].centery,
                            item["mail"]["color"]
                        )

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, item in enumerate(self.mail_rects):
                if item["rect"].collidepoint(pos) and not item["opened"]:
                    item["opened"] = True

                    # Opening effect
                    pressure_particles.emit_clock_ticks(
                        (item["rect"].centerx, item["rect"].centery), 25, 6
                    )

                    if item["mail"]["important"]:
                        self.found_summons = True
                        self.show_summons = True

                        # Big warning effect for court summons
                        pressure_particles.emit_alarm_particles(
                            item["rect"].centerx,
                            item["rect"].centery,
                            count=15
                        )
                        pressure_particles.emit_conflict_pulse(
                            item["rect"].centerx,
                            item["rect"].centery,
                            PressureUIColors.PRESSURE_RED
                        )
                        pressure_feedback.trigger_screen_shake(12)
                        pressure_feedback.set_stress_level(0.7)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.show_summons:
                    self.show_result = True
                    pressure_feedback.add_urgent_summons_banner()

    def render(self, screen):
        """Render the mailbox game with pressure visuals"""
        # Background
        pressure_visuals.draw_pressure_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            stress_level=0.2 if not self.show_summons else 0.6
        )

        # Title
        title_color = PressureUIColors.HIGHLIGHT_WHITE
        title_glow = PressureUIColors.TIME_GOLD
        if self.show_summons:
            title_glow = PressureUIColors.PRESSURE_RED

        PressureVisualHelpers.draw_text_with_glow(
            screen, "Check Your Mail",
            (self.SCREEN_WIDTH // 2, 40),
            pressure_visuals.fonts['title'],
            title_color, title_glow
        )

        # Instructions
        PressureVisualHelpers.draw_text_with_glow(
            screen, "Click on each envelope to open it",
            (self.SCREEN_WIDTH // 2, 80),
            pressure_visuals.fonts['small'],
            PressureUIColors.HIGHLIGHT_DIM,
            PressureUIColors.CALM_BLUE
        )

        # Mailbox visual
        self._render_mailbox(screen)

        # Draw mail envelopes
        for i, item in enumerate(self.mail_rects):
            self._render_envelope(screen, item, i)

        # Show court summons popup
        if self.show_summons:
            self._render_summons_popup(screen)

        # Show result
        if self.show_result:
            self._render_result(screen)

        # Render particles and feedback
        pressure_particles.render(screen)
        pressure_feedback.render(screen)

    def _render_mailbox(self, screen):
        """Render the mailbox visual"""
        mailbox_x = self.SCREEN_WIDTH // 2
        mailbox_y = 180

        # Mailbox post
        post_rect = pygame.Rect(mailbox_x - 8, mailbox_y + 40, 16, 80)
        pygame.draw.rect(screen, (80, 70, 60), post_rect)
        pygame.draw.rect(screen, (100, 90, 80), post_rect, 2)

        # Mailbox body
        body_rect = pygame.Rect(mailbox_x - 60, mailbox_y - 25, 120, 70)

        # Shadow
        shadow_rect = body_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=8)

        # Main body
        pygame.draw.rect(screen, (70, 85, 110), body_rect, border_radius=8)
        pygame.draw.rect(screen, (90, 110, 140), body_rect.inflate(-8, -8), border_radius=6)

        # Door flap (open)
        flap_rect = pygame.Rect(mailbox_x - 50, mailbox_y - 35, 100, 20)
        pygame.draw.rect(screen, (100, 120, 150), flap_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 140, 170), flap_rect, 2, border_radius=4)

        # Flag
        flag_color = PressureUIColors.PRESSURE_RED if not self.found_summons else PressureUIColors.HIGHLIGHT_DIM
        pygame.draw.rect(screen, flag_color,
                        (mailbox_x + 55, mailbox_y - 15, 20, 30))
        pygame.draw.rect(screen, (180, 80, 80),
                        (mailbox_x + 55, mailbox_y - 15, 20, 30), 2)

        # "MAIL" text
        mail_text = pressure_visuals.fonts['small'].render("MAIL", True, (60, 75, 100))
        screen.blit(mail_text, (mailbox_x - mail_text.get_width() // 2, mailbox_y + 5))

    def _render_envelope(self, screen, item, index):
        """Render a mail envelope with styling"""
        mail = item["mail"]
        rect = item["rect"]
        anim = self.mail_animations[index] if index < len(self.mail_animations) else None

        is_hover = (index == self.hovered_index)
        is_opened = item["opened"]

        # Calculate position with hover and float
        float_offset = 0
        if anim and not is_opened:
            float_offset = int(math.sin(anim.phase) * 3)

        draw_y = rect.y + float_offset + item["hover_offset"]
        draw_rect = pygame.Rect(rect.x, draw_y, rect.width, rect.height)

        # Glow for important/hover
        if mail["important"] and not is_opened:
            glow_intensity = 0.4 + math.sin(self.time * 4) * 0.2
            for i in range(4, 0, -1):
                glow_rect = draw_rect.inflate(i * 6, i * 4)
                glow_alpha = int(50 * glow_intensity * (1 - i / 5))
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*PressureUIColors.PRESSURE_RED, glow_alpha),
                               (0, 0, glow_rect.width, glow_rect.height), border_radius=8)
                screen.blit(glow_surface, glow_rect)
        elif is_hover:
            for i in range(3, 0, -1):
                glow_rect = draw_rect.inflate(i * 4, i * 3)
                glow_alpha = int(30 * (1 - i / 4))
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*mail["color"], glow_alpha),
                               (0, 0, glow_rect.width, glow_rect.height), border_radius=8)
                screen.blit(glow_surface, glow_rect)

        # Envelope background
        if is_opened:
            bg_color = tuple(c // 2 for c in mail["accent"])
        elif is_hover:
            bg_color = tuple(min(255, c + 20) for c in mail["accent"])
        else:
            bg_color = mail["accent"]

        # Draw envelope shape
        envelope_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)

        # Main envelope body
        pygame.draw.rect(envelope_surface, (*bg_color, 255 if not is_opened else 180),
                        (0, 0, draw_rect.width, draw_rect.height), border_radius=6)

        # Envelope flap (triangle at top)
        flap_points = [
            (0, 0),
            (draw_rect.width // 2, 30),
            (draw_rect.width, 0)
        ]
        flap_color = tuple(max(0, c - 20) for c in bg_color)
        pygame.draw.polygon(envelope_surface, (*flap_color, 200 if not is_opened else 120), flap_points)

        screen.blit(envelope_surface, draw_rect)

        # Border
        border_color = mail["color"] if not is_opened else PressureUIColors.HIGHLIGHT_DIM
        if mail["important"] and not is_opened:
            pulse = 0.7 + math.sin(self.time * 5) * 0.3
            border_color = tuple(int(c * pulse) for c in PressureUIColors.PRESSURE_RED_LIGHT)
        pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=6)

        # Content
        if not is_opened:
            # Type indicator with icon
            if mail["type"] == "junk":
                self._draw_junk_indicator(screen, draw_rect)
            elif mail["type"] == "bill":
                self._draw_bill_indicator(screen, draw_rect)
            elif mail["type"] == "court":
                self._draw_court_indicator(screen, draw_rect)
        else:
            # Opened indicator
            opened_text = pressure_visuals.fonts['small'].render("[OPENED]", True,
                                                                  PressureUIColors.HIGHLIGHT_DIM)
            screen.blit(opened_text, (draw_rect.centerx - opened_text.get_width() // 2,
                                      draw_rect.centery - opened_text.get_height() // 2))

        # Title and preview (if not opened)
        if not is_opened:
            title_color = PressureUIColors.HIGHLIGHT_WHITE if mail["important"] else PressureUIColors.HIGHLIGHT_DIM
            title_text = pressure_visuals.fonts['body'].render(mail["title"], True, title_color)
            screen.blit(title_text, (draw_rect.x + 45, draw_rect.y + 35))

            preview_text = pressure_visuals.fonts['small'].render(mail["preview"], True,
                                                                   PressureUIColors.HIGHLIGHT_DIM)
            screen.blit(preview_text, (draw_rect.x + 45, draw_rect.y + 60))

    def _draw_junk_indicator(self, screen, rect):
        """Draw junk mail indicator"""
        pygame.draw.circle(screen, (100, 95, 90), (rect.x + 25, rect.y + 50), 15)
        ad_text = pressure_visuals.fonts['small'].render("AD", True, (60, 55, 50))
        screen.blit(ad_text, (rect.x + 17, rect.y + 43))

    def _draw_bill_indicator(self, screen, rect):
        """Draw bill indicator"""
        pygame.draw.circle(screen, PressureUIColors.URGENT_ORANGE, (rect.x + 25, rect.y + 50), 15)
        bill_text = pressure_visuals.fonts['body'].render("$", True, PressureUIColors.DARK_BG)
        screen.blit(bill_text, (rect.x + 19, rect.y + 42))

    def _draw_court_indicator(self, screen, rect):
        """Draw court summons indicator with urgency"""
        # Pulsing warning circle
        pulse = 0.8 + math.sin(self.time * 6) * 0.2
        radius = int(15 * pulse)
        pygame.draw.circle(screen, PressureUIColors.PRESSURE_RED, (rect.x + 25, rect.y + 50), radius)

        # Exclamation mark
        exclaim_text = pressure_visuals.fonts['body'].render("!", True, PressureUIColors.HIGHLIGHT_WHITE)
        screen.blit(exclaim_text, (rect.x + 21, rect.y + 42))

        # URGENT stamp
        stamp_font = pressure_visuals.fonts['small']
        stamp_text = stamp_font.render("URGENT", True, PressureUIColors.PRESSURE_RED)
        # Rotated stamp effect
        rotated = pygame.transform.rotate(stamp_text, -15)
        screen.blit(rotated, (rect.x + rect.width - 65, rect.y + 8))

    def _render_summons_popup(self, screen):
        """Render the court summons popup with official styling"""
        # Darken background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(self.summons_timer * 150))
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        # Document panel
        doc_rect = pygame.Rect(140, 120, 520, 360)

        # Panel glow
        pulse = 0.5 + math.sin(self.time * 4) * 0.2
        for i in range(5, 0, -1):
            glow_rect = doc_rect.inflate(i * 8, i * 6)
            glow_alpha = int(40 * pulse * (1 - i / 6))
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*PressureUIColors.PRESSURE_RED, glow_alpha),
                           (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
            screen.blit(glow_surface, glow_rect)

        # Document background
        pressure_visuals.draw_pressure_panel(
            screen, doc_rect,
            glow_color=PressureUIColors.PRESSURE_RED,
            glow_intensity=0.5
        )

        # Header with official styling
        header_rect = pygame.Rect(doc_rect.x, doc_rect.y, doc_rect.width, 50)
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED_DARK, header_rect,
                        border_top_left_radius=10, border_top_right_radius=10)

        PressureVisualHelpers.draw_text_with_glow(
            screen, "COURT SUMMONS",
            (doc_rect.centerx, doc_rect.y + 25),
            pressure_visuals.fonts['heading'],
            PressureUIColors.HIGHLIGHT_WHITE,
            PressureUIColors.PRESSURE_RED
        )

        # Content
        content_lines = [
            ("You are required to appear:", False, 1.0),
            ("", False, 0),
            ("Date: Next Tuesday", False, 1.5),
            ("Time: 10:00 AM", False, 1.8),
            ("", False, 0),
            ("Case: Housing Dispute #2024-1847", False, 2.2),
            ("", False, 0),
            ("CONFLICT: This overlaps with your midterm exam!", True, 2.8)
        ]

        y_offset = 75
        for line, is_warning, appear_time in content_lines:
            if not line:
                y_offset += 10
                continue

            if self.summons_timer >= appear_time:
                progress = min(1.0, (self.summons_timer - appear_time) / 0.5)

                if is_warning:
                    # Pulsing warning text
                    warning_pulse = 0.7 + math.sin(self.time * 6) * 0.3
                    warning_color = tuple(int(c * warning_pulse) for c in PressureUIColors.PRESSURE_RED_LIGHT)
                    PressureVisualHelpers.draw_text_with_glow(
                        screen, line,
                        (doc_rect.centerx, doc_rect.y + y_offset),
                        pressure_visuals.fonts['body'],
                        warning_color,
                        PressureUIColors.PRESSURE_RED
                    )
                else:
                    text_surf = pressure_visuals.fonts['body'].render(line, True,
                                                                       PressureUIColors.HIGHLIGHT_DIM)
                    text_surf.set_alpha(int(255 * progress))
                    screen.blit(text_surf, (doc_rect.x + 30, doc_rect.y + y_offset - 10))

            y_offset += 30

        # Continue prompt
        if self.summons_timer > 3.5:
            prompt_alpha = min(255, int((self.summons_timer - 3.5) * 200))
            prompt_text = pressure_visuals.fonts['small'].render(
                "Press SPACE to continue...", True, PressureUIColors.HIGHLIGHT_DIM
            )
            prompt_text.set_alpha(prompt_alpha)
            screen.blit(prompt_text, (doc_rect.centerx - prompt_text.get_width() // 2,
                                      doc_rect.bottom - 35))

    def _render_result(self, screen):
        """Render the result overlay"""
        result_rect = pygame.Rect(175, 470, 450, 100)

        pressure_visuals.draw_pressure_panel(
            screen, result_rect,
            glow_color=PressureUIColors.URGENT_ORANGE,
            glow_intensity=0.4
        )

        result_alpha = min(255, int(self.result_timer * 200))

        PressureVisualHelpers.draw_text_with_glow(
            screen, "Court date conflicts with school.",
            (result_rect.centerx, result_rect.y + 30),
            pressure_visuals.fonts['body'],
            PressureUIColors.PRESSURE_RED_LIGHT,
            PressureUIColors.PRESSURE_RED
        )

        if self.result_timer > 0.5:
            text2 = pressure_visuals.fonts['body'].render(
                "What will you tell your teacher?", True, PressureUIColors.HIGHLIGHT_DIM
            )
            text2.set_alpha(min(255, int((self.result_timer - 0.5) * 200)))
            screen.blit(text2, (result_rect.centerx - text2.get_width() // 2, result_rect.y + 60))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

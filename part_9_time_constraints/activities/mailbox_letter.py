"""
Mailbox Letter Mini-Game - Clean Version
Sort through mail to find the court summons
Reveals the conflict with school midterm
Clean visuals, no heavy effects
"""
import pygame
import math

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    UIAnimation, pressure_visuals
)
from .time_particles import time_particles
from .time_feedback import time_feedback


class MailboxLetter:
    """Mailbox sorting game to find court summons - Clean version"""

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
                "color": PressureUIColors.TEXT_MUTED,
                "accent": (120, 115, 110),
                "icon": "AD",
                "important": False
            },
            {
                "type": "bill",
                "title": "Electric Bill",
                "preview": "Amount Due: $87.50",
                "color": PressureUIColors.URGENT_ORANGE,
                "accent": (180, 130, 80),
                "icon": "$",
                "important": False
            },
            {
                "type": "court",
                "title": "COURT SUMMONS",
                "preview": "Appearance Required",
                "color": PressureUIColors.PRESSURE_RED,
                "accent": (180, 80, 80),
                "icon": "!",
                "important": True
            },
            {
                "type": "junk",
                "title": "Credit Card Offer",
                "preview": "You're pre-approved!",
                "color": PressureUIColors.TEXT_MUTED,
                "accent": (130, 125, 120),
                "icon": "CC",
                "important": False
            },
        ]

        # Mail item rects
        self.mail_rects = []
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
                "opened": False,
                "hover_offset": 0
            })

        # Clear feedback
        time_particles.clear()
        time_feedback.clear()

    def stop(self):
        """Stop the game"""
        self.active = False

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        self.time += dt

        # Update hover offset animations
        for i, item in enumerate(self.mail_rects):
            target_offset = -8 if i == self.hovered_index else 0
            diff = target_offset - item["hover_offset"]
            item["hover_offset"] += diff * dt * 10

        if self.show_summons:
            self.summons_timer += dt

            if self.summons_timer > 4.5:
                self.show_result = True
                time_feedback.add_urgent_summons_banner()

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 3.5:
                self.completed = True
                self.active = False

        # Update feedback
        time_feedback.update(dt)

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_summons:
            return

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_index = -1
            for i, item in enumerate(self.mail_rects):
                if item["rect"].collidepoint(pos) and not item["opened"]:
                    self.hovered_index = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, item in enumerate(self.mail_rects):
                if item["rect"].collidepoint(pos) and not item["opened"]:
                    item["opened"] = True

                    if item["mail"]["important"]:
                        self.found_summons = True
                        self.show_summons = True
                        time_feedback.set_stress_level(0.7)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.show_summons:
                    self.show_result = True
                    time_feedback.add_urgent_summons_banner()

    def render(self, screen):
        """Render the mailbox game with clean visuals"""
        # Background with stress tint
        stress = 0.2 if not self.show_summons else 0.6
        pressure_visuals.draw_background(screen, stress)

        # Title
        title_color = PressureUIColors.TEXT_PRIMARY
        if self.show_summons:
            title_color = PressureUIColors.PRESSURE_RED_LIGHT
        pressure_visuals.draw_title(screen, "Check Your Mail",
                                    self.SCREEN_WIDTH // 2, 40)

        # Instructions
        inst_surface = pressure_visuals.fonts['body'].render(
            "Click on each envelope to open it", True, PressureUIColors.TEXT_SECONDARY
        )
        screen.blit(inst_surface,
                   (self.SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, 80))

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

        # Render feedback on top
        time_feedback.render(screen)

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
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_rect.width, shadow_rect.height),
                        border_radius=8)
        screen.blit(shadow_surf, shadow_rect)

        # Main body
        pygame.draw.rect(screen, (70, 85, 110), body_rect, border_radius=8)
        pygame.draw.rect(screen, (90, 110, 140), body_rect.inflate(-8, -8), border_radius=6)

        # Door flap (open)
        flap_rect = pygame.Rect(mailbox_x - 50, mailbox_y - 35, 100, 20)
        pygame.draw.rect(screen, (100, 120, 150), flap_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 140, 170), flap_rect, 2, border_radius=4)

        # Flag
        flag_color = PressureUIColors.PRESSURE_RED if not self.found_summons else PressureUIColors.TEXT_MUTED
        pygame.draw.rect(screen, flag_color,
                        (mailbox_x + 55, mailbox_y - 15, 20, 30))
        pygame.draw.rect(screen, (180, 80, 80),
                        (mailbox_x + 55, mailbox_y - 15, 20, 30), 2)

        # "MAIL" text
        mail_text = pressure_visuals.fonts['small'].render("MAIL", True, (60, 75, 100))
        screen.blit(mail_text, (mailbox_x - mail_text.get_width() // 2, mailbox_y + 5))

    def _render_envelope(self, screen, item, index):
        """Render a mail envelope with simple styling"""
        mail = item["mail"]
        rect = item["rect"]

        is_hover = (index == self.hovered_index)
        is_opened = item["opened"]

        # Calculate position with hover offset
        draw_y = rect.y + item["hover_offset"]
        draw_rect = pygame.Rect(rect.x, draw_y, rect.width, rect.height)

        # Simple highlight for important/hover
        if mail["important"] and not is_opened:
            # Pulsing border for important mail
            pulse = PressureVisualHelpers.get_pulse_alpha(180, 255, 4.0)
            highlight_rect = draw_rect.inflate(6, 4)
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surf, (*PressureUIColors.PRESSURE_RED, pulse // 3),
                           (0, 0, highlight_rect.width, highlight_rect.height), border_radius=10)
            screen.blit(highlight_surf, highlight_rect)
        elif is_hover:
            # Simple hover highlight
            highlight_rect = draw_rect.inflate(4, 3)
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surf, (*mail["color"], 40),
                           (0, 0, highlight_rect.width, highlight_rect.height), border_radius=8)
            screen.blit(highlight_surf, highlight_rect)

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
        alpha = 255 if not is_opened else 180
        pygame.draw.rect(envelope_surface, (*bg_color, alpha),
                        (0, 0, draw_rect.width, draw_rect.height), border_radius=6)

        # Envelope flap (triangle at top)
        flap_points = [
            (0, 0),
            (draw_rect.width // 2, 30),
            (draw_rect.width, 0)
        ]
        flap_color = tuple(max(0, c - 20) for c in bg_color)
        flap_alpha = 200 if not is_opened else 120
        pygame.draw.polygon(envelope_surface, (*flap_color, flap_alpha), flap_points)

        screen.blit(envelope_surface, draw_rect)

        # Border
        if mail["important"] and not is_opened:
            pulse = PressureVisualHelpers.get_pulse_alpha(180, 255, 5.0)
            border_color = tuple(int(c * pulse / 255) for c in PressureUIColors.PRESSURE_RED_LIGHT)
        else:
            border_color = mail["color"] if not is_opened else PressureUIColors.TEXT_MUTED
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
                                                                  PressureUIColors.TEXT_MUTED)
            screen.blit(opened_text, (draw_rect.centerx - opened_text.get_width() // 2,
                                      draw_rect.centery - opened_text.get_height() // 2))

        # Title and preview (if not opened)
        if not is_opened:
            title_color = PressureUIColors.TEXT_PRIMARY if mail["important"] else PressureUIColors.TEXT_SECONDARY
            title_text = pressure_visuals.fonts['body'].render(mail["title"], True, title_color)
            screen.blit(title_text, (draw_rect.x + 45, draw_rect.y + 35))

            preview_text = pressure_visuals.fonts['small'].render(mail["preview"], True,
                                                                   PressureUIColors.TEXT_MUTED)
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
        pulse = PressureVisualHelpers.get_pulse_alpha(200, 255, 6.0)
        radius = 15
        pygame.draw.circle(screen, PressureUIColors.PRESSURE_RED, (rect.x + 25, rect.y + 50), radius)

        # Exclamation mark
        exclaim_text = pressure_visuals.fonts['body'].render("!", True, PressureUIColors.TEXT_PRIMARY)
        screen.blit(exclaim_text, (rect.x + 21, rect.y + 42))

        # URGENT text (no rotation for performance)
        stamp_text = pressure_visuals.fonts['small'].render("URGENT", True, PressureUIColors.PRESSURE_RED)
        screen.blit(stamp_text, (rect.right - stamp_text.get_width() - 8, rect.y + 8))

    def _render_summons_popup(self, screen):
        """Render the court summons popup with clean styling"""
        # Darken background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = min(180, int(self.summons_timer * 150))
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        # Document panel
        doc_rect = pygame.Rect(140, 120, 520, 360)

        # Panel background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, doc_rect, border_radius=10)
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED, doc_rect, 3, border_radius=10)

        # Header with official styling
        header_rect = pygame.Rect(doc_rect.x, doc_rect.y, doc_rect.width, 50)
        pygame.draw.rect(screen, PressureUIColors.PRESSURE_RED_DARK, header_rect,
                        border_top_left_radius=10, border_top_right_radius=10)

        header_text = pressure_visuals.fonts['heading'].render(
            "COURT SUMMONS", True, PressureUIColors.TEXT_PRIMARY
        )
        screen.blit(header_text, (doc_rect.centerx - header_text.get_width() // 2, doc_rect.y + 12))

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
                    pulse = PressureVisualHelpers.get_pulse_alpha(180, 255, 6.0)
                    warning_color = PressureUIColors.PRESSURE_RED_LIGHT
                    warning_surf = pressure_visuals.fonts['body_bold'].render(line, True, warning_color)
                    warning_surf.set_alpha(pulse)
                    screen.blit(warning_surf,
                               (doc_rect.centerx - warning_surf.get_width() // 2, doc_rect.y + y_offset - 10))
                else:
                    text_surf = pressure_visuals.fonts['body'].render(line, True,
                                                                       PressureUIColors.TEXT_SECONDARY)
                    text_surf.set_alpha(int(255 * progress))
                    screen.blit(text_surf, (doc_rect.x + 30, doc_rect.y + y_offset - 10))

            y_offset += 30

        # Continue prompt
        if self.summons_timer > 3.5:
            prompt_alpha = min(255, int((self.summons_timer - 3.5) * 200))
            prompt_text = pressure_visuals.fonts['small'].render(
                "Press SPACE to continue...", True, PressureUIColors.TEXT_MUTED
            )
            prompt_text.set_alpha(prompt_alpha)
            screen.blit(prompt_text, (doc_rect.centerx - prompt_text.get_width() // 2,
                                      doc_rect.bottom - 35))

    def _render_result(self, screen):
        """Render the result overlay"""
        result_rect = pygame.Rect(175, 470, 450, 100)

        # Panel background
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, result_rect, border_radius=10)
        pygame.draw.rect(screen, PressureUIColors.URGENT_ORANGE, result_rect, 2, border_radius=10)

        # Result text
        result_surface = pressure_visuals.fonts['body_bold'].render(
            "Court date conflicts with school.", True, PressureUIColors.PRESSURE_RED_LIGHT
        )
        screen.blit(result_surface,
                   (result_rect.centerx - result_surface.get_width() // 2, result_rect.y + 25))

        if self.result_timer > 0.5:
            text2 = pressure_visuals.fonts['body'].render(
                "What will you tell your teacher?", True, PressureUIColors.TEXT_SECONDARY
            )
            alpha = min(255, int((self.result_timer - 0.5) * 200))
            text2.set_alpha(alpha)
            screen.blit(text2, (result_rect.centerx - text2.get_width() // 2, result_rect.y + 60))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

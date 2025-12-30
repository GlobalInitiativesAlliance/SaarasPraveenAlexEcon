"""
Mailbox Letter Mini-Game
Sort through mail to find the court summons
Reveals the conflict with school midterm
"""
import pygame


class MailboxLetter:
    """Mailbox sorting game to find court summons"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Mail items
        self.mail_items = [
            {
                "type": "junk",
                "title": "Pizza Coupons",
                "preview": "50% off your next order!",
                "color": (100, 100, 100),
                "important": False
            },
            {
                "type": "bill",
                "title": "Electric Bill",
                "preview": "Amount Due: $87.50",
                "color": (180, 150, 100),
                "important": False
            },
            {
                "type": "court",
                "title": "COURT SUMMONS",
                "preview": "Appearance Required",
                "color": (200, 80, 80),
                "important": True
            },
            {
                "type": "junk",
                "title": "Credit Card Offer",
                "preview": "You're pre-approved!",
                "color": (100, 100, 100),
                "important": False
            },
        ]

        # Mail item rects
        self.mail_rects = []
        self.card_width = 200
        self.card_height = 80

        # Selection state
        self.selected_index = -1
        self.hovered_index = -1

        # Game state
        self.found_summons = False
        self.show_summons = False
        self.summons_timer = 0

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

        # Initialize mail positions
        start_x = 100
        start_y = 200
        self.mail_rects = []
        for i, mail in enumerate(self.mail_items):
            row = i // 2
            col = i % 2
            rect = pygame.Rect(
                start_x + col * (self.card_width + 50),
                start_y + row * (self.card_height + 30),
                self.card_width,
                self.card_height
            )
            self.mail_rects.append({
                "mail": mail,
                "rect": rect,
                "opened": False
            })

    def stop(self):
        """Stop the game"""
        self.active = False

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        if self.show_summons:
            self.summons_timer += dt
            if self.summons_timer > 4.0:
                self.show_result = True

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 3.0:
                self.completed = True
                self.active = False

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_summons:
            return

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_index = -1
            for i, item in enumerate(self.mail_rects):
                if item["rect"].collidepoint(pos):
                    self.hovered_index = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, item in enumerate(self.mail_rects):
                if item["rect"].collidepoint(pos):
                    item["opened"] = True
                    if item["mail"]["important"]:
                        self.found_summons = True
                        self.show_summons = True
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.show_summons:
                    self.show_result = True

    def render(self, screen):
        """Render the mailbox game"""
        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((35, 35, 45))
        overlay.set_alpha(245)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Check Your Mail", True, (200, 200, 210))
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst = inst_font.render("Click on each piece of mail to open it", True, (150, 150, 160))
        screen.blit(inst, (self.SCREEN_WIDTH // 2 - inst.get_width() // 2, 80))

        # Mailbox icon
        mailbox_font = pygame.font.Font(None, 60)
        mailbox_icon = mailbox_font.render("[MAILBOX]", True, (120, 120, 130))
        screen.blit(mailbox_icon, (self.SCREEN_WIDTH // 2 - mailbox_icon.get_width() // 2, 130))

        # Draw mail items
        card_font = pygame.font.Font(None, 24)
        for i, item in enumerate(self.mail_rects):
            mail = item["mail"]
            rect = item["rect"]

            # Card background
            bg_color = mail["color"]
            if i == self.hovered_index:
                bg_color = tuple(min(255, c + 40) for c in bg_color)
            if item["opened"]:
                bg_color = tuple(c // 2 for c in bg_color)

            pygame.draw.rect(screen, bg_color, rect)

            # Border
            border_color = (200, 200, 200) if mail["important"] else (120, 120, 130)
            if mail["important"] and not item["opened"]:
                border_color = (255, 100, 100)
            pygame.draw.rect(screen, border_color, rect, 2)

            # Text
            title_text = card_font.render(mail["title"], True, (255, 255, 255))
            screen.blit(title_text, (rect.x + 10, rect.y + 15))

            preview_text = card_font.render(mail["preview"], True, (200, 200, 200))
            screen.blit(preview_text, (rect.x + 10, rect.y + 45))

            if item["opened"]:
                opened_text = card_font.render("[OPENED]", True, (150, 150, 150))
                screen.blit(opened_text, (rect.x + rect.width - 80, rect.y + 5))

        # Show court summons popup
        if self.show_summons:
            summons_rect = pygame.Rect(150, 150, 500, 300)
            pygame.draw.rect(screen, (60, 40, 40), summons_rect)
            pygame.draw.rect(screen, (200, 80, 80), summons_rect, 4)

            summons_font = pygame.font.Font(None, 36)
            header = summons_font.render("COURT SUMMONS", True, (255, 150, 150))
            screen.blit(header, (summons_rect.centerx - header.get_width() // 2, summons_rect.y + 30))

            content_font = pygame.font.Font(None, 26)
            lines = [
                "You are required to appear:",
                "",
                "Date: Next Tuesday",
                "Time: 10:00 AM",
                "",
                "Case: Housing Dispute #2024-1847",
                "",
                "CONFLICT: This is during your midterm exam."
            ]

            y_offset = 80
            for line in lines:
                if "CONFLICT" in line:
                    text = content_font.render(line, True, (255, 100, 100))
                else:
                    text = content_font.render(line, True, (200, 200, 200))
                screen.blit(text, (summons_rect.x + 30, summons_rect.y + y_offset))
                y_offset += 28

        # Show result
        if self.show_result:
            result_rect = pygame.Rect(200, 450, 400, 100)
            pygame.draw.rect(screen, (50, 45, 55), result_rect)
            pygame.draw.rect(screen, (150, 100, 100), result_rect, 2)

            result_font = pygame.font.Font(None, 28)
            text1 = result_font.render("Court date conflicts with school.", True, (200, 150, 150))
            screen.blit(text1, (result_rect.centerx - text1.get_width() // 2, result_rect.y + 25))

            text2 = result_font.render("What will you tell your teacher?", True, (180, 180, 180))
            screen.blit(text2, (result_rect.centerx - text2.get_width() // 2, result_rect.y + 60))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

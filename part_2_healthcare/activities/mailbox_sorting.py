"""
Mailbox Sorting Mini-Game
Drag letters to "Important" or "Junk" piles
"""
import pygame
import random

class MailboxSortingGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Mail items to sort
        self.mail_items = [
            {"text": "Notice: Your Medi-Cal coverage has ended", "category": "important", "is_critical": True},
            {"text": "50% Off Pizza Special!", "category": "junk", "is_critical": False},
            {"text": "Therapy Appointment Reminder", "category": "important", "is_critical": False},
            {"text": "Credit Card Pre-Approval", "category": "junk", "is_critical": False},
            {"text": "Bank Statement", "category": "important", "is_critical": False},
            {"text": "Furniture Sale - Limited Time!", "category": "junk", "is_critical": False},
            {"text": "Foster Youth Services Update", "category": "important", "is_critical": False},
            {"text": "Win $1000 Cash Now!", "category": "junk", "is_critical": False}
        ]

        # Shuffle mail order
        random.shuffle(self.mail_items)

        # Game state
        self.current_mail = 0
        self.dragging = False
        self.drag_offset = (0, 0)
        self.score = 0
        self.mistakes = 0
        self.found_critical = False

        # UI elements
        self.mail_rect = pygame.Rect(500, 200, 280, 100)
        self.important_pile = pygame.Rect(200, 450, 200, 150)
        self.junk_pile = pygame.Rect(880, 450, 200, 150)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.RED = (220, 20, 60)
        self.GREEN = (34, 139, 34)
        self.GRAY = (128, 128, 128)
        self.LIGHT_BLUE = (173, 216, 230)
        self.LIGHT_RED = (255, 182, 193)

        # Fonts
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

    def handle_event(self, event):
        """Handle player input"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicking on current mail
            if self.mail_rect.collidepoint(mouse_pos) and self.current_mail < len(self.mail_items):
                self.dragging = True
                self.drag_offset = (
                    mouse_pos[0] - self.mail_rect.x,
                    mouse_pos[1] - self.mail_rect.y
                )

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                mouse_pos = pygame.mouse.get_pos()

                # Check which pile the mail was dropped on
                current_item = self.mail_items[self.current_mail]

                if self.important_pile.collidepoint(mouse_pos):
                    self.sort_mail("important", current_item)
                elif self.junk_pile.collidepoint(mouse_pos):
                    self.sort_mail("junk", current_item)
                else:
                    # Reset position if dropped elsewhere
                    self.mail_rect.x = 500
                    self.mail_rect.y = 200

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            self.mail_rect.x = mouse_pos[0] - self.drag_offset[0]
            self.mail_rect.y = mouse_pos[1] - self.drag_offset[1]

        return True

    def sort_mail(self, pile, mail_item):
        """Handle mail sorting result"""
        correct = (pile == mail_item["category"])

        if correct:
            self.score += 1
            if mail_item["is_critical"]:
                self.found_critical = True
        else:
            self.mistakes += 1

        # Move to next mail
        self.current_mail += 1

        # Reset mail position
        self.mail_rect.x = 500
        self.mail_rect.y = 200

        # Check if game is complete
        if self.current_mail >= len(self.mail_items):
            self.complete_game()

    def complete_game(self):
        """Complete the mailbox sorting game"""
        self.completed = True

        # Must find the critical Medi-Cal notice to progress
        if self.found_critical:
            if self.objective_manager:
                self.objective_manager.advance_to_next_objective()
        else:
            # Player missed the important notice - restart or hint
            self.current_mail = 0
            self.score = 0
            self.mistakes = 0
            self.found_critical = False
            random.shuffle(self.mail_items)

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

    def render(self, screen):
        """Render the mailbox sorting interface"""
        if not self.active:
            return

        # Background
        screen.fill((240, 248, 255))

        # Title
        title = self.font_large.render("Sort Your Mail", True, self.BLACK)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Instructions
        instructions = [
            "Drag mail to the correct pile:",
            "Important mail → Left pile",
            "Junk mail → Right pile"
        ]

        y = 100
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, self.GRAY)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
            screen.blit(text, text_rect)
            y += 25

        # Draw piles
        pygame.draw.rect(screen, self.LIGHT_BLUE, self.important_pile)
        pygame.draw.rect(screen, self.BLUE, self.important_pile, 3)

        pygame.draw.rect(screen, self.LIGHT_RED, self.junk_pile)
        pygame.draw.rect(screen, self.RED, self.junk_pile, 3)

        # Pile labels
        important_label = self.font_medium.render("IMPORTANT", True, self.BLUE)
        important_rect = important_label.get_rect(center=self.important_pile.center)
        screen.blit(important_label, important_rect)

        junk_label = self.font_medium.render("JUNK", True, self.RED)
        junk_rect = junk_label.get_rect(center=self.junk_pile.center)
        screen.blit(junk_label, junk_rect)

        # Current mail item
        if self.current_mail < len(self.mail_items):
            current_item = self.mail_items[self.current_mail]

            # Mail envelope
            color = self.RED if current_item["is_critical"] else self.WHITE
            pygame.draw.rect(screen, color, self.mail_rect)
            pygame.draw.rect(screen, self.BLACK, self.mail_rect, 2)

            # Mail text (wrapped)
            text = current_item["text"]
            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                if len(test_line) <= 35:  # Characters per line
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())

            # Render lines
            y_offset = self.mail_rect.y + 10
            for line in lines:
                line_surface = self.font_small.render(line, True, self.BLACK)
                screen.blit(line_surface, (self.mail_rect.x + 10, y_offset))
                y_offset += 20

        # Progress
        progress_text = f"Mail: {self.current_mail + 1}/{len(self.mail_items)}"
        progress_surface = self.font_medium.render(progress_text, True, self.BLACK)
        screen.blit(progress_surface, (50, 50))

        # Score
        score_text = f"Correct: {self.score} | Mistakes: {self.mistakes}"
        score_surface = self.font_medium.render(score_text, True, self.BLACK)
        screen.blit(score_surface, (50, 80))

        # Completion message
        if self.completed:
            if self.found_critical:
                message = "Critical notice found! Healthcare crisis ahead..."
                color = self.RED
            else:
                message = "Try again - you missed something important!"
                color = self.BLACK

            message_surface = self.font_large.render(message, True, color)
            message_rect = message_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 650))

            # Background for message
            bg_rect = message_rect.copy()
            bg_rect.inflate(20, 10)
            pygame.draw.rect(screen, self.WHITE, bg_rect)
            pygame.draw.rect(screen, color, bg_rect, 2)

            screen.blit(message_surface, message_rect)

    def start(self):
        """Start the mailbox sorting game"""
        self.active = True
        self.completed = False
        self.current_mail = 0
        self.dragging = False
        self.score = 0
        self.mistakes = 0
        self.found_critical = False

        # Reset mail position
        self.mail_rect.x = 500
        self.mail_rect.y = 200

        # Reshuffle mail
        random.shuffle(self.mail_items)

    def stop(self):
        """Stop the mailbox sorting game"""
        self.active = False
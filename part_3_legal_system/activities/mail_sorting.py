"""
Mail Sorting Mini-Game for Legal System Part
Drag and drop mail into trash or important pile
"""
import pygame
import random

class MailSortingGame:
    """Sort through scattered mail - yellow envelopes to trash, important to desk"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Mail pieces
        self.mail_pieces = []
        self.create_mail_pieces()

        # Zones
        self.trash_zone = pygame.Rect(100, 500, 200, 150)
        self.desk_zone = pygame.Rect(980, 500, 200, 150)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Sorting progress
        self.correctly_sorted = 0
        self.total_important = 5

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0

        # Found court notice
        self.found_court_notice = False

    def create_mail_pieces(self):
        """Create various mail pieces scattered on floor"""
        mail_types = [
            {'type': 'junk', 'color': (255, 230, 100), 'label': 'SALE!'},
            {'type': 'junk', 'color': (255, 230, 100), 'label': 'COUPON'},
            {'type': 'junk', 'color': (255, 230, 100), 'label': 'AD'},
            {'type': 'junk', 'color': (255, 230, 100), 'label': 'PROMO'},
            {'type': 'junk', 'color': (255, 200, 80), 'label': 'OFFER'},
            {'type': 'important', 'color': (255, 255, 255), 'label': 'COURT'},
            {'type': 'important', 'color': (255, 255, 255), 'label': 'BILL'},
            {'type': 'important', 'color': (255, 255, 255), 'label': 'NOTICE'},
            {'type': 'important', 'color': (200, 200, 255), 'label': 'GOV'},
            {'type': 'important', 'color': (255, 255, 255), 'label': 'URGENT'},
        ]

        # Shuffle and place mail
        random.shuffle(mail_types)

        for i, mail in enumerate(mail_types):
            x = random.randint(300, 900)
            y = random.randint(100, 400)

            mail_piece = {
                'rect': pygame.Rect(x, y, 120, 80),
                'type': mail['type'],
                'color': mail['color'],
                'label': mail['label'],
                'sorted': False
            }

            # The COURT letter is special
            if mail['label'] == 'COURT':
                mail_piece['is_court_notice'] = True

            self.mail_pieces.append(mail_piece)

    def start(self):
        """Start the activity"""
        self.active = True
        self.instruction_timer = pygame.time.get_ticks()

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        # Hide instructions after 3 seconds
        if self.show_instructions:
            if pygame.time.get_ticks() - self.instruction_timer > 3000:
                self.show_instructions = False

        # Check completion
        important_sorted = sum(1 for m in self.mail_pieces
                              if m['type'] == 'important' and m['sorted'])

        if important_sorted >= self.total_important:
            self.completed = True
            self.active = False

    def handle_mouse_down(self, pos):
        """Start dragging mail"""
        for mail in reversed(self.mail_pieces):  # Check top pieces first
            if not mail['sorted'] and mail['rect'].collidepoint(pos):
                self.dragging = mail
                self.drag_offset = (
                    mail['rect'].x - pos[0],
                    mail['rect'].y - pos[1]
                )
                break

    def handle_mouse_up(self, pos):
        """Drop mail and check if sorted correctly"""
        if not self.dragging:
            return

        # Check if dropped in trash zone
        if self.trash_zone.collidepoint(pos):
            if self.dragging['type'] == 'junk':
                self.dragging['sorted'] = True
                self.dragging['rect'].x = -200  # Move off screen
            else:
                # Wrong zone - bounce back
                self.dragging['rect'].x = random.randint(300, 900)
                self.dragging['rect'].y = random.randint(100, 400)

        # Check if dropped in desk zone
        elif self.desk_zone.collidepoint(pos):
            if self.dragging['type'] == 'important':
                self.dragging['sorted'] = True
                self.dragging['rect'].x = -200  # Move off screen
                self.correctly_sorted += 1

                # Check if this was the court notice
                if self.dragging.get('is_court_notice'):
                    self.found_court_notice = True
            else:
                # Wrong zone - bounce back
                self.dragging['rect'].x = random.randint(300, 900)
                self.dragging['rect'].y = random.randint(100, 400)

        self.dragging = None

    def handle_mouse_motion(self, pos):
        """Move dragged mail with mouse"""
        if self.dragging:
            self.dragging['rect'].x = pos[0] + self.drag_offset[0]
            self.dragging['rect'].y = pos[1] + self.drag_offset[1]

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)

    def draw(self, screen):
        """Draw the activity"""
        # Background
        screen.fill((50, 40, 30))

        # Draw floor texture
        for y in range(0, self.SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, (40, 30, 20), (0, y), (self.SCREEN_WIDTH, y))

        # Draw zones
        # Trash zone
        pygame.draw.rect(screen, (80, 60, 40), self.trash_zone)
        pygame.draw.rect(screen, (60, 40, 20), self.trash_zone, 3)

        font = pygame.font.Font(None, 36)
        trash_text = font.render("TRASH", True, (200, 200, 200))
        trash_rect = trash_text.get_rect(center=self.trash_zone.center)
        screen.blit(trash_text, trash_rect)

        # Desk zone
        pygame.draw.rect(screen, (100, 80, 60), self.desk_zone)
        pygame.draw.rect(screen, (80, 60, 40), self.desk_zone, 3)

        desk_text = font.render("IMPORTANT", True, (200, 200, 200))
        desk_rect = desk_text.get_rect(center=self.desk_zone.center)
        screen.blit(desk_text, desk_rect)

        # Draw mail pieces
        for mail in self.mail_pieces:
            if not mail['sorted']:
                # Shadow
                shadow_rect = mail['rect'].copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(screen, (20, 20, 20), shadow_rect)

                # Envelope
                pygame.draw.rect(screen, mail['color'], mail['rect'])
                pygame.draw.rect(screen, (100, 100, 100), mail['rect'], 2)

                # Label
                label_font = pygame.font.Font(None, 24)
                label_text = label_font.render(mail['label'], True, (50, 50, 50))
                label_rect = label_text.get_rect(center=mail['rect'].center)
                screen.blit(label_text, label_rect)

        # Draw instructions
        if self.show_instructions:
            inst_font = pygame.font.Font(None, 48)
            inst_text = inst_font.render("Sort the mail: Yellow to TRASH, White to IMPORTANT", True, (255, 255, 255))
            inst_rect = inst_text.get_rect(center=(self.SCREEN_WIDTH // 2, 50))

            # Background for text
            padding = 20
            bg_rect = inst_rect.inflate(padding * 2, padding)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)

            screen.blit(inst_text, inst_rect)

        # Draw progress
        progress_font = pygame.font.Font(None, 32)
        progress_text = progress_font.render(
            f"Important Mail Found: {self.correctly_sorted}/{self.total_important}",
            True, (255, 255, 255)
        )
        progress_rect = progress_text.get_rect(topright=(self.SCREEN_WIDTH - 20, 20))
        screen.blit(progress_text, progress_rect)

        # Special notice if court letter found
        if self.found_court_notice:
            notice_font = pygame.font.Font(None, 40)
            notice_text = notice_font.render("! COURT SUMMONS FOUND !", True, (255, 100, 100))
            notice_rect = notice_text.get_rect(center=(self.SCREEN_WIDTH // 2, 680))
            screen.blit(notice_text, notice_rect)

    def get_results(self):
        """Return results of the activity"""
        return {
            'court_notice_found': self.found_court_notice,
            'mail_sorted': self.correctly_sorted
        }
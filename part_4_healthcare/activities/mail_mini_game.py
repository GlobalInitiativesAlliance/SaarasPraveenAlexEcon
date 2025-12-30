"""
Healthcare Mail Sorting Mini-Game
Drag and drop mail into Important or Junk piles
Reveals Medi-Cal termination notice
"""
import pygame
import random

class HealthcareMailGame:
    """Sort mail to find the Medi-Cal termination notice"""

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
        self.junk_zone = pygame.Rect(100, 500, 250, 150)
        self.important_zone = pygame.Rect(930, 500, 250, 150)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Sorting progress
        self.correctly_sorted = 0
        self.total_to_sort = 8
        self.found_medicaid_notice = False

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0

        # Special notice reveal
        self.reveal_timer = 0
        self.showing_notice = False

    def create_mail_pieces(self):
        """Create various mail pieces including the Medi-Cal notice"""
        mail_types = [
            {'type': 'junk', 'color': (255, 230, 100), 'label': 'PIZZA DEAL!'},
            {'type': 'junk', 'color': (255, 230, 100), 'label': '50% OFF'},
            {'type': 'junk', 'color': (255, 200, 80), 'label': 'CREDIT CARD'},
            {'type': 'junk', 'color': (255, 230, 100), 'label': 'BUY NOW'},
            {'type': 'important', 'color': (200, 200, 255), 'label': 'BANK STMT'},
            {'type': 'important', 'color': (255, 200, 200), 'label': 'RENT DUE'},
            {'type': 'important', 'color': (200, 255, 200), 'label': 'TLP NOTICE'},
            {'type': 'medicaid', 'color': (255, 100, 100), 'label': 'MEDI-CAL'},
        ]

        # Shuffle positions
        positions = []
        for i in range(8):
            x = 300 + (i % 4) * 180
            y = 200 + (i // 4) * 120
            positions.append((x, y))
        random.shuffle(positions)

        # Create mail pieces
        for i, mail_data in enumerate(mail_types):
            rect = pygame.Rect(positions[i][0], positions[i][1], 140, 80)
            self.mail_pieces.append({
                'rect': rect,
                'type': mail_data['type'],
                'color': mail_data['color'],
                'label': mail_data['label'],
                'sorted': False,
                'original_pos': (rect.x, rect.y)
            })

    def handle_event(self, event):
        """Handle mouse events for dragging mail"""
        if not self.active or self.showing_notice:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for mail in self.mail_pieces:
                    if not mail['sorted'] and mail['rect'].collidepoint(mouse_pos):
                        self.dragging = mail
                        self.drag_offset = (
                            mail['rect'].x - mouse_pos[0],
                            mail['rect'].y - mouse_pos[1]
                        )
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                # Check if dropped in a zone
                if self.dragging['type'] == 'junk' and self.junk_zone.colliderect(self.dragging['rect']):
                    self.dragging['sorted'] = True
                    self.correctly_sorted += 1
                    self.dragging['rect'].center = self.junk_zone.center
                elif self.dragging['type'] in ['important', 'medicaid'] and self.important_zone.colliderect(self.dragging['rect']):
                    self.dragging['sorted'] = True
                    self.correctly_sorted += 1
                    self.dragging['rect'].center = self.important_zone.center

                    # Found the Medi-Cal notice
                    if self.dragging['type'] == 'medicaid':
                        self.found_medicaid_notice = True
                        self.reveal_timer = 120  # 2 seconds at 60 FPS
                else:
                    # Return to original position if dropped incorrectly
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

        return True

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update instruction timer
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 3:
                self.show_instructions = False

        # Check for completion
        if self.correctly_sorted >= self.total_to_sort and not self.completed:
            if self.found_medicaid_notice:
                if self.reveal_timer > 0:
                    self.reveal_timer -= 1
                    if self.reveal_timer <= 60:
                        self.showing_notice = True
                    if self.reveal_timer == 0:
                        self.completed = True
                        # Activity completion is handled by interior callback
                        # Don't call objective_manager directly here

    def render(self, screen):
        """Render the mail sorting game"""
        if not self.active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))

        # Draw zones
        pygame.draw.rect(screen, (100, 50, 50), self.junk_zone, 3)
        pygame.draw.rect(screen, (50, 100, 50), self.important_zone, 3)

        # Zone labels
        font = pygame.font.Font(None, 36)
        junk_text = font.render("JUNK", True, (150, 100, 100))
        important_text = font.render("IMPORTANT", True, (100, 150, 100))
        screen.blit(junk_text, (self.junk_zone.centerx - junk_text.get_width()//2, self.junk_zone.centery - 20))
        screen.blit(important_text, (self.important_zone.centerx - important_text.get_width()//2, self.important_zone.centery - 20))

        # Draw mail pieces
        for mail in self.mail_pieces:
            if not mail['sorted'] or self.dragging == mail:
                # Shadow effect if dragging
                if self.dragging == mail:
                    shadow_rect = mail['rect'].copy()
                    shadow_rect.x += 5
                    shadow_rect.y += 5
                    pygame.draw.rect(screen, (10, 10, 10), shadow_rect)

                # Mail piece
                pygame.draw.rect(screen, mail['color'], mail['rect'])
                pygame.draw.rect(screen, (50, 50, 50), mail['rect'], 2)

                # Label
                small_font = pygame.font.Font(None, 20)
                label_text = small_font.render(mail['label'], True, (30, 30, 30))
                label_x = mail['rect'].centerx - label_text.get_width()//2
                label_y = mail['rect'].centery - label_text.get_height()//2
                screen.blit(label_text, (label_x, label_y))

        # Instructions
        if self.show_instructions:
            inst_text = font.render("Drag mail to JUNK or IMPORTANT pile", True, (255, 255, 255))
            screen.blit(inst_text, (self.SCREEN_WIDTH//2 - inst_text.get_width()//2, 100))

        # Progress counter
        progress_text = font.render(f"Sorted: {self.correctly_sorted}/{self.total_to_sort}", True, (200, 200, 200))
        screen.blit(progress_text, (self.SCREEN_WIDTH//2 - progress_text.get_width()//2, 50))

        # ESC hint
        esc_font = pygame.font.Font(None, 24)
        esc_text = esc_font.render("Press ESC to exit", True, (150, 150, 150))
        screen.blit(esc_text, (20, self.SCREEN_HEIGHT - 40))

        # Show Medi-Cal notice if found
        if self.showing_notice:
            notice_rect = pygame.Rect(self.SCREEN_WIDTH//2 - 300, self.SCREEN_HEIGHT//2 - 150, 600, 300)
            pygame.draw.rect(screen, (255, 100, 100), notice_rect)
            pygame.draw.rect(screen, (50, 50, 50), notice_rect, 3)

            title_font = pygame.font.Font(None, 48)
            title_text = title_font.render("NOTICE OF TERMINATION", True, (255, 255, 255))
            screen.blit(title_text, (notice_rect.centerx - title_text.get_width()//2, notice_rect.y + 30))

            content_font = pygame.font.Font(None, 28)
            lines = [
                "Your Medi-Cal coverage has ended",
                "due to age eligibility (21 years).",
                "",
                "You may reapply under the",
                "Former Foster Youth program.",
                "",
                "Visit your local clinic for assistance."
            ]

            y_offset = 100
            for line in lines:
                line_text = content_font.render(line, True, (255, 255, 255))
                screen.blit(line_text, (notice_rect.centerx - line_text.get_width()//2, notice_rect.y + y_offset))
                y_offset += 30

    def start(self):
        """Start the mini-game"""
        self.active = True
        self.completed = False
        self.show_instructions = True
        self.instruction_timer = 0

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Draw method (alias for render) - standard interface"""
        self.render(screen)

    def handle_key(self, key):
        """Handle keyboard input - ESC to exit"""
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False
"""
Document Sorting Mini-Game
Sort documents into Required vs Optional piles
Always marked incomplete to show systemic barriers
"""
import pygame
import random

class DocumentSortingGame:
    """Sort documents but always fail - systemic barrier demonstration"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 45.0  # seconds
        self.time_remaining = self.time_limit

        # Documents to sort
        self.documents = [
            {'name': 'Birth Certificate', 'type': 'required', 'placed': False},
            {'name': 'Social Security Card', 'type': 'required', 'placed': False},
            {'name': 'Proof of Income', 'type': 'required', 'placed': False},
            {'name': 'Photo ID', 'type': 'required', 'placed': False},
            {'name': 'Address Verification', 'type': 'required', 'placed': False},
            {'name': 'Bank Statements', 'type': 'optional', 'placed': False},
            {'name': 'Medical Records', 'type': 'optional', 'placed': False},
            {'name': 'Employment Letter', 'type': 'optional', 'placed': False},
            {'name': 'Reference Letters', 'type': 'optional', 'placed': False},
            {'name': 'Foster Care Verification', 'type': 'required', 'placed': False},
        ]

        # Sorting bins
        self.required_bin = pygame.Rect(200, 400, 300, 200)
        self.optional_bin = pygame.Rect(780, 400, 300, 200)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Scoring (but it doesn't matter)
        self.correctly_sorted = 0
        self.total_documents = len(self.documents)

        # Result state
        self.show_result = False
        self.result_timer = 0
        self.stamp_animation = 0

        # Create document rectangles
        self.create_document_rects()

    def create_document_rects(self):
        """Create draggable document cards"""
        start_x = 300
        start_y = 120

        for i, doc in enumerate(self.documents):
            x = start_x + (i % 5) * 140
            y = start_y + (i // 5) * 80
            doc['rect'] = pygame.Rect(x, y, 120, 60)
            doc['original_pos'] = (x, y)

    def handle_event(self, event):
        """Handle document dragging"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for doc in self.documents:
                if not doc['placed'] and doc['rect'].collidepoint(mouse_pos):
                    self.dragging = doc
                    self.drag_offset = (
                        doc['rect'].x - mouse_pos[0],
                        doc['rect'].y - mouse_pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check which bin it was dropped in
                if self.required_bin.colliderect(self.dragging['rect']):
                    self.dragging['placed'] = True
                    self.dragging['placed_in'] = 'required'
                    if self.dragging['type'] == 'required':
                        self.correctly_sorted += 1
                elif self.optional_bin.colliderect(self.dragging['rect']):
                    self.dragging['placed'] = True
                    self.dragging['placed_in'] = 'optional'
                    if self.dragging['type'] == 'optional':
                        self.correctly_sorted += 1
                else:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Check if all sorted
                if all(doc['placed'] for doc in self.documents):
                    self.trigger_result()

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

        return True

    def trigger_result(self):
        """Show the unfair result"""
        self.show_result = True
        self.result_timer = 180  # 3 seconds
        self.stamp_animation = 0

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        if not self.show_result:
            # Update timer
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.trigger_result()

        else:
            # Update result display
            self.result_timer -= 1
            self.stamp_animation = min(100, self.stamp_animation + 5)

            if self.result_timer <= 0:
                self.completed = True
                if self.objective_manager:
                    self.objective_manager.complete_objective("document_sorting")

    def render(self, screen):
        """Render the document sorting interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(245)
        overlay.fill((240, 240, 245))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Social Services - Document Sorting", True, (30, 30, 40))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

        # Timer
        timer_font = pygame.font.Font(None, 32)
        timer_color = (255, 100, 100) if self.time_remaining < 10 else (100, 100, 110)
        timer_text = timer_font.render(f"Time: {int(self.time_remaining)}s", True, timer_color)
        screen.blit(timer_text, (self.SCREEN_WIDTH - 150, 40))

        if not self.show_result:
            # Instructions
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Sort documents into Required or Optional bins", True, (80, 80, 90))
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 70))

            # Sorting bins
            # Required bin
            pygame.draw.rect(screen, (200, 200, 255), self.required_bin)
            pygame.draw.rect(screen, (100, 100, 150), self.required_bin, 3)
            bin_font = pygame.font.Font(None, 36)
            req_text = bin_font.render("REQUIRED", True, (50, 50, 100))
            req_x = self.required_bin.centerx - req_text.get_width() // 2
            screen.blit(req_text, (req_x, self.required_bin.y + 20))

            # Optional bin
            pygame.draw.rect(screen, (200, 255, 200), self.optional_bin)
            pygame.draw.rect(screen, (100, 150, 100), self.optional_bin, 3)
            opt_text = bin_font.render("OPTIONAL", True, (50, 100, 50))
            opt_x = self.optional_bin.centerx - opt_text.get_width() // 2
            screen.blit(opt_text, (opt_x, self.optional_bin.y + 20))

            # Documents
            doc_font = pygame.font.Font(None, 18)
            for doc in self.documents:
                if not doc['placed']:
                    # Document card
                    color = (255, 255, 255)
                    if self.dragging == doc:
                        color = (230, 230, 255)

                    pygame.draw.rect(screen, color, doc['rect'])
                    pygame.draw.rect(screen, (150, 150, 160), doc['rect'], 2)

                    # Document name
                    # Split long names
                    words = doc['name'].split()
                    y_offset = 15
                    for word in words:
                        text = doc_font.render(word, True, (30, 30, 40))
                        text_x = doc['rect'].centerx - text.get_width() // 2
                        screen.blit(text, (text_x, doc['rect'].y + y_offset))
                        y_offset += 18

            # Show placed documents count
            count_font = pygame.font.Font(None, 24)
            placed_count = sum(1 for d in self.documents if d['placed'])
            count_text = count_font.render(
                f"Sorted: {placed_count}/{self.total_documents}",
                True, (100, 100, 110)
            )
            screen.blit(count_text, (self.SCREEN_WIDTH // 2 - count_text.get_width() // 2, 630))

        else:
            # Show unfair result
            self.render_result(screen)

    def render_result(self, screen):
        """Render the always-incomplete result"""
        # Result panel
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 350, 200, 700, 300)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect)
        pygame.draw.rect(screen, (200, 50, 50), panel_rect, 4)

        # Perfect score text (but it doesn't matter)
        score_font = pygame.font.Font(None, 28)
        score_text = f"You correctly sorted {self.correctly_sorted}/{self.total_documents} documents"
        score_surface = score_font.render(score_text, True, (50, 150, 50))
        score_x = panel_rect.centerx - score_surface.get_width() // 2
        screen.blit(score_surface, (score_x, panel_rect.y + 50))

        # But...
        but_font = pygame.font.Font(None, 32)
        but_text = "BUT..."
        but_surface = but_font.render(but_text, True, (150, 50, 50))
        but_x = panel_rect.centerx - but_surface.get_width() // 2
        screen.blit(but_surface, (but_x, panel_rect.y + 100))

        # INCOMPLETE stamp with animation
        if self.stamp_animation > 50:
            stamp_font = pygame.font.Font(None, 72)
            stamp_text = "INCOMPLETE"
            stamp_surface = stamp_font.render(stamp_text, True, (255, 50, 50))

            # Rotate stamp slightly
            angle = -15
            rotated_stamp = pygame.transform.rotate(stamp_surface, angle)

            stamp_x = panel_rect.centerx - rotated_stamp.get_width() // 2
            stamp_y = panel_rect.y + 140
            screen.blit(rotated_stamp, (stamp_x, stamp_y))

            # Reason (arbitrary)
            reason_font = pygame.font.Font(None, 24)
            reasons = [
                "Missing Form 4B-7 (not mentioned anywhere)",
                "Signature on wrong line (line not marked)",
                "Used blue ink instead of black",
                "Document copy not notarized"
            ]
            reason = random.choice(reasons) if self.stamp_animation == 55 else reasons[0]
            reason_surface = reason_font.render(reason, True, (100, 50, 50))
            reason_x = panel_rect.centerx - reason_surface.get_width() // 2
            screen.blit(reason_surface, (reason_x, panel_rect.y + 230))

    def start(self):
        """Start the document sorting game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.time_remaining = self.time_limit
        self.correctly_sorted = 0
        self.result_timer = 0

        # Reset documents
        for doc in self.documents:
            doc['placed'] = False
            doc['rect'].x = doc['original_pos'][0]
            doc['rect'].y = doc['original_pos'][1]

    def stop(self):
        """Stop the mini-game"""
        self.active = False
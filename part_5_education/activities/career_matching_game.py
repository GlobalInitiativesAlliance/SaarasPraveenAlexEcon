"""
Career Matching Mini-Game
Match career fields with their training length
Counselor dialogue task
"""
import pygame

class CareerMatchingGame:
    """Drag careers to match with training duration categories"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Career items
        self.careers = [
            {'name': 'Electrician', 'correct_category': 'trade', 'placed': False},
            {'name': 'Nurse (RN)', 'correct_category': 'associate', 'placed': False},
            {'name': 'Software Engineer', 'correct_category': 'bachelor', 'placed': False},
            {'name': 'Dental Hygienist', 'correct_category': 'associate', 'placed': False},
            {'name': 'Plumber', 'correct_category': 'trade', 'placed': False},
            {'name': 'Teacher', 'correct_category': 'bachelor', 'placed': False},
            {'name': 'HVAC Technician', 'correct_category': 'trade', 'placed': False},
            {'name': 'Medical Assistant', 'correct_category': 'certificate', 'placed': False},
            {'name': 'Accountant', 'correct_category': 'bachelor', 'placed': False},
            {'name': 'Phlebotomist', 'correct_category': 'certificate', 'placed': False},
        ]

        # Training categories
        self.categories = [
            {'id': 'certificate', 'label': 'Certificate (6 months)', 'rect': None, 'careers': []},
            {'id': 'trade', 'label': 'Trade School (1-2 years)', 'rect': None, 'careers': []},
            {'id': 'associate', 'label': "Associate's (2 years)", 'rect': None, 'careers': []},
            {'id': 'bachelor', 'label': "Bachelor's (4 years)", 'rect': None, 'careers': []},
        ]

        # Create UI elements
        self.create_career_cards()
        self.create_category_zones()

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Scoring
        self.correct_placements = 0
        self.total_careers = len(self.careers)

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0

        # Counselor feedback
        self.show_feedback = False
        self.feedback_timer = 0

    def create_career_cards(self):
        """Create draggable career cards"""
        start_x = 100
        start_y = 150

        for i, career in enumerate(self.careers):
            x = start_x + (i % 2) * 200
            y = start_y + (i // 2) * 60
            career['rect'] = pygame.Rect(x, y, 180, 45)
            career['original_pos'] = (x, y)

    def create_category_zones(self):
        """Create drop zones for categories"""
        zone_width = 220
        zone_height = 200
        start_x = 500
        start_y = 150

        for i, category in enumerate(self.categories):
            x = start_x + (i % 2) * 250
            y = start_y + (i // 2) * 230
            category['rect'] = pygame.Rect(x, y, zone_width, zone_height)

    def handle_event(self, event):
        """Handle drag and drop interactions"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicking on a career card
            for career in self.careers:
                if not career['placed'] and career['rect'].collidepoint(mouse_pos):
                    self.dragging = career
                    self.drag_offset = (
                        career['rect'].x - mouse_pos[0],
                        career['rect'].y - mouse_pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in a category zone
                placed = False
                for category in self.categories:
                    if category['rect'].colliderect(self.dragging['rect']):
                        # Place in category
                        self.dragging['placed'] = True
                        self.dragging['placed_category'] = category['id']
                        category['careers'].append(self.dragging)

                        # Check if correct
                        if category['id'] == self.dragging['correct_category']:
                            self.correct_placements += 1

                        placed = True
                        break

                if not placed:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Check for completion
                if all(career['placed'] for career in self.careers):
                    self.show_feedback = True
                    self.feedback_timer = 180  # 3 seconds
                    self.completed = True

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
            if self.instruction_timer > 4:
                self.show_instructions = False

        # Update feedback timer
        if self.show_feedback and self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self.completed = True
                # Activity completion handled by interior callback

    def render(self, screen):
        """Render the career matching interface"""
        if not self.active:
            return

        # Background overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(245)
        overlay.fill((245, 245, 250))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Career Planning with Counselor", True, (30, 30, 40))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 40))

        # Category zones
        zone_font = pygame.font.Font(None, 24)
        for category in self.categories:
            # Draw zone
            pygame.draw.rect(screen, (240, 240, 250), category['rect'])
            pygame.draw.rect(screen, (150, 150, 160), category['rect'], 2)

            # Zone label
            label = zone_font.render(category['label'], True, (50, 50, 60))
            label_x = category['rect'].centerx - label.get_width() // 2
            label_y = category['rect'].y + 10
            screen.blit(label, (label_x, label_y))

            # Draw placed careers
            y_offset = 40
            small_font = pygame.font.Font(None, 20)
            for placed_career in category['careers']:
                color = (50, 150, 50) if placed_career['correct_category'] == category['id'] else (200, 50, 50)
                text = small_font.render(placed_career['name'], True, color)
                screen.blit(text, (category['rect'].x + 10, category['rect'].y + y_offset))
                y_offset += 25

        # Career cards (unplaced)
        card_font = pygame.font.Font(None, 22)
        for career in self.careers:
            if not career['placed']:
                # Card background
                if self.dragging == career:
                    bg_color = (200, 220, 255)
                    border_color = (100, 150, 255)
                else:
                    bg_color = (255, 255, 255)
                    border_color = (180, 180, 190)

                pygame.draw.rect(screen, bg_color, career['rect'])
                pygame.draw.rect(screen, border_color, career['rect'], 2)

                # Career name
                name_text = card_font.render(career['name'], True, (30, 30, 40))
                text_x = career['rect'].centerx - name_text.get_width() // 2
                text_y = career['rect'].centery - name_text.get_height() // 2
                screen.blit(name_text, (text_x, text_y))

        # Instructions
        if self.show_instructions:
            inst_font = pygame.font.Font(None, 28)
            inst_text = inst_font.render(
                "Drag careers to their correct training duration category",
                True, (100, 100, 120)
            )
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 90))

        # Feedback
        if self.show_feedback:
            feedback_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 300, self.SCREEN_HEIGHT // 2 - 100, 600, 200)
            pygame.draw.rect(screen, (255, 255, 255), feedback_rect)
            pygame.draw.rect(screen, (100, 100, 110), feedback_rect, 3)

            feedback_font = pygame.font.Font(None, 36)
            score_text = f"Score: {self.correct_placements}/{self.total_careers} correct"
            score_surface = feedback_font.render(score_text, True, (30, 30, 40))
            screen.blit(score_surface, (feedback_rect.centerx - score_surface.get_width() // 2, feedback_rect.y + 40))

            message_font = pygame.font.Font(None, 28)
            if self.correct_placements >= 8:
                message = "Excellent! You understand education pathways well."
                color = (50, 150, 50)
            elif self.correct_placements >= 6:
                message = "Good job! Consider exploring all your options."
                color = (150, 150, 50)
            else:
                message = "Let's review these career paths together."
                color = (200, 50, 50)

            msg_surface = message_font.render(message, True, color)
            screen.blit(msg_surface, (feedback_rect.centerx - msg_surface.get_width() // 2, feedback_rect.y + 100))

            # Trade school note
            trade_font = pygame.font.Font(None, 24)
            trade_text = "A trade school tour has been added to your map!"
            trade_surface = trade_font.render(trade_text, True, (100, 100, 200))
            screen.blit(trade_surface, (feedback_rect.centerx - trade_surface.get_width() // 2, feedback_rect.y + 140))

    def start(self):
        """Start the career matching game"""
        self.active = True
        self.completed = False
        self.show_instructions = True
        self.instruction_timer = 0
        self.show_feedback = False
        self.feedback_timer = 0
        self.correct_placements = 0

        # Reset careers
        for career in self.careers:
            career['placed'] = False
            career['rect'].x = career['original_pos'][0]
            career['rect'].y = career['original_pos'][1]

        # Clear categories
        for category in self.categories:
            category['careers'] = []

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False
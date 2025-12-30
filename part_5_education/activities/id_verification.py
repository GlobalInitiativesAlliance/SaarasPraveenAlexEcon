"""
ID Verification Mini-Game
Match ID and foster verification documents to correct forms
Library laptop request process
"""
import pygame

class IDVerificationGame:
    """Match documents to correct form fields for laptop request"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Documents
        self.documents = [
            {'type': 'id', 'name': 'State ID', 'icon': 'ID', 'placed': False},
            {'type': 'foster', 'name': 'Foster Care Letter', 'icon': 'FCL', 'placed': False},
            {'type': 'address', 'name': 'Proof of Address', 'icon': 'ADDR', 'placed': False},
            {'type': 'income', 'name': 'Income Statement', 'icon': 'INC', 'placed': False},
        ]

        # Form requirements
        self.form_slots = [
            {'label': 'Photo ID Required', 'accepts': 'id', 'filled': None, 'required': True},
            {'label': 'Foster Youth Verification', 'accepts': 'foster', 'filled': None, 'required': True},
            {'label': 'Current Address Proof', 'accepts': 'address', 'filled': None, 'required': False},
        ]

        # Create UI elements
        self.create_document_cards()
        self.create_form_slots()

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Result state
        self.verification_complete = False
        self.show_result = False
        self.laptop_available = False  # Will be out of stock

        # Submit button
        self.submit_button = pygame.Rect(540, 500, 200, 50)

    def create_document_cards(self):
        """Create draggable document cards"""
        start_x = 150
        start_y = 200

        for i, doc in enumerate(self.documents):
            x = start_x
            y = start_y + (i * 80)
            doc['rect'] = pygame.Rect(x, y, 150, 60)
            doc['original_pos'] = (x, y)

    def create_form_slots(self):
        """Create form slot areas"""
        start_x = 500
        start_y = 200

        for i, slot in enumerate(self.form_slots):
            slot['rect'] = pygame.Rect(start_x, start_y + (i * 100), 400, 70)

    def handle_event(self, event):
        """Handle document dragging and placement"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check submit button
            if self.submit_button.collidepoint(mouse_pos) and not self.show_result:
                self.check_verification()
                return True

            # Check document dragging
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
                # Check if dropped on a form slot
                placed = False
                for slot in self.form_slots:
                    if slot['rect'].colliderect(self.dragging['rect']):
                        # Check if slot already filled
                        if slot['filled']:
                            # Return previous document
                            slot['filled']['placed'] = False
                            slot['filled']['rect'].x = slot['filled']['original_pos'][0]
                            slot['filled']['rect'].y = slot['filled']['original_pos'][1]

                        # Place document
                        slot['filled'] = self.dragging
                        self.dragging['placed'] = True
                        self.dragging['rect'].center = slot['rect'].center
                        placed = True
                        break

                if not placed:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]
                    self.dragging['placed'] = False

                self.dragging = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

        return True

    def check_verification(self):
        """Check if documents are correctly placed"""
        correct = True

        for slot in self.form_slots:
            if slot['required']:
                if not slot['filled'] or slot['filled']['type'] != slot['accepts']:
                    correct = False
                    break

        self.verification_complete = correct
        self.show_result = True
        self.laptop_available = False  # Always out of stock for narrative

        # Complete after showing result
        self.completed = True
        # Activity completion handled by interior callback

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

    def render(self, screen):
        """Render the ID verification interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(245)
        overlay.fill((250, 250, 255))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Library Laptop Request - Document Verification", True, (30, 30, 40))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst_text = inst_font.render("Drag the correct documents to the form requirements", True, (80, 80, 100))
        screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 100))

        # Form slots
        slot_font = pygame.font.Font(None, 26)
        for slot in self.form_slots:
            # Slot background
            if slot['filled'] and slot['filled']['type'] == slot['accepts']:
                bg_color = (200, 255, 200)
            elif slot['filled']:
                bg_color = (255, 200, 200)
            else:
                bg_color = (255, 255, 255)

            pygame.draw.rect(screen, bg_color, slot['rect'])
            pygame.draw.rect(screen, (100, 100, 110), slot['rect'], 2)

            # Slot label
            label = slot['label']
            if slot['required']:
                label += " *"
            label_text = slot_font.render(label, True, (50, 50, 60))
            screen.blit(label_text, (slot['rect'].x + 10, slot['rect'].y - 25))

        # Document cards
        card_font = pygame.font.Font(None, 22)
        icon_font = pygame.font.Font(None, 28)

        for doc in self.documents:
            if not doc['placed'] or self.dragging == doc:
                # Card background
                if self.dragging == doc:
                    bg_color = (200, 220, 255)
                    border_color = (100, 150, 255)
                else:
                    bg_color = (255, 255, 255)
                    border_color = (150, 150, 160)

                pygame.draw.rect(screen, bg_color, doc['rect'])
                pygame.draw.rect(screen, border_color, doc['rect'], 2)

                # Document icon
                icon_text = icon_font.render(doc['icon'], True, (100, 100, 150))
                icon_x = doc['rect'].x + 10
                icon_y = doc['rect'].centery - icon_text.get_height() // 2
                screen.blit(icon_text, (icon_x, icon_y))

                # Document name
                name_text = card_font.render(doc['name'], True, (30, 30, 40))
                name_x = doc['rect'].x + 60
                name_y = doc['rect'].centery - name_text.get_height() // 2
                screen.blit(name_text, (name_x, name_y))

        # Submit button
        if not self.show_result:
            mouse_pos = pygame.mouse.get_pos()
            btn_color = (100, 150, 200) if self.submit_button.collidepoint(mouse_pos) else (80, 130, 180)
            pygame.draw.rect(screen, btn_color, self.submit_button)
            pygame.draw.rect(screen, (60, 90, 120), self.submit_button, 2)

            btn_text = slot_font.render("Submit Request", True, (255, 255, 255))
            btn_x = self.submit_button.centerx - btn_text.get_width() // 2
            btn_y = self.submit_button.centery - btn_text.get_height() // 2
            screen.blit(btn_text, (btn_x, btn_y))

        # Result message
        if self.show_result:
            result_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 300, self.SCREEN_HEIGHT // 2 - 100, 600, 250)

            if self.verification_complete:
                # Documents correct but laptop unavailable
                pygame.draw.rect(screen, (255, 250, 200), result_rect)
                pygame.draw.rect(screen, (200, 180, 100), result_rect, 3)

                result_font = pygame.font.Font(None, 36)
                result_text = result_font.render("Documents Verified!", True, (50, 100, 50))
                screen.blit(result_text, (result_rect.centerx - result_text.get_width() // 2, result_rect.y + 30))

                msg_font = pygame.font.Font(None, 28)
                messages = [
                    "Your documents are in order.",
                    "Unfortunately, all laptops are currently",
                    "checked out.",
                    "",
                    "You're scheduled for pickup next week.",
                    "We'll notify you when one is available."
                ]

                y = result_rect.y + 80
                for msg in messages:
                    if msg:
                        msg_surface = msg_font.render(msg, True, (80, 80, 90))
                        screen.blit(msg_surface, (result_rect.centerx - msg_surface.get_width() // 2, y))
                    y += 30
            else:
                # Incorrect documents
                pygame.draw.rect(screen, (255, 200, 200), result_rect)
                pygame.draw.rect(screen, (200, 100, 100), result_rect, 3)

                result_font = pygame.font.Font(None, 36)
                result_text = result_font.render("Incorrect Documents", True, (150, 50, 50))
                screen.blit(result_text, (result_rect.centerx - result_text.get_width() // 2, result_rect.y + 50))

                msg_font = pygame.font.Font(None, 28)
                msg = "Please provide the correct documents."
                msg_surface = msg_font.render(msg, True, (100, 50, 50))
                screen.blit(msg_surface, (result_rect.centerx - msg_surface.get_width() // 2, result_rect.y + 120))

    def start(self):
        """Start the ID verification game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.verification_complete = False

        # Reset documents
        for doc in self.documents:
            doc['placed'] = False
            doc['rect'].x = doc['original_pos'][0]
            doc['rect'].y = doc['original_pos'][1]

        # Reset form slots
        for slot in self.form_slots:
            slot['filled'] = None

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False
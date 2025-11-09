"""
Medication Selection Mini-Game
Find a generic medication that meets both affordability and dosage requirements
"""
import pygame
import random

class MedicationSelectionGame:
    """Select affordable generic medication at pharmacy"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Budget constraint
        self.budget = 40.00
        self.selected_medication = None

        # Medications with prices and dosages
        self.medications = [
            {
                'name': 'SertraGen',
                'generic': True,
                'price': 35.99,
                'dosage': '50mg',
                'doses_per_month': 30,
                'description': 'Generic antidepressant'
            },
            {
                'name': 'Zoloft',
                'generic': False,
                'price': 127.50,
                'dosage': '50mg',
                'doses_per_month': 30,
                'description': 'Brand name antidepressant'
            },
            {
                'name': 'FluxoCap',
                'generic': True,
                'price': 28.75,
                'dosage': '20mg',
                'doses_per_month': 30,
                'description': 'Generic - different compound'
            },
            {
                'name': 'MoodBalance Plus',
                'generic': False,
                'price': 89.99,
                'dosage': '25mg',
                'doses_per_month': 60,
                'description': 'Extended release brand'
            },
            {
                'name': 'GenericMood',
                'generic': True,
                'price': 42.00,
                'dosage': '75mg',
                'doses_per_month': 30,
                'description': 'Higher dose generic'
            },
            {
                'name': 'CalmRx Basic',
                'generic': True,
                'price': 31.50,
                'dosage': '50mg',
                'doses_per_month': 30,
                'description': 'Affordable generic option'
            }
        ]

        # Correct choice (CalmRx Basic - meets budget and dosage)
        self.correct_medication = self.medications[5]

        # UI elements
        self.medication_cards = []
        self.create_medication_cards()
        self.confirm_button = pygame.Rect(540, 620, 200, 50)

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0

        # Result display
        self.show_result = False
        self.purchase_successful = False

    def create_medication_cards(self):
        """Create clickable medication cards"""
        self.medication_cards = []

        # Arrange in 3 columns, 2 rows
        for i, med in enumerate(self.medications):
            col = i % 3
            row = i // 3

            x = 240 + col * 280
            y = 200 + row * 180

            card = pygame.Rect(x, y, 250, 160)
            self.medication_cards.append({
                'rect': card,
                'medication': med,
                'selected': False,
                'hover': False
            })

    def handle_event(self, event):
        """Handle medication selection"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEMOTION:
            # Update hover states
            for card in self.medication_cards:
                card['hover'] = card['rect'].collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check medication selection
            for card in self.medication_cards:
                if card['rect'].collidepoint(mouse_pos):
                    # Deselect all others
                    for c in self.medication_cards:
                        c['selected'] = False

                    card['selected'] = True
                    self.selected_medication = card['medication']
                    break

            # Check confirm button
            if self.confirm_button.collidepoint(mouse_pos) and self.selected_medication:
                self.process_purchase()

        return True

    def process_purchase(self):
        """Process the medication purchase"""
        self.show_result = True

        # Check if selection meets criteria
        if (self.selected_medication['generic'] and
            self.selected_medication['price'] <= self.budget and
            self.selected_medication['dosage'] == '50mg'):
            self.purchase_successful = True
        else:
            self.purchase_successful = False

        self.completed = True

        if self.purchase_successful and self.objective_manager:
            self.objective_manager.complete_objective("select_medication")

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update instruction timer
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 4:
                self.show_instructions = False

    def render(self, screen):
        """Render the medication selection interface"""
        if not self.active:
            return

        # Background overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(245)
        overlay.fill((245, 245, 250))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Pharmacy - Select Your Medication", True, (30, 30, 40))
        screen.blit(title_text, (self.SCREEN_WIDTH//2 - title_text.get_width()//2, 40))

        # Requirements
        req_font = pygame.font.Font(None, 28)
        requirements = [
            f"Budget: ${self.budget:.2f}",
            "Need: Generic version, 50mg dosage, 30-day supply"
        ]

        y_offset = 90
        for req in requirements:
            req_text = req_font.render(req, True, (60, 60, 70))
            screen.blit(req_text, (self.SCREEN_WIDTH//2 - req_text.get_width()//2, y_offset))
            y_offset += 30

        if not self.show_result:
            # Medication cards
            card_font = pygame.font.Font(None, 24)
            price_font = pygame.font.Font(None, 32)
            small_font = pygame.font.Font(None, 20)

            for card in self.medication_cards:
                med = card['medication']

                # Card background
                if card['selected']:
                    bg_color = (150, 200, 150)
                    border_color = (50, 150, 50)
                elif card['hover']:
                    bg_color = (230, 230, 240)
                    border_color = (100, 100, 120)
                else:
                    bg_color = (255, 255, 255)
                    border_color = (180, 180, 190)

                pygame.draw.rect(screen, bg_color, card['rect'])
                pygame.draw.rect(screen, border_color, card['rect'], 2)

                # Generic badge
                if med['generic']:
                    badge_rect = pygame.Rect(card['rect'].x + 5, card['rect'].y + 5, 60, 20)
                    pygame.draw.rect(screen, (100, 150, 255), badge_rect)
                    badge_text = small_font.render("GENERIC", True, (255, 255, 255))
                    screen.blit(badge_text, (badge_rect.x + 5, badge_rect.y + 2))

                # Medication name
                name_text = card_font.render(med['name'], True, (30, 30, 40))
                screen.blit(name_text, (card['rect'].x + 10, card['rect'].y + 35))

                # Price (large)
                price_color = (50, 150, 50) if med['price'] <= self.budget else (200, 50, 50)
                price_text = price_font.render(f"${med['price']:.2f}", True, price_color)
                screen.blit(price_text, (card['rect'].x + 10, card['rect'].y + 65))

                # Dosage info
                dosage_text = small_font.render(f"{med['dosage']} × {med['doses_per_month']} doses", True, (80, 80, 90))
                screen.blit(dosage_text, (card['rect'].x + 10, card['rect'].y + 100))

                # Description
                desc_text = small_font.render(med['description'], True, (100, 100, 110))
                screen.blit(desc_text, (card['rect'].x + 10, card['rect'].y + 125))

            # Confirm button
            if self.selected_medication:
                mouse_pos = pygame.mouse.get_pos()
                btn_color = (80, 140, 200) if self.confirm_button.collidepoint(mouse_pos) else (60, 120, 180)
                pygame.draw.rect(screen, btn_color, self.confirm_button)
                pygame.draw.rect(screen, (40, 80, 120), self.confirm_button, 2)

                btn_text = req_font.render("PURCHASE", True, (255, 255, 255))
                btn_x = self.confirm_button.centerx - btn_text.get_width()//2
                btn_y = self.confirm_button.centery - btn_text.get_height()//2
                screen.blit(btn_text, (btn_x, btn_y))

            # Instructions
            if self.show_instructions:
                inst_font = pygame.font.Font(None, 26)
                inst_text = inst_font.render(
                    "Click a medication that is generic, affordable, and the right dosage",
                    True, (100, 100, 120)
                )
                screen.blit(inst_text, (self.SCREEN_WIDTH//2 - inst_text.get_width()//2, 570))

        else:
            # Show result
            result_rect = pygame.Rect(self.SCREEN_WIDTH//2 - 300, self.SCREEN_HEIGHT//2 - 150, 600, 300)

            if self.purchase_successful:
                pygame.draw.rect(screen, (100, 200, 100), result_rect)
                pygame.draw.rect(screen, (50, 150, 50), result_rect, 3)

                result_font = pygame.font.Font(None, 48)
                result_text = result_font.render("Purchase Successful!", True, (255, 255, 255))
                screen.blit(result_text, (self.SCREEN_WIDTH//2 - result_text.get_width()//2, result_rect.y + 50))

                detail_font = pygame.font.Font(None, 28)
                details = [
                    f"You bought: {self.selected_medication['name']}",
                    f"Price: ${self.selected_medication['price']:.2f}",
                    f"Change: ${self.budget - self.selected_medication['price']:.2f}",
                    "",
                    "You have your medication for the month!"
                ]

                y = result_rect.y + 110
                for detail in details:
                    if detail:
                        detail_text = detail_font.render(detail, True, (255, 255, 255))
                        screen.blit(detail_text, (self.SCREEN_WIDTH//2 - detail_text.get_width()//2, y))
                    y += 30

            else:
                pygame.draw.rect(screen, (200, 100, 100), result_rect)
                pygame.draw.rect(screen, (150, 50, 50), result_rect, 3)

                result_font = pygame.font.Font(None, 48)
                result_text = result_font.render("Wrong Choice!", True, (255, 255, 255))
                screen.blit(result_text, (self.SCREEN_WIDTH//2 - result_text.get_width()//2, result_rect.y + 50))

                detail_font = pygame.font.Font(None, 28)
                reason = ""
                if not self.selected_medication['generic']:
                    reason = "This is a brand name, not generic!"
                elif self.selected_medication['price'] > self.budget:
                    reason = f"Too expensive! You only have ${self.budget:.2f}"
                elif self.selected_medication['dosage'] != '50mg':
                    reason = "Wrong dosage! You need 50mg"

                details = [
                    f"You selected: {self.selected_medication['name']}",
                    reason,
                    "",
                    "You'll have to manage without medication",
                    "until your insurance is restored."
                ]

                y = result_rect.y + 110
                for detail in details:
                    if detail:
                        detail_text = detail_font.render(detail, True, (255, 255, 255))
                        screen.blit(detail_text, (self.SCREEN_WIDTH//2 - detail_text.get_width()//2, y))
                    y += 30

    def start(self):
        """Start the medication selection mini-game"""
        self.active = True
        self.completed = False
        self.selected_medication = None
        self.show_instructions = True
        self.instruction_timer = 0
        self.show_result = False
        self.purchase_successful = False

        # Reset card states
        for card in self.medication_cards:
            card['selected'] = False
            card['hover'] = False

    def stop(self):
        """Stop the mini-game"""
        self.active = False
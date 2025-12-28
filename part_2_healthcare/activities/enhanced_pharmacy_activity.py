"""
Enhanced Pharmacy Medication Selection Activity
Professional pharmacy interface with realistic medication displays and detailed comparisons
"""
import pygame
import math
import random

class EnhancedPharmacyActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Enhanced medication data with realistic details
        self.medications = [
            {
                "brand_name": "Anxiolex",
                "generic_name": "Sertraline HCl",
                "dosage": "50mg",
                "quantity": "30 tablets",
                "price": 89.99,
                "generic": False,
                "correct_dosage": True,
                "affordable": False,
                "manufacturer": "PharmaCorp",
                "ndc": "12345-678-90",
                "description": "Brand name antidepressant for anxiety and depression",
                "side_effects": ["Nausea", "Headache", "Dizziness"],
                "pill_color": (255, 255, 255),
                "pill_shape": "oval"
            },
            {
                "brand_name": "Generic Sertraline",
                "generic_name": "Sertraline HCl",
                "dosage": "25mg",
                "quantity": "30 tablets",
                "price": 12.50,
                "generic": True,
                "correct_dosage": False,
                "affordable": True,
                "manufacturer": "Generic Pharma",
                "ndc": "98765-432-10",
                "description": "Generic version - lower dose than prescribed",
                "side_effects": ["Nausea", "Headache", "Dizziness"],
                "pill_color": (200, 200, 255),
                "pill_shape": "round"
            },
            {
                "brand_name": "Generic Sertraline",
                "generic_name": "Sertraline HCl",
                "dosage": "50mg",
                "quantity": "30 tablets",
                "price": 15.99,
                "generic": True,
                "correct_dosage": True,
                "affordable": True,
                "manufacturer": "Generic Pharma",
                "ndc": "98765-432-50",
                "description": "Generic version - correct dose and affordable",
                "side_effects": ["Nausea", "Headache", "Dizziness"],
                "pill_color": (200, 255, 200),
                "pill_shape": "round"
            },
            {
                "brand_name": "Zoloft",
                "generic_name": "Sertraline HCl",
                "dosage": "50mg",
                "quantity": "30 tablets",
                "price": 125.00,
                "generic": False,
                "correct_dosage": True,
                "affordable": False,
                "manufacturer": "Pfizer Inc.",
                "ndc": "54321-987-50",
                "description": "Brand name antidepressant - premium pricing",
                "side_effects": ["Nausea", "Headache", "Dizziness"],
                "pill_color": (100, 200, 255),
                "pill_shape": "oval"
            },
            {
                "brand_name": "Generic Fluoxetine",
                "generic_name": "Fluoxetine HCl",
                "dosage": "20mg",
                "quantity": "30 capsules",
                "price": 8.99,
                "generic": True,
                "correct_dosage": False,
                "affordable": True,
                "manufacturer": "Generic Pharma",
                "ndc": "11111-222-20",
                "description": "Different medication class - not what was prescribed",
                "side_effects": ["Insomnia", "Anxiety", "Nausea"],
                "pill_color": (255, 200, 100),
                "pill_shape": "capsule"
            },
            {
                "brand_name": "Generic Escitalopram",
                "generic_name": "Escitalopram Oxalate",
                "dosage": "10mg",
                "quantity": "30 tablets",
                "price": 45.00,
                "generic": True,
                "correct_dosage": True,
                "affordable": False,
                "manufacturer": "Generic Pharma",
                "ndc": "33333-444-10",
                "description": "Generic medication - correct dose but over budget",
                "side_effects": ["Drowsiness", "Nausea", "Fatigue"],
                "pill_color": (255, 255, 200),
                "pill_shape": "round"
            }
        ]

        # Game state
        self.selected_medication = None
        self.budget = 20.00
        self.required_dosage = "50mg"
        self.required_medication = "Sertraline"
        self.attempts = 0
        self.max_attempts = 3
        self.hover_medication = None
        self.comparison_mode = False

        # Animation state
        self.time = 0
        self.selection_animation = 0
        self.scroll_offset = 0
        self.target_scroll = 0

        # UI layout
        self.setup_ui_layout()

        # Enhanced color scheme
        self.colors = {
            'background': (248, 250, 252),
            'pharmacy_blue': (70, 130, 180),
            'pharmacy_green': (85, 170, 85),
            'price_red': (220, 53, 69),
            'price_green': (40, 167, 69),
            'warning_yellow': (255, 193, 7),
            'text_dark': (33, 37, 41),
            'text_light': (108, 117, 125),
            'card_white': (255, 255, 255),
            'card_shadow': (0, 0, 0, 10),
            'generic_badge': (23, 162, 184),
            'brand_badge': (220, 53, 69),
            'correct_green': (40, 167, 69),
            'incorrect_red': (220, 53, 69)
        }

        # Professional fonts
        self.fonts = {
            'title': pygame.font.Font(None, 56),
            'subtitle': pygame.font.Font(None, 36),
            'header': pygame.font.Font(None, 32),
            'body': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 20),
            'tiny': pygame.font.Font(None, 16)
        }

        # Icons and visual elements
        self.pill_animations = {}

    def setup_ui_layout(self):
        """Setup responsive UI layout"""
        # Header area
        self.header_area = pygame.Rect(0, 0, self.SCREEN_WIDTH, 120)

        # Prescription info panel
        self.prescription_panel = pygame.Rect(20, 130, 400, 180)

        # Medication grid
        self.grid_area = pygame.Rect(440, 130, 820, 460)
        self.medication_cards = []

        # Setup medication card positions (2x3 grid)
        card_width = 260
        card_height = 140
        cards_per_row = 3
        spacing_x = 20
        spacing_y = 20

        for i, med in enumerate(self.medications):
            row = i // cards_per_row
            col = i % cards_per_row

            x = self.grid_area.x + col * (card_width + spacing_x)
            y = self.grid_area.y + row * (card_height + spacing_y)

            card_rect = pygame.Rect(x, y, card_width, card_height)
            self.medication_cards.append(card_rect)

        # Feedback area
        self.feedback_area = pygame.Rect(20, 320, 400, 280)

        # Action buttons
        self.compare_button = pygame.Rect(self.SCREEN_WIDTH - 200, 600, 160, 40)

    def draw_pharmacy_header(self, surface):
        """Draw professional pharmacy header"""
        # Background gradient
        for y in range(self.header_area.height):
            progress = y / self.header_area.height
            r = int(70 + (180 - 70) * progress)
            g = int(130 + (200 - 130) * progress)
            b = int(180 + (220 - 180) * progress)
            pygame.draw.line(surface, (r, g, b),
                           (0, y), (self.SCREEN_WIDTH, y))

        # Pharmacy logo area
        logo_rect = pygame.Rect(30, 20, 80, 80)
        pygame.draw.ellipse(surface, (255, 255, 255), logo_rect)
        pygame.draw.ellipse(surface, self.colors['pharmacy_blue'], logo_rect, width=4)

        # Cross symbol
        cross_color = self.colors['pharmacy_green']
        pygame.draw.line(surface, cross_color,
                        (logo_rect.centerx, logo_rect.centery - 25),
                        (logo_rect.centerx, logo_rect.centery + 25), width=8)
        pygame.draw.line(surface, cross_color,
                        (logo_rect.centerx - 25, logo_rect.centery),
                        (logo_rect.centerx + 25, logo_rect.centery), width=8)

        # Pharmacy name
        title_text = self.fonts['title'].render("MediCare Pharmacy", True, (255, 255, 255))
        surface.blit(title_text, (130, 35))

        subtitle_text = self.fonts['body'].render("Professional Medication Services", True, (255, 255, 255, 200))
        surface.blit(subtitle_text, (130, 75))

        # Current time and date
        import datetime
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        current_date = datetime.datetime.now().strftime("%B %d, %Y")

        time_text = self.fonts['small'].render(current_time, True, (255, 255, 255))
        date_text = self.fonts['tiny'].render(current_date, True, (255, 255, 255, 180))

        surface.blit(time_text, (self.SCREEN_WIDTH - 150, 30))
        surface.blit(date_text, (self.SCREEN_WIDTH - 150, 50))

    def draw_prescription_panel(self, surface):
        """Draw prescription requirements panel"""
        # Panel background with shadow
        shadow_rect = pygame.Rect(self.prescription_panel.x + 3, self.prescription_panel.y + 3,
                                 self.prescription_panel.width, self.prescription_panel.height)
        pygame.draw.rect(surface, (0, 0, 0, 20), shadow_rect, border_radius=12)

        pygame.draw.rect(surface, self.colors['card_white'], self.prescription_panel, border_radius=12)
        pygame.draw.rect(surface, self.colors['pharmacy_blue'], self.prescription_panel, width=2, border_radius=12)

        # Header
        header_text = self.fonts['header'].render("Your Prescription", True, self.colors['text_dark'])
        surface.blit(header_text, (self.prescription_panel.x + 20, self.prescription_panel.y + 20))

        # Requirements list
        requirements = [
            ("Medication:", self.required_medication),
            ("Dosage:", self.required_dosage),
            ("Budget:", f"${self.budget:.2f}"),
            ("Insurance:", "None (pay cash)")
        ]

        y_offset = 60
        for label, value in requirements:
            label_text = self.fonts['body'].render(label, True, self.colors['text_light'])
            value_text = self.fonts['body'].render(value, True, self.colors['text_dark'])

            surface.blit(label_text, (self.prescription_panel.x + 20, self.prescription_panel.y + y_offset))
            surface.blit(value_text, (self.prescription_panel.x + 150, self.prescription_panel.y + y_offset))

            y_offset += 30

    def draw_medication_card(self, surface, medication, card_rect, index):
        """Draw detailed medication card"""
        is_hovered = (self.hover_medication == index)
        is_selected = (self.selected_medication == medication)

        # Card shadow
        shadow_rect = pygame.Rect(card_rect.x + 2, card_rect.y + 2,
                                 card_rect.width, card_rect.height)
        shadow_color = (0, 0, 0, 30) if is_hovered else (0, 0, 0, 15)
        pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=8)

        # Card background
        card_color = self.colors['card_white']
        if is_selected:
            card_color = (240, 248, 255)
        elif is_hovered:
            card_color = (248, 249, 250)

        pygame.draw.rect(surface, card_color, card_rect, border_radius=8)

        # Border color based on correctness (if selected or attempted)
        border_color = self.colors['text_light']
        border_width = 1

        if is_selected or self.attempts >= self.max_attempts:
            is_correct = (medication["generic"] and
                         medication["correct_dosage"] and
                         medication["price"] <= self.budget)

            if is_correct:
                border_color = self.colors['correct_green']
                border_width = 3
            elif is_selected:
                border_color = self.colors['incorrect_red']
                border_width = 3

        pygame.draw.rect(surface, border_color, card_rect, width=border_width, border_radius=8)

        # Generic/Brand badge
        badge_color = self.colors['generic_badge'] if medication['generic'] else self.colors['brand_badge']
        badge_text = "GENERIC" if medication['generic'] else "BRAND"
        badge_rect = pygame.Rect(card_rect.x + 10, card_rect.y + 10, 80, 20)

        pygame.draw.rect(surface, badge_color, badge_rect, border_radius=10)
        badge_surface = self.fonts['tiny'].render(badge_text, True, (255, 255, 255))
        badge_text_rect = badge_surface.get_rect(center=badge_rect.center)
        surface.blit(badge_surface, badge_text_rect)

        # Medication name
        name_text = self.fonts['body'].render(medication['brand_name'], True, self.colors['text_dark'])
        surface.blit(name_text, (card_rect.x + 10, card_rect.y + 40))

        # Generic name (smaller)
        generic_text = self.fonts['small'].render(medication['generic_name'], True, self.colors['text_light'])
        surface.blit(generic_text, (card_rect.x + 10, card_rect.y + 65))

        # Dosage and quantity
        dosage_text = self.fonts['body'].render(f"{medication['dosage']}", True, self.colors['text_dark'])
        quantity_text = self.fonts['small'].render(medication['quantity'], True, self.colors['text_light'])

        surface.blit(dosage_text, (card_rect.x + 10, card_rect.y + 85))
        surface.blit(quantity_text, (card_rect.x + 10, card_rect.y + 105))

        # Price (prominent display)
        price_color = self.colors['price_green'] if medication['price'] <= self.budget else self.colors['price_red']
        price_text = self.fonts['header'].render(f"${medication['price']:.2f}", True, price_color)

        # Price background
        price_bg = pygame.Rect(card_rect.right - 90, card_rect.y + 40, 80, 35)
        pygame.draw.rect(surface, (price_color[0], price_color[1], price_color[2], 20), price_bg, border_radius=5)

        price_rect = price_text.get_rect(center=price_bg.center)
        surface.blit(price_text, price_rect)

        # Visual pill representation
        pill_x = card_rect.right - 45
        pill_y = card_rect.y + 85

        if medication['pill_shape'] == 'round':
            pygame.draw.circle(surface, medication['pill_color'], (pill_x, pill_y), 12)
            pygame.draw.circle(surface, self.colors['text_light'], (pill_x, pill_y), 12, width=1)
        elif medication['pill_shape'] == 'oval':
            pill_rect = pygame.Rect(pill_x - 15, pill_y - 8, 30, 16)
            pygame.draw.ellipse(surface, medication['pill_color'], pill_rect)
            pygame.draw.ellipse(surface, self.colors['text_light'], pill_rect, width=1)
        else:  # capsule
            # Draw capsule as two circles connected
            pygame.draw.circle(surface, medication['pill_color'], (pill_x - 8, pill_y), 6)
            pygame.draw.circle(surface, (255, 255, 255), (pill_x + 8, pill_y), 6)
            pygame.draw.rect(surface, medication['pill_color'],
                           pygame.Rect(pill_x - 8, pill_y - 6, 16, 12))

        # Affordability indicator
        if medication['price'] <= self.budget:
            check_pos = (card_rect.right - 20, card_rect.bottom - 20)
            pygame.draw.circle(surface, self.colors['correct_green'], check_pos, 8)
            # Checkmark
            check_points = [
                (check_pos[0] - 3, check_pos[1]),
                (check_pos[0] - 1, check_pos[1] + 2),
                (check_pos[0] + 3, check_pos[1] - 2)
            ]
            pygame.draw.lines(surface, (255, 255, 255), False, check_points, 2)

    def draw_feedback_panel(self, surface):
        """Draw detailed feedback panel"""
        # Panel background
        shadow_rect = pygame.Rect(self.feedback_area.x + 3, self.feedback_area.y + 3,
                                 self.feedback_area.width, self.feedback_area.height)
        pygame.draw.rect(surface, (0, 0, 0, 20), shadow_rect, border_radius=12)

        pygame.draw.rect(surface, self.colors['card_white'], self.feedback_area, border_radius=12)
        pygame.draw.rect(surface, self.colors['pharmacy_blue'], self.feedback_area, width=2, border_radius=12)

        # Header
        header_text = self.fonts['header'].render("Selection Analysis", True, self.colors['text_dark'])
        surface.blit(header_text, (self.feedback_area.x + 20, self.feedback_area.y + 20))

        # Attempts counter
        attempts_text = f"Attempts: {self.attempts}/{self.max_attempts}"
        attempts_surface = self.fonts['body'].render(attempts_text, True, self.colors['text_light'])
        surface.blit(attempts_surface, (self.feedback_area.right - 150, self.feedback_area.y + 25))

        y_offset = 60

        if self.selected_medication:
            med = self.selected_medication

            # Analysis criteria
            criteria = [
                ("Generic Option", med["generic"], "Saves money vs brand name"),
                ("Correct Dosage", med["correct_dosage"], f"Need {self.required_dosage}"),
                ("Within Budget", med["price"] <= self.budget, f"${med['price']:.2f} vs ${self.budget:.2f}"),
                ("Right Medication", self.required_medication.lower() in med["generic_name"].lower(),
                 f"Need {self.required_medication}")
            ]

            for criterion, passed, description in criteria:
                # Criterion name
                criterion_text = self.fonts['body'].render(criterion, True, self.colors['text_dark'])
                surface.blit(criterion_text, (self.feedback_area.x + 20, self.feedback_area.y + y_offset))

                # Status icon
                status_pos = (self.feedback_area.x + 180, self.feedback_area.y + y_offset + 8)
                status_color = self.colors['correct_green'] if passed else self.colors['incorrect_red']
                status_icon = "✓" if passed else "✗"

                pygame.draw.circle(surface, status_color, status_pos, 10)
                icon_surface = self.fonts['body'].render(status_icon, True, (255, 255, 255))
                icon_rect = icon_surface.get_rect(center=status_pos)
                surface.blit(icon_surface, icon_rect)

                # Description
                desc_surface = self.fonts['small'].render(description, True, self.colors['text_light'])
                surface.blit(desc_surface, (self.feedback_area.x + 210, self.feedback_area.y + y_offset + 5))

                y_offset += 35

            # Overall recommendation
            all_criteria_met = all([
                med["generic"],
                med["correct_dosage"],
                med["price"] <= self.budget,
                self.required_medication.lower() in med["generic_name"].lower()
            ])

            if all_criteria_met:
                recommendation = "✓ RECOMMENDED CHOICE"
                rec_color = self.colors['correct_green']
            else:
                recommendation = "⚠ NOT RECOMMENDED"
                rec_color = self.colors['incorrect_red']

            rec_surface = self.fonts['header'].render(recommendation, True, rec_color)
            rec_rect = rec_surface.get_rect(center=(self.feedback_area.centerx, self.feedback_area.y + y_offset + 20))
            surface.blit(rec_surface, rec_rect)

        else:
            # Instructions when no medication selected
            instructions = [
                "Select a medication to see detailed analysis",
                "",
                "Consider these factors:",
                "• Generic vs Brand (cost savings)",
                "• Correct dosage for your prescription",
                "• Price within your budget",
                "• Same active ingredient"
            ]

            for instruction in instructions:
                if instruction:
                    color = self.colors['text_dark'] if instruction.startswith('•') else self.colors['text_light']
                    font = self.fonts['small'] if instruction.startswith('•') else self.fonts['body']

                    text_surface = font.render(instruction, True, color)
                    surface.blit(text_surface, (self.feedback_area.x + 20, self.feedback_area.y + y_offset))

                y_offset += 25

    def handle_event(self, event):
        """Handle enhanced pharmacy interface events"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        # Update hover state
        self.hover_medication = None
        for i, card_rect in enumerate(self.medication_cards):
            if card_rect.collidepoint(mouse_pos):
                self.hover_medication = i
                break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check medication card clicks
            for i, card_rect in enumerate(self.medication_cards):
                if card_rect.collidepoint(mouse_pos):
                    self.select_medication(i)
                    break

        elif event.type == pygame.KEYDOWN:
            # Number keys for quick selection
            if pygame.K_1 <= event.key <= pygame.K_6:
                med_index = event.key - pygame.K_1
                if med_index < len(self.medications):
                    self.select_medication(med_index)
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def select_medication(self, index):
        """Select medication with enhanced validation"""
        self.selected_medication = self.medications[index]
        self.attempts += 1

        # Check if selection meets all criteria
        med = self.selected_medication
        is_correct = (med["generic"] and
                     med["correct_dosage"] and
                     med["price"] <= self.budget and
                     self.required_medication.lower() in med["generic_name"].lower())

        if is_correct:
            self.complete_activity(success=True)
        elif self.attempts >= self.max_attempts:
            self.complete_activity(success=False)

    def complete_activity(self, success):
        """Complete pharmacy activity with results"""
        self.completed = True
        self.success_achieved = success

        # Store results for manager
        self.results = {
            'success': success,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'message': 'Medication selection completed' if success else 'Maximum attempts reached'
        }

    def get_results(self):
        """Get results from the pharmacy activity"""
        if hasattr(self, 'results'):
            return self.results
        return {
            'success': False,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'message': 'Pharmacy activity in progress'
        }

    def update(self, dt):
        """Update pharmacy interface animations"""
        if not self.active:
            return

        self.time += dt

        # Smooth hover animations
        if self.hover_medication is not None:
            self.selection_animation = min(1.0, self.selection_animation + dt * 4)
        else:
            self.selection_animation = max(0.0, self.selection_animation - dt * 4)

    def render(self, screen):
        """Render enhanced pharmacy interface"""
        if not self.active:
            return

        # Background
        screen.fill(self.colors['background'])

        # Draw pharmacy header
        self.draw_pharmacy_header(screen)

        # Draw prescription panel
        self.draw_prescription_panel(screen)

        # Draw medication cards
        for i, (medication, card_rect) in enumerate(zip(self.medications, self.medication_cards)):
            self.draw_medication_card(screen, medication, card_rect, i)

        # Draw feedback panel
        self.draw_feedback_panel(screen)

        # Completion message
        if self.completed:
            message_bg = pygame.Rect(200, 300, 880, 120)
            pygame.draw.rect(screen, (255, 255, 255), message_bg, border_radius=15)
            pygame.draw.rect(screen, self.colors['pharmacy_blue'], message_bg, width=3, border_radius=15)

            if (self.selected_medication and
                self.selected_medication["generic"] and
                self.selected_medication["correct_dosage"] and
                self.selected_medication["price"] <= self.budget):

                message = "✓ Excellent Choice! You found affordable, appropriate medication."
                message_color = self.colors['correct_green']
            else:
                message = "⚠ Medication challenges are common. Pharmacist can help find alternatives."
                message_color = self.colors['incorrect_red']

            message_surface = self.fonts['subtitle'].render(message, True, message_color)
            message_rect = message_surface.get_rect(center=message_bg.center)
            screen.blit(message_surface, message_rect)

    def start(self):
        """Start enhanced pharmacy activity"""
        self.active = True
        self.completed = False
        self.selected_medication = None
        self.attempts = 0
        self.hover_medication = None

    def stop(self):
        """Stop pharmacy activity"""
        self.active = False
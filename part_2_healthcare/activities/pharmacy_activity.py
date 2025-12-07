"""
Pharmacy Medication Selection Activity
Find generic medication that meets both affordability and dosage requirements
"""
import pygame

class PharmacyMedicationActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Medication options
        self.medications = [
            {
                "name": "Brand Name Anxiolex",
                "dosage": "10mg",
                "price": 89.99,
                "generic": False,
                "correct_dosage": True,
                "affordable": False
            },
            {
                "name": "Generic Sertraline",
                "dosage": "25mg",
                "price": 12.50,
                "generic": True,
                "correct_dosage": False,
                "affordable": True
            },
            {
                "name": "Generic Sertraline",
                "dosage": "50mg",
                "price": 15.99,
                "generic": True,
                "correct_dosage": True,
                "affordable": True
            },
            {
                "name": "Brand Name Zoloft",
                "dosage": "50mg",
                "price": 125.00,
                "generic": False,
                "correct_dosage": True,
                "affordable": False
            },
            {
                "name": "Generic Fluoxetine",
                "dosage": "20mg",
                "price": 8.99,
                "generic": True,
                "correct_dosage": False,
                "affordable": True
            },
            {
                "name": "Generic Escitalopram",
                "dosage": "10mg",
                "price": 45.00,
                "generic": True,
                "correct_dosage": True,
                "affordable": False
            }
        ]

        # Game state
        self.selected_medication = None
        self.budget = 20.00  # Player's budget
        self.required_dosage = "50mg"
        self.attempts = 0
        self.max_attempts = 3

        # UI elements
        self.med_rects = []
        self.setup_medication_rects()

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        self.LIGHT_BLUE = (173, 216, 230)
        self.LIGHT_GREEN = (144, 238, 144)
        self.LIGHT_RED = (255, 182, 193)

        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)

    def setup_medication_rects(self):
        """Set up rectangles for medication options"""
        self.med_rects = []
        cols = 2
        rows = 3

        start_x = 150
        start_y = 200
        width = 450
        height = 120
        spacing_x = 500
        spacing_y = 140

        for i, med in enumerate(self.medications):
            col = i % cols
            row = i // cols
            x = start_x + (col * spacing_x)
            y = start_y + (row * spacing_y)
            self.med_rects.append(pygame.Rect(x, y, width, height))

    def handle_event(self, event):
        """Handle player input"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check medication clicks
            for i, rect in enumerate(self.med_rects):
                if rect.collidepoint(mouse_pos):
                    self.select_medication(i)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def select_medication(self, index):
        """Select a medication option"""
        self.selected_medication = self.medications[index]
        self.attempts += 1

        # Check if selection is correct
        med = self.selected_medication
        correct_choice = (med["generic"] and
                         med["correct_dosage"] and
                         med["affordable"] and
                         med["price"] <= self.budget)

        if correct_choice:
            self.complete_activity(success=True)
        elif self.attempts >= self.max_attempts:
            self.complete_activity(success=False)
        else:
            # Give feedback and let them try again
            pass

    def complete_activity(self, success):
        """Complete the pharmacy activity"""
        self.completed = True

        if self.objective_manager:
            if success:
                self.objective_manager.complete_objective("medication_selection")
            else:
                # Failed to find affordable medication - consequences
                self.objective_manager.advance_to_next_objective()

    def get_medication_color(self, med, rect_index):
        """Get color for medication based on selection and correctness"""
        if self.selected_medication == med:
            if self.attempts >= self.max_attempts or (med["generic"] and med["correct_dosage"] and med["affordable"]):
                # Show correct answer
                if med["generic"] and med["correct_dosage"] and med["affordable"] and med["price"] <= self.budget:
                    return self.LIGHT_GREEN
                else:
                    return self.LIGHT_RED
            else:
                return self.LIGHT_BLUE
        else:
            return self.WHITE

    def render(self, screen):
        """Render the pharmacy activity interface"""
        if not self.active:
            return

        # Background
        screen.fill(self.LIGHT_BLUE)

        # Title
        title = self.font_large.render("Metro Pharmacy", True, self.BLUE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # Instructions
        instruction_lines = [
            f"Find a medication that meets ALL requirements:",
            f"• Generic version (to save money)",
            f"• Correct dosage: {self.required_dosage}",
            f"• Within budget: ${self.budget:.2f}",
            f"",
            f"Attempts: {self.attempts}/{self.max_attempts}"
        ]

        y = 90
        for line in instruction_lines:
            if line:
                text = self.font_small.render(line, True, self.BLACK)
                text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
                screen.blit(text, text_rect)
            y += 20

        # Medication options
        for i, (med, rect) in enumerate(zip(self.medications, self.med_rects)):
            # Background color based on selection
            bg_color = self.get_medication_color(med, i)
            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, self.BLACK, rect, 2)

            # Medication name
            name_text = self.font_medium.render(med["name"], True, self.BLACK)
            screen.blit(name_text, (rect.x + 10, rect.y + 10))

            # Dosage
            dosage_text = self.font_small.render(f"Dosage: {med['dosage']}", True, self.BLACK)
            screen.blit(dosage_text, (rect.x + 10, rect.y + 40))

            # Price
            price_color = self.GREEN if med["price"] <= self.budget else self.RED
            price_text = self.font_small.render(f"Price: ${med['price']:.2f}", True, price_color)
            screen.blit(price_text, (rect.x + 10, rect.y + 65))

            # Generic indicator
            generic_text = "Generic" if med["generic"] else "Brand Name"
            generic_color = self.GREEN if med["generic"] else self.RED
            generic_surface = self.font_small.render(generic_text, True, generic_color)
            screen.blit(generic_surface, (rect.x + 200, rect.y + 40))

            # Affordability indicator
            affordable = med["price"] <= self.budget
            afford_text = "Affordable" if affordable else "Too Expensive"
            afford_color = self.GREEN if affordable else self.RED
            afford_surface = self.font_small.render(afford_text, True, afford_color)
            screen.blit(afford_surface, (rect.x + 200, rect.y + 65))

            # Dosage correctness (only show after selection or max attempts)
            if self.selected_medication or self.attempts >= self.max_attempts:
                dosage_correct = med["correct_dosage"]
                dosage_text = "Correct Dosage" if dosage_correct else "Wrong Dosage"
                dosage_color = self.GREEN if dosage_correct else self.RED
                dosage_surface = self.font_small.render(dosage_text, True, dosage_color)
                screen.blit(dosage_surface, (rect.x + 200, rect.y + 90))

        # Selection feedback
        if self.selected_medication:
            med = self.selected_medication

            feedback_lines = []

            if not med["generic"]:
                feedback_lines.append("❌ Brand name medications are expensive")
            else:
                feedback_lines.append("✓ Generic medication saves money")

            if not med["correct_dosage"]:
                feedback_lines.append(f"❌ Need {self.required_dosage}, this is {med['dosage']}")
            else:
                feedback_lines.append(f"✓ Correct dosage: {med['dosage']}")

            if med["price"] > self.budget:
                feedback_lines.append(f"❌ ${med['price']:.2f} exceeds ${self.budget:.2f} budget")
            else:
                feedback_lines.append(f"✓ ${med['price']:.2f} is within budget")

            # Feedback box
            feedback_rect = pygame.Rect(50, 550, 600, 120)
            pygame.draw.rect(screen, self.WHITE, feedback_rect)
            pygame.draw.rect(screen, self.BLACK, feedback_rect, 2)

            y = feedback_rect.y + 10
            for line in feedback_lines:
                feedback_surface = self.font_small.render(line, True, self.BLACK)
                screen.blit(feedback_surface, (feedback_rect.x + 10, y))
                y += 25

        # Completion message
        if self.completed:
            if (self.selected_medication and
                self.selected_medication["generic"] and
                self.selected_medication["correct_dosage"] and
                self.selected_medication["affordable"] and
                self.selected_medication["price"] <= self.budget):

                message = "Success! You found the right medication."
                message_color = self.GREEN
            else:
                message = "Unable to find affordable medication. This is a common challenge."
                message_color = self.RED

            message_surface = self.font_large.render(message, True, message_color)
            message_rect = message_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 680))

            # Message background
            bg_rect = message_rect.copy()
            bg_rect.inflate(40, 20)
            pygame.draw.rect(screen, self.WHITE, bg_rect)
            pygame.draw.rect(screen, message_color, bg_rect, 2)

            screen.blit(message_surface, message_rect)

        # Help text
        if not self.completed:
            help_text = "Click on a medication to select it"
            help_surface = self.font_small.render(help_text, True, self.GRAY)
            screen.blit(help_surface, (50, self.SCREEN_HEIGHT - 40))

    def start(self):
        """Start the pharmacy activity"""
        self.active = True
        self.completed = False
        self.selected_medication = None
        self.attempts = 0

    def stop(self):
        """Stop the pharmacy activity"""
        self.active = False
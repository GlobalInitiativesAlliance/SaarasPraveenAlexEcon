"""
Budget Breakdown Activity
Visual representation of impossible monthly expenses vs income
"""
import pygame
import math
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class BudgetBreakdown(Activity):
    """Interactive budget breakdown showing the impossible math of poverty"""

    def __init__(self, game):
        super().__init__(game)
        self.narrative_ref = None  # Set by parent interior

        # Budget categories with amounts
        self.expenses = [
            {"category": "Phone", "amount": 50, "essential": True, "note": "Need for job"},
            {"category": "Food", "amount": 400, "essential": True, "note": "Bare minimum"},
            {"category": "Transport", "amount": 120, "essential": True, "note": "Bus pass"},
            {"category": "Toiletries", "amount": 80, "essential": True, "note": "Basic hygiene"},
            {"category": "Laundry", "amount": 60, "essential": True, "note": "Coin laundry"},
            {"category": "Clothes", "amount": 100, "essential": True, "note": "Work clothes"},
            {"category": "Medical", "amount": 150, "essential": True, "note": "Prescriptions"},
            {"category": "Misc", "amount": 190, "essential": True, "note": "Everything else"}
        ]

        # Financial values
        self.monthly_income = 1200  # From previous calculation
        self.total_expenses = sum(exp["amount"] for exp in self.expenses)
        self.remaining = self.monthly_income - self.total_expenses

        # Visual state
        self.current_expense_index = 0
        self.all_revealed = False
        self.animation_timer = 0
        self.shake_timer = 0
        self.pulse_timer = 0

        # UI elements
        self.continue_button_rect = None
        self.hover_element = None
        self.bar_rects = {}

        # Colors for categories
        self.expense_colors = [
            (100, 150, 255),  # Phone - blue
            (255, 150, 100),  # Food - orange
            (150, 255, 150),  # Transport - green
            (255, 255, 150),  # Toiletries - yellow
            (200, 150, 255),  # Laundry - purple
            (255, 150, 200),  # Clothes - pink
            (255, 100, 100),  # Medical - red
            (180, 180, 180)   # Misc - gray
        ]

    def start(self):
        """Start the budget breakdown activity"""
        super().start()
        self.current_expense_index = 0
        self.all_revealed = False
        self.animation_timer = 0

    def draw(self, screen):
        """Main draw function"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Update animation
        self.animation_timer += 0.016
        self.pulse_timer += 0.016

        # Main container
        container_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (40, 35, 30), container_rect)
        pygame.draw.rect(screen, (200, 180, 160), container_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Monthly Budget Breakdown", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Draw income bar
        self.draw_income_bar(screen)

        # Draw expense bars
        self.draw_expense_bars(screen)

        # Draw savings calculation
        if self.all_revealed:
            self.draw_savings_math(screen)

        # Continue button when all revealed
        if self.all_revealed:
            self.draw_continue_button(screen)

    def draw_income_bar(self, screen):
        """Draw the income bar at the top"""
        bar_x = 100
        bar_y = 130
        bar_width = SCREEN_WIDTH - 200
        bar_height = 40

        # Background
        income_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 150, 100), income_rect)
        pygame.draw.rect(screen, (255, 255, 255), income_rect, 2)

        # Label
        label_font = pygame.font.Font(None, 28)
        label = label_font.render(f"Monthly Income: ${self.monthly_income}", True, (255, 255, 255))
        screen.blit(label, (bar_x + 10, bar_y + 8))

        # Scale indicator
        scale_font = pygame.font.Font(None, 18)
        for i in range(0, 1201, 200):
            x_pos = bar_x + (i / 1200) * bar_width
            pygame.draw.line(screen, (255, 255, 255), (x_pos, bar_y + bar_height), (x_pos, bar_y + bar_height + 5), 2)
            scale_text = scale_font.render(f"${i}", True, (200, 200, 200))
            screen.blit(scale_text, (x_pos - 20, bar_y + bar_height + 10))

    def draw_expense_bars(self, screen):
        """Draw expense bars stacking up"""
        start_x = 100
        start_y = 220
        bar_width_max = SCREEN_WIDTH - 200
        bar_height = 35
        spacing = 5

        # Track cumulative amount
        cumulative = 0

        for i, expense in enumerate(self.expenses):
            if i > self.current_expense_index:
                break  # Don't show unrevealed expenses

            y_pos = start_y + i * (bar_height + spacing)

            # Calculate bar width based on amount
            bar_width = int((expense["amount"] / 1200) * bar_width_max)

            # Create rect for interaction
            bar_rect = pygame.Rect(start_x, y_pos, bar_width, bar_height)
            self.bar_rects[expense["category"]] = bar_rect

            # Draw bar with color
            color = self.expense_colors[i]

            # Add pulse effect to current revealing bar
            if i == self.current_expense_index and not self.all_revealed:
                pulse = abs(math.sin(self.pulse_timer * 3)) * 20
                color = tuple(min(255, c + pulse) for c in color)

            pygame.draw.rect(screen, color, bar_rect)
            pygame.draw.rect(screen, (255, 255, 255), bar_rect, 2)

            # Category label
            label_font = pygame.font.Font(None, 22)
            label = label_font.render(f"{expense['category']}: ${expense['amount']}", True, (255, 255, 255))
            screen.blit(label, (start_x + 5, y_pos + 7))

            # Note on the right
            note_font = pygame.font.Font(None, 18)
            note = note_font.render(f"({expense['note']})", True, (200, 200, 200))
            screen.blit(note, (start_x + bar_width + 10, y_pos + 9))

            cumulative += expense["amount"]

            # Show cumulative total
            if i == self.current_expense_index or self.all_revealed:
                total_font = pygame.font.Font(None, 20)
                total_text = f"Total so far: ${cumulative}"

                # Color based on whether it exceeds income
                if cumulative > self.monthly_income:
                    total_color = (255, 100, 100)
                    # Add shake when first exceeding
                    if self.shake_timer > 0 and cumulative > self.monthly_income:
                        shake_x = int(math.sin(self.shake_timer * 20) * 3)
                        total_surf = total_font.render(total_text, True, total_color)
                        screen.blit(total_surf, (SCREEN_WIDTH - 250 + shake_x, y_pos + 9))
                        self.shake_timer -= 0.016
                    else:
                        total_surf = total_font.render(total_text, True, total_color)
                        screen.blit(total_surf, (SCREEN_WIDTH - 250, y_pos + 9))
                else:
                    total_color = (200, 200, 200)
                    total_surf = total_font.render(total_text, True, total_color)
                    screen.blit(total_surf, (SCREEN_WIDTH - 250, y_pos + 9))

        # Draw line showing income limit
        income_line_x = start_x + bar_width_max
        pygame.draw.line(screen, (255, 50, 50),
                        (income_line_x, start_y - 10),
                        (income_line_x, start_y + len(self.expenses) * (bar_height + spacing)),
                        3)

        # Income limit label
        limit_font = pygame.font.Font(None, 20)
        limit_text = "Income Limit →"
        limit_surf = limit_font.render(limit_text, True, (255, 50, 50))
        screen.blit(limit_surf, (income_line_x - 100, start_y - 30))

    def draw_savings_math(self, screen):
        """Draw the final savings calculation"""
        math_x = SCREEN_WIDTH // 2 - 200
        math_y = 550

        # Background box
        math_rect = pygame.Rect(math_x - 20, math_y - 20, 400, 150)
        pygame.draw.rect(screen, (50, 40, 40), math_rect)
        pygame.draw.rect(screen, (255, 100, 100), math_rect, 3)

        # Calculation
        calc_font = pygame.font.Font(None, 32)

        # Income
        income_text = f"Income: ${self.monthly_income}"
        income_surf = calc_font.render(income_text, True, (100, 255, 100))
        screen.blit(income_surf, (math_x, math_y))

        # Minus sign
        minus_text = "–"
        minus_surf = calc_font.render(minus_text, True, (255, 255, 255))
        screen.blit(minus_surf, (math_x, math_y + 30))

        # Expenses
        expense_text = f"Expenses: ${self.total_expenses}"
        expense_surf = calc_font.render(expense_text, True, (255, 100, 100))
        screen.blit(expense_surf, (math_x, math_y + 30))

        # Line
        pygame.draw.line(screen, (255, 255, 255),
                        (math_x, math_y + 65),
                        (math_x + 250, math_y + 65), 2)

        # Result
        result_text = f"Remaining: ${self.remaining}"
        if self.remaining >= 0:
            result_color = (255, 220, 100)  # Yellow for barely surviving
        else:
            result_color = (255, 50, 50)  # Red for impossible

        # Make it blink if very low
        if abs(self.remaining) < 100:
            if int(self.animation_timer * 2) % 2 == 0:
                result_surf = calc_font.render(result_text, True, result_color)
                screen.blit(result_surf, (math_x, math_y + 75))
        else:
            result_surf = calc_font.render(result_text, True, result_color)
            screen.blit(result_surf, (math_x, math_y + 75))

        # Additional context
        context_font = pygame.font.Font(None, 20)
        if self.remaining > 0:
            context = f"That's ${self.remaining} for EVERYTHING else. For 30 days."
        else:
            context = "You literally cannot afford to exist."
        context_surf = context_font.render(context, True, (255, 150, 150))
        screen.blit(context_surf, (math_x, math_y + 110))

    def draw_continue_button(self, screen):
        """Draw continue button"""
        button_font = pygame.font.Font(None, 32)
        button_text = "Face Reality"

        button_surf = button_font.render(button_text, True, (255, 255, 255))

        self.continue_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50
        )

        # Red button for harsh reality
        button_color = (150, 50, 50)
        pygame.draw.rect(screen, button_color, self.continue_button_rect)

        if self.hover_element == "continue":
            pygame.draw.rect(screen, (255, 255, 255), self.continue_button_rect, 3)
        else:
            pygame.draw.rect(screen, (200, 200, 200), self.continue_button_rect, 2)

        button_x = self.continue_button_rect.centerx - button_surf.get_width() // 2
        button_y = self.continue_button_rect.centery - button_surf.get_height() // 2
        screen.blit(button_surf, (button_x, button_y))

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Reveal next expense
        if self.current_expense_index < len(self.expenses) - 1:
            self.current_expense_index += 1
            # Trigger shake when expenses exceed income
            cumulative = sum(self.expenses[i]["amount"] for i in range(self.current_expense_index + 1))
            if cumulative > self.monthly_income:
                self.shake_timer = 1.0
        elif self.current_expense_index == len(self.expenses) - 1:
            self.all_revealed = True
            self.shake_timer = 1.5

        # Handle continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            if self.all_revealed:
                self.complete_breakdown()

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        self.hover_element = None

        # Check bar hovers
        for category, rect in self.bar_rects.items():
            if rect.collidepoint(pos):
                self.hover_element = category
                break

        # Check continue button hover
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.hover_element = "continue"

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        # Space to reveal next expense
        if key == pygame.K_SPACE:
            if self.current_expense_index < len(self.expenses) - 1:
                self.current_expense_index += 1
                # Trigger shake when expenses exceed income
                cumulative = sum(self.expenses[i]["amount"] for i in range(self.current_expense_index + 1))
                if cumulative > self.monthly_income:
                    self.shake_timer = 1.0
            elif self.current_expense_index == len(self.expenses) - 1:
                self.all_revealed = True
                self.shake_timer = 1.5
            elif self.all_revealed:
                self.complete_breakdown()

    def complete_breakdown(self):
        """Complete the budget breakdown"""
        # Update parent interior state
        if self.narrative_ref:
            self.narrative_ref.budget_reviewed = True
            self.narrative_ref.monthly_savings = self.remaining

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show completion message through parent's dialogue box
            if hasattr(self.narrative_ref, 'dialogue_box'):
                if self.remaining > 0:
                    msg = f"${self.remaining} left each month. If nothing goes wrong. "
                    msg += "No emergencies. No sick days. No life."
                else:
                    msg = f"You're ${abs(self.remaining)} short every month. "
                    msg += "The math doesn't work. It never did."
                self.narrative_ref.dialogue_box.show(None, msg)

        # Mark activity complete
        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt

        # Auto-reveal expenses for dramatic effect
        if not self.all_revealed and self.animation_timer > (self.current_expense_index + 1) * 1.2:
            if self.current_expense_index < len(self.expenses) - 1:
                self.current_expense_index += 1
                # Trigger shake when expenses exceed income
                cumulative = sum(self.expenses[i]["amount"] for i in range(self.current_expense_index + 1))
                if cumulative > self.monthly_income:
                    self.shake_timer = 1.0
            else:
                self.all_revealed = True
                self.shake_timer = 1.5
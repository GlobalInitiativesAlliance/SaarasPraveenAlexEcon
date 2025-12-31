"""
Income Calculator Activity
Visual breakdown of part-time minimum wage reality
"""
import pygame
import math
from src.activities.activities import Activity
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class IncomeCalculator(Activity):
    """Interactive income calculation showing the harsh math of minimum wage"""

    def __init__(self, game):
        super().__init__(game)
        self.narrative_ref = None  # Set by parent interior

        # Calculation stages
        self.current_stage = 0
        self.stages_complete = False

        # Income values
        self.hourly_wage = 15
        self.hours_per_week = 20
        self.weeks_per_month = 4.33  # Average

        # Calculated values
        self.weekly_income = 0
        self.monthly_gross = 0
        self.tax_amount = 0
        self.monthly_net = 0

        # Animation timers
        self.animation_timer = 0
        self.number_reveal_timer = 0
        self.shake_timer = 0

        # UI elements
        self.continue_button_rect = None
        self.hover_element = None

        # Visual effects
        self.revealed_numbers = [False, False, False, False, False]
        self.calculator_display = ""

        # Load textures
        self.load_textures()

    def load_textures(self):
        """Create visual elements for the calculator"""
        # Calculator background
        self.calc_bg = pygame.Surface((500, 600))
        self.calc_bg.fill((60, 60, 70))

        # Display screen for calculator
        self.display_bg = pygame.Surface((460, 80))
        self.display_bg.fill((180, 200, 180))

    def start(self):
        """Start the income calculator activity"""
        super().start()
        self.current_stage = 0
        self.animation_timer = 0
        self.calculator_display = ""

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
        if self.number_reveal_timer > 0:
            self.number_reveal_timer -= 0.016

        # Main container
        container_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (40, 35, 30), container_rect)
        pygame.draw.rect(screen, (200, 180, 160), container_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("Income Reality Check", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Draw calculator
        self.draw_calculator(screen)

        # Draw calculation stages
        self.draw_calculation_stages(screen)

        # Draw reality comparison
        if self.current_stage >= 4:
            self.draw_reality_comparison(screen)

        # Continue button when all stages complete
        if self.stages_complete:
            self.draw_continue_button(screen)

    def draw_calculator(self, screen):
        """Draw calculator visual"""
        calc_x = SCREEN_WIDTH // 2 - 250
        calc_y = 120

        # Calculator body
        screen.blit(self.calc_bg, (calc_x, calc_y))
        pygame.draw.rect(screen, (40, 40, 50), (calc_x, calc_y, 500, 600), 3)

        # Display screen
        display_rect = pygame.Rect(calc_x + 20, calc_y + 20, 460, 80)
        screen.blit(self.display_bg, (display_rect.x, display_rect.y))
        pygame.draw.rect(screen, (20, 20, 30), display_rect, 2)

        # Display text
        display_font = pygame.font.Font(None, 48)
        if self.calculator_display:
            # Add shake effect for final low number
            if "$1,200" in self.calculator_display and self.shake_timer > 0:
                shake_x = int(math.sin(self.shake_timer * 20) * 3)
                display_surf = display_font.render(self.calculator_display, True, (20, 40, 20))
                screen.blit(display_surf, (display_rect.x + 20 + shake_x, display_rect.y + 25))
                self.shake_timer -= 0.016
            else:
                display_surf = display_font.render(self.calculator_display, True, (20, 40, 20))
                screen.blit(display_surf, (display_rect.x + 20, display_rect.y + 25))

        # Draw calculator buttons (visual only)
        button_size = 70
        button_spacing = 10
        start_x = calc_x + 40
        start_y = calc_y + 130

        button_labels = [
            ['7', '8', '9', '÷'],
            ['4', '5', '6', '×'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]

        button_font = pygame.font.Font(None, 36)
        for row_idx, row in enumerate(button_labels):
            for col_idx, label in enumerate(row):
                button_x = start_x + col_idx * (button_size + button_spacing)
                button_y = start_y + row_idx * (button_size + button_spacing)
                button_rect = pygame.Rect(button_x, button_y, button_size, button_size)

                # Button appearance
                if label in ['÷', '×', '-', '+', '=']:
                    button_color = (100, 100, 120)
                else:
                    button_color = (80, 80, 90)

                pygame.draw.rect(screen, button_color, button_rect)
                pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)

                # Button label
                label_surf = button_font.render(label, True, (255, 255, 255))
                label_x = button_rect.centerx - label_surf.get_width() // 2
                label_y = button_rect.centery - label_surf.get_height() // 2
                screen.blit(label_surf, (label_x, label_y))

    def draw_calculation_stages(self, screen):
        """Draw step-by-step calculation"""
        stages_x = 100
        stages_y = 150
        stage_font = pygame.font.Font(None, 28)
        value_font = pygame.font.Font(None, 32)

        stages = [
            ("Hourly Wage:", f"${self.hourly_wage}/hour"),
            ("Hours per Week:", f"{self.hours_per_week} hours"),
            ("Weekly Income:", f"${self.weekly_income}"),
            ("Monthly Gross:", f"${self.monthly_gross}"),
            ("After Taxes (~15%):", f"${self.monthly_net}")
        ]

        for i, (label, value) in enumerate(stages):
            y_pos = stages_y + i * 60

            # Draw label
            label_surf = stage_font.render(label, True, (200, 200, 200))
            screen.blit(label_surf, (stages_x, y_pos))

            # Draw value if revealed
            if self.revealed_numbers[i]:
                # Color code the values
                if i == 0:  # Hourly wage - neutral
                    value_color = (200, 200, 200)
                elif i < 3:  # Calculations - yellow
                    value_color = (255, 220, 100)
                elif i == 3:  # Gross - orange
                    value_color = (255, 180, 100)
                else:  # Net - red for low amount
                    value_color = (255, 100, 100)

                value_surf = value_font.render(value, True, value_color)
                screen.blit(value_surf, (stages_x, y_pos + 30))

                # Draw calculation arrow
                if i > 0 and i <= self.current_stage:
                    arrow_y = y_pos - 20
                    pygame.draw.lines(screen, (150, 150, 150), False,
                                    [(stages_x + 250, arrow_y - 10),
                                     (stages_x + 250, arrow_y),
                                     (stages_x + 240, arrow_y - 5)], 2)

    def draw_reality_comparison(self, screen):
        """Draw comparison with living costs"""
        comp_x = SCREEN_WIDTH - 350
        comp_y = 200

        # Background for comparison
        comp_rect = pygame.Rect(comp_x - 10, comp_y - 10, 300, 400)
        pygame.draw.rect(screen, (50, 40, 40), comp_rect)
        pygame.draw.rect(screen, (200, 100, 100), comp_rect, 2)

        # Title
        title_font = pygame.font.Font(None, 28)
        title_surf = title_font.render("Living Costs Reality", True, (255, 200, 200))
        screen.blit(title_surf, (comp_x, comp_y))

        # Cost breakdown
        cost_font = pygame.font.Font(None, 22)
        costs = [
            ("Cheapest Apartment:", "$1,400/mo"),
            ("Required Income:", "$4,200/mo"),
            ("Your Income:", f"${self.monthly_net}/mo"),
            ("", ""),
            ("Income Gap:", f"-${4200 - self.monthly_net}/mo"),
            ("", ""),
            ("Result:", "IMPOSSIBLE")
        ]

        y_offset = comp_y + 40
        for label, value in costs:
            if label == "":
                y_offset += 10
                continue

            # Draw label
            label_surf = cost_font.render(label, True, (200, 180, 180))
            screen.blit(label_surf, (comp_x, y_offset))

            # Draw value
            if value:
                if "IMPOSSIBLE" in value:
                    value_color = (255, 50, 50)
                    # Make it blink
                    if int(self.animation_timer * 2) % 2 == 0:
                        value_surf = cost_font.render(value, True, value_color)
                        screen.blit(value_surf, (comp_x + 150, y_offset))
                elif "-$" in value:
                    value_color = (255, 100, 100)
                    value_surf = cost_font.render(value, True, value_color)
                    screen.blit(value_surf, (comp_x + 150, y_offset))
                else:
                    value_color = (200, 200, 200)
                    value_surf = cost_font.render(value, True, value_color)
                    screen.blit(value_surf, (comp_x + 150, y_offset))

            y_offset += 30

        # Bottom message
        msg_font = pygame.font.Font(None, 20)
        msg = "You'd need 3.5x your income"
        msg_surf = msg_font.render(msg, True, (255, 150, 150))
        screen.blit(msg_surf, (comp_x, comp_y + 350))

        msg2 = "just for the cheapest place"
        msg2_surf = msg_font.render(msg2, True, (255, 150, 150))
        screen.blit(msg2_surf, (comp_x, comp_y + 370))

    def draw_continue_button(self, screen):
        """Draw continue button"""
        button_font = pygame.font.Font(None, 32)
        button_text = "Accept Reality"

        button_surf = button_font.render(button_text, True, (255, 255, 255))

        self.continue_button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 120, 200, 50
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

        # Progress through calculation stages
        if self.current_stage < 5 and self.number_reveal_timer <= 0:
            self.advance_calculation()

        # Handle continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            if self.stages_complete:
                self.complete_calculation()

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        self.hover_element = None

        # Check continue button hover
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            self.hover_element = "continue"

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        # Space to advance calculation
        if key == pygame.K_SPACE:
            if self.current_stage < 5 and self.number_reveal_timer <= 0:
                self.advance_calculation()
            elif self.stages_complete:
                self.complete_calculation()

    def advance_calculation(self):
        """Advance to next calculation stage"""
        if self.current_stage == 0:
            # Show hourly wage
            self.calculator_display = "$15"
            self.revealed_numbers[0] = True
            self.number_reveal_timer = 0.5
        elif self.current_stage == 1:
            # Show hours per week
            self.calculator_display = "20 hrs"
            self.revealed_numbers[1] = True
            self.number_reveal_timer = 0.5
        elif self.current_stage == 2:
            # Calculate weekly
            self.weekly_income = self.hourly_wage * self.hours_per_week
            self.calculator_display = f"${self.weekly_income}"
            self.revealed_numbers[2] = True
            self.number_reveal_timer = 0.5
        elif self.current_stage == 3:
            # Calculate monthly gross
            self.monthly_gross = int(self.weekly_income * self.weeks_per_month)
            self.calculator_display = f"${self.monthly_gross}"
            self.revealed_numbers[3] = True
            self.number_reveal_timer = 0.5
        elif self.current_stage == 4:
            # Calculate after taxes
            self.tax_amount = int(self.monthly_gross * 0.15)
            self.monthly_net = self.monthly_gross - self.tax_amount
            self.calculator_display = f"${self.monthly_net}"
            self.revealed_numbers[4] = True
            self.shake_timer = 2.0  # Shake to emphasize how low it is
            self.stages_complete = True

        self.current_stage += 1

    def complete_calculation(self):
        """Complete the income calculation"""
        # Update parent interior state
        if self.narrative_ref:
            self.narrative_ref.income_calculated = True
            self.narrative_ref.monthly_income = self.monthly_net

            if hasattr(self.narrative_ref, 'update_objective_display'):
                self.narrative_ref.update_objective_display()

            # Show completion message through parent's dialogue box
            if hasattr(self.narrative_ref, 'dialogue_box'):
                msg = f"${self.monthly_net} per month. "
                msg += "That's your entire income. Before any emergencies. "
                msg += "Before any life happens."
                self.narrative_ref.dialogue_box.show(None, msg)

        # Mark activity complete
        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt

        # Auto-advance calculation for dramatic effect
        if self.number_reveal_timer <= 0 and self.current_stage < 5:
            if self.animation_timer > (self.current_stage + 1) * 1.5:
                self.advance_calculation()
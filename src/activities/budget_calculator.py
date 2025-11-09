"""
Budget Calculator Activity - The Impossible Math
Visual demonstration of how full-time minimum wage doesn't cover basic expenses
"""

import pygame
import math
import random
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class BudgetCalculator(Activity):
    """Interactive budget calculator showing the impossible math of poverty"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.narrative_ref = None

        # Initialize fonts
        self.small_font = pygame.font.Font(None, 20)
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 32)
        self.huge_font = pygame.font.Font(None, 48)
        self.calculator_font = pygame.font.Font(None, 36)

        # Financial data
        self.monthly_income = 1200  # Full-time minimum wage
        self.expenses = {
            'rent': {'amount': 900, 'essential': True, 'color': (200, 50, 50)},
            'utilities': {'amount': 200, 'essential': True, 'color': (100, 150, 255)},
            'food': {'amount': 200, 'essential': True, 'color': (255, 150, 50)},
            'phone': {'amount': 50, 'essential': True, 'color': (150, 255, 150)},
            'transport': {'amount': 120, 'essential': True, 'color': (255, 255, 100)},
            'medical': {'amount': 150, 'essential': True, 'color': (255, 100, 255)},
            'clothes': {'amount': 50, 'essential': True, 'color': (150, 200, 255)},
            'toiletries': {'amount': 30, 'essential': True, 'color': (200, 200, 150)}
        }

        # Calculator state
        self.calculator_display = "1200"
        self.current_calculation = self.monthly_income
        self.calculation_history = []
        self.current_expense_index = 0
        self.expense_keys = list(self.expenses.keys())

        # Animation states
        self.sequence_step = 0  # 0: show income, 1: add rent, 2: utilities, etc.
        self.animation_timer = 0
        self.shake_timer = 0
        self.red_flash_timer = 0
        self.money_particles = []
        self.stress_level = 0
        self.crack_effect = False

        # Visual elements
        self.money_stacks = []  # Visual money representations
        self.receipt_items = []  # Items on the receipt tape
        self.calculator_buttons = self.create_calculator_buttons()

        # Interactive elements
        self.hovering_button = None
        self.adjustment_mode = False
        self.impossible_message_timer = 0

        # Initialize money stacks
        self.initialize_money_stacks()

    def initialize_money_stacks(self):
        """Create visual money stack representations"""
        # Create stack for income
        bills_count = self.monthly_income // 100  # Each bill = $100
        for i in range(bills_count):
            self.money_stacks.append({
                'x': 150 + (i % 6) * 30,
                'y': 200 - (i // 6) * 5,
                'value': 100,
                'color': (50, 200, 50),
                'status': 'income',
                'alpha': 255
            })

    def create_calculator_buttons(self):
        """Create calculator button layout"""
        buttons = {}
        calc_x, calc_y = 650, 200
        button_size = 50
        spacing = 5

        # Number buttons
        for i in range(10):
            if i == 0:
                x = calc_x + button_size + spacing
                y = calc_y + 4 * (button_size + spacing)
            else:
                row = (9 - i) // 3
                col = (i - 1) % 3
                x = calc_x + col * (button_size + spacing)
                y = calc_y + row * (button_size + spacing) + button_size + spacing

            buttons[str(i)] = pygame.Rect(x, y, button_size, button_size)

        # Operation buttons
        operations = ['+', '-', '=', 'C']
        for i, op in enumerate(operations):
            x = calc_x + 3 * (button_size + spacing)
            y = calc_y + (i + 1) * (button_size + spacing)
            buttons[op] = pygame.Rect(x, y, button_size, button_size)

        return buttons

    def start(self):
        """Start the budget calculator"""
        super().start()
        self.sequence_step = 0
        self.animation_timer = 0
        self.stress_level = 0
        self.calculation_history = []
        self.receipt_items = []

        # Add income to receipt
        self.add_to_receipt("INCOME", self.monthly_income, (50, 200, 50))

    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.complete_activity()
            elif event.key == pygame.K_SPACE:
                # Advance to next step
                if self.sequence_step <= len(self.expense_keys):
                    self.advance_sequence()
            elif event.key == pygame.K_r and self.sequence_step > len(self.expense_keys):
                # Reset to try again (shows it's still impossible)
                self.reset_calculation()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check calculator button clicks
            for button_text, button_rect in self.calculator_buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    self.handle_calculator_input(button_text)
                    break

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hovering_button = None

            for button_text, button_rect in self.calculator_buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    self.hovering_button = button_text
                    break

    def handle_calculator_input(self, button_text):
        """Handle calculator button presses"""
        if button_text == 'C':
            self.calculator_display = "0"
            self.current_calculation = 0
        elif button_text == '=':
            # Advance sequence when equals is pressed
            self.advance_sequence()
        elif button_text in '0123456789':
            if self.calculator_display == "0":
                self.calculator_display = button_text
            else:
                self.calculator_display += button_text
            self.current_calculation = int(self.calculator_display)

    def advance_sequence(self):
        """Advance to the next expense in the sequence"""
        if self.sequence_step == 0:
            # First expense: Rent
            self.subtract_expense('rent')
            self.sequence_step = 1
        elif self.sequence_step < len(self.expense_keys):
            # Next expenses
            expense_key = self.expense_keys[self.sequence_step]
            self.subtract_expense(expense_key)
            self.sequence_step += 1

        # Check if we've added all expenses
        if self.sequence_step >= len(self.expense_keys):
            self.show_final_result()

    def subtract_expense(self, expense_key):
        """Subtract an expense from the current total"""
        expense = self.expenses[expense_key]
        self.current_calculation -= expense['amount']
        self.calculator_display = str(self.current_calculation)

        # Add to receipt
        self.add_to_receipt(expense_key.upper(), -expense['amount'], expense['color'])

        # Visual effects
        if self.current_calculation < 0:
            self.trigger_negative_effects()

        # Remove money stacks
        bills_to_remove = expense['amount'] // 100
        for _ in range(min(bills_to_remove, len(self.money_stacks))):
            if self.money_stacks:
                bill = self.money_stacks.pop()
                # Create particle effect
                self.create_money_particle(bill['x'], bill['y'], expense['color'])

        # Increase stress
        self.stress_level = min(100, self.stress_level + 15)

    def add_to_receipt(self, item_name, amount, color):
        """Add item to the receipt tape"""
        self.receipt_items.append({
            'name': item_name,
            'amount': amount,
            'color': color,
            'y_offset': 0,
            'alpha': 0
        })

    def create_money_particle(self, x, y, color):
        """Create a particle effect for money disappearing"""
        for _ in range(5):
            self.money_particles.append({
                'x': x + random.randint(-20, 20),
                'y': y + random.randint(-20, 20),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'life': 1.0,
                'color': color
            })

    def trigger_negative_effects(self):
        """Trigger visual effects when balance goes negative"""
        self.shake_timer = 1.0
        self.red_flash_timer = 1.0
        if self.current_calculation < -100:
            self.crack_effect = True

    def show_final_result(self):
        """Show the final impossible result"""
        self.impossible_message_timer = 3.0

        # Calculate what's missing
        total_expenses = sum(exp['amount'] for exp in self.expenses.values())
        self.deficit = self.monthly_income - total_expenses

        # Pass results to narrative if available
        if self.narrative_ref:
            self.narrative_ref.budget_calculated = True
            self.narrative_ref.monthly_deficit = self.deficit

    def reset_calculation(self):
        """Reset the calculation to try different combinations"""
        self.sequence_step = 0
        self.current_calculation = self.monthly_income
        self.calculator_display = str(self.monthly_income)
        self.receipt_items = []
        self.stress_level = 0
        self.crack_effect = False
        self.initialize_money_stacks()
        self.add_to_receipt("INCOME", self.monthly_income, (50, 200, 50))

    def complete_activity(self):
        """Complete the budget calculator activity"""
        self.completed = True
        self.active = False

    def update(self, dt):
        """Update animations and particles"""
        self.animation_timer += dt

        # Update shake
        if self.shake_timer > 0:
            self.shake_timer -= dt

        # Update red flash
        if self.red_flash_timer > 0:
            self.red_flash_timer -= dt

        # Update impossible message
        if self.impossible_message_timer > 0:
            self.impossible_message_timer -= dt

        # Update particles
        for particle in self.money_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= dt * 2

            if particle['life'] <= 0:
                self.money_particles.remove(particle)

        # Animate receipt items
        for item in self.receipt_items:
            if item['alpha'] < 255:
                item['alpha'] = min(255, item['alpha'] + 10)
            if item['y_offset'] < 20:
                item['y_offset'] = min(20, item['y_offset'] + 2)

    def draw(self, screen):
        """Draw the budget calculator interface"""
        # Background
        screen.fill((30, 25, 20))

        # Apply red flash effect
        if self.red_flash_timer > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((200, 0, 0))
            flash_surf.set_alpha(int(50 * self.red_flash_timer))
            screen.blit(flash_surf, (0, 0))

        # Apply shake effect
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = int(math.sin(self.shake_timer * 30) * 5)
            shake_y = int(math.cos(self.shake_timer * 30) * 3)

        # Draw main elements with shake
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Title
        title = self.huge_font.render("THE IMPOSSIBLE MATH", True, (200, 50, 50))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))

        # Draw money area
        self.draw_money_area(surface)

        # Draw calculator
        self.draw_calculator(surface)

        # Draw receipt
        self.draw_receipt(surface)

        # Draw stress meter
        self.draw_stress_meter(surface)

        # Draw particles
        for particle in self.money_particles:
            alpha = int(255 * particle['life'])
            pygame.draw.circle(surface, (*particle['color'], alpha),
                             (int(particle['x']), int(particle['y'])), 3)

        # Draw crack effect
        if self.crack_effect:
            self.draw_crack_effect(surface)

        # Draw final message
        if self.impossible_message_timer > 0:
            self.draw_impossible_message(surface)

        # Apply shake to final render
        screen.blit(surface, (shake_x, shake_y))

        # Draw instructions
        self.draw_instructions(screen)

    def draw_money_area(self, surface):
        """Draw the visual money representation"""
        # Money area background
        money_rect = pygame.Rect(50, 150, 500, 300)
        pygame.draw.rect(surface, (40, 35, 30), money_rect)
        pygame.draw.rect(surface, (100, 90, 80), money_rect, 2)

        # Label
        label = self.font.render("YOUR MONEY", True, (200, 200, 200))
        surface.blit(label, (money_rect.centerx - label.get_width()//2, money_rect.y - 30))

        # Draw money stacks
        for bill in self.money_stacks:
            bill_rect = pygame.Rect(bill['x'], bill['y'], 25, 15)
            pygame.draw.rect(surface, bill['color'], bill_rect)
            pygame.draw.rect(surface, (0, 0, 0), bill_rect, 1)

        # Show current balance
        balance_color = (50, 200, 50) if self.current_calculation >= 0 else (200, 50, 50)
        balance_text = self.large_font.render(f"Balance: ${self.current_calculation}", True, balance_color)
        surface.blit(balance_text, (money_rect.centerx - balance_text.get_width()//2, money_rect.bottom + 20))

    def draw_calculator(self, surface):
        """Draw the calculator interface"""
        # Calculator body
        calc_rect = pygame.Rect(630, 150, 250, 350)
        pygame.draw.rect(surface, (60, 60, 70), calc_rect)
        pygame.draw.rect(surface, (150, 150, 160), calc_rect, 3)

        # Display
        display_rect = pygame.Rect(calc_rect.x + 10, calc_rect.y + 10, calc_rect.width - 20, 50)
        pygame.draw.rect(surface, (20, 30, 20), display_rect)
        pygame.draw.rect(surface, (100, 150, 100), display_rect, 2)

        # Display text
        display_color = (0, 255, 0) if self.current_calculation >= 0 else (255, 0, 0)
        display_text = self.calculator_font.render(self.calculator_display, True, display_color)
        text_x = display_rect.right - display_text.get_width() - 10
        text_y = display_rect.centery - display_text.get_height()//2
        surface.blit(display_text, (text_x, text_y))

        # Draw buttons
        for button_text, button_rect in self.calculator_buttons.items():
            # Button color
            if button_text == self.hovering_button:
                button_color = (100, 100, 120)
            elif button_text in '0123456789':
                button_color = (70, 70, 80)
            else:
                button_color = (100, 60, 60)

            pygame.draw.rect(surface, button_color, button_rect)
            pygame.draw.rect(surface, (200, 200, 200), button_rect, 2)

            # Button text
            btn_text = self.font.render(button_text, True, (255, 255, 255))
            text_x = button_rect.centerx - btn_text.get_width()//2
            text_y = button_rect.centery - btn_text.get_height()//2
            surface.blit(btn_text, (text_x, text_y))

    def draw_receipt(self, surface):
        """Draw the receipt tape showing expenses"""
        # Receipt background
        receipt_rect = pygame.Rect(50, 480, 300, 250)
        pygame.draw.rect(surface, (240, 240, 230), receipt_rect)
        pygame.draw.rect(surface, (100, 100, 100), receipt_rect, 2)

        # Header
        header = self.font.render("--- MONTHLY BUDGET ---", True, (0, 0, 0))
        surface.blit(header, (receipt_rect.x + 20, receipt_rect.y + 10))

        # Receipt items
        y_offset = receipt_rect.y + 40
        for item in self.receipt_items[-8:]:  # Show last 8 items
            # Item name
            name_text = self.small_font.render(item['name'], True, (0, 0, 0))
            surface.blit(name_text, (receipt_rect.x + 20, y_offset + item['y_offset']))

            # Amount
            amount_str = f"${abs(item['amount'])}" if item['amount'] < 0 else f"+${item['amount']}"
            amount_color = (0, 100, 0) if item['amount'] > 0 else (150, 0, 0)
            amount_text = self.small_font.render(amount_str, True, amount_color)
            surface.blit(amount_text, (receipt_rect.right - amount_text.get_width() - 20, y_offset + item['y_offset']))

            y_offset += 25

        # Total line
        if self.receipt_items:
            pygame.draw.line(surface, (0, 0, 0),
                           (receipt_rect.x + 20, y_offset),
                           (receipt_rect.right - 20, y_offset), 2)

            total_color = (0, 100, 0) if self.current_calculation >= 0 else (200, 0, 0)
            total_text = self.font.render(f"TOTAL: ${self.current_calculation}", True, total_color)
            surface.blit(total_text, (receipt_rect.centerx - total_text.get_width()//2, y_offset + 10))

    def draw_stress_meter(self, surface):
        """Draw stress level indicator"""
        # Stress meter background
        meter_rect = pygame.Rect(SCREEN_WIDTH - 150, 150, 30, 200)
        pygame.draw.rect(surface, (50, 50, 50), meter_rect)
        pygame.draw.rect(surface, (100, 100, 100), meter_rect, 2)

        # Stress fill
        if self.stress_level > 0:
            fill_height = int((self.stress_level / 100) * meter_rect.height)
            fill_rect = pygame.Rect(meter_rect.x, meter_rect.bottom - fill_height,
                                   meter_rect.width, fill_height)

            # Color based on stress level
            if self.stress_level < 30:
                color = (100, 200, 100)
            elif self.stress_level < 60:
                color = (200, 200, 50)
            elif self.stress_level < 80:
                color = (200, 100, 50)
            else:
                color = (200, 50, 50)
                # Pulse effect at high stress
                pulse = abs(math.sin(self.animation_timer * 3)) * 50
                color = tuple(min(255, c + int(pulse)) for c in color)

            pygame.draw.rect(surface, color, fill_rect)

        # Label
        label = self.small_font.render("STRESS", True, (200, 200, 200))
        surface.blit(label, (meter_rect.centerx - label.get_width()//2, meter_rect.bottom + 10))

        # Stress percentage
        percent_text = self.small_font.render(f"{int(self.stress_level)}%", True, (200, 200, 200))
        surface.blit(percent_text, (meter_rect.centerx - percent_text.get_width()//2, meter_rect.bottom + 30))

    def draw_crack_effect(self, surface):
        """Draw screen crack effect when severely in debt"""
        crack_points = [
            (SCREEN_WIDTH//2, 0),
            (SCREEN_WIDTH//2 + 20, 200),
            (SCREEN_WIDTH//2 - 10, 400),
            (SCREEN_WIDTH//2 + 30, 600),
            (SCREEN_WIDTH//2, SCREEN_HEIGHT)
        ]

        for i in range(len(crack_points) - 1):
            pygame.draw.line(surface, (100, 0, 0), crack_points[i], crack_points[i+1], 3)
            # Branch cracks
            if i % 2 == 0:
                branch_x = crack_points[i][0] + random.randint(-50, 50)
                branch_y = crack_points[i][1]
                pygame.draw.line(surface, (80, 0, 0),
                               crack_points[i],
                               (branch_x, branch_y + 50), 2)

    def draw_impossible_message(self, surface):
        """Draw the final message showing it's impossible"""
        # Darken screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))

        # Message box
        box_rect = pygame.Rect(SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 150, 800, 300)
        pygame.draw.rect(surface, (20, 20, 30), box_rect)
        pygame.draw.rect(surface, (200, 50, 50), box_rect, 4)

        # Title
        title = self.huge_font.render("IT'S LITERALLY IMPOSSIBLE", True, (255, 50, 50))
        surface.blit(title, (box_rect.centerx - title.get_width()//2, box_rect.y + 30))

        # Details
        details = [
            f"Monthly Income: ${self.monthly_income}",
            f"Essential Expenses: ${sum(exp['amount'] for exp in self.expenses.values())}",
            f"Monthly Deficit: ${self.deficit}",
            "",
            "You need to earn 50% more just to break even.",
            "This doesn't include: savings, emergencies, healthcare, or joy."
        ]

        y_offset = box_rect.y + 100
        for line in details:
            if line:
                color = (200, 200, 200) if not line.startswith("Monthly Deficit") else (255, 100, 100)
                line_text = self.font.render(line, True, color)
                surface.blit(line_text, (box_rect.centerx - line_text.get_width()//2, y_offset))
            y_offset += 30

    def draw_instructions(self, screen):
        """Draw control instructions"""
        instructions = []

        if self.sequence_step == 0:
            instructions.append("Click calculator buttons or press SPACE to subtract rent")
        elif self.sequence_step < len(self.expense_keys):
            instructions.append("Press SPACE to add next expense")
        else:
            instructions.append("Press R to try different combinations (spoiler: they all fail)")
            instructions.append("Press ESC to continue")

        y_offset = SCREEN_HEIGHT - 40 * len(instructions)
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (150, 150, 150))
            screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, y_offset))
            y_offset += 25
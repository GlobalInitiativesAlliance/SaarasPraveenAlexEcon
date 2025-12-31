"""
Bill Paying Mini-Game
Drag bills to the 'Paid' pile, watch your money drain to just $40
Demonstrates the stress of living paycheck to paycheck
"""
import pygame

class BillPayingGame:
    """Drag bills to paid pile, showing paycheck-to-paycheck reality"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Money tracking
        self.paycheck = 400.0
        self.current_balance = self.paycheck
        self.final_leftover = 40.0  # Always end with $40

        # Bills to pay
        self.bills = [
            {'name': 'Rent', 'amount': 200, 'paid': False, 'required': True},
            {'name': 'Electric', 'amount': 45, 'paid': False, 'required': True},
            {'name': 'Phone', 'amount': 35, 'paid': False, 'required': True},
            {'name': 'Bus Pass', 'amount': 40, 'paid': False, 'required': True},
            {'name': 'Insurance', 'amount': 40, 'paid': False, 'required': True},
        ]

        # UI elements
        self.paid_pile = pygame.Rect(800, 300, 300, 250)
        self.unpaid_area = pygame.Rect(180, 300, 300, 250)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Result state
        self.all_paid = False
        self.show_result = False
        self.result_timer = 0

        # Stress meter (visual only)
        self.stress_level = 0.0

        # Create bill rectangles
        self.create_bill_rects()

    def create_bill_rects(self):
        """Create draggable bill cards"""
        start_x = 200
        start_y = 320

        for i, bill in enumerate(self.bills):
            x = start_x + (i % 2) * 140
            y = start_y + (i // 2) * 70
            bill['rect'] = pygame.Rect(x, y, 120, 55)
            bill['original_pos'] = (x, y)

    def handle_event(self, event):
        """Handle bill dragging"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.completed = True
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for bill in self.bills:
                if not bill['paid'] and bill['rect'].collidepoint(mouse_pos):
                    self.dragging = bill
                    self.drag_offset = (
                        bill['rect'].x - mouse_pos[0],
                        bill['rect'].y - mouse_pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in paid pile
                if self.paid_pile.colliderect(self.dragging['rect']):
                    self.dragging['paid'] = True
                    self.current_balance -= self.dragging['amount']
                    self.stress_level = min(1.0, self.stress_level + 0.2)

                    # Position in paid pile
                    paid_count = sum(1 for b in self.bills if b['paid']) - 1
                    self.dragging['rect'].x = self.paid_pile.x + 20 + (paid_count % 2) * 140
                    self.dragging['rect'].y = self.paid_pile.y + 20 + (paid_count // 2) * 60
                else:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Check if all paid
                if all(bill['paid'] for bill in self.bills):
                    self.trigger_result()

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

        return True

    def trigger_result(self):
        """Show the final balance result"""
        self.all_paid = True
        self.show_result = True
        self.result_timer = 180  # 3 seconds

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the bill paying interface"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)
        overlay.fill((245, 240, 235))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = title_font.render("Monthly Bills - Payday", True, (40, 40, 50))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

        # Paycheck display
        check_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 150, 80, 300, 80)
        pygame.draw.rect(screen, (255, 255, 240), check_rect)
        pygame.draw.rect(screen, (100, 150, 100), check_rect, 3)

        check_font = pygame.font.Font(None, 28)
        check_label = check_font.render("PAYCHECK", True, (50, 100, 50))
        screen.blit(check_label, (check_rect.centerx - check_label.get_width() // 2, check_rect.y + 10))

        amount_font = pygame.font.Font(None, 36)
        amount_text = amount_font.render(f"${self.paycheck:.2f}", True, (50, 100, 50))
        screen.blit(amount_text, (check_rect.centerx - amount_text.get_width() // 2, check_rect.y + 40))

        # Current balance (shows money draining)
        balance_font = pygame.font.Font(None, 32)
        balance_color = (50, 150, 50) if self.current_balance > 100 else (200, 100, 50)
        if self.current_balance <= 50:
            balance_color = (200, 50, 50)
        balance_text = balance_font.render(f"Remaining: ${self.current_balance:.2f}", True, balance_color)
        screen.blit(balance_text, (self.SCREEN_WIDTH // 2 - balance_text.get_width() // 2, 180))

        if not self.show_result:
            # Stress meter
            self.render_stress_meter(screen)

            # Unpaid area label
            area_font = pygame.font.Font(None, 28)
            unpaid_label = area_font.render("UNPAID BILLS", True, (150, 50, 50))
            screen.blit(unpaid_label, (self.unpaid_area.centerx - unpaid_label.get_width() // 2, self.unpaid_area.y - 25))

            # Unpaid area
            pygame.draw.rect(screen, (255, 230, 230), self.unpaid_area)
            pygame.draw.rect(screen, (200, 100, 100), self.unpaid_area, 2)

            # Paid pile label
            paid_label = area_font.render("PAID", True, (50, 150, 50))
            screen.blit(paid_label, (self.paid_pile.centerx - paid_label.get_width() // 2, self.paid_pile.y - 25))

            # Paid pile
            pygame.draw.rect(screen, (230, 255, 230), self.paid_pile)
            pygame.draw.rect(screen, (100, 200, 100), self.paid_pile, 2)

            # Draw arrow
            arrow_font = pygame.font.Font(None, 48)
            arrow_text = arrow_font.render("-->", True, (100, 100, 120))
            screen.blit(arrow_text, (550, 400))

            # Bills
            self.render_bills(screen)

            # Instructions
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Drag each bill to the PAID pile", True, (100, 100, 110))
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 650))

        else:
            self.render_result(screen)

    def render_stress_meter(self, screen):
        """Render the stress meter"""
        meter_rect = pygame.Rect(100, 220, 200, 20)
        pygame.draw.rect(screen, (220, 220, 220), meter_rect)

        # Fill based on stress
        if self.stress_level > 0:
            fill_width = int(self.stress_level * meter_rect.width)
            fill_rect = pygame.Rect(meter_rect.x, meter_rect.y, fill_width, meter_rect.height)
            stress_color = (100 + int(self.stress_level * 155), 100 - int(self.stress_level * 50), 100 - int(self.stress_level * 50))
            pygame.draw.rect(screen, stress_color, fill_rect)

        pygame.draw.rect(screen, (100, 100, 110), meter_rect, 2)

        label_font = pygame.font.Font(None, 20)
        label = label_font.render("Stress Level", True, (100, 100, 110))
        screen.blit(label, (meter_rect.x, meter_rect.y - 18))

    def render_bills(self, screen):
        """Render all bill cards"""
        bill_font = pygame.font.Font(None, 20)
        amount_font = pygame.font.Font(None, 24)

        for bill in self.bills:
            # Bill card
            if bill['paid']:
                color = (200, 255, 200)
                border_color = (100, 200, 100)
            elif self.dragging == bill:
                color = (255, 255, 200)
                border_color = (200, 200, 100)
            else:
                color = (255, 230, 230)
                border_color = (200, 150, 150)

            pygame.draw.rect(screen, color, bill['rect'])
            pygame.draw.rect(screen, border_color, bill['rect'], 2)

            # Bill name
            name_text = bill_font.render(bill['name'], True, (40, 40, 50))
            name_x = bill['rect'].centerx - name_text.get_width() // 2
            screen.blit(name_text, (name_x, bill['rect'].y + 8))

            # Amount
            amt_text = amount_font.render(f"${bill['amount']}", True, (150, 50, 50))
            amt_x = bill['rect'].centerx - amt_text.get_width() // 2
            screen.blit(amt_text, (amt_x, bill['rect'].y + 28))

    def render_result(self, screen):
        """Render the final result screen"""
        # Result panel
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 300, 280, 600, 200)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, 3)

        # All bills paid message
        result_font = pygame.font.Font(None, 32)
        result_text = result_font.render("All bills paid!", True, (50, 150, 50))
        result_x = panel_rect.centerx - result_text.get_width() // 2
        screen.blit(result_text, (result_x, panel_rect.y + 30))

        # Final balance
        balance_font = pygame.font.Font(None, 48)
        final_text = balance_font.render(f"Remaining: ${self.final_leftover:.2f}", True, (200, 100, 50))
        final_x = panel_rect.centerx - final_text.get_width() // 2
        screen.blit(final_text, (final_x, panel_rect.y + 70))

        # Commentary
        comment_font = pygame.font.Font(None, 24)
        comments = [
            "This has to last until next paycheck.",
            "Food, emergencies, anything unexpected..."
        ]

        y = panel_rect.y + 130
        for comment in comments:
            comment_surface = comment_font.render(comment, True, (100, 100, 110))
            comment_x = panel_rect.centerx - comment_surface.get_width() // 2
            screen.blit(comment_surface, (comment_x, y))
            y += 25

        # Continue prompt
        if self.result_timer < 120:
            prompt_font = pygame.font.Font(None, 22)
            prompt = "Press any key to continue..."
            prompt_surface = prompt_font.render(prompt, True, (120, 120, 130))
            prompt_x = panel_rect.centerx - prompt_surface.get_width() // 2
            screen.blit(prompt_surface, (prompt_x, panel_rect.bottom - 30))

    def start(self):
        """Start the bill paying game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.all_paid = False
        self.current_balance = self.paycheck
        self.stress_level = 0.0
        self.result_timer = 0

        # Reset bills
        for bill in self.bills:
            bill['paid'] = False
            bill['rect'].x = bill['original_pos'][0]
            bill['rect'].y = bill['original_pos'][1]

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

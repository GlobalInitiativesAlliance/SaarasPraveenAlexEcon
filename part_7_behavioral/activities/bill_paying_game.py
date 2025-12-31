"""
Bill Paying Mini-Game
Drag bills to the 'Paid' pile, watch your money drain to just $40
Demonstrates the stress of living paycheck to paycheck
"""
import pygame
import math
import time

from .behavioral_visual_base import (
    BehavioralUIColors, BehavioralUIMetrics, UIAnimation,
    BehavioralVisualHelpers, behavioral_visuals
)
from .behavioral_particles import behavioral_particles


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
        self.displayed_balance = UIAnimation(self.paycheck, self.paycheck, 0.1)
        self.final_leftover = 40.0  # Always end with $40

        # Bills to pay
        self.bills = [
            {'name': 'Rent', 'amount': 200, 'paid': False, 'required': True, 'icon': 'home'},
            {'name': 'Electric', 'amount': 45, 'paid': False, 'required': True, 'icon': 'bolt'},
            {'name': 'Phone', 'amount': 35, 'paid': False, 'required': True, 'icon': 'phone'},
            {'name': 'Bus Pass', 'amount': 40, 'paid': False, 'required': True, 'icon': 'bus'},
            {'name': 'Insurance', 'amount': 40, 'paid': False, 'required': True, 'icon': 'shield'},
        ]

        # UI elements - positioned for professional layout
        self.paid_pile = pygame.Rect(820, 280, 340, 300)
        self.unpaid_area = pygame.Rect(120, 280, 340, 300)

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.hover_bill = None

        # Result state
        self.all_paid = False
        self.show_result = False
        self.result_timer = 0
        self.result_animation = UIAnimation(0, 0, 0.08)

        # Stress meter (visual feedback)
        self.stress_level = UIAnimation(0.0, 0.0, 0.12)

        # Animations
        self.balance_shake = 0
        self.last_payment_time = 0

        # Create bill rectangles
        self.create_bill_rects()

    def create_bill_rects(self):
        """Create draggable bill cards in a professional grid"""
        start_x = 140
        start_y = 320

        for i, bill in enumerate(self.bills):
            col = i % 2
            row = i // 2
            x = start_x + col * 160
            y = start_y + row * 85
            bill['rect'] = pygame.Rect(x, y, BehavioralUIMetrics.BILL_CARD_WIDTH,
                                       BehavioralUIMetrics.BILL_CARD_HEIGHT)
            bill['original_pos'] = (x, y)
            bill['hover_animation'] = UIAnimation(0, 0, 0.2)

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
                    self.pay_bill(self.dragging)
                else:
                    # Return to original position
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Check if all paid
                if all(bill['paid'] for bill in self.bills):
                    self.trigger_result()

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]
            else:
                # Update hover state
                self.hover_bill = None
                for bill in self.bills:
                    if not bill['paid'] and bill['rect'].collidepoint(mouse_pos):
                        self.hover_bill = bill
                        break

        return True

    def pay_bill(self, bill):
        """Process bill payment with visual effects"""
        bill['paid'] = True
        self.current_balance -= bill['amount']
        self.displayed_balance.target = self.current_balance
        self.stress_level.target = min(1.0, self.stress_level.target + 0.2)
        self.last_payment_time = time.time()
        self.balance_shake = 10

        # Position in paid pile
        paid_count = sum(1 for b in self.bills if b['paid']) - 1
        bill['rect'].x = self.paid_pile.x + 25 + (paid_count % 2) * 165
        bill['rect'].y = self.paid_pile.y + 25 + (paid_count // 2) * 85

        # Emit particles
        behavioral_particles.emit_bill_drop(bill['rect'].centerx, bill['rect'].centery, bill['amount'])
        behavioral_particles.emit_payment_success(bill['rect'].centerx, bill['rect'].centery)

    def trigger_result(self):
        """Show the final balance result"""
        self.all_paid = True
        self.show_result = True
        self.result_timer = 240  # 4 seconds
        self.result_animation.target = 1.0
        behavioral_particles.emit_success_burst(self.SCREEN_WIDTH // 2, 400)

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update animations
        self.displayed_balance.update(dt)
        self.stress_level.update(dt)
        self.result_animation.update(dt)
        behavioral_particles.update(dt)

        # Update hover animations
        for bill in self.bills:
            if bill == self.hover_bill:
                bill['hover_animation'].target = 1.0
            else:
                bill['hover_animation'].target = 0.0
            bill['hover_animation'].update(dt)

        # Balance shake decay
        if self.balance_shake > 0:
            self.balance_shake *= 0.9

        # Stress particles when high
        if self.stress_level.value > 0.6 and not self.show_result:
            if time.time() - self.last_payment_time > 0.5:
                behavioral_particles.emit_anxiety_swirl(
                    self.SCREEN_WIDTH // 2, 200, 50
                )

        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the bill paying interface"""
        if not self.active:
            return

        # Background with stress-based tint
        stress_val = self.stress_level.value
        bg_color = BehavioralVisualHelpers.interpolate_color(
            BehavioralUIColors.BG_CALM,
            BehavioralUIColors.BG_STRESSED,
            stress_val * 0.5
        )
        screen.fill(bg_color)

        # Title with shadow
        self._draw_title(screen)

        # Paycheck display
        self._draw_paycheck(screen)

        # Current balance display (with shake when decreasing)
        self._draw_balance(screen)

        if not self.show_result:
            # Stress meter
            stress_rect = pygame.Rect(100, 200, 220, BehavioralUIMetrics.METER_HEIGHT)
            behavioral_visuals.draw_stress_meter(screen, stress_rect,
                                                 self.stress_level.value,
                                                 "Stress Level", True)

            # Drop zones
            self._draw_drop_zones(screen)

            # Arrow indicator
            self._draw_arrow(screen)

            # Bills
            self._draw_bills(screen)

            # Instructions
            behavioral_visuals.draw_instruction_text(
                screen, "Drag each bill to the PAID pile",
                self.SCREEN_WIDTH // 2, 630
            )

        else:
            self._draw_result(screen)

        # Draw particles on top
        behavioral_particles.draw(screen)

    def _draw_title(self, screen):
        """Draw the game title"""
        title_text = behavioral_visuals.fonts['title'].render(
            "Monthly Bills - Payday", True, BehavioralUIColors.TEXT_PRIMARY
        )
        # Shadow
        shadow_text = behavioral_visuals.fonts['title'].render(
            "Monthly Bills - Payday", True, (0, 0, 0, 30)
        )
        screen.blit(shadow_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 32))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

    def _draw_paycheck(self, screen):
        """Draw the paycheck display"""
        check_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 160, 75, 320, 90)
        behavioral_visuals.draw_money_display(screen, check_rect, self.paycheck, "PAYCHECK", True)

    def _draw_balance(self, screen):
        """Draw current balance with animations"""
        # Shake effect
        shake_x = math.sin(time.time() * 30) * self.balance_shake if self.balance_shake > 0.5 else 0

        balance_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 140 + shake_x,
            175,
            280, 55
        )

        # Shadow
        BehavioralVisualHelpers.draw_shadow(screen, balance_rect, 4, 30,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)

        # Background gradient based on amount
        displayed = self.displayed_balance.value
        if displayed > 100:
            bg_top, bg_bottom = (248, 255, 250), (240, 252, 245)
            text_color = BehavioralUIColors.MONEY_GREEN
        elif displayed > 50:
            bg_top, bg_bottom = (255, 252, 242), (250, 248, 235)
            text_color = BehavioralUIColors.MONEY_GOLD
        else:
            bg_top, bg_bottom = (255, 245, 245), (252, 238, 238)
            text_color = BehavioralUIColors.MONEY_RED
            # Pulsing when low
            pulse = abs(math.sin(time.time() * 3)) * 20
            text_color = (min(255, text_color[0] + int(pulse)), text_color[1], text_color[2])

        BehavioralVisualHelpers.draw_gradient_rect(screen, balance_rect, bg_top, bg_bottom,
                                                   BehavioralUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, text_color, balance_rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Label
        label_text = behavioral_visuals.fonts['small'].render("Remaining", True,
                                                              BehavioralUIColors.TEXT_SECONDARY)
        screen.blit(label_text, (balance_rect.x + 15, balance_rect.y + 8))

        # Amount
        amount_text = behavioral_visuals.fonts['money'].render(
            f"${displayed:.2f}", True, text_color
        )
        screen.blit(amount_text, (balance_rect.right - amount_text.get_width() - 15,
                                  balance_rect.y + 15))

    def _draw_drop_zones(self, screen):
        """Draw the paid and unpaid drop zones"""
        # Check if dragging over paid pile
        is_over_paid = (self.dragging and
                       self.paid_pile.colliderect(self.dragging['rect']))

        # Unpaid area
        behavioral_visuals.draw_drop_zone(
            screen, self.unpaid_area, "UNPAID BILLS", False,
            BehavioralUIColors.BILL_RED
        )

        # Paid pile
        behavioral_visuals.draw_drop_zone(
            screen, self.paid_pile, "PAID", is_over_paid,
            BehavioralUIColors.BILL_GREEN if is_over_paid else None
        )

    def _draw_arrow(self, screen):
        """Draw the arrow between zones"""
        arrow_x = 500
        arrow_y = self.SCREEN_HEIGHT // 2 + 40

        # Arrow body
        arrow_color = BehavioralUIColors.TEXT_MUTED
        points = [
            (arrow_x, arrow_y),
            (arrow_x + 100, arrow_y),
            (arrow_x + 100, arrow_y - 15),
            (arrow_x + 130, arrow_y + 10),
            (arrow_x + 100, arrow_y + 35),
            (arrow_x + 100, arrow_y + 20),
            (arrow_x, arrow_y + 20),
        ]
        pygame.draw.polygon(screen, arrow_color, points)

    def _draw_bills(self, screen):
        """Render all bill cards"""
        # Draw non-dragging bills first
        for bill in self.bills:
            if bill != self.dragging:
                self._draw_bill_card(screen, bill)

        # Draw dragging bill on top
        if self.dragging:
            self._draw_bill_card(screen, self.dragging)

    def _draw_bill_card(self, screen, bill):
        """Draw a single bill card"""
        is_dragging = bill == self.dragging
        is_hover = bill == self.hover_bill and not is_dragging

        behavioral_visuals.draw_bill_card(
            screen, bill['rect'],
            bill['name'], bill['amount'],
            bill['paid'], is_dragging, is_hover
        )

    def _draw_result(self, screen):
        """Render the result screen"""
        # Animate panel appearance
        anim_progress = self.result_animation.value

        panel_width = 620
        panel_height = 280
        panel_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - panel_width // 2,
            int(280 + (1 - anim_progress) * 50),
            panel_width,
            panel_height
        )

        # Draw modal
        behavioral_visuals.draw_modal_container(
            screen, panel_rect,
            "All Bills Paid!",
            BehavioralUIColors.DECISION_GREEN,
            True
        )

        # Final balance display
        balance_rect = pygame.Rect(
            panel_rect.centerx - 120,
            panel_rect.y + 75,
            240, 70
        )
        behavioral_visuals.draw_money_display(
            screen, balance_rect,
            self.final_leftover, "Remaining",
            self.final_leftover > 50
        )

        # Commentary
        comments = [
            "This has to last until next paycheck.",
            "Food, emergencies, anything unexpected..."
        ]

        y = panel_rect.y + 170
        for comment in comments:
            comment_surface = behavioral_visuals.fonts['body'].render(
                comment, True, BehavioralUIColors.TEXT_SECONDARY
            )
            comment_x = panel_rect.centerx - comment_surface.get_width() // 2
            screen.blit(comment_surface, (comment_x, y))
            y += 28

        # Continue prompt
        if self.result_timer < 180:
            behavioral_visuals.draw_continue_prompt(
                screen, panel_rect.centerx, panel_rect.bottom - 25
            )

    def start(self):
        """Start the bill paying game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.all_paid = False
        self.current_balance = self.paycheck
        self.displayed_balance = UIAnimation(self.paycheck, self.paycheck, 0.1)
        self.stress_level = UIAnimation(0.0, 0.0, 0.12)
        self.result_animation = UIAnimation(0, 0, 0.08)
        self.result_timer = 0
        self.balance_shake = 0
        self.dragging = None
        self.hover_bill = None

        # Reset bills
        for bill in self.bills:
            bill['paid'] = False
            bill['rect'].x = bill['original_pos'][0]
            bill['rect'].y = bill['original_pos'][1]
            bill['hover_animation'] = UIAnimation(0, 0, 0.2)

        # Clear particles
        behavioral_particles.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

"""
Medication Selection Mini-Game
Find a generic medication that meets both affordability and dosage requirements
UPGRADED with healthcare visual system - card animations, affordability indicators, polish
"""
import pygame
import random
import math

from part_4_healthcare.activities.healthcare_visual_base import (
    HealthcareUIColors, HealthcareUIMetrics, HealthcareVisualHelpers,
    HealthcareVisualComponents, UIAnimation, healthcare_visuals
)
from part_4_healthcare.activities.healthcare_particle_effects import healthcare_particles
from part_4_healthcare.activities.healthcare_feedback_popups import healthcare_feedback


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
        self.confirm_button = pygame.Rect(540, 600, 200, 55)

        # Animation states
        self.card_animations = {}  # card_index -> animation data
        self.overlay_alpha = UIAnimation(0.0, 0.0, 0.3)
        self.content_scale = UIAnimation(0.95, 0.95, 0.3)
        self.confirm_slide = UIAnimation(80, 80, 0.3)  # Slides up from below
        self.confirm_scale = UIAnimation(1.0, 1.0, 0.15)
        self.confirm_pulse_timer = 0.0

        # Result state
        self.show_result = False
        self.purchase_successful = False
        self.result_scale = UIAnimation(0.0, 0.0, 0.3)
        self.savings_counter = UIAnimation(0.0, 0.0, 0.5)
        self.confetti_spawned = False

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0
        self.instruction_alpha = UIAnimation(1.0, 1.0, 0.4)

        # Generic badge pulse
        self.generic_pulse_timer = 0.0

        # Budget meter
        self.budget_fill = UIAnimation(0.0, 0.0, 0.4)

        # Fonts
        self.title_font = pygame.font.Font(None, 40)
        self.card_font = pygame.font.Font(None, 26)
        self.price_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        self.badge_font = pygame.font.Font(None, 18)
        self.result_font = pygame.font.Font(None, 44)

    def create_medication_cards(self):
        """Create clickable medication cards with animations"""
        self.medication_cards = []
        self.card_animations = {}

        # Arrange in 3 columns, 2 rows
        for i, med in enumerate(self.medications):
            col = i % 3
            row = i // 3

            x = 220 + col * 290
            y = 210 + row * 185

            card = pygame.Rect(x, y, 260, 165)
            self.medication_cards.append({
                'rect': card,
                'medication': med,
                'selected': False,
                'hover': False,
                'index': i
            })

            # Staggered entrance animations
            delay = i * 0.08
            self.card_animations[i] = {
                'scale': UIAnimation(0.0, 1.0, 0.3),
                'alpha': UIAnimation(0.0, 1.0, 0.4),
                'hover_scale': UIAnimation(1.0, 1.0, 0.12),
                'selected_scale': UIAnimation(1.0, 1.0, 0.15),
                'checkmark_scale': UIAnimation(0.0, 0.0, 0.2),
                'fade_opacity': UIAnimation(1.0, 1.0, 0.3),  # For fading non-selected
            }

    def handle_event(self, event):
        """Handle medication selection"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEMOTION:
            # Update hover states
            for card in self.medication_cards:
                was_hover = card['hover']
                card['hover'] = card['rect'].collidepoint(mouse_pos) and not card['selected']

                anim = self.card_animations.get(card['index'])
                if anim:
                    if card['hover'] and not was_hover:
                        anim['hover_scale'].target = 1.04
                    elif not card['hover'] and was_hover:
                        anim['hover_scale'].target = 1.0

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check medication selection
            for card in self.medication_cards:
                if card['rect'].collidepoint(mouse_pos) and not self.show_result:
                    # Deselect all others
                    for c in self.medication_cards:
                        if c != card:
                            c['selected'] = False
                            anim = self.card_animations.get(c['index'])
                            if anim:
                                anim['checkmark_scale'].target = 0.0
                                anim['fade_opacity'].target = 0.6  # Fade others

                    # Select this card
                    card['selected'] = True
                    self.selected_medication = card['medication']

                    # Animation
                    anim = self.card_animations.get(card['index'])
                    if anim:
                        anim['selected_scale'].current = 1.08
                        anim['selected_scale'].target = 1.03
                        anim['checkmark_scale'].target = 1.0
                        anim['fade_opacity'].target = 1.0

                    # Show confirm button
                    self.confirm_slide.target = 0

                    # Particles and feedback
                    healthcare_particles.emit_pill(card['rect'].centerx, card['rect'].centery)
                    healthcare_particles.emit_sparkle(card['rect'].centerx, card['rect'].centery, count=10)
                    healthcare_feedback.add_text(card['rect'].centerx, card['rect'].y - 20, "Selected!",
                                                HealthcareUIColors.PRIMARY)

                    break

            # Check confirm button
            confirm_rect = self.confirm_button.copy()
            confirm_rect.y += self.confirm_slide.current
            if confirm_rect.collidepoint(mouse_pos) and self.selected_medication:
                self.process_purchase()

        return True

    def process_purchase(self):
        """Process the medication purchase"""
        self.show_result = True
        self.result_scale.target = 1.0

        # Check if selection meets criteria
        med = self.selected_medication
        if med['generic'] and med['price'] <= self.budget and med['dosage'] == '50mg':
            self.purchase_successful = True
            self.savings_counter.target = self.budget - med['price']

            # Emit success effects
            healthcare_particles.emit_confetti(self.SCREEN_WIDTH // 2, 350, count=50)
            healthcare_particles.emit_money_saved(self.SCREEN_WIDTH // 2, 300)
            healthcare_feedback.add_medication_selected()
            healthcare_feedback.add_savings(self.SCREEN_WIDTH // 2, 300, self.budget - med['price'])
        else:
            self.purchase_successful = False
            healthcare_particles.emit_error(self.SCREEN_WIDTH // 2, 350)

        self.completed = True

    def update(self, dt):
        """Update game state and animations"""
        if not self.active:
            return

        # Update all animations
        self.overlay_alpha.update(dt)
        self.content_scale.update(dt)
        self.confirm_slide.update(dt)
        self.confirm_scale.update(dt)
        self.result_scale.update(dt)
        self.savings_counter.update(dt)
        self.budget_fill.update(dt)
        self.instruction_alpha.update(dt)

        # Card animations
        for i, anim_data in self.card_animations.items():
            for anim in anim_data.values():
                if isinstance(anim, UIAnimation):
                    anim.update(dt)

        # Generic badge pulse
        self.generic_pulse_timer += dt

        # Confirm button pulse when visible
        if self.selected_medication and not self.show_result:
            self.confirm_pulse_timer += dt
            pulse = 1.0 + math.sin(self.confirm_pulse_timer * 3) * 0.03
            self.confirm_scale.current = pulse

        # Instruction fade
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 3:
                self.instruction_alpha.target = 0.0
            if self.instruction_timer > 4:
                self.show_instructions = False

        # Confetti on successful result
        if self.show_result and self.purchase_successful and not self.confetti_spawned:
            if self.result_scale.current > 0.8:
                self.confetti_spawned = True

        # Update particles and feedback
        healthcare_particles.update(dt)
        healthcare_feedback.update(dt)

    def render(self, screen):
        """Render the medication selection interface with visual polish"""
        if not self.active:
            return

        # Background overlay with gradient
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = HealthcareVisualHelpers.color_lerp(
                (248, 250, 252),
                (238, 242, 248),
                progress * 0.6
            )
            pygame.draw.line(overlay, (*color, 252), (0, y), (self.SCREEN_WIDTH, y))
        screen.blit(overlay, (0, 0))

        # Header bar
        header_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, 80)
        header_surface = pygame.Surface((header_rect.width, header_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(header_surface, (*HealthcareUIColors.PRIMARY, 240), header_surface.get_rect())
        screen.blit(header_surface, header_rect.topleft)

        # Title
        title_text = self.title_font.render("Pharmacy - Select Your Medication", True, (255, 255, 255))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 25))

        # ESC hint
        esc_text = self.small_font.render("Press ESC to exit", True, (180, 190, 200))
        screen.blit(esc_text, (20, self.SCREEN_HEIGHT - 30))

        # Requirements panel
        req_rect = pygame.Rect(180, 95, 920, 90)
        HealthcareVisualHelpers.draw_shadow(screen, req_rect, offset=4, blur_radius=8, alpha=30)
        pygame.draw.rect(screen, (255, 255, 255), req_rect, border_radius=10)
        pygame.draw.rect(screen, HealthcareUIColors.FORM_BORDER, req_rect, 1, border_radius=10)

        # Budget section
        budget_label = self.small_font.render("YOUR BUDGET", True, HealthcareUIColors.TEXT_SECONDARY)
        screen.blit(budget_label, (req_rect.x + 25, req_rect.y + 15))

        budget_value = self.price_font.render(f"${self.budget:.2f}", True, HealthcareUIColors.SUCCESS)
        screen.blit(budget_value, (req_rect.x + 25, req_rect.y + 35))

        # Budget meter
        meter_rect = pygame.Rect(req_rect.x + 25, req_rect.y + 70, 120, 8)
        healthcare_visuals.draw_progress_bar(screen, meter_rect, 1.0, color=HealthcareUIColors.SUCCESS)

        # Divider
        pygame.draw.line(screen, HealthcareUIColors.FORM_BORDER,
                        (req_rect.x + 170, req_rect.y + 15),
                        (req_rect.x + 170, req_rect.y + 75), 1)

        # Requirements
        req_label = self.small_font.render("REQUIREMENTS", True, HealthcareUIColors.TEXT_SECONDARY)
        screen.blit(req_label, (req_rect.x + 195, req_rect.y + 15))

        requirements = [
            ("Generic Version", HealthcareUIColors.GENERIC),
            ("50mg Dosage", HealthcareUIColors.PRIMARY),
            ("30-day Supply", HealthcareUIColors.SECONDARY)
        ]

        req_x = req_rect.x + 195
        for i, (req_text, color) in enumerate(requirements):
            # Pill-shaped badge
            badge_width = len(req_text) * 7 + 20
            badge_rect = pygame.Rect(req_x, req_rect.y + 40, badge_width, 24)

            pygame.draw.rect(screen, (*color, 30), badge_rect, border_radius=12)
            pygame.draw.rect(screen, color, badge_rect, 1, border_radius=12)

            text = self.badge_font.render(req_text, True, color)
            screen.blit(text, (badge_rect.centerx - text.get_width() // 2,
                              badge_rect.centery - text.get_height() // 2))

            req_x += badge_width + 12

        if not self.show_result:
            self._render_medication_cards(screen)
            self._render_confirm_button(screen)
            self._render_instructions(screen)
        else:
            self._render_result(screen)

        # Particles and feedback
        healthcare_particles.draw(screen)
        healthcare_feedback.draw(screen)

    def _render_medication_cards(self, screen):
        """Render medication cards with animations"""
        mouse_pos = pygame.mouse.get_pos()

        for card in self.medication_cards:
            idx = card['index']
            med = card['medication']
            anim = self.card_animations.get(idx, {})

            scale = anim.get('scale', UIAnimation(1.0, 1.0, 0.1)).current
            alpha = anim.get('alpha', UIAnimation(1.0, 1.0, 0.1)).current
            hover_scale = anim.get('hover_scale', UIAnimation(1.0, 1.0, 0.1)).current
            selected_scale = anim.get('selected_scale', UIAnimation(1.0, 1.0, 0.1)).current
            fade_opacity = anim.get('fade_opacity', UIAnimation(1.0, 1.0, 0.1)).current

            if scale < 0.01 or alpha < 0.01:
                continue

            total_scale = scale * hover_scale * selected_scale
            total_alpha = alpha * fade_opacity

            # Calculate scaled rect
            base_rect = card['rect']
            width = int(base_rect.width * total_scale)
            height = int(base_rect.height * total_scale)
            scaled_rect = pygame.Rect(
                base_rect.centerx - width // 2,
                base_rect.centery - height // 2,
                width,
                height
            )

            # Shadow
            shadow_offset = 6 if card['selected'] else 3
            HealthcareVisualHelpers.draw_shadow(screen, scaled_rect, offset=shadow_offset,
                                               blur_radius=10, alpha=int(40 * total_alpha))

            # Card surface
            card_surface = pygame.Surface((width, height), pygame.SRCALPHA)

            # Background color
            if card['selected']:
                bg_color = (235, 255, 235)
                border_color = HealthcareUIColors.SUCCESS
            elif card['hover']:
                bg_color = (245, 248, 255)
                border_color = HealthcareUIColors.PRIMARY
            else:
                bg_color = (255, 255, 255)
                border_color = HealthcareUIColors.FORM_BORDER

            pygame.draw.rect(card_surface, (*bg_color, int(255 * total_alpha)),
                           card_surface.get_rect(), border_radius=12)

            # Left accent stripe
            accent_color = HealthcareUIColors.GENERIC if med['generic'] else (180, 180, 190)
            accent_rect = pygame.Rect(0, 0, 6, height)
            pygame.draw.rect(card_surface, (*accent_color, int(255 * total_alpha)), accent_rect,
                           border_top_left_radius=12, border_bottom_left_radius=12)

            # Border
            pygame.draw.rect(card_surface, (*border_color, int(200 * total_alpha)),
                           card_surface.get_rect(), 2, border_radius=12)

            # Generic badge with pulse
            if med['generic']:
                pulse = 1.0 + math.sin(self.generic_pulse_timer * 2 + idx) * 0.05
                badge_width = int(65 * pulse)
                badge_rect = pygame.Rect(width - badge_width - 10, 10, badge_width, 22)

                pygame.draw.rect(card_surface, (*HealthcareUIColors.GENERIC, int(255 * total_alpha)),
                               badge_rect, border_radius=11)
                badge_text = self.badge_font.render("GENERIC", True, (255, 255, 255))
                badge_text.set_alpha(int(255 * total_alpha))
                card_surface.blit(badge_text, (badge_rect.centerx - badge_text.get_width() // 2,
                                              badge_rect.centery - badge_text.get_height() // 2))

            # Medication name
            name_text = self.card_font.render(med['name'], True, HealthcareUIColors.TEXT_PRIMARY)
            name_text.set_alpha(int(255 * total_alpha))
            card_surface.blit(name_text, (18, 15))

            # Price with affordability color
            affordable = med['price'] <= self.budget
            price_color = HealthcareUIColors.AFFORDABLE if affordable else HealthcareUIColors.EXPENSIVE
            price_text = self.price_font.render(f"${med['price']:.2f}", True, price_color)
            price_text.set_alpha(int(255 * total_alpha))
            card_surface.blit(price_text, (18, 45))

            # Affordability badge
            if affordable:
                aff_text = self.badge_font.render("AFFORDABLE", True, HealthcareUIColors.AFFORDABLE)
            else:
                aff_text = self.badge_font.render("OVER BUDGET", True, HealthcareUIColors.EXPENSIVE)
            aff_text.set_alpha(int(200 * total_alpha))
            card_surface.blit(aff_text, (18 + price_text.get_width() + 10, 52))

            # Dosage with highlight if correct
            dosage_str = f"{med['dosage']} × {med['doses_per_month']} doses"
            dosage_color = HealthcareUIColors.SUCCESS if med['dosage'] == '50mg' else HealthcareUIColors.TEXT_SECONDARY
            dosage_text = self.small_font.render(dosage_str, True, dosage_color)
            dosage_text.set_alpha(int(255 * total_alpha))
            card_surface.blit(dosage_text, (18, 90))

            # Description
            desc_text = self.small_font.render(med['description'], True, HealthcareUIColors.TEXT_SECONDARY)
            desc_text.set_alpha(int(180 * total_alpha))
            card_surface.blit(desc_text, (18, 115))

            # Selection checkmark
            checkmark_scale = anim.get('checkmark_scale', UIAnimation(0.0, 0.0, 0.1)).current
            if checkmark_scale > 0.01 and card['selected']:
                check_size = int(24 * checkmark_scale)
                check_x = width - check_size - 15
                check_y = height - check_size - 15

                # Circle background
                pygame.draw.circle(card_surface, (*HealthcareUIColors.SUCCESS, int(255 * total_alpha)),
                                 (check_x + check_size // 2, check_y + check_size // 2),
                                 check_size // 2 + 2)

                # Checkmark
                healthcare_visuals.draw_checkmark(card_surface, (check_x, check_y),
                                                 check_size, (255, 255, 255))

            screen.blit(card_surface, scaled_rect.topleft)

    def _render_confirm_button(self, screen):
        """Render the confirm/purchase button"""
        if not self.selected_medication:
            return

        slide_y = self.confirm_slide.current
        scale = self.confirm_scale.current

        btn_rect = pygame.Rect(
            self.confirm_button.centerx - self.confirm_button.width * scale / 2,
            self.confirm_button.centery - self.confirm_button.height * scale / 2 + slide_y,
            self.confirm_button.width * scale,
            self.confirm_button.height * scale
        )

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = btn_rect.collidepoint(mouse_pos)

        # Shadow
        HealthcareVisualHelpers.draw_shadow(screen, btn_rect, offset=4, blur_radius=8)

        # Button with glow on hover
        if is_hovered:
            glow_rect = btn_rect.inflate(12, 12)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*HealthcareUIColors.SECONDARY, 60),
                           glow_surface.get_rect(), border_radius=14)
            screen.blit(glow_surface, glow_rect.topleft)

        btn_color = HealthcareUIColors.SECONDARY if not is_hovered else (35, 155, 85)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=10)

        # Button text
        btn_text = self.card_font.render("PURCHASE", True, (255, 255, 255))
        screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2,
                              btn_rect.centery - btn_text.get_height() // 2))

        # Price preview
        price_preview = self.small_font.render(f"${self.selected_medication['price']:.2f}",
                                               True, (220, 255, 220))
        screen.blit(price_preview, (btn_rect.centerx - price_preview.get_width() // 2,
                                   btn_rect.bottom + 8))

    def _render_instructions(self, screen):
        """Render instructions overlay"""
        if not self.show_instructions or self.instruction_alpha.current < 0.01:
            return

        alpha = int(self.instruction_alpha.current * 255)

        inst_surface = pygame.Surface((700, 45), pygame.SRCALPHA)
        pygame.draw.rect(inst_surface, (30, 40, 50, int(alpha * 0.85)),
                        inst_surface.get_rect(), border_radius=8)

        inst_text = self.small_font.render(
            "Select a medication that is generic, affordable, and has the correct dosage",
            True, (255, 255, 255)
        )
        inst_text.set_alpha(alpha)
        inst_surface.blit(inst_text, (inst_surface.get_width() // 2 - inst_text.get_width() // 2, 13))

        screen.blit(inst_surface, (self.SCREEN_WIDTH // 2 - 350, 570))

    def _render_result(self, screen):
        """Render purchase result"""
        scale = self.result_scale.current
        if scale < 0.01:
            return

        # Dim background
        dim_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, int(150 * scale)))
        screen.blit(dim_surface, (0, 0))

        # Result card
        card_width = int(550 * scale)
        card_height = int(300 * scale)
        card_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - card_width // 2,
            self.SCREEN_HEIGHT // 2 - card_height // 2,
            card_width,
            card_height
        )

        # Shadow
        HealthcareVisualHelpers.draw_shadow(screen, card_rect, offset=12, blur_radius=20, alpha=80)

        if self.purchase_successful:
            self._render_success_result(screen, card_rect, scale)
        else:
            self._render_failure_result(screen, card_rect, scale)

    def _render_success_result(self, screen, card_rect, scale):
        """Render successful purchase result"""
        # Card with gradient
        card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        for y in range(card_rect.height):
            progress = y / card_rect.height
            color = HealthcareVisualHelpers.color_lerp(
                HealthcareUIColors.SUCCESS,
                (35, 165, 90),
                progress * 0.3
            )
            pygame.draw.line(card_surface, color, (0, y), (card_rect.width, y))

        pygame.draw.rect(card_surface, (255, 255, 255), card_surface.get_rect(), 3, border_radius=15)
        screen.blit(card_surface, card_rect.topleft)

        if scale > 0.5:
            # Success icon
            check_size = 50
            check_x = card_rect.centerx - check_size // 2
            check_y = card_rect.y + 25
            pygame.draw.circle(screen, (255, 255, 255, 200), (check_x + check_size // 2, check_y + check_size // 2), 30)
            healthcare_visuals.draw_checkmark(screen, (check_x + 10, check_y + 10), 30, HealthcareUIColors.SUCCESS)

            # Title
            title = self.result_font.render("Purchase Successful!", True, (255, 255, 255))
            screen.blit(title, (card_rect.centerx - title.get_width() // 2, card_rect.y + 90))

            # Details
            med = self.selected_medication
            details = [
                f"Medication: {med['name']}",
                f"Price: ${med['price']:.2f}",
            ]

            y = card_rect.y + 145
            for detail in details:
                text = self.card_font.render(detail, True, (240, 255, 240))
                screen.blit(text, (card_rect.centerx - text.get_width() // 2, y))
                y += 30

            # Savings with animated counter
            savings = self.savings_counter.current
            savings_text = self.price_font.render(f"You saved: ${savings:.2f}", True, (255, 255, 200))
            screen.blit(savings_text, (card_rect.centerx - savings_text.get_width() // 2, y + 10))

            # Final message
            msg = self.small_font.render("You have your medication for the month!", True, (255, 255, 255))
            screen.blit(msg, (card_rect.centerx - msg.get_width() // 2, card_rect.bottom - 40))

    def _render_failure_result(self, screen, card_rect, scale):
        """Render failed purchase result"""
        # Card with gradient
        card_surface = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        for y in range(card_rect.height):
            progress = y / card_rect.height
            color = HealthcareVisualHelpers.color_lerp(
                HealthcareUIColors.ERROR,
                (180, 60, 60),
                progress * 0.3
            )
            pygame.draw.line(card_surface, color, (0, y), (card_rect.width, y))

        pygame.draw.rect(card_surface, (255, 255, 255), card_surface.get_rect(), 3, border_radius=15)
        screen.blit(card_surface, card_rect.topleft)

        if scale > 0.5:
            # X icon
            x_size = 50
            x_x = card_rect.centerx - x_size // 2
            x_y = card_rect.y + 25
            pygame.draw.circle(screen, (255, 255, 255, 200), (x_x + x_size // 2, x_y + x_size // 2), 30)
            healthcare_visuals.draw_x_mark(screen, x_x + 12, x_y + 12, 26, HealthcareUIColors.ERROR)

            # Title
            title = self.result_font.render("Wrong Choice!", True, (255, 255, 255))
            screen.blit(title, (card_rect.centerx - title.get_width() // 2, card_rect.y + 90))

            # Reason
            med = self.selected_medication
            if not med['generic']:
                reason = "This is a brand name, not generic!"
            elif med['price'] > self.budget:
                reason = f"Too expensive! You only have ${self.budget:.2f}"
            elif med['dosage'] != '50mg':
                reason = "Wrong dosage! You need 50mg"
            else:
                reason = "This doesn't meet the requirements"

            y = card_rect.y + 145
            selected_text = self.card_font.render(f"You selected: {med['name']}", True, (255, 220, 220))
            screen.blit(selected_text, (card_rect.centerx - selected_text.get_width() // 2, y))
            y += 35

            reason_text = self.card_font.render(reason, True, (255, 255, 200))
            screen.blit(reason_text, (card_rect.centerx - reason_text.get_width() // 2, y))

            # Message
            msg_lines = [
                "You'll have to manage without medication",
                "until your insurance is restored."
            ]
            y = card_rect.bottom - 70
            for line in msg_lines:
                msg = self.small_font.render(line, True, (255, 255, 255))
                screen.blit(msg, (card_rect.centerx - msg.get_width() // 2, y))
                y += 22

    def start(self):
        """Start the medication selection mini-game"""
        self.active = True
        self.completed = False
        self.selected_medication = None
        self.show_instructions = True
        self.instruction_timer = 0
        self.show_result = False
        self.purchase_successful = False
        self.confetti_spawned = False

        # Reset animations
        self.overlay_alpha = UIAnimation(0.0, 1.0, 0.3)
        self.content_scale = UIAnimation(0.95, 1.0, 0.3)
        self.confirm_slide = UIAnimation(80, 80, 0.3)
        self.confirm_scale = UIAnimation(1.0, 1.0, 0.15)
        self.confirm_pulse_timer = 0.0
        self.result_scale = UIAnimation(0.0, 0.0, 0.3)
        self.savings_counter = UIAnimation(0.0, 0.0, 0.5)
        self.instruction_alpha = UIAnimation(1.0, 1.0, 0.4)
        self.generic_pulse_timer = 0.0

        # Create fresh cards
        self.create_medication_cards()

        # Clear particles/feedback
        healthcare_particles.particles.clear()
        healthcare_feedback.popups.clear()
        healthcare_feedback.achievements.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Draw method (alias for render) - standard interface"""
        self.render(screen)

    def handle_key(self, key):
        """Handle keyboard input - ESC to exit"""
        if key == pygame.K_ESCAPE:
            self.completed = True
            self.active = False

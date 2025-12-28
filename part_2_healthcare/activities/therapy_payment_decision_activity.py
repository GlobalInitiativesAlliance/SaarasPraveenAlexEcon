"""
Therapy Payment Decision Activity
Interactive budget and decision-making interface for choosing therapy payment option
"""
import pygame
import math

class TherapyPaymentDecisionActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Activity state
        self.decision_stage = "budget_overview"  # budget_overview, decision_options, impact_preview, confirmation
        self.current_selection = None
        self.hovered_option = None
        self.decision_timer = 0
        self.animation_timer = 0
        self.budget_animation_progress = 0
        self.stress_level = 60  # Starting stress level
        self.health_level = 70  # Starting mental health level

        # Budget information
        self.budget_data = {
            "weekly_income": 200,
            "rent_monthly": 450,
            "food_weekly": 50,
            "utilities_monthly": 80,
            "current_savings": 125,
            "therapy_full_price": 150,
            "therapy_sliding_scale": 40,
            "days_until_rent": 14
        }

        # Decision options
        self.payment_options = [
            {
                "id": "sliding_scale",
                "title": "Sliding Scale Program",
                "cost": 40,
                "description": "Income-based fee for former foster youth",
                "pros": [
                    "Affordable monthly payment",
                    "Continue regular therapy schedule",
                    "Designed specifically for your situation",
                    "Maintains treatment continuity"
                ],
                "cons": [
                    "Requires income documentation",
                    "Limited appointment slots"
                ],
                "budget_impact": {
                    "remaining_funds": 85,
                    "stress_change": -20,
                    "health_change": +15,
                    "rent_risk": "low"
                },
                "color": (100, 200, 150),
                "recommendation": "ideal"
            },
            {
                "id": "cancel_appointment",
                "title": "Cancel Appointment",
                "cost": 0,
                "description": "Reschedule when insurance coverage returns",
                "pros": [
                    "No immediate financial cost",
                    "Preserve savings for rent",
                    "Can reschedule in two weeks"
                ],
                "cons": [
                    "Mental health may deteriorate",
                    "Break in treatment routine",
                    "Risk of crisis without support",
                    "Uncertainty about future coverage"
                ],
                "budget_impact": {
                    "remaining_funds": 125,
                    "stress_change": +30,
                    "health_change": -25,
                    "rent_risk": "none"
                },
                "color": (255, 180, 100),
                "recommendation": "risky"
            },
            {
                "id": "full_price",
                "title": "Pay Full Price",
                "cost": 150,
                "description": "Out-of-pocket payment for therapy session",
                "pros": [
                    "Keep therapy appointment",
                    "Maintain treatment schedule",
                    "No paperwork delays"
                ],
                "cons": [
                    "Severely strains budget",
                    "Risk unable to pay rent",
                    "May need to skip meals",
                    "Creates financial stress"
                ],
                "budget_impact": {
                    "remaining_funds": -25,
                    "stress_change": +40,
                    "health_change": +5,
                    "rent_risk": "high"
                },
                "color": (255, 120, 120),
                "recommendation": "dangerous"
            }
        ]

        # UI elements
        self.main_panel_rect = pygame.Rect(50, 50, 1180, 620)
        self.budget_panel_rect = pygame.Rect(80, 100, 500, 300)
        self.options_panel_rect = pygame.Rect(600, 100, 600, 500)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.YELLOW = (255, 215, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (240, 240, 240)
        self.DARK_GRAY = (60, 60, 70)
        self.PANEL_BG = (250, 252, 255)
        self.STRESS_RED = (220, 60, 60)
        self.HEALTH_GREEN = (80, 180, 80)

        # Fonts
        self.font_title = pygame.font.Font(None, 42)
        self.font_header = pygame.font.Font(None, 32)
        self.font_content = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 36)
        self.font_budget = pygame.font.Font(None, 28)

        # Animation timers
        self.pulse_timer = 0
        self.slide_animation = 0
        self.meter_animation = 0
        self.glow_timer = 0
        self.shake_timer = 0
        self.type_writer_timer = 0
        self.type_writer_progress = 0

    def start(self):
        """Start the therapy payment decision activity"""
        print("[PAYMENT_DECISION] Activity starting...")
        self.active = True
        self.completed = False
        self.decision_stage = "budget_overview"
        self.current_selection = None
        self.hovered_option = None
        self.decision_timer = 0
        self.animation_timer = 0
        self.budget_animation_progress = 0
        self.stress_level = 60
        self.health_level = 70
        self.pulse_timer = 0
        self.slide_animation = 0
        self.meter_animation = 0
        print("[PAYMENT_DECISION] Activity started successfully!")

    def stop(self):
        """Stop the therapy payment decision activity"""
        print("[PAYMENT_DECISION] Activity stopping...")
        self.active = False

    def handle_event(self, event):
        """Handle player input"""
        print(f"[PAYMENT_DECISION] handle_event called: active={self.active}, completed={self.completed}, event_type={event.type}")

        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            print(f"[PAYMENT_DECISION] Mouse click at {mouse_pos}")

            if self.decision_stage == "budget_overview":
                # Click anywhere to proceed to options
                self.decision_stage = "decision_options"
                self.slide_animation = 1.0
            elif self.decision_stage == "decision_options":
                # Check option selection
                self.handle_option_click(mouse_pos)
            elif self.decision_stage == "impact_preview":
                # Proceed to confirmation
                self.decision_stage = "confirmation"
                self.decision_timer = 3.0
            elif self.decision_stage == "confirmation":
                # Complete activity
                self.complete_activity()

        elif event.type == pygame.KEYDOWN:
            print(f"[PAYMENT_DECISION] Key pressed: {event.key}")
            if event.key == pygame.K_SPACE:
                if self.decision_stage == "budget_overview":
                    self.decision_stage = "decision_options"
                    self.slide_animation = 1.0
                elif self.decision_stage == "impact_preview":
                    self.decision_stage = "confirmation"
                    self.decision_timer = 3.0
                elif self.decision_stage == "confirmation":
                    self.complete_activity()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        elif event.type == pygame.MOUSEMOTION:
            # Handle option hovering
            if self.decision_stage == "decision_options":
                self.handle_option_hover(event.pos)

        return True

    def handle_mouse_click(self, pos, button):
        """Handle mouse click events from main game engine"""
        print(f"[PAYMENT_DECISION] handle_mouse_click called: pos={pos}, button={button}")
        if button == 1:
            event = type('Event', (), {'type': pygame.MOUSEBUTTONDOWN, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_mouse_release(self, pos, button):
        """Handle mouse release events from main game engine"""
        print(f"[PAYMENT_DECISION] handle_mouse_release called: pos={pos}, button={button}")
        if button == 1:
            event = type('Event', (), {'type': pygame.MOUSEBUTTONUP, 'button': 1, 'pos': pos})()
            self.handle_event(event)

    def handle_option_click(self, mouse_pos):
        """Handle clicking on payment options"""
        option_start_y = 200
        option_height = 120
        option_spacing = 30

        for i, option in enumerate(self.payment_options):
            option_y = option_start_y + (i * (option_height + option_spacing))
            option_rect = pygame.Rect(self.options_panel_rect.x + 20, option_y,
                                    self.options_panel_rect.width - 40, option_height)

            if option_rect.collidepoint(mouse_pos):
                print(f"[PAYMENT_DECISION] Selected option: {option['title']}")
                self.current_selection = i
                self.update_meters_for_selection(option)
                self.decision_stage = "impact_preview"
                self.meter_animation = 1.5  # Animate meters

    def handle_option_hover(self, mouse_pos):
        """Handle hovering over payment options"""
        option_start_y = 200
        option_height = 120
        option_spacing = 30
        old_hover = self.hovered_option

        self.hovered_option = None
        for i, option in enumerate(self.payment_options):
            option_y = option_start_y + (i * (option_height + option_spacing))
            option_rect = pygame.Rect(self.options_panel_rect.x + 20, option_y,
                                    self.options_panel_rect.width - 40, option_height)

            if option_rect.collidepoint(mouse_pos):
                self.hovered_option = i
                break

        # Trigger hover animation if changed
        if old_hover != self.hovered_option and self.hovered_option is not None:
            self.pulse_timer = 0

    def update_meters_for_selection(self, option):
        """Update stress and health meters based on selection"""
        impact = option["budget_impact"]

        # Update stress level
        new_stress = max(0, min(100, self.stress_level + impact["stress_change"]))
        self.stress_level = new_stress

        # Update health level
        new_health = max(0, min(100, self.health_level + impact["health_change"]))
        self.health_level = new_health

        # Trigger shake effect for high-stress decisions
        if impact["stress_change"] > 20 or option["recommendation"] == "dangerous":
            self.shake_timer = 2.0

    def complete_activity(self):
        """Complete the therapy payment decision activity"""
        print("[PAYMENT_DECISION] Completing activity...")

        if self.current_selection is not None:
            selected_option = self.payment_options[self.current_selection]
            print(f"[PAYMENT_DECISION] Player chose: {selected_option['title']}")

        self.completed = True

        if self.objective_manager:
            print("[PAYMENT_DECISION] Completed therapy payment decision...")
            self.objective_manager.complete_current_objective()

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update animation timers
        self.pulse_timer += dt
        self.animation_timer += dt
        self.glow_timer += dt * 2
        self.type_writer_timer += dt

        # Budget overview animation
        if self.decision_stage == "budget_overview":
            self.budget_animation_progress = min(1.0, self.budget_animation_progress + dt * 0.8)
            # Add typewriter effect for text
            self.type_writer_progress = min(1.0, self.type_writer_progress + dt * 2.0)

        # Slide animation
        if self.slide_animation > 0:
            self.slide_animation = max(0, self.slide_animation - dt * 1.5)

        # Meter animation
        if self.meter_animation > 0:
            self.meter_animation = max(0, self.meter_animation - dt * 0.7)

        # Shake animation for high stress decisions
        if self.shake_timer > 0:
            self.shake_timer = max(0, self.shake_timer - dt * 3)

        # Decision timer for confirmation
        if self.decision_stage == "confirmation" and self.decision_timer > 0:
            self.decision_timer -= dt

    def draw_background(self, screen):
        """Draw professional background with subtle animation"""
        # Animated gradient background
        for y in range(screen.get_height()):
            progress = y / screen.get_height()
            # Add subtle wave animation
            wave = math.sin((y * 0.02) + (self.glow_timer * 0.5)) * 5
            r = int(240 - progress * 20 + wave)
            g = int(245 - progress * 15 + wave)
            b = int(250 - progress * 10 + wave)
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))

        # Shake effect for stress
        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_timer > 0:
            shake_intensity = int(self.shake_timer * 10)
            shake_offset_x = int(math.sin(self.glow_timer * 20) * shake_intensity)
            shake_offset_y = int(math.cos(self.glow_timer * 25) * shake_intensity)

        # Main panel with subtle glow
        panel_rect = pygame.Rect(
            self.main_panel_rect.x + shake_offset_x,
            self.main_panel_rect.y + shake_offset_y,
            self.main_panel_rect.width,
            self.main_panel_rect.height
        )

        # Glow effect
        glow_alpha = int(50 + math.sin(self.glow_timer) * 20)
        glow_surface = pygame.Surface((panel_rect.width + 20, panel_rect.height + 20), pygame.SRCALPHA)
        glow_surface.fill((200, 220, 255, glow_alpha))
        screen.blit(glow_surface, (panel_rect.x - 10, panel_rect.y - 10))

        # Main panel
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((255, 255, 255, 250))
        screen.blit(panel_surface, (panel_rect.x, panel_rect.y))

        # Panel border with glow
        border_color = (180 + int(math.sin(self.glow_timer) * 20), 190, 220)
        pygame.draw.rect(screen, border_color, panel_rect, 3, border_radius=15)
        pygame.draw.rect(screen, (240, 245, 250), panel_rect, 1, border_radius=15)

    def draw_header(self, screen):
        """Draw activity header"""
        if self.decision_stage == "budget_overview":
            title = "Financial Situation Overview"
            subtitle = "Understanding your current budget before making a decision"
        elif self.decision_stage == "decision_options":
            title = "Therapy Payment Options"
            subtitle = "Choose how to handle tomorrow's therapy appointment"
        elif self.decision_stage == "impact_preview":
            title = "Decision Impact Preview"
            subtitle = "See how your choice affects your budget and wellbeing"
        else:  # confirmation
            title = "Decision Confirmed"
            subtitle = "Your choice has been recorded"

        # Title
        title_surface = self.font_title.render(title, True, (50, 70, 90))
        title_rect = title_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 80))
        screen.blit(title_surface, title_rect)

        # Subtitle
        subtitle_surface = self.font_content.render(subtitle, True, (100, 120, 140))
        subtitle_rect = subtitle_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 110))
        screen.blit(subtitle_surface, subtitle_rect)

    def draw_budget_overview(self, screen):
        """Draw budget overview with animated bars"""
        if self.decision_stage != "budget_overview":
            return

        # Budget panel background
        panel_surface = pygame.Surface((self.budget_panel_rect.width, self.budget_panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((250, 252, 255, 200))
        screen.blit(panel_surface, (self.budget_panel_rect.x, self.budget_panel_rect.y))
        pygame.draw.rect(screen, (180, 190, 200), self.budget_panel_rect, 2, border_radius=10)

        # Budget header
        header_text = self.font_header.render("Current Financial Situation", True, (60, 80, 100))
        screen.blit(header_text, (self.budget_panel_rect.x + 20, self.budget_panel_rect.y + 20))

        # Budget items with animated bars
        items = [
            ("Weekly Income", self.budget_data["weekly_income"], 200, self.GREEN),
            ("Current Savings", self.budget_data["current_savings"], 200, self.BLUE),
            ("Weekly Food Budget", self.budget_data["food_weekly"], 200, self.YELLOW),
            ("Monthly Rent", self.budget_data["rent_monthly"], 500, self.RED)
        ]

        start_y = self.budget_panel_rect.y + 70
        bar_height = 35
        spacing = 45

        for i, (label, amount, max_amount, color) in enumerate(items):
            y_pos = start_y + (i * spacing)

            # Label
            label_text = self.font_budget.render(label, True, (70, 90, 110))
            screen.blit(label_text, (self.budget_panel_rect.x + 30, y_pos))

            # Amount
            amount_text = self.font_budget.render(f"${amount}", True, (50, 70, 90))
            screen.blit(amount_text, (self.budget_panel_rect.x + 250, y_pos))

            # Animated progress bar
            bar_rect = pygame.Rect(self.budget_panel_rect.x + 320, y_pos + 5, 150, 20)
            pygame.draw.rect(screen, (230, 230, 235), bar_rect, border_radius=5)

            # Fill based on animation progress
            fill_width = int((amount / max_amount) * bar_rect.width * self.budget_animation_progress)
            if fill_width > 0:
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
                pygame.draw.rect(screen, color, fill_rect, border_radius=5)

            pygame.draw.rect(screen, (150, 160, 170), bar_rect, 1, border_radius=5)

        # Current situation summary
        summary_y = start_y + (len(items) * spacing) + 20
        summary_text = "You have $125 in savings. Rent is due in 2 weeks."
        summary_surface = self.font_content.render(summary_text, True, (80, 100, 120))
        screen.blit(summary_surface, (self.budget_panel_rect.x + 30, summary_y))

        # Continue instruction
        instruction_text = "Click anywhere or press SPACE to see payment options"
        instruction_surface = self.font_small.render(instruction_text, True, (120, 140, 160))
        instruction_rect = instruction_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 650))
        screen.blit(instruction_surface, instruction_rect)

    def draw_stress_health_meters(self, screen):
        """Draw stress and health meters"""
        if self.decision_stage in ["budget_overview"]:
            return

        meter_x = 50
        meter_y = 450
        meter_width = 200
        meter_height = 20

        # Stress meter
        stress_label = self.font_content.render("Stress Level", True, (70, 90, 110))
        screen.blit(stress_label, (meter_x, meter_y - 25))

        stress_bg = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
        pygame.draw.rect(screen, (240, 240, 240), stress_bg, border_radius=10)

        # Animated stress fill
        stress_fill_width = int((self.stress_level / 100) * meter_width)
        if self.meter_animation > 0:
            # Pulse effect during animation
            pulse = math.sin(self.meter_animation * 10) * 0.1 + 1.0
            stress_fill_width = int(stress_fill_width * pulse)

        if stress_fill_width > 0:
            stress_color = self.STRESS_RED if self.stress_level > 60 else self.YELLOW
            stress_fill = pygame.Rect(meter_x, meter_y, stress_fill_width, meter_height)
            pygame.draw.rect(screen, stress_color, stress_fill, border_radius=10)

        pygame.draw.rect(screen, (150, 160, 170), stress_bg, 2, border_radius=10)

        stress_text = f"{int(self.stress_level)}%"
        stress_surface = self.font_small.render(stress_text, True, (50, 70, 90))
        screen.blit(stress_surface, (meter_x + meter_width + 10, meter_y + 2))

        # Health meter
        health_y = meter_y + 50
        health_label = self.font_content.render("Mental Health", True, (70, 90, 110))
        screen.blit(health_label, (meter_x, health_y - 25))

        health_bg = pygame.Rect(meter_x, health_y, meter_width, meter_height)
        pygame.draw.rect(screen, (240, 240, 240), health_bg, border_radius=10)

        # Animated health fill
        health_fill_width = int((self.health_level / 100) * meter_width)
        if self.meter_animation > 0:
            pulse = math.sin(self.meter_animation * 10) * 0.1 + 1.0
            health_fill_width = int(health_fill_width * pulse)

        if health_fill_width > 0:
            health_color = self.HEALTH_GREEN if self.health_level > 50 else self.RED
            health_fill = pygame.Rect(meter_x, health_y, health_fill_width, meter_height)
            pygame.draw.rect(screen, health_color, health_fill, border_radius=10)

        pygame.draw.rect(screen, (150, 160, 170), health_bg, 2, border_radius=10)

        health_text = f"{int(self.health_level)}%"
        health_surface = self.font_small.render(health_text, True, (50, 70, 90))
        screen.blit(health_surface, (meter_x + meter_width + 10, health_y + 2))

    def draw_payment_options(self, screen):
        """Draw payment options with professional styling"""
        if self.decision_stage != "decision_options":
            return

        # Options header
        options_header = self.font_header.render("Choose Your Payment Option", True, (60, 80, 100))
        header_rect = options_header.get_rect(center=(self.options_panel_rect.centerx, self.options_panel_rect.y - 20))
        screen.blit(options_header, header_rect)

        # Draw each option
        option_start_y = 200
        option_height = 120
        option_spacing = 30

        for i, option in enumerate(self.payment_options):
            option_y = option_start_y + (i * (option_height + option_spacing))
            option_rect = pygame.Rect(self.options_panel_rect.x + 20, option_y,
                                    self.options_panel_rect.width - 40, option_height)

            # Enhanced hover and glow effects
            is_hovered = self.hovered_option == i
            hover_alpha = 255
            hover_scale = 1.0

            if is_hovered:
                hover_alpha = int(220 + math.sin(self.pulse_timer * 8) * 35)
                hover_scale = 1.02 + math.sin(self.pulse_timer * 6) * 0.01

                # Add glow for hovered option
                glow_rect = option_rect.inflate(10, 10)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                glow_alpha = int(80 + math.sin(self.pulse_timer * 10) * 40)
                glow_surface.fill((*option["color"], glow_alpha))
                screen.blit(glow_surface, (glow_rect.x, glow_rect.y))

            # Scale for hover effect
            if hover_scale != 1.0:
                scaled_width = int(option_rect.width * hover_scale)
                scaled_height = int(option_rect.height * hover_scale)
                option_rect = pygame.Rect(
                    option_rect.centerx - scaled_width // 2,
                    option_rect.centery - scaled_height // 2,
                    scaled_width,
                    scaled_height
                )

            # Option background
            bg_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)

            if option["recommendation"] == "ideal":
                bg_color = (240, 255, 245, hover_alpha)
                border_color = option["color"]
                border_width = 3
            elif option["recommendation"] == "dangerous":
                bg_color = (255, 240, 240, hover_alpha)
                border_color = option["color"]
                border_width = 2
            else:
                bg_color = (250, 248, 245, hover_alpha)
                border_color = option["color"]
                border_width = 2

            bg_surface.fill(bg_color)
            screen.blit(bg_surface, (option_rect.x, option_rect.y))
            pygame.draw.rect(screen, border_color, option_rect, border_width, border_radius=12)

            # Recommendation badge
            if option["recommendation"] == "ideal":
                badge_rect = pygame.Rect(option_rect.right - 120, option_rect.y + 10, 100, 25)
                pygame.draw.rect(screen, (34, 139, 34), badge_rect, border_radius=12)
                badge_text = self.font_small.render("RECOMMENDED", True, (255, 255, 255))
                badge_text_rect = badge_text.get_rect(center=badge_rect.center)
                screen.blit(badge_text, badge_text_rect)
            elif option["recommendation"] == "dangerous":
                badge_rect = pygame.Rect(option_rect.right - 100, option_rect.y + 10, 80, 25)
                pygame.draw.rect(screen, (200, 60, 60), badge_rect, border_radius=12)
                badge_text = self.font_small.render("RISKY", True, (255, 255, 255))
                badge_text_rect = badge_text.get_rect(center=badge_rect.center)
                screen.blit(badge_text, badge_text_rect)

            # Option title and cost
            title_text = self.font_large.render(option["title"], True, (50, 70, 90))
            cost_text = self.font_header.render(f"${option['cost']}", True, option["color"])

            screen.blit(title_text, (option_rect.x + 20, option_rect.y + 15))
            cost_rect = cost_text.get_rect(right=option_rect.right - 20, top=option_rect.y + 15)
            screen.blit(cost_text, cost_rect)

            # Description
            desc_text = self.font_content.render(option["description"], True, (80, 100, 120))
            screen.blit(desc_text, (option_rect.x + 20, option_rect.y + 50))

            # Quick pros/cons summary
            if len(option["pros"]) > 0:
                pro_text = f"✓ {option['pros'][0]}"
                pro_surface = self.font_small.render(pro_text, True, (60, 140, 60))
                screen.blit(pro_surface, (option_rect.x + 20, option_rect.y + 75))

            if len(option["cons"]) > 0:
                con_text = f"⚠ {option['cons'][0]}"
                con_surface = self.font_small.render(con_text, True, (140, 90, 60))
                screen.blit(con_surface, (option_rect.x + 20, option_rect.y + 95))

    def draw_impact_preview(self, screen):
        """Draw impact preview of selected decision"""
        if self.decision_stage != "impact_preview" or self.current_selection is None:
            return

        option = self.payment_options[self.current_selection]
        impact = option["budget_impact"]

        # Impact panel
        impact_rect = pygame.Rect(300, 200, 680, 320)
        pygame.draw.rect(screen, (255, 255, 255), impact_rect, border_radius=15)
        pygame.draw.rect(screen, option["color"], impact_rect, 3, border_radius=15)

        # Selected option header
        header_text = f"Impact of: {option['title']}"
        header_surface = self.font_header.render(header_text, True, (50, 70, 90))
        header_rect = header_surface.get_rect(center=(impact_rect.centerx, impact_rect.y + 40))
        screen.blit(header_surface, header_rect)

        # Budget impact
        budget_y = impact_rect.y + 80
        budget_header = self.font_budget.render("Financial Impact:", True, (70, 90, 110))
        screen.blit(budget_header, (impact_rect.x + 40, budget_y))

        remaining_text = f"Remaining funds after payment: ${impact['remaining_funds']}"
        remaining_color = self.GREEN if impact["remaining_funds"] > 0 else self.RED
        remaining_surface = self.font_content.render(remaining_text, True, remaining_color)
        screen.blit(remaining_surface, (impact_rect.x + 40, budget_y + 30))

        # Wellbeing impact
        wellbeing_y = budget_y + 80
        wellbeing_header = self.font_budget.render("Wellbeing Impact:", True, (70, 90, 110))
        screen.blit(wellbeing_header, (impact_rect.x + 40, wellbeing_y))

        stress_change = impact["stress_change"]
        stress_symbol = "↓" if stress_change < 0 else "↑"
        stress_color = self.GREEN if stress_change < 0 else self.RED
        stress_text = f"Stress level: {stress_symbol} {abs(stress_change)}%"
        stress_surface = self.font_content.render(stress_text, True, stress_color)
        screen.blit(stress_surface, (impact_rect.x + 40, wellbeing_y + 30))

        health_change = impact["health_change"]
        health_symbol = "↑" if health_change > 0 else "↓"
        health_color = self.GREEN if health_change > 0 else self.RED
        health_text = f"Mental health: {health_symbol} {abs(health_change)}%"
        health_surface = self.font_content.render(health_text, True, health_color)
        screen.blit(health_surface, (impact_rect.x + 40, wellbeing_y + 60))

        # Risk assessment
        risk_y = wellbeing_y + 110
        risk_header = self.font_budget.render("Risk Assessment:", True, (70, 90, 110))
        screen.blit(risk_header, (impact_rect.x + 40, risk_y))

        risk_level = impact["rent_risk"]
        risk_colors = {"none": self.GREEN, "low": self.YELLOW, "high": self.RED}
        risk_text = f"Risk of missing rent payment: {risk_level.upper()}"
        risk_surface = self.font_content.render(risk_text, True, risk_colors.get(risk_level, self.GRAY))
        screen.blit(risk_surface, (impact_rect.x + 40, risk_y + 30))

        # Confirmation instruction
        confirm_text = "Click anywhere or press SPACE to confirm this decision"
        confirm_surface = self.font_small.render(confirm_text, True, (120, 140, 160))
        confirm_rect = confirm_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 650))
        screen.blit(confirm_surface, confirm_rect)

    def draw_confirmation(self, screen):
        """Draw decision confirmation"""
        if self.decision_stage != "confirmation" or self.current_selection is None:
            return

        option = self.payment_options[self.current_selection]

        # Confirmation overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Confirmation panel
        panel_rect = pygame.Rect(300, 250, 680, 220)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, border_radius=20)
        pygame.draw.rect(screen, option["color"], panel_rect, 4, border_radius=20)

        # Confirmation text
        confirm_title = self.font_title.render("Decision Confirmed", True, (50, 70, 90))
        title_rect = confirm_title.get_rect(center=(panel_rect.centerx, panel_rect.y + 50))
        screen.blit(confirm_title, title_rect)

        # Selected option
        option_text = f"You chose: {option['title']} (${option['cost']})"
        option_surface = self.font_header.render(option_text, True, option["color"])
        option_rect = option_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 100))
        screen.blit(option_surface, option_rect)

        # Outcome message
        outcome_messages = {
            "sliding_scale": "A wise choice that balances your mental health needs with financial reality.",
            "cancel_appointment": "Sometimes difficult choices are necessary. Your mental health support network is still available.",
            "full_price": "Prioritizing your mental health is important, though this choice may require careful budgeting ahead."
        }

        outcome_text = outcome_messages.get(option["id"], "Your decision has been recorded.")
        outcome_surface = self.font_content.render(outcome_text, True, (70, 90, 110))

        # Word wrap for longer messages
        words = outcome_text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font_content.size(test_line)[0] < panel_rect.width - 60:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        outcome_y = panel_rect.y + 140
        for line in lines:
            line_surface = self.font_content.render(line, True, (70, 90, 110))
            line_rect = line_surface.get_rect(center=(panel_rect.centerx, outcome_y))
            screen.blit(line_surface, line_rect)
            outcome_y += 25

        # Continue instruction
        if self.decision_timer <= 0:
            continue_text = "Click anywhere or press SPACE to continue"
            continue_surface = self.font_small.render(continue_text, True, (120, 140, 160))
            continue_rect = continue_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 30))
            screen.blit(continue_surface, continue_rect)

    def draw(self, screen):
        """Render the therapy payment decision interface"""
        if not self.active:
            return

        # Draw background and main layout
        self.draw_background(screen)
        self.draw_header(screen)

        # Draw stage-specific content
        self.draw_budget_overview(screen)
        self.draw_stress_health_meters(screen)
        self.draw_payment_options(screen)
        self.draw_impact_preview(screen)
        self.draw_confirmation(screen)

        # Debug: Show current stage
        debug_text = f"Stage: {self.decision_stage}"
        debug_surface = self.font_small.render(debug_text, True, (150, 150, 150))
        screen.blit(debug_surface, (10, 10))
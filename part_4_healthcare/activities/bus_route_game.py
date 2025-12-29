"""
Bus Route Selection Mini-Game
Choose the correct bus route within 20 seconds to make appointment
"""
import pygame
import random

class BusRouteGame:
    """Select the correct bus within time limit or miss appointment"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.failed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 20.0  # seconds
        self.time_remaining = self.time_limit
        self.timer_color = (100, 200, 100)

        # Bus routes
        self.bus_routes = [
            {'number': '14', 'route': 'Downtown → West Side', 'stops': 'School, Mall, Hospital'},
            {'number': '27', 'route': 'North Loop', 'stops': 'University, Park, Library'},
            {'number': '38', 'route': 'Cross-Town Express', 'stops': 'School, Clinic, Downtown'},
            {'number': '42', 'route': 'South Central', 'stops': 'Mall, Apartments, Market'},
            {'number': '51', 'route': 'East Circle', 'stops': 'Station, School, Shops'},
            {'number': '63', 'route': 'Medical District', 'stops': 'Hospital, Clinic, Pharmacy'}
        ]

        # Correct route (38 goes to clinic)
        self.correct_route_index = 2

        # UI elements
        self.route_buttons = []
        self.create_route_buttons()

        # Instructions
        self.show_instructions = True
        self.instruction_timer = 0

        # Result display
        self.show_result = False
        self.result_timer = 0

        # Destination info
        self.destination = "Community Health Clinic"
        self.current_location = "School"

    def create_route_buttons(self):
        """Create clickable bus route buttons"""
        self.route_buttons = []

        # Arrange in 2 columns, 3 rows
        for i, route in enumerate(self.bus_routes):
            col = i % 2
            row = i // 2

            x = 340 + col * 300
            y = 250 + row * 120
            rect = pygame.Rect(x, y, 280, 100)

            self.route_buttons.append({
                'rect': rect,
                'route': route,
                'index': i,
                'selected': False,
                'hover': False
            })

    def handle_event(self, event):
        """Handle bus selection"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEMOTION:
            # Update hover states
            for button in self.route_buttons:
                button['hover'] = button['rect'].collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check bus selection
            for button in self.route_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    button['selected'] = True

                    # Check if correct
                    if button['index'] == self.correct_route_index:
                        self.completed = True
                        self.show_result = True
                        self.result_timer = 120

                        if self.objective_manager:
                            self.objective_manager.complete_objective("catch_bus")
                    else:
                        self.failed = True
                        self.completed = True
                        self.show_result = True
                        self.result_timer = 120

                    break

        return True

    def update(self, dt):
        """Update timer and game state"""
        if not self.active or self.completed:
            if self.show_result and self.result_timer > 0:
                self.result_timer -= 1
            return

        # Update instruction timer
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 3:
                self.show_instructions = False

        # Update countdown timer
        self.time_remaining -= dt

        # Update timer color based on urgency
        if self.time_remaining < 5:
            self.timer_color = (255, 100, 100)  # Red
        elif self.time_remaining < 10:
            self.timer_color = (255, 200, 100)  # Orange
        else:
            self.timer_color = (100, 200, 100)  # Green

        # Check for timeout
        if self.time_remaining <= 0:
            self.failed = True
            self.completed = True
            self.show_result = True
            self.result_timer = 120
            self.time_remaining = 0

    def render(self, screen):
        """Render the bus route selection interface"""
        if not self.active:
            return

        # Background overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(240)
        overlay.fill((20, 30, 40))
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("QUICK! Select the Right Bus!", True, (255, 255, 255))
        screen.blit(title_text, (self.SCREEN_WIDTH//2 - title_text.get_width()//2, 50))

        # ESC hint
        esc_font = pygame.font.Font(None, 24)
        esc_text = esc_font.render("Press ESC to exit", True, (150, 150, 150))
        screen.blit(esc_text, (20, self.SCREEN_HEIGHT - 40))

        # Destination info
        info_font = pygame.font.Font(None, 32)
        location_text = info_font.render(f"Current Location: {self.current_location}", True, (200, 200, 200))
        dest_text = info_font.render(f"Destination: {self.destination}", True, (255, 255, 150))
        screen.blit(location_text, (self.SCREEN_WIDTH//2 - location_text.get_width()//2, 110))
        screen.blit(dest_text, (self.SCREEN_WIDTH//2 - dest_text.get_width()//2, 145))

        # Timer
        timer_font = pygame.font.Font(None, 64)
        timer_text = timer_font.render(f"{self.time_remaining:.1f}", True, self.timer_color)
        timer_x = self.SCREEN_WIDTH//2 - timer_text.get_width()//2
        timer_y = 180
        screen.blit(timer_text, (timer_x, timer_y))

        # Timer label
        label_font = pygame.font.Font(None, 24)
        label_text = label_font.render("seconds remaining", True, (150, 150, 150))
        screen.blit(label_text, (self.SCREEN_WIDTH//2 - label_text.get_width()//2, timer_y + 45))

        if not self.show_result:
            # Bus route buttons
            button_font = pygame.font.Font(None, 28)
            small_font = pygame.font.Font(None, 22)

            for button in self.route_buttons:
                # Button background
                if button['selected']:
                    color = (100, 150, 100) if button['index'] == self.correct_route_index else (150, 50, 50)
                elif button['hover']:
                    color = (80, 120, 160)
                else:
                    color = (60, 90, 120)

                pygame.draw.rect(screen, color, button['rect'])
                pygame.draw.rect(screen, (100, 100, 100), button['rect'], 2)

                # Bus number (large)
                route = button['route']
                number_font = pygame.font.Font(None, 48)
                number_text = number_font.render(f"#{route['number']}", True, (255, 255, 255))
                screen.blit(number_text, (button['rect'].x + 10, button['rect'].y + 10))

                # Route name
                route_text = button_font.render(route['route'], True, (255, 255, 255))
                screen.blit(route_text, (button['rect'].x + 10, button['rect'].y + 45))

                # Stops
                stops_text = small_font.render(route['stops'], True, (200, 200, 200))
                screen.blit(stops_text, (button['rect'].x + 10, button['rect'].y + 70))

            # Instructions
            if self.show_instructions:
                inst_text = info_font.render("Click the bus that goes to the clinic!", True, (200, 255, 200))
                screen.blit(inst_text, (self.SCREEN_WIDTH//2 - inst_text.get_width()//2, 600))

        else:
            # Show result
            result_rect = pygame.Rect(self.SCREEN_WIDTH//2 - 250, self.SCREEN_HEIGHT//2 - 100, 500, 200)

            if self.failed:
                pygame.draw.rect(screen, (150, 50, 50), result_rect)
                pygame.draw.rect(screen, (255, 100, 100), result_rect, 3)

                result_font = pygame.font.Font(None, 48)
                if self.time_remaining <= 0:
                    result_text = result_font.render("TOO SLOW!", True, (255, 255, 255))
                    detail_text = "You missed your appointment!"
                else:
                    result_text = result_font.render("WRONG BUS!", True, (255, 255, 255))
                    detail_text = "You'll be late for your appointment!"

                screen.blit(result_text, (self.SCREEN_WIDTH//2 - result_text.get_width()//2, result_rect.y + 40))

                detail_font = pygame.font.Font(None, 28)
                detail = detail_font.render(detail_text, True, (255, 200, 200))
                screen.blit(detail, (self.SCREEN_WIDTH//2 - detail.get_width()//2, result_rect.y + 100))

                consequence = detail_font.render("Caseworker trust decreased", True, (255, 150, 150))
                screen.blit(consequence, (self.SCREEN_WIDTH//2 - consequence.get_width()//2, result_rect.y + 130))

            else:
                pygame.draw.rect(screen, (50, 150, 50), result_rect)
                pygame.draw.rect(screen, (100, 255, 100), result_rect, 3)

                result_font = pygame.font.Font(None, 48)
                result_text = result_font.render("CORRECT!", True, (255, 255, 255))
                screen.blit(result_text, (self.SCREEN_WIDTH//2 - result_text.get_width()//2, result_rect.y + 40))

                detail_font = pygame.font.Font(None, 28)
                detail = detail_font.render("Bus #38 will take you to the clinic!", True, (200, 255, 200))
                screen.blit(detail, (self.SCREEN_WIDTH//2 - detail.get_width()//2, result_rect.y + 100))

                success = detail_font.render("You'll make your appointment on time!", True, (150, 255, 150))
                screen.blit(success, (self.SCREEN_WIDTH//2 - success.get_width()//2, result_rect.y + 130))

    def start(self):
        """Start the bus route mini-game"""
        self.active = True
        self.completed = False
        self.failed = False
        self.time_remaining = self.time_limit
        self.show_instructions = True
        self.instruction_timer = 0
        self.show_result = False
        self.result_timer = 0

        # Reset button states
        for button in self.route_buttons:
            button['selected'] = False
            button['hover'] = False

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
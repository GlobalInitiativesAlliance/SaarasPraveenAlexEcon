"""
Bus Route Selection Mini-Game
Choose the correct bus within 20 seconds or miss appointment
"""
import pygame
import random

class BusRouteGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game settings
        self.time_limit = 20.0  # 20 seconds
        self.time_remaining = self.time_limit
        self.selected_route = None

        # Bus routes
        self.routes = [
            {
                "number": "Route 15",
                "destination": "Downtown Mall",
                "travel_time": "45 min",
                "correct": False
            },
            {
                "number": "Route 42",
                "destination": "Medical District",
                "travel_time": "15 min",
                "correct": True
            },
            {
                "number": "Route 8",
                "destination": "University Campus",
                "travel_time": "25 min",
                "correct": False
            },
            {
                "number": "Route 23",
                "destination": "Airport Terminal",
                "travel_time": "60 min",
                "correct": False
            },
            {
                "number": "Route 67",
                "destination": "Industrial District",
                "travel_time": "35 min",
                "correct": False
            }
        ]

        # Shuffle routes for variety
        random.shuffle(self.routes)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_BLUE = (173, 216, 230)
        self.ORANGE = (255, 165, 0)

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # UI elements
        self.route_rects = []
        self.setup_route_rects()

        # Animation
        self.urgency_flash = 0

    def setup_route_rects(self):
        """Set up rectangles for route options"""
        self.route_rects = []

        start_x = 150
        start_y = 250
        width = 400
        height = 80
        spacing = 90

        for i in range(len(self.routes)):
            y = start_y + (i * spacing)
            self.route_rects.append(pygame.Rect(start_x, y, width, height))

    def handle_event(self, event):
        """Handle player input"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check route clicks
            for i, rect in enumerate(self.route_rects):
                if rect.collidepoint(mouse_pos):
                    self.select_route(i)
                    break

        elif event.type == pygame.KEYDOWN:
            # Number keys for quick selection
            if pygame.K_1 <= event.key <= pygame.K_5:
                route_index = event.key - pygame.K_1
                if route_index < len(self.routes):
                    self.select_route(route_index)
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def select_route(self, index):
        """Select a bus route"""
        self.selected_route = self.routes[index]
        route = self.selected_route

        if route["correct"]:
            self.complete_game(success=True)
        else:
            self.complete_game(success=False)

    def complete_game(self, success):
        """Complete the bus route game"""
        self.completed = True

        if self.objective_manager:
            # Both success and missed appointment advance to next objective
            # The outcome is tracked in the success variable
            self.objective_manager.advance_to_next_objective()

    def update(self, dt):
        """Update game state"""
        if not self.active or self.completed:
            return

        self.time_remaining -= dt
        self.urgency_flash += dt

        # Time up - miss the appointment
        if self.time_remaining <= 0:
            self.time_remaining = 0
            if not self.completed:
                self.complete_game(success=False)

    def get_time_color(self):
        """Get color for timer based on urgency"""
        if self.time_remaining > 10:
            return self.GREEN
        elif self.time_remaining > 5:
            return self.YELLOW
        else:
            # Flash red when urgent
            if int(self.urgency_flash * 4) % 2:
                return self.RED
            else:
                return self.WHITE

    def draw(self, screen):
        """Render the bus route selection interface"""
        if not self.active:
            return

        # Background
        screen.fill((30, 30, 40))

        # Title
        title = self.font_large.render("Bus Stop - Route Selection", True, self.WHITE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 60))
        screen.blit(title, title_rect)

        # Situation context
        context_lines = [
            "URGENT: You have an appointment at the Community Health Clinic!",
            "Choose the correct bus route to get there on time.",
            "You need to get to the Medical District quickly."
        ]

        y = 100
        for line in context_lines:
            color = self.RED if "URGENT" in line else self.WHITE
            text = self.font_small.render(line, True, color)
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, y))
            screen.blit(text, text_rect)
            y += 25

        # Timer
        time_text = f"Time Remaining: {self.time_remaining:.1f}s"
        time_color = self.get_time_color()
        time_surface = self.font_large.render(time_text, True, time_color)

        # Timer background
        timer_rect = time_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
        bg_rect = timer_rect.copy()
        bg_rect.inflate(20, 10)
        pygame.draw.rect(screen, self.BLACK, bg_rect)
        pygame.draw.rect(screen, time_color, bg_rect, 3)

        screen.blit(time_surface, timer_rect)

        # Route options
        for i, (route, rect) in enumerate(zip(self.routes, self.route_rects)):
            # Background color
            if self.completed and route["correct"]:
                bg_color = (144, 238, 144)  # Light green for correct answer
            elif self.completed and self.selected_route == route and not route["correct"]:
                bg_color = (255, 182, 193)  # Light red for wrong selection
            else:
                bg_color = self.WHITE

            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos) and not self.completed:
                bg_color = self.LIGHT_BLUE

            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, self.BLACK, rect, 2)

            # Route number and key
            number_text = f"{i + 1}. {route['number']}"
            number_surface = self.font_medium.render(number_text, True, self.BLACK)
            screen.blit(number_surface, (rect.x + 15, rect.y + 10))

            # Destination
            dest_text = f"To: {route['destination']}"
            dest_surface = self.font_small.render(dest_text, True, self.BLACK)
            screen.blit(dest_surface, (rect.x + 15, rect.y + 35))

            # Travel time
            time_text = f"Est. Time: {route['travel_time']}"
            time_surface = self.font_small.render(time_text, True, self.GRAY)
            screen.blit(time_surface, (rect.x + 15, rect.y + 55))

        # Instructions
        if not self.completed:
            instruction_text = "Click on a route or press 1-5 to select"
            instruction_surface = self.font_small.render(instruction_text, True, self.GRAY)
            screen.blit(instruction_surface, (150, 650))

        # Result message
        if self.completed:
            if self.selected_route and self.selected_route["correct"]:
                message = "Success! You caught the right bus to your appointment."
                message_color = self.GREEN
            elif self.time_remaining <= 0:
                message = "Time's up! You missed all the buses and your appointment."
                message_color = self.RED
            else:
                message = f"Wrong bus! You went to {self.selected_route['destination']} instead of Medical District."
                message_color = self.RED

            message_surface = self.font_large.render(message, True, message_color)
            message_rect = message_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 670))

            # Message background
            bg_rect = message_rect.copy()
            bg_rect.inflate(40, 20)
            pygame.draw.rect(screen, self.WHITE, bg_rect)
            pygame.draw.rect(screen, message_color, bg_rect, 2)

            screen.blit(message_surface, message_rect)

            # Consequence text
            if not (self.selected_route and self.selected_route["correct"]):
                consequence = "Missing appointments affects your relationship with your caseworker."
                cons_surface = self.font_medium.render(consequence, True, self.RED)
                cons_rect = cons_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 700))
                screen.blit(cons_surface, cons_rect)

        # Progress indicator
        progress_width = 400
        progress_height = 8
        progress_x = (self.SCREEN_WIDTH - progress_width) // 2
        progress_y = 200

        # Background
        pygame.draw.rect(screen, self.GRAY, (progress_x, progress_y, progress_width, progress_height))

        # Progress fill
        progress = max(0, self.time_remaining / self.time_limit)
        fill_width = int(progress_width * progress)
        progress_color = self.get_time_color()
        pygame.draw.rect(screen, progress_color, (progress_x, progress_y, fill_width, progress_height))

        # Border
        pygame.draw.rect(screen, self.BLACK, (progress_x, progress_y, progress_width, progress_height), 1)

    def start(self):
        """Start the bus route game"""
        self.active = True
        self.completed = False
        self.time_remaining = self.time_limit
        self.selected_route = None
        self.urgency_flash = 0

        # Reshuffle routes for variety
        random.shuffle(self.routes)

    def stop(self):
        """Stop the bus route game"""
        self.active = False
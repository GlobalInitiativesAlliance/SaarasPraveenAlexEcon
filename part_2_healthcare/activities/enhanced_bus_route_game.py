"""
Enhanced Bus Route Selection Mini-Game
Realistic bus stop interface with live route updates, real-time arrivals, and city map visualization
"""
import pygame
import random
import math

class EnhancedBusRouteGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game settings
        self.time_limit = 20.0
        self.time_remaining = self.time_limit
        self.selected_route = None
        self.urgency_level = 0  # Increases as time runs out

        # Enhanced bus routes with realistic details
        self.routes = [
            {
                "number": "Route 15",
                "destination": "Downtown Mall",
                "travel_time": 45,
                "next_arrival": random.randint(3, 8),
                "frequency": "Every 12 min",
                "correct": False,
                "color": (255, 150, 100),  # Orange
                "transfers": 1,
                "accessibility": True,
                "fare": 2.50,
                "route_type": "Local"
            },
            {
                "number": "Route 42",
                "destination": "Medical District",
                "travel_time": 15,
                "next_arrival": random.randint(1, 5),
                "frequency": "Every 8 min",
                "correct": True,
                "color": (100, 200, 100),  # Green
                "transfers": 0,
                "accessibility": True,
                "fare": 2.50,
                "route_type": "Express"
            },
            {
                "number": "Route 8",
                "destination": "University Campus",
                "travel_time": 25,
                "next_arrival": random.randint(2, 7),
                "frequency": "Every 15 min",
                "correct": False,
                "color": (100, 150, 255),  # Blue
                "transfers": 0,
                "accessibility": True,
                "fare": 2.50,
                "route_type": "Local"
            },
            {
                "number": "Route 23",
                "destination": "Airport Terminal",
                "travel_time": 60,
                "next_arrival": random.randint(5, 12),
                "frequency": "Every 20 min",
                "correct": False,
                "color": (200, 100, 200),  # Purple
                "transfers": 0,
                "accessibility": True,
                "fare": 4.00,
                "route_type": "Express"
            },
            {
                "number": "Route 67",
                "destination": "Industrial District",
                "travel_time": 35,
                "next_arrival": random.randint(4, 10),
                "frequency": "Every 18 min",
                "correct": False,
                "color": (255, 200, 100),  # Yellow
                "transfers": 1,
                "accessibility": False,
                "fare": 2.50,
                "route_type": "Local"
            }
        ]

        # Sort routes by next arrival time for realistic display
        self.routes.sort(key=lambda x: x["next_arrival"])

        # Animation state
        self.time = 0
        self.bus_animations = {}
        self.arrival_animations = {}

        # UI Layout
        self.setup_ui_layout()

        # Enhanced color scheme
        self.colors = {
            'background': (235, 240, 245),
            'transit_blue': (0, 123, 191),
            'transit_green': (0, 150, 57),
            'warning_red': (220, 53, 69),
            'urgent_orange': (255, 133, 27),
            'text_dark': (33, 37, 41),
            'text_light': (108, 117, 125),
            'card_white': (255, 255, 255),
            'success_green': (40, 167, 69),
            'shadow': (0, 0, 0, 15),
            'glass': (255, 255, 255, 200)
        }

        # Professional fonts
        self.fonts = {
            'title': pygame.font.Font(None, 64),
            'subtitle': pygame.font.Font(None, 36),
            'header': pygame.font.Font(None, 32),
            'body': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 20),
            'tiny': pygame.font.Font(None, 16)
        }

        # Sound and visual effects
        self.particles = []
        self.notification_flash = 0
        self.selection_confirmed = False

    def setup_ui_layout(self):
        """Setup responsive UI layout for bus stop interface"""
        # Header area with transit info
        self.header_area = pygame.Rect(0, 0, self.SCREEN_WIDTH, 100)

        # Digital display area
        self.display_area = pygame.Rect(50, 110, self.SCREEN_WIDTH - 100, 120)

        # Route cards area
        self.routes_area = pygame.Rect(50, 250, self.SCREEN_WIDTH - 350, 420)

        # Info panel (appointment details)
        self.info_panel = pygame.Rect(self.SCREEN_WIDTH - 280, 250, 230, 300)

        # Timer area
        self.timer_area = pygame.Rect(self.SCREEN_WIDTH - 280, 570, 230, 100)

        # Setup route card positions
        self.route_cards = []
        card_height = 75
        spacing = 10

        for i, route in enumerate(self.routes):
            y = self.routes_area.y + i * (card_height + spacing)
            card_rect = pygame.Rect(self.routes_area.x, y,
                                   self.routes_area.width, card_height)
            self.route_cards.append(card_rect)

    def create_particle(self, x, y, color, velocity=(0, 0)):
        """Create particle for visual effects"""
        return {
            'x': x,
            'y': y,
            'vx': velocity[0] + random.uniform(-1, 1),
            'vy': velocity[1] + random.uniform(-2, 0),
            'color': color,
            'life': random.uniform(1, 3),
            'max_life': 3,
            'size': random.uniform(2, 5)
        }

    def update_particles(self, dt):
        """Update particle effects"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            particle['life'] -= dt

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_transit_header(self, surface):
        """Draw realistic transit system header"""
        # Background gradient
        for y in range(self.header_area.height):
            progress = y / self.header_area.height
            r = int(0 + (50 * progress))
            g = int(123 + (50 * progress))
            b = int(191 + (30 * progress))
            pygame.draw.line(surface, (r, g, b), (0, y), (self.SCREEN_WIDTH, y))

        # Transit logo
        logo_rect = pygame.Rect(30, 20, 60, 60)
        pygame.draw.ellipse(surface, (255, 255, 255), logo_rect)
        pygame.draw.ellipse(surface, self.colors['transit_green'], logo_rect, width=4)

        # Bus icon in logo
        bus_rect = pygame.Rect(logo_rect.centerx - 15, logo_rect.centery - 8, 30, 16)
        pygame.draw.rect(surface, self.colors['transit_blue'], bus_rect, border_radius=4)

        # Windows
        for i in range(3):
            window_x = bus_rect.x + 4 + (i * 7)
            window_rect = pygame.Rect(window_x, bus_rect.y + 2, 5, 6)
            pygame.draw.rect(surface, (255, 255, 255), window_rect)

        # System name
        title_text = self.fonts['title'].render("MetroTransit", True, (255, 255, 255))
        surface.blit(title_text, (110, 25))

        subtitle_text = self.fonts['body'].render("Real-Time Arrivals", True, (255, 255, 255, 200))
        surface.blit(subtitle_text, (110, 65))

        # Current stop info
        stop_info = "Bus Stop #247: Community Health Center"
        stop_text = self.fonts['small'].render(stop_info, True, (255, 255, 255))
        surface.blit(stop_text, (self.SCREEN_WIDTH - 350, 30))

        # Current time
        import datetime
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        time_text = self.fonts['body'].render(current_time, True, (255, 255, 255))
        surface.blit(time_text, (self.SCREEN_WIDTH - 120, 55))

    def draw_digital_display(self, surface):
        """Draw LED-style digital arrival display"""
        # Display background (dark with LED effect)
        pygame.draw.rect(surface, (20, 20, 30), self.display_area, border_radius=10)
        pygame.draw.rect(surface, self.colors['transit_blue'], self.display_area, width=3, border_radius=10)

        # LED grid effect
        for x in range(self.display_area.x, self.display_area.right, 4):
            for y in range(self.display_area.y, self.display_area.bottom, 4):
                if random.random() < 0.02:  # Subtle LED dots
                    pygame.draw.circle(surface, (0, 100, 50), (x, y), 1)

        # Header text
        header_text = "NEXT ARRIVALS"
        header_surface = self.fonts['header'].render(header_text, True, (100, 255, 100))
        header_rect = header_surface.get_rect(center=(self.display_area.centerx, self.display_area.y + 25))
        surface.blit(header_surface, header_rect)

        # Scrolling arrivals text
        arrival_text = ""
        for route in self.routes[:3]:  # Show top 3 arrivals
            arrival_text += f"Route {route['number']}: {route['next_arrival']} min  •  "

        # Remove trailing separator
        arrival_text = arrival_text.rstrip("  •  ")

        # Scrolling effect
        scroll_x = (self.time * 30) % (len(arrival_text) * 10)
        display_text = arrival_text + "     " + arrival_text  # Wrap text

        arrival_surface = self.fonts['body'].render(display_text, True, (255, 200, 0))
        text_y = self.display_area.y + 65

        # Create clipping rect for scrolling
        clip_rect = pygame.Rect(self.display_area.x + 20, text_y,
                               self.display_area.width - 40, 30)

        # Save the original clip
        original_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        surface.blit(arrival_surface, (self.display_area.x + 20 - scroll_x, text_y))

        # Restore original clip
        surface.set_clip(original_clip)

    def draw_route_card(self, surface, route, card_rect, index):
        """Draw detailed route information card"""
        is_correct = route['correct']
        is_hovered = card_rect.collidepoint(pygame.mouse.get_pos())

        # Card shadow
        shadow_rect = pygame.Rect(card_rect.x + 2, card_rect.y + 2,
                                 card_rect.width, card_rect.height)
        pygame.draw.rect(surface, self.colors['shadow'], shadow_rect, border_radius=8)

        # Card background
        card_color = self.colors['card_white']
        if is_hovered:
            card_color = (248, 252, 255)

        pygame.draw.rect(surface, card_color, card_rect, border_radius=8)

        # Route color strip (left side)
        color_strip = pygame.Rect(card_rect.x, card_rect.y,
                                 8, card_rect.height)
        pygame.draw.rect(surface, route['color'], color_strip,
                        border_top_left_radius=8, border_bottom_left_radius=8)

        # Route number (prominent)
        route_num_text = self.fonts['header'].render(route['number'], True, self.colors['text_dark'])
        surface.blit(route_num_text, (card_rect.x + 20, card_rect.y + 10))

        # Route type badge
        type_color = self.colors['transit_green'] if route['route_type'] == 'Express' else self.colors['text_light']
        type_rect = pygame.Rect(card_rect.x + 120, card_rect.y + 12, 60, 18)
        pygame.draw.rect(surface, type_color, type_rect, border_radius=9)

        type_text = self.fonts['tiny'].render(route['route_type'], True, (255, 255, 255))
        type_text_rect = type_text.get_rect(center=type_rect.center)
        surface.blit(type_text, type_text_rect)

        # Destination
        dest_text = self.fonts['body'].render(f"To: {route['destination']}", True, self.colors['text_dark'])
        surface.blit(dest_text, (card_rect.x + 20, card_rect.y + 35))

        # Travel time
        time_color = self.colors['success_green'] if route['travel_time'] <= 20 else self.colors['text_light']
        time_text = self.fonts['small'].render(f"{route['travel_time']} min journey", True, time_color)
        surface.blit(time_text, (card_rect.x + 20, card_rect.y + 55))

        # Next arrival (prominent, right side)
        arrival_mins = route['next_arrival']
        if arrival_mins <= 1:
            arrival_text = "ARRIVING"
            arrival_color = self.colors['urgent_orange']
        elif arrival_mins <= 3:
            arrival_text = f"{arrival_mins} MIN"
            arrival_color = self.colors['warning_red']
        else:
            arrival_text = f"{arrival_mins} MIN"
            arrival_color = self.colors['text_dark']

        arrival_surface = self.fonts['header'].render(arrival_text, True, arrival_color)
        arrival_rect = arrival_surface.get_rect(center=(card_rect.right - 80, card_rect.centery))

        # Arrival background
        arrival_bg = pygame.Rect(arrival_rect.x - 10, arrival_rect.y - 5,
                               arrival_rect.width + 20, arrival_rect.height + 10)
        bg_color = (*arrival_color, 20)
        pygame.draw.rect(surface, bg_color, arrival_bg, border_radius=5)

        surface.blit(arrival_surface, arrival_rect)

        # Accessibility icon
        if route['accessibility']:
            wheelchair_pos = (card_rect.right - 25, card_rect.y + 15)
            pygame.draw.circle(surface, self.colors['transit_blue'], wheelchair_pos, 8)
            wheelchair_text = self.fonts['tiny'].render("♿", True, (255, 255, 255))
            wheelchair_rect = wheelchair_text.get_rect(center=wheelchair_pos)
            surface.blit(wheelchair_text, wheelchair_rect)

        # Selection highlight
        if self.selected_route == route:
            pygame.draw.rect(surface, self.colors['transit_blue'], card_rect, width=4, border_radius=8)

        # Hover effect
        if is_hovered and not self.completed:
            pygame.draw.rect(surface, self.colors['transit_blue'], card_rect, width=2, border_radius=8)

    def draw_info_panel(self, surface):
        """Draw appointment information panel"""
        # Panel background
        pygame.draw.rect(surface, self.colors['card_white'], self.info_panel, border_radius=12)
        pygame.draw.rect(surface, self.colors['transit_blue'], self.info_panel, width=2, border_radius=12)

        # Header
        header_text = self.fonts['header'].render("Your Appointment", True, self.colors['text_dark'])
        surface.blit(header_text, (self.info_panel.x + 15, self.info_panel.y + 15))

        # Appointment details
        details = [
            ("Time:", "2:00 PM"),
            ("Location:", "Community"),
            ("", "Health Clinic"),
            ("Address:", "Medical District"),
            ("Purpose:", "Medi-Cal"),
            ("", "Application")
        ]

        y_offset = 50
        for label, value in details:
            if label:
                label_text = self.fonts['small'].render(label, True, self.colors['text_light'])
                surface.blit(label_text, (self.info_panel.x + 15, self.info_panel.y + y_offset))

            value_text = self.fonts['small'].render(value, True, self.colors['text_dark'])
            x_offset = 80 if label else 15
            surface.blit(value_text, (self.info_panel.x + x_offset, self.info_panel.y + y_offset))

            y_offset += 20

        # Urgency note
        urgency_text = "Don't miss this important appointment!"
        urgency_color = self.colors['warning_red'] if self.time_remaining < 10 else self.colors['text_light']

        urgency_surface = self.fonts['tiny'].render(urgency_text, True, urgency_color)
        surface.blit(urgency_surface, (self.info_panel.x + 15, self.info_panel.y + 200))

        # Instructions
        instructions = [
            "Click on the route",
            "that goes to the",
            "Medical District"
        ]

        y_offset = 230
        for instruction in instructions:
            inst_text = self.fonts['small'].render(instruction, True, self.colors['text_dark'])
            surface.blit(inst_text, (self.info_panel.x + 15, self.info_panel.y + y_offset))
            y_offset += 20

    def draw_timer_panel(self, surface):
        """Draw countdown timer with urgency effects"""
        # Panel background
        timer_color = self.colors['card_white']
        if self.time_remaining < 5:
            # Flash red when urgent
            flash_intensity = math.sin(self.time * 8) * 0.3 + 0.7
            timer_color = (int(255 * flash_intensity), int(200 * (1 - flash_intensity)), int(200 * (1 - flash_intensity)))

        pygame.draw.rect(surface, timer_color, self.timer_area, border_radius=12)

        border_color = self.colors['warning_red'] if self.time_remaining < 10 else self.colors['transit_blue']
        pygame.draw.rect(surface, border_color, self.timer_area, width=3, border_radius=12)

        # Timer header
        header_text = "Time Remaining"
        header_surface = self.fonts['body'].render(header_text, True, self.colors['text_dark'])
        header_rect = header_surface.get_rect(center=(self.timer_area.centerx, self.timer_area.y + 25))
        surface.blit(header_surface, header_rect)

        # Time display
        time_text = f"{self.time_remaining:.1f}s"
        time_color = self.colors['warning_red'] if self.time_remaining < 10 else self.colors['text_dark']

        time_surface = self.fonts['title'].render(time_text, True, time_color)
        time_rect = time_surface.get_rect(center=(self.timer_area.centerx, self.timer_area.centery + 10))
        surface.blit(time_surface, time_rect)

        # Progress bar
        bar_width = self.timer_area.width - 20
        bar_height = 8
        bar_x = self.timer_area.x + 10
        bar_y = self.timer_area.bottom - 20

        # Background bar
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

        # Progress fill
        progress = max(0, self.time_remaining / self.time_limit)
        fill_width = int(bar_width * progress)

        if self.time_remaining > 10:
            fill_color = self.colors['success_green']
        elif self.time_remaining > 5:
            fill_color = self.colors['urgent_orange']
        else:
            fill_color = self.colors['warning_red']

        if fill_width > 0:
            pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)

    def handle_event(self, event):
        """Handle enhanced bus route selection"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check route card clicks
            for i, card_rect in enumerate(self.route_cards):
                if card_rect.collidepoint(mouse_pos):
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
        """Select a bus route with enhanced feedback"""
        self.selected_route = self.routes[index]
        self.selection_confirmed = True

        # Create selection particles
        route = self.selected_route
        card_rect = self.route_cards[index]

        particle_color = self.colors['success_green'] if route['correct'] else self.colors['warning_red']
        for _ in range(15):
            particle = self.create_particle(
                card_rect.centerx + random.uniform(-50, 50),
                card_rect.centery + random.uniform(-20, 20),
                particle_color,
                (random.uniform(-3, 3), random.uniform(-5, -1))
            )
            self.particles.append(particle)

        # Complete with result
        if route["correct"]:
            self.complete_game(success=True)
        else:
            self.complete_game(success=False)

    def complete_game(self, success):
        """Complete the bus route game with enhanced results"""
        self.completed = True

        if self.objective_manager:
            # Both correct and wrong bus advance to next objective
            # The game outcome is tracked in self.completed and success variable
            self.objective_manager.advance_to_next_objective()

    def update(self, dt):
        """Update enhanced bus route game"""
        if not self.active or self.completed:
            return

        self.time += dt
        self.time_remaining -= dt

        # Update particles
        self.update_particles(dt)

        # Update arrival times (simulate real-time)
        if int(self.time) % 2 == 0:  # Update every 2 seconds
            for route in self.routes:
                if random.random() < 0.1:  # 10% chance to decrement
                    route['next_arrival'] = max(0, route['next_arrival'] - 1)

        # Time up - missed all buses
        if self.time_remaining <= 0:
            self.time_remaining = 0
            if not self.completed:
                self.complete_game(success=False)

    def render(self, screen):
        """Render enhanced bus route interface"""
        if not self.active:
            return

        # Background
        screen.fill(self.colors['background'])

        # Draw transit header
        self.draw_transit_header(screen)

        # Draw digital display
        self.draw_digital_display(screen)

        # Draw route cards
        for i, (route, card_rect) in enumerate(zip(self.routes, self.route_cards)):
            self.draw_route_card(screen, route, card_rect, i)

        # Draw info panel
        self.draw_info_panel(screen)

        # Draw timer panel
        self.draw_timer_panel(screen)

        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            size = max(1, int(particle['size']))

            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))

        # Result message
        if self.completed:
            message_rect = pygame.Rect(200, 300, 880, 120)
            pygame.draw.rect(screen, self.colors['card_white'], message_rect, border_radius=15)

            if self.selected_route and self.selected_route["correct"]:
                message = "✓ Perfect! You caught Route 42 to the Medical District."
                message_color = self.colors['success_green']
                pygame.draw.rect(screen, message_color, message_rect, width=4, border_radius=15)
            elif self.time_remaining <= 0:
                message = "⏰ Time's up! You missed all the buses and your appointment."
                message_color = self.colors['warning_red']
                pygame.draw.rect(screen, message_color, message_rect, width=4, border_radius=15)
            else:
                dest = self.selected_route['destination'] if self.selected_route else "unknown"
                message = f"❌ Wrong route! You went to {dest} instead of Medical District."
                message_color = self.colors['warning_red']
                pygame.draw.rect(screen, message_color, message_rect, width=4, border_radius=15)

            message_surface = self.fonts['subtitle'].render(message, True, message_color)
            message_text_rect = message_surface.get_rect(center=message_rect.center)
            screen.blit(message_surface, message_text_rect)

            # Consequence note
            if not (self.selected_route and self.selected_route["correct"]):
                consequence = "Missing appointments affects your relationship with healthcare providers."
                cons_surface = self.fonts['body'].render(consequence, True, self.colors['text_light'])
                cons_rect = cons_surface.get_rect(center=(message_rect.centerx, message_rect.bottom + 30))
                screen.blit(cons_surface, cons_rect)

    def start(self):
        """Start enhanced bus route game"""
        self.active = True
        self.completed = False
        self.time_remaining = self.time_limit
        self.selected_route = None
        self.selection_confirmed = False
        self.particles.clear()
        self.time = 0

        # Randomize arrival times for variety
        for route in self.routes:
            route['next_arrival'] = random.randint(1, 12)

        # Re-sort by arrival time
        self.routes.sort(key=lambda x: x["next_arrival"])

    def stop(self):
        """Stop enhanced bus route game"""
        self.active = False
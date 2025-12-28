"""
Clinic Navigation Mini-Game
Interactive clinic floor plan with departments to navigate through
Features realistic clinic layout with visual guidance system
"""

import pygame
import math
import random

class ClinicNavigationGame:
    """Interactive clinic navigation mini-game"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Navigation state
        self.player_pos = [100, 600]  # Starting position (entrance)
        self.target_department = "Registration"
        self.current_step = 0
        self.navigation_steps = [
            {"department": "Registration", "description": "Check in and get forms", "pos": [300, 400]},
            {"department": "Waiting Area", "description": "Wait for your name to be called", "pos": [600, 450]},
            {"department": "Eligibility Office", "description": "Meet with eligibility specialist", "pos": [900, 300]},
            {"department": "Exit", "description": "Complete - Ready to leave", "pos": [100, 600]}
        ]

        # Clinic layout
        self.clinic_layout = {
            "rooms": [
                {"name": "Main Entrance", "rect": pygame.Rect(50, 550, 100, 100), "color": (100, 150, 100), "icon": "🚪"},
                {"name": "Reception Desk", "rect": pygame.Rect(200, 350, 200, 100), "color": (150, 100, 150), "icon": "💻"},
                {"name": "Waiting Area", "rect": pygame.Rect(500, 400, 250, 150), "color": (100, 100, 150), "icon": "🪑"},
                {"name": "Eligibility Office", "rect": pygame.Rect(850, 250, 200, 150), "color": (150, 150, 100), "icon": "📋"},
                {"name": "Pharmacy Window", "rect": pygame.Rect(850, 450, 150, 100), "color": (100, 150, 150), "icon": "💊"},
                {"name": "Information Desk", "rect": pygame.Rect(200, 200, 150, 100), "color": (150, 100, 100), "icon": "ℹ️"},
                {"name": "Restrooms", "rect": pygame.Rect(50, 250, 100, 150), "color": (120, 120, 120), "icon": "🚻"},
                {"name": "Medical Records", "rect": pygame.Rect(500, 150, 200, 150), "color": (100, 120, 150), "icon": "📁"},
            ],
            "hallways": [
                {"start": [150, 600], "end": [400, 600]},  # Main hallway
                {"start": [400, 600], "end": [400, 500]},  # To waiting area
                {"start": [400, 500], "end": [750, 500]},  # To departments
                {"start": [750, 500], "end": [950, 500]},  # To eligibility
                {"start": [400, 400], "end": [400, 200]},  # North hallway
                {"start": [400, 200], "end": [700, 200]},  # To records
            ]
        }

        # Game state
        self.animation_time = 0
        self.path_finding = False
        self.current_path = []
        self.path_index = 0
        self.movement_speed = 150  # pixels per second

        # UI state
        self.hovered_room = None
        self.show_instructions = True
        self.instruction_timer = 0

        # Fonts
        self.title_font = pygame.font.Font(None, 42)
        self.header_font = pygame.font.Font(None, 36)
        self.content_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)

        # Colors
        self.colors = {
            'player': (255, 100, 100),
            'target': (100, 255, 100),
            'path': (100, 200, 255),
            'hallway': (200, 200, 200),
            'wall': (80, 80, 80),
            'text': (255, 255, 255),
            'ui_bg': (40, 50, 70),
            'highlight': (255, 255, 100)
        }

        # Visual effects
        self.particles = []
        self.target_pulse = 0

    def start(self):
        """Start the clinic navigation"""
        self.active = True
        self.completed = False
        self.animation_time = 0
        self.current_step = 0
        self.player_pos = [100, 600]  # Reset to entrance
        self.path_finding = False
        self.current_path = []
        self.show_instructions = True
        self.instruction_timer = 0

        # Clear effects
        self.particles = []

    def update(self, dt):
        """Update navigation state and animations"""
        if not self.active:
            return

        self.animation_time += dt
        self.target_pulse += dt * 3

        # Update instruction timer
        if self.show_instructions:
            self.instruction_timer += dt
            if self.instruction_timer > 8.0:  # Hide after 8 seconds
                self.show_instructions = False

        # Update player movement along path
        if self.path_finding and self.current_path:
            self.update_player_movement(dt)

        # Update particles
        self.update_particles(dt)

        # Check if player reached current target
        if self.current_step < len(self.navigation_steps):
            target = self.navigation_steps[self.current_step]
            distance = math.sqrt(
                (self.player_pos[0] - target["pos"][0]) ** 2 +
                (self.player_pos[1] - target["pos"][1]) ** 2
            )

            if distance < 50:  # Close enough to target
                self.reach_target()

    def update_player_movement(self, dt):
        """Update player movement along the calculated path"""
        if not self.current_path or self.path_index >= len(self.current_path):
            self.path_finding = False
            return

        target_point = self.current_path[self.path_index]
        dx = target_point[0] - self.player_pos[0]
        dy = target_point[1] - self.player_pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 5:  # Reached current path point
            self.path_index += 1
            if self.path_index >= len(self.current_path):
                self.path_finding = False
        else:
            # Move towards target point
            move_x = (dx / distance) * self.movement_speed * dt
            move_y = (dy / distance) * self.movement_speed * dt
            self.player_pos[0] += move_x
            self.player_pos[1] += move_y

    def update_particles(self, dt):
        """Update particle effects"""
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vel_x'] * dt
            particle['y'] += particle['vel_y'] * dt
            particle['alpha'] = max(0, int(255 * particle['life'] / particle['max_life']))

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def reach_target(self):
        """Handle reaching a navigation target"""
        current_target = self.navigation_steps[self.current_step]

        # Create success particles
        for _ in range(20):
            self.particles.append({
                'x': self.player_pos[0] + random.randint(-30, 30),
                'y': self.player_pos[1] + random.randint(-30, 30),
                'vel_x': random.uniform(-100, 100),
                'vel_y': random.uniform(-150, -50),
                'life': random.uniform(1.0, 2.0),
                'max_life': 2.0,
                'color': self.colors['target'],
                'alpha': 255
            })

        # Advance to next step
        self.current_step += 1

        # Check if completed all steps
        if self.current_step >= len(self.navigation_steps):
            self.complete_navigation()

    def complete_navigation(self):
        """Complete the navigation mini-game"""
        self.completed = True
        self.active = False

        # Notify objective manager
        if self.objective_manager and hasattr(self.objective_manager, 'show_notification'):
            self.objective_manager.show_notification("Navigation Complete! You've successfully navigated through the clinic process.")

    def handle_click(self, pos):
        """Handle mouse clicks for navigation"""
        if not self.active or self.path_finding:
            return

        mx, my = pos

        # Check if clicked on a room
        clicked_room = None
        for room in self.clinic_layout["rooms"]:
            if room["rect"].collidepoint(mx, my):
                clicked_room = room
                break

        if clicked_room and self.current_step < len(self.navigation_steps):
            current_target = self.navigation_steps[self.current_step]

            # Check if clicked on correct target
            if current_target["department"].lower() in clicked_room["name"].lower() or \
               (current_target["department"] == "Registration" and "Reception" in clicked_room["name"]) or \
               (current_target["department"] == "Exit" and "Entrance" in clicked_room["name"]):

                # Calculate path to target
                self.calculate_path_to_target(current_target["pos"])

    def handle_mouse_motion(self, pos):
        """Handle mouse movement for hover effects"""
        if not self.active:
            return

        mx, my = pos
        self.hovered_room = None

        # Check hover on rooms
        for room in self.clinic_layout["rooms"]:
            if room["rect"].collidepoint(mx, my):
                self.hovered_room = room
                break

    def calculate_path_to_target(self, target_pos):
        """Calculate a path from player to target using hallways"""
        # Simple path finding - follow hallway network
        # For this mini-game, we'll use a simplified direct path with waypoints

        start_pos = self.player_pos.copy()
        end_pos = target_pos

        # Create a simple path with intermediate waypoints
        path = [start_pos]

        # Add waypoints based on clinic layout
        # This is a simplified pathfinding - in a real clinic, you'd use A* or similar
        if start_pos[0] < 400:  # From entrance area
            path.append([400, start_pos[1]])  # Go to main junction

        if end_pos[1] < 400:  # Going to upper areas
            path.append([400, 400])  # Main junction
            path.append([end_pos[0], 400])  # Horizontal to target area
        elif end_pos[0] > 700:  # Going to right side
            path.append([400, 500])  # Main hallway junction
            path.append([750, 500])  # Right hallway

        path.append(end_pos)

        self.current_path = path
        self.path_index = 1  # Skip first point (current position)
        self.path_finding = True

    def draw(self, screen):
        """Draw the clinic navigation interface"""
        if not self.active:
            return

        # Background
        self.draw_background(screen)

        # Clinic floor plan
        self.draw_clinic_layout(screen)

        # Navigation path
        self.draw_navigation_path(screen)

        # Player
        self.draw_player(screen)

        # Current target highlight
        self.draw_current_target(screen)

        # UI panels
        self.draw_ui_panels(screen)

        # Instructions
        if self.show_instructions:
            self.draw_instructions(screen)

        # Particles
        self.draw_particles(screen)

    def draw_background(self, screen):
        """Draw the clinic background"""
        # Floor color
        screen.fill((240, 240, 245))

        # Grid pattern for floor tiles
        grid_size = 40
        grid_color = (220, 220, 230)
        for x in range(0, self.SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, self.SCREEN_HEIGHT))
        for y in range(0, self.SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (self.SCREEN_WIDTH, y))

    def draw_clinic_layout(self, screen):
        """Draw the clinic rooms and hallways"""
        # Draw hallways first
        for hallway in self.clinic_layout["hallways"]:
            pygame.draw.line(screen, self.colors['hallway'],
                           hallway["start"], hallway["end"], 20)

        # Draw rooms
        for room in self.clinic_layout["rooms"]:
            # Room background
            room_color = room["color"]
            if self.hovered_room == room:
                # Brighten color on hover
                room_color = tuple(min(255, c + 30) for c in room_color)

            pygame.draw.rect(screen, room_color, room["rect"], 0, 8)
            pygame.draw.rect(screen, (100, 100, 100), room["rect"], 3, 8)

            # Room icon
            icon_surf = self.content_font.render(room["icon"], True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(center=room["rect"].center)
            screen.blit(icon_surf, icon_rect)

            # Room label
            label_surf = self.small_font.render(room["name"], True, (50, 50, 50))
            label_rect = label_surf.get_rect(center=(room["rect"].centerx, room["rect"].bottom + 15))
            screen.blit(label_surf, label_rect)

    def draw_navigation_path(self, screen):
        """Draw the current navigation path"""
        if self.current_path and len(self.current_path) > 1:
            # Draw path line
            for i in range(len(self.current_path) - 1):
                start_pos = self.current_path[i]
                end_pos = self.current_path[i + 1]

                # Draw path with dashed line effect
                distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
                steps = int(distance // 20)

                for step in range(steps):
                    if step % 2 == 0:  # Dashed line
                        progress = step / steps
                        x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                        y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                        pygame.draw.circle(screen, self.colors['path'], (int(x), int(y)), 4)

    def draw_player(self, screen):
        """Draw the player indicator"""
        # Player circle with pulsing effect
        pulse_size = 15 + 3 * math.sin(self.animation_time * 6)
        pygame.draw.circle(screen, self.colors['player'],
                         (int(self.player_pos[0]), int(self.player_pos[1])), int(pulse_size))

        # Player icon
        player_icon = "👤"
        player_surf = self.content_font.render(player_icon, True, (255, 255, 255))
        player_rect = player_surf.get_rect(center=(int(self.player_pos[0]), int(self.player_pos[1])))
        screen.blit(player_surf, player_rect)

    def draw_current_target(self, screen):
        """Draw the current navigation target"""
        if self.current_step < len(self.navigation_steps):
            target = self.navigation_steps[self.current_step]
            target_pos = target["pos"]

            # Pulsing target indicator
            pulse_alpha = int(128 + 127 * math.sin(self.target_pulse))
            pulse_size = 40 + 10 * math.sin(self.target_pulse)

            # Create surface with alpha for pulsing effect
            target_surface = pygame.Surface((int(pulse_size * 2), int(pulse_size * 2)))
            target_surface.set_alpha(pulse_alpha)
            target_surface.fill(self.colors['target'])
            target_rect = target_surface.get_rect(center=target_pos)
            screen.blit(target_surface, target_rect)

            # Target ring
            pygame.draw.circle(screen, self.colors['target'], target_pos, int(pulse_size), 3)

            # Target label
            label_surf = self.small_font.render(target["department"], True, self.colors['target'])
            label_rect = label_surf.get_rect(center=(target_pos[0], target_pos[1] - 60))

            # Label background
            label_bg = label_rect.inflate(10, 6)
            pygame.draw.rect(screen, (0, 0, 0, 180), label_bg, 0, 5)
            screen.blit(label_surf, label_rect)

    def draw_ui_panels(self, screen):
        """Draw UI information panels"""
        # Progress panel
        progress_rect = pygame.Rect(20, 20, 300, 120)
        pygame.draw.rect(screen, self.colors['ui_bg'], progress_rect, 0, 10)
        pygame.draw.rect(screen, self.colors['text'], progress_rect, 2, 10)

        # Progress title
        progress_title = "Navigation Progress"
        title_surf = self.header_font.render(progress_title, True, self.colors['text'])
        screen.blit(title_surf, (30, 35))

        # Current step
        if self.current_step < len(self.navigation_steps):
            current_target = self.navigation_steps[self.current_step]
            step_text = f"Step {self.current_step + 1}: {current_target['department']}"
            step_surf = self.content_font.render(step_text, True, self.colors['highlight'])
            screen.blit(step_surf, (30, 65))

            desc_surf = self.small_font.render(current_target['description'], True, self.colors['text'])
            screen.blit(desc_surf, (30, 90))

        # Progress bar
        bar_rect = pygame.Rect(30, 110, 260, 20)
        pygame.draw.rect(screen, (60, 60, 80), bar_rect, 0, 10)

        progress = self.current_step / len(self.navigation_steps)
        fill_width = int(260 * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(30, 110, fill_width, 20)
            pygame.draw.rect(screen, self.colors['target'], fill_rect, 0, 10)

        # Instructions panel
        if self.hovered_room:
            instruction_rect = pygame.Rect(self.SCREEN_WIDTH - 320, 20, 300, 80)
            pygame.draw.rect(screen, self.colors['ui_bg'], instruction_rect, 0, 10)
            pygame.draw.rect(screen, self.colors['text'], instruction_rect, 2, 10)

            inst_title = f"📍 {self.hovered_room['name']}"
            inst_surf = self.content_font.render(inst_title, True, self.colors['text'])
            screen.blit(inst_surf, (self.SCREEN_WIDTH - 310, 35))

            inst_desc = "Click to navigate here"
            desc_surf = self.small_font.render(inst_desc, True, self.colors['highlight'])
            screen.blit(desc_surf, (self.SCREEN_WIDTH - 310, 65))

    def draw_instructions(self, screen):
        """Draw initial navigation instructions"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(int(200 * (8.0 - min(8.0, self.instruction_timer)) / 8.0))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Instruction panel
        panel_width = 600
        panel_height = 300
        panel_x = (self.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.SCREEN_HEIGHT - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, self.colors['ui_bg'], panel_rect, 0, 15)
        pygame.draw.rect(screen, self.colors['text'], panel_rect, 3, 15)

        # Instructions
        instructions = [
            "🏥 Clinic Navigation Guide",
            "",
            "Follow these steps to complete your visit:",
            "1. Check in at Registration",
            "2. Wait in the Waiting Area",
            "3. Meet with Eligibility Specialist",
            "4. Exit when complete",
            "",
            "💡 Click on highlighted rooms to navigate",
            "⭐ Follow the green target indicators"
        ]

        for i, instruction in enumerate(instructions):
            if instruction.startswith("🏥"):
                font = self.header_font
                color = self.colors['highlight']
            elif instruction.startswith(("💡", "⭐")):
                font = self.small_font
                color = self.colors['target']
            elif instruction:
                font = self.content_font
                color = self.colors['text']
            else:
                continue

            inst_surf = font.render(instruction, True, color)
            inst_rect = inst_surf.get_rect(center=(panel_x + panel_width // 2, panel_y + 40 + i * 25))
            screen.blit(inst_surf, inst_rect)

    def draw_particles(self, screen):
        """Draw particle effects"""
        for particle in self.particles:
            if particle['alpha'] > 0:
                color = (*particle['color'], particle['alpha'])
                size = max(1, int(6 * particle['life'] / particle['max_life']))
                pygame.draw.circle(screen, color[:3], (int(particle['x']), int(particle['y'])), size)

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.show_instructions = False

    def get_results(self):
        """Return results for the objective system"""
        return {
            'completed': self.completed,
            'steps_completed': self.current_step,
            'total_steps': len(self.navigation_steps),
            'message': "Successfully navigated through the clinic!",
            'color': self.colors['target']
        }

    def render(self, screen):
        """Render method for compatibility with activity system"""
        self.draw(screen)
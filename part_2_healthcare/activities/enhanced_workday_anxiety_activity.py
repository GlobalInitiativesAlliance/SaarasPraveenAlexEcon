"""
Enhanced Workday Anxiety Activity with Professional Graphics
Matching Part 1 visual quality with realistic sprites, animations, and professional UI
"""
import pygame
import math
import random
import os

class EnhancedWorkdayAnxietyActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Enhanced color palette
        self.COLORS = {
            'background_kitchen': (85, 65, 45),     # Warm kitchen brown
            'counter_steel': (180, 180, 190),      # Stainless steel
            'grill_surface': (60, 60, 70),         # Dark grill surface
            'flame_orange': (255, 140, 60),        # Grill flames
            'steam_white': (240, 240, 250),        # Steam effects
            'anxiety_red': (220, 60, 60),          # Anxiety indicators
            'success_green': (80, 180, 80),        # Success feedback
            'warning_yellow': (255, 200, 60),      # Warning states
            'text_dark': (40, 40, 40),             # Primary text
            'text_light': (200, 200, 200),         # Light text
            'shadow': (0, 0, 0, 60),               # Semi-transparent shadows
            'highlight': (255, 255, 255, 100),     # Highlights
            'ui_background': (250, 245, 240),      # UI panel background
            'order_paper': (255, 255, 240),        # Order ticket paper
            'floor_tile': (120, 100, 80),          # Kitchen floor
            'wall_tile': (160, 140, 110),          # Kitchen wall
            'equipment_metal': (140, 140, 150),    # Kitchen equipment
        }

        # Game state
        self.timer = 0.0
        self.anxiety_level = 15  # Start with mild workplace stress
        self.scene_progress = 0
        self.ready_for_breathing = False
        self.show_break_prompt = False

        # Enhanced workplace state
        self.burger_count = 0
        self.orders_completed = 0
        self.orders_failed = 0
        self.shift_timer = 0.0
        self.current_task = "Preparing orders"

        # Enhanced visual effects
        self.anxiety_pulse_timer = 0
        self.screen_shake_intensity = 0
        self.heart_beat_timer = 0
        self.heart_rate = 65  # BPM, starts slightly elevated
        self.stress_overlay_alpha = 0
        self.thought_display_timer = 0

        # Advanced particle systems
        self.steam_particles = []
        self.stress_particles = []
        self.success_particles = []

        # Enhanced order system
        self.order_queue = []
        self.completed_orders = []

        # Enhanced NPC system
        self.manager = {
            'x': 950, 'y': 300, 'sprite_frame': 0,
            'watching': False, 'patience': 90,
            'mood': 'neutral', 'movement_timer': 0
        }

        self.coworker = {
            'x': 400, 'y': 380, 'sprite_frame': 0,
            'busy': True, 'helping': False,
            'mood': 'focused', 'efficiency': 0.8
        }

        # Enhanced thought system with healthcare anxiety
        self.healthcare_thoughts = [
            {
                "text": "Tomorrow's therapy appointment... how will I pay $150?",
                "intensity": 25,
                "duration": 4.5,
                "category": "financial"
            },
            {
                "text": "What if I can't get my prescription refilled?",
                "intensity": 30,
                "duration": 4.0,
                "category": "medical"
            },
            {
                "text": "I need to focus on work, but I can't stop worrying...",
                "intensity": 20,
                "duration": 3.5,
                "category": "concentration"
            },
            {
                "text": "My hands are shaking. I hope the manager doesn't notice.",
                "intensity": 35,
                "duration": 4.0,
                "category": "physical"
            },
            {
                "text": "Without insurance, every medical bill could ruin me.",
                "intensity": 40,
                "duration": 5.0,
                "category": "financial"
            },
            {
                "text": "What if my mental health gets worse without treatment?",
                "intensity": 45,
                "duration": 4.5,
                "category": "health_anxiety"
            }
        ]

        self.current_thought = None
        self.thought_timer = 0
        self.thought_fade_timer = 0

        # Professional font system
        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 28),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 18),
            'ui': pygame.font.Font(None, 24)
        }

        # Load workplace sprites and assets
        self.load_workplace_assets()

        # Initialize enhanced workplace
        self.setup_enhanced_workplace()

    def load_workplace_assets(self):
        """Load professional workplace sprites and create fallback graphics"""
        self.sprites = {}
        self.surfaces = {}

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

            # Kitchen and restaurant sprite paths
            sprite_paths = {
                'kitchen': os.path.join(base_dir, 'assets', 'moderninteriors-win', '1_Interiors', '16x16', 'Theme_Sorter', '12_Kitchen_16x16.png'),
                'restaurant': os.path.join(base_dir, 'assets', 'moderninteriors-win', '1_Interiors', '16x16', 'Theme_Sorter', '16_Grocery_store_16x16.png'),
                'characters': os.path.join(base_dir, 'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator', '0_Premade_Characters', '16x16', 'Premade_Character_01.png')
            }

            # Load sprites if available
            for name, path in sprite_paths.items():
                if os.path.exists(path):
                    self.sprites[name] = pygame.image.load(path).convert_alpha()
                    print(f"[WORKDAY] Loaded {name} sprites")

        except Exception as e:
            print(f"[WORKDAY] Could not load sprites: {e}")

        # Always create enhanced fallback graphics
        self.create_enhanced_graphics()

    def create_enhanced_graphics(self):
        """Create professional-looking workplace graphics"""
        tile_size = 32

        # Enhanced kitchen background
        self.surfaces['kitchen_bg'] = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.draw_kitchen_background(self.surfaces['kitchen_bg'])

        # Professional grill with realistic details
        self.surfaces['grill'] = pygame.Surface((tile_size * 4, tile_size * 2), pygame.SRCALPHA)
        self.draw_realistic_grill(self.surfaces['grill'])

        # Stainless steel counter with highlights
        self.surfaces['counter'] = pygame.Surface((tile_size * 6, tile_size), pygame.SRCALPHA)
        self.draw_steel_counter(self.surfaces['counter'])

        # Character sprites with uniforms
        self.surfaces['player'] = pygame.Surface((tile_size, tile_size * 2), pygame.SRCALPHA)
        self.draw_employee_character(self.surfaces['player'], (100, 150, 200))  # Blue uniform

        self.surfaces['manager'] = pygame.Surface((tile_size, tile_size * 2), pygame.SRCALPHA)
        self.draw_employee_character(self.surfaces['manager'], (120, 80, 60))  # Brown manager shirt

        self.surfaces['coworker'] = pygame.Surface((tile_size, tile_size * 2), pygame.SRCALPHA)
        self.draw_employee_character(self.surfaces['coworker'], (100, 180, 100))  # Green uniform

        # UI elements
        self.create_professional_ui_elements()

    def draw_kitchen_background(self, surface):
        """Draw a realistic kitchen background"""
        # Kitchen floor tiles
        surface.fill(self.COLORS['floor_tile'])

        # Add floor tile pattern
        tile_size = 32
        for y in range(0, self.SCREEN_HEIGHT, tile_size):
            for x in range(0, self.SCREEN_WIDTH, tile_size):
                # Add subtle tile borders
                pygame.draw.rect(surface, (100, 90, 70),
                               (x, y, tile_size, tile_size), 1)

        # Kitchen walls (upper portion)
        wall_rect = pygame.Rect(0, 0, self.SCREEN_WIDTH, 200)
        surface.fill(self.COLORS['wall_tile'], wall_rect)

        # Add wall tile pattern
        for y in range(0, 200, tile_size):
            for x in range(0, self.SCREEN_WIDTH, tile_size):
                pygame.draw.rect(surface, (140, 130, 100),
                               (x, y, tile_size, tile_size), 1)

    def draw_realistic_grill(self, surface):
        """Draw a realistic grill with details"""
        w, h = surface.get_size()

        # Grill base (dark metal)
        pygame.draw.rect(surface, self.COLORS['grill_surface'], (0, 0, w, h))
        pygame.draw.rect(surface, (40, 40, 50), (0, 0, w, h), 3)

        # Grill grates
        for i in range(4):
            y_pos = 10 + i * 12
            pygame.draw.line(surface, (80, 80, 90), (8, y_pos), (w-8, y_pos), 2)

        # Control knobs
        for i in range(2):
            x_pos = 20 + i * (w - 60)
            pygame.draw.circle(surface, (120, 120, 130), (x_pos, h-15), 8)
            pygame.draw.circle(surface, (60, 60, 70), (x_pos, h-15), 8, 2)

    def draw_steel_counter(self, surface):
        """Draw a stainless steel counter with realistic highlights"""
        w, h = surface.get_size()

        # Base steel color
        surface.fill(self.COLORS['counter_steel'])

        # Add metallic highlights
        highlight_rect = pygame.Rect(0, 5, w, h//3)
        pygame.draw.rect(surface, (200, 200, 210), highlight_rect)

        # Edge shadows
        pygame.draw.rect(surface, (140, 140, 150), (0, 0, w, h), 2)

    def draw_employee_character(self, surface, uniform_color):
        """Draw a realistic employee character"""
        w, h = surface.get_size()

        # Body (uniform)
        body_rect = pygame.Rect(8, h//2, w-16, h//2-8)
        pygame.draw.rect(surface, uniform_color, body_rect)
        pygame.draw.rect(surface, tuple(max(0, c-30) for c in uniform_color), body_rect, 2)

        # Head
        head_center = (w//2, h//4)
        pygame.draw.circle(surface, (255, 220, 177), head_center, w//4)
        pygame.draw.circle(surface, (200, 180, 140), head_center, w//4, 1)

        # Simple facial features
        # Eyes
        pygame.draw.circle(surface, (60, 60, 60), (head_center[0]-4, head_center[1]-2), 2)
        pygame.draw.circle(surface, (60, 60, 60), (head_center[0]+4, head_center[1]-2), 2)

    def create_professional_ui_elements(self):
        """Create professional UI elements"""
        # Anxiety meter with gradient
        self.surfaces['anxiety_meter'] = pygame.Surface((340, 50), pygame.SRCALPHA)
        self.draw_anxiety_meter_bg(self.surfaces['anxiety_meter'])

        # Order ticket with realistic paper texture
        self.surfaces['order_ticket'] = pygame.Surface((140, 120), pygame.SRCALPHA)
        self.draw_order_ticket(self.surfaces['order_ticket'])

    def draw_anxiety_meter_bg(self, surface):
        """Draw professional anxiety meter background"""
        w, h = surface.get_size()

        # Background panel
        bg_rect = pygame.Rect(10, 10, w-20, h-20)
        pygame.draw.rect(surface, self.COLORS['ui_background'], bg_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLORS['text_dark'], bg_rect, 2, border_radius=8)

        # Meter track
        track_rect = pygame.Rect(50, 20, w-100, 10)
        pygame.draw.rect(surface, (200, 200, 200), track_rect, border_radius=5)

    def draw_order_ticket(self, surface):
        """Draw a realistic order ticket"""
        w, h = surface.get_size()

        # Paper background with slight shadow
        shadow_rect = pygame.Rect(3, 3, w-3, h-3)
        pygame.draw.rect(surface, (180, 180, 180), shadow_rect, border_radius=3)

        paper_rect = pygame.Rect(0, 0, w-3, h-3)
        pygame.draw.rect(surface, self.COLORS['order_paper'], paper_rect, border_radius=3)
        pygame.draw.rect(surface, (200, 200, 200), paper_rect, 1, border_radius=3)

    def setup_enhanced_workplace(self):
        """Set up the enhanced workplace"""
        # Create realistic orders
        self.create_realistic_orders()

        # Initialize particle systems
        self.init_enhanced_particles()

        # Set workplace layout
        self.layout = {
            'grill_station': pygame.Rect(480, 350, 128, 64),
            'prep_counter': pygame.Rect(300, 420, 300, 32),
            'order_board': pygame.Rect(50, 80, 800, 140),
            'customer_area': pygame.Rect(100, 550, 600, 100)
        }

    def create_realistic_orders(self):
        """Create realistic burger orders"""
        order_types = [
            {"name": "Classic Burger", "time": 180, "urgency": "normal"},
            {"name": "Cheeseburger", "time": 200, "urgency": "normal"},
            {"name": "Double Bacon", "time": 240, "urgency": "high"},
            {"name": "Chicken Deluxe", "time": 160, "urgency": "normal"},
            {"name": "Fish Sandwich", "time": 220, "urgency": "low"}
        ]

        for i in range(random.randint(3, 5)):
            order = random.choice(order_types).copy()
            order['id'] = f"#{100 + i}"
            order['position'] = (80 + i * 160, 100)
            order['time_remaining'] = order['time']
            self.order_queue.append(order)

    def init_enhanced_particles(self):
        """Initialize enhanced particle effects"""
        # Steam particles
        for i in range(12):
            self.steam_particles.append({
                'x': 540 + random.uniform(-20, 20),
                'y': 380 + random.uniform(-5, 5),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-1.5, -0.8),
                'life': random.uniform(2.0, 3.5),
                'max_life': 3.5,
                'size': random.uniform(2, 6)
            })

    def start(self):
        """Start the enhanced workday anxiety activity"""
        print("[ENHANCED_WORKDAY] Starting anxiety simulation...")
        self.active = True
        self.completed = False
        self.timer = 0.0
        self.anxiety_level = 15
        self.scene_progress = 0
        self.ready_for_breathing = False
        self.show_break_prompt = False
        print("[ENHANCED_WORKDAY] Activity started successfully!")

    def update(self, dt):
        """Update enhanced workday anxiety simulation"""
        if not self.active or self.completed:
            return

        self.timer += dt
        self.shift_timer += dt
        self.anxiety_pulse_timer += dt
        self.heart_beat_timer += dt
        self.thought_timer += dt

        # Progressive anxiety build-up
        self.update_anxiety_progression(dt)

        # Update visual effects
        self.update_enhanced_effects(dt)

        # Update workplace simulation
        self.update_workplace_simulation(dt)

        # Update thoughts
        self.update_healthcare_thoughts(dt)

        # Check for breathing trigger
        if self.anxiety_level >= 75 and not self.ready_for_breathing:
            self.ready_for_breathing = True
            self.show_break_prompt = True
            print("[ENHANCED_WORKDAY] Anxiety threshold reached - offering break")

        # Auto-trigger after sufficient time
        if self.timer >= 20.0:
            self.trigger_breathing_exercise()

    def update_anxiety_progression(self, dt):
        """Update anxiety with realistic progression"""
        # Base anxiety increase
        anxiety_rate = 1.2

        # Healthcare-specific anxiety triggers
        if 8 < self.timer < 12:
            anxiety_rate = 2.5  # Thinking about appointment
        elif 15 < self.timer < 18:
            anxiety_rate = 3.0  # Financial pressure peaks

        # Manager watching increases anxiety
        if self.manager['watching']:
            anxiety_rate *= 1.5

        # Failed orders increase anxiety
        if self.orders_failed > 0:
            anxiety_rate += self.orders_failed * 0.5

        self.anxiety_level = min(100, self.anxiety_level + anxiety_rate * dt)

        # Update heart rate
        self.heart_rate = 65 + (self.anxiety_level * 0.7)  # 65-135 BPM range

    def update_enhanced_effects(self, dt):
        """Update visual effects with smooth animations"""
        # Screen shake based on anxiety
        if self.anxiety_level > 60:
            self.screen_shake_intensity = (self.anxiety_level - 60) / 8
        else:
            self.screen_shake_intensity = 0

        # Stress overlay
        if self.anxiety_level > 70:
            target_alpha = (self.anxiety_level - 70) * 2
            self.stress_overlay_alpha += (target_alpha - self.stress_overlay_alpha) * dt * 3
        else:
            self.stress_overlay_alpha = max(0, self.stress_overlay_alpha - dt * 60)

        # Update particles
        self.update_particle_systems(dt)

    def update_workplace_simulation(self, dt):
        """Update workplace elements"""
        # Update orders
        for order in self.order_queue:
            order['time_remaining'] -= dt
            if order['time_remaining'] <= 0:
                self.orders_failed += 1
                self.order_queue.remove(order)
                self.anxiety_level += 8  # Failed order increases anxiety

        # Manager behavior
        self.update_manager_behavior(dt)

        # Coworker behavior
        self.update_coworker_behavior(dt)

    def update_manager_behavior(self, dt):
        """Update manager NPC behavior"""
        self.manager['movement_timer'] += dt

        # Manager starts watching when anxiety is visible
        if self.anxiety_level > 40 and not self.manager['watching']:
            if random.random() < 0.3 * dt:  # 30% chance per second
                self.manager['watching'] = True
                self.manager['patience'] = 90

        # Manager moves occasionally
        if self.manager['movement_timer'] > 3.0:
            self.manager['x'] += random.uniform(-20, 20)
            self.manager['x'] = max(900, min(1100, self.manager['x']))
            self.manager['movement_timer'] = 0

    def update_coworker_behavior(self, dt):
        """Update coworker behavior"""
        # Coworker becomes more stressed as anxiety spreads
        if self.anxiety_level > 50:
            self.coworker['mood'] = 'stressed'
            self.coworker['efficiency'] = 0.6

        # Animate coworker
        self.coworker['sprite_frame'] = int(self.timer * 2) % 4

    def update_healthcare_thoughts(self, dt):
        """Update healthcare-related anxious thoughts"""
        self.thought_timer += dt

        if not self.current_thought and self.thought_timer >= 4.0:
            # Select thought based on anxiety level and timer
            eligible_thoughts = []
            for thought in self.healthcare_thoughts:
                if thought['intensity'] <= self.anxiety_level + 20:
                    eligible_thoughts.append(thought)

            if eligible_thoughts:
                self.current_thought = random.choice(eligible_thoughts).copy()
                self.thought_timer = 0
                self.thought_fade_timer = 0

        elif self.current_thought:
            self.thought_fade_timer += dt
            if self.thought_fade_timer >= self.current_thought['duration']:
                self.current_thought = None

    def update_particle_systems(self, dt):
        """Update all particle effects"""
        # Update steam particles
        for particle in self.steam_particles[:]:
            particle['x'] += particle['vx'] * 60 * dt
            particle['y'] += particle['vy'] * 60 * dt
            particle['life'] -= dt

            if particle['life'] <= 0:
                # Reset particle
                particle['x'] = 540 + random.uniform(-20, 20)
                particle['y'] = 380 + random.uniform(-5, 5)
                particle['life'] = random.uniform(2.0, 3.5)

        # Add stress particles when anxiety is high
        if self.anxiety_level > 80 and random.random() < dt * 5:
            self.stress_particles.append({
                'x': random.uniform(100, 1180),
                'y': random.uniform(100, 620),
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-30, 30),
                'life': 1.0,
                'size': random.uniform(1, 3),
                'color': self.COLORS['anxiety_red']
            })

        # Update stress particles
        for particle in self.stress_particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt

            if particle['life'] <= 0:
                self.stress_particles.remove(particle)

    def handle_event(self, event):
        """Handle enhanced input events"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.show_break_prompt:
                print("[ENHANCED_WORKDAY] Player chose to take a break")
                self.trigger_breathing_exercise()
                return True
            elif event.key == pygame.K_SPACE:
                # Simulate work action
                self.perform_work_action()
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def perform_work_action(self):
        """Simulate performing work (cooking)"""
        if self.order_queue:
            # Complete an order
            completed_order = self.order_queue.pop(0)
            self.orders_completed += 1
            self.burger_count += 1

            # Slight anxiety relief from productivity
            self.anxiety_level = max(10, self.anxiety_level - 3)

            # Add success particle
            self.success_particles.append({
                'x': 540, 'y': 350, 'life': 2.0,
                'text': f"Completed {completed_order['name']}"
            })

    def trigger_breathing_exercise(self):
        """Trigger the breathing exercise transition"""
        print("[ENHANCED_WORKDAY] Triggering breathing exercise...")
        self.completed = True

        if self.objective_manager:
            self.objective_manager.advance_to_next_objective()

    def stop(self):
        """Stop the enhanced activity"""
        print("[ENHANCED_WORKDAY] Activity stopping...")
        self.active = False

    def get_screen_shake_offset(self):
        """Calculate realistic screen shake"""
        if self.screen_shake_intensity <= 0:
            return (0, 0)

        shake_x = math.sin(self.timer * 12) * self.screen_shake_intensity
        shake_y = math.cos(self.timer * 15) * self.screen_shake_intensity
        return (int(shake_x), int(shake_y))

    def draw(self, screen):
        """Render the enhanced workplace anxiety scene"""
        if not self.active:
            return

        # Get screen shake
        shake_x, shake_y = self.get_screen_shake_offset()

        # Draw kitchen background
        screen.blit(self.surfaces['kitchen_bg'], (shake_x, shake_y))

        # Draw workplace elements
        self.draw_workplace_equipment(screen, shake_x, shake_y)

        # Draw characters
        self.draw_characters(screen, shake_x, shake_y)

        # Draw order system
        self.draw_order_system(screen, shake_x, shake_y)

        # Draw particle effects
        self.draw_particles(screen, shake_x, shake_y)

        # Draw UI overlay
        self.draw_enhanced_ui(screen)

        # Draw healthcare thoughts
        if self.current_thought:
            self.draw_healthcare_thought(screen)

        # Draw break prompt
        if self.show_break_prompt:
            self.draw_break_prompt(screen)

        # Draw stress overlay
        if self.stress_overlay_alpha > 0:
            self.draw_stress_overlay(screen)

    def draw_workplace_equipment(self, screen, shake_x, shake_y):
        """Draw realistic workplace equipment"""
        # Grill station
        grill_pos = (480 + shake_x, 350 + shake_y)
        screen.blit(self.surfaces['grill'], grill_pos)

        # Add grill flames if cooking
        if len(self.order_queue) > 0:
            self.draw_grill_flames(screen, grill_pos[0] + 20, grill_pos[1] + 10)

        # Prep counter
        counter_pos = (300 + shake_x, 420 + shake_y)
        screen.blit(self.surfaces['counter'], counter_pos)

    def draw_grill_flames(self, screen, x, y):
        """Draw animated grill flames"""
        flame_height = 15 + math.sin(self.timer * 10) * 5

        for i in range(4):
            flame_x = x + i * 20 + random.uniform(-2, 2)
            flame_y = y - flame_height + random.uniform(-3, 3)

            # Draw flame gradient
            for j in range(int(flame_height)):
                alpha = max(0, 255 - j * 15)
                color = (255, 140 + j * 2, 60, alpha)

                flame_surface = pygame.Surface((8, 2), pygame.SRCALPHA)
                flame_surface.fill(color)
                screen.blit(flame_surface, (flame_x, flame_y + j))

    def draw_characters(self, screen, shake_x, shake_y):
        """Draw characters with animations"""
        # Player character at grill
        player_pos = (520 + shake_x, 300 + shake_y)

        # Add stress animation to player
        if self.anxiety_level > 50:
            stress_offset_x = math.sin(self.timer * 8) * 2
            stress_offset_y = math.cos(self.timer * 10) * 1
            player_pos = (player_pos[0] + stress_offset_x, player_pos[1] + stress_offset_y)

        screen.blit(self.surfaces['player'], player_pos)

        # Draw stress indicators on player
        if self.anxiety_level > 60:
            self.draw_stress_indicators(screen, player_pos[0] + 16, player_pos[1])

        # Manager
        manager_pos = (int(self.manager['x']) + shake_x, self.manager['y'] + shake_y)
        screen.blit(self.surfaces['manager'], manager_pos)

        # Manager watching indicator
        if self.manager['watching']:
            self.draw_watching_indicator(screen, manager_pos[0], manager_pos[1] - 20)

        # Coworker
        coworker_pos = (int(self.coworker['x']) + shake_x, self.coworker['y'] + shake_y)
        screen.blit(self.surfaces['coworker'], coworker_pos)

    def draw_stress_indicators(self, screen, x, y):
        """Draw stress sweat drops or shaking"""
        # Sweat drops
        for i in range(3):
            drop_x = x + random.uniform(-5, 5)
            drop_y = y - 10 + i * 5
            pygame.draw.circle(screen, (180, 220, 255), (int(drop_x), int(drop_y)), 2)

    def draw_watching_indicator(self, screen, x, y):
        """Draw manager watching indicator"""
        # Eye symbol
        eye_surface = pygame.Surface((30, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(eye_surface, (255, 255, 255), (0, 0, 30, 15))
        pygame.draw.ellipse(eye_surface, (60, 60, 60), (0, 0, 30, 15), 2)
        pygame.draw.circle(eye_surface, (40, 40, 40), (15, 7), 5)

        screen.blit(eye_surface, (x, y))

    def draw_order_system(self, screen, shake_x, shake_y):
        """Draw the order board with realistic tickets"""
        board_rect = pygame.Rect(50 + shake_x, 80 + shake_y, 800, 140)

        # Order board background
        pygame.draw.rect(screen, (100, 80, 60), board_rect)
        pygame.draw.rect(screen, self.COLORS['text_dark'], board_rect, 3)

        # Board title
        title = self.fonts['medium'].render("ORDER BOARD", True, self.COLORS['text_light'])
        screen.blit(title, (board_rect.x + 20, board_rect.y + 10))

        # Draw order tickets
        for i, order in enumerate(self.order_queue):
            ticket_x = board_rect.x + 20 + i * 160
            ticket_y = board_rect.y + 50

            self.draw_order_ticket_detailed(screen, ticket_x, ticket_y, order)

    def draw_order_ticket_detailed(self, screen, x, y, order):
        """Draw a detailed order ticket"""
        # Ticket background
        ticket_rect = pygame.Rect(x, y, 140, 80)

        # Paper with shadow
        shadow_rect = ticket_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (160, 160, 160), shadow_rect, border_radius=5)

        pygame.draw.rect(screen, self.COLORS['order_paper'], ticket_rect, border_radius=5)
        pygame.draw.rect(screen, self.COLORS['text_dark'], ticket_rect, 2, border_radius=5)

        # Order details
        id_text = self.fonts['small'].render(f"Order {order['id']}", True, self.COLORS['text_dark'])
        name_text = self.fonts['tiny'].render(order['name'], True, self.COLORS['text_dark'])

        screen.blit(id_text, (x + 8, y + 8))
        screen.blit(name_text, (x + 8, y + 28))

        # Time remaining with urgency color
        time_remaining = int(order['time_remaining'])
        if time_remaining < 30:
            time_color = self.COLORS['anxiety_red']
        elif time_remaining < 60:
            time_color = self.COLORS['warning_yellow']
        else:
            time_color = self.COLORS['success_green']

        time_text = self.fonts['small'].render(f"{time_remaining}s", True, time_color)
        screen.blit(time_text, (x + 8, y + 50))

    def draw_particles(self, screen, shake_x, shake_y):
        """Draw enhanced particle effects"""
        # Steam particles
        for particle in self.steam_particles:
            alpha = int((particle['life'] / particle['max_life']) * 120)
            steam_color = (*self.COLORS['steam_white'][:3], alpha)

            steam_surface = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(steam_surface, steam_color,
                             (int(particle['size']), int(particle['size'])),
                             int(particle['size']))

            screen.blit(steam_surface,
                       (particle['x'] + shake_x - particle['size'],
                        particle['y'] + shake_y - particle['size']))

        # Stress particles
        for particle in self.stress_particles:
            alpha = int(particle['life'] * 255)
            stress_color = (*particle['color'][:3], alpha)

            stress_surface = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(stress_surface, stress_color,
                             (int(particle['size']), int(particle['size'])),
                             int(particle['size']))

            screen.blit(stress_surface,
                       (particle['x'] + shake_x - particle['size'],
                        particle['y'] + shake_y - particle['size']))

    def draw_enhanced_ui(self, screen):
        """Draw professional UI overlay"""
        # Anxiety meter
        self.draw_professional_anxiety_meter(screen)

        # Status panel
        self.draw_status_panel(screen)

        # Heart rate monitor
        if self.heart_rate > 90:
            self.draw_heart_rate_monitor(screen)

    def draw_professional_anxiety_meter(self, screen):
        """Draw a professional anxiety meter"""
        meter_x, meter_y = 50, 50
        meter_width, meter_height = 320, 40

        # Background
        bg_rect = pygame.Rect(meter_x - 10, meter_y - 10, meter_width + 20, meter_height + 20)
        pygame.draw.rect(screen, self.COLORS['ui_background'], bg_rect, border_radius=8)
        pygame.draw.rect(screen, self.COLORS['text_dark'], bg_rect, 2, border_radius=8)

        # Label
        label = self.fonts['medium'].render("STRESS LEVEL", True, self.COLORS['text_dark'])
        screen.blit(label, (meter_x, meter_y - 35))

        # Meter track
        track_rect = pygame.Rect(meter_x, meter_y + 8, meter_width, meter_height - 16)
        pygame.draw.rect(screen, (200, 200, 200), track_rect, border_radius=8)

        # Meter fill with gradient effect
        fill_width = int((self.anxiety_level / 100) * meter_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(meter_x, meter_y + 8, fill_width, meter_height - 16)

            # Color based on anxiety level
            if self.anxiety_level < 30:
                fill_color = self.COLORS['success_green']
            elif self.anxiety_level < 70:
                fill_color = self.COLORS['warning_yellow']
            else:
                fill_color = self.COLORS['anxiety_red']

            # Pulsing effect for high anxiety
            if self.anxiety_level >= 70:
                pulse = abs(math.sin(self.anxiety_pulse_timer * 6)) * 0.3 + 0.7
                fill_color = tuple(int(c * pulse) for c in fill_color)

            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)

        # Percentage text
        percent_text = self.fonts['ui'].render(f"{int(self.anxiety_level)}%", True, self.COLORS['text_dark'])
        screen.blit(percent_text, (meter_x + meter_width + 15, meter_y + 8))

    def draw_status_panel(self, screen):
        """Draw workplace status panel"""
        panel_x, panel_y = 900, 50
        panel_width, panel_height = 320, 120

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, self.COLORS['ui_background'], panel_rect, border_radius=8)
        pygame.draw.rect(screen, self.COLORS['text_dark'], panel_rect, 2, border_radius=8)

        # Status information
        y_offset = panel_y + 15

        shift_time = f"Shift: {int(self.shift_timer // 60)}:{int(self.shift_timer % 60):02d}"
        shift_text = self.fonts['small'].render(shift_time, True, self.COLORS['text_dark'])
        screen.blit(shift_text, (panel_x + 15, y_offset))
        y_offset += 25

        completed_text = self.fonts['small'].render(f"Completed: {self.orders_completed}", True, self.COLORS['text_dark'])
        screen.blit(completed_text, (panel_x + 15, y_offset))
        y_offset += 25

        failed_text = self.fonts['small'].render(f"Failed: {self.orders_failed}", True, self.COLORS['anxiety_red'])
        screen.blit(failed_text, (panel_x + 15, y_offset))
        y_offset += 25

        queue_text = self.fonts['small'].render(f"Queue: {len(self.order_queue)}", True, self.COLORS['text_dark'])
        screen.blit(queue_text, (panel_x + 15, y_offset))

    def draw_heart_rate_monitor(self, screen):
        """Draw heart rate monitor when anxiety is high"""
        monitor_x, monitor_y = 50, 120
        monitor_width, monitor_height = 250, 60

        # Monitor background
        bg_rect = pygame.Rect(monitor_x, monitor_y, monitor_width, monitor_height)
        pygame.draw.rect(screen, (20, 20, 30), bg_rect, border_radius=5)
        pygame.draw.rect(screen, self.COLORS['anxiety_red'], bg_rect, 2, border_radius=5)

        # Heart rate text
        hr_text = self.fonts['medium'].render(f"♥ {int(self.heart_rate)} BPM", True, self.COLORS['anxiety_red'])
        screen.blit(hr_text, (monitor_x + 15, monitor_y + 15))

        # Simple heartbeat line
        line_y = monitor_y + 45
        line_points = []
        for i in range(0, monitor_width - 30, 4):
            beat_intensity = math.sin((i + self.timer * 100) * 0.1) * 10
            line_points.append((monitor_x + 15 + i, line_y + beat_intensity))

        if len(line_points) > 1:
            pygame.draw.lines(screen, self.COLORS['anxiety_red'], False, line_points, 2)

    def draw_healthcare_thought(self, screen):
        """Draw healthcare-related anxious thoughts"""
        thought_text = self.current_thought['text']
        intensity = self.current_thought['intensity']

        # Thought bubble background
        bubble_width = 600
        bubble_height = 120
        bubble_x = (self.SCREEN_WIDTH - bubble_width) // 2
        bubble_y = 200

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Color intensity based on anxiety level
        if intensity > 35:
            bubble_color = (255, 240, 240)  # Light red for high intensity
            border_color = self.COLORS['anxiety_red']
        elif intensity > 20:
            bubble_color = (255, 255, 240)  # Light yellow for medium
            border_color = self.COLORS['warning_yellow']
        else:
            bubble_color = (240, 245, 255)  # Light blue for low
            border_color = (100, 150, 200)

        # Fade effect
        fade_progress = min(1.0, self.thought_fade_timer / 1.0)  # 1 second fade in
        alpha = int(255 * min(1.0, fade_progress))

        # Create surface with alpha
        thought_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)

        # Draw bubble
        pygame.draw.ellipse(thought_surface, (*bubble_color, alpha), (0, 0, bubble_width, bubble_height))
        pygame.draw.ellipse(thought_surface, (*border_color, alpha), (0, 0, bubble_width, bubble_height), 3)

        # Wrap and draw text
        words = thought_text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            text_surface = self.fonts['small'].render(test_line, True, self.COLORS['text_dark'])
            text_width = text_surface.get_width()

            if text_width > bubble_width - 40:  # Leave margin
                if len(current_line) > 1:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        # Draw text lines
        text_start_y = (bubble_height - len(lines) * 25) // 2
        for i, line in enumerate(lines):
            text_surface = self.fonts['small'].render(line, True, (*self.COLORS['text_dark'], alpha))
            text_rect = text_surface.get_rect()
            text_rect.centerx = bubble_width // 2
            text_rect.y = text_start_y + i * 25
            thought_surface.blit(text_surface, text_rect)

        screen.blit(thought_surface, (bubble_x, bubble_y))

    def draw_break_prompt(self, screen):
        """Draw professional break prompt"""
        prompt_width, prompt_height = 500, 140
        prompt_x = (self.SCREEN_WIDTH - prompt_width) // 2
        prompt_y = 400

        prompt_rect = pygame.Rect(prompt_x, prompt_y, prompt_width, prompt_height)

        # Background with pulsing effect
        pulse = abs(math.sin(self.timer * 4)) * 0.3 + 0.7
        bg_color = tuple(int(c * pulse) for c in (80, 120, 160))

        pygame.draw.rect(screen, bg_color, prompt_rect, border_radius=15)
        pygame.draw.rect(screen, self.COLORS['text_light'], prompt_rect, 4, border_radius=15)

        # Prompt text
        lines = [
            "You're feeling overwhelmed!",
            "Your anxiety is affecting your work.",
            "Press E to step outside and breathe"
        ]

        y_offset = prompt_y + 25
        for i, line in enumerate(lines):
            if i == 2:  # Highlight action line
                color = (255, 255, 100)
                font = self.fonts['medium']
            else:
                color = self.COLORS['text_light']
                font = self.fonts['small']

            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = prompt_x + prompt_width // 2
            text_rect.y = y_offset
            screen.blit(text_surface, text_rect)
            y_offset += 30

    def draw_stress_overlay(self, screen):
        """Draw stress visual overlay"""
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)

        # Red tint around edges
        alpha = int(self.stress_overlay_alpha)
        edge_color = (*self.COLORS['anxiety_red'][:3], alpha)

        # Draw gradient from edges
        edge_width = 100
        for i in range(edge_width):
            edge_alpha = int(alpha * (edge_width - i) / edge_width)
            edge_surf_color = (*self.COLORS['anxiety_red'][:3], edge_alpha)

            # Top/bottom edges
            pygame.draw.rect(overlay, edge_surf_color, (0, i, self.SCREEN_WIDTH, 1))
            pygame.draw.rect(overlay, edge_surf_color, (0, self.SCREEN_HEIGHT - i - 1, self.SCREEN_WIDTH, 1))

            # Left/right edges
            pygame.draw.rect(overlay, edge_surf_color, (i, 0, 1, self.SCREEN_HEIGHT))
            pygame.draw.rect(overlay, edge_surf_color, (self.SCREEN_WIDTH - i - 1, 0, 1, self.SCREEN_HEIGHT))

        screen.blit(overlay, (0, 0))
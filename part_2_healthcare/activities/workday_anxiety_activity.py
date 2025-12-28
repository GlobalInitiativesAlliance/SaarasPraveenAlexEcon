"""
Enhanced Workday Anxiety Activity with High-Quality Graphics
Professional workplace scene matching Part 1 visual standards with realistic sprites and animations
"""
import pygame
import math
import random
import os

class WorkdayAnxietyActivity:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Enhanced color palette
        self.COLORS = {
            'background_kitchen': (85, 65, 45),  # Warm kitchen brown
            'counter_steel': (180, 180, 190),   # Stainless steel
            'grill_surface': (60, 60, 70),      # Dark grill surface
            'flame_orange': (255, 140, 60),     # Grill flames
            'steam_white': (240, 240, 250),     # Steam effects
            'anxiety_red': (200, 60, 60),       # Anxiety indicators
            'success_green': (80, 180, 80),     # Success feedback
            'warning_yellow': (255, 200, 60),   # Warning states
            'text_dark': (40, 40, 40),          # Primary text
            'text_light': (200, 200, 200),      # Light text
            'shadow': (0, 0, 0, 60),            # Semi-transparent shadows
            'highlight': (255, 255, 255, 100),  # Highlights
            'ui_background': (250, 245, 240),   # UI panel background
            'button_default': (120, 140, 160),  # Default button
            'button_hover': (140, 160, 180),    # Hovered button
            'button_pressed': (100, 120, 140),  # Pressed button
        }

        # Game state
        self.timer = 0.0
        self.anxiety_level = 10  # Start with mild workplace stress
        self.scene_progress = 0
        self.ready_for_breathing = False
        self.show_break_prompt = False
        self.workplace_sounds_timer = 0

        # Enhanced workplace state
        self.burger_count = 0
        self.orders_completed = 0
        self.orders_failed = 0
        self.shift_timer = 0.0
        self.manager_watching = False
        self.customer_satisfaction = 85
        self.current_task = "Cooking burgers"
        self.task_difficulty = 1.0

        # Enhanced visual effects
        self.anxiety_pulse_timer = 0
        self.screen_shake_intensity = 0
        self.heart_beat_timer = 0
        self.heart_rate = 60  # BPM, increases with anxiety
        self.breath_visualization = 0
        self.stress_overlay_alpha = 0

        # Advanced particle systems
        self.steam_particles = []
        self.smoke_particles = []
        self.spark_particles = []
        self.stress_particles = []

        # Realistic workplace elements
        self.equipment = {
            'grill': {'temp': 350, 'busy': False, 'items': []},
            'fryer': {'temp': 375, 'busy': False, 'items': []},
            'prep_station': {'clean': True, 'busy': False}
        }

        # Enhanced order system
        self.order_queue = []
        self.active_orders = []
        self.completed_orders = []

        # Enhanced NPC system with realistic behavior
        self.npcs = {
            'manager': {
                'x': 1000, 'y': 300, 'sprite_frame': 0,
                'watching': False, 'patience': 100,
                'mood': 'neutral', 'last_interaction': 0,
                'movement_pattern': 'patrol'
            },
            'coworker': {
                'x': 500, 'y': 380, 'sprite_frame': 0,
                'busy': True, 'helping': False,
                'mood': 'stressed', 'efficiency': 0.8,
                'movement_pattern': 'work_station'
            },
            'customers': []  # Dynamic customer queue
        }

        # Enhanced thought system
        self.anxiety_thoughts = [
            {
                "text": "I can't stop thinking about that therapy appointment tomorrow...",
                "intensity": 20,
                "category": "healthcare_worry",
                "duration": 4.0
            },
            {
                "text": "How am I going to afford $150 without insurance?",
                "intensity": 35,
                "category": "financial_stress",
                "duration": 5.0
            },
            {
                "text": "What if my mental health gets worse without treatment?",
                "intensity": 40,
                "category": "health_anxiety",
                "duration": 4.5
            },
            {
                "text": "The manager keeps watching me... I need to focus",
                "intensity": 25,
                "category": "work_pressure",
                "duration": 3.0
            },
            {
                "text": "My hands are shaking. I hope no one notices.",
                "intensity": 30,
                "category": "physical_symptoms",
                "duration": 3.5
            },
            {
                "text": "Everything feels overwhelming right now...",
                "intensity": 45,
                "category": "overwhelm",
                "duration": 4.0
            }
        ]
        self.current_thought = None
        self.thought_timer = 0
        self.thought_fade_timer = 0

        # Professional font system
        self.fonts = {
            'title': pygame.font.Font(None, 42),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 28),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 18),
            'ui': pygame.font.Font(None, 24)
        }

        # Load workplace sprites and assets
        self.load_assets()

        # Initialize enhanced workplace
        self.init_enhanced_workplace()

    def load_assets(self):
        """Load sprites and graphical assets"""
        self.sprites = {}
        self.surfaces = {}

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

            # Load kitchen/restaurant sprite sheets
            kitchen_path = os.path.join(base_dir, 'assets', 'moderninteriors-win', '1_Interiors', '16x16', 'Theme_Sorter', '12_Kitchen_16x16.png')
            grocery_path = os.path.join(base_dir, 'assets', 'moderninteriors-win', '1_Interiors', '16x16', 'Theme_Sorter', '16_Grocery_store_16x16.png')

            # Try to load kitchen sprites
            if os.path.exists(kitchen_path):
                self.sprites['kitchen'] = pygame.image.load(kitchen_path).convert_alpha()
                print("[WORKDAY] Loaded kitchen sprites")
            else:
                print("[WORKDAY] Kitchen sprites not found, using fallback graphics")

            # Try to load grocery/restaurant sprites
            if os.path.exists(grocery_path):
                self.sprites['restaurant'] = pygame.image.load(grocery_path).convert_alpha()
                print("[WORKDAY] Loaded restaurant sprites")

            # Load character sprites
            char_path = os.path.join(base_dir, 'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator', '0_Premade_Characters', '16x16', 'Premade_Character_01.png')
            if os.path.exists(char_path):
                self.sprites['characters'] = pygame.image.load(char_path).convert_alpha()
                print("[WORKDAY] Loaded character sprites")

        except Exception as e:
            print(f"[WORKDAY] Could not load sprites: {e}")
            # Create fallback colored surfaces
            self.create_fallback_graphics()

        # Pre-render UI elements
        self.create_ui_surfaces()

    def create_fallback_graphics(self):
        """Create simple colored surfaces as fallbacks"""
        tile_size = 32

        # Kitchen equipment fallbacks
        self.surfaces['grill'] = pygame.Surface((tile_size * 3, tile_size * 2))
        self.surfaces['grill'].fill(self.COLORS['grill_surface'])

        self.surfaces['counter'] = pygame.Surface((tile_size * 4, tile_size))
        self.surfaces['counter'].fill(self.COLORS['counter_steel'])

        # Character fallbacks
        self.surfaces['player'] = pygame.Surface((tile_size, tile_size * 2))
        self.surfaces['player'].fill((100, 150, 200))  # Blue uniform

        self.surfaces['manager'] = pygame.Surface((tile_size, tile_size * 2))
        self.surfaces['manager'].fill((150, 100, 100))  # Brown manager outfit

        self.surfaces['coworker'] = pygame.Surface((tile_size, tile_size * 2))
        self.surfaces['coworker'].fill((100, 200, 150))  # Green uniform

    def create_ui_surfaces(self):
        """Pre-render UI elements for better performance"""
        # Anxiety meter background
        self.surfaces['anxiety_bg'] = pygame.Surface((320, 40))
        self.surfaces['anxiety_bg'].fill(self.COLORS['ui_background'])
        pygame.draw.rect(self.surfaces['anxiety_bg'], self.COLORS['text_dark'],
                        self.surfaces['anxiety_bg'].get_rect(), 2)

        # Order ticket template
        self.surfaces['order_ticket'] = pygame.Surface((120, 100))
        self.surfaces['order_ticket'].fill((255, 255, 240))  # Off-white paper
        pygame.draw.rect(self.surfaces['order_ticket'], self.COLORS['text_dark'],
                        self.surfaces['order_ticket'].get_rect(), 1)

    def get_sprite_tile(self, sheet_name, tile_x, tile_y, tile_size=16):
        """Extract a tile from a sprite sheet"""
        if sheet_name not in self.sprites:
            return None

        sheet = self.sprites[sheet_name]
        rect = pygame.Rect(tile_x * tile_size, tile_y * tile_size, tile_size, tile_size)

        try:
            tile_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            tile_surface.blit(sheet, (0, 0), rect)
            return pygame.transform.scale(tile_surface, (32, 32))  # Scale to display size
        except:
            return None

    def init_enhanced_workplace(self):
        """Initialize the enhanced workplace environment"""
        # Create realistic order queue
        self.create_initial_orders()

        # Initialize enhanced particle systems
        self.init_particle_systems()

        # Set up workplace layout with sprites
        self.setup_workplace_layout()

        # Initialize customer queue
        self.spawn_initial_customers()

    def create_initial_orders(self):
        """Create realistic initial orders"""
        order_types = [
            {"name": "Classic Burger", "time": 180, "difficulty": 1.0, "value": 8.99},
            {"name": "Cheeseburger", "time": 200, "difficulty": 1.2, "value": 9.49},
            {"name": "Double Burger", "time": 240, "difficulty": 1.8, "value": 11.99},
            {"name": "Chicken Sandwich", "time": 160, "difficulty": 0.9, "value": 8.49},
            {"name": "Fish Sandwich", "time": 220, "difficulty": 1.5, "value": 9.99}
        ]

        # Create 3-5 initial orders
        for i in range(random.randint(3, 5)):
            order = random.choice(order_types).copy()
            order['id'] = f"ORDER_{i + 1}"
            order['position'] = (80 + i * 140, 120)
            order['urgent'] = False
            self.order_queue.append(order)

    def init_particle_systems(self):
        """Initialize enhanced particle systems"""
        # Steam particles for grill
        for i in range(15):
            self.steam_particles.append({
                'x': 520 + random.randint(-30, 30),
                'y': 400 + random.randint(-5, 5),
                'velocity_x': random.uniform(-0.5, 0.5),
                'velocity_y': random.uniform(-2.0, -1.0),
                'life': random.uniform(2.0, 4.0),
                'max_life': 4.0,
                'size': random.uniform(3, 8),
                'opacity': random.randint(80, 120)
            })

        # Stress particles (appear when anxiety is high)
        self.stress_particles = []

        # Spark particles for grill
        self.spark_particles = []

    def setup_workplace_layout(self):
        """Set up the workplace layout with proper positioning"""
        # Define kitchen layout
        self.layout = {
            'grill_station': {'x': 480, 'y': 350, 'width': 120, 'height': 80},
            'prep_counter': {'x': 300, 'y': 420, 'width': 300, 'height': 60},
            'order_board': {'x': 50, 'y': 100, 'width': 800, 'height': 120},
            'customer_counter': {'x': 100, 'y': 500, 'width': 600, 'height': 40},
            'manager_office': {'x': 950, 'y': 280, 'width': 120, 'height': 120}
        }

        # Player starting position (at grill)
        self.player_pos = {'x': 520, 'y': 320}

    def spawn_initial_customers(self):
        """Spawn initial customers in queue"""
        customer_count = random.randint(2, 4)
        for i in range(customer_count):
            customer = {
                'id': f"CUSTOMER_{i}",
                'x': 150 + i * 80,
                'y': 580,
                'patience': random.uniform(60, 120),  # seconds
                'order_placed': False,
                'sprite_variant': i % 3,
                'mood': 'waiting'
            }
            self.npcs['customers'].append(customer)

    def start(self):
        """Start the workday anxiety activity"""
        print("[WORKDAY_ANXIETY] Activity starting...")
        self.active = True
        self.completed = False
        self.timer = 0.0
        self.anxiety_level = 10  # Start with mild anxiety
        self.scene_progress = 0
        self.ready_for_breathing = False
        self.show_break_prompt = False
        self.burger_count = 0
        self.orders_completed = 0
        self.shift_timer = 0.0
        self.manager_watching = False
        self.customer_satisfaction = 80
        self.anxiety_pulse_timer = 0
        self.screen_shake_intensity = 0
        self.heart_beat_timer = 0
        self.heart_rate = 60
        self.current_thought_index = 0
        self.thought_timer = 0
        self.show_thought = False
        self.grill_heat = 50
        self.fluorescent_flicker = 0
        self.workplace_sounds_timer = 0

        self.init_workplace()
        print("[WORKDAY_ANXIETY] Activity started successfully!")

    def stop(self):
        """Stop the workday anxiety activity"""
        print("[WORKDAY_ANXIETY] Activity stopping...")
        self.active = False

    def update(self, dt):
        """Update workday anxiety state"""
        if not self.active or self.completed:
            return

        self.timer += dt
        self.shift_timer += dt
        self.anxiety_pulse_timer += dt
        self.heart_beat_timer += dt
        self.thought_timer += dt
        self.workplace_sounds_timer += dt

        # Build anxiety over time
        self.build_anxiety(dt)

        # Update visual effects
        self.update_visual_effects(dt)

        # Update workplace elements
        self.update_workplace_elements(dt)

        # Update NPCs
        self.update_npcs(dt)

        # Check for breathing exercise trigger
        if self.anxiety_level >= 75 and not self.ready_for_breathing:
            self.ready_for_breathing = True
            self.show_break_prompt = True

        # Auto-advance after enough anxiety build-up
        if self.timer >= 25.0:  # After 25 seconds, force transition
            self.trigger_breathing_exercise()

    def build_anxiety(self, dt):
        """Build anxiety level over time with events"""
        base_rate = 1.0  # Base anxiety increase per second

        # Anxiety increases faster at certain intervals
        if 5 < self.timer < 10:
            base_rate = 1.5  # Manager starts watching
            self.manager['watching'] = True
        elif 10 < self.timer < 15:
            base_rate = 2.0  # Rush period
        elif self.timer > 15:
            base_rate = 2.5  # Peak anxiety period

        self.anxiety_level = min(100, self.anxiety_level + base_rate * dt)

        # Update heart rate based on anxiety
        self.heart_rate = 60 + (self.anxiety_level * 0.8)  # 60-140 BPM range

        # Show anxious thoughts periodically
        if self.thought_timer >= 4.0:  # Every 4 seconds
            self.show_thought = True
            self.current_thought_index = (self.current_thought_index + 1) % len(self.anxiety_thoughts)
            self.thought_timer = 0

        if self.show_thought and self.thought_timer >= 3.0:  # Show for 3 seconds
            self.show_thought = False

    def update_visual_effects(self, dt):
        """Update visual anxiety effects"""
        # Screen shake intensity based on anxiety
        if self.anxiety_level > 50:
            self.screen_shake_intensity = (self.anxiety_level - 50) / 10
        else:
            self.screen_shake_intensity = 0

        # Fluorescent light flicker
        self.fluorescent_flicker += dt * 10
        if self.fluorescent_flicker > 100:
            self.fluorescent_flicker = 0

        # Update steam particles
        for particle in self.steam_particles:
            particle['y'] -= particle['speed'] * dt * 60  # Move up
            particle['opacity'] = max(0, particle['opacity'] - dt * 30)

            # Reset particle when it fades or goes off screen
            if particle['opacity'] <= 0 or particle['y'] < 300:
                particle['x'] = 640 + random.randint(-50, 50)
                particle['y'] = 450 + random.randint(-10, 10)
                particle['opacity'] = random.randint(50, 100)
                particle['size'] = random.randint(3, 8)

    def update_workplace_elements(self, dt):
        """Update grill, orders, and other workplace elements"""
        # Update grill heat
        self.grill_heat = 50 + (self.anxiety_level * 0.3)  # Gets hotter with anxiety

        # Update order timers
        for order in self.order_tickets:
            order['time'] -= dt
            if order['time'] <= 0:
                # Order expired - decrease satisfaction
                self.customer_satisfaction = max(0, self.customer_satisfaction - 10)
                order['time'] = random.randint(120, 300)  # New order

    def update_npcs(self, dt):
        """Update manager and coworker behavior"""
        # Manager becomes more watchful as anxiety increases
        if self.anxiety_level > 40:
            self.manager['watching'] = True
            self.manager['patience'] = max(0, self.manager['patience'] - dt * 2)

        # Coworker gets busier, less helpful
        if self.timer > 10:
            self.coworker['busy'] = True

    def trigger_breathing_exercise(self):
        """Trigger the breathing exercise activity"""
        print("[WORKDAY_ANXIETY] Triggering breathing exercise...")
        self.completed = True

        if self.objective_manager:
            # Advance to breathing exercise objective
            self.objective_manager.advance_to_next_objective()

    def handle_event(self, event):
        """Handle player input"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.show_break_prompt:
                print("[WORKDAY_ANXIETY] Player chose to take a break")
                self.trigger_breathing_exercise()
                return True
            elif event.key == pygame.K_SPACE:
                # Simulate working (cooking burgers)
                self.burger_count += 1
                self.orders_completed += 1
                # Temporarily reduce anxiety slightly from feeling productive
                self.anxiety_level = max(0, self.anxiety_level - 2)
            elif event.key == pygame.K_ESCAPE:
                self.stop()

        return True

    def get_screen_shake_offset(self):
        """Calculate screen shake offset"""
        if self.screen_shake_intensity <= 0:
            return (0, 0)

        shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
        shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
        return (int(shake_x), int(shake_y))

    def draw(self, screen):
        """Render the workday anxiety scene"""
        if not self.active:
            return

        # Get screen shake offset
        shake_x, shake_y = self.get_screen_shake_offset()

        # Background - burger shop interior
        bg_color = (101, 67, 33)  # Brown kitchen background
        if self.fluorescent_flicker % 20 < 2 and self.anxiety_level > 60:
            bg_color = (111, 77, 43)  # Slightly lighter for flicker effect

        screen.fill(bg_color)

        # Draw kitchen counter
        counter_rect = pygame.Rect(200 + shake_x, 400 + shake_y, 800, 100)
        pygame.draw.rect(screen, self.GRAY, counter_rect)
        pygame.draw.rect(screen, self.DARK_GRAY, counter_rect, 3)

        # Draw grill
        grill_rect = pygame.Rect(500 + shake_x, 350 + shake_y, 200, 150)
        grill_color = (139, 69, 19) if self.grill_heat < 60 else (180, 90, 40)
        pygame.draw.rect(screen, grill_color, grill_rect)
        pygame.draw.rect(screen, self.BLACK, grill_rect, 3)

        # Draw steam particles
        for particle in self.steam_particles:
            if particle['opacity'] > 0:
                steam_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
                steam_surface.set_alpha(particle['opacity'])
                steam_color = (200, 200, 200)
                pygame.draw.circle(steam_surface, steam_color,
                                 (particle['size'], particle['size']), particle['size'])
                screen.blit(steam_surface,
                          (particle['x'] + shake_x - particle['size'],
                           particle['y'] + shake_y - particle['size']))

        # Draw player character (simplified)
        player_rect = pygame.Rect(580 + shake_x, 280 + shake_y, 40, 60)
        pygame.draw.rect(screen, (100, 50, 200), player_rect)  # Purple uniform

        # Draw player face with stress indicators
        face_rect = pygame.Rect(585 + shake_x, 285 + shake_y, 30, 30)
        face_color = (255, 220, 177) if self.anxiety_level < 50 else (255, 200, 150)
        pygame.draw.ellipse(screen, face_color, face_rect)

        # Stressed expression
        if self.anxiety_level > 40:
            # Worried eyebrows
            pygame.draw.line(screen, self.BLACK,
                           (590 + shake_x, 295 + shake_y), (595 + shake_x, 292 + shake_y), 2)
            pygame.draw.line(screen, self.BLACK,
                           (605 + shake_x, 292 + shake_y), (610 + shake_x, 295 + shake_y), 2)

        # Draw NPCs
        self.draw_npcs(screen, shake_x, shake_y)

        # Draw order tickets
        self.draw_order_tickets(screen, shake_x, shake_y)

        # Draw anxiety meter
        self.draw_anxiety_meter(screen)

        # Draw workplace UI
        self.draw_workplace_ui(screen, shake_x, shake_y)

        # Draw anxious thoughts
        if self.show_thought:
            self.draw_anxious_thought(screen)

        # Draw break prompt
        if self.show_break_prompt:
            self.draw_break_prompt(screen)

        # Draw title
        title = self.font_large.render("Work Day at Burger Palace", True, self.WHITE)
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)

    def draw_npcs(self, screen, shake_x, shake_y):
        """Draw manager and coworker NPCs"""
        # Manager
        manager_rect = pygame.Rect(self.manager['x'] + shake_x, self.manager['y'] + shake_y, 40, 60)
        manager_color = self.RED if self.manager['watching'] else self.GRAY
        pygame.draw.rect(screen, manager_color, manager_rect)

        # Manager watching indicator
        if self.manager['watching']:
            watch_text = self.font_small.render("Manager watching!", True, self.RED)
            screen.blit(watch_text, (self.manager['x'] + shake_x - 20, self.manager['y'] + shake_y - 30))

        # Coworker
        coworker_rect = pygame.Rect(self.coworker['x'] + shake_x, self.coworker['y'] + shake_y, 35, 55)
        pygame.draw.rect(screen, self.BLUE if not self.coworker['busy'] else self.GRAY, coworker_rect)

    def draw_order_tickets(self, screen, shake_x, shake_y):
        """Draw order tickets on the wall"""
        y_pos = 150
        for i, order in enumerate(self.order_tickets):
            ticket_rect = pygame.Rect(order['x'] + shake_x, y_pos + shake_y, 100, 80)

            # Color based on urgency
            urgency_color = self.WHITE
            if order['time'] < 60:
                urgency_color = self.RED
            elif order['time'] < 120:
                urgency_color = self.ORANGE

            pygame.draw.rect(screen, urgency_color, ticket_rect)
            pygame.draw.rect(screen, self.BLACK, ticket_rect, 2)

            # Order details
            item_text = self.font_tiny.render(order['item'], True, self.BLACK)
            time_text = self.font_tiny.render(f"{int(order['time'])}s", True, self.BLACK)

            screen.blit(item_text, (order['x'] + 5 + shake_x, y_pos + 10 + shake_y))
            screen.blit(time_text, (order['x'] + 5 + shake_x, y_pos + 30 + shake_y))

    def draw_anxiety_meter(self, screen):
        """Draw the anxiety meter with pulsing effect"""
        meter_x = 50
        meter_y = 100
        meter_width = 300
        meter_height = 30

        # Pulsing effect
        pulse = abs(math.sin(self.anxiety_pulse_timer * 3)) * 0.3 + 0.7
        if self.anxiety_level >= 75:
            pulse = abs(math.sin(self.anxiety_pulse_timer * 8)) * 0.5 + 0.5  # Faster pulse

        # Background
        bg_rect = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
        pygame.draw.rect(screen, self.DARK_GRAY, bg_rect)

        # Anxiety level fill
        fill_width = int((self.anxiety_level / 100) * meter_width)
        fill_rect = pygame.Rect(meter_x, meter_y, fill_width, meter_height)

        anxiety_color = self.GREEN
        if self.anxiety_level > 30:
            anxiety_color = self.ORANGE
        if self.anxiety_level > 60:
            anxiety_color = self.RED

        # Apply pulse effect
        if self.anxiety_level >= 75:
            anxiety_color = tuple(int(c * pulse) for c in anxiety_color)

        pygame.draw.rect(screen, anxiety_color, fill_rect)
        pygame.draw.rect(screen, self.WHITE, bg_rect, 2)

        # Label
        label = self.font_medium.render("ANXIETY", True, self.WHITE)
        screen.blit(label, (meter_x, meter_y - 35))

        # Percentage
        percent_text = self.font_small.render(f"{int(self.anxiety_level)}%", True, self.WHITE)
        screen.blit(percent_text, (meter_x + meter_width + 10, meter_y + 5))

        # Heart rate indicator
        if self.anxiety_level > 40:
            heart_text = f"♥ {int(self.heart_rate)} BPM"
            heart_color = self.RED if self.heart_rate > 100 else self.WHITE
            heart_surface = self.font_small.render(heart_text, True, heart_color)
            screen.blit(heart_surface, (meter_x, meter_y + 40))

    def draw_workplace_ui(self, screen, shake_x, shake_y):
        """Draw workplace statistics and indicators"""
        # Shift timer
        shift_text = f"Shift: {int(self.shift_timer // 60)}:{int(self.shift_timer % 60):02d}"
        shift_surface = self.font_medium.render(shift_text, True, self.WHITE)
        screen.blit(shift_surface, (50, 600))

        # Customer satisfaction
        satisfaction_text = f"Customer Satisfaction: {self.customer_satisfaction}%"
        satisfaction_color = self.GREEN if self.customer_satisfaction > 70 else self.RED
        satisfaction_surface = self.font_medium.render(satisfaction_text, True, satisfaction_color)
        screen.blit(satisfaction_surface, (50, 630))

        # Orders completed
        orders_text = f"Orders Completed: {self.orders_completed}"
        orders_surface = self.font_medium.render(orders_text, True, self.WHITE)
        screen.blit(orders_surface, (50, 660))

        # Instructions
        instruction_text = "Press SPACE to cook burgers"
        instruction_surface = self.font_small.render(instruction_text, True, self.LIGHT_GRAY)
        screen.blit(instruction_surface, (900, 650))

    def draw_anxious_thought(self, screen):
        """Draw anxious thought bubbles"""
        if self.current_thought_index < len(self.anxiety_thoughts):
            thought = self.anxiety_thoughts[self.current_thought_index]

            # Thought bubble background
            bubble_rect = pygame.Rect(300, 150, 600, 100)
            pygame.draw.ellipse(screen, (240, 240, 240), bubble_rect)
            pygame.draw.ellipse(screen, self.BLACK, bubble_rect, 2)

            # Thought text
            thought_lines = self.wrap_text(thought, 550)
            y_offset = 0
            for line in thought_lines:
                text_surface = self.font_small.render(line, True, self.BLACK)
                text_rect = text_surface.get_rect(center=(600, 190 + y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += 25

    def draw_break_prompt(self, screen):
        """Draw the prompt to take a break"""
        prompt_rect = pygame.Rect(400, 300, 480, 120)
        pygame.draw.rect(screen, (50, 50, 100), prompt_rect)
        pygame.draw.rect(screen, self.YELLOW, prompt_rect, 3)

        # Prompt text
        prompt_lines = [
            "You're feeling overwhelmed!",
            "Maybe you should take a moment to breathe.",
            "Press E to step outside for a break"
        ]

        y_offset = 0
        for line in prompt_lines:
            color = self.YELLOW if "Press E" in line else self.WHITE
            text_surface = self.font_medium.render(line, True, color)
            text_rect = text_surface.get_rect(center=(640, 340 + y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30

    def wrap_text(self, text, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_surface = self.font_small.render(test_line, True, self.BLACK)

            if text_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
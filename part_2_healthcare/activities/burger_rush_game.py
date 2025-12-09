"""
Burger Rush - Professional Cooking Mini-Game
A fun, engaging burger cooking game with quality graphics, drag-drop mechanics,
and progressive difficulty. Replaces the anxiety simulation with actual gameplay.
"""
import pygame
import random
import math
import os

# Tutorial methods - will be added inline to avoid import issues

class BurgerRushGame:
    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Game state
        self.game_timer = 180.0  # 3 minutes
        self.score = 0
        self.burgers_completed = 0
        self.burgers_failed = 0
        self.current_level = 1
        self.max_level = 5

        # Enhanced color palette
        self.COLORS = {
            'kitchen_bg': (85, 65, 45),
            'counter_steel': (180, 180, 190),
            'grill_surface': (60, 60, 70),
            'ui_background': (250, 245, 240),
            'success_green': (80, 180, 80),
            'warning_orange': (255, 165, 0),
            'danger_red': (220, 60, 60),
            'text_dark': (40, 40, 40),
            'text_light': (240, 240, 240),
            'ingredient_bun_top': (210, 180, 140),
            'ingredient_bun_bottom': (200, 170, 130),
            'ingredient_patty_raw': (180, 50, 50),
            'ingredient_patty_cooked': (139, 69, 19),
            'ingredient_cheese': (255, 215, 0),
            'ingredient_lettuce': (50, 205, 50),
            'ingredient_tomato': (255, 99, 71),
            'ingredient_pickle': (154, 205, 50),
            'ingredient_onion': (255, 255, 224),
            'flame_orange': (255, 140, 60),
            'steam_white': (240, 240, 250),
        }

        # Burger ingredients with cooking properties
        self.ingredients = {
            'bun_top': {'name': 'Top Bun', 'cookable': False, 'cook_time': 0},
            'bun_bottom': {'name': 'Bottom Bun', 'cookable': False, 'cook_time': 0},
            'patty': {'name': 'Beef Patty', 'cookable': True, 'cook_time': 4.0},
            'cheese': {'name': 'Cheese', 'cookable': False, 'cook_time': 0},
            'lettuce': {'name': 'Lettuce', 'cookable': False, 'cook_time': 0},
            'tomato': {'name': 'Tomato', 'cookable': False, 'cook_time': 0},
            'pickle': {'name': 'Pickle', 'cookable': False, 'cook_time': 0},
            'onion': {'name': 'Onion', 'cookable': True, 'cook_time': 2.0},
        }

        # Game mechanics
        self.dragging_ingredient = None
        self.drag_offset = (0, 0)
        self.cooking_items = []  # Items currently on the grill
        self.assembled_burger = []  # Current burger being assembled
        self.order_queue = []
        self.completed_orders = []

        # Visual effects
        self.particles = []
        self.ui_animations = []
        self.screen_shake = 0

        # Game areas (screen regions)
        self.areas = {
            'ingredient_station': pygame.Rect(60, 180, 280, 480),
            'grill': pygame.Rect(380, 220, 250, 180),
            'assembly_station': pygame.Rect(670, 180, 280, 250),
            'order_board': pygame.Rect(980, 80, 280, 580),
            'completed_area': pygame.Rect(670, 460, 280, 120),
            'tutorial_overlay': pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        }

        # Tutorial state
        self.tutorial_active = True
        self.tutorial_step = 0
        self.tutorial_steps = [
            {
                'title': 'Welcome to Burger Rush!',
                'text': 'Drag ingredients from the station to cook delicious burgers!',
                'highlight': 'ingredient_station',
                'action': 'Click anywhere to continue'
            },
            {
                'title': 'Step 1: Cook the Patty',
                'text': 'Drag the beef patty to the grill and watch it cook!',
                'highlight': 'grill',
                'action': 'Drag patty to grill'
            },
            {
                'title': 'Step 2: Perfect Timing',
                'text': 'Click the patty when it turns golden brown for perfect cooking!',
                'highlight': 'grill',
                'action': 'Click when patty is ready'
            },
            {
                'title': 'Step 3: Build Your Burger',
                'text': 'Drag cooked patty and other ingredients to assembly area!',
                'highlight': 'assembly_station',
                'action': 'Build the burger'
            },
            {
                'title': 'Step 4: Serve It Up!',
                'text': 'Click the completed area to serve your burger!',
                'highlight': 'completed_area',
                'action': 'Click to serve'
            }
        ]

        # Setup and load assets
        self.setup_fonts()
        self.load_assets()
        self.generate_initial_orders()

    def load_assets(self):
        """Load kitchen sprites and create fallback graphics"""
        self.sprites = {}
        self.surfaces = {}

        # Initialize pygame font if not already initialized
        if not pygame.font.get_init():
            pygame.font.init()

        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

            # Kitchen sprite paths
            sprite_paths = {
                'kitchen': os.path.join(base_dir, 'assets', 'moderninteriors-win', '1_Interiors', '16x16', 'Theme_Sorter', '12_Kitchen_16x16.png'),
                'grill_anim': os.path.join(base_dir, 'assets', 'moderninteriors-win', '3_Animated_objects', '32x32', 'spritesheets', 'animated_kitchen_bbq_32x32.png'),
                'oven_anim': os.path.join(base_dir, 'assets', 'moderninteriors-win', '3_Animated_objects', '32x32', 'spritesheets', 'animated_kitchen_oven_2cookers_32x32.png')
            }

            # Load sprites if available
            for name, path in sprite_paths.items():
                if os.path.exists(path):
                    self.sprites[name] = pygame.image.load(path).convert_alpha()
                    print(f"[BURGER_RUSH] Loaded {name} sprites")

        except Exception as e:
            print(f"[BURGER_RUSH] Could not load sprites: {e}")

        # Always create fallback graphics
        self.create_game_graphics()

    def create_game_graphics(self):
        """Create high-quality cooking game graphics"""
        # Kitchen background with professional layout
        self.surfaces['kitchen_bg'] = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.draw_kitchen_background(self.surfaces['kitchen_bg'])

        # Enhanced grill with realistic details
        self.surfaces['grill'] = pygame.Surface((250, 180), pygame.SRCALPHA)
        self.draw_realistic_grill(self.surfaces['grill'])

        # High-quality ingredient graphics
        for ingredient_name in self.ingredients.keys():
            self.surfaces[f'ingredient_{ingredient_name}'] = pygame.Surface((60, 45), pygame.SRCALPHA)
            self.draw_realistic_ingredient(self.surfaces[f'ingredient_{ingredient_name}'], ingredient_name)

        # Create cooking state variations
        self.create_cooking_variants()

        # Professional UI elements
        self.create_ui_elements()

        # Tutorial graphics
        self.create_tutorial_graphics()

    def draw_kitchen_background(self, surface):
        """Draw professional kitchen background"""
        # Base kitchen floor
        surface.fill(self.COLORS['kitchen_bg'])

        # Add tile pattern
        tile_size = 32
        for y in range(0, self.SCREEN_HEIGHT, tile_size):
            for x in range(0, self.SCREEN_WIDTH, tile_size):
                if (x // tile_size + y // tile_size) % 2:
                    pygame.draw.rect(surface, (75, 60, 40), (x, y, tile_size, tile_size))

        # Draw station backgrounds
        pygame.draw.rect(surface, self.COLORS['counter_steel'], self.areas['ingredient_station'], border_radius=10)
        pygame.draw.rect(surface, self.COLORS['counter_steel'], self.areas['assembly_station'], border_radius=10)
        pygame.draw.rect(surface, self.COLORS['counter_steel'], self.areas['completed_area'], border_radius=10)
        pygame.draw.rect(surface, self.COLORS['ui_background'], self.areas['order_board'], border_radius=10)

        # Add station labels
        font = pygame.font.Font(None, 24)

        labels = [
            ("INGREDIENTS", self.areas['ingredient_station'].centerx, self.areas['ingredient_station'].y - 20),
            ("GRILL", self.areas['grill'].centerx, self.areas['grill'].y - 20),
            ("ASSEMBLY", self.areas['assembly_station'].centerx, self.areas['assembly_station'].y - 20),
            ("ORDERS", self.areas['order_board'].centerx, self.areas['order_board'].y + 15),
            ("COMPLETED", self.areas['completed_area'].centerx, self.areas['completed_area'].y - 20)
        ]

        for label, x, y in labels:
            text = font.render(label, True, self.COLORS['text_dark'])
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)

    def draw_realistic_grill(self, surface):
        """Draw high-quality grill with realistic details"""
        w, h = surface.get_size()

        # Grill base - stainless steel
        grill_rect = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(surface, self.COLORS['grill_surface'], grill_rect)

        # Add metallic gradient
        for i in range(h//3):
            gradient_color = (min(255, 80 + i), min(255, 80 + i), min(255, 90 + i))
            pygame.draw.line(surface, gradient_color, (0, i), (w, i))

        # Grill grates with realistic spacing and shadows
        grate_spacing = (h - 40) // 6
        for i in range(1, 7):
            y_pos = 20 + i * grate_spacing
            # Shadow under grate
            pygame.draw.line(surface, (30, 30, 35), (8, y_pos + 2), (w-8, y_pos + 2), 3)
            # Main grate
            pygame.draw.line(surface, (100, 100, 110), (8, y_pos), (w-8, y_pos), 3)
            # Highlight on top
            pygame.draw.line(surface, (140, 140, 150), (8, y_pos - 1), (w-8, y_pos - 1), 1)

        # Control panel at bottom
        control_panel = pygame.Rect(10, h - 35, w - 20, 30)
        pygame.draw.rect(surface, (40, 40, 50), control_panel, border_radius=5)

        # Control knobs
        for i in range(3):
            x_pos = 30 + i * ((w - 60) // 2)
            # Knob base
            pygame.draw.circle(surface, (60, 60, 70), (x_pos, h - 20), 15)
            pygame.draw.circle(surface, (100, 100, 110), (x_pos, h - 20), 15, 2)
            # Knob indicator
            pygame.draw.circle(surface, (200, 50, 50), (x_pos - 5, h - 25), 3)
            # Knob center
            pygame.draw.circle(surface, (80, 80, 90), (x_pos, h - 20), 8)

        # Temperature display
        temp_rect = pygame.Rect(w - 80, 10, 70, 25)
        pygame.draw.rect(surface, (20, 20, 30), temp_rect, border_radius=3)
        pygame.draw.rect(surface, (100, 200, 100), temp_rect, 2, border_radius=3)

        # Add grill brand label
        if hasattr(pygame.font, 'Font'):
            font = pygame.font.Font(None, 16)
            brand_text = font.render("GRILL MASTER 3000", True, (200, 200, 200))
            text_rect = brand_text.get_rect(center=(w//2, 10))
            surface.blit(brand_text, text_rect)

    def draw_realistic_ingredient(self, surface, ingredient_name):
        """Draw high-quality, realistic ingredient graphics"""
        w, h = surface.get_size()
        color = self.COLORS.get(f'ingredient_{ingredient_name}', (150, 150, 150))

        if ingredient_name == 'bun_top':
            # Draw realistic top bun with dome shape
            pygame.draw.ellipse(surface, color, (5, 15, w-10, h-20))
            # Add sesame seeds
            seed_positions = [(15, 25), (25, 20), (35, 25), (45, 22), (20, 30), (40, 28)]
            for seed_x, seed_y in seed_positions:
                pygame.draw.ellipse(surface, (255, 255, 200), (seed_x, seed_y, 3, 2))
            # Add highlights
            pygame.draw.ellipse(surface, (240, 200, 160), (8, 18, w-16, 8))

        elif ingredient_name == 'bun_bottom':
            # Draw flat bottom bun
            pygame.draw.ellipse(surface, color, (5, h-25, w-10, 20))
            # Add crust line
            pygame.draw.ellipse(surface, (180, 150, 110), (5, h-25, w-10, 20), 2)

        elif ingredient_name == 'patty':
            # Draw realistic meat patty
            pygame.draw.ellipse(surface, self.COLORS['ingredient_patty_raw'], (8, h//2-6, w-16, 15))
            # Add meat texture
            for i in range(4):
                x_start = 12 + i * 8
                pygame.draw.arc(surface, (150, 40, 40), (x_start, h//2-3, 6, 8), 0, 3.14, 1)
            # Add grill marks if cooked
            pygame.draw.line(surface, (100, 30, 30), (12, h//2), (w-12, h//2-2), 2)
            pygame.draw.line(surface, (100, 30, 30), (15, h//2+3), (w-8, h//2+1), 2)

        elif ingredient_name == 'cheese':
            # Draw melted cheese slice
            cheese_rect = pygame.Rect(6, h//2-4, w-12, 12)
            pygame.draw.rect(surface, color, cheese_rect, border_radius=3)
            # Add melted edges
            pygame.draw.polygon(surface, color, [(6, h//2+4), (4, h//2+6), (8, h//2+8)])
            pygame.draw.polygon(surface, color, [(w-6, h//2+4), (w-4, h//2+6), (w-8, h//2+8)])
            # Add shine
            pygame.draw.ellipse(surface, (255, 235, 20), (12, h//2-2, 8, 4))

        elif ingredient_name == 'lettuce':
            # Draw detailed lettuce leaf
            pygame.draw.ellipse(surface, color, (4, h//2-8, w-8, 18))
            # Add leaf veins
            vein_color = (30, 150, 30)
            pygame.draw.lines(surface, vein_color, False, [(8, h//2), (w//2, h//2-4), (w-8, h//2+2)], 1)
            pygame.draw.lines(surface, vein_color, False, [(10, h//2+3), (w//2, h//2+1), (w-10, h//2+5)], 1)
            # Add ruffled edges
            for i in range(0, w-8, 4):
                y_offset = random.randint(-2, 2)
                pygame.draw.circle(surface, color, (6 + i, h//2 + 6 + y_offset), 2)

        elif ingredient_name == 'tomato':
            # Draw juicy tomato slice
            pygame.draw.ellipse(surface, color, (6, h//2-5, w-12, 14))
            # Add tomato segments
            center_x, center_y = w//2, h//2
            for i in range(4):
                angle = i * 90
                segment_x = center_x + 8 * math.cos(math.radians(angle))
                segment_y = center_y + 6 * math.sin(math.radians(angle))
                pygame.draw.circle(surface, (255, 180, 150), (int(segment_x), int(segment_y)), 3)
            # Add seeds
            seed_positions = [(20, h//2), (25, h//2-2), (35, h//2+1), (40, h//2-1)]
            for seed_x, seed_y in seed_positions:
                pygame.draw.ellipse(surface, (255, 240, 200), (seed_x, seed_y, 2, 1))

        elif ingredient_name == 'pickle':
            # Draw pickle slice with bumpy texture
            pygame.draw.ellipse(surface, color, (8, h//2-3, w-16, 10))
            # Add pickle bumps
            for i in range(0, w-16, 3):
                bump_y = h//2 + random.randint(-2, 2)
                pygame.draw.circle(surface, (120, 180, 50), (10 + i, bump_y), 1)
            # Add brine shine
            pygame.draw.ellipse(surface, (200, 255, 180), (12, h//2-1, 6, 3))

        elif ingredient_name == 'onion':
            # Draw onion slice with rings
            pygame.draw.ellipse(surface, color, (8, h//2-3, w-16, 10))
            # Add onion rings
            for ring_size in [6, 4, 2]:
                ring_rect = pygame.Rect(w//2 - ring_size, h//2 - ring_size//2, ring_size*2, ring_size)
                pygame.draw.ellipse(surface, (245, 245, 235), ring_rect, 1)

        # Add realistic shadow
        shadow_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(2, 2, w-2, h-2)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 30), shadow_rect)
        surface.blit(shadow_surface, (0, 0))

    def create_cooking_variants(self):
        """Create different cooking states for ingredients"""
        # Create cooked versions of cookable ingredients
        cookable_ingredients = ['patty', 'onion']

        for ingredient in cookable_ingredients:
            # Raw state (already created)
            # Cooking state
            self.surfaces[f'ingredient_{ingredient}_cooking'] = pygame.Surface((60, 45), pygame.SRCALPHA)
            self.draw_cooking_ingredient(self.surfaces[f'ingredient_{ingredient}_cooking'], ingredient, 'cooking')

            # Cooked state
            self.surfaces[f'ingredient_{ingredient}_cooked'] = pygame.Surface((60, 45), pygame.SRCALPHA)
            self.draw_cooking_ingredient(self.surfaces[f'ingredient_{ingredient}_cooked'], ingredient, 'cooked')

            # Perfect state
            self.surfaces[f'ingredient_{ingredient}_perfect'] = pygame.Surface((60, 45), pygame.SRCALPHA)
            self.draw_cooking_ingredient(self.surfaces[f'ingredient_{ingredient}_perfect'], ingredient, 'perfect')

            # Burned state
            self.surfaces[f'ingredient_{ingredient}_burned'] = pygame.Surface((60, 45), pygame.SRCALPHA)
            self.draw_cooking_ingredient(self.surfaces[f'ingredient_{ingredient}_burned'], ingredient, 'burned')

    def draw_cooking_ingredient(self, surface, ingredient_name, cook_state):
        """Draw ingredients in different cooking states"""
        w, h = surface.get_size()

        if ingredient_name == 'patty':
            if cook_state == 'cooking':
                color = (150, 60, 50)  # Slightly browned
                pygame.draw.ellipse(surface, color, (8, h//2-6, w-16, 15))
                # Add some browning
                pygame.draw.ellipse(surface, (120, 50, 40), (10, h//2-4, w-20, 11), 2)

            elif cook_state == 'cooked':
                color = self.COLORS['ingredient_patty_cooked']
                pygame.draw.ellipse(surface, color, (8, h//2-6, w-16, 15))
                # Add grill marks
                pygame.draw.line(surface, (80, 40, 20), (12, h//2-2), (w-12, h//2-4), 3)
                pygame.draw.line(surface, (80, 40, 20), (15, h//2+2), (w-8, h//2), 3)

            elif cook_state == 'perfect':
                color = (160, 90, 50)  # Perfect golden brown
                pygame.draw.ellipse(surface, color, (8, h//2-6, w-16, 15))
                # Perfect grill marks
                pygame.draw.line(surface, (60, 30, 15), (12, h//2-2), (w-12, h//2-4), 3)
                pygame.draw.line(surface, (60, 30, 15), (15, h//2+2), (w-8, h//2), 3)
                # Add golden outline
                pygame.draw.ellipse(surface, (255, 215, 0), (6, h//2-8, w-12, 19), 2)

            elif cook_state == 'burned':
                color = (50, 30, 20)  # Burned black
                pygame.draw.ellipse(surface, color, (8, h//2-6, w-16, 15))
                # Add char marks
                for i in range(3):
                    char_x = 12 + i * 8
                    pygame.draw.circle(surface, (30, 20, 10), (char_x, h//2), 2)

        elif ingredient_name == 'onion':
            base_color = self.COLORS['ingredient_onion']

            if cook_state == 'cooking':
                color = (240, 240, 200)  # Slightly translucent
                pygame.draw.ellipse(surface, color, (8, h//2-3, w-16, 10))

            elif cook_state in ['cooked', 'perfect']:
                color = (220, 200, 150)  # Golden caramelized
                pygame.draw.ellipse(surface, color, (8, h//2-3, w-16, 10))
                if cook_state == 'perfect':
                    # Add caramelization highlights
                    pygame.draw.ellipse(surface, (255, 220, 100), (12, h//2-1, w-24, 6))

            elif cook_state == 'burned':
                color = (80, 60, 40)  # Burned brown
                pygame.draw.ellipse(surface, color, (8, h//2-3, w-16, 10))

    def create_tutorial_graphics(self):
        """Create tutorial overlay graphics"""
        # Tutorial background
        self.surfaces['tutorial_bg'] = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.surfaces['tutorial_bg'].fill((0, 0, 0, 150))

        # Arrow graphics
        self.surfaces['arrow_right'] = pygame.Surface((40, 30), pygame.SRCALPHA)
        arrow_points = [(5, 15), (25, 5), (25, 12), (35, 12), (35, 18), (25, 18), (25, 25)]
        pygame.draw.polygon(self.surfaces['arrow_right'], (255, 255, 0), arrow_points)
        pygame.draw.polygon(self.surfaces['arrow_right'], (200, 200, 0), arrow_points, 2)

        # Highlight circle
        self.surfaces['highlight_circle'] = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.surfaces['highlight_circle'], (255, 255, 0, 100), (40, 40), 35)
        pygame.draw.circle(self.surfaces['highlight_circle'], (255, 255, 0), (40, 40), 35, 3)

    def create_ui_elements(self):
        """Create UI graphics"""
        # Order ticket background
        self.surfaces['order_ticket'] = pygame.Surface((280, 120), pygame.SRCALPHA)
        ticket_bg = pygame.Rect(0, 0, 280, 120)
        pygame.draw.rect(self.surfaces['order_ticket'], (255, 255, 240), ticket_bg, border_radius=5)
        pygame.draw.rect(self.surfaces['order_ticket'], (200, 200, 200), ticket_bg, 2, border_radius=5)

        # Score panel
        self.surfaces['score_panel'] = pygame.Surface((300, 100), pygame.SRCALPHA)
        panel_bg = pygame.Rect(0, 0, 300, 100)
        pygame.draw.rect(self.surfaces['score_panel'], self.COLORS['ui_background'], panel_bg, border_radius=10)
        pygame.draw.rect(self.surfaces['score_panel'], self.COLORS['text_dark'], panel_bg, 3, border_radius=10)

    def setup_fonts(self):
        """Setup font system"""
        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 28),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 18),
            'ui': pygame.font.Font(None, 24)
        }

    def generate_initial_orders(self):
        """Create initial burger orders"""
        # Define burger types with ingredients (bottom to top)
        burger_recipes = [
            {
                'name': 'Classic Burger',
                'ingredients': ['bun_bottom', 'patty', 'cheese', 'lettuce', 'tomato', 'bun_top'],
                'time_limit': 45,
                'points': 100,
                'difficulty': 1
            },
            {
                'name': 'Cheeseburger',
                'ingredients': ['bun_bottom', 'patty', 'cheese', 'bun_top'],
                'time_limit': 35,
                'points': 80,
                'difficulty': 1
            },
            {
                'name': 'Deluxe Burger',
                'ingredients': ['bun_bottom', 'patty', 'cheese', 'lettuce', 'tomato', 'pickle', 'onion', 'bun_top'],
                'time_limit': 60,
                'points': 150,
                'difficulty': 2
            },
            {
                'name': 'Double Cheeseburger',
                'ingredients': ['bun_bottom', 'patty', 'cheese', 'patty', 'cheese', 'bun_top'],
                'time_limit': 55,
                'points': 180,
                'difficulty': 3
            },
            {
                'name': 'Veggie Burger',
                'ingredients': ['bun_bottom', 'lettuce', 'tomato', 'onion', 'pickle', 'bun_top'],
                'time_limit': 30,
                'points': 90,
                'difficulty': 1
            }
        ]

        # Generate initial orders based on current level
        orders_to_generate = min(3, 2 + self.current_level)

        for i in range(orders_to_generate):
            # Select recipe based on current level
            available_recipes = [r for r in burger_recipes if r['difficulty'] <= self.current_level]
            recipe = random.choice(available_recipes)

            order = {
                'id': f'#{random.randint(100, 999)}',
                'recipe': recipe.copy(),
                'time_remaining': recipe['time_limit'],
                'position': (0, i * 130),  # Will be positioned in order board
                'urgency': 'normal'
            }

            # Add urgency based on time limit
            if recipe['time_limit'] <= 35:
                order['urgency'] = 'high'
            elif recipe['time_limit'] >= 50:
                order['urgency'] = 'low'

            self.order_queue.append(order)

    def start(self):
        """Start the burger rush game with tutorial"""
        print("[BURGER_RUSH] Starting cooking game...")
        self.active = True
        self.completed = False
        self.game_timer = 180.0
        self.score = 0
        self.burgers_completed = 0
        self.burgers_failed = 0
        self.current_level = 1

        # Reset tutorial to beginning (already initialized in __init__)
        self.tutorial_active = True
        self.tutorial_step = 0

        # Clear game state
        self.dragging_ingredient = None
        self.cooking_items.clear()
        self.assembled_burger.clear()
        self.order_queue.clear()
        self.completed_orders.clear()
        self.particles.clear()

        # Start with a simple tutorial order
        self.create_tutorial_order()
        print("[BURGER_RUSH] Game started with tutorial!")

    def create_tutorial_order(self):
        """Create a simple order for the tutorial"""
        tutorial_order = {
            'id': '#TUTORIAL',
            'recipe': {
                'name': 'Simple Cheeseburger',
                'ingredients': ['bun_bottom', 'patty', 'cheese', 'bun_top'],
                'time_limit': 120,
                'points': 100,
                'difficulty': 1
            },
            'time_remaining': 120,
            'position': (0, 0),
            'urgency': 'tutorial'
        }
        self.order_queue.append(tutorial_order)

    def update(self, dt):
        """Update game state"""
        if not self.active or self.completed:
            return

        # Update game timer
        self.game_timer -= dt
        if self.game_timer <= 0:
            self.end_game()
            return

        # Update cooking items
        self.update_cooking(dt)

        # Update orders
        self.update_orders(dt)

        # Update visual effects
        self.update_particles(dt)
        self.update_animations(dt)

        # Check for new orders
        if len(self.order_queue) < 2 and random.random() < dt * 0.3:  # 30% chance per second
            self.add_new_order()

        # Check level progression
        if self.burgers_completed >= 5 * self.current_level and self.current_level < self.max_level:
            self.level_up()

        # Screen shake decay
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 10)

    def update_cooking(self, dt):
        """Update items on the grill"""
        for item in self.cooking_items[:]:
            item['cook_time'] += dt

            # Check if overcooked
            required_time = self.ingredients[item['type']]['cook_time']
            if item['cook_time'] > required_time * 1.5:
                # Item is burned
                item['burned'] = True
                self.add_particle_effect('smoke', item['position'])

            # Auto-remove severely burned items
            if item['cook_time'] > required_time * 2.0:
                self.cooking_items.remove(item)
                self.add_screen_shake(3)

    def update_orders(self, dt):
        """Update order timers and urgency"""
        for order in self.order_queue[:]:
            order['time_remaining'] -= dt

            # Update urgency
            if order['time_remaining'] <= 10:
                order['urgency'] = 'critical'
            elif order['time_remaining'] <= 20:
                order['urgency'] = 'high'

            # Remove expired orders
            if order['time_remaining'] <= 0:
                self.order_queue.remove(order)
                self.burgers_failed += 1
                self.add_screen_shake(5)
                print(f"[BURGER_RUSH] Order {order['id']} expired!")

    def update_particles(self, dt):
        """Update enhanced particle effects"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt

            # Update rotation for spinning particles
            if 'spin' in particle:
                particle['rotation'] += particle['spin'] * dt

            # Apply gravity to celebration particles
            if particle['type'] == 'celebration':
                particle['vy'] += 100 * dt  # Gravity effect

            # Steam particles rise and fade
            elif particle['type'] == 'steam':
                particle['vy'] -= 5 * dt  # Additional upward force
                particle['size'] = particle['size'] * (1 + 0.5 * dt)  # Expand

            # Sizzle particles fade quickly
            elif particle['type'] == 'sizzle':
                particle['vx'] *= (1 - dt * 2)  # Slow down
                particle['vy'] *= (1 - dt * 2)

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def update_animations(self, dt):
        """Update UI animations"""
        for animation in self.ui_animations[:]:
            animation['timer'] += dt
            if animation['timer'] >= animation['duration']:
                self.ui_animations.remove(animation)

    def add_new_order(self):
        """Add a new order to the queue"""
        if len(self.order_queue) < 4:  # Max 4 orders at once
            # Select harder recipes as level increases
            burger_recipes = [
                {'name': 'Classic Burger', 'ingredients': ['bun_bottom', 'patty', 'cheese', 'lettuce', 'tomato', 'bun_top'], 'time_limit': 45, 'points': 100, 'difficulty': 1},
                {'name': 'Deluxe Burger', 'ingredients': ['bun_bottom', 'patty', 'cheese', 'lettuce', 'tomato', 'pickle', 'onion', 'bun_top'], 'time_limit': 60, 'points': 150, 'difficulty': 2},
                {'name': 'Double Cheeseburger', 'ingredients': ['bun_bottom', 'patty', 'cheese', 'patty', 'cheese', 'bun_top'], 'time_limit': 55, 'points': 180, 'difficulty': 3}
            ]

            available_recipes = [r for r in burger_recipes if r['difficulty'] <= self.current_level + 1]
            recipe = random.choice(available_recipes)

            order = {
                'id': f'#{random.randint(100, 999)}',
                'recipe': recipe.copy(),
                'time_remaining': recipe['time_limit'],
                'position': (0, len(self.order_queue) * 130),
                'urgency': 'normal'
            }

            self.order_queue.append(order)

    def level_up(self):
        """Increase difficulty level"""
        self.current_level += 1
        self.add_ui_animation('level_up', f"LEVEL {self.current_level}!")
        self.add_particle_effect('celebration', (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        print(f"[BURGER_RUSH] Level up! Now level {self.current_level}")

    def add_particle_effect(self, effect_type, position):
        """Add enhanced visual particle effects"""
        x, y = position

        if effect_type == 'smoke':
            for _ in range(5):
                self.particles.append({
                    'x': x + random.uniform(-10, 10),
                    'y': y,
                    'vx': random.uniform(-20, 20),
                    'vy': random.uniform(-50, -20),
                    'life': random.uniform(1.0, 2.0),
                    'max_life': 2.0,
                    'type': 'smoke',
                    'size': random.uniform(3, 8),
                    'color': (100, 100, 100),
                    'rotation': random.uniform(0, 360)
                })

        elif effect_type == 'steam':
            for _ in range(12):
                self.particles.append({
                    'x': x + random.uniform(-15, 15),
                    'y': y,
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-30, -15),
                    'life': random.uniform(1.5, 2.5),
                    'max_life': 2.5,
                    'type': 'steam',
                    'size': random.uniform(2, 6),
                    'color': self.COLORS['steam_white'],
                    'rotation': 0
                })

        elif effect_type == 'celebration':
            for _ in range(20):
                self.particles.append({
                    'x': x + random.uniform(-50, 50),
                    'y': y + random.uniform(-30, 30),
                    'vx': random.uniform(-80, 80),
                    'vy': random.uniform(-120, -40),
                    'life': random.uniform(2.0, 3.5),
                    'max_life': 3.5,
                    'type': 'celebration',
                    'size': random.uniform(4, 12),
                    'color': random.choice([self.COLORS['success_green'], (255, 215, 0), (255, 105, 180), (100, 200, 255)]),
                    'rotation': random.uniform(0, 360),
                    'spin': random.uniform(-180, 180)
                })

        elif effect_type == 'perfect_cook':
            # Special effect for perfect cooking
            for _ in range(10):
                self.particles.append({
                    'x': x + random.uniform(-20, 20),
                    'y': y + random.uniform(-15, 15),
                    'vx': random.uniform(-30, 30),
                    'vy': random.uniform(-40, -10),
                    'life': random.uniform(1.0, 2.0),
                    'max_life': 2.0,
                    'type': 'sparkle',
                    'size': random.uniform(3, 8),
                    'color': (255, 215, 0),
                    'rotation': 0
                })

        elif effect_type == 'sizzle':
            # Sizzle effect for cooking
            for _ in range(6):
                self.particles.append({
                    'x': x + random.uniform(-25, 25),
                    'y': y + random.uniform(-10, 10),
                    'vx': random.uniform(-10, 10),
                    'vy': random.uniform(-20, -5),
                    'life': random.uniform(0.5, 1.0),
                    'max_life': 1.0,
                    'type': 'sizzle',
                    'size': random.uniform(2, 4),
                    'color': (255, 255, 150),
                    'rotation': 0
                })

    def add_ui_animation(self, anim_type, text):
        """Add UI animation"""
        self.ui_animations.append({
            'type': anim_type,
            'text': text,
            'timer': 0,
            'duration': 3.0,
            'position': (self.SCREEN_WIDTH // 2, 100)
        })

    def add_screen_shake(self, intensity):
        """Add screen shake effect"""
        self.screen_shake = intensity

    def end_game(self):
        """End the cooking game"""
        print(f"[BURGER_RUSH] Game ended! Score: {self.score}, Burgers: {self.burgers_completed}")
        self.completed = True

        if self.objective_manager:
            # Always advance - this is meant to be fun, not punishing
            self.objective_manager.advance_to_next_objective()

    def handle_event(self, event):
        """Handle game input events"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_mouse_down(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.handle_mouse_up(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_ingredient:
                self.handle_mouse_drag(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.end_game()
            elif event.key == pygame.K_SPACE:
                # Quick action - flip items on grill
                self.flip_grill_items()

        return True

    def handle_mouse_down(self, pos):
        """Handle mouse down - start dragging ingredients"""
        # Check if clicking on ingredient station
        if self.areas['ingredient_station'].collidepoint(pos):
            # Determine which ingredient was clicked
            rel_x = pos[0] - self.areas['ingredient_station'].x
            rel_y = pos[1] - self.areas['ingredient_station'].y

            # Calculate ingredient grid
            ingredients_per_row = 3
            ingredient_width = 60
            ingredient_height = 50

            col = rel_x // ingredient_width
            row = rel_y // ingredient_height

            ingredient_list = list(self.ingredients.keys())
            ingredient_index = row * ingredients_per_row + col

            if 0 <= ingredient_index < len(ingredient_list):
                ingredient_name = ingredient_list[ingredient_index]

                self.dragging_ingredient = {
                    'type': ingredient_name,
                    'original_pos': pos
                }

                self.drag_offset = (pos[0] - (self.areas['ingredient_station'].x + col * ingredient_width + ingredient_width//2),
                                  pos[1] - (self.areas['ingredient_station'].y + row * ingredient_height + ingredient_height//2))

                print(f"[BURGER_RUSH] Started dragging {ingredient_name}")

        # Check if clicking on grill items
        elif self.areas['grill'].collidepoint(pos):
            for item in self.cooking_items:
                item_rect = pygame.Rect(item['position'][0] - 20, item['position'][1] - 15, 40, 30)
                if item_rect.collidepoint(pos):
                    # Flip the item
                    if not item.get('flipped', False):
                        item['flipped'] = True
                        print(f"[BURGER_RUSH] Flipped {item['type']}")

        # Check if clicking on completed burger to serve
        elif self.areas['completed_area'].collidepoint(pos) and self.assembled_burger:
            self.try_serve_burger()

    def handle_mouse_up(self, pos):
        """Handle mouse release - drop ingredients"""
        if self.dragging_ingredient:
            dropped = False

            # Check if dropping on grill
            if self.areas['grill'].collidepoint(pos):
                if self.ingredients[self.dragging_ingredient['type']]['cookable']:
                    # Add to grill
                    grill_pos = (pos[0] - self.areas['grill'].x, pos[1] - self.areas['grill'].y)

                    cooking_item = {
                        'type': self.dragging_ingredient['type'],
                        'position': pos,
                        'cook_time': 0,
                        'flipped': False,
                        'burned': False
                    }

                    self.cooking_items.append(cooking_item)
                    dropped = True
                    print(f"[BURGER_RUSH] Added {self.dragging_ingredient['type']} to grill")

                    # Add sizzle effect
                    self.add_particle_effect('steam', pos)

            # Check if dropping on assembly station
            elif self.areas['assembly_station'].collidepoint(pos):
                # Add to burger assembly
                ingredient_data = {
                    'type': self.dragging_ingredient['type'],
                    'cooked': False
                }

                # Check if this ingredient was cooked on grill
                for cooked_item in self.cooking_items[:]:
                    if cooked_item['type'] == self.dragging_ingredient['type']:
                        # Check if properly cooked
                        required_time = self.ingredients[cooked_item['type']]['cook_time']

                        if (cooked_item['cook_time'] >= required_time * 0.8 and
                            cooked_item['cook_time'] <= required_time * 1.2 and
                            not cooked_item.get('burned', False)):
                            ingredient_data['cooked'] = True
                            ingredient_data['quality'] = 'perfect' if cooked_item.get('flipped', False) else 'good'
                        else:
                            ingredient_data['quality'] = 'burned' if cooked_item.get('burned', False) else 'raw'

                        self.cooking_items.remove(cooked_item)
                        break

                self.assembled_burger.append(ingredient_data)
                dropped = True
                print(f"[BURGER_RUSH] Added {self.dragging_ingredient['type']} to assembly")

            self.dragging_ingredient = None

    def handle_mouse_drag(self, pos):
        """Handle mouse drag - update dragging position"""
        # Dragging is handled by drawing at mouse position
        pass

    def flip_grill_items(self):
        """Flip all items on the grill (spacebar shortcut)"""
        for item in self.cooking_items:
            if not item.get('flipped', False):
                item['flipped'] = True
                print(f"[BURGER_RUSH] Quick-flipped {item['type']}")

    def try_serve_burger(self):
        """Try to serve the assembled burger to match an order"""
        if not self.assembled_burger:
            return

        # Check against orders
        for order in self.order_queue[:]:
            if self.burger_matches_order(self.assembled_burger, order):
                # Calculate score based on accuracy and time
                base_points = order['recipe']['points']
                time_bonus = max(0, int(order['time_remaining'] * 2))
                quality_bonus = self.calculate_quality_bonus(self.assembled_burger)

                total_points = base_points + time_bonus + quality_bonus
                self.score += total_points
                self.burgers_completed += 1

                # Remove order and clear assembly
                self.order_queue.remove(order)
                self.assembled_burger.clear()

                # Visual feedback
                self.add_particle_effect('celebration', self.areas['completed_area'].center)
                self.add_ui_animation('score', f"+{total_points} pts!")

                print(f"[BURGER_RUSH] Served {order['recipe']['name']} for {total_points} points!")
                return

        # No matching order found
        print("[BURGER_RUSH] Burger doesn't match any order!")
        self.assembled_burger.clear()  # Clear the wrong burger

    def burger_matches_order(self, assembled, order):
        """Check if assembled burger matches the order"""
        required_ingredients = order['recipe']['ingredients']
        assembled_types = [item['type'] for item in assembled]

        # Check if ingredients match (order matters for proper burger assembly)
        return assembled_types == required_ingredients

    def calculate_quality_bonus(self, assembled_burger):
        """Calculate bonus points for cooking quality"""
        bonus = 0
        for item in assembled_burger:
            if item.get('cooked', False):
                if item.get('quality') == 'perfect':
                    bonus += 20
                elif item.get('quality') == 'good':
                    bonus += 10
                # No bonus for raw/burned
        return bonus

    def stop(self):
        """Stop the game"""
        print("[BURGER_RUSH] Game stopping...")
        self.active = False

    def draw(self, screen):
        """Draw the enhanced cooking game"""
        if not self.active:
            return

        # Apply screen shake
        shake_offset = (0, 0)
        if self.screen_shake > 0:
            shake_offset = (random.randint(-int(self.screen_shake), int(self.screen_shake)),
                           random.randint(-int(self.screen_shake), int(self.screen_shake)))

        # Draw kitchen background
        screen.blit(self.surfaces['kitchen_bg'], shake_offset)

        # Draw game areas
        self.draw_ingredient_station(screen, shake_offset)
        self.draw_grill_area(screen, shake_offset)
        self.draw_assembly_station(screen, shake_offset)
        self.draw_order_board(screen, shake_offset)

        # Draw particles
        self.draw_particles(screen, shake_offset)

        # Draw UI
        self.draw_ui(screen)

        # Draw tutorial overlay if active
        if self.tutorial_active:
            self.draw_tutorial(screen)

        # Draw dragging ingredient
        if self.dragging_ingredient:
            self.draw_dragging_ingredient(screen)

        # Draw UI animations
        self.draw_ui_animations(screen)

    def draw_ingredient_station(self, screen, offset):
        """Draw the ingredient selection area"""
        area = self.areas['ingredient_station']
        adjusted_area = area.move(offset)

        # Draw ingredients in a grid
        ingredients_per_row = 3
        ingredient_width = 60
        ingredient_height = 50

        ingredient_list = list(self.ingredients.keys())

        for i, ingredient_name in enumerate(ingredient_list):
            row = i // ingredients_per_row
            col = i % ingredients_per_row

            x = adjusted_area.x + col * ingredient_width + 10
            y = adjusted_area.y + row * ingredient_height + 30

            # Draw ingredient background
            ingredient_rect = pygame.Rect(x, y, ingredient_width - 10, ingredient_height - 10)
            pygame.draw.rect(screen, (255, 255, 255), ingredient_rect, border_radius=5)
            pygame.draw.rect(screen, self.COLORS['text_dark'], ingredient_rect, 2, border_radius=5)

            # Draw ingredient graphic
            ingredient_surface = self.surfaces[f'ingredient_{ingredient_name}']
            ingredient_pos = (x + (ingredient_width - 50) // 2, y + 5)
            screen.blit(ingredient_surface, ingredient_pos)

            # Draw ingredient name
            name_text = self.fonts['tiny'].render(self.ingredients[ingredient_name]['name'], True, self.COLORS['text_dark'])
            name_rect = name_text.get_rect(center=(x + ingredient_width // 2, y + ingredient_height - 15))
            screen.blit(name_text, name_rect)

    def draw_grill_area(self, screen, offset):
        """Draw the enhanced grill with realistic cooking visualization"""
        grill_pos = (self.areas['grill'].x + offset[0], self.areas['grill'].y + offset[1])

        # Draw grill
        screen.blit(self.surfaces['grill'], grill_pos)

        # Draw flames if items are cooking
        if self.cooking_items:
            self.draw_grill_flames(screen, grill_pos[0] + 60, grill_pos[1] + 140)

        # Draw cooking items with enhanced visuals
        for item in self.cooking_items:
            item_pos = (item['position'][0] + offset[0] - 30, item['position'][1] + offset[1] - 22)

            # Determine cooking state and visual
            required_time = self.ingredients[item['type']]['cook_time']
            cook_progress = item['cook_time'] / required_time

            # Select appropriate ingredient surface based on cooking state
            ingredient_surface = None
            if item.get('burned', False):
                ingredient_surface = self.surfaces.get(f'ingredient_{item["type"]}_burned')
            elif cook_progress >= 1.2:
                ingredient_surface = self.surfaces.get(f'ingredient_{item["type"]}_burned')
                item['burned'] = True
            elif cook_progress >= 0.9 and item.get('flipped', False):
                ingredient_surface = self.surfaces.get(f'ingredient_{item["type"]}_perfect')
            elif cook_progress >= 0.8:
                ingredient_surface = self.surfaces.get(f'ingredient_{item["type"]}_cooked')
            elif cook_progress >= 0.3:
                ingredient_surface = self.surfaces.get(f'ingredient_{item["type"]}_cooking')
            else:
                ingredient_surface = self.surfaces.get(f'ingredient_{item["type"]}')

            # Draw the ingredient with cooking state
            if ingredient_surface:
                screen.blit(ingredient_surface, item_pos)
            else:
                # Fallback to colored ellipse
                color = self.get_cooking_color(item["type"], cook_progress, item.get('flipped', False), item.get('burned', False))
                pygame.draw.ellipse(screen, color, pygame.Rect(item_pos[0], item_pos[1], 60, 45))

            # Draw enhanced cooking progress bar
            self.draw_cooking_progress(screen, item, item_pos, required_time)

            # Draw cooking effects
            self.draw_cooking_effects(screen, item, item_pos, cook_progress)

    def get_cooking_color(self, ingredient_type, progress, flipped, burned):
        """Get color based on cooking progress"""
        if burned:
            return (50, 30, 20)
        elif ingredient_type == 'patty':
            if progress < 0.3:
                return self.COLORS['ingredient_patty_raw']
            elif progress < 0.8:
                return (150, 60, 50)  # Cooking
            elif flipped and progress >= 0.9:
                return (160, 90, 50)  # Perfect
            else:
                return self.COLORS['ingredient_patty_cooked']
        return self.COLORS.get(f'ingredient_{ingredient_type}', (150, 150, 150))

    def draw_cooking_progress(self, screen, item, item_pos, required_time):
        """Draw enhanced cooking progress visualization"""
        progress = min(1.0, item['cook_time'] / required_time)

        # Progress bar background
        bar_width = 60
        bar_height = 8
        bar_x = item_pos[0]
        bar_y = item_pos[1] - 15

        bar_bg = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (60, 60, 60), bar_bg, border_radius=4)
        pygame.draw.rect(screen, (200, 200, 200), bar_bg, 2, border_radius=4)

        # Progress fill with color coding
        fill_width = int(bar_width * min(progress, 1.0))
        if fill_width > 0:
            if progress < 0.8:
                fill_color = self.COLORS['warning_orange']
            elif progress < 1.2:
                fill_color = self.COLORS['success_green']
            else:
                fill_color = self.COLORS['danger_red']

            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=4)

        # Optimal cooking zone indicator
        optimal_start = int(bar_width * 0.8)
        optimal_end = int(bar_width * 1.0)
        optimal_rect = pygame.Rect(bar_x + optimal_start, bar_y - 2, optimal_end - optimal_start, bar_height + 4)
        pygame.draw.rect(screen, (255, 255, 255), optimal_rect, 2, border_radius=4)

        # Flip reminder
        if progress >= 0.5 and not item.get('flipped', False):
            flip_text = self.fonts['tiny'].render("FLIP!", True, (255, 255, 0))
            flip_rect = flip_text.get_rect(center=(item_pos[0] + 30, item_pos[1] - 25))
            screen.blit(flip_text, flip_rect)

    def draw_cooking_effects(self, screen, item, item_pos, progress):
        """Draw cooking effects like steam and sizzle"""
        # Steam effect when cooking
        if 0.2 < progress < 1.2 and not item.get('burned', False):
            for i in range(random.randint(1, 3)):
                steam_x = item_pos[0] + 20 + random.randint(-15, 15)
                steam_y = item_pos[1] - 5 + random.randint(-5, 5)
                steam_alpha = random.randint(50, 120)

                steam_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                steam_surface.fill((220, 220, 255, steam_alpha))
                screen.blit(steam_surface, (steam_x, steam_y))

        # Sizzle effect for perfect cooking
        if 0.8 <= progress <= 1.0 and item.get('flipped', False):
            for i in range(2):
                sizzle_x = item_pos[0] + random.randint(5, 55)
                sizzle_y = item_pos[1] + random.randint(10, 35)
                pygame.draw.circle(screen, (255, 255, 150), (sizzle_x, sizzle_y), 2)

        # Smoke when burning
        if item.get('burned', False):
            for i in range(random.randint(2, 4)):
                smoke_x = item_pos[0] + 20 + random.randint(-10, 10)
                smoke_y = item_pos[1] - random.randint(5, 15)
                smoke_alpha = random.randint(80, 150)

                smoke_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                smoke_surface.fill((80, 80, 80, smoke_alpha))
                screen.blit(smoke_surface, (smoke_x, smoke_y))

    def draw_grill_flames(self, screen, x, y):
        """Draw animated grill flames"""
        import time
        flame_time = time.time() * 10

        for i in range(3):
            flame_x = x + i * 25 + random.uniform(-2, 2)
            flame_height = 15 + math.sin(flame_time + i) * 5

            # Draw flame gradient
            for j in range(int(flame_height)):
                alpha = max(50, 200 - j * 10)
                flame_color = self.COLORS['flame_orange'][:3]

                flame_surface = pygame.Surface((8, 2), pygame.SRCALPHA)
                flame_surface.set_alpha(alpha)
                flame_surface.fill(flame_color)
                screen.blit(flame_surface, (flame_x, y - j))

    def draw_assembly_station(self, screen, offset):
        """Draw burger assembly area"""
        area = self.areas['assembly_station']
        adjusted_area = area.move(offset)

        # Draw assembled burger
        if self.assembled_burger:
            burger_y = adjusted_area.centery

            for i, ingredient in enumerate(self.assembled_burger):
                ingredient_y = burger_y - i * 8  # Stack ingredients
                ingredient_x = adjusted_area.centerx - 20

                # Draw ingredient with cooking quality color
                color = self.COLORS[f'ingredient_{ingredient["type"]}']
                if ingredient.get('cooked', False):
                    if ingredient.get('quality') == 'perfect':
                        # Add golden outline for perfect cooking
                        pygame.draw.ellipse(screen, (255, 215, 0), pygame.Rect(ingredient_x - 2, ingredient_y - 2, 44, 34))
                    elif ingredient.get('quality') == 'burned':
                        color = (50, 50, 50)  # Burned color

                pygame.draw.ellipse(screen, color, pygame.Rect(ingredient_x, ingredient_y, 40, 30))

        # Draw assembly instructions
        if self.order_queue:
            next_order = self.order_queue[0]
            instruction_text = self.fonts['small'].render("Build:", True, self.COLORS['text_dark'])
            screen.blit(instruction_text, (adjusted_area.x + 10, adjusted_area.y + 10))

            recipe_text = self.fonts['tiny'].render(next_order['recipe']['name'], True, self.COLORS['text_dark'])
            screen.blit(recipe_text, (adjusted_area.x + 10, adjusted_area.y + 30))

    def draw_order_board(self, screen, offset):
        """Draw the order board with current orders"""
        area = self.areas['order_board']
        adjusted_area = area.move(offset)

        for i, order in enumerate(self.order_queue):
            order_y = adjusted_area.y + 40 + i * 130
            order_rect = pygame.Rect(adjusted_area.x + 10, order_y, 280, 120)

            # Draw order background with urgency color
            bg_color = self.COLORS['ui_background']
            border_color = self.COLORS['text_dark']

            if order['urgency'] == 'critical':
                border_color = self.COLORS['danger_red']
            elif order['urgency'] == 'high':
                border_color = self.COLORS['warning_orange']

            pygame.draw.rect(screen, bg_color, order_rect, border_radius=5)
            pygame.draw.rect(screen, border_color, order_rect, 3, border_radius=5)

            # Draw order details
            order_font = self.fonts['small']
            tiny_font = self.fonts['tiny']

            # Order ID and name
            id_text = order_font.render(f"Order {order['id']}", True, self.COLORS['text_dark'])
            screen.blit(id_text, (order_rect.x + 10, order_rect.y + 10))

            name_text = tiny_font.render(order['recipe']['name'], True, self.COLORS['text_dark'])
            screen.blit(name_text, (order_rect.x + 10, order_rect.y + 30))

            # Time remaining
            time_color = self.COLORS['text_dark']
            if order['time_remaining'] <= 10:
                time_color = self.COLORS['danger_red']
            elif order['time_remaining'] <= 20:
                time_color = self.COLORS['warning_orange']

            time_text = order_font.render(f"Time: {int(order['time_remaining'])}s", True, time_color)
            screen.blit(time_text, (order_rect.x + 10, order_rect.y + 50))

            # Points
            points_text = tiny_font.render(f"Points: {order['recipe']['points']}", True, self.COLORS['text_dark'])
            screen.blit(points_text, (order_rect.x + 10, order_rect.y + 70))

            # Ingredient list
            ingredients_text = "Ingredients: " + " → ".join([ing.replace('_', ' ').title() for ing in order['recipe']['ingredients']])
            if len(ingredients_text) > 35:
                ingredients_text = ingredients_text[:35] + "..."

            ing_text = tiny_font.render(ingredients_text, True, self.COLORS['text_dark'])
            screen.blit(ing_text, (order_rect.x + 10, order_rect.y + 90))

    def draw_particles(self, screen, offset):
        """Draw enhanced particle effects"""
        for particle in self.particles:
            x = particle['x'] + offset[0]
            y = particle['y'] + offset[1]

            # Calculate alpha based on lifetime
            if 'max_life' in particle:
                alpha_ratio = particle['life'] / particle['max_life']
            else:
                alpha_ratio = particle['life'] / 2.0

            alpha = int(alpha_ratio * 255)
            alpha = min(255, max(0, alpha))
            color = particle['color'][:3]

            size = int(particle['size'])
            if size <= 0:
                continue

            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

            if particle['type'] == 'celebration':
                # Draw colorful sparkly particles
                particle_surface.set_alpha(alpha)
                pygame.draw.circle(particle_surface, color, (size, size), size)
                # Add sparkle effect
                for i in range(4):
                    angle = particle.get('rotation', 0) + i * 90
                    spark_x = size + int(size * 0.7 * math.cos(math.radians(angle)))
                    spark_y = size + int(size * 0.7 * math.sin(math.radians(angle)))
                    if 0 <= spark_x < size * 2 and 0 <= spark_y < size * 2:
                        pygame.draw.circle(particle_surface, (255, 255, 255), (spark_x, spark_y), 1)

            elif particle['type'] == 'sparkle':
                # Draw star-shaped sparkles
                particle_surface.set_alpha(alpha)
                center = (size, size)
                points = []
                for i in range(8):
                    angle = i * 45 + particle.get('rotation', 0)
                    radius = size if i % 2 == 0 else size // 2
                    px = center[0] + int(radius * math.cos(math.radians(angle)))
                    py = center[1] + int(radius * math.sin(math.radians(angle)))
                    points.append((px, py))

                if len(points) > 2:
                    pygame.draw.polygon(particle_surface, color, points)

            elif particle['type'] in ['steam', 'smoke']:
                # Draw soft circular particles
                particle_surface.set_alpha(alpha)
                pygame.draw.circle(particle_surface, color, (size, size), size)

            elif particle['type'] == 'sizzle':
                # Draw small bright dots
                particle_surface.set_alpha(alpha)
                pygame.draw.circle(particle_surface, color, (size, size), size)

            else:
                # Default particle
                particle_surface.set_alpha(alpha)
                pygame.draw.circle(particle_surface, color, (size, size), size)

            screen.blit(particle_surface, (x - size, y - size))

    def draw_ui(self, screen):
        """Draw game UI elements"""
        # Score panel
        score_rect = pygame.Rect(20, 20, 300, 80)
        pygame.draw.rect(screen, self.COLORS['ui_background'], score_rect, border_radius=10)
        pygame.draw.rect(screen, self.COLORS['text_dark'], score_rect, 3, border_radius=10)

        # Score text
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, self.COLORS['text_dark'])
        screen.blit(score_text, (score_rect.x + 15, score_rect.y + 10))

        burgers_text = self.fonts['small'].render(f"Completed: {self.burgers_completed}", True, self.COLORS['text_dark'])
        screen.blit(burgers_text, (score_rect.x + 15, score_rect.y + 35))

        level_text = self.fonts['small'].render(f"Level: {self.current_level}", True, self.COLORS['text_dark'])
        screen.blit(level_text, (score_rect.x + 15, score_rect.y + 55))

        # Timer
        timer_rect = pygame.Rect(self.SCREEN_WIDTH - 150, 20, 130, 40)
        pygame.draw.rect(screen, self.COLORS['ui_background'], timer_rect, border_radius=5)
        pygame.draw.rect(screen, self.COLORS['text_dark'], timer_rect, 2, border_radius=5)

        timer_color = self.COLORS['danger_red'] if self.game_timer <= 30 else self.COLORS['text_dark']
        timer_text = self.fonts['medium'].render(f"Time: {int(self.game_timer)}", True, timer_color)
        timer_rect_centered = timer_text.get_rect(center=timer_rect.center)
        screen.blit(timer_text, timer_rect_centered)

        # Instructions
        if not self.order_queue:
            instruction_text = self.fonts['small'].render("No orders yet! Get ready...", True, self.COLORS['text_dark'])
            screen.blit(instruction_text, (20, self.SCREEN_HEIGHT - 60))
        else:
            instruction_lines = [
                "Drag ingredients to grill → cook → drag to assembly → serve!",
                "SPACE: Flip all grill items | ESC: Exit game"
            ]

            for i, line in enumerate(instruction_lines):
                instruction_text = self.fonts['tiny'].render(line, True, self.COLORS['text_dark'])
                screen.blit(instruction_text, (20, self.SCREEN_HEIGHT - 40 + i * 15))

    def draw_dragging_ingredient(self, screen):
        """Draw the ingredient being dragged"""
        if self.dragging_ingredient:
            mouse_pos = pygame.mouse.get_pos()
            ingredient_surface = self.surfaces[f'ingredient_{self.dragging_ingredient["type"]}']

            # Draw with slight transparency and larger size
            drag_surface = pygame.transform.scale(ingredient_surface, (50, 40))
            drag_surface.set_alpha(200)

            drag_pos = (mouse_pos[0] - 25, mouse_pos[1] - 20)
            screen.blit(drag_surface, drag_pos)

    def draw_ui_animations(self, screen):
        """Draw UI animations like score popups"""
        for animation in self.ui_animations:
            if animation['type'] == 'level_up':
                # Large centered level up text
                alpha = int(255 * (1.0 - animation['timer'] / animation['duration']))
                font = self.fonts['title']
                text_surface = font.render(animation['text'], True, (*self.COLORS['success_green'][:3], alpha))
                text_rect = text_surface.get_rect(center=(self.SCREEN_WIDTH // 2, 150))

                # Add scaling effect
                scale = 1.0 + math.sin(animation['timer'] * 8) * 0.1
                scaled_surface = pygame.transform.scale(text_surface,
                                                      (int(text_surface.get_width() * scale),
                                                       int(text_surface.get_height() * scale)))
                scaled_rect = scaled_surface.get_rect(center=text_rect.center)
                screen.blit(scaled_surface, scaled_rect)

            elif animation['type'] == 'score':
                # Score popup
                alpha = int(255 * (1.0 - animation['timer'] / animation['duration']))
                font = self.fonts['medium']
                text_surface = font.render(animation['text'], True, (*self.COLORS['success_green'][:3], alpha))

                # Float upward
                y_offset = animation['timer'] * 30
                pos = (animation['position'][0] - text_surface.get_width() // 2,
                      animation['position'][1] - y_offset)
                screen.blit(text_surface, pos)

    def draw_tutorial(self, screen):
        """Draw the tutorial overlay with instructions"""
        if not self.tutorial_active or self.tutorial_step >= len(self.tutorial_steps):
            return

        current_step = self.tutorial_steps[self.tutorial_step]

        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Highlight the relevant area
        if current_step.get('highlight') and current_step['highlight'] in self.areas:
            highlight_area = self.areas[current_step['highlight']]

            # Create pulsing highlight effect
            import time
            pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5
            highlight_color = (255, 255, 0, int(100 * pulse))

            # Draw highlight circle/rectangle around area
            highlight_surface = pygame.Surface((highlight_area.width + 40, highlight_area.height + 40), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, highlight_color, (0, 0, highlight_area.width + 40, highlight_area.height + 40), border_radius=20)
            screen.blit(highlight_surface, (highlight_area.x - 20, highlight_area.y - 20))

            # Draw arrow pointing to area
            arrow_pos = (highlight_area.centerx, highlight_area.y - 60)
            self.draw_tutorial_arrow(screen, arrow_pos, 'down')

        # Draw instruction panel
        panel_width = 600
        panel_height = 200
        panel_x = (self.SCREEN_WIDTH - panel_width) // 2
        panel_y = 50

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Panel background with gradient
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for i in range(panel_height):
            brightness = 240 - (i // 4)
            color = (min(255, brightness), min(255, brightness-5), min(255, brightness-10))
            pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

        screen.blit(panel_surface, (panel_x, panel_y))
        pygame.draw.rect(screen, (100, 150, 200), panel_rect, 4, border_radius=15)

        # Title
        title_font = self.fonts['large']
        title_text = title_font.render(current_step['title'], True, (50, 100, 150))
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 40))
        screen.blit(title_text, title_rect)

        # Instruction text (word-wrapped)
        instruction_lines = self.wrap_text(current_step['text'], self.fonts['medium'], panel_width - 40)
        y_offset = panel_y + 80

        for line in instruction_lines:
            line_surface = self.fonts['medium'].render(line, True, (60, 60, 60))
            line_rect = line_surface.get_rect(center=(panel_x + panel_width // 2, y_offset))
            screen.blit(line_surface, line_rect)
            y_offset += 30

        # Action hint
        action_text = self.fonts['small'].render(current_step['action'], True, (100, 150, 100))
        action_rect = action_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 30))
        screen.blit(action_text, action_rect)

        # Tutorial progress
        progress_text = f"Step {self.tutorial_step + 1} of {len(self.tutorial_steps)}"
        progress_surface = self.fonts['small'].render(progress_text, True, (100, 100, 100))
        screen.blit(progress_surface, (panel_x + 10, panel_y + panel_height - 20))

        # Skip hint
        skip_text = "Press ESC to skip tutorial"
        skip_surface = self.fonts['tiny'].render(skip_text, True, (150, 150, 150))
        screen.blit(skip_surface, (self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT - 30))

    def draw_tutorial_arrow(self, screen, pos, direction):
        """Draw an animated arrow pointing in the specified direction"""
        import time
        bounce = math.sin(time.time() * 5) * 10

        if direction == 'down':
            arrow_points = [
                (pos[0], pos[1] + bounce),
                (pos[0] - 15, pos[1] - 15 + bounce),
                (pos[0] + 15, pos[1] - 15 + bounce)
            ]
        elif direction == 'right':
            arrow_points = [
                (pos[0] + bounce, pos[1]),
                (pos[0] - 15 + bounce, pos[1] - 15),
                (pos[0] - 15 + bounce, pos[1] + 15)
            ]

        pygame.draw.polygon(screen, (255, 255, 0), arrow_points)
        pygame.draw.polygon(screen, (200, 200, 0), arrow_points, 3)

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_text = ' '.join(current_line)
            text_width = font.size(line_text)[0]

            if text_width > max_width:
                if len(current_line) > 1:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
                else:
                    lines.append(line_text)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        return lines
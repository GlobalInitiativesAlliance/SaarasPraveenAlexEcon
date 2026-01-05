import asyncio
import pygame
import math
import datetime
import os
from src.constants import *
from src.core.game_world import ObjectiveManager, AnimatedPlayer, TileManager, CityMap
from src.core.main_menu import MainMenu
from src.core.scenarios_menu import ScenariosMenu
from src.core.scenarios_menu_v2 import ImprovedScenariosMenu
from src.core.progress_manager import get_progress_manager
from src.core.character_select import CharacterSelect
from src.core.smooth_transition_manager import SmoothTransitionManager
# Old interior imports removed - using narrative system now
# from src.interiors.public.classroom_interior import ClassroomInterior
# from src.interiors.commercial.pizzaplace_interior import PizzaPlaceInterior
# from src.activities.work.pizza_activity import PizzaMakingActivity  # Removed old activity
# from src.interiors.commercial.burgerplace_interior import BurgerPlaceInterior
# from src.interiors.residential.home_interior import HomeInterior
# from src.interiors.residential.japanese_home_interior import JapaneseHomeAuto
# from src.interiors.residential.foster_home_interior import FosterHomeInterior
# from src.interiors.public.community_center_interior import CommunityCenterInterior
# from src.interiors.residential.tlp_apartment_interior import TLPApartmentInterior
# from src.interiors.public.housing_office_interior import HousingOfficeInterior
# from src.interiors.commercial.grocery_store_interior import GroceryStoreInterior
# from src.interiors.public.library_interior import LibraryInterior
from src.core.building_manager import BuildingManager
from src.core.debug_panel import DebugPanel
from src.core.debug_logger import debug_logger, dprint
from src.core.transition_health_manager import TransitionHealthManager
from src.core.debug_system import DebugMenu, apply_debug_settings, is_debug_mode
from src.core.input_manager import initialize_input_manager, process_input_frame, clear_input_buffer
from src.core.performance_monitor import start_frame, end_frame
from src.core.cli_controller import CLIController
from src.core.game_state_api import GameStateAPI
from src.core.scene_manager import SceneManager
from src.core.auto_player import AutoPlayer
from src.core.scenario_completion import ScenarioCompletionHandler

# Pre-load scenario registry at startup
from src.core.scenario_registry import ScenarioRegistry
ScenarioRegistry.load()

# Import sprite cache for web compatibility (actual preload happens after pygame init)
from src.core.sprite_cache import preload_all_sprites


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Economics Adventure")
        self.clock = pygame.time.Clock()

        # Preload all sprites for web compatibility (must be after display init)
        preload_all_sprites()

        # Game states
        self.game_state = 'menu'  # 'menu', 'character_select', 'playing', 'help', 'credits', 'scenarios'
        self.main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scenarios_menu = ScenariosMenu(SCREEN_WIDTH, SCREEN_HEIGHT)  # Legacy menu (fallback)
        self.improved_scenarios_menu = ImprovedScenariosMenu(SCREEN_WIDTH, SCREEN_HEIGHT)  # New improved menu
        self.use_improved_scenarios = True  # Toggle to use new menu
        self.character_select = CharacterSelect(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Progress manager for persistent save/load
        self.progress_manager = get_progress_manager()
        self.selected_character = None

        self.tile_manager = TileManager()
        self.city_map = CityMap()
        self.city_map.tile_manager = self.tile_manager
        self.city_map.load_from_image()

        self.player = AnimatedPlayer(
            self.city_map.width // 2,
            self.city_map.height // 2,
            TILE_SIZE
        )

        # Enable new housing objectives for Part 1
        self.use_housing_objectives = True
        
        # Player attributes needed by task system
        self.player_money = 73.00  # Starting money
        self.player_health = 80
        self.player_stress = 50
        self.player_energy = 70
        self.player_debt = 0
        self.player_work_ready = 0
        self.game_hour = 8  # Starting at 8 AM
        self.mini_game_active = False
        self.current_objective = None
        
        self.objective_manager = ObjectiveManager(self)
        self.player_near_objective = False

        self.camera_x = 0
        self.camera_y = 0
        self.update_camera()

        self.font = pygame.font.Font(None, 20)
        self.show_grid = False

        self.render_map_cache()
        # Don't start objectives until game actually begins
        # self.objective_manager.start()
        
        # Building interiors
        self.current_interior = None
        self.classroom_interior = None
        self.pizzaplace_interior = None
        self.burgerplace_interior = None
        self.home_interior = None
        self.foster_home_interior = None
        self.community_center_interior = None
        self.tlp_apartment_interior = None
        self.housing_office_interior = None
        self.grocery_store_interior = None
        self.library_interior = None

        # Building manager for generic interiors
        self.building_manager = BuildingManager(self)
        self.near_building_with_interior = None

        # Unified scenario completion handler (TV transition effect)
        self.scenario_completion = ScenarioCompletionHandler(self)

        # Debug panel
        self.debug_panel = DebugPanel(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Debug menu system
        self.debug_menu = DebugMenu(self)

        # Initialize input manager with debug mode
        self.input_manager = initialize_input_manager(debug_mode=is_debug_mode())

        # Professional smooth transitions
        self.transition_manager = SmoothTransitionManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Transition health monitoring and user guidance
        self.health_manager = TransitionHealthManager(self)

        # Emergency exit state
        self.emergency_exit_timer = 0

        # Apply debug settings if in debug mode
        if is_debug_mode():
            apply_debug_settings(self)

        # Initialize state management systems
        self.state_api = GameStateAPI(self)
        self.scene_manager = SceneManager(self)
        self.api_server = None  # Will be initialized by CLI if needed

        # CLI controller for command-line arguments
        self.cli_controller = CLIController()

        # Auto-player for automated testing
        self.auto_player = AutoPlayer(self)

    def update_camera(self):
        self.camera_x = self.player.pixel_x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.player.pixel_y - (SCREEN_HEIGHT - UI_HEIGHT) // 2 + TILE_SIZE // 2

        max_camera_x = self.city_map.width * TILE_SIZE - SCREEN_WIDTH
        max_camera_y = self.city_map.height * TILE_SIZE - (SCREEN_HEIGHT - UI_HEIGHT)

        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def render_map_cache(self):
        self.map_cache = {}
        tile_count = 0
        building_count = 0

        for y in range(self.city_map.height):
            for x in range(self.city_map.width):
                tile_data = self.city_map.map_data[y][x]

                if isinstance(tile_data, tuple) and tile_data[0] in ['building', 'building_with_bg']:
                    if tile_data[0] == 'building_with_bg':
                        _, building_key, offset_x, offset_y, bg_info = tile_data
                        bg_tile = self.tile_manager.get_tile(bg_info[0], bg_info[1], bg_info[2])
                        if bg_tile:
                            self.map_cache[(x, y)] = ('background', bg_tile)
                    else:
                        _, building_key, offset_x, offset_y = tile_data

                    building = self.tile_manager.building_data.get(building_key)

                    if building and offset_y < len(building['tiles']) and offset_x < len(building['tiles'][offset_y]):
                        tile_info = building['tiles'][offset_y][offset_x]
                        tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                        if tile:
                            if tile_data[0] == 'building_with_bg':
                                self.map_cache[(x, y)] = ('building_with_bg', bg_tile, tile)
                            else:
                                self.map_cache[(x, y)] = ('building', tile)
                            building_count += 1

                elif isinstance(tile_data, tuple) and tile_data[0] == 'tile':
                    _, tile_info = tile_data
                    tile = self.tile_manager.get_tile(tile_info[0], tile_info[1], tile_info[2])
                    if tile:
                        self.map_cache[(x, y)] = ('tile', tile)
                        tile_count += 1
                elif tile_data == 'grass':
                    tile = self.tile_manager.get_grass_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('grass', tile)
                elif tile_data == 'sidewalk':
                    tile = self.tile_manager.get_sidewalk_tile_for_position(
                        self.city_map.map_data, x, y
                    )
                    if tile:
                        self.map_cache[(x, y)] = ('sidewalk', tile)
                elif tile_data == 'road':
                    tile = self.tile_manager.get_random_tile('road')
                    if tile:
                        self.map_cache[(x, y)] = ('road', tile)
                else:
                    self.map_cache[(x, y)] = ('dirt', None)

        print(f"Map cache rendered: {tile_count} tiles, {building_count} building parts")

    def handle_input(self):
        # REMOVED: Problematic fallback that was auto-completing activities
        # Let activities manage their own lifecycle through proper completion flow
        if self.objective_manager.current_activity:
            activity = self.objective_manager.current_activity
            # If activity is active, block input as intended (normal behavior)
            if hasattr(activity, 'active') and activity.active:
                if activity.__class__.__name__ == 'TransitionScene':
                    print("🎬 [TRANSITION_DEBUG] Input blocked - transition scene active")
                return

        keys = pygame.key.get_pressed()

        # Handle interior movement differently
        if self.current_interior:
            self.current_interior.handle_input(keys)
            return

        if not self.player.moving:
            new_x, new_y = self.player.x, self.player.y

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if new_x > 0:
                    new_x -= 1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if new_x < self.city_map.width - 1:
                    new_x += 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                if new_y > 0:
                    new_y -= 1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if new_y < self.city_map.height - 1:
                    new_y += 1

            if new_x != self.player.x or new_y != self.player.y:
                self.player.move_to(new_x, new_y)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        # Draw interior if active
        if self.current_interior:
            self.current_interior.draw(self.screen)
            # Update interior if it has an update method
            if hasattr(self.current_interior, 'update'):
                self.current_interior.update(1/60.0)  # Assuming 60 FPS
            # Don't draw objective UI if pizza activity is active
            if not (hasattr(self, 'pizzaplace_interior') and self.pizzaplace_interior and
                    self.pizzaplace_interior.active and self.pizzaplace_interior.tutorial_state == "work"):
                self.objective_manager.draw_ui(self.screen)

            # Draw debug panel for interiors too
            self.debug_panel.draw(self.screen, self)
            return

        # Ensure camera values are properly converted to int to avoid floating point glitches
        cam_x = int(self.camera_x)
        cam_y = int(self.camera_y)

        start_x = max(0, cam_x // TILE_SIZE)
        end_x = min((cam_x + SCREEN_WIDTH) // TILE_SIZE + 2, self.city_map.width)
        start_y = max(0, cam_y // TILE_SIZE)
        end_y = min((cam_y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE + 3, self.city_map.height)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - cam_x
                screen_y = y * TILE_SIZE - cam_y

                if (x, y) in self.map_cache:
                    cache_data = self.map_cache[(x, y)]

                    if cache_data[0] == 'dirt':
                        pygame.draw.rect(self.screen, (139, 90, 43),
                                         (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    elif cache_data[0] == 'building_with_bg':
                        _, bg_tile, building_tile = cache_data
                        if bg_tile:
                            self.screen.blit(bg_tile, (screen_x, screen_y))
                        if building_tile:
                            self.screen.blit(building_tile, (screen_x, screen_y))
                    else:
                        tile_type, tile_surface = cache_data
                        if tile_surface:
                            self.screen.blit(tile_surface, (screen_x, screen_y))

                if self.show_grid:
                    pygame.draw.rect(self.screen, GRID_COLOR,
                                     (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        self.player.draw(self.screen, self.camera_x, self.camera_y)
        self.objective_manager.draw_objective_markers(self.screen, self.camera_x, self.camera_y)
        self.draw_ui()

        # Draw debug panel last (on top of everything)
        self.debug_panel.draw(self.screen, self)

        # Draw debug menu (on top of debug panel)
        self.debug_menu.draw(self.screen)

        # Draw smooth transitions last (on top of everything for professional feel)
        self.transition_manager.draw(self.screen)

        # Draw health manager guidance overlay (if active)
        if hasattr(self, 'health_manager'):
            self.health_manager.draw(self.screen)

        # Draw scenario completion transition (TV effect) - on top of everything
        if hasattr(self, 'scenario_completion'):
            self.scenario_completion.draw(self.screen)

    def draw_ui(self):
        # Controls display removed - clean UI
        # Use Y key to toggle debug info if needed
        self.objective_manager.draw_ui(self.screen)

        # Draw hover text for buildings with interiors (but not during TransitionScene)
        if (self.near_building_with_interior and not self.current_interior and
            not (hasattr(self.objective_manager, 'current_activity') and
                 self.objective_manager.current_activity and
                 hasattr(self.objective_manager.current_activity, 'active') and
                 self.objective_manager.current_activity.active and
                 self.objective_manager.current_activity.__class__.__name__ == 'TransitionScene')):

            building_pos, building_name, room_name = self.near_building_with_interior

            # Create hover text
            hover_font = pygame.font.Font(None, 24)
            hover_text = "Press E to enter"
            text_surface = hover_font.render(hover_text, True, (255, 255, 200))

            # Position above player
            player_screen_x = self.player.pixel_x - self.camera_x
            player_screen_y = self.player.pixel_y - self.camera_y - 40

            # Draw background for text
            text_bg = pygame.Surface((text_surface.get_width() + 10, 30))
            text_bg.fill((40, 40, 40))
            text_bg.set_alpha(200)

            bg_x = player_screen_x - text_surface.get_width() // 2 - 5
            bg_y = player_screen_y - 5

            self.screen.blit(text_bg, (bg_x, bg_y))
            self.screen.blit(text_surface, (player_screen_x - text_surface.get_width() // 2, player_screen_y))
    
    def draw_help_screen(self):
        """Draw the help/how to play screen"""
        self.screen.fill((50, 50, 50))
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("How to Play", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Help content
        help_font = pygame.font.Font(None, 24)
        help_lines = [
            "Welcome to Economics Adventure!",
            "",
            "OBJECTIVE:",
            "Navigate through economic challenges as a young person in the city.",
            "Complete objectives to learn about economics, work, and life skills.",
            "",
            "CONTROLS:",
            "WASD - Move your character around the city",
            "E - Interact with buildings and objects",
            "G - Toggle grid view",
            "ESC - Return to menu / Exit buildings",
            "",
            "GAMEPLAY:",
            "• Follow the objectives shown at the top of the screen",
            "• Enter buildings by walking to them and pressing E",
            "• Complete mini-games and activities to earn money",
            "• Make economic decisions that affect your progress",
            "• Learn about budgeting, work, and financial literacy",
            "",
            "Press ESC or ENTER to return to the main menu"
        ]
        
        y_offset = 150
        for line in help_lines:
            if line.startswith(("OBJECTIVE:", "CONTROLS:", "GAMEPLAY:")):
                text_color = (120, 170, 255)  # Blue for headers
            else:
                text_color = (220, 220, 220)
            
            text_surface = help_font.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30


    def draw_credits_screen(self):
        """Draw the credits screen"""
        self.screen.fill((50, 50, 50))
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Credits", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Credits content
        credits_font = pygame.font.Font(None, 28)
        credits_lines = [
            "Economics Adventure",
            "",
            "Created for Economics Education",
            "",
            "This educational game teaches economic concepts",
            "through interactive city exploration and mini-games.",
            "",
            "Special Thanks:",
            "• Educators who inspire learning through games",
            "• Students who engage with economic concepts",
            "• Open source game development community",
            "",
            "",
            "Press ESC or ENTER to return to the main menu"
        ]
        
        y_offset = 200
        for line in credits_lines:
            if line == "Economics Adventure":
                text_color = (120, 170, 255)  # Blue for title
                font = pygame.font.Font(None, 36)
            elif line.startswith("Special Thanks:"):
                text_color = (255, 170, 120)  # Orange for section
                font = credits_font
            else:
                text_color = (220, 220, 220)
                font = credits_font
            
            text_surface = font.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 35 if line == "Economics Adventure" else 30
    
    def show_notification(self, message, color=(255, 255, 255)):
        """Show a notification message"""
        if hasattr(self, 'objective_manager'):
            self.objective_manager.show_notification(message, color)
            
    def start_mini_game(self, mini_game_name):
        """Start a mini-game"""
        # This would be handled by the housing game integration
        self.mini_game_active = True
        
    def advance_time(self, hours):
        """Advance the game time by hours"""
        self.game_hour += hours
        while self.game_hour >= 24:
            self.game_hour -= 24
            # Advance day if needed
            
    def take_screenshot(self):
        """Take a screenshot and save it with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")

    async def run(self):
        running = True

        while running:
            # Start performance monitoring for this frame
            start_frame()

            dt = self.clock.tick(FPS) / 1000.0

            # Process input once per frame for all game states
            frame_events = process_input_frame(self.game_state)

            # Handle menu state
            if self.game_state == 'menu':
                # Check for special events that need immediate handling
                for input_event in frame_events:
                    event = input_event.event
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self.take_screenshot()

                # Process all menu events using centralized system
                if running:  # Only process if we're not quitting
                    action = self.main_menu.handle_events(frame_events)
                    if action:
                        dprint(f"[MENU_DEBUG] Main menu returned action: {action}")
                        if action == 'start_game':
                            print("[MENU_DEBUG] Starting game - switching to character select")
                            clear_input_buffer()  # Clear input buffer during state transition
                            self.game_state = 'character_select'
                            self.character_select.reset()
                        elif action == 'quit':
                            print("[MENU_DEBUG] Quitting game")
                            running = False
                        elif action == 'scenarios':
                            print("[MENU_DEBUG] Opening scenarios menu")
                            clear_input_buffer()  # Clear input buffer during state transition
                            self.game_state = 'scenarios'
                        elif action == 'howto':
                            print("[MENU_DEBUG] Opening help")
                            clear_input_buffer()  # Clear input buffer during state transition
                            self.game_state = 'help'
                        elif action == 'credits':
                            print("[MENU_DEBUG] Opening credits")
                            clear_input_buffer()  # Clear input buffer during state transition
                            self.game_state = 'credits'

                # Draw menu
                self.main_menu.draw(self.screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle character select state
            elif self.game_state == 'character_select':
                # Check for special events that need immediate handling
                for input_event in frame_events:
                    event = input_event.event
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self.take_screenshot()

                # Process character select events using centralized system
                if running:  # Only process if we're not quitting
                    action = self.character_select.handle_events(frame_events)
                    if action == 'character_selected':
                        # Store selected character
                        self.selected_character = self.character_select.selected_character
                        print(f"Selected character: {self.selected_character.name}")
                        # Update player sprite to use selected character
                        self.player.selected_character_index = self.selected_character.sprite_index
                        self.player.load_animations()
                        # Start the game
                        clear_input_buffer()  # Clear input buffer during state transition
                        self.game_state = 'playing'

                        # Determine which part to start based on progress
                        from src.core.progress_manager import get_progress_manager
                        pm = get_progress_manager()

                        # Find the appropriate scenario to start
                        start_part = 1
                        for scenario_id in range(1, 9):
                            progress = pm.get_scenario_progress(scenario_id)
                            if progress:
                                if progress.get("completed", False):
                                    # This scenario is done, try the next one
                                    continue
                                elif progress.get("started", False):
                                    # Resume this scenario
                                    start_part = scenario_id
                                    break
                                elif progress.get("unlocked", False):
                                    # Start this unlocked scenario
                                    start_part = scenario_id
                                    break
                            else:
                                break

                        print(f"[GAME] Starting Part {start_part}")

                        # Set the game part and load objectives if not Part 1
                        if start_part == 1:
                            self.objective_manager.game_part = 1
                            self.objective_manager.load_from_saved_progress(1)
                        elif start_part == 2:
                            self.objective_manager.game_part = 2
                            self.objective_manager.load_part2_objectives()
                            self.player.x, self.player.y = 54, 33
                            self.player.pixel_x = 54 * TILE_SIZE
                            self.player.pixel_y = 33 * TILE_SIZE
                            self.player.target_x = self.player.pixel_x
                            self.player.target_y = self.player.pixel_y
                        elif start_part >= 3:
                            # For parts 3+, load appropriate objectives
                            self.objective_manager.game_part = start_part
                            if start_part == 3:
                                self.objective_manager.load_part3_objectives()
                            elif start_part == 4:
                                self.objective_manager.load_part4_objectives()
                            elif start_part == 5:
                                self.objective_manager.load_part5_objectives()
                            elif start_part == 6:
                                self.objective_manager.load_part6_objectives()
                            elif start_part == 7:
                                self.objective_manager.load_part7_objectives()
                            elif start_part == 8:
                                self.objective_manager.load_part8_objectives()
                            self.player.x, self.player.y = 54, 33
                            self.player.pixel_x = 54 * TILE_SIZE
                            self.player.pixel_y = 33 * TILE_SIZE
                            self.player.target_x = self.player.pixel_x
                            self.player.target_y = self.player.pixel_y

                        # Now start the objective system
                        self.objective_manager.start()
                    elif action == 'back_to_menu':
                        clear_input_buffer()  # Clear input buffer during state transition
                        self.game_state = 'menu'
                        self.main_menu.reset()

                # Draw character selection
                self.character_select.draw(self.screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle help state
            elif self.game_state == 'help':
                for input_event in frame_events:
                    event = input_event.event
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F12:
                            self.take_screenshot()
                        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            clear_input_buffer()  # Clear input buffer during state transition
                            self.game_state = 'menu'
                            self.main_menu.reset()

                self.draw_help_screen()
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle scenarios state
            elif self.game_state == 'scenarios':
                # Check for special events that need immediate handling
                for input_event in frame_events:
                    event = input_event.event
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self.take_screenshot()

                # Process scenarios menu events using centralized system
                if running:  # Only process if we're not quitting
                    # Use improved menu if enabled, otherwise fallback to legacy
                    if self.use_improved_scenarios:
                        action = self.improved_scenarios_menu.handle_events(frame_events)
                    else:
                        action = self.scenarios_menu.handle_events(frame_events)

                    if action == 'start_part1':
                        # Start Part 1: Housing Stability
                        clear_input_buffer()  # Clear input buffer during state transition
                        self.game_state = 'character_select'
                        self.character_select.reset()
                    elif action == 'start_part2':
                        # Start Part 2: Legal System (was Part 3)
                        print("Part 2: Legal System - Starting...")
                        clear_input_buffer()
                        self.objective_manager.game_part = 2
                        self.objective_manager.load_part2_objectives()
                        # Load from saved progress if available
                        self.objective_manager.load_from_saved_progress(2)
                        self.game_state = 'playing'
                        # Start player at TLP apartment for legal system scenario
                        self.player.x = 54
                        self.player.y = 33
                        self.player.pixel_x = 54 * TILE_SIZE
                        self.player.pixel_y = 33 * TILE_SIZE
                        self.player.target_x = self.player.pixel_x
                        self.player.target_y = self.player.pixel_y
                    elif action == 'start_part3':
                        # Start Part 3: Healthcare Crisis (was Part 4)
                        print("Part 3: Healthcare Crisis - Starting...")
                        clear_input_buffer()
                        self.objective_manager.game_part = 3
                        self.objective_manager.load_part3_objectives()
                        # Load from saved progress if available
                        self.objective_manager.load_from_saved_progress(3)
                        self.game_state = 'playing'
                        # Start player at TLP apartment
                        self.player.x = 54
                        self.player.y = 33
                        self.player.pixel_x = 54 * TILE_SIZE
                        self.player.pixel_y = 33 * TILE_SIZE
                        self.player.target_x = self.player.pixel_x
                        self.player.target_y = self.player.pixel_y
                    elif action == 'start_part4':
                        # Start Part 4: Education Journey
                        print("Part 4: Education Journey - Starting...")
                        clear_input_buffer()
                        self.objective_manager.game_part = 4
                        self.objective_manager.load_part4_objectives()
                        # Load from saved progress if available
                        self.objective_manager.load_from_saved_progress(4)
                        self.game_state = 'playing'
                        self.player.x = 54
                        self.player.y = 33
                        self.player.pixel_x = 54 * TILE_SIZE
                        self.player.pixel_y = 33 * TILE_SIZE
                        self.player.target_x = self.player.pixel_x
                        self.player.target_y = self.player.pixel_y
                    elif action == 'start_part5':
                        # Start Part 5: Systemic Barriers
                        print("Part 5: Systemic Barriers - Starting...")
                        clear_input_buffer()
                        self.objective_manager.game_part = 5
                        self.objective_manager.load_part5_objectives()
                        # Load from saved progress if available
                        self.objective_manager.load_from_saved_progress(5)
                        self.game_state = 'playing'
                        self.player.x = 54
                        self.player.y = 33
                        self.player.pixel_x = 54 * TILE_SIZE
                        self.player.pixel_y = 33 * TILE_SIZE
                        self.player.target_x = self.player.pixel_x
                        self.player.target_y = self.player.pixel_y
                    elif action == 'coming_soon':
                        # Show coming soon message (already handled in scenarios_menu)
                        pass
                    elif action == 'back_to_menu':
                        clear_input_buffer()  # Clear input buffer during state transition
                        self.game_state = 'menu'
                        self.main_menu.reset()
                        self.scenarios_menu.reset()
                        if self.use_improved_scenarios:
                            self.improved_scenarios_menu.reset()

                # Draw scenarios menu
                if self.use_improved_scenarios:
                    self.improved_scenarios_menu.draw(self.screen)
                else:
                    self.scenarios_menu.draw(self.screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle credits state
            elif self.game_state == 'credits':
                for input_event in frame_events:
                    event = input_event.event
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F12:
                            self.take_screenshot()
                        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            clear_input_buffer()  # Clear input buffer during state transition
                            self.game_state = 'menu'
                            self.main_menu.reset()

                self.draw_credits_screen()
                pygame.display.flip()
                await asyncio.sleep(0)
                continue
            
            # Normal game loop (playing state)
            for input_event in frame_events:
                event = input_event.event
                if event.type == pygame.QUIT:
                    running = False
                    continue

                # Check if scenario completion transition is active (blocks all input)
                if hasattr(self, 'scenario_completion') and self.scenario_completion.is_transitioning:
                    if self.scenario_completion.handle_event(event):
                        continue  # Event consumed by transition

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F12:
                        self.take_screenshot()
                    elif event.key == pygame.K_F1:
                        # Toggle debug menu
                        self.debug_menu.toggle()
                    elif event.key == pygame.K_F3:
                        # Toggle debug panel
                        self.debug_panel.toggle()
                        debug_logger.info('DEBUG', "Debug panel toggled",
                                        visible=self.debug_panel.visible)
                    elif event.key == pygame.K_F4:
                        # Manual health check for user stuck states
                        if hasattr(self, 'health_manager'):
                            self.health_manager.manual_check()
                            print("[USER_INPUT] Manual health check triggered via F4")
                    elif event.key == pygame.K_ESCAPE:
                        # Check for emergency exit (CTRL+ESC)
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            self.emergency_exit_room()
                        else:
                            if self.current_interior:
                                # Let the interior handle escape first
                                if hasattr(self.current_interior, 'handle_event'):
                                    self.current_interior.handle_event(event)
                                # Check if interior wants to exit
                                if self.current_interior and not self.current_interior.active:
                                    self.current_interior = None
                            else:
                                # Return to menu
                                clear_input_buffer()  # Clear input buffer during state transition
                                self.game_state = 'menu'
                                self.main_menu.reset()
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_t:
                        # Toggle auto-play mode
                        if hasattr(self, 'auto_player'):
                            self.auto_player.toggle()
                    elif event.key == pygame.K_y:
                        # Check if an activity is active (e.g., typing in form)
                        activity_active = (
                            (hasattr(self.objective_manager, 'current_activity') and
                             self.objective_manager.current_activity and
                             hasattr(self.objective_manager.current_activity, 'active') and
                             self.objective_manager.current_activity.active) or
                            (self.current_interior and
                             hasattr(self.current_interior, 'current_activity') and
                             self.current_interior.current_activity and
                             hasattr(self.current_interior.current_activity, 'active') and
                             self.current_interior.current_activity.active) or
                            (hasattr(self.objective_manager, 'activity_manager') and
                             self.objective_manager.activity_manager.current_activity and
                             self.objective_manager.activity_manager.current_activity.active)
                        )
                        if activity_active:
                            # Pass Y key to interior/activity
                            if self.current_interior and hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                        else:
                            # Toggle debug panel with Y key
                            if (hasattr(self.objective_manager, 'ui_manager') and
                                self.objective_manager.ui_manager and
                                hasattr(self.objective_manager.ui_manager, 'toggle_debug')):
                                self.objective_manager.ui_manager.toggle_debug()
                    elif event.key == pygame.K_r:
                        # Check if an activity is active (e.g., typing in form)
                        activity_active = (
                            (hasattr(self.objective_manager, 'current_activity') and
                             self.objective_manager.current_activity and
                             hasattr(self.objective_manager.current_activity, 'active') and
                             self.objective_manager.current_activity.active) or
                            (self.current_interior and
                             hasattr(self.current_interior, 'current_activity') and
                             self.current_interior.current_activity and
                             hasattr(self.current_interior.current_activity, 'active') and
                             self.current_interior.current_activity.active) or
                            (hasattr(self.objective_manager, 'activity_manager') and
                             self.objective_manager.activity_manager.current_activity and
                             self.objective_manager.activity_manager.current_activity.active)
                        )
                        if activity_active:
                            # Pass R key to interior/activity
                            if self.current_interior and hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                        else:
                            # Reload city map
                            self.city_map.load_from_image()
                            self.render_map_cache()
                    elif event.key == pygame.K_e:
                        dprint(f"[MAIN_DEBUG] E key pressed")
                        dprint(f"[MAIN_DEBUG] Current interior: {self.current_interior}")
                        dprint(f"[MAIN_DEBUG] Current activity: {self.objective_manager.current_activity}")

                        # Check if transition scene is active - if so, ignore E key
                        if (hasattr(self.objective_manager, 'current_activity') and
                            self.objective_manager.current_activity and
                            hasattr(self.objective_manager.current_activity, 'active') and
                            self.objective_manager.current_activity.active and
                            self.objective_manager.current_activity.__class__.__name__ == 'TransitionScene'):
                            print("🎬 [TRANSITION_DEBUG] E key ignored - transition scene is active")
                            continue

                        # Handle notification first
                        if self.objective_manager.showing_notification:
                            # Skip the notification and advance immediately
                            self.objective_manager.notification_timer = 0
                            self.objective_manager.showing_notification = False
                            self.objective_manager.advance_to_next_objective()
                        # Handle building with interior entry
                        elif self.near_building_with_interior and not self.current_interior:
                            building_pos, building_name, room_name = self.near_building_with_interior

                            # Check if this is a clinic-related objective at the hospital building
                            current_obj = self.objective_manager.get_current_objective()
                            clinic_objectives = ['travel_to_clinic', 'clinic_checklist', 'foster_youth_application', 'application_approved']

                            if (current_obj and current_obj.id in clinic_objectives and
                                building_pos == (34, 31)):

                                dprint(f"[CLINIC_PRIORITY] Using enhanced clinic for objective: {current_obj.id}")

                                # Part 2 clinic removed - use normal building manager
                                if self.building_manager.enter_building(building_pos, building_name, room_name):
                                    print(f"Entered building: {building_name} at {building_pos}")
                            else:
                                # Normal building entry
                                if self.building_manager.enter_building(building_pos, building_name, room_name):
                                    print(f"Entered building: {building_name} at {building_pos}")
                        # Handle interior interactions
                        elif self.current_interior:
                            dprint(f"[MAIN_DEBUG] Passing E key to interior: {self.current_interior.__class__.__name__}")
                            # Pass E key event to interior
                            if hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                            else:
                                dprint(f"[MAIN_DEBUG] Interior {self.current_interior.__class__.__name__} has no handle_event method!")
                        elif self.player_near_objective:
                            # Check if it's a quiz objective that should use classroom
                            current_obj = self.objective_manager.get_current_objective()
                            if current_obj and current_obj.id == "school_quiz":
                                # Enter the school classroom
                                quiz_activity = self.objective_manager.workplace_quiz
                                # Old classroom interior removed - need narrative version
                                # self.classroom_interior = ClassroomInterior(self, quiz_activity, "classroom")
                                # self.current_interior = self.classroom_interior
                                # self.current_interior.enter()
                                pass
                            elif current_obj and current_obj.id == "foster_home_class":
                                # Enter the foster home for tenant rights class
                                # Old foster home interior removed - use foster_home_narrative instead
                                # self.foster_home_interior = FosterHomeInterior(self, "foster_home")
                                # self.current_interior = self.foster_home_interior
                                # self.current_interior.enter()
                                pass
                            else:
                                # Check for different building entries based on objective
                                current_obj = self.objective_manager.get_current_objective()
                                if current_obj:
                                    if current_obj.id == "start_work":
                                        # Enter pizza place for work
                                        # pizza_activity = PizzaMakingActivity(self.objective_manager)  # Removed old activity
                                        pizza_activity = None
                                        # Old pizza place interior removed - need narrative version
                                        # self.pizzaplace_interior = PizzaPlaceInterior(self, pizza_activity, "pizzaplace")
                                        # self.current_interior = self.pizzaplace_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id in ["work_burger_place", "receive_training"]:
                                        # Enter burger place for work or training
                                        # Old burger place interior removed - need narrative version
                                        # self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        # self.current_interior = self.burgerplace_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id in ["sleep_work", "go_home_sleep_day2", "go_home_day1"]:
                                        # Enter home for sleep or rest
                                        # Use auto-loading Japanese home that reads from editor saves
                                        # Old home interior removed - need narrative version
                                        # self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        # self.current_interior = self.home_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id in ["community_center_workshop", "submit_application"]:
                                        # Enter community center for workshop or TLP application
                                        # Old community center interior removed - need narrative version
                                        # self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        # self.current_interior = self.community_center_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id in ["pack_belongings", "meet_roommate", "rest_tomorrow", "pack_essentials", "roommate_conflict", "living_agreement"]:
                                        # Enter TLP apartment for various activities
                                        # Old TLP apartment interior removed - need narrative version
                                        # self.tlp_apartment_interior = TLPApartmentInterior(self, "tlp_apartment")
                                        # self.current_interior = self.tlp_apartment_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id in ["housing_services", "emergency_assistance"]:
                                        # Enter housing office for assistance
                                        # Old housing office interior removed - need narrative version
                                        # self.housing_office_interior = HousingOfficeInterior(self, "housing_office")
                                        # self.current_interior = self.housing_office_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id in ["grocery_shopping", "grocery_shopping_work"]:
                                        # Enter grocery store for shopping
                                        # Old grocery store interior removed - need narrative version
                                        # self.grocery_store_interior = GroceryStoreInterior(self, "groccery_store")
                                        # self.current_interior = self.grocery_store_interior
                                        # self.current_interior.enter()
                                        pass
                                    elif current_obj.id == "go_to_library":
                                        # Enter library for research
                                        # Old library interior removed - need narrative version
                                        # self.library_interior = LibraryInterior(self, "library")
                                        # self.current_interior = self.library_interior
                                        # self.current_interior.enter()
                                        pass
                                    # Part 2 Healthcare removed - complete objective directly
                                    else:
                                        self.objective_manager.complete_current_objective()
                                else:
                                    self.objective_manager.complete_current_objective()
                    elif event.key == pygame.K_b:
                        # Go to previous objective
                        if hasattr(self, 'objective_manager') and self.objective_manager:
                            print("[MAIN] B key pressed - going to previous objective")
                            self.objective_manager.go_to_previous_objective()
                    elif event.key == pygame.K_n:
                        # Skip to next objective - REQUIRES Ctrl to prevent accidental skips
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            # Check if an activity is active (e.g., typing in form) - if so, don't skip
                            activity_active = (
                                (hasattr(self.objective_manager, 'current_activity') and
                                 self.objective_manager.current_activity and
                                 hasattr(self.objective_manager.current_activity, 'active') and
                                 self.objective_manager.current_activity.active) or
                                (self.current_interior and
                                 hasattr(self.current_interior, 'current_activity') and
                                 self.current_interior.current_activity and
                                 hasattr(self.current_interior.current_activity, 'active') and
                                 self.current_interior.current_activity.active) or
                                (hasattr(self.objective_manager, 'activity_manager') and
                                 self.objective_manager.activity_manager.current_activity and
                                 self.objective_manager.activity_manager.current_activity.active)
                            )
                            if not activity_active:
                                # Admin skip - Ctrl+N to skip to next objective
                                print("[DEBUG] Ctrl+N pressed - Skipping to next objective")
                                self.objective_manager.skip_to_next_objective()
                        else:
                            # Pass N key to interior/activity for text input
                            if self.current_interior and hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                    elif event.key == pygame.K_p:
                        # Skip to next part - REQUIRES Ctrl to prevent accidental skips
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            # Check if an activity is active (e.g., typing in form) - if so, don't skip
                            activity_active = (
                                (hasattr(self.objective_manager, 'current_activity') and
                                 self.objective_manager.current_activity and
                                 hasattr(self.objective_manager.current_activity, 'active') and
                                 self.objective_manager.current_activity.active) or
                                (self.current_interior and
                                 hasattr(self.current_interior, 'current_activity') and
                                 self.current_interior.current_activity and
                                 hasattr(self.current_interior.current_activity, 'active') and
                                 self.current_interior.current_activity.active) or
                                (hasattr(self.objective_manager, 'activity_manager') and
                                 self.objective_manager.activity_manager.current_activity and
                                 self.objective_manager.activity_manager.current_activity.active)
                            )
                            if not activity_active:
                                # Skip to next part (Ctrl+P) - Parts 1-5
                                print("[DEBUG] Ctrl+P pressed - Skipping to next part")
                                if self.objective_manager.game_part == 1:
                                    self.objective_manager.skip_to_part2()  # Legal System
                                elif self.objective_manager.game_part == 2:
                                    self.objective_manager.skip_to_part3()  # Healthcare Crisis
                                elif self.objective_manager.game_part == 3:
                                    self.objective_manager.skip_to_part4()  # Education
                                elif self.objective_manager.game_part == 4:
                                    self.objective_manager.skip_to_part5()  # Systemic Barriers
                                elif self.objective_manager.game_part == 5:
                                    self.objective_manager.skip_to_part6()  # Behavioral & Emotional
                                elif self.objective_manager.game_part == 6:
                                    self.objective_manager.skip_to_part7()  # Lack of Guidance/Mentorship
                                elif self.objective_manager.game_part == 7:
                                    self.objective_manager.skip_to_part8()  # Conflicting Responsibilities
                                elif self.objective_manager.game_part == 8:
                                    print("Already at final part (Part 8 - Conflicting Responsibilities)")
                        else:
                            # Pass P key to interior/activity for text input
                            if self.current_interior and hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                    elif event.key == pygame.K_F5:
                        # Force complete stuck activities (Ctrl+F5 for safety)
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                            print("[FORCE_COMPLETE] Ctrl+F5 pressed - Force completing stuck activity")
                            if hasattr(self.objective_manager, 'force_complete_current_activity'):
                                success = self.objective_manager.force_complete_current_activity()
                                if success:
                                    self.show_notification("Activity force completed", (255, 255, 100))
                                else:
                                    self.show_notification("No stuck activity found", (255, 200, 100))
                    else:
                        # Check debug menu first
                        if self.debug_menu.visible:
                            self.debug_menu.handle_key(event.key)
                        # Handle other keys in interior
                        elif self.current_interior:
                            if hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                        elif self.objective_manager.activity_manager.current_activity:
                            # Pass to universal activity manager
                            self.objective_manager.activity_manager.handle_event(event)
                        elif (self.objective_manager.current_activity and
                              self.objective_manager.current_activity.active and
                              hasattr(self.objective_manager.current_activity, 'handle_key')):
                            self.objective_manager.current_activity.handle_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    # Handle UI mouse motion for hover effects
                    if (hasattr(self.objective_manager, 'use_modern_ui') and
                        self.objective_manager.use_modern_ui and
                        self.objective_manager.ui_manager and
                        hasattr(self.objective_manager.ui_manager, 'handle_mouse_motion')):
                        self.objective_manager.ui_manager.handle_mouse_motion(event.pos)

                    # Route to interior FIRST if active (for drag-and-drop activities)
                    if self.current_interior:
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                    elif (self.objective_manager.current_activity and
                        self.objective_manager.current_activity.active and
                        hasattr(self.objective_manager.current_activity, 'handle_mouse_motion')):
                        self.objective_manager.current_activity.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    dprint(f"[MAIN_DEBUG] Mouse click at {event.pos}, button {event.button}")
                    dprint(f"[MAIN_DEBUG] Current interior: {self.current_interior}")
                    dprint(f"[MAIN_DEBUG] Current activity: {self.objective_manager.current_activity}")

                    # Check debug menu first
                    if self.debug_menu.visible and self.debug_menu.handle_click(event.pos):
                        continue

                    # Check modern UI FIRST (even in interiors) - allows hamburger button to work
                    if (hasattr(self.objective_manager, 'use_modern_ui') and
                        self.objective_manager.use_modern_ui and
                        self.objective_manager.ui_manager):
                        if self.objective_manager.ui_manager.handle_click(event.pos):
                            continue

                    # Check if interior should handle this
                    if self.current_interior:
                        dprint(f"[MAIN_DEBUG] Routing mouse click to interior: {self.current_interior.__class__.__name__}")
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                        continue

                    # Check for skip button click (legacy UI)
                    if event.button == 1:  # Left click
                        mx, my = event.pos
                        # Skip button position (matching draw_ui in ObjectiveManager)
                        margin = 25
                        panel_width = 320
                        skip_width = 80
                        skip_height = 28
                        skip_x = margin + panel_width - skip_width - 15
                        skip_y = margin + 15

                        if skip_x <= mx <= skip_x + skip_width and skip_y <= my <= skip_y + skip_height:
                            self.objective_manager.skip_to_next_objective()
                            continue

                    # Check for active activities if no interior
                    if (self.objective_manager.current_activity and
                        self.objective_manager.current_activity.active and
                        hasattr(self.objective_manager.current_activity, 'handle_mouse_click')):
                        self.objective_manager.current_activity.handle_mouse_click(event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    dprint(f"[MAIN_DEBUG] Mouse release at {event.pos}, button {event.button}")

                    # Check if interior should handle this FIRST
                    if self.current_interior:
                        dprint(f"[MAIN_DEBUG] Routing mouse release to interior: {self.current_interior.__class__.__name__}")
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                    # Check for active activities if no interior
                    elif (self.objective_manager.current_activity and
                        self.objective_manager.current_activity.active and
                        hasattr(self.objective_manager.current_activity, 'handle_mouse_release')):
                        self.objective_manager.current_activity.handle_mouse_release(event.pos, event.button)
                elif event.type == pygame.TEXTINPUT:
                    dprint(f"[MAIN_DEBUG] Text input: {event.text}")

                    # Check if interior should handle this FIRST
                    if self.current_interior:
                        dprint(f"[MAIN_DEBUG] Routing text input to interior: {self.current_interior.__class__.__name__}")
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                    # Handle text input for activities if no interior
                    elif (self.objective_manager.current_activity and
                        self.objective_manager.current_activity.active and
                        hasattr(self.objective_manager.current_activity, 'handle_text_input')):
                        self.objective_manager.current_activity.handle_text_input(event.text)

            self.handle_input()
            
            # Update interior if active
            if self.current_interior:
                self.current_interior.update(dt)
                # Check if interior is no longer active (verify it still exists after update)
                if self.current_interior and not self.current_interior.active:
                    self.current_interior = None
            else:
                self.player.update(dt)
                # Only check objective proximity when not in an interior
                if not self.current_interior:
                    self.player_near_objective = self.objective_manager.check_player_at_objective(
                        self.player.x, self.player.y
                    )
                    # Check for buildings with interiors
                    building_pos, building_name, room_name = self.building_manager.check_player_near_building(
                        self.player.x, self.player.y
                    )
                    if building_pos:
                        self.near_building_with_interior = (building_pos, building_name, room_name)
                    else:
                        self.near_building_with_interior = None
                else:
                    self.player_near_objective = False
                    self.near_building_with_interior = None
                self.update_camera()

            self.objective_manager.update(dt)

            # Update scenario completion transition (TV effect)
            if hasattr(self, 'scenario_completion'):
                self.scenario_completion.update(dt)

            # Update auto-player if enabled
            if hasattr(self, 'auto_player') and self.auto_player.enabled:
                self.auto_player.update(dt)

            # Update smooth transitions
            self.transition_manager.update(dt)

            # Update health monitoring and user guidance
            if hasattr(self, 'health_manager'):
                self.health_manager.update(dt)

            self.draw()
            pygame.display.flip()

            # End performance monitoring for this frame
            end_frame()

            # Give control back to the browser
            await asyncio.sleep(0)

        pygame.quit()

    def emergency_exit_room(self):
        """Emergency exit from any room when CTRL+ESC is pressed"""
        debug_logger.warning('EMERGENCY', "Emergency exit triggered")

        if self.current_interior:
            room_name = self.current_interior.__class__.__name__
            building_pos = getattr(self.current_interior, 'building_pos', 'Unknown')

            debug_logger.error('EMERGENCY', f"Force exiting room: {room_name}",
                              building_pos=building_pos)

            # Clean up current interior
            try:
                self.building_manager.cleanup_current_interior()
            except Exception as e:
                debug_logger.error('EMERGENCY', f"Error during cleanup: {str(e)}")

            # Force clear the interior
            self.current_interior = None

            # Reset player to a safe position if needed
            if hasattr(self, 'player'):
                # Move player away from building entrance
                self.player.x = max(5, min(self.player.x, self.city_map.width - 5))
                self.player.y = max(5, min(self.player.y, self.city_map.height - 5))

            debug_logger.info('EMERGENCY', "Player returned to exterior map")

            # Show notification to player
            if hasattr(self, 'objective_manager'):
                self.objective_manager.show_notification ("Emergency exit - returned to map")

        else:
            debug_logger.warning('EMERGENCY', "Emergency exit called but no interior active")

    def take_screenshot(self):
        """Take a screenshot of the current game state"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        debug_logger.info('SCREENSHOT', f"Screenshot saved: {filename}")


async def main():
    # Initialize game
    game = Game()

    # Parse and apply CLI arguments
    try:
        args = game.cli_controller.parse_args()
        dprint(f"[MAIN] CLI Configuration: {game.cli_controller.get_startup_summary()}")
        game.cli_controller.apply_to_game(game)
    except SystemExit:
        # Handle --help or --list-scenes
        return
    except Exception as e:
        dprint(f"[MAIN] CLI Error: {e}")

    # Run the game
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
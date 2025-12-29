import asyncio
import pygame
import math
import datetime
import os
import sys
import argparse
from src.constants import *
from src.core.game_world import ObjectiveManager, AnimatedPlayer, TileManager, CityMap
from src.core.main_menu import MainMenu
from src.core.scenarios_menu import ScenariosMenu
from src.core.character_select import CharacterSelect
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
from src.core.debug_logger import debug_logger
from src.core.event_bus import EventBus

# Debug scene mappings - map names to (module_path, class_name)
DEBUG_SCENES = {
    # Part 2 - Healthcare Access activities
    'mailbox': ('part_2_healthcare.activities.mailbox_sorting', 'MailboxSortingGame'),
    'medicaid': ('part_2_healthcare.activities.medicaid_notice_activity', 'MedicaidNoticeActivity'),
    'therapy_reminder': ('part_2_healthcare.activities.therapy_reminder_activity', 'TherapyReminderActivity'),
    'insurance_panic': ('part_2_healthcare.activities.insurance_panic_activity', 'InsurancePanicActivity'),
    'breathing': ('part_2_healthcare.activities.breathing_exercise', 'BreathingExerciseGame'),
    'pharmacy': ('part_2_healthcare.activities.pharmacy_activity', 'PharmacyMedicationActivity'),
    'bus_route': ('part_2_healthcare.activities.bus_route_game', 'BusRouteGame'),
    'burger_rush': ('part_2_healthcare.activities.burger_rush_game', 'BurgerRushGame'),
    'clinic_checklist': ('part_2_healthcare.activities.clinic_checklist_activity', 'ClinicChecklistActivity'),
    'foster_youth_form': ('part_2_healthcare.activities.foster_youth_application_form', 'FosterYouthApplicationFormGame'),
}


def parse_args():
    """Parse command-line arguments for debug mode"""
    parser = argparse.ArgumentParser(
        description='Economics Adventure Game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Debug Mode Examples:
  python src/main.py --debug mailbox     Jump directly to mailbox sorting activity
  python src/main.py --debug breathing   Jump directly to breathing exercise
  python src/main.py --list-scenes       Show all available debug scenes
        '''
    )
    parser.add_argument('--debug', metavar='SCENE',
                       help='Launch directly into a debug scene (skips menu)')
    parser.add_argument('--list-scenes', action='store_true',
                       help='List all available debug scenes and exit')
    return parser.parse_args()


def list_debug_scenes():
    """Print available debug scenes and exit"""
    print("\n=== Available Debug Scenes ===\n")
    for name, (module, cls) in sorted(DEBUG_SCENES.items()):
        print(f"  {name:20} -> {cls}")
    print("\nUsage: python src/main.py --debug <scene_name>")
    print("Example: python src/main.py --debug mailbox\n")


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Economics Adventure")
        self.clock = pygame.time.Clock()
        
        # Game states
        self.game_state = 'menu'  # 'menu', 'character_select', 'playing', 'help', 'credits', 'scenarios'
        self.main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.scenarios_menu = ScenariosMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.character_select = CharacterSelect(SCREEN_WIDTH, SCREEN_HEIGHT)
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

        # Debug panel
        self.debug_panel = DebugPanel(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Centralized event bus for reliable event routing
        self.event_bus = EventBus(self)

        # Emergency exit state
        self.emergency_exit_timer = 0

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
        if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
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
            # Check if there's an active activity that should be drawn INSTEAD of interior
            activity = self.objective_manager.current_activity
            if activity and hasattr(activity, 'active') and activity.active:
                # Draw the activity (it takes over the screen)
                print(f"[DRAW] Drawing activity: {type(activity).__name__}")
                if hasattr(activity, 'draw'):
                    activity.draw(self.screen)
            else:
                # No active activity - draw the interior normally
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

    def draw_ui(self):
        # Controls display removed - clean UI
        # Use Y key to toggle debug info if needed
        self.objective_manager.draw_ui(self.screen)

        # Draw hover text for buildings with interiors
        if self.near_building_with_interior and not self.current_interior:
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
            dt = self.clock.tick(FPS) / 1000.0

            # Handle menu state
            if self.game_state == 'menu':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self.take_screenshot()
                    else:
                        action = self.main_menu.handle_event(event)
                        if action == 'start_game':
                            self.game_state = 'character_select'
                            self.character_select.reset()
                        elif action == 'quit':
                            running = False
                        elif action == 'scenarios':
                            self.game_state = 'scenarios'
                        elif action == 'howto':
                            self.game_state = 'help'
                        elif action == 'credits':
                            self.game_state = 'credits'
                
                # Draw menu
                self.main_menu.draw(self.screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle character select state
            elif self.game_state == 'character_select':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self.take_screenshot()
                    else:
                        action = self.character_select.handle_event(event)
                        if action == 'character_selected':
                            # Store selected character
                            self.selected_character = self.character_select.selected_character
                            print(f"Selected character: {self.selected_character.name}")
                            # Update player sprite to use selected character
                            self.player.selected_character_index = self.selected_character.sprite_index
                            self.player.load_animations()
                            # Start the game
                            self.game_state = 'playing'
                            self.objective_manager.start()
                        elif action == 'back_to_menu':
                            self.game_state = 'menu'
                            self.main_menu.reset()

                # Draw character selection
                self.character_select.draw(self.screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle help state
            elif self.game_state == 'help':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F12:
                            self.take_screenshot()
                        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            self.game_state = 'menu'
                            self.main_menu.reset()
                
                self.draw_help_screen()
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle scenarios state
            elif self.game_state == 'scenarios':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                        self.take_screenshot()
                    else:
                        action = self.scenarios_menu.handle_event(event)
                        if action == 'start_part1':
                            # Start Part 1: Housing Stability
                            self.game_state = 'character_select'
                            self.character_select.reset()
                        elif action == 'start_part2':
                            # Start Part 2 if available (set to character select for now)
                            print("Part 2: Healthcare Access - Starting...")
                            self.game_state = 'character_select'
                            self.character_select.reset()
                            # TODO: Set up Part 2 specific initialization
                        elif action == 'coming_soon':
                            # Show coming soon message (already handled in scenarios_menu)
                            pass
                        elif action == 'back_to_menu':
                            self.game_state = 'menu'
                            self.main_menu.reset()
                            self.scenarios_menu.reset()

                # Draw scenarios menu
                self.scenarios_menu.draw(self.screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

            # Handle credits state
            elif self.game_state == 'credits':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F12:
                            self.take_screenshot()
                        elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                            self.game_state = 'menu'
                            self.main_menu.reset()
                
                self.draw_credits_screen()
                pygame.display.flip()
                await asyncio.sleep(0)
                continue
            
            # Normal game loop (playing state)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F12:
                        self.take_screenshot()
                    elif event.key == pygame.K_F3:
                        # Toggle debug panel and event bus debug mode
                        self.debug_panel.toggle()
                        self.event_bus.debug_events = self.debug_panel.visible
                        debug_logger.info('DEBUG', "Debug panel toggled",
                                        visible=self.debug_panel.visible)
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
                                self.game_state = 'menu'
                                self.main_menu.reset()
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
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
                             self.current_interior.current_activity.active)
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
                             self.current_interior.current_activity.active)
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
                        # Handle notification first
                        if self.objective_manager.showing_notification:
                            # Skip the notification and advance immediately
                            self.objective_manager.notification_timer = 0
                            self.objective_manager.showing_notification = False
                            self.objective_manager.advance_to_next_objective()
                        # Handle building with interior entry
                        elif self.near_building_with_interior and not self.current_interior:
                            building_pos, building_name, room_name = self.near_building_with_interior
                            if self.building_manager.enter_building(building_pos, building_name, room_name):
                                print(f"Entered building: {building_name} at {building_pos}")
                        # Handle interior interactions
                        elif self.current_interior:
                            # Pass E key event to interior
                            if hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
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
                                    else:
                                        self.objective_manager.complete_current_objective()
                                else:
                                    self.objective_manager.complete_current_objective()
                    elif event.key == pygame.K_n:
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
                             self.current_interior.current_activity.active)
                        )
                        if not activity_active:
                            # Admin skip - press N to skip to next objective
                            self.objective_manager.skip_to_next_objective()
                        else:
                            # Pass N key to interior/activity for text input
                            if self.current_interior and hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                    elif event.key == pygame.K_p:
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
                             self.current_interior.current_activity.active)
                        )
                        if not activity_active:
                            # Skip to next part
                            if self.objective_manager.game_part == 1:
                                self.objective_manager.skip_to_part2()
                            elif self.objective_manager.game_part == 2:
                                self.objective_manager.skip_to_part3()
                            elif self.objective_manager.game_part == 3:
                                self.objective_manager.skip_to_part4()
                            elif self.objective_manager.game_part == 4:
                                self.objective_manager.skip_to_part5()
                            elif self.objective_manager.game_part == 5:
                                self.objective_manager.skip_to_part6()
                        else:
                            # Pass P key to interior/activity for text input
                            if self.current_interior and hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                    else:
                        # Handle other keys in interior
                        if self.current_interior:
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
                    # Route through event bus first - activities get priority
                    if self.event_bus.route_event(event):
                        continue  # Event consumed by activity

                    # Handle UI mouse motion for hover effects (fallback)
                    if (hasattr(self.objective_manager, 'use_modern_ui') and
                        self.objective_manager.use_modern_ui and
                        self.objective_manager.ui_manager and
                        hasattr(self.objective_manager.ui_manager, 'handle_mouse_motion')):
                        self.objective_manager.ui_manager.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Route through event bus first - activities get priority
                    if self.event_bus.route_event(event):
                        continue  # Event consumed by activity

                    # Check modern UI if available (fallback)
                    if (hasattr(self.objective_manager, 'use_modern_ui') and
                        self.objective_manager.use_modern_ui and
                        self.objective_manager.ui_manager):
                        if self.objective_manager.ui_manager.handle_click(event.pos):
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

                    # Handle interior interactions (when no activity is active)
                    if self.current_interior:
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Route through event bus first - activities get priority
                    if self.event_bus.route_event(event):
                        continue  # Event consumed by activity

                    # Handle interior events (when no activity is active)
                    if self.current_interior:
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                elif event.type == pygame.TEXTINPUT:
                    # Route through event bus first - activities get priority
                    if self.event_bus.route_event(event):
                        continue  # Event consumed by activity

                    # Handle interior text input (when no activity is active)
                    if self.current_interior:
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)

            self.handle_input()

            # Update interior if active
            if self.current_interior:
                # Check if there's an active activity that needs updating
                activity = self.objective_manager.current_activity
                if activity and hasattr(activity, 'active') and activity.active:
                    # Update the activity (it takes priority over interior)
                    if hasattr(activity, 'update'):
                        activity.update(dt)
                    # Check if activity completed
                    if hasattr(activity, 'completed') and activity.completed:
                        print(f"[MAIN] Activity completed: {type(activity).__name__}")
                        self.objective_manager.current_activity = None
                else:
                    # No active activity - update interior normally
                    self.current_interior.update(dt)
                # Check if interior is no longer active
                if not self.current_interior.active:
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
            self.draw()
            pygame.display.flip()
            
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
                self.objective_manager.show_notification("Emergency exit - returned to map")

        else:
            debug_logger.warning('EMERGENCY', "Emergency exit called but no interior active")

    def take_screenshot(self):
        """Take a screenshot of the current game state"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        debug_logger.info('SCREENSHOT', f"Screenshot saved: {filename}")

    async def launch_debug_scene(self, scene_name):
        """Launch directly into a debug scene, skipping menu and character select"""
        if scene_name not in DEBUG_SCENES:
            print(f"\nError: Unknown scene '{scene_name}'")
            print("Use --list-scenes to see available scenes\n")
            return

        module_path, class_name = DEBUG_SCENES[scene_name]

        try:
            # Dynamic import of the activity
            module = __import__(module_path, fromlist=[class_name])
            activity_class = getattr(module, class_name)

            # Initialize game state for debug mode
            self.game_state = 'playing'
            self.objective_manager.game_part = 2  # Most debug activities are Part 2
            pygame.display.set_caption(f"Economics Adventure [DEBUG: {scene_name}]")

            # Create and launch activity
            activity = activity_class(self.objective_manager)
            activity.start()
            self.objective_manager.current_activity = activity

            # Enable debug panel and event logging
            self.debug_panel.visible = True
            self.event_bus.debug_events = True

            print(f"\n{'='*50}")
            print(f"  DEBUG MODE: {scene_name}")
            print(f"  Activity: {class_name}")
            print(f"{'='*50}")
            print("  Controls:")
            print("    F3  - Toggle debug panel")
            print("    F12 - Take screenshot")
            print("    ESC - Exit debug mode")
            print(f"{'='*50}\n")

            # Run simplified debug loop
            await self._run_debug_loop()

        except ImportError as e:
            print(f"\nError: Failed to import activity module")
            print(f"  Module: {module_path}")
            print(f"  Error: {e}\n")
        except AttributeError as e:
            print(f"\nError: Activity class not found")
            print(f"  Class: {class_name}")
            print(f"  Error: {e}\n")
        except Exception as e:
            print(f"\nError launching debug scene: {e}")
            import traceback
            traceback.print_exc()

    async def _run_debug_loop(self):
        """Simplified game loop for debug mode - focuses on activity only"""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F3:
                        self.debug_panel.toggle()
                        self.event_bus.debug_events = self.debug_panel.visible
                    elif event.key == pygame.K_F12:
                        self.take_screenshot()
                    else:
                        # Route keyboard events through event bus
                        self.event_bus.route_event(event)
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                                   pygame.MOUSEMOTION, pygame.TEXTINPUT):
                    # Route mouse/text events through event bus
                    self.event_bus.route_event(event)

            # Update activity
            activity = self.objective_manager.current_activity
            if activity and hasattr(activity, 'active') and activity.active:
                if hasattr(activity, 'update'):
                    activity.update(dt)
            else:
                # Activity completed or stopped
                print("\n[DEBUG] Activity completed or stopped")
                running = False

            # Draw
            self.screen.fill((40, 40, 50))  # Dark background

            # Draw activity
            if activity and hasattr(activity, 'draw'):
                activity.draw(self.screen)

            # Draw debug panel
            self.debug_panel.draw(self.screen, self)

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()
        print("\n[DEBUG] Debug session ended\n")


async def main():
    args = parse_args()

    # Handle --list-scenes
    if args.list_scenes:
        list_debug_scenes()
        return

    # Initialize pygame
    pygame.init()

    game = Game()

    # Handle --debug mode
    if args.debug:
        await game.launch_debug_scene(args.debug)
    else:
        await game.run()


if __name__ == "__main__":
    asyncio.run(main())
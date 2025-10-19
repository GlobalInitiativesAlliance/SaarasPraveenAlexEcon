import asyncio
import pygame
import math
import datetime
import os
from src.constants import *
from src.core.game_world import ObjectiveManager, AnimatedPlayer, TileManager, CityMap
from src.interiors.public.classroom_interior import ClassroomInterior
from src.interiors.commercial.pizzaplace_interior import PizzaPlaceInterior
from src.activities.work.pizza_activity import PizzaMakingActivity
from src.interiors.commercial.burgerplace_interior import BurgerPlaceInterior
from src.interiors.residential.home_interior import HomeInterior
from src.interiors.residential.japanese_home_interior import JapaneseHomeAuto
from src.interiors.residential.foster_home_interior import FosterHomeInterior
from src.interiors.public.community_center_interior import CommunityCenterInterior
from src.interiors.residential.tlp_apartment_interior import TLPApartmentInterior
from src.interiors.public.housing_office_interior import HousingOfficeInterior
from src.interiors.commercial.grocery_store_interior import GroceryStoreInterior
from src.core.main_menu import MainMenu


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Economics Adventure")
        self.clock = pygame.time.Clock()
        
        # Game states
        self.game_state = 'menu'  # 'menu', 'playing', 'help', 'credits', 'levels'
        self.main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_selection = None  # Will be created when needed

        self.tile_manager = TileManager()
        self.city_map = CityMap()
        self.city_map.tile_manager = self.tile_manager
        self.city_map.load_from_image()

        self.player = AnimatedPlayer(
            self.city_map.width // 2,
            self.city_map.height // 2,
            TILE_SIZE
        )

        self.objective_manager = ObjectiveManager(self)
        self.player_near_objective = False

        self.camera_x = 0
        self.camera_y = 0
        self.update_camera()

        self.font = pygame.font.Font(None, 20)
        self.show_grid = True

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
            self.current_interior.draw(self.screen)
            # Don't draw objective UI if pizza activity is active
            if not (hasattr(self, 'pizzaplace_interior') and self.pizzaplace_interior and 
                    self.pizzaplace_interior.active and self.pizzaplace_interior.tutorial_state == "work"):
                self.objective_manager.draw_ui(self.screen)
            return

        start_x = max(0, int(self.camera_x // TILE_SIZE))
        end_x = min(int((self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 2), self.city_map.width)
        start_y = max(0, int(self.camera_y // TILE_SIZE))
        end_y = min(int((self.camera_y + (SCREEN_HEIGHT - UI_HEIGHT)) // TILE_SIZE + 2), self.city_map.height)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - int(self.camera_x)
                screen_y = y * TILE_SIZE - int(self.camera_y)

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
        self.objective_manager.draw_ui(self.screen)

    def draw_ui(self):
        controls_font = pygame.font.Font(None, 18)

        controls_texts = [
            "WASD - Move",
            "E - Interact",
            "G - Toggle Grid",
            "N - Skip Objective",
            "P - Next Part"
        ]

        controls_height = len(controls_texts) * 20 + 15
        controls_width = 120
        controls_x = SCREEN_WIDTH - controls_width - 20
        controls_y = SCREEN_HEIGHT - controls_height - 20

        # Draw controls background with rounded corners
        pygame.draw.rect(self.screen, (20, 20, 25), 
                        (controls_x - 5, controls_y - 5, controls_width, controls_height),
                        0, border_radius=5)

        for i, text in enumerate(controls_texts):
            text_surface = controls_font.render(text, True, (180, 180, 180))
            self.screen.blit(text_surface, (controls_x, controls_y + i * 20))

        self.objective_manager.draw_ui(self.screen)
    
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
                    else:
                        # Global screenshot key
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                            self.take_screenshot()
                        else:
                            action = self.main_menu.handle_event(event)
                            if action == 'start':
                                pass  # Transition handled in update
                            elif action == 'quit':
                                running = False
                            elif action == 'help':
                                self.game_state = 'help'
                            elif action == 'credits':
                                self.game_state = 'credits'
                            elif action == 'levels':
                                self.game_state = 'levels'
                                # Create level selection screen if needed
                                if not self.level_selection:
                                    from src.core.level_selection import LevelSelection
                                    self.level_selection = LevelSelection(SCREEN_WIDTH, SCREEN_HEIGHT)
                
                # Update menu
                menu_result = self.main_menu.update(dt)
                if menu_result == 'start_game':
                    self.game_state = 'playing'
                    self.objective_manager.start()
                
                # Draw menu
                self.main_menu.draw(self.screen)
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
            
            # Handle levels state
            elif self.game_state == 'levels':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_F12:
                            self.take_screenshot()
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = 'menu'
                            self.main_menu.reset()
                    else:
                        # Handle level selection events
                        action = self.level_selection.handle_event(event)
                        if action and action.startswith('part_'):
                            # Extract part number from action (e.g., 'part_1' -> 1)
                            part_num = int(action.split('_')[1])
                            self.objective_manager.game_part = part_num
                            self.objective_manager.setup_objectives()
                            self.game_state = 'playing'
                            self.objective_manager.start()
                
                # Update and draw level selection
                self.level_selection.update(dt)
                self.level_selection.draw(self.screen)
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
                    elif event.key == pygame.K_ESCAPE:
                        if self.current_interior:
                            # Exit interior first
                            self.current_interior = None
                        else:
                            # Return to menu
                            self.game_state = 'menu'
                            self.main_menu.reset()
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_r:
                        self.city_map.load_from_image()
                        self.render_map_cache()
                    elif event.key == pygame.K_e:
                        # Handle notification first
                        if self.objective_manager.showing_notification:
                            # Skip the notification and advance immediately
                            self.objective_manager.notification_timer = 0
                            self.objective_manager.showing_notification = False
                            self.objective_manager.advance_to_next_objective()
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
                                self.classroom_interior = ClassroomInterior(self, quiz_activity, "classroom")
                                self.current_interior = self.classroom_interior
                                self.current_interior.enter()
                            elif current_obj and current_obj.id == "foster_home_class":
                                # Enter the foster home for tenant rights class
                                self.foster_home_interior = FosterHomeInterior(self, "foster_home")
                                self.current_interior = self.foster_home_interior
                                self.current_interior.enter()
                            else:
                                # Check for different building entries based on objective
                                current_obj = self.objective_manager.get_current_objective()
                                if current_obj:
                                    if current_obj.id == "start_work":
                                        # Enter pizza place for work
                                        pizza_activity = PizzaMakingActivity(self.objective_manager)
                                        self.pizzaplace_interior = PizzaPlaceInterior(self, pizza_activity, "pizzaplace")
                                        self.current_interior = self.pizzaplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["work_burger_place", "receive_training"]:
                                        # Enter burger place for work or training
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["sleep_work", "go_home_sleep_day2", "go_home_day1"]:
                                        # Enter home for sleep or rest
                                        # Use auto-loading Japanese home that reads from editor saves
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["community_center_workshop", "submit_application"]:
                                        # Enter community center for workshop or TLP application
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["pack_belongings", "meet_roommate", "rest_tomorrow", "pack_essentials", "roommate_conflict", "living_agreement"]:
                                        # Enter TLP apartment for various activities
                                        self.tlp_apartment_interior = TLPApartmentInterior(self, "tlp_apartment")
                                        self.current_interior = self.tlp_apartment_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["housing_services", "emergency_assistance"]:
                                        # Enter housing office for assistance
                                        self.housing_office_interior = HousingOfficeInterior(self, "housing_office")
                                        self.current_interior = self.housing_office_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["grocery_shopping", "grocery_shopping_work"]:
                                        # Enter grocery store for shopping
                                        self.grocery_store_interior = GroceryStoreInterior(self, "groccery_store")
                                        self.current_interior = self.grocery_store_interior
                                        self.current_interior.enter()
                                    # Part 3 - Financial Stress objectives with building interactions
                                    elif current_obj.id in ["check_bank", "plead_with_teller"]:
                                        # Enter bank (use housing office interior as placeholder)
                                        self.housing_office_interior = HousingOfficeInterior(self, "housing_office")
                                        self.current_interior = self.housing_office_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["empty_fridge", "count_change", "last_calls", "fever_starts", "final_night"]:
                                        # Use home interior for home activities
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["dollar_menu", "food_math"]:
                                        # Use grocery store as dollar store
                                        self.grocery_store_interior = GroceryStoreInterior(self, "groccery_store")
                                        self.current_interior = self.grocery_store_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["walk_to_library", "library_computer", "food_bank_search", "homeless_research"]:
                                        # Use classroom as library
                                        self.classroom_interior = ClassroomInterior(self, None, "classroom")
                                        self.current_interior = self.classroom_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["walk_foodbank", "food_bank_line"]:
                                        # Enter community center for food bank
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["pawn_shop_walk", "lowball_offer", "final_offer"]:
                                        # Use grocery store as pawn shop
                                        self.grocery_store_interior = GroceryStoreInterior(self, "groccery_store")
                                        self.current_interior = self.grocery_store_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["work_sick", "hiding_symptoms", "dizzy_spell"]:
                                        # Use workplace
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["emergency_room", "treatment_received"]:
                                        # Use community center as hospital
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    # Part 4 - Credit/Debt objectives
                                    elif current_obj.id in ["first_viewing", "slumlord_meeting"]:
                                        # Use apartment interior for viewings
                                        self.tlp_apartment_interior = TLPApartmentInterior(self, "tlp_apartment")
                                        self.current_interior = self.tlp_apartment_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["credit_report_request", "payday_loan_search", "know_your_rights", "unemployment_application"]:
                                        # Use classroom as library/computer access
                                        self.classroom_interior = ClassroomInterior(self, None, "classroom")
                                        self.current_interior = self.classroom_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["payday_storefront", "loan_salesperson", "payday_arrives", "rollover_accepted"]:
                                        # Use housing office as payday loan office
                                        self.housing_office_interior = HousingOfficeInterior(self, "housing_office")
                                        self.current_interior = self.housing_office_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["new_job_start", "work_overtime_request", "work_calls", "manager_complaint"]:
                                        # Use workplace for job
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["check_cashing_search", "check_cashing_fee", "money_orders"]:
                                        # Use grocery store as check cashing place
                                        self.grocery_store_interior = GroceryStoreInterior(self, "groccery_store")
                                        self.current_interior = self.grocery_store_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["hide_car", "wake_up_4am", "cash_budgeting", "feel_weak"]:
                                        # Use home interior
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["sell_plasma", "bankruptcy_consultation"]:
                                        # Use community center for services
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    # Part 5 - Healthcare objectives
                                    elif current_obj.id in ["first_er_visit", "er_visit_2", "er_mental_health"]:
                                        # Use community center as hospital ER
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["otc_painkillers", "dental_school_option"]:
                                        # Use grocery store as pharmacy
                                        self.grocery_store_interior = GroceryStoreInterior(self, "groccery_store")
                                        self.current_interior = self.grocery_store_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["cant_eat_properly", "morning_drinks", "medicaid_application"]:
                                        # Use home interior
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["work_mistakes", "call_in_sick", "panic_attack_work", "caught_drinking"]:
                                        # Use workplace
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    # Part 6 - Education objectives
                                    elif current_obj.id in ["adult_education_center", "intake_appointment", "placement_test", "library_option", "library_computers", "test_day_1", "third_math_attempt"]:
                                        # Use classroom for education activities
                                        self.classroom_interior = ClassroomInterior(self, None, "classroom")
                                        self.current_interior = self.classroom_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["talk_to_manager", "miss_monday_class"]:
                                        # Use workplace for boss interaction
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["share_books", "study_alone", "youtube_university"]:
                                        # Use home for studying
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    # Part 7 - Isolation objectives  
                                    elif current_obj.id in ["weekend_move", "empty_apartment", "call_mom", "thin_walls", "tv_company", "complete_silence", "talk_to_self", "still_alone"]:
                                        # Use home for isolation activities
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["lunch_alone", "eat_in_car"]:
                                        # Use workplace for work isolation
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["support_group_search", "depression_group", "first_meeting", "online_forums", "library_internet"]:
                                        # Use classroom as library/computer
                                        self.classroom_interior = ClassroomInterior(self, None, "classroom")
                                        self.current_interior = self.classroom_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["public_spaces", "park_bench"]:
                                        # Use community center as public space
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["crisis_hotline", "make_call"]:
                                        # Use housing office for phone calls
                                        self.housing_office_interior = HousingOfficeInterior(self, "housing_office")
                                        self.current_interior = self.housing_office_interior
                                        self.current_interior.enter()
                                    # Part 8 - Legal objectives
                                    elif current_obj.id in ["approach_turnstile", "jump_quick"]:
                                        # Use community center as transit station
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["late_to_work", "final_warning_job", "request_day_off"]:
                                        # Use workplace
                                        self.burgerplace_interior = BurgerPlaceInterior(self, "burger_room")
                                        self.current_interior = self.burgerplace_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["booking_process", "overnight_hold", "court_transport", "meet_defender", "first_meeting_po"]:
                                        # Use housing office as courthouse/jail
                                        self.housing_office_interior = HousingOfficeInterior(self, "housing_office")
                                        self.current_interior = self.housing_office_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["phone_dead", "work_voicemail"]:
                                        # Use home
                                        self.home_interior = JapaneseHomeAuto(self, "japenese_home")
                                        self.current_interior = self.home_interior
                                        self.current_interior.enter()
                                    elif current_obj.id in ["application_question", "auto_rejections"]:
                                        # Use classroom as job center/library
                                        self.classroom_interior = ClassroomInterior(self, None, "classroom")
                                        self.current_interior = self.classroom_interior
                                        self.current_interior.enter()
                                    elif current_obj.id == "community_service":
                                        # Use community center for service
                                        self.community_center_interior = CommunityCenterInterior(self, "community_center")
                                        self.current_interior = self.community_center_interior
                                        self.current_interior.enter()
                                    else:
                                        self.objective_manager.complete_current_objective()
                                else:
                                    self.objective_manager.complete_current_objective()
                    elif event.key == pygame.K_n:
                        # Admin skip - press N to skip to next objective
                        self.objective_manager.skip_to_next_objective()
                    elif event.key == pygame.K_p:
                        # Skip to next part (cycle through all parts)
                        current_part = self.objective_manager.game_part
                        next_part = (current_part % 8) + 1  # Cycle through 1-8
                        self.objective_manager.game_part = next_part
                        self.objective_manager.setup_objectives()
                        self.objective_manager.start()
                    else:
                        # Handle other keys in interior
                        if self.current_interior:
                            if hasattr(self.current_interior, 'handle_event'):
                                self.current_interior.handle_event(event)
                        elif self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                            self.objective_manager.current_activity.handle_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    if self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        self.objective_manager.current_activity.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check for skip button click first
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
                    
                    # Handle mouse clicks in interior first
                    if self.current_interior:
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                    elif self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        self.objective_manager.current_activity.handle_mouse_click(event.pos, event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Handle mouse release in interior first
                    if self.current_interior:
                        if hasattr(self.current_interior, 'handle_event'):
                            self.current_interior.handle_event(event)
                    elif self.objective_manager.current_activity and self.objective_manager.current_activity.active:
                        if hasattr(self.objective_manager.current_activity, 'handle_mouse_release'):
                            self.objective_manager.current_activity.handle_mouse_release(event.pos, event.button)

            self.handle_input()
            
            # Update interior if active
            if self.current_interior:
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
                else:
                    self.player_near_objective = False
                self.update_camera()

            self.objective_manager.update(dt)
            self.draw()
            pygame.display.flip()
            
            # Give control back to the browser
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
import pygame
import sys
import numpy as np
import random
import os
from pizza_maker import PizzaMakerModal
from burger_maker import BurgerMakerModal
from building_definitions import BUILDING_DEFINITIONS

pygame.init()

# Constants
TILE_SIZE = 32
ORIGINAL_TILE_SIZE = 16
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
MAP_WIDTH = 32
MAP_HEIGHT = 24

# Building definitions
BUILDING_DISPLAY_NAMES = {
    'skyscraper_1_3x6': 'ILP Office',
    'store_1_4x3': 'School',
    'store_2_4x4': 'Burger Place',
    'house_1_3x3': 'Pizza Place',
    'bank_1_3x6': 'Job Center',
    'home_area_4x3': 'Foster Home'
}

# Simple single tiles for ground
TILE_POSITIONS = {
    'grass': [('CP_V1.0.4.png', 16, 48)],
    'road': [('CP_V1.0.4.png', 3, 38)],
    'sidewalk': [('CP_V1.0.4.png', 5, 8)],
}

class GameState:
    def __init__(self):
        self.day = 1
        self.money = 0.0
        self.health = 100
        self.calories_today = 0
        self.calories_needed = 2000
        
        # Story progression - MODIFIED to follow exact requirements
        self.story_stage = "attend_school"  # First objective
        self.has_job = False
        self.job_location = None
        self.been_fired = False
        self.times_fired = 0
        self.completed_school_quiz = False
        self.burger_training_completed = False
        self.emergency_happened = False
        self.mandatory_meeting_scheduled = False
        self.ilp_officer_contacted = False
        self.has_id = True  # For job center
        self.has_ssn = True
        self.has_resume = True
        
        # Inventory
        self.inventory = {}
        
    def add_money(self, amount):
        self.money += amount
        
    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

class QuizModal:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.current_question = 0
        self.score = 0
        self.questions = [
            {
                "question": "What should you do if you're going to be late for work?",
                "options": ["Don't tell anyone", "Call your manager", "Just don't show up", "Quit immediately"],
                "correct": 1
            },
            {
                "question": "If you get fired, what's your first step?",
                "options": ["Give up", "Apply for unemployment benefits", "Blame everyone else", "Hide at home"],
                "correct": 1
            },
            {
                "question": "As a foster youth, who can help you with work issues?",
                "options": ["Nobody", "Your ILP officer", "Random strangers", "Only your boss"],
                "correct": 1
            }
        ]
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running and self.current_question < len(self.questions):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_4:
                        choice = event.key - pygame.K_1
                        if choice == self.questions[self.current_question]["correct"]:
                            self.score += 1
                        self.current_question += 1
                        
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
            
        return True
        
    def draw(self):
        self.screen.fill((20, 30, 40))
        
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            
            # Draw question
            question_text = self.font.render(q["question"], True, (255, 255, 255))
            question_rect = question_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(question_text, question_rect)
            
            # Draw options
            for i, option in enumerate(q["options"]):
                option_text = self.font.render(f"{i+1}. {option}", True, (255, 255, 255))
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 300 + i * 50))
                self.screen.blit(option_text, option_rect)
                
            # Instructions
            inst_text = self.font.render("Press 1-4 to select your answer", True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, 500))
            self.screen.blit(inst_text, inst_rect)

class ShopModal:
    def __init__(self, screen, font, game_state):
        self.screen = screen
        self.font = font
        self.game_state = game_state
        self.items = {
            "Apple": {"price": 2.50, "calories": 80, "health": 5},
            "Banana": {"price": 1.50, "calories": 105, "health": 3},
            "Sandwich": {"price": 8.00, "calories": 400, "health": 2},
            "Salad": {"price": 12.00, "calories": 200, "health": 10},
            "Energy Drink": {"price": 3.00, "calories": 120, "health": -2},
            "Chips": {"price": 4.00, "calories": 300, "health": -1}
        }
        self.selected_item = 0
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.items)
                    elif event.key == pygame.K_RETURN:
                        self.buy_item()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
            
        return True
        
    def buy_item(self):
        item_name = list(self.items.keys())[self.selected_item]
        item = self.items[item_name]
        
        if self.game_state.spend_money(item["price"]):
            self.game_state.calories_today += item["calories"]
            self.game_state.health += item["health"]
            self.game_state.health = max(0, min(100, self.game_state.health))
            
    def draw(self):
        self.screen.fill((40, 20, 30))
        
        # Title
        title = self.font.render("GROCERY STORE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Money display
        money_text = self.font.render(f"Money: ${self.game_state.money:.2f}", True, (255, 255, 255))
        self.screen.blit(money_text, (50, 100))
        
        # Calories display
        cal_text = self.font.render(f"Calories today: {self.game_state.calories_today}/{self.game_state.calories_needed}", True, (255, 255, 255))
        self.screen.blit(cal_text, (50, 130))
        
        # Health display
        health_text = self.font.render(f"Health: {self.game_state.health}/100", True, (255, 255, 255))
        self.screen.blit(health_text, (50, 160))
        
        # Items
        y_offset = 200
        for i, (name, item) in enumerate(self.items.items()):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            item_text = self.font.render(f"{name} - ${item['price']:.2f} ({item['calories']} cal, {item['health']:+d} health)", True, color)
            self.screen.blit(item_text, (100, y_offset + i * 30))
            
        # Instructions
        inst_text = self.font.render("UP/DOWN to select, ENTER to buy, ESC to exit", True, (200, 200, 200))
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
        self.screen.blit(inst_text, inst_rect)

class DialogueModal:
    def __init__(self, screen, font, dialogue_data):
        self.screen = screen
        self.font = font
        self.dialogue_data = dialogue_data
        self.current_node = "start"
        self.result = None
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running and self.current_node and self.current_node != "end":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        choice_idx = event.key - pygame.K_1
                        node = self.dialogue_data[self.current_node]
                        if choice_idx < len(node.get("choices", [])):
                            choice = node["choices"][choice_idx]
                            self.current_node = choice["next"]
                            if "result" in choice:
                                self.result = choice["result"]
                                
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
            
        return self.result
        
    def draw(self):
        self.screen.fill((30, 30, 50))
        
        if self.current_node in self.dialogue_data:
            node = self.dialogue_data[self.current_node]
            
            # Draw speaker
            if "speaker" in node:
                speaker_text = self.font.render(node["speaker"], True, (255, 255, 0))
                self.screen.blit(speaker_text, (50, 50))
                
            # Draw text
            text_lines = node["text"].split('\n')
            for i, line in enumerate(text_lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (50, 100 + i * 30))
                
            # Draw choices
            if "choices" in node:
                for i, choice in enumerate(node["choices"]):
                    choice_text = self.font.render(f"{i+1}. {choice['text']}", True, (200, 255, 200))
                    self.screen.blit(choice_text, (100, 300 + i * 40))

class LifeSimulationGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Foster Youth Life Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.popup_font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 28)
        self.story_font = pygame.font.Font(None, 28)

        # Game state
        self.game_state = GameState()

        # Load sprite sheets
        self.sheets = {}
        self.load_sheets()

        # Generate map
        self.map_data = self.generate_focused_map()

        # Load sprites
        self.sprites = {}
        self.load_sprites()

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Player
        self.player_x = float(MAP_WIDTH // 2)
        self.player_y = float(MAP_HEIGHT // 2)
        self.player_vel_x = 0.0
        self.player_vel_y = 0.0
        self.acceleration = 0.3
        self.max_speed = 0.15
        self.friction = 0.8
        
        # Building interaction
        self.current_building = None
        self.current_building_type = None
        self.popup_timer = 0
        self.popup_duration = 120
        self.popup_message = ""
        
        # Modals
        self.pizza_maker_active = False
        self.pizza_maker = None
        self.burger_maker_active = False
        self.burger_maker = None
        
        # Story tracking
        self.story_progress = 0
        self.current_objective = "Go to School to take the quiz"
        self.objective_timer = 0
        self.objective_duration = 300

    def load_sheets(self):
        base_dir = os.path.dirname(__file__)
        try:
            path = os.path.join(base_dir, "CP_V1.1.0_nyknck", "CP_V1.0.4_nyknck", "CP_V1.0.4.png")
            self.sheets['CP_V1.0.4.png'] = pygame.image.load(path)
        except Exception as e:
            print(f"Failed to load sprite sheet: {e}")
            self.sheets['CP_V1.0.4.png'] = pygame.Surface((1024, 1024))
            self.sheets['CP_V1.0.4.png'].fill((100, 100, 100))

    def load_sprites(self):
        for tile_type, positions in TILE_POSITIONS.items():
            self.sprites[tile_type] = []
            for sheet_name, x, y in positions:
                if sheet_name in self.sheets:
                    sheet = self.sheets[sheet_name]
                    rect = pygame.Rect(x * ORIGINAL_TILE_SIZE, y * ORIGINAL_TILE_SIZE,
                                       ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                    if rect.right <= sheet.get_width() and rect.bottom <= sheet.get_height():
                        tile = sheet.subsurface(rect).copy()
                        tile = pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))
                        self.sprites[tile_type].append(tile)

            if not self.sprites[tile_type]:
                fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
                colors = {
                    'grass': (50, 150, 50),
                    'road': (60, 60, 60),
                    'sidewalk': (150, 150, 150),
                }
                fallback.fill(colors.get(tile_type, (255, 0, 255)))
                self.sprites[tile_type] = [fallback]

        # Create player sprite
        player = pygame.Surface((TILE_SIZE - 8, TILE_SIZE - 8), pygame.SRCALPHA)
        pygame.draw.circle(player, (0, 100, 255), (player.get_width() // 2, player.get_height() // 2), 12)
        pygame.draw.circle(player, (0, 150, 255), (player.get_width() // 2, player.get_height() // 2), 10)
        pygame.draw.circle(player, (255, 255, 255), (player.get_width() // 2, player.get_height() // 2 - 3), 3)
        self.sprites['player'] = player

    def can_place_building(self, map_data, building_def, x, y):
        width, height = building_def['size']
        if x + width > MAP_WIDTH or y + height > MAP_HEIGHT:
            return False
        for dy in range(height):
            for dx in range(width):
                if map_data[y + dy][x + dx] != 'grass':
                    return False
        return True

    def place_building(self, map_data, building_name, x, y):
        building = BUILDING_DEFINITIONS[building_name]
        width, height = building['size']
        for dy in range(height):
            for dx in range(width):
                map_data[y + dy][x + dx] = f'building:{building_name}:{dx},{dy}'

    def generate_focused_map(self):
        map_data = [['grass' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

        # Add strategic roads
        main_road_y = MAP_HEIGHT // 2
        for x in range(MAP_WIDTH):
            map_data[main_road_y][x] = 'road'
            
        main_road_x = MAP_WIDTH // 2
        for y in range(MAP_HEIGHT):
            map_data[y][main_road_x] = 'road'

        road_y2 = MAP_HEIGHT // 4
        for x in range(MAP_WIDTH):
            map_data[road_y2][x] = 'road'

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if map_data[y][x] == 'road':
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH:
                            if map_data[ny][nx] == 'grass':
                                map_data[ny][nx] = 'sidewalk'

        # Strategic building placement
        building_placements = [
            ('skyscraper_1_3x6', 26, 2),    # ILP Office
            ('store_1_4x3', 7, 1),          # School
            ('store_2_4x4', 18, 1),         # Burger Place
            ('house_1_3x3', 2, 15),         # Pizza Place
            ('bank_1_3x6', 26, 15),         # Job Center
            ('home_area_4x3', 12, 15),      # Foster Home
        ]

        building_count = 0
        failed_placements = []
        
        for building_name, x, y in building_placements:
            if building_name in BUILDING_DEFINITIONS:
                building = BUILDING_DEFINITIONS[building_name]
                if self.can_place_building(map_data, building, x, y):
                    self.place_building(map_data, building_name, x, y)
                    building_count += 1
                else:
                    failed_placements.append((building_name, x, y))

        alternative_positions = [
            (25, 15), (24, 10), (3, 8), (12, 15), (22, 8), (5, 18), (15, 3),
            (28, 8), (1, 8), (10, 8), (20, 15), (5, 12), (15, 18), (25, 8)
        ]
        
        for building_name, orig_x, orig_y in failed_placements:
            placed = False
            building = BUILDING_DEFINITIONS[building_name]
            
            for alt_x, alt_y in alternative_positions:
                if self.can_place_building(map_data, building, alt_x, alt_y):
                    self.place_building(map_data, building_name, alt_x, alt_y)
                    building_count += 1
                    placed = True
                    break
        
        return map_data

    def get_tile_sprite(self, x, y):
        cell = self.map_data[y][x]

        if cell.startswith('building:'):
            parts = cell.split(':')
            building_name = parts[1]
            offset = parts[2]
            dx, dy = map(int, offset.split(','))

            building = BUILDING_DEFINITIONS[building_name]
            sheet_name, tile_x, tile_y = building['tiles'][dy][dx]

            if sheet_name in self.sheets:
                sheet = self.sheets[sheet_name]
                rect = pygame.Rect(tile_x * ORIGINAL_TILE_SIZE, tile_y * ORIGINAL_TILE_SIZE,
                                   ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE)
                if rect.right <= sheet.get_width() and rect.bottom <= sheet.get_height():
                    tile = sheet.subsurface(rect).copy()
                    return pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE))

            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill((200, 100, 100))
            return fallback
        else:
            if cell in self.sprites and self.sprites[cell]:
                return self.sprites[cell][0]
            else:
                fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback.fill((255, 0, 255))
                return fallback

    def get_building_name_at_position(self, x, y):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            cell = self.map_data[y][x]
            if cell.startswith('building:'):
                parts = cell.split(':')
                building_name = parts[1]
                display_name = BUILDING_DISPLAY_NAMES.get(building_name, building_name)
                return display_name
        return None

    def start_school_quiz(self):
        quiz = QuizModal(self.screen, self.font)
        if quiz.run():
            self.game_state.completed_school_quiz = True
            self.game_state.story_stage = "apply_for_job"
            self.update_objective("Go to Pizza Place to apply for a job")
            self.story_progress = 1
            self.show_popup_message("Quiz completed! Time to find a job.")

    def apply_for_pizza_job(self):
        if not self.game_state.has_job:
            self.game_state.has_job = True
            self.game_state.job_location = "Pizza Place"
            self.game_state.story_stage = "work_first_day"
            self.update_objective("Go to Pizza Place to start your first shift")
            self.story_progress = 2
            self.show_popup_message("You got hired at the Pizza Shop!")

    def start_pizza_work(self):
        self.pizza_maker_active = True
        self.pizza_maker = PizzaMakerModal()
        self.game_state.add_money(71.24)  # LA minimum wage for 4 hours
        self.game_state.story_stage = "after_first_work"
        self.update_objective("Return to Foster Home")
        self.story_progress = 3
        self.show_popup_message("Good work! You earned $71.24")

    def trigger_emergency(self):
        self.game_state.emergency_happened = True
        self.game_state.story_stage = "fired_from_pizza" 
        self.update_objective("Go to Pizza Place - you're late for work!")
        self.story_progress = 4
        self.show_popup_message("Emergency! You'll be late for work")

    def handle_firing(self):
        self.game_state.has_job = False
        self.game_state.been_fired = True
        self.game_state.times_fired += 1
        self.game_state.story_stage = "visit_job_center"
        self.update_objective("Go to Job Center for help")
        self.story_progress = 5
        self.show_popup_message("You were fired! Visit the Job Center")

    def visit_job_center(self):
        dialogue_data = {
            "start": {
                "speaker": "Job Center Worker",
                "text": "Welcome to the Job Center. Do you have your ID, SSN, and Resume?",
                "choices": [
                    {"text": "Yes, I have everything", "next": "training_offer", "result": "has_documents"},
                    {"text": "No, I'm missing some documents", "next": "come_back_later", "result": "missing_docs"}
                ]
            },
            "training_offer": {
                "speaker": "Job Center Worker", 
                "text": "Great! I see you have pizza experience. Would you like burger training?",
                "choices": [
                    {"text": "Yes (only option)", "next": "end", "result": "accept_training"}
                ]
            },
            "come_back_later": {
                "speaker": "Job Center Worker",
                "text": "Please come back when you have all required documents.",
                "choices": [
                    {"text": "Okay", "next": "end", "result": "need_documents"}
                ]
            }
        }
        
        dialogue = DialogueModal(self.screen, self.font, dialogue_data)
        result = dialogue.run()
        
        if result == "accept_training":
            self.game_state.burger_training_completed = True
            self.game_state.story_stage = "burger_training"
            self.update_objective("Go to Burger Place for training")
            self.story_progress = 6
            self.show_popup_message("You'll receive burger training!")

    def start_burger_training(self):
        self.burger_maker_active = True
        self.burger_maker = BurgerMakerModal()
        self.game_state.story_stage = "work_burger_job"
        self.update_objective("Go to Burger Place to start your new job")
        self.story_progress = 7
        self.show_popup_message("Training complete! Time to work")

    def start_burger_work(self):
        self.burger_maker_active = True
        self.burger_maker = BurgerMakerModal()
        self.game_state.add_money(71.24)
        self.game_state.story_stage = "go_shopping"
        self.update_objective("Go to Grocery Store to buy food")
        self.story_progress = 8
        self.show_popup_message("Burger shift complete! Time to shop")

    def start_shopping(self):
        shop = ShopModal(self.screen, self.font, self.game_state)
        shop.run()
        self.game_state.story_stage = "mandatory_meeting_conflict"
        self.update_objective("Go to School for a mandatory meeting notice")
        self.story_progress = 9
        self.show_popup_message("Supplies purchased! Check school notices")

    def show_panic_scene(self):
        dialogue_data = {
            "start": {
                "speaker": "You",
                "text": "Oh no! I have a mandatory school meeting but I also have work!\nWhat should I do?",
                "choices": [
                    {"text": "1. Contact ILP Officer for help", "next": "ilp_help", "result": "contact_ilp"},
                    {"text": "2. Do nothing and hope for the best", "next": "do_nothing", "result": "do_nothing"},
                    {"text": "3. Call manager directly", "next": "call_manager", "result": "call_manager"}
                ]
            },
            "ilp_help": {
                "speaker": "ILP Officer",
                "text": "I'll call your manager and explain the situation. This is exactly what I'm here for!",
                "choices": [
                    {"text": "Thank you!", "next": "ilp_success", "result": "ilp_success"}
                ]
            },
            "ilp_success": {
                "speaker": "ILP Officer",
                "text": "Good news! Your manager understands and you can attend the meeting.",
                "choices": [
                    {"text": "Continue", "next": "end", "result": "meeting_resolved"}
                ]
            },
            "do_nothing": {
                "speaker": "Manager",
                "text": "You didn't show up for work again! You're fired!",
                "choices": [
                    {"text": "Go back", "next": "start", "result": "back_button"}
                ]
            },
            "call_manager": {
                "speaker": "Manager",
                "text": "I appreciate you calling ahead. We can work something out.",
                "choices": [
                    {"text": "Continue", "next": "end", "result": "manager_understanding"}
                ]
            }
        }
        
        dialogue = DialogueModal(self.screen, self.font, dialogue_data)
        result = dialogue.run()
        
        if result in ["meeting_resolved", "manager_understanding"]:
            self.game_state.ilp_officer_contacted = True
            self.game_state.story_stage = "story_complete"
            self.update_objective("Congratulations! You've completed the simulation!")
            self.story_progress = 10
            self.show_popup_message("Success! You balanced work and school")

    def check_building_collision(self):
        player_tile_x = int(self.player_x)
        player_tile_y = int(self.player_y)
        
        building_name = self.get_building_name_at_position(player_tile_x, player_tile_y)
        
        if building_name:
            if self.current_building != building_name:
                self.current_building = building_name
                self.popup_timer = self.popup_duration
            elif self.popup_timer > 0:
                self.popup_timer -= 1
        else:
            if self.popup_timer > 0:
                self.popup_timer -= 1
            if self.popup_timer <= 0:
                self.current_building = None

    def draw_building_popup(self):
        if self.current_building and self.popup_timer > 0:
            text = f"Building: {self.current_building}"
            text_surface = self.popup_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            
            popup_width = max(300, text_rect.width + 40)
            popup_x = SCREEN_WIDTH // 2 - popup_width // 2
            popup_y = 50
            
            padding = 20
            bg_height = text_rect.height + padding * 2
            
            show_action = self.should_show_action_button()
            if show_action:
                bg_height += 60
            
            bg_surface = pygame.Surface((popup_width, bg_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 200), bg_surface.get_rect(), border_radius=10)
            pygame.draw.rect(bg_surface, (100, 200, 255, 50), bg_surface.get_rect(), width=2, border_radius=10)
            
            if self.popup_timer < 30:
                alpha = int((self.popup_timer / 30) * 255)
                bg_surface.set_alpha(alpha)
                text_surface.set_alpha(alpha)
            
            self.screen.blit(bg_surface, (popup_x, popup_y))
            self.screen.blit(text_surface, (popup_x + (popup_width - text_rect.width) // 2, popup_y + padding))
            
            if show_action:
                button_width = 150
                button_height = 40
                button_y = popup_y + text_rect.height + padding * 1.5
                button_x = popup_x + (popup_width - button_width) // 2
                
                self.action_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                pygame.draw.rect(self.screen, (0, 150, 0), self.action_button_rect, border_radius=5)
                pygame.draw.rect(self.screen, (200, 200, 200), self.action_button_rect, width=2, border_radius=5)
                
                action_text = self.get_action_button_text()
                button_text = self.button_font.render(action_text, True, (255, 255, 255))
                self.screen.blit(button_text, (button_x + (button_width - button_text.get_width()) // 2, 
                               button_y + (button_height - button_text.get_height()) // 2))

    def should_show_action_button(self):
        if not self.current_building:
            return False
            
        if (self.current_building == "School" and 
            self.game_state.story_stage in ["attend_school", "mandatory_meeting_conflict"]):
            return True
            
        if (self.current_building == "Pizza Place" and 
            self.game_state.story_stage in ["apply_for_job", "work_first_day", "fired_from_pizza"]):
            return True
            
        if (self.current_building == "Job Center" and 
            self.game_state.story_stage in ["visit_job_center"]):
            return True
            
        if (self.current_building == "Burger Place" and
            self.game_state.story_stage in ["burger_training", "work_burger_job"]):
            return True
            
        if (self.current_building == "ILP Office" and
            self.game_state.story_stage == "mandatory_meeting_conflict"):
            return True
            
        if (self.current_building == "Foster Home" and
            self.game_state.story_stage in ["after_first_work"]):
            return True
            
        if (self.current_building == "Grocery Store" and
            self.game_state.story_stage in ["go_shopping"]):
            return True
            
        return False

    def get_action_button_text(self):
        if self.current_building == "School":
            if self.game_state.story_stage == "attend_school":
                return "Take Quiz"
            else:
                return "Check Notices"
        elif self.current_building == "Pizza Place":
            if self.game_state.story_stage == "apply_for_job":
                return "Apply for Job"
            elif self.game_state.story_stage == "work_first_day":
                return "Start Work"
            elif self.game_state.story_stage == "fired_from_pizza":
                return "Face Manager"
        elif self.current_building == "Job Center":
            return "Get Help"
        elif self.current_building == "Burger Place":
            if self.game_state.story_stage == "burger_training":
                return "Get Training"
            else:
                return "Start Work"
        elif self.current_building == "ILP Office":
            return "Get Help"
        elif self.current_building == "Foster Home":
            return "Continue"
        elif self.current_building == "Grocery Store":
            return "Shop"
        return "Interact"

    def handle_building_button_click(self, pos):
        if hasattr(self, 'action_button_rect') and self.action_button_rect.collidepoint(pos):
            if self.current_building == "School":
                if self.game_state.story_stage == "attend_school":
                    self.start_school_quiz()
                else:
                    self.show_panic_scene()
                return True
            elif self.current_building == "Pizza Place":
                if self.game_state.story_stage == "apply_for_job":
                    self.apply_for_pizza_job()
                elif self.game_state.story_stage == "work_first_day":
                    self.start_pizza_work()
                elif self.game_state.story_stage == "fired_from_pizza":
                    self.handle_firing()
                return True
            elif self.current_building == "Job Center":
                self.visit_job_center()
                return True
            elif self.current_building == "Burger Place":
                if self.game_state.story_stage == "burger_training":
                    self.start_burger_training()
                else:
                    self.start_burger_work()
                return True
            elif self.current_building == "ILP Office":
                self.show_panic_scene()
                return True
            elif self.current_building == "Foster Home":
                self.trigger_emergency()
                return True
            elif self.current_building == "Grocery Store":
                self.start_shopping()
                return True
        return False

    def show_popup_message(self, message):
        self.popup_message = message
        self.popup_timer = 180  # 3 seconds at 60 FPS

    def update_objective(self, text):
        self.current_objective = text
        self.objective_timer = self.objective_duration
        self.show_popup_message(text)

    def draw_popup_message(self):
        if self.popup_timer > 0:
            text = self.popup_font.render(self.popup_message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            bg_width = text_rect.width + 40
            bg_height = text_rect.height + 20
            bg_rect = pygame.Rect(SCREEN_WIDTH//2 - bg_width//2, 
                                 SCREEN_HEIGHT//2 - bg_height//2, 
                                 bg_width, bg_height)
            
            pygame.draw.rect(self.screen, (0, 0, 0, 200), bg_rect)
            pygame.draw.rect(self.screen, (100, 200, 255), bg_rect, 2)
            self.screen.blit(text, text_rect)
            
            if self.popup_timer < 60:  # Fade out last second
                alpha = int(255 * (self.popup_timer / 60))
                overlay = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 255 - alpha))
                self.screen.blit(overlay, bg_rect)
            
            self.popup_timer -= 1

    def draw(self):
        self.screen.fill((20, 20, 30))

        # Calculate visible tiles
        start_x = max(0, self.camera_x // TILE_SIZE)
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_x = min(MAP_WIDTH, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(MAP_HEIGHT, (self.camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)

        # Draw map
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y
                sprite = self.get_tile_sprite(x, y)
                self.screen.blit(sprite, (screen_x, screen_y))

        # Draw player
        player_screen_x = int(self.player_x * TILE_SIZE - self.camera_x + 4)
        player_screen_y = int(self.player_y * TILE_SIZE - self.camera_y + 4)
        
        # Shadow
        shadow = pygame.Surface((TILE_SIZE - 8, TILE_SIZE - 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 100), (shadow.get_width() // 2, shadow.get_height() // 2), 12)
        self.screen.blit(shadow, (player_screen_x + 2, player_screen_y + 2))
        
        # Player
        self.screen.blit(self.sprites['player'], (player_screen_x, player_screen_y))

        # Draw UI
        self.draw_ui()
        
        # Draw building popup
        self.draw_building_popup()
        
        # Draw story objective
        self.draw_story_objective()
        
        # Draw progress bar
        self.draw_progress_bar()
        
        # Draw popup message
        self.draw_popup_message()

    def draw_ui(self):
        texts = [
            "Foster Youth Life Simulation",
            f"Money: ${self.game_state.money:.2f}",
            f"Health: {self.game_state.health}/100",
            f"Calories: {self.game_state.calories_today}/{self.game_state.calories_needed}",
            "WASD: Move, ESC: Exit",
        ]
        
        # Add story-specific info
        if self.game_state.has_job:
            texts.append(f"Job: {self.game_state.job_location}")
        if self.game_state.been_fired:
            texts.append(f"Times fired: {self.game_state.times_fired}")
        
        # Background for UI
        ui_bg = pygame.Surface((300, len(texts) * 25 + 20), pygame.SRCALPHA)
        pygame.draw.rect(ui_bg, (0, 0, 0, 150), ui_bg.get_rect(), border_radius=10)
        self.screen.blit(ui_bg, (10, 10))
        
        for i, text in enumerate(texts):
            rendered = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(rendered, (20, 20 + i * 25))

        # Health bar
        health_bar_x = 20
        health_bar_y = 20 + len(texts) * 25 + 10
        health_bar_width = 200
        health_bar_height = 20
        
        # Background
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        # Health fill
        health_fill = (self.game_state.health / 100) * health_bar_width
        health_color = (255, 0, 0) if self.game_state.health < 30 else (255, 255, 0) if self.game_state.health < 60 else (0, 255, 0)
        pygame.draw.rect(self.screen, health_color,
                        (health_bar_x, health_bar_y, health_fill, health_bar_height))

        # Calories bar
        cal_bar_y = health_bar_y + 30
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (health_bar_x, cal_bar_y, health_bar_width, health_bar_height))
        cal_fill = min(1.0, self.game_state.calories_today / self.game_state.calories_needed) * health_bar_width
        cal_color = (0, 255, 0) if self.game_state.calories_today >= self.game_state.calories_needed else (255, 255, 0)
        pygame.draw.rect(self.screen, cal_color,
                        (health_bar_x, cal_bar_y, cal_fill, health_bar_height))

    def draw_story_objective(self):
        # Create message box
        message_lines = []
        words = self.current_objective.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font.size(test_line)[0] < SCREEN_WIDTH - 100:
                current_line = test_line
            else:
                if current_line:
                    message_lines.append(current_line)
                current_line = word
        if current_line:
            message_lines.append(current_line)
        
        # Calculate message box size
        box_height = len(message_lines) * 30 + 40
        box_width = SCREEN_WIDTH - 100
        box_x = 50
        box_y = SCREEN_HEIGHT - box_height - 50
        
        # Draw background
        msg_bg = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(msg_bg, (0, 0, 50, 220), msg_bg.get_rect(), border_radius=10)
        pygame.draw.rect(msg_bg, (100, 150, 255), msg_bg.get_rect(), width=3, border_radius=10)
        self.screen.blit(msg_bg, (box_x, box_y))
        
        # Draw text
        for i, line in enumerate(message_lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (box_x + 20, box_y + 20 + i * 30))
        
        # Decrease timer but keep objective always visible
        if self.objective_timer > 0:
            self.objective_timer -= 1
            
    def draw_progress_bar(self):
        # Draw story progress bar at top
        bar_width = SCREEN_WIDTH - 40
        bar_height = 20
        bar_x = 20
        bar_y = 10
        
        # Background
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill based on story progress
        progress = self.story_progress / 10.0
        fill_width = int(progress * bar_width)
        pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Text
        progress_text = self.font.render(f"Story Progress: {self.story_progress}/10", True, (255, 255, 255))
        self.screen.blit(progress_text, (bar_x + 10, bar_y))

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Input handling for movement
        input_x, input_y = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            input_x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            input_x = 1
            
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            input_y = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            input_y = 1

        # Apply acceleration
        if input_x != 0:
            self.player_vel_x += input_x * self.acceleration
        else:
            self.player_vel_x *= self.friction
            
        if input_y != 0:
            self.player_vel_y += input_y * self.acceleration  
        else:
            self.player_vel_y *= self.friction

        # Limit maximum speed
        if abs(self.player_vel_x) > self.max_speed:
            self.player_vel_x = self.max_speed if self.player_vel_x > 0 else -self.max_speed
        if abs(self.player_vel_y) > self.max_speed:
            self.player_vel_y = self.max_speed if self.player_vel_y > 0 else -self.max_speed

        # Stop very small movements
        if abs(self.player_vel_x) < 0.01:
            self.player_vel_x = 0
        if abs(self.player_vel_y) < 0.01:
            self.player_vel_y = 0

        # Calculate new position
        new_x = self.player_x + self.player_vel_x
        new_y = self.player_y + self.player_vel_y

        # Boundary checking
        if 0 <= new_x < MAP_WIDTH:
            self.player_x = new_x
        else:
            self.player_vel_x = 0

        if 0 <= new_y < MAP_HEIGHT:
            self.player_y = new_y
        else:
            self.player_vel_y = 0

        # Update camera
        target_camera_x = max(0, min(self.player_x * TILE_SIZE - SCREEN_WIDTH // 2,
                                    MAP_WIDTH * TILE_SIZE - SCREEN_WIDTH))
        target_camera_y = max(0, min(self.player_y * TILE_SIZE - SCREEN_HEIGHT // 2,
                                    MAP_HEIGHT * TILE_SIZE - SCREEN_HEIGHT))
        
        self.camera_x += (target_camera_x - self.camera_x) * 0.1
        self.camera_y += (target_camera_y - self.camera_y) * 0.1

    def run(self):
        running = True
        print("\nFoster Youth Life Simulation")
        print("Follow the story prompts to learn important life skills!")
        print("WASD to move, click buttons to interact")
        print("ESC to exit\n")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_building_button_click(event.pos)

            # Handle modals
            if self.pizza_maker_active:
                self.pizza_maker.run()
                self.pizza_maker_active = False
                self.pizza_maker = None
            elif self.burger_maker_active:
                self.burger_maker.run()
                self.burger_maker_active = False
                self.burger_maker = None
            else:
                # Normal game update
                self.handle_input()
                self.check_building_collision()
                self.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = LifeSimulationGame()
    game.run()
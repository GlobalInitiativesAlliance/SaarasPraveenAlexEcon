"""Integration module for Part 1 Housing Game"""

import pygame
from part_1_housing_stability.game_manager import Part1GameManager
from part_1_housing_stability.mini_games import BurgerFlippingGame, DeliveryRaceGame, PlasmaTimingGame
# from part_1_housing_stability.activities.housing_dialogue_simple import SimpleHousingDialogue  # Removed
from shared.constants import *

class Part1HousingGame:
    """Main class that integrates all Part 1 components"""
    
    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        
        # Game state
        self.current_state = "intro"  # "intro", "gameplay", "minigame", "ending"
        
        # Components
        # self.dialogue_system = SimpleHousingDialogue(objective_manager)  # Removed
        self.dialogue_system = None
        self.game_manager = Part1GameManager()
        
        # Mini-games
        self.burger_game = BurgerFlippingGame()
        self.delivery_game = DeliveryRaceGame()
        self.plasma_game = PlasmaTimingGame()
        
        self.active_minigame = None
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
    def start(self):
        """Start Part 1 of the game"""
        self.active = True
        self.current_state = "intro"
        self.dialogue_system.start()
        
    def update(self, dt):
        """Update the current game state"""
        if not self.active:
            return
            
        if self.current_state == "intro":
            self.dialogue_system.update(dt)
            
            # Check if dialogue is complete
            if not self.dialogue_system.active:
                self.current_state = "gameplay"
                self.game_manager.add_notification(
                    "Welcome to reality. You have 30 days to find housing.", 
                    (255, 100, 100)
                )
                
        elif self.current_state == "gameplay":
            self.game_manager.update(dt)
            
            # Check for mini-game triggers
            if self.active_minigame:
                self.current_state = "minigame"
                
        elif self.current_state == "minigame":
            if self.active_minigame == "burger":
                self.burger_game.update(dt)
                if not self.burger_game.active:
                    # Mini-game complete
                    self.game_manager.resources.money += self.burger_game.money_earned
                    self.game_manager.add_notification(
                        f"Shift complete! Earned ${self.burger_game.money_earned:.2f}",
                        (100, 255, 100)
                    )
                    self.active_minigame = None
                    self.current_state = "gameplay"
                    
            elif self.active_minigame == "delivery":
                self.delivery_game.update(dt)
                if not self.delivery_game.active:
                    self.game_manager.resources.money += self.delivery_game.money_earned
                    self.game_manager.add_notification(
                        f"Deliveries done! Earned ${self.delivery_game.money_earned:.2f}",
                        (100, 255, 100)
                    )
                    self.active_minigame = None
                    self.current_state = "gameplay"
                    
            elif self.active_minigame == "plasma":
                self.plasma_game.update(dt)
                if not self.plasma_game.active:
                    self.game_manager.resources.money += self.plasma_game.money_earned
                    self.game_manager.add_notification(
                        f"Donation complete! Earned ${self.plasma_game.money_earned:.2f}",
                        (100, 255, 100)
                    )
                    self.active_minigame = None
                    self.current_state = "gameplay"
                    
        # Check end conditions
        if self.game_manager.resources.days_remaining <= 0:
            self.check_ending()
            
    def check_ending(self):
        """Check which ending the player achieved"""
        resources = self.game_manager.resources
        
        if resources.has_housing:
            if resources.housing_type == "apartment":
                self.show_ending("stable_housing", 
                               "You found an apartment! It's not perfect, but it's home.")
            elif resources.housing_type == "transitional":
                self.show_ending("temporary_relief",
                               "You're in transitional housing. It's temporary, but you're safe for now.")
            else:
                self.show_ending("couch_surfing",
                               "Still couch surfing, but you have a network of friends.")
        else:
            if resources.money > 500:
                self.show_ending("money_no_home",
                               "You saved money but couldn't find housing. The system failed you.")
            else:
                self.show_ending("chronic_homelessness",
                               "No money, no home. The streets are your only option now.")
                
    def show_ending(self, ending_type, message):
        """Display ending screen"""
        self.current_state = "ending"
        self.ending_message = message
        self.ending_type = ending_type
        
    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return
            
        if self.current_state == "intro":
            if event.type == pygame.KEYDOWN:
                self.dialogue_system.handle_key(event.key)
                
        elif self.current_state == "gameplay":
            result = self.game_manager.handle_input(event)
            
            # Check if a task was selected that starts a mini-game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                selected_task = self.get_selected_task()
                if selected_task:
                    if selected_task.id == "burger_shift":
                        self.active_minigame = "burger"
                        self.burger_game.start()
                    elif selected_task.id == "gig_delivery":
                        self.active_minigame = "delivery"
                        self.delivery_game.start()
                    elif selected_task.id == "plasma_donation":
                        self.active_minigame = "plasma"
                        self.plasma_game.start()
                        
        elif self.current_state == "minigame":
            if self.active_minigame == "burger":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.burger_game.handle_click(event.pos)
            elif self.active_minigame == "delivery":
                if event.type == pygame.KEYDOWN:
                    self.delivery_game.handle_key(event.key)
            elif self.active_minigame == "plasma":
                if event.type == pygame.KEYDOWN:
                    self.plasma_game.handle_key(event.key)
                    
        elif self.current_state == "ending":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Return to main game
                self.active = False
                self.completed = True
                
    def get_selected_task(self):
        """Get the currently selected task in the game manager"""
        if self.game_manager.current_view == "tasks":
            available_tasks = [t for t in self.game_manager.tasks if t.available]
            if 0 <= self.game_manager.selected_task_index < len(available_tasks):
                return available_tasks[self.game_manager.selected_task_index]
        return None
        
    def draw(self, screen):
        """Draw the current game state"""
        if not self.active:
            return
            
        if self.current_state == "intro":
            # Draw dialogue
            self.dialogue_system.draw(screen)
            
        elif self.current_state == "gameplay":
            # Draw main game
            self.game_manager.draw(screen)
            
        elif self.current_state == "minigame":
            # Draw active mini-game
            if self.active_minigame == "burger":
                self.burger_game.draw(screen)
            elif self.active_minigame == "delivery":
                self.delivery_game.draw(screen)
            elif self.active_minigame == "plasma":
                self.plasma_game.draw(screen)
                
        elif self.current_state == "ending":
            # Draw ending screen
            self.draw_ending(screen)
            
    def draw_ending(self, screen):
        """Draw the ending screen"""
        # Background
        screen.fill((20, 20, 30))
        
        # Title
        title_text = "30 DAYS LATER..."
        title_surf = self.big_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)
        
        # Ending message
        lines = self.ending_message.split(". ")
        y = 200
        for line in lines:
            if line:
                line_surf = self.font.render(line + ".", True, (200, 200, 200))
                line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                screen.blit(line_surf, line_rect)
                y += 40
                
        # Stats
        stats_y = 350
        stats = [
            f"Money saved: ${self.game_manager.resources.money:.2f}",
            f"Days with housing: {self.game_manager.resources.days_housed}",
            f"Jobs worked: {len([t for t in self.game_manager.tasks if t.category == 'work' and t.completed])}",
            f"Friends who helped: {len(self.game_manager.resources.friend_couches)}"
        ]
        
        for stat in stats:
            stat_surf = self.font.render(stat, True, (150, 150, 150))
            stat_rect = stat_surf.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
            screen.blit(stat_surf, stat_rect)
            stats_y += 30
            
        # Continue prompt
        prompt_text = "PRESS SPACE TO CONTINUE"
        prompt_surf = self.font.render(prompt_text, True, (255, 255, 100))
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        
        if pygame.time.get_ticks() % 1000 < 700:
            screen.blit(prompt_surf, prompt_rect)
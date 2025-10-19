"""Enhanced Interior Base Class with Task Support"""

import pygame
from shared.base_interior import BaseInterior
from shared.task_system import UniversalTaskSystem
from shared.constants import *

class TaskEnabledInterior(BaseInterior):
    """Base interior class with integrated task support"""
    
    def __init__(self, game, room_name, interior_type='generic'):
        super().__init__(game, room_name)
        self.interior_type = interior_type
        
        # Task system integration
        if not hasattr(game, 'task_system'):
            game.task_system = UniversalTaskSystem(game)
        self.task_system = game.task_system
        
        # Available tasks in this interior
        self.available_tasks = []
        self.selected_task_index = 0
        self.showing_task_menu = False
        
        # Interaction points
        self.interaction_points = {}
        self.setup_interaction_points()
        
        # Context-specific decorations based on current use
        self.context_decorations = []
        
    def setup_interaction_points(self):
        """Define interaction points based on interior type"""
        if self.interior_type == 'home':
            self.interaction_points = {
                'bed': {'pos': (10, 5), 'tasks': ['sleep_shelter'], 'sprite': 'bed'},
                'closet': {'pos': (12, 5), 'tasks': ['pack_belongings'], 'sprite': 'wardrobe'},
                'desk': {'pos': (8, 8), 'tasks': ['job_search', 'fill_forms'], 'sprite': 'desk'}
            }
        elif self.interior_type == 'office':
            self.interaction_points = {
                'desk': {'pos': (8, 6), 'tasks': ['apply_for_housing', 'fafsa_help', 'meet_caseworker'], 'sprite': 'desk'},
                'waiting': {'pos': (5, 8), 'tasks': ['wait_appointment'], 'sprite': 'chairs'},
                'computer': {'pos': (10, 6), 'tasks': ['use_computer', 'job_search'], 'sprite': 'computer'}
            }
        elif self.interior_type == 'store':
            self.interaction_points = {
                'counter': {'pos': (8, 4), 'tasks': ['buy_items', 'pharmacy_meds'], 'sprite': 'counter'},
                'bathroom': {'pos': (2, 2), 'tasks': ['use_bathroom', 'shower_at_gym'], 'sprite': 'door'},
                'outlet': {'pos': (14, 10), 'tasks': ['charge_phone'], 'sprite': 'outlet'}
            }
        elif self.interior_type == 'restaurant':
            self.interaction_points = {
                'kitchen': {'pos': (8, 3), 'tasks': ['work_shift'], 'sprite': 'kitchen'},
                'breakroom': {'pos': (12, 8), 'tasks': ['take_break'], 'sprite': 'table'},
                'timeclock': {'pos': (2, 6), 'tasks': ['clock_in'], 'sprite': 'timeclock'}
            }
        elif self.interior_type == 'medical':
            self.interaction_points = {
                'reception': {'pos': (8, 10), 'tasks': ['check_in', 'er_visit'], 'sprite': 'desk'},
                'exam_room': {'pos': (5, 5), 'tasks': ['see_doctor', 'free_clinic_wait'], 'sprite': 'medical'},
                'pharmacy': {'pos': (12, 5), 'tasks': ['get_prescription'], 'sprite': 'counter'}
            }
            
    def enter(self):
        """Enter the interior and set up available tasks"""
        super().enter()
        self.update_available_tasks()
        self.apply_context_decorations()
        
    def update_available_tasks(self):
        """Update list of tasks available in this interior"""
        self.available_tasks = []
        
        # Get all tasks that can be done here
        for task_id, task in self.task_system.tasks.items():
            if self.task_system.can_perform_task(task_id, self.room_name):
                # Check if near required interaction point
                for point_name, point_data in self.interaction_points.items():
                    if task_id in point_data.get('tasks', []):
                        self.available_tasks.append((task_id, point_name))
                        
    def apply_context_decorations(self):
        """Change room appearance based on current use"""
        self.context_decorations = []
        current_objective = self.game.objective_manager.get_current_objective()
        
        if not current_objective:
            return
            
        # Transform appearance based on objective
        if 'shelter' in current_objective.id and self.interior_type == 'office':
            # Office becomes shelter at night
            self.context_decorations = [
                {'type': 'sleeping_bags', 'positions': [(5, 8), (7, 8), (9, 8)]},
                {'type': 'belongings', 'positions': [(5, 9), (7, 9)]},
                {'type': 'dim_lights', 'alpha': 180}
            ]
        elif 'court' in current_objective.id and self.interior_type == 'office':
            # Office becomes courtroom
            self.context_decorations = [
                {'type': 'judge_bench', 'position': (8, 2)},
                {'type': 'defendant_table', 'position': (6, 6)},
                {'type': 'prosecutor_table', 'position': (10, 6)}
            ]
        elif 'food_bank' in current_objective.id and self.interior_type == 'office':
            # Office becomes food distribution
            self.context_decorations = [
                {'type': 'food_tables', 'positions': [(4, 6), (8, 6), (12, 6)]},
                {'type': 'queue_markers', 'positions': [(8, 8), (8, 9), (8, 10)]}
            ]
            
    def handle_event(self, event):
        """Handle input events with task support"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # Toggle task menu
                self.showing_task_menu = not self.showing_task_menu
                self.selected_task_index = 0
            elif self.showing_task_menu:
                if event.key == pygame.K_UP:
                    self.selected_task_index = max(0, self.selected_task_index - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_task_index = min(len(self.available_tasks) - 1, 
                                                  self.selected_task_index + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.start_selected_task()
                elif event.key == pygame.K_ESCAPE:
                    self.showing_task_menu = False
            else:
                # Check for interaction with E key
                if event.key == pygame.K_e:
                    self.check_interactions()
                else:
                    # Normal movement
                    super().handle_event(event)
                    
    def check_interactions(self):
        """Check if player is near any interaction point"""
        for point_name, point_data in self.interaction_points.items():
            px, py = point_data['pos']
            if abs(self.player_x - px) <= 1 and abs(self.player_y - py) <= 1:
                # Show available tasks at this point
                self.available_tasks = [(task_id, point_name) 
                                       for task_id in point_data['tasks']
                                       if task_id in self.task_system.tasks]
                if self.available_tasks:
                    self.showing_task_menu = True
                    self.selected_task_index = 0
                break
                
    def start_selected_task(self):
        """Start the currently selected task"""
        if 0 <= self.selected_task_index < len(self.available_tasks):
            task_id, point_name = self.available_tasks[self.selected_task_index]
            if self.task_system.start_task(task_id):
                self.showing_task_menu = False
                
    def update(self, dt):
        """Update interior and active tasks"""
        super().update(dt)
        
        # Update task system
        if self.task_system.active:
            self.task_system.update(dt)
            
    def draw_interaction_points(self, screen):
        """Draw interaction point indicators"""
        for point_name, point_data in self.interaction_points.items():
            px, py = point_data['pos']
            screen_x = self.room_x + px * TILE_SIZE
            screen_y = self.room_y + py * TILE_SIZE
            
            # Draw highlight if player is near
            if abs(self.player_x - px) <= 1 and abs(self.player_y - py) <= 1:
                pygame.draw.rect(screen, (255, 255, 100), 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 2)
                
                # Draw "Press E" prompt
                prompt = self.small_font.render("E", True, (255, 255, 100))
                prompt_rect = prompt.get_rect(center=(screen_x + TILE_SIZE // 2, 
                                                     screen_y - 10))
                screen.blit(prompt, prompt_rect)
                
    def draw_context_decorations(self, screen):
        """Draw context-specific decorations"""
        for decoration in self.context_decorations:
            if decoration['type'] == 'dim_lights':
                # Darken the room
                overlay = pygame.Surface((self.room_width * TILE_SIZE, 
                                        self.room_height * TILE_SIZE))
                overlay.fill((0, 0, 20))
                overlay.set_alpha(decoration['alpha'])
                screen.blit(overlay, (self.room_x, self.room_y))
            elif decoration['type'] == 'sleeping_bags':
                # Draw sleeping bag sprites
                for pos in decoration['positions']:
                    x, y = pos
                    screen_x = self.room_x + x * TILE_SIZE
                    screen_y = self.room_y + y * TILE_SIZE
                    pygame.draw.rect(screen, (80, 80, 100), 
                                   (screen_x + 4, screen_y + 8, 24, 40))
            elif decoration['type'] == 'food_tables':
                # Draw food distribution tables
                for pos in decoration['positions']:
                    x, y = pos
                    screen_x = self.room_x + x * TILE_SIZE
                    screen_y = self.room_y + y * TILE_SIZE
                    pygame.draw.rect(screen, (139, 69, 19), 
                                   (screen_x, screen_y, TILE_SIZE * 2, TILE_SIZE))
                    
    def draw_task_menu(self, screen):
        """Draw available tasks menu"""
        if not self.showing_task_menu or not self.available_tasks:
            return
            
        # Menu background
        menu_width = 400
        menu_height = 50 + len(self.available_tasks) * 40
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = 200
        
        pygame.draw.rect(screen, (40, 40, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (100, 100, 120), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Title
        title_surf = self.font.render("Available Tasks", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 25))
        screen.blit(title_surf, title_rect)
        
        # Tasks
        task_y = menu_y + 50
        for i, (task_id, point_name) in enumerate(self.available_tasks):
            task = self.task_system.tasks[task_id]
            
            # Highlight selected
            if i == self.selected_task_index:
                pygame.draw.rect(screen, (60, 60, 80), 
                               (menu_x + 10, task_y - 5, menu_width - 20, 35))
                
            # Task name
            color = (255, 255, 100) if i == self.selected_task_index else (200, 200, 200)
            task_surf = self.font.render(task.name, True, color)
            screen.blit(task_surf, (menu_x + 20, task_y))
            
            # Requirements check
            can_do, missing = self.task_system.check_requirements(task_id)
            if not can_do:
                req_surf = self.small_font.render(f"Missing: {missing[0]}", True, (255, 100, 100))
                screen.blit(req_surf, (menu_x + 20, task_y + 20))
            else:
                time_surf = self.small_font.render(f"Duration: {task.duration}h", True, (150, 150, 150))
                screen.blit(time_surf, (menu_x + 20, task_y + 20))
                
            task_y += 40
            
        # Instructions
        inst_surf = self.small_font.render("Arrow Keys: Select | Enter: Start | ESC: Cancel", 
                                         True, (150, 150, 150))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, menu_y + menu_height - 15))
        screen.blit(inst_surf, inst_rect)
        
    def draw(self, screen):
        """Draw interior with task system integration"""
        # Draw base interior
        super().draw(screen)
        
        # Draw context decorations
        self.draw_context_decorations(screen)
        
        # Draw interaction points
        self.draw_interaction_points(screen)
        
        # Draw task UI
        if self.task_system.active:
            self.task_system.draw_task_ui(screen)
        elif self.showing_task_menu:
            self.draw_task_menu(screen)
            
        # Draw current objective hint
        if hasattr(self.game, 'objective_manager'):
            obj = self.game.objective_manager.get_current_objective()
            if obj and any(task_id == obj.id for task_id, _ in self.available_tasks):
                hint_surf = self.font.render(f"Objective: {obj.description}", True, (255, 255, 100))
                hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(hint_surf, hint_rect)
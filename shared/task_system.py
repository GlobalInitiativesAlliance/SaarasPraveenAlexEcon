"""Universal Task System - Reuse interiors for different tasks across all parts"""

import pygame
from shared.constants import *
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable

@dataclass
class Task:
    """A task that can be performed in any interior"""
    id: str
    name: str
    description: str
    interior_type: str  # 'home', 'store', 'office', etc.
    duration: float  # Time in game hours
    requirements: Dict  # Money, items, stats needed
    effects: Dict  # Changes to player state
    mini_game: Optional[str] = None  # Mini-game to trigger
    time_window: Optional[tuple] = None  # (start_hour, end_hour) in 24hr
    
class UniversalTaskSystem:
    """Manages tasks across all game parts using existing interiors"""
    
    def __init__(self, game):
        self.game = game
        self.current_task = None
        self.task_progress = 0.0
        self.active = False
        
        # Define all tasks for all parts
        self.define_all_tasks()
        
        # Interior mappings - which buildings can serve which purposes
        self.interior_mappings = {
            'home': ['home_interior', 'tlp_apartment_interior', 'foster_home_interior'],
            'office': ['housing_office_interior', 'community_center_interior', 'education_center_interior'],
            'store': ['grocery_store_interior', 'pharmacy_interior'],
            'restaurant': ['pizzaplace_interior', 'burgerplace_interior'],
            'medical': ['hospital_interior', 'clinic_interior'],
            'legal': ['courtroom_interior', 'community_center_interior'],
            'education': ['classroom_interior', 'education_center_interior']
        }
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
    def define_all_tasks(self):
        """Define tasks for all game parts"""
        self.tasks = {
            # === PART 1: HOUSING TASKS ===
            'pack_belongings': Task(
                id='pack_belongings',
                name='Pack Your Life',
                description='Pack everything into garbage bags - 2 hour deadline',
                interior_type='home',
                duration=2.0,
                requirements={},
                effects={'has_belongings': True, 'stress': 20},
                mini_game='packing_game'
            ),
            
            'shower_at_gym': Task(
                id='shower_at_gym',
                name='Gym Shower',
                description='Use gym day pass to shower and clean up',
                interior_type='store',  # Reuse store as gym
                duration=1.0,
                requirements={'money': 15},
                effects={'hygiene': 80, 'money': -15, 'work_ready': 30}
            ),
            
            'apply_for_housing': Task(
                id='apply_for_housing',
                name='Housing Application',
                description='Fill out transitional housing application',
                interior_type='office',
                duration=2.0,
                requirements={'has_id': True, 'has_documents': True},
                effects={'housing_applied': True, 'stress': -10},
                mini_game='form_filling',
                time_window=(9, 15)  # Only during business hours
            ),
            
            'work_shift': Task(
                id='work_shift',
                name='Work Your Shift',
                description='Complete your scheduled work shift',
                interior_type='restaurant',
                duration=8.0,
                requirements={'work_ready': 50},
                effects={'money': 96, 'energy': -40, 'hunger': -30},
                mini_game='work_minigame'
            ),
            
            'sleep_shelter': Task(
                id='sleep_shelter',
                name='Shelter Night',
                description='Try to sleep at emergency shelter',
                interior_type='office',  # Reuse office as shelter
                duration=8.0,
                requirements={'checked_in': True},
                effects={'energy': 40, 'stress': 10, 'safety': -20},
                time_window=(20, 6)  # 8 PM to 6 AM
            ),
            
            # === PART 3: HEALTHCARE TASKS ===
            'er_visit': Task(
                id='er_visit',
                name='Emergency Room',
                description='Seek emergency medical care',
                interior_type='medical',
                duration=4.0,
                requirements={},
                effects={'health': 30, 'debt': 3847, 'stress': 20}
            ),
            
            'pharmacy_meds': Task(
                id='pharmacy_meds',
                name='Get Medication',
                description='Try to fill prescription at pharmacy',
                interior_type='store',
                duration=0.5,
                requirements={'prescription': True, 'money': 247},
                effects={'has_meds': True, 'money': -247, 'mental_health': 40}
            ),
            
            'free_clinic_wait': Task(
                id='free_clinic_wait',
                name='Free Clinic',
                description='Wait at free clinic for medical care',
                interior_type='medical',
                duration=6.0,
                requirements={},
                effects={'health': 20, 'energy': -20, 'hunger': -20}
            ),
            
            # === PART 4: FINANCIAL TASKS ===
            'payday_loan': Task(
                id='payday_loan',
                name='Quick Cash Loan',
                description='Take out high-interest payday loan',
                interior_type='office',
                duration=0.5,
                requirements={'has_id': True, 'employed': True},
                effects={'money': 300, 'debt': 390, 'stress': 15},
                mini_game='loan_terms'
            ),
            
            'plasma_donation': Task(
                id='plasma_donation',
                name='Donate Plasma',
                description='Sell plasma for quick cash',
                interior_type='medical',
                duration=2.0,
                requirements={'health': 50},
                effects={'money': 70, 'health': -15, 'energy': -25}
            ),
            
            # === PART 5: EDUCATION TASKS ===
            'ged_class': Task(
                id='ged_class',
                name='GED Class',
                description='Attend GED preparation class',
                interior_type='education',
                duration=3.0,
                requirements={'enrolled': True},
                effects={'education_progress': 10, 'energy': -20},
                time_window=(9, 12)  # Morning classes
            ),
            
            'fafsa_help': Task(
                id='fafsa_help',
                name='FAFSA Application',
                description='Get help with financial aid forms',
                interior_type='office',
                duration=2.0,
                requirements={'has_ssn': True},
                effects={'fafsa_progress': 25, 'stress': -5},
                mini_game='form_filling'
            ),
            
            # === PART 6: SOCIAL/SURVIVAL TASKS ===
            'food_bank': Task(
                id='food_bank',
                name='Food Bank',
                description='Wait in line for free groceries',
                interior_type='office',
                duration=3.0,
                requirements={},
                effects={'food': 40, 'energy': -10},
                time_window=(10, 14)
            ),
            
            'laundromat': Task(
                id='laundromat',
                name='Wash Clothes',
                description='Do laundry to stay presentable',
                interior_type='store',
                duration=2.0,
                requirements={'money': 5},
                effects={'hygiene': 30, 'work_ready': 20, 'money': -5}
            ),
            
            # === PART 7: LEGAL TASKS ===
            'court_appearance': Task(
                id='court_appearance',
                name='Court Date',
                description='Mandatory court appearance',
                interior_type='legal',
                duration=4.0,
                requirements={'dressed_appropriately': True},
                effects={'legal_status': 'pending', 'stress': 30},
                time_window=(9, 11)
            ),
            
            'public_defender': Task(
                id='public_defender',
                name='Meet Lawyer',
                description='Meet with overworked public defender',
                interior_type='office',
                duration=0.5,
                requirements={},
                effects={'has_representation': True, 'stress': -5}
            ),
            
            # === CROSS-PART TASKS ===
            'job_interview': Task(
                id='job_interview',
                name='Job Interview',
                description='Interview for better paying position',
                interior_type='office',
                duration=1.0,
                requirements={'work_ready': 70, 'has_resume': True},
                effects={'interview_complete': True},
                mini_game='interview_game'
            ),
            
            'charge_phone': Task(
                id='charge_phone',
                name='Charge Phone',
                description='Find somewhere to charge your phone',
                interior_type='store',
                duration=1.0,
                requirements={},
                effects={'phone_battery': 60}
            ),
            
            'use_computer': Task(
                id='use_computer',
                name='Computer Access',
                description='Use computer for job search/applications',
                interior_type='education',  # Library computer
                duration=2.0,
                requirements={},
                effects={'applications_sent': 5}
            )
        }
        
    def can_perform_task(self, task_id: str, current_interior: str) -> bool:
        """Check if task can be performed in current interior"""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        
        # Check if current interior matches task requirement
        interior_type = task.interior_type
        valid_interiors = self.interior_mappings.get(interior_type, [])
        
        # Check if current interior type is in valid list
        for valid in valid_interiors:
            if valid in current_interior.lower():
                return True
                
        return False
        
    def check_requirements(self, task_id: str) -> tuple[bool, List[str]]:
        """Check if player meets task requirements"""
        task = self.tasks.get(task_id)
        if not task:
            return False, ["Task not found"]
            
        missing = []
        
        # Check each requirement
        for req, value in task.requirements.items():
            if req == 'money':
                if self.game.player_money < value:
                    missing.append(f"Need ${value} (have ${self.game.player_money})")
            elif req == 'health':
                if self.game.player_health < value:
                    missing.append(f"Health too low (need {value}%)")
            elif req == 'work_ready':
                if self.game.player_work_ready < value:
                    missing.append(f"Not presentable enough for work")
            else:
                # Check boolean flags
                if not getattr(self.game, f'player_{req}', False):
                    missing.append(f"Missing: {req.replace('_', ' ').title()}")
                    
        # Check time window
        if task.time_window:
            current_hour = self.game.game_hour
            start, end = task.time_window
            if start < end:  # Normal hours (e.g., 9-17)
                if not (start <= current_hour < end):
                    missing.append(f"Only available {start}:00 - {end}:00")
            else:  # Overnight hours (e.g., 20-6)
                if not (current_hour >= start or current_hour < end):
                    missing.append(f"Only available {start}:00 - {end}:00")
                    
        return len(missing) == 0, missing
        
    def start_task(self, task_id: str) -> bool:
        """Start performing a task"""
        can_do, missing = self.check_requirements(task_id)
        if not can_do:
            self.game.show_notification(f"Can't do this: {', '.join(missing)}", (255, 100, 100))
            return False
            
        task = self.tasks[task_id]
        self.current_task = task
        self.task_progress = 0.0
        self.active = True
        
        # Start mini-game if specified
        if task.mini_game:
            self.game.start_mini_game(task.mini_game)
        else:
            self.game.show_notification(f"Started: {task.name}", (100, 200, 255))
            
        return True
        
    def update(self, dt):
        """Update current task progress"""
        if not self.active or not self.current_task:
            return
            
        # If mini-game active, wait for it
        if self.current_task.mini_game and self.game.mini_game_active:
            return
            
        # Progress task
        self.task_progress += dt / (self.current_task.duration * 60)  # Convert hours to seconds
        
        if self.task_progress >= 1.0:
            self.complete_task()
            
    def complete_task(self):
        """Complete current task and apply effects"""
        if not self.current_task:
            return
            
        # Apply effects
        for effect, value in self.current_task.effects.items():
            if effect == 'money':
                self.game.player_money += value
            elif effect == 'stress':
                self.game.player_stress = max(0, min(100, self.game.player_stress + value))
            elif effect == 'health':
                self.game.player_health = max(0, min(100, self.game.player_health + value))
            elif effect == 'energy':
                self.game.player_energy = max(0, min(100, self.game.player_energy + value))
            elif effect == 'debt':
                self.game.player_debt += value
            else:
                # Set boolean flags
                setattr(self.game, f'player_{effect}', value)
                
        # Show completion message
        self.game.show_notification(
            f"Completed: {self.current_task.name}",
            (100, 255, 100)
        )
        
        # Advance game time
        self.game.advance_time(self.current_task.duration)
        
        # Complete objective if tied to one
        if self.game.current_objective and self.game.current_objective.id == self.current_task.id:
            self.game.objective_manager.complete_current_objective()
            
        self.current_task = None
        self.active = False
        
    def draw_task_ui(self, screen):
        """Draw task progress UI"""
        if not self.active or not self.current_task:
            return
            
        # Task progress bar
        bar_width = 400
        bar_height = 40
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 150
        
        # Background
        pygame.draw.rect(screen, (40, 40, 50), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(screen, (20, 20, 30), (bar_x, bar_y, bar_width, bar_height))
        
        # Progress fill
        fill_width = int(self.task_progress * (bar_width - 4))
        if fill_width > 0:
            pygame.draw.rect(screen, (100, 200, 100), (bar_x + 2, bar_y + 2, fill_width, bar_height - 4))
            
        # Task name
        task_surf = self.font.render(self.current_task.name, True, (255, 255, 255))
        task_rect = task_surf.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(task_surf, task_rect)
        
        # Time remaining
        time_left = self.current_task.duration * (1 - self.task_progress)
        time_text = f"{int(time_left * 60)} minutes remaining"
        time_surf = self.small_font.render(time_text, True, (200, 200, 200))
        time_rect = time_surf.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 20))
        screen.blit(time_surf, time_rect)
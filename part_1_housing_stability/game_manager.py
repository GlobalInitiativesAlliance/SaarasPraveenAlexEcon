"""Part 1 Game Manager - Housing & Stability Gameplay System"""

import pygame
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Optional
from shared.constants import *

@dataclass
class PlayerResources:
    """Track player's resources"""
    money: float = 73.0
    energy: int = 100  # 0-100
    hygiene: int = 80  # 0-100, affects job performance
    phone_battery: int = 60  # 0-100, needed for many activities
    hunger: int = 70  # 0-100, depletes over time
    days_remaining: int = 30  # Days until foster care ends
    
    # Housing status
    has_housing: bool = False
    housing_type: Optional[str] = None
    days_housed: int = 0
    
    # Work status
    has_job: bool = False
    job_type: Optional[str] = None
    work_performance: int = 80  # Affects income
    
    # Relationships
    friend_couches: Dict[str, int] = None  # Name -> days available
    
    def __post_init__(self):
        if self.friend_couches is None:
            self.friend_couches = {
                "Sarah": 3,
                "Mike": 5,
                "Alex": 2
            }

@dataclass
class Task:
    """Represents an available task/activity"""
    id: str
    name: str
    description: str
    category: str  # "work", "housing", "survival", "social"
    
    # Requirements
    energy_cost: int = 0
    money_cost: float = 0
    phone_required: bool = False
    hygiene_required: int = 0  # Minimum hygiene level
    time_hours: int = 1  # How many hours it takes
    
    # Rewards
    money_reward: float = 0
    energy_reward: int = 0
    hygiene_reward: int = 0
    
    # Special effects
    unlocks: List[str] = None  # Task IDs this unlocks
    housing_progress: bool = False
    
    # Visual
    icon: str = "📋"
    color: tuple = (100, 100, 100)
    
    # Availability
    available: bool = True
    repeatable: bool = True
    completed: bool = False
    cooldown_days: int = 0
    last_completed_day: int = -999

class Part1GameManager:
    """Manages the task-based gameplay for Part 1"""
    
    def __init__(self):
        self.resources = PlayerResources()
        self.current_hour = 8  # Start at 8 AM
        self.current_view = "map"  # "map", "tasks", "status", "housing"
        self.selected_task_index = 0
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Create initial tasks
        self.tasks = self.create_initial_tasks()
        self.completed_tasks = []
        self.active_mini_game = None
        
        # UI state
        self.transition_alpha = 0
        self.notification_queue = []
        self.current_notification = None
        self.notification_timer = 0
        
        # Time of day colors
        self.time_colors = {
            6: (255, 200, 150),   # Dawn
            12: (255, 255, 200),  # Noon
            18: (255, 180, 100),  # Dusk
            22: (100, 100, 150)   # Night
        }
        
    def create_initial_tasks(self) -> List[Task]:
        """Create the initial set of available tasks"""
        return [
            # Work Tasks
            Task(
                id="burger_shift",
                name="Burger Place Shift",
                description="Work 4-hour shift flipping burgers ($60)",
                category="work",
                energy_cost=40,
                time_hours=4,
                hygiene_required=60,
                money_reward=60,
                icon="🍔",
                color=(255, 150, 50)
            ),
            
            Task(
                id="gig_delivery",
                name="Food Delivery Gig",
                description="Deliver food for 2 hours ($15-30)",
                category="work",
                energy_cost=25,
                time_hours=2,
                phone_required=True,
                money_reward=22.50,  # Average
                icon="🚴",
                color=(100, 200, 100)
            ),
            
            Task(
                id="plasma_donation",
                name="Donate Plasma",
                description="Donate plasma for $50 (can't do often)",
                category="work",
                energy_cost=30,
                time_hours=3,
                money_reward=50,
                icon="💉",
                color=(255, 100, 100),
                cooldown_days=7
            ),
            
            # Housing Search Tasks
            Task(
                id="apartment_search",
                name="Search Apartments Online",
                description="Look for affordable housing options",
                category="housing",
                energy_cost=10,
                time_hours=2,
                phone_required=True,
                housing_progress=True,
                icon="🏠",
                color=(100, 150, 255)
            ),
            
            Task(
                id="view_apartment",
                name="View Apartment",
                description="Tour a potential apartment",
                category="housing",
                energy_cost=20,
                time_hours=2,
                money_cost=20,  # Transportation
                hygiene_required=70,
                housing_progress=True,
                icon="🔍",
                color=(150, 100, 255),
                available=False  # Unlocked by apartment_search
            ),
            
            # Survival Tasks
            Task(
                id="shower_gym",
                name="Shower at Gym",
                description="Use gym day pass for shower ($10)",
                category="survival",
                energy_cost=5,
                time_hours=1,
                money_cost=10,
                hygiene_reward=80,
                icon="🚿",
                color=(100, 200, 255)
            ),
            
            Task(
                id="charge_phone",
                name="Charge Phone",
                description="Charge at library (free)",
                category="survival",
                energy_cost=5,
                time_hours=2,
                icon="🔌",
                color=(255, 255, 100)
            ),
            
            Task(
                id="eat_cheap",
                name="Dollar Menu Meal",
                description="Eat cheap fast food ($5)",
                category="survival",
                money_cost=5,
                time_hours=1,
                icon="🍕",
                color=(255, 200, 100)
            ),
            
            # Social Tasks
            Task(
                id="ask_couch",
                name="Ask Friend for Couch",
                description="See if you can crash somewhere tonight",
                category="social",
                energy_cost=10,
                time_hours=1,
                phone_required=True,
                icon="💬",
                color=(255, 150, 200)
            ),
            
            Task(
                id="sleep_rough",
                name="Sleep Outside",
                description="Find a safe place to rest (risky)",
                category="survival",
                time_hours=8,
                energy_reward=40,  # Poor quality sleep
                hygiene_reward=-30,
                icon="😴",
                color=(100, 100, 100)
            )
        ]
    
    def add_notification(self, text: str, color: tuple = (255, 255, 255)):
        """Add a notification to the queue"""
        self.notification_queue.append({
            'text': text,
            'color': color,
            'duration': 3.0
        })
        
    def update_resources(self, dt: float):
        """Update resources based on time passage"""
        # Hunger depletes over time
        self.resources.hunger = max(0, self.resources.hunger - dt * 2)
        
        # Low hunger affects energy
        if self.resources.hunger < 30:
            self.resources.energy = max(0, self.resources.energy - dt * 3)
            
        # Phone battery depletes slowly
        self.resources.phone_battery = max(0, self.resources.phone_battery - dt * 0.5)
        
        # Hygiene decreases over time
        self.resources.hygiene = max(0, self.resources.hygiene - dt * 1)
        
    def can_do_task(self, task: Task) -> tuple[bool, str]:
        """Check if player can perform a task"""
        if not task.available:
            return False, "Task not available yet"
            
        if task.energy_cost > self.resources.energy:
            return False, f"Need {task.energy_cost} energy"
            
        if task.money_cost > self.resources.money:
            return False, f"Need ${task.money_cost:.2f}"
            
        if task.phone_required and self.resources.phone_battery < 10:
            return False, "Phone battery too low"
            
        if task.hygiene_required > self.resources.hygiene:
            return False, f"Need {task.hygiene_required}% hygiene"
            
        if self.current_hour + task.time_hours > 24:
            return False, "Not enough time today"
            
        # Check cooldown
        if task.cooldown_days > 0 and not task.repeatable:
            days_since = self.resources.days_remaining - task.last_completed_day
            if days_since < task.cooldown_days:
                return False, f"Wait {task.cooldown_days - days_since} more days"
                
        return True, "Can do task"
    
    def perform_task(self, task: Task):
        """Execute a task and apply its effects"""
        # Pay costs
        self.resources.money -= task.money_cost
        self.resources.energy -= task.energy_cost
        
        # Advance time
        self.current_hour += task.time_hours
        
        # Apply rewards
        self.resources.money += task.money_reward
        self.resources.energy += task.energy_reward
        self.resources.hygiene += task.hygiene_reward
        
        # Cap resources
        self.resources.energy = max(0, min(100, self.resources.energy))
        self.resources.hygiene = max(0, min(100, self.resources.hygiene))
        self.resources.hunger = max(0, min(100, self.resources.hunger))
        self.resources.phone_battery = max(0, min(100, self.resources.phone_battery))
        
        # Track completion
        task.last_completed_day = self.resources.days_remaining
        if not task.repeatable:
            task.completed = True
            
        # Unlock new tasks
        if task.unlocks:
            for task_id in task.unlocks:
                for t in self.tasks:
                    if t.id == task_id:
                        t.available = True
                        self.add_notification(f"New option available: {t.name}", (100, 255, 100))
        
        # Add completion notification
        self.add_notification(f"Completed: {task.name}", task.color)
        
    def advance_day(self):
        """Move to the next day"""
        self.resources.days_remaining -= 1
        self.current_hour = 8  # Reset to morning
        
        # Reset daily cooldowns
        for task in self.tasks:
            if task.cooldown_days == 1:
                task.completed = False
                
        # Check housing status
        if not self.resources.has_housing:
            self.resources.energy = min(60, self.resources.energy)  # Poor sleep
            self.add_notification("Another night without stable housing...", (255, 100, 100))
        
        # Random events
        if random.random() < 0.2:
            self.trigger_random_event()
            
    def trigger_random_event(self):
        """Trigger a random event that affects resources"""
        events = [
            ("Phone screen cracked! -$30", -30, 0, 0),
            ("Found $10 on the ground!", 10, 0, 0),
            ("Food poisoning from cheap food", 0, -30, -20),
            ("Friend bought you lunch!", 5, 0, 20),
            ("Got soaked in rain", 0, -10, -40)
        ]
        
        event = random.choice(events)
        self.add_notification(event[0], (255, 255, 100))
        self.resources.money += event[1]
        self.resources.energy += event[2]
        self.resources.hygiene += event[3]
        
    def draw(self, screen):
        """Draw the current game view"""
        # Background
        screen.fill((30, 30, 40))
        
        # Draw header
        self.draw_header(screen)
        
        # Draw main content based on view
        if self.current_view == "tasks":
            self.draw_tasks_view(screen)
        elif self.current_view == "status":
            self.draw_status_view(screen)
        elif self.current_view == "housing":
            self.draw_housing_view(screen)
        else:  # map view
            self.draw_map_view(screen)
            
        # Draw notifications
        self.draw_notifications(screen)
        
    def draw_header(self, screen):
        """Draw the header with resources and time"""
        header_height = 100
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, header_height)
        pygame.draw.rect(screen, (20, 20, 30), header_rect)
        pygame.draw.line(screen, (50, 50, 60), (0, header_height), (SCREEN_WIDTH, header_height), 2)
        
        # Time and day
        time_text = f"Day {30 - self.resources.days_remaining}/30 - {self.current_hour}:00"
        time_color = self.interpolate_time_color()
        time_surf = self.font.render(time_text, True, time_color)
        screen.blit(time_surf, (20, 10))
        
        # Resources in a grid
        resources = [
            (f"${self.resources.money:.2f}", (100, 255, 100), "💵"),
            (f"Energy: {self.resources.energy}%", (255, 200, 100), "⚡"),
            (f"Hygiene: {self.resources.hygiene}%", (100, 200, 255), "🧼"),
            (f"Phone: {self.resources.phone_battery}%", (255, 255, 100), "📱"),
            (f"Hunger: {self.resources.hunger}%", (255, 150, 150), "🍔")
        ]
        
        x = 20
        y = 40
        for text, color, icon in resources:
            # Draw icon
            icon_surf = self.font.render(icon, True, color)
            screen.blit(icon_surf, (x, y))
            
            # Draw text
            text_surf = self.small_font.render(text, True, color)
            screen.blit(text_surf, (x + 30, y + 5))
            
            x += 150
            if x > SCREEN_WIDTH - 200:
                x = 20
                y += 25
                
        # Housing status
        housing_text = f"Housing: {self.resources.housing_type or 'NONE'}"
        housing_color = (100, 255, 100) if self.resources.has_housing else (255, 100, 100)
        housing_surf = self.font.render(housing_text, True, housing_color)
        screen.blit(housing_surf, (SCREEN_WIDTH - 200, 10))
        
    def draw_tasks_view(self, screen):
        """Draw the tasks selection view"""
        # Title
        title_surf = self.title_font.render("AVAILABLE TASKS", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(title_surf, title_rect)
        
        # Group tasks by category
        categories = {}
        for task in self.tasks:
            if task.category not in categories:
                categories[task.category] = []
            categories[task.category].append(task)
            
        # Draw categories
        y = 180
        task_index = 0
        
        for category, tasks in categories.items():
            # Category header
            cat_surf = self.font.render(category.upper(), True, (200, 200, 200))
            screen.blit(cat_surf, (50, y))
            y += 30
            
            # Tasks in category
            for task in tasks:
                can_do, reason = self.can_do_task(task)
                
                # Task background
                task_rect = pygame.Rect(70, y, SCREEN_WIDTH - 140, 60)
                
                if task_index == self.selected_task_index:
                    pygame.draw.rect(screen, task.color, task_rect, border_radius=10)
                    pygame.draw.rect(screen, (255, 255, 255), task_rect, width=2, border_radius=10)
                else:
                    bg_color = (40, 40, 50) if can_do else (30, 30, 35)
                    pygame.draw.rect(screen, bg_color, task_rect, border_radius=10)
                    pygame.draw.rect(screen, task.color if can_do else (60, 60, 60), 
                                   task_rect, width=1, border_radius=10)
                
                # Task icon
                icon_surf = self.title_font.render(task.icon, True, task.color)
                screen.blit(icon_surf, (task_rect.x + 10, task_rect.y + 10))
                
                # Task name and description
                name_color = (255, 255, 255) if can_do else (100, 100, 100)
                name_surf = self.font.render(task.name, True, name_color)
                screen.blit(name_surf, (task_rect.x + 60, task_rect.y + 10))
                
                desc_surf = self.small_font.render(task.description, True, (180, 180, 180))
                screen.blit(desc_surf, (task_rect.x + 60, task_rect.y + 35))
                
                # Requirements/status on the right
                if not can_do:
                    reason_surf = self.small_font.render(reason, True, (255, 100, 100))
                    reason_rect = reason_surf.get_rect(right=task_rect.right - 10, 
                                                      centery=task_rect.centery)
                    screen.blit(reason_surf, reason_rect)
                else:
                    # Show costs and rewards
                    info_parts = []
                    if task.money_cost > 0:
                        info_parts.append(f"-${task.money_cost:.0f}")
                    if task.money_reward > 0:
                        info_parts.append(f"+${task.money_reward:.0f}")
                    if task.energy_cost > 0:
                        info_parts.append(f"-{task.energy_cost}E")
                    if task.time_hours > 0:
                        info_parts.append(f"{task.time_hours}h")
                        
                    info_text = " ".join(info_parts)
                    info_surf = self.small_font.render(info_text, True, (200, 200, 200))
                    info_rect = info_surf.get_rect(right=task_rect.right - 10,
                                                  centery=task_rect.centery)
                    screen.blit(info_surf, info_rect)
                
                task_index += 1
                y += 70
                
            y += 20  # Space between categories
            
        # Instructions
        inst_text = "↑↓ Navigate   ENTER Select   TAB Change View   ESC Menu"
        inst_surf = self.small_font.render(inst_text, True, (150, 150, 150))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst_surf, inst_rect)
        
    def draw_map_view(self, screen):
        """Draw the city map view"""
        # Title
        title_surf = self.title_font.render("CITY MAP", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(title_surf, title_rect)
        
        # Draw simplified map with locations
        locations = [
            ("Burger Place", (200, 250), "🍔", self.resources.has_job and self.resources.job_type == "burger"),
            ("Plasma Center", (400, 300), "💉", False),
            ("Library", (300, 400), "📚", True),
            ("Gym", (500, 250), "🏃", False),
            ("Shelter", (350, 500), "🏠", False),
            ("Your Location", (SCREEN_WIDTH // 2, 350), "📍", True)
        ]
        
        # Draw roads
        road_color = (60, 60, 70)
        pygame.draw.line(screen, road_color, (100, 300), (700, 300), 3)
        pygame.draw.line(screen, road_color, (100, 450), (700, 450), 3)
        pygame.draw.line(screen, road_color, (250, 200), (250, 550), 3)
        pygame.draw.line(screen, road_color, (550, 200), (550, 550), 3)
        
        # Draw locations
        for name, pos, icon, accessible in locations:
            # Location marker
            color = (100, 255, 100) if accessible else (100, 100, 100)
            pygame.draw.circle(screen, color, pos, 20)
            
            # Icon
            icon_surf = self.font.render(icon, True, (255, 255, 255))
            icon_rect = icon_surf.get_rect(center=pos)
            screen.blit(icon_surf, icon_rect)
            
            # Name
            name_surf = self.small_font.render(name, True, color)
            name_rect = name_surf.get_rect(center=(pos[0], pos[1] + 30))
            screen.blit(name_surf, name_rect)
            
        # Quick actions
        action_y = 200
        quick_text = "QUICK ACTIONS:"
        quick_surf = self.font.render(quick_text, True, (200, 200, 200))
        screen.blit(quick_surf, (50, action_y))
        
        actions = [
            "1 - Go to Work",
            "2 - Find Housing", 
            "3 - Basic Needs",
            "4 - Check Status"
        ]
        
        for i, action in enumerate(actions):
            action_surf = self.small_font.render(action, True, (150, 150, 150))
            screen.blit(action_surf, (50, action_y + 30 + i * 25))
            
    def draw_status_view(self, screen):
        """Draw detailed status view"""
        # Title
        title_surf = self.title_font.render("STATUS REPORT", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(title_surf, title_rect)
        
        # Draw status bars
        self.draw_status_bar(screen, "Energy", self.resources.energy, 100, 
                           (255, 200, 100), (200, 300))
        self.draw_status_bar(screen, "Hygiene", self.resources.hygiene, 100,
                           (100, 200, 255), (200, 350))
        self.draw_status_bar(screen, "Hunger", self.resources.hunger, 100,
                           (255, 150, 150), (200, 400))
        self.draw_status_bar(screen, "Phone Battery", self.resources.phone_battery, 100,
                           (255, 255, 100), (200, 450))
        
        # Financial summary
        fin_y = 250
        fin_surf = self.font.render("FINANCIAL STATUS", True, (255, 255, 255))
        screen.blit(fin_surf, (500, fin_y))
        
        fin_details = [
            f"Current Money: ${self.resources.money:.2f}",
            f"Daily Income: ${self.calculate_daily_income():.2f}",
            f"Days Until Homeless: {self.resources.days_remaining}",
            f"Deposit Needed: $800-2800"
        ]
        
        for i, detail in enumerate(fin_details):
            detail_surf = self.small_font.render(detail, True, (180, 180, 180))
            screen.blit(detail_surf, (500, fin_y + 30 + i * 25))
            
    def draw_status_bar(self, screen, label, value, max_value, color, pos):
        """Draw a status bar"""
        # Label
        label_surf = self.small_font.render(label, True, (200, 200, 200))
        screen.blit(label_surf, (pos[0] - 100, pos[1]))
        
        # Bar background
        bar_width = 200
        bar_height = 20
        bar_rect = pygame.Rect(pos[0], pos[1], bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 60), bar_rect, border_radius=10)
        
        # Bar fill
        fill_width = int(bar_width * (value / max_value))
        if fill_width > 0:
            fill_rect = pygame.Rect(pos[0], pos[1], fill_width, bar_height)
            pygame.draw.rect(screen, color, fill_rect, border_radius=10)
            
        # Value text
        value_text = f"{value}%"
        value_surf = self.small_font.render(value_text, True, (255, 255, 255))
        value_rect = value_surf.get_rect(center=bar_rect.center)
        screen.blit(value_surf, value_rect)
        
    def draw_notifications(self, screen):
        """Draw notification messages"""
        if self.current_notification:
            # Fade in/out effect
            alpha = min(255, self.notification_timer * 500)
            if self.notification_timer > 2:
                alpha = max(0, 255 - (self.notification_timer - 2) * 500)
                
            # Notification box
            notif_surf = self.font.render(self.current_notification['text'], True, 
                                        self.current_notification['color'])
            notif_rect = notif_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            
            # Background
            bg_rect = notif_rect.inflate(40, 20)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surf.set_alpha(int(alpha * 0.8))
            bg_surf.fill((20, 20, 30))
            screen.blit(bg_surf, bg_rect)
            
            # Text
            notif_surf.set_alpha(int(alpha))
            screen.blit(notif_surf, notif_rect)
            
    def interpolate_time_color(self):
        """Get color based on time of day"""
        base_color = (200, 200, 200)
        for hour, color in self.time_colors.items():
            if abs(self.current_hour - hour) < 3:
                return color
        return base_color
        
    def calculate_daily_income(self):
        """Calculate average daily income"""
        if self.resources.has_job:
            if self.resources.job_type == "burger":
                return 60.0  # Assuming one shift per day
            elif self.resources.job_type == "gig":
                return 45.0  # Average gig income
        return 0.0
        
    def update(self, dt):
        """Update game state"""
        # Update resources
        self.update_resources(dt)
        
        # Update notifications
        if self.current_notification:
            self.notification_timer += dt
            if self.notification_timer > self.current_notification['duration']:
                self.current_notification = None
                self.notification_timer = 0
                
        # Check for next notification
        if not self.current_notification and self.notification_queue:
            self.current_notification = self.notification_queue.pop(0)
            self.notification_timer = 0
            
        # Check time progression
        if self.current_hour >= 24:
            self.advance_day()
            
        # Check game over conditions
        if self.resources.days_remaining <= 0:
            if not self.resources.has_housing:
                self.add_notification("Time's up! You're now homeless.", (255, 50, 50))
            else:
                self.add_notification("You found housing! But the struggle continues...", (100, 255, 100))
                
    def handle_input(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # Cycle through views
                views = ["map", "tasks", "status", "housing"]
                current_index = views.index(self.current_view)
                self.current_view = views[(current_index + 1) % len(views)]
                
            elif self.current_view == "tasks":
                if event.key == pygame.K_UP:
                    self.selected_task_index = max(0, self.selected_task_index - 1)
                elif event.key == pygame.K_DOWN:
                    total_tasks = len([t for t in self.tasks if t.available])
                    self.selected_task_index = min(total_tasks - 1, self.selected_task_index + 1)
                elif event.key == pygame.K_RETURN:
                    # Get selected task
                    available_tasks = [t for t in self.tasks if t.available]
                    if 0 <= self.selected_task_index < len(available_tasks):
                        task = available_tasks[self.selected_task_index]
                        can_do, reason = self.can_do_task(task)
                        if can_do:
                            self.perform_task(task)
                        else:
                            self.add_notification(f"Can't do task: {reason}", (255, 100, 100))
                            
            elif self.current_view == "map":
                # Quick number shortcuts
                if event.key == pygame.K_1:
                    self.current_view = "tasks"
                elif event.key == pygame.K_2:
                    self.current_view = "housing"
                elif event.key == pygame.K_3:
                    self.current_view = "tasks"
                elif event.key == pygame.K_4:
                    self.current_view = "status"
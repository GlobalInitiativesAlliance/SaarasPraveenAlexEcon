"""Schedule Conflict Game - Everything important happens at the same time"""

import pygame
import random
from shared.constants import *

class ScheduleConflictGame:
    """Manage conflicting appointments, work, and survival needs"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.current_week = 1
        self.total_weeks = 4
        self.money = 187  # From part-time work
        self.job_strikes = 0  # 3 = fired
        self.missed_appointments = []
        
        # Schedule grid (7 days x 24 hours)
        self.schedule_grid = {}
        self.selected_day = 0
        self.selected_hour = 9
        self.selected_event = None
        
        # Resources
        self.has_job = True
        self.has_housing_interview = False
        self.has_benefits = False
        self.stress_level = 60
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colors for different event types
        self.event_colors = {
            'work': (100, 150, 255),
            'housing': (255, 150, 100),
            'medical': (255, 100, 100),
            'benefits': (100, 255, 100),
            'court': (255, 100, 255),
            'education': (255, 255, 100)
        }
        
        # Days of week
        self.days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
    def start(self):
        """Start the scheduling game"""
        self.active = True
        self.completed = False
        self.current_week = 1
        self.generate_week_schedule()
        
    def generate_week_schedule(self):
        """Generate conflicting events for the week"""
        self.schedule_grid = {}
        
        # Fixed work schedule (part-time, irregular)
        work_shifts = [
            ('Mon', 14, 22),  # 2 PM - 10 PM
            ('Wed', 8, 16),   # 8 AM - 4 PM
            ('Thu', 16, 24),  # 4 PM - 12 AM
            ('Sat', 10, 18),  # 10 AM - 6 PM
            ('Sun', 12, 20)   # 12 PM - 8 PM
        ]
        
        for day, start, end in work_shifts:
            day_idx = self.days.index(day)
            for hour in range(start, end):
                self.add_event(day_idx, hour, {
                    'name': 'Work Shift',
                    'type': 'work',
                    'mandatory': True,
                    'description': f'${12}/hr - Need this job!',
                    'consequences': 'Strike if missed'
                })
                
        # Add conflicting appointments
        appointments = [
            {
                'name': 'Housing Office',
                'type': 'housing',
                'description': 'Apply for transitional housing',
                'hours': 2,
                'available_times': [(1, 9), (1, 14), (3, 10), (3, 14)],  # Tue/Thu business hours
                'consequences': 'Lose housing opportunity'
            },
            {
                'name': 'SNAP Benefits',
                'type': 'benefits',
                'description': 'Food assistance interview',
                'hours': 1,
                'available_times': [(0, 10), (2, 10), (4, 10)],  # MWF mornings only
                'consequences': 'No food assistance for month'
            },
            {
                'name': 'Free Clinic',
                'type': 'medical',
                'description': 'Refill anxiety medication',
                'hours': 3,
                'available_times': [(1, 8), (3, 8)],  # Tue/Thu early morning
                'consequences': 'Mental health crisis'
            },
            {
                'name': 'Court Date',
                'type': 'court',
                'description': 'Unpaid transit ticket hearing',
                'hours': 4,
                'available_times': [(2, 9)],  # Wed 9 AM only
                'consequences': 'Bench warrant issued'
            },
            {
                'name': 'Job Interview',
                'type': 'work',
                'description': 'Better paying position!',
                'hours': 2,
                'available_times': [(0, 11), (2, 15), (4, 11)],
                'consequences': 'Stay in poverty wages'
            }
        ]
        
        # Randomly place 3-4 appointments, ensuring conflicts
        selected_appointments = random.sample(appointments, random.randint(3, 4))
        
        for apt in selected_appointments:
            # Pick a time that might conflict with work
            day, hour = random.choice(apt['available_times'])
            
            # Check for conflicts
            conflicts = []
            for h in range(hour, hour + apt['hours']):
                if (day, h) in self.schedule_grid:
                    conflicts.append(self.schedule_grid[(day, h)])
                    
            event = {
                'name': apt['name'],
                'type': apt['type'],
                'description': apt['description'],
                'mandatory': False,
                'consequences': apt['consequences'],
                'duration': apt['hours'],
                'conflicts': len(conflicts) > 0
            }
            
            for h in range(hour, hour + apt['hours']):
                self.add_event(day, h, event)
                
        # Add survival necessities
        survival_events = [
            {
                'name': 'Food Bank',
                'type': 'benefits',
                'description': 'Get groceries for week',
                'hours': 3,
                'day': random.randint(0, 4),
                'hour': random.randint(10, 14)
            },
            {
                'name': 'Laundromat',
                'type': 'benefits',
                'description': 'Only clean clothes left',
                'hours': 2,
                'day': random.randint(0, 6),
                'hour': random.randint(8, 20)
            }
        ]
        
        for event_data in survival_events:
            event = {
                'name': event_data['name'],
                'type': event_data['type'],
                'description': event_data['description'],
                'mandatory': False,
                'consequences': 'Quality of life decrease',
                'duration': event_data['hours']
            }
            
            for h in range(event_data['hour'], event_data['hour'] + event_data['hours']):
                if h < 24:  # Don't go past midnight
                    self.add_event(event_data['day'], h, event)
                    
    def add_event(self, day, hour, event):
        """Add event to schedule, tracking conflicts"""
        key = (day, hour)
        if key not in self.schedule_grid:
            self.schedule_grid[key] = []
        self.schedule_grid[key].append(event)
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Check end conditions
        if self.job_strikes >= 3:
            self.end_game("Fired from job - no income")
        elif self.stress_level >= 100:
            self.end_game("Mental breakdown - hospitalized")
        elif self.current_week > self.total_weeks:
            self.end_game("Survived the month!", success=True)
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_LEFT:
            self.selected_day = max(0, self.selected_day - 1)
        elif key == pygame.K_RIGHT:
            self.selected_day = min(6, self.selected_day + 1)
        elif key == pygame.K_UP:
            self.selected_hour = max(0, self.selected_hour - 1)
        elif key == pygame.K_DOWN:
            self.selected_hour = min(23, self.selected_hour + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.select_event()
        elif key == pygame.K_n:
            self.next_week()
            
    def select_event(self):
        """Handle event selection"""
        key = (self.selected_day, self.selected_hour)
        if key in self.schedule_grid and len(self.schedule_grid[key]) > 1:
            # Multiple events at this time - must choose
            self.selected_event = self.schedule_grid[key]
            
    def choose_event(self, event_index):
        """Choose which event to attend"""
        if not self.selected_event:
            return
            
        events = self.selected_event
        chosen = events[event_index]
        
        # Apply consequences for missed events
        for i, event in enumerate(events):
            if i != event_index:
                if event['type'] == 'work':
                    self.job_strikes += 1
                    self.money -= 96  # Lost day's wages
                else:
                    self.missed_appointments.append(event['name'])
                    
                self.stress_level += 10
                
        self.selected_event = None
        
    def next_week(self):
        """Move to next week"""
        self.current_week += 1
        if self.current_week <= self.total_weeks:
            self.generate_week_schedule()
            
    def end_game(self, reason, success=False):
        """End the scheduling game"""
        self.active = False
        self.completed = True
        self.end_reason = reason
        self.success = success
        
    def draw(self, screen):
        """Draw the schedule interface"""
        if not self.active:
            return
            
        screen.fill((20, 20, 30))
        
        # Title
        title = f"SCHEDULE CONFLICTS - Week {self.current_week} of {self.total_weeks}"
        title_surf = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Stats bar
        stats_y = 70
        stats = [
            (f"${self.money}", (100, 255, 100) if self.money > 100 else (255, 100, 100)),
            (f"Job Strikes: {self.job_strikes}/3", (255, 100, 100) if self.job_strikes > 0 else (200, 200, 200)),
            (f"Stress: {self.stress_level}%", (255, 100, 100) if self.stress_level > 70 else (200, 200, 200)),
            (f"Missed: {len(self.missed_appointments)}", (255, 150, 100))
        ]
        
        x_offset = 100
        for stat_text, color in stats:
            stat_surf = self.font.render(stat_text, True, color)
            screen.blit(stat_surf, (x_offset, stats_y))
            x_offset += 180
            
        # Calendar grid
        grid_start_x = 50
        grid_start_y = 120
        cell_width = 100
        cell_height = 20
        
        # Draw hour labels
        for hour in range(24):
            hour_text = f"{hour:02d}:00"
            hour_surf = self.small_font.render(hour_text, True, (100, 100, 100))
            screen.blit(hour_surf, (5, grid_start_y + hour * cell_height))
            
        # Draw day labels and grid
        for day_idx, day in enumerate(self.days):
            # Day label
            day_color = (255, 255, 100) if day_idx == self.selected_day else (200, 200, 200)
            day_surf = self.font.render(day, True, day_color)
            day_x = grid_start_x + day_idx * cell_width + cell_width // 2 - 20
            screen.blit(day_surf, (day_x, 100))
            
            # Draw cells
            for hour in range(24):
                cell_x = grid_start_x + day_idx * cell_width
                cell_y = grid_start_y + hour * cell_height
                
                # Cell border
                cell_rect = pygame.Rect(cell_x, cell_y, cell_width - 2, cell_height - 2)
                
                # Highlight selected cell
                if day_idx == self.selected_day and hour == self.selected_hour:
                    pygame.draw.rect(screen, (255, 255, 100), cell_rect, 2)
                else:
                    pygame.draw.rect(screen, (50, 50, 60), cell_rect, 1)
                    
                # Draw events in cell
                key = (day_idx, hour)
                if key in self.schedule_grid:
                    events = self.schedule_grid[key]
                    
                    if len(events) == 1:
                        # Single event
                        event = events[0]
                        color = self.event_colors.get(event['type'], (200, 200, 200))
                        pygame.draw.rect(screen, color, cell_rect.inflate(-2, -2))
                        
                        # Event name (abbreviated)
                        name = event['name'][:8]
                        text_surf = self.small_font.render(name, True, (0, 0, 0))
                        text_rect = text_surf.get_rect(center=cell_rect.center)
                        screen.blit(text_surf, text_rect)
                    else:
                        # Conflict! Multiple events
                        pygame.draw.rect(screen, (255, 50, 50), cell_rect.inflate(-2, -2))
                        conflict_surf = self.small_font.render("CONFLICT!", True, (255, 255, 255))
                        conflict_rect = conflict_surf.get_rect(center=cell_rect.center)
                        screen.blit(conflict_surf, conflict_rect)
                        
        # Event details panel
        detail_y = grid_start_y + 24 * cell_height + 20
        
        key = (self.selected_day, self.selected_hour)
        if key in self.schedule_grid:
            events = self.schedule_grid[key]
            
            detail_box = pygame.Rect(50, detail_y, SCREEN_WIDTH - 100, 120)
            pygame.draw.rect(screen, (40, 40, 50), detail_box)
            pygame.draw.rect(screen, (100, 100, 120), detail_box, 2)
            
            if len(events) == 1:
                # Single event details
                event = events[0]
                
                # Event name
                name_surf = self.font.render(event['name'], True, self.event_colors.get(event['type'], (255, 255, 255)))
                screen.blit(name_surf, (70, detail_y + 10))
                
                # Description
                desc_surf = self.small_font.render(event['description'], True, (200, 200, 200))
                screen.blit(desc_surf, (70, detail_y + 35))
                
                # Consequences
                cons_text = f"If missed: {event['consequences']}"
                cons_surf = self.small_font.render(cons_text, True, (255, 150, 150))
                screen.blit(cons_surf, (70, detail_y + 55))
                
            else:
                # Conflict - show all events
                conflict_text = "SCHEDULING CONFLICT - Choose one:"
                conflict_surf = self.font.render(conflict_text, True, (255, 100, 100))
                screen.blit(conflict_surf, (70, detail_y + 10))
                
                y_offset = detail_y + 40
                for i, event in enumerate(events):
                    event_text = f"{i+1}. {event['name']} - {event['description']}"
                    event_surf = self.small_font.render(event_text, True, self.event_colors.get(event['type'], (255, 255, 255)))
                    screen.blit(event_surf, (90, y_offset))
                    y_offset += 20
                    
        # Instructions
        inst_text = "Arrow keys: Navigate | SPACE: Select | N: Next week"
        inst_surf = self.small_font.render(inst_text, True, (150, 150, 150))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst_surf, inst_rect)
        
        # Choice modal if selecting
        if self.selected_event:
            # Darken background
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Choice box
            choice_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
            pygame.draw.rect(screen, (30, 30, 40), choice_box)
            pygame.draw.rect(screen, (255, 100, 100), choice_box, 3)
            
            # Title
            choice_title = "IMPOSSIBLE CHOICE"
            title_surf = self.title_font.render(choice_title, True, (255, 100, 100))
            title_rect = title_surf.get_rect(center=(choice_box.centerx, choice_box.y + 30))
            screen.blit(title_surf, title_rect)
            
            # Options
            y_offset = choice_box.y + 80
            for i, event in enumerate(self.selected_event):
                option_text = f"{i+1}. {event['name']}"
                option_surf = self.font.render(option_text, True, self.event_colors.get(event['type'], (255, 255, 255)))
                screen.blit(option_surf, (choice_box.x + 20, y_offset))
                
                cons_text = f"   Miss: {event['consequences']}"
                cons_surf = self.small_font.render(cons_text, True, (255, 150, 150))
                screen.blit(cons_surf, (choice_box.x + 40, y_offset + 25))
                
                y_offset += 60
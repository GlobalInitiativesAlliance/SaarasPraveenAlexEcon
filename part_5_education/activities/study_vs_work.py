"""Study vs Work Game - Balance education and survival"""

import pygame
import random
import math
from shared.constants import *

class StudyVsWorkGame:
    """Try to balance studying with work hours needed to survive"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Time management
        self.current_week = 1
        self.total_weeks = 8  # Half semester
        self.hours_per_week = 168  # Total hours in a week
        
        # Schedule tracking
        self.scheduled_activities = {
            'work': 0,
            'class': 0,
            'study': 0,
            'sleep': 0,
            'commute': 0,
            'other': 0
        }
        
        # Academic performance
        self.gpa = 2.5
        self.attendance_rate = 100
        self.assignments_completed = 0
        self.assignments_due = 0
        self.missed_classes = 0
        
        # Life metrics
        self.money = 200
        self.health = 70
        self.stress = 40
        self.exhaustion = 30
        
        # Fixed commitments
        self.class_hours_required = 15  # Per week
        self.rent_due = 400  # Every 4 weeks
        self.food_cost_weekly = 50
        self.hourly_wage = 12
        
        # Current planning state
        self.planning_day = 'Monday'
        self.current_screen = 'weekly_plan'  # weekly_plan, daily_schedule, results
        self.selected_activity = 'work'
        self.daily_schedules = {}
        
        # Events and crises
        self.weekly_events = []
        self.current_crisis = None
        
        # Visual elements
        self.calendar_particles = []
        self.stress_indicator = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 48)
        
        # Days of week
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Initialize daily schedules
        for day in self.days:
            self.daily_schedules[day] = {
                'work': 0,
                'class': 0,
                'study': 0,
                'sleep': 6,  # Start with 6 hours default
                'commute': 0,
                'other': 0
            }
            
    def start(self):
        """Start the study vs work balancing game"""
        self.active = True
        self.completed = False
        self.current_week = 1
        self.generate_weekly_obligations()
        
    def generate_weekly_obligations(self):
        """Generate obligations for the current week"""
        # Reset weekly totals
        for key in self.scheduled_activities:
            self.scheduled_activities[key] = 0
            
        # Academic obligations
        self.assignments_due = random.randint(2, 5)
        
        # Generate potential crisis
        crisis_chance = 0.3 + (self.stress / 200)  # Higher stress = more crises
        if random.random() < crisis_chance:
            crises = [
                {'name': 'Car broke down', 'cost': 200, 'time': 8},
                {'name': 'Got sick', 'health': -20, 'time': 16},
                {'name': 'Family emergency', 'stress': 20, 'time': 24},
                {'name': 'Extra shift available', 'money': 100, 'time': -8},
                {'name': 'Group project deadline', 'time': 12, 'stress': 15}
            ]
            self.current_crisis = random.choice(crises)
        else:
            self.current_crisis = None
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if self.current_screen == 'weekly_plan':
            if key == pygame.K_TAB:
                # Cycle through days
                current_idx = self.days.index(self.planning_day)
                self.planning_day = self.days[(current_idx + 1) % 7]
            elif key == pygame.K_UP:
                # Cycle activities
                activities = list(self.daily_schedules[self.planning_day].keys())
                current_idx = activities.index(self.selected_activity)
                self.selected_activity = activities[(current_idx - 1) % len(activities)]
            elif key == pygame.K_DOWN:
                # Cycle activities
                activities = list(self.daily_schedules[self.planning_day].keys())
                current_idx = activities.index(self.selected_activity)
                self.selected_activity = activities[(current_idx + 1) % len(activities)]
            elif key == pygame.K_LEFT:
                # Decrease hours
                self.adjust_hours(-1)
            elif key == pygame.K_RIGHT:
                # Increase hours
                self.adjust_hours(1)
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                # Confirm schedule and simulate week
                self.simulate_week()
                
    def adjust_hours(self, delta):
        """Adjust hours for selected activity"""
        schedule = self.daily_schedules[self.planning_day]
        current = schedule[self.selected_activity]
        
        # Calculate total scheduled hours
        total_scheduled = sum(schedule.values())
        
        # Can't exceed 24 hours or go negative
        new_value = current + delta
        if 0 <= new_value <= 24 and total_scheduled + delta <= 24:
            schedule[self.selected_activity] = new_value
            
    def simulate_week(self):
        """Simulate the week with current schedule"""
        # Calculate weekly totals
        for day in self.days:
            for activity, hours in self.daily_schedules[day].items():
                self.scheduled_activities[activity] += hours
                
        # Work income
        work_hours = self.scheduled_activities['work']
        income = work_hours * self.hourly_wage
        self.money += income
        
        # Class attendance
        scheduled_class_hours = self.scheduled_activities['class']
        attendance_ratio = min(1.0, scheduled_class_hours / self.class_hours_required)
        self.attendance_rate = (self.attendance_rate * 0.7 + attendance_ratio * 100 * 0.3)
        
        if attendance_ratio < 0.8:
            self.missed_classes += int(self.class_hours_required - scheduled_class_hours)
            
        # Study effectiveness
        study_hours = self.scheduled_activities['study']
        sleep_hours = self.scheduled_activities['sleep']
        
        # Sleep affects study effectiveness
        sleep_ratio = min(1.0, sleep_hours / 56)  # 8 hours/night ideal
        study_effectiveness = study_hours * sleep_ratio
        
        # Complete assignments based on study time
        assignments_possible = int(study_effectiveness / 3)  # 3 hours per assignment
        self.assignments_completed = min(assignments_possible, self.assignments_due)
        
        # GPA impact
        completion_rate = self.assignments_completed / max(1, self.assignments_due)
        gpa_change = (completion_rate - 0.5) * 0.3  # +/- 0.3 GPA points
        gpa_change *= attendance_ratio  # Attendance affects grades
        self.gpa = max(0.0, min(4.0, self.gpa + gpa_change))
        
        # Health impact
        if sleep_hours < 42:  # Less than 6 hours/night average
            self.health -= (42 - sleep_hours) / 2
        if work_hours > 40:
            self.health -= (work_hours - 40) / 4
            
        # Stress impact
        total_obligations = work_hours + scheduled_class_hours + study_hours
        if total_obligations > 80:
            self.stress += (total_obligations - 80) / 2
        if self.assignments_completed < self.assignments_due:
            self.stress += (self.assignments_due - self.assignments_completed) * 10
            
        # Exhaustion
        if sleep_hours < 49:  # Less than 7 hours average
            self.exhaustion += (49 - sleep_hours) / 3
        else:
            self.exhaustion = max(0, self.exhaustion - 10)
            
        # Weekly expenses
        self.money -= self.food_cost_weekly
        
        # Rent check
        if self.current_week % 4 == 0:
            self.money -= self.rent_due
            
        # Apply crisis if any
        if self.current_crisis:
            if 'cost' in self.current_crisis:
                self.money -= self.current_crisis['cost']
            if 'health' in self.current_crisis:
                self.health += self.current_crisis['health']
            if 'stress' in self.current_crisis:
                self.stress += self.current_crisis['stress']
            if 'money' in self.current_crisis:
                self.money += self.current_crisis['money']
                
        # Advance week
        self.current_week += 1
        
        # Check end conditions
        if self.current_week > self.total_weeks:
            self.end_game()
        elif self.gpa < 2.0:
            self.end_game()
        elif self.money < -500:
            self.end_game()
        elif self.health < 0:
            self.end_game()
        else:
            # Generate next week
            self.generate_weekly_obligations()
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update visual effects
        self.stress_indicator = math.sin(pygame.time.get_ticks() * 0.01) * (self.stress / 10)
        
        # Update particles
        for particle in self.calendar_particles[:]:
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.calendar_particles.remove(particle)
                
    def end_game(self):
        """End the study vs work game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Determine outcome
        if self.gpa < 2.0:
            message = f"Academic probation. GPA: {self.gpa:.2f}"
            success = False
        elif self.money < -500:
            message = "Dropped out due to financial crisis"
            success = False
        elif self.health < 0:
            message = "Collapsed from exhaustion"
            success = False
        elif self.gpa >= 3.0 and self.money > 0:
            message = f"Balanced successfully! GPA: {self.gpa:.2f}"
            success = True
        else:
            message = f"Barely survived. GPA: {self.gpa:.2f}"
            success = False
            
        return {
            'stress': -20 if success else 30,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the study vs work interface"""
        if not self.active:
            return
            
        # Background gradient based on stress
        for y in range(SCREEN_HEIGHT):
            stress_factor = min(1.0, self.stress / 100)
            r = int(240 + stress_factor * 15)
            g = int(240 - stress_factor * 20)
            b = int(245 - stress_factor * 15)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        # Title
        title = f"WEEK {self.current_week} - BALANCE STUDY & WORK"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Status panel
        self.draw_status_panel(screen)
        
        # Main content area
        if self.current_screen == 'weekly_plan':
            self.draw_weekly_planner(screen)
            
        # Draw particles
        for particle in self.calendar_particles:
            alpha = int(255 * particle['life'] / 30)
            pygame.draw.circle(screen, (255, 200, 100, alpha),
                             (int(particle['x']), int(particle['y'])), 2)
                             
    def draw_status_panel(self, screen):
        """Draw status information panel"""
        status_rect = pygame.Rect(50, 70, SCREEN_WIDTH - 100, 100)
        pygame.draw.rect(screen, (255, 255, 255), status_rect)
        pygame.draw.rect(screen, (200, 200, 210), status_rect, 2)
        
        # Left side - Academic
        academic_x = status_rect.x + 20
        academic_y = status_rect.y + 10
        
        # GPA with color coding
        gpa_color = (100, 200, 100) if self.gpa >= 3.0 else (255, 200, 100) if self.gpa >= 2.0 else (255, 100, 100)
        gpa_text = f"GPA: {self.gpa:.2f}"
        gpa_surf = self.font.render(gpa_text, True, gpa_color)
        screen.blit(gpa_surf, (academic_x, academic_y))
        
        # Attendance
        att_y = academic_y + 25
        att_color = (100, 200, 100) if self.attendance_rate >= 80 else (255, 200, 100) if self.attendance_rate >= 60 else (255, 100, 100)
        att_text = f"Attendance: {int(self.attendance_rate)}%"
        att_surf = self.font.render(att_text, True, att_color)
        screen.blit(att_surf, (academic_x, att_y))
        
        # Assignments
        assign_y = att_y + 25
        assign_text = f"Assignments: {self.assignments_completed}/{self.assignments_due}"
        assign_color = (100, 200, 100) if self.assignments_completed >= self.assignments_due else (255, 100, 100)
        assign_surf = self.font.render(assign_text, True, assign_color)
        screen.blit(assign_surf, (academic_x, assign_y))
        
        # Center - Financial
        financial_x = status_rect.centerx - 80
        
        # Money with warning colors
        money_color = (100, 200, 100) if self.money > 100 else (255, 200, 100) if self.money > 0 else (255, 100, 100)
        money_text = f"Money: ${self.money:.2f}"
        money_surf = self.font.render(money_text, True, money_color)
        screen.blit(money_surf, (financial_x, academic_y))
        
        # Next rent
        rent_weeks_until = 4 - (self.current_week % 4)
        rent_text = f"Rent due in: {rent_weeks_until} weeks"
        rent_surf = self.font.render(rent_text, True, (100, 100, 120))
        screen.blit(rent_surf, (financial_x, academic_y + 25))
        
        # Income needed
        weekly_need = self.food_cost_weekly + (self.rent_due / 4)
        need_text = f"Need: ${weekly_need:.0f}/week"
        need_surf = self.font.render(need_text, True, (150, 150, 170))
        screen.blit(need_surf, (financial_x, academic_y + 50))
        
        # Right side - Health/Wellbeing
        health_x = status_rect.right - 180
        
        # Health bar
        health_rect = pygame.Rect(health_x, academic_y, 150, 20)
        pygame.draw.rect(screen, (220, 220, 230), health_rect)
        health_fill = pygame.Rect(health_rect.x, health_rect.y, 
                                 int(health_rect.width * max(0, self.health) / 100), 20)
        health_color = (100, 200, 100) if self.health > 60 else (255, 200, 100) if self.health > 30 else (255, 100, 100)
        pygame.draw.rect(screen, health_color, health_fill)
        pygame.draw.rect(screen, (150, 150, 160), health_rect, 2)
        health_label = self.small_font.render("Health", True, (80, 80, 90))
        screen.blit(health_label, (health_x - 50, academic_y + 2))
        
        # Stress bar
        stress_y = academic_y + 25
        stress_rect = pygame.Rect(health_x, stress_y, 150, 20)
        pygame.draw.rect(screen, (220, 220, 230), stress_rect)
        stress_fill = pygame.Rect(stress_rect.x, stress_rect.y,
                                 int(stress_rect.width * min(100, self.stress) / 100), 20)
        stress_color = (255, 100, 100) if self.stress > 70 else (255, 200, 100) if self.stress > 40 else (100, 200, 100)
        pygame.draw.rect(screen, stress_color, stress_fill)
        pygame.draw.rect(screen, (150, 150, 160), stress_rect, 2)
        stress_label = self.small_font.render("Stress", True, (80, 80, 90))
        screen.blit(stress_label, (health_x - 50, stress_y + 2))
        
        # Exhaustion
        exhaust_y = stress_y + 25
        exhaust_rect = pygame.Rect(health_x, exhaust_y, 150, 20)
        pygame.draw.rect(screen, (220, 220, 230), exhaust_rect)
        exhaust_fill = pygame.Rect(exhaust_rect.x, exhaust_rect.y,
                                  int(exhaust_rect.width * min(100, self.exhaustion) / 100), 20)
        exhaust_color = (255, 100, 100) if self.exhaustion > 70 else (255, 200, 100) if self.exhaustion > 40 else (100, 200, 100)
        pygame.draw.rect(screen, exhaust_color, exhaust_fill)
        pygame.draw.rect(screen, (150, 150, 160), exhaust_rect, 2)
        exhaust_label = self.small_font.render("Exhaustion", True, (80, 80, 90))
        screen.blit(exhaust_label, (health_x - 70, exhaust_y + 2))
        
    def draw_weekly_planner(self, screen):
        """Draw weekly schedule planner"""
        # Crisis notification if any
        if self.current_crisis:
            crisis_rect = pygame.Rect(50, 180, SCREEN_WIDTH - 100, 60)
            pygame.draw.rect(screen, (255, 240, 200), crisis_rect)
            pygame.draw.rect(screen, (255, 150, 50), crisis_rect, 3)
            
            crisis_title = f"CRISIS: {self.current_crisis['name']}"
            crisis_surf = self.font.render(crisis_title, True, (200, 50, 50))
            screen.blit(crisis_surf, (crisis_rect.x + 20, crisis_rect.y + 10))
            
            # Crisis details
            details = []
            if 'cost' in self.current_crisis:
                details.append(f"Cost: ${self.current_crisis['cost']}")
            if 'time' in self.current_crisis:
                details.append(f"Time needed: {abs(self.current_crisis['time'])}h")
            detail_text = " | ".join(details)
            detail_surf = self.small_font.render(detail_text, True, (150, 50, 50))
            screen.blit(detail_surf, (crisis_rect.x + 20, crisis_rect.y + 35))
            
        # Weekly calendar grid
        calendar_y = 260 if self.current_crisis else 200
        calendar_rect = pygame.Rect(50, calendar_y, SCREEN_WIDTH - 100, 280)
        pygame.draw.rect(screen, (255, 255, 255), calendar_rect)
        pygame.draw.rect(screen, (200, 200, 210), calendar_rect, 2)
        
        # Calendar header
        header_text = f"Planning: {self.planning_day}"
        header_surf = self.font.render(header_text, True, (60, 60, 80))
        screen.blit(header_surf, (calendar_rect.x + 20, calendar_rect.y + 10))
        
        # Day tabs
        tab_width = (calendar_rect.width - 20) // 7
        tab_y = calendar_rect.y + 40
        for i, day in enumerate(self.days):
            tab_x = calendar_rect.x + 10 + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width - 5, 25)
            
            # Highlight current day
            if day == self.planning_day:
                pygame.draw.rect(screen, (220, 230, 255), tab_rect)
                pygame.draw.rect(screen, (150, 170, 220), tab_rect, 2)
            else:
                pygame.draw.rect(screen, (240, 240, 245), tab_rect)
                pygame.draw.rect(screen, (200, 200, 210), tab_rect, 1)
                
            # Day abbreviation
            day_abbr = day[:3]
            day_surf = self.small_font.render(day_abbr, True, (60, 60, 80))
            day_rect = day_surf.get_rect(center=tab_rect.center)
            screen.blit(day_surf, day_rect)
            
        # Activity breakdown for current day
        activity_y = tab_y + 40
        schedule = self.daily_schedules[self.planning_day]
        
        activities_info = [
            ('work', 'Work Hours', (150, 200, 150)),
            ('class', 'Class Time', (150, 150, 255)),
            ('study', 'Study Time', (255, 200, 150)),
            ('sleep', 'Sleep Hours', (200, 150, 200)),
            ('commute', 'Commute', (180, 180, 190)),
            ('other', 'Other/Free', (150, 180, 150))
        ]
        
        for activity_key, activity_name, color in activities_info:
            # Activity row
            row_rect = pygame.Rect(calendar_rect.x + 20, activity_y, calendar_rect.width - 40, 30)
            
            # Highlight selected
            if activity_key == self.selected_activity:
                pygame.draw.rect(screen, (230, 240, 255), row_rect)
                
            # Activity name
            name_surf = self.font.render(activity_name, True, (60, 60, 80))
            screen.blit(name_surf, (row_rect.x + 10, row_rect.y + 5))
            
            # Hours display
            hours = schedule[activity_key]
            hours_text = f"{hours}h"
            hours_surf = self.font.render(hours_text, True, color)
            screen.blit(hours_surf, (row_rect.x + 200, row_rect.y + 5))
            
            # Visual bar
            bar_rect = pygame.Rect(row_rect.x + 250, row_rect.y + 8, 200, 14)
            pygame.draw.rect(screen, (230, 230, 240), bar_rect)
            if hours > 0:
                fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, 
                                      int(bar_rect.width * hours / 24), 14)
                pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, (180, 180, 190), bar_rect, 1)
            
            # Arrow indicators for selected
            if activity_key == self.selected_activity:
                arrow_x = row_rect.right - 30
                arrow_y = row_rect.centery
                pygame.draw.polygon(screen, (100, 100, 120),
                                  [(arrow_x - 10, arrow_y), (arrow_x, arrow_y - 5), (arrow_x, arrow_y + 5)])
                pygame.draw.polygon(screen, (100, 100, 120),
                                  [(arrow_x + 20, arrow_y), (arrow_x + 10, arrow_y - 5), (arrow_x + 10, arrow_y + 5)])
                                  
            activity_y += 35
            
        # Total hours check
        total_hours = sum(schedule.values())
        total_y = activity_y + 10
        total_text = f"Total: {total_hours}/24 hours"
        total_color = (100, 200, 100) if total_hours == 24 else (255, 200, 100) if total_hours < 24 else (255, 100, 100)
        total_surf = self.font.render(total_text, True, total_color)
        screen.blit(total_surf, (calendar_rect.x + 20, total_y))
        
        # Weekly totals on the right
        totals_rect = pygame.Rect(calendar_rect.right - 180, activity_y + 30, 160, 80)
        pygame.draw.rect(screen, (240, 240, 250), totals_rect)
        pygame.draw.rect(screen, (200, 200, 220), totals_rect, 2)
        
        weekly_work = sum(self.daily_schedules[day]['work'] for day in self.days)
        weekly_income = weekly_work * self.hourly_wage
        
        totals_text = [
            f"Weekly work: {weekly_work}h",
            f"Income: ${weekly_income:.0f}",
            f"Needed: ${self.food_cost_weekly + self.rent_due/4:.0f}"
        ]
        
        totals_y = totals_rect.y + 10
        for text in totals_text:
            text_surf = self.small_font.render(text, True, (80, 80, 100))
            screen.blit(text_surf, (totals_rect.x + 10, totals_y))
            totals_y += 20
            
        # Instructions
        inst_lines = [
            "TAB: Switch days | ↑↓: Select activity | ←→: Adjust hours",
            "ENTER: Confirm schedule and simulate week"
        ]
        inst_y = SCREEN_HEIGHT - 50
        for line in inst_lines:
            inst_surf = self.small_font.render(line, True, (120, 120, 140))
            inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect)
            inst_y += 20
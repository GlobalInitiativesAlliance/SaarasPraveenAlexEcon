"""Class Attendance Game - Balance school and survival"""

import pygame
import random
import math
from shared.constants import *

class ClassAttendanceGame:
    """Try to attend class while managing work and life crises"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Semester tracking
        self.current_week = 1
        self.total_weeks = 16  # Full semester
        self.current_day = 'Monday'
        
        # Class schedule
        self.class_schedule = {
            'Monday': [('Math', '9:00 AM'), ('English', '11:00 AM')],
            'Tuesday': [('History', '10:00 AM')],
            'Wednesday': [('Math', '9:00 AM'), ('Lab', '2:00 PM')],
            'Thursday': [('History', '10:00 AM'), ('English', '11:00 AM')],
            'Friday': [('Lab', '1:00 PM')]
        }
        
        # Attendance tracking
        self.classes_attended = {}
        self.classes_missed = {}
        self.total_classes = 0
        self.attendance_rate = 100
        
        # Academic performance
        self.gpa = 2.5
        self.grade_points = {'Math': 2.5, 'English': 2.5, 'History': 2.5, 'Lab': 2.5}
        self.assignments_missed = 0
        
        # Life circumstances
        self.work_schedule_conflict = False
        self.transportation_issues = False
        self.health_problems = False
        self.family_emergency = False
        
        # Resources
        self.money = 50
        self.has_car = False
        self.bus_pass_days = 5
        self.energy_level = 70
        
        # Current decision
        self.todays_classes = []
        self.current_class_index = 0
        self.current_conflict = None
        self.decision_made = False
        
        # Visual elements
        self.calendar_visual = {}
        self.stress_effects = []
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 32)
        
        # Initialize tracking
        for subject in ['Math', 'English', 'History', 'Lab']:
            self.classes_attended[subject] = 0
            self.classes_missed[subject] = 0
            
    def start(self):
        """Start the attendance balancing game"""
        self.active = True
        self.completed = False
        self.current_week = 1
        self.current_day = 'Monday'
        self.generate_weekly_conflicts()
        self.load_todays_classes()
        
    def generate_weekly_conflicts(self):
        """Generate conflicts for this week"""
        # Work schedule conflict
        if random.random() < 0.6:  # 60% chance
            self.work_schedule_conflict = True
            self.work_hours = random.choice([
                ('Morning shift', '7:00 AM - 3:00 PM'),
                ('Day shift', '9:00 AM - 5:00 PM'),
                ('Split shift', '6:00 AM - 10:00 AM, 4:00 PM - 8:00 PM')
            ])
        
        # Transportation issues
        if not self.has_car and random.random() < 0.4:
            self.transportation_issues = True
            self.transport_problem = random.choice([
                'Bus is running 45 minutes late',
                'Bus route cancelled today',
                'No money for bus fare',
                'Have to walk 3 miles to campus'
            ])
            
        # Random life events
        event_roll = random.random()
        if event_roll < 0.1:
            self.family_emergency = True
            self.emergency_type = random.choice([
                'Sibling needs babysitting',
                'Parent in hospital',
                'Eviction notice - need to find new place'
            ])
        elif event_roll < 0.2:
            self.health_problems = True
            self.health_issue = random.choice([
                'Severe migraine',
                'Food poisoning', 
                'No health insurance for doctor',
                'Chronic fatigue from overwork'
            ])
            
    def load_todays_classes(self):
        """Load classes for current day"""
        if self.current_day in self.class_schedule:
            self.todays_classes = self.class_schedule[self.current_day]
            self.current_class_index = 0
            self.decision_made = False
            self.check_current_conflict()
        else:
            # Weekend
            self.advance_day()
            
    def check_current_conflict(self):
        """Check if current class has conflicts"""
        if self.current_class_index >= len(self.todays_classes):
            self.advance_day()
            return
            
        class_name, class_time = self.todays_classes[self.current_class_index]
        conflicts = []
        
        # Check work conflict
        if self.work_schedule_conflict:
            work_name, work_time = self.work_hours
            if self.check_time_overlap(class_time, work_time):
                conflicts.append(('Work', f"{work_name}: {work_time}", 'Lose $60 if skip'))
                
        # Check transportation
        if self.transportation_issues:
            conflicts.append(('Transportation', self.transport_problem, 'Might miss class'))
            
        # Check emergencies
        if self.family_emergency:
            conflicts.append(('Family Emergency', self.emergency_type, 'Urgent'))
            
        if self.health_problems:
            conflicts.append(('Health', self.health_issue, 'Need rest'))
            
        # Energy check
        if self.energy_level < 30:
            conflicts.append(('Exhaustion', 'Too tired to focus', 'Risk falling asleep'))
            
        self.current_conflict = conflicts[0] if conflicts else None
        
    def check_time_overlap(self, class_time, work_time):
        """Simple time overlap check"""
        # This is simplified - just check if morning/afternoon conflict
        if 'AM' in class_time and 'AM' in work_time:
            return True
        if 'PM' in class_time and 'PM' in work_time and '12:' not in class_time:
            return True
        return 'Day shift' in work_time or 'Morning shift' in work_time
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active or self.decision_made:
            return
            
        if self.current_class_index >= len(self.todays_classes):
            return
            
        class_name, class_time = self.todays_classes[self.current_class_index]
        
        if key == pygame.K_1:  # Attend class
            self.attend_class(class_name)
        elif key == pygame.K_2:  # Skip class  
            self.skip_class(class_name)
        elif key == pygame.K_3 and self.current_conflict:  # Try to manage both
            self.attempt_both(class_name)
            
    def attend_class(self, class_name):
        """Attend the class"""
        self.classes_attended[class_name] += 1
        self.total_classes += 1
        self.decision_made = True
        
        # Consequences of attending
        if self.current_conflict:
            conflict_type = self.current_conflict[0]
            if conflict_type == 'Work':
                self.money -= 60  # Lost wages
            elif conflict_type == 'Transportation':
                self.energy_level -= 20  # Extra effort to get there
                if random.random() < 0.5:
                    # Arrived late
                    self.grade_points[class_name] -= 0.1
            elif conflict_type == 'Family Emergency':
                # Family consequences
                self.grade_points[class_name] += 0.05  # Attended but distracted
                
        # Normal attendance benefits
        else:
            self.grade_points[class_name] += 0.1
            
        self.energy_level -= 10
        self.next_class()
        
    def skip_class(self, class_name):
        """Skip the class"""
        self.classes_missed[class_name] += 1
        self.total_classes += 1
        self.decision_made = True
        
        # Academic penalty
        self.grade_points[class_name] -= 0.2
        
        # Check if missed important content
        if random.random() < 0.3:
            self.assignments_missed += 1
            self.grade_points[class_name] -= 0.1
            
        # Benefits of skipping
        if self.current_conflict:
            conflict_type = self.current_conflict[0]
            if conflict_type == 'Work':
                self.money += 60  # Earned wages
            elif conflict_type == 'Health':
                self.energy_level += 20  # Rested
            elif conflict_type == 'Transportation':
                self.energy_level += 10  # Saved effort
                
        self.next_class()
        
    def attempt_both(self, class_name):
        """Try to manage both commitments"""
        success_chance = 0.3  # Usually difficult
        
        if self.energy_level > 80:
            success_chance += 0.2
        if self.money > 100:
            success_chance += 0.1  # Can afford solutions
            
        if random.random() < success_chance:
            # Managed both!
            self.classes_attended[class_name] += 1
            self.grade_points[class_name] += 0.05
            if self.current_conflict[0] == 'Work':
                self.money += 30  # Partial pay
        else:
            # Failed - attended neither properly
            self.classes_missed[class_name] += 1
            self.grade_points[class_name] -= 0.15
            self.energy_level -= 25  # Exhausting attempt
            
        self.total_classes += 1
        self.decision_made = True
        self.next_class()
        
    def next_class(self):
        """Move to next class"""
        self.current_class_index += 1
        self.decision_made = False
        
        if self.current_class_index < len(self.todays_classes):
            self.check_current_conflict()
        else:
            self.advance_day()
            
    def advance_day(self):
        """Move to next day"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_index = days.index(self.current_day)
        self.current_day = days[(current_index + 1) % 7]
        
        # Start new week
        if self.current_day == 'Monday':
            self.current_week += 1
            if self.current_week > self.total_weeks:
                self.end_game()
            else:
                self.generate_weekly_conflicts()
                self.calculate_gpa()
                
        # Daily energy recovery
        self.energy_level = min(100, self.energy_level + 20)
        
        # Daily expenses
        self.money -= 10  # Food, etc
        
        # Load next day's classes
        self.load_todays_classes()
        
    def calculate_gpa(self):
        """Calculate current GPA"""
        total_points = sum(self.grade_points.values())
        self.gpa = total_points / len(self.grade_points)
        self.gpa = max(0.0, min(4.0, self.gpa))
        
        # Calculate attendance rate
        total_attended = sum(self.classes_attended.values())
        self.attendance_rate = (total_attended / max(1, self.total_classes)) * 100
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update stress effects based on GPA
        if self.gpa < 2.0:
            if random.random() < 0.05:
                self.stress_effects.append({
                    'x': random.randint(100, SCREEN_WIDTH - 100),
                    'y': random.randint(100, SCREEN_HEIGHT - 100),
                    'text': 'ACADEMIC PROBATION WARNING',
                    'life': 60
                })
                
        # Update visual effects
        for effect in self.stress_effects[:]:
            effect['life'] -= 1
            if effect['life'] <= 0:
                self.stress_effects.remove(effect)
                
    def end_game(self):
        """End the attendance game"""
        self.active = False
        self.completed = True
        self.calculate_gpa()
        
    def get_results(self):
        """Return game results"""
        if self.gpa < 2.0:
            message = f"Academic probation - GPA: {self.gpa:.2f}, Attendance: {self.attendance_rate:.0f}%"
            success = False
        elif self.attendance_rate < 60:
            message = f"Dropped for poor attendance ({self.attendance_rate:.0f}%)"
            success = False
        elif self.gpa >= 3.0:
            message = f"Dean's list! GPA: {self.gpa:.2f}, Attendance: {self.attendance_rate:.0f}%"
            success = True
        else:
            message = f"Completed semester - GPA: {self.gpa:.2f}, Attendance: {self.attendance_rate:.0f}%"
            success = self.gpa >= 2.5
            
        return {
            'stress': -10 if success else 20,
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the attendance decision interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((245, 245, 250))
        
        # Title
        title = f"SEMESTER WEEK {self.current_week} - {self.current_day.upper()}"
        title_surf = self.title_font.render(title, True, (50, 50, 60))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Status panel
        self.draw_status_panel(screen)
        
        # Current class decision
        if self.current_class_index < len(self.todays_classes) and not self.decision_made:
            self.draw_class_decision(screen)
        elif self.current_day in ['Saturday', 'Sunday']:
            # Weekend message
            weekend_rect = pygame.Rect(100, 300, SCREEN_WIDTH - 200, 100)
            pygame.draw.rect(screen, (240, 240, 255), weekend_rect)
            pygame.draw.rect(screen, (180, 180, 220), weekend_rect, 2)
            
            weekend_text = "Weekend - No classes scheduled"
            weekend_surf = self.font.render(weekend_text, True, (60, 60, 80))
            weekend_text_rect = weekend_surf.get_rect(center=weekend_rect.center)
            screen.blit(weekend_surf, weekend_text_rect)
            
            cont_text = "(Day will advance automatically)"
            cont_surf = self.small_font.render(cont_text, True, (100, 100, 120))
            cont_rect = cont_surf.get_rect(center=(weekend_rect.centerx, weekend_rect.centery + 30))
            screen.blit(cont_surf, cont_rect)
            
        # Draw stress warnings
        for effect in self.stress_effects:
            alpha = int(255 * effect['life'] / 60)
            warn_surf = self.font.render(effect['text'], True, (255, 50, 50))
            warn_surf.set_alpha(alpha)
            screen.blit(warn_surf, (effect['x'], effect['y']))
            
    def draw_status_panel(self, screen):
        """Draw status information"""
        # Left panel - Academic
        academic_rect = pygame.Rect(50, 80, 200, 150)
        pygame.draw.rect(screen, (255, 255, 255), academic_rect)
        pygame.draw.rect(screen, (200, 200, 210), academic_rect, 2)
        
        # GPA display
        gpa_color = (100, 200, 100) if self.gpa >= 3.0 else (255, 200, 100) if self.gpa >= 2.0 else (255, 100, 100)
        gpa_text = f"GPA: {self.gpa:.2f}"
        gpa_surf = self.big_font.render(gpa_text, True, gpa_color)
        screen.blit(gpa_surf, (academic_rect.x + 20, academic_rect.y + 15))
        
        # Attendance rate
        att_text = f"Attendance: {int(self.attendance_rate)}%"
        att_color = (100, 200, 100) if self.attendance_rate >= 80 else (255, 200, 100) if self.attendance_rate >= 60 else (255, 100, 100)
        att_surf = self.font.render(att_text, True, att_color)
        screen.blit(att_surf, (academic_rect.x + 20, academic_rect.y + 55))
        
        # Classes this semester
        class_y = academic_rect.y + 85
        for subject in ['Math', 'English', 'History', 'Lab']:
            ratio = self.classes_attended[subject] / max(1, self.classes_attended[subject] + self.classes_missed[subject])
            class_text = f"{subject}: {self.classes_attended[subject]}/{self.classes_attended[subject] + self.classes_missed[subject]}"
            class_color = (100, 200, 100) if ratio >= 0.8 else (255, 200, 100) if ratio >= 0.6 else (255, 100, 100)
            class_surf = self.small_font.render(class_text, True, class_color)
            screen.blit(class_surf, (academic_rect.x + 20, class_y))
            class_y += 20
            
        # Right panel - Resources
        resource_rect = pygame.Rect(SCREEN_WIDTH - 250, 80, 200, 150)
        pygame.draw.rect(screen, (255, 255, 255), resource_rect)
        pygame.draw.rect(screen, (200, 200, 210), resource_rect, 2)
        
        # Money
        money_color = (100, 200, 100) if self.money > 50 else (255, 200, 100) if self.money > 0 else (255, 100, 100)
        money_text = f"Money: ${self.money:.2f}"
        money_surf = self.font.render(money_text, True, money_color)
        screen.blit(money_surf, (resource_rect.x + 20, resource_rect.y + 15))
        
        # Energy
        energy_y = resource_rect.y + 45
        energy_rect = pygame.Rect(resource_rect.x + 20, energy_y, 160, 20)
        pygame.draw.rect(screen, (220, 220, 230), energy_rect)
        energy_fill = pygame.Rect(energy_rect.x, energy_rect.y,
                                 int(energy_rect.width * self.energy_level / 100), 20)
        energy_color = (100, 200, 100) if self.energy_level > 50 else (255, 200, 100) if self.energy_level > 20 else (255, 100, 100)
        pygame.draw.rect(screen, energy_color, energy_fill)
        pygame.draw.rect(screen, (180, 180, 190), energy_rect, 2)
        
        energy_label = self.small_font.render("Energy", True, (80, 80, 90))
        screen.blit(energy_label, (resource_rect.x + 20, energy_y - 18))
        
        # Transportation
        transport_y = resource_rect.y + 85
        if self.has_car:
            transport_text = "✓ Has car"
            transport_color = (100, 200, 100)
        else:
            transport_text = f"Bus pass: {self.bus_pass_days} days"
            transport_color = (255, 200, 100) if self.bus_pass_days > 0 else (255, 100, 100)
        transport_surf = self.font.render(transport_text, True, transport_color)
        screen.blit(transport_surf, (resource_rect.x + 20, transport_y))
        
        # Conflicts
        conflicts_y = resource_rect.y + 115
        if self.work_schedule_conflict:
            work_text = "⚠ Work conflict"
            work_surf = self.small_font.render(work_text, True, (255, 150, 50))
            screen.blit(work_surf, (resource_rect.x + 20, conflicts_y))
            
    def draw_class_decision(self, screen):
        """Draw current class decision screen"""
        if self.current_class_index >= len(self.todays_classes):
            return
            
        class_name, class_time = self.todays_classes[self.current_class_index]
        
        # Class info box
        class_rect = pygame.Rect(100, 250, SCREEN_WIDTH - 200, 120)
        pygame.draw.rect(screen, (250, 250, 255), class_rect)
        pygame.draw.rect(screen, (180, 180, 200), class_rect, 3)
        
        # Class details
        class_title = f"{class_name} - {class_time}"
        class_surf = self.big_font.render(class_title, True, (50, 50, 100))
        screen.blit(class_surf, (class_rect.x + 20, class_rect.y + 20))
        
        # Current grade in class
        grade_points = self.grade_points[class_name]
        letter_grade = 'A' if grade_points >= 4.0 else 'B' if grade_points >= 3.0 else 'C' if grade_points >= 2.0 else 'D' if grade_points >= 1.0 else 'F'
        grade_text = f"Current grade: {letter_grade} ({grade_points:.2f})"
        grade_surf = self.font.render(grade_text, True, (60, 60, 80))
        screen.blit(grade_surf, (class_rect.x + 20, class_rect.y + 60))
        
        # Attendance in this class
        total_class = self.classes_attended[class_name] + self.classes_missed[class_name]
        if total_class > 0:
            class_att_rate = (self.classes_attended[class_name] / total_class) * 100
            att_text = f"Attendance: {int(class_att_rate)}% ({self.classes_attended[class_name]}/{total_class})"
            att_surf = self.small_font.render(att_text, True, (80, 80, 100))
            screen.blit(att_surf, (class_rect.x + 20, class_rect.y + 90))
            
        # Conflict display
        if self.current_conflict:
            conflict_rect = pygame.Rect(100, 380, SCREEN_WIDTH - 200, 100)
            pygame.draw.rect(screen, (255, 240, 240), conflict_rect)
            pygame.draw.rect(screen, (255, 150, 150), conflict_rect, 3)
            
            conflict_type, conflict_desc, consequence = self.current_conflict
            
            conflict_title = f"CONFLICT: {conflict_type}"
            conflict_surf = self.font.render(conflict_title, True, (200, 50, 50))
            screen.blit(conflict_surf, (conflict_rect.x + 20, conflict_rect.y + 10))
            
            desc_surf = self.font.render(conflict_desc, True, (150, 50, 50))
            screen.blit(desc_surf, (conflict_rect.x + 20, conflict_rect.y + 40))
            
            cons_surf = self.small_font.render(f"Consequence: {consequence}", True, (180, 80, 80))
            screen.blit(cons_surf, (conflict_rect.x + 20, conflict_rect.y + 70))
            
        # Options
        options_y = 500
        options = [
            ("1 - Attend class", (100, 200, 100)),
            ("2 - Skip class", (255, 100, 100))
        ]
        
        if self.current_conflict:
            options.append(("3 - Try to do both", (255, 200, 100)))
            
        for option_text, color in options:
            option_rect = pygame.Rect(200, options_y, SCREEN_WIDTH - 400, 35)
            pygame.draw.rect(screen, color, option_rect, 2)
            
            option_surf = self.font.render(option_text, True, color)
            option_text_rect = option_surf.get_rect(center=option_rect.center)
            screen.blit(option_surf, option_text_rect)
            
            options_y += 45

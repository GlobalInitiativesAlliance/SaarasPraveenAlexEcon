"""Emergency Room Waiting Game - Experience the healthcare crisis"""

import pygame
import random
from shared.constants import *

class EmergencyRoomWait:
    """Survive the emergency room wait while managing pain and anxiety"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.wait_time = 0  # Hours waited
        self.pain_level = 80  # 0-100
        self.anxiety_level = 60  # 0-100
        self.exhaustion = 30  # 0-100
        self.hunger = 40  # 0-100
        
        # Resources
        self.phone_battery = 45  # %
        self.money = 12.50  # For vending machine
        self.has_insurance = False
        
        # Events and people
        self.current_event = None
        self.event_timer = 0
        self.other_patients = []
        self.triage_priority = 4  # 1-5, 5 is lowest
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Generate random patients
        self.patient_conditions = [
            "Chest pain - Priority 1",
            "Broken arm - Priority 3", 
            "Fever and cough - Priority 4",
            "Abdominal pain - Priority 3",
            "Cut requiring stitches - Priority 4",
            "Difficulty breathing - Priority 2",
            "Migraine - Priority 5",
            "Sprained ankle - Priority 5"
        ]
        
    def start(self):
        """Start the ER wait"""
        self.active = True
        self.completed = False
        self.wait_time = 0
        self.generate_waiting_room()
        
    def generate_waiting_room(self):
        """Create other patients in waiting room"""
        self.other_patients = []
        num_patients = random.randint(15, 25)
        
        for _ in range(num_patients):
            condition = random.choice(self.patient_conditions)
            arrival_time = random.randint(-120, 0)  # Arrived up to 2 hours ago
            self.other_patients.append({
                'condition': condition,
                'arrival_time': arrival_time,
                'seen': False
            })
            
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Time passes slowly in the ER
        self.wait_time += dt * 20  # 1 second = 20 seconds game time
        
        # Increase suffering
        self.pain_level = min(100, self.pain_level + dt * 2)
        self.anxiety_level = min(100, self.anxiety_level + dt * 3)
        self.exhaustion = min(100, self.exhaustion + dt * 1.5)
        self.hunger = min(100, self.hunger + dt * 1)
        
        # Drain phone battery
        if self.phone_battery > 0:
            self.phone_battery = max(0, self.phone_battery - dt * 0.5)
            
        # Random events
        if self.event_timer <= 0:
            self.trigger_random_event()
        else:
            self.event_timer -= dt
            
        # Check if finally seen (based on wait time and priority)
        min_wait = [60, 120, 240, 360, 480][self.triage_priority - 1]
        if self.wait_time >= min_wait and random.random() < 0.01:
            self.get_called()
            
        # Process other patients
        for patient in self.other_patients:
            if not patient['seen']:
                patient_wait = self.wait_time - patient['arrival_time']
                priority = int(patient['condition'].split('Priority ')[1])
                min_wait = [30, 60, 180, 300, 420][priority - 1]
                
                if patient_wait >= min_wait and random.random() < 0.02:
                    patient['seen'] = True
                    
    def trigger_random_event(self):
        """Random ER events"""
        events = [
            {
                'text': "Ambulance arrives - serious case takes priority",
                'effect': lambda: setattr(self, 'anxiety_level', min(100, self.anxiety_level + 10))
            },
            {
                'text': "Someone vomits nearby. The smell is awful.",
                'effect': lambda: setattr(self, 'anxiety_level', min(100, self.anxiety_level + 15))
            },
            {
                'text': "Nurse walks by without making eye contact",
                'effect': lambda: None
            },
            {
                'text': "Someone who arrived after you gets called",
                'effect': lambda: setattr(self, 'anxiety_level', min(100, self.anxiety_level + 20))
            },
            {
                'text': "Security escorts an aggressive patient out",
                'effect': lambda: setattr(self, 'anxiety_level', min(100, self.anxiety_level + 10))
            },
            {
                'text': "You try to sleep but the chairs are too uncomfortable",
                'effect': lambda: setattr(self, 'exhaustion', min(100, self.exhaustion + 10))
            }
        ]
        
        event = random.choice(events)
        self.current_event = event['text']
        event['effect']()
        self.event_timer = 3.0
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_1:
            # Use phone (if battery)
            if self.phone_battery > 5:
                self.phone_battery -= 5
                self.anxiety_level = max(0, self.anxiety_level - 10)
        elif key == pygame.K_2:
            # Try to sleep
            if self.exhaustion > 70:
                self.exhaustion = max(0, self.exhaustion - 20)
                self.wait_time += 1800  # 30 minutes pass
        elif key == pygame.K_3:
            # Buy from vending machine
            if self.money >= 2.50:
                self.money -= 2.50
                self.hunger = max(0, self.hunger - 30)
        elif key == pygame.K_4:
            # Ask nurse for update
            self.anxiety_level = min(100, self.anxiety_level + 5)  # Usually makes it worse
            self.current_event = "Nurse says 'It shouldn't be much longer' (3 hours ago she said the same)"
            self.event_timer = 3.0
        elif key == pygame.K_5:
            # Consider leaving
            if self.pain_level < 90:
                self.consider_leaving()
                
    def consider_leaving(self):
        """Player considers leaving without treatment"""
        self.current_event = "Leave without treatment? You'll still get a huge bill..."
        self.event_timer = 5.0
        
    def get_called(self):
        """Finally get called back"""
        self.active = False
        self.completed = True
        
    def draw(self, screen):
        """Draw the ER waiting room"""
        if not self.active:
            return
            
        # Harsh fluorescent lighting background
        screen.fill((240, 245, 240))
        
        # Title
        title = "EMERGENCY ROOM - WAITING"
        title_surf = self.title_font.render(title, True, (150, 50, 50))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Wait time
        hours = int(self.wait_time // 3600)
        minutes = int((self.wait_time % 3600) // 60)
        wait_text = f"Time Waited: {hours}h {minutes}m"
        wait_surf = self.font.render(wait_text, True, (100, 50, 50))
        screen.blit(wait_surf, (50, 70))
        
        # Triage priority
        priority_text = f"Your Priority: {self.triage_priority}/5 (Non-urgent)"
        priority_surf = self.small_font.render(priority_text, True, (100, 100, 120))
        screen.blit(priority_surf, (50, 100))
        
        # Stats panel
        stats_rect = pygame.Rect(50, 140, 300, 200)
        pygame.draw.rect(screen, (255, 255, 255), stats_rect)
        pygame.draw.rect(screen, (200, 200, 210), stats_rect, 2)
        
        # Draw stat bars
        stats = [
            ('Pain', self.pain_level, (255, 100, 100)),
            ('Anxiety', self.anxiety_level, (255, 180, 100)),
            ('Exhaustion', self.exhaustion, (150, 150, 255)),
            ('Hunger', self.hunger, (200, 150, 100))
        ]
        
        y_offset = stats_rect.y + 20
        for stat_name, value, color in stats:
            # Label
            label_surf = self.font.render(stat_name, True, (60, 60, 70))
            screen.blit(label_surf, (stats_rect.x + 10, y_offset))
            
            # Bar
            bar_rect = pygame.Rect(stats_rect.x + 100, y_offset, 180, 25)
            pygame.draw.rect(screen, (220, 220, 220), bar_rect)
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_rect.width * value / 100), 25)
            pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, (150, 150, 150), bar_rect, 2)
            
            # Value
            value_surf = self.small_font.render(f"{int(value)}%", True, (80, 80, 90))
            screen.blit(value_surf, (bar_rect.x + bar_rect.width - 35, y_offset + 5))
            
            y_offset += 40
            
        # Resources
        resources_rect = pygame.Rect(380, 140, 200, 120)
        pygame.draw.rect(screen, (250, 250, 255), resources_rect)
        pygame.draw.rect(screen, (180, 180, 200), resources_rect, 2)
        
        res_y = resources_rect.y + 10
        res_title = self.font.render("Resources", True, (60, 60, 80))
        screen.blit(res_title, (resources_rect.x + 10, res_y))
        
        res_y += 30
        phone_text = f"Phone: {int(self.phone_battery)}%"
        phone_color = (255, 100, 100) if self.phone_battery < 20 else (80, 80, 90)
        phone_surf = self.small_font.render(phone_text, True, phone_color)
        screen.blit(phone_surf, (resources_rect.x + 10, res_y))
        
        res_y += 25
        money_surf = self.small_font.render(f"Money: ${self.money:.2f}", True, (80, 80, 90))
        screen.blit(money_surf, (resources_rect.x + 10, res_y))
        
        res_y += 25
        insurance_text = "Insurance: None"
        insurance_surf = self.small_font.render(insurance_text, True, (180, 80, 80))
        screen.blit(insurance_surf, (resources_rect.x + 10, res_y))
        
        # Waiting room visualization
        waiting_rect = pygame.Rect(50, 370, SCREEN_WIDTH - 100, 150)
        pygame.draw.rect(screen, (245, 245, 250), waiting_rect)
        pygame.draw.rect(screen, (180, 180, 190), waiting_rect, 2)
        
        waiting_title = self.font.render("Waiting Room", True, (80, 80, 90))
        screen.blit(waiting_title, (waiting_rect.x + 10, waiting_rect.y + 5))
        
        # Draw other patients
        visible_patients = [p for p in self.other_patients if not p['seen']][:12]
        x_offset = waiting_rect.x + 20
        y_offset = waiting_rect.y + 40
        
        for i, patient in enumerate(visible_patients):
            # Patient icon
            if 'Priority 1' in patient['condition'] or 'Priority 2' in patient['condition']:
                color = (255, 100, 100)
            elif 'Priority 3' in patient['condition']:
                color = (255, 200, 100)
            else:
                color = (200, 200, 200)
                
            pygame.draw.circle(screen, color, (x_offset + (i % 6) * 90, y_offset + (i // 6) * 50), 15)
            
            # Wait time
            patient_wait = (self.wait_time - patient['arrival_time']) // 60
            wait_surf = self.small_font.render(f"{int(patient_wait)}m", True, (100, 100, 110))
            screen.blit(wait_surf, (x_offset + (i % 6) * 90 - 15, y_offset + (i // 6) * 50 + 20))
            
        # Current event
        if self.event_timer > 0:
            event_rect = pygame.Rect(100, 280, SCREEN_WIDTH - 200, 60)
            pygame.draw.rect(screen, (255, 250, 200), event_rect)
            pygame.draw.rect(screen, (200, 180, 100), event_rect, 2)
            
            event_lines = self.current_event.split('. ')
            ev_y = event_rect.y + 10
            for line in event_lines:
                if line:
                    line_surf = self.small_font.render(line, True, (80, 60, 40))
                    line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, ev_y))
                    screen.blit(line_surf, line_rect)
                    ev_y += 25
                    
        # Actions
        actions_y = 540
        actions = [
            "1: Use Phone (5% battery)",
            "2: Try to Sleep",
            "3: Vending Machine ($2.50)",
            "4: Ask Nurse for Update",
            "5: Consider Leaving"
        ]
        
        for action in actions:
            action_surf = self.small_font.render(action, True, (60, 60, 80))
            screen.blit(action_surf, (50, actions_y))
            actions_y += 22
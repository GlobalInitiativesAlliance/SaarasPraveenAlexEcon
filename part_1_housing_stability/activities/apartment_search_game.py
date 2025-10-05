"""Apartment Search Mini-Game - Navigate Craigslist and rental barriers"""

import pygame
import random
from shared.constants import *

class ApartmentSearchGame:
    """Search for apartments while managing time, money, and requirements"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Resources
        self.money = 73
        self.time_hours = 8  # Hours available to search
        self.phone_battery = 65
        self.data_remaining = 200  # MB
        
        # Game state
        self.current_listing_index = 0
        self.applied_count = 0
        self.viewings_scheduled = []
        self.application_fees_paid = 0
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Generate listings
        self.generate_listings()
        
        # UI state
        self.selected_action = 0  # 0: Next, 1: Call, 2: Apply, 3: Schedule
        self.message = ""
        self.message_timer = 0
        
    def generate_listings(self):
        """Generate realistic apartment listings"""
        self.listings = []
        
        # Templates for listings
        neighborhoods = ['Downtown', 'Eastside', 'Northview', 'College Area', 'Industrial']
        
        for i in range(20):
            rent = random.randint(600, 1800)
            
            # More expensive = slightly more likely to consider
            will_consider = random.random() < 0.3 if rent < 1000 else random.random() < 0.1
            
            listing = {
                'title': f"{random.choice(['Studio', '1BR', '2BR'])} in {random.choice(neighborhoods)}",
                'rent': rent,
                'deposit': rent * random.choice([1, 1.5, 2]),
                'requirements': self.generate_requirements(rent),
                'available': random.choice([True, True, False]),  # Some already rented
                'will_consider_you': will_consider,
                'viewing_time': random.randint(9, 17),  # 9 AM to 5 PM
                'application_fee': random.choice([0, 25, 35, 45, 50]),
                'red_flags': self.generate_red_flags() if rent < 800 else []
            }
            self.listings.append(listing)
            
    def generate_requirements(self, rent):
        """Generate requirements based on rent level"""
        reqs = []
        
        # Income requirement
        income_multiplier = random.choice([2.5, 3, 3.5])
        reqs.append(f"Income {income_multiplier}x rent (${int(rent * income_multiplier)}/mo)")
        
        # Credit score
        if rent > 800:
            reqs.append(f"Credit score {random.choice([650, 700, 720])}+")
            
        # Other requirements
        possible_reqs = [
            "First + Last + Deposit",
            "No evictions",
            "Employment verification",
            "References required",
            "Co-signer required",
            "Background check ($35)",
            "NO SECTION 8",
            "Professional only",
            "1 year lease minimum"
        ]
        
        # Add 2-4 random requirements
        for _ in range(random.randint(2, 4)):
            req = random.choice(possible_reqs)
            if req not in reqs:
                reqs.append(req)
                
        return reqs
        
    def generate_red_flags(self):
        """Generate red flags for cheap listings"""
        flags = []
        possible_flags = [
            "Cash only",
            "No lease provided",
            "Shared bathroom",
            "No kitchen access",
            "Must be female",
            "Utilities not included",
            "In basement",
            "No visitors allowed",
            "Mold issues"
        ]
        
        for _ in range(random.randint(0, 3)):
            flag = random.choice(possible_flags)
            if flag not in flags:
                flags.append(flag)
                
        return flags
        
    def start(self):
        """Start the apartment search"""
        self.active = True
        self.completed = False
        self.current_listing_index = 0
        self.message = "Starting apartment search..."
        self.message_timer = 2
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            
        # Check end conditions
        if self.money < 0:
            self.end_game("Ran out of money")
        elif self.time_hours <= 0:
            self.end_game("Ran out of time")
        elif self.phone_battery <= 0:
            self.end_game("Phone died")
        elif self.current_listing_index >= len(self.listings):
            self.end_game("No more listings")
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active or self.completed:
            return
            
        listing = self.listings[self.current_listing_index]
        
        if key == pygame.K_UP:
            self.selected_action = max(0, self.selected_action - 1)
        elif key == pygame.K_DOWN:
            self.selected_action = min(3, self.selected_action + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.execute_action()
        elif key == pygame.K_n:  # Quick next
            self.next_listing()
            
    def execute_action(self):
        """Execute the selected action"""
        listing = self.listings[self.current_listing_index]
        
        if self.selected_action == 0:  # Next listing
            self.next_listing()
            
        elif self.selected_action == 1:  # Call landlord
            self.time_hours -= 0.5
            self.phone_battery -= 5
            
            if not listing['available']:
                self.message = "Already rented. Wasted 30 minutes."
                self.message_timer = 3
            elif listing['will_consider_you']:
                self.message = "Landlord willing to discuss! Viewing available."
                self.message_timer = 3
                listing['can_schedule'] = True
            else:
                responses = [
                    "We require 3x income verification.",
                    "Do you have a co-signer?",
                    "Credit score must be 700+",
                    "Sorry, already have applications."
                ]
                self.message = random.choice(responses)
                self.message_timer = 3
                
        elif self.selected_action == 2:  # Apply online
            if listing['application_fee'] > 0:
                if self.money >= listing['application_fee']:
                    self.money -= listing['application_fee']
                    self.application_fees_paid += 1
                    self.time_hours -= 1
                    self.data_remaining -= 50
                    
                    if listing['will_consider_you'] and random.random() < 0.3:
                        self.message = "Application submitted! They'll call back."
                        listing['applied'] = True
                    else:
                        self.message = "Application denied. Fee non-refundable."
                    self.message_timer = 3
                else:
                    self.message = f"Need ${listing['application_fee']} for application"
                    self.message_timer = 3
            else:
                self.message = "No online application available"
                self.message_timer = 2
                
        elif self.selected_action == 3:  # Schedule viewing
            if hasattr(listing, 'can_schedule') and listing['can_schedule']:
                if listing['viewing_time'] < 15:  # During work hours
                    self.message = f"Viewing at {listing['viewing_time']}:00 - During work!"
                    self.viewings_scheduled.append(listing)
                else:
                    self.message = f"Viewing scheduled for {listing['viewing_time']}:00"
                    self.viewings_scheduled.append(listing)
                self.message_timer = 3
            else:
                self.message = "Must call first"
                self.message_timer = 2
                
    def next_listing(self):
        """Move to next listing"""
        self.current_listing_index += 1
        self.selected_action = 0
        self.time_hours -= 0.1  # Time to browse
        self.data_remaining -= 5
        self.phone_battery -= 1
        
    def end_game(self, reason):
        """End the apartment search"""
        self.completed = True
        self.active = False
        self.end_reason = reason
        
    def draw(self, screen):
        """Draw the apartment search interface"""
        if not self.active:
            return
            
        # Background
        screen.fill((20, 20, 30))
        
        # Title bar
        title = "CraigsList - Apartments / Housing"
        title_surf = self.title_font.render(title, True, (200, 200, 200))
        title_rect = title_surf.get_rect(x=50, y=30)
        screen.blit(title_surf, title_rect)
        
        # Resources bar
        resource_y = 70
        resources = [
            f"${self.money}",
            f"⏰ {self.time_hours:.1f}hrs",
            f"🔋 {self.phone_battery}%",
            f"📶 {self.data_remaining}MB"
        ]
        
        x_offset = 50
        for resource in resources:
            color = (255, 100, 100) if '⏰' in resource and self.time_hours < 2 else (200, 200, 200)
            surf = self.font.render(resource, True, color)
            screen.blit(surf, (x_offset, resource_y))
            x_offset += 150
            
        # Current listing
        if self.current_listing_index < len(self.listings):
            listing = self.listings[self.current_listing_index]
            
            # Listing box
            list_box = pygame.Rect(50, 120, SCREEN_WIDTH - 100, 400)
            pygame.draw.rect(screen, (40, 40, 50), list_box)
            pygame.draw.rect(screen, (100, 100, 120), list_box, 2)
            
            # Listing title and rent
            y_offset = 140
            title_text = f"{listing['title']} - ${listing['rent']}/mo"
            title_surf = self.font.render(title_text, True, (255, 255, 255))
            screen.blit(title_surf, (70, y_offset))
            y_offset += 40
            
            # Deposit
            deposit_text = f"Move-in cost: ${listing['deposit'] + listing['rent']}"
            deposit_surf = self.small_font.render(deposit_text, True, (255, 200, 100))
            screen.blit(deposit_surf, (70, y_offset))
            y_offset += 30
            
            # Requirements
            req_title = "Requirements:"
            req_surf = self.small_font.render(req_title, True, (200, 200, 200))
            screen.blit(req_surf, (70, y_offset))
            y_offset += 25
            
            for req in listing['requirements']:
                req_text = f"• {req}"
                color = (255, 100, 100) if any(x in req for x in ['Co-signer', '3x', 'Credit']) else (180, 180, 180)
                req_surf = self.small_font.render(req_text, True, color)
                screen.blit(req_surf, (90, y_offset))
                y_offset += 20
                
            # Red flags
            if listing['red_flags']:
                y_offset += 10
                flag_title = "⚠️ Concerns:"
                flag_surf = self.small_font.render(flag_title, True, (255, 100, 100))
                screen.blit(flag_surf, (70, y_offset))
                y_offset += 25
                
                for flag in listing['red_flags']:
                    flag_text = f"• {flag}"
                    flag_surf = self.small_font.render(flag_text, True, (255, 150, 150))
                    screen.blit(flag_surf, (90, y_offset))
                    y_offset += 20
                    
            # Application fee
            if listing['application_fee'] > 0:
                fee_text = f"Application Fee: ${listing['application_fee']}"
                color = (255, 100, 100) if listing['application_fee'] > self.money else (200, 200, 100)
                fee_surf = self.small_font.render(fee_text, True, color)
                screen.blit(fee_surf, (70, list_box.bottom - 40))
                
        # Action menu
        actions = [
            ("Next Listing", True),
            ("Call Landlord", True),
            (f"Apply (${listing['application_fee']})" if listing['application_fee'] > 0 else "Apply", True),
            ("Schedule Viewing", hasattr(listing, 'can_schedule'))
        ]
        
        action_y = list_box.bottom + 20
        for i, (action, enabled) in enumerate(actions):
            if i == self.selected_action:
                pygame.draw.rect(screen, (60, 60, 80), (50, action_y - 5, 300, 30))
                
            color = (255, 255, 255) if enabled else (100, 100, 100)
            if i == self.selected_action and enabled:
                color = (255, 255, 100)
                
            action_surf = self.font.render(action, True, color)
            screen.blit(action_surf, (60, action_y))
            action_y += 35
            
        # Message
        if self.message_timer > 0:
            msg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 100, 400, 50)
            pygame.draw.rect(screen, (40, 40, 50), msg_rect)
            pygame.draw.rect(screen, (255, 255, 100), msg_rect, 2)
            
            msg_surf = self.font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75))
            screen.blit(msg_surf, msg_rect)
            
        # Stats
        stats_text = f"Viewed: {self.current_listing_index + 1}/20 | Applied: {self.application_fees_paid} | Scheduled: {len(self.viewings_scheduled)}"
        stats_surf = self.small_font.render(stats_text, True, (150, 150, 150))
        stats_rect = stats_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(stats_surf, stats_rect)
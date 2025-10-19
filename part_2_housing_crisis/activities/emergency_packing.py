"""Emergency Packing Game - Pack essentials when facing eviction"""

import pygame
import random
from shared.constants import *

class EmergencyPackingGame:
    """Pack essential items quickly when facing sudden eviction"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Game state
        self.time_remaining = 180  # 3 minutes to pack
        self.packed_items = []
        self.available_items = []
        self.selected_item = 0
        self.backpack_weight = 0
        self.max_weight = 100
        self.stress_level = 50
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Items with properties
        self.all_items = {
            # Essential documents
            'id_documents': {'name': 'ID & Birth Certificate', 'weight': 2, 'essential': 100, 'category': 'documents'},
            'social_security': {'name': 'Social Security Card', 'weight': 1, 'essential': 95, 'category': 'documents'},
            'medical_records': {'name': 'Medical Records', 'weight': 5, 'essential': 85, 'category': 'documents'},
            'lease_papers': {'name': 'Lease & Housing Papers', 'weight': 3, 'essential': 80, 'category': 'documents'},
            'bank_cards': {'name': 'Bank Cards & Cash', 'weight': 1, 'essential': 100, 'category': 'documents'},
            
            # Survival essentials
            'medications': {'name': 'Prescription Medications', 'weight': 3, 'essential': 100, 'category': 'medical'},
            'phone_charger': {'name': 'Phone & Charger', 'weight': 2, 'essential': 95, 'category': 'tech'},
            'water_bottle': {'name': 'Water Bottle', 'weight': 4, 'essential': 70, 'category': 'survival'},
            'snacks': {'name': 'Non-perishable Food', 'weight': 8, 'essential': 65, 'category': 'survival'},
            'flashlight': {'name': 'Flashlight', 'weight': 3, 'essential': 60, 'category': 'survival'},
            
            # Clothing
            'change_clothes': {'name': '2 Changes of Clothes', 'weight': 10, 'essential': 85, 'category': 'clothing'},
            'jacket': {'name': 'Warm Jacket', 'weight': 8, 'essential': 80, 'category': 'clothing'},
            'shoes': {'name': 'Extra Shoes', 'weight': 6, 'essential': 60, 'category': 'clothing'},
            'underwear': {'name': 'Underwear (5 days)', 'weight': 3, 'essential': 75, 'category': 'clothing'},
            
            # Hygiene
            'toothbrush': {'name': 'Toothbrush & Toothpaste', 'weight': 2, 'essential': 70, 'category': 'hygiene'},
            'soap': {'name': 'Soap & Deodorant', 'weight': 3, 'essential': 65, 'category': 'hygiene'},
            'towel': {'name': 'Small Towel', 'weight': 5, 'essential': 50, 'category': 'hygiene'},
            
            # Emotional/Personal
            'photos': {'name': 'Family Photos', 'weight': 2, 'essential': 30, 'category': 'personal'},
            'journal': {'name': 'Personal Journal', 'weight': 3, 'essential': 25, 'category': 'personal'},
            'stuffed_animal': {'name': 'Childhood Stuffed Animal', 'weight': 4, 'essential': 20, 'category': 'personal'},
            
            # Work/School
            'work_uniform': {'name': 'Work Uniform', 'weight': 6, 'essential': 90, 'category': 'work'},
            'laptop': {'name': 'Laptop (if you have one)', 'weight': 8, 'essential': 85, 'category': 'work'},
            'textbooks': {'name': 'Important Textbooks', 'weight': 15, 'essential': 40, 'category': 'work'},
        }
        
        # Crisis events that can happen
        self.crisis_events = [
            "Landlord is banging on the door!",
            "You hear footsteps in the hallway...",
            "Your hands are shaking from stress",
            "Can't find your medication!",
            "Phone battery at 5%!",
            "Roommate's stuff is mixed with yours"
        ]
        self.current_crisis = None
        self.crisis_timer = 0
        
    def start(self):
        """Start the packing game"""
        self.active = True
        self.completed = False
        self.time_remaining = 180
        self.packed_items = []
        self.backpack_weight = 0
        self.stress_level = 50
        
        # Randomize item availability
        self.available_items = list(self.all_items.keys())
        random.shuffle(self.available_items)
        self.selected_item = 0
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.end_game()
            return
            
        # Increase stress over time
        self.stress_level = min(100, self.stress_level + dt * 5)
        
        # Random crisis events
        if self.crisis_timer <= 0 and random.random() < 0.01:
            self.current_crisis = random.choice(self.crisis_events)
            self.crisis_timer = 3.0
            self.stress_level = min(100, self.stress_level + 10)
        
        if self.crisis_timer > 0:
            self.crisis_timer -= dt
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_UP:
            self.selected_item = (self.selected_item - 1) % len(self.available_items)
        elif key == pygame.K_DOWN:
            self.selected_item = (self.selected_item + 1) % len(self.available_items)
        elif key == pygame.K_SPACE or key == pygame.K_RETURN:
            self.pack_item()
        elif key == pygame.K_TAB:
            # Quick pack essentials
            self.quick_pack_essentials()
            
    def pack_item(self):
        """Pack the selected item"""
        if self.selected_item >= len(self.available_items):
            return
            
        item_key = self.available_items[self.selected_item]
        item = self.all_items[item_key]
        
        # Check weight limit
        if self.backpack_weight + item['weight'] <= self.max_weight:
            self.packed_items.append(item_key)
            self.backpack_weight += item['weight']
            self.available_items.pop(self.selected_item)
            
            # Reduce stress for packing essentials
            if item['essential'] > 80:
                self.stress_level = max(0, self.stress_level - 5)
                
            # Adjust selection
            if self.selected_item >= len(self.available_items) and self.available_items:
                self.selected_item = len(self.available_items) - 1
                
    def quick_pack_essentials(self):
        """Automatically pack most essential items that fit"""
        # Sort by essential score
        sorted_items = sorted(self.available_items, 
                            key=lambda x: self.all_items[x]['essential'], 
                            reverse=True)
        
        for item_key in sorted_items:
            item = self.all_items[item_key]
            if self.backpack_weight + item['weight'] <= self.max_weight:
                self.packed_items.append(item_key)
                self.backpack_weight += item['weight']
                self.available_items.remove(item_key)
                
        # Update selected item
        if self.available_items:
            self.selected_item = 0
            
    def end_game(self):
        """End the packing game"""
        self.active = False
        self.completed = True
        
    def calculate_score(self):
        """Calculate how well the player packed"""
        if not self.packed_items:
            return 0
            
        total_essential = sum(self.all_items[item]['essential'] for item in self.packed_items)
        max_possible = sum(item['essential'] for item in self.all_items.values())
        
        return int((total_essential / max_possible) * 100)
        
    def draw(self, screen):
        """Draw the packing interface"""
        if not self.active:
            return
            
        # Dark stressed background
        screen.fill((180, 180, 190))
        
        # Crisis overlay
        if self.crisis_timer > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(int(50 * (self.crisis_timer / 3.0)))
            overlay.fill((255, 100, 100))
            screen.blit(overlay, (0, 0))
            
            # Crisis text
            crisis_surf = self.title_font.render(self.current_crisis, True, (255, 50, 50))
            crisis_rect = crisis_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(crisis_surf, crisis_rect)
        
        # Title
        title = "EMERGENCY EVICTION - PACK NOW!"
        title_surf = self.title_font.render(title, True, (200, 50, 50))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_surf, title_rect)
        
        # Timer (flashing red when low)
        timer_color = (255, 0, 0) if self.time_remaining < 30 else (50, 50, 60)
        if self.time_remaining < 10 and int(self.time_remaining * 10) % 10 < 5:
            timer_color = (255, 255, 255)
            
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        timer_text = f"TIME: {minutes}:{seconds:02d}"
        timer_surf = self.font.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (50, 60))
        
        # Weight meter
        weight_percent = self.backpack_weight / self.max_weight
        weight_color = (255, 100, 100) if weight_percent > 0.9 else (100, 200, 100)
        weight_text = f"Weight: {self.backpack_weight}/{self.max_weight} lbs"
        weight_surf = self.font.render(weight_text, True, (50, 50, 60))
        screen.blit(weight_surf, (SCREEN_WIDTH - 200, 60))
        
        # Weight bar
        bar_rect = pygame.Rect(SCREEN_WIDTH - 200, 85, 150, 20)
        pygame.draw.rect(screen, (100, 100, 100), bar_rect, 2)
        fill_rect = pygame.Rect(bar_rect.x + 2, bar_rect.y + 2, 
                               int((bar_rect.width - 4) * weight_percent), 16)
        pygame.draw.rect(screen, weight_color, fill_rect)
        
        # Stress meter
        stress_text = f"Stress: {int(self.stress_level)}%"
        stress_surf = self.font.render(stress_text, True, (150, 50, 50))
        screen.blit(stress_surf, (50, 90))
        
        # Main packing area
        main_area = pygame.Rect(50, 130, SCREEN_WIDTH - 100, 400)
        pygame.draw.rect(screen, (240, 240, 245), main_area)
        pygame.draw.rect(screen, (100, 100, 110), main_area, 2)
        
        # Available items (left side)
        avail_area = pygame.Rect(main_area.x + 10, main_area.y + 10, 
                                main_area.width // 2 - 20, main_area.height - 20)
        pygame.draw.rect(screen, (255, 255, 255), avail_area)
        pygame.draw.rect(screen, (180, 180, 190), avail_area, 1)
        
        avail_title = self.font.render("AVAILABLE ITEMS", True, (50, 50, 60))
        screen.blit(avail_title, (avail_area.x + 10, avail_area.y + 5))
        
        # Draw available items
        y_offset = avail_area.y + 35
        visible_start = max(0, self.selected_item - 5)
        visible_end = min(len(self.available_items), visible_start + 10)
        
        for i in range(visible_start, visible_end):
            if i >= len(self.available_items):
                break
                
            item_key = self.available_items[i]
            item = self.all_items[item_key]
            
            # Highlight selected
            if i == self.selected_item:
                sel_rect = pygame.Rect(avail_area.x + 5, y_offset - 2, 
                                     avail_area.width - 10, 30)
                pygame.draw.rect(screen, (200, 220, 255), sel_rect)
                
            # Item name
            name_color = (50, 50, 60) if i != self.selected_item else (0, 0, 200)
            name_surf = self.small_font.render(item['name'], True, name_color)
            screen.blit(name_surf, (avail_area.x + 10, y_offset))
            
            # Weight and importance
            info_text = f"{item['weight']}lbs"
            if item['essential'] > 80:
                info_text += " ⚠️"
            info_surf = self.small_font.render(info_text, True, (100, 100, 120))
            screen.blit(info_surf, (avail_area.x + avail_area.width - 60, y_offset))
            
            y_offset += 35
            
        # Packed items (right side)
        packed_area = pygame.Rect(main_area.x + main_area.width // 2 + 10, 
                                 main_area.y + 10,
                                 main_area.width // 2 - 20, main_area.height - 20)
        pygame.draw.rect(screen, (240, 255, 240), packed_area)
        pygame.draw.rect(screen, (100, 180, 100), packed_area, 1)
        
        packed_title = self.font.render("PACKED ITEMS", True, (50, 120, 50))
        screen.blit(packed_title, (packed_area.x + 10, packed_area.y + 5))
        
        # Draw packed items
        y_offset = packed_area.y + 35
        for item_key in self.packed_items[:10]:  # Show first 10
            item = self.all_items[item_key]
            item_surf = self.small_font.render(f"✓ {item['name']}", True, (50, 120, 50))
            screen.blit(item_surf, (packed_area.x + 10, y_offset))
            y_offset += 25
            
        if len(self.packed_items) > 10:
            more_text = f"... and {len(self.packed_items) - 10} more items"
            more_surf = self.small_font.render(more_text, True, (100, 150, 100))
            screen.blit(more_surf, (packed_area.x + 10, y_offset))
            
        # Instructions
        inst_lines = [
            "↑↓ Select item | SPACE Pack item | TAB Quick pack essentials"
        ]
        inst_y = SCREEN_HEIGHT - 40
        for line in inst_lines:
            inst_surf = self.small_font.render(line, True, (100, 100, 120))
            inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect)
            inst_y += 20
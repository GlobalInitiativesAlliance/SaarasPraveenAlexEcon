"""Packing Game - Interactive room where you pack belongings under time pressure"""

import pygame
import random
import math
from shared.constants import *

class PackingGame:
    """Pack your life into boxes - interactive room experience"""
    
    def __init__(self):
        self.active = False
        self.completed = False
        
        # Room setup
        self.room_width = 16
        self.room_height = 12
        self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
        self.room_y = (SCREEN_HEIGHT - self.room_height * TILE_SIZE) // 2 + 20
        
        # Player position
        self.player_x = 8
        self.player_y = 10
        self.player_facing = "up"
        
        # Time pressure
        self.time_limit = 120  # 2 minutes in seconds
        self.time_remaining = self.time_limit
        self.stress_level = 30
        
        # Packing state
        self.suitcase_capacity = 20
        self.items_packed = []
        self.total_weight = 0
        self.max_weight = 50  # pounds
        
        # Items in room
        self.items = []
        self.selected_item = None
        self.interaction_range = 1.5
        
        # Visual effects
        self.clock_flash = 0
        self.stress_particles = []
        self.pack_effects = []
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.timer_font = pygame.font.Font(None, 48)
        
        # Room tiles (simple layout)
        self.room_tiles = []
        self.init_room()
        self.place_items()
        
    def init_room(self):
        """Initialize room layout"""
        # Create basic room
        self.room_tiles = []
        for y in range(self.room_height):
            row = []
            for x in range(self.room_width):
                # Walls
                if x == 0 or x == self.room_width - 1 or y == 0 or y == self.room_height - 1:
                    row.append(1)  # Wall
                else:
                    row.append(0)  # Floor
            self.room_tiles.append(row)
            
        # Add furniture (obstacles)
        # Bed
        for x in range(1, 4):
            for y in range(1, 3):
                self.room_tiles[y][x] = 2
                
        # Desk
        for x in range(12, 15):
            self.room_tiles[1][x] = 2
            self.room_tiles[2][x] = 2
            
        # Dresser
        for y in range(5, 8):
            self.room_tiles[y][14] = 2
            
    def place_items(self):
        """Place packable items around the room"""
        # Define item types with properties
        item_types = [
            # Essential items (high value, low weight)
            {'name': 'ID & Documents', 'x': 13, 'y': 3, 'weight': 0.5, 'value': 100, 'essential': True, 'color': (255, 200, 100)},
            {'name': 'Phone Charger', 'x': 12, 'y': 3, 'weight': 0.5, 'value': 80, 'essential': True, 'color': (200, 200, 255)},
            {'name': 'Medications', 'x': 14, 'y': 8, 'weight': 1, 'value': 90, 'essential': True, 'color': (255, 150, 150)},
            {'name': 'Money/Cards', 'x': 7, 'y': 7, 'weight': 0.1, 'value': 100, 'essential': True, 'color': (100, 255, 100)},
            
            # Practical items
            {'name': 'Work Clothes', 'x': 13, 'y': 6, 'weight': 3, 'value': 70, 'essential': False, 'color': (150, 150, 200)},
            {'name': 'Laptop', 'x': 13, 'y': 2, 'weight': 3, 'value': 85, 'essential': False, 'color': (200, 200, 200)},
            {'name': 'Shoes', 'x': 10, 'y': 9, 'weight': 2, 'value': 60, 'essential': False, 'color': (150, 100, 50)},
            {'name': 'Jacket', 'x': 2, 'y': 5, 'weight': 2, 'value': 65, 'essential': False, 'color': (100, 150, 100)},
            {'name': 'Toiletries', 'x': 5, 'y': 2, 'weight': 2, 'value': 50, 'essential': False, 'color': (150, 200, 255)},
            
            # Sentimental items (low practical value, emotional weight)
            {'name': 'Photo Album', 'x': 4, 'y': 8, 'weight': 2, 'value': 20, 'essential': False, 'color': (255, 200, 200)},
            {'name': "Mom's Necklace", 'x': 6, 'y': 5, 'weight': 0.5, 'value': 15, 'essential': False, 'color': (255, 255, 200)},
            {'name': 'Childhood Toy', 'x': 2, 'y': 8, 'weight': 1, 'value': 10, 'essential': False, 'color': (255, 150, 200)},
            {'name': 'Letters', 'x': 9, 'y': 4, 'weight': 0.5, 'value': 25, 'essential': False, 'color': (200, 255, 200)},
            
            # Bulky items (hard choices)
            {'name': 'Blanket', 'x': 5, 'y': 10, 'weight': 3, 'value': 40, 'essential': False, 'color': (180, 180, 220)},
            {'name': 'Books', 'x': 11, 'y': 2, 'weight': 5, 'value': 30, 'essential': False, 'color': (200, 150, 100)},
            {'name': 'Kitchen Stuff', 'x': 8, 'y': 2, 'weight': 4, 'value': 45, 'essential': False, 'color': (180, 180, 180)},
            
            # Extra clothes
            {'name': 'Extra Clothes', 'x': 13, 'y': 9, 'weight': 4, 'value': 35, 'essential': False, 'color': (200, 150, 200)},
            {'name': 'Winter Coat', 'x': 3, 'y': 10, 'weight': 4, 'value': 55, 'essential': False, 'color': (100, 100, 150)}
        ]
        
        # Create items
        self.items = []
        for item_data in item_types:
            # Make sure position is valid
            if self.is_valid_position(item_data['x'], item_data['y']):
                self.items.append({
                    'name': item_data['name'],
                    'x': item_data['x'],
                    'y': item_data['y'],
                    'weight': item_data['weight'],
                    'value': item_data['value'],
                    'essential': item_data['essential'],
                    'color': item_data['color'],
                    'packed': False,
                    'hover': False
                })
                
    def is_valid_position(self, x, y):
        """Check if position is valid for placing items"""
        if 0 <= y < self.room_height and 0 <= x < self.room_width:
            return self.room_tiles[y][x] == 0  # Floor tile
        return False
        
    def start(self):
        """Start the packing game"""
        self.active = True
        self.completed = False
        self.time_remaining = self.time_limit
        self.items_packed = []
        self.total_weight = 0
        self.stress_level = 30
        
        # Reset items
        for item in self.items:
            item['packed'] = False
            
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        # Movement
        new_x, new_y = self.player_x, self.player_y
        
        if key == pygame.K_UP or key == pygame.K_w:
            new_y = self.player_y - 1
            self.player_facing = "up"
        elif key == pygame.K_DOWN or key == pygame.K_s:
            new_y = self.player_y + 1
            self.player_facing = "down"
        elif key == pygame.K_LEFT or key == pygame.K_a:
            new_x = self.player_x - 1
            self.player_facing = "left"
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            new_x = self.player_x + 1
            self.player_facing = "right"
        elif key == pygame.K_e or key == pygame.K_SPACE:
            # Pack nearby item
            self.pack_nearby_item()
            
        # Check if new position is walkable
        if self.is_walkable(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y
            
    def is_walkable(self, x, y):
        """Check if a position is walkable"""
        if 0 <= y < self.room_height and 0 <= x < self.room_width:
            return self.room_tiles[y][x] == 0
        return False
        
    def pack_nearby_item(self):
        """Pack the nearest item if within range"""
        nearest_item = None
        nearest_distance = float('inf')
        
        for item in self.items:
            if not item['packed']:
                dx = abs(self.player_x - item['x'])
                dy = abs(self.player_y - item['y'])
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= self.interaction_range and distance < nearest_distance:
                    nearest_distance = distance
                    nearest_item = item
                    
        if nearest_item:
            # Check weight limit
            if self.total_weight + nearest_item['weight'] <= self.max_weight:
                # Pack it
                nearest_item['packed'] = True
                self.items_packed.append(nearest_item)
                self.total_weight += nearest_item['weight']
                
                # Visual effect
                self.pack_effects.append({
                    'x': nearest_item['x'],
                    'y': nearest_item['y'],
                    'life': 30,
                    'text': nearest_item['name']
                })
                
                # Reduce stress for essential items
                if nearest_item['essential']:
                    self.stress_level = max(0, self.stress_level - 5)
            else:
                # Too heavy
                self.pack_effects.append({
                    'x': self.player_x,
                    'y': self.player_y,
                    'life': 30,
                    'text': 'Too heavy!'
                })
                
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update time
        self.time_remaining -= dt
        
        # Time pressure effects
        if self.time_remaining < 30:
            self.clock_flash = (self.clock_flash + 1) % 30
            self.stress_level = min(100, self.stress_level + dt * 2)
            
        if self.time_remaining <= 0:
            self.end_game()
            
        # Update hover states
        for item in self.items:
            if not item['packed']:
                dx = abs(self.player_x - item['x'])
                dy = abs(self.player_y - item['y'])
                distance = math.sqrt(dx*dx + dy*dy)
                item['hover'] = distance <= self.interaction_range
                
        # Update effects
        for effect in self.pack_effects[:]:
            effect['life'] -= 1
            if effect['life'] <= 0:
                self.pack_effects.remove(effect)
                
        # Update stress particles
        if self.stress_level > 70 and random.random() < 0.1:
            self.stress_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, 100),
                'vy': random.uniform(0.5, 2),
                'life': 60
            })
            
        for particle in self.stress_particles[:]:
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.stress_particles.remove(particle)
                
    def end_game(self):
        """End the packing game"""
        self.active = False
        self.completed = True
        
    def get_results(self):
        """Return game results"""
        # Calculate score based on items packed
        essential_packed = sum(1 for item in self.items_packed if item['essential'])
        total_essentials = sum(1 for item in self.items if item['essential'])
        total_value = sum(item['value'] for item in self.items_packed)
        
        if essential_packed < total_essentials:
            message = f"Forgot essential items! Only packed {essential_packed}/{total_essentials} essentials."
            success = False
        elif len(self.items_packed) < 5:
            message = "Barely grabbed anything. Starting over with almost nothing."
            success = False
        elif total_value > 600:
            message = "Packed wisely. Ready for the next chapter."
            success = True
        else:
            message = f"Packed {len(self.items_packed)} items. It'll have to do."
            success = len(self.items_packed) > 8
            
        return {
            'stress': -20 if success else 20,
            'preparedness': total_value / 10,  # Convert to percentage
            'message': message,
            'color': (100, 255, 100) if success else (255, 100, 100)
        }
        
    def draw(self, screen):
        """Draw the packing game"""
        if not self.active:
            return
            
        # Clear background
        screen.fill((20, 20, 30))
        
        # Draw room
        self.draw_room(screen)
        
        # Draw items
        for item in self.items:
            if not item['packed']:
                self.draw_item(screen, item)
                
        # Draw player
        self.draw_player(screen)
        
        # Draw pack effects
        for effect in self.pack_effects:
            self.draw_effect(screen, effect)
            
        # Draw stress particles
        for particle in self.stress_particles:
            alpha = int(255 * particle['life'] / 60)
            pygame.draw.circle(screen, (255, 100, 100, alpha),
                             (int(particle['x']), int(particle['y'])), 3)
                             
        # Draw UI
        self.draw_ui(screen)
        
    def draw_room(self, screen):
        """Draw room tiles"""
        for y in range(self.room_height):
            for x in range(self.room_width):
                pixel_x = self.room_x + x * TILE_SIZE
                pixel_y = self.room_y + y * TILE_SIZE
                
                tile = self.room_tiles[y][x]
                
                if tile == 0:  # Floor
                    color = (80, 70, 60)
                    pygame.draw.rect(screen, color, 
                                   (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))
                    # Add subtle grid
                    pygame.draw.rect(screen, (70, 60, 50),
                                   (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE), 1)
                elif tile == 1:  # Wall
                    color = (40, 35, 30)
                    pygame.draw.rect(screen, color,
                                   (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))
                elif tile == 2:  # Furniture
                    color = (60, 50, 40)
                    pygame.draw.rect(screen, color,
                                   (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, (50, 40, 30),
                                   (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE), 2)
                                   
    def draw_item(self, screen, item):
        """Draw a packable item"""
        pixel_x = self.room_x + item['x'] * TILE_SIZE
        pixel_y = self.room_y + item['y'] * TILE_SIZE
        
        # Draw item
        center_x = pixel_x + TILE_SIZE // 2
        center_y = pixel_y + TILE_SIZE // 2
        
        # Glow if hoverable
        if item['hover']:
            glow_radius = TILE_SIZE // 2 + 5 + int(math.sin(pygame.time.get_ticks() * 0.005) * 3)
            for i in range(3):
                alpha = 50 - i * 15
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*item['color'], alpha), 
                                 (glow_radius, glow_radius), glow_radius - i * 2)
                screen.blit(glow_surf, (center_x - glow_radius, center_y - glow_radius))
                
        # Draw item icon
        pygame.draw.rect(screen, item['color'],
                        (pixel_x + 8, pixel_y + 8, TILE_SIZE - 16, TILE_SIZE - 16))
        pygame.draw.rect(screen, tuple(c // 2 for c in item['color']),
                        (pixel_x + 8, pixel_y + 8, TILE_SIZE - 16, TILE_SIZE - 16), 2)
                        
        # Essential indicator
        if item['essential']:
            pygame.draw.circle(screen, (255, 255, 100), 
                             (pixel_x + TILE_SIZE - 10, pixel_y + 10), 4)
                             
    def draw_player(self, screen):
        """Draw the player character"""
        pixel_x = self.room_x + self.player_x * TILE_SIZE
        pixel_y = self.room_y + self.player_y * TILE_SIZE
        
        # Simple character
        center_x = pixel_x + TILE_SIZE // 2
        center_y = pixel_y + TILE_SIZE // 2
        
        # Body
        pygame.draw.circle(screen, (100, 150, 255), (center_x, center_y), TILE_SIZE // 3)
        
        # Direction indicator
        if self.player_facing == "up":
            pygame.draw.circle(screen, (255, 255, 255),
                             (center_x, center_y - TILE_SIZE // 4), 3)
        elif self.player_facing == "down":
            pygame.draw.circle(screen, (255, 255, 255),
                             (center_x, center_y + TILE_SIZE // 4), 3)
        elif self.player_facing == "left":
            pygame.draw.circle(screen, (255, 255, 255),
                             (center_x - TILE_SIZE // 4, center_y), 3)
        elif self.player_facing == "right":
            pygame.draw.circle(screen, (255, 255, 255),
                             (center_x + TILE_SIZE // 4, center_y), 3)
                             
    def draw_effect(self, screen, effect):
        """Draw pack effect"""
        pixel_x = self.room_x + effect['x'] * TILE_SIZE + TILE_SIZE // 2
        pixel_y = self.room_y + effect['y'] * TILE_SIZE - effect['life']
        
        alpha = int(255 * effect['life'] / 30)
        text_surf = self.small_font.render(effect['text'], True, (255, 255, 255))
        text_surf.set_alpha(alpha)
        
        text_rect = text_surf.get_rect(center=(pixel_x, pixel_y))
        screen.blit(text_surf, text_rect)
        
    def draw_ui(self, screen):
        """Draw UI elements"""
        # Timer (prominent)
        time_color = (255, 100, 100) if self.time_remaining < 30 else (255, 200, 100) if self.time_remaining < 60 else (255, 255, 255)
        
        if self.time_remaining < 30 and self.clock_flash < 15:
            time_color = (255, 255, 255)
            
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        time_text = f"{minutes}:{seconds:02d}"
        
        time_surf = self.timer_font.render(time_text, True, time_color)
        time_rect = time_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        
        # Timer background
        pygame.draw.rect(screen, (40, 40, 50), time_rect.inflate(40, 20))
        pygame.draw.rect(screen, time_color, time_rect.inflate(40, 20), 3)
        screen.blit(time_surf, time_rect)
        
        # Weight indicator
        weight_rect = pygame.Rect(50, 50, 200, 60)
        pygame.draw.rect(screen, (40, 40, 50), weight_rect)
        pygame.draw.rect(screen, (200, 200, 210), weight_rect, 2)
        
        weight_text = f"Weight: {self.total_weight:.1f}/{self.max_weight} lbs"
        weight_color = (255, 100, 100) if self.total_weight > self.max_weight * 0.8 else (255, 200, 100) if self.total_weight > self.max_weight * 0.5 else (100, 255, 100)
        weight_surf = self.font.render(weight_text, True, weight_color)
        screen.blit(weight_surf, (weight_rect.x + 10, weight_rect.y + 10))
        
        # Progress bar
        bar_rect = pygame.Rect(weight_rect.x + 10, weight_rect.y + 35, weight_rect.width - 20, 15)
        pygame.draw.rect(screen, (60, 60, 70), bar_rect)
        fill_width = int(bar_rect.width * (self.total_weight / self.max_weight))
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, min(fill_width, bar_rect.width), bar_rect.height)
        pygame.draw.rect(screen, weight_color, fill_rect)
        pygame.draw.rect(screen, (150, 150, 160), bar_rect, 1)
        
        # Items packed
        items_rect = pygame.Rect(SCREEN_WIDTH - 250, 50, 200, 60)
        pygame.draw.rect(screen, (40, 40, 50), items_rect)
        pygame.draw.rect(screen, (200, 200, 210), items_rect, 2)
        
        items_text = f"Packed: {len(self.items_packed)}/{len(self.items)}"
        items_surf = self.font.render(items_text, True, (200, 200, 255))
        screen.blit(items_surf, (items_rect.x + 10, items_rect.y + 10))
        
        # Essential items indicator
        essential_packed = sum(1 for item in self.items_packed if item['essential'])
        total_essentials = sum(1 for item in self.items if item['essential'])
        essential_text = f"Essentials: {essential_packed}/{total_essentials}"
        essential_color = (100, 255, 100) if essential_packed == total_essentials else (255, 200, 100) if essential_packed > 0 else (255, 100, 100)
        essential_surf = self.font.render(essential_text, True, essential_color)
        screen.blit(essential_surf, (items_rect.x + 10, items_rect.y + 35))
        
        # Instructions
        inst_rect = pygame.Rect(50, SCREEN_HEIGHT - 80, SCREEN_WIDTH - 100, 60)
        pygame.draw.rect(screen, (30, 30, 40), inst_rect)
        pygame.draw.rect(screen, (100, 100, 120), inst_rect, 2)
        
        instructions = [
            "WASD/Arrow Keys: Move around the room",
            "E/SPACE: Pack nearby items (yellow = essential!)"
        ]
        
        inst_y = inst_rect.y + 10
        for inst in instructions:
            inst_surf = self.font.render(inst, True, (200, 200, 220))
            inst_rect_text = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect_text)
            inst_y += 25
            
        # Stress indicator (visual)
        if self.stress_level > 50:
            stress_alpha = int((self.stress_level - 50) * 2.5)
            stress_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            stress_surf.set_alpha(stress_alpha)
            stress_surf.fill((255, 50, 50))
            screen.blit(stress_surf, (0, 0))
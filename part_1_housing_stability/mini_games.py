"""Mini-games for Part 1 - Money earning activities"""

import pygame
import random
import math
from shared.constants import *

class BurgerFlippingGame:
    """Fast-paced burger flipping mini-game"""
    
    def __init__(self):
        self.active = False
        self.score = 0
        self.time_remaining = 60  # 60 second shifts
        self.perfect_flips = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)
        
        # Burger grid (4x2 grill)
        self.grill_slots = []
        self.grill_cols = 4
        self.grill_rows = 2
        
        for row in range(self.grill_rows):
            for col in range(self.grill_cols):
                x = 200 + col * 120
                y = 200 + row * 120
                self.grill_slots.append({
                    'pos': (x, y),
                    'burger': None,
                    'slot_index': row * self.grill_cols + col
                })
        
        # Orders queue
        self.orders = []
        self.completed_orders = 0
        self.failed_orders = 0
        
        # Visual effects
        self.smoke_particles = []
        self.score_popups = []
        
    def start(self):
        """Start the mini-game"""
        self.active = True
        self.score = 0
        self.time_remaining = 60
        self.perfect_flips = 0
        self.completed_orders = 0
        self.failed_orders = 0
        
        # Clear grill
        for slot in self.grill_slots:
            slot['burger'] = None
            
        # Start with some orders
        for _ in range(3):
            self.add_random_order()
            
    def add_random_order(self):
        """Add a new customer order"""
        cook_levels = ['rare', 'medium', 'well']
        self.orders.append({
            'cook_level': random.choice(cook_levels),
            'time_limit': 30,
            'time_elapsed': 0
        })
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.end_game()
            return
            
        # Update burgers on grill
        for slot in self.grill_slots:
            if slot['burger']:
                burger = slot['burger']
                
                # Cook the burger
                if not burger['flipped']:
                    burger['bottom_cook'] += dt
                else:
                    burger['top_cook'] += dt
                    
                # Check if burning
                total_cook = burger['bottom_cook'] + burger['top_cook']
                if total_cook > 20:
                    # Burnt!
                    self.create_smoke(slot['pos'])
                    slot['burger'] = None
                    self.score -= 10
                    self.add_score_popup(slot['pos'], "-10", (255, 100, 100))
                    
        # Update orders
        for order in self.orders[:]:
            order['time_elapsed'] += dt
            if order['time_elapsed'] > order['time_limit']:
                # Order expired
                self.orders.remove(order)
                self.failed_orders += 1
                self.score -= 5
                
        # Add new orders periodically
        if random.random() < dt * 0.3 and len(self.orders) < 5:
            self.add_random_order()
            
        # Update visual effects
        self.update_particles(dt)
        self.update_score_popups(dt)
        
    def update_particles(self, dt):
        """Update smoke particles"""
        for particle in self.smoke_particles[:]:
            particle['life'] -= dt
            particle['y'] -= dt * 50
            particle['x'] += particle['vx'] * dt
            if particle['life'] <= 0:
                self.smoke_particles.remove(particle)
                
    def update_score_popups(self, dt):
        """Update score popup animations"""
        for popup in self.score_popups[:]:
            popup['life'] -= dt
            popup['y'] -= dt * 30
            if popup['life'] <= 0:
                self.score_popups.remove(popup)
                
    def create_smoke(self, pos):
        """Create smoke effect"""
        for _ in range(10):
            self.smoke_particles.append({
                'x': pos[0] + random.randint(-20, 20),
                'y': pos[1],
                'vx': random.randint(-20, 20),
                'life': 1.0,
                'size': random.randint(5, 15)
            })
            
    def add_score_popup(self, pos, text, color):
        """Add a score popup"""
        self.score_popups.append({
            'x': pos[0],
            'y': pos[1],
            'text': text,
            'color': color,
            'life': 1.0
        })
        
    def handle_click(self, pos):
        """Handle mouse click"""
        if not self.active:
            return
            
        # Check which slot was clicked
        for slot in self.grill_slots:
            slot_rect = pygame.Rect(slot['pos'][0] - 50, slot['pos'][1] - 50, 100, 100)
            if slot_rect.collidepoint(pos):
                self.handle_slot_click(slot)
                return
                
    def handle_slot_click(self, slot):
        """Handle clicking on a grill slot"""
        if slot['burger'] is None:
            # Place new burger
            slot['burger'] = {
                'bottom_cook': 0,
                'top_cook': 0,
                'flipped': False
            }
        else:
            burger = slot['burger']
            if not burger['flipped'] and burger['bottom_cook'] >= 3:
                # Flip burger
                burger['flipped'] = True
            elif burger['flipped'] and burger['top_cook'] >= 3:
                # Serve burger
                self.serve_burger(slot, burger)
                
    def serve_burger(self, slot, burger):
        """Serve a completed burger"""
        total_cook = burger['bottom_cook'] + burger['top_cook']
        
        # Determine cook level
        if total_cook < 8:
            cook_level = 'rare'
        elif total_cook < 14:
            cook_level = 'medium'
        else:
            cook_level = 'well'
            
        # Check against orders
        order_filled = False
        for order in self.orders[:]:
            if order['cook_level'] == cook_level:
                # Perfect order!
                self.orders.remove(order)
                self.completed_orders += 1
                
                # Calculate score based on time
                time_bonus = max(0, 30 - order['time_elapsed'])
                score = 20 + int(time_bonus)
                self.score += score
                
                self.add_score_popup(slot['pos'], f"+{score}", (100, 255, 100))
                order_filled = True
                
                # Check for perfect flip
                if abs(burger['bottom_cook'] - burger['top_cook']) < 0.5:
                    self.perfect_flips += 1
                    self.score += 5
                    self.add_score_popup((slot['pos'][0], slot['pos'][1] - 20), 
                                       "Perfect!", (255, 255, 100))
                break
                
        if not order_filled:
            # No matching order
            self.score += 5  # Still get some points
            self.add_score_popup(slot['pos'], "+5", (200, 200, 100))
            
        # Clear slot
        slot['burger'] = None
        
    def end_game(self):
        """End the mini-game and calculate earnings"""
        self.active = False
        
        # Calculate final score
        efficiency_bonus = self.completed_orders * 5
        perfection_bonus = self.perfect_flips * 10
        self.final_score = self.score + efficiency_bonus + perfection_bonus
        
        # Convert to money (1 point = $0.50)
        self.money_earned = max(20, min(80, self.final_score * 0.5))
        
    def draw(self, screen):
        """Draw the mini-game"""
        if not self.active:
            return
            
        # Background
        screen.fill((40, 30, 20))
        
        # Title
        title_text = "BURGER RUSH - Flip burgers to fill orders!"
        title_surf = self.font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 30))
        
        # Timer and score
        timer_text = f"Time: {int(self.time_remaining)}s"
        timer_color = (255, 100, 100) if self.time_remaining < 10 else (255, 255, 255)
        timer_surf = self.font.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (50, 60))
        
        score_text = f"Score: {self.score}"
        score_surf = self.font.render(score_text, True, (100, 255, 100))
        screen.blit(score_surf, (SCREEN_WIDTH - 150, 60))
        
        # Draw orders
        order_y = 100
        order_surf = self.font.render("ORDERS:", True, (255, 200, 100))
        screen.blit(order_surf, (50, order_y))
        
        for i, order in enumerate(self.orders):
            y = order_y + 30 + i * 25
            
            # Order text
            order_text = f"{order['cook_level'].upper()}"
            time_left = order['time_limit'] - order['time_elapsed']
            color = (255, 100, 100) if time_left < 10 else (255, 255, 255)
            
            order_surf = self.small_font.render(order_text, True, color)
            screen.blit(order_surf, (50, y))
            
            # Timer bar
            bar_width = 100
            bar_height = 15
            bar_x = 150
            
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, y, bar_width, bar_height))
            fill_width = int(bar_width * (time_left / order['time_limit']))
            if fill_width > 0:
                pygame.draw.rect(screen, color, (bar_x, y, fill_width, bar_height))
                
        # Draw grill
        for slot in self.grill_slots:
            x, y = slot['pos']
            
            # Grill slot
            slot_rect = pygame.Rect(x - 50, y - 50, 100, 100)
            pygame.draw.rect(screen, (80, 80, 80), slot_rect, border_radius=10)
            pygame.draw.rect(screen, (120, 120, 120), slot_rect, width=2, border_radius=10)
            
            # Grill lines
            for i in range(5):
                line_y = y - 40 + i * 20
                pygame.draw.line(screen, (60, 60, 60), (x - 40, line_y), (x + 40, line_y), 2)
            
            if slot['burger']:
                burger = slot['burger']
                
                # Draw burger
                burger_color = self.get_burger_color(burger)
                
                # Bottom bun
                pygame.draw.ellipse(screen, (200, 150, 100), (x - 35, y + 20, 70, 20))
                
                # Patty
                pygame.draw.ellipse(screen, burger_color, (x - 40, y - 5, 80, 25))
                
                if burger['flipped']:
                    # Show grill marks on top
                    for i in range(3):
                        mark_x = x - 25 + i * 25
                        pygame.draw.line(screen, (60, 40, 20), (mark_x, y - 5), 
                                       (mark_x + 10, y + 10), 2)
                else:
                    # Show cook level indicator
                    cook_percent = burger['bottom_cook'] / 10
                    indicator_width = int(60 * cook_percent)
                    pygame.draw.rect(screen, (255, 200, 100), 
                                   (x - 30, y - 25, indicator_width, 5))
                    
                # Top bun (if ready to serve)
                if burger['flipped'] and burger['top_cook'] >= 3:
                    pygame.draw.ellipse(screen, (200, 150, 100), (x - 35, y - 25, 70, 25))
                    # Sesame seeds
                    for _ in range(5):
                        seed_x = x + random.randint(-25, 25)
                        seed_y = y + random.randint(-20, -10)
                        pygame.draw.circle(screen, (255, 240, 200), (seed_x, seed_y), 2)
                        
        # Draw smoke particles
        for particle in self.smoke_particles:
            alpha = int(255 * particle['life'])
            size = int(particle['size'] * particle['life'])
            pygame.draw.circle(screen, (100, 100, 100), 
                             (int(particle['x']), int(particle['y'])), size)
            
        # Draw score popups
        for popup in self.score_popups:
            alpha = int(255 * popup['life'])
            popup_surf = self.font.render(popup['text'], True, popup['color'])
            popup_surf.set_alpha(alpha)
            screen.blit(popup_surf, (int(popup['x'] - popup_surf.get_width() // 2), 
                                   int(popup['y'])))
            
        # Instructions
        inst_text = "Click to place burger • Click again to flip • Click when done to serve"
        inst_surf = self.small_font.render(inst_text, True, (180, 180, 180))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst_surf, inst_rect)
        
    def get_burger_color(self, burger):
        """Get burger color based on cook level"""
        total_cook = burger['bottom_cook'] + burger['top_cook']
        
        if total_cook < 6:
            # Raw to rare
            return (200, 100, 100)
        elif total_cook < 10:
            # Medium
            return (150, 75, 50)
        elif total_cook < 15:
            # Well done
            return (100, 50, 25)
        else:
            # Burnt
            return (50, 25, 10)


class DeliveryRaceGame:
    """Delivery mini-game - navigate through city to deliver food"""
    
    def __init__(self):
        self.active = False
        self.score = 0
        self.time_remaining = 45
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
        # Player bike
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT - 150
        self.player_speed = 300
        
        # Delivery targets
        self.deliveries = []
        self.completed_deliveries = 0
        
        # Obstacles (cars, pedestrians)
        self.obstacles = []
        
        # Road lanes
        self.lanes = [200, 300, 400, 500, 600]
        self.current_lane = 2
        
        # Visual effects
        self.road_offset = 0
        self.tip_popups = []
        
    def start(self):
        """Start the delivery game"""
        self.active = True
        self.score = 0
        self.time_remaining = 45
        self.completed_deliveries = 0
        self.current_lane = 2
        self.player_x = self.lanes[self.current_lane]
        
        # Create initial deliveries
        self.create_delivery()
        
        # Clear obstacles
        self.obstacles = []
        
    def create_delivery(self):
        """Create a new delivery target"""
        lane = random.randint(0, len(self.lanes) - 1)
        self.deliveries.append({
            'x': self.lanes[lane],
            'y': -50,
            'lane': lane,
            'tip_amount': random.randint(2, 8)
        })
        
    def create_obstacle(self):
        """Create a new obstacle"""
        lane = random.randint(0, len(self.lanes) - 1)
        obstacle_type = random.choice(['car', 'pedestrian'])
        
        self.obstacles.append({
            'x': self.lanes[lane],
            'y': -50,
            'type': obstacle_type,
            'speed': random.randint(50, 150) if obstacle_type == 'car' else 30
        })
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.end_game()
            return
            
        # Update road animation
        self.road_offset += 400 * dt
        if self.road_offset > 50:
            self.road_offset -= 50
            
        # Move deliveries
        for delivery in self.deliveries[:]:
            delivery['y'] += 200 * dt
            
            # Check if player collected delivery
            if abs(delivery['x'] - self.player_x) < 50 and \
               abs(delivery['y'] - self.player_y) < 50:
                # Collected!
                self.completed_deliveries += 1
                self.score += delivery['tip_amount']
                self.add_tip_popup(delivery['x'], delivery['y'], 
                                  f"+${delivery['tip_amount']}")
                self.deliveries.remove(delivery)
                
            # Remove if off screen
            elif delivery['y'] > SCREEN_HEIGHT:
                self.deliveries.remove(delivery)
                self.score -= 2  # Penalty for missed delivery
                
        # Move obstacles
        for obstacle in self.obstacles[:]:
            obstacle['y'] += obstacle['speed'] * dt
            
            # Check collision
            if abs(obstacle['x'] - self.player_x) < 40 and \
               abs(obstacle['y'] - self.player_y) < 40:
                # Hit obstacle!
                self.score -= 5
                self.time_remaining -= 5
                self.add_tip_popup(self.player_x, self.player_y, "-$5", 
                                  (255, 100, 100))
                self.obstacles.remove(obstacle)
                
            # Remove if off screen
            elif obstacle['y'] > SCREEN_HEIGHT:
                self.obstacles.remove(obstacle)
                
        # Create new deliveries and obstacles
        if random.random() < dt * 0.5:
            self.create_delivery()
        if random.random() < dt * 1.5:
            self.create_obstacle()
            
        # Update visual effects
        for popup in self.tip_popups[:]:
            popup['life'] -= dt
            popup['y'] -= 50 * dt
            if popup['life'] <= 0:
                self.tip_popups.remove(popup)
                
    def add_tip_popup(self, x, y, text, color=(100, 255, 100)):
        """Add a tip notification popup"""
        self.tip_popups.append({
            'x': x,
            'y': y,
            'text': text,
            'color': color,
            'life': 1.0
        })
        
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_LEFT and self.current_lane > 0:
            self.current_lane -= 1
            self.player_x = self.lanes[self.current_lane]
        elif key == pygame.K_RIGHT and self.current_lane < len(self.lanes) - 1:
            self.current_lane += 1
            self.player_x = self.lanes[self.current_lane]
            
    def end_game(self):
        """End the game and calculate earnings"""
        self.active = False
        
        # Base pay plus tips
        base_pay = 10
        self.money_earned = base_pay + self.score
        
    def draw(self, screen):
        """Draw the delivery game"""
        if not self.active:
            return
            
        # Background
        screen.fill((40, 40, 50))
        
        # Draw road
        road_left = 150
        road_right = 650
        pygame.draw.rect(screen, (60, 60, 70), (road_left, 0, road_right - road_left, SCREEN_HEIGHT))
        
        # Draw lane lines
        for lane in self.lanes[1:-1]:
            for y in range(int(-self.road_offset), SCREEN_HEIGHT, 50):
                pygame.draw.rect(screen, (255, 255, 255), (lane - 2, y, 4, 30))
                
        # Draw deliveries
        for delivery in self.deliveries:
            # Delivery icon (pizza box)
            pygame.draw.rect(screen, (200, 50, 50), 
                           (delivery['x'] - 20, delivery['y'] - 20, 40, 40),
                           border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255),
                           (delivery['x'] - 20, delivery['y'] - 20, 40, 40),
                           width=2, border_radius=5)
            
            # Dollar sign
            dollar_surf = self.font.render("$", True, (255, 255, 255))
            dollar_rect = dollar_surf.get_rect(center=(delivery['x'], delivery['y']))
            screen.blit(dollar_surf, dollar_rect)
            
        # Draw obstacles
        for obstacle in self.obstacles:
            if obstacle['type'] == 'car':
                # Simple car shape
                pygame.draw.rect(screen, (100, 100, 120),
                               (obstacle['x'] - 25, obstacle['y'] - 40, 50, 80),
                               border_radius=10)
                # Windows
                pygame.draw.rect(screen, (150, 150, 200),
                               (obstacle['x'] - 20, obstacle['y'] - 30, 40, 25))
            else:
                # Pedestrian
                pygame.draw.circle(screen, (255, 200, 150),
                                 (obstacle['x'], obstacle['y'] - 20), 10)
                pygame.draw.rect(screen, (100, 100, 200),
                               (obstacle['x'] - 10, obstacle['y'] - 10, 20, 30))
                
        # Draw player (delivery bike)
        # Bike body
        pygame.draw.rect(screen, (50, 150, 255),
                       (self.player_x - 15, self.player_y - 20, 30, 40),
                       border_radius=5)
        # Wheels
        pygame.draw.circle(screen, (50, 50, 50), 
                         (self.player_x - 10, self.player_y + 15), 8)
        pygame.draw.circle(screen, (50, 50, 50),
                         (self.player_x + 10, self.player_y + 15), 8)
        # Delivery bag
        pygame.draw.rect(screen, (255, 150, 50),
                       (self.player_x - 10, self.player_y - 30, 20, 20),
                       border_radius=3)
        
        # Draw tip popups
        for popup in self.tip_popups:
            alpha = int(255 * popup['life'])
            popup_surf = self.font.render(popup['text'], True, popup['color'])
            popup_surf.set_alpha(alpha)
            screen.blit(popup_surf, (int(popup['x'] - popup_surf.get_width() // 2),
                                   int(popup['y'])))
            
        # UI elements
        # Timer
        timer_text = f"Time: {int(self.time_remaining)}s"
        timer_color = (255, 100, 100) if self.time_remaining < 10 else (255, 255, 255)
        timer_surf = self.font.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (50, 30))
        
        # Score
        score_text = f"Tips: ${self.score}"
        score_surf = self.font.render(score_text, True, (100, 255, 100))
        screen.blit(score_surf, (SCREEN_WIDTH - 150, 30))
        
        # Deliveries completed
        delivery_text = f"Deliveries: {self.completed_deliveries}"
        delivery_surf = self.font.render(delivery_text, True, (255, 255, 255))
        screen.blit(delivery_surf, (SCREEN_WIDTH // 2 - 60, 30))
        
        # Instructions
        inst_text = "← → Move lanes • Collect deliveries • Avoid obstacles"
        inst_surf = pygame.font.Font(None, 18).render(inst_text, True, (180, 180, 180))
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst_surf, inst_rect)


class PlasmaTimingGame:
    """Plasma donation mini-game - timing and patience based"""
    
    def __init__(self):
        self.active = False
        self.score = 0
        self.donation_progress = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
        # Game mechanics
        self.needle_stability = 50  # 0-100, affects donation speed
        self.comfort_level = 80     # 0-100, affects score
        self.hydration = 70         # 0-100, affects success
        
        # Timing elements
        self.squeeze_timer = 0
        self.squeeze_interval = 3  # Squeeze every 3 seconds
        
        # Visual elements
        self.arm_shake = 0
        self.blood_flow_particles = []
        
    def start(self):
        """Start the plasma donation game"""
        self.active = True
        self.score = 0
        self.donation_progress = 0
        self.needle_stability = 50
        self.comfort_level = 80
        self.hydration = 70
        
    def update(self, dt):
        """Update game state"""
        if not self.active:
            return
            
        # Update donation progress
        if self.needle_stability > 30:
            progress_rate = (self.needle_stability / 100) * (self.hydration / 100)
            self.donation_progress += progress_rate * dt * 2
            
        # Check completion
        if self.donation_progress >= 100:
            self.end_game()
            return
            
        # Decrease comfort and hydration over time
        self.comfort_level = max(0, self.comfort_level - dt * 5)
        self.hydration = max(0, self.hydration - dt * 3)
        
        # Needle becomes unstable if comfort is low
        if self.comfort_level < 40:
            self.needle_stability = max(0, self.needle_stability - dt * 10)
            
        # Update squeeze timer
        self.squeeze_timer += dt
        
        # Arm shake based on stability
        self.arm_shake = (100 - self.needle_stability) / 100 * 5
        
        # Update blood flow particles
        if self.needle_stability > 30:
            if random.random() < dt * 5:
                self.blood_flow_particles.append({
                    'x': SCREEN_WIDTH // 2,
                    'y': 300,
                    'life': 1.0
                })
                
        for particle in self.blood_flow_particles[:]:
            particle['life'] -= dt
            particle['x'] += 50 * dt
            if particle['life'] <= 0:
                self.blood_flow_particles.remove(particle)
                
    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return
            
        if key == pygame.K_SPACE:
            # Squeeze ball to maintain blood flow
            if self.squeeze_timer >= self.squeeze_interval - 0.5:
                # Good timing!
                self.needle_stability = min(100, self.needle_stability + 10)
                self.score += 5
                self.squeeze_timer = 0
            else:
                # Too early
                self.needle_stability = max(0, self.needle_stability - 5)
                
        elif key == pygame.K_r:
            # Relax to increase comfort
            self.comfort_level = min(100, self.comfort_level + 15)
            self.needle_stability = max(0, self.needle_stability - 5)
            
        elif key == pygame.K_d:
            # Drink water (if available)
            if self.hydration < 50:
                self.hydration = min(100, self.hydration + 20)
                self.score += 2
                
    def end_game(self):
        """End the game and calculate payment"""
        self.active = False
        
        # Base payment with bonuses for good performance
        base_payment = 35
        comfort_bonus = int(self.comfort_level / 10)
        stability_bonus = int(self.needle_stability / 10)
        
        self.money_earned = base_payment + comfort_bonus + stability_bonus
        
    def draw(self, screen):
        """Draw the plasma donation game"""
        if not self.active:
            return
            
        # Background
        screen.fill((220, 220, 230))
        
        # Title
        title_text = "PLASMA DONATION - Stay calm and squeeze on time!"
        title_surf = self.font.render(title_text, True, (50, 50, 50))
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 30))
        
        # Draw donation chair and arm
        chair_x = SCREEN_WIDTH // 2 - 100
        chair_y = 250
        
        # Chair
        pygame.draw.rect(screen, (100, 100, 120), 
                       (chair_x - 50, chair_y, 300, 200),
                       border_radius=10)
        
        # Arm with shake effect
        arm_x = chair_x + 50 + random.randint(-int(self.arm_shake), int(self.arm_shake))
        arm_y = chair_y + 50
        
        # Arm shape
        pygame.draw.ellipse(screen, (255, 220, 200),
                          (arm_x, arm_y, 150, 60))
        
        # Needle and tube
        needle_x = arm_x + 75
        needle_y = arm_y + 30
        pygame.draw.circle(screen, (150, 150, 150), (needle_x, needle_y), 5)
        
        # Draw tube to machine
        tube_points = [
            (needle_x, needle_y),
            (needle_x + 50, needle_y + 20),
            (SCREEN_WIDTH // 2 + 150, 300)
        ]
        pygame.draw.lines(screen, (200, 50, 50), False, tube_points, 3)
        
        # Plasma collection machine
        machine_x = SCREEN_WIDTH // 2 + 120
        machine_y = 250
        pygame.draw.rect(screen, (200, 200, 210),
                       (machine_x, machine_y, 100, 150),
                       border_radius=5)
        
        # Collection bag
        bag_fill = int(self.donation_progress)
        pygame.draw.rect(screen, (255, 255, 200),
                       (machine_x + 20, machine_y + 100 - bag_fill, 60, bag_fill))
        pygame.draw.rect(screen, (100, 100, 100),
                       (machine_x + 20, machine_y + 20, 60, 80), 
                       width=2)
        
        # Draw blood flow particles
        for particle in self.blood_flow_particles:
            alpha = int(255 * particle['life'])
            pygame.draw.circle(screen, (255, 100, 100),
                             (int(particle['x']), int(particle['y'])), 3)
            
        # Draw status bars
        self.draw_status_bar(screen, "Needle Stability", self.needle_stability, 
                           (100, 255, 100), (50, 100))
        self.draw_status_bar(screen, "Comfort Level", self.comfort_level,
                           (100, 200, 255), (50, 140))
        self.draw_status_bar(screen, "Hydration", self.hydration,
                           (50, 150, 255), (50, 180))
        
        # Squeeze indicator
        squeeze_ready = self.squeeze_timer >= self.squeeze_interval - 0.5
        squeeze_color = (100, 255, 100) if squeeze_ready else (255, 255, 100)
        
        squeeze_text = "SQUEEZE NOW!" if squeeze_ready else f"Wait {int(self.squeeze_interval - self.squeeze_timer)}s"
        squeeze_surf = self.font.render(squeeze_text, True, squeeze_color)
        squeeze_rect = squeeze_surf.get_rect(center=(SCREEN_WIDTH // 2, 450))
        
        if squeeze_ready:
            # Pulsing effect
            scale = 1 + math.sin(self.squeeze_timer * 10) * 0.1
            scaled_surf = pygame.transform.scale(squeeze_surf, 
                                               (int(squeeze_surf.get_width() * scale),
                                                int(squeeze_surf.get_height() * scale)))
            scaled_rect = scaled_surf.get_rect(center=squeeze_rect.center)
            screen.blit(scaled_surf, scaled_rect)
        else:
            screen.blit(squeeze_surf, squeeze_rect)
            
        # Progress
        progress_text = f"Progress: {int(self.donation_progress)}%"
        progress_surf = self.font.render(progress_text, True, (50, 50, 50))
        screen.blit(progress_surf, (SCREEN_WIDTH // 2 - 50, 500))
        
        # Instructions
        inst_lines = [
            "SPACE - Squeeze when ready",
            "R - Relax (increases comfort)",
            "D - Drink water (when low)"
        ]
        
        y = 550
        for line in inst_lines:
            inst_surf = pygame.font.Font(None, 18).render(line, True, (100, 100, 100))
            screen.blit(inst_surf, (50, y))
            y += 20
            
    def draw_status_bar(self, screen, label, value, color, pos):
        """Draw a status bar"""
        # Label
        label_surf = pygame.font.Font(None, 18).render(label, True, (50, 50, 50))
        screen.blit(label_surf, pos)
        
        # Bar
        bar_width = 200
        bar_height = 20
        bar_x = pos[0] + 120
        bar_y = pos[1]
        
        pygame.draw.rect(screen, (200, 200, 200), 
                       (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * value / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, color,
                           (bar_x, bar_y, fill_width, bar_height))
            
        # Value text
        value_text = f"{int(value)}%"
        value_surf = pygame.font.Font(None, 16).render(value_text, True, (50, 50, 50))
        value_rect = value_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + 10))
        screen.blit(value_surf, value_rect)
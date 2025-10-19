import pygame
import math

class LevelSelection:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # UI Colors - Pixel art palette
        self.colors = {
            'background': (20, 15, 30),  # Dark purple background
            'panel_bg': (35, 30, 50),
            'panel_highlight': (55, 50, 75),
            'panel_shadow': (15, 10, 25),
            'text_white': (255, 255, 255),
            'text_cream': (255, 240, 220),
            'text_gray': (200, 200, 210),
            'text_dim': (130, 130, 140),
            # Pixel art inspired accent colors
            'accent_1': (255, 115, 105),  # Coral red
            'accent_2': (255, 195, 80),   # Golden yellow
            'accent_3': (120, 230, 170),  # Mint green
            'accent_4': (120, 170, 255),  # Sky blue
            'accent_5': (200, 120, 255),  # Purple
            'accent_6': (255, 170, 120),  # Peach
            'accent_7': (100, 200, 220),  # Cyan
            'accent_8': (255, 120, 150),  # Pink
            'glow': (255, 255, 255, 30),
            'locked': (60, 60, 70),
            'scroll_track': (30, 25, 45),
            'scroll_thumb': (80, 75, 100)
        }
        
        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.level_title_font = pygame.font.Font(None, 32)
        self.subtitle_font = pygame.font.Font(None, 22)
        self.desc_font = pygame.font.Font(None, 18)
        self.tiny_font = pygame.font.Font(None, 16)
        
        # Level card properties - vertical rectangles
        self.card_width = 320
        self.card_height = 100
        self.card_spacing = 20
        self.card_margin_x = (screen_width - 320) // 2  # Center the cards
        
        # Animation states
        self.hover_card = None
        self.selected_card = None
        self.animation_time = 0
        self.card_animations = {}
        self.particles = []
        
        # Create level data
        self.create_levels()
        
        # Scroll position
        self.scroll_y = 0
        self.target_scroll_y = 0
        self.max_scroll = 0
        self.scroll_velocity = 0
        
    def create_levels(self):
        """Create level/part information"""
        self.levels = [
            {
                'part': 1,
                'title': 'HOUSING & STABILITY',
                'subtitle': 'Aging Out at 18',
                'description': 'No home after foster care ends',
                'color': self.colors['accent_1'],
                'icon': '🏠',
                'unlocked': True,
                'completed': False,
                'progress': 0.0  # Non-linear progression
            },
            {
                'part': 2,
                'title': 'HOUSING CRISIS',
                'subtitle': 'No Place Like Home',
                'description': 'Navigate housing instability',
                'color': self.colors['accent_2'],
                'icon': '🏠',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            },
            {
                'part': 3,
                'title': 'HEALTHCARE MAZE',
                'subtitle': 'Sick Without Coverage',
                'description': 'When you can\'t afford to be ill',
                'color': self.colors['accent_3'],
                'icon': '💊',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            },
            {
                'part': 4,
                'title': 'DEBT SPIRAL',
                'subtitle': 'The Payday Trap',
                'description': 'How $100 becomes $1000',
                'color': self.colors['accent_4'],
                'icon': '💳',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            },
            {
                'part': 5,
                'title': 'EDUCATION BARRIERS',
                'subtitle': 'The GED Dream',
                'description': 'Education costs more than money',
                'color': self.colors['accent_5'],
                'icon': '📚',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            },
            {
                'part': 6,
                'title': 'TOTAL ISOLATION',
                'subtitle': 'Alone in the City',
                'description': 'When support systems fail',
                'color': self.colors['accent_6'],
                'icon': '😔',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            },
            {
                'part': 7,
                'title': 'LEGAL SYSTEM',
                'subtitle': 'The $2.50 Crime',
                'description': 'One fare, lifetime consequences',
                'color': self.colors['accent_7'],
                'icon': '⚖️',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            },
            {
                'part': 8,
                'title': 'FINANCIAL COLLAPSE',
                'subtitle': 'The Final Straw',
                'description': 'When all systems fail at once',
                'color': self.colors['accent_8'],
                'icon': '💸',
                'unlocked': True,
                'completed': False,
                'progress': 0.0
            }
        ]
        
        # Position cards vertically with nice spacing
        start_y = 160
        
        for i, level in enumerate(self.levels):
            level['rect'] = pygame.Rect(
                self.card_margin_x,
                start_y + i * (self.card_height + self.card_spacing),
                self.card_width,
                self.card_height
            )
            
            # Initialize animations
            self.card_animations[i] = {
                'offset_x': 0,
                'target_offset_x': 0,
                'glow_alpha': 0,
                'shake_x': 0,
                'hover_progress': 0,
                'select_bounce': 0
            }
        
        # Calculate max scroll
        total_height = start_y + len(self.levels) * (self.card_height + self.card_spacing) + 100
        self.max_scroll = max(0, total_height - self.screen_height)
        # Debug removed - scrolling confirmed working
    
    def create_particle(self, x, y, color):
        """Create a decorative particle"""
        self.particles.append({
            'x': x,
            'y': y,
            'vx': (pygame.time.get_ticks() % 10 - 5) / 5,
            'vy': -2,
            'life': 1.0,
            'color': color,
            'size': 3
        })
    
    def handle_event(self, event):
        """Handle input events"""
        # Handle mousewheel event for modern pygame (this is the primary method)
        if hasattr(pygame, 'MOUSEWHEEL') and event.type == pygame.MOUSEWHEEL:
            scroll_amount = event.y * 80  # Negative because y is inverted
            self.target_scroll_y = max(0, min(self.max_scroll, 
                                             self.target_scroll_y - scroll_amount))
            return None  # Don't process button 4/5 if we handled MOUSEWHEEL
            
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            adjusted_mouse_y = mouse_y + self.scroll_y
            old_hover = self.hover_card
            self.hover_card = None
            
            for i, level in enumerate(self.levels):
                # Expand hit area when hovering
                hit_rect = level['rect'].copy()
                hit_rect.x = self.card_margin_x + self.card_animations[i]['offset_x']
                hit_rect.y -= self.scroll_y
                hit_rect.width += 50  # Extend hit area to the right
                
                if hit_rect.collidepoint(mouse_x, mouse_y):
                    self.hover_card = i
                    if old_hover != i:
                        # Create particles on hover
                        for _ in range(3):
                            self.create_particle(
                                hit_rect.right - 10,
                                hit_rect.centery,
                                level['color']
                            )
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, level in enumerate(self.levels):
                    hit_rect = level['rect'].copy()
                    hit_rect.x = self.card_margin_x + self.card_animations[i]['offset_x']
                    hit_rect.y -= self.scroll_y
                    hit_rect.width += 50
                    
                    if hit_rect.collidepoint(mouse_x, mouse_y) and level['unlocked']:
                        self.selected_card = i
                        self.card_animations[i]['select_bounce'] = 1.0
                        # Create celebration particles
                        for _ in range(10):
                            self.create_particle(
                                hit_rect.centerx,
                                hit_rect.centery,
                                level['color']
                            )
                        return f"part_{level['part']}"
                        
            # Only handle button 4/5 if we don't have MOUSEWHEEL support
            elif not hasattr(pygame, 'MOUSEWHEEL'):
                if event.button == 4:  # Scroll up (fallback)
                    self.target_scroll_y = max(0, self.target_scroll_y - 80)
                elif event.button == 5:  # Scroll down (fallback)
                    self.target_scroll_y = min(self.max_scroll, self.target_scroll_y + 80)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.target_scroll_y = max(0, self.target_scroll_y - 50)
                self.scroll_velocity = -300
            elif event.key == pygame.K_DOWN:
                self.target_scroll_y = min(self.max_scroll, self.target_scroll_y + 50)
                self.scroll_velocity = 300
            elif event.key == pygame.K_HOME:
                self.target_scroll_y = 0
            elif event.key == pygame.K_END:
                self.target_scroll_y = self.max_scroll
        
        return None
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
        
        # Smooth scrolling with velocity
        if self.scroll_velocity != 0:
            self.target_scroll_y += self.scroll_velocity * dt
            self.target_scroll_y = max(0, min(self.max_scroll, self.target_scroll_y))
            self.scroll_velocity *= 0.9  # Damping
            if abs(self.scroll_velocity) < 1:
                self.scroll_velocity = 0
        
        # Interpolate scroll position with faster response
        if self.scroll_y != self.target_scroll_y:
            diff = self.target_scroll_y - self.scroll_y
            self.scroll_y += diff * dt * 15
            if abs(diff) < 0.5:
                self.scroll_y = self.target_scroll_y
        
        # Update card animations
        for i, anim in self.card_animations.items():
            # Hover slide effect
            if self.hover_card == i:
                anim['target_offset_x'] = 40
                anim['hover_progress'] = min(1.0, anim['hover_progress'] + dt * 8)
                anim['glow_alpha'] = min(80, anim['glow_alpha'] + dt * 400)
                # Small shake animation
                anim['shake_x'] = math.sin(self.animation_time * 20) * 2
            else:
                anim['target_offset_x'] = 0
                anim['hover_progress'] = max(0, anim['hover_progress'] - dt * 8)
                anim['glow_alpha'] = max(0, anim['glow_alpha'] - dt * 200)
                anim['shake_x'] = 0
            
            # Smooth slide animation
            offset_diff = anim['target_offset_x'] - anim['offset_x']
            anim['offset_x'] += offset_diff * dt * 15
            
            # Selection bounce
            if anim['select_bounce'] > 0:
                anim['select_bounce'] = max(0, anim['select_bounce'] - dt * 3)
        
        # Update particles
        new_particles = []
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= dt * 2
            if particle['life'] > 0:
                new_particles.append(particle)
        self.particles = new_particles
    
    def draw_card(self, screen, level, index, y_offset):
        """Draw a single level card with pixel art style"""
        anim = self.card_animations[index]
        
        # Calculate card position
        card_x = self.card_margin_x + anim['offset_x'] + anim['shake_x']
        card_y = level['rect'].y - y_offset
        
        # Apply selection bounce
        if anim['select_bounce'] > 0:
            bounce_scale = 1 + anim['select_bounce'] * 0.1
            card_x -= (bounce_scale - 1) * self.card_width / 2
            card_y -= (bounce_scale - 1) * self.card_height / 2
        
        # Skip if card is off screen
        if card_y > self.screen_height or card_y + self.card_height < 0:
            return
        
        # Create card rectangle
        card_rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
        
        # Draw glow effect when hovering
        if anim['glow_alpha'] > 0:
            glow_surf = pygame.Surface((self.card_width + 40, self.card_height + 40), pygame.SRCALPHA)
            glow_color = (*level['color'], int(anim['glow_alpha']))
            for i in range(3):
                size = 20 - i * 6
                pygame.draw.rect(glow_surf, (*level['color'], int(anim['glow_alpha'] / (i + 1))), 
                               (size, size, self.card_width + 40 - size * 2, self.card_height + 40 - size * 2),
                               border_radius=12)
            screen.blit(glow_surf, (card_x - 20, card_y - 20))
        
        # Draw shadow
        shadow_offset = 4 + anim['hover_progress'] * 4
        shadow_rect = card_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, self.colors['panel_shadow'], shadow_rect, border_radius=8)
        
        # Draw main card background
        bg_color = self.colors['panel_bg'] if level['unlocked'] else self.colors['locked']
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)
        
        # Draw decorative border
        border_width = 3
        border_rect = card_rect.inflate(-border_width, -border_width)
        border_color = level['color'] if level['unlocked'] else self.colors['text_dim']
        pygame.draw.rect(screen, border_color, card_rect, width=border_width, border_radius=8)
        
        # Draw progress bar background
        progress_height = 6
        progress_rect = pygame.Rect(
            card_rect.x + 15,
            card_rect.bottom - progress_height - 10,
            card_rect.width - 30,
            progress_height
        )
        pygame.draw.rect(screen, self.colors['panel_shadow'], progress_rect, border_radius=3)
        
        # Draw progress fill
        if level['progress'] > 0:
            fill_width = int((progress_rect.width - 2) * level['progress'])
            fill_rect = pygame.Rect(
                progress_rect.x + 1,
                progress_rect.y + 1,
                fill_width,
                progress_height - 2
            )
            pygame.draw.rect(screen, level['color'], fill_rect, border_radius=2)
        
        # Draw part number in stylized box
        part_box_size = 45
        part_box_rect = pygame.Rect(
            card_rect.x + 15,
            card_rect.centery - part_box_size // 2,
            part_box_size,
            part_box_size
        )
        
        # Part number background with gradient effect
        pygame.draw.rect(screen, level['color'], part_box_rect, border_radius=8)
        inner_rect = part_box_rect.inflate(-6, -6)
        pygame.draw.rect(screen, self.colors['panel_bg'], inner_rect, border_radius=6)
        
        # Part number text
        part_text = self.level_title_font.render(str(level['part']), True, level['color'])
        part_text_rect = part_text.get_rect(center=part_box_rect.center)
        screen.blit(part_text, part_text_rect)
        
        # Title with slight offset when hovering
        title_x = card_rect.x + 75 + anim['hover_progress'] * 5
        title_y = card_rect.y + 20
        
        title_surf = self.subtitle_font.render(level['title'], True, self.colors['text_cream'])
        screen.blit(title_surf, (title_x, title_y))
        
        # Subtitle
        subtitle_surf = self.tiny_font.render(level['subtitle'], True, level['color'])
        screen.blit(subtitle_surf, (title_x, title_y + 22))
        
        # Description
        desc_color = self.colors['text_gray'] if level['unlocked'] else self.colors['text_dim']
        desc_surf = self.desc_font.render(level['description'], True, desc_color)
        screen.blit(desc_surf, (title_x, title_y + 40))
        
        # Draw hover indicator arrow with animation
        if self.hover_card == index and anim['hover_progress'] > 0.3:
            arrow_x = card_rect.right - 25 + math.sin(self.animation_time * 4) * 3
            arrow_y = card_rect.centery
            arrow_size = 10
            
            # Draw arrow with fade effect
            arrow_alpha = int(anim['hover_progress'] * 255)
            arrow_surf = pygame.Surface((arrow_size * 2, arrow_size * 2), pygame.SRCALPHA)
            arrow_points = [
                (0, 0),
                (arrow_size, arrow_size),
                (0, arrow_size * 2)
            ]
            pygame.draw.polygon(arrow_surf, (*level['color'], arrow_alpha), arrow_points)
            screen.blit(arrow_surf, (arrow_x - arrow_size, arrow_y - arrow_size))
        
        # Lock overlay
        if not level['unlocked']:
            lock_text = self.subtitle_font.render("LOCKED", True, self.colors['text_dim'])
            lock_rect = lock_text.get_rect(center=card_rect.center)
            screen.blit(lock_text, lock_rect)
    
    def draw_background_pattern(self, screen):
        """Draw a subtle background pattern"""
        # Draw gradient background
        for y in range(self.screen_height):
            progress = y / self.screen_height
            color = (
                int(20 + progress * 10),
                int(15 + progress * 10),
                int(30 + progress * 15)
            )
            pygame.draw.line(screen, color, (0, y), (self.screen_width, y))
        
        # Draw subtle dots pattern
        dot_spacing = 50
        for y in range(0, self.screen_height, dot_spacing):
            for x in range(0, self.screen_width, dot_spacing):
                if (x // dot_spacing + y // dot_spacing) % 2 == 0:
                    pygame.draw.circle(screen, (30, 25, 45), (x + dot_spacing//2, y + dot_spacing//2), 2)
    
    def draw(self, screen):
        """Draw the level selection screen"""
        # Background
        screen.fill(self.colors['background'])
        self.draw_background_pattern(screen)
        
        # Title with better positioning
        title_y = 60
        title_shadow = self.title_font.render("CHAPTER SELECT", True, (10, 5, 20))
        screen.blit(title_shadow, (self.screen_width // 2 - title_shadow.get_width() // 2 + 2, title_y + 2))
        
        title_text = self.title_font.render("CHAPTER SELECT", True, self.colors['text_cream'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, title_y))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = "Choose your struggle"
        subtitle_surf = self.subtitle_font.render(subtitle_text, True, self.colors['text_gray'])
        subtitle_rect = subtitle_surf.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw decorative lines
        line_y = 130
        pygame.draw.line(screen, self.colors['panel_highlight'], 
                        (50, line_y), (self.screen_width - 50, line_y), 2)
        
        # Draw cards
        for i, level in enumerate(self.levels):
            self.draw_card(screen, level, i, self.scroll_y)
        
        # Draw particles
        for particle in self.particles:
            alpha = int(particle['life'] * 255)
            color = (*particle['color'], alpha)
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             int(particle['size'] * particle['life']))
        
        # Draw scrollbar
        if self.max_scroll > 0:
            scrollbar_width = 10
            scrollbar_x = self.screen_width - 30
            scrollbar_track_height = self.screen_height - 240
            scrollbar_y = 140
            
            # Track
            track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_track_height)
            pygame.draw.rect(screen, self.colors['scroll_track'], track_rect, border_radius=5)
            
            # Thumb
            thumb_height = max(40, scrollbar_track_height * (self.screen_height / (self.max_scroll + self.screen_height)))
            scroll_progress = self.scroll_y / self.max_scroll if self.max_scroll > 0 else 0
            thumb_y = scrollbar_y + scroll_progress * (scrollbar_track_height - thumb_height)
            
            thumb_rect = pygame.Rect(scrollbar_x + 1, thumb_y, scrollbar_width - 2, thumb_height)
            # Add glow to scrollbar when hovering near it
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if abs(mouse_x - scrollbar_x - scrollbar_width//2) < 50:
                pygame.draw.rect(screen, self.colors['accent_4'], thumb_rect, border_radius=4)
            else:
                pygame.draw.rect(screen, self.colors['scroll_thumb'], thumb_rect, border_radius=4)
        
        # Navigation hints with background
        nav_font = self.desc_font
        nav_y = self.screen_height - 40
        
        # Draw hint background
        hint_bg = pygame.Surface((self.screen_width, 60), pygame.SRCALPHA)
        pygame.draw.rect(hint_bg, (10, 10, 20, 180), hint_bg.get_rect())
        screen.blit(hint_bg, (0, self.screen_height - 60))
        
        esc_text = "ESC - Back to Menu"
        esc_surf = nav_font.render(esc_text, True, self.colors['text_dim'])
        screen.blit(esc_surf, (30, nav_y))
        
        scroll_text = "↑↓ or Mouse Wheel - Scroll"
        scroll_surf = nav_font.render(scroll_text, True, self.colors['text_dim'])
        scroll_rect = scroll_surf.get_rect(right=self.screen_width - 30, y=nav_y)
        screen.blit(scroll_surf, scroll_rect)
        
        # Debug info - remove this later
        if self.max_scroll > 0:
            debug_text = f"Scroll: {int(self.scroll_y)}/{int(self.max_scroll)}"
            debug_surf = self.tiny_font.render(debug_text, True, (255, 255, 100))
            screen.blit(debug_surf, (self.screen_width // 2 - 50, nav_y))
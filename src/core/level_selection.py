import pygame
import math

class LevelSelection:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # UI Colors matching game style
        self.colors = {
            'background': (50, 50, 50),
            'panel_bg': (25, 25, 30),
            'panel_border': (70, 70, 80),
            'text_white': (255, 255, 255),
            'text_gray': (220, 220, 220),
            'text_dim': (150, 150, 150),
            'accent_blue': (120, 170, 255),
            'accent_orange': (255, 170, 120),
            'accent_green': (120, 255, 170),
            'accent_red': (255, 120, 120),
            'accent_purple': (200, 120, 255),
            'accent_yellow': (255, 220, 120),
            'button_hover': (80, 80, 90),
            'button_pressed': (100, 100, 110),
            'shadow': (10, 10, 15, 128),
            'locked': (80, 80, 80)
        }
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 24)
        self.desc_font = pygame.font.Font(None, 20)
        
        # Level card properties
        self.card_width = 180
        self.card_height = 240
        self.card_spacing = 20
        
        # State
        self.hover_card = None
        self.animation_time = 0
        self.card_animations = {}
        
        # Create level data
        self.create_levels()
        
        # Scroll position
        self.scroll_y = 0
        self.target_scroll_y = 0
        self.max_scroll = 0
        
    def create_levels(self):
        """Create level/part information"""
        self.levels = [
            {
                'part': 1,
                'title': 'Employment Rights',
                'subtitle': 'School to Work',
                'description': 'Learn about workplace rights and navigate your first job',
                'color': self.colors['accent_blue'],
                'unlocked': True,
                'tasks': 68  # Original Part 1 objectives
            },
            {
                'part': 2,
                'title': 'Housing Crisis',
                'subtitle': 'Finding Shelter',
                'description': 'Deal with housing instability and transitional living',
                'color': self.colors['accent_orange'],
                'unlocked': True,
                'tasks': 55  # Original Part 2 objectives
            },
            {
                'part': 3,
                'title': 'Financial Stress',
                'subtitle': '10 Days to Homelessness',
                'description': 'Watch how a $5 overdraft spirals into complete disaster',
                'color': self.colors['accent_red'],
                'unlocked': True,
                'tasks': 68  # Enhanced with detailed 10-day journey
            },
            {
                'part': 4,
                'title': 'Credit & Debt',
                'subtitle': 'Modern Debtor\'s Prison',
                'description': 'Experience how predatory lending traps the poor permanently',
                'color': self.colors['accent_purple'],
                'unlocked': True,
                'tasks': 80  # Enhanced with 8-month debt spiral
            },
            {
                'part': 5,
                'title': 'Healthcare Crisis',
                'subtitle': 'The Tooth That Destroyed Everything',
                'description': 'One untreated cavity leads to job loss, addiction risk, and debt',
                'color': self.colors['accent_green'],
                'unlocked': True,
                'tasks': 65  # Enhanced with 6-month healthcare nightmare
            },
            {
                'part': 6,
                'title': 'Education Barriers',
                'subtitle': 'The GED Trap',
                'description': 'Try to escape poverty through education but face every obstacle',
                'color': self.colors['accent_yellow'],
                'unlocked': True,
                'tasks': 62  # Enhanced with detailed education struggles
            },
            {
                'part': 7,
                'title': 'Total Isolation',
                'subtitle': 'Death by Loneliness',
                'description': 'Experience complete social isolation and its mental health impact',
                'color': self.colors['accent_blue'],
                'unlocked': True,
                'tasks': 71  # Enhanced with 6-month isolation journey
            },
            {
                'part': 8,
                'title': 'Legal Entrapment',
                'subtitle': 'The $2.50 Crime',
                'description': 'A single fare jump leads to permanent criminal record',
                'color': self.colors['accent_red'],
                'unlocked': True,
                'tasks': 75  # Enhanced with complete legal system trap
            }
        ]
        
        # Calculate positions in a grid
        cols = 3
        rows = math.ceil(len(self.levels) / cols)
        
        # Calculate total height needed
        panel_height = rows * (self.card_height + self.card_spacing) + 200
        self.max_scroll = max(0, panel_height - self.screen_height)
        
        # Position cards
        start_x = (self.screen_width - (cols * self.card_width + (cols - 1) * self.card_spacing)) // 2
        start_y = 150
        
        for i, level in enumerate(self.levels):
            row = i // cols
            col = i % cols
            
            level['rect'] = pygame.Rect(
                start_x + col * (self.card_width + self.card_spacing),
                start_y + row * (self.card_height + self.card_spacing),
                self.card_width,
                self.card_height
            )
            
            # Initialize animations
            self.card_animations[i] = {
                'scale': 1.0,
                'rotation': 0,
                'float_y': 0
            }
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            adjusted_mouse_y = mouse_pos[1] + self.scroll_y
            self.hover_card = None
            
            for i, level in enumerate(self.levels):
                adjusted_rect = level['rect'].copy()
                adjusted_rect.y -= self.scroll_y
                if adjusted_rect.collidepoint(mouse_pos):
                    self.hover_card = i
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, level in enumerate(self.levels):
                    adjusted_rect = level['rect'].copy()
                    adjusted_rect.y -= self.scroll_y
                    if adjusted_rect.collidepoint(mouse_pos) and level['unlocked']:
                        return f"part_{level['part']}"
            elif event.button == 4:  # Scroll up
                self.target_scroll_y = max(0, self.target_scroll_y - 40)
            elif event.button == 5:  # Scroll down
                self.target_scroll_y = min(self.max_scroll, self.target_scroll_y + 40)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.target_scroll_y = max(0, self.target_scroll_y - 40)
            elif event.key == pygame.K_DOWN:
                self.target_scroll_y = min(self.max_scroll, self.target_scroll_y + 40)
        
        return None
    
    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
        
        # Smooth scrolling
        if self.scroll_y != self.target_scroll_y:
            diff = self.target_scroll_y - self.scroll_y
            self.scroll_y += diff * dt * 10
            if abs(diff) < 1:
                self.scroll_y = self.target_scroll_y
        
        # Update card animations
        for i, anim in self.card_animations.items():
            # Hover effects
            if self.hover_card == i:
                anim['scale'] = min(1.05, anim['scale'] + dt * 8)
                anim['rotation'] = math.sin(self.animation_time * 3) * 2
            else:
                anim['scale'] = max(1.0, anim['scale'] - dt * 8)
                anim['rotation'] *= 0.95
            
            # Floating animation
            anim['float_y'] = math.sin(self.animation_time * 2 + i * 0.5) * 3
    
    def draw_card(self, screen, level, index, y_offset):
        """Draw a single level card"""
        anim = self.card_animations[index]
        card_rect = level['rect'].copy()
        card_rect.y -= y_offset
        
        # Skip if card is off screen
        if card_rect.bottom < 0 or card_rect.top > self.screen_height:
            return
        
        # Apply floating animation
        card_rect.y += anim['float_y']
        
        # Card shadow
        shadow_surf = pygame.Surface((card_rect.width + 20, card_rect.height + 20), pygame.SRCALPHA)
        shadow_color = (*self.colors['shadow'][:3], 80)
        pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=15)
        screen.blit(shadow_surf, (card_rect.x - 10, card_rect.y + 5))
        
        # Card background
        if level['unlocked']:
            bg_color = self.colors['panel_bg']
            border_color = level['color']
        else:
            bg_color = self.colors['locked']
            border_color = self.colors['panel_border']
        
        # Scale effect for hover
        if anim['scale'] != 1.0:
            scaled_rect = card_rect.inflate(
                (anim['scale'] - 1) * card_rect.width,
                (anim['scale'] - 1) * card_rect.height
            )
            pygame.draw.rect(screen, border_color, scaled_rect, border_radius=10)
            pygame.draw.rect(screen, bg_color, scaled_rect.inflate(-4, -4), border_radius=8)
            card_rect = scaled_rect
        else:
            pygame.draw.rect(screen, border_color, card_rect, border_radius=10)
            pygame.draw.rect(screen, bg_color, card_rect.inflate(-4, -4), border_radius=8)
        
        # Part number circle
        circle_radius = 25
        circle_center = (card_rect.centerx, card_rect.y + 40)
        pygame.draw.circle(screen, level['color'], circle_center, circle_radius)
        pygame.draw.circle(screen, self.colors['text_white'], circle_center, circle_radius - 3)
        pygame.draw.circle(screen, level['color'], circle_center, circle_radius - 5)
        
        # Part number
        part_text = self.subtitle_font.render(str(level['part']), True, self.colors['text_white'])
        part_rect = part_text.get_rect(center=circle_center)
        screen.blit(part_text, part_rect)
        
        # Title
        title_text = self.button_font.render(level['title'], True, level['color'])
        title_rect = title_text.get_rect(centerx=card_rect.centerx, y=card_rect.y + 80)
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.desc_font.render(level['subtitle'], True, self.colors['text_gray'])
        subtitle_rect = subtitle_text.get_rect(centerx=card_rect.centerx, y=card_rect.y + 105)
        screen.blit(subtitle_text, subtitle_rect)
        
        # Description (wrapped)
        desc_lines = self.wrap_text(level['description'], self.desc_font, card_rect.width - 20)
        y = card_rect.y + 130
        for line in desc_lines:
            line_surf = self.desc_font.render(line, True, self.colors['text_dim'])
            line_rect = line_surf.get_rect(centerx=card_rect.centerx, y=y)
            screen.blit(line_surf, line_rect)
            y += 20
        
        # Task count
        tasks_text = self.desc_font.render(f"{level['tasks']} tasks", True, self.colors['text_dim'])
        tasks_rect = tasks_text.get_rect(centerx=card_rect.centerx, bottom=card_rect.bottom - 15)
        screen.blit(tasks_text, tasks_rect)
        
        # Lock overlay if locked
        if not level['unlocked']:
            lock_surf = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            lock_surf.fill((0, 0, 0, 150))
            screen.blit(lock_surf, card_rect.topleft)
            
            lock_text = self.button_font.render("LOCKED", True, self.colors['text_dim'])
            lock_rect = lock_text.get_rect(center=card_rect.center)
            screen.blit(lock_text, lock_rect)
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw(self, screen):
        """Draw the level selection screen"""
        # Background
        screen.fill(self.colors['background'])
        
        # Title
        title_text = "Select Chapter"
        title_surf = self.title_font.render(title_text, True, self.colors['text_white'])
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Choose your economic challenge"
        subtitle_surf = self.subtitle_font.render(subtitle_text, True, self.colors['text_gray'])
        subtitle_rect = subtitle_surf.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw cards
        for i, level in enumerate(self.levels):
            self.draw_card(screen, level, i, self.scroll_y)
        
        # Scroll indicator if needed
        if self.max_scroll > 0:
            # Scrollbar background
            scrollbar_x = self.screen_width - 20
            scrollbar_y = 150
            scrollbar_height = self.screen_height - 200
            pygame.draw.rect(screen, self.colors['panel_border'], 
                           (scrollbar_x, scrollbar_y, 10, scrollbar_height), border_radius=5)
            
            # Scrollbar thumb
            thumb_height = max(30, scrollbar_height * (self.screen_height / (self.max_scroll + self.screen_height)))
            thumb_y = scrollbar_y + (self.scroll_y / self.max_scroll) * (scrollbar_height - thumb_height)
            pygame.draw.rect(screen, self.colors['accent_blue'], 
                           (scrollbar_x + 2, thumb_y, 6, thumb_height), border_radius=3)
        
        # Back instruction
        back_text = "Press ESC to return to menu"
        back_surf = self.desc_font.render(back_text, True, self.colors['text_dim'])
        back_rect = back_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        screen.blit(back_surf, back_rect)
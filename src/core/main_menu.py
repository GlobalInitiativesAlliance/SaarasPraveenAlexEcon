import pygame
import math

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clock = pygame.time.Clock()
        
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
            'button_hover': (80, 80, 90),
            'button_pressed': (100, 100, 110),
            'shadow': (10, 10, 15, 128)
        }
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 32)
        self.credit_font = pygame.font.Font(None, 20)
        
        # Button properties
        self.button_width = 280
        self.button_height = 50
        self.button_spacing = 15
        
        # Menu state
        self.selected_button = None
        self.hover_button = None
        self.transition_alpha = 255
        self.transitioning = False
        self.game_starting = False
        
        # Animation variables
        self.animation_time = 0
        self.title_y_offset = 0
        self.button_animations = {}
        
        # Create buttons
        self.create_buttons()
        
        # Background particles for visual effect
        self.particles = []
        self.create_particles()
        
        # Logo/icon position for future use
        self.logo_rotation = 0
        
        # Debug mode for alignment
        self.debug_mode = False
        
    def create_buttons(self):
        """Create menu buttons with proper positioning"""
        # Calculate button positions to be centered in panel
        panel_height = 500
        panel_y = (self.screen_height - panel_height) // 2
        
        # Reserve space for title/subtitle and bottom text
        title_space = 140
        bottom_space = 60
        
        # Calculate available space for buttons - now 5 buttons
        available_height = panel_height - title_space - bottom_space
        total_buttons_height = 5 * self.button_height + 4 * self.button_spacing
        
        # Center buttons vertically in available space
        buttons_start_y = panel_y + title_space + (available_height - total_buttons_height) // 2
        
        center_x = self.screen_width // 2
        
        self.buttons = [
            {
                'text': 'Start Game',
                'rect': pygame.Rect(center_x - self.button_width // 2, buttons_start_y, 
                                   self.button_width, self.button_height),
                'action': 'start',
                'color': self.colors['accent_blue']
            },
            {
                'text': 'Levels',
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                   buttons_start_y + self.button_height + self.button_spacing, 
                                   self.button_width, self.button_height),
                'action': 'levels',
                'color': self.colors['accent_orange']
            },
            {
                'text': 'How to Play',
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                   buttons_start_y + 2 * (self.button_height + self.button_spacing), 
                                   self.button_width, self.button_height),
                'action': 'help',
                'color': self.colors['accent_orange']
            },
            {
                'text': 'Credits',
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                   buttons_start_y + 3 * (self.button_height + self.button_spacing), 
                                   self.button_width, self.button_height),
                'action': 'credits',
                'color': self.colors['text_gray']
            },
            {
                'text': 'Quit',
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                   buttons_start_y + 4 * (self.button_height + self.button_spacing), 
                                   self.button_width, self.button_height),
                'action': 'quit',
                'color': self.colors['text_dim']
            }
        ]
        
        # Initialize button animations
        for i, button in enumerate(self.buttons):
            self.button_animations[i] = {
                'scale': 1.0,
                'offset_x': 0,
                'alpha': 0
            }
    
    def create_particles(self):
        """Create background particles for visual effect"""
        import random
        for _ in range(30):  # Reduced particle count for better performance
            self.particles.append({
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5),
                'alpha': random.randint(50, 150)
            })
    
    def update_particles(self, dt):
        """Update particle positions"""
        for particle in self.particles:
            particle['y'] -= particle['speed']
            if particle['y'] < -10:
                particle['y'] = self.screen_height + 10
                particle['x'] = pygame.time.get_ticks() % self.screen_width
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        
    def draw_rounded_rect_with_border(self, surface, bg_color, border_color, rect, radius, border_width=2):
        """Draw a rounded rectangle with border"""
        # Draw border
        border_rect = rect.inflate(border_width * 2, border_width * 2)
        pygame.draw.rect(surface, border_color, border_rect, border_radius=radius)
        # Draw background
        pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
        
        # Add subtle gradient overlay
        gradient_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height // 2):
            alpha = int(20 * (1 - y / (rect.height // 2)))
            pygame.draw.line(gradient_surf, (255, 255, 255, alpha), (0, y), (rect.width, y))
        surface.blit(gradient_surf, rect.topleft)
    
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hover_button = None
            for i, button in enumerate(self.buttons):
                if button['rect'].collidepoint(mouse_pos):
                    self.hover_button = i
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.buttons):
                    if button['rect'].collidepoint(mouse_pos):
                        self.selected_button = button['action']
                        if button['action'] == 'start':
                            self.game_starting = True
                            self.transitioning = True
                        return button['action']
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Start game with Enter or Space
                self.selected_button = 'start'
                self.game_starting = True
                self.transitioning = True
                return 'start'
                
        return None
    
    def update(self, dt):
        """Update menu animations"""
        self.animation_time += dt
        
        # Update title animation
        self.title_y_offset = math.sin(self.animation_time * 2) * 5
        self.logo_rotation = self.animation_time * 30  # Slow rotation
        
        # Update particles
        self.update_particles(dt)
        
        # Update button animations
        for i in range(len(self.buttons)):
            anim = self.button_animations[i]
            
            # Fade in animation
            if anim['alpha'] < 255:
                anim['alpha'] = min(255, anim['alpha'] + dt * 500)
            
            # Hover animation
            if self.hover_button == i:
                anim['scale'] = min(1.05, anim['scale'] + dt * 10)
                anim['offset_x'] = min(10, anim['offset_x'] + dt * 100)
            else:
                anim['scale'] = max(1.0, anim['scale'] - dt * 10)
                anim['offset_x'] = max(0, anim['offset_x'] - dt * 100)
        
        # Handle transition out
        if self.transitioning:
            self.transition_alpha = max(0, self.transition_alpha - dt * 500)
            if self.transition_alpha == 0 and self.game_starting:
                return 'start_game'
        
        return None
    
    def draw(self, screen):
        """Draw the main menu"""
        # Clear screen
        screen.fill(self.colors['background'])
        
        # Draw particles
        for particle in self.particles:
            alpha = min(particle['alpha'], self.transition_alpha)
            color = (*self.colors['text_dim'], alpha)
            pygame.draw.circle(screen, color[:3], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        # Draw main panel
        panel_width = 700
        panel_height = 500
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Panel shadow
        shadow_surf = pygame.Surface((panel_width + 30, panel_height + 30), pygame.SRCALPHA)
        shadow_color = (*self.colors['shadow'][:3], int(80 * self.transition_alpha / 255))
        pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=25)
        screen.blit(shadow_surf, (panel_x - 15, panel_y - 10))
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_rounded_rect_with_border(screen, self.colors['panel_bg'], 
                                         self.colors['panel_border'], 
                                         panel_rect, 20)
        
        # Draw title with animation and glow effect
        title_text = "Economics Adventure"
        
        # Create glow effect
        glow_surf = pygame.Surface((800, 100), pygame.SRCALPHA)
        for i in range(3):
            glow_alpha = int(30 * self.transition_alpha / 255)
            glow_color = (*self.colors['accent_blue'], glow_alpha)
            glow_title = self.title_font.render(title_text, True, glow_color)
            glow_rect = glow_title.get_rect(center=(400, 50))
            glow_rect.x += i - 1
            glow_rect.y += i - 1
            glow_surf.blit(glow_title, glow_rect)
        
        glow_pos = ((self.screen_width - 800) // 2, panel_y + 20 + self.title_y_offset)
        screen.blit(glow_surf, glow_pos)
        
        # Draw main title
        title_surface = self.title_font.render(title_text, True, self.colors['text_white'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 
                                                   panel_y + 70 + self.title_y_offset))
        title_surface.set_alpha(self.transition_alpha)
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_text = "Learn Economics Through City Life"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.colors['text_gray'])
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_width // 2, 
                                                        panel_y + 115))
        subtitle_surface.set_alpha(int(self.transition_alpha * 0.8))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons
        for i, button in enumerate(self.buttons):
            anim = self.button_animations[i]
            
            # Calculate animated position
            button_rect = button['rect'].copy()
            button_rect.x += anim['offset_x']
            
            # Button shadow
            if self.hover_button == i:
                shadow_surf = pygame.Surface((button_rect.width + 10, button_rect.height + 10), pygame.SRCALPHA)
                shadow_color = (*self.colors['shadow'][:3], int(60 * self.transition_alpha / 255))
                pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=8)
                screen.blit(shadow_surf, (button_rect.x - 5, button_rect.y + 3))
            
            # Button background
            if self.hover_button == i:
                bg_color = self.colors['button_hover']
            else:
                bg_color = self.colors['panel_bg']
            
            # Draw button with scale animation
            if anim['scale'] != 1.0:
                scaled_rect = button_rect.inflate(
                    (anim['scale'] - 1) * button_rect.width,
                    (anim['scale'] - 1) * button_rect.height
                )
                self.draw_rounded_rect_with_border(screen, bg_color, 
                                                 button['color'], 
                                                 scaled_rect, 8)
                button_rect = scaled_rect
            else:
                self.draw_rounded_rect_with_border(screen, bg_color, 
                                                 button['color'], 
                                                 button_rect, 8)
            
            # Button text
            text_surface = self.button_font.render(button['text'], True, button['color'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            text_surface.set_alpha(int(anim['alpha'] * self.transition_alpha / 255))
            screen.blit(text_surface, text_rect)
        
        # Draw help text in the panel
        if not self.transitioning:
            help_text = "Press ENTER to start"
            help_surface = self.credit_font.render(help_text, True, self.colors['text_dim'])
            help_rect = help_surface.get_rect(center=(self.screen_width // 2, 
                                                     panel_y + panel_height - 40))
            # Pulsing effect
            pulse_alpha = int((math.sin(self.animation_time * 3) + 1) * 0.5 * 150 + 105)
            help_surface.set_alpha(min(pulse_alpha, self.transition_alpha))
            screen.blit(help_surface, help_rect)
        
        # Draw credits at bottom
        credits_text = "Created for Economics Education"
        credits_surface = self.credit_font.render(credits_text, True, self.colors['text_dim'])
        credits_rect = credits_surface.get_rect(center=(self.screen_width // 2, 
                                                       self.screen_height - 30))
        credits_surface.set_alpha(int(self.transition_alpha * 0.6))
        screen.blit(credits_surface, credits_rect)
        
        # Debug mode - show panel boundaries
        if self.debug_mode:
            pygame.draw.rect(screen, (255, 0, 0), panel_rect, 2)
            # Show button container area
            button_area = pygame.Rect(panel_x + 50, panel_y + 140, 
                                    panel_width - 100, panel_height - 200)
            pygame.draw.rect(screen, (0, 255, 0), button_area, 1)
    
    def reset(self):
        """Reset menu state"""
        self.selected_button = None
        self.hover_button = None
        self.transition_alpha = 255
        self.transitioning = False
        self.game_starting = False
        self.animation_time = 0
        
        # Reset button animations
        for anim in self.button_animations.values():
            anim['alpha'] = 0
            anim['scale'] = 1.0
            anim['offset_x'] = 0
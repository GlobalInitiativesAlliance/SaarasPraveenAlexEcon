import pygame
import math
import time
from typing import Tuple, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

class UITheme(Enum):
    """Modern UI color themes"""
    DARK_GLASS = {
        'primary': (147, 51, 234),  # Purple
        'secondary': (59, 130, 246),  # Blue
        'accent': (34, 197, 94),  # Green
        'danger': (239, 68, 68),  # Red
        'warning': (245, 158, 11),  # Amber
        'background': (15, 23, 42),  # Dark slate
        'surface': (30, 41, 59),  # Slate 800
        'text_primary': (248, 250, 252),  # Slate 50
        'text_secondary': (148, 163, 184),  # Slate 400
        'glass': (255, 255, 255, 10),  # White with alpha
    }

    CYBERPUNK = {
        'primary': (236, 72, 153),  # Pink
        'secondary': (168, 85, 247),  # Purple
        'accent': (14, 165, 233),  # Cyan
        'danger': (244, 63, 94),  # Rose
        'warning': (251, 146, 60),  # Orange
        'background': (9, 9, 11),  # Zinc 950
        'surface': (24, 24, 27),  # Zinc 900
        'text_primary': (244, 244, 245),  # Zinc 100
        'text_secondary': (161, 161, 170),  # Zinc 400
        'glass': (255, 255, 255, 8),
    }


@dataclass
class Animation:
    """Animation state tracker"""
    start_time: float
    duration: float
    start_value: float
    end_value: float
    easing: str = 'ease_out'

    def get_value(self) -> float:
        """Get current animation value with easing"""
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            return self.end_value

        progress = elapsed / self.duration

        # Apply easing
        if self.easing == 'ease_out':
            progress = 1 - (1 - progress) ** 3
        elif self.easing == 'ease_in':
            progress = progress ** 3
        elif self.easing == 'ease_in_out':
            if progress < 0.5:
                progress = 2 * progress ** 2
            else:
                progress = 1 - pow(-2 * progress + 2, 2) / 2

        return self.start_value + (self.end_value - self.start_value) * progress

    @property
    def is_complete(self) -> bool:
        return time.time() - self.start_time >= self.duration


class ModernObjectiveUI:
    """High-quality modern UI for objectives/tasks"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.theme = UITheme.DARK_GLASS.value

        # Animation states
        self.animations: Dict[str, Animation] = {}
        self.panel_y = -200  # Start off-screen
        self.panel_opacity = 0
        self.is_visible = False

        # Hover states
        self.button_hovers = {}
        self.last_hover_time = {}

        # Progress animation
        self.progress_particles = []

        # Notification queue
        self.notifications = []

        # Load custom fonts if available
        self.load_fonts()

        # Create surfaces for glass effect
        self.glass_surface = None
        self.shadow_surface = None

    def load_fonts(self):
        """Load custom fonts with fallback"""
        try:
            # Try to load custom fonts
            self.font_title = pygame.font.Font(None, 32)
            self.font_subtitle = pygame.font.Font(None, 24)
            self.font_body = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)
            self.font_icon = pygame.font.Font(None, 28)
        except:
            # Fallback to system fonts
            self.font_title = pygame.font.SysFont('helvetica', 32, bold=True)
            self.font_subtitle = pygame.font.SysFont('helvetica', 24)
            self.font_body = pygame.font.SysFont('helvetica', 20)
            self.font_small = pygame.font.SysFont('helvetica', 16)
            self.font_icon = pygame.font.SysFont('helvetica', 28)

    def create_glass_panel(self, width: int, height: int, opacity: int = 200) -> pygame.Surface:
        """Create a glass-morphism panel with blur effect"""
        panel = pygame.Surface((width, height), pygame.SRCALPHA)

        # Multi-layer gradient for depth
        for i in range(3):
            alpha = opacity - i * 30
            color = (*self.theme['surface'][:3], alpha if alpha > 0 else 0)
            offset = i * 2
            pygame.draw.rect(panel, color,
                           (offset, offset, width - offset*2, height - offset*2),
                           border_radius=12 - i*2)

        # Add subtle gradient overlay
        gradient = self.create_gradient(width, height,
                                       (255, 255, 255, 5),
                                       (255, 255, 255, 15))
        panel.blit(gradient, (0, 0))

        # Add glow border
        self.add_glow_border(panel, width, height, self.theme['primary'], 40)

        return panel

    def create_gradient(self, width: int, height: int,
                       start_color: Tuple, end_color: Tuple) -> pygame.Surface:
        """Create a vertical gradient surface"""
        gradient = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(height):
            ratio = y / height
            color = [
                int(start_color[i] + (end_color[i] - start_color[i]) * ratio)
                for i in range(len(start_color))
            ]
            pygame.draw.line(gradient, color, (0, y), (width, y))

        return gradient

    def add_glow_border(self, surface: pygame.Surface, width: int, height: int,
                       color: Tuple[int, int, int], intensity: int):
        """Add a glowing border effect"""
        # Create multiple layers of decreasing opacity
        for i in range(5):
            alpha = intensity - i * 8
            if alpha <= 0:
                break
            glow_color = (*color, alpha)
            pygame.draw.rect(surface, glow_color,
                           (i, i, width - i*2, height - i*2),
                           width=2, border_radius=12)

    def animate_in(self):
        """Animate the UI panel sliding in"""
        self.is_visible = True
        self.animations['panel_y'] = Animation(
            start_time=time.time(),
            duration=0.5,
            start_value=-200,
            end_value=20,
            easing='ease_out'
        )
        self.animations['opacity'] = Animation(
            start_time=time.time(),
            duration=0.3,
            start_value=0,
            end_value=255,
            easing='ease_out'
        )

    def draw_objective_panel(self, screen: pygame.Surface, objective_data: Dict):
        """Draw the main objective panel with modern styling"""

        # Update animations
        if 'panel_y' in self.animations:
            self.panel_y = self.animations['panel_y'].get_value()
            if self.animations['panel_y'].is_complete:
                del self.animations['panel_y']

        if 'opacity' in self.animations:
            self.panel_opacity = self.animations['opacity'].get_value()
            if self.animations['opacity'].is_complete:
                del self.animations['opacity']

        # Panel dimensions
        panel_width = 380
        panel_height = 180
        panel_x = 30

        # Create glass panel
        panel_surface = self.create_glass_panel(panel_width, panel_height, int(self.panel_opacity * 0.8))

        # Draw shadow
        shadow = pygame.Surface((panel_width + 20, panel_height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
        screen.blit(shadow, (panel_x - 10, self.panel_y + 10))

        # Draw the panel
        screen.blit(panel_surface, (panel_x, self.panel_y))

        # Content with better spacing
        content_x = panel_x + 25
        content_y = self.panel_y + 20

        # Draw chapter/part indicator with icon
        self.draw_chapter_badge(screen, content_x, content_y, objective_data.get('part', 1))

        # Draw time with icon
        self.draw_time_display(screen, content_x + 280, content_y,
                              objective_data.get('time', '8:00 AM'))

        # Objective title with animation
        title_y = content_y + 45
        title_text = objective_data.get('title', 'Current Objective')
        self.draw_animated_text(screen, title_text, content_x, title_y,
                               self.font_subtitle, self.theme['text_primary'])

        # Objective description with word wrap
        desc_y = title_y + 35
        description = objective_data.get('description', '')
        self.draw_wrapped_text(screen, description, content_x, desc_y,
                             panel_width - 50, self.font_body, self.theme['text_secondary'])

        # Progress bar with particles
        progress_y = self.panel_y + panel_height - 25
        self.draw_progress_bar(screen, panel_x + 20, progress_y,
                             panel_width - 40, objective_data.get('progress', 0.3))

        # Skip button with hover effect
        self.draw_skip_button(screen, panel_x + panel_width - 100, self.panel_y + 20)

    def draw_chapter_badge(self, screen: pygame.Surface, x: int, y: int, chapter: int):
        """Draw a styled chapter/part badge"""
        badge_width = 80
        badge_height = 30

        # Badge background with gradient
        badge = pygame.Surface((badge_width, badge_height), pygame.SRCALPHA)
        gradient = self.create_gradient(badge_width, badge_height,
                                      self.theme['primary'], self.theme['secondary'])
        badge.blit(gradient, (0, 0))

        # Round the corners
        pygame.draw.rect(badge, (0, 0, 0, 0), badge.get_rect(), border_radius=15)

        # Add to screen
        screen.blit(badge, (x, y))

        # Text
        text = self.font_small.render(f"PART {chapter}", True, self.theme['text_primary'])
        text_rect = text.get_rect(center=(x + badge_width//2, y + badge_height//2))
        screen.blit(text, text_rect)

    def draw_time_display(self, screen: pygame.Surface, x: int, y: int, time_str: str):
        """Draw time with clock icon"""
        # Clock icon (simple circle with hands)
        clock_radius = 10
        clock_x = x
        clock_y = y + 15

        pygame.draw.circle(screen, self.theme['text_secondary'],
                         (clock_x, clock_y), clock_radius, 2)

        # Clock hands
        angle = -math.pi/2 + (time.time() % 60) * (2*math.pi/60)
        hand_end_x = clock_x + int(clock_radius * 0.7 * math.cos(angle))
        hand_end_y = clock_y + int(clock_radius * 0.7 * math.sin(angle))
        pygame.draw.line(screen, self.theme['text_secondary'],
                        (clock_x, clock_y), (hand_end_x, hand_end_y), 2)

        # Time text
        time_text = self.font_small.render(time_str, True, self.theme['text_secondary'])
        screen.blit(time_text, (x + 20, y + 8))

    def draw_animated_text(self, screen: pygame.Surface, text: str, x: int, y: int,
                         font: pygame.font.Font, color: Tuple[int, int, int]):
        """Draw text with subtle animation"""
        # Add slight wave effect
        for i, char in enumerate(text):
            offset_y = math.sin(time.time() * 2 + i * 0.1) * 1
            char_surface = font.render(char, True, color)
            screen.blit(char_surface, (x + i * 12, y + offset_y))

    def draw_wrapped_text(self, screen: pygame.Surface, text: str, x: int, y: int,
                        max_width: int, font: pygame.font.Font, color: Tuple[int, int, int]):
        """Draw word-wrapped text"""
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

        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines[:2]):  # Max 2 lines
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (x, y + i * 22))

    def draw_progress_bar(self, screen: pygame.Surface, x: int, y: int,
                        width: int, progress: float):
        """Draw an animated progress bar with particles"""
        height = 8

        # Background track
        track = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(track, (*self.theme['surface'], 100),
                        track.get_rect(), border_radius=4)
        screen.blit(track, (x, y))

        # Progress fill with gradient
        if progress > 0:
            fill_width = int(width * progress)
            fill = pygame.Surface((fill_width, height), pygame.SRCALPHA)

            # Gradient from accent to primary
            gradient = self.create_gradient(fill_width, height,
                                          self.theme['accent'], self.theme['primary'])
            fill.blit(gradient, (0, 0))

            # Add pulsing glow
            pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7
            glow_color = (*self.theme['accent'], int(100 * pulse))
            pygame.draw.rect(fill, glow_color, fill.get_rect(),
                           width=2, border_radius=4)

            screen.blit(fill, (x, y))

            # Add particles at the end
            self.spawn_progress_particle(x + fill_width, y + height//2)
            self.draw_progress_particles(screen)

        # Progress text
        percent_text = f"{int(progress * 100)}%"
        text_surface = self.font_small.render(percent_text, True, self.theme['text_primary'])
        text_x = x + width + 10
        text_y = y - 2
        screen.blit(text_surface, (text_x, text_y))

    def spawn_progress_particle(self, x: int, y: int):
        """Spawn a particle at progress bar end"""
        if len(self.progress_particles) < 10 and time.time() % 0.1 < 0.05:
            particle = {
                'x': x,
                'y': y,
                'vx': pygame.time.get_ticks() % 3 - 1,
                'vy': -2,
                'life': 1.0,
                'color': self.theme['accent']
            }
            self.progress_particles.append(particle)

    def draw_progress_particles(self, screen: pygame.Surface):
        """Draw and update particles"""
        for particle in self.progress_particles[:]:
            # Update particle
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= 0.02

            if particle['life'] <= 0:
                self.progress_particles.remove(particle)
                continue

            # Draw particle
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            size = int(3 * particle['life'])

            if size > 0:
                particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (size, size), size)
                screen.blit(particle_surface,
                          (int(particle['x'] - size), int(particle['y'] - size)))

    def draw_skip_button(self, screen: pygame.Surface, x: int, y: int):
        """Draw an interactive skip button"""
        button_width = 80
        button_height = 32
        button_id = 'skip'

        # Check hover state
        mouse_pos = pygame.mouse.get_pos()
        is_hover = (x <= mouse_pos[0] <= x + button_width and
                   y <= mouse_pos[1] <= y + button_height)

        # Animate hover
        if is_hover and button_id not in self.button_hovers:
            self.button_hovers[button_id] = Animation(
                start_time=time.time(),
                duration=0.2,
                start_value=0,
                end_value=1,
                easing='ease_out'
            )
        elif not is_hover and button_id in self.button_hovers:
            del self.button_hovers[button_id]

        # Get hover animation value
        hover_value = 0
        if button_id in self.button_hovers:
            hover_value = self.button_hovers[button_id].get_value()

        # Button surface
        button = pygame.Surface((button_width, button_height), pygame.SRCALPHA)

        # Background with hover effect
        bg_color = self.blend_colors(self.theme['danger'], self.theme['warning'], hover_value)
        bg_alpha = int(150 + hover_value * 50)
        pygame.draw.rect(button, (*bg_color, bg_alpha),
                        button.get_rect(), border_radius=6)

        # Border
        border_color = (*bg_color, 255)
        pygame.draw.rect(button, border_color, button.get_rect(),
                        width=2, border_radius=6)

        # Add to screen
        screen.blit(button, (x, y))

        # Text with arrow
        text = "SKIP →" if hover_value < 0.5 else "SKIP ⟶"
        text_color = self.blend_colors(self.theme['text_secondary'],
                                      self.theme['text_primary'], hover_value)
        text_surface = self.font_small.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + button_width//2, y + button_height//2))
        screen.blit(text_surface, text_rect)

        # Change cursor on hover
        if is_hover:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def blend_colors(self, color1: Tuple[int, int, int],
                    color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
        """Blend two colors together"""
        return tuple(int(color1[i] + (color2[i] - color1[i]) * ratio) for i in range(3))

    def show_notification(self, title: str, message: str, type: str = 'info'):
        """Add a notification to the queue"""
        notification = {
            'title': title,
            'message': message,
            'type': type,
            'start_time': time.time(),
            'duration': 3.0,
            'y': self.screen_height,
            'target_y': self.screen_height - 100 - len(self.notifications) * 110
        }
        self.notifications.append(notification)

    def draw_notifications(self, screen: pygame.Surface):
        """Draw all active notifications"""
        for notif in self.notifications[:]:
            elapsed = time.time() - notif['start_time']

            # Remove expired notifications
            if elapsed > notif['duration']:
                self.notifications.remove(notif)
                continue

            # Animate position
            if elapsed < 0.3:  # Slide in
                progress = elapsed / 0.3
                notif['y'] = self.screen_height - (self.screen_height - notif['target_y']) * progress
            elif elapsed > notif['duration'] - 0.3:  # Slide out
                progress = (elapsed - (notif['duration'] - 0.3)) / 0.3
                notif['y'] = notif['target_y'] + (self.screen_height - notif['target_y']) * progress
            else:
                notif['y'] = notif['target_y']

            # Draw notification
            self.draw_notification(screen, notif['title'], notif['message'],
                                 self.screen_width - 350, int(notif['y']), notif['type'])

    def draw_notification(self, screen: pygame.Surface, title: str, message: str,
                        x: int, y: int, type: str):
        """Draw a single notification toast"""
        width = 320
        height = 80

        # Create notification surface
        notif = pygame.Surface((width, height), pygame.SRCALPHA)

        # Background with type-specific color
        bg_color = {
            'info': self.theme['primary'],
            'success': self.theme['accent'],
            'warning': self.theme['warning'],
            'error': self.theme['danger']
        }.get(type, self.theme['primary'])

        # Glass background
        pygame.draw.rect(notif, (*self.theme['surface'], 220),
                        notif.get_rect(), border_radius=8)

        # Colored left border
        pygame.draw.rect(notif, bg_color, (0, 0, 4, height))

        # Icon area
        icon_size = 24
        icon_x = 15
        icon_y = height // 2 - icon_size // 2
        pygame.draw.circle(notif, bg_color, (icon_x + icon_size//2, icon_y + icon_size//2),
                         icon_size//2, 2)

        # Title
        title_surface = self.font_subtitle.render(title, True, self.theme['text_primary'])
        notif.blit(title_surface, (icon_x + icon_size + 15, 15))

        # Message
        msg_surface = self.font_small.render(message, True, self.theme['text_secondary'])
        notif.blit(msg_surface, (icon_x + icon_size + 15, 40))

        # Add to screen
        screen.blit(notif, (x, y))

    def draw_interaction_prompt(self, screen: pygame.Surface, text: str,
                               x: Optional[int] = None, y: Optional[int] = None):
        """Draw an interaction prompt (Press E to...)"""
        if x is None:
            x = self.screen_width // 2
        if y is None:
            y = self.screen_height // 2 - 100

        # Prompt dimensions
        padding = 20
        text_surface = self.font_body.render(text, True, self.theme['text_primary'])
        width = text_surface.get_width() + 60 + padding * 2
        height = 50

        # Center horizontally
        x = x - width // 2

        # Create prompt surface with glass effect
        prompt = self.create_glass_panel(width, height, 180)

        # Pulsing border
        pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5
        border_color = (*self.theme['accent'], int(255 * pulse))
        pygame.draw.rect(prompt, border_color, prompt.get_rect(),
                        width=2, border_radius=8)

        # Key indicator
        key_bg = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(key_bg, (*self.theme['accent'], 100),
                        key_bg.get_rect(), border_radius=6)
        pygame.draw.rect(key_bg, self.theme['accent'],
                        key_bg.get_rect(), width=2, border_radius=6)
        prompt.blit(key_bg, (padding, 7))

        # E key
        key_text = self.font_subtitle.render("E", True, self.theme['text_primary'])
        key_rect = key_text.get_rect(center=(padding + 18, 25))
        prompt.blit(key_text, key_rect)

        # Interaction text
        prompt.blit(text_surface, (padding + 50, 15))

        # Add to screen
        screen.blit(prompt, (x, y))
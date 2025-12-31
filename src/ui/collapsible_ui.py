"""
Professional Task Checklist UI
Clean, minimal, game-quality design
"""

import pygame
from typing import Tuple, Dict
from enum import Enum


class UIState(Enum):
    COLLAPSED = "collapsed"
    EXPANDING = "expanding"
    EXPANDED = "expanded"
    COLLAPSING = "collapsing"


class CollapsibleUI:
    """Professional top-center task UI"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Professional color palette
        self.colors = {
            'bg': (20, 20, 24),
            'bg_light': (30, 30, 36),
            'border': (55, 55, 65),
            'accent': (90, 140, 255),
            'success': (70, 200, 120),
            'text': (240, 240, 245),
            'text_secondary': (140, 145, 160),
            'text_muted': (90, 95, 110),
            'checkbox_empty': (45, 45, 55),
            'checkbox_border': (75, 75, 90),
        }

        # Dimensions - clean proportions
        self.collapsed_height = 42
        self.expanded_height = 180
        self.panel_width = 300
        self.corner_radius = 8
        self.padding = 16

        # Position - top center
        self.x = (screen_width - self.panel_width) // 2
        self.y = 16

        # Animation - start collapsed
        self.state = UIState.COLLAPSED
        self.animation_progress = 0.0
        self.animation_speed = 0.12
        self.current_height = self.collapsed_height

        # Interaction
        self.is_hovered = False
        self.header_rect = None

        # Fonts - will be initialized on first draw
        self.fonts_initialized = False
        self.font_title = None
        self.font_task = None
        self.font_small = None

        # Task cache
        self.cached_tasks = []

        # Compatibility
        self.button_rect = pygame.Rect(0, 0, 0, 0)
        self.prev_button_rect = None
        self.next_button_rect = None

    def init_fonts(self):
        """Initialize fonts"""
        if not self.fonts_initialized:
            self.font_title = pygame.font.Font(None, 20)
            self.font_task = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 16)
            self.fonts_initialized = True

    def handle_click(self, pos: Tuple[int, int]) -> str:
        """Handle clicks"""
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.toggle()
            return 'toggle'
        return None

    def handle_motion(self, pos: Tuple[int, int]):
        """Handle hover"""
        self.is_hovered = self.header_rect and self.header_rect.collidepoint(pos)

    def toggle(self):
        """Toggle state"""
        if self.state == UIState.COLLAPSED:
            self.state = UIState.EXPANDING
        elif self.state == UIState.EXPANDED:
            self.state = UIState.COLLAPSING

    def update(self, dt: float):
        """Update animation"""
        if self.state == UIState.EXPANDING:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
            if self.animation_progress >= 1.0:
                self.state = UIState.EXPANDED
        elif self.state == UIState.COLLAPSING:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)
            if self.animation_progress <= 0.0:
                self.state = UIState.COLLAPSED

        # Smooth easing
        t = self.animation_progress
        eased = 1 - pow(1 - t, 3)  # ease-out cubic

        self.current_height = self.collapsed_height + (self.expanded_height - self.collapsed_height) * eased

    def draw(self, screen: pygame.Surface, objective_data: Dict):
        """Draw the professional UI"""
        self.init_fonts()
        self.extract_tasks(objective_data)

        h = int(self.current_height)
        w = self.panel_width

        # Create panel surface
        panel = pygame.Surface((w, h), pygame.SRCALPHA)

        # Draw shadow
        shadow = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 40), (2, 2, w, h), border_radius=self.corner_radius)
        screen.blit(shadow, (self.x - 2, self.y - 1))

        # Main background
        pygame.draw.rect(panel, self.colors['bg'], (0, 0, w, h), border_radius=self.corner_radius)

        # Border
        pygame.draw.rect(panel, self.colors['border'], (0, 0, w, h), width=1, border_radius=self.corner_radius)

        # Draw header
        self.draw_header(panel, objective_data)

        # Draw tasks if expanded
        if self.animation_progress > 0.3:
            alpha = min(255, int(255 * (self.animation_progress - 0.3) / 0.7))
            self.draw_tasks(panel, alpha)

        screen.blit(panel, (self.x, self.y))

        # Update click rect
        self.header_rect = pygame.Rect(self.x, self.y, w, self.collapsed_height)
        self.button_rect = self.header_rect

    def draw_header(self, surface: pygame.Surface, data: Dict):
        """Draw clean header"""
        w = self.panel_width
        header_h = self.collapsed_height

        # Header background (slightly lighter)
        header_rect = pygame.Rect(0, 0, w, header_h)
        pygame.draw.rect(surface, self.colors['bg_light'], header_rect,
                        border_top_left_radius=self.corner_radius,
                        border_top_right_radius=self.corner_radius)

        # Separator line at bottom of header
        pygame.draw.line(surface, self.colors['border'], (0, header_h - 1), (w, header_h - 1), 1)

        # Calculate task progress
        completed = sum(1 for t in self.cached_tasks if t.get('completed', False))
        total = max(1, len(self.cached_tasks))

        # Left side: Part badge + Title
        part_num = data.get('part', 1)
        part_text = f"Part {part_num}"
        part_surf = self.font_small.render(part_text, True, self.colors['text'])

        # Draw Part badge
        badge_w = part_surf.get_width() + 12
        badge_h = 18
        badge_x = self.padding
        badge_y = (header_h - badge_h) // 2

        # Badge background (accent color)
        pygame.draw.rect(surface, self.colors['accent'], (badge_x, badge_y, badge_w, badge_h), border_radius=badge_h // 2)
        surface.blit(part_surf, (badge_x + 6, badge_y + (badge_h - part_surf.get_height()) // 2))

        # Title after badge
        title = data.get('title', 'Tasks')
        title_x = badge_x + badge_w + 8
        max_title_len = 16  # Shorter since we have the badge
        if len(title) > max_title_len:
            title = title[:max_title_len - 3] + "..."
        title_surf = self.font_title.render(title, True, self.colors['text'])
        surface.blit(title_surf, (title_x, (header_h - title_surf.get_height()) // 2))

        # Right side: Progress pill
        progress_text = f"{completed}/{total}"
        progress_surf = self.font_small.render(progress_text, True, self.colors['text'])

        pill_w = progress_surf.get_width() + 20
        pill_h = 22
        pill_x = w - pill_w - self.padding
        pill_y = (header_h - pill_h) // 2

        # Pill background color based on completion
        if completed == total and total > 0:
            pill_color = self.colors['success']
        else:
            pill_color = self.colors['accent']

        pygame.draw.rect(surface, pill_color, (pill_x, pill_y, pill_w, pill_h), border_radius=pill_h // 2)
        surface.blit(progress_surf, (pill_x + (pill_w - progress_surf.get_width()) // 2,
                                     pill_y + (pill_h - progress_surf.get_height()) // 2))

        # Expand/collapse indicator (chevron)
        chevron_x = pill_x - 20
        chevron_y = header_h // 2
        if self.state in [UIState.EXPANDED, UIState.EXPANDING]:
            # Down chevron
            points = [(chevron_x, chevron_y - 3), (chevron_x + 6, chevron_y + 3), (chevron_x + 12, chevron_y - 3)]
        else:
            # Right chevron
            points = [(chevron_x + 2, chevron_y - 5), (chevron_x + 8, chevron_y), (chevron_x + 2, chevron_y + 5)]
        pygame.draw.polygon(surface, self.colors['text_muted'], points)

    def draw_tasks(self, surface: pygame.Surface, alpha: int):
        """Draw task list"""
        if not self.cached_tasks:
            return

        # Create content surface
        content_h = int(self.current_height) - self.collapsed_height
        if content_h <= 0:
            return

        content = pygame.Surface((self.panel_width, content_h), pygame.SRCALPHA)

        y = 12
        task_h = 36

        for i, task in enumerate(self.cached_tasks[:4]):
            is_done = task.get('completed', False)

            # Task row
            row_x = self.padding
            row_w = self.panel_width - self.padding * 2

            # Checkbox
            cb_size = 18
            cb_x = row_x
            cb_y = y + (task_h - cb_size) // 2

            if is_done:
                # Filled checkbox
                pygame.draw.rect(content, self.colors['success'], (cb_x, cb_y, cb_size, cb_size), border_radius=4)
                # Checkmark
                check_points = [
                    (cb_x + 4, cb_y + 9),
                    (cb_x + 7, cb_y + 13),
                    (cb_x + 14, cb_y + 5)
                ]
                pygame.draw.lines(content, self.colors['text'], False, check_points, 2)
            else:
                # Empty checkbox
                pygame.draw.rect(content, self.colors['checkbox_empty'], (cb_x, cb_y, cb_size, cb_size), border_radius=4)
                pygame.draw.rect(content, self.colors['checkbox_border'], (cb_x, cb_y, cb_size, cb_size), width=1, border_radius=4)

            # Task text
            text = task.get('text', '')
            if len(text) > 30:
                text = text[:27] + "..."

            text_color = self.colors['text_muted'] if is_done else self.colors['text']
            text_surf = self.font_task.render(text, True, text_color)
            text_x = cb_x + cb_size + 12
            text_y = y + (task_h - text_surf.get_height()) // 2

            content.blit(text_surf, (text_x, text_y))

            # Strikethrough for completed
            if is_done:
                line_y = text_y + text_surf.get_height() // 2
                pygame.draw.line(content, self.colors['text_muted'],
                               (text_x, line_y), (text_x + text_surf.get_width(), line_y), 1)

            y += task_h

        # Apply alpha
        content.set_alpha(alpha)
        surface.blit(content, (0, self.collapsed_height))

    def extract_tasks(self, objective_data: Dict):
        """Extract tasks from game state"""
        title = objective_data.get('title', '')
        description = objective_data.get('description', '')
        tasks = []

        # Try to get from game interior
        if hasattr(self, 'game') and self.game:
            interior = getattr(self.game, 'current_interior', None)
            if interior and hasattr(interior, 'items_packed'):
                items = interior.items_packed
                tasks = [
                    {'text': 'Pack clothes', 'completed': 'clothes' in items},
                    {'text': 'Get documents', 'completed': 'documents' in items},
                    {'text': 'Choose photo', 'completed': 'photo' in items},
                ]

        # Fallback
        if not tasks:
            if 'pack' in title.lower() or 'pack' in description.lower():
                tasks = [
                    {'text': 'Pack clothes', 'completed': False},
                    {'text': 'Get documents', 'completed': False},
                    {'text': 'Choose photo', 'completed': False},
                ]
            else:
                tasks = [{'text': title if title else 'Complete objective', 'completed': False}]

        self.cached_tasks = tasks

    def force_update(self):
        """Force refresh"""
        self.cached_tasks = []

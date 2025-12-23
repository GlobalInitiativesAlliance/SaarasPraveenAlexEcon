"""
Advanced Task Checklist UI - Top Center
Clean, modern task tracker with progress visualization
"""

import pygame
import math
from typing import Tuple, Optional, Dict, List
from enum import Enum


class UIState(Enum):
    COLLAPSED = "collapsed"
    EXPANDING = "expanding"
    EXPANDED = "expanded"
    COLLAPSING = "collapsing"


class CollapsibleUI:
    """Advanced task checklist UI - positioned top center"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Colors - Modern dark theme
        self.colors = {
            'panel_bg': (22, 22, 26),
            'panel_border': (50, 50, 58),
            'header_bg': (32, 32, 38),
            'accent': (99, 102, 241),  # Indigo
            'accent_glow': (99, 102, 241, 40),
            'success': (34, 197, 94),  # Green
            'success_dim': (22, 130, 62),
            'warning': (245, 158, 11),  # Amber
            'text': (255, 255, 255),
            'text_dim': (160, 165, 180),
            'text_muted': (100, 105, 115),
            'checkbox_bg': (40, 40, 48),
            'checkbox_border': (70, 70, 80),
            'progress_bg': (35, 35, 42),
            'progress_fill': (99, 102, 241),
        }

        # Dimensions
        self.collapsed_width = 200
        self.collapsed_height = 36
        self.expanded_width = 320
        self.expanded_height = 200
        self.corner_radius = 12

        # Position - TOP CENTER
        self.x = (screen_width - self.expanded_width) // 2
        self.y = 12

        # Current dimensions - start collapsed
        self.current_width = self.collapsed_width
        self.current_height = self.collapsed_height

        # Animation state - start COLLAPSED
        self.state = UIState.COLLAPSED
        self.animation_progress = 0.0
        self.animation_speed = 0.15

        # Interaction
        self.header_rect = None
        self.header_hover = False
        self.task_hover_index = -1

        # Fonts
        self.setup_fonts()

        # Task data cache
        self.cached_tasks = []

        # For compatibility with existing code
        self.prev_button_rect = None
        self.next_button_rect = None
        self.button_rect = pygame.Rect(0, 0, 0, 0)

    def setup_fonts(self):
        """Initialize fonts"""
        self.font_header = pygame.font.Font(None, 18)
        self.font_task = pygame.font.Font(None, 17)
        self.font_small = pygame.font.Font(None, 14)
        self.font_icon = pygame.font.Font(None, 20)

    def handle_click(self, pos: Tuple[int, int]) -> str:
        """Handle mouse clicks"""
        if self.header_rect and self.header_rect.collidepoint(pos):
            self.toggle()
            return 'toggle'
        return None

    def handle_motion(self, pos: Tuple[int, int]):
        """Handle mouse motion"""
        self.header_hover = self.header_rect and self.header_rect.collidepoint(pos)

        # Check task hover
        self.task_hover_index = -1
        if self.state == UIState.EXPANDED:
            task_y_start = self.y + 44
            for i, task in enumerate(self.cached_tasks[:4]):
                task_rect = pygame.Rect(self.x + 8, task_y_start + i * 32,
                                       int(self.current_width) - 16, 28)
                if task_rect.collidepoint(pos):
                    self.task_hover_index = i
                    break

    def toggle(self):
        """Toggle expanded/collapsed"""
        if self.state == UIState.COLLAPSED:
            self.state = UIState.EXPANDING
        elif self.state == UIState.EXPANDED:
            self.state = UIState.COLLAPSING

    def update(self, dt: float):
        """Update animations"""
        if self.state == UIState.EXPANDING:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
            if self.animation_progress >= 1.0:
                self.state = UIState.EXPANDED
        elif self.state == UIState.COLLAPSING:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)
            if self.animation_progress <= 0.0:
                self.state = UIState.COLLAPSED

        # Smooth easing
        eased = self.ease_out_quart(self.animation_progress)

        # Update dimensions
        self.current_width = self.collapsed_width + (self.expanded_width - self.collapsed_width) * eased
        self.current_height = self.collapsed_height + (self.expanded_height - self.collapsed_height) * eased

        # Keep centered
        self.x = (self.screen_width - int(self.current_width)) // 2

    def ease_out_quart(self, t: float) -> float:
        """Smooth easing"""
        return 1 - pow(1 - t, 4)

    def draw(self, screen: pygame.Surface, objective_data: Dict):
        """Draw the task checklist UI"""
        w = int(self.current_width)
        h = int(self.current_height)

        # Extract tasks from objective data
        self.extract_tasks(objective_data)

        # Main panel surface
        panel = pygame.Surface((w, h), pygame.SRCALPHA)

        # Shadow
        shadow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 50),
                        pygame.Rect(4, 4, w, h), border_radius=self.corner_radius)
        screen.blit(shadow, (self.x - 4, self.y - 4))

        # Panel background
        pygame.draw.rect(panel, self.colors['panel_bg'],
                        pygame.Rect(0, 0, w, h), border_radius=self.corner_radius)

        # Border with subtle glow effect
        pygame.draw.rect(panel, self.colors['panel_border'],
                        pygame.Rect(0, 0, w, h), width=1, border_radius=self.corner_radius)

        # Draw header
        self.draw_header(panel, objective_data)

        # Draw task list if expanded
        if self.animation_progress > 0.5:
            content_alpha = int(255 * ((self.animation_progress - 0.5) / 0.5))
            self.draw_tasks(panel, content_alpha)

        screen.blit(panel, (self.x, self.y))

        # Update header rect for click detection
        self.header_rect = pygame.Rect(self.x, self.y, w, 36)

        # Update button_rect for compatibility
        self.button_rect = self.header_rect

    def draw_header(self, surface: pygame.Surface, data: Dict):
        """Draw the header bar with progress"""
        w = int(self.current_width)

        # Header background
        header_rect = pygame.Rect(0, 0, w, 36)
        pygame.draw.rect(surface, self.colors['header_bg'], header_rect,
                        border_top_left_radius=self.corner_radius,
                        border_top_right_radius=self.corner_radius)

        # Calculate progress
        completed = sum(1 for t in self.cached_tasks if t.get('completed', False))
        total = len(self.cached_tasks) if self.cached_tasks else 1

        # Progress bar background
        progress_margin = 12
        progress_width = w - 120
        progress_height = 6
        progress_x = progress_margin
        progress_y = 15

        pygame.draw.rect(surface, self.colors['progress_bg'],
                        (progress_x, progress_y, progress_width, progress_height),
                        border_radius=3)

        # Progress bar fill
        if total > 0:
            fill_width = int(progress_width * (completed / total))
            if fill_width > 0:
                # Gradient effect with glow
                fill_color = self.colors['success'] if completed == total else self.colors['accent']
                pygame.draw.rect(surface, fill_color,
                                (progress_x, progress_y, fill_width, progress_height),
                                border_radius=3)

        # Progress text on right
        progress_text = f"{completed}/{total}"
        progress_surf = self.font_header.render(progress_text, True, self.colors['text'])
        surface.blit(progress_surf, (w - progress_surf.get_width() - 40, 10))

        # Chevron icon (expand/collapse indicator)
        chevron = "▼" if self.state in [UIState.EXPANDED, UIState.EXPANDING] else "▶"
        chevron_surf = self.font_small.render(chevron, True, self.colors['text_muted'])
        surface.blit(chevron_surf, (w - 20, 12))

        # Title on left side of progress bar (only when collapsed)
        if self.animation_progress < 0.5:
            title = data.get('title', 'Tasks')
            if len(title) > 20:
                title = title[:17] + "..."
            title_alpha = int(255 * (1 - self.animation_progress * 2))
            title_surf = self.font_header.render(title, True, self.colors['text_dim'])
            title_surf.set_alpha(title_alpha)
            # Position below progress bar when showing
            surface.blit(title_surf, (progress_margin, 22))

    def draw_tasks(self, surface: pygame.Surface, alpha: int):
        """Draw the task list"""
        if alpha <= 0 or not self.cached_tasks:
            return

        content = pygame.Surface((int(self.current_width), int(self.current_height) - 40), pygame.SRCALPHA)

        y = 8
        task_height = 32
        margin = 10

        for i, task in enumerate(self.cached_tasks[:4]):  # Max 4 tasks visible
            is_completed = task.get('completed', False)
            is_hover = (i == self.task_hover_index)

            # Task row background
            row_rect = pygame.Rect(margin, y, int(self.current_width) - margin * 2, task_height - 4)

            if is_hover and not is_completed:
                pygame.draw.rect(content, (45, 45, 52), row_rect, border_radius=6)

            # Checkbox
            checkbox_size = 18
            checkbox_x = margin + 8
            checkbox_y = y + (task_height - checkbox_size) // 2 - 2

            if is_completed:
                # Filled checkbox with checkmark
                pygame.draw.rect(content, self.colors['success'],
                               (checkbox_x, checkbox_y, checkbox_size, checkbox_size),
                               border_radius=4)
                # Checkmark
                check_surf = self.font_icon.render("✓", True, self.colors['text'])
                content.blit(check_surf, (checkbox_x + 3, checkbox_y + 1))
            else:
                # Empty checkbox
                pygame.draw.rect(content, self.colors['checkbox_bg'],
                               (checkbox_x, checkbox_y, checkbox_size, checkbox_size),
                               border_radius=4)
                pygame.draw.rect(content, self.colors['checkbox_border'],
                               (checkbox_x, checkbox_y, checkbox_size, checkbox_size),
                               width=1, border_radius=4)

            # Task text
            task_text = task.get('text', '')
            if len(task_text) > 32:
                task_text = task_text[:29] + "..."

            text_color = self.colors['text_muted'] if is_completed else self.colors['text']
            text_surf = self.font_task.render(task_text, True, text_color)

            # Strikethrough effect for completed tasks
            text_x = checkbox_x + checkbox_size + 10
            text_y = y + (task_height - text_surf.get_height()) // 2 - 2
            content.blit(text_surf, (text_x, text_y))

            if is_completed:
                # Draw strikethrough line
                line_y = text_y + text_surf.get_height() // 2
                pygame.draw.line(content, self.colors['text_muted'],
                               (text_x, line_y), (text_x + text_surf.get_width(), line_y), 1)

            y += task_height

        # Apply alpha
        content.set_alpha(alpha)
        surface.blit(content, (0, 40))

    def extract_tasks(self, objective_data: Dict):
        """Extract tasks from objective data"""
        # Check if objective has specific tasks
        title = objective_data.get('title', '')
        description = objective_data.get('description', '')

        # Try to get tasks from the game's objective manager
        tasks = []

        if hasattr(self, 'game') and self.game:
            obj_mgr = getattr(self.game, 'objective_manager', None)
            if obj_mgr:
                current_obj = obj_mgr.get_current_objective()
                if current_obj:
                    # Check for sub-tasks or checklist items
                    if hasattr(current_obj, 'tasks'):
                        tasks = current_obj.tasks
                    elif hasattr(current_obj, 'checklist'):
                        tasks = current_obj.checklist

                    # Check for foster home packing tasks
                    if hasattr(obj_mgr, 'game') and obj_mgr.game:
                        interior = getattr(obj_mgr.game, 'current_interior', None)
                        if interior and hasattr(interior, 'items_packed'):
                            items_packed = interior.items_packed
                            required = getattr(interior, 'required_items', {'clothes', 'documents', 'photo'})
                            tasks = [
                                {'text': 'Pack clothes from closet', 'completed': 'clothes' in items_packed},
                                {'text': 'Get documents from desk', 'completed': 'documents' in items_packed},
                                {'text': 'Choose photo from nightstand', 'completed': 'photo' in items_packed},
                            ]

        # Fallback: create tasks from description
        if not tasks:
            if 'pack' in description.lower() or 'pack' in title.lower():
                tasks = [
                    {'text': 'Pack your belongings', 'completed': False},
                    {'text': 'Find important documents', 'completed': False},
                    {'text': 'Choose what to keep', 'completed': False},
                ]
            elif description:
                tasks = [{'text': description[:40], 'completed': False}]
            else:
                tasks = [{'text': title, 'completed': False}]

        self.cached_tasks = tasks

    def force_update(self):
        """Force cache reset"""
        self.cached_tasks = []

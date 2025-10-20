"""
Modern Collapsible UI System for Economics Adventure
Clean, minimalist design with smooth animations
"""

import pygame
import math
import time
from typing import Tuple, Optional, Dict
from enum import Enum


class UIState(Enum):
    COLLAPSED = "collapsed"
    EXPANDING = "expanding"
    EXPANDED = "expanded"
    COLLAPSING = "collapsing"


class CollapsibleUI:
    """Clean, aesthetic collapsible UI panel"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Colors - Modern, clean palette
        self.colors = {
            'bg': (18, 18, 20),  # Almost black
            'panel': (28, 28, 32),  # Dark gray
            'accent': (88, 101, 242),  # Modern blue
            'text': (255, 255, 255),  # Pure white
            'text_dim': (156, 163, 175),  # Dimmed text
            'success': (34, 197, 94),  # Green
            'hover': (55, 65, 81),  # Hover state
            'border': (55, 55, 60),  # Subtle border
        }

        # Dimensions
        self.collapsed_width = 48  # Just the hamburger button
        self.collapsed_height = 48  # Small square for hamburger
        self.expanded_width = 320
        self.expanded_height = 180
        self.margin = 20
        self.corner_radius = 12

        # Position (top-left corner)
        self.x = self.margin
        self.y = self.margin

        # Animation
        self.state = UIState.EXPANDED
        self.animation_progress = 1.0  # 0 = collapsed, 1 = expanded
        self.animation_speed = 0.15
        self.current_width = self.expanded_width
        self.current_height = self.expanded_height

        # Hamburger menu button
        self.button_size = 32
        self.button_hover = False
        # Button rect will be updated dynamically
        self.update_button_rect()

        # Content visibility based on animation
        self.content_alpha = 255

        # Fonts
        self.setup_fonts()

        # Cached surfaces for performance
        self.shadow_surface = None
        self.create_shadow()

    def setup_fonts(self):
        """Initialize fonts with fallbacks"""
        try:
            # Try modern system fonts
            self.font_title = pygame.font.SysFont('Inter', 18, bold=True)
            self.font_body = pygame.font.SysFont('Inter', 14)
            self.font_small = pygame.font.SysFont('Inter', 12)
        except:
            # Fallback fonts
            self.font_title = pygame.font.Font(None, 18)
            self.font_body = pygame.font.Font(None, 14)
            self.font_small = pygame.font.Font(None, 12)

    def create_shadow(self):
        """Create a reusable shadow surface"""
        shadow_size = max(self.expanded_width, self.expanded_height) + 40
        self.shadow_surface = pygame.Surface((shadow_size, shadow_size), pygame.SRCALPHA)

        # Multi-layer shadow for depth
        for i in range(3):
            alpha = 30 - i * 10
            offset = i * 2
            shadow_rect = pygame.Rect(
                10 + offset,
                10 + offset,
                self.expanded_width - offset * 2,
                self.expanded_height - offset * 2
            )
            pygame.draw.rect(
                self.shadow_surface,
                (0, 0, 0, alpha),
                shadow_rect,
                border_radius=self.corner_radius
            )

    def update_button_rect(self):
        """Update button rect position"""
        button_margin = 8 if self.state == UIState.COLLAPSED else 10
        self.button_rect = pygame.Rect(
            self.x + button_margin,
            self.y + button_margin,
            self.button_size,
            self.button_size
        )

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse clicks"""
        # Check if hamburger button was clicked
        if self.button_rect.collidepoint(pos):
            self.toggle()
            return True
        return False

    def handle_motion(self, pos: Tuple[int, int]):
        """Handle mouse motion for hover effects"""
        self.button_hover = self.button_rect.collidepoint(pos)

    def toggle(self):
        """Toggle between collapsed and expanded states"""
        if self.state == UIState.COLLAPSED:
            self.state = UIState.EXPANDING
        elif self.state == UIState.EXPANDED:
            self.state = UIState.COLLAPSING

    def update(self, dt: float):
        """Update animations"""
        # Handle state transitions
        if self.state == UIState.EXPANDING:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
            if self.animation_progress >= 1.0:
                self.state = UIState.EXPANDED

        elif self.state == UIState.COLLAPSING:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)
            if self.animation_progress <= 0.0:
                self.state = UIState.COLLAPSED

        # Smooth animation using easing
        eased_progress = self.ease_in_out_cubic(self.animation_progress)

        # Update current dimensions
        self.current_width = self.collapsed_width + (self.expanded_width - self.collapsed_width) * eased_progress
        self.current_height = self.collapsed_height + (self.expanded_height - self.collapsed_height) * eased_progress

        # Update button rect position
        self.update_button_rect()

        # Update content alpha for fade effect
        self.content_alpha = int(255 * eased_progress)

    def ease_in_out_cubic(self, t: float) -> float:
        """Smooth easing function"""
        if t < 0.5:
            return 4 * t * t * t
        p = 2 * t - 2
        return 1 + p * p * p / 2

    def draw(self, screen: pygame.Surface, objective_data: Dict):
        """Draw the collapsible UI panel"""
        # Draw shadow only when expanded
        if self.animation_progress > 0.2:
            shadow_alpha = int(60 * self.animation_progress)
            # Create dynamic shadow based on current size
            shadow_surf = pygame.Surface((int(self.current_width) + 8, int(self.current_height) + 8), pygame.SRCALPHA)
            for i in range(2):
                alpha = shadow_alpha - i * 20
                offset = i * 2
                pygame.draw.rect(
                    shadow_surf,
                    (0, 0, 0, alpha),
                    pygame.Rect(2 + offset, 2 + offset,
                               int(self.current_width) - offset * 2,
                               int(self.current_height) - offset * 2),
                    border_radius=self.corner_radius
                )
            screen.blit(shadow_surf, (self.x - 4, self.y - 4))

        # Create panel surface with current dimensions
        panel_surface = pygame.Surface((int(self.current_width), int(self.current_height)), pygame.SRCALPHA)

        # Draw panel background
        pygame.draw.rect(
            panel_surface,
            self.colors['panel'],
            panel_surface.get_rect(),
            border_radius=self.corner_radius
        )

        # Draw subtle border
        pygame.draw.rect(
            panel_surface,
            self.colors['border'],
            panel_surface.get_rect(),
            width=1,
            border_radius=self.corner_radius
        )

        # Draw hamburger menu button
        self.draw_hamburger_button(panel_surface)

        # Draw content if expanded enough
        if self.animation_progress > 0.3:
            self.draw_content(panel_surface, objective_data)

        # Draw to screen
        screen.blit(panel_surface, (self.x, self.y))

    def draw_hamburger_button(self, surface: pygame.Surface):
        """Draw the animated hamburger menu button"""
        # Button position changes when collapsed
        if self.state == UIState.COLLAPSED or self.animation_progress < 0.1:
            # Center button in small panel
            button_x = (int(self.current_width) - self.button_size) // 2
            button_y = (int(self.current_height) - self.button_size) // 2
        else:
            # Normal position when expanded
            button_x = 8
            button_y = 8

        # Button background
        button_color = self.colors['hover'] if self.button_hover else (38, 38, 42)
        button_rect = pygame.Rect(button_x, button_y, self.button_size, self.button_size)
        pygame.draw.rect(
            surface,
            button_color,
            button_rect,
            border_radius=8
        )

        # Hamburger lines with animation
        line_width = 18
        line_height = 2
        line_spacing = 4
        center_x = button_x + self.button_size // 2
        center_y = button_y + self.button_size // 2

        # Calculate rotation based on animation
        rotation = self.animation_progress * 45

        # Top line
        top_y = center_y - line_spacing
        if self.animation_progress > 0.5:
            # Rotate to form X
            self.draw_rotated_line(
                surface,
                (center_x, center_y),
                line_width,
                line_height,
                rotation,
                self.colors['text']
            )
        else:
            pygame.draw.rect(
                surface,
                self.colors['text'],
                (center_x - line_width // 2, top_y - line_height // 2, line_width, line_height),
                border_radius=1
            )

        # Middle line (fades out)
        if self.animation_progress < 0.5:
            middle_alpha = int(255 * (1 - self.animation_progress * 2))
            middle_color = (*self.colors['text'], middle_alpha)
            middle_surf = pygame.Surface((line_width, line_height), pygame.SRCALPHA)
            pygame.draw.rect(
                middle_surf,
                middle_color,
                middle_surf.get_rect(),
                border_radius=1
            )
            surface.blit(middle_surf, (center_x - line_width // 2, center_y - line_height // 2))

        # Bottom line
        bottom_y = center_y + line_spacing
        if self.animation_progress > 0.5:
            # Rotate to form X
            self.draw_rotated_line(
                surface,
                (center_x, center_y),
                line_width,
                line_height,
                -rotation,
                self.colors['text']
            )
        else:
            pygame.draw.rect(
                surface,
                self.colors['text'],
                (center_x - line_width // 2, bottom_y - line_height // 2, line_width, line_height),
                border_radius=1
            )

    def draw_rotated_line(self, surface, center, width, height, angle, color):
        """Draw a rotated rectangle line"""
        # Create a surface for the line
        line_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(line_surf, color, line_surf.get_rect(), border_radius=1)

        # Rotate it
        rotated = pygame.transform.rotate(line_surf, angle)

        # Position it
        rect = rotated.get_rect(center=center)
        surface.blit(rotated, rect)

    def draw_content(self, surface: pygame.Surface, data: Dict):
        """Draw the panel content with fade effect"""
        content_x = 60  # Start after hamburger button
        content_y = 15

        # Apply fade effect
        if self.content_alpha < 255:
            surface.set_alpha(self.content_alpha)

        # Part and Day info (compact)
        info_text = f"Part {data.get('part', 1)} • Day {data.get('day', 1)}"
        info_surf = self.font_small.render(info_text, True, self.colors['text_dim'])
        surface.blit(info_surf, (content_x, content_y))

        # Time (right-aligned)
        time_text = data.get('time', '8:00 AM')
        time_surf = self.font_small.render(time_text, True, self.colors['accent'])
        time_x = int(self.current_width) - time_surf.get_width() - 20
        surface.blit(time_surf, (time_x, content_y))

        # Main objective title
        title_y = content_y + 25
        title = data.get('title', 'Current Objective')
        # Truncate if too long
        if len(title) > 30:
            title = title[:27] + "..."
        title_surf = self.font_title.render(title, True, self.colors['text'])
        surface.blit(title_surf, (content_x, title_y))

        # Description (2 lines max)
        desc_y = title_y + 25
        description = data.get('description', '')
        words = description.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font_body.size(test_line)[0] <= int(self.current_width) - 80:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                if len(lines) >= 2:
                    break

        if current_line and len(lines) < 2:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines[:2]):
            line_surf = self.font_body.render(line, True, self.colors['text_dim'])
            surface.blit(line_surf, (content_x, desc_y + i * 18))

        # Progress indicator (simple dots)
        if data.get('progress') and self.animation_progress > 0.5:
            self.draw_progress_dots(surface, content_x, int(self.current_height) - 30, data['progress'])

        # "Press E" hint at bottom
        if self.animation_progress > 0.8:
            hint_alpha = int(self.colors['text_dim'][0] * (self.animation_progress - 0.8) * 5)
            hint_color = (hint_alpha, hint_alpha, hint_alpha)
            hint_text = "Press E to interact"
            hint_surf = self.font_small.render(hint_text, True, hint_color)
            hint_x = int(self.current_width) // 2 - hint_surf.get_width() // 2
            surface.blit(hint_surf, (hint_x, int(self.current_height) - 25))

    def draw_progress_dots(self, surface: pygame.Surface, x: int, y: int, progress: float):
        """Draw simple progress dots"""
        num_dots = 5
        dot_size = 4
        dot_spacing = 10

        for i in range(num_dots):
            dot_progress = i / num_dots
            if dot_progress <= progress:
                color = self.colors['accent']
            else:
                color = self.colors['border']

            dot_x = x + i * (dot_size + dot_spacing)
            pygame.draw.circle(surface, color, (dot_x, y), dot_size)
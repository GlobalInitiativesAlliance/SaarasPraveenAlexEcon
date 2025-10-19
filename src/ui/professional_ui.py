"""
Professional, Clean UI System for Economics Adventure
Designed with proper visual hierarchy, symmetry, and game cohesion
"""

import pygame
import math
import time
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class UIColors:
    """Professional color palette that matches the game aesthetic"""
    # Primary UI Colors
    PANEL_BG = (28, 32, 40)  # Softer dark blue-gray
    PANEL_BORDER = (52, 58, 70)  # Slightly lighter border
    PANEL_ACCENT = (72, 82, 100)  # Accent line color

    # Text Colors
    TEXT_PRIMARY = (255, 255, 255)  # Pure white for main text
    TEXT_SECONDARY = (185, 195, 210)  # Soft blue-gray for secondary
    TEXT_MUTED = (120, 130, 145)  # Muted for less important

    # Status Colors (softer, more professional)
    SUCCESS = (72, 187, 120)  # Soft green
    WARNING = (246, 173, 85)  # Warm orange
    DANGER = (237, 94, 104)  # Soft red
    INFO = (90, 156, 248)  # Soft blue

    # Interactive Elements
    BUTTON_DEFAULT = (55, 65, 81)
    BUTTON_HOVER = (71, 85, 105)
    BUTTON_ACTIVE = (96, 165, 250)

    # Progress Bar
    PROGRESS_BG = (35, 40, 48)
    PROGRESS_FILL = (90, 156, 248)
    PROGRESS_SHINE = (120, 186, 255)

    # Shadows and Effects
    SHADOW = (10, 12, 15, 128)  # Semi-transparent shadow
    GLOW = (255, 255, 255, 30)  # Subtle glow


class UIMetrics:
    """Standardized spacing and sizing for consistent layout"""
    # Grid system - everything aligns to 8px grid
    GRID_UNIT = 8

    # Spacing
    PADDING_SMALL = GRID_UNIT  # 8px
    PADDING = GRID_UNIT * 2  # 16px
    PADDING_LARGE = GRID_UNIT * 3  # 24px
    MARGIN = GRID_UNIT * 4  # 32px

    # Panel dimensions
    PANEL_WIDTH = GRID_UNIT * 48  # 384px - perfectly divisible
    PANEL_HEIGHT = GRID_UNIT * 22  # 176px

    # Component heights
    HEADER_HEIGHT = GRID_UNIT * 5  # 40px
    BUTTON_HEIGHT = GRID_UNIT * 4  # 32px
    PROGRESS_HEIGHT = GRID_UNIT  # 8px

    # Border radius
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12

    # Animation
    TRANSITION_SPEED = 0.15  # Subtle, not distracting


@dataclass
class UIAnimation:
    """Smooth animation handler"""
    current: float
    target: float
    speed: float = UIMetrics.TRANSITION_SPEED

    def update(self, dt: float) -> float:
        """Smoothly animate towards target"""
        diff = self.target - self.current
        self.current += diff * min(self.speed * 60 * dt, 1.0)
        return self.current

    @property
    def value(self) -> float:
        return self.current


class ProfessionalObjectiveUI:
    """Clean, professional UI for game objectives"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Positioning
        self.panel_x = UIMetrics.MARGIN
        self.panel_y = UIMetrics.MARGIN

        # Animations
        self.panel_slide = UIAnimation(-UIMetrics.PANEL_HEIGHT, UIMetrics.MARGIN, 0.08)
        self.panel_alpha = UIAnimation(0, 255, 0.05)
        self.progress_animation = UIAnimation(0, 0)

        # Interaction states
        self.button_hover_states = {}
        self.last_progress = 0

        # Font system with proper hierarchy
        self.setup_fonts()

        # Pre-render static elements for performance
        self.cache = {}

    def setup_fonts(self):
        """Setup professional font hierarchy"""
        try:
            # Try to use system fonts for clean look
            self.font_title = pygame.font.SysFont('SF Pro Display', 24, bold=True)
            self.font_subtitle = pygame.font.SysFont('SF Pro Display', 18)
            self.font_body = pygame.font.SysFont('SF Pro Text', 16)
            self.font_caption = pygame.font.SysFont('SF Pro Text', 14)
            self.font_small = pygame.font.SysFont('SF Pro Text', 12)
        except:
            # Fallback fonts
            self.font_title = pygame.font.Font(None, 24)
            self.font_subtitle = pygame.font.Font(None, 18)
            self.font_body = pygame.font.Font(None, 16)
            self.font_caption = pygame.font.Font(None, 14)
            self.font_small = pygame.font.Font(None, 12)

    def create_panel_surface(self) -> pygame.Surface:
        """Create the main panel with proper shadows and borders"""
        # Create surface with alpha for shadows
        total_width = UIMetrics.PANEL_WIDTH + 16
        total_height = UIMetrics.PANEL_HEIGHT + 16
        surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)

        # Draw shadow (subtle, not too strong)
        shadow_offset = 4
        for i in range(3):
            alpha = 30 - i * 10
            shadow_rect = pygame.Rect(
                shadow_offset + i,
                shadow_offset + i,
                UIMetrics.PANEL_WIDTH - i * 2,
                UIMetrics.PANEL_HEIGHT - i * 2
            )
            pygame.draw.rect(
                surface,
                (*UIColors.SHADOW[:3], alpha),
                shadow_rect,
                border_radius=UIMetrics.RADIUS_LARGE
            )

        # Main panel background
        panel_rect = pygame.Rect(0, 0, UIMetrics.PANEL_WIDTH, UIMetrics.PANEL_HEIGHT)
        pygame.draw.rect(
            surface,
            UIColors.PANEL_BG,
            panel_rect,
            border_radius=UIMetrics.RADIUS_LARGE
        )

        # Subtle gradient overlay for depth
        for y in range(UIMetrics.PANEL_HEIGHT // 3):
            alpha = int(15 * (1 - y / (UIMetrics.PANEL_HEIGHT // 3)))
            pygame.draw.line(
                surface,
                (*UIColors.GLOW[:3], alpha),
                (UIMetrics.RADIUS_LARGE, y),
                (UIMetrics.PANEL_WIDTH - UIMetrics.RADIUS_LARGE, y)
            )

        # Border (subtle, professional)
        pygame.draw.rect(
            surface,
            UIColors.PANEL_BORDER,
            panel_rect,
            width=1,
            border_radius=UIMetrics.RADIUS_LARGE
        )

        # Top accent line (adds visual interest)
        accent_rect = pygame.Rect(
            UIMetrics.PADDING_LARGE,
            0,
            UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE * 2,
            2
        )
        pygame.draw.rect(surface, UIColors.BUTTON_ACTIVE, accent_rect)

        return surface

    def draw_header_section(self, surface: pygame.Surface, data: Dict):
        """Draw the header with Part/Time information"""
        header_y = UIMetrics.PADDING

        # Part badge (left aligned)
        badge_width = UIMetrics.GRID_UNIT * 10  # 80px
        badge_height = UIMetrics.BUTTON_HEIGHT - 8  # 24px
        badge_x = UIMetrics.PADDING_LARGE
        badge_y = header_y + 4

        # Badge background with subtle gradient
        badge_rect = pygame.Rect(badge_x, badge_y, badge_width, badge_height)
        pygame.draw.rect(
            surface,
            UIColors.BUTTON_DEFAULT,
            badge_rect,
            border_radius=badge_height // 2  # Pill shape
        )

        # Badge text
        part_text = f"PART {data.get('part', 1)}"
        text_surf = self.font_caption.render(part_text, True, UIColors.TEXT_PRIMARY)
        text_rect = text_surf.get_rect(center=(badge_x + badge_width // 2, badge_y + badge_height // 2))
        surface.blit(text_surf, text_rect)

        # Time display (right aligned)
        time_text = data.get('time', '8:00 AM')
        day_text = f"Day {data.get('day', 1)}"

        time_x = UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE

        # Day
        day_surf = self.font_caption.render(day_text, True, UIColors.TEXT_MUTED)
        day_rect = day_surf.get_rect(topright=(time_x, header_y + 4))
        surface.blit(day_surf, day_rect)

        # Time (below day)
        time_surf = self.font_body.render(time_text, True, UIColors.TEXT_SECONDARY)
        time_rect = time_surf.get_rect(topright=(time_x, header_y + 20))
        surface.blit(time_surf, time_rect)

        # Divider line
        divider_y = header_y + UIMetrics.HEADER_HEIGHT
        pygame.draw.line(
            surface,
            UIColors.PANEL_ACCENT,
            (UIMetrics.PADDING_LARGE, divider_y),
            (UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE, divider_y),
            1
        )

    def draw_objective_content(self, surface: pygame.Surface, data: Dict):
        """Draw the main objective text"""
        content_y = UIMetrics.PADDING + UIMetrics.HEADER_HEIGHT + UIMetrics.PADDING
        content_x = UIMetrics.PADDING_LARGE
        max_width = UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE * 2

        # Title (with proper weight)
        title = data.get('title', 'Current Objective')
        title_surf = self.font_subtitle.render(title, True, UIColors.TEXT_PRIMARY)
        surface.blit(title_surf, (content_x, content_y))

        # Description (wrapped properly)
        desc_y = content_y + 28
        description = data.get('description', '')
        wrapped_lines = self.wrap_text(description, self.font_body, max_width)

        for i, line in enumerate(wrapped_lines[:2]):  # Max 2 lines
            line_surf = self.font_body.render(line, True, UIColors.TEXT_SECONDARY)
            surface.blit(line_surf, (content_x, desc_y + i * 20))

    def draw_progress_section(self, surface: pygame.Surface, progress: float):
        """Draw progress bar with smooth animation"""
        progress_y = UIMetrics.PANEL_HEIGHT - UIMetrics.PADDING_LARGE - UIMetrics.PROGRESS_HEIGHT
        progress_x = UIMetrics.PADDING_LARGE
        progress_width = UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE * 2 - 100  # Leave room for skip button

        # Background track
        track_rect = pygame.Rect(progress_x, progress_y, progress_width, UIMetrics.PROGRESS_HEIGHT)
        pygame.draw.rect(
            surface,
            UIColors.PROGRESS_BG,
            track_rect,
            border_radius=UIMetrics.PROGRESS_HEIGHT // 2
        )

        # Animated fill
        if progress > 0:
            fill_width = int(progress_width * progress)
            fill_rect = pygame.Rect(progress_x, progress_y, fill_width, UIMetrics.PROGRESS_HEIGHT)

            # Main fill
            pygame.draw.rect(
                surface,
                UIColors.PROGRESS_FILL,
                fill_rect,
                border_radius=UIMetrics.PROGRESS_HEIGHT // 2
            )

            # Subtle shine effect on top
            shine_rect = pygame.Rect(progress_x, progress_y, fill_width, UIMetrics.PROGRESS_HEIGHT // 2)
            shine_surf = pygame.Surface((fill_width, UIMetrics.PROGRESS_HEIGHT // 2), pygame.SRCALPHA)
            pygame.draw.rect(
                shine_surf,
                (*UIColors.PROGRESS_SHINE, 60),
                shine_surf.get_rect(),
                border_radius=UIMetrics.PROGRESS_HEIGHT // 4
            )
            surface.blit(shine_surf, (progress_x, progress_y))

        # Progress text
        percent_text = f"{int(progress * 100)}%"
        percent_surf = self.font_small.render(percent_text, True, UIColors.TEXT_MUTED)
        percent_rect = percent_surf.get_rect(
            midleft=(progress_x + progress_width + UIMetrics.PADDING_SMALL, progress_y + UIMetrics.PROGRESS_HEIGHT // 2)
        )
        surface.blit(percent_surf, percent_rect)

    def draw_skip_button(self, surface: pygame.Surface, hover: bool = False):
        """Draw professional skip button"""
        button_width = UIMetrics.GRID_UNIT * 9  # 72px
        button_height = UIMetrics.BUTTON_HEIGHT - 8  # 24px
        button_x = UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE - button_width
        button_y = UIMetrics.PANEL_HEIGHT - UIMetrics.PADDING_LARGE - button_height + 2

        # Button color based on state
        button_color = UIColors.BUTTON_HOVER if hover else UIColors.BUTTON_DEFAULT

        # Button background
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(
            surface,
            button_color,
            button_rect,
            border_radius=UIMetrics.RADIUS_SMALL
        )

        # Button border (subtle)
        pygame.draw.rect(
            surface,
            UIColors.PANEL_ACCENT,
            button_rect,
            width=1,
            border_radius=UIMetrics.RADIUS_SMALL
        )

        # Button text
        text_color = UIColors.TEXT_PRIMARY if hover else UIColors.TEXT_SECONDARY
        button_text = "Skip →" if not hover else "Skip ⟶"
        text_surf = self.font_caption.render(button_text, True, text_color)
        text_rect = text_surf.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        surface.blit(text_surf, text_rect)

        return button_rect

    def wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
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

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def show(self):
        """Animate panel in"""
        self.panel_slide.target = UIMetrics.MARGIN
        self.panel_alpha.target = 255

    def hide(self):
        """Animate panel out"""
        self.panel_slide.target = -UIMetrics.PANEL_HEIGHT
        self.panel_alpha.target = 0

    def update(self, dt: float):
        """Update animations"""
        self.panel_slide.update(dt)
        self.panel_alpha.update(dt)
        self.progress_animation.update(dt)

    def draw(self, screen: pygame.Surface, data: Dict):
        """Draw the complete objective UI"""
        # Update animation for new progress
        if data.get('progress', 0) != self.last_progress:
            self.progress_animation.target = data.get('progress', 0)
            self.last_progress = data.get('progress', 0)

        # Create or get cached panel
        if 'panel' not in self.cache:
            self.cache['panel'] = self.create_panel_surface()

        panel_surface = self.cache['panel'].copy()

        # Draw all sections
        self.draw_header_section(panel_surface, data)
        self.draw_objective_content(panel_surface, data)
        self.draw_progress_section(panel_surface, self.progress_animation.value)

        # Check for button hover
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(
            self.panel_x + UIMetrics.PANEL_WIDTH - UIMetrics.PADDING_LARGE - 72,
            self.panel_slide.value + UIMetrics.PANEL_HEIGHT - UIMetrics.PADDING_LARGE - 24 + 2,
            72, 24
        )
        is_hover = button_rect.collidepoint(mouse_pos)

        self.draw_skip_button(panel_surface, is_hover)

        # Set cursor
        if is_hover:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Apply alpha and draw to screen
        panel_surface.set_alpha(int(self.panel_alpha.value))
        screen.blit(panel_surface, (self.panel_x, self.panel_slide.value))

        return button_rect if is_hover else None


class InteractionPrompt:
    """Clean interaction prompt (Press E to...)"""

    def __init__(self):
        self.font = pygame.font.Font(None, 18)
        self.visible = False
        self.alpha = UIAnimation(0, 0)
        self.pulse = 0

    def show(self, text: str):
        """Show prompt with text"""
        self.text = text
        self.visible = True
        self.alpha.target = 255

    def hide(self):
        """Hide prompt"""
        self.visible = False
        self.alpha.target = 0

    def update(self, dt: float):
        """Update animations"""
        self.alpha.update(dt)
        self.pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7

    def draw(self, screen: pygame.Surface, x: int, y: int):
        """Draw the prompt at position"""
        if self.alpha.value <= 0:
            return

        # Calculate dimensions
        padding = UIMetrics.PADDING
        key_size = 28
        text_surf = self.font.render(self.text, True, UIColors.TEXT_PRIMARY)
        total_width = key_size + padding + text_surf.get_width() + padding * 2
        height = 40

        # Center horizontally
        x = x - total_width // 2

        # Create prompt surface
        prompt_surf = pygame.Surface((total_width, height), pygame.SRCALPHA)

        # Background
        bg_alpha = int(self.alpha.value * 0.9)
        pygame.draw.rect(
            prompt_surf,
            (*UIColors.PANEL_BG, bg_alpha),
            prompt_surf.get_rect(),
            border_radius=UIMetrics.RADIUS_MEDIUM
        )

        # Border (pulsing)
        border_alpha = int(self.alpha.value * self.pulse)
        pygame.draw.rect(
            prompt_surf,
            (*UIColors.BUTTON_ACTIVE, border_alpha),
            prompt_surf.get_rect(),
            width=2,
            border_radius=UIMetrics.RADIUS_MEDIUM
        )

        # Key indicator
        key_rect = pygame.Rect(padding, 6, key_size, key_size)
        pygame.draw.rect(
            prompt_surf,
            UIColors.BUTTON_DEFAULT,
            key_rect,
            border_radius=UIMetrics.RADIUS_SMALL
        )
        pygame.draw.rect(
            prompt_surf,
            UIColors.BUTTON_ACTIVE,
            key_rect,
            width=1,
            border_radius=UIMetrics.RADIUS_SMALL
        )

        # E key
        key_surf = self.font.render("E", True, UIColors.TEXT_PRIMARY)
        key_text_rect = key_surf.get_rect(center=(padding + key_size // 2, 20))
        prompt_surf.blit(key_surf, key_text_rect)

        # Prompt text
        prompt_surf.blit(text_surf, (padding + key_size + padding, 11))

        # Draw to screen
        screen.blit(prompt_surf, (x, y))


class NotificationToast:
    """Professional notification system"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.notifications = []
        self.font_title = pygame.font.Font(None, 18)
        self.font_body = pygame.font.Font(None, 16)

    def show(self, title: str, message: str, type: str = 'info'):
        """Add a new notification"""
        notification = {
            'title': title,
            'message': message,
            'type': type,
            'created': time.time(),
            'duration': 4.0,
            'y': UIAnimation(self.screen_height, self.screen_height - 100 - len(self.notifications) * 70),
            'alpha': UIAnimation(0, 255)
        }
        self.notifications.append(notification)

    def update(self, dt: float):
        """Update all notifications"""
        for notif in self.notifications[:]:
            notif['y'].update(dt)
            notif['alpha'].update(dt)

            # Check if expired
            if time.time() - notif['created'] > notif['duration']:
                notif['alpha'].target = 0
                if notif['alpha'].value <= 1:
                    self.notifications.remove(notif)
            elif time.time() - notif['created'] > notif['duration'] - 0.5:
                # Start fading out
                notif['alpha'].target = 0

    def draw(self, screen: pygame.Surface):
        """Draw all active notifications"""
        for i, notif in enumerate(self.notifications):
            if notif['alpha'].value <= 0:
                continue

            # Position
            x = self.screen_width - 320 - UIMetrics.MARGIN
            y = int(notif['y'].value)

            # Create notification surface
            width = 300
            height = 60
            notif_surf = pygame.Surface((width, height), pygame.SRCALPHA)

            # Background
            bg_alpha = int(notif['alpha'].value * 0.95)
            pygame.draw.rect(
                notif_surf,
                (*UIColors.PANEL_BG, bg_alpha),
                notif_surf.get_rect(),
                border_radius=UIMetrics.RADIUS_MEDIUM
            )

            # Type indicator (left border)
            type_colors = {
                'info': UIColors.INFO,
                'success': UIColors.SUCCESS,
                'warning': UIColors.WARNING,
                'error': UIColors.DANGER
            }
            indicator_color = type_colors.get(notif['type'], UIColors.INFO)
            pygame.draw.rect(
                notif_surf,
                indicator_color,
                pygame.Rect(0, 0, 3, height),
                border_top_left_radius=UIMetrics.RADIUS_MEDIUM,
                border_bottom_left_radius=UIMetrics.RADIUS_MEDIUM
            )

            # Icon circle
            icon_x = 20
            icon_y = height // 2
            pygame.draw.circle(notif_surf, indicator_color, (icon_x, icon_y), 8, 2)

            # Title
            title_surf = self.font_title.render(notif['title'], True, UIColors.TEXT_PRIMARY)
            notif_surf.blit(title_surf, (icon_x + 20, 12))

            # Message
            msg_surf = self.font_body.render(notif['message'], True, UIColors.TEXT_SECONDARY)
            notif_surf.blit(msg_surf, (icon_x + 20, 32))

            # Draw to screen
            screen.blit(notif_surf, (x, y))
"""
Premium Scenarios Menu - Refined Professional Design

Design Philosophy - Sophisticated & Clean:
- Refined color palette with subtle blue accents
- Deep elegant dark backgrounds for sophistication
- Subtle multi-layered glows for depth
- Fluid spring animations with natural easing
- Professional glassmorphism with understated elegance
- Clear typography hierarchy with refined accents
- Minimal gradient background for subtle depth
- Premium polish with refined micro-interactions
"""

import pygame
import math
import os
from pathlib import Path
from .progress_manager import get_progress_manager, load_scenario_objectives


class UIColors:
    """Refined Professional Palette - Sophisticated & Clean"""
    # Backgrounds - Deep elegant darks
    PANEL_BG = (16, 18, 22)
    PANEL_BG_LIGHT = (22, 25, 30)
    PANEL_BG_ELEVATED = (28, 32, 38)
    PANEL_BG_HOVER = (35, 40, 48)

    # Frosted glass overlays
    GLASS_LIGHT = (255, 255, 255, 5)
    GLASS_MEDIUM = (255, 255, 255, 8)
    GLASS_STRONG = (255, 255, 255, 12)

    # Borders - Subtle and refined
    BORDER_SUBTLE = (45, 50, 60)
    BORDER_MEDIUM = (60, 68, 80)
    BORDER_ELEVATED = (80, 90, 105)

    # Text - Clean hierarchy
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (200, 205, 215)
    TEXT_TERTIARY = (150, 160, 175)
    TEXT_MUTED = (110, 120, 135)
    TEXT_DISABLED = (70, 75, 85)

    # Accents - Subtle blue
    ACCENT_BLUE = (100, 150, 220)
    ACCENT_BLUE_BRIGHT = (130, 170, 235)
    ACCENT_BLUE_DIM = (70, 110, 180)
    ACCENT_BLUE_GLOW = (100, 150, 220, 40)

    # Status colors
    SUCCESS = (80, 200, 120)
    SUCCESS_BRIGHT = (100, 220, 140)
    SUCCESS_GLOW = (80, 200, 120, 35)
    WARNING = (220, 180, 100)
    DANGER = (220, 100, 100)

    # Special effects
    SHADOW_SOFT = (0, 0, 0, 20)
    SHADOW_MEDIUM = (0, 0, 0, 40)
    SHADOW_STRONG = (0, 0, 0, 80)
    HIGHLIGHT = (255, 255, 255, 15)

    # Locked state
    LOCKED_BG = (18, 20, 24)
    LOCKED_OVERLAY = (12, 14, 18, 220)
    LOCKED_TEXT = (60, 65, 75)


def ease_out_cubic(t):
    """Smooth deceleration curve - Apple's favorite"""
    return 1 - pow(1 - t, 3)


def ease_in_out_cubic(t):
    """Smooth acceleration and deceleration"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def spring_ease(t, tension=0.6):
    """Spring-like animation with natural bounce"""
    return 1 - math.cos(t * math.pi * tension) * (1 - t)


class ScenarioCard:
    """Premium scenario card with Apple-level polish and micro-interactions"""

    CARD_WIDTH = 700
    CARD_HEIGHT_COLLAPSED = 170
    CARD_HEIGHT_EXPANDED = 520  # Spacious layout
    CARD_MARGIN = 20
    CORNER_RADIUS = 16  # Larger, more premium corners

    def __init__(self, scenario_id, scenario_info, y_position, screen_width):
        self.scenario_id = scenario_id
        self.info = scenario_info
        self.screen_width = screen_width

        self.x = (screen_width - self.CARD_WIDTH) // 2
        self.y = y_position
        self.target_y = y_position

        self.is_expanded = False
        self.is_hovered = False
        self.current_height = self.CARD_HEIGHT_COLLAPSED
        self.target_height = self.CARD_HEIGHT_COLLAPSED
        self.hover_glow = 0.0
        self.click_feedback = 0.0
        self.expand_progress = 0.0
        self.pulse_time = 0.0

        # Play button rect (updated in draw)
        self.play_button_rect = pygame.Rect(0, 0, 100, 32)

        # Objectives list (loaded on first expand)
        self.objectives = None
        self.objectives_scroll_offset = 0
        self.max_objectives_scroll = 0

        self.background_image = None
        self._load_background_image()

        self.font_title = None
        self.font_subtitle = None
        self.font_body = None
        self.font_small = None
        self.font_badge = None

    def _load_background_image(self):
        """Load scenario-specific background image"""
        project_root = Path(__file__).parent.parent.parent
        paths = [
            project_root / f"assets/scenarios/scenario_{self.scenario_id}.png",
            project_root / f"assets/scenarios/part{self.scenario_id}_bg.png",
        ]
        for path in paths:
            if path.exists():
                try:
                    img = pygame.image.load(str(path)).convert()
                    self.background_image = pygame.transform.scale(
                        img, (self.CARD_WIDTH, self.CARD_HEIGHT_EXPANDED)
                    )
                    break
                except pygame.error:
                    pass

    def _init_fonts(self):
        if self.font_title is None:
            self.font_title = pygame.font.Font(None, 38)
            self.font_subtitle = pygame.font.Font(None, 26)
            self.font_body = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 18)
            self.font_badge = pygame.font.Font(None, 28)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.CARD_WIDTH, int(self.current_height))

    def update(self, dt, scroll_offset=0):
        self.pulse_time += dt

        # Smooth height transition with spring easing
        height_diff = self.target_height - self.current_height
        ease_factor = min(dt * 12, 1.0)  # Faster, snappier
        self.current_height += height_diff * ease_factor

        # Expand progress with smooth easing
        target_expand = 1.0 if self.is_expanded else 0.0
        expand_diff = target_expand - self.expand_progress
        self.expand_progress += expand_diff * min(dt * 10, 1.0)

        # Hover glow with quick response (Apple-style responsiveness)
        target_glow = 1.0 if self.is_hovered else 0.0
        glow_diff = target_glow - self.hover_glow
        glow_speed = 15 if target_glow > self.hover_glow else 8  # Faster in, slower out
        self.hover_glow += glow_diff * min(dt * glow_speed, 1.0)

        # Click feedback with natural decay
        if self.click_feedback > 0:
            self.click_feedback -= dt * 4.5
            self.click_feedback = max(0, self.click_feedback)

    def toggle_expanded(self):
        self.is_expanded = not self.is_expanded
        self.target_height = self.CARD_HEIGHT_EXPANDED if self.is_expanded else self.CARD_HEIGHT_COLLAPSED
        self.objectives_scroll_offset = 0  # Reset scroll when toggling

        # Load objectives on first expand
        if self.is_expanded and self.objectives is None:
            self.objectives = load_scenario_objectives(self.scenario_id)
            # Calculate max scroll based on number of objectives
            obj_height = len(self.objectives) * 32  # 32px per objective
            visible_height = self.CARD_HEIGHT_EXPANDED - self.CARD_HEIGHT_COLLAPSED - 100
            self.max_objectives_scroll = max(0, obj_height - visible_height)

    def scroll_objectives(self, amount):
        """Scroll the objectives list within the expanded card"""
        if self.is_expanded and self.max_objectives_scroll > 0:
            self.objectives_scroll_offset += amount
            self.objectives_scroll_offset = max(0, min(self.max_objectives_scroll, self.objectives_scroll_offset))
            return True  # Consumed the scroll
        return False

    def draw(self, screen, scroll_offset=0):
        self._init_fonts()

        draw_y = self.y - scroll_offset
        rect = pygame.Rect(self.x, draw_y, self.CARD_WIDTH, int(self.current_height))

        if rect.bottom < 0 or rect.top > screen.get_height():
            return

        is_unlocked = self.info.get("unlocked", False)

        # Draw shadow
        self._draw_shadow(screen, rect)

        # Draw card
        if is_unlocked:
            self._draw_unlocked_card(screen, rect)
        else:
            self._draw_locked_card(screen, rect)

        # Hover/click effects
        self._draw_effects(screen, rect, is_unlocked)

    def _draw_shadow(self, screen, rect):
        """Draw multi-layered soft shadow for premium depth"""
        # Apple uses multiple shadow layers for depth
        # Layer 1: Soft ambient shadow
        shadow1 = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(shadow1, UIColors.SHADOW_SOFT,
                        (0, 0, rect.width + 40, rect.height + 40),
                        border_radius=self.CORNER_RADIUS + 4)
        screen.blit(shadow1, (rect.x - 20, rect.y - 18))

        # Layer 2: Medium definition shadow
        shadow2 = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow2, UIColors.SHADOW_MEDIUM,
                        (0, 0, rect.width + 20, rect.height + 20),
                        border_radius=self.CORNER_RADIUS + 2)
        screen.blit(shadow2, (rect.x - 10, rect.y - 8))

        # Layer 3: Sharp contact shadow (elevated on hover)
        shadow_offset = 2 if not self.is_hovered else 4
        shadow3 = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        shadow_alpha = UIColors.SHADOW_MEDIUM if not self.is_hovered else UIColors.SHADOW_SOFT
        pygame.draw.rect(shadow3, shadow_alpha,
                        (0, 0, rect.width + 8, rect.height + 8),
                        border_radius=self.CORNER_RADIUS + 1)
        screen.blit(shadow3, (rect.x - 4, rect.y + shadow_offset))

    def _draw_unlocked_card(self, screen, rect):
        """Draw unlocked card with glassmorphism and premium styling"""
        # Main card surface with alpha for glassmorphism
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Base background - Elevated on hover
        base_color = UIColors.PANEL_BG_ELEVATED if self.is_hovered else UIColors.PANEL_BG_LIGHT
        pygame.draw.rect(card_surface, base_color,
                        (0, 0, rect.width, rect.height),
                        border_radius=self.CORNER_RADIUS)

        # Glassmorphism frosted overlay
        glass_alpha = int(18 if self.is_hovered else 12)
        glass_overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_overlay, (255, 255, 255, glass_alpha),
                        (0, 0, rect.width, rect.height),
                        border_radius=self.CORNER_RADIUS)
        card_surface.blit(glass_overlay, (0, 0))

        # Background image with subtle visibility
        if self.background_image:
            img_height = min(int(rect.height), self.background_image.get_height())
            img_section = self.background_image.subsurface((0, 0, rect.width, img_height))
            img_copy = img_section.copy()
            img_copy.set_alpha(25)  # Very subtle
            card_surface.blit(img_copy, (0, 0))

        # Refined accent bar (subtle blue for active, green for completed)
        is_completed = self.info.get("completed")
        accent_color = UIColors.SUCCESS if is_completed else UIColors.ACCENT_BLUE

        # Subtle glow for depth
        glow_rect = pygame.Rect(0, 0, rect.width, 6)
        glow_surface = pygame.Surface((rect.width, 6), pygame.SRCALPHA)
        for i in range(6):
            alpha = int(30 * (1 - i / 6))
            pygame.draw.line(glow_surface, (*accent_color, alpha),
                           (0, i), (rect.width, i))
        card_surface.blit(glow_surface, (0, 0))

        # Clean accent bar
        pygame.draw.rect(card_surface, accent_color,
                        (0, 0, rect.width, 3),
                        border_radius=self.CORNER_RADIUS)

        # Subtle inner highlight (top edge)
        highlight_gradient = pygame.Surface((rect.width, 60), pygame.SRCALPHA)
        for i in range(60):
            alpha = int(UIColors.HIGHLIGHT[3] * (1 - i / 60) * 0.6)
            pygame.draw.line(highlight_gradient, (255, 255, 255, alpha),
                           (0, i), (rect.width, i))
        card_surface.blit(highlight_gradient, (0, 4))

        screen.blit(card_surface, rect.topleft)

        # Draw content
        self._draw_unlocked_content(screen, rect)

        # Premium border - Multi-layered for depth
        # Outer border (subtle)
        outer_color = UIColors.BORDER_SUBTLE
        pygame.draw.rect(screen, outer_color,
                        rect.inflate(2, 2), 1, border_radius=self.CORNER_RADIUS + 1)

        # Main border - subtle and refined
        if is_completed:
            border_color = UIColors.SUCCESS
            border_width = 2
        elif self.is_hovered:
            border_color = UIColors.ACCENT_BLUE_BRIGHT
            border_width = 2
        else:
            border_color = UIColors.BORDER_MEDIUM
            border_width = 1

        pygame.draw.rect(screen, border_color, rect, border_width,
                        border_radius=self.CORNER_RADIUS)

    def _draw_unlocked_content(self, screen, rect):
        """Draw content for unlocked card with premium typography and layout"""
        padding = 28  # More breathing room
        content_x = rect.x + padding
        content_y = rect.y + padding + 4  # Account for accent bar

        # Refined badge (subtle blue for active, green for completed)
        badge_width = 76
        badge_height = 30
        badge_rect = pygame.Rect(content_x, content_y, badge_width, badge_height)
        is_completed = self.info.get("completed")
        badge_color = UIColors.SUCCESS if is_completed else UIColors.ACCENT_BLUE

        # Subtle glow on hover
        if self.is_hovered:
            glow_badge = badge_rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_badge.width, glow_badge.height), pygame.SRCALPHA)
            glow_color = UIColors.SUCCESS_GLOW if is_completed else UIColors.ACCENT_BLUE_GLOW
            pygame.draw.rect(glow_surface, glow_color,
                           (0, 0, glow_badge.width, glow_badge.height),
                           border_radius=glow_badge.height // 2)
            screen.blit(glow_surface, glow_badge.topleft)

        # Badge background
        badge_surface = pygame.Surface((badge_width, badge_height), pygame.SRCALPHA)
        pygame.draw.rect(badge_surface, badge_color,
                        (0, 0, badge_width, badge_height),
                        border_radius=badge_height // 2)

        # Badge shine effect (top half)
        shine_surface = pygame.Surface((badge_width, badge_height // 2), pygame.SRCALPHA)
        pygame.draw.rect(shine_surface, (255, 255, 255, 30),
                        (0, 0, badge_width, badge_height // 2),
                        border_radius=badge_height // 2)
        badge_surface.blit(shine_surface, (0, 0))

        screen.blit(badge_surface, badge_rect.topleft)

        # Badge text - white text on vibrant background
        badge_font = pygame.font.Font(None, 24)
        badge_text = badge_font.render(f"Part {self.scenario_id}", True, (255, 255, 255))
        badge_text_rect = badge_text.get_rect(center=badge_rect.center)
        screen.blit(badge_text, badge_text_rect)

        # Title
        title_x = content_x + badge_width + 16
        title_text = self.font_title.render(self.info["title"], True, UIColors.TEXT_PRIMARY)
        screen.blit(title_text, (title_x, content_y + 2))

        # Subtitle
        subtitle_text = self.font_subtitle.render(self.info["subtitle"], True, UIColors.TEXT_SECONDARY)
        screen.blit(subtitle_text, (title_x, content_y + 32))

        # Refined button (subtle blue for active, green for completed)
        btn_width = 110
        btn_height = 38
        btn_x = rect.right - padding - btn_width
        btn_y = content_y
        self.play_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

        has_progress = self.info.get("started") and self.info.get("objectives_completed", 0) > 0

        # Professional buttons
        if is_completed:
            btn_color = UIColors.SUCCESS
            btn_text_str = "Replay"
        elif has_progress:
            btn_color = UIColors.ACCENT_BLUE
            btn_text_str = "Continue"
        else:
            btn_color = UIColors.ACCENT_BLUE
            btn_text_str = "Start"

        # Subtle glow on hover
        glow_intensity = 45 if self.is_hovered else 25
        glow_rect = self.play_button_rect.inflate(12, 12)
        glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        glow_color = UIColors.SUCCESS_GLOW if is_completed else UIColors.ACCENT_BLUE_GLOW
        pygame.draw.rect(glow_surface, glow_color,
                        (0, 0, glow_rect.width, glow_rect.height),
                        border_radius=10)
        screen.blit(glow_surface, glow_rect.topleft)

        # Button background
        btn_surface = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, btn_color,
                        (0, 0, btn_width, btn_height),
                        border_radius=8)

        # Top shine gradient (Apple's signature button sheen)
        shine_height = btn_height // 2 + 2
        shine_surface = pygame.Surface((btn_width, shine_height), pygame.SRCALPHA)
        for i in range(shine_height):
            alpha = int(45 * (1 - i / shine_height))
            pygame.draw.line(shine_surface, (255, 255, 255, alpha),
                           (0, i), (btn_width, i))
        btn_surface.blit(shine_surface, (0, 0))

        # Subtle inner shadow at bottom for depth
        shadow_height = 3
        for i in range(shadow_height):
            alpha = int(30 * (i / shadow_height))
            pygame.draw.line(btn_surface, (0, 0, 0, alpha),
                           (0, btn_height - shadow_height + i),
                           (btn_width, btn_height - shadow_height + i))

        screen.blit(btn_surface, self.play_button_rect.topleft)

        # Button text - white on vibrant background
        btn_font = pygame.font.Font(None, 26)
        btn_text = btn_font.render(btn_text_str, True, (255, 255, 255))  # White text
        btn_text_rect = btn_text.get_rect(center=self.play_button_rect.center)
        screen.blit(btn_text, btn_text_rect)

        # Status label below button
        status_y = btn_y + btn_height + 4
        if is_completed:
            status_color = UIColors.SUCCESS
            status_str = "COMPLETE"
        elif has_progress:
            status_color = UIColors.TEXT_SECONDARY
            done = self.info.get("objectives_completed", 0)
            total = self.info.get("objectives_count", 0)
            status_str = f"{done}/{total} done"
        else:
            status_color = UIColors.TEXT_MUTED
            status_str = "NEW"

        status_text = self.font_small.render(status_str, True, status_color)
        status_rect = status_text.get_rect(centerx=self.play_button_rect.centerx, y=status_y)
        screen.blit(status_text, status_rect)

        # Progress section
        progress_y = content_y + 70
        self._draw_progress_bar(screen, rect, progress_y, padding)

        # Premium expand indicator with animated cue
        expand_y = rect.y + self.CARD_HEIGHT_COLLAPSED - 32
        if not self.is_expanded:
            # Pulsing glow for unexpanded state
            pulse = math.sin(self.pulse_time * 2.5) * 0.5 + 0.5
            expand_alpha = int(160 + pulse * 70)

            # Subtle background pill
            pill_width = 160
            pill_height = 24
            pill_rect = pygame.Rect(rect.centerx - pill_width // 2, expand_y,
                                   pill_width, pill_height)

            # Pill glow
            if self.is_hovered:
                glow_pill = pill_rect.inflate(8, 8)
                glow_surface = pygame.Surface((glow_pill.width, glow_pill.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 255, 255, int(15 * pulse)),
                               (0, 0, glow_pill.width, glow_pill.height),
                               border_radius=pill_height // 2)
                screen.blit(glow_surface, glow_pill.topleft)

            # Pill background
            pill_surface = pygame.Surface((pill_width, pill_height), pygame.SRCALPHA)
            pygame.draw.rect(pill_surface, (255, 255, 255, 8),
                           (0, 0, pill_width, pill_height),
                           border_radius=pill_height // 2)
            screen.blit(pill_surface, pill_rect.topleft)

            # Arrow and text
            arrow_font = pygame.font.Font(None, 20)
            arrow = "▼ View objectives"
            expand_text = arrow_font.render(arrow, True, UIColors.TEXT_TERTIARY)
            expand_text.set_alpha(expand_alpha)
        else:
            # Collapsed state - subtle
            arrow_font = pygame.font.Font(None, 20)
            arrow = "▲ Hide objectives"
            expand_text = arrow_font.render(arrow, True, UIColors.TEXT_MUTED)

        expand_rect = expand_text.get_rect(centerx=rect.centerx, y=expand_y + 2)
        screen.blit(expand_text, expand_rect)

        # Expanded content
        if self.expand_progress > 0.1:
            self._draw_expanded_content(screen, rect, content_x, padding)

    def _draw_progress_bar(self, screen, rect, y, padding):
        """Draw premium progress bar with smooth animations"""
        bar_x = rect.x + padding
        bar_width = rect.width - padding * 2 - 90
        bar_height = 8  # Slightly thinner, more refined

        # Track background (inset look)
        track_rect = pygame.Rect(bar_x, y, bar_width, bar_height)

        # Inner shadow for track
        track_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(track_surface, (0, 0, 0, 60),
                        (0, 0, bar_width, bar_height),
                        border_radius=bar_height // 2)
        screen.blit(track_surface, track_rect.topleft)

        # Track base
        pygame.draw.rect(screen, UIColors.PANEL_BG,
                        track_rect, border_radius=bar_height // 2)

        # Progress fill - refined colors
        completion = self.info.get("completion_percentage", 0)
        if completion > 0:
            fill_width = max(bar_height, int((completion / 100) * bar_width))
            fill_color = UIColors.SUCCESS if completion >= 100 else UIColors.ACCENT_BLUE

            # Subtle glow matching fill
            glow_rect = pygame.Rect(bar_x - 2, y - 2, fill_width + 4, bar_height + 4)
            glow_surface = pygame.Surface((fill_width + 4, bar_height + 4), pygame.SRCALPHA)
            glow_color = UIColors.SUCCESS_GLOW if completion >= 100 else UIColors.ACCENT_BLUE_GLOW
            pygame.draw.rect(glow_surface, glow_color,
                           (0, 0, fill_width + 4, bar_height + 4),
                           border_radius=(bar_height + 4) // 2)
            screen.blit(glow_surface, glow_rect.topleft)

            # Fill base
            fill_rect = pygame.Rect(bar_x, y, fill_width, bar_height)
            pygame.draw.rect(screen, fill_color, fill_rect,
                           border_radius=bar_height // 2)

            # Top shine gradient
            shine_height = bar_height // 2
            shine_surface = pygame.Surface((fill_width, shine_height), pygame.SRCALPHA)
            for i in range(shine_height):
                alpha = int(50 * (1 - i / shine_height))
                pygame.draw.line(shine_surface, (255, 255, 255, alpha),
                               (0, i), (fill_width, i))
            screen.blit(shine_surface, (bar_x, y))

            # Animated shimmer effect (subtle)
            if completion < 100:
                shimmer_x = int((math.sin(self.pulse_time * 2) + 1) * 0.5 * (fill_width - 30))
                shimmer_rect = pygame.Rect(bar_x + shimmer_x, y, 30, bar_height)
                shimmer_surface = pygame.Surface((30, bar_height), pygame.SRCALPHA)
                for i in range(30):
                    fade = 1 - abs(i - 15) / 15
                    alpha = int(25 * fade)
                    pygame.draw.line(shimmer_surface, (255, 255, 255, alpha),
                                   (i, 0), (i, bar_height))
                pygame.draw.rect(shimmer_surface, (0, 0, 0, 0),
                               (0, 0, 30, bar_height),
                               border_radius=bar_height // 2)
                screen.blit(shimmer_surface, shimmer_rect, special_flags=pygame.BLEND_RGBA_ADD)

        # Percentage text (cleaner positioning)
        percent_font = pygame.font.Font(None, 22)
        percent_text = percent_font.render(f"{completion:.0f}%", True, UIColors.TEXT_SECONDARY)
        screen.blit(percent_text, (bar_x + bar_width + 14, y - 4))

        # Objectives count (refined)
        done = self.info.get("objectives_completed", 0)
        total = self.info.get("objectives_count", 0)
        count_font = pygame.font.Font(None, 19)
        count_text = count_font.render(f"{done}/{total} objectives", True, UIColors.TEXT_TERTIARY)
        screen.blit(count_text, (bar_x, y + 16))

    def _draw_expanded_content(self, screen, rect, content_x, padding):
        """Draw expanded objectives list with actual game objectives"""
        expand_y = rect.y + self.CARD_HEIGHT_COLLAPSED + 8
        alpha = int(255 * min(self.expand_progress * 1.5, 1.0))

        # Description
        desc = self.info.get("description", "")
        desc_surface = self.font_body.render(desc, True, UIColors.TEXT_SECONDARY)
        desc_surface.set_alpha(alpha)
        screen.blit(desc_surface, (content_x, expand_y))

        # Objectives header with count
        header_y = expand_y + 30
        completed_count = self.info.get("objectives_completed", 0)
        total_count = len(self.objectives) if self.objectives else self.info.get("objectives_count", 0)

        header_str = f"Objectives ({completed_count}/{total_count})"
        header = self.font_subtitle.render(header_str, True, UIColors.TEXT_PRIMARY)
        header.set_alpha(alpha)
        screen.blit(header, (content_x, header_y))

        # Scroll hint if there are many objectives
        if self.max_objectives_scroll > 0:
            scroll_hint = self.font_small.render("Scroll to see more ↕", True, UIColors.TEXT_MUTED)
            scroll_hint.set_alpha(alpha)
            screen.blit(scroll_hint, (rect.right - padding - 120, header_y + 4))

        # Divider line
        divider_y = header_y + 26
        pygame.draw.line(screen, (*UIColors.BORDER_MEDIUM[:3], alpha),
                        (content_x, divider_y),
                        (rect.right - padding, divider_y), 1)

        # Create clipping region for objectives list
        list_y = divider_y + 8
        list_height = rect.bottom - list_y - 16
        list_rect = pygame.Rect(content_x - 4, list_y, rect.width - padding * 2 + 8, list_height)

        # Draw objectives
        if self.objectives:
            obj_y = list_y - self.objectives_scroll_offset

            for i, obj in enumerate(self.objectives):
                # Skip if above visible area
                if obj_y + 30 < list_y:
                    obj_y += 32
                    continue
                # Stop if below visible area
                if obj_y > rect.bottom - 16:
                    break

                is_done = i < completed_count
                is_current = i == completed_count  # This is the next objective to complete

                # Row background - highlight current objective with subtle blue glow
                row_bg = pygame.Surface((rect.width - padding * 2, 30), pygame.SRCALPHA)
                if is_current:
                    # Highlight current objective with subtle blue glow
                    pulse = int(15 + math.sin(self.pulse_time * 3) * 8)
                    pygame.draw.rect(row_bg, (*UIColors.ACCENT_BLUE, int((30 + pulse) * self.expand_progress)),
                                   (0, 0, rect.width - padding * 2, 30), border_radius=4)
                elif i % 2 == 0:
                    pygame.draw.rect(row_bg, (*UIColors.PANEL_BG[:3], int(40 * self.expand_progress)),
                                   (0, 0, rect.width - padding * 2, 30), border_radius=4)
                screen.blit(row_bg, (content_x, obj_y))

                # Current indicator arrow - refined blue
                if is_current:
                    arrow = self.font_body.render("▶", True, UIColors.ACCENT_BLUE_BRIGHT)
                    arrow.set_alpha(alpha)
                    screen.blit(arrow, (content_x + 2, obj_y + 5))

                # Objective number - refined colors
                num_color = UIColors.SUCCESS if is_done else (UIColors.ACCENT_BLUE if is_current else UIColors.TEXT_MUTED)
                num_text = self.font_small.render(f"{i + 1}.", True, num_color)
                num_text.set_alpha(alpha)
                screen.blit(num_text, (content_x + (18 if is_current else 4), obj_y + 6))

                # Checkbox - refined blue/green
                cb_size = 16
                cb_x = content_x + 38
                cb_rect = pygame.Rect(cb_x, obj_y + 6, cb_size, cb_size)

                if is_done:
                    # Filled green checkbox for completed
                    pygame.draw.rect(screen, (*UIColors.SUCCESS, alpha), cb_rect, border_radius=3)
                    check = self.font_small.render("✓", True, (255, 255, 255))  # White checkmark
                    check.set_alpha(alpha)
                    check_rect = check.get_rect(center=cb_rect.center)
                    screen.blit(check, check_rect)
                elif is_current:
                    # Pulsing subtle blue border for current
                    pulse_alpha = int(160 + math.sin(self.pulse_time * 4) * 60)
                    pygame.draw.rect(screen, (*UIColors.ACCENT_BLUE_BRIGHT, min(pulse_alpha, alpha)), cb_rect, 2, border_radius=3)
                else:
                    # Subtle border for pending
                    pygame.draw.rect(screen, (*UIColors.BORDER_MEDIUM, alpha), cb_rect, 2, border_radius=3)

                # Objective title - refined hierarchy
                title = obj.get("title", "Unknown")
                max_title_width = rect.width - padding * 2 - 80
                if is_done:
                    title_color = UIColors.SUCCESS  # Green for completed
                elif is_current:
                    title_color = UIColors.ACCENT_BLUE_BRIGHT  # Refined blue for current
                else:
                    title_color = UIColors.TEXT_TERTIARY  # Muted for pending

                title_surface = self.font_body.render(title, True, title_color)

                # Truncate title if needed
                if title_surface.get_width() > max_title_width:
                    while title_surface.get_width() > max_title_width - 20 and len(title) > 10:
                        title = title[:-1]
                    title += "..."
                    title_surface = self.font_body.render(title, True, title_color)

                title_surface.set_alpha(alpha)
                screen.blit(title_surface, (cb_x + cb_size + 10, obj_y + 6))

                obj_y += 32

        # Scroll indicators
        if self.max_objectives_scroll > 0:
            # Top fade if scrolled down
            if self.objectives_scroll_offset > 0:
                fade = pygame.Surface((rect.width - padding * 2, 20), pygame.SRCALPHA)
                for i in range(20):
                    fade_alpha = int(200 * (1 - i / 20) * self.expand_progress)
                    pygame.draw.line(fade, (*UIColors.PANEL_BG_LIGHT[:3], fade_alpha),
                                   (0, i), (rect.width - padding * 2, i))
                screen.blit(fade, (content_x, list_y))

            # Bottom fade if more content below
            if self.objectives_scroll_offset < self.max_objectives_scroll:
                fade = pygame.Surface((rect.width - padding * 2, 20), pygame.SRCALPHA)
                for i in range(20):
                    fade_alpha = int(200 * (i / 20) * self.expand_progress)
                    pygame.draw.line(fade, (*UIColors.PANEL_BG_LIGHT[:3], fade_alpha),
                                   (0, i), (rect.width - padding * 2, i))
                screen.blit(fade, (content_x, rect.bottom - 36))

    def _draw_locked_card(self, screen, rect):
        """Draw locked scenario card"""
        # Dark background
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, UIColors.LOCKED_BG,
                        (0, 0, rect.width, rect.height),
                        border_radius=self.CORNER_RADIUS)
        screen.blit(card_surface, rect.topleft)

        padding = 24
        content_x = rect.x + padding
        content_y = rect.y + padding

        # Lock icon area
        lock_size = 50
        lock_rect = pygame.Rect(content_x, content_y, lock_size, lock_size)
        pygame.draw.rect(screen, UIColors.PANEL_BG, lock_rect, border_radius=10)

        # Simple lock icon
        lock_body = pygame.Rect(content_x + 15, content_y + 25, 20, 18)
        pygame.draw.rect(screen, UIColors.TEXT_MUTED, lock_body, border_radius=3)
        pygame.draw.arc(screen, UIColors.TEXT_MUTED,
                       (content_x + 17, content_y + 12, 16, 16),
                       0, math.pi, 3)

        # Title (dimmed)
        title_x = content_x + lock_size + 16
        title = self.font_title.render(self.info["title"], True, UIColors.TEXT_DISABLED)
        screen.blit(title, (title_x, content_y + 5))

        # Locked label
        locked_label = self.font_subtitle.render("LOCKED", True, UIColors.DANGER)
        screen.blit(locked_label, (title_x, content_y + 38))

        # Unlock requirement
        pm = get_progress_manager()
        unlock_msg = pm.get_unlock_status_message(self.scenario_id)
        unlock_text = self.font_body.render(unlock_msg, True, UIColors.TEXT_MUTED)
        screen.blit(unlock_text, (title_x, content_y + 70))

        # Dark overlay
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, UIColors.LOCKED_OVERLAY,
                        (0, 0, rect.width, rect.height),
                        border_radius=self.CORNER_RADIUS)
        screen.blit(overlay, rect.topleft)

        # Border
        pygame.draw.rect(screen, UIColors.PANEL_BG, rect, 2, border_radius=self.CORNER_RADIUS)

    def _draw_effects(self, screen, rect, is_unlocked):
        """Draw refined hover effects - subtle and professional"""
        if self.hover_glow > 0.05 and is_unlocked:
            # Smooth eased glow intensity
            eased_glow = ease_out_cubic(self.hover_glow)
            glow_alpha = int(35 * eased_glow)

            # Multi-layer subtle glow for depth
            # Outer soft glow
            outer_glow = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(outer_glow, (100, 130, 180, glow_alpha // 3),
                           (0, 0, rect.width + 20, rect.height + 20),
                           border_radius=self.CORNER_RADIUS + 3)
            screen.blit(outer_glow, (rect.x - 10, rect.y - 10))

            # Inner glow
            inner_glow = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(inner_glow, (120, 160, 210, glow_alpha // 2),
                           (0, 0, rect.width + 10, rect.height + 10),
                           border_radius=self.CORNER_RADIUS + 2)
            screen.blit(inner_glow, (rect.x - 5, rect.y - 5))

        # Refined click feedback with spring animation
        if self.click_feedback > 0:
            # Spring-eased feedback for natural feel
            spring_feedback = spring_ease(1 - self.click_feedback)
            feedback_alpha = int(50 * self.click_feedback)

            # Subtle flash
            feedback_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(feedback_surface, (255, 255, 255, feedback_alpha),
                           (0, 0, rect.width, rect.height),
                           border_radius=self.CORNER_RADIUS)
            screen.blit(feedback_surface, rect.topleft)


class ImprovedScenariosMenu:
    """Refined Professional Scenarios Menu

    Features:
    - Sophisticated color scheme with subtle blue accents
    - Deep elegant dark backgrounds
    - Subtle multi-layered hover glows for depth
    - Fluid spring animations with natural easing
    - Professional glassmorphism with refined elegance
    - Clear typography hierarchy
    - Minimal radial gradient background
    - Premium micro-interactions with understated polish
    """

    HEADER_HEIGHT = 90
    FOOTER_HEIGHT = 60
    SCROLL_SPEED = 50

    def __init__(self, screen_width=1536, screen_height=1024):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.progress_manager = get_progress_manager()

        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_velocity = 0

        self.cards = []
        self._create_cards()

        self.hovered_card_index = -1
        self.hover_back_button = False
        self.back_button_rect = pygame.Rect(40, 25, 110, 40)

        self.font_title = None
        self.font_button = None
        self.animation_time = 0

    def _create_cards(self):
        self.cards = []
        scenarios = self.progress_manager.get_all_scenarios_with_progress()

        y_position = self.HEADER_HEIGHT + 24
        for scenario in scenarios:
            card = ScenarioCard(
                scenario["scenario_id"],
                scenario,
                y_position,
                self.screen_width
            )
            self.cards.append(card)
            y_position += ScenarioCard.CARD_HEIGHT_COLLAPSED + ScenarioCard.CARD_MARGIN

        content_height = y_position + self.FOOTER_HEIGHT
        visible_height = self.screen_height - self.HEADER_HEIGHT
        self.max_scroll = max(0, content_height - visible_height)

    def refresh_cards(self):
        """Refresh cards with latest progress"""
        scenarios = self.progress_manager.get_all_scenarios_with_progress()
        for i, scenario in enumerate(scenarios):
            if i < len(self.cards):
                self.cards[i].info = scenario

    def _init_fonts(self):
        if self.font_title is None:
            self.font_title = pygame.font.Font(None, 48)
            self.font_button = pygame.font.Font(None, 26)

    def handle_events(self, frame_events):
        for input_event in frame_events:
            event = input_event.event
            action = self.handle_event(event)
            if action:
                return action
        return None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(pygame.mouse.get_pos())

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1:
                return self._handle_click(mouse_pos)
            elif event.button == 4:  # Scroll up
                if not self._handle_card_scroll(-30, mouse_pos):
                    self.scroll_offset = max(0, self.scroll_offset - self.SCROLL_SPEED)
            elif event.button == 5:  # Scroll down
                if not self._handle_card_scroll(30, mouse_pos):
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.SCROLL_SPEED)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            scroll_amount = -event.y * 30
            if not self._handle_card_scroll(scroll_amount, mouse_pos):
                self.scroll_offset -= event.y * self.SCROLL_SPEED
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back_to_menu"
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - self.SCROLL_SPEED)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + self.SCROLL_SPEED)
            elif pygame.K_1 <= event.key <= pygame.K_5:
                return self._try_start_scenario(event.key - pygame.K_0)

        return None

    def _handle_card_scroll(self, amount, mouse_pos):
        """Handle scrolling within an expanded card's objectives list"""
        if mouse_pos[1] <= self.HEADER_HEIGHT:
            return False

        for card in self.cards:
            if card.is_expanded:
                card_rect = card.get_rect()
                card_rect.y -= self.scroll_offset
                if card_rect.collidepoint(mouse_pos):
                    # Check if mouse is in the objectives area (below collapsed height)
                    objectives_area_y = card_rect.y + ScenarioCard.CARD_HEIGHT_COLLAPSED
                    if mouse_pos[1] > objectives_area_y:
                        return card.scroll_objectives(amount)
        return False

    def _handle_mouse_motion(self, mouse_pos):
        self.hover_back_button = self.back_button_rect.collidepoint(mouse_pos)

        self.hovered_card_index = -1
        for i, card in enumerate(self.cards):
            card_rect = card.get_rect()
            card_rect.y -= self.scroll_offset
            card.is_hovered = card_rect.collidepoint(mouse_pos) and mouse_pos[1] > self.HEADER_HEIGHT
            if card.is_hovered:
                self.hovered_card_index = i
        return None

    def _handle_click(self, mouse_pos):
        if self.back_button_rect.collidepoint(mouse_pos):
            return "back_to_menu"

        if mouse_pos[1] > self.HEADER_HEIGHT:
            for card in self.cards:
                card_rect = card.get_rect()
                card_rect.y -= self.scroll_offset

                if card_rect.collidepoint(mouse_pos):
                    card.click_feedback = 1.0

                    if card.info.get("unlocked"):
                        # Check if play button was clicked
                        play_btn = card.play_button_rect.copy()
                        play_btn.y -= self.scroll_offset
                        if play_btn.collidepoint(mouse_pos):
                            return self._start_scenario(card.scenario_id)

                        # Check expand zone (bottom area of collapsed card)
                        collapse_zone_y = card_rect.y + ScenarioCard.CARD_HEIGHT_COLLAPSED - 35
                        if mouse_pos[1] > collapse_zone_y or card.is_expanded:
                            card.toggle_expanded()
                            self._recalculate_card_positions()
                        else:
                            # Clicking anywhere else on unlocked card starts it
                            return self._start_scenario(card.scenario_id)
                    break
        return None

    def _recalculate_card_positions(self):
        y_position = self.HEADER_HEIGHT + 24
        for card in self.cards:
            card.y = y_position
            card.target_y = y_position
            y_position += int(card.current_height) + ScenarioCard.CARD_MARGIN

        content_height = y_position + self.FOOTER_HEIGHT
        visible_height = self.screen_height - self.HEADER_HEIGHT
        self.max_scroll = max(0, content_height - visible_height)

    def _try_start_scenario(self, num):
        if 1 <= num <= len(self.cards):
            card = self.cards[num - 1]
            if card.info.get("unlocked"):
                return self._start_scenario(num)
        return None

    def _start_scenario(self, scenario_id):
        self.progress_manager.mark_scenario_started(scenario_id)
        return f"start_part{scenario_id}"

    def update(self, dt):
        self.animation_time += dt

        for card in self.cards:
            card.update(dt, self.scroll_offset)

        self._recalculate_card_positions()

        if abs(self.scroll_velocity) > 0.1:
            self.scroll_offset += self.scroll_velocity
            self.scroll_velocity *= 0.9
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))

    def draw(self, screen):
        self._init_fonts()
        self.update(0.016)

        # Clean dark background
        screen.fill(UIColors.PANEL_BG)

        # Subtle radial gradient for depth
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        glow_radius = 500
        glow_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Very subtle glow from center
        for i in range(60):
            radius = glow_radius - i * 8
            alpha = int(5 * (1 - i / 60))
            if radius > 0 and alpha > 0:
                pygame.draw.circle(glow_surface, (80, 100, 140, alpha),
                                 (center_x, center_y), radius, 1)
        screen.blit(glow_surface, (0, 0))

        # Minimal dot grid pattern
        dot_spacing = 40
        dot_size = 1
        max_radius = math.sqrt(center_x**2 + center_y**2)

        for y in range(0, self.screen_height, dot_spacing):
            for x in range(0, self.screen_width, dot_spacing):
                # Distance from center for radial fade
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                fade = 1 - (dist / max_radius) * 0.3
                alpha = int(12 * fade)

                # Subtle neutral dots
                dot_color = (80, 90, 110, alpha)
                pygame.draw.circle(screen, dot_color, (x, y), dot_size)

        # Draw cards
        for card in self.cards:
            card.draw(screen, self.scroll_offset)

        # Header
        self._draw_header(screen)

        # Scroll indicators
        self._draw_scroll_indicators(screen)

    def _draw_header(self, screen):
        """Draw premium header with frosted glass effect"""
        # Frosted glass header background
        header_surface = pygame.Surface((self.screen_width, self.HEADER_HEIGHT), pygame.SRCALPHA)

        # Base color with slight transparency
        for i in range(self.HEADER_HEIGHT):
            if i < self.HEADER_HEIGHT - 20:
                alpha = 245
            else:
                alpha = int(245 * (1 - (i - self.HEADER_HEIGHT + 20) / 20))
            pygame.draw.line(header_surface, (*UIColors.PANEL_BG_LIGHT, alpha),
                           (0, i), (self.screen_width, i))

        # Glassmorphism overlay
        glass_overlay = pygame.Surface((self.screen_width, self.HEADER_HEIGHT), pygame.SRCALPHA)
        for i in range(self.HEADER_HEIGHT):
            alpha = 15 if i < self.HEADER_HEIGHT - 20 else int(15 * (1 - (i - self.HEADER_HEIGHT + 20) / 20))
            pygame.draw.line(glass_overlay, (255, 255, 255, alpha),
                           (0, i), (self.screen_width, i))
        header_surface.blit(glass_overlay, (0, 0))

        screen.blit(header_surface, (0, 0))

        # Refined top accent line
        accent_glow = pygame.Surface((self.screen_width, 6), pygame.SRCALPHA)
        for i in range(6):
            alpha = int(35 * (1 - i / 6))
            pygame.draw.line(accent_glow, (*UIColors.ACCENT_BLUE, alpha),
                           (0, i), (self.screen_width, i))
        screen.blit(accent_glow, (0, 0))
        pygame.draw.line(screen, UIColors.ACCENT_BLUE, (0, 0), (self.screen_width, 0), 3)

        # Title with subtle shadow for depth
        title_font = pygame.font.Font(None, 52)
        title_text = "Choose Your Story"

        # Title shadow
        title_shadow = title_font.render(title_text, True, (0, 0, 0))
        title_shadow.set_alpha(60)
        shadow_rect = title_shadow.get_rect(centerx=self.screen_width // 2 + 2,
                                           centery=self.HEADER_HEIGHT // 2 + 2)
        screen.blit(title_shadow, shadow_rect)

        # Title main
        title = title_font.render(title_text, True, UIColors.TEXT_PRIMARY)
        title_rect = title.get_rect(centerx=self.screen_width // 2,
                                   centery=self.HEADER_HEIGHT // 2)
        screen.blit(title, title_rect)

        # Premium Back button with glassmorphism
        btn_rect = self.back_button_rect

        # Button glow on hover - subtle blue
        if self.hover_back_button:
            glow_rect = btn_rect.inflate(12, 12)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, UIColors.ACCENT_BLUE_GLOW,
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=11)
            screen.blit(glow_surface, glow_rect.topleft)

        # Button background
        btn_color = UIColors.PANEL_BG_ELEVATED if self.hover_back_button else UIColors.PANEL_BG_LIGHT
        btn_surface = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surface, btn_color,
                        (0, 0, btn_rect.width, btn_rect.height),
                        border_radius=10)

        # Glass overlay
        glass_btn = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_btn, (255, 255, 255, 12),
                        (0, 0, btn_rect.width, btn_rect.height),
                        border_radius=10)
        btn_surface.blit(glass_btn, (0, 0))

        screen.blit(btn_surface, btn_rect.topleft)

        # Button border - refined blue on hover
        border_color = UIColors.ACCENT_BLUE_BRIGHT if self.hover_back_button else UIColors.BORDER_MEDIUM
        border_width = 2 if self.hover_back_button else 1
        pygame.draw.rect(screen, border_color, btn_rect, border_width, border_radius=10)

        # Button text
        btn_font = pygame.font.Font(None, 26)
        back_text = btn_font.render("← Back", True, UIColors.TEXT_PRIMARY)
        back_rect = back_text.get_rect(center=btn_rect.center)
        screen.blit(back_text, back_rect)

    def _draw_scroll_indicators(self, screen):
        """Draw premium scroll indicators with smooth gradients"""
        if self.max_scroll <= 0:
            return

        # Top fade with glassmorphism
        if self.scroll_offset > 0:
            fade_height = 50
            fade = pygame.Surface((self.screen_width, fade_height), pygame.SRCALPHA)
            for i in range(fade_height):
                # Smooth gradient fade
                fade_amount = (fade_height - i) / fade_height
                alpha = int(200 * fade_amount * fade_amount)  # Quadratic for smoothness
                pygame.draw.line(fade, (*UIColors.PANEL_BG, alpha),
                               (0, i), (self.screen_width, i))
            screen.blit(fade, (0, self.HEADER_HEIGHT))

        # Bottom fade + hint with premium styling
        if self.scroll_offset < self.max_scroll:
            fade_height = 60
            fade = pygame.Surface((self.screen_width, fade_height), pygame.SRCALPHA)
            for i in range(fade_height):
                # Smooth gradient fade (reversed)
                fade_amount = i / fade_height
                alpha = int(210 * fade_amount * fade_amount)
                pygame.draw.line(fade, (*UIColors.PANEL_BG, alpha),
                               (0, i), (self.screen_width, i))
            screen.blit(fade, (0, self.screen_height - fade_height))

            # Animated scroll hint with refined styling
            pulse = math.sin(self.animation_time * 2) * 0.5 + 0.5
            hint_alpha = int(140 + pulse * 80)

            # Hint pill background
            hint_font = pygame.font.Font(None, 22)
            hint_text_str = "▼ Scroll for more"
            hint_text_temp = hint_font.render(hint_text_str, True, UIColors.TEXT_TERTIARY)
            pill_width = hint_text_temp.get_width() + 32
            pill_height = 28
            pill_x = self.screen_width // 2 - pill_width // 2
            pill_y = self.screen_height - 38
            pill_rect = pygame.Rect(pill_x, pill_y, pill_width, pill_height)

            # Pill glow
            glow_pill = pill_rect.inflate(int(8 * pulse + 4), int(8 * pulse + 4))
            glow_surface = pygame.Surface((glow_pill.width, glow_pill.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 255, int(20 * pulse)),
                           (0, 0, glow_pill.width, glow_pill.height),
                           border_radius=pill_height // 2)
            screen.blit(glow_surface, glow_pill.topleft)

            # Pill background
            pill_surface = pygame.Surface((pill_width, pill_height), pygame.SRCALPHA)
            pygame.draw.rect(pill_surface, (255, 255, 255, 10),
                           (0, 0, pill_width, pill_height),
                           border_radius=pill_height // 2)
            screen.blit(pill_surface, pill_rect.topleft)

            # Hint text
            hint = hint_font.render(hint_text_str, True, UIColors.TEXT_TERTIARY)
            hint.set_alpha(hint_alpha)
            hint_rect = hint.get_rect(center=pill_rect.center)
            screen.blit(hint, hint_rect)

    def reset(self):
        self.scroll_offset = 0
        self.scroll_velocity = 0
        self.hovered_card_index = -1
        self.hover_back_button = False

        for card in self.cards:
            card.is_expanded = False
            card.target_height = ScenarioCard.CARD_HEIGHT_COLLAPSED
            card.current_height = ScenarioCard.CARD_HEIGHT_COLLAPSED
            card.is_hovered = False

        self.refresh_cards()
        self._recalculate_card_positions()

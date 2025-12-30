"""
Improved Scenarios Menu - Vertical card-based layout with progress tracking

Styled to match the game's professional dark UI aesthetic:
- Dark blue-gray backgrounds
- Sky blue accents
- Soft green success states
- Smooth animations with glow effects
- Rounded corners and subtle shadows
"""

import pygame
import math
import os
from pathlib import Path
from .progress_manager import get_progress_manager, load_scenario_objectives


class UIColors:
    """Color palette matching the game's professional UI"""
    # Panel backgrounds
    PANEL_BG = (28, 32, 40)
    PANEL_BG_LIGHT = (35, 42, 52)
    PANEL_BG_HOVER = (42, 52, 65)
    PANEL_BORDER = (52, 58, 70)
    PANEL_ACCENT = (72, 82, 100)

    # Text
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (185, 195, 210)
    TEXT_MUTED = (120, 130, 145)
    TEXT_DISABLED = (80, 85, 95)

    # Accent colors
    ACCENT_BLUE = (96, 165, 250)
    ACCENT_BLUE_BRIGHT = (120, 186, 255)
    ACCENT_BLUE_DIM = (60, 100, 160)

    # Status colors
    SUCCESS = (72, 187, 120)
    SUCCESS_BRIGHT = (100, 220, 150)
    WARNING = (246, 173, 85)
    DANGER = (237, 94, 104)

    # Special
    GOLD = (255, 220, 100)
    SHADOW = (10, 12, 15)

    # Locked state
    LOCKED_BG = (22, 25, 32)
    LOCKED_OVERLAY = (15, 18, 24, 200)
    LOCKED_TEXT = (70, 75, 85)


class ScenarioCard:
    """Individual scenario card with polished game-matching style"""

    CARD_WIDTH = 680
    CARD_HEIGHT_COLLAPSED = 160
    CARD_HEIGHT_EXPANDED = 500  # Taller to fit more objectives
    CARD_MARGIN = 16
    CORNER_RADIUS = 12

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

        # Smooth height transition
        height_diff = self.target_height - self.current_height
        self.current_height += height_diff * min(dt * 10, 1.0)

        # Expand progress
        target_expand = 1.0 if self.is_expanded else 0.0
        self.expand_progress += (target_expand - self.expand_progress) * min(dt * 8, 1.0)

        # Hover glow
        target_glow = 1.0 if self.is_hovered else 0.0
        self.hover_glow += (target_glow - self.hover_glow) * min(dt * 12, 1.0)

        # Click feedback
        if self.click_feedback > 0:
            self.click_feedback -= dt * 5
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
        """Draw soft shadow beneath card"""
        shadow_offset = 4
        shadow_rect = rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset

        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (*UIColors.SHADOW, 60),
                        (0, 0, shadow_rect.width, shadow_rect.height),
                        border_radius=self.CORNER_RADIUS)
        screen.blit(shadow_surface, shadow_rect.topleft)

    def _draw_unlocked_card(self, screen, rect):
        """Draw unlocked scenario card with full styling"""
        # Main card surface
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Background gradient
        bg_color = UIColors.PANEL_BG_HOVER if self.is_hovered else UIColors.PANEL_BG_LIGHT
        pygame.draw.rect(card_surface, bg_color,
                        (0, 0, rect.width, rect.height),
                        border_radius=self.CORNER_RADIUS)

        # Background image with overlay
        if self.background_image:
            img_height = min(int(rect.height), self.background_image.get_height())
            img_section = self.background_image.subsurface((0, 0, rect.width, img_height))
            img_copy = img_section.copy()
            img_copy.set_alpha(40)
            card_surface.blit(img_copy, (0, 0))

        # Top accent line
        accent_color = UIColors.SUCCESS if self.info.get("completed") else UIColors.ACCENT_BLUE
        pygame.draw.rect(card_surface, accent_color,
                        (0, 0, rect.width, 3),
                        border_radius=self.CORNER_RADIUS)

        # Subtle top gradient for depth
        for i in range(40):
            alpha = int(30 * (1 - i / 40))
            pygame.draw.line(card_surface, (255, 255, 255, alpha),
                           (0, 3 + i), (rect.width, 3 + i))

        screen.blit(card_surface, rect.topleft)

        # Draw content
        self._draw_unlocked_content(screen, rect)

        # Border
        border_color = UIColors.SUCCESS if self.info.get("completed") else UIColors.PANEL_BORDER
        if self.is_hovered:
            border_color = UIColors.ACCENT_BLUE
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=self.CORNER_RADIUS)

    def _draw_unlocked_content(self, screen, rect):
        """Draw content for unlocked card"""
        padding = 24
        content_x = rect.x + padding
        content_y = rect.y + padding

        # Part badge (pill shape)
        badge_width = 70
        badge_height = 28
        badge_rect = pygame.Rect(content_x, content_y, badge_width, badge_height)
        badge_color = UIColors.SUCCESS if self.info.get("completed") else UIColors.ACCENT_BLUE
        pygame.draw.rect(screen, badge_color, badge_rect, border_radius=badge_height // 2)
        badge_text = self.font_badge.render(f"Part {self.scenario_id}", True, UIColors.TEXT_PRIMARY)
        badge_text_rect = badge_text.get_rect(center=badge_rect.center)
        screen.blit(badge_text, badge_text_rect)

        # Title
        title_x = content_x + badge_width + 16
        title_text = self.font_title.render(self.info["title"], True, UIColors.TEXT_PRIMARY)
        screen.blit(title_text, (title_x, content_y + 2))

        # Subtitle
        subtitle_text = self.font_subtitle.render(self.info["subtitle"], True, UIColors.TEXT_SECONDARY)
        screen.blit(subtitle_text, (title_x, content_y + 32))

        # Play button (right side) - shows Continue or Start
        btn_width = 100
        btn_height = 32
        btn_x = rect.right - padding - btn_width
        btn_y = content_y + 4
        self.play_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

        has_progress = self.info.get("started") and self.info.get("objectives_completed", 0) > 0
        is_completed = self.info.get("completed")

        if is_completed:
            btn_color = UIColors.SUCCESS
            btn_text_str = "Replay"
        elif has_progress:
            btn_color = UIColors.ACCENT_BLUE
            btn_text_str = "Continue"
        else:
            btn_color = UIColors.ACCENT_BLUE
            btn_text_str = "Start"

        # Button glow on hover
        if self.is_hovered:
            glow_rect = self.play_button_rect.inflate(6, 6)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*btn_color, 40), (0, 0, glow_rect.width, glow_rect.height), border_radius=8)
            screen.blit(glow_surface, glow_rect.topleft)

        pygame.draw.rect(screen, btn_color, self.play_button_rect, border_radius=6)
        # Add shine effect
        shine_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height // 2)
        shine_surface = pygame.Surface((btn_width, btn_height // 2), pygame.SRCALPHA)
        pygame.draw.rect(shine_surface, (255, 255, 255, 30), (0, 0, btn_width, btn_height // 2), border_radius=6)
        screen.blit(shine_surface, shine_rect.topleft)

        btn_text = self.font_subtitle.render(btn_text_str, True, UIColors.TEXT_PRIMARY)
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

        # Expand indicator
        expand_y = rect.y + self.CARD_HEIGHT_COLLAPSED - 28
        expand_alpha = int(180 + math.sin(self.pulse_time * 3) * 40)
        expand_color = (*UIColors.TEXT_SECONDARY[:3], expand_alpha) if not self.is_expanded else UIColors.TEXT_MUTED
        arrow = "▼ View objectives" if not self.is_expanded else "▲ Hide objectives"
        expand_text = self.font_small.render(arrow, True, expand_color[:3])
        expand_rect = expand_text.get_rect(centerx=rect.centerx, y=expand_y)
        screen.blit(expand_text, expand_rect)

        # Expanded content
        if self.expand_progress > 0.1:
            self._draw_expanded_content(screen, rect, content_x, padding)

    def _draw_progress_bar(self, screen, rect, y, padding):
        """Draw the progress bar with percentage"""
        bar_x = rect.x + padding
        bar_width = rect.width - padding * 2 - 80
        bar_height = 10

        # Background
        pygame.draw.rect(screen, UIColors.PANEL_BG,
                        (bar_x, y, bar_width, bar_height),
                        border_radius=5)

        # Fill
        completion = self.info.get("completion_percentage", 0)
        if completion > 0:
            fill_width = int((completion / 100) * bar_width)
            fill_color = UIColors.SUCCESS if completion >= 100 else UIColors.ACCENT_BLUE
            pygame.draw.rect(screen, fill_color,
                           (bar_x, y, fill_width, bar_height),
                           border_radius=5)

            # Shine effect
            shine_rect = pygame.Rect(bar_x, y, fill_width, bar_height // 2)
            shine_surface = pygame.Surface((fill_width, bar_height // 2), pygame.SRCALPHA)
            pygame.draw.rect(shine_surface, (255, 255, 255, 40),
                           (0, 0, fill_width, bar_height // 2),
                           border_radius=5)
            screen.blit(shine_surface, shine_rect.topleft)

        # Percentage text
        percent_text = self.font_small.render(f"{completion:.0f}%", True, UIColors.TEXT_SECONDARY)
        screen.blit(percent_text, (bar_x + bar_width + 12, y - 2))

        # Objectives count
        done = self.info.get("objectives_completed", 0)
        total = self.info.get("objectives_count", 0)
        count_text = self.font_small.render(f"{done}/{total} objectives", True, UIColors.TEXT_MUTED)
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
        pygame.draw.line(screen, (*UIColors.PANEL_ACCENT[:3], alpha),
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

                # Row background - highlight current objective
                row_bg = pygame.Surface((rect.width - padding * 2, 30), pygame.SRCALPHA)
                if is_current:
                    # Highlight current objective with blue glow
                    pulse = int(20 + math.sin(self.pulse_time * 3) * 10)
                    pygame.draw.rect(row_bg, (*UIColors.ACCENT_BLUE[:3], int((40 + pulse) * self.expand_progress)),
                                   (0, 0, rect.width - padding * 2, 30), border_radius=4)
                elif i % 2 == 0:
                    pygame.draw.rect(row_bg, (*UIColors.PANEL_BG[:3], int(40 * self.expand_progress)),
                                   (0, 0, rect.width - padding * 2, 30), border_radius=4)
                screen.blit(row_bg, (content_x, obj_y))

                # Current indicator arrow
                if is_current:
                    arrow = self.font_body.render("▶", True, UIColors.ACCENT_BLUE)
                    arrow.set_alpha(alpha)
                    screen.blit(arrow, (content_x + 2, obj_y + 5))

                # Objective number
                num_color = UIColors.SUCCESS if is_done else (UIColors.ACCENT_BLUE if is_current else UIColors.TEXT_MUTED)
                num_text = self.font_small.render(f"{i + 1}.", True, num_color)
                num_text.set_alpha(alpha)
                screen.blit(num_text, (content_x + (18 if is_current else 4), obj_y + 6))

                # Checkbox
                cb_size = 16
                cb_x = content_x + 38
                cb_rect = pygame.Rect(cb_x, obj_y + 6, cb_size, cb_size)

                if is_done:
                    pygame.draw.rect(screen, (*UIColors.SUCCESS[:3], alpha), cb_rect, border_radius=3)
                    check = self.font_small.render("✓", True, UIColors.TEXT_PRIMARY)
                    check.set_alpha(alpha)
                    check_rect = check.get_rect(center=cb_rect.center)
                    screen.blit(check, check_rect)
                elif is_current:
                    # Pulsing border for current
                    pulse_alpha = int(180 + math.sin(self.pulse_time * 4) * 75)
                    pygame.draw.rect(screen, (*UIColors.ACCENT_BLUE[:3], min(pulse_alpha, alpha)), cb_rect, 2, border_radius=3)
                else:
                    pygame.draw.rect(screen, (*UIColors.PANEL_ACCENT[:3], alpha), cb_rect, 2, border_radius=3)

                # Objective title (truncate if too long)
                title = obj.get("title", "Unknown")
                max_title_width = rect.width - padding * 2 - 80
                if is_done:
                    title_color = UIColors.SUCCESS
                elif is_current:
                    title_color = UIColors.TEXT_PRIMARY
                else:
                    title_color = UIColors.TEXT_MUTED

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
        """Draw hover and click effects"""
        if self.hover_glow > 0.05 and is_unlocked:
            glow_alpha = int(50 * self.hover_glow)
            glow_surface = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*UIColors.ACCENT_BLUE, glow_alpha),
                           (0, 0, rect.width + 8, rect.height + 8),
                           border_radius=self.CORNER_RADIUS + 2)
            screen.blit(glow_surface, (rect.x - 4, rect.y - 4))

        if self.click_feedback > 0:
            feedback_alpha = int(100 * self.click_feedback)
            feedback_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(feedback_surface, (255, 255, 255, feedback_alpha),
                           (0, 0, rect.width, rect.height),
                           border_radius=self.CORNER_RADIUS)
            screen.blit(feedback_surface, rect.topleft)


class ImprovedScenariosMenu:
    """Main scenarios menu with vertical scrolling cards - game-matched styling"""

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

        # Background
        screen.fill(UIColors.PANEL_BG)

        # Subtle pattern/texture (optional grid)
        for y in range(0, self.screen_height, 40):
            pygame.draw.line(screen, (32, 36, 45), (0, y), (self.screen_width, y), 1)

        # Draw cards
        for card in self.cards:
            card.draw(screen, self.scroll_offset)

        # Header
        self._draw_header(screen)

        # Scroll indicators
        self._draw_scroll_indicators(screen)

    def _draw_header(self, screen):
        # Header background with gradient
        header_surface = pygame.Surface((self.screen_width, self.HEADER_HEIGHT), pygame.SRCALPHA)
        for i in range(self.HEADER_HEIGHT):
            alpha = 255 if i < self.HEADER_HEIGHT - 20 else int(255 * (1 - (i - self.HEADER_HEIGHT + 20) / 20))
            pygame.draw.line(header_surface, (*UIColors.PANEL_BG, alpha),
                           (0, i), (self.screen_width, i))
        screen.blit(header_surface, (0, 0))

        # Top accent line
        pygame.draw.line(screen, UIColors.ACCENT_BLUE, (0, 0), (self.screen_width, 0), 3)

        # Title
        title = self.font_title.render("Choose Your Story", True, UIColors.TEXT_PRIMARY)
        title_rect = title.get_rect(centerx=self.screen_width // 2, centery=self.HEADER_HEIGHT // 2)
        screen.blit(title, title_rect)

        # Back button
        btn_color = UIColors.PANEL_BG_HOVER if self.hover_back_button else UIColors.PANEL_BG_LIGHT
        pygame.draw.rect(screen, btn_color, self.back_button_rect, border_radius=8)
        pygame.draw.rect(screen, UIColors.PANEL_BORDER, self.back_button_rect, 1, border_radius=8)

        if self.hover_back_button:
            pygame.draw.rect(screen, UIColors.ACCENT_BLUE, self.back_button_rect, 2, border_radius=8)

        back_text = self.font_button.render("← Back", True, UIColors.TEXT_PRIMARY)
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_rect)

    def _draw_scroll_indicators(self, screen):
        if self.max_scroll <= 0:
            return

        # Top fade
        if self.scroll_offset > 0:
            fade = pygame.Surface((self.screen_width, 30), pygame.SRCALPHA)
            for i in range(30):
                alpha = int(150 * (1 - i / 30))
                pygame.draw.line(fade, (*UIColors.PANEL_BG, alpha), (0, i), (self.screen_width, i))
            screen.blit(fade, (0, self.HEADER_HEIGHT))

        # Bottom fade + hint
        if self.scroll_offset < self.max_scroll:
            fade = pygame.Surface((self.screen_width, 40), pygame.SRCALPHA)
            for i in range(40):
                alpha = int(180 * (i / 40))
                pygame.draw.line(fade, (*UIColors.PANEL_BG, alpha), (0, i), (self.screen_width, i))
            screen.blit(fade, (0, self.screen_height - 40))

            pulse = int(180 + math.sin(self.animation_time * 3) * 50)
            hint = self.font_button.render("▼ Scroll for more", True, (*UIColors.TEXT_MUTED[:2], pulse))
            hint_rect = hint.get_rect(centerx=self.screen_width // 2, bottom=self.screen_height - 12)
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

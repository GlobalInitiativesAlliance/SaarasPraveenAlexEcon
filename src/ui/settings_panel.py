"""
Settings Panel UI
Clean, minimal settings menu with save/autosave options
"""

import pygame
from typing import Tuple, Optional, Callable


class SettingsPanel:
    """Settings panel with save/autosave controls"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Colors (matching CollapsibleUI)
        self.colors = {
            'bg': (20, 20, 24),
            'bg_light': (30, 30, 36),
            'border': (55, 55, 65),
            'accent': (90, 140, 255),
            'success': (70, 200, 120),
            'warning': (255, 180, 70),
            'text': (240, 240, 245),
            'text_secondary': (140, 145, 160),
            'text_muted': (90, 95, 110),
            'button_bg': (45, 50, 60),
            'button_hover': (60, 65, 80),
            'toggle_off': (60, 60, 70),
            'toggle_on': (70, 200, 120),
        }

        # Panel dimensions
        self.panel_width = 320
        self.panel_height = 400  # Increased for reset button
        self.corner_radius = 10
        self.padding = 20

        # Center on screen
        self.x = (screen_width - self.panel_width) // 2
        self.y = (screen_height - self.panel_height) // 2

        # State
        self.visible = False
        self.autosave_enabled = True
        self.autosave_interval = 60  # seconds

        # Animation
        self.animation_progress = 0.0
        self.animation_speed = 0.15

        # Fonts
        self.fonts_initialized = False
        self.font_title = None
        self.font_label = None
        self.font_button = None

        # Button rects for click detection
        self.close_button_rect = None
        self.save_button_rect = None
        self.autosave_toggle_rect = None
        self.autoplay_button_rect = None
        self.reset_button_rect = None
        self.reset_confirm_rect = None
        self.reset_cancel_rect = None

        # Hover states
        self.save_hovered = False
        self.close_hovered = False
        self.autosave_hovered = False
        self.autoplay_hovered = False
        self.reset_hovered = False
        self.reset_confirm_hovered = False
        self.reset_cancel_hovered = False

        # Reset confirmation state
        self.showing_reset_confirm = False

        # Callbacks
        self.on_save: Optional[Callable] = None
        self.on_autosave_change: Optional[Callable[[bool], None]] = None
        self.on_autoplay: Optional[Callable] = None
        self.on_reset: Optional[Callable] = None

        # Last save time display
        self.last_save_time = "Never"

    def init_fonts(self):
        """Initialize fonts"""
        if not self.fonts_initialized:
            self.font_title = pygame.font.Font(None, 28)
            self.font_label = pygame.font.Font(None, 20)
            self.font_button = pygame.font.Font(None, 22)
            self.fonts_initialized = True

    def show(self):
        """Show the settings panel"""
        self.visible = True
        self.animation_progress = 0.0

    def hide(self):
        """Hide the settings panel"""
        self.visible = False
        self.animation_progress = 0.0

    def toggle(self):
        """Toggle visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()

    def update(self, dt: float):
        """Update animation"""
        if self.visible and self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
        elif not self.visible and self.animation_progress > 0.0:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Handle click events. Returns action string or None."""
        if not self.visible:
            return None

        # Handle reset confirmation dialog first
        if self.showing_reset_confirm:
            if self.reset_confirm_rect and self.reset_confirm_rect.collidepoint(pos):
                # Confirmed - reset progress
                from src.core.progress_manager import get_progress_manager
                progress_manager = get_progress_manager()
                progress_manager.reset_progress()
                print("Game progress reset!")
                self.showing_reset_confirm = False
                if self.on_reset:
                    self.on_reset()
                return 'reset_progress'
            elif self.reset_cancel_rect and self.reset_cancel_rect.collidepoint(pos):
                self.showing_reset_confirm = False
                return 'cancel_reset'
            # Consume all clicks when dialog is showing
            return 'settings_panel'

        # Check close button
        if self.close_button_rect and self.close_button_rect.collidepoint(pos):
            self.hide()
            return 'close_settings'

        # Check save button
        if self.save_button_rect and self.save_button_rect.collidepoint(pos):
            if self.on_save:
                self.on_save()
            return 'save_game'

        # Check autosave toggle
        if self.autosave_toggle_rect and self.autosave_toggle_rect.collidepoint(pos):
            self.autosave_enabled = not self.autosave_enabled
            if self.on_autosave_change:
                self.on_autosave_change(self.autosave_enabled)
            return 'toggle_autosave'

        # Check auto-play button
        if self.autoplay_button_rect and self.autoplay_button_rect.collidepoint(pos):
            if self.on_autoplay:
                self.on_autoplay()
            self.hide()
            return 'start_autoplay'

        # Check reset button
        if self.reset_button_rect and self.reset_button_rect.collidepoint(pos):
            self.showing_reset_confirm = True
            return 'show_reset_confirm'

        # Click inside panel but not on any button - consume the click
        panel_rect = pygame.Rect(self.x, self.y, self.panel_width, self.panel_height)
        if panel_rect.collidepoint(pos):
            return 'settings_panel'

        # Click outside panel - close it
        self.hide()
        return 'close_settings'

    def handle_motion(self, pos: Tuple[int, int]):
        """Handle mouse motion for hover effects"""
        if not self.visible:
            return

        self.save_hovered = self.save_button_rect and self.save_button_rect.collidepoint(pos)
        self.close_hovered = self.close_button_rect and self.close_button_rect.collidepoint(pos)
        self.autosave_hovered = self.autosave_toggle_rect and self.autosave_toggle_rect.collidepoint(pos)
        self.autoplay_hovered = self.autoplay_button_rect and self.autoplay_button_rect.collidepoint(pos)
        self.reset_hovered = self.reset_button_rect and self.reset_button_rect.collidepoint(pos)
        self.reset_confirm_hovered = self.reset_confirm_rect and self.reset_confirm_rect.collidepoint(pos)
        self.reset_cancel_hovered = self.reset_cancel_rect and self.reset_cancel_rect.collidepoint(pos)

    def set_last_save_time(self, time_str: str):
        """Update the last save time display"""
        self.last_save_time = time_str

    def draw(self, screen: pygame.Surface):
        """Draw the settings panel"""
        if self.animation_progress <= 0:
            return

        self.init_fonts()

        # Calculate animated alpha and scale
        alpha = int(255 * self.animation_progress)
        scale = 0.9 + 0.1 * self.animation_progress

        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(120 * self.animation_progress)))
        screen.blit(overlay, (0, 0))

        # Create panel surface
        panel_w = int(self.panel_width * scale)
        panel_h = int(self.panel_height * scale)
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

        # Draw shadow
        shadow_offset = 4
        pygame.draw.rect(panel, (0, 0, 0, 60),
                        (shadow_offset, shadow_offset, panel_w - shadow_offset, panel_h - shadow_offset),
                        border_radius=self.corner_radius)

        # Main background
        pygame.draw.rect(panel, self.colors['bg'], (0, 0, panel_w, panel_h),
                        border_radius=self.corner_radius)

        # Border
        pygame.draw.rect(panel, self.colors['border'], (0, 0, panel_w, panel_h),
                        width=1, border_radius=self.corner_radius)

        # Header
        header_h = 50
        pygame.draw.rect(panel, self.colors['bg_light'],
                        (0, 0, panel_w, header_h),
                        border_top_left_radius=self.corner_radius,
                        border_top_right_radius=self.corner_radius)

        # Title
        title_surf = self.font_title.render("Settings", True, self.colors['text'])
        panel.blit(title_surf, (self.padding, (header_h - title_surf.get_height()) // 2))

        # Close button (X)
        close_size = 24
        close_x = panel_w - self.padding - close_size
        close_y = (header_h - close_size) // 2
        close_color = self.colors['text'] if self.close_hovered else self.colors['text_muted']
        pygame.draw.line(panel, close_color, (close_x, close_y), (close_x + close_size, close_y + close_size), 2)
        pygame.draw.line(panel, close_color, (close_x + close_size, close_y), (close_x, close_y + close_size), 2)

        # Content area
        content_y = header_h + 20

        # --- Autosave Toggle ---
        label_surf = self.font_label.render("Autosave", True, self.colors['text'])
        panel.blit(label_surf, (self.padding, content_y))

        # Toggle switch
        toggle_w = 44
        toggle_h = 24
        toggle_x = panel_w - self.padding - toggle_w
        toggle_y = content_y - 2

        # Toggle background
        toggle_color = self.colors['toggle_on'] if self.autosave_enabled else self.colors['toggle_off']
        pygame.draw.rect(panel, toggle_color, (toggle_x, toggle_y, toggle_w, toggle_h),
                        border_radius=toggle_h // 2)

        # Toggle knob
        knob_size = toggle_h - 4
        knob_x = toggle_x + (toggle_w - knob_size - 2) if self.autosave_enabled else toggle_x + 2
        pygame.draw.circle(panel, self.colors['text'],
                          (knob_x + knob_size // 2, toggle_y + toggle_h // 2), knob_size // 2)

        # Autosave status text
        status_text = "Every 60 seconds" if self.autosave_enabled else "Disabled"
        status_surf = self.font_label.render(status_text, True, self.colors['text_secondary'])
        panel.blit(status_surf, (self.padding, content_y + 28))

        content_y += 70

        # --- Last Save Info ---
        last_save_label = self.font_label.render("Last Saved:", True, self.colors['text_muted'])
        panel.blit(last_save_label, (self.padding, content_y))

        last_save_time = self.font_label.render(self.last_save_time, True, self.colors['text'])
        panel.blit(last_save_time, (self.padding + last_save_label.get_width() + 8, content_y))

        content_y += 40

        # --- Save Now Button ---
        button_w = panel_w - self.padding * 2
        button_h = 44
        button_x = self.padding
        button_y = content_y

        button_color = self.colors['button_hover'] if self.save_hovered else self.colors['button_bg']
        pygame.draw.rect(panel, button_color, (button_x, button_y, button_w, button_h),
                        border_radius=8)
        pygame.draw.rect(panel, self.colors['accent'], (button_x, button_y, button_w, button_h),
                        width=1, border_radius=8)

        save_text = self.font_button.render("Save Game", True, self.colors['text'])
        text_x = button_x + (button_w - save_text.get_width()) // 2
        text_y = button_y + (button_h - save_text.get_height()) // 2
        panel.blit(save_text, (text_x, text_y))

        # Store save button position for later
        save_button_y = button_y

        content_y += 54

        # --- Auto-Play Button ---
        autoplay_button_x = self.padding
        autoplay_button_y = content_y
        autoplay_button_w = button_w
        autoplay_button_h = 44

        # Use warning color for auto-play to make it stand out
        autoplay_color = self.colors['button_hover'] if self.autoplay_hovered else self.colors['button_bg']
        pygame.draw.rect(panel, autoplay_color, (autoplay_button_x, autoplay_button_y, autoplay_button_w, autoplay_button_h),
                        border_radius=8)
        pygame.draw.rect(panel, self.colors['warning'], (autoplay_button_x, autoplay_button_y, autoplay_button_w, autoplay_button_h),
                        width=1, border_radius=8)

        autoplay_text = self.font_button.render("Auto-Play (Test)", True, self.colors['warning'])
        text_x = autoplay_button_x + (autoplay_button_w - autoplay_text.get_width()) // 2
        text_y = autoplay_button_y + (autoplay_button_h - autoplay_text.get_height()) // 2
        panel.blit(autoplay_text, (text_x, text_y))

        content_y += 54

        # --- Reset Progress Button ---
        reset_button_x = self.padding
        reset_button_y = content_y
        reset_button_w = button_w
        reset_button_h = 44

        # Use red/danger color for reset
        danger_color = (180, 60, 60)
        danger_hover = (200, 80, 80)
        reset_color = danger_hover if self.reset_hovered else danger_color
        pygame.draw.rect(panel, reset_color, (reset_button_x, reset_button_y, reset_button_w, reset_button_h),
                        border_radius=8)
        pygame.draw.rect(panel, (255, 100, 100), (reset_button_x, reset_button_y, reset_button_w, reset_button_h),
                        width=1, border_radius=8)

        reset_text = self.font_button.render("Reset Progress", True, (255, 200, 200))
        text_x = reset_button_x + (reset_button_w - reset_text.get_width()) // 2
        text_y = reset_button_y + (reset_button_h - reset_text.get_height()) // 2
        panel.blit(reset_text, (text_x, text_y))

        # Apply alpha
        panel.set_alpha(alpha)

        # Center panel on screen
        panel_x = (self.screen_width - panel_w) // 2
        panel_y = (self.screen_height - panel_h) // 2
        screen.blit(panel, (panel_x, panel_y))

        # Update button rects for click detection (in screen coordinates)
        scale_offset_x = (self.panel_width - panel_w) // 2
        scale_offset_y = (self.panel_height - panel_h) // 2

        self.close_button_rect = pygame.Rect(
            panel_x + close_x - 4, panel_y + close_y - 4,
            close_size + 8, close_size + 8
        )
        self.save_button_rect = pygame.Rect(
            panel_x + button_x, panel_y + button_y,
            button_w, button_h
        )
        self.autosave_toggle_rect = pygame.Rect(
            panel_x + toggle_x - 4, panel_y + toggle_y - 4,
            toggle_w + 8, toggle_h + 8
        )
        self.autoplay_button_rect = pygame.Rect(
            panel_x + autoplay_button_x, panel_y + autoplay_button_y,
            autoplay_button_w, autoplay_button_h
        )
        self.reset_button_rect = pygame.Rect(
            panel_x + reset_button_x, panel_y + reset_button_y,
            reset_button_w, reset_button_h
        )

        # Draw reset confirmation dialog if showing
        if self.showing_reset_confirm:
            self._draw_reset_confirmation(screen)

    def _draw_reset_confirmation(self, screen: pygame.Surface):
        """Draw the reset progress confirmation dialog"""
        # Semi-transparent overlay on top of everything
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_width, dialog_height = 350, 180
        dialog_x = self.screen_width // 2 - dialog_width // 2
        dialog_y = self.screen_height // 2 - dialog_height // 2

        # Dialog background
        pygame.draw.rect(screen, (40, 40, 50), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
        pygame.draw.rect(screen, (255, 100, 100), (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=10)

        # Title text
        title = self.font_title.render("Reset All Progress?", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.screen_width // 2, y=dialog_y + 25)
        screen.blit(title, title_rect)

        # Warning text
        warning = self.font_label.render("This will erase ALL saved progress.", True, (255, 200, 100))
        warning_rect = warning.get_rect(centerx=self.screen_width // 2, y=dialog_y + 65)
        screen.blit(warning, warning_rect)

        warning2 = self.font_label.render("This cannot be undone!", True, (255, 100, 100))
        warning2_rect = warning2.get_rect(centerx=self.screen_width // 2, y=dialog_y + 90)
        screen.blit(warning2, warning2_rect)

        # Buttons
        btn_w, btn_h = 100, 40
        confirm_x = self.screen_width // 2 - btn_w - 15
        cancel_x = self.screen_width // 2 + 15
        btn_y = dialog_y + 125

        # Confirm button (red)
        confirm_color = (200, 60, 60) if self.reset_confirm_hovered else (150, 50, 50)
        pygame.draw.rect(screen, confirm_color, (confirm_x, btn_y, btn_w, btn_h), border_radius=5)
        pygame.draw.rect(screen, (255, 100, 100), (confirm_x, btn_y, btn_w, btn_h), 2, border_radius=5)

        yes_text = self.font_button.render("Yes, Reset", True, (255, 255, 255))
        yes_rect = yes_text.get_rect(center=(confirm_x + btn_w // 2, btn_y + btn_h // 2))
        screen.blit(yes_text, yes_rect)

        # Cancel button (green)
        cancel_color = (60, 150, 60) if self.reset_cancel_hovered else (50, 120, 50)
        pygame.draw.rect(screen, cancel_color, (cancel_x, btn_y, btn_w, btn_h), border_radius=5)
        pygame.draw.rect(screen, (100, 200, 100), (cancel_x, btn_y, btn_w, btn_h), 2, border_radius=5)

        no_text = self.font_button.render("Cancel", True, (255, 255, 255))
        no_rect = no_text.get_rect(center=(cancel_x + btn_w // 2, btn_y + btn_h // 2))
        screen.blit(no_text, no_rect)

        # Update button rects
        self.reset_confirm_rect = pygame.Rect(confirm_x, btn_y, btn_w, btn_h)
        self.reset_cancel_rect = pygame.Rect(cancel_x, btn_y, btn_w, btn_h)

    def is_visible(self) -> bool:
        """Check if panel is visible"""
        return self.visible or self.animation_progress > 0

"""
Dialogue Box UI Component - Displays narrative text at bottom of screen
Clean design without embedded portraits (portraits handled separately)
"""
import pygame
import math
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class DialogueBox:
    def __init__(self):
        self.active = False
        self.current_text = ""
        self.current_speaker = ""
        self.text_progress = 0  # For typewriter effect
        self.text_speed = 30  # Characters per second
        self.animation_time = 0

        # Box dimensions
        self.box_height = 150
        self.box_y = SCREEN_HEIGHT - self.box_height - 20
        self.box_x = 50
        self.box_width = SCREEN_WIDTH - 100

        # Colors - polished dark theme
        self.box_color = (20, 25, 35)
        self.border_color = (60, 70, 90)
        self.text_color = (240, 240, 245)
        self.speaker_color = (255, 220, 100)
        self.narrator_color = (170, 175, 190)

        # Fonts
        self.speaker_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 24)
        self.prompt_font = pygame.font.Font(None, 20)

        # Text wrapping
        self.max_line_width = self.box_width - 40
        self.lines = []

    def show(self, speaker, text):
        """Display dialogue with speaker name and text"""
        self.active = True
        self.current_speaker = speaker
        self.current_text = text
        self.text_progress = 0
        self.wrap_text()

    def wrap_text(self):
        """Wrap text to fit in dialogue box"""
        self.lines = []
        words = self.current_text.split(' ')
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_surface = self.text_font.render(test_line, True, self.text_color)

            if text_surface.get_width() > self.max_line_width:
                if current_line:
                    self.lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            self.lines.append(current_line.strip())

    def update(self, dt):
        """Update typewriter effect"""
        self.animation_time += dt

        if self.active and self.text_progress < len(self.current_text):
            self.text_progress += self.text_speed * dt
            if self.text_progress > len(self.current_text):
                self.text_progress = len(self.current_text)

    def skip_typewriter(self):
        """Skip to full text"""
        self.text_progress = len(self.current_text)

    def hide(self):
        """Hide the dialogue box"""
        self.active = False
        self.current_text = ""
        self.current_speaker = ""

    def draw(self, screen):
        """Draw the dialogue box with polished styling"""
        if not self.active:
            return

        is_narrator = self.current_speaker is None or self.current_speaker == ""

        # Draw shadow
        shadow_offset = 4
        shadow_surface = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80),
                        (0, 0, self.box_width, self.box_height), border_radius=12)
        screen.blit(shadow_surface, (self.box_x + shadow_offset, self.box_y + shadow_offset))

        # Draw box background
        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        box_surface = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (*self.box_color, 245),
                        (0, 0, self.box_width, self.box_height), border_radius=12)
        screen.blit(box_surface, (self.box_x, self.box_y))

        # Draw border
        pygame.draw.rect(screen, self.border_color, box_rect, 2, border_radius=12)

        # Draw speaker name
        text_y_offset = 15
        if self.current_speaker and not is_narrator:
            speaker_surf = self.speaker_font.render(self.current_speaker, True, self.speaker_color)
            screen.blit(speaker_surf, (self.box_x + 20, self.box_y + text_y_offset))
            text_y_offset = 45
        elif is_narrator:
            text_y_offset = 25

        # Draw text with typewriter effect
        visible_chars = int(self.text_progress)
        char_count = 0

        text_color = self.narrator_color if is_narrator else self.text_color

        for i, line in enumerate(self.lines[:4]):  # Max 4 lines
            if char_count >= visible_chars:
                break

            line_to_show = line
            if char_count + len(line) > visible_chars:
                line_to_show = line[:visible_chars - char_count]

            text_surf = self.text_font.render(line_to_show, True, text_color)
            screen.blit(text_surf, (self.box_x + 20, self.box_y + text_y_offset + i * 28))
            char_count += len(line) + 1

        # Draw continue prompt with pulsing animation
        if self.text_progress >= len(self.current_text):
            pulse = abs(math.sin(self.animation_time * 3)) * 0.5 + 0.5
            indicator_color = (int(100 + 100 * pulse), int(100 + 100 * pulse), int(100 + 100 * pulse))

            indicator_x = self.box_x + self.box_width - 30
            indicator_y = self.box_y + self.box_height - 22

            # Pulsing triangle
            points = [
                (indicator_x, indicator_y - 6),
                (indicator_x + 10, indicator_y - 6),
                (indicator_x + 5, indicator_y + 2)
            ]
            pygame.draw.polygon(screen, indicator_color, points)

            # Small prompt
            prompt_surf = self.prompt_font.render("SPACE", True, (120, 120, 130))
            screen.blit(prompt_surf, (indicator_x - 35, indicator_y - 5))

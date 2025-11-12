"""
Dialogue Box UI Component - Displays narrative text at bottom of screen
"""
import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class DialogueBox:
    def __init__(self):
        self.active = False
        self.current_text = ""
        self.current_speaker = ""
        self.text_progress = 0  # For typewriter effect
        self.text_speed = 30  # Characters per second

        # Box dimensions
        self.box_height = 150
        self.box_y = SCREEN_HEIGHT - self.box_height - 20
        self.box_x = 50
        self.box_width = SCREEN_WIDTH - 100

        # Colors
        self.box_color = (30, 30, 40)
        self.border_color = (200, 200, 220)
        self.text_color = (255, 255, 255)
        self.speaker_color = (255, 220, 100)

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
        """Draw the dialogue box"""
        if not self.active:
            return

        # Draw box background
        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_width, self.box_height)
        pygame.draw.rect(screen, self.box_color, box_rect)
        pygame.draw.rect(screen, self.border_color, box_rect, 3)

        # Draw corner decorations
        corner_size = 15
        corners = [
            (self.box_x, self.box_y),
            (self.box_x + self.box_width - corner_size, self.box_y),
            (self.box_x, self.box_y + self.box_height - corner_size),
            (self.box_x + self.box_width - corner_size, self.box_y + self.box_height - corner_size)
        ]

        for cx, cy in corners:
            pygame.draw.lines(screen, self.speaker_color, False,
                            [(cx, cy + corner_size), (cx, cy), (cx + corner_size, cy)], 2)

        # Draw speaker name
        if self.current_speaker:
            speaker_surf = self.speaker_font.render(self.current_speaker + ":", True, self.speaker_color)
            screen.blit(speaker_surf, (self.box_x + 20, self.box_y + 15))

        # Draw text with typewriter effect
        y_offset = 50 if self.current_speaker else 20
        visible_chars = int(self.text_progress)
        char_count = 0

        for i, line in enumerate(self.lines):
            if char_count >= visible_chars:
                break

            line_to_show = line
            if char_count + len(line) > visible_chars:
                line_to_show = line[:visible_chars - char_count]

            text_surf = self.text_font.render(line_to_show, True, self.text_color)
            screen.blit(text_surf, (self.box_x + 20, self.box_y + y_offset + i * 30))
            char_count += len(line) + 1  # +1 for space

        # Draw continue prompt
        if self.text_progress >= len(self.current_text):
            prompt_text = "[SPACE] Continue"
            prompt_surf = self.prompt_font.render(prompt_text, True, (180, 180, 190))
            prompt_rect = prompt_surf.get_rect(bottomright=(self.box_x + self.box_width - 20,
                                                           self.box_y + self.box_height - 10))
            screen.blit(prompt_surf, prompt_rect)

            # Add blinking animated arrow for better visibility
            blink_visible = (pygame.time.get_ticks() // 500) % 2  # Blink every 500ms
            if blink_visible:
                # Draw triangle arrow pointing right
                arrow_x = prompt_rect.right + 10
                arrow_y = prompt_rect.centery
                arrow_points = [
                    (arrow_x, arrow_y - 6),
                    (arrow_x + 10, arrow_y),
                    (arrow_x, arrow_y + 6)
                ]
                pygame.draw.polygon(screen, (255, 220, 100), arrow_points)
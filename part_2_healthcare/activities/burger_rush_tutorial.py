"""
Tutorial system for the Burger Rush game
"""
import pygame
import math

def draw_tutorial(self, screen):
    """Draw the tutorial overlay with instructions"""
    if not self.tutorial_active or self.tutorial_step >= len(self.tutorial_steps):
        return

    current_step = self.tutorial_steps[self.tutorial_step]

    # Draw semi-transparent overlay
    overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    # Highlight the relevant area
    if current_step.get('highlight') and current_step['highlight'] in self.areas:
        highlight_area = self.areas[current_step['highlight']]

        # Create pulsing highlight effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.5 + 0.5
        highlight_color = (255, 255, 0, int(100 * pulse))

        # Draw highlight circle/rectangle around area
        highlight_surface = pygame.Surface((highlight_area.width + 40, highlight_area.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, highlight_color, (0, 0, highlight_area.width + 40, highlight_area.height + 40), border_radius=20)
        screen.blit(highlight_surface, (highlight_area.x - 20, highlight_area.y - 20))

        # Draw arrow pointing to area
        arrow_pos = (highlight_area.centerx, highlight_area.y - 60)
        self.draw_tutorial_arrow(screen, arrow_pos, 'down')

    # Draw instruction panel
    panel_width = 600
    panel_height = 200
    panel_x = (self.SCREEN_WIDTH - panel_width) // 2
    panel_y = 50

    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    # Panel background with gradient
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    for i in range(panel_height):
        alpha = 240 - (i // 4)
        color = (250, 245, 240, alpha)
        pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))

    screen.blit(panel_surface, (panel_x, panel_y))
    pygame.draw.rect(screen, (100, 150, 200), panel_rect, 4, border_radius=15)

    # Title
    title_font = self.fonts['large']
    title_text = title_font.render(current_step['title'], True, (50, 100, 150))
    title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 40))
    screen.blit(title_text, title_rect)

    # Instruction text (word-wrapped)
    instruction_lines = self.wrap_text(current_step['text'], self.fonts['medium'], panel_width - 40)
    y_offset = panel_y + 80

    for line in instruction_lines:
        line_surface = self.fonts['medium'].render(line, True, (60, 60, 60))
        line_rect = line_surface.get_rect(center=(panel_x + panel_width // 2, y_offset))
        screen.blit(line_surface, line_rect)
        y_offset += 30

    # Action hint
    action_text = self.fonts['small'].render(current_step['action'], True, (100, 150, 100))
    action_rect = action_text.get_rect(center=(panel_x + panel_width // 2, panel_y + panel_height - 30))
    screen.blit(action_text, action_rect)

    # Tutorial progress
    progress_text = f"Step {self.tutorial_step + 1} of {len(self.tutorial_steps)}"
    progress_surface = self.fonts['small'].render(progress_text, True, (100, 100, 100))
    screen.blit(progress_surface, (panel_x + 10, panel_y + panel_height - 20))

    # Skip hint
    skip_text = "Press ESC to skip tutorial"
    skip_surface = self.fonts['tiny'].render(skip_text, True, (150, 150, 150))
    screen.blit(skip_surface, (self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT - 30))

def draw_tutorial_arrow(self, screen, pos, direction):
    """Draw an animated arrow pointing in the specified direction"""
    bounce = math.sin(pygame.time.get_ticks() * 0.01) * 10

    if direction == 'down':
        arrow_points = [
            (pos[0], pos[1] + bounce),
            (pos[0] - 15, pos[1] - 15 + bounce),
            (pos[0] + 15, pos[1] - 15 + bounce)
        ]
    elif direction == 'right':
        arrow_points = [
            (pos[0] + bounce, pos[1]),
            (pos[0] - 15 + bounce, pos[1] - 15),
            (pos[0] - 15 + bounce, pos[1] + 15)
        ]

    pygame.draw.polygon(screen, (255, 255, 0), arrow_points)
    pygame.draw.polygon(screen, (200, 200, 0), arrow_points, 3)

def wrap_text(self, text, font, max_width):
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        line_text = ' '.join(current_line)
        text_width = font.size(line_text)[0]

        if text_width > max_width:
            if len(current_line) > 1:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
            else:
                lines.append(line_text)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    return lines

# Add these methods to the BurgerRushGame class
def add_tutorial_methods(cls):
    """Add tutorial methods to BurgerRushGame class"""
    cls.draw_tutorial = draw_tutorial
    cls.draw_tutorial_arrow = draw_tutorial_arrow
    cls.wrap_text = wrap_text
    return cls
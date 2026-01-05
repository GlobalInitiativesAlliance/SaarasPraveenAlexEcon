"""
Dialogue Box UI Component - Displays narrative text at bottom of screen
Enhanced with integrated character portraits
"""
import pygame
import math
import os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class DialogueBox:
    # Map speaker names to character IDs for portraits
    SPEAKER_TO_CHARACTER = {
        'You': 'player',
        'Officer': 'officer',
        'Judge': 'judge',
        'Clerk': 'clerk',
        'Manager': 'manager',
        'Coworker': 'coworker',
        'Classmate': 'coworker',
        'Professor': 'professor',
        'Other Person': 'coworker',
        'Security Guard': 'officer',
        'Bailiff': 'officer',
        'Prosecutor': 'officer',
    }

    # Map character IDs to premade sprite indices
    CHARACTER_SPRITES = {
        'player': 1,     # Default, can be overridden
        'officer': 15,
        'judge': 20,
        'clerk': 12,
        'manager': 14,
        'coworker': 8,
        'professor': 18,
    }

    # Character accent colors
    CHARACTER_COLORS = {
        'player': (100, 180, 100),     # Green
        'officer': (70, 100, 180),     # Blue
        'judge': (160, 120, 80),       # Brown/gold
        'clerk': (130, 130, 140),      # Gray
        'manager': (180, 130, 70),     # Orange
        'coworker': (100, 160, 180),   # Light blue
        'professor': (140, 110, 170),  # Purple
    }

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

        # Portrait system
        self.portraits_enabled = True
        self.portrait_cache = {}
        self.player_sprite_index = 1
        self.portrait_size = 100
        self.animation_time = 0

    def set_player_sprite(self, sprite_index):
        """Set the player's sprite index for portraits"""
        self.player_sprite_index = sprite_index
        if 'player' in self.portrait_cache:
            del self.portrait_cache['player']

    def _get_sprite_path(self, sprite_index):
        """Get path to premade character sprite"""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(
            base_path, 'assets', 'moderninteriors-win', '2_Characters',
            'Character_Generator', '0_Premade_Characters', '32x32',
            f'Premade_Character_32x32_{sprite_index:02d}.png'
        )

    def _load_portrait(self, character_id):
        """Load and cache a character portrait"""
        if character_id in self.portrait_cache:
            return self.portrait_cache[character_id]

        # Get sprite index
        if character_id == 'player':
            sprite_index = self.player_sprite_index
        else:
            sprite_index = self.CHARACTER_SPRITES.get(character_id, 1)

        try:
            sprite_path = self._get_sprite_path(sprite_index)

            if os.path.exists(sprite_path):
                spritesheet = pygame.image.load(sprite_path).convert_alpha()

                # Sprite sheet layout: 32x32 sprites
                # Row 0: idle animations (col 0=down/front, 1=left, 2=right, 3=up)
                # Extract the front-facing idle sprite (column 0, row 0)
                sprite_size = 32
                front_facing_rect = pygame.Rect(0, 0, sprite_size, sprite_size)

                raw_portrait = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
                raw_portrait.blit(spritesheet, (0, 0), front_facing_rect)

                # Scale up for portrait display (square aspect ratio)
                portrait_height = self.box_height - 20
                portrait_width = portrait_height  # Keep square for front-facing view
                scaled = pygame.transform.scale(raw_portrait, (portrait_width, portrait_height))

                self.portrait_cache[character_id] = scaled
                return scaled

        except Exception as e:
            pass

        # Fallback placeholder
        return self._create_placeholder(character_id)

    def _create_placeholder(self, character_id):
        """Create colored placeholder portrait"""
        color = self.CHARACTER_COLORS.get(character_id, (100, 100, 100))

        portrait_height = self.box_height - 20
        portrait_width = portrait_height  # Square for consistency

        surface = pygame.Surface((portrait_width, portrait_height), pygame.SRCALPHA)

        # Gradient background
        for y in range(portrait_height):
            shade = 1 - (y / portrait_height) * 0.3
            pygame.draw.line(surface,
                           (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade), 200),
                           (0, y), (portrait_width, y))

        # Initial letter
        font = pygame.font.Font(None, 48)
        initial = character_id[0].upper()
        text = font.render(initial, True, (255, 255, 255))
        text_rect = text.get_rect(center=(portrait_width // 2, portrait_height // 2))
        surface.blit(text, text_rect)

        self.portrait_cache[character_id] = surface
        return surface

    def show(self, speaker, text):
        """Display dialogue with speaker name and text"""
        self.active = True
        self.current_speaker = speaker
        self.current_text = text
        self.text_progress = 0
        self.wrap_text()

    def wrap_text(self):
        """Wrap text to fit in dialogue box (accounting for portrait)"""
        self.lines = []

        # Calculate available width
        character_id = self.SPEAKER_TO_CHARACTER.get(self.current_speaker) if self.current_speaker else None
        has_portrait = self.portraits_enabled and character_id is not None

        if has_portrait:
            portrait_height = self.box_height - 20
            portrait_width = portrait_height  # Square portrait
            available_width = self.box_width - portrait_width - 60
        else:
            available_width = self.box_width - 40

        words = self.current_text.split(' ')
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_surface = self.text_font.render(test_line, True, self.text_color)

            if text_surface.get_width() > available_width:
                if current_line:
                    self.lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            self.lines.append(current_line.strip())

    def update(self, dt):
        """Update typewriter effect and animations"""
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
        """Draw the dialogue box with integrated portrait"""
        if not self.active:
            return

        # Determine if we should show a portrait
        character_id = self.SPEAKER_TO_CHARACTER.get(self.current_speaker) if self.current_speaker else None
        has_portrait = self.portraits_enabled and character_id is not None
        is_narrator = self.current_speaker is None or self.current_speaker == ""

        # Draw shadow
        shadow_offset = 4
        shadow_rect = pygame.Rect(self.box_x + shadow_offset, self.box_y + shadow_offset,
                                 self.box_width, self.box_height)
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

        # Text positioning
        text_x = self.box_x + 20
        text_y_offset = 15

        # Draw portrait if available
        if has_portrait:
            portrait = self._load_portrait(character_id)
            color = self.CHARACTER_COLORS.get(character_id, (100, 100, 100))

            portrait_margin = 10
            portrait_x = self.box_x + portrait_margin
            portrait_y = self.box_y + portrait_margin
            portrait_height = self.box_height - portrait_margin * 2
            portrait_width = portrait_height  # Square portrait for front-facing view

            # Portrait background
            portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_width, portrait_height)
            pygame.draw.rect(screen, (15, 18, 25), portrait_rect, border_radius=8)

            # Colored accent border
            pygame.draw.rect(screen, color, portrait_rect, 3, border_radius=8)

            # Speaking bounce animation
            bounce = math.sin(self.animation_time * 6) * 2

            # Draw portrait
            if portrait:
                # Scale to fit
                scaled_w = portrait_width - 8
                scaled_h = portrait_height - 8
                scaled_portrait = pygame.transform.scale(portrait, (scaled_w, scaled_h))
                screen.blit(scaled_portrait, (portrait_x + 4, portrait_y + 4 + bounce))

            # Accent divider line
            divider_x = portrait_x + portrait_width + 8
            pygame.draw.line(screen, (*color, 150),
                           (divider_x, self.box_y + 15),
                           (divider_x, self.box_y + self.box_height - 15), 2)

            # Adjust text position
            text_x = divider_x + 12

        # Draw speaker name
        if self.current_speaker and not is_narrator:
            if character_id:
                name_color = self.CHARACTER_COLORS.get(character_id, self.speaker_color)
            else:
                name_color = self.speaker_color

            speaker_surf = self.speaker_font.render(self.current_speaker, True, name_color)
            screen.blit(speaker_surf, (text_x, self.box_y + text_y_offset))
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
            screen.blit(text_surf, (text_x, self.box_y + text_y_offset + i * 28))
            char_count += len(line) + 1

        # Draw continue prompt
        if self.text_progress >= len(self.current_text):
            # Pulsing triangle indicator
            pulse = abs(math.sin(self.animation_time * 3)) * 0.5 + 0.5
            indicator_color = (int(100 + 100 * pulse), int(100 + 100 * pulse), int(100 + 100 * pulse))

            indicator_x = self.box_x + self.box_width - 30
            indicator_y = self.box_y + self.box_height - 22

            points = [
                (indicator_x, indicator_y - 6),
                (indicator_x + 10, indicator_y - 6),
                (indicator_x + 5, indicator_y + 2)
            ]
            pygame.draw.polygon(screen, indicator_color, points)

            # Small prompt text
            prompt_surf = self.prompt_font.render("SPACE", True, (120, 120, 130))
            screen.blit(prompt_surf, (indicator_x - 35, indicator_y - 5))

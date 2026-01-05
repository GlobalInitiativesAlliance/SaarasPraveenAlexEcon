"""
Dialogue Portrait System for Part 3 - Legal System
Uses actual character sprites integrated into the dialogue box
Visual novel / RPG style with portrait on left of dialogue
"""
import pygame
import os
import math
import time
from enum import Enum


class Emotion(Enum):
    """Character emotions for portrait expressions"""
    NEUTRAL = "neutral"
    WORRIED = "worried"
    SCARED = "scared"
    DETERMINED = "determined"
    RELIEVED = "relieved"
    STERN = "stern"
    DISAPPOINTED = "disappointed"
    SYMPATHETIC = "sympathetic"
    SUSPICIOUS = "suspicious"
    AGGRESSIVE = "aggressive"
    DISMISSIVE = "dismissive"
    ANNOYED = "annoyed"
    UNDERSTANDING = "understanding"
    RUSHED = "rushed"
    FRIENDLY = "friendly"
    CONCERNED = "concerned"


class PortraitRenderer:
    """
    Renders character portraits integrated into dialogue box
    Uses actual character sprites from the game assets
    """

    # Map character IDs to premade sprite indices (1-32 available)
    CHARACTER_SPRITES = {
        'player': None,  # Uses selected character
        'officer': 15,   # Police officer look
        'judge': 20,     # Formal/authority look
        'clerk': 12,     # Office worker look
        'manager': 14,   # Business look
        'coworker': 8,   # Casual look
        'professor': 18, # Academic look
    }

    # Character display names
    CHARACTER_NAMES = {
        'player': 'You',
        'officer': 'Officer',
        'judge': 'Judge',
        'clerk': 'Clerk',
        'manager': 'Manager',
        'coworker': 'Classmate',
        'professor': 'Professor',
    }

    # Character accent colors (for border highlighting)
    CHARACTER_COLORS = {
        'player': (100, 180, 100),     # Green - protagonist
        'officer': (70, 100, 180),     # Blue - authority
        'judge': (160, 120, 80),       # Brown/gold - judicial
        'clerk': (130, 130, 140),      # Gray - bureaucrat
        'manager': (180, 130, 70),     # Orange - business
        'coworker': (100, 160, 180),   # Light blue - friendly
        'professor': (140, 110, 170),  # Purple - academic
    }

    def __init__(self):
        self.player_sprite_index = 1
        self.portrait_cache = {}
        self.speaking_timer = 0
        self.animation_time = 0

        # Portrait size
        self.portrait_size = 96

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.name_font = pygame.font.Font(None, 24)
            self.text_font = pygame.font.Font(None, 26)
        except:
            self.name_font = pygame.font.Font(None, 24)
            self.text_font = pygame.font.Font(None, 26)

    def set_player_sprite(self, sprite_index):
        """Set which sprite the player character uses"""
        self.player_sprite_index = sprite_index
        # Clear player portrait cache
        if 'player' in self.portrait_cache:
            del self.portrait_cache['player']

    def _get_sprite_path(self, sprite_index):
        """Get the path to a premade character sprite"""
        base_path = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(
            base_path, 'assets', 'moderninteriors-win', '2_Characters',
            'Character_Generator', '0_Premade_Characters', '32x32',
            f'Premade_Character_32x32_{sprite_index:02d}.png'
        )

    def _load_portrait(self, character_id):
        """Load and cache a character portrait from sprite"""
        if character_id in self.portrait_cache:
            return self.portrait_cache[character_id]

        # Determine sprite index
        if character_id == 'player':
            sprite_index = self.player_sprite_index
        else:
            sprite_index = self.CHARACTER_SPRITES.get(character_id, 1)

        try:
            sprite_path = self._get_sprite_path(sprite_index)

            if os.path.exists(sprite_path):
                spritesheet = pygame.image.load(sprite_path).convert_alpha()

                # Extract head/upper body from idle-down pose (first frame)
                # Characters are 32 wide, we want the top portion
                head_rect = pygame.Rect(0, 0, 32, 44)

                raw_portrait = pygame.Surface((32, 44), pygame.SRCALPHA)
                raw_portrait.blit(spritesheet, (0, 0), head_rect)

                # Scale up for display
                scaled = pygame.transform.scale(raw_portrait, (self.portrait_size, int(self.portrait_size * 1.375)))

                self.portrait_cache[character_id] = scaled
                return scaled

        except Exception as e:
            print(f"[PORTRAIT] Error loading {character_id}: {e}")

        # Fallback: colored placeholder with initial
        return self._create_placeholder(character_id)

    def _create_placeholder(self, character_id):
        """Create a colored placeholder portrait"""
        color = self.CHARACTER_COLORS.get(character_id, (100, 100, 100))
        name = self.CHARACTER_NAMES.get(character_id, '?')

        surface = pygame.Surface((self.portrait_size, int(self.portrait_size * 1.375)), pygame.SRCALPHA)

        # Background with gradient effect
        for y in range(surface.get_height()):
            alpha = 200 - int(y * 0.3)
            shade = 1 - (y / surface.get_height()) * 0.3
            pygame.draw.line(surface,
                           (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade), alpha),
                           (0, y), (surface.get_width(), y))

        # Initial letter
        font = pygame.font.Font(None, 56)
        initial = name[0].upper()
        text = font.render(initial, True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 10))
        surface.blit(text, text_rect)

        self.portrait_cache[character_id] = surface
        return surface

    def update(self, dt):
        """Update animations"""
        self.animation_time += dt

    def draw_portrait(self, screen, character_id, position='left',
                     emotion=None, is_speaking=False):
        """
        Draw a character portrait (for backwards compatibility)
        This now draws the portrait in its traditional floating position
        """
        portrait = self._load_portrait(character_id)
        if not portrait:
            return

        screen_width, screen_height = screen.get_size()
        margin = 50

        # Calculate position
        if position == 'left':
            x = margin
        else:
            x = screen_width - self.portrait_size - margin

        y = screen_height - 300 - int(self.portrait_size * 1.375)

        # Speaking bounce
        bounce = 0
        if is_speaking:
            bounce = math.sin(self.animation_time * 6) * 4

        # Get character color
        color = self.CHARACTER_COLORS.get(character_id, (100, 100, 100))

        # Portrait frame
        frame_rect = pygame.Rect(x - 6, y - 6 + bounce,
                                self.portrait_size + 12, int(self.portrait_size * 1.375) + 12)

        # Glow if speaking
        if is_speaking:
            glow_rect = frame_rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color, 80), glow_surface.get_rect(), border_radius=12)
            screen.blit(glow_surface, glow_rect.topleft)

        # Frame background
        pygame.draw.rect(screen, (30, 35, 45), frame_rect, border_radius=10)
        pygame.draw.rect(screen, color if is_speaking else (60, 65, 75),
                        frame_rect, 3, border_radius=10)

        # Draw portrait
        screen.blit(portrait, (x, y + bounce))

        # Name plate
        name = self.CHARACTER_NAMES.get(character_id, '???')
        name_surface = self.name_font.render(name, True, (255, 255, 255))
        name_bg = pygame.Rect(x - 6, frame_rect.bottom - 28,
                             self.portrait_size + 12, 28)
        pygame.draw.rect(screen, color if is_speaking else (50, 55, 65),
                        name_bg, border_bottom_left_radius=10, border_bottom_right_radius=10)
        name_rect = name_surface.get_rect(center=name_bg.center)
        screen.blit(name_surface, name_rect)


class IntegratedDialogueBox:
    """
    Dialogue box with portrait integrated on the left side
    More polished visual novel / RPG style
    """

    def __init__(self, portrait_renderer):
        self.portrait_renderer = portrait_renderer
        self.animation_time = 0

        # Box settings
        self.box_height = 150
        self.box_margin = 30
        self.portrait_size = 100

        # Fonts
        self.speaker_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 26)

    def update(self, dt):
        """Update animations"""
        self.animation_time += dt
        self.portrait_renderer.update(dt)

    def draw(self, screen, speaker, text, character_id=None):
        """
        Draw dialogue box with integrated portrait

        Args:
            screen: Pygame surface
            speaker: Speaker name (None for narrator)
            text: Dialogue text
            character_id: Character ID for portrait (None for no portrait)
        """
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        is_narrator = speaker is None
        has_portrait = character_id is not None and not is_narrator

        # Box dimensions
        box_width = screen_width - self.box_margin * 2
        box_x = self.box_margin
        box_y = screen_height - self.box_height - 25

        # Draw shadow
        shadow_offset = 4
        shadow_rect = pygame.Rect(box_x + shadow_offset, box_y + shadow_offset,
                                 box_width, self.box_height)
        shadow_surface = pygame.Surface((box_width, self.box_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80),
                        (0, 0, box_width, self.box_height), border_radius=12)
        screen.blit(shadow_surface, (box_x + shadow_offset, box_y + shadow_offset))

        # Main box background
        box_surface = pygame.Surface((box_width, self.box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (20, 25, 35, 245),
                        (0, 0, box_width, self.box_height), border_radius=12)
        screen.blit(box_surface, (box_x, box_y))

        # Border
        pygame.draw.rect(screen, (60, 70, 90),
                        (box_x, box_y, box_width, self.box_height), 2, border_radius=12)

        # Portrait section (left side)
        text_x = box_x + 20
        text_width = box_width - 40

        if has_portrait:
            portrait = self.portrait_renderer._load_portrait(character_id)
            color = self.portrait_renderer.CHARACTER_COLORS.get(character_id, (100, 100, 100))

            # Portrait container
            portrait_margin = 10
            portrait_x = box_x + portrait_margin
            portrait_height = self.box_height - portrait_margin * 2
            portrait_width = int(portrait_height * 0.75)

            # Portrait background
            portrait_rect = pygame.Rect(portrait_x, box_y + portrait_margin,
                                       portrait_width, portrait_height)
            pygame.draw.rect(screen, (15, 18, 25), portrait_rect, border_radius=8)

            # Colored accent border
            pygame.draw.rect(screen, color, portrait_rect, 3, border_radius=8)

            # Speaking bounce
            bounce = math.sin(self.animation_time * 6) * 2

            # Scale and draw portrait
            if portrait:
                scaled_portrait = pygame.transform.scale(portrait, (portrait_width - 8, portrait_height - 8))
                screen.blit(scaled_portrait, (portrait_x + 4, box_y + portrait_margin + 4 + bounce))

            # Adjust text area
            text_x = portrait_x + portrait_width + 15
            text_width = box_width - portrait_width - 45

            # Accent line from portrait
            accent_x = portrait_x + portrait_width + 5
            pygame.draw.line(screen, (*color, 150),
                           (accent_x, box_y + 15), (accent_x, box_y + self.box_height - 15), 2)

        # Speaker name
        text_y_start = box_y + 18
        if speaker and not is_narrator:
            if character_id:
                name_color = self.portrait_renderer.CHARACTER_COLORS.get(character_id, (200, 180, 100))
            else:
                name_color = (200, 180, 100)

            name_surface = self.speaker_font.render(speaker, True, name_color)
            screen.blit(name_surface, (text_x, text_y_start))
            text_y_start = box_y + 48
        elif is_narrator:
            text_y_start = box_y + 30

        # Dialogue text
        text_color = (170, 175, 190) if is_narrator else (240, 240, 245)
        lines = self._wrap_text(text, self.text_font, text_width)

        for i, line in enumerate(lines[:3]):  # Max 3 lines
            line_surface = self.text_font.render(line, True, text_color)
            screen.blit(line_surface, (text_x, text_y_start + i * 28))

        # Continue indicator (pulsing triangle)
        pulse = abs(math.sin(self.animation_time * 3)) * 0.5 + 0.5
        indicator_color = (int(100 + 100 * pulse), int(100 + 100 * pulse), int(100 + 100 * pulse))
        indicator_x = box_x + box_width - 30
        indicator_y = box_y + self.box_height - 22

        # Draw triangle
        points = [
            (indicator_x, indicator_y - 6),
            (indicator_x + 10, indicator_y - 6),
            (indicator_x + 5, indicator_y + 2)
        ]
        pygame.draw.polygon(screen, indicator_color, points)

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit width"""
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


# Global instances
portrait_renderer = PortraitRenderer()
integrated_dialogue = IntegratedDialogueBox(portrait_renderer)


def draw_dialogue_with_portrait(screen, speaker, text, speaker_to_char_map=None):
    """
    Convenience function to draw dialogue with integrated portrait

    Args:
        screen: Pygame surface
        speaker: Speaker name (e.g., "Officer", "You", None for narrator)
        text: Dialogue text
        speaker_to_char_map: Dict mapping speaker names to character IDs
    """
    # Determine character ID from speaker
    character_id = None

    if speaker and speaker_to_char_map:
        character_id = speaker_to_char_map.get(speaker)
    elif speaker:
        # Default mappings
        default_map = {
            'You': 'player',
            'Officer': 'officer',
            'Judge': 'judge',
            'Clerk': 'clerk',
            'Manager': 'manager',
            'Coworker': 'coworker',
            'Classmate': 'coworker',
            'Professor': 'professor',
            'Other Person': 'coworker',
        }
        character_id = default_map.get(speaker)

    integrated_dialogue.update(1/60)
    integrated_dialogue.draw(screen, speaker, text, character_id)

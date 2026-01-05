"""
Global Dialogue Portrait System
Renders floating character portraits above dialogue box
Used by all narrative interiors across all game parts
"""
import pygame
import os
import math
import time


class DialoguePortraitRenderer:
    """
    Renders character portraits floating above the dialogue box
    Shows speaker on one side with name plate and speaking animation
    """

    # Map speaker names to character IDs
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
        'Person Ahead': 'coworker',
        'Receptionist': 'clerk',
        'Doctor': 'professor',
        'Nurse': 'clerk',
        'Caseworker': 'clerk',
        'Boss': 'manager',
        'Landlord': 'manager',
        'Friend': 'coworker',
        'Roommate': 'coworker',
    }

    # Map character IDs to premade sprite indices
    CHARACTER_SPRITES = {
        'player': 1,      # Default, overridden by selected character
        'officer': 15,    # Authority look
        'judge': 20,      # Formal look
        'clerk': 12,      # Office worker
        'manager': 14,    # Business look
        'coworker': 8,    # Casual look
        'professor': 18,  # Academic look
    }

    # Character accent colors
    CHARACTER_COLORS = {
        'player': (100, 180, 100),     # Green - protagonist
        'officer': (70, 100, 180),     # Blue - authority
        'judge': (160, 120, 80),       # Brown/gold - judicial
        'clerk': (130, 130, 140),      # Gray - bureaucrat
        'manager': (180, 130, 70),     # Orange - business
        'coworker': (100, 160, 180),   # Light blue - friendly
        'professor': (140, 110, 170),  # Purple - academic
    }

    # Character display names
    CHARACTER_NAMES = {
        'player': 'You',
        'officer': 'Officer',
        'judge': 'Judge',
        'clerk': 'Clerk',
        'manager': 'Manager',
        'coworker': 'Friend',
        'professor': 'Professor',
    }

    def __init__(self):
        self.portrait_cache = {}
        self.player_sprite_index = 1
        self.animation_time = 0
        self.speaking_timer = 0

        # Portrait dimensions
        self.portrait_size = 96

        # Fonts
        self.name_font = pygame.font.Font(None, 22)

    def set_player_sprite(self, sprite_index):
        """Set which sprite the player character uses"""
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

                # Extract front-facing idle sprite (column 0, row 0)
                # Sprites are 32x32 per frame
                sprite_size = 32
                front_rect = pygame.Rect(0, 0, sprite_size, sprite_size)

                raw_portrait = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
                raw_portrait.blit(spritesheet, (0, 0), front_rect)

                # Scale up
                scaled = pygame.transform.scale(raw_portrait, (self.portrait_size, self.portrait_size))

                self.portrait_cache[character_id] = scaled
                return scaled

        except Exception as e:
            print(f"[PORTRAIT] Error loading {character_id}: {e}")

        # Fallback placeholder
        return self._create_placeholder(character_id)

    def _create_placeholder(self, character_id):
        """Create colored placeholder portrait"""
        color = self.CHARACTER_COLORS.get(character_id, (100, 100, 100))
        name = self.CHARACTER_NAMES.get(character_id, '?')

        surface = pygame.Surface((self.portrait_size, self.portrait_size), pygame.SRCALPHA)

        # Gradient background
        for y in range(self.portrait_size):
            shade = 1 - (y / self.portrait_size) * 0.3
            pygame.draw.line(surface,
                           (int(color[0] * shade), int(color[1] * shade), int(color[2] * shade), 200),
                           (0, y), (self.portrait_size, y))

        # Initial letter
        font = pygame.font.Font(None, 56)
        initial = name[0].upper()
        text = font.render(initial, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.portrait_size // 2, self.portrait_size // 2))
        surface.blit(text, text_rect)

        self.portrait_cache[character_id] = surface
        return surface

    def update(self, dt):
        """Update animations"""
        self.animation_time += dt

    def get_character_from_speaker(self, speaker):
        """Get character ID from speaker name"""
        if not speaker:
            return None
        return self.SPEAKER_TO_CHARACTER.get(speaker)

    def draw_portrait(self, screen, character_id, position='left', is_speaking=False):
        """
        Draw a floating portrait above the dialogue box

        Args:
            screen: Pygame surface
            character_id: Character ID to draw
            position: 'left' or 'right'
            is_speaking: Whether this character is speaking (adds bounce)
        """
        if not character_id:
            return

        portrait = self._load_portrait(character_id)
        if not portrait:
            return

        screen_width, screen_height = screen.get_size()
        margin = 50

        # Position above dialogue box
        if position == 'left':
            x = margin
        else:
            x = screen_width - self.portrait_size - margin

        # Y position - above the dialogue box (which is at bottom - 170)
        y = screen_height - 170 - self.portrait_size - 30

        # Speaking bounce animation
        bounce = 0
        if is_speaking:
            bounce = math.sin(self.animation_time * 6) * 4

        # Get character color
        color = self.CHARACTER_COLORS.get(character_id, (100, 100, 100))

        # Portrait frame dimensions
        frame_padding = 6
        frame_rect = pygame.Rect(
            x - frame_padding,
            y - frame_padding + bounce,
            self.portrait_size + frame_padding * 2,
            self.portrait_size + frame_padding * 2
        )

        # Glow effect when speaking
        if is_speaking:
            glow_rect = frame_rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color, 60), glow_surface.get_rect(), border_radius=12)
            screen.blit(glow_surface, glow_rect.topleft)

        # Frame background
        pygame.draw.rect(screen, (25, 30, 40), frame_rect, border_radius=10)

        # Colored border
        border_color = color if is_speaking else (60, 65, 75)
        border_width = 3 if is_speaking else 2
        pygame.draw.rect(screen, border_color, frame_rect, border_width, border_radius=10)

        # Draw portrait
        screen.blit(portrait, (x, y + bounce))

        # Name plate
        name = self.CHARACTER_NAMES.get(character_id, 'Unknown')
        if character_id in self.SPEAKER_TO_CHARACTER.values():
            # Find the speaker name for this character
            for speaker, char_id in self.SPEAKER_TO_CHARACTER.items():
                if char_id == character_id and speaker != 'You':
                    name = speaker
                    break

        name_surface = self.name_font.render(name, True, (255, 255, 255))
        name_bg = pygame.Rect(
            x - frame_padding,
            frame_rect.bottom - 26 + bounce,
            self.portrait_size + frame_padding * 2,
            26
        )
        pygame.draw.rect(screen, color if is_speaking else (45, 50, 60),
                        name_bg, border_bottom_left_radius=10, border_bottom_right_radius=10)
        name_rect = name_surface.get_rect(center=name_bg.center)
        screen.blit(name_surface, name_rect)

    def draw_dialogue_portraits(self, screen, speaker, speaker_map=None):
        """
        Draw portraits based on current speaker

        Args:
            screen: Pygame surface
            speaker: Current speaker name
            speaker_map: Optional custom speaker->character mapping
        """
        if not speaker:
            return

        # Get character ID
        if speaker_map:
            character_id = speaker_map.get(speaker)
        else:
            character_id = self.SPEAKER_TO_CHARACTER.get(speaker)

        if not character_id:
            return

        # Draw player on left, other character on right
        if character_id == 'player':
            self.draw_portrait(screen, 'player', 'left', is_speaking=True)
        else:
            # Draw both - player listening, other speaking
            self.draw_portrait(screen, 'player', 'left', is_speaking=False)
            self.draw_portrait(screen, character_id, 'right', is_speaking=True)


# Global instance
dialogue_portraits = DialoguePortraitRenderer()

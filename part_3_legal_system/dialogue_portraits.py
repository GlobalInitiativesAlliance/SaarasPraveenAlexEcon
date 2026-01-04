"""
Dialogue Portrait System for Part 3 Legal System
Renders character portraits with emotion states during dialogue sequences
Provides visual representation of characters with speaking indicators
"""

import pygame
import math
import time
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class Emotion(Enum):
    """Available emotion states for characters"""
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


@dataclass
class CharacterConfig:
    """Configuration for a character's visual appearance"""
    name: str
    primary_color: Tuple[int, int, int]
    secondary_color: Tuple[int, int, int]
    silhouette_type: str  # 'authority', 'young', 'professional', 'casual'
    default_emotion: Emotion = Emotion.NEUTRAL


class PortraitRenderer:
    """
    Renders stylized character portraits for dialogue scenes

    Features:
    - Silhouette-style portraits with color accents
    - Multiple emotion states per character
    - Speaking animation (gentle bounce)
    - Emotion indicator icons
    - Name plates with speaker highlighting
    - Smooth transitions between emotions
    """

    # Character definitions
    CHARACTERS: Dict[str, CharacterConfig] = {
        'judge': CharacterConfig(
            name="Judge Thompson",
            primary_color=(70, 50, 90),      # Deep purple (authority)
            secondary_color=(180, 160, 100),  # Gold accents
            silhouette_type='authority',
            default_emotion=Emotion.STERN
        ),
        'officer': CharacterConfig(
            name="Officer Martinez",
            primary_color=(40, 60, 100),      # Navy blue
            secondary_color=(180, 180, 190),  # Badge silver
            silhouette_type='authority',
            default_emotion=Emotion.NEUTRAL
        ),
        'player': CharacterConfig(
            name="You",
            primary_color=(80, 100, 80),      # Muted green
            secondary_color=(200, 180, 160),  # Skin tone neutral
            silhouette_type='young',
            default_emotion=Emotion.WORRIED
        ),
        'manager': CharacterConfig(
            name="Manager",
            primary_color=(100, 70, 50),      # Brown (work uniform)
            secondary_color=(60, 60, 70),     # Dark accents
            silhouette_type='professional',
            default_emotion=Emotion.RUSHED
        ),
        'coworker': CharacterConfig(
            name="Alex",
            primary_color=(100, 70, 50),      # Same work uniform
            secondary_color=(150, 130, 110),
            silhouette_type='casual',
            default_emotion=Emotion.FRIENDLY
        ),
        'professor': CharacterConfig(
            name="Professor Davis",
            primary_color=(60, 70, 80),       # Professional gray
            secondary_color=(140, 100, 70),   # Leather/book tones
            silhouette_type='professional',
            default_emotion=Emotion.UNDERSTANDING
        ),
        'clerk': CharacterConfig(
            name="Court Clerk",
            primary_color=(80, 80, 90),       # Office gray
            secondary_color=(150, 140, 130),
            silhouette_type='professional',
            default_emotion=Emotion.DISMISSIVE
        )
    }

    # Emotion to icon mapping
    EMOTION_ICONS: Dict[Emotion, str] = {
        Emotion.NEUTRAL: "",
        Emotion.WORRIED: "...",
        Emotion.SCARED: "!",
        Emotion.DETERMINED: "!",
        Emotion.RELIEVED: "~",
        Emotion.STERN: "",
        Emotion.DISAPPOINTED: "...",
        Emotion.SYMPATHETIC: "",
        Emotion.SUSPICIOUS: "?",
        Emotion.AGGRESSIVE: "!!",
        Emotion.DISMISSIVE: "...",
        Emotion.ANNOYED: "!",
        Emotion.UNDERSTANDING: "",
        Emotion.RUSHED: "!!",
        Emotion.FRIENDLY: "",
        Emotion.CONCERNED: "?",
    }

    def __init__(self):
        self.fonts = {}
        self._init_fonts()

        # Animation state
        self.speaking_character: Optional[str] = None
        self.speaking_timer = 0
        self.current_emotions: Dict[str, Emotion] = {}
        self.emotion_transition_progress: Dict[str, float] = {}
        self.portrait_positions: Dict[str, Tuple[int, int]] = {}

        # Cache for rendered portraits
        self._portrait_cache: Dict[str, pygame.Surface] = {}

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.fonts['name'] = pygame.font.SysFont('SF Pro Display', 18, bold=True)
            self.fonts['emotion'] = pygame.font.SysFont('SF Pro Display', 16)
            self.fonts['icon'] = pygame.font.SysFont('SF Pro Display', 24, bold=True)
        except:
            self.fonts['name'] = pygame.font.Font(None, 22)
            self.fonts['emotion'] = pygame.font.Font(None, 18)
            self.fonts['icon'] = pygame.font.Font(None, 28)

    def set_speaking(self, character_id: Optional[str]):
        """Set which character is currently speaking"""
        self.speaking_character = character_id
        self.speaking_timer = time.time()

    def set_emotion(self, character_id: str, emotion: Emotion):
        """Set a character's emotion with smooth transition"""
        if character_id in self.current_emotions:
            if self.current_emotions[character_id] != emotion:
                self.emotion_transition_progress[character_id] = 0
        self.current_emotions[character_id] = emotion

    def update(self, dt: float):
        """Update portrait animations"""
        # Update emotion transitions
        for char_id in list(self.emotion_transition_progress.keys()):
            self.emotion_transition_progress[char_id] = min(
                1.0,
                self.emotion_transition_progress[char_id] + dt * 3
            )
            if self.emotion_transition_progress[char_id] >= 1.0:
                del self.emotion_transition_progress[char_id]

    def draw_portrait(self, screen: pygame.Surface, character_id: str,
                     position: str = 'left', emotion: Optional[Emotion] = None,
                     is_speaking: bool = False) -> pygame.Rect:
        """
        Draw a character portrait

        Args:
            screen: Pygame surface to draw on
            character_id: ID of character to draw
            position: 'left' or 'right' side of screen
            emotion: Override emotion (uses default if None)
            is_speaking: Whether this character is currently speaking

        Returns:
            Rect of the portrait area
        """
        if character_id not in self.CHARACTERS:
            return pygame.Rect(0, 0, 0, 0)

        config = self.CHARACTERS[character_id]
        current_emotion = emotion or self.current_emotions.get(
            character_id, config.default_emotion
        )

        # Portrait dimensions
        portrait_width = 180
        portrait_height = 220
        margin = 40

        # Calculate position
        screen_width, screen_height = screen.get_size()
        if position == 'left':
            x = margin
        else:
            x = screen_width - portrait_width - margin

        # Position above dialogue box
        y = screen_height - 280 - portrait_height

        # Store position for future reference
        self.portrait_positions[character_id] = (x, y)

        # Create portrait surface
        portrait_rect = pygame.Rect(x, y, portrait_width, portrait_height)

        # Draw portrait background/frame
        self._draw_portrait_frame(screen, portrait_rect, config, is_speaking)

        # Draw character silhouette
        self._draw_silhouette(screen, portrait_rect, config, current_emotion, is_speaking)

        # Draw name plate
        self._draw_name_plate(screen, portrait_rect, config, is_speaking)

        # Draw emotion indicator
        if current_emotion != Emotion.NEUTRAL:
            self._draw_emotion_indicator(screen, portrait_rect, current_emotion)

        # Draw speaking indicator
        if is_speaking:
            self._draw_speaking_indicator(screen, portrait_rect)

        return portrait_rect

    def _draw_portrait_frame(self, screen: pygame.Surface, rect: pygame.Rect,
                            config: CharacterConfig, is_speaking: bool):
        """Draw the portrait frame/background"""
        # Outer glow when speaking
        if is_speaking:
            glow_rect = rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (*config.primary_color, 60)
            pygame.draw.rect(glow_surface, glow_color,
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=12)
            screen.blit(glow_surface, glow_rect.topleft)

        # Frame background
        pygame.draw.rect(screen, (25, 28, 35, 220), rect, border_radius=10)

        # Accent border
        border_color = config.primary_color if is_speaking else (60, 65, 75)
        border_width = 3 if is_speaking else 2
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=10)

    def _draw_silhouette(self, screen: pygame.Surface, rect: pygame.Rect,
                        config: CharacterConfig, emotion: Emotion,
                        is_speaking: bool):
        """Draw the character silhouette based on type"""
        # Calculate speaking bounce
        bounce_offset = 0
        if is_speaking:
            elapsed = time.time() - self.speaking_timer
            bounce_offset = int(math.sin(elapsed * 8) * 3)

        # Silhouette area
        silhouette_rect = pygame.Rect(
            rect.x + 20,
            rect.y + 15 + bounce_offset,
            rect.width - 40,
            rect.height - 60
        )

        # Create silhouette surface
        silhouette = pygame.Surface((silhouette_rect.width, silhouette_rect.height), pygame.SRCALPHA)

        # Draw based on silhouette type
        if config.silhouette_type == 'authority':
            self._draw_authority_silhouette(silhouette, config, emotion)
        elif config.silhouette_type == 'young':
            self._draw_young_silhouette(silhouette, config, emotion)
        elif config.silhouette_type == 'professional':
            self._draw_professional_silhouette(silhouette, config, emotion)
        else:  # casual
            self._draw_casual_silhouette(silhouette, config, emotion)

        screen.blit(silhouette, silhouette_rect.topleft)

    def _draw_authority_silhouette(self, surface: pygame.Surface,
                                   config: CharacterConfig, emotion: Emotion):
        """Draw authority figure silhouette (judge, officer)"""
        w, h = surface.get_size()
        color = (*config.primary_color, 200)
        accent = (*config.secondary_color, 180)

        # Head
        head_radius = w // 4
        head_x = w // 2
        head_y = h // 4
        pygame.draw.circle(surface, color, (head_x, head_y), head_radius)

        # Hat/cap (for authority)
        hat_rect = pygame.Rect(head_x - head_radius - 5, head_y - head_radius - 5,
                              head_radius * 2 + 10, head_radius // 2)
        pygame.draw.ellipse(surface, accent, hat_rect)

        # Shoulders (broad)
        shoulder_width = w - 20
        shoulder_y = h // 3 + 10
        pygame.draw.ellipse(surface, color,
                          (10, shoulder_y, shoulder_width, h // 3))

        # Torso
        pygame.draw.rect(surface, color,
                        (w // 4, shoulder_y + 20, w // 2, h // 2))

        # Badge/detail
        badge_x = w // 2 - 10
        badge_y = shoulder_y + 30
        pygame.draw.circle(surface, accent, (badge_x, badge_y), 8)

        # Expression based on emotion
        self._draw_expression(surface, head_x, head_y, head_radius, emotion)

    def _draw_young_silhouette(self, surface: pygame.Surface,
                               config: CharacterConfig, emotion: Emotion):
        """Draw young person silhouette (player)"""
        w, h = surface.get_size()
        color = (*config.primary_color, 200)

        # Head (slightly smaller for youth)
        head_radius = w // 5
        head_x = w // 2
        head_y = h // 4
        pygame.draw.circle(surface, color, (head_x, head_y), head_radius)

        # Hair suggestion
        hair_rect = pygame.Rect(head_x - head_radius, head_y - head_radius - 5,
                               head_radius * 2, head_radius)
        pygame.draw.arc(surface, (*config.secondary_color, 150), hair_rect,
                       0, math.pi, 3)

        # Shoulders (narrower)
        shoulder_width = w - 40
        shoulder_y = h // 3 + 5
        pygame.draw.ellipse(surface, color,
                          (20, shoulder_y, shoulder_width, h // 4))

        # Torso (casual clothes indication)
        pygame.draw.rect(surface, color,
                        (w // 4 + 5, shoulder_y + 15, w // 2 - 10, h // 2))

        # Expression
        self._draw_expression(surface, head_x, head_y, head_radius, emotion)

    def _draw_professional_silhouette(self, surface: pygame.Surface,
                                      config: CharacterConfig, emotion: Emotion):
        """Draw professional silhouette (manager, professor, clerk)"""
        w, h = surface.get_size()
        color = (*config.primary_color, 200)
        accent = (*config.secondary_color, 180)

        # Head
        head_radius = w // 5
        head_x = w // 2
        head_y = h // 4
        pygame.draw.circle(surface, color, (head_x, head_y), head_radius)

        # Collar/tie detail
        collar_y = head_y + head_radius + 5
        pygame.draw.polygon(surface, accent, [
            (head_x - 15, collar_y),
            (head_x, collar_y + 20),
            (head_x + 15, collar_y)
        ])

        # Shoulders
        shoulder_width = w - 30
        shoulder_y = h // 3
        pygame.draw.ellipse(surface, color,
                          (15, shoulder_y, shoulder_width, h // 4))

        # Torso (suit-like)
        pygame.draw.rect(surface, color,
                        (w // 4, shoulder_y + 15, w // 2, h // 2))

        # Expression
        self._draw_expression(surface, head_x, head_y, head_radius, emotion)

    def _draw_casual_silhouette(self, surface: pygame.Surface,
                                config: CharacterConfig, emotion: Emotion):
        """Draw casual silhouette (coworker)"""
        w, h = surface.get_size()
        color = (*config.primary_color, 200)

        # Head
        head_radius = w // 5
        head_x = w // 2
        head_y = h // 4
        pygame.draw.circle(surface, color, (head_x, head_y), head_radius)

        # Shoulders (relaxed)
        shoulder_width = w - 35
        shoulder_y = h // 3 + 5
        pygame.draw.ellipse(surface, color,
                          (17, shoulder_y, shoulder_width, h // 4))

        # Torso
        pygame.draw.rect(surface, color,
                        (w // 4, shoulder_y + 15, w // 2, h // 2))

        # Expression
        self._draw_expression(surface, head_x, head_y, head_radius, emotion)

    def _draw_expression(self, surface: pygame.Surface, head_x: int, head_y: int,
                        head_radius: int, emotion: Emotion):
        """Draw facial expression indicators based on emotion"""
        eye_y = head_y - 2
        eye_spacing = head_radius // 2

        # Eye positions
        left_eye_x = head_x - eye_spacing
        right_eye_x = head_x + eye_spacing

        # Base eye shape varies by emotion
        if emotion in [Emotion.SCARED, Emotion.WORRIED]:
            # Wide eyes
            pygame.draw.circle(surface, (40, 40, 50), (left_eye_x, eye_y), 4)
            pygame.draw.circle(surface, (40, 40, 50), (right_eye_x, eye_y), 4)
            # Eyebrows raised
            pygame.draw.arc(surface, (30, 30, 40),
                          (left_eye_x - 6, eye_y - 10, 12, 8), 0, math.pi, 2)
            pygame.draw.arc(surface, (30, 30, 40),
                          (right_eye_x - 6, eye_y - 10, 12, 8), 0, math.pi, 2)
        elif emotion in [Emotion.STERN, Emotion.AGGRESSIVE, Emotion.ANNOYED]:
            # Narrow eyes
            pygame.draw.line(surface, (40, 40, 50),
                           (left_eye_x - 4, eye_y), (left_eye_x + 4, eye_y), 3)
            pygame.draw.line(surface, (40, 40, 50),
                           (right_eye_x - 4, eye_y), (right_eye_x + 4, eye_y), 3)
            # Angled eyebrows
            pygame.draw.line(surface, (30, 30, 40),
                           (left_eye_x - 6, eye_y - 8), (left_eye_x + 4, eye_y - 5), 2)
            pygame.draw.line(surface, (30, 30, 40),
                           (right_eye_x - 4, eye_y - 5), (right_eye_x + 6, eye_y - 8), 2)
        elif emotion in [Emotion.SYMPATHETIC, Emotion.UNDERSTANDING, Emotion.FRIENDLY]:
            # Soft eyes
            pygame.draw.circle(surface, (40, 40, 50), (left_eye_x, eye_y), 3)
            pygame.draw.circle(surface, (40, 40, 50), (right_eye_x, eye_y), 3)
            # Soft curved eyebrows
            pygame.draw.arc(surface, (30, 30, 40),
                          (left_eye_x - 5, eye_y - 8, 10, 6), 0, math.pi, 2)
            pygame.draw.arc(surface, (30, 30, 40),
                          (right_eye_x - 5, eye_y - 8, 10, 6), 0, math.pi, 2)
        else:
            # Neutral eyes
            pygame.draw.circle(surface, (40, 40, 50), (left_eye_x, eye_y), 3)
            pygame.draw.circle(surface, (40, 40, 50), (right_eye_x, eye_y), 3)

        # Mouth varies by emotion
        mouth_y = head_y + head_radius // 2

        if emotion in [Emotion.SCARED, Emotion.WORRIED]:
            # Open/worried mouth
            pygame.draw.arc(surface, (40, 40, 50),
                          (head_x - 6, mouth_y - 3, 12, 10), math.pi, 2 * math.pi, 2)
        elif emotion in [Emotion.FRIENDLY, Emotion.RELIEVED]:
            # Smile
            pygame.draw.arc(surface, (40, 40, 50),
                          (head_x - 8, mouth_y - 6, 16, 10), 0, math.pi, 2)
        elif emotion in [Emotion.STERN, Emotion.DISAPPOINTED, Emotion.DISMISSIVE]:
            # Frown/flat line
            pygame.draw.line(surface, (40, 40, 50),
                           (head_x - 6, mouth_y + 2), (head_x + 6, mouth_y + 2), 2)
        else:
            # Neutral
            pygame.draw.line(surface, (40, 40, 50),
                           (head_x - 5, mouth_y), (head_x + 5, mouth_y), 2)

    def _draw_name_plate(self, screen: pygame.Surface, rect: pygame.Rect,
                        config: CharacterConfig, is_speaking: bool):
        """Draw the character name plate"""
        plate_height = 28
        plate_rect = pygame.Rect(
            rect.x,
            rect.bottom - plate_height - 5,
            rect.width,
            plate_height
        )

        # Plate background
        bg_color = config.primary_color if is_speaking else (40, 45, 55)
        pygame.draw.rect(screen, bg_color, plate_rect,
                        border_bottom_left_radius=8,
                        border_bottom_right_radius=8)

        # Name text
        name_text = self.fonts['name'].render(config.name, True, (240, 240, 240))
        name_rect = name_text.get_rect(center=plate_rect.center)
        screen.blit(name_text, name_rect)

    def _draw_emotion_indicator(self, screen: pygame.Surface, rect: pygame.Rect,
                               emotion: Emotion):
        """Draw emotion indicator icon"""
        icon_text = self.EMOTION_ICONS.get(emotion, "")
        if not icon_text:
            return

        # Position in top-right corner of portrait
        icon_x = rect.right - 25
        icon_y = rect.top + 10

        # Icon background bubble
        pygame.draw.circle(screen, (50, 55, 65), (icon_x, icon_y), 15)
        pygame.draw.circle(screen, (80, 85, 95), (icon_x, icon_y), 15, 2)

        # Icon text
        icon_surface = self.fonts['icon'].render(icon_text, True, (200, 200, 210))
        icon_rect = icon_surface.get_rect(center=(icon_x, icon_y))
        screen.blit(icon_surface, icon_rect)

    def _draw_speaking_indicator(self, screen: pygame.Surface, rect: pygame.Rect):
        """Draw speaking indicator (speech bubble dots)"""
        # Animated dots
        elapsed = time.time() - self.speaking_timer
        base_y = rect.bottom - 45

        for i in range(3):
            # Staggered bounce
            offset = math.sin(elapsed * 6 + i * 0.5) * 3
            dot_x = rect.right - 15 + i * 8
            dot_y = base_y + offset

            pygame.draw.circle(screen, (150, 200, 150), (int(dot_x), int(dot_y)), 3)

    def draw_dialogue_portraits(self, screen: pygame.Surface,
                               left_character: Optional[str] = None,
                               right_character: Optional[str] = None,
                               speaking: Optional[str] = None,
                               left_emotion: Optional[Emotion] = None,
                               right_emotion: Optional[Emotion] = None):
        """
        Convenience method to draw both portraits for a dialogue scene

        Args:
            screen: Surface to draw on
            left_character: Character ID for left portrait
            right_character: Character ID for right portrait
            speaking: ID of currently speaking character
            left_emotion: Emotion for left character
            right_emotion: Emotion for right character
        """
        if left_character:
            self.draw_portrait(
                screen, left_character, 'left',
                emotion=left_emotion,
                is_speaking=(speaking == left_character)
            )

        if right_character:
            self.draw_portrait(
                screen, right_character, 'right',
                emotion=right_emotion,
                is_speaking=(speaking == right_character)
            )


# Global instance for easy access
portrait_renderer = PortraitRenderer()

"""
Photo selection mini-game for the foster home narrative
High-quality visuals matching Part 5 education style
"""
import pygame
import math
from src.activities.activities import Activity
from .part1_visual_base import Part1UIColors
from .particle_effects import part1_particles
from .feedback_popups import part1_feedback

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


class PhotoUIColors:
    """Photo selection themed color palette"""
    # Primary theme - warm nostalgic tones
    PRIMARY = (180, 130, 90)           # Sepia/warm brown
    SECONDARY = (120, 100, 140)        # Soft purple (memories)
    ACCENT = (220, 180, 120)           # Golden warm

    # Card states
    CARD_BG = (252, 250, 245)          # Warm paper
    CARD_SELECTED = (230, 245, 230)    # Light green tint
    CARD_HOVER = (255, 252, 248)       # Slightly brighter

    # Status
    SELECTED_GREEN = (72, 180, 120)
    UNSELECTED = (180, 175, 170)

    # UI
    PANEL_BG = (35, 32, 38)            # Dark warm gray
    OVERLAY_BG = (20, 18, 25)          # Near black
    TEXT_LIGHT = (255, 255, 255)
    TEXT_DARK = (45, 40, 50)
    TEXT_MUTED = (140, 135, 145)

    # Buttons
    BUTTON_PRIMARY = (100, 160, 100)
    BUTTON_HOVER = (120, 180, 120)


class PhotoSelection(Activity):
    """High-quality photo selection with Part 5 visual style"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)
        self.foster_home_ref = None

        # Photo data - simpler structure, visuals handled separately
        self.photos = [
            {"id": "family", "title": "Foster Family", "desc": "Before they had their baby", "emotion": "bittersweet", "color": (180, 150, 120)},
            {"id": "birthday", "title": "15th Birthday", "desc": "A rare celebration", "emotion": "happy", "color": (255, 210, 160)},
            {"id": "friends", "title": "School Friends", "desc": "Lost touch after 8th grade", "emotion": "nostalgic", "color": (150, 180, 220)},
            {"id": "pet", "title": "Dog Max", "desc": "Your only friend for a while", "emotion": "sad", "color": (200, 175, 130)},
            {"id": "award", "title": "Honor Roll", "desc": "You worked so hard", "emotion": "proud", "color": (220, 200, 150)},
            {"id": "home", "title": "First Home", "desc": "You barely remember", "emotion": "distant", "color": (175, 175, 180)},
        ]

        for p in self.photos:
            p["selected"] = False
            p["hover_anim"] = 0.0
            p["select_anim"] = 0.0

        self.max_photos = 3
        self.hover_index = -1

        # Layout
        self.card_width = 145
        self.card_height = 180
        self.cards_per_row = 3
        self.card_gap = 25

        total_width = self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_gap
        self.grid_x = (SCREEN_WIDTH - total_width) // 2
        self.grid_y = 170

        # Button
        self.button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 90, 220, 50)
        self.button_hover = False

        # Fonts (lazy init)
        self.fonts_initialized = False
        self.title_font = None
        self.subtitle_font = None
        self.card_title_font = None
        self.card_desc_font = None
        self.button_font = None
        self.hint_font = None

        # Animation time
        self.time = 0

    def _init_fonts(self):
        """Initialize fonts"""
        if self.fonts_initialized:
            return
        try:
            self.title_font = pygame.font.SysFont('Helvetica', 38, bold=True)
            self.subtitle_font = pygame.font.SysFont('Helvetica', 20)
            self.card_title_font = pygame.font.SysFont('Helvetica', 18, bold=True)
            self.card_desc_font = pygame.font.SysFont('Helvetica', 14)
            self.button_font = pygame.font.SysFont('Helvetica', 22, bold=True)
            self.hint_font = pygame.font.SysFont('Helvetica', 14)
        except:
            self.title_font = pygame.font.Font(None, 44)
            self.subtitle_font = pygame.font.Font(None, 24)
            self.card_title_font = pygame.font.Font(None, 22)
            self.card_desc_font = pygame.font.Font(None, 18)
            self.button_font = pygame.font.Font(None, 26)
            self.hint_font = pygame.font.Font(None, 18)
        self.fonts_initialized = True

    def start(self):
        """Start the activity"""
        super().start()
        self._init_fonts()
        for p in self.photos:
            p["selected"] = False
            p["hover_anim"] = 0.0
            p["select_anim"] = 0.0
        self.hover_index = -1
        self.time = 0

    def get_card_rect(self, index):
        """Get card rectangle for index"""
        row = index // self.cards_per_row
        col = index % self.cards_per_row
        x = self.grid_x + col * (self.card_width + self.card_gap)
        y = self.grid_y + row * (self.card_height + self.card_gap)
        return pygame.Rect(x, y, self.card_width, self.card_height)

    def get_selected_count(self):
        """Count selected photos"""
        return sum(1 for p in self.photos if p["selected"])

    def draw_shadow(self, screen, rect, offset=4, alpha=50, radius=10):
        """Draw soft shadow"""
        shadow = pygame.Surface((rect.width + offset * 2, rect.height + offset * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(offset, offset, rect.width, rect.height)
        pygame.draw.rect(shadow, (0, 0, 0, alpha), shadow_rect, border_radius=radius)
        screen.blit(shadow, (rect.x - offset // 2, rect.y))

    def draw_photo_icon(self, screen, rect, photo):
        """Draw a simple but attractive photo icon"""
        color = photo["color"]
        darker = tuple(max(0, c - 30) for c in color)
        lighter = tuple(min(255, c + 30) for c in color)

        # Photo area with gradient effect
        pygame.draw.rect(screen, color, rect, border_radius=6)

        # Subtle highlight at top
        highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
        highlight = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (*lighter, 60), highlight.get_rect(), border_radius=6)
        screen.blit(highlight, highlight_rect.topleft)

        # Simple scene icon based on emotion
        cx, cy = rect.centerx, rect.centery + 5
        icon_color = darker

        emotion = photo.get("emotion", "")
        if emotion == "happy":
            # Star
            for i in range(5):
                angle = math.radians(-90 + i * 72)
                x = cx + int(15 * math.cos(angle))
                y = cy + int(15 * math.sin(angle))
                pygame.draw.line(screen, icon_color, (cx, cy), (x, y), 3)
        elif emotion == "sad":
            # Teardrop
            pygame.draw.circle(screen, icon_color, (cx, cy - 5), 10)
            pygame.draw.polygon(screen, icon_color, [(cx - 8, cy), (cx + 8, cy), (cx, cy + 15)])
        elif emotion == "nostalgic":
            # Clock/time
            pygame.draw.circle(screen, icon_color, (cx, cy), 14, 3)
            pygame.draw.line(screen, icon_color, (cx, cy), (cx, cy - 9), 2)
            pygame.draw.line(screen, icon_color, (cx, cy), (cx + 7, cy + 2), 2)
        elif emotion == "proud":
            # Medal/ribbon
            pygame.draw.circle(screen, icon_color, (cx, cy - 5), 12, 3)
            pygame.draw.polygon(screen, icon_color, [(cx - 8, cy + 5), (cx, cy + 20), (cx + 8, cy + 5)])
        elif emotion == "bittersweet":
            # Heart
            pygame.draw.circle(screen, icon_color, (cx - 7, cy - 3), 8)
            pygame.draw.circle(screen, icon_color, (cx + 7, cy - 3), 8)
            pygame.draw.polygon(screen, icon_color, [(cx - 14, cy), (cx, cy + 15), (cx + 14, cy)])
        else:
            # House
            pygame.draw.rect(screen, icon_color, (cx - 12, cy - 5, 24, 18))
            pygame.draw.polygon(screen, icon_color, [(cx - 15, cy - 5), (cx, cy - 18), (cx + 15, cy - 5)])

    def draw_card(self, screen, index, photo):
        """Draw a single photo card with animations"""
        rect = self.get_card_rect(index)
        is_hover = (index == self.hover_index)
        is_selected = photo["selected"]

        # Animate hover
        target_hover = 1.0 if is_hover else 0.0
        photo["hover_anim"] += (target_hover - photo["hover_anim"]) * 0.2

        # Animate selection
        target_select = 1.0 if is_selected else 0.0
        photo["select_anim"] += (target_select - photo["select_anim"]) * 0.15

        # Lift effect on hover
        lift = int(photo["hover_anim"] * 4)
        draw_rect = rect.copy()
        draw_rect.y -= lift

        # Shadow (stronger on hover/select)
        shadow_alpha = 40 + int(photo["hover_anim"] * 30) + int(photo["select_anim"] * 20)
        self.draw_shadow(screen, draw_rect, offset=5 + lift, alpha=shadow_alpha, radius=12)

        # Card background
        if is_selected:
            bg = PhotoUIColors.CARD_SELECTED
        elif is_hover:
            bg = PhotoUIColors.CARD_HOVER
        else:
            bg = PhotoUIColors.CARD_BG

        pygame.draw.rect(screen, bg, draw_rect, border_radius=12)

        # Selection border glow
        if photo["select_anim"] > 0.1:
            glow_alpha = int(100 * photo["select_anim"])
            glow_rect = draw_rect.inflate(6, 6)
            glow = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*PhotoUIColors.SELECTED_GREEN, glow_alpha), glow.get_rect(), border_radius=14)
            screen.blit(glow, glow_rect.topleft)
            pygame.draw.rect(screen, bg, draw_rect, border_radius=12)

        # Hover border
        border_color = PhotoUIColors.SELECTED_GREEN if is_selected else (
            PhotoUIColors.PRIMARY if is_hover else PhotoUIColors.UNSELECTED
        )
        pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=12)

        # Photo area (top portion)
        photo_rect = pygame.Rect(draw_rect.x + 10, draw_rect.y + 10, draw_rect.width - 20, 90)
        self.draw_photo_icon(screen, photo_rect, photo)

        # Title
        title_surf = self.card_title_font.render(photo["title"], True, PhotoUIColors.TEXT_DARK)
        title_x = draw_rect.x + (draw_rect.width - title_surf.get_width()) // 2
        screen.blit(title_surf, (title_x, draw_rect.y + 108))

        # Description
        desc_surf = self.card_desc_font.render(photo["desc"], True, PhotoUIColors.TEXT_MUTED)
        desc_x = draw_rect.x + (draw_rect.width - desc_surf.get_width()) // 2
        screen.blit(desc_surf, (desc_x, draw_rect.y + 130))

        # Selection indicator
        indicator_x = draw_rect.right - 22
        indicator_y = draw_rect.y + 15
        indicator_size = 16

        if is_selected:
            # Green checkmark circle
            pygame.draw.circle(screen, PhotoUIColors.SELECTED_GREEN, (indicator_x, indicator_y), indicator_size)
            # Checkmark
            check_pts = [
                (indicator_x - 6, indicator_y),
                (indicator_x - 2, indicator_y + 5),
                (indicator_x + 6, indicator_y - 5)
            ]
            pygame.draw.lines(screen, (255, 255, 255), False, check_pts, 3)
        else:
            # Empty circle
            pygame.draw.circle(screen, PhotoUIColors.UNSELECTED, (indicator_x, indicator_y), indicator_size, 2)

        # Emotion label
        emotion_labels = {
            "bittersweet": "Bittersweet",
            "happy": "Joy",
            "nostalgic": "Nostalgia",
            "sad": "Loss",
            "proud": "Pride",
            "distant": "Faded"
        }
        emotion_text = emotion_labels.get(photo.get("emotion", ""), "")
        if emotion_text:
            label_surf = self.hint_font.render(emotion_text, True, PhotoUIColors.TEXT_MUTED)
            label_x = draw_rect.x + (draw_rect.width - label_surf.get_width()) // 2
            screen.blit(label_surf, (label_x, draw_rect.y + 152))

    def draw(self, screen):
        """Draw the photo selection UI"""
        if not self.active:
            return

        # Dark overlay with subtle warmth
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((25, 22, 28, 235))
        screen.blit(overlay, (0, 0))

        # Title with subtle shadow
        title_shadow = self.title_font.render("Choose Your Memories", True, (0, 0, 0))
        title_main = self.title_font.render("Choose Your Memories", True, PhotoUIColors.ACCENT)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_main.get_width() // 2 + 2, 42))
        screen.blit(title_main, (SCREEN_WIDTH // 2 - title_main.get_width() // 2, 40))

        # Subtitle
        selected = self.get_selected_count()
        subtitle_text = f"Select up to {self.max_photos} photos to take with you"
        subtitle_surf = self.subtitle_font.render(subtitle_text, True, (180, 175, 185))
        screen.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 90))

        # Selection count indicator
        count_text = f"{selected}/{self.max_photos} selected"
        count_color = PhotoUIColors.SELECTED_GREEN if selected > 0 else PhotoUIColors.TEXT_MUTED
        count_surf = self.subtitle_font.render(count_text, True, count_color)
        screen.blit(count_surf, (SCREEN_WIDTH // 2 - count_surf.get_width() // 2, 120))

        # Draw photo cards
        for i, photo in enumerate(self.photos):
            self.draw_card(screen, i, photo)

        # Done/Skip button
        btn_hover = self.button_rect.collidepoint(pygame.mouse.get_pos())
        btn_color = PhotoUIColors.BUTTON_HOVER if btn_hover else PhotoUIColors.BUTTON_PRIMARY

        # Button shadow
        self.draw_shadow(screen, self.button_rect, offset=4, alpha=60, radius=25)

        # Button background
        pygame.draw.rect(screen, btn_color, self.button_rect, border_radius=25)

        # Button text
        btn_text = "Pack Photos" if selected > 0 else "Skip Photos"
        btn_surf = self.button_font.render(btn_text, True, PhotoUIColors.TEXT_LIGHT)
        btn_x = self.button_rect.centerx - btn_surf.get_width() // 2
        btn_y = self.button_rect.centery - btn_surf.get_height() // 2
        screen.blit(btn_surf, (btn_x, btn_y))

        # Hint
        hint_surf = self.hint_font.render("Press SPACE, ENTER, or ESC to continue", True, (100, 95, 105))
        screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, SCREEN_HEIGHT - 35))

        # Draw particles and feedback on top
        part1_particles.render(screen)
        part1_feedback.render(screen)

    def handle_mouse_motion(self, pos):
        """Track hover"""
        if not self.active:
            return
        self.hover_index = -1
        for i in range(len(self.photos)):
            if self.get_card_rect(i).collidepoint(pos):
                self.hover_index = i
                break

    def handle_mouse_click(self, pos, button):
        """Handle clicks"""
        if not self.active or button != 1:
            return

        # Check button
        if self.button_rect.collidepoint(pos):
            self.finish_selection()
            return

        # Check cards
        for i, photo in enumerate(self.photos):
            rect = self.get_card_rect(i)
            if rect.collidepoint(pos):
                if photo["selected"]:
                    photo["selected"] = False
                elif self.get_selected_count() < self.max_photos:
                    photo["selected"] = True
                    # Particle effects for selecting a memory
                    part1_particles.emit_memory_sparkle(rect.centerx, rect.centery)
                    part1_feedback.add_memory_selected(rect.centerx, rect.centery - 40)
                break

    def handle_key(self, key):
        """Handle keyboard"""
        if not self.active:
            return
        if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.finish_selection()

    def finish_selection(self):
        """Complete and exit"""
        selected_count = self.get_selected_count()

        # Achievement and celebration
        if selected_count > 0:
            part1_feedback.add_photos_selected_achievement()
            part1_particles.emit_achievement(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if self.foster_home_ref:
            self.foster_home_ref.items_packed.add('photo')
            self.foster_home_ref.update_objective_display()

            if selected_count > 0:
                titles = [p["title"] for p in self.photos if p["selected"]]
                msg = f"You carefully pack: {', '.join(titles[:2])}"
                if selected_count > 2:
                    msg += f" and {selected_count - 2} more"
                msg += ". These memories are yours to keep."
            else:
                msg = "You decide to leave the photos behind. Maybe it's better to start fresh."

            if hasattr(self.foster_home_ref, 'dialogue_box'):
                self.foster_home_ref.dialogue_box.show(None, msg)

        self.complete()

    def update(self, dt):
        """Update animations"""
        if self.active:
            self.time += dt
            # Update particles and feedback
            part1_particles.update(dt)
            part1_feedback.update(dt)

"""
Photo selection mini-game for the foster home narrative
"""
import pygame
import math
import random
from src.activities.activities import Activity

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

class PhotoSelection(Activity):
    """Mini-game where player chooses which photos to take from foster home"""

    def __init__(self, objective_manager):
        super().__init__(objective_manager)  # Call parent Activity init
        self.foster_home_ref = None

        # Photos with memories and emotional weight
        self.photos = [
            {
                "id": "family_12",
                "title": "Foster Family at 12",
                "description": "Your previous foster family, before they had their baby",
                "memory": "They were kind to you for two years",
                "emotion": "bittersweet",
                "pos": (0, 0),
                "selected": False,
                "required": True  # This one is mentioned in the narrative
            },
            {
                "id": "birthday_15",
                "title": "15th Birthday",
                "description": "A rare birthday party the home threw for you",
                "memory": "One of the few celebrations you had",
                "emotion": "happy",
                "pos": (1, 0),
                "selected": False,
                "required": False
            },
            {
                "id": "school_friends",
                "title": "School Friends",
                "description": "Friends from middle school you lost touch with",
                "memory": "They moved away after 8th grade",
                "emotion": "nostalgic",
                "pos": (2, 0),
                "selected": False,
                "required": False
            },
            {
                "id": "first_home",
                "title": "First Foster Home",
                "description": "The house you lived in when you were 8",
                "memory": "You barely remember this place",
                "emotion": "distant",
                "pos": (0, 1),
                "selected": False,
                "required": False
            },
            {
                "id": "pet_dog",
                "title": "Foster Dog Max",
                "description": "The dog from your second placement",
                "memory": "He was your only friend for a while",
                "emotion": "sad",
                "pos": (1, 1),
                "selected": False,
                "required": False
            },
            {
                "id": "award",
                "title": "Honor Roll Certificate",
                "description": "You made honor roll in 10th grade",
                "memory": "You worked so hard that semester",
                "emotion": "proud",
                "pos": (2, 1),
                "selected": False,
                "required": False
            }
        ]

        # Selection state
        self.max_photos = 3  # Can only take 3 photos
        self.selected_photos = []
        self.hover_photo = None
        self.viewing_photo = None

        # Animation
        self.animation_timer = 0
        self.fade_alpha = 0
        self.photo_shake = {}

        # UI elements
        self.continue_button_rect = None

    def start(self):
        """Start the photo selection activity"""
        super().start()  # Call parent start method
        self.selected_photos = []
        self.viewing_photo = None
        self.animation_timer = 0
        self.fade_alpha = 0

        # Reset all photos
        for photo in self.photos:
            photo["selected"] = False
            self.photo_shake[photo["id"]] = 0

    def get_photo_rect(self, photo):
        """Get the rectangle for a photo"""
        base_x = 250
        base_y = 200
        photo_width = 150
        photo_height = 120
        spacing = 20

        x = base_x + photo["pos"][0] * (photo_width + spacing)
        y = base_y + photo["pos"][1] * (photo_height + spacing)
        return pygame.Rect(x, y, photo_width, photo_height)

    def draw_photo_frame(self, screen, rect, photo, hover=False, selected=False):
        """Draw a photo frame with visual effects"""
        # Shadow
        shadow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 50))
        screen.blit(shadow_surf, (rect.x - 5, rect.y - 3))

        # Photo background (white polaroid-style)
        polaroid_rect = pygame.Rect(rect.x - 10, rect.y - 10, rect.width + 20, rect.height + 40)
        pygame.draw.rect(screen, (255, 255, 255), polaroid_rect)
        pygame.draw.rect(screen, (200, 200, 200), polaroid_rect, 1)

        # Photo image area (colored based on emotion)
        emotion_colors = {
            "bittersweet": (180, 150, 120),
            "happy": (255, 220, 150),
            "nostalgic": (150, 180, 220),
            "distant": (180, 180, 180),
            "sad": (150, 150, 180),
            "proud": (220, 200, 150)
        }

        photo_color = emotion_colors.get(photo["emotion"], (150, 150, 150))
        pygame.draw.rect(screen, photo_color, rect)

        # Draw simple scene representation
        self.draw_photo_content(screen, rect, photo)

        # Selection overlay
        if selected:
            selected_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            selected_surf.fill((100, 255, 100, 60))
            screen.blit(selected_surf, (rect.x, rect.y))
            # Checkmark
            check_points = [
                (rect.x + 10, rect.y + rect.height - 20),
                (rect.x + 25, rect.y + rect.height - 10),
                (rect.x + 45, rect.y + rect.height - 30)
            ]
            pygame.draw.lines(screen, (0, 200, 0), False, check_points, 4)

        # Hover effect
        if hover:
            pygame.draw.rect(screen, (255, 220, 100), rect, 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)

        # Title below photo (on the white border)
        font = pygame.font.Font(None, 16)
        title_text = font.render(photo["title"], True, (50, 50, 50))
        title_x = rect.x + rect.width // 2 - title_text.get_width() // 2
        title_y = rect.y + rect.height + 10
        screen.blit(title_text, (title_x, title_y))

    def draw_photo_content(self, screen, rect, photo):
        """Draw simple visual representation inside photo"""
        if photo["id"] == "family_12":
            # Draw simple figures for family
            pygame.draw.circle(screen, (100, 80, 60), (rect.x + 30, rect.y + 40), 15)  # Adult 1
            pygame.draw.circle(screen, (100, 80, 60), (rect.x + 70, rect.y + 40), 15)  # Adult 2
            pygame.draw.circle(screen, (100, 80, 60), (rect.x + 50, rect.y + 60), 12)  # You
            pygame.draw.circle(screen, (100, 80, 60), (rect.x + 90, rect.y + 50), 8)   # Baby

        elif photo["id"] == "birthday_15":
            # Draw a cake
            pygame.draw.rect(screen, (255, 200, 150), (rect.x + 40, rect.y + 50, 70, 40))
            pygame.draw.rect(screen, (255, 150, 200), (rect.x + 40, rect.y + 60, 70, 10))
            # Candles
            for i in range(3):
                x = rect.x + 55 + i * 20
                pygame.draw.rect(screen, (255, 255, 200), (x, rect.y + 40, 3, 10))
                pygame.draw.circle(screen, (255, 200, 0), (x + 1, rect.y + 38), 3)

        elif photo["id"] == "school_friends":
            # Draw 3-4 small faces
            for i in range(4):
                x = rect.x + 25 + i * 25
                y = rect.y + 50 + (i % 2) * 10
                pygame.draw.circle(screen, (100, 80, 60), (x, y), 10)

        elif photo["id"] == "first_home":
            # Simple house shape
            pygame.draw.rect(screen, (150, 100, 80), (rect.x + 35, rect.y + 45, 80, 50))
            pygame.draw.polygon(screen, (100, 50, 30), [
                (rect.x + 30, rect.y + 45),
                (rect.x + 75, rect.y + 20),
                (rect.x + 120, rect.y + 45)
            ])
            # Windows
            pygame.draw.rect(screen, (150, 180, 220), (rect.x + 45, rect.y + 55, 15, 15))
            pygame.draw.rect(screen, (150, 180, 220), (rect.x + 90, rect.y + 55, 15, 15))

        elif photo["id"] == "pet_dog":
            # Simple dog shape
            pygame.draw.ellipse(screen, (120, 80, 50), (rect.x + 40, rect.y + 50, 40, 30))  # Body
            pygame.draw.circle(screen, (120, 80, 50), (rect.x + 85, rect.y + 55), 15)  # Head
            pygame.draw.ellipse(screen, (120, 80, 50), (rect.x + 90, rect.y + 45, 8, 15))  # Ear
            # Tail
            pygame.draw.arc(screen, (120, 80, 50), (rect.x + 30, rect.y + 45, 20, 30), 0, 1.5, 5)

        elif photo["id"] == "award":
            # Certificate shape
            pygame.draw.rect(screen, (255, 255, 230), (rect.x + 25, rect.y + 20, 100, 70))
            pygame.draw.rect(screen, (200, 150, 50), (rect.x + 25, rect.y + 20, 100, 70), 2)
            # Ribbon/seal
            pygame.draw.circle(screen, (200, 50, 50), (rect.x + 75, rect.y + 70), 12)
            pygame.draw.circle(screen, (255, 215, 0), (rect.x + 75, rect.y + 70), 8)

    def draw(self, screen):
        """Draw the photo selection interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Update animation
        self.animation_timer += 0.016

        # Main container
        container_rect = pygame.Rect(100, 50, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (50, 45, 40), container_rect)
        pygame.draw.rect(screen, (150, 130, 110), container_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Choose Your Memories", True, (255, 220, 180))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

        # Subtitle
        subtitle_font = pygame.font.Font(None, 28)
        subtitle = subtitle_font.render(f"Select up to {self.max_photos} photos to take with you",
                                       True, (220, 200, 180))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 120))

        # Selection count
        count_text = f"Selected: {len(self.selected_photos)}/{self.max_photos}"
        count_color = (100, 255, 100) if len(self.selected_photos) > 0 else (200, 200, 200)
        count_surf = subtitle_font.render(count_text, True, count_color)
        screen.blit(count_surf, (SCREEN_WIDTH // 2 - count_surf.get_width() // 2, 150))

        # Draw photos in grid
        for photo in self.photos:
            rect = self.get_photo_rect(photo)

            # Add shake effect for recently selected
            if self.photo_shake.get(photo["id"], 0) > 0:
                rect.x += int(math.sin(self.photo_shake[photo["id"]] * 10) * 3)
                self.photo_shake[photo["id"]] -= 0.1

            self.draw_photo_frame(
                screen, rect, photo,
                hover=(photo == self.hover_photo),
                selected=photo["selected"]
            )

        # Draw viewing panel if a photo is being viewed
        if self.viewing_photo:
            self.draw_viewing_panel(screen)

        # Continue button
        if len(self.selected_photos) >= 1:  # At least one photo selected
            button_font = pygame.font.Font(None, 32)
            button_text = "Pack Selected Photos" if len(self.selected_photos) > 0 else "Continue Without Photos"
            button_surf = button_font.render(button_text, True, (255, 255, 255))

            self.continue_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 120, 240, 50
            )

            button_color = (100, 150, 100) if len(self.selected_photos) > 0 else (150, 100, 100)
            pygame.draw.rect(screen, button_color, self.continue_button_rect)
            pygame.draw.rect(screen, (200, 200, 200), self.continue_button_rect, 2)

            button_x = self.continue_button_rect.x + self.continue_button_rect.width // 2 - button_surf.get_width() // 2
            button_y = self.continue_button_rect.y + 12
            screen.blit(button_surf, (button_x, button_y))

    def draw_viewing_panel(self, screen):
        """Draw detailed view of selected photo"""
        if not self.viewing_photo:
            return

        # Larger overlay for focus
        panel_width = 500
        panel_height = 400
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2

        # Background
        pygame.draw.rect(screen, (30, 25, 20), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (200, 180, 150), (panel_x, panel_y, panel_width, panel_height), 3)

        # Large photo
        photo_rect = pygame.Rect(panel_x + 50, panel_y + 50, 200, 150)
        self.draw_photo_frame(screen, photo_rect, self.viewing_photo, selected=self.viewing_photo["selected"])

        # Details
        detail_font = pygame.font.Font(None, 24)
        detail_y = panel_y + 50

        # Title
        title_surf = pygame.font.Font(None, 32).render(self.viewing_photo["title"], True, (255, 220, 180))
        screen.blit(title_surf, (panel_x + 280, detail_y))

        # Description
        desc_lines = self.wrap_text(self.viewing_photo["description"], detail_font, 180)
        for i, line in enumerate(desc_lines):
            line_surf = detail_font.render(line, True, (220, 200, 180))
            screen.blit(line_surf, (panel_x + 280, detail_y + 40 + i * 25))

        # Memory
        memory_y = panel_y + 230
        memory_label = detail_font.render("Memory:", True, (200, 180, 150))
        screen.blit(memory_label, (panel_x + 50, memory_y))

        memory_lines = self.wrap_text(self.viewing_photo["memory"], detail_font, 400)
        for i, line in enumerate(memory_lines):
            line_surf = detail_font.render(line, True, (200, 200, 200))
            screen.blit(line_surf, (panel_x + 50, memory_y + 30 + i * 25))

        # Close button
        close_text = "Click anywhere to close"
        close_surf = pygame.font.Font(None, 20).render(close_text, True, (150, 150, 150))
        screen.blit(close_surf, (panel_x + panel_width // 2 - close_surf.get_width() // 2, panel_y + panel_height - 30))

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
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

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if not self.active or button != 1:
            return

        # Close viewing panel if open
        if self.viewing_photo:
            self.viewing_photo = None
            return

        # Check continue button
        if self.continue_button_rect and self.continue_button_rect.collidepoint(pos):
            if len(self.selected_photos) >= 1 or len(self.selected_photos) == 0:
                self.complete_selection()
            return

        # Check photo clicks
        for photo in self.photos:
            rect = self.get_photo_rect(photo)
            if rect.collidepoint(pos):
                # Toggle selection
                if photo["selected"]:
                    photo["selected"] = False
                    self.selected_photos.remove(photo["id"])
                else:
                    if len(self.selected_photos) < self.max_photos:
                        photo["selected"] = True
                        self.selected_photos.append(photo["id"])
                        self.photo_shake[photo["id"]] = 1.0
                    else:
                        # Show message that max is reached
                        pass

                # Open viewing panel
                self.viewing_photo = photo
                break

        # Call parent's handle_mouse_click for continue prompt handling
        super().handle_mouse_click(pos, button)

    def handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        if not self.active:
            return

        self.hover_photo = None
        for photo in self.photos:
            rect = self.get_photo_rect(photo)
            if rect.collidepoint(pos):
                self.hover_photo = photo
                break

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if key == pygame.K_ESCAPE and self.viewing_photo:
            self.viewing_photo = None
            return

        # Call parent's handle_key for continue prompt handling
        super().handle_key(key)

    def complete_selection(self):
        """Complete the photo selection"""
        # Update foster home state
        if self.foster_home_ref:
            self.foster_home_ref.items_packed.add('photo')
            self.foster_home_ref.update_objective_display()

            # Show message about photos
            if hasattr(self.foster_home_ref, 'dialogue_box'):
                if len(self.selected_photos) > 0:
                    selected_titles = [p["title"] for p in self.photos if p["id"] in self.selected_photos]
                    msg = f"You carefully pack: {', '.join(selected_titles[:2])}"
                    if len(selected_titles) > 2:
                        msg += f" and {len(selected_titles) - 2} more"
                    msg += ". These memories are all you're taking."
                else:
                    msg = "You decide not to take any photos. Maybe it's better to leave the past behind."

                self.foster_home_ref.dialogue_box.show(None, msg)

        self.complete_immediately()  # Use immediate completion instead of feedback

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt
"""
Photo selection mini-game for the foster home narrative
"""
import pygame
import math
import random
from src.activities.activities import Activity
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

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
        horizontal_spacing = 20
        vertical_spacing = 80  # Increased to accommodate labels

        x = base_x + photo["pos"][0] * (photo_width + horizontal_spacing)
        y = base_y + photo["pos"][1] * (photo_height + vertical_spacing)
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
        """Draw enhanced visual representation inside photo"""
        if photo["id"] == "family_12":
            # Background - sky and grass
            pygame.draw.rect(screen, (135, 206, 235), (rect.x, rect.y, rect.width, rect.height // 2))  # Sky
            pygame.draw.rect(screen, (100, 180, 100), (rect.x, rect.y + rect.height // 2, rect.width, rect.height // 2))  # Grass

            # Draw family figures with more detail
            figures = [
                {"x": 30, "y": 50, "size": 18, "skin": (210, 180, 140), "hair": (80, 50, 30), "shirt": (70, 130, 180)},  # Adult 1
                {"x": 70, "y": 50, "size": 18, "skin": (230, 200, 160), "hair": (200, 150, 100), "shirt": (180, 100, 120)},  # Adult 2
                {"x": 50, "y": 75, "size": 14, "skin": (220, 190, 150), "hair": (60, 40, 20), "shirt": (100, 150, 100)},  # You
                {"x": 95, "y": 65, "size": 10, "skin": (230, 200, 160), "hair": (200, 180, 140), "shirt": (255, 200, 150)}  # Baby
            ]

            for fig in figures:
                # Body (shirt)
                body_height = fig["size"] * 1.2
                pygame.draw.rect(screen, fig["shirt"],
                               (rect.x + fig["x"] - fig["size"]//2, rect.y + fig["y"] + fig["size"]//2,
                                fig["size"], body_height))
                # Head
                pygame.draw.circle(screen, fig["skin"], (rect.x + fig["x"], rect.y + fig["y"]), fig["size"]//2)
                # Hair
                pygame.draw.arc(screen, fig["hair"],
                              (rect.x + fig["x"] - fig["size"]//2, rect.y + fig["y"] - fig["size"]//2,
                               fig["size"], fig["size"]//2),
                              0, 3.14, 3)
                # Eyes
                pygame.draw.circle(screen, (50, 50, 50),
                                 (rect.x + fig["x"] - 3, rect.y + fig["y"] - 2), 2)
                pygame.draw.circle(screen, (50, 50, 50),
                                 (rect.x + fig["x"] + 3, rect.y + fig["y"] - 2), 2)
                # Smile
                pygame.draw.arc(screen, (150, 100, 100),
                              (rect.x + fig["x"] - 5, rect.y + fig["y"] - 3, 10, 8),
                              3.14, 0, 2)

        elif photo["id"] == "birthday_15":
            # Background - party atmosphere
            pygame.draw.rect(screen, (255, 245, 220), rect)  # Warm background

            # Plate
            pygame.draw.ellipse(screen, (200, 200, 200), (rect.x + 25, rect.y + 75, 100, 20))

            # Three-layer cake with vibrant colors
            layers = [
                {"y": 65, "h": 15, "color": (255, 180, 200), "frosting": (255, 220, 230)},  # Top
                {"y": 50, "h": 15, "color": (255, 220, 180), "frosting": (255, 240, 200)},  # Middle
                {"y": 35, "h": 15, "color": (200, 180, 255), "frosting": (230, 220, 255)}   # Bottom
            ]

            for layer in layers[::-1]:  # Draw bottom to top
                # Cake layer
                pygame.draw.rect(screen, layer["color"],
                               (rect.x + 40, rect.y + layer["y"], 70, layer["h"]))
                # Frosting trim
                pygame.draw.rect(screen, layer["frosting"],
                               (rect.x + 40, rect.y + layer["y"], 70, 3))
                # Side lines for depth
                pygame.draw.line(screen, (200, 150, 150),
                               (rect.x + 40, rect.y + layer["y"]),
                               (rect.x + 40, rect.y + layer["y"] + layer["h"]), 2)

            # Candles with flames
            for i in range(5):
                x = rect.x + 50 + i * 15
                # Candle
                pygame.draw.rect(screen, (255, 240, 220), (x, rect.y + 25, 4, 12))
                pygame.draw.rect(screen, (230, 180, 120), (x, rect.y + 25, 4, 12), 1)
                # Flame
                pygame.draw.circle(screen, (255, 200, 0), (x + 2, rect.y + 22), 4)
                pygame.draw.circle(screen, (255, 150, 50), (x + 2, rect.y + 20), 3)
                pygame.draw.circle(screen, (255, 255, 100), (x + 2, rect.y + 21), 2)

            # Decorative stars
            for i in range(4):
                star_x = rect.x + 15 + i * 35
                star_y = rect.y + 10 + (i % 2) * 8
                pygame.draw.circle(screen, (255, 215, 0), (star_x, star_y), 3)

        elif photo["id"] == "school_friends":
            # Background - schoolyard
            pygame.draw.rect(screen, (135, 206, 250), (rect.x, rect.y, rect.width, rect.height // 2))  # Sky
            pygame.draw.rect(screen, (120, 200, 120), (rect.x, rect.y + rect.height // 2, rect.width, rect.height // 2))  # Ground

            # Four friends with different appearances
            friends = [
                {"x": 25, "y": 55, "h": 35, "skin": (210, 180, 140), "hair": (60, 40, 20), "shirt": (220, 100, 100)},
                {"x": 55, "y": 50, "h": 40, "skin": (200, 170, 130), "hair": (120, 80, 60), "shirt": (100, 150, 220)},
                {"x": 85, "y": 52, "h": 38, "skin": (230, 200, 170), "hair": (200, 150, 100), "shirt": (150, 200, 150)},
                {"x": 115, "y": 58, "h": 33, "skin": (220, 190, 150), "hair": (40, 30, 20), "shirt": (200, 180, 100)}
            ]

            for friend in friends:
                head_size = 12
                # Body
                pygame.draw.rect(screen, friend["shirt"],
                               (rect.x + friend["x"] - 8, rect.y + friend["y"] + head_size, 16, friend["h"] - head_size))
                # Head
                pygame.draw.circle(screen, friend["skin"], (rect.x + friend["x"], rect.y + friend["y"]), head_size//2)
                # Hair
                pygame.draw.circle(screen, friend["hair"], (rect.x + friend["x"], rect.y + friend["y"] - 3), head_size//2 + 1)
                # Eyes (happy)
                pygame.draw.circle(screen, (50, 50, 50), (rect.x + friend["x"] - 3, rect.y + friend["y"]), 2)
                pygame.draw.circle(screen, (50, 50, 50), (rect.x + friend["x"] + 3, rect.y + friend["y"]), 2)
                # Smile
                pygame.draw.arc(screen, (200, 100, 100),
                              (rect.x + friend["x"] - 4, rect.y + friend["y"] - 2, 8, 6),
                              3.14, 0, 2)
                # Arms (waving)
                if friend["x"] in [25, 85]:
                    pygame.draw.line(screen, friend["skin"],
                                   (rect.x + friend["x"] + 8, rect.y + friend["y"] + 15),
                                   (rect.x + friend["x"] + 15, rect.y + friend["y"] + 8), 3)

        elif photo["id"] == "first_home":
            # Background - sky with clouds
            pygame.draw.rect(screen, (135, 206, 235), (rect.x, rect.y, rect.width, rect.height * 0.6))  # Sky
            # Clouds
            for cloud_x in [30, 100]:
                pygame.draw.circle(screen, (255, 255, 255), (rect.x + cloud_x, rect.y + 20), 8)
                pygame.draw.circle(screen, (255, 255, 255), (rect.x + cloud_x + 10, rect.y + 20), 10)

            # Grass
            pygame.draw.rect(screen, (100, 180, 100), (rect.x, rect.y + rect.height * 0.6, rect.width, rect.height * 0.4))

            # House
            house_x = rect.x + 40
            house_y = rect.y + 50
            # Walls - warm beige
            pygame.draw.rect(screen, (245, 222, 179), (house_x, house_y, 70, 50))
            pygame.draw.rect(screen, (200, 180, 140), (house_x, house_y, 70, 50), 2)

            # Roof - dark red
            roof_points = [
                (house_x - 5, house_y),
                (house_x + 35, house_y - 20),
                (house_x + 75, house_y)
            ]
            pygame.draw.polygon(screen, (139, 69, 19), roof_points)
            pygame.draw.polygon(screen, (100, 50, 20), roof_points, 2)

            # Chimney
            pygame.draw.rect(screen, (180, 100, 80), (house_x + 50, house_y - 15, 10, 20))
            # Smoke
            for i in range(3):
                pygame.draw.circle(screen, (200, 200, 200),
                                 (house_x + 55 + i * 3, house_y - 18 - i * 5), 3)

            # Door
            pygame.draw.rect(screen, (139, 90, 60), (house_x + 28, house_y + 25, 15, 25))
            pygame.draw.circle(screen, (255, 215, 0), (house_x + 40, house_y + 37), 2)  # Doorknob

            # Windows with frames
            windows = [(house_x + 10, house_y + 15), (house_x + 50, house_y + 15)]
            for wx, wy in windows:
                pygame.draw.rect(screen, (135, 206, 250), (wx, wy, 15, 15))  # Glass
                pygame.draw.rect(screen, (100, 70, 50), (wx, wy, 15, 15), 2)  # Frame
                pygame.draw.line(screen, (100, 70, 50), (wx + 7, wy), (wx + 7, wy + 15), 1)  # Cross
                pygame.draw.line(screen, (100, 70, 50), (wx, wy + 7), (wx + 15, wy + 7), 1)

        elif photo["id"] == "pet_dog":
            # Background - outdoor scene
            pygame.draw.rect(screen, (135, 206, 235), (rect.x, rect.y, rect.width, rect.height // 2))  # Sky
            pygame.draw.rect(screen, (100, 180, 100), (rect.x, rect.y + rect.height // 2, rect.width, rect.height // 2))  # Grass

            # Golden retriever dog - centered and larger
            dog_x = rect.x + 50
            dog_y = rect.y + 50

            # Body
            pygame.draw.ellipse(screen, (210, 160, 90), (dog_x, dog_y + 10, 50, 35))
            # Highlight on body
            pygame.draw.ellipse(screen, (230, 190, 120), (dog_x + 5, dog_y + 12, 30, 15))

            # Head
            pygame.draw.circle(screen, (210, 160, 90), (dog_x + 55, dog_y + 20), 16)
            # Snout
            pygame.draw.ellipse(screen, (230, 190, 120), (dog_x + 55, dog_y + 25, 12, 10))

            # Ears (floppy)
            pygame.draw.ellipse(screen, (190, 140, 80), (dog_x + 42, dog_y + 15, 10, 18))  # Left ear
            pygame.draw.ellipse(screen, (190, 140, 80), (dog_x + 60, dog_y + 15, 10, 18))  # Right ear

            # Facial features
            # Eyes (friendly)
            pygame.draw.circle(screen, (80, 50, 30), (dog_x + 50, dog_y + 18), 3)
            pygame.draw.circle(screen, (80, 50, 30), (dog_x + 60, dog_y + 18), 3)
            pygame.draw.circle(screen, (255, 255, 255), (dog_x + 51, dog_y + 17), 1)  # Gleam
            pygame.draw.circle(screen, (255, 255, 255), (dog_x + 61, dog_y + 17), 1)
            # Nose
            pygame.draw.circle(screen, (50, 30, 20), (dog_x + 55, dog_y + 27), 3)
            # Mouth (smile)
            pygame.draw.arc(screen, (50, 30, 20), (dog_x + 50, dog_y + 27, 10, 6), 3.14, 0, 2)

            # Legs
            leg_color = (200, 150, 80)
            legs = [(dog_x + 10, dog_y + 35), (dog_x + 25, dog_y + 35),
                   (dog_x + 40, dog_y + 35), (dog_x + 55, dog_y + 35)]
            for lx, ly in legs:
                pygame.draw.rect(screen, leg_color, (lx, ly, 6, 15))
                pygame.draw.ellipse(screen, (180, 130, 70), (lx - 1, ly + 13, 8, 5))  # Paws

            # Tail (wagging - curved)
            tail_points = [
                (dog_x + 5, dog_y + 25),
                (dog_x - 5, dog_y + 15),
                (dog_x - 8, dog_y + 5)
            ]
            pygame.draw.lines(screen, (200, 150, 80), False, tail_points, 6)

            # Ball toy
            pygame.draw.circle(screen, (255, 100, 100), (rect.x + 20, rect.y + 90), 8)
            pygame.draw.circle(screen, (255, 150, 150), (rect.x + 20, rect.y + 90), 8, 2)

        elif photo["id"] == "award":
            # Background - wall
            pygame.draw.rect(screen, (240, 230, 210), rect)

            # Certificate with ornate border
            cert_x = rect.x + 20
            cert_y = rect.y + 15
            cert_w = 110
            cert_h = 85

            # Certificate background (aged paper)
            pygame.draw.rect(screen, (255, 250, 235), (cert_x, cert_y, cert_w, cert_h))

            # Ornate border - multiple layers
            pygame.draw.rect(screen, (200, 160, 100), (cert_x, cert_y, cert_w, cert_h), 3)
            pygame.draw.rect(screen, (220, 180, 120), (cert_x + 3, cert_y + 3, cert_w - 6, cert_h - 6), 2)
            pygame.draw.rect(screen, (180, 140, 80), (cert_x + 6, cert_y + 6, cert_w - 12, cert_h - 12), 1)

            # Decorative corners
            corners = [
                (cert_x + 10, cert_y + 10), (cert_x + cert_w - 10, cert_y + 10),
                (cert_x + 10, cert_y + cert_h - 10), (cert_x + cert_w - 10, cert_y + cert_h - 10)
            ]
            for cx, cy in corners:
                pygame.draw.circle(screen, (200, 160, 100), (cx, cy), 4)
                pygame.draw.circle(screen, (255, 215, 0), (cx, cy), 2)

            # Text lines (representing writing)
            for i in range(4):
                line_y = cert_y + 25 + i * 10
                line_w = 70 if i == 0 else (60 if i < 3 else 40)
                line_x = cert_x + (cert_w - line_w) // 2
                pygame.draw.line(screen, (100, 100, 100),
                               (line_x, line_y), (line_x + line_w, line_y), 1)

            # Star badge at top
            star_x = cert_x + cert_w // 2
            star_y = cert_y + 15
            pygame.draw.circle(screen, (255, 215, 0), (star_x, star_y), 8)
            # Star points (simplified)
            for angle in range(0, 360, 72):
                import math
                rad = math.radians(angle)
                px = star_x + int(6 * math.cos(rad))
                py = star_y + int(6 * math.sin(rad))
                pygame.draw.line(screen, (255, 200, 0), (star_x, star_y), (px, py), 2)

            # Ribbon/seal at bottom
            seal_x = cert_x + cert_w // 2
            seal_y = cert_y + cert_h - 15
            # Outer circle (red ribbon)
            pygame.draw.circle(screen, (200, 50, 50), (seal_x, seal_y), 12)
            # Inner circle (gold seal)
            pygame.draw.circle(screen, (255, 215, 0), (seal_x, seal_y), 9)
            # Ribbon tails
            pygame.draw.polygon(screen, (200, 50, 50), [
                (seal_x - 3, seal_y + 8),
                (seal_x - 8, seal_y + 20),
                (seal_x, seal_y + 12)
            ])
            pygame.draw.polygon(screen, (200, 50, 50), [
                (seal_x + 3, seal_y + 8),
                (seal_x + 8, seal_y + 20),
                (seal_x, seal_y + 12)
            ])

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
            print(f"[PHOTO_SELECTION] Added 'photo' to items_packed. Now: {self.foster_home_ref.items_packed}")
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
        else:
            print("[PHOTO_SELECTION] WARNING: No foster_home_ref set!")

        self.complete()

    def update(self, dt):
        """Update animations"""
        if not self.active:
            return

        self.animation_timer += dt
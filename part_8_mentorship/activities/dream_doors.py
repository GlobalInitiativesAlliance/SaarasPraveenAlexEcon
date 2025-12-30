"""
Dream Doors Sequence
Shows multiple doors labeled "Work," "School," "Homelessness," "Unknown"
Forced choice: walk through a door without knowing consequences
"""
import pygame


class DreamDoors:
    """Dream sequence with door choices"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Doors
        self.doors = [
            {"label": "Work", "color": (80, 120, 80), "hover": False, "description": "Steady income, but limited growth"},
            {"label": "School", "color": (80, 100, 140), "hover": False, "description": "Investment in future, debt today"},
            {"label": "Homelessness", "color": (100, 60, 60), "hover": False, "description": "The path of no choices left"},
            {"label": "Unknown", "color": (80, 80, 100), "hover": False, "description": "???"},
        ]

        self.door_rects = []
        self.door_width = 120
        self.door_height = 200

        # Selection
        self.selected_door = None
        self.show_result = False
        self.result_timer = 0

        # Animation
        self.fade_alpha = 0
        self.fading_in = True

    def start(self):
        """Start the dream sequence"""
        self.active = True
        self.completed = False
        self.selected_door = None
        self.show_result = False
        self.result_timer = 0
        self.fade_alpha = 0
        self.fading_in = True

        # Position doors
        start_x = 100
        y = 200
        spacing = 160
        self.door_rects = []

        for i, door in enumerate(self.doors):
            rect = pygame.Rect(
                start_x + i * spacing,
                y,
                self.door_width,
                self.door_height
            )
            self.door_rects.append(rect)
            door["hover"] = False

    def stop(self):
        """Stop the dream sequence"""
        self.active = False

    def update(self, dt):
        """Update dream state"""
        if not self.active:
            return

        # Fade in effect
        if self.fading_in:
            self.fade_alpha = min(255, self.fade_alpha + dt * 200)
            if self.fade_alpha >= 255:
                self.fading_in = False

        # Result timer
        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

    def handle_event(self, event):
        """Handle mouse events"""
        if not self.active or self.show_result or self.fading_in:
            return

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for i, rect in enumerate(self.door_rects):
                self.doors[i]["hover"] = rect.collidepoint(pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, rect in enumerate(self.door_rects):
                if rect.collidepoint(pos):
                    self.selected_door = i
                    self.show_result = True
                    break

        elif event.type == pygame.KEYDOWN:
            # Number keys to select doors
            if event.key == pygame.K_1:
                self.selected_door = 0
                self.show_result = True
            elif event.key == pygame.K_2:
                self.selected_door = 1
                self.show_result = True
            elif event.key == pygame.K_3:
                self.selected_door = 2
                self.show_result = True
            elif event.key == pygame.K_4:
                self.selected_door = 3
                self.show_result = True

    def render(self, screen):
        """Render the dream sequence"""
        # Dream background - dark with slight purple tint
        screen.fill((20, 15, 30))

        # Foggy overlay effect
        fog = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        fog.fill((40, 35, 50))
        fog.set_alpha(100)
        screen.blit(fog, (0, 0))

        # Title text with dream-like effect
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("You dream of doors...", True, (180, 170, 200))
        title.set_alpha(int(self.fade_alpha))
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Subtitle
        sub_font = pygame.font.Font(None, 28)
        sub = sub_font.render("Each leads somewhere, but you cannot see beyond.", True, (140, 130, 160))
        sub.set_alpha(int(self.fade_alpha))
        screen.blit(sub, (self.SCREEN_WIDTH // 2 - sub.get_width() // 2, 100))

        # Draw doors
        door_font = pygame.font.Font(None, 26)
        for i, (door, rect) in enumerate(zip(self.doors, self.door_rects)):
            # Door shadow
            shadow_rect = rect.copy()
            shadow_rect.x += 8
            shadow_rect.y += 8
            pygame.draw.rect(screen, (10, 10, 15), shadow_rect)

            # Door body
            color = door["color"]
            if door["hover"]:
                color = tuple(min(255, c + 40) for c in color)

            pygame.draw.rect(screen, color, rect)

            # Door frame
            frame_color = (150, 140, 130) if door["hover"] else (100, 90, 80)
            pygame.draw.rect(screen, frame_color, rect, 4)

            # Door handle
            handle_x = rect.x + rect.width - 25
            handle_y = rect.y + rect.height // 2
            pygame.draw.circle(screen, (180, 160, 100), (handle_x, handle_y), 8)

            # Door label
            label = door_font.render(door["label"], True, (220, 210, 200))
            label_x = rect.x + rect.width // 2 - label.get_width() // 2
            label_y = rect.y + 30
            screen.blit(label, (label_x, label_y))

            # Number indicator
            num = door_font.render(f"[{i + 1}]", True, (150, 140, 160))
            screen.blit(num, (rect.x + rect.width // 2 - num.get_width() // 2, rect.y + rect.height + 10))

            # Show description on hover
            if door["hover"] and not self.show_result:
                desc_font = pygame.font.Font(None, 22)
                desc = desc_font.render(door["description"], True, (180, 170, 190))
                screen.blit(desc, (rect.x + rect.width // 2 - desc.get_width() // 2, rect.y + rect.height + 35))

        # Instructions
        if not self.show_result and not self.fading_in:
            inst_font = pygame.font.Font(None, 24)
            inst = inst_font.render("Click a door or press 1-4 to choose your path", True, (130, 120, 150))
            screen.blit(inst, (self.SCREEN_WIDTH // 2 - inst.get_width() // 2, 480))

            warning = inst_font.render("You cannot know what lies beyond until you step through.", True, (150, 100, 100))
            screen.blit(warning, (self.SCREEN_WIDTH // 2 - warning.get_width() // 2, 510))

        # Show result
        if self.show_result and self.selected_door is not None:
            door = self.doors[self.selected_door]

            # Fade overlay
            fade = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            fade.fill((10, 10, 20))
            fade.set_alpha(min(200, int(self.result_timer * 100)))
            screen.blit(fade, (0, 0))

            # Result text
            result_font = pygame.font.Font(None, 40)
            text1 = result_font.render(f"You stepped through: {door['label']}", True, (200, 190, 210))
            screen.blit(text1, (self.SCREEN_WIDTH // 2 - text1.get_width() // 2, 250))

            sub_font = pygame.font.Font(None, 28)
            text2 = sub_font.render("You made a decision...", True, (160, 150, 180))
            screen.blit(text2, (self.SCREEN_WIDTH // 2 - text2.get_width() // 2, 310))

            text3 = sub_font.render("But without guidance, your long-term path remains uncertain.", True, (180, 140, 140))
            screen.blit(text3, (self.SCREEN_WIDTH // 2 - text3.get_width() // 2, 350))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

import pygame
import sys
import os
import math

class ScenariosMenu:
    def __init__(self, screen_width=1536, screen_height=1024):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load the scenarios background image
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scenarios_bg.png")

        # Try to load scenarios background, fallback to main background if not found
        try:
            self.background = pygame.image.load(image_path).convert()
        except (pygame.error, FileNotFoundError):
            print("scenarios_bg.png not found, using loadedimage.png as fallback")
            try:
                fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "loadedimage.png")
                self.background = pygame.image.load(fallback_path).convert()
            except (pygame.error, FileNotFoundError):
                print("loadedimage.png not found, creating solid color background")
                # Create a simple colored background as final fallback
                self.background = pygame.Surface((screen_width, screen_height))
                self.background.fill((30, 50, 80))  # Dark blue background

        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))

        # Define clickable regions for each scenario panel
        # Based on 2x3 grid layout in the image
        panel_width = 360
        panel_height = 265

        # Left column x, right column x
        left_x = 225
        right_x = 535

        # Row positions
        top_y = 245
        middle_y = 545
        bottom_y = 665

        self.panels = {
            1: pygame.Rect(left_x, top_y, panel_width, panel_height),      # Housing Stability
            2: pygame.Rect(right_x, top_y, panel_width, panel_height),     # Healthcare Access
            3: pygame.Rect(left_x, middle_y, panel_width, panel_height),   # Legal System
            4: pygame.Rect(right_x, middle_y, panel_width, panel_height),  # Healthcare Crisis
            5: pygame.Rect(left_x, bottom_y, panel_width, panel_height),   # Education Journey
            6: pygame.Rect(right_x, bottom_y, panel_width, panel_height)   # Systemic Barriers
        }

        # Panel metadata
        self.panel_info = {
            1: {"title": "Housing Stability", "available": True, "part": 1},
            2: {"title": "Healthcare Access", "available": False, "part": 2},  # Set to True if Part 2 is ready
            3: {"title": "Legal System", "available": False, "part": 3},
            4: {"title": "Healthcare Crisis", "available": False, "part": 4},
            5: {"title": "Education Journey", "available": False, "part": 5},
            6: {"title": "Systemic Barriers", "available": False, "part": 6}
        }

        # UI state
        self.hover_panel = None
        self.selected_panel = None
        self.selected_action = None

        # Animation properties
        self.panel_scales = {i: 1.0 for i in range(1, 7)}
        self.target_scales = {i: 1.0 for i in range(1, 7)}
        self.animation_time = 0

        # Overlay for hover effects
        self.hover_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        self.hover_surface.fill((255, 255, 255, 30))  # Semi-transparent white

        # Click feedback surface
        self.click_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        self.click_surface.fill((255, 255, 255, 60))  # Brighter for click feedback

        self.click_feedback = {i: 0.0 for i in range(1, 7)}  # Timer for click animation

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hover_panel = None

            for panel_num, rect in self.panels.items():
                if rect.collidepoint(mouse_pos):
                    self.hover_panel = panel_num
                    self.target_scales[panel_num] = 1.05  # Slight scale up on hover
                else:
                    self.target_scales[panel_num] = 1.0

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for panel_num, rect in self.panels.items():
                if rect.collidepoint(mouse_pos):
                    self.selected_panel = panel_num
                    self.click_feedback[panel_num] = 0.3  # Start click animation

                    panel_data = self.panel_info[panel_num]
                    if panel_data["available"]:
                        if panel_num == 1:  # Housing Stability
                            self.selected_action = "start_part1"
                            return "start_part1"
                        elif panel_num == 2:  # Healthcare Access (if available)
                            self.selected_action = "start_part2"
                            return "start_part2"
                    else:
                        # Show coming soon message
                        print(f"{panel_data['title']} - Coming Soon!")
                        return "coming_soon"

        elif event.type == pygame.KEYDOWN:
            # Number keys 1-6 for quick selection
            if pygame.K_1 <= event.key <= pygame.K_6:
                panel_num = event.key - pygame.K_0  # Convert to number
                panel_data = self.panel_info[panel_num]

                if panel_data["available"]:
                    if panel_num == 1:
                        return "start_part1"
                    elif panel_num == 2:
                        return "start_part2"
                else:
                    print(f"{panel_data['title']} - Coming Soon!")
                    return "coming_soon"

            elif event.key == pygame.K_ESCAPE:
                return "back_to_menu"

        return None

    def update_animations(self, dt):
        """Update animation values"""
        self.animation_time += dt

        # Smooth scale transitions
        for panel_num in range(1, 7):
            current = self.panel_scales[panel_num]
            target = self.target_scales[panel_num]
            self.panel_scales[panel_num] = current + (target - current) * 0.15

        # Update click feedback timers
        for panel_num in range(1, 7):
            if self.click_feedback[panel_num] > 0:
                self.click_feedback[panel_num] -= dt * 3  # Fade out over ~0.1 seconds
                self.click_feedback[panel_num] = max(0, self.click_feedback[panel_num])

    def draw(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Update animations
        self.update_animations(0.016)  # Assuming ~60 FPS

        # Draw hover effects and click feedback
        for panel_num, rect in self.panels.items():
            # Hover effect
            if self.hover_panel == panel_num:
                # Create a slightly scaled version for hover effect
                scale = self.panel_scales[panel_num]
                if scale != 1.0:
                    # For now, just draw the hover overlay
                    screen.blit(self.hover_surface, rect.topleft)

            # Click feedback
            if self.click_feedback[panel_num] > 0:
                alpha = int(255 * self.click_feedback[panel_num])
                click_surf = self.click_surface.copy()
                click_surf.set_alpha(alpha)
                screen.blit(click_surf, rect.topleft)

        # Draw status text for unavailable scenarios when hovered
        if self.hover_panel and not self.panel_info[self.hover_panel]["available"]:
            font = pygame.font.Font(None, 32)
            text = f"{self.panel_info[self.hover_panel]['title']} - Coming Soon!"
            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, 50))

            # Background for text
            bg_rect = text_rect.copy()
            bg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)

            screen.blit(text_surf, text_rect)

    def reset(self):
        """Reset menu state"""
        self.hover_panel = None
        self.selected_panel = None
        self.selected_action = None
        self.panel_scales = {i: 1.0 for i in range(1, 7)}
        self.target_scales = {i: 1.0 for i in range(1, 7)}
        self.click_feedback = {i: 0.0 for i in range(1, 7)}
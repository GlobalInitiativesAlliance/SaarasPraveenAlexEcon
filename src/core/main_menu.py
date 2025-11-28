import pygame
import sys
import os
import math
import random

class Airplane:
    """Animated airplane that flies across the screen"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        """Reset airplane to starting position"""
        # Random starting position (left or right side)
        self.direction = random.choice([-1, 1])
        if self.direction > 0:
            self.x = -100
        else:
            self.x = self.screen_width + 100

        # Random height (upper 60% of screen for sky)
        self.y = random.randint(50, int(self.screen_height * 0.4))

        # Random speed
        self.speed = random.uniform(1.5, 3.5)

        # Random size
        self.size = random.randint(30, 60)

        # Create airplane shape
        self.create_airplane()

    def create_airplane(self):
        """Create a simple airplane sprite with transparency"""
        # Create surface for airplane
        self.surface = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)

        # Use semi-transparent colors so airplane appears in background
        # Fuselage
        pygame.draw.ellipse(self.surface, (200, 200, 200, 80),
                          (self.size * 0.3, self.size * 0.3, self.size * 1.2, self.size * 0.4))

        # Wings
        pygame.draw.polygon(self.surface, (180, 180, 180, 80), [
            (self.size * 0.5, self.size * 0.5),
            (self.size * 1.3, self.size * 0.5),
            (self.size * 1.1, self.size * 0.2),
            (self.size * 0.7, self.size * 0.2)
        ])

        # Tail
        pygame.draw.polygon(self.surface, (180, 180, 180, 80), [
            (self.size * 0.3, self.size * 0.5),
            (self.size * 0.5, self.size * 0.5),
            (self.size * 0.4, self.size * 0.1)
        ])

        # Windows
        for i in range(3):
            window_x = self.size * (0.6 + i * 0.15)
            pygame.draw.circle(self.surface, (100, 150, 200, 90),
                             (int(window_x), int(self.size * 0.45)), 3)

        # Flip if going left
        if self.direction < 0:
            self.surface = pygame.transform.flip(self.surface, True, False)

    def update(self):
        """Update airplane position"""
        self.x += self.speed * self.direction

        # Add slight bobbing motion
        self.y_offset = math.sin(self.x * 0.02) * 3

        # Reset if off screen
        if self.direction > 0 and self.x > self.screen_width + 100:
            self.reset()
        elif self.direction < 0 and self.x < -100:
            self.reset()

    def draw(self, screen):
        """Draw the airplane"""
        screen.blit(self.surface, (int(self.x), int(self.y + self.y_offset)))


class Cloud:
    """Animated cloud that drifts across the sky"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        self.x = random.randint(-200, self.screen_width)
        self.y = random.randint(50, int(self.screen_height * 0.3))
        self.speed = random.uniform(0.2, 0.8)
        self.size = random.randint(40, 100)
        self.alpha = random.randint(20, 50)  # More transparent to stay in background

    def update(self):
        self.x += self.speed
        if self.x > self.screen_width + 200:
            self.x = -200
            self.y = random.randint(50, int(self.screen_height * 0.3))

    def draw(self, screen):
        cloud_surface = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
        # Draw multiple circles to form cloud
        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha),
                         (int(self.size * 0.5), int(self.size * 0.5)), int(self.size * 0.3))
        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha),
                         (int(self.size * 0.8), int(self.size * 0.5)), int(self.size * 0.35))
        pygame.draw.circle(cloud_surface, (255, 255, 255, self.alpha),
                         (int(self.size * 1.1), int(self.size * 0.5)), int(self.size * 0.3))
        screen.blit(cloud_surface, (int(self.x), int(self.y)))


class MainMenu:
    def __init__(self, screen_width=1536, screen_height=1024):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clock = pygame.time.Clock()

        # Load landscape background - use path relative to project root
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "loadedimage.png")
        self.background = pygame.image.load(image_path).convert()
        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))

        # Button hitboxes tuned for 1536x1024 layout
        self.buttons = {
            "start": pygame.Rect(310, 250, 500, 95),
            "scenarios": pygame.Rect(310, 375, 500, 80),
            "howto": pygame.Rect(310, 475, 500, 80),
            "credits": pygame.Rect(310, 575, 500, 80),
            "quit": pygame.Rect(560, 850, 420, 80),
        }

        self.hover_button = None
        self.selected_action = None

        # Animation properties
        self.button_scales = {name: 1.0 for name in self.buttons.keys()}
        self.target_scales = {name: 1.0 for name in self.buttons.keys()}
        self.button_pulses = {name: 0.0 for name in self.buttons.keys()}
        self.animation_time = 0

        # Background animations
        self.airplanes = [Airplane(screen_width, screen_height) for _ in range(3)]
        self.clouds = [Cloud(screen_width, screen_height) for _ in range(5)]

    def get_animated_button_rect(self, name):
        """Get the actual animated position of a button for accurate collision detection"""
        rect = self.buttons[name]
        is_hovered = self.hover_button == name

        # Calculate animation values (same as in draw method)
        scale = self.button_scales[name] + self.button_pulses[name]

        # Calculate scaled dimensions
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)

        # Center the scaled button on original position
        scaled_x = rect.centerx - scaled_width // 2
        scaled_y = rect.centery - scaled_height // 2

        # Add floating effect when hovered
        float_offset = 0
        if is_hovered:
            float_offset = math.sin(self.animation_time * 3) * 5

        # Return the actual animated rectangle
        return pygame.Rect(scaled_x, scaled_y + float_offset, scaled_width, scaled_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hover_button = None
            for name, rect in self.buttons.items():
                # Use animated rect for collision detection
                animated_rect = self.get_animated_button_rect(name)
                if animated_rect.collidepoint(mouse_pos):
                    self.hover_button = name
                    self.target_scales[name] = 1.15  # Scale up on hover
                else:
                    self.target_scales[name] = 1.0  # Scale down when not hovering

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for name, rect in self.buttons.items():
                # Use animated rect for collision detection
                animated_rect = self.get_animated_button_rect(name)
                if animated_rect.collidepoint(mouse_pos):
                    print(f"Button clicked: {name}")
                    self.selected_action = name
                    if name == "start":
                        return "start_game"
                    elif name == "quit":
                        pygame.quit()
                        sys.exit()
                    else:
                        return name

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "start_game"
        return None

    def update_animations(self, dt):
        """Update animation values"""
        self.animation_time += dt

        # Smooth scale transitions using lerp
        for name in self.buttons.keys():
            current = self.button_scales[name]
            target = self.target_scales[name]
            # Smooth interpolation
            self.button_scales[name] = current + (target - current) * 0.15

        # Update pulse values for hover effect
        for name in self.buttons.keys():
            if self.hover_button == name:
                self.button_pulses[name] = math.sin(self.animation_time * 5) * 0.05
            else:
                self.button_pulses[name] *= 0.9  # Fade out pulse

        # Update background animations
        for airplane in self.airplanes:
            airplane.update()

        for cloud in self.clouds:
            cloud.update()

    def draw(self, screen):
        # === LAYER 1: Background ===
        screen.blit(self.background, (0, 0))

        # Update animations (assuming ~60 FPS, dt ~ 0.016)
        self.update_animations(0.016)

        # === LAYER 2: Sky Elements (behind everything) ===
        # Draw clouds first (furthest back in sky)
        for cloud in self.clouds:
            cloud.draw(screen)

        # Draw airplanes (in front of clouds but behind UI)
        for airplane in self.airplanes:
            airplane.draw(screen)

        # === LAYER 3: UI Elements (drawn last, appears on top) ===
        # Draw animated buttons
        for name, rect in self.buttons.items():
            is_hovered = self.hover_button == name

            # Calculate animation values
            scale = self.button_scales[name] + self.button_pulses[name]

            # Calculate scaled dimensions
            scaled_width = int(rect.width * scale)
            scaled_height = int(rect.height * scale)

            # Center the scaled button on original position
            scaled_x = rect.centerx - scaled_width // 2
            scaled_y = rect.centery - scaled_height // 2

            # Add floating effect when hovered
            float_offset = 0
            if is_hovered:
                float_offset = math.sin(self.animation_time * 3) * 5

            # Draw glow effect for hovered buttons (multiple layers)
            if is_hovered:
                for i in range(3):
                    glow_scale = scale + 0.05 * (i + 1)
                    glow_width = int(rect.width * glow_scale)
                    glow_height = int(rect.height * glow_scale)
                    glow_x = rect.centerx - glow_width // 2
                    glow_y = rect.centery - glow_height // 2 + float_offset

                    glow_alpha = int(30 - i * 8)
                    glow = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                    glow.fill((100, 255, 100, glow_alpha))
                    screen.blit(glow, (glow_x, glow_y))

            # Draw main button overlay
            color = (0, 255, 0) if is_hovered else (255, 255, 255)
            alpha = int(120 + math.sin(self.animation_time * 4) * 20) if is_hovered else 50

            overlay = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            overlay.fill((*color, alpha))
            screen.blit(overlay, (scaled_x, scaled_y + float_offset))

            # Draw border highlight for hovered buttons
            if is_hovered:
                border_rect = pygame.Rect(scaled_x, scaled_y + float_offset, scaled_width, scaled_height)
                pygame.draw.rect(screen, (150, 255, 150), border_rect, 3)

    def reset(self):
        self.hover_button = None
        self.selected_action = None
        self.button_scales = {name: 1.0 for name in self.buttons.keys()}
        self.target_scales = {name: 1.0 for name in self.buttons.keys()}
        self.button_pulses = {name: 0.0 for name in self.buttons.keys()}
        self.animation_time = 0
        # Reset background animations
        for airplane in self.airplanes:
            airplane.reset()
        for cloud in self.clouds:
            cloud.reset()


# --- Example run ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1536, 1024))
    pygame.display.set_caption("EquityPlay Main Menu (Landscape)")
    menu = MainMenu()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            action = menu.handle_event(event)
            if action == "start_game":
                print("Starting game... (Transition here)")
                running = False

        menu.draw(screen)
        pygame.display.flip()

    pygame.quit()

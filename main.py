import pygame
import sys
import random

pygame.init()

# Screen size
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling World Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

print("hello")
# Fonts
FONT = pygame.font.SysFont(None, 48)

# Game states
MENU = "menu"
SETTINGS = "settings"
GAME = "game"
state = MENU

# Define a Button class
class Button:
    def __init__(self, rect, text, color, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = FONT.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create buttons
play_button = Button((WIDTH//2 - 100, 200, 200, 60), "Play", BLUE)
settings_button = Button((WIDTH//2 - 100, 300, 200, 60), "Settings", GREEN)

# World parameters
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000

# Player
player_size = 50
player_speed = 5
player_rect = pygame.Rect(WORLD_WIDTH//2, WORLD_HEIGHT//2, player_size, player_size)

# Camera offset
camera_x = 0
camera_y = 0

# Obstacles
obstacles = []
for _ in range(30):
    x = random.randint(0, WORLD_WIDTH - 100)
    y = random.randint(0, WORLD_HEIGHT - 100)
    w = random.randint(50, 200)
    h = random.randint(50, 200)
    obstacles.append(pygame.Rect(x, y, w, h))

clock = pygame.time.Clock()

running = True
while running:
    SCREEN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.is_clicked(event.pos):
                    state = GAME
                elif settings_button.is_clicked(event.pos):
                    state = SETTINGS

        elif state == SETTINGS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = MENU

        elif state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = MENU

    if state == MENU:
        play_button.draw(SCREEN)
        settings_button.draw(SCREEN)

    elif state == SETTINGS:
        text = FONT.render("Settings Screen - Press ESC", True, WHITE)
        SCREEN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))

    elif state == GAME:
        keys = pygame.key.get_pressed()

        # Save original position
        original_pos = player_rect.topleft

        # Move player
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
        if keys[pygame.K_UP]:
            player_rect.y -= player_speed
        if keys[pygame.K_DOWN]:
            player_rect.y += player_speed

        # Keep player inside world bounds
        player_rect.x = max(0, min(WORLD_WIDTH - player_size, player_rect.x))
        player_rect.y = max(0, min(WORLD_HEIGHT - player_size, player_rect.y))

        # Check collisions
        for obs in obstacles:
            if player_rect.colliderect(obs):
                # If collided, undo move
                player_rect.topleft = original_pos
                break

        # Center camera on player
        camera_x = player_rect.centerx - WIDTH // 2
        camera_y = player_rect.centery - HEIGHT // 2

        # Clamp camera to world bounds
        camera_x = max(0, min(camera_x, WORLD_WIDTH - WIDTH))
        camera_y = max(0, min(camera_y, WORLD_HEIGHT - HEIGHT))

        # Draw world background
        SCREEN.fill((30, 30, 60))  # dark blue background

        # Draw obstacles
        for obs in obstacles:
            obs_screen = obs.move(-camera_x, -camera_y)
            pygame.draw.rect(SCREEN, WHITE, obs_screen)

        # Draw player
        player_screen_rect = player_rect.move(-camera_x, -camera_y)
        pygame.draw.rect(SCREEN, RED, player_screen_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

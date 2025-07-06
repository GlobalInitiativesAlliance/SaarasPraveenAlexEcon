import pygame
import sys
import random
from college_selector import CollegeSelector
import os

pygame.init()
pygame.mixer.init()

# Screen size
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling World Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)

print("hello")

# Audio settings
MUSIC_VOLUME = 0.3
SOUND_VOLUME = 0.5

# Load audio files (with error handling)
def load_audio():
    """Load audio files with error handling"""
    audio_files = {
        'menu_music': None,
        'game_music': None,
        'button_click': None,
        'collision_sound': None,
        'success_sound': None
    }
    
    # Try to load music files (common formats)
    music_files = [
        'menu_music.mp3', 'menu_music.ogg', 'menu_music.wav',
        'game_music.mp3', 'game_music.ogg', 'game_music.wav'
    ]
    
    sound_files = [
        'button_click.wav', 'button_click.ogg', 'button_click.mp3',
        'collision.wav', 'collision.ogg', 'collision.mp3',
        'success.wav', 'success.ogg', 'success.mp3'
    ]
    
    # Check for existing audio files
    for file in music_files:
        if os.path.exists(file):
            if 'menu' in file:
                audio_files['menu_music'] = file
            elif 'game' in file:
                audio_files['game_music'] = file
    
    # Load sound effects
    for file in sound_files:
        if os.path.exists(file):
            try:
                if 'button' in file or 'click' in file:
                    audio_files['button_click'] = pygame.mixer.Sound(file)
                elif 'collision' in file:
                    audio_files['collision_sound'] = pygame.mixer.Sound(file)
                elif 'success' in file:
                    audio_files['success_sound'] = pygame.mixer.Sound(file)
            except pygame.error:
                print(f"Could not load sound file: {file}")
    
    return audio_files

# Initialize audio
audio_files = load_audio()
current_music = None
music_enabled = True
sound_enabled = True

def play_music(music_file):
    """Play background music"""
    global current_music
    if music_enabled and music_file and music_file != current_music:
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            current_music = music_file
        except pygame.error:
            print(f"Could not load music file: {music_file}")

def play_sound(sound):
    """Play a sound effect"""
    if sound_enabled and sound:
        try:
            sound.set_volume(SOUND_VOLUME)
            sound.play()
        except:
            pass

def stop_music():
    """Stop background music"""
    pygame.mixer.music.stop()
    global current_music
    current_music = None

def toggle_music():
    """Toggle music on/off"""
    global music_enabled
    music_enabled = not music_enabled
    if not music_enabled:
        stop_music()
    else:
        # Resume appropriate music based on current state
        if state == MENU and audio_files['menu_music']:
            play_music(audio_files['menu_music'])
        elif state == GAME and audio_files['game_music']:
            play_music(audio_files['game_music'])

def toggle_sound():
    """Toggle sound effects on/off"""
    global sound_enabled
    sound_enabled = not sound_enabled

# Fonts
FONT = pygame.font.SysFont(None, 48)
HUD_FONT = pygame.font.SysFont(None, 20)
HUD_FONT_SMALL = pygame.font.SysFont(None, 16)

# Game states
MENU = "menu"
SETTINGS = "settings"
GAME = "game"
state = MENU

# Game Stats - Initialize all stats
class GameStats:
    def __init__(self):
        self.credit_score = 0
        self.debit_balance = 0.0
        self.credit_balance = 0.0
        self.savings_balance = 0.0
        self.physical_health = 0
        self.mental_health = 0
        self.total_wealth = 0.0
        self.game_score = 0
    
    def update_total_wealth(self):
        self.total_wealth = self.debit_balance + self.savings_balance - self.credit_balance

# Initialize game stats
game_stats = GameStats()

# HUD dimensions
HUD_HEIGHT = 120
HUD_Y = HEIGHT - HUD_HEIGHT

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

def draw_hud():
    """Draw the HUD with all game stats"""
    # Draw HUD background
    hud_rect = pygame.Rect(0, HUD_Y, WIDTH, HUD_HEIGHT)
    pygame.draw.rect(SCREEN, DARK_GRAY, hud_rect)
    pygame.draw.rect(SCREEN, WHITE, hud_rect, 2)
    
    # HUD Title
    title_text = HUD_FONT.render("GAME STATS", True, WHITE)
    SCREEN.blit(title_text, (10, HUD_Y + 5))
    
    # Stats positioning
    col1_x = 10
    col2_x = 200
    col3_x = 400
    col4_x = 600
    stats_y = HUD_Y + 30
    
    # Credit Score
    credit_color = RED if game_stats.credit_score < 300 else ORANGE if game_stats.credit_score < 600 else GREEN if game_stats.credit_score >= 700 else YELLOW
    credit_text = "N/A" if game_stats.credit_score == 0 else str(game_stats.credit_score)
    credit_surface = HUD_FONT_SMALL.render(f"Credit Score: {credit_text}", True, credit_color)
    SCREEN.blit(credit_surface, (col1_x, stats_y))
    
    # Bank Accounts
    debit_surface = HUD_FONT_SMALL.render(f"Debit: ${game_stats.debit_balance:,.2f}", True, GREEN)
    SCREEN.blit(debit_surface, (col1_x, stats_y + 20))
    
    credit_surface = HUD_FONT_SMALL.render(f"Credit: -${game_stats.credit_balance:,.2f}", True, RED)
    SCREEN.blit(credit_surface, (col1_x, stats_y + 35))
    
    savings_surface = HUD_FONT_SMALL.render(f"Savings: ${game_stats.savings_balance:,.2f}", True, LIGHT_BLUE)
    SCREEN.blit(savings_surface, (col1_x, stats_y + 50))
    
    # Physical Health
    health_color = RED if game_stats.physical_health < 30 else ORANGE if game_stats.physical_health < 60 else GREEN
    health_text = "N/A" if game_stats.physical_health == 0 else f"{game_stats.physical_health}%"
    physical_surface = HUD_FONT_SMALL.render(f"Physical Health: {health_text}", True, health_color)
    SCREEN.blit(physical_surface, (col2_x, stats_y))
    
    # Mental Health
    mental_color = RED if game_stats.mental_health < 30 else ORANGE if game_stats.mental_health < 60 else GREEN
    mental_text = "N/A" if game_stats.mental_health == 0 else f"{game_stats.mental_health}%"
    mental_surface = HUD_FONT_SMALL.render(f"Mental Health: {mental_text}", True, mental_color)
    SCREEN.blit(mental_surface, (col2_x, stats_y + 20))
    
    # Total Wealth
    game_stats.update_total_wealth()
    wealth_color = RED if game_stats.total_wealth < 0 else GREEN if game_stats.total_wealth > 1000 else WHITE
    wealth_surface = HUD_FONT_SMALL.render(f"Total Wealth: ${game_stats.total_wealth:,.2f}", True, wealth_color)
    SCREEN.blit(wealth_surface, (col3_x, stats_y))
    
    # Game Score
    score_surface = HUD_FONT_SMALL.render(f"Game Score: {game_stats.game_score:,}", True, YELLOW)
    SCREEN.blit(score_surface, (col4_x, stats_y))

def draw_settings_menu():
    """Draw the settings menu with audio controls"""
    # Settings title
    title_text = FONT.render("SETTINGS", True, WHITE)
    SCREEN.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
    
    # Audio settings
    music_status = "ON" if music_enabled else "OFF"
    music_color = GREEN if music_enabled else RED
    music_text = HUD_FONT.render(f"Music: {music_status} (Press M to toggle)", True, music_color)
    SCREEN.blit(music_text, (WIDTH//2 - music_text.get_width()//2, 200))
    
    sound_status = "ON" if sound_enabled else "OFF"
    sound_color = GREEN if sound_enabled else RED
    sound_text = HUD_FONT.render(f"Sound Effects: {sound_status} (Press S to toggle)", True, sound_color)
    SCREEN.blit(sound_text, (WIDTH//2 - sound_text.get_width()//2, 230))
    
    # Volume controls
    volume_text = HUD_FONT.render(f"Music Volume: {int(MUSIC_VOLUME * 100)}% (Use +/- to adjust)", True, WHITE)
    SCREEN.blit(volume_text, (WIDTH//2 - volume_text.get_width()//2, 280))
    
    # Instructions
    instructions = [
        "Press ESC to return to menu",
        "M - Toggle Music",
        "S - Toggle Sound Effects",
        "+/- - Adjust Music Volume"
    ]
    
    y_offset = 350
    for instruction in instructions:
        text = HUD_FONT_SMALL.render(instruction, True, WHITE)
        SCREEN.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
        y_offset += 25

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

# College selector instance
college_selector = CollegeSelector()
selected_college = None

# Start with menu music
if audio_files['menu_music']:
    play_music(audio_files['menu_music'])

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
                    # Play button click sound
                    play_sound(audio_files['button_click'])
                    # Launch college selector
                    selected_college = college_selector.run()
                    if selected_college:
                        state = GAME
                        # Switch to game music
                        if audio_files['game_music']:
                            play_music(audio_files['game_music'])
                        play_sound(audio_files['success_sound'])
                elif settings_button.is_clicked(event.pos):
                    play_sound(audio_files['button_click'])
                    state = SETTINGS

        elif state == SETTINGS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_sound(audio_files['button_click'])
                    state = MENU
                    # Return to menu music
                    if audio_files['menu_music']:
                        play_music(audio_files['menu_music'])
                elif event.key == pygame.K_m:
                    toggle_music()
                elif event.key == pygame.K_s:
                    toggle_sound()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    MUSIC_VOLUME = min(1.0, MUSIC_VOLUME + 0.1)
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                elif event.key == pygame.K_MINUS:
                    MUSIC_VOLUME = max(0.0, MUSIC_VOLUME - 0.1)
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)

        elif state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_sound(audio_files['button_click'])
                    state = MENU
                    # Return to menu music
                    if audio_files['menu_music']:
                        play_music(audio_files['menu_music'])

    if state == MENU:
        play_button.draw(SCREEN)
        settings_button.draw(SCREEN)

    elif state == SETTINGS:
        draw_settings_menu()

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
                # If collided, undo move and play collision sound
                player_rect.topleft = original_pos
                play_sound(audio_files['collision_sound'])
                break

        # Center camera on player
        camera_x = player_rect.centerx - WIDTH // 2
        camera_y = player_rect.centery - HEIGHT // 2

        # Clamp camera to world bounds (adjust for HUD)
        camera_x = max(0, min(camera_x, WORLD_WIDTH - WIDTH))
        camera_y = max(0, min(camera_y, WORLD_HEIGHT - (HEIGHT - HUD_HEIGHT)))

        # Draw world background
        SCREEN.fill((30, 30, 60))  # dark blue background

        # Draw obstacles
        for obs in obstacles:
            obs_screen = obs.move(-camera_x, -camera_y)
            # Only draw if obstacle is visible (not in HUD area)
            if obs_screen.bottom <= HEIGHT - HUD_HEIGHT:
                pygame.draw.rect(SCREEN, WHITE, obs_screen)

        # Draw player
        player_screen_rect = player_rect.move(-camera_x, -camera_y)
        pygame.draw.rect(SCREEN, RED, player_screen_rect)
        
        # Show selected college info in game (above HUD)
        if selected_college:
            college_name = selected_college.get('school.name', 'Unknown College')
            earnings = selected_college.get('latest.earnings.10_yrs_after_entry.median')
            
            # College info HUD
            name_text = pygame.font.SysFont(None, 24).render(f"College: {college_name}", True, WHITE)
            SCREEN.blit(name_text, (10, 10))
            
            if earnings:
                earnings_text = pygame.font.SysFont(None, 24).render(f"Expected Earnings: ${earnings:,}", True, GREEN)
                SCREEN.blit(earnings_text, (10, 35))
        
        # Draw HUD
        draw_hud()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
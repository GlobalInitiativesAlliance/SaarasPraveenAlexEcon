"""Clean, minimalist classroom interior"""

import pygame
from src.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, UI_HEIGHT
from src.core.game_world import GameObjective
import math

class ClassroomInterior:
    """Clean classroom with minimal UI clutter"""
    
    def __init__(self, game, quiz_activity=None, interior_type="classroom"):
        self.game = game
        self.quiz_activity = quiz_activity
        self.interior_type = interior_type
        self.active = False
        
        # Room dimensions
        self.room_width = 15
        self.room_height = 15
        self.room_x = (SCREEN_WIDTH - self.room_width * TILE_SIZE) // 2
        self.room_y = (SCREEN_HEIGHT - UI_HEIGHT - self.room_height * TILE_SIZE) // 2 + 50
        
        # Player state
        self.player_x = 8
        self.player_y = 13
        self.player_facing = 'up'
        self.player_in_seat = False
        
        # Lesson state
        self.lesson_started = False
        self.lesson_phase = 0
        self.lesson_complete = False
        self.showing_dialogue = False
        self.current_dialogue = []
        self.dialogue_index = 0
        
        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.dialogue_font = pygame.font.Font(None, 24)
        self.hint_font = pygame.font.Font(None, 22)
        
        # Animation timers
        self.hint_alpha = 255
        self.hint_fade_direction = -2
        self.arrow_bounce = 0
        
        # Simple desk layout
        self.player_seat_pos = (8, 7)  # Center of room
        
        # Teacher
        self.teacher = {
            'x': 8,
            'y': 2,
            'facing': 'down',
            'name': 'Ms. Rodriguez'
        }
        
        # Other students (simplified)
        self.student_positions = [
            (5, 5), (7, 5), (9, 5), (11, 5),
            (5, 7), (11, 7),  # Player seat at (8, 7)
            (5, 9), (7, 9), (9, 9), (11, 9)
        ]
        
        # Create collision map
        self.create_collision_map()
        
        # Start with a clear prompt instead of dialogue
        self.show_initial_prompt = True
        self.prompt_timer = 0
        
    def enter(self):
        """Called when entering the classroom"""
        self.active = True
        
    def create_collision_map(self):
        """Create simple collision map"""
        self.collision_map = [[False for _ in range(self.room_width)] for _ in range(self.room_height)]
        
        # Just walls and teacher position
        for x in range(self.room_width):
            self.collision_map[0][x] = True
            self.collision_map[self.room_height - 1][x] = True
        for y in range(self.room_height):
            self.collision_map[y][0] = True
            self.collision_map[y][self.room_width - 1] = True
            
        # Teacher
        self.collision_map[self.teacher['y']][self.teacher['x']] = True
        
        # Door
        self.collision_map[self.room_height - 1][8] = False
        
    def handle_input(self, keys):
        """Handle player input"""
        if self.showing_dialogue:
            return
            
        if not self.player_in_seat:
            new_x, new_y = self.player_x, self.player_y
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x -= 1
                self.player_facing = 'left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x += 1
                self.player_facing = 'right'
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                new_y -= 1
                self.player_facing = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                new_y += 1
                self.player_facing = 'down'
                
            # Check bounds and collision
            if (0 <= new_x < self.room_width and 
                0 <= new_y < self.room_height and 
                not self.collision_map[new_y][new_x]):
                self.player_x = new_x
                self.player_y = new_y
                
            # Check if at seat
            if (self.player_x, self.player_y) == self.player_seat_pos and not self.lesson_started:
                self.player_in_seat = True
                self.start_lesson()
                
            # Check if at door to exit
            if self.player_y == self.room_height - 1 and self.player_x == 8:
                if self.lesson_complete:
                    self.exit_classroom()
                    
    def handle_event(self, event):
        """Handle events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if self.show_initial_prompt:
                    self.show_initial_prompt = False
                elif self.showing_dialogue:
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.current_dialogue):
                        self.showing_dialogue = False
                        self.dialogue_index = 0
                        
                        if self.lesson_started and not self.lesson_complete:
                            self.complete_lesson()
                            
    def start_lesson(self):
        """Start the lesson"""
        self.lesson_started = True
        self.showing_dialogue = True
        self.current_dialogue = [
            "Good, everyone's here. Let's begin.",
            "Today: Tenant rights - crucial for your future.",
            "Key points: 24hr notice, repairs, stable rent.",
            "Now for a quick quiz to check understanding."
        ]
        self.dialogue_index = 0
        
    def complete_lesson(self):
        """Complete the lesson"""
        self.lesson_complete = True
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.complete_current_objective()
            
    def exit_classroom(self):
        """Exit the classroom"""
        self.active = False
        self.game.current_interior = None
        
    def update(self, dt):
        """Update animations"""
        # Update hint fade
        self.hint_alpha += self.hint_fade_direction
        if self.hint_alpha <= 100:
            self.hint_fade_direction = 2
        elif self.hint_alpha >= 255:
            self.hint_fade_direction = -2
            
        # Update arrow bounce
        self.arrow_bounce = math.sin(pygame.time.get_ticks() * 0.003) * 10
        
        # Update prompt timer
        if self.show_initial_prompt:
            self.prompt_timer += dt
            
    def draw(self, screen):
        """Draw the classroom with minimal clutter"""
        # Dark background
        screen.fill((30, 30, 40))
        
        # Draw floor (simple pattern)
        for y in range(1, self.room_height - 1):
            for x in range(1, self.room_width - 1):
                tile_x = self.room_x + x * TILE_SIZE
                tile_y = self.room_y + y * TILE_SIZE
                
                # Subtle checkerboard pattern
                if (x + y) % 2 == 0:
                    color = (45, 40, 35)
                else:
                    color = (40, 35, 30)
                    
                pygame.draw.rect(screen, color, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                
        # Draw walls (simple)
        wall_color = (60, 55, 50)
        for x in range(self.room_width):
            # Top wall
            pygame.draw.rect(screen, wall_color,
                           (self.room_x + x * TILE_SIZE, self.room_y, TILE_SIZE, TILE_SIZE))
            # Bottom wall
            if x != 8:  # Skip door
                pygame.draw.rect(screen, wall_color,
                               (self.room_x + x * TILE_SIZE, 
                                self.room_y + (self.room_height - 1) * TILE_SIZE, 
                                TILE_SIZE, TILE_SIZE))
                                
        for y in range(1, self.room_height - 1):
            # Side walls
            pygame.draw.rect(screen, wall_color,
                           (self.room_x, self.room_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, wall_color,
                           (self.room_x + (self.room_width - 1) * TILE_SIZE,
                            self.room_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                            
        # Draw door (subtle)
        door_x = self.room_x + 8 * TILE_SIZE
        door_y = self.room_y + (self.room_height - 1) * TILE_SIZE
        pygame.draw.rect(screen, (40, 30, 20), (door_x, door_y, TILE_SIZE, TILE_SIZE))
        
        # Draw simple blackboard (no box, just text)
        board_text = self.font.render("TENANT RIGHTS", True, (200, 200, 200))
        board_rect = board_text.get_rect(center=(self.room_x + 8 * TILE_SIZE, self.room_y + 1.5 * TILE_SIZE))
        screen.blit(board_text, board_rect)
        
        # Draw desks as simple dots/markers
        for pos in self.student_positions:
            desk_x = self.room_x + pos[0] * TILE_SIZE + TILE_SIZE // 2
            desk_y = self.room_y + pos[1] * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(screen, (70, 60, 50), (desk_x, desk_y), 8)
            
        # Highlight player's seat
        if not self.player_in_seat:
            seat_x = self.room_x + self.player_seat_pos[0] * TILE_SIZE
            seat_y = self.room_y + self.player_seat_pos[1] * TILE_SIZE + self.arrow_bounce
            
            # Draw pulsing circle
            pulse_size = 15 + abs(math.sin(pygame.time.get_ticks() * 0.003)) * 5
            pygame.draw.circle(screen, (100, 200, 100, self.hint_alpha), 
                             (seat_x + TILE_SIZE // 2, seat_y + TILE_SIZE // 2), 
                             int(pulse_size), 2)
            
        # Draw all characters
        self.draw_character_sprite(screen, self.teacher['x'], self.teacher['y'], self.teacher['facing'])
        
        for pos in self.student_positions:
            self.draw_character_sprite(screen, pos[0], pos[1], 'up')
            
        self.draw_character_sprite(screen, self.player_x, self.player_y, self.player_facing, is_player=True)
        
        # Draw prompts/dialogue
        if self.show_initial_prompt:
            self.draw_initial_prompt(screen)
        elif self.showing_dialogue and self.dialogue_index < len(self.current_dialogue):
            self.draw_simple_dialogue(screen, self.current_dialogue[self.dialogue_index])
        elif not self.player_in_seat:
            self.draw_hint(screen, "Find your seat (empty desk)")
        elif self.lesson_complete:
            self.draw_hint(screen, "Exit through the door")
            
    def draw_character_sprite(self, screen, grid_x, grid_y, facing='down', is_player=False):
        """Draw character using player sprite or simple shape"""
        pixel_x = self.room_x + grid_x * TILE_SIZE
        pixel_y = self.room_y + grid_y * TILE_SIZE
        
        # Try to use player sprite
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'animations'):
            anim_key = f'idle_{facing}'
            if anim_key in self.game.player.animations and self.game.player.animations[anim_key]:
                sprite = self.game.player.animations[anim_key][0]
                screen.blit(sprite, (pixel_x, pixel_y))
                return
                
        # Simple shape fallback
        color = (200, 100, 100) if is_player else (100, 100, 150)
        pygame.draw.circle(screen, color,
                         (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2),
                         TILE_SIZE // 3)
                         
    def draw_initial_prompt(self, screen):
        """Draw the initial prompt clearly"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Simple centered text
        texts = [
            "Welcome to Tenant Rights Class",
            "",
            "Find your seat to begin",
            "",
            "Press SPACE to continue"
        ]
        
        y = SCREEN_HEIGHT // 2 - 60
        for text in texts:
            if text:
                color = (255, 255, 255) if "Press SPACE" in text else (200, 200, 200)
                text_surf = self.dialogue_font.render(text, True, color)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                screen.blit(text_surf, text_rect)
            y += 30
            
    def draw_simple_dialogue(self, screen, text):
        """Draw dialogue without box clutter"""
        # Dark strip at bottom
        strip_height = 80
        strip_y = SCREEN_HEIGHT - UI_HEIGHT - strip_height - 20
        
        strip = pygame.Surface((SCREEN_WIDTH, strip_height))
        strip.set_alpha(200)
        strip.fill((20, 20, 30))
        screen.blit(strip, (0, strip_y))
        
        # Speaker name
        name_surf = self.dialogue_font.render(self.teacher['name'], True, (255, 200, 100))
        screen.blit(name_surf, (50, strip_y + 10))
        
        # Dialogue text
        text_surf = self.font.render(text, True, (255, 255, 255))
        screen.blit(text_surf, (50, strip_y + 35))
        
        # Continue hint (small and subtle)
        hint_surf = self.font.render("SPACE", True, (150, 150, 150))
        hint_rect = hint_surf.get_rect(right=SCREEN_WIDTH - 50, bottom=strip_y + strip_height - 10)
        screen.blit(hint_surf, hint_rect)
        
    def draw_hint(self, screen, text):
        """Draw a subtle hint"""
        hint_surf = self.hint_font.render(text, True, (200, 200, 200, self.hint_alpha))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(hint_surf, hint_rect)
import pygame
import math
from constants import *


class BuildingInterior:
    """Base class for building interior scenes"""
    def __init__(self, game):
        self.game = game
        self.active = False
        self.transition_alpha = 255  # For fade effects
        self.transition_state = "fade_in"  # fade_in, active, fade_out
        self.transition_speed = 400
        
        # Interior dimensions
        self.interior_width = 20  # tiles
        self.interior_height = 15  # tiles
        self.interior_surface = None
        
        # Player position in interior
        self.interior_player_x = 10
        self.interior_player_y = 12
        
    def enter(self):
        """Enter the building interior"""
        self.active = True
        self.transition_state = "fade_in"
        self.transition_alpha = 255
        self.setup_interior()
        
    def exit(self):
        """Exit the building interior"""
        self.transition_state = "fade_out"
        
    def setup_interior(self):
        """Setup the interior layout - override in subclasses"""
        pass
        
    def update(self, dt):
        """Update interior state and transitions"""
        if self.transition_state == "fade_in":
            self.transition_alpha = max(0, self.transition_alpha - self.transition_speed * dt)
            if self.transition_alpha <= 0:
                self.transition_state = "active"
                
        elif self.transition_state == "fade_out":
            self.transition_alpha = min(255, self.transition_alpha + self.transition_speed * dt)
            if self.transition_alpha >= 255:
                self.active = False
                self.on_exit_complete()
                
    def on_exit_complete(self):
        """Called when exit transition completes"""
        pass
        
    def handle_input(self, keys):
        """Handle input while in interior"""
        pass
        
    def draw(self, screen):
        """Draw the interior scene"""
        if not self.active:
            return
            
        # Draw interior background
        interior_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        interior_surface.fill((40, 35, 30))  # Dark brown interior color
        
        # Draw floor pattern
        floor_color = (80, 70, 60)
        alt_floor_color = (75, 65, 55)
        for y in range(self.interior_height):
            for x in range(self.interior_width):
                screen_x = x * TILE_SIZE + (SCREEN_WIDTH - self.interior_width * TILE_SIZE) // 2
                screen_y = y * TILE_SIZE + (SCREEN_HEIGHT - self.interior_height * TILE_SIZE) // 2
                
                # Checkerboard pattern
                color = floor_color if (x + y) % 2 == 0 else alt_floor_color
                pygame.draw.rect(interior_surface, color, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        
        screen.blit(interior_surface, (0, 0))
        
        # Draw transition overlay
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.transition_alpha)
            screen.blit(fade_surface, (0, 0))


class ClassroomInterior(BuildingInterior):
    """Classroom interior for the tenant rights quiz"""
    def __init__(self, game, quiz_activity):
        super().__init__(game)
        self.quiz_activity = quiz_activity
        self.desks = []
        self.board_rect = None
        self.teacher_pos = None
        self.students = []  # NPC students
        self.player_at_desk = False
        self.player_desk_pos = None
        self.show_quiz_prompt = False
        self.quiz_started = False
        
    def setup_interior(self):
        """Setup classroom layout"""
        # Create desks in rows
        desk_start_x = 3
        desk_start_y = 6
        desk_spacing_x = 3
        desk_spacing_y = 3
        
        for row in range(4):
            for col in range(5):
                desk_x = desk_start_x + col * desk_spacing_x
                desk_y = desk_start_y + row * desk_spacing_y
                self.desks.append((desk_x, desk_y))
                
                # Add some NPC students (not in player's desk)
                if row < 3 and col != 2:  # Leave middle front desk for player
                    self.students.append({
                        'x': desk_x,
                        'y': desk_y - 1,
                        'facing': 'up',
                        'sprite_offset': (row + col) % 3  # Variety in appearance
                    })
        
        # Player's desk (front row, middle)
        self.player_desk_pos = (desk_start_x + 2 * desk_spacing_x, desk_start_y)
        
        # Blackboard position
        board_center_x = self.interior_width // 2
        self.board_rect = pygame.Rect(
            (board_center_x - 4) * TILE_SIZE + (SCREEN_WIDTH - self.interior_width * TILE_SIZE) // 2,
            2 * TILE_SIZE + (SCREEN_HEIGHT - self.interior_height * TILE_SIZE) // 2,
            8 * TILE_SIZE,
            3 * TILE_SIZE
        )
        
        # Teacher position
        self.teacher_pos = (board_center_x, 5)
        
    def handle_input(self, keys):
        """Handle classroom input"""
        if self.quiz_started:
            # Don't handle movement keys during quiz
            return
            
        # Movement in classroom
        new_x, new_y = self.interior_player_x, self.interior_player_y
        move_made = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if new_x > 1:
                new_x -= 1
                move_made = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if new_x < self.interior_width - 2:
                new_x += 1
                move_made = True
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            if new_y > 1:
                new_y -= 1
                move_made = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if new_y < self.interior_height - 2:
                new_y += 1
                move_made = True
        
        # Check collision with desks and walls
        if move_made and not self.check_collision(new_x, new_y):
            self.interior_player_x = new_x
            self.interior_player_y = new_y
            
        # Check if player is at their desk
        if (self.interior_player_x, self.interior_player_y) == self.player_desk_pos:
            self.player_at_desk = True
            self.show_quiz_prompt = True
        else:
            self.player_at_desk = False
            self.show_quiz_prompt = False
            
    def check_collision(self, x, y):
        """Check if position collides with furniture"""
        # Check desks
        for desk_x, desk_y in self.desks:
            if x == desk_x and y == desk_y:
                return True
                
        # Check teacher position
        if x == self.teacher_pos[0] and y == self.teacher_pos[1]:
            return True
            
        # Check walls (leaving entrance at bottom)
        if x <= 0 or x >= self.interior_width - 1:
            return True
        if y <= 0 or (y >= self.interior_height - 1 and x != self.interior_width // 2):
            return True
            
        return False
        
    def start_quiz(self):
        """Transition to quiz on blackboard"""
        self.quiz_started = True
        self.quiz_activity.board_mode = True  # Special flag for board display
        self.quiz_activity.start()
        # Set entrance complete for board mode to skip animation
        self.quiz_activity.entrance_complete = True
        
    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks in the classroom"""
        if self.quiz_started and self.quiz_activity.active:
            # Translate mouse position relative to board
            mouse_x, mouse_y = pos
            
            # Check if click is within board area
            if self.board_rect.collidepoint(mouse_x, mouse_y):
                # Adjust coordinates relative to board
                board_x = mouse_x - self.board_rect.x
                board_y = mouse_y - self.board_rect.y
                
                # Handle quiz options (simplified click areas for board)
                if hasattr(self.quiz_activity, 'option_rects') and self.quiz_activity.option_rects:
                    for i, (opt_x, opt_y, opt_w, opt_h) in enumerate(self.quiz_activity.option_rects):
                        # Check if click is on this option
                        if (opt_x <= mouse_x <= opt_x + opt_w and
                            opt_y <= mouse_y <= opt_y + opt_h):
                            if not self.quiz_activity.show_result:
                                self.quiz_activity.selected_option = i
                                # Submit answer on click
                                if self.quiz_activity.selected_option == self.quiz_activity.questions[self.quiz_activity.current_question]["correct"]:
                                    self.quiz_activity.score += 1
                                self.quiz_activity.show_result = True
                                self.quiz_activity.result_timer = 2.0
                                break
                                
    def handle_key_press(self, key):
        """Handle individual key presses during quiz"""
        if self.quiz_started and self.quiz_activity.active:
            self.quiz_activity.handle_key(key)
            
    def update(self, dt):
        """Update classroom and quiz"""
        super().update(dt)
        
        # Update quiz if it's active
        if self.quiz_started and self.quiz_activity.active:
            self.quiz_activity.update(dt)
        
    def draw(self, screen):
        """Draw classroom interior"""
        if not self.active:
            return
            
        # Call parent to draw base interior
        super().draw(screen)
        
        # Calculate offset for centering
        offset_x = (SCREEN_WIDTH - self.interior_width * TILE_SIZE) // 2
        offset_y = (SCREEN_HEIGHT - self.interior_height * TILE_SIZE) // 2
        
        # Draw walls with windows
        wall_color = (100, 90, 80)
        window_color = (150, 200, 255)
        
        # Back wall with blackboard
        pygame.draw.rect(screen, wall_color, 
                        (offset_x, offset_y, self.interior_width * TILE_SIZE, TILE_SIZE * 2))
        
        # Windows on side walls
        for i in range(2, 5):
            # Left wall window
            pygame.draw.rect(screen, window_color,
                           (offset_x + TILE_SIZE // 4, offset_y + i * TILE_SIZE, 
                            TILE_SIZE // 2, TILE_SIZE))
            # Right wall window  
            pygame.draw.rect(screen, window_color,
                           (offset_x + (self.interior_width - 1) * TILE_SIZE + TILE_SIZE // 4, 
                            offset_y + i * TILE_SIZE, TILE_SIZE // 2, TILE_SIZE))
        
        # Draw blackboard
        pygame.draw.rect(screen, (20, 40, 20), self.board_rect)
        pygame.draw.rect(screen, (80, 60, 40), self.board_rect, 3)
        
        # Blackboard text
        if not self.quiz_started:
            board_font = pygame.font.Font(None, 28)
            title_text = "TENANT RIGHTS"
            title_surface = board_font.render(title_text, True, (255, 255, 255))
            screen.blit(title_surface, 
                       (self.board_rect.centerx - title_surface.get_width() // 2,
                        self.board_rect.y + 20))
            
            subtitle_font = pygame.font.Font(None, 20)
            subtitle_text = "Please take your seat"
            subtitle_surface = subtitle_font.render(subtitle_text, True, (200, 200, 200))
            screen.blit(subtitle_surface,
                       (self.board_rect.centerx - subtitle_surface.get_width() // 2,
                        self.board_rect.y + 50))
        
        # Draw desks
        desk_color = (139, 90, 43)
        for desk_x, desk_y in self.desks:
            screen_x = desk_x * TILE_SIZE + offset_x
            screen_y = desk_y * TILE_SIZE + offset_y
            
            # Desk top
            pygame.draw.rect(screen, desk_color,
                           (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (100, 60, 30),
                           (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 2)
            
            # Highlight player's desk
            if (desk_x, desk_y) == self.player_desk_pos:
                pygame.draw.rect(screen, (255, 220, 100),
                               (screen_x - 2, screen_y - 2, TILE_SIZE + 4, TILE_SIZE + 4), 2)
        
        # Draw NPCs (students and teacher)
        self.draw_npcs(screen, offset_x, offset_y)
        
        # Draw player
        player_screen_x = self.interior_player_x * TILE_SIZE + offset_x
        player_screen_y = self.interior_player_y * TILE_SIZE + offset_y
        
        # Simple player representation (will be replaced with sprite)
        pygame.draw.circle(screen, (255, 100, 100),
                         (player_screen_x + TILE_SIZE // 2, player_screen_y + TILE_SIZE // 2),
                         TILE_SIZE // 3)
        
        # Draw interaction prompt
        if self.show_quiz_prompt and not self.quiz_started:
            prompt_font = pygame.font.Font(None, 24)
            prompt_text = "Press E to start quiz"
            prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 255))
            prompt_bg = pygame.Surface((prompt_surface.get_width() + 20, 35))
            prompt_bg.fill((40, 40, 40))
            prompt_bg.set_alpha(200)
            
            prompt_x = player_screen_x - prompt_surface.get_width() // 2 + TILE_SIZE // 2
            prompt_y = player_screen_y - 50
            
            screen.blit(prompt_bg, (prompt_x - 10, prompt_y - 5))
            screen.blit(prompt_surface, (prompt_x, prompt_y))
            
        # Draw exit prompt at door
        door_x = (self.interior_width // 2) * TILE_SIZE + offset_x
        door_y = (self.interior_height - 1) * TILE_SIZE + offset_y
        
        if (abs(self.interior_player_x - self.interior_width // 2) <= 1 and 
            abs(self.interior_player_y - (self.interior_height - 1)) <= 1):
            exit_font = pygame.font.Font(None, 20)
            exit_text = "Press E to exit"
            exit_surface = exit_font.render(exit_text, True, (255, 255, 200))
            screen.blit(exit_surface, (door_x - 40, door_y - 30))
            
        # Draw door
        pygame.draw.rect(screen, (80, 60, 40),
                        (door_x, door_y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, (60, 40, 20),
                        (door_x, door_y, TILE_SIZE, TILE_SIZE), 2)
        
        # Draw quiz if started
        if self.quiz_started and self.quiz_activity.active:
            self.quiz_activity.draw_on_board(screen, self.board_rect)
            
        # Draw transition overlay
        if self.transition_alpha > 0:
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.transition_alpha)
            screen.blit(fade_surface, (0, 0))
            
    def draw_npcs(self, screen, offset_x, offset_y):
        """Draw teacher and student NPCs"""
        # Draw teacher
        teacher_x = self.teacher_pos[0] * TILE_SIZE + offset_x
        teacher_y = self.teacher_pos[1] * TILE_SIZE + offset_y
        
        # Teacher body (simple representation)
        pygame.draw.circle(screen, (100, 100, 200),
                         (teacher_x + TILE_SIZE // 2, teacher_y + TILE_SIZE // 2),
                         TILE_SIZE // 3)
        
        # Draw students
        student_colors = [(100, 200, 100), (200, 100, 100), (100, 100, 200)]
        for student in self.students:
            student_x = student['x'] * TILE_SIZE + offset_x
            student_y = student['y'] * TILE_SIZE + offset_y
            color = student_colors[student['sprite_offset']]
            
            pygame.draw.circle(screen, color,
                             (student_x + TILE_SIZE // 2, student_y + TILE_SIZE // 2),
                             TILE_SIZE // 3)
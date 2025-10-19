import pygame
import os


class AnimatedPlayer:
    def __init__(self, x, y, tile_size):
        self.x = x  # Tile position
        self.y = y
        self.tile_size = tile_size

        # Pixel position for smooth movement
        self.pixel_x = x * tile_size
        self.pixel_y = y * tile_size
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y

        # Movement
        self.moving = False
        self.move_speed = 4  # Pixels per frame
        self.direction = 'down'  # 'up', 'down', 'left', 'right'

        # Animation
        self.animations = {}
        self.current_animation = 'idle_down'
        self.animation_frame = 0
        self.animation_speed = 0.08  # Faster animation for smoother movement (was 0.15)
        self.animation_timer = 0

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load character animations from premade character spritesheet"""
        # Path to the premade character spritesheet
        sprite_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'moderninteriors-win', '2_Characters', 'Character_Generator',
            '0_Premade_Characters', '32x32', 'Premade_Character_32x32_01.png'
        )

        try:
            # Load the entire spritesheet
            spritesheet = pygame.image.load(sprite_path)
            print(f"Loaded professional character spritesheet")

            # Sprite dimensions on the sheet
            sprite_width = 32
            sprite_height = 32

            # Function to extract a sprite from the sheet
            def get_sprite(col, row):
                rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
                sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                sprite.blit(spritesheet, (0, 0), rect)
                return sprite

            # Load idle animations (row 0, 4 directions: down, left, right, up)
            self.animations['idle_down'] = [get_sprite(0, 0)]
            self.animations['idle_left'] = [get_sprite(1, 0)]
            self.animations['idle_right'] = [get_sprite(2, 0)]
            self.animations['idle_up'] = [get_sprite(3, 0)]

            # Load walk animations with proper 6 frames per direction
            # Walking animations are in rows 1-2
            # Pattern: Each direction gets 6 frames total (3 from row 1, 3 from row 2)

            # Walk down - columns 0,4,8 (row 1) and 0,4,8 (row 2)
            self.animations['walk_down'] = [
                get_sprite(0, 1), get_sprite(4, 1), get_sprite(8, 1),
                get_sprite(0, 2), get_sprite(4, 2), get_sprite(8, 2)
            ]

            # Walk left - columns 1,5,9 (row 1) and 1,5,9 (row 2)
            self.animations['walk_left'] = [
                get_sprite(1, 1), get_sprite(5, 1), get_sprite(9, 1),
                get_sprite(1, 2), get_sprite(5, 2), get_sprite(9, 2)
            ]

            # Walk right - columns 2,6,10 (row 1) and 2,6,10 (row 2)
            self.animations['walk_right'] = [
                get_sprite(2, 1), get_sprite(6, 1), get_sprite(10, 1),
                get_sprite(2, 2), get_sprite(6, 2), get_sprite(10, 2)
            ]

            # Walk up - columns 3,7,11 (row 1) and 3,7,11 (row 2)
            self.animations['walk_up'] = [
                get_sprite(3, 1), get_sprite(7, 1), get_sprite(11, 1),
                get_sprite(3, 2), get_sprite(7, 2), get_sprite(11, 2)
            ]

            print(f"Loaded professional animations: idle (4 dirs), walk (6 frames x 4 dirs)")

        except Exception as e:
            print(f"Error loading spritesheet: {e}")
            # Create fallback colored squares
            placeholder = pygame.Surface((self.tile_size, self.tile_size))
            placeholder.fill((255, 0, 0))
            for anim in ['idle_down', 'idle_up', 'idle_left', 'idle_right']:
                self.animations[anim] = [placeholder]
            for anim in ['walk_down', 'walk_up', 'walk_left', 'walk_right']:
                self.animations[anim] = [placeholder, placeholder]

    def move_to(self, new_x, new_y):
        """Start moving to a new tile position"""
        if self.moving:
            return False  # Already moving

        # Set new target position
        self.x = new_x
        self.y = new_y
        self.target_x = new_x * self.tile_size
        self.target_y = new_y * self.tile_size

        # Determine direction
        dx = self.target_x - self.pixel_x
        dy = self.target_y - self.pixel_y

        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'

        self.moving = True
        self.set_animation(f'walk_{self.direction}')
        return True

    def set_animation(self, anim_name):
        """Change current animation"""
        if anim_name != self.current_animation and anim_name in self.animations:
            self.current_animation = anim_name
            self.animation_frame = 0
            self.animation_timer = 0

    def update(self, dt):
        """Update player position and animation"""
        # Update movement
        if self.moving:
            # Move towards target
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y

            # Move in x direction
            if abs(dx) > self.move_speed:
                self.pixel_x += self.move_speed if dx > 0 else -self.move_speed
            else:
                self.pixel_x = self.target_x

            # Move in y direction
            if abs(dy) > self.move_speed:
                self.pixel_y += self.move_speed if dy > 0 else -self.move_speed
            else:
                self.pixel_y = self.target_y

            # Check if reached target
            if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
                self.moving = False
                self.set_animation(f'idle_{self.direction}')

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            current_anim = self.animations.get(self.current_animation, [])
            if current_anim:
                self.animation_frame = (self.animation_frame + 1) % len(current_anim)

    def draw(self, screen, camera_x, camera_y):
        """Draw the player"""
        # Calculate screen position
        screen_x = self.pixel_x - camera_x
        screen_y = self.pixel_y - camera_y

        # Get current frame
        current_anim = self.animations.get(self.current_animation)
        if current_anim and current_anim[self.animation_frame]:
            screen.blit(current_anim[self.animation_frame], (screen_x, screen_y))
        else:
            # Fallback circle if no sprite
            pygame.draw.circle(screen, (255, 0, 0),
                               (int(screen_x + self.tile_size // 2),
                                int(screen_y + self.tile_size // 2)),
                               self.tile_size // 3)
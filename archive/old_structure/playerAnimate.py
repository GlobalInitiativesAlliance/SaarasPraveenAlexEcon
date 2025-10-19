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
        self.animation_speed = 0.15  # How fast to cycle frames
        self.animation_timer = 0

        # Load sprites
        self.load_animations()

    def load_animations(self):
        """Load all character animations"""
        sprite_dir = os.path.join(os.path.dirname(__file__), 'sprites', 'player')

        # Define which files belong to which animations
        # You'll need to adjust these based on your actual file names
        animation_files = {
            'idle_down': ['idle_front.png'],
            'idle_up': ['idle_back.png'],
            'idle_left': ['idle_left.png'],
            'idle_right': ['idle_right.png'],
            'walk_down': ['walk_front_1.png', 'walk_front_2.png'],
            'walk_up': ['walk_back_1.png', 'walk_back_2.png'],
            'walk_left': ['idle_left.png', 'idle_left.png'],
            'walk_right': ['idle_right.png', 'idle_right.png']
        }

        # Load each animation
        for anim_name, files in animation_files.items():
            self.animations[anim_name] = []
            for file in files:
                path = os.path.join(sprite_dir, file)
                try:
                    # Load and scale the image
                    img = pygame.image.load(path)
                    # Scale to match tile size (adjust if your sprites are different size)
                    img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                    self.animations[anim_name].append(img)
                except:
                    print(f"Warning: Could not load {path}")
                    # Create placeholder if file missing
                    placeholder = pygame.Surface((self.tile_size, self.tile_size))
                    placeholder.fill((255, 0, 255))  # Magenta for missing sprites
                    self.animations[anim_name].append(placeholder)

        # Fallback if no animations loaded
        if not any(self.animations.values()):
            print("No animations loaded, using placeholder")
            placeholder = pygame.Surface((self.tile_size, self.tile_size))
            placeholder.fill((255, 0, 0))
            self.animations['idle_down'] = [placeholder]

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
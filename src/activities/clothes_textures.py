"""
Simple texture loader for the existing ClothesPacking activity
Just adds actual sprites to the existing drag-drop system
"""

import pygame
import os

def load_clothing_sprites():
    """Load actual clothing sprites from game assets"""
    sprites = {}

    # Path to Modern Interiors assets
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'assets', 'moderninteriors-win', '1_Interiors', '16x16'
    )

    try:
        # Load bedroom items spritesheet (has clothing)
        bedroom_sheet = pygame.image.load(os.path.join(base_path, '4_Bedroom_16x16.png'))

        # Define sprite positions in the sheet (16x16 tiles)
        # These are example positions - you'd need to find actual clothing sprites
        sprite_coords = {
            'T-Shirt': (0, 224, 16, 16),      # Shirt on hanger
            'Jeans': (16, 224, 16, 16),       # Folded clothes
            'Underwear Pack': (32, 224, 16, 16),  # Drawer items
            'Hoodie': (48, 224, 16, 16),      # Jacket/coat
            'Jacket': (64, 224, 16, 16),      # Another jacket
            'Dress Shirt': (80, 224, 16, 16), # Formal shirt
            'Sneakers': (96, 224, 16, 16),    # Shoes
            'Socks Pack': (112, 224, 16, 16), # Socks
            'Old Photo': (144, 192, 16, 16),  # Picture frame
            'Belt': (128, 224, 16, 16),       # Accessories
            'Winter Coat': (0, 240, 16, 16),  # Heavy coat
        }

        # Extract and scale sprites
        for name, (x, y, w, h) in sprite_coords.items():
            sprite_rect = pygame.Rect(x, y, w, h)
            sprite = bedroom_sheet.subsurface(sprite_rect)
            # Scale up to fit the item boxes (120x80)
            scaled_sprite = pygame.transform.scale(sprite, (60, 60))
            sprites[name] = scaled_sprite

    except:
        # Fallback to creating simple visual icons if sprites can't load
        print("Could not load sprites, creating fallback visuals")

        # Create simple but better looking placeholders
        icon_designs = {
            'T-Shirt': lambda s: draw_shirt(s),
            'Jeans': lambda s: draw_jeans(s),
            'Underwear Pack': lambda s: draw_underwear(s),
            'Hoodie': lambda s: draw_hoodie(s),
            'Jacket': lambda s: draw_jacket(s),
            'Dress Shirt': lambda s: draw_dress_shirt(s),
            'Sneakers': lambda s: draw_shoes(s),
            'Socks Pack': lambda s: draw_socks(s),
            'Old Photo': lambda s: draw_photo(s),
            'Belt': lambda s: draw_belt(s),
            'Winter Coat': lambda s: draw_coat(s),
        }

        for name, draw_func in icon_designs.items():
            surface = pygame.Surface((100, 70), pygame.SRCALPHA)
            draw_func(surface)
            sprites[name] = surface

    return sprites

def draw_shirt(surface):
    """Draw a simple t-shirt icon"""
    # Body
    pygame.draw.rect(surface, (100, 150, 255), (25, 20, 50, 40), border_radius=5)
    # Sleeves
    pygame.draw.rect(surface, (100, 150, 255), (15, 20, 15, 20), border_radius=3)
    pygame.draw.rect(surface, (100, 150, 255), (70, 20, 15, 20), border_radius=3)
    # Collar
    pygame.draw.arc(surface, (80, 130, 235), (35, 15, 30, 20), 0, 3.14, 4)
    # Optional: Add a simple design
    pygame.draw.circle(surface, (255, 255, 255, 100), (50, 40), 8)

def draw_jeans(surface):
    """Draw simple jeans icon"""
    # Legs
    pygame.draw.rect(surface, (50, 100, 180), (15, 10, 12, 40))
    pygame.draw.rect(surface, (50, 100, 180), (33, 10, 12, 40))
    # Waist
    pygame.draw.rect(surface, (50, 100, 180), (15, 10, 30, 8))
    # Pockets
    pygame.draw.rect(surface, (40, 80, 160), (17, 20, 8, 6))
    pygame.draw.rect(surface, (40, 80, 160), (35, 20, 8, 6))

def draw_underwear(surface):
    """Draw a simple underwear pack icon"""
    pygame.draw.rect(surface, (220, 220, 255), (10, 15, 40, 30))
    pygame.draw.rect(surface, (200, 200, 235), (10, 15, 40, 30), 2)
    # Stack lines
    pygame.draw.line(surface, (180, 180, 215), (10, 25), (50, 25), 1)
    pygame.draw.line(surface, (180, 180, 215), (10, 35), (50, 35), 1)

def draw_hoodie(surface):
    """Draw a hoodie icon"""
    # Body
    pygame.draw.rect(surface, (180, 140, 200), (10, 25, 40, 30))
    # Hood
    pygame.draw.arc(surface, (180, 140, 200), (15, 10, 30, 30), 0, 3.14, 0)
    pygame.draw.ellipse(surface, (180, 140, 200), (15, 10, 30, 20))
    # Pocket
    pygame.draw.rect(surface, (160, 120, 180), (20, 35, 20, 10))

def draw_jacket(surface):
    """Draw a jacket icon"""
    # Body
    pygame.draw.rect(surface, (100, 150, 100), (10, 20, 40, 35))
    # Sleeves
    pygame.draw.rect(surface, (100, 150, 100), (5, 20, 10, 20))
    pygame.draw.rect(surface, (100, 150, 100), (45, 20, 10, 20))
    # Zipper
    pygame.draw.line(surface, (200, 200, 200), (30, 20), (30, 55), 2)

def draw_dress_shirt(surface):
    """Draw a dress shirt icon"""
    # Body
    pygame.draw.rect(surface, (240, 240, 255), (10, 20, 40, 35))
    # Collar
    pygame.draw.polygon(surface, (220, 220, 255), [(20, 20), (30, 15), (40, 20)])
    # Buttons
    for y in range(25, 50, 8):
        pygame.draw.circle(surface, (100, 100, 100), (30, y), 2)

def draw_shoes(surface):
    """Draw sneakers icon"""
    # Left shoe
    pygame.draw.ellipse(surface, (80, 60, 40), (10, 25, 20, 15))
    pygame.draw.ellipse(surface, (80, 60, 40), (10, 35, 20, 8))
    # Right shoe
    pygame.draw.ellipse(surface, (80, 60, 40), (30, 25, 20, 15))
    pygame.draw.ellipse(surface, (80, 60, 40), (30, 35, 20, 8))
    # Laces
    pygame.draw.line(surface, (255, 255, 255), (15, 30), (25, 30), 1)
    pygame.draw.line(surface, (255, 255, 255), (35, 30), (45, 30), 1)

def draw_socks(surface):
    """Draw socks pack icon"""
    pygame.draw.rect(surface, (255, 255, 255), (10, 15, 40, 30))
    pygame.draw.rect(surface, (200, 200, 200), (10, 15, 40, 30), 2)
    # Sock shapes
    pygame.draw.arc(surface, (150, 150, 150), (15, 20, 15, 20), 0, 3.14, 2)
    pygame.draw.arc(surface, (150, 150, 150), (30, 20, 15, 20), 0, 3.14, 2)

def draw_photo(surface):
    """Draw photo frame icon"""
    # Frame
    pygame.draw.rect(surface, (139, 69, 19), (10, 10, 40, 40))
    pygame.draw.rect(surface, (200, 200, 255), (15, 15, 30, 30))
    # Simple picture
    pygame.draw.circle(surface, (255, 220, 100), (25, 25), 5)  # Sun
    pygame.draw.rect(surface, (100, 200, 100), (15, 35, 30, 10))  # Grass

def draw_belt(surface):
    """Draw belt icon"""
    # Belt strap
    pygame.draw.rect(surface, (80, 60, 40), (5, 25, 50, 10))
    # Buckle
    pygame.draw.rect(surface, (192, 192, 192), (5, 23, 12, 14))
    pygame.draw.rect(surface, (50, 50, 50), (7, 25, 8, 10), 1)

def draw_coat(surface):
    """Draw winter coat icon"""
    # Body (thicker)
    pygame.draw.rect(surface, (50, 50, 100), (8, 15, 44, 40))
    # Sleeves
    pygame.draw.rect(surface, (50, 50, 100), (3, 15, 12, 25))
    pygame.draw.rect(surface, (50, 50, 100), (45, 15, 12, 25))
    # Fur collar
    pygame.draw.ellipse(surface, (200, 200, 200), (15, 10, 30, 15))
    # Buttons
    for y in range(25, 45, 10):
        pygame.draw.circle(surface, (30, 30, 30), (30, y), 3)


def enhance_clothes_packing_draw(original_draw_method):
    """Decorator to enhance the existing draw method with sprites"""

    # Load sprites once
    sprites = load_clothing_sprites()

    def enhanced_draw(self, screen):
        # Call original draw method first
        original_draw_method(self, screen)

        # Then overlay sprites on top of the existing rectangles
        for item in self.closet_items:
            if not item["packed"] and item != self.dragged_item:
                rect = self.get_item_rect(item)

                # Draw sprite if available
                if item["name"] in sprites:
                    sprite = sprites[item["name"]]
                    # Center sprite in the rectangle
                    sprite_x = rect.x + (rect.width - sprite.get_width()) // 2
                    sprite_y = rect.y + 5
                    screen.blit(sprite, (sprite_x, sprite_y))

        # Also draw sprite for dragged item if dragging
        if self.dragging and self.dragged_item and self.dragged_item["name"] in sprites:
            mouse_pos = pygame.mouse.get_pos()
            sprite = sprites[self.dragged_item["name"]]
            # Draw at mouse position with offset
            screen.blit(sprite, (
                mouse_pos[0] - self.drag_offset[0] + 30,
                mouse_pos[1] - self.drag_offset[1] + 5
            ))

    return enhanced_draw
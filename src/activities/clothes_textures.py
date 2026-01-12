"""
Simple texture loader for the existing ClothesPacking activity
Just adds actual sprites to the existing drag-drop system
"""

import pygame
import os
from src.core.transform_cache import get_scaled

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
            'Nightlamp': (160, 192, 16, 16),  # Lamp sprite
        }

        # Extract and scale sprites
        for name, (x, y, w, h) in sprite_coords.items():
            sprite_rect = pygame.Rect(x, y, w, h)
            sprite = bedroom_sheet.subsurface(sprite_rect)
            # Scale up to fit the item boxes (120x80) - NOT CACHED (loaded once at startup)
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
            'Nightlamp': lambda s: draw_nightlamp(s),
        }

        for name, draw_func in icon_designs.items():
            surface = pygame.Surface((100, 70), pygame.SRCALPHA)
            draw_func(surface)
            sprites[name] = surface

    return sprites

def draw_shirt(surface):
    """Draw enhanced t-shirt icon with detailed graphics"""
    # Shadow under shirt
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (20, 58, 60, 8))

    # Color palette
    shirt_color = (100, 150, 255)  # Vibrant blue
    shirt_shadow = (70, 120, 220)  # Darker blue for shadows
    shirt_light = (130, 180, 255)  # Lighter blue for highlights

    # Main body (folded view with rounded edges)
    pygame.draw.rect(surface, shirt_shadow, (26, 21, 48, 38), border_radius=6)
    pygame.draw.rect(surface, shirt_color, (25, 20, 48, 38), border_radius=6)

    # Sleeves with depth (folded appearance)
    # Left sleeve
    left_sleeve = [
        (25, 22),  # Top inner
        (15, 26),  # Top outer
        (15, 38),  # Bottom outer
        (25, 42)   # Bottom inner
    ]
    pygame.draw.polygon(surface, shirt_shadow, left_sleeve)
    pygame.draw.polygon(surface, shirt_color, [(x-1, y) for x, y in left_sleeve])

    # Right sleeve
    right_sleeve = [
        (73, 22),  # Top inner
        (83, 26),  # Top outer
        (83, 38),  # Bottom outer
        (73, 42)   # Bottom inner
    ]
    pygame.draw.polygon(surface, shirt_shadow, right_sleeve)
    pygame.draw.polygon(surface, shirt_color, [(x+1, y) for x, y in right_sleeve])

    # Sleeve cuffs (ribbed detail)
    pygame.draw.line(surface, shirt_shadow, (15, 37), (25, 41), 2)
    pygame.draw.line(surface, shirt_shadow, (73, 41), (83, 37), 2)

    # Neck opening (V-neck style)
    neck_points = [
        (49, 20),   # Center bottom
        (42, 16),   # Left top
        (40, 20),   # Left shoulder
    ]
    pygame.draw.polygon(surface, shirt_shadow, neck_points)

    # Right side of V-neck
    neck_points_r = [
        (49, 20),   # Center bottom
        (56, 16),   # Right top
        (58, 20),   # Right shoulder
    ]
    pygame.draw.polygon(surface, shirt_shadow, neck_points_r)

    # Neck collar trim
    pygame.draw.arc(surface, shirt_shadow, (40, 14, 18, 14), 0, 3.14, 3)

    # Print/logo design (star pattern)
    star_center = (49, 38)
    star_color = (255, 255, 255, 180)
    star_points = []
    import math
    for i in range(5):
        # Outer points
        angle = (i * 4 * math.pi / 5) - math.pi / 2
        x = star_center[0] + int(10 * math.cos(angle))
        y = star_center[1] + int(10 * math.sin(angle))
        star_points.append((x, y))
        # Inner points
        angle = ((i * 4 + 2) * math.pi / 5) - math.pi / 2
        x = star_center[0] + int(5 * math.cos(angle))
        y = star_center[1] + int(5 * math.sin(angle))
        star_points.append((x, y))

    pygame.draw.polygon(surface, star_color, star_points)

    # Fabric wrinkles (natural folds)
    pygame.draw.line(surface, shirt_shadow, (30, 28), (32, 40), 1)
    pygame.draw.line(surface, shirt_shadow, (66, 28), (64, 40), 1)
    pygame.draw.line(surface, shirt_shadow, (45, 52), (53, 52), 1)

    # Stitching detail at bottom hem
    for x in range(28, 70, 3):
        pygame.draw.circle(surface, shirt_shadow, (x, 56), 1)

    # Highlights (light reflection on fabric)
    pygame.draw.line(surface, shirt_light, (28, 24), (30, 35), 2)
    pygame.draw.line(surface, shirt_light, (68, 24), (66, 35), 2)
    pygame.draw.ellipse(surface, (255, 255, 255, 50), (35, 25, 28, 18))

def draw_jeans(surface):
    """Draw enhanced jeans icon with denim texture and details"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (22, 58, 36, 8))

    # Color palette - classic denim
    denim_base = (70, 100, 150)
    denim_dark = (50, 75, 120)
    denim_light = (90, 125, 180)
    denim_fade = (100, 140, 200)

    # Folded jeans view - waistband at top
    # Waistband (wider, folded over)
    pygame.draw.rect(surface, denim_dark, (25, 12, 50, 8), border_radius=2)
    pygame.draw.rect(surface, denim_base, (25, 10, 50, 8), border_radius=2)

    # Belt loops (small vertical rectangles)
    loop_positions = [28, 40, 52, 64, 70]
    for x in loop_positions:
        pygame.draw.rect(surface, denim_dark, (x, 10, 3, 6))
        pygame.draw.line(surface, denim_light, (x, 10), (x, 15), 1)

    # Main jeans body (folded)
    pygame.draw.rect(surface, denim_dark, (26, 19, 48, 38), border_radius=4)
    pygame.draw.rect(surface, denim_base, (25, 18, 48, 38), border_radius=4)

    # Legs visible at bottom (folded view)
    # Left leg
    pygame.draw.rect(surface, denim_dark, (28, 35, 18, 21))
    pygame.draw.rect(surface, denim_base, (27, 34, 18, 21))

    # Right leg
    pygame.draw.rect(surface, denim_dark, (54, 35, 18, 21))
    pygame.draw.rect(surface, denim_fade, (53, 34, 18, 21))  # Lighter fade

    # Front pockets with stitching
    # Left pocket
    pocket_left = [
        (30, 20),
        (40, 20),
        (39, 32),
        (31, 32)
    ]
    pygame.draw.polygon(surface, denim_dark, pocket_left)
    # Pocket stitching (curved)
    pygame.draw.arc(surface, (200, 150, 50), (30, 18, 10, 10), 0, 3.14, 1)
    pygame.draw.line(surface, (200, 150, 50), (31, 22), (31, 30), 1)
    pygame.draw.line(surface, (200, 150, 50), (39, 22), (39, 30), 1)

    # Right pocket
    pocket_right = [
        (58, 20),
        (68, 20),
        (67, 32),
        (59, 32)
    ]
    pygame.draw.polygon(surface, denim_dark, pocket_right)
    # Pocket stitching
    pygame.draw.arc(surface, (200, 150, 50), (58, 18, 10, 10), 0, 3.14, 1)
    pygame.draw.line(surface, (200, 150, 50), (59, 22), (59, 30), 1)
    pygame.draw.line(surface, (200, 150, 50), (67, 22), (67, 30), 1)

    # Coin pocket (small pocket on right)
    pygame.draw.rect(surface, denim_dark, (62, 21, 6, 6))
    pygame.draw.rect(surface, denim_dark, (62, 21, 6, 6), 1)

    # Zipper detail (center)
    pygame.draw.line(surface, (180, 180, 180), (49, 18), (49, 28), 2)
    pygame.draw.rect(surface, (200, 200, 200), (48, 28, 3, 4))  # Zipper pull

    # Button at waist
    pygame.draw.circle(surface, (150, 120, 80), (49, 14), 3)
    pygame.draw.circle(surface, (180, 150, 100), (49, 14), 2)

    # Seam lines down legs (orange/gold stitching)
    stitch_color = (200, 150, 50)
    # Left leg seam
    pygame.draw.line(surface, stitch_color, (36, 35), (36, 54), 1)
    # Right leg seam
    pygame.draw.line(surface, stitch_color, (62, 35), (62, 54), 1)
    # Center seam
    pygame.draw.line(surface, stitch_color, (49, 28), (49, 35), 1)

    # Back pockets (visible on fold)
    # Small rectangular shapes on sides
    pygame.draw.rect(surface, denim_dark, (26, 42, 8, 10))
    pygame.draw.rect(surface, stitch_color, (26, 42, 8, 10), 1)
    pygame.draw.rect(surface, denim_dark, (65, 42, 8, 10))
    pygame.draw.rect(surface, stitch_color, (65, 42, 8, 10), 1)

    # Denim texture (cross-hatch pattern)
    for i in range(20, 55, 4):
        pygame.draw.line(surface, (denim_light[0], denim_light[1], denim_light[2], 30), (27, i), (71, i), 1)

    # Fading effect (worn areas)
    fade_areas = [(35, 22, 8, 6), (56, 24, 8, 6), (40, 48, 12, 6)]
    for area in fade_areas:
        pygame.draw.rect(surface, (*denim_fade, 80), area)

    # Hem stitching at leg bottoms
    for x in range(28, 45, 3):
        pygame.draw.circle(surface, stitch_color, (x, 54), 1)
    for x in range(54, 71, 3):
        pygame.draw.circle(surface, stitch_color, (x, 54), 1)

    # Rivets (metal reinforcements)
    rivet_color = (180, 150, 100)
    pygame.draw.circle(surface, rivet_color, (30, 20), 2)
    pygame.draw.circle(surface, rivet_color, (68, 20), 2)
    pygame.draw.circle(surface, (120, 100, 70), (30, 20), 1)
    pygame.draw.circle(surface, (120, 100, 70), (68, 20), 1)

def draw_underwear(surface):
    """Draw enhanced underwear pack with packaging details"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (18, 56, 64, 8))

    # Packaging colors
    pack_bg = (240, 245, 255)
    pack_border = (200, 210, 230)
    underwear_color = (255, 255, 255)
    label_color = (100, 150, 255)

    # Main package (clear plastic look)
    pygame.draw.rect(surface, (180, 190, 210), (21, 16, 58, 42), border_radius=4)
    pygame.draw.rect(surface, pack_bg, (20, 15, 58, 42), border_radius=4)
    pygame.draw.rect(surface, pack_border, (20, 15, 58, 42), 2, border_radius=4)

    # Folded underwear stack (3 visible)
    # Bottom layer
    underwear_positions = [(25, 35), (25, 30), (25, 25)]
    for i, (x, y) in enumerate(underwear_positions):
        shade = 220 - (i * 15)
        # Waistband
        pygame.draw.rect(surface, (shade, shade, shade + 20), (x, y, 48, 4))
        pygame.draw.rect(surface, (180, 180, 200), (x, y, 48, 2))
        # Body
        pygame.draw.ellipse(surface, (shade, shade, shade + 20), (x + 2, y + 3, 44, 12))
        # Elastic band detail
        pygame.draw.line(surface, (150, 150, 170), (x + 4, y + 1), (x + 44, y + 1), 1)

    # Brand label at top
    pygame.draw.rect(surface, label_color, (30, 17, 38, 10), border_radius=2)
    pygame.draw.rect(surface, (255, 255, 255), (32, 19, 34, 6))

    # Label text simulation (lines)
    pygame.draw.line(surface, label_color, (34, 20), (44, 20), 1)
    pygame.draw.line(surface, label_color, (34, 22), (50, 22), 1)
    pygame.draw.line(surface, label_color, (34, 24), (42, 24), 1)

    # Package seal/tape at top
    tape_color = (255, 200, 100, 120)
    pygame.draw.rect(surface, tape_color, (35, 15, 28, 6))
    pygame.draw.line(surface, (200, 150, 50), (35, 17), (63, 17), 1)

    # Barcode on side
    barcode_x = 72
    for i in range(8):
        width = 1 if i % 2 == 0 else 2
        pygame.draw.line(surface, (0, 0, 0), (barcode_x + i * 2, 45), (barcode_x + i * 2, 52), width)

    # Size indicator (circle sticker)
    pygame.draw.circle(surface, (255, 100, 100), (70, 25), 6)
    pygame.draw.circle(surface, (255, 255, 255), (70, 25), 4)
    # "M" for medium
    pygame.draw.line(surface, (255, 100, 100), (68, 26), (68, 24), 1)
    pygame.draw.line(surface, (255, 100, 100), (72, 26), (72, 24), 1)
    pygame.draw.line(surface, (255, 100, 100), (68, 24), (70, 25), 1)
    pygame.draw.line(surface, (255, 100, 100), (70, 25), (72, 24), 1)

    # Plastic wrap texture (subtle shine lines)
    for i in range(5):
        y = 20 + i * 8
        pygame.draw.line(surface, (255, 255, 255, 50), (22, y), (30, y - 5), 1)

    # Package count label ("3-PACK")
    pygame.draw.rect(surface, (50, 200, 100), (22, 50, 24, 6), border_radius=1)
    pygame.draw.line(surface, (255, 255, 255), (24, 52), (28, 52), 1)
    pygame.draw.line(surface, (255, 255, 255), (30, 52), (34, 52), 1)
    pygame.draw.line(surface, (255, 255, 255), (36, 52), (42, 52), 1)

def draw_hoodie(surface):
    """Draw enhanced hoodie with drawstring and kangaroo pocket"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (18, 58, 64, 8))

    # Color palette - gray hoodie
    hoodie_base = (120, 120, 140)
    hoodie_dark = (90, 90, 110)
    hoodie_light = (150, 150, 170)
    drawstring_color = (200, 200, 210)

    # Hood (visible at top, folded back)
    hood_outer = [
        (35, 12),  # Left top
        (25, 18),  # Left outer
        (25, 24),  # Left bottom
        (50, 22),  # Center bottom
        (75, 24),  # Right bottom
        (75, 18),  # Right outer
        (65, 12)   # Right top
    ]
    pygame.draw.polygon(surface, hoodie_dark, hood_outer)
    pygame.draw.polygon(surface, hoodie_base, [(x, y-1) for x, y in hood_outer])

    # Hood inner lining (visible fold)
    hood_inner = [
        (38, 14),
        (30, 20),
        (30, 24),
        (50, 22),
        (70, 24),
        (70, 20),
        (62, 14)
    ]
    pygame.draw.polygon(surface, hoodie_light, hood_inner)

    # Main body (folded hoodie)
    pygame.draw.rect(surface, hoodie_dark, (24, 24, 52, 34), border_radius=6)
    pygame.draw.rect(surface, hoodie_base, (23, 23, 52, 34), border_radius=6)

    # Sleeves (folded on sides)
    # Left sleeve
    pygame.draw.rect(surface, hoodie_dark, (18, 26, 10, 24))
    pygame.draw.rect(surface, hoodie_base, (17, 25, 10, 24))

    # Right sleeve
    pygame.draw.rect(surface, hoodie_dark, (72, 26, 10, 24))
    pygame.draw.rect(surface, hoodie_light, (71, 25, 10, 24))

    # Ribbed cuffs on sleeves
    for y in [47, 49]:
        pygame.draw.line(surface, hoodie_dark, (17, y), (27, y), 2)
        pygame.draw.line(surface, hoodie_dark, (71, y), (81, y), 2)

    # Kangaroo pocket (front center)
    pocket_color = hoodie_dark
    # Pocket opening (curved)
    pygame.draw.arc(surface, pocket_color, (33, 32, 34, 16), 0, 3.14, 3)
    # Pocket body
    pygame.draw.ellipse(surface, pocket_color, (35, 38, 30, 14))
    # Pocket stitching
    pygame.draw.arc(surface, (70, 70, 90), (33, 32, 34, 16), 0, 3.14, 1)

    # Drawstrings from hood
    # Left string
    pygame.draw.line(surface, drawstring_color, (42, 22), (38, 28), 2)
    pygame.draw.line(surface, drawstring_color, (38, 28), (38, 32), 2)
    pygame.draw.circle(surface, drawstring_color, (38, 33), 2)

    # Right string
    pygame.draw.line(surface, drawstring_color, (58, 22), (62, 28), 2)
    pygame.draw.line(surface, drawstring_color, (62, 28), (62, 32), 2)
    pygame.draw.circle(surface, drawstring_color, (62, 33), 2)

    # Ribbed hem at bottom
    for y in [54, 56]:
        pygame.draw.line(surface, hoodie_dark, (24, y), (75, y), 2)

    # Fabric texture/wrinkles
    pygame.draw.line(surface, hoodie_dark, (28, 30), (30, 42), 1)
    pygame.draw.line(surface, hoodie_dark, (70, 30), (68, 42), 1)

    # Stitching along edges
    pygame.draw.line(surface, (70, 70, 90), (24, 25), (24, 56), 1)
    pygame.draw.line(surface, (70, 70, 90), (74, 25), (74, 56), 1)

    # Hood edge stitching
    pygame.draw.arc(surface, (70, 70, 90), (28, 12, 44, 16), 0, 3.14, 1)

    # Highlight on hood (light reflection)
    pygame.draw.line(surface, hoodie_light, (40, 16), (45, 20), 2)

def draw_jacket(surface):
    """Draw enhanced jacket with zipper and pockets"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (15, 58, 70, 8))

    # Color palette - olive green jacket
    jacket_base = (100, 130, 90)
    jacket_dark = (70, 100, 60)
    jacket_light = (130, 160, 120)
    zipper_color = (180, 180, 180)

    # Main body (split for zipper)
    # Left side
    pygame.draw.rect(surface, jacket_dark, (20, 18, 28, 40), border_radius=4)
    pygame.draw.rect(surface, jacket_base, (19, 17, 28, 40), border_radius=4)

    # Right side
    pygame.draw.rect(surface, jacket_dark, (52, 18, 28, 40), border_radius=4)
    pygame.draw.rect(surface, jacket_light, (51, 17, 28, 40), border_radius=4)

    # Collar (standing collar)
    collar_left = [
        (19, 17),
        (19, 12),
        (25, 10),
        (30, 12)
    ]
    pygame.draw.polygon(surface, jacket_dark, collar_left)
    pygame.draw.polygon(surface, jacket_base, [(x, y-1) for x, y in collar_left])

    collar_right = [
        (79, 17),
        (79, 12),
        (73, 10),
        (68, 12)
    ]
    pygame.draw.polygon(surface, jacket_dark, collar_right)
    pygame.draw.polygon(surface, jacket_light, [(x, y-1) for x, y in collar_right])

    # Sleeves
    # Left sleeve
    pygame.draw.rect(surface, jacket_dark, (12, 20, 12, 26))
    pygame.draw.rect(surface, jacket_base, (11, 19, 12, 26))
    # Sleeve cuff
    pygame.draw.rect(surface, jacket_dark, (11, 43, 12, 5))

    # Right sleeve
    pygame.draw.rect(surface, jacket_dark, (76, 20, 12, 26))
    pygame.draw.rect(surface, jacket_light, (75, 19, 12, 26))
    # Sleeve cuff
    pygame.draw.rect(surface, jacket_dark, (75, 43, 12, 5))

    # Zipper (center, metallic)
    # Zipper teeth
    pygame.draw.line(surface, (120, 120, 120), (49, 17), (49, 56), 3)
    pygame.draw.line(surface, zipper_color, (49, 17), (49, 56), 2)

    # Zipper pull tab
    pygame.draw.rect(surface, (200, 200, 200), (47, 24, 4, 8), border_radius=1)
    pygame.draw.circle(surface, (150, 150, 150), (49, 28), 3)
    pygame.draw.circle(surface, zipper_color, (49, 28), 2)

    # Zipper teeth detail
    for y in range(18, 55, 3):
        pygame.draw.line(surface, (140, 140, 140), (47, y), (48, y + 1), 1)
        pygame.draw.line(surface, (140, 140, 140), (51, y), (50, y + 1), 1)

    # Pockets with flaps
    # Left pocket
    # Pocket flap
    pygame.draw.rect(surface, jacket_dark, (22, 32, 20, 8))
    pygame.draw.rect(surface, jacket_base, (22, 31, 20, 8))
    pygame.draw.line(surface, jacket_dark, (23, 38), (41, 38), 1)
    # Pocket opening
    pygame.draw.line(surface, jacket_dark, (22, 40), (42, 40), 2)

    # Right pocket
    # Pocket flap
    pygame.draw.rect(surface, jacket_dark, (56, 32, 20, 8))
    pygame.draw.rect(surface, jacket_light, (56, 31, 20, 8))
    pygame.draw.line(surface, jacket_dark, (57, 38), (75, 38), 1)
    # Pocket opening
    pygame.draw.line(surface, jacket_dark, (56, 40), (76, 40), 2)

    # Snap buttons on pockets
    for x in [25, 38, 59, 72]:
        pygame.draw.circle(surface, (100, 80, 60), (x, 35), 2)
        pygame.draw.circle(surface, (130, 110, 90), (x, 35), 1)

    # Stitching details
    pygame.draw.line(surface, (80, 110, 70), (20, 18), (20, 56), 1)
    pygame.draw.line(surface, (80, 110, 70), (78, 18), (78, 56), 1)

    # Sleeve stitching
    pygame.draw.line(surface, (80, 110, 70), (12, 44), (22, 44), 1)
    pygame.draw.line(surface, (80, 110, 70), (76, 44), (86, 44), 1)

    # Hem at bottom
    pygame.draw.rect(surface, jacket_dark, (19, 54, 60, 4))

def draw_dress_shirt(surface):
    """Draw enhanced dress shirt with collar and buttons"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (18, 58, 64, 8))

    # Color palette - crisp white/light blue shirt
    shirt_base = (230, 240, 255)
    shirt_shadow = (200, 210, 230)
    shirt_light = (250, 255, 255)
    button_color = (200, 200, 210)

    # Main body (folded view)
    pygame.draw.rect(surface, shirt_shadow, (24, 22, 52, 36), border_radius=3)
    pygame.draw.rect(surface, shirt_base, (23, 21, 52, 36), border_radius=3)

    # Collar (pointed dress shirt collar)
    # Left collar point
    collar_left = [
        (35, 21),  # Inner
        (28, 14),  # Point
        (26, 18),  # Outer
        (30, 21)   # Bottom
    ]
    pygame.draw.polygon(surface, shirt_shadow, collar_left)
    pygame.draw.polygon(surface, shirt_base, [(x, y-1) for x, y in collar_left])
    pygame.draw.line(surface, shirt_shadow, (28, 14), (30, 21), 1)

    # Right collar point
    collar_right = [
        (63, 21),  # Inner
        (70, 14),  # Point
        (72, 18),  # Outer
        (68, 21)   # Bottom
    ]
    pygame.draw.polygon(surface, shirt_shadow, collar_right)
    pygame.draw.polygon(surface, shirt_base, [(x, y-1) for x, y in collar_right])
    pygame.draw.line(surface, shirt_shadow, (70, 14), (68, 21), 1)

    # Collar band
    pygame.draw.rect(surface, shirt_shadow, (35, 18, 28, 4))
    pygame.draw.rect(surface, shirt_light, (35, 17, 28, 4))

    # Button placket (center strip)
    pygame.draw.rect(surface, shirt_shadow, (45, 21, 8, 36))
    pygame.draw.rect(surface, shirt_light, (45, 21, 8, 36))

    # Buttons down the front
    button_positions = [24, 30, 36, 42, 48, 54]
    for y in button_positions:
        # Button with hole detail
        pygame.draw.circle(surface, button_color, (49, y), 2)
        pygame.draw.circle(surface, shirt_base, (49, y), 1)
        # Button holes (4 tiny dots)
        pygame.draw.circle(surface, (150, 150, 160), (48, y - 1), 0)
        pygame.draw.circle(surface, (150, 150, 160), (50, y - 1), 0)
        pygame.draw.circle(surface, (150, 150, 160), (48, y + 1), 0)
        pygame.draw.circle(surface, (150, 150, 160), (50, y + 1), 0)

    # Breast pocket (left side)
    pygame.draw.rect(surface, shirt_shadow, (28, 26, 14, 12))
    pygame.draw.rect(surface, shirt_base, (28, 25, 14, 12))
    pygame.draw.line(surface, shirt_shadow, (28, 25), (42, 25), 1)
    pygame.draw.line(surface, shirt_shadow, (28, 25), (28, 37), 1)
    pygame.draw.line(surface, shirt_shadow, (42, 25), (42, 37), 1)
    # Pocket flap
    pygame.draw.line(surface, shirt_shadow, (29, 27), (41, 27), 1)

    # Sleeves (folded at sides)
    # Left sleeve
    pygame.draw.rect(surface, shirt_shadow, (18, 24, 10, 20))
    pygame.draw.rect(surface, shirt_base, (17, 23, 10, 20))
    # Cuff
    pygame.draw.rect(surface, shirt_light, (17, 41, 10, 4))
    # Cuff button
    pygame.draw.circle(surface, button_color, (22, 43), 1)

    # Right sleeve
    pygame.draw.rect(surface, shirt_shadow, (72, 24, 10, 20))
    pygame.draw.rect(surface, shirt_light, (71, 23, 10, 20))
    # Cuff
    pygame.draw.rect(surface, shirt_light, (71, 41, 10, 4))
    # Cuff button
    pygame.draw.circle(surface, button_color, (76, 43), 1)

    # Stitching details
    pygame.draw.line(surface, shirt_shadow, (24, 22), (24, 56), 1)
    pygame.draw.line(surface, shirt_shadow, (74, 22), (74, 56), 1)

    # Placket stitching
    pygame.draw.line(surface, shirt_shadow, (45, 21), (45, 56), 1)
    pygame.draw.line(surface, shirt_shadow, (53, 21), (53, 56), 1)

    # Crisp fold lines
    pygame.draw.line(surface, shirt_shadow, (32, 28), (34, 50), 1)
    pygame.draw.line(surface, shirt_shadow, (64, 28), (62, 50), 1)

    # Collar stitching
    pygame.draw.line(surface, shirt_shadow, (28, 15), (32, 20), 1)
    pygame.draw.line(surface, shirt_shadow, (70, 15), (66, 20), 1)

    # Subtle sheen/highlight
    pygame.draw.ellipse(surface, (255, 255, 255, 40), (35, 28, 28, 16))

def draw_shoes(surface):
    """Draw enhanced sneakers with detailed design"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (12, 56, 76, 10))

    # Color palette - white sneakers with colored accents
    shoe_white = (240, 240, 250)
    shoe_shadow = (200, 200, 210)
    sole_color = (220, 220, 230)
    accent_color = (100, 150, 255)  # Blue swoosh/accent
    lace_color = (255, 255, 255)

    # Left shoe
    # Sole (bottom layer, rubber)
    pygame.draw.ellipse(surface, (180, 180, 190), (15, 48, 32, 12))
    pygame.draw.ellipse(surface, sole_color, (15, 47, 32, 12))

    # Shoe body
    # Toe box
    pygame.draw.ellipse(surface, shoe_shadow, (16, 36, 30, 18))
    pygame.draw.ellipse(surface, shoe_white, (15, 35, 30, 18))

    # Side panel
    pygame.draw.polygon(surface, shoe_shadow, [(26, 35), (35, 32), (40, 38), (30, 45)])
    pygame.draw.polygon(surface, shoe_white, [(25, 35), (34, 32), (39, 38), (29, 45)])

    # Heel counter
    pygame.draw.ellipse(surface, shoe_shadow, (34, 34, 12, 16))
    pygame.draw.ellipse(surface, shoe_white, (33, 33, 12, 16))

    # Tongue (center, visible)
    pygame.draw.rect(surface, (220, 220, 235), (23, 30, 8, 12), border_radius=2)

    # Laces (crossing pattern)
    lace_positions = [(22, 34), (28, 34), (22, 37), (28, 37), (22, 40), (28, 40)]
    for i in range(0, len(lace_positions) - 1, 2):
        x1, y1 = lace_positions[i]
        x2, y2 = lace_positions[i + 1]
        # Cross laces
        pygame.draw.line(surface, lace_color, (x1, y1), (x2 + 2, y2 + 3), 2)
        pygame.draw.line(surface, lace_color, (x2, y1), (x1 - 2, y2 + 3), 2)

    # Eyelets
    for x, y in lace_positions:
        pygame.draw.circle(surface, (100, 100, 110), (x, y), 2)
        pygame.draw.circle(surface, (60, 60, 70), (x, y), 1)

    # Swoosh/brand accent (Nike-style)
    swoosh = [(20, 42), (28, 40), (34, 42), (30, 43), (24, 44)]
    pygame.draw.lines(surface, accent_color, False, swoosh, 2)

    # Toe cap (rubber reinforcement)
    pygame.draw.arc(surface, (200, 200, 210), (16, 45, 18, 10), 0, 3.14, 2)

    # Right shoe (slightly offset, behind left)
    # Sole
    pygame.draw.ellipse(surface, (180, 180, 190), (53, 48, 32, 12))
    pygame.draw.ellipse(surface, sole_color, (53, 47, 32, 12))

    # Shoe body
    # Toe box
    pygame.draw.ellipse(surface, shoe_shadow, (54, 36, 30, 18))
    pygame.draw.ellipse(surface, shoe_white, (53, 35, 30, 18))

    # Side panel
    pygame.draw.polygon(surface, shoe_shadow, [(64, 35), (73, 32), (78, 38), (68, 45)])
    pygame.draw.polygon(surface, shoe_white, [(63, 35), (72, 32), (77, 38), (67, 45)])

    # Heel counter
    pygame.draw.ellipse(surface, shoe_shadow, (72, 34, 12, 16))
    pygame.draw.ellipse(surface, shoe_white, (71, 33, 12, 16))

    # Tongue
    pygame.draw.rect(surface, (220, 220, 235), (61, 30, 8, 12), border_radius=2)

    # Laces
    lace_positions_r = [(60, 34), (66, 34), (60, 37), (66, 37), (60, 40), (66, 40)]
    for i in range(0, len(lace_positions_r) - 1, 2):
        x1, y1 = lace_positions_r[i]
        x2, y2 = lace_positions_r[i + 1]
        # Cross laces
        pygame.draw.line(surface, lace_color, (x1, y1), (x2 + 2, y2 + 3), 2)
        pygame.draw.line(surface, lace_color, (x2, y1), (x1 - 2, y2 + 3), 2)

    # Eyelets
    for x, y in lace_positions_r:
        pygame.draw.circle(surface, (100, 100, 110), (x, y), 2)
        pygame.draw.circle(surface, (60, 60, 70), (x, y), 1)

    # Swoosh
    swoosh_r = [(58, 42), (66, 40), (72, 42), (68, 43), (62, 44)]
    pygame.draw.lines(surface, accent_color, False, swoosh_r, 2)

    # Toe cap
    pygame.draw.arc(surface, (200, 200, 210), (54, 45, 18, 10), 0, 3.14, 2)

    # Sole treads (texture lines)
    for x in range(17, 44, 4):
        pygame.draw.line(surface, (180, 180, 190), (x, 52), (x + 2, 54), 1)
    for x in range(55, 82, 4):
        pygame.draw.line(surface, (180, 180, 190), (x, 52), (x + 2, 54), 1)

def draw_socks(surface):
    """Draw enhanced socks pack with packaging"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (18, 56, 64, 8))

    # Color palette
    pack_bg = (245, 250, 255)
    pack_border = (200, 210, 230)
    sock_white = (255, 255, 255)
    sock_gray = (220, 220, 230)
    ribbing_color = (200, 200, 210)

    # Main package (clear plastic with cardboard backing)
    pygame.draw.rect(surface, (180, 190, 210), (21, 16, 58, 42), border_radius=4)
    pygame.draw.rect(surface, pack_bg, (20, 15, 58, 42), border_radius=4)
    pygame.draw.rect(surface, pack_border, (20, 15, 58, 42), 2, border_radius=4)

    # Cardboard header
    pygame.draw.rect(surface, (200, 180, 150), (20, 15, 58, 10), border_radius=4)
    pygame.draw.rect(surface, (180, 160, 130), (20, 15, 58, 8))

    # Brand/size label on header
    pygame.draw.rect(surface, (100, 150, 255), (25, 17, 16, 5), border_radius=1)
    pygame.draw.line(surface, (255, 255, 255), (27, 19), (32, 19), 1)
    pygame.draw.line(surface, (255, 255, 255), (34, 19), (39, 19), 1)

    # Size indicator
    pygame.draw.circle(surface, (255, 100, 100), (70, 19), 4)
    pygame.draw.circle(surface, (255, 255, 255), (70, 19), 3)
    pygame.draw.line(surface, (255, 100, 100), (68, 19), (68, 20), 1)
    pygame.draw.line(surface, (255, 100, 100), (72, 19), (72, 20), 1)

    # Three pairs of socks visible (folded/rolled)
    # Bottom pair (most visible)
    # Left sock (rolled)
    pygame.draw.ellipse(surface, sock_gray, (25, 42, 16, 12))
    pygame.draw.ellipse(surface, sock_white, (25, 41, 16, 12))
    # Ribbing lines
    for i in range(4):
        y = 43 + i * 2
        pygame.draw.line(surface, ribbing_color, (26, y), (40, y), 1)
    # Cuff opening (top of roll)
    pygame.draw.ellipse(surface, (230, 230, 240), (28, 41, 10, 6))

    # Right sock (rolled)
    pygame.draw.ellipse(surface, sock_gray, (43, 42, 16, 12))
    pygame.draw.ellipse(surface, sock_white, (43, 41, 16, 12))
    # Ribbing
    for i in range(4):
        y = 43 + i * 2
        pygame.draw.line(surface, ribbing_color, (44, y), (58, y), 1)
    # Cuff opening
    pygame.draw.ellipse(surface, (230, 230, 240), (46, 41, 10, 6))

    # Middle pair (partially visible)
    pygame.draw.ellipse(surface, sock_gray, (30, 33, 14, 10))
    pygame.draw.ellipse(surface, sock_white, (30, 32, 14, 10))
    for i in range(3):
        y = 34 + i * 2
        pygame.draw.line(surface, ribbing_color, (31, y), (43, y), 1)

    pygame.draw.ellipse(surface, sock_gray, (46, 33, 14, 10))
    pygame.draw.ellipse(surface, sock_white, (46, 32, 14, 10))
    for i in range(3):
        y = 34 + i * 2
        pygame.draw.line(surface, ribbing_color, (47, y), (59, y), 1)

    # Top pair (least visible, behind)
    pygame.draw.ellipse(surface, sock_gray, (35, 26, 12, 8))
    pygame.draw.ellipse(surface, sock_white, (35, 25, 12, 8))
    for i in range(2):
        y = 27 + i * 2
        pygame.draw.line(surface, ribbing_color, (36, y), (46, y), 1)

    pygame.draw.ellipse(surface, sock_gray, (48, 26, 12, 8))
    pygame.draw.ellipse(surface, sock_white, (48, 25, 12, 8))
    for i in range(2):
        y = 27 + i * 2
        pygame.draw.line(surface, ribbing_color, (49, y), (59, y), 1)

    # Pack count label ("6-PACK")
    pygame.draw.rect(surface, (50, 200, 100), (22, 50, 26, 6), border_radius=1)
    pygame.draw.line(surface, (255, 255, 255), (24, 52), (28, 52), 1)
    pygame.draw.line(surface, (255, 255, 255), (30, 52), (34, 52), 1)
    pygame.draw.line(surface, (255, 255, 255), (36, 52), (46, 52), 1)

    # Material info
    pygame.draw.rect(surface, (255, 255, 255), (52, 50, 24, 6), border_radius=1)
    pygame.draw.line(surface, (100, 100, 100), (54, 52), (58, 52), 1)
    pygame.draw.line(surface, (100, 100, 100), (60, 52), (74, 52), 1)

    # Plastic wrap shine effect
    for i in range(4):
        y = 22 + i * 9
        pygame.draw.line(surface, (255, 255, 255, 60), (22, y), (30, y - 5), 1)

def draw_photo(surface):
    """Draw enhanced vintage photo frame with aged appearance"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (18, 56, 64, 8))

    # Color palette - vintage/sepia tones
    frame_dark = (100, 70, 40)
    frame_base = (139, 99, 59)
    frame_light = (170, 130, 80)
    photo_bg = (240, 230, 210)  # Aged paper
    sepia_dark = (120, 100, 70)
    sepia_mid = (180, 160, 120)
    sepia_light = (220, 200, 160)

    # Outer frame (ornate wooden frame)
    pygame.draw.rect(surface, frame_dark, (20, 16, 60, 42), border_radius=2)
    pygame.draw.rect(surface, frame_base, (20, 15, 60, 42), border_radius=2)

    # Frame edges with depth
    # Top edge highlight
    pygame.draw.line(surface, frame_light, (21, 16), (78, 16), 2)
    # Left edge highlight
    pygame.draw.line(surface, frame_light, (21, 16), (21, 55), 2)
    # Bottom edge shadow
    pygame.draw.line(surface, frame_dark, (22, 55), (78, 55), 2)
    # Right edge shadow
    pygame.draw.line(surface, frame_dark, (78, 17), (78, 55), 2)

    # Frame corners (decorative)
    corner_positions = [(22, 17), (75, 17), (22, 52), (75, 52)]
    for x, y in corner_positions:
        pygame.draw.rect(surface, frame_light, (x, y, 3, 3))

    # Inner frame border (matting)
    pygame.draw.rect(surface, (180, 170, 150), (26, 20, 48, 34))
    pygame.draw.rect(surface, photo_bg, (28, 22, 44, 30))

    # Photo content (vintage family/person photo in sepia)
    # Background gradient (aged paper)
    for i in range(30):
        shade = 240 - i * 2
        pygame.draw.line(surface, (shade, shade - 10, shade - 30), (28, 22 + i), (72, 22 + i), 1)

    # Silhouette of people (simplified family)
    # Person 1 (left, adult)
    # Head
    pygame.draw.circle(surface, sepia_dark, (38, 30), 4)
    # Body
    pygame.draw.rect(surface, sepia_dark, (35, 34, 6, 10))
    # Arms
    pygame.draw.line(surface, sepia_dark, (35, 36), (32, 40), 2)
    pygame.draw.line(surface, sepia_dark, (41, 36), (44, 40), 2)

    # Person 2 (center, child)
    # Head
    pygame.draw.circle(surface, sepia_mid, (50, 34), 3)
    # Body
    pygame.draw.rect(surface, sepia_mid, (48, 37, 4, 8))
    # Arms
    pygame.draw.line(surface, sepia_mid, (48, 39), (46, 42), 1)
    pygame.draw.line(surface, sepia_mid, (52, 39), (54, 42), 1)

    # Person 3 (right, adult)
    # Head
    pygame.draw.circle(surface, sepia_dark, (62, 30), 4)
    # Body
    pygame.draw.rect(surface, sepia_dark, (59, 34, 6, 10))
    # Arms
    pygame.draw.line(surface, sepia_dark, (59, 36), (56, 40), 2)
    pygame.draw.line(surface, sepia_dark, (65, 36), (68, 40), 2)

    # Ground/floor in photo
    pygame.draw.rect(surface, sepia_light, (28, 45, 44, 7))

    # Aged effects
    # Age spots/foxing (random brown spots on old photos)
    age_spots = [(32, 24), (45, 26), (65, 28), (70, 35), (35, 48), (58, 50)]
    for x, y in age_spots:
        pygame.draw.circle(surface, (160, 130, 90, 80), (x, y), 1)

    # Corner wear/damage
    # Top left worn corner
    pygame.draw.line(surface, (200, 180, 140), (28, 22), (32, 22), 1)
    pygame.draw.line(surface, (200, 180, 140), (28, 22), (28, 26), 1)

    # Bottom right fold/crease
    pygame.draw.line(surface, (180, 160, 120), (60, 48), (70, 52), 1)

    # Frame texture (wood grain)
    for i in range(5):
        y = 20 + i * 8
        pygame.draw.line(surface, (frame_dark[0], frame_dark[1], frame_dark[2], 40), (21, y), (25, y + 3), 1)
        pygame.draw.line(surface, (frame_dark[0], frame_dark[1], frame_dark[2], 40), (75, y), (79, y + 3), 1)

    # Photo edge wear (border fading)
    pygame.draw.rect(surface, (220, 210, 190, 60), (28, 22, 44, 30), 1)

    # Vintage vignette effect (darker edges)
    vignette_points = [(28, 22), (72, 22), (72, 52), (28, 52)]
    for i, (x, y) in enumerate(vignette_points):
        pygame.draw.circle(surface, (100, 90, 70, 40), (x, y), 8)

def draw_belt(surface):
    """Draw enhanced leather belt with detailed buckle"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (12, 42, 76, 8))

    # Color palette - brown leather
    leather_base = (100, 70, 40)
    leather_dark = (70, 50, 25)
    leather_light = (130, 95, 55)
    buckle_metal = (180, 180, 190)
    buckle_dark = (120, 120, 130)

    # Belt strap (rolled/coiled view)
    # Main strap body
    pygame.draw.rect(surface, leather_dark, (16, 26, 68, 14), border_radius=3)
    pygame.draw.rect(surface, leather_base, (15, 25, 68, 14), border_radius=3)

    # Leather texture/grain
    for i in range(8):
        x = 18 + i * 8
        pygame.draw.line(surface, (leather_dark[0], leather_dark[1], leather_dark[2], 60), (x, 27), (x + 4, 28), 1)
        pygame.draw.line(surface, (leather_light[0], leather_light[1], leather_light[2], 40), (x + 1, 36), (x + 5, 37), 1)

    # Belt holes along strap
    hole_positions = [28, 38, 48, 58, 68, 78]
    for x in hole_positions:
        # Hole
        pygame.draw.circle(surface, (40, 30, 15), (x, 32), 2)
        pygame.draw.circle(surface, (20, 15, 5), (x, 32), 1)
        # Wear around hole (lighter leather from use)
        pygame.draw.circle(surface, (leather_light[0], leather_light[1], leather_light[2], 80), (x, 32), 3, 1)

    # Stitching along edges
    # Top stitching
    for x in range(18, 80, 4):
        pygame.draw.circle(surface, (120, 90, 50), (x, 27), 1)
    # Bottom stitching
    for x in range(18, 80, 4):
        pygame.draw.circle(surface, (120, 90, 50), (x, 37), 1)

    # Belt keeper (small loop that holds excess strap)
    pygame.draw.rect(surface, leather_dark, (45, 23, 6, 18))
    pygame.draw.rect(surface, leather_base, (45, 22, 6, 18))
    pygame.draw.line(surface, leather_light, (46, 23), (46, 38), 1)

    # Buckle (metallic, at left end)
    # Buckle frame (rectangular with rounded edges)
    pygame.draw.rect(surface, buckle_dark, (13, 24, 18, 16), border_radius=2)
    pygame.draw.rect(surface, buckle_metal, (12, 23, 18, 16), border_radius=2)

    # Buckle inner opening (where strap goes through)
    pygame.draw.rect(surface, (40, 40, 45), (14, 26, 14, 10), border_radius=1)

    # Buckle prong (metal pin)
    prong_points = [
        (21, 32),   # Base on buckle
        (28, 32),   # Point (goes through hole)
        (27, 31),   # Top of point
        (21, 30)    # Top of base
    ]
    pygame.draw.polygon(surface, buckle_dark, prong_points)
    pygame.draw.polygon(surface, buckle_metal, [(x, y-1) for x, y in prong_points])
    # Prong tip
    pygame.draw.line(surface, (220, 220, 230), (27, 32), (29, 32), 2)

    # Buckle decorative details
    # Rivets on buckle
    rivet_positions = [(14, 26), (26, 26), (14, 37), (26, 37)]
    for x, y in rivet_positions:
        pygame.draw.circle(surface, (150, 150, 160), (x, y), 2)
        pygame.draw.circle(surface, (200, 200, 210), (x, y), 1)

    # Buckle frame detail (crossbar)
    pygame.draw.rect(surface, (150, 150, 160), (12, 30, 18, 2))

    # Belt tip (pointed end, on right)
    tip_points = [
        (83, 25),   # Top
        (90, 29),   # Point tip
        (88, 32),   # Bottom point
        (83, 39)    # Bottom
    ]
    pygame.draw.polygon(surface, leather_dark, [(x+1, y) for x, y in tip_points])
    pygame.draw.polygon(surface, leather_base, tip_points)
    pygame.draw.line(surface, leather_light, (84, 27), (87, 30), 1)

    # Stitching on tip
    pygame.draw.line(surface, (120, 90, 50), (84, 28), (86, 32), 1)
    pygame.draw.line(surface, (120, 90, 50), (84, 36), (86, 32), 1)

    # Wear marks (scuff marks from use)
    wear_areas = [(35, 28), (50, 30), (65, 35)]
    for x, y in wear_areas:
        pygame.draw.line(surface, (leather_light[0], leather_light[1], leather_light[2], 100), (x, y), (x + 6, y), 1)

    # Buckle shine/reflection
    pygame.draw.line(surface, (220, 220, 230), (13, 24), (28, 24), 1)
    pygame.draw.circle(surface, (240, 240, 250), (15, 27), 1)

def draw_coat(surface):
    """Draw enhanced winter coat with quilted pattern and fur trim"""
    # Shadow
    pygame.draw.ellipse(surface, (0, 0, 0, 30), (10, 58, 80, 8))

    # Color palette - dark navy winter coat
    coat_base = (40, 50, 80)
    coat_dark = (25, 35, 60)
    coat_light = (55, 65, 100)
    fur_color = (220, 220, 230)
    fur_shadow = (180, 180, 190)
    zipper_metal = (180, 180, 190)

    # Main body (puffy, insulated)
    pygame.draw.rect(surface, coat_dark, (21, 18, 58, 40), border_radius=6)
    pygame.draw.rect(surface, coat_base, (20, 17, 58, 40), border_radius=6)

    # Quilted/puffy pattern (horizontal sections)
    quilt_sections = [22, 28, 34, 40, 46, 52]
    for y in quilt_sections:
        # Quilting seam (horizontal line)
        pygame.draw.line(surface, coat_dark, (21, y), (77, y), 1)
        # Puffy effect (highlight above seam)
        pygame.draw.line(surface, coat_light, (22, y - 2), (76, y - 2), 1)

    # Vertical quilt sections (creates rectangular puffy pattern)
    quilt_vertical = [35, 49, 63]
    for x in quilt_vertical:
        pygame.draw.line(surface, coat_dark, (x, 18), (x, 56), 1)

    # Sleeves (puffy with quilting)
    # Left sleeve
    pygame.draw.rect(surface, coat_dark, (13, 20, 14, 28), border_radius=3)
    pygame.draw.rect(surface, coat_base, (12, 19, 14, 28), border_radius=3)
    # Sleeve quilting
    for y in [24, 30, 36, 42]:
        pygame.draw.line(surface, coat_dark, (13, y), (25, y), 1)
        pygame.draw.line(surface, coat_light, (14, y - 2), (24, y - 2), 1)

    # Right sleeve
    pygame.draw.rect(surface, coat_dark, (73, 20, 14, 28), border_radius=3)
    pygame.draw.rect(surface, coat_light, (72, 19, 14, 28), border_radius=3)
    # Sleeve quilting
    for y in [24, 30, 36, 42]:
        pygame.draw.line(surface, coat_dark, (73, y), (85, y), 1)
        pygame.draw.line(surface, (coat_light[0] + 10, coat_light[1] + 10, coat_light[2] + 10), (74, y - 2), (84, y - 2), 1)

    # Sleeve cuffs (ribbed/elastic)
    pygame.draw.rect(surface, (30, 35, 55), (12, 45, 14, 4))
    pygame.draw.rect(surface, (30, 35, 55), (72, 45, 14, 4))

    # Fur/fleece collar (thick, fluffy)
    # Outer fur layer (fluffy texture)
    for i in range(15):
        x = 22 + i * 4
        y = 12 + (i % 3)
        pygame.draw.circle(surface, fur_shadow, (x, y), 3)
        pygame.draw.circle(surface, fur_color, (x, y - 1), 3)

    # Fur hood trim
    pygame.draw.ellipse(surface, fur_shadow, (25, 10, 50, 12))
    pygame.draw.ellipse(surface, fur_color, (25, 9, 50, 12))

    # Fur texture (individual strands)
    for i in range(20):
        x = 27 + i * 2
        pygame.draw.line(surface, (240, 240, 250), (x, 11), (x, 14), 1)

    # Hood (visible at top)
    hood_points = [
        (30, 17),
        (25, 10),
        (49, 8),
        (73, 10),
        (68, 17)
    ]
    pygame.draw.polygon(surface, coat_dark, hood_points)
    pygame.draw.polygon(surface, coat_base, [(x, y - 1) for x, y in hood_points])

    # Zipper (center, heavy duty)
    # Zipper track
    pygame.draw.line(surface, (100, 100, 110), (49, 17), (49, 56), 4)
    pygame.draw.line(surface, zipper_metal, (49, 17), (49, 56), 3)

    # Zipper teeth (individual)
    for y in range(18, 55, 3):
        # Left teeth
        pygame.draw.line(surface, (140, 140, 150), (47, y), (48, y + 1), 2)
        # Right teeth
        pygame.draw.line(surface, (140, 140, 150), (51, y), (50, y + 1), 2)

    # Zipper pull (large, easy to grab with gloves)
    pygame.draw.rect(surface, (200, 200, 210), (47, 22, 5, 10), border_radius=1)
    pygame.draw.circle(surface, (180, 180, 190), (49, 27), 4)
    pygame.draw.circle(surface, zipper_metal, (49, 27), 3)
    # Pull tab ring
    pygame.draw.circle(surface, (160, 160, 170), (49, 32), 3, 1)

    # Pockets (large, with flaps and zippers)
    # Left pocket
    pygame.draw.rect(surface, coat_dark, (24, 38, 18, 12))
    pygame.draw.rect(surface, coat_base, (24, 37, 18, 12))
    pygame.draw.line(surface, coat_dark, (25, 48), (41, 48), 2)
    # Pocket zipper
    pygame.draw.line(surface, zipper_metal, (26, 41), (40, 41), 1)

    # Right pocket
    pygame.draw.rect(surface, coat_dark, (56, 38, 18, 12))
    pygame.draw.rect(surface, coat_light, (56, 37, 18, 12))
    pygame.draw.line(surface, coat_dark, (57, 48), (73, 48), 2)
    # Pocket zipper
    pygame.draw.line(surface, zipper_metal, (58, 41), (72, 41), 1)

    # Buttons/snaps (additional closure under zipper)
    snap_positions = [(46, 25), (52, 25), (46, 35), (52, 35), (46, 45), (52, 45)]
    for x, y in snap_positions:
        pygame.draw.circle(surface, (60, 60, 70), (x, y), 2)
        pygame.draw.circle(surface, (80, 80, 90), (x, y), 1)

    # Velcro storm flap (overlaps zipper)
    # Left flap
    pygame.draw.rect(surface, coat_dark, (20, 20, 7, 34))
    pygame.draw.rect(surface, coat_base, (20, 19, 7, 34))

    # Right flap
    pygame.draw.rect(surface, coat_dark, (71, 20, 7, 34))
    pygame.draw.rect(surface, coat_light, (71, 19, 7, 34))

    # Elastic drawstring at waist
    pygame.draw.line(surface, (100, 100, 110), (22, 44), (76, 44), 2)
    # Drawstring ends
    pygame.draw.circle(surface, (120, 120, 130), (35, 44), 2)
    pygame.draw.circle(surface, (120, 120, 130), (63, 44), 2)

    # Brand patch/logo (on sleeve)
    pygame.draw.rect(surface, (180, 50, 50), (14, 22, 8, 6), border_radius=1)
    pygame.draw.line(surface, (255, 255, 255), (16, 24), (20, 24), 1)

    # Reflective strip (safety feature)
    pygame.draw.rect(surface, (200, 200, 50, 120), (22, 54, 54, 2))

    # Hem (bottom edge, ribbed)
    pygame.draw.rect(surface, (30, 35, 55), (20, 54, 58, 4))

def draw_nightlamp(surface):
    """Draw nightlamp icon with detailed graphics"""
    # Shadow under base
    pygame.draw.ellipse(surface, (0, 0, 0, 40), (20, 58, 60, 10))

    # Lamp base (wider, rounded, bronze/brown)
    base_color = (120, 100, 80)
    base_shadow = (80, 65, 50)
    base_highlight = (160, 135, 105)

    # Base platform (wide bottom)
    pygame.draw.ellipse(surface, base_shadow, (25, 52, 50, 12))
    pygame.draw.ellipse(surface, base_color, (25, 50, 50, 12))
    pygame.draw.ellipse(surface, base_highlight, (30, 50, 40, 6))

    # Base body (rounded column)
    pygame.draw.rect(surface, base_shadow, (40, 40, 20, 15))
    pygame.draw.rect(surface, base_color, (38, 38, 24, 15))
    pygame.draw.line(surface, base_highlight, (39, 40), (39, 50), 2)

    # Lamp stand/neck (thin column)
    stand_color = (140, 120, 95)
    pygame.draw.rect(surface, base_shadow, (47, 25, 6, 18))
    pygame.draw.rect(surface, stand_color, (46, 24, 6, 18))
    pygame.draw.line(surface, base_highlight, (46, 26), (46, 40), 1)

    # Top of stand (connector)
    pygame.draw.ellipse(surface, base_color, (43, 22, 14, 8))

    # Lampshade (cone shape, cream/beige)
    shade_color = (255, 240, 200)
    shade_shadow = (220, 200, 160)
    shade_glow = (255, 250, 220)

    # Shade body (trapezoid using polygon)
    shade_points = [
        (45, 23),  # Top left
        (55, 23),  # Top right
        (65, 38),  # Bottom right
        (35, 38)   # Bottom left
    ]
    pygame.draw.polygon(surface, shade_shadow, shade_points)

    # Lighter front face
    front_points = [
        (46, 24),
        (54, 24),
        (62, 37),
        (38, 37)
    ]
    pygame.draw.polygon(surface, shade_color, front_points)

    # Shade rim (bottom edge)
    pygame.draw.ellipse(surface, shade_shadow, (35, 36, 30, 6))
    pygame.draw.ellipse(surface, shade_color, (36, 36, 28, 5))

    # Shade top opening
    pygame.draw.ellipse(surface, (200, 180, 140), (44, 22, 12, 5))

    # Glow effect (warm yellow light emanating)
    glow_color = (255, 230, 150, 80)
    glow_outer = (255, 240, 180, 40)

    # Multiple layers for glow gradient
    for i in range(3):
        alpha = 60 - (i * 20)
        radius = 18 + (i * 4)
        glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*glow_color[:3], alpha), (radius, radius), radius)
        surface.blit(glow_surface, (50 - radius, 30 - radius))

    # Light coming from bottom of shade
    light_triangle = [
        (45, 38),
        (55, 38),
        (50, 48)
    ]
    light_surface = pygame.Surface((100, 70), pygame.SRCALPHA)
    pygame.draw.polygon(light_surface, (255, 245, 200, 60), light_triangle)
    surface.blit(light_surface, (0, 0))

    # Power cord (small detail)
    cord_color = (40, 40, 40)
    # Cord coming from base
    pygame.draw.line(surface, cord_color, (28, 55), (18, 58), 2)
    pygame.draw.line(surface, cord_color, (18, 58), (15, 62), 2)

    # On/off switch on base
    pygame.draw.rect(surface, (60, 60, 60), (41, 48, 4, 3))
    pygame.draw.rect(surface, (100, 100, 100), (41, 48, 2, 3))

    # Highlight on shade (light reflection)
    pygame.draw.line(surface, shade_glow, (48, 26), (50, 32), 2)
    pygame.draw.line(surface, shade_glow, (50, 26), (52, 30), 1)


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
"""
Generate custom grocery store sprites in retro pixel art style
Creates a 256x256 PNG sprite sheet (16x16 grid of 16px tiles)
"""
from PIL import Image, ImageDraw
import os

# Sprite sheet dimensions
TILE_SIZE = 16
GRID_SIZE = 16
SHEET_SIZE = TILE_SIZE * GRID_SIZE  # 256x256

# Retro color palette (saturated, limited colors)
COLORS = {
    # Produce colors
    'red': (220, 20, 20),
    'dark_red': (150, 10, 10),
    'light_red': (255, 100, 100),
    'green': (50, 200, 50),
    'dark_green': (30, 120, 30),
    'light_green': (150, 255, 150),
    'orange': (255, 140, 0),
    'dark_orange': (200, 100, 0),
    'yellow': (255, 220, 0),
    'dark_yellow': (200, 170, 0),
    'purple': (160, 50, 200),
    'dark_purple': (100, 30, 130),

    # Store fixture colors
    'brown': (139, 90, 43),
    'dark_brown': (90, 60, 30),
    'light_brown': (180, 130, 80),
    'gray': (150, 150, 150),
    'dark_gray': (80, 80, 80),
    'light_gray': (200, 200, 200),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'blue': (70, 130, 220),
    'light_blue': (150, 200, 255),
    'cyan': (100, 200, 220),
}

def create_tile():
    """Create a blank 16x16 tile with transparency"""
    return Image.new('RGBA', (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))

def draw_pixel_circle(draw, cx, cy, radius, fill_color, outline_color=None):
    """Draw a pixel-perfect circle (no anti-aliasing)"""
    # Draw filled circle
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx)**2 + (y - cy)**2 <= radius**2:
                draw.point((x, y), fill=fill_color)

    # Draw outline if specified
    if outline_color:
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                dist_sq = (x - cx)**2 + (y - cy)**2
                if radius**2 - radius < dist_sq <= radius**2:
                    draw.point((x, y), fill=outline_color)

def draw_shading(draw, x, y, w, h, dark_color, direction='bottom-right'):
    """Add retro-style shading to a region"""
    if direction == 'bottom-right':
        # Shading on bottom and right
        draw.rectangle([x + w//2, y + h//2, x + w - 1, y + h - 1], fill=dark_color)
    elif direction == 'bottom':
        # Shading on bottom only
        draw.rectangle([x, y + h//2, x + w - 1, y + h - 1], fill=dark_color)

# ============ PRODUCE TILES (Row 0-1) ============

def tile_red_apple(tile_pos):
    """Red apple with stem and leaf"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Apple body (offset circle)
    draw_pixel_circle(draw, 8, 9, 5, COLORS['red'])
    # Dark shading
    draw.ellipse([9, 10, 13, 14], fill=COLORS['dark_red'])
    # Highlight
    draw.rectangle([6, 6, 7, 7], fill=COLORS['light_red'])
    # Stem
    draw.rectangle([7, 3, 8, 5], fill=COLORS['dark_brown'])
    # Leaf
    draw.polygon([(9, 4), (11, 4), (10, 6)], fill=COLORS['green'])

    return img

def tile_orange(tile_pos):
    """Orange fruit"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Orange body
    draw_pixel_circle(draw, 8, 8, 5, COLORS['orange'])
    # Dark shading
    draw.ellipse([9, 9, 13, 13], fill=COLORS['dark_orange'])
    # Highlight
    draw.rectangle([5, 5, 6, 6], fill=COLORS['yellow'])
    # Stem dot
    draw.rectangle([7, 3, 8, 4], fill=COLORS['dark_green'])

    return img

def tile_banana(tile_pos):
    """Banana"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Banana curve (approximate with rectangles)
    draw.rectangle([5, 6, 12, 9], fill=COLORS['yellow'])
    draw.rectangle([4, 8, 6, 10], fill=COLORS['yellow'])
    draw.rectangle([11, 7, 13, 9], fill=COLORS['yellow'])
    # Shading
    draw.line([(5, 9), (12, 9)], fill=COLORS['dark_yellow'], width=1)
    # Brown tips
    draw.point((4, 9), fill=COLORS['dark_brown'])
    draw.point((12, 7), fill=COLORS['dark_brown'])

    return img

def tile_lettuce(tile_pos):
    """Lettuce head"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Lettuce layers (wavy circles)
    draw_pixel_circle(draw, 8, 9, 6, COLORS['light_green'])
    draw_pixel_circle(draw, 7, 8, 4, COLORS['green'])
    draw_pixel_circle(draw, 9, 8, 3, COLORS['green'])
    # Dark shading
    for i in range(3):
        draw.point((6 + i, 12), fill=COLORS['dark_green'])
        draw.point((9 + i, 11), fill=COLORS['dark_green'])

    return img

def tile_tomato(tile_pos):
    """Tomato"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Tomato body
    draw_pixel_circle(draw, 8, 9, 5, COLORS['red'])
    # Highlight
    draw.rectangle([6, 6, 7, 7], fill=COLORS['light_red'])
    # Green stem/leaves
    draw.rectangle([7, 4, 9, 6], fill=COLORS['dark_green'])
    draw.line([(6, 5), (10, 5)], fill=COLORS['green'], width=1)

    return img

def tile_carrot(tile_pos):
    """Carrot"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Carrot body (tapered)
    draw.polygon([(8, 6), (6, 8), (7, 13), (9, 13), (10, 8)], fill=COLORS['orange'])
    # Shading lines
    draw.line([(8, 7), (8, 12)], fill=COLORS['dark_orange'], width=1)
    # Green top
    draw.line([(7, 4), (8, 6)], fill=COLORS['green'], width=2)
    draw.line([(9, 4), (8, 6)], fill=COLORS['green'], width=2)

    return img

def tile_broccoli(tile_pos):
    """Broccoli"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Broccoli florets (bumpy top)
    for x in [6, 8, 10]:
        for y in [5, 7]:
            draw_pixel_circle(draw, x, y, 2, COLORS['dark_green'])
    # Stem
    draw.rectangle([7, 9, 9, 13], fill=COLORS['light_green'])
    draw.line([(7, 10), (9, 10)], fill=COLORS['green'], width=1)

    return img

def tile_corn(tile_pos):
    """Corn on the cob"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Corn body
    draw.rectangle([6, 5, 10, 12], fill=COLORS['yellow'])
    # Kernel pattern
    for y in range(6, 12, 2):
        for x in range(7, 10):
            draw.point((x, y), fill=COLORS['dark_yellow'])
    # Husk
    draw.polygon([(5, 5), (6, 4), (7, 5)], fill=COLORS['light_green'])
    draw.polygon([(11, 5), (10, 4), (9, 5)], fill=COLORS['light_green'])

    return img

# ============ SHELVING UNITS (Row 2-3) ============

def tile_shelf_left(tile_pos):
    """Left end of shelf"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Vertical support
    draw.rectangle([2, 0, 4, 15], fill=COLORS['dark_brown'])
    # Shelves (3 levels)
    for y in [3, 8, 13]:
        draw.rectangle([2, y, 15, y + 1], fill=COLORS['brown'])
        draw.line([(2, y + 2), (15, y + 2)], fill=COLORS['dark_brown'], width=1)

    return img

def tile_shelf_middle(tile_pos):
    """Middle section of shelf"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Shelves (3 levels)
    for y in [3, 8, 13]:
        draw.rectangle([0, y, 15, y + 1], fill=COLORS['brown'])
        draw.line([(0, y + 2), (15, y + 2)], fill=COLORS['dark_brown'], width=1)
    # Add some items on shelves (colored boxes)
    draw.rectangle([2, 5, 4, 7], fill=COLORS['red'])
    draw.rectangle([6, 5, 8, 7], fill=COLORS['blue'])
    draw.rectangle([10, 5, 12, 7], fill=COLORS['green'])

    return img

def tile_shelf_right(tile_pos):
    """Right end of shelf"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Shelves (3 levels)
    for y in [3, 8, 13]:
        draw.rectangle([0, y, 13, y + 1], fill=COLORS['brown'])
        draw.line([(0, y + 2), (13, y + 2)], fill=COLORS['dark_brown'], width=1)
    # Vertical support
    draw.rectangle([11, 0, 13, 15], fill=COLORS['dark_brown'])

    return img

def tile_shelf_tall(tile_pos):
    """Tall single column shelf"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Frame
    draw.rectangle([4, 0, 11, 15], fill=COLORS['brown'], outline=COLORS['dark_brown'])
    # Shelves (5 levels)
    for y in [2, 5, 8, 11, 14]:
        draw.line([(5, y), (10, y)], fill=COLORS['dark_brown'], width=1)
    # Items
    draw.rectangle([6, 3, 9, 4], fill=COLORS['orange'])
    draw.rectangle([6, 9, 9, 10], fill=COLORS['purple'])

    return img

# ============ REFRIGERATION (Row 4-5) ============

def tile_fridge_closed(tile_pos):
    """Closed refrigerator"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Fridge body
    draw.rectangle([3, 1, 12, 14], fill=COLORS['white'], outline=COLORS['gray'])
    # Door line
    draw.line([(3, 7), (12, 7)], fill=COLORS['gray'], width=1)
    # Handles
    draw.rectangle([10, 4, 11, 6], fill=COLORS['dark_gray'])
    draw.rectangle([10, 9, 11, 11], fill=COLORS['dark_gray'])
    # Highlight
    draw.line([(4, 2), (4, 13)], fill=COLORS['light_gray'], width=1)

    return img

def tile_fridge_glass(tile_pos):
    """Glass door fridge"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Fridge frame
    draw.rectangle([3, 1, 12, 14], fill=COLORS['light_gray'], outline=COLORS['gray'])
    # Glass (semi-transparent effect with cyan)
    draw.rectangle([4, 2, 11, 13], fill=COLORS['cyan'])
    # Items visible inside
    draw.rectangle([6, 4, 8, 6], fill=COLORS['orange'])
    draw.rectangle([6, 8, 8, 10], fill=COLORS['green'])
    # Handle
    draw.rectangle([10, 7, 11, 9], fill=COLORS['dark_gray'])

    return img

def tile_freezer(tile_pos):
    """Ice cream freezer (horizontal)"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Freezer body
    draw.rectangle([1, 5, 14, 14], fill=COLORS['white'], outline=COLORS['gray'])
    # Glass top (light blue for frozen)
    draw.rectangle([2, 6, 13, 9], fill=COLORS['light_blue'])
    # Handle/edge
    draw.line([(2, 9), (13, 9)], fill=COLORS['dark_gray'], width=2)
    # Ice cream containers inside
    draw.rectangle([4, 10, 6, 12], fill=COLORS['purple'])
    draw.rectangle([8, 10, 10, 12], fill=COLORS['yellow'])

    return img

# ============ CHECKOUT AREA (Row 6) ============

def tile_checkout_counter_left(tile_pos):
    """Left end of checkout counter"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Counter surface
    draw.rectangle([0, 6, 15, 11], fill=COLORS['gray'], outline=COLORS['dark_gray'])
    # Front panel
    draw.rectangle([0, 12, 15, 15], fill=COLORS['dark_gray'])
    # Shading
    draw.line([(0, 7), (15, 7)], fill=COLORS['light_gray'], width=1)

    return img

def tile_checkout_counter_middle(tile_pos):
    """Middle section of checkout counter"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Conveyor belt effect (alternating stripes)
    for x in range(0, 16, 3):
        draw.rectangle([x, 6, x + 1, 11], fill=COLORS['black'])
        draw.rectangle([x + 2, 6, x + 3, 11], fill=COLORS['dark_gray'])
    # Front panel
    draw.rectangle([0, 12, 15, 15], fill=COLORS['dark_gray'])

    return img

def tile_cash_register(tile_pos):
    """Cash register"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Counter base
    draw.rectangle([0, 10, 15, 15], fill=COLORS['gray'])
    # Register body
    draw.rectangle([4, 5, 11, 10], fill=COLORS['dark_gray'], outline=COLORS['black'])
    # Screen
    draw.rectangle([5, 6, 10, 8], fill=COLORS['light_blue'])
    # Number pad (dots)
    for y in [11, 13]:
        for x in [6, 8, 10]:
            draw.point((x, y), fill=COLORS['white'])

    return img

def tile_bagging_area(tile_pos):
    """Bagging area with bag"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Counter
    draw.rectangle([0, 8, 15, 15], fill=COLORS['gray'])
    # Bag (simple rectangle with handles)
    draw.rectangle([5, 4, 11, 10], fill=COLORS['brown'], outline=COLORS['dark_brown'])
    # Handles
    draw.line([(6, 4), (6, 2)], fill=COLORS['brown'], width=2)
    draw.line([(10, 4), (10, 2)], fill=COLORS['brown'], width=2)

    return img

# ============ PACKAGED GOODS (Row 7) ============

def tile_cereal_box_red(tile_pos):
    """Red cereal box"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Box
    draw.rectangle([5, 3, 10, 13], fill=COLORS['red'], outline=COLORS['dark_red'])
    # Label area
    draw.rectangle([6, 5, 9, 7], fill=COLORS['white'])
    # Text lines (dots)
    for y in [6, 8, 10]:
        draw.line([(6, y), (9, y)], fill=COLORS['white'], width=1)

    return img

def tile_cereal_box_blue(tile_pos):
    """Blue cereal box"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Box
    draw.rectangle([5, 3, 10, 13], fill=COLORS['blue'], outline=COLORS['dark_gray'])
    # Label area
    draw.rectangle([6, 5, 9, 7], fill=COLORS['yellow'])
    # Text lines
    for y in [6, 8, 10]:
        draw.line([(6, y), (9, y)], fill=COLORS['white'], width=1)

    return img

def tile_canned_good(tile_pos):
    """Canned food"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Can body (cylinder)
    draw.rectangle([5, 6, 10, 13], fill=COLORS['light_gray'], outline=COLORS['gray'])
    # Top (ellipse)
    draw.ellipse([5, 5, 10, 8], fill=COLORS['gray'])
    # Label
    draw.rectangle([6, 8, 9, 11], fill=COLORS['red'])
    # Shine
    draw.line([(6, 7), (6, 12)], fill=COLORS['white'], width=1)

    return img

def tile_bottle(tile_pos):
    """Bottle (soda/juice)"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Bottle body
    draw.rectangle([6, 6, 9, 13], fill=COLORS['green'], outline=COLORS['dark_green'])
    # Cap
    draw.rectangle([6, 4, 9, 6], fill=COLORS['dark_red'])
    # Liquid level
    draw.rectangle([7, 8, 8, 12], fill=COLORS['light_green'])
    # Highlight
    draw.line([(7, 7), (7, 12)], fill=COLORS['light_green'], width=1)

    return img

# ============ STORE FIXTURES (Row 8) ============

def tile_shopping_cart(tile_pos):
    """Shopping cart"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Cart basket
    draw.rectangle([4, 4, 12, 10], fill=COLORS['gray'], outline=COLORS['dark_gray'])
    # Handle
    draw.line([(3, 4), (3, 8)], fill=COLORS['dark_gray'], width=2)
    # Wheels
    draw_pixel_circle(draw, 6, 13, 2, COLORS['black'])
    draw_pixel_circle(draw, 10, 13, 2, COLORS['black'])
    # Mesh pattern
    for y in range(5, 10, 2):
        draw.line([(5, y), (11, y)], fill=COLORS['dark_gray'], width=1)

    return img

def tile_basket(tile_pos):
    """Shopping basket"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Basket body
    draw.rectangle([4, 7, 11, 13], fill=COLORS['orange'], outline=COLORS['dark_orange'])
    # Handle
    draw.arc([5, 3, 10, 10], start=0, end=180, fill=COLORS['dark_orange'], width=2)
    # Weave pattern
    for y in range(8, 13, 2):
        for x in range(5, 11, 2):
            draw.point((x, y), fill=COLORS['dark_orange'])

    return img

def tile_sign_aisle(tile_pos):
    """Aisle number sign"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Sign board
    draw.rectangle([3, 4, 12, 11], fill=COLORS['white'], outline=COLORS['black'])
    # Number "1" (simple)
    draw.rectangle([7, 6, 8, 9], fill=COLORS['black'])

    return img

def tile_price_tag(tile_pos):
    """Price tag"""
    img = create_tile()
    draw = ImageDraw.Draw(img)

    # Tag shape
    draw.polygon([(4, 6), (12, 6), (13, 8), (12, 10), (4, 10)], fill=COLORS['yellow'], outline=COLORS['dark_yellow'])
    # Price lines (representing $)
    draw.line([(5, 7), (7, 7)], fill=COLORS['black'], width=1)
    draw.line([(5, 9), (7, 9)], fill=COLORS['black'], width=1)
    # Hole
    draw_pixel_circle(draw, 11, 8, 1, COLORS['white'])

    return img

# ============ SPRITE SHEET GENERATION ============

def generate_sprite_sheet():
    """Generate the complete sprite sheet"""
    # Create blank sheet
    sheet = Image.new('RGBA', (SHEET_SIZE, SHEET_SIZE), (0, 0, 0, 0))

    # Define sprite layout (function, x, y position in grid)
    sprite_layout = [
        # Row 0: Produce
        (tile_red_apple, 0, 0),
        (tile_orange, 1, 0),
        (tile_banana, 2, 0),
        (tile_lettuce, 3, 0),
        (tile_tomato, 4, 0),
        (tile_carrot, 5, 0),
        (tile_broccoli, 6, 0),
        (tile_corn, 7, 0),

        # Row 2: Shelving
        (tile_shelf_left, 0, 2),
        (tile_shelf_middle, 1, 2),
        (tile_shelf_right, 2, 2),
        (tile_shelf_tall, 3, 2),

        # Row 4: Refrigeration
        (tile_fridge_closed, 0, 4),
        (tile_fridge_glass, 1, 4),
        (tile_freezer, 2, 4),

        # Row 6: Checkout
        (tile_checkout_counter_left, 0, 6),
        (tile_checkout_counter_middle, 1, 6),
        (tile_cash_register, 2, 6),
        (tile_bagging_area, 3, 6),

        # Row 7: Packaged goods
        (tile_cereal_box_red, 0, 7),
        (tile_cereal_box_blue, 1, 7),
        (tile_canned_good, 2, 7),
        (tile_bottle, 3, 7),

        # Row 8: Store fixtures
        (tile_shopping_cart, 0, 8),
        (tile_basket, 1, 8),
        (tile_sign_aisle, 2, 8),
        (tile_price_tag, 3, 8),
    ]

    # Generate and place each tile
    for tile_func, grid_x, grid_y in sprite_layout:
        tile = tile_func((grid_x, grid_y))
        pixel_x = grid_x * TILE_SIZE
        pixel_y = grid_y * TILE_SIZE
        sheet.paste(tile, (pixel_x, pixel_y))
        print(f"Generated: {tile_func.__name__} at ({grid_x}, {grid_y})")

    return sheet

if __name__ == "__main__":
    print("Generating custom grocery store sprite sheet...")
    print(f"Sheet size: {SHEET_SIZE}x{SHEET_SIZE} pixels")
    print(f"Tile size: {TILE_SIZE}x{TILE_SIZE} pixels")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE} tiles")
    print()

    sprite_sheet = generate_sprite_sheet()

    # Save to assets directory
    output_path = "/Users/saaraskodali/SaarasPraveenAlexEcon/assets/grocery_custom_16x16.png"
    sprite_sheet.save(output_path)

    print()
    print(f"✅ Sprite sheet saved to: {output_path}")
    print()
    print("Tile Reference Guide:")
    print("=" * 50)
    print("Row 0: Produce")
    print("  (0,0) Red Apple    (1,0) Orange      (2,0) Banana")
    print("  (3,0) Lettuce      (4,0) Tomato      (5,0) Carrot")
    print("  (6,0) Broccoli     (7,0) Corn")
    print()
    print("Row 2: Shelving")
    print("  (0,2) Shelf Left   (1,2) Shelf Middle  (2,2) Shelf Right")
    print("  (3,2) Tall Shelf")
    print()
    print("Row 4: Refrigeration")
    print("  (0,4) Fridge Closed  (1,4) Glass Fridge  (2,4) Freezer")
    print()
    print("Row 6: Checkout")
    print("  (0,6) Counter Left  (1,6) Counter Middle")
    print("  (2,6) Cash Register (3,6) Bagging Area")
    print()
    print("Row 7: Packaged Goods")
    print("  (0,7) Red Cereal   (1,7) Blue Cereal")
    print("  (2,7) Canned Good  (3,7) Bottle")
    print()
    print("Row 8: Store Fixtures")
    print("  (0,8) Shopping Cart  (1,8) Basket")
    print("  (2,8) Aisle Sign     (3,8) Price Tag")

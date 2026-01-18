"""
Isometric Utility Module

Provides coordinate conversion functions and rendering utilities
for isometric exterior view rendering.
"""

# Isometric tile dimensions (standard 2:1 ratio diamond)
ISO_TILE_WIDTH = 128
ISO_TILE_HEIGHT = 64

# Half-tile dimensions for calculations
ISO_TILE_HALF_WIDTH = ISO_TILE_WIDTH // 2
ISO_TILE_HALF_HEIGHT = ISO_TILE_HEIGHT // 2


def cart_to_iso(cart_x, cart_y):
    """
    Convert Cartesian (grid) coordinates to isometric screen coordinates.

    Args:
        cart_x: Grid x position (column)
        cart_y: Grid y position (row)

    Returns:
        tuple: (iso_x, iso_y) screen coordinates for the tile center
    """
    iso_x = (cart_x - cart_y) * ISO_TILE_HALF_WIDTH
    iso_y = (cart_x + cart_y) * ISO_TILE_HALF_HEIGHT
    return iso_x, iso_y


def iso_to_cart(iso_x, iso_y):
    """
    Convert isometric screen coordinates back to Cartesian (grid) coordinates.

    Args:
        iso_x: Screen x position
        iso_y: Screen y position

    Returns:
        tuple: (cart_x, cart_y) grid coordinates (may be float for sub-tile precision)
    """
    cart_x = (iso_x / ISO_TILE_HALF_WIDTH + iso_y / ISO_TILE_HALF_HEIGHT) / 2
    cart_y = (iso_y / ISO_TILE_HALF_HEIGHT - iso_x / ISO_TILE_HALF_WIDTH) / 2
    return cart_x, cart_y


def get_tile_screen_pos(cart_x, cart_y, camera_x=0, camera_y=0):
    """
    Get the screen position for rendering a tile, accounting for camera offset.

    Args:
        cart_x: Grid x position
        cart_y: Grid y position
        camera_x: Camera x offset in screen pixels
        camera_y: Camera y offset in screen pixels

    Returns:
        tuple: (screen_x, screen_y) top-left corner for blitting the tile sprite
    """
    iso_x, iso_y = cart_to_iso(cart_x, cart_y)
    # Offset to get top-left corner of the tile sprite
    screen_x = iso_x - ISO_TILE_HALF_WIDTH - camera_x
    screen_y = iso_y - camera_y
    return screen_x, screen_y


def get_render_order(map_width, map_height):
    """
    Generate tile coordinates in proper back-to-front rendering order.
    For isometric rendering, we need to draw from back (top-left) to front (bottom-right).

    Args:
        map_width: Number of columns in the map
        map_height: Number of rows in the map

    Yields:
        tuple: (x, y) coordinates in render order
    """
    # Render diagonal stripes from top-left to bottom-right
    # Each diagonal has constant (x + y) value
    for diagonal in range(map_width + map_height - 1):
        for x in range(max(0, diagonal - map_height + 1), min(diagonal + 1, map_width)):
            y = diagonal - x
            if 0 <= y < map_height:
                yield x, y


def get_visible_tiles(camera_x, camera_y, screen_width, screen_height, map_width, map_height):
    """
    Calculate which tiles are visible on screen for culling optimization.

    Args:
        camera_x: Camera x offset in screen pixels
        camera_y: Camera y offset in screen pixels
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        map_width: Number of columns in the map
        map_height: Number of rows in the map

    Returns:
        tuple: (min_x, max_x, min_y, max_y) tile range to render
    """
    # Convert screen corners to tile coordinates with some padding
    # Top-left corner of screen
    tl_cart_x, tl_cart_y = iso_to_cart(camera_x - ISO_TILE_WIDTH, camera_y - ISO_TILE_HEIGHT)

    # Bottom-right corner of screen
    br_cart_x, br_cart_y = iso_to_cart(
        camera_x + screen_width + ISO_TILE_WIDTH,
        camera_y + screen_height + ISO_TILE_HEIGHT
    )

    # Convert to tile indices with padding
    min_x = max(0, int(tl_cart_x) - 2)
    max_x = min(map_width, int(br_cart_x) + 3)
    min_y = max(0, int(tl_cart_y) - 2)
    max_y = min(map_height, int(br_cart_y) + 3)

    return min_x, max_x, min_y, max_y


def get_depth_value(cart_x, cart_y, layer=0):
    """
    Calculate depth value for sorting sprites in rendering order.
    Higher depth values should be drawn later (in front).

    Args:
        cart_x: Grid x position
        cart_y: Grid y position
        layer: Layer offset (0=ground, 1=buildings, 2=player/props)

    Returns:
        float: Depth value for sorting
    """
    # Base depth from position (diagonal distance from origin)
    base_depth = cart_x + cart_y
    # Add layer offset (each layer is effectively "above" the previous)
    return base_depth + layer * 1000


def point_in_tile(screen_x, screen_y, tile_screen_x, tile_screen_y):
    """
    Check if a screen point is within an isometric tile diamond.

    Args:
        screen_x, screen_y: Screen point to test
        tile_screen_x, tile_screen_y: Top-left corner of tile sprite

    Returns:
        bool: True if point is inside the tile diamond
    """
    # Convert to tile-local coordinates (center of diamond)
    local_x = screen_x - tile_screen_x - ISO_TILE_HALF_WIDTH
    local_y = screen_y - tile_screen_y - ISO_TILE_HALF_HEIGHT

    # Diamond test: |x/w| + |y/h| <= 0.5
    if ISO_TILE_HALF_WIDTH > 0 and ISO_TILE_HALF_HEIGHT > 0:
        return (abs(local_x) / ISO_TILE_HALF_WIDTH +
                abs(local_y) / ISO_TILE_HALF_HEIGHT) <= 1.0
    return False


def screen_to_tile(screen_x, screen_y, camera_x=0, camera_y=0):
    """
    Convert screen coordinates (with camera offset) to tile coordinates.

    Args:
        screen_x, screen_y: Screen position
        camera_x, camera_y: Camera offset

    Returns:
        tuple: (tile_x, tile_y) as integers
    """
    # Convert screen to world coordinates
    world_x = screen_x + camera_x
    world_y = screen_y + camera_y

    # Convert to cartesian grid coordinates
    cart_x, cart_y = iso_to_cart(world_x + ISO_TILE_HALF_WIDTH, world_y)

    return int(cart_x), int(cart_y)

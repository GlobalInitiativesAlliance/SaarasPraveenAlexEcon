"""
Furniture Collision Shape Definitions

Maps tile sprites to their collision shapes.
Uses sensible defaults so you don't need to define every single tile.

Design principle: Collision shapes are SMALLER than visual sprites
to make movement feel less "blocky".
"""
from src.interiors.collision_shapes import CollisionShape, ShapeType


# Tile size in pixels (scaled from 16x16 to 32x32)
TILE_SIZE = 32


# ============================================================================
# FURNITURE COLLISION DEFINITIONS
# ============================================================================
# Key: (sheet_name, sprite_x, sprite_y) - matches the tile_info format
# Value: dict with 'shape' and optional 'offset' for multi-tile furniture
#
# Shape types:
#   - CIRCLE: Good for round tables, plants, barrels
#   - RECTANGLE: Good for desks, beds, bookshelves
#
# All positions are relative to the tile's top-left corner (0,0 to 32,32)
# ============================================================================

FURNITURE_COLLIDERS = {
    # -------------------------------------------------------------------------
    # Living Room Furniture (2_LivingRoom_16x16.png)
    # -------------------------------------------------------------------------

    # Couch/sofa pieces - use rectangles, slightly smaller than tile
    ("2_LivingRoom_16x16.png", 7, 1): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 8, "w": 28, "h": 20},
    ("2_LivingRoom_16x16.png", 8, 1): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 8, "w": 28, "h": 20},
    ("2_LivingRoom_16x16.png", 9, 1): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 8, "w": 28, "h": 20},

    # TV/entertainment center - narrow rectangle
    ("2_LivingRoom_16x16.png", 13, 0): {"shape": ShapeType.RECTANGLE, "x": 4, "y": 12, "w": 24, "h": 16},
    ("2_LivingRoom_16x16.png", 14, 0): {"shape": ShapeType.RECTANGLE, "x": 4, "y": 12, "w": 24, "h": 16},

    # Small round table - circle collider!
    ("2_LivingRoom_16x16.png", 5, 17): {"shape": ShapeType.CIRCLE, "x": 16, "y": 16, "r": 12},
    ("2_LivingRoom_16x16.png", 6, 17): {"shape": ShapeType.CIRCLE, "x": 16, "y": 16, "r": 12},

    # -------------------------------------------------------------------------
    # Interior Furniture (Interiors_16x16.png)
    # -------------------------------------------------------------------------

    # Bookshelves - tall rectangles
    ("Interiors_16x16.png", 5, 14): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 4, "w": 28, "h": 26},
    ("Interiors_16x16.png", 6, 14): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 4, "w": 28, "h": 26},

    # Beds - larger rectangles
    ("Interiors_16x16.png", 2, 19): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 4, "w": 28, "h": 26},
    ("Interiors_16x16.png", 3, 19): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 4, "w": 28, "h": 26},
    ("Interiors_16x16.png", 4, 19): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 4, "w": 28, "h": 26},
    ("Interiors_16x16.png", 5, 19): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 4, "w": 28, "h": 26},

    # Table/desk - rectangle
    ("Interiors_16x16.png", 0, 10): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 6, "w": 28, "h": 22},
    ("Interiors_16x16.png", 1, 10): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 6, "w": 28, "h": 22},
    ("Interiors_16x16.png", 2, 10): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 6, "w": 28, "h": 22},
    ("Interiors_16x16.png", 3, 10): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 6, "w": 28, "h": 22},

    # Chairs - small rectangle or circle
    ("Interiors_16x16.png", 6, 21): {"shape": ShapeType.RECTANGLE, "x": 6, "y": 8, "w": 20, "h": 20},
    ("Interiors_16x16.png", 7, 21): {"shape": ShapeType.RECTANGLE, "x": 6, "y": 8, "w": 20, "h": 20},
    ("Interiors_16x16.png", 6, 22): {"shape": ShapeType.RECTANGLE, "x": 6, "y": 4, "w": 20, "h": 24},
    ("Interiors_16x16.png", 7, 22): {"shape": ShapeType.RECTANGLE, "x": 6, "y": 4, "w": 20, "h": 24},

    # Door frame (yellow grid in foster home) - no collision, it's a passage
    ("Interiors_16x16.png", 13, 11): {"shape": None},  # Explicitly no collision
    ("Interiors_16x16.png", 14, 11): {"shape": None},
    ("Interiors_16x16.png", 15, 11): {"shape": None},
    ("Interiors_16x16.png", 13, 12): {"shape": None},
    ("Interiors_16x16.png", 14, 12): {"shape": None},
    ("Interiors_16x16.png", 15, 12): {"shape": None},
    ("Interiors_16x16.png", 13, 13): {"shape": None},
    ("Interiors_16x16.png", 14, 13): {"shape": None},
    ("Interiors_16x16.png", 15, 13): {"shape": None},
    ("Interiors_16x16.png", 13, 14): {"shape": None},
    ("Interiors_16x16.png", 14, 14): {"shape": None},
    ("Interiors_16x16.png", 15, 14): {"shape": None},

    # -------------------------------------------------------------------------
    # Kitchen Furniture (12_Kitchen_16x16.png)
    # -------------------------------------------------------------------------

    # Kitchen floor tiles - no collision (flat)
    ("12_Kitchen_16x16.png", 3, 31): {"shape": None},

    # Counters - rectangles
    ("12_Kitchen_16x16.png", 0, 10): {"shape": ShapeType.RECTANGLE, "x": 2, "y": 8, "w": 28, "h": 22},

    # -------------------------------------------------------------------------
    # Room Builder (Room_Builder_16x16.png)
    # -------------------------------------------------------------------------

    # Floor tiles - no collision (flat ground)
    ("Room_Builder_16x16.png", 22, 22): {"shape": None},
}


# Tiles that should NEVER have collision (floor, rugs, shadows)
# Add tiles here that are purely decorative floor elements
FLAT_TILES = {
    # Standard floor tiles
    ("Room_Builder_16x16.png", 22, 22),  # Standard floor
    ("12_Kitchen_16x16.png", 3, 31),     # Kitchen floor

    # Common rug/carpet patterns - add more as needed
    # Format: (spritesheet, sprite_x, sprite_y)
}


def get_collider_for_tile(tile_info, tile_x, tile_y):
    """
    Get the collision shape for a furniture tile.

    Args:
        tile_info: [sheet_name, sprite_x, sprite_y] from room JSON
        tile_x: Tile X position in room grid
        tile_y: Tile Y position in room grid

    Returns:
        CollisionShape at world position, or None if tile has no collision
    """
    if not tile_info or len(tile_info) < 3:
        return None

    key = (tile_info[0], tile_info[1], tile_info[2])

    # Check if this is a flat tile (no collision)
    if key in FLAT_TILES:
        return None

    # Look up specific collider definition
    collider_def = FURNITURE_COLLIDERS.get(key)

    if collider_def is not None:
        if collider_def.get("shape") is None:
            return None  # Explicitly no collision

        shape_type = collider_def["shape"]
        offset_x = collider_def.get("x", 4)
        offset_y = collider_def.get("y", 4)

        # Calculate world position
        world_x = tile_x * TILE_SIZE + offset_x
        world_y = tile_y * TILE_SIZE + offset_y

        if shape_type == ShapeType.CIRCLE:
            radius = collider_def.get("r", 12)
            return CollisionShape(
                shape_type=ShapeType.CIRCLE,
                x=world_x,
                y=world_y,
                width=radius
            )
        else:
            width = collider_def.get("w", 24)
            height = collider_def.get("h", 24)
            return CollisionShape(
                shape_type=ShapeType.RECTANGLE,
                x=world_x,
                y=world_y,
                width=width,
                height=height
            )

    # DEFAULT: Use a smaller rectangle (not full tile)
    # This makes collision feel less blocky
    return CollisionShape(
        shape_type=ShapeType.RECTANGLE,
        x=tile_x * TILE_SIZE + 4,  # 4px padding
        y=tile_y * TILE_SIZE + 4,
        width=24,  # 24px instead of 32
        height=24
    )


def is_flat_tile(tile_info):
    """
    Check if a tile is "flat" (floor, rug, shadow) and shouldn't have collision.

    Args:
        tile_info: [sheet_name, sprite_x, sprite_y]

    Returns:
        True if tile should have no collision
    """
    if not tile_info or len(tile_info) < 3:
        return True  # Empty tiles are "flat"

    key = (tile_info[0], tile_info[1], tile_info[2])

    # Check explicit flat tiles
    if key in FLAT_TILES:
        return True

    # Check if explicitly marked as no collision
    collider_def = FURNITURE_COLLIDERS.get(key)
    if collider_def is not None and collider_def.get("shape") is None:
        return True

    return False

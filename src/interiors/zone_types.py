"""
Zone types for interior room movement system.
Provides more sophisticated collision/interaction handling than simple blocked/walkable.
"""
from enum import IntEnum


class ZoneType(IntEnum):
    """Zone types for interior tiles"""
    WALKABLE = 0      # Player can walk freely
    BLOCKED = 1       # Impassable (furniture, walls)
    INTERACTIVE = 2   # Can walk but shows interaction prompt
    TRANSITION = 3    # Triggers room/floor transition (doors, stairs)
    BOUNDARY = 4      # Room edge - treated as wall


# Zone types that allow movement
WALKABLE_ZONES = {ZoneType.WALKABLE, ZoneType.INTERACTIVE, ZoneType.TRANSITION}

# Zone types that block movement
BLOCKING_ZONES = {ZoneType.BLOCKED, ZoneType.BOUNDARY}

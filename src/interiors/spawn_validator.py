"""
NPC Spawn Validation System
Ensures NPCs are placed only on walkable tiles.
Uses BFS spiral search to find nearest valid position when blocked.
"""


class SpawnValidator:
    """Validates and corrects NPC spawn positions using zone system"""

    # Maximum tiles to search when finding valid position
    MAX_SEARCH_RADIUS = 10

    @staticmethod
    def validate_position(zone_system, x, y, entity_name="NPC"):
        """
        Check if position is valid for spawning.

        Args:
            zone_system: ZoneSystem instance with built zone map
            x: Tile X coordinate
            y: Tile Y coordinate
            entity_name: Name for debug logging

        Returns:
            tuple: (is_valid: bool, validated_x: int, validated_y: int)
        """
        # Check if original position is walkable
        if zone_system.can_move_to(x, y):
            return True, x, y

        # Position is blocked - find nearest valid position
        print(f"[NPC_SPAWN] Warning: '{entity_name}' position ({x}, {y}) is blocked - finding nearest valid")

        valid_x, valid_y = SpawnValidator.find_nearest_walkable(zone_system, x, y)

        if valid_x is not None:
            distance = abs(valid_x - x) + abs(valid_y - y)
            print(f"[NPC_SPAWN] '{entity_name}' relocated from ({x}, {y}) to ({valid_x}, {valid_y}) [distance: {distance}]")
            return False, valid_x, valid_y
        else:
            print(f"[NPC_SPAWN] ERROR: Could not find valid position for '{entity_name}' near ({x}, {y})")
            return False, x, y  # Return original as fallback

    @staticmethod
    def find_nearest_walkable(zone_system, start_x, start_y):
        """
        Find nearest walkable tile using BFS spiral search.
        Memory efficient - no pre-computation required.

        Args:
            zone_system: ZoneSystem instance
            start_x, start_y: Starting tile coordinates

        Returns:
            tuple: (x, y) of nearest walkable tile, or (None, None) if none found
        """
        visited = set()
        visited.add((start_x, start_y))

        # Check in expanding rings (Manhattan distance)
        for radius in range(1, SpawnValidator.MAX_SEARCH_RADIUS + 1):
            candidates = SpawnValidator._get_ring_positions(start_x, start_y, radius)

            for x, y in candidates:
                if (x, y) in visited:
                    continue
                visited.add((x, y))

                # Check walkability (zone system handles bounds)
                if zone_system.can_move_to(x, y):
                    return x, y

        return None, None

    @staticmethod
    def _get_ring_positions(cx, cy, radius):
        """
        Get all positions at exactly 'radius' Manhattan distance.
        Returns positions in a deterministic order (prioritizes cardinal directions).

        Args:
            cx, cy: Center coordinates
            radius: Manhattan distance from center

        Returns:
            list: List of (x, y) tuples at the given radius
        """
        positions = []

        # Generate positions at exactly 'radius' Manhattan distance
        # Start from top and go clockwise for deterministic ordering
        for dx in range(-radius, radius + 1):
            dy = radius - abs(dx)
            # Top half of the diamond
            positions.append((cx + dx, cy - dy))
            # Bottom half (skip if dy is 0 to avoid duplicates)
            if dy != 0:
                positions.append((cx + dx, cy + dy))

        return positions

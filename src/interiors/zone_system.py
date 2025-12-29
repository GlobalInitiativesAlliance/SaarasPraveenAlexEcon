"""
Zone-based movement system for interior rooms.
Provides sophisticated collision detection with different zone types.
"""
from .zone_types import ZoneType, WALKABLE_ZONES, BLOCKING_ZONES
from .furniture_colliders import is_flat_tile


class ZoneMap:
    """2D map of zone types for a room"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Initialize all tiles as WALKABLE
        self.zones = [[ZoneType.WALKABLE] * width for _ in range(height)]
        # Metadata for special zones (interactions, transitions, etc.)
        self.zone_metadata = {}  # {(x, y): {"type": "desk", "prompt": "Use desk", ...}}

    def get_zone(self, x, y):
        """Get zone type at position, returns BOUNDARY if out of bounds"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.zones[y][x]
        return ZoneType.BOUNDARY

    def set_zone(self, x, y, zone_type, metadata=None):
        """Set zone type at position with optional metadata"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.zones[y][x] = zone_type
            if metadata:
                self.zone_metadata[(x, y)] = metadata

    def get_metadata(self, x, y):
        """Get metadata for a position if it exists"""
        return self.zone_metadata.get((x, y))

    def is_walkable(self, x, y):
        """Check if position is walkable"""
        return self.get_zone(x, y) in WALKABLE_ZONES

    def is_blocked(self, x, y):
        """Check if position is blocked"""
        return self.get_zone(x, y) in BLOCKING_ZONES


class ZoneSystem:
    """Manages zone maps for interior rooms"""

    def __init__(self, room_width, room_height):
        self.zone_map = ZoneMap(room_width, room_height)
        self.room_width = room_width
        self.room_height = room_height

    def build_from_room_data(self, room_data, doors=None, blocking_layers=None):
        """
        Build zone map from room layer data.

        Args:
            room_data: Dict containing 'layers' with 'furniture', 'walls', etc.
            doors: List of door positions [[x, y], ...]
            blocking_layers: List of layer names to treat as blocking (default: walls, furniture, decor)

        Returns:
            ZoneMap instance
        """
        doors = doors or []
        door_set = set((d[0], d[1]) for d in doors if len(d) >= 2)

        # Default blocking layers - include decor since furniture is often placed there
        if blocking_layers is None:
            blocking_layers = ['walls', 'furniture', 'decor']

        layers = room_data.get('layers', {})

        # Process all blocking layers
        for layer_name in blocking_layers:
            self._process_layer(layers.get(layer_name, []), ZoneType.BLOCKED)

        # Mark door positions as TRANSITION
        for door in doors:
            if len(door) >= 2:
                x, y = door[0], door[1]
                self.zone_map.set_zone(x, y, ZoneType.TRANSITION, {
                    "type": "door",
                    "action": "exit"
                })

        # Process custom zones from room_data if present
        zones_def = room_data.get('zones', {})
        self._apply_interactive_zones(zones_def.get('interactive', []))
        self._apply_transition_zones(zones_def.get('transition', []))

        return self.zone_map

    def build_from_collision_map(self, collision_map):
        """
        Convert legacy collision map (set of blocked tiles) to zone system.
        Maintains backward compatibility with existing rooms.

        Args:
            collision_map: Set of (x, y) tuples representing blocked tiles
        """
        for pos in collision_map:
            self.zone_map.set_zone(pos[0], pos[1], ZoneType.BLOCKED)

        return self.zone_map

    def _process_layer(self, layer, zone_type):
        """Mark tiles with content in a layer as the specified zone type.

        Skips 'flat' tiles like carpets, rugs, and floor decorations that
        shouldn't block movement.
        """
        for y in range(min(len(layer), self.room_height)):
            for x in range(min(len(layer[y]) if y < len(layer) else 0, self.room_width)):
                tile_info = layer[y][x]
                if tile_info is not None:
                    # Skip flat tiles (carpets, rugs, floor decor) - they don't block
                    if is_flat_tile(tile_info):
                        continue
                    self.zone_map.set_zone(x, y, zone_type)

    def _apply_interactive_zones(self, interactive_list):
        """Apply interactive zone definitions from room data"""
        for item in interactive_list:
            x = item.get('x', 0)
            y = item.get('y', 0)
            self.zone_map.set_zone(x, y, ZoneType.INTERACTIVE, {
                "type": item.get('type', 'unknown'),
                "prompt": item.get('prompt', 'Interact'),
                "action": item.get('action', 'none')
            })

    def _apply_transition_zones(self, transition_list):
        """Apply transition zone definitions from room data"""
        for item in transition_list:
            x = item.get('x', 0)
            y = item.get('y', 0)
            self.zone_map.set_zone(x, y, ZoneType.TRANSITION, {
                "type": "transition",
                "target": item.get('target', 'exterior'),
                "door_id": item.get('door_id'),
                "stairs": item.get('stairs', False)
            })

    def can_move_to(self, x, y):
        """Check if player can move to position"""
        return self.zone_map.is_walkable(x, y)

    def get_zone_at(self, x, y):
        """Get zone type at position"""
        return self.zone_map.get_zone(x, y)

    def get_interaction_at(self, x, y):
        """Get interaction metadata if position is interactive or transition"""
        zone = self.zone_map.get_zone(x, y)
        if zone in (ZoneType.INTERACTIVE, ZoneType.TRANSITION):
            return self.zone_map.get_metadata(x, y)
        return None

    def mark_boundary(self, doors=None):
        """Mark room perimeter as BOUNDARY (except doors)"""
        doors = doors or []
        door_set = set((d[0], d[1]) for d in doors if len(d) >= 2)

        # Top and bottom edges
        for x in range(self.room_width):
            if (x, 0) not in door_set:
                self.zone_map.set_zone(x, 0, ZoneType.BOUNDARY)
            if (x, self.room_height - 1) not in door_set:
                self.zone_map.set_zone(x, self.room_height - 1, ZoneType.BOUNDARY)

        # Left and right edges
        for y in range(self.room_height):
            if (0, y) not in door_set:
                self.zone_map.set_zone(0, y, ZoneType.BOUNDARY)
            if (self.room_width - 1, y) not in door_set:
                self.zone_map.set_zone(self.room_width - 1, y, ZoneType.BOUNDARY)

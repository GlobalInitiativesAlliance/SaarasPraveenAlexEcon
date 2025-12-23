"""
Auto-wall generator for interior rooms.
Generates wall tiles around room perimeters with gaps for doors.
"""
import os


class WallGenerator:
    """Generates wall tiles for room perimeters"""

    # Wall tile positions in Room_Builder_Walls_16x16.png
    # Standard tileset layout: 3x3 grid for corners and edges
    WALL_STYLES = {
        "modern": {
            "tileset": "Room_Builder_Walls_16x16.png",
            "tileset_path": "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Walls_16x16.png",
            # Top row of room (wall top)
            "top_left_corner": (0, 0),
            "top_wall": (1, 0),
            "top_right_corner": (2, 0),
            # Middle (side walls)
            "left_wall": (0, 1),
            "right_wall": (2, 1),
            # Bottom row
            "bottom_left_corner": (0, 2),
            "bottom_wall": (1, 2),
            "bottom_right_corner": (2, 2),
            # Door frames (optional)
            "door_frame_left": (3, 0),
            "door_frame_right": (4, 0),
        },
        "office": {
            "tileset": "Room_Builder_Walls_16x16.png",
            "tileset_path": "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Walls_16x16.png",
            # Use different row in tileset for office style
            "top_left_corner": (0, 3),
            "top_wall": (1, 3),
            "top_right_corner": (2, 3),
            "left_wall": (0, 4),
            "right_wall": (2, 4),
            "bottom_left_corner": (0, 5),
            "bottom_wall": (1, 5),
            "bottom_right_corner": (2, 5),
        },
        "home": {
            "tileset": "Room_Builder_Walls_16x16.png",
            "tileset_path": "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Walls_16x16.png",
            # Use different row in tileset for home style
            "top_left_corner": (0, 6),
            "top_wall": (1, 6),
            "top_right_corner": (2, 6),
            "left_wall": (0, 7),
            "right_wall": (2, 7),
            "bottom_left_corner": (0, 8),
            "bottom_wall": (1, 8),
            "bottom_right_corner": (2, 8),
        }
    }

    # Shadow tile positions in Room_Builder_Floor_Shadows_16x16.png
    SHADOW_TILESET = "Room_Builder_Floor_Shadows_16x16.png"
    SHADOW_TILESET_PATH = "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Floor_Shadows_16x16.png"

    # Baseboard tile positions in Room_Builder_Baseboards_16x16.png
    BASEBOARD_TILESET = "Room_Builder_Baseboards_16x16.png"
    BASEBOARD_TILESET_PATH = "assets/moderninteriors-win/1_Interiors/16x16/Room_Builder_subfiles/Room_Builder_Baseboards_16x16.png"

    def __init__(self, style="modern"):
        """Initialize wall generator with a style"""
        self.style = style if style in self.WALL_STYLES else "modern"
        self.tiles = self.WALL_STYLES[self.style]

    def generate_walls(self, room_width, room_height, doors=None, include_bottom=False):
        """
        Generate wall layer data for room perimeter.

        Args:
            room_width: Width of room in tiles
            room_height: Height of room in tiles
            doors: List of door positions [[x, y], ...] to leave gaps
            include_bottom: Whether to include bottom wall (usually false for exit)

        Returns:
            2D list of wall tile data [[tile_info, ...], ...]
            where tile_info is [tileset_name, tile_x, tile_y] or None
        """
        doors = doors or []
        door_set = set((d[0], d[1]) for d in doors if len(d) >= 2)

        # Initialize empty wall layer
        walls = [[None] * room_width for _ in range(room_height)]

        tileset = self.tiles["tileset"]

        # Top wall (y = 0)
        for x in range(room_width):
            if (x, 0) not in door_set:
                if x == 0:
                    tile_pos = self.tiles["top_left_corner"]
                elif x == room_width - 1:
                    tile_pos = self.tiles["top_right_corner"]
                else:
                    tile_pos = self.tiles["top_wall"]
                walls[0][x] = [tileset, tile_pos[0], tile_pos[1]]

        # Side walls (y = 1 to room_height - 2)
        for y in range(1, room_height - 1):
            # Left wall (x = 0)
            if (0, y) not in door_set:
                tile_pos = self.tiles["left_wall"]
                walls[y][0] = [tileset, tile_pos[0], tile_pos[1]]

            # Right wall (x = room_width - 1)
            if (room_width - 1, y) not in door_set:
                tile_pos = self.tiles["right_wall"]
                walls[y][room_width - 1] = [tileset, tile_pos[0], tile_pos[1]]

        # Bottom wall (y = room_height - 1) - only if include_bottom
        if include_bottom:
            for x in range(room_width):
                if (x, room_height - 1) not in door_set:
                    if x == 0:
                        tile_pos = self.tiles["bottom_left_corner"]
                    elif x == room_width - 1:
                        tile_pos = self.tiles["bottom_right_corner"]
                    else:
                        tile_pos = self.tiles["bottom_wall"]
                    walls[room_height - 1][x] = [tileset, tile_pos[0], tile_pos[1]]

        return walls

    def generate_shadows(self, walls_layer, room_width, room_height):
        """
        Generate floor shadows cast by walls.

        Args:
            walls_layer: The wall layer data from generate_walls()
            room_width: Width of room in tiles
            room_height: Height of room in tiles

        Returns:
            2D list of shadow tile data
        """
        shadows = [[None] * room_width for _ in range(room_height)]

        # Shadow below top wall
        for x in range(room_width):
            if walls_layer[0][x] is not None:
                if 1 < room_height:
                    # Add shadow tile below wall
                    shadows[1][x] = [self.SHADOW_TILESET, 0, 0]

        # Shadow to the right of left wall
        for y in range(1, room_height - 1):
            if walls_layer[y][0] is not None:
                if 1 < room_width:
                    # Only add if not already shadowed
                    if shadows[y][1] is None:
                        shadows[y][1] = [self.SHADOW_TILESET, 1, 0]

        return shadows

    def generate_baseboards(self, walls_layer, room_width, room_height):
        """
        Generate baseboards where walls meet floor.

        Args:
            walls_layer: The wall layer data from generate_walls()
            room_width: Width of room in tiles
            room_height: Height of room in tiles

        Returns:
            2D list of baseboard tile data
        """
        baseboards = [[None] * room_width for _ in range(room_height)]

        # Baseboard along bottom of top wall
        for x in range(room_width):
            if walls_layer[0][x] is not None:
                if 1 < room_height and walls_layer[1][x] is None:
                    baseboards[1][x] = [self.BASEBOARD_TILESET, 0, 0]

        return baseboards

    def merge_walls_with_existing(self, auto_walls, existing_walls):
        """
        Merge auto-generated walls with existing manually placed walls.
        Existing walls take priority (won't be overwritten).

        Args:
            auto_walls: Auto-generated wall layer
            existing_walls: Existing wall layer from room data

        Returns:
            Merged wall layer
        """
        if not existing_walls:
            return auto_walls

        room_height = len(auto_walls)
        room_width = len(auto_walls[0]) if room_height > 0 else 0

        merged = [[None] * room_width for _ in range(room_height)]

        for y in range(room_height):
            for x in range(room_width):
                # Check existing walls first
                if y < len(existing_walls) and x < len(existing_walls[y]):
                    if existing_walls[y][x] is not None:
                        merged[y][x] = existing_walls[y][x]
                        continue

                # Use auto-generated wall
                merged[y][x] = auto_walls[y][x]

        return merged


def get_wall_generator(style="modern"):
    """Factory function to create a wall generator"""
    return WallGenerator(style)

"""
Room data mapping constants.

Maps interior room names to their JSON layout files.
"""

# Non-building objects that should be filtered out when detecting buildings
NON_BUILDING_OBJECTS = frozenset([
    'tree', 'bush', 'flower', 'plant', 'grass', 'rock', 'stone'
])

# Building tile types that indicate a valid building
BUILDING_TILE_TYPES = frozenset([
    'building', 'building_with_bg', 'building_part_with_bg'
])

# Maps room names to their JSON layout files
# Scene-specific interiors use base room layouts
ROOM_DATA_MAP = {
    'foster_home_aging_out': 'foster_home.json',
    'tlp_housing_final': 'foster_home.json',
    'tlp_housing_dynamic': 'foster_home.json',
    'studio_apartment_part1': 'bad_studio.json',
    'studio_apartment_part2': 'bad_studio.json',
    'crappy_apartment': 'bad_studio.json',
    'community_center': 'community_center.json',
    'classroom': 'classroom.json',
    'housing_office': 'rental.json',
    'government_office': 'housing_office.json',
    'courthouse': 'hospital.json',
    'pharmacy': 'hospital.json',
}


def get_room_json_file(room_name: str) -> str:
    """
    Get the JSON file for a given room name.

    Args:
        room_name: The name of the room interior.

    Returns:
        The JSON filename to load for this room.
    """
    return ROOM_DATA_MAP.get(room_name, f"{room_name}.json")


def is_non_building_object(building_name: str) -> bool:
    """
    Check if a building name is actually a non-building object (tree, bush, etc.).

    Args:
        building_name: The name of the building/object.

    Returns:
        True if this is a non-building object that should be filtered out.
    """
    building_name_lower = building_name.lower()
    return any(nb in building_name_lower for nb in NON_BUILDING_OBJECTS)


def is_building_tile_type(tile_type: str) -> bool:
    """
    Check if a tile type represents a building.

    Args:
        tile_type: The type of the tile.

    Returns:
        True if this tile type indicates a building.
    """
    return tile_type in BUILDING_TILE_TYPES

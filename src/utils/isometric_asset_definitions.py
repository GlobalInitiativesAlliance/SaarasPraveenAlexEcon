"""
Isometric Asset Definitions

Maps the Isometric City asset pack files to logical categories for the game.
Each asset file is a horizontal strip containing 4 sprite variants.
"""

import os

# Base path for isometric assets
ISOMETRIC_ASSETS_BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'assets', 'Isometric City'
)

# Ground tile definitions (category -> list of asset files)
# Each file contains 4 variants as a horizontal strip
GROUND_TILES = {
    'road': [
        'GroundModules/City-26-road1.png',
    ],
    'sidewalk': [
        'GroundModules/City-6-sidewalk_D.png',
        'GroundModules/City-7-sidewalk_B.png',
        'GroundModules/City-8-sidewalk_A.png',
        'GroundModules/City-24-sidewalk_E.png',
        'GroundModules/City-25-sidewalk_C.png',
    ],
    'grass': [
        'GroundModules/City-11-parkgrass_A.png',
        'GroundModules/City-34-parkgrass_K.png',
        'GroundModules/City-35-parkgrass_J.png',
        'GroundModules/City-36-parkgrass_I.png',
        'GroundModules/City-37-parkgrass_H.png',
        'GroundModules/City-38-parkgrass_G.png',
        'GroundModules/City-39-parkgrass_F.png',
        'GroundModules/City-40-parkgrass_E.png',
        'GroundModules/City-41-parkgrass_D.png',
        'GroundModules/City-42-parkgrass_C.png',
        'GroundModules/City-43-parkgrass_B.png',
    ],
    'path': [
        'GroundModules/City-29-path_4.png',
        'GroundModules/City-30-path_3.png',
        'GroundModules/City-31-path_2.png',
        'GroundModules/City-32-path_1.png',
    ],
    'parking': [
        'GroundModules/City-33-parking.png',
    ],
    'basketball': [
        'GroundModules/City-66-basket_terrain_4.png',
        'GroundModules/City-67-basket_terrain_3.png',
        'GroundModules/City-68-basket_terrain_2.png',
        'GroundModules/City-69-basket_terrain_1.png',
    ],
}

# Building definitions (building_type -> list of asset files)
# Buildings are larger sprites, not horizontal strips
BUILDINGS = {
    'yellow': [
        'Building/City-12-building_yellow_C.png',
        'Building/City-13-building_yellow_B.png',
        'Building/City-14-building_yellow_A.png',
    ],
    'blue': [
        'Building/City-19-building_blue_A.png',
        'Building/City-63-building_blue_B.png',
    ],
    'brown': [
        'Building/City-17-building_brown_B.png',
        'Building/City-18-building_brown_A.png',
    ],
    'light_brown': [
        'Building/City-15-building_light_brown_D.png',
        'Building/City-16-building_light_brown_C.png',
        'Building/City-62-building_light_brown_B.png',
    ],
}

# Prop definitions (prop_type -> list of asset files)
PROPS = {
    'trees': [
        'Nature&Character/City-21-tree_C.png',
        'Nature&Character/City-22-tree_B.png',
        'Nature&Character/City-23-tree_A.png',
    ],
    'vehicles': [
        'Props/City-20-truck.png',
        'Props/City-28-pickup.png',
        'Props/City-46-icecream_truck.png',
        'Props/City-49-garbagetruck.png',
        'Props/City-50-garbagetruck.png',
        'Props/City-51-foodtruck.png',
        'Props/City-52-firetruck.png',
        'Props/City-54-car5.png',
        'Props/City-55-car4.png',
        'Props/City-56-car3.png',
        'Props/City-57-car3.png',
        'Props/City-58-car2.png',
        'Props/City-59-car2.png',
    ],
    'street_furniture': [
        'Props/City-60-bus stop.png',
        'Props/City-84-utility_poles.png',
        'Props/City-86-trash bin.png',
        'Props/City-104-parking meter.png',
        'Props/City-105-park_trashcan.png',
        'Props/City-106-newspaper booth.png',
        'Props/City-121-bench.png',
        'Props/City-133-ATM.png',
    ],
    'food_stands': [
        'Props/City-44-noodle.png',
        'Props/City-53-donut.png',
        'Props/City-61-burger.png',
        'Props/City-88-tacos_2.png',
        'Props/City-97-pizza_slice_sign.png',
        'Props/City-98-pizza_sign.png',
        'Props/City-107-milkshake.png',
        'Props/City-109-icecream.png',
        'Props/City-110-hotdog_stand.png',
    ],
    'park': [
        'Props/City-100-picnic_table.png',
        'Props/City-101-picnic_bench.png',
        'Props/City-102-picnic_bench.png',
        'Props/City-111-fountain.png',
        'Props/City-122-basketball_hoop.png',
    ],
    'signs': [
        'Props/City-123-XXX.png',
        'Props/City-124-PUB.png',
        'Props/City-125-HOTEL.png',
    ],
    'trains': [
        'Props/City-0-train_station_C.png',
        'Props/City-1-train_station_B.png',
        'Props/City-2-train_station_A.png',
        'Props/City-5-stairwell.png',
        'Props/City-9-rail_B.png',
        'Props/City-10-rail_A.png',
        'Props/City-27-rail_C.png',
        'Props/City-45-metro.png',
    ],
    'sunshades': [
        'Props/City-3-sunshade_medium_red.png',
        'Props/City-4-sunshade_big_yellow.png',
    ],
    'misc': [
        'Props/City-78-security_barrier.png',
        'Props/City-79-parable.png',
        'Props/City-80-outdoor_unit.png',
        'Props/City-90-stroller.png',
        'Props/City-91-skate.png',
        'Props/City-92-security cam.png',
        'Props/City-93-roof glass window.png',
        'Props/City-112-flowers in windows.png',
        'Props/City-117-cardboard.png',
        'Props/City-119-bike_2.png',
        'Props/City-134-ventilation_C-0.png',
    ],
    'laundry': [
        'Props/City-47-hanging_clothes_B.png',
        'Props/City-48-hanging_clothes_A.png',
    ],
}

# Building type to interior mapping
# Maps building visual types to room/interior types
BUILDING_INTERIOR_MAPPING = {
    'yellow_0': 'apartment',
    'yellow_1': 'office',
    'yellow_2': 'library',
    'blue_0': 'hospital',
    'blue_1': 'school',
    'brown_0': 'bank',
    'brown_1': 'grocery_store',
    'light_brown_0': 'foster_home',
    'light_brown_1': 'community_center',
    'light_brown_2': 'tlp_apartment',
}


def get_asset_path(relative_path):
    """Get full path for an asset file."""
    return os.path.join(ISOMETRIC_ASSETS_BASE, relative_path)


def get_all_ground_files():
    """Get list of all ground tile asset files."""
    files = []
    for category_files in GROUND_TILES.values():
        files.extend(category_files)
    return files


def get_all_building_files():
    """Get list of all building asset files."""
    files = []
    for category_files in BUILDINGS.values():
        files.extend(category_files)
    return files


def get_all_prop_files():
    """Get list of all prop asset files."""
    files = []
    for category_files in PROPS.values():
        files.extend(category_files)
    return files

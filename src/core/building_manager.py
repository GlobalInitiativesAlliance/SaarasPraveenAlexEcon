"""
Building Manager - Handles building detection and interior loading
"""
import json
import os
import pygame
from shared.constants import TILE_SIZE

class BuildingManager:
    def __init__(self, game):
        self.game = game
        self.building_interiors = {}
        self.load_building_interiors()

    def load_building_interiors(self):
        """Load building-interior mappings from file"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        mappings_file = os.path.join(base_dir, "data", "maps", "building_interiors.json")

        if os.path.exists(mappings_file):
            try:
                with open(mappings_file, 'r') as f:
                    self.building_interiors = json.load(f)
                print(f"Loaded {len(self.building_interiors)} building-interior mappings")
            except Exception as e:
                print(f"Error loading building interiors: {e}")
                self.building_interiors = {}
        else:
            print("No building-interior mappings found")
            self.building_interiors = {}

    def get_building_at_position(self, world_x, world_y):
        """Check if there's a building at the given world position"""
        # Convert world coordinates to tile coordinates
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        # Check if position is within map bounds
        if 0 <= tile_x < self.game.city_map.width and 0 <= tile_y < self.game.city_map.height:
            # Get the tile data at this position
            tile_data = self.game.city_map.map_data[tile_y][tile_x]


            if tile_data and isinstance(tile_data, tuple):
                # Check if it's a building tile
                if tile_data[0] in ['building', 'building_with_bg']:
                    # Extract building info based on type
                    if tile_data[0] == 'building_with_bg':
                        _, building_name, offset_x, offset_y, _ = tile_data
                    else:
                        _, building_name, offset_x, offset_y = tile_data

                    # Filter out non-building objects like trees
                    building_name_lower = building_name.lower()
                    non_buildings = ['tree', 'bush', 'flower', 'plant', 'grass', 'rock', 'stone']
                    if any(nb in building_name_lower for nb in non_buildings):
                        return None, None

                    # Calculate base position
                    base_x = tile_x - offset_x
                    base_y = tile_y - offset_y

                    return (base_x, base_y), building_name

        return None, None

    def check_player_near_building(self, player_x, player_y, range_tiles=2):
        """Check if player is near any building with an assigned interior"""
        # Player x,y are already in tile coordinates, not pixels!
        player_tile_x = int(player_x)
        player_tile_y = int(player_y)

        # Debug: Print player position occasionally
        import random
        if random.random() < 0.02:  # 2% chance to avoid spam
            print(f"Player at tile ({player_tile_x},{player_tile_y}), checking for buildings...")
            # Also print what we're looking for
            if (abs(player_tile_x - 4) <= 2 and abs(player_tile_y - 1) <= 2) or \
               (abs(player_tile_x - 8) <= 2 and abs(player_tile_y - 11) <= 2):
                print(f"  -> Player is near a building with interior!")

        buildings_found = []
        for dy in range(-range_tiles, range_tiles + 1):
            for dx in range(-range_tiles, range_tiles + 1):
                check_x = player_tile_x + dx
                check_y = player_tile_y + dy

                # Check if there's a building at this position
                # get_building_at_position expects pixel coordinates
                building_pos, building_name = self.get_building_at_position(
                    check_x * TILE_SIZE,
                    check_y * TILE_SIZE
                )

                if building_pos:
                    # Don't add duplicates
                    if (building_pos, building_name) not in buildings_found:
                        buildings_found.append((building_pos, building_name))

                    # Check if this building has an interior assigned
                    pos_key = f"{building_pos[0]},{building_pos[1]}"
                    if pos_key in self.building_interiors:
                        print(f"Found building with interior: {building_name} at {building_pos} -> {self.building_interiors[pos_key]}")
                        return building_pos, building_name, self.building_interiors[pos_key]

        if buildings_found:
            print(f"Found {len(buildings_found)} buildings nearby but none have interiors assigned")
            print(f"Buildings found: {buildings_found}")
            print(f"Available mappings: {self.building_interiors}")

        return None, None, None

    def load_interior_room(self, room_name, building_pos):
        """Load an interior room from file"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        room_file = os.path.join(base_dir, "data", "interiors", "rooms", f"{room_name}.json")

        if os.path.exists(room_file):
            try:
                with open(room_file, 'r') as f:
                    room_data = json.load(f)

                # Check if this room needs narrative features
                if room_name == "foster_home":
                    # Use the narrative-enabled foster home
                    from src.interiors.narratives.foster_home_narrative import FosterHomeNarrative
                    interior = FosterHomeNarrative(self.game, room_data, building_pos)
                elif room_name == "emergency_shelter":
                    # Use the narrative-enabled emergency shelter
                    from src.interiors.narratives.emergency_shelter_narrative import EmergencyShelterNarrative
                    interior = EmergencyShelterNarrative(self.game, room_data, building_pos)
                elif room_name == "library":
                    # Use the narrative-enabled library
                    from src.interiors.narratives.library_narrative import LibraryNarrative
                    interior = LibraryNarrative(self.game, room_data, building_pos)
                elif room_name == "rental_office":
                    # Use the narrative-enabled rental office
                    from src.interiors.narratives.rental_office_narrative import RentalOfficeNarrative
                    interior = RentalOfficeNarrative(self.game, room_data, building_pos)
                elif room_name == "alex_apartment":
                    # Use the narrative-enabled Alex apartment
                    from src.interiors.narratives.alex_apartment_narrative import AlexApartmentNarrative
                    interior = AlexApartmentNarrative(self.game, room_data, building_pos)
                elif room_name == "sarahs_place":
                    # Use the narrative-enabled Sarah's place
                    from src.interiors.narratives.sarahs_place_narrative import SarahsPlaceNarrative
                    interior = SarahsPlaceNarrative(self.game, room_data, building_pos)
                elif room_name == "mike":
                    # Use the narrative-enabled Mike's place
                    from src.interiors.narratives.mikes_place_narrative import MikesPlaceNarrative
                    interior = MikesPlaceNarrative(self.game, room_data, building_pos)
                elif room_name == "grocery_store":
                    # Use the narrative-enabled grocery store
                    from src.interiors.narratives.grocery_store_narrative import GroceryStoreNarrative
                    interior = GroceryStoreNarrative(self.game, room_data, building_pos)
                else:
                    # Create a generic interior handler
                    from src.interiors.generic_interior import GenericInterior
                    interior = GenericInterior(self.game, room_data, building_pos)
                return interior
            except Exception as e:
                print(f"Error loading interior room {room_name}: {e}")
                import traceback
                traceback.print_exc()

        return None

    def enter_building(self, building_pos, building_name, room_name):
        """Enter a building with the specified interior room"""
        print(f"Entering building '{building_name}' at {building_pos} with room '{room_name}'")

        # Load the interior
        interior = self.load_interior_room(room_name, building_pos)
        if interior:
            self.game.current_interior = interior
            interior.enter()
            return True
        else:
            print(f"Failed to load interior room: {room_name}")
            return False
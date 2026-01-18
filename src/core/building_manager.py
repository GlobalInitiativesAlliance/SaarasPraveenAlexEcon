"""
Building Manager - Handles building detection and interior loading.
"""
import json
import os
import time
from typing import Optional, Tuple, Dict, Any, TYPE_CHECKING

from shared.constants import TILE_SIZE
from src.core.debug_logger import debug_logger, dprint
from src.core.room_data_loader import RoomDataLoader
from src.core.scenario_registry import ScenarioRegistry
from src.interiors.generic_interior import GenericInterior
from src.utils.timeout_utils import timeout_operation
from src.utils.room_data_constants import (
    is_non_building_object,
    is_building_tile_type,
)

if TYPE_CHECKING:
    from shared.base_interior import BaseInterior

# Module-level base directory (project root)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class BuildingPositionCache:
    """Handles caching of building positions for O(1) lookup."""

    def __init__(self):
        self._cache: Dict[Tuple[int, int], Dict[str, Any]] = {}

    def build_from_mappings(self, building_interiors: Dict[str, str]):
        """
        Build position cache from building-interior mappings.

        Args:
            building_interiors: Dict mapping "x,y" strings to room names.
        """
        self._cache.clear()

        for pos_key, room_name in building_interiors.items():
            try:
                x, y = map(int, pos_key.split(','))
                self._cache[(x, y)] = {
                    'pos': (x, y),
                    'room_name': room_name
                }
            except (ValueError, AttributeError):
                continue

        dprint(f"[PERF] Cached {len(self._cache)} building positions")

    def get_nearby_building(
        self,
        player_tile_x: int,
        player_tile_y: int,
        range_tiles: int = 2
    ) -> Optional[Dict[str, Any]]:
        """
        Find a building near the player position.

        Args:
            player_tile_x: Player's tile X coordinate.
            player_tile_y: Player's tile Y coordinate.
            range_tiles: Search range in tiles.

        Returns:
            Building data dict if found, None otherwise.
        """
        for (bx, by), building_data in self._cache.items():
            if (abs(player_tile_x - bx) <= range_tiles and
                    abs(player_tile_y - by) <= range_tiles):
                return building_data
        return None

    def clear(self):
        """Clear the position cache."""
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)


class BuildingDetector:
    """Handles detection of buildings at world positions."""

    def __init__(self, game):
        self.game = game

    def get_building_at_position(
        self,
        world_x: float,
        world_y: float
    ) -> Tuple[Optional[Tuple[int, int]], Optional[str]]:
        """
        Check if there's a building at the given world position.

        Args:
            world_x: World X coordinate.
            world_y: World Y coordinate.

        Returns:
            Tuple of (base_position, building_name) or (None, None).
        """
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        if not self._is_within_bounds(tile_x, tile_y):
            return None, None

        tile_data = self.game.city_map.map_data[tile_y][tile_x]
        if not tile_data:
            return None, None

        building_info = self._extract_building_info(tile_data)
        if not building_info:
            return None, None

        building_name, offset_x, offset_y = building_info

        if is_non_building_object(building_name):
            return None, None

        base_x = tile_x - offset_x
        base_y = tile_y - offset_y
        return (base_x, base_y), building_name

    def _is_within_bounds(self, tile_x: int, tile_y: int) -> bool:
        """Check if tile coordinates are within map bounds."""
        return (0 <= tile_x < self.game.city_map.width and
                0 <= tile_y < self.game.city_map.height)

    def _extract_building_info(
        self,
        tile_data: Any
    ) -> Optional[Tuple[str, int, int]]:
        """
        Extract building info from tile data.

        Args:
            tile_data: The tile data (dict or tuple format).

        Returns:
            Tuple of (building_name, offset_x, offset_y) or None.
        """
        if isinstance(tile_data, dict):
            return self._extract_from_dict(tile_data)
        elif isinstance(tile_data, tuple):
            return self._extract_from_tuple(tile_data)
        return None

    def _extract_from_dict(
        self,
        tile_data: Dict[str, Any]
    ) -> Optional[Tuple[str, int, int]]:
        """Extract building info from dict format tile data."""
        tile_type = tile_data.get('type', '')
        if not is_building_tile_type(tile_type):
            return None

        building_name = tile_data.get('building_name', '')
        if not building_name:
            return None

        offset_x = tile_data.get('offset_x', 0)
        offset_y = tile_data.get('offset_y', 0)
        return building_name, offset_x, offset_y

    def _extract_from_tuple(
        self,
        tile_data: tuple
    ) -> Optional[Tuple[str, int, int]]:
        """Extract building info from tuple format tile data."""
        if not tile_data or tile_data[0] not in ['building', 'building_with_bg']:
            return None

        if tile_data[0] == 'building_with_bg':
            _, building_name, offset_x, offset_y, _ = tile_data
        else:
            _, building_name, offset_x, offset_y = tile_data

        return building_name, offset_x, offset_y


class InteriorManager:
    """Handles interior instance creation and cleanup."""

    def __init__(self, game):
        self.game = game
        self.cached_interiors: Dict[str, "BaseInterior"] = {}

    def create_interior(
        self,
        room_name: str,
        room_data: Dict[str, Any],
        building_pos: Tuple[int, int]
    ) -> "BaseInterior":
        """
        Create a scene-specific interior instance.

        Args:
            room_name: Name of the room.
            room_data: The room data from JSON.
            building_pos: Building position tuple.

        Returns:
            Interior instance.
        """
        game_part = self.game.objective_manager.game_part
        interior = ScenarioRegistry.create_interior(
            game_part, building_pos, self.game, room_data
        )

        if interior:
            print(f"[BUILDING_MANAGER] Registry loaded: "
                  f"{interior.__class__.__name__} for {building_pos}")
            return interior

        # Fallback to generic interior
        print(f"[BUILDING_MANAGER] No registry entry for {building_pos} "
              f"in Part {game_part}, using GenericInterior")
        return GenericInterior(self.game, room_data, building_pos)

    def _reset_interior_state(self, interior: "BaseInterior"):
        """
        Reset common interior state attributes.

        Args:
            interior: The interior instance to reset.
        """
        if hasattr(interior, 'active'):
            interior.active = False

        if hasattr(interior, 'dialogue_box') and interior.dialogue_box:
            interior.dialogue_box.hide()

        if hasattr(interior, 'narrative_active'):
            interior.narrative_active = False

    def cleanup_interior(self, interior: Optional["BaseInterior"]):
        """
        Clean up an interior instance.

        Args:
            interior: The interior instance to clean up.
        """
        if not interior:
            return

        self._reset_interior_state(interior)

        if hasattr(interior, 'current_activity'):
            interior.current_activity = None

    def cleanup_cache(self):
        """Clean up all cached interior instances."""
        print("[CLEANUP] Clearing interior cache...")

        for interior in self.cached_interiors.values():
            if interior:
                self._cleanup_cached_interior(interior)

        self.cached_interiors.clear()

    def _cleanup_cached_interior(self, interior: "BaseInterior"):
        """Clean up a single cached interior."""
        self._reset_interior_state(interior)

        if hasattr(interior, 'completed_interactions'):
            interior.completed_interactions.clear()

        if hasattr(interior, 'interactive_objects'):
            interior.interactive_objects.clear()


class BuildingManager:
    """
    Main building manager that orchestrates building detection and interior loading.
    """

    def __init__(self, game):
        self.game = game
        self.building_interiors: Dict[str, str] = {}

        # Initialize sub-components
        self._position_cache = BuildingPositionCache()
        self._detector = BuildingDetector(game)
        self._interior_manager = InteriorManager(game)
        self._room_loader = RoomDataLoader(_BASE_DIR)

        self.load_building_interiors()

        # NOTE: Removed preload_all_rooms() for better Chromebook performance
        # Room JSON data is now loaded on-demand and cached by RoomDataLoader
        # This reduces startup time and memory usage

    def load_building_interiors(self):
        """Load building-interior mappings from file."""
        mappings_file = os.path.join(
            _BASE_DIR, "data", "maps", "building_interiors.json"
        )

        if not os.path.exists(mappings_file):
            print("No building-interior mappings found")
            self.building_interiors = {}
            return

        try:
            with open(mappings_file, 'r') as f:
                self.building_interiors = json.load(f)
            print(f"Loaded {len(self.building_interiors)} building-interior mappings")
            self._position_cache.build_from_mappings(self.building_interiors)
        except Exception as e:
            print(f"Error loading building interiors: {e}")
            self.building_interiors = {}

    def preload_rooms_for_scenario(self, scenario_id: int) -> int:
        """
        Preload room data for a specific scenario (optional optimization).
        Call this when a scenario starts to preload rooms likely to be used.

        Args:
            scenario_id: The scenario number (1-8).

        Returns:
            Number of rooms preloaded.
        """
        # Get rooms used by this scenario from the registry
        scenario_rooms = ScenarioRegistry.get_rooms_for_scenario(scenario_id)
        if scenario_rooms:
            loaded = self._room_loader.preload_rooms(scenario_rooms)
            print(f"[BUILDING_MANAGER] Preloaded {loaded} rooms for scenario {scenario_id}")
            return loaded
        return 0

    def _preload_all_rooms(self):
        """
        Preload all room JSON data (DEPRECATED - use preload_rooms_for_scenario instead).
        This is kept for backwards compatibility but should not be called at startup.
        """
        all_rooms = [
            "alex_apartment", "bad_studio", "bank", "benefits_office",
            "campus_quad", "classroom", "community_center", "courthouse",
            "emergency_shelter", "foster_home", "government_office",
            "grocery_store", "home", "hospital", "housing_office",
            "initial_room", "internet_cafe", "library", "mike",
            "rental", "rental_office", "sarahs_place", "school_counselor_office",
            "social_services_office", "trade_school", "waiting_room"
        ]
        loaded = self._room_loader.preload_rooms(all_rooms)
        print(f"[BUILDING_MANAGER] Preloaded {loaded}/{len(all_rooms)} room data files")
        return loaded

    # Delegate to sub-components while maintaining API compatibility

    def get_building_at_position(
        self,
        world_x: float,
        world_y: float
    ) -> Tuple[Optional[Tuple[int, int]], Optional[str]]:
        """Check if there's a building at the given world position."""
        return self._detector.get_building_at_position(world_x, world_y)

    def check_player_near_building(
        self,
        player_x: float,
        player_y: float,
        range_tiles: int = 2
    ) -> Tuple[Optional[Tuple[int, int]], Optional[str], Optional[str]]:
        """
        Check if player is near any building with an assigned interior.

        Returns:
            Tuple of (building_pos, building_name, room_name) or (None, None, None).
        """
        player_tile_x = int(player_x)
        player_tile_y = int(player_y)

        building_data = self._position_cache.get_nearby_building(
            player_tile_x, player_tile_y, range_tiles
        )

        if not building_data:
            return None, None, None

        room_name = building_data['room_name']
        building_pos = building_data['pos']
        bx, by = building_pos

        # Get building name from map data
        _, building_name = self._detector.get_building_at_position(
            bx * TILE_SIZE, by * TILE_SIZE
        )

        return building_pos, building_name or f"Building_{bx}_{by}", room_name

    def load_interior_room(
        self,
        room_name: str,
        building_pos: Tuple[int, int]
    ) -> Optional["BaseInterior"]:
        """Load an interior room with scene-specific awareness."""
        current_obj = self.game.objective_manager.get_current_objective()
        objective_id = current_obj.id if current_obj else None

        room_data = self._room_loader.get_room_data(room_name, objective_id)
        if not room_data:
            return None

        try:
            return self._interior_manager.create_interior(
                room_name, room_data, building_pos
            )
        except Exception as e:
            print(f"Error loading interior room {room_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_clean_interior_instance(
        self,
        room_name: str,
        building_pos: Tuple[int, int]
    ) -> Optional["BaseInterior"]:
        """Get a fresh, clean interior instance (no caching for scene separation)."""
        return self.load_interior_room(room_name, building_pos)

    @timeout_operation(3.0)
    def enter_building(
        self,
        building_pos: Tuple[int, int],
        building_name: str,
        room_name: str
    ) -> bool:
        """Enter a building with the specified interior room."""
        start_time = time.time()

        current_obj = self.game.objective_manager.get_current_objective()
        objective_id = current_obj.id if current_obj else None

        debug_logger.log_room_entry(room_name, building_pos, objective_id)

        try:
            interior = self.get_clean_interior_instance(room_name, building_pos)

            if not interior:
                error_msg = f"Failed to create interior instance for {room_name}"
                debug_logger.log_room_failure(room_name, error_msg)
                return False

            # Clean up previous interior if any
            if hasattr(self.game, 'current_interior') and self.game.current_interior:
                self.cleanup_current_interior()

            self.game.current_interior = interior
            interior.enter()

            load_time = time.time() - start_time
            debug_logger.log_room_success(room_name, load_time)
            return True

        except Exception as e:
            error_msg = f"Exception during room entry: {str(e)}"
            debug_logger.log_room_failure(room_name, error_msg)
            print(f"Error entering building: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup_current_interior(self):
        """Clean up the current interior instance."""
        if not hasattr(self.game, 'current_interior') or not self.game.current_interior:
            return

        self._interior_manager.cleanup_interior(self.game.current_interior)
        print("[CLEANUP] Current interior cleaned up")

    def cleanup_interior_cache(self):
        """Clean up all cached interior instances."""
        self._interior_manager.cleanup_cache()

    # Legacy API - maintained for backwards compatibility with existing code
    # These delegate to the appropriate sub-components

    @property
    def cached_interiors(self) -> Dict[str, "BaseInterior"]:
        """Access cached interiors (delegates to InteriorManager)."""
        return self._interior_manager.cached_interiors

    @cached_interiors.setter
    def cached_interiors(self, value: Dict[str, "BaseInterior"]):
        """Set cached interiors (delegates to InteriorManager)."""
        self._interior_manager.cached_interiors = value

    @property
    def building_positions_cache(self) -> Dict[Tuple[int, int], Dict[str, Any]]:
        """Access building positions cache (delegates to BuildingPositionCache)."""
        return self._position_cache._cache

    def _build_position_cache(self):
        """Rebuild position cache from current building_interiors mappings."""
        self._position_cache.build_from_mappings(self.building_interiors)

    def get_room_data_for_interior(
        self,
        room_name: str,
        base_dir: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Get room data for an interior.

        Args:
            room_name: Name of the room to load.
            base_dir: Ignored (kept for backwards compatibility).

        Returns:
            Room data dictionary or None if not found.
        """
        current_obj = self.game.objective_manager.get_current_objective()
        objective_id = current_obj.id if current_obj else None
        return self._room_loader.get_room_data(room_name, objective_id)

    def create_scene_specific_interior(
        self,
        room_name: str,
        room_data: Dict[str, Any],
        building_pos: Tuple[int, int]
    ) -> Optional["BaseInterior"]:
        """
        Create a scene-specific interior instance.

        Args:
            room_name: Name of the room.
            room_data: The room data from JSON.
            building_pos: Building position tuple.

        Returns:
            Interior instance or None.
        """
        return self._interior_manager.create_interior(
            room_name, room_data, building_pos
        )

"""
Unit tests for building_manager module and related components.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.room_data_constants import (
    get_room_json_file,
    is_non_building_object,
    is_building_tile_type,
    ROOM_DATA_MAP,
    NON_BUILDING_OBJECTS,
    BUILDING_TILE_TYPES,
)
from src.utils.timeout_utils import timeout_operation
from src.core.room_data_loader import RoomDataLoader
from src.core.building_manager import (
    BuildingPositionCache,
    BuildingDetector,
    InteriorManager,
    BuildingManager,
)


class TestRoomDataConstants(unittest.TestCase):
    """Tests for room_data_constants module."""

    def test_get_room_json_file_mapped_room(self):
        """Test getting JSON file for a mapped room."""
        result = get_room_json_file('foster_home_aging_out')
        self.assertEqual(result, 'foster_home.json')

    def test_get_room_json_file_unmapped_room(self):
        """Test getting JSON file for an unmapped room."""
        result = get_room_json_file('some_new_room')
        self.assertEqual(result, 'some_new_room.json')

    def test_is_non_building_object_tree(self):
        """Test that tree is identified as non-building."""
        self.assertTrue(is_non_building_object('oak_tree'))
        self.assertTrue(is_non_building_object('Tree_Large'))

    def test_is_non_building_object_building(self):
        """Test that buildings are not identified as non-building."""
        self.assertFalse(is_non_building_object('house_1'))
        self.assertFalse(is_non_building_object('apartment_building'))

    def test_is_building_tile_type_valid(self):
        """Test valid building tile types."""
        self.assertTrue(is_building_tile_type('building'))
        self.assertTrue(is_building_tile_type('building_with_bg'))
        self.assertTrue(is_building_tile_type('building_part_with_bg'))

    def test_is_building_tile_type_invalid(self):
        """Test invalid tile types."""
        self.assertFalse(is_building_tile_type('road'))
        self.assertFalse(is_building_tile_type('grass'))
        self.assertFalse(is_building_tile_type(''))

    def test_room_data_map_contains_expected_rooms(self):
        """Test that ROOM_DATA_MAP contains expected entries."""
        self.assertIn('foster_home_aging_out', ROOM_DATA_MAP)
        self.assertIn('classroom', ROOM_DATA_MAP)
        self.assertIn('housing_office', ROOM_DATA_MAP)


class TestTimeoutUtils(unittest.TestCase):
    """Tests for timeout_utils module."""

    def test_timeout_operation_completes(self):
        """Test that operations completing in time return their result."""
        @timeout_operation(1.0)
        def quick_operation():
            return "success"

        result = quick_operation()
        self.assertEqual(result, "success")

    def test_timeout_operation_with_args(self):
        """Test that arguments are passed correctly."""
        @timeout_operation(1.0)
        def add(a, b):
            return a + b

        result = add(2, 3)
        self.assertEqual(result, 5)

    def test_timeout_operation_with_kwargs(self):
        """Test that keyword arguments work."""
        @timeout_operation(1.0)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}"

        result = greet("World", greeting="Hi")
        self.assertEqual(result, "Hi, World")

    def test_timeout_operation_exception_propagates(self):
        """Test that exceptions are propagated."""
        @timeout_operation(1.0)
        def failing_operation():
            raise ValueError("test error")

        with self.assertRaises(ValueError):
            failing_operation()


class TestBuildingPositionCache(unittest.TestCase):
    """Tests for BuildingPositionCache class."""

    def setUp(self):
        self.cache = BuildingPositionCache()

    def test_build_from_mappings(self):
        """Test building cache from mappings."""
        mappings = {
            '4,1': 'initial_room',
            '8,11': 'foster_home',
        }
        self.cache.build_from_mappings(mappings)
        self.assertEqual(len(self.cache), 2)

    def test_build_from_mappings_invalid_key(self):
        """Test that invalid keys are skipped."""
        mappings = {
            '4,1': 'initial_room',
            'invalid': 'some_room',
            'not,a,valid,key': 'another_room',
        }
        self.cache.build_from_mappings(mappings)
        self.assertEqual(len(self.cache), 1)

    def test_get_nearby_building_found(self):
        """Test finding a nearby building."""
        mappings = {'5,5': 'test_room'}
        self.cache.build_from_mappings(mappings)

        result = self.cache.get_nearby_building(6, 6, range_tiles=2)
        self.assertIsNotNone(result)
        self.assertEqual(result['room_name'], 'test_room')

    def test_get_nearby_building_not_found(self):
        """Test when no building is nearby."""
        mappings = {'5,5': 'test_room'}
        self.cache.build_from_mappings(mappings)

        result = self.cache.get_nearby_building(100, 100, range_tiles=2)
        self.assertIsNone(result)

    def test_get_nearby_building_edge_of_range(self):
        """Test finding building at edge of range."""
        mappings = {'5,5': 'test_room'}
        self.cache.build_from_mappings(mappings)

        # Exactly 2 tiles away should be found
        result = self.cache.get_nearby_building(7, 5, range_tiles=2)
        self.assertIsNotNone(result)

        # 3 tiles away should not be found
        result = self.cache.get_nearby_building(8, 5, range_tiles=2)
        self.assertIsNone(result)

    def test_clear(self):
        """Test clearing the cache."""
        mappings = {'5,5': 'test_room'}
        self.cache.build_from_mappings(mappings)
        self.assertEqual(len(self.cache), 1)

        self.cache.clear()
        self.assertEqual(len(self.cache), 0)


class TestBuildingDetector(unittest.TestCase):
    """Tests for BuildingDetector class."""

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.city_map.width = 100
        self.mock_game.city_map.height = 100
        self.mock_game.city_map.map_data = [[None] * 100 for _ in range(100)]
        self.detector = BuildingDetector(self.mock_game)

    def test_get_building_at_position_dict_format(self):
        """Test detection with dict format tile data."""
        self.mock_game.city_map.map_data[5][10] = {
            'type': 'building',
            'building_name': 'house_1',
            'offset_x': 0,
            'offset_y': 0
        }

        # TILE_SIZE is typically 32, so world coords for tile (10,5) would be (320, 160)
        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertEqual(pos, (10, 5))
        self.assertEqual(name, 'house_1')

    def test_get_building_at_position_tuple_format(self):
        """Test detection with tuple format tile data."""
        self.mock_game.city_map.map_data[5][10] = (
            'building', 'old_house', 1, 2
        )

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertEqual(pos, (9, 3))  # base position = tile - offset
        self.assertEqual(name, 'old_house')

    def test_get_building_at_position_non_building_filtered(self):
        """Test that non-building objects are filtered."""
        self.mock_game.city_map.map_data[5][10] = {
            'type': 'building',
            'building_name': 'oak_tree',
            'offset_x': 0,
            'offset_y': 0
        }

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertIsNone(pos)
        self.assertIsNone(name)

    def test_get_building_at_position_out_of_bounds(self):
        """Test detection with out of bounds coordinates."""
        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(-100, -100)

        self.assertIsNone(pos)
        self.assertIsNone(name)

    def test_get_building_at_position_empty_tile(self):
        """Test detection on empty tile."""
        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertIsNone(pos)
        self.assertIsNone(name)


class TestRoomDataLoader(unittest.TestCase):
    """Tests for RoomDataLoader class."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.rooms_dir = os.path.join(self.temp_dir, "data", "interiors", "rooms")
        os.makedirs(self.rooms_dir, exist_ok=True)
        self.loader = RoomDataLoader(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_get_room_data_existing_file(self):
        """Test loading existing room data."""
        room_data = {"width": 20, "height": 15, "doors": []}
        room_file = os.path.join(self.rooms_dir, "test_room.json")
        with open(room_file, 'w') as f:
            json.dump(room_data, f)

        result = self.loader.get_room_data("test_room")
        self.assertEqual(result, room_data)

    def test_get_room_data_caching(self):
        """Test that room data is cached."""
        room_data = {"width": 20, "height": 15}
        room_file = os.path.join(self.rooms_dir, "cached_room.json")
        with open(room_file, 'w') as f:
            json.dump(room_data, f)

        # First load
        result1 = self.loader.get_room_data("cached_room")
        # Modify file
        with open(room_file, 'w') as f:
            json.dump({"width": 100}, f)
        # Second load should return cached data
        result2 = self.loader.get_room_data("cached_room")

        self.assertEqual(result1, result2)
        self.assertEqual(result2["width"], 20)

    def test_get_room_data_nonexistent_file(self):
        """Test loading non-existent room data."""
        result = self.loader.get_room_data("nonexistent_room")
        self.assertIsNone(result)

    def test_get_room_data_invalid_json(self):
        """Test loading invalid JSON."""
        room_file = os.path.join(self.rooms_dir, "invalid.json")
        with open(room_file, 'w') as f:
            f.write("not valid json{{{")

        result = self.loader.get_room_data("invalid")
        self.assertIsNone(result)

    def test_clear_cache(self):
        """Test clearing the cache."""
        room_data = {"width": 20}
        room_file = os.path.join(self.rooms_dir, "to_clear.json")
        with open(room_file, 'w') as f:
            json.dump(room_data, f)

        self.loader.get_room_data("to_clear")
        self.assertIn("to_clear.json", self.loader._cache)

        self.loader.clear_cache()
        self.assertEqual(len(self.loader._cache), 0)

    def test_resolve_json_file_mike_floor_override(self):
        """Test objective-specific override for mike_floor."""
        result = self.loader._resolve_json_file("crappy_apartment", "mike_floor")
        self.assertEqual(result, "mike.json")

    def test_resolve_json_file_no_override(self):
        """Test normal resolution without override."""
        result = self.loader._resolve_json_file("crappy_apartment", None)
        self.assertEqual(result, "bad_studio.json")


class TestInteriorManager(unittest.TestCase):
    """Tests for InteriorManager class."""

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.objective_manager.game_part = 1
        self.manager = InteriorManager(self.mock_game)

    def test_cleanup_interior(self):
        """Test cleaning up an interior instance."""
        mock_interior = MagicMock()
        mock_interior.dialogue_box = MagicMock()
        mock_interior.narrative_active = True
        mock_interior.current_activity = "something"
        mock_interior.active = True

        self.manager.cleanup_interior(mock_interior)

        mock_interior.dialogue_box.hide.assert_called_once()
        self.assertFalse(mock_interior.narrative_active)
        self.assertIsNone(mock_interior.current_activity)
        self.assertFalse(mock_interior.active)

    def test_cleanup_interior_none(self):
        """Test that cleanup handles None gracefully."""
        # Should not raise
        self.manager.cleanup_interior(None)

    def test_cleanup_cache(self):
        """Test cleaning up the interior cache."""
        mock_interior1 = MagicMock()
        mock_interior2 = MagicMock()
        self.manager.cached_interiors = {
            'key1': mock_interior1,
            'key2': mock_interior2,
        }

        self.manager.cleanup_cache()

        self.assertEqual(len(self.manager.cached_interiors), 0)


class TestBuildingManager(unittest.TestCase):
    """Tests for BuildingManager class."""

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.city_map.width = 100
        self.mock_game.city_map.height = 100
        self.mock_game.city_map.map_data = [[None] * 100 for _ in range(100)]
        self.mock_game.objective_manager.game_part = 1
        self.mock_game.objective_manager.get_current_objective.return_value = None
        self.mock_game.current_interior = None

    @patch('src.core.building_manager.os.path.exists')
    @patch('builtins.open', create=True)
    def test_load_building_interiors(self, mock_open, mock_exists):
        """Test loading building interiors from file."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
            '4,1': 'initial_room',
            '8,11': 'foster_home'
        })

        with patch.object(json, 'load', return_value={'4,1': 'initial_room', '8,11': 'foster_home'}):
            manager = BuildingManager(self.mock_game)

        self.assertEqual(len(manager.building_interiors), 2)

    @patch('src.core.building_manager.os.path.exists')
    def test_load_building_interiors_no_file(self, mock_exists):
        """Test behavior when mappings file doesn't exist."""
        mock_exists.return_value = False

        manager = BuildingManager(self.mock_game)

        self.assertEqual(manager.building_interiors, {})

    @patch('src.core.building_manager.os.path.exists')
    @patch('builtins.open', create=True)
    def test_check_player_near_building(self, mock_open, mock_exists):
        """Test checking if player is near a building."""
        mock_exists.return_value = True

        with patch.object(json, 'load', return_value={'5,5': 'test_room'}):
            manager = BuildingManager(self.mock_game)

        # Set up a building at the expected position
        manager.game.city_map.map_data[5][5] = {
            'type': 'building',
            'building_name': 'test_house',
            'offset_x': 0,
            'offset_y': 0
        }

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name, room = manager.check_player_near_building(6, 6, range_tiles=2)

        self.assertEqual(pos, (5, 5))
        self.assertEqual(room, 'test_room')

    @patch('src.core.building_manager.os.path.exists')
    def test_cleanup_current_interior(self, mock_exists):
        """Test cleaning up current interior."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)

        mock_interior = MagicMock()
        manager.game.current_interior = mock_interior

        manager.cleanup_current_interior()

        # Verify cleanup was called on the interior
        self.assertFalse(mock_interior.active)

    @patch('src.core.building_manager.os.path.exists')
    def test_legacy_properties(self, mock_exists):
        """Test legacy compatibility properties."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)

        # Should not raise
        _ = manager.cached_interiors
        _ = manager.building_positions_cache


class TestBuildingDetectorExtended(unittest.TestCase):
    """Extended tests for BuildingDetector class."""

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.city_map.width = 100
        self.mock_game.city_map.height = 100
        self.mock_game.city_map.map_data = [[None] * 100 for _ in range(100)]
        self.detector = BuildingDetector(self.mock_game)

    def test_get_building_at_position_building_with_bg_tuple(self):
        """Test detection with building_with_bg tuple format."""
        # Format: ('building_with_bg', building_name, offset_x, offset_y, bg_type)
        self.mock_game.city_map.map_data[5][10] = (
            'building_with_bg', 'fancy_house', 2, 1, 'grass'
        )

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertEqual(pos, (8, 4))  # base position = tile - offset
        self.assertEqual(name, 'fancy_house')

    def test_get_building_at_position_invalid_tuple_type(self):
        """Test detection with invalid tuple type."""
        self.mock_game.city_map.map_data[5][10] = (
            'road', 'some_road', 0, 0
        )

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertIsNone(pos)
        self.assertIsNone(name)

    def test_get_building_at_position_empty_tuple(self):
        """Test detection with empty tuple."""
        self.mock_game.city_map.map_data[5][10] = ()

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertIsNone(pos)
        self.assertIsNone(name)

    def test_get_building_at_position_dict_non_building_type(self):
        """Test detection with dict that has non-building type."""
        self.mock_game.city_map.map_data[5][10] = {
            'type': 'grass',
            'building_name': 'house_1',
            'offset_x': 0,
            'offset_y': 0
        }

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertIsNone(pos)
        self.assertIsNone(name)

    def test_get_building_at_position_dict_no_building_name(self):
        """Test detection with dict that has no building_name."""
        self.mock_game.city_map.map_data[5][10] = {
            'type': 'building',
            'offset_x': 0,
            'offset_y': 0
        }

        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name = self.detector.get_building_at_position(320, 160)

        self.assertIsNone(pos)
        self.assertIsNone(name)

    def test_is_within_bounds_edge_cases(self):
        """Test boundary checking edge cases."""
        self.assertFalse(self.detector._is_within_bounds(-1, 0))
        self.assertFalse(self.detector._is_within_bounds(0, -1))
        self.assertFalse(self.detector._is_within_bounds(100, 0))
        self.assertFalse(self.detector._is_within_bounds(0, 100))
        self.assertTrue(self.detector._is_within_bounds(0, 0))
        self.assertTrue(self.detector._is_within_bounds(99, 99))


class TestBuildingManagerExtended(unittest.TestCase):
    """Extended tests for BuildingManager class."""

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.city_map.width = 100
        self.mock_game.city_map.height = 100
        self.mock_game.city_map.map_data = [[None] * 100 for _ in range(100)]
        self.mock_game.objective_manager.game_part = 1
        self.mock_game.objective_manager.get_current_objective.return_value = None
        self.mock_game.current_interior = None

    @patch('src.core.building_manager.os.path.exists')
    def test_load_interior_room_returns_none_for_missing_data(self, mock_exists):
        """Test that load_interior_room returns None when room data is missing."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        manager._room_loader.get_room_data = MagicMock(return_value=None)

        result = manager.load_interior_room('nonexistent_room', (5, 5))

        self.assertIsNone(result)

    @patch('src.core.building_manager.os.path.exists')
    def test_load_interior_room_handles_exception(self, mock_exists):
        """Test that load_interior_room handles exceptions gracefully."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        manager._room_loader.get_room_data = MagicMock(return_value={'width': 20})
        manager._interior_manager.create_interior = MagicMock(
            side_effect=Exception("Test error")
        )

        result = manager.load_interior_room('test_room', (5, 5))

        self.assertIsNone(result)

    @patch('src.core.building_manager.os.path.exists')
    def test_get_clean_interior_instance(self, mock_exists):
        """Test get_clean_interior_instance delegates to load_interior_room."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        mock_interior = MagicMock()
        manager.load_interior_room = MagicMock(return_value=mock_interior)

        result = manager.get_clean_interior_instance('test_room', (5, 5))

        manager.load_interior_room.assert_called_once_with('test_room', (5, 5))
        self.assertEqual(result, mock_interior)

    @patch('src.core.building_manager.os.path.exists')
    def test_enter_building_success(self, mock_exists):
        """Test successful building entry."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        mock_interior = MagicMock()
        manager.get_clean_interior_instance = MagicMock(return_value=mock_interior)

        result = manager.enter_building((5, 5), 'test_building', 'test_room')

        self.assertTrue(result)
        self.assertEqual(self.mock_game.current_interior, mock_interior)
        mock_interior.enter.assert_called_once()

    @patch('src.core.building_manager.os.path.exists')
    def test_enter_building_failure_no_interior(self, mock_exists):
        """Test building entry failure when interior creation fails."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        manager.get_clean_interior_instance = MagicMock(return_value=None)

        result = manager.enter_building((5, 5), 'test_building', 'test_room')

        self.assertFalse(result)

    @patch('src.core.building_manager.os.path.exists')
    def test_enter_building_cleans_up_previous_interior(self, mock_exists):
        """Test that entering a building cleans up any previous interior."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        mock_interior = MagicMock()
        old_interior = MagicMock()
        old_interior.active = True
        self.mock_game.current_interior = old_interior

        manager.get_clean_interior_instance = MagicMock(return_value=mock_interior)

        result = manager.enter_building((5, 5), 'test_building', 'test_room')

        self.assertTrue(result)
        # Old interior should have been cleaned up
        self.assertFalse(old_interior.active)

    @patch('src.core.building_manager.os.path.exists')
    def test_enter_building_handles_exception(self, mock_exists):
        """Test that enter_building handles exceptions gracefully."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        manager.get_clean_interior_instance = MagicMock(
            side_effect=Exception("Test error")
        )

        result = manager.enter_building((5, 5), 'test_building', 'test_room')

        self.assertFalse(result)

    @patch('src.core.building_manager.os.path.exists')
    def test_cleanup_current_interior_no_interior(self, mock_exists):
        """Test cleanup when there is no current interior."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        self.mock_game.current_interior = None

        # Should not raise
        manager.cleanup_current_interior()

    @patch('src.core.building_manager.os.path.exists')
    @patch('builtins.open', create=True)
    def test_check_player_near_building_no_building_nearby(self, mock_open, mock_exists):
        """Test checking player position when no building is nearby."""
        mock_exists.return_value = True

        with patch.object(json, 'load', return_value={'50,50': 'test_room'}):
            manager = BuildingManager(self.mock_game)

        pos, name, room = manager.check_player_near_building(0, 0, range_tiles=2)

        self.assertIsNone(pos)
        self.assertIsNone(name)
        self.assertIsNone(room)

    @patch('src.core.building_manager.os.path.exists')
    def test_get_room_data_for_interior_legacy_method(self, mock_exists):
        """Test the legacy get_room_data_for_interior method."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        mock_room_data = {'width': 20}
        manager._room_loader.get_room_data = MagicMock(return_value=mock_room_data)

        result = manager.get_room_data_for_interior('test_room', '/some/path')

        self.assertEqual(result, mock_room_data)

    @patch('src.core.building_manager.os.path.exists')
    def test_create_scene_specific_interior_legacy_method(self, mock_exists):
        """Test the legacy create_scene_specific_interior method."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        mock_interior = MagicMock()
        manager._interior_manager.create_interior = MagicMock(return_value=mock_interior)

        result = manager.create_scene_specific_interior(
            'test_room', {'width': 20}, (5, 5)
        )

        self.assertEqual(result, mock_interior)

    @patch('src.core.building_manager.os.path.exists')
    def test_build_position_cache_legacy_method(self, mock_exists):
        """Test the legacy _build_position_cache method."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        manager.building_interiors = {'10,10': 'test_room'}

        manager._build_position_cache()

        self.assertEqual(len(manager._position_cache), 1)

    @patch('src.core.building_manager.os.path.exists')
    def test_cleanup_interior_cache(self, mock_exists):
        """Test cleanup_interior_cache method."""
        mock_exists.return_value = False
        manager = BuildingManager(self.mock_game)
        mock_interior = MagicMock()
        manager._interior_manager.cached_interiors = {'key': mock_interior}

        manager.cleanup_interior_cache()

        self.assertEqual(len(manager._interior_manager.cached_interiors), 0)


class TestInteriorManagerExtended(unittest.TestCase):
    """Extended tests for InteriorManager class."""

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.objective_manager.game_part = 1
        self.manager = InteriorManager(self.mock_game)

    def test_cleanup_interior_partial_attributes(self):
        """Test cleanup handles interior with only some attributes."""
        mock_interior = MagicMock(spec=['active', 'dialogue_box'])
        mock_interior.dialogue_box = None
        mock_interior.active = True

        # Should not raise even with missing attributes
        self.manager.cleanup_interior(mock_interior)

        self.assertFalse(mock_interior.active)

    def test_cleanup_cached_interior_with_interactions(self):
        """Test cleanup of cached interior with completed_interactions."""
        mock_interior = MagicMock()
        mock_interior.completed_interactions = {'interaction1', 'interaction2'}
        mock_interior.interactive_objects = [MagicMock(), MagicMock()]
        mock_interior.active = True

        self.manager._cleanup_cached_interior(mock_interior)

        self.assertFalse(mock_interior.active)
        self.assertEqual(len(mock_interior.completed_interactions), 0)
        self.assertEqual(len(mock_interior.interactive_objects), 0)

    @patch('src.core.scenario_registry.ScenarioRegistry')
    def test_create_interior_uses_registry(self, mock_registry):
        """Test that create_interior uses ScenarioRegistry."""
        mock_interior = MagicMock()
        mock_registry.create_interior.return_value = mock_interior

        result = self.manager.create_interior(
            'test_room', {'width': 20}, (5, 5)
        )

        mock_registry.create_interior.assert_called_once()
        self.assertEqual(result, mock_interior)

    @patch('src.core.scenario_registry.ScenarioRegistry')
    def test_create_interior_fallback_to_generic(self, mock_registry):
        """Test fallback to GenericInterior when registry returns None."""
        mock_registry.create_interior.return_value = None

        with patch('src.interiors.generic_interior.GenericInterior') as mock_generic:
            mock_generic_instance = MagicMock()
            mock_generic.return_value = mock_generic_instance

            result = self.manager.create_interior(
                'test_room', {'width': 20}, (5, 5)
            )

            mock_generic.assert_called_once()
            self.assertEqual(result, mock_generic_instance)


class TestBuildingPositionCacheExtended(unittest.TestCase):
    """Extended tests for BuildingPositionCache."""

    def setUp(self):
        self.cache = BuildingPositionCache()

    def test_build_from_mappings_with_various_formats(self):
        """Test building cache with various coordinate formats."""
        mappings = {
            '0,0': 'origin_room',
            '99,99': 'far_room',
            '50,25': 'middle_room',
        }
        self.cache.build_from_mappings(mappings)
        self.assertEqual(len(self.cache), 3)

        # Verify all positions are cached correctly
        result = self.cache.get_nearby_building(0, 0, range_tiles=0)
        self.assertEqual(result['room_name'], 'origin_room')

        result = self.cache.get_nearby_building(99, 99, range_tiles=0)
        self.assertEqual(result['room_name'], 'far_room')

    def test_get_nearby_building_multiple_buildings(self):
        """Test finding nearby building when multiple exist."""
        mappings = {
            '5,5': 'room_a',
            '10,10': 'room_b',
        }
        self.cache.build_from_mappings(mappings)

        # Should find closest or first in iteration
        result = self.cache.get_nearby_building(6, 6, range_tiles=2)
        self.assertIsNotNone(result)

    def test_get_nearby_building_zero_range(self):
        """Test finding building with zero range (exact match only)."""
        mappings = {'5,5': 'test_room'}
        self.cache.build_from_mappings(mappings)

        # Exact match
        result = self.cache.get_nearby_building(5, 5, range_tiles=0)
        self.assertIsNotNone(result)

        # One tile away, should not match
        result = self.cache.get_nearby_building(6, 5, range_tiles=0)
        self.assertIsNone(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the building manager system."""

    def test_full_flow_position_cache_to_detection(self):
        """Test the flow from position cache to building detection."""
        cache = BuildingPositionCache()
        cache.build_from_mappings({'10,10': 'test_interior'})

        # Simulate player near building
        result = cache.get_nearby_building(11, 11, range_tiles=2)
        self.assertIsNotNone(result)
        self.assertEqual(result['room_name'], 'test_interior')
        self.assertEqual(result['pos'], (10, 10))

    def test_building_manager_full_workflow(self):
        """Test complete workflow from building detection to entry."""
        mock_game = MagicMock()
        mock_game.city_map.width = 100
        mock_game.city_map.height = 100
        mock_game.city_map.map_data = [[None] * 100 for _ in range(100)]
        mock_game.objective_manager.game_part = 1
        mock_game.objective_manager.get_current_objective.return_value = None
        mock_game.current_interior = None

        # Set up a building at position (10, 10)
        mock_game.city_map.map_data[10][10] = {
            'type': 'building',
            'building_name': 'test_house',
            'offset_x': 0,
            'offset_y': 0
        }

        with patch('src.core.building_manager.os.path.exists', return_value=True):
            with patch.object(json, 'load', return_value={'10,10': 'test_room'}):
                manager = BuildingManager(mock_game)

        # Check player is near building
        with patch('src.core.building_manager.TILE_SIZE', 32):
            pos, name, room = manager.check_player_near_building(11, 11, range_tiles=2)

        self.assertEqual(pos, (10, 10))
        self.assertEqual(room, 'test_room')


if __name__ == '__main__':
    unittest.main()

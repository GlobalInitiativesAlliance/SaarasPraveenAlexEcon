"""
Room Data Loader - Handles loading and caching of interior room data.
"""
import json
import os
from typing import Optional, Dict, Any

from src.utils.room_data_constants import get_room_json_file


class RoomDataLoader:
    """Handles loading and caching of room data from JSON files."""

    def __init__(self, base_dir: str):
        """
        Initialize the room data loader.

        Args:
            base_dir: The base directory of the project.
        """
        self.base_dir = base_dir
        self.rooms_dir = os.path.join(base_dir, "data", "interiors", "rooms")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_room_data(
        self,
        room_name: str,
        objective_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get room data for the specified room.

        Args:
            room_name: The name of the room to load.
            objective_id: Optional objective ID for objective-specific overrides.

        Returns:
            The room data dictionary, or None if not found.
        """
        json_file = self._resolve_json_file(room_name, objective_id)
        return self._load_json_file(json_file)

    def _resolve_json_file(
        self,
        room_name: str,
        objective_id: Optional[str] = None
    ) -> str:
        """
        Resolve the JSON file to load for a room.

        Args:
            room_name: The name of the room.
            objective_id: Optional objective ID for overrides.

        Returns:
            The JSON filename to load.
        """
        # Check for objective-specific room overrides
        if objective_id == "mike_floor" and room_name == "crappy_apartment":
            return "mike.json"

        return get_room_json_file(room_name)

    def _load_json_file(self, json_file: str) -> Optional[Dict[str, Any]]:
        """
        Load a JSON file, using cache if available.

        Args:
            json_file: The JSON filename to load.

        Returns:
            The parsed JSON data, or None if not found.
        """
        # Check cache first
        if json_file in self._cache:
            return self._cache[json_file]

        room_file = os.path.join(self.rooms_dir, json_file)

        if not os.path.exists(room_file):
            print(f"Room data file not found: {room_file}")
            return None

        try:
            with open(room_file, 'r') as f:
                room_data = json.load(f)
                self._cache[json_file] = room_data
                return room_data
        except json.JSONDecodeError as e:
            print(f"Error parsing room data from {room_file}: {e}")
            return None
        except Exception as e:
            print(f"Error loading room data from {room_file}: {e}")
            return None

    def clear_cache(self):
        """Clear the room data cache."""
        self._cache.clear()

    def preload_rooms(self, room_names: list) -> int:
        """
        Preload multiple rooms into cache.

        Args:
            room_names: List of room names to preload.

        Returns:
            Number of rooms successfully loaded.
        """
        loaded = 0
        for room_name in room_names:
            if self.get_room_data(room_name) is not None:
                loaded += 1
        return loaded

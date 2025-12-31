"""
Scenario Registry - Loads and manages scenario-building mappings from JSON.
Provides clean routing and startup validation.

This replaces the 400+ lines of if/elif chains in building_manager.py with
a simple dictionary lookup. Each scenario explicitly declares its buildings,
preventing bleeding between scenarios.
"""

import json
import importlib
from pathlib import Path
from typing import Dict, Tuple, Optional, List


class ScenarioRegistryError(Exception):
    """Raised when scenario registry validation fails"""
    pass


class ScenarioRegistry:
    """
    Loads scenario configuration from JSON and provides:
    - Interior class lookup by (game_part, position)
    - Startup validation that blocks on mismatches
    """

    # Class-level registry storage
    _registry: Dict[int, Dict[Tuple[int, int], dict]] = {}
    _loaded = False

    @classmethod
    def load(cls, config_path: str = None):
        """Load registry from JSON file"""
        if cls._loaded:
            return

        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "data" / "scenario_registry.json"

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"[REGISTRY] Warning: {config_path} not found, using empty registry")
            cls._loaded = True
            return
        except json.JSONDecodeError as e:
            print(f"[REGISTRY] Error parsing {config_path}: {e}")
            cls._loaded = True
            return

        cls._registry = {}
        scenario_count = 0
        building_count = 0

        for game_part_str, scenario_data in data.get("scenarios", {}).items():
            game_part = int(game_part_str)
            cls._registry[game_part] = {}
            scenario_count += 1

            for pos_str, building_config in scenario_data.get("buildings", {}).items():
                x, y = map(int, pos_str.split(","))
                cls._registry[game_part][(x, y)] = building_config
                building_count += 1

        cls._loaded = True
        print(f"[REGISTRY] Loaded {scenario_count} scenarios, {building_count} buildings from {config_path}")

    @classmethod
    def get_interior_config(cls, game_part: int, position: Tuple[int, int]) -> Optional[dict]:
        """Get interior config for a game_part and position"""
        if not cls._loaded:
            cls.load()

        if game_part in cls._registry:
            return cls._registry[game_part].get(position)
        return None

    @classmethod
    def create_interior(cls, game_part: int, position: Tuple[int, int], game, room_data):
        """
        Create interior instance from registry config.
        Returns None if no config found (caller should use fallback).
        """
        config = cls.get_interior_config(game_part, position)

        if not config:
            return None

        try:
            # Dynamic import of interior class
            interior_path = config["interior"]
            module_path, class_name = interior_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            interior_class = getattr(module, class_name)

            return interior_class(game, room_data, position)

        except (ImportError, AttributeError) as e:
            print(f"[REGISTRY] Failed to load interior {config['interior']}: {e}")
            return None

    @classmethod
    def get_registered_positions(cls, game_part: int) -> List[Tuple[int, int]]:
        """Get all positions registered for a game_part"""
        if not cls._loaded:
            cls.load()

        if game_part in cls._registry:
            return list(cls._registry[game_part].keys())
        return []

    @classmethod
    def get_objectives_for_position(cls, game_part: int, position: Tuple[int, int]) -> List[str]:
        """Get list of objectives handled at a specific position"""
        config = cls.get_interior_config(game_part, position)
        if config:
            return config.get("objectives", [])
        return []

    @classmethod
    def validate_objectives(cls, game_part: int, objectives: List) -> List[str]:
        """
        Validate all objective positions have registered buildings.
        Returns list of error messages (empty if valid).
        """
        if not cls._loaded:
            cls.load()

        errors = []

        if game_part not in cls._registry:
            errors.append(f"No buildings registered for game_part {game_part} (Part {game_part + 1})")
            return errors

        registered = set(cls._registry[game_part].keys())

        for obj in objectives:
            pos = obj.target_position
            if pos not in registered:
                errors.append(
                    f"POSITION MISMATCH: Objective '{obj.id}' targets {pos} "
                    f"but no building registered there for Part {game_part + 1}"
                )

        return errors

    @classmethod
    def validate_or_fail(cls, game_part: int, objectives: List):
        """
        Validate objectives and BLOCK startup if any mismatches.
        Raises ScenarioRegistryError if validation fails.
        """
        errors = cls.validate_objectives(game_part, objectives)

        if errors:
            print("\n" + "=" * 60)
            print("FATAL: Scenario Registry Validation Failed!")
            print("=" * 60)
            for error in errors:
                print(f"  - {error}")
            print("=" * 60)
            print("Fix objective positions or update data/scenario_registry.json")
            print("=" * 60 + "\n")
            raise ScenarioRegistryError(
                f"Validation failed with {len(errors)} position mismatch(es)"
            )

        print(f"[REGISTRY] Validated {len(objectives)} objectives for Part {game_part + 1}")

    @classmethod
    def get_scenario_name(cls, game_part: int) -> str:
        """Get the human-readable name for a scenario"""
        if not cls._loaded:
            cls.load()

        # Load from JSON to get name
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "data" / "scenario_registry.json"

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                scenario = data.get("scenarios", {}).get(str(game_part), {})
                return scenario.get("name", f"Part {game_part + 1}")
        except:
            return f"Part {game_part + 1}"

    @classmethod
    def clear(cls):
        """Clear registry (for testing)"""
        cls._registry = {}
        cls._loaded = False

    @classmethod
    def is_loaded(cls) -> bool:
        """Check if registry is loaded"""
        return cls._loaded

    @classmethod
    def get_all_scenarios(cls) -> Dict[int, str]:
        """Get all registered scenarios with their names"""
        if not cls._loaded:
            cls.load()

        return {gp: cls.get_scenario_name(gp) for gp in cls._registry.keys()}

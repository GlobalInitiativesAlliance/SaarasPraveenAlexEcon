"""
Game State API - Clean JSON-serializable game state export
Provides computer-readable game state for external monitoring and debugging
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

class GameStateAPI:
    """Clean API for game state export and monitoring"""

    def __init__(self, game):
        self.game = game
        self.export_enabled = False
        self.export_interval = 1.0
        self.export_thread = None
        self.state_file = "current_state.json"

    def get_full_state(self):
        """Get complete game state as JSON-serializable dict"""
        try:
            # Get current objective
            current_obj = None
            if hasattr(self.game, 'objective_manager') and self.game.objective_manager:
                current_obj = self.game.objective_manager.get_current_objective()

            # Get player info
            player_pos = (0, 0)
            if hasattr(self.game, 'player') and self.game.player:
                player_pos = (int(self.game.player.x), int(self.game.player.y))

            # Get location info
            interior_name = None
            building_pos = None
            activity_name = None

            if hasattr(self.game, 'current_interior') and self.game.current_interior:
                interior_name = self.game.current_interior.__class__.__name__
                building_pos = getattr(self.game.current_interior, 'building_pos', None)

            if (hasattr(self.game, 'objective_manager') and
                hasattr(self.game.objective_manager, 'current_activity') and
                self.game.objective_manager.current_activity):
                activity_name = self.game.objective_manager.current_activity.__class__.__name__

            # Build state dict
            state = {
                "timestamp": datetime.now().isoformat(),
                "game_info": {
                    "version": "2.0",
                    "running": True,
                    "debug_mode": True
                },
                "game_part": getattr(self.game.objective_manager, 'game_part', 1) if hasattr(self.game, 'objective_manager') else 1,
                "current_objective": {
                    "id": current_obj.id if current_obj else None,
                    "title": current_obj.title if current_obj else None,
                    "description": current_obj.description if current_obj else None,
                    "position": list(current_obj.position) if current_obj and hasattr(current_obj, 'position') else None,
                    "index": getattr(self.game.objective_manager, 'current_objective_index', 0) if hasattr(self.game, 'objective_manager') else 0
                },
                "player": {
                    "position": list(player_pos),
                    "money": getattr(self.game.objective_manager, 'player_money', 0.0) if hasattr(self.game, 'objective_manager') else 0.0,
                    "health": 100  # Default health
                },
                "location": {
                    "current_interior": interior_name,
                    "building_pos": list(building_pos) if building_pos else None,
                    "activity": activity_name,
                    "on_map": interior_name is None
                },
                "progress": {
                    "objectives_completed": getattr(self.game.objective_manager, 'current_objective_index', 0) if hasattr(self.game, 'objective_manager') else 0,
                    "total_objectives": len(getattr(self.game.objective_manager, 'objectives', [])) if hasattr(self.game, 'objective_manager') else 0,
                    "completion_percentage": 0.0
                },
                "available_actions": self._get_available_actions(),
                "scene_map": self._get_scene_map()
            }

            # Calculate completion percentage
            if state["progress"]["total_objectives"] > 0:
                state["progress"]["completion_percentage"] = (
                    state["progress"]["objectives_completed"] / state["progress"]["total_objectives"] * 100
                )

            return state

        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Failed to get game state: {str(e)}",
                "game_info": {"running": False, "error": True}
            }

    def _get_available_actions(self):
        """Get list of available actions player can take"""
        actions = []

        if hasattr(self.game, 'objective_manager') and self.game.objective_manager:
            # Can always skip to next objective (debug)
            actions.append("skip_objective")

            # Can skip to next part
            if self.game.objective_manager.game_part < 6:
                actions.append("skip_to_next_part")

        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            actions.append("exit_interior")
        else:
            actions.append("move_on_map")

        return actions

    def _get_scene_map(self):
        """Get available scenes to jump to"""
        return {
            "burger_rush": {
                "name": "Burger Rush Mini-Game",
                "part": 2,
                "objective": "work_day_anxiety",
                "position": [39, 51],
                "description": "Play the fixed burger cooking game"
            },
            "doctor": {
                "name": "Doctor Appointment",
                "part": 2,
                "objective": "doctor_appointment",
                "position": [34, 31],
                "description": "Visit the clinic for healthcare"
            },
            "therapist": {
                "name": "Therapist Call",
                "part": 2,
                "objective": "therapist_call",
                "description": "Make therapy appointment call"
            },
            "part2_start": {
                "name": "Part 2 Beginning",
                "part": 2,
                "objective": "healthcare_intro",
                "description": "Start of healthcare access storyline"
            }
        }

    def save_state(self, filename=None):
        """Save current state to JSON file"""
        if filename is None:
            filename = self.state_file

        state = self.get_full_state()

        try:
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"[STATE_API] Failed to save state: {e}")
            return False

    def enable_continuous_export(self, interval=1.0):
        """Enable continuous state export for monitoring"""
        self.export_enabled = True
        self.export_interval = interval

        if self.export_thread is None or not self.export_thread.is_alive():
            self.export_thread = threading.Thread(target=self._export_loop, daemon=True)
            self.export_thread.start()
            print(f"[STATE_API] Continuous export enabled (interval: {interval}s)")

    def disable_continuous_export(self):
        """Disable continuous state export"""
        self.export_enabled = False
        print("[STATE_API] Continuous export disabled")

    def _export_loop(self):
        """Background thread for continuous state export"""
        while self.export_enabled:
            try:
                self.save_state()
                time.sleep(self.export_interval)
            except Exception as e:
                print(f"[STATE_API] Export error: {e}")
                time.sleep(self.export_interval)

    def get_state_summary(self):
        """Get brief state summary for display"""
        state = self.get_full_state()

        if "error" in state:
            return f"ERROR: {state['error']}"

        obj = state["current_objective"]
        location = state["location"]

        summary_parts = []
        summary_parts.append(f"Part {state['game_part']}")

        if obj["id"]:
            summary_parts.append(f"Objective: {obj['id']}")

        if location["activity"]:
            summary_parts.append(f"Activity: {location['activity']}")
        elif location["current_interior"]:
            summary_parts.append(f"Interior: {location['current_interior']}")
        else:
            summary_parts.append("On Map")

        return " | ".join(summary_parts)

    def export_debug_info(self):
        """Export comprehensive debug information"""
        debug_info = {
            "state": self.get_full_state(),
            "objective_manager": self._serialize_objective_manager(),
            "game_objects": self._serialize_game_objects(),
            "debug_logs": self._get_recent_debug_logs()
        }

        debug_file = f"debug_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(debug_file, 'w') as f:
                json.dump(debug_info, f, indent=2, default=str)
            print(f"[STATE_API] Debug info exported to {debug_file}")
            return debug_file
        except Exception as e:
            print(f"[STATE_API] Failed to export debug info: {e}")
            return None

    def _serialize_objective_manager(self):
        """Serialize objective manager state"""
        if not hasattr(self.game, 'objective_manager'):
            return None

        om = self.game.objective_manager

        return {
            "current_index": getattr(om, 'current_objective_index', 0),
            "game_part": getattr(om, 'game_part', 1),
            "total_objectives": len(getattr(om, 'objectives', [])),
            "current_activity": om.current_activity.__class__.__name__ if hasattr(om, 'current_activity') and om.current_activity else None,
            "player_money": getattr(om, 'player_money', 0.0)
        }

    def _serialize_game_objects(self):
        """Serialize key game objects"""
        objects = {}

        if hasattr(self.game, 'player'):
            objects["player"] = {
                "position": (self.game.player.x, self.game.player.y),
                "class": self.game.player.__class__.__name__
            }

        if hasattr(self.game, 'current_interior'):
            objects["interior"] = {
                "class": self.game.current_interior.__class__.__name__ if self.game.current_interior else None,
                "active": bool(self.game.current_interior)
            }

        return objects

    def _get_recent_debug_logs(self):
        """Get recent debug log entries if available"""
        try:
            from src.core.debug_logger import debug_logger
            return debug_logger.get_recent_entries(10)
        except:
            return []
"""
Progress Manager - Persistent save system for tracking game progress across sessions.
Handles scenario unlocking, objective completion tracking, and save/load functionality.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def load_scenario_objectives(scenario_id):
    """Load the actual objectives for a scenario from the game files

    Note: Folder names don't match scenario IDs due to renumbering:
    - Scenario 1 = part_1_housing_stability
    - Scenario 2 = part_3_legal_system (was Part 3)
    - Scenario 3 = part_4_healthcare (was Part 4)
    - Scenario 4 = part_5_education (was Part 5)
    - Scenario 5 = part_6_systemic_barriers (was Part 6)
    - Scenario 6 = part_7_behavioral (was Part 7)
    """
    objectives = []

    try:
        if scenario_id == 1:
            from part_1_housing_stability.objectives_narrative import get_part1_narrative_objectives
            objs = get_part1_narrative_objectives()
        elif scenario_id == 2:
            from part_3_legal_system.objectives import get_part3_objectives
            objs = get_part3_objectives()
        elif scenario_id == 3:
            from part_4_healthcare.objectives import get_part4_objectives
            objs = get_part4_objectives()
        elif scenario_id == 4:
            from part_5_education.objectives import get_part5_objectives
            objs = get_part5_objectives()
        elif scenario_id == 5:
            from part_6_systemic_barriers.objectives import get_part6_objectives
            objs = get_part6_objectives()
        elif scenario_id == 6:
            from part_7_behavioral.objectives import get_part7_objectives
            objs = get_part7_objectives()
        else:
            objs = []

        for obj in objs:
            objectives.append({
                "id": obj.id,
                "title": obj.title,
                "description": obj.description
            })
    except ImportError as e:
        print(f"Could not load objectives for scenario {scenario_id}: {e}")
    except Exception as e:
        print(f"Error loading objectives for scenario {scenario_id}: {e}")

    return objectives


class ProgressManager:
    """Manages persistent game progress and scenario unlocking"""

    SAVE_FILE = "game_progress.json"

    # Scenario definitions with their objectives
    SCENARIOS = {
        1: {
            "id": "housing_stability",
            "title": "Housing Stability",
            "subtitle": "Aging out of foster care",
            "description": "Navigate the challenges of finding stable housing after aging out of foster care at 18.",
            "objectives_count": 30,
            "unlock_requirement": None,  # Always unlocked
            "key_objectives": [
                "Aging out of foster care",
                "Find emergency shelter",
                "Search for housing",
                "Navigate rental barriers",
                "Find roommate situation",
                "Handle eviction crisis",
                "Explore transitional housing"
            ]
        },
        2: {
            "id": "legal_system",
            "title": "Legal System",
            "subtitle": "Understanding court and legal processes",
            "description": "Experience the complexity of the legal system when facing court dates while juggling work and school.",
            "objectives_count": 25,
            "unlock_requirement": {"scenario": 1, "min_completion": 50},
            "key_objectives": [
                "Receive court notice",
                "Balance work schedule",
                "Navigate government offices",
                "Handle warrant situation",
                "Understand legal rights"
            ]
        },
        3: {
            "id": "healthcare_crisis",
            "title": "Healthcare Crisis",
            "subtitle": "Accessing medical care without support",
            "description": "Face the barriers to healthcare access including insurance, transportation, and cost.",
            "objectives_count": 20,
            "unlock_requirement": {"scenario": 2, "min_completion": 50},
            "key_objectives": [
                "Handle health emergency",
                "Navigate insurance barriers",
                "Find transportation to clinic",
                "Afford medication costs",
                "Access mental health support"
            ]
        },
        4: {
            "id": "education_journey",
            "title": "Education Journey",
            "subtitle": "Pursuing education against the odds",
            "description": "Try to continue education while managing housing instability and financial pressures.",
            "objectives_count": 15,
            "unlock_requirement": {"scenario": 3, "min_completion": 50},
            "key_objectives": [
                "Apply for financial aid",
                "Navigate FAFSA process",
                "Balance work and classes",
                "Handle academic challenges"
            ]
        },
        5: {
            "id": "systemic_barriers",
            "title": "Systemic Barriers",
            "subtitle": "Breaking the cycle",
            "description": "Confront the interconnected systemic barriers that create cycles of poverty and instability.",
            "objectives_count": 21,
            "unlock_requirement": {"scenario": 4, "min_completion": 50},
            "key_objectives": [
                "Understand interconnected barriers",
                "Navigate multiple systems",
                "Build support network",
                "Plan for stability"
            ]
        },
        6: {
            "id": "behavioral_emotional",
            "title": "Survival Strategies",
            "subtitle": "Managing the emotional toll",
            "description": "Navigate the behavioral and emotional challenges of survival mode - budgeting stress, work conflicts, and decision paralysis.",
            "objectives_count": 20,
            "unlock_requirement": {"scenario": 5, "min_completion": 50},
            "key_objectives": [
                "Pay bills on limited income",
                "Make spending decisions",
                "Handle manager conflicts",
                "Prioritize overwhelming tasks",
                "Make food budget choices"
            ]
        }
    }

    def __init__(self):
        self.save_path = self._get_save_path()
        self.progress_data = self._load_progress()

    def _get_save_path(self):
        """Get the save file path in the project directory"""
        # Save in project data directory
        project_root = Path(__file__).parent.parent.parent
        save_dir = project_root / "data" / "saves"
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir / self.SAVE_FILE

    def _get_default_progress(self):
        """Return default progress structure"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "scenarios": {
                str(i): {
                    "unlocked": i == 1,  # Only first scenario unlocked by default
                    "started": False,
                    "completed": False,
                    "objectives_completed": 0,
                    "total_objectives": self.SCENARIOS[i]["objectives_count"],
                    "completion_percentage": 0.0,
                    "last_objective_id": None,
                    "play_time_seconds": 0
                }
                for i in range(1, 7)
            },
            "total_play_time_seconds": 0,
            "achievements": []
        }

    def _load_progress(self):
        """Load progress from save file or create new"""
        if self.save_path.exists():
            try:
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                    # Validate and migrate if needed
                    return self._migrate_progress(data)
            except (json.JSONDecodeError, KeyError):
                print("Corrupted save file, creating new progress")
                return self._get_default_progress()
        return self._get_default_progress()

    def _migrate_progress(self, data):
        """Migrate old save formats to current version"""
        # Ensure all required fields exist
        default = self._get_default_progress()

        if "scenarios" not in data:
            data["scenarios"] = default["scenarios"]

        # Add any missing scenarios
        for scenario_id in range(1, 7):
            str_id = str(scenario_id)
            if str_id not in data["scenarios"]:
                data["scenarios"][str_id] = default["scenarios"][str_id]
            else:
                # Ensure all fields exist
                for key, value in default["scenarios"][str_id].items():
                    if key not in data["scenarios"][str_id]:
                        data["scenarios"][str_id][key] = value

        return data

    def save_progress(self):
        """Save current progress to file"""
        self.progress_data["last_played"] = datetime.now().isoformat()
        try:
            with open(self.save_path, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except IOError as e:
            print(f"Failed to save progress: {e}")

    def is_scenario_unlocked(self, scenario_id):
        """Check if a scenario is unlocked"""
        str_id = str(scenario_id)
        if str_id in self.progress_data["scenarios"]:
            return self.progress_data["scenarios"][str_id]["unlocked"]
        return scenario_id == 1  # First scenario always unlocked

    def get_scenario_progress(self, scenario_id):
        """Get progress data for a specific scenario"""
        str_id = str(scenario_id)
        if str_id in self.progress_data["scenarios"]:
            return self.progress_data["scenarios"][str_id]
        return None

    def get_scenario_info(self, scenario_id):
        """Get static scenario info combined with progress"""
        if scenario_id not in self.SCENARIOS:
            return None

        info = self.SCENARIOS[scenario_id].copy()
        progress = self.get_scenario_progress(scenario_id)

        if progress:
            info["unlocked"] = progress["unlocked"]
            info["started"] = progress["started"]
            info["completed"] = progress["completed"]
            info["objectives_completed"] = progress["objectives_completed"]
            info["completion_percentage"] = progress["completion_percentage"]
        else:
            info["unlocked"] = scenario_id == 1
            info["started"] = False
            info["completed"] = False
            info["objectives_completed"] = 0
            info["completion_percentage"] = 0.0

        return info

    def update_scenario_progress(self, scenario_id, objectives_completed, total_objectives=None, objective_id=None):
        """Update progress for a scenario"""
        str_id = str(scenario_id)

        if str_id not in self.progress_data["scenarios"]:
            return

        scenario = self.progress_data["scenarios"][str_id]
        scenario["started"] = True
        scenario["objectives_completed"] = objectives_completed

        # Store the current objective index for resume functionality
        scenario["last_objective_index"] = objectives_completed

        if objective_id:
            scenario["last_objective_id"] = objective_id

        if total_objectives:
            scenario["total_objectives"] = total_objectives

        total = scenario["total_objectives"]
        if total > 0:
            scenario["completion_percentage"] = (objectives_completed / total) * 100

        # Check if completed
        if objectives_completed >= total:
            scenario["completed"] = True
            self._check_unlock_next_scenario(scenario_id)

        self.save_progress()

    def get_resume_info(self, scenario_id):
        """Get information needed to resume a scenario from saved progress"""
        str_id = str(scenario_id)
        if str_id not in self.progress_data["scenarios"]:
            return None

        scenario = self.progress_data["scenarios"][str_id]
        if not scenario.get("started"):
            return None

        return {
            "scenario_id": scenario_id,
            "objective_index": scenario.get("last_objective_index", 0),
            "objective_id": scenario.get("last_objective_id"),
            "objectives_completed": scenario.get("objectives_completed", 0),
            "completion_percentage": scenario.get("completion_percentage", 0)
        }

    def can_resume_scenario(self, scenario_id):
        """Check if a scenario can be resumed (has saved progress)"""
        resume_info = self.get_resume_info(scenario_id)
        return resume_info is not None and resume_info["objective_index"] > 0

    def get_last_played_scenario(self):
        """Get the scenario that was most recently played"""
        last_scenario = None
        for scenario_id in range(1, 7):
            str_id = str(scenario_id)
            if str_id in self.progress_data["scenarios"]:
                scenario = self.progress_data["scenarios"][str_id]
                if scenario.get("started") and not scenario.get("completed"):
                    last_scenario = scenario_id
        return last_scenario

    def _check_unlock_next_scenario(self, completed_scenario_id):
        """Check if completing a scenario unlocks the next one"""
        for scenario_id, info in self.SCENARIOS.items():
            req = info.get("unlock_requirement")
            if req and req.get("scenario") == completed_scenario_id:
                completed_progress = self.get_scenario_progress(completed_scenario_id)
                if completed_progress:
                    completion = completed_progress["completion_percentage"]
                    if completion >= req.get("min_completion", 100):
                        self.unlock_scenario(scenario_id)

    def unlock_scenario(self, scenario_id):
        """Unlock a specific scenario"""
        str_id = str(scenario_id)
        if str_id in self.progress_data["scenarios"]:
            self.progress_data["scenarios"][str_id]["unlocked"] = True
            self.save_progress()

    def mark_scenario_started(self, scenario_id):
        """Mark a scenario as started"""
        str_id = str(scenario_id)
        if str_id in self.progress_data["scenarios"]:
            self.progress_data["scenarios"][str_id]["started"] = True
            self.save_progress()

    def get_all_scenarios_with_progress(self):
        """Get all scenarios with their progress data"""
        scenarios = []
        for scenario_id in sorted(self.SCENARIOS.keys()):
            info = self.get_scenario_info(scenario_id)
            info["scenario_id"] = scenario_id
            scenarios.append(info)
        return scenarios

    def reset_progress(self):
        """Reset all progress (for testing or new game)"""
        self.progress_data = self._get_default_progress()
        self.save_progress()

    def unlock_all_scenarios(self):
        """Unlock all scenarios (debug function)"""
        for scenario_id in range(1, 7):
            self.unlock_scenario(scenario_id)

    def get_unlock_status_message(self, scenario_id):
        """Get a message about what's needed to unlock a scenario"""
        info = self.SCENARIOS.get(scenario_id)
        if not info:
            return "Unknown scenario"

        req = info.get("unlock_requirement")
        if not req:
            return "Always available"

        req_scenario = req.get("scenario")
        min_completion = req.get("min_completion", 100)
        req_scenario_name = self.SCENARIOS.get(req_scenario, {}).get("title", f"Part {req_scenario}")

        return f"Complete {min_completion}% of {req_scenario_name} to unlock"


# Global instance for easy access
_progress_manager = None

def get_progress_manager():
    """Get or create the global progress manager instance"""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    return _progress_manager

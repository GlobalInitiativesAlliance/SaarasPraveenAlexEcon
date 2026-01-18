"""
Lazy Activity Loader - Loads activities on-demand to reduce initial memory footprint.
This prevents loading all 17,000+ lines of activity code at startup.
"""

import importlib
import gc
from typing import Dict, Optional, Any


class LazyActivityLoader:
    """Load activities only when needed to reduce memory usage"""

    def __init__(self):
        """Initialize the lazy activity loader"""
        self._loaded_activities = {}
        self._activity_instances = {}

        # Map activity class names to their module paths
        self._activity_modules = {
            # From activities.py (large monolithic file)
            'TenantRightsQuiz': 'src.activities.activities',
            'ClothesPacking': 'src.activities.activities',
            'PackingActivity': 'src.activities.activities',
            'LifeSkillsWorkshop': 'src.activities.activities',
            'EmergencyNoticeActivity': 'src.activities.activities',
            'DocumentChecklistActivity': 'src.activities.activities',
            'WorkplaceQuiz': 'src.activities.activities',
            'JobApplicationActivity': 'src.activities.activities',
            'TransitionScene': 'src.activities.activities',
            'SchoolEmergencyScene': 'src.activities.activities',
            'FiringScene': 'src.activities.activities',
            'PizzaMakingGame': 'src.activities.activities',
            'BurgerMakingGame': 'src.activities.activities',
            'DocumentChecklistWork': 'src.activities.activities',
            'BurgerTrainingActivity': 'src.activities.activities',
            'JobListingsActivity': 'src.activities.activities',
            'ManagerNoticeActivity': 'src.activities.activities',
            'PanicSceneActivity': 'src.activities.activities',

            # Standalone activity files
            'ERWaitingRoom': 'src.activities.er_waiting',
            'TextDesperation': 'src.activities.text_desperation',
            'TextMessaging': 'src.activities.text_messaging',
            'VisualClothesPacking': 'src.activities.clothes_packing_visual',
            'BudgetCalculator': 'src.activities.budget_calculator',
            'BudgetBreakdown': 'src.activities.budget_breakdown',
            'IncomeCalculator': 'src.activities.income_calculator',
            'SavingsCalculator': 'src.activities.savings_calculator',
            'ApartmentSearch': 'src.activities.apartment_search',
            'ApartmentInspection': 'src.activities.apartment_inspection',
            'HousingChoice': 'src.activities.housing_choice',
            'HousingDialogue': 'src.activities.housing_dialogue',
            'RoommateSearch': 'src.activities.roommate_search',
            'CouchSurfingGame': 'src.activities.couch_surfing_game',
            'ShelterCheckin': 'src.activities.shelter_checkin',
            'ShelterNightGame': 'src.activities.shelter_night_game',
            'TLPApplication': 'src.activities.tlp_application',
            'WaitlistTracker': 'src.activities.waitlist_tracker',
            'DocumentViolations': 'src.activities.document_violations',
            'ResearchRights': 'src.activities.research_rights',
            'FacebookSearch': 'src.activities.facebook_search',
            'FosterParentCall': 'src.activities.foster_parent_call',
            'BackpackInvestigation': 'src.activities.backpack_investigation',
            'JobApplication': 'src.activities.job_application',
        }

    def get_activity_class(self, activity_name: str) -> Optional[type]:
        """
        Get activity class by name, loading module if necessary.

        Args:
            activity_name: Name of the activity class

        Returns:
            Activity class, or None if not found
        """
        # Return cached class if already loaded
        if activity_name in self._loaded_activities:
            return self._loaded_activities[activity_name]

        # Get module path
        module_path = self._activity_modules.get(activity_name)
        if not module_path:
            print(f"[LAZY_LOADER] Unknown activity: {activity_name}")
            return None

        try:
            # Lazy import the module
            print(f"[LAZY_LOADER] Loading {activity_name} from {module_path}")
            module = importlib.import_module(module_path)

            # Get the activity class
            activity_class = getattr(module, activity_name, None)
            if activity_class is None:
                print(f"[LAZY_LOADER] Class {activity_name} not found in {module_path}")
                return None

            # Cache the class
            self._loaded_activities[activity_name] = activity_class
            return activity_class

        except Exception as e:
            print(f"[LAZY_LOADER] Error loading {activity_name}: {e}")
            return None

    def create_activity(self, activity_name: str, *args, **kwargs) -> Optional[Any]:
        """
        Create an activity instance by name.

        Args:
            activity_name: Name of the activity class
            *args: Arguments to pass to activity constructor
            **kwargs: Keyword arguments to pass to activity constructor

        Returns:
            Activity instance, or None if failed
        """
        activity_class = self.get_activity_class(activity_name)
        if activity_class is None:
            return None

        try:
            # Create instance
            instance = activity_class(*args, **kwargs)

            # Store weak reference for tracking (optional)
            self._activity_instances[activity_name] = instance

            return instance

        except Exception as e:
            print(f"[LAZY_LOADER] Error creating {activity_name}: {e}")
            return None

    def unload_activity(self, activity_name: str):
        """
        Unload an activity instance to free memory.

        Args:
            activity_name: Name of the activity to unload
        """
        if activity_name in self._activity_instances:
            del self._activity_instances[activity_name]

            # Force garbage collection
            gc.collect()
            print(f"[LAZY_LOADER] Unloaded {activity_name}")

    def get_loaded_count(self) -> int:
        """
        Get count of currently loaded activity modules.

        Returns:
            Number of loaded modules
        """
        return len(self._loaded_activities)

    def get_instance_count(self) -> int:
        """
        Get count of active activity instances.

        Returns:
            Number of active instances
        """
        return len(self._activity_instances)

    def get_stats(self) -> dict:
        """
        Get loader statistics.

        Returns:
            Dictionary with loader stats
        """
        return {
            'modules_loaded': len(self._loaded_activities),
            'instances_active': len(self._activity_instances),
            'total_activities': len(self._activity_modules)
        }


# Global lazy loader instance
_lazy_loader = LazyActivityLoader()


def get_activity_class(activity_name: str) -> Optional[type]:
    """Get activity class from global loader"""
    return _lazy_loader.get_activity_class(activity_name)


def create_activity(activity_name: str, *args, **kwargs) -> Optional[Any]:
    """Create activity instance from global loader"""
    return _lazy_loader.create_activity(activity_name, *args, **kwargs)


def unload_activity(activity_name: str):
    """Unload activity from global loader"""
    _lazy_loader.unload_activity(activity_name)


def get_loader_stats() -> dict:
    """Get statistics from global loader"""
    return _lazy_loader.get_stats()

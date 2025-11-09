"""Unified objectives system for all parts"""

from src.core.objectives import GameObjective

class UnifiedObjectivesManager:
    """Manages objectives across all parts with unified interior system"""

    def __init__(self):
        self.current_part = 1

    def get_objectives_for_part(self, part: int):
        """Get objectives for a specific part"""
        if part == 1:
            return self.get_part1_objectives_unified()
        elif part == 2:
            return self.get_part2_objectives_unified()
        else:
            return []

    def get_part1_objectives_unified(self):
        """Part 1 housing stability objectives using unified interiors"""
        return [
            # Initial setup
            GameObjective(
                "wake_up_foster",
                "Last Day",
                "You turn 18 today. Must leave foster home.",
                'home',  # Foster home
                "Press E to pack",
                task_id="pack_belongings"
            ),

            GameObjective(
                "housing_search",
                "Find Housing",
                "Search for affordable apartment",
                'office',  # Housing office
                "Press E to inquire",
                task_id="apartment_search"
            ),

            GameObjective(
                "job_application",
                "Apply for Jobs",
                "Need income for rent",
                'restaurant',  # Fast food place
                "Press E to apply",
                task_id="job_application"
            ),

            GameObjective(
                "couch_surfing",
                "Sarah's Couch",
                "Friend offers temporary place",
                'home',  # Sarah's apartment
                "Press E to stay",
                task_id="couch_surfing"
            ),

            GameObjective(
                "tlp_discovery",
                "Youth Program",
                "Transitional Living Program - up to 18 months",
                'office',  # TLP office
                "Press E to apply",
                task_id="tlp_application"
            )
        ]

    def get_part2_objectives_unified(self):
        """Part 2 housing crisis objectives"""
        return [
            GameObjective(
                "rent_notice",
                "Eviction Warning",
                "5 days to pay or leave",
                'home',  # Your apartment
                "Press E to read notice",
                task_id="eviction_notice"
            ),

            GameObjective(
                "landlord_plea",
                "Negotiate with Landlord",
                "Try to get extension on rent",
                'office',  # Landlord office
                "Press E to plead case",
                task_id="landlord_negotiation"
            ),

            GameObjective(
                "storage_scramble",
                "Pack Essentials",
                "Can't afford storage. Choose what to keep.",
                'home',
                "Press E to pack",
                task_id="emergency_packing"
            ),

            GameObjective(
                "shelter_intake",
                "Emergency Shelter",
                "Last resort: homeless shelter",
                'office',  # Shelter intake
                "Press E for intake",
                task_id="shelter_intake"
            ),

            GameObjective(
                "food_bank_visit",
                "Food Bank",
                "No money for groceries",
                'store',  # Community center/food bank
                "Press E to get in line",
                task_id="food_bank"
            )
        ]

def create_objective_with_interior(obj_id: str, title: str, description: str,
                                 interior_type: str, task_id: str,
                                 interaction_text: str = "Press E") -> GameObjective:
    """Helper to create objectives with proper interior mappings"""

    # Map interior types to actual building types on map
    building_mappings = {
        'office': ['bank', 'office'],
        'home': ['house', 'apartment'],
        'store': ['store', 'grocery'],
        'restaurant': ['burger', 'pizza'],
        'medical': ['hospital', 'office']  # Some offices serve as clinics
    }

    objective = GameObjective(
        obj_id,
        title,
        description,
        None,  # Position set by objective manager
        interaction_text
    )

    # Store metadata for interior selection
    objective.interior_type = interior_type
    objective.building_types = building_mappings.get(interior_type, ['building'])
    objective.task_id = task_id

    return objective
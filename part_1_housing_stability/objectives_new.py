"""Part 1 Housing & Stability - New Game-Based Objectives"""

from src.core.game_world import GameObjective

def get_part1_objectives_new():
    """Return the new game-based objectives for Part 1
    
    This is a simplified objective list that works with the new task-based gameplay system.
    Most of the gameplay happens through the Part1GameManager, not through linear objectives.
    """
    return [
        # Introduction - triggers the dialogue system
        GameObjective(
            "housing_intro",
            "Aging Out",
            "You're turning 18 tomorrow. Time to face reality.",
            None,
            "Press E to begin"
        ),
        
        # Main gameplay objective - this launches the task-based game
        GameObjective(
            "housing_gameplay",
            "Find Housing in 30 Days",
            "Earn money, find housing, survive. You have 30 days.",
            None,
            "Press E to start surviving"
        ),
        
        # Different possible endings based on player performance
        GameObjective(
            "ending_stable_housing",
            "Housing Secured",
            "You found stable housing! Not perfect, but it's yours.",
            None,
            "Press E to reflect"
        ),
        
        GameObjective(
            "ending_temporary_housing", 
            "Temporary Relief",
            "You're in transitional housing. It's temporary, but you're safe.",
            None,
            "Press E to continue"
        ),
        
        GameObjective(
            "ending_couch_surfing",
            "Still Unstable",
            "Still bouncing between couches, but you have friends.",
            None,
            "Press E to keep going"
        ),
        
        GameObjective(
            "ending_homeless",
            "System Failed You",
            "No home, little money. The streets are your only option.",
            None,
            "Press E to survive"
        ),
        
        # Completion
        GameObjective(
            "part1_complete",
            "Part 1 Complete",
            "You've experienced the housing crisis facing foster youth",
            None,
            "Press E to continue to Part 2"
        )
    ]

# Map old objective IDs to new system for compatibility
OBJECTIVE_MAPPING = {
    # Old dialogue/menu objectives just trigger the new game
    "housing_intro": "housing_intro",
    "housing_menu": "housing_gameplay",
    
    # All the old task objectives are now handled by the game manager
    "apartment_search": "housing_gameplay",
    "rental_application": "housing_gameplay",
    "cosigner_denial": "housing_gameplay",
    "roommate_search": "housing_gameplay",
    "couch_surf_start": "housing_gameplay",
    "tlp_application": "housing_gameplay",
    "shelter_search": "housing_gameplay",
    "save_deposit": "housing_gameplay",
    
    # Endings map to appropriate ending objectives
    "stable_housing": "ending_stable_housing",
    "temporary_relief": "ending_temporary_housing", 
    "chronic_homelessness": "ending_homeless",
    
    # Completion
    "part1_complete": "part1_complete"
}
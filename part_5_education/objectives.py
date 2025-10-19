"""Part 5 Education Access & Confusion Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part5_objectives():
    """Return all Part 5 objectives - Education storyline"""
    return [
        # Test Event 1 - GED Attempt
        GameObjective(
            "need_diploma",
            "Job Requires Diploma",
            "Every decent job requires a high school diploma",
            None,
            "Press E to research GED"
        ),
        GameObjective(
            "ged_center",
            "Adult Education Center", 
            "Visit the adult education center for GED classes",
            None,
            "Press E to enter"
        ),
        GameObjective(
            "class_schedule",
            "Schedule Conflict",
            "Classes are 9AM-12PM. You work those hours.",
            None,
            "Press E to see options"
        ),
        
        # Test Event 2 - Online Learning
        GameObjective(
            "online_option",
            "Try Online GED",
            "Online classes available but need computer/internet",
            None,
            "Press E to check requirements"
        ),
        GameObjective(
            "library_computers",
            "Library Computer Lab",
            "Library has computers but 1-hour time limit",
            None,
            "Press E to try studying"
        ),
        GameObjective(
            "kicked_out",
            "Time's Up",
            "Your hour is up. 20 people waiting for computers.",
            None,
            "Press E to leave"
        ),
        GameObjective(
            "part5_complete",
            "Part 5 Complete",
            "Education remains out of reach",
            None,
            "Press E to continue"
        )
    ]
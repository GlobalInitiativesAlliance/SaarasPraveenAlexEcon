"""Part 7 Legal System Entanglements Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part7_objectives():
    """Return all Part 7 objectives - Legal System storyline"""
    return [
        # Test Event 1 - Minor Offense
        GameObjective(
            "cant_afford_transit",
            "No Bus Fare",
            "Need to get to work but have no money for bus",
            None,
            "Press E to face dilemma"
        ),
        GameObjective(
            "jump_turnstile",
            "Fare Evasion",
            "Jump the turnstile to avoid being late",
            None,
            "Press E to jump"
        ),
        GameObjective(
            "caught_police",
            "Arrested",
            "Transit police arrest you. Criminal record begins.",
            None,
            "Press E to be processed"
        ),
        
        # Test Event 2 - System Trap
        GameObjective(
            "court_date",
            "Mandatory Court",
            "Must appear in court but it's during work hours",
            None,
            "Press E to check date"
        ),
        GameObjective(
            "miss_court",
            "Bench Warrant",
            "Missed court due to work. Warrant issued.",
            None,
            "Press E to realize mistake"
        ),
        GameObjective(
            "job_background",
            "Background Check",
            "Lost job opportunity due to criminal record",
            None,
            "Press E to read rejection"
        ),
        GameObjective(
            "part7_complete",
            "Part 7 Complete", 
            "Trapped in the criminal justice system",
            None,
            "Press E to continue"
        )
    ]
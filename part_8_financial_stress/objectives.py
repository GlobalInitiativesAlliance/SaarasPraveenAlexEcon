"""Part 8 Financial Stress & Survival Decisions Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part8_objectives():
    """Return all Part 8 objectives - Financial Stress storyline"""
    return [
        # Test Event 1 - Impossible Choices
        GameObjective(
            "final_paycheck",
            "Last Paycheck",
            "$287 to last the month. Rent is $500.",
            None,
            "Press E to check bills"
        ),
        GameObjective(
            "survival_math",
            "Impossible Math",
            "Rent: $500, Food: $100, Bus: $50, Meds: $85",
            None,
            "Press E to despair"
        ),
        GameObjective(
            "choose_priority",
            "Choose What to Skip",
            "Pay rent or eat? Medicine or transportation?",
            None,
            "Press E to choose"
        ),
        
        # Test Event 2 - Consequences
        GameObjective(
            "skip_meds",
            "No Medicine",
            "Chose food over medication. Getting sicker.",
            None,
            "Press E to suffer"
        ),
        GameObjective(
            "eviction_notice",
            "Final Eviction",
            "Still couldn't make rent. 3 days to leave.",
            None,
            "Press E to read notice"
        ),
        GameObjective(
            "nowhere_to_go",
            "Homeless Tomorrow",
            "No money, no health, no home, no hope.",
            None,
            "Press E to pack"
        ),
        GameObjective(
            "part8_complete",
            "Part 8 Complete",
            "The poverty trap is complete",
            None,
            "Press E to finish"
        )
    ]
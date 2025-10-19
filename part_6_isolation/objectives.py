"""Part 6 Isolation & Lack of Support Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part6_objectives():
    """Return all Part 6 objectives - Isolation storyline"""
    return [
        # Test Event 1 - Losing Connections
        GameObjective(
            "roommate_leaves",
            "Roommate Moving Out",
            "Your only friend/roommate is moving back home",
            None,
            "Press E to talk"
        ),
        GameObjective(
            "alone_apartment",
            "Empty Apartment",
            "Now completely alone. Can't afford rent solo.",
            None,
            "Press E to sit in silence"
        ),
        GameObjective(
            "call_family",
            "Try Calling Family",
            "Haven't talked in years. Try calling mom.",
            None,
            "Press E to dial"
        ),
        
        # Test Event 2 - Seeking Connection
        GameObjective(
            "no_answer",
            "No Response",
            "Number disconnected. No other contacts.",
            None,
            "Press E to put phone down"
        ),
        GameObjective(
            "support_group",
            "Find Support Group",
            "Search online for free support groups",
            None,
            "Press E to search"
        ),
        GameObjective(
            "too_far",
            "Transportation Barrier",
            "Support group is 2 hours away by bus",
            None,
            "Press E to give up"
        ),
        GameObjective(
            "part6_complete",
            "Part 6 Complete",
            "Complete social isolation achieved",
            None,
            "Press E to continue"
        )
    ]
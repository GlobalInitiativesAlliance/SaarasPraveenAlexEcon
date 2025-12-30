"""
Part 8: Lack of Guidance/Mentorship
20 objectives exploring the challenges of making life decisions without adult guidance
"""
from src.core.game_world import GameObjective


def get_part8_objectives():
    """Return all Part 8 objectives"""
    return [
        # Bedroom - Future Planning
        GameObjective(
            "future_planning",
            "Future Planning",
            "Open the Future Planning Worksheet on your laptop",
            (54, 33),  # crappy_apartment
            "Press E to interact"
        ),
        GameObjective(
            "priority_puzzle",
            "Set Priorities",
            "Drag life options into priority order",
            (54, 33),
            "Mini-game"
        ),
        GameObjective(
            "incomplete_plan",
            "Incomplete",
            "Your plan shows as incomplete - no feedback given",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "no_advisor",
            "No Advisor",
            "Pop-up tells you to contact your ILP case manager",
            (54, 33),
            "Press E"
        ),

        # Community Center - Seeking Help
        GameObjective(
            "community_center",
            "Find Help",
            "Walk to the Community Center looking for guidance",
            (3, 31),  # community center
            "Press E to enter"
        ),
        GameObjective(
            "conflicting_advice",
            "Conflicting Voices",
            "NPCs give you conflicting advice about your future",
            (3, 31),
            "Talk to NPCs"
        ),
        GameObjective(
            "ask_whats_best",
            "What's Best?",
            "Ask 'What's best for me?' - NPCs shrug and walk away",
            (3, 31),
            "Dialogue choice"
        ),

        # Phone Notifications - Forced Decision
        GameObjective(
            "phone_notifications",
            "Notifications",
            "Receive texts about job opening and college deadline",
            (54, 33),
            "Check phone"
        ),
        GameObjective(
            "impossible_choice",
            "Impossible Choice",
            "Choose: job interview OR college applications",
            (54, 33),
            "Make a choice"
        ),
        GameObjective(
            "choice_consequence",
            "Consequence",
            "Whatever you chose, you lost the other opportunity",
            (54, 33),
            "Press E"
        ),

        # Panic and Seeking Help
        GameObjective(
            "panic_meter",
            "No Safety Net",
            "Panic meter appears - no safety net available",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "call_ilp",
            "Call for Help",
            "Try to call your ILP officer for advice",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "no_decision_help",
            "Your Choice",
            "ILP officer: 'I can't decide for you'",
            (54, 33),
            "Press E"
        ),

        # Balance Scale Puzzle
        GameObjective(
            "balance_puzzle",
            "Life Balance",
            "Balance scale puzzle with income, education, housing",
            (54, 33),
            "Mini-game"
        ),
        GameObjective(
            "puzzle_result",
            "Collapse",
            "The balance failed - future plan collapsed",
            (54, 33),
            "Press E"
        ),

        # Mentor Mechanic
        GameObjective(
            "seek_mentor",
            "Who Can Guide Me?",
            "Ask the right question to find a mentor",
            (3, 31),
            "Dialogue choice"
        ),
        GameObjective(
            "mentor_result",
            "Mentor Search",
            "Did you find guidance? Or remain alone?",
            (3, 31),
            "Press E"
        ),

        # Dream Sequence
        GameObjective(
            "sleep",
            "Rest",
            "Go to sleep after an exhausting day",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "dream_doors",
            "Dream Doors",
            "Dream shows doors: Work, School, Homelessness, Unknown",
            (54, 33),
            "Choose a door"
        ),
        GameObjective(
            "wake_up",
            "Uncertain Future",
            "Without guidance, your long-term path remains uncertain",
            (54, 33),
            "Press E"
        ),
    ]

"""
Part 7: Behavioral & Emotional Survival Strategies
20 objectives covering budgeting, guilt/anxiety meters, work conflicts, and decision paralysis
"""

from src.core.game_world import GameObjective

def get_part7_objectives():
    """Return all Part 7 objectives - Behavioral & Emotional Survival storyline"""
    return [
        # --- Apartment: Paycheck & Bills (Objectives 1-5) ---
        GameObjective(
            "paycheck_arrival",
            "Payday",
            "Check the paycheck envelope on the table",
            (54, 33),  # crappy_apartment
            "Press E to check paycheck"
        ),

        GameObjective(
            "bill_paying_game",
            "Pay Bills",
            "Drag each bill to the 'Paid' pile",
            (54, 33),
            "Click and drag bills"
        ),

        GameObjective(
            "leftover_money",
            "What's Left",
            "Look at your remaining balance: $40",
            (54, 33),
            "Press E to continue"
        ),

        GameObjective(
            "spending_choice",
            "Budget Decision",
            "Decide what to do with your $40: Save, Spend, or Ignore?",
            (54, 33),
            "Choose an option"
        ),

        GameObjective(
            "spending_consequence",
            "Emotional Cost",
            "Experience the consequence of your choice",
            (54, 33),
            "Press E to continue"
        ),

        # --- Workplace: Manager & Conflict (Objectives 6-10) ---
        GameObjective(
            "work_arrival",
            "Work Day",
            "Arrive at work and talk to your manager",
            (42, 42),  # government_office as workplace
            "Press E to enter"
        ),

        GameObjective(
            "manager_praise",
            "Recognition",
            "Receive praise from your manager",
            (42, 42),
            "Press E to listen"
        ),

        GameObjective(
            "self_sabotage",
            "Accept or Deflect",
            "Respond to the praise - accept or deflect?",
            (42, 42),
            "Choose a response"
        ),

        GameObjective(
            "shift_conflict",
            "Impossible Choice",
            "Choose: Take the extra shift or attend ILP meeting?",
            (42, 42),
            "Choose an option"
        ),

        GameObjective(
            "shift_consequence",
            "No Win",
            "Face the consequence of your work/meeting choice",
            (42, 42),
            "Press E to continue"
        ),

        # --- Apartment: Task Overwhelm (Objectives 11-15) ---
        GameObjective(
            "return_home",
            "Exhausted",
            "Return home exhausted",
            (54, 33),
            "Press E to enter"
        ),

        GameObjective(
            "college_reminder",
            "Reminder",
            "Notice the college application reminder on your phone",
            (54, 33),
            "Press E to check phone"
        ),

        GameObjective(
            "floating_tasks",
            "Overwhelmed",
            "See all your tasks floating around you",
            (54, 33),
            "Press E to focus"
        ),

        GameObjective(
            "task_game",
            "Prioritize",
            "Prioritize your tasks before the timer runs out",
            (54, 33),
            "Drag tasks to priority slots"
        ),

        GameObjective(
            "task_result",
            "Task Outcome",
            "See what happened with your task choices",
            (54, 33),
            "Press E to continue"
        ),

        # --- Grocery Store: Survival Choices (Objectives 16-18) ---
        GameObjective(
            "grocery_trip",
            "Shopping",
            "Go to the grocery store to buy food",
            (39, 51),  # grocery_store
            "Press E to enter store"
        ),

        GameObjective(
            "food_choice",
            "Health vs Budget",
            "Choose between fresh fruit or instant ramen",
            (39, 51),
            "Choose food option"
        ),

        GameObjective(
            "food_consequence",
            "Food Reality",
            "Experience the result of your food choice",
            (39, 51),
            "Press E to checkout"
        ),

        # --- Final Reflection (Objectives 19-20) ---
        GameObjective(
            "final_return",
            "End of Day",
            "Return home for the evening",
            (54, 33),
            "Press E to enter"
        ),

        GameObjective(
            "survival_reflection",
            "Survival Mode",
            "Reflect on the day's survival strategies",
            (54, 33),
            "Press E to continue"
        ),

        # Part completion
        GameObjective(
            "part6_complete",
            "Part 6 Complete",
            "You've developed survival strategies.",
            None,
            "Transitioning..."
        )
    ]


# Keep the original OBJECTIVES list for compatibility
OBJECTIVES = [
    {"id": obj.id, "text": obj.description, "location": obj.target_position}
    for obj in get_part7_objectives()
]

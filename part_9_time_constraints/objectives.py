"""
Part 9: Conflicting Responsibilities & Time Constraints
20 objectives exploring the impossible task of managing overlapping obligations
"""
from src.core.game_world import GameObjective


def get_part9_objectives():
    """Return all Part 9 objectives"""
    return [
        # Phone Notifications - Triple Conflict
        GameObjective(
            "phone_buzzes",
            "Phone Buzzes",
            "Check your phone - three notifications arrive",
            (54, 33),  # crappy_apartment
            "Press E to check phone"
        ),
        GameObjective(
            "calendar_conflict",
            "Calendar Conflict",
            "Drag notifications into calendar slots",
            (54, 33),
            "Mini-game"
        ),
        GameObjective(
            "overlap_warning",
            "Everything Overlaps",
            "Calendar flashes red - all three events overlap",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "choose_one",
            "Choose One",
            "You cannot attend everything - choose one priority",
            (54, 33),
            "Make a choice"
        ),
        GameObjective(
            "first_consequence",
            "Consequence",
            "Whatever you chose, you lost the others",
            (54, 33),
            "Press E"
        ),

        # Court Summons
        GameObjective(
            "next_morning",
            "Next Morning",
            "Wake up to check the mailbox",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "mailbox_letter",
            "Court Summons",
            "A court summons letter appears in your mailbox",
            (54, 33),
            "Mini-game"
        ),
        GameObjective(
            "court_school_conflict",
            "During Midterms",
            "Court date is scheduled during your school midterm",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "teacher_choice",
            "Tell or Hide",
            "Dialogue choice: tell your teacher or skip class silently",
            (54, 51),  # classroom
            "Make a choice"
        ),
        GameObjective(
            "teacher_consequence",
            "Academic Impact",
            "Either understanding but lost grade, or probation warning",
            (54, 51),
            "Press E"
        ),

        # Reschedule Attempt
        GameObjective(
            "try_reschedule",
            "Try to Reschedule",
            "Attempt to reschedule court date online",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "no_appointments",
            "No Options",
            "Website: 'No alternate appointments available'",
            (54, 33),
            "Press E"
        ),

        # Case Manager Conflict
        GameObjective(
            "case_manager_notice",
            "Case Manager",
            "Housing case manager scheduled check-in at 2pm tomorrow",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "work_conflict_again",
            "Another Conflict",
            "Work shift is also at 2pm - direct conflict again",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "housing_vs_work",
            "Housing vs Work",
            "Choose: case manager meeting OR work shift",
            (54, 33),
            "Make a choice"
        ),
        GameObjective(
            "second_consequence",
            "The Cost",
            "Miss meeting: housing at risk. Miss work: final warning.",
            (54, 33),
            "Press E"
        ),

        # Stress Overload
        GameObjective(
            "stress_maximum",
            "Stress Overload",
            "Stress meter fills as all priorities flash on screen",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "priorities_flash",
            "Everything at Once",
            "Court. School. Housing. Work. Health. All demanding attention.",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "collapse",
            "Collapse",
            "Character collapses onto bed with papers scattered",
            (54, 33),
            "Press E"
        ),
        GameObjective(
            "final_narration",
            "Without Support",
            "Too many responsibilities, not enough time. Every decision feels like failure.",
            (54, 33),
            "Press E"
        ),
    ]

"""Part 3 Legal System Entanglements Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part3_objectives():
    """Return all Part 3 objectives - Legal System storyline"""
    return [
        # Scene 1: Mail sorting at home
        GameObjective(
            "mail_on_floor",
            "Unopened Mail",
            "Scattered mail covers your apartment floor. Sort through it.",
            None,
            "Press E to sort mail"
        ),

        # Scene 2: Read the court notice
        GameObjective(
            "read_court_notice",
            "Court Summons",
            "Read the important mail you found",
            None,
            "Press E to read"
        ),

        # Scene 3: Walk to school with popup
        GameObjective(
            "walk_to_school",
            "Head to Class",
            "Walk to school for your morning class",
            None,
            "Press E at school entrance"
        ),

        # Scene 4: Note-taking while getting texts
        GameObjective(
            "class_distraction",
            "Focus in Class",
            "Take notes while your boss texts about tomorrow's shift",
            None,
            "Press E to start class"
        ),

        # Scene 5: Go to work (skipping court)
        GameObjective(
            "morning_shift",
            "Work Priority",
            "Head straight to work for your morning shift",
            None,
            "Press E at workplace"
        ),

        # Scene 6: Missed court notification
        GameObjective(
            "missed_court_notice",
            "Court Absence",
            "You missed your court appearance...",
            None,
            "Continue working"
        ),

        # Scene 7: Police encounter
        GameObjective(
            "police_stop",
            "Warrant Check",
            "A police officer stops you on your way home",
            None,
            "Press E to interact"
        ),

        # Scene 8: Breathing exercise
        GameObjective(
            "stay_calm",
            "Remain Composed",
            "Stay calm during the police interaction",
            None,
            "Press SPACE to breathe"
        ),

        # Scene 9: Receive citation
        GameObjective(
            "court_citation",
            "48-Hour Notice",
            "You must appear in court within 48 hours",
            None,
            "Press E to accept citation"
        ),

        # Scene 10: Courthouse line
        GameObjective(
            "courthouse_queue",
            "Wait in Line",
            "Stand in the courthouse line with your documents",
            None,
            "Press E to enter courthouse"
        ),

        # Scene 11: Fill out forms
        GameObjective(
            "court_forms",
            "Complete Paperwork",
            "Fill out the required court forms quickly",
            None,
            "Press E to start forms"
        ),

        # Scene 12: Wrong room
        GameObjective(
            "wrong_courtroom",
            "Misdirection",
            "You're told you're in the wrong room",
            None,
            "Press E to find correct room"
        ),

        # Scene 13: Judge appearance
        GameObjective(
            "face_judge",
            "Court Hearing",
            "Stand before the judge",
            None,
            "Press E to approach bench"
        ),

        # Scene 14: Receive fine
        GameObjective(
            "court_fine",
            "Financial Penalty",
            "$150 fine for missing court - added to your debt",
            None,
            "Press E to accept ruling"
        ),

        # Scene 15: Try to dispute
        GameObjective(
            "dispute_denied",
            "Appeal Rejected",
            "Your attempt to explain is dismissed",
            None,
            "Press E to leave courtroom"
        ),

        # Scene 16: Return home
        GameObjective(
            "go_home",
            "Head Home",
            "Walk back to your apartment",
            None,
            "Press E at apartment"
        ),

        # Scene 17: Final scene
        GameObjective(
            "courthouse_reflection",
            "Impossible Choice",
            "Stand outside the courthouse, holding court papers and study guide",
            None,
            "Press E to complete Part 3"
        )
    ]
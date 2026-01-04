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
            (54, 33),  # TLP apartment
            "Press E to sort mail"
        ),

        # Scene 2: Read the court notice
        GameObjective(
            "read_court_notice",
            "Court Summons",
            "Read the important mail you found",
            (54, 33),  # TLP apartment
            "Press E to read"
        ),

        # Scene 3: Walk to school with popup
        GameObjective(
            "walk_to_school",
            "Head to Class",
            "Walk to school for your morning class",
            (54, 51),  # School
            "Press E at school entrance"
        ),

        # Scene 4: Note-taking while getting texts
        GameObjective(
            "class_distraction",
            "Focus in Class",
            "Take notes while your boss texts about tomorrow's shift",
            (54, 51),  # School
            "Press E to start class"
        ),

        # Scene 5: Go to work (skipping court)
        GameObjective(
            "morning_shift",
            "Work Priority",
            "Head straight to work for your morning shift",
            (39, 51),  # Workplace
            "Press E at workplace"
        ),

        # Scene 6: Missed court notification
        GameObjective(
            "missed_court_notice",
            "Court Absence",
            "You missed your court appearance...",
            (39, 51),  # Workplace
            "Continue working"
        ),

        # Scene 7: Police encounter (at government office area)
        GameObjective(
            "police_stop",
            "Warrant Check",
            "A police officer stops you on your way to handle paperwork",
            (42, 42),  # Government office - shop building
            "Press E to interact"
        ),

        # Scene 8: Breathing exercise
        GameObjective(
            "stay_calm",
            "Remain Composed",
            "Stay calm during the police interaction",
            (42, 42),  # Government office - same location
            "Press SPACE to breathe"
        ),

        # Scene 9: Receive citation
        GameObjective(
            "court_citation",
            "48-Hour Notice",
            "You must appear in court within 48 hours",
            (42, 42),  # Government office - same location
            "Press E to accept citation"
        ),

        # Scene 9b: Government office queue
        GameObjective(
            "gov_office_queue",
            "Government Office",
            "Wait in line at the government office to handle paperwork",
            (42, 42),  # Government office location
            "Press E to enter"
        ),

        # Scene 9c: Document sorting
        GameObjective(
            "document_sorting",
            "Sort Documents",
            "Sort the legal documents as requested by the clerk",
            (42, 42),  # Government office location
            "Press E to start sorting"
        ),

        # Scene 9d: Paperwork rejection
        GameObjective(
            "paperwork_rejection",
            "Bureaucratic Barrier",
            "Your paperwork has a problem...",
            (42, 42),  # Government office location
            "Press E to continue"
        ),

        # Scene 10: Courthouse line
        GameObjective(
            "courthouse_queue",
            "Wait in Line",
            "Stand in the courthouse line with your documents",
            (43, 33),  # Courthouse - skyscraper building
            "Press E to enter courthouse"
        ),

        # Scene 11: Fill out forms
        GameObjective(
            "court_forms",
            "Complete Paperwork",
            "Fill out the required court forms quickly",
            (43, 33),  # Courthouse
            "Press E to start forms"
        ),

        # Scene 12: Wrong room
        GameObjective(
            "wrong_courtroom",
            "Misdirection",
            "You're told you're in the wrong room",
            (43, 33),  # Courthouse
            "Press E to find correct room"
        ),

        # Scene 13: Judge appearance
        GameObjective(
            "face_judge",
            "Court Hearing",
            "Stand before the judge",
            (43, 33),  # Courthouse
            "Press E to approach bench"
        ),

        # Scene 14: Receive fine
        GameObjective(
            "court_fine",
            "Financial Penalty",
            "$150 fine for missing court - added to your debt",
            (43, 33),  # Courthouse
            "Press E to accept ruling"
        ),

        # Scene 15: Try to dispute
        GameObjective(
            "dispute_denied",
            "Appeal Rejected",
            "Your attempt to explain is dismissed",
            (43, 33),  # Courthouse
            "Press E to leave courtroom"
        ),

        # Scene 16: Return home
        GameObjective(
            "go_home",
            "Head Home",
            "Walk back to your apartment",
            (54, 33),  # TLP apartment
            "Press E at apartment"
        ),

        # Scene 17: Final scene
        GameObjective(
            "courthouse_reflection",
            "Impossible Choice",
            "Stand outside the courthouse, holding court papers and study guide",
            (43, 33),  # Outside courthouse
            "Press E to continue"
        ),

        # Part completion
        GameObjective(
            "part2_complete",
            "Part 2 Complete",
            "You've navigated the legal system's barriers.",
            None,
            "Transitioning..."
        )
    ]
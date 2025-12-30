"""Part 6 Systemic and Structural Barriers Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part6_objectives():
    """Return all Part 6 objectives - Systemic Barriers storyline"""
    return [
        # Scene 1: Social Services Office start
        GameObjective(
            "social_services_start",
            "Forms and Paperwork",
            "Start at Social Services Office with stack of forms",
            (42, 42),  # Government office location
            "Press E to enter office"
        ),

        # Scene 2: Document sorting mini-game
        GameObjective(
            "document_sorting",
            "Sort Documents",
            "Drag documents to Required vs Optional piles before timer runs out",
            (42, 42),  # Government office
            "Click and drag documents"
        ),

        # Scene 3: Always incomplete stamp
        GameObjective(
            "incomplete_stamp",
            "Application Rejected",
            "Clerk stamps 'INCOMPLETE' no matter what you did",
            (42, 42),  # Government office
            "Press E to continue"
        ),

        # Scene 4: Wait in line again
        GameObjective(
            "wait_in_line",
            "Two Hour Wait",
            "Wait in line again, told you missed a signature",
            (42, 42),  # Government office
            "Press E to wait"
        ),

        # Scene 5: Food assistance notice
        GameObjective(
            "food_assistance_mail",
            "Possible Benefits",
            "Receive mail: 'You may qualify for food assistance'",
            (54, 33),  # Home/apartment
            "Press E to read mail"
        ),

        # Scene 6: Application knowledge check
        GameObjective(
            "application_quiz",
            "How to Apply?",
            "Do you know how to apply for benefits?",
            (54, 33),  # Home
            "Choose an answer"
        ),

        # Scene 7: Online application attempt
        GameObjective(
            "online_application",
            "Website Crash",
            "Try to apply online - site crashes after 5 minutes",
            (54, 33),  # Home
            "Click to fill form"
        ),

        # Scene 8: Phone system navigation
        GameObjective(
            "phone_maze",
            "Automated Loop",
            "Call benefits line - stuck in automated system",
            (54, 33),  # Home
            "Press numbers to navigate"
        ),

        # Scene 9: Peer advice
        GameObjective(
            "peer_advice",
            "Hidden Knowledge",
            "Ask peer for help - unlock foster youth navigator path",
            (54, 33),  # Home or street
            "Press E to ask peer"
        ),

        # Scene 10: Hunger consequence
        GameObjective(
            "hunger_drop",
            "Benefits Failed",
            "Hunger meter drops - couldn't access food assistance",
            (54, 33),  # Home
            "Press E to continue"
        ),

        # Scene 11: Age out notification
        GameObjective(
            "age_out_notice",
            "Turn 21",
            "Flash-forward: You no longer qualify for Medi-Cal",
            (54, 33),  # Home
            "Press E to read notice"
        ),

        # Scene 12: Benefits application with expired docs
        GameObjective(
            "expired_documents",
            "Document Submission",
            "Drag expired card, ID, and letter to application",
            (54, 33),  # Home
            "Drag documents to screen"
        ),

        # Scene 13: Rejection screen
        GameObjective(
            "aged_out_rejection",
            "Application Denied",
            "Rejection: You have aged out of the system",
            (54, 33),  # Home
            "Press E to continue"
        ),

        # Scene 14: ILP officer call
        GameObjective(
            "ilp_call",
            "Too Old",
            "ILP officer says you're too old for services",
            (54, 33),  # Home
            "Press E to end call"
        ),

        # Scene 15: Online research
        GameObjective(
            "research_programs",
            "Find Solutions",
            "Research online - discover Former Foster Youth program",
            (54, 33),  # Home
            "Press E to search"
        ),

        # Scene 16: Benefits office lobby
        GameObjective(
            "benefits_lobby",
            "Shared Frustration",
            "Enter Benefits Office - NPCs share frustrations",
            (42, 42),  # Government office
            "Press E to enter"
        ),

        # Scene 17: Dialogue specificity game
        GameObjective(
            "dialogue_choice",
            "Choose Words Carefully",
            "Dialogue: vague vs specific phrasing matters",
            (42, 42),  # Government office
            "Choose dialogue option"
        ),

        # Scene 18: Correct phrasing success
        GameObjective(
            "specific_request",
            "Progress Unlocked",
            "Say 'CalFresh as foster youth' - clerk helps",
            (42, 42),  # Government office
            "Press E to continue"
        ),

        # Scene 19: Workshop notification
        GameObjective(
            "workshop_notice",
            "Mandatory Meeting",
            "ILP workshop scheduled at 3pm - conflicts with work",
            (54, 33),  # Home
            "Press E to read notice"
        ),

        # Scene 20: Impossible choice
        GameObjective(
            "workshop_conflict",
            "No Win Scenario",
            "Choose: workshop and lose job, or work and lose benefits",
            (54, 33),  # Home
            "Press 1 or 2 to decide"
        ),

        # Final reflection
        GameObjective(
            "systemic_reflection",
            "Broken System",
            "You've experienced how the system creates barriers",
            (54, 33),  # Home
            "Press E to complete Part 6"
        )
    ]
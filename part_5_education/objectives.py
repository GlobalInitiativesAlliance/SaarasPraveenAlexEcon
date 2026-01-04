"""Part 5 Education Access and Confusion Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part5_objectives():
    """Return all Part 5 objectives - Education Access storyline"""
    return [
        # Scene 1: Foster home with laptop
        GameObjective(
            "foster_home_laptop",
            "FAFSA Application",
            "Start in foster home living room with laptop open",
            (54, 33),  # TLP apartment/foster home
            "Press E to open laptop"
        ),

        # Scene 2: FAFSA mini-game
        GameObjective(
            "fafsa_form",
            "Complete FAFSA",
            "Fill in FAFSA information before timer runs out (60 seconds)",
            (54, 33),  # Foster home
            "Click to fill form fields"
        ),

        # Scene 3: Parental info bypass
        GameObjective(
            "parent_info_bypass",
            "Independent Status",
            "Answer how foster youth bypass parental requirements",
            (54, 33),  # Foster home
            "Choose correct answer"
        ),

        # Scene 4: School counselor visit
        GameObjective(
            "visit_counselor",
            "Career Guidance",
            "Walk to school counselor's office",
            (54, 51),  # School
            "Press E to enter office"
        ),

        # Scene 5: Career matching dialogue
        GameObjective(
            "career_matching",
            "Education Planning",
            "Match career fields with their training length",
            (54, 51),  # School counselor
            "Drag careers to correct categories"
        ),

        # Scene 6: Trade school appears
        GameObjective(
            "trade_school_unlock",
            "New Option",
            "Trade school tour location appears on map",
            (54, 51),  # School
            "Check map for new location"
        ),

        # Scene 7: Library laptop request
        GameObjective(
            "library_visit",
            "Request Laptop",
            "Go to library to request a laptop",
            (46, 51),  # Library location
            "Press E to enter library"
        ),

        # Scene 8: ID verification
        GameObjective(
            "id_verification",
            "Document Check",
            "Match your ID and foster verification to the correct form",
            (46, 51),  # Library
            "Click to match documents"
        ),

        # Scene 9: Laptop unavailable
        GameObjective(
            "laptop_waitlist",
            "Out of Stock",
            "Laptops unavailable - scheduled for next week pickup",
            (46, 51),  # Library
            "Press E to accept"
        ),

        # Scene 10: Work vs study dilemma
        GameObjective(
            "double_shift_notice",
            "Work Conflict",
            "Double shift tonight but exam tomorrow - make a choice",
            (54, 33),  # Back home
            "Press 1 or 2 to decide"
        ),

        # Scene 11: Study vs money choice
        GameObjective(
            "work_study_choice",
            "Difficult Decision",
            "Call out to study (-$50) or work and risk failing?",
            (54, 33),  # Home
            "Select your choice"
        ),

        # Scene 12: Orientation email
        GameObjective(
            "orientation_notice",
            "Campus Event",
            "Mandatory campus orientation tomorrow at 11am",
            (54, 33),  # Home
            "Press E to read email"
        ),

        # Scene 13: Schedule puzzle
        GameObjective(
            "schedule_puzzle",
            "Time Management",
            "Rearrange schedule to fit work and orientation",
            (54, 33),  # Home
            "Drag to rearrange schedule"
        ),

        # Scene 14: Enrollment consequence
        GameObjective(
            "schedule_result",
            "Enrollment Status",
            "Handle result of schedule puzzle (success/delay)",
            (54, 33),  # Home
            "Press E to continue"
        ),

        # Scene 15: FAFSA confirmation
        GameObjective(
            "advisor_meeting",
            "Financial Aid",
            "Meet advisor for FAFSA confirmation and resources",
            (54, 51),  # School/Campus
            "Press E to meet advisor"
        ),

        # Scene 16: Resource packet
        GameObjective(
            "resource_packet",
            "Campus Resources",
            "Receive packet with housing, tutoring, and aid info",
            (54, 51),  # Campus
            "Press E to review packet"
        ),

        # Scene 17: Campus quad navigation
        GameObjective(
            "campus_quad",
            "Choose Your Path",
            "Walk through campus quad with education options",
            (54, 51),  # Campus quad
            "Press E to explore options"
        ),

        # Scene 18: Final education choice
        GameObjective(
            "education_path",
            "Decision Time",
            "Choose: class, trade school, or work",
            (54, 51),  # Campus quad
            "Press 1, 2, or 3 to choose"
        ),

        # Final reflection
        GameObjective(
            "education_reflection",
            "Path Forward",
            "You've navigated the complex education system",
            (54, 51),  # Campus
            "Press E to continue"
        ),

        # Part completion
        GameObjective(
            "part4_complete",
            "Part 4 Complete",
            "You've overcome education barriers.",
            None,
            "Transitioning..."
        )
    ]
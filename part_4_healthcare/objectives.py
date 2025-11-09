"""Part 4 Healthcare and Mental Health Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part4_objectives():
    """Return all Part 4 objectives - Healthcare and Mental Health storyline"""
    return [
        # Scene 1: Morning mail in apartment
        GameObjective(
            "morning_mail",
            "Check Your Mail",
            "Start your day at 9am and check the mail",
            (54, 33),  # TLP apartment
            "Press E to check mailbox"
        ),

        # Scene 2: Mail sorting mini-game
        GameObjective(
            "sort_mail",
            "Sort Through Mail",
            "Drag mail to 'Important' or 'Junk' pile",
            (54, 33),  # TLP apartment
            "Click and drag mail"
        ),

        # Scene 3: Read Medi-Cal termination notice
        GameObjective(
            "medicaid_notice",
            "Coverage Terminated",
            "Your Medi-Cal coverage has ended due to age eligibility",
            (54, 33),  # TLP apartment
            "Press E to read notice"
        ),

        # Scene 4: Therapy appointment notification
        GameObjective(
            "therapy_reminder",
            "Appointment Tomorrow",
            "Your phone buzzes: therapy appointment tomorrow, no insurance",
            (54, 33),  # TLP apartment
            "Press E to check phone"
        ),

        # Scene 5: Go to Community Health Clinic
        GameObjective(
            "visit_clinic",
            "Visit Health Clinic",
            "Go to the Community Health Clinic on the map",
            (20, 40),  # Office building (repurposed as clinic)
            "Press E to enter clinic"
        ),

        # Scene 6: Document checklist
        GameObjective(
            "document_check",
            "Gather Documents",
            "Check that you have: ID, previous Medi-Cal card, proof of income",
            (20, 40),  # Clinic
            "Press E to check documents"
        ),

        # Scene 7: Fill out application form
        GameObjective(
            "medicaid_form",
            "Reapply for Coverage",
            "Fill out Former Foster Youth program application (4 questions)",
            (20, 40),  # Clinic
            "Press E to start form"
        ),

        # Scene 8: Coverage approval but with delay
        GameObjective(
            "coverage_delay",
            "Two Week Wait",
            "Approved! But reinstatement takes two weeks...",
            (20, 40),  # Clinic
            "Press E to accept"
        ),

        # Scene 9: Therapy payment decision
        GameObjective(
            "therapy_decision",
            "Payment Options",
            "Therapist calls: pay $150, cancel, or ask about sliding scale",
            (54, 33),  # Back at apartment
            "Press 1, 2, or 3 to choose"
        ),

        # Scene 10: Work shift with anxiety
        GameObjective(
            "work_anxiety",
            "Anxiety at Work",
            "Next day at burger shop, anxiety meter starts flashing",
            (39, 51),  # Workplace
            "Press E to start shift"
        ),

        # Scene 11: Breathing exercise mini-game
        GameObjective(
            "breathing_game",
            "Manage Anxiety",
            "Complete breathing exercise to match inhale/exhale timing",
            (39, 51),  # Workplace
            "Press SPACE to breathe"
        ),

        # Scene 12: Burger incident (if breathing fails)
        GameObjective(
            "work_warning",
            "Manager Warning",
            "Handle the manager's warning about burned burger",
            (39, 51),  # Workplace
            "Press E to continue"
        ),

        # Scene 13: Pharmacy medication search
        GameObjective(
            "pharmacy_visit",
            "Get Medication",
            "Go to pharmacy to find affordable generic medication",
            (66, 40),  # Store (as pharmacy)
            "Press E to enter pharmacy"
        ),

        # Scene 14: Medication selection mini-game
        GameObjective(
            "select_medication",
            "Choose Generic",
            "Find medication that meets affordability and dosage requirements",
            (66, 40),  # Pharmacy
            "Click to select medication"
        ),

        # Scene 15: Appointment during school
        GameObjective(
            "appointment_conflict",
            "Schedule Conflict",
            "Appointment reminder appears during school hours",
            (54, 51),  # School
            "Press E to check reminder"
        ),

        # Scene 16: Bus route mini-game
        GameObjective(
            "catch_bus",
            "Navigate Transit",
            "Choose correct bus route within 20 seconds",
            (54, 51),  # School area
            "Click correct bus quickly"
        ),

        # Scene 17: Missed appointment consequence
        GameObjective(
            "missed_appointment",
            "Lost Trust",
            "Missing appointment lowers trust with caseworker",
            (54, 33),  # Apartment
            "Press E to continue"
        ),

        # Scene 18: Caseworker call
        GameObjective(
            "caseworker_call",
            "Get Support",
            "Caseworker calls and guides you to foster youth navigator",
            (54, 33),  # Apartment
            "Press E to answer call"
        ),

        # Scene 19: Navigator questions
        GameObjective(
            "navigator_quiz",
            "Learn the System",
            "Answer questions about maintaining coverage and managing medications",
            (54, 33),  # Apartment
            "Press number keys to answer"
        ),

        # Scene 20: Coverage restored
        GameObjective(
            "coverage_active",
            "Success!",
            "Coverage is active again, new therapy appointment scheduled",
            (54, 33),  # Apartment
            "Press E to check confirmation"
        ),

        # Final reflection
        GameObjective(
            "healthcare_reflection",
            "System Navigation",
            "You've learned to navigate the complex healthcare system",
            (54, 33),  # Apartment
            "Press E to complete Part 4"
        )
    ]
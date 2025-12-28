"""Part 2: Healthcare Access - Managing health coverage and mental health challenges"""

from src.core.game_world import GameObjective

def get_part2_healthcare_objectives():
    """Return Part 2 Healthcare Access storyline objectives"""
    return [
        # Morning - Starting Crisis
        GameObjective(
            "start_apartment_morning",
            "9:00 AM - Wake Up",
            "Start in your apartment. Another day begins.",
            (54, 33),  # Apartment location
            "Press E to get up"
        ),

        # Mailbox Mini-game
        GameObjective(
            "check_mailbox",
            "Check Mailbox",
            "Go to your mailbox and sort through today's mail",
            (54, 33),  # Near apartment
            "Press E to check mail"
        ),

        # The Crisis - Medi-Cal Loss
        GameObjective(
            "medicaid_notice",
            "Coverage Terminated",
            "Important letter: Your Medi-Cal coverage has ended due to age eligibility",
            (54, 33),  # Still at mailbox
            "Press E to read notice"
        ),

        # Phone Notification
        GameObjective(
            "therapy_reminder",
            "Therapy Appointment",
            "Phone buzzes: Reminder - Therapy appointment tomorrow at 2 PM",
            (54, 33),  # Apartment
            "Press E to check phone"
        ),

        # Crisis Realization
        GameObjective(
            "insurance_panic",
            "No Insurance Coverage",
            "Realize you have a therapy appointment but no insurance to cover it",
            (54, 33),  # Apartment
            "Press E to worry"
        ),

        # Go to Clinic
        GameObjective(
            "travel_to_clinic",
            "Community Health Clinic",
            "Go to the Community Health Clinic to apply for coverage",
            (34, 31),  # Using hospital location for clinic
            "Press E to enter clinic"
        ),

        # Clinic Checklist
        GameObjective(
            "clinic_checklist",
            "Required Documents",
            "Check off that you have: ID, previous Medi-Cal card, and proof of income",
            (34, 31),  # Clinic
            "Press E to show documents"
        ),

        # Application Process
        GameObjective(
            "foster_youth_application",
            "Former Foster Youth Application",
            "Fill out form with 4 questions about age, residency, and foster history",
            (34, 31),  # Clinic
            "Press E to complete form"
        ),

        # Instant Approval
        GameObjective(
            "application_approved",
            "Approved - But Wait",
            "Good news: Approved instantly! Bad news: Reinstatement takes two weeks",
            (34, 31),  # Clinic
            "Press E to understand"
        ),

        # Therapist Call
        GameObjective(
            "therapist_call_options",
            "Therapist Office Calls",
            "Options: Pay $150 out-of-pocket, cancel appointment, or ask about sliding scale",
            (54, 33),  # Back at apartment
            "Press E to choose"
        ),

        # Payment Decision (Branch point)
        GameObjective(
            "therapy_payment_decision",
            "Choose Payment Option",
            "Sliding scale = $40, Cancel = decreased mental health, Full price = $150",
            (54, 33),  # Apartment
            "Press E to decide"
        ),

        # Next Day - Work Anxiety
        GameObjective(
            "work_day_anxiety",
            "Next Day at Work",
            "At your burger shop job, anxiety meter starts flashing",
            (39, 51),  # Grocery store used as workplace
            "Press E to start work"
        ),

        # Breathing Exercise
        GameObjective(
            "breathing_exercise",
            "Manage Anxiety",
            "Complete breathing exercise to match inhale and exhale timing",
            (39, 51),  # Workplace
            "Press E to breathe"
        ),

        # Work Consequence (if failed)
        GameObjective(
            "work_performance",
            "Work Performance",
            "If breathing failed: Burn a burger and get manager warning",
            (39, 51),  # Workplace
            "Press E to continue"
        ),

        # Pharmacy Visit
        GameObjective(
            "pharmacy_visit",
            "Visit Pharmacy",
            "Go to pharmacy to find affordable generic medication",
            (12, 34),  # Bank used as pharmacy
            "Press E to enter pharmacy"
        ),

        # Medication Selection
        GameObjective(
            "medication_selection",
            "Choose Medication",
            "Find generic medication that meets both affordability and dosage requirements",
            (12, 34),  # Pharmacy
            "Press E to compare options"
        ),

        # Appointment Reminder During School
        GameObjective(
            "school_appointment_conflict",
            "Appointment During School",
            "Appointment reminder appears during school hours - need to get there",
            (54, 51),  # School
            "Press E to plan route"
        ),

        # Bus Route Mini-game
        GameObjective(
            "bus_route_game",
            "Catch the Right Bus",
            "Choose correct bus route within 20 seconds or miss appointment",
            (54, 51),  # School
            "Press E to choose bus"
        ),

        # Appointment Outcome
        GameObjective(
            "appointment_outcome",
            "Appointment Result",
            "Missing appointment lowers trust with caseworker",
            (34, 31),  # Clinic/appointment location
            "Press E to check result"
        ),

        # Caseworker Call
        GameObjective(
            "caseworker_guidance",
            "Caseworker Calls",
            "Caseworker guides you to foster youth mental health navigator",
            (54, 33),  # Apartment
            "Press E to answer call"
        ),

        # Navigator Questions
        GameObjective(
            "navigator_questions",
            "Mental Health Navigator",
            "Answer multiple choice questions about maintaining coverage and managing medications",
            (54, 33),  # Apartment
            "Press E to answer questions"
        ),

        # Coverage Restored
        GameObjective(
            "coverage_restored",
            "Coverage Active Again",
            "Receive text: Coverage is active and new therapy appointment scheduled",
            (54, 33),  # Apartment
            "Press E to read text"
        ),

        # Part 2 Complete
        GameObjective(
            "part2_healthcare_complete",
            "Part 2 Complete",
            "You've learned to navigate healthcare access as a young adult!",
            (54, 33),  # Apartment
            "Press E to continue to Part 3"
        )
    ]
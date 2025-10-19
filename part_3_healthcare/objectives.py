"""Part 3 Healthcare & Mental Health Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part3_objectives():
    """Return all Part 3 objectives - Healthcare & Mental Health storyline"""
    return [
        # Day 1 - Health Issues Begin
        GameObjective(
            "feeling_unwell",
            "Not Feeling Well",
            "You wake up feeling sick. Visit the clinic for help.",
            None,
            "Press E to get out of bed"
        ),
        GameObjective(
            "visit_clinic",
            "Community Health Clinic",
            "Go to the free clinic to see what's wrong",
            None,
            "Press E to enter clinic"
        ),
        GameObjective(
            "long_wait",
            "Waiting Room Blues",
            "The clinic is overcrowded. Wait for your turn (3+ hours).",
            None,
            "Press E to wait"
        ),
        GameObjective(
            "see_doctor",
            "Quick Examination",
            "Doctor says you need medication but clinic doesn't have it",
            None,
            "Press E to talk to doctor"
        ),
        GameObjective(
            "pharmacy_prices",
            "Pharmacy Sticker Shock",
            "The medication costs $85 without insurance",
            None,
            "Press E to check prices"
        ),
        
        # Day 2 - Mental Health Struggles
        GameObjective(
            "anxiety_rising",
            "Anxiety Attack",
            "Stress from being sick and broke triggers anxiety",
            None,
            "Press E to try to calm down"
        ),
        GameObjective(
            "seek_counseling",
            "Mental Health Services",
            "Look for free mental health support at community center",
            None,
            "Press E to enter"
        ),
        GameObjective(
            "waitlist_news",
            "6-Month Wait List",
            "Free counseling has a 6-month wait. Crisis hotline given.",
            None,
            "Press E to take hotline number"
        ),
        GameObjective(
            "call_hotline",
            "Crisis Hotline",
            "Call the mental health crisis hotline from home",
            None,
            "Press E to make call"
        ),
        
        # Day 3 - Emergency Room Visit
        GameObjective(
            "getting_worse",
            "Symptoms Worsen",
            "Your untreated condition is getting worse",
            None,
            "Press E to assess symptoms"
        ),
        GameObjective(
            "emergency_room",
            "ER Visit",
            "No choice but to go to the emergency room",
            None,
            "Press E to enter ER"
        ),
        GameObjective(
            "er_treatment",
            "Emergency Treatment",
            "Finally get treatment but at huge cost",
            None,
            "Press E for treatment"
        ),
        GameObjective(
            "hospital_bill",
            "Medical Debt",
            "Receive $3,500 ER bill. No way to pay.",
            None,
            "Press E to view bill"
        ),
        
        # Day 4 - Trying to Recover
        GameObjective(
            "missed_work",
            "Lost Income",
            "You've missed 3 days of work while sick",
            None,
            "Press E to check messages"
        ),
        GameObjective(
            "collection_calls",
            "Debt Collectors",
            "Hospital bill sent to collections already",
            None,
            "Press E to answer phone"
        ),
        GameObjective(
            "medication_rationing",
            "Rationing Medicine",
            "Try to make expensive medication last longer",
            None,
            "Press E to count pills"
        ),
        GameObjective(
            "support_group",
            "Find Support Group",
            "Look for free support group at library",
            None,
            "Press E to enter library"
        ),
        GameObjective(
            "part3_complete",
            "Part 3 Complete",
            "You've experienced the healthcare crisis firsthand",
            None,
            "Press E to continue"
        )
    ]
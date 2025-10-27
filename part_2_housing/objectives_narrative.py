"""Part 2 Housing Stability - Continued Narrative Flow

This continues the housing crisis narrative with more systemic challenges:
1. Transitional housing programs and their limitations
2. Emergency housing services bureaucracy
3. Roommate conflicts in unstable housing
4. The cycle of temporary solutions
"""

from src.core.game_world import GameObjective

def get_part2_narrative_objectives():
    """Return Part 2 objectives as pure narrative notifications"""

    return [
        # === INTRODUCTION TO PART 2 ===
        GameObjective(
            "part2_intro",
            "Part 2: Housing Services",
            "After months of instability, you're trying formal housing programs...",
            None,
            "Press E to continue"
        ),

        GameObjective(
            "case_worker_meeting",
            "Meeting Case Worker",
            "Your ILP case worker found a Transitional Living Program with openings.",
            None,
            "Press E to learn more"
        ),

        # === TLP APPLICATION PROCESS ===
        GameObjective(
            "tlp_requirements",
            "TLP Requirements",
            "Must attend classes, follow curfew, save 30% income, no guests after 10pm",
            None,
            "Press E to accept terms"
        ),

        GameObjective(
            "mandatory_classes",
            "Tenant Rights Class",
            "8 hours of tenant rights education. You learn about deposits, leases, eviction laws.",
            None,
            "Press E to complete class"
        ),

        GameObjective(
            "life_skills_workshop",
            "Life Skills Workshop",
            "Budgeting, cooking, cleaning schedules. Things you already know how to do.",
            None,
            "Press E to endure workshop"
        ),

        GameObjective(
            "application_submitted",
            "TLP Application Complete",
            "Application submitted. They'll call you within 2-4 weeks. Maybe.",
            None,
            "Press E to wait anxiously"
        ),

        # === MOVING INTO TLP ===
        GameObjective(
            "tlp_approval",
            "Approved for TLP!",
            "You got in! Shared apartment, $400/month, 18-month maximum stay.",
            None,
            "Press E to feel relief"
        ),

        GameObjective(
            "pack_belongings",
            "Packing Your Life",
            "Everything you own fits in two bags. At least it's yours.",
            None,
            "Press E to pack"
        ),

        GameObjective(
            "meet_roommate",
            "Meet Sarah",
            "Your new roommate Sarah seems nice. She's been here 6 months already.",
            None,
            "Press E to introduce yourself"
        ),

        GameObjective(
            "first_night_tlp",
            "First Night",
            "Your own bed. A door that locks. Running water. It feels like luxury.",
            None,
            "Press E to sleep peacefully"
        ),

        # === CRISIS: ROOMMATE LEAVES ===
        GameObjective(
            "three_weeks_later",
            "Three Weeks Later",
            "Sarah got a job in another city. She's leaving tomorrow.",
            None,
            "Press E to panic"
        ),

        GameObjective(
            "rent_increase",
            "Rent Doubled",
            "Without roommate, your share jumps to $800. You make $1200/month.",
            None,
            "Press E to see the math"
        ),

        GameObjective(
            "impossible_budget",
            "The Math",
            "Income: $1200 | Rent: $800 | Food: $200 | Phone: $50 | Transport: $100 | Left: $50",
            None,
            "Press E to feel trapped"
        ),

        GameObjective(
            "emergency_meeting",
            "Meeting with TLP Staff",
            "They'll try to find you a new roommate. Could take 2-3 months.",
            None,
            "Press E to plead for help"
        ),

        # === TEMPORARY SOLUTIONS ===
        GameObjective(
            "payment_plan",
            "Payment Plan Approved",
            "TLP agrees to payment plan. You owe $400 extra each month for 3 months.",
            None,
            "Press E to sign agreement"
        ),

        GameObjective(
            "second_job_search",
            "Need Second Job",
            "One job isn't enough. Start applying for night and weekend shifts.",
            None,
            "Press E to exhaust yourself"
        ),

        GameObjective(
            "new_roommate_arrives",
            "New Roommate: Mike",
            "Mike just aged out too. Seems angry at the world. Plays music until 3am.",
            None,
            "Press E to lose sleep"
        ),

        GameObjective(
            "roommate_conflict",
            "Growing Tensions",
            "Mike hasn't paid his share in 2 months. Uses your food. Breaks house rules.",
            None,
            "Press E to confront him"
        ),

        GameObjective(
            "mike_evicted",
            "Mike Gets Evicted",
            "TLP evicts Mike for non-payment. You're alone again. Rent doubles again.",
            None,
            "Press E to start over"
        ),

        # === THE CYCLE CONTINUES ===
        GameObjective(
            "six_months_in",
            "Six Months in TLP",
            "12 months left in program. Still no affordable housing available after.",
            None,
            "Press E to worry about future"
        ),

        GameObjective(
            "housing_search_again",
            "Search for Next Place",
            "Studios now $1500. Still need 3x income ($4500). Still no co-signer.",
            None,
            "Press E to feel hopeless"
        ),

        GameObjective(
            "savings_depleted",
            "No Savings",
            "Between double rent and payment plans, you've saved nothing.",
            None,
            "Press E to check empty account"
        ),

        GameObjective(
            "year_in_tlp",
            "One Year in TLP",
            "6 months left. Case worker asks about your 'exit plan.' You have none.",
            None,
            "Press E to fake confidence"
        ),

        GameObjective(
            "final_warning",
            "Three Months Left",
            "TLP sends reminder: Program ends in 90 days. Find housing or be homeless.",
            None,
            "Press E to panic again"
        ),

        # === ENDING: BACK TO SQUARE ONE ===
        GameObjective(
            "program_ending",
            "Last Week in TLP",
            "Seven days until you're homeless again. No housing secured.",
            None,
            "Press E to pack again"
        ),

        GameObjective(
            "emergency_extension",
            "Extension Denied",
            "Request for 3-month extension denied. Someone else needs the bed.",
            None,
            "Press E to understand"
        ),

        GameObjective(
            "couch_surfing_return",
            "Back to Couches",
            "Messaging everyone you know. 'Just for a few nights' you promise.",
            None,
            "Press E to swallow pride"
        ),

        GameObjective(
            "part2_reflection",
            "System Reflection",
            "TLP helped temporarily but solved nothing. The cycle continues.",
            None,
            "Press E to continue surviving"
        ),

        GameObjective(
            "part2_complete",
            "Part 2 Complete",
            "Housing programs help but don't address root causes: poverty wages and high rents.",
            None,
            "Press E for Part 3"
        )
    ]
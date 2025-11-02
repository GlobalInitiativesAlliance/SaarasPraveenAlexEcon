"""Part 2: Maintaining Housing - The Fight to Stay Housed

Continues directly from Part 1's ending where player got a crappy studio apartment.
Player is now ~20-21 years old, has been through 2+ years of housing instability.
The studio has roaches, thin walls, and a broken heater - but their name is finally on a lease.

This part explores:
1. The reality that getting housing isn't the end - keeping it is another battle
2. Tenant rights and organizing
3. Building financial stability while housed
4. The constant threat of displacement
"""

from src.core.game_world import GameObjective

def get_part2_narrative_objectives():
    """Return Part 2 objectives continuing from Part 1's studio apartment ending"""

    return [
        # === CHAPTER 1: Reality of "Success" (First Month in Studio) ===
        GameObjective(
            "studio_day_one",
            "Day 1: Your 'Home'",
            "Inventory the problems: roaches, mold, broken heater, thin walls",
            (11, 28),  # Trade school - Part 2 studio apartment narratives
            "Press E to examine apartment"
        ),

        GameObjective(
            "document_problems",
            "Document Everything",
            "Use phone to photograph all issues. Build evidence file.",
            (11, 28),  # Trade school
            "Press E to take photos"
        ),

        GameObjective(
            "first_repair_request",
            "Request Repairs",
            "Text landlord about heater. He reads it but doesn't respond.",
            (11, 28),  # Trade school
            "Press E to send text"
        ),

        GameObjective(
            "meet_neighbors",
            "Warning from Neighbors",
            "Neighbor tells you about 3 break-ins this month. Lock your windows.",
            (11, 28),  # Trade school
            "Press E to listen"
        ),

        GameObjective(
            "first_utility_bill",
            "Utility Shock",
            "$200 electric bill! Heat is electric, poorly insulated. That's 1/6 your income.",
            (11, 28),  # Trade school
            "Press E to panic"
        ),

        GameObjective(
            "budget_crisis",
            "New Math",
            "Rent $900 + Utilities $200 + Food $200 = Nothing left for anything else",
            (11, 28),  # Trade school
            "Press E to calculate"
        ),

        # === CHAPTER 2: The Increase (Month 3) ===
        GameObjective(
            "rent_increase_notice",
            "Notice on Door",
            "30-day notice: Rent increasing to $1,035. That's 15% more.",
            (55, 34),
            "Press E to read notice"
        ),

        GameObjective(
            "impossible_math_again",
            "Can't Afford This",
            "New rent = 86% of income. Literally impossible to survive.",
            (55, 34),
            "Press E to despair"
        ),

        GameObjective(
            "roommate_search",
            "Finding a Roommate",
            "Studio too small to legally share. Against lease terms anyway.",
            (8, 11),  # Library computers
            "Press E to search online"
        ),

        GameObjective(
            "second_job_hunt",
            "Need More Income",
            "Apply for night shifts. But when would you sleep?",
            (39, 51),  # Grocery store
            "Press E to apply"
        ),

        GameObjective(
            "exhaustion_sets_in",
            "Running on Empty",
            "Working 60 hours/week. Falling asleep standing up.",
            (39, 51),
            "Press E to keep going"
        ),

        # === CHAPTER 3: The Crisis (Month 4) ===
        GameObjective(
            "broken_stair_accident",
            "The Fall",
            "Broken stair you reported 3 times. Ankle sprained badly.",
            (55, 34),
            "Press E to get help"
        ),

        GameObjective(
            "emergency_room",
            "Hospital Visit",
            "6 hours in ER. Bill will come later. Can't walk properly.",
            (34, 31),  # Hospital (using existing hospital location)
            "Press E to wait"
        ),

        GameObjective(
            "missed_work",
            "No Work, No Pay",
            "Miss 5 days. No sick leave. Lost $450 income.",
            (55, 34),
            "Press E to worry"
        ),

        GameObjective(
            "short_on_rent",
            "Can't Make Rent",
            "Have $700. Rent is $900. First time being short.",
            (55, 34),
            "Press E to count again"
        ),

        GameObjective(
            "eviction_threat",
            "Pay or Quit",
            "3-day notice posted on door. Pay $900 or face eviction court.",
            (55, 34),
            "Press E to panic"
        ),

        # === CHAPTER 4: Fighting Back (Month 5) ===
        GameObjective(
            "research_rights",
            "Learning the Law",
            "Library research: Landlords must maintain habitable conditions.",
            (8, 11),  # Library
            "Press E to research"
        ),

        GameObjective(
            "legal_aid_visit",
            "Free Legal Help",
            "Legal aid says you have a case. Landlord violating multiple codes.",
            (8, 11),  # Library - for legal research/help
            "Press E to get help"
        ),

        GameObjective(
            "inspection_request",
            "Call Code Enforcement",
            "Request city inspection. Document 12 violations found.",
            (55, 34),
            "Press E to show inspector"
        ),

        GameObjective(
            "withholding_threat",
            "Legal Leverage",
            "Lawyer sends letter: Fix violations or tenant can withhold rent legally.",
            (8, 11),  # Library - legal assistance
            "Press E to send letter"
        ),

        GameObjective(
            "negotiation",
            "Landlord Backs Down",
            "Agrees to payment plan. Fixes heater only. Small victory.",
            (55, 34),
            "Press E to accept deal"
        ),

        # === CHAPTER 5: Building Stability (Month 8) ===
        GameObjective(
            "promotion_earned",
            "Shift Lead",
            "Promoted! Extra $2/hour. That's $320 more monthly.",
            (39, 51),  # Grocery store
            "Press E to celebrate"
        ),

        GameObjective(
            "night_school",
            "Community College",
            "Start business classes at night. Exhausting but worth it.",
            (54, 51),  # Classroom building
            "Press E to attend class"
        ),

        GameObjective(
            "secured_credit",
            "Building Credit",
            "Open secured card with $200. First step to credit history.",
            (12, 34),  # Bank
            "Press E to apply"
        ),

        GameObjective(
            "tenant_union",
            "Finding Community",
            "Join tenant union. Learn you're not alone in this fight.",
            (8, 11),  # Library meeting room
            "Press E to join meeting"
        ),

        GameObjective(
            "small_savings",
            "Emergency Fund",
            "Finally save $50/month. Have $400 after 8 months.",
            (12, 34),  # Bank
            "Press E to check balance"
        ),

        # === CHAPTER 6: The Ultimatum (Month 12) ===
        GameObjective(
            "building_sold",
            "New Owner",
            "Building sold to developer. Plans to renovate and triple rents.",
            (55, 34),
            "Press E to read notice"
        ),

        GameObjective(
            "cash_for_keys",
            "The Offer",
            "$2000 to leave voluntarily in 60 days. Or face eviction proceedings.",
            (55, 34),
            "Press E to consider"
        ),

        GameObjective(
            "better_apartment",
            "Found Option",
            "Decent 1-bedroom, $1200. But need perfect rental history.",
            (27, 56),  # Rental office
            "Press E to inquire"
        ),

        GameObjective(
            "impossible_choice",
            "The Decision",
            "Take money and leave? Or fight and risk eviction record?",
            (55, 34),
            "Press E to think"
        ),

        GameObjective(
            "tenant_meeting",
            "Organizing Together",
            "Other tenants want to fight. Together you might win.",
            (8, 11),  # Library
            "Press E to strategize"
        ),

        GameObjective(
            "final_decision",
            "Your Choice",
            "[Choose: Take $2000 and leave OR Fight with other tenants]",
            (55, 34),
            "Press 1 or 2 to choose"
        ),

        # === ENDING A: Take the Money ===
        GameObjective(
            "moving_out",
            "Leaving Voluntarily",
            "Pack up. Take the $2000. Use it for new deposit.",
            (55, 34),
            "Press E to pack"
        ),

        GameObjective(
            "new_apartment",
            "Slightly Better",
            "New place has working heat. Small victory in long war.",
            (27, 56),  # Rental office
            "Press E to move in"
        ),

        # === ENDING B: Fight Together ===
        GameObjective(
            "court_battle",
            "Fighting Eviction",
            "Go to court with other tenants. Judge delays eviction 6 months.",
            (27, 52),  # Housing office - for legal proceedings
            "Press E to testify"
        ),

        GameObjective(
            "still_fighting",
            "The Struggle Continues",
            "Still in crappy studio. But learned to fight back.",
            (55, 34),
            "Press E to keep fighting"
        ),

        # === CONCLUSION ===
        GameObjective(
            "part2_reflection",
            "One Year Later",
            "Survived another year. The cycle of housing instability continues...",
            None,
            "Press E to reflect"
        ),

        GameObjective(
            "part2_complete",
            "Part 2 Complete",
            "You've learned that having housing is just the beginning of the fight.",
            None,
            "Press E to continue"
        )
    ]
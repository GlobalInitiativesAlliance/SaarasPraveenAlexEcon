"""Part 1 Housing Stability - Sequential Narrative Flow

This creates a structured narrative that follows the key housing challenges:
1. Aging out with no place to live
2. Barriers to renting without co-signer or proof of income
3. Risk of eviction if roommate leaves
4. Unstable couchsurfing situations
5. Unable to afford deposit and first month's rent
6. Transitional housing ending with no next step
"""

from src.core.game_world import GameObjective

def get_part1_narrative_objectives():
    """Return Part 1 objectives in narrative sequence"""

    return [
        # === INTRODUCTION: Aging Out ===
        GameObjective(
            "housing_intro",
            "Day 1: Aging Out",
            "You turned 18 yesterday. Foster care ends today. You have $73 and nowhere to go.",
            None,
            "Press E to continue"
        ),

        GameObjective(
            "reality_check",
            "Reality Sets In",
            "No family. No co-signer. Just a backpack and a phone with 12% battery.",
            None,
            "Press E to face reality"
        ),

        # === CHAPTER 1: Trying to Rent (Barriers) ===
        GameObjective(
            "apartment_search",
            "Search for Apartments",
            "Use library computer to search for affordable housing",
            None,
            "Go to Library and press E"
        ),

        GameObjective(
            "found_listing",
            "Studio Apartment: $1400",
            "Found a studio! Cheapest in area. Need to apply quickly.",
            None,
            "Press E to view requirements"
        ),

        GameObjective(
            "application_barriers",
            "Application Requirements",
            "Need: 3x income ($4200/mo), credit score 650+, co-signer, $2800 deposit",
            None,
            "Press E to see your situation"
        ),

        GameObjective(
            "your_reality",
            "Your Situation",
            "Income: $0 | Credit: None | Co-signer: Nobody | Savings: $73",
            None,
            "Press E to feel defeated"
        ),

        GameObjective(
            "call_foster_parents",
            "Desperate Call",
            "Call old foster parents to ask for co-signing. They say no - not their problem anymore.",
            None,
            "Press E to hang up"
        ),

        GameObjective(
            "first_rejection",
            "Application Denied",
            "Without meeting ANY requirements, you can't even submit application.",
            None,
            "Press E to leave office"
        ),

        # === CHAPTER 2: Roommate Risk ===
        GameObjective(
            "facebook_search",
            "Search Social Media",
            "Look for 'Roommate Wanted' posts on Facebook groups",
            None,
            "Press E to search"
        ),

        GameObjective(
            "alex_room",
            "Found: Room for $600",
            "Alex has a spare room. No lease, cash only. Seems sketchy but affordable.",
            None,
            "Press E to message Alex"
        ),

        GameObjective(
            "meet_alex",
            "Meeting Alex",
            "Alex seems nice enough. Room is small but clean. No paperwork, just handshake.",
            None,
            "Press E to accept risk"
        ),

        GameObjective(
            "move_in_alex",
            "Moving In",
            "You move your few belongings. Finally, a roof! But no legal protection.",
            None,
            "Press E to unpack"
        ),

        GameObjective(
            "three_months_later",
            "3 Months Later",
            "Things were okay until today. Alex is moving in with their partner.",
            None,
            "Press E to panic"
        ),

        GameObjective(
            "landlord_eviction",
            "Landlord Arrives",
            "\"You're not on the lease. Get out in 3 days or I call police.\"",
            None,
            "Press E to plead"
        ),

        GameObjective(
            "pack_again",
            "Packing Again",
            "No time to find new place. Pack everything. Back to square one.",
            None,
            "Press E to pack"
        ),

        # === CHAPTER 3: Couch Surfing ===
        GameObjective(
            "text_everyone",
            "Mass Text",
            "\"Hey, weird question but can I crash for a few nights? Emergency.\"",
            None,
            "Press E to send"
        ),

        GameObjective(
            "sarah_responds",
            "Sarah's Couch - 3 Nights",
            "Old classmate Sarah: \"3 nights max. Parents don't know. Be quiet.\"",
            None,
            "Press E to accept gratefully"
        ),

        GameObjective(
            "sneaking_around",
            "Walking on Eggshells",
            "Sneaking in after parents sleep. Leaving before they wake. So stressful.",
            None,
            "Press E to stay invisible"
        ),

        GameObjective(
            "mike_floor",
            "Mike's Floor - 1 Week",
            "Sarah's time up. Mike offers floor space. 5 roommates, no privacy.",
            None,
            "Press E to move again"
        ),

        GameObjective(
            "losing_stuff",
            "Lost Belongings",
            "Forgot phone charger at Sarah's. Work uniform at Mike's. Losing track.",
            None,
            "Press E to keep going"
        ),

        GameObjective(
            "wearing_out_welcome",
            "Day 15: No Options",
            "Friends avoiding texts. Everyone helped already. Where tonight?",
            None,
            "Press E to desperation"
        ),

        # === CHAPTER 4: Savings Reality ===
        GameObjective(
            "job_search",
            "Need Income Fast",
            "Apply everywhere. Finally hired: Part-time retail, $15/hour",
            None,
            "Press E to calculate"
        ),

        GameObjective(
            "income_math",
            "Monthly Income",
            "20 hours/week x $15/hour x 4 weeks = $1,200/month before taxes",
            None,
            "Press E to see expenses"
        ),

        GameObjective(
            "expense_reality",
            "Monthly Expenses",
            "Phone $50 + Food $400 + Transport $120 + Basics $580 = $1,150",
            None,
            "Press E to see savings"
        ),

        GameObjective(
            "savings_rate",
            "Can Save: $50/month",
            "Need $2,800 for apartment. At $50/month = 56 months = 4.7 YEARS",
            None,
            "Press E to despair"
        ),

        GameObjective(
            "impossible_math",
            "The Impossible Equation",
            "Can't save while homeless. Can't get home without savings. Trapped.",
            None,
            "Press E to continue"
        ),

        # === CHAPTER 5: Transitional Housing ===
        GameObjective(
            "learn_about_tlp",
            "Transitional Living Program",
            "Case worker mentions TLP - housing for youth 18-24. Apply immediately!",
            None,
            "Press E to apply"
        ),

        GameObjective(
            "tlp_paperwork",
            "Application Process",
            "50 pages. Proof of homelessness. References. Medical records. Background check.",
            None,
            "Press E to complete"
        ),

        GameObjective(
            "waitlist_47",
            "Waitlist Position: #47",
            "Estimated wait: 6-8 months. But you need shelter TONIGHT.",
            None,
            "Press E to wait"
        ),

        GameObjective(
            "six_months_surviving",
            "6 Months Later",
            "Survived through shelters, couches, cars. Finally: TLP acceptance call!",
            None,
            "Press E to celebrate"
        ),

        GameObjective(
            "tlp_rules",
            "TLP Move-In",
            "Shared room. Curfew 10pm. Mandatory meetings. But it's STABLE!",
            None,
            "Press E to follow rules"
        ),

        GameObjective(
            "eighteen_months",
            "18 Months at TLP",
            "Worked, saved, went to community college. Time limit approaching.",
            None,
            "Press E to see savings"
        ),

        GameObjective(
            "still_not_enough",
            "Saved $1,800",
            "Better, but still need $1,000 more for apartment. 6 months left.",
            None,
            "Press E to strategize"
        ),

        # === CHAPTER 6: Time's Up ===
        GameObjective(
            "final_month",
            "TLP Ending",
            "24 months maximum reached. Must leave in 30 days. Still short $600.",
            None,
            "Press E to face reality"
        ),

        GameObjective(
            "desperate_measures",
            "Selling Everything",
            "Laptop for classes: $200. Winter coat: $40. Textbooks: $30.",
            None,
            "Press E to sacrifice"
        ),

        GameObjective(
            "found_studio",
            "Last Minute Studio",
            "Found room in bad area. Landlord accepts partial deposit. Risky, but only option.",
            None,
            "Press E to sign lease"
        ),

        GameObjective(
            "moving_day",
            "Finally: Your Own Place",
            "Roaches. Thin walls. Broken heater. But YOUR name on lease. Safe.",
            None,
            "Press E to cry with relief"
        ),

        # === EPILOGUE ===
        GameObjective(
            "reflection",
            "Two Years of Hell",
            "From foster care to your own apartment. Should've taken 2 months, took 2 years.",
            None,
            "Press E to reflect"
        ),

        GameObjective(
            "the_system",
            "System Analysis",
            "Every barrier designed to exclude. Every program underfunded. Every wait too long.",
            None,
            "Press E to understand"
        ),

        GameObjective(
            "not_alone",
            "You're Not Alone",
            "20,000 youth age out yearly. 20% become instantly homeless. You survived.",
            None,
            "Press E to continue"
        ),

        GameObjective(
            "part1_complete",
            "Part 1 Complete",
            "Housing Stability: The impossible foundation of everything else.",
            None,
            "Press E for Part 2"
        )
    ]
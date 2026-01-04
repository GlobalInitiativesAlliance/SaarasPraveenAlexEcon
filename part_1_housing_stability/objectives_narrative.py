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
            "You turned 18 yesterday. Pack your belongings and leave the foster home.",
            (29, 39),  # Foster home - where you're aging out from
            "Enter foster home to pack"
        ),

        GameObjective(
            "reality_check",
            "Find Emergency Shelter",
            "With nowhere to go, you need to find the emergency shelter for tonight.",
            (30, 11),  # Emergency shelter - first stop after aging out
            "Go to Emergency Shelter"
        ),

        # === CHAPTER 1: Trying to Rent (Barriers) ===
        GameObjective(
            "apartment_search",
            "Search for Housing",
            "Use library computer to search for affordable apartments",
            (8, 11),  # Library - actual library location
            "Go to Library"
        ),

        GameObjective(
            "found_listing",
            "Studio Apartment: $1400",
            "Found a studio! Cheapest in area. Check the rental office.",
            (27, 52),  # Rental office - aligned with building mapping
            "Go to Rental Office"
    ),

        GameObjective(
            "application_barriers",
            "Application Denied",
            "Need: 3x income ($4200/mo), credit score 650+, co-signer, $2800 deposit",
            (27, 52),  # Rental office
            "Press E to continue"
        ),

        GameObjective(
            "your_reality",
            "Harsh Reality",
            "Income: $0 | Credit: None | Co-signer: Nobody | Savings: $73",
            (27, 52),  # Rental office
            "Press E to continue"
        ),

        GameObjective(
            "call_foster_parents",
            "Desperate Call",
            "Call old foster parents to ask for co-signing. They say no - not their problem anymore.",
            (27, 52),  # Rental office - making call from there
            "Press E to hang up"
        ),

        GameObjective(
            "first_rejection",
            "Application Denied",
            "Without meeting ANY requirements, you can't even submit application.",
            (27, 52),  # Rental office
            "Press E to leave office"
        ),

        # === CHAPTER 2: Roommate Risk ===
        GameObjective(
            "facebook_search",
            "Search Social Media",
            "Look for 'Roommate Wanted' posts on Facebook groups",
            (8, 11),  # Library computers
            "Press E to search"
        ),

        GameObjective(
            "alex_room",
            "Found: Room for $600",
            "Alex has a spare room. No lease, cash only. Seems sketchy but affordable.",
            (1, 5),  # Alex's apartment location
            "Press E to message Alex"
        ),

        GameObjective(
            "meet_alex",
            "Meeting Alex",
            "Alex seems nice enough. Room is small but clean. No paperwork, just handshake.",
            (1, 5),  # Alex's apartment
            "Press E to accept risk"
        ),

        GameObjective(
            "move_in_alex",
            "Moving In",
            "You move your few belongings. Finally, a roof! But no legal protection.",
            (1, 5),  # Alex's apartment - moving in
            "Press E to unpack"
        ),

        GameObjective(
            "three_months_later",
            "3 Months Later",
            "Things were okay until today. Alex is moving in with their partner.",
            (1, 5),  # Alex's apartment - bad news
            "Press E to panic"
        ),

        GameObjective(
            "landlord_eviction",
            "Landlord Arrives",
            "\"You're not on the lease. Get out in 3 days or I call police.\"",
            (1, 5),  # Alex's apartment - eviction
            "Press E to plead"
        ),

        GameObjective(
            "pack_again",
            "Packing Again",
            "No time to find new place. Pack everything. Back to square one.",
            (1, 5),  # Alex's apartment - packing
            "Press E to pack"
        ),

        # === CHAPTER 3: Couch Surfing ===
        GameObjective(
            "text_everyone",
            "Mass Text",
            "\"Hey, weird question but can I crash for a few nights? Emergency.\"",
            (8, 11),  # Library - free WiFi to text
            "Press E to send"
        ),

        GameObjective(
            "sarah_responds",
            "Sarah's Couch - 3 Nights",
            "Old classmate Sarah: \"3 nights max. Parents don't know. Be quiet.\"",
            (4, 31),  # Sarah's place
            "Press E to accept gratefully"
        ),

        GameObjective(
            "sneaking_around",
            "Walking on Eggshells",
            "Sneaking in after parents sleep. Leaving before they wake. So stressful.",
            (4, 31),  # Sarah's place
            "Press E to stay invisible"
        ),

        GameObjective(
            "mike_floor",
            "Mike's Floor - 1 Week",
            "Sarah's time up. Mike offers floor space. 5 roommates, no privacy.",
            (54, 33),  # Mike's place (shared building with crappy_apartment)
            "Press E to move again"
        ),

        GameObjective(
            "losing_stuff",
            "Lost Belongings",
            "Forgot phone charger at Sarah's. Work uniform at Mike's. Losing track.",
            (30, 11),  # Emergency shelter - safe place
            "Press E to keep going"
        ),

        GameObjective(
            "wearing_out_welcome",
            "Day 15: No Options",
            "Friends avoiding texts. Everyone helped already. Where tonight?",
            (30, 11),  # Emergency shelter - last resort
            "Press E to desperation"
        ),

        # === CHAPTER 4: Realizing You Need Income ===
        GameObjective(
            "job_search_reality",
            "Need Income Fast",
            "Can't survive on kindness alone. Need a job to save for apartment.",
            (39, 51),  # Grocery store - got hired
            "Press E to apply"
        ),

        GameObjective(
            "income_math",
            "Monthly Income",
            "20 hours/week × $15/hour × 4 weeks = $1,200/month before taxes",
            (39, 51),  # Calculating at grocery store
            "Press E to see expenses"
        ),

        GameObjective(
            "expense_reality",
            "Monthly Expenses",
            "Phone $50 + Food $400 + Transport $120 + Basics $580 = $1,150",
            (39, 51),  # Calculating at grocery store
            "Press E to see savings"
        ),

        GameObjective(
            "savings_rate",
            "Can Save: $50/month",
            "Need $2,800 for apartment. At $50/month = 56 months = 4.7 YEARS",
            (39, 51),  # Grocery store - where you do the math
            "Press E to despair"
        ),

        GameObjective(
            "impossible_math",
            "The Impossible Equation",
            "Can't save while homeless. Can't get home without savings. Trapped.",
            (39, 51),  # Grocery store - see the trap visualization
            "Press E to realize truth"
        ),

        # === CHAPTER 5: Transitional Housing (Need alternative to 4.7 year wait) ===
        GameObjective(
            "learn_about_tlp",
            "Transitional Living Program",
            "Case worker mentions TLP - housing for youth 18-24. Apply immediately!",
            (27, 52),  # Housing office - proper location
            "Press E to apply"
        ),

        GameObjective(
            "tlp_paperwork",
            "Application Process",
            "50 pages. Proof of homelessness. References. Medical records. Background check.",
            (27, 52),  # Housing office
            "Press E to complete"
        ),

        GameObjective(
            "waitlist_47",
            "Waitlist Position: #47",
            "Estimated wait: 6-8 months. But you need shelter TONIGHT.",
            (27, 52),  # Housing office
            "Press E to wait"
        ),

        GameObjective(
            "six_months_surviving",
            "6 Months Later",
            "Survived through shelters, couches, cars. Finally: TLP acceptance call!",
            (30, 11),  # Getting call at school
            "Press E to celebrate"
        ),

        GameObjective(
            "tlp_rules",
            "Success: TLP Acceptance!",
            "After 6 months of homelessness, you made it. Safe housing for 24 months!",
            (29, 39),  # TLP housing - your new home
            "Enter TLP to start your new life"
        ),

        # === PART 1 COMPLETE: Success! ===
        GameObjective(
            "part1_complete",
            "Part 1 Complete: Housing Secured",
            "You survived the impossible. TLP provides 24 months of stability to build your future.",
            None,  # No specific location - triggers automatically
            "Transitioning to Part 2..."
        )
    ]

"""Part 1 Housing & Stability - Detailed Storyline with Real Tasks"""

from src.core.game_world import GameObjective

def get_part1_objectives():
    """Return all Part 1 objectives - Housing & Stability storyline
    
    Based on the real experiences of youth aging out of foster care.
    """
    return [
        # === INTRO ===
        GameObjective(
            "housing_intro", 
            "Day 1: Reality Check",
            "You just turned 18. The system is done with you.",
            None,
            "Watch the intro"
        ),
        
        # === IMMEDIATE CRISIS - Day 1-3 ===
        GameObjective(
            "packed_belongings",
            "Pack Your Life",
            "Foster parents gave you 2 hours to pack. Everything you own fits in a garbage bag.",
            None,
            "Press E to pack"
        ),
        
        GameObjective(
            "cash_reality",
            "Count Your Money",
            "You have $73. That's it. No savings, no safety net.",
            None,
            "Press E to check wallet"
        ),
        
        GameObjective(
            "first_night",
            "Find Tonight's Shelter",
            "It's 6 PM. Where will you sleep? Sarah said you could crash for 3 nights max.",
            None,
            "Press E to text Sarah"
        ),
        
        # === COUCH SURFING - Day 3-10 ===
        GameObjective(
            "sarah_couch_rules",
            "Sarah's House Rules",
            "No guests, be out by 8am, don't use the kitchen, her parents can't know.",
            None,
            "Press E to agree"
        ),
        
        GameObjective(
            "mike_couch_unsafe",
            "Mike's Offer",
            "Mike says you can stay, but his roommates party hard and you don't feel safe.",
            None,
            "Press E to decline/accept"
        ),
        
        GameObjective(
            "couch_exhausted",
            "Running Out of Couches",
            "You've stayed with 4 different people. Everyone's patience is wearing thin.",
            None,
            "Press E to check messages"
        ),
        
        # === APARTMENT HUNTING - Day 10-15 ===
        GameObjective(
            "apartment_search",
            "Search Craigslist",
            "Every listing: 'NO SECTION 8, MUST HAVE 3X INCOME, 650+ CREDIT'",
            None,
            "Press E to search"
        ),
        
        GameObjective(
            "viewing_scheduled",
            "Apartment Viewing",
            "Finally! A viewing at 2 PM. But you work until 3 PM...",
            None,
            "Press E to decide"
        ),
        
        GameObjective(
            "application_fee",
            "$45 Application Fee",
            "Non-refundable. That's more than half your money. They'll probably reject you anyway.",
            None,
            "Press E to pay/skip"
        ),
        
        GameObjective(
            "cosigner_needed",
            "Co-Signer Required",
            "'Do you have a parent or guardian who can co-sign?' You have nobody.",
            None,
            "Press E to explain"
        ),
        
        GameObjective(
            "application_denied",
            "DENIED",
            "'Insufficient income history.' You've been working for 2 weeks.",
            None,
            "Press E to continue"
        ),
        
        # === ROOMMATE SEARCH - Day 15-20 ===
        GameObjective(
            "facebook_roommates",
            "Facebook Roommate Groups",
            "Posting: '18yo, clean, working, need room ASAP, budget $400'",
            None,
            "Press E to post"
        ),
        
        GameObjective(
            "alex_response",
            "Alex Has a Room",
            "'$600/month, no lease, cash only, can move in today.' Seems sketchy but...",
            None,
            "Press E to meet Alex"
        ),
        
        GameObjective(
            "move_in_alex",
            "Moving In",
            "No paperwork. No rights. If Alex decides they don't like you, you're homeless again.",
            None,
            "Press E to unpack"
        ),
        
        # === TRANSITIONAL HOUSING - Day 20-30 ===
        GameObjective(
            "tlp_discovery",
            "Transitional Living Program",
            "Your case worker mentions TLP. 18-24 months of housing... if you qualify.",
            None,
            "Press E to learn more"
        ),
        
        GameObjective(
            "tlp_application",
            "TLP Application",
            "20 pages. Proof of homelessness. Mental health eval. Background check. References.",
            None,
            "Press E at office"
        ),
        
        GameObjective(
            "tlp_interview",
            "TLP Interview",
            "Interview at 10 AM Tuesday. You're scheduled to work. Missing work = no money.",
            None,
            "Press E to choose"
        ),
        
        GameObjective(
            "tlp_waitlist",
            "Waitlist #47",
            "Congratulations! You're on the waitlist. Estimated wait: 6-8 months.",
            None,
            "Press E to accept"
        ),
        
        # === EMERGENCY SHELTER - Day 25-30 ===
        GameObjective(
            "alex_eviction",
            "Alex Kicks You Out",
            "Alex's ex is moving back in. You have 24 hours to leave. No warning.",
            None,
            "Press E to pack"
        ),
        
        GameObjective(
            "shelter_search",
            "Find Emergency Shelter",
            "Calling shelters: 'Full.' 'Full.' '30-day wait.' 'Must be sober 90 days.'",
            None,
            "Press E to call next"
        ),
        
        GameObjective(
            "youth_shelter",
            "Youth Shelter Has Space",
            "One bed available. Curfew 8 PM. Out by 6 AM. 3-night maximum stay.",
            None,
            "Press E to check in"
        ),
        
        GameObjective(
            "shelter_rules",
            "Shelter Reality",
            "Your stuff was stolen. Can't work night shifts. Miss curfew = banned.",
            None,
            "Press E to adapt"
        ),
        
        # === WORK CONFLICTS - Throughout ===
        GameObjective(
            "work_schedule_conflict",
            "Scheduled During Appointment",
            "Housing office only open 9-3. You work 8-4. Manager won't give time off.",
            None,
            "Press E to decide"
        ),
        
        GameObjective(
            "fired_for_absence",
            "Employment Terminated",
            "Missed one shift for TLP interview. 'We need reliable people.' Fired.",
            None,
            "Press E to clear locker"
        ),
        
        GameObjective(
            "no_address_job",
            "Job Application Problem",
            "'Current address?' The shelter won't let you use theirs. Can't put 'homeless'.",
            None,
            "Press E to lie/truth"
        ),
        
        # === SYSTEMATIC BARRIERS ===
        GameObjective(
            "deposit_math",
            "Deposit Reality Check",
            "$2800 needed. You make $12/hr, 25 hrs/week. After expenses: save $50/month.",
            None,
            "Press E to calculate"
        ),
        
        GameObjective(
            "id_expired",
            "ID Expired",
            "Need ID for everything. DMV needs proof of address. You don't have an address.",
            None,
            "Press E to problem-solve"
        ),
        
        GameObjective(
            "phone_shutoff",
            "Phone Service Ended",
            "No money for phone bill. Now can't receive callbacks for jobs or housing.",
            None,
            "Press E to find wifi"
        ),
        
        # === WINTER APPROACHING ===
        GameObjective(
            "winter_prep",
            "October Cold",
            "Sleeping outside tonight. 38 degrees. Your jacket was stolen at the shelter.",
            None,
            "Press E to survive"
        ),
        
        GameObjective(
            "storage_unit",
            "Storage or Stuff?",
            "$90 for storage unit or keep carrying everything. Storage = no food for a week.",
            None,
            "Press E to choose"
        ),
        
        # === SMALL VICTORIES ===
        GameObjective(
            "shower_access",
            "Found Shower Access",
            "Gym has 7-day trial. You can shower! Feel human again. Applied to 3 jobs.",
            None,
            "Press E to clean up"
        ),
        
        GameObjective(
            "food_bank",
            "Food Bank Wednesday",
            "3-hour wait. Got groceries but nowhere to cook. Trading canned goods for ready-to-eat.",
            None,
            "Press E to wait"
        ),
        
        GameObjective(
            "library_refuge",
            "Library Safe Space",
            "Warm, quiet, free wifi. Applied for 10 jobs. Security says you can't sleep here.",
            None,
            "Press E to stay awake"
        ),
        
        # === CHRONIC CRISIS ===
        GameObjective(
            "three_months_later",
            "Day 90",
            "Still homeless. Lost 20 pounds. Haven't talked to friends - too ashamed.",
            None,
            "Press E to continue"
        ),
        
        GameObjective(
            "health_declining",
            "Getting Sick",
            "Chest cold for 2 weeks. Can't rest. Can't afford doctor. Getting worse.",
            None,
            "Press E to power through"
        ),
        
        GameObjective(
            "giving_up",
            "Rock Bottom",
            "Why try? Every system failed you. Nobody cares if you live or die.",
            None,
            "Press E to..."
        ),
        
        # === GLIMMER OF HOPE ===
        GameObjective(
            "outreach_worker",
            "Street Outreach",
            "'Hey, I'm James from Youth Services. Want some food? Let's talk.'",
            None,
            "Press E to trust"
        ),
        
        GameObjective(
            "rapid_rehousing",
            "Rapid Rehousing Program",
            "New program. They'll pay deposit + 3 months rent. You just need to maintain it after.",
            None,
            "Press E to apply"
        ),
        
        GameObjective(
            "studio_apartment",
            "Your Own Place",
            "Studio apartment. Your name on the lease. A door that locks. You cry.",
            None,
            "Press E to unlock door"
        ),
        
        GameObjective(
            "first_night_housed",
            "First Night",
            "Can't sleep. Keep checking the door. Is this real? Will they take it away?",
            None,
            "Press E to breathe"
        ),
        
        # === EPILOGUE ===
        GameObjective(
            "six_months_stable",
            "6 Months Later",
            "Still housed. Working full-time. Saved $400. Helping another youth with resources.",
            None,
            "Press E to reflect"
        ),
        
        GameObjective(
            "part1_complete",
            "Housing Crisis Survived",
            "You made it. Millions don't. The system needs to change.",
            None,
            "Press SPACE to continue"
        )
    ]
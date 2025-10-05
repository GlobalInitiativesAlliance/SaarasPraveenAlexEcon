"""Part 1 Housing & Stability Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part1_objectives():
    """Return all Part 1 objectives - Housing & Stability storyline
    
    This part focuses on the housing crisis facing youth aging out of foster care.
    Tasks are non-sequential and represent different challenges and choices.
    """
    return [
        # Introduction
        GameObjective(
            "housing_intro",
            "Aging Out",
            "You're turning 18 tomorrow. Foster care ends. Where will you live?",
            None,
            "Press E to face reality"
        ),
        
        # === TASK MENU - Player can choose which housing challenge to tackle ===
        GameObjective(
            "housing_menu",
            "Housing Challenges",
            "Choose which housing situation to explore",
            None,
            "Press E to see options"
        ),
        
        # --- Option 1: Try to Rent an Apartment ---
        GameObjective(
            "apartment_search",
            "Apartment Hunt",
            "Search for affordable apartments online",
            None,
            "Press E to search listings"
        ),
        GameObjective(
            "rental_application",
            "Rental Barriers",
            "Need: Co-signer, 3x income proof, credit check, $2800 deposit",
            None,
            "Press E to see requirements"
        ),
        GameObjective(
            "cosigner_denial",
            "No Co-Signer",
            "Foster parents won't co-sign. No family to ask. Application denied.",
            None,
            "Press E to accept rejection"
        ),
        
        # --- Option 2: Find a Roommate ---
        GameObjective(
            "roommate_search",
            "Find Roommate",
            "Look for shared housing on social media",
            None,
            "Press E to search"
        ),
        GameObjective(
            "roommate_found",
            "Potential Roommate",
            "Alex has a room for $600/month. Seems nice but you don't know them.",
            None,
            "Press E to meet Alex"
        ),
        GameObjective(
            "roommate_risk",
            "Risky Situation",
            "No lease. If Alex leaves, you're homeless. But it's your only option.",
            None,
            "Press E to decide"
        ),
        GameObjective(
            "roommate_leaves",
            "Eviction Notice",
            "After 3 months, Alex moves out. Landlord wants you gone in 3 days.",
            None,
            "Press E to pack belongings"
        ),
        
        # --- Option 3: Couch Surfing ---
        GameObjective(
            "couch_surf_start",
            "Couch Surfing",
            "Ask friends from school if you can crash for a few nights",
            None,
            "Press E to text friends"
        ),
        GameObjective(
            "sarah_couch",
            "Sarah's Couch",
            "Sarah says 3 nights max. Her parents don't like guests.",
            None,
            "Press E to accept"
        ),
        GameObjective(
            "mike_couch",
            "Mike's Floor",
            "After Sarah's, Mike offers his floor for a week. No privacy.",
            None,
            "Press E to move again"
        ),
        GameObjective(
            "couch_exhaustion",
            "Wearing Out Welcome",
            "Friends avoiding you. Running out of couches. So tired of moving.",
            None,
            "Press E to keep searching"
        ),
        
        # --- Option 4: Transitional Housing ---
        GameObjective(
            "tlp_application",
            "Transitional Living",
            "Apply for Transitional Living Program (TLP) - 18-24 months max",
            None,
            "Press E to apply"
        ),
        GameObjective(
            "tlp_waitlist",
            "Waitlist #47",
            "You're #47 on waitlist. Current wait: 6-8 months. But you need housing NOW.",
            None,
            "Press E to wait"
        ),
        GameObjective(
            "tlp_accepted",
            "TLP Acceptance",
            "Finally accepted! Shared room, curfews, mandatory programs.",
            None,
            "Press E to move in"
        ),
        GameObjective(
            "tlp_ending",
            "Time's Up",
            "18 months at TLP ending. Still can't afford market rent. Now what?",
            None,
            "Press E to face deadline"
        ),
        
        # --- Option 5: Emergency Shelter ---
        GameObjective(
            "shelter_search",
            "Emergency Shelter",
            "No other options. Look for youth shelter beds.",
            None,
            "Press E to search"
        ),
        GameObjective(
            "shelter_full",
            "No Beds Available",
            "Youth shelter: Full. Adult shelter: Too dangerous at 18.",
            None,
            "Press E to keep looking"
        ),
        GameObjective(
            "shelter_rules",
            "Shelter Life",
            "Finally found bed. Must leave by 6am daily. Can't store belongings.",
            None,
            "Press E to accept rules"
        ),
        
        # --- Option 6: Try to Save for Deposit ---
        GameObjective(
            "save_deposit",
            "Save for Deposit",
            "Need $2800 for deposit + first month. Current savings: $73",
            None,
            "Press E to make plan"
        ),
        GameObjective(
            "work_calculate",
            "Do the Math",
            "At $15/hr, 20hrs/week = $1200/month. Expenses: $1150. Save: $50/month.",
            None,
            "Press E to see timeline"
        ),
        GameObjective(
            "deposit_timeline",
            "56 Months to Save",
            "Will take 4.5 years to save deposit. Need housing TODAY.",
            None,
            "Press E to despair"
        ),
        
        # --- Recurring Challenges ---
        GameObjective(
            "address_needed",
            "Need Address",
            "Job application needs address. Using friend's. Hope they don't check.",
            None,
            "Press E to lie on form"
        ),
        GameObjective(
            "belongings_stolen",
            "Belongings Stolen",
            "Left backpack at shelter. Everything gone: ID, phone charger, clothes.",
            None,
            "Press E to start over"
        ),
        GameObjective(
            "shower_access",
            "Hygiene Crisis",
            "Haven't showered in 3 days. Gym membership expired. Work tomorrow.",
            None,
            "Press E to problem-solve"
        ),
        GameObjective(
            "winter_coming",
            "Winter Approaching",
            "Getting colder. Current couch surfing ending. Scared of freezing.",
            None,
            "Press E to find warmth"
        ),
        
        # --- Support Systems ---
        GameObjective(
            "case_worker",
            "Case Worker Meeting",
            "Old case worker offers one-time emergency fund: $500. Won't solve everything.",
            None,
            "Press E to accept help"
        ),
        GameObjective(
            "support_group",
            "Foster Youth Group",
            "Meet others facing same challenges. Share resources and couches.",
            None,
            "Press E to connect"
        ),
        GameObjective(
            "document_help",
            "Document Recovery",
            "Social worker helps replace stolen ID and birth certificate. Takes 6 weeks.",
            None,
            "Press E to start process"
        ),
        
        # --- Consequences and Outcomes ---
        GameObjective(
            "job_lost",
            "Lost Job",
            "Missed shifts while moving between couches. Fired. Income gone.",
            None,
            "Press E to accept"
        ),
        GameObjective(
            "school_dropped",
            "Dropped Out",
            "Can't focus on homework without stable housing. GPA tanked. Withdrew.",
            None,
            "Press E to give up education"
        ),
        GameObjective(
            "health_declining",
            "Health Impact",
            "Constant stress, poor sleep, irregular meals. Getting sick often.",
            None,
            "Press E to ignore symptoms"
        ),
        GameObjective(
            "police_harassment",
            "Move Along",
            "Police say can't sleep in car. Ticket for 'loitering'. Now have record.",
            None,
            "Press E to accept ticket"
        ),
        
        # --- Small Victories ---
        GameObjective(
            "found_room",
            "Temporary Relief",
            "Found room for 2 months! Overpriced but stable. Can breathe briefly.",
            None,
            "Press E to enjoy moment"
        ),
        GameObjective(
            "laundry_day",
            "Clean Clothes",
            "Friend let you do laundry. First time in weeks. Feel human again.",
            None,
            "Press E to appreciate"
        ),
        GameObjective(
            "hot_meal",
            "Community Dinner",
            "Church serving free dinner. Hot food and kind people. Not alone tonight.",
            None,
            "Press E to eat"
        ),
        
        # --- End States (Multiple Possible Endings) ---
        GameObjective(
            "chronic_homelessness",
            "Chronic Homelessness",
            "2 years later. Still unstable. System failed you completely.",
            None,
            "Press E to survive another day"
        ),
        GameObjective(
            "stable_housing",
            "Finally Stable",
            "After 3 years of struggle, found subsidized housing. Healing begins.",
            None,
            "Press E to rest"
        ),
        GameObjective(
            "helping_others",
            "Paying It Forward",
            "Stable now. Offering couch to another youth aging out. Cycle continues.",
            None,
            "Press E to help"
        ),
        
        # Part 1 Complete
        GameObjective(
            "part1_complete",
            "Part 1 Complete",
            "You've experienced the housing instability facing foster youth",
            None,
            "Press E to continue"
        )
    ]
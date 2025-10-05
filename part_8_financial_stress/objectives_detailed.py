"""Part 8: Financial Collapse - When All Systems Fail At Once"""

from src.core.game_world import GameObjective

def get_part8_objectives():
    """Financial stress and survival decisions facing homeless youth"""
    return [
        # === THE SETUP - You finally had stability ===
        GameObjective(
            "three_months_stable",
            "Finally Stable",
            "3 months in your apartment. Full-time job. Building savings. Then...",
            None,
            "Press E to continue"
        ),
        
        # === THE CATALYST ===
        GameObjective(
            "hours_cut",
            "Hours Cut",
            "'Sorry, we're cutting everyone to 20 hours. Economy's tough.'",
            None,
            "Press E to panic"
        ),
        
        GameObjective(
            "income_calculation",
            "New Reality",
            "Income: $600/month. Rent: $850. The math doesn't work.",
            None,
            "Press E to calculate"
        ),
        
        # === WEEK 1: IMMEDIATE DECISIONS ===
        GameObjective(
            "check_savings",
            "Savings Account",
            "$340 saved. That covers... nothing. Rent due in 12 days.",
            None,
            "Press E to check balance"
        ),
        
        GameObjective(
            "food_or_rent",
            "First Choice",
            "Grocery money = $120 toward rent. Ramen for 2 weeks?",
            None,
            "Press E to choose"
        ),
        
        GameObjective(
            "second_job_search",
            "Desperation Applications",
            "Applied to 47 jobs in 3 days. Need something NOW.",
            None,
            "Press E to refresh email"
        ),
        
        # === WEEK 2: SPIRALING ===
        GameObjective(
            "phone_bill_due",
            "Phone Shutoff Warning",
            "$85 phone bill. Need phone for job callbacks. But rent...",
            None,
            "Press E to decide"
        ),
        
        GameObjective(
            "payday_loan_ad",
            "Quick Cash Ad",
            "'Need money fast? $300 today! No credit check!'",
            None,
            "Press E to consider"
        ),
        
        GameObjective(
            "loan_terms",
            "The Fine Print",
            "$300 loan = $390 due in 2 weeks. That's 30% interest but...",
            None,
            "Press E to sign/decline"
        ),
        
        GameObjective(
            "plasma_donation",
            "Selling Plasma",
            "$70 for first donation. Feel dizzy but need the money.",
            None,
            "Press E to donate"
        ),
        
        # === WEEK 3: CASCADING FAILURES ===
        GameObjective(
            "rent_late",
            "5-Day Pay or Quit",
            "Official eviction notice. $850 + $100 late fee = $950.",
            None,
            "Press E to read notice"
        ),
        
        GameObjective(
            "car_breakdown",
            "Car Won't Start",
            "Need car for work. Repair estimate: $400. You have $47.",
            None,
            "Press E to call mechanic"
        ),
        
        GameObjective(
            "missed_shift",
            "Can't Get to Work",
            "No car = missed shift = final warning. One more and fired.",
            None,
            "Press E to explain"
        ),
        
        GameObjective(
            "loan_due",
            "Payday Loan Due",
            "Owe $390. Have $47. They're calling 10 times a day.",
            None,
            "Press E to ignore calls"
        ),
        
        # === WEEK 4: IMPOSSIBLE CHOICES ===
        GameObjective(
            "food_pantry_closed",
            "Food Pantry",
            "'Sorry, we're out. Try again Thursday.' Haven't eaten in 2 days.",
            None,
            "Press E to leave hungry"
        ),
        
        GameObjective(
            "eviction_court",
            "Court Date Set",
            "Eviction hearing Tuesday 9 AM. Same time as job interview.",
            None,
            "Press E to choose"
        ),
        
        GameObjective(
            "utilities_shutoff",
            "Power Disconnected",
            "No electricity. Food spoiling. Charging phone at library.",
            None,
            "Press E to sit in dark"
        ),
        
        GameObjective(
            "rollover_loan",
            "Loan Rollover Offer",
            "'Can't pay? Roll it over! Just $117 fee!' Now owe $507.",
            None,
            "Press E to trap deeper"
        ),
        
        # === MENTAL TOLL ===
        GameObjective(
            "anxiety_attack",
            "Can't Breathe",
            "Panic attack at work. Manager says 'pull yourself together.'",
            None,
            "Press E to hide in bathroom"
        ),
        
        GameObjective(
            "avoiding_reality",
            "Unopened Mail",
            "Stack of bills. Shutoff notices. Court summons. Can't look.",
            None,
            "Press E to avoid"
        ),
        
        GameObjective(
            "isolation_complete",
            "Cutting Off Friends",
            "Too ashamed to answer texts. They can't help anyway.",
            None,
            "Press E to go dark"
        ),
        
        # === THE CRASH ===
        GameObjective(
            "final_paycheck",
            "Last Check",
            "Fired for missing shift (court appearance). $240 final pay.",
            None,
            "Press E to calculate"
        ),
        
        GameObjective(
            "everything_due",
            "Total Owed",
            "Rent: $950, Loan: $507, Phone: $85, Utilities: $120 = $1,662",
            None,
            "Press E to laugh/cry"
        ),
        
        GameObjective(
            "eviction_day",
            "Lock Changed",
            "Came home to new locks. Your stuff in trash bags by door.",
            None,
            "Press E to collect belongings"
        ),
        
        # === SURVIVAL MODE ===
        GameObjective(
            "storage_or_food",
            "What to Save",
            "$240 final pay. Storage unit: $90. Food: $50. Phone: $85?",
            None,
            "Press E to prioritize"
        ),
        
        GameObjective(
            "sleep_in_car",
            "First Night in Car",
            "Walmart parking lot. Security knocking. 'Can't stay here.'",
            None,
            "Press E to drive"
        ),
        
        GameObjective(
            "gas_empty",
            "Running on Empty",
            "$12 left. Gas light on. Where do you even go?",
            None,
            "Press E to coast"
        ),
        
        # === HITTING BOTTOM ===
        GameObjective(
            "everything_lost",
            "Day 30",
            "Lost apartment, job, car (repo'd), phone. Back to nothing.",
            None,
            "Press E to exist"
        ),
        
        GameObjective(
            "debt_collectors",
            "Collections",
            "Debt sold to collectors. Threatening legal action. For being poor.",
            None,
            "Press E to ignore"
        ),
        
        GameObjective(
            "credit_destroyed",
            "Credit Score: 402",
            "Won't qualify for anything for 7 years. You're 21.",
            None,
            "Press E to accept"
        ),
        
        # === THE LESSON ===
        GameObjective(
            "reflection",
            "The Poverty Trap",
            "Started with stable housing. One hour cut. Dominoes fell.",
            None,
            "Press E to understand"
        ),
        
        GameObjective(
            "systemic_failure",
            "Individual Problem?",
            "You did everything right. The system is designed to fail you.",
            None,
            "Press E to see truth"
        ),
        
        GameObjective(
            "part8_complete",
            "Financial Collapse Complete",
            "No safety net. No room for error. This is poverty in America.",
            None,
            "Press SPACE to finish"
        )
    ]
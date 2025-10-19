"""Part 4 Credit, Debt, and Financial Systems Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part4_objectives():
    """Return all Part 4 objectives - Credit & Debt storyline"""
    return [
        # Test Event 1 - Payday Loan
        GameObjective(
            "need_quick_cash",
            "Emergency Cash Needed",
            "Your car broke down and you need $500 for repairs",
            None,
            "Press E to explore options"
        ),
        GameObjective(
            "payday_loan_store",
            "Visit Payday Lender",
            "No other options - visit the payday loan store",
            None,
            "Press E to enter store"
        ),
        GameObjective(
            "loan_terms",
            "Shocking Terms",
            "Borrow $500, pay back $650 in two weeks (390% APR)",
            None,
            "Press E to accept (no choice)"
        ),
        
        # Test Event 2 - Debt Spiral
        GameObjective(
            "cant_repay",
            "Payment Due",
            "Two weeks later - you don't have $650",
            None,
            "Press E to face the problem"
        ),
        GameObjective(
            "rollover_loan",
            "Loan Rollover",
            "Pay $150 fee to extend loan. Now owe $800.",
            None,
            "Press E to rollover"
        ),
        GameObjective(
            "collections_call",
            "Debt Collectors",
            "Constant calls. Threats to garnish wages.",
            None,
            "Press E to answer phone"
        ),
        GameObjective(
            "part4_complete",
            "Part 4 Complete",
            "Trapped in the payday loan cycle",
            None,
            "Press E to continue"
        )
    ]
"""Part 2 Housing Crisis Storyline Objectives"""

from src.core.game_world import GameObjective

def get_part2_objectives():
    """Return all Part 2 objectives - Housing Crisis storyline"""
    return [
        # Day 1 - Morning
        GameObjective(
            "foster_home_class",
            "Attend Tenant Rights Class",
            "Go to the Foster Home and attend the tenant rights class (8:00 AM - 3:00 PM)",
            None,
            "Press E to enter class"
        ),
        GameObjective(
            "community_center_workshop",
            "Life Skills Workshop",
            "Head to the Community Center for the Life Skills Workshop",
            None,
            "Press E to enter workshop"
        ),
        GameObjective(
            "submit_application",
            "Submit TLP Application",
            "Apply for Transitional Living Program housing",
            None,
            "Press E to submit application"
        ),
        # Day 1 - Evening
        GameObjective(
            "pack_belongings",
            "Move to TLP Apartment",
            "Pack and move into your new TLP apartment (5:00 PM - 9:00 PM)",
            None,
            "Press E to start packing"
        ),
        GameObjective(
            "meet_roommate",
            "Meet Your Roommate",
            "Return to apartment and meet your new roommate",
            None,
            "Press E to greet roommate"
        ),
        GameObjective(
            "sleep_day1",
            "Rest for Tomorrow",
            "Go to sleep in your new apartment",
            None,
            "Press E to sleep"
        ),
        # Day 2 - Crisis
        GameObjective(
            "discover_emergency",
            "Emergency: Roommate Gone!",
            "Check your apartment - something's wrong",
            None,
            "Press E to investigate"
        ),
        GameObjective(
            "receive_notices",
            "Urgent Notices",
            "You've received a 3-day pay or quit notice and utility shutoff warning",
            None,
            "Press E to read notices"
        ),
        GameObjective(
            "housing_services",
            "Visit Housing Services",
            "Go to Housing Services Office with your documents",
            None,
            "Press E to enter office"
        ),
        GameObjective(
            "emergency_assistance",
            "Emergency Housing Help",
            "Accept emergency housing assistance",
            None,
            "Press E to proceed"
        ),
        GameObjective(
            "pack_essentials",
            "Pack Essential Items",
            "Return to apartment and pack essentials for temporary housing",
            None,
            "Press E to pack"
        ),
        # Day 3 - Recovery
        GameObjective(
            "return_housing_services",
            "Return to Housing Services",
            "Come back at 3:00 PM as instructed",
            None,
            "Press E to enter"
        ),
        GameObjective(
            "select_roommate",
            "Choose New Roommate",
            "Review roommate profiles and select a compatible match",
            None,
            "Press E to view profiles"
        ),
        GameObjective(
            "roommate_agreement",
            "Set Up Living Agreement",
            "Go to apartment and establish roommate agreement",
            None,
            "Press E to start agreement"
        ),
        GameObjective(
            "grocery_shopping",
            "Shop for Groceries",
            "Visit grocery store and learn to split costs with roommate",
            None,
            "Press E to shop"
        ),
        # Day 4 - New Crisis
        GameObjective(
            "heater_broken",
            "Emergency: No Heat!",
            "Your heater is broken and you have a test tomorrow",
            None,
            "Press E to assess situation"
        ),
        GameObjective(
            "contact_help",
            "Get Help for Heater",
            "Contact TLP case manager or landlord for emergency repair",
            None,
            "Press E to make calls"
        ),
        GameObjective(
            "resolution",
            "Crisis Resolved",
            "Maintenance is on the way - you've learned to advocate for yourself",
            None,
            "Press E to continue"
        )
    ]
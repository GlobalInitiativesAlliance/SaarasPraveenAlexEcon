#!/usr/bin/env python3
"""
Final test script to verify all auto-skip fixes
"""

import sys
import os
import pygame

# Initialize pygame
pygame.init()

sys.path.append('/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon')

from part_2_healthcare.interiors.healthcare_apartment_interior import HealthcareApartmentInterior

def test_all_activity_objectives():
    """Test that all activity-based objectives don't auto-complete"""
    print("🧪 Testing All Activity-Based Objective Auto-Skip Fixes")
    print("=" * 60)

    # Create mock objects
    class MockObjectiveManager:
        def __init__(self):
            self.complete_called = False
            self.current_obj_id = None

        def complete_current_objective(self):
            self.complete_called = True
            print(f"⚠️  complete_current_objective() was called for {self.current_obj_id}!")

        def get_current_objective(self):
            class MockObjective:
                def __init__(self, obj_id):
                    self.id = obj_id
            return MockObjective(self.current_obj_id)

    class MockGame:
        def __init__(self):
            self.objective_manager = MockObjectiveManager()

    mock_room_data = {}
    mock_building_pos = (0, 0)

    # Create interior
    interior = HealthcareApartmentInterior(MockGame(), mock_room_data, mock_building_pos)

    # Test objectives that should NOT auto-complete (activity-based)
    activity_objectives = [
        ('check_mailbox', 'sort_mail'),
        ('medicaid_notice', 'read_notice'),
        ('therapy_reminder', 'check_phone'),
        ('insurance_panic', 'panic_about_coverage'),
        ('therapist_call_options', 'answer_call'),
        ('therapy_payment_decision', 'make_payment_decision'),
    ]

    print("Testing activity-based objectives (should NOT auto-complete):")
    print("-" * 50)

    all_passed = True

    for obj_id, interaction_name in activity_objectives:
        print(f"\n🔍 Testing {obj_id}")

        # Reset state
        interior.game.objective_manager.complete_called = False
        interior.game.objective_manager.current_obj_id = obj_id
        interior.completed_interactions.clear()

        # Add the interaction to completed interactions
        interior.completed_interactions.add(interaction_name)
        print(f"   ✅ Added '{interaction_name}' to completed_interactions")

        # Call update_objective_display
        interior.update_objective_display()

        # Check if objective was auto-completed (it should NOT be)
        if interior.game.objective_manager.complete_called:
            print(f"   ❌ FAILED: {obj_id} was auto-completed (should be activity-based)")
            all_passed = False
        else:
            print(f"   ✅ SUCCESS: {obj_id} was NOT auto-completed (correct behavior)")

    # Test objectives that SHOULD auto-complete (interaction-based)
    interaction_objectives = [
        ('start_apartment_morning', 'get_up'),
        ('travel_to_clinic', 'leave_for_clinic'),
        ('caseworker_guidance', 'answer_caseworker'),
        ('coverage_restored', 'read_good_news'),
    ]

    print("\n\nTesting interaction-based objectives (should auto-complete):")
    print("-" * 50)

    for obj_id, interaction_name in interaction_objectives:
        print(f"\n🔍 Testing {obj_id}")

        # Reset state
        interior.game.objective_manager.complete_called = False
        interior.game.objective_manager.current_obj_id = obj_id
        interior.completed_interactions.clear()

        # Add the interaction to completed interactions
        interior.completed_interactions.add(interaction_name)
        print(f"   ✅ Added '{interaction_name}' to completed_interactions")

        # Call update_objective_display
        interior.update_objective_display()

        # Check if objective was auto-completed (it SHOULD be)
        if interior.game.objective_manager.complete_called:
            print(f"   ✅ SUCCESS: {obj_id} was auto-completed (correct behavior)")
        else:
            print(f"   ❌ FAILED: {obj_id} was NOT auto-completed (should be interaction-based)")
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 SUMMARY OF FIXES:")
        print("   ✅ therapist_call_options: Fixed auto-skip issue")
        print("   ✅ therapy_payment_decision: Fixed auto-skip issue")
        print("   ✅ All other objectives: Working correctly")
        print("\n🎮 EXPECTED GAME FLOW:")
        print("   1. Clinic activities complete normally")
        print("   2. application_approved completes")
        print("   3. Player returns to apartment for therapist_call_options")
        print("   4. Player presses E → TherapistCallActivity launches")
        print("   5. Player goes through phone call and makes choice")
        print("   6. Activity completes → advances to therapy_payment_decision")
        print("   7. Player presses E → TherapyPaymentDecisionActivity launches")
        print("   8. Player makes final payment decision")
        print("   9. Activity completes → continues to next objective")
        print("   10. NO MORE AUTO-SKIPPING!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the failed objectives above.")
        return False

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE AUTO-SKIP FIX VERIFICATION")
    print("=" * 70)

    if test_all_activity_objectives():
        print("\n🏆 ALL AUTO-SKIP ISSUES FIXED! 🏆")
    else:
        print("\n❌ ADDITIONAL FIXES NEEDED!")

    print("\n" + "=" * 70)
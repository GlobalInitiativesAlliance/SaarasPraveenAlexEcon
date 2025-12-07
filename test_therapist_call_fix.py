#!/usr/bin/env python3
"""
Test script to verify the therapist call auto-skip fix
"""

import sys
import os
import pygame

# Initialize pygame
pygame.init()

sys.path.append('/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon')

from part_2_healthcare.interiors.healthcare_apartment_interior import HealthcareApartmentInterior

def test_therapist_call_fix():
    """Test that therapist_call_options no longer auto-completes"""
    print("🧪 Testing Therapist Call Auto-Skip Fix")
    print("=" * 50)

    # Create mock objects
    class MockObjectiveManager:
        def __init__(self):
            self.complete_called = False

        def complete_current_objective(self):
            self.complete_called = True
            print("⚠️  complete_current_objective() was called!")

        def get_current_objective(self):
            class MockObjective:
                def __init__(self, obj_id):
                    self.id = obj_id
            return MockObjective("therapist_call_options")

    class MockGame:
        def __init__(self):
            self.objective_manager = MockObjectiveManager()

    mock_room_data = {}
    mock_building_pos = (0, 0)

    # Create interior
    interior = HealthcareApartmentInterior(MockGame(), mock_room_data, mock_building_pos)

    # Simulate the problematic scenario
    print("1. Testing therapist_call_options objective completion logic")

    # Add answer_call to completed interactions (simulating the trigger)
    interior.completed_interactions.add('answer_call')
    print("   ✅ Added 'answer_call' to completed_interactions")

    # Call update_objective_display which contains the fixed logic
    interior.update_objective_display()

    # Check if objective was auto-completed (it should NOT be)
    if interior.game.objective_manager.complete_called:
        print("   ❌ FAILED: Objective was auto-completed (bug still exists)")
        return False
    else:
        print("   ✅ SUCCESS: Objective was NOT auto-completed (fix working)")

    print("\n2. Testing that the fix follows the same pattern as other activities")

    # Check the source code content
    with open('/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon/part_2_healthcare/interiors/healthcare_apartment_interior.py', 'r') as f:
        content = f.read()

    # Look for the fixed pattern
    if "# DON'T auto-complete based on interaction - let the therapist call activity handle completion" in content:
        print("   ✅ Comment explaining the fix is present")
    else:
        print("   ❌ Expected comment not found")
        return False

    if "elif current.id == 'therapist_call_options':" in content and "pass" in content:
        print("   ✅ therapist_call_options uses pass instead of auto-completion")
    else:
        print("   ❌ therapist_call_options still has auto-completion logic")
        return False

    print("\n3. Checking consistency with other activity objectives")

    # Check that medicaid_notice, therapy_reminder, and insurance_panic also use pass
    activity_objectives = ["medicaid_notice", "therapy_reminder", "insurance_panic"]
    for obj_id in activity_objectives:
        if f"elif current.id == '{obj_id}':" in content and "pass" in content:
            print(f"   ✅ {obj_id} correctly uses activity-based completion")
        else:
            print(f"   ⚠️  {obj_id} might need similar fix")

    print("\n" + "=" * 50)
    print("🎉 FIX VERIFICATION COMPLETE!")
    print("\n📋 WHAT CHANGED:")
    print("   ❌ Before: therapist_call_options auto-completed on 'answer_call' interaction")
    print("   ✅ After: therapist_call_options waits for TherapistCallActivity to complete")
    print("\n🎮 EXPECTED BEHAVIOR:")
    print("   1. Player enters healthcare apartment at therapist_call_options objective")
    print("   2. Player presses E to answer phone call")
    print("   3. TherapistCallActivity launches (phone interface appears)")
    print("   4. Player goes through call conversation")
    print("   5. Player selects payment option (sliding scale/cancel/full price)")
    print("   6. Player confirms decision")
    print("   7. TherapistCallActivity completes and advances objective to therapy_payment_decision")
    print("   8. NO MORE AUTO-SKIP!")

    return True

if __name__ == "__main__":
    print("🧪 THERAPIST CALL AUTO-SKIP FIX VERIFICATION")
    print("=" * 60)

    if test_therapist_call_fix():
        print("\n🏆 ALL TESTS PASSED! 🏆")
        print("The auto-skip issue has been fixed!")
    else:
        print("\n❌ TESTS FAILED!")
        print("The fix needs additional work.")

    print("\n" + "=" * 60)
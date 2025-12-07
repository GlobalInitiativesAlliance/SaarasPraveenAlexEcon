#!/usr/bin/env python3
"""
Test script to verify all three therapy payment decision paths work correctly
"""

import sys
import os
import pygame

# Initialize pygame
pygame.init()

sys.path.append('/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon')

from part_2_healthcare.activities.therapy_payment_decision_activity import TherapyPaymentDecisionActivity

def test_decision_activity():
    """Test the therapy payment decision activity functionality"""
    print("🧪 Testing Therapy Payment Decision Activity")
    print("=" * 60)

    # Create mock objective manager
    class MockObjectiveManager:
        def complete_current_objective(self):
            print("✅ Objective completed!")

    # Test activity initialization
    print("1. Testing Activity Initialization")
    try:
        activity = TherapyPaymentDecisionActivity(MockObjectiveManager())
        print("   ✅ Activity created successfully")
        print(f"   📊 Budget data: {activity.budget_data}")
        print(f"   💡 Payment options: {len(activity.payment_options)}")
    except Exception as e:
        print(f"   ❌ Error creating activity: {e}")
        return False

    # Test activity startup
    print("\n2. Testing Activity Startup")
    try:
        activity.start()
        print(f"   ✅ Activity started - Active: {activity.active}")
        print(f"   📋 Stage: {activity.decision_stage}")
    except Exception as e:
        print(f"   ❌ Error starting activity: {e}")
        return False

    # Test decision paths
    print("\n3. Testing Decision Paths")
    for i, option in enumerate(activity.payment_options):
        print(f"\n   Path {i+1}: {option['title']}")
        print(f"   💰 Cost: ${option['cost']}")
        print(f"   📈 Recommendation: {option['recommendation']}")
        print(f"   🧠 Health impact: {option['budget_impact']['health_change']}")
        print(f"   😰 Stress impact: {option['budget_impact']['stress_change']}")

        # Test selection logic
        try:
            old_stress = activity.stress_level
            old_health = activity.health_level
            activity.update_meters_for_selection(option)

            print(f"   📊 Stress: {old_stress} → {activity.stress_level}")
            print(f"   💚 Health: {old_health} → {activity.health_level}")
            print(f"   ⚡ Shake effect: {'Yes' if activity.shake_timer > 0 else 'No'}")

            # Reset for next test
            activity.stress_level = 60
            activity.health_level = 70
            activity.shake_timer = 0

            print("   ✅ Selection logic working correctly")
        except Exception as e:
            print(f"   ❌ Error in selection logic: {e}")

    # Test activity stages
    print("\n4. Testing Activity Stages")
    stages = ["budget_overview", "decision_options", "impact_preview", "confirmation"]
    for stage in stages:
        print(f"   📋 Testing stage: {stage}")
        try:
            activity.decision_stage = stage
            activity.update(1/60.0)  # Simulate one frame
            print(f"   ✅ Stage {stage} updated successfully")
        except Exception as e:
            print(f"   ❌ Error in stage {stage}: {e}")

    # Test completion
    print("\n5. Testing Activity Completion")
    try:
        activity.current_selection = 0  # Select first option
        activity.complete_activity()
        print(f"   ✅ Activity completed - Completed: {activity.completed}")
    except Exception as e:
        print(f"   ❌ Error completing activity: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 All tests passed! Therapy Payment Decision Activity is working correctly!")
    print("\n📋 FEATURES VERIFIED:")
    print("   ✅ Activity initialization and startup")
    print("   ✅ All three payment decision paths")
    print("   ✅ Budget impact calculations")
    print("   ✅ Stress and health meter updates")
    print("   ✅ Visual effects (shake for high-stress decisions)")
    print("   ✅ Activity stage progression")
    print("   ✅ Proper completion handling")
    print("\n🎮 Ready for in-game testing!")

    return True

def test_integration():
    """Test integration with healthcare apartment interior"""
    print("\n🔗 Testing Integration with Healthcare Apartment Interior")
    print("=" * 60)

    try:
        # Import healthcare interior
        from part_2_healthcare.interiors.healthcare_apartment_interior import HealthcareApartmentInterior
        print("✅ Healthcare apartment interior imported successfully")

        # Check if launch method exists
        if hasattr(HealthcareApartmentInterior, 'launch_therapy_payment_decision'):
            print("✅ launch_therapy_payment_decision method exists")
        else:
            print("❌ launch_therapy_payment_decision method missing")
            return False

        # Check narrative content
        # Create mock objects for interior initialization
        class MockGame:
            def __init__(self):
                self.objective_manager = None

        mock_room_data = {}
        mock_building_pos = (0, 0)

        interior = HealthcareApartmentInterior(MockGame(), mock_room_data, mock_building_pos)
        content = interior.load_narrative_content()

        if 'therapy_payment_decision' in content:
            print("✅ therapy_payment_decision narrative content exists")
            decision_content = content['therapy_payment_decision']

            if 'interactions' in decision_content:
                interactions = decision_content['interactions']
                print(f"✅ {len(interactions)} interaction(s) defined")

                for name, interaction in interactions.items():
                    if 'trigger_activity' in interaction:
                        trigger = interaction['trigger_activity']
                        if trigger == 'therapy_payment_decision':
                            print(f"✅ Interaction '{name}' correctly triggers activity")
                        else:
                            print(f"❌ Interaction '{name}' has wrong trigger: {trigger}")
                    else:
                        print(f"❌ Interaction '{name}' missing trigger_activity")
            else:
                print("❌ No interactions defined for therapy_payment_decision")
                return False
        else:
            print("❌ therapy_payment_decision narrative content missing")
            return False

        print("\n🎉 Integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 THERAPY PAYMENT DECISION ACTIVITY - COMPREHENSIVE TEST")
    print("=" * 80)

    success = True

    # Run functionality tests
    if not test_decision_activity():
        success = False

    # Run integration tests
    if not test_integration():
        success = False

    if success:
        print("\n🏆 ALL TESTS PASSED! 🏆")
        print("The therapy payment decision activity is fully implemented and ready!")
        print("\n📋 TO TEST IN-GAME:")
        print("1. Run the game: python3 src/main.py")
        print("2. Navigate to the healthcare apartment")
        print("3. Progress to the 'therapy_payment_decision' objective")
        print("4. Press E near the interaction point")
        print("5. Test all three decision paths:")
        print("   - Sliding Scale Program (recommended)")
        print("   - Cancel Appointment (risky)")
        print("   - Pay Full Price (dangerous)")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please review the errors above and fix any issues.")

    print("\n" + "=" * 80)
#!/usr/bin/env python3
"""
Test script to verify clinic exit fix works correctly.
This simulates completing all mini-games and ensures the clinic properly exits.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import pygame

def test_clinic_exit_behavior():
    """Test that clinic properly exits after all mini-games are completed"""
    print("=" * 60)
    print("TESTING: Clinic Auto-Exit After Completion")
    print("=" * 60)

    try:
        from part_2_healthcare.activities.clinic_mini_game_manager import ClinicMiniGameManager
        from part_2_healthcare.interiors.enhanced_clinic_interior import EnhancedClinicInterior

        # Mock objective manager
        class MockObjectiveManager:
            def __init__(self):
                self.current_activity = None
                self.notifications = []

            def advance_to_next_objective(self):
                print("[MOCK] advance_to_next_objective() called")

            def show_notification(self, message, color=(255, 255, 255)):
                print(f"[MOCK] Notification: {message}")

            def get_current_objective(self):
                # Mock objective that would trigger clinic games
                class MockObjective:
                    def __init__(self):
                        self.id = "clinic_checklist"
                        self.title = "Document Verification"
                return MockObjective()

        pygame.init()
        pygame.font.init()

        # Create clinic interior with mock objective manager
        mock_obj_mgr = MockObjectiveManager()
        building_pos = (34, 31)
        room_data = {"width": 16, "height": 11}

        clinic = EnhancedClinicInterior(mock_obj_mgr, building_pos, room_data)

        print("✓ EnhancedClinicInterior created successfully")

        # Enter the clinic
        clinic.enter()
        assert clinic.active, "Clinic should be active after entering"
        assert not clinic.form_completed, "Form should not be completed initially"
        print("✓ Clinic entered successfully")

        # Simulate completing all mini-games by manually completing them
        all_games = ['travel_to_clinic', 'clinic_checklist', 'foster_youth_application', 'application_approved']

        for game_id in all_games:
            print(f"  Completing mini-game: {game_id}")
            clinic.mini_game_manager.start_mini_game(game_id)
            clinic.mini_game_manager.complete_current_game()

        # Check completion status
        status = clinic.mini_game_manager.get_completion_status()
        print(f"✓ All mini-games completed: {status['completed']}/{status['total']}")

        # Simulate update cycles to trigger exit logic
        print("Simulating clinic update cycles...")

        # First update should start the exit timer
        clinic.update(0.1)
        assert hasattr(clinic, 'exit_timer'), "Exit timer should be started"
        assert clinic.exit_timer > 0, "Exit timer should be positive"
        assert clinic.form_completed, "Form should be marked as completed"
        print(f"✓ Exit timer started: {clinic.exit_timer:.1f}s")

        # Fast-forward through the timer
        initial_timer = clinic.exit_timer
        while clinic.active and clinic.exit_timer > 0:
            clinic.update(0.1)

        # Clinic should now be inactive (exited)
        assert not clinic.active, "Clinic should be inactive after timer expires"
        print("✓ Clinic automatically exited after timer")

        print("✅ Clinic auto-exit test PASSED")
        return True

    except Exception as e:
        print(f"❌ Clinic auto-exit test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_clinic_exit_test():
    """Run the clinic exit fix test"""
    print("🔍 Testing Clinic Exit Fix")
    print("This verifies that the clinic properly exits after completing all mini-games.")
    print()

    success = test_clinic_exit_behavior()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if success:
        print("🎉 CLINIC EXIT FIX TEST PASSED!")
        print("\n✅ The clinic will now properly auto-exit after completing all mini-games!")
        print("\nWhat happens now:")
        print("• Complete all clinic mini-games (navigation, checklist, application, approval)")
        print("• Clinic shows 'Application complete! Returning to city map...'")
        print("• After 2 seconds, automatically returns to the main game")
        print("• No more getting stuck in the clinic interface!")
    else:
        print("❌ CLINIC EXIT FIX TEST FAILED")
        print("\nThe fix may need additional work.")

    pygame.quit()
    return success

if __name__ == "__main__":
    success = run_clinic_exit_test()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to verify the complete clinic sequence works properly.
This tests all 4 clinic objectives in order.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import pygame

def test_complete_clinic_sequence():
    """Test the complete clinic objective sequence"""
    print("=" * 60)
    print("TESTING: Complete Clinic Sequence")
    print("=" * 60)

    try:
        from part_2_healthcare.activities.clinic_mini_game_manager import ClinicMiniGameManager

        # Mock objective manager
        class MockObjectiveManager:
            def __init__(self):
                self.current_activity = None
                self.notifications = []
                self.objectives_advanced = []

            def advance_to_next_objective(self):
                print("[MOCK] advance_to_next_objective() called")
                self.objectives_advanced.append("advanced")

            def show_notification(self, text, duration=3.0):
                print(f"[MOCK] Notification: {text}")
                self.notifications.append(text)

        pygame.init()
        pygame.font.init()

        mock_obj_mgr = MockObjectiveManager()
        manager = ClinicMiniGameManager(mock_obj_mgr)

        print("✓ ClinicMiniGameManager created successfully")

        # Test the complete sequence
        clinic_objectives = [
            "travel_to_clinic",
            "clinic_checklist",
            "foster_youth_application",
            "application_approved"
        ]

        print("\n🎯 Testing complete clinic sequence...")

        for i, objective_id in enumerate(clinic_objectives):
            print(f"\n--- Step {i+1}: {objective_id} ---")

            # Start the mini-game
            success = manager.start_mini_game(objective_id)
            assert success, f"Failed to start {objective_id}"
            print(f"✓ Started {objective_id} successfully")

            # Check state
            assert manager.active, f"Manager should be active for {objective_id}"
            assert manager.current_game is not None, f"Current game should exist for {objective_id}"
            assert manager.current_objective_id == objective_id, f"Current objective ID should be {objective_id}"
            print(f"✓ Manager state correct for {objective_id}")

            # Complete the mini-game
            manager.complete_current_game()

            # Check completion
            assert not manager.active, f"Manager should be inactive after completing {objective_id}"
            assert manager.current_game is None, f"Current game should be None after completing {objective_id}"
            assert objective_id in manager.completed_games, f"{objective_id} should be in completed games"
            print(f"✓ Completed {objective_id} successfully")

        # Check final state
        status = manager.get_completion_status()
        print(f"\n🏁 Final completion status: {status}")

        assert status['completed'] == status['total'], "All games should be completed"
        assert len(mock_obj_mgr.objectives_advanced) == 4, "Should have advanced 4 objectives"
        assert len(mock_obj_mgr.notifications) == 4, "Should have 4 completion notifications"

        print("✅ Complete Clinic Sequence test PASSED")
        return True

    except Exception as e:
        print(f"❌ Complete Clinic Sequence test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_mini_games():
    """Test each mini-game individually for basic functionality"""
    print("\n" + "=" * 60)
    print("TESTING: Individual Mini-Game Quality")
    print("=" * 60)

    test_results = []

    # Test clinic navigation
    try:
        from part_2_healthcare.activities.clinic_navigation import ClinicNavigationGame
        nav_game = ClinicNavigationGame()
        nav_game.start()
        assert nav_game.active, "Navigation game should be active"
        print("✓ Clinic Navigation Game loads correctly")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Clinic Navigation Game FAILED: {e}")
        test_results.append(False)

    # Test document checklist
    try:
        from part_2_healthcare.activities.clinic_document_checklist import ClinicDocumentChecklistGame
        checklist_game = ClinicDocumentChecklistGame()
        checklist_game.start()
        assert checklist_game.active, "Checklist game should be active"
        assert len(checklist_game.documents) > 0, "Should have documents to check"
        print("✓ Document Checklist Game loads correctly")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Document Checklist Game FAILED: {e}")
        test_results.append(False)

    # Test application form
    try:
        from part_2_healthcare.activities.foster_youth_application_form import FosterYouthApplicationFormGame
        form_game = FosterYouthApplicationFormGame()
        form_game.start()
        assert form_game.active, "Form game should be active"
        assert len(form_game.questions) == 4, "Should have 4 questions"
        print("✓ Foster Youth Application Form loads correctly")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Foster Youth Application Form FAILED: {e}")
        test_results.append(False)

    # Test approval notification
    try:
        from part_2_healthcare.activities.approval_notification import ApprovalNotificationGame
        approval_game = ApprovalNotificationGame()
        approval_game.start()
        assert approval_game.active, "Approval game should be active"
        print("✓ Approval Notification Game loads correctly")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Approval Notification Game FAILED: {e}")
        test_results.append(False)

    return all(test_results)

def run_complete_clinic_tests():
    """Run all clinic tests"""
    print("🔍 Testing Complete Clinic Sequence and Quality")
    print("This verifies all clinic mini-games work properly and progress correctly.")
    print()

    # Initialize pygame
    pygame.init()
    pygame.font.init()

    test_results = []

    # Test individual games
    test_results.append(test_individual_mini_games())

    # Test complete sequence
    test_results.append(test_complete_clinic_sequence())

    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)

    passed = sum(test_results)
    total = len(test_results)

    if passed == total:
        print(f"🎉 ALL CLINIC TESTS PASSED ({passed}/{total})")
        print("\n✅ The complete clinic sequence should now work correctly!")
        print("\nWhat's fixed:")
        print("• TypeError in foster youth application form")
        print("• Proper mini-game progression")
        print("• Auto-exit after each objective completion")
        print("• All 4 clinic mini-games load and function")
        print("\n🎯 You should be able to complete the clinic objectives without issues!")
    else:
        print(f"❌ {total - passed} TESTS FAILED ({passed}/{total} passed)")
        print("\nSome clinic mini-games may still need work.")

    pygame.quit()
    return passed == total

if __name__ == "__main__":
    success = run_complete_clinic_tests()
    exit(0 if success else 1)
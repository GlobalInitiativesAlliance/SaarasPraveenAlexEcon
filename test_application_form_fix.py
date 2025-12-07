#!/usr/bin/env python3
"""
Test script to verify the foster youth application form works correctly.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import pygame

def test_application_form():
    """Test the foster youth application form for proper completion"""
    print("=" * 60)
    print("TESTING: Foster Youth Application Form")
    print("=" * 60)

    try:
        from part_2_healthcare.activities.foster_youth_application_form import FosterYouthApplicationFormGame

        # Mock objective manager
        class MockObjectiveManager:
            def show_notification(self, text, duration=3.0):
                print(f"[MOCK NOTIFICATION] {text}")

        pygame.init()
        pygame.font.init()

        mock_obj_mgr = MockObjectiveManager()
        form_game = FosterYouthApplicationFormGame(mock_obj_mgr)

        print("✓ FosterYouthApplicationFormGame created successfully")

        # Start the form
        form_game.start()
        assert form_game.active, "Form should be active after starting"
        print("✓ Form started successfully")

        # Simulate answering all questions correctly
        for i, question in enumerate(form_game.questions):
            print(f"  Answering question {i+1}: {question['question']}")
            # Select first correct answer
            correct_answer = question['correct'][0]
            question['selected'] = correct_answer
            form_game.current_question = i

        # Complete the form
        form_game.current_question = len(form_game.questions) - 1  # Last question
        form_game.complete_form()

        # Check completion
        assert form_game.completed, "Form should be completed"
        assert not form_game.active, "Form should be inactive after completion"
        print("✓ Form completed successfully")

        # Check results
        results = form_game.get_results()
        assert results['completed'], "Results should show completion"
        assert results['eligible'], "Results should show eligibility"
        print(f"✓ Form results correct: {results}")

        print("✅ Foster Youth Application Form test PASSED")
        return True

    except Exception as e:
        print(f"❌ Foster Youth Application Form test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_application_test():
    """Run the application form test"""
    print("🔍 Testing Foster Youth Application Form Fix")
    print("This verifies the form properly completes without errors.")
    print()

    success = test_application_form()

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if success:
        print("🎉 APPLICATION FORM FIX TEST PASSED!")
        print("\n✅ The foster youth application form should now work correctly!")
        print("\nFixed issues:")
        print("• show_notification() method call fixed")
        print("• Form completion properly handled")
        print("• Results properly returned")
        print("• No more TypeError crashes")
    else:
        print("❌ APPLICATION FORM FIX TEST FAILED")
        print("\nThe fix may need additional work.")

    pygame.quit()
    return success

if __name__ == "__main__":
    success = run_application_test()
    exit(0 if success else 1)
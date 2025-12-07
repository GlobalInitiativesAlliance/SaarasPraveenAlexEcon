#!/usr/bin/env python3
"""
Test script to verify the foster youth application form visual quality improvements.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import pygame

def test_form_visual_rendering():
    """Test that the form renders properly with all visual improvements"""
    print("=" * 60)
    print("TESTING: Form Visual Quality and Rendering")
    print("=" * 60)

    try:
        from part_2_healthcare.activities.foster_youth_application_form import FosterYouthApplicationFormGame

        pygame.init()
        pygame.display.set_mode((1280, 720))  # Set a display mode for testing
        pygame.font.init()

        form_game = FosterYouthApplicationFormGame()
        print("✓ FosterYouthApplicationFormGame created successfully")

        # Test screen size adaptation
        assert hasattr(form_game, 'SCREEN_WIDTH'), "Should have SCREEN_WIDTH attribute"
        assert hasattr(form_game, 'SCREEN_HEIGHT'), "Should have SCREEN_HEIGHT attribute"
        assert form_game.SCREEN_WIDTH > 0, "Screen width should be positive"
        assert form_game.SCREEN_HEIGHT > 0, "Screen height should be positive"
        print(f"✓ Screen dimensions: {form_game.SCREEN_WIDTH}x{form_game.SCREEN_HEIGHT}")

        # Start the form to test initialization
        form_game.start()
        assert form_game.active, "Form should be active after starting"
        assert form_game.current_question == 0, "Should start at question 0"
        print("✓ Form initialization works correctly")

        # Test layout calculations
        option_rects = form_game.get_option_rects()
        current_question = form_game.questions[form_game.current_question]
        expected_options = len(current_question['options'])
        assert len(option_rects) == expected_options, f"Should have {expected_options} option rectangles for current question"

        # Check that options are properly positioned
        for i, rect in enumerate(option_rects):
            assert rect.width > 0, f"Option {i} should have positive width"
            assert rect.height > 0, f"Option {i} should have positive height"
            assert rect.x >= 0, f"Option {i} should be positioned within screen bounds"
            assert rect.y >= 0, f"Option {i} should be positioned within screen bounds"
            assert rect.right <= form_game.SCREEN_WIDTH, f"Option {i} should fit within screen width"
            assert rect.bottom <= form_game.SCREEN_HEIGHT, f"Option {i} should fit within screen height"

        print("✓ Option layout calculations are correct")

        # Test navigation button positioning
        nav_rects = form_game.get_navigation_rects()
        assert 'prev' in nav_rects, "Should have previous button"
        assert 'next' in nav_rects, "Should have next button"

        prev_rect = nav_rects['prev']
        next_rect = nav_rects['next']

        assert prev_rect.x >= 0, "Previous button should be within screen bounds"
        assert next_rect.right <= form_game.SCREEN_WIDTH, "Next button should be within screen bounds"
        assert prev_rect.right < next_rect.left, "Buttons should not overlap"

        print("✓ Navigation button positioning is correct")

        # Test visual rendering (create a test surface)
        test_surface = pygame.Surface((form_game.SCREEN_WIDTH, form_game.SCREEN_HEIGHT))

        try:
            form_game.draw(test_surface)
            print("✓ Form draws without errors")
        except Exception as e:
            print(f"❌ Form drawing failed: {e}")
            return False

        # Test question progression
        for question_num in range(form_game.total_questions):
            form_game.current_question = question_num

            # Test that each question has proper layout
            option_rects = form_game.get_option_rects()
            current_q = form_game.questions[question_num]

            assert len(option_rects) == len(current_q['options']), f"Question {question_num} should have correct number of option rectangles"

            # Test rendering each question
            try:
                form_game.draw(test_surface)
            except Exception as e:
                print(f"❌ Question {question_num} drawing failed: {e}")
                return False

        print("✓ All questions render correctly")

        print("✅ Form Visual Quality test PASSED")
        return True

    except Exception as e:
        print(f"❌ Form Visual Quality test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_responsive_design():
    """Test that the form adapts to different screen sizes"""
    print("\n" + "=" * 60)
    print("TESTING: Responsive Design")
    print("=" * 60)

    try:
        from part_2_healthcare.activities.foster_youth_application_form import FosterYouthApplicationFormGame

        # Test different screen sizes
        test_sizes = [
            (1280, 720),  # Standard HD
            (1920, 1080), # Full HD
            (1024, 768),  # Older standard
            (1366, 768),  # Common laptop size
        ]

        for width, height in test_sizes:
            print(f"\n  Testing screen size: {width}x{height}")

            # Set up pygame with this screen size
            pygame.display.set_mode((width, height))

            form_game = FosterYouthApplicationFormGame()
            form_game.start()

            # Check that elements adapt to screen size
            assert form_game.SCREEN_WIDTH == width, f"Width should adapt to {width}"
            assert form_game.SCREEN_HEIGHT == height, f"Height should adapt to {height}"

            # Check layout calculations
            option_rects = form_game.get_option_rects()
            nav_rects = form_game.get_navigation_rects()

            # Verify all elements fit within screen bounds
            for i, rect in enumerate(option_rects):
                assert rect.right <= width, f"Option {i} should fit in width {width}"
                assert rect.bottom <= height, f"Option {i} should fit in height {height}"

            assert nav_rects['prev'].right <= width, "Previous button should fit in width"
            assert nav_rects['next'].right <= width, "Next button should fit in width"

            print(f"    ✓ Layout adapts correctly to {width}x{height}")

        print("✅ Responsive Design test PASSED")
        return True

    except Exception as e:
        print(f"❌ Responsive Design test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_form_visual_tests():
    """Run all form visual quality tests"""
    print("🎨 Testing Foster Youth Application Form Visual Quality")
    print("This verifies the form looks professional and adapts to different screen sizes.")
    print()

    # Initialize pygame
    pygame.init()
    pygame.font.init()

    test_results = []

    # Run tests
    test_results.append(test_form_visual_rendering())
    test_results.append(test_responsive_design())

    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)

    passed = sum(test_results)
    total = len(test_results)

    if passed == total:
        print(f"🎉 ALL FORM VISUAL TESTS PASSED ({passed}/{total})")
        print("\n✅ The foster youth application form is now high-quality and visually consistent!")
        print("\nVisual improvements made:")
        print("• Responsive layout that adapts to screen size")
        print("• Proper text truncation for long option text")
        print("• Enhanced gradient background with texture")
        print("• Text shadows for better readability")
        print("• Option letters (A, B, C, D) for clarity")
        print("• Consistent spacing and margins")
        print("• Professional color scheme")
        print("\n🎯 The form should now look polished and work on different screen sizes!")
    else:
        print(f"❌ {total - passed} TESTS FAILED ({passed}/{total} passed)")
        print("\nSome visual issues may still need work.")

    pygame.quit()
    return passed == total

if __name__ == "__main__":
    success = run_form_visual_tests()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Simple test script to trigger part1_complete and see where the transition fails
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock pygame to avoid display requirements
class MockPygame:
    class font:
        @staticmethod
        def Font(name, size):
            return None

    @staticmethod
    def init():
        pass

sys.modules['pygame'] = MockPygame()

def test_transition_trigger():
    """Test triggering the transition manually"""
    print("🧪 Testing transition trigger...")

    try:
        # Import required modules
        from src.core.game_world import ObjectiveManager
        from src.activities.activities import TransitionScene

        # Mock game object
        class MockGame:
            def __init__(self):
                self.use_modern_ui = False
                self.ui_manager = None

        # Create mock game and objective manager
        game = MockGame()
        obj_mgr = ObjectiveManager(game)
        game.objective_manager = obj_mgr

        print(f"✅ ObjectiveManager created")
        print(f"   Game part: {obj_mgr.game_part}")
        print(f"   Transition scene object: {obj_mgr.transition_scene}")
        print(f"   Transition scene type: {type(obj_mgr.transition_scene)}")

        # Load Part 1 objectives
        obj_mgr.setup_objectives()
        print(f"✅ Objectives loaded: {len(obj_mgr.objectives)} objectives")

        # Find part1_complete objective
        part1_complete_index = None
        for i, obj in enumerate(obj_mgr.objectives):
            if obj.id == 'part1_complete':
                part1_complete_index = i
                break

        if part1_complete_index is None:
            print("❌ part1_complete objective not found!")
            return False

        print(f"✅ Found part1_complete at index {part1_complete_index}")

        # Jump to part1_complete objective
        obj_mgr.current_objective_index = part1_complete_index
        current = obj_mgr.get_current_objective()
        print(f"✅ Current objective: {current.id} - {current.title}")

        # Manually trigger complete_current_objective
        print("\n🎬 TRIGGERING part1_complete...")
        obj_mgr.complete_current_objective()

        # Check if transition scene was started
        print(f"\n🔍 Post-trigger state:")
        print(f"   Current activity: {obj_mgr.current_activity}")
        print(f"   Activity type: {type(obj_mgr.current_activity) if obj_mgr.current_activity else None}")
        print(f"   Activity active: {obj_mgr.current_activity.active if obj_mgr.current_activity else None}")
        print(f"   Activity completed: {obj_mgr.current_activity.completed if obj_mgr.current_activity else None}")

        if obj_mgr.current_activity and isinstance(obj_mgr.current_activity, TransitionScene):
            print("✅ TransitionScene was started correctly!")

            # Test the transition scene manually
            print("\n🎬 TESTING TransitionScene progression...")
            transition = obj_mgr.current_activity

            # Simulate time progression to complete all stages
            for stage in range(5):
                print(f"   Stage {transition.stage}: timer={transition.timer:.2f}")
                transition.update(0.5)  # Update with 0.5 second steps

                # Force progression through stages
                if stage == 0 and transition.stage == 0:
                    transition.timer = 5  # Force fade in complete
                elif stage == 1 and transition.stage == 1:
                    transition.timer = 5  # Force text complete
                elif stage == 2 and transition.stage == 2:
                    transition.timer = 2  # Force pause complete
                elif stage == 3 and transition.stage == 3:
                    transition.timer = 5  # Force Part 2 text complete

                transition.update(0.1)  # Small update to trigger stage change

                if transition.completed:
                    print("✅ TransitionScene completed!")
                    break

            print(f"\n🔍 Final transition state:")
            print(f"   Stage: {transition.stage}")
            print(f"   Active: {transition.active}")
            print(f"   Completed: {transition.completed}")

            if transition.completed:
                # Now test the game_world update logic
                print("\n🎬 TESTING game_world transition detection...")
                obj_mgr.update(0.1)  # This should detect the completed transition scene

                print(f"🔍 Post-update state:")
                print(f"   Current activity: {obj_mgr.current_activity}")
                print(f"   Game part: {obj_mgr.game_part}")

                return True
            else:
                print("❌ TransitionScene did not complete")
                return False
        else:
            print("❌ TransitionScene was not started correctly!")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("🧪 Testing Part 1 Complete Transition Trigger...")
    print("=" * 60)

    success = test_transition_trigger()

    print("\n" + "=" * 60)
    if success:
        print("✅ Transition trigger test successful!")
        print("💡 The transition logic is working correctly")
    else:
        print("❌ Transition trigger test failed!")
        print("💡 Check the debug output for clues")

if __name__ == "__main__":
    main()
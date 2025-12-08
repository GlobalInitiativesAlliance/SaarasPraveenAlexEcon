#!/usr/bin/env python3
"""
Debug script to analyze the Part 1 to Part 2 transition issue
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required classes can be imported"""
    print("🔍 Testing imports...")

    try:
        from src.activities.activities import TransitionScene
        print("✅ TransitionScene imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import TransitionScene: {e}")
        return False

    try:
        from src.activities import TransitionScene
        print("✅ TransitionScene imports via activities module")
    except ImportError as e:
        print(f"❌ Failed to import TransitionScene via activities module: {e}")
        return False

    try:
        from src.core.part_transition_manager import PartTransitionManager
        print("✅ PartTransitionManager imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import PartTransitionManager: {e}")
        return False

    return True

def test_transition_scene_behavior():
    """Test TransitionScene behavior"""
    print("\n🎬 Testing TransitionScene behavior...")

    try:
        from src.activities.activities import TransitionScene

        # Mock objective manager
        class MockObjectiveManager:
            def __init__(self):
                pass

        # Create transition scene
        obj_mgr = MockObjectiveManager()
        transition = TransitionScene(obj_mgr)

        print(f"✅ TransitionScene created successfully")
        print(f"   Active: {transition.active}")
        print(f"   Completed: {transition.completed}")
        print(f"   Stage: {transition.stage}")

        # Test start
        transition.start()
        print(f"✅ TransitionScene started")
        print(f"   Active: {transition.active}")
        print(f"   Completed: {transition.completed}")

        # Test completion
        transition.complete()
        print(f"✅ TransitionScene completed")
        print(f"   Active: {transition.active}")
        print(f"   Completed: {transition.completed}")

        return True

    except Exception as e:
        print(f"❌ TransitionScene test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_part1_complete_logic():
    """Test the part1_complete objective logic"""
    print("\n🎯 Testing part1_complete objective logic...")

    try:
        # Test that part1_complete is handled correctly
        from part_1_housing_stability.objectives_narrative import get_part1_narrative_objectives

        objectives = get_part1_narrative_objectives()
        part1_complete_obj = None

        for obj in objectives:
            if obj.id == 'part1_complete':
                part1_complete_obj = obj
                break

        if not part1_complete_obj:
            print("❌ part1_complete objective not found")
            return False

        print(f"✅ part1_complete objective found:")
        print(f"   ID: {part1_complete_obj.id}")
        print(f"   Title: {part1_complete_obj.title}")
        print(f"   Description: {part1_complete_obj.description}")
        print(f"   Position: {part1_complete_obj.target_position}")
        print(f"   Progress text: {part1_complete_obj.progress_text}")

        return True

    except Exception as e:
        print(f"❌ part1_complete test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_transition_issue():
    """Analyze what might be going wrong with the transition"""
    print("\n🔍 ANALYZING TRANSITION ISSUE...")

    print("\n1. The flow should be:")
    print("   • part1_complete objective triggers")
    print("   • game_world.py complete_current_objective() is called")
    print("   • Handler for part1_complete starts TransitionScene")
    print("   • TransitionScene runs through stages 0-4")
    print("   • TransitionScene.complete() is called")
    print("   • game_world.py detects completed TransitionScene")
    print("   • part_transition_manager.transition_to_part2() is called")
    print("   • Part 2 objectives are loaded")

    print("\n2. Possible failure points:")
    print("   ❓ part1_complete objective never gets triggered")
    print("   ❓ TransitionScene never starts")
    print("   ❓ TransitionScene starts but never completes")
    print("   ❓ TransitionScene completes but isinstance check fails")
    print("   ❓ part_transition_manager.transition_to_part2() fails")
    print("   ❓ Part 2 objectives fail to load")

    print("\n3. Debug recommendations:")
    print("   • Add debug prints to part1_complete handler")
    print("   • Add debug prints to TransitionScene.complete()")
    print("   • Add debug prints to isinstance check")
    print("   • Add debug prints to transition_to_part2()")
    print("   • Check if TransitionScene.update() is being called")

def main():
    """Run all tests and analysis"""
    print("🧪 Debugging Part 1 to Part 2 Transition Issue...")
    print("=" * 60)

    success = True

    if not test_imports():
        success = False

    if not test_transition_scene_behavior():
        success = False

    if not test_part1_complete_logic():
        success = False

    analyze_transition_issue()

    print("\n" + "=" * 60)
    if success:
        print("✅ All basic tests passed - the issue is likely in runtime logic")
        print("💡 Recommendation: Add debug prints to the actual transition flow")
    else:
        print("❌ Basic tests failed - fix import/setup issues first")

if __name__ == "__main__":
    main()
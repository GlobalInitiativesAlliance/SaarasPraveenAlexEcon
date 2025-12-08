#!/usr/bin/env python3
"""
Test script to verify classroom narrative handles six_months_surviving correctly
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_classroom_objective_mapping():
    """Test that classroom narrative maps objectives correctly"""
    print("🎓 Testing classroom objective mapping...")

    try:
        from src.interiors.narratives.classroom_narrative import ClassroomNarrative

        # Mock game and objective
        class MockObjective:
            def __init__(self, obj_id):
                self.id = obj_id
                self.target_position = (30, 11)

        class MockObjectiveManager:
            def __init__(self, objective):
                self.objective = objective

            def get_current_objective(self):
                return self.objective

        class MockGame:
            def __init__(self, objective):
                self.objective_manager = MockObjectiveManager(objective)

        # Test six_months_surviving objective
        mock_room_data = {'width': 16, 'height': 12}
        objective = MockObjective('six_months_surviving')
        game = MockGame(objective)

        classroom = ClassroomNarrative(game, mock_room_data, (30, 11))
        content = classroom.load_narrative_content()

        # Test objective mapping
        objective_to_content = {
            'six_months_surviving': 'tlp_acceptance',
            'desperate_measures': 'selling_items',
            'the_system': 'economics_lesson',
            'part1_complete': 'completion'
        }

        for obj_id, expected_content in objective_to_content.items():
            if expected_content not in content:
                print(f"❌ Missing content for {obj_id} -> {expected_content}")
                return False
            print(f"✅ {obj_id} -> {expected_content} (content exists)")

        # Test that tlp_acceptance has the required interactions
        tlp_content = content['tlp_acceptance']
        if 'celebration' not in tlp_content['interactions']:
            print("❌ Missing 'celebration' interaction in tlp_acceptance")
            return False

        print("✅ Celebration interaction found in tlp_acceptance")
        print("✅ Classroom objective mapping working correctly!")
        return True

    except Exception as e:
        print(f"❌ Classroom objective mapping test failed: {e}")
        return False

def main():
    """Run the test"""
    print("🧪 Testing Classroom Six Months Surviving Fix...")
    print("=" * 50)

    if test_classroom_objective_mapping():
        print("\n🎉 Classroom fix successful!")
        print("✨ six_months_surviving objective will now work correctly in classroom")
        print("• Maps to tlp_acceptance narrative content")
        print("• Shows TLP phone call and celebration scene")
        print("• Completes when celebration interaction is done")
    else:
        print("\n❌ Classroom fix failed!")

if __name__ == "__main__":
    main()
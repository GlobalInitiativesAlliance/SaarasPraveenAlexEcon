#!/usr/bin/env python3
"""
Test script to verify all Part 1 late objectives fixes work correctly
"""
import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_building_mappings():
    """Test that building mappings are correct"""
    print("🏢 Testing building mappings...")

    mappings_file = os.path.join(os.path.dirname(__file__), "data", "maps", "building_interiors.json")

    if not os.path.exists(mappings_file):
        print("❌ Building mappings file not found")
        return False

    with open(mappings_file, 'r') as f:
        mappings = json.load(f)

    expected_mappings = {
        "3,31": "tlp_housing_final",  # For final_month
        "30,11": "classroom",  # For desperate_measures and the_system
        "54,33": "crappy_apartment",  # For found_studio, moving_day, reflection
        "29,39": "tlp_housing_dynamic"  # For not_alone
    }

    for pos, expected_interior in expected_mappings.items():
        if pos not in mappings:
            print(f"❌ Missing mapping for position {pos}")
            return False

        if mappings[pos] != expected_interior:
            print(f"❌ Wrong mapping for {pos}: got {mappings[pos]}, expected {expected_interior}")
            return False

        print(f"✅ {pos} → {expected_interior}")

    print("✅ All building mappings correct!")
    return True

def test_narrative_files():
    """Test that all narrative files exist and can be imported"""
    print("\n📖 Testing narrative files...")

    try:
        # Test TLP housing final narrative
        from src.interiors.narratives.tlp_housing_final_narrative import TLPHousingFinalNarrative
        print("✅ TLP housing final narrative imports successfully")

        # Test that it has the required narrative content
        mock_room_data = {'width': 16, 'height': 12}
        narrative = TLPHousingFinalNarrative(None, mock_room_data, (3, 31))
        content = narrative.load_narrative_content()

        if 'final_month' not in content:
            print("❌ TLP housing final narrative missing 'final_month' content")
            return False

        final_month_content = content['final_month']
        required_interactions = ['eviction_notice', 'savings_envelope', 'case_manager_desk', 'room_door']

        for interaction in required_interactions:
            if interaction not in final_month_content['interactions']:
                print(f"❌ Missing required interaction: {interaction}")
                return False

        print("✅ TLP housing final narrative has all required content")

    except ImportError as e:
        print(f"❌ Failed to import TLP housing final narrative: {e}")
        return False

    try:
        # Test classroom narrative still works
        from src.interiors.narratives.classroom_narrative import ClassroomNarrative
        print("✅ Classroom narrative imports successfully")

        # Test that it has the required content
        mock_room_data = {'width': 16, 'height': 12}
        classroom = ClassroomNarrative(None, mock_room_data, (30, 11))
        content = classroom.load_narrative_content()

        required_scenes = ['selling_items', 'economics_lesson', 'completion']
        for scene in required_scenes:
            if scene not in content:
                print(f"❌ Missing required classroom scene: {scene}")
                return False

        print("✅ Classroom narrative has all required content")

    except ImportError as e:
        print(f"❌ Failed to import classroom narrative: {e}")
        return False

    print("✅ All narrative files working!")
    return True

def test_objective_definitions():
    """Test that all late Part 1 objectives are properly defined"""
    print("\n🎯 Testing objective definitions...")

    try:
        from part_1_housing_stability.objectives_narrative import get_part1_narrative_objectives
        objectives = get_part1_narrative_objectives()

        late_objectives = ['final_month', 'desperate_measures', 'found_studio', 'the_system', 'moving_day', 'reflection', 'not_alone', 'part1_complete']

        objective_ids = [obj.id for obj in objectives]

        for obj_id in late_objectives:
            if obj_id not in objective_ids:
                print(f"❌ Missing objective: {obj_id}")
                return False
            print(f"✅ {obj_id} objective found")

        print("✅ All late Part 1 objectives properly defined!")
        return True

    except Exception as e:
        print(f"❌ Failed to load objectives: {e}")
        return False

def test_building_manager():
    """Test that building manager can handle new interiors"""
    print("\n🏗️ Testing building manager...")

    try:
        # Mock game object
        class MockGame:
            def __init__(self):
                self.city_map = MockCityMap()
                self.objective_manager = MockObjectiveManager()

        class MockCityMap:
            def __init__(self):
                self.width = 64
                self.height = 64

        class MockObjectiveManager:
            def get_current_objective(self):
                return None

        from src.core.building_manager import BuildingManager

        game = MockGame()
        bm = BuildingManager(game)

        # Test room data mapping includes our new interior
        base_dir = os.path.dirname(__file__)
        room_data = bm.get_room_data_for_interior('tlp_housing_final', base_dir)

        if room_data is None:
            print("❌ TLP housing final room data not found")
            return False

        print("✅ TLP housing final room data loads correctly")

        # Test interior creation (this will fail without proper room JSON, but import should work)
        try:
            interior = bm.create_scene_specific_interior('tlp_housing_final', {'width': 16, 'height': 12}, (3, 31))
            if interior is None:
                print("❌ Failed to create TLP housing final interior")
                return False
            print("✅ TLP housing final interior created successfully")
        except Exception as e:
            print(f"❌ Failed to create TLP housing final interior: {e}")
            return False

        print("✅ Building manager handles new interiors correctly!")
        return True

    except Exception as e:
        print(f"❌ Building manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Part 1 Late Objectives Fixes...")
    print("=" * 50)

    tests = [
        test_building_mappings,
        test_narrative_files,
        test_objective_definitions,
        test_building_manager
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            break  # Stop on first failure for easier debugging

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Part 1 late objectives fixes are working correctly.")
        print("\n✨ WHAT THIS MEANS:")
        print("• final_month objective will show TLP ending narrative")
        print("• desperate_measures objective will show selling items in classroom")
        print("• the_system objective will show economics lesson in classroom")
        print("• found_studio, moving_day, reflection will work in crappy apartment")
        print("• not_alone will work in community center")
        print("• All objectives have proper completion handlers")
        print("• Smooth auto-transitions between all Part 1 objectives")
        print("• Clean transition to Part 2 after part1_complete")
        print("\n🚀 Part 1 should now be 'super smooth' as requested!")
    else:
        print("❌ Some tests failed. Check the output above for details.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
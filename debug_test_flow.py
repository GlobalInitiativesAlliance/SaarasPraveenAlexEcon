#!/usr/bin/env python3
"""
Debug Testing Script - Emergency Shelter → Library Apartment Search Flow
This script helps debug the specific flow where players get stuck after completing apartment search.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_apartment_search_flow():
    """Debug the specific flow that gets players stuck"""
    print("🔍 DEBUGGING APARTMENT SEARCH FLOW")
    print("=" * 50)

    # Test the specific scenario:
    # 1. Emergency shelter (reality_check objective)
    # 2. Library apartment search (apartment_search objective)
    # 3. Check what happens after completion

    print("📋 TESTING SCENARIO:")
    print("  1. Start at emergency shelter (reality_check)")
    print("  2. Enter emergency shelter → should be 'already checked in'")
    print("  3. Exit emergency shelter")
    print("  4. Go to library for apartment search")
    print("  5. Complete apartment search mini-game")
    print("  6. ❌ EXPECTED: Player gets stuck, can't exit room")
    print("  7. ❌ EXPECTED: Game doesn't progress to next objective")
    print("")

    # Import the game components we need to test
    from main import Game
    from core.objective_manager import ObjectiveManager

    # Create a minimal test game instance
    print("🎮 Creating test game instance...")
    try:
        game = Game()
        print("✅ Game instance created")

        # Check objective manager state
        if hasattr(game, 'objective_manager'):
            obj_mgr = game.objective_manager
            print(f"📍 Current objective: {obj_mgr.current_objective_index}")
            current_obj = obj_mgr.get_current_objective()
            if current_obj:
                print(f"🎯 Objective ID: {current_obj.id}")
                print(f"🎯 Objective Title: {current_obj.title}")

            # Check activity state
            if hasattr(obj_mgr, 'current_activity'):
                current_activity = obj_mgr.current_activity
                print(f"⚡ Current Activity: {current_activity}")
                if current_activity:
                    print(f"⚡ Activity Type: {type(current_activity).__name__}")
                    if hasattr(current_activity, 'active'):
                        print(f"⚡ Activity Active: {current_activity.active}")
                    if hasattr(current_activity, 'completed'):
                        print(f"⚡ Activity Completed: {current_activity.completed}")
        else:
            print("❌ No objective manager found")

    except Exception as e:
        print(f"❌ Error creating game: {e}")
        return

    print("")
    print("🔧 TO PROPERLY DEBUG THIS ISSUE:")
    print("  1. We need to run the game interactively")
    print("  2. Navigate through the exact flow")
    print("  3. Monitor debug output in real-time")
    print("  4. Identify where the state management breaks")
    print("")
    print("💡 HYPOTHESIS:")
    print("  - Apartment search activity completes but doesn't trigger objective progression")
    print("  - Room exit logic may be blocked by stale activity state")
    print("  - Natural narrative flow interrupted by safety systems")

if __name__ == "__main__":
    debug_apartment_search_flow()
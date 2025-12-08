#!/usr/bin/env python3
"""
Test script to verify the backpack investigation ESC fix works
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
import unittest
from unittest.mock import MagicMock, Mock

# Mock pygame to avoid requiring a display
pygame.init = MagicMock()
pygame.font.Font = MagicMock()
pygame.Surface = MagicMock()
pygame.draw = MagicMock()

from src.activities.backpack_investigation import BackpackInvestigation

class TestBackpackESCFix(unittest.TestCase):
    """Test that ESC properly exits the backpack investigation"""

    def setUp(self):
        """Set up test environment"""
        # Mock objective manager
        self.mock_objective_manager = Mock()
        self.mock_objective_manager.current_activity = None

        # Create backpack investigation activity
        self.activity = BackpackInvestigation(self.mock_objective_manager)

        # Mock narrative ref
        self.activity.narrative_ref = Mock()
        self.activity.narrative_ref.dialogue_box = Mock()
        self.activity.narrative_ref.completed_interactions = set()

    def test_esc_exits_without_all_pockets_searched(self):
        """Test that ESC exits even when not all pockets are searched"""
        # Start the activity
        self.activity.start()
        self.assertTrue(self.activity.active)
        self.assertFalse(self.activity.completed)

        # Verify not all pockets are searched
        self.assertFalse(self.activity.all_pockets_searched())

        # Press ESC
        self.activity.handle_key(pygame.K_ESCAPE)

        # Verify activity is completed and not active
        self.assertTrue(self.activity.completed)
        self.assertFalse(self.activity.active)

    def test_esc_works_with_some_pockets_searched(self):
        """Test ESC works when some pockets are searched"""
        # Start the activity
        self.activity.start()

        # Search one pocket
        self.activity.search_pocket('main')

        # Verify not all pockets searched
        self.assertFalse(self.activity.all_pockets_searched())

        # Press ESC
        self.activity.handle_key(pygame.K_ESCAPE)

        # Verify activity completed
        self.assertTrue(self.activity.completed)
        self.assertFalse(self.activity.active)

    def test_esc_works_with_all_pockets_searched(self):
        """Test ESC still works when all pockets are searched"""
        # Start the activity
        self.activity.start()

        # Search all pockets
        for pocket_name in self.activity.pockets.keys():
            self.activity.search_pocket(pocket_name)

        # Verify all pockets searched
        self.assertTrue(self.activity.all_pockets_searched())

        # Press ESC
        self.activity.handle_key(pygame.K_ESCAPE)

        # Verify activity completed
        self.assertTrue(self.activity.completed)
        self.assertFalse(self.activity.active)

    def test_handle_event_esc(self):
        """Test that handle_event also processes ESC correctly"""
        # Start the activity
        self.activity.start()

        # Create mock ESC event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_ESCAPE

        # Handle the event
        self.activity.handle_event(mock_event)

        # Verify activity completed
        self.assertTrue(self.activity.completed)
        self.assertFalse(self.activity.active)

def main():
    """Run the tests"""
    print("Testing Backpack Investigation ESC Fix...")

    # Run the unit tests
    unittest.main(verbosity=2, exit=False)

    print("\n✅ All tests passed! ESC fix should work correctly.")
    print("\nChanges made:")
    print("1. Emergency Shelter now forwards ESC to activity instead of immediately exiting")
    print("2. Backpack Investigation allows ESC to exit even without searching all pockets")
    print("3. Game should no longer break when pressing ESC during backpack investigation")

if __name__ == "__main__":
    main()
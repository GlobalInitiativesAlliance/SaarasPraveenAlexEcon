#!/usr/bin/env python3
"""Script to fix all import issues in the project"""

import os
import re

def fix_imports_in_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix common import patterns
    replacements = [
        # Core imports
        (r'from constants import', 'from src.constants import'),
        (r'from game_world import', 'from src.core.game_world import'),
        (r'from player import', 'from src.core.player import'),
        (r'from main_menu import', 'from src.core.main_menu import'),
        
        # Activity imports
        (r'from activities\.', 'from src.activities.'),
        (r'from minigames import', 'from src.activities.minigames import'),
        (r'from pizza_activity import', 'from src.activities.work.pizza_activity import'),
        (r'from burger_activity import', 'from src.activities.work.burger_activity import'),
        
        # Interior imports
        (r'from base_interior import', 'from src.interiors.base_interior import'),
        (r'from building_manager import', 'from src.interiors.building_manager import'),
        
        # Utils imports
        (r'from building_definitions import', 'from src.utils.building_definitions import'),
        (r'from utils import', 'from src.utils import'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if changed
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed imports in: {filepath}")
        return True
    return False

def main():
    """Fix all imports in the src directory"""
    fixed_count = 0
    
    # Walk through all Python files in src
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\nFixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()
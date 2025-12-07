#!/usr/bin/env python3
"""
Debug Analysis System: Part 1 vs Part 2 Comparison
This script analyzes the working Part 1 implementation to understand patterns
and identify what's missing or broken in Part 2.
"""

import os
import sys
import re
from pathlib import Path

class PartComparisonAnalyzer:
    def __init__(self):
        self.base_path = Path("/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon")
        self.part1_path = self.base_path / "part_1_housing_stability"
        self.part2_path = self.base_path / "part_2_healthcare"
        self.src_path = self.base_path / "src"

    def analyze_all(self):
        """Run complete analysis"""
        print("=" * 80)
        print("PART 1 vs PART 2 IMPLEMENTATION ANALYSIS")
        print("=" * 80)

        self.analyze_directory_structure()
        self.analyze_activity_patterns()
        self.analyze_interior_patterns()
        self.analyze_integration_patterns()
        self.generate_recommendations()

    def analyze_directory_structure(self):
        """Compare directory structures"""
        print("\n📁 DIRECTORY STRUCTURE COMPARISON")
        print("-" * 50)

        print("Part 1 structure:")
        for item in sorted(self.part1_path.rglob("*.py")):
            rel_path = item.relative_to(self.part1_path)
            print(f"  ✓ {rel_path}")

        print("\nPart 2 structure:")
        for item in sorted(self.part2_path.rglob("*.py")):
            rel_path = item.relative_to(self.part2_path)
            print(f"  ✓ {rel_path}")

    def analyze_activity_patterns(self):
        """Analyze how Part 1 activities work vs Part 2"""
        print("\n🎮 ACTIVITY PATTERNS ANALYSIS")
        print("-" * 50)

        # Part 1 mini-games
        part1_games = self.part1_path / "mini_games.py"
        if part1_games.exists():
            content = part1_games.read_text()
            classes = re.findall(r'class (\w+).*?:', content)
            methods = re.findall(r'def (draw|update|handle_\w+)', content)

            print(f"Part 1 mini-games classes: {classes}")
            print(f"Part 1 common methods: {set(methods)}")

            # Check for draw vs render
            if 'def draw(' in content:
                print("  ✓ Part 1 uses draw() method")
            if 'def render(' in content:
                print("  ⚠ Part 1 also has render() methods")

        # Part 2 activities
        part2_activities = list(self.part2_path.glob("activities/*.py"))
        print(f"\nPart 2 activities found: {len(part2_activities)}")
        for activity in part2_activities:
            content = activity.read_text()
            if 'def draw(' in content:
                print(f"  ✓ {activity.name} has draw() method")
            elif 'def render(' in content:
                print(f"  ⚠ {activity.name} has render() method (should be draw)")
            else:
                print(f"  ✗ {activity.name} missing draw/render method")

    def analyze_interior_patterns(self):
        """Analyze interior implementation patterns"""
        print("\n🏠 INTERIOR PATTERNS ANALYSIS")
        print("-" * 50)

        # Check src/interiors/narratives for working examples
        narrative_interiors = list((self.src_path / "interiors" / "narratives").glob("*.py"))

        print(f"Found {len(narrative_interiors)} working narrative interiors:")

        essential_methods = ['enter', 'setup_', 'update_objective_display', 'draw']

        for interior in narrative_interiors[:5]:  # Check first 5
            content = interior.read_text()
            print(f"\n  📄 {interior.name}:")

            for method in essential_methods:
                if method == 'setup_':
                    setup_methods = re.findall(r'def (setup_\w+)', content)
                    if setup_methods:
                        print(f"    ✓ Setup methods: {setup_methods[:3]}...")
                    else:
                        print(f"    ✗ No setup methods found")
                elif f'def {method}(' in content:
                    print(f"    ✓ Has {method}() method")
                else:
                    print(f"    ✗ Missing {method}() method")

        # Check Part 2 healthcare interior
        print(f"\n  📄 Part 2 Healthcare Interior:")
        healthcare_interior = self.part2_path / "interiors" / "healthcare_apartment_interior.py"
        if healthcare_interior.exists():
            content = healthcare_interior.read_text()
            for method in essential_methods:
                if method == 'setup_':
                    setup_methods = re.findall(r'def (setup_\w+)', content)
                    if setup_methods:
                        print(f"    ✓ Setup methods: {setup_methods[:3]}...")
                    else:
                        print(f"    ✗ No setup methods found")
                elif f'def {method}(' in content:
                    print(f"    ✓ Has {method}() method")
                else:
                    print(f"    ✗ Missing {method}() method")

    def analyze_integration_patterns(self):
        """Analyze how activities integrate with main game"""
        print("\n🔗 INTEGRATION PATTERNS ANALYSIS")
        print("-" * 50)

        main_py = self.src_path / "main.py"
        if main_py.exists():
            content = main_py.read_text()

            # Find Part 1 activity integrations
            part1_patterns = re.findall(r'elif current_obj\.id == ["\'](\w+)["\']:(.*?)(?=elif|$)', content, re.DOTALL)

            print("Part 1 activity integration patterns:")
            for obj_id, code in part1_patterns[:3]:
                if any(keyword in code for keyword in ['game', 'activity', 'start']):
                    lines = [line.strip() for line in code.split('\n') if line.strip()][:3]
                    print(f"  ✓ {obj_id}: {' | '.join(lines)}")

            # Check Part 2 integrations
            if 'check_mailbox' in content:
                print(f"\n  ✓ Part 2 mailbox integration found in main.py")
                mailbox_section = content[content.find('check_mailbox'):content.find('check_mailbox') + 500]
                print(f"    Code: {mailbox_section[:200]}...")
            else:
                print(f"\n  ✗ Part 2 mailbox integration missing from main.py")

    def analyze_objective_system(self):
        """Analyze how objectives are structured"""
        print("\n🎯 OBJECTIVE SYSTEM ANALYSIS")
        print("-" * 50)

        # Check Part 1 objectives
        part1_files = list(self.part1_path.glob("**/*objective*.py"))
        print(f"Part 1 objective files: {[f.name for f in part1_files]}")

        # Check Part 2 objectives
        part2_objectives = self.part2_path / "objectives.py"
        if part2_objectives.exists():
            content = part2_objectives.read_text()
            objectives = re.findall(r'GameObjective\(\s*["\'](\w+)["\']', content)
            print(f"Part 2 objectives: {objectives[:5]}... ({len(objectives)} total)")

    def generate_recommendations(self):
        """Generate specific recommendations to fix Part 2"""
        print("\n💡 RECOMMENDATIONS TO FIX PART 2")
        print("-" * 50)

        print("1. ✅ FIXED: Changed render() to draw() in mailbox activity")
        print("2. ✅ FIXED: Added enter() method to healthcare apartment interior")
        print("3. ✅ FIXED: Added setup methods for all objectives")
        print("4. ❌ TODO: Add update_objective_display() method")
        print("5. ❌ TODO: Verify activity mouse handling methods")
        print("6. ❌ TODO: Test actual narrative sequence progression")
        print("7. ❌ TODO: Verify objective completion triggers")

        print("\nNext steps:")
        print("  - Test the mailbox interaction in-game")
        print("  - Add proper error handling and debugging")
        print("  - Implement missing methods based on working Part 1 patterns")

if __name__ == "__main__":
    analyzer = PartComparisonAnalyzer()
    analyzer.analyze_all()
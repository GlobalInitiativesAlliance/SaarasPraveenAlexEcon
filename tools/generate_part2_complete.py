"""
Generate all Part 2 narrative scenes
"""

import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
tools_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tools_dir)

from scene_generator import SceneGenerator
from part2_scene_configs import PART2_COMPLETE_SCENES

def generate_all_part2_scenes():
    """Generate all narrative files for Part 2"""
    generator = SceneGenerator()

    print("GENERATING COMPLETE PART 2 SCENES")
    print("=" * 50)

    results = {
        'success': [],
        'failed': [],
        'updated': []
    }

    for location, config in PART2_COMPLETE_SCENES.items():
        print(f"\nProcessing {location}...")
        print("-" * 40)

        try:
            # Generate the scene file
            scene_content = generator.generate_scene(config)

            # Validate
            issues = generator.validate_scene(scene_content)
            if issues:
                print(f"  ⚠️  Validation issues: {issues}")

            # Determine output path
            if location == 'school':
                # School reuses sarah's place
                narrative_file = 'sarahs_place_narrative.py'
            elif location == 'courthouse':
                # Courthouse reuses rental office
                narrative_file = 'rental_office_narrative.py'
            elif location == 'new_apartment':
                # New apartment reuses alex's apartment
                narrative_file = 'alex_apartment_narrative.py'
            elif location == 'hospital':
                # Hospital needs its own narrative
                narrative_file = 'hospital_narrative.py'
            elif location == 'bank':
                # Bank needs its own narrative
                narrative_file = 'bank_narrative.py'
            else:
                narrative_file = f"{location}_narrative.py"

            output_path = f"/Users/praveenvadlamani/Desktop/SaarasPraveenAlexEcon/src/interiors/narratives/{narrative_file}"

            # Check if file exists
            file_exists = os.path.exists(output_path)

            if file_exists and location not in ['studio_apartment', 'library', 'grocery_store', 'legal_aid']:
                # For existing files that aren't our main Part 2 locations,
                # we'll need to merge the content carefully
                print(f"  ⚠️  {narrative_file} exists - would need merging")
                results['updated'].append(location)
            else:
                # Save the file
                with open(output_path, 'w') as f:
                    f.write(scene_content)

                if file_exists:
                    print(f"  ✅ Updated: {narrative_file}")
                    print(f"     {len(config['objectives'])} objectives added")
                    results['updated'].append(location)
                else:
                    print(f"  ✅ Created: {narrative_file}")
                    print(f"     {len(config['objectives'])} objectives")
                    results['success'].append(location)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results['failed'].append((location, str(e)))

    # Summary
    print("\n" + "=" * 50)
    print("GENERATION SUMMARY")
    print("=" * 50)

    if results['success']:
        print(f"\n✅ Successfully created {len(results['success'])} new narrative files:")
        for loc in results['success']:
            print(f"   - {loc}")

    if results['updated']:
        print(f"\n✅ Updated {len(results['updated'])} existing narrative files:")
        for loc in results['updated']:
            print(f"   - {loc}")

    if results['failed']:
        print(f"\n❌ Failed to generate {len(results['failed'])} files:")
        for loc, err in results['failed']:
            print(f"   - {loc}: {err}")

    total_objectives = sum(len(config['objectives']) for config in PART2_COMPLETE_SCENES.values())
    print(f"\n📊 Total objectives configured: {total_objectives}")

    return results

if __name__ == "__main__":
    generate_all_part2_scenes()
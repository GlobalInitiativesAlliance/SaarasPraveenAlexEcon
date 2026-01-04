#!/usr/bin/env python3
"""
Script to populate interior_rooms.json registry with all room data
from individual JSON files in data/interiors/rooms/
"""
import json
import os

def populate_interior_rooms():
    """Scan all room JSON files and merge into central registry"""

    registry = {"rooms": {}}
    rooms_dir = 'data/interiors/rooms/'

    print(f"Scanning directory: {rooms_dir}")

    if not os.path.exists(rooms_dir):
        print(f"ERROR: Directory {rooms_dir} does not exist!")
        return

    # Scan all room JSON files
    count = 0
    for filename in sorted(os.listdir(rooms_dir)):
        if filename.endswith('.json'):
            room_name = filename.replace('.json', '')
            filepath = os.path.join(rooms_dir, filename)

            try:
                with open(filepath, 'r') as f:
                    room_data = json.load(f)

                registry["rooms"][room_name] = room_data
                count += 1

                # Show file size for verification
                file_size = os.path.getsize(filepath)
                print(f"  ✓ Loaded {room_name:30s} ({file_size:>7,} bytes)")

            except Exception as e:
                print(f"  ✗ ERROR loading {filename}: {e}")

    print(f"\nTotal rooms loaded: {count}")

    # Write to both central registry locations
    output_files = [
        'data/interiors/interior_rooms.json',
        'interior_rooms.json'
    ]

    for output_file in output_files:
        try:
            with open(output_file, 'w') as f:
                json.dump(registry, f, indent=2)

            output_size = os.path.getsize(output_file)
            print(f"\n✓ Written to {output_file} ({output_size:,} bytes)")
        except Exception as e:
            print(f"\n✗ ERROR writing to {output_file}: {e}")

    # Verify grocery_store is present
    if 'grocery_store' in registry["rooms"]:
        print("\n✓ VERIFIED: grocery_store data is in registry")
    else:
        print("\n✗ WARNING: grocery_store not found in registry!")

    if 'groccery' in registry["rooms"]:
        print("✓ VERIFIED: groccery data is in registry (old misspelled version)")

if __name__ == '__main__':
    print("=" * 70)
    print("Populating interior_rooms.json Registry")
    print("=" * 70)
    populate_interior_rooms()
    print("=" * 70)
    print("Done!")

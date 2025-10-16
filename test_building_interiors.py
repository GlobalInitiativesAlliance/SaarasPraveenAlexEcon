#!/usr/bin/env python3
"""
Test script to verify building-interior system is working
"""
import pygame
import json
import os

def test_files_exist():
    """Check if all necessary files exist"""
    print("=" * 50)
    print("CHECKING FILES...")

    files_to_check = [
        ('data/maps/city_map_data.json', 'City map data'),
        ('data/maps/building_interiors.json', 'Building-interior mappings'),
        ('data/interiors/rooms/initial_room.json', 'Initial room definition')
    ]

    all_exist = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {description}: {file_path}")
        else:
            print(f"✗ {description}: {file_path} NOT FOUND")
            all_exist = False

    return all_exist

def test_map_data():
    """Check if map has building at expected position"""
    print("\n" + "=" * 50)
    print("CHECKING MAP DATA...")

    with open('data/maps/city_map_data.json', 'r') as f:
        map_data = json.load(f)

    success = True

    # Check position (4,1)
    cell_4_1 = map_data['map_data'][1][4]
    print(f"Cell at (4,1): type={cell_4_1.get('type')}, building={cell_4_1.get('building_name')}, offset=({cell_4_1.get('offset_x')},{cell_4_1.get('offset_y')})")

    if cell_4_1 and cell_4_1.get('building_name') == 'house_2' and cell_4_1.get('offset_x') == 0 and cell_4_1.get('offset_y') == 0:
        print("✓ Building 'house_2' base position found at (4,1)")
    else:
        print("✗ Expected building not found at position (4,1)")
        success = False

    # Check position (8,11)
    cell_8_11 = map_data['map_data'][11][8]
    print(f"\nCell at (8,11): type={cell_8_11.get('type')}, building={cell_8_11.get('building_name')}, offset=({cell_8_11.get('offset_x')},{cell_8_11.get('offset_y')})")

    if cell_8_11 and cell_8_11.get('building_name') == 'house_1' and cell_8_11.get('offset_x') == 0 and cell_8_11.get('offset_y') == 0:
        print("✓ Building 'house_1' base position found at (8,11)")
    else:
        print("✗ Expected building not found at position (8,11)")
        success = False

    return success

def test_mappings():
    """Check if building-interior mapping exists"""
    print("\n" + "=" * 50)
    print("CHECKING MAPPINGS...")

    with open('data/maps/building_interiors.json', 'r') as f:
        mappings = json.load(f)

    print(f"Mappings found: {mappings}")

    success = True
    if '4,1' in mappings:
        print(f"✓ Building at (4,1) is mapped to: {mappings['4,1']}")
    else:
        print("✗ No mapping found for building at (4,1)")
        success = False

    if '8,11' in mappings:
        print(f"✓ Building at (8,11) is mapped to: {mappings['8,11']}")
    else:
        print("✗ No mapping found for building at (8,11)")
        success = False

    return success

def test_room_file():
    """Check if room file exists and is valid"""
    print("\n" + "=" * 50)
    print("CHECKING ROOM FILE...")

    room_file = 'data/interiors/rooms/initial_room.json'
    if os.path.exists(room_file):
        with open(room_file, 'r') as f:
            room_data = json.load(f)

        print(f"✓ Room dimensions: {room_data.get('width', 0)}x{room_data.get('height', 0)}")
        print(f"✓ Has doors: {len(room_data.get('doors', [])) > 0}")
        return True
    else:
        print("✗ Room file not found")
        return False

def main():
    print("\n" + "=" * 50)
    print("BUILDING-INTERIOR SYSTEM TEST")
    print("=" * 50)

    tests = [
        test_files_exist(),
        test_map_data(),
        test_mappings(),
        test_room_file()
    ]

    print("\n" + "=" * 50)
    if all(tests):
        print("✓ ALL TESTS PASSED!")
        print("\nThe building-interior system is properly configured.")
        print("You should be able to:")
        print("1. See 'Press E to enter' when near buildings at (4,1) or (8,11)")
        print("2. Press E to enter the initial_room interior")
        print("3. Move around inside and press E at doors to exit")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease fix the issues above and try again.")

    print("\n" + "=" * 50)
    print("DEBUG TIPS:")
    print("- Buildings with interiors are at positions (4,1) and (8,11)")
    print("- These are near the top-left corner of the map")
    print("- Check the console for 'Found building with interior' messages")
    print("- You should see 'Press E to enter' when within 2 tiles of these buildings")

if __name__ == "__main__":
    main()
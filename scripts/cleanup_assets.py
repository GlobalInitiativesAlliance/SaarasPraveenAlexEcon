#!/usr/bin/env python3
"""
Asset Cleanup Script - Removes unused assets to reduce build size.

This script identifies and removes assets that are not referenced in the codebase,
significantly reducing the web build size for better Chromebook performance.

Before running:
- Total moderninteriors-win size: ~165MB

After cleanup (estimated):
- Total size: ~10-15MB

Usage:
    python scripts/cleanup_assets.py --dry-run  # Preview what will be deleted
    python scripts/cleanup_assets.py            # Actually delete files
"""

import os
import shutil
import argparse

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "moderninteriors-win")

# Directories that can be completely removed (not used in codebase)
REMOVE_DIRS = [
    "3_Animated_objects",  # 11MB - not used
    "6_Home_Designs",      # 2.7MB - not used
    "1_Interiors/16x16/Old stuff",  # 260KB - not used
    "1_Interiors/16x16/Theme_Sorter_Black_Shadow",  # 1.3MB - not used
    "1_Interiors/16x16/Theme_Sorter_Black_Shadow_Singles",  # 21MB - not used
    "1_Interiors/16x16/Theme_Sorter_Singles",  # 21MB - not used
    "1_Interiors/16x16/Theme_Sorter_Shadowless",  # 1.8MB - not used (using Theme_Sorter instead)
]

# Files/dirs to keep in Theme_Sorter_Shadowless_Singles (only Grocery Store used)
SHADOWLESS_SINGLES_KEEP = [
    "16_Grocery_Store_Singles_Shadowless",
]

# Files to keep in 2_Characters (only Character_Generator used)
CHARACTERS_KEEP = [
    "Character_Generator",
]


def get_dir_size(path):
    """Get total size of a directory in bytes."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def format_size(size_bytes):
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def cleanup_assets(dry_run=True):
    """
    Remove unused assets from moderninteriors-win directory.

    Args:
        dry_run: If True, only print what would be deleted without actually deleting.
    """
    total_freed = 0
    actions = []

    print(f"Asset cleanup script {'(DRY RUN)' if dry_run else ''}")
    print(f"Working directory: {ASSETS_DIR}")
    print("-" * 60)

    # 1. Remove entire directories that are not used
    for rel_dir in REMOVE_DIRS:
        dir_path = os.path.join(ASSETS_DIR, rel_dir)
        if os.path.exists(dir_path):
            size = get_dir_size(dir_path)
            total_freed += size
            actions.append(f"DELETE DIR: {rel_dir} ({format_size(size)})")
            if not dry_run:
                shutil.rmtree(dir_path)
                print(f"  Deleted: {rel_dir}")

    # 2. Clean up Theme_Sorter_Shadowless_Singles - keep only Grocery Store
    shadowless_singles = os.path.join(
        ASSETS_DIR, "1_Interiors", "16x16", "Theme_Sorter_Shadowless_Singles"
    )
    if os.path.exists(shadowless_singles):
        for item in os.listdir(shadowless_singles):
            if item not in SHADOWLESS_SINGLES_KEEP:
                item_path = os.path.join(shadowless_singles, item)
                if os.path.isdir(item_path):
                    size = get_dir_size(item_path)
                    total_freed += size
                    actions.append(f"DELETE DIR: Theme_Sorter_Shadowless_Singles/{item} ({format_size(size)})")
                    if not dry_run:
                        shutil.rmtree(item_path)

    # 3. Clean up 2_Characters - keep only Character_Generator
    characters_dir = os.path.join(ASSETS_DIR, "2_Characters")
    if os.path.exists(characters_dir):
        for item in os.listdir(characters_dir):
            if item not in CHARACTERS_KEEP:
                item_path = os.path.join(characters_dir, item)
                if os.path.isdir(item_path):
                    size = get_dir_size(item_path)
                    total_freed += size
                    actions.append(f"DELETE DIR: 2_Characters/{item} ({format_size(size)})")
                    if not dry_run:
                        shutil.rmtree(item_path)

    # Print summary
    print("\nActions:")
    for action in actions:
        print(f"  {action}")

    print("-" * 60)
    print(f"Total space to free: {format_size(total_freed)}")

    if dry_run:
        print("\nThis was a dry run. No files were deleted.")
        print("Run without --dry-run to actually delete files.")
    else:
        print(f"\nCleanup complete! Freed {format_size(total_freed)}")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up unused assets to reduce build size."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what will be deleted without actually deleting"
    )
    args = parser.parse_args()

    if not os.path.exists(ASSETS_DIR):
        print(f"Error: Assets directory not found: {ASSETS_DIR}")
        return 1

    # Get initial size
    initial_size = get_dir_size(ASSETS_DIR)
    print(f"Current assets size: {format_size(initial_size)}")

    cleanup_assets(dry_run=args.dry_run)

    if not args.dry_run:
        final_size = get_dir_size(ASSETS_DIR)
        print(f"Final assets size: {format_size(final_size)}")

    return 0


if __name__ == "__main__":
    exit(main())

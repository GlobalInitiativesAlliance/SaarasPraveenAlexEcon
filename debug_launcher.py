#!/usr/bin/env python3
"""
Debug Launcher - Quick Game Testing
Launch the game at specific objectives, parts, or with debug presets for fast testing.

Usage:
    python debug_launcher.py                           # Normal game launch
    python debug_launcher.py --objective check_mailbox  # Start at specific objective
    python debug_launcher.py --part 2                  # Start at specific part
    python debug_launcher.py --preset test_clinic      # Use debug preset
    python debug_launcher.py --list-objectives         # List all objectives
    python debug_launcher.py --list-presets           # List all presets
"""

import argparse
import sys
import os
import json
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_debug_config():
    """Load debug configuration from debug_config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'debug_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Debug config not found at {config_path}")
        print("Creating default config...")
        create_default_config(config_path)
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing debug config: {e}")
        return {}

def create_default_config(config_path):
    """Create a default debug configuration file"""
    default_config = {
        "debug_mode": True,
        "show_all_objectives": True,
        "instant_transitions": False,
        "presets": {
            "test_mailbox": {
                "description": "Test mailbox sorting mini-game",
                "part": 2,
                "objective": "check_mailbox",
                "player_pos": [54, 33],
                "stats": {
                    "money": 100.0,
                    "health": 80,
                    "stress": 50,
                    "energy": 70
                }
            },
            "test_clinic": {
                "description": "Test clinic checklist and forms",
                "part": 2,
                "objective": "clinic_checklist",
                "player_pos": [34, 31],
                "stats": {
                    "money": 50.0,
                    "health": 60,
                    "stress": 70,
                    "energy": 50
                },
                "enter_interior": "clinic"
            },
            "test_breathing": {
                "description": "Test breathing exercise at work",
                "part": 2,
                "objective": "breathing_exercise",
                "player_pos": [39, 51],
                "stats": {
                    "money": 75.0,
                    "health": 40,
                    "stress": 90,
                    "energy": 30
                }
            },
            "test_pharmacy": {
                "description": "Test pharmacy medication selection",
                "part": 2,
                "objective": "pharmacy_visit",
                "player_pos": [12, 34],
                "stats": {
                    "money": 25.0,
                    "health": 50,
                    "stress": 80,
                    "energy": 60
                }
            },
            "part1_start": {
                "description": "Start Part 1 - Housing Stability",
                "part": 1,
                "objective": "school_quiz",
                "player_pos": [25, 25],
                "stats": {
                    "money": 73.0,
                    "health": 80,
                    "stress": 50,
                    "energy": 70
                }
            },
            "part2_start": {
                "description": "Start Part 2 - Healthcare Access",
                "part": 2,
                "objective": "start_apartment_morning",
                "player_pos": [54, 33],
                "stats": {
                    "money": 200.0,
                    "health": 80,
                    "stress": 40,
                    "energy": 80
                }
            }
        }
    }

    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=4)
    print(f"✅ Created default debug config at {config_path}")

def list_objectives():
    """List all available objectives from both parts"""
    print("\n📋 AVAILABLE OBJECTIVES:")
    print("=" * 50)

    # Import game components to get objectives
    try:
        from src.core.game_world import ObjectiveManager
        from src.main import Game

        # Create temporary game to access objectives
        game = Game()
        obj_mgr = game.objective_manager

        # Part 1 objectives
        obj_mgr.game_part = 1
        obj_mgr.setup_objectives()
        print("\n🏠 PART 1 - HOUSING STABILITY:")
        for i, obj in enumerate(obj_mgr.objectives):
            print(f"  {i:2d}. {obj.id:<25} - {obj.title}")

        # Part 2 objectives
        obj_mgr.game_part = 2
        obj_mgr.setup_objectives()
        print("\n🏥 PART 2 - HEALTHCARE ACCESS:")
        for i, obj in enumerate(obj_mgr.objectives):
            print(f"  {i:2d}. {obj.id:<25} - {obj.title}")

    except ImportError as e:
        print(f"❌ Could not import game components: {e}")
    except Exception as e:
        print(f"❌ Error listing objectives: {e}")

def list_presets(config):
    """List all available debug presets"""
    print("\n🎮 AVAILABLE PRESETS:")
    print("=" * 50)

    if 'presets' not in config or not config['presets']:
        print("No presets found in debug config.")
        return

    for preset_name, preset_data in config['presets'].items():
        desc = preset_data.get('description', 'No description')
        part = preset_data.get('part', '?')
        obj = preset_data.get('objective', 'unknown')
        print(f"\n📌 {preset_name}")
        print(f"   Description: {desc}")
        print(f"   Part {part} → {obj}")
        if 'stats' in preset_data:
            stats = preset_data['stats']
            print(f"   Stats: Money=${stats.get('money', 0)}, Health={stats.get('health', 0)}")

def main():
    """Main debug launcher function"""
    parser = argparse.ArgumentParser(
        description="Debug launcher for Economics Adventure Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_launcher.py --preset test_clinic
  python debug_launcher.py --part 2 --objective check_mailbox
  python debug_launcher.py --list-presets
        """
    )

    parser.add_argument('--objective', '-o',
                       help='Start at specific objective ID')
    parser.add_argument('--part', '-p', type=int, choices=[1, 2, 3, 4, 5, 6, 7],
                       help='Start at specific game part')
    parser.add_argument('--preset',
                       help='Use debug preset from config')
    parser.add_argument('--list-objectives', action='store_true',
                       help='List all available objectives and exit')
    parser.add_argument('--list-presets', action='store_true',
                       help='List all available presets and exit')
    parser.add_argument('--debug-menu', action='store_true',
                       help='Enable debug menu (F1) at startup')
    parser.add_argument('--player-pos', nargs=2, type=int, metavar=('X', 'Y'),
                       help='Set player starting position')
    parser.add_argument('--money', type=float,
                       help='Set starting money amount')

    args = parser.parse_args()

    # Load debug configuration
    config = load_debug_config()

    # Handle listing commands
    if args.list_objectives:
        list_objectives()
        return

    if args.list_presets:
        list_presets(config)
        return

    # Prepare debug settings
    debug_settings = {
        'debug_mode': True,
        'show_debug_menu': args.debug_menu,
    }

    # Handle preset
    if args.preset:
        if 'presets' in config and args.preset in config['presets']:
            preset = config['presets'][args.preset]
            debug_settings.update(preset)
            print(f"🎮 Loading preset: {args.preset}")
            if 'description' in preset:
                print(f"   {preset['description']}")
        else:
            print(f"❌ Preset '{args.preset}' not found!")
            print("Available presets:")
            list_presets(config)
            return

    # Handle individual arguments (override preset)
    if args.part:
        debug_settings['part'] = args.part

    if args.objective:
        debug_settings['objective'] = args.objective

    if args.player_pos:
        debug_settings['player_pos'] = args.player_pos

    if args.money is not None:
        if 'stats' not in debug_settings:
            debug_settings['stats'] = {}
        debug_settings['stats']['money'] = args.money

    # Apply global config settings
    debug_settings.update({
        'show_all_objectives': config.get('show_all_objectives', True),
        'instant_transitions': config.get('instant_transitions', False)
    })

    # Print startup info
    print("\n🚀 LAUNCHING ECONOMICS ADVENTURE (DEBUG MODE)")
    print("=" * 50)
    if 'part' in debug_settings:
        print(f"🎯 Starting Part: {debug_settings['part']}")
    if 'objective' in debug_settings:
        print(f"🎯 Starting Objective: {debug_settings['objective']}")
    if 'player_pos' in debug_settings:
        x, y = debug_settings['player_pos']
        print(f"📍 Player Position: ({x}, {y})")
    if 'stats' in debug_settings:
        stats = debug_settings['stats']
        print(f"💰 Starting Stats: ${stats.get('money', '?')} | Health: {stats.get('health', '?')}")

    print("\n🔧 DEBUG CONTROLS:")
    print("  F1 - Debug Menu")
    print("  F3 - Debug Panel")
    print("  N  - Skip Objective")
    print("  P  - Skip to Next Part")
    print("  Ctrl+ESC - Emergency Exit")
    print("\n" + "="*50)

    # Install pygame if needed
    try:
        import pygame
    except ImportError:
        print('Installing pygame...')
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame==2.5.2'])

    # Import and start the game with debug settings
    from src.main import main as game_main

    # Store debug settings in a way the game can access
    import src.core.debug_system as debug_system
    debug_system.set_debug_settings(debug_settings)

    # Launch the game
    asyncio.run(game_main())

if __name__ == "__main__":
    main()
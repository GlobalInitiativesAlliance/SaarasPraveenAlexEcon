"""
CLI Controller - Command-line interface for game control
Enables starting the game at any scene/objective via command line arguments
"""

import argparse
import sys

class CLIController:
    """Command-line interface controller for game startup"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='SaarasPraveenAlexEcon Game - Healthcare Access Simulation',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_epilog()
        )
        self._setup_arguments()
        self.args = None

    def _setup_arguments(self):
        """Setup command-line arguments"""

        # Scene jumping
        self.parser.add_argument(
            '--scene',
            help='Jump directly to a scene (burger_rush, doctor, therapist, etc.)',
            choices=['burger_rush', 'doctor', 'doctor_enhanced', 'therapist', 'breathing',
                    'pharmacy', 'part2_start', 'part1_burger']
        )

        # Part control
        self.parser.add_argument(
            '--part',
            type=int,
            choices=[1, 2, 3, 4, 5, 6],
            help='Start at specific game part (1-6)'
        )

        # Objective control
        self.parser.add_argument(
            '--objective',
            help='Start at specific objective ID'
        )

        # Position control
        self.parser.add_argument(
            '--position',
            nargs=2,
            type=int,
            metavar=('X', 'Y'),
            help='Set player position (X Y coordinates)'
        )

        # State management
        self.parser.add_argument(
            '--state-export',
            action='store_true',
            help='Enable continuous state export to current_state.json'
        )

        self.parser.add_argument(
            '--state-interval',
            type=float,
            default=1.0,
            help='State export interval in seconds (default: 1.0)'
        )

        # API server
        self.parser.add_argument(
            '--api',
            action='store_true',
            help='Start HTTP API server for external control'
        )

        self.parser.add_argument(
            '--api-port',
            type=int,
            default=8080,
            help='API server port (default: 8080)'
        )

        # Debug options
        self.parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with additional logging'
        )

        self.parser.add_argument(
            '--list-scenes',
            action='store_true',
            help='List all available scenes and exit'
        )

        self.parser.add_argument(
            '--export-debug',
            action='store_true',
            help='Export debug information and continue'
        )

        # Game control
        self.parser.add_argument(
            '--fullscreen',
            action='store_true',
            help='Start in fullscreen mode'
        )

        self.parser.add_argument(
            '--no-audio',
            action='store_true',
            help='Disable audio'
        )

    def _get_epilog(self):
        """Get help epilog with examples"""
        return """
Examples:
  python3 src/main.py --scene burger_rush
      Start directly in the burger cooking mini-game

  python3 src/main.py --part 2 --objective doctor_appointment
      Start at Part 2 doctor appointment

  python3 src/main.py --state-export --api --api-port 8080
      Start with state export and API server

  python3 src/main.py --scene doctor --debug --state-export
      Debug doctor scene with state monitoring

  python3 src/main.py --list-scenes
      Show all available scenes

Available Scenes:
  burger_rush    - Fixed burger cooking mini-game
  doctor         - Basic doctor appointment
  doctor_enhanced- Enhanced clinic experience
  therapist      - Therapy appointment call
  breathing      - Breathing exercise activity
  pharmacy       - Pharmacy medication selection
  part2_start    - Start of Part 2 healthcare
  part1_burger   - Part 1 burger job training
        """

    def parse_args(self, args=None):
        """Parse command-line arguments"""
        self.args = self.parser.parse_args(args)
        return self.args

    def apply_to_game(self, game):
        """Apply parsed arguments to game instance"""
        if not self.args:
            print("[CLI] No arguments parsed. Call parse_args() first.")
            return

        print("[CLI] Applying command-line arguments...")

        # Handle list scenes
        if self.args.list_scenes:
            self._list_scenes_and_exit(game)

        # Export debug info
        if self.args.export_debug:
            self._export_debug_info(game)

        # Setup state API
        if self.args.state_export:
            self._setup_state_export(game)

        # Setup API server
        if self.args.api:
            self._setup_api_server(game)

        # Apply game modifications
        if self.args.part:
            self._set_part(game, self.args.part)

        if self.args.objective:
            self._jump_to_objective(game, self.args.objective)

        if self.args.position:
            self._set_position(game, self.args.position)

        if self.args.scene:
            self._jump_to_scene(game, self.args.scene)

        # Apply game settings
        if self.args.debug:
            self._enable_debug_mode(game)

        print("[CLI] Command-line arguments applied successfully")

    def _list_scenes_and_exit(self, game):
        """List available scenes and exit"""
        from src.core.scene_manager import SceneManager
        scene_manager = SceneManager(game)

        print("\n" + "="*60)
        print("AVAILABLE SCENES")
        print("="*60)

        for scene_name, scene_data in scene_manager.get_available_scenes().items():
            print(f"\n{scene_name:15} - {scene_data['name']}")
            print(f"{'':15}   {scene_data['description']}")
            if 'part' in scene_data:
                print(f"{'':15}   Part {scene_data['part']}")
            if 'objective' in scene_data:
                print(f"{'':15}   Objective: {scene_data['objective']}")

        print("\n" + "="*60)
        sys.exit(0)

    def _export_debug_info(self, game):
        """Export debug information"""
        if not hasattr(game, 'state_api'):
            from src.core.game_state_api import GameStateAPI
            game.state_api = GameStateAPI(game)

        debug_file = game.state_api.export_debug_info()
        if debug_file:
            print(f"[CLI] Debug info exported to {debug_file}")

    def _setup_state_export(self, game):
        """Setup continuous state export"""
        if not hasattr(game, 'state_api'):
            from src.core.game_state_api import GameStateAPI
            game.state_api = GameStateAPI(game)

        game.state_api.enable_continuous_export(self.args.state_interval)
        print(f"[CLI] State export enabled (interval: {self.args.state_interval}s)")

    def _setup_api_server(self, game):
        """Setup HTTP API server"""
        try:
            from src.core.api_server import GameAPIServer
            game.api_server = GameAPIServer(game, self.args.api_port)
            game.api_server.start()
            print(f"[CLI] API server started on port {self.args.api_port}")
        except ImportError:
            print("[CLI] API server not available (flask not installed)")
        except Exception as e:
            print(f"[CLI] Failed to start API server: {e}")

    def _set_part(self, game, part):
        """Set game part"""
        if not hasattr(game, 'scene_manager'):
            from src.core.scene_manager import SceneManager
            game.scene_manager = SceneManager(game)

        game.scene_manager._set_game_part(part)
        print(f"[CLI] Set game part to {part}")

    def _jump_to_objective(self, game, objective_id):
        """Jump to specific objective"""
        if not hasattr(game, 'scene_manager'):
            from src.core.scene_manager import SceneManager
            game.scene_manager = SceneManager(game)

        game.scene_manager._jump_to_objective(objective_id)
        print(f"[CLI] Jumped to objective: {objective_id}")

    def _set_position(self, game, position):
        """Set player position"""
        if not hasattr(game, 'scene_manager'):
            from src.core.scene_manager import SceneManager
            game.scene_manager = SceneManager(game)

        game.scene_manager._teleport_player(position)
        print(f"[CLI] Set player position to {position}")

    def _jump_to_scene(self, game, scene_name):
        """Jump to specific scene"""
        if not hasattr(game, 'scene_manager'):
            from src.core.scene_manager import SceneManager
            game.scene_manager = SceneManager(game)

        success = game.scene_manager.jump_to_scene(scene_name)
        if success:
            print(f"[CLI] Jumped to scene: {scene_name}")
        else:
            print(f"[CLI] Failed to jump to scene: {scene_name}")

    def _enable_debug_mode(self, game):
        """Enable debug mode"""
        print("[CLI] Debug mode enabled")

        # Enable debug panel
        if hasattr(game, 'debug_panel'):
            game.debug_panel.visible = True

        # Enable debug menu
        if hasattr(game, 'debug_menu'):
            game.debug_menu.visible = True

    def get_startup_summary(self):
        """Get summary of startup configuration"""
        if not self.args:
            return "No CLI arguments provided"

        summary_parts = []

        if self.args.scene:
            summary_parts.append(f"Scene: {self.args.scene}")

        if self.args.part:
            summary_parts.append(f"Part: {self.args.part}")

        if self.args.objective:
            summary_parts.append(f"Objective: {self.args.objective}")

        if self.args.position:
            summary_parts.append(f"Position: {self.args.position}")

        if self.args.state_export:
            summary_parts.append(f"State Export: {self.args.state_interval}s")

        if self.args.api:
            summary_parts.append(f"API: Port {self.args.api_port}")

        if self.args.debug:
            summary_parts.append("Debug Mode")

        return " | ".join(summary_parts) if summary_parts else "Default startup"
"""
HTTP API Server - REST API for external game control
Provides external access to game state and control via HTTP endpoints
"""

import threading
import time
from datetime import datetime

try:
    from flask import Flask, jsonify, request, Response
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

class GameAPIServer:
    """HTTP API server for external game control"""

    def __init__(self, game, port=8080):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not available. Install with: pip install flask flask-cors")

        self.game = game
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web interfaces

        self.server_thread = None
        self.running = False

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.route('/')
        def index():
            """API documentation"""
            return jsonify({
                "name": "SaarasPraveenAlexEcon Game API",
                "version": "1.0",
                "endpoints": {
                    "/state": "GET - Get current game state",
                    "/state/summary": "GET - Get brief state summary",
                    "/scenes": "GET - List available scenes",
                    "/scenes/{name}": "POST - Jump to scene",
                    "/control/jump": "POST - Jump to objective/scene",
                    "/control/teleport": "POST - Teleport player",
                    "/control/key": "POST - Send key event",
                    "/debug/export": "POST - Export debug info",
                    "/api/status": "GET - API server status"
                }
            })

        @self.app.route('/state')
        def get_state():
            """Get complete game state"""
            try:
                if not hasattr(self.game, 'state_api'):
                    from src.core.game_state_api import GameStateAPI
                    self.game.state_api = GameStateAPI(self.game)

                state = self.game.state_api.get_full_state()
                return jsonify(state)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/state/summary')
        def get_state_summary():
            """Get brief state summary"""
            try:
                if not hasattr(self.game, 'state_api'):
                    from src.core.game_state_api import GameStateAPI
                    self.game.state_api = GameStateAPI(self.game)

                summary = self.game.state_api.get_state_summary()
                return jsonify({"summary": summary, "timestamp": datetime.now().isoformat()})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/scenes')
        def list_scenes():
            """List available scenes"""
            try:
                if not hasattr(self.game, 'scene_manager'):
                    from src.core.scene_manager import SceneManager
                    self.game.scene_manager = SceneManager(self.game)

                scenes = self.game.scene_manager.get_available_scenes()
                return jsonify(scenes)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/scenes/<scene_name>', methods=['POST'])
        def jump_to_scene(scene_name):
            """Jump to specific scene"""
            try:
                if not hasattr(self.game, 'scene_manager'):
                    from src.core.scene_manager import SceneManager
                    self.game.scene_manager = SceneManager(self.game)

                success = self.game.scene_manager.jump_to_scene(scene_name)
                return jsonify({
                    "success": success,
                    "scene": scene_name,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route('/control/jump', methods=['POST'])
        def control_jump():
            """Jump to objective or scene"""
            try:
                data = request.json
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400

                if not hasattr(self.game, 'scene_manager'):
                    from src.core.scene_manager import SceneManager
                    self.game.scene_manager = SceneManager(self.game)

                success = False
                action = None

                if 'scene' in data:
                    success = self.game.scene_manager.jump_to_scene(data['scene'])
                    action = f"jump_to_scene({data['scene']})"

                elif 'objective' in data:
                    self.game.scene_manager._jump_to_objective(data['objective'])
                    success = True
                    action = f"jump_to_objective({data['objective']})"

                elif 'part' in data:
                    self.game.scene_manager._set_game_part(data['part'])
                    success = True
                    action = f"set_part({data['part']})"

                else:
                    return jsonify({"error": "Must specify 'scene', 'objective', or 'part'"}), 400

                return jsonify({
                    "success": success,
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route('/control/teleport', methods=['POST'])
        def control_teleport():
            """Teleport player to position"""
            try:
                data = request.json
                if not data or 'position' not in data:
                    return jsonify({"error": "Must provide 'position' as [x, y]"}), 400

                if not hasattr(self.game, 'scene_manager'):
                    from src.core.scene_manager import SceneManager
                    self.game.scene_manager = SceneManager(self.game)

                position = data['position']
                if not isinstance(position, list) or len(position) != 2:
                    return jsonify({"error": "Position must be [x, y]"}), 400

                self.game.scene_manager._teleport_player(position)

                return jsonify({
                    "success": True,
                    "action": f"teleport_to({position})",
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route('/control/key', methods=['POST'])
        def control_key():
            """Send key event to game"""
            try:
                data = request.json
                if not data or 'key' not in data:
                    return jsonify({"error": "Must provide 'key'"}), 400

                key = data['key']

                # This would require pygame event injection
                # For now, just return success
                return jsonify({
                    "success": True,
                    "action": f"key_press({key})",
                    "note": "Key injection not implemented yet",
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route('/debug/export', methods=['POST'])
        def debug_export():
            """Export debug information"""
            try:
                if not hasattr(self.game, 'state_api'):
                    from src.core.game_state_api import GameStateAPI
                    self.game.state_api = GameStateAPI(self.game)

                debug_file = self.game.state_api.export_debug_info()

                return jsonify({
                    "success": bool(debug_file),
                    "file": debug_file,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @self.app.route('/api/status')
        def api_status():
            """Get API server status"""
            return jsonify({
                "status": "running",
                "port": self.port,
                "uptime": time.time() - getattr(self, 'start_time', time.time()),
                "game_connected": hasattr(self.game, 'objective_manager'),
                "endpoints_available": len(self.app.url_map._rules),
                "timestamp": datetime.now().isoformat()
            })

        # Stream endpoint for real-time state monitoring
        @self.app.route('/stream/state')
        def stream_state():
            """Stream real-time game state"""
            def generate():
                while self.running:
                    try:
                        if not hasattr(self.game, 'state_api'):
                            from src.core.game_state_api import GameStateAPI
                            self.game.state_api = GameStateAPI(self.game)

                        state = self.game.state_api.get_full_state()
                        yield f"data: {jsonify(state).get_data(as_text=True)}\n\n"
                        time.sleep(1)  # 1 second intervals
                    except Exception as e:
                        yield f"data: {jsonify({'error': str(e)}).get_data(as_text=True)}\n\n"
                        time.sleep(1)

            return Response(generate(), mimetype='text/plain')

    def start(self):
        """Start the API server in a background thread"""
        if self.running:
            print("[API] Server already running")
            return

        self.running = True
        self.start_time = time.time()

        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()

        # Wait a moment for server to start
        time.sleep(0.5)

        print(f"[API] Server started on http://localhost:{self.port}")
        print(f"[API] Endpoints: http://localhost:{self.port}/")

    def _run_server(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host='localhost',
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            print(f"[API] Server error: {e}")
            self.running = False

    def stop(self):
        """Stop the API server"""
        self.running = False
        print("[API] Server stopped")

    def get_status(self):
        """Get server status"""
        return {
            "running": self.running,
            "port": self.port,
            "uptime": time.time() - getattr(self, 'start_time', time.time()) if self.running else 0
        }


# Simple API server without Flask (fallback)
class SimpleAPIServer:
    """Simple HTTP server fallback if Flask is not available"""

    def __init__(self, game, port=8080):
        self.game = game
        self.port = port
        self.running = False

    def start(self):
        print(f"[API] Flask not available. Simple API server not implemented.")
        print(f"[API] Install Flask with: pip install flask flask-cors")

    def stop(self):
        pass

    def get_status(self):
        return {"running": False, "error": "Flask not available"}
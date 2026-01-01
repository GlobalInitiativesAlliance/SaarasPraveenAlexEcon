"""
Auto-Player - Automatically plays through the game for testing
Simulates actual player input (keypresses, clicks) for natural gameplay
"""

import pygame
import time
import math


class AutoPlayer:
    """Automatically plays the game by simulating player input"""

    def __init__(self, game, speed: float = 0.2):
        self.game = game
        self.speed = speed  # Seconds between actions
        self.enabled = False
        self.last_action_time = 0
        self.actions_taken = 0
        self.objectives_completed = 0
        self.start_time = None

        # Movement state
        self.target_tile = None
        self.path = []
        self.move_cooldown = 0
        self.move_direction = None  # Current direction we're holding

        # Track state
        self.stuck_counter = 0
        self.last_objective_id = None
        self.last_state = None
        self.activity_complete_count = 0  # Track repeated activity completions
        self.last_activity_name = None

    def start_full_playthrough(self, from_part: int = 1):
        """Start a full automatic playthrough"""
        self.enabled = True
        self.start_time = time.time()
        self.actions_taken = 0
        self.objectives_completed = 0
        self.path = []
        self.target_tile = None

        print("\n" + "=" * 60)
        print("🤖 AUTO-PLAY: FULL PLAYTHROUGH STARTED")
        print(f"   Speed: {self.speed}s between actions")
        print("   Press 'A' to toggle auto-play on/off")
        print("=" * 60 + "\n")

    def update(self, dt: float):
        """Called every frame"""
        if not self.enabled:
            return

        if self.start_time is None:
            self.start_time = time.time()

        # Wait for player movement to complete, then queue next step
        if self._is_player_moving():
            return  # Let the smooth walking animation play

        # Take next step immediately if we have a path
        if self.path:
            self._take_next_step()
            return  # Keep walking, don't do other actions

        # Rate limit actions
        current_time = time.time()
        if current_time - self.last_action_time < self.speed:
            return

        self.last_action_time = current_time

        # Determine current state and take appropriate action
        state = self._get_game_state()

        if state != self.last_state:
            print(f"[AUTO] State: {state}")
            self.last_state = state

        action_taken = False

        if state == 'dialogue_active':
            # Press SPACE to advance dialogue
            self._simulate_key(pygame.K_SPACE)
            action_taken = True

        elif state == 'activity_active':
            # Auto-complete the activity
            action_taken = self._auto_complete_activity()

        elif state == 'in_interior':
            # Try to interact with something or exit
            action_taken = self._handle_interior()

        elif state == 'in_world':
            # Move to objective or enter building
            action_taken = self._handle_world()

        if action_taken:
            self.actions_taken += 1
            self.stuck_counter = 0
        else:
            self.stuck_counter += 1
            if self.stuck_counter > 20:
                self._handle_stuck()

    def _get_game_state(self) -> str:
        """Determine current game state"""
        interior = getattr(self.game, 'current_interior', None)

        if interior and hasattr(interior, 'active') and interior.active:
            # Check for active dialogue
            if hasattr(interior, 'dialogue_box') and interior.dialogue_box.active:
                return 'dialogue_active'

            # Check for active activity on interior
            if hasattr(interior, 'current_activity') and interior.current_activity:
                if getattr(interior.current_activity, 'active', False):
                    return 'activity_active'

            # Check objective manager's direct activity
            obj_manager = getattr(self.game, 'objective_manager', None)
            if obj_manager:
                # Check UAM (Universal Activity Manager)
                if hasattr(obj_manager, 'activity_manager'):
                    uam = obj_manager.activity_manager
                    if hasattr(uam, 'current_activity') and uam.current_activity:
                        if getattr(uam.current_activity, 'active', False):
                            return 'activity_active'

                # Check objective manager's own activity
                if hasattr(obj_manager, 'current_activity') and obj_manager.current_activity:
                    if getattr(obj_manager.current_activity, 'active', False):
                        return 'activity_active'

            return 'in_interior'

        return 'in_world'

    def _simulate_key(self, key):
        """Simulate a keypress"""
        # Create and post a KEYDOWN event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
        pygame.event.post(event)
        print(f"[AUTO] Pressed key: {pygame.key.name(key)}")

    def _is_player_moving(self) -> bool:
        """Check if player is animating movement"""
        player = getattr(self.game, 'player', None)
        if not player:
            return False
        return (abs(player.pixel_x - player.target_x) > 1 or
                abs(player.pixel_y - player.target_y) > 1)

    def _take_next_step(self):
        """Move one tile towards target - continuous walking"""
        if not self.path:
            return

        player = getattr(self.game, 'player', None)
        if not player:
            return

        next_tile = self.path.pop(0)
        player.move_to(next_tile[0], next_tile[1])
        # No cooldown - let the player's animation complete naturally
        # The _is_player_moving() check ensures we wait for each tile move

    def _calculate_path(self, start, end):
        """Calculate path from start to end - moves cardinal directions only for natural movement"""
        path = []
        current_x, current_y = int(start[0]), int(start[1])
        target_x, target_y = int(end[0]), int(end[1])

        while current_x != target_x or current_y != target_y:
            # Move horizontally first, then vertically (or alternate for more natural paths)
            # This makes movement look more like actual player WASD movement
            if current_x != target_x:
                if current_x < target_x:
                    current_x += 1
                else:
                    current_x -= 1
            elif current_y != target_y:
                if current_y < target_y:
                    current_y += 1
                else:
                    current_y -= 1

            path.append((current_x, current_y))

        return path

    def _auto_complete_activity(self) -> bool:
        """Auto-complete current activity"""
        # Check interior activity
        interior = getattr(self.game, 'current_interior', None)
        if interior and hasattr(interior, 'current_activity') and interior.current_activity:
            activity = interior.current_activity
            if getattr(activity, 'active', False):
                return self._complete_activity(activity)

        # Check objective manager
        obj_manager = getattr(self.game, 'objective_manager', None)
        if obj_manager:
            # Check UAM (Universal Activity Manager) first
            if hasattr(obj_manager, 'activity_manager'):
                uam = obj_manager.activity_manager
                if hasattr(uam, 'current_activity') and uam.current_activity:
                    if getattr(uam.current_activity, 'active', False):
                        return self._complete_activity(uam.current_activity)

            # Check objective manager's direct activity
            if hasattr(obj_manager, 'current_activity') and obj_manager.current_activity:
                activity = obj_manager.current_activity
                if getattr(activity, 'active', False):
                    return self._complete_activity(activity)

        return False

    def _complete_activity(self, activity) -> bool:
        """Call activity's completion method"""
        name = activity.__class__.__name__

        # Track repeated activity completions to detect loops
        if name == self.last_activity_name:
            self.activity_complete_count += 1
            if self.activity_complete_count > 3:
                print(f"[AUTO] ⚠️ Activity loop detected ({name}), forcing exit")
                activity.active = False
                self.activity_complete_count = 0
                # Force exit the interior
                interior = getattr(self.game, 'current_interior', None)
                if interior:
                    interior.active = False
                    self.game.current_interior = None
                return True
        else:
            self.last_activity_name = name
            self.activity_complete_count = 1

        # Try various completion methods
        methods = ['complete_packing', 'complete_search', 'complete_selection',
                   'complete_activity', 'complete_call', 'complete_calculation',
                   'complete_inspection', 'complete_checkin', 'complete_breakdown',
                   'complete_application', 'complete']

        for method_name in methods:
            if hasattr(activity, method_name):
                try:
                    getattr(activity, method_name)()
                    print(f"[AUTO] Completed {name} via {method_name}()")
                    return True
                except Exception as e:
                    print(f"[AUTO] Error in {method_name}: {e}")

        # Force deactivate
        activity.active = False
        print(f"[AUTO] Force-deactivated {name}")
        return True

    def _handle_interior(self) -> bool:
        """Handle actions while in an interior"""
        interior = getattr(self.game, 'current_interior', None)
        if not interior:
            return False

        # Check if there are uncompleted interactions
        if hasattr(interior, 'interactive_objects'):
            completed = getattr(interior, 'completed_interactions', set())
            items_packed = getattr(interior, 'items_packed', set())
            item_map = {'closet': 'clothes', 'desk': 'documents', 'nightstand': 'photo'}

            for name in interior.interactive_objects:
                if name in completed:
                    continue
                if name in item_map and item_map[name] in items_packed:
                    continue

                # Found an uncompleted interaction - press E
                self._simulate_key(pygame.K_e)
                return True

        # Check if we can exit (all done)
        if hasattr(interior, 'check_objective_complete'):
            if interior.check_objective_complete():
                # Press ESC to exit
                self._simulate_key(pygame.K_ESCAPE)
                print("[AUTO] All interactions complete, exiting interior")
                return True

        # Nothing to do - might need to wait
        return False

    def _handle_world(self) -> bool:
        """Handle actions in the world"""
        # Already have a path? Continue walking
        if self.path:
            return False

        # Check objective
        obj_manager = getattr(self.game, 'objective_manager', None)
        if not obj_manager:
            return False

        current = obj_manager.get_current_objective()
        if not current:
            return False

        # Track objective changes
        if current.id != self.last_objective_id:
            self.last_objective_id = current.id
            self.objectives_completed += 1
            elapsed = time.time() - self.start_time if self.start_time else 0
            print(f"\n[AUTO] 📍 Objective {self.objectives_completed}: {current.id}")
            print(f"       Time: {elapsed:.1f}s, Actions: {self.actions_taken}\n")

        # Get player and objective position
        player = getattr(self.game, 'player', None)
        if not player or not current.target_position:
            return False

        target_x, target_y = current.target_position
        distance = math.sqrt((target_x - player.x)**2 + (target_y - player.y)**2)

        # If we're not at the objective yet, move there first
        if distance > 2:
            self.path = self._calculate_path((player.x, player.y), (target_x, target_y))
            if self.path:
                print(f"[AUTO] 🚶 Moving to ({target_x}, {target_y}) - {len(self.path)} steps")
                return True

        # We're at the objective - check if there's a building to enter
        near_building = getattr(self.game, 'near_building_with_interior', None)
        if near_building:
            building_pos, building_name, room_name = near_building
            # Only enter if it's at or near the objective position
            bx, by = building_pos
            if abs(bx - target_x) <= 2 and abs(by - target_y) <= 2:
                if hasattr(self.game, 'building_manager'):
                    if self.game.building_manager.enter_building(building_pos, building_name, room_name):
                        print(f"[AUTO] 🏠 Entered {building_name}")
                        return True

        return False

    def _handle_stuck(self):
        """Handle being stuck"""
        print(f"[AUTO] ⚠️ Stuck! Trying emergency action")

        # Try ESC to close any modal
        self._simulate_key(pygame.K_ESCAPE)
        self.stuck_counter = 0

        # Force exit interior if stuck too long
        interior = getattr(self.game, 'current_interior', None)
        if interior:
            interior.active = False
            self.game.current_interior = None
            print("[AUTO] Force-exited interior")

    def toggle(self):
        """Toggle auto-play"""
        self.enabled = not self.enabled
        status = "ENABLED" if self.enabled else "DISABLED"
        print(f"\n[AUTO] Auto-play {status}\n")
        if not self.enabled:
            self.path = []

    def get_stats(self) -> dict:
        """Get statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'enabled': self.enabled,
            'actions_taken': self.actions_taken,
            'objectives_completed': self.objectives_completed,
            'elapsed_time': elapsed
        }

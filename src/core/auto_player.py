"""
Auto-Player - Automatically plays through the game for testing
Directly interacts with game objects for reliable automation
"""

import pygame
import time
import math


class AutoPlayer:
    """Automatically plays the game by directly calling game methods"""

    def __init__(self, game, speed: float = 1.0):
        self.game = game
        self.speed = speed  # Seconds between major actions
        self.enabled = False
        self.last_action_time = 0
        self.actions_taken = 0
        self.objectives_completed = 0
        self.start_time = None

        # World movement state
        self.path = []

        # Interior movement state
        self.interior_path = []
        self.interior_walking = False

        # Track state
        self.stuck_counter = 0
        self.last_objective_id = None
        self.last_state = None
        self.interior_idle_count = 0
        self.target_interaction = None
        self.last_interaction_time = 0

        # Activity state
        self.activity_action_count = 0
        self.last_activity_name = None

        # Dialogue state
        self.dialogue_wait_time = 0
        self.waiting_to_read = False

    def start_full_playthrough(self, from_part: int = 1):
        """Start a full automatic playthrough"""
        self.enabled = True
        self.start_time = time.time()
        self.actions_taken = 0
        self.objectives_completed = 0
        self.path = []

        print("\n" + "=" * 60)
        print("AUTO-PLAY STARTED")
        print(f"   Speed: {self.speed}x")
        print("   Press 'T' to toggle")
        print("=" * 60 + "\n")

    def update(self, dt: float):
        """Main update - called every frame"""
        if not self.enabled:
            return

        if self.start_time is None:
            self.start_time = time.time()

        # Get current state
        state = self._get_game_state()

        if state != self.last_state:
            print(f"[AUTO] State: {state}")
            self.last_state = state
            self.waiting_to_read = False

        action_taken = False

        if state == 'dialogue_active':
            action_taken = self._handle_dialogue()

        elif state == 'activity_active':
            action_taken = self._handle_activity()

        elif state == 'in_interior':
            action_taken = self._handle_interior()

        elif state == 'in_world':
            action_taken = self._handle_world()

        if action_taken:
            self.actions_taken += 1
            self.stuck_counter = 0
        else:
            self.stuck_counter += 1
            if self.stuck_counter > 100:
                self._handle_stuck()

    def _get_game_state(self) -> str:
        """Determine current game state"""
        interior = getattr(self.game, 'current_interior', None)

        if interior and getattr(interior, 'active', False):
            # Check for active dialogue
            if hasattr(interior, 'dialogue_box') and interior.dialogue_box.active:
                return 'dialogue_active'

            # Check for active activity
            activity = self._get_current_activity()
            if activity and getattr(activity, 'active', False):
                return 'activity_active'

            return 'in_interior'

        return 'in_world'

    def _get_current_activity(self):
        """Get the currently active activity from any source"""
        # Check interior's current_activity
        interior = getattr(self.game, 'current_interior', None)
        if interior and hasattr(interior, 'current_activity'):
            if interior.current_activity and getattr(interior.current_activity, 'active', False):
                return interior.current_activity

        # Check objective manager
        obj_manager = getattr(self.game, 'objective_manager', None)
        if obj_manager:
            # Check UAM
            if hasattr(obj_manager, 'activity_manager'):
                uam = obj_manager.activity_manager
                if hasattr(uam, 'current_activity') and uam.current_activity:
                    if getattr(uam.current_activity, 'active', False):
                        return uam.current_activity

            # Check direct activity
            if hasattr(obj_manager, 'current_activity') and obj_manager.current_activity:
                if getattr(obj_manager.current_activity, 'active', False):
                    return obj_manager.current_activity

        return None

    def _handle_dialogue(self) -> bool:
        """Handle dialogue - wait for typewriter then advance"""
        interior = getattr(self.game, 'current_interior', None)
        if not interior:
            return False

        dialogue_box = getattr(interior, 'dialogue_box', None)
        if not dialogue_box or not dialogue_box.active:
            return False

        # Check if typewriter is still animating
        text_length = len(dialogue_box.current_text) if dialogue_box.current_text else 0
        current_progress = int(dialogue_box.text_progress) if hasattr(dialogue_box, 'text_progress') else 0

        if current_progress < text_length:
            return True  # Actively waiting for typewriter

        # Typewriter done - wait for reading time
        if not self.waiting_to_read:
            word_count = text_length / 5
            read_time = max(0.3, min(word_count / 4, 2.0)) * self.speed
            self.dialogue_wait_time = time.time() + read_time
            self.waiting_to_read = True
            return True

        remaining = self.dialogue_wait_time - time.time()
        if remaining > 0:
            return True  # Still reading

        # Done reading - advance
        self.waiting_to_read = False

        # Try to advance dialogue through narrative interior
        if hasattr(interior, 'show_next_dialogue'):
            interior.show_next_dialogue()
            return True

        # Fallback: press space via event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
        pygame.event.post(event)
        return True

    def _handle_activity(self) -> bool:
        """Handle activity by directly calling its methods"""
        activity = self._get_current_activity()
        if not activity:
            return False

        name = activity.__class__.__name__

        # Rate limit
        current_time = time.time()
        if current_time - self.last_action_time < self.speed * 0.3:
            return True

        # Track for loop detection
        if name == self.last_activity_name:
            self.activity_action_count += 1
            if self.activity_action_count > 50:
                print(f"[AUTO] Activity loop in {name}, forcing complete")
                activity.active = False
                if hasattr(activity, 'completed'):
                    activity.completed = True
                return True
        else:
            self.last_activity_name = name
            self.activity_action_count = 0

        self.last_action_time = current_time

        # Handle specific activity types
        if name == 'PackingGame':
            return self._play_packing_game(activity)
        elif name == 'FacebookSearch':
            return self._play_facebook_search(activity)
        elif name == 'FosterParentCall':
            return self._play_phone_call(activity)
        else:
            return self._play_generic_activity(activity, name)

    def _play_packing_game(self, activity) -> bool:
        """Play packing game by directly manipulating items - with smooth timing"""
        # Track if we already completed this activity
        if getattr(activity, '_auto_completed', False):
            return True

        # Check for continue button first
        if activity.continue_button_rect:
            activity._auto_completed = True
            activity.complete_packing()
            print("[AUTO] Completed packing game")
            return True

        # Get target zone based on mode
        if activity.mode == 'unpack':
            target_rect = activity.room_rect
            need_to_move = [item for item in activity.items if item['packed']]
        else:
            target_rect = activity.bag_rect
            need_to_move = [item for item in activity.items
                           if not item['packed'] and item['name'] != 'Small Plant']

        if not need_to_move:
            # All items moved, wait for continue button
            return True

        if not target_rect:
            return True

        # Rate limit: only move one item per second for natural feel
        current_time = time.time()
        if current_time - self.last_action_time < 1.0 * self.speed:
            return True

        self.last_action_time = current_time

        # Move an item
        item = need_to_move[0]
        target_pos = (target_rect.centerx, target_rect.centery)

        # Directly update item state (simulates completed drag)
        item['packed'] = not item['packed']
        item['pos'] = [target_pos[0], target_pos[1]]

        # Show memory message
        if hasattr(activity, 'show_memory'):
            activity.show_memory(item, target_pos)

        print(f"[AUTO] Moved {item['name']} in packing game")
        return True

    def _play_facebook_search(self, activity) -> bool:
        """Play Facebook search by directly updating state"""
        # If Alex contacted and continue button exists, click it
        if activity.alex_contacted and activity.continue_button_rect:
            activity.complete_search()
            print("[AUTO] Completed Facebook search")
            return True

        # If not contacted Alex yet, contact them
        if not activity.alex_contacted:
            activity.alex_contacted = True
            activity.notification_message = "Message sent to Alex Chen!"
            activity.notification_timer = 2.0
            print("[AUTO] Contacted Alex in Facebook search")
            return True

        # Wait for continue button to appear
        return True

    def _play_phone_call(self, activity) -> bool:
        """Play phone call activity"""
        # Check for complete method
        if hasattr(activity, 'complete_call'):
            activity.complete_call()
            print("[AUTO] Completed phone call")
            return True

        if hasattr(activity, 'complete'):
            activity.complete()
            return True

        # Force complete
        activity.active = False
        if hasattr(activity, 'completed'):
            activity.completed = True
        return True

    def _play_generic_activity(self, activity, name) -> bool:
        """Generic activity handler"""
        # Try various completion methods
        for method in ['complete', 'complete_activity', 'complete_search',
                       'complete_packing', 'complete_call', 'finish']:
            if hasattr(activity, method):
                try:
                    getattr(activity, method)()
                    print(f"[AUTO] Completed {name} via {method}()")
                    return True
                except:
                    pass

        # Force deactivate
        activity.active = False
        if hasattr(activity, 'completed'):
            activity.completed = True
        print(f"[AUTO] Force-completed {name}")
        return True

    def _handle_interior(self) -> bool:
        """Handle interior - walk to objectives and interact"""
        interior = getattr(self.game, 'current_interior', None)
        if not interior:
            return False

        current_time = time.time()

        # Continue walking if in progress
        if self.interior_walking:
            return self._continue_interior_walk(interior)

        # Rate limit actions
        if current_time - self.last_action_time < self.speed * 0.3:
            return True

        # Check if activity-based objective is already complete
        obj_manager = getattr(self.game, 'objective_manager', None)
        if obj_manager:
            current = obj_manager.get_current_objective()
            if current:
                # Skip if packing is already complete
                if current.id == 'pack_again' and getattr(interior, 'packing_complete', False):
                    print(f"[AUTO] pack_again objective complete, waiting for exit")
                    return True
                if current.id == 'move_in_alex' and getattr(interior, 'possessions_unpacked', False):
                    print(f"[AUTO] move_in_alex objective complete, waiting for exit")
                    return True

        # Check for interactions to complete
        if hasattr(interior, 'interactive_objects'):
            completed = getattr(interior, 'completed_interactions', set())

            for name, obj in interior.interactive_objects.items():
                if name in completed:
                    continue

                # Skip recently attempted interactions
                if name == self.target_interaction and current_time - self.last_interaction_time < 2.0:
                    return True

                # Get object position
                obj_x = obj.get('x', 8)
                obj_y = obj.get('y', 8)

                # Get player position (from pixel, like the game does)
                TILE_SIZE = getattr(interior, 'TILE_SIZE', 48)
                player_x = int(getattr(interior, 'player_pixel_x', 0) // TILE_SIZE)
                player_y = int(getattr(interior, 'player_pixel_y', 0) // TILE_SIZE)

                # Check distance - game uses abs(x) <= 1 AND abs(y) <= 1
                close_x = abs(player_x - obj_x) <= 1
                close_y = abs(player_y - obj_y) <= 1

                if close_x and close_y:
                    # Close enough - interact directly
                    self.target_interaction = name
                    self.last_interaction_time = current_time
                    self.last_action_time = current_time

                    # Call interact_with_object directly
                    if hasattr(interior, 'interact_with_object'):
                        interior.interact_with_object(name)
                        print(f"[AUTO] Interacted with {name}")
                        return True

                    # Fallback: send E keypress
                    event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_e})
                    pygame.event.post(event)
                    print(f"[AUTO] Pressed E for {name}")
                    return True
                else:
                    # Walk to tile adjacent to object
                    target_x = obj_x
                    target_y = obj_y + 1  # Stand below the object
                    self._start_interior_walk(interior, target_x, target_y)
                    print(f"[AUTO] Walking to {name} at ({target_x}, {target_y})")
                    return True

        # Check if should exit
        if hasattr(interior, 'should_exit') and interior.should_exit:
            interior.active = False
            self.game.current_interior = None
            print("[AUTO] Exiting interior")
            return True

        # Check if objective changed to different location
        obj_manager = getattr(self.game, 'objective_manager', None)
        if obj_manager:
            current = obj_manager.get_current_objective()
            if current and current.id != self.last_objective_id:
                building_pos = getattr(interior, 'building_pos', None)
                new_target = current.target_position

                if building_pos and new_target:
                    if building_pos[0] == new_target[0] and building_pos[1] == new_target[1]:
                        # Same location - stay and trigger new narrative
                        self.last_objective_id = current.id
                        if hasattr(interior, 'check_narrative_on_entry'):
                            interior.check_narrative_on_entry()
                        print(f"[AUTO] New objective {current.id} at same location")
                        return True
                    else:
                        # Different location - exit
                        interior.active = False
                        self.game.current_interior = None
                        print(f"[AUTO] Exiting for new objective {current.id}")
                        return True

        # Track idle time
        self.interior_idle_count += 1
        if self.interior_idle_count > 50:
            # Force progress
            if obj_manager:
                current = obj_manager.get_current_objective()
                if current and not current.completed:
                    current.complete()
                obj_manager.complete_current_objective()
            interior.active = False
            self.game.current_interior = None
            self.interior_idle_count = 0
            print("[AUTO] Forced interior exit")
            return True

        return True

    def _start_interior_walk(self, interior, target_x, target_y):
        """Start walking in interior - sets target tile"""
        TILE_SIZE = getattr(interior, 'TILE_SIZE', 48)
        self.interior_target = (target_x * TILE_SIZE, target_y * TILE_SIZE)
        self.interior_walking = True

    def _continue_interior_walk(self, interior) -> bool:
        """Move player toward target in interior (direct pixel movement)"""
        if not hasattr(self, 'interior_target') or not self.interior_target:
            self.interior_walking = False
            return False

        TILE_SIZE = getattr(interior, 'TILE_SIZE', 48)
        move_speed = getattr(interior, 'move_speed', 4)

        # Current position
        px = getattr(interior, 'player_pixel_x', 0)
        py = getattr(interior, 'player_pixel_y', 0)
        tx, ty = self.interior_target

        # Check if arrived
        if abs(px - tx) < move_speed and abs(py - ty) < move_speed:
            interior.player_pixel_x = float(tx)
            interior.player_pixel_y = float(ty)
            interior.player_tile_x = int(tx / TILE_SIZE)
            interior.player_tile_y = int(ty / TILE_SIZE)
            interior.player_walking = False
            self.interior_walking = False
            self.interior_target = None
            return False

        # Move toward target
        dx = 0
        dy = 0

        if abs(px - tx) > 1:
            dx = move_speed if px < tx else -move_speed
            interior.player_direction = 'right' if dx > 0 else 'left'
        elif abs(py - ty) > 1:
            dy = move_speed if py < ty else -move_speed
            interior.player_direction = 'down' if dy > 0 else 'up'

        if dx != 0 or dy != 0:
            interior.player_pixel_x = px + dx
            interior.player_pixel_y = py + dy
            interior.player_tile_x = int(interior.player_pixel_x / TILE_SIZE)
            interior.player_tile_y = int(interior.player_pixel_y / TILE_SIZE)
            interior.player_walking = True

        return True

    def _handle_world(self) -> bool:
        """Handle world navigation"""
        # Continue walking if path exists
        if self.path:
            return self._continue_world_walk()

        # Get current objective
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
            print(f"       Time: {elapsed:.1f}s\n")
            self.interior_idle_count = 0

        # Get positions
        player = getattr(self.game, 'player', None)
        if not player or not current.target_position:
            return False

        target_x, target_y = current.target_position
        dist = abs(target_x - player.x) + abs(target_y - player.y)

        # If not at objective, walk there
        if dist > 2:
            self._calculate_world_path(player.x, player.y, target_x, target_y)
            if self.path:
                print(f"[AUTO] 🚶 Walking to ({target_x}, {target_y})")
                return True

        # At objective - try to enter building
        # First check near_building_with_interior from game state
        near_building = getattr(self.game, 'near_building_with_interior', None)
        if near_building:
            building_pos, building_name, room_name = near_building
            bx, by = building_pos
            if abs(bx - target_x) <= 2 and abs(by - target_y) <= 2:
                if hasattr(self.game, 'building_manager'):
                    if self.game.building_manager.enter_building(building_pos, building_name, room_name):
                        print(f"[AUTO] 🏠 Entered {building_name}")
                        return True

        # Fallback: try to find and enter building at player position
        if hasattr(self.game, 'building_manager'):
            px, py = player.x, player.y
            # Check if there's a building near current location (range_tiles=2)
            try:
                result = self.game.building_manager.check_player_near_building(px, py, 2)
                if result and result[0]:
                    building_pos, building_name, room_name = result
                    if self.game.building_manager.enter_building(building_pos, building_name, room_name):
                        print(f"[AUTO] 🏠 Entered {building_name} (fallback)")
                        return True
            except Exception as e:
                print(f"[AUTO] Building check error: {e}")

        return False

    def _calculate_world_path(self, start_x, start_y, end_x, end_y):
        """Calculate path for world movement"""
        self.path = []
        cx, cy = int(start_x), int(start_y)
        tx, ty = int(end_x), int(end_y)

        while cx != tx or cy != ty:
            if cx != tx:
                cx += 1 if cx < tx else -1
            elif cy != ty:
                cy += 1 if cy < ty else -1
            self.path.append((cx, cy))

    def _continue_world_walk(self) -> bool:
        """Continue walking in world"""
        player = getattr(self.game, 'player', None)
        if not player:
            self.path = []
            return False

        # Check if player is still moving
        if abs(player.pixel_x - player.target_x) > 1 or abs(player.pixel_y - player.target_y) > 1:
            return True

        # Take next step
        if not self.path:
            return False

        next_tile = self.path.pop(0)
        player.move_to(next_tile[0], next_tile[1])
        return True

    def _handle_stuck(self):
        """Handle being stuck"""
        print("[AUTO] ⚠️ Stuck - forcing progress")
        self.stuck_counter = 0

        interior = getattr(self.game, 'current_interior', None)
        if interior:
            interior.active = False
            self.game.current_interior = None

        obj_manager = getattr(self.game, 'objective_manager', None)
        if obj_manager:
            current = obj_manager.get_current_objective()
            if current and not current.completed:
                current.complete()
            obj_manager.complete_current_objective()

        self.path = []
        self.interior_path = []
        self.interior_walking = False

    def toggle(self):
        """Toggle auto-play"""
        self.enabled = not self.enabled
        status = "ENABLED" if self.enabled else "DISABLED"
        print(f"\n[AUTO] Auto-play {status}\n")
        if not self.enabled:
            self.path = []
            self.interior_path = []

    def get_stats(self) -> dict:
        """Get statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'enabled': self.enabled,
            'actions': self.actions_taken,
            'objectives': self.objectives_completed,
            'time': elapsed
        }

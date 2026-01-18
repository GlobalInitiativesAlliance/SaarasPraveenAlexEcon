"""
Centralized Input Management System
Handles all pygame events in one place to prevent double-processing and missed inputs.
"""

import pygame
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from collections import deque
from dataclasses import dataclass, field


@dataclass
class FrameState:
    """
    Cached game state for the current frame.

    This eliminates redundant hasattr() and state checks by
    caching commonly-queried state once per frame.

    Usage:
        frame_state = FrameState.from_game(game)
        if frame_state.has_active_activity:
            # Handle activity...
    """
    # Interior state
    has_active_interior: bool = False
    interior_name: str = ""

    # Activity state
    has_active_activity: bool = False
    activity_name: str = ""
    activity_completed: bool = False

    # Dialogue state
    is_dialogue_active: bool = False

    # UI state
    is_debug_menu_visible: bool = False
    is_debug_panel_visible: bool = False

    # Player state
    player_near_objective: bool = False
    near_building: Optional[Tuple] = None

    # Transition state
    is_transition_active: bool = False

    @classmethod
    def from_game(cls, game: Any) -> 'FrameState':
        """
        Create a FrameState from the current game state.

        Args:
            game: The Game instance to extract state from

        Returns:
            FrameState with all relevant state cached
        """
        state = cls()

        # Interior state
        if hasattr(game, 'current_interior') and game.current_interior is not None:
            state.has_active_interior = True
            state.interior_name = type(game.current_interior).__name__

        # Activity state - check objective_manager first
        if hasattr(game, 'objective_manager'):
            om = game.objective_manager
            current_activity = getattr(om, 'current_activity', None)
            if current_activity is not None:
                if hasattr(current_activity, 'active') and current_activity.active:
                    state.has_active_activity = True
                    state.activity_name = type(current_activity).__name__
                    state.activity_completed = getattr(current_activity, 'completed', False)

        # Also check interior's current_activity
        if not state.has_active_activity and state.has_active_interior:
            interior = game.current_interior
            interior_activity = getattr(interior, 'current_activity', None)
            if interior_activity is not None:
                if hasattr(interior_activity, 'active') and interior_activity.active:
                    state.has_active_activity = True
                    state.activity_name = type(interior_activity).__name__
                    state.activity_completed = getattr(interior_activity, 'completed', False)

        # Dialogue state
        if state.has_active_interior:
            interior = game.current_interior
            if hasattr(interior, 'dialogue_box'):
                state.is_dialogue_active = getattr(interior.dialogue_box, 'active', False)

        # UI state
        if hasattr(game, 'debug_menu'):
            state.is_debug_menu_visible = getattr(game.debug_menu, 'visible', False)
        if hasattr(game, 'debug_panel'):
            state.is_debug_panel_visible = getattr(game.debug_panel, 'visible', False)

        # Player/objective state
        if hasattr(game, 'player_near_objective'):
            state.player_near_objective = game.player_near_objective
        if hasattr(game, 'near_building_with_interior'):
            state.near_building = game.near_building_with_interior

        # Transition state
        if hasattr(game, 'transition_manager'):
            tm = game.transition_manager
            state.is_transition_active = getattr(tm, 'is_active', False)

        return state

    def is_activity_blocking_input(self) -> bool:
        """Check if an activity should block normal input handling"""
        return self.has_active_activity and not self.activity_completed

    def should_route_to_interior(self) -> bool:
        """Check if events should be routed to interior"""
        return self.has_active_interior

    def should_route_to_activity(self) -> bool:
        """Check if events should be routed to activity"""
        return self.has_active_activity and not self.activity_completed


class InputEvent:
    """Wrapper for pygame events with timing information and propagation control"""
    def __init__(self, pygame_event: pygame.event.Event):
        self.event = pygame_event
        self.timestamp = time.time()
        self.processed = False
        self.propagation_stopped = False

    def reset(self, pygame_event: pygame.event.Event):
        """Reset this InputEvent for reuse (object pooling)"""
        self.event = pygame_event
        self.timestamp = time.time()
        self.processed = False
        self.propagation_stopped = False

    def __getattr__(self, name):
        """Delegate attribute access to the pygame event"""
        return getattr(self.event, name)

    def stop_propagation(self) -> None:
        """Mark event as consumed - no further handlers should process it"""
        self.propagation_stopped = True

    def is_consumed(self) -> bool:
        """Check if event has been consumed (processed or propagation stopped)"""
        return self.propagation_stopped or self.processed


class InputEventPool:
    """Object pool for InputEvent instances to reduce allocation overhead"""

    def __init__(self, initial_size: int = 50):
        """
        Initialize the event pool.

        Args:
            initial_size: Initial pool size (pre-allocated objects)
        """
        self.available = []
        self.active = []

        # Pre-allocate pool objects (use dummy event for initialization)
        dummy_event = pygame.event.Event(pygame.NOEVENT)
        for _ in range(initial_size):
            self.available.append(InputEvent(dummy_event))

    def acquire(self, pygame_event: pygame.event.Event) -> InputEvent:
        """
        Get an InputEvent from the pool or create new one if empty.

        Args:
            pygame_event: Pygame event to wrap

        Returns:
            InputEvent instance
        """
        if self.available:
            # Reuse from pool
            event = self.available.pop()
            event.reset(pygame_event)
        else:
            # Pool exhausted, create new (will be returned to pool later)
            event = InputEvent(pygame_event)

        self.active.append(event)
        return event

    def release_all(self):
        """Return all active events to the pool (call after frame processing)"""
        self.available.extend(self.active)
        self.active.clear()

    def get_stats(self) -> dict:
        """Get pool statistics"""
        return {
            'available': len(self.available),
            'active': len(self.active),
            'total_size': len(self.available) + len(self.active)
        }


class InputBuffer:
    """Buffered input system to prevent missed keypresses"""
    def __init__(self, buffer_time: float = 0.2):
        self.buffer_time = buffer_time  # Time to keep events in buffer
        self.key_buffer: deque = deque(maxlen=10)  # Recent keydown events
        self.mouse_buffer: deque = deque(maxlen=5)  # Recent mouse events

    def add_key_event(self, event: InputEvent) -> None:
        """Add a key event to the buffer"""
        if event.type == pygame.KEYDOWN:
            self.key_buffer.append(event)
            self._cleanup_old_events()

    def add_mouse_event(self, event: InputEvent) -> None:
        """Add a mouse event to the buffer"""
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            self.mouse_buffer.append(event)
            self._cleanup_old_events()

    def _cleanup_old_events(self) -> None:
        """Remove events older than buffer_time"""
        current_time = time.time()

        # Clean key buffer
        while (self.key_buffer and
               current_time - self.key_buffer[0].timestamp > self.buffer_time):
            self.key_buffer.popleft()

        # Clean mouse buffer
        while (self.mouse_buffer and
               current_time - self.mouse_buffer[0].timestamp > self.buffer_time):
            self.mouse_buffer.popleft()

    def get_unprocessed_key_events(self) -> List[InputEvent]:
        """Get unprocessed key events from buffer"""
        unprocessed = []
        for event in self.key_buffer:
            if not event.processed:
                unprocessed.append(event)
        return unprocessed

    def get_recent_key(self, key: int) -> Optional[InputEvent]:
        """Check if a specific key was recently pressed (and not processed)"""
        for event in reversed(self.key_buffer):
            if (event.event.key == key and
                not event.processed and
                time.time() - event.timestamp <= self.buffer_time):
                return event
        return None

    def mark_processed(self, event: InputEvent) -> None:
        """Mark an event as processed"""
        event.processed = True


class InputManager:
    """Centralized input management for the entire game"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.input_buffer = InputBuffer()
        self.raw_events: List[InputEvent] = []
        self.frame_events: List[InputEvent] = []

        # Object pool for InputEvent instances (reduces allocation overhead)
        self.event_pool = InputEventPool(initial_size=50)

        # Event handlers by state
        self.state_handlers: Dict[str, List[Callable]] = {}

        # Mouse motion coalescing - only keep latest motion event per frame
        self.coalesce_mouse_motion = True

        # Centralized debouncing configuration
        self.debounce_enabled = True
        self.debounce_intervals: Dict[int, float] = {
            pygame.KEYDOWN: 0.15,      # 150ms for key presses
            pygame.MOUSEBUTTONDOWN: 0.1,  # 100ms for mouse clicks
        }
        # Track last event times: (event_type, key_or_button) -> timestamp
        self.last_event_times: Dict[tuple, float] = {}

        # Input statistics for debugging
        self.stats = {
            'events_this_frame': 0,
            'events_dropped': 0,
            'events_buffered': 0,
            'events_coalesced': 0,
            'events_debounced': 0,
            'last_frame_time': 0,
            'input_lag_warnings': 0
        }

        # Performance monitoring
        self.last_event_process_time = 0
        self.event_process_times: deque = deque(maxlen=60)  # Last 60 frames

    def register_handler(self, state: str, handler: Callable) -> None:
        """Register an event handler for a specific game state"""
        if state not in self.state_handlers:
            self.state_handlers[state] = []
        self.state_handlers[state].append(handler)

    def unregister_handler(self, state: str, handler: Callable) -> None:
        """Unregister an event handler"""
        if state in self.state_handlers and handler in self.state_handlers[state]:
            self.state_handlers[state].remove(handler)

    def should_debounce(self, event_type: int, key_or_button: int = 0) -> bool:
        """
        Check if an event should be debounced (blocked due to recent same event).

        Args:
            event_type: The pygame event type (KEYDOWN, MOUSEBUTTONDOWN, etc.)
            key_or_button: The key code or mouse button number

        Returns:
            True if event should be blocked (too soon), False if event should pass
        """
        if not self.debounce_enabled:
            return False

        if event_type not in self.debounce_intervals:
            return False

        event_key = (event_type, key_or_button)
        current_time = time.time()
        interval = self.debounce_intervals[event_type]

        if event_key in self.last_event_times:
            elapsed = current_time - self.last_event_times[event_key]
            if elapsed < interval:
                if self.debug_mode:
                    print(f"[DEBOUNCE] Blocked {pygame.event.event_name(event_type)} "
                          f"key={key_or_button} (elapsed: {elapsed:.3f}s < {interval}s)")
                return True

        # Record this event time
        self.last_event_times[event_key] = current_time
        return False

    def set_debounce_interval(self, event_type: int, interval: float) -> None:
        """Set custom debounce interval for an event type"""
        self.debounce_intervals[event_type] = interval

    def clear_debounce_history(self) -> None:
        """Clear debounce timing history - useful during state transitions"""
        self.last_event_times.clear()

    def process_frame(self, current_state: str) -> List[InputEvent]:
        """Process all events for this frame - call once per frame"""
        start_time = time.time()

        # Return previous frame's events to pool (object pooling optimization)
        self.event_pool.release_all()

        # Get all pygame events (single call)
        pygame_events = pygame.event.get()

        # Convert to InputEvent objects with timing
        self.frame_events = []
        pending_mouse_motion: Optional[InputEvent] = None
        motion_coalesced_count = 0
        debounced_count = 0

        for pygame_event in pygame_events:
            # Get InputEvent from pool instead of creating new (reduces allocation overhead)
            input_event = self.event_pool.acquire(pygame_event)

            # Apply debouncing for key and mouse button events
            if pygame_event.type == pygame.KEYDOWN:
                if self.should_debounce(pygame_event.type, pygame_event.key):
                    input_event.processed = True  # Mark as already processed
                    debounced_count += 1
            elif pygame_event.type == pygame.MOUSEBUTTONDOWN:
                if self.should_debounce(pygame_event.type, pygame_event.button):
                    input_event.processed = True
                    debounced_count += 1

            # Coalesce mouse motion events - keep only the latest
            if self.coalesce_mouse_motion and pygame_event.type == pygame.MOUSEMOTION:
                if pending_mouse_motion is not None:
                    motion_coalesced_count += 1
                pending_mouse_motion = input_event
            else:
                # Flush pending motion before other events (preserves event order)
                if pending_mouse_motion is not None:
                    self.frame_events.append(pending_mouse_motion)
                    self.input_buffer.add_mouse_event(pending_mouse_motion)
                    pending_mouse_motion = None

                self.frame_events.append(input_event)

                # Add to appropriate buffers
                if pygame_event.type == pygame.KEYDOWN:
                    self.input_buffer.add_key_event(input_event)
                elif pygame_event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    self.input_buffer.add_mouse_event(input_event)

        # Don't forget final pending motion event
        if pending_mouse_motion is not None:
            self.frame_events.append(pending_mouse_motion)
            self.input_buffer.add_mouse_event(pending_mouse_motion)

        # Update statistics
        self.stats['events_this_frame'] = len(self.frame_events)
        self.stats['events_coalesced'] = motion_coalesced_count
        self.stats['events_debounced'] = debounced_count
        self.stats['events_buffered'] = len(self.input_buffer.key_buffer) + len(self.input_buffer.mouse_buffer)

        # Performance tracking
        process_time = time.time() - start_time
        self.event_process_times.append(process_time)

        if process_time > 0.005:  # 5ms threshold
            self.stats['input_lag_warnings'] += 1
            if self.debug_mode:
                print(f"⚠️  Input processing lag: {process_time*1000:.2f}ms")

        if self.debug_mode and self.frame_events:
            self._log_debug_info()

        return self.frame_events

    def get_events_for_state(self, state: str) -> List[InputEvent]:
        """Get events that should be processed by a specific state"""
        return self.frame_events.copy()

    def check_recent_key(self, key: int, max_age: float = 0.2) -> Optional[InputEvent]:
        """Check if a key was pressed recently (within max_age seconds)"""
        return self.input_buffer.get_recent_key(key)

    def mark_event_processed(self, event: InputEvent) -> None:
        """Mark an event as processed to prevent re-processing"""
        self.input_buffer.mark_processed(event)

    def clear_buffer(self) -> None:
        """Clear the input buffer and debounce history - useful during state transitions"""
        self.input_buffer.key_buffer.clear()
        self.input_buffer.mouse_buffer.clear()
        self.last_event_times.clear()  # Also clear debounce history
        if self.debug_mode:
            print("🧹 Input buffer and debounce history cleared")

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about input processing"""
        avg_process_time = 0
        if self.event_process_times:
            avg_process_time = sum(self.event_process_times) / len(self.event_process_times)

        return {
            'events_this_frame': self.stats['events_this_frame'],
            'buffered_events': self.stats['events_buffered'],
            'dropped_events': self.stats['events_dropped'],
            'coalesced_events': self.stats['events_coalesced'],
            'debounced_events': self.stats['events_debounced'],
            'avg_process_time_ms': avg_process_time * 1000,
            'input_lag_warnings': self.stats['input_lag_warnings'],
            'key_buffer_size': len(self.input_buffer.key_buffer),
            'mouse_buffer_size': len(self.input_buffer.mouse_buffer)
        }

    def _log_debug_info(self) -> None:
        """Log debug information about input events"""
        event_types = {}
        for event in self.frame_events:
            event_type = pygame.event.event_name(event.type)
            event_types[event_type] = event_types.get(event_type, 0) + 1

        if event_types:
            type_list = ', '.join([f"{t}:{c}" for t, c in event_types.items()])
            print(f"🎮 Input events: {type_list}")

    def is_key_held(self, key: int) -> bool:
        """Check if a key is currently being held down"""
        keys = pygame.key.get_pressed()
        return keys[key]

    def get_mouse_pos(self) -> tuple:
        """Get current mouse position"""
        return pygame.mouse.get_pos()

    def reset_stats(self) -> None:
        """Reset input statistics"""
        self.stats = {
            'events_this_frame': 0,
            'events_dropped': 0,
            'events_buffered': 0,
            'events_coalesced': 0,
            'events_debounced': 0,
            'last_frame_time': 0,
            'input_lag_warnings': 0
        }
        self.event_process_times.clear()
        self.last_event_times.clear()  # Also clear debounce history


# Global input manager instance
_global_input_manager = None

def get_input_manager() -> InputManager:
    """Get the global input manager instance"""
    global _global_input_manager
    if _global_input_manager is None:
        _global_input_manager = InputManager(debug_mode=False)
    return _global_input_manager

def initialize_input_manager(debug_mode: bool = False) -> InputManager:
    """Initialize the global input manager"""
    global _global_input_manager
    _global_input_manager = InputManager(debug_mode=debug_mode)
    return _global_input_manager

def cleanup_input_manager() -> None:
    """Cleanup the global input manager"""
    global _global_input_manager
    if _global_input_manager:
        _global_input_manager.clear_buffer()
        _global_input_manager = None


# Convenience functions for common operations
def process_input_frame(current_state: str) -> List[InputEvent]:
    """Process input for current frame"""
    return get_input_manager().process_frame(current_state)

def was_key_pressed(key: int, max_age: float = 0.2) -> bool:
    """Check if a key was recently pressed"""
    event = get_input_manager().check_recent_key(key, max_age)
    if event:
        get_input_manager().mark_event_processed(event)
        return True
    return False

def clear_input_buffer() -> None:
    """Clear input buffer during state transitions"""
    get_input_manager().clear_buffer()

def get_input_debug_info() -> Dict[str, Any]:
    """Get input system debug information"""
    return get_input_manager().get_debug_info()

# Export main classes and functions
__all__ = [
    'InputManager', 'InputEvent', 'InputBuffer', 'FrameState',
    'get_input_manager', 'initialize_input_manager', 'cleanup_input_manager',
    'process_input_frame', 'was_key_pressed', 'clear_input_buffer', 'get_input_debug_info'
]
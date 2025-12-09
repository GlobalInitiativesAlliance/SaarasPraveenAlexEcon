"""
Centralized Input Management System
Handles all pygame events in one place to prevent double-processing and missed inputs.
"""

import pygame
import time
from typing import List, Dict, Any, Optional, Callable
from collections import deque


class InputEvent:
    """Wrapper for pygame events with timing information"""
    def __init__(self, pygame_event: pygame.event.Event):
        self.event = pygame_event
        self.timestamp = time.time()
        self.processed = False

    def __getattr__(self, name):
        """Delegate attribute access to the pygame event"""
        return getattr(self.event, name)


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

        # Event handlers by state
        self.state_handlers: Dict[str, List[Callable]] = {}

        # Input statistics for debugging
        self.stats = {
            'events_this_frame': 0,
            'events_dropped': 0,
            'events_buffered': 0,
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

    def process_frame(self, current_state: str) -> List[InputEvent]:
        """Process all events for this frame - call once per frame"""
        start_time = time.time()

        # Get all pygame events (single call)
        pygame_events = pygame.event.get()

        # Convert to InputEvent objects with timing
        self.frame_events = []
        for pygame_event in pygame_events:
            input_event = InputEvent(pygame_event)
            self.frame_events.append(input_event)

            # Add to appropriate buffers
            if pygame_event.type == pygame.KEYDOWN:
                self.input_buffer.add_key_event(input_event)
            elif pygame_event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                self.input_buffer.add_mouse_event(input_event)

        # Update statistics
        self.stats['events_this_frame'] = len(self.frame_events)
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
        """Clear the input buffer - useful during state transitions"""
        self.input_buffer.key_buffer.clear()
        self.input_buffer.mouse_buffer.clear()
        if self.debug_mode:
            print("🧹 Input buffer cleared")

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about input processing"""
        avg_process_time = 0
        if self.event_process_times:
            avg_process_time = sum(self.event_process_times) / len(self.event_process_times)

        return {
            'events_this_frame': self.stats['events_this_frame'],
            'buffered_events': self.stats['events_buffered'],
            'dropped_events': self.stats['events_dropped'],
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
            'last_frame_time': 0,
            'input_lag_warnings': 0
        }
        self.event_process_times.clear()


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
    'InputManager', 'InputEvent', 'InputBuffer',
    'get_input_manager', 'initialize_input_manager', 'cleanup_input_manager',
    'process_input_frame', 'was_key_pressed', 'clear_input_buffer', 'get_input_debug_info'
]
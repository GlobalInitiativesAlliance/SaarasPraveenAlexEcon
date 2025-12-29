"""
Event Dispatcher System
Table-driven event routing to replace nested conditionals.
"""

import pygame
import time
from typing import Dict, Callable, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class DispatchResult:
    """Result of event dispatch"""
    handled: bool
    handler_name: str = ""
    stop_propagation: bool = False


class EventDispatcher:
    """
    Table-driven event routing system.

    Provides centralized event dispatch with:
    - Global handlers (always run: QUIT, F12 screenshot)
    - Priority handlers (checked first: debug menu, modal dialogs)
    - State-specific handlers (by game state)
    - Event consumption/propagation control

    Usage:
        dispatcher = EventDispatcher()

        # Register a global handler
        dispatcher.register_global(pygame.QUIT, handle_quit)

        # Register a priority handler (checked before state handlers)
        dispatcher.add_priority_handler(handle_debug_menu)

        # Register state-specific handler
        dispatcher.register_state_handler('playing', pygame.KEYDOWN, pygame.K_e, handle_interaction)

        # Dispatch events
        for event in frame_events:
            dispatcher.dispatch(event, game_state, context)
    """

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode

        # Global handlers: event_type -> handler
        # These run regardless of game state
        self.global_handlers: Dict[int, Callable] = {}

        # Priority handlers: list of (handler, name) tuples
        # These are checked before state-specific handlers
        self.priority_handlers: List[Tuple[Callable, str]] = []

        # State-specific handlers: state -> event_type -> key -> (handler, name)
        # Use key=-1 for "any key" handlers
        self.state_handlers: Dict[str, Dict[int, Dict[int, Tuple[Callable, str]]]] = {}

        # Event log for debugging
        self.event_log: List[Dict[str, Any]] = []
        self.max_log_size = 100

    def register_global(self, event_type: int, handler: Callable, name: str = "") -> None:
        """
        Register a handler that runs regardless of game state.

        Args:
            event_type: pygame event type (QUIT, KEYDOWN, etc.)
            handler: Function that takes (input_event, context) and returns bool
            name: Optional handler name for debugging
        """
        self.global_handlers[event_type] = (handler, name or handler.__name__)
        if self.debug_mode:
            print(f"[DISPATCHER] Registered global handler: {name or handler.__name__} for {pygame.event.event_name(event_type)}")

    def add_priority_handler(self, handler: Callable, name: str = "") -> None:
        """
        Add a priority handler that's checked before state handlers.
        Priority handlers can intercept events for modals, debug menus, etc.

        Args:
            handler: Function that takes (input_event, game_state, context) and returns bool
            name: Optional handler name for debugging
        """
        self.priority_handlers.append((handler, name or handler.__name__))
        if self.debug_mode:
            print(f"[DISPATCHER] Added priority handler: {name or handler.__name__}")

    def register_state_handler(
        self,
        state: str,
        event_type: int,
        key: Optional[int],
        handler: Callable,
        name: str = ""
    ) -> None:
        """
        Register a handler for specific state/event/key combination.

        Args:
            state: Game state (e.g., 'playing', 'menu')
            event_type: pygame event type (KEYDOWN, MOUSEBUTTONDOWN, etc.)
            key: Specific key code (e.g., pygame.K_e), or None for any key
            handler: Function that takes (input_event, context) and returns bool
            name: Optional handler name for debugging
        """
        if state not in self.state_handlers:
            self.state_handlers[state] = {}
        if event_type not in self.state_handlers[state]:
            self.state_handlers[state][event_type] = {}

        key_or_default = key if key is not None else -1
        self.state_handlers[state][event_type][key_or_default] = (handler, name or handler.__name__)

        if self.debug_mode:
            key_name = pygame.key.name(key) if key is not None else "any"
            print(f"[DISPATCHER] Registered state handler: {name or handler.__name__} "
                  f"for state={state}, type={pygame.event.event_name(event_type)}, key={key_name}")

    def dispatch(self, input_event: Any, game_state: str, context: Any) -> DispatchResult:
        """
        Dispatch an event through the handler chain.

        Args:
            input_event: InputEvent wrapper or pygame event
            game_state: Current game state
            context: Game context object (usually the Game instance)

        Returns:
            DispatchResult with handling info
        """
        # Check if already consumed
        if hasattr(input_event, 'is_consumed') and input_event.is_consumed():
            return DispatchResult(handled=True, handler_name="already_consumed", stop_propagation=True)

        # Get event type
        event = input_event.event if hasattr(input_event, 'event') else input_event
        event_type = event.type

        result = DispatchResult(handled=False)

        # 1. Global handlers (QUIT, etc.)
        if event_type in self.global_handlers:
            handler, name = self.global_handlers[event_type]
            try:
                if handler(input_event, context):
                    result = DispatchResult(handled=True, handler_name=name, stop_propagation=True)
                    self._log_event(input_event, game_state, result)
                    self._consume_event(input_event)
                    return result
            except Exception as e:
                if self.debug_mode:
                    print(f"[DISPATCHER] Error in global handler {name}: {e}")

        # 2. Priority handlers (debug menu, modals)
        for handler, name in self.priority_handlers:
            try:
                if handler(input_event, game_state, context):
                    result = DispatchResult(handled=True, handler_name=name, stop_propagation=True)
                    self._log_event(input_event, game_state, result)
                    self._consume_event(input_event)
                    return result
            except Exception as e:
                if self.debug_mode:
                    print(f"[DISPATCHER] Error in priority handler {name}: {e}")

        # 3. State-specific handlers
        if game_state in self.state_handlers:
            state_dispatch = self.state_handlers[game_state]
            if event_type in state_dispatch:
                type_dispatch = state_dispatch[event_type]

                # Get the key for this event
                key = -1
                if event_type == pygame.KEYDOWN or event_type == pygame.KEYUP:
                    key = getattr(event, 'key', -1)
                elif event_type == pygame.MOUSEBUTTONDOWN or event_type == pygame.MOUSEBUTTONUP:
                    key = getattr(event, 'button', -1)

                # Try specific key handler first
                if key in type_dispatch:
                    handler, name = type_dispatch[key]
                    try:
                        if handler(input_event, context):
                            result = DispatchResult(handled=True, handler_name=name, stop_propagation=True)
                            self._log_event(input_event, game_state, result)
                            self._consume_event(input_event)
                            return result
                    except Exception as e:
                        if self.debug_mode:
                            print(f"[DISPATCHER] Error in state handler {name}: {e}")

                # Try default handler (-1)
                if -1 in type_dispatch:
                    handler, name = type_dispatch[-1]
                    try:
                        if handler(input_event, context):
                            result = DispatchResult(handled=True, handler_name=name, stop_propagation=True)
                            self._log_event(input_event, game_state, result)
                            self._consume_event(input_event)
                            return result
                    except Exception as e:
                        if self.debug_mode:
                            print(f"[DISPATCHER] Error in default handler {name}: {e}")

        self._log_event(input_event, game_state, result)
        return result

    def dispatch_to_handler(self, input_event: Any, handler: Any) -> bool:
        """
        Dispatch event directly to an EventHandler instance.

        Args:
            input_event: InputEvent wrapper
            handler: Object implementing EventHandler interface

        Returns:
            True if handler consumed the event
        """
        if not hasattr(handler, 'handle_event'):
            return False

        # Check if handler wants this event
        if hasattr(handler, 'wants_event') and not handler.wants_event(input_event):
            return False

        # Check if handler is active
        if hasattr(handler, 'is_active') and not handler.is_active():
            return False

        try:
            if handler.handle_event(input_event):
                self._consume_event(input_event)
                return True
        except Exception as e:
            if self.debug_mode:
                print(f"[DISPATCHER] Error dispatching to handler {type(handler).__name__}: {e}")

        return False

    def _consume_event(self, input_event: Any) -> None:
        """Mark event as consumed"""
        if hasattr(input_event, 'stop_propagation'):
            input_event.stop_propagation()
        elif hasattr(input_event, 'propagation_stopped'):
            input_event.propagation_stopped = True

    def _log_event(self, input_event: Any, game_state: str, result: DispatchResult) -> None:
        """Log event for debugging"""
        if not self.debug_mode:
            return

        event = input_event.event if hasattr(input_event, 'event') else input_event

        log_entry = {
            'time': time.time(),
            'type': pygame.event.event_name(event.type),
            'state': game_state,
            'handled': result.handled,
            'handler': result.handler_name,
            'stopped': result.stop_propagation
        }

        self.event_log.append(log_entry)

        # Trim log if too large
        if len(self.event_log) > self.max_log_size:
            self.event_log = self.event_log[-self.max_log_size:]

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the dispatcher"""
        return {
            'global_handlers': len(self.global_handlers),
            'priority_handlers': len(self.priority_handlers),
            'state_handlers': {
                state: sum(len(keys) for keys in types.values())
                for state, types in self.state_handlers.items()
            },
            'recent_events': self.event_log[-10:] if self.event_log else []
        }

    def clear_handlers(self) -> None:
        """Clear all registered handlers"""
        self.global_handlers.clear()
        self.priority_handlers.clear()
        self.state_handlers.clear()
        self.event_log.clear()


# Convenience function to create a dispatcher with common handlers
def create_game_dispatcher(debug_mode: bool = False) -> EventDispatcher:
    """Create an EventDispatcher with common game handlers pre-registered"""
    dispatcher = EventDispatcher(debug_mode=debug_mode)

    # Register QUIT as a global handler
    def handle_quit(input_event, context):
        # Let the main loop handle quit by not returning True
        # This allows proper cleanup
        return False

    dispatcher.register_global(pygame.QUIT, handle_quit, "handle_quit")

    return dispatcher

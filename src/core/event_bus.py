"""
Event Bus - Centralized event routing with priority and consumption
Single source of truth for all game event routing.
"""
import pygame
from src.core.debug_logger import debug_logger


class EventBus:
    """
    Centralized event routing system with clear priority order.

    Priority levels:
    - PRIORITY_ACTIVITY (100): Active mini-games get events first
    - PRIORITY_INTERIOR (50): Room interiors
    - PRIORITY_GAME (10): Main game/UI fallback

    Events are routed in priority order. If a handler returns True,
    the event is considered "consumed" and won't propagate further.
    """

    PRIORITY_ACTIVITY = 100
    PRIORITY_INTERIOR = 50
    PRIORITY_GAME = 10

    def __init__(self, game):
        self.game = game
        self.debug_events = False  # Toggle with F3 debug panel
        self._recent_events = []  # For debug panel display
        self._max_recent = 8

    def get_active_activity(self):
        """
        Get the ONE authoritative active activity.
        Uses ObjectiveManager.current_activity as the single source of truth.
        """
        if hasattr(self.game, 'objective_manager'):
            activity = self.game.objective_manager.current_activity
            if activity and hasattr(activity, 'active') and activity.active:
                return activity
        return None

    def route_event(self, event):
        """
        Route event with priority and consumption.

        Args:
            event: pygame event object

        Returns:
            True if event was consumed, False otherwise
        """
        if self.debug_events:
            self._log_event_start(event)

        # Priority 1: Active activity (highest priority)
        activity = self.get_active_activity()
        if activity:
            consumed = self._dispatch_to_activity(activity, event)
            if consumed:
                self._record_event(event, type(activity).__name__, True)
                return True

        # Priority 2: Current interior
        if self.game.current_interior:
            consumed = self._dispatch_to_interior(self.game.current_interior, event)
            if consumed:
                self._record_event(event, type(self.game.current_interior).__name__, True)
                return True

        # Not consumed - let main.py handle at game level
        self._record_event(event, "game_level", False)
        return False

    def _dispatch_to_activity(self, activity, event):
        """
        Dispatch event to activity with normalized handler names.
        Adapts between different handler method naming conventions.

        Returns True if event was handled/consumed.
        """
        try:
            # Try unified handle_event first (preferred interface)
            if hasattr(activity, 'handle_event'):
                result = activity.handle_event(event)
                # handle_event returns True/False for consumption, or None
                if result is True:
                    return True
                elif result is False:
                    return False
                # If None, check specific handlers as fallback

            # Fallback to specific handlers based on event type
            if event.type == pygame.KEYDOWN:
                if hasattr(activity, 'handle_key'):
                    activity.handle_key(event.key)
                    return True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(activity, 'handle_mouse_click'):
                    activity.handle_mouse_click(event.pos, event.button)
                    return True
                elif hasattr(activity, 'handle_click'):
                    activity.handle_click(event.pos)
                    return True

            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(activity, 'handle_mouse_release'):
                    activity.handle_mouse_release(event.pos, event.button)
                    return True

            elif event.type == pygame.MOUSEMOTION:
                if hasattr(activity, 'handle_mouse_motion'):
                    activity.handle_mouse_motion(event.pos)
                    return True

            elif event.type == pygame.TEXTINPUT:
                if hasattr(activity, 'handle_text_input'):
                    activity.handle_text_input(event.text)
                    return True

        except Exception as e:
            debug_logger.error('EVENT', f"Error dispatching to activity: {e}")

        return False

    def _dispatch_to_interior(self, interior, event):
        """
        Dispatch event to interior.

        Returns True if event was handled/consumed.
        """
        try:
            if hasattr(interior, 'handle_event'):
                result = interior.handle_event(event)
                # Explicit True means consumed
                return result is True
        except Exception as e:
            debug_logger.error('EVENT', f"Error dispatching to interior: {e}")

        return False

    def _log_event_start(self, event):
        """Log event for debugging"""
        event_names = {
            pygame.KEYDOWN: 'KEYDOWN',
            pygame.KEYUP: 'KEYUP',
            pygame.MOUSEBUTTONDOWN: 'MOUSEDOWN',
            pygame.MOUSEBUTTONUP: 'MOUSEUP',
            pygame.MOUSEMOTION: 'MOUSEMOTION',
            pygame.TEXTINPUT: 'TEXTINPUT',
        }
        name = event_names.get(event.type, str(event.type))

        extra_info = ""
        if event.type == pygame.KEYDOWN:
            extra_info = f" key={event.key}"
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            extra_info = f" pos={event.pos} btn={event.button}"
        elif event.type == pygame.MOUSEMOTION:
            extra_info = f" pos={event.pos}"

        debug_logger.debug('EVENT', f"Routing: {name}{extra_info}")

    def _record_event(self, event, handler, consumed):
        """Record event for debug panel display"""
        import time

        event_names = {
            pygame.KEYDOWN: 'KEY',
            pygame.KEYUP: 'KEY_UP',
            pygame.MOUSEBUTTONDOWN: 'CLICK',
            pygame.MOUSEBUTTONUP: 'RELEASE',
            pygame.MOUSEMOTION: 'MOVE',
            pygame.TEXTINPUT: 'TEXT',
        }

        self._recent_events.append({
            'time': time.strftime('%H:%M:%S'),
            'type': event_names.get(event.type, '?'),
            'handler': handler[:20],  # Truncate long names
            'consumed': consumed
        })

        if len(self._recent_events) > self._max_recent:
            self._recent_events.pop(0)

    def get_recent_events(self):
        """Get recent events for debug panel"""
        return self._recent_events.copy()

    def clear_recent_events(self):
        """Clear recent events list"""
        self._recent_events.clear()

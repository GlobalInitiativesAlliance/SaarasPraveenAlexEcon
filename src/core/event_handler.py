"""
Event Handler Interface
Standardized interface for all event-handling game components.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.input_manager import InputEvent


class EventHandler(ABC):
    """
    Standard interface for all event-handling game components.

    Provides a consistent way to handle events across activities,
    interiors, menus, and other game components.
    """

    @abstractmethod
    def handle_event(self, input_event: 'InputEvent') -> bool:
        """
        Handle an input event.

        Args:
            input_event: The wrapped pygame event with metadata

        Returns:
            True if event was consumed (stop propagation), False otherwise
        """
        pass

    def wants_event(self, input_event: 'InputEvent') -> bool:
        """
        Check if this handler wants to process the given event.
        Override to filter events before handle_event is called.

        Args:
            input_event: The event to check

        Returns:
            True if handler should receive this event, False to skip
        """
        return True

    def is_active(self) -> bool:
        """
        Check if this handler is currently active and should receive events.
        Override to implement activation logic.

        Returns:
            True if handler is active, False otherwise
        """
        return True

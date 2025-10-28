"""Interior building implementations"""

# Old base_interior removed - using narrative system now
# from .base_interior import BaseInterior

from .narrative_interior import NarrativeInterior
from .generic_interior import GenericInterior

__all__ = ['NarrativeInterior', 'GenericInterior']

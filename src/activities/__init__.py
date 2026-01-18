"""Game activities - with lazy loading support"""

import os

# Check if lazy loading is enabled (set via environment variable)
LAZY_LOAD_ENABLED = os.getenv('LAZY_LOAD_ACTIVITIES', 'false').lower() == 'true'

if LAZY_LOAD_ENABLED:
    # Lazy loading mode - activities loaded on-demand
    from src.core.lazy_loader import get_activity_class

    print("[ACTIVITIES] Lazy loading enabled - activities will load on-demand")

    def __getattr__(name):
        """Lazy load activities when accessed"""
        activity_class = get_activity_class(name)
        if activity_class is not None:
            # Cache in module globals
            globals()[name] = activity_class
            return activity_class
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

else:
    # Eager loading mode (default) - load all activities at startup
    from .activities import *

    # Note: Individual activities are imported with * due to the large number of classes

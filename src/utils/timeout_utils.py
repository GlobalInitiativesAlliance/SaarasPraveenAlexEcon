"""
Timeout utilities for protecting operations from hanging.

NOTE: Threading is NOT supported in Pygbag/web builds. This module detects
the web environment and skips threading-based timeouts, calling functions
directly instead.
"""
import sys
from typing import TypeVar, Callable, Optional, Any

T = TypeVar('T')

# Detect if running in web/Pygbag environment
# In Pygbag, sys.platform is 'emscripten' and threading doesn't work
def _is_web_environment() -> bool:
    """Check if running in a web/Pygbag environment where threading doesn't work."""
    return sys.platform == 'emscripten' or hasattr(sys, '_emscripten_info')


def timeout_operation(timeout_seconds: float):
    """
    Decorator to add timeout protection to operations.

    Args:
        timeout_seconds: Maximum time to wait for the operation to complete.

    Returns:
        Decorated function that will return None if timeout is exceeded.

    NOTE: In web/Pygbag builds, threading is not available. The decorator
    will simply call the function directly without timeout protection.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        def wrapper(*args, **kwargs) -> Optional[T]:
            # Skip threading in web environment - just call directly
            if _is_web_environment():
                return func(*args, **kwargs)

            # Desktop environment - use threading for timeout
            import threading

            result: list = [None]
            exception: list = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                # Import here to avoid circular imports
                try:
                    from src.core.debug_logger import debug_logger
                    debug_logger.log_timeout(f"{func.__name__}", timeout_seconds)
                except ImportError:
                    print(f"[TIMEOUT] {func.__name__} exceeded {timeout_seconds}s")
                return None
            elif exception[0]:
                raise exception[0]
            else:
                return result[0]
        return wrapper
    return decorator

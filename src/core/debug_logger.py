"""
Debug Logger - Centralized debugging system for tracking room transitions and game state
"""
import time
from collections import deque
from datetime import datetime

# GLOBAL PERFORMANCE FLAG - Set to False to disable ALL debug output
# This significantly improves FPS by removing print overhead
DEBUG_VERBOSE = False


class DebugLogger:
    """Centralized debug logging system"""

    def __init__(self, max_entries=100):
        self.max_entries = max_entries
        self.entries = deque(maxlen=max_entries)
        self.room_history = deque(maxlen=20)
        self.error_count = 0
        self.last_error = None
        self.start_time = time.time()
        self.verbose = DEBUG_VERBOSE  # Instance flag
        self.performance_stats = {
            'room_loads': 0,
            'room_load_times': [],
            'average_load_time': 0,
            'failed_loads': 0
        }

    def log(self, level, category, message, **kwargs):
        """Add a debug entry with timestamp and context"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        entry = {
            'timestamp': timestamp,
            'level': level,  # DEBUG, INFO, WARNING, ERROR
            'category': category,  # ROOM, PLAYER, OBJECTIVE, ACTIVITY, etc.
            'message': message,
            'data': kwargs,
            'game_time': time.time() - self.start_time
        }

        self.entries.append(entry)

        # Track errors separately
        if level == 'ERROR':
            self.error_count += 1
            self.last_error = entry

        # Only print to console if verbose mode is enabled (performance optimization)
        if not self.verbose:
            return

        # Print to console with color coding
        color_codes = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'RESET': '\033[0m'      # Reset
        }

        color = color_codes.get(level, '')
        reset = color_codes['RESET']

        print(f"{color}[{timestamp}] {level:7} {category:12} {message}{reset}")
        if kwargs:
            for key, value in kwargs.items():
                print(f"{color}    {key}: {value}{reset}")

    def debug(self, category, message, **kwargs):
        """Log debug message"""
        self.log('DEBUG', category, message, **kwargs)

    def info(self, category, message, **kwargs):
        """Log info message"""
        self.log('INFO', category, message, **kwargs)

    def warning(self, category, message, **kwargs):
        """Log warning message"""
        self.log('WARNING', category, message, **kwargs)

    def error(self, category, message, **kwargs):
        """Log error message"""
        self.log('ERROR', category, message, **kwargs)

    def log_room_entry(self, room_name, building_pos, objective_id=None):
        """Log room entry attempt"""
        self.info('ROOM', f"Entering room: {room_name}",
                 building_pos=building_pos, objective=objective_id)
        self.room_history.append({
            'room': room_name,
            'pos': building_pos,
            'time': datetime.now().strftime("%H:%M:%S"),
            'objective': objective_id
        })

    def log_room_success(self, room_name, load_time=None):
        """Log successful room entry"""
        self.info('ROOM', f"Successfully entered: {room_name}")
        self.performance_stats['room_loads'] += 1

        if load_time:
            self.performance_stats['room_load_times'].append(load_time)
            # Keep only last 10 load times for average
            if len(self.performance_stats['room_load_times']) > 10:
                self.performance_stats['room_load_times'].pop(0)

            self.performance_stats['average_load_time'] = (
                sum(self.performance_stats['room_load_times']) /
                len(self.performance_stats['room_load_times'])
            )

    def log_room_failure(self, room_name, error_msg):
        """Log failed room entry"""
        self.error('ROOM', f"Failed to enter: {room_name}", error=error_msg)
        self.performance_stats['failed_loads'] += 1

    def log_timeout(self, operation, timeout_duration):
        """Log operation timeout"""
        self.error('TIMEOUT', f"Operation timed out: {operation}",
                  duration=f"{timeout_duration}s")

    def get_recent_entries(self, count=10, level=None):
        """Get recent debug entries, optionally filtered by level"""
        entries = list(self.entries)

        if level:
            entries = [e for e in entries if e['level'] == level]

        return entries[-count:]

    def get_room_history(self):
        """Get recent room entry history"""
        return list(self.room_history)

    def get_performance_summary(self):
        """Get performance statistics summary"""
        return {
            'total_room_loads': self.performance_stats['room_loads'],
            'failed_loads': self.performance_stats['failed_loads'],
            'success_rate': (
                (self.performance_stats['room_loads'] - self.performance_stats['failed_loads']) /
                max(1, self.performance_stats['room_loads']) * 100
            ),
            'average_load_time': self.performance_stats['average_load_time'],
            'total_errors': self.error_count,
            'uptime': time.time() - self.start_time
        }

    def clear(self):
        """Clear all debug entries"""
        self.entries.clear()
        self.room_history.clear()
        self.error_count = 0
        self.last_error = None

# Global debug logger instance
debug_logger = DebugLogger()


def dprint(*args, **kwargs):
    """Debug print - only prints if DEBUG_VERBOSE is True.

    Use this instead of print() for debug output that should be
    disabled in production for performance.
    """
    if DEBUG_VERBOSE:
        print(*args, **kwargs)
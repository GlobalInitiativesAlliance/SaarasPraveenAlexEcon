"""
Performance Monitor - Track frame timing and input lag issues
"""

import time
import pygame
from collections import deque
from typing import Dict, List, Any


class PerformanceMonitor:
    """Monitor game performance and identify input-related issues"""

    def __init__(self, sample_size: int = 120):  # 2 seconds at 60 FPS
        self.sample_size = sample_size

        # Frame timing data
        self.frame_times: deque = deque(maxlen=sample_size)
        self.frame_start_time = 0
        self.last_frame_time = time.time()

        # Performance statistics
        self.stats = {
            'avg_frame_time': 0.0,
            'min_frame_time': float('inf'),
            'max_frame_time': 0.0,
            'fps': 0.0,
            'frame_drops': 0,
            'input_lag_events': 0
        }

        # Performance thresholds (in milliseconds)
        self.target_frame_time = 1000.0 / 60.0  # 16.67ms for 60 FPS
        self.frame_drop_threshold = self.target_frame_time * 1.5  # 25ms
        self.input_lag_threshold = 5.0  # 5ms input processing time

        # Event tracking
        self.input_processing_times: deque = deque(maxlen=60)
        self.slow_frames: List[Dict] = []

    def frame_start(self):
        """Mark the start of a frame"""
        self.frame_start_time = time.time()

    def frame_end(self):
        """Mark the end of a frame and calculate timing"""
        current_time = time.time()
        frame_time_ms = (current_time - self.frame_start_time) * 1000.0

        # Store frame time
        self.frame_times.append(frame_time_ms)

        # Check for frame drops
        if frame_time_ms > self.frame_drop_threshold:
            self.stats['frame_drops'] += 1
            self.slow_frames.append({
                'time': current_time,
                'frame_time': frame_time_ms,
                'type': 'frame_drop'
            })

        # Update statistics
        self.update_stats()

        self.last_frame_time = current_time

    def record_input_processing_time(self, processing_time_ms: float):
        """Record input processing time"""
        self.input_processing_times.append(processing_time_ms)

        if processing_time_ms > self.input_lag_threshold:
            self.stats['input_lag_events'] += 1
            self.slow_frames.append({
                'time': time.time(),
                'processing_time': processing_time_ms,
                'type': 'input_lag'
            })

    def update_stats(self):
        """Update performance statistics"""
        if not self.frame_times:
            return

        frame_times_list = list(self.frame_times)

        # Basic statistics
        self.stats['avg_frame_time'] = sum(frame_times_list) / len(frame_times_list)
        self.stats['min_frame_time'] = min(frame_times_list)
        self.stats['max_frame_time'] = max(frame_times_list)

        # FPS calculation
        if self.stats['avg_frame_time'] > 0:
            self.stats['fps'] = 1000.0 / self.stats['avg_frame_time']

        # Clean up old slow frame records (keep last 60 seconds)
        current_time = time.time()
        self.slow_frames = [
            frame for frame in self.slow_frames
            if current_time - frame['time'] < 60.0
        ]

    def get_performance_report(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        input_avg = 0.0
        if self.input_processing_times:
            input_avg = sum(self.input_processing_times) / len(self.input_processing_times)

        return {
            'fps': self.stats['fps'],
            'avg_frame_time_ms': self.stats['avg_frame_time'],
            'min_frame_time_ms': self.stats['min_frame_time'],
            'max_frame_time_ms': self.stats['max_frame_time'],
            'frame_drops': self.stats['frame_drops'],
            'input_lag_events': self.stats['input_lag_events'],
            'avg_input_processing_ms': input_avg,
            'recent_slow_frames': len([
                f for f in self.slow_frames
                if time.time() - f['time'] < 10.0
            ])
        }

    def is_performance_degraded(self) -> bool:
        """Check if performance is currently degraded"""
        return (
            self.stats['fps'] < 55.0 or  # Below 55 FPS
            self.stats['avg_frame_time'] > 20.0 or  # Above 20ms per frame
            len([f for f in self.slow_frames if time.time() - f['time'] < 5.0]) > 3  # 3+ slow frames in 5 seconds
        )

    def get_performance_recommendations(self) -> List[str]:
        """Get performance improvement recommendations"""
        recommendations = []

        if self.stats['fps'] < 50.0:
            recommendations.append("FPS is below 50 - consider reducing debug output")

        if self.stats['avg_frame_time'] > 25.0:
            recommendations.append("Frame time is high - check for expensive operations")

        if self.stats['input_lag_events'] > 5:
            recommendations.append("Input lag detected - review event processing")

        if self.stats['frame_drops'] > 10:
            recommendations.append("Frequent frame drops - optimize main game loop")

        # Input processing specific recommendations
        if self.input_processing_times:
            avg_input = sum(self.input_processing_times) / len(self.input_processing_times)
            if avg_input > 3.0:
                recommendations.append("Input processing slow - consider reducing debug prints")

        return recommendations

    def reset_stats(self):
        """Reset all performance statistics"""
        self.frame_times.clear()
        self.input_processing_times.clear()
        self.slow_frames.clear()

        self.stats = {
            'avg_frame_time': 0.0,
            'min_frame_time': float('inf'),
            'max_frame_time': 0.0,
            'fps': 0.0,
            'frame_drops': 0,
            'input_lag_events': 0
        }


class InputLagDetector:
    """Detect input lag and responsiveness issues"""

    def __init__(self):
        self.last_keypress_time = 0
        self.keypress_response_times: deque = deque(maxlen=10)

    def record_keypress(self):
        """Record when a key is pressed"""
        self.last_keypress_time = time.time()

    def record_response(self):
        """Record when the system responds to the keypress"""
        if self.last_keypress_time > 0:
            response_time = (time.time() - self.last_keypress_time) * 1000.0
            self.keypress_response_times.append(response_time)
            self.last_keypress_time = 0
            return response_time
        return 0

    def get_avg_response_time(self) -> float:
        """Get average response time in milliseconds"""
        if not self.keypress_response_times:
            return 0.0
        return sum(self.keypress_response_times) / len(self.keypress_response_times)

    def is_responsive(self) -> bool:
        """Check if input is currently responsive"""
        avg_response = self.get_avg_response_time()
        return avg_response < 50.0  # Less than 50ms is considered responsive


# Global performance monitor instance
_global_performance_monitor = None
_global_input_lag_detector = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor

def get_input_lag_detector() -> InputLagDetector:
    """Get the global input lag detector instance"""
    global _global_input_lag_detector
    if _global_input_lag_detector is None:
        _global_input_lag_detector = InputLagDetector()
    return _global_input_lag_detector

# Convenience functions
def start_frame():
    """Mark the start of a frame for performance monitoring"""
    get_performance_monitor().frame_start()

def end_frame():
    """Mark the end of a frame for performance monitoring"""
    get_performance_monitor().frame_end()

def record_input_processing_time(time_ms: float):
    """Record input processing time"""
    get_performance_monitor().record_input_processing_time(time_ms)

def get_performance_report() -> Dict[str, Any]:
    """Get current performance report"""
    return get_performance_monitor().get_performance_report()

def is_performance_degraded() -> bool:
    """Check if performance is currently degraded"""
    return get_performance_monitor().is_performance_degraded()

def get_performance_recommendations() -> List[str]:
    """Get performance improvement recommendations"""
    return get_performance_monitor().get_performance_recommendations()

# Export main classes and functions
__all__ = [
    'PerformanceMonitor', 'InputLagDetector',
    'get_performance_monitor', 'get_input_lag_detector',
    'start_frame', 'end_frame', 'record_input_processing_time',
    'get_performance_report', 'is_performance_degraded', 'get_performance_recommendations'
]
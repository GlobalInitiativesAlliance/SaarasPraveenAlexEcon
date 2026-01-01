"""
Autoplay Performance Logging Utility

Tracks timing and performance metrics for:
- Activity completion times
- Auto narration speed and pacing
- Dialogue progression
- Overall autoplay smoothness
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ActivityMetrics:
    """Metrics for a single activity completion."""
    activity_name: str
    start_time: float
    end_time: Optional[float] = None
    actions_taken: int = 0
    was_auto_completed: bool = False

    @property
    def duration(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def actions_per_second(self) -> float:
        dur = self.duration
        if dur <= 0:
            return 0.0
        return self.actions_taken / dur


@dataclass
class DialogueMetrics:
    """Metrics for dialogue/narration timing."""
    speaker: str
    text_length: int
    word_count: int
    start_time: float
    end_time: Optional[float] = None
    was_skipped: bool = False

    @property
    def duration(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def chars_per_second(self) -> float:
        dur = self.duration
        if dur <= 0:
            return 0.0
        return self.text_length / dur

    @property
    def words_per_minute(self) -> float:
        dur = self.duration
        if dur <= 0:
            return 0.0
        return (self.word_count / dur) * 60


class AutoplayLogger:
    """
    Central logger for autoplay performance metrics.

    Usage:
        from src.utils.logging import autoplay_logger

        # Start tracking an activity
        autoplay_logger.start_activity("packing_game")

        # Log an action within the activity
        autoplay_logger.log_action("packed_item")

        # End the activity
        autoplay_logger.end_activity("packing_game")

        # Get performance report
        print(autoplay_logger.get_summary())
    """

    def __init__(self, enabled: bool = True, verbose: bool = False):
        self.enabled = enabled
        self.verbose = verbose

        # Session tracking
        self.session_start: Optional[float] = None
        self.session_end: Optional[float] = None

        # Activity metrics
        self.activities: Dict[str, ActivityMetrics] = {}
        self.completed_activities: List[ActivityMetrics] = []

        # Dialogue/narration metrics
        self.current_dialogue: Optional[DialogueMetrics] = None
        self.completed_dialogues: List[DialogueMetrics] = []

        # Frame timing for smoothness
        self.frame_times: List[float] = []
        self.last_frame_time: Optional[float] = None
        self.frame_drops: int = 0  # frames > 50ms

        # Action log
        self.action_log: List[Dict[str, Any]] = []

        # Objective tracking
        self.objectives_completed: List[Dict[str, Any]] = []
        self.current_objective: Optional[str] = None
        self.objective_start_time: Optional[float] = None

        # Stuck detection
        self.stuck_events: List[Dict[str, Any]] = []

    def start_session(self):
        """Start a new autoplay session."""
        self.session_start = time.time()
        self.session_end = None
        self._log("SESSION", "Autoplay session started")

    def end_session(self):
        """End the current autoplay session."""
        self.session_end = time.time()
        duration = self.session_end - (self.session_start or self.session_end)
        self._log("SESSION", f"Autoplay session ended. Duration: {duration:.2f}s")

    # =========================================================================
    # ACTIVITY TRACKING
    # =========================================================================

    def start_activity(self, activity_name: str):
        """Start tracking an activity."""
        if not self.enabled:
            return

        metrics = ActivityMetrics(
            activity_name=activity_name,
            start_time=time.time()
        )
        self.activities[activity_name] = metrics
        self._log("ACTIVITY_START", f"{activity_name}")

    def log_action(self, action_name: str, activity_name: Optional[str] = None):
        """Log an action within an activity."""
        if not self.enabled:
            return

        # Find the activity
        if activity_name and activity_name in self.activities:
            self.activities[activity_name].actions_taken += 1
        elif self.activities:
            # Use most recent activity
            latest = list(self.activities.values())[-1]
            latest.actions_taken += 1

        self.action_log.append({
            "action": action_name,
            "activity": activity_name,
            "time": time.time()
        })

        if self.verbose:
            self._log("ACTION", f"{action_name}")

    def end_activity(self, activity_name: str, auto_completed: bool = False):
        """End tracking an activity."""
        if not self.enabled:
            return

        if activity_name in self.activities:
            metrics = self.activities.pop(activity_name)
            metrics.end_time = time.time()
            metrics.was_auto_completed = auto_completed
            self.completed_activities.append(metrics)

            self._log("ACTIVITY_END",
                f"{activity_name} | {metrics.duration:.2f}s | "
                f"{metrics.actions_taken} actions | "
                f"{metrics.actions_per_second:.1f} actions/s | "
                f"auto={auto_completed}")

    def force_complete_activity(self, activity_name: str):
        """Force complete a stuck activity."""
        self.end_activity(activity_name, auto_completed=True)
        self.stuck_events.append({
            "type": "activity_force_complete",
            "activity": activity_name,
            "time": time.time()
        })
        self._log("STUCK", f"Force completed: {activity_name}")

    # =========================================================================
    # DIALOGUE/NARRATION TRACKING
    # =========================================================================

    def start_dialogue(self, speaker: str, text: str):
        """Start tracking a dialogue."""
        if not self.enabled:
            return

        # End any previous dialogue
        if self.current_dialogue:
            self.end_dialogue(skipped=True)

        word_count = len(text.split())
        self.current_dialogue = DialogueMetrics(
            speaker=speaker,
            text_length=len(text),
            word_count=word_count,
            start_time=time.time()
        )

        if self.verbose:
            self._log("DIALOGUE_START", f"[{speaker}] {len(text)} chars, {word_count} words")

    def end_dialogue(self, skipped: bool = False):
        """End tracking current dialogue."""
        if not self.enabled or not self.current_dialogue:
            return

        self.current_dialogue.end_time = time.time()
        self.current_dialogue.was_skipped = skipped

        metrics = self.current_dialogue
        self.completed_dialogues.append(metrics)

        self._log("DIALOGUE_END",
            f"[{metrics.speaker}] {metrics.duration:.2f}s | "
            f"{metrics.chars_per_second:.0f} cps | "
            f"{metrics.words_per_minute:.0f} wpm | "
            f"skipped={skipped}")

        self.current_dialogue = None

    # =========================================================================
    # OBJECTIVE TRACKING
    # =========================================================================

    def start_objective(self, objective_id: str):
        """Start tracking an objective."""
        if not self.enabled:
            return

        # End previous objective if any
        if self.current_objective:
            self.end_objective()

        self.current_objective = objective_id
        self.objective_start_time = time.time()
        self._log("OBJECTIVE_START", f"{objective_id}")

    def end_objective(self, success: bool = True):
        """End tracking current objective."""
        if not self.enabled or not self.current_objective:
            return

        duration = time.time() - (self.objective_start_time or time.time())
        self.objectives_completed.append({
            "objective_id": self.current_objective,
            "duration": duration,
            "success": success,
            "time": time.time()
        })

        self._log("OBJECTIVE_END",
            f"{self.current_objective} | {duration:.2f}s | success={success}")

        self.current_objective = None
        self.objective_start_time = None

    # =========================================================================
    # FRAME TIMING / SMOOTHNESS
    # =========================================================================

    def log_frame(self, dt: float):
        """Log a frame for smoothness analysis."""
        if not self.enabled:
            return

        now = time.time()

        if self.last_frame_time is not None:
            frame_delta = now - self.last_frame_time
            self.frame_times.append(frame_delta)

            # Track frame drops (>50ms = <20fps)
            if frame_delta > 0.05:
                self.frame_drops += 1
                if self.verbose:
                    self._log("FRAME_DROP", f"{frame_delta*1000:.1f}ms")

        self.last_frame_time = now

        # Keep only last 1000 frames
        if len(self.frame_times) > 1000:
            self.frame_times = self.frame_times[-1000:]

    def log_stuck(self, reason: str, location: Optional[str] = None):
        """Log a stuck event."""
        self.stuck_events.append({
            "reason": reason,
            "location": location,
            "time": time.time()
        })
        self._log("STUCK", f"{reason} @ {location or 'unknown'}")

    # =========================================================================
    # REPORTING
    # =========================================================================

    def get_activity_stats(self) -> Dict[str, Any]:
        """Get activity performance statistics."""
        if not self.completed_activities:
            return {"count": 0}

        durations = [a.duration for a in self.completed_activities]
        actions = [a.actions_taken for a in self.completed_activities]
        auto_completed = sum(1 for a in self.completed_activities if a.was_auto_completed)

        return {
            "count": len(self.completed_activities),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "min_time": min(durations),
            "max_time": max(durations),
            "total_actions": sum(actions),
            "auto_completed": auto_completed,
            "activities": [
                {
                    "name": a.activity_name,
                    "duration": a.duration,
                    "actions": a.actions_taken,
                    "auto": a.was_auto_completed
                }
                for a in self.completed_activities
            ]
        }

    def get_dialogue_stats(self) -> Dict[str, Any]:
        """Get dialogue/narration performance statistics."""
        if not self.completed_dialogues:
            return {"count": 0}

        durations = [d.duration for d in self.completed_dialogues]
        wpm_values = [d.words_per_minute for d in self.completed_dialogues if d.words_per_minute > 0]
        skipped = sum(1 for d in self.completed_dialogues if d.was_skipped)

        return {
            "count": len(self.completed_dialogues),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "avg_wpm": sum(wpm_values) / len(wpm_values) if wpm_values else 0,
            "skipped_count": skipped,
            "total_words": sum(d.word_count for d in self.completed_dialogues),
            "total_chars": sum(d.text_length for d in self.completed_dialogues)
        }

    def get_smoothness_stats(self) -> Dict[str, Any]:
        """Get frame timing / smoothness statistics."""
        if not self.frame_times:
            return {"frames": 0}

        avg_frame = sum(self.frame_times) / len(self.frame_times)

        return {
            "frames": len(self.frame_times),
            "avg_frame_ms": avg_frame * 1000,
            "avg_fps": 1.0 / avg_frame if avg_frame > 0 else 0,
            "frame_drops": self.frame_drops,
            "drop_rate": self.frame_drops / len(self.frame_times) if self.frame_times else 0,
            "stuck_events": len(self.stuck_events)
        }

    def get_objective_stats(self) -> Dict[str, Any]:
        """Get objective completion statistics."""
        if not self.objectives_completed:
            return {"count": 0}

        durations = [o["duration"] for o in self.objectives_completed]
        successful = sum(1 for o in self.objectives_completed if o["success"])

        return {
            "count": len(self.objectives_completed),
            "successful": successful,
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "objectives": self.objectives_completed
        }

    def get_summary(self) -> str:
        """Get a formatted summary of all metrics."""
        lines = []
        lines.append("=" * 60)
        lines.append("AUTOPLAY PERFORMANCE SUMMARY")
        lines.append("=" * 60)

        # Session info
        if self.session_start:
            session_duration = (self.session_end or time.time()) - self.session_start
            lines.append(f"\nSession Duration: {session_duration:.1f}s")

        # Activity stats
        activity_stats = self.get_activity_stats()
        if activity_stats["count"] > 0:
            lines.append(f"\n--- ACTIVITIES ---")
            lines.append(f"  Completed: {activity_stats['count']}")
            lines.append(f"  Total Time: {activity_stats['total_time']:.1f}s")
            lines.append(f"  Avg Time: {activity_stats['avg_time']:.2f}s")
            lines.append(f"  Auto-completed: {activity_stats['auto_completed']}")
            lines.append(f"  Total Actions: {activity_stats['total_actions']}")

            # Per-activity breakdown
            lines.append(f"\n  Breakdown:")
            for a in activity_stats["activities"]:
                auto_tag = " [AUTO]" if a["auto"] else ""
                lines.append(f"    {a['name']}: {a['duration']:.2f}s, {a['actions']} actions{auto_tag}")

        # Dialogue stats
        dialogue_stats = self.get_dialogue_stats()
        if dialogue_stats["count"] > 0:
            lines.append(f"\n--- NARRATION ---")
            lines.append(f"  Dialogues: {dialogue_stats['count']}")
            lines.append(f"  Total Time: {dialogue_stats['total_time']:.1f}s")
            lines.append(f"  Avg Time: {dialogue_stats['avg_time']:.2f}s")
            lines.append(f"  Avg Reading Speed: {dialogue_stats['avg_wpm']:.0f} wpm")
            lines.append(f"  Total Words: {dialogue_stats['total_words']}")
            lines.append(f"  Skipped: {dialogue_stats['skipped_count']}")

        # Objective stats
        obj_stats = self.get_objective_stats()
        if obj_stats["count"] > 0:
            lines.append(f"\n--- OBJECTIVES ---")
            lines.append(f"  Completed: {obj_stats['count']}")
            lines.append(f"  Successful: {obj_stats['successful']}")
            lines.append(f"  Total Time: {obj_stats['total_time']:.1f}s")
            lines.append(f"  Avg Time: {obj_stats['avg_time']:.2f}s")

        # Smoothness stats
        smooth_stats = self.get_smoothness_stats()
        if smooth_stats["frames"] > 0:
            lines.append(f"\n--- SMOOTHNESS ---")
            lines.append(f"  Frames Tracked: {smooth_stats['frames']}")
            lines.append(f"  Avg FPS: {smooth_stats['avg_fps']:.1f}")
            lines.append(f"  Frame Drops: {smooth_stats['frame_drops']} ({smooth_stats['drop_rate']*100:.1f}%)")
            lines.append(f"  Stuck Events: {smooth_stats['stuck_events']}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def get_json_report(self) -> Dict[str, Any]:
        """Get all metrics as a JSON-serializable dict."""
        return {
            "session": {
                "start": self.session_start,
                "end": self.session_end,
                "duration": (self.session_end or time.time()) - (self.session_start or time.time()) if self.session_start else 0
            },
            "activities": self.get_activity_stats(),
            "dialogues": self.get_dialogue_stats(),
            "objectives": self.get_objective_stats(),
            "smoothness": self.get_smoothness_stats(),
            "stuck_events": self.stuck_events
        }

    def reset(self):
        """Reset all metrics for a new session."""
        self.session_start = None
        self.session_end = None
        self.activities.clear()
        self.completed_activities.clear()
        self.current_dialogue = None
        self.completed_dialogues.clear()
        self.frame_times.clear()
        self.last_frame_time = None
        self.frame_drops = 0
        self.action_log.clear()
        self.objectives_completed.clear()
        self.current_objective = None
        self.objective_start_time = None
        self.stuck_events.clear()
        self._log("RESET", "All metrics reset")

    def _log(self, category: str, message: str):
        """Internal logging with timestamp."""
        if self.enabled:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] [AUTOPLAY:{category}] {message}")


# Global singleton instance
autoplay_logger = AutoplayLogger(enabled=True, verbose=False)


# Convenience functions for quick logging
def log_activity_start(name: str):
    autoplay_logger.start_activity(name)

def log_activity_end(name: str, auto: bool = False):
    autoplay_logger.end_activity(name, auto)

def log_dialogue(speaker: str, text: str):
    autoplay_logger.start_dialogue(speaker, text)

def log_dialogue_end(skipped: bool = False):
    autoplay_logger.end_dialogue(skipped)

def log_objective(objective_id: str):
    autoplay_logger.start_objective(objective_id)

def log_objective_complete(success: bool = True):
    autoplay_logger.end_objective(success)

def log_frame(dt: float):
    autoplay_logger.log_frame(dt)

def log_action(action: str):
    autoplay_logger.log_action(action)

def log_stuck(reason: str, location: str = None):
    autoplay_logger.log_stuck(reason, location)

def get_summary() -> str:
    return autoplay_logger.get_summary()

def enable_verbose():
    autoplay_logger.verbose = True

def disable_logging():
    autoplay_logger.enabled = False

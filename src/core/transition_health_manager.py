"""
Transition Health Manager - Ensures smooth user experience and prevents stuck states
"""
import time
import pygame

class TransitionHealthManager:
    """Monitors game state and prevents users from getting stuck"""

    def __init__(self, game):
        self.game = game

        # State monitoring
        self.last_objective_change = time.time()
        self.last_room_change = time.time()
        self.last_activity_change = time.time()
        self.current_room = None
        self.current_objective_id = None
        self.current_activity_name = None

        # Health check timers
        self.stuck_room_threshold = 120.0  # 2 minutes in same room
        self.stuck_objective_threshold = 300.0  # 5 minutes on same objective
        self.stuck_activity_threshold = 180.0  # 3 minutes in same activity

        # User guidance
        self.guidance_shown = set()  # Track what guidance we've already shown
        self.help_font = pygame.font.Font(None, 24)
        self.help_surface = None
        self.help_timer = 0
        self.help_duration = 8.0  # Show help for 8 seconds

        # Auto-recovery options
        self.recovery_options = {
            'stuck_in_room': self.offer_room_exit,
            'stuck_on_objective': self.offer_objective_hint,
            'stuck_in_activity': self.offer_activity_help,
            'stale_activity_state': self.fix_stale_activity,
        }

    def update(self, dt):
        """Update health monitoring and provide assistance"""
        self.update_state_tracking()
        self.check_for_stuck_states()
        self.update_help_display(dt)

    def update_state_tracking(self):
        """Track current game state for transition monitoring"""
        current_time = time.time()

        # Track room changes
        new_room = None
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            new_room = type(self.game.current_interior).__name__

        if new_room != self.current_room:
            self.current_room = new_room
            self.last_room_change = current_time

        # Track objective changes
        new_objective = None
        if hasattr(self.game, 'objective_manager'):
            current_obj = self.game.objective_manager.get_current_objective()
            if current_obj:
                new_objective = current_obj.id

        if new_objective != self.current_objective_id:
            self.current_objective_id = new_objective
            self.last_objective_change = current_time

        # Track activity changes
        new_activity = None
        if (hasattr(self.game, 'objective_manager') and
            hasattr(self.game.objective_manager, 'current_activity') and
            self.game.objective_manager.current_activity):
            new_activity = type(self.game.objective_manager.current_activity).__name__

        if new_activity != self.current_activity_name:
            self.current_activity_name = new_activity
            self.last_activity_change = current_time

    def check_for_stuck_states(self):
        """Proactively check for states where user might be stuck"""
        current_time = time.time()

        # Check for stuck in room
        if (current_time - self.last_room_change > self.stuck_room_threshold and
            'stuck_in_room' not in self.guidance_shown):
            self.recovery_options['stuck_in_room']()
            self.guidance_shown.add('stuck_in_room')

        # Check for stuck on objective
        if (current_time - self.last_objective_change > self.stuck_objective_threshold and
            'stuck_on_objective' not in self.guidance_shown):
            self.recovery_options['stuck_on_objective']()
            self.guidance_shown.add('stuck_on_objective')

        # Check for stuck in activity
        if (self.current_activity_name and
            current_time - self.last_activity_change > self.stuck_activity_threshold and
            'stuck_in_activity' not in self.guidance_shown):
            self.recovery_options['stuck_in_activity']()
            self.guidance_shown.add('stuck_in_activity')

        # Check for stale activity state
        self.check_stale_activity_state()

    def check_stale_activity_state(self):
        """Check for activities that might be in invalid states"""
        if not hasattr(self.game, 'objective_manager'):
            return

        current_activity = getattr(self.game.objective_manager, 'current_activity', None)
        if current_activity:
            # Check if activity is completed but still blocking
            if (hasattr(current_activity, 'completed') and current_activity.completed and
                hasattr(current_activity, 'active') and current_activity.active):
                print("[HEALTH_CHECK] Detected completed activity still blocking - fixing")
                self.fix_stale_activity()

            # Check if activity is missing required attributes (but be less aggressive with legitimate activities)
            if not hasattr(current_activity, 'active') or not hasattr(current_activity, 'completed'):
                activity_name = current_activity.__class__.__name__
                print(f"[HEALTH_CHECK] Activity {activity_name} missing attributes - active: {hasattr(current_activity, 'active')}, completed: {hasattr(current_activity, 'completed')}")
                # Only clear truly malformed activities, not mini-game managers
                if 'MiniGameManager' not in activity_name and 'Manager' not in activity_name:
                    print(f"[HEALTH_CHECK] Clearing malformed activity: {activity_name}")
                    self.fix_stale_activity()
                else:
                    print(f"[HEALTH_CHECK] Skipping clearing of manager activity: {activity_name}")

    def offer_room_exit(self):
        """Offer help when user seems stuck in a room"""
        guidance = (
            "🤔 You've been in this room for a while.\n"
            "💡 Try pressing 'E' near highlighted objects\n"
            "🚪 Press 'ESC' to exit if you're done here\n"
            "📋 Check your objective in the top-left corner"
        )
        self.show_help(guidance)

    def offer_objective_hint(self):
        """Offer help when user seems stuck on an objective"""
        if not hasattr(self.game, 'objective_manager'):
            return

        current_obj = self.game.objective_manager.get_current_objective()
        if not current_obj:
            return

        # Provide objective-specific hints
        hints = {
            'reality_check': "Go to the Emergency Shelter and complete intake process",
            'losing_stuff': "Check your backpack and complete the investigation",
            'housing_menu': "Visit the Housing Office to learn about options",
            'move_in_alex': "Go to Alex's apartment and start packing",
            'meet_alex': "Visit Alex's apartment to meet them",
        }

        hint = hints.get(current_obj.id, f"Work on: {current_obj.title}")
        guidance = f"🎯 Current Goal: {hint}\n💭 Need help? Check the objective description"
        self.show_help(guidance)

    def offer_activity_help(self):
        """Offer help when user seems stuck in an activity"""
        guidance = (
            "⚡ You're in an interactive activity\n"
            "🎮 Follow the on-screen prompts\n"
            "⌨️ Try different keys or mouse clicks\n"
            "🆘 Press 'ESC' if you need to exit"
        )
        self.show_help(guidance)

    def fix_stale_activity(self):
        """Fix activities in invalid states"""
        if not hasattr(self.game, 'objective_manager'):
            return

        current_activity = getattr(self.game.objective_manager, 'current_activity', None)
        if current_activity:
            print(f"[HEALTH_CHECK] Clearing stale activity: {type(current_activity).__name__}")

            # Mark as completed and inactive
            if hasattr(current_activity, 'completed'):
                current_activity.completed = True
            if hasattr(current_activity, 'active'):
                current_activity.active = False

            # Clear from objective manager
            self.game.objective_manager.current_activity = None

            # Show user feedback
            guidance = "🔧 Fixed a stuck activity - you can continue playing!"
            self.show_help(guidance)

    def show_help(self, text):
        """Display helpful guidance to the user"""
        print(f"[USER_GUIDANCE] {text.replace(chr(10), ' | ')}")  # Log for debugging

        # Create help surface for display
        lines = text.split('\n')
        line_height = 30
        total_height = len(lines) * line_height + 20
        width = 400

        self.help_surface = pygame.Surface((width, total_height), pygame.SRCALPHA)
        self.help_surface.fill((0, 0, 0, 180))  # Semi-transparent black background

        # Add border
        pygame.draw.rect(self.help_surface, (255, 255, 255), (0, 0, width, total_height), 2)

        # Render text lines
        y_offset = 10
        for line in lines:
            text_surface = self.help_font.render(line, True, (255, 255, 255))
            self.help_surface.blit(text_surface, (10, y_offset))
            y_offset += line_height

        # Show for duration
        self.help_timer = self.help_duration

    def update_help_display(self, dt):
        """Update help display timer"""
        if self.help_timer > 0:
            self.help_timer -= dt
            if self.help_timer <= 0:
                self.help_surface = None

    def draw(self, screen):
        """Draw help overlay if active"""
        if self.help_surface:
            # Center on screen
            screen_rect = screen.get_rect()
            help_rect = self.help_surface.get_rect()
            help_rect.center = screen_rect.center
            screen.blit(self.help_surface, help_rect)

    def manual_check(self):
        """Allow manual health check (for testing or emergency use)"""
        print("[HEALTH_CHECK] Manual health check requested")
        self.check_for_stuck_states()

        # Also provide immediate state summary
        status = f"""
🔍 GAME STATE HEALTH CHECK:
📍 Room: {self.current_room or 'Overworld'}
🎯 Objective: {self.current_objective_id or 'None'}
⚡ Activity: {self.current_activity_name or 'None'}
⏱️ Time since last change: {int(time.time() - self.last_objective_change)}s
"""
        self.show_help(status.strip())

    def reset_guidance_tracking(self):
        """Reset guidance tracking (useful for testing)"""
        self.guidance_shown.clear()
        print("[HEALTH_CHECK] Guidance tracking reset")

    def on_objective_complete(self):
        """Called when an objective completes - reset guidance tracking"""
        self.guidance_shown.discard('stuck_on_objective')

    def on_room_exit(self):
        """Called when exiting a room - reset guidance tracking"""
        self.guidance_shown.discard('stuck_in_room')

    def on_activity_complete(self):
        """Called when an activity completes - reset guidance tracking"""
        self.guidance_shown.discard('stuck_in_activity')
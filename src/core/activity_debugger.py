"""
Activity Debugger - Debug overlay for activity states and progression
"""
import pygame

class ActivityDebugger:
    """Debug monitor for activities and objective progression"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False

        # Font setup
        self.font_small = pygame.font.Font(None, 16)
        self.font_normal = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 24)

        # Panel dimensions and position
        self.panel_width = 350
        self.panel_height = 500
        self.panel_x = 10  # Left side of screen
        self.panel_y = 10

        # Colors
        self.bg_color = (20, 20, 25, 220)
        self.border_color = (100, 255, 100)
        self.text_color = (255, 255, 255)
        self.active_color = (100, 255, 100)
        self.warning_color = (255, 200, 100)
        self.error_color = (255, 100, 100)

        # Data tracking
        self.current_activity = None
        self.current_objective = None
        self.activity_history = []
        self.completion_queue = []

    def toggle(self):
        """Toggle debugger visibility"""
        self.visible = not self.visible

    def update(self, game):
        """Update debugger with current game state"""
        if not self.visible:
            return

        # Get current activity info
        current_activity = None
        if hasattr(game, 'current_interior') and game.current_interior:
            if hasattr(game.current_interior, 'current_activity') and game.current_interior.current_activity:
                current_activity = game.current_interior.current_activity

        # Track activity changes
        if current_activity != self.current_activity:
            if current_activity:
                self.activity_history.append({
                    'type': type(current_activity).__name__,
                    'stage': getattr(current_activity, 'stage', 'unknown'),
                    'active': current_activity.active,
                    'completed': current_activity.completed
                })
            self.current_activity = current_activity

        # Get current objective
        if hasattr(game, 'objective_manager') and game.objective_manager:
            self.current_objective = game.objective_manager.get_current_objective()

    def draw(self, screen, game):
        """Draw the activity debugger overlay"""
        if not self.visible:
            return

        # Update with latest data
        self.update(game)

        # Create panel surface
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)

        # Draw border
        pygame.draw.rect(panel_surface, self.border_color,
                        (0, 0, self.panel_width, self.panel_height), 2)

        # Draw content
        y_offset = 10
        y_offset = self.draw_header(panel_surface, y_offset)
        y_offset = self.draw_current_activity(panel_surface, y_offset, game)
        y_offset = self.draw_current_objective(panel_surface, y_offset, game)
        y_offset = self.draw_completion_status(panel_surface, y_offset, game)
        y_offset = self.draw_activity_history(panel_surface, y_offset)
        self.draw_controls(panel_surface, self.panel_height - 50)

        # Blit to main screen
        screen.blit(panel_surface, (self.panel_x, self.panel_y))

    def draw_header(self, surface, y):
        """Draw panel header"""
        title = self.font_large.render("ACTIVITY DEBUGGER", True, self.active_color)
        surface.blit(title, (10, y))
        y += 30

        # Draw separator
        pygame.draw.line(surface, self.border_color, (10, y), (self.panel_width - 10, y), 1)
        return y + 15

    def draw_current_activity(self, surface, y, game):
        """Draw current activity information"""
        title = self.font_normal.render("CURRENT ACTIVITY", True, self.active_color)
        surface.blit(title, (10, y))
        y += 25

        if self.current_activity:
            # Activity type
            activity_type = type(self.current_activity).__name__
            text = self.font_small.render(f"Type: {activity_type}", True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

            # Activity state
            stage = getattr(self.current_activity, 'stage', 'N/A')
            text = self.font_small.render(f"Stage: {stage}", True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

            # Activity status
            active_color = self.active_color if self.current_activity.active else self.error_color
            text = self.font_small.render(f"Active: {self.current_activity.active}", True, active_color)
            surface.blit(text, (15, y))
            y += 18

            completed_color = self.active_color if self.current_activity.completed else self.text_color
            text = self.font_small.render(f"Completed: {self.current_activity.completed}", True, completed_color)
            surface.blit(text, (15, y))
            y += 18

            # Completion state if available
            if hasattr(self.current_activity, 'completion_state'):
                completion_state = self.current_activity.completion_state
                state_color = self.active_color if completion_state == "completing" else self.text_color
                text = self.font_small.render(f"State: {completion_state}", True, state_color)
                surface.blit(text, (15, y))
                y += 18

            # Completion feedback status
            if hasattr(self.current_activity, 'completion_feedback'):
                feedback_active = self.current_activity.completion_feedback.is_active()
                feedback_color = self.active_color if feedback_active else self.text_color
                text = self.font_small.render(f"Feedback: {feedback_active}", True, feedback_color)
                surface.blit(text, (15, y))
                y += 18

        else:
            text = self.font_small.render("No active activity", True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

        return y + 10

    def draw_current_objective(self, surface, y, game):
        """Draw current objective information"""
        title = self.font_normal.render("CURRENT OBJECTIVE", True, self.active_color)
        surface.blit(title, (10, y))
        y += 25

        if self.current_objective:
            # Objective ID
            text = self.font_small.render(f"ID: {self.current_objective.id}", True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

            # Objective title
            title_text = self.current_objective.title[:30] + "..." if len(self.current_objective.title) > 30 else self.current_objective.title
            text = self.font_small.render(f"Title: {title_text}", True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

            # Objective status
            completed_color = self.active_color if self.current_objective.completed else self.text_color
            text = self.font_small.render(f"Completed: {self.current_objective.completed}", True, completed_color)
            surface.blit(text, (15, y))
            y += 18

        else:
            text = self.font_small.render("No current objective", True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

        return y + 10

    def draw_completion_status(self, surface, y, game):
        """Draw activity completion and progression status"""
        title = self.font_normal.render("COMPLETION STATUS", True, self.active_color)
        surface.blit(title, (10, y))
        y += 25

        # Check current interior for completion info
        if hasattr(game, 'current_interior') and game.current_interior:
            interior = game.current_interior

            # Completed interactions
            if hasattr(interior, 'completed_interactions'):
                completed_count = len(interior.completed_interactions)
                text = self.font_small.render(f"Completed interactions: {completed_count}", True, self.text_color)
                surface.blit(text, (15, y))
                y += 18

                # Show last few completed interactions
                if interior.completed_interactions:
                    recent = list(interior.completed_interactions)[-3:]  # Last 3
                    for interaction in recent:
                        text = self.font_small.render(f"  ✓ {interaction}", True, self.active_color)
                        surface.blit(text, (20, y))
                        y += 15

            # Required interactions
            if hasattr(interior, 'get_required_interactions'):
                try:
                    required = interior.get_required_interactions()
                    if required:
                        text = self.font_small.render(f"Required interactions:", True, self.warning_color)
                        surface.blit(text, (15, y))
                        y += 18

                        for req in required[:3]:  # Show first 3
                            status = "✓" if req in interior.completed_interactions else "○"
                            color = self.active_color if req in interior.completed_interactions else self.text_color
                            text = self.font_small.render(f"  {status} {req}", True, color)
                            surface.blit(text, (20, y))
                            y += 15
                except:
                    pass

        return y + 10

    def draw_activity_history(self, surface, y):
        """Draw recent activity history"""
        title = self.font_normal.render("ACTIVITY HISTORY", True, self.active_color)
        surface.blit(title, (10, y))
        y += 25

        # Show last 3 activities
        recent_activities = self.activity_history[-3:] if self.activity_history else []

        if recent_activities:
            for i, activity in enumerate(reversed(recent_activities)):
                activity_text = f"{len(recent_activities)-i}. {activity['type']}"
                text = self.font_small.render(activity_text, True, self.text_color)
                surface.blit(text, (15, y))
                y += 15

                status_text = f"   Stage: {activity['stage']}, Complete: {activity['completed']}"
                text = self.font_small.render(status_text, True, self.text_color)
                surface.blit(text, (15, y))
                y += 15
        else:
            text = self.font_small.render("No activity history", True, self.text_color)
            surface.blit(text, (15, y))

        return y + 10

    def draw_controls(self, surface, y):
        """Draw control instructions"""
        title = self.font_normal.render("CONTROLS", True, self.warning_color)
        surface.blit(title, (10, y))
        y += 25

        controls = [
            "F4: Toggle this panel",
            "F3: Toggle debug panel"
        ]

        for control in controls:
            text = self.font_small.render(control, True, self.text_color)
            surface.blit(text, (15, y))
            y += 18

    def get_required_interactions(self, interior):
        """Helper to get required interactions from current interior"""
        if not hasattr(interior, 'narrative_content'):
            return []

        current = interior.game.objective_manager.get_current_objective()
        if not current:
            return []

        if current.id in interior.narrative_content:
            interactions = interior.narrative_content[current.id].get('interactions', {})
            return [name for name, data in interactions.items() if data.get('required', False)]

        return []
"""
Activity Status HUD - Small overlay showing current activity progress
"""
import pygame
import math

class ActivityStatusHUD:
    """Heads-up display showing activity progress and hints"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Position in top-right corner
        self.hud_width = 250
        self.hud_height = 80
        self.hud_x = screen_width - self.hud_width - 15
        self.hud_y = 15

        # Fonts
        self.title_font = pygame.font.Font(None, 22)
        self.text_font = pygame.font.Font(None, 18)
        self.hint_font = pygame.font.Font(None, 16)

        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.border_color = (100, 150, 255)
        self.text_color = (255, 255, 255)
        self.progress_color = (100, 255, 100)
        self.hint_color = (255, 255, 150)

        # Animation
        self.fade_alpha = 0
        self.target_alpha = 0
        self.slide_offset = -50  # Start off-screen
        self.target_offset = 0

        # State
        self.visible = False
        self.current_activity = None
        self.time_visible = 0.0

    def show_activity(self, activity, hint_text=""):
        """Show HUD for the given activity"""
        self.current_activity = activity
        self.hint_text = hint_text
        self.visible = True
        self.target_alpha = 255
        self.target_offset = 0
        self.time_visible = 0.0

    def hide(self):
        """Hide the HUD"""
        self.target_alpha = 0
        self.target_offset = -50

    def update(self, dt, game):
        """Update HUD animation and content"""
        # Update animation
        fade_speed = 400  # Alpha units per second
        slide_speed = 200  # Pixels per second

        if self.fade_alpha < self.target_alpha:
            self.fade_alpha = min(self.target_alpha, self.fade_alpha + fade_speed * dt)
        elif self.fade_alpha > self.target_alpha:
            self.fade_alpha = max(self.target_alpha, self.fade_alpha - fade_speed * dt)

        if self.slide_offset < self.target_offset:
            self.slide_offset = min(self.target_offset, self.slide_offset + slide_speed * dt)
        elif self.slide_offset > self.target_offset:
            self.slide_offset = max(self.target_offset, self.slide_offset - slide_speed * dt)

        # Check if we should hide
        if self.target_alpha == 0 and self.fade_alpha <= 0:
            self.visible = False

        # Auto-detect activity state
        if self.visible:
            self.time_visible += dt

            # Get current activity from game
            current_activity = self.get_current_activity(game)

            # If activity changed or completed, update display
            if current_activity != self.current_activity:
                if current_activity is None:
                    # Activity ended, hide HUD
                    self.hide()
                else:
                    # New activity, show it
                    self.show_activity(current_activity)

    def get_current_activity(self, game):
        """Get the current active activity from the game"""
        if hasattr(game, 'current_interior') and game.current_interior:
            if hasattr(game.current_interior, 'current_activity'):
                return game.current_interior.current_activity
        return None

    def draw(self, screen, game):
        """Draw the activity status HUD"""
        if not self.visible or self.fade_alpha <= 0:
            return

        # Calculate position with slide animation
        draw_x = self.hud_x + self.slide_offset
        draw_y = self.hud_y

        # Create HUD surface with alpha
        hud_surface = pygame.Surface((self.hud_width, self.hud_height), pygame.SRCALPHA)

        # Background with rounded corners effect
        bg_color = (*self.bg_color[:3], min(self.bg_color[3], int(self.fade_alpha)))
        pygame.draw.rect(hud_surface, bg_color, (0, 0, self.hud_width, self.hud_height), border_radius=8)

        # Border
        border_alpha = min(255, int(self.fade_alpha))
        border_color = (*self.border_color, border_alpha)
        pygame.draw.rect(hud_surface, border_color, (0, 0, self.hud_width, self.hud_height), 2, border_radius=8)

        # Content alpha
        content_alpha = min(255, int(self.fade_alpha))

        if self.current_activity:
            # Activity title
            activity_name = self.get_activity_display_name(self.current_activity)
            title_surface = self.title_font.render(activity_name, True, (*self.text_color, content_alpha))
            hud_surface.blit(title_surface, (10, 8))

            # Progress information
            progress_info = self.get_progress_info(self.current_activity)
            if progress_info:
                progress_surface = self.text_font.render(progress_info, True, (*self.progress_color, content_alpha))
                hud_surface.blit(progress_surface, (10, 30))

            # Hint text
            hint_text = self.get_hint_text(self.current_activity)
            if hint_text:
                hint_surface = self.hint_font.render(hint_text, True, (*self.hint_color, content_alpha))
                hud_surface.blit(hint_surface, (10, 50))

            # Progress bar for applicable activities
            progress_percent = self.get_progress_percentage(self.current_activity)
            if progress_percent is not None:
                self.draw_progress_bar(hud_surface, 10, self.hud_height - 15, self.hud_width - 20, 8,
                                     progress_percent, content_alpha)

        # Blit to screen
        screen.blit(hud_surface, (int(draw_x), int(draw_y)))

    def get_activity_display_name(self, activity):
        """Get a user-friendly display name for the activity"""
        class_name = type(activity).__name__

        # Convert class names to readable names
        name_mapping = {
            'JobApplicationActivity': 'Job Application',
            'TLPApplication': 'Housing Application',
            'TenantRightsQuiz': 'Tenant Rights Quiz',
            'CreditApplication': 'Credit Application',
            'RentalApplication': 'Rental Application',
            'TransitionScene': 'Story Transition'
        }

        return name_mapping.get(class_name, class_name.replace('Activity', ''))

    def get_progress_info(self, activity):
        """Get progress information text for the activity"""
        if hasattr(activity, 'stage'):
            if hasattr(activity, 'form_data') and hasattr(activity, 'fields'):
                # Form-based activity
                completed_fields = sum(1 for field in activity.fields if activity.form_data.get(field, '').strip())
                total_fields = len(activity.fields)
                return f"{completed_fields}/{total_fields} fields completed"

            elif hasattr(activity, 'current_page') and hasattr(activity, 'total_pages'):
                # Multi-page activity
                return f"Page {activity.current_page}/{activity.total_pages}"

            elif hasattr(activity, 'current_question') and hasattr(activity, 'questions'):
                # Quiz activity
                return f"Question {activity.current_question + 1}/{len(activity.questions)}"

            else:
                # Generic stage-based activity
                stage_names = {
                    0: "Starting",
                    1: "In Progress",
                    2: "Completing"
                }
                return stage_names.get(activity.stage, f"Stage {activity.stage}")

        return None

    def get_hint_text(self, activity):
        """Get hint text for the current activity"""
        if hasattr(activity, 'stage'):
            if hasattr(activity, 'form_data') and hasattr(activity, 'fields'):
                # Form-based activity hints
                if activity.stage == 0:
                    return "Click Apply to start"
                elif activity.stage == 1:
                    completed = sum(1 for field in activity.fields if activity.form_data.get(field, '').strip())
                    if completed < len(activity.fields):
                        return "Fill all fields, then press ENTER"
                    else:
                        return "Press ENTER to submit"
                elif activity.stage == 2:
                    return "Press any key to continue"

            elif hasattr(activity, 'questions'):
                # Quiz activity hints
                if activity.stage == 0:
                    return "Read and answer questions"
                else:
                    return "Select answer and continue"

            else:
                # Generic hints
                if activity.stage == 0:
                    return "Follow on-screen instructions"
                elif activity.stage == 1:
                    return "Complete the task"
                elif activity.stage == 2:
                    return "Task completed!"

        return ""

    def get_progress_percentage(self, activity):
        """Get progress as a percentage (0-100) or None if not applicable"""
        if hasattr(activity, 'form_data') and hasattr(activity, 'fields'):
            # Form-based progress
            completed_fields = sum(1 for field in activity.fields if activity.form_data.get(field, '').strip())
            total_fields = len(activity.fields)
            return (completed_fields / total_fields) * 100 if total_fields > 0 else 0

        elif hasattr(activity, 'current_page') and hasattr(activity, 'total_pages'):
            # Page-based progress
            return (activity.current_page / activity.total_pages) * 100

        elif hasattr(activity, 'current_question') and hasattr(activity, 'questions'):
            # Quiz progress
            return ((activity.current_question + 1) / len(activity.questions)) * 100

        return None

    def draw_progress_bar(self, surface, x, y, width, height, percentage, alpha):
        """Draw a progress bar"""
        # Background
        bg_color = (50, 50, 50, alpha)
        pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=height//2)

        # Progress fill
        fill_width = int((width - 4) * min(percentage, 100) / 100)
        if fill_width > 0:
            fill_color = (*self.progress_color, alpha)
            pygame.draw.rect(surface, fill_color, (x + 2, y + 2, fill_width, height - 4), border_radius=max(1, (height-4)//2))

    def should_show_for_activity(self, activity):
        """Determine if HUD should be shown for this activity type"""
        # Show HUD for interactive activities, hide for transition scenes
        return not isinstance(activity, type(None)) and hasattr(activity, 'active') and activity.active
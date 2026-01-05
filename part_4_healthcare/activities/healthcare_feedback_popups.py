"""
Feedback Popup System for Healthcare Mini-Games
Animated score popups, achievements, and notifications
Includes healthcare-specific achievements
"""

import pygame
import math
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ScorePopup:
    """Animated score/text popup that fades up and out"""
    x: float
    y: float
    text: str
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 1.0
    font_size: str = 'medium'  # 'small', 'medium', 'large'
    velocity_y: float = -40  # Pixels per second upward
    scale: float = 1.0
    start_scale: float = 1.5  # Start larger, shrink to normal
    icon: Optional[str] = None  # Optional icon prefix


@dataclass
class AchievementBanner:
    """Slide-in achievement banner"""
    title: str
    description: str
    icon: str
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 3.0  # Visible for 3 seconds
    slide_progress: float = 0.0  # 0 = off screen, 1 = fully visible
    state: str = 'entering'  # 'entering', 'visible', 'exiting'


class HealthcareFeedbackManager:
    """
    Manages animated feedback popups for healthcare mini-games
    Provides score popups, achievements, and notification toasts
    """

    def __init__(self):
        self.popups: List[ScorePopup] = []
        self.achievements: List[AchievementBanner] = []
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize font cache"""
        try:
            self.fonts['small'] = pygame.font.SysFont('SF Pro Display', 18, bold=True)
            self.fonts['medium'] = pygame.font.SysFont('SF Pro Display', 24, bold=True)
            self.fonts['large'] = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.fonts['achievement_title'] = pygame.font.SysFont('SF Pro Display', 20, bold=True)
            self.fonts['achievement_desc'] = pygame.font.SysFont('SF Pro Text', 16)
        except:
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['medium'] = pygame.font.Font(None, 28)
            self.fonts['large'] = pygame.font.Font(None, 42)
            self.fonts['achievement_title'] = pygame.font.Font(None, 24)
            self.fonts['achievement_desc'] = pygame.font.Font(None, 18)

    def update(self, dt: float) -> None:
        """Update all popups and achievements"""
        # Update score popups
        for popup in self.popups[:]:
            popup.life -= dt / popup.max_life
            if popup.life <= 0:
                self.popups.remove(popup)
                continue

            # Move upward
            popup.y += popup.velocity_y * dt

            # Scale animation (start big, shrink to normal)
            progress = 1 - popup.life  # 0 to 1
            if progress < 0.2:
                # First 20%: shrink from start_scale to 1.0
                popup.scale = popup.start_scale - (popup.start_scale - 1.0) * (progress / 0.2)
            else:
                popup.scale = 1.0

        # Update achievements
        for achievement in self.achievements[:]:
            achievement.life -= dt / achievement.max_life
            if achievement.life <= 0:
                self.achievements.remove(achievement)
                continue

            # State transitions
            if achievement.state == 'entering':
                achievement.slide_progress = min(1.0, achievement.slide_progress + dt * 5)
                if achievement.slide_progress >= 1.0:
                    achievement.state = 'visible'
            elif achievement.state == 'visible':
                if achievement.life < 0.3:  # Last 30% of life
                    achievement.state = 'exiting'
            elif achievement.state == 'exiting':
                achievement.slide_progress = max(0.0, achievement.slide_progress - dt * 5)

    def render(self, screen: pygame.Surface) -> None:
        """Render all active popups and achievements"""
        # Render score popups
        for popup in self.popups:
            self._render_popup(screen, popup)

        # Render achievements
        for i, achievement in enumerate(self.achievements):
            self._render_achievement(screen, achievement, i)

    def draw(self, screen: pygame.Surface) -> None:
        """Alias for render - draw all active popups and achievements"""
        self.render(screen)

    def _render_popup(self, screen: pygame.Surface, popup: ScorePopup) -> None:
        """Render a single score popup"""
        # Calculate alpha based on life
        alpha = int(255 * min(1.0, popup.life * 2))  # Fade out in last 50%

        # Get font
        font = self.fonts.get(popup.font_size, self.fonts['medium'])

        # Render text
        text = popup.text
        if popup.icon:
            text = f"{popup.icon} {text}"

        text_surface = font.render(text, True, popup.color)

        # Apply scale
        if popup.scale != 1.0:
            new_width = int(text_surface.get_width() * popup.scale)
            new_height = int(text_surface.get_height() * popup.scale)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        # Apply alpha
        text_surface.set_alpha(alpha)

        # Draw with shadow for visibility
        shadow_offset = 2
        shadow_surface = font.render(text, True, (0, 0, 0))
        if popup.scale != 1.0:
            shadow_surface = pygame.transform.scale(shadow_surface, (new_width, new_height))
        shadow_surface.set_alpha(alpha // 2)

        # Center the text
        x = int(popup.x - text_surface.get_width() // 2)
        y = int(popup.y - text_surface.get_height() // 2)

        screen.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
        screen.blit(text_surface, (x, y))

    def _render_achievement(self, screen: pygame.Surface, achievement: AchievementBanner,
                           index: int) -> None:
        """Render an achievement banner"""
        screen_width = screen.get_width()

        # Banner dimensions
        banner_width = 300
        banner_height = 70
        padding = 15

        # Calculate position (slide from right)
        target_x = screen_width - banner_width - 20
        start_x = screen_width + 20
        current_x = start_x + (target_x - start_x) * self._ease_out(achievement.slide_progress)

        y = 80 + index * (banner_height + 10)

        # Create banner surface
        banner_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)

        # Background with slight transparency
        pygame.draw.rect(banner_surface, (28, 32, 40, 240),
                        (0, 0, banner_width, banner_height),
                        border_radius=12)

        # Left accent bar
        pygame.draw.rect(banner_surface, achievement.color,
                        (0, 0, 4, banner_height),
                        border_top_left_radius=12,
                        border_bottom_left_radius=12)

        # Icon circle
        icon_x = 25
        icon_y = banner_height // 2
        pygame.draw.circle(banner_surface, achievement.color, (icon_x, icon_y), 18)

        # Icon text
        icon_text = self.fonts['medium'].render(achievement.icon, True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(icon_x, icon_y))
        banner_surface.blit(icon_text, icon_rect)

        # Title
        title_text = self.fonts['achievement_title'].render(achievement.title, True, (255, 255, 255))
        banner_surface.blit(title_text, (55, 12))

        # Description
        desc_text = self.fonts['achievement_desc'].render(achievement.description, True, (180, 185, 200))
        banner_surface.blit(desc_text, (55, 38))

        # Border
        pygame.draw.rect(banner_surface, (52, 58, 70),
                        (0, 0, banner_width, banner_height),
                        width=1, border_radius=12)

        # Draw to screen
        screen.blit(banner_surface, (int(current_x), y))

    def _ease_out(self, t: float) -> float:
        """Ease out cubic function for smooth animations"""
        return 1 - pow(1 - t, 3)

    def clear(self) -> None:
        """Clear all popups and achievements"""
        self.popups.clear()
        self.achievements.clear()

    # ==================== Popup Creation Functions ====================

    def add_score(self, x: float, y: float, points: int,
                 positive: bool = True) -> None:
        """Add a score popup (+10, -5, etc.)"""
        if positive:
            text = f"+{points}"
            color = (46, 204, 113)  # Healthcare green
        else:
            text = f"-{points}"
            color = (231, 76, 60)  # Healthcare red

        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=text,
            color=color,
            max_life=1.2,
            font_size='medium',
            start_scale=1.3
        ))

    def add_text(self, x: float, y: float, text: str,
                color: Tuple[int, int, int] = (255, 255, 255),
                size: str = 'medium', duration: float = 1.0) -> None:
        """Add a text popup with custom message"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=text,
            color=color,
            max_life=duration,
            font_size=size,
            start_scale=1.2
        ))

    def add_correct(self, x: float, y: float) -> None:
        """Add a 'Correct!' popup"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="Correct!",
            color=(46, 204, 113),
            max_life=1.0,
            font_size='medium',
            icon="✓",
            start_scale=1.4
        ))

    def add_incorrect(self, x: float, y: float) -> None:
        """Add an 'Incorrect' popup (subtle)"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="Try again",
            color=(231, 76, 60),
            max_life=0.8,
            font_size='small',
            start_scale=1.2
        ))

    def add_complete(self, x: float, y: float) -> None:
        """Add a 'Complete!' popup"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="Complete!",
            color=(46, 204, 113),
            max_life=2.0,
            font_size='large',
            icon="✓",
            start_scale=1.5
        ))

    def add_time_bonus(self, x: float, y: float, bonus: int) -> None:
        """Add a time bonus popup"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=f"Time Bonus +{bonus}",
            color=(243, 156, 18),  # Orange
            max_life=1.5,
            font_size='small',
            icon="⏱",
            start_scale=1.2
        ))

    # ==================== Healthcare-Specific Popups ====================

    def add_approved(self, x: float, y: float) -> None:
        """Add an 'APPROVED' popup for insurance/forms"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="APPROVED!",
            color=(46, 204, 113),  # Green
            max_life=2.0,
            font_size='large',
            icon="✓",
            start_scale=1.8
        ))

    def add_denied(self, x: float, y: float) -> None:
        """Add a 'DENIED' popup"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="DENIED",
            color=(231, 76, 60),  # Red
            max_life=2.0,
            font_size='large',
            icon="✗",
            start_scale=1.6
        ))

    def add_pending(self, x: float, y: float) -> None:
        """Add a 'PENDING' popup"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="PENDING...",
            color=(241, 196, 15),  # Yellow
            max_life=1.5,
            font_size='medium',
            start_scale=1.3
        ))

    def add_savings(self, x: float, y: float, amount: int) -> None:
        """Add a savings popup for medication choices"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=f"Saved ${amount}!",
            color=(46, 204, 113),  # Green
            max_life=1.5,
            font_size='medium',
            icon="$",
            start_scale=1.4
        ))

    def add_anxiety_reduced(self, x: float, y: float, amount: int = 0) -> None:
        """Add anxiety reduction feedback"""
        text = "Anxiety Reduced!" if amount == 0 else f"Anxiety -{amount}%"
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=text,
            color=(46, 204, 113),  # Calming green
            max_life=1.5,
            font_size='medium',
            start_scale=1.3
        ))

    def add_anxiety_increased(self, x: float, y: float, amount: int = 0) -> None:
        """Add anxiety increase warning"""
        text = "Anxiety Increased!" if amount == 0 else f"Anxiety +{amount}%"
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=text,
            color=(231, 76, 60),  # Red
            max_life=1.0,
            font_size='small',
            start_scale=1.2
        ))

    def add_good_timing(self, x: float, y: float) -> None:
        """Add 'Good Timing!' popup for breathing exercise"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="Good Timing!",
            color=(52, 152, 219),  # Blue
            max_life=1.0,
            font_size='medium',
            icon="✓",
            start_scale=1.3
        ))

    def add_mail_found(self, x: float, y: float, mail_type: str = "Important") -> None:
        """Add popup for finding important mail"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=f"{mail_type} Mail Found!",
            color=(231, 76, 60) if mail_type == "Urgent" else (52, 152, 219),
            max_life=1.2,
            font_size='medium',
            icon="!",
            start_scale=1.4
        ))

    def add_sorted(self, x: float, y: float, correct: bool = True) -> None:
        """Add sorting feedback popup"""
        if correct:
            self.popups.append(ScorePopup(
                x=x,
                y=y,
                text="Sorted!",
                color=(46, 204, 113),
                max_life=0.8,
                font_size='small',
                icon="✓",
                start_scale=1.2
            ))
        else:
            self.popups.append(ScorePopup(
                x=x,
                y=y,
                text="Wrong pile",
                color=(231, 76, 60),
                max_life=0.8,
                font_size='small',
                start_scale=1.1
            ))

    # ==================== Achievement Functions ====================

    def add_achievement(self, title: str, description: str,
                       icon: str = "★",
                       color: Tuple[int, int, int] = (243, 156, 18)) -> None:
        """Add an achievement banner"""
        self.achievements.append(AchievementBanner(
            title=title,
            description=description,
            icon=icon,
            color=color,
            max_life=4.0
        ))

    def add_form_submitted(self) -> None:
        """Add Medi-Cal form submission achievement"""
        self.add_achievement(
            title="Application Submitted!",
            description="Medi-Cal form completed",
            icon="📄",
            color=(46, 204, 113)
        )

    def add_coverage_approved(self) -> None:
        """Add insurance coverage approval achievement"""
        self.add_achievement(
            title="Coverage Approved!",
            description="Medi-Cal benefits active",
            icon="✓",
            color=(46, 204, 113)
        )

    def add_coverage_denied(self) -> None:
        """Add insurance denial notification"""
        self.add_achievement(
            title="Coverage Denied",
            description="Additional documents needed",
            icon="!",
            color=(231, 76, 60)
        )

    def add_medication_selected(self, saved: bool = False, amount: int = 0) -> None:
        """Add medication selection achievement"""
        if saved and amount > 0:
            self.add_achievement(
                title="Smart Choice!",
                description=f"Saved ${amount} with generic",
                icon="💊",
                color=(155, 89, 182)  # Purple for generic
            )
        else:
            self.add_achievement(
                title="Medication Selected",
                description="Ready for pickup",
                icon="💊",
                color=(41, 128, 185)
            )

    def add_breathing_complete(self, success: bool = True) -> None:
        """Add breathing exercise completion achievement"""
        if success:
            self.add_achievement(
                title="Calm Restored!",
                description="Anxiety level reduced",
                icon="☮",
                color=(46, 204, 113)
            )
        else:
            self.add_achievement(
                title="Keep Trying",
                description="Match the breathing pattern",
                icon="⚠",
                color=(241, 196, 15)
            )

    def add_bus_caught(self, on_time: bool = True) -> None:
        """Add bus route achievement"""
        if on_time:
            self.add_achievement(
                title="Bus Caught!",
                description="You'll make your appointment",
                icon="🚌",
                color=(46, 204, 113)
            )
        else:
            self.add_achievement(
                title="Wrong Bus!",
                description="This route won't work",
                icon="⚠",
                color=(231, 76, 60)
            )

    def add_mail_sorted(self, found_important: bool = False) -> None:
        """Add mail sorting completion achievement"""
        if found_important:
            self.add_achievement(
                title="Important Mail Found!",
                description="Medi-Cal notice discovered",
                icon="📬",
                color=(231, 76, 60)
            )
        else:
            self.add_achievement(
                title="Mail Sorted",
                description="Inbox organized",
                icon="📬",
                color=(41, 128, 185)
            )

    def add_documents_verified(self) -> None:
        """Add document verification achievement"""
        self.add_achievement(
            title="Documents Verified!",
            description="All requirements met",
            icon="📋",
            color=(46, 204, 113)
        )


# Global instance for easy access
healthcare_feedback = HealthcareFeedbackManager()

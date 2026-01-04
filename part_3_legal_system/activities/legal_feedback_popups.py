"""
Legal System Feedback Popup System
Animated score popups, achievements, and notifications for Part 3 mini-games
Includes legal-themed messages and debt notifications
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
    shake: bool = False  # Add shake effect for errors


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


@dataclass
class DebtNotification:
    """Animated debt change notification"""
    amount: int
    is_increase: bool
    x: float
    y: float
    life: float = 1.0
    max_life: float = 2.0
    scale: float = 1.0


class LegalFeedbackManager:
    """
    Manages animated feedback popups for legal system mini-games
    Provides score popups, achievements, debt notifications, and status messages
    """

    # Legal-themed colors
    LEGAL_PRIMARY = (70, 90, 120)
    LEGAL_GOLD = (212, 175, 55)
    SUCCESS = (72, 187, 120)
    ERROR = (237, 94, 104)
    WARNING = (246, 173, 85)
    URGENT = (198, 40, 40)

    def __init__(self):
        self.popups: List[ScorePopup] = []
        self.achievements: List[AchievementBanner] = []
        self.debt_notifications: List[DebtNotification] = []
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
            self.fonts['debt'] = pygame.font.SysFont('SF Pro Display', 28, bold=True)
        except:
            self.fonts['small'] = pygame.font.Font(None, 20)
            self.fonts['medium'] = pygame.font.Font(None, 28)
            self.fonts['large'] = pygame.font.Font(None, 42)
            self.fonts['achievement_title'] = pygame.font.Font(None, 24)
            self.fonts['achievement_desc'] = pygame.font.Font(None, 18)
            self.fonts['debt'] = pygame.font.Font(None, 32)

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

        # Update debt notifications
        for notification in self.debt_notifications[:]:
            notification.life -= dt / notification.max_life
            if notification.life <= 0:
                self.debt_notifications.remove(notification)
                continue

            # Scale pulse animation
            pulse = abs(math.sin(notification.life * 10)) * 0.1
            notification.scale = 1.0 + pulse

    def render(self, screen: pygame.Surface) -> None:
        """Render all active popups and achievements"""
        # Render score popups
        for popup in self.popups:
            self._render_popup(screen, popup)

        # Render achievements
        for i, achievement in enumerate(self.achievements):
            self._render_achievement(screen, achievement, i)

        # Render debt notifications
        for notification in self.debt_notifications:
            self._render_debt_notification(screen, notification)

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
            if new_width > 0 and new_height > 0:
                text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        # Apply alpha
        text_surface.set_alpha(alpha)

        # Calculate position with optional shake
        x = int(popup.x - text_surface.get_width() // 2)
        y = int(popup.y - text_surface.get_height() // 2)

        if popup.shake and popup.life > 0.7:
            shake_amount = int(5 * (popup.life - 0.7) / 0.3)
            x += pygame.time.get_ticks() % 2 * shake_amount - shake_amount // 2
            y += (pygame.time.get_ticks() + 100) % 2 * shake_amount - shake_amount // 2

        # Draw with shadow for visibility
        shadow_offset = 2
        shadow_surface = font.render(text if not popup.icon else f"{popup.icon} {popup.text}",
                                     True, (0, 0, 0))
        if popup.scale != 1.0 and text_surface.get_width() > 0:
            shadow_surface = pygame.transform.scale(shadow_surface,
                                                    (text_surface.get_width(), text_surface.get_height()))
        shadow_surface.set_alpha(alpha // 2)

        screen.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
        screen.blit(text_surface, (x, y))

    def _render_achievement(self, screen: pygame.Surface, achievement: AchievementBanner,
                           index: int) -> None:
        """Render an achievement banner"""
        screen_width = screen.get_width()

        # Banner dimensions
        banner_width = 320
        banner_height = 75
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
                        (0, 0, 5, banner_height),
                        border_top_left_radius=12,
                        border_bottom_left_radius=12)

        # Icon circle
        icon_x = 30
        icon_y = banner_height // 2
        pygame.draw.circle(banner_surface, achievement.color, (icon_x, icon_y), 20)

        # Icon text
        icon_text = self.fonts['medium'].render(achievement.icon, True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(icon_x, icon_y))
        banner_surface.blit(icon_text, icon_rect)

        # Title
        title_text = self.fonts['achievement_title'].render(achievement.title, True, (255, 255, 255))
        banner_surface.blit(title_text, (60, 14))

        # Description
        desc_text = self.fonts['achievement_desc'].render(achievement.description, True, (180, 185, 200))
        banner_surface.blit(desc_text, (60, 40))

        # Border
        pygame.draw.rect(banner_surface, (52, 58, 70),
                        (0, 0, banner_width, banner_height),
                        width=1, border_radius=12)

        # Draw to screen
        screen.blit(banner_surface, (int(current_x), y))

    def _render_debt_notification(self, screen: pygame.Surface,
                                  notification: DebtNotification) -> None:
        """Render a debt change notification"""
        # Format amount
        if notification.is_increase:
            text = f"+${notification.amount:,}"
            color = self.URGENT
        else:
            text = f"-${notification.amount:,}"
            color = self.SUCCESS

        # Render text with scale
        font = self.fonts['debt']
        text_surface = font.render(text, True, color)

        if notification.scale != 1.0:
            new_width = int(text_surface.get_width() * notification.scale)
            new_height = int(text_surface.get_height() * notification.scale)
            if new_width > 0 and new_height > 0:
                text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        # Alpha based on life
        alpha = int(255 * min(1.0, notification.life * 2))
        text_surface.set_alpha(alpha)

        # Position
        x = int(notification.x - text_surface.get_width() // 2)
        y = int(notification.y - text_surface.get_height() // 2)

        # Shadow
        shadow_surface = font.render(text, True, (0, 0, 0))
        if notification.scale != 1.0:
            shadow_surface = pygame.transform.scale(shadow_surface,
                                                   (text_surface.get_width(), text_surface.get_height()))
        shadow_surface.set_alpha(alpha // 2)

        screen.blit(shadow_surface, (x + 2, y + 2))
        screen.blit(text_surface, (x, y))

    def _ease_out(self, t: float) -> float:
        """Ease out cubic function for smooth animations"""
        return 1 - pow(1 - t, 3)

    def clear(self) -> None:
        """Clear all popups and achievements"""
        self.popups.clear()
        self.achievements.clear()
        self.debt_notifications.clear()

    # ==================== Popup Creation Functions ====================

    def add_score(self, x: float, y: float, points: int,
                 positive: bool = True) -> None:
        """Add a score popup (+10, -5, etc.)"""
        if positive:
            text = f"+{points}"
            color = self.SUCCESS
        else:
            text = f"-{points}"
            color = self.ERROR

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
            color=self.SUCCESS,
            max_life=1.0,
            font_size='medium',
            icon="✓",
            start_scale=1.4
        ))

    def add_incorrect(self, x: float, y: float) -> None:
        """Add an 'Incorrect' popup with shake"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="Wrong pile!",
            color=self.ERROR,
            max_life=0.8,
            font_size='small',
            start_scale=1.2,
            shake=True
        ))

    def add_sorted(self, x: float, y: float, correct: bool) -> None:
        """Add popup for mail sorting result"""
        if correct:
            self.add_correct(x, y)
        else:
            self.add_incorrect(x, y)

    def add_found_important(self, x: float, y: float, label: str) -> None:
        """Add popup when important mail is found"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text=f"{label} Found!",
            color=self.LEGAL_GOLD,
            max_life=1.5,
            font_size='medium',
            icon="📄",
            start_scale=1.4
        ))

    def add_court_summons_found(self, x: float, y: float) -> None:
        """Special dramatic popup for court summons discovery"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="COURT SUMMONS!",
            color=self.URGENT,
            max_life=2.5,
            font_size='large',
            icon="⚠",
            start_scale=1.8,
            shake=True
        ))

    def add_complete(self, x: float, y: float) -> None:
        """Add a 'Complete!' popup"""
        self.popups.append(ScorePopup(
            x=x,
            y=y,
            text="Complete!",
            color=self.SUCCESS,
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
            color=self.LEGAL_GOLD,
            max_life=1.5,
            font_size='small',
            icon="⏱",
            start_scale=1.2
        ))

    # ==================== Debt Notification Functions ====================

    def add_debt_change(self, x: float, y: float, amount: int,
                       is_increase: bool = True) -> None:
        """Add a debt change notification"""
        self.debt_notifications.append(DebtNotification(
            amount=amount,
            is_increase=is_increase,
            x=x,
            y=y,
            max_life=2.0
        ))

    def add_debt_increase(self, x: float, y: float, amount: int) -> None:
        """Add debt increase notification (red, going up)"""
        self.add_debt_change(x, y, amount, is_increase=True)

    def add_debt_decrease(self, x: float, y: float, amount: int) -> None:
        """Add debt decrease notification (green, going down)"""
        self.add_debt_change(x, y, amount, is_increase=False)

    # ==================== Achievement Functions ====================

    def add_achievement(self, title: str, description: str,
                       icon: str = "★",
                       color: Tuple[int, int, int] = None) -> None:
        """Add an achievement banner"""
        if color is None:
            color = self.LEGAL_GOLD

        self.achievements.append(AchievementBanner(
            title=title,
            description=description,
            icon=icon,
            color=color,
            max_life=4.0
        ))

    def add_mail_sorted_achievement(self, found_all: bool) -> None:
        """Add mail sorting completion achievement"""
        if found_all:
            self.add_achievement(
                title="Mail Sorted!",
                description="All important documents found",
                icon="📬",
                color=self.SUCCESS
            )
        else:
            self.add_achievement(
                title="Sorting Complete",
                description="Some mail may have been missed",
                icon="📭",
                color=self.WARNING
            )

    def add_court_summons_achievement(self) -> None:
        """Add court summons discovery achievement (negative)"""
        self.add_achievement(
            title="Court Summons Found",
            description="A legal matter requires attention",
            icon="⚖",
            color=self.URGENT
        )

    def add_note_taking_achievement(self, score: int, max_score: int) -> None:
        """Add note-taking completion achievement"""
        percentage = (score / max_score) * 100 if max_score > 0 else 0

        if percentage >= 90:
            self.add_achievement(
                title="Perfect Notes!",
                description="Despite distractions, you focused",
                icon="📝",
                color=self.LEGAL_GOLD
            )
        elif percentage >= 70:
            self.add_achievement(
                title="Good Notes",
                description=f"{int(percentage)}% accuracy achieved",
                icon="📝",
                color=self.SUCCESS
            )
        else:
            self.add_achievement(
                title="Notes Taken",
                description="Some information was missed",
                icon="📝",
                color=self.WARNING
            )

    def add_breathing_achievement(self, avg_sync: float) -> None:
        """Add breathing exercise achievement"""
        if avg_sync >= 80:
            self.add_achievement(
                title="Stayed Calm",
                description="You kept your composure",
                icon="🧘",
                color=self.SUCCESS
            )
        elif avg_sync >= 50:
            self.add_achievement(
                title="Managed Stress",
                description="Breathing helped, but stress remained",
                icon="🧘",
                color=self.WARNING
            )
        else:
            self.add_achievement(
                title="High Stress",
                description="The encounter was overwhelming",
                icon="😰",
                color=self.ERROR
            )

    def add_document_sorting_achievement(self, errors: int, time_remaining: float) -> None:
        """Add document sorting achievement"""
        if errors == 0 and time_remaining > 20:
            self.add_achievement(
                title="Perfect Sort!",
                description="All documents correctly filed",
                icon="📋",
                color=self.LEGAL_GOLD
            )
        elif errors <= 2:
            self.add_achievement(
                title="Documents Filed",
                description=f"{errors} minor mistakes made",
                icon="📋",
                color=self.SUCCESS
            )
        else:
            self.add_achievement(
                title="Filing Complete",
                description="Several documents were misfiled",
                icon="📋",
                color=self.WARNING
            )


# Global instance for easy access
legal_feedback = LegalFeedbackManager()

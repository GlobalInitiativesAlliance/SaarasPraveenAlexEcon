"""
Feedback Popup System for Part 1 Housing Stability
Animated score popups, achievements, and notifications
Themed for housing/packing/survival scenarios
"""

import pygame
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass


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
    velocity_y: float = -40
    scale: float = 1.0
    start_scale: float = 1.5
    icon: Optional[str] = None


@dataclass
class AchievementBanner:
    """Slide-in achievement banner"""
    title: str
    description: str
    icon: str
    color: Tuple[int, int, int]
    life: float = 1.0
    max_life: float = 3.0
    slide_progress: float = 0.0
    state: str = 'entering'


class Part1FeedbackManager:
    """
    Manages animated feedback popups for Part 1 Housing Stability
    Provides score popups, achievements, and notification toasts
    """

    def __init__(self):
        self.popups: List[ScorePopup] = []
        self.achievements: List[AchievementBanner] = []
        self.fonts = {}
        self._fonts_initialized = False

    def init_fonts(self):
        """Initialize font cache"""
        if self._fonts_initialized:
            return
        try:
            self.fonts['small'] = pygame.font.SysFont('Georgia', 16, bold=True)
            self.fonts['medium'] = pygame.font.SysFont('Georgia', 22, bold=True)
            self.fonts['large'] = pygame.font.SysFont('Georgia', 32, bold=True)
            self.fonts['achievement_title'] = pygame.font.SysFont('Georgia', 18, bold=True)
            self.fonts['achievement_desc'] = pygame.font.SysFont('Georgia', 14)
        except:
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['medium'] = pygame.font.Font(None, 26)
            self.fonts['large'] = pygame.font.Font(None, 38)
            self.fonts['achievement_title'] = pygame.font.Font(None, 22)
            self.fonts['achievement_desc'] = pygame.font.Font(None, 16)
        self._fonts_initialized = True

    def update(self, dt: float) -> None:
        """Update all popups and achievements"""
        # Update score popups
        for popup in self.popups[:]:
            popup.life -= dt / popup.max_life
            if popup.life <= 0:
                self.popups.remove(popup)
                continue

            popup.y += popup.velocity_y * dt

            progress = 1 - popup.life
            if progress < 0.2:
                popup.scale = popup.start_scale - (popup.start_scale - 1.0) * (progress / 0.2)
            else:
                popup.scale = 1.0

        # Update achievements
        for achievement in self.achievements[:]:
            achievement.life -= dt / achievement.max_life
            if achievement.life <= 0:
                self.achievements.remove(achievement)
                continue

            if achievement.state == 'entering':
                achievement.slide_progress = min(1.0, achievement.slide_progress + dt * 5)
                if achievement.slide_progress >= 1.0:
                    achievement.state = 'visible'
            elif achievement.state == 'visible':
                if achievement.life < 0.3:
                    achievement.state = 'exiting'
            elif achievement.state == 'exiting':
                achievement.slide_progress = max(0.0, achievement.slide_progress - dt * 5)

    def render(self, screen: pygame.Surface) -> None:
        """Render all active popups and achievements"""
        self.init_fonts()

        for popup in self.popups:
            self._render_popup(screen, popup)

        for i, achievement in enumerate(self.achievements):
            self._render_achievement(screen, achievement, i)

    def _render_popup(self, screen: pygame.Surface, popup: ScorePopup) -> None:
        """Render a single score popup"""
        alpha = int(255 * min(1.0, popup.life * 2))
        font = self.fonts.get(popup.font_size, self.fonts['medium'])

        text = popup.text
        if popup.icon:
            text = f"{popup.icon} {text}"

        text_surface = font.render(text, True, popup.color)

        if popup.scale != 1.0:
            new_width = int(text_surface.get_width() * popup.scale)
            new_height = int(text_surface.get_height() * popup.scale)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))

        text_surface.set_alpha(alpha)

        # Shadow for visibility
        shadow_offset = 2
        shadow_surface = font.render(text, True, (0, 0, 0))
        if popup.scale != 1.0:
            shadow_surface = pygame.transform.scale(shadow_surface, (new_width, new_height))
        shadow_surface.set_alpha(alpha // 2)

        x = int(popup.x - text_surface.get_width() // 2)
        y = int(popup.y - text_surface.get_height() // 2)

        screen.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
        screen.blit(text_surface, (x, y))

    def _render_achievement(self, screen: pygame.Surface, achievement: AchievementBanner,
                           index: int) -> None:
        """Render an achievement banner"""
        screen_width = screen.get_width()

        banner_width = 280
        banner_height = 65

        target_x = screen_width - banner_width - 20
        start_x = screen_width + 20
        current_x = start_x + (target_x - start_x) * self._ease_out(achievement.slide_progress)
        y = 80 + index * (banner_height + 10)

        banner_surface = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)

        # Warm background (housing theme)
        pygame.draw.rect(banner_surface, (45, 42, 38, 235),
                        (0, 0, banner_width, banner_height),
                        border_radius=10)

        # Left accent bar
        pygame.draw.rect(banner_surface, achievement.color,
                        (0, 0, 4, banner_height),
                        border_top_left_radius=10,
                        border_bottom_left_radius=10)

        # Icon circle
        icon_x = 25
        icon_y = banner_height // 2
        pygame.draw.circle(banner_surface, achievement.color, (icon_x, icon_y), 16)

        # Icon text
        icon_text = self.fonts['medium'].render(achievement.icon, True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(icon_x, icon_y))
        banner_surface.blit(icon_text, icon_rect)

        # Title
        title_text = self.fonts['achievement_title'].render(achievement.title, True, (240, 235, 220))
        banner_surface.blit(title_text, (50, 12))

        # Description
        desc_text = self.fonts['achievement_desc'].render(achievement.description, True, (180, 175, 160))
        banner_surface.blit(desc_text, (50, 35))

        # Border
        pygame.draw.rect(banner_surface, (70, 65, 55),
                        (0, 0, banner_width, banner_height),
                        width=1, border_radius=10)

        screen.blit(banner_surface, (int(current_x), y))

    def _ease_out(self, t: float) -> float:
        """Ease out cubic function"""
        return 1 - pow(1 - t, 3)

    def clear(self) -> None:
        """Clear all popups and achievements"""
        self.popups.clear()
        self.achievements.clear()

    # ==================== Housing-Themed Popup Functions ====================

    def add_item_packed(self, x: float, y: float, item_name: str = "Item") -> None:
        """Add 'Item Packed!' popup"""
        self.popups.append(ScorePopup(
            x=x, y=y,
            text=f"{item_name} packed!",
            color=(134, 168, 133),  # Soft green
            max_life=1.0,
            font_size='medium',
            start_scale=1.3
        ))

    def add_document_found(self, x: float, y: float, doc_name: str = "Document") -> None:
        """Add document found popup"""
        self.popups.append(ScorePopup(
            x=x, y=y,
            text=f"Found: {doc_name}",
            color=(255, 220, 150),  # Golden
            max_life=1.2,
            font_size='medium',
            icon="*",
            start_scale=1.4
        ))

    def add_memory_selected(self, x: float, y: float) -> None:
        """Add memory/photo selection popup"""
        self.popups.append(ScorePopup(
            x=x, y=y,
            text="Memory saved",
            color=(220, 190, 170),  # Warm sepia
            max_life=1.0,
            font_size='small',
            start_scale=1.2
        ))

    def add_progress(self, x: float, y: float, current: int, total: int, label: str = "") -> None:
        """Add progress popup (3/5 items)"""
        text = f"{current}/{total}"
        if label:
            text = f"{label}: {text}"

        color = (134, 168, 133) if current == total else (180, 170, 150)

        self.popups.append(ScorePopup(
            x=x, y=y,
            text=text,
            color=color,
            max_life=1.0,
            font_size='small',
            start_scale=1.2
        ))

    def add_money_change(self, x: float, y: float, amount: float, positive: bool = True) -> None:
        """Add money change popup"""
        if positive:
            text = f"+${amount:.2f}"
            color = (134, 168, 133)
        else:
            text = f"-${abs(amount):.2f}"
            color = (180, 90, 90)

        self.popups.append(ScorePopup(
            x=x, y=y,
            text=text,
            color=color,
            max_life=1.2,
            font_size='medium',
            start_scale=1.3
        ))

    def add_rejection(self, x: float, y: float, reason: str = "Rejected") -> None:
        """Add rejection popup"""
        self.popups.append(ScorePopup(
            x=x, y=y,
            text=reason,
            color=(180, 90, 90),
            max_life=1.5,
            font_size='medium',
            start_scale=1.2
        ))

    def add_success(self, x: float, y: float, text: str = "Success!") -> None:
        """Add general success popup"""
        self.popups.append(ScorePopup(
            x=x, y=y,
            text=text,
            color=(134, 168, 133),
            max_life=1.2,
            font_size='large',
            start_scale=1.5
        ))

    def add_complete(self, x: float, y: float) -> None:
        """Add task complete popup"""
        self.popups.append(ScorePopup(
            x=x, y=y,
            text="Complete!",
            color=(134, 168, 133),
            max_life=1.5,
            font_size='large',
            start_scale=1.5
        ))

    # ==================== Achievement Functions ====================

    def add_achievement(self, title: str, description: str,
                       icon: str = "*",
                       color: Tuple[int, int, int] = (200, 170, 120)) -> None:
        """Add an achievement banner"""
        self.achievements.append(AchievementBanner(
            title=title,
            description=description,
            icon=icon,
            color=color,
            max_life=4.0
        ))

    def add_packing_complete_achievement(self) -> None:
        """Add packing complete achievement"""
        self.add_achievement(
            title="All Packed!",
            description="Everything fits in your bag",
            icon="~",
            color=(134, 168, 133)
        )

    def add_documents_complete_achievement(self, found: int, total: int) -> None:
        """Add documents gathered achievement"""
        if found == total:
            self.add_achievement(
                title="Documents Secured!",
                description="All important papers gathered",
                icon="*",
                color=(200, 170, 120)
            )
        elif found > 0:
            self.add_achievement(
                title="Documents Collected",
                description=f"Found {found} of {total} documents",
                icon="!",
                color=(180, 150, 100)
            )

    def add_photos_selected_achievement(self) -> None:
        """Add photo selection achievement"""
        self.add_achievement(
            title="Memories Saved",
            description="Photos to remember what matters",
            icon="@",
            color=(220, 190, 170)
        )

    def add_housing_found_achievement(self) -> None:
        """Add housing found achievement"""
        self.add_achievement(
            title="Housing Found!",
            description="A place to stay, for now...",
            icon="#",
            color=(134, 168, 133)
        )

    def add_job_found_achievement(self) -> None:
        """Add job achievement"""
        self.add_achievement(
            title="Job Secured!",
            description="Income to help cover costs",
            icon="$",
            color=(200, 170, 120)
        )

    def add_survival_achievement(self, days: int) -> None:
        """Add survival milestone achievement"""
        self.add_achievement(
            title=f"{days} Days Survived",
            description="Still fighting for stability",
            icon="+",
            color=(101, 128, 156)
        )

    def add_tlp_acceptance_achievement(self) -> None:
        """Add TLP program acceptance achievement"""
        self.add_achievement(
            title="TLP Accepted!",
            description="Transitional housing secured",
            icon="^",
            color=(134, 168, 133)
        )

    def add_leaving_foster_care_achievement(self) -> None:
        """Add aging out achievement (bittersweet)"""
        self.add_achievement(
            title="On Your Own",
            description="The system says you're an adult now",
            icon="<",
            color=(160, 140, 130)
        )


# Global instance for easy access
part1_feedback = Part1FeedbackManager()

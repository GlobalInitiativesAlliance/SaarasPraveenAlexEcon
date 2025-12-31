"""
Career Matching Mini-Game
Match career fields with their training length
Counselor dialogue task

UPGRADED: Professional cards with shadows, animated drop zones,
placement particles, and career icons
"""
import pygame
import math
import time

from .education_visual_base import (
    EducationUIColors, EducationUIMetrics, EducationVisualHelpers,
    EducationVisualComponents, UIAnimation, education_visuals
)
from .particle_effects import ParticleSystem
from .feedback_popups import FeedbackPopupManager


class CareerMatchingGame:
    """Drag careers to match with training duration categories"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Career items with icons
        self.careers = [
            {'name': 'Electrician', 'correct_category': 'trade', 'placed': False, 'icon': '⚡'},
            {'name': 'Nurse (RN)', 'correct_category': 'associate', 'placed': False, 'icon': '🏥'},
            {'name': 'Software Engineer', 'correct_category': 'bachelor', 'placed': False, 'icon': '💻'},
            {'name': 'Dental Hygienist', 'correct_category': 'associate', 'placed': False, 'icon': '🦷'},
            {'name': 'Plumber', 'correct_category': 'trade', 'placed': False, 'icon': '🔧'},
            {'name': 'Teacher', 'correct_category': 'bachelor', 'placed': False, 'icon': '📚'},
            {'name': 'HVAC Technician', 'correct_category': 'trade', 'placed': False, 'icon': '❄️'},
            {'name': 'Medical Assistant', 'correct_category': 'certificate', 'placed': False, 'icon': '💉'},
            {'name': 'Accountant', 'correct_category': 'bachelor', 'placed': False, 'icon': '📊'},
            {'name': 'Phlebotomist', 'correct_category': 'certificate', 'placed': False, 'icon': '🩸'},
        ]

        # Training categories with icons and colors
        self.categories = [
            {'id': 'certificate', 'label': 'Certificate', 'duration': '6 months',
             'rect': None, 'careers': [], 'icon': '📜', 'color': (246, 173, 85)},
            {'id': 'trade', 'label': 'Trade School', 'duration': '1-2 years',
             'rect': None, 'careers': [], 'icon': '🔨', 'color': (237, 94, 104)},
            {'id': 'associate', 'label': "Associate's", 'duration': '2 years',
             'rect': None, 'careers': [], 'icon': '🎓', 'color': (72, 156, 118)},
            {'id': 'bachelor', 'label': "Bachelor's", 'duration': '4 years',
             'rect': None, 'careers': [], 'icon': '🏛️', 'color': (56, 123, 203)},
        ]

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.drag_start_pos = None

        # Scoring
        self.correct_placements = 0
        self.total_careers = len(self.careers)

        # Visual systems
        self.particles = ParticleSystem()
        self.popups = FeedbackPopupManager()
        self.visuals = education_visuals

        # Animations
        self.card_animations = {}  # Card ID -> animation state
        self.zone_highlights = {}  # Zone ID -> highlight intensity
        self.entrance_animation = UIAnimation(0, 1, speed=0.08)

        # Create UI elements (after initializing animation dicts)
        self.create_career_cards()
        self.create_category_zones()

        # Feedback
        self.show_feedback = False
        self.feedback_timer = 0
        self.feedback_scale = UIAnimation(0.5, 1.0, speed=0.15)

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.font_category = pygame.font.SysFont('SF Pro Display', 18, bold=True)
            self.font_duration = pygame.font.SysFont('SF Pro Text', 14)
            self.font_career = pygame.font.SysFont('SF Pro Text', 16)
            self.font_small = pygame.font.SysFont('SF Pro Text', 14)
            self.font_icon = pygame.font.SysFont('Segoe UI Emoji', 20)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_category = pygame.font.Font(None, 22)
            self.font_duration = pygame.font.Font(None, 16)
            self.font_career = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 16)
            self.font_icon = pygame.font.Font(None, 24)

    def create_career_cards(self):
        """Create draggable career cards"""
        start_x = 60
        start_y = 160

        for i, career in enumerate(self.careers):
            col = i % 2
            row = i // 2
            x = start_x + (col * 170)
            y = start_y + (row * 55)
            career['rect'] = pygame.Rect(x, y, 155, 45)
            career['original_pos'] = (x, y)
            career['hover'] = False
            career['glow_alpha'] = 0

    def create_category_zones(self):
        """Create drop zones for categories"""
        zone_width = 200
        zone_height = 220
        start_x = 480
        start_y = 140
        gap = 20

        for i, category in enumerate(self.categories):
            col = i % 2
            row = i // 2
            x = start_x + (col * (zone_width + gap))
            y = start_y + (row * (zone_height + gap))
            category['rect'] = pygame.Rect(x, y, zone_width, zone_height)
            self.zone_highlights[category['id']] = 0

    def handle_event(self, event):
        """Handle drag and drop interactions"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicking on a career card
            for career in self.careers:
                if not career['placed'] and career['rect'].collidepoint(mouse_pos):
                    self.dragging = career
                    self.drag_offset = (
                        career['rect'].x - mouse_pos[0],
                        career['rect'].y - mouse_pos[1]
                    )
                    self.drag_start_pos = (career['rect'].x, career['rect'].y)

                    # Emit paper trail
                    self.particles.emit_paper_trail(mouse_pos[0], mouse_pos[1])
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in a category zone
                placed = False
                for category in self.categories:
                    if category['rect'].colliderect(self.dragging['rect']):
                        # Place in category
                        self.dragging['placed'] = True
                        self.dragging['placed_category'] = category['id']
                        category['careers'].append(self.dragging)

                        # Check if correct
                        is_correct = category['id'] == self.dragging['correct_category']
                        if is_correct:
                            self.correct_placements += 1
                            self.particles.emit_success(
                                self.dragging['rect'].centerx,
                                self.dragging['rect'].centery
                            )
                            self.popups.add_score(
                                self.dragging['rect'].centerx,
                                self.dragging['rect'].y - 15, 10
                            )
                            self.dragging['glow_alpha'] = 255
                            self.dragging['glow_color'] = EducationUIColors.VERIFIED
                        else:
                            self.particles.emit_error(
                                self.dragging['rect'].centerx,
                                self.dragging['rect'].centery
                            )
                            self.dragging['glow_alpha'] = 255
                            self.dragging['glow_color'] = EducationUIColors.BLOCKED

                        placed = True
                        break

                if not placed:
                    # Return to original position with animation
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Reset zone highlights
                for zone_id in self.zone_highlights:
                    self.zone_highlights[zone_id] = 0

                # Check for completion
                if all(career['placed'] for career in self.careers):
                    self.show_feedback = True
                    self.feedback_timer = 180
                    self.feedback_scale = UIAnimation(0.5, 1.0, speed=0.15)
                    self.completed = True

                    # Achievement based on score
                    self.popups.add_career_match_achievement(
                        self.correct_placements, self.total_careers
                    )

                    # Celebration particles
                    if self.correct_placements >= 8:
                        center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
                        self.particles.emit_confetti(center[0], center[1], 40)

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

                # Emit trail particles occasionally
                if int(time.time() * 10) % 3 == 0:
                    self.particles.emit_paper_trail(mouse_pos[0], mouse_pos[1], 2)

                # Update zone highlights
                for category in self.categories:
                    if category['rect'].colliderect(self.dragging['rect']):
                        self.zone_highlights[category['id']] = min(1.0,
                            self.zone_highlights[category['id']] + 0.1)
                    else:
                        self.zone_highlights[category['id']] = max(0,
                            self.zone_highlights[category['id']] - 0.1)

            # Update hover states
            for career in self.careers:
                if not career['placed']:
                    career['hover'] = career['rect'].collidepoint(mouse_pos)

        return True

    def update(self, dt):
        """Update game state and animations"""
        if not self.active:
            return

        # Update entrance animation
        self.entrance_animation.update(dt)

        # Update particles and popups
        self.particles.update(dt)
        self.popups.update(dt)

        # Update feedback animation
        if self.show_feedback:
            self.feedback_scale.update(dt)
            if self.feedback_timer > 0:
                self.feedback_timer -= 1

        # Update card glow animations
        for career in self.careers:
            if career.get('glow_alpha', 0) > 0:
                career['glow_alpha'] = max(0, career['glow_alpha'] - dt * 200)

        # Update zone highlight animations
        for zone_id in self.zone_highlights:
            if self.dragging is None:
                self.zone_highlights[zone_id] = max(0,
                    self.zone_highlights[zone_id] - dt * 3)

    def render(self, screen):
        """Render the career matching interface"""
        if not self.active:
            return

        # Background gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = EducationVisualHelpers.interpolate_color(
                (240, 242, 248), (225, 230, 240), progress
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Title area
        self._render_header(screen)

        # Score panel
        self._render_score_panel(screen)

        # Category zones (render first, behind cards)
        for category in self.categories:
            self._render_category_zone(screen, category)

        # Career cards (unplaced ones)
        for career in self.careers:
            if not career['placed'] and career != self.dragging:
                self._render_career_card(screen, career)

        # Dragging card (on top)
        if self.dragging:
            self._render_career_card(screen, self.dragging, is_dragging=True)

        # Instructions
        if not self.show_feedback:
            inst_text = self.font_small.render(
                "Drag each career to its training duration category",
                True, EducationUIColors.TEXT_MUTED
            )
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2,
                                   self.SCREEN_HEIGHT - 35))

        # Feedback modal
        if self.show_feedback:
            self._render_feedback(screen)

        # Particles and popups (always on top)
        self.particles.render(screen)
        self.popups.render(screen)

    def _render_header(self, screen):
        """Render the title and counselor context"""
        # Title
        title_text = self.font_title.render("Career Planning", True,
                                           EducationUIColors.EDUCATION_PRIMARY)
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 25))

        # Subtitle
        subtitle = self.font_small.render("Match careers with their education requirements",
                                         True, EducationUIColors.TEXT_SECONDARY)
        screen.blit(subtitle, (self.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 65))

        # Counselor badge
        badge_rect = pygame.Rect(40, 20, 140, 35)
        pygame.draw.rect(screen, EducationUIColors.PANEL_BG, badge_rect,
                        border_radius=badge_rect.height // 2)
        badge_text = self.font_small.render("With Counselor", True,
                                           EducationUIColors.TEXT_LIGHT)
        screen.blit(badge_text, (badge_rect.centerx - badge_text.get_width() // 2,
                                badge_rect.centery - badge_text.get_height() // 2))

    def _render_score_panel(self, screen):
        """Render the score panel"""
        panel_rect = pygame.Rect(self.SCREEN_WIDTH - 150, 100, 130, 100)

        # Panel shadow
        EducationVisualHelpers.draw_shadow(screen, panel_rect, 4, 30,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Panel background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, panel_rect,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, panel_rect, 1,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Score header
        header_text = self.font_small.render("Progress", True, EducationUIColors.TEXT_MUTED)
        screen.blit(header_text, (panel_rect.centerx - header_text.get_width() // 2,
                                 panel_rect.y + 10))

        # Placed count
        placed_count = sum(1 for c in self.careers if c['placed'])
        count_text = self.font_title.render(f"{placed_count}/{self.total_careers}",
                                           True, EducationUIColors.EDUCATION_PRIMARY)
        screen.blit(count_text, (panel_rect.centerx - count_text.get_width() // 2,
                                panel_rect.y + 35))

        # Correct count
        correct_text = self.font_small.render(f"{self.correct_placements} correct",
                                             True, EducationUIColors.VERIFIED)
        screen.blit(correct_text, (panel_rect.centerx - correct_text.get_width() // 2,
                                  panel_rect.y + 75))

    def _render_category_zone(self, screen, category):
        """Render a category drop zone"""
        rect = category['rect']
        highlight = self.zone_highlights.get(category['id'], 0)

        # Glow effect when highlighted
        if highlight > 0:
            glow_rect = rect.inflate(int(12 * highlight), int(12 * highlight))
            glow_color = (*category['color'], int(80 * highlight))
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color,
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=EducationUIMetrics.RADIUS_LARGE + 6)
            screen.blit(glow_surface, glow_rect.topleft)

        # Zone shadow
        EducationVisualHelpers.draw_shadow(screen, rect, 5, 40,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Zone background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Header with category color
        header_height = 45
        header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_height)
        pygame.draw.rect(screen, category['color'], header_rect,
                        border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

        # Category icon and name
        icon_text = self.font_icon.render(category['icon'], True, (255, 255, 255))
        screen.blit(icon_text, (rect.x + 10, rect.y + 10))

        label_text = self.font_category.render(category['label'], True, (255, 255, 255))
        screen.blit(label_text, (rect.x + 40, rect.y + 8))

        duration_text = self.font_duration.render(category['duration'], True, (255, 255, 255, 200))
        screen.blit(duration_text, (rect.x + 40, rect.y + 26))

        # Capacity indicator
        capacity = 3
        placed = len(category['careers'])
        cap_text = self.font_small.render(f"{placed}/{capacity}", True, (255, 255, 255, 180))
        screen.blit(cap_text, (rect.right - 35, rect.y + 13))

        # Placed careers list
        y_offset = header_height + 10
        for placed_career in category['careers']:
            is_correct = placed_career['correct_category'] == category['id']
            color = EducationUIColors.VERIFIED if is_correct else EducationUIColors.BLOCKED

            # Small career tag
            tag_rect = pygame.Rect(rect.x + 10, rect.y + y_offset, rect.width - 20, 26)
            pygame.draw.rect(screen, (*color, 30), tag_rect,
                            border_radius=EducationUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, color, tag_rect, 1,
                            border_radius=EducationUIMetrics.RADIUS_SMALL)

            # Icon and name
            career_icon = self.font_small.render(placed_career['icon'], True, color)
            screen.blit(career_icon, (tag_rect.x + 5, tag_rect.y + 4))

            career_text = self.font_small.render(placed_career['name'], True, color)
            screen.blit(career_text, (tag_rect.x + 25, tag_rect.y + 5))

            # Checkmark or X
            if is_correct:
                self.visuals.draw_checkmark(screen, (tag_rect.right - 15, tag_rect.centery), 8, color)
            else:
                self.visuals.draw_x_mark(screen, (tag_rect.right - 15, tag_rect.centery), 8, color)

            y_offset += 32

        # Border
        border_color = category['color'] if highlight > 0 else EducationUIColors.PANEL_BORDER
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def _render_career_card(self, screen, career, is_dragging=False):
        """Render a career card with professional styling"""
        rect = career['rect']

        # Shadow (larger when dragging)
        shadow_offset = 8 if is_dragging else 3
        shadow_alpha = 80 if is_dragging else 40
        EducationVisualHelpers.draw_shadow(screen, rect, shadow_offset, shadow_alpha,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Glow effect
        if career.get('glow_alpha', 0) > 0:
            glow_color = career.get('glow_color', EducationUIColors.VERIFIED)
            glow_rect = rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, int(career['glow_alpha'] * 0.5)),
                           (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=EducationUIMetrics.RADIUS_MEDIUM + 4)
            screen.blit(glow_surface, glow_rect.topleft)

        # Card background
        if is_dragging:
            bg_color = (230, 240, 255)
            border_color = EducationUIColors.EDUCATION_PRIMARY
        elif career.get('hover'):
            bg_color = (250, 252, 255)
            border_color = EducationUIColors.EDUCATION_SECONDARY
        else:
            bg_color = EducationUIColors.PAPER_BG
            border_color = EducationUIColors.PANEL_BORDER

        pygame.draw.rect(screen, bg_color, rect,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Icon
        icon_text = self.font_icon.render(career['icon'], True, EducationUIColors.TEXT_PRIMARY)
        screen.blit(icon_text, (rect.x + 8, rect.centery - icon_text.get_height() // 2))

        # Career name
        name_text = self.font_career.render(career['name'], True, EducationUIColors.TEXT_PRIMARY)
        screen.blit(name_text, (rect.x + 35, rect.centery - name_text.get_height() // 2))

    def _render_feedback(self, screen):
        """Render the completion feedback modal"""
        scale = self.feedback_scale.value

        # Modal dimensions
        modal_width = int(500 * scale)
        modal_height = int(220 * scale)
        modal_x = (self.SCREEN_WIDTH - modal_width) // 2
        modal_y = (self.SCREEN_HEIGHT - modal_height) // 2

        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Modal shadow
        EducationVisualHelpers.draw_shadow(screen, modal_rect, 10, 80,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Modal background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, modal_rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Score display
        score_text = self.font_title.render(
            f"{self.correct_placements}/{self.total_careers} Correct!",
            True, EducationUIColors.EDUCATION_PRIMARY
        )
        screen.blit(score_text, (modal_rect.centerx - score_text.get_width() // 2,
                                modal_y + 30))

        # Message based on score
        if self.correct_placements >= 8:
            message = "Excellent! You understand education pathways well."
            color = EducationUIColors.VERIFIED
        elif self.correct_placements >= 6:
            message = "Good job! Consider exploring all your options."
            color = EducationUIColors.PENDING
        else:
            message = "Let's review these career paths together."
            color = EducationUIColors.BLOCKED

        msg_text = self.font_career.render(message, True, color)
        screen.blit(msg_text, (modal_rect.centerx - msg_text.get_width() // 2,
                              modal_y + 90))

        # Trade school note
        note_rect = pygame.Rect(modal_x + 30, modal_y + 130, modal_width - 60, 40)
        pygame.draw.rect(screen, (240, 248, 255), note_rect,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)
        pygame.draw.rect(screen, EducationUIColors.EDUCATION_PRIMARY, note_rect, 1,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)

        note_text = self.font_small.render("Trade school tour added to your map!",
                                          True, EducationUIColors.EDUCATION_PRIMARY)
        screen.blit(note_text, (note_rect.centerx - note_text.get_width() // 2,
                               note_rect.centery - note_text.get_height() // 2))

        # Border
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, modal_rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the career matching game"""
        self.active = True
        self.completed = False
        self.show_feedback = False
        self.feedback_timer = 0
        self.correct_placements = 0
        self.entrance_animation = UIAnimation(0, 1, speed=0.08)

        # Reset careers
        for career in self.careers:
            career['placed'] = False
            career['hover'] = False
            career['glow_alpha'] = 0
            career['rect'].x = career['original_pos'][0]
            career['rect'].y = career['original_pos'][1]

        # Clear categories
        for category in self.categories:
            category['careers'] = []

        # Reset zone highlights
        for zone_id in self.zone_highlights:
            self.zone_highlights[zone_id] = 0

        # Clear effects
        self.particles.clear()
        self.popups.clear()

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False

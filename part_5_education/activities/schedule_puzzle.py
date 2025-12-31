"""
Schedule Puzzle Mini-Game
Rearrange schedule to fit work and orientation
Visual calendar puzzle

UPGRADED: Professional calendar styling, gradient blocks,
animated drag effects, and result modals
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


class SchedulePuzzleGame:
    """Drag and rearrange schedule blocks to fit both commitments"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.failed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Time blocks with icons and gradients
        self.schedule_blocks = [
            {'name': 'Work Shift', 'duration': 4, 'color': (255, 150, 100),
             'color_dark': (220, 120, 80), 'moveable': True, 'required': True, 'icon': '💼'},
            {'name': 'Orientation', 'duration': 2, 'color': (100, 150, 255),
             'color_dark': (70, 120, 220), 'moveable': False, 'required': True,
             'fixed_time': 11, 'icon': '🎓'},
            {'name': 'Class', 'duration': 2, 'color': (150, 220, 150),
             'color_dark': (120, 190, 120), 'moveable': True, 'required': False, 'icon': '📚'},
            {'name': 'Study Time', 'duration': 2, 'color': (255, 220, 130),
             'color_dark': (220, 190, 100), 'moveable': True, 'required': False, 'icon': '📝'},
        ]

        # Calendar grid (8am to 8pm = 12 hours)
        self.calendar_hours = list(range(8, 20))
        self.grid_start_x = 180
        self.grid_start_y = 280
        self.hour_width = 75
        self.block_height = 80

        # Placed blocks
        self.placed_blocks = {}

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)

        # Create block rectangles
        self.create_block_rects()

        # Solution check
        self.solution_valid = False
        self.check_button = pygame.Rect(540, 550, 200, 50)
        self.button_hover = False
        self.button_scale = 1.0

        # Visual systems
        self.particles = ParticleSystem()
        self.popups = FeedbackPopupManager()
        self.visuals = education_visuals

        # Animations
        self.result_visible = False
        self.result_scale = UIAnimation(0.5, 1.0, speed=0.15)
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 36, bold=True)
            self.font_time = pygame.font.SysFont('SF Pro Text', 14)
            self.font_block = pygame.font.SysFont('SF Pro Display', 16, bold=True)
            self.font_duration = pygame.font.SysFont('SF Pro Text', 12)
            self.font_small = pygame.font.SysFont('SF Pro Text', 14)
            self.font_button = pygame.font.SysFont('SF Pro Display', 18, bold=True)
            self.font_result = pygame.font.SysFont('SF Pro Display', 28, bold=True)
            self.font_icon = pygame.font.SysFont('Segoe UI Emoji', 18)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_time = pygame.font.Font(None, 16)
            self.font_block = pygame.font.Font(None, 20)
            self.font_duration = pygame.font.Font(None, 14)
            self.font_small = pygame.font.Font(None, 16)
            self.font_button = pygame.font.Font(None, 22)
            self.font_result = pygame.font.Font(None, 32)
            self.font_icon = pygame.font.Font(None, 22)

    def create_block_rects(self):
        """Create visual rectangles for schedule blocks"""
        # Position blocks on left side as draggable items
        start_x = 80
        start_y = 160

        for i, block in enumerate(self.schedule_blocks):
            width = block['duration'] * self.hour_width
            height = 55
            y = start_y + (i * 70)
            rect = pygame.Rect(start_x, y, width, height)
            block['rect'] = rect
            block['original_rect'] = rect.copy()
            block['placed'] = False
            block['hover'] = False

            # Pre-place orientation at 11am
            if block.get('fixed_time'):
                hour_index = block['fixed_time'] - 8
                block['rect'].x = self.grid_start_x + (hour_index * self.hour_width)
                block['rect'].y = self.grid_start_y
                block['rect'].height = self.block_height
                block['placed'] = True
                for h in range(block['fixed_time'], block['fixed_time'] + block['duration']):
                    self.placed_blocks[h] = block

    def handle_event(self, event):
        """Handle schedule block dragging"""
        if not self.active or self.completed:
            return False

        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button click
            if self.check_button.collidepoint(mouse_pos):
                self.check_solution()
                return True

            # Check block dragging
            for block in self.schedule_blocks:
                if block['moveable'] and block['rect'].collidepoint(mouse_pos):
                    self.dragging = block
                    self.drag_offset = (
                        block['rect'].x - mouse_pos[0],
                        block['rect'].y - mouse_pos[1]
                    )

                    # Remove from placed blocks if already placed
                    if block['placed']:
                        hours_to_remove = []
                        for hour, placed_block in self.placed_blocks.items():
                            if placed_block == block:
                                hours_to_remove.append(hour)
                        for hour in hours_to_remove:
                            del self.placed_blocks[hour]
                        block['placed'] = False

                    # Emit paper trail
                    self.particles.emit_paper_trail(mouse_pos[0], mouse_pos[1])
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                grid_y = self.grid_start_y
                if abs(self.dragging['rect'].y - grid_y) < 60:
                    # Find closest hour slot
                    closest_hour = None
                    min_dist = float('inf')

                    for i, hour in enumerate(self.calendar_hours):
                        slot_x = self.grid_start_x + (i * self.hour_width)
                        dist = abs(self.dragging['rect'].x - slot_x)
                        if dist < min_dist:
                            min_dist = dist
                            closest_hour = hour

                    if closest_hour and min_dist < self.hour_width:
                        # Check if space is available
                        can_place = True
                        for h in range(closest_hour, min(closest_hour + self.dragging['duration'], 20)):
                            if h in self.placed_blocks and self.placed_blocks[h] != self.dragging:
                                can_place = False
                                break

                        if can_place and closest_hour + self.dragging['duration'] <= 20:
                            # Place block with snap animation
                            hour_index = closest_hour - 8
                            self.dragging['rect'].x = self.grid_start_x + (hour_index * self.hour_width)
                            self.dragging['rect'].y = grid_y
                            self.dragging['rect'].height = self.block_height
                            self.dragging['placed'] = True

                            # Mark hours as occupied
                            for h in range(closest_hour, closest_hour + self.dragging['duration']):
                                self.placed_blocks[h] = self.dragging

                            # Success particles
                            self.particles.emit_success(
                                self.dragging['rect'].centerx,
                                self.dragging['rect'].centery
                            )
                        else:
                            # Return to original position
                            self._return_to_original(self.dragging)
                    else:
                        self._return_to_original(self.dragging)
                else:
                    if not self.dragging['placed']:
                        self._return_to_original(self.dragging)

                self.dragging = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

                # Emit trail particles occasionally
                if int(time.time() * 10) % 4 == 0:
                    self.particles.emit_paper_trail(mouse_pos[0], mouse_pos[1], 2)

            # Update button hover
            self.button_hover = self.check_button.collidepoint(mouse_pos)

            # Update block hover states
            for block in self.schedule_blocks:
                if block['moveable'] and not block['placed']:
                    block['hover'] = block['rect'].collidepoint(mouse_pos)

        return True

    def _return_to_original(self, block):
        """Return block to original position"""
        block['rect'] = block['original_rect'].copy()
        block['placed'] = False

    def check_solution(self):
        """Check if all required blocks are placed without conflicts"""
        work_placed = False
        orientation_placed = False

        for block in self.schedule_blocks:
            if block['required'] and block['placed']:
                if block['name'] == 'Work Shift':
                    work_placed = True
                elif block['name'] == 'Orientation':
                    orientation_placed = True

        self.solution_valid = work_placed and orientation_placed
        self.result_visible = True
        self.result_scale = UIAnimation(0.5, 1.0, speed=0.15)
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)

        if self.solution_valid:
            # Success celebration
            center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
            self.particles.emit_confetti(center[0], center[1], 40)
            self.popups.add_schedule_complete_achievement(True)
            self.popups.add_complete(center[0], center[1] - 50)
        else:
            self.popups.add_schedule_complete_achievement(False)

        self.completed = True
        self.failed = not self.solution_valid

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update particles and popups
        self.particles.update(dt)
        self.popups.update(dt)

        # Update button scale
        target_scale = 1.05 if self.button_hover else 1.0
        self.button_scale += (target_scale - self.button_scale) * 0.2

        # Update result animations
        if self.result_visible:
            self.result_scale.update(dt)
            self.result_alpha.update(dt)

    def render(self, screen):
        """Render the schedule puzzle interface"""
        if not self.active:
            return

        # Background gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = EducationVisualHelpers.interpolate_color(
                (235, 240, 250), (220, 228, 240), progress
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        # Title
        self._render_header(screen)

        # Calendar grid
        self._render_calendar(screen)

        # Schedule blocks (unplaced, in sidebar)
        for block in self.schedule_blocks:
            if not block['placed'] and block != self.dragging:
                self._render_block_sidebar(screen, block)

        # Placed blocks on calendar
        for block in self.schedule_blocks:
            if block['placed'] and block != self.dragging:
                self._render_block_calendar(screen, block)

        # Dragging block (on top)
        if self.dragging:
            self._render_block_dragging(screen, self.dragging)

        # Check button
        self._render_check_button(screen)

        # Instructions
        if not self.result_visible:
            inst_text = self.font_small.render(
                "Drag blocks to schedule. Orientation at 11am is MANDATORY!",
                True, EducationUIColors.BLOCKED
            )
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 100))

        # Result modal
        if self.result_visible:
            self._render_result(screen)

        # Particles and popups
        self.particles.render(screen)
        self.popups.render(screen)

    def _render_header(self, screen):
        """Render title area"""
        title_text = self.font_title.render("Schedule Puzzle", True,
                                           EducationUIColors.EDUCATION_PRIMARY)
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 25))

        subtitle = self.font_small.render("Fit work and orientation into your day",
                                         True, EducationUIColors.TEXT_SECONDARY)
        screen.blit(subtitle, (self.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 65))

    def _render_calendar(self, screen):
        """Render the calendar grid"""
        # Calendar container
        container_rect = pygame.Rect(
            self.grid_start_x - 20,
            self.grid_start_y - 50,
            len(self.calendar_hours) * self.hour_width + 40,
            self.block_height + 80
        )

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, container_rect, 6, 40,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, container_rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Time labels row
        for i, hour in enumerate(self.calendar_hours):
            x = self.grid_start_x + (i * self.hour_width)

            # Alternating header backgrounds
            header_rect = pygame.Rect(x, self.grid_start_y - 35, self.hour_width, 30)
            bg_color = (245, 247, 252) if i % 2 == 0 else (238, 242, 248)
            pygame.draw.rect(screen, bg_color, header_rect)

            # Time label
            time_str = self._format_hour(hour)
            time_text = self.font_time.render(time_str, True, EducationUIColors.TEXT_SECONDARY)
            screen.blit(time_text, (x + self.hour_width // 2 - time_text.get_width() // 2,
                                   self.grid_start_y - 28))

        # Grid cells
        mouse_pos = pygame.mouse.get_pos()
        for i, hour in enumerate(self.calendar_hours):
            x = self.grid_start_x + (i * self.hour_width)
            cell_rect = pygame.Rect(x, self.grid_start_y, self.hour_width, self.block_height)

            is_occupied = hour in self.placed_blocks
            is_hovered = self.dragging and cell_rect.collidepoint(mouse_pos)

            # Cell background
            if is_occupied:
                continue  # Block will be rendered on top
            elif is_hovered:
                bg_color = (*EducationUIColors.EDUCATION_PRIMARY, 30)
                cell_surface = pygame.Surface((self.hour_width, self.block_height), pygame.SRCALPHA)
                cell_surface.fill(bg_color)
                screen.blit(cell_surface, (x, self.grid_start_y))
            else:
                bg_color = (252, 252, 255) if i % 2 == 0 else (248, 250, 254)
                pygame.draw.rect(screen, bg_color, cell_rect)

            # Grid lines
            pygame.draw.rect(screen, (210, 215, 225), cell_rect, 1)

        # Border
        grid_rect = pygame.Rect(
            self.grid_start_x,
            self.grid_start_y,
            len(self.calendar_hours) * self.hour_width,
            self.block_height
        )
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, grid_rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)

        # Container border
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, container_rect, 1,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def _format_hour(self, hour):
        """Format hour for display"""
        if hour == 12:
            return "12 PM"
        elif hour > 12:
            return f"{hour - 12} PM"
        else:
            return f"{hour} AM"

    def _render_block_sidebar(self, screen, block):
        """Render a block in the sidebar (not placed)"""
        rect = block['rect']

        # Shadow
        shadow_offset = 5 if block.get('hover') else 3
        EducationVisualHelpers.draw_shadow(screen, rect, shadow_offset, 40,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Gradient background
        EducationVisualHelpers.draw_gradient_rect(
            screen, rect, block['color'], block['color_dark'],
            EducationUIMetrics.RADIUS_MEDIUM
        )

        # Border
        border_color = (255, 255, 255) if block.get('hover') else EducationVisualHelpers.darken_color(block['color'], 0.8)
        pygame.draw.rect(screen, border_color, rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Icon
        icon_text = self.font_icon.render(block['icon'], True, (255, 255, 255))
        screen.blit(icon_text, (rect.x + 8, rect.centery - icon_text.get_height() // 2))

        # Name
        name_text = self.font_block.render(block['name'], True, (255, 255, 255))
        screen.blit(name_text, (rect.x + 35, rect.y + 10))

        # Duration
        dur_text = self.font_duration.render(f"{block['duration']}h", True, (255, 255, 255, 200))
        screen.blit(dur_text, (rect.x + 35, rect.y + 30))

        # Required indicator
        if block['required']:
            req_text = self.font_duration.render("Required", True, (255, 255, 255, 180))
            screen.blit(req_text, (rect.right - 55, rect.centery - 6))

    def _render_block_calendar(self, screen, block):
        """Render a block placed on the calendar"""
        rect = block['rect']

        # Gradient background
        EducationVisualHelpers.draw_gradient_rect(
            screen, rect, block['color'], block['color_dark'],
            EducationUIMetrics.RADIUS_SMALL
        )

        # Border
        pygame.draw.rect(screen, EducationVisualHelpers.darken_color(block['color'], 0.7),
                        rect, 2, border_radius=EducationUIMetrics.RADIUS_SMALL)

        # Icon
        icon_text = self.font_icon.render(block['icon'], True, (255, 255, 255))
        screen.blit(icon_text, (rect.x + 10, rect.y + 10))

        # Name (centered)
        name_text = self.font_block.render(block['name'], True, (255, 255, 255))
        screen.blit(name_text, (rect.centerx - name_text.get_width() // 2, rect.centery - 15))

        # Duration badge
        badge_rect = pygame.Rect(rect.right - 35, rect.bottom - 25, 30, 20)
        pygame.draw.rect(screen, (0, 0, 0, 80), badge_rect,
                        border_radius=EducationUIMetrics.RADIUS_SMALL)
        dur_text = self.font_duration.render(f"{block['duration']}h", True, (255, 255, 255))
        screen.blit(dur_text, (badge_rect.centerx - dur_text.get_width() // 2,
                              badge_rect.centery - dur_text.get_height() // 2))

        # Fixed indicator
        if not block['moveable']:
            fixed_text = self.font_duration.render("FIXED", True, (255, 200, 200))
            screen.blit(fixed_text, (rect.x + 10, rect.bottom - 20))

    def _render_block_dragging(self, screen, block):
        """Render a block being dragged"""
        rect = block['rect']

        # Larger shadow
        EducationVisualHelpers.draw_shadow(screen, rect, 10, 80,
                                          EducationUIMetrics.RADIUS_MEDIUM)

        # Gradient background with slight transparency
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            progress = y / max(rect.height - 1, 1)
            r = int(block['color'][0] + (block['color_dark'][0] - block['color'][0]) * progress)
            g = int(block['color'][1] + (block['color_dark'][1] - block['color'][1]) * progress)
            b = int(block['color'][2] + (block['color_dark'][2] - block['color'][2]) * progress)
            pygame.draw.line(surface, (r, g, b, 230), (0, y), (rect.width, y))

        screen.blit(surface, rect.topleft)

        # Bright border
        pygame.draw.rect(screen, (255, 255, 255), rect, 3,
                        border_radius=EducationUIMetrics.RADIUS_MEDIUM)

        # Icon
        icon_text = self.font_icon.render(block['icon'], True, (255, 255, 255))
        screen.blit(icon_text, (rect.x + 10, rect.y + 10))

        # Name
        name_text = self.font_block.render(block['name'], True, (255, 255, 255))
        screen.blit(name_text, (rect.centerx - name_text.get_width() // 2,
                               rect.centery - name_text.get_height() // 2))

    def _render_check_button(self, screen):
        """Render the check schedule button"""
        # Calculate scaled rect
        width = int(200 * self.button_scale)
        height = int(50 * self.button_scale)
        x = self.SCREEN_WIDTH // 2 - width // 2
        y = 550 - (height - 50) // 2

        scaled_rect = pygame.Rect(x, y, width, height)

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, scaled_rect, 4, 40,
                                          scaled_rect.height // 2)

        # Button gradient
        color = EducationUIColors.EDUCATION_PRIMARY if self.button_hover else EducationUIColors.BUTTON_DEFAULT
        pygame.draw.rect(screen, color, scaled_rect, border_radius=scaled_rect.height // 2)

        # Text
        btn_text = self.font_button.render("Check Schedule", True, EducationUIColors.TEXT_LIGHT)
        screen.blit(btn_text, (scaled_rect.centerx - btn_text.get_width() // 2,
                              scaled_rect.centery - btn_text.get_height() // 2))

        # Update actual button rect for click detection
        self.check_button = scaled_rect

    def _render_result(self, screen):
        """Render result modal"""
        scale = self.result_scale.value
        alpha = self.result_alpha.value

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(150 * alpha)))
        screen.blit(overlay, (0, 0))

        # Modal dimensions
        modal_width = int(480 * scale)
        modal_height = int(180 * scale)
        modal_x = (self.SCREEN_WIDTH - modal_width) // 2
        modal_y = (self.SCREEN_HEIGHT - modal_height) // 2

        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

        # Shadow
        EducationVisualHelpers.draw_shadow(screen, modal_rect, 10, 80,
                                          EducationUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, EducationUIColors.PAPER_BG, modal_rect,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

        # Header strip
        header_color = EducationUIColors.VERIFIED if self.solution_valid else EducationUIColors.BLOCKED
        header_rect = pygame.Rect(modal_x, modal_y, modal_width, 55)
        pygame.draw.rect(screen, header_color, header_rect,
                        border_top_left_radius=EducationUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=EducationUIMetrics.RADIUS_LARGE)

        # Result title
        if self.solution_valid:
            title = "Schedule Complete!"
            icon = "✓"
        else:
            title = "Schedule Failed"
            icon = "✗"

        title_text = self.font_result.render(f"{icon} {title}", True, EducationUIColors.TEXT_LIGHT)
        screen.blit(title_text, (modal_rect.centerx - title_text.get_width() // 2, modal_y + 12))

        # Message
        if self.solution_valid:
            msg = "You can attend both work and orientation!"
            msg_color = EducationUIColors.VERIFIED
        else:
            msg = "Place both Work Shift and Orientation to proceed."
            msg_color = EducationUIColors.BLOCKED

        msg_text = self.font_small.render(msg, True, msg_color)
        screen.blit(msg_text, (modal_rect.centerx - msg_text.get_width() // 2, modal_y + 85))

        # Consequence text
        if self.solution_valid:
            consequence = "Your enrollment is confirmed!"
        else:
            consequence = "Course enrollment will be delayed!"

        cons_text = self.font_small.render(consequence, True, EducationUIColors.TEXT_SECONDARY)
        screen.blit(cons_text, (modal_rect.centerx - cons_text.get_width() // 2, modal_y + 120))

        # Border
        pygame.draw.rect(screen, EducationUIColors.PANEL_BORDER, modal_rect, 2,
                        border_radius=EducationUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the schedule puzzle game"""
        self.active = True
        self.completed = False
        self.failed = False
        self.solution_valid = False
        self.placed_blocks = {}
        self.result_visible = False
        self.create_block_rects()

        # Clear effects
        self.particles.clear()
        self.popups.clear()

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

    def stop(self):
        """Stop the mini-game"""
        self.active = False

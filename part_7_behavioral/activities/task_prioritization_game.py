"""
Task Prioritization Mini-Game
Floating tasks overwhelm the screen - prioritize them before the timer runs out
Demonstrates decision paralysis and task overwhelm
"""
import pygame
import random
import math
import time

from .behavioral_visual_base import (
    BehavioralUIColors, BehavioralUIMetrics, UIAnimation,
    BehavioralVisualHelpers, behavioral_visuals
)
from .behavioral_particles import behavioral_particles


class TaskPrioritizationGame:
    """Prioritize floating tasks under time pressure"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Timer
        self.time_limit = 30.0  # seconds
        self.time_remaining = self.time_limit

        # Tasks that float around
        self.tasks = [
            {'name': 'College Application', 'urgency': 'HIGH', 'prioritized': False},
            {'name': 'Work Shift Tomorrow', 'urgency': 'HIGH', 'prioritized': False},
            {'name': 'Pay Electric Bill', 'urgency': 'MEDIUM', 'prioritized': False},
            {'name': 'Grocery Shopping', 'urgency': 'MEDIUM', 'prioritized': False},
            {'name': 'Call Case Worker', 'urgency': 'MEDIUM', 'prioritized': False},
            {'name': 'Laundry', 'urgency': 'LOW', 'prioritized': False},
            {'name': 'Clean Apartment', 'urgency': 'LOW', 'prioritized': False},
            {'name': 'Text Friend Back', 'urgency': 'LOW', 'prioritized': False},
        ]

        # Priority slots
        self.priority_slots = [
            {'label': '#1 Priority', 'rect': None, 'task': None},
            {'label': '#2 Priority', 'rect': None, 'task': None},
            {'label': '#3 Priority', 'rect': None, 'task': None},
        ]

        # Dragging state
        self.dragging = None
        self.drag_offset = (0, 0)
        self.hover_task = None
        self.hover_slot = None

        # Animation
        self.float_offsets = []
        self.float_speeds = []
        self.float_amplitudes = []

        # Result state
        self.show_result = False
        self.result_timer = 0
        self.result_animation = UIAnimation(0, 0, 0.08)
        self.success = False

        # Overwhelm effects
        self.overwhelm_level = UIAnimation(0.3, 0.3, 0.1)
        self.last_particle_time = 0
        self.time_warning_emitted = False

        # Initialize positions
        self.initialize_tasks()

    def initialize_tasks(self):
        """Create floating task positions"""
        self.float_offsets = []
        self.float_speeds = []
        self.float_amplitudes = []

        for i, task in enumerate(self.tasks):
            # Random starting position in left area
            x = random.randint(80, 480)
            y = random.randint(160, 520)
            task['rect'] = pygame.Rect(x, y, BehavioralUIMetrics.TASK_CARD_WIDTH,
                                       BehavioralUIMetrics.TASK_CARD_HEIGHT)
            task['original_pos'] = (x, y)
            task['hover_animation'] = UIAnimation(0, 0, 0.2)

            # Random float pattern
            self.float_offsets.append(random.uniform(0, math.pi * 2))
            self.float_speeds.append(random.uniform(0.015, 0.04))
            self.float_amplitudes.append((random.uniform(10, 20), random.uniform(8, 15)))

        # Priority slot positions
        slot_x = 920
        slot_y = 180
        for i, slot in enumerate(self.priority_slots):
            slot['rect'] = pygame.Rect(slot_x, slot_y + i * 130, 280, 100)

    def handle_event(self, event):
        """Handle task dragging"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.completed = True
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            for task in self.tasks:
                if not task['prioritized'] and task['rect'].collidepoint(mouse_pos):
                    self.dragging = task
                    self.drag_offset = (
                        task['rect'].x - mouse_pos[0],
                        task['rect'].y - mouse_pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                # Check if dropped in a priority slot
                placed = False
                for slot in self.priority_slots:
                    if slot['task'] is None and slot['rect'].colliderect(self.dragging['rect']):
                        slot['task'] = self.dragging
                        self.dragging['prioritized'] = True
                        # Center in slot
                        self.dragging['rect'].center = slot['rect'].center
                        placed = True

                        # Success particles
                        behavioral_particles.emit_task_complete(
                            self.dragging['rect'].centerx,
                            self.dragging['rect'].centery
                        )
                        break

                if not placed:
                    # Return to floating
                    self.dragging['rect'].x = self.dragging['original_pos'][0]
                    self.dragging['rect'].y = self.dragging['original_pos'][1]

                self.dragging = None

                # Check if all slots filled
                if all(slot['task'] is not None for slot in self.priority_slots):
                    self.trigger_result()

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()

            if self.dragging:
                self.dragging['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.dragging['rect'].y = mouse_pos[1] + self.drag_offset[1]

                # Check hover over slots
                self.hover_slot = None
                for slot in self.priority_slots:
                    if slot['task'] is None and slot['rect'].collidepoint(mouse_pos):
                        self.hover_slot = slot
                        break
            else:
                # Update hover state for tasks
                self.hover_task = None
                for task in self.tasks:
                    if not task['prioritized'] and task['rect'].collidepoint(mouse_pos):
                        self.hover_task = task
                        break

                self.hover_slot = None

        return True

    def trigger_result(self):
        """Show the result"""
        self.show_result = True
        self.result_timer = 240
        self.result_animation.target = 1.0

        # Check if high urgency tasks were prioritized
        high_urgency_prioritized = 0
        for slot in self.priority_slots:
            if slot['task'] and slot['task']['urgency'] == 'HIGH':
                high_urgency_prioritized += 1

        self.success = high_urgency_prioritized >= 1

        if self.success:
            behavioral_particles.emit_success_burst(self.SCREEN_WIDTH // 2, 350)
        else:
            behavioral_particles.emit_stress_burst(self.SCREEN_WIDTH // 2, 350, 1.5)

    def update(self, dt):
        """Update game state"""
        if not self.active:
            return

        # Update animations
        self.result_animation.update(dt)
        self.overwhelm_level.update(dt)
        behavioral_particles.update(dt)

        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True
            return

        # Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.show_result = True
            self.success = False
            self.result_timer = 240
            self.result_animation.target = 1.0
            behavioral_particles.emit_stress_burst(self.SCREEN_WIDTH // 2, 350, 2.0)
            return

        # Time warning particles
        if self.time_remaining < 10 and not self.time_warning_emitted:
            self.time_warning_emitted = True
        if self.time_remaining < 8 and time.time() - self.last_particle_time > 0.5:
            behavioral_particles.emit_time_warning(self.SCREEN_WIDTH // 2, 95)
            self.last_particle_time = time.time()

        # Update floating animation for unprioritized tasks
        for i, task in enumerate(self.tasks):
            if not task['prioritized'] and task != self.dragging:
                self.float_offsets[i] += self.float_speeds[i]
                amp_x, amp_y = self.float_amplitudes[i]
                offset_x = math.sin(self.float_offsets[i]) * amp_x
                offset_y = math.cos(self.float_offsets[i] * 0.7) * amp_y
                task['rect'].x = task['original_pos'][0] + offset_x
                task['rect'].y = task['original_pos'][1] + offset_y

            # Update hover animations
            if task == self.hover_task:
                task['hover_animation'].target = 1.0
            else:
                task['hover_animation'].target = 0.0
            task['hover_animation'].update(dt)

        # Update overwhelm level based on remaining tasks
        unprioritized = sum(1 for t in self.tasks if not t['prioritized'])
        self.overwhelm_level.target = min(1.0, unprioritized / 8 + (1 - self.time_remaining / self.time_limit) * 0.3)

        # Overwhelm particles when high
        if self.overwhelm_level.value > 0.6 and time.time() - self.last_particle_time > 0.8:
            behavioral_particles.emit_overwhelm_cloud(400, 350, 300)
            self.last_particle_time = time.time()

    def render(self, screen):
        """Render the task prioritization interface"""
        if not self.active:
            return

        # Background with overwhelm-based tint
        overwhelm_val = self.overwhelm_level.value
        time_factor = max(0, 1 - (self.time_remaining / self.time_limit))

        bg_color = BehavioralVisualHelpers.interpolate_color(
            BehavioralUIColors.BG_CALM,
            BehavioralUIColors.BG_ANXIOUS,
            overwhelm_val * 0.4 + time_factor * 0.3
        )
        screen.fill(bg_color)

        # Title
        self._draw_title(screen)

        # Timer
        self._draw_timer(screen)

        if not self.show_result:
            # Instruction
            behavioral_visuals.draw_instruction_text(
                screen, "Drag the 3 most important tasks to priority slots",
                self.SCREEN_WIDTH // 2, 130
            )

            # Overwhelm indicator
            self._draw_overwhelm_indicator(screen)

            # Priority slots
            self._draw_priority_slots(screen)

            # Floating tasks
            self._draw_tasks(screen)

        else:
            self._draw_result(screen)

        # Draw particles on top
        behavioral_particles.draw(screen)

    def _draw_title(self, screen):
        """Draw the game title"""
        title_text = behavioral_visuals.fonts['title'].render(
            "Prioritize Your Tasks!", True, BehavioralUIColors.TEXT_PRIMARY
        )
        # Shadow
        shadow_text = behavioral_visuals.fonts['title'].render(
            "Prioritize Your Tasks!", True, (0, 0, 0)
        )
        shadow_surf = pygame.Surface(shadow_text.get_size(), pygame.SRCALPHA)
        shadow_surf.blit(shadow_text, (0, 0))
        shadow_surf.set_alpha(30)
        screen.blit(shadow_surf, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 32))
        screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

    def _draw_timer(self, screen):
        """Draw the countdown timer"""
        timer_center = (self.SCREEN_WIDTH // 2, 95)
        behavioral_visuals.draw_countdown_timer(
            screen, timer_center,
            self.time_remaining, self.time_limit,
            radius=35
        )

    def _draw_overwhelm_indicator(self, screen):
        """Draw the overwhelm/task count indicator"""
        unprioritized = sum(1 for t in self.tasks if not t['prioritized'])

        if unprioritized > 4:
            # Draw overwhelm text with pulsing effect
            pulse = abs(math.sin(time.time() * 2)) * 0.3
            alpha = int(180 + pulse * 75)

            text = f"{unprioritized} tasks competing for attention..."
            text_surface = behavioral_visuals.fonts['small'].render(
                text, True, BehavioralUIColors.STRESS_RED
            )
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (180, 590))

    def _draw_priority_slots(self, screen):
        """Render the priority slots"""
        for slot in self.priority_slots:
            is_highlighted = (slot == self.hover_slot and
                            slot['task'] is None and
                            self.dragging is not None)

            behavioral_visuals.draw_priority_slot(
                screen, slot['rect'],
                slot['label'],
                is_filled=slot['task'] is not None,
                is_highlighted=is_highlighted
            )

            # Show task name if placed
            if slot['task']:
                task_text = behavioral_visuals.fonts['body'].render(
                    slot['task']['name'], True, BehavioralUIColors.TEXT_PRIMARY
                )
                text_x = slot['rect'].centerx - task_text.get_width() // 2
                screen.blit(task_text, (text_x, slot['rect'].centery - 10))

                # Urgency badge
                urgency = slot['task']['urgency']
                if urgency == 'HIGH':
                    badge_color = BehavioralUIColors.STRESS_RED
                elif urgency == 'MEDIUM':
                    badge_color = BehavioralUIColors.ANXIETY_ORANGE
                else:
                    badge_color = BehavioralUIColors.CALM_BLUE

                urgency_text = behavioral_visuals.fonts['tiny'].render(
                    urgency, True, badge_color
                )
                screen.blit(urgency_text, (text_x, slot['rect'].centery + 12))

    def _draw_tasks(self, screen):
        """Render floating task cards"""
        # Draw non-dragging tasks first
        for task in self.tasks:
            if not task['prioritized'] and task != self.dragging:
                self._draw_task_card(screen, task)

        # Draw dragging task on top
        if self.dragging:
            self._draw_task_card(screen, self.dragging)

    def _draw_task_card(self, screen, task):
        """Draw a single task card"""
        is_dragging = task == self.dragging
        is_hover = task == self.hover_task and not is_dragging

        behavioral_visuals.draw_task_card(
            screen, task['rect'],
            task['name'], task['urgency'],
            is_dragging, is_hover, task['prioritized']
        )

    def _draw_result(self, screen):
        """Render the result screen"""
        anim_progress = self.result_animation.value

        panel_width = 700
        panel_height = 380
        panel_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - panel_width // 2,
            int(170 + (1 - anim_progress) * 50),
            panel_width,
            panel_height
        )

        # Determine header
        if self.success:
            header_text = "You managed to prioritize!"
            header_color = BehavioralUIColors.DECISION_GREEN
        else:
            if self.time_remaining <= 0:
                header_text = "Time ran out - too many tasks!"
            else:
                header_text = "Important tasks were missed"
            header_color = BehavioralUIColors.STRESS_RED

        # Draw modal
        behavioral_visuals.draw_modal_container(
            screen, panel_rect,
            header_text,
            header_color,
            self.success
        )

        # Show priorities
        y = panel_rect.y + 80
        priority_label = behavioral_visuals.fonts['body_bold'].render(
            "Your priorities:", True, BehavioralUIColors.TEXT_SECONDARY
        )
        screen.blit(priority_label, (panel_rect.x + 50, y))
        y += 35

        for i, slot in enumerate(self.priority_slots):
            if slot['task']:
                urgency = slot['task']['urgency']
                if urgency == 'HIGH':
                    color = BehavioralUIColors.STRESS_RED
                elif urgency == 'MEDIUM':
                    color = BehavioralUIColors.ANXIETY_ORANGE
                else:
                    color = BehavioralUIColors.CALM_BLUE

                # Number badge
                num_rect = pygame.Rect(panel_rect.x + 60, y - 2, 28, 28)
                pygame.draw.rect(screen, color, num_rect, border_radius=14)
                num_text = behavioral_visuals.fonts['small_bold'].render(
                    str(i + 1), True, BehavioralUIColors.TEXT_LIGHT
                )
                screen.blit(num_text, (num_rect.centerx - num_text.get_width() // 2,
                                       num_rect.centery - num_text.get_height() // 2))

                # Task info
                text = f"{slot['task']['name']}"
                slot_text = behavioral_visuals.fonts['body'].render(text, True,
                                                                    BehavioralUIColors.TEXT_PRIMARY)
                screen.blit(slot_text, (panel_rect.x + 100, y))

                urgency_text = behavioral_visuals.fonts['tiny'].render(
                    f"({urgency})", True, color
                )
                screen.blit(urgency_text, (panel_rect.x + 100 + slot_text.get_width() + 10, y + 3))
            else:
                text = f"#{i + 1}: (empty)"
                slot_text = behavioral_visuals.fonts['body'].render(
                    text, True, BehavioralUIColors.TEXT_MUTED
                )
                screen.blit(slot_text, (panel_rect.x + 60, y))
            y += 32

        # Commentary
        y = panel_rect.y + 260
        comments = [
            "When everything feels urgent, nothing gets done.",
            "Decision paralysis is real for foster youth managing alone."
        ]

        for comment in comments:
            comment_surface = behavioral_visuals.fonts['body'].render(
                comment, True, BehavioralUIColors.TEXT_SECONDARY
            )
            comment_x = panel_rect.centerx - comment_surface.get_width() // 2
            screen.blit(comment_surface, (comment_x, y))
            y += 28

        # Continue prompt
        if self.result_timer < 180:
            behavioral_visuals.draw_continue_prompt(
                screen, panel_rect.centerx, panel_rect.bottom - 25
            )

    def start(self):
        """Start the task prioritization game"""
        self.active = True
        self.completed = False
        self.show_result = False
        self.success = False
        self.time_remaining = self.time_limit
        self.result_timer = 0
        self.result_animation = UIAnimation(0, 0, 0.08)
        self.overwhelm_level = UIAnimation(0.3, 0.3, 0.1)
        self.time_warning_emitted = False
        self.last_particle_time = 0
        self.dragging = None
        self.hover_task = None
        self.hover_slot = None

        # Reset tasks
        for task in self.tasks:
            task['prioritized'] = False
            task['rect'].x = task['original_pos'][0]
            task['rect'].y = task['original_pos'][1]
            task['hover_animation'] = UIAnimation(0, 0, 0.2)

        # Reset slots
        for slot in self.priority_slots:
            slot['task'] = None

        # Randomize positions
        self.initialize_tasks()

        # Clear particles
        behavioral_particles.clear()

    def stop(self):
        """Stop the mini-game"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

"""
Choice Dialogue System for Part 9 - Clean Version
Handles multiple forced choice scenarios about time conflicts
Clean visuals, no heavy effects
"""
import pygame
import math

from .time_visual_base import (
    PressureUIColors, PressureUIMetrics, PressureVisualHelpers,
    pressure_visuals
)
from .time_particles import time_particles
from .time_feedback import time_feedback


class ChoiceDialoguePart9:
    """Choice-based dialogue system for Part 9 - Clean version"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Scenarios with choices and urgency colors
        self.scenarios = {
            'choose_one': {
                'title': 'Choose One Priority',
                'prompt': 'You can only attend ONE. Choose:',
                'context': [
                    "All three events are at the same time.",
                    "Missing any of them has consequences."
                ],
                'urgency': 'high',
                'choices': [
                    {
                        'text': 'Go to work (3pm shift)',
                        'icon': 'W',
                        'color': PressureUIColors.TIME_GOLD,
                        'result': 'You earned wages today.',
                        'consequence': 'Program progress lost. Benefits at risk.',
                        'positive': True
                    },
                    {
                        'text': 'Go to program meeting',
                        'icon': 'P',
                        'color': PressureUIColors.CALM_BLUE_LIGHT,
                        'result': 'Benefits protected.',
                        'consequence': 'Fired from job. No income.',
                        'positive': True
                    },
                    {
                        'text': 'Go to therapy session',
                        'icon': 'T',
                        'color': PressureUIColors.STRESS_PURPLE_LIGHT,
                        'result': 'Mental health improved.',
                        'consequence': 'Rent money decreases. Job warning.',
                        'positive': True
                    }
                ]
            },
            'teacher_choice': {
                'title': 'Tell Your Teacher?',
                'prompt': 'Court date is during your midterm exam:',
                'context': [
                    "You have a court summons for next Tuesday.",
                    "That's the same day as your midterm."
                ],
                'urgency': 'medium',
                'choices': [
                    {
                        'text': 'Tell the teacher honestly',
                        'icon': 'H',
                        'color': PressureUIColors.CALM_BLUE_LIGHT,
                        'result': 'Teacher is understanding.',
                        'consequence': 'But you still lose the exam grade. No makeup offered.',
                        'positive': False
                    },
                    {
                        'text': 'Skip class silently',
                        'icon': 'S',
                        'color': PressureUIColors.URGENT_ORANGE,
                        'result': 'You avoid the awkward conversation.',
                        'consequence': 'Academic probation warning arrives in mail.',
                        'positive': False
                    }
                ]
            },
            'housing_vs_work': {
                'title': 'Housing vs Work',
                'prompt': 'Case manager meeting OR work shift at 2pm:',
                'context': [
                    "Your housing case manager needs to see you at 2pm.",
                    "Your work shift is also at 2pm.",
                    "You cannot be in two places at once."
                ],
                'urgency': 'high',
                'choices': [
                    {
                        'text': 'Attend case manager meeting',
                        'icon': 'H',
                        'color': PressureUIColors.URGENT_ORANGE,
                        'result': 'Housing secured.',
                        'consequence': 'Missed work. FIRED.',
                        'positive': False
                    },
                    {
                        'text': 'Go to work shift',
                        'icon': 'W',
                        'color': PressureUIColors.TIME_GOLD,
                        'result': 'Income secured.',
                        'consequence': '30-day placement at risk notice received.',
                        'positive': False
                    }
                ]
            }
        }

        # Current state
        self.current_scenario = None
        self.scenario_data = None
        self.selected_index = -1
        self.show_result = False
        self.result_timer = 0
        self.time = 0

        # Hover state
        self.hovered_choice = -1

        # Track what was chosen
        self.choice_made = None

    def set_scenario(self, scenario_id):
        """Set the current scenario"""
        if scenario_id in self.scenarios:
            self.current_scenario = scenario_id
            self.scenario_data = self.scenarios[scenario_id]

    def start(self):
        """Start the dialogue"""
        self.active = True
        self.completed = False
        self.selected_index = -1
        self.show_result = False
        self.result_timer = 0
        self.hovered_choice = -1
        self.choice_made = None
        self.time = 0

        # Clear feedback
        time_particles.clear()
        time_feedback.clear()

        # Set stress based on urgency
        if self.scenario_data:
            urgency = self.scenario_data.get('urgency', 'medium')
            if urgency == 'high':
                time_feedback.set_stress_level(0.5)
            else:
                time_feedback.set_stress_level(0.3)

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        self.time += dt

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.5:
                self.completed = True
                self.active = False

        # Update feedback
        time_feedback.update(dt)

    def handle_event(self, event):
        """Handle input events"""
        if not self.active or self.show_result or not self.scenario_data:
            return

        choices = self.scenario_data['choices']

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_choice = -1

            # Check hover on choice boxes
            choice_y = 290
            for i in range(len(choices)):
                choice_rect = pygame.Rect(140, choice_y + i * 85, 520, 70)
                if choice_rect.collidepoint(pos):
                    self.hovered_choice = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            choice_y = 290
            for i in range(len(choices)):
                choice_rect = pygame.Rect(140, choice_y + i * 85, 520, 70)
                if choice_rect.collidepoint(pos):
                    self.select_choice(i)
                    break

        elif event.type == pygame.KEYDOWN:
            # Number keys
            if event.key == pygame.K_1 and len(choices) >= 1:
                self.select_choice(0)
            elif event.key == pygame.K_2 and len(choices) >= 2:
                self.select_choice(1)
            elif event.key == pygame.K_3 and len(choices) >= 3:
                self.select_choice(2)

    def select_choice(self, index):
        """Select a choice"""
        if not self.scenario_data:
            return

        choices = self.scenario_data['choices']
        if 0 <= index < len(choices):
            self.selected_index = index
            self.show_result = True
            self.choice_made = choices[index]['text']

            choice = choices[index]

            # Consequence feedback
            if not choice.get('positive', True):
                time_feedback.add_consequence_banner(
                    positive=False,
                    text="Every choice has a cost..."
                )
            else:
                time_feedback.add_consequence_banner(
                    positive=True,
                    text="Choice made."
                )

    def render(self, screen):
        """Render the dialogue with clean visuals"""
        if not self.scenario_data:
            return

        # Background with stress tint
        urgency = self.scenario_data.get('urgency', 'medium')
        stress_level = 0.5 if urgency == 'high' else 0.3
        pressure_visuals.draw_background(screen, stress_level if not self.show_result else 0.4)

        # Title
        pressure_visuals.draw_title(screen, self.scenario_data['title'],
                                    self.SCREEN_WIDTH // 2, 45)

        # Context lines
        context_y = 100
        for i, line in enumerate(self.scenario_data['context']):
            text_surf = pressure_visuals.fonts['body'].render(
                line, True, PressureUIColors.TEXT_SECONDARY
            )
            screen.blit(text_surf, (150, context_y + i * 28))

        # Prompt with warning color
        prompt_color = PressureUIColors.URGENT_ORANGE if urgency == 'high' else PressureUIColors.TEXT_PRIMARY
        prompt_surf = pressure_visuals.fonts['heading'].render(
            self.scenario_data['prompt'], True, prompt_color
        )
        screen.blit(prompt_surf,
                   (self.SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, 240))

        # Choices
        choices = self.scenario_data['choices']
        choice_y = 290

        for i, choice in enumerate(choices):
            self._render_choice(screen, choice, i, choice_y + i * 85)

        # Show result
        if self.show_result and self.selected_index >= 0:
            self._render_result(screen, choices)

        # Render feedback on top
        time_feedback.render(screen)

    def _render_choice(self, screen, choice, index, y):
        """Render a single choice panel"""
        rect = pygame.Rect(140, y, 520, 70)

        is_selected = (self.show_result and index == self.selected_index)
        is_hover = (index == self.hovered_choice)
        is_unchosen = (self.show_result and index != self.selected_index)

        # Background color
        if is_selected:
            bg_color = PressureUIColors.PANEL_BG_LIGHT
        elif is_unchosen:
            bg_color = tuple(c // 2 for c in PressureUIColors.PANEL_BG)
        elif is_hover:
            bg_color = PressureUIColors.PANEL_BG_LIGHT
        else:
            bg_color = PressureUIColors.PANEL_BG

        # Draw panel
        pygame.draw.rect(screen, bg_color, rect, border_radius=10)

        # Border color
        choice_color = choice.get('color', PressureUIColors.CALM_BLUE)
        if is_selected:
            border_color = PressureUIColors.TIME_GOLD
        elif is_unchosen:
            border_color = PressureUIColors.PRESSURE_RED_DARK
        elif is_hover:
            border_color = choice_color
        else:
            border_color = PressureUIColors.BORDER_DEFAULT

        border_width = 3 if is_selected else 2
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=10)

        # Icon circle
        icon_x = rect.x + 35
        icon_y = rect.centery
        icon_color = choice_color if not is_unchosen else PressureUIColors.TEXT_MUTED

        if is_unchosen:
            # Draw X over unchosen
            pygame.draw.circle(screen, (60, 50, 50), (icon_x, icon_y), 20)
            pygame.draw.line(screen, PressureUIColors.PRESSURE_RED,
                           (icon_x - 8, icon_y - 8), (icon_x + 8, icon_y + 8), 3)
            pygame.draw.line(screen, PressureUIColors.PRESSURE_RED,
                           (icon_x + 8, icon_y - 8), (icon_x - 8, icon_y + 8), 3)
        else:
            pygame.draw.circle(screen, icon_color, (icon_x, icon_y), 20)
            icon_text = pressure_visuals.fonts['body_bold'].render(
                choice.get('icon', str(index + 1)), True, PressureUIColors.DARK_BG
            )
            screen.blit(icon_text, (icon_x - icon_text.get_width() // 2,
                                    icon_y - icon_text.get_height() // 2))

        # Choice number
        num_color = PressureUIColors.TEXT_PRIMARY if is_hover else PressureUIColors.TEXT_MUTED
        if is_unchosen:
            num_color = (80, 70, 70)
        num_text = pressure_visuals.fonts['body'].render(f"[{index + 1}]", True, num_color)
        screen.blit(num_text, (rect.x + 60, rect.centery - num_text.get_height() // 2))

        # Choice text
        text_color = PressureUIColors.TEXT_PRIMARY if (is_hover or is_selected) else PressureUIColors.TEXT_SECONDARY
        if is_unchosen:
            text_color = (100, 90, 90)

        text_surface = pressure_visuals.fonts['body'].render(choice['text'], True, text_color)
        screen.blit(text_surface, (rect.x + 100, rect.centery - text_surface.get_height() // 2))

        # Warning indicator for all choices (no good options)
        if not self.show_result:
            pulse = PressureVisualHelpers.get_pulse_alpha(150, 255, 3.0)
            warning_size = 6
            warning_color = (*PressureUIColors.URGENT_ORANGE, pulse)
            warning_surf = pygame.Surface((warning_size * 2, warning_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(warning_surf, warning_color, (warning_size, warning_size), warning_size)
            screen.blit(warning_surf, (rect.right - 25 - warning_size, rect.centery - warning_size))

    def _render_result(self, screen, choices):
        """Render the result panel"""
        choice = choices[self.selected_index]

        # Result panel position
        result_y = 290 + len(choices) * 85 + 15
        result_rect = pygame.Rect(100, result_y, 600, 110)

        # Determine if positive or negative
        is_positive = choice.get('positive', True)
        border_color = PressureUIColors.CALM_BLUE if is_positive else PressureUIColors.PRESSURE_RED

        # Fade in effect
        alpha_progress = min(1.0, self.result_timer / 0.5)

        # Draw result panel
        pygame.draw.rect(screen, PressureUIColors.PANEL_BG, result_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, result_rect, 2, border_radius=10)

        # Result text
        result_color = PressureUIColors.TIME_GOLD if is_positive else PressureUIColors.CALM_BLUE_LIGHT
        result_surface = pressure_visuals.fonts['body_bold'].render(
            choice['result'], True, result_color
        )
        result_surface.set_alpha(int(255 * alpha_progress))
        screen.blit(result_surface,
                   (result_rect.centerx - result_surface.get_width() // 2, result_rect.y + 30))

        # Consequence (appears after delay)
        if self.result_timer > 0.8:
            cons_progress = min(1.0, (self.result_timer - 0.8) / 0.5)
            cons_alpha = int(255 * cons_progress)

            # Consequence always has a cost
            cons_color = PressureUIColors.PRESSURE_RED_LIGHT
            cons_surface = pressure_visuals.fonts['body'].render(
                choice['consequence'], True, cons_color
            )
            cons_surface.set_alpha(cons_alpha)
            screen.blit(cons_surface,
                       (result_rect.centerx - cons_surface.get_width() // 2, result_rect.y + 65))

        # "No good options" indicator
        if self.result_timer > 2.0:
            no_good_alpha = min(200, int((self.result_timer - 2.0) * 150))
            no_good_text = pressure_visuals.fonts['small'].render(
                "Every choice has consequences.", True, PressureUIColors.TEXT_MUTED
            )
            no_good_text.set_alpha(no_good_alpha)
            screen.blit(no_good_text, (self.SCREEN_WIDTH // 2 - no_good_text.get_width() // 2,
                                       result_rect.bottom + 15))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

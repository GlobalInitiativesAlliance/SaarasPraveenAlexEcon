"""
Choice Dialogue System for Part 8 - Ethereal Version
Handles job vs college, conflicting advice, mentor search, and ILP responses
Features: Floating choice panels, ethereal text, mentor glow effect
"""
import pygame
import math
import random

from .mentorship_visual_base import (
    DreamUIColors, DreamUIMetrics, DreamVisualHelpers,
    DreamVisualComponents, FloatAnimation, dream_visuals
)
from .mentorship_particles import dream_particles
from .mentorship_feedback import dream_feedback


class ChoiceDialoguePart8:
    """Choice-based dialogue system with dream visuals"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions - Full HD layout
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Scenarios with choices
        self.scenarios = {
            'impossible_choice': {
                'title': 'Impossible Choice',
                'prompt': 'You can only do one thing today. Choose:',
                'context': [
                    "Your phone shows two notifications:",
                    "- Job interview at 2pm (good opportunity)",
                    "- College application deadline is TODAY"
                ],
                'choices': [
                    {
                        'text': 'Go to job interview',
                        'result': 'You got the job... but missed the college deadline.',
                        'consequence': 'The application is gone. Another year lost.',
                        'color': DreamUIColors.SUCCESS_GREEN
                    },
                    {
                        'text': 'Work on college applications',
                        'result': 'Application submitted... but you missed the interview.',
                        'consequence': 'The job went to someone else. No income for now.',
                        'color': DreamUIColors.ETHEREAL_BLUE
                    }
                ]
            },
            'conflicting_advice': {
                'title': 'Conflicting Voices',
                'prompt': 'Everyone has advice, but none of it matches:',
                'context': [
                    "You asked for guidance at the Community Center."
                ],
                'choices': [
                    {
                        'text': '"Get a job now - money first!"',
                        'result': 'One person says focus on immediate income.',
                        'consequence': 'But what about your future?',
                        'color': DreamUIColors.SUCCESS_GREEN
                    },
                    {
                        'text': '"Go to school - invest in yourself!"',
                        'result': 'Another says education is the key.',
                        'consequence': 'But how will you pay rent?',
                        'color': DreamUIColors.ETHEREAL_BLUE
                    },
                    {
                        'text': '"Take out loans - everyone does it!"',
                        'result': 'Someone suggests debt as the answer.',
                        'consequence': 'Debt without guidance is dangerous.',
                        'color': DreamUIColors.UNCERTAIN_AMBER
                    }
                ]
            },
            'seek_mentor': {
                'title': 'Finding Guidance',
                'prompt': 'You can ask one question. Choose carefully:',
                'context': [
                    "You're at the Community Center.",
                    "Maybe someone here can actually help..."
                ],
                'choices': [
                    {
                        'text': 'What should I do with my life?',
                        'result': 'People shrug and walk away.',
                        'consequence': 'No one can answer that for you.',
                        'mentor_found': False,
                        'color': DreamUIColors.FOG_GRAY
                    },
                    {
                        'text': 'Who can guide me?',
                        'result': 'Someone pauses. "There\'s a counselor who helps youth..."',
                        'consequence': 'A mentor appears! They offer to help you plan.',
                        'mentor_found': True,
                        'color': DreamUIColors.GLOW_GOLD
                    },
                    {
                        'text': 'Why is everything so hard?',
                        'result': 'Sympathetic looks, but no answers.',
                        'consequence': 'Venting feels good, but doesn\'t solve anything.',
                        'mentor_found': False,
                        'color': DreamUIColors.GLOW_PINK
                    }
                ]
            },
            'ilp_response': {
                'title': 'Calling ILP',
                'prompt': 'You call your ILP officer for advice:',
                'context': [
                    "You're panicking about your future.",
                    "Maybe your case manager can help decide..."
                ],
                'choices': [
                    {
                        'text': '"What should I choose - job or school?"',
                        'result': '"I can\'t decide for you. It\'s your choice."',
                        'consequence': 'They have rules. They can\'t tell you what to do.',
                        'color': DreamUIColors.FOG_GRAY
                    },
                    {
                        'text': '"Can you help me figure this out?"',
                        'result': '"I can give you information, but the decision is yours."',
                        'consequence': 'Information without guidance isn\'t enough.',
                        'color': DreamUIColors.ETHEREAL_BLUE
                    },
                    {
                        'text': '"I don\'t know what I\'m doing!"',
                        'result': '"That\'s normal. Many young people feel that way."',
                        'consequence': 'Validation, but still no direction.',
                        'color': DreamUIColors.GLOW_PINK
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
        self.mentor_found = False
        self.time = 0

        # Hover state
        self.hovered_choice = -1

        # Float animations
        self.choice_floats = []

    def set_scenario(self, scenario_id):
        """Set the current scenario"""
        if scenario_id in self.scenarios:
            self.current_scenario = scenario_id
            self.scenario_data = self.scenarios[scenario_id]

            # Initialize float animations for choices
            self.choice_floats = []
            for i in range(len(self.scenario_data['choices'])):
                self.choice_floats.append(FloatAnimation(
                    phase=i * 0.7,
                    amplitude=4,
                    speed=0.6 + i * 0.1
                ))

    def start(self):
        """Start the dialogue"""
        self.active = True
        self.completed = False
        self.selected_index = -1
        self.show_result = False
        self.result_timer = 0
        self.hovered_choice = -1
        self.time = 0

        # Initialize particles
        dream_particles.clear()
        dream_particles.enable_ambient(pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Add atmosphere
        dream_particles.emit_dust_motes(
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            count=20
        )

        # Clear feedback
        dream_feedback.clear()

    def stop(self):
        """Stop the dialogue"""
        self.active = False
        dream_particles.disable_ambient()

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        self.time += dt

        # Update float animations
        for float_anim in self.choice_floats:
            float_anim.update(dt)

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.5:
                self.completed = True
                self.active = False

        # Update particles and feedback
        dream_particles.update(dt)
        dream_feedback.update(dt)

    def handle_event(self, event):
        """Handle input events"""
        if not self.active or self.show_result or not self.scenario_data:
            return

        choices = self.scenario_data['choices']

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            old_hover = self.hovered_choice
            self.hovered_choice = -1

            # Check hover on choice boxes - HD layout
            choice_width = 700
            choice_x = (self.SCREEN_WIDTH - choice_width) // 2
            choice_y = 320
            for i in range(len(choices)):
                choice_rect = pygame.Rect(choice_x, choice_y + i * 85, choice_width, 70)
                if choice_rect.collidepoint(pos):
                    self.hovered_choice = i

                    # Emit glow on first hover
                    if old_hover != i:
                        color = choices[i].get('color', DreamUIColors.GLOW_CYAN)
                        dream_particles.emit_glow_sparks(
                            choice_rect.centerx, choice_rect.centery, 6, color
                        )

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            choice_width = 700
            choice_x = (self.SCREEN_WIDTH - choice_width) // 2
            choice_y = 320
            for i in range(len(choices)):
                choice_rect = pygame.Rect(choice_x, choice_y + i * 85, choice_width, 70)
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

            choice = choices[index]
            color = choice.get('color', DreamUIColors.GLOW_CYAN)

            # Selection effect - HD layout
            choice_y = 320 + index * 85 + 35
            dream_particles.emit_glow_sparks(
                self.SCREEN_WIDTH // 2, choice_y, 20, color
            )

            # Check for mentor found
            if 'mentor_found' in choice:
                self.mentor_found = choice['mentor_found']
                if self.mentor_found:
                    # Special mentor glow effect
                    dream_particles.emit_mentor_glow(
                        self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2
                    )
                    dream_feedback.add_mentor_found_banner()
                else:
                    # No guidance effect - HD layout
                    dream_particles.emit_question_marks(
                        pygame.Rect(300, 250, 680, 300), 8
                    )
                    dream_feedback.add_no_guidance_banner()
            else:
                # Standard no guidance
                dream_feedback.add_no_guidance_banner()

    def render(self, screen):
        """Render the dialogue with dream visuals"""
        if not self.scenario_data:
            return

        # Dream background
        dream_visuals.draw_dream_background(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        # Title with ethereal glow - HD layout
        DreamVisualHelpers.draw_ethereal_text(
            screen, self.scenario_data['title'],
            (self.SCREEN_WIDTH // 2, 55),
            dream_visuals.fonts['title'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_PINK
        )

        # Context lines with fade-in effect - HD layout
        context_y = 120
        for i, line in enumerate(self.scenario_data['context']):
            float_offset = int(math.sin(self.time * 0.8 + i * 0.5) * 2)
            DreamVisualHelpers.draw_ethereal_text(
                screen, line,
                (self.SCREEN_WIDTH // 2, context_y + i * 35 + float_offset),
                dream_visuals.fonts['body'],
                DreamUIColors.TEXT_DIM,
                DreamUIColors.FOG_GRAY
            )

        # Prompt - HD layout
        prompt_y = 260 + int(math.sin(self.time * 1.2) * 2)
        DreamVisualHelpers.draw_ethereal_text(
            screen, self.scenario_data['prompt'],
            (self.SCREEN_WIDTH // 2, prompt_y),
            dream_visuals.fonts['heading'],
            DreamUIColors.TEXT_ETHEREAL,
            DreamUIColors.GLOW_CYAN
        )

        # Choices as floating panels - HD layout
        choices = self.scenario_data['choices']
        choice_width = 700
        choice_x = (self.SCREEN_WIDTH - choice_width) // 2
        choice_y = 320

        for i, choice in enumerate(choices):
            float_offset = self.choice_floats[i].y_offset if i < len(self.choice_floats) else 0
            rect = pygame.Rect(choice_x, choice_y + i * 85 + float_offset, choice_width, 70)

            is_selected = (self.show_result and i == self.selected_index)
            is_hover = (i == self.hovered_choice)

            choice_color = choice.get('color', DreamUIColors.GLOW_CYAN)

            # Determine glow intensity
            glow_intensity = 0.2
            if is_hover:
                glow_intensity = 0.6
            if is_selected:
                glow_intensity = 0.9

            # Draw glowing panel
            dream_visuals.draw_glowing_panel(
                screen, rect,
                glow_color=choice_color if is_hover or is_selected else DreamUIColors.FOG_GRAY,
                bg_color=DreamUIColors.DREAM_PURPLE_DARK if not is_selected else DreamUIColors.DREAM_PURPLE,
                glow_intensity=glow_intensity,
                border_alpha=200 if is_hover else 150
            )

            # Choice number
            num_color = DreamUIColors.TEXT_DIM if not is_hover else DreamUIColors.TEXT_ETHEREAL
            num_text = dream_visuals.fonts['body'].render(f"[{i + 1}]", True, num_color)
            screen.blit(num_text, (rect.x + 15, rect.centery - num_text.get_height() // 2))

            # Choice text
            text_color = DreamUIColors.TEXT_ETHEREAL if is_hover or is_selected else DreamUIColors.TEXT_DIM
            text_surface = dream_visuals.fonts['body'].render(choice['text'], True, text_color)
            screen.blit(text_surface, (rect.x + 60, rect.centery - text_surface.get_height() // 2))

        # Show result - HD layout
        if self.show_result and self.selected_index >= 0:
            choice = choices[self.selected_index]
            choice_color = choice.get('color', DreamUIColors.GLOW_CYAN)

            # Result appears below choices with fade-in
            result_y = choice_y + len(choices) * 85 + 40
            result_alpha = min(255, int(self.result_timer * 200))

            # Result text
            DreamVisualHelpers.draw_ethereal_text(
                screen, choice['result'],
                (self.SCREEN_WIDTH // 2, result_y),
                dream_visuals.fonts['heading'],
                DreamUIColors.TEXT_ETHEREAL,
                choice_color,
                result_alpha
            )

            # Consequence
            if self.result_timer > 0.8:
                cons_alpha = min(255, int((self.result_timer - 0.8) * 200))
                cons_color = DreamUIColors.COLLAPSE_RED if not self.mentor_found else DreamUIColors.SUCCESS_GREEN

                DreamVisualHelpers.draw_ethereal_text(
                    screen, choice['consequence'],
                    (self.SCREEN_WIDTH // 2, result_y + 45),
                    dream_visuals.fonts['body'],
                    cons_color,
                    DreamUIColors.UNCERTAIN_AMBER,
                    cons_alpha
                )

            # Mentor found special effect
            if self.current_scenario == 'seek_mentor' and self.mentor_found and self.result_timer > 1.5:
                mentor_alpha = min(255, int((self.result_timer - 1.5) * 200))
                DreamVisualHelpers.draw_ethereal_text(
                    screen, "✨ A mentor has appeared! ✨",
                    (self.SCREEN_WIDTH // 2, result_y + 100),
                    dream_visuals.fonts['title'],
                    DreamUIColors.GLOW_GOLD_BRIGHT,
                    DreamUIColors.GLOW_GOLD,
                    mentor_alpha
                )

        # Render particles
        dream_particles.render(screen)

        # Render feedback
        dream_feedback.render(screen)

        # Vignette
        DreamVisualHelpers.draw_vignette(screen, 0.3)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

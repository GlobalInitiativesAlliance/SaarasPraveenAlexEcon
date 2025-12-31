"""
Choice Dialogue System for Part 8 - Professional Version
Handles job vs college, conflicting advice, mentor search, and ILP responses
Clean professional choice buttons
"""
import pygame

from .mentorship_visual_base import (
    MentorshipUIColors, MentorshipUIMetrics, MentorshipVisualHelpers,
    mentorship_visuals
)
from .mentorship_particles import dream_particles
from .mentorship_feedback import dream_feedback


class ChoiceDialoguePart8:
    """Choice-based dialogue system with professional visuals"""

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
                        'color': MentorshipUIColors.SUCCESS_GREEN
                    },
                    {
                        'text': 'Work on college applications',
                        'result': 'Application submitted... but you missed the interview.',
                        'consequence': 'The job went to someone else. No income for now.',
                        'color': MentorshipUIColors.OPTION_SCHOOL
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
                        'color': MentorshipUIColors.SUCCESS_GREEN
                    },
                    {
                        'text': '"Go to school - invest in yourself!"',
                        'result': 'Another says education is the key.',
                        'consequence': 'But how will you pay rent?',
                        'color': MentorshipUIColors.OPTION_SCHOOL
                    },
                    {
                        'text': '"Take out loans - everyone does it!"',
                        'result': 'Someone suggests debt as the answer.',
                        'consequence': 'Debt without guidance is dangerous.',
                        'color': MentorshipUIColors.WARNING_AMBER
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
                        'color': MentorshipUIColors.SLATE_GRAY
                    },
                    {
                        'text': 'Who can guide me?',
                        'result': 'Someone pauses. "There\'s a counselor who helps youth..."',
                        'consequence': 'A mentor appears! They offer to help you plan.',
                        'mentor_found': True,
                        'color': MentorshipUIColors.GUIDANCE_ACCENT
                    },
                    {
                        'text': 'Why is everything so hard?',
                        'result': 'Sympathetic looks, but no answers.',
                        'consequence': 'Venting feels good, but doesn\'t solve anything.',
                        'mentor_found': False,
                        'color': MentorshipUIColors.OPTION_ALTERNATIVE
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
                        'color': MentorshipUIColors.SLATE_GRAY
                    },
                    {
                        'text': '"Can you help me figure this out?"',
                        'result': '"I can give you information, but the decision is yours."',
                        'consequence': 'Information without guidance isn\'t enough.',
                        'color': MentorshipUIColors.OPTION_SCHOOL
                    },
                    {
                        'text': '"I don\'t know what I\'m doing!"',
                        'result': '"That\'s normal. Many young people feel that way."',
                        'consequence': 'Validation, but still no direction.',
                        'color': MentorshipUIColors.OPTION_ALTERNATIVE
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

        # Hover state
        self.hovered_choice = -1

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
        self.mentor_found = False

        # Clear feedback
        dream_feedback.clear()

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.5:
                self.completed = True
                self.active = False

        # Update feedback
        dream_feedback.update(dt)

    def handle_event(self, event):
        """Handle input events"""
        if not self.active or self.show_result or not self.scenario_data:
            return

        choices = self.scenario_data['choices']

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_choice = -1

            # Check hover on choice boxes
            choice_width = 650
            choice_x = (self.SCREEN_WIDTH - choice_width) // 2
            choice_y = 320
            for i in range(len(choices)):
                choice_rect = pygame.Rect(choice_x, choice_y + i * 75, choice_width, 60)
                if choice_rect.collidepoint(pos):
                    self.hovered_choice = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            choice_width = 650
            choice_x = (self.SCREEN_WIDTH - choice_width) // 2
            choice_y = 320
            for i in range(len(choices)):
                choice_rect = pygame.Rect(choice_x, choice_y + i * 75, choice_width, 60)
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

            # Check for mentor found
            if 'mentor_found' in choice:
                self.mentor_found = choice['mentor_found']
                if self.mentor_found:
                    dream_feedback.add_mentor_found_banner()
                else:
                    dream_feedback.add_no_guidance_banner()
            else:
                dream_feedback.add_no_guidance_banner()

    def render(self, screen):
        """Render the dialogue with professional visuals"""
        if not self.scenario_data:
            return

        # Clean background
        screen.fill(MentorshipUIColors.BACKGROUND)

        # Title
        mentorship_visuals.draw_title(
            screen, self.scenario_data['title'],
            self.SCREEN_WIDTH // 2, 50
        )

        # Context lines
        context_y = 120
        for i, line in enumerate(self.scenario_data['context']):
            context_surface = mentorship_visuals.fonts['body'].render(
                line, True, MentorshipUIColors.TEXT_SECONDARY
            )
            screen.blit(context_surface,
                       (self.SCREEN_WIDTH // 2 - context_surface.get_width() // 2,
                        context_y + i * 30))

        # Prompt
        prompt_y = 260
        prompt_surface = mentorship_visuals.fonts['heading'].render(
            self.scenario_data['prompt'], True, MentorshipUIColors.TEXT_PRIMARY
        )
        screen.blit(prompt_surface,
                   (self.SCREEN_WIDTH // 2 - prompt_surface.get_width() // 2, prompt_y))

        # Choices as buttons
        choices = self.scenario_data['choices']
        choice_width = 650
        choice_x = (self.SCREEN_WIDTH - choice_width) // 2
        choice_y = 320

        for i, choice in enumerate(choices):
            rect = pygame.Rect(choice_x, choice_y + i * 75, choice_width, 60)

            is_selected = (self.show_result and i == self.selected_index)
            is_hover = (i == self.hovered_choice)

            mentorship_visuals.draw_choice_button(
                screen, rect,
                choice['text'], i,
                is_hover=is_hover,
                is_selected=is_selected
            )

        # Show result
        if self.show_result and self.selected_index >= 0:
            choice = choices[self.selected_index]

            # Result appears below choices with fade-in
            result_y = choice_y + len(choices) * 75 + 30
            result_alpha = min(255, int(self.result_timer * 200))

            # Result text
            result_surface = mentorship_visuals.fonts['body_bold'].render(
                choice['result'], True, MentorshipUIColors.TEXT_PRIMARY
            )
            result_surface.set_alpha(result_alpha)
            screen.blit(result_surface,
                       (self.SCREEN_WIDTH // 2 - result_surface.get_width() // 2, result_y))

            # Consequence
            if self.result_timer > 0.8:
                cons_alpha = min(255, int((self.result_timer - 0.8) * 200))
                cons_color = MentorshipUIColors.SUCCESS_GREEN if self.mentor_found else MentorshipUIColors.ERROR_RED

                cons_surface = mentorship_visuals.fonts['body'].render(
                    choice['consequence'], True, cons_color
                )
                cons_surface.set_alpha(cons_alpha)
                screen.blit(cons_surface,
                           (self.SCREEN_WIDTH // 2 - cons_surface.get_width() // 2, result_y + 40))

            # Mentor found special message
            if self.current_scenario == 'seek_mentor' and self.mentor_found and self.result_timer > 1.5:
                mentor_alpha = min(255, int((self.result_timer - 1.5) * 200))
                mentor_surface = mentorship_visuals.fonts['heading'].render(
                    "A mentor has appeared!", True, MentorshipUIColors.GUIDANCE_ACCENT
                )
                mentor_surface.set_alpha(mentor_alpha)
                screen.blit(mentor_surface,
                           (self.SCREEN_WIDTH // 2 - mentor_surface.get_width() // 2, result_y + 90))

        # Render feedback
        dream_feedback.render(screen)

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

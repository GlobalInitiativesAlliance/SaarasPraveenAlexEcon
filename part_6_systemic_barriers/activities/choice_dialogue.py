"""
Choice Dialogue System for Part 6 - Systemic Barriers
Handles dialogue choices that demonstrate how specific language
and knowledge of the system affects outcomes

UPGRADED: Clipboard aesthetic, hover effects, color-coded results,
typewriter text, smooth transitions
"""
import pygame
import math
import time

from .systemic_visual_base import (
    SystemicUIColors, SystemicUIMetrics, SystemicVisualHelpers,
    SystemicVisualComponents, UIAnimation, systemic_visuals
)
from .systemic_particles import SystemicParticleSystem
from .systemic_feedback import SystemicFeedbackManager


class ChoiceDialogueSystem:
    """Dialogue system with meaningful choices for Part 6"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Current scenario
        self.current_scenario = None
        self.scenario_id = None

        # Choice state
        self.selected_choice = 0
        self.choice_made = False
        self.show_result = False
        self.result_timer = 0

        # Scenarios
        self.scenarios = {
            'application_quiz': {
                'title': 'Benefits Knowledge Check',
                'description': [
                    "You received a letter saying you might qualify for food assistance.",
                    "But how do you actually apply?",
                ],
                'question': "What's the best way to apply for CalFresh benefits?",
                'choices': [
                    {
                        'text': 'Go to the office and ask for help',
                        'result': 'partial',
                        'response': [
                            "You go to the office but wait 2 hours.",
                            "The clerk hands you a stack of forms.",
                            "You're not sure which ones you need.",
                        ]
                    },
                    {
                        'text': 'Apply online at GetCalFresh.org',
                        'result': 'good',
                        'response': [
                            "GetCalFresh.org is easier than the official site.",
                            "It walks you through the process step by step.",
                            "But you still need reliable internet access.",
                        ]
                    },
                    {
                        'text': 'Call the benefits hotline',
                        'result': 'bad',
                        'response': [
                            "You spend 45 minutes navigating phone menus.",
                            "The call drops before you reach a human.",
                            "You'll have to try again another day.",
                        ]
                    },
                    {
                        'text': "I don't know how to apply",
                        'result': 'honest',
                        'response': [
                            "That's understandable - the system is confusing.",
                            "Many people don't know where to start.",
                            "This lack of clear information is itself a barrier.",
                        ]
                    }
                ]
            },
            'dialogue_choice': {
                'title': 'Speaking to the Clerk',
                'description': [
                    "You're at the benefits office front desk.",
                    "The clerk looks tired and has a long line behind you.",
                    "How you phrase your request matters.",
                ],
                'question': "What do you say to the clerk?",
                'choices': [
                    {
                        'text': '"I need help with benefits."',
                        'result': 'bad',
                        'response': [
                            '"Which benefits? We handle many programs."',
                            "The clerk hands you a general information packet.",
                            "You're sent to wait without clear direction.",
                        ]
                    },
                    {
                        'text': '"I want to apply for food stamps."',
                        'result': 'partial',
                        'response': [
                            '"It\'s called CalFresh now. Here\'s the form."',
                            "You get the right form but minimal guidance.",
                            "At least you're pointed in the right direction.",
                        ]
                    },
                    {
                        'text': '"I\'m a former foster youth applying for CalFresh under AB 1930."',
                        'result': 'good',
                        'response': [
                            "The clerk's demeanor changes immediately.",
                            '"Oh! Let me get you to our specialized worker."',
                            "Knowing the specific program unlocks faster service.",
                        ]
                    },
                    {
                        'text': '"Can someone help me figure out what I qualify for?"',
                        'result': 'mixed',
                        'response': [
                            '"We can\'t do assessments. You need to apply first."',
                            "The system requires you to already know what you need.",
                            "It's designed for people who understand bureaucracy.",
                        ]
                    }
                ]
            },
            'workshop_conflict': {
                'title': 'Impossible Schedule',
                'description': [
                    "Your ILP workshop is scheduled for Tuesday at 3pm.",
                    "Missing it means losing your housing assistance.",
                    "But your work shift is also Tuesday, 2pm-10pm.",
                    "Calling out means losing your job.",
                ],
                'question': "What do you choose?",
                'choices': [
                    {
                        'text': 'Attend the workshop, miss work',
                        'result': 'workshop',
                        'response': [
                            "You attend the mandatory workshop.",
                            "Your manager is furious - this is your final warning.",
                            "You keep your housing assistance... for now.",
                            "But one more absence and you're fired.",
                        ]
                    },
                    {
                        'text': 'Go to work, skip the workshop',
                        'result': 'work',
                        'response': [
                            "You keep your job and your income.",
                            "But you receive a notice: benefits suspended.",
                            "You'll need to reapply from scratch.",
                            "The workshop won't be offered again for 3 months.",
                        ]
                    },
                    {
                        'text': 'Try to do both (leave work early)',
                        'result': 'both',
                        'response': [
                            "You ask to leave work early - request denied.",
                            "You leave anyway and rush to the workshop.",
                            "You arrive 20 minutes late - marked absent.",
                            "You've now upset your boss AND missed the workshop.",
                        ]
                    },
                    {
                        'text': 'Call both to explain and reschedule',
                        'result': 'call',
                        'response': [
                            "The workshop hotline puts you on hold for an hour.",
                            "When you finally reach someone: 'No exceptions.'",
                            "Your manager says: 'Not my problem.'",
                            "The system wasn't designed for working people.",
                        ]
                    }
                ]
            }
        }

        # Visual systems
        self.particles = SystemicParticleSystem()
        self.feedback = SystemicFeedbackManager()
        self.visuals = systemic_visuals

        # Animations
        self.entrance_progress = 0.0
        self.hover_scales = {}
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)
        self.typewriter_progress = 0

        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.font_title = pygame.font.SysFont('SF Pro Display', 32, bold=True)
            self.font_heading = pygame.font.SysFont('SF Pro Display', 24, bold=True)
            self.font_body = pygame.font.SysFont('SF Pro Text', 18)
            self.font_small = pygame.font.SysFont('SF Pro Text', 14)
            self.font_choice = pygame.font.SysFont('SF Pro Text', 17)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_heading = pygame.font.Font(None, 28)
            self.font_body = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 18)
            self.font_choice = pygame.font.Font(None, 20)

    def set_scenario_by_id(self, scenario_id):
        """Set which scenario to use"""
        self.scenario_id = scenario_id
        if scenario_id in self.scenarios:
            self.current_scenario = self.scenarios[scenario_id]

    def handle_event(self, event):
        """Handle choice selection"""
        if not self.active or self.completed:
            return False

        if self.show_result:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if self.result_timer < 180:
                    self.completed = True
            return True

        if not self.current_scenario:
            return False

        choices = self.current_scenario.get('choices', [])
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_choice = (self.selected_choice - 1) % len(choices)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_choice = (self.selected_choice + 1) % len(choices)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.make_choice()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                idx = event.key - pygame.K_1
                if idx < len(choices):
                    self.selected_choice = idx
                    self.make_choice()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check clicks on choices
            choice_start_y = 380
            for i in range(len(choices)):
                choice_rect = pygame.Rect(240, choice_start_y + i * 72, 800, 62)
                if choice_rect.collidepoint(mouse_pos):
                    self.selected_choice = i
                    self.make_choice()
                    break

        elif event.type == pygame.MOUSEMOTION:
            # Update hover for animation
            choice_start_y = 380
            for i in range(len(choices)):
                choice_rect = pygame.Rect(240, choice_start_y + i * 72, 800, 62)
                if choice_rect.collidepoint(mouse_pos):
                    self.selected_choice = i
                    break

        return True

    def make_choice(self):
        """Process the selected choice"""
        self.choice_made = True
        self.show_result = True
        self.result_timer = 280
        self.result_alpha = UIAnimation(0, 1.0, speed=0.1)
        self.typewriter_progress = 0

        # Get result type and emit appropriate particles
        choices = self.current_scenario.get('choices', [])
        chosen = choices[self.selected_choice]
        result_type = chosen.get('result', 'neutral')

        if result_type == 'good':
            self.particles.emit_success(self.SCREEN_WIDTH // 2, 300, 20)
        elif result_type in ['bad', 'both', 'call']:
            self.particles.emit_frustration(self.SCREEN_WIDTH // 2, 250, 1.0)
            self.feedback.add_warning_popup(self.SCREEN_WIDTH // 2, 300, "No-Win Situation")

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        # Update particles and feedback
        self.particles.update(dt)
        self.feedback.update(dt)

        # Entrance animation
        self.entrance_progress = min(1.0, self.entrance_progress + dt * 3)

        # Hover scale animations
        choices = self.current_scenario.get('choices', []) if self.current_scenario else []
        for i in range(len(choices)):
            target = 1.02 if i == self.selected_choice else 1.0
            current = self.hover_scales.get(i, 1.0)
            self.hover_scales[i] = current + (target - current) * 0.2

        if self.show_result:
            self.result_alpha.update(dt)
            self.result_timer -= 1
            self.typewriter_progress = min(100, self.typewriter_progress + 1.5)

            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the choice dialogue"""
        if not self.active or not self.current_scenario:
            return

        # Dark background with gradient
        for y in range(self.SCREEN_HEIGHT):
            progress = y / self.SCREEN_HEIGHT
            color = SystemicVisualHelpers.interpolate_color(
                (35, 35, 45), (25, 25, 35), progress
            )
            pygame.draw.line(screen, color, (0, y), (self.SCREEN_WIDTH, y))

        if self.show_result:
            self._render_result(screen)
        else:
            self._render_choices(screen)

        # Particles and feedback
        self.particles.render(screen)
        self.feedback.render(screen)

    def _render_choices(self, screen):
        """Render the choice selection screen"""
        scenario = self.current_scenario

        # Clipboard background
        clip_rect = pygame.Rect(180, 40, 920, 640)
        SystemicVisualHelpers.draw_shadow(screen, clip_rect, 15, 60,
                                         SystemicUIMetrics.RADIUS_LARGE)

        # Clipboard body
        pygame.draw.rect(screen, SystemicUIColors.MANILA, clip_rect,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Clipboard clip at top
        clip_holder = pygame.Rect(clip_rect.centerx - 60, clip_rect.y - 10, 120, 30)
        pygame.draw.rect(screen, SystemicUIColors.INSTITUTIONAL_GRAY, clip_holder,
                        border_radius=5)

        # Paper area
        paper_rect = pygame.Rect(clip_rect.x + 20, clip_rect.y + 30,
                                clip_rect.width - 40, clip_rect.height - 50)
        pygame.draw.rect(screen, SystemicUIColors.FORM_CREAM, paper_rect,
                        border_radius=SystemicUIMetrics.RADIUS_SMALL)

        # Title
        title = scenario.get('title', 'Make a Choice')
        title_text = self.font_title.render(title, True, SystemicUIColors.GOVERNMENT_BLUE)
        screen.blit(title_text, (paper_rect.centerx - title_text.get_width() // 2,
                                paper_rect.y + 25))

        # Description
        y = paper_rect.y + 80
        for line in scenario.get('description', []):
            desc_text = self.font_body.render(line, True, SystemicUIColors.TEXT_SECONDARY)
            screen.blit(desc_text, (paper_rect.centerx - desc_text.get_width() // 2, y))
            y += 30

        # Question
        question = scenario.get('question', '')
        question_text = self.font_heading.render(question, True, SystemicUIColors.WARNING_ORANGE)
        screen.blit(question_text, (paper_rect.centerx - question_text.get_width() // 2,
                                   y + 20))

        # Choices
        choices = scenario.get('choices', [])
        choice_start_y = 380

        for i, choice in enumerate(choices):
            self._render_choice_option(screen, choice, i, choice_start_y + i * 72)

        # Instructions
        inst_text = self.font_small.render("Use UP/DOWN or 1-4 to select, ENTER to confirm",
                                          True, SystemicUIColors.TEXT_MUTED)
        screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 680))

    def _render_choice_option(self, screen, choice, index, y):
        """Render a single choice option"""
        is_selected = index == self.selected_choice
        scale = self.hover_scales.get(index, 1.0)

        # Calculate scaled dimensions
        base_width = 800
        base_height = 62
        width = int(base_width * scale)
        height = int(base_height * scale)
        x = 240 - (width - base_width) // 2

        choice_rect = pygame.Rect(x, y - (height - base_height) // 2, width, height)

        # Background
        if is_selected:
            bg_color = SystemicUIColors.GOVERNMENT_BLUE_LIGHT
            border_color = SystemicUIColors.GOVERNMENT_BLUE
            text_color = SystemicUIColors.TEXT_LIGHT
        else:
            bg_color = (250, 250, 252)
            border_color = SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT
            text_color = SystemicUIColors.TEXT_PRIMARY

        # Shadow for selected
        if is_selected:
            SystemicVisualHelpers.draw_shadow(screen, choice_rect, 6, 40,
                                             SystemicUIMetrics.RADIUS_MEDIUM)

        pygame.draw.rect(screen, bg_color, choice_rect,
                        border_radius=SystemicUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, border_color, choice_rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_MEDIUM)

        # Number badge
        badge_x = choice_rect.x + 20
        badge_y = choice_rect.centery
        badge_color = SystemicUIColors.GOVERNMENT_BLUE if is_selected else SystemicUIColors.INSTITUTIONAL_GRAY
        pygame.draw.circle(screen, badge_color, (badge_x, badge_y), 14)

        num_text = self.font_small.render(str(index + 1), True, SystemicUIColors.TEXT_LIGHT)
        screen.blit(num_text, (badge_x - num_text.get_width() // 2,
                              badge_y - num_text.get_height() // 2))

        # Choice text
        choice_text = choice.get('text', '')
        text_surface = self.font_choice.render(choice_text, True, text_color)
        screen.blit(text_surface, (choice_rect.x + 50,
                                  choice_rect.centery - text_surface.get_height() // 2))

        # Arrow indicator for selected
        if is_selected:
            arrow_text = self.font_heading.render(">", True, SystemicUIColors.TEXT_LIGHT)
            screen.blit(arrow_text, (choice_rect.right - 35,
                                    choice_rect.centery - arrow_text.get_height() // 2))

    def _render_result(self, screen):
        """Render the choice result"""
        scenario = self.current_scenario
        choices = scenario.get('choices', [])
        chosen = choices[self.selected_choice]

        alpha = self.result_alpha.value

        # Result panel
        panel_width = 900
        panel_height = 450
        panel_x = (self.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.SCREEN_HEIGHT - panel_height) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        # Shadow
        SystemicVisualHelpers.draw_shadow(screen, panel_rect, 15, int(80 * alpha),
                                         SystemicUIMetrics.RADIUS_LARGE)

        # Background
        pygame.draw.rect(screen, SystemicUIColors.FORM_CREAM, panel_rect,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Result type determines header color
        result_type = chosen.get('result', 'neutral')
        header_colors = {
            'good': SystemicUIColors.APPROVAL_GREEN,
            'partial': SystemicUIColors.WARNING_ORANGE,
            'bad': SystemicUIColors.ERROR_RED,
            'mixed': SystemicUIColors.WARNING_ORANGE,
            'honest': SystemicUIColors.GOVERNMENT_BLUE,
            'workshop': SystemicUIColors.WARNING_ORANGE,
            'work': SystemicUIColors.WARNING_ORANGE,
            'both': SystemicUIColors.ERROR_RED,
            'call': SystemicUIColors.ERROR_RED,
        }
        header_color = header_colors.get(result_type, SystemicUIColors.INSTITUTIONAL_GRAY)

        # Header bar
        header_rect = pygame.Rect(panel_x, panel_y, panel_width, 60)
        pygame.draw.rect(screen, header_color, header_rect,
                        border_top_left_radius=SystemicUIMetrics.RADIUS_LARGE,
                        border_top_right_radius=SystemicUIMetrics.RADIUS_LARGE)

        # Header text
        header_text = "Outcome"
        header_surface = self.font_heading.render(header_text, True, SystemicUIColors.TEXT_LIGHT)
        screen.blit(header_surface, (panel_rect.centerx - header_surface.get_width() // 2,
                                    panel_y + 18))

        # What you chose
        chose_text = f"You chose: {chosen.get('text', '')}"
        chose_surface = self.font_body.render(chose_text, True, SystemicUIColors.TEXT_SECONDARY)
        screen.blit(chose_surface, (panel_rect.x + 40, panel_rect.y + 85))

        # Divider
        pygame.draw.line(screen, SystemicUIColors.INSTITUTIONAL_GRAY_LIGHT,
                        (panel_rect.x + 40, panel_rect.y + 125),
                        (panel_rect.right - 40, panel_rect.y + 125), 2)

        # Response text with typewriter effect
        response_lines = chosen.get('response', [])
        y = panel_rect.y + 150

        total_chars = sum(len(line) for line in response_lines)
        chars_to_show = int(total_chars * self.typewriter_progress / 100)
        chars_shown = 0

        # Text color based on result
        text_color = header_color if result_type in ['bad', 'both', 'call'] else SystemicUIColors.TEXT_PRIMARY

        for line in response_lines:
            if chars_shown >= chars_to_show:
                break

            visible_chars = min(len(line), chars_to_show - chars_shown)
            visible_text = line[:visible_chars]

            line_surface = self.font_body.render(visible_text, True, text_color)
            screen.blit(line_surface, (panel_rect.x + 50, y))
            y += 35
            chars_shown += len(line)

        # Systemic message for bad outcomes
        if result_type in ['bad', 'both', 'call'] and self.typewriter_progress > 80:
            msg_rect = pygame.Rect(panel_rect.x + 40, panel_rect.y + 330,
                                  panel_rect.width - 80, 50)
            pygame.draw.rect(screen, (255, 240, 240), msg_rect,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)
            pygame.draw.rect(screen, SystemicUIColors.ERROR_RED, msg_rect, 2,
                           border_radius=SystemicUIMetrics.RADIUS_SMALL)

            msg_text = "The system creates no-win situations."
            msg_surface = self.font_heading.render(msg_text, True, SystemicUIColors.ERROR_RED)
            screen.blit(msg_surface, (msg_rect.centerx - msg_surface.get_width() // 2,
                                     msg_rect.centery - msg_surface.get_height() // 2))

        # Continue prompt
        if self.result_timer < 220:
            prompt_text = self.font_small.render("Press any key to continue...", True,
                                                SystemicUIColors.TEXT_MUTED)
            screen.blit(prompt_text, (panel_rect.centerx - prompt_text.get_width() // 2,
                                     panel_rect.bottom - 40))

        # Border
        pygame.draw.rect(screen, header_color, panel_rect, 2,
                        border_radius=SystemicUIMetrics.RADIUS_LARGE)

    def start(self):
        """Start the choice dialogue"""
        self.active = True
        self.completed = False
        self.selected_choice = 0
        self.choice_made = False
        self.show_result = False
        self.entrance_progress = 0.0
        self.hover_scales = {}
        self.typewriter_progress = 0

        # Default to first scenario if none set
        if not self.current_scenario and self.scenarios:
            first_key = list(self.scenarios.keys())[0]
            self.set_scenario_by_id(first_key)

        # Clear effects
        self.particles.clear()
        self.feedback.clear()

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

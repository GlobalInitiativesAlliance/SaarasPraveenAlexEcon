"""
Choice Dialogue System for Part 8 - Lack of Guidance/Mentorship
Handles job vs college, conflicting advice, mentor search, and ILP responses
"""
import pygame


class ChoiceDialoguePart8:
    """Choice-based dialogue system for Part 8"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

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
                        'consequence': 'The application is gone. Another year lost.'
                    },
                    {
                        'text': 'Work on college applications',
                        'result': 'Application submitted... but you missed the interview.',
                        'consequence': 'The job went to someone else. No income for now.'
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
                        'consequence': 'But what about your future?'
                    },
                    {
                        'text': '"Go to school - invest in yourself!"',
                        'result': 'Another says education is the key.',
                        'consequence': 'But how will you pay rent?'
                    },
                    {
                        'text': '"Take out loans - everyone does it!"',
                        'result': 'Someone suggests debt as the answer.',
                        'consequence': 'Debt without guidance is dangerous.'
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
                        'mentor_found': False
                    },
                    {
                        'text': 'Who can guide me?',
                        'result': 'Someone pauses. "There\'s a counselor who helps youth..."',
                        'consequence': 'A mentor appears! They offer to help you plan.',
                        'mentor_found': True
                    },
                    {
                        'text': 'Why is everything so hard?',
                        'result': 'Sympathetic looks, but no answers.',
                        'consequence': 'Venting feels good, but doesn\'t solve anything.',
                        'mentor_found': False
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
                        'consequence': 'They have rules. They can\'t tell you what to do.'
                    },
                    {
                        'text': '"Can you help me figure this out?"',
                        'result': '"I can give you information, but the decision is yours."',
                        'consequence': 'Information without guidance isn\'t enough.'
                    },
                    {
                        'text': '"I don\'t know what I\'m doing!"',
                        'result': '"That\'s normal. Many young people feel that way."',
                        'consequence': 'Validation, but still no direction.'
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

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer += dt
            if self.result_timer > 4.0:
                self.completed = True
                self.active = False

    def handle_event(self, event):
        """Handle input events"""
        if not self.active or self.show_result or not self.scenario_data:
            return

        choices = self.scenario_data['choices']

        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_choice = -1

            # Check hover on choice boxes
            choice_y = 300
            for i in range(len(choices)):
                choice_rect = pygame.Rect(150, choice_y + i * 70, 500, 55)
                if choice_rect.collidepoint(pos):
                    self.hovered_choice = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            choice_y = 300
            for i in range(len(choices)):
                choice_rect = pygame.Rect(150, choice_y + i * 70, 500, 55)
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

            # Check for mentor found
            if 'mentor_found' in choices[index]:
                self.mentor_found = choices[index]['mentor_found']

    def render(self, screen):
        """Render the dialogue"""
        if not self.scenario_data:
            return

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((30, 30, 40))
        overlay.set_alpha(235)
        screen.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render(self.scenario_data['title'], True, (200, 200, 210))
        screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        # Context
        context_font = pygame.font.Font(None, 24)
        context_y = 100
        for line in self.scenario_data['context']:
            text = context_font.render(line, True, (160, 160, 170))
            screen.blit(text, (150, context_y))
            context_y += 28

        # Prompt
        prompt_font = pygame.font.Font(None, 30)
        prompt = prompt_font.render(self.scenario_data['prompt'], True, (180, 180, 190))
        screen.blit(prompt, (150, 250))

        # Choices
        choices = self.scenario_data['choices']
        choice_font = pygame.font.Font(None, 26)
        choice_y = 300

        for i, choice in enumerate(choices):
            rect = pygame.Rect(150, choice_y + i * 70, 500, 55)

            # Background
            if self.show_result and i == self.selected_index:
                bg_color = (70, 90, 70)
            elif i == self.hovered_choice:
                bg_color = (60, 65, 80)
            else:
                bg_color = (45, 50, 60)

            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, (100, 105, 115), rect, 2)

            # Choice number
            num = choice_font.render(f"[{i + 1}]", True, (140, 140, 150))
            screen.blit(num, (rect.x + 10, rect.y + 17))

            # Choice text
            text = choice_font.render(choice['text'], True, (220, 220, 230))
            screen.blit(text, (rect.x + 50, rect.y + 17))

        # Show result
        if self.show_result and self.selected_index >= 0:
            choice = choices[self.selected_index]

            result_y = choice_y + len(choices) * 70 + 20

            # Result box
            result_rect = pygame.Rect(100, result_y, 600, 120)
            pygame.draw.rect(screen, (50, 55, 65), result_rect)
            pygame.draw.rect(screen, (120, 130, 140), result_rect, 2)

            # Result text
            result_font = pygame.font.Font(None, 28)
            result_text = result_font.render(choice['result'], True, (200, 200, 210))
            screen.blit(result_text, (result_rect.x + 20, result_rect.y + 25))

            # Consequence
            cons_font = pygame.font.Font(None, 24)
            cons_text = cons_font.render(choice['consequence'], True, (180, 150, 150))
            screen.blit(cons_text, (result_rect.x + 20, result_rect.y + 65))

            # Mentor found indicator
            if self.current_scenario == 'seek_mentor' and self.mentor_found:
                mentor_text = result_font.render("A mentor has appeared!", True, (100, 200, 100))
                screen.blit(mentor_text, (result_rect.x + 20, result_rect.y + 90))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

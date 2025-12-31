"""
Choice Dialogue System for Part 9 - Conflicting Responsibilities
Handles multiple forced choice scenarios about time conflicts
"""
import pygame


class ChoiceDialoguePart9:
    """Choice-based dialogue system for Part 9"""

    def __init__(self):
        self.active = False
        self.completed = False

        # Screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Scenarios with choices
        self.scenarios = {
            'choose_one': {
                'title': 'Choose One Priority',
                'prompt': 'You can only attend ONE. Choose:',
                'context': [
                    "All three events are at the same time.",
                    "Missing any of them has consequences."
                ],
                'choices': [
                    {
                        'text': 'Go to work (3pm shift)',
                        'result': 'You earned wages today.',
                        'consequence': 'Program progress lost. Benefits at risk.'
                    },
                    {
                        'text': 'Go to program meeting',
                        'result': 'Benefits protected.',
                        'consequence': 'Fired from job. No income.'
                    },
                    {
                        'text': 'Go to therapy session',
                        'result': 'Mental health improved.',
                        'consequence': 'Rent money decreases. Job warning.'
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
                'choices': [
                    {
                        'text': 'Tell the teacher honestly',
                        'result': 'Teacher is understanding.',
                        'consequence': 'But you still lose the exam grade. No makeup offered.'
                    },
                    {
                        'text': 'Skip class silently',
                        'result': 'You avoid the awkward conversation.',
                        'consequence': 'Academic probation warning arrives in mail.'
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
                'choices': [
                    {
                        'text': 'Attend case manager meeting',
                        'result': 'Housing secured.',
                        'consequence': 'Missed work. FIRED.'
                    },
                    {
                        'text': 'Go to work shift',
                        'result': 'Income secured.',
                        'consequence': '30-day placement at risk notice received.'
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
                choice_rect = pygame.Rect(150, choice_y + i * 80, 500, 65)
                if choice_rect.collidepoint(pos):
                    self.hovered_choice = i

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            choice_y = 300
            for i in range(len(choices)):
                choice_rect = pygame.Rect(150, choice_y + i * 80, 500, 65)
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

    def render(self, screen):
        """Render the dialogue"""
        if not self.scenario_data:
            return

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.fill((30, 30, 40))
        overlay.set_alpha(240)
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
        prompt = prompt_font.render(self.scenario_data['prompt'], True, (200, 150, 150))
        screen.blit(prompt, (150, 250))

        # Choices
        choices = self.scenario_data['choices']
        choice_font = pygame.font.Font(None, 26)
        choice_y = 300

        for i, choice in enumerate(choices):
            rect = pygame.Rect(150, choice_y + i * 80, 500, 65)

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
            screen.blit(num, (rect.x + 10, rect.y + 22))

            # Choice text
            text = choice_font.render(choice['text'], True, (220, 220, 230))
            screen.blit(text, (rect.x + 50, rect.y + 22))

        # Show result
        if self.show_result and self.selected_index >= 0:
            choice = choices[self.selected_index]

            result_y = choice_y + len(choices) * 80 + 10

            # Result box
            result_rect = pygame.Rect(100, result_y, 600, 100)
            pygame.draw.rect(screen, (50, 55, 65), result_rect)
            pygame.draw.rect(screen, (120, 130, 140), result_rect, 2)

            # Result text
            result_font = pygame.font.Font(None, 28)
            result_text = result_font.render(choice['result'], True, (150, 200, 150))
            screen.blit(result_text, (result_rect.x + 20, result_rect.y + 20))

            # Consequence
            cons_font = pygame.font.Font(None, 24)
            cons_text = cons_font.render(choice['consequence'], True, (200, 130, 130))
            screen.blit(cons_text, (result_rect.x + 20, result_rect.y + 55))

    def draw(self, screen):
        """Alias for render"""
        self.render(screen)

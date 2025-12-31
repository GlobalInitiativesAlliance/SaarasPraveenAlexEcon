"""
Choice Dialogue System for Part 6 - Systemic Barriers
Handles dialogue choices that demonstrate how specific language
and knowledge of the system affects outcomes
"""
import pygame


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

        # Scenarios for Part 6
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
                self.completed = True
            return True

        if not self.current_scenario:
            return False

        choices = self.current_scenario.get('choices', [])

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
            # Check if clicking on a choice
            mouse_pos = pygame.mouse.get_pos()
            choice_start_y = 380
            for i, _ in enumerate(choices):
                choice_rect = pygame.Rect(240, choice_start_y + i * 70, 800, 60)
                if choice_rect.collidepoint(mouse_pos):
                    self.selected_choice = i
                    self.make_choice()
                    break

        return True

    def make_choice(self):
        """Process the selected choice"""
        self.choice_made = True
        self.show_result = True
        self.result_timer = 240  # 4 seconds

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        if self.show_result:
            self.result_timer -= 1
            if self.result_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the choice dialogue"""
        if not self.active or not self.current_scenario:
            return

        # Background overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(245)
        overlay.fill((35, 35, 45))
        screen.blit(overlay, (0, 0))

        if self.show_result:
            self.render_result(screen)
        else:
            self.render_choices(screen)

    def render_choices(self, screen):
        """Render the choice selection screen"""
        scenario = self.current_scenario

        # Title
        title_font = pygame.font.Font(None, 42)
        title_text = scenario.get('title', 'Make a Choice')
        title_surface = title_font.render(title_text, True, (230, 230, 240))
        screen.blit(title_surface, (self.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 60))

        # Description
        desc_font = pygame.font.Font(None, 28)
        y = 120
        for line in scenario.get('description', []):
            desc_surface = desc_font.render(line, True, (180, 180, 190))
            screen.blit(desc_surface, (self.SCREEN_WIDTH // 2 - desc_surface.get_width() // 2, y))
            y += 35

        # Question
        question_font = pygame.font.Font(None, 32)
        question = scenario.get('question', '')
        question_surface = question_font.render(question, True, (255, 220, 150))
        screen.blit(question_surface, (self.SCREEN_WIDTH // 2 - question_surface.get_width() // 2, 300))

        # Choices
        choices = scenario.get('choices', [])
        choice_font = pygame.font.Font(None, 26)
        choice_start_y = 380

        for i, choice in enumerate(choices):
            # Choice box
            choice_rect = pygame.Rect(240, choice_start_y + i * 70, 800, 60)

            if i == self.selected_choice:
                pygame.draw.rect(screen, (70, 90, 110), choice_rect, border_radius=8)
                pygame.draw.rect(screen, (150, 180, 220), choice_rect, 3, border_radius=8)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(screen, (50, 50, 60), choice_rect, border_radius=8)
                pygame.draw.rect(screen, (80, 80, 90), choice_rect, 2, border_radius=8)
                text_color = (200, 200, 210)

            # Choice number
            num_text = f"[{i + 1}]"
            num_surface = choice_font.render(num_text, True, (150, 150, 160))
            screen.blit(num_surface, (choice_rect.x + 15, choice_rect.centery - num_surface.get_height() // 2))

            # Choice text
            choice_text = choice.get('text', '')
            choice_surface = choice_font.render(choice_text, True, text_color)
            screen.blit(choice_surface, (choice_rect.x + 60, choice_rect.centery - choice_surface.get_height() // 2))

        # Instructions
        inst_font = pygame.font.Font(None, 22)
        inst_text = "Use UP/DOWN or 1-4 to select, ENTER to confirm"
        inst_surface = inst_font.render(inst_text, True, (120, 120, 130))
        screen.blit(inst_surface, (self.SCREEN_WIDTH // 2 - inst_surface.get_width() // 2, 680))

    def render_result(self, screen):
        """Render the choice result"""
        scenario = self.current_scenario
        choices = scenario.get('choices', [])
        chosen = choices[self.selected_choice]

        # Result panel
        panel_rect = pygame.Rect(190, 150, 900, 420)
        pygame.draw.rect(screen, (45, 45, 55), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 110), panel_rect, 2, border_radius=10)

        # What you chose
        chose_font = pygame.font.Font(None, 28)
        chose_text = f"You chose: {chosen.get('text', '')}"
        chose_surface = chose_font.render(chose_text, True, (180, 180, 190))
        screen.blit(chose_surface, (panel_rect.x + 30, panel_rect.y + 30))

        # Result type indicator
        result_type = chosen.get('result', 'neutral')
        result_colors = {
            'good': (100, 200, 100),
            'partial': (200, 200, 100),
            'bad': (200, 100, 100),
            'mixed': (200, 150, 100),
            'honest': (150, 150, 200),
            'workshop': (200, 150, 100),
            'work': (200, 150, 100),
            'both': (200, 100, 100),
            'call': (200, 100, 100),
        }
        result_color = result_colors.get(result_type, (180, 180, 180))

        # Divider
        pygame.draw.line(screen, (80, 80, 90),
                         (panel_rect.x + 30, panel_rect.y + 70),
                         (panel_rect.right - 30, panel_rect.y + 70), 2)

        # Response text
        response_font = pygame.font.Font(None, 30)
        y = panel_rect.y + 100
        for line in chosen.get('response', []):
            response_surface = response_font.render(line, True, result_color)
            screen.blit(response_surface, (panel_rect.x + 40, y))
            y += 40

        # Systemic message
        if result_type in ['bad', 'both', 'call']:
            msg_font = pygame.font.Font(None, 26)
            msg_text = "The system creates no-win situations."
            msg_surface = msg_font.render(msg_text, True, (200, 100, 100))
            screen.blit(msg_surface, (panel_rect.centerx - msg_surface.get_width() // 2, panel_rect.y + 340))

        # Continue prompt
        if self.result_timer < 180:
            prompt_font = pygame.font.Font(None, 24)
            prompt_text = "Press any key to continue..."
            prompt_surface = prompt_font.render(prompt_text, True, (150, 150, 160))
            screen.blit(prompt_surface, (panel_rect.centerx - prompt_surface.get_width() // 2, panel_rect.y + 380))

    def start(self):
        """Start the choice dialogue"""
        self.active = True
        self.completed = False
        self.selected_choice = 0
        self.choice_made = False
        self.show_result = False

        # Default to first scenario if none set
        if not self.current_scenario and self.scenarios:
            first_key = list(self.scenarios.keys())[0]
            self.set_scenario_by_id(first_key)

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

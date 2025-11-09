"""
Choice Dialogue System
Work vs Study decision mechanics
Track consequences of choices
"""
import pygame

class ChoiceDialogueSystem:
    """Interactive decision system for work/study dilemmas"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Choice scenarios
        self.scenarios = [
            {
                'id': 'work_vs_exam',
                'title': 'Double Shift vs Exam',
                'description': [
                    'Your manager just called:',
                    '"We need you for a double shift tonight. $100 bonus."',
                    '',
                    'But you have an important exam tomorrow morning.',
                    'You haven\'t studied enough yet.'
                ],
                'choices': [
                    {
                        'text': 'Take the shift (+$100, risk failing exam)',
                        'money': 100,
                        'grade': -20,
                        'stress': 15
                    },
                    {
                        'text': 'Call out sick to study (-$50 lost wages, keep grades)',
                        'money': -50,
                        'grade': 10,
                        'stress': 5
                    }
                ]
            }
        ]

        self.current_scenario = 0
        self.selected_choice = None
        self.show_consequence = False

        # Player stats (visual representation)
        self.player_money = 150
        self.player_grade = 75
        self.player_stress = 60

        # UI elements
        self.choice_buttons = []

    def handle_event(self, event):
        """Handle choice selection"""
        if not self.active or self.completed:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            if not self.show_consequence:
                # Check choice buttons
                for i, button in enumerate(self.choice_buttons):
                    if button.collidepoint(mouse_pos):
                        scenario = self.scenarios[self.current_scenario]
                        self.selected_choice = scenario['choices'][i]
                        self.apply_choice()
                        self.show_consequence = True
                        break

            elif self.show_consequence:
                # Click to continue
                self.completed = True
                if self.objective_manager:
                    self.objective_manager.complete_objective("work_study_choice")

        elif event.type == pygame.KEYDOWN:
            if not self.show_consequence:
                scenario = self.scenarios[self.current_scenario]
                if event.key == pygame.K_1 and len(scenario['choices']) > 0:
                    self.selected_choice = scenario['choices'][0]
                    self.apply_choice()
                    self.show_consequence = True
                elif event.key == pygame.K_2 and len(scenario['choices']) > 1:
                    self.selected_choice = scenario['choices'][1]
                    self.apply_choice()
                    self.show_consequence = True

        return True

    def apply_choice(self):
        """Apply the consequences of the choice"""
        if self.selected_choice:
            self.player_money += self.selected_choice['money']
            self.player_grade += self.selected_choice['grade']
            self.player_stress += self.selected_choice['stress']

            # Clamp values
            self.player_money = max(0, self.player_money)
            self.player_grade = max(0, min(100, self.player_grade))
            self.player_stress = max(0, min(100, self.player_stress))

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

    def render(self, screen):
        """Render the choice dialogue interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))

        scenario = self.scenarios[self.current_scenario]

        # Main dialogue box
        dialog_rect = pygame.Rect(240, 150, 800, 420)
        pygame.draw.rect(screen, (40, 40, 50), dialog_rect)
        pygame.draw.rect(screen, (100, 100, 110), dialog_rect, 3)

        # Title
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render(scenario['title'], True, (255, 255, 255))
        title_x = dialog_rect.centerx - title_text.get_width() // 2
        screen.blit(title_text, (title_x, dialog_rect.y + 20))

        if not self.show_consequence:
            # Description
            desc_font = pygame.font.Font(None, 26)
            y_offset = 80
            for line in scenario['description']:
                if line:
                    line_surface = desc_font.render(line, True, (220, 220, 230))
                    line_x = dialog_rect.centerx - line_surface.get_width() // 2
                    screen.blit(line_surface, (dialog_rect.x + 40, dialog_rect.y + y_offset))
                y_offset += 30

            # Stats preview
            self.render_stats_preview(screen, dialog_rect)

            # Choice buttons
            self.choice_buttons = []
            choice_font = pygame.font.Font(None, 24)
            button_y = dialog_rect.y + 280

            for i, choice in enumerate(scenario['choices']):
                button_rect = pygame.Rect(dialog_rect.x + 50, button_y + (i * 60), 700, 50)
                self.choice_buttons.append(button_rect)

                # Button background
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    bg_color = (80, 80, 100)
                else:
                    bg_color = (60, 60, 80)

                pygame.draw.rect(screen, bg_color, button_rect)
                pygame.draw.rect(screen, (120, 120, 140), button_rect, 2)

                # Choice text with number
                choice_text = f"{i+1}. {choice['text']}"
                text_surface = choice_font.render(choice_text, True, (255, 255, 255))
                screen.blit(text_surface, (button_rect.x + 20, button_rect.centery - text_surface.get_height() // 2))

        else:
            # Show consequence
            self.render_consequence(screen, dialog_rect)

    def render_stats_preview(self, screen, dialog_rect):
        """Render current stats with preview of changes"""
        stats_font = pygame.font.Font(None, 22)

        # Stats box
        stats_rect = pygame.Rect(dialog_rect.x + 550, dialog_rect.y + 100, 200, 120)
        pygame.draw.rect(screen, (50, 50, 60), stats_rect)
        pygame.draw.rect(screen, (80, 80, 90), stats_rect, 1)

        stats_title = stats_font.render("Current Status:", True, (200, 200, 210))
        screen.blit(stats_title, (stats_rect.x + 10, stats_rect.y + 10))

        # Display stats
        stats = [
            ('Money:', f'${self.player_money}', (150, 255, 150)),
            ('Grades:', f'{self.player_grade}%', (150, 150, 255)),
            ('Stress:', f'{self.player_stress}%', (255, 150, 150))
        ]

        y = stats_rect.y + 40
        for label, value, color in stats:
            label_surface = stats_font.render(label, True, (180, 180, 190))
            value_surface = stats_font.render(value, True, color)
            screen.blit(label_surface, (stats_rect.x + 10, y))
            screen.blit(value_surface, (stats_rect.x + 100, y))
            y += 25

    def render_consequence(self, screen, dialog_rect):
        """Render the consequence of the choice"""
        cons_font = pygame.font.Font(None, 32)
        detail_font = pygame.font.Font(None, 26)

        # Title
        title = "Choice Made!"
        title_surface = cons_font.render(title, True, (255, 255, 255))
        title_x = dialog_rect.centerx - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, dialog_rect.y + 60))

        # Choice description
        choice_text = self.selected_choice['text']
        choice_surface = detail_font.render(choice_text, True, (200, 200, 210))
        choice_x = dialog_rect.centerx - choice_surface.get_width() // 2
        screen.blit(choice_surface, (choice_x, dialog_rect.y + 120))

        # Consequences
        y = dialog_rect.y + 180
        consequences = []

        if self.selected_choice['money'] > 0:
            consequences.append((f"+${self.selected_choice['money']}", (100, 255, 100)))
        elif self.selected_choice['money'] < 0:
            consequences.append((f"${self.selected_choice['money']}", (255, 100, 100)))

        if self.selected_choice['grade'] > 0:
            consequences.append((f"Grades +{self.selected_choice['grade']}%", (100, 255, 100)))
        elif self.selected_choice['grade'] < 0:
            consequences.append((f"Grades {self.selected_choice['grade']}%", (255, 100, 100)))

        if self.selected_choice['stress'] > 0:
            consequences.append((f"Stress +{self.selected_choice['stress']}%", (255, 150, 100)))

        for text, color in consequences:
            cons_surface = cons_font.render(text, True, color)
            cons_x = dialog_rect.centerx - cons_surface.get_width() // 2
            screen.blit(cons_surface, (cons_x, y))
            y += 40

        # Updated stats
        self.render_updated_stats(screen, dialog_rect)

        # Continue prompt
        prompt_font = pygame.font.Font(None, 24)
        prompt = "Click to continue..."
        prompt_surface = prompt_font.render(prompt, True, (150, 150, 160))
        prompt_x = dialog_rect.centerx - prompt_surface.get_width() // 2
        screen.blit(prompt_surface, (prompt_x, dialog_rect.bottom - 40))

    def render_updated_stats(self, screen, dialog_rect):
        """Render updated stats after choice"""
        stats_font = pygame.font.Font(None, 22)

        # Stats box
        stats_rect = pygame.Rect(dialog_rect.centerx - 100, dialog_rect.y + 300, 200, 90)
        pygame.draw.rect(screen, (50, 50, 60), stats_rect)
        pygame.draw.rect(screen, (80, 80, 90), stats_rect, 1)

        stats_title = stats_font.render("New Status:", True, (200, 200, 210))
        title_x = stats_rect.centerx - stats_title.get_width() // 2
        screen.blit(stats_title, (title_x, stats_rect.y + 10))

        # Display updated stats
        stats = [
            (f'Money: ${self.player_money}', (150, 255, 150) if self.player_money > 50 else (255, 150, 150)),
            (f'Grades: {self.player_grade}%', (150, 255, 150) if self.player_grade >= 70 else (255, 150, 150)),
            (f'Stress: {self.player_stress}%', (150, 255, 150) if self.player_stress < 70 else (255, 150, 150))
        ]

        y = stats_rect.y + 35
        for text, color in stats:
            stat_surface = stats_font.render(text, True, color)
            stat_x = stats_rect.centerx - stat_surface.get_width() // 2
            screen.blit(stat_surface, (stat_x, y))
            y += 20

    def start(self):
        """Start the choice dialogue"""
        self.active = True
        self.completed = False
        self.current_scenario = 0
        self.selected_choice = None
        self.show_consequence = False

    def stop(self):
        """Stop the dialogue system"""
        self.active = False
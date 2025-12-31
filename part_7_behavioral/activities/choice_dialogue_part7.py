"""
Choice Dialogue System for Part 7
Handles spending choices, self-sabotage responses, shift conflicts, and food choices
Each choice affects emotional meters (guilt, anxiety)
"""
import pygame

class ChoiceDialoguePart7:
    """Choice-based dialogues with emotional consequences"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Current scenario
        self.current_scenario = None
        self.selected_choice = None

        # Emotional meters (tracked across scenarios)
        self.guilt_level = 0.0
        self.anxiety_level = 0.0

        # Scenarios with choices and consequences
        self.scenarios = {
            'spending_choice': {
                'title': 'What do you do with the $40?',
                'context': 'You have $40 left after bills. Next paycheck is in two weeks.',
                'choices': [
                    {
                        'text': 'Save it for emergencies',
                        'response': 'You put the money in a jar. It feels responsible, but the jar is hard to access when you need it quickly.',
                        'effect': 'anxiety',
                        'effect_amount': 0.2,
                        'effect_text': 'Anxiety +20% (What if something comes up?)'
                    },
                    {
                        'text': 'Buy something nice for yourself',
                        'response': 'You treat yourself to a small comfort - maybe a coffee or cheap earbuds. For a moment, you feel normal.',
                        'effect': 'guilt',
                        'effect_amount': 0.4,
                        'effect_text': 'Guilt +40% (Should I have saved that?)'
                    },
                    {
                        'text': 'Ignore it and not think about money',
                        'response': 'You close your eyes to the problem. The $40 sits there, slowly disappearing on small things.',
                        'effect': 'anxiety',
                        'effect_amount': 0.5,
                        'effect_text': 'Anxiety +50% (Money stress builds up)'
                    }
                ],
                'selected_index': -1
            },
            'self_sabotage': {
                'title': 'Your manager just praised your work',
                'context': '"You\'re doing great! Keep it up - you could go far here."',
                'choices': [
                    {
                        'text': '"Thank you, I\'m trying my best"',
                        'response': 'You accept the compliment. It feels strange, like you don\'t quite deserve it.',
                        'effect': 'anxiety',
                        'effect_amount': 0.15,
                        'effect_text': 'Slight anxiety (Waiting for the other shoe to drop)'
                    },
                    {
                        'text': '"It was nothing special..."',
                        'response': 'You deflect the praise. It\'s safer not to raise expectations you might not meet.',
                        'effect': 'guilt',
                        'effect_amount': 0.2,
                        'effect_text': 'Guilt +20% (Why do I do this to myself?)'
                    },
                    {
                        'text': 'Change the subject awkwardly',
                        'response': 'You mumble something about the weather. The moment passes, but so does the opportunity.',
                        'effect': 'anxiety',
                        'effect_amount': 0.3,
                        'effect_text': 'Anxiety +30% (Did I mess that up?)'
                    }
                ],
                'selected_index': -1
            },
            'shift_conflict': {
                'title': 'Extra Shift vs ILP Meeting',
                'context': 'Your manager offers an extra shift, but it conflicts with your mandatory ILP meeting.',
                'choices': [
                    {
                        'text': 'Take the shift (need the money)',
                        'response': 'You take the shift. The extra $50 helps, but you\'ll have to reschedule ILP again...',
                        'effect': 'anxiety',
                        'effect_amount': 0.4,
                        'effect_text': 'Anxiety +40% (ILP might drop you)'
                    },
                    {
                        'text': 'Go to ILP meeting (benefits at risk)',
                        'response': 'You keep the ILP meeting. Your manager looks disappointed. "Maybe next time then."',
                        'effect': 'guilt',
                        'effect_amount': 0.3,
                        'effect_text': 'Guilt +30% (Letting the team down)'
                    },
                    {
                        'text': 'Ask to leave shift early',
                        'response': '"That\'s not really how it works here." The manager shakes their head.',
                        'effect': 'anxiety',
                        'effect_amount': 0.35,
                        'effect_text': 'Anxiety +35% (Now they think I\'m difficult)'
                    }
                ],
                'selected_index': -1
            },
            'food_choice': {
                'title': 'Grocery Shopping Decision',
                'context': 'Fresh fruit costs $8. A pack of instant ramen costs $2. You have $12 for food this week.',
                'choices': [
                    {
                        'text': 'Buy the fresh fruit',
                        'response': 'You buy the fruit. It\'s healthier, but you\'ll be short on food by Thursday.',
                        'effect': 'anxiety',
                        'effect_amount': 0.3,
                        'effect_text': 'Anxiety +30% (Will this be enough?)'
                    },
                    {
                        'text': 'Buy the ramen packs',
                        'response': 'You buy several ramen packs. You\'ll have enough to eat, but you feel tired thinking about another week of sodium.',
                        'effect': 'guilt',
                        'effect_amount': 0.25,
                        'effect_text': 'Guilt +25% (I should eat better)'
                    },
                    {
                        'text': 'Split between both',
                        'response': 'You grab one fruit and some ramen. A compromise that leaves neither need fully met.',
                        'effect': 'anxiety',
                        'effect_amount': 0.2,
                        'effect_text': 'Anxiety +20% (Never quite enough)'
                    }
                ],
                'selected_index': -1
            }
        }

        # UI state
        self.show_response = False
        self.response_timer = 0
        self.hover_index = -1

    def set_scenario(self, scenario_id):
        """Set the current scenario"""
        if scenario_id in self.scenarios:
            self.current_scenario = self.scenarios[scenario_id]
            self.current_scenario['selected_index'] = -1
            self.selected_choice = None
            self.show_response = False

    def handle_event(self, event):
        """Handle choice selection"""
        if not self.active or self.completed:
            return False

        if self.show_response:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.completed = True
            return True

        if not self.current_scenario:
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check choice buttons
            for i, choice in enumerate(self.current_scenario['choices']):
                button_rect = self.get_choice_rect(i)
                if button_rect.collidepoint(mouse_pos):
                    self.select_choice(i)
                    break

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hover_index = -1
            for i in range(len(self.current_scenario['choices'])):
                if self.get_choice_rect(i).collidepoint(mouse_pos):
                    self.hover_index = i
                    break

        return True

    def get_choice_rect(self, index):
        """Get rectangle for choice button"""
        button_width = 700
        button_height = 60
        x = self.SCREEN_WIDTH // 2 - button_width // 2
        y = 350 + index * 80
        return pygame.Rect(x, y, button_width, button_height)

    def select_choice(self, index):
        """Process the selected choice"""
        self.current_scenario['selected_index'] = index
        self.selected_choice = self.current_scenario['choices'][index]

        # Apply emotional effect
        if self.selected_choice['effect'] == 'guilt':
            self.guilt_level = min(1.0, self.guilt_level + self.selected_choice['effect_amount'])
        elif self.selected_choice['effect'] == 'anxiety':
            self.anxiety_level = min(1.0, self.anxiety_level + self.selected_choice['effect_amount'])

        self.show_response = True
        self.response_timer = 180

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        if self.show_response:
            self.response_timer -= 1
            if self.response_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the choice dialogue"""
        if not self.active:
            return

        # Background
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(250)
        overlay.fill((240, 238, 235))
        screen.blit(overlay, (0, 0))

        if not self.current_scenario:
            return

        # Emotional meters at top
        self.render_meters(screen)

        if not self.show_response:
            # Title
            title_font = pygame.font.Font(None, 42)
            title_text = title_font.render(self.current_scenario['title'], True, (40, 40, 50))
            screen.blit(title_text, (self.SCREEN_WIDTH // 2 - title_text.get_width() // 2, 120))

            # Context
            context_font = pygame.font.Font(None, 28)
            context_text = context_font.render(self.current_scenario['context'], True, (80, 80, 90))
            screen.blit(context_text, (self.SCREEN_WIDTH // 2 - context_text.get_width() // 2, 180))

            # Instruction
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("Choose your response:", True, (100, 100, 110))
            screen.blit(inst_text, (self.SCREEN_WIDTH // 2 - inst_text.get_width() // 2, 300))

            # Choice buttons
            self.render_choices(screen)

        else:
            self.render_response(screen)

    def render_meters(self, screen):
        """Render guilt and anxiety meters"""
        meter_width = 150
        meter_height = 20
        y = 30

        # Guilt meter
        guilt_rect = pygame.Rect(50, y, meter_width, meter_height)
        pygame.draw.rect(screen, (220, 220, 220), guilt_rect)
        if self.guilt_level > 0:
            fill_width = int(self.guilt_level * meter_width)
            fill_rect = pygame.Rect(guilt_rect.x, guilt_rect.y, fill_width, meter_height)
            pygame.draw.rect(screen, (180, 100, 180), fill_rect)
        pygame.draw.rect(screen, (100, 100, 110), guilt_rect, 2)

        label_font = pygame.font.Font(None, 18)
        guilt_label = label_font.render("Guilt", True, (100, 100, 110))
        screen.blit(guilt_label, (guilt_rect.x, guilt_rect.y - 16))

        # Anxiety meter
        anxiety_rect = pygame.Rect(self.SCREEN_WIDTH - 200, y, meter_width, meter_height)
        pygame.draw.rect(screen, (220, 220, 220), anxiety_rect)
        if self.anxiety_level > 0:
            fill_width = int(self.anxiety_level * meter_width)
            fill_rect = pygame.Rect(anxiety_rect.x, anxiety_rect.y, fill_width, meter_height)
            pygame.draw.rect(screen, (200, 150, 100), fill_rect)
        pygame.draw.rect(screen, (100, 100, 110), anxiety_rect, 2)

        anxiety_label = label_font.render("Anxiety", True, (100, 100, 110))
        screen.blit(anxiety_label, (anxiety_rect.x, anxiety_rect.y - 16))

    def render_choices(self, screen):
        """Render choice buttons"""
        choice_font = pygame.font.Font(None, 26)

        for i, choice in enumerate(self.current_scenario['choices']):
            button_rect = self.get_choice_rect(i)

            # Button color based on hover
            if i == self.hover_index:
                color = (230, 240, 255)
                border_color = (100, 150, 200)
            else:
                color = (255, 255, 255)
                border_color = (180, 180, 190)

            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)

            # Choice number
            num_text = choice_font.render(f"{i+1}.", True, (100, 100, 150))
            screen.blit(num_text, (button_rect.x + 15, button_rect.centery - 10))

            # Choice text
            text = choice_font.render(choice['text'], True, (40, 40, 50))
            screen.blit(text, (button_rect.x + 50, button_rect.centery - 10))

    def render_response(self, screen):
        """Render the response after choice"""
        # Response panel
        panel_rect = pygame.Rect(self.SCREEN_WIDTH // 2 - 350, 180, 700, 340)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect)
        pygame.draw.rect(screen, (150, 150, 160), panel_rect, 3)

        # Your choice
        choice_font = pygame.font.Font(None, 28)
        choice_label = choice_font.render("You chose:", True, (80, 80, 90))
        screen.blit(choice_label, (panel_rect.x + 30, panel_rect.y + 30))

        choice_text = choice_font.render(f'"{self.selected_choice["text"]}"', True, (60, 100, 150))
        screen.blit(choice_text, (panel_rect.x + 30, panel_rect.y + 60))

        # Response
        response_font = pygame.font.Font(None, 24)

        # Word wrap response
        words = self.selected_choice['response'].split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if response_font.size(test_line)[0] > panel_rect.width - 60:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        y = panel_rect.y + 110
        for line in lines:
            line_surface = response_font.render(line, True, (60, 60, 70))
            screen.blit(line_surface, (panel_rect.x + 30, y))
            y += 25

        # Effect
        effect_font = pygame.font.Font(None, 26)
        effect_color = (180, 100, 180) if self.selected_choice['effect'] == 'guilt' else (200, 150, 100)
        effect_text = effect_font.render(self.selected_choice['effect_text'], True, effect_color)
        screen.blit(effect_text, (panel_rect.centerx - effect_text.get_width() // 2, panel_rect.y + 250))

        # Continue prompt
        if self.response_timer < 120:
            prompt_font = pygame.font.Font(None, 22)
            prompt = "Press any key to continue..."
            prompt_surface = prompt_font.render(prompt, True, (120, 120, 130))
            prompt_x = panel_rect.centerx - prompt_surface.get_width() // 2
            screen.blit(prompt_surface, (prompt_x, panel_rect.bottom - 30))

    def start(self):
        """Start the choice dialogue"""
        self.active = True
        self.completed = False
        self.show_response = False
        self.hover_index = -1
        self.selected_choice = None

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

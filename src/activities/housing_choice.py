"""
Housing Choice Activity
Player must decide between taking cash-for-keys or fighting eviction
"""

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class HousingChoice:
    """Critical decision point - take money or fight together"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False
        self.choice_made = None

        # Choice options with consequences
        self.choices = {
            'take_money': {
                'title': 'Take the $2,000',
                'pros': [
                    'Get $2,000 cash immediately',
                    'Avoid eviction on your record',
                    'Can use money for new deposit',
                    'Peaceful transition'
                ],
                'cons': [
                    'Enable gentrification',
                    'Abandon your neighbors',
                    'Start over somewhere else',
                    'They win without a fight'
                ],
                'outcome': 'You take the money and leave quietly.'
            },
            'fight': {
                'title': 'Fight with Tenants',
                'pros': [
                    'Stand in solidarity',
                    'Might win and stay',
                    'Learn to organize',
                    'Make them work for it'
                ],
                'cons': [
                    'Risk eviction record',
                    'Legal battles ahead',
                    'No guaranteed win',
                    'Stress and uncertainty'
                ],
                'outcome': 'You join the fight for tenant rights.'
            }
        }

        self.selected_choice = 'take_money'
        self.confirmation_phase = False
        self.animation_timer = 0

    def start(self):
        """Start the choice activity"""
        self.active = True
        self.completed = False
        self.choice_made = None
        self.selected_choice = 'take_money'
        self.confirmation_phase = False
        self.animation_timer = 0

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update animation timer
        self.animation_timer += dt

    def handle_event(self, event):
        """Handle player input"""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not self.confirmation_phase:
                # Can't escape this choice
                return True

            elif event.key == pygame.K_1:
                self.selected_choice = 'take_money'
                if self.confirmation_phase:
                    self.make_choice('take_money')

            elif event.key == pygame.K_2:
                self.selected_choice = 'fight'
                if self.confirmation_phase:
                    self.make_choice('fight')

            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                # Toggle between choices
                if self.selected_choice == 'take_money':
                    self.selected_choice = 'fight'
                else:
                    self.selected_choice = 'take_money'

            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if not self.confirmation_phase:
                    self.confirmation_phase = True
                else:
                    self.make_choice(self.selected_choice)

            elif event.key == pygame.K_BACKSPACE:
                if self.confirmation_phase:
                    self.confirmation_phase = False

        return True

    def make_choice(self, choice):
        """Finalize the player's choice"""
        self.choice_made = choice
        self.complete()

    def render(self, screen):
        """Render the choice interface"""
        if not self.active:
            return

        # Dark background
        screen.fill((15, 15, 25))

        # Fonts
        title_font = pygame.font.Font(None, 56)
        header_font = pygame.font.Font(None, 36)
        item_font = pygame.font.Font(None, 24)
        desc_font = pygame.font.Font(None, 20)

        # Main title
        title = "THE IMPOSSIBLE CHOICE"
        title_text = title_font.render(title, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title_text, title_rect)

        # Subtitle
        subtitle = "Your building has been sold. You must decide."
        sub_text = item_font.render(subtitle, True, (180, 180, 180))
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(sub_text, sub_rect)

        # Draw choice panels
        panel_width = 380
        panel_height = 400
        panel_y = 150

        # Left panel - Take money
        left_x = SCREEN_WIDTH // 2 - panel_width - 20
        self.draw_choice_panel(
            screen,
            'take_money',
            left_x,
            panel_y,
            panel_width,
            panel_height,
            self.selected_choice == 'take_money'
        )

        # VS divider
        vs_text = header_font.render("VS", True, (255, 255, 100))
        vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height // 2))
        screen.blit(vs_text, vs_rect)

        # Right panel - Fight
        right_x = SCREEN_WIDTH // 2 + 20
        self.draw_choice_panel(
            screen,
            'fight',
            right_x,
            panel_y,
            panel_width,
            panel_height,
            self.selected_choice == 'fight'
        )

        # Instructions
        if not self.confirmation_phase:
            instructions = [
                "Use ← → or 1/2 to select",
                "Press SPACE to confirm choice"
            ]
        else:
            instructions = [
                f"Are you sure you want to: {self.choices[self.selected_choice]['title']}?",
                "Press 1 or 2 to confirm, BACKSPACE to reconsider"
            ]

        inst_y = panel_y + panel_height + 40
        for instruction in instructions:
            inst_text = item_font.render(instruction, True, (200, 200, 200))
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
            screen.blit(inst_text, inst_rect)
            inst_y += 30

        # Warning at bottom
        warning = "This decision will determine your ending"
        warn_text = header_font.render(warning, True, (255, 100, 100))
        warn_rect = warn_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(warn_text, warn_rect)

    def draw_choice_panel(self, screen, choice_key, x, y, width, height, selected):
        """Draw a choice panel with pros and cons"""
        choice = self.choices[choice_key]

        # Panel background
        if selected:
            color = (40, 40, 80) if not self.confirmation_phase else (60, 60, 100)
            border_color = (255, 255, 100)
            border_width = 3
        else:
            color = (25, 25, 35)
            border_color = (100, 100, 100)
            border_width = 1

        pygame.draw.rect(screen, color, (x, y, width, height))
        pygame.draw.rect(screen, border_color, (x, y, width, height), border_width)

        # Fonts
        header_font = pygame.font.Font(None, 32)
        item_font = pygame.font.Font(None, 20)

        # Choice number
        num_text = header_font.render(f"[{1 if choice_key == 'take_money' else 2}]", True, (255, 255, 100))
        screen.blit(num_text, (x + 10, y + 10))

        # Title
        title_text = header_font.render(choice['title'], True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(x + width // 2, y + 35))
        screen.blit(title_text, title_rect)

        # Pros section
        pros_y = y + 70
        pros_header = item_font.render("PROS:", True, (100, 255, 100))
        screen.blit(pros_header, (x + 20, pros_y))

        pros_y += 25
        for pro in choice['pros']:
            pro_text = item_font.render(f"+ {pro}", True, (150, 255, 150))
            screen.blit(pro_text, (x + 30, pros_y))
            pros_y += 22

        # Cons section
        cons_y = pros_y + 20
        cons_header = item_font.render("CONS:", True, (255, 100, 100))
        screen.blit(cons_header, (x + 20, cons_y))

        cons_y += 25
        for con in choice['cons']:
            con_text = item_font.render(f"- {con}", True, (255, 150, 150))
            screen.blit(con_text, (x + 30, cons_y))
            cons_y += 22

        # Outcome preview
        if selected and self.confirmation_phase:
            outcome_y = y + height - 40
            outcome_text = item_font.render(choice['outcome'], True, (255, 255, 200))
            outcome_rect = outcome_text.get_rect(center=(x + width // 2, outcome_y))
            screen.blit(outcome_text, outcome_rect)

    def complete(self):
        """Complete the activity with the choice made"""
        if not self.active:
            return

        self.active = False
        self.completed = True

        # Update objective based on choice
        current = self.objective_manager.get_current_objective()
        if current and current.id == 'final_decision':
            self.objective_manager.complete_objective('final_decision')

            # Set the path based on choice
            if self.choice_made == 'take_money':
                # Path A: Take the money
                print("Player chose: Take the money and leave")
                # The game should now progress to 'moving_out' objective
            else:
                # Path B: Fight together
                print("Player chose: Fight with other tenants")
                # The game should now progress to 'court_battle' objective

        return True

    def is_active(self):
        """Check if activity is active"""
        return self.active

    def is_completed(self):
        """Check if activity was completed"""
        return self.completed

    def get_choice(self):
        """Get the choice that was made"""
        return self.choice_made
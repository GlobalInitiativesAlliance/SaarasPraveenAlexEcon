"""
Choice Dialogue System for Part 7
Handles spending choices, self-sabotage responses, shift conflicts, and food choices
Each choice affects emotional meters (guilt, anxiety)
"""
import pygame
import math
import time

from .behavioral_visual_base import (
    BehavioralUIColors, BehavioralUIMetrics, UIAnimation,
    BehavioralVisualHelpers, behavioral_visuals
)
from .behavioral_particles import behavioral_particles


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

        # Emotional meters (tracked across scenarios) with animations
        self.guilt_level = 0.0
        self.guilt_animation = UIAnimation(0.0, 0.0, 0.12)
        self.anxiety_level = 0.0
        self.anxiety_animation = UIAnimation(0.0, 0.0, 0.12)

        # Scenarios with choices and consequences
        self.scenarios = {
            'spending_choice': {
                'title': 'What do you do with the $40?',
                'context': 'You have $40 left after bills. Next paycheck is in two weeks.',
                'icon': 'money',
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
                'icon': 'work',
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
                'icon': 'conflict',
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
                'icon': 'food',
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
        self.response_animation = UIAnimation(0, 0, 0.1)
        self.hover_index = -1

        # Effect flash animation
        self.effect_flash = UIAnimation(0, 0, 0.15)
        self.last_effect_type = None

    def set_scenario(self, scenario_id):
        """Set the current scenario"""
        if scenario_id in self.scenarios:
            self.current_scenario = self.scenarios[scenario_id]
            self.current_scenario['selected_index'] = -1
            self.selected_choice = None
            self.show_response = False
            self.response_animation = UIAnimation(0, 0, 0.1)

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
        button_width = 720
        button_height = 65
        x = self.SCREEN_WIDTH // 2 - button_width // 2
        y = 340 + index * 85
        return pygame.Rect(x, y, button_width, button_height)

    def select_choice(self, index):
        """Process the selected choice"""
        self.current_scenario['selected_index'] = index
        self.selected_choice = self.current_scenario['choices'][index]

        # Apply emotional effect
        self.last_effect_type = self.selected_choice['effect']
        if self.selected_choice['effect'] == 'guilt':
            self.guilt_level = min(1.0, self.guilt_level + self.selected_choice['effect_amount'])
            self.guilt_animation.target = self.guilt_level
            behavioral_particles.emit_guilt_particles(150, 50)
        elif self.selected_choice['effect'] == 'anxiety':
            self.anxiety_level = min(1.0, self.anxiety_level + self.selected_choice['effect_amount'])
            self.anxiety_animation.target = self.anxiety_level
            behavioral_particles.emit_anxiety_swirl(self.SCREEN_WIDTH - 150, 50)

        self.effect_flash.current = 1.0
        self.effect_flash.target = 0.0

        self.show_response = True
        self.response_timer = 240
        self.response_animation.target = 1.0

        # Emit choice particles
        choice_rect = self.get_choice_rect(index)
        behavioral_particles.emit_decision_sparkle(choice_rect.centerx, choice_rect.centery)

    def update(self, dt):
        """Update dialogue state"""
        if not self.active:
            return

        # Update animations
        self.guilt_animation.update(dt)
        self.anxiety_animation.update(dt)
        self.response_animation.update(dt)
        self.effect_flash.update(dt)
        behavioral_particles.update(dt)

        if self.show_response:
            self.response_timer -= 1
            if self.response_timer <= 0:
                self.completed = True

    def render(self, screen):
        """Render the choice dialogue"""
        if not self.active:
            return

        # Background
        screen.fill(BehavioralUIColors.BG_CALM)

        if not self.current_scenario:
            return

        # Emotional meters at top
        self._draw_meters(screen)

        if not self.show_response:
            # Title with icon
            self._draw_title(screen)

            # Context
            self._draw_context(screen)

            # Instruction
            behavioral_visuals.draw_instruction_text(
                screen, "Choose your response:",
                self.SCREEN_WIDTH // 2, 295
            )

            # Choice buttons
            self._draw_choices(screen)

        else:
            self._draw_response(screen)

        # Draw particles on top
        behavioral_particles.draw(screen)

    def _draw_meters(self, screen):
        """Render guilt and anxiety meters with professional styling"""
        meter_width = 180
        meter_height = BehavioralUIMetrics.METER_HEIGHT

        # Guilt meter - left side
        guilt_rect = pygame.Rect(50, 35, meter_width, meter_height)

        # Flash effect when guilt changes
        if self.last_effect_type == 'guilt' and self.effect_flash.value > 0.1:
            flash_alpha = int(self.effect_flash.value * 100)
            BehavioralVisualHelpers.draw_glow(screen, guilt_rect,
                                             BehavioralUIColors.GUILT_PURPLE,
                                             flash_alpha, 8)

        behavioral_visuals.draw_emotional_meter(
            screen, guilt_rect,
            self.guilt_animation.value, "Guilt",
            BehavioralUIColors.GUILT_PURPLE
        )

        # Anxiety meter - right side
        anxiety_rect = pygame.Rect(self.SCREEN_WIDTH - 50 - meter_width, 35,
                                   meter_width, meter_height)

        # Flash effect when anxiety changes
        if self.last_effect_type == 'anxiety' and self.effect_flash.value > 0.1:
            flash_alpha = int(self.effect_flash.value * 100)
            BehavioralVisualHelpers.draw_glow(screen, anxiety_rect,
                                             BehavioralUIColors.ANXIETY_ORANGE,
                                             flash_alpha, 8)

        behavioral_visuals.draw_emotional_meter(
            screen, anxiety_rect,
            self.anxiety_animation.value, "Anxiety",
            BehavioralUIColors.ANXIETY_ORANGE
        )

    def _draw_title(self, screen):
        """Draw scenario title"""
        title_text = behavioral_visuals.fonts['heading'].render(
            self.current_scenario['title'], True, BehavioralUIColors.TEXT_PRIMARY
        )

        # Shadow
        shadow_text = behavioral_visuals.fonts['heading'].render(
            self.current_scenario['title'], True, (0, 0, 0)
        )
        shadow_surf = pygame.Surface(shadow_text.get_size(), pygame.SRCALPHA)
        shadow_surf.blit(shadow_text, (0, 0))
        shadow_surf.set_alpha(25)

        title_x = self.SCREEN_WIDTH // 2 - title_text.get_width() // 2
        screen.blit(shadow_surf, (title_x + 2, 102))
        screen.blit(title_text, (title_x, 100))

    def _draw_context(self, screen):
        """Draw scenario context"""
        # Context box
        context_text = self.current_scenario['context']

        # Calculate text width for wrapping
        max_width = 800
        words = context_text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if behavioral_visuals.fonts['body'].size(test_line)[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Draw context panel
        panel_height = 30 + len(lines) * 28
        panel_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - 420, 150,
            840, panel_height
        )

        BehavioralVisualHelpers.draw_shadow(screen, panel_rect, 4, 25,
                                           BehavioralUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)
        pygame.draw.rect(screen, BehavioralUIColors.CARD_BORDER, panel_rect, 1,
                        border_radius=BehavioralUIMetrics.RADIUS_MEDIUM)

        # Draw text
        y = panel_rect.y + 15
        for line in lines:
            line_surface = behavioral_visuals.fonts['body'].render(
                line, True, BehavioralUIColors.TEXT_SECONDARY
            )
            screen.blit(line_surface, (panel_rect.centerx - line_surface.get_width() // 2, y))
            y += 28

    def _draw_choices(self, screen):
        """Render choice buttons"""
        for i, choice in enumerate(self.current_scenario['choices']):
            button_rect = self.get_choice_rect(i)
            is_hover = i == self.hover_index

            behavioral_visuals.draw_choice_button(
                screen, button_rect,
                choice['text'], i,
                is_hover, False
            )

    def _draw_response(self, screen):
        """Render the response after choice"""
        anim_progress = self.response_animation.value

        # Response panel
        panel_width = 720
        panel_height = 380
        panel_rect = pygame.Rect(
            self.SCREEN_WIDTH // 2 - panel_width // 2,
            int(170 + (1 - anim_progress) * 40),
            panel_width,
            panel_height
        )

        # Draw modal container
        behavioral_visuals.draw_modal_container(
            screen, panel_rect,
            "Your Choice",
            BehavioralUIColors.CALM_BLUE,
            True
        )

        # Your choice text
        choice_y = panel_rect.y + 75
        choice_label = behavioral_visuals.fonts['small'].render(
            "You chose:", True, BehavioralUIColors.TEXT_MUTED
        )
        screen.blit(choice_label, (panel_rect.x + 35, choice_y))

        choice_text = behavioral_visuals.fonts['body_bold'].render(
            f'"{self.selected_choice["text"]}"', True, BehavioralUIColors.TEXT_PRIMARY
        )
        screen.blit(choice_text, (panel_rect.x + 35, choice_y + 25))

        # Response text with word wrap
        response_y = choice_y + 70
        words = self.selected_choice['response'].split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if behavioral_visuals.fonts['body'].size(test_line)[0] > panel_rect.width - 70:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        for line in lines:
            line_surface = behavioral_visuals.fonts['body'].render(
                line, True, BehavioralUIColors.TEXT_SECONDARY
            )
            screen.blit(line_surface, (panel_rect.x + 35, response_y))
            response_y += 26

        # Effect display with appropriate color
        effect_y = panel_rect.y + 270
        effect_color = (BehavioralUIColors.GUILT_PURPLE if self.selected_choice['effect'] == 'guilt'
                       else BehavioralUIColors.ANXIETY_ORANGE)

        # Effect badge
        effect_text = self.selected_choice['effect_text']
        effect_surface = behavioral_visuals.fonts['body_bold'].render(
            effect_text, True, effect_color
        )

        # Background for effect
        effect_rect = pygame.Rect(
            panel_rect.centerx - effect_surface.get_width() // 2 - 15,
            effect_y - 5,
            effect_surface.get_width() + 30,
            effect_surface.get_height() + 10
        )

        # Light colored background
        bg_color = BehavioralVisualHelpers.lighten_color(effect_color, 1.6)
        bg_color = (min(255, bg_color[0] + 80), min(255, bg_color[1] + 80), min(255, bg_color[2] + 80))
        pygame.draw.rect(screen, bg_color, effect_rect,
                        border_radius=BehavioralUIMetrics.RADIUS_SMALL)
        pygame.draw.rect(screen, effect_color, effect_rect, 2,
                        border_radius=BehavioralUIMetrics.RADIUS_SMALL)

        screen.blit(effect_surface, (panel_rect.centerx - effect_surface.get_width() // 2, effect_y))

        # Continue prompt
        if self.response_timer < 180:
            behavioral_visuals.draw_continue_prompt(
                screen, panel_rect.centerx, panel_rect.bottom - 30
            )

    def start(self):
        """Start the choice dialogue"""
        self.active = True
        self.completed = False
        self.show_response = False
        self.hover_index = -1
        self.selected_choice = None
        self.response_animation = UIAnimation(0, 0, 0.1)
        self.effect_flash = UIAnimation(0, 0, 0.15)
        self.last_effect_type = None

        # Sync animation values with current levels
        self.guilt_animation = UIAnimation(self.guilt_level, self.guilt_level, 0.12)
        self.anxiety_animation = UIAnimation(self.anxiety_level, self.anxiety_level, 0.12)

        # Clear particles
        behavioral_particles.clear()

    def stop(self):
        """Stop the dialogue"""
        self.active = False

    def draw(self, screen):
        """Alias for render to match activity interface"""
        self.render(screen)

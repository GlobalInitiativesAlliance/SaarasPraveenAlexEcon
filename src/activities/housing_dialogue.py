"""Housing Crisis Dialogue System"""

import pygame
import math
from shared.constants import *

class HousingDialogueActivity:
    """Animated dialogue system for housing crisis narrative"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False

        # Fonts
        self.speaker_font = pygame.font.Font(None, 28)
        self.dialogue_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Dialogue state
        self.current_dialogue_set = 0
        self.current_line = 0
        self.text_progress = 0
        self.text_speed = 0.5  # Characters per frame
        self.pause_timer = 0
        self.fade_in = 0

        # Visual elements
        self.portrait_bounce = 0
        self.text_wobble = 0

        # Define dialogue sequences
        self.dialogue_sets = [
            # Opening - Foster parent
            {
                'speaker': 'FOSTER PARENT',
                'portrait_color': (150, 100, 80),
                'lines': [
                    "Listen... you turn 18 tomorrow.",
                    "You know what that means, right?",
                    "The state stops paying for you.",
                    "You can't stay here anymore.",
                    "I'm sorry, but... you need to find somewhere else."
                ]
            },
            # Player thoughts
            {
                'speaker': 'YOUR THOUGHTS',
                'portrait_color': (100, 120, 200),
                'lines': [
                    "Eighteen. The magic number where suddenly you're an adult.",
                    "Except... where do I go?",
                    "No family. No savings. No credit history.",
                    "Just $73 in my pocket and a backpack of clothes.",
                    "How is anyone supposed to do this?"
                ]
            },
            # Case worker
            {
                'speaker': 'CASE WORKER',
                'portrait_color': (120, 150, 100),
                'lines': [
                    "I've compiled some housing resources for you.",
                    "There's transitional housing, but the waitlist is 6-8 months.",
                    "You could try finding a roommate...",
                    "Or maybe couch surf with friends for a while?",
                    "I know it's not ideal, but these are your options."
                ]
            },
            # Friend
            {
                'speaker': 'SARAH (FRIEND)',
                'portrait_color': (200, 120, 150),
                'lines': [
                    "Hey, I heard about your situation...",
                    "You can crash on my couch for a few nights.",
                    "But my parents... they don't really like guests.",
                    "So maybe like 3 nights max? Sorry.",
                    "I wish I could do more."
                ]
            },
            # Landlord
            {
                'speaker': 'LANDLORD',
                'portrait_color': (180, 140, 100),
                'lines': [
                    "First month, last month, and security deposit.",
                    "That's $2,800 upfront. Plus application fee.",
                    "I'll need proof of income - 3 times the rent.",
                    "Credit score above 650. And a co-signer.",
                    "No co-signer? Sorry, I can't help you."
                ]
            },
            # Your realization
            {
                'speaker': 'YOUR THOUGHTS',
                'portrait_color': (100, 120, 200),
                'lines': [
                    "Every option seems impossible.",
                    "The math doesn't work. The system doesn't work.",
                    "But I have to try something.",
                    "Tomorrow I'll have nowhere to sleep.",
                    "What do I do first?"
                ]
            }
        ]

        # Choice prompt
        self.choice_prompt = {
            'speaker': 'HOUSING ASSISTANCE',
            'portrait_color': (150, 150, 150),
            'lines': [
                "Welcome. Let's explore your housing options.",
                "Remember: There's no perfect choice here.",
                "Each path has its own challenges.",
                "What would you like to try first?"
            ]
        }

        self.showing_menu_prompt = False
        self.completed = False

    def start(self):
        """Start the dialogue sequence"""
        self.active = True
        self.current_dialogue_set = 0
        self.current_line = 0
        self.text_progress = 0
        self.fade_in = 0

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if key == pygame.K_SPACE or key == pygame.K_RETURN or key == pygame.K_e:
            current_set = self.dialogue_sets[self.current_dialogue_set] if not self.showing_menu_prompt else self.choice_prompt

            # If text is still animating, complete it instantly
            if self.text_progress < len(current_set['lines'][self.current_line]):
                self.text_progress = len(current_set['lines'][self.current_line])
            else:
                # Move to next line
                self.current_line += 1
                self.text_progress = 0

                # Check if we've finished this dialogue set
                if self.current_line >= len(current_set['lines']):
                    if self.showing_menu_prompt:
                        # End dialogue and mark as completed
                        # NOTE: Do NOT call complete_current_objective() here!
                        # The narrative/interior system should handle objective
                        # completion based on ALL required interactions being done
                        self.active = False
                        self.completed = True
                    else:
                        # Move to next dialogue set
                        self.current_dialogue_set += 1
                        self.current_line = 0

                        # Check if we've finished all dialogue
                        if self.current_dialogue_set >= len(self.dialogue_sets):
                            self.showing_menu_prompt = True
                            self.current_line = 0

        elif key == pygame.K_ESCAPE:
            # Skip to menu
            self.showing_menu_prompt = True
            self.current_line = 0
            self.text_progress = 0

    def update(self, dt):
        """Update dialogue animation"""
        if not self.active:
            return

        # Fade in effect
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + dt * 2)

        # Text animation
        current_set = self.dialogue_sets[self.current_dialogue_set] if not self.showing_menu_prompt else self.choice_prompt
        if self.current_line < len(current_set['lines']):
            target_length = len(current_set['lines'][self.current_line])
            if self.text_progress < target_length:
                self.text_progress = min(target_length, self.text_progress + self.text_speed)

        # Portrait animation
        self.portrait_bounce = math.sin(pygame.time.get_ticks() * 0.002) * 5
        self.text_wobble = math.sin(pygame.time.get_ticks() * 0.003) * 2

    def draw(self, screen):
        """Draw the dialogue interface"""
        if not self.active:
            return

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(int(180 * self.fade_in))
        overlay.fill((10, 10, 20))
        screen.blit(overlay, (0, 0))

        # Dialogue box
        box_height = 200
        box_y = SCREEN_HEIGHT - box_height - 50
        box_margin = 50

        # Box background with gradient effect
        box_rect = pygame.Rect(box_margin, box_y, SCREEN_WIDTH - box_margin * 2, box_height)

        # Draw box shadow
        shadow_rect = box_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=15)

        # Draw main box
        pygame.draw.rect(screen, (30, 30, 40), box_rect, border_radius=15)
        pygame.draw.rect(screen, (60, 60, 80), box_rect, width=3, border_radius=15)

        # Get current dialogue
        current_set = self.dialogue_sets[self.current_dialogue_set] if not self.showing_menu_prompt else self.choice_prompt

        # Draw speaker portrait
        portrait_x = box_rect.x + 30
        portrait_y = box_rect.y + 30 + self.portrait_bounce
        portrait_size = 80

        # Portrait background
        portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_size, portrait_size)
        pygame.draw.rect(screen, current_set['portrait_color'], portrait_rect, border_radius=40)
        pygame.draw.rect(screen, (255, 255, 255), portrait_rect, width=3, border_radius=40)

        # Simple face
        eye_y = portrait_y + 25
        pygame.draw.circle(screen, (0, 0, 0), (portrait_x + 25, eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (portrait_x + 55, eye_y), 5)

        # Talking animation
        if self.text_progress < len(current_set['lines'][self.current_line]) - 1:
            mouth_width = 20 + abs(math.sin(pygame.time.get_ticks() * 0.01) * 10)
            pygame.draw.ellipse(screen, (0, 0, 0),
                              (portrait_x + portrait_size//2 - mouth_width//2, portrait_y + 50, mouth_width, 15))
        else:
            pygame.draw.arc(screen, (0, 0, 0),
                          (portrait_x + 25, portrait_y + 45, 30, 20), 0, math.pi, 3)

        # Draw speaker name
        name_y = portrait_y - 30
        name_surf = self.speaker_font.render(current_set['speaker'], True, (255, 255, 255))
        name_rect = name_surf.get_rect(x=portrait_x, y=name_y)

        # Name background
        name_bg_rect = name_rect.inflate(20, 10)
        pygame.draw.rect(screen, current_set['portrait_color'], name_bg_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), name_bg_rect, width=2, border_radius=5)
        screen.blit(name_surf, name_rect)

        # Draw dialogue text
        text_x = portrait_x + portrait_size + 30
        text_y = box_rect.y + 40
        max_text_width = box_rect.width - (text_x - box_rect.x) - 30

        if self.current_line < len(current_set['lines']):
            # Get the current line of text
            full_text = current_set['lines'][self.current_line]
            displayed_text = full_text[:int(self.text_progress)]

            # Word wrap
            words = displayed_text.split(' ')
            lines = []
            current_line_text = ""

            for word in words:
                test_line = current_line_text + word + " "
                if self.dialogue_font.size(test_line)[0] < max_text_width:
                    current_line_text = test_line
                else:
                    if current_line_text:
                        lines.append(current_line_text.strip())
                    current_line_text = word + " "

            if current_line_text:
                lines.append(current_line_text.strip())

            # Draw each line
            for i, line in enumerate(lines):
                text_surf = self.dialogue_font.render(line, True, (255, 255, 255))
                screen.blit(text_surf, (text_x, text_y + i * 30))

            # Draw blinking cursor if still typing
            if self.text_progress < len(full_text) and pygame.time.get_ticks() % 500 < 250:
                cursor_x = text_x + self.dialogue_font.size(lines[-1] if lines else "")[0] + 5
                cursor_y = text_y + (len(lines) - 1) * 30
                pygame.draw.rect(screen, (255, 255, 255), (cursor_x, cursor_y, 2, 20))

        # Draw continue prompt
        if self.text_progress >= len(current_set['lines'][self.current_line]):
            prompt_text = "PRESS SPACE TO CONTINUE" if not self.showing_menu_prompt or self.current_line < len(self.choice_prompt['lines']) - 1 else "PRESS SPACE TO SEE OPTIONS"
            prompt_surf = self.small_font.render(prompt_text, True, (200, 200, 200))
            prompt_rect = prompt_surf.get_rect(center=(box_rect.centerx, box_rect.bottom - 20))

            # Blinking effect
            if pygame.time.get_ticks() % 1000 < 700:
                screen.blit(prompt_surf, prompt_rect)

        # Skip hint
        if not self.showing_menu_prompt:
            skip_text = "ESC - Skip to menu"
            skip_surf = self.small_font.render(skip_text, True, (150, 150, 150))
            skip_rect = skip_surf.get_rect(topright=(SCREEN_WIDTH - 30, 30))
            screen.blit(skip_surf, skip_rect)
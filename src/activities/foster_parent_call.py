"""
Foster Parent Phone Call Activity
A desperate call for help that ends in rejection
"""
import pygame
import math
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class FosterParentCall:
    """Interactive phone call to foster parents asking for co-signing help"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Phone UI dimensions
        self.phone_width = 320
        self.phone_height = 600
        self.phone_x = (SCREEN_WIDTH - self.phone_width) // 2
        self.phone_y = (SCREEN_HEIGHT - self.phone_height) // 2

        # Dialogue state
        self.current_stage = 'dialing'
        self.dialogue_index = 0
        self.choice_selected = -1
        self.emotional_state = 'hopeful'  # hopeful -> desperate -> defeated

        # Visual effects
        self.ring_timer = 0
        self.shake_amount = 0
        self.fade_alpha = 0

        # Call stages and dialogue
        self.setup_dialogue()

        # Fonts
        self.phone_font = pygame.font.Font(None, 24)
        self.speaker_font = pygame.font.Font(None, 28)
        self.dialogue_font = pygame.font.Font(None, 22)
        self.choice_font = pygame.font.Font(None, 20)

        # Colors
        self.phone_bg = (20, 20, 25)
        self.screen_color = (40, 40, 45)
        self.text_color = (255, 255, 255)
        self.foster_mom_color = (200, 150, 255)
        self.foster_dad_color = (150, 200, 255)
        self.player_color = (255, 220, 100)

        # Sound effects placeholders
        self.ring_sound = None
        self.hangup_sound = None

    def setup_dialogue(self):
        """Setup the dialogue tree for the phone call"""
        self.dialogues = {
            'dialing': [
                "Calling Foster Parents...",
                "Ring...",
                "Ring...",
                "Ring...",
                "*click*"
            ],
            'opening': {
                'speaker': 'Foster Mom',
                'text': "Hello? Oh... it's you. What do you need?",
                'choices': [
                    ('Explain about the apartment', 'explain'),
                    ('Ask how they are first', 'small_talk'),
                    ('Get straight to the point', 'direct')
                ]
            },
            'small_talk': {
                'speaker': 'Foster Mom',
                'text': "We're fine. Very busy with the new kids. Is that all?",
                'choices': [
                    ('Actually, I need help with something...', 'explain'),
                    ('The new kids? How many?', 'new_kids'),
                ]
            },
            'new_kids': {
                'speaker': 'Foster Mom',
                'text': "Three. Much younger than you were. Look, I don't have time for this.",
                'background': "Foster Dad: Who is it? Tell them we're eating dinner!",
                'choices': [
                    ('Wait, I really need help!', 'explain'),
                    ('Sorry for bothering you...', 'apologize')
                ]
            },
            'direct': {
                'speaker': 'Foster Mom',
                'text': "Of course you need something. You only call when you want something.",
                'choices': [
                    ("That's not fair, I just aged out yesterday!", 'defend'),
                    ("You're right, I'm desperate", 'desperate'),
                ]
            },
            'explain': {
                'speaker': 'You',
                'text': "I found an apartment but they need a co-signer. Someone with good credit.",
                'next': 'rejection_1'
            },
            'desperate': {
                'speaker': 'You',
                'text': "You're right. I'm desperate. I need a co-signer for an apartment. Please.",
                'next': 'rejection_1'
            },
            'defend': {
                'speaker': 'You',
                'text': "I literally just aged out! You were my parents for seven years!",
                'next': 'cold_response'
            },
            'cold_response': {
                'speaker': 'Foster Mom',
                'text': "We were your FOSTER parents. There's a difference. You're 18 now.",
                'next': 'rejection_1'
            },
            'rejection_1': {
                'speaker': 'Foster Mom',
                'text': "A co-signer? Absolutely not. We can't take on that liability.",
                'background': "Foster Dad: We're not a bank! They aged out!",
                'choices': [
                    ('Please, I have nowhere else to go', 'plead'),
                    ("I'll pay on time, I promise!", 'promise'),
                    ("After everything, you won't help?", 'guilt')
                ]
            },
            'plead': {
                'speaker': 'You',
                'text': "Please... I'm at the emergency shelter. I have nowhere else to go.",
                'next': 'rejection_2'
            },
            'promise': {
                'speaker': 'You',
                'text': "I'll get a job! I'll pay on time! You know I'm responsible!",
                'next': 'rejection_2'
            },
            'guilt': {
                'speaker': 'You',
                'text': "Seven years I lived with you. Doesn't that mean anything?",
                'next': 'harsh_rejection'
            },
            'harsh_rejection': {
                'speaker': 'Foster Mom',
                'text': "Don't try to guilt trip us. We did our job. You got food, shelter, and education.",
                'background': "Foster Dad: Hang up! This is ridiculous!",
                'next': 'rejection_2'
            },
            'rejection_2': {
                'speaker': 'Foster Mom',
                'text': "The answer is no. We have three new foster kids now. Our responsibility is to them.",
                'choices': [
                    ('But I have nobody else...', 'nobody'),
                    ('This is really how it ends?', 'ending'),
                    ('Fine. Forget I asked.', 'angry')
                ]
            },
            'nobody': {
                'speaker': 'You',
                'text': "I literally have nobody else. You were my only family for seven years...",
                'next': 'final_rejection'
            },
            'ending': {
                'speaker': 'You',
                'text': "After seven years, this is really how it ends? Just... goodbye?",
                'next': 'final_rejection'
            },
            'angry': {
                'speaker': 'You',
                'text': "Fine. Forget I asked. Forget I existed.",
                'next': 'hangup'
            },
            'final_rejection': {
                'speaker': 'Foster Mom',
                'text': "You aged out. That's how the system works. I'm sorry, but the answer is no.",
                'background': "Foster Dad: For crying out loud, hang up already!",
                'choices': [
                    ("Please don't do this...", 'last_plea'),
                    ('...', 'silence'),
                ]
            },
            'last_plea': {
                'speaker': 'You',
                'text': "Please... please don't do this. I'm scared.",
                'next': 'hangup'
            },
            'silence': {
                'speaker': 'You',
                'text': "...",
                'next': 'hangup'
            },
            'hangup': {
                'speaker': 'Foster Mom',
                'text': "Good luck. Don't call again.",
                'next': 'dial_tone'
            },
            'apologize': {
                'speaker': 'You',
                'text': "Sorry for bothering you during dinner...",
                'next': 'quick_hangup'
            },
            'quick_hangup': {
                'speaker': 'Foster Mom',
                'text': "Yes, well. Take care.",
                'next': 'dial_tone'
            },
            'dial_tone': {
                'speaker': None,
                'text': "*dial tone*",
                'final': True
            }
        }

        # Track path taken for emotional impact
        self.dialogue_path = []

    def start(self):
        """Start the phone call activity"""
        self.active = True
        self.completed = False
        self.current_stage = 'dialing'
        self.dialogue_index = 0
        self.ring_timer = 0

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if self.current_stage == 'dialing':
            if key == pygame.K_SPACE or key == pygame.K_e:
                # Advance through dialing sequence
                self.dialogue_index += 1
                if self.dialogue_index >= len(self.dialogues['dialing']):
                    self.current_stage = 'opening'
                    self.dialogue_index = 0

        elif self.current_stage == 'dial_tone':
            if key == pygame.K_SPACE or key == pygame.K_e:
                self.complete_call()

        elif key == pygame.K_ESCAPE:
            # Can't escape during the call - too important
            pass

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for choices"""
        if not self.active or button != 1:
            return

        # Check if clicking on a choice
        if self.current_stage in self.dialogues and self.current_stage != 'dialing':
            dialogue = self.dialogues[self.current_stage]

            if isinstance(dialogue, dict) and 'choices' in dialogue:
                # Calculate choice positions
                choice_y = self.phone_y + 350
                for i, (text, next_stage) in enumerate(dialogue['choices']):
                    choice_rect = pygame.Rect(
                        self.phone_x + 20,
                        choice_y + i * 35,
                        self.phone_width - 40,
                        30
                    )
                    if choice_rect.collidepoint(pos):
                        self.select_choice(i, next_stage)
                        break

    def handle_mouse_motion(self, pos):
        """Handle mouse hover for visual feedback"""
        if not self.active:
            return

        # Update hover state for choices
        if self.current_stage in self.dialogues and self.current_stage != 'dialing':
            dialogue = self.dialogues[self.current_stage]
            if isinstance(dialogue, dict) and 'choices' in dialogue:
                choice_y = self.phone_y + 350
                for i in range(len(dialogue['choices'])):
                    choice_rect = pygame.Rect(
                        self.phone_x + 20,
                        choice_y + i * 35,
                        self.phone_width - 40,
                        30
                    )
                    if choice_rect.collidepoint(pos):
                        self.choice_selected = i
                        return
        self.choice_selected = -1

    def select_choice(self, index, next_stage):
        """Process a dialogue choice"""
        self.dialogue_path.append((self.current_stage, index))

        # Update emotional state based on path
        if next_stage in ['desperate', 'plead', 'nobody']:
            self.emotional_state = 'desperate'
            self.shake_amount = 2
        elif next_stage in ['angry', 'guilt']:
            self.emotional_state = 'angry'
            self.shake_amount = 3
        elif next_stage in ['silence', 'dial_tone']:
            self.emotional_state = 'defeated'
            self.fade_alpha = 100

        # Move to next stage
        self.current_stage = next_stage
        self.dialogue_index = 0

        # Check for special transitions
        if next_stage in self.dialogues:
            dialogue = self.dialogues[next_stage]
            if isinstance(dialogue, dict) and 'next' in dialogue:
                # Automatically progress after showing this dialogue
                pygame.time.wait(1500)  # Brief pause to read
                self.current_stage = dialogue['next']

    def complete_call(self):
        """End the phone call and return results"""
        self.completed = True
        self.active = False

        # Record emotional impact
        results = {
            'emotional_state': self.emotional_state,
            'rejection_type': self.get_rejection_type(),
            'dialogue_path': self.dialogue_path
        }

        # Store results for narrative continuity
        if hasattr(self.objective_manager, 'phone_call_results'):
            self.objective_manager.phone_call_results = results

    def get_rejection_type(self):
        """Determine the type of rejection based on path"""
        path_stages = [stage for stage, _ in self.dialogue_path]

        if 'angry' in path_stages:
            return 'hostile'
        elif 'guilt' in path_stages:
            return 'cold'
        elif 'desperate' in path_stages or 'plead' in path_stages:
            return 'pitying'
        else:
            return 'polite'

    def update(self, dt):
        """Update the phone call state"""
        if not self.active:
            return

        # Update visual effects
        if self.shake_amount > 0:
            self.shake_amount *= 0.95

        if self.fade_alpha > 0:
            self.fade_alpha = min(255, self.fade_alpha + dt * 50)

        # Update ring animation
        if self.current_stage == 'dialing':
            self.ring_timer += dt

        # Auto-advance certain dialogue
        if self.current_stage in self.dialogues:
            dialogue = self.dialogues[self.current_stage]
            if isinstance(dialogue, dict) and dialogue.get('final'):
                # Auto-complete after showing final message
                if self.dialogue_index > 60:  # About 2 seconds
                    self.complete_call()
                else:
                    self.dialogue_index += 1

    def draw(self, screen):
        """Draw the phone call interface"""
        if not self.active:
            return

        # Draw darkened background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Calculate phone shake
        shake_x = 0
        shake_y = 0
        if self.shake_amount > 0.5:
            shake_x = math.sin(pygame.time.get_ticks() * 0.05) * self.shake_amount
            shake_y = math.cos(pygame.time.get_ticks() * 0.07) * self.shake_amount

        # Draw phone frame
        phone_rect = pygame.Rect(
            self.phone_x + shake_x,
            self.phone_y + shake_y,
            self.phone_width,
            self.phone_height
        )
        pygame.draw.rect(screen, self.phone_bg, phone_rect, border_radius=25)
        pygame.draw.rect(screen, (100, 100, 110), phone_rect, 3, border_radius=25)

        # Draw phone screen
        screen_rect = pygame.Rect(
            phone_rect.x + 15,
            phone_rect.y + 60,
            self.phone_width - 30,
            self.phone_height - 120
        )
        pygame.draw.rect(screen, self.screen_color, screen_rect, border_radius=15)

        # Draw current content based on stage
        if self.current_stage == 'dialing':
            self.draw_dialing(screen, screen_rect)
        elif self.current_stage == 'dial_tone':
            self.draw_dial_tone(screen, screen_rect)
        else:
            self.draw_dialogue(screen, screen_rect)

        # Draw emotional overlay
        if self.fade_alpha > 0:
            fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_overlay.set_alpha(self.fade_alpha)
            fade_overlay.fill((0, 0, 30))
            screen.blit(fade_overlay, (0, 0))

    def draw_dialing(self, screen, screen_rect):
        """Draw the dialing animation"""
        # Draw "Calling..." text
        if self.dialogue_index < len(self.dialogues['dialing']):
            text = self.dialogues['dialing'][self.dialogue_index]
            text_surf = self.phone_font.render(text, True, self.text_color)
            text_rect = text_surf.get_rect(center=(screen_rect.centerx, screen_rect.centery))
            screen.blit(text_surf, text_rect)

            # Pulsing ring animation
            if "Ring" in text:
                pulse = abs(math.sin(self.ring_timer * 3))
                ring_color = (
                    int(100 + pulse * 155),
                    int(100 + pulse * 155),
                    int(100 + pulse * 155)
                )
                pygame.draw.circle(
                    screen,
                    ring_color,
                    (screen_rect.centerx, screen_rect.centery - 50),
                    30 + pulse * 10,
                    3
                )

        # Draw "Press E to continue" prompt
        prompt_text = "Press E to continue"
        prompt_surf = self.choice_font.render(prompt_text, True, (150, 150, 150))
        prompt_rect = prompt_surf.get_rect(center=(screen_rect.centerx, screen_rect.bottom - 30))
        screen.blit(prompt_surf, prompt_rect)

    def draw_dial_tone(self, screen, screen_rect):
        """Draw the dial tone ending"""
        # Draw "Call Ended" text
        ended_text = "Call Ended"
        ended_surf = self.speaker_font.render(ended_text, True, (255, 100, 100))
        ended_rect = ended_surf.get_rect(center=(screen_rect.centerx, screen_rect.centery - 50))
        screen.blit(ended_surf, ended_rect)

        # Draw dial tone message
        tone_text = "*dial tone*"
        tone_surf = self.dialogue_font.render(tone_text, True, (150, 150, 150))
        tone_rect = tone_surf.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        screen.blit(tone_surf, tone_rect)

        # Draw emotional message based on state
        if self.emotional_state == 'desperate':
            msg = "They won't help. You're truly alone."
        elif self.emotional_state == 'angry':
            msg = "Seven years meant nothing to them."
        elif self.emotional_state == 'defeated':
            msg = "Not their problem anymore."
        else:
            msg = "The line goes dead."

        msg_surf = self.choice_font.render(msg, True, (200, 200, 200))
        msg_rect = msg_surf.get_rect(center=(screen_rect.centerx, screen_rect.centery + 50))
        screen.blit(msg_surf, msg_rect)

        # Draw continue prompt
        prompt_text = "Press E to hang up"
        prompt_surf = self.choice_font.render(prompt_text, True, (150, 150, 150))
        prompt_rect = prompt_surf.get_rect(center=(screen_rect.centerx, screen_rect.bottom - 30))
        screen.blit(prompt_surf, prompt_rect)

    def draw_dialogue(self, screen, screen_rect):
        """Draw the current dialogue and choices"""
        if self.current_stage not in self.dialogues:
            return

        dialogue = self.dialogues[self.current_stage]

        # Draw speaker name
        if 'speaker' in dialogue:
            speaker = dialogue['speaker']
            if speaker:
                color = self.foster_mom_color if 'Mom' in speaker else \
                       self.foster_dad_color if 'Dad' in speaker else \
                       self.player_color if speaker == 'You' else self.text_color

                speaker_surf = self.speaker_font.render(speaker, True, color)
                screen.blit(speaker_surf, (screen_rect.x + 20, screen_rect.y + 20))

        # Draw main dialogue text (word wrapped)
        if 'text' in dialogue:
            self.draw_wrapped_text(
                screen,
                dialogue['text'],
                screen_rect.x + 20,
                screen_rect.y + 60,
                screen_rect.width - 40,
                self.dialogue_font,
                self.text_color
            )

        # Draw background voice if present
        if 'background' in dialogue:
            bg_surf = self.choice_font.render(dialogue['background'], True, (150, 150, 180))
            screen.blit(bg_surf, (screen_rect.x + 20, screen_rect.y + 160))

        # Draw choices if present
        if 'choices' in dialogue:
            choice_y = screen_rect.y + 220
            for i, (text, _) in enumerate(dialogue['choices']):
                # Highlight selected choice
                if i == self.choice_selected:
                    choice_bg = pygame.Rect(
                        screen_rect.x + 15,
                        choice_y + i * 35,
                        screen_rect.width - 30,
                        30
                    )
                    pygame.draw.rect(screen, (60, 60, 70), choice_bg, border_radius=5)

                # Draw choice text
                choice_text = f"{i+1}. {text}"
                choice_surf = self.choice_font.render(choice_text, True, self.text_color)
                screen.blit(choice_surf, (screen_rect.x + 20, choice_y + i * 35 + 5))

        # Draw emotional indicator
        if self.emotional_state != 'hopeful':
            emotion_text = f"[Feeling: {self.emotional_state}]"
            emotion_surf = self.choice_font.render(emotion_text, True, (180, 180, 180))
            screen.blit(emotion_surf, (screen_rect.x + 20, screen_rect.bottom - 50))

    def draw_wrapped_text(self, screen, text, x, y, max_width, font, color):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines):
            line_surf = font.render(line, True, color)
            screen.blit(line_surf, (x, y + i * 25))
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

        # Enhanced animation effects
        self.phone_slide_offset = 0  # For entry/exit animations
        self.transition_alpha = 0    # For smooth fade transitions
        self.is_exiting = False      # Exit animation state
        self.exit_animation_timer = 0
        self.ring_speed = 2.0        # Faster ring speed

        # Auto-transition system to prevent getting stuck
        self.auto_transition_timer = 0
        self.auto_transition_target = None

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

        # Start with phone sliding up from bottom
        self.phone_slide_offset = 600  # Start below screen
        self.transition_alpha = 0
        self.is_exiting = False

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.active:
            return

        if self.current_stage == 'dialing':
            if key == pygame.K_SPACE or key == pygame.K_e:
                # Skip dialing animation and go straight to opening
                self.current_stage = 'opening'
                self.dialogue_index = 0

        elif self.current_stage == 'dial_tone':
            if key == pygame.K_SPACE or key == pygame.K_e:
                self.start_exit_animation()

        # UNIVERSAL ESCAPE - always allow ESC to exit
        if key == pygame.K_ESCAPE:
            self.start_exit_animation()

    def handle_mouse_click(self, pos, button):
        """Handle mouse clicks for choices"""
        if not self.active or button != 1:
            return

        # Check if clicking on a choice
        if self.current_stage in self.dialogues and self.current_stage != 'dialing':
            dialogue = self.dialogues[self.current_stage]

            if isinstance(dialogue, dict) and 'choices' in dialogue:
                # Calculate choice positions - MATCH the drawing coordinates
                screen_rect_y = self.phone_y + 60  # Phone screen starts 60px down
                choice_y = screen_rect_y + 220     # Same as drawing code
                for i, (text, next_stage) in enumerate(dialogue['choices']):
                    choice_rect = pygame.Rect(
                        self.phone_x + 35,  # Screen x + 15 + 20 padding
                        choice_y + i * 35,
                        self.phone_width - 70,  # Screen width - 30 - 40 padding
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
                # Calculate choice positions - MATCH the drawing coordinates
                screen_rect_y = self.phone_y + 60  # Phone screen starts 60px down
                choice_y = screen_rect_y + 220     # Same as drawing code
                for i in range(len(dialogue['choices'])):
                    choice_rect = pygame.Rect(
                        self.phone_x + 35,  # Screen x + 15 + 20 padding
                        choice_y + i * 35,
                        self.phone_width - 70,  # Screen width - 30 - 40 padding
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

        # Check for special transitions with smooth fade
        if next_stage in self.dialogues:
            dialogue = self.dialogues[next_stage]
            if isinstance(dialogue, dict) and 'next' in dialogue:
                # Set up automatic transition with timer
                self.auto_transition_timer = 2.0  # 2 seconds to read
                self.auto_transition_target = dialogue['next']

    def start_exit_animation(self):
        """Start the phone slide-down exit animation"""
        self.is_exiting = True
        self.exit_animation_timer = 0

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

        # Handle exit animation
        if self.is_exiting:
            self.exit_animation_timer += dt
            # Slide phone down smoothly
            target_offset = 700  # Slide below screen
            animation_speed = 800  # pixels per second
            self.phone_slide_offset = min(target_offset, self.exit_animation_timer * animation_speed)

            # Complete when fully off screen
            if self.phone_slide_offset >= target_offset:
                self.complete_call()
            return

        # Entry animation - slide phone up
        if self.phone_slide_offset > 0:
            self.phone_slide_offset = max(0, self.phone_slide_offset - dt * 1200)  # Fast slide up

        # Fade in transition
        if self.transition_alpha > 0:
            self.transition_alpha = max(0, self.transition_alpha - dt * 300)

        # Update visual effects
        if self.shake_amount > 0:
            self.shake_amount *= 0.95

        if self.fade_alpha > 0:
            self.fade_alpha = min(255, self.fade_alpha + dt * 50)

        # Update ring animation and auto-advance after 1.5 seconds
        if self.current_stage == 'dialing':
            self.ring_timer += dt * self.ring_speed  # Apply faster ring speed

            # Auto-advance after 1.5 seconds total
            if self.ring_timer >= 1.5:
                self.current_stage = 'opening'
                self.dialogue_index = 0

        # Handle auto-transition timer to prevent getting stuck
        if self.auto_transition_timer > 0:
            self.auto_transition_timer -= dt
            if self.auto_transition_timer <= 0 and self.auto_transition_target:
                self.current_stage = self.auto_transition_target
                self.auto_transition_target = None
                self.dialogue_index = 0

        # Auto-advance certain dialogue
        if self.current_stage in self.dialogues:
            dialogue = self.dialogues[self.current_stage]
            if isinstance(dialogue, dict) and dialogue.get('final'):
                # Auto-complete after showing final message
                if self.dialogue_index > 60:  # About 2 seconds
                    self.current_stage = 'dial_tone'  # Move to dial tone instead of completing
                else:
                    self.dialogue_index += 1

    def draw(self, screen):
        """Draw the phone call interface"""
        if not self.active:
            return

        # Draw darkened background with fade-in effect
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_alpha = 180
        if self.phone_slide_offset > 0:
            # Fade in background as phone slides up
            bg_alpha = int(180 * (1 - self.phone_slide_offset / 600))
        overlay.set_alpha(bg_alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Calculate phone shake
        shake_x = 0
        shake_y = 0
        if self.shake_amount > 0.5:
            shake_x = math.sin(pygame.time.get_ticks() * 0.05) * self.shake_amount
            shake_y = math.cos(pygame.time.get_ticks() * 0.07) * self.shake_amount

        # Apply slide offset for entry/exit animations
        current_phone_y = self.phone_y + self.phone_slide_offset

        # Draw phone frame with animation
        phone_rect = pygame.Rect(
            self.phone_x + shake_x,
            current_phone_y + shake_y,
            self.phone_width,
            self.phone_height
        )

        # Add subtle glow effect during entry
        if self.phone_slide_offset > 0:
            glow_rect = pygame.Rect(
                phone_rect.x - 5,
                phone_rect.y - 5,
                phone_rect.width + 10,
                phone_rect.height + 10
            )
            glow_alpha = int(50 * (self.phone_slide_offset / 600))
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 255, glow_alpha),
                           (0, 0, glow_rect.width, glow_rect.height), border_radius=30)
            screen.blit(glow_surface, glow_rect.topleft)

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

        # Draw transition overlay for smooth stage changes
        if self.transition_alpha > 0:
            transition_overlay = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
            transition_overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(transition_overlay, screen_rect.topleft)

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

            # Subtle pulsing ring animation
            if "Ring" in text:
                pulse = abs(math.sin(self.ring_timer * 3))  # Moderate pulse
                ring_color = (
                    int(150 + pulse * 50),  # More subtle color change
                    int(150 + pulse * 50),
                    int(150 + pulse * 50)
                )
                # Draw 2 subtle rings
                for i in range(2):
                    offset_pulse = abs(math.sin(self.ring_timer * 3 + i * 0.8))
                    ring_radius = 30 + offset_pulse * 5 + i * 3  # Much smaller expansion
                    ring_alpha = int(120 - i * 40 - offset_pulse * 30)  # More subtle alpha
                    ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surface, (*ring_color, max(30, ring_alpha)),
                                     (ring_radius, ring_radius), ring_radius, 1)  # Thinner lines
                    screen.blit(ring_surface,
                              (screen_rect.centerx - ring_radius, screen_rect.centery - 50 - ring_radius))

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

        # Draw continue prompt with multiple options
        prompt_text = "Press E to hang up or ESC to exit"
        prompt_surf = self.choice_font.render(prompt_text, True, (150, 150, 150))
        prompt_rect = prompt_surf.get_rect(center=(screen_rect.centerx, screen_rect.bottom - 40))
        screen.blit(prompt_surf, prompt_rect)

        # Add a subtle pulsing effect to the prompt
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        pulse_color = (150 + int(pulse * 50), 150 + int(pulse * 50), 150 + int(pulse * 50))
        pulse_surf = self.choice_font.render("►", True, pulse_color)
        pulse_rect = pulse_surf.get_rect(center=(screen_rect.centerx - 120, screen_rect.bottom - 40))
        screen.blit(pulse_surf, pulse_rect)

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
                # Enhanced highlight for selected choice
                if i == self.choice_selected:
                    choice_bg = pygame.Rect(
                        screen_rect.x + 15,
                        choice_y + i * 35,
                        screen_rect.width - 30,
                        30
                    )
                    # Animated highlight
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
                    highlight_color = (60 + int(pulse * 30), 60 + int(pulse * 30), 70 + int(pulse * 20))
                    pygame.draw.rect(screen, highlight_color, choice_bg, border_radius=5)

                    # Add a subtle glow
                    glow_rect = pygame.Rect(choice_bg.x - 2, choice_bg.y - 2, choice_bg.width + 4, choice_bg.height + 4)
                    glow_alpha = int(50 + pulse * 30)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (100, 150, 200, glow_alpha),
                                   (0, 0, glow_rect.width, glow_rect.height), border_radius=7)
                    screen.blit(glow_surface, glow_rect.topleft)

                # Draw choice text with color based on selection
                choice_text = f"{i+1}. {text}"
                text_color = (255, 255, 200) if i == self.choice_selected else self.text_color
                choice_surf = self.choice_font.render(choice_text, True, text_color)
                screen.blit(choice_surf, (screen_rect.x + 20, choice_y + i * 35 + 5))

        # Draw emotional indicator
        if self.emotional_state != 'hopeful':
            emotion_text = f"[Feeling: {self.emotional_state}]"
            emotion_surf = self.choice_font.render(emotion_text, True, (180, 180, 180))
            screen.blit(emotion_surf, (screen_rect.x + 20, screen_rect.bottom - 70))

        # Always show escape option
        escape_text = "Press ESC to exit"
        escape_surf = self.choice_font.render(escape_text, True, (120, 120, 120))
        escape_rect = escape_surf.get_rect(center=(screen_rect.centerx, screen_rect.bottom - 20))
        screen.blit(escape_surf, escape_rect)

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
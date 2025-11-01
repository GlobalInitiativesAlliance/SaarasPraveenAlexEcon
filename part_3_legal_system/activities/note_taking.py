"""
Note-Taking Mini-Game for Legal System Part
Take notes while being distracted by text messages
"""
import pygame
import random
import time

class NoteTakingGame:
    """Take class notes while receiving distracting texts from boss"""

    def __init__(self, objective_manager=None):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Notebook area
        self.notebook_rect = pygame.Rect(340, 150, 600, 400)

        # Phone area
        self.phone_rect = pygame.Rect(950, 200, 280, 500)

        # Text messages from boss
        self.boss_messages = [
            "Hey, need you tomorrow 7am SHARP",
            "Can't find anyone to cover",
            "You there???",
            "This is MANDATORY",
            "I'm scheduling you for doubles",
            "Reply ASAP!!!",
            "Missing this = write up",
            "Last warning about attendance"
        ]

        # Class notes to type
        self.class_notes = [
            "Chapter 7: Constitutional Rights",
            "Due process - fair treatment",
            "Right to legal representation",
            "Court procedures and filing",
            "Important: Always appear on scheduled dates"
        ]

        # Game state
        self.current_note_index = 0
        self.typed_text = ""
        self.current_target = self.class_notes[0]
        self.messages_received = []
        self.last_message_time = 0
        self.message_interval = 3000  # 3 seconds between texts
        self.start_time = 0
        self.typing_enabled = True
        self.distraction_level = 0
        self.focus_timer = 0

        # Performance tracking
        self.notes_completed = 0
        self.errors = 0
        self.phone_vibrating = False
        self.vibrate_timer = 0

    def start(self):
        """Start the activity"""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.last_message_time = self.start_time

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        current_time = pygame.time.get_ticks()

        # Send boss messages periodically
        if current_time - self.last_message_time > self.message_interval:
            self.send_boss_message()
            self.last_message_time = current_time

        # Update phone vibration
        if self.phone_vibrating:
            if current_time - self.vibrate_timer > 500:
                self.phone_vibrating = False

        # Check if all notes completed
        if self.notes_completed >= len(self.class_notes):
            self.completed = True
            self.active = False

        # Reduce focus over time when messages arrive
        if self.distraction_level > 0:
            self.distraction_level -= dt * 0.5

    def send_boss_message(self):
        """Add a new message from boss"""
        if self.messages_received and len(self.messages_received) >= len(self.boss_messages):
            return

        message_index = len(self.messages_received) % len(self.boss_messages)
        message = self.boss_messages[message_index]

        self.messages_received.append({
            'text': message,
            'time': pygame.time.get_ticks(),
            'read': False
        })

        self.phone_vibrating = True
        self.vibrate_timer = pygame.time.get_ticks()
        self.distraction_level = min(self.distraction_level + 2, 10)

    def handle_key(self, key):
        """Handle keyboard input"""
        if not self.typing_enabled:
            return

        # Check for backspace
        if key == pygame.K_BACKSPACE:
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
        elif key == pygame.K_RETURN:
            # Check if current note is complete
            if self.typed_text.strip() == self.current_target:
                self.notes_completed += 1
                self.typed_text = ""

                if self.notes_completed < len(self.class_notes):
                    self.current_note_index = self.notes_completed
                    self.current_target = self.class_notes[self.current_note_index]
        else:
            # Add character if it's printable
            if len(self.typed_text) < len(self.current_target):
                char = pygame.key.name(key)
                if len(char) == 1:
                    # Handle shift for uppercase
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        char = char.upper()
                    self.typed_text += char
                elif key == pygame.K_SPACE:
                    self.typed_text += " "
                elif key == pygame.K_COLON:
                    self.typed_text += ":"
                elif key == pygame.K_MINUS:
                    self.typed_text += "-"

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)

    def draw(self, screen):
        """Draw the activity"""
        # Classroom background
        screen.fill((245, 235, 220))

        # Draw chalkboard
        board_rect = pygame.Rect(50, 20, 1180, 100)
        pygame.draw.rect(screen, (30, 60, 30), board_rect)
        pygame.draw.rect(screen, (150, 120, 90), board_rect, 5)

        # Chalkboard text
        chalk_font = pygame.font.Font(None, 36)
        chalk_text = chalk_font.render("Legal Studies 101 - Know Your Rights", True, (255, 255, 255))
        chalk_rect = chalk_text.get_rect(center=board_rect.center)
        screen.blit(chalk_text, chalk_rect)

        # Draw notebook
        pygame.draw.rect(screen, (255, 255, 240), self.notebook_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.notebook_rect, 2)

        # Notebook lines
        for i in range(10):
            y = self.notebook_rect.y + 40 + (i * 35)
            pygame.draw.line(screen, (200, 200, 255),
                           (self.notebook_rect.x + 20, y),
                           (self.notebook_rect.right - 20, y), 1)

        # Draw target text (what to type)
        note_font = pygame.font.Font(None, 28)
        target_surface = note_font.render(self.current_target, True, (150, 150, 150))
        target_rect = target_surface.get_rect(
            x=self.notebook_rect.x + 30,
            y=self.notebook_rect.y + 20
        )
        screen.blit(target_surface, target_rect)

        # Draw typed text
        if self.typed_text:
            typed_color = (0, 100, 0) if self.typed_text == self.current_target[:len(self.typed_text)] else (200, 0, 0)
            typed_surface = note_font.render(self.typed_text, True, typed_color)
            typed_rect = typed_surface.get_rect(
                x=self.notebook_rect.x + 30,
                y=self.notebook_rect.y + 60
            )
            screen.blit(typed_surface, typed_rect)

            # Draw cursor
            cursor_x = typed_rect.right + 2
            cursor_y = typed_rect.y
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + 25), 2)

        # Draw phone
        phone_color = (20, 20, 20)
        if self.phone_vibrating:
            # Shake effect
            offset = random.randint(-2, 2)
            vibrate_rect = self.phone_rect.copy()
            vibrate_rect.x += offset
            pygame.draw.rect(screen, phone_color, vibrate_rect)
        else:
            pygame.draw.rect(screen, phone_color, self.phone_rect)

        # Phone screen
        phone_screen = pygame.Rect(
            self.phone_rect.x + 10,
            self.phone_rect.y + 40,
            self.phone_rect.width - 20,
            self.phone_rect.height - 80
        )
        pygame.draw.rect(screen, (240, 240, 255), phone_screen)

        # Draw messages
        message_font = pygame.font.Font(None, 20)
        y_offset = 10
        for i, msg in enumerate(self.messages_received[-6:]):  # Show last 6 messages
            # Message bubble
            bubble_rect = pygame.Rect(
                phone_screen.x + 10,
                phone_screen.y + y_offset,
                phone_screen.width - 20,
                50
            )
            pygame.draw.rect(screen, (100, 200, 100), bubble_rect, border_radius=10)

            # Message text
            lines = self.wrap_text(msg['text'], message_font, bubble_rect.width - 10)
            for j, line in enumerate(lines):
                text_surface = message_font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    x=bubble_rect.x + 5,
                    y=bubble_rect.y + 5 + (j * 20)
                )
                screen.blit(text_surface, text_rect)

            y_offset += 60

        # Draw progress
        progress_font = pygame.font.Font(None, 32)
        progress_text = progress_font.render(
            f"Notes: {self.notes_completed}/{len(self.class_notes)}",
            True, (0, 0, 0)
        )
        progress_rect = progress_text.get_rect(topleft=(20, 140))
        screen.blit(progress_text, progress_rect)

        # Draw distraction indicator
        if self.distraction_level > 0:
            distraction_text = progress_font.render(
                "DISTRACTED!",
                True, (255, 0, 0)
            )
            distraction_rect = distraction_text.get_rect(center=(640, 600))
            if pygame.time.get_ticks() % 500 < 250:  # Flashing effect
                screen.blit(distraction_text, distraction_rect)

        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst_text = inst_font.render("Type the gray text exactly, press ENTER to submit each note", True, (100, 100, 100))
        inst_rect = inst_text.get_rect(bottomleft=(20, self.SCREEN_HEIGHT - 20))
        screen.blit(inst_text, inst_rect)

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
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
                else:
                    lines.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def get_results(self):
        """Return results of the activity"""
        return {
            'notes_completed': self.notes_completed,
            'messages_received': len(self.messages_received),
            'stress': self.distraction_level * 5  # Convert to stress points
        }
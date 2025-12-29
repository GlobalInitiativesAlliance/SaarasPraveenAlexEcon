"""
Police Encounter Activity - Fullscreen Overlay for Part 3
Handles scenes 7-9: police_stop, stay_calm (breathing game), court_citation
"""
import pygame
import random


class PoliceEncounterActivity:
    """Fullscreen police encounter with breathing game integration"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Phase management: 'police_stop', 'stay_calm', 'court_citation', 'complete'
        self.phase = 'police_stop'

        # Dialogue system
        self.dialogue_sequences = self.load_dialogue_sequences()
        self.current_dialogue = []
        self.dialogue_index = 0
        self.dialogue_complete = False
        self.waiting_for_input = True

        # Breathing game sub-activity
        self.breathing_game = None

        # Visual effects
        self.police_lights_timer = 0
        self.lights_red = True
        self.screen_shake = 0
        self.anxiety_level = 100  # Starts high

        # Citation display
        self.show_citation = False
        self.citation_timer = 0

    def load_dialogue_sequences(self):
        """Load all dialogue for the three scenes"""
        return {
            'police_stop': [
                (None, "Walking home from work. Tired. Worried."),
                (None, "The evening air is cold. Your thoughts are heavy."),
                (None, "Red and blue lights flash behind you."),
                (None, "Your heart stops."),
                ("Officer", "Excuse me. Can I see some ID?"),
                ("You", "(heart racing) Uh, sure... what's this about?"),
                ("Officer", "Routine check. Just need to run your name."),
                (None, "Your heart pounds. The warrant."),
                (None, "You hand over your ID with shaking hands."),
                ("Officer", "(into radio) Running a check on..."),
                (None, "Seconds feel like hours."),
                (None, "The officer's expression changes."),
                ("Officer", "There's a warrant for your arrest."),
                ("You", "I can explain—"),
                ("Officer", "Save it. You missed your court date."),
                ("You", "I had to work! I would have lost my job!"),
                ("Officer", "That's not how the law works."),
                (None, "Everything is spinning. You can't breathe."),
            ],

            'stay_calm_intro': [
                (None, "Your hands are shaking. Your vision narrows."),
                ("Officer", "I need you to stay calm."),
                ("You", "(trying to breathe) I just... I had work..."),
                ("Officer", "Take a breath. I'm not going to arrest you right now."),
                (None, "Focus. Breathe. Don't make this worse."),
                (None, "Press SPACE when ready to begin breathing exercise..."),
            ],

            'stay_calm_outro': [
                (None, "Your breathing steadies. The panic recedes slightly."),
                ("Officer", "Better. Now listen carefully."),
            ],

            'court_citation': [
                ("Officer", "Look, I could take you in right now."),
                ("You", "Please... I have school. I have work..."),
                ("Officer", "I'm going to give you a break."),
                (None, "He pulls out a citation pad."),
                ("Officer", "You have 48 hours to appear at the courthouse."),
                ("Officer", "48 hours. Not 49. Not 'when you get around to it.'"),
                ("You", "You're not arresting me?"),
                ("Officer", "Against my better judgment, no."),
                ("Officer", "But if you miss this deadline..."),
                ("Officer", "I will personally come find you."),
                (None, "He hands you the citation. Your hands still shake."),
                ("Officer", "Don't make me regret this."),
                ("You", "I won't. Thank you. I'm sorry."),
                (None, "You watch him return to his car."),
                (None, "The red and blue lights fade into the distance."),
                (None, "48 hours."),
                (None, "Another impossible deadline in an impossible life."),
            ]
        }

    def start(self):
        """Start the activity"""
        self.active = True
        self.phase = 'police_stop'
        self.current_dialogue = self.dialogue_sequences['police_stop']
        self.dialogue_index = 0
        self.dialogue_complete = False

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        # Update police lights animation
        self.police_lights_timer += dt
        if self.police_lights_timer > 0.5:
            self.police_lights_timer = 0
            self.lights_red = not self.lights_red

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 5)

        # Update breathing game if active
        if self.phase == 'stay_calm' and self.breathing_game:
            self.breathing_game.update(dt)
            if self.breathing_game.completed:
                # Breathing game done, show outro and move to citation
                self.breathing_game = None
                self.current_dialogue = self.dialogue_sequences['stay_calm_outro']
                self.dialogue_index = 0
                self.dialogue_complete = False
                self.phase = 'stay_calm_outro'

        # Update citation display timer
        if self.show_citation:
            self.citation_timer += dt

    def handle_key(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            # Allow escape to exit (will complete all scenes)
            self.completed = True
            self.active = False
            return

        # Handle breathing game input
        if self.phase == 'stay_calm' and self.breathing_game:
            self.breathing_game.handle_key(key)
            return

        # Advance dialogue on space/enter
        if key in [pygame.K_SPACE, pygame.K_RETURN]:
            self.advance_dialogue()

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.handle_key(event.key)
        elif event.type == pygame.KEYUP:
            if self.phase == 'stay_calm' and self.breathing_game:
                if event.key == pygame.K_SPACE:
                    pass  # Breathing game might use key release

    def advance_dialogue(self):
        """Advance to next dialogue line"""
        if self.dialogue_index < len(self.current_dialogue) - 1:
            self.dialogue_index += 1

            # Add screen shake for dramatic moments
            current_line = self.current_dialogue[self.dialogue_index]
            if current_line[1] and ('warrant' in current_line[1].lower() or
                                    'arrest' in current_line[1].lower()):
                self.screen_shake = 5
        else:
            # Dialogue sequence complete
            self.handle_phase_complete()

    def handle_phase_complete(self):
        """Handle completion of current phase"""
        if self.phase == 'police_stop':
            # Move to breathing exercise intro
            self.phase = 'stay_calm_intro'
            self.current_dialogue = self.dialogue_sequences['stay_calm_intro']
            self.dialogue_index = 0

            # Complete the police_stop objective
            if self.objective_manager:
                current = self.objective_manager.get_current_objective()
                if current and current.id == 'police_stop':
                    self.objective_manager.complete_current_objective()

        elif self.phase == 'stay_calm_intro':
            # Start the breathing game
            self.phase = 'stay_calm'
            from part_3_legal_system.activities.breathing_game import BreathingGame
            self.breathing_game = BreathingGame(self.objective_manager)
            self.breathing_game.start()

            # Complete the stay_calm objective
            if self.objective_manager:
                current = self.objective_manager.get_current_objective()
                if current and current.id == 'stay_calm':
                    self.objective_manager.complete_current_objective()

        elif self.phase == 'stay_calm_outro':
            # Move to court citation
            self.phase = 'court_citation'
            self.current_dialogue = self.dialogue_sequences['court_citation']
            self.dialogue_index = 0

        elif self.phase == 'court_citation':
            # Show citation visual, then complete
            self.show_citation = True
            self.phase = 'complete'

            # Complete the court_citation objective
            if self.objective_manager:
                current = self.objective_manager.get_current_objective()
                if current and current.id == 'court_citation':
                    self.objective_manager.complete_current_objective()

        elif self.phase == 'complete':
            # End the entire activity
            self.completed = True
            self.active = False

    def draw(self, screen):
        """Draw the activity"""
        # Apply screen shake
        shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0
        shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0

        # Dark street background
        screen.fill((15, 15, 25))

        # Draw street
        pygame.draw.rect(screen, (30, 30, 35),
                        (0, self.SCREEN_HEIGHT // 2, self.SCREEN_WIDTH, self.SCREEN_HEIGHT // 2))

        # Street lines
        for x in range(0, self.SCREEN_WIDTH, 100):
            pygame.draw.rect(screen, (80, 80, 60),
                           (x + shake_x, self.SCREEN_HEIGHT // 2 + 50 + shake_y, 50, 8))

        # Draw streetlights
        for x in [200, 1080]:
            # Light glow
            glow_color = (60, 60, 40)
            pygame.draw.circle(screen, glow_color, (x + shake_x, 100 + shake_y), 100)
            # Light pole
            pygame.draw.rect(screen, (40, 40, 40),
                           (x - 5 + shake_x, 100 + shake_y, 10, 300))

        # Police car lights effect
        if self.phase != 'complete':
            light_intensity = 150
            if self.lights_red:
                # Red light
                pygame.draw.circle(screen, (light_intensity, 0, 0),
                                 (self.SCREEN_WIDTH - 150 + shake_x, 200 + shake_y), 80)
            else:
                # Blue light
                pygame.draw.circle(screen, (0, 0, light_intensity),
                                 (self.SCREEN_WIDTH - 150 + shake_x, 200 + shake_y), 80)

        # Draw breathing game if active
        if self.phase == 'stay_calm' and self.breathing_game:
            self.breathing_game.draw(screen)
            return

        # Draw citation if showing
        if self.show_citation:
            self.draw_citation(screen, shake_x, shake_y)
            return

        # Draw dialogue box
        self.draw_dialogue(screen, shake_x, shake_y)

        # Draw continue prompt
        if self.dialogue_index < len(self.current_dialogue) - 1 or self.phase != 'complete':
            prompt_font = pygame.font.Font(None, 24)
            prompt_text = prompt_font.render("Press SPACE to continue", True, (150, 150, 150))
            prompt_rect = prompt_text.get_rect(bottomright=(self.SCREEN_WIDTH - 30, self.SCREEN_HEIGHT - 30))
            screen.blit(prompt_text, prompt_rect)

    def draw_dialogue(self, screen, shake_x, shake_y):
        """Draw the current dialogue"""
        if not self.current_dialogue or self.dialogue_index >= len(self.current_dialogue):
            return

        speaker, text = self.current_dialogue[self.dialogue_index]

        # Dialogue box
        box_height = 150
        box_rect = pygame.Rect(50 + shake_x, self.SCREEN_HEIGHT - box_height - 50 + shake_y,
                              self.SCREEN_WIDTH - 100, box_height)

        # Box background
        pygame.draw.rect(screen, (0, 0, 0), box_rect)
        pygame.draw.rect(screen, (100, 100, 120), box_rect, 3)

        # Speaker name
        if speaker:
            name_font = pygame.font.Font(None, 32)
            # Color code speakers
            if speaker == "Officer":
                name_color = (100, 100, 200)
            elif speaker == "You":
                name_color = (200, 200, 100)
            else:
                name_color = (200, 200, 200)

            name_text = name_font.render(speaker, True, name_color)
            name_rect = name_text.get_rect(topleft=(box_rect.x + 20, box_rect.y + 15))
            screen.blit(name_text, name_rect)

        # Dialogue text
        text_font = pygame.font.Font(None, 28)
        text_y = box_rect.y + 50 if speaker else box_rect.y + 20

        # Word wrap
        words = text.split(' ')
        lines = []
        current_line = []
        max_width = box_rect.width - 40

        for word in words:
            test_line = ' '.join(current_line + [word])
            if text_font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Render lines
        for i, line in enumerate(lines):
            # Italicize narrator text
            if speaker is None:
                text_color = (180, 180, 200)
            else:
                text_color = (255, 255, 255)

            line_surface = text_font.render(line, True, text_color)
            screen.blit(line_surface, (box_rect.x + 20, text_y + i * 30))

    def draw_citation(self, screen, shake_x, shake_y):
        """Draw the citation document"""
        # Citation paper
        paper_width = 500
        paper_height = 350
        paper_x = (self.SCREEN_WIDTH - paper_width) // 2 + shake_x
        paper_y = (self.SCREEN_HEIGHT - paper_height) // 2 + shake_y

        # Paper background
        pygame.draw.rect(screen, (250, 245, 230), (paper_x, paper_y, paper_width, paper_height))
        pygame.draw.rect(screen, (100, 100, 100), (paper_x, paper_y, paper_width, paper_height), 2)

        # Header
        header_font = pygame.font.Font(None, 36)
        header_text = header_font.render("COUNTY COURT CITATION", True, (0, 0, 0))
        header_rect = header_text.get_rect(centerx=paper_x + paper_width // 2, top=paper_y + 20)
        screen.blit(header_text, header_rect)

        # Line
        pygame.draw.line(screen, (0, 0, 0),
                        (paper_x + 30, paper_y + 60),
                        (paper_x + paper_width - 30, paper_y + 60), 2)

        # Citation text
        body_font = pygame.font.Font(None, 24)
        citation_lines = [
            "FAILURE TO APPEAR - TRAFFIC VIOLATION",
            "",
            "You are hereby ordered to appear at:",
            "County Courthouse, Room 204",
            "",
            "WITHIN 48 HOURS",
            "",
            "Failure to appear will result in:",
            "IMMEDIATE ARREST",
            "",
            "This is your FINAL WARNING.",
        ]

        y_offset = paper_y + 80
        for line in citation_lines:
            if line == "WITHIN 48 HOURS" or line == "IMMEDIATE ARREST":
                text_surface = body_font.render(line, True, (200, 0, 0))
            else:
                text_surface = body_font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(centerx=paper_x + paper_width // 2, top=y_offset)
            screen.blit(text_surface, text_rect)
            y_offset += 25

        # Continue prompt
        prompt_font = pygame.font.Font(None, 28)
        prompt_text = prompt_font.render("Press SPACE to continue", True, (100, 100, 100))
        prompt_rect = prompt_text.get_rect(centerx=self.SCREEN_WIDTH // 2,
                                          bottom=self.SCREEN_HEIGHT - 50)
        screen.blit(prompt_text, prompt_rect)

    def get_results(self):
        """Return results of the activity"""
        return {
            'stayed_calm': self.anxiety_level < 50 if self.breathing_game else True,
            'citation_received': True,
            'scenes_completed': 3
        }

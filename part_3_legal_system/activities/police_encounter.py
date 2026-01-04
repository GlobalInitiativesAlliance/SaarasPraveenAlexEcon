"""
Police Encounter Activity - Fullscreen Overlay for Part 3
Handles scenes 7-9: police_stop, stay_calm (breathing game), court_citation
Upgraded with Part 5-style visuals: particles, enhanced lighting, feedback system
"""
import pygame
import random
import math
import time

from .legal_visual_base import (
    LegalUIColors, LegalUIMetrics, LegalVisualHelpers,
    LegalVisualComponents, UIAnimation, legal_visuals
)
from .legal_particle_effects import LegalParticleSystem
from .legal_feedback_popups import LegalFeedbackManager


class PoliceEncounterActivity:
    """Fullscreen police encounter with breathing game integration

    Features:
    - Enhanced police lights with glow effect
    - Officer silhouette presence
    - Flashlight beam effect
    - Stress-based screen vignette
    - Improved dialogue box styling
    - Citation reveal with animation
    - Particle effects for dramatic moments
    """

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Screen settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Visual systems
        self.visuals = legal_visuals
        self.particles = LegalParticleSystem()
        self.feedback = LegalFeedbackManager()

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
        self.lights_phase = 0  # 0-1 smooth transition
        self.screen_shake = 0
        self.anxiety_level = 100  # Starts high
        self.vignette_intensity = UIAnimation(current=0.2, target=0.3, speed=0.1)

        # Animation timers
        self.pulse_time = 0
        self.flashlight_angle = 0
        self.officer_presence = UIAnimation(current=0, target=1.0, speed=0.05)

        # Citation display
        self.show_citation = False
        self.citation_timer = 0
        self.citation_slide = UIAnimation(current=0, target=0, speed=0.08)

        # Typewriter effect for dialogue
        self.displayed_chars = 0
        self.chars_per_second = 40
        self.last_char_time = 0

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
        self.displayed_chars = 0
        self.last_char_time = time.time()
        self.particles.clear()
        self.feedback.clear()

    def update(self, dt):
        """Update the activity"""
        if not self.active:
            return

        current_time = time.time()
        self.pulse_time += dt

        # Update visual systems
        self.particles.update(dt)
        self.feedback.update(dt)
        self.vignette_intensity.update(dt)
        self.officer_presence.update(dt)
        self.citation_slide.update(dt)

        # Update police lights animation (smoother)
        self.police_lights_timer += dt * 2
        self.lights_phase = (math.sin(self.police_lights_timer * 3) + 1) / 2

        # Update flashlight sway
        self.flashlight_angle = math.sin(self.pulse_time * 0.5) * 0.1

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 5)

        # Typewriter effect
        if self.current_dialogue and self.dialogue_index < len(self.current_dialogue):
            speaker, text = self.current_dialogue[self.dialogue_index]
            target_chars = len(text)
            if self.displayed_chars < target_chars:
                self.displayed_chars = min(target_chars,
                                          self.displayed_chars + self.chars_per_second * dt)

        # Update breathing game if active
        if self.phase == 'stay_calm' and self.breathing_game:
            self.breathing_game.update(dt)
            if self.breathing_game.completed:
                # Breathing game done, show outro and move to citation
                self.breathing_game = None
                self.current_dialogue = self.dialogue_sequences['stay_calm_outro']
                self.dialogue_index = 0
                self.displayed_chars = 0
                self.dialogue_complete = False
                self.phase = 'stay_calm_outro'

                # Success particles
                self.particles.emit_success(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
                self.feedback.add_breathing_achievement(70)  # Assume decent sync

        # Update citation display timer and animation
        if self.show_citation:
            self.citation_timer += dt
            self.citation_slide.target = 1.0

        # Adjust vignette based on phase
        if self.phase in ['police_stop', 'stay_calm_intro']:
            self.vignette_intensity.target = 0.35
        elif self.phase == 'court_citation':
            self.vignette_intensity.target = 0.2
        else:
            self.vignette_intensity.target = 0.1

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
            # If typewriter still going, complete it first
            if self.current_dialogue and self.dialogue_index < len(self.current_dialogue):
                speaker, text = self.current_dialogue[self.dialogue_index]
                if self.displayed_chars < len(text):
                    self.displayed_chars = len(text)
                    return

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
            self.displayed_chars = 0

            # Add screen shake and particles for dramatic moments
            current_line = self.current_dialogue[self.dialogue_index]
            if current_line[1]:
                text_lower = current_line[1].lower()
                if 'warrant' in text_lower or 'arrest' in text_lower:
                    self.screen_shake = 6
                    self.particles.emit_warning(self.SCREEN_WIDTH // 2, 400, count=15)
                    self.vignette_intensity.target = 0.5
                elif "can't breathe" in text_lower or 'spinning' in text_lower:
                    self.screen_shake = 4
                    self.particles.emit_error(self.SCREEN_WIDTH // 2, 400, count=10)
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
            self.displayed_chars = 0

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
            self.displayed_chars = 0

        elif self.phase == 'court_citation':
            # Show citation visual, then complete
            self.show_citation = True
            self.phase = 'complete'

            # Stamp effect and achievement
            self.particles.emit_stamp(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2,
                                     color=LegalUIColors.LEGAL_PRIMARY)
            self.feedback.add_achievement(
                title="Citation Received",
                description="48 hours to appear at courthouse",
                icon="📋",
                color=LegalUIColors.WARNING
            )

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
        """Draw the activity with enhanced visuals"""
        # Apply screen shake
        shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0
        shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake)) if self.screen_shake > 0 else 0

        # Dark night street background with gradient
        LegalVisualHelpers.draw_gradient_rect(
            screen,
            pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT // 2),
            (10, 10, 20),
            (20, 20, 35)
        )

        # Street surface
        street_rect = pygame.Rect(0, self.SCREEN_HEIGHT // 2, self.SCREEN_WIDTH, self.SCREEN_HEIGHT // 2)
        LegalVisualHelpers.draw_gradient_rect(
            screen, street_rect,
            (35, 35, 40),
            (25, 25, 30)
        )

        # Street lines with perspective
        for i, x in enumerate(range(-50, self.SCREEN_WIDTH + 100, 100)):
            y_base = self.SCREEN_HEIGHT // 2 + 60
            line_width = 50 - i % 10
            pygame.draw.rect(screen, (70, 70, 55),
                           (x + shake_x, y_base + shake_y, line_width, 6))

        # Draw streetlights with glow
        self._draw_streetlights(screen, shake_x, shake_y)

        # Police car lights effect (enhanced)
        if self.phase != 'complete':
            self._draw_police_lights(screen, shake_x, shake_y)

        # Draw officer silhouette
        if self.phase in ['police_stop', 'stay_calm_intro', 'stay_calm_outro', 'court_citation']:
            self._draw_officer_silhouette(screen, shake_x, shake_y)

        # Draw flashlight beam
        if self.phase in ['police_stop', 'stay_calm_intro']:
            self._draw_flashlight_beam(screen, shake_x, shake_y)

        # Draw breathing game if active
        if self.phase == 'stay_calm' and self.breathing_game:
            self.breathing_game.draw(screen)
            self.particles.render(screen)
            self.feedback.render(screen)
            return

        # Draw citation if showing
        if self.show_citation:
            self._draw_citation(screen, shake_x, shake_y)
        else:
            # Draw dialogue box
            self._draw_dialogue(screen, shake_x, shake_y)

        # Draw particles
        self.particles.render(screen)

        # Draw vignette for stress effect
        self._draw_stress_vignette(screen)

        # Draw feedback popups
        self.feedback.render(screen)

        # Draw continue prompt
        if not self.show_citation and (self.dialogue_index < len(self.current_dialogue) - 1 or self.phase != 'complete'):
            self._draw_continue_prompt(screen)

    def _draw_streetlights(self, screen, shake_x, shake_y):
        """Draw streetlights with realistic glow"""
        for x in [180, 1100]:
            # Light glow (layered for bloom effect)
            for radius, alpha in [(120, 20), (80, 40), (50, 60)]:
                glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (80, 75, 50, alpha), (radius, radius), radius)
                screen.blit(glow_surface, (x - radius + shake_x, 80 - radius + shake_y))

            # Light pole
            pygame.draw.rect(screen, (45, 45, 50),
                           (x - 4 + shake_x, 80 + shake_y, 8, 320))
            # Pole highlight
            pygame.draw.rect(screen, (55, 55, 60),
                           (x - 4 + shake_x, 80 + shake_y, 3, 320))

    def _draw_police_lights(self, screen, shake_x, shake_y):
        """Draw enhanced police lights with bloom"""
        car_x = self.SCREEN_WIDTH - 180
        car_y = 220

        # Calculate smooth color transition
        red_intensity = int(200 * (1 - self.lights_phase))
        blue_intensity = int(200 * self.lights_phase)

        # Multiple glow layers for bloom effect
        for radius, alpha_mult in [(100, 0.3), (70, 0.5), (40, 0.8)]:
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

            # Red glow
            red_alpha = int(alpha_mult * red_intensity * 0.5)
            pygame.draw.circle(glow_surface, (red_intensity, 0, 0, red_alpha),
                             (radius, radius), radius)
            screen.blit(glow_surface, (car_x - 30 - radius + shake_x, car_y - radius + shake_y))

            # Blue glow (offset)
            blue_alpha = int(alpha_mult * blue_intensity * 0.5)
            pygame.draw.circle(glow_surface, (0, 0, blue_intensity, blue_alpha),
                             (radius, radius), radius)
            screen.blit(glow_surface, (car_x + 30 - radius + shake_x, car_y - radius + shake_y))

        # Core lights
        pygame.draw.circle(screen, (red_intensity, 20, 20), (car_x - 30 + shake_x, car_y + shake_y), 20)
        pygame.draw.circle(screen, (20, 20, blue_intensity), (car_x + 30 + shake_x, car_y + shake_y), 20)

    def _draw_officer_silhouette(self, screen, shake_x, shake_y):
        """Draw officer silhouette"""
        presence = self.officer_presence.value
        if presence < 0.01:
            return

        # Officer position
        officer_x = self.SCREEN_WIDTH - 350 + shake_x
        officer_y = 200 + shake_y

        # Create silhouette surface
        silhouette = pygame.Surface((150, 300), pygame.SRCALPHA)

        # Body (simple silhouette shape)
        alpha = int(180 * presence)
        body_color = (20, 20, 30, alpha)

        # Torso
        pygame.draw.ellipse(silhouette, body_color, (30, 80, 90, 140))
        # Head
        pygame.draw.circle(silhouette, body_color, (75, 50), 35)
        # Hat
        pygame.draw.ellipse(silhouette, body_color, (45, 20, 60, 30))
        # Arms
        pygame.draw.ellipse(silhouette, body_color, (10, 100, 40, 80))
        pygame.draw.ellipse(silhouette, body_color, (100, 100, 40, 80))
        # Legs
        pygame.draw.rect(silhouette, body_color, (40, 200, 30, 100))
        pygame.draw.rect(silhouette, body_color, (80, 200, 30, 100))

        screen.blit(silhouette, (officer_x, officer_y))

    def _draw_flashlight_beam(self, screen, shake_x, shake_y):
        """Draw flashlight beam effect"""
        # Beam origin (officer's hand area)
        origin_x = self.SCREEN_WIDTH - 300 + shake_x
        origin_y = 350 + shake_y

        # Beam end (sweeping slightly)
        angle = -0.3 + self.flashlight_angle
        beam_length = 400
        end_x = origin_x + math.cos(angle) * beam_length
        end_y = origin_y + math.sin(angle) * beam_length

        # Draw beam as gradient polygon
        beam_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)

        # Beam cone
        spread = 60
        left_x = end_x - spread * math.sin(angle)
        left_y = end_y + spread * math.cos(angle)
        right_x = end_x + spread * math.sin(angle)
        right_y = end_y - spread * math.cos(angle)

        # Draw beam with gradient alpha
        for i in range(20, 0, -1):
            alpha = int(15 * (i / 20))
            scale = 1 + (20 - i) * 0.1
            points = [
                (origin_x, origin_y),
                (origin_x + (left_x - origin_x) * scale, origin_y + (left_y - origin_y) * scale),
                (origin_x + (right_x - origin_x) * scale, origin_y + (right_y - origin_y) * scale)
            ]
            pygame.draw.polygon(beam_surface, (255, 250, 200, alpha), points)

        screen.blit(beam_surface, (0, 0))

    def _draw_dialogue(self, screen, shake_x, shake_y):
        """Draw enhanced dialogue box"""
        if not self.current_dialogue or self.dialogue_index >= len(self.current_dialogue):
            return

        speaker, text = self.current_dialogue[self.dialogue_index]

        # Dialogue box dimensions
        box_height = 160
        box_margin = 60
        box_rect = pygame.Rect(
            box_margin + shake_x,
            self.SCREEN_HEIGHT - box_height - 50 + shake_y,
            self.SCREEN_WIDTH - box_margin * 2,
            box_height
        )

        # Box shadow
        LegalVisualHelpers.draw_shadow(screen, box_rect, offset=6, alpha=80, border_radius=12)

        # Box background with slight transparency
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (15, 15, 25, 230),
                        (0, 0, box_rect.width, box_rect.height),
                        border_radius=12)
        screen.blit(box_surface, box_rect.topleft)

        # Speaker-colored accent bar
        if speaker:
            if speaker == "Officer":
                accent_color = (80, 80, 180)
            elif speaker == "You":
                accent_color = (180, 180, 80)
            else:
                accent_color = (150, 150, 150)

            pygame.draw.rect(screen, accent_color,
                           (box_rect.x, box_rect.y, 5, box_rect.height),
                           border_top_left_radius=12,
                           border_bottom_left_radius=12)

        # Box border
        pygame.draw.rect(screen, (80, 80, 100), box_rect, 2, border_radius=12)

        # Speaker name
        if speaker:
            name_font = self.visuals.fonts['body']
            if speaker == "Officer":
                name_color = (120, 120, 220)
            elif speaker == "You":
                name_color = (220, 220, 120)
            else:
                name_color = (200, 200, 200)

            name_text = name_font.render(speaker, True, name_color)
            screen.blit(name_text, (box_rect.x + 25, box_rect.y + 15))

        # Dialogue text with typewriter effect
        text_font = self.visuals.fonts['body']
        text_y = box_rect.y + 50 if speaker else box_rect.y + 25
        displayed_text = text[:int(self.displayed_chars)]

        # Word wrap
        lines = self._wrap_text(displayed_text, text_font, box_rect.width - 50)

        # Render lines
        for i, line in enumerate(lines):
            if speaker is None:
                text_color = (180, 180, 210)  # Narrator - italicized feel
            else:
                text_color = (240, 240, 240)

            line_surface = text_font.render(line, True, text_color)
            screen.blit(line_surface, (box_rect.x + 25, text_y + i * 28))

    def _draw_citation(self, screen, shake_x, shake_y):
        """Draw the citation document with animation"""
        slide_progress = self._ease_out(self.citation_slide.value)

        # Citation paper
        paper_width = 520
        paper_height = 380
        target_x = (self.SCREEN_WIDTH - paper_width) // 2
        start_y = self.SCREEN_HEIGHT  # Start from bottom
        target_y = (self.SCREEN_HEIGHT - paper_height) // 2

        paper_x = target_x + shake_x
        paper_y = start_y + (target_y - start_y) * slide_progress + shake_y

        # Paper shadow
        shadow_rect = pygame.Rect(paper_x + 8, paper_y + 8, paper_width, paper_height)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=4)

        # Paper background
        pygame.draw.rect(screen, (250, 248, 240), (paper_x, paper_y, paper_width, paper_height),
                        border_radius=4)
        pygame.draw.rect(screen, (180, 175, 165), (paper_x, paper_y, paper_width, paper_height),
                        2, border_radius=4)

        # Red urgent stripe at top
        pygame.draw.rect(screen, LegalUIColors.URGENT,
                        (paper_x, paper_y, paper_width, 8),
                        border_top_left_radius=4, border_top_right_radius=4)

        # Header
        header_font = self.visuals.fonts['heading']
        header_text = header_font.render("COUNTY COURT CITATION", True, (30, 30, 30))
        header_rect = header_text.get_rect(centerx=paper_x + paper_width // 2, top=paper_y + 25)
        screen.blit(header_text, header_rect)

        # Decorative line
        pygame.draw.line(screen, (150, 145, 135),
                        (paper_x + 40, paper_y + 65),
                        (paper_x + paper_width - 40, paper_y + 65), 2)

        # Citation text
        body_font = self.visuals.fonts['body']
        small_font = self.visuals.fonts['small']

        citation_content = [
            ("FAILURE TO APPEAR - TRAFFIC VIOLATION", body_font, (30, 30, 30)),
            ("", None, None),
            ("You are hereby ordered to appear at:", small_font, (60, 60, 60)),
            ("County Courthouse, Room 204", body_font, (30, 30, 30)),
            ("", None, None),
            ("WITHIN 48 HOURS", header_font, LegalUIColors.URGENT),
            ("", None, None),
            ("Failure to appear will result in:", small_font, (60, 60, 60)),
            ("IMMEDIATE ARREST", body_font, LegalUIColors.URGENT),
            ("", None, None),
            ("This is your FINAL WARNING.", small_font, (80, 80, 80)),
        ]

        y_offset = paper_y + 85
        for line_text, font, color in citation_content:
            if font:
                text_surface = font.render(line_text, True, color)
                text_rect = text_surface.get_rect(centerx=paper_x + paper_width // 2, top=y_offset)
                screen.blit(text_surface, text_rect)
            y_offset += 28

        # Official stamp effect (appears after slide completes)
        if self.citation_timer > 0.5:
            stamp_alpha = min(255, int((self.citation_timer - 0.5) * 500))
            stamp_surface = pygame.Surface((120, 50), pygame.SRCALPHA)
            pygame.draw.rect(stamp_surface, (*LegalUIColors.LEGAL_PRIMARY, stamp_alpha),
                           (0, 0, 120, 50), border_radius=4)
            pygame.draw.rect(stamp_surface, (255, 255, 255, stamp_alpha),
                           (0, 0, 120, 50), 3, border_radius=4)

            stamp_font = self.visuals.fonts['small']
            stamp_text = stamp_font.render("OFFICIAL", True, (255, 255, 255))
            stamp_text.set_alpha(stamp_alpha)
            stamp_surface.blit(stamp_text, (25, 15))

            # Rotate slightly for realism
            rotated_stamp = pygame.transform.rotate(stamp_surface, -8)
            screen.blit(rotated_stamp, (paper_x + paper_width - 150, paper_y + paper_height - 80))

        # Continue prompt
        if self.citation_timer > 1.0:
            prompt_font = self.visuals.fonts['small']
            prompt_text = prompt_font.render("Press SPACE to continue", True, (120, 120, 120))
            prompt_rect = prompt_text.get_rect(centerx=self.SCREEN_WIDTH // 2,
                                              bottom=self.SCREEN_HEIGHT - 40)
            screen.blit(prompt_text, prompt_rect)

    def _draw_stress_vignette(self, screen):
        """Draw vignette effect for stress/anxiety"""
        intensity = self.vignette_intensity.value
        if intensity < 0.01:
            return

        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw gradient edges with red tint
        edge_width = int(150 * intensity)
        for i in range(edge_width):
            alpha = int(200 * intensity * (1 - i / edge_width) ** 2)
            color = (100, 20, 20, alpha)

            # All edges
            pygame.draw.line(vignette, color, (i, 0), (i, height))
            pygame.draw.line(vignette, color, (width - i - 1, 0), (width - i - 1, height))
            pygame.draw.line(vignette, color, (0, i), (width, i))
            pygame.draw.line(vignette, color, (0, height - i - 1), (width, height - i - 1))

        screen.blit(vignette, (0, 0))

    def _draw_continue_prompt(self, screen):
        """Draw continue prompt"""
        prompt_font = self.visuals.fonts['small']

        # Pulsing effect
        pulse = abs(math.sin(self.pulse_time * 2)) * 0.3 + 0.7
        alpha = int(200 * pulse)

        prompt_text = prompt_font.render("Press SPACE to continue", True, (150, 150, 150))
        prompt_text.set_alpha(alpha)
        prompt_rect = prompt_text.get_rect(bottomright=(self.SCREEN_WIDTH - 40, self.SCREEN_HEIGHT - 35))
        screen.blit(prompt_text, prompt_rect)

    def _wrap_text(self, text, font, max_width):
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

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _ease_out(self, t):
        """Ease out cubic function"""
        return 1 - pow(1 - t, 3)

    def get_results(self):
        """Return results of the activity"""
        return {
            'stayed_calm': self.anxiety_level < 50 if self.breathing_game else True,
            'citation_received': True,
            'scenes_completed': 3
        }

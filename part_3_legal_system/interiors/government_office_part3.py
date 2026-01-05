"""
Government Office Interior for Part 3 - Legal System
Handles police encounter, document processing, and bureaucratic barriers
Police encounter is now IN-GAME with animated NPCs and portrait dialogue
"""
import pygame
import math
import time
from src.interiors.narrative_interior import NarrativeInterior
from part_3_legal_system.dialogue_portraits import portrait_renderer, Emotion


class GovernmentOfficePart3(NarrativeInterior):
    """Government office with integrated police encounter and document activities"""

    # Part 3 handles its own portrait rendering with emotions
    handles_own_portraits = True

    # Speaker to character mapping for portraits
    SPEAKER_TO_CHARACTER = {
        'You': 'player',
        'Officer': 'officer',
        'Clerk': 'clerk',
        'Other Person': 'coworker',
    }

    # Emotion mapping per phase
    CONTEXT_EMOTIONS = {
        'police_stop': {
            'player': Emotion.SCARED,
            'officer': Emotion.STERN,
        },
        'stay_calm': {
            'player': Emotion.WORRIED,
            'officer': Emotion.NEUTRAL,
        },
        'court_citation': {
            'player': Emotion.RELIEVED,
            'officer': Emotion.STERN,
        },
        'gov_office_queue': {
            'player': Emotion.WORRIED,
            'clerk': Emotion.DISMISSIVE,
        },
        'document_sorting': {
            'player': Emotion.WORRIED,
            'clerk': Emotion.NEUTRAL,
        },
        'paperwork_rejection': {
            'player': Emotion.SCARED,
            'clerk': Emotion.DISMISSIVE,
        },
    }

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.documents_sorted = False
        self.paperwork_filed = False

        # Police encounter tracking (now dialogue-based)
        self.police_encounter_phase = None  # 'stop', 'calm', 'citation'
        self.breathing_count = 0
        self.breathing_target = 3  # Player needs to "breathe" 3 times

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Portrait system
        self.portrait_renderer = portrait_renderer

        # Police lights effect (for police phases)
        self.police_lights_timer = 0
        self.show_police_lights = False

        # Screen effects
        self.vignette_intensity = 0
        self.target_vignette = 0
        self.screen_shake = 0
        self.shake_timer = 0

        # Officer animation
        self.officer_walk_timer = 0
        self.officer_approached = False

    def enter(self):
        """Override enter to set up scene based on objective"""
        super().enter()

        print(f"[GOV_OFFICE_P3] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[GOV_OFFICE_P3]   current objective: {current.id if current else 'None'}")
        print(f"[GOV_OFFICE_P3]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[GOV_OFFICE_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()
                self.officer_approached = False
                self.breathing_count = 0

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[GOV_OFFICE_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[GOV_OFFICE_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        # Police encounter phases - all dialogue-based now
        if phase_id in ['police_stop', 'stay_calm', 'court_citation']:
            self.show_police_lights = True
            self.target_vignette = 0.3
            # Officer appears as NPC via narrative content

        else:
            self.show_police_lights = False
            self.target_vignette = 0

        # Government office phases
        if phase_id == 'document_sorting':
            interactions = self.narrative_content['document_sorting']['interactions']
            if 'sort_documents' in interactions:
                self.add_interactive_object('sort_documents', interactions['sort_documents'])

    def load_narrative_content(self):
        """Load narrative content - police encounter is now pure dialogue"""
        return {
            # Police encounter - dialogue based with portrait system
            'police_stop': {
                'npcs': [
                    {'name': 'Officer', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    (None, "Walking toward the government office. Tired. Worried."),
                    (None, "Suddenly - red and blue lights flash behind you."),
                    (None, "Your heart stops. A police car."),
                    (None, "An officer approaches you."),
                    ("Officer", "Excuse me. Can I see some ID?"),
                    ("You", "(heart racing) Uh, sure... what's this about?"),
                    ("Officer", "Routine check. Just need to run your name."),
                    (None, "You hand over your ID with shaking hands."),
                    ("Officer", "(into radio) Running a check..."),
                    (None, "Seconds feel like hours."),
                    (None, "The officer's expression changes."),
                    ("Officer", "There's a warrant for your arrest."),
                    ("You", "What?! I can explain—"),
                    ("Officer", "You missed your court date."),
                    ("You", "I had to work! I would have lost my job!"),
                    ("Officer", "That's not how the law works."),
                    (None, "Everything is spinning. This can't be happening."),
                ],
                'interactions': {}
            },

            'stay_calm': {
                'npcs': [
                    {'name': 'Officer', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    (None, "Your hands are shaking. Your vision narrows."),
                    ("Officer", "Hey. I need you to stay calm."),
                    ("You", "(trying to breathe) I just... I had to work..."),
                    ("Officer", "Take a deep breath. I'm not arresting you right now."),
                    (None, "You try to steady yourself..."),
                    (None, "[Press SPACE to take a deep breath]"),
                    (None, "That's one. Keep breathing..."),
                    (None, "[Press SPACE to breathe again]"),
                    (None, "Good. One more..."),
                    (None, "[Press SPACE to breathe once more]"),
                    (None, "Your heartbeat starts to slow."),
                    ("Officer", "Better. Now listen to me carefully."),
                ],
                'interactions': {}
            },

            'court_citation': {
                'npcs': [
                    {'name': 'Officer', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Officer", "Look, I could take you in right now."),
                    ("You", "Please... I have school. I have work..."),
                    ("Officer", "I'm going to give you a break."),
                    (None, "He pulls out a citation pad."),
                    ("Officer", "You have 48 hours to appear at the courthouse."),
                    ("Officer", "48 hours. Not 49. Not 'when you get around to it.'"),
                    ("You", "You're... not arresting me?"),
                    ("Officer", "Against my better judgment, no."),
                    ("Officer", "But if you miss this deadline..."),
                    ("Officer", "I will personally come find you."),
                    (None, "He hands you a citation. Your hands still tremble."),
                    ("Officer", "Don't make me regret this."),
                    ("You", "I won't. Thank you. I'm sorry."),
                    (None, "The officer returns to his car."),
                    (None, "The red and blue lights fade away."),
                    (None, "48 hours. Another impossible deadline."),
                    (None, "But at least you're not in handcuffs."),
                ],
                'interactions': {}
            },

            # Government office phases
            'gov_office_queue': {
                'npcs': [
                    {'name': 'Clerk', 'x': 8, 'y': 3},
                    {'name': 'Other Person', 'x': 6, 'y': 8}
                ],
                'dialogue_sequence': [
                    (None, "The government office is packed."),
                    (None, "Numbers being called. Fluorescent lights humming."),
                    (None, "Your ticket says 247. They're on 198."),
                    ("Other Person", "Been here since 7am. Don't expect to leave before noon."),
                    ("You", "But I have class later..."),
                    ("Other Person", "Welcome to the system, kid."),
                    (None, "Hours pass. The lights buzz overhead."),
                    (None, "Finally, your number is called."),
                    ("Clerk", "Number 247! Window 3!"),
                ],
                'interactions': {}
            },

            'document_sorting': {
                'npcs': [
                    {'name': 'Clerk', 'x': 8, 'y': 3}
                ],
                'dialogue_sequence': [
                    ("Clerk", "I need these documents sorted for processing."),
                    ("Clerk", "Legal documents on the left. Personal records on the right."),
                    ("You", "Okay, I think I understand..."),
                    (None, "The clerk slides a stack of papers across the counter."),
                ],
                'interactions': {
                    'sort_documents': {
                        'position': (8, 5),
                        'prompt': 'Sort the documents',
                        'trigger_activity': 'document_sorting',
                        'required': True
                    }
                }
            },

            'paperwork_rejection': {
                'npcs': [
                    {'name': 'Clerk', 'x': 8, 'y': 3}
                ],
                'dialogue_sequence': [
                    ("Clerk", "I'm sorry, but this form is missing a signature."),
                    ("You", "What? Where? I signed everywhere!"),
                    ("Clerk", "Page 3, section B, subsection ii."),
                    ("You", "That section wasn't even on my form!"),
                    ("Clerk", "You'll need to come back with the correct form."),
                    ("Clerk", "We close in 30 minutes, so... tomorrow?"),
                    ("You", "But I've been here all day!"),
                    ("Clerk", "Next in line please!"),
                    (None, "Another day lost to bureaucracy."),
                ],
                'interactions': {}
            }
        }

    def _get_activity_manager(self):
        """Get the UniversalActivityManager"""
        if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'activity_manager'):
            return self.game.objective_manager.activity_manager
        return None

    def _start_activity_via_manager(self, objective_id):
        """Start activity via UniversalActivityManager"""
        activity_manager = self._get_activity_manager()
        if activity_manager:
            if activity_manager.current_activity:
                if activity_manager.current_activity.active:
                    return False
                elif not activity_manager.current_activity.completed:
                    return False

            success = activity_manager.start_activity_for_objective(objective_id, narrative_ref=self)
            if success:
                print(f"[GOV_OFFICE_P3] Started activity for {objective_id}")
                return True
        return False

    def update_objective_display(self):
        """Update objective text"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        displays = {
            'police_stop': ("Police Stop", "An officer wants to talk to you"),
            'stay_calm': ("Stay Calm", "Focus on your breathing"),
            'court_citation': ("Citation", "Listen to the officer"),
            'gov_office_queue': ("Wait in Line", "Your number: 247"),
            'document_sorting': ("Sort Documents", "Legal vs Personal"),
            'paperwork_rejection': ("Submit Paperwork", "Hope for approval"),
        }

        if current.id in displays:
            current.dynamic_description = displays[current.id][0]
            current.progress_text = displays[current.id][1]

    def interact_with_object(self, name):
        """Handle interactions"""
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'document_sorting':
                self._start_activity_via_manager('document_sorting')
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            self.end_narrative_sequence()

    def on_activity_complete(self, activity, results):
        """Callback when activity completes"""
        print(f"[GOV_OFFICE_P3] Activity complete: {results}")

        if self.current_objective_phase == 'document_sorting':
            self.documents_sorted = True

        if self.check_objective_complete():
            self.end_narrative_sequence()

    def handle_event(self, event):
        """Handle events"""
        # Check for activity
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity and activity_manager.current_activity.active:
            activity_manager.handle_event(event)
            return

        super().handle_event(event)

    def update(self, dt):
        """Update with visual effects"""
        super().update(dt)

        # Update police lights
        if self.show_police_lights:
            self.police_lights_timer += dt * 3

        # Update vignette
        if self.vignette_intensity < self.target_vignette:
            self.vignette_intensity = min(self.target_vignette, self.vignette_intensity + dt * 0.5)
        elif self.vignette_intensity > self.target_vignette:
            self.vignette_intensity = max(self.target_vignette, self.vignette_intensity - dt * 0.5)

        # Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.screen_shake = 3 * (self.shake_timer / 0.3)
        else:
            self.screen_shake = 0

        # Activity manager update
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity:
            activity_manager.update(dt)

    def _get_dialogue_characters(self):
        """Get characters for portrait rendering"""
        if not self.dialogue_box.active:
            return None, None, None

        speaker = self.dialogue_box.current_speaker
        phase = self.current_objective_phase

        speaking_char = self.SPEAKER_TO_CHARACTER.get(speaker) if speaker else None

        left_char = 'player'
        right_char = None

        # Determine right character based on phase
        if phase in ['police_stop', 'stay_calm', 'court_citation']:
            right_char = 'officer'
        elif phase in ['gov_office_queue', 'document_sorting', 'paperwork_rejection']:
            if speaker == 'Other Person':
                right_char = 'coworker'
            else:
                right_char = 'clerk'

        return left_char, right_char, speaking_char

    def _get_character_emotion(self, char_id):
        """Get emotion for character"""
        phase = self.current_objective_phase
        if phase in self.CONTEXT_EMOTIONS:
            return self.CONTEXT_EMOTIONS[phase].get(char_id, Emotion.NEUTRAL)
        return Emotion.NEUTRAL

    def draw(self, screen):
        """Draw with police lights and portrait system"""
        # Check for active activity
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity:
            current_activity = activity_manager.current_activity
            if current_activity.active and not getattr(current_activity, 'completed', False):
                activity_manager.draw(screen)
                return

        # Draw base interior
        super().draw(screen)

        # Police lights effect during police phases
        if self.show_police_lights and self.current_objective_phase in ['police_stop', 'stay_calm', 'court_citation']:
            self._draw_police_lights(screen)

        # Stress vignette
        if self.vignette_intensity > 0.01:
            self._draw_vignette(screen)

        # Draw portraits during dialogue
        if self.dialogue_box.active:
            left_char, right_char, speaking = self._get_dialogue_characters()

            if left_char:
                left_emotion = self._get_character_emotion(left_char)
                self.portrait_renderer.draw_portrait(
                    screen, left_char, 'left',
                    emotion=left_emotion,
                    is_speaking=(speaking == left_char)
                )

            if right_char:
                right_emotion = self._get_character_emotion(right_char)
                self.portrait_renderer.draw_portrait(
                    screen, right_char, 'right',
                    emotion=right_emotion,
                    is_speaking=(speaking == right_char)
                )

        # Phase indicator for police encounter
        if self.current_objective_phase in ['police_stop', 'stay_calm', 'court_citation']:
            self._draw_phase_indicator(screen)

    def _draw_police_lights(self, screen):
        """Draw police light effect overlay"""
        # Calculate light phase
        phase = (math.sin(self.police_lights_timer) + 1) / 2

        # Create overlay
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)

        # Red and blue alternating glow from edges
        red_intensity = int(40 * (1 - phase))
        blue_intensity = int(40 * phase)

        # Left edge red
        for x in range(100):
            alpha = int(red_intensity * (1 - x / 100))
            pygame.draw.line(overlay, (200, 0, 0, alpha), (x, 0), (x, self.SCREEN_HEIGHT))

        # Right edge blue
        for x in range(100):
            alpha = int(blue_intensity * (1 - x / 100))
            pygame.draw.line(overlay, (0, 0, 200, alpha),
                           (self.SCREEN_WIDTH - x - 1, 0),
                           (self.SCREEN_WIDTH - x - 1, self.SCREEN_HEIGHT))

        screen.blit(overlay, (0, 0))

    def _draw_vignette(self, screen):
        """Draw stress vignette"""
        width, height = screen.get_size()
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)

        edge_width = int(100 * self.vignette_intensity)
        for i in range(edge_width):
            alpha = int(150 * self.vignette_intensity * (1 - i / edge_width) ** 2)
            color = (80, 20, 20, alpha)

            pygame.draw.line(vignette, color, (i, 0), (i, height))
            pygame.draw.line(vignette, color, (width - i - 1, 0), (width - i - 1, height))
            pygame.draw.line(vignette, color, (0, i), (width, i))
            pygame.draw.line(vignette, color, (0, height - i - 1), (width, height - i - 1))

        screen.blit(vignette, (0, 0))

    def _draw_phase_indicator(self, screen):
        """Draw indicator for police encounter phase"""
        phase_names = {
            'police_stop': '⚠ POLICE STOP',
            'stay_calm': '💨 STAY CALM',
            'court_citation': '📋 CITATION',
        }

        if self.current_objective_phase in phase_names:
            font = pygame.font.Font(None, 28)
            text = font.render(phase_names[self.current_objective_phase], True, (255, 200, 100))
            text_rect = text.get_rect(topright=(self.SCREEN_WIDTH - 20, 20))

            # Background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 200, 100), bg_rect, 2, border_radius=5)

            screen.blit(text, text_rect)

    def end_narrative_sequence(self):
        """Handle transitions"""
        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[GOV_OFFICE_P3] Completing: {current.id}")

        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

    def check_objective_complete(self):
        """Check if objective is complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Police phases are dialogue-only now
        if current.id in ['police_stop', 'stay_calm', 'court_citation']:
            return True  # Complete when dialogue ends

        if current.id == 'document_sorting':
            return self.documents_sorted

        # Dialogue-only scenes
        if current.id in ['gov_office_queue', 'paperwork_rejection']:
            return True

        return True

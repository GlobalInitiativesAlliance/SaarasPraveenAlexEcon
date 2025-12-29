"""
Workplace Interior for Part 3 - Legal System
Handles morning shift and missed court notification scenes
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class WorkplacePart3(NarrativeInterior):
    """Workplace with Part 3 legal system narrative - choosing work over court"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.shift_started = False
        self.warrant_notification_received = False

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up workplace scene based on objective"""
        super().enter()

        print(f"[WORK_P3] enter() called")

        current = self.game.objective_manager.get_current_objective()
        print(f"[WORK_P3]   current objective: {current.id if current else 'None'}")

        if current:
            if self.current_objective_phase != current.id:
                print(f"[WORK_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            if not self.phase_initialized:
                print(f"[WORK_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        # Both workplace scenes are dialogue-only
        pass

    def load_narrative_content(self):
        """Load the workplace narrative content for Part 3"""
        return {
            'morning_shift': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 4},
                    {'name': 'Coworker', 'x': 5, 'y': 6},
                ],
                'dialogue_sequence': [
                    (None, "You chose work over court."),
                    (None, "The decision weighs on you as you walk through the door."),
                    ("You", "(thinking) I can't risk losing this job. I'll figure out court later."),
                    (None, "Your manager spots you immediately."),
                    ("Manager", "Good, you're here. We're short-staffed today."),
                    ("You", "Yeah, I'm... I'm here."),
                    ("Manager", "You don't look so good. Everything okay?"),
                    ("You", "Just tired. Didn't sleep well."),
                    ("Manager", "Well, push through it. It's going to be a long day."),
                    (None, "You clock in. The familiar routine begins."),
                    (None, "But today, nothing feels routine."),
                    ("Coworker", "Hey, you okay? You keep checking your phone."),
                    ("You", "I'm fine. Just... waiting for something."),
                    (None, "Every minute feels heavy with the weight of your decision."),
                    (None, "You glance at the clock. 9:15 AM."),
                    ("You", "(thinking) Court started at 9. It's already past..."),
                    (None, "There's no going back now."),
                    ("You", "(thinking) What's done is done. Focus on work."),
                ],
                'interactions': {}
            },

            'missed_court_notice': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 4},
                ],
                'dialogue_sequence': [
                    (None, "It's your break. Finally a moment to breathe."),
                    (None, "Your phone buzzes. Unknown number."),
                    ("You", "(thinking) Should I answer? What if it's about court?"),
                    (None, "You let it go to voicemail. Then check it."),
                    ("Voicemail", "'This is an automated message from the County Court.'"),
                    ("Voicemail", "'You failed to appear for your scheduled hearing...'"),
                    (None, "Your heart stops."),
                    ("Voicemail", "'...a bench warrant has been issued for your arrest...'"),
                    ("You", "(whispering) A warrant? For missing court?"),
                    ("Voicemail", "'You must appear within 48 hours or face arrest.'"),
                    ("You", "I was at WORK! I had to be here!"),
                    (None, "But the system doesn't care about your reasons."),
                    (None, "You're now technically a fugitive."),
                    (None, "All because you had to choose between court and your job."),
                    ("Manager", "(from nearby) Break's over in 5 minutes!"),
                    ("You", "(trying to compose yourself) Yeah... okay."),
                    (None, "You slide your phone back in your pocket."),
                    (None, "Your hands are shaking."),
                    ("You", "(thinking) I have to finish this shift. Then figure this out."),
                    (None, "The weight of the warrant presses down on every moment."),
                    (None, "But you have no choice. You need this job."),
                    (None, "So you go back to work. Like nothing happened."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on workplace progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'morning_shift':
            current.dynamic_description = "Work your shift"
            current.progress_text = "Court can wait... right?"

        elif current.id == 'missed_court_notice':
            current.dynamic_description = "Check your voicemail"
            current.progress_text = "Something's wrong..."

    def end_narrative_sequence(self):
        """Override to properly handle workplace transitions"""
        print(f"[WORK_P3] *** end_narrative_sequence() CALLED ***")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()

        if not current:
            return

        if not self.check_objective_complete():
            print(f"[WORK_P3] Objective not complete yet")
            return

        def _complete_and_transition(from_phase, to_phase):
            print(f"[WORK_P3] Completing {from_phase}, moving to {to_phase}")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.should_exit = False

            next_obj = self.game.objective_manager.get_current_objective()
            if next_obj and next_obj.id == to_phase:
                self.enter()

        if current.id == 'morning_shift':
            _complete_and_transition('morning_shift', 'missed_court_notice')
        elif current.id == 'missed_court_notice':
            # Exit workplace - player encounters police on way home
            print("[WORK_P3] Completing missed_court_notice, exiting workplace")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.active = False
        else:
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.should_exit = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Both workplace scenes are dialogue-only, so complete after dialogue
        return True

    def draw(self, screen):
        """Draw workplace interior"""
        super().draw(screen)

        # Add visual cues based on scene
        if self.current_objective_phase == 'missed_court_notice':
            # Anxious overlay after hearing voicemail
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(25)
            overlay.fill((50, 0, 0))  # Dark red anxiety tint
            screen.blit(overlay, (0, 0))

            # Subtle vignette effect
            vignette = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            for i in range(50):
                alpha = int((50 - i) * 2)
                pygame.draw.rect(vignette, (0, 0, 0, alpha),
                               (i, i, self.SCREEN_WIDTH - 2*i, self.SCREEN_HEIGHT - 2*i), 1)
            screen.blit(vignette, (0, 0))

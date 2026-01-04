"""
TLP Apartment Interior for Part 3 - Legal System
Handles mail sorting, court notice discovery, and return home scenes
Enhanced with portrait system for dialogue
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior
from part_3_legal_system.dialogue_portraits import portrait_renderer, Emotion


class TLPApartmentPart3(NarrativeInterior):
    """TLP apartment with legal system narrative phases"""

    # Speaker name to character ID mapping for portraits
    SPEAKER_TO_CHARACTER = {
        'You': 'player',
        'Boss': None,  # Text message, no portrait
    }

    # Emotion mapping for specific dialogue contexts
    CONTEXT_EMOTIONS = {
        'mail_on_floor': {
            'player': Emotion.WORRIED,
        },
        'read_court_notice': {
            'player': Emotion.SCARED,
        },
        'go_home': {
            'player': Emotion.WORRIED,
        },
    }

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.mail_sorted = False
        self.court_notice_read = False

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Portrait system
        self.portrait_renderer = portrait_renderer

    def enter(self):
        """Override enter to set up apartment scene based on objective"""
        super().enter()

        print(f"[TLP_APT_P3] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[TLP_APT_P3]   current objective: {current.id if current else 'None'}")
        print(f"[TLP_APT_P3]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[TLP_APT_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[TLP_APT_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[TLP_APT_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'mail_on_floor':
            # Mail sorting scene
            interactions = self.narrative_content['mail_on_floor']['interactions']
            if 'sort_mail' in interactions:
                self.add_interactive_object('sort_mail', interactions['sort_mail'])

        elif phase_id == 'read_court_notice':
            # Reading court notice - just dialogue
            pass  # Dialogue sequence handles this

        elif phase_id == 'go_home':
            # Return home after courthouse
            pass  # Dialogue sequence handles this

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 3"""
        return {
            'mail_on_floor': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You return to your TLP apartment after a long day."),
                    (None, "Mail is scattered across the floor - you've been too busy to sort it."),
                    (None, "Bills, junk mail, official-looking envelopes... it's overwhelming."),
                    ("You", "I should really go through this stuff..."),
                ],
                'interactions': {
                    'sort_mail': {
                        'position': (8, 6),
                        'prompt': 'Sort through the mail',
                        'trigger_activity': 'mail_sorting',
                        'required': True
                    }
                }
            },

            'read_court_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Among the sorted mail, one envelope stands out."),
                    (None, "Official government letterhead. Your name in bold."),
                    ("You", "(reading) 'You are hereby summoned to appear...'"),
                    ("You", "A court date? For what? I didn't do anything!"),
                    (None, "The summons is for an unpaid traffic violation from months ago."),
                    (None, "You remember now - a ticket you couldn't afford to pay."),
                    (None, "Court date: Tomorrow morning. 9:00 AM."),
                    ("You", "Tomorrow?! But I have class AND work tomorrow!"),
                    (None, "The letter warns: Failure to appear may result in a warrant."),
                    ("You", "I can't miss work. I'll lose my job. But court..."),
                    (None, "Your phone buzzes. A text from your boss."),
                    ("Boss", "(text) Reminder: 7am shift tomorrow. MANDATORY. No excuses."),
                    ("You", "7am work. 9am court. How am I supposed to do both?"),
                    (None, "There's no good option. Only impossible choices."),
                ],
                'interactions': {}
            },

            'go_home': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You're back at your apartment."),
                    (None, "The court papers sit heavy in your pocket."),
                    (None, "$300 in fines. 30 days to pay."),
                    ("You", "Three hundred dollars..."),
                    (None, "That's almost your entire paycheck."),
                    ("You", "Rent is due next week. And utilities. And food."),
                    (None, "You sit on the edge of your bed, staring at the papers."),
                    ("You", "How am I supposed to survive this?"),
                    (None, "The walls feel like they're closing in."),
                    (None, "But there's no time to process. There never is."),
                    ("You", "I have an exam to study for..."),
                    (None, "You pull out your textbook, but the words blur together."),
                    (None, "Court. Work. School. Survival."),
                    (None, "Pick two. You can't have all four."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on apartment progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'mail_on_floor':
            if not self.mail_sorted:
                current.dynamic_description = "Sort through the scattered mail"
                current.progress_text = "Find anything important"
            else:
                current.dynamic_description = "Mail sorted..."

        elif current.id == 'read_court_notice':
            current.dynamic_description = "Read the official-looking envelope"
            current.progress_text = "Discover the court summons"

        elif current.id == 'go_home':
            current.dynamic_description = "Return to your apartment"
            current.progress_text = "Process everything that happened"

    def end_narrative_sequence(self):
        """Override to properly handle apartment transitions - Part 1 pattern"""
        print(f"")
        print(f"="*80)
        print(f"[TLP_APT_P3] *** end_narrative_sequence() CALLED ***")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[TLP_APT_P3]   current objective: {current.id if current else 'None'}")
        print(f"[TLP_APT_P3]   objective complete check: {self.check_objective_complete()}")
        print(f"="*80)

        if not current:
            return

        # Only signal completion when the objective is actually complete (all tasks done)
        if not self.check_objective_complete():
            print(f"[TLP_APT_P3] Objective not complete yet - waiting for interactions")
            return

        # Part 1 Pattern: Just set should_exit flag
        # Main game's complete_current_objective() handles advancement and re-entry
        print(f"[TLP_APT_P3] Objective complete - setting should_exit = True")
        print(f"[TLP_APT_P3]   Main game will handle advancement via complete_current_objective()")
        self.should_exit = True

        # Call complete_current_objective() to let main game handle transition
        self.game.objective_manager.complete_current_objective()

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'mail_on_floor':
            print(f"[TLP_APT_P3] check_objective_complete for {current.id}")
            print(f"[TLP_APT_P3]   mail_sorted: {self.mail_sorted}")
            return self.mail_sorted

        # Get required interactions for current phase
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        # Find all required interactions
        required_interactions = set()
        for obj_name, obj_data in interactions.items():
            if obj_data.get('required', False):
                required_interactions.add(obj_name)

        print(f"[TLP_APT_P3] check_objective_complete for {current.id}")
        print(f"[TLP_APT_P3]   required: {required_interactions}")
        print(f"[TLP_APT_P3]   completed: {self.completed_interactions}")

        # Check if all required interactions are completed
        if required_interactions:
            completion_status = required_interactions.issubset(self.completed_interactions)
            print(f"[TLP_APT_P3]   completion status: {completion_status}")
            return completion_status
        else:
            # If no required interactions, complete after dialogue ends
            print(f"[TLP_APT_P3]   no required interactions - complete")
            return True

    def launch_activity(self, activity_name):
        """Launch activity by name - bridges NarrativeInterior to specific activities"""
        print(f"[TLP_APT_P3] Activity trigger: {activity_name}")

        if activity_name == 'mail_sorting':
            self._start_activity_via_manager('mail_on_floor')
        else:
            print(f"[TLP_APT_P3] Unknown activity: {activity_name}")

    def _get_activity_manager(self):
        """Get the UniversalActivityManager"""
        if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'activity_manager'):
            return self.game.objective_manager.activity_manager
        return None

    def _start_activity_via_manager(self, objective_id):
        """Start activity via UniversalActivityManager"""
        activity_manager = self._get_activity_manager()
        if activity_manager:
            # Check if ANY activity is already running (active OR just exists)
            if activity_manager.current_activity:
                if activity_manager.current_activity.active:
                    print("[TLP_APT_P3] Activity already running and active, skipping launch")
                    return False
                elif not activity_manager.current_activity.completed:
                    print("[TLP_APT_P3] Activity exists but not completed, skipping launch")
                    return False

            success = activity_manager.start_activity_for_objective(objective_id, narrative_ref=self)
            if success:
                print(f"[TLP_APT_P3] Started activity via UniversalActivityManager for {objective_id}")
                return True
            else:
                print(f"[TLP_APT_P3] Failed to start activity via manager for {objective_id}")
        return False

    def interact_with_object(self, name):
        """Handle apartment-specific interactions"""
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'mail_on_floor'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified - use UniversalActivityManager
            trigger = interaction.get('trigger_activity')

            if trigger == 'mail_sorting':
                self._start_activity_via_manager('mail_on_floor')
                return

        # Use parent's interaction handling
        super().interact_with_object(name)

        self.update_objective_display()

        # Check if current phase is complete (will trigger end_narrative_sequence)
        if self.check_objective_complete():
            print(f"[TLP_APT_P3] Phase complete, end_narrative_sequence will handle transition")
            self.end_narrative_sequence()

    def on_activity_complete(self, activity, results):
        """Callback from UniversalActivityManager when activity completes"""
        print(f"[TLP_APT_P3] on_activity_complete called with results: {results}")

        if self.current_objective_phase == 'mail_on_floor':
            self.mail_sorted = True
            if results and results.get('court_notice_found'):
                print("[TLP_APT_P3] Court notice found in mail!")

        # Check if objective is now complete and transition
        if self.check_objective_complete():
            print(f"[TLP_APT_P3] Objective complete - calling end_narrative_sequence")
            self.end_narrative_sequence()

    def handle_event(self, event):
        """Handle events with activity priority - delegates to UniversalActivityManager"""
        # Check if activity manager has active activity - MUST be checked first
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity and activity_manager.current_activity.active:
            # Route ALL events (including ESC) to activity first
            activity_manager.handle_event(event)
            return  # Don't let parent handle the event

        # Use parent's event handling only when no activity is active
        super().handle_event(event)

    def update(self, dt):
        """Update with activity management - delegates to UniversalActivityManager"""
        super().update(dt)

        # Let activity manager handle its own updates
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity:
            # Activity manager update returns True if activity completed
            # The on_activity_complete callback will handle state changes
            activity_manager.update(dt)

    def _get_dialogue_characters(self):
        """Determine which characters should be shown for current dialogue"""
        if not self.dialogue_box.active:
            return None, None, None

        speaker = self.dialogue_box.current_speaker
        phase = self.current_objective_phase

        # Map speaker to character
        speaking_char = self.SPEAKER_TO_CHARACTER.get(speaker) if speaker else None

        # Apartment scenes are mostly solo/internal monologue
        left_char = 'player'  # Player always on left
        right_char = None  # No other characters in apartment

        return left_char, right_char, speaking_char

    def _get_character_emotion(self, char_id):
        """Get emotion for a character in current context"""
        phase = self.current_objective_phase
        if phase in self.CONTEXT_EMOTIONS:
            return self.CONTEXT_EMOTIONS[phase].get(char_id, Emotion.NEUTRAL)
        return Emotion.NEUTRAL

    def draw(self, screen):
        """Draw apartment interior with portrait system"""
        # Check if activity manager has active activity
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity:
            current_activity = activity_manager.current_activity
            if current_activity.active and not getattr(current_activity, 'completed', False):
                activity_manager.draw(screen)
                return

        # Draw base interior (normal view)
        super().draw(screen)

        # Add subtle visual cues based on scene
        if self.current_objective_phase == 'go_home':
            # Dark overlay for somber mood
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(30)
            overlay.fill((0, 0, 40))  # Dark blue tint
            screen.blit(overlay, (0, 0))

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

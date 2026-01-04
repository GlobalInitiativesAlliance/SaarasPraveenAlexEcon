"""
School Interior for Part 3 - Legal System
Handles arrival at school and note-taking while distracted scenes
Enhanced with portrait system for dialogue
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior
from part_3_legal_system.dialogue_portraits import portrait_renderer, Emotion


class SchoolPart3(NarrativeInterior):
    """School/Classroom with Part 3 legal system narrative"""

    # Speaker name to character ID mapping for portraits
    SPEAKER_TO_CHARACTER = {
        'You': 'player',
        'Professor': 'professor',
        'Classmate': 'coworker',  # Reuse coworker for classmate
        'Boss': None,  # Text message, no portrait
    }

    # Emotion mapping for specific dialogue contexts
    CONTEXT_EMOTIONS = {
        'walk_to_school': {
            'player': Emotion.WORRIED,
            'coworker': Emotion.FRIENDLY,
        },
        'class_distraction': {
            'player': Emotion.WORRIED,
            'professor': Emotion.UNDERSTANDING,
        },
    }

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.notes_completed = False
        self.arrived_at_school = False

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Portrait system
        self.portrait_renderer = portrait_renderer

    def enter(self):
        """Override enter to set up school scene based on objective"""
        super().enter()

        print(f"[SCHOOL_P3] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P3]   current objective: {current.id if current else 'None'}")
        print(f"[SCHOOL_P3]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[SCHOOL_P3]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[SCHOOL_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[SCHOOL_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'walk_to_school':
            # Arrival scene - just dialogue
            pass

        elif phase_id == 'class_distraction':
            # Note-taking with distractions
            interactions = self.narrative_content['class_distraction']['interactions']
            if 'take_notes' in interactions:
                self.add_interactive_object('take_notes', interactions['take_notes'])

    def load_narrative_content(self):
        """Load the school narrative content for Part 3"""
        return {
            'walk_to_school': {
                'npcs': [
                    {'name': 'Classmate', 'x': 5, 'y': 4},
                ],
                'dialogue_sequence': [
                    (None, "You arrive at school, exhausted and distracted."),
                    ("You", "I couldn't sleep last night. That court thing..."),
                    (None, "Your mind keeps racing through impossible options."),
                    (None, "Your phone buzzes. Another text from your boss."),
                    ("Boss", "(text) Don't forget - 7am shift tomorrow. MANDATORY."),
                    ("You", "Court is at 9am. Work is at 7am. Class is now."),
                    (None, "A classmate waves at you from across the hall."),
                    ("Classmate", "Hey! You look tired. Everything okay?"),
                    ("You", "Yeah, just... a lot going on. You know how it is."),
                    ("Classmate", "Totally. Hey, don't forget - exam next week!"),
                    ("You", "Right... the exam..."),
                    (None, "Another thing to worry about. Another ball to juggle."),
                    (None, "You take a seat as the professor begins."),
                ],
                'interactions': {}
            },

            'class_distraction': {
                'npcs': [
                    {'name': 'Professor', 'x': 8, 'y': 2},
                ],
                'dialogue_sequence': [
                    ("Professor", "Good morning, everyone. Today we'll cover Chapter 7."),
                    ("Professor", "Constitutional Rights - an important topic."),
                    (None, "You pull out your notebook, trying to focus."),
                    ("Professor", "The right to due process. The right to representation."),
                    (None, "Your phone vibrates in your pocket."),
                    ("You", "(thinking) Ignore it. Focus on class."),
                    ("Professor", "Pay attention - this will be on the exam."),
                    (None, "Another vibration. And another."),
                    ("You", "(thinking) I need to focus. But what about court?"),
                    (None, "The irony isn't lost on you - learning about legal rights"),
                    (None, "while your own legal problems threaten to consume you."),
                ],
                'interactions': {
                    'take_notes': {
                        'position': (6, 5),
                        'prompt': 'Try to take notes',
                        'trigger_activity': 'note_taking',
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on school progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'walk_to_school':
            current.dynamic_description = "Head to class"
            current.progress_text = "Try to focus despite everything"

        elif current.id == 'class_distraction':
            if not self.notes_completed:
                current.dynamic_description = "Take notes in class"
                current.progress_text = "Stay focused despite distractions"
            else:
                current.dynamic_description = "Class ending..."

    def end_narrative_sequence(self):
        """Override to properly handle school transitions - Part 1 pattern"""
        print(f"")
        print(f"="*80)
        print(f"[SCHOOL_P3] *** end_narrative_sequence() CALLED ***")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[SCHOOL_P3]   current objective: {current.id if current else 'None'}")
        print(f"[SCHOOL_P3]   objective complete check: {self.check_objective_complete()}")
        print(f"="*80)

        if not current:
            return

        # Only signal completion when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[SCHOOL_P3] Objective not complete yet - waiting for interactions")
            return

        # Part 1 Pattern: Just set should_exit flag
        # Main game's complete_current_objective() handles advancement and re-entry
        print(f"[SCHOOL_P3] Objective complete - setting should_exit = True")
        print(f"[SCHOOL_P3]   Main game will handle advancement via complete_current_objective()")
        self.should_exit = True

        # Call complete_current_objective() to let main game handle transition
        self.game.objective_manager.complete_current_objective()

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'class_distraction':
            print(f"[SCHOOL_P3] check_objective_complete for {current.id}")
            print(f"[SCHOOL_P3]   notes_completed: {self.notes_completed}")
            return self.notes_completed

        # Get required interactions for current phase
        current_content = self.narrative_content.get(current.id, {})
        interactions = current_content.get('interactions', {})

        required_interactions = set()
        for obj_name, obj_data in interactions.items():
            if obj_data.get('required', False):
                required_interactions.add(obj_name)

        print(f"[SCHOOL_P3] check_objective_complete for {current.id}")
        print(f"[SCHOOL_P3]   required: {required_interactions}")
        print(f"[SCHOOL_P3]   completed: {self.completed_interactions}")

        if required_interactions:
            completion_status = required_interactions.issubset(self.completed_interactions)
            return completion_status
        else:
            return True

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
                    print("[SCHOOL_P3] Activity already running and active, skipping launch")
                    return False
                elif not activity_manager.current_activity.completed:
                    print("[SCHOOL_P3] Activity exists but not completed, skipping launch")
                    return False

            success = activity_manager.start_activity_for_objective(objective_id, narrative_ref=self)
            if success:
                print(f"[SCHOOL_P3] Started activity via UniversalActivityManager for {objective_id}")
                return True
            else:
                print(f"[SCHOOL_P3] Failed to start activity via manager for {objective_id}")
        return False

    def launch_activity(self, activity_name):
        """Launch activity by name"""
        print(f"[SCHOOL_P3] Activity trigger: {activity_name}")

        if activity_name == 'note_taking':
            self._start_activity_via_manager('class_distraction')
        else:
            print(f"[SCHOOL_P3] Unknown activity: {activity_name}")

    def interact_with_object(self, name):
        """Handle school-specific interactions"""
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'walk_to_school'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'note_taking':
                self._start_activity_via_manager('class_distraction')
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            print(f"[SCHOOL_P3] Phase complete")
            self.end_narrative_sequence()

    def on_activity_complete(self, activity, results):
        """Callback from UniversalActivityManager when activity completes"""
        print(f"[SCHOOL_P3] on_activity_complete called with results: {results}")

        if self.current_objective_phase == 'class_distraction':
            self.notes_completed = True
            if results:
                stress_gained = results.get('stress', 0)
                print(f"[SCHOOL_P3] Notes completed with stress: {stress_gained}")

        # Check if objective is now complete and transition
        if self.check_objective_complete():
            print(f"[SCHOOL_P3] Objective complete - calling end_narrative_sequence")
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

        # Determine character positions based on scene
        left_char = 'player'  # Player always on left
        right_char = None

        # Determine right character based on phase and speaker
        if phase == 'walk_to_school':
            right_char = 'coworker' if speaker == 'Classmate' else None
        elif phase == 'class_distraction':
            right_char = 'professor'

        return left_char, right_char, speaking_char

    def _get_character_emotion(self, char_id):
        """Get emotion for a character in current context"""
        phase = self.current_objective_phase
        if phase in self.CONTEXT_EMOTIONS:
            return self.CONTEXT_EMOTIONS[phase].get(char_id, Emotion.NEUTRAL)
        return Emotion.NEUTRAL

    def draw(self, screen):
        """Draw school interior with portrait system"""
        # Check if activity manager has active activity
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity:
            current_activity = activity_manager.current_activity
            if current_activity.active and not getattr(current_activity, 'completed', False):
                activity_manager.draw(screen)
                return

        # Draw base interior
        super().draw(screen)

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

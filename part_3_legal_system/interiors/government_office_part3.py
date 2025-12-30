"""
Government Office Interior for Part 3 - Legal System
Handles document processing, bureaucratic barriers, and system navigation
Uses UniversalActivityManager for consistent activity management
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class GovernmentOfficePart3(NarrativeInterior):
    """Government office with Part 3 legal system document sorting activity"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.documents_sorted = False
        self.paperwork_filed = False
        self.police_encounter_complete = False
        self.stayed_calm = False
        self.citation_received = False

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up office scene based on objective"""
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

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[GOV_OFFICE_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[GOV_OFFICE_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

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
                    print("[GOV_OFFICE_P3] Activity already running and active, skipping launch")
                    return False
                elif not activity_manager.current_activity.completed:
                    print("[GOV_OFFICE_P3] Activity exists but not completed, skipping launch")
                    return False

            success = activity_manager.start_activity_for_objective(objective_id, narrative_ref=self)
            if success:
                print(f"[GOV_OFFICE_P3] Started activity via UniversalActivityManager for {objective_id}")
                return True
            else:
                print(f"[GOV_OFFICE_P3] Failed to start activity via manager for {objective_id}")
        return False

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        # Police encounter phases
        if phase_id == 'police_stop':
            # Police stop - start encounter activity
            interactions = self.narrative_content.get('police_stop', {}).get('interactions', {})
            if 'police_encounter' in interactions:
                self.add_interactive_object('police_encounter', interactions['police_encounter'])

        elif phase_id == 'stay_calm':
            # Breathing exercise - auto-start activity
            interactions = self.narrative_content.get('stay_calm', {}).get('interactions', {})
            if 'breathing_exercise' in interactions:
                self.add_interactive_object('breathing_exercise', interactions['breathing_exercise'])

        elif phase_id == 'court_citation':
            # Citation scene - dialogue only
            pass

        # Government office phases
        elif phase_id == 'gov_office_queue':
            # Initial waiting scene - dialogue only
            pass

        elif phase_id == 'document_sorting':
            # Document sorting mini-game
            interactions = self.narrative_content['document_sorting']['interactions']
            if 'sort_documents' in interactions:
                self.add_interactive_object('sort_documents', interactions['sort_documents'])

        elif phase_id == 'paperwork_rejection':
            # Rejection scene - dialogue only
            pass

    def load_narrative_content(self):
        """Load the government office narrative content including police encounter"""
        return {
            # Police encounter phases (happen outside/at government office)
            'police_stop': {
                'npcs': [
                    {'name': 'Officer', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "Walking toward the government office. Tired. Worried."),
                    (None, "Red and blue lights flash behind you."),
                    (None, "Your heart stops."),
                    ("Officer", "Excuse me. Can I see some ID?"),
                    ("You", "(heart racing) Uh, sure... what's this about?"),
                    ("Officer", "Routine check. Just need to run your name."),
                    (None, "You hand over your ID with shaking hands."),
                    ("Officer", "(into radio) Running a check on..."),
                    (None, "Seconds feel like hours."),
                    ("Officer", "There's a warrant for your arrest."),
                    ("You", "I can explain—"),
                    ("Officer", "You missed your court date."),
                    ("You", "I had to work! I would have lost my job!"),
                    ("Officer", "That's not how the law works."),
                ],
                'interactions': {
                    'police_encounter': {
                        'position': (8, 5),
                        'prompt': 'Talk to officer',
                        'trigger_activity': 'police_encounter',
                        'required': True
                    }
                }
            },

            'stay_calm': {
                'npcs': [
                    {'name': 'Officer', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "Your hands are shaking. Your vision narrows."),
                    ("Officer", "I need you to stay calm."),
                    ("You", "(trying to breathe) I just... I had work..."),
                    ("Officer", "Take a breath. I'm not going to arrest you right now."),
                    (None, "Focus. Breathe. Don't make this worse."),
                ],
                'interactions': {
                    'breathing_exercise': {
                        'position': (8, 6),
                        'prompt': 'Practice breathing',
                        'trigger_activity': 'breathing_exercise',
                        'required': True
                    }
                }
            },

            'court_citation': {
                'npcs': [
                    {'name': 'Officer', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "Your breathing steadies. The panic recedes slightly."),
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
                    (None, "48 hours. Another impossible deadline."),
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
                    (None, "The government office is packed. Numbers being called out."),
                    (None, "Your ticket says 247. They're on 198."),
                    ("Other Person", "Been here since 7am. Don't expect to leave before noon."),
                    ("You", "But I have class later..."),
                    ("Other Person", "Welcome to the system, kid."),
                    (None, "Hours pass. The fluorescent lights hum overhead."),
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
                    ("Clerk", "I need you to sort these documents for processing."),
                    ("Clerk", "Legal documents on the left, personal records on the right."),
                    ("Clerk", "Make sure the court summons is in the legal pile."),
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
                    ("You", "What? Where? I signed everywhere..."),
                    ("Clerk", "Page 3, section B, subsection ii."),
                    ("You", "That section wasn't even on my form!"),
                    ("Clerk", "You'll need to come back with the correct form."),
                    ("Clerk", "We close in 30 minutes, so... tomorrow?"),
                    (None, "Another day lost to bureaucracy."),
                    ("You", "But I've been here all day!"),
                    ("Clerk", "Next in line please!"),
                    (None, "You still need to handle the court papers somehow."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        objective_displays = {
            # Police encounter objectives
            'police_stop': ("A police officer has stopped you", "Stay calm..."),
            'stay_calm': ("Stay calm during the encounter", "Focus on breathing"),
            'court_citation': ("Receive the court citation", "48 hours to appear"),
            # Government office objectives
            'gov_office_queue': ("Wait in the government office line", "Your number: 247"),
            'document_sorting': ("Sort the required documents", "Legal vs Personal"),
            'paperwork_rejection': ("Submit your paperwork", "Hope for approval"),
        }

        if current.id in objective_displays:
            current.dynamic_description = objective_displays[current.id][0]
            current.progress_text = objective_displays[current.id][1]

    def interact_with_object(self, name):
        """Handle government office interactions - uses UniversalActivityManager"""
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            if trigger == 'document_sorting':
                self._start_activity_via_manager('document_sorting')
                return
            elif trigger == 'police_encounter':
                self._start_activity_via_manager('police_stop')
                return
            elif trigger == 'breathing_exercise':
                self._start_activity_via_manager('stay_calm')
                return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            self.end_narrative_sequence()

    def on_activity_complete(self, activity, results):
        """Callback from UniversalActivityManager when activity completes"""
        print(f"[GOV_OFFICE_P3] on_activity_complete called with results: {results}")

        # Handle police encounter phases
        if self.current_objective_phase == 'police_stop':
            self.police_encounter_complete = True
            print("[GOV_OFFICE_P3] Police encounter complete")

        elif self.current_objective_phase == 'stay_calm':
            self.stayed_calm = True
            if results:
                stress_level = results.get('final_stress', 100)
                print(f"[GOV_OFFICE_P3] Breathing exercise complete, stress: {stress_level}")

        elif self.current_objective_phase == 'court_citation':
            self.citation_received = True

        # Handle document sorting
        elif self.current_objective_phase == 'document_sorting':
            if results:
                self.documents_sorted = results.get('completed', False)
                if results.get('found_critical_document'):
                    print("[GOV_OFFICE_P3] Critical document found!")
            else:
                # If no results, still mark as sorted
                self.documents_sorted = True

        # Check if objective is now complete and transition
        if self.check_objective_complete():
            print(f"[GOV_OFFICE_P3] Objective complete - calling end_narrative_sequence")
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

    def draw(self, screen):
        """Draw office interior with activity overlay - delegates to UniversalActivityManager"""
        # Check if activity manager has active activity
        activity_manager = self._get_activity_manager()
        if activity_manager and activity_manager.current_activity:
            current_activity = activity_manager.current_activity
            if current_activity.active and not getattr(current_activity, 'completed', False):
                activity_manager.draw(screen)
                return

        # Draw base interior
        super().draw(screen)

        # Add institutional atmosphere overlay for certain phases
        if self.current_objective_phase in ['gov_office_queue', 'paperwork_rejection']:
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 100, 80, 20))
            screen.blit(overlay, (0, 0))

    def end_narrative_sequence(self):
        """Handle government office transitions - Part 1 pattern"""
        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[GOV_OFFICE_P3] Completing objective: {current.id}")

        # Part 1 Pattern: Just set should_exit flag
        # Main game's complete_current_objective() handles advancement and re-entry
        print(f"[GOV_OFFICE_P3] Objective complete - setting should_exit = True")
        print(f"[GOV_OFFICE_P3]   Main game will handle advancement via complete_current_objective()")
        self.should_exit = True

        # Call complete_current_objective() to let main game handle transition
        self.game.objective_manager.complete_current_objective()

    def check_objective_complete(self):
        """Check if the current objective's requirements are met"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Police encounter phases
        if current.id == 'police_stop':
            return self.police_encounter_complete

        if current.id == 'stay_calm':
            return self.stayed_calm

        if current.id == 'court_citation':
            # Citation is dialogue only - complete when narrative ends
            return not self.narrative_active

        # Government office phases
        if current.id == 'document_sorting':
            return self.documents_sorted

        # Dialogue-only scenes complete when dialogue ends
        if current.id in ['gov_office_queue', 'paperwork_rejection']:
            return not self.narrative_active

        return True

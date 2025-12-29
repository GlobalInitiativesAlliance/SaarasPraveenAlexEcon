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

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

        # Activity cleanup flag
        self._activity_cleanup_pending = False

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
                self._cleanup_activity_state()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[GOV_OFFICE_P3]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[GOV_OFFICE_P3]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def _cleanup_activity_state(self):
        """Clean up any stale activity references - single cleanup point"""
        if hasattr(self.game, 'objective_manager'):
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = None
            self.game.objective_manager.current_activity = None
        self._activity_cleanup_pending = False
        print("[GOV_OFFICE_P3] Activity state cleaned up")

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'gov_office_queue':
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
        """Load the government office narrative content"""
        return {
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
                # Use UniversalActivityManager for consistent activity handling
                if hasattr(self.game.objective_manager, 'activity_manager'):
                    success = self.game.objective_manager.activity_manager.start_activity_for_objective('document_sorting')
                    if success:
                        print("[GOV_OFFICE_P3] Started document_sorting via UniversalActivityManager")
                        return
                    else:
                        print("[GOV_OFFICE_P3] Failed to start activity via manager, trying direct launch")
                        self._launch_document_sorting_fallback()
                        return
                else:
                    self._launch_document_sorting_fallback()
                    return

        super().interact_with_object(name)
        self.update_objective_display()

        if self.check_objective_complete():
            self.end_narrative_sequence()

    def _launch_document_sorting_fallback(self):
        """Fallback method to launch document sorting directly"""
        try:
            from part_3_legal_system.activities.document_sorting_legal import LegalDocumentSortingGame

            activity = LegalDocumentSortingGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            # Set via activity manager if available
            if hasattr(self.game.objective_manager, 'activity_manager'):
                self.game.objective_manager.activity_manager.current_activity = activity
            self.game.objective_manager.current_activity = activity

            print("[GOV_OFFICE_P3] Launched document sorting (fallback)")

        except Exception as e:
            print(f"[GOV_OFFICE_P3] Failed to launch activity: {e}")
            self._cleanup_activity_state()

    def handle_event(self, event):
        """Handle events with proper activity priority"""
        # Check if activity manager has active activity
        activity_manager = getattr(self.game.objective_manager, 'activity_manager', None)
        current_activity = None

        if activity_manager:
            current_activity = activity_manager.current_activity
        if not current_activity:
            current_activity = getattr(self.game.objective_manager, 'current_activity', None)

        # Activity events first
        if current_activity and current_activity.active:
            if activity_manager:
                activity_manager.handle_event(event)
            elif hasattr(current_activity, 'handle_event'):
                current_activity.handle_event(event)
            return

        super().handle_event(event)

    def update(self, dt):
        """Update with improved activity lifecycle management"""
        super().update(dt)

        # Check activity manager for completion
        activity_manager = getattr(self.game.objective_manager, 'activity_manager', None)
        current_activity = None

        if activity_manager:
            current_activity = activity_manager.current_activity

        if current_activity is not None:
            if current_activity.active:
                if activity_manager:
                    completed = activity_manager.update(dt)
                    if completed:
                        self._handle_activity_completion(current_activity)
            elif current_activity.completed or not current_activity.active:
                if not self._activity_cleanup_pending:
                    self._activity_cleanup_pending = True
                    self._handle_activity_completion(current_activity)

    def _handle_activity_completion(self, activity):
        """Handle activity completion"""
        if self.current_objective_phase == 'document_sorting':
            if hasattr(activity, 'get_results'):
                results = activity.get_results()
                self.documents_sorted = results.get('completed', False)
                if results.get('found_critical_document'):
                    print("[GOV_OFFICE_P3] Critical document found!")

        # Clean up
        self._cleanup_activity_state()

        # Check objective completion
        if self.check_objective_complete():
            self.end_narrative_sequence()

    def draw(self, screen):
        """Draw office interior with activity overlay"""
        # Check for active activity
        activity_manager = getattr(self.game.objective_manager, 'activity_manager', None)
        current_activity = None

        if activity_manager:
            current_activity = activity_manager.current_activity

        # Draw activity if active (takes full screen)
        if (current_activity and
            current_activity.active and
            not getattr(current_activity, 'completed', False)):
            if activity_manager:
                activity_manager.draw(screen)
            elif hasattr(current_activity, 'draw'):
                current_activity.draw(screen)
            return

        # Draw base interior
        super().draw(screen)

        # Add institutional atmosphere overlay for certain phases
        if self.current_objective_phase in ['gov_office_queue', 'paperwork_rejection']:
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 100, 80, 20))
            screen.blit(overlay, (0, 0))

    def end_narrative_sequence(self):
        """Handle government office transitions"""
        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if not self.check_objective_complete():
            return

        print(f"[GOV_OFFICE_P3] Completing objective: {current.id}")

        # Complete and transition - use advance_to_next_objective directly
        # to avoid activity manager trying to start an activity again
        self.should_exit = True
        self.game.objective_manager.advance_to_next_objective()

        # Check if next objective is also at this location
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            print(f"[GOV_OFFICE_P3] Next objective at same location, re-entering")
            self.should_exit = False
            self.enter()
        else:
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's requirements are met"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        if current.id == 'document_sorting':
            return self.documents_sorted

        # Dialogue-only scenes complete when dialogue ends
        if current.id in ['gov_office_queue', 'paperwork_rejection']:
            return not self.narrative_active

        return True

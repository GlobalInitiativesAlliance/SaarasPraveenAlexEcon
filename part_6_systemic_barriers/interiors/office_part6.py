"""
Government Office Interior for Part 6 - Systemic Barriers
Handles social services visits, document sorting, and benefits applications
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class OfficePart6(NarrativeInterior):
    """Government office with systemic barrier narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.document_sorting_completed = False
        self.dialogue_choice_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up office scene based on objective"""
        super().enter()

        print(f"[OFFICE_P6] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[OFFICE_P6]   current objective: {current.id if current else 'None'}")
        print(f"[OFFICE_P6]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[OFFICE_P6]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[OFFICE_P6]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[OFFICE_P6]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'social_services_start':
            # Initial office visit - approach front desk
            interactions = self.narrative_content.get('social_services_start', {}).get('interactions', {})
            if 'front_desk' in interactions:
                self.add_interactive_object('front_desk', interactions['front_desk'])

        elif phase_id == 'document_sorting':
            # Document sorting mini-game
            interactions = self.narrative_content.get('document_sorting', {}).get('interactions', {})
            if 'sorting_station' in interactions:
                self.add_interactive_object('sorting_station', interactions['sorting_station'])

        elif phase_id == 'incomplete_stamp':
            # Application rejected - dialogue only
            pass

        elif phase_id == 'wait_in_line':
            # Wait in line again - dialogue only
            pass

        elif phase_id == 'benefits_lobby':
            # Return visit - benefits lobby
            interactions = self.narrative_content.get('benefits_lobby', {}).get('interactions', {})
            if 'lobby_area' in interactions:
                self.add_interactive_object('lobby_area', interactions['lobby_area'])

        elif phase_id == 'dialogue_choice':
            # Dialogue choice mini-game
            interactions = self.narrative_content.get('dialogue_choice', {}).get('interactions', {})
            if 'clerk_window' in interactions:
                self.add_interactive_object('clerk_window', interactions['clerk_window'])

        elif phase_id == 'specific_request':
            # Success with specific language - dialogue only
            pass

    def load_narrative_content(self):
        """Load the office narrative content for Part 6"""
        return {
            'social_services_start': {
                'npcs': [
                    {'name': 'Security Guard', 'x': 6, 'y': 4},
                    {'name': 'Clerk', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You enter the Social Services Office."),
                    (None, "The fluorescent lights buzz overhead."),
                    (None, "A long line of people wait at the front desk."),
                    ("Security Guard", "Take a number and wait to be called."),
                    ("You", "I'm here about benefits... I'm not sure which ones."),
                    ("Security Guard", "Fill out the intake form first. Have a seat."),
                    (None, "You receive a thick stack of forms."),
                ],
                'interactions': {
                    'front_desk': {
                        'position': (10, 4),
                        'prompt': 'Approach the front desk',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'document_sorting': {
                'npcs': [
                    {'name': 'Clerk', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Clerk", "I need you to sort these documents."),
                    ("Clerk", "Put required documents on one side, optional on the other."),
                    (None, "You have 45 seconds before the system times out."),
                    ("You", "Okay, I think I understand..."),
                ],
                'interactions': {
                    'sorting_station': {
                        'position': (8, 6),
                        'prompt': 'Sort the documents',
                        'trigger_activity': 'document_sorting',
                        'required': True
                    }
                }
            },

            'incomplete_stamp': {
                'npcs': [
                    {'name': 'Clerk', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "The clerk reviews your sorted documents."),
                    ("Clerk", "Hmm... let me check these."),
                    (None, "She stamps your application."),
                    (None, "INCOMPLETE"),
                    ("You", "But I sorted everything correctly!"),
                    ("Clerk", "You're missing Form 4B-7."),
                    ("You", "No one told me about that form..."),
                    ("Clerk", "It's listed on our website. Next!"),
                ],
                'interactions': {}
            },

            'wait_in_line': {
                'npcs': [
                    {'name': 'Clerk', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You get back in line with the missing form."),
                    (None, "Two hours pass."),
                    ("Clerk", "Oh, you also missed a signature on page 3."),
                    ("You", "Can I sign it now?"),
                    ("Clerk", "No, it needs to be notarized. Come back tomorrow."),
                    (None, "The office closes in 10 minutes."),
                    ("You", "But I've been here all day..."),
                    ("Clerk", "I'm sorry, those are the rules. Next!"),
                ],
                'interactions': {}
            },

            'benefits_lobby': {
                'npcs': [
                    {'name': 'Waiting Person 1', 'x': 4, 'y': 6},
                    {'name': 'Waiting Person 2', 'x': 6, 'y': 8}
                ],
                'dialogue_sequence': [
                    (None, "You return to the Benefits Office."),
                    (None, "The same tired faces fill the waiting room."),
                    ("Waiting Person 1", "Been here since 7am. Still waiting."),
                    ("Waiting Person 2", "Third time this month. They keep losing my paperwork."),
                    ("You", "Does it ever get easier?"),
                    ("Waiting Person 1", "Only if you know the magic words."),
                    ("You", "Magic words?"),
                    ("Waiting Person 2", "The specific programs. The law numbers."),
                    ("Waiting Person 2", "Otherwise they just give you the runaround."),
                ],
                'interactions': {
                    'lobby_area': {
                        'position': (5, 7),
                        'prompt': 'Talk to people waiting',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'dialogue_choice': {
                'npcs': [
                    {'name': 'Clerk', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "Your number is finally called."),
                    ("Clerk", "How can I help you today?"),
                    (None, "How you phrase your request matters..."),
                ],
                'interactions': {
                    'clerk_window': {
                        'position': (10, 4),
                        'prompt': 'Speak to the clerk',
                        'trigger_activity': 'dialogue_choice',
                        'required': True
                    }
                }
            },

            'specific_request': {
                'npcs': [
                    {'name': 'Specialized Worker', 'x': 12, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Clerk", "Oh, you're a former foster youth?"),
                    ("Clerk", "Let me get you to our specialized worker."),
                    ("Specialized Worker", "Hi! I handle former foster youth cases."),
                    ("Specialized Worker", "We have expedited processing for you."),
                    ("You", "Really? Why didn't anyone tell me before?"),
                    ("Specialized Worker", "Unfortunately, you have to know to ask."),
                    ("Specialized Worker", "The system doesn't advertise these programs."),
                    (None, "You finally make progress... but wonder how many don't."),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'social_services_start':
            current.dynamic_description = "Enter Social Services Office"
            current.progress_text = "Take a number and wait"

        elif current.id == 'document_sorting':
            if self.document_sorting_completed:
                current.dynamic_description = "Documents sorted!"
            else:
                current.dynamic_description = "Sort the documents"
                current.progress_text = "Required vs Optional"

        elif current.id == 'dialogue_choice':
            if self.dialogue_choice_completed:
                current.dynamic_description = "Request made!"
            else:
                current.dynamic_description = "Speak to the clerk"
                current.progress_text = "Choose your words carefully"

    def interact_with_object(self, name):
        """Handle interactions for Part 6 office"""
        print(f"[OFFICE_P6] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            # Mark interaction as completed
            self.completed_interactions.add(name)

            if trigger == 'document_sorting':
                self.launch_document_sorting_game()
                return

            if trigger == 'dialogue_choice':
                self.launch_dialogue_choice()
                return
        else:
            # Mark interaction as completed for non-activity interactions
            self.completed_interactions.add(name)

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[OFFICE_P6] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_document_sorting_game(self):
        """Launch the document sorting mini-game"""
        from part_6_systemic_barriers.activities.document_sorting_game import DocumentSortingGame

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[OFFICE_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = DocumentSortingGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[OFFICE_P6] Document sorting game launched")

    def launch_dialogue_choice(self):
        """Launch the dialogue choice system"""
        from part_6_systemic_barriers.activities.choice_dialogue import ChoiceDialogueSystem

        # Don't launch if activity already running
        if self.current_activity and self.current_activity.active:
            print("[OFFICE_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialogueSystem(self.game.objective_manager)
            activity.set_scenario_by_id('dialogue_choice')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[OFFICE_P6] Dialogue choice launched")

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                if hasattr(self.current_activity, 'handle_key'):
                    self.current_activity.handle_key(event.key)
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_event'):
                    self.current_activity.handle_event(event)
            return

        # Use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Auto-launch document sorting for document_sorting phase
        if (self.current_objective_phase == 'document_sorting' and
            not self.narrative_active and
            self.current_activity is None and
            not self.document_sorting_completed):
            self.launch_document_sorting_game()

        # Auto-launch dialogue choice for dialogue_choice phase
        if (self.current_objective_phase == 'dialogue_choice' and
            not self.narrative_active and
            self.current_activity is None and
            not self.dialogue_choice_completed):
            self.launch_dialogue_choice()

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[OFFICE_P6] Activity completed/inactive - cleaning up")

                # Handle completion based on activity TYPE (not phase)
                from part_6_systemic_barriers.activities.document_sorting_game import DocumentSortingGame
                from part_6_systemic_barriers.activities.choice_dialogue import ChoiceDialogueSystem

                if isinstance(self.current_activity, DocumentSortingGame):
                    self.document_sorting_completed = True
                    print(f"[OFFICE_P6] Document sorting marked complete")
                elif isinstance(self.current_activity, ChoiceDialogueSystem):
                    self.dialogue_choice_completed = True
                    print(f"[OFFICE_P6] Dialogue choice marked complete")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[OFFICE_P6] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[OFFICE_P6] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw office interior with activity overlay"""
        # Draw activity ONLY if it's truly active
        if (self.current_activity is not None and
            self.current_activity.active and
            not getattr(self.current_activity, 'completed', False)):
            if hasattr(self.current_activity, 'render'):
                self.current_activity.render(screen)
            elif hasattr(self.current_activity, 'draw'):
                self.current_activity.draw(screen)
            return

        # Draw base interior
        super().draw(screen)

    def end_narrative_sequence(self):
        """Override to properly handle office transitions"""
        print(f"[OFFICE_P6] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[OFFICE_P6]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[OFFICE_P6] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[OFFICE_P6] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this office
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in office, reinitialize for next phase
            print(f"[OFFICE_P6] Next objective also at office: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            # Exit office
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'document_sorting':
            print(f"[OFFICE_P6] check_objective_complete: document_sorting_completed={self.document_sorting_completed}")
            return self.document_sorting_completed

        if current.id == 'dialogue_choice':
            print(f"[OFFICE_P6] check_objective_complete: dialogue_choice_completed={self.dialogue_choice_completed}")
            return self.dialogue_choice_completed

        # For interaction-based objectives
        if current.id == 'social_services_start':
            return 'front_desk' in self.completed_interactions

        if current.id == 'benefits_lobby':
            return 'lobby_area' in self.completed_interactions

        # For dialogue-only objectives, complete after dialogue ends
        if current.id in ['incomplete_stamp', 'wait_in_line', 'specific_request']:
            return not self.narrative_active

        return True

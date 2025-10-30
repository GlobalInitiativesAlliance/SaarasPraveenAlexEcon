"""
Housing Office Interior with TLP Application Process
Handles the bureaucratic nightmare of applying for transitional housing
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class HousingOfficeNarrative(NarrativeInterior):
    """Housing services office with TLP application narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track application progress
        self.tlp_explained = False
        self.application_started = False
        self.application_submitted = False
        self.waitlist_position = 47
        self.months_waited = 0
        self.current_activity = None

        # Exit timer for auto-transitions
        self.should_exit = False
        self.exit_timer = 0

        # Office atmosphere
        self.waiting_count = 8  # Other people waiting
        self.frustration_level = 0
        self.hope_meter = 100

    def enter(self):
        """Override enter to set up housing office scene"""
        super().enter()

        # Check which objective we're on
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'learn_about_tlp':
                # Add case worker desk for TLP explanation
                interactions = self.narrative_content['learn_about_tlp']['interactions']
                if 'case_worker_desk' in interactions:
                    self.add_interactive_object('case_worker_desk', interactions['case_worker_desk'])
                    if 'case_worker_desk' in self.completed_interactions:
                        self.completed_interactions.remove('case_worker_desk')

            elif current.id == 'tlp_paperwork':
                # Add application computer station
                interactions = self.narrative_content['tlp_paperwork']['interactions']
                if 'application_computer' in interactions:
                    self.add_interactive_object('application_computer', interactions['application_computer'])

            elif current.id == 'waitlist_47':
                # Add waitlist board
                interactions = self.narrative_content['waitlist_47']['interactions']
                if 'waitlist_board' in interactions:
                    self.add_interactive_object('waitlist_board', interactions['waitlist_board'])

        self.update_objective_display()

    def load_narrative_content(self):
        """Load the housing office narrative content"""
        return {
            'learn_about_tlp': {
                'npcs': [
                    {'name': 'Case Worker Sarah', 'x': 8, 'y': 3},
                    {'name': 'Waiting Youth 1', 'x': 4, 'y': 7},
                    {'name': 'Waiting Youth 2', 'x': 12, 'y': 7},
                    {'name': 'Receptionist', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "The housing office is packed. The air smells of desperation and cheap coffee."),
                    ("Receptionist", "Take a number. Current wait time: 2-3 hours."),
                    ("Waiting Youth 1", "I've been here since 8am. It's now 2pm."),
                    ("You", "I just aged out of foster care. I need help finding housing."),
                    ("Receptionist", "Talk to Sarah when your number is called. She handles youth programs."),
                    (None, "After 2.5 hours, your number is finally called.")
                ],
                'interactions': {
                    'case_worker_desk': {
                        'position': (8, 3),
                        'prompt': 'Talk to Case Worker',
                        'dialogue': [
                            "Sarah: You aged out? I'm sorry. Let me tell you about TLP.",
                            "Sarah: Transitional Living Program. 18-24 months of subsidized housing.",
                            "You: That sounds perfect! Can I move in today?",
                            "Sarah: *laughs bitterly* Oh honey, no. There's a waitlist.",
                            "Sarah: Currently about 6-8 months wait. Maybe longer.",
                            "You: But I need housing NOW. Where do I sleep tonight?",
                            "Sarah: Emergency shelter if they have space. Most don't.",
                            "Sarah: Start the application anyway. The sooner you apply, the sooner you get housed.",
                            "You: *trying not to cry* Okay. What do I need to do?"
                        ],
                        'required': True
                    }
                }
            },

            'tlp_paperwork': {
                'npcs': [
                    {'name': 'Case Worker Sarah', 'x': 8, 'y': 3},
                    {'name': 'Frustrated Applicant', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Case Worker Sarah", "Here's the application. It's... comprehensive."),
                    ("You", "50 pages?! This is like applying to college."),
                    ("Case Worker Sarah", "Actually, it's harder. You need more documentation."),
                    ("Frustrated Applicant", "I've been working on mine for two weeks. Still missing documents."),
                    (None, "You sit at the computer. The form loads. Your heart sinks.")
                ],
                'interactions': {
                    'application_computer': {
                        'position': (10, 6),
                        'prompt': 'Start application',
                        'trigger_activity': 'tlp_application',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'waitlist_47': {
                'npcs': [
                    {'name': 'Case Worker Sarah', 'x': 8, 'y': 3}
                ],
                'dialogue_sequence': [
                    (None, "Three weeks later. You return to check your application status."),
                    ("Case Worker Sarah", "Let me pull up your file... Okay, you're approved for the waitlist!"),
                    ("You", "Waitlist? What number am I?"),
                    ("Case Worker Sarah", "You're number 47."),
                    ("You", "FORTY-SEVEN?! How long will that take?"),
                    ("Case Worker Sarah", "At current pace... 6 to 8 months. Maybe longer."),
                    ("You", "Where do I live for 6-8 months?!"),
                    ("Case Worker Sarah", "That's... that's the hard part. I'm sorry."),
                    (None, "You stare at the waitlist board. 47 people ahead of you. 47 lifetimes.")
                ],
                'interactions': {
                    'waitlist_board': {
                        'position': (4, 4),
                        'prompt': 'Check waitlist',
                        'trigger_activity': 'waitlist_tracker',
                        'dialogue': None,
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on housing office progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'learn_about_tlp':
            if self.narrative_active and self.sequence_index < 5:
                current.dynamic_description = f"Waiting... {self.waiting_count} people ahead"
            else:
                current.dynamic_description = "Learn about Transitional Living Program"
                current.progress_text = "Talk to case worker"

        elif current.id == 'tlp_paperwork':
            if not self.application_started:
                current.dynamic_description = "50-page application awaits"
                current.progress_text = "This will take hours..."
            else:
                current.dynamic_description = "Filling out endless forms"
                current.progress_text = f"Hope remaining: {self.hope_meter}%"

        elif current.id == 'waitlist_47':
            current.dynamic_description = f"Waitlist Position: #{self.waitlist_position}"
            current.progress_text = "6-8 months if you're lucky"

    def interact_with_object(self, name):
        """Handle interactions with special handling for activities"""
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'learn_about_tlp'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            if trigger == 'tlp_application':
                print("DEBUG: Launching TLP application")
                self.launch_tlp_application()
                return
            elif trigger == 'waitlist_tracker':
                print("DEBUG: Launching waitlist tracker")
                self.launch_waitlist_tracker()
                return

        # Handle non-activity interactions
        super().interact_with_object(name)

        self.update_objective_display()

    def launch_tlp_application(self):
        """Launch the TLP application activity"""
        from src.activities.tlp_application import TLPApplication

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = TLPApplication(self.game)
        activity.narrative_ref = self
        activity.start()
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity

    def launch_waitlist_tracker(self):
        """Launch the waitlist tracker activity"""
        from src.activities.waitlist_tracker import WaitlistTracker

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = WaitlistTracker(self.game)
        activity.narrative_ref = self
        activity.start()
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            return

        # Use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                current = self.game.objective_manager.get_current_objective()

                # Handle different activity completions
                if current and current.id == 'tlp_paperwork':
                    # Application completed
                    self.application_submitted = True
                    self.update_objective_display()
                    self.dialogue_box.show("Case Worker Sarah", "Application received. Now we wait...")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                elif current and current.id == 'waitlist_47':
                    # Waitlist tracking completed
                    self.months_waited = 6
                    self.update_objective_display()
                    self.dialogue_box.show(None, "6 months of hell. But finally... a call.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Complete objective
                self.game.objective_manager.complete_current_objective()

                # Exit the interior
                self.active = False

    def draw(self, screen):
        """Draw with activity overlay"""
        # Draw base interior
        super().draw(screen)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            self.current_activity.draw(screen)

        # Draw waiting room atmosphere
        if self.game.objective_manager.get_current_objective():
            current = self.game.objective_manager.get_current_objective()
            if current.id == 'learn_about_tlp' and not self.narrative_active:
                # Show waiting room stress
                font = pygame.font.Font(None, 24)
                wait_text = font.render(f"Others waiting: {self.waiting_count}", True, (200, 180, 160))
                screen.blit(wait_text, (50, 100))
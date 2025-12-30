"""
Apartment Interior for Part 6 - Systemic Barriers
Handles home-based interactions: mail, online applications, phone calls, aging out
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior


class ApartmentPart6(NarrativeInterior):
    """Apartment with systemic barrier narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.application_quiz_completed = False
        self.online_application_completed = False
        self.phone_maze_completed = False
        self.expired_documents_completed = False
        self.workshop_conflict_completed = False

        # Current activity tracking
        self.current_activity = None

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up apartment scene based on objective"""
        super().enter()

        print(f"[APT_P6] enter() called")

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P6]   current objective: {current.id if current else 'None'}")
        print(f"[APT_P6]   previous phase: {self.current_objective_phase}")

        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                print(f"[APT_P6]   Phase changed! Clearing old state")
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                print(f"[APT_P6]   Initializing phase: {current.id}")
                self.initialize_phase(current.id)
                self.phase_initialized = True
                print(f"[APT_P6]   Interactive objects: {list(self.interactive_objects.keys())}")

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'food_assistance_mail':
            interactions = self.narrative_content.get('food_assistance_mail', {}).get('interactions', {})
            if 'mailbox' in interactions:
                self.add_interactive_object('mailbox', interactions['mailbox'])

        elif phase_id == 'application_quiz':
            interactions = self.narrative_content.get('application_quiz', {}).get('interactions', {})
            if 'laptop' in interactions:
                self.add_interactive_object('laptop', interactions['laptop'])

        elif phase_id == 'online_application':
            interactions = self.narrative_content.get('online_application', {}).get('interactions', {})
            if 'laptop' in interactions:
                self.add_interactive_object('laptop', interactions['laptop'])

        elif phase_id == 'phone_maze':
            interactions = self.narrative_content.get('phone_maze', {}).get('interactions', {})
            if 'phone' in interactions:
                self.add_interactive_object('phone', interactions['phone'])

        elif phase_id == 'expired_documents':
            interactions = self.narrative_content.get('expired_documents', {}).get('interactions', {})
            if 'documents' in interactions:
                self.add_interactive_object('documents', interactions['documents'])

        elif phase_id == 'workshop_conflict':
            interactions = self.narrative_content.get('workshop_conflict', {}).get('interactions', {})
            if 'calendar' in interactions:
                self.add_interactive_object('calendar', interactions['calendar'])

        # Dialogue-only phases don't need interactions
        # peer_advice, hunger_drop, age_out_notice, aged_out_rejection
        # ilp_call, research_programs, workshop_notice, systemic_reflection

    def load_narrative_content(self):
        """Load the apartment narrative content for Part 6"""
        return {
            'food_assistance_mail': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You check your mailbox."),
                    (None, "Among the bills, there's an official-looking letter."),
                    (None, "'You may qualify for CalFresh food assistance.'"),
                    ("You", "This could really help with groceries..."),
                    (None, "But the instructions are confusing."),
                    (None, "'Apply online, by phone, or in person.'"),
                    ("You", "Which way is fastest?"),
                ],
                'interactions': {
                    'mailbox': {
                        'position': (4, 8),
                        'prompt': 'Check the mail',
                        'trigger_activity': None,
                        'required': True
                    }
                }
            },

            'application_quiz': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit down to figure out how to apply."),
                    (None, "The letter doesn't make it clear."),
                    ("You", "Let me think about this..."),
                ],
                'interactions': {
                    'laptop': {
                        'position': (8, 6),
                        'prompt': 'Research how to apply',
                        'trigger_activity': 'application_quiz',
                        'required': True
                    }
                }
            },

            'online_application': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You decide to try applying online."),
                    (None, "The official benefits website loads slowly."),
                    ("You", "Come on, come on..."),
                ],
                'interactions': {
                    'laptop': {
                        'position': (8, 6),
                        'prompt': 'Start online application',
                        'trigger_activity': 'online_application',
                        'required': True
                    }
                }
            },

            'phone_maze': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "After the website crashed, you try calling instead."),
                    (None, "You dial the benefits hotline."),
                    ("Automated Voice", "Welcome to California Benefits..."),
                    ("You", "Please let me talk to a person..."),
                ],
                'interactions': {
                    'phone': {
                        'position': (10, 6),
                        'prompt': 'Call the benefits hotline',
                        'trigger_activity': 'phone_maze',
                        'required': True
                    }
                }
            },

            'peer_advice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You text a friend who went through the system."),
                    ("Friend", "The official channels are broken on purpose."),
                    ("Friend", "Try GetCalFresh.org instead."),
                    ("Friend", "And if you go in person, mention you're former foster youth."),
                    ("You", "Why does that matter?"),
                    ("Friend", "There are special programs. They just don't tell you about them."),
                    ("Friend", "You have to know to ask."),
                    (None, "Hidden knowledge. The system rewards those who already know it."),
                ],
                'interactions': {}
            },

            'hunger_drop': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Days pass. Your food assistance still hasn't come through."),
                    (None, "Your hunger meter has dropped."),
                    ("You", "I've been eating ramen for a week..."),
                    (None, "The system that's supposed to help is making things worse."),
                    (None, "You're burning energy just trying to access help."),
                ],
                'interactions': {}
            },

            'age_out_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "TIME PASSES..."),
                    (None, "You receive an official notice."),
                    (None, "'Your Medi-Cal coverage will end when you turn 21.'"),
                    ("You", "Wait, what? I thought I had until 26?"),
                    (None, "The fine print: 'Extended coverage requires re-enrollment.'"),
                    (None, "Nobody told you about the paperwork deadline."),
                ],
                'interactions': {}
            },

            'expired_documents': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You try to re-enroll for Medi-Cal."),
                    (None, "But your foster care verification has expired."),
                    (None, "Your old caseworker's number is disconnected."),
                    ("You", "How am I supposed to prove something from years ago?"),
                ],
                'interactions': {
                    'documents': {
                        'position': (6, 6),
                        'prompt': 'Gather your documents',
                        'trigger_activity': 'expired_documents',
                        'required': True
                    }
                }
            },

            'aged_out_rejection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your application is denied."),
                    (None, "'Reason: Unable to verify foster care status.'"),
                    (None, "'Reason: Documentation expired.'"),
                    ("You", "But I WAS in foster care! For years!"),
                    (None, "The system has no memory. You have to prove it all over again."),
                    (None, "Every. Single. Time."),
                ],
                'interactions': {}
            },

            'ilp_call': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You try calling your old ILP office."),
                    ("ILP Worker", "I'm sorry, but you've aged out of our services."),
                    ("You", "But I still need help!"),
                    ("ILP Worker", "Our program only serves youth up to age 21."),
                    ("ILP Worker", "You're 21 and 3 months. I can't help you."),
                    ("You", "Where am I supposed to go?"),
                    ("ILP Worker", "Try 211 or general social services."),
                    (None, "The safety net has holes. You just fell through one."),
                ],
                'interactions': {}
            },

            'research_programs': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You spend hours researching online."),
                    (None, "Finally, you find something."),
                    (None, "'Former Foster Youth Program - Extended Benefits'"),
                    ("You", "This is what I need! Why didn't anyone tell me?"),
                    (None, "The program exists. But it's buried on page 47 of a PDF."),
                    (None, "You have to know it exists to search for it."),
                ],
                'interactions': {}
            },

            'workshop_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You receive a notice."),
                    (None, "'MANDATORY: Benefits Workshop - Tuesday 3pm'"),
                    (None, "'Failure to attend will result in benefit suspension.'"),
                    ("You", "But I work Tuesday afternoons!"),
                    (None, "You check your work schedule. Shift: 2pm - 10pm."),
                    (None, "There's no way to do both."),
                ],
                'interactions': {}
            },

            'workshop_conflict': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at your calendar."),
                    (None, "Workshop: Tuesday 3pm. Benefits depend on it."),
                    (None, "Work: Tuesday 2pm. Income depends on it."),
                    ("You", "There has to be a way to fix this..."),
                ],
                'interactions': {
                    'calendar': {
                        'position': (8, 4),
                        'prompt': 'Consider your options',
                        'trigger_activity': 'workshop_conflict',
                        'required': True
                    }
                }
            },

            'systemic_reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit in your apartment, exhausted."),
                    (None, "It wasn't one big failure."),
                    (None, "It was a thousand small barriers."),
                    ("You", "Websites that crash. Phones that never connect."),
                    ("You", "Forms that require forms that require other forms."),
                    ("You", "Schedules that assume you don't have a job."),
                    (None, "The system isn't broken."),
                    (None, "It's working exactly as designed."),
                    (None, "To make it hard. To make you give up."),
                    (None, "But you haven't. Not yet."),
                    (None, "Part 6 Complete - Systemic Barriers"),
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'online_application':
            if self.online_application_completed:
                current.dynamic_description = "Website crashed!"
            else:
                current.dynamic_description = "Apply online"
                current.progress_text = "Fill out the form"

        elif current.id == 'phone_maze':
            if self.phone_maze_completed:
                current.dynamic_description = "Call disconnected!"
            else:
                current.dynamic_description = "Call benefits hotline"
                current.progress_text = "Navigate the phone system"

        elif current.id == 'workshop_conflict':
            if self.workshop_conflict_completed:
                current.dynamic_description = "Decision made"
            else:
                current.dynamic_description = "Make an impossible choice"
                current.progress_text = "Work vs Benefits"

    def interact_with_object(self, name):
        """Handle interactions for Part 6 apartment"""
        print(f"[APT_P6] Interacting with: {name}")

        # Check if this interaction triggers an activity
        current_content = self.narrative_content.get(self.current_objective_phase, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]
            trigger = interaction.get('trigger_activity')

            # Mark interaction as completed
            self.completed_interactions.add(name)

            if trigger == 'application_quiz':
                self.launch_application_quiz()
                return

            if trigger == 'online_application':
                self.launch_online_application()
                return

            if trigger == 'phone_maze':
                self.launch_phone_maze()
                return

            if trigger == 'expired_documents':
                self.launch_expired_documents()
                return

            if trigger == 'workshop_conflict':
                self.launch_workshop_conflict()
                return
        else:
            # Mark interaction as completed for non-activity interactions
            self.completed_interactions.add(name)

        # Otherwise use parent's interaction handling
        super().interact_with_object(name)
        self.update_objective_display()

        # Check if objective is now complete
        if self.check_objective_complete():
            print(f"[APT_P6] Phase complete, transitioning...")
            self.end_narrative_sequence()

    def launch_application_quiz(self):
        """Launch the application knowledge quiz"""
        from part_6_systemic_barriers.activities.choice_dialogue import ChoiceDialogueSystem

        if self.current_activity and self.current_activity.active:
            print("[APT_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialogueSystem(self.game.objective_manager)
            activity.set_scenario_by_id('application_quiz')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P6] Application quiz launched")

    def launch_online_application(self):
        """Launch the online application crash game"""
        from part_6_systemic_barriers.activities.online_application import OnlineApplicationGame

        if self.current_activity and self.current_activity.active:
            print("[APT_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = OnlineApplicationGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P6] Online application launched")

    def launch_phone_maze(self):
        """Launch the phone maze game"""
        from part_6_systemic_barriers.activities.phone_maze import PhoneMazeGame

        if self.current_activity and self.current_activity.active:
            print("[APT_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = PhoneMazeGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P6] Phone maze launched")

    def launch_expired_documents(self):
        """Launch the expired documents activity (reuse document sorting)"""
        from part_6_systemic_barriers.activities.document_sorting_game import DocumentSortingGame

        if self.current_activity and self.current_activity.active:
            print("[APT_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = DocumentSortingGame(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P6] Expired documents (sorting) launched")

    def launch_workshop_conflict(self):
        """Launch the workshop conflict choice"""
        from part_6_systemic_barriers.activities.choice_dialogue import ChoiceDialogueSystem

        if self.current_activity and self.current_activity.active:
            print("[APT_P6] Activity already running, skipping launch")
            return

        if hasattr(self.game, 'objective_manager'):
            activity = ChoiceDialogueSystem(self.game.objective_manager)
            activity.set_scenario_by_id('workshop_conflict')
            activity.narrative_ref = self
            activity.start()

            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
            print(f"[APT_P6] Workshop conflict choice launched")

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

        # Auto-launch activities for their respective phases
        if (self.current_objective_phase == 'application_quiz' and
            not self.narrative_active and
            self.current_activity is None and
            not self.application_quiz_completed):
            self.launch_application_quiz()

        if (self.current_objective_phase == 'online_application' and
            not self.narrative_active and
            self.current_activity is None and
            not self.online_application_completed):
            self.launch_online_application()

        if (self.current_objective_phase == 'phone_maze' and
            not self.narrative_active and
            self.current_activity is None and
            not self.phone_maze_completed):
            self.launch_phone_maze()

        if (self.current_objective_phase == 'expired_documents' and
            not self.narrative_active and
            self.current_activity is None and
            not self.expired_documents_completed):
            self.launch_expired_documents()

        if (self.current_objective_phase == 'workshop_conflict' and
            not self.narrative_active and
            self.current_activity is None and
            not self.workshop_conflict_completed):
            self.launch_workshop_conflict()

        # Update current activity if active
        if self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed or not self.current_activity.active:
                print(f"[APT_P6] Activity completed/inactive - cleaning up")

                # Handle completion based on activity TYPE (not phase)
                from part_6_systemic_barriers.activities.online_application import OnlineApplicationGame
                from part_6_systemic_barriers.activities.phone_maze import PhoneMazeGame
                from part_6_systemic_barriers.activities.document_sorting_game import DocumentSortingGame
                from part_6_systemic_barriers.activities.choice_dialogue import ChoiceDialogueSystem

                if isinstance(self.current_activity, OnlineApplicationGame):
                    self.online_application_completed = True
                    print(f"[APT_P6] Online application marked complete")
                elif isinstance(self.current_activity, PhoneMazeGame):
                    self.phone_maze_completed = True
                    print(f"[APT_P6] Phone maze marked complete")
                elif isinstance(self.current_activity, DocumentSortingGame):
                    self.expired_documents_completed = True
                    print(f"[APT_P6] Expired documents marked complete")
                elif isinstance(self.current_activity, ChoiceDialogueSystem):
                    # Check which scenario was active
                    if self.current_objective_phase == 'application_quiz':
                        self.application_quiz_completed = True
                        print(f"[APT_P6] Application quiz marked complete")
                    elif self.current_objective_phase == 'workshop_conflict':
                        self.workshop_conflict_completed = True
                        print(f"[APT_P6] Workshop conflict marked complete")

                # Clear ALL activity references
                self.current_activity = None
                self.game.objective_manager.current_activity = None
                print(f"[APT_P6] All activities cleared")

                # Check if objective is now complete and transition
                if self.check_objective_complete():
                    print(f"[APT_P6] Objective complete - calling end_narrative_sequence")
                    self.end_narrative_sequence()
                return

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                self.active = False

    def draw(self, screen):
        """Draw apartment interior with activity overlay"""
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
        """Override to properly handle apartment transitions"""
        print(f"[APT_P6] end_narrative_sequence() called")

        self.narrative_active = False
        self.dialogue_box.hide()

        current = self.game.objective_manager.get_current_objective()
        print(f"[APT_P6]   current objective: {current.id if current else 'None'}")

        if not current:
            return

        # Only transition when the objective is actually complete
        if not self.check_objective_complete():
            print(f"[APT_P6] Objective not complete yet - waiting")
            return

        # Complete and transition based on phase
        print(f"[APT_P6] Completing {current.id}")
        self.should_exit = True
        self.game.objective_manager.complete_current_objective()

        # Check if next objective is also at this apartment
        next_obj = self.game.objective_manager.get_current_objective()
        if next_obj and next_obj.target_position == self.building_pos:
            # Stay in apartment, reinitialize for next phase
            print(f"[APT_P6] Next objective also at apartment: {next_obj.id}")
            self.should_exit = False
            self.enter()
        else:
            # Exit apartment
            self.active = False

    def check_objective_complete(self):
        """Check if the current objective's required interactions are complete"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return True

        # Special handling for activity-based objectives
        if current.id == 'application_quiz':
            return self.application_quiz_completed

        if current.id == 'online_application':
            return self.online_application_completed

        if current.id == 'phone_maze':
            return self.phone_maze_completed

        if current.id == 'expired_documents':
            return self.expired_documents_completed

        if current.id == 'workshop_conflict':
            return self.workshop_conflict_completed

        # For interaction-based objectives
        if current.id == 'food_assistance_mail':
            return 'mailbox' in self.completed_interactions

        # For dialogue-only objectives, complete after dialogue ends
        dialogue_only = [
            'peer_advice', 'hunger_drop', 'age_out_notice',
            'aged_out_rejection', 'ilp_call', 'research_programs',
            'workshop_notice', 'systemic_reflection'
        ]
        if current.id in dialogue_only:
            return not self.narrative_active

        return True

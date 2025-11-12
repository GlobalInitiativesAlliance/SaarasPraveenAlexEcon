"""
Rental Office Interior with Housing Application Narrative
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class RentalOfficeNarrative(NarrativeInterior):
    """Rental office with harsh reality of housing barriers"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track interaction progress
        self.reality_checks_completed = set()
        self.required_checks = {'wallet_check', 'phone_check', 'application_form'}
        self.phone_call_triggered = False

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective we're on
        self.current_objective_phase = None

        # Dialogue sequence handling
        self.pending_dialogue = []
        self.current_dialogue_index = 0

        # Auto-reload prevention
        self.is_reloading = False

    def enter(self):
        """Override enter to set up rental office scene"""
        super().enter()

        # Reset reload flag
        self.is_reloading = False

        # Reset interaction state for new objective
        if hasattr(self, 'current_objective_phase'):
            old_phase = self.current_objective_phase
        else:
            old_phase = None

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        if current:
            self.current_objective_phase = current.id

            # Clear state if objective changed
            if old_phase != current.id:
                self.reality_checks_completed = set()
                self.phone_call_triggered = False
                # Clear previous interactions
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Add interactions based on objective
            if current.id == 'your_reality':
                # Add reality check interactions immediately
                interactions = self.narrative_content['your_reality']['interactions']
                for obj_name in ['wallet_check', 'phone_check', 'application_form']:
                    if obj_name in interactions:
                        self.add_interactive_object(obj_name, interactions[obj_name])

            elif current.id == 'call_foster_parents':
                # Add phone interaction for calling
                if 'phone_call' in self.narrative_content['call_foster_parents']['interactions']:
                    phone_data = self.narrative_content['call_foster_parents']['interactions']['phone_call']
                    self.add_interactive_object('phone_call', phone_data)

        self.update_objective_display()

    def load_narrative_content(self):
        """Load the rental office narrative content"""
        return {
            # First visit - checking the listing
            'found_listing': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 4},
                    {'name': 'Well-Dressed Applicant', 'x': 5, 'y': 6},
                    {'name': 'Security Guard', 'x': 12, 'y': 10}
                ],
                'dialogue_sequence': [
                    (None, "The rental office is pristine. Marble floors, modern furniture, success posters."),
                    (None, "Everything here whispers 'you don't belong.'"),
                    ("Leasing Agent", "Next! What can I help you with?"),
                    ("You", "Hi, I saw your listing online for the $1,400 studio apartment..."),
                    ("Leasing Agent", "Oh, that one. Very popular unit. Cheapest we have."),
                    ("Leasing Agent", "Do you have your application packet ready?"),
                    ("You", "Application packet? I... I just wanted to see if it's still available."),
                    ("Leasing Agent", "*sighs heavily* First time renting? Let me explain the requirements."),
                    (None, "The agent pulls out a thick folder and starts flipping through pages."),
                    (None, "Your stomach sinks with each page turn.")
                ],
                'interactions': {}
            },

            # Learning about barriers
            'application_barriers': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 4},
                    {'name': 'Well-Dressed Applicant', 'x': 5, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Leasing Agent", "Income requirement: You must earn three times the monthly rent."),
                    ("Leasing Agent", "For this unit, that's $4,200 per month minimum. Before taxes."),
                    ("You", "$4,200?! But minimum wage is only $15 an hour..."),
                    ("Leasing Agent", "That's about 70 hours a week at minimum wage. *shrugs*"),
                    (None, "The math doesn't work. It was never meant to."),
                    ("Leasing Agent", "Credit score must be 650 or higher. No exceptions."),
                    ("You", "I... I don't even have credit history yet."),
                    ("Leasing Agent", "Then you'll need a qualified co-signer with excellent credit."),
                    ("Leasing Agent", "Plus first month, last month, and security deposit."),
                    ("Leasing Agent", "Total move-in cost: $2,800. Cash or certified check only."),
                    (None, "Each requirement feels like another wall being built between you and housing."),
                    ("Well-Dressed Applicant", "Excuse me, I'm ready with my documents."),
                    ("Leasing Agent", "Oh wonderful! *brightens* Let me help you right away!"),
                    (None, "They walk past you like you've become invisible.")
                ],
                'interactions': {}
            },

            # Reality check with interactive elements
            'your_reality': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "The agent has turned away, helping the 'real' customer."),
                    (None, "You stand there with the application form, each blank line mocking you."),
                    ("You", "(thinking) Maybe if I check what I have... maybe there's something..."),
                    (None, "Deep down, you already know the answer.")
                ],
                'interactions': {
                    'wallet_check': {
                        'position': (7, 8),
                        'prompt': 'Check wallet',
                        'dialogue': [
                            "You pull out your worn wallet. The leather is cracked, held together with tape.",
                            "Three crumpled twenties. A ten. Three ones.",
                            "$73. That's literally all you have in the world.",
                            "The $2,800 deposit might as well be $2.8 million.",
                            "You notice the agent glancing at you with pity. Or is it disgust?"
                        ],
                        'required': True
                    },
                    'phone_check': {
                        'position': (9, 8),
                        'prompt': 'Check phone',
                        'dialogue': [
                            "You check your phone. Cracked screen, 8% battery.",
                            "No missed calls. No texts. No one checking if you're okay.",
                            "Contacts: A few old classmates who've moved on. The shelter hotline. That's it.",
                            "Foster parents' number is still there. Should you try calling?",
                            "What's the point? They made it clear you're on your own at 18."
                        ],
                        'required': True
                    },
                    'application_form': {
                        'position': (8, 5),
                        'prompt': 'Review application',
                        'dialogue': [
                            "MONTHLY INCOME: $_________ (You have: $0)",
                            "CREDIT SCORE: _________ (You have: No credit history)",
                            "CO-SIGNER NAME: _________ (You have: Nobody)",
                            "EMPLOYER REFERENCE: _________ (You have: Unemployed)",
                            "PREVIOUS LANDLORD: _________ (You have: Foster care)",
                            "BANK STATEMENTS: _________ (You have: $73 total)",
                            "",
                            "Every blank line is another locked door.",
                            "The system wasn't designed for people like you."
                        ],
                        'required': True
                    },
                    'exit_door': {
                        'position': (8, 10),
                        'prompt': 'Face reality',
                        'dialogue': [
                            "There's nothing more to check. Nothing more to hope for.",
                            "Income: $0. Credit: None. Co-signer: Nobody. Savings: $73.",
                            "You fold the blank application and put it in your pocket.",
                            "Maybe... maybe you should call your foster parents anyway?",
                            "What's the worst they can say? No?"
                        ],
                        'required': False
                    }
                }
            },

            # Phone call to foster parents
            'call_foster_parents': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You step into the corner of the office for some privacy."),
                    (None, "Your hands shake as you pull up their number."),
                    (None, "It rings once... twice... three times..."),
                    (None, "Maybe they won't even answer...")
                ],
                'interactions': {
                    'phone_call': {
                        'position': (8, 9),
                        'prompt': 'Make the call',
                        'trigger_activity': 'foster_parent_call',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            # After the phone call
            'call_aftermath': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You lower the phone. The dial tone echoes in your ear."),
                    ("Leasing Agent", "Everything alright over there?"),
                    ("You", "I... I don't have a co-signer."),
                    ("Leasing Agent", "Then I'm afraid there's nothing we can do. Next!"),
                    (None, "Not their problem anymore. Not anyone's problem."),
                    (None, "Just yours.")
                ],
                'interactions': {}
            },

            # Final rejection
            'first_rejection': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 4},
                    {'name': 'Security Guard', 'x': 12, 'y': 10}
                ],
                'dialogue_sequence': [
                    ("Leasing Agent", "Look, I'll be honest with you."),
                    ("Leasing Agent", "Without income, credit, or a co-signer, you can't rent anywhere."),
                    ("Leasing Agent", "Not here, not anywhere in the city. That's just how it is."),
                    ("You", "But I need somewhere to live..."),
                    ("Leasing Agent", "That's not really my problem. Security, please escort them out."),
                    ("Security Guard", "Time to go, kid."),
                    (None, "The guard's hand on your shoulder isn't rough, just firm. Dismissive."),
                    (None, "You're not a threat. You're not even worth remembering."),
                    (None, "Outside, the door clicks shut behind you. Another door that won't open.")
                ],
                'interactions': {
                    'exit_door': {
                        'position': (8, 11),
                        'prompt': 'Leave',
                        'dialogue': [
                            "You walk out into the harsh daylight.",
                            "The busy street continues as if your world hasn't just collapsed.",
                            "People with homes, jobs, and futures walk past.",
                            "You're invisible to them. A ghost already."
                        ],
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on rental office progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'found_listing':
            if self.narrative_active and self.sequence_index < 6:
                current.dynamic_description = "Listen to the leasing agent..."
            else:
                current.dynamic_description = "Understanding the requirements..."

        elif current.id == 'application_barriers':
            if self.narrative_active:
                if self.sequence_index < 5:
                    current.dynamic_description = "Learning about income requirements..."
                elif self.sequence_index < 10:
                    current.dynamic_description = "Understanding credit and deposit needs..."
                else:
                    current.dynamic_description = "Watching others succeed where you can't..."

        elif current.id == 'your_reality':
            checks = len(self.reality_checks_completed)
            if checks < 3:
                current.dynamic_description = f"Face your reality ({checks}/3 checks)"
                if checks == 0:
                    current.progress_text = "Check wallet, phone, and application"
                else:
                    remaining = self.required_checks - self.reality_checks_completed
                    current.progress_text = f"Check: {', '.join(list(remaining)[:2])}"
            else:
                current.dynamic_description = "The truth is clear now..."
                current.progress_text = "Maybe call for help?"

        elif current.id == 'call_foster_parents':
            if not self.phone_call_triggered:
                current.dynamic_description = "Make a desperate call..."
                current.progress_text = "Use your phone"
            else:
                current.dynamic_description = "Processing the rejection..."

        elif current.id == 'first_rejection':
            if self.narrative_active:
                current.dynamic_description = "Being escorted out..."
            else:
                current.dynamic_description = "Leave the office"

    def end_narrative_sequence(self):
        """Override to auto-reload room when objective changes"""
        # Call parent implementation first
        super().end_narrative_sequence()

        # Check if we should auto-reload
        if self.is_reloading:
            # Prevent infinite loops
            return

        # Check if objective has changed since sequence started
        current = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None

        if current and self.sequence_start_objective_id:
            # If the objective changed during the sequence, reload the room
            if current.id != self.sequence_start_objective_id:
                print(f"[AUTO-RELOAD] Objective changed from '{self.sequence_start_objective_id}' to '{current.id}' - reloading room")
                self.is_reloading = True
                # Clear dialogue box to avoid any visual glitches
                self.dialogue_box.hide()
                # Reload the room with new objective content
                self.enter()

    def interact_with_object(self, name):
        """Handle rental office specific interactions"""
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'found_listing'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Handle reality check interactions
            if name in self.required_checks:
                # Show the dialogue sequence
                if interaction.get('dialogue'):
                    # Store dialogue sequence for processing
                    self.pending_dialogue = interaction['dialogue']
                    self.current_dialogue_index = 0
                    # Show first line
                    if self.pending_dialogue:
                        self.dialogue_box.show(None, self.pending_dialogue[0])
                        self.current_dialogue_index = 1

                # Mark as completed
                self.reality_checks_completed.add(name)
                self.completed_interactions.add(name)

                # Check if all reality checks done
                if self.reality_checks_completed == self.required_checks:
                    # Add exit door option
                    if 'exit_door' in interactions:
                        self.add_interactive_object('exit_door', interactions['exit_door'])

                    # Show completion message
                    self.dialogue_box.show(None, "You've checked everything. The reality is undeniable.")

            # Handle phone call trigger
            elif name == 'phone_call':
                trigger = interaction.get('trigger_activity')
                if trigger == 'foster_parent_call':
                    self.launch_foster_parent_call()
                    self.phone_call_triggered = True
                    return

        # Use parent's interaction handling for other cases
        super().interact_with_object(name)

        self.update_objective_display()

        # Handle exit scenarios
        if name == 'exit_door':
            current = self.game.objective_manager.get_current_objective()
            if current:
                if current.id == 'your_reality' and 'exit_door' in self.completed_interactions:
                    # Complete your_reality and move to phone call without exiting
                    self.game.objective_manager.complete_current_objective()
                    # Re-initialize for next objective (call_foster_parents)
                    self.enter()
                elif current.id == 'first_rejection':
                    # Complete the entire sequence and exit
                    self.should_exit = True
                    self.exit_timer = 3.0

    def launch_foster_parent_call(self):
        """Launch the foster parent phone call activity"""
        from src.activities.foster_parent_call import FosterParentCall

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = FosterParentCall(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            return

        # Handle dialogue sequence advancement
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if hasattr(self, 'pending_dialogue') and self.pending_dialogue:
                if hasattr(self, 'current_dialogue_index') and self.current_dialogue_index < len(self.pending_dialogue):
                    # Show next dialogue line
                    self.dialogue_box.show(None, self.pending_dialogue[self.current_dialogue_index])
                    self.current_dialogue_index += 1
                elif hasattr(self, 'current_dialogue_index') and self.current_dialogue_index >= len(self.pending_dialogue):
                    # Dialogue sequence complete
                    self.pending_dialogue = []
                    self.current_dialogue_index = 0
                    self.dialogue_box.hide()
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
                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Start the aftermath narrative and transition to first_rejection
                if self.current_objective_phase == 'call_foster_parents':
                    self.start_narrative_sequence('call_aftermath')
                    # Complete call_foster_parents and move to first_rejection
                    self.game.objective_manager.complete_current_objective()
                    # Re-initialize for next objective (first_rejection)
                    self.enter()

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Complete objective and exit
                current = self.game.objective_manager.get_current_objective()
                if current:
                    self.game.objective_manager.complete_current_objective()
                # Exit the interior
                self.active = False

    def draw(self, screen):
        """Draw rental office interior with activity overlay"""
        # Draw base interior
        super().draw(screen)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return

        # Draw status for reality checks
        if self.current_objective_phase == 'your_reality' and len(self.reality_checks_completed) > 0:
            font = pygame.font.Font(None, 24)

            # Draw completed checks
            y_offset = 10
            for check in self.reality_checks_completed:
                check_text = check.replace('_', ' ').title()
                status_text = f"✓ {check_text}"
                status_surf = font.render(status_text, True, (100, 255, 100))
                screen.blit(status_surf, (10, y_offset))
                y_offset += 30

        # Draw emotional state indicator
        if self.current_objective_phase in ['your_reality', 'call_foster_parents']:
            # Subtle vignette effect to show emotional state
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(30)
            overlay.fill((0, 0, 50))  # Dark blue tint for sadness
            screen.blit(overlay, (0, 0))
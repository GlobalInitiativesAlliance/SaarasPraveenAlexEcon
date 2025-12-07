"""
Healthcare Apartment Interior for Part 2: Healthcare Access
Provides narrative content for healthcare storyline objectives
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class HealthcareApartmentInterior(NarrativeInterior):
    """Healthcare apartment interior with Part 2 narrative content"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)
        self.interior_name = "Healthcare Apartment"
        print(f"[HEALTHCARE] Initialized healthcare apartment interior at {building_pos}")

    def enter(self):
        """Set up apartment based on current healthcare objective"""
        super().enter()
        print("[HEALTHCARE] Player entered healthcare apartment")

        current = self.game.objective_manager.get_current_objective()
        if current:
            print(f"[HEALTHCARE] Current objective: {current.id}")
            if current.id == 'start_apartment_morning':
                self.setup_start_apartment_morning()
            elif current.id == 'check_mailbox':
                self.setup_check_mailbox()
            elif current.id == 'medicaid_notice':
                self.setup_medicaid_notice()
            elif current.id == 'therapy_reminder':
                self.setup_therapy_reminder()
            elif current.id == 'insurance_panic':
                self.setup_insurance_panic()
            elif current.id == 'therapist_call_options':
                self.setup_therapist_call_options()
            elif current.id == 'therapy_payment_decision':
                self.setup_therapy_payment_decision()
            elif current.id == 'caseworker_guidance':
                self.setup_caseworker_guidance()
            elif current.id == 'coverage_restored':
                self.setup_coverage_restored()
            else:
                print(f"[HEALTHCARE] No specific setup for objective: {current.id}")

        self.update_objective_display()

    def update(self, dt):
        """Update healthcare apartment interior"""
        # Call parent update first
        super().update(dt)

        # Check for objective changes to trigger auto-exit
        self.update_objective_display()

    def interact_with_object(self, name):
        """Override to handle healthcare activity launching"""
        if name in self.interactive_objects:
            obj = self.interactive_objects[name]
            trigger = obj.get('trigger_activity')

            if trigger == 'mailbox_sorting':
                print("[HEALTHCARE] Launching mailbox sorting activity")
                self.launch_mailbox_sorting()
                return

        # Handle non-activity interactions normally
        super().interact_with_object(name)
        self.update_objective_display()

    def launch_mailbox_sorting(self):
        """Launch the mailbox sorting game"""
        from part_2_healthcare.activities.mailbox_sorting import MailboxSortingGame

        print("[HEALTHCARE] Creating mailbox sorting game...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = MailboxSortingGame(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[HEALTHCARE] Setting mailbox game as current activity...")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[HEALTHCARE] Mailbox sorting game launched successfully!")

    def update_objective_display(self):
        """Update objectives based on completed interactions"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # Check if objective changed (activity completed it)
        if not hasattr(self, 'last_objective_id'):
            self.last_objective_id = current.id
        elif self.last_objective_id != current.id:
            print(f"[HEALTHCARE] Objective changed from {self.last_objective_id} to {current.id} - starting exit timer")

            # Show completion message based on what was completed
            if self.last_objective_id == 'check_mailbox':
                completion_message = "Critical mail found! Your Medi-Cal coverage has been terminated."
            elif self.last_objective_id == 'start_apartment_morning':
                completion_message = "Ready to face the day. Time to check the mail."
            else:
                completion_message = f"Objective '{self.last_objective_id}' completed."

            # Show dialogue with completion message
            self.dialogue_box.show(None, completion_message)

            # Show objective completion feedback (if method exists)
            if hasattr(self, 'show_objective_completion'):
                try:
                    self.show_objective_completion()
                except Exception as e:
                    print(f"[HEALTHCARE] Could not show objective completion: {e}")

            # Start exit timer with longer delay to read message
            self.start_exit_timer(4.0)  # 4 second delay to read completion message
            self.last_objective_id = current.id
            return

        # Check completion conditions for each healthcare objective
        if current.id == 'start_apartment_morning':
            if 'get_up' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'check_mailbox':
            # DON'T auto-complete based on interaction - let the mailbox game handle completion
            # The mailbox sorting activity will complete the objective when critical mail is found
            pass

        elif current.id == 'medicaid_notice':
            if 'read_notice' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'therapy_reminder':
            if 'check_phone' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'insurance_panic':
            if 'panic_about_coverage' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'therapist_call_options':
            if 'answer_call' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'therapy_payment_decision':
            if 'make_payment_decision' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'caseworker_guidance':
            if 'answer_caseworker' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'coverage_restored':
            if 'read_good_news' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

    def setup_start_apartment_morning(self):
        """Setup for morning wake-up objective"""
        interactions = self.narrative_content['start_apartment_morning']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('start_apartment_morning')

    def setup_check_mailbox(self):
        """Setup for mailbox check objective"""
        print("[HEALTHCARE] Setting up check_mailbox objective")
        interactions = self.narrative_content['check_mailbox']['interactions']
        for obj_name, obj_data in interactions.items():
            print(f"[HEALTHCARE] Adding interactive object: {obj_name} at {obj_data.get('position')}")
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('check_mailbox')
        print("[HEALTHCARE] check_mailbox setup complete")

    def setup_therapist_call_options(self):
        """Setup for therapist call options objective"""
        interactions = self.narrative_content['therapist_call_options']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('therapist_call_options')

    def setup_therapy_payment_decision(self):
        """Setup for therapy payment decision objective"""
        interactions = self.narrative_content['therapy_payment_decision']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('therapy_payment_decision')

    def setup_caseworker_guidance(self):
        """Setup for caseworker guidance objective"""
        interactions = self.narrative_content['caseworker_guidance']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('caseworker_guidance')

    def setup_coverage_restored(self):
        """Setup for coverage restored objective"""
        interactions = self.narrative_content['coverage_restored']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('coverage_restored')

    def setup_medicaid_notice(self):
        """Setup for reading medicaid termination notice"""
        interactions = self.narrative_content['medicaid_notice']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('medicaid_notice')

    def setup_therapy_reminder(self):
        """Setup for therapy appointment reminder"""
        interactions = self.narrative_content['therapy_reminder']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('therapy_reminder')

    def setup_insurance_panic(self):
        """Setup for insurance panic realization"""
        interactions = self.narrative_content['insurance_panic']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('insurance_panic')

    def load_narrative_content(self):
        """Load narrative content for healthcare apartment objectives"""
        return {
            'start_apartment_morning': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone alarm buzzes. 9:00 AM."),
                    (None, "Sunlight filters through the cracked window of your small apartment."),
                    (None, "Another day begins. You stretch and get ready to face whatever comes next."),
                    (None, "Time to check the mail and see what the day brings.")
                ],
                'interactions': {
                    'get_up': {
                        'position': (8, 6),
                        'prompt': 'Get up and start your day',
                        'dialogue': [
                            "You swing your legs out of bed and stretch.",
                            "The apartment may be small, but it's yours.",
                            "You should check your mail - important letters sometimes arrive.",
                            "Time to see what today has in store."
                        ],
                        'required': True,
                        'objective_completion': 'start_apartment_morning'
                    }
                }
            },
            'check_mailbox': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You walk to your mailbox outside the apartment."),
                    (None, "There are several pieces of mail today."),
                    (None, "Time to sort through them and see what's important.")
                ],
                'interactions': {
                    'sort_mail': {
                        'position': (8, 4),
                        'prompt': 'Sort through today\'s mail',
                        'dialogue': [
                            "You pull out a stack of mail.",
                            "Bills, advertisements, and... something from the state.",
                            "Time to sort through this carefully."
                        ],
                        'required': True,
                        'trigger_activity': 'mailbox_sorting'
                    }
                }
            },
            'medicaid_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You stare at the official notice in disbelief."),
                    (None, "'Coverage Terminated' - the words seem to burn on the page."),
                    (None, "Your Medi-Cal coverage has ended due to age eligibility."),
                    (None, "This can't be happening...")
                ],
                'interactions': {
                    'read_notice': {
                        'position': (8, 5),
                        'prompt': 'Read the termination notice carefully',
                        'dialogue': [
                            "IMPORTANT NOTICE: Medi-Cal Coverage Termination",
                            "Dear Former Foster Youth,",
                            "Your coverage under the Former Foster Youth program has ended.",
                            "Reason: Age eligibility expired (over 26 years old)",
                            "Coverage end date: Effective immediately",
                            "You: No, no, no... I still need this coverage!",
                            "The letter feels heavy in your hands.",
                            "Without insurance, everything becomes more expensive."
                        ],
                        'required': True,
                        'objective_completion': 'medicaid_notice'
                    }
                }
            },
            'therapy_reminder': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone buzzes with a notification."),
                    (None, "It's a reminder about your therapy appointment."),
                    (None, "Tomorrow at 2 PM with Dr. Sarah.")
                ],
                'interactions': {
                    'check_phone': {
                        'position': (6, 6),
                        'prompt': 'Check your phone notification',
                        'dialogue': [
                            "*BUZZ BUZZ*",
                            "Reminder: Therapy appointment tomorrow at 2:00 PM",
                            "Dr. Sarah Wilson - Mindful Healing Center",
                            "Don't forget to bring your insurance card!",
                            "You stare at the reminder.",
                            "Insurance card... the one that no longer works.",
                            "This is going to be a problem."
                        ],
                        'required': True,
                        'objective_completion': 'therapy_reminder'
                    }
                }
            },
            'insurance_panic': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The reality hits you like a punch to the gut."),
                    (None, "No insurance + therapy appointment = financial disaster."),
                    (None, "You need to figure this out, and fast.")
                ],
                'interactions': {
                    'panic_about_coverage': {
                        'position': (7, 6),
                        'prompt': 'Worry about the insurance situation',
                        'dialogue': [
                            "Your mind races with calculations:",
                            "• Therapy session without insurance: $150",
                            "• Your weekly income: $200",
                            "• Rent due in two weeks: $450",
                            "• Food budget: $50/week",
                            "You: There's no way I can afford this...",
                            "You: But I NEED therapy. My mental health depends on it.",
                            "You: I have to find a solution. Fast.",
                            "Maybe the community health clinic can help."
                        ],
                        'required': True,
                        'objective_completion': 'insurance_panic'
                    }
                }
            },
            'therapist_call_options': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone rings. It's Dr. Sarah's office."),
                    (None, "They're calling about tomorrow's appointment and payment.")
                ],
                'interactions': {
                    'answer_call': {
                        'position': (6, 6),
                        'prompt': 'Answer the therapist office call',
                        'dialogue': [
                            "Receptionist: Hi, this is about your appointment tomorrow.",
                            "Receptionist: We received notice your insurance was terminated.",
                            "Receptionist: You have a few options for tomorrow:",
                            "• Pay full price: $150",
                            "• Cancel the appointment",
                            "• Apply for our sliding scale fee: $40 based on income",
                            "Receptionist: What would you like to do?",
                            "You: I... I need to think about this.",
                            "This is a tough decision with serious consequences."
                        ],
                        'required': True,
                        'objective_completion': 'therapist_call_options'
                    }
                }
            },
            'therapy_payment_decision': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to decide how to handle your therapy appointment."),
                    (None, "Each choice has different consequences for your health and finances.")
                ],
                'interactions': {
                    'make_payment_decision': {
                        'position': (8, 6),
                        'prompt': 'Choose your payment option',
                        'dialogue': [
                            "Your options:",
                            "1. Sliding scale fee ($40) - Affordable, maintains mental health",
                            "2. Cancel appointment - Free, but mental health may suffer",
                            "3. Full price ($150) - Keeps appointment, strains budget severely",
                            "You think carefully about what you can afford.",
                            "Your mental health is important, but so is paying rent.",
                            "This is the kind of impossible choice many face.",
                            "You: I'll go with the sliding scale option.",
                            "It's the best balance of affordability and care."
                        ],
                        'required': True,
                        'objective_completion': 'therapy_payment_decision'
                    }
                }
            },
            'caseworker_guidance': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone rings. It's your caseworker."),
                    (None, "They have some guidance about healthcare resources.")
                ],
                'interactions': {
                    'answer_caseworker': {
                        'position': (6, 6),
                        'prompt': 'Answer your caseworker\'s call',
                        'dialogue': [
                            "Caseworker: Hi, I heard about your insurance situation.",
                            "Caseworker: I want to connect you with our mental health navigator.",
                            "Caseworker: They specialize in helping former foster youth.",
                            "Caseworker: They can help you understand your options.",
                            "Caseworker: And make sure you don't lose coverage again.",
                            "You: That would be really helpful. Thank you.",
                            "Having professional guidance makes all the difference."
                        ],
                        'required': True,
                        'objective_completion': 'caseworker_guidance'
                    }
                }
            },
            'coverage_restored': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Your phone buzzes with a text message."),
                    (None, "It's good news about your coverage!")
                ],
                'interactions': {
                    'read_good_news': {
                        'position': (6, 6),
                        'prompt': 'Check the text message',
                        'dialogue': [
                            "*TEXT MESSAGE*",
                            "Great news! Your Medi-Cal coverage is now active.",
                            "Your new therapy appointment is scheduled for Friday at 2 PM.",
                            "Dr. Sarah is looking forward to seeing you.",
                            "Remember: You have resources and support available.",
                            "You: Finally! This is such a relief.",
                            "You've learned to navigate the healthcare system.",
                            "And you have ongoing support to maintain your coverage."
                        ],
                        'required': True,
                        'objective_completion': 'coverage_restored'
                    }
                }
            }
        }

    def draw(self, screen):
        """Draw the healthcare apartment interior with activity support"""
        # Draw base narrative interior
        super().draw(screen)

        # Draw exit countdown if exiting
        if hasattr(self, 'should_exit') and self.should_exit and hasattr(self, 'exit_timer') and self.exit_timer > 0:
            self.draw_exit_countdown(screen)

        # Also draw any active objective manager activity (like mailbox game)
        if (hasattr(self.game, 'objective_manager') and
            hasattr(self.game.objective_manager, 'current_activity') and
            self.game.objective_manager.current_activity and
            hasattr(self.game.objective_manager.current_activity, 'active') and
            self.game.objective_manager.current_activity.active):
            self.game.objective_manager.current_activity.draw(screen)

    def draw_exit_countdown(self, screen):
        """Draw exit countdown timer"""
        countdown_seconds = int(self.exit_timer) + 1

        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Draw countdown text
        font = pygame.font.Font(None, 48)
        countdown_text = f"Leaving in {countdown_seconds}..."
        text_surface = font.render(countdown_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))

        # Draw background for text
        bg_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(screen, (40, 40, 50), bg_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, width=2, border_radius=10)

        screen.blit(text_surface, text_rect)

    def get_exit_position(self):
        """Return position where player exits to world map"""
        return (54, 34)  # Just below the apartment building
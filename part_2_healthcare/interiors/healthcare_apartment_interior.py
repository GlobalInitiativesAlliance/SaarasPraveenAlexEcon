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
        self.current_activity = None  # Initialize activity tracking
        print(f"[HEALTHCARE] Initialized healthcare apartment interior at {building_pos}")

    def setup_start_apartment_morning(self):
        """Setup for morning wake-up objective"""
        interactions = self.narrative_content['start_apartment_morning']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('start_apartment_morning')

    def setup_check_mailbox(self):
        """Setup for mailbox check objective"""
        interactions = self.narrative_content['check_mailbox']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('check_mailbox')

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
                        'trigger_activity': 'mailbox_sorting'
                        # Note: removed 'required' and 'objective_completion' to prevent auto-completion
                        # The mini-game itself will handle objective completion when finished
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

    def launch_activity(self, activity_name):
        """Launch healthcare-specific activities"""
        print(f"[HEALTHCARE] launch_activity called with: {activity_name}")
        if activity_name == 'mailbox_sorting':
            print("[HEALTHCARE] Launching mailbox sorting mini-game...")

            # Clear any active dialogue
            if hasattr(self, 'dialogue_box'):
                self.dialogue_box.hide()

            # Launch the enhanced mailbox sorting mini-game
            from part_2_healthcare.activities.enhanced_mailbox_sorting import EnhancedMailboxSortingGame
            mailbox_game = EnhancedMailboxSortingGame(self.game.objective_manager)
            mailbox_game.start()

            # Set as current activity on both interior and objective manager
            self.current_activity = mailbox_game
            self.game.objective_manager.current_activity = mailbox_game
            print(f"[HEALTHCARE] Mini-game started - Active: {mailbox_game.active}")
        else:
            print(f"[HEALTHCARE] Unknown activity: {activity_name}, calling parent")
            # Call parent method for other activities
            super().launch_activity(activity_name)

    def handle_event(self, event):
        """Handle events including activity events"""
        # If there's an active activity, let it handle events first
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            print(f"[HEALTHCARE] Activity is active, passing event to activity")
            if hasattr(self.current_activity, 'handle_event'):
                if self.current_activity.handle_event(event):
                    return True

        # Otherwise use parent event handling
        result = super().handle_event(event)
        if event.type == 768:  # KEYDOWN
            print(f"[HEALTHCARE] Parent handle_event returned: {result}")
        return result

    def update(self, dt):
        """Update interior including activities"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)
                # Only print occasionally to avoid spam
                if int(dt * 1000) % 500 < 50:  # Print every ~500ms
                    print(f"[HEALTHCARE] Updating active activity")

            # Check if activity completed
            if self.current_activity.completed:
                print(f"[HEALTHCARE] Activity completed! Completing objective.")
                # Mark interaction as completed
                self.completed_interactions.add('sort_mail')

                # Clear the current activity
                self.current_activity = None
                if hasattr(self.game, 'objective_manager'):
                    self.game.objective_manager.current_activity = None

                # Complete the objective
                if hasattr(self.game, 'objective_manager'):
                    self.game.objective_manager.complete_current_objective()

    def draw(self, screen):
        """Draw interior including activities"""
        # If there's an active activity, render it instead of the interior
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            print(f"[HEALTHCARE] Rendering activity instead of interior")
            self.current_activity.render(screen)
        else:
            # Otherwise use parent drawing
            super().draw(screen)

    def get_exit_position(self):
        """Return position where player exits to world map"""
        return (54, 34)  # Just below the apartment building
"""
Healthcare Apartment Interior for Part 2: Healthcare Access
Provides narrative content for healthcare storyline objectives
"""
import pygame
import math
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
            elif current.id == 'travel_to_clinic':
                self.setup_travel_to_clinic()
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

        # FORCE check current objective every frame
        current = self.game.objective_manager.get_current_objective()
        if current:
            print(f"[HEALTHCARE_UPDATE] Current objective: {current.id}, Interactions: {list(self.interactive_objects.keys())}")

            # FORCE narrative_active to False for all healthcare objectives to allow E key
            if current.id in ['therapy_reminder', 'medicaid_notice', 'insurance_panic', 'travel_to_clinic', 'therapist_call_options', 'therapy_payment_decision', 'caseworker_guidance', 'coverage_restored']:
                self.narrative_active = False

            # If we have no interactions but should have them, force setup
            if current.id == 'therapy_reminder' and not self.interactive_objects:
                print("[HEALTHCARE_UPDATE] EMERGENCY: No interactions for therapy_reminder, forcing setup NOW")
                self.force_objective_setup('therapy_reminder')

        # Check for objective changes to trigger auto-exit
        self.update_objective_display()

        # Update contextual thoughts
        self.update_contextual_thoughts(dt)

    def handle_event(self, event):
        """Handle events with debug logging and direct E key handling"""
        print(f"[HEALTHCARE] handle_event called: type={event.type}, key={getattr(event, 'key', None)}")

        if event.type == pygame.KEYDOWN:
            print(f"[HEALTHCARE] Key pressed: {event.key}")
            if event.key == pygame.K_e:
                print("[HEALTHCARE] E key detected in healthcare apartment!")

                # Handle E key for interactions directly
                print(f"[HEALTHCARE] Checking interactions: {list(self.interactive_objects.keys())}")
                print(f"[HEALTHCARE] narrative_active: {getattr(self, 'narrative_active', 'undefined')}")
                print(f"[HEALTHCARE] dialogue_active: {getattr(self.dialogue_box, 'active', 'undefined')}")

                # Check if we can interact
                if (not getattr(self, 'narrative_active', False) and
                    not getattr(self.dialogue_box, 'active', False)):

                    # Debug player position and interactions
                    if hasattr(self.game, 'player'):
                        player_pos = (self.game.player.x, self.game.player.y)
                        print(f"[HEALTHCARE] Player position: {player_pos}")

                    print(f"[HEALTHCARE] Available interactions: {list(self.interactive_objects.keys())}")
                    for name, obj in self.interactive_objects.items():
                        interaction_pos = obj.get('position', 'no position')
                        print(f"[HEALTHCARE] - {name} at {interaction_pos}")

                    # Check for nearby interactive objects
                    obj_name, obj = self.check_interactions()
                    print(f"[HEALTHCARE] Interaction check result: obj_name={obj_name}, obj={obj}")

                    if obj:
                        print(f"[HEALTHCARE] Triggering interaction: {obj_name}")
                        self.interact_with_object(obj_name)
                        return
                    else:
                        print("[HEALTHCARE] No interactions found - player not close enough to any interaction")
                else:
                    print(f"[HEALTHCARE] E key blocked - narrative_active: {getattr(self, 'narrative_active', False)}, dialogue_active: {getattr(self.dialogue_box, 'active', False)}")

        # Call parent method for other events
        super().handle_event(event)

    def interact_with_object(self, name):
        """Override to handle healthcare activity launching"""
        print(f"[HEALTHCARE] interact_with_object called with: {name}")

        if name in self.interactive_objects:
            obj = self.interactive_objects[name]
            print(f"[HEALTHCARE] Object data: {obj}")
            trigger = obj.get('trigger_activity')
            print(f"[HEALTHCARE] Trigger activity: {trigger}")

            if trigger == 'mailbox_sorting':
                print("[HEALTHCARE] Launching mailbox sorting activity")
                self.launch_mailbox_sorting()
                return
            elif trigger == 'medicaid_notice':
                print("[HEALTHCARE] Launching medicaid notice reading activity")
                self.launch_medicaid_notice()
                return
            elif trigger == 'therapy_reminder':
                print("[HEALTHCARE] Launching therapy reminder phone activity")
                self.launch_therapy_reminder()
                return
            elif trigger == 'insurance_panic':
                print("[HEALTHCARE] Launching insurance panic crisis activity")
                self.launch_insurance_panic()
                return
            elif trigger == 'therapist_call':
                print("[HEALTHCARE] Launching therapist call options activity")
                self.launch_therapist_call()
                return
            elif trigger == 'therapy_payment_decision':
                print("[HEALTHCARE] Launching therapy payment decision activity")
                self.launch_therapy_payment_decision()
                return

        # Handle non-activity interactions normally
        print(f"[HEALTHCARE] Calling parent interact_with_object for: {name}")
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

    def launch_medicaid_notice(self):
        """Launch the medicaid notice reading activity"""
        from part_2_healthcare.activities.medicaid_notice_activity import MedicaidNoticeActivity

        print("[HEALTHCARE] Starting medicaid notice reading...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = MedicaidNoticeActivity(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[HEALTHCARE] Setting medicaid notice as current activity...")
            print(f"[HEALTHCARE] Activity active state: {activity.active}")
            print(f"[HEALTHCARE] Activity completed state: {activity.completed}")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[HEALTHCARE] Medicaid notice activity launched successfully!")
        else:
            print("[HEALTHCARE] ERROR: No objective manager found!")

    def launch_therapy_reminder(self):
        """Launch the therapy reminder phone notification activity"""
        from part_2_healthcare.activities.therapy_reminder_activity import TherapyReminderActivity

        print("[HEALTHCARE] Starting therapy reminder reading...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = TherapyReminderActivity(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[HEALTHCARE] Setting therapy reminder as current activity...")
            print(f"[HEALTHCARE] Activity active state: {activity.active}")
            print(f"[HEALTHCARE] Activity completed state: {activity.completed}")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[HEALTHCARE] Therapy reminder activity launched successfully!")
        else:
            print("[HEALTHCARE] ERROR: No objective manager found!")

    def launch_insurance_panic(self):
        """Launch the insurance panic crisis realization activity"""
        from part_2_healthcare.activities.insurance_panic_activity import InsurancePanicActivity

        print("[HEALTHCARE] Starting insurance panic crisis...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = InsurancePanicActivity(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[HEALTHCARE] Setting insurance panic as current activity...")
            print(f"[HEALTHCARE] Activity active state: {activity.active}")
            print(f"[HEALTHCARE] Activity completed state: {activity.completed}")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[HEALTHCARE] Insurance panic activity launched successfully!")
        else:
            print("[HEALTHCARE] ERROR: No objective manager found!")

    def launch_therapist_call(self):
        """Launch the therapist call options activity"""
        from part_2_healthcare.activities.therapist_call_activity import TherapistCallActivity

        print("[HEALTHCARE] Starting therapist call options...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = TherapistCallActivity(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[HEALTHCARE] Setting therapist call as current activity...")
            print(f"[HEALTHCARE] Activity active state: {activity.active}")
            print(f"[HEALTHCARE] Activity completed state: {activity.completed}")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[HEALTHCARE] Therapist call activity launched successfully!")
        else:
            print("[HEALTHCARE] ERROR: No objective manager found!")

    def launch_therapy_payment_decision(self):
        """Launch the therapy payment decision activity"""
        from part_2_healthcare.activities.therapy_payment_decision_activity import TherapyPaymentDecisionActivity

        print("[HEALTHCARE] Starting therapy payment decision...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = TherapyPaymentDecisionActivity(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[HEALTHCARE] Setting therapy payment decision as current activity...")
            print(f"[HEALTHCARE] Activity active state: {activity.active}")
            print(f"[HEALTHCARE] Activity completed state: {activity.completed}")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[HEALTHCARE] Therapy payment decision activity launched successfully!")
        else:
            print("[HEALTHCARE] ERROR: No objective manager found!")

    def force_objective_setup(self, objective_id):
        """Force setup of interactions for a specific objective"""
        print(f"[HEALTHCARE] Force setting up objective: {objective_id}")
        print(f"[HEALTHCARE] Current interactions before cleanup: {list(self.interactive_objects.keys())}")

        # Clear old interactions to prevent conflicts
        self.interactive_objects.clear()
        self.completed_interactions.clear()

        # CRITICAL FIX: Force narrative_active to False to allow E key interactions
        self.narrative_active = False
        print(f"[HEALTHCARE] Set narrative_active to False")

        # Set up interactions for the objective
        if objective_id == 'medicaid_notice':
            self.setup_medicaid_notice()
        elif objective_id == 'therapy_reminder':
            self.setup_therapy_reminder()
        elif objective_id == 'insurance_panic':
            self.setup_insurance_panic()
        elif objective_id == 'travel_to_clinic':
            self.setup_travel_to_clinic()
        elif objective_id == 'therapist_call_options':
            self.setup_therapist_call_options()
        elif objective_id == 'therapy_payment_decision':
            self.setup_therapy_payment_decision()
        elif objective_id == 'caseworker_guidance':
            self.setup_caseworker_guidance()
        elif objective_id == 'coverage_restored':
            self.setup_coverage_restored()
        elif objective_id == 'check_mailbox':
            self.setup_check_mailbox()
        elif objective_id == 'start_apartment_morning':
            self.setup_start_apartment_morning()
        else:
            print(f"[HEALTHCARE] No specific setup for objective: {objective_id}")

        print(f"[HEALTHCARE] Current interactions after setup: {list(self.interactive_objects.keys())}")

    def update_objective_display(self):
        """Update objectives based on completed interactions"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # Track objective changes and handle transitions
        if not hasattr(self, 'last_objective_id'):
            self.last_objective_id = current.id

        # Force refresh interactions for current objective if none exist
        if not self.interactive_objects and current.id:
            print(f"[HEALTHCARE] No interactions found for {current.id}, forcing setup")
            self.force_objective_setup(current.id)

        # Handle objective transitions
        elif self.last_objective_id != current.id:
            print(f"[HEALTHCARE] Objective changed from {self.last_objective_id} to {current.id}")
            self.force_objective_setup(current.id)
            self.last_objective_id = current.id

        # Check completion conditions for each healthcare objective
        if current.id == 'start_apartment_morning':
            if 'get_up' in self.completed_interactions:
                self.game.objective_manager.complete_current_objective()

        elif current.id == 'check_mailbox':
            # DON'T auto-complete based on interaction - let the mailbox game handle completion
            # The mailbox sorting activity will complete the objective when critical mail is found
            pass

        elif current.id == 'medicaid_notice':
            # DON'T auto-complete based on interaction - let the medicaid notice activity handle completion
            # The medicaid notice reading activity will complete the objective when fully read
            pass

        elif current.id == 'therapy_reminder':
            # DON'T auto-complete based on interaction - let the therapy reminder activity handle completion
            # The therapy reminder phone activity will complete the objective when fully read
            pass

        elif current.id == 'insurance_panic':
            # DON'T auto-complete based on interaction - let the insurance panic activity handle completion
            # The insurance panic crisis activity will complete the objective when fully experienced
            pass

        elif current.id == 'travel_to_clinic':
            if 'leave_for_clinic' in self.completed_interactions:
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
        """Setup for therapist call options objective with contextual dialogue"""
        print("[HEALTHCARE] Setting up therapist call options interactions")
        interactions = self.narrative_content['therapist_call_options']['interactions']
        print(f"[HEALTHCARE] Available interactions: {interactions.keys()}")
        for obj_name, obj_data in interactions.items():
            print(f"[HEALTHCARE] Adding interaction: {obj_name} at {obj_data.get('position')}")
            self.add_interactive_object(obj_name, obj_data)

        # Show contextual thoughts that DON'T block E key
        self.show_contextual_thoughts('therapist_call_options')
        print("[HEALTHCARE] Therapist call options setup complete")

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
        print("[HEALTHCARE] Setting up medicaid notice interactions")
        interactions = self.narrative_content['medicaid_notice']['interactions']
        print(f"[HEALTHCARE] Available interactions: {interactions.keys()}")
        for obj_name, obj_data in interactions.items():
            print(f"[HEALTHCARE] Adding interaction: {obj_name} at {obj_data.get('position')}")
            self.add_interactive_object(obj_name, obj_data)
        # Don't start narrative sequence since we removed the dialogue
        print("[HEALTHCARE] Medicaid notice setup complete")

    def setup_therapy_reminder(self):
        """Setup for therapy appointment reminder"""
        interactions = self.narrative_content['therapy_reminder']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('therapy_reminder')

    def setup_insurance_panic(self):
        """Setup for insurance panic realization"""
        print("[HEALTHCARE] Setting up insurance panic interactions")
        interactions = self.narrative_content['insurance_panic']['interactions']
        print(f"[HEALTHCARE] Available interactions: {interactions.keys()}")
        for obj_name, obj_data in interactions.items():
            print(f"[HEALTHCARE] Adding interaction: {obj_name} at {obj_data.get('position')}")
            self.add_interactive_object(obj_name, obj_data)
        # Don't start narrative sequence since we removed the dialogue
        print("[HEALTHCARE] Insurance panic setup complete")

    def setup_travel_to_clinic(self):
        """Setup for traveling to community health clinic with contextual dialogue"""
        print("[HEALTHCARE] Setting up travel to clinic interactions")
        interactions = self.narrative_content['travel_to_clinic']['interactions']
        print(f"[HEALTHCARE] Available interactions: {interactions.keys()}")
        for obj_name, obj_data in interactions.items():
            print(f"[HEALTHCARE] Adding interaction: {obj_name} at {obj_data.get('position')}")
            self.add_interactive_object(obj_name, obj_data)

        # Show contextual thoughts that DON'T block E key
        self.show_contextual_thoughts('travel_to_clinic')
        print("[HEALTHCARE] Travel to clinic setup complete")

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
                'dialogue_sequence': [],
                'interactions': {
                    'read_notice': {
                        'position': (8, 5),
                        'prompt': 'Read the termination notice carefully',
                        'dialogue': [
                            "You pick up the official government letter.",
                            "The header reads: 'NOTICE OF MEDICAID COVERAGE TERMINATION'",
                            "Your hands tremble slightly as you prepare to read it."
                        ],
                        'required': True,
                        'trigger_activity': 'medicaid_notice'
                    }
                }
            },
            'therapy_reminder': {
                'npcs': [],
                'dialogue_sequence': [],
                'interactions': {
                    'check_phone': {
                        'position': (6, 6),
                        'prompt': 'Check phone notification',
                        'dialogue': [
                            "Your phone is buzzing with a notification.",
                            "It's from the Wellness Center.",
                            "You pick up your phone to read the message."
                        ],
                        'required': True,
                        'trigger_activity': 'therapy_reminder'
                    }
                }
            },
            'insurance_panic': {
                'npcs': [],
                'dialogue_sequence': [],
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
                        'trigger_activity': 'insurance_panic'
                    }
                }
            },
            'travel_to_clinic': {
                'npcs': [],
                'dialogue_sequence': [],
                'interactions': {
                    'leave_for_clinic': {
                        'position': (8, 8),  # Near apartment exit
                        'prompt': 'Leave apartment and go to clinic',
                        'dialogue': [
                            "You take a deep breath and grab your wallet and keys.",
                            "The weight of the insurance situation sits heavy on your mind.",
                            "The Community Health Clinic has helped other foster youth before.",
                            "Maybe they'll have a solution for your coverage gap.",
                            "You lock the apartment door behind you.",
                            "As you walk toward the clinic, you try to stay hopeful.",
                            "Healthcare shouldn't be this complicated for young adults aging out of care.",
                            "But you're taking action - that's what matters right now."
                        ],
                        'required': True,
                        'objective_completion': 'travel_to_clinic'
                    }
                }
            },
            'therapist_call_options': {
                'npcs': [],
                'dialogue_sequence': [],
                'interactions': {
                    'answer_call': {
                        'position': (6, 6),
                        'prompt': 'Answer the therapist office call',
                        'dialogue': [
                            "Your phone is ringing with a call from Dr. Chen's office.",
                            "Time to discuss payment options for tomorrow's therapy session."
                        ],
                        'required': True,
                        'trigger_activity': 'therapist_call'
                    }
                }
            },
            'therapy_payment_decision': {
                'npcs': [],
                'dialogue_sequence': [],
                'interactions': {
                    'make_payment_decision': {
                        'position': (8, 6),
                        'prompt': 'Choose your payment option',
                        'dialogue': [
                            "Time to decide how to handle your therapy appointment.",
                            "Each choice has different consequences for your health and finances."
                        ],
                        'required': True,
                        'trigger_activity': 'therapy_payment_decision'
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

    def draw_enhanced_background(self, screen):
        """Draw enhanced apartment background with emotional context"""
        # Get current objective for emotional context
        current = self.game.objective_manager.get_current_objective()

        # Base color depends on current emotional state of story
        if current and current.id in ['insurance_panic', 'therapy_reminder']:
            # Anxious/stressful environment
            base_r, base_g, base_b = 45, 35, 50
        elif current and current.id in ['medicaid_notice']:
            # Official/serious environment
            base_r, base_g, base_b = 40, 45, 55
        else:
            # Neutral apartment environment
            base_r, base_g, base_b = 50, 55, 65

        # Create atmospheric gradient
        for y in range(screen.get_height()):
            progress = y / screen.get_height()

            r = int(base_r + progress * 20)
            g = int(base_g + progress * 25)
            b = int(base_b + progress * 30)

            # Add subtle texture
            texture = math.sin(y * 0.02) * 3
            r = min(255, max(0, r + int(texture)))
            g = min(255, max(0, g + int(texture)))
            b = min(255, max(0, b + int(texture)))

            pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))

    def draw(self, screen):
        """Draw the healthcare apartment interior with enhanced visuals and activity support"""
        # Draw enhanced background
        self.draw_enhanced_background(screen)

        # Draw base narrative interior
        super().draw(screen)

        # DEBUG: Draw interaction hotspots with labels
        if hasattr(self, 'interactive_objects'):
            for name, obj in self.interactive_objects.items():
                if 'position' in obj:
                    pos = obj['position']
                    # Convert grid position to screen coordinates (assuming 32x32 tiles)
                    screen_x = pos[0] * 32
                    screen_y = pos[1] * 32

                    # Draw debug circle at interaction position
                    pygame.draw.circle(screen, (255, 0, 0), (screen_x + 16, screen_y + 16), 20, 3)

                    # Draw label
                    font = pygame.font.Font(None, 24)
                    text = font.render(f"E: {name}", True, (255, 255, 0))
                    screen.blit(text, (screen_x - 20, screen_y - 30))

                    print(f"[DEBUG] Interaction '{name}' at grid {pos} -> screen ({screen_x}, {screen_y})")

        # Silent exit - no countdown overlay

        # Draw contextual thoughts (non-blocking narrative)
        self.draw_contextual_thoughts(screen)

        # Draw any active activity (like mailbox game or medicaid notice)
        if (hasattr(self.game, 'objective_manager') and
            hasattr(self.game.objective_manager, 'current_activity') and
            self.game.objective_manager.current_activity and
            hasattr(self.game.objective_manager.current_activity, 'active') and
            self.game.objective_manager.current_activity.active):

            activity = self.game.objective_manager.current_activity
            activity_type = type(activity).__name__
            print(f"[HEALTHCARE] Drawing active activity: {activity_type}")
            activity.draw(screen)

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

    def show_contextual_thoughts(self, objective_id):
        """Show contextual thoughts that enhance narrative without blocking gameplay"""
        if not hasattr(self, 'contextual_thoughts'):
            self.contextual_thoughts = {
                'text': '',
                'timer': 0,
                'fade_alpha': 0,
                'position': 0
            }

        thoughts = {
            'travel_to_clinic': "You need to get to the Community Health Clinic. Maybe they can help with your insurance situation.",
            'therapy_reminder': "Your phone is buzzing. It looks like a message from your therapist's office.",
            'insurance_panic': "The reality is hitting you - no insurance means expensive healthcare costs.",
            'therapist_call_options': "Your phone is ringing. It's Dr. Sarah's office calling about tomorrow's appointment and payment options."
        }

        if objective_id in thoughts:
            self.contextual_thoughts['text'] = thoughts[objective_id]
            self.contextual_thoughts['timer'] = 8.0  # Show for 8 seconds
            self.contextual_thoughts['fade_alpha'] = 255
            self.contextual_thoughts['position'] = 0

    def update_contextual_thoughts(self, dt):
        """Update contextual thoughts display"""
        if hasattr(self, 'contextual_thoughts') and self.contextual_thoughts['timer'] > 0:
            self.contextual_thoughts['timer'] -= dt

            # Fade out in last 2 seconds
            if self.contextual_thoughts['timer'] < 2.0:
                fade_progress = self.contextual_thoughts['timer'] / 2.0
                self.contextual_thoughts['fade_alpha'] = int(255 * fade_progress)

            # Subtle floating animation
            self.contextual_thoughts['position'] = math.sin(pygame.time.get_ticks() * 0.001) * 3

    def draw_contextual_thoughts(self, screen):
        """Draw contextual thoughts overlay that doesn't block gameplay"""
        if (hasattr(self, 'contextual_thoughts') and
            self.contextual_thoughts['timer'] > 0 and
            self.contextual_thoughts['text']):

            # Semi-transparent thought bubble at top of screen
            thought_rect = pygame.Rect(100, 50 + self.contextual_thoughts['position'], screen.get_width() - 200, 80)

            # Bubble background
            bubble_surface = pygame.Surface((thought_rect.width, thought_rect.height), pygame.SRCALPHA)
            alpha = self.contextual_thoughts['fade_alpha']
            bubble_surface.fill((20, 30, 45, int(alpha * 0.9)))

            # Bubble border
            pygame.draw.rect(bubble_surface, (100, 150, 200, int(alpha * 0.8)),
                           (0, 0, thought_rect.width, thought_rect.height), 2, border_radius=15)

            screen.blit(bubble_surface, (thought_rect.x, thought_rect.y))

            # Thought text
            font = pygame.font.Font(None, 28)
            text_color = (255, 255, 255, alpha)

            # Word wrap the text
            words = self.contextual_thoughts['text'].split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if font.size(test_line)[0] < thought_rect.width - 30:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw text lines
            text_y = thought_rect.y + 15
            for line in lines:
                text_surface = font.render(line, True, text_color[:3])
                text_surface.set_alpha(alpha)
                text_x = thought_rect.x + 15
                screen.blit(text_surface, (text_x, text_y))
                text_y += 25
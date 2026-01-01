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

        # Track rental sequence progress
        self.reality_checks_completed = set()
        self.required_checks = {'wallet_check', 'phone_check', 'application_form'}
        self.phone_call_triggered = False

        # Exit timer for auto-transitions
        self.should_exit = False
        self.exit_timer = 0

        # Office atmosphere
        self.waiting_count = 8  # Other people waiting
        self.frustration_level = 0
        self.hope_meter = 100

        # CRITICAL: Reload narrative content after full initialization
        # The parent __init__ calls load_narrative_content() before our override exists
        self.narrative_content = self.load_narrative_content()

        # Dialogue sequence handling for multi-line interactions
        self.pending_dialogue = []
        self.current_dialogue_index = 0

        # Auto-reload prevention
        self.is_reloading = False

        # Track whether we've shown the call_foster_parents dialogue
        self.call_dialogue_shown = False

    def enter(self):
        """Override enter to set up housing office scene"""
        super().enter()

        # Reset reload flag
        self.is_reloading = False
        print(f"[HOUSING_OFFICE] enter() called")

        # Track previous objective to detect changes
        previous_objective = getattr(self, '_previous_objective_id', None)

        # Check which objective we're on
        current = self.game.objective_manager.get_current_objective()
        print(f"[HOUSING_OFFICE] Current objective: {current.id if current else 'None'}")
        print(f"[HOUSING_OFFICE] Previous objective: {previous_objective}")

        if current:
            # Clear old interactions if objective changed in rental sequence
            rental_sequence = ['found_listing', 'application_barriers', 'your_reality', 'call_foster_parents', 'first_rejection']
            if previous_objective in rental_sequence and current.id in rental_sequence and previous_objective != current.id:
                print(f"[HOUSING_OFFICE]   CLEARING old interactions (objective changed from {previous_objective} to {current.id})")
                self.interactive_objects.clear()
                self.completed_interactions.clear()
                self.reality_checks_completed.clear()
                # Reset call_foster_parents dialogue flag when leaving that objective (but not when reloading within it)
                if previous_objective == 'call_foster_parents' and current.id != 'call_foster_parents':
                    self.call_dialogue_shown = False
                    print(f"[HOUSING_OFFICE]   Reset call_dialogue_shown flag")

            # Update previous objective tracker
            self._previous_objective_id = current.id

            # === RENTAL SEQUENCE ===
            if current.id == 'your_reality':
                # Add reality check interactions
                print(f"[HOUSING_OFFICE]   Setting up your_reality interactions")
                interactions = self.narrative_content['your_reality']['interactions']
                for obj_name in ['wallet_check', 'phone_check', 'application_form']:
                    if obj_name in interactions:
                        print(f"[HOUSING_OFFICE]     Adding {obj_name}")
                        self.add_interactive_object(obj_name, interactions[obj_name])
                print(f"[HOUSING_OFFICE]     Interactive objects now: {list(self.interactive_objects.keys())}")

            elif current.id == 'call_foster_parents':
                # Two-phase handling: First show dialogue, then show phone interaction
                print(f"[HOUSING_OFFICE]   Setting up call_foster_parents")
                print(f"[HOUSING_OFFICE]     call_dialogue_shown: {self.call_dialogue_shown}")
                print(f"[HOUSING_OFFICE]     previous_objective: {previous_objective}")

                # CRITICAL: If coming from your_reality, skip dialogue and go directly to phone interaction
                if previous_objective == 'your_reality':
                    print(f"[HOUSING_OFFICE]     COMING FROM your_reality - SKIP TO PHASE 2")
                    self.call_dialogue_shown = True

                    # CRITICAL: Clear any existing activity to allow E key interactions
                    if hasattr(self, 'current_activity') and self.current_activity:
                        print(f"[HOUSING_OFFICE]       CLEARING existing activity: {self.current_activity}")
                        self.current_activity = None

                    # CRITICAL: Clear narrative state to allow E key interactions
                    self.narrative_active = False
                    self.dialogue_box.hide()
                    print(f"[HOUSING_OFFICE]       CLEARED narrative state - narrative_active: {self.narrative_active}")

                    # Phase 2: Add phone interaction directly
                    print(f"[HOUSING_OFFICE]     Phase 2: Adding phone interaction")
                    interactions = self.narrative_content['call_foster_parents']['interactions']
                    if 'phone_call' in interactions:
                        print(f"[HOUSING_OFFICE]       Adding phone_call interaction at position {interactions['phone_call']['position']}")
                        self.add_interactive_object('phone_call', interactions['phone_call'])
                        print(f"[HOUSING_OFFICE]       Interactive objects now: {list(self.interactive_objects.keys())}")
                        # CRITICAL: Skip check_for_objective_narrative() to prevent dialogue restart
                        print(f"[HOUSING_OFFICE]       Skipping check_for_objective_narrative() - phone added")
                        self.update_objective_display()
                        return  # Exit early, don't call check_for_objective_narrative()
                    else:
                        print(f"[HOUSING_OFFICE]       ERROR: phone_call not found in interactions!")

                elif not self.call_dialogue_shown:
                    # Phase 1: Show dialogue only, don't add interaction yet
                    print(f"[HOUSING_OFFICE]     Phase 1: Showing dialogue only")
                    print(f"[HOUSING_OFFICE]     Dialogue already started by parent check_for_objective_narrative()")
                    # Don't manually start again - parent already started it
                else:
                    # Phase 2: Add phone interaction (dialogue already shown)
                    print(f"[HOUSING_OFFICE]     Phase 2: Adding phone interaction")
                    interactions = self.narrative_content['call_foster_parents']['interactions']
                    if 'phone_call' in interactions:
                        print(f"[HOUSING_OFFICE]       Adding phone_call interaction at position {interactions['phone_call']['position']}")
                        self.add_interactive_object('phone_call', interactions['phone_call'])
                        print(f"[HOUSING_OFFICE]       Interactive objects now: {list(self.interactive_objects.keys())}")
                        # CRITICAL: Skip check_for_objective_narrative() to prevent dialogue restart
                        print(f"[HOUSING_OFFICE]       Skipping check_for_objective_narrative() - phone added")
                        self.update_objective_display()
                        return  # Exit early, don't call check_for_objective_narrative()
                    else:
                        print(f"[HOUSING_OFFICE]       ERROR: phone_call not found in interactions!")

            # === TLP SEQUENCE ===
            elif current.id == 'learn_about_tlp':
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

    def check_for_objective_narrative(self):
        """Override to handle call_foster_parents Phase 2 correctly"""
        if not hasattr(self.game, 'objective_manager'):
            print("No objective manager found")
            return

        current = self.game.objective_manager.get_current_objective()
        if not current:
            print("No current objective found")
            return

        # Special handling for call_foster_parents Phase 2
        if current.id == 'call_foster_parents' and self.call_dialogue_shown:
            print(f"[HOUSING_OFFICE] check_for_objective_narrative: SKIPPING Phase 2 - dialogue already shown")
            return

        # For all other cases, use parent's behavior
        print(f"[HOUSING_OFFICE] check_for_objective_narrative: Using parent for {current.id}")
        super().check_for_objective_narrative()

    def start_narrative_sequence(self, objective_id):
        """Override to add debugging"""
        print(f"[HOUSING_OFFICE] start_narrative_sequence({objective_id})")
        super().start_narrative_sequence(objective_id)
        print(f"[HOUSING_OFFICE]   sequence_start_objective_id set to: {self.sequence_start_objective_id}")
        print(f"[HOUSING_OFFICE]   narrative_active: {self.narrative_active}")
        print(f"[HOUSING_OFFICE]   current_sequence length: {len(self.current_sequence)}")
        print(f"[HOUSING_OFFICE]   NPCs added: {list(self.npcs.keys())}")
        print(f"[HOUSING_OFFICE]   dialogue_box.active: {self.dialogue_box.active}")

    def show_next_dialogue(self):
        """Override to add debugging"""
        current = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        print(f"[HOUSING_OFFICE] show_next_dialogue() - index: {self.sequence_index}/{len(self.current_sequence)}")
        print(f"[HOUSING_OFFICE]   Current objective: {current.id if current else 'None'}")
        print(f"[HOUSING_OFFICE]   call_dialogue_shown: {self.call_dialogue_shown}")

        # CRITICAL DEBUG: Check if we're about to complete call_foster_parents
        if current and current.id == 'call_foster_parents' and self.sequence_index >= len(self.current_sequence) - 1:
            print(f"[HOUSING_OFFICE]   >>> ABOUT TO COMPLETE call_foster_parents DIALOGUE <<<")
            print(f"[HOUSING_OFFICE]   >>> sequence_index={self.sequence_index}, sequence_length={len(self.current_sequence)} <<<")

        super().show_next_dialogue()

        if self.sequence_index >= len(self.current_sequence):
            print(f"[HOUSING_OFFICE]   *** SEQUENCE COMPLETE - end_narrative_sequence() will be called next ***")
            # CRITICAL DEBUG: For call_foster_parents, ensure end_narrative_sequence is called
            if current and current.id == 'call_foster_parents':
                print(f"[HOUSING_OFFICE]   >>> CALLING end_narrative_sequence() FOR call_foster_parents <<<")

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
            },

            # === RENTAL APARTMENT SEQUENCE ===
            # When youth try private rental before learning about TLP

            'found_listing': {
                'npcs': [
                    {'name': 'Housing Counselor', 'x': 8, 'y': 4},
                    {'name': 'Hopeful Youth', 'x': 5, 'y': 6}
                ],
                'dialogue_sequence': [
                    (None, "You rush into the housing office with a crumpled printout."),
                    ("You", "I found a studio apartment! $1,400 a month. Can you help me apply?"),
                    ("Housing Counselor", "Oh honey... private market rental? Let me guess - online listing?"),
                    ("You", "Yeah! It's the cheapest I could find. It's perfect!"),
                    ("Housing Counselor", "*sighs* Sit down. We need to talk about requirements."),
                    ("Hopeful Youth", "I had the same idea last month. Didn't go well."),
                    (None, "The counselor pulls out a standard rental application form."),
                    (None, "Your optimism starts to crack.")
                ],
                'interactions': {}
            },

            'application_barriers': {
                'npcs': [
                    {'name': 'Housing Counselor', 'x': 8, 'y': 4},
                    {'name': 'Hopeful Youth', 'x': 5, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Housing Counselor", "Income requirement: Three times monthly rent. That's $4,200 monthly."),
                    ("You", "$4,200?! But minimum wage is only..."),
                    ("Housing Counselor", "About 70 hours a week. Yeah, the math doesn't work."),
                    ("Housing Counselor", "Credit score: 650 minimum. No credit history counts as bad credit."),
                    ("You", "I don't even have a credit card yet..."),
                    ("Housing Counselor", "Co-signer required with income over $50,000 and 700+ credit."),
                    ("Housing Counselor", "Plus first month, last month, security deposit: $4,200 upfront."),
                    ("Hopeful Youth", "I tried five places. All the same requirements."),
                    (None, "Each requirement feels like another wall being built."),
                    (None, "The system was never designed for people like you.")
                ],
                'interactions': {}
            },

            'your_reality': {
                'npcs': [
                    {'name': 'Housing Counselor', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "The counselor gives you space to process the information."),
                    ("Housing Counselor", "I know it's a lot. Take your time to check what you have."),
                    ("You", "(thinking) Maybe... maybe there's something I missed?"),
                    (None, "Deep down, you already know the answer.")
                ],
                'interactions': {
                    'wallet_check': {
                        'position': (7, 8),
                        'prompt': 'Check wallet',
                        'dialogue': [
                            "You pull out your worn wallet. Three twenties, a ten, three ones.",
                            "$73. That's literally everything you own.",
                            "The $4,200 deposit might as well be $4.2 million.",
                            "The counselor watches with practiced sympathy.",
                            "She's seen this heartbreak before."
                        ],
                        'required': True
                    },
                    'phone_check': {
                        'position': (9, 8),
                        'prompt': 'Check phone',
                        'dialogue': [
                            "Cracked screen, 8% battery, no missed calls.",
                            "Contacts: Few old classmates, shelter hotline, that's it.",
                            "Foster parents' number is still there...",
                            "Should you try calling them?",
                            "What's the worst they could say? No?"
                        ],
                        'required': True
                    },
                    'application_form': {
                        'position': (8, 5),
                        'prompt': 'Review application',
                        'dialogue': [
                            "MONTHLY INCOME: $_________ (You have: $0)",
                            "CREDIT SCORE: _________ (You have: No history)",
                            "CO-SIGNER: _________ (You have: Nobody)",
                            "EMPLOYER: _________ (You have: Unemployed)",
                            "PREVIOUS LANDLORD: _________ (You have: Foster care)",
                            "BANK STATEMENTS: _________ (You have: $73)",
                            "",
                            "Every blank line mocks you.",
                            "The system wasn't built for foster youth."
                        ],
                        'required': True
                    }
                }
            },

            'call_foster_parents': {
                'npcs': [
                    {'name': 'Housing Counselor', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "The counselor steps away to give you privacy."),
                    ("Housing Counselor", "Take your time. I've seen kids make this call before."),
                    (None, "Your hands shake as you dial the number."),
                    (None, "Maybe they'll help. They have to help... right?")
                ],
                'interactions': {
                    'phone_call': {
                        'position': (8, 9),
                        'prompt': 'Call foster parents',
                        'trigger_activity': 'foster_parent_call',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'first_rejection': {
                'npcs': [
                    {'name': 'Housing Counselor', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You hang up the phone. The counselor returns."),
                    ("Housing Counselor", "I heard. I'm sorry."),
                    ("You", "Seven years... and they just... hung up."),
                    ("Housing Counselor", "I wish I could say that was unusual."),
                    ("You", "So I can't rent this apartment?"),
                    ("Housing Counselor", "Not this one. Not any private rental."),
                    ("Housing Counselor", "But there are other options. Let me tell you about TLP."),
                    (None, "Another program, another waitlist, another hope to be crushed."),
                    (None, "But what choice do you have?")
                ],
                'interactions': {}
            }
        }

    def update_objective_display(self):
        """Update objective text based on housing office progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # === RENTAL SEQUENCE OBJECTIVES ===
        if current.id == 'found_listing':
            if self.narrative_active and self.sequence_index < 6:
                current.dynamic_description = "Sharing your exciting discovery..."
            else:
                current.dynamic_description = "Reality check incoming..."

        elif current.id == 'application_barriers':
            if self.narrative_active:
                if self.sequence_index < 5:
                    current.dynamic_description = "Learning about income requirements..."
                else:
                    current.dynamic_description = "The system works against you..."

        elif current.id == 'your_reality':
            checks = len(self.reality_checks_completed)
            if checks < 3:
                current.dynamic_description = f"Face your reality ({checks}/3 checks)"
                remaining = self.required_checks - self.reality_checks_completed
                current.progress_text = f"Check: {', '.join(list(remaining)[:2])}"
            else:
                current.dynamic_description = "The truth is undeniable..."
                current.progress_text = "Maybe call for help?"

        elif current.id == 'call_foster_parents':
            if not self.phone_call_triggered:
                current.dynamic_description = "Make a desperate call..."
                current.progress_text = "Use your phone"
            else:
                current.dynamic_description = "Processing the rejection..."

        elif current.id == 'first_rejection':
            if self.narrative_active:
                current.dynamic_description = "Facing the truth..."
            else:
                current.dynamic_description = "Private rental impossible"

        # === TLP SEQUENCE OBJECTIVES ===
        elif current.id == 'learn_about_tlp':
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

    def end_narrative_sequence(self):
        """Override to chain housing office objectives with auto-reload"""
        print(f"")
        print(f"="*80)
        print(f"[HOUSING_OFFICE] *** end_narrative_sequence() CALLED ***")
        print(f"[HOUSING_OFFICE]   is_reloading: {self.is_reloading}")
        print(f"[HOUSING_OFFICE]   call_dialogue_shown: {self.call_dialogue_shown}")
        print(f"[HOUSING_OFFICE]   sequence_start_objective_id: {self.sequence_start_objective_id}")

        # Prevent infinite loops
        if self.is_reloading:
            print(f"[HOUSING_OFFICE] Already reloading, returning early")
            print(f"="*80)
            return

        current = self.game.objective_manager.get_current_objective()
        print(f"[HOUSING_OFFICE]   current objective: {current.id if current else 'None'}")
        print(f"="*80)

        if not current:
            # Only hide if no current objective
            self.narrative_active = False
            self.dialogue_box.hide()
            print(f"[HOUSING_OFFICE] No current objective, hiding dialogue")
            return

        # Chain rental sequence objectives - KEEP dialogue active
        if current.id == 'found_listing':
            print("[HOUSING_OFFICE] Completing found_listing, moving to application_barriers")
            # Set should_exit temporarily so objective manager will accept completion
            print(f"[HOUSING_OFFICE]   Setting should_exit = True")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            print(f"[HOUSING_OFFICE]   Resetting should_exit = False")
            self.should_exit = False  # Reset immediately

            next_obj = self.game.objective_manager.get_current_objective()
            print(f"[HOUSING_OFFICE]   Next objective: {next_obj.id if next_obj else 'None'}")

            if next_obj and next_obj.id == 'application_barriers':
                print("[HOUSING_OFFICE]   Auto-reloading room for application_barriers")
                self.is_reloading = True
                self.dialogue_box.hide()
                self.narrative_active = False
                # Reload the room to get fresh content
                self.enter()
                return

        elif current.id == 'application_barriers':
            print("[HOUSING_OFFICE] Completing application_barriers, moving to your_reality")
            # Set should_exit temporarily so objective manager will accept completion
            print(f"[HOUSING_OFFICE]   Setting should_exit = True")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            print(f"[HOUSING_OFFICE]   Resetting should_exit = False")
            self.should_exit = False  # Reset immediately

            next_obj = self.game.objective_manager.get_current_objective()
            print(f"[HOUSING_OFFICE]   Next objective: {next_obj.id if next_obj else 'None'}")

            if next_obj and next_obj.id == 'your_reality':
                print("[HOUSING_OFFICE]   Auto-reloading room for your_reality")
                self.is_reloading = True
                self.dialogue_box.hide()
                self.narrative_active = False
                # Reload the room to get fresh interactions
                self.enter()
                return

        elif current.id == 'call_foster_parents':
            # Special handling: Dialogue just ended, now reload to show phone interaction
            print("[HOUSING_OFFICE] *** REACHED call_foster_parents BRANCH ***")
            print(f"[HOUSING_OFFICE]   call_dialogue_shown = {self.call_dialogue_shown}")
            print(f"[HOUSING_OFFICE]   is_reloading = {self.is_reloading}")
            print(f"[HOUSING_OFFICE]   narrative_active = {self.narrative_active}")

            if not self.call_dialogue_shown:
                print("[HOUSING_OFFICE]   >>> TRIGGERING RELOAD TO SHOW PHONE INTERACTION <<<")
                self.call_dialogue_shown = True
                print(f"[HOUSING_OFFICE]   Set call_dialogue_shown = {self.call_dialogue_shown}")
                # Reload room to show phone interaction
                self.is_reloading = True
                self.dialogue_box.hide()
                self.narrative_active = False
                print(f"[HOUSING_OFFICE]   About to call enter() for reload...")
                self.enter()
                print(f"[HOUSING_OFFICE]   Returned from enter(), exiting end_narrative_sequence")
                return
            else:
                # Phone interaction phase - shouldn't reach here unless something's wrong
                print("[HOUSING_OFFICE]   WARNING: Dialogue ended in phase 2 (shouldn't happen)")
                self.narrative_active = False
                self.dialogue_box.hide()

        elif (current and current.id == 'first_rejection') or self.sequence_start_objective_id == 'first_rejection':
            # End of sequence - NOW we can hide dialogue
            self.narrative_active = False
            self.dialogue_box.hide()
            print("[HOUSING_OFFICE] Completing first_rejection, preparing to exit")
            self.should_exit = True
            self.exit_timer = 2.0

        else:
            # For other objectives (your_reality with interactions, etc.)
            # Check if complete, then hide dialogue
            print(f"[HOUSING_OFFICE] Other objective: {current.id}, checking if complete")

            # For learn_about_tlp - complete normally after case worker interaction
            if current.id == 'learn_about_tlp':
                print("[HOUSING_OFFICE]   learn_about_tlp - checking if case worker interaction completed")
                if 'case_worker_desk' in self.completed_interactions:
                    print("[HOUSING_OFFICE]   Case worker interaction completed - completing objective and exiting")
                    self.narrative_active = False
                    self.dialogue_box.hide()
                    # Set should_exit so the objective manager advances properly
                    self.should_exit = True
                    self.exit_timer = 2.0
                    self.game.objective_manager.complete_current_objective()
                    return
                else:
                    print("[HOUSING_OFFICE]   Case worker interaction not yet completed - hiding dialogue only")
                    self.narrative_active = False
                    self.dialogue_box.hide()
                    return

            if self.check_objective_complete():
                print("[HOUSING_OFFICE]   Objective complete, hiding dialogue")
                self.narrative_active = False
                self.dialogue_box.hide()
                self.game.objective_manager.complete_current_objective()

    def interact_with_object(self, name):
        """Handle interactions with special handling for activities"""
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'learn_about_tlp'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # === RENTAL SEQUENCE INTERACTIONS ===
            # Handle reality check interactions
            if name in self.required_checks:
                print(f"[HOUSING_OFFICE] Reality check interaction: {name}")
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
                print(f"[HOUSING_OFFICE]   Checks completed: {self.reality_checks_completed}")
                print(f"[HOUSING_OFFICE]   Required checks: {self.required_checks}")

                # Check if all reality checks done
                if self.reality_checks_completed == self.required_checks:
                    print(f"[HOUSING_OFFICE]   ALL REALITY CHECKS COMPLETE!")
                    # Complete your_reality and transition to call_foster_parents
                    print(f"[HOUSING_OFFICE]   Completing your_reality, moving to call_foster_parents")
                    print(f"[HOUSING_OFFICE]   Setting should_exit = True")
                    self.should_exit = True
                    self.game.objective_manager.complete_current_objective()
                    print(f"[HOUSING_OFFICE]   Resetting should_exit = False")
                    self.should_exit = False

                    next_obj = self.game.objective_manager.get_current_objective()
                    print(f"[HOUSING_OFFICE]   Next objective: {next_obj.id if next_obj else 'None'}")

                    if next_obj and next_obj.id == 'call_foster_parents':
                        print("[HOUSING_OFFICE]   IMMEDIATELY reloading room for call_foster_parents")
                        # Immediately reload - no timer delay
                        self.is_reloading = True
                        self.dialogue_box.hide()
                        self.narrative_active = False
                        self.enter()
                        return

                self.update_objective_display()
                return

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            if trigger == 'foster_parent_call':
                print(f"[HOUSING_OFFICE] Launching foster_parent_call activity")
                self.launch_foster_parent_call()
                self.phone_call_triggered = True
                print(f"[HOUSING_OFFICE]   phone_call_triggered set to True")
                return
            elif trigger == 'tlp_application':
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

    def launch_foster_parent_call(self):
        """Launch the foster parent phone call activity"""
        try:
            from src.activities.foster_parent_call import FosterParentCall

            print(f"[HOUSING_OFFICE] Launching foster parent call activity...")

            # Create and start the activity
            if hasattr(self.game, 'objective_manager'):
                activity = FosterParentCall(self.game.objective_manager)
                activity.narrative_ref = self  # Pass reference to this interior

                print(f"[HOUSING_OFFICE] Created activity, starting...")
                activity.start()

                print(f"[HOUSING_OFFICE] Activity started, setting as current...")

                # Set as current activity
                self.game.objective_manager.current_activity = activity
                self.current_activity = activity

                print(f"[HOUSING_OFFICE] Foster parent call activity launched successfully")
            else:
                print(f"[HOUSING_OFFICE] ERROR: No objective_manager found")

        except Exception as e:
            print(f"[HOUSING_OFFICE] ERROR launching foster parent call: {e}")
            import traceback
            traceback.print_exc()
            # Mark as completed to prevent getting stuck
            self.phone_call_triggered = True

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

        # Also set in game directly for rendering
        if hasattr(self.game, 'current_activity'):
            self.game.current_activity = activity

    def handle_event(self, event):
        """Handle events with activity priority"""
        # CRITICAL: Handle ESC key properly during phone call activity
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # If phone call activity is active, complete it properly instead of just exiting
            if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
                current_obj = self.game.objective_manager.get_current_objective()
                if current_obj and current_obj.id == 'call_foster_parents':
                    print(f"[HOUSING_OFFICE] ESC pressed during phone call - completing activity properly")
                    # Mark the activity as completed
                    self.current_activity.completed = True
                    self.current_activity.active = False
                    # Trigger the completion flow
                    self.handle_activity_completion()
                    return

            print(f"[HOUSING_OFFICE] ESC pressed - forcing exit")
            self.active = False
            return

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

        # Handle dialogue sequence advancement with SPACE or E
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_SPACE or event.key == pygame.K_e):
                if hasattr(self, 'pending_dialogue') and self.pending_dialogue:
                    if self.current_dialogue_index < len(self.pending_dialogue):
                        # Show next dialogue line
                        self.dialogue_box.show(None, self.pending_dialogue[self.current_dialogue_index])
                        self.current_dialogue_index += 1
                        return
                    elif self.current_dialogue_index >= len(self.pending_dialogue):
                        # Dialogue sequence complete
                        self.pending_dialogue = []
                        self.current_dialogue_index = 0
                        self.dialogue_box.hide()
                        return

        # Use parent's event handling
        super().handle_event(event)

    def handle_activity_completion(self):
        """Handle proper completion of activities and trigger next narrative"""
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj and current_obj.id == 'call_foster_parents':
            print(f"[HOUSING_OFFICE] Phone call completed - transitioning to first_rejection")
            # Mark as completed and advance to first_rejection
            self.phone_call_triggered = True

            # Complete the current objective
            print(f"[HOUSING_OFFICE]   Completing call_foster_parents, moving to first_rejection")
            self.should_exit = True
            self.game.objective_manager.complete_current_objective()
            self.should_exit = False

            # Get the new objective
            next_obj = self.game.objective_manager.get_current_objective()
            if next_obj and next_obj.id == 'first_rejection':
                print(f"[HOUSING_OFFICE]   IMMEDIATELY reloading room for first_rejection")
                # Clear activity
                self.current_activity = None
                if hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Reload to show first_rejection dialogue
                self.is_reloading = True
                self.dialogue_box.hide()
                self.narrative_active = False
                self.enter()

    def handle_auto_progression(self):
        """Custom auto-progression that stays inside for consecutive housing office objectives"""
        # Check if objective is complete
        if not self.check_completion_status():
            return  # Not complete yet

        if self.completion_triggered:
            return  # Already handled

        # Mark as triggered
        self.completion_triggered = True

        # Show completion message
        self.show_objective_completion()

        # Get current objective
        current = self.game.objective_manager.get_current_objective()
        if not current:
            # No current objective - just exit normally
            self.start_exit_timer(0.5)
            return

        print(f"[HOUSING_OFFICE] Objective {current.id} complete")

        # Check if next objective is also at housing office
        current_index = self.game.objective_manager.current_objective_index
        next_index = current_index + 1

        if next_index < len(self.game.objective_manager.objectives):
            next_obj = self.game.objective_manager.objectives[next_index]

            # If next objective is at same location (housing office at 27, 52), stay inside
            if next_obj.target_position == (27, 52):
                print(f"[HOUSING_OFFICE] Next objective '{next_obj.id}' is also here - staying inside")

                # Advance to next objective without exiting
                if hasattr(self.game, 'health_manager'):
                    self.game.health_manager.on_objective_complete()
                self.game.objective_manager.advance_to_next_objective()

                # Reset state for next objective
                self.completed_interactions.clear()
                self.narrative_active = False
                self.completion_triggered = False

                # Re-enter for next objective
                self.enter()

                # DON'T call start_exit_timer - stay inside!
                return

        # Next objective is elsewhere OR no more objectives - exit normally
        print(f"[HOUSING_OFFICE] Exiting to continue elsewhere")
        self.start_exit_timer(0.5)

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
                    # Mark interaction completed - let handle_auto_progression() decide whether to exit
                    self.completed_interactions.add('application_computer')

                elif current and current.id == 'waitlist_47':
                    # Waitlist tracking completed
                    self.months_waited = 6
                    self.update_objective_display()
                    self.dialogue_box.show(None, "6 months of hell. But finally... a call.")
                    # Mark interaction completed - let handle_auto_progression() decide whether to exit
                    self.completed_interactions.add('waitlist_board')

                elif current and current.id == 'call_foster_parents':
                    # Foster parent call completed - they said no
                    print(f"[HOUSING_OFFICE] Foster parent call activity completed!")
                    self.phone_call_triggered = True
                    self.update_objective_display()
                    # Complete this objective and transition to first_rejection
                    print(f"[HOUSING_OFFICE]   Completing call_foster_parents, moving to first_rejection")
                    print(f"[HOUSING_OFFICE]   Setting should_exit = True")
                    self.should_exit = True
                    self.game.objective_manager.complete_current_objective()
                    print(f"[HOUSING_OFFICE]   Resetting should_exit = False")
                    self.should_exit = False

                    next_obj = self.game.objective_manager.get_current_objective()
                    print(f"[HOUSING_OFFICE]   Next objective: {next_obj.id if next_obj else 'None'}")

                    if next_obj and next_obj.id == 'first_rejection':
                        print("[HOUSING_OFFICE]   IMMEDIATELY reloading room for first_rejection")
                        # Immediately reload to show rejection dialogue
                        self.is_reloading = True
                        self.dialogue_box.hide()
                        self.narrative_active = False
                        self.enter()
                        # Note: enter() will trigger start_narrative_sequence('first_rejection')
                        return

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                print(f"[HOUSING_OFFICE] Exit timer expired, is_reloading={self.is_reloading}")
                # Check if we're reloading or actually exiting
                if self.is_reloading:
                    print(f"[HOUSING_OFFICE]   Reloading room instead of exiting")
                    # Reset flags and reload
                    self.should_exit = False
                    self.dialogue_box.hide()
                    self.narrative_active = False
                    self.enter()
                else:
                    print(f"[HOUSING_OFFICE]   Actually exiting interior")
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
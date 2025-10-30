"""
Grocery Store Interior with Job Search and Income Reality Narrative
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class GroceryStoreNarrative(NarrativeInterior):
    """Grocery store with job application and income calculation narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track job search progress
        self.applied_count = 0
        self.got_hired = False
        self.income_calculated = False
        self.budget_reviewed = False
        self.savings_calculated = False
        self.reality_accepted = False
        self.current_activity = None

        # Exit timer for auto-transitions
        self.should_exit = False
        self.exit_timer = 0

    def enter(self):
        """Override enter to set up grocery store scene"""
        super().enter()

        # Check which objective we're on
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'job_search':
                # Add application kiosk immediately
                interactions = self.narrative_content['job_search']['interactions']
                if 'application_kiosk' in interactions:
                    self.add_interactive_object('application_kiosk', interactions['application_kiosk'])
                    if 'application_kiosk' in self.completed_interactions:
                        self.completed_interactions.remove('application_kiosk')

            elif current.id == 'income_math':
                # Add calculator station
                interactions = self.narrative_content['income_math']['interactions']
                if 'break_room' in interactions:
                    self.add_interactive_object('break_room', interactions['break_room'])

            elif current.id == 'expense_reality':
                # Add budget notebook
                interactions = self.narrative_content['expense_reality']['interactions']
                if 'budget_notebook' in interactions:
                    self.add_interactive_object('budget_notebook', interactions['budget_notebook'])

            elif current.id == 'savings_rate':
                # Add savings calculator
                interactions = self.narrative_content['savings_rate']['interactions']
                if 'savings_calculator' in interactions:
                    self.add_interactive_object('savings_calculator', interactions['savings_calculator'])

            elif current.id == 'impossible_math':
                # Add trap visualizer and exit
                interactions = self.narrative_content['impossible_math']['interactions']
                if 'trap_visualizer' in interactions:
                    self.add_interactive_object('trap_visualizer', interactions['trap_visualizer'])
                if 'exit_door' in interactions:
                    self.add_interactive_object('exit_door', interactions['exit_door'])

        self.update_objective_display()

    def load_narrative_content(self):
        """Load the grocery store narrative content"""
        return {
            'job_search': {
                'npcs': [
                    {'name': 'Store Manager', 'x': 17, 'y': 3},
                    {'name': 'Other Applicant', 'x': 13, 'y': 10},
                    {'name': 'Employee', 'x': 5, 'y': 10}
                ],
                'dialogue_sequence': [
                    (None, "Day 47 without stable income. The grocery store is hiring."),
                    ("Other Applicant", "Been here three times this week. They keep saying they'll call."),
                    ("Employee", "We're always 'hiring' but never actually hire. Good luck."),
                    (None, "You approach the application kiosk. Your 48th job application."),
                    ("Store Manager", "Part-time only. No benefits. Can you work ANY hours?"),
                    ("You", "Yes, any hours. I really need this job."),
                    ("Store Manager", "We'll call if interested."),
                    (None, "You've heard that before. But what choice do you have?")
                ],
                'interactions': {
                    'application_kiosk': {
                        'position': (15, 10),
                        'prompt': 'Apply for job',
                        'trigger_activity': 'job_application',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'income_math': {
                'npcs': [
                    {'name': 'Store Manager', 'x': 17, 'y': 3}
                ],
                'dialogue_sequence': [
                    (None, "Miracle! They actually called back. You got the job."),
                    ("Store Manager", "Part-time retail. $15 an hour. 20 hours a week maximum."),
                    ("You", "Can I get more hours?"),
                    ("Store Manager", "We keep everyone under 30 to avoid benefits. Company policy."),
                    (None, "Time to calculate what this actually means for survival.")
                ],
                'interactions': {
                    'break_room': {
                        'position': (18, 7),
                        'prompt': 'Calculate income',
                        'trigger_activity': 'income_calculator',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'expense_reality': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "$1,200 a month. Before taxes. That has to cover everything."),
                    (None, "You pull out your notebook with monthly expenses."),
                    (None, "Time to face the brutal math of poverty.")
                ],
                'interactions': {
                    'budget_notebook': {
                        'position': (10, 7),
                        'prompt': 'Review expenses',
                        'trigger_activity': 'budget_breakdown',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'savings_rate': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "$50 left each month. If nothing goes wrong."),
                    (None, "You need $2,800 for first, last, and deposit on an apartment."),
                    (None, "At $50 per month..."),
                    (None, "The calculator shows: 56 months."),
                    (None, "4.7 YEARS to save for housing."),
                    (None, "If you never get sick. Never miss work. Never have emergencies."),
                    (None, "The math doesn't lie. You're trapped.")
                ],
                'interactions': {
                    'savings_calculator': {
                        'position': (15, 10),
                        'prompt': 'Calculate timeline',
                        'trigger_activity': 'savings_calculator',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'impossible_math': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Can't save while homeless because everything costs more."),
                    (None, "Can't get housing without savings."),
                    (None, "Can't get better job without stable address."),
                    (None, "Can't get stable address without better job."),
                    (None, "The cycle is designed to trap you."),
                    (None, "This isn't about laziness or bad choices."),
                    (None, "The system is working exactly as intended."),
                    (None, "To keep you desperate. To keep wages low."),
                    (None, "To make you grateful for scraps."),
                    (None, "Welcome to the permanent underclass.")
                ],
                'interactions': {
                    'trap_visualizer': {
                        'position': (15, 10),
                        'prompt': 'See the trap',
                        'trigger_activity': 'savings_calculator',
                        'dialogue': None,
                        'required': True
                    },
                    'exit_door': {
                        'position': (9, 14),
                        'prompt': 'Leave store',
                        'dialogue': [
                            "You walk out knowing the truth.",
                            "No amount of hard work will save you.",
                            "Not at $15 an hour.",
                            "Not in this economy.",
                            "The American Dream is a lie.",
                            "For people like you, it always was."
                        ],
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on grocery store progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'job_search':
            if self.narrative_active and self.sequence_index < 4:
                current.dynamic_description = "Another rejection incoming..."
            elif not self.got_hired:
                current.dynamic_description = "Fill out application #48"
                current.progress_text = "Use the kiosk to apply"
            else:
                current.dynamic_description = "You got hired! Part-time only."
                current.progress_text = "Miracle #1"

        elif current.id == 'income_math':
            if not self.income_calculated:
                current.dynamic_description = "Calculate your monthly income"
                current.progress_text = "$15/hour x 20 hours/week"
            else:
                current.dynamic_description = "$1,200/month before taxes"
                current.progress_text = "That's it."

        elif current.id == 'expense_reality':
            if not self.budget_reviewed:
                current.dynamic_description = "Review your monthly expenses"
                current.progress_text = "The brutal math"
            else:
                current.dynamic_description = "$1,150 in expenses. $50 left."
                current.progress_text = "If nothing goes wrong"

        elif current.id == 'savings_rate':
            if not self.savings_calculated:
                current.dynamic_description = "Calculate time to save for apartment"
                current.progress_text = "Do the math"
            else:
                current.dynamic_description = "4.7 YEARS to save $2,800"
                current.progress_text = "Impossible"

        elif current.id == 'impossible_math':
            current.dynamic_description = "The system is rigged"
            current.progress_text = "You can't win"

    def interact_with_object(self, name):
        """Handle grocery store-specific interactions"""
        print(f"DEBUG: Interacting with {name}")
        print(f"DEBUG: Current activity: {self.current_activity}")

        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'job_search'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            if trigger == 'job_application':
                print("DEBUG: Launching job application")
                self.launch_job_application()
                return
            elif trigger == 'income_calculator':
                print("DEBUG: Launching income calculator")
                self.launch_income_calculator()
                return
            elif trigger == 'budget_breakdown':
                print("DEBUG: Launching budget breakdown")
                self.launch_budget_breakdown()
                return
            elif trigger == 'savings_calculator':
                print("DEBUG: Launching savings calculator")
                self.launch_savings_calculator()
                return

        # Handle non-activity interactions
        super().interact_with_object(name)

        self.update_objective_display()

        # Handle exit completion for impossible_math
        if name == 'exit_door' and current_narrative_id == 'impossible_math':
            self.should_exit = True
            self.exit_timer = 3.0

    def launch_job_application(self):
        """Launch the job application mini-game"""
        from src.activities.job_application import JobApplication

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = JobApplication(self.game.objective_manager)
            activity.narrative_ref = self
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def launch_income_calculator(self):
        """Launch the income calculator activity"""
        from src.activities.income_calculator import IncomeCalculator

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = IncomeCalculator(self.game)
        activity.narrative_ref = self
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity

    def launch_budget_breakdown(self):
        """Launch the budget breakdown activity"""
        from src.activities.budget_breakdown import BudgetBreakdown

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = BudgetBreakdown(self.game)
        activity.narrative_ref = self
        activity.start()
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity

    def launch_savings_calculator(self):
        """Launch the savings calculator activity"""
        from src.activities.savings_calculator import SavingsCalculator

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = SavingsCalculator(self.game)
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
            print(f"DEBUG: Activity is active, blocking other events")
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
                if current and current.id == 'job_search':
                    # Job application completed
                    self.got_hired = True
                    self.applied_count = 48
                    self.update_objective_display()
                    self.dialogue_box.show("Store Manager", "Congratulations! You start tomorrow. Part-time.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                elif current and current.id == 'income_math':
                    # Income calculation completed
                    self.income_calculated = True
                    self.update_objective_display()
                    self.dialogue_box.show(None, "$1,200 a month. That's your lifeline.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                elif current and current.id == 'expense_reality':
                    # Budget breakdown completed
                    self.budget_reviewed = True
                    self.update_objective_display()
                    self.dialogue_box.show(None, "$50 left each month. If you're lucky.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                elif current and current.id == 'savings_rate':
                    # Savings calculation completed
                    self.savings_calculated = True
                    self.update_objective_display()
                    self.dialogue_box.show(None, "4.7 years to save. The math doesn't lie.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                elif current and current.id == 'impossible_math':
                    # Trap visualization completed
                    self.reality_accepted = True
                    self.update_objective_display()
                    self.dialogue_box.show(None, "The system is working exactly as designed.")
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

                # Check if we need to auto-transition
                next_obj = self.game.objective_manager.get_current_objective()
                if next_obj and next_obj.id in ['income_math', 'expense_reality', 'savings_rate', 'impossible_math']:
                    # Stay in grocery store for next calculation
                    self.should_exit = False
                    self.enter()  # Re-enter to set up next phase
                else:
                    # Exit the interior
                    self.active = False

    def draw(self, screen):
        """Draw grocery store interior with activity overlay"""
        # Draw base interior
        super().draw(screen)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return

        # Draw status in corner
        current = self.game.objective_manager.get_current_objective()
        if current:
            font = pygame.font.Font(None, 24)

            if current.id == 'job_search' and self.got_hired:
                status_text = "✓ Hired! Part-time retail"
                status_surf = font.render(status_text, True, (100, 255, 100))
                screen.blit(status_surf, (10, 10))

            elif current.id == 'income_math' and self.income_calculated:
                status_text = "Monthly Income: $1,200"
                status_surf = font.render(status_text, True, (255, 220, 100))
                screen.blit(status_surf, (10, 10))

            elif current.id == 'expense_reality' and self.budget_reviewed:
                status_text = "Monthly Savings: $50"
                status_surf = font.render(status_text, True, (255, 100, 100))
                screen.blit(status_surf, (10, 10))

            elif current.id == 'savings_rate':
                status_text = "Time to save $2,800: 4.7 YEARS"
                status_surf = font.render(status_text, True, (255, 50, 50))
                screen.blit(status_surf, (10, 10))
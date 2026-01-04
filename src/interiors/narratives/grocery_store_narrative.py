"""
Your workplace - where you struggle to earn enough
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class GroceryStoreNarrative(NarrativeInterior):
    """grocery_store with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None
        self.should_exit = False
        self.exit_timer = 0.0

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/grocery_store.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'still_not_enough': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You pull out your calculator at the break room table."),
                    (None, "Saved so far: $1,800"),
                    (None, "Apartment needs: First month ($1,400) + Last month ($1,400) + Deposit ($1,400)"),
                    (None, "Total needed: $4,200"),
                    (None, "Still short: $2,400"),
                    (None, "Time left at TLP: 6 months"),
                    (None, "At $100 savings per month, you'll only have $2,400 by then."),
                    (None, "Still $1,800 short of the apartment."),
                    (None, "The math is crushing. You need a miracle or a second job.")
                ],
                'interactions': {
                    'calculator': {
                        'position': (6, 5),
                        'prompt': 'Recalculate desperately',
                        'dialogue': [
                            "Maybe if you skip meals...",
                            "Save $50 more per month on food.",
                            "That's still only $300 in 6 months.",
                            "Maybe a payday loan?",
                            "No, the interest would destroy you.",
                            "Sell plasma twice a week?",
                            "$65 per week = $260/month = $1,560 in 6 months",
                            "That would work! But at what cost to your health?"
                        ],
                        'required': True
                    },
                    'schedule_board': {
                        'position': (8, 3),
                        'prompt': 'Check for extra shifts',
                        'dialogue': [
                            "Scanning the schedule board for any open shifts.",
                            "Holiday shifts: Time and a half pay.",
                            "Overnight stocking: $2 more per hour.",
                            "Weekend doubles: 16-hour shifts available.",
                            "You could work yourself to death and maybe make it.",
                            "Or work yourself to death and still fall short.",
                            "Either way, you're working yourself to death."
                        ],
                        'required': False
                    }
                }
            },
            'second_job_hunt': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("You", "Any chance of more hours? Or overtime?"),
                    ("Manager", "Sorry, company policy. No overtime."),
                    ("Manager", "I can give you 5 more hours a week, max."),
                    ("You", "That's only $75 more. I need another job."),
                    ("Manager", "The diner down the street is hiring night shift."),
                    (None, "Night shift means no sleep."),
                    (None, "But homelessness means no sleep either.")
                ],
                'interactions': {
                    'schedule': {
                        'position': (8, 6),
                        'prompt': 'Check work schedule',
                        'dialogue': ["Current: 20 hours/week", "Maximum: 25 hours/week", "Still not enough to survive."],
                    }
                }
            },
            'exhaustion_sets_in': {
                'npcs': [
                    {'name': 'Coworker', 'x': 6, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Coworker", "You okay? You look exhausted."),
                    ("You", "Working 60 hours between two jobs."),
                    ("Coworker", "That's not sustainable."),
                    ("You", "Neither is homelessness."),
                    (None, "You're falling asleep standing up."),
                    (None, "Making mistakes. Getting complaints."),
                    (None, "But what choice do you have?")
                ],
                'interactions': {}
            },
            'promotion_earned': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Manager", "I have good news. You're being promoted to shift lead."),
                    ("You", "Really? What does that mean?"),
                    ("Manager", "$2 more per hour. More responsibility."),
                    ("Manager", "That's $320 more per month if you work full time."),
                    ("You", "I'll take it! Thank you!"),
                    (None, "It's not much, but it's something."),
                    (None, "Maybe now you can save a little.")
                ],
                'interactions': {
                    'name_tag': {
                        'position': (8, 6),
                        'prompt': 'Put on new name tag',
                        'dialogue': ["'Shift Lead'", "A small step up.", "Every dollar counts."],
                    }
                }
            },

            # === PART 1 OBJECTIVES: Job Search & Income Reality ===
            'job_search_reality': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5},
                    {'name': 'Customer Service', 'x': 12, 'y': 8}
                ],
                'dialogue_sequence': [
                    (None, "You walk into the grocery store, desperate for work."),
                    ("You", "Hi, I'm looking for a job. Are you hiring?"),
                    ("Manager", "Let me guess - no experience, need to start immediately?"),
                    ("You", "I... yes. I really need work."),
                    ("Manager", "We're always hiring. High turnover. $15 an hour, part-time."),
                    ("Manager", "Can you start tomorrow?"),
                    ("You", "Yes! Thank you so much!"),
                    (None, "Finally, a glimmer of hope. Income means independence... right?")
                ],
                'interactions': {
                    'application': {
                        'position': (8, 6),
                        'prompt': 'Fill out application',
                        'trigger_activity': 'job_application',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'income_math': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5},
                    {'name': 'Coworker', 'x': 6, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("You", "So if I work 20 hours a week at $15 an hour..."),
                    ("Coworker", "That's $300 a week, $1,200 a month before taxes."),
                    ("Manager", "Don't forget taxes take about 20%. So $960 take-home."),
                    ("You", "Wait... $960? Not $1,200?"),
                    ("Coworker", "Welcome to the real world, kid."),
                    (None, "The numbers are already getting smaller."),
                    (None, "But $960 is still something, right?")
                ],
                'interactions': {
                    'calculator': {
                        'position': (10, 6),
                        'prompt': 'Use break room calculator',
                        'dialogue': ["20 hours × $15 = $300/week", "× 4 weeks = $1,200/month", "- 20% taxes = $960 take-home"],
                        'required': True
                    }
                }
            },

            'expense_reality': {
                'npcs': [
                    {'name': 'Coworker', 'x': 6, 'y': 6},
                    {'name': 'Older Employee', 'x': 4, 'y': 8}
                ],
                'dialogue_sequence': [
                    ("Coworker", "So what's $960 gonna get you for housing?"),
                    ("You", "I don't know... maybe a studio apartment?"),
                    ("Older Employee", "Hah! Kid thinks $960 covers rent AND food."),
                    ("Coworker", "Let's see... phone $50, food $400, bus pass $120..."),
                    ("Older Employee", "Basic stuff like soap, clothes, laundry... $580 easy."),
                    ("You", "That's... $1,150 total."),
                    ("Coworker", "And you make $960. You're already $190 short."),
                    (None, "The math doesn't work. It was never going to work.")
                ],
                'interactions': {
                    'budget_sheet': {
                        'position': (8, 8),
                        'prompt': 'Look at expense breakdown',
                        'dialogue': ["Phone: $50", "Food: $400", "Transport: $120", "Basics: $580", "Total: $1,150", "Income: $960", "Shortfall: -$190"],
                        'required': True
                    }
                }
            },

            'savings_rate': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5},
                    {'name': 'Coworker', 'x': 6, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("You", "But if I could somehow save just $50 a month..."),
                    ("Manager", "Save? You can't even afford to live on what we pay."),
                    ("Coworker", "But let's pretend. $50 a month for a $2,800 apartment deposit..."),
                    ("Manager", "That's 56 months. Almost 5 years."),
                    ("You", "Five... years?"),
                    ("Coworker", "To save for ONE apartment deposit. While homeless."),
                    (None, "The impossible equation becomes clear."),
                    (None, "The system was never designed for people like you.")
                ],
                'interactions': {
                    'savings_calc': {
                        'position': (10, 6),
                        'prompt': 'Calculate savings timeline',
                        'dialogue': ["$2,800 needed ÷ $50/month = 56 months", "56 months = 4.7 years", "4.7 years of homelessness to afford housing"],
                        'required': True
                    }
                }
            },

            'impossible_math': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5},
                    {'name': 'Coworker', 'x': 6, 'y': 6},
                    {'name': 'Customer', 'x': 12, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Customer", "Can you help me find the organic section?"),
                    ("You", "(thinking) They're buying $200 of groceries without thinking..."),
                    ("Manager", "You okay? You look upset."),
                    ("You", "I can't save money while homeless. Can't get housing without savings."),
                    ("Coworker", "It's a trap. The whole system."),
                    ("Manager", "Why do you think we have such high turnover?"),
                    (None, "Everyone who works here either lives with family or works 3 jobs."),
                    (None, "No one can afford housing on this wage alone."),
                    (None, "You finally understand: it's not a personal failure."),
                    (None, "The system is designed to keep you trapped.")
                ],
                'interactions': {
                    'reality_check': {
                        'position': (8, 6),
                        'prompt': 'Face the truth',
                        'dialogue': ["Can't save while homeless", "Can't get housing without savings", "Minimum wage = maximum exploitation", "The trap is intentional"],
                        'required': True
                    }
                }
            },
        }

    def check_objective_complete(self):
        """Override base class to provide grocery store specific completion logic"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return False

        # Grocery store specific completion conditions
        if current.id == 'job_search_reality':
            # Complete when application is filled out
            return 'application' in self.completed_interactions

        elif current.id == 'income_math':
            # Complete when calculator is used (understanding the math)
            return 'calculator' in self.completed_interactions

        elif current.id == 'expense_reality':
            # Complete when budget sheet is reviewed
            return 'budget_sheet' in self.completed_interactions

        elif current.id == 'savings_rate':
            # Complete when savings calculation is done
            return 'savings_calc' in self.completed_interactions

        elif current.id == 'impossible_math':
            # Complete when reality check is faced
            return 'reality_check' in self.completed_interactions

        # For objectives with only dialogue (no interactions)
        elif current.id in ['still_not_enough', 'second_job_hunt', 'exhaustion_sets_in', 'promotion_earned']:
            # Complete when dialogue sequence is finished
            return not self.narrative_active and self.sequence_index >= len(self.current_sequence)

        # Use base class logic for other objectives
        return super().check_objective_complete()

    def launch_activity(self, activity_name):
        """Launch an activity based on its name"""
        if activity_name == 'job_application':
            self.launch_job_application()
        else:
            super().launch_activity(activity_name)

    def launch_job_application(self):
        """Launch the job application activity with smooth transition"""

        def start_application():
            # Clear any active dialogue
            if hasattr(self, 'dialogue_box'):
                self.dialogue_box.hide()

            # Create and start the job application activity
            from src.activities.job_application import JobApplication
            activity = JobApplication(self.game.objective_manager)
            activity.narrative_ref = self  # Set reference for completion callbacks
            activity.start()
            self.current_activity = activity

            # Set it in the game/objective manager if available
            if hasattr(self.game, 'objective_manager'):
                self.game.objective_manager.current_activity = activity

        # Use professional smooth transition
        self.launch_activity_with_transition(start_application)

    def handle_auto_progression(self):
        """Custom auto-progression that stays inside for consecutive grocery store objectives"""
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

        print(f"[GROCERY] Objective {current.id} complete")

        # Check if next objective is also at grocery store
        current_index = self.game.objective_manager.current_objective_index
        next_index = current_index + 1

        if next_index < len(self.game.objective_manager.objectives):
            next_obj = self.game.objective_manager.objectives[next_index]

            # If next objective is at same location (grocery store at 39, 51), stay inside
            if next_obj.target_position == (39, 51):
                print(f"[GROCERY] Next objective '{next_obj.id}' is also here - staying inside")

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
        print(f"[GROCERY] Exiting to continue elsewhere")
        self.start_exit_timer(0.5)

    def update(self, dt):
        """Update grocery store with activity support"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                # Mark interaction as completed
                self.completed_interactions.add('application')

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

        # Base class handles exit logic via handle_auto_progression() override

    def draw(self, screen):
        """Draw grocery store with activity overlay"""
        # Draw base interior
        super().draw(screen)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)

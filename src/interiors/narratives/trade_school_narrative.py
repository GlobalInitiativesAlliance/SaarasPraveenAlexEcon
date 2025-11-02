"""
Trade School Narrative - Part 2 Studio Apartment Stories
Handles Part 2 housing stability narratives with working mini-games
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class TradeSchoolNarrative(NarrativeInterior):
    """Trade school with Part 2 studio apartment narrative sequences and working mini-games"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None
        self.inspection_results = None  # Store results from inspection activity

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/classroom.json"  # Use classroom layout for trade school

    def load_narrative_content(self):
        """Load Part 2 studio apartment narrative content"""
        return {
            'studio_day_one': {
                'npcs': [
                    {'name': 'Landlord', 'x': 5, 'y': 6},
                    {'name': 'Neighbor', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "You're back in your crappy studio apartment..."),
                    (None, "After all that struggle, this is what you finally got."),
                    ("Landlord", "Rent's due on the first. Don't be late."),
                    ("You", "What about the broken heater you promised to fix?"),
                    ("Landlord", "I'll get to it when I get to it."),
                    (None, "He leaves without another word. You're on your own."),
                    ("Neighbor", "Hey, new tenant? Word of advice - document everything."),
                    ("Neighbor", "Take photos, save texts. You'll need evidence."),
                    ("Neighbor", "And watch out - we've had 3 break-ins this month."),
                    (None, "The apartment is worse than you thought. Roaches scatter as you walk.")
                ],
                'interactions': {
                    'broken_heater': {
                        'position': (3, 8),
                        'prompt': 'Examine broken heater',
                        'dialogue': ["It hasn't worked in months.", "Ice cold to the touch.", "Landlord knew about this."],
                    },
                    'window_locks': {
                        'position': (12, 5),
                        'prompt': 'Check window locks',
                        'dialogue': ["The lock is broken.", "Anyone could get in.", "No wonder there were break-ins."],
                    },
                    'phone': {
                        'position': (7, 7),
                        'prompt': 'Document problems',
                        'trigger_activity': 'document_violations',
                    }
                }
            },

            'document_problems': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Time to build your case. Document everything."),
                    (None, "Take photos of every violation, every broken thing."),
                    (None, "This evidence might save you later.")
                ],
                'interactions': {
                    'camera': {
                        'position': (7, 7),
                        'prompt': 'Start documenting',
                        'trigger_activity': 'document_violations',
                    }
                }
            },

            'first_repair_request': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You text the landlord about the heater."),
                    (None, "He reads it immediately. The 'read' receipt shows."),
                    (None, "No response. Hours pass. Still nothing."),
                    (None, "You'll freeze tonight. Again.")
                ],
                'interactions': {}
            },

            'meet_neighbors': {
                'npcs': [
                    {'name': 'Upstairs Neighbor', 'x': 8, 'y': 5},
                    {'name': 'Next Door Neighbor', 'x': 10, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Upstairs Neighbor", "Welcome to the building. Sorry about the noise."),
                    ("You", "It's okay. The walls are pretty thin."),
                    ("Upstairs Neighbor", "That's not the worst part. Watch your stuff."),
                    ("Next Door Neighbor", "Three break-ins just this month. My bike got stolen."),
                    ("Next Door Neighbor", "Landlord won't fix the security door downstairs."),
                    ("You", "Have you reported it?"),
                    ("Upstairs Neighbor", "We've tried everything. He doesn't care."),
                    (None, "You're starting to understand what you've gotten into.")
                ],
                'interactions': {}
            },

            'first_utility_bill': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The utility bill arrives. You open it nervously."),
                    (None, "$200?! For electricity?!"),
                    (None, "The heat is electric. The insulation is terrible."),
                    (None, "That's one-sixth of your monthly income."),
                    (None, "You weren't told about this when you signed the lease.")
                ],
                'interactions': {
                    'bill': {
                        'position': (7, 6),
                        'prompt': 'Examine bill details',
                        'dialogue': ["Usage: 1800 kWh", "Rate: $0.11/kWh", "Your broken heater is costing you a fortune."],
                    }
                }
            },

            'budget_crisis': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You sit down with a calculator and your bills."),
                    (None, "Rent: $900"),
                    (None, "Utilities: $200"),
                    (None, "Food: $200 minimum"),
                    (None, "Income: $1,200"),
                    (None, "That leaves... negative $100."),
                    (None, "The math doesn't work. It literally doesn't work.")
                ],
                'interactions': {
                    'calculator': {
                        'position': (7, 7),
                        'prompt': 'Run the numbers again',
                        'trigger_activity': 'budget_breakdown',
                    }
                }
            },
        }

    def interact_with_object(self, name):
        """Handle object interactions and launch activities using the working pattern"""
        current = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None

        if not current:
            super().interact_with_object(name)
            return

        # Get interactions for current objective
        interactions = self.narrative_content.get(current.id, {}).get('interactions', {})

        if name not in interactions:
            super().interact_with_object(name)
            return

        interaction = interactions[name]
        trigger = interaction.get('trigger_activity')

        # Launch activity if specified - using the working pattern from studio_apartment_narrative
        if trigger == 'document_violations':
            # Launch apartment inspection activity
            from src.activities.apartment_inspection import ApartmentInspection
            activity = ApartmentInspection(self.game.objective_manager)
            activity.narrative_ref = self
            # Use activity manager to start activity (the working pattern!)
            if hasattr(self.game, 'activity_manager'):
                self.game.activity_manager.start_activity(activity)
            else:
                # Fallback direct launch
                activity.start()
                self.current_activity = activity

        elif trigger == 'budget_breakdown':
            # Launch budget calculator activity
            from src.activities.budget_calculator import BudgetCalculator
            activity = BudgetCalculator(self.game.objective_manager)
            activity.narrative_ref = self
            if hasattr(self.game, 'activity_manager'):
                self.game.activity_manager.start_activity(activity)
            else:
                activity.start()
                self.current_activity = activity

        else:
            # No activity, show dialogue if present
            if interaction.get('dialogue'):
                self.current_sequence = [(None, text) for text in interaction['dialogue']]
                self.sequence_index = 0
                self.show_next_dialogue()

        # Mark interaction as completed
        self.completed_interactions.add(name)

        # Check if all required interactions are complete for this objective
        self.check_objective_completion()

    def check_objective_completion(self):
        """Check if current objective should be completed"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        interactions = self.narrative_content.get(current.id, {}).get('interactions', {})

        # Check if all required interactions are complete
        all_complete = True
        for obj_name, obj_data in interactions.items():
            if obj_data.get('required', False) and obj_name not in self.completed_interactions:
                all_complete = False
                break

        # If specific objectives need special completion logic, handle them here
        if current.id == 'document_problems' and self.inspection_results:
            # Complete if inspection found enough problems
            if self.inspection_results.get('problems_found', 0) >= 4:
                self.game.objective_manager.complete_current_objective()

    def update_objective_display(self):
        """Update the objective display based on current progress"""
        current = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        if not current:
            return

        # Update any HUD elements if needed
        # This is called when entering the room and after interactions
        # Can be extended to update visual indicators or objective status

        # Check if we have completed interactions to show progress
        if hasattr(self, 'completed_interactions'):
            interactions = self.narrative_content.get(current.id, {}).get('interactions', {})
            required_count = sum(1 for i in interactions.values() if i.get('required', False))
            completed_count = sum(1 for name in self.completed_interactions
                                 if name in interactions and interactions[name].get('required', False))

            # Could update a progress indicator here if we had one
            # For now, this just ensures the method exists to prevent AttributeError

    def handle_event(self, event):
        """Handle events - forward to activity if active, otherwise to parent"""
        # If an activity is active, forward events to it
        if self.current_activity and hasattr(self.current_activity, 'active') and self.current_activity.active:
            if hasattr(self.current_activity, 'handle_event'):
                self.current_activity.handle_event(event)
                return  # Don't process further if activity handled it

        # Otherwise use parent's event handling for narrative
        super().handle_event(event)

    def update(self, dt):
        """Update interior including any active activities"""
        super().update(dt)

        # Update current activity if one is active
        if self.current_activity and hasattr(self.current_activity, 'active'):
            if self.current_activity.active:
                self.current_activity.update(dt)
            else:
                # Activity completed
                self.current_activity = None

    def draw(self, screen):
        """Draw interior or active activity"""
        # If an activity is active, draw it instead of the normal interior
        if self.current_activity and hasattr(self.current_activity, 'active') and self.current_activity.active:
            self.current_activity.draw(screen)
        else:
            # Draw normal interior
            super().draw(screen)
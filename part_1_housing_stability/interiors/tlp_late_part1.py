"""
TLP Housing Late Stage - Clean Single-Purpose Interior
Handles ONLY the 'eighteen_months' objective where player is near TLP time limit
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class TLPHousingLateStage(NarrativeInterior):
    """TLP housing late stage - single objective only"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

    def enter(self):
        """Override enter to set up TLP late stage scene"""
        super().enter()

        # Add interactions for eighteen_months
        interactions = self.narrative_content['eighteen_months']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)

        # Start the narrative sequence
        self.start_narrative_sequence('eighteen_months')

    def load_narrative_content(self):
        """Load ONLY the TLP late stage narrative content"""
        return {
            'eighteen_months': {
                'npcs': [
                    {'name': 'Stressed Roommate', 'x': 12, 'y': 8}
                ],
                'dialogue_sequence': [
                    (None, "18 months at the TLP. 6 months left."),
                    (None, "You've been working. Saving. Going to community college."),
                    (None, "Bank account: $1,800 saved."),
                    (None, "But apartments still need first, last, and deposit."),
                    (None, "That's $4,200 for a $1,400 apartment."),
                    (None, "You're $2,400 short. With 6 months left."),
                    (None, "The clock is ticking.")
                ],
                'interactions': {
                    'savings_book': {
                        'position': (8, 5),
                        'prompt': 'Check savings',
                        'dialogue': [
                            "Your savings record book.",
                            "18 months of saving $100/month.",
                            "Total saved: $1,800",
                            "Needed for apartment: $4,200",
                            "Still need: $2,400",
                            "Time remaining at TLP: 6 months",
                            "The math doesn't work."
                        ],
                        'required': True
                    },
                    'calendar': {
                        'position': (5, 3),
                        'prompt': 'Check calendar',
                        'dialogue': [
                            "Month 18 of 24 at TLP.",
                            "Red X marks: 6 months remaining.",
                            "You've circled apartment viewing dates.",
                            "All crossed out - 'Need more savings'",
                            "The deadline approaches."
                        ],
                        'required': False
                    },
                    'termination_notice': {
                        'position': (10, 7),
                        'prompt': 'Read notice',
                        'dialogue': [
                            "TLP TERMINATION NOTICE",
                            "Resident must vacate by: 6 months from today",
                            "Reason: Maximum stay period reached",
                            "Housing assistance available: None",
                            "You knew this day was coming..."
                        ],
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on TLP late stage progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'eighteen_months':
            if self.narrative_active:
                current.dynamic_description = "Checking your savings progress..."
            else:
                current.dynamic_description = "Still $2,400 short with 6 months left"
                current.progress_text = "Check your savings book"

    def interact_with_object(self, name):
        """Handle interactions for eighteen_months objective"""
        super().interact_with_object(name)
        self.update_objective_display()

    def show_next_dialogue(self):
        """Override to update objective during dialogue"""
        super().show_next_dialogue()
        self.update_objective_display()

    def end_narrative_sequence(self):
        """Override to update when narrative ends"""
        super().end_narrative_sequence()
        self.update_objective_display()

    def handle_event(self, event):
        """Handle events with completion checking"""
        super().handle_event(event)

        # Check if objective should be completed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            current = self.game.objective_manager.get_current_objective()
            if current and current.id == 'eighteen_months':
                # Check if requirements met
                if 'savings_book' in self.completed_interactions and not self.narrative_active:
                    self.game.objective_manager.complete_current_objective()
                    self.active = False
                else:
                    self.dialogue_box.show(None, "You need to face reality. Check your savings book.")
                    return

    def draw(self, screen):
        """Draw the TLP housing late stage interior"""
        super().draw(screen)

        # Draw pressure indicators
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'eighteen_months' and not self.narrative_active:
            font = pygame.font.Font(None, 24)

            # Show pressure indicators
            pressure_text = font.render("PRESSURE: Time running out", True, (255, 100, 100))
            screen.blit(pressure_text, (50, 100))

            # Show savings shortfall
            shortfall_text = font.render("Shortfall: $2,400", True, (255, 200, 100))
            screen.blit(shortfall_text, (50, 130))

            # Show countdown
            countdown_text = font.render("Time left: 6 months", True, (255, 150, 150))
            screen.blit(countdown_text, (50, 160))
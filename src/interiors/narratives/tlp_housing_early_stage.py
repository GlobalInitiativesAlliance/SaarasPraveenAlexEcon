"""
TLP Housing Early Stage - Clean Single-Purpose Interior
Handles ONLY the 'tlp_rules' objective where player moves into TLP housing
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class TLPHousingEarlyStage(NarrativeInterior):
    """TLP housing early stage - single objective only"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

    def enter(self):
        """Override enter to set up TLP housing scene"""
        super().enter()

        # Add interactions for tlp_rules
        interactions = self.narrative_content['tlp_rules']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)

        # Start the narrative sequence
        self.start_narrative_sequence('tlp_rules')

    def load_narrative_content(self):
        """Load ONLY the TLP early stage narrative content"""
        return {
            'tlp_rules': {
                'npcs': [
                    {'name': 'House Manager', 'x': 8, 'y': 3}
                ],
                'dialogue_sequence': [
                    (None, "TLP Housing - Your new home for the next 24 months."),
                    ("House Manager", "Welcome! Let me show you the rules."),
                    ("House Manager", "Shared room with one roommate. Keep it clean."),
                    ("House Manager", "Curfew is 10 PM sharp. Three violations and you're out."),
                    ("House Manager", "Mandatory life skills meetings every Tuesday."),
                    ("House Manager", "Save 30% of your income. We check monthly."),
                    ("House Manager", "No overnight guests. No substances. No excuses."),
                    ("You", "I understand. I'm just grateful to be here."),
                    ("House Manager", "Work hard. Save money. You have 24 months to get stable."),
                    (None, "It's restrictive. But after 6 months of chaos, restrictions feel like safety.")
                ],
                'interactions': {
                    'your_bed': {
                        'position': (10, 6),
                        'prompt': 'Sit on bed',
                        'dialogue': [
                            "Your own bed. First time in 6 months.",
                            "You sit on the bed. It's firm but clean.",
                            "Your own bed. Not a couch, not a floor.",
                            "You can stay here for 24 months.",
                            "Time to rebuild."
                        ],
                        'required': True
                    },
                    'rules_poster': {
                        'position': (7, 3),
                        'prompt': 'Read house rules',
                        'dialogue': [
                            "TLP House Rules:",
                            "1. Curfew: 10 PM (No exceptions)",
                            "2. Savings: 30% of income mandatory",
                            "3. Meetings: Tuesday 7 PM (Required)",
                            "4. Chores: See weekly schedule",
                            "5. Guests: No overnight visitors",
                            "6. Substances: Zero tolerance",
                            "Breaking rules = losing housing. Again."
                        ],
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on TLP housing progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'tlp_rules':
            if self.narrative_active:
                current.dynamic_description = "Learning the TLP house rules..."
            else:
                current.dynamic_description = "Your new home for 24 months"
                current.progress_text = "Read the rules, check your bed"

    def interact_with_object(self, name):
        """Handle interactions for TLP rules objective"""
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
            if current and current.id == 'tlp_rules':
                # Check if requirements met
                if 'your_bed' in self.completed_interactions and not self.narrative_active:
                    self.game.objective_manager.complete_current_objective()
                    self.active = False
                else:
                    self.dialogue_box.show(None, "You need to settle in first. Check your bed.")
                    return

    def draw(self, screen):
        """Draw the TLP housing interior"""
        super().draw(screen)

        # Draw TLP atmosphere indicators
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'tlp_rules' and not self.narrative_active:
            font = pygame.font.Font(None, 24)

            # Show stability indicator
            stability_text = font.render("STABILITY: First time in months", True, (100, 255, 100))
            screen.blit(stability_text, (50, 100))

            # Show time limit
            time_text = font.render("Time limit: 24 months", True, (255, 200, 100))
            screen.blit(time_text, (50, 130))
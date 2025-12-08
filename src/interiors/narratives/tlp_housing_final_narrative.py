"""
TLP Housing Final Month - The end of transitional housing
Where the 24-month limit is reached and reality sets in
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class TLPHousingFinalNarrative(NarrativeInterior):
    """TLP housing during final month - time's up"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track the emotional state
        self.panic_level = 0
        self.reality_accepted = False

    def enter(self):
        """Set up final month scene based on current objective"""
        super().enter()

        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'final_month':
            self.setup_final_month_scene()

        self.update_objective_display()

    def setup_final_month_scene(self):
        """Set up the scene where time runs out at TLP"""
        interactions = self.narrative_content['final_month']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('final_month')

    def load_narrative_content(self):
        """Load narrative content for TLP housing final month"""
        return {
            'final_month': {
                'npcs': [
                    {'name': 'Case Manager', 'x': 6, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "The notice sits on your bed. Official letterhead. Final warning."),
                    ("Case Manager", "I'm sorry, but the 24-month limit is federal law. I can't extend it."),
                    ("You", "But I'm still $600 short for the deposit..."),
                    ("Case Manager", "I know. I'm so sorry. You've done everything right."),
                    ("Case Manager", "The system isn't designed for success. It's designed for compliance."),
                    (None, "30 days. After 18 months of stability, you have 30 days to find housing."),
                    (None, "The math still doesn't work. It never worked.")
                ],
                'interactions': {
                    'eviction_notice': {
                        'position': (5, 6),
                        'prompt': 'Read the notice',
                        'dialogue': [
                            "TRANSITIONAL LIVING PROGRAM - FINAL NOTICE",
                            "Resident: [Your Name]",
                            "Maximum stay: 24 months (Federal Regulation)",
                            "Time remaining: 30 days",
                            "Departure date: [Next Month]",
                            "",
                            "You must vacate by the date listed above.",
                            "No exceptions. No extensions.",
                            "Thank you for your participation in the program.",
                            "",
                            "Your hands shake as you read it again.",
                            "Everything you built. Everything you saved. Still not enough."
                        ],
                        'required': True
                    },
                    'savings_envelope': {
                        'position': (4, 5),
                        'prompt': 'Count your savings',
                        'dialogue': [
                            "You carefully count the bills in the envelope:",
                            "$1,200 total saved over 18 months",
                            "Studio deposit needed: $1,800",
                            "Still short: $600",
                            "",
                            "18 months of saving every penny.",
                            "No new clothes. No entertainment. No life.",
                            "$600 might as well be $6,000.",
                            "The math never worked. The system isn't designed for you to succeed."
                        ],
                        'required': True
                    },
                    'case_manager_desk': {
                        'position': (6, 4),
                        'prompt': 'Ask for help',
                        'dialogue': [
                            "Case Manager: I've called every emergency assistance program.",
                            "Case Manager: I've written letters. Made referrals. Fought the system.",
                            "Case Manager: In 8 years doing this job, you're the most deserving resident I've worked with.",
                            "You: Then why isn't there anything?",
                            "Case Manager: Because the system wants you to fail. It's cheaper when you give up.",
                            "Case Manager: But you won't give up. You'll find a way. You always do.",
                            "You: What if I don't?",
                            "Case Manager: Then it proves the system is broken. Not you."
                        ],
                        'required': True
                    },
                    'room_door': {
                        'position': (3, 7),
                        'prompt': 'Face reality',
                        'dialogue': [
                            "You look around your room. Your safe space for 18 months.",
                            "The bed you sleep in without fear.",
                            "The dresser with your few possessions.",
                            "The window overlooking a world that's about to reject you again.",
                            "",
                            "In 30 days, you'll be homeless again.",
                            "Not because you failed. Because the system did.",
                            "But knowing that doesn't keep you housed.",
                            "",
                            "Time to get desperate."
                        ],
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective display based on current state"""
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'final_month':
            if self.narrative_active:
                current.dynamic_description = "Getting the 30-day notice..."
            else:
                current.dynamic_description = "24 months maximum reached. $600 still needed. 30 days left."
                current.progress_text = "Face the reality - you need desperate measures"

    def handle_interaction_complete(self):
        """Check if objective should be completed"""
        current = self.game.objective_manager.get_current_objective()

        if current and current.id == 'final_month':
            # Check if all required interactions are complete
            required_interactions = ['eviction_notice', 'savings_envelope', 'case_manager_desk', 'room_door']
            if all(interaction in self.completed_interactions for interaction in required_interactions):
                if not self.narrative_active:  # Wait for narrative to finish
                    print(f"[TLP_FINAL] Final month objective complete - advancing to desperate_measures")
                    self.game.objective_manager.complete_current_objective()
                    self.active = False

    def draw(self, screen):
        """Draw the TLP housing interior during final month"""
        super().draw(screen)

        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'final_month':
            # Draw stress indicators
            font = pygame.font.Font(None, 24)

            # Show countdown
            countdown_text = font.render("30 DAYS LEFT", True, (255, 100, 100))
            screen.blit(countdown_text, (50, 100))

            # Show financial status
            money_text = font.render("SAVINGS: $1,200 / $1,800 NEEDED", True, (255, 200, 100))
            screen.blit(money_text, (50, 130))

            # Show system failure
            system_text = font.render("SYSTEM STATUS: FAILING", True, (255, 50, 50))
            screen.blit(system_text, (50, 160))

    def get_room_description(self):
        """Get description of TLP housing during final month"""
        return {
            'base': "Your TLP room. Safe haven for 18 months. About to become a memory.",
            'details': [
                "The eviction notice sits prominently on your bed",
                "Your savings envelope seems pathetically thin",
                "Case manager files scattered on the desk",
                "Every possession here will need to be moved in 30 days",
                "The walls that protected you are closing in",
                "Time is up. The system has spoken."
            ]
        }
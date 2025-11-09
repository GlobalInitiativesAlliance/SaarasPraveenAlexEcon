"""
Studio Apartment Part 1 Ending - Clean Single-Purpose Interior
Handles ONLY Part 1 ending objectives: moving_day, reflection
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class StudioApartmentPart1(NarrativeInterior):
    """Studio apartment for Part 1 ending scenes only"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

    def enter(self):
        """Override enter to set up Part 1 ending scene"""
        super().enter()

        # Check which objective we're on
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id in ['moving_day', 'reflection']:
                # Add interactions for current objective
                interactions = self.narrative_content.get(current.id, {}).get('interactions', {})
                for obj_name, obj_data in interactions.items():
                    self.add_interactive_object(obj_name, obj_data)

                # Start the narrative sequence
                self.start_narrative_sequence(current.id)

    def load_narrative_content(self):
        """Load ONLY the Part 1 studio apartment narrative content"""
        return {
            'moving_day': {
                'npcs': [],  # No NPCs - you're alone
                'dialogue_sequence': [
                    (None, "Finally: Your Own Place"),
                    (None, "You unlock the door with YOUR key."),
                    (None, "The studio is tiny. 300 square feet."),
                    (None, "Roaches scatter when you turn on the light."),
                    (None, "The walls are paper-thin. You hear everything."),
                    (None, "The heater is broken. It's going to be cold."),
                    (None, "But it's YOURS. Your name on the lease."),
                    (None, "For the first time in 2 years, you're safe.")
                ],
                'interactions': {
                    'lease_paper': {
                        'position': (8, 5),
                        'prompt': 'Look at lease',
                        'dialogue': [
                            "LEASE AGREEMENT",
                            "Tenant: YOUR NAME HERE",
                            "Rent: $1,400/month",
                            "Deposit: $1,400 (partial payment accepted)",
                            "Term: 12 months",
                            "YOUR NAME. On an official document.",
                            "You exist. You have an address."
                        ],
                        'required': True
                    },
                    'broken_heater': {
                        'position': (3, 8),
                        'prompt': 'Check heater',
                        'dialogue': [
                            "The heater is completely broken.",
                            "Cold air blows out when you try it.",
                            "You'll need to buy a space heater.",
                            "Another expense. But manageable.",
                            "Problems you can solve with money feel like luxury."
                        ],
                        'required': False
                    },
                    'thin_walls': {
                        'position': (12, 6),
                        'prompt': 'Listen to walls',
                        'dialogue': [
                            "*THUMP* *THUMP* from upstairs",
                            "TV blaring from next door",
                            "A baby crying somewhere",
                            "You can hear everything.",
                            "But nobody can kick you out for listening."
                        ],
                        'required': False
                    }
                }
            },

            'reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Two Years of Hell"),
                    (None, "You sit on your one piece of furniture - a folding chair."),
                    (None, "Two years ago: Aged out of foster care"),
                    (None, "Emergency shelters. Couches. Cars. Floors."),
                    (None, "TLP waitlist. 6 months of surviving."),
                    (None, "18 months in transitional housing."),
                    (None, "And now... your own place."),
                    (None, "It should have taken 2 months. It took 2 years.")
                ],
                'interactions': {
                    'folding_chair': {
                        'position': (8, 8),
                        'prompt': 'Sit and reflect',
                        'dialogue': [
                            "You sit in your only chair.",
                            "From foster care to here: 2 years, 3 months, 12 days.",
                            "You counted every single one.",
                            "How many people your age just... got apartments?",
                            "Called their parents for deposits?",
                            "Had co-signers and credit scores?",
                            "You did this alone. Against a system designed to exclude you.",
                            "You survived."
                        ],
                        'required': True
                    },
                    'window_view': {
                        'position': (12, 3),
                        'prompt': 'Look out window',
                        'dialogue': [
                            "The view is a brick wall 10 feet away.",
                            "Not exactly scenic.",
                            "But it's YOUR view.",
                            "Your window. Your wall. Your perspective.",
                            "The foundation is set. Now you can build."
                        ],
                        'required': False
                    },
                    'phone_contacts': {
                        'position': (5, 5),
                        'prompt': 'Check contacts',
                        'dialogue': [
                            "Contacts: 12",
                            "Case workers: 4",
                            "Emergency lines: 3",
                            "Friends who helped: 3",
                            "Family: 0",
                            "But you made it. And you remember everyone who helped.",
                            "Time to pay it forward."
                        ],
                        'required': False
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'moving_day':
            if self.narrative_active:
                current.dynamic_description = "Finally moving into your own place..."
            else:
                current.dynamic_description = "YOUR apartment. YOUR lease. YOUR home."
                current.progress_text = "Look at your lease to make it real"

        elif current.id == 'reflection':
            if self.narrative_active:
                current.dynamic_description = "Reflecting on the journey..."
            else:
                current.dynamic_description = "2 years of hell. But you made it."
                current.progress_text = "Sit in your chair and reflect"

    def interact_with_object(self, name):
        """Handle interactions for Part 1 ending objectives"""
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

            if current and current.id == 'moving_day':
                # Check if requirements met
                if 'lease_paper' in self.completed_interactions and not self.narrative_active:
                    self.game.objective_manager.complete_current_objective()
                    self.active = False
                else:
                    self.dialogue_box.show(None, "Look at your lease first. Make this real.")
                    return

            elif current and current.id == 'reflection':
                # Check if requirements met
                if 'folding_chair' in self.completed_interactions and not self.narrative_active:
                    self.game.objective_manager.complete_current_objective()
                    self.active = False
                else:
                    self.dialogue_box.show(None, "Take a moment to reflect on your journey.")
                    return

    def draw(self, screen):
        """Draw the studio apartment Part 1 interior"""
        super().draw(screen)

        # Draw Part 1 completion atmosphere
        current = self.game.objective_manager.get_current_objective()
        if current and not self.narrative_active:
            font = pygame.font.Font(None, 24)

            if current.id == 'moving_day':
                # Show achievement indicators
                achievement_text = font.render("ACHIEVEMENT: Your own lease!", True, (100, 255, 100))
                screen.blit(achievement_text, (50, 100))

                stability_text = font.render("STABILITY: Finally secured", True, (150, 255, 150))
                screen.blit(stability_text, (50, 130))

            elif current.id == 'reflection':
                # Show journey completion
                journey_text = font.render("JOURNEY: 2 years, 3 months, 12 days", True, (255, 200, 100))
                screen.blit(journey_text, (50, 100))

                part1_text = font.render("PART 1: COMPLETE", True, (100, 255, 100))
                screen.blit(part1_text, (50, 130))
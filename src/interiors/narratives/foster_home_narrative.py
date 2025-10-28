"""
Foster Home Interior with Aging Out Narrative
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class FosterHomeNarrative(NarrativeInterior):
    """Foster home with aging out narrative sequence"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track packing progress
        self.items_packed = set()
        self.required_items = {'clothes', 'documents', 'photo'}

    def load_narrative_content(self):
        """Load the foster home narrative content"""
        return {
            # First objective: Aging out introduction
            'housing_intro': {
                'npcs': [
                    {'name': 'Foster Parent', 'x': 8, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Foster Parent", "Happy 18th birthday. I know this is hard, but you know the rules."),
                    ("Foster Parent", "Foster care ends at 18. You need to pack your things today."),
                    ("You", "Today? But I don't have anywhere to go..."),
                    ("Foster Parent", "I'm sorry, but those are the state regulations. You have until noon."),
                    ("Foster Parent", "Pack your essentials - clothes, documents, and anything personal you want to keep."),
                    (None, "You feel a knot in your stomach. This is really happening.")
                ],
                'interactions': {
                    'dresser': {
                        'position': (5, 8),
                        'prompt': 'Pack clothes',
                        'dialogue': [
                            "You open the dresser. Most of these clothes were donated.",
                            "You pack what fits in your backpack - two shirts, one pair of jeans, some underwear.",
                            "Everything else belongs to the foster home."
                        ],
                        'required': True
                    },
                    'desk': {
                        'position': (12, 8),
                        'prompt': 'Grab documents',
                        'dialogue': [
                            "You gather your important documents from the desk drawer.",
                            "Birth certificate, social security card, incomplete medical records.",
                            "No high school diploma yet. No ID. No proof of income.",
                            "These papers are all you have to prove you exist."
                        ],
                        'required': True
                    },
                    'nightstand': {
                        'position': (3, 6),
                        'prompt': 'Take photo',
                        'dialogue': [
                            "A photo from when you were 12, with your previous foster family.",
                            "They were nice, but couldn't keep you when they had their own baby.",
                            "You slip it into your pocket. At least you have one good memory."
                        ],
                        'required': True
                    },
                    'door': {
                        'position': (8, 11),
                        'prompt': 'Leave foster home',
                        'dialogue': [
                            "You stand at the door with your backpack. Seven years in this house, and now...",
                            "The foster parent watches from the kitchen, says nothing.",
                            "Once you leave, you can't come back. This is it.",
                            "You step outside. The door clicks shut behind you. You're on your own now."
                        ],
                        'required': False  # Only available after packing
                    }
                }
            },

            # Second objective: Reality check
            'reality_check': {
                'dialogue_sequence': [
                    (None, "You're standing outside the foster home with nowhere to go."),
                    (None, "Your phone shows 12% battery. You have $73 in your pocket."),
                    (None, "No family to call. No couch to crash on. No backup plan."),
                    (None, "You remember hearing about an emergency shelter downtown."),
                    (None, "Maybe they have beds available. You start walking.")
                ],
                'interactions': {}
            }
        }

    def interact_with_object(self, name):
        """Handle special interactions for packing"""
        if name in ['dresser', 'desk', 'nightstand']:
            # Track packed items
            item_map = {
                'dresser': 'clothes',
                'desk': 'documents',
                'nightstand': 'photo'
            }
            self.items_packed.add(item_map[name])

        # Call parent interaction
        super().interact_with_object(name)

        # Check if all required items are packed
        if self.items_packed == self.required_items:
            # Enable the door interaction
            if 'door' not in self.completed_interactions:
                self.add_door_interaction()

    def add_door_interaction(self):
        """Add the final door interaction after packing"""
        # Make door visible as interactive
        if 'housing_intro' in self.narrative_content:
            door_data = self.narrative_content['housing_intro']['interactions']['door']
            self.add_interactive_object('door', door_data)

            # Show a message
            self.dialogue_box.show(None, "You've packed everything. Time to leave.")

    def check_objective_complete(self):
        """Check if the objective is complete"""
        current = self.game.objective_manager.get_current_objective()

        if current and current.id == 'housing_intro':
            # Complete when player interacts with door
            return 'door' in self.completed_interactions
        elif current and current.id == 'reality_check':
            # Complete after dialogue sequence
            return not self.narrative_active

        return True

    def draw(self, screen):
        """Draw the foster home interior with visual indicators"""
        # Draw base interior
        super().draw(screen)

        # Draw packed status in corner
        if self.items_packed:
            font = pygame.font.Font(None, 22)
            y_offset = 10

            # Draw packed items list
            for item in ['clothes', 'documents', 'photo']:
                color = (100, 255, 100) if item in self.items_packed else (150, 150, 150)
                text = f"✓ {item.capitalize()}" if item in self.items_packed else f"  {item.capitalize()}"
                item_surf = font.render(text, True, color)
                screen.blit(item_surf, (10, y_offset))
                y_offset += 25

            # Show completion status
            if self.items_packed == self.required_items:
                ready_surf = font.render("Ready to leave", True, (255, 220, 100))
                screen.blit(ready_surf, (10, y_offset + 10))
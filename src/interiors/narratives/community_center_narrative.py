"""
Community Center Interior - A Hub of Support and Resources
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class CommunityCenterNarrative(NarrativeInterior):
    """Community center with support groups and resources"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track interactions with different areas
        self.resources_viewed = set()
        self.stories_heard = 0

    def enter(self):
        """Override enter to set up community center state"""
        super().enter()

        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'not_alone':
            # Set up the support group scene
            interactions = self.narrative_content['not_alone']['interactions']
            for obj_name, obj_data in interactions.items():
                self.add_interactive_object(obj_name, obj_data)
            # Start with the volunteer greeting
            self.start_narrative_sequence('not_alone')

        self.update_objective_display()

    def load_narrative_content(self):
        """Load the community center narrative content"""
        return {
            'not_alone': {
                'npcs': [
                    {'name': 'Volunteer', 'x': 5, 'y': 4},
                    {'name': 'Marcus', 'x': 3, 'y': 7},  # Another youth who aged out
                    {'name': 'Sofia', 'x': 7, 'y': 7},   # Young person in support group
                    {'name': 'Counselor', 'x': 5, 'y': 8}
                ],
                'dialogue_sequence': [
                    ("Volunteer", "Welcome! I haven't seen you here before. First time?"),
                    ("You", "Yeah... I just got my own place after aging out of foster care."),
                    ("Volunteer", "Congratulations on getting housed! That's a huge accomplishment."),
                    ("Volunteer", "We have a support group meeting starting now. You're welcome to join."),
                    (None, "You see a circle of young people, all with similar exhausted but determined faces."),
                    ("Counselor", "Today we're sharing our housing journeys. Marcus, would you like to start?")
                ],
                'interactions': {
                    'support_circle': {
                        'position': (5, 7),
                        'prompt': 'Join support group',
                        'dialogue': [
                            "Marcus: I aged out two years ago. Couch surfed for 8 months.",
                            "Marcus: The waiting lists, the paperwork... it never ends. But I made it through.",
                            "Sofia: I'm still in TLP housing. Six months left and I'm terrified.",
                            "Sofia: But seeing people like you who made it... it gives me hope.",
                            "You: It took me two years to get stable housing. Two years.",
                            "Counselor: 20,000 youth age out every year. 20% become instantly homeless.",
                            "Counselor: But look around this room. You all survived. You're the proof it's possible.",
                            "You realize you're not alone. Others have walked this same impossible path."
                        ],
                        'required': True
                    },
                    'resource_board': {
                        'position': (10, 3),
                        'prompt': 'Check resource board',
                        'dialogue': [
                            "The bulletin board is covered with resources:",
                            "• Emergency shelter hotline: 211",
                            "• Food pantry hours: M-F 9am-5pm",
                            "• Free legal aid for evictions",
                            "• Job training programs for youth",
                            "• Mental health crisis line: 988",
                            "So many resources, but you had to find them all yourself the hard way."
                        ],
                        'required': False
                    },
                    'food_pantry': {
                        'position': (2, 3),
                        'prompt': 'Visit food pantry',
                        'dialogue': [
                            "Volunteer: Take whatever you need. No questions asked.",
                            "Shelves of canned goods, pasta, rice. Basic but life-saving.",
                            "Volunteer: We also have hygiene products and blankets if you need them.",
                            "You remember days when this would have meant everything."
                        ],
                        'required': False
                    },
                    'volunteer_desk': {
                        'position': (5, 4),
                        'prompt': 'Talk to volunteer coordinator',
                        'dialogue': [
                            "Volunteer: A lot of our volunteers are people who've been through the system.",
                            "Volunteer: They come back to help others navigate what they survived.",
                            "You: Maybe... maybe I could volunteer once I'm more stable.",
                            "Volunteer: You'd be amazing. Your experience is valuable. It helps others know they're not alone.",
                            "The cycle of support. Those who escaped reaching back to pull others up."
                        ],
                        'required': False
                    }
                }
            }
        }

    def get_room_description(self):
        """Get description of the community center"""
        return {
            'base': "A large community room with folding chairs arranged in circles. Fluorescent lights flicker overhead.",
            'details': [
                "A bulletin board overflows with flyers for resources and services",
                "The food pantry shelves are stocked but clearly rely on donations",
                "Motivational posters about resilience cover the walls",
                "A kids' corner has worn toys and donated books",
                "The volunteer desk has sign-in sheets and information packets",
                "Through it all, there's warmth here - people who understand"
            ]
        }

    def update_objective_display(self):
        """Update the objective when all stories are heard"""
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'not_alone':
            # Check if support circle interaction is complete
            if 'support_circle' in self.completed_interactions:
                # Complete the objective to move forward
                if not hasattr(self, 'objective_completed'):
                    self.objective_completed = True
                    self.game.objective_manager.complete_current_objective()

    def interact_with_object(self, obj_name):
        """Track community center interactions"""
        result = super().interact_with_object(obj_name)

        if obj_name == 'support_circle':
            self.stories_heard += 1
        elif obj_name == 'resource_board':
            self.resources_viewed.add('board')
        elif obj_name == 'food_pantry':
            self.resources_viewed.add('pantry')
        elif obj_name == 'volunteer_desk':
            self.resources_viewed.add('volunteer')

        self.update_objective_display()
        return result
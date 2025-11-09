"""
School Classroom Interior - Multiple narrative states based on objectives
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class ClassroomNarrative(NarrativeInterior):
    """Classroom with different states for various objectives"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track which narrative state we're in
        self.current_narrative_state = None
        self.sarah_met = False

    def enter(self):
        """Set up classroom based on current objective"""
        super().enter()

        current = self.game.objective_manager.get_current_objective()
        if current:
            # Set up different scenes based on objective
            if current.id in ['sarah_responds', 'sneaking_around']:
                self.setup_sarah_scene(current.id)
            elif current.id == 'six_months_surviving':
                self.setup_tlp_acceptance_scene()
            elif current.id == 'the_system':
                self.setup_economics_lesson_scene()
            elif current.id == 'part1_complete':
                self.setup_completion_scene()
            elif current.id == 'desperate_measures':
                self.setup_selling_scene()

        self.update_objective_display()

    def setup_sarah_scene(self, objective_id):
        """Set up the scene where Sarah offers her couch"""
        self.current_narrative_state = objective_id
        interactions = self.narrative_content['sarah_couch']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)

        if objective_id == 'sarah_responds':
            self.start_narrative_sequence('sarah_couch')

    def setup_tlp_acceptance_scene(self):
        """Set up the scene for TLP acceptance call"""
        self.current_narrative_state = 'tlp_acceptance'
        interactions = self.narrative_content['tlp_acceptance']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('tlp_acceptance')

    def setup_economics_lesson_scene(self):
        """Set up the economics class scene about the system"""
        self.current_narrative_state = 'economics_lesson'
        interactions = self.narrative_content['economics_lesson']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('economics_lesson')

    def setup_completion_scene(self):
        """Set up the Part 1 completion scene"""
        self.current_narrative_state = 'completion'
        interactions = self.narrative_content['completion']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('completion')

    def setup_selling_scene(self):
        """Set up scene for selling belongings to classmates"""
        self.current_narrative_state = 'selling_items'
        interactions = self.narrative_content['selling_items']['interactions']
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence('selling_items')

    def load_narrative_content(self):
        """Load classroom narrative content for different objectives"""
        return {
            'sarah_couch': {
                'npcs': [
                    {'name': 'Sarah', 'x': 7, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "The classroom is empty except for Sarah waiting by the window."),
                    ("Sarah", "Hey! I got your text. Things are really that bad?"),
                    ("You", "Alex's lease... I'm not on it. The landlord gave me 3 days."),
                    ("Sarah", "Oh no... Look, my parents don't know, but you can crash for a few nights."),
                    ("Sarah", "Just... you have to be really quiet. Come after 11pm, leave before 6am."),
                    ("You", "Sarah, thank you so much. I promise I'll be invisible."),
                    ("Sarah", "It's just for 3 nights max. My parents can't find out or we're both screwed.")
                ],
                'interactions': {
                    'backpack': {
                        'position': (5, 6),
                        'prompt': 'Pack for couch surfing',
                        'dialogue': [
                            "You carefully pack the essentials into your backpack:",
                            "• Change of clothes (1 outfit)",
                            "• Phone charger (can't lose this)",
                            "• Toothbrush",
                            "• Work uniform (need the job)",
                            "Everything else stays in a locker. Travel light, stay mobile."
                        ],
                        'required': True
                    },
                    'window': {
                        'position': (10, 4),
                        'prompt': 'Look outside',
                        'dialogue': [
                            "Students heading home to stable families.",
                            "You used to be one of them. Now you're counting nights of shelter.",
                            "Sarah: Hey, it's going to be okay. We'll figure something out."
                        ],
                        'required': False
                    }
                }
            },
            'tlp_acceptance': {
                'npcs': [
                    {'name': 'Classmate', 'x': 6, 'y': 5},
                    {'name': 'Another Student', 'x': 8, 'y': 6}
                ],
                'dialogue_sequence': [
                    (None, "Your phone rings in the middle of class. Unknown number."),
                    ("Phone", "Hello, is this [Your Name]? This is TLP Housing Services."),
                    ("You", "Yes! Yes, this is me!"),
                    ("Phone", "We have an opening. Can you move in tomorrow?"),
                    ("You", "Tomorrow? YES! Absolutely yes!"),
                    ("Classmate", "What happened? You're crying..."),
                    ("You", "I got it... I got into transitional housing. After 6 months on the waitlist..."),
                    ("Another Student", "That's amazing! Congratulations!"),
                    (None, "Six months of shelters, couches, and cars. Finally, stability.")
                ],
                'interactions': {
                    'celebration': {
                        'position': (7, 6),
                        'prompt': 'Celebrate with classmates',
                        'dialogue': [
                            "Classmate: I had no idea you were going through all that.",
                            "You: Most people don't talk about it. The shame is overwhelming.",
                            "Another Student: You're incredible for making it through while keeping up with school.",
                            "For the first time in months, you feel hope."
                        ],
                        'required': True
                    }
                }
            },
            'economics_lesson': {
                'npcs': [
                    {'name': 'Professor', 'x': 5, 'y': 3}
                ],
                'dialogue_sequence': [
                    ("Professor", "Today we're discussing systemic barriers in housing access."),
                    ("Professor", "Can anyone explain why housing costs have outpaced wages?"),
                    (None, "You know the answer intimately. You've lived it.")
                ],
                'interactions': {
                    'whiteboard': {
                        'position': (5, 2),
                        'prompt': 'Study the statistics',
                        'dialogue': [
                            "The whiteboard shows devastating statistics:",
                            "• 20,000 youth age out of foster care annually",
                            "• 20% become instantly homeless",
                            "• 50% unemployed by age 24",
                            "• Average time to stable housing: 2+ years",
                            "Professor: These aren't just numbers. These are people's lives.",
                            "You: Every statistic up there... I've been that statistic.",
                            "The class goes quiet. The numbers suddenly feel real."
                        ],
                        'required': True
                    },
                    'desk': {
                        'position': (7, 5),
                        'prompt': 'Review your notes',
                        'dialogue': [
                            "Your notebook is filled with real experience:",
                            "• Security deposits = 2-3x monthly rent (impossible)",
                            "• Credit check fees = $50 per application (adds up fast)",
                            "• No co-signer = automatic rejection",
                            "• Part-time minimum wage = $1200/month",
                            "• Cheapest studio = $1400/month",
                            "The math never worked. The system wasn't designed for you to succeed."
                        ],
                        'required': False
                    }
                }
            },
            'selling_items': {
                'npcs': [
                    {'name': 'Buyer 1', 'x': 4, 'y': 5},
                    {'name': 'Buyer 2', 'x': 8, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "You've laid out your possessions on a desk. Everything must go."),
                    ("You", "Selling some things. Need the money for a deposit."),
                    ("Buyer 1", "Is that your laptop? Don't you need it for class?"),
                    ("You", "I need housing more than I need to take notes."),
                    (None, "Each item sold is a sacrifice. Education for shelter.")
                ],
                'interactions': {
                    'sell_laptop': {
                        'position': (5, 5),
                        'prompt': 'Sell laptop - $200',
                        'dialogue': [
                            "Buyer 1: I'll give you $200 for the laptop.",
                            "You: It's worth more, but... okay. I need the money today.",
                            "No more digital assignments. You'll handwrite everything now.",
                            "+$200 towards deposit"
                        ],
                        'required': True
                    },
                    'sell_textbooks': {
                        'position': (6, 5),
                        'prompt': 'Sell textbooks - $30',
                        'dialogue': [
                            "Buyer 2: $30 for all the textbooks?",
                            "You: They cost me $300, but... fine.",
                            "You'll share books or use the library. Whatever it takes.",
                            "+$30 towards deposit"
                        ],
                        'required': True
                    },
                    'sell_coat': {
                        'position': (7, 5),
                        'prompt': 'Sell winter coat - $40',
                        'dialogue': [
                            "Buyer 1: It's almost winter. You sure about the coat?",
                            "You: I'll layer up. I've survived worse.",
                            "You remember nights without any coat. You'll manage.",
                            "+$40 towards deposit"
                        ],
                        'required': True
                    }
                }
            },
            'completion': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The classroom is empty. Just you and your thoughts."),
                    (None, "Two years ago, you sat in these same desks with a different life."),
                    (None, "Now you understand economics from the bottom up."),
                    (None, "You've lived every theory, every policy failure, every systemic barrier."),
                    (None, "Part 1 Complete: You've secured housing. The foundation is set."),
                    (None, "But maintaining it? That's a whole different battle...")
                ],
                'interactions': {
                    'diploma': {
                        'position': (5, 3),
                        'prompt': 'Look at achievement',
                        'dialogue': [
                            "A certificate on the wall: 'Student Achievement Award'",
                            "You maintained grades while homeless. An impossible achievement.",
                            "No award for surviving the streets, but you earned that too.",
                            "Ready for Part 2: Maintaining Housing"
                        ],
                        'required': True
                    }
                }
            }
        }

    def get_room_description(self):
        """Get description based on current state"""
        if self.current_narrative_state == 'sarah_couch':
            return {
                'base': "An empty classroom after hours. Desks pushed aside, backpacks scattered.",
                'details': [
                    "The fluorescent lights hum in the silence",
                    "Sarah waits nervously by the window",
                    "Outside, the parking lot empties as students go home",
                    "The whiteboard still has today's lessons",
                    "Your entire life fits in one backpack now"
                ]
            }
        elif self.current_narrative_state == 'economics_lesson':
            return {
                'base': "A typical classroom during economics class. The irony isn't lost on you.",
                'details': [
                    "The whiteboard is covered in housing statistics",
                    "Students take notes on poverty they've never experienced",
                    "You could teach this class from lived experience",
                    "The professor's theories vs your reality",
                    "Every statistic has been your life"
                ]
            }
        else:
            return {
                'base': "A familiar classroom. Site of learning, struggles, and small victories.",
                'details': [
                    "Rows of desks where you've fought to stay awake",
                    "Windows overlooking a world that kept spinning while you survived",
                    "The education you fought to maintain despite everything",
                    "Proof that you belonged here, even when you had nowhere to sleep"
                ]
            }

    def update_objective_display(self):
        """Complete objectives based on interactions"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        # Complete objectives when key interactions are done
        if current.id == 'sarah_responds' and 'backpack' in self.completed_interactions:
            self.game.objective_manager.complete_current_objective()
        elif current.id == 'six_months_surviving' and 'celebration' in self.completed_interactions:
            self.game.objective_manager.complete_current_objective()
        elif current.id == 'the_system' and 'whiteboard' in self.completed_interactions:
            self.game.objective_manager.complete_current_objective()
        elif current.id == 'desperate_measures':
            # Check if all items are sold
            if all(item in self.completed_interactions for item in ['sell_laptop', 'sell_textbooks', 'sell_coat']):
                self.game.objective_manager.complete_current_objective()
        elif current.id == 'part1_complete' and 'diploma' in self.completed_interactions:
            self.game.objective_manager.complete_current_objective()
"""
Final Crappy Apartment - The "victory" of Part 1
A terrible apartment, but it's YOURS. Your name on the lease.
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class CrappyApartmentNarrative(NarrativeInterior):
    """The worst apartment ever, but with your name on the lease"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track the state of the apartment
        self.roaches_seen = 0
        self.problems_documented = set()
        self.emotional_state = 'exhausted'

    # Map objective IDs to scene IDs (some differ)
    OBJECTIVE_TO_SCENE = {
        'mike_floor': 'mike_floor',
        'found_studio': 'viewing',
        'moving_day': 'moving_day',
        'reflection': 'reflection'
    }

    def enter(self):
        """Set up apartment based on current objective"""
        super().enter()

        current = self.game.objective_manager.get_current_objective()
        if current:
            scene_id = self.OBJECTIVE_TO_SCENE.get(current.id)
            if scene_id:
                self.setup_scene(scene_id)

        self.update_objective_display()

    def setup_scene(self, scene_id: str):
        """Generic scene setup - adds interactions and starts narrative sequence"""
        if scene_id not in self.narrative_content:
            return

        scene_data = self.narrative_content[scene_id]
        interactions = scene_data.get('interactions', {})
        for obj_name, obj_data in interactions.items():
            self.add_interactive_object(obj_name, obj_data)
        self.start_narrative_sequence(scene_id)

    def load_narrative_content(self):
        """Load narrative content for the crappy apartment"""
        return {
            'mike_floor': {
                'npcs': [
                    {'name': 'Mike', 'x': 6, 'y': 4}
                ],
                'dialogue_sequence': [
                    ("Mike", "Hey! Sorry about the mess. We've got 5 people in a 2-bedroom."),
                    (None, "The apartment is chaos. Clothes everywhere. Dishes piled high."),
                    ("Mike", "You can crash on the floor by the couch. Best I can do."),
                    (None, "You see a thin strip of carpet between the couch and the wall."),
                    ("You", "Thanks Mike. I really appreciate this."),
                    ("Mike", "No worries. But fair warning - my roommates aren't thrilled."),
                    (None, "Someone coughs pointedly from the other room."),
                    ("Mike", "Just... try to be invisible, you know?"),
                    (None, "You nod. You've gotten good at being invisible.")
                ],
                'interactions': {
                    'claim_spot': {
                        'position': (4, 6),
                        'prompt': 'Set up your sleeping spot',
                        'dialogue': [
                            "You lay out your sleeping bag in the narrow space.",
                            "The carpet is stained. Something crunches underneath.",
                            "You're wedged between the couch and the wall.",
                            "If someone walks to the bathroom at night, they'll step over you.",
                            "This is your home now. A 2-foot strip of floor.",
                            "At least it's indoors."
                        ],
                        'required': True
                    },
                    'meet_roommates': {
                        'position': (8, 4),
                        'prompt': 'Introduce yourself to roommates',
                        'dialogue': [
                            "You try to introduce yourself to Mike's roommates.",
                            "One barely looks up from their phone. 'Hey.'",
                            "Another sighs audibly. 'How long are you staying?'",
                            "You: Just until I find something. A week, maybe.",
                            "They exchange a look. You've seen that look before.",
                            "'That's what the last one said. Stayed three months.'",
                            "You promise yourself you'll be gone before you wear out welcome.",
                            "But you've made that promise before too."
                        ],
                        'required': True
                    },
                    'hide_belongings': {
                        'position': (3, 5),
                        'prompt': 'Secure your belongings',
                        'dialogue': [
                            "You stuff your bag under the couch, out of sight.",
                            "Everything you own fits in that bag.",
                            "You've learned: visible belongings invite questions.",
                            "Or worse - they disappear.",
                            "You zip it tight and push it deeper under.",
                            "You'll sleep with your hand touching the strap.",
                            "Just in case."
                        ],
                        'required': True
                    },
                    'check_rules': {
                        'position': (6, 5),
                        'prompt': 'Ask about house rules',
                        'dialogue': [
                            "You ask about house rules.",
                            "Mike: Don't eat anyone's labeled food. Clean up after yourself.",
                            "Mike: Bathroom's first come first serve. Good luck at 7am.",
                            "Mike: No guests. Obviously.",
                            "Mike: And uh... the landlord doesn't know you're here.",
                            "Mike: So if anyone asks, you're just visiting for the day.",
                            "Invisible. You need to stay invisible.",
                            "One complaint and you're back on the street."
                        ],
                        'required': True
                    }
                }
            },
            'viewing': {
                'npcs': [
                    {'name': 'Landlord', 'x': 6, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "The door creaks open. The smell hits you first - mildew and something worse."),
                    ("Landlord", "It's $900 a month. I know it needs work, but housing's tight."),
                    ("You", "The ceiling... is that black mold?"),
                    ("Landlord", "Look, you want it or not? I've got three other viewings today."),
                    (None, "A roach scurries across the floor. The landlord doesn't even react."),
                    ("Landlord", "I can work with you on the deposit. $600 now, $600 later."),
                    ("You", "The heater's broken..."),
                    ("Landlord", "Space heater works fine. Take it or leave it. Decide now.")
                ],
                'interactions': {
                    'inspect_damage': {
                        'position': (4, 4),
                        'prompt': 'Document the damage',
                        'dialogue': [
                            "You mentally catalog the problems:",
                            "• Black mold spreading across bathroom ceiling",
                            "• Broken radiator, rusted beyond repair",
                            "• Roach infestation (you count 3 just standing here)",
                            "• Windows cracked, sealed with duct tape",
                            "• Water stains suggesting active leaks",
                            "• Electrical outlet sparking when touched",
                            "You: This place could be condemned...",
                            "Landlord: It's this or the street. Your choice."
                        ],
                        'required': True
                    },
                    'check_lease': {
                        'position': (6, 5),
                        'prompt': 'Read the lease terms',
                        'dialogue': [
                            "The lease is predatory but it's your only option:",
                            "• $900/month (will take 75% of your income)",
                            "• No repairs guaranteed",
                            "• Can be evicted with 3 days notice",
                            "• No guests after 9pm",
                            "• Responsible for all pest control",
                            "You: These terms are horrible...",
                            "Landlord: But it's a lease. With YOUR name on it. That's what matters, right?",
                            "He's right. After two years, your name on a lease means everything."
                        ],
                        'required': True
                    },
                    'sign_lease': {
                        'position': (6, 6),
                        'prompt': 'Sign the lease',
                        'dialogue': [
                            "Your hand shakes as you sign.",
                            "Landlord: Smart choice. Here's the key. Rent's due on the 1st.",
                            "A metal key in your hand. YOUR key. To YOUR apartment.",
                            "It's terrible. It's unsafe. It's probably illegal.",
                            "It's yours.",
                            "You: Thank you...",
                            "You hate that you're grateful for this disaster. But you are."
                        ],
                        'required': True
                    }
                }
            },
            'moving_day': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Moving day. One cardboard box contains your entire life."),
                    (None, "You set it down on the stained carpet."),
                    (None, "A roach scurries across your foot. You don't even flinch anymore."),
                    (None, "The walls are so thin you can hear every word from next door's TV."),
                    (None, "But when you close the door, you're closing YOUR door."),
                    (None, "For the first time in two years, you have a door you can close.")
                ],
                'interactions': {
                    'unpack_box': {
                        'position': (5, 5),
                        'prompt': 'Unpack your belongings',
                        'dialogue': [
                            "You carefully unpack your few possessions:",
                            "• Three changes of clothes (all you have left)",
                            "• Photo of your birth parents (creased from so much moving)",
                            "• Toothbrush and basic hygiene items",
                            "• Phone charger (your lifeline)",
                            "• The folder of documents that proved you deserved to exist",
                            "• A small plant someone gave you (a hope for the future)",
                            "Everything fits in one corner. The apartment still looks empty.",
                            "But it's YOUR empty apartment."
                        ],
                        'required': True
                    },
                    'test_locks': {
                        'position': (3, 6),
                        'prompt': 'Test the door locks',
                        'dialogue': [
                            "You lock the door. Unlock it. Lock it again.",
                            "The deadbolt barely works, but it's there.",
                            "You can lock out the world. No one can make you leave at 6am.",
                            "No one can tell you 'just three more nights'.",
                            "No one can kick you out because their partner is moving in.",
                            "This broken lock is freedom."
                        ],
                        'required': False
                    },
                    'claim_space': {
                        'position': (6, 4),
                        'prompt': 'Make it yours',
                        'dialogue': [
                            "You tape the photo to the wall. Your first decoration.",
                            "Place the plant on the windowsill. Something living, growing.",
                            "Lay out your sleeping bag. No bed yet, but the floor is YOURS.",
                            "Turn on the single lamp. Your electricity. Your light.",
                            "A roach crawls up the wall. You name it Fred.",
                            "If Fred's living here, he's paying half the rent.",
                            "You laugh. Then cry. Then laugh again.",
                            "You're home."
                        ],
                        'required': True
                    },
                    'check_mailbox': {
                        'position': (8, 6),
                        'prompt': 'Check your mailbox',
                        'dialogue': [
                            "You go to the building's mailboxes.",
                            "There it is. Apartment 4B. Your name on the label.",
                            "Official proof you live somewhere.",
                            "You can receive mail. Open a bank account. Apply for jobs with an address.",
                            "This little metal box represents citizenship in the housed world.",
                            "You touch your name on the label.",
                            "You exist. You have an address. You matter."
                        ],
                        'required': True
                    }
                }
            },
            'reflection': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Night falls on your first day with stable housing."),
                    (None, "You sit on the floor, back against the wall."),
                    (None, "Through the cracked window, the city continues its indifferent rhythm."),
                    (None, "Two years. It took two years to get here."),
                    (None, "This roach-infested, mold-covered, broken disaster."),
                    (None, "And you're grateful. That's the worst part. You're so grateful."),
                    (None, "Because tonight, no one can make you leave.")
                ],
                'interactions': {
                    'journal_entry': {
                        'position': (5, 5),
                        'prompt': 'Write in journal',
                        'dialogue': [
                            "You pull out a notebook and write:",
                            "'Day 1 of having my own place.'",
                            "'734 days since aging out of foster care.'",
                            "'Survived: 12 foster homes, 6 months in shelters, 8 couches, 3 cars.'",
                            "'Lost: Education opportunities, jobs, relationships, health, faith in the system.'",
                            "'Gained: Knowledge that I can survive anything.'",
                            "'The apartment has roaches. The heater is broken. The walls are moldy.'",
                            "'My name is on the lease.'",
                            "'I won.'"
                        ],
                        'required': True
                    },
                    'window_view': {
                        'position': (8, 4),
                        'prompt': 'Look out window',
                        'dialogue': [
                            "Through the cracked glass, you see the city at night.",
                            "Thousands of windows lit up. People in their homes.",
                            "You're one of them now. A person with a window.",
                            "Tomorrow you'll wake up in the same place you fell asleep.",
                            "Revolutionary. Impossible. Achieved."
                        ],
                        'required': False
                    },
                    'count_costs': {
                        'position': (4, 6),
                        'prompt': 'Calculate the true cost',
                        'dialogue': [
                            "You do the math of what it really cost to get here:",
                            "• $600 deposit (sold everything you owned)",
                            "• $900 first month (80% of your income)",
                            "• 734 days of survival",
                            "• Countless rejections and humiliations",
                            "• Physical and mental health deteriorated",
                            "• Education interrupted, dreams deferred",
                            "Should have cost: First month + deposit",
                            "Actual cost: Everything",
                            "Worth it: Your name on a lease"
                        ],
                        'required': True
                    },
                    'plan_future': {
                        'position': (6, 5),
                        'prompt': 'Think about tomorrow',
                        'dialogue': [
                            "Now the next challenge begins: keeping this place.",
                            "$900 monthly rent on $1200 income.",
                            "No savings left. No safety net.",
                            "One missed paycheck from eviction.",
                            "But that's tomorrow's battle.",
                            "Tonight, you have a door you can lock.",
                            "Tonight, you sleep without one ear open.",
                            "Tonight, you're home.",
                            "Part 1 Complete: Housing obtained.",
                            "Part 2 awaits: Keeping it."
                        ],
                        'required': True
                    }
                }
            }
        }

    def get_room_description(self):
        """Get description of this disaster of an apartment"""
        current = self.game.objective_manager.get_current_objective()

        if current and current.id == 'mike_floor':
            return {
                'base': "Mike's overcrowded 2-bedroom apartment. 5 people. 1 bathroom. Your spot: the floor.",
                'details': [
                    "Clothes and belongings scattered everywhere",
                    "Dishes piled in the sink, overflowing",
                    "A thin strip of carpet by the couch - your 'room'",
                    "Tension thick enough to cut",
                    "The landlord doesn't know you're here",
                    "One week. You promised yourself one week."
                ]
            }
        elif current and current.id == 'found_studio':
            return {
                'base': "A 200 sq ft efficiency apartment. Calling it 'distressed' is generous.",
                'details': [
                    "Black mold creeps across the bathroom ceiling",
                    "Roaches scatter as you walk",
                    "The radiator is a rusted sculpture of dysfunction",
                    "Duct tape holds the window together",
                    "Water stains map unknown leaks above",
                    "But there's a lease with a signature line waiting"
                ]
            }
        elif current and current.id == 'moving_day':
            return {
                'base': "YOUR apartment. Terrible, unsafe, barely legal. YOURS.",
                'details': [
                    "One cardboard box holds everything you own",
                    "A sleeping bag instead of a bed",
                    "Your photo taped to the wall - first decoration",
                    "A small plant on the windowsill - hope growing",
                    "Roaches you're learning to coexist with",
                    "A door that locks. Your door. That you can lock."
                ]
            }
        else:
            return {
                'base': "Home. After 734 days, you're home.",
                'details': [
                    "The mold is spreading but you'll deal with it",
                    "The heater's broken but you have blankets",
                    "The roaches are many but they're YOUR roaches",
                    "The walls are thin but they're YOUR walls",
                    "Your name on the lease makes it all worth it",
                    "This disaster is your victory"
                ]
            }

    def update_objective_display(self):
        """Update objectives based on interactions - data-driven from narrative content"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        scene_id = self.OBJECTIVE_TO_SCENE.get(current.id)
        if not scene_id or scene_id not in self.narrative_content:
            return

        # Get required interactions from narrative content
        scene_data = self.narrative_content[scene_id]
        interactions = scene_data.get('interactions', {})
        required = [name for name, data in interactions.items() if data.get('required', False)]

        # Complete objective when all required interactions are done
        if required and all(x in self.completed_interactions for x in required):
            self.game.objective_manager.complete_current_objective()
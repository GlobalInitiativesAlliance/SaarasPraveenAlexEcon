"""
Your crappy studio apartment - the battleground for housing stability
Auto-generated narrative interior for Part 2 Housing
"""

import pygame
import json
from src.interiors.narrative_interior import NarrativeInterior

class StudioApartmentNarrative(NarrativeInterior):
    """studio_apartment with narrative sequences"""

    def __init__(self, game, room_data, building_pos):
        # Load room data from JSON if string path provided
        if isinstance(room_data, str):
            with open(room_data, 'r') as f:
                room_data = json.load(f)

        super().__init__(game, room_data, building_pos)
        self.current_activity = None

    def get_room_data_path(self):
        """Return the path to the room JSON file"""
        return "data/interiors/rooms/bad_studio.json"

    def load_narrative_content(self):
        """Load the narrative content for this location"""
        return {
            'studio_day_one': {
                'npcs': [
                    {'name': 'Landlord', 'x': 5, 'y': 6},
                    {'name': 'Neighbor', 'x': 10, 'y': 4}
                ],
                'dialogue_sequence': [
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
                    'heater': {
                        'position': (3, 8),
                        'prompt': 'Examine broken heater',
                        'dialogue': ["It hasn't worked in months.", "Ice cold to the touch.", "Landlord knew about this."],
                    },
                    'window': {
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
            'rent_increase_notice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "There's a notice taped to your door."),
                    (None, "'30-Day Notice of Rent Increase'"),
                    (None, "New rent: $1,035. Effective next month."),
                    (None, "That's a 15% increase."),
                    (None, "Your hands shake as you read it again."),
                    (None, "This can't be legal. Can it?")
                ],
                'interactions': {
                    'notice': {
                        'position': (8, 10),
                        'prompt': 'Read notice carefully',
                        'dialogue': ["'Due to market conditions...'", "'This increase is within legal limits...'", "It's technically legal. But it's a death sentence."],
                    }
                }
            },
            'impossible_math_again': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "New rent: $1,035"),
                    (None, "Your income: $1,200"),
                    (None, "That's 86% of your income just for rent."),
                    (None, "The recommended amount is 30%."),
                    (None, "This is literally impossible to survive.")
                ],
                'interactions': {}
            },
            'broken_stair_accident': {
                'npcs': [
                    {'name': 'Concerned Neighbor', 'x': 8, 'y': 9}
                ],
                'dialogue_sequence': [
                    (None, "You're carrying groceries up the stairs."),
                    (None, "The broken step you've reported three times gives way."),
                    (None, "You fall hard. Your ankle twists badly."),
                    ("Concerned Neighbor", "Oh my god! Are you okay?"),
                    ("You", "My ankle... I can't put weight on it."),
                    ("Concerned Neighbor", "We need to get you to the hospital."),
                    (None, "You think about the medical bills. But you can't walk.")
                ],
                'interactions': {}
            },
            'missed_work': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You've been out for 5 days with your injury."),
                    (None, "No paid sick leave at your job."),
                    (None, "5 days × $90/day = $450 lost income."),
                    (None, "Your next paycheck will be half what you need."),
                    (None, "The rent is still due in full.")
                ],
                'interactions': {}
            },
            'short_on_rent': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Rent day. You count your money again."),
                    (None, "You have $700."),
                    (None, "Rent is $900."),
                    (None, "First time in your life you can't pay rent."),
                    (None, "Your stomach churns with anxiety.")
                ],
                'interactions': {
                    'wallet': {
                        'position': (7, 6),
                        'prompt': 'Count money again',
                        'dialogue': ["$700 exactly.", "Still $200 short.", "Maybe you miscounted? No..."],
                    }
                }
            },
            'eviction_threat': {
                'npcs': [
                    {'name': 'Landlord', 'x': 8, 'y': 10}
                ],
                'dialogue_sequence': [
                    ("Landlord", "You're late on rent."),
                    ("You", "I was injured on your broken stairs! I missed work!"),
                    ("Landlord", "Not my problem. Pay or quit."),
                    ("Landlord", "You have 3 days to pay in full or I start eviction."),
                    (None, "He posts a notice on your door and leaves."),
                    (None, "'3-Day Pay or Quit Notice'"),
                    (None, "An eviction on your record means you'll never rent again.")
                ],
                'interactions': {}
            },
            'inspection_request': {
                'npcs': [
                    {'name': 'City Inspector', 'x': 6, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("City Inspector", "I'm here for the requested inspection."),
                    ("You", "Thank you for coming. Let me show you the violations."),
                    (None, "You walk through the apartment together."),
                    ("City Inspector", "Broken heater... that's a habitability violation."),
                    ("City Inspector", "Mold in the bathroom... health hazard."),
                    ("City Inspector", "Broken window locks... security violation."),
                    ("City Inspector", "I'm documenting 12 violations total."),
                    ("You", "What happens now?"),
                    ("City Inspector", "Your landlord has 30 days to fix these or face fines.")
                ],
                'interactions': {
                    'clipboard': {
                        'position': (6, 6),
                        'prompt': 'Review inspection report',
                        'dialogue': ["12 code violations documented", "Landlord must remedy within 30 days", "This is your leverage."],
                    }
                }
            },
            'negotiation': {
                'npcs': [
                    {'name': 'Landlord', 'x': 8, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Landlord", "Fine. I got your lawyer's letter."),
                    ("Landlord", "I'll fix the heater. And give you a payment plan for back rent."),
                    ("You", "What about the other violations?"),
                    ("Landlord", "The heater. That's it. Take it or leave it."),
                    (None, "It's not everything, but it's something."),
                    (None, "You accept. A small victory is still a victory.")
                ],
                'interactions': {}
            },
            'building_sold': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Another notice on your door. Your heart sinks."),
                    (None, "'Notice to Tenants: Building Under New Ownership'"),
                    (None, "The new owner plans to 'renovate and reposition the property.'"),
                    (None, "That's code for: kick everyone out and triple the rent."),
                    (None, "You've seen this story before. Gentrification."),
                    (None, "But this time, you're the one being displaced.")
                ],
                'interactions': {}
            },
            'cash_for_keys': {
                'npcs': [
                    {'name': 'Property Manager', 'x': 8, 'y': 6}
                ],
                'dialogue_sequence': [
                    ("Property Manager", "We'd like to make you an offer."),
                    ("Property Manager", "$2,000 cash if you vacate voluntarily within 60 days."),
                    ("You", "And if I don't?"),
                    ("Property Manager", "We'll proceed with eviction for the unpaid rent."),
                    ("Property Manager", "You still owe from when you were injured, right?"),
                    ("Property Manager", "An eviction on your record... that follows you forever."),
                    ("You", "I need time to think."),
                    ("Property Manager", "You have 48 hours to decide.")
                ],
                'interactions': {}
            },
            'impossible_choice': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "Take the money: You get $2,000 and avoid eviction on your record."),
                    (None, "But you enable them. They'll do this to others."),
                    (None, "Fight back: Stand with other tenants. Maybe win."),
                    (None, "But if you lose, you'll have an eviction record forever."),
                    (None, "There's no good choice. Just different kinds of survival.")
                ],
                'interactions': {
                    'phone': {
                        'position': (7, 7),
                        'prompt': 'Call other tenants',
                        'dialogue': ["'Are you fighting or taking the money?'", "'I don't know yet...'", "'We need to decide together.'"],
                    }
                }
            },
            'final_decision': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "The deadline has arrived. You must choose."),
                    (None, "Option 1: Take the $2,000 and leave peacefully."),
                    (None, "Option 2: Fight the eviction with other tenants."),
                    (None, "This decision will change everything.")
                ],
                'interactions': {
                    'door': {
                        'position': (8, 10),
                        'prompt': 'Make your choice',
                        'trigger_activity': 'housing_choice',
                    }
                }
            },
            'moving_out': {
                'npcs': [],
                'dialogue_sequence': [
                    (None, "You pack your belongings. Again."),
                    (None, "The $2,000 will cover a deposit elsewhere."),
                    (None, "You're not proud of this choice."),
                    (None, "But survival isn't about pride."),
                    (None, "It's about living to fight another day.")
                ],
                'interactions': {}
            },
            'still_fighting': {
                'npcs': [
                    {'name': 'Fellow Tenant', 'x': 6, 'y': 5},
                    {'name': 'Organizer', 'x': 9, 'y': 5}
                ],
                'dialogue_sequence': [
                    ("Organizer", "The judge granted a 6-month stay!"),
                    ("Fellow Tenant", "We did it! We're still here!"),
                    ("You", "For now. But what about after 6 months?"),
                    ("Organizer", "We keep fighting. We keep organizing."),
                    ("Organizer", "This isn't over. It's just beginning."),
                    (None, "The apartment is still crappy. The heater barely works."),
                    (None, "But you learned something valuable: how to fight back."),
                    (None, "Sometimes that's the real victory.")
                ],
                'interactions': {}
            },
        }

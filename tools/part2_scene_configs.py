"""
Complete Part 2 Scene Configurations
All objectives from Part 2: Maintaining Housing
"""

PART2_COMPLETE_SCENES = {
    # Studio apartment scenes (most objectives happen here)
    'studio_apartment': {
        'location_name': 'studio_apartment',
        'description': 'Your crappy studio apartment - the battleground for housing stability',
        'objectives': {
            # Chapter 1: Reality of "Success"
            'studio_day_one': {
                'npcs': [
                    {'name': 'Landlord', 'x': 5, 'y': 6},
                    {'name': 'Neighbor', 'x': 10, 'y': 4}
                ],
                'dialogue': [
                    ('Landlord', "Rent's due on the first. Don't be late."),
                    ('You', "What about the broken heater you promised to fix?"),
                    ('Landlord', "I'll get to it when I get to it."),
                    (None, "He leaves without another word. You're on your own."),
                    ('Neighbor', "Hey, new tenant? Word of advice - document everything."),
                    ('Neighbor', "Take photos, save texts. You'll need evidence."),
                    ('Neighbor', "And watch out - we've had 3 break-ins this month."),
                    (None, "The apartment is worse than you thought. Roaches scatter as you walk.")
                ],
                'interactions': {
                    'heater': {
                        'position': (3, 8),
                        'prompt': 'Examine broken heater',
                        'dialogue': ["It hasn't worked in months.", "Ice cold to the touch.", "Landlord knew about this."]
                    },
                    'window': {
                        'position': (12, 5),
                        'prompt': 'Check window locks',
                        'dialogue': ["The lock is broken.", "Anyone could get in.", "No wonder there were break-ins."]
                    },
                    'phone': {
                        'position': (7, 7),
                        'prompt': 'Document problems',
                        'trigger_activity': 'document_violations'
                    }
                }
            },

            'document_problems': {
                'npcs': [],
                'dialogue': [
                    (None, "Time to build your case. Document everything."),
                    (None, "Take photos of every violation, every broken thing."),
                    (None, "This evidence might save you later.")
                ],
                'interactions': {
                    'camera': {
                        'position': (7, 7),
                        'prompt': 'Start documenting',
                        'trigger_activity': 'document_violations'
                    }
                }
            },

            'first_repair_request': {
                'npcs': [],
                'dialogue': [
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
                'dialogue': [
                    ('Upstairs Neighbor', "Welcome to the building. Sorry about the noise."),
                    ('You', "It's okay. The walls are pretty thin."),
                    ('Upstairs Neighbor', "That's not the worst part. Watch your stuff."),
                    ('Next Door Neighbor', "Three break-ins just this month. My bike got stolen."),
                    ('Next Door Neighbor', "Landlord won't fix the security door downstairs."),
                    ('You', "Have you reported it?"),
                    ('Upstairs Neighbor', "We've tried everything. He doesn't care."),
                    (None, "You're starting to understand what you've gotten into.")
                ],
                'interactions': {}
            },

            'first_utility_bill': {
                'npcs': [],
                'dialogue': [
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
                        'dialogue': ["Usage: 1800 kWh", "Rate: $0.11/kWh", "Your broken heater is costing you a fortune."]
                    }
                }
            },

            'budget_crisis': {
                'npcs': [],
                'dialogue': [
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
                        'trigger_activity': 'budget_breakdown'
                    }
                }
            },

            # Chapter 2: The Increase
            'rent_increase_notice': {
                'npcs': [],
                'dialogue': [
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
                        'dialogue': ["'Due to market conditions...'", "'This increase is within legal limits...'", "It's technically legal. But it's a death sentence."]
                    }
                }
            },

            'impossible_math_again': {
                'npcs': [],
                'dialogue': [
                    (None, "New rent: $1,035"),
                    (None, "Your income: $1,200"),
                    (None, "That's 86% of your income just for rent."),
                    (None, "The recommended amount is 30%."),
                    (None, "This is literally impossible to survive.")
                ],
                'interactions': {}
            },

            # Chapter 3: The Crisis
            'broken_stair_accident': {
                'npcs': [
                    {'name': 'Concerned Neighbor', 'x': 8, 'y': 9}
                ],
                'dialogue': [
                    (None, "You're carrying groceries up the stairs."),
                    (None, "The broken step you've reported three times gives way."),
                    (None, "You fall hard. Your ankle twists badly."),
                    ('Concerned Neighbor', "Oh my god! Are you okay?"),
                    ('You', "My ankle... I can't put weight on it."),
                    ('Concerned Neighbor', "We need to get you to the hospital."),
                    (None, "You think about the medical bills. But you can't walk.")
                ],
                'interactions': {}
            },

            'missed_work': {
                'npcs': [],
                'dialogue': [
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
                'dialogue': [
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
                        'dialogue': ["$700 exactly.", "Still $200 short.", "Maybe you miscounted? No..."]
                    }
                }
            },

            'eviction_threat': {
                'npcs': [
                    {'name': 'Landlord', 'x': 8, 'y': 10}
                ],
                'dialogue': [
                    ('Landlord', "You're late on rent."),
                    ('You', "I was injured on your broken stairs! I missed work!"),
                    ('Landlord', "Not my problem. Pay or quit."),
                    ('Landlord', "You have 3 days to pay in full or I start eviction."),
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
                'dialogue': [
                    ('City Inspector', "I'm here for the requested inspection."),
                    ('You', "Thank you for coming. Let me show you the violations."),
                    (None, "You walk through the apartment together."),
                    ('City Inspector', "Broken heater... that's a habitability violation."),
                    ('City Inspector', "Mold in the bathroom... health hazard."),
                    ('City Inspector', "Broken window locks... security violation."),
                    ('City Inspector', "I'm documenting 12 violations total."),
                    ('You', "What happens now?"),
                    ('City Inspector', "Your landlord has 30 days to fix these or face fines.")
                ],
                'interactions': {
                    'clipboard': {
                        'position': (6, 6),
                        'prompt': 'Review inspection report',
                        'dialogue': ["12 code violations documented", "Landlord must remedy within 30 days", "This is your leverage."]
                    }
                }
            },

            'negotiation': {
                'npcs': [
                    {'name': 'Landlord', 'x': 8, 'y': 6}
                ],
                'dialogue': [
                    ('Landlord', "Fine. I got your lawyer's letter."),
                    ('Landlord', "I'll fix the heater. And give you a payment plan for back rent."),
                    ('You', "What about the other violations?"),
                    ('Landlord', "The heater. That's it. Take it or leave it."),
                    (None, "It's not everything, but it's something."),
                    (None, "You accept. A small victory is still a victory.")
                ],
                'interactions': {}
            },

            # Chapter 6: The Ultimatum
            'building_sold': {
                'npcs': [],
                'dialogue': [
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
                'dialogue': [
                    ('Property Manager', "We'd like to make you an offer."),
                    ('Property Manager', "$2,000 cash if you vacate voluntarily within 60 days."),
                    ('You', "And if I don't?"),
                    ('Property Manager', "We'll proceed with eviction for the unpaid rent."),
                    ('Property Manager', "You still owe from when you were injured, right?"),
                    ('Property Manager', "An eviction on your record... that follows you forever."),
                    ('You', "I need time to think."),
                    ('Property Manager', "You have 48 hours to decide.")
                ],
                'interactions': {}
            },

            'impossible_choice': {
                'npcs': [],
                'dialogue': [
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
                        'dialogue': ["'Are you fighting or taking the money?'", "'I don't know yet...'", "'We need to decide together.'"]
                    }
                }
            },

            'final_decision': {
                'npcs': [],
                'dialogue': [
                    (None, "The deadline has arrived. You must choose."),
                    (None, "Option 1: Take the $2,000 and leave peacefully."),
                    (None, "Option 2: Fight the eviction with other tenants."),
                    (None, "This decision will change everything.")
                ],
                'interactions': {
                    'door': {
                        'position': (8, 10),
                        'prompt': 'Make your choice',
                        'trigger_activity': 'housing_choice'
                    }
                }
            },

            # Ending A
            'moving_out': {
                'npcs': [],
                'dialogue': [
                    (None, "You pack your belongings. Again."),
                    (None, "The $2,000 will cover a deposit elsewhere."),
                    (None, "You're not proud of this choice."),
                    (None, "But survival isn't about pride."),
                    (None, "It's about living to fight another day.")
                ],
                'interactions': {}
            },

            # Ending B
            'still_fighting': {
                'npcs': [
                    {'name': 'Fellow Tenant', 'x': 6, 'y': 5},
                    {'name': 'Organizer', 'x': 9, 'y': 5}
                ],
                'dialogue': [
                    ('Organizer', "The judge granted a 6-month stay!"),
                    ('Fellow Tenant', "We did it! We're still here!"),
                    ('You', "For now. But what about after 6 months?"),
                    ('Organizer', "We keep fighting. We keep organizing."),
                    ('Organizer', "This isn't over. It's just beginning."),
                    (None, "The apartment is still crappy. The heater barely works."),
                    (None, "But you learned something valuable: how to fight back."),
                    (None, "Sometimes that's the real victory.")
                ],
                'interactions': {}
            }
        }
    },

    # Library scenes for research and organizing
    'library': {
        'location_name': 'library',
        'description': 'Public library - for research and tenant organizing',
        'objectives': {
            'roommate_search': {
                'npcs': [
                    {'name': 'Librarian', 'x': 8, 'y': 4}
                ],
                'dialogue': [
                    ('Librarian', "Looking for roommate listings?"),
                    ('You', "Yeah, my rent just went up 15%."),
                    ('Librarian', "Try Facebook groups and Craigslist."),
                    (None, "You search for an hour."),
                    (None, "Every listing wants credit checks, references, deposits."),
                    (None, "Plus your studio is too small to legally share."),
                    (None, "The lease also forbids subletting."),
                    (None, "There's no way out of this.")
                ],
                'interactions': {
                    'computer': {
                        'position': (5, 6),
                        'prompt': 'Search for roommates',
                        'trigger_activity': 'roommate_search'
                    }
                }
            },

            'research_rights': {
                'npcs': [
                    {'name': 'Law Student', 'x': 10, 'y': 7}
                ],
                'dialogue': [
                    ('Law Student', "Researching tenant law?"),
                    ('You', "My landlord won't fix anything."),
                    ('Law Student', "Check the warranty of habitability statute."),
                    ('Law Student', "Landlords must maintain livable conditions."),
                    ('Law Student', "Document everything. Get it in writing."),
                    ('Law Student', "You might be able to withhold rent legally."),
                    ('You', "Really? That's allowed?"),
                    ('Law Student', "If done properly. Get legal help first.")
                ],
                'interactions': {
                    'law_book': {
                        'position': (10, 6),
                        'prompt': 'Read tenant rights',
                        'trigger_activity': 'tenant_rights_quiz'
                    }
                }
            },

            'tenant_union': {
                'npcs': [
                    {'name': 'Union Organizer', 'x': 7, 'y': 5},
                    {'name': 'Fellow Tenant 1', 'x': 5, 'y': 6},
                    {'name': 'Fellow Tenant 2', 'x': 9, 'y': 6}
                ],
                'dialogue': [
                    ('Union Organizer', "Welcome to the tenant union meeting."),
                    ('Fellow Tenant 1', "My landlord raised rent 20% last month."),
                    ('Fellow Tenant 2', "Mine won't fix the black mold."),
                    ('You', "Mine threatened eviction after I got injured."),
                    ('Union Organizer', "Together we have power. Alone we're victims."),
                    ('Union Organizer', "We share resources, knowledge, support."),
                    ('Union Organizer', "And when needed, we fight together."),
                    (None, "For the first time, you don't feel alone.")
                ],
                'interactions': {
                    'signup_sheet': {
                        'position': (7, 6),
                        'prompt': 'Join the union',
                        'dialogue': ["You write your name and contact info.", "You're part of something bigger now.", "Together, you might win."]
                    }
                }
            },

            'tenant_meeting': {
                'npcs': [
                    {'name': 'Building Organizer', 'x': 7, 'y': 5},
                    {'name': 'Tenant A', 'x': 4, 'y': 6},
                    {'name': 'Tenant B', 'x': 10, 'y': 6},
                    {'name': 'Tenant C', 'x': 7, 'y': 8}
                ],
                'dialogue': [
                    ('Building Organizer', "How many got the cash-for-keys offer?"),
                    ('Tenant A', "I did. $1,500 for me."),
                    ('Tenant B', "They offered me $2,000."),
                    ('Tenant C', "Only $1,000 for me. Why the difference?"),
                    ('Building Organizer', "They're trying to divide us."),
                    ('Building Organizer', "If we all refuse, they can't evict everyone."),
                    ('You', "But what if they try anyway?"),
                    ('Building Organizer', "Then we make it very public. Very expensive for them."),
                    (None, "The room buzzes with nervous energy. This is resistance.")
                ],
                'interactions': {
                    'strategy_board': {
                        'position': (7, 4),
                        'prompt': 'Review strategy',
                        'dialogue': ["Tenant rights hotline numbers", "Media contacts", "Legal aid resources", "Protest plans"]
                    }
                }
            }
        }
    },

    # Grocery store for work scenes
    'grocery_store': {
        'location_name': 'grocery_store',
        'description': 'Your workplace - where you struggle to earn enough',
        'objectives': {
            'second_job_hunt': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5}
                ],
                'dialogue': [
                    ('You', "Any chance of more hours? Or overtime?"),
                    ('Manager', "Sorry, company policy. No overtime."),
                    ('Manager', "I can give you 5 more hours a week, max."),
                    ('You', "That's only $75 more. I need another job."),
                    ('Manager', "The diner down the street is hiring night shift."),
                    (None, "Night shift means no sleep."),
                    (None, "But homelessness means no sleep either.")
                ],
                'interactions': {
                    'schedule': {
                        'position': (8, 6),
                        'prompt': 'Check work schedule',
                        'dialogue': ["Current: 20 hours/week", "Maximum: 25 hours/week", "Still not enough to survive."]
                    }
                }
            },

            'exhaustion_sets_in': {
                'npcs': [
                    {'name': 'Coworker', 'x': 6, 'y': 6}
                ],
                'dialogue': [
                    ('Coworker', "You okay? You look exhausted."),
                    ('You', "Working 60 hours between two jobs."),
                    ('Coworker', "That's not sustainable."),
                    ('You', "Neither is homelessness."),
                    (None, "You're falling asleep standing up."),
                    (None, "Making mistakes. Getting complaints."),
                    (None, "But what choice do you have?")
                ],
                'interactions': {}
            },

            'promotion_earned': {
                'npcs': [
                    {'name': 'Manager', 'x': 8, 'y': 5}
                ],
                'dialogue': [
                    ('Manager', "I have good news. You're being promoted to shift lead."),
                    ('You', "Really? What does that mean?"),
                    ('Manager', "$2 more per hour. More responsibility."),
                    ('Manager', "That's $320 more per month if you work full time."),
                    ('You', "I'll take it! Thank you!"),
                    (None, "It's not much, but it's something."),
                    (None, "Maybe now you can save a little.")
                ],
                'interactions': {
                    'name_tag': {
                        'position': (8, 6),
                        'prompt': 'Put on new name tag',
                        'dialogue': ["'Shift Lead'", "A small step up.", "Every dollar counts."]
                    }
                }
            }
        }
    },

    # Hospital for injury scene
    'hospital': {
        'location_name': 'hospital',
        'description': 'Emergency room - where bills pile up',
        'objectives': {
            'emergency_room': {
                'npcs': [
                    {'name': 'Nurse', 'x': 6, 'y': 5},
                    {'name': 'Doctor', 'x': 9, 'y': 5}
                ],
                'dialogue': [
                    ('Nurse', "What brings you in today?"),
                    ('You', "I fell on broken stairs. My ankle..."),
                    ('Nurse', "We'll get you an X-ray. Have a seat."),
                    (None, "Six hours pass. The pain is unbearable."),
                    ('Doctor', "Severe sprain. You need to stay off it for a week."),
                    ('You', "I can't miss work. I'll lose my apartment."),
                    ('Doctor', "If you don't rest it, you could cause permanent damage."),
                    (None, "The bill will come later. Thousands, probably."),
                    (None, "Another debt you can't pay.")
                ],
                'interactions': {
                    'discharge_papers': {
                        'position': (7, 6),
                        'prompt': 'Review discharge papers',
                        'dialogue': ["Diagnosis: Severe ankle sprain", "Treatment: Rest, ice, elevation", "Follow up in 2 weeks", "You can't afford any of this."]
                    }
                }
            }
        }
    },

    # Bank for financial scenes
    'bank': {
        'location_name': 'bank',
        'description': 'Local bank - trying to build financial stability',
        'objectives': {
            'secured_credit': {
                'npcs': [
                    {'name': 'Bank Teller', 'x': 7, 'y': 5}
                ],
                'dialogue': [
                    ('Bank Teller', "How can I help you today?"),
                    ('You', "I want to build credit. I have no credit history."),
                    ('Bank Teller', "We offer a secured credit card."),
                    ('Bank Teller', "You put down $200, that becomes your credit limit."),
                    ('You', "So I'm borrowing my own money?"),
                    ('Bank Teller', "Essentially, yes. But it builds credit history."),
                    ('You', "I'll do it. I need to break this cycle."),
                    (None, "You hand over $200 you can't really spare."),
                    (None, "But maybe it's an investment in your future.")
                ],
                'interactions': {
                    'application': {
                        'position': (7, 6),
                        'prompt': 'Fill out application',
                        'trigger_activity': 'credit_application'
                    }
                }
            },

            'small_savings': {
                'npcs': [
                    {'name': 'Bank Teller', 'x': 7, 'y': 5}
                ],
                'dialogue': [
                    ('Bank Teller', "Checking your balance?"),
                    ('You', "Yeah. I've been saving $50 a month."),
                    ('Bank Teller', "Your balance is $400."),
                    ('You', "It took 8 months to save that."),
                    ('Bank Teller', "Every bit helps. You're doing great."),
                    (None, "It's not much. One emergency could wipe it out."),
                    (None, "But it's more than you've ever had before."),
                    (None, "Maybe things are getting better. Slowly.")
                ],
                'interactions': {
                    'atm': {
                        'position': (5, 6),
                        'prompt': 'Check balance',
                        'dialogue': ["Savings: $400", "Checking: $87", "Total: $487", "Your entire net worth."]
                    }
                }
            }
        }
    },

    # School for education scenes
    'school': {
        'location_name': 'sarahs_place',  # Reusing Sarah's place as school
        'description': 'Community college - trying to build a better future',
        'objectives': {
            'night_school': {
                'npcs': [
                    {'name': 'Professor', 'x': 7, 'y': 4},
                    {'name': 'Classmate', 'x': 5, 'y': 6}
                ],
                'dialogue': [
                    ('Professor', "Welcome to Introduction to Business."),
                    ('Professor', "Classes are Tuesday and Thursday, 7-10 PM."),
                    ('Classmate', "You're new? What brings you here?"),
                    ('You', "Trying to get a better job. Better life."),
                    ('Classmate', "Same. Working full time?"),
                    ('You', "Yeah. Two jobs actually."),
                    ('Classmate', "This is going to be tough."),
                    (None, "But education is the only way out you can see."),
                    (None, "So you'll make it work. Somehow.")
                ],
                'interactions': {
                    'textbook': {
                        'position': (7, 6),
                        'prompt': 'Open textbook',
                        'dialogue': ["Business Fundamentals", "Cost: $200 (used)", "You'll eat ramen for a month to afford this."]
                    }
                }
            }
        }
    },

    # Rental office for new apartment search
    'rental_office': {
        'location_name': 'rental_office',
        'description': 'Rental office - searching for better housing',
        'objectives': {
            'better_apartment': {
                'npcs': [
                    {'name': 'Leasing Agent', 'x': 8, 'y': 5}
                ],
                'dialogue': [
                    ('Leasing Agent', "The one-bedroom is $1,200 a month."),
                    ('You', "I can afford that with my promotion."),
                    ('Leasing Agent', "Great! I'll just need to run a background check."),
                    ('Leasing Agent', "Any evictions or late payments?"),
                    ('You', "I... had some late payments. Medical emergency."),
                    ('Leasing Agent', "Hmm. That might be a problem."),
                    ('Leasing Agent', "We require perfect rental history."),
                    (None, "Even when you can afford it, the past haunts you."),
                    (None, "The system is designed to keep you down.")
                ],
                'interactions': {
                    'application': {
                        'position': (8, 6),
                        'prompt': 'Review application',
                        'dialogue': ["Credit check: $50", "Background check: $35", "Application fee: $100", "Non-refundable even if rejected."]
                    }
                }
            }
        }
    },

    # Courthouse for legal battle
    'courthouse': {
        'location_name': 'rental_office',  # Reusing rental office as courthouse
        'description': 'City courthouse - fighting eviction',
        'objectives': {
            'court_battle': {
                'npcs': [
                    {'name': 'Judge', 'x': 7, 'y': 3},
                    {'name': 'Landlord Lawyer', 'x': 5, 'y': 5},
                    {'name': 'Tenant Lawyer', 'x': 9, 'y': 5}
                ],
                'dialogue': [
                    ('Judge', "This is the matter of mass eviction at 54-33 Skyview."),
                    ('Landlord Lawyer', "The new owners have the right to renovate."),
                    ('Tenant Lawyer', "They're displacing 40 families with nowhere to go."),
                    ('You', "Your Honor, may I speak?"),
                    ('Judge', "Briefly."),
                    ('You', "We're not numbers. We're people. This is our home."),
                    ('You', "We've built a community. We've survived together."),
                    ('Judge', "I'm granting a 6-month stay of eviction."),
                    ('Judge', "Use that time to find housing or negotiate."),
                    (None, "It's not a permanent win. But it's time."),
                    (None, "Sometimes that's all you can hope for.")
                ],
                'interactions': {}
            }
        }
    },

    # New apartment ending
    'new_apartment': {
        'location_name': 'alex_apartment',  # Reusing Alex's apartment as the better place
        'description': 'A slightly better apartment - small victory',
        'objectives': {
            'new_apartment': {
                'npcs': [],
                'dialogue': [
                    (None, "You stand in your new apartment."),
                    (None, "It's not fancy. But the heat works."),
                    (None, "The windows lock. No visible mold."),
                    (None, "The $2,000 covered the deposit."),
                    (None, "You feel guilty about taking the money."),
                    (None, "But you're tired of fighting. So tired."),
                    (None, "Maybe this is what progress looks like."),
                    (None, "Not victory. Just slightly less defeat."),
                    (None, "Tomorrow you'll keep climbing."),
                    (None, "Because what else can you do?")
                ],
                'interactions': {
                    'window': {
                        'position': (10, 5),
                        'prompt': 'Look outside',
                        'dialogue': ["Your old building is being gutted.", "Luxury condos coming soon.", "The cycle continues."]
                    }
                }
            }
        }
    }
}
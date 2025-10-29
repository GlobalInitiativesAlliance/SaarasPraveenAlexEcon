"""
Alex's Apartment Interior - Illegal Subletting Narrative
Shows the cycle of housing instability through informal arrangements
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class AlexApartmentNarrative(NarrativeInterior):
    """Alex's apartment with multiple narrative phases"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track narrative progression
        self.alex_trust = 100  # Starts high, degrades over time
        self.days_lived = 0
        self.rent_paid = 0
        self.possessions_unpacked = False
        self.eviction_started = False
        self.packing_complete = False

        # Current activity tracking
        self.current_activity = None

        # Emotional state
        self.hope_level = 0  # Tracks emotional journey
        self.stability_achieved = False

        # Exit control
        self.should_exit = False
        self.exit_timer = 0

        # Track which objective phase we're in
        self.current_objective_phase = None
        self.phase_initialized = False

    def enter(self):
        """Override enter to set up apartment scene based on objective"""
        super().enter()

        # Determine which objective phase we're in
        current = self.game.objective_manager.get_current_objective()
        if current:
            # Reset state if objective changed
            if self.current_objective_phase != current.id:
                self.current_objective_phase = current.id
                self.phase_initialized = False
                self.interactive_objects.clear()
                self.completed_interactions.clear()

            # Initialize phase-specific content
            if not self.phase_initialized:
                self.initialize_phase(current.id)
                self.phase_initialized = True

        self.update_objective_display()

    def initialize_phase(self, phase_id):
        """Initialize specific narrative phase"""
        if phase_id == 'meet_alex':
            # Initial apartment viewing
            interactions = self.narrative_content['meet_alex']['interactions']
            for obj_name in ['examine_couch', 'check_kitchen', 'look_bedroom']:
                if obj_name in interactions:
                    self.add_interactive_object(obj_name, interactions[obj_name])

        elif phase_id == 'alex_room':
            # Room tour
            interactions = self.narrative_content['alex_room']['interactions']
            for obj_name in ['inspect_bathroom', 'check_window', 'examine_closet']:
                if obj_name in interactions:
                    self.add_interactive_object(obj_name, interactions[obj_name])

        elif phase_id == 'move_in':
            # Moving in phase
            interactions = self.narrative_content['move_in']['interactions']
            if 'unpack_belongings' in interactions:
                self.add_interactive_object('unpack_belongings', interactions['unpack_belongings'])

        elif phase_id == 'three_months_later':
            # Time skip - room looks lived in
            self.days_lived = 90
            self.stability_achieved = True
            interactions = self.narrative_content['three_months_later']['interactions']
            if 'talk_to_alex' in interactions:
                self.add_interactive_object('talk_to_alex', interactions['talk_to_alex'])

        elif phase_id == 'landlord_eviction':
            # Confrontation scene
            self.eviction_started = True
            interactions = self.narrative_content['landlord_eviction']['interactions']
            for obj_name in ['check_phone', 'review_documents', 'plead_with_landlord']:
                if obj_name in interactions:
                    self.add_interactive_object(obj_name, interactions[obj_name])

        elif phase_id == 'pack_again':
            # Forced to pack and leave
            interactions = self.narrative_content['pack_again']['interactions']
            if 'pack_belongings' in interactions:
                self.add_interactive_object('pack_belongings', interactions['pack_belongings'])

    def load_narrative_content(self):
        """Load the apartment narrative content"""
        return {
            'meet_alex': {
                'npcs': [
                    {'name': 'Alex', 'x': 8, 'y': 5},
                ],
                'dialogue_sequence': [
                    (None, "The apartment door opens. Alex looks exactly like their Facebook photo - friendly, disheveled."),
                    ("Alex", "Oh hey! You must be the person from Facebook! Come in, come in!"),
                    ("You", "Hi, yeah I messaged about the room..."),
                    ("Alex", "Perfect timing! I literally just finished cleaning. Well, 'cleaning'."),
                    (None, "You notice takeout containers on the coffee table and dishes in the sink."),
                    ("Alex", "Want some leftover pizza? I ordered way too much last night."),
                    ("You", "I'm okay, thanks. The place looks... nice."),
                    ("Alex", "Yeah! Rent control baby! My ex moved out last week so I need someone ASAP."),
                    ("Alex", "Rent's due in like 3 days. Landlord's super strict about late payments."),
                    ("You", "That's... very soon. What about a lease or paperwork?"),
                    ("Alex", "Oh we don't need all that formal stuff. Too complicated."),
                    ("Alex", "Just Venmo me monthly. Way easier for both of us!"),
                    (None, "Red flag #1: No legal protection. But what choice do you have?"),
                    ("You", "I guess that works... Can I see the room?")
                ],
                'interactions': {
                    'examine_couch': {
                        'position': (6, 6),
                        'prompt': 'Check couch',
                        'dialogue': [
                            "The couch is stained but looks comfortable.",
                            "There are blankets and pillows scattered around.",
                            "Looks like Alex sometimes sleeps here instead of their room.",
                            "Gaming controllers and empty energy drinks cover the coffee table."
                        ],
                        'required': False
                    },
                    'check_kitchen': {
                        'position': (11, 4),
                        'prompt': 'Inspect kitchen',
                        'dialogue': [
                            "Dishes are piled high in the sink.",
                            "The fridge hums loudly - sounds like it's struggling.",
                            "Takeout menus cover every surface.",
                            "At least all the appliances seem to work."
                        ],
                        'required': False
                    },
                    'look_bedroom': {
                        'position': (8, 8),
                        'prompt': 'View your room',
                        'dialogue': [
                            "The room is completely empty.",
                            "Just worn carpet and off-white walls.",
                            "There's a concerning water stain on the ceiling.",
                            "But it's a room. Your own room. Finally."
                        ],
                        'required': True
                    }
                }
            },

            'alex_room': {
                'npcs': [
                    {'name': 'Alex', 'x': 8, 'y': 5},
                ],
                'dialogue_sequence': [
                    ("Alex", "So this would be your room. Previous roommate left the closet door."),
                    ("Alex", "That's about all they left though. No furniture or anything."),
                    ("You", "It's... perfect. I don't have much anyway."),
                    ("Alex", "Oh good! Some people expect furnished rooms. Can't help with that."),
                    (None, "You notice mold in the corner where the walls meet."),
                    ("You", "Is that... water damage on the ceiling?"),
                    ("Alex", "Oh yeah, upstairs neighbor's washing machine leaked once."),
                    ("Alex", "Landlord said he'd fix it. That was like 6 months ago."),
                    (None, "Red flag #2: Negligent landlord who doesn't know you exist."),
                    ("Alex", "Bathroom's shared. I'm not super clean but I try."),
                    ("Alex", "Well, I say I try. I don't really try."),
                    ("You", "That's fine. I'm just grateful for a place."),
                    ("Alex", "Utilities are split 50/50. Internet's included though!"),
                    ("Alex", "Sometimes I'm late paying bills but we've never lost power!"),
                    ("Alex", "Well, only twice. But they turned it back on quick!"),
                    (None, "Every revelation is worse, but you're desperate.")
                ],
                'interactions': {
                    'inspect_bathroom': {
                        'position': (10, 6),
                        'prompt': 'Check bathroom',
                        'dialogue': [
                            "The bathroom needs serious cleaning.",
                            "Black mold creeps along the shower tiles.",
                            "The toilet runs constantly.",
                            "The mirror is cracked in one corner.",
                            "Still better than the shelter's communal bathroom."
                        ],
                        'required': True
                    },
                    'check_window': {
                        'position': (8, 3),
                        'prompt': 'Look out window',
                        'dialogue': [
                            "Third floor view of the city.",
                            "You can see people living their normal lives below.",
                            "For a moment, you imagine being one of them.",
                            "Having a real home, stability, a future.",
                            "Maybe this is the start of that."
                        ],
                        'required': False
                    },
                    'examine_closet': {
                        'position': (6, 8),
                        'prompt': 'Check closet',
                        'dialogue': [
                            "Small but functional closet.",
                            "The door is off its tracks but still works.",
                            "Previous tenant left some hangers.",
                            "You could fit all your possessions in one corner."
                        ],
                        'required': False
                    }
                }
            },

            'move_in': {
                'npcs': [
                    {'name': 'Alex', 'x': 8, 'y': 5},
                    {'name': 'Suspicious Neighbor', 'x': 12, 'y': 10}
                ],
                'dialogue_sequence': [
                    (None, "You arrive with your single bag of possessions."),
                    ("You", "Hey, I'm here with my stuff..."),
                    ("Alex", "(on phone) Yeah babe, they're moving in now..."),
                    ("Alex", "(on phone) No, didn't do a background check..."),
                    ("Alex", "(on phone) Because they had cash! First month upfront!"),
                    (None, "You overhear concerning parts of the conversation."),
                    ("Alex", "(hangs up) Sorry! Girlfriend drama. You know how it is."),
                    ("You", "Is everything okay with me moving in?"),
                    ("Alex", "Totally! She's just paranoid about strangers."),
                    (None, "Red flag #3: Relationship issues affecting your housing."),
                    ("Suspicious Neighbor", "(from hallway) Another one, Alex? Really?"),
                    ("Alex", "Mind your business, Karen!"),
                    ("Suspicious Neighbor", "Landlord's gonna find out eventually..."),
                    ("Alex", "(nervous laugh) She's crazy. Don't worry about her."),
                    (None, "Red flag #4: You're clearly not the first unofficial tenant."),
                    ("Alex", "So yeah! Make yourself at home! Mi casa es su casa!"),
                    ("Alex", "Just... maybe don't talk to the neighbors too much."),
                    ("Alex", "Or the landlord if you see him. Actually, just avoid everyone."),
                    ("You", "I'll be quiet. You won't even know I'm here."),
                    ("Alex", "Perfect! That's the spirit!")
                ],
                'interactions': {
                    'unpack_belongings': {
                        'position': (8, 8),
                        'prompt': 'Unpack your things',
                        'trigger_activity': 'packing_game',
                        'dialogue': None,
                        'required': True
                    }
                }
            },

            'three_months_later': {
                'npcs': [
                    {'name': 'Alex', 'x': 8, 'y': 5},
                ],
                'dialogue_sequence': [
                    (None, "Three months have passed. The room finally feels like home."),
                    (None, "You've added small touches - a lamp, some books, even a small plant."),
                    (None, "You've been paying rent on time. Alex has been decent."),
                    (None, "For the first time since aging out, you feel stable."),
                    (None, "That's when Alex knocks on your door."),
                    ("Alex", "Hey... we need to talk about something."),
                    ("You", "What's wrong? I paid rent already."),
                    ("Alex", "No, no, it's not that. It's..."),
                    (None, "Alex can't make eye contact. Your stomach drops."),
                ],
                'interactions': {
                    'talk_to_alex': {
                        'position': (8, 5),
                        'prompt': 'Hear Alex out',
                        'dialogue': [
                            "Alex: 'So remember my girlfriend?'",
                            "You: 'Yeah...'",
                            "Alex: 'Well... we're moving in together.'",
                            "You: 'That's... great for you?'",
                            "Alex: 'Yeah so... she wants to move in here. Next week.'",
                            "You: (stunned) 'Next week?!'",
                            "Alex: 'I know it's sudden but she gave me an ultimatum.'",
                            "You: 'But I live here! I've been paying rent!'",
                            "Alex: 'I know, I know! I feel terrible!'",
                            "Alex: 'I'll give you your deposit back... oh wait, you didn't pay one.'",
                            "Alex: 'Look, you can crash on the couch for a few days?'",
                            "You: 'Alex, I need more than a few days to find somewhere!'",
                            "Alex: 'The thing is... the landlord doesn't even know you live here.'",
                            "Alex: 'If he finds out, we're both screwed.'",
                            "You: 'So I have no rights. No recourse. Nothing.'",
                            "Alex: 'I'm really sorry. I didn't plan this.'",
                            "You: 'No one ever plans to screw me over. It just happens.'",
                            "",
                            "The stability you thought you'd found crumbles instantly.",
                            "Three months of believing you'd escaped the cycle.",
                            "But you were never safe. You were never secure.",
                            "You were just borrowing time in someone else's life."
                        ],
                        'required': True
                    }
                }
            },

            'landlord_eviction': {
                'npcs': [
                    {'name': 'Landlord', 'x': 8, 'y': 10},
                    {'name': 'Alex', 'x': 6, 'y': 5},
                    {'name': 'Girlfriend', 'x': 7, 'y': 5}
                ],
                'dialogue_sequence': [
                    (None, "LOUD KNOCKING on the door."),
                    ("Landlord", "CHEN! Open up! I know you're in there!"),
                    ("Alex", "(panicking) Shit shit shit..."),
                    (None, "The door opens. A large man in a cheap suit storms in."),
                    ("Landlord", "Who the hell is this?"),
                    (None, "He's pointing directly at you."),
                    ("Alex", "They're just... visiting?"),
                    ("You", "I live here. I've been paying rent for three months."),
                    ("Landlord", "Not to ME you haven't! This is a lease violation!"),
                    ("Landlord", "You're subletting without permission!"),
                    ("Alex", "It's not subletting! They're just helping with rent!"),
                    ("Landlord", "That's literally what subletting IS, you idiot!"),
                    ("Girlfriend", "(to Alex) I told you this would happen!"),
                    ("Landlord", "Everyone out. NOW. Or I call the cops."),
                    ("You", "But I have nowhere to go!"),
                    ("Landlord", "Not my problem. You're trespassing."),
                    ("You", "I have rights! Tenant rights!"),
                    ("Landlord", "(laughing) You're not a tenant. You're nothing."),
                    ("Landlord", "Your name isn't on anything. You don't exist here."),
                    ("Landlord", "You're a ghost. And ghosts don't have rights."),
                    ("Alex", "I'm sorry... I'm so sorry..."),
                    ("Girlfriend", "Alex, let's just go. This isn't our problem."),
                    ("Landlord", "Five minutes. Then I call the police."),
                    (None, "The brutal reality: without paperwork, you're nobody.")
                ],
                'interactions': {
                    'check_phone': {
                        'position': (10, 7),
                        'prompt': 'Check for help',
                        'dialogue': [
                            "You pull out your phone with shaking hands.",
                            "Contacts: Almost empty.",
                            "The shelter hotline.",
                            "A few acquaintances from the library.",
                            "No one who could help. No one who would care.",
                            "Battery: 31%. Even your phone is giving up."
                        ],
                        'required': True
                    },
                    'review_documents': {
                        'position': (8, 6),
                        'prompt': 'Look for proof',
                        'dialogue': [
                            "You frantically search for anything with your name.",
                            "Venmo payments to Alex - not legal proof.",
                            "No lease. No rental agreement. No receipts.",
                            "You paid cash. You trusted. You were foolish.",
                            "In the eyes of the law, you never lived here."
                        ],
                        'required': True
                    },
                    'plead_with_landlord': {
                        'position': (8, 9),
                        'prompt': 'Beg for time',
                        'dialogue': [
                            "You: 'Please, just give me a week to find something.'",
                            "Landlord: 'Get out or I call the cops. Final warning.'",
                            "You: 'I've been a good tenant! I'm quiet, I pay on time!'",
                            "Landlord: 'You're NOT a tenant!'",
                            "You: 'Where am I supposed to go?!'",
                            "Landlord: 'Try the shelter. Where you belong.'",
                            "",
                            "His words hit like physical blows.",
                            "Where you belong. Like you're a different species.",
                            "Like you deserve this cycle of instability."
                        ],
                        'required': True
                    }
                }
            },

            'pack_again': {
                'npcs': [
                    {'name': 'Alex', 'x': 8, 'y': 5},
                ],
                'dialogue_sequence': [
                    (None, "You're in your room - former room - packing in silence."),
                    ("Alex", "(from doorway) I... I found this in my wallet."),
                    (None, "Alex hands you $50."),
                    ("You", "Guilt money?"),
                    ("Alex", "I really didn't mean for this to happen."),
                    ("You", "But it did. And I'm the one who pays."),
                    ("Alex", "Where will you go?"),
                    ("You", "Back to the shelter. If they have space."),
                    ("Alex", "Jesus... I didn't know it was that bad."),
                    ("You", "You never asked."),
                    ("Girlfriend", "(from other room) Alex! Are they gone yet?!"),
                    ("Alex", "Look, maybe in a few months—"),
                    ("You", "Don't. Just... don't."),
                    (None, "You zip up your bag. Somehow it feels lighter than before."),
                    (None, "Not because you have less."),
                    (None, "Because you have less hope."),
                    (None, "Hope weighs more than you realized.")
                ],
                'interactions': {
                    'pack_belongings': {
                        'position': (8, 8),
                        'prompt': 'Pack your things',
                        'trigger_activity': 'packing_game_exit',
                        'dialogue': None,
                        'required': True
                    }
                }
            }
        }

    def update_objective_display(self):
        """Update objective text based on apartment progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'meet_alex':
            if self.narrative_active and self.sequence_index < 5:
                current.dynamic_description = "Meeting Alex..."
            elif 'look_bedroom' not in self.completed_interactions:
                current.dynamic_description = "Check out the apartment"
                current.progress_text = "View the room"
            else:
                current.dynamic_description = "Deciding whether to risk it..."

        elif current.id == 'alex_room':
            completed = len(self.completed_interactions)
            if completed < 1:
                current.dynamic_description = "Touring your potential room"
                current.progress_text = "Inspect the space"
            else:
                current.dynamic_description = "Red flags everywhere, but it's shelter"

        elif current.id == 'move_in':
            if not self.possessions_unpacked:
                current.dynamic_description = "Moving in with what little you have"
                current.progress_text = "Unpack belongings"
            else:
                current.dynamic_description = "Settling into your new 'home'"

        elif current.id == 'three_months_later':
            if self.narrative_active:
                current.dynamic_description = "Three months of stability... ending"
            elif 'talk_to_alex' not in self.completed_interactions:
                current.dynamic_description = "Alex needs to talk..."
                current.progress_text = "Hear the bad news"
            else:
                current.dynamic_description = "Processing the betrayal..."

        elif current.id == 'landlord_eviction':
            checks = len(self.completed_interactions)
            if checks < 3:
                current.dynamic_description = f"Facing eviction ({checks}/3)"
                current.progress_text = "No legal recourse"
            else:
                current.dynamic_description = "You have no rights here..."

        elif current.id == 'pack_again':
            if not self.packing_complete:
                current.dynamic_description = "Forced to leave. Again."
                current.progress_text = "Pack your things"
            else:
                current.dynamic_description = "Back to square one..."

    def interact_with_object(self, name):
        """Handle apartment-specific interactions"""
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'meet_alex'

        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})

        if name in interactions:
            interaction = interactions[name]

            # Launch activity if specified
            trigger = interaction.get('trigger_activity')

            if trigger == 'packing_game':
                self.launch_packing_game(mode='unpack')
                return
            elif trigger == 'packing_game_exit':
                self.launch_packing_game(mode='pack')
                return

        # Use parent's interaction handling
        super().interact_with_object(name)

        self.update_objective_display()

        # Handle phase completions
        if current_narrative_id == 'meet_alex' and 'look_bedroom' in self.completed_interactions:
            # Auto-progress after seeing the room
            self.should_exit = True
            self.exit_timer = 2.0

        elif current_narrative_id == 'alex_room' and len(self.completed_interactions) >= 1:
            # Progress after bathroom inspection
            self.should_exit = True
            self.exit_timer = 2.0

        elif current_narrative_id == 'three_months_later' and 'talk_to_alex' in self.completed_interactions:
            # Move to eviction scene
            self.game.objective_manager.complete_current_objective()
            self.enter()  # Re-initialize for landlord_eviction

        elif current_narrative_id == 'landlord_eviction' and len(self.completed_interactions) >= 3:
            # All desperate attempts failed
            self.game.objective_manager.complete_current_objective()
            self.enter()  # Re-initialize for pack_again

    def launch_packing_game(self, mode='unpack'):
        """Launch the packing mini-game"""
        from src.activities.packing_game import PackingGame

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = PackingGame(self.game.objective_manager, mode=mode)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            return

        # Use parent's event handling
        super().handle_event(event)

    def update(self, dt):
        """Update with activity management and emotional states"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                # Handle completion based on activity type
                if self.current_objective_phase == 'move_in':
                    self.possessions_unpacked = True
                    self.hope_level = 50  # Some hope
                elif self.current_objective_phase == 'pack_again':
                    self.packing_complete = True
                    self.hope_level = 0  # No hope left
                    self.should_exit = True
                    self.exit_timer = 3.0

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                self.update_objective_display()

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Complete objective and handle transitions
                current = self.game.objective_manager.get_current_objective()
                if current:
                    if current.id in ['meet_alex', 'alex_room']:
                        # Progress to next phase
                        self.game.objective_manager.complete_current_objective()
                        next_obj = self.game.objective_manager.get_current_objective()
                        if next_obj and next_obj.id in ['alex_room', 'move_in']:
                            # Continue in same interior
                            self.enter()
                            self.should_exit = False
                        else:
                            # Exit interior
                            self.active = False
                    elif current.id == 'pack_again':
                        # Final exit - back to shelter
                        self.game.objective_manager.complete_current_objective()
                        self.active = False
                        # Show message about returning to shelter
                        if hasattr(self, 'dialogue_box'):
                            self.dialogue_box.show(None, "You head back to the emergency shelter... if they have space.")

    def draw(self, screen):
        """Draw apartment interior with emotional overlay"""
        # Draw base interior
        super().draw(screen)

        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return

        # Emotional state visualization
        if self.current_objective_phase in ['landlord_eviction', 'pack_again']:
            # Dark vignette for despair
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            overlay.set_alpha(50)
            overlay.fill((0, 0, 30))  # Dark blue tint
            screen.blit(overlay, (0, 0))

            # Add subtle screen shake during eviction
            if self.current_objective_phase == 'landlord_eviction' and self.eviction_started:
                shake_x = pygame.time.get_ticks() % 100 / 50 - 1
                shake_y = pygame.time.get_ticks() % 150 / 75 - 1
                screen.scroll(int(shake_x * 2), int(shake_y * 2))

        # Hope indicator
        if self.hope_level > 0:
            font = pygame.font.Font(None, 20)
            hope_text = f"Hope: {'▮' * (self.hope_level // 10)}"
            color = (100, 200, 100) if self.hope_level > 30 else (200, 100, 100)
            hope_surf = font.render(hope_text, True, color)
            screen.blit(hope_surf, (10, 10))

        # Days lived counter
        if self.days_lived > 0:
            font = pygame.font.Font(None, 20)
            days_text = f"Days here: {self.days_lived}"
            days_surf = font.render(days_text, True, (200, 200, 200))
            screen.blit(days_surf, (10, 35))

        # Warning during eviction
        if self.current_objective_phase == 'landlord_eviction':
            font = pygame.font.Font(None, 36)
            warning_text = "! EVICTION IN PROGRESS !"
            warning_surf = font.render(warning_text, True, (255, 50, 50))
            x = self.SCREEN_WIDTH // 2 - warning_surf.get_width() // 2
            y = 50
            # Flashing effect
            if int(pygame.time.get_ticks() / 500) % 2:
                screen.blit(warning_surf, (x, y))
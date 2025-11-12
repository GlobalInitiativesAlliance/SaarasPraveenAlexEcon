"""
Emergency Shelter Interior with Check-in Process
"""
import pygame
import random
from src.interiors.narrative_interior import NarrativeInterior

class EmergencyShelterNarrative(NarrativeInterior):
    """Emergency shelter with intake process narrative"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)

        # Track shelter progress
        self.intake_complete = False
        self.bed_assigned = False
        self.current_activity = None

        # Exit timer for auto-exit after completion
        self.should_exit = False
        self.exit_timer = 0

        # Losing stuff tracking
        self.backpack_searched = False
        self.missing_items_found = []
        self.exhaustion_level = 0
        self.flashback_active = False
        self.flashback_timer = 0
        self.current_flashback = None
        
    def enter(self):
        """Override enter to set up shelter scene"""
        super().enter()

        # Check which objective we're on
        current = self.game.objective_manager.get_current_objective()
        if current:
            if current.id == 'reality_check':
                # Add intake desk immediately
                interactions = self.narrative_content['reality_check']['interactions']
                if 'intake_desk' in interactions:
                    self.add_interactive_object('intake_desk', interactions['intake_desk'])
                    if 'intake_desk' in self.completed_interactions:
                        self.completed_interactions.remove('intake_desk')

            elif current.id == 'losing_stuff':
                # Set up losing stuff scenario
                self.exhaustion_level = 100  # Coming from Mike's with no sleep
                interactions = self.narrative_content['losing_stuff']['interactions']
                for obj_name in ['shelter_bed', 'backpack_check', 'lost_and_found']:
                    if obj_name in interactions:
                        self.add_interactive_object(obj_name, interactions[obj_name])

                # Start with exhaustion dialogue
                self.start_narrative_sequence('losing_stuff')

            elif current.id == 'wearing_out_welcome':
                # Set up wearing out welcome scenario - Day 15, no options
                self.day_count = 15
                self.shelter_full = True  # Shelter at capacity
                interactions = self.narrative_content['wearing_out_welcome']['interactions']
                for obj_name in ['phone_check', 'intake_desk_return', 'waiting_area']:
                    if obj_name in interactions:
                        self.add_interactive_object(obj_name, interactions[obj_name])

                # Start with desperation dialogue
                self.start_narrative_sequence('wearing_out_welcome')

            elif current.id == 'six_months_surviving':
                # TLP acceptance call after 6 months
                self.months_survived = 6
                interactions = self.narrative_content.get('six_months_surviving', {}).get('interactions', {})

                for obj_name, obj_data in interactions.items():
                    self.add_interactive_object(obj_name, obj_data)

                # Start acceptance call sequence
                self.start_narrative_sequence('six_months_surviving')

        self.update_objective_display()
    
    def load_narrative_content(self):
        """Load the shelter narrative content"""
        return {
            'reality_check': {
                'npcs': [
                    {'name': 'Intake Worker', 'x': 8, 'y': 4},
                    {'name': 'Security Guard', 'x': 3, 'y': 8}
                ],
                'dialogue_sequence': [
                    ("Security Guard", "First time at the shelter? You'll need to check in at the desk."),
                    ("You", "Yes, I just aged out of foster care today..."),
                    ("Security Guard", "Sorry to hear that, kid. Talk to intake, they'll get you sorted."),
                    (None, "The shelter is crowded and loud. The smell of disinfectant can't mask everything else."),
                    (None, "You see people of all ages here. Some look like they've been here a while.")
                ],
                'interactions': {
                    'intake_desk': {
                        'position': (8, 3),
                        'prompt': 'Check in at desk',
                        'trigger_activity': 'shelter_checkin',
                        'dialogue': None,
                        'required': True
                    },
                    'exit_door': {
                        'position': (8, 11),
                        'prompt': 'Go to your bed',
                        'dialogue': [
                            "Bed 47. Bottom bunk in the back corner.",
                            "Your few possessions feel even smaller in this huge room.",
                            "The person in the top bunk is already asleep. Or pretending to be.",
                            "Tomorrow you'll need to be out by 6 AM to look for work.",
                            "But for tonight, you have somewhere safe to sleep.",
                            "You lie down on the thin mattress, exhausted from the day.",
                            "Tomorrow you'll start searching for real housing..."
                        ],
                        'required': False
                    }
                }
            },

            'losing_stuff': {
                'npcs': [
                    {'name': 'Shelter Worker', 'x': 8, 'y': 4},
                    {'name': 'Another Resident', 'x': 5, 'y': 7}
                ],
                'dialogue_sequence': [
                    (None, "After Mike's chaotic apartment, you're back at the shelter."),
                    (None, "Your body sways from exhaustion. 8+ hours without sleep."),
                    ("Shelter Worker", "You look rough. Tough night?"),
                    ("You", "Couch surfing didn't work out..."),
                    ("Shelter Worker", "Never does. That's why we're always full.")
                ],
                'interactions': {
                    'shelter_bed': {
                        'position': (10, 8),
                        'prompt': 'Collapse on bed',
                        'dialogue': [
                            "You drop onto the thin mattress, still fully clothed.",
                            "Wait... you need your work uniform for tomorrow.",
                            "You force yourself to sit up and check your bag."
                        ],
                        'required': True
                    },
                    'backpack_check': {
                        'position': (10, 9),
                        'prompt': 'Search backpack',
                        'trigger_activity': 'backpack_investigation',
                        'dialogue': None,
                        'required': True
                    },
                    'lost_and_found': {
                        'position': (8, 3),
                        'prompt': 'Check lost & found',
                        'dialogue': [
                            "You desperately check the shelter's lost and found box.",
                            "Old jackets, single shoes, broken umbrellas...",
                            "Nothing yours. Of course not.",
                            "Your stuff is scattered across the city.",
                            "Sarah's place. Mike's bathroom. Alex's apartment.",
                            "You'll never get it all back."
                        ],
                        'required': False
                    }
                }
            },

            'wearing_out_welcome': {
                'npcs': [
                    {'name': 'Intake Worker', 'x': 8, 'y': 4},
                    {'name': 'Waiting Resident', 'x': 5, 'y': 6},
                    {'name': 'Security Guard', 'x': 3, 'y': 8}
                ],
                'dialogue_sequence': [
                    (None, "Day 15. You're back at the shelter. Again."),
                    (None, "Your phone shows a graveyard of unanswered messages."),
                    ("Intake Worker", "Back again? Let me guess - ran out of couches."),
                    ("You", "Everyone's already helped..."),
                    ("Intake Worker", "It's always Day 10 to 20 when they come back."),
                    ("Intake Worker", "Friends want to help, but they have limits."),
                    (None, "You're not anyone's responsibility. But whose are you?"),
                    ("Waiting Resident", "First time back? Won't be the last."),
                    ("Waiting Resident", "Average is 3-4 cycles before finding anything stable."),
                    (None, "The cycle. You're trapped in the cycle.")
                ],
                'interactions': {
                    'phone_check': {
                        'position': (6, 7),
                        'prompt': 'Check messages',
                        'trigger_activity': 'text_desperation',
                        'dialogue': None,
                        'required': True
                    },
                    'intake_desk_return': {
                        'position': (8, 3),
                        'prompt': 'Talk to intake',
                        'dialogue': [
                            "You approach the familiar intake desk.",
                            "Same worker. Same forms. Same questions.",
                            "But this time, there's a 'NO VACANCY' sign.",
                            "Worker: 'We're full. You can wait, but...'",
                            "Worker: 'Honestly? Could be hours. Could be tomorrow.'",
                            "You have nowhere else to go. You wait."
                        ],
                        'required': True
                    },
                    'waiting_area': {
                        'position': (5, 8),
                        'prompt': 'Sit and wait',
                        'dialogue': [
                            "You sit in the plastic chair. It's 7 PM.",
                            "8 PM. Still waiting. More people arriving.",
                            "9 PM. Someone you know from foster care walks in.",
                            "They avoid eye contact. You both know why you're here.",
                            "10 PM. 'Sorry, we're full for tonight.'",
                            "Where do you go when the shelter is full?"
                        ],
                        'required': True
                    }
                }
            },

            'shelter_reality': {
                'dialogue_sequence': [
                    ("Intake Worker", "Your intake is complete. You're assigned to bed 47."),
                    ("Intake Worker", "Lights out at 10 PM, wake up is 5:30 AM. You need to be out by 6."),
                    ("Intake Worker", "No drugs, no alcohol, no weapons. Break the rules and you're banned."),
                    ("You", "What about during the day? Can I leave my things here?"),
                    ("Intake Worker", "No storage. Take everything with you when you leave."),
                    ("Intake Worker", "There's a job placement board by the exit. Check it in the morning."),
                    (None, "You realize this is temporary. Very temporary. You need a plan.")
                ],
                'interactions': {}
            },

            'six_months_surviving': {
                'npcs': [
                    {'name': 'Case Worker', 'x': 8, 'y': 4}
                ],
                'dialogue_sequence': [
                    (None, "It's been 6 months since you applied for the TLP."),
                    (None, "180 days of shelters, couches, cars, and desperation."),
                    (None, "Your phone rings. Unknown number."),
                    ("You", "Hello?"),
                    ("Case Worker (phone)", "Is this the applicant for the Transitional Living Program?"),
                    ("You", "Yes! Yes, this is them!"),
                    ("Case Worker (phone)", "Good news. A spot opened up. Can you move in tomorrow?"),
                    ("You", "Tomorrow? Yes! Absolutely! Thank you!"),
                    ("Case Worker (phone)", "Be at the TLP house at 9 AM. Bring your documents."),
                    (None, "After 6 months of hell... finally, stable housing.")
                ],
                'interactions': {
                    'phone_ringing': {
                        'position': (5, 5),
                        'prompt': 'Answer phone',
                        'dialogue': [
                            "Your phone is ringing. Unknown number.",
                            "You answer with shaking hands.",
                            "It's the call you've been waiting for.",
                            "After 6 months... finally."
                        ],
                        'required': True
                    }
                }
            }
        }
    
    def update_objective_display(self):
        """Update objective text based on shelter progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return
        
        if current.id == 'reality_check':
            if self.narrative_active and self.sequence_index < 3:
                current.dynamic_description = "Listen to the security guard..."
            elif not self.intake_complete:
                current.dynamic_description = "Complete shelter intake process"
                current.progress_text = "Check in at the intake desk"
            elif self.intake_complete and 'exit_door' not in self.completed_interactions:
                current.dynamic_description = "You're checked in. Find your bed."
                current.progress_text = "Bed 47 assigned"
            elif 'exit_door' in self.completed_interactions:
                current.dynamic_description = "Settling in for the night..."
                current.progress_text = None
        
        elif current.id == 'shelter_reality':
            if self.narrative_active:
                current.dynamic_description = "Understanding shelter life..."
            else:
                current.dynamic_description = "First night in the shelter"

        elif current.id == 'six_months_surviving':
            if self.narrative_active:
                current.dynamic_description = "The call you've been waiting for..."
            else:
                current.dynamic_description = "TLP acceptance after 6 months!"
    
    def interact_with_object(self, name):
        """Handle shelter-specific interactions"""
        print(f"DEBUG: Interacting with {name}")
        print(f"DEBUG: Current activity: {self.current_activity}")
        print(f"DEBUG: Intake complete: {self.intake_complete}")
        
        # Get current narrative content
        current_obj = self.game.objective_manager.get_current_objective() if hasattr(self.game, 'objective_manager') else None
        current_narrative_id = current_obj.id if current_obj else 'reality_check'
        
        current_content = self.narrative_content.get(current_narrative_id, {})
        interactions = current_content.get('interactions', {})
        
        if name in interactions:
            interaction = interactions[name]
            
            # Launch activity if specified
            trigger = interaction.get('trigger_activity')
            
            # Check if already completed intake
            if trigger == 'shelter_checkin' and self.intake_complete:
                self.dialogue_box.show(None, "You've already completed the intake process.")
                return
            
            if trigger == 'shelter_checkin':
                print("DEBUG: Launching shelter check-in")
                self.launch_shelter_checkin()
                return
            elif trigger == 'backpack_investigation':
                print("DEBUG: Launching backpack investigation")
                self.launch_backpack_investigation()
                return
            elif trigger == 'text_desperation':
                print("DEBUG: Launching text desperation activity")
                self.launch_text_desperation()
                return
        
        # Handle non-activity interactions
        if name != 'intake_desk':
            super().interact_with_object(name)
        
        self.update_objective_display()
        
        # Handle exit door completion
        if name == 'exit_door' and 'exit_door' in self.completed_interactions:
            current = self.game.objective_manager.get_current_objective()
            if current and current.id == 'reality_check':
                # Start exit timer to let final dialogue show
                self.should_exit = True
                self.exit_timer = 3.0  # 3 seconds to read the final messages
                # Complete objective will happen when timer expires
    
    def launch_shelter_checkin(self):
        """Launch the shelter check-in mini-game"""
        from src.activities.shelter_checkin import EmergencyShelterCheckIn
        
        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = EmergencyShelterCheckIn(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()
            
            # Set as current activity
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity
    
    def launch_backpack_investigation(self):
        """Launch the backpack investigation activity"""
        from src.activities.backpack_investigation import BackpackInvestigation

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = BackpackInvestigation(self.game)
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity

    def launch_text_desperation(self):
        """Launch the text messaging desperation activity for wearing_out_welcome"""
        from src.activities.text_desperation import TextDesperation

        # Clear any active dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.hide()

        # Create and start the activity
        activity = TextDesperation(self.game)
        activity.start()  # Properly initialize the activity
        self.current_activity = activity

        # Set it in the game/objective manager if available
        if hasattr(self.game, 'objective_manager'):
            self.game.objective_manager.current_activity = activity

    def add_exit_interaction(self):
        """Add the exit door after completing intake"""
        if 'reality_check' in self.narrative_content:
            exit_data = self.narrative_content['reality_check']['interactions']['exit_door']
            self.add_interactive_object('exit_door', exit_data)

            # Show completion message
            self.dialogue_box.show(None, "You're all checked in. Your bed is ready.")
    
    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first - BLOCK EVERYTHING ELSE
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            if event.type == pygame.KEYDOWN:
                print(f"[EMERGENCY_SHELTER] KEYDOWN event: key={event.key}, char='{chr(event.key) if 32 <= event.key <= 126 else '?'}', forwarding to activity")
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.TEXTINPUT:
                # Handle text input for activities that support it
                print(f"[EMERGENCY_SHELTER] TEXTINPUT event received: '{event.text}'")
                if hasattr(self.current_activity, 'handle_text_input'):
                    print(f"[EMERGENCY_SHELTER] Forwarding to activity's handle_text_input")
                    self.current_activity.handle_text_input(event.text)
                else:
                    print(f"[EMERGENCY_SHELTER] Activity does not have handle_text_input method")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
            # CRITICAL: Return immediately, don't process ANY other events
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current = self.game.objective_manager.get_current_objective()
                
                if current and current.id == 'reality_check':
                    if not self.intake_complete:
                        self.dialogue_box.show(None, "You need to complete the intake process first!")
                        return
                    elif 'exit_door' not in self.completed_interactions:
                        self.dialogue_box.show(None, "You should go to your assigned bed.")
                        return
        
        # Use parent's event handling
        super().handle_event(event)
    
    def get_nearby_object(self):
        """Allow re-interaction with intake desk"""
        player_tile_x = int(self.player_pixel_x // self.TILE_SIZE)
        player_tile_y = int(self.player_pixel_y // self.TILE_SIZE)
        
        for name, obj in self.interactive_objects.items():
            # Always allow intake desk interaction
            if name == 'intake_desk':
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj
            # Normal logic for other objects
            elif name not in self.completed_interactions:
                if abs(player_tile_x - obj['x']) <= 1 and abs(player_tile_y - obj['y']) <= 1:
                    return name, obj
        
        return None, None
    
    def update(self, dt):
        """Update with activity management"""
        super().update(dt)

        # Update current activity if active
        if hasattr(self, 'current_activity') and self.current_activity is not None:
            if self.current_activity.active:
                self.current_activity.update(dt)

            # Check if activity completed
            if self.current_activity.completed:
                current = self.game.objective_manager.get_current_objective()

                # Handle different activity completions
                if current and current.id == 'reality_check':
                    # Shelter checkin completed
                    self.intake_complete = True
                    self.bed_assigned = True
                    self.update_objective_display()
                    # Add exit door interaction
                    self.add_exit_interaction()

                elif current and current.id == 'losing_stuff':
                    # Backpack investigation completed
                    self.dialogue_box.show(None, "The reality hits hard... You're losing pieces of yourself.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                elif current and current.id == 'wearing_out_welcome':
                    # Text desperation completed - everyone has already helped
                    self.dialogue_box.show(None, "No one can help. You need to find work immediately.")
                    # Mark for completion
                    self.should_exit = True
                    self.exit_timer = 3.0

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

        # Handle exit timer
        if self.should_exit and self.exit_timer > 0:
            self.exit_timer -= dt
            if self.exit_timer <= 0:
                # Complete objective
                self.game.objective_manager.complete_current_objective()

                # Auto-transition to library for apartment search
                next_obj = self.game.objective_manager.get_current_objective()
                if next_obj and next_obj.id == 'apartment_search':
                    # Show transition message
                    if hasattr(self, 'dialogue_box'):
                        self.dialogue_box.show(None, "The next morning, you head straight to the library...")

                    # Load library room data
                    import os
                    import json
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    library_file = os.path.join(base_dir, "data", "interiors", "rooms", "library.json")

                    try:
                        with open(library_file, 'r') as f:
                            room_data = json.load(f)

                        # Create and enter library interior directly
                        from src.interiors.narratives.library_narrative import LibraryNarrative
                        library = LibraryNarrative(self.game, room_data, (8, 11))
                        self.game.current_interior = library
                        library.enter()

                        # Set this interior as inactive
                        self.active = False
                    except Exception as e:
                        print(f"Error transitioning to library: {e}")
                        # Fallback to normal exit
                        self.active = False
                        if hasattr(self, 'dialogue_box'):
                            self.dialogue_box.show(None, "Head to the library to search for housing.")
                else:
                    # Normal exit if not apartment_search
                    self.active = False
    
    def draw(self, screen):
        """Draw shelter interior with activity overlay"""
        # Draw base interior
        super().draw(screen)

        # No dark overlay - the flickering lights in the backpack activity handle atmosphere

        # Always show intake desk even if "completed"
        if 'intake_desk' in self.interactive_objects and 'intake_desk' in self.completed_interactions:
            obj = self.interactive_objects['intake_desk']
            obj_x = (self.SCREEN_WIDTH - self.room_width * self.TILE_SIZE) // 2 + obj['x'] * self.TILE_SIZE
            obj_y = (self.SCREEN_HEIGHT - self.room_height * self.TILE_SIZE) // 2 + obj['y'] * self.TILE_SIZE
            
            # Draw with green tint if completed
            if self.intake_complete:
                pygame.draw.rect(screen, (100, 200, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)
            else:
                pygame.draw.rect(screen, (255, 220, 100), (obj_x + 8, obj_y + 8, 48, 48), 2)
        
        # Draw activity on top if active
        if hasattr(self, 'current_activity') and self.current_activity and self.current_activity.active:
            self.current_activity.draw(screen)
            return
        
        # Draw status in corner
        if self.intake_complete:
            font = pygame.font.Font(None, 24)
            status_text = "✓ Checked In - Bed 47"
            status_surf = font.render(status_text, True, (100, 255, 100))
            screen.blit(status_surf, (10, 10))
            
            if self.bed_assigned:
                instruction = "Find your bed to rest"
                inst_surf = font.render(instruction, True, (255, 220, 100))
                screen.blit(inst_surf, (10, 40))
"""
Emergency Shelter Interior with Check-in Process
"""
import pygame
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
        
    def enter(self):
        """Override enter to set up shelter scene"""
        super().enter()
        
        # Add intake desk immediately
        current = self.game.objective_manager.get_current_objective()
        if current and current.id == 'reality_check':
            interactions = self.narrative_content['reality_check']['interactions']
            if 'intake_desk' in interactions:
                self.add_interactive_object('intake_desk', interactions['intake_desk'])
                if 'intake_desk' in self.completed_interactions:
                    self.completed_interactions.remove('intake_desk')
        
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
    
    def add_exit_interaction(self):
        """Add the exit door after completing intake"""
        if 'reality_check' in self.narrative_content:
            exit_data = self.narrative_content['reality_check']['interactions']['exit_door']
            self.add_interactive_object('exit_door', exit_data)
            
            # Show completion message
            self.dialogue_box.show(None, "You're all checked in. Your bed is ready.")
    
    def handle_event(self, event):
        """Handle events with activity priority"""
        # Handle activity events first
        if hasattr(self, 'current_activity') and self.current_activity is not None and self.current_activity.active:
            print(f"DEBUG: Activity is active, blocking other events")
            if event.type == pygame.KEYDOWN:
                self.current_activity.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.current_activity.handle_mouse_click(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(self.current_activity, 'handle_mouse_release'):
                    self.current_activity.handle_mouse_release(event.pos, event.button)
            elif event.type == pygame.MOUSEMOTION:
                self.current_activity.handle_mouse_motion(event.pos)
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
                # Mark intake as complete
                self.intake_complete = True
                self.bed_assigned = True
                self.update_objective_display()

                # Clear the current activity
                self.current_activity = None

                # Clear from objective manager
                if hasattr(self.game, 'objective_manager') and hasattr(self.game.objective_manager, 'current_activity'):
                    self.game.objective_manager.current_activity = None

                # Add exit door interaction
                self.add_exit_interaction()

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
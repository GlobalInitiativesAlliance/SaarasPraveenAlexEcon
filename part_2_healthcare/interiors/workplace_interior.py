"""
Workplace Interior for Part 2: Healthcare Access
Handles the burger shop workplace where work_day_anxiety occurs
"""
import pygame
from src.interiors.narrative_interior import NarrativeInterior

class WorkplaceInterior(NarrativeInterior):
    """Workplace interior for work_day_anxiety scenario"""

    def __init__(self, game, room_data, building_pos):
        super().__init__(game, room_data, building_pos)
        self.interior_name = "Burger Palace Workplace"
        print(f"[WORKPLACE] Initialized workplace interior at {building_pos}")

    def enter(self):
        """Set up workplace based on current healthcare objective"""
        super().enter()
        print("[WORKPLACE] Player entered workplace")

        current = self.game.objective_manager.get_current_objective()
        if current:
            print(f"[WORKPLACE] Current objective: {current.id}")
            if current.id == 'work_day_anxiety':
                self.setup_work_day_anxiety()
            else:
                print(f"[WORKPLACE] No specific setup for objective: {current.id}")

        self.update_objective_display()

    def update(self, dt):
        """Update workplace interior"""
        super().update(dt)

        # Force check current objective every frame
        current = self.game.objective_manager.get_current_objective()
        if current:
            print(f"[WORKPLACE_UPDATE] Current objective: {current.id}, Interactions: {list(self.interactive_objects.keys())}")

            # Force narrative_active to False for workplace objectives
            if current.id in ['work_day_anxiety']:
                self.narrative_active = False

            # If we have no interactions but should have them, force setup
            if current.id == 'work_day_anxiety' and not self.interactive_objects:
                print("[WORKPLACE_UPDATE] EMERGENCY: No interactions for work_day_anxiety, forcing setup NOW")
                self.force_objective_setup('work_day_anxiety')

        self.update_objective_display()

    def handle_event(self, event):
        """Handle events with activity routing and direct E key handling"""
        print(f"[WORKPLACE] handle_event called: type={event.type}, key={getattr(event, 'key', None)}")

        # CRITICAL FIX: Check if BurgerRushGame activity is active and route events to it
        current_activity = getattr(self, 'current_activity', None)
        if current_activity and hasattr(current_activity, 'active') and current_activity.active:
            print(f"[WORKPLACE] Routing event to active activity: {current_activity.__class__.__name__}")

            # Route mouse events to the activity
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(current_activity, 'handle_event'):
                    current_activity.handle_event(event)
                return
            elif event.type == pygame.MOUSEBUTTONUP:
                if hasattr(current_activity, 'handle_event'):
                    current_activity.handle_event(event)
                return
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(current_activity, 'handle_event'):
                    current_activity.handle_event(event)
                return
            elif event.type == pygame.KEYDOWN:
                # Let activity handle keyboard events too (like ESC to exit game)
                if hasattr(current_activity, 'handle_event'):
                    current_activity.handle_event(event)
                return

        # Handle interior-specific events when no activity is active
        if event.type == pygame.KEYDOWN:
            print(f"[WORKPLACE] Key pressed: {event.key}")
            if event.key == pygame.K_e:
                print("[WORKPLACE] E key detected in workplace!")

                # Handle E key for interactions directly
                print(f"[WORKPLACE] Checking interactions: {list(self.interactive_objects.keys())}")
                print(f"[WORKPLACE] narrative_active: {getattr(self, 'narrative_active', 'undefined')}")
                print(f"[WORKPLACE] dialogue_active: {getattr(self.dialogue_box, 'active', 'undefined')}")

                # Check if we can interact
                if (not getattr(self, 'narrative_active', False) and
                    not getattr(self.dialogue_box, 'active', False)):

                    # Debug player position and interactions
                    if hasattr(self.game, 'player'):
                        player_pos = (self.game.player.x, self.game.player.y)
                        print(f"[WORKPLACE] Player position: {player_pos}")

                    print(f"[WORKPLACE] Available interactions: {list(self.interactive_objects.keys())}")
                    for name, obj in self.interactive_objects.items():
                        interaction_pos = (obj.get('x', 'no x'), obj.get('y', 'no y'))
                        print(f"[WORKPLACE] - {name} at {interaction_pos}")

                    # Check for nearby interactive objects
                    obj_name, obj = self.check_interactions()
                    print(f"[WORKPLACE] Interaction check result: obj_name={obj_name}, obj={obj}")

                    if obj:
                        print(f"[WORKPLACE] Triggering interaction: {obj_name}")
                        self.interact_with_object(obj_name)
                        return
                    else:
                        print("[WORKPLACE] No interactions found - player not close enough to any interaction")
                else:
                    print(f"[WORKPLACE] E key blocked - narrative_active: {getattr(self, 'narrative_active', False)}, dialogue_active: {getattr(self.dialogue_box, 'active', False)}")

        # Call parent method for other events when no activity is active
        super().handle_event(event)

    def interact_with_object(self, name):
        """Override to handle workplace activity launching"""
        print(f"[WORKPLACE] interact_with_object called with: {name}")

        if name in self.interactive_objects:
            obj = self.interactive_objects[name]
            print(f"[WORKPLACE] Object data: {obj}")
            trigger = obj.get('trigger_activity')
            print(f"[WORKPLACE] Trigger activity: {trigger}")

            if trigger == 'workday_anxiety':
                print("[WORKPLACE] Launching workday anxiety activity")
                self.launch_workday_anxiety()
                return

        # Handle non-activity interactions normally
        print(f"[WORKPLACE] Calling parent interact_with_object for: {name}")
        super().interact_with_object(name)
        self.update_objective_display()

    def launch_workday_anxiety(self):
        """Launch the burger rush cooking game"""
        from part_2_healthcare.activities.burger_rush_game import BurgerRushGame

        print("[WORKPLACE] Starting burger rush cooking game...")

        # Create and start the activity
        if hasattr(self.game, 'objective_manager'):
            activity = BurgerRushGame(self.game.objective_manager)
            activity.narrative_ref = self  # Pass reference to this interior
            activity.start()

            print("[WORKPLACE] Setting burger rush game as current activity...")
            print(f"[WORKPLACE] Activity active state: {activity.active}")
            print(f"[WORKPLACE] Activity completed state: {activity.completed}")

            # Set as current activity (both on objective manager and interior)
            self.game.objective_manager.current_activity = activity
            self.current_activity = activity

            print("[WORKPLACE] Burger rush cooking game launched successfully!")
        else:
            print("[WORKPLACE] ERROR: No objective manager found!")

    def setup_work_day_anxiety(self):
        """Set up the work day anxiety scenario"""
        print("[WORKPLACE] Setting up work day anxiety scenario")

        # Clear any existing interactions
        self.interactive_objects.clear()
        self.narrative_active = False

        # Add interaction to start work shift and launch cooking game
        self.interactive_objects['work_station'] = {
            'description': 'Your work station at the grill. Press E to start cooking burgers!',
            'x': 10,  # Use x/y format expected by parent class
            'y': 8,   # Position near center of workplace
            'trigger_activity': 'workday_anxiety',
            'prompt': 'Press E to start cooking',
            'dialogue': []  # Required by parent class
        }

        print(f"[WORKPLACE] Added work_station interaction at position (10, 8)")
        print(f"[WORKPLACE] Total interactions: {len(self.interactive_objects)}")

        # Update objective display
        current_obj = self.game.objective_manager.get_current_objective()
        if current_obj:
            current_obj.dynamic_description = "At your burger shop job, it's time to cook! Go to your work station and show off your cooking skills."

    def force_objective_setup(self, objective_id):
        """Force setup of interactions for a specific objective"""
        print(f"[WORKPLACE] Force setting up objective: {objective_id}")
        print(f"[WORKPLACE] Current interactions before cleanup: {list(self.interactive_objects.keys())}")

        # Clear old interactions to prevent conflicts
        self.interactive_objects.clear()
        self.completed_interactions.clear()

        # Force narrative_active to False to allow E key interactions
        self.narrative_active = False
        print(f"[WORKPLACE] Set narrative_active to False")

        # Set up interactions for the objective
        if objective_id == 'work_day_anxiety':
            self.setup_work_day_anxiety()

        print(f"[WORKPLACE] Interactions after setup: {list(self.interactive_objects.keys())}")

    def update_objective_display(self):
        """Update the objective text based on current progress"""
        current = self.game.objective_manager.get_current_objective()
        if not current:
            return

        if current.id == 'work_day_anxiety':
            # Update based on current state
            if 'work_station' in self.interactive_objects:
                current.dynamic_description = "At your burger shop job, it's time to cook! Go to your work station and start making burgers."
            else:
                current.dynamic_description = "At your burger shop job, time to get cooking!"

    def update_contextual_thoughts(self, dt):
        """Update contextual thoughts - placeholder for consistency"""
        pass

    def draw_custom_elements(self, screen):
        """Draw workplace-specific visual elements"""
        # Add workplace ambiance - draw basic kitchen elements
        if not self.active:
            return

        # Draw some basic workplace indicators (grill, counter, etc.)
        # This adds visual context even when not in the activity
        grill_rect = pygame.Rect(400, 300, 80, 40)
        pygame.draw.rect(screen, (139, 69, 19), grill_rect)  # Brown grill

        counter_rect = pygame.Rect(300, 350, 200, 30)
        pygame.draw.rect(screen, (128, 128, 128), counter_rect)  # Gray counter

        # Draw work station indicator if applicable
        if 'work_station' in self.interactive_objects:
            station_obj = self.interactive_objects['work_station']
            # Convert grid position to screen position (approximate)
            screen_x = station_obj['x'] * 32
            screen_y = station_obj['y'] * 32

            # Draw a small indicator
            indicator_rect = pygame.Rect(screen_x, screen_y, 20, 20)
            pygame.draw.rect(screen, (255, 255, 0), indicator_rect)  # Yellow indicator

    def draw(self, screen):
        """Override draw to add workplace elements"""
        super().draw(screen)
        self.draw_custom_elements(screen)
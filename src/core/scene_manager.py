"""
Scene Manager - Direct jumping to specific game scenes/mini-games
Provides clean navigation to any scene without manual progression
"""

class SceneManager:
    """Manages direct scene jumping and game state manipulation"""

    SCENE_MAP = {
        'burger_rush': {
            'name': 'Burger Rush Cooking Game',
            'part': 2,
            'objective': 'work_day_anxiety',
            'interior': 'WorkplaceInterior',
            'activity': 'BurgerRushGame',
            'position': (39, 51),
            'description': 'Fixed burger cooking mini-game with drag & drop'
        },
        'doctor': {
            'name': 'Doctor Appointment',
            'part': 2,
            'objective': 'doctor_appointment',
            'interior': 'ClinicInterior',
            'position': (34, 31),
            'description': 'Visit clinic for healthcare appointment'
        },
        'doctor_enhanced': {
            'name': 'Enhanced Doctor Visit',
            'part': 2,
            'objective': 'doctor_appointment',
            'interior': 'EnhancedClinicInterior',
            'position': (34, 31),
            'description': 'Enhanced clinic experience with mini-games'
        },
        'therapist': {
            'name': 'Therapist Call',
            'part': 2,
            'objective': 'therapist_call',
            'activity': 'TherapistCallActivity',
            'description': 'Make therapy appointment phone call'
        },
        'breathing': {
            'name': 'Breathing Exercise',
            'part': 2,
            'objective': 'breathing_exercise',
            'activity': 'EnhancedBreathingExercise',
            'description': 'Anxiety management breathing exercise'
        },
        'pharmacy': {
            'name': 'Pharmacy Visit',
            'part': 2,
            'objective': 'pharmacy_visit',
            'activity': 'EnhancedPharmacyActivity',
            'description': 'Medication selection at pharmacy'
        },
        'part2_start': {
            'name': 'Part 2 Beginning',
            'part': 2,
            'objective': 'healthcare_intro',
            'description': 'Start of healthcare access storyline'
        },
        'part1_burger': {
            'name': 'Part 1 Burger Job',
            'part': 1,
            'objective': 'burger_training',
            'activity': 'BurgerTrainingActivity',
            'description': 'Part 1 burger job training'
        }
    }

    def __init__(self, game):
        self.game = game

    def get_available_scenes(self):
        """Get list of all available scenes"""
        return self.SCENE_MAP

    def jump_to_scene(self, scene_name):
        """Jump directly to a specific scene"""
        if scene_name not in self.SCENE_MAP:
            print(f"[SCENE_MANAGER] Unknown scene: {scene_name}")
            print(f"Available scenes: {list(self.SCENE_MAP.keys())}")
            return False

        scene = self.SCENE_MAP[scene_name]
        print(f"[SCENE_MANAGER] Jumping to scene: {scene_name} - {scene['name']}")

        try:
            # Set game part
            if 'part' in scene:
                self._set_game_part(scene['part'])

            # Jump to objective
            if 'objective' in scene:
                self._jump_to_objective(scene['objective'])

            # Teleport player
            if 'position' in scene:
                self._teleport_player(scene['position'])

            # Enter interior
            if 'interior' in scene:
                self._enter_interior(scene['interior'], scene.get('position'))

            # Launch activity
            if 'activity' in scene:
                self._launch_activity(scene['activity'])

            print(f"[SCENE_MANAGER] Successfully jumped to {scene_name}")
            return True

        except Exception as e:
            print(f"[SCENE_MANAGER] Failed to jump to {scene_name}: {e}")
            return False

    def _set_game_part(self, part):
        """Set the game part and load appropriate objectives"""
        print(f"[SCENE_MANAGER] Setting game part to {part}")

        if not hasattr(self.game, 'objective_manager'):
            print("[SCENE_MANAGER] No objective manager found")
            return

        self.game.objective_manager.game_part = part

        # Load objectives for the part
        if part == 2:
            self.game.objective_manager.setup_part2_objectives()
        elif part == 1:
            self.game.objective_manager.setup_part1_objectives()
        else:
            self.game.objective_manager.setup_objectives()

        print(f"[SCENE_MANAGER] Game part set to {part}")

    def _jump_to_objective(self, objective_id):
        """Jump directly to a specific objective"""
        print(f"[SCENE_MANAGER] Jumping to objective: {objective_id}")

        if not hasattr(self.game, 'objective_manager'):
            print("[SCENE_MANAGER] No objective manager found")
            return

        objectives = self.game.objective_manager.objectives

        # Find the objective index
        target_index = None
        for i, obj in enumerate(objectives):
            if obj.id == objective_id:
                target_index = i
                break

        if target_index is not None:
            self.game.objective_manager.current_objective_index = target_index
            print(f"[SCENE_MANAGER] Set objective index to {target_index} ({objective_id})")
        else:
            print(f"[SCENE_MANAGER] Objective '{objective_id}' not found")
            print(f"Available objectives: {[obj.id for obj in objectives]}")

    def _teleport_player(self, position):
        """Teleport player to specific position"""
        x, y = position
        print(f"[SCENE_MANAGER] Teleporting player to ({x}, {y})")

        if hasattr(self.game, 'player'):
            self.game.player.x = x
            self.game.player.y = y
            print(f"[SCENE_MANAGER] Player teleported to ({x}, {y})")
        else:
            print("[SCENE_MANAGER] No player object found")

    def _enter_interior(self, interior_name, position=None):
        """Enter a specific interior"""
        print(f"[SCENE_MANAGER] Entering interior: {interior_name}")

        try:
            # Get building position
            if position:
                building_pos = position
            else:
                building_pos = (0, 0)  # Default

            # Create interior based on name
            if interior_name in ['WorkplaceInterior', 'ClinicInterior', 'EnhancedClinicInterior']:
                print(f"[SCENE_MANAGER] Part 2 interior {interior_name} no longer available")
                return
            else:
                print(f"[SCENE_MANAGER] Unknown interior: {interior_name}")
                return

            # Set as current interior
            self.game.current_interior = interior
            print(f"[SCENE_MANAGER] Entered {interior_name}")

        except Exception as e:
            print(f"[SCENE_MANAGER] Failed to enter {interior_name}: {e}")

    def _launch_activity(self, activity_name):
        """Launch a specific activity"""
        print(f"[SCENE_MANAGER] Launching activity: {activity_name}")

        try:
            activity = None

            if activity_name in ['BurgerRushGame', 'TherapistCallActivity', 'EnhancedBreathingExercise', 'EnhancedPharmacyActivity']:
                print(f"[SCENE_MANAGER] Part 2 activity {activity_name} no longer available")
                return

            elif activity_name == 'BurgerTrainingActivity':
                # Part 1 activity
                activity = self.game.objective_manager.burger_training

            else:
                print(f"[SCENE_MANAGER] Unknown activity: {activity_name}")
                return

            if activity:
                activity.start()
                self.game.objective_manager.current_activity = activity
                print(f"[SCENE_MANAGER] Launched {activity_name}")

        except Exception as e:
            print(f"[SCENE_MANAGER] Failed to launch {activity_name}: {e}")

    def get_current_scene(self):
        """Get information about current scene"""
        current_obj = None
        if hasattr(self.game, 'objective_manager'):
            current_obj = self.game.objective_manager.get_current_objective()

        current_interior = None
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            current_interior = self.game.current_interior.__class__.__name__

        current_activity = None
        if (hasattr(self.game, 'objective_manager') and
            hasattr(self.game.objective_manager, 'current_activity') and
            self.game.objective_manager.current_activity):
            current_activity = self.game.objective_manager.current_activity.__class__.__name__

        # Try to match current state to a scene
        for scene_name, scene_data in self.SCENE_MAP.items():
            match = True

            if 'objective' in scene_data and current_obj:
                if scene_data['objective'] != current_obj.id:
                    match = False

            if 'interior' in scene_data:
                if scene_data['interior'] != current_interior:
                    match = False

            if 'activity' in scene_data:
                if scene_data['activity'] != current_activity:
                    match = False

            if match and ('objective' in scene_data or 'interior' in scene_data or 'activity' in scene_data):
                return scene_name, scene_data

        return None, None

    def list_scenes(self):
        """List all available scenes with descriptions"""
        print("\n[SCENE_MANAGER] Available Scenes:")
        for scene_name, scene_data in self.SCENE_MAP.items():
            print(f"  {scene_name:15} - {scene_data['name']}")
            print(f"                    {scene_data['description']}")

    def quick_jump(self, scene_name):
        """Quick jump with minimal output"""
        if scene_name in self.SCENE_MAP:
            return self.jump_to_scene(scene_name)
        return False
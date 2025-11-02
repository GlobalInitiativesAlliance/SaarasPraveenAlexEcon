"""
Part Transition Manager - Handles clean transitions between game parts
Ensures no state contamination between Part 1 and Part 2
"""
import pygame

class PartTransitionManager:
    """Manages clean transitions between game parts"""

    def __init__(self, game):
        self.game = game
        self.objective_manager = game.objective_manager if hasattr(game, 'objective_manager') else None
        self.building_manager = game.building_manager if hasattr(game, 'building_manager') else None

    def transition_to_part2(self):
        """Complete transition from Part 1 to Part 2 with full state cleanup"""
        print("=== PART TRANSITION MANAGER: Starting Part 1 → Part 2 ===")

        try:
            # Phase 1: Complete Part 1 cleanup
            print("[PHASE 1] Starting Part 1 cleanup...")
            self.cleanup_part1_state()
            print("[PHASE 1] ✅ Part 1 cleanup complete")

            # Phase 2: Reset all systems
            print("[PHASE 2] Resetting core systems...")
            self.reset_core_systems()
            print("[PHASE 2] ✅ Core systems reset complete")

            # Phase 3: Initialize Part 2
            print("[PHASE 3] Setting up Part 2 state...")
            self.setup_part2_state()
            print("[PHASE 3] ✅ Part 2 state setup complete")

            print("=== PART TRANSITION MANAGER: Part 2 ready ===")

        except Exception as e:
            print(f"[CRITICAL ERROR] Part transition failed at some phase: {e}")
            import traceback
            traceback.print_exc()

            # Try emergency recovery
            print("[EMERGENCY] Attempting emergency recovery...")
            self.handle_transition_error(e)

    def cleanup_part1_state(self):
        """Comprehensive cleanup of all Part 1 state"""
        print("[CLEANUP] Starting Part 1 state cleanup...")

        # 1. Clear all interior instances
        self.cleanup_interior_instances()

        # 2. Clear objective manager state
        self.cleanup_objective_state()

        # 3. Clear activity states
        self.cleanup_activity_state()

        # 4. Clear building manager state
        self.cleanup_building_state()

        # 5. Clear UI state
        self.cleanup_ui_state()

        print("[CLEANUP] Part 1 state cleanup complete")

    def cleanup_interior_instances(self):
        """Destroy all interior instances and their state"""
        print("[CLEANUP] Clearing interior instances...")

        # Clear current interior
        if hasattr(self.game, 'current_interior'):
            if self.game.current_interior:
                # Clear any active dialogues
                if hasattr(self.game.current_interior, 'dialogue_box'):
                    self.game.current_interior.dialogue_box.hide()

                # Clear narrative state
                if hasattr(self.game.current_interior, 'narrative_active'):
                    self.game.current_interior.narrative_active = False

                # Clear completed interactions
                if hasattr(self.game.current_interior, 'completed_interactions'):
                    self.game.current_interior.completed_interactions.clear()

                # Clear interactive objects
                if hasattr(self.game.current_interior, 'interactive_objects'):
                    self.game.current_interior.interactive_objects.clear()

                # Deactivate
                self.game.current_interior.active = False

            self.game.current_interior = None

        # Clear any cached interiors in building manager
        if self.building_manager and hasattr(self.building_manager, 'cached_interiors'):
            self.building_manager.cached_interiors = {}

    def cleanup_objective_state(self):
        """Clear objective manager state"""
        print("[CLEANUP] Clearing objective state...")

        if not self.objective_manager:
            return

        # Clear current activity
        if hasattr(self.objective_manager, 'current_activity'):
            if self.objective_manager.current_activity:
                self.objective_manager.current_activity.active = False
                self.objective_manager.current_activity = None

        # Clear notification state
        if hasattr(self.objective_manager, 'showing_notification'):
            self.objective_manager.showing_notification = False
            self.objective_manager.notification_text = ""
            self.objective_manager.notification_timer = 0

        # Clear Part 1 specific activities
        part1_activities = ['workplace_quiz', 'job_application', 'pizza_game']
        for activity_name in part1_activities:
            if hasattr(self.objective_manager, activity_name):
                activity = getattr(self.objective_manager, activity_name)
                if activity:
                    activity.active = False
                setattr(self.objective_manager, activity_name, None)

    def cleanup_activity_state(self):
        """Clear activity manager and mini-game state"""
        print("[CLEANUP] Clearing activity state...")

        if hasattr(self.objective_manager, 'activity_manager'):
            activity_manager = self.objective_manager.activity_manager
            if activity_manager:
                # Clear any active activities
                if hasattr(activity_manager, 'current_activity'):
                    activity_manager.current_activity = None

                # Clear activity history
                if hasattr(activity_manager, 'completed_activities'):
                    activity_manager.completed_activities.clear()

        # Clear global pygame mixer state (in case audio was used)
        try:
            pygame.mixer.stop()
        except:
            pass

    def cleanup_building_state(self):
        """Clear building manager state"""
        print("[CLEANUP] Clearing building manager state...")

        if not self.building_manager:
            return

        # Clear any cached building lookups
        if hasattr(self.building_manager, 'building_cache'):
            self.building_manager.building_cache = {}

        # Clear any active building state
        if hasattr(self.building_manager, 'current_building'):
            self.building_manager.current_building = None

    def cleanup_ui_state(self):
        """Clear UI manager state"""
        print("[CLEANUP] Clearing UI state...")

        if hasattr(self.objective_manager, 'ui_manager'):
            ui_manager = self.objective_manager.ui_manager
            if ui_manager:
                # Clear any active UI elements
                if hasattr(ui_manager, 'active_panels'):
                    ui_manager.active_panels = []

                # Clear notification state (preserve the NotificationToast object)
                if hasattr(ui_manager, 'notifications'):
                    # If it's a NotificationToast object, clear its internal notifications list
                    if hasattr(ui_manager.notifications, 'notifications'):
                        ui_manager.notifications.notifications.clear()
                    # If it's already a list (shouldn't happen, but fallback)
                    elif isinstance(ui_manager.notifications, list):
                        ui_manager.notifications.clear()

    def reset_core_systems(self):
        """Reset all core game systems"""
        print("[RESET] Resetting core systems...")

        # Reset objective manager for Part 2
        if self.objective_manager:
            print("[RESET] Configuring objective manager for Part 2...")
            # Set Part 2 state
            old_part = getattr(self.objective_manager, 'game_part', 'unknown')
            self.objective_manager.game_part = 2
            self.objective_manager.current_objective_index = 0

            # Reset time and money for Part 2
            self.objective_manager.game_time = "8:00 AM"
            self.objective_manager.current_day = 1
            self.objective_manager.player_money = 0.0  # Part 2 starts fresh

            print(f"[RESET] ✅ Game part: {old_part} → {self.objective_manager.game_part}")
            print(f"[RESET] ✅ Objective index reset to: {self.objective_manager.current_objective_index}")
        else:
            print("[WARNING] No objective manager to reset")

        # Reset building manager mappings
        if self.building_manager:
            print("[RESET] Reloading building manager mappings...")
            # Reload building interior mappings to get fresh state
            self.building_manager.load_building_interiors()
            print("[RESET] ✅ Building manager mappings reloaded")
        else:
            print("[WARNING] No building manager to reset")

        # Clear any global game state
        if hasattr(self.game, 'game_state'):
            print(f"[RESET] ✅ Game state maintained as: {self.game.game_state}")
            self.game.game_state = 'playing'

    def setup_part2_state(self):
        """Initialize Part 2 state"""
        print("[SETUP] Initializing Part 2 state...")

        if not self.objective_manager:
            print("[ERROR] No objective manager available for Part 2 setup")
            raise Exception("Cannot setup Part 2: No objective manager found")

        try:
            # Load Part 2 objectives using the main setup method (ensures game_part logic is used)
            print("[SETUP] Loading Part 2 objectives...")
            if hasattr(self.objective_manager, 'setup_objectives'):
                self.objective_manager.setup_objectives()
            else:
                print("[FALLBACK] Using direct setup_part2_objectives method")
                self.objective_manager.setup_part2_objectives()

            print(f"[SETUP] Loaded {len(self.objective_manager.objectives)} Part 2 objectives")

            # Find building locations for Part 2
            print("[SETUP] Finding building locations...")
            if hasattr(self.objective_manager, 'find_building_locations'):
                self.objective_manager.find_building_locations()

            # Initialize Part 2 specific systems
            print("[SETUP] Initializing Part 2 systems...")
            self.init_part2_systems()

            # Activate first Part 2 objective
            print("[SETUP] Activating first Part 2 objective...")
            if hasattr(self.objective_manager, 'activate_current_objective'):
                self.objective_manager.activate_current_objective()

                # Verify activation
                current = self.objective_manager.get_current_objective() if hasattr(self.objective_manager, 'get_current_objective') else None
                if current:
                    print(f"[SETUP] ✅ Part 2 first objective activated: {current.id}")
                else:
                    print("[WARNING] No current objective after activation")
            else:
                print("[ERROR] activate_current_objective method not found")

        except Exception as e:
            print(f"[ERROR] Part 2 state setup failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def init_part2_systems(self):
        """Initialize Part 2 specific systems"""
        print("[SETUP] Initializing Part 2 systems...")

        # Initialize Part 2 activities if needed
        if hasattr(self.objective_manager, 'init_part2_activities'):
            self.objective_manager.init_part2_activities()

        # Set Part 2 UI theme if available
        if hasattr(self.objective_manager, 'ui_manager'):
            ui_manager = self.objective_manager.ui_manager
            if hasattr(ui_manager, 'set_part_theme'):
                ui_manager.set_part_theme(2)

    def validate_clean_transition(self):
        """Validate that the transition was clean"""
        issues = []

        # Check for lingering Part 1 state
        if hasattr(self.game, 'current_interior') and self.game.current_interior:
            issues.append("Interior instance still active")

        if self.objective_manager:
            if hasattr(self.objective_manager, 'current_activity') and self.objective_manager.current_activity:
                issues.append("Activity still active")

            if self.objective_manager.game_part != 2:
                issues.append(f"Game part not set to 2: {self.objective_manager.game_part}")

        if issues:
            print(f"[WARNING] Transition validation failed: {issues}")
            return False
        else:
            print("[VALIDATION] Clean transition confirmed")
            return True

    def emergency_cleanup(self):
        """Emergency cleanup if normal transition fails"""
        print("[EMERGENCY] Performing emergency cleanup...")

        # Force clear everything
        if hasattr(self.game, 'current_interior'):
            self.game.current_interior = None

        if self.objective_manager:
            self.objective_manager.current_activity = None
            self.objective_manager.game_part = 2

        # Force garbage collection
        import gc
        gc.collect()

        print("[EMERGENCY] Emergency cleanup complete")

    def handle_transition_error(self, error):
        """Handle errors during transition"""
        print(f"[ERROR] Transition error: {error}")

        # Attempt emergency cleanup
        self.emergency_cleanup()

        # Try to continue with Part 2
        try:
            self.setup_part2_state()
        except Exception as e:
            print(f"[CRITICAL] Could not recover from transition error: {e}")
            raise

    def get_transition_status(self):
        """Get current transition status"""
        status = {
            'current_part': self.objective_manager.game_part if self.objective_manager else 'unknown',
            'interior_active': bool(hasattr(self.game, 'current_interior') and self.game.current_interior),
            'activity_active': bool(self.objective_manager and hasattr(self.objective_manager, 'current_activity') and self.objective_manager.current_activity),
            'objectives_loaded': bool(self.objective_manager and len(self.objective_manager.objectives) > 0)
        }
        return status
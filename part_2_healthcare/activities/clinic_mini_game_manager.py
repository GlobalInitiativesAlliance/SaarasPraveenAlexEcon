"""
Clinic Mini-Game Manager
Integrates all clinic mini-games with the objective system
Handles transitions between mini-games and objective completion
"""

import pygame
from .clinic_navigation import ClinicNavigationGame
from .clinic_document_checklist import ClinicDocumentChecklistGame
from .foster_youth_application_form import FosterYouthApplicationFormGame
from .approval_notification import ApprovalNotificationGame

class ClinicMiniGameManager:
    """Manages all clinic-related mini-games and their integration"""

    def __init__(self, objective_manager=None):
        # Ensure pygame font is initialized
        pygame.font.init()

        self.objective_manager = objective_manager
        self.active = False
        self.current_game = None

        # Initialize all mini-games
        self.mini_games = {
            'travel_to_clinic': ClinicNavigationGame(objective_manager),
            'clinic_checklist': ClinicDocumentChecklistGame(objective_manager),
            'foster_youth_application': FosterYouthApplicationFormGame(objective_manager),
            'application_approved': ApprovalNotificationGame(objective_manager)
        }

        # Game state tracking
        self.completed_games = set()
        self.current_objective_id = None

    def start_mini_game(self, objective_id):
        """Start the appropriate mini-game for the given objective"""
        if objective_id not in self.mini_games:
            print(f"Warning: No mini-game found for objective {objective_id}")
            return False

        self.current_objective_id = objective_id
        self.current_game = self.mini_games[objective_id]
        self.current_game.start()
        self.active = True

        # Set this manager as the current activity for proper integration
        if self.objective_manager and hasattr(self.objective_manager, 'current_activity'):
            self.objective_manager.current_activity = self

        print(f"Started mini-game for objective: {objective_id}")
        return True

    def update(self, dt):
        """Update the current mini-game"""
        if not self.active or not self.current_game:
            return

        self.current_game.update(dt)

        # Check if current game completed
        if self.current_game.completed:
            self.complete_current_game()

    def handle_event(self, event):
        """Handle pygame events for current mini-game"""
        if not self.active or not self.current_game:
            return

        self.current_game.handle_event(event)

    def draw(self, screen):
        """Draw the current mini-game"""
        print(f"[DEBUG_MGR] ===== MINI-GAME MANAGER DRAW CALLED =====")
        print(f"[DEBUG_MGR] Manager active: {self.active}")
        print(f"[DEBUG_MGR] Current game exists: {self.current_game is not None}")

        if not self.active or not self.current_game:
            print(f"[DEBUG_MGR] Not active or no current game, returning")
            return

        print(f"[DEBUG_MGR] Current game type: {type(self.current_game).__name__}")
        print(f"[DEBUG_MGR] Current game active: {self.current_game.active}")
        print(f"[DEBUG_MGR] Calling current game draw()...")
        self.current_game.draw(screen)
        print(f"[DEBUG_MGR] Current game draw() completed")

    def render(self, screen):
        """Render method for compatibility with activity system"""
        self.draw(screen)

    def complete_current_game(self):
        """Handle completion of the current mini-game"""
        if not self.current_game or not self.current_objective_id:
            return

        # Mark game as completed
        self.completed_games.add(self.current_objective_id)

        # Get results from the mini-game
        results = self.current_game.get_results()

        # Notify objective manager of completion
        if self.objective_manager:
            # Complete the objective
            if hasattr(self.objective_manager, 'complete_objective'):
                self.objective_manager.complete_objective(self.current_objective_id)

            # Show completion notification
            if hasattr(self.objective_manager, 'show_notification'):
                message = f"Completed: {self.get_objective_title(self.current_objective_id)}! {results.get('message', 'Mini-game completed successfully!')}"
                self.objective_manager.show_notification(message)

        # Clear current activity
        if self.objective_manager and hasattr(self.objective_manager, 'current_activity'):
            self.objective_manager.current_activity = None

        # Deactivate current game
        self.active = False
        self.current_game = None
        self.current_objective_id = None

        print(f"Mini-game completed. Results: {results}")

    def get_objective_title(self, objective_id):
        """Get user-friendly title for objective"""
        titles = {
            'travel_to_clinic': 'Clinic Navigation',
            'clinic_checklist': 'Document Verification',
            'foster_youth_application': 'Application Form',
            'application_approved': 'Approval Notification'
        }
        return titles.get(objective_id, objective_id)

    def is_game_completed(self, objective_id):
        """Check if a specific mini-game has been completed"""
        return objective_id in self.completed_games

    def get_completion_status(self):
        """Get overall completion status"""
        total_games = len(self.mini_games)
        completed_count = len(self.completed_games)

        return {
            'total': total_games,
            'completed': completed_count,
            'percentage': (completed_count / total_games) * 100 if total_games > 0 else 0,
            'completed_games': list(self.completed_games)
        }

    def reset_progress(self):
        """Reset all mini-game progress"""
        self.completed_games.clear()
        self.active = False
        self.current_game = None
        self.current_objective_id = None

        # Reset individual mini-games
        for game in self.mini_games.values():
            game.active = False
            game.completed = False

    def force_complete_objective(self, objective_id):
        """Force complete an objective (for testing/debugging)"""
        if objective_id in self.mini_games:
            self.completed_games.add(objective_id)

            if self.objective_manager and hasattr(self.objective_manager, 'complete_objective'):
                self.objective_manager.complete_objective(objective_id)

            print(f"Force completed objective: {objective_id}")
            return True
        return False

# Test function to verify mini-games work correctly
def test_clinic_mini_games():
    """Test all clinic mini-games for basic functionality"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Clinic Mini-Games Test")
    clock = pygame.time.Clock()

    # Create manager without objective system for testing
    manager = ClinicMiniGameManager()

    # Test sequence: navigation -> checklist -> application -> approval
    test_sequence = [
        'travel_to_clinic',
        'clinic_checklist',
        'foster_youth_application',
        'application_approved'
    ]

    current_test = 0
    test_timer = 0
    auto_advance = True  # Automatically advance for testing

    print("Starting clinic mini-games test...")
    print("Press SPACE to manually advance, or let auto-advance after 10 seconds")
    print("Press ESC to quit")

    running = True
    while running and current_test < len(test_sequence):
        dt = clock.tick(60) / 1000.0
        test_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Manual advance to next test
                    if manager.active:
                        manager.complete_current_game()
                    current_test += 1
                    test_timer = 0
                    if current_test < len(test_sequence):
                        manager.start_mini_game(test_sequence[current_test])
                elif event.key == pygame.K_a:
                    auto_advance = not auto_advance
                    print(f"Auto-advance: {auto_advance}")
            else:
                manager.handle_event(event)

        # Start first test or advance automatically
        if not manager.active:
            if current_test < len(test_sequence):
                print(f"Starting test {current_test + 1}: {test_sequence[current_test]}")
                manager.start_mini_game(test_sequence[current_test])
                test_timer = 0

        # Auto advance after 10 seconds
        if auto_advance and test_timer > 10.0 and manager.active:
            print(f"Auto-advancing from {test_sequence[current_test]}")
            manager.complete_current_game()
            current_test += 1
            test_timer = 0

        # Update and draw
        manager.update(dt)

        screen.fill((30, 40, 60))
        manager.draw(screen)

        # Draw test info
        if not manager.active:
            font = pygame.font.Font(None, 36)
            if current_test < len(test_sequence):
                text = f"Starting {test_sequence[current_test]}..."
            else:
                text = "All tests completed!"

            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(640, 360))
            screen.blit(text_surf, text_rect)

        # Draw controls
        control_font = pygame.font.Font(None, 24)
        controls = [
            "SPACE: Next test",
            "A: Toggle auto-advance",
            "ESC: Quit",
            f"Test {current_test + 1}/{len(test_sequence)}: {test_sequence[current_test] if current_test < len(test_sequence) else 'Complete'}"
        ]

        for i, control in enumerate(controls):
            control_surf = control_font.render(control, True, (200, 200, 200))
            screen.blit(control_surf, (10, 10 + i * 25))

        pygame.display.flip()

    # Display final results
    if running:
        print("\nTest completed! Results:")
        status = manager.get_completion_status()
        print(f"Completed {status['completed']}/{status['total']} mini-games")
        print(f"Completion rate: {status['percentage']:.1f}%")
        print(f"Completed games: {status['completed_games']}")

        # Wait for user to close
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False

            screen.fill((50, 70, 50))
            font = pygame.font.Font(None, 48)
            text = "All Tests Completed!"
            text_surf = font.render(text, True, (100, 255, 100))
            text_rect = text_surf.get_rect(center=(640, 300))
            screen.blit(text_surf, text_rect)

            result_font = pygame.font.Font(None, 32)
            result_text = f"Completed {status['completed']}/{status['total']} mini-games"
            result_surf = result_font.render(result_text, True, (255, 255, 255))
            result_rect = result_surf.get_rect(center=(640, 360))
            screen.blit(result_surf, result_rect)

            exit_font = pygame.font.Font(None, 24)
            exit_surf = exit_font.render("Press ESC to exit", True, (200, 200, 200))
            exit_rect = exit_surf.get_rect(center=(640, 400))
            screen.blit(exit_surf, exit_rect)

            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    test_clinic_mini_games()
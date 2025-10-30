"""
Document Violations Activity
Player photographs housing code violations to build legal case
"""

import pygame
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class DocumentViolations:
    """Mini-game where player documents apartment problems"""

    def __init__(self, objective_manager):
        self.objective_manager = objective_manager
        self.active = False
        self.completed = False

        # Violations to document
        self.violations = [
            {
                "name": "Broken Heater",
                "location": (200, 150),
                "size": (80, 60),
                "documented": False,
                "description": "Hasn't worked in 3 months. No heat in winter.",
                "severity": "Critical"
            },
            {
                "name": "Mold Growth",
                "location": (450, 200),
                "size": (100, 80),
                "documented": False,
                "description": "Black mold spreading on bathroom ceiling.",
                "severity": "Health Hazard"
            },
            {
                "name": "Broken Window Lock",
                "location": (600, 300),
                "size": (60, 80),
                "documented": False,
                "description": "Security risk. Anyone could break in.",
                "severity": "Safety Issue"
            },
            {
                "name": "Roach Infestation",
                "location": (350, 400),
                "size": (120, 60),
                "documented": False,
                "description": "Roaches everywhere. Landlord refuses to treat.",
                "severity": "Health Hazard"
            },
            {
                "name": "Water Damage",
                "location": (150, 350),
                "size": (90, 90),
                "documented": False,
                "description": "Ceiling leaks when upstairs neighbor showers.",
                "severity": "Structural"
            }
        ]

        # Camera viewfinder
        self.viewfinder_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.viewfinder_size = 120
        self.flash_timer = 0

        # UI elements
        self.photos_taken = 0
        self.evidence_quality = 0

    def start(self):
        """Start the documentation activity"""
        self.active = True
        self.completed = False
        self.photos_taken = 0
        self.evidence_quality = 0
        self.flash_timer = 0

        # Reset all violations
        for violation in self.violations:
            violation['documented'] = False

    def update(self, dt):
        """Update activity state"""
        if not self.active:
            return

        # Update flash animation
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Check if all violations documented
        documented_count = sum(1 for v in self.violations if v['documented'])
        if documented_count == len(self.violations):
            self.complete()

    def handle_event(self, event):
        """Handle player input"""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.complete()
                return True

            # Move viewfinder with arrow keys
            move_speed = 15
            if event.key == pygame.K_LEFT:
                self.viewfinder_pos[0] = max(60, self.viewfinder_pos[0] - move_speed)
            elif event.key == pygame.K_RIGHT:
                self.viewfinder_pos[0] = min(SCREEN_WIDTH - 60, self.viewfinder_pos[0] + move_speed)
            elif event.key == pygame.K_UP:
                self.viewfinder_pos[1] = max(60, self.viewfinder_pos[1] - move_speed)
            elif event.key == pygame.K_DOWN:
                self.viewfinder_pos[1] = min(SCREEN_HEIGHT - 100, self.viewfinder_pos[1] + move_speed)

            # Take photo with SPACE
            elif event.key == pygame.K_SPACE:
                self.take_photo()

        return True

    def take_photo(self):
        """Check if viewfinder is over a violation and document it"""
        viewfinder_rect = pygame.Rect(
            self.viewfinder_pos[0] - self.viewfinder_size // 2,
            self.viewfinder_pos[1] - self.viewfinder_size // 2,
            self.viewfinder_size,
            self.viewfinder_size
        )

        for violation in self.violations:
            if violation['documented']:
                continue

            violation_rect = pygame.Rect(
                violation['location'][0],
                violation['location'][1],
                violation['size'][0],
                violation['size'][1]
            )

            # Check if viewfinder overlaps violation
            if viewfinder_rect.colliderect(violation_rect):
                violation['documented'] = True
                self.photos_taken += 1
                self.flash_timer = 0.3  # Flash effect
                self.evidence_quality += 20
                break

    def render(self, screen):
        """Render the activity"""
        if not self.active:
            return

        # Dark apartment background
        screen.fill((40, 35, 30))

        # Draw violations (as colored rectangles for now)
        for violation in self.violations:
            color = (100, 180, 100) if violation['documented'] else (180, 100, 100)
            rect = pygame.Rect(
                violation['location'][0],
                violation['location'][1],
                violation['size'][0],
                violation['size'][1]
            )
            pygame.draw.rect(screen, color, rect)

            # Draw violation name
            font = pygame.font.Font(None, 20)
            text = font.render(violation['name'], True, (255, 255, 255))
            screen.blit(text, (violation['location'][0], violation['location'][1] - 20))

            # Show checkmark if documented
            if violation['documented']:
                check = font.render("✓", True, (0, 255, 0))
                screen.blit(check, (violation['location'][0] + violation['size'][0] - 20, violation['location'][1]))

        # Draw viewfinder
        viewfinder_rect = pygame.Rect(
            self.viewfinder_pos[0] - self.viewfinder_size // 2,
            self.viewfinder_pos[1] - self.viewfinder_size // 2,
            self.viewfinder_size,
            self.viewfinder_size
        )

        # Viewfinder border
        pygame.draw.rect(screen, (255, 255, 255), viewfinder_rect, 3)

        # Crosshairs
        pygame.draw.line(screen, (255, 255, 255),
                        (self.viewfinder_pos[0] - 20, self.viewfinder_pos[1]),
                        (self.viewfinder_pos[0] + 20, self.viewfinder_pos[1]), 2)
        pygame.draw.line(screen, (255, 255, 255),
                        (self.viewfinder_pos[0], self.viewfinder_pos[1] - 20),
                        (self.viewfinder_pos[0], self.viewfinder_pos[1] + 20), 2)

        # Flash effect
        if self.flash_timer > 0:
            flash_alpha = int(255 * (self.flash_timer / 0.3))
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill((255, 255, 255))
            screen.blit(flash_surface, (0, 0))

        # UI Panel
        panel_y = SCREEN_HEIGHT - 80
        pygame.draw.rect(screen, (20, 20, 20), (0, panel_y, SCREEN_WIDTH, 80))

        # Instructions
        font = pygame.font.Font(None, 24)
        instructions = font.render("Arrow Keys: Move Camera | SPACE: Take Photo | ESC: Finish", True, (255, 255, 255))
        screen.blit(instructions, (20, panel_y + 10))

        # Progress
        progress_text = f"Photos: {self.photos_taken}/{len(self.violations)} | Evidence Quality: {self.evidence_quality}%"
        progress = font.render(progress_text, True, (200, 200, 200))
        screen.blit(progress, (20, panel_y + 40))

        # Current violation info if hovering
        for violation in self.violations:
            violation_rect = pygame.Rect(
                violation['location'][0],
                violation['location'][1],
                violation['size'][0],
                violation['size'][1]
            )

            if viewfinder_rect.colliderect(violation_rect) and not violation['documented']:
                info = font.render(f"Press SPACE to document: {violation['name']}", True, (255, 255, 100))
                screen.blit(info, (SCREEN_WIDTH // 2 - 150, 50))
                break

    def complete(self):
        """Complete the activity"""
        if not self.active:
            return

        self.active = False
        self.completed = True

        # Update objective if all violations documented
        documented_count = sum(1 for v in self.violations if v['documented'])
        if documented_count == len(self.violations):
            current = self.objective_manager.get_current_objective()
            if current and current.id == 'document_problems':
                self.objective_manager.complete_objective('document_problems')

        return True

    def is_active(self):
        """Check if activity is active"""
        return self.active

    def is_completed(self):
        """Check if activity was completed"""
        return self.completed